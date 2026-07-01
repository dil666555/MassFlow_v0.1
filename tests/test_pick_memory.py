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
FLAT_PICK_METHODS = ["sd"]
NUMBA_THREADS = [1, 2, 4, 8, 16, 32]
FLAT_PICK_CASES = [
    pytest.param(method, "forward", threads, id=f"{method}-forward-{threads}")
    for method in FLAT_PICK_METHODS
    for threads in NUMBA_THREADS
]
# FILE_MIN = "/home/Share_Space/data_local/min/file_min_profile.imzML"
# FILE_MID = "/home/Share_Space/data_local/mid/file_mid_profile.imzML"
FILE_MAX = "/home/Share_Space/data_local/Example_read/example.imzML"
# FILE_ULTRA = "/home/Share_Space/data_local/original/original.imzML"
TEMP_DIR = "./temp"


def _run_peak_pick_from_dm_process(
    ms_raw_data: MSDataManagerImzML,
    method: str,
    width: int,
    relheight: float,
    snr: float,
    return_type: str,
):
    batch_kwargs = {
        "width": width,
        "method": method,
        "relheight": relheight,
        "snr": snr,
        "return_type": return_type,
        "use_numba": True,
    }

    processed_manager = dm_process(
        ms_raw_data,
        256,
        BatchPreprocess.peak_pick_batch,
        batch_kwargs,
        TEMP_DIR,
    )
    processed_manager.close()

def _run_peak_pick_from_pipeline(
    ms_raw_data: MSDataManagerImzML,
    method: str,
    width: int,
    snr: float,
    return_type: str,
    run_order: str,
    threads: int,
):
    processed_manager = (
        Preprocessor(
            ms_raw_data,
            batch_size=64,
            temp_dir=f"{TEMP_DIR}/pick_flat_{run_order}_threads_{threads}",
            numba_max_threads=threads,
        )
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

    @pytest.fixture(scope="module", params=[FILE_MAX])
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

        benchmark.pedantic(
            _run_peak_pick_from_dm_process,
            args=(ms_raw_data, method, 2, 0.012, 2.0, "height"),
            rounds=ROUNDS,
            iterations=1,
            warmup_rounds=1,
        )

    @pytest.mark.benchmark(timer=time.perf_counter)
    @pytest.mark.parametrize("method,run_order,threads", FLAT_PICK_CASES)
    def test_pick_flat_memory(self, benchmark, method, run_order, threads, ms_raw_data):
        """Benchmark flat peak pick via peak_pick pipeline."""
        logger.info(
            f"Benchmarking flat peak pick method={method}, run_order={run_order}, threads={threads}"
        )

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
                run_order,
                threads,
            ),
            rounds=ROUNDS,
            iterations=1,
            warmup_rounds=1,
        )
