import time
import pytest
from massflow.data_manager import MSDataManagerImzML
from massflow.preprocess import BatchPreprocess
from massflow.preprocess.flat_pre_fun import FlatPreprocess
from massflow.r_preprocess.adapter import CardinalAdapter
from massflow.tools.dm_process import speed_process
from massflow.tools.logger import get_logger

logger = get_logger("test_normalization")

ROUNDS = 5
BATCH_NORM_METHODS = ["tic", "rms"]
FLAT_NORM_METHODS = ["tic_numba", "rms_numba", "ref_numba"]
CARDINAL_NORM_METHODS = ["tic", "rms"]
# FILE_MIN = '/Users/dre/Desktop/data/test_data_profile/file_min_profile/file_min_profile.imzML'
# FILE_MAX = '/Users/dre/Desktop/data/test_data_profile/file_max_profile/file_max_profile.imzML'
FILE_MMAX = '/Users/dre/Desktop/data/Example_read/example.imzML'

def _normalization_flat_from_flat_batches(
    flat_batches,
    method: str,
    scale: float | None = None,
    ref_tolerance: float = 0.1,
):
    for mz_flat, intensity_flat, lengths, ref in flat_batches:
        kwargs = {
            "mz_data": mz_flat,
            "intensity": intensity_flat,
            "method": method,
            "scale": scale,
            "lengths": lengths,
        }
        if method == "ref_numba":
            kwargs["mz_flat"] = mz_flat
            kwargs["ref"] = ref
            kwargs["ref_tolerance"] = ref_tolerance

        _ = FlatPreprocess.normalization_flat(**kwargs)


def _normalization_from_cardinal(
    dm: MSDataManagerImzML,
    method: str,
):
    _ = CardinalAdapter.normalization(
        dm,
        method=method,
    )


class TestNormalizationAPI:
    """Normalization API tests: memory, speed, consistency, and normalization invariants."""

    @pytest.fixture(scope="module", params=[FILE_MMAX])
    def ms_raw_data(self, request) -> MSDataManagerImzML:
        data_file_path = request.param
        dm = MSDataManagerImzML(filepath=data_file_path)
        dm.load_head_data()
        for _ in dm.batch_generator(batch_size=512):
            pass
        return dm

    @pytest.fixture(scope="module")
    def flat_caches(self, ms_raw_data):

        caches = []
        for mz_data, intensity_flat, lengths, _ in ms_raw_data.flat_generator(
            batch_size=4096,
            include_mz=True,
            max_threads=16,
        ):
            ref = float(mz_data[mz_data.size // 2]) if mz_data is not None and mz_data.size > 0 else None
            caches.append((mz_data, intensity_flat, lengths, ref))

        return caches

    @pytest.mark.benchmark(timer=time.perf_counter)
    @pytest.mark.parametrize("method", BATCH_NORM_METHODS)
    def test_norm_batch_speed(
        self,
        benchmark,
        method,
        ms_raw_data,
    ):
        logger.info("Benchmarking batch normalization method=%s", method)

        batch_kwargs = {
            "method": method,
        }

        benchmark.pedantic(
            speed_process,
            args=(ms_raw_data, 4096, BatchPreprocess.normalization_batch, batch_kwargs),
            rounds=ROUNDS,
            iterations=1,
            warmup_rounds=1,
        )

    @pytest.mark.benchmark(timer=time.perf_counter)
    @pytest.mark.parametrize("method", FLAT_NORM_METHODS)
    def test_norm_flat_speed(
        self,
        benchmark,
        method,
        flat_caches,
    ):
        logger.info("Benchmarking flat normalization method=%s", method)

        benchmark.pedantic(
            _normalization_flat_from_flat_batches,
            args=(flat_caches, method),
            rounds=ROUNDS,
            iterations=1,
            warmup_rounds=1,
        )

    @pytest.mark.benchmark(timer=time.perf_counter)
    @pytest.mark.parametrize("method", CARDINAL_NORM_METHODS)
    def test_norm_cardinal_speed(
        self,
        benchmark,
        method,
        ms_raw_data,
    ):
        logger.info("Benchmarking Cardinal normalization method=%s", method)

        benchmark.pedantic(
            _normalization_from_cardinal,
            args=(ms_raw_data, method),
            rounds=ROUNDS,
            iterations=1,
            warmup_rounds=1,
        )
