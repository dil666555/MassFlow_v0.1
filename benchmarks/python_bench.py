"""One benchmark case; launched by run.py, never by pytest."""
from contextlib import ExitStack
import gc
import json
from pathlib import Path
import sys
import tempfile
import time

from numba import get_num_threads, threading_layer
from massflow.data_manager import MSDataManagerImzML
from massflow.module import MassSpectrumSet
from massflow.preprocess import BatchPreprocess
from massflow.preprocess.flat_pre_fun import FlatPreprocess
from massflow.preprocess.helper.peak_align_helper import reference_computer
from massflow.preprocess.helper.peak_align_helper_v1 import compute_reference
from massflow.preprocess.numba.numba_runtime import apply_numba_runtime
from massflow.preprocess.preprocessor import Preprocessor
from massflow.tools.infer_spectrum_type import set_spectrum_type_metadata

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
# Pipeline: input open/read, one operator, output finalization
# ---------------------------------------------------------------------------
def run_pipeline(job, stack, temp_dir):
    dm = open_input(job, stack)
    kwargs = parameters(job)
    stage = job["case"]["stage"]
    details = {}
    if stage == "align":
        reference, tolerance = compute_reference(
            dm, **kwargs, clear_memory=True,
            batch_size=job["config"]["batch_size"],
        )
        # Both reference builders return fractional tolerance. The direct flat
        # API does not convert ppm numbers; use relative units at every boundary.
        details = {"reference_length": len(reference), "tolerance_relative": tolerance}
        kwargs = dict(reference=reference, tolerance=tolerance, units="relative")

    if job["backend"] == "numba":
        pre = Preprocessor(
            dm, batch_size=job["config"]["batch_size"],
            queue_ab_size=1, queue_bc_size=1, keep_order=True,
            temp_dir=temp_dir, numba_max_threads=job["config"]["numba_threads"],
        )
        out = getattr(pre, PIPELINE_METHODS[stage])(**kwargs).start()
        stack.callback(out.close)
    else:
        # Mirror dm_process, setting output spectrum metadata before opening writer.
        out = MSDataManagerImzML(MassSpectrumSet(), temp_dir=temp_dir)
        stack.callback(out.close)
        out.copy_meta(dm)
        output_type = "centroid" if stage in ("pick", "align") else "profile"
        set_spectrum_type_metadata(out.ms.meta, output_type)
        writer = out.writer
        for batch in dm.batch_generator(batch_size=job["config"]["batch_size"]):
            processed = BATCH_FUNCTIONS[stage](batch_spectra=batch, **kwargs)
            dm.clear_batch_data_memory(batch)
            out.swap_batch_data_out2disk(processed, writer)
        out.close_writer()
        out.load_head_data()
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


def main():
    job = json.loads(Path(sys.argv[1]).read_text())
    cfg = job["config"]
    apply_numba_runtime(override_workers=cfg["numba_threads"])
    scratch = Path(job["scratch"])
    scratch.mkdir(parents=True, exist_ok=True)
    elapsed = []
    outputs = []
    # Only Min/Mid core jobs may allocate a complete input cache.
    with ExitStack() as cache_stack:
        if job["scope"] == "cache_core":
            dm, batches = cache_input(job, cache_stack)
        count = cfg["rounds"]
        for index in range(cfg["warmup"] + count):
            measured = index >= cfg["warmup"]
            with tempfile.TemporaryDirectory(dir=scratch) as tmp, ExitStack() as stack:
                gc.collect()
                if measured and job["mode"] == "memory":
                    memory_marker(job, "ready", index - cfg["warmup"] + 1)
                # GC remains enabled in both Python and R timed calls.
                start = time.perf_counter()
                if job["scope"] == "cache_core":
                    details = run_core(job, dm, batches)
                else:
                    out, expected, details = run_pipeline(job, stack, tmp)
                seconds = time.perf_counter() - start
                if measured and job["mode"] == "memory":
                    memory_marker(job, "done", index - cfg["warmup"] + 1)
                if measured:
                    elapsed.append(seconds)
                    if job["scope"] != "cache_core":
                        outputs.append({**output_info(out, expected), **details})
                    else:
                        outputs.append(details)
                # Close managers and delete output files only after stopping timer.
            if job["scope"] != "cache_core":
                del out  # A warmup manager must not remain alive in measured runs.
    result = {
        "elapsed_seconds": elapsed, "outputs": outputs,
        "numba_threads": get_num_threads(), "numba_threading_layer": threading_layer(),
    }
    Path(job["output"]).write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
