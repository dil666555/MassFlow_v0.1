import os
import time
from pathlib import Path

import numpy as np
import pytest

from massflow.data_manager import MSDataManagerImzML
from massflow.preprocess.flat_pre_fun import FlatPreprocess
from massflow.preprocess.numba.numba_runtime import apply_numba_runtime


ROUNDS = int(os.getenv("MASSFLOW_M2AIA_BENCHMARK_ROUNDS", "5"))
BATCH_SIZE = int(os.getenv("MASSFLOW_M2AIA_BENCHMARK_BATCH_SIZE", "256"))
MAX_THREADS = int(os.getenv("MASSFLOW_M2AIA_BENCHMARK_MAX_THREADS", str(os.cpu_count() or 16)))
BENCHMARK_DATASETS = [
    ("example", Path("/root/autodl-tmp/data/example.imzML")),
    ("min", Path("/root/autodl-tmp/data/file_min_profile.imzML")),
    ("mid", Path("/root/autodl-tmp/data/file_mid_profile.imzML")),
    ("original", Path("/root/autodl-tmp/data/original.imzML")),
]
SMOOTHING_CASES = [
    ("gaussian_window5", "gaussian_numba", "Gaussian", 5, 2),
]


@pytest.fixture(scope="module", params=BENCHMARK_DATASETS, ids=[item[0] for item in BENCHMARK_DATASETS])
def imzml_path(request):
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


def _massflow_smoothing(path: Path, method: str, window: int) -> tuple[int, int, float]:
    apply_numba_runtime(override_workers=MAX_THREADS)

    dm = MSDataManagerImzML(filepath=str(path), max_threads=MAX_THREADS)
    try:
        dm.load_head_data()

        spectrum_count = 0
        point_count = 0
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
                method=method,
                window=window,
            )
            spectrum_count += int(lengths.size)
            point_count += int(lengths.sum())
            intensity_sum += float(result.intensity.sum())

        return spectrum_count, point_count, intensity_sum
    finally:
        dm.close()


def _m2aia_smoothing(m2, path: Path, method: str, half_window_size: int) -> tuple[int, int, float]:
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


class TestSmoothingBenchmark:
    @pytest.mark.benchmark(timer=time.perf_counter)
    @pytest.mark.parametrize(
        ("_case_name", "massflow_method", "window"),
        [(case[0], case[1], case[3]) for case in SMOOTHING_CASES],
        ids=[case[0] for case in SMOOTHING_CASES],
    )
    def test_massflow_smoothing(
        self,
        benchmark,
        imzml_path,
        _case_name,
        massflow_method,
        window,
    ):
        result = benchmark.pedantic(
            _massflow_smoothing,
            args=(imzml_path, massflow_method, window),
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
    def test_m2aia_smoothing(
        self,
        benchmark,
        imzml_path,
        _case_name,
        m2aia_method,
        half_window_size,
    ):
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
