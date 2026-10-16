"""Streaming reference binning with the original Numba arithmetic.

Retain bin_peaks_parallel exactly, except obtain the spectrum count from
metadata instead of reading the entire stream only for a log message.
"""
import numpy as np
from numpy.typing import NDArray
import massflow.preprocess.numba.peak_align_numba as compute
from massflow.preprocess.helper.peak_align_helper import (
    estimate_domain_parallel, get_method_code, logger, merge_peaks,
)


def bin_peaks_stream(
    flat_caches,
    domain: NDArray,
    tolerance: float,
    tol_method: str = "abs",
    *,
    total_spectra: int,
) -> NDArray:
    """Parallel binning using flat batches + parallel nearest search."""
    logger.info(
        f"[parallel] Binning peaks: {total_spectra} spectra, "
        f"domain size {domain.size}, tolerance {tolerance}"
    )

    code = get_method_code(tol_method)
    peaks_acc = np.zeros(domain.size, dtype=np.float64)
    counts = np.zeros(domain.size, dtype=np.int64)

    for mz_data, _, lengths in flat_caches:
        if mz_data is None:
            continue

        lengths_arr = np.asarray(lengths, dtype=np.int32)
        if lengths_arr.size == 0:
            continue

        mz_arr = np.asarray(mz_data, dtype=np.float64)

        if mz_arr.ndim != 1:
            raise ValueError(f"Unsupported mz_data ndim={mz_arr.ndim}; expected 1.")

        total_points = int(np.sum(lengths_arr, dtype=np.int64))
        max_len = int(np.max(lengths_arr)) if lengths_arr.size > 0 else 0
        is_shared_mz = mz_arr.size != total_points

        # Continuous mode: shared m/z for all spectra in this batch
        if is_shared_mz:
            if mz_arr.size != max_len:
                raise ValueError(
                    "Incompatible flat batch for shared m/z mode: "
                    f"mz_size={mz_arr.size}, max_len={max_len}, total_points={total_points}."
                )

            raw_peaks = mz_arr
            if raw_peaks.size == 0:
                continue

            bin_indices = compute.search_nearest_jit(
                queries=raw_peaks,
                targets=domain,
                tolerance=tolerance,
                code=code,
                nomatch_value=-1,
                force_nearest=False,
            )

            if np.all(lengths_arr == raw_peaks.size):
                tmp_peaks_acc = np.zeros_like(peaks_acc)
                tmp_counts = np.zeros_like(counts)
                compute.accumulate_best_matches_for_spectrum_jit(
                    raw_peaks=raw_peaks,
                    bin_indices=bin_indices,
                    domain=domain,
                    method_code=code,
                    peaks_acc=tmp_peaks_acc,
                    counts=tmp_counts,
                )

                n_spec = int(lengths_arr.size)
                if n_spec > 0:
                    peaks_acc += tmp_peaks_acc * n_spec
                    counts += tmp_counts * n_spec
            else:
                for valid_len in lengths_arr:
                    peak_len = int(valid_len)
                    if peak_len <= 0:
                        continue

                    compute.accumulate_best_matches_for_spectrum_jit(
                        raw_peaks=raw_peaks[:peak_len],
                        bin_indices=bin_indices[:peak_len],
                        domain=domain,
                        method_code=code,
                        peaks_acc=peaks_acc,
                        counts=counts,
                    )
            continue

        # Processed mode: per-spectrum flattened m/z array
        nearest_idx = compute.search_nearest_flat_parallel_jit(
            mz_flat=mz_arr,
            lengths=lengths_arr,
            targets=domain,
            tolerance=tolerance,
            code=code,
            nomatch_value=-1,
        )

        compute.accumulate_best_matches_for_flat_jit(
            raw_peaks_flat=mz_arr,
            bin_indices_flat=nearest_idx,
            lengths=lengths_arr,
            domain=domain,
            method_code=code,
            peaks_acc=peaks_acc,
            counts=counts,
        )

    nonzero = counts != 0
    peaks_acc[nonzero] /= counts[nonzero]
    peaks_acc[~nonzero] = np.nan

    valid_mask = ~np.isnan(peaks_acc)
    valid_peaks = peaks_acc[valid_mask]
    valid_counts = counts[valid_mask]

    reference = merge_peaks(
        mz_list=valid_peaks,
        counts=valid_counts,
        tolerance=tolerance,
        tol_method=tol_method,
    )

    return reference


def reference_computer_stream(flat_batches, total_spectra, binfun="median",
                              binratio=2.0, units="ppm"):
    norm_units = "relative" if units in ("ppm", "relative") else "absolute"
    domain, tolerance = estimate_domain_parallel(
        flat_batches, binfun=binfun, binratio=binratio, units=norm_units,
    )
    reference = bin_peaks_stream(
        flat_batches, domain, tolerance,
        tol_method="x" if norm_units == "relative" else "abs",
        total_spectra=total_spectra,
    )
    return reference, tolerance
