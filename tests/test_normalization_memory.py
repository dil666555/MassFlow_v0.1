import time
import numpy as np
import pytest

from massflow.data_manager import MSDataManagerImzML
from massflow.preprocess import BatchPreprocess
from massflow.preprocess.preprocessor import Preprocessor
from massflow.tools.dm_process import dm_process
from massflow.tools.logger import get_logger

logger = get_logger("test_normalization")

ROUNDS = 2
BATCH_NORM_METHODS = ["tic", "rms"]
FLAT_NORM_METHODS = ["tic_numba", "rms_numba", "ref_numba"]
# FILE_MIN = '/Users/dre/Desktop/data/test_data_profile/file_min_profile/file_min_profile.imzML'
FILE_MID = '/Users/dre/Desktop/data/mid/file_mid_profile.imzml'
# FILE_MAX = '/Users/dre/Desktop/data/Example_read/example.imzML'
# FILE_ULTRA = '/Users/dre/Desktop/data/original/original.imzML'
TEMP_DIR = "./temp"

def _resolve_ref_inputs(ms_raw_data: MSDataManagerImzML) -> tuple[np.ndarray, float]:
    for mz_data, _, _, _ in ms_raw_data.flat_generator(
        batch_size=1,
        include_mz=True,
        max_threads=16,
    ):
        if mz_data is not None and mz_data.size > 0:
            ref = float(mz_data[mz_data.size // 2])
            return mz_data, ref

    raise ValueError("Unable to infer mz_flat/ref for ref_numba normalization")


def _run_normalization_from_dm_process(
    ms_raw_data: MSDataManagerImzML,
    method: str,
):
    batch_kwargs = {
        "method": method,
    }

    processed_manager = dm_process(
        ms_raw_data,
        256,
        BatchPreprocess.normalization_batch,
        batch_kwargs,
        TEMP_DIR,
    )
    processed_manager.close()


def _run_normalization_from_pipeline(
    ms_raw_data: MSDataManagerImzML,
    method: str,
    scale: float | None = None,
    ref_tolerance: float = 0.1,
    mz_flat: np.ndarray | None = None,
    ref: float | None = None,
):
    norm_kwargs = {
        "method": method,
        "scale": scale,
    }

    if method == "ref_numba":
        if ref is None:
            raise ValueError("ref_numba requires ref")
        if mz_flat is not None:
            norm_kwargs["mz_flat"] = mz_flat
        norm_kwargs["ref"] = ref
        norm_kwargs["ref_tolerance"] = ref_tolerance

    processed_manager = (
        Preprocessor(ms_raw_data, batch_size=128, temp_dir=TEMP_DIR, queue_ab_size=1, queue_bc_size=1)
        .normalization(**norm_kwargs)
        .start()
    )

    processed_manager.close()

class TestNormalization:
    """
    Normalization benchmark tests.
            use:
            uv run pytest ./tests/test_normalization_memory.py -k "test_normalization_memory or test_normalization_flat_memory" -q
    """

    @pytest.fixture(scope="module", params=[FILE_MID])
    def ms_raw_data(self, request) -> MSDataManagerImzML:
        """Fixture providing batch-readable data manager cache for normalization benchmarks."""
        data_file_path = request.param
        dm = MSDataManagerImzML(filepath=data_file_path)
        dm.load_head_data()
        return dm

    @pytest.mark.benchmark(timer=time.perf_counter)
    @pytest.mark.parametrize("method", BATCH_NORM_METHODS)
    def test_normalization_memory(self, benchmark, method, ms_raw_data):
        """Benchmark batch normalization via dm_process."""
        logger.info(f"Benchmarking batch normalization method={method}")

        benchmark.pedantic(
            _run_normalization_from_dm_process,
            args=(ms_raw_data, method),
            rounds=ROUNDS,
            iterations=1,
            warmup_rounds=1,
        )

    @pytest.mark.benchmark(timer=time.perf_counter)
    @pytest.mark.parametrize("method", FLAT_NORM_METHODS)
    def test_normalization_flat_memory(self, ms_raw_data, benchmark, method):
        """Benchmark flat numba normalization via normalization pipeline."""
        logger.info(f"Benchmarking flat normalization method={method}")

        mz_flat = None
        ref = None
        if method == "ref_numba":
            _, ref = _resolve_ref_inputs(ms_raw_data)

        benchmark.pedantic(
            _run_normalization_from_pipeline,
            args=(ms_raw_data, method, None, 0.1, mz_flat, ref),
            rounds=ROUNDS,
            iterations=1,
            warmup_rounds=1,
        )
