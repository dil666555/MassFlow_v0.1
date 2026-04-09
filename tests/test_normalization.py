import gc
import time
import tracemalloc
import warnings

import numpy as np
import pytest

from massflow.data_manager import MSDataManagerImzML
from massflow.preprocess import BatchPreprocess
from massflow.preprocess.flat_pre_fun import FlatPreprocess
from massflow.tools.dm_process import speed_process
from massflow.tools.logger import get_logger

logger = get_logger("massflow.test.test_normalization")

ROUNDS = 3
BATCH_NORM_METHODS = ["tic", "rms", "median"]
FLAT_NORM_METHODS = ["tic_numba", "rms_numba", "median_numba"]
BATCH_FLAT_NORM_METHOD_PAIRS = [
    ("tic", "tic_numba"),
    ("rms", "rms_numba"),
    ("median", "median_numba"),
]


def _normalization_flat_from_flat_batches(
    flat_batches,
    method: str,
    scale: float,
    scale_method: str,
):
    for intensity_flat, lengths in flat_batches:
        _ = FlatPreprocess.normalization_flat(
            intensity=intensity_flat,
            method=method,
            scale=scale,
            scale_method=scale_method,
            lengths=lengths,
        )


class TestNormalizationAPI:
    """Normalization API tests: memory, speed, consistency, and normalization invariants."""

    @pytest.fixture(scope="module", params=["data/CellTrain.imzML"])
    def ms_raw_data(self, request) -> MSDataManagerImzML:
        data_file_path = request.param
        dm = MSDataManagerImzML(filepath=data_file_path)
        dm.load_head_data()
        for _ in dm.batch_generator(batch_size=512):
            pass
        return dm

    @pytest.fixture(scope="module", params=["data/CellTrain.imzML"])
    def flat_caches(self, request):
        data_file_path = request.param
        dm = MSDataManagerImzML(filepath=data_file_path)
        dm.load_head_data()

        caches = []
        for _, intensity_flat, lengths, _ in dm.flat_generator(
            batch_size=4096,
            include_mz=False,
            max_threads=16,
        ):
            caches.append((intensity_flat, lengths))

        return caches

    @pytest.mark.benchmark(timer=time.perf_counter)
    @pytest.mark.parametrize("method", BATCH_NORM_METHODS)
    def test_norm_batch_speed(
        self,
        benchmark,
        method,
        ms_raw_data,
    ):
        logger.info("Benchmarking batch normalization method=%s", method)

        batch_kwargs = {
            "method": method,
            "scale": 1.0,
            "scale_method": "none",
        }

        benchmark.pedantic(
            speed_process,
            args=(ms_raw_data, 4096, BatchPreprocess.normalization_batch, batch_kwargs),
            rounds=ROUNDS,
            iterations=1,
            warmup_rounds=1,
        )

    @pytest.mark.benchmark(timer=time.perf_counter)
    @pytest.mark.parametrize("method", FLAT_NORM_METHODS)
    def test_norm_flat_speed(
        self,
        benchmark,
        method,
        flat_caches,
    ):
        logger.info("Benchmarking flat normalization method=%s", method)

        benchmark.pedantic(
            _normalization_flat_from_flat_batches,
            args=(flat_caches, method, 1.0, "none"),
            rounds=ROUNDS,
            iterations=1,
            warmup_rounds=1,
        )

    @pytest.mark.parametrize(("batch_method", "flat_method"), BATCH_FLAT_NORM_METHOD_PAIRS)
    def test_norm_flat_batch_intensity_consistency(self, batch_method, flat_method, ms_raw_data):
        batch = next(ms_raw_data.batch_generator(batch_size=256))

        batch_result = BatchPreprocess.normalization_batch(
            batch_spectra=batch,
            method=batch_method,
            scale=1.0,
            scale_method="none",
        )

        lengths = np.array([spectrum.intensity.size for spectrum in batch], dtype=np.int64)
        intensity_flat = np.concatenate(
            [spectrum.intensity.astype(np.float64, copy=False) for spectrum in batch]
        )

        flat_result = FlatPreprocess.normalization_flat(
            intensity=intensity_flat,
            method=flat_method,
            scale=1.0,
            scale_method="none",
            lengths=lengths,
        )

        offset = 0
        for spectrum_batch, valid_len in zip(batch_result, lengths):
            end = offset + int(valid_len)
            flat_slice = flat_result[offset:end]
            assert spectrum_batch.intensity is not None
            np.testing.assert_allclose(
                spectrum_batch.intensity,
                flat_slice,
                rtol=1e-5,
                atol=1e-5,
            )
            offset = end

    @pytest.mark.parametrize("method", BATCH_NORM_METHODS)
    def test_norm_invariants_none(self, method, ms_raw_data):
        batch = next(ms_raw_data.batch_generator(batch_size=32))
        normalized_batch = BatchPreprocess.normalization_batch(
            batch_spectra=batch,
            method=method,
            scale=1.0,
            scale_method="none",
        )

        for spectrum in normalized_batch:
            y = spectrum.intensity
            assert y is not None
            if method == "tic":
                assert np.isclose(np.sum(y), 1.0, rtol=1e-6)
            elif method == "rms":
                assert np.isclose(np.sqrt(np.mean(y ** 2)), 1.0, rtol=1e-6)
            else:
                assert np.isclose(np.median(y), 1.0, rtol=1e-6)

    def test_norm_unit_scaling_range(self, ms_raw_data):
        batch = next(ms_raw_data.batch_generator(batch_size=32))
        normalized_batch = BatchPreprocess.normalization_batch(
            batch_spectra=batch,
            method="tic",
            scale=1.0,
            scale_method="unit",
        )

        for spectrum in normalized_batch:
            y = spectrum.intensity
            assert y is not None
            assert np.min(y) >= 0.0
            assert np.max(y) <= 1.0

    @pytest.mark.parametrize("method", FLAT_NORM_METHODS)
    def test_norm_flat_memory_profile(self, method, flat_caches):
        # Use a small subset for stable memory profiling and to keep test runtime bounded.
        subset = flat_caches[:3]

        gc.collect()
        tracemalloc.start()
        for intensity_flat, lengths in subset:
            _ = FlatPreprocess.normalization_flat(
                intensity=intensity_flat,
                method=method,
                scale=1.0,
                scale_method="none",
                lengths=lengths,
            )
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        logger.info("method=%s tracemalloc current=%d peak=%d", method, current, peak)

        # Guardrail threshold: this test checks absence of obvious runaway allocations.
        assert peak < 512 * 1024 * 1024

    @pytest.mark.parametrize(("batch_method", "flat_method"), BATCH_FLAT_NORM_METHOD_PAIRS)
    def test_norm_batch_flat_memory_comparison(self, batch_method, flat_method, ms_raw_data):
        """Compare steady-state tracemalloc peaks for batch vs flat normalization paths."""
        batch = next(ms_raw_data.batch_generator(batch_size=256))
        lengths = np.array([spectrum.intensity.size for spectrum in batch], dtype=np.int64)
        intensity_flat = np.concatenate(
            [spectrum.intensity.astype(np.float64, copy=False) for spectrum in batch]
        )

        # Warm-up to avoid counting one-time setup/JIT costs in comparison.
        _ = BatchPreprocess.normalization_batch(
            batch_spectra=batch,
            method=batch_method,
            scale=1.0,
            scale_method="none",
        )
        _ = FlatPreprocess.normalization_flat(
            intensity=intensity_flat,
            method=flat_method,
            scale=1.0,
            scale_method="none",
            lengths=lengths,
        )

        gc.collect()
        tracemalloc.start()
        _ = BatchPreprocess.normalization_batch(
            batch_spectra=batch,
            method=batch_method,
            scale=1.0,
            scale_method="none",
        )
        _, batch_peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        gc.collect()
        tracemalloc.start()
        _ = FlatPreprocess.normalization_flat(
            intensity=intensity_flat,
            method=flat_method,
            scale=1.0,
            scale_method="none",
            lengths=lengths,
        )
        _, flat_peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        ratio = float(batch_peak / flat_peak) if flat_peak > 0 else float("inf")
        msg = (
            f"memory-compare method={batch_method}/{flat_method} "
            f"batch_peak={int(batch_peak)}B flat_peak={int(flat_peak)}B ratio_batch_over_flat={ratio:.4f}"
        )
        logger.info(msg)
        warnings.warn(msg, UserWarning)

        assert batch_peak < 512 * 1024 * 1024
        assert flat_peak < 512 * 1024 * 1024
