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
MAX_THREADS = int(os.getenv("MASSFLOW_M2AIA_BENCHMARK_MAX_THREADS", str(os.cpu_count() or 16)))
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


def _massflow_normalization(path: Path, method: str) -> tuple[int, int, float]:
    """Run MassFlow flat normalization and consume all processed intensities."""
    apply_numba_runtime(override_workers=MAX_THREADS)


    dm = MSDataManagerImzML(filepath=str(path), max_threads=MAX_THREADS)
    try:
        dm.load_head_data()

        intensity_sum = 0.0
        spectrum_count = 0
        point_count = 0


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
            point_count += int(lengths.sum())
            intensity_sum += float(np.sum(result.intensity, dtype=np.float64))

        return spectrum_count, point_count, intensity_sum
    finally:
        dm.close()


def _m2aia_normalization(m2, path: Path, method: str) -> tuple[int, int, float]:
    """Run m2aia normalization and consume all processed intensities."""
    reader = m2.ImzMLReader(str(path), normalization=method)

    spectrum_count = 0
    point_count = 0
    intensity_sum = 0.0

    for _, _, ys in reader.SpectrumIterator():
        y = np.asarray(ys, dtype=np.float64)
        spectrum_count += 1
        point_count += int(y.size)
        intensity_sum += float(np.sum(y, dtype=np.float64))

    return spectrum_count, point_count, intensity_sum


class TestNormalizationBenchmark:
    @pytest.mark.benchmark(timer=time.perf_counter)
    @pytest.mark.parametrize(
        ("_case_name", "massflow_method"),
        [(case[0], case[1]) for case in NORMALIZATION_CASES],
        ids=[case[0] for case in NORMALIZATION_CASES],
    )
    def test_massflow_normalization(self, benchmark, imzml_path, _case_name, massflow_method):
        result = benchmark.pedantic(
            _massflow_normalization,
            args=(imzml_path, massflow_method),
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
    def test_m2aia_normalization(self, benchmark, imzml_path, _case_name, m2aia_method):
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
