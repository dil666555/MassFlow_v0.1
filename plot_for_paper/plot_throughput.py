"""Throughput figure for the ProjectNAME full-pipeline benchmark.

Throughput is computed from the Table 1 datasets as:
    total m/z-intensity pairs in the imzML file / ProjectNAME runtime.

The ProjectNAME runtime is the second tuple element in tests/pipeline_outcome.py.
The script also records spectra/s for audit, but the plotted throughput uses
data points/s because the datasets have very different m/z array lengths.
"""
import json
import os
import sys
import tempfile
import xml.etree.ElementTree as ET

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

from tests.pipeline_outcome import TIME_DATA

OUT = os.path.join(ROOT, "figures")

DATASETS = ["min", "mid", "max", "ultra"]
DATASET_LABELS = ["Min", "Mid", "Max", "Ultra"]
DATASET_PATHS = {
    "min": "/Users/dre/Desktop/data/min/file_min_profile.imzML",
    "mid": "/Users/dre/Desktop/data/mid/file_mid_profile.imzML",
    "max": "/Users/dre/Desktop/data/Example_read/example.imzML",
    "ultra": "/Users/dre/Desktop/data/original/original.imzML",
}
DATASET_COLORS = ["#D8EEF7", "#9CD4E7", "#4EA3C8", "#1F5D8F"]
METHOD_COLORS = ["#2B6C9B", "#CC6B49", "#3B8F72", "#D89C3A"]

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

GRID_COLOR = "#E8E8E8"
METHOD_LABEL_SIZE = 8.3
TICK_LABEL_SIZE = 7.2
AXIS_LABEL_SIZE = 8.2
STAGE_TITLE_SIZE = 9.5
LEGEND_LABEL_SIZE = 8.1


def configure_style():
    plt.rcParams.update({
        "font.family": "Arial",
        "font.sans-serif": ["Arial"],
        "font.size": 8,
        "mathtext.fontset": "custom",
        "mathtext.rm": "Arial",
        "mathtext.it": "Arial:italic",
        "mathtext.bf": "Arial:bold",
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


def local_name(tag):
    return tag.rsplit("}", 1)[-1]


def referenceable_groups(imzml_path):
    groups = {}
    for _event, elem in ET.iterparse(imzml_path, events=("end",)):
        if local_name(elem.tag) == "referenceableParamGroup":
            names = {
                child.attrib.get("name")
                for child in elem
                if local_name(child.tag) == "cvParam"
            }
            kind = "other"
            if "m/z array" in names:
                kind = "mz"
            elif "intensity array" in names:
                kind = "intensity"
            groups[elem.attrib["id"]] = kind
            elem.clear()
        elif local_name(elem.tag) == "run":
            break
    return groups


def imzml_metrics(imzml_path):
    groups = referenceable_groups(imzml_path)
    spectrum_count = None
    parsed_spectra = 0
    total_mz_points = 0
    total_intensity_points = 0
    min_points = None
    max_points = None

    for _event, elem in ET.iterparse(imzml_path, events=("end",)):
        tag = local_name(elem.tag)
        if tag == "spectrumList":
            spectrum_count = int(elem.attrib["count"])
        elif tag == "spectrum":
            parsed_spectra += 1
            spectrum_points = []
            for bda in elem.iter():
                if local_name(bda.tag) != "binaryDataArray":
                    continue
                ref = None
                array_length = None
                for child in bda:
                    child_tag = local_name(child.tag)
                    if child_tag == "referenceableParamGroupRef":
                        ref = child.attrib["ref"]
                    elif child_tag == "cvParam" and child.attrib.get("name") == "external array length":
                        array_length = int(child.attrib["value"])
                kind = groups.get(ref, "other")
                if kind == "mz":
                    total_mz_points += array_length
                    spectrum_points.append(array_length)
                elif kind == "intensity":
                    total_intensity_points += array_length
            if spectrum_points:
                current = max(spectrum_points)
                min_points = current if min_points is None else min(min_points, current)
                max_points = current if max_points is None else max(max_points, current)
            elem.clear()

    ibd_path = os.path.splitext(imzml_path)[0] + ".ibd"
    file_bytes = os.path.getsize(imzml_path) + os.path.getsize(ibd_path)
    return {
        "spectra": spectrum_count,
        "parsed_spectra": parsed_spectra,
        "total_mz_points": total_mz_points,
        "total_intensity_points": total_intensity_points,
        "min_points_per_spectrum": min_points,
        "max_points_per_spectrum": max_points,
        "file_size_gb": file_bytes / 1e9,
    }


def method_label(method):
    if method.startswith("Savitzky"):
        return "SG"
    return METHOD_SHORT.get(method, method)


def throughput_rows(dataset_metrics):
    rows = []
    for stage in STAGE_ORDER:
        for method in TIME_DATA[stage]:
            for dataset in DATASETS:
                project_time_s = TIME_DATA[stage][method][dataset][1]
                metrics = dataset_metrics[dataset]
                total_points = metrics["total_intensity_points"]
                rows.append({
                    "stage": stage,
                    "method": method,
                    "dataset": dataset,
                    "project_time_s": project_time_s,
                    "million_points_per_s": total_points / project_time_s / 1e6,
                    "spectra_per_s": metrics["spectra"] / project_time_s,
                })
    return rows


def save_figure(fig, stem):
    os.makedirs(OUT, exist_ok=True)
    for ext, kwargs in [
        ("svg", {}),
        ("pdf", {}),
        ("png", {"dpi": 600}),
    ]:
        fig.savefig(os.path.join(OUT, f"{stem}.{ext}"), bbox_inches="tight", **kwargs)


def hide_all_text(fig):
    for text in fig.findobj(mtext.Text):
        text.set_color("none")


def rows_by_stage(rows):
    grouped = {stage: [] for stage in STAGE_ORDER}
    for row in rows:
        grouped[row["stage"]].append(row)
    return grouped


def methods_by_stage(rows):
    grouped = rows_by_stage(rows)
    methods = {}
    for stage in STAGE_ORDER:
        seen = []
        for row in grouped[stage]:
            if row["method"] not in seen:
                seen.append(row["method"])
        methods[stage] = seen
    return methods


def throughput_value(grouped_rows, stage, method, dataset):
    for row in grouped_rows[stage]:
        if row["method"] == method and row["dataset"] == dataset:
            return row["million_points_per_s"]
    raise KeyError((stage, method, dataset))


def make_dot_figure(rows):
    configure_style()
    grouped = rows_by_stage(rows)
    methods = methods_by_stage(rows)
    offsets = [-0.24, -0.08, 0.08, 0.24]

    fig = plt.figure(figsize=(7.2, 3.05))
    grid = fig.add_gridspec(
        1,
        len(STAGE_ORDER),
        left=0.078,
        right=0.99,
        top=0.78,
        bottom=0.22,
        wspace=0.46,
    )

    for col, stage in enumerate(STAGE_ORDER):
        ax = fig.add_subplot(grid[0, col])
        stage_methods = methods[stage]
        ypos = {
            method: len(stage_methods) - 1 - idx
            for idx, method in enumerate(stage_methods)
        }

        for method in stage_methods:
            y = ypos[method]
            values = [
                throughput_value(grouped, stage, method, dataset)
                for dataset in DATASETS
            ]
            ax.hlines(y, min(values), max(values), color="#D5D5D5", lw=0.7, zorder=1)
            for idx, value in enumerate(values):
                ax.scatter(
                    value,
                    y + offsets[idx],
                    s=25,
                    color=DATASET_COLORS[idx],
                    edgecolor="white",
                    linewidth=0.45,
                    zorder=3,
                )

        ax.set_xscale("log")
        ax.set_xlim(20, 520)
        ax.xaxis.set_major_locator(mticker.FixedLocator([30, 100, 300]))
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda value, _pos: f"{value:g}"))
        ax.xaxis.set_minor_locator(mticker.NullLocator())
        ax.set_ylim(-0.65, len(stage_methods) - 0.35)
        ax.set_yticks([ypos[method] for method in stage_methods])
        ax.set_yticklabels([method_label(method) for method in stage_methods], fontsize=7.6)
        ax.set_title(STAGE_SHORT[stage], fontsize=9.2, pad=3)
        ax.grid(axis="x", color=GRID_COLOR, lw=0.45, zorder=0)
        ax.tick_params(axis="x", labelsize=TICK_LABEL_SIZE, length=2.0, pad=1.6)
        ax.tick_params(axis="y", labelsize=7.6, length=0, pad=2.0)

    fig.text(
        0.53,
        0.075,
        "Throughput (million m/z-intensity pairs/s)",
        ha="center",
        va="center",
        fontsize=AXIS_LABEL_SIZE,
    )
    handles = [
        mpatches.Patch(facecolor=color, edgecolor="white", label=label)
        for color, label in zip(DATASET_COLORS, DATASET_LABELS)
    ]
    fig.legend(
        handles=handles,
        loc="upper center",
        bbox_to_anchor=(0.56, 0.985),
        ncol=len(handles),
        fontsize=LEGEND_LABEL_SIZE,
        handlelength=1.0,
        handletextpad=0.35,
        columnspacing=1.0,
    )
    return fig


def adjust_label_positions(label_items, min_gap=0.055):
    lower = np.log10(22.0)
    upper = np.log10(500.0)
    adjusted = []
    for log_y, method, values, color in sorted(label_items):
        if adjusted and log_y - adjusted[-1][0] < min_gap:
            log_y = adjusted[-1][0] + min_gap
        adjusted.append((log_y, method, values, color))

    if adjusted:
        overflow = adjusted[-1][0] - upper
        if overflow > 0:
            adjusted = [
                (log_y - overflow, method, values, color)
                for log_y, method, values, color in adjusted
            ]
        underflow = lower - adjusted[0][0]
        if underflow > 0:
            adjusted = [
                (log_y + underflow, method, values, color)
                for log_y, method, values, color in adjusted
            ]
    return adjusted


def make_slope_figure(rows):
    configure_style()
    grouped = rows_by_stage(rows)
    methods = methods_by_stage(rows)
    dataset_x = np.linspace(0.0, 3.9, len(DATASETS))

    fig = plt.figure(figsize=(7.2, 3.2))
    grid = fig.add_gridspec(
        1,
        len(STAGE_ORDER),
        left=0.072,
        right=0.99,
        top=0.82,
        bottom=0.20,
        wspace=0.40,
    )

    for col, stage in enumerate(STAGE_ORDER):
        ax = fig.add_subplot(grid[0, col])
        label_items = []
        for idx, method in enumerate(methods[stage]):
            values = [
                throughput_value(grouped, stage, method, dataset)
                for dataset in DATASETS
            ]
            color = METHOD_COLORS[idx % len(METHOD_COLORS)]
            label_items.append((np.log10(values[-1]), method, values, color))
            ax.plot(
                dataset_x,
                values,
                color=color,
                marker="o",
                markersize=3.4,
                linewidth=1.0,
                markeredgecolor="white",
                markeredgewidth=0.35,
                alpha=0.95,
                zorder=3,
            )

        for log_y, method, values, color in adjust_label_positions(label_items):
            label_y = 10 ** log_y
            ax.plot(
                [dataset_x[-1], dataset_x[-1] + 0.20],
                [values[-1], label_y],
                color=color,
                lw=0.55,
                alpha=0.65,
                clip_on=False,
                zorder=2,
            )
            ax.text(
                dataset_x[-1] + 0.26,
                label_y,
                method_label(method),
                color=color,
                fontsize=6.1,
                ha="left",
                va="center",
                clip_on=False,
            )

        ax.set_yscale("log")
        ax.set_ylim(20, 520)
        ax.yaxis.set_major_locator(mticker.FixedLocator([30, 100, 300]))
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda value, _pos: f"{value:g}"))
        ax.yaxis.set_minor_locator(mticker.NullLocator())
        ax.set_xlim(-0.25, dataset_x[-1] + 0.25)
        ax.set_xticks(dataset_x)
        ax.set_xticklabels(DATASET_LABELS, fontsize=7.4)
        ax.set_title(STAGE_SHORT[stage], fontsize=9.2, pad=3)
        ax.grid(axis="y", color=GRID_COLOR, lw=0.45, zorder=0)
        ax.tick_params(axis="x", length=0, pad=2)
        ax.tick_params(axis="y", labelsize=TICK_LABEL_SIZE, pad=1.6)

        if col == 0:
            ax.set_ylabel("Throughput (million pairs/s)", fontsize=AXIS_LABEL_SIZE)
        else:
            ax.set_yticklabels([])
            ax.tick_params(axis="y", length=0)

    fig.text(
        0.53,
        0.075,
        "Dataset",
        ha="center",
        va="center",
        fontsize=AXIS_LABEL_SIZE,
    )
    return fig


def write_metrics(dataset_metrics, rows):
    payload = {
        "dataset_metrics": dataset_metrics,
        "throughput_rows": rows,
    }
    with open(os.path.join(OUT, "throughput_metrics.json"), "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def main():
    os.makedirs(OUT, exist_ok=True)
    dataset_metrics = {
        dataset: imzml_metrics(path)
        for dataset, path in DATASET_PATHS.items()
    }
    rows = throughput_rows(dataset_metrics)

    dot_fig = make_dot_figure(rows)
    save_figure(dot_fig, "fig_throughput_dot")
    hide_all_text(dot_fig)
    save_figure(dot_fig, "fig_throughput_dot_notext")
    plt.close(dot_fig)

    slope_fig = make_slope_figure(rows)
    save_figure(slope_fig, "fig_throughput_slope")
    hide_all_text(slope_fig)
    save_figure(slope_fig, "fig_throughput_slope_notext")
    plt.close(slope_fig)

    write_metrics(dataset_metrics, rows)
    print("Saved throughput figure to", OUT)


if __name__ == "__main__":
    main()
