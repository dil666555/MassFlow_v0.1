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

NORMALIZATION_CASES = [
    ("tic", "tic_numba", "TIC"),
    ("rms", "rms_numba", "RMS"),
]


@pytest.fixture(scope="module")
def imzml_path() -> Path:
    path = Path(os.getenv("MASSFLOW_M2AIA_BENCHMARK_IMZML", DEFAULT_IMZML_FILE)).expanduser()
    if not path.exists():
        pytest.skip(
            "Benchmark imzML file not found. Set MASSFLOW_M2AIA_BENCHMARK_IMZML "
            "to the input .imzML file path."
        )
    return path


def _load_m2aia_reader(path: Path, *, normalization: str):
    m2 = pytest.importorskip("m2aia")
    reader = m2.ImzMLReader(str(path))

    if not hasattr(reader, "SetNormalization"):
        pytest.skip("Installed m2aia does not expose ImzMLReader.SetNormalization")

    reader.SetNormalization(normalization)
    reader.Execute()
    return reader


def _massflow_normalization(path: Path, method: str) -> tuple[int, float]:
    """Run MassFlow flat normalization and consume all processed intensities."""
    dm = MSDataManagerImzML(filepath=str(path), max_threads=MAX_THREADS)
    try:
        dm.load_head_data()

        intensity_sum = 0.0
        spectrum_count = 0

        for mz_data, intensity_flat, lengths, _ in dm.flat_generator(
            batch_size=BATCH_SIZE,
            include_mz=False,
            max_threads=MAX_THREADS,
        ):
            result = FlatPreprocess.normalization_flat(
                mz_data=mz_data,
                intensity=intensity_flat,
                lengths=lengths,
                method=method,
            )
            spectrum_count += int(lengths.size)
            intensity_sum += float(np.sum(result.intensity, dtype=np.float64))

        return spectrum_count, intensity_sum
    finally:
        dm.close()


def _m2aia_normalization(path: Path, method: str) -> tuple[int, float]:
    """Run m2aia normalization and consume all processed intensities."""
    reader = _load_m2aia_reader(path, normalization=method)

    spectrum_count = 0
    intensity_sum = 0.0

    for _, _, ys in reader.SpectrumIterator():
        spectrum_count += 1
        intensity_sum += float(np.sum(ys, dtype=np.float64))

    return spectrum_count, intensity_sum


class TestNormalizationBenchmark:
    @pytest.mark.benchmark(timer=time.perf_counter)
    @pytest.mark.parametrize(
        ("case_name", "massflow_method", "m2aia_method"),
        NORMALIZATION_CASES,
        ids=[case[0] for case in NORMALIZATION_CASES],
    )
    def test_massflow_normalization(self, benchmark, imzml_path, case_name, massflow_method, m2aia_method):
        result = benchmark.pedantic(
            _massflow_normalization,
            args=(imzml_path, massflow_method),
            rounds=ROUNDS,
            iterations=1,
            warmup_rounds=1,
        )
        assert result[0] > 0

    @pytest.mark.benchmark(timer=time.perf_counter)
    @pytest.mark.parametrize(
        ("case_name", "massflow_method", "m2aia_method"),
        NORMALIZATION_CASES,
        ids=[case[0] for case in NORMALIZATION_CASES],
    )
    def test_m2aia_normalization(self, benchmark, imzml_path, case_name, massflow_method, m2aia_method):
        result = benchmark.pedantic(
            _m2aia_normalization,
            args=(imzml_path, m2aia_method),
            rounds=ROUNDS,
            iterations=1,
            warmup_rounds=1,
        )
        assert result[0] > 0
