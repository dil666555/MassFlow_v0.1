import os
import time
from pathlib import Path

import numpy as np
import pytest

from massflow.data_manager import MSDataManagerImzML


ROUNDS = int(os.getenv("MASSFLOW_M2AIA_BENCHMARK_ROUNDS", "5"))
BATCH_SIZE = int(os.getenv("MASSFLOW_M2AIA_BENCHMARK_BATCH_SIZE", "256"))
MAX_THREADS = int(os.getenv("MASSFLOW_M2AIA_BENCHMARK_MAX_THREADS", str(os.cpu_count() or 16)))
BENCHMARK_DATASETS = [
    ("example", Path("/root/autodl-tmp/data/example.imzML")),
    ("min", Path("/root/autodl-tmp/data/file_min_profile.imzML")),
    ("mid", Path("/root/autodl-tmp/data/file_mid_profile.imzML")),
    ("original", Path("/root/autodl-tmp/data/original.imzML")),
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


def _read_all_spectra_massflow_flat(path: Path) -> tuple[int, int, int, float, float]:
    """Read all spectra through MassFlow's direct flat imzML reader."""
    dm = MSDataManagerImzML(filepath=str(path), max_threads=MAX_THREADS)
    try:
        dm.load_head_data()

        spectrum_count = 0
        point_count = 0
        mz_point_count = 0
        mz_sum = 0.0
        intensity_sum = 0.0

        for mz_data, intensity_flat, lengths, _ in dm.flat_generator(
            batch_size=BATCH_SIZE,
            include_mz=True,
            max_threads=MAX_THREADS,
        ):
            logical_points = int(lengths.sum())
            spectrum_count += int(lengths.size)
            point_count += logical_points
            mz_point_count += logical_points
            if mz_data.size == intensity_flat.size:
                mz_sum += float(np.sum(mz_data, dtype=np.float64))
            else:
                mz_sum += float(np.sum(mz_data, dtype=np.float64)) * int(lengths.size)
            intensity_sum += float(np.sum(intensity_flat, dtype=np.float64))

        return spectrum_count, point_count, mz_point_count, mz_sum, intensity_sum
    finally:
        dm.close()


def _read_all_spectra_m2aia(m2, path: Path) -> tuple[int, int, int, float, float]:
    """Read all spectra through m2aia without signal processing."""
    reader = m2.ImzMLReader(str(path))

    spectrum_count = 0
    point_count = 0
    mz_point_count = 0
    mz_sum = 0.0
    intensity_sum = 0.0

    for _, xs, ys in reader.SpectrumIterator():
        x = np.asarray(xs, dtype=np.float64)
        y = np.asarray(ys, dtype=np.float64)
        spectrum_count += 1
        point_count += int(y.size)
        mz_point_count += int(x.size)
        mz_sum += float(np.sum(x, dtype=np.float64))
        intensity_sum += float(np.sum(y, dtype=np.float64))

    return spectrum_count, point_count, mz_point_count, mz_sum, intensity_sum


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
        assert result[2] > 0

    @pytest.mark.benchmark(timer=time.perf_counter)
    def test_m2aia_read_all_spectra(self, benchmark, imzml_path):
        m2 = _import_m2aia()
        result = benchmark.pedantic(
            _read_all_spectra_m2aia,
            args=(m2, imzml_path),
            rounds=ROUNDS,
            iterations=1,
            warmup_rounds=1,
        )
        assert result[0] > 0
        assert result[1] > 0
        assert result[2] > 0
