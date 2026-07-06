"""Paper-ready composite MassFlow benchmark figure.

Generates one five-panel figure:
  a) internal implementation speedup
  b) Cardinal full-pipeline runtime ratio
  c) Cardinal full-pipeline peak-memory ratio
  d) pyM2aia in-memory preprocessing runtime ratio
  e) multithreading scalability
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
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
import matplotlib.text as mtext
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

from tests.compare_m2aia_outcome import TIME_DATA as M2AIA_TIME
from tests.parallel_outcome import PARALLEL_DATA, THREADS
from tests.pipeline_outcome import MEMORY_DATA as CARDINAL_MEM
from tests.pipeline_outcome import TIME_DATA as CARDINAL_TIME
from tests.python_outcome import TIME_DATA as INTERNAL_TIME

OUT = os.path.join(ROOT, "figures")


# ---------------------------------------------------------------------------
# Shared figure constants
# ---------------------------------------------------------------------------

STAGE_ORDER = [
    "Normalization",
    "Noise Reduction",
    "Baseline Correction",
    "Peak Alignment",
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
    "Noise Reduction": ["Gaussian", "Savitzky–Golay", "MA"],
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

CARDINAL_DATASETS = ["min", "mid", "max", "ultra"]
CARDINAL_DATASET_LABELS = ["Min", "Mid", "Max", "Ultra"]
M2AIA_DATASETS = ["min", "mid", "example", "original"]
M2AIA_DATASET_LABELS = ["Min", "Mid", "Example", "Original"]
DATASET_COLORS = ["#D8EEF7", "#9CD4E7", "#4EA3C8", "#1F5D8F"]

GRID_COLOR = "#E8E8E8"
LOSS_EDGE = "#CC4C4C"
IDEAL_COLOR = "#B8B8B8"
METHOD_LABEL_SIZE = 8.3
TICK_LABEL_SIZE = 7.2
AXIS_LABEL_SIZE = 8.2
STAGE_TITLE_SIZE = 9.5
PANEL_LABEL_SIZE = 11.0
LEGEND_LABEL_SIZE = 8.1
PARALLEL_LEGEND_SIZE = 6.0
ROW_LABEL_X = 0.018
ROW_LABEL_Y_OFFSET = 0.028

PARALLEL_STAGE_ORDER = [
    "Peak Picking",
    "Normalization",
    "Noise Reduction",
    "Baseline Correction",
    "Peak Alignment",
]
PARALLEL_STAGE_SHORT = {
    "Peak Picking": "Peak picking",
    "Normalization": "Normalization",
    "Noise Reduction": "Denoising",
    "Baseline Correction": "Baseline",
    "Peak Alignment": "Alignment",
}
PARALLEL_COLORS = ["#2B6C9B", "#CC6B49", "#3B8F72", "#D89C3A", "#A06AA5"]
PARALLEL_MARKERS = ["o", "s", "D", "^", "v"]

M2AIA_STAGE_ORDER = ["Noise Reduction", "Normalization"]
M2AIA_STAGE_SHORT = {
    "Noise Reduction": "Denoising",
    "Normalization": "Normalization",
}
M2AIA_METHODS = {
    "Noise Reduction": ["Gaussian", "Savitzky–Golay"],
    "Normalization": ["TIC", "RMS"],
}


def configure_style():
    plt.rcParams.update({
        "font.family": "Arial",
        "font.sans-serif": ["Arial"],
        "font.size": 8,
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
# Shared helpers
# ---------------------------------------------------------------------------

def ratio(baseline, massflow):
    return baseline / massflow


def method_label(method):
    if method.startswith("Savitzky"):
        return "SG"
    return METHOD_SHORT.get(method, method)


def add_panel_label(ax, label, x=-0.18, y=1.12):
    ax.text(
        x,
        y,
        label,
        transform=ax.transAxes,
        fontsize=PANEL_LABEL_SIZE,
        fontweight="bold",
        ha="left",
        va="top",
        clip_on=False,
    )


def add_row_panel_label(ax, label):
    bbox = ax.get_position()
    ax.figure.text(
        ROW_LABEL_X,
        bbox.y1 + ROW_LABEL_Y_OFFSET,
        label,
        fontsize=PANEL_LABEL_SIZE,
        fontweight="bold",
        ha="left",
        va="top",
    )


def ratio_values(data, stages, stage_methods, datasets):
    return np.array([
        ratio(*data[stage][method][dataset])
        for stage in stages
        for method in stage_methods[stage]
        if method in data[stage]
        for dataset in datasets
    ], dtype=float)


def log_tick_formatter(value, _pos):
    if value >= 1:
        return f"{value:.0f}"
    return f"{value:.1f}"


def save_figure(fig, stem, output_dir=OUT):
    os.makedirs(output_dir, exist_ok=True)
    for ext, kwargs in [
        ("svg", {}),
        ("pdf", {}),
        ("png", {"dpi": 600}),
    ]:
        fig.savefig(os.path.join(output_dir, f"{stem}.{ext}"), bbox_inches="tight", **kwargs)


def hide_all_text(fig):
    for text in fig.findobj(mtext.Text):
        text.set_color("none")


# ---------------------------------------------------------------------------
# Ratio bar panels
# ---------------------------------------------------------------------------

def draw_stage_ratio_panel(
    fig,
    outer_spec,
    data,
    datasets,
    panel_label,
    ylabel,
    stages=STAGE_ORDER,
    stage_methods=STAGE_METHODS,
    hide_missing_labels=True,
):
    values = ratio_values(data, stages, stage_methods, datasets)
    ymin = min(0.7, values.min() * 0.78)
    ymax = values.max() * 1.45
    inner = outer_spec.subgridspec(
        1,
        len(stages),
        width_ratios=[len(stage_methods[stage]) for stage in stages],
        wspace=0.22,
    )
    axes = []

    for col, stage in enumerate(stages):
        ax = fig.add_subplot(inner[0, col])
        axes.append(ax)
        methods = stage_methods[stage]
        x = np.arange(len(methods))
        bar_width = 0.78 / len(datasets)

        for idx, dataset in enumerate(datasets):
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
        ax.yaxis.set_major_locator(mticker.FixedLocator([1, 10, 100, 1000]))
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(log_tick_formatter))
        ax.yaxis.set_minor_locator(mticker.NullLocator())
        ax.yaxis.set_minor_formatter(mticker.NullFormatter())
        ax.set_xlim(-0.55, len(methods) - 0.45)
        ax.set_xticks(x)
        ax.set_xticklabels([method_label(method) for method in methods], fontsize=METHOD_LABEL_SIZE)
        for tick, tick_label, method in zip(ax.xaxis.get_major_ticks(), ax.get_xticklabels(), methods):
            if hide_missing_labels and method not in data[stage]:
                tick.tick1line.set_visible(False)
                tick.tick2line.set_visible(False)
                tick_label.set_visible(False)
        ax.set_title(STAGE_SHORT.get(stage, stage), fontsize=STAGE_TITLE_SIZE, pad=2.5)
        ax.grid(axis="y", color=GRID_COLOR, lw=0.45, zorder=0)
        ax.tick_params(axis="x", labelsize=METHOD_LABEL_SIZE, pad=1.6)
        ax.tick_params(axis="y", labelsize=TICK_LABEL_SIZE, pad=1.6)

        if col == 0:
            ax.set_ylabel(ylabel, fontsize=AXIS_LABEL_SIZE)
        else:
            ax.set_yticklabels([])
            ax.tick_params(axis="y", length=0)

    add_row_panel_label(axes[0], panel_label)
    return axes


def draw_m2aia_panel(fig, outer_spec):
    stages = ["Normalization", "Noise Reduction"]
    stage_methods = {
        "Normalization": STAGE_METHODS["Normalization"],
        "Noise Reduction": STAGE_METHODS["Noise Reduction"],
    }
    values = ratio_values(M2AIA_TIME, M2AIA_STAGE_ORDER, M2AIA_METHODS, M2AIA_DATASETS)
    ymax = float(np.ceil(values.max() * 1.18 * 2) / 2)
    inner = outer_spec.subgridspec(
        1,
        len(stages),
        width_ratios=[len(stage_methods[stage]) for stage in stages],
        wspace=0.22,
    )
    axes = []

    for col, stage in enumerate(stages):
        ax = fig.add_subplot(inner[0, col])
        axes.append(ax)
        methods = stage_methods[stage]
        x = np.arange(len(methods))
        bar_width = 0.78 / len(M2AIA_DATASETS)

        for idx, dataset in enumerate(M2AIA_DATASETS):
            xpos = []
            heights = []
            for method_idx, method in enumerate(methods):
                if method not in M2AIA_TIME[stage]:
                    continue
                xpos.append(method_idx - 0.39 + bar_width * (idx + 0.5))
                heights.append(ratio(*M2AIA_TIME[stage][method][dataset]))
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
        ax.set_xticklabels([method_label(method) for method in methods], fontsize=METHOD_LABEL_SIZE)
        for tick, tick_label, method in zip(ax.xaxis.get_major_ticks(), ax.get_xticklabels(), methods):
            if method not in M2AIA_TIME[stage]:
                tick.tick1line.set_visible(False)
                tick.tick2line.set_visible(False)
                tick_label.set_visible(False)
        ax.set_title(STAGE_SHORT[stage], fontsize=STAGE_TITLE_SIZE, pad=2.5)
        ax.grid(axis="y", color=GRID_COLOR, lw=0.45, zorder=0)
        ax.tick_params(axis="x", labelsize=METHOD_LABEL_SIZE, pad=1.6)
        ax.tick_params(axis="y", labelsize=TICK_LABEL_SIZE, pad=1.6)

        if col == 0:
            ax.set_ylabel("Runtime ratio (x)", fontsize=AXIS_LABEL_SIZE)
        else:
            ax.set_yticklabels([])
            ax.tick_params(axis="y", length=0)

    add_row_panel_label(axes[0], "d")
    return axes


# ---------------------------------------------------------------------------
# Parallel scaling panels
# ---------------------------------------------------------------------------

def parallel_series(stage):
    stage_data = PARALLEL_DATA[stage]
    method_key = list(stage_data.keys())[0]
    time_by_thread = stage_data[method_key]
    threads = np.array(sorted(time_by_thread.keys()), dtype=float)
    times = np.array([time_by_thread[int(thread)] for thread in threads], dtype=float)
    return threads, times


def draw_parallel_panel(fig, time_spec, speed_spec):
    ax_time = fig.add_subplot(time_spec)
    ax_speed = fig.add_subplot(speed_spec)
    ideal_threads = np.array(THREADS, dtype=float)
    ideal_speedup = ideal_threads / ideal_threads[0]

    for idx, stage in enumerate(PARALLEL_STAGE_ORDER):
        threads, times = parallel_series(stage)
        speedup = times[0] / times
        common = {
            "color": PARALLEL_COLORS[idx],
            "marker": PARALLEL_MARKERS[idx],
            "markersize": 3.3,
            "linewidth": 1.1,
            "markeredgecolor": "white",
            "markeredgewidth": 0.35,
            "zorder": 3,
            "label": PARALLEL_STAGE_SHORT[stage],
        }
        ax_time.plot(threads, times, **common)
        ax_speed.plot(threads, speedup, **common)

    ax_speed.plot(
        ideal_threads,
        ideal_speedup,
        color=IDEAL_COLOR,
        lw=0.9,
        ls="--",
        zorder=1,
        label="Ideal",
    )

    for ax in (ax_time, ax_speed):
        ax.set_xscale("log", base=2)
        ax.set_xticks(THREADS)
        ax.xaxis.set_major_formatter(mticker.ScalarFormatter())
        ax.xaxis.set_minor_locator(mticker.NullLocator())
        ax.set_xlabel("Threads", fontsize=AXIS_LABEL_SIZE)
        ax.grid(axis="both", color=GRID_COLOR, lw=0.45, zorder=0)
        ax.tick_params(axis="both", labelsize=TICK_LABEL_SIZE, length=2.0, pad=1.6)

    ax_time.set_yscale("log")
    ax_time.yaxis.set_minor_locator(mticker.NullLocator())
    ax_time.set_ylabel("Time (s)", fontsize=AXIS_LABEL_SIZE)
    ax_time.set_title("Execution time", fontsize=STAGE_TITLE_SIZE, pad=2.5)

    ax_speed.set_yscale("log", base=2)
    ax_speed.set_yticks([1, 2, 4, 8, 16, 32])
    ax_speed.yaxis.set_major_formatter(mticker.ScalarFormatter())
    ax_speed.yaxis.set_minor_locator(mticker.NullLocator())
    ax_speed.set_ylim(0.8, 40)
    ax_speed.set_ylabel("Speedup (x)", fontsize=AXIS_LABEL_SIZE)
    ax_speed.set_title("Parallel speedup", fontsize=STAGE_TITLE_SIZE, pad=2.5)

    add_panel_label(ax_time, "e", x=-0.16, y=1.20)
    return ax_time, ax_speed


# ---------------------------------------------------------------------------
# Figure construction
# ---------------------------------------------------------------------------

def make_paper_figure():
    configure_style()
    fig = plt.figure(figsize=(7.2, 8.15))
    outer = fig.add_gridspec(
        4,
        1,
        left=0.078,
        right=0.99,
        top=0.92,
        bottom=0.075,
        hspace=0.56,
    )
    draw_stage_ratio_panel(
        fig,
        outer[0, 0],
        INTERNAL_TIME,
        CARDINAL_DATASETS,
        "a",
        "Speedup ratio (x)",
    )
    draw_stage_ratio_panel(
        fig,
        outer[1, 0],
        CARDINAL_TIME,
        CARDINAL_DATASETS,
        "b",
        "Runtime ratio (x)",
    )
    draw_stage_ratio_panel(
        fig,
        outer[2, 0],
        CARDINAL_MEM,
        CARDINAL_DATASETS,
        "c",
        "Memory ratio (x)",
    )

    bottom = outer[3, 0].subgridspec(
        1,
        len(STAGE_ORDER),
        width_ratios=[len(STAGE_METHODS[stage]) for stage in STAGE_ORDER],
        wspace=0.22,
    )
    draw_m2aia_panel(fig, bottom[0, :2])
    parallel = bottom[0, 2:].subgridspec(1, 2, wspace=0.32)
    ax_time, ax_speed = draw_parallel_panel(fig, parallel[0, 0], parallel[0, 1])

    cardinal_handles = [
        mpatches.Patch(facecolor=color, edgecolor="white", label=label)
        for color, label in zip(DATASET_COLORS, CARDINAL_DATASET_LABELS)
    ]
    fig.legend(
        handles=cardinal_handles,
        loc="upper left",
        bbox_to_anchor=(0.40, 0.992),
        ncol=len(cardinal_handles),
        fontsize=LEGEND_LABEL_SIZE,
        handlelength=1.0,
        handletextpad=0.35,
        columnspacing=1.0,
    )
    stage_handles = [
        mlines.Line2D(
            [],
            [],
            color=PARALLEL_COLORS[idx],
            marker=PARALLEL_MARKERS[idx],
            markersize=3.0,
            linewidth=1.0,
            markeredgecolor="white",
            markeredgewidth=0.35,
            label=PARALLEL_STAGE_SHORT[stage],
        )
        for idx, stage in enumerate(PARALLEL_STAGE_ORDER)
    ]
    stage_handles.append(mlines.Line2D([], [], color=IDEAL_COLOR, lw=0.8, ls="--", label="Ideal"))
    ax_speed.legend(
        handles=stage_handles,
        loc="upper left",
        fontsize=PARALLEL_LEGEND_SIZE,
        handlelength=1.15,
        labelspacing=0.24,
        borderpad=0.2,
    )
    return fig


def main():
    fig = make_paper_figure()
    save_figure(fig, "fig_paper_benchmark")
    hide_all_text(fig)
    save_figure(fig, "fig_paper_benchmark_notext")
    plt.close(fig)
    print("Saved paper benchmark figure to", OUT)


if __name__ == "__main__":
    main()
