import time
import pytest

from massflow.data_manager import MSDataManagerImzML
from massflow.preprocess import BatchPreprocess
from massflow.preprocess.helper.peak_align_helper import reference_computer
from massflow.preprocess.helper.peak_align_helper_v1 import compute_reference
from massflow.preprocess.preprocessor import Preprocessor
from massflow.tools.dm_process import dm_process
from massflow.tools.logger import get_logger

logger = get_logger("test_align")

ROUNDS = 5
ALIGN_UNITS = ["ppm"]
FILE_MIN = '/Users/dre/Desktop/data/test_data_centroid/file_min_centroid/file_min_centroid.imzML'
FILE_MAX = '/Users/dre/Desktop/data/test_data_centroid/file_max_centroid/file_max_centroid.imzML'
TEMP_DIR = "./temp"

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

    processed_manager = dm_process(
        ms_raw_data,
        batch_size,
        BatchPreprocess.peak_align_batch,
        batch_kwargs=batch_kwargs,
        temp_dir=TEMP_DIR,
    )
    processed_manager.close()

def _run_peak_align_from_pipeline(
    ms_raw_data: MSDataManagerImzML,
    flat_batches,
    units: str,
):
    reference, tolerance = reference_computer(flat_batches, units=units)
    pipeline_tolerance = tolerance * 1e6 if units == "ppm" else tolerance

    processed_manager = (
        Preprocessor(ms_raw_data, batch_size=256, temp_dir=TEMP_DIR)
        .peak_align(reference=reference, tolerance=pipeline_tolerance, units=units)
        .start()
    )

    processed_manager.close()


class TestAlign:
    """
    Peak align benchmark tests.
            use:
            uv run pytest ./tests/test_align_memory.py -k "test_align_memory or test_align_flat_memory" -q
    """

    @pytest.fixture(scope="module", params=[FILE_MIN, FILE_MAX])
    def ms_raw_data(self, request) -> MSDataManagerImzML:
        """Fixture providing batch-readable data manager cache for align benchmarks."""
        data_file_path = request.param
        dm = MSDataManagerImzML(filepath=data_file_path)
        dm.load_head_data()
        return dm

    @pytest.fixture(scope="module")
    def flat_caches(self, ms_raw_data: MSDataManagerImzML):
        """Fixture providing pre-generated flat arrays for align memory benchmarks."""
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
    def test_align_memory(self, benchmark, ms_raw_data, units):
        """Benchmark batch peak align via dm_process."""

        benchmark.pedantic(
            _run_peak_align_from_dm_process,
            args=(
                ms_raw_data,
                256,
                units,
            ),
            rounds=ROUNDS,
            iterations=1,
            warmup_rounds=1,
        )

    @pytest.mark.benchmark(timer=time.perf_counter)
    @pytest.mark.parametrize("units", ALIGN_UNITS)
    def test_align_flat_memory(self, benchmark, ms_raw_data, flat_caches, units):
        """Benchmark flat peak align via peak_align pipeline."""

        benchmark.pedantic(
            _run_peak_align_from_pipeline,
            args=(ms_raw_data, flat_caches, units),
            rounds=ROUNDS,
            iterations=1,
            warmup_rounds=1,
        )
