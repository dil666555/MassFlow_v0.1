import time
import pytest
from massflow.data_manager import MSDataManagerImzML
from massflow.preprocess import BatchPreprocess
from massflow.preprocess.preprocessor import Preprocessor
from massflow.tools.dm_process import dm_process
from massflow.tools.logger import get_logger

logger = get_logger("massflow.test.test_noise_reduction")

ROUNDS = 5
BATCH_NR_METHODS = ["ma", "gaussian", "savgol"]
FLAT_NR_METHODS = ["ma_numba", "gaussian_numba", "savgol_numba"]
FILE_MIN = '/Users/dre/Desktop/data/test_data_profile/file_min_profile/file_min_profile.imzML'
FILE_MAX = '/Users/dre/Desktop/data/test_data_profile/file_max_profile/file_max_profile.imzML'
TEMP_DIR = "./temp"


def _run_noise_reduction_from_dm_process(
    ms_raw_data: MSDataManagerImzML,
    method: str,
    window: int,
):
    batch_kwargs = {
        "method": method,
        "window": window,
    }

    processed_manager = dm_process(
        ms_raw_data,
        256,
        BatchPreprocess.noise_reduction_batch,
        batch_kwargs,
        TEMP_DIR,
    )
    processed_manager.close()

def _run_noise_reduction_flat_from_pipeline(
    ms_raw_data: MSDataManagerImzML,
    method: str,
    window: int,
):
    processed_manager = (
        Preprocessor(ms_raw_data, batch_size=256, temp_dir=TEMP_DIR)
        .noise_reduction(method=method, window=window)
        .start()
    )

    processed_manager.close()

class TestNoiseReductionAPI:
    """
    Test suite for noise reduction API functionality and performance.
        use :
        uv run  pytest ./tests/test_noise_reduction.py -k "test_nr_speed or test_nr_flat_speed" -q
    """

    @pytest.fixture(scope="module", params=[FILE_MIN, FILE_MAX])
    def ms_raw_data(self, request) -> MSDataManagerImzML:
        """Fixture providing MSDataManagerImzML instance with fully initialized spectra for noise reduction tests."""
        data_file_path = request.param
        dm = MSDataManagerImzML(filepath=data_file_path)
        dm.load_head_data()
        return dm

    @pytest.mark.benchmark(timer=time.perf_counter)
    @pytest.mark.parametrize("method", BATCH_NR_METHODS)
    def test_nr_memory(
        self,
        benchmark,
        method,
        ms_raw_data
    ):
        """Test noise reduction speed for different methods."""
        logger.info(f"Benchmarking noise reduction method={method}")

        benchmark.pedantic(
            _run_noise_reduction_from_dm_process,
            args=(ms_raw_data, method, 5),
            rounds=ROUNDS,
            iterations=1,
            warmup_rounds=1,
        )

    @pytest.mark.benchmark(timer=time.perf_counter)
    @pytest.mark.parametrize("method", FLAT_NR_METHODS)
    def test_nr_flat_memory(
        self,
        benchmark,
        method,
        ms_raw_data
    ):
        """Test flat noise reduction speed using pre-generated flat batches."""
        logger.info(f"Benchmarking flat noise reduction method={method}")

        flat_kwargs = {
            "method": method,
            "window": 5,
        }

        benchmark.pedantic(
            _run_noise_reduction_flat_from_pipeline,
            args=(ms_raw_data, flat_kwargs["method"], flat_kwargs["window"]),
            rounds=ROUNDS,
            iterations=1,
            warmup_rounds=1,
        )
