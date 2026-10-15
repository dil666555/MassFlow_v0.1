import os
import time
import pytest

from massflow.data_manager import MSDataManagerImzML
from massflow.preprocess import BatchPreprocess
from massflow.preprocess.numba.numba_runtime import apply_numba_runtime
from massflow.preprocess.helper.peak_align_helper import reference_computer
from massflow.preprocess.helper.peak_align_helper_v1 import compute_reference
from massflow.preprocess.preprocessor import Preprocessor
from massflow.tools.dm_process import dm_process
from massflow.tools.logger import get_logger

logger = get_logger("test_align")

ROUNDS = 2
ALIGN_UNITS = ["ppm"]
BINFUN = ["min"]
THREADS = [1, 2, 4, 8, 16, 32]
# FILE_MIN = "/home/Share_Space/data_local/min/file_min_profile.imzML"
# FILE_MID = "/home/Share_Space/data_local/mid/file_mid_profile.imzML"
FILE_MAX = os.getenv("MASSFLOW_S11_MAX_FILE", "/Users/dre/Desktop/data/example/example.imzML")
FILE_ULTRA = os.getenv("MASSFLOW_S11_ULTRA_FILE", "/Users/dre/Desktop/data/original/original.imzML")

def _run_peak_align_from_dm_process(
    ms_raw_data: MSDataManagerImzML,
    batch_size: int,
    units: str,
    binfun: str,
):
    reference, tolerance = compute_reference(ms_raw_data, units=units, binfun=binfun, clear_memory=True)
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
        temp_dir="./temp",
    )
    processed_manager.close()

def _run_peak_align_from_pipeline(
    ms_raw_data: MSDataManagerImzML,
    flat_batches,
    units: str,
    binfun: str,
    threads: int,
):
    from massflow.preprocess.numba.numba_runtime import apply_numba_runtime

    apply_numba_runtime(override_workers=threads)
    reference, tolerance = reference_computer(flat_batches, units=units, binfun=binfun)
    pipeline_tolerance = tolerance * 1e6 if units == "ppm" else tolerance

    processed_manager = (
        Preprocessor(ms_raw_data, batch_size=128, temp_dir="./temp", numba_max_threads=threads)
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

    @pytest.fixture(scope="module", params=[FILE_MAX, FILE_ULTRA], ids=["max", "ultra"])
    def ms_raw_data(self, request):
        """Fixture providing batch-readable data manager cache for align benchmarks."""
        data_file_path = request.param
        with MSDataManagerImzML(filepath=data_file_path, max_threads=8) as dm:
            dm.load_head_data()
            picked_dm = Preprocessor(dm).peak_pick().start()
        with picked_dm:
            yield picked_dm

    @pytest.fixture(scope="module")
    def flat_caches(self, ms_raw_data):
        """Fixture providing pre-generated flat arrays for align memory benchmarks."""
        caches = []
        for mz_data, intensity_flat, lengths, _ in ms_raw_data.flat_generator(
            batch_size=256,
            include_mz=True,
            max_threads=16,
        ):
            caches.append((mz_data, intensity_flat, lengths))

        return caches

    @pytest.mark.benchmark(timer=time.perf_counter)
    @pytest.mark.parametrize("units", ALIGN_UNITS)
    @pytest.mark.parametrize("binfun", BINFUN)
    def test_align_memory(self, benchmark, ms_raw_data, units, binfun):
        """Benchmark batch peak align via dm_process."""
        benchmark.extra_info.update(
            batch_size=256, read_threads=ms_raw_data.max_threads,
            numba_threads=apply_numba_runtime(),
        )

        benchmark.pedantic(
            _run_peak_align_from_dm_process,
            args=(
                ms_raw_data,
                256,
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
    @pytest.mark.parametrize("threads", THREADS)
    def test_align_flat_memory(self, benchmark, ms_raw_data, flat_caches, units, binfun, threads):
        """Benchmark flat peak align via peak_align pipeline."""

        benchmark.pedantic(
            _run_peak_align_from_pipeline,
            args=(ms_raw_data, flat_caches, units, binfun, threads),
            rounds=ROUNDS,
            iterations=1,
            warmup_rounds=1,
        )
