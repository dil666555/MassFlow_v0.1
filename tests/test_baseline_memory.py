import time
import pytest

from massflow.data_manager import MSDataManagerImzML
from massflow.preprocess import BatchPreprocess
from massflow.preprocess.preprocessor import Preprocessor
from massflow.tools.dm_process import dm_process
from massflow.tools.logger import get_logger

logger = get_logger("test_baseline")

ROUNDS = 5
BATCH_BASELINE_METHODS = ["locmin", "snip"]
FLAT_BASELINE_METHODS = ["locmin_numba", "snip_numba"]
FILE_MIN = '/Users/dre/Desktop/data/200TopL, 170TopR, 190BottomL, 180BottomR-profile/200TopL, 170TopR, 190BottomL, 180BottomR-profile.imzML'
FILE_MAX = '/Users/dre/Desktop/data/80TopL, 50TopR, 70BottomL, 60BottomR-profile/80TopL, 50TopR, 70BottomL, 60BottomR-profile.imzML'

def _run_baseline_reduction_from_pipeline(
    ms_raw_data: MSDataManagerImzML,
    method: str,
    width: int,
):
    processed_manager = (
        Preprocessor(ms_raw_data, batch_size=256)
        .baseline_correction(method=method, width=width)
        .start()
    )

    processed_manager.close()


class TestBaseline:
    """
    Baseline correction benchmark tests.
            use:
            uv run pytest ./tests/test_baseline.py -k "test_baseline_speed or test_baseline_flat_speed" -q
    """

    @pytest.fixture(scope="module", params=[FILE_MIN, FILE_MAX])
    def ms_raw_data(self, request) -> MSDataManagerImzML:
        """Fixture providing batch-readable data manager cache for baseline benchmarks."""
        data_file_path = request.param
        dm = MSDataManagerImzML(filepath=data_file_path)
        dm.load_head_data()
        return dm

    @pytest.mark.benchmark(timer=time.perf_counter)
    @pytest.mark.parametrize("method", BATCH_BASELINE_METHODS)
    def test_baseline_memory(self, benchmark, method, ms_raw_data):
        """Benchmark batch baseline correction via dm_process."""
        logger.info(f"Benchmarking batch baseline correction method={method}")

        batch_kwargs = {
            "method": method,
            "width": 5,
            "smooth": "none",
        }

        benchmark.pedantic(
            dm_process,
            args=(
                ms_raw_data,
                256,
                BatchPreprocess.baseline_correction_batch,
                batch_kwargs,
            ),
            rounds=ROUNDS,
            iterations=1,
            warmup_rounds=1,
        )

    @pytest.mark.benchmark(timer=time.perf_counter)
    @pytest.mark.parametrize("method", FLAT_BASELINE_METHODS)
    def test_baseline_flat_memory(self, ms_raw_data, benchmark, method):
        """Benchmark flat numba baseline reduction via baseline_reduction_flat."""
        logger.info(f"Benchmarking flat baseline reduction method={method}")

        flat_kwargs = {
            "method": method,
            "width": 5,
        }

        benchmark.pedantic(
            _run_baseline_reduction_from_pipeline,
            args=(ms_raw_data, flat_kwargs["method"], flat_kwargs["width"]),
            rounds=ROUNDS,
            iterations=1,
            warmup_rounds=1,
        )
