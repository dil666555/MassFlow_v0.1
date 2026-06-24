import os
import time
from pathlib import Path

import numpy as np
import pytest

from massflow.data_manager import MSDataManagerImzML
from massflow.preprocess.flat_pre_fun import FlatPreprocess


ROUNDS = int(os.getenv("MASSFLOW_M2AIA_BENCHMARK_ROUNDS", "5"))
BATCH_SIZE = int(os.getenv("MASSFLOW_M2AIA_BENCHMARK_BATCH_SIZE", "256"))
MAX_THREADS = int(os.getenv("MASSFLOW_M2AIA_BENCHMARK_MAX_THREADS", "16"))
DEFAULT_IMZML_FILE = "/Users/dre/Desktop/data/original/original.imzML"


@pytest.fixture(scope="module")
def imzml_path():
    path = Path(os.getenv("MASSFLOW_M2AIA_BENCHMARK_IMZML", DEFAULT_IMZML_FILE)).expanduser()
    if not path.exists():
        pytest.skip("imzML file not found")
    return path


def _massflow_smoothing(path: Path) -> tuple[int, float]:
    dm = MSDataManagerImzML(filepath=str(path), max_threads=MAX_THREADS)
    try:
        dm.load_head_data()

        spectrum_count = 0
        intensity_sum = 0.0

        for mz_data, intensity_flat, lengths, _ in dm.flat_generator(
            batch_size=BATCH_SIZE,
            include_mz=False,
            max_threads=MAX_THREADS,
        ):
            result = FlatPreprocess.noise_reduction_flat(
                mz_data=mz_data,
                intensity=intensity_flat,
                lengths=lengths,
                method="gaussian_numba",
                window=5,
            )
            spectrum_count += int(lengths.size)
            intensity_sum += float(result.intensity.sum())

        return spectrum_count, intensity_sum
    finally:
        dm.close()


def _m2aia_smoothing(path: Path) -> tuple[int, float]:
    m2 = pytest.importorskip("m2aia")

    reader = m2.ImzMLReader(str(path), smoothing="Gaussian", smoothing_half_window_size=2)

    spectrum_count = 0
    intensity_sum = 0.0

    if hasattr(reader, "Execute"):
        try:
            reader.Execute()
        except Exception:
            pass

    for _, _, ys in reader.SpectrumIterator():
        y = np.asarray(ys, dtype=np.float64)
        spectrum_count += 1
        intensity_sum += float(y.sum())

    return spectrum_count, intensity_sum


class TestSmoothingBenchmark:
    @pytest.mark.benchmark(timer=time.perf_counter)
    def test_massflow_smoothing(self, benchmark, imzml_path):
        result = benchmark.pedantic(
            _massflow_smoothing,
            args=(imzml_path,),
            rounds=ROUNDS,
            iterations=1,
            warmup_rounds=1,
        )
        assert result[0] > 0

    @pytest.mark.benchmark(timer=time.perf_counter)
    def test_m2aia_smoothing(self, benchmark, imzml_path):
        result = benchmark.pedantic(
            _m2aia_smoothing,
            args=(imzml_path,),
            rounds=ROUNDS,
            iterations=1,
            warmup_rounds=1,
        )
        assert result[0] > 0
