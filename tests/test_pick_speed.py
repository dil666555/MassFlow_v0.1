import time
import pytest

from massflow.data_manager import MSDataManagerImzML
from massflow.preprocess import BatchPreprocess
from massflow.preprocess.flat_pre_fun import FlatPreprocess
from massflow.tools.dm_process import speed_process
from massflow.tools.logger import get_logger

logger = get_logger("test_pick")

ROUNDS = 5
BATCH_PICK_METHODS = ["origin"]
FLAT_PICK_METHODS = ["quantile", "diff", "sd", "mad"]
FILE_MIN = '/Users/dre/Desktop/data/test_data_profile/file_min_profile/file_min_profile.imzML'
FILE_MID = '/Users/dre/Desktop/data/test_data_profile/file_max_profile/file_max_profile.imzML'
FILE_MAX = '/Users/dre/Desktop/data/Example_read/example.imzML'
FILE_ULTRA = "/Users/dre/Desktop/data/original/original.imzML"


def _peak_pick_flat_from_flat_batches(
    flat_batches,
    method: str,
    width: int,
    snr: float,
    return_type: str,
):
    for mz_flat, intensity_flat, lengths in flat_batches:
        _ = FlatPreprocess.peak_pick_flat(
            mz_data=mz_flat,
            intensity=intensity_flat,
            lengths=lengths,
            width=width,
            method=method,
            snr=snr,
            return_type=return_type,
        )

class TestPick:
    """
    Peak pick benchmark tests.
            use:
            uv run pytest ./tests/test_pick_speed.py -k "test_pick_speed or test_pick_flat_speed" -q
    """

    @pytest.fixture(scope="module", params=[FILE_ULTRA])
    def ms_raw_data(self, request) -> MSDataManagerImzML:
        """Fixture providing batch-readable data manager cache for pick benchmarks."""
        data_file_path = request.param
        dm = MSDataManagerImzML(filepath=data_file_path)
        dm.load_head_data()
        for _ in dm.batch_generator(batch_size=512):
            pass
        return dm

    @pytest.fixture(scope="module", params=[FILE_ULTRA])
    def flat_caches(self, request):
        """Fixture providing pre-generated flat arrays for flat pick benchmarks."""
        data_file_path = request.param
        dm = MSDataManagerImzML(filepath=data_file_path)
        dm.load_head_data()

        caches = []
        for mz_data, intensity_flat, lengths, _ in dm.flat_generator(
            batch_size=4096,
            include_mz=True,
            max_threads=16,
        ):
            caches.append((mz_data, intensity_flat, lengths))

        dm.close()
        return caches

    @pytest.mark.benchmark(timer=time.perf_counter)
    @pytest.mark.parametrize("method", BATCH_PICK_METHODS)
    def test_pick_speed(self, benchmark, method, ms_raw_data):
        """Benchmark batch peak pick via speed_process."""
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
            speed_process,
            args=(
                ms_raw_data,
                1024,
                BatchPreprocess.peak_pick_batch,
                batch_kwargs,
            ),
            rounds=ROUNDS,
            iterations=1,
            warmup_rounds=1,
        )

    @pytest.mark.benchmark(timer=time.perf_counter)
    @pytest.mark.parametrize("method", FLAT_PICK_METHODS)
    def test_pick_flat_speed(self, benchmark, method, flat_caches):
        """Benchmark flat peak pick via peak_pick_flat."""
        logger.info(f"Benchmarking flat peak pick method={method}")

        flat_kwargs = {
            "method": method,
            "width": 5,
            "snr": 2.0,
            "return_type": "height",
        }

        benchmark.pedantic(
            _peak_pick_flat_from_flat_batches,
            args=(
                flat_caches,
                flat_kwargs["method"],
                flat_kwargs["width"],
                flat_kwargs["snr"],
                flat_kwargs["return_type"],
            ),
            rounds=ROUNDS,
            iterations=1,
            warmup_rounds=1,
        )
