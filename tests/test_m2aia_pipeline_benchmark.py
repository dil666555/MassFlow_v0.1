"""End-to-end pipeline benchmarks: MassFlow Preprocessor vs pyM2aia reader pipeline.

Both sides run each library's own end-to-end pipeline over the whole imzML file:

- MassFlow: MSDataManagerImzML(path).load_head_data() → Preprocessor(dm, numba_max_threads=32)
  .normalization(...) / .noise_reduction(...).start() → close processed manager.
- pyM2aia: m2.ImzMLReader(path, normalization=..., smoothing=...) → consume every spectrum
  via SpectrumIterator (m2aia applies the pipeline lazily during iteration).

Both timings therefore include reader construction, header parsing, full read, full compute,
and result production in the natural form each library exposes.

Scope: **speed only**. Do not use this file to assert numerical equivalence between the two
libraries' outputs. In particular, Gaussian smoothing uses the same window point count on
both sides (MassFlow window=5 ↔ m2aia half_window_size=2, both yield a 5-point kernel), but
the underlying sigma differs (MassFlow defaults sd = window/4 = 1.25; m2aia's sigma is fixed
in its C++ backend and not exposed). TIC / RMS normalization semantics are algorithmically
equivalent between the two libraries.
"""

import os
import time
from pathlib import Path

import numpy as np
import pytest

from massflow.data_manager import MSDataManagerImzML
from massflow.preprocess.preprocessor import Preprocessor


ROUNDS = int(os.getenv("MASSFLOW_M2AIA_BENCHMARK_ROUNDS", "3"))
BATCH_SIZE = int(os.getenv("MASSFLOW_M2AIA_BENCHMARK_BATCH_SIZE", "256"))
NUMBA_THREADS = int(os.getenv("MASSFLOW_M2AIA_BENCHMARK_NUMBA_THREADS", "32"))
TEMP_DIR = os.getenv("MASSFLOW_M2AIA_BENCHMARK_TEMP_DIR", "./temp_pipeline_benchmark")

BENCHMARK_DATASETS = [
    ("example", Path("/root/autodl-tmp/data/example.imzML")),
    ("min", Path("/root/autodl-tmp/data/file_min_profile.imzML")),
    ("mid", Path("/root/autodl-tmp/data/file_mid_profile.imzML")),
    ("original", Path("/root/autodl-tmp/data/original.imzML")),
]

NORMALIZATION_CASES = [
    ("tic", "tic_numba", "TIC"),
    ("rms", "rms_numba", "RMS"),
]

SMOOTHING_CASES = [
    ("gaussian_window5", "gaussian_numba", 5, "Gaussian", 2),
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


# ---------------------------------------------------------------------------
# MassFlow pipeline runners
# ---------------------------------------------------------------------------

def _massflow_pipeline_normalization(path: Path, method: str, temp_subdir: str) -> None:
    dm = MSDataManagerImzML(filepath=str(path))
    dm.load_head_data()
    processed_manager = (
        Preprocessor(
            dm,
            batch_size=BATCH_SIZE,
            temp_dir=f"{TEMP_DIR}/{temp_subdir}",
            numba_max_threads=NUMBA_THREADS,
        )
        .normalization(method=method)
        .start()
    )
    processed_manager.close()


def _massflow_pipeline_smoothing(path: Path, method: str, window: int, temp_subdir: str) -> None:
    dm = MSDataManagerImzML(filepath=str(path))
    dm.load_head_data()
    processed_manager = (
        Preprocessor(
            dm,
            batch_size=BATCH_SIZE,
            temp_dir=f"{TEMP_DIR}/{temp_subdir}",
            numba_max_threads=NUMBA_THREADS,
        )
        .noise_reduction(method=method, window=window)
        .start()
    )
    processed_manager.close()


# ---------------------------------------------------------------------------
# pyM2aia pipeline runners
# ---------------------------------------------------------------------------

def _m2aia_pipeline_normalization(m2, path: Path, method: str) -> tuple[int, int, float]:
    reader = m2.ImzMLReader(str(path), normalization=method)

    spectrum_count = 0
    point_count = 0
    intensity_sum = 0.0
    for _, _, ys in reader.SpectrumIterator():
        y = np.asarray(ys, dtype=np.float64)
        spectrum_count += 1
        point_count += int(y.size)
        intensity_sum += float(y.sum())

    return spectrum_count, point_count, intensity_sum


def _m2aia_pipeline_smoothing(
    m2, path: Path, method: str, half_window_size: int
) -> tuple[int, int, float]:
    reader = m2.ImzMLReader(
        str(path),
        smoothing=method,
        smoothing_half_window_size=half_window_size,
    )

    spectrum_count = 0
    point_count = 0
    intensity_sum = 0.0
    for _, _, ys in reader.SpectrumIterator():
        y = np.asarray(ys, dtype=np.float64)
        spectrum_count += 1
        point_count += int(y.size)
        intensity_sum += float(y.sum())

    return spectrum_count, point_count, intensity_sum


# ---------------------------------------------------------------------------
# Benchmarks
# ---------------------------------------------------------------------------

class TestPipelineNormalizationBenchmark:
    @pytest.mark.benchmark(timer=time.perf_counter)
    @pytest.mark.parametrize(
        ("_case_name", "massflow_method"),
        [(case[0], case[1]) for case in NORMALIZATION_CASES],
        ids=[case[0] for case in NORMALIZATION_CASES],
    )
    def test_massflow_pipeline_normalization(
        self, benchmark, imzml_path, _case_name, massflow_method
    ):
        temp_subdir = f"norm_{imzml_path.stem}_{_case_name}"
        benchmark.pedantic(
            _massflow_pipeline_normalization,
            args=(imzml_path, massflow_method, temp_subdir),
            rounds=ROUNDS,
            iterations=1,
            warmup_rounds=1,
        )

    @pytest.mark.benchmark(timer=time.perf_counter)
    @pytest.mark.parametrize(
        ("_case_name", "m2aia_method"),
        [(case[0], case[2]) for case in NORMALIZATION_CASES],
        ids=[case[0] for case in NORMALIZATION_CASES],
    )
    def test_m2aia_pipeline_normalization(
        self, benchmark, imzml_path, _case_name, m2aia_method
    ):
        m2 = _import_m2aia()
        result = benchmark.pedantic(
            _m2aia_pipeline_normalization,
            args=(m2, imzml_path, m2aia_method),
            rounds=ROUNDS,
            iterations=1,
            warmup_rounds=1,
        )
        assert result[0] > 0
        assert result[1] > 0


class TestPipelineSmoothingBenchmark:
    @pytest.mark.benchmark(timer=time.perf_counter)
    @pytest.mark.parametrize(
        ("_case_name", "massflow_method", "window"),
        [(case[0], case[1], case[2]) for case in SMOOTHING_CASES],
        ids=[case[0] for case in SMOOTHING_CASES],
    )
    def test_massflow_pipeline_smoothing(
        self, benchmark, imzml_path, _case_name, massflow_method, window
    ):
        temp_subdir = f"smooth_{imzml_path.stem}_{_case_name}"
        benchmark.pedantic(
            _massflow_pipeline_smoothing,
            args=(imzml_path, massflow_method, window, temp_subdir),
            rounds=ROUNDS,
            iterations=1,
            warmup_rounds=1,
        )

    @pytest.mark.benchmark(timer=time.perf_counter)
    @pytest.mark.parametrize(
        ("_case_name", "m2aia_method", "half_window_size"),
        [(case[0], case[3], case[4]) for case in SMOOTHING_CASES],
        ids=[case[0] for case in SMOOTHING_CASES],
    )
    def test_m2aia_pipeline_smoothing(
        self, benchmark, imzml_path, _case_name, m2aia_method, half_window_size
    ):
        m2 = _import_m2aia()
        result = benchmark.pedantic(
            _m2aia_pipeline_smoothing,
            args=(m2, imzml_path, m2aia_method, half_window_size),
            rounds=ROUNDS,
            iterations=1,
            warmup_rounds=1,
        )
        assert result[0] > 0
        assert result[1] > 0
