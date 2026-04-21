import time
import numpy as np
import pytest

from massflow.data_manager import MSDataManagerImzML
from massflow.preprocess import BatchPreprocess
from massflow.preprocess.flat_pre_fun import FlatPreprocess
from massflow.tools.dm_process import speed_process
from massflow.tools.logger import get_logger

logger = get_logger("test_align")

ROUNDS = 5
ALIGN_UNITS = ["mz"]
FILE_MIN = '/Users/dre/Desktop/data/200TopL, 170TopR, 190BottomL, 180BottomR-profile/200TopL, 170TopR, 190BottomL, 180BottomR-profile.imzML'
FILE_MAX = '/Users/dre/Desktop/data/80TopL, 50TopR, 70BottomL, 60BottomR-profile/80TopL, 50TopR, 70BottomL, 60BottomR-profile.imzML'


def _resolve_alignment_reference(ms_raw_data: MSDataManagerImzML) -> np.ndarray:
    shared_mz = ms_raw_data.ms.shared_mz_list
    if shared_mz is not None and len(shared_mz) > 0:
        return np.asarray(shared_mz, dtype=np.float64)

    for mz_data, _, _, _ in ms_raw_data.flat_generator(
        batch_size=1,
        include_mz=True,
        max_threads=16,
    ):
        if mz_data is not None and mz_data.size > 0:
            return np.asarray(mz_data, dtype=np.float64)

    raise ValueError("Unable to infer reference m/z axis for alignment")


def _peak_align_flat_from_flat_batches(
    flat_batches,
    reference: np.ndarray,
    tolerance: float,
    units: str,
):
    for mz_flat, intensity_flat, lengths in flat_batches:
        _ = FlatPreprocess.peak_align_flat(
            mz_data=mz_flat,
            intensity=intensity_flat,
            lengths=lengths,
            reference=reference,
            tolerance=tolerance,
            units=units,
        )


class TestAlign:
    """
    Peak align benchmark tests.
            use:
            uv run pytest ./tests/test_align_speed.py -k "test_align_speed or test_align_flat_speed" -q
    """

    @pytest.fixture(scope="module", params=[FILE_MIN, FILE_MAX])
    def ms_raw_data(self, request) -> MSDataManagerImzML:
        """Fixture providing batch-readable data manager cache for align benchmarks."""
        data_file_path = request.param
        dm = MSDataManagerImzML(filepath=data_file_path)
        dm.load_head_data()
        for _ in dm.batch_generator(batch_size=512):
            pass
        return dm

    @pytest.fixture(scope="module", params=[FILE_MIN, FILE_MAX])
    def flat_caches(self, request):
        """Fixture providing pre-generated flat arrays and reference axis for align benchmarks."""
        data_file_path = request.param
        dm = MSDataManagerImzML(filepath=data_file_path)
        dm.load_head_data()

        reference = _resolve_alignment_reference(dm)
        caches = []
        for mz_data, intensity_flat, lengths, _ in dm.flat_generator(
            batch_size=4096,
            include_mz=True,
            max_threads=16,
        ):
            caches.append((mz_data, intensity_flat, lengths))

        return caches, reference

    @pytest.mark.benchmark(timer=time.perf_counter)
    @pytest.mark.parametrize("units", ALIGN_UNITS)
    def test_align_speed(self, benchmark, units, ms_raw_data):
        """Benchmark batch peak align via speed_process."""
        logger.info(f"Benchmarking batch peak align units={units}")

        reference = _resolve_alignment_reference(ms_raw_data)
        batch_kwargs = {
            "reference": reference,
            "tolerance": 0.1,
            "units": units,
        }

        benchmark.pedantic(
            speed_process,
            args=(
                ms_raw_data,
                1024,
                BatchPreprocess.peak_align_batch,
                batch_kwargs,
            ),
            rounds=ROUNDS,
            iterations=1,
            warmup_rounds=1,
        )

    @pytest.mark.benchmark(timer=time.perf_counter)
    @pytest.mark.parametrize("units", ALIGN_UNITS)
    def test_align_flat_speed(self, benchmark, units, flat_caches):
        """Benchmark flat peak align via peak_align_flat."""
        logger.info(f"Benchmarking flat peak align units={units}")

        flat_batches, reference = flat_caches

        benchmark.pedantic(
            _peak_align_flat_from_flat_batches,
            args=(flat_batches, reference, 0.1, units),
            rounds=ROUNDS,
            iterations=1,
            warmup_rounds=1,
        )
