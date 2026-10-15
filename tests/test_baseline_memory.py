import os
import time

import pytest

from massflow.data_manager import MSDataManagerImzML
from massflow.preprocess import BatchPreprocess
from massflow.preprocess.numba.numba_runtime import apply_numba_runtime
from massflow.preprocess.preprocessor import Preprocessor
from massflow.tools.dm_process import dm_process
from massflow.tools.logger import get_logger

logger = get_logger("test_baseline")

ROUNDS = 2
BATCH_BASELINE_METHODS = ["locmin", "snip"]
FLAT_BASELINE_METHODS = ["locmin_numba", "snip_numba"]
THREADS = [1, 2, 4, 8, 16, 32]
FILE_MAX = os.getenv("MASSFLOW_S11_MAX_FILE", "/Users/dre/Desktop/data/example/example.imzML")
FILE_ULTRA = os.getenv("MASSFLOW_S11_ULTRA_FILE", "/Users/dre/Desktop/data/original/original.imzML")
TEMP_DIR = "./temp"


def _run_baseline_reduction_from_dm_process(
    ms_raw_data: MSDataManagerImzML,
    method: str,
    width: int,
):
    batch_kwargs = {"method": method, "width": width, "smooth": "none"}
    if method == "snip":
        batch_kwargs.update(m=5, decreasing=True)

    processed_manager = dm_process(
        ms_raw_data,
        256,
        BatchPreprocess.baseline_correction_batch,
        batch_kwargs,
        TEMP_DIR,
    )
    processed_manager.close()


def _run_baseline_reduction_flat_from_pipeline(
    ms_raw_data: MSDataManagerImzML,
    method: str,
    width: int,
    threads: int,
):
    baseline_kwargs = {"method": method, "width": width, "smooth": "none"}
    if method == "snip_numba":
        baseline_kwargs.update(m=5, decreasing=True)
    processed_manager = (
        Preprocessor(ms_raw_data, batch_size=256, temp_dir=TEMP_DIR, numba_max_threads=threads)
        .baseline_correction(**baseline_kwargs)
        .start()
    )
    processed_manager.close()


class TestBaseline:
    """Baseline correction pipeline benchmarks for Max and Ultra."""

    @pytest.fixture(scope="module", params=[FILE_MAX, FILE_ULTRA], ids=["max", "ultra"])
    def ms_raw_data(self, request):
        with MSDataManagerImzML(filepath=request.param, max_threads=8) as dm:
            dm.load_head_data()
            yield dm

    @pytest.mark.benchmark(timer=time.perf_counter)
    @pytest.mark.parametrize("method", BATCH_BASELINE_METHODS)
    def test_baseline_memory(self, benchmark, method, ms_raw_data):
        """Time Python/NumPy batch reading, baseline correction, and writing."""
        logger.info(f"Benchmarking batch baseline correction method={method}")
        benchmark.extra_info.update(
            batch_size=256, read_threads=ms_raw_data.max_threads,
            numba_threads=apply_numba_runtime(),
        )
        benchmark.pedantic(
            _run_baseline_reduction_from_dm_process,
            args=(ms_raw_data, method, 5),
            rounds=ROUNDS,
            iterations=1,
            warmup_rounds=1,
        )

    @pytest.mark.benchmark(timer=time.perf_counter)
    @pytest.mark.parametrize("method", FLAT_BASELINE_METHODS)
    @pytest.mark.parametrize("threads", THREADS)
    def test_baseline_flat_memory(self, benchmark, method, ms_raw_data, threads):
        """Time flat/Numba baseline correction through Preprocessor."""
        benchmark.pedantic(
            _run_baseline_reduction_flat_from_pipeline,
            args=(ms_raw_data, method, 5, threads),
            rounds=ROUNDS,
            iterations=1,
            warmup_rounds=1,
        )
