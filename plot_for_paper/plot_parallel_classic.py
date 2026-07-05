"""Parallel scalability benchmark figure (classic two-panel layout).

Left panel  (a): absolute execution time vs. thread count (log–log)
Right panel (b): parallel speedup vs. thread count (log₂–log₂)

All five preprocessing stages are overlaid with distinct markers.
The ideal linear-scaling reference is shown as a grey dashed line.

Style: Analytical Chemistry / Nature — Arial, two-spine, muted blue family.
Exports: SVG (editable text), PDF (Type-42), PNG (600 dpi).

Data source: tests/parallel_outcome.py
Run:  python plot_parallel_classic.py
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(ROOT)
sys.path.insert(0, PKG)

os.environ.setdefault(
    "MPLCONFIGDIR",
    os.path.join(tempfile.gettempdir(), "massflow-essay-matplotlib-cache"),
)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.ticker as mticker
import numpy as np

from tests.parallel_outcome import PARALLEL_DATA, THREADS

# ── Output directory ─────────────────────────────────────────────────────────
OUT = os.path.join(ROOT, "figures")
os.makedirs(OUT, exist_ok=True)

# ── Style ────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family":       "Arial",
    "font.size":         7.5,
    "axes.linewidth":    0.65,
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "legend.frameon":    False,
    "pdf.fonttype":      42,
    "svg.fonttype":      "none",
    "mathtext.default":  "regular",
})

# ── Palette & markers ────────────────────────────────────────────────────────
# Five distinct hues — one per stage, easy to distinguish in print & screen.
COLORS = ["#0072B2", "#D55E00", "#009E73", "#E69F00", "#CC79A7"]
MARKERS = ["o", "s", "D", "^", "v"]
IDEAL_COLOR = "#C0C0C0"

# ── Stage definitions ────────────────────────────────────────────────────────
STAGE_ORDER = [
    "Peak Picking",
    "Normalization",
    "Noise Reduction",
    "Baseline Correction",
    "Peak Alignment",
]
STAGE_SHORT = {
    "Peak Picking":        "Peak Picking",
    "Normalization":       "Normalization",
    "Noise Reduction":     "Noise Reduction",
    "Baseline Correction": "Baseline Corr.",
    "Peak Alignment":      "Peak Alignment",
}
METHOD_DISPLAY = {
    "diff":         "Diff",
    "rms_numba":    "RMS",
    "savgol_numba": "Savitzky–Golay",
    "snip_numba":   "SNIP",
    "min-ppm":      "Min-PPM",
}


# ── Helpers ──────────────────────────────────────────────────────────────────

def _extract(stage):
    """Return (method_display_name, threads_array, times_array)."""
    data = PARALLEL_DATA[stage]
    key = list(data.keys())[0]
    td = data[key]
    th = np.array(sorted(td.keys()))
    tm = np.array([td[t] for t in th])
    return METHOD_DISPLAY.get(key, key), th, tm


# ── Figure construction ─────────────────────────────────────────────────────

def make_figure():
    """Build the two-panel parallel-scaling figure and return the Figure."""

    fig, (ax_l, ax_r) = plt.subplots(
        1, 2,
        figsize=(7.0, 3.0),
        gridspec_kw={"wspace": 0.38},
    )

    threads_arr = np.array(THREADS, dtype=float)
    ideal_sp = threads_arr / threads_arr[0]

    # ── Draw each stage ──────────────────────────────────────────────────
    for i, stage in enumerate(STAGE_ORDER):
        _mn, th, tm = _extract(stage)
        sp = tm[0] / tm

        common = dict(
            color=COLORS[i], marker=MARKERS[i], markersize=4,
            linewidth=1.2, markeredgecolor="white", markeredgewidth=0.4,
            zorder=3, label=STAGE_SHORT[stage],
        )

        # Left: absolute time
        ax_l.plot(th, tm, **common)

        # Right: speedup
        ax_r.plot(th, sp, **common)

    # ── Ideal reference (right panel only) ───────────────────────────────
    ax_r.plot(threads_arr, ideal_sp,
              color=IDEAL_COLOR, lw=1.0, ls="--", zorder=1, label="Ideal")

    # ── Axis formatting ──────────────────────────────────────────────────
    for ax in (ax_l, ax_r):
        ax.set_xscale("log", base=2)
        ax.set_xticks(THREADS)
        ax.xaxis.set_major_formatter(mticker.ScalarFormatter())
        ax.xaxis.set_minor_locator(mticker.NullLocator())
        ax.set_xlabel("Threads", fontsize=7.5)
        ax.tick_params(axis="both", labelsize=6.5, length=2.2, pad=2)
        ax.grid(axis="both", color="#F0F0F0", lw=0.4, zorder=0)

    # Left: log y
    ax_l.set_yscale("log")
    ax_l.yaxis.set_minor_locator(mticker.NullLocator())
    ax_l.set_ylabel("Time (s)", fontsize=7.5)
    ax_l.set_title("Execution time", fontsize=8.5, fontweight="bold", pad=6)

    # Right: log₂ y with clean ticks
    ax_r.set_yscale("log", base=2)
    ax_r.set_yticks([1, 2, 4, 8, 16, 32])
    ax_r.yaxis.set_major_formatter(mticker.ScalarFormatter())
    ax_r.yaxis.set_minor_locator(mticker.NullLocator())
    ax_r.set_ylim(0.8, 40)
    ax_r.set_ylabel("Speedup (×)", fontsize=7.5)
    ax_r.set_title("Parallel speedup", fontsize=8.5, fontweight="bold", pad=6)

    # ── Panel labels (a, b) ──────────────────────────────────────────────
    for ax, label in [(ax_l, "a"), (ax_r, "b")]:
        ax.text(-0.16, 1.10, label, transform=ax.transAxes,
                fontsize=10, fontweight="bold", ha="left", va="bottom")

    # ── Legend in right panel ────────────────────────────────────────────
    ax_r.legend(fontsize=5.5, loc="upper left", handlelength=1.4,
                labelspacing=0.32, borderpad=0.5)

    fig.subplots_adjust(left=0.10, right=0.97, top=0.85, bottom=0.17)
    return fig


# ── Save & entry point ──────────────────────────────────────────────────────

def save_figure(fig, output_dir=OUT, stem="fig_parallel_classic"):
    """Save to SVG (primary), PDF, and PNG (600 dpi)."""
    os.makedirs(output_dir, exist_ok=True)
    for ext, kwargs in [
        ("svg", {}),
        ("png", {"dpi": 600}),
    ]:
        fig.savefig(
            os.path.join(output_dir, f"{stem}.{ext}"),
            bbox_inches="tight",
            **kwargs,
        )


def _hide_all_text(fig):
    """Set every Text object in the figure to transparent (invisible)."""
    import matplotlib.text as mtext
    for obj in fig.findobj(mtext.Text):
        obj.set_color("none")


def plot_parallel_classic():
    """Public entry point: build, save with-text and notext versions, close."""
    fig = make_figure()
    save_figure(fig)
    _hide_all_text(fig)
    save_figure(fig, stem="fig_parallel_classic_notext")
    plt.close(fig)
    print("Saved parallel-classic figure to", OUT)


if __name__ == "__main__":
    plot_parallel_classic()
