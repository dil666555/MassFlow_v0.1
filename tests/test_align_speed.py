import time
import pytest

from massflow.data_manager import MSDataManagerImzML
from massflow.preprocess.helper.peak_align_helper import reference_computer
from massflow.preprocess.helper.peak_align_helper_v1 import compute_reference
from massflow.preprocess import BatchPreprocess
from massflow.preprocess.flat_pre_fun import FlatPreprocess
from massflow.preprocess.preprocessor import Preprocessor
from massflow.tools.dm_process import speed_process
from massflow.tools.logger import get_logger

logger = get_logger("test_align")

ROUNDS = 2
ALIGN_UNITS = ["ppm"]
BINFUN = ["min"]
# FILE_MIN = "/Users/dre/Desktop/data/min/file_min_profile.imzML"
# FILE_MID = "/Users/dre/Desktop/data/mid/file_mid_profile.imzML"
# FILE_MAX = "/Users/dre/Desktop/data/Example_read/example.imzML"
FILE_ULTRA = "/Users/dre/Desktop/data/original/original.imzML"

def _run_peak_align_from_dm_process(
    ms_raw_data: MSDataManagerImzML,
    batch_size: int,
    units: str,
    binfun: str,
):
    reference, tolerance = compute_reference(ms_raw_data, units=units, clear_memory=False, binfun=binfun)
    tolerance = tolerance * 1e6 if units == "ppm" else tolerance
    batch_kwargs = {
        "reference": reference,
        "tolerance": tolerance,
        "units": units,
    }

    speed_process(
        ms_raw_data,
        batch_size,
        BatchPreprocess.peak_align_batch,
        batch_kwargs=batch_kwargs,
    )

def _peak_align_flat_from_flat_batches(
    flat_batches,
    units: str,
    binfun: str,
):
    reference, tolerance = reference_computer(flat_batches, units=units, binfun=binfun)

    for mz_flat, intensity_flat, lengths in flat_batches:
        _ = FlatPreprocess.peak_align_flat(
            mz_data=mz_flat,
            intensity=intensity_flat,
            lengths=lengths,
            reference=reference,
            tolerance=tolerance,
            units=units,
        )

class TestAlign:
    """
    Peak align benchmark tests.
            use:
            uv run pytest ./tests/test_align_speed.py -k "test_align_speed or test_align_flat_speed" -q
    """

    @pytest.fixture(scope="module", params=[FILE_ULTRA])
    def ms_raw_data(self, request) -> MSDataManagerImzML:
        """Fixture providing batch-readable data manager cache for align benchmarks."""
        data_file_path = request.param
        dm = MSDataManagerImzML(filepath=data_file_path)
        dm.load_head_data()
        picked_dm = Preprocessor(dm).peak_pick().start()
        picked_dm.load_head_data()

        for _ in picked_dm.batch_generator(batch_size=512):
            pass
        return picked_dm

    @pytest.fixture(scope="module", params=[FILE_ULTRA])
    def flat_caches(self, request):
        """Fixture providing pre-generated flat arrays and reference axis for align benchmarks."""
        data_file_path = request.param
        dm = MSDataManagerImzML(filepath=data_file_path)
        dm.load_head_data()
        picked_dm = Preprocessor(dm).peak_pick().start()
        picked_dm.load_head_data()

        caches = []
        for mz_data, intensity_flat, lengths, _ in picked_dm.flat_generator(
            batch_size=256,
            include_mz=True,
            max_threads=16,
        ):
            caches.append((mz_data, intensity_flat, lengths))

        picked_dm.close()
        dm.close()
        return caches

    @pytest.mark.benchmark(timer=time.perf_counter)
    @pytest.mark.parametrize("units", ALIGN_UNITS)
    @pytest.mark.parametrize("binfun", BINFUN)
    def test_align_speed(self, benchmark, ms_raw_data, units, binfun):
        """Benchmark batch peak align via speed_process."""

        benchmark.pedantic(
            _run_peak_align_from_dm_process,
            args=(
                ms_raw_data,
                1024,
                units,
                binfun,
            ),
            rounds=ROUNDS,
            iterations=1,
            warmup_rounds=1,
        )

    @pytest.mark.benchmark(timer=time.perf_counter)
    @pytest.mark.parametrize("units", ALIGN_UNITS)
    @pytest.mark.parametrize("binfun", BINFUN)
    def test_align_flat_speed(self, benchmark, flat_caches, units, binfun):
        """Benchmark flat peak align via peak_align_flat."""

        flat_batches = flat_caches

        benchmark.pedantic(
            _peak_align_flat_from_flat_batches,
            args=(flat_batches, units, binfun),
            rounds=ROUNDS,
            iterations=1,
            warmup_rounds=1,
        )
