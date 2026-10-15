"""Python/Numba benchmarks using the original pytest-benchmark entry pattern."""
from contextlib import ExitStack
import json
from pathlib import Path
import time

import pytest
from numba import get_num_threads, threading_layer
from massflow.data_manager import MSDataManagerImzML
from massflow.preprocess import BatchPreprocess
from massflow.preprocess.flat_pre_fun import FlatPreprocess
from massflow.preprocess.helper.peak_align_helper import reference_computer
from massflow.preprocess.numba.numba_runtime import apply_numba_runtime
from massflow.preprocess.preprocessor import Preprocessor
from massflow.tools.dm_process import dm_process
from peak_align_numpy import compute_reference

BATCH_FUNCTIONS = {
    "baseline": BatchPreprocess.baseline_correction_batch,
    "noise": BatchPreprocess.noise_reduction_batch,
    "normalization": BatchPreprocess.normalization_batch,
    "pick": BatchPreprocess.peak_pick_batch,
    "align": BatchPreprocess.peak_align_batch,
}
FLAT_FUNCTIONS = {
    "baseline": FlatPreprocess.baseline_reduction_flat,
    "noise": FlatPreprocess.noise_reduction_flat,
    "normalization": FlatPreprocess.normalization_flat,
    "pick": FlatPreprocess.peak_pick_flat,
    "align": FlatPreprocess.peak_align_flat,
}
PIPELINE_METHODS = {
    "baseline": "baseline_correction", "noise": "noise_reduction",
    "normalization": "normalization", "pick": "peak_pick", "align": "peak_align",
}


def open_input(job, stack):
    dm = stack.enter_context(MSDataManagerImzML(
        filepath=job["input"], max_threads=job["config"]["read_threads"],
    ))
    dm.load_head_data()
    return dm


def parameters(job):
    kwargs = dict(job["case"][job["backend"]])
    if job["case"]["id"] == "reference":
        kwargs.update(ref=job["reference"], ref_tolerance=job["ref_tolerance"])
    return kwargs


# ---------------------------------------------------------------------------
# Pipeline operators; input setup is performed by the pytest fixture
# ---------------------------------------------------------------------------
def run_pipeline(job, stack, temp_dir, dm=None, reference_batches=None):
    if dm is None:
        dm = open_input(job, stack)
    kwargs = parameters(job)
    stage = job["case"]["stage"]
    details = {}
    if stage == "align":
        if job["backend"] == "python":
            reference, tolerance = compute_reference(
                dm, **kwargs, clear_memory=True,
                batch_size=job["config"]["batch_size"],
            )
        else:
            reference, tolerance = reference_computer(reference_batches, **kwargs)
        # Both reference builders return fractional tolerance. The direct flat
        # API does not convert ppm numbers; use relative units at every boundary.
        details = {"reference_length": len(reference), "tolerance_relative": tolerance}
        kwargs = dict(reference=reference, tolerance=tolerance, units="relative")

    if job["backend"] == "numba":
        pre = Preprocessor(
            dm, batch_size=job["config"]["batch_size"],
            queue_ab_size=1, queue_bc_size=1,
            temp_dir=temp_dir, numba_max_threads=job["config"]["numba_threads"],
        )
        out = getattr(pre, PIPELINE_METHODS[stage])(**kwargs).start()
        stack.callback(out.close)
    else:
        out = dm_process(
            dm, job["config"]["batch_size"], BATCH_FUNCTIONS[stage], kwargs,
            temp_dir, numba_max_threads=job["config"]["numba_threads"],
        )
        stack.callback(out.close)
    return out, len(dm.ms), details


def output_info(out, expected):
    # Header/count checks and byte counts are outside the timer/RSS window.
    if len(out.ms) != expected:
        raise ValueError(f"Output spectrum count {len(out.ms)} != input {expected}")
    return {
        "spectra": expected,
        "imzml_bytes": Path(out.imzml_filepath).stat().st_size,
        "ibd_bytes": Path(out.ibd_filepath).stat().st_size,
        "output_mz_dtype": str(out.parser.mzPrecision),
        "output_intensity_dtype": str(out.parser.intensityPrecision),
    }


# ---------------------------------------------------------------------------
# Core: cache creation is outside every timed call
# ---------------------------------------------------------------------------
class CachedSpectra:
    """Reference-builder view of already loaded batches; never opens files."""

    def __init__(self, ms, batches):
        self.ms = ms
        self.batches = batches

    def batch_generator(self, batch_size):
        return iter(self.batches)


def cache_input(job, stack):
    dm = open_input(job, stack)
    size = job["config"]["batch_size"]
    if job["backend"] == "python":
        batches = list(dm.batch_generator(batch_size=size))
        dm.close()
        return CachedSpectra(dm.ms, batches), batches
    include_mz = job["case"]["id"] in ("reference", "align") or job["case"]["stage"] == "pick"
    batches = [
        (mz, intensity, lengths)
        for mz, intensity, lengths, _ in dm.flat_generator(
            batch_size=size, include_mz=include_mz,
        )
    ]
    dm.close()
    return dm, batches


def run_core(job, dm, batches):
    kwargs = parameters(job)
    stage = job["case"]["stage"]
    details = {}
    if stage == "align":
        if job["backend"] == "python":
            reference, tolerance = compute_reference(
                dm, **kwargs, clear_memory=False,
                batch_size=job["config"]["batch_size"],
            )
        else:
            reference, tolerance = reference_computer(batches, **kwargs)
        details = {"reference_length": len(reference), "tolerance_relative": tolerance}
        kwargs = dict(reference=reference, tolerance=tolerance, units="relative")
    if job["backend"] == "python":
        for batch in batches:
            BATCH_FUNCTIONS[stage](batch_spectra=batch, **kwargs)
    else:
        for mz, intensity, lengths in batches:
            FLAT_FUNCTIONS[stage](mz_data=mz, intensity=intensity, lengths=lengths, **kwargs)
    return details


def memory_marker(job, name, round_number):
    control = Path(job["control"])
    (control / f"{name}-{round_number}").touch()
    ack = "go" if name == "ready" else "collected"
    while not (control / f"{ack}-{round_number}").exists():
        time.sleep(0.005)


@pytest.fixture
def prepared_input(job):
    cfg = job["config"]
    apply_numba_runtime(override_workers=cfg["numba_threads"])
    scratch = Path(job["scratch"])
    scratch.mkdir(parents=True, exist_ok=True)
    with ExitStack() as cache_stack:
        if job["scope"] == "cache_core":
            dm, batches = cache_input(job, cache_stack)
        else:
            dm = open_input(job, cache_stack)
            batches = None
            if job["backend"] == "numba" and job["case"]["id"] == "align":
                # Match the original flat_caches fixture on picked spectra.
                batches = [(mz, intensity, lengths)
                           for mz, intensity, lengths, _ in dm.flat_generator(
                               batch_size=cfg["batch_size"], include_mz=True)]
        yield dm, batches


@pytest.mark.benchmark(timer=time.perf_counter)
def test_operator(benchmark, job, prepared_input):
    dm, batches = prepared_input
    cfg = job["config"]

    def target():
        if job["scope"] == "cache_core":
            return run_core(job, dm, batches)
        with ExitStack() as stack:
            _, _, details = run_pipeline(job, stack, job["scratch"], dm, batches)
        # As in the original memory.py targets, output close is inside timing.
        return details

    timed_target = target
    if job["mode"] == "memory":
        calls = 0

        def measured_target():
            nonlocal calls
            calls += 1
            round_number = calls - cfg["warmup"]
            if round_number > 0:
                memory_marker(job, "ready", round_number)
            details = target()
            if round_number > 0:
                memory_marker(job, "done", round_number)
            return details

        timed_target = measured_target
    details = benchmark.pedantic(
        timed_target, rounds=cfg["rounds"], iterations=1,
        warmup_rounds=cfg["warmup"],
    )
    result = {
        "outputs": [details], "numba_threads": get_num_threads(),
        "numba_threading_layer": threading_layer(),
    }
    benchmark.extra_info.update(
        dataset=job["dataset"], method=job["case"]["id"], scope=job["scope"],
        batch_size=cfg["batch_size"], read_threads=cfg["read_threads"],
        worker=result,
    )
    if "output" in job:
        Path(job["output"]).write_text(json.dumps(result, indent=2) + "\n")
