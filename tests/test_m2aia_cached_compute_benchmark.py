"""Cached-input compute benchmarks for MassFlow vs pyM2aia.

MassFlow exposes ndarray-level flat kernels, so its benchmark below preloads
flat batches once and times only FlatPreprocess calls plus result consumption.

pyM2aia does not expose ndarray-level normalization/smoothing kernels. Its
closest public boundary is an already constructed ImzMLReader followed by
SetNormalization/SetSmoothing, lib.Update, and spectrum consumption. Treat the
m2aia numbers as cached-reader preprocessing time, not as a strict kernel-only
measurement.
"""

import os
import time
from pathlib import Path

import numpy as np
import pytest

from massflow.data_manager import MSDataManagerImzML
from massflow.preprocess.flat_pre_fun import FlatPreprocess
from massflow.preprocess.numba.numba_runtime import apply_numba_runtime


ROUNDS = int(os.getenv("MASSFLOW_M2AIA_BENCHMARK_ROUNDS", "3"))
BATCH_SIZE = int(os.getenv("MASSFLOW_M2AIA_BENCHMARK_BATCH_SIZE", "256"))
READ_THREADS = int(os.getenv("MASSFLOW_M2AIA_BENCHMARK_READ_THREADS", "8"))
NUMBA_THREADS = int(os.getenv("MASSFLOW_M2AIA_BENCHMARK_NUMBA_THREADS", "32"))
MAX_SPECTRA = int(os.getenv("MASSFLOW_M2AIA_CACHED_MAX_SPECTRA", "2048"))

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
    ("gaussian_window5", "gaussian_numba", "Gaussian", 5, 2),
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


def _truncate_flat_batch(
    intensity_flat: np.ndarray,
    lengths: np.ndarray,
    max_spectra: int,
) -> tuple[np.ndarray, np.ndarray]:
    if max_spectra <= 0 or lengths.size <= max_spectra:
        return intensity_flat, lengths

    kept_lengths = np.asarray(lengths[:max_spectra], dtype=np.int32)
    kept_points = int(np.sum(kept_lengths, dtype=np.int64))
    return intensity_flat[:kept_points], kept_lengths


@pytest.fixture(scope="module")
def massflow_flat_caches(imzml_path):
    dm = MSDataManagerImzML(filepath=str(imzml_path), max_threads=READ_THREADS)
    caches = []
    seen_spectra = 0
    try:
        dm.load_head_data()
        for mz_data, intensity_flat, lengths, _ in dm.flat_generator(
            batch_size=BATCH_SIZE,
            include_mz=False,
            max_threads=READ_THREADS,
        ):
            remaining = MAX_SPECTRA - seen_spectra if MAX_SPECTRA > 0 else lengths.size
            if remaining <= 0:
                break

            intensity_flat, lengths = _truncate_flat_batch(
                np.asarray(intensity_flat),
                np.asarray(lengths, dtype=np.int32),
                remaining,
            )
            caches.append((mz_data, intensity_flat, lengths))
            seen_spectra += int(lengths.size)

            if MAX_SPECTRA > 0 and seen_spectra >= MAX_SPECTRA:
                break
    finally:
        dm.close()

    if not caches:
        pytest.skip(f"No MassFlow flat batches loaded from {imzml_path}")
    return caches


@pytest.fixture(scope="function")
def m2aia_reader(imzml_path):
    m2 = _import_m2aia()
    return m2.ImzMLReader(str(imzml_path))


def _consume_m2aia_spectra(reader, max_spectra: int) -> tuple[int, int, float]:
    spectrum_count = 0
    point_count = 0
    intensity_sum = 0.0
    for _, _, ys in reader.SpectrumIterator():
        y = np.asarray(ys, dtype=np.float64)
        spectrum_count += 1
        point_count += int(y.size)
        intensity_sum += float(np.sum(y, dtype=np.float64))
        if max_spectra > 0 and spectrum_count >= max_spectra:
            break
    return spectrum_count, point_count, intensity_sum


def _massflow_cached_normalization(flat_caches, method: str) -> tuple[int, int, float]:
    apply_numba_runtime(override_workers=NUMBA_THREADS)
    spectrum_count = 0
    point_count = 0
    intensity_sum = 0.0

    for mz_data, intensity_flat, lengths in flat_caches:
        result = FlatPreprocess.normalization_flat(
            mz_data=mz_data,
            intensity=intensity_flat,
            lengths=lengths,
            method=method,
        )
        spectrum_count += int(lengths.size)
        point_count += int(np.sum(lengths, dtype=np.int64))
        intensity_sum += float(np.sum(result.intensity, dtype=np.float64))

    return spectrum_count, point_count, intensity_sum


def _m2aia_cached_normalization(reader, method: str) -> tuple[int, int, float]:
    reader.SetNormalization("None")
    reader.SetNormalization(method)
    reader.lib.Update(reader.handle)
    return _consume_m2aia_spectra(reader, MAX_SPECTRA)


def _massflow_cached_smoothing(flat_caches, method: str, window: int) -> tuple[int, int, float]:
    apply_numba_runtime(override_workers=NUMBA_THREADS)
    spectrum_count = 0
    point_count = 0
    intensity_sum = 0.0

    for mz_data, intensity_flat, lengths in flat_caches:
        result = FlatPreprocess.noise_reduction_flat(
            mz_data=mz_data,
            intensity=intensity_flat,
            lengths=lengths,
            method=method,
            window=window,
        )
        spectrum_count += int(lengths.size)
        point_count += int(np.sum(lengths, dtype=np.int64))
        intensity_sum += float(np.sum(result.intensity, dtype=np.float64))

    return spectrum_count, point_count, intensity_sum


def _m2aia_cached_smoothing(reader, method: str, half_window_size: int) -> tuple[int, int, float]:
    reader.SetSmoothing("None", half_window_size)
    reader.SetSmoothing(method, half_window_size)
    reader.lib.Update(reader.handle)
    return _consume_m2aia_spectra(reader, MAX_SPECTRA)


class TestCachedNormalizationBenchmark:
    @pytest.mark.benchmark(timer=time.perf_counter)
    @pytest.mark.parametrize(
        ("_case_name", "massflow_method"),
        [(case[0], case[1]) for case in NORMALIZATION_CASES],
        ids=[case[0] for case in NORMALIZATION_CASES],
    )
    def test_massflow_cached_normalization(self, benchmark, massflow_flat_caches, _case_name, massflow_method):
        result = benchmark.pedantic(
            _massflow_cached_normalization,
            args=(massflow_flat_caches, massflow_method),
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
    def test_m2aia_cached_normalization(self, benchmark, m2aia_reader, _case_name, m2aia_method):
        result = benchmark.pedantic(
            _m2aia_cached_normalization,
            args=(m2aia_reader, m2aia_method),
            rounds=ROUNDS,
            iterations=1,
            warmup_rounds=1,
        )
        assert result[0] > 0
        assert result[1] > 0


class TestCachedSmoothingBenchmark:
    @pytest.mark.benchmark(timer=time.perf_counter)
    @pytest.mark.parametrize(
        ("_case_name", "massflow_method", "window"),
        [(case[0], case[1], case[3]) for case in SMOOTHING_CASES],
        ids=[case[0] for case in SMOOTHING_CASES],
    )
    def test_massflow_cached_smoothing(self, benchmark, massflow_flat_caches, _case_name, massflow_method, window):
        result = benchmark.pedantic(
            _massflow_cached_smoothing,
            args=(massflow_flat_caches, massflow_method, window),
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
    def test_m2aia_cached_smoothing(self, benchmark, m2aia_reader, _case_name, m2aia_method, half_window_size):
        result = benchmark.pedantic(
            _m2aia_cached_smoothing,
            args=(m2aia_reader, m2aia_method, half_window_size),
            rounds=ROUNDS,
            iterations=1,
            warmup_rounds=1,
        )
        assert result[0] > 0
        assert result[1] > 0
