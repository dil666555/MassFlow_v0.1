import time
import numpy as np
import pytest

from massflow.data_manager import MSDataManagerImzML
from massflow.preprocess import BatchPreprocess
from massflow.preprocess.preprocessor import Preprocessor
from massflow.tools.dm_process import dm_process
from massflow.tools.logger import get_logger

logger = get_logger("test_align")

ROUNDS = 5
ALIGN_UNITS = ["mz"]
FILE_MIN = '/Users/dre/Desktop/data/200TopL, 170TopR, 190BottomL, 180BottomR-profile/200TopL, 170TopR, 190BottomL, 180BottomR-profile.imzML'
FILE_MAX = '/Users/dre/Desktop/data/80TopL, 50TopR, 70BottomL, 60BottomR-profile/80TopL, 50TopR, 70BottomL, 60BottomR-profile.imzML'
TEMP_DIR = "./temp"


def _resolve_alignment_reference(ms_raw_data: MSDataManagerImzML) -> np.ndarray:
    shared_mz = ms_raw_data.ms.shared_mz_list
    if shared_mz is not None and len(shared_mz) > 0:
        return np.asarray(shared_mz, dtype=np.float64)

    for mz_data, _, _, _ in ms_raw_data.flat_generator(
        batch_size=1,
        include_mz=True,
        max_threads=16,
    ):
        if mz_data is not None and mz_data.size > 0:
            return np.asarray(mz_data, dtype=np.float64)

    raise ValueError("Unable to infer reference m/z axis for alignment")


def _run_peak_align_from_pipeline(
    ms_raw_data: MSDataManagerImzML,
    reference: np.ndarray,
    tolerance: float,
    units: str,
):
    processed_manager = (
        Preprocessor(ms_raw_data, batch_size=256, temp_dir=TEMP_DIR)
        .peak_align(reference=reference, tolerance=tolerance, units=units)
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

    @pytest.mark.benchmark(timer=time.perf_counter)
    @pytest.mark.parametrize("units", ALIGN_UNITS)
    def test_align_memory(self, benchmark, units, ms_raw_data):
        """Benchmark batch peak align via dm_process."""
        logger.info(f"Benchmarking batch peak align units={units}")

        reference = _resolve_alignment_reference(ms_raw_data)
        batch_kwargs = {
            "reference": reference,
            "tolerance": 0.1,
            "units": units,
        }

        benchmark.pedantic(
            dm_process,
            args=(
                ms_raw_data,
                256,
                BatchPreprocess.peak_align_batch,
                batch_kwargs,
                TEMP_DIR,
            ),
            rounds=ROUNDS,
            iterations=1,
            warmup_rounds=1,
        )

    @pytest.mark.benchmark(timer=time.perf_counter)
    @pytest.mark.parametrize("units", ALIGN_UNITS)
    def test_align_flat_memory(self, benchmark, units, ms_raw_data):
        """Benchmark flat peak align via peak_align pipeline."""
        logger.info(f"Benchmarking flat peak align units={units}")

        reference = _resolve_alignment_reference(ms_raw_data)

        benchmark.pedantic(
            _run_peak_align_from_pipeline,
            args=(ms_raw_data, reference, 0.1, units),
            rounds=ROUNDS,
            iterations=1,
            warmup_rounds=1,
        )
