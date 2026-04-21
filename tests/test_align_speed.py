import time
import pytest

from massflow.data_manager import MSDataManagerImzML
from massflow.preprocess.helper.peak_align_helper import reference_computer
from massflow.preprocess.helper.peak_align_helper_v1 import compute_reference
from massflow.preprocess import BatchPreprocess
from massflow.preprocess.flat_pre_fun import FlatPreprocess
from massflow.tools.dm_process import speed_process
from massflow.tools.logger import get_logger

logger = get_logger("test_align")

ROUNDS = 5
ALIGN_UNITS = ["ppm"]
FILE_MIN = '/Users/dre/Desktop/data/200TopL, 170TopR, 190BottomL, 180BottomR-profile/200TopL, 170TopR, 190BottomL, 180BottomR-profile.imzML'
FILE_MAX = '/Users/dre/Desktop/data/80TopL, 50TopR, 70BottomL, 60BottomR-profile/80TopL, 50TopR, 70BottomL, 60BottomR-profile.imzML'


def _run_peak_align_from_dm_process(
    ms_raw_data: MSDataManagerImzML,
    batch_size: int,
    units: str,
):
    reference, tolerance = compute_reference(ms_raw_data, units=units)
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
    ms_raw_data: MSDataManagerImzML,
    flat_batches,
    units: str,
):
    reference, tolerance = reference_computer(ms_raw_data, units=units)

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

    @pytest.fixture(scope="module", params=[FILE_MIN, FILE_MAX])
    def ms_raw_data(self, request) -> MSDataManagerImzML:
        """Fixture providing batch-readable data manager cache for align benchmarks."""
        data_file_path = request.param
        dm = MSDataManagerImzML(filepath=data_file_path)
        dm.load_head_data()
        for _ in dm.batch_generator(batch_size=512):
            pass
        return dm

    @pytest.fixture(scope="module")
    def flat_caches(self, ms_raw_data: MSDataManagerImzML):
        """Fixture providing pre-generated flat arrays and reference axis for align benchmarks."""
        caches = []
        for mz_data, intensity_flat, lengths, _ in ms_raw_data.flat_generator(
            batch_size=4096,
            include_mz=True,
            max_threads=16,
        ):
            caches.append((mz_data, intensity_flat, lengths))

        return caches

    @pytest.mark.benchmark(timer=time.perf_counter)
    @pytest.mark.parametrize("units", ALIGN_UNITS)
    def test_align_speed(self, benchmark, ms_raw_data, units):
        """Benchmark batch peak align via speed_process."""

        benchmark.pedantic(
            _run_peak_align_from_dm_process,
            args=(
                ms_raw_data,
                1024,
                units,
            ),
            rounds=ROUNDS,
            iterations=1,
            warmup_rounds=1,
        )

    @pytest.mark.benchmark(timer=time.perf_counter)
    @pytest.mark.parametrize("units", ALIGN_UNITS)
    def test_align_flat_speed(self, benchmark, ms_raw_data, flat_caches, units):
        """Benchmark flat peak align via peak_align_flat."""

        flat_batches = flat_caches

        benchmark.pedantic(
            _peak_align_flat_from_flat_batches,
            args=(ms_raw_data, flat_batches, units),
            rounds=ROUNDS,
            iterations=1,
            warmup_rounds=1,
        )
