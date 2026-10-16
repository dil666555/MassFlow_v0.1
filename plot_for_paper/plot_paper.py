"""Plot this campaign with the original paper figure's a–c styling."""
import argparse
import json
import os
from pathlib import Path
import tempfile

os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "massflow-essay-matplotlib-cache"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.patches as mpatches
import matplotlib.text as mtext
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

from benchmark_results import DEFAULT_RUN, Results, write_csv

OUT = Path(__file__).resolve().parent / "figures"

# ---------------------------------------------------------------------------
# Original paper figure constants and drawing helpers
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


DATASET_COLORS = ["#D8EEF7", "#9CD4E7", "#4EA3C8", "#1F5D8F"]


GRID_COLOR = "#E8E8E8"


LOSS_EDGE = "#CC4C4C"


METHOD_LABEL_SIZE = 8.3


TICK_LABEL_SIZE = 7.2


RATIO_AXIS_LABEL_SIZE = 10.5


STAGE_TITLE_SIZE = 9.5


STAGE_TITLE_PAD = 12.0


PANEL_LABEL_SIZE = 14.0


BAR_LABEL_SIZE = 8.0


LEGEND_LABEL_SIZE = 8.1


ROW_LABEL_X = 0.018


ROW_LABEL_Y_OFFSET = 0.028


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


def ratio(baseline, massflow):
    return baseline / massflow


def method_label(method):
    if method.startswith("Savitzky"):
        return "SG"
    return METHOD_SHORT.get(method, method)


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


def annotate_highest_bar(ax):
    bar = max(ax.patches, key=lambda patch: patch.get_height())
    height = bar.get_height()
    annotation = ax.annotate(
        f"{height:.2f}x",
        xy=(bar.get_x() + bar.get_width() / 2, height),
        xytext=(0, 3),
        textcoords="offset points",
        fontsize=BAR_LABEL_SIZE,
        ha="center",
        va="bottom",
    )
    bbox = annotation.get_window_extent(ax.figure.canvas.get_renderer())
    if bbox.x0 < ax.bbox.x0:
        annotation.set_horizontalalignment("left")
    elif bbox.x1 > ax.bbox.x1:
        annotation.set_horizontalalignment("right")


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
    ylabel_size=RATIO_AXIS_LABEL_SIZE,
):
    values = ratio_values(data, stages, stage_methods, datasets)
    ymin = min(0.7, values.min() * 0.78)
    ymax = values.max() * 2.0
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
        ax.set_title(STAGE_SHORT.get(stage, stage), fontsize=STAGE_TITLE_SIZE, pad=STAGE_TITLE_PAD)
        annotate_highest_bar(ax)
        ax.grid(axis="y", color=GRID_COLOR, lw=0.45, zorder=0)
        ax.tick_params(axis="x", labelsize=METHOD_LABEL_SIZE, pad=1.6)
        ax.tick_params(axis="y", labelsize=TICK_LABEL_SIZE, pad=1.6)

        if col == 0:
            ax.set_ylabel(ylabel, fontsize=ylabel_size)
        else:
            ax.set_yticklabels([])
            ax.tick_params(axis="y", length=0)

    add_row_panel_label(axes[0], panel_label)
    return axes

# ---------------------------------------------------------------------------
# Current-campaign panels and source-data export
# ---------------------------------------------------------------------------

def make_abc_figure(panels):
    configure_style()
    fig = plt.figure(figsize=(7.2, 6.25))
    outer = fig.add_gridspec(
        3, 1, left=0.078, right=0.99, top=0.90, bottom=0.075, hspace=0.56,
    )
    for row, (panel, ylabel) in enumerate((
        ("a", "Speedup ratio"), ("b", "Runtime ratio (x)"), ("c", "Memory ratio"),
    )):
        draw_stage_ratio_panel(
            fig, outer[row, 0], panels[panel], CARDINAL_DATASETS,
            panel, ylabel, ylabel_size=RATIO_AXIS_LABEL_SIZE,
        )
    handles = [
        mpatches.Patch(facecolor=color, edgecolor="white", label=label)
        for color, label in zip(DATASET_COLORS, CARDINAL_DATASET_LABELS)
    ]
    fig.legend(
        handles=handles, loc="upper left", bbox_to_anchor=(0.40, 0.992),
        ncol=len(handles), fontsize=LEGEND_LABEL_SIZE, handlelength=1.0,
        handletextpad=0.35, columnspacing=1.0,
    )
    return fig


def check_layout(fig):
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    texts = list(fig.texts)
    for legend in fig.legends:
        texts.extend(legend.get_texts())
    for ax in fig.axes:
        texts.extend([ax.title, ax.xaxis.label, ax.yaxis.label, *ax.texts])
        for axis in (ax.xaxis, ax.yaxis):
            low, high = sorted(axis.get_view_interval())
            for tick in axis.get_major_ticks():
                if low <= tick.get_loc() <= high:
                    texts.extend([tick.label1, tick.label2])
    texts = [text for text in texts if text.get_visible() and text.get_text()]
    outside = []
    for text in texts:
        box = text.get_window_extent(renderer)
        if box.width and box.height and (box.x0 < 0 or box.y0 < 0
                                        or box.x1 > fig.bbox.x1 or box.y1 > fig.bbox.y1):
            outside.append(text.get_text())
    return {"axes": len(fig.axes), "bars": sum(len(ax.patches) for ax in fig.axes),
            "texts_outside_canvas": outside,
            "svg_text": "editable", "pdf_fonttype": plt.rcParams["pdf.fonttype"],
            "preview_dpi": 600}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN)
    parser.add_argument("--output-dir", type=Path, default=OUT)
    args = parser.parse_args()
    results = Results(args.run_dir)
    panels, sources = results.panels()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir / "source_data.csv", sources)
    fig = make_abc_figure(panels)
    qa = check_layout(fig)
    if qa["texts_outside_canvas"]:
        raise ValueError(f"Figure text outside canvas: {qa['texts_outside_canvas']}")
    save_figure(fig, "fig_paper_benchmark_abc", args.output_dir)
    hide_all_text(fig)
    save_figure(fig, "fig_paper_benchmark_abc_notext", args.output_dir)
    plt.close(fig)
    metadata = {"campaign_id": results.manifest["id"], "run_dir": str(results.run),
                "source_rows": len(sources), "technical_repeats": 2,
                "center": "ratio of two arithmetic means", "error_bars": "none",
                "styles": "original a–c figure constants, helpers and layout",
                "qa": qa}
    (args.output_dir / "figure_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    caption = """# Figure a–c | Runtime and sampled RSS ratios

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
"""
    (args.output_dir / "FIGURE_NOTES.md").write_text(caption)
    print(f"Saved figure, no-text exports and {len(sources)} source rows to {args.output_dir}")


if __name__ == "__main__":
    main()
