"""Python/NumPy reference-axis computation for the benchmark.

Ported from peak_align_helper_v1.py: retain its grid estimation, per-spectrum
bin conflict resolution and frequency-weighted merging. Replace only the
Numba nearest-neighbor search with NumPy searchsorted and vector operations.
No Numba or MassFlow processing helper is imported by this module.
"""
import numpy as np

MIN_RELATIVE_RES = 5e-7
MIN_ABSOLUTE_RES = 1e-4


def search_nearest_numpy(queries, targets, tolerance, code=2,
                         nomatch_value=-1, force_nearest=False):
    """Nearest sorted target; prefer the left neighbor on equal distances."""
    queries = np.asarray(queries, dtype=np.float64)
    targets = np.asarray(targets, dtype=np.float64)
    result = np.full(queries.size, nomatch_value, dtype=np.int64)
    if targets.size == 0:
        return result
    positions = np.searchsorted(targets, queries)
    left = np.clip(positions - 1, 0, targets.size - 1)
    right = np.clip(positions, 0, targets.size - 1)
    left_distance = np.abs(queries - targets[left])
    right_distance = np.abs(queries - targets[right])
    if code != 2:
        left_denominator = np.abs(queries if code == 0 else targets[left])
        right_denominator = np.abs(queries if code == 0 else targets[right])
        with np.errstate(divide="ignore", invalid="ignore"):
            left_distance = left_distance / left_denominator
            right_distance = right_distance / right_denominator
    accept_left = (positions > 0) & (force_nearest | (left_distance <= tolerance))
    accept_right = (positions < targets.size) & (force_nearest | (right_distance <= tolerance))
    result[accept_left] = left[accept_left]
    replace = accept_right & (~accept_left | (right_distance < left_distance))
    result[replace] = right[replace]
    return result


def _normalize_units(units):
    if units in ('ppm', 'relative'):
        return 'relative'
    return 'absolute'

def get_method_code(tol_method):
    if tol_method == 'x':
        return 0
    if tol_method == 'y':
        return 1
    return 2

def mad(x, constant=1.4826):
    if x.size == 0:
        return np.nan
    median = np.median(x)
    diff = np.abs(x - median)
    return constant * float(np.median(diff))

def estimate_resolution(x, tolerance=None, method=None):
    if x.size <= 1:
        return np.nan
    xs = np.sort(x)
    dx = np.diff(xs)
    (a, b) = (xs[:-1], xs[1:])
    rx = 2.0 * (b - a) / (b + a)
    eps = np.finfo(float).eps
    dx = dx[dx > eps]
    rx = rx[np.abs(rx) > eps]
    chosen_method = method
    if chosen_method is None:
        if dx.size and rx.size:
            range_span = xs[-1] - xs[0]
            lhs = mad(dx / range_span) if range_span > 0 else np.nan
            rhs = mad(rx)
            chosen_method = 'abs' if lhs < rhs else 'x'
        elif dx.size:
            chosen_method = 'abs'
        elif rx.size:
            chosen_method = 'x'
        else:
            return np.nan
    target_arr = dx if chosen_method == 'abs' else rx
    if target_arr.size == 0:
        return np.nan
    res = float(np.min(target_arr))
    if tolerance is not None:
        residuals = np.mod(target_arr, res)
        if not np.all(residuals <= tolerance):
            return np.nan
    return res

def generate_relative_sequence(start, end, step):
    if start <= 0 or end <= 0:
        return np.array([], dtype=np.float64)
    half = step / 2.0
    ratio = (1.0 + half) / (1.0 - half)
    count = int(np.floor(1.0 + (np.log(end) - np.log(start)) / np.log(ratio)))
    indices = np.arange(count, dtype=np.float64)
    return start * np.power(ratio, indices)

def calc_diff(x, y=None, method='y'):
    if y is None:
        if x.size <= 1:
            return np.array([], dtype=np.float64)
        y = x[:-1]
        x = x[1:]
    x = x.astype(np.float64, copy=False)
    y = y.astype(np.float64, copy=False)
    n = max(x.size, y.size)
    if x.size != n:
        x = np.resize(x, n)
    if y.size != n:
        y = np.resize(y, n)
    if method == 'abs':
        return x - y
    denominator = x if method == 'x' else y
    return (x - y) / denominator

def scalar_diff(val1, val2, method):
    diff = abs(val1 - val2)
    if method == 'abs':
        return diff
    denominator = val1 if method == 'x' else val2
    return diff / abs(denominator) if denominator != 0 else float('inf')

def estimate_domain(data_manager, binfun='median', binratio=2.0, units='relative', clear_memory=True, batch_size=256):
    ref_method = 'x' if units == 'relative' else 'abs'
    stats = []
    for batch in data_manager.batch_generator(batch_size=batch_size):
        for spec in batch:
            mz_list = np.asarray(spec.mz_list, dtype=np.float64)
            valid_mz = mz_list[np.isfinite(mz_list)]
            res = estimate_resolution(valid_mz, method=ref_method)
            if valid_mz.size > 0 and np.isfinite(res):
                stats.append((float(np.min(valid_mz)), float(np.max(valid_mz)), res))
            else:
                stats.append((np.nan, np.nan, res))
        if clear_memory:
            data_manager.clear_batch_data_memory(batch)
    stats_arr = np.array(stats, dtype=np.float64)
    mz_min = float(np.floor(np.nanmin(stats_arr[:, 0])))
    mz_max = float(np.ceil(np.nanmax(stats_arr[:, 1])))
    resolutions = stats_arr[:, 2]
    if binfun == 'median':
        step = float(np.nanmedian(resolutions))
    elif binfun == 'min':
        step = float(np.nanmin(resolutions))
    elif binfun == 'max':
        step = float(np.nanmax(resolutions))
    else:
        step = float(np.nanmean(resolutions))
    if units == 'relative':
        step = round(2.0 * step, 6) * 0.5
        step = max(MIN_RELATIVE_RES, step)
        tolerance = round(2.0 * (step * binratio), 6) * 0.5
        domain = generate_relative_sequence(mz_min, mz_max, step)
    else:
        step = round(step, 4)
        step = max(MIN_ABSOLUTE_RES, step)
        tolerance = round(step * binratio, 4)
        domain = np.arange(mz_min, mz_max + step, step, dtype=np.float64)
    return (domain, tolerance)

def bin_peaks(data_manager, domain, tolerance, tol_method='abs', batch_size=256, clear_memory=True):
    code = get_method_code(tol_method)
    peaks_acc = np.zeros(domain.size, dtype=np.float64)
    counts = np.zeros(domain.size, dtype=np.int64)
    for batch in data_manager.batch_generator(batch_size=batch_size):
        for spec in batch:
            raw_peaks = np.array(spec.mz_list, dtype=np.float64)
            if raw_peaks.size == 0:
                continue
            bin_indices = search_nearest_numpy(raw_peaks, domain, tolerance, code, nomatch_value=-1, force_nearest=False)
            valid_mask = bin_indices >= 0
            if not np.any(valid_mask):
                continue
            valid_bins = bin_indices[valid_mask].astype(np.int64)
            valid_peaks = raw_peaks[valid_mask]
            dists = np.abs(calc_diff(valid_peaks, domain[valid_bins], method=tol_method))
            n_valid = valid_bins.size
            sort_arr = np.empty(n_valid, dtype=[('bin', 'i8'), ('dist', 'f8'), ('idx', 'i8')])
            sort_arr['bin'] = valid_bins
            sort_arr['dist'] = dists
            sort_arr['idx'] = np.arange(n_valid)
            sort_arr.sort(order=['bin', 'dist'], kind='stable')
            (_, unique_indices) = np.unique(sort_arr['bin'], return_index=True)
            best_matches = sort_arr[unique_indices]
            matched_bins = best_matches['bin']
            matched_peaks = valid_peaks[best_matches['idx']]
            np.add.at(peaks_acc, matched_bins, matched_peaks)
            np.add.at(counts, matched_bins, 1)
        if clear_memory:
            data_manager.clear_batch_data_memory(batch)
    nonzero = counts != 0
    peaks_acc[nonzero] /= counts[nonzero]
    peaks_acc[~nonzero] = np.nan
    valid_mask = ~np.isnan(peaks_acc)
    valid_peaks = peaks_acc[valid_mask]
    valid_counts = counts[valid_mask]
    reference = merge_peaks(mz_list=valid_peaks, counts=valid_counts, tolerance=tolerance, tol_method=tol_method)
    return reference

def merge_peaks(mz_list, counts, tolerance, tol_method='abs'):
    valid_peaks = mz_list[~np.isnan(mz_list)]
    if valid_peaks.size > 1 and np.any(np.diff(valid_peaks) < 0):
        raise ValueError('peaks must be sorted')
    n = mz_list.size
    k = 0
    while k < n and np.isnan(mz_list[k]):
        k += 1
    while k < n:
        i = k
        j = k
        left_of_mode = False
        while i - 1 >= 0:
            if np.isnan(mz_list[i - 1]):
                break
            dist = scalar_diff(mz_list[i], mz_list[i - 1], tol_method)
            if dist > tolerance:
                break
            if counts[i - 1] < counts[i]:
                left_of_mode = True
            if counts[i - 1] > counts[i] and left_of_mode:
                break
            i -= 1
        right_of_mode = False
        while j + 1 < n:
            if np.isnan(mz_list[j + 1]):
                break
            dist = scalar_diff(mz_list[j + 1], mz_list[j], tol_method)
            if dist > tolerance:
                break
            if counts[j + 1] < counts[j]:
                right_of_mode = True
            if counts[j + 1] > counts[j] and right_of_mode:
                break
            j += 1
        indices = np.arange(i, j + 1)
        w = counts[indices].astype(np.float64)
        w_sum = np.sum(w)
        if w_sum > 0:
            merged_peak = np.sum(w * mz_list[indices]) / w_sum
        else:
            merged_peak = np.mean(mz_list[indices])
        merged_count = np.sum(counts[indices])
        p = int(np.floor((i + j) / 2.0))
        mz_list[p] = merged_peak
        counts[p] = int(merged_count)
        mask = np.ones(indices.size, dtype=bool)
        mask[p - i] = False
        cleared_indices = indices[mask]
        mz_list[cleared_indices] = np.nan
        counts[cleared_indices] = 0
        k = j + 1
        while k < n and np.isnan(mz_list[k]):
            k += 1
    valid = ~np.isnan(mz_list)
    return mz_list[valid]

def compute_reference(data_manager, reference=None, binfun='median', binratio=2.0, tolerance=None, units='ppm', clear_memory=True, batch_size=256):
    norm_units = _normalize_units(units)
    tol_method = 'x' if norm_units == 'relative' else 'abs'
    (domain, estimate_tolerance) = estimate_domain(data_manager=data_manager, binfun=binfun, binratio=binratio, units=norm_units, clear_memory=clear_memory, batch_size=batch_size)
    tolerance = estimate_tolerance if tolerance is None else tolerance * 1e-06 if units == 'ppm' else tolerance
    if reference is not None:
        return (reference, tolerance)
    reference = bin_peaks(data_manager=data_manager, domain=domain, tolerance=tolerance, tol_method=tol_method, batch_size=batch_size, clear_memory=clear_memory)
    return (reference, tolerance)
