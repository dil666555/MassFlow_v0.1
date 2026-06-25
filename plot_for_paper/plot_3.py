"""Generate a text-minimal composite figure for paper/PPT editing.

The figure combines the three ratio plots from plot.py into one SVG/PNG while
leaving only the dataset legend as text. Axis lines and tick marks are kept;
axis labels, tick labels, panel titles, and row titles are intentionally omitted.
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
import matplotlib.ticker as mticker
import numpy as np

from tests.python_outcome import TIME_DATA as A_TIME
from tests.pipeline_outcome import MEMORY_DATA as B_MEM
from tests.pipeline_outcome import TIME_DATA as B_TIME

OUT = os.path.join(ROOT, "figures")
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({
    "font.family": "Arial",
    "font.size": 10,
    "axes.linewidth": 0.7,
    "svg.fonttype": "none",
})

SHADES4 = ["#CFE8F7", "#8FCDEC", "#4FA8DC", "#2E73B0"]
LOSS = "#E8A0A0"

STAGE_ORDER = [
    "Baseline Correction",
    "Normalization",
    "Peak Alignment",
    "Noise Reduction",
    "Peak Picking",
]
DS4 = ["min", "mid", "max", "ultra"]
LAB4 = ["Min", "Mid", "Max", "Ultra"]


def ratio(num, den):
    return float("inf") if den == 0 else num / den


def draw_ratio_row(fig, outer_gs, row, data, ymin, ymax):
    methods = {stage: list(data[stage].keys()) for stage in STAGE_ORDER}
    counts = [len(methods[stage]) for stage in STAGE_ORDER]
    inner_gs = outer_gs[row, 0].subgridspec(
        1,
        len(STAGE_ORDER),
        width_ratios=counts,
        wspace=0.26,
    )

    for col, stage in enumerate(STAGE_ORDER):
        ax = fig.add_subplot(inner_gs[0, col])
        stage_methods = methods[stage]
        x = np.arange(len(stage_methods))
        bar_width = 0.8 / len(DS4)

        for idx, dataset in enumerate(DS4):
            values = [
                ratio(*data[stage][method][dataset])
                for method in stage_methods
            ]
            xpos = x - 0.4 + bar_width * (idx + 0.5)
            bars = ax.bar(
                xpos,
                values,
                bar_width,
                color=SHADES4[idx],
                edgecolor="white",
                linewidth=0.4,
                zorder=2,
            )
            for bar, value in zip(bars, values):
                if value < 1.0:
                    bar.set_edgecolor(LOSS)
                    bar.set_linewidth(0.8)

        ax.axhline(1.0, color="#eeeeee", lw=0.5, zorder=1)
        ax.set_yscale("log")
        ax.set_ylim(ymin, ymax)
        ax.yaxis.set_major_locator(mticker.LogLocator(base=10, subs=(1.0,)))
        ax.yaxis.set_major_formatter(mticker.NullFormatter())
        ax.yaxis.set_minor_locator(mticker.NullLocator())
        ax.yaxis.set_minor_formatter(mticker.NullFormatter())
        ax.set_xlim(-0.5, len(stage_methods) - 0.5)
        ax.set_xticks(x)
        ax.tick_params(
            axis="both",
            which="both",
            length=2,
            width=0.7,
            labelbottom=False,
            labelleft=False,
        )
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_visible(True)
        ax.spines["left"].set_visible(True)
        ax.spines["bottom"].set_zorder(5)
        ax.spines["left"].set_zorder(5)
        ax.grid(axis="y", color="#eeeeee", lw=0.5, zorder=0)


def ratio_range(data):
    values = []
    for stage in STAGE_ORDER:
        for method in data[stage]:
            for dataset in DS4:
                values.append(ratio(*data[stage][method][dataset]))
    return min(values), max(values)


def main():
    rows = [A_TIME, B_TIME, B_MEM]

    fig = plt.figure(figsize=(7.2, 6.2))
    outer_gs = fig.add_gridspec(3, 1, hspace=0.12)

    for row, data in enumerate(rows):
        vmin, vmax = ratio_range(data)
        draw_ratio_row(fig, outer_gs, row, data, min(0.7, vmin * 0.8), vmax * 1.5)

    proxies = [
        mpatches.Patch(
            facecolor=SHADES4[idx],
            edgecolor="white",
            label=LAB4[idx],
        )
        for idx in range(len(DS4))
    ]
    fig.legend(
        handles=proxies,
        loc="upper center",
        ncol=len(DS4),
        frameon=False,
        bbox_to_anchor=(0.5, 0.995),
        handlelength=1.1,
        columnspacing=1.6,
    )
    fig.subplots_adjust(left=0.02, right=0.995, top=0.94, bottom=0.02)

    fig.savefig(os.path.join(OUT, "fig_combined_3.png"), dpi=300)
    fig.savefig(os.path.join(OUT, "fig_combined_3.svg"))
    plt.close(fig)
    print("Saved figure to", OUT)


if __name__ == "__main__":
    main()
