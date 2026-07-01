"""Benchmark ratio dot plot for the paper figure.

Rows are preprocessing algorithms, columns are benchmark comparisons, and each
dot is one dataset size. Ratios are baseline / MassFlow, so values above 1x
favor MassFlow.
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
import matplotlib.pyplot as plt
import matplotlib.text as mtext
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
DATASETS = ["min", "mid", "max", "ultra"]
DATASET_LABELS = ["Min", "Mid", "Max", "Ultra"]
DATASET_COLORS = ["#C84EB4", "#95ED8F", "#37D4E6", "#EDEA17"]
DATASET_OFFSETS = [-0.24, -0.08, 0.08, 0.24]
PANEL_SPECS = [
    ("a)", "Internal compute", A_TIME),
    ("b)", "Cardinal / MassFlow time", B_TIME),
    ("c)", "Cardinal / MassFlow memory", B_MEM),
]
XTICKS = [1, 2, 5, 10, 50, 100]


def configure_style():
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
        "font.size": 7,
        "axes.linewidth": 0.7,
        "axes.spines.top": False,
        "axes.spines.right": False,
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


def row_layout():
    rows = []
    stage_centers = {}
    separators = []
    y = 0
    for stage in STAGE_ORDER:
        start = y
        for method in STAGE_METHODS[stage]:
            rows.append((stage, method, y))
            y += 1
        stage_centers[stage] = (start + y - 1) / 2
        separators.append(y - 0.5)
        y += 0.7
    return rows, stage_centers, separators[:-1]


def all_ratios():
    values = []
    for _, _, data in PANEL_SPECS:
        for stage in STAGE_ORDER:
            for method, dataset_values in data[stage].items():
                for dataset in DATASETS:
                    values.append(ratio(*dataset_values[dataset]))
    return np.asarray(values, dtype=float)


def x_limits():
    values = all_ratios()
    return max(0.65, values.min() * 0.75), values.max() * 1.25


def tick_label(value, _pos):
    if value >= 10:
        return f"{value:.0f}"
    return f"{value:g}"


# ---------------------------------------------------------------------------
# Drawing
# ---------------------------------------------------------------------------

def draw_panel(ax, data, rows, stage_centers, separators, title, panel_label, show_y):
    for stage, method, y in rows:
        if method not in data[stage]:
            continue
        for dataset, offset, color in zip(DATASETS, DATASET_OFFSETS, DATASET_COLORS):
            value = ratio(*data[stage][method][dataset])
            ax.scatter(
                value,
                y + offset,
                s=22,
                color=color,
                edgecolors="white",
                linewidths=0.35,
                zorder=3,
            )

    for sep in separators:
        ax.axhline(sep, color="#ECECEC", lw=0.6, zorder=0)
    ax.axvline(1, color="#9B9B9B", lw=0.75, ls=(0, (2, 2)), zorder=1)
    ax.set_xscale("log")
    ax.set_xlim(*x_limits())
    ax.xaxis.set_major_locator(mticker.FixedLocator(XTICKS))
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(tick_label))
    ax.xaxis.set_minor_locator(mticker.NullLocator())
    ax.grid(axis="x", color="#E9E9E9", lw=0.5, zorder=0)
    ax.tick_params(axis="both", labelsize=6.6, length=2.2, pad=2)
    ax.set_title(title, fontsize=7.4, fontweight="bold", pad=5)
    ax.text(
        -0.12,
        1.035,
        panel_label,
        transform=ax.transAxes,
        fontsize=9,
        fontweight="bold",
        ha="left",
        va="bottom",
    )
    ax.set_xlabel("Ratio (x)", fontsize=6.8)

    y_ticks = [y for _, _, y in rows]
    y_labels = [method_label(method) for _, method, _ in rows]
    ax.set_yticks(y_ticks)
    if show_y:
        ax.set_yticklabels(y_labels, fontsize=6.4)
        for stage, center in stage_centers.items():
            ax.text(
                -0.43,
                center,
                STAGE_SHORT[stage],
                transform=ax.get_yaxis_transform(),
                fontsize=6.5,
                fontweight="bold",
                ha="right",
                va="center",
            )
    else:
        ax.tick_params(axis="y", length=0, labelleft=False)


def make_figure():
    configure_style()
    rows, stage_centers, separators = row_layout()
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 4.8), sharey=True)

    max_y = rows[-1][2] + 0.6
    for ax, (panel_label, title, data), show_y in zip(axes, PANEL_SPECS, [True, False, False]):
        draw_panel(ax, data, rows, stage_centers, separators, title, panel_label, show_y)
        ax.set_ylim(max_y, -0.8)

    handles = [
        mpatches.Patch(facecolor=color, edgecolor="white", label=label)
        for color, label in zip(DATASET_COLORS, DATASET_LABELS)
    ]
    fig.legend(
        handles=handles,
        loc="upper center",
        bbox_to_anchor=(0.55, 1.0),
        ncol=len(DATASETS),
        handlelength=1.0,
        handletextpad=0.35,
        columnspacing=1.2,
        fontsize=6.8,
    )
    fig.subplots_adjust(left=0.19, right=0.99, top=0.91, bottom=0.09, wspace=0.22)
    return fig


def save_figure(fig, output_dir=OUT, stem="fig_benchmark_dot"):
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
    save_figure(fig, stem="fig_benchmark_dot_notext")
    plt.close(fig)
    print("Saved dot plot figure to", OUT)


if __name__ == "__main__":
    main()
