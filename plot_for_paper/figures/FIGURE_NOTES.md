# Figure a–c | Runtime and sampled RSS ratios

a, Python/NumPy divided by Numba time. Min/Mid use cached spectra; Max/Ultra
use each implementation's pipeline time. Min/Mid Python SNIP reuses the
previous M5 measurement, including its cache-generator overhead. Python
Origin serves as a shared method reference for Quantile/Diff/SD; these are
different peak-picking algorithms. Reference and MAD have no Python baseline.

b, Cardinal process divided by Numba pipeline time. c, Cardinal divided by
Numba pipeline sampled peak RSS. Every bar divides two means from two
technical repetitions after one warmup; error bars are not shown. Red edges
indicate ratios below 1. Stage annotations identify the highest ratio.

MassFlow includes result writing; Cardinal does not export and does not force
all lazy aligned intensities. Gaussian defaults, normalization scales and
reference-selection rules differ. Numba uses four compute threads. Cardinal
passes BPPARAM=NULL to matter's serial loop; the registered eight-worker
BiocParallel backend is not the effective process backend.

Cardinal's R vector-heap limit was raised from 16 to 32 GiB after the Max
failure; the machine has 16 GiB physical RAM. RSS is sampled, includes runtime
and resident caches, and excludes swapped-out pages. No thermal or swap
history was recorded. Close-to-one ratios and high-variation cases should
not be interpreted as statistically established gains. Full provenance,
round values and caveats are in benchmarks/RESULTS.md; each bar is traced by
source_data.csv, including original JSON SHA-256 hashes.

QA: 15 axes; 148 bars; labels within the canvas; original font sizes, palette,
line widths and layout retained. SVG/PDF contain editable text; PNG is 600 dpi.
The rendered PNG was visually compared with the original a–c figure;
font, palette, stage spacing and annotation placement were reviewed.
