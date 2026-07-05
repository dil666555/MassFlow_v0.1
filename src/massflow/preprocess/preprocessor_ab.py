from __future__ import annotations

from dataclasses import dataclass, field
from queue import Queue
from threading import Event, Lock, Thread
from typing import Any, Callable, Optional, cast

import numpy as np

from massflow.data_manager import MSDataManager, MSDataManagerImzML
from massflow.preprocess.api import PreprocessorAPI, TaskScope
from massflow.preprocess.flat_pre_fun import FlatBatchResult
from massflow.preprocess.numba.numba_runtime import apply_numba_runtime
from massflow.tools.infer_spectrum_type import SpectrumType, resolve_spectrum_type
from massflow.tools.logger import get_logger

logger = get_logger("massflow.preprocess.async_pipeline_ab")


@dataclass(slots=True)
class FlatChunkAB:
    """Transport object between read and process stages."""

    mz_data: Optional[np.ndarray]
    intensity: np.ndarray
    lengths: np.ndarray


@dataclass(slots=True)
class PreprocessTaskAB:
    """Lazy task registration model for AB-only preprocessing."""

    name: str
    apply_fn: Callable[..., FlatBatchResult] | Callable[..., MSDataManagerImzML]
    scope: TaskScope = "batch"
    kwargs: dict[str, Any] = field(default_factory=dict)
    sequence: int = 0


@dataclass(slots=True)
class PreprocessABResult:
    """Consumed AB-only preprocessing result."""

    spectrum_count: int
    point_count: int
    intensity_sum: float


class PreprocessorAB(PreprocessorAPI):
    """AB-only preprocessing executor: read flat batches, process them, and skip writes."""

    _OPERATION_ORDER: dict[str, int] = {
        "baseline_correction": 10,
        "noise_reduction": 20,
        "normalization": 30,
        "peak_pick": 40,
        "peak_align": 50,
    }
    _PROFILE_ONLY_TASKS = frozenset({"baseline_correction", "noise_reduction", "peak_pick"})

    def __init__(
        self,
        data_manager: MSDataManager,
        *,
        batch_size: int = 256,
        queue_ab_size: int = 4,
        include_mz: bool = False,
        numba_max_threads: Optional[int] = None,
    ):  # pylint: disable=super-init-not-called
        if data_manager is None or batch_size <= 0 or queue_ab_size <= 0:
            logger.error(
                "Invalid parameter values: data_manager=%s, batch_size=%s, queue_ab_size=%s",
                data_manager,
                batch_size,
                queue_ab_size,
            )
            raise ValueError("Invalid parameter values.")

        self.data_manager = data_manager
        self.batch_size = batch_size
        self.queue_ab_size = queue_ab_size
        self.include_mz = include_mz
        self.numba_max_threads = numba_max_threads

        self._tasks: list[PreprocessTaskAB] = []
        self._task_sequence = 0

    def _register_task(
        self,
        name: str,
        *,
        scope: TaskScope = "batch",
        apply_fn: Callable[..., FlatBatchResult] | Callable[..., MSDataManagerImzML],
        **kwargs: Any,
    ) -> "PreprocessorAB":
        self._task_sequence += 1
        self._tasks.append(
            PreprocessTaskAB(
                name=name,
                scope=scope,
                apply_fn=apply_fn,
                kwargs=kwargs,
                sequence=self._task_sequence,
            )
        )
        return self

    def _sorted_tasks(self, spectrum_type: SpectrumType) -> list[PreprocessTaskAB]:
        def sort_key(task: PreprocessTaskAB) -> tuple[int, int]:
            return (self._OPERATION_ORDER.get(task.name, 10_000), task.sequence)

        ordered = sorted(self._tasks, key=sort_key)

        if spectrum_type == "centroid":
            dropped_task_names = [task.name for task in ordered if task.name in self._PROFILE_ONLY_TASKS]
            if dropped_task_names:
                logger.warning(
                    "Detected centroid spectra; dropping unsupported tasks: %s",
                    dropped_task_names,
                )
                ordered = [task for task in ordered if task.name not in self._PROFILE_ONLY_TASKS]

        if ordered:
            task_names = [f"{task.name}:{task.scope}" for task in ordered]
            logger.info("async_pipeline_ab_task_order: %s", task_names)
        else:
            logger.warning("No supported preprocessing tasks remain after task arrangement.")

        return ordered

    def _resolve_input_spectrum_type(self) -> SpectrumType:
        return resolve_spectrum_type(self.data_manager)

    def _should_read_mz(self, tasks: list[PreprocessTaskAB]) -> bool:
        if self.include_mz:
            return True
        return any(
            task.name == "peak_pick"
            or (
                task.name == "normalization"
                and (task.kwargs.get("method") or "").strip().lower() == "ref_numba"
                and task.kwargs.get("mz_flat") is None
            )
            for task in tasks
        )

    def _set_error(
        self,
        *,
        error_holder: list[BaseException],
        error_lock: Lock,
        stop_event: Event,
        exc: BaseException,
    ) -> None:
        with error_lock:
            if not error_holder:
                error_holder.append(exc)
        stop_event.set()

    def _stage_a_reader(
        self,
        *,
        include_mz: bool,
        queue_ab: Queue[Optional[FlatChunkAB]],
        stop_event: Event,
        error_holder: list[BaseException],
        error_lock: Lock,
    ) -> None:
        try:
            for mz_data, intensity, lengths, _ in self.data_manager.flat_generator(
                batch_size=self.batch_size,
                include_mz=include_mz,
            ):
                if stop_event.is_set():
                    break

                queue_ab.put(
                    FlatChunkAB(
                        mz_data=mz_data if mz_data is None else np.asarray(mz_data),
                        intensity=np.asarray(intensity),
                        lengths=np.asarray(lengths, dtype=np.int32),
                    )
                )
        except BaseException as exc:  # pylint: disable=broad-exception-caught
            self._set_error(
                error_holder=error_holder,
                error_lock=error_lock,
                stop_event=stop_event,
                exc=exc,
            )
        finally:
            queue_ab.put(None)

    def _stage_b_processor(
        self,
        *,
        tasks: list[PreprocessTaskAB],
        queue_ab: Queue[Optional[FlatChunkAB]],
        result_holder: list[PreprocessABResult],
        stop_event: Event,
        error_holder: list[BaseException],
        error_lock: Lock,
    ) -> None:
        spectrum_count = 0
        point_count = 0
        intensity_sum = 0.0

        try:
            apply_numba_runtime(override_workers=self.numba_max_threads)
            while True:
                chunk = queue_ab.get()
                if chunk is None:
                    break

                if stop_event.is_set():
                    continue

                mz_data = chunk.mz_data
                intensity = chunk.intensity
                lengths = chunk.lengths

                for task in tasks:
                    batch_apply_fn = cast(Callable[..., FlatBatchResult], task.apply_fn)
                    output = batch_apply_fn(
                        mz_data=mz_data,
                        intensity=intensity,
                        lengths=lengths,
                        **task.kwargs,
                    )
                    mz_data = output.mz_data
                    intensity = output.intensity
                    lengths = output.lengths

                spectrum_count += int(lengths.size)
                point_count += int(np.sum(lengths, dtype=np.int64))
                intensity_sum += float(np.sum(intensity, dtype=np.float64))

            result_holder.append(
                PreprocessABResult(
                    spectrum_count=spectrum_count,
                    point_count=point_count,
                    intensity_sum=intensity_sum,
                )
            )
        except BaseException as exc:  # pylint: disable=broad-exception-caught
            self._set_error(
                error_holder=error_holder,
                error_lock=error_lock,
                stop_event=stop_event,
                exc=exc,
            )

    def _run_ab_task(self, *, tasks: list[PreprocessTaskAB]) -> PreprocessABResult:
        queue_ab: Queue[Optional[FlatChunkAB]] = Queue(maxsize=self.queue_ab_size)
        result_holder: list[PreprocessABResult] = []
        include_mz = self._should_read_mz(tasks)

        stop_event = Event()
        error_holder: list[BaseException] = []
        error_lock = Lock()

        t_a = Thread(
            target=self._stage_a_reader,
            kwargs={
                "include_mz": include_mz,
                "queue_ab": queue_ab,
                "stop_event": stop_event,
                "error_holder": error_holder,
                "error_lock": error_lock,
            },
            name="massflow-stage-a-reader-ab",
            daemon=True,
        )
        t_b = Thread(
            target=self._stage_b_processor,
            kwargs={
                "tasks": tasks,
                "queue_ab": queue_ab,
                "result_holder": result_holder,
                "stop_event": stop_event,
                "error_holder": error_holder,
                "error_lock": error_lock,
            },
            name="massflow-stage-b-processor-ab",
            daemon=True,
        )

        t_a.start()
        t_b.start()

        t_a.join()
        t_b.join()

        if error_holder:
            raise RuntimeError("AB preprocessing pipeline failed.") from error_holder[0]

        if not result_holder:
            return PreprocessABResult(spectrum_count=0, point_count=0, intensity_sum=0.0)
        return result_holder[0]

    def start(self) -> PreprocessABResult:
        """Execute registered batch tasks without writing processed data."""
        if len(self._tasks) == 0:
            raise ValueError("No preprocessing task registered. Please register tasks before start().")

        current_spectrum_type = self._resolve_input_spectrum_type()
        ordered_tasks = self._sorted_tasks(current_spectrum_type)

        if not ordered_tasks:
            raise ValueError("No supported preprocessing tasks remain after task arrangement.")

        dataset_tasks = [task.name for task in ordered_tasks if task.scope != "batch"]
        if dataset_tasks:
            raise NotImplementedError(f"AB preprocessing only supports batch tasks: {dataset_tasks}")

        return self._run_ab_task(tasks=ordered_tasks)


__all__ = ["FlatChunkAB", "PreprocessABResult", "PreprocessTaskAB", "PreprocessorAB"]
