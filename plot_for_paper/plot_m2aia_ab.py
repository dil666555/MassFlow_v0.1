"""Candidate paper panel for MassFlow vs pyM2aia AB-only benchmarks."""
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
import matplotlib.ticker as mticker
import numpy as np

from tests.compare_m2aia_outcome import TIME_DATA

OUT = os.path.join(ROOT, "figures")

DATASETS = ["min", "mid", "example", "original"]
DATASET_LABELS = ["Min", "Mid", "Example", "Original"]
DATASET_COLORS = ["#D8EEF7", "#9CD4E7", "#4EA3C8", "#1F5D8F"]
GRID_COLOR = "#E8E8E8"

STAGE_ORDER = ["Noise Reduction", "Normalization"]
STAGE_LABELS = {
    "Noise Reduction": "Denoising",
    "Normalization": "Normalization",
}
METHOD_ORDER = {
    "Noise Reduction": ["Gaussian", "Savitzky–Golay"],
    "Normalization": ["TIC", "RMS"],
}
METHOD_LABELS = {
    "Gaussian": "Gaussian",
    "Savitzky–Golay": "SG",
    "TIC": "TIC",
    "RMS": "RMS",
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


def ratio(baseline, massflow):
    return baseline / massflow


def collect_values(data=TIME_DATA):
    return np.array([
        ratio(*data[stage][method][dataset])
        for stage in STAGE_ORDER
        for method in METHOD_ORDER[stage]
        for dataset in DATASETS
    ])


def draw_m2aia_ab_panel(fig, outer_spec, data=TIME_DATA):
    """Draw a compact MassFlow-vs-pyM2aia runtime speedup panel."""
    values = collect_values(data)
    ymax = float(np.ceil(values.max() * 1.18 * 2) / 2)
    inner = outer_spec.subgridspec(
        1,
        len(STAGE_ORDER),
        width_ratios=[len(METHOD_ORDER[stage]) for stage in STAGE_ORDER],
        wspace=0.22,
    )
    axes = []

    for col, stage in enumerate(STAGE_ORDER):
        ax = fig.add_subplot(inner[0, col])
        axes.append(ax)
        methods = METHOD_ORDER[stage]
        x = np.arange(len(methods))
        bar_width = 0.78 / len(DATASETS)

        for idx, dataset in enumerate(DATASETS):
            heights = [ratio(*data[stage][method][dataset]) for method in methods]
            xpos = x - 0.39 + bar_width * (idx + 0.5)
            ax.bar(
                xpos,
                heights,
                width=bar_width,
                color=DATASET_COLORS[idx],
                edgecolor="white",
                linewidth=0.35,
                zorder=2,
            )

        ax.axhline(1.0, color="#B5B5B5", lw=0.55, ls=(0, (2, 2)), zorder=1)
        ax.set_ylim(0, ymax)
        ax.yaxis.set_major_locator(mticker.MultipleLocator(1.0))
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda value, _pos: f"{value:g}"))
        ax.set_xlim(-0.55, len(methods) - 0.45)
        ax.set_xticks(x)
        ax.set_xticklabels([METHOD_LABELS[method] for method in methods], fontsize=6.1)
        ax.set_title(STAGE_LABELS[stage], fontsize=6.8, pad=2.5)
        ax.grid(axis="y", color=GRID_COLOR, lw=0.45, zorder=0)
        ax.tick_params(axis="both", labelsize=5.9, pad=1.6)

        if col == 0:
            ax.set_ylabel("Runtime speedup (x)", fontsize=6.8)
        else:
            ax.set_yticklabels([])
            ax.tick_params(axis="y", length=0)

    return axes


def make_figure():
    configure_style()
    values = collect_values()
    fig = plt.figure(figsize=(4.9, 2.2))
    outer = fig.add_gridspec(
        1,
        1,
        left=0.09,
        right=0.99,
        top=0.54,
        bottom=0.18,
    )
    draw_m2aia_ab_panel(fig, outer[0, 0])
    fig.text(
        0.02,
        0.72,
        "c",
        fontsize=9,
        fontweight="bold",
        va="top",
        ha="left",
    )
    fig.text(
        0.085,
        0.72,
        "Python in-memory benchmark: pyM2aia / MassFlow runtime",
        fontsize=7.4,
        fontweight="bold",
        va="top",
        ha="left",
    )
    fig.text(
        0.085,
        0.64,
        f"All operations favor MassFlow ({values.min():.2f}-{values.max():.2f}x)",
        fontsize=6.2,
        color="#555555",
        va="top",
        ha="left",
    )
    legend_handles = [
        mpatches.Patch(facecolor=color, edgecolor="white", label=label)
        for color, label in zip(DATASET_COLORS, DATASET_LABELS)
    ]
    fig.legend(
        handles=legend_handles,
        loc="upper center",
        bbox_to_anchor=(0.63, 0.86),
        ncol=len(DATASETS),
        handlelength=1.0,
        handletextpad=0.35,
        columnspacing=1.0,
        fontsize=6.6,
    )
    return fig


def save_figure(fig, output_dir=OUT, stem="fig_m2aia_ab_candidate"):
    os.makedirs(output_dir, exist_ok=True)
    for ext, kwargs in [
        ("svg", {}),
        ("pdf", {}),
        ("png", {"dpi": 600}),
    ]:
        fig.savefig(os.path.join(output_dir, f"{stem}.{ext}"), bbox_inches="tight", **kwargs)


def main():
    fig = make_figure()
    save_figure(fig)
    plt.close(fig)
    print("Saved m2aia AB candidate figure to", OUT)


if __name__ == "__main__":
    main()
