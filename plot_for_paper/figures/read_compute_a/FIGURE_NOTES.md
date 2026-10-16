# Panel a | Python/NumPy time divided by Numba time

Purpose: compare the measured runtime advantage across operators and dataset sizes, using the original panel a layout, palette and logarithmic axis.

Min/Mid retain cached core timings; Max/Ultra use the new streaming read + compute measurements. No measured operation writes processed results. Input manager/header initialization and peak-picking input preparation remain outside the timer. These four columns must not all be described as pure computation.

Each bar divides the arithmetic means of two technical repetitions after one warmup. No error bars or statistical tests are shown. The dashed line is 1×; red bar edges indicate ratios below 1×. Annotations give each stage's highest ratio. Numba uses four compute threads. Python and Numba retain their own reading APIs; the comparison includes their native batching and allocation costs.

Python Origin is the shared reference for Quantile, Diff and SD: these compare different peak-picking algorithms. Python has no Reference or MAD baseline; their original positions remain empty. Min/Mid Python SNIP retains the previously reused M5 cache entry, including its documented entry overhead.

The two campaigns use the same recorded machine, input data and numerical configuration. They ran separately, with no thermal or swap history; ratios near 1× should not be read as established differences. Source JSON paths, hashes, scopes and reuse flags are in source_data.csv. The old a–c figure is preserved.

## Speedup ratios

| Stage | Method | Min | Mid | Max | Ultra |
| --- | --- | ---: | ---: | ---: | ---: |
| Baseline Correction | LocMin | 6.228× | 5.526× | 5.392× | 3.438× |
| Baseline Correction | SNIP | 4.204× | 2.118× | 2.071× | 1.978× |
| Normalization | TIC | 8.476× | 1.971× | 2.292× | 2.464× |
| Normalization | RMS | 16.729× | 4.653× | 3.610× | 2.934× |
| Peak Alignment | Default | 10.151× | 3.788× | 2.592× | 1.630× |
| Noise Reduction | MA | 17.149× | 4.410× | 3.631× | 2.824× |
| Noise Reduction | Gaussian | 14.388× | 2.096× | 2.201× | 2.579× |
| Noise Reduction | Savitzky–Golay | 38.644× | 5.000× | 4.045× | 4.897× |
| Peak Picking | Quantile | 4.535× | 1.707× | 1.577× | 1.554× |
| Peak Picking | Diff | 25.019× | 7.576× | 6.809× | 5.544× |
| Peak Picking | SD | 16.280× | 5.899× | 5.089× | 4.407× |

## Export and QA

Python/matplotlib; quantitative grid; 7.2 × 2.75 inch canvas; 5 stage axes, 44 bars; no text outside the canvas. Editable SVG/PDF and 600 dpi PNG. Original font, palette, bar spacing, logarithmic axis, missing-method positions and stage maxima are retained.

Reproduce from the repository root:

```bash
uv run --frozen --extra r python plot_for_paper/plot_read_compute_a.py
```
