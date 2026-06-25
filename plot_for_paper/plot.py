"""Composite, publication-style bar charts for the ProjectNAME performance
subsection of the technical note (results & discussion).

Generates the three figures embedded in the paper plus the absolute-performance
table data:
  - fig_expb_speedup.{png,svg}  -> 图2  Experiment (b): Numba(Flat) vs NumPy(Batch) pure-compute speedup
  - fig_expa_time.{png,svg}     -> 图3  Experiment (a): ProjectNAME vs Cardinal runtime ratio
  - fig_expa_memory.{png,svg}   -> 图4  Experiment (a): ProjectNAME vs Cardinal peak-memory ratio
  - stats.json                  -> Table 2 cell values (ProjectNAME flat: time s / peak mem MiB)

Each bar = baseline-tool time/memory divided by ProjectNAME's; bars below 1×
(ProjectNAME loses) are flagged with a red outline. Log y-axis. Output goes to
./figures next to this file.

Sources of truth (curated by the authors, identical to the existing per-method SVGs):
  - ../tests/pipeline_outcome.py : (Cardinal, MassFlow/flat) for time & memory, 4 datasets
  - ../tests/python_outcome.py   : (Batch/NumPy, Flat/Numba) pure-compute time, 3 datasets

Run:  ../.venv/Scripts/python.exe plot.py
"""
import os, sys
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))           # .../MassFlow_v0.1/plot_for_paper
PKG = os.path.dirname(ROOT)                                 # .../MassFlow_v0.1
sys.path.insert(0, PKG)
from tests.pipeline_outcome import TIME_DATA as A_TIME, MEMORY_DATA as A_MEM   # (cardinal, massflow)
from tests.python_outcome import TIME_DATA as B_TIME                            # (batch, flat)

OUT = os.path.join(ROOT, "figures")
os.makedirs(OUT, exist_ok=True)

# ---- style ------------------------------------------------------------------
plt.rcParams.update({
    "font.family": "Arial",
    "font.size": 10,
    "axes.linewidth": 0.7,
    "svg.fonttype": "none",
})
# blue sequential shades (light Min -> dark Ultra), consistent with MassFlow blue
SHADES4 = ["#CFE8F7", "#8FCDEC", "#4FA8DC", "#2E73B0"]
SHADES3 = ["#9AD3EF", "#4FA8DC", "#2E73B0"]
REF = "#9aa0a6"
LOSS = "#E8A0A0"  # outline flag when ProjectNAME loses (<1)

STAGE_ORDER = ["Baseline Correction", "Normalization", "Peak Alignment",
               "Noise Reduction", "Peak Picking"]
STAGE_SHORT = {"Baseline Correction": "Baseline", "Noise Reduction": "Denoising",
               "Normalization": "Normalization", "Peak Picking": "Peak Picking",
               "Peak Alignment": "Alignment"}
METH_SHORT = {"Savitzky–Golay": "SG", "locmin": "LocMin", "snip": "SNIP",
              "Gaussian": "Gauss", "Reference": "Ref"}


def ratio(num, den):
    return float("inf") if den == 0 else num / den


def short(m):
    return METH_SHORT.get(m, m)


def composite(data, stages, datasets, ds_labels, shades, fname, logscale=True):
    """One row of stage panels; grouped bars per method, one bar per dataset.

    Both dicts store the *baseline* tool first and ProjectNAME second, so the
    plotted ratio = baseline / ProjectNAME (>1 favours ProjectNAME).
    """
    methods = {s: list(data[s].keys()) for s in stages}
    counts = [len(methods[s]) for s in stages]
    fig = plt.figure(figsize=(7.2, 2.75))
    gs = fig.add_gridspec(1, len(stages), width_ratios=counts, wspace=0.34)

    all_vals = []
    for s in stages:
        for m in methods[s]:
            for d in datasets:
                a, b = data[s][m][d]
                all_vals.append(ratio(a, b))
    vmax = max(all_vals); vmin = min(all_vals)

    axes = []
    for j, s in enumerate(stages):
        ax = fig.add_subplot(gs[0, j])
        axes.append(ax)
        ms = methods[s]
        x = np.arange(len(ms))
        n = len(datasets)
        bw = 0.8 / n
        for k, d in enumerate(datasets):
            vals = [ratio(*data[s][m][d]) for m in ms]
            xpos = x - 0.4 + bw * (k + 0.5)
            bars = ax.bar(xpos, vals, bw, color=shades[k],
                          edgecolor="white", linewidth=0.4,
                          label=ds_labels[k], zorder=2)
            # flag losses (<1) with a red outline
            for bar, v in zip(bars, vals):
                if v < 1.0:
                    bar.set_edgecolor(LOSS); bar.set_linewidth(0.8)
        ax.axhline(1.0, color="#eeeeee", lw=0.5, zorder=1)
        if logscale:
            ax.set_yscale("log")
            ax.set_ylim(min(0.7, vmin * 0.8), vmax * 1.5)
            ax.yaxis.set_major_locator(mticker.LogLocator(base=10, subs=(1.0,)))
            ax.yaxis.set_major_formatter(mticker.FuncFormatter(
                lambda v, _: ("%g" % v)))
            ax.yaxis.set_minor_locator(mticker.NullLocator())
            ax.yaxis.set_minor_formatter(mticker.NullFormatter())
        else:
            ax.set_ylim(0, vmax * 1.15)
        ax.set_xticks(x)
        ax.set_xticklabels([short(m) for m in ms], rotation=0, fontsize=7.5)
        ax.set_title(STAGE_SHORT[s], fontsize=8.5, fontweight="bold", pad=4)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_zorder(5)
        ax.spines["left"].set_zorder(5)
        ax.tick_params(axis="both", labelsize=7, length=2)
        ax.margins(x=0.08)
        if j == 0:
            ax.set_ylabel("Relative ratio (×)", fontsize=8)
        ax.grid(axis="y", color="#eeeeee", lw=0.5, zorder=0)

    # Legend lives in a reserved top strip so panel titles never collide.
    fig.subplots_adjust(left=0.072, right=0.985, top=0.82, bottom=0.11)
    proxies = [mpatches.Patch(facecolor=shades[k], edgecolor="white", label=ds_labels[k])
               for k in range(len(datasets))]
    fig.legend(handles=proxies, loc="upper center", ncol=len(datasets),
               frameon=False, fontsize=8, bbox_to_anchor=(0.5, 1.005),
               handlelength=1.1, columnspacing=1.6)
    fig.savefig(os.path.join(OUT, fname + ".png"), dpi=300)
    fig.savefig(os.path.join(OUT, fname + ".svg"))
    plt.close(fig)
    return dict(vmin=vmin, vmax=vmax)


DS4 = ["min", "mid", "max", "ultra"]
DS3 = ["min", "mid", "max"]
LAB4 = ["Min", "Mid", "Max", "Ultra"]
LAB3 = ["Min", "Mid", "Max"]

sb = composite(B_TIME, STAGE_ORDER, DS3, LAB3, SHADES3,
               "fig_expb_speedup", logscale=True)
# Experiment (a): time speedup MassFlow vs Cardinal
sa_t = composite(A_TIME, STAGE_ORDER, DS4, LAB4, SHADES4,
                 "fig_expa_time", logscale=True)
# Experiment (a): memory ratio MassFlow vs Cardinal
sa_m = composite(A_MEM, STAGE_ORDER, DS4, LAB4, SHADES4,
                 "fig_expa_memory", logscale=True)

# ---- statistics -------------------------------------------------------------
def stats_block(data, stages, datasets, label):
    rows = []
    allr = []
    for s in stages:
        for m in data[s]:
            for d in datasets:
                a, b = data[s][m][d]
                r = ratio(a, b)
                rows.append((s, m, d, a, b, r))
                allr.append(r)
    allr = np.array(allr)
    print(f"\n===== {label} =====")
    print(f"  n={len(allr)}  min={allr.min():.2f}x  median={np.median(allr):.2f}x  "
          f"mean={allr.mean():.2f}x  max={allr.max():.2f}x")
    print(f"  fraction >=1x : {(allr>=1).mean()*100:.0f}%")
    # extremes
    rows_sorted = sorted(rows, key=lambda r: r[5])
    print("  lowest 3:", [(r[0], r[1], r[2], round(r[5], 2)) for r in rows_sorted[:3]])
    print("  highest 3:", [(r[0], r[1], r[2], round(r[5], 2)) for r in rows_sorted[-3:]])
    return rows


rb = stats_block(B_TIME, STAGE_ORDER, DS3, "Experiment (a) Numba/Flat speedup over NumPy/Batch")
ra_t = stats_block(A_TIME, STAGE_ORDER, DS4, "Experiment (b) time speedup MassFlow over Cardinal")
ra_m = stats_block(A_MEM, STAGE_ORDER, DS4, "Experiment (b) memory ratio Cardinal/MassFlow")

# ---- absolute framework table (MassFlow flat = 2nd element of pipeline data) --
print("\n===== Table 2: ProjectNAME (flat) absolute time(s) / peak mem(MiB) =====")
print("stage | method | " + " | ".join(f"{d}_t/{d}_m" for d in DS4))
table2 = {}
for s in STAGE_ORDER:
    for m in A_TIME[s]:
        cells = []
        rowdata = {}
        for d in DS4:
            t = A_TIME[s][m][d][1]
            mem = A_MEM[s][m][d][1]
            rowdata[d] = (round(t, 2), round(mem))
            cells.append(f"{t:6.2f}/{mem:6.0f}")
        table2[f"{s}|{m}"] = rowdata
        print(f"{STAGE_SHORT[s]:13s} | {short(m):8s} | " + " | ".join(cells))

with open(os.path.join(OUT, "stats.json"), "w", encoding="utf-8") as f:
    json.dump({"table2": table2}, f, ensure_ascii=False, indent=1)
print("\nSaved figures to", OUT)
print("files:", sorted(os.listdir(OUT)))
