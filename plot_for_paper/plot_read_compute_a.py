"""Draw panel a using retained cached core and new read-compute measurements."""
import argparse
import hashlib
import json
from pathlib import Path
import statistics

from benchmark_results import CASE_LAYOUT, DATASETS, DEFAULT_RUN, ROOT, write_csv
from plot_paper import (
    CARDINAL_DATASET_LABELS, DATASET_COLORS, LEGEND_LABEL_SIZE,
    check_layout, configure_style, draw_stage_ratio_panel, mpatches, plt,
    save_figure,
)


def load_record(run, campaign, backend, dataset, case):
    path = run / f"{backend}-core" / f"{dataset}-{case}.json"
    record = json.loads(path.read_text())
    expected_scopes = ("cache_core", "cache_core_legacy") if dataset in DATASETS[:2] else ("read_compute",)
    stats = record["stats"]
    if (record["campaign_id"] != campaign or record["scope"] not in expected_scopes
            or record["dataset"] != dataset or record["case"] != case
            or record["backend"] != backend or record["mode"] != "time"
            or stats["rounds"] != 2 or len(stats["data"]) != 2
            or stats["mean"] != statistics.mean(stats["data"])):
        raise ValueError(f"Inconsistent core measurement: {path}")
    return record, path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-run", type=Path, default=DEFAULT_RUN)
    parser.add_argument("--run-dir", type=Path, default=ROOT / "benchmarks/results/read-compute")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "plot_for_paper/figures/read_compute_a")
    args = parser.parse_args()
    base, run = args.base_run.resolve(), args.run_dir.resolve()
    manifests = {folder: json.loads((folder / "manifest.json").read_text()) for folder in (base, run)}
    data = {stage: {} for stage, *_ in CASE_LAYOUT}
    sources = []
    for stage, method, case, _ in CASE_LAYOUT:
        if case in ("reference", "mad"):
            continue
        python_case = "origin" if case in ("quantile", "diff", "sd") else case
        data[stage][method] = {}
        for dataset in DATASETS:
            folder = base if dataset in DATASETS[:2] else run
            campaign = manifests[folder]["id"]
            python, python_path = load_record(folder, campaign, "python", dataset, python_case)
            numba, numba_path = load_record(folder, campaign, "numba", dataset, case)
            top, bottom = python["stats"]["mean"], numba["stats"]["mean"]
            data[stage][method][dataset] = (top, bottom)
            source = {
                "panel": "a", "stage": stage, "method": method, "dataset": dataset,
                "python_case": python_case, "numba_case": case,
                "python_mean_seconds": top, "numba_mean_seconds": bottom,
                "ratio": top / bottom, "campaign_id": campaign,
                "python_scope": python["scope"], "numba_scope": numba["scope"],
                "reused_python_result": python.get("reused_result", False),
                "comparison": "different_peak_picking_methods" if python_case == "origin" else "native_implementations",
            }
            for prefix, path in (("python", python_path), ("numba", numba_path)):
                source[f"{prefix}_json"] = str(path.relative_to(ROOT))
                source[f"{prefix}_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
            sources.append(source)

    configure_style()
    fig = plt.figure(figsize=(7.2, 2.75))
    grid = fig.add_gridspec(1, 1, left=0.078, right=0.99, top=0.77, bottom=0.28)
    draw_stage_ratio_panel(fig, grid[0, 0], data, DATASETS, "a", "Speedup ratio")
    handles = [mpatches.Patch(facecolor=color, edgecolor="white", label=label)
               for color, label in zip(DATASET_COLORS, CARDINAL_DATASET_LABELS)]
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.40, 0.992),
               ncol=4, fontsize=LEGEND_LABEL_SIZE, handlelength=1.0,
               handletextpad=0.35, columnspacing=1.0)
    fig.text(0.078, 0.025,
             "Min/Mid: cached compute; Max/Ultra: read + compute. No output writing.\n"
             "Peak picking: shared Python Origin reference (different methods).",
             fontsize=6.3, va="bottom", linespacing=1.5)
    qa = check_layout(fig)
    if qa["texts_outside_canvas"]:
        raise ValueError(f"Figure text outside canvas: {qa['texts_outside_canvas']}")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    save_figure(fig, "fig_numba_vs_python_a", args.output_dir)
    plt.close(fig)
    write_csv(args.output_dir / "source_data.csv", sources)
    metadata = {
        "campaigns": {"min_mid": manifests[base]["id"], "max_ultra": manifests[run]["id"]},
        "source_rows": len(sources), "technical_repeats": 2,
        "center": "Python arithmetic mean / Numba arithmetic mean",
        "error_bars": "none", "styles": "original panel a drawing helper and constants",
        "qa": qa,
    }
    (args.output_dir / "figure_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    notes = [
        "# Panel a | Python/NumPy time divided by Numba time", "",
        "Purpose: compare the measured runtime advantage across operators and dataset sizes, using the original panel a layout, palette and logarithmic axis.", "",
        "Min/Mid retain cached core timings; Max/Ultra use the new streaming read + compute measurements. No measured operation writes processed results. Input manager/header initialization and peak-picking input preparation remain outside the timer. These four columns must not all be described as pure computation.", "",
        "Each bar divides the arithmetic means of two technical repetitions after one warmup. No error bars or statistical tests are shown. The dashed line is 1×; red bar edges indicate ratios below 1×. Annotations give each stage's highest ratio. Numba uses four compute threads. Python and Numba retain their own reading APIs; the comparison includes their native batching and allocation costs.", "",
        "Python Origin is the shared reference for Quantile, Diff and SD: these compare different peak-picking algorithms. Python has no Reference or MAD baseline; their original positions remain empty. Min/Mid Python SNIP retains the previously reused M5 cache entry, including its documented entry overhead.", "",
        "The two campaigns use the same recorded machine, input data and numerical configuration. They ran separately, with no thermal or swap history; ratios near 1× should not be read as established differences. Source JSON paths, hashes, scopes and reuse flags are in source_data.csv. The old a–c figure is preserved.", "",
        "## Speedup ratios", "",
        "| Stage | Method | Min | Mid | Max | Ultra |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for stage, method, case, label in CASE_LAYOUT:
        if method not in data[stage]:
            continue
        values = [f"{data[stage][method][ds][0] / data[stage][method][ds][1]:.3f}×" for ds in DATASETS]
        notes.append("| " + " | ".join([stage, label, *values]) + " |")
    notes += ["", "## Export and QA", "",
              f"Python/matplotlib; quantitative grid; 7.2 × 2.75 inch canvas; {qa['axes']} stage axes, {qa['bars']} bars; no text outside the canvas. Editable SVG/PDF and 600 dpi PNG. Original font, palette, bar spacing, logarithmic axis, missing-method positions and stage maxima are retained.", "",
              "Reproduce from the repository root:", "",
              "```bash", "uv run --frozen --extra r python plot_for_paper/plot_read_compute_a.py", "```", ""]
    (args.output_dir / "FIGURE_NOTES.md").write_text("\n".join(notes))
    print(f"Saved panel a and {len(sources)} source rows to {args.output_dir}")
    for ds in DATASETS:
        rows = [row for row in sources if row["dataset"] == ds]
        highest = max(rows, key=lambda row: row["ratio"])
        print(f"{ds}: {min(row['ratio'] for row in rows):.3f}–{highest['ratio']:.3f}x; highest {highest['method']}")


if __name__ == "__main__":
    main()
