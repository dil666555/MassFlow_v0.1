"""Analytical Chemistry-style composite performance figure.

This script reuses the three ratio plots from plot.py and arranges them as a
single multi-panel paper figure:
  a) internal pure-compute speedup
  b) external runtime ratio against Cardinal
  c) external peak-memory ratio against Cardinal
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
import matplotlib.patches as mpatches
import matplotlib.text as mtext
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

from tests.python_outcome import TIME_DATA as A_TIME
from tests.pipeline_outcome import MEMORY_DATA as B_MEM
from tests.pipeline_outcome import TIME_DATA as B_TIME

OUT = os.path.join(ROOT, "figures")


# ---------------------------------------------------------------------------
# Figure constants
# ---------------------------------------------------------------------------

STAGE_ORDER = [
    "Baseline Correction",
    "Normalization",
    "Peak Alignment",
    "Noise Reduction",
    "Peak Picking",
]
STAGE_SHORT = {
    "Baseline Correction": "Baseline",
    "Normalization": "Normalization",
    "Peak Alignment": "Alignment",
    "Noise Reduction": "Denoising",
    "Peak Picking": "Peak picking",
}
STAGE_METHODS = {
    "Baseline Correction": ["locmin", "snip"],
    "Normalization": ["TIC", "RMS", "Reference"],
    "Peak Alignment": ["Default"],
    "Noise Reduction": ["MA", "Gaussian", "Savitzky–Golay"],
    "Peak Picking": ["Quantile", "Diff", "SD", "MAD"],
}
DATASETS = ["min", "mid", "max", "ultra"]
DATASET_LABELS = ["Min", "Mid", "Max", "Ultra"]
DATASET_COLORS = ["#CFE8F7", "#8FCDEC", "#4FA8DC", "#2E73B0"]
LOSS_EDGE = "#CC4C4C"
GRID_COLOR = "#E8E8E8"

METHOD_SHORT = {
    "locmin": "LocMin",
    "snip": "SNIP",
    "MA": "MA",
    "Gaussian": "Gauss",
    "TIC": "TIC",
    "RMS": "RMS",
    "Reference": "Ref",
    "Quantile": "Quantile",
    "Diff": "Diff",
    "SD": "SD",
    "MAD": "MAD",
    "Default": "Default",
}


def configure_style():
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
        "font.size": 7,
        "axes.linewidth": 0.7,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "xtick.major.width": 0.7,
        "ytick.major.width": 0.7,
        "xtick.major.size": 2.2,
        "ytick.major.size": 2.2,
        "legend.frameon": False,
        "pdf.fonttype": 42,
        "svg.fonttype": "none",
    })


# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------

def ratio(baseline, massflow):
    return baseline / massflow


def method_label(method):
    if method.startswith("Savitzky"):
        return "SG"
    return METHOD_SHORT.get(method, method)


def panel_values(data):
    values = []
    for stage in STAGE_ORDER:
        for method in data[stage]:
            for dataset in DATASETS:
                values.append(ratio(*data[stage][method][dataset]))
    return np.asarray(values, dtype=float)


def log_ylim(values):
    ymin = values.min() * 0.78
    ymax = values.max() * 1.45
    return min(0.7, ymin), ymax


def log_tick_formatter(value, _pos):
    if value >= 1:
        return f"{value:.0f}"
    return f"{value:.1f}"


# ---------------------------------------------------------------------------
# Drawing
# ---------------------------------------------------------------------------

def draw_ratio_panel(fig, outer_spec, data, label, title, ylabel):
    values = panel_values(data)
    ymin, ymax = log_ylim(values)
    width_ratios = [len(STAGE_METHODS[stage]) for stage in STAGE_ORDER]
    inner = outer_spec.subgridspec(
        1,
        len(STAGE_ORDER),
        width_ratios=width_ratios,
        wspace=0.22,
    )
    axes = []

    for col, stage in enumerate(STAGE_ORDER):
        ax = fig.add_subplot(inner[0, col])
        axes.append(ax)
        methods = STAGE_METHODS[stage]
        x = np.arange(len(methods))
        bar_width = 0.78 / len(DATASETS)

        for idx, dataset in enumerate(DATASETS):
            xpos = []
            heights = []
            for method_idx, method in enumerate(methods):
                if method not in data[stage]:
                    continue
                xpos.append(method_idx - 0.39 + bar_width * (idx + 0.5))
                heights.append(ratio(*data[stage][method][dataset]))
            bars = ax.bar(
                xpos,
                heights,
                width=bar_width,
                color=DATASET_COLORS[idx],
                edgecolor="white",
                linewidth=0.35,
                zorder=2,
            )
            for bar, height in zip(bars, heights):
                if height < 1.0:
                    bar.set_edgecolor(LOSS_EDGE)
                    bar.set_linewidth(0.85)

        ax.axhline(1.0, color="#B5B5B5", lw=0.55, ls=(0, (2, 2)), zorder=1)
        ax.set_yscale("log")
        ax.set_ylim(ymin, ymax)
        ax.yaxis.set_major_locator(mticker.FixedLocator([1, 10, 100]))
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(log_tick_formatter))
        ax.yaxis.set_minor_locator(mticker.NullLocator())
        ax.yaxis.set_minor_formatter(mticker.NullFormatter())
        ax.set_xlim(-0.55, len(methods) - 0.45)
        ax.set_xticks(x)
        ax.set_xticklabels(
            [method_label(method) for method in methods],
            rotation=0,
            ha="center",
            fontsize=5.8,
        )
        for tick, tick_label, method in zip(ax.xaxis.get_major_ticks(), ax.get_xticklabels(), methods):
            if method not in data[stage]:
                tick.tick1line.set_visible(False)
                tick.tick2line.set_visible(False)
                tick_label.set_visible(False)
        ax.set_title(STAGE_SHORT[stage], fontsize=6.6, pad=2.5)
        ax.grid(axis="y", color=GRID_COLOR, lw=0.45, zorder=0)
        ax.tick_params(axis="both", labelsize=5.8, pad=1.6)

        if col == 0:
            ax.set_ylabel(ylabel, fontsize=6.6)
        else:
            ax.set_yticklabels([])
            ax.tick_params(axis="y", length=0)

    first = axes[0]
    first.text(
        -0.54,
        1.20,
        label,
        transform=first.transAxes,
        fontsize=9,
        fontweight="bold",
        va="top",
        ha="left",
        clip_on=False,
    )
    first.text(
        -0.29,
        1.20,
        title,
        transform=first.transAxes,
        fontsize=7.4,
        fontweight="bold",
        va="top",
        ha="left",
        clip_on=False,
    )
    return axes


def make_figure():
    configure_style()
    fig = plt.figure(figsize=(7.2, 6.6))
    outer = fig.add_gridspec(
        3,
        1,
        left=0.078,
        right=0.99,
        top=0.91,
        bottom=0.082,
        hspace=0.53,
    )

    draw_ratio_panel(
        fig,
        outer[0, 0],
        A_TIME,
        "a)",
        "Internal benchmark: NumPy batch / Numba flat",
        "Speedup ratio (x)",
    )
    draw_ratio_panel(
        fig,
        outer[1, 0],
        B_TIME,
        "b)",
        "External benchmark: Cardinal / MassFlow runtime",
        "Runtime ratio (x)",
    )
    draw_ratio_panel(
        fig,
        outer[2, 0],
        B_MEM,
        "c)",
        "External benchmark: Cardinal / MassFlow peak memory",
        "Memory ratio (x)",
    )

    legend_handles = [
        mpatches.Patch(facecolor=color, edgecolor="white", label=label)
        for color, label in zip(DATASET_COLORS, DATASET_LABELS)
    ]
    fig.legend(
        handles=legend_handles,
        labels=DATASET_LABELS,
        loc="upper center",
        bbox_to_anchor=(0.56, 0.985),
        ncol=len(DATASETS),
        handlelength=1.0,
        handletextpad=0.35,
        columnspacing=1.15,
        fontsize=6.8,
    )
    return fig


def save_figure(fig, output_dir=OUT, stem="fig_1_combined"):
    os.makedirs(output_dir, exist_ok=True)
    for ext, kwargs in [
        ("svg", {}),
        ("pdf", {}),
        ("png", {"dpi": 600}),
    ]:
        fig.savefig(os.path.join(output_dir, f"{stem}.{ext}"), bbox_inches="tight", **kwargs)


def make_text_background_colored(fig, color="white"):
    for text in fig.findobj(mtext.Text):
        text.set_color(color)


def main():
    fig = make_figure()
    save_figure(fig)
    make_text_background_colored(fig)
    save_figure(fig, stem="fig_1_combined_notext")
    plt.close(fig)
    print("Saved composite figure to", OUT)


if __name__ == "__main__":
    main()
