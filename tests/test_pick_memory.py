import time
import pytest

from massflow.data_manager import MSDataManagerImzML
from massflow.preprocess import BatchPreprocess
from massflow.preprocess.preprocessor import Preprocessor
from massflow.tools.dm_process import dm_process
from massflow.tools.logger import get_logger

logger = get_logger("test_pick")

ROUNDS = 5
BATCH_PICK_METHODS = ["origin"]
FLAT_PICK_METHODS = ["quantile", "diff"]
FILE_MIN = '/Users/dre/Desktop/data/200TopL, 170TopR, 190BottomL, 180BottomR-profile/200TopL, 170TopR, 190BottomL, 180BottomR-profile.imzML'
FILE_MAX = '/Users/dre/Desktop/data/80TopL, 50TopR, 70BottomL, 60BottomR-profile/80TopL, 50TopR, 70BottomL, 60BottomR-profile.imzML'
TEMP_DIR = "./temp"


def _run_peak_pick_from_pipeline(
    ms_raw_data: MSDataManagerImzML,
    method: str,
    width: int,
    snr: float,
    return_type: str,
):
    processed_manager = (
        Preprocessor(ms_raw_data, batch_size=256, temp_dir=TEMP_DIR)
        .peak_pick(
            method=method,
            width=width,
            snr=snr,
            return_type=return_type,
        )
        .start()
    )

    processed_manager.close()


class TestPick:
    """
    Peak pick benchmark tests.
            use:
            uv run pytest ./tests/test_pick_memory.py -k "test_pick_memory or test_pick_flat_memory" -q
    """

    @pytest.fixture(scope="module", params=[FILE_MIN, FILE_MAX])
    def ms_raw_data(self, request) -> MSDataManagerImzML:
        """Fixture providing batch-readable data manager cache for pick benchmarks."""
        data_file_path = request.param
        dm = MSDataManagerImzML(filepath=data_file_path)
        dm.load_head_data()
        return dm

    @pytest.mark.benchmark(timer=time.perf_counter)
    @pytest.mark.parametrize("method", BATCH_PICK_METHODS)
    def test_pick_memory(self, benchmark, method, ms_raw_data):
        """Benchmark batch peak pick via dm_process."""
        logger.info(f"Benchmarking batch peak pick method={method}")

        batch_kwargs = {
            "width": 2,
            "method": method,
            "relheight": 0.012,
            "snr": 2.0,
            "return_type": "height",
            "use_numba": True,
        }

        benchmark.pedantic(
            dm_process,
            args=(
                ms_raw_data,
                256,
                BatchPreprocess.peak_pick_batch,
                batch_kwargs,
                TEMP_DIR,
            ),
            rounds=ROUNDS,
            iterations=1,
            warmup_rounds=1,
        )

    @pytest.mark.benchmark(timer=time.perf_counter)
    @pytest.mark.parametrize("method", FLAT_PICK_METHODS)
    def test_pick_flat_memory(self, benchmark, method, ms_raw_data):
        """Benchmark flat peak pick via peak_pick pipeline."""
        logger.info(f"Benchmarking flat peak pick method={method}")

        flat_kwargs = {
            "method": method,
            "width": 5,
            "snr": 2.0,
            "return_type": "height",
        }

        benchmark.pedantic(
            _run_peak_pick_from_pipeline,
            args=(
                ms_raw_data,
                flat_kwargs["method"],
                flat_kwargs["width"],
                flat_kwargs["snr"],
                flat_kwargs["return_type"],
            ),
            rounds=ROUNDS,
            iterations=1,
            warmup_rounds=1,
        )
