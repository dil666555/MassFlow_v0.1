import os
import time
from pathlib import Path

import numpy as np
import pytest

from massflow.data_manager import MSDataManagerImzML


ROUNDS = int(os.getenv("MASSFLOW_M2AIA_BENCHMARK_ROUNDS", "5"))
BATCH_SIZE = int(os.getenv("MASSFLOW_M2AIA_BENCHMARK_BATCH_SIZE", "256"))
MAX_THREADS = int(os.getenv("MASSFLOW_M2AIA_BENCHMARK_MAX_THREADS", "16"))
DEFAULT_IMZML_FILE = "/Users/dre/Desktop/data/original/original.imzML"


def _benchmark_file_path() -> Path:
    path = Path(os.getenv("MASSFLOW_M2AIA_BENCHMARK_IMZML", DEFAULT_IMZML_FILE)).expanduser()
    if not path.exists():
        pytest.skip(
            "Benchmark imzML file not found. Set MASSFLOW_M2AIA_BENCHMARK_IMZML "
            "to the input .imzML file path."
        )
    return path


@pytest.fixture(scope="module")
def imzml_path() -> Path:
    return _benchmark_file_path()


def _read_all_spectra_massflow_flat(path: Path) -> tuple[int, int, float]:
    dm = MSDataManagerImzML(filepath=str(path), max_threads=MAX_THREADS)
    try:
        dm.load_head_data()

        spectrum_count = 0
        point_count = 0
        intensity_sum = 0.0

        for _, intensity_flat, lengths, _ in dm.flat_generator(
            batch_size=BATCH_SIZE,
            include_mz=True,
            max_threads=MAX_THREADS,
        ):
            spectrum_count += int(lengths.size)
            point_count += int(lengths.sum())
            intensity_sum += float(np.asarray(intensity_flat, dtype=np.float64).sum())

        return spectrum_count, point_count, intensity_sum
    finally:
        dm.close()


def _read_all_spectra_m2aia(path: Path) -> tuple[int, int, float]:
    m2 = pytest.importorskip("m2aia")
    reader = m2.ImzMLReader(str(path))

    spectrum_count = 0
    point_count = 0
    intensity_sum = 0.0

    for _, _, ys in reader.SpectrumIterator():
        y_values = np.asarray(ys, dtype=np.float64)
        spectrum_count += 1
        point_count += int(y_values.size)
        intensity_sum += float(y_values.sum())

    return spectrum_count, point_count, intensity_sum


class TestReadAllSpectraBenchmark:
    @pytest.mark.benchmark(timer=time.perf_counter)
    def test_massflow_flat_read_all_spectra(self, benchmark, imzml_path):
        result = benchmark.pedantic(
            _read_all_spectra_massflow_flat,
            args=(imzml_path,),
            rounds=ROUNDS,
            iterations=1,
            warmup_rounds=1,
        )
        assert result[0] > 0
        assert result[1] > 0

    @pytest.mark.benchmark(timer=time.perf_counter)
    def test_m2aia_read_all_spectra(self, benchmark, imzml_path):
        result = benchmark.pedantic(
            _read_all_spectra_m2aia,
            args=(imzml_path,),
            rounds=ROUNDS,
            iterations=1,
            warmup_rounds=1,
        )
        assert result[0] > 0
        assert result[1] > 0
