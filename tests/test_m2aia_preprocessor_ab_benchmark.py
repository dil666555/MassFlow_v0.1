"""AB-only read-plus-process benchmarks for MassFlow vs pyM2aia.

This file compares the fastest MassFlow read/process boundary against m2aia:

- MassFlow: ``MSDataManagerImzML(path).load_head_data()`` ->
  ``PreprocessorAB(...).normalization/noise_reduction(...).start()``. The AB
  executor reads flat batches, processes them, consumes the processed result,
  and does not write processed data.
- pyM2aia: ``m2.ImzMLReader(path, normalization=.../smoothing=...)`` ->
  consume all spectra from ``SpectrumIterator``.

Scope: speed only. The Gaussian smoothing comparison keeps the same point
window size (MassFlow window=5, m2aia half_window_size=2).
"""

import os
import time
from pathlib import Path

import numpy as np
import pytest

from massflow.data_manager import MSDataManagerImzML
from massflow.preprocess.preprocessor_ab import PreprocessABResult, PreprocessorAB


ROUNDS = int(os.getenv("MASSFLOW_M2AIA_BENCHMARK_ROUNDS", "3"))
BATCH_SIZE = int(os.getenv("MASSFLOW_M2AIA_BENCHMARK_BATCH_SIZE", "256"))
READ_THREADS = int(os.getenv("MASSFLOW_M2AIA_BENCHMARK_READ_THREADS", "12"))
NUMBA_THREADS = int(os.getenv("MASSFLOW_M2AIA_BENCHMARK_NUMBA_THREADS", "32"))
QUEUE_AB_SIZE = int(os.getenv("MASSFLOW_M2AIA_AB_QUEUE_SIZE", "4"))

BENCHMARK_DATASETS = [
    # ("example", Path("/root/autodl-tmp/data/example.imzML")),
    # ("min", Path("/root/autodl-tmp/data/file_min_profile.imzML")),
    ("mid", Path("/root/autodl-tmp/data/file_mid_profile.imzML")),
    # ("original", Path("/root/autodl-tmp/data/original.imzML")),
]

NORMALIZATION_CASES = [
    ("tic", "tic_numba", "TIC"),
    ("rms", "rms_numba", "RMS"),
]

SMOOTHING_CASES = [
    ("gaussian_window5", "gaussian_numba", "Gaussian", 5, 2),
    ("savgol_window5", "savgol_numba", "SavitzkyGolay", 5, 2),
]


@pytest.fixture(scope="module", params=BENCHMARK_DATASETS, ids=[item[0] for item in BENCHMARK_DATASETS])
def imzml_path(request) -> Path:
    dataset_name, path = request.param
    path = path.expanduser()
    if not path.exists():
        pytest.skip(f"{dataset_name} imzML file not found: {path}")
    return path


def _import_m2aia():
    try:
        import m2aia as m2
    except (ImportError, OSError) as exc:
        pytest.skip(f"m2aia is not available in this environment: {exc}")
    return m2


def _consume_m2aia_spectra(reader) -> tuple[int, int, float]:
    spectrum_count = 0
    point_count = 0
    intensity_sum = 0.0
    for _, _, ys in reader.SpectrumIterator():
        y = np.asarray(ys, dtype=np.float64)
        spectrum_count += 1
        point_count += int(y.size)
        intensity_sum += float(np.sum(y, dtype=np.float64))
    return spectrum_count, point_count, intensity_sum


def _as_tuple(result: PreprocessABResult) -> tuple[int, int, float]:
    return result.spectrum_count, result.point_count, result.intensity_sum


def _massflow_ab_normalization(dm: MSDataManagerImzML, method: str) -> tuple[int, int, float]:
    result = (
        PreprocessorAB(
            dm,
            batch_size=BATCH_SIZE,
            queue_ab_size=QUEUE_AB_SIZE,
            numba_max_threads=NUMBA_THREADS,
        )
        .normalization(method=method)
        .start()
    )
    return _as_tuple(result)


def _m2aia_normalization(m2, path: Path, method: str) -> tuple[int, int, float]:
    reader = m2.ImzMLReader(str(path), normalization=method)
    return _consume_m2aia_spectra(reader)


def _massflow_ab_smoothing(dm: MSDataManagerImzML, method: str, window: int) -> tuple[int, int, float]:
    result = (
        PreprocessorAB(
            dm,
            batch_size=BATCH_SIZE,
            queue_ab_size=QUEUE_AB_SIZE,
            numba_max_threads=NUMBA_THREADS,
        )
        .noise_reduction(method=method, window=window)
        .start()
    )
    return _as_tuple(result)


def _m2aia_smoothing(m2, path: Path, method: str, half_window_size: int) -> tuple[int, int, float]:
    reader = m2.ImzMLReader(
        str(path),
        smoothing=method,
        smoothing_half_window_size=half_window_size,
    )
    return _consume_m2aia_spectra(reader)


class TestABNormalizationBenchmark:
    @pytest.fixture(scope="class")
    def data_manager(self, imzml_path) -> MSDataManagerImzML:
        dm = MSDataManagerImzML(filepath=str(imzml_path), max_threads=READ_THREADS)
        try:
            dm.load_head_data()
            yield dm
        finally:
            dm.close()

    @pytest.mark.benchmark(timer=time.perf_counter)
    @pytest.mark.parametrize(
        ("_case_name", "massflow_method"),
        [(case[0], case[1]) for case in NORMALIZATION_CASES],
        ids=[case[0] for case in NORMALIZATION_CASES],
    )
    def test_massflow_ab_normalization(self, benchmark, data_manager, _case_name, massflow_method):
        result = benchmark.pedantic(
            _massflow_ab_normalization,
            args=(data_manager, massflow_method),
            rounds=ROUNDS,
            iterations=1,
            warmup_rounds=1,
        )
        assert result[0] > 0
        assert result[1] > 0

    @pytest.mark.benchmark(timer=time.perf_counter)
    @pytest.mark.parametrize(
        ("_case_name", "m2aia_method"),
        [(case[0], case[2]) for case in NORMALIZATION_CASES],
        ids=[case[0] for case in NORMALIZATION_CASES],
    )
    def test_m2aia_ab_normalization(self, benchmark, imzml_path, _case_name, m2aia_method):
        m2 = _import_m2aia()
        result = benchmark.pedantic(
            _m2aia_normalization,
            args=(m2, imzml_path, m2aia_method),
            rounds=ROUNDS,
            iterations=1,
            warmup_rounds=1,
        )
        assert result[0] > 0
        assert result[1] > 0


class TestABSmoothingBenchmark:

    @pytest.fixture(scope="class")
    def data_manager(self, imzml_path) -> MSDataManagerImzML:
        dm = MSDataManagerImzML(filepath=str(imzml_path), max_threads=READ_THREADS)
        try:
            dm.load_head_data()
            yield dm
        finally:
            dm.close()

    @pytest.mark.benchmark(timer=time.perf_counter)
    @pytest.mark.parametrize(
        ("_case_name", "massflow_method", "window"),
        [(case[0], case[1], case[3]) for case in SMOOTHING_CASES],
        ids=[case[0] for case in SMOOTHING_CASES],
    )
    def test_massflow_ab_smoothing(self, benchmark, data_manager, _case_name, massflow_method, window):
        result = benchmark.pedantic(
            _massflow_ab_smoothing,
            args=(data_manager, massflow_method, window),
            rounds=ROUNDS,
            iterations=1,
            warmup_rounds=1,
        )
        assert result[0] > 0
        assert result[1] > 0

    @pytest.mark.benchmark(timer=time.perf_counter)
    @pytest.mark.parametrize(
        ("_case_name", "m2aia_method", "half_window_size"),
        [(case[0], case[2], case[4]) for case in SMOOTHING_CASES],
        ids=[case[0] for case in SMOOTHING_CASES],
    )
    def test_m2aia_ab_smoothing(self, benchmark, imzml_path, _case_name, m2aia_method, half_window_size):
        m2 = _import_m2aia()
        result = benchmark.pedantic(
            _m2aia_smoothing,
            args=(m2, imzml_path, m2aia_method, half_window_size),
            rounds=ROUNDS,
            iterations=1,
            warmup_rounds=1,
        )
        assert result[0] > 0
        assert result[1] > 0
