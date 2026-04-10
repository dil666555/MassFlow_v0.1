from typing import Optional
import numpy as np
from numba import jit, prange
from massflow.tools.funs import prepare_flat_inputs, lengths_to_offsets

# -----------------------------------------------------------------------------
# Core Calculation Kernels (Helpers)
# -----------------------------------------------------------------------------


@jit(nopython=True, cache=True)
def _get_tic(arr: np.ndarray) -> float:
    return np.sum(arr)


@jit(nopython=True, cache=True)
def _get_rms(arr: np.ndarray) -> float:
    # RMS = sqrt( sum(x^2) / n )
    s = 0.0
    n = arr.shape[0]
    if n == 0:
        return 0.0
    for i in range(n):
        val = arr[i]
        s += val * val
    return np.sqrt(s / n)


@jit(nopython=True, cache=True)
def _get_median(arr: np.ndarray) -> float:
    return np.median(arr)  # type: ignore


@jit(nopython=True, cache=True)
def _apply_unit_scaling_inplace(arr: np.ndarray):
    """Applies Min-Max scaling to [0, 1] in-place."""
    n = arr.shape[0]
    if n == 0:
        return

    min_val = np.inf
    max_val = -np.inf

    # Pass 1: Find Min/Max
    for i in range(n):
        val = arr[i]
        if val < min_val:
            min_val = val
        if val > max_val:
            max_val = val

    rng = max_val - min_val

    # Pass 2: Scale
    if rng > 0:
        for i in range(n):
            arr[i] = (arr[i] - min_val) / rng
    else:
        for i in range(n):
            arr[i] = 0.0


# -----------------------------------------------------------------------------
# Batch Logic
# -----------------------------------------------------------------------------


@jit(nopython=True, cache=True)
def _normalize_core(
    in_arr: np.ndarray,
    out_arr: np.ndarray,
    method_enum: int,
    scale_factor: float,
    do_unit_scale: bool,
):
    """
    Process a single row (view) and write to output view.
    """
    # 1. Calculate Base Factor
    base = np.float64(0.0)
    if method_enum == 0:  # TIC
        base = np.float64(_get_tic(in_arr))
    elif method_enum == 1:  # RMS
        base = np.float64(_get_rms(in_arr))
    elif method_enum == 2:  # MEDIAN
        base = np.float64(_get_median(in_arr))

    # Safety Check
    if base <= 0.0 or np.isnan(base):
        # Assuming out_arr is zeroed by caller, just return
        return

    # 2. Apply Normalization
    factor = np.float64(scale_factor) / base
    n = in_arr.shape[0]

    for i in range(n):
        out_arr[i] = np.float64(in_arr[i]) * factor

    # 3. Apply Unit Scaling if requested
    if do_unit_scale:
        _apply_unit_scaling_inplace(out_arr)


@jit(nopython=True, parallel=True, cache=True)
def _normalize_flat_jit(
    flat: np.ndarray,
    method_enum: int,
    scale_factor: float,
    do_unit_scale: bool,
    lengths: np.ndarray,
) -> np.ndarray:
    res = np.zeros(flat.size, dtype=flat.dtype)
    offsets = lengths_to_offsets(lengths)

    for p in prange(lengths.size): # pylint: disable=not-an-iterable
        start = offsets[p]
        end = offsets[p + 1]
        if end > start:
            _normalize_core(
                flat[start:end],
                res[start:end],
                method_enum,
                scale_factor,
                do_unit_scale,
            )

    return res


# -----------------------------------------------------------------------------
# Main Dispatcher
# -----------------------------------------------------------------------------


def normalizer_numba(
    intensity: np.ndarray,
    method: str = "tic",
    scale: float = 1.0,
    scale_method: str = "none",
    lengths: Optional[np.ndarray] = None,
) -> np.ndarray:
    """
    Numba backend for flat-mode normalization.

    Parameters:
        intensity: 1D flat array.
        method: 'tic', 'rms', 'median'.
        scale: Amplitude scaling factor.
        scale_method: 'none' or 'unit'.
        lengths: (Optional) 1D int array of valid lengths per spectrum. If omitted,
            the full input is treated as one spectrum.
    """

    intensity_arr, lengths_arr = prepare_flat_inputs(intensity, lengths)

    # Map Method
    method_clean = method.strip().lower()
    if method_clean == "tic":
        m_enum = 0
    elif method_clean == "rms":
        m_enum = 1
    elif method_clean == "median":
        m_enum = 2
    else:
        raise ValueError(f"Unknown method for numba normalizer: {method}")

    # Map Scale Method
    scale_clean = (scale_method or "none").strip().lower()
    do_unit = scale_clean == "unit"

    return _normalize_flat_jit(intensity_arr, m_enum, float(scale), do_unit, lengths_arr)
