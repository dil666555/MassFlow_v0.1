"""Parallel scalability benchmark figure for the paper.

Generates a publication-quality composite figure showing how each MassFlow
preprocessing stage scales with increasing thread count (1–32).

Layout:
  - Top row (a–e): absolute wall-clock time (log–log) per stage
  - Bottom row (f–j): parallel speedup relative to single-thread (log scale)

The figure follows Analytical Chemistry illustration conventions:
  - Arial font, compact 7 pt base size
  - Clean two-spine axes (left + bottom only)
  - Muted blue sequential palette, consistent with the project's other figures
  - Ideal-scaling reference in grey dashed line
  - Direct label of max speedup at 32 threads
  - SVG (editable text) + PDF (Type-42) + PNG (600 dpi) exports

Data source: tests/parallel_outcome.py
Run:  python plot_parallel.py
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
import matplotlib.ticker as mticker
import numpy as np

from tests.parallel_outcome import PARALLEL_DATA, THREADS

# ── Output ───────────────────────────────────────────────────────────────────
OUT = os.path.join(ROOT, "figures")
os.makedirs(OUT, exist_ok=True)

# ── Style (Analytical Chemistry / Nature-compatible) ─────────────────────────
plt.rcParams.update({
    "font.family":       "Arial",
    "font.size":         7,
    "axes.linewidth":    0.7,
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "legend.frameon":    False,
    "pdf.fonttype":      42,
    "svg.fonttype":      "none",
    "mathtext.default":  "regular",
})

# ── Colour palette ───────────────────────────────────────────────────────────
# Five distinct hues — one per stage, easy to distinguish in print & screen.
STAGE_COLORS = {
    "Peak Picking":        "#0072B2",   # blue
    "Normalization":       "#D55E00",   # vermillion
    "Noise Reduction":     "#009E73",   # bluish green
    "Baseline Correction": "#E69F00",   # orange
    "Peak Alignment":      "#CC79A7",   # reddish purple
}
IDEAL_COLOR = "#B0B0B0"
FILL_ALPHA = 0.08

# ── Stage ordering & short names ─────────────────────────────────────────────
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
    "rms_numba":    "RMS (Numba)",
    "savgol_numba": "SG (Numba)",
    "snip_numba":   "SNIP (Numba)",
    "min-ppm":      "Min-PPM",
}

# ── Panel labels ─────────────────────────────────────────────────────────────
PANEL_LABELS_TOP    = list("abcde")
PANEL_LABELS_BOTTOM = list("fghij")


# ═══════════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════════

def _extract_series(stage_name):
    """Return (method_display_name, threads_array, times_array) for a stage."""
    stage_data = PARALLEL_DATA[stage_name]
    method_key = list(stage_data.keys())[0]
    time_dict = stage_data[method_key]
    threads = np.array(sorted(time_dict.keys()))
    times = np.array([time_dict[t] for t in threads])
    return METHOD_DISPLAY.get(method_key, method_key), threads, times


def _add_panel_label(ax, label):
    """Place a bold lowercase panel label (a, b, …) in the top-left corner."""
    ax.text(
        -0.22, 1.10, label,
        transform=ax.transAxes,
        fontsize=9, fontweight="bold",
        ha="left", va="bottom",
    )


def _format_thread_tick(v, _pos):
    """Format thread-count ticks as clean integers."""
    iv = int(v)
    return f"{iv}" if v == iv else f"{v:g}"


# ═══════════════════════════════════════════════════════════════════════════════
# Figure construction
# ═══════════════════════════════════════════════════════════════════════════════

def make_parallel_figure():
    """Build and return the composite 2×5 parallel-scalability figure."""

    fig, axes = plt.subplots(
        2, 5,
        figsize=(7.2, 3.6),
        gridspec_kw={"hspace": 0.58, "wspace": 0.45},
    )

    for col, stage in enumerate(STAGE_ORDER):
        method_name, threads, times = _extract_series(stage)
        color = STAGE_COLORS[stage]

        # Derived series
        t1 = times[0]
        speedup = t1 / times
        ideal_speedup = threads.astype(float) / threads[0]

        # ── Top row: absolute time (log–log) ─────────────────────────────
        ax_t = axes[0, col]
        ax_t.plot(
            threads, times,
            color=color, marker="o", markersize=4,
            linewidth=1.4, markeredgecolor="white", markeredgewidth=0.5,
            zorder=3,
        )
        # Ideal scaling reference: t₁ / n
        ideal_time = t1 / ideal_speedup
        ax_t.plot(
            threads, ideal_time,
            color=IDEAL_COLOR, linewidth=0.8, linestyle="--",
            zorder=2,
        )
        ax_t.set_xscale("log", base=2)
        ax_t.set_yscale("log")

        # x ticks
        ax_t.set_xticks(threads)
        ax_t.xaxis.set_major_formatter(mticker.FuncFormatter(_format_thread_tick))
        ax_t.xaxis.set_minor_locator(mticker.NullLocator())
        ax_t.yaxis.set_minor_locator(mticker.NullLocator())

        ax_t.set_title(STAGE_SHORT[stage], fontsize=7.5, fontweight="bold", pad=5)
        if col == 0:
            ax_t.set_ylabel("Time (s)", fontsize=7)
        ax_t.tick_params(axis="both", labelsize=6, length=2.2, pad=2)
        ax_t.grid(axis="y", color="#ECECEC", linewidth=0.5, zorder=0)
        _add_panel_label(ax_t, PANEL_LABELS_TOP[col])

        # Direct label: method name near the first data point
        ax_t.annotate(
            method_name,
            xy=(threads[0], times[0]),
            xytext=(6, -2), textcoords="offset points",
            fontsize=5.5, color=color, fontweight="bold",
            va="top", ha="left",
        )

        # ── Bottom row: speedup (log scale) ──────────────────────────────
        ax_s = axes[1, col]
        ax_s.plot(
            threads, speedup,
            color=color, marker="s", markersize=3.5,
            linewidth=1.4, markeredgecolor="white", markeredgewidth=0.5,
            zorder=3,
        )
        ax_s.plot(
            threads, ideal_speedup,
            color=IDEAL_COLOR, linewidth=0.8, linestyle="--",
            zorder=2,
        )
        # Shade the gap between measured and ideal
        ax_s.fill_between(
            threads, speedup, ideal_speedup,
            color=color, alpha=FILL_ALPHA, zorder=1,
        )
        ax_s.set_xscale("log", base=2)
        ax_s.set_yscale("log", base=2)
        ax_s.set_xticks(threads)
        ax_s.xaxis.set_major_formatter(mticker.FuncFormatter(_format_thread_tick))
        ax_s.xaxis.set_minor_locator(mticker.NullLocator())
        # y ticks: powers of 2
        yticks_s = [1, 2, 4, 8, 16, 32]
        ax_s.set_yticks(yticks_s)
        ax_s.yaxis.set_major_formatter(mticker.FuncFormatter(
            lambda v, _: f"{int(v)}" if v >= 1 and v == int(v) else f"{v:g}"
        ))
        ax_s.yaxis.set_minor_locator(mticker.NullLocator())
        ax_s.set_ylim(0.8, 40)

        if col == 0:
            ax_s.set_ylabel("Speedup (×)", fontsize=7)
        ax_s.set_xlabel("Threads", fontsize=6.5)
        ax_s.tick_params(axis="both", labelsize=6, length=2.2, pad=2)
        ax_s.grid(axis="y", color="#ECECEC", linewidth=0.5, zorder=0)
        _add_panel_label(ax_s, PANEL_LABELS_BOTTOM[col])

        # Annotate the achieved speedup at max threads
        max_speedup = speedup[-1]
        ax_s.annotate(
            f"{max_speedup:.1f}×",
            xy=(threads[-1], max_speedup),
            xytext=(-4, 6), textcoords="offset points",
            fontsize=5.5, color=color, fontweight="bold",
            ha="right", va="bottom",
        )

    # ── Shared legend (top-centre) ───────────────────────────────────────────
    import matplotlib.lines as mlines
    legend_handles = [
        mlines.Line2D([], [], color="#444444", marker="o", markersize=4,
                       linewidth=1.4, markeredgecolor="white",
                       markeredgewidth=0.5, label="Measured"),
        mlines.Line2D([], [], color=IDEAL_COLOR, linewidth=0.8,
                       linestyle="--", label="Ideal scaling"),
    ]
    fig.legend(
        handles=legend_handles,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.02),
        ncol=2,
        fontsize=6.5,
        handlelength=1.8,
        handletextpad=0.4,
        columnspacing=1.5,
    )
    fig.subplots_adjust(left=0.08, right=0.98, top=0.87, bottom=0.13)
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# Save helpers
# ═══════════════════════════════════════════════════════════════════════════════

def save_figure(fig, output_dir=OUT, stem="fig_parallel_scaling"):
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


def plot_parallel():
    """Public entry point: build, save with-text and notext versions, close."""
    fig = make_parallel_figure()
    save_figure(fig)
    _hide_all_text(fig)
    save_figure(fig, stem="fig_parallel_scaling_notext")
    plt.close(fig)
    print("Saved parallel-scaling figure to", OUT)


# ═══════════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    plot_parallel()
