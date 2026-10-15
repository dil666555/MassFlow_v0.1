"""Six benchmark campaigns, preparation, and provenance-aware summaries."""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
import os
from pathlib import Path
import platform
import shutil
import statistics
import subprocess
import sys
import tempfile
import time

import psutil

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "benchmarks"
GROUPS = ("python-core", "numba-pipeline", "numba-core", "cardinal-pipeline",
          "numba-memory", "cardinal-memory")
DATASETS = ("min", "mid", "max", "ultra")


def read_json(path):
    return json.loads(Path(path).read_text())


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # A completed JSON is the resume marker; interrupted writes stay as .partial.
    partial = path.with_suffix(path.suffix + ".partial")
    partial.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    partial.replace(path)


def command_output(args):
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def environment():
    keys = ("NUMBA_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
            "VECLIB_MAXIMUM_THREADS")
    return {
        "host": platform.node(), "system": platform.platform(),
        "machine": platform.machine(), "cpu": platform.processor(),
        "logical_cpus": os.cpu_count(), "ram_bytes": psutil.virtual_memory().total,
        "python": sys.version, "python_executable": sys.executable,
        "packages": {p: version(p) for p in ("numpy", "scipy", "numba", "pyimzml", "psutil")},
        "R": json.loads(command_output(["Rscript", "--vanilla", str(HERE / "cardinal_bench.R"), "--probe"])),
        "thread_env": {k: os.environ[k] for k in keys},
    }


def source_hash():
    paths = [*sorted((ROOT / "src").rglob("*.py")), *sorted(HERE.glob("*.py")),
             HERE / "cardinal_bench.R", HERE / "config.json", ROOT / "uv.lock"]
    digest = hashlib.sha256()
    for p in paths:
        digest.update(str(p.relative_to(ROOT)).encode())
        digest.update(p.read_bytes())
    return digest.hexdigest()


def inspect_input(path):
    """Parse headers and inspect only m/z endpoints; never load all intensities."""
    import numpy as np
    from pyimzml.ImzMLParser import ImzMLParser

    path = Path(path).resolve()
    ibd = path.with_suffix(".ibd")
    if not path.is_file() or not ibd.is_file():
        raise FileNotFoundError(f"Missing imzML/ibd pair: {path}")
    parser = ImzMLParser(str(path))
    try:
        dtype = np.dtype(parser.mzPrecision)
        # Shared m/z axes are read once, not once per pixel.
        axes = dict(zip(parser.mzOffsets, parser.mzLengths))
        lower, upper = [], []
        with ibd.open("rb") as f:
            uuid = f.read(16).hex()
            for offset, length in axes.items():
                if length == 0:
                    raise ValueError(f"Empty m/z axis in {path}")
                f.seek(offset)
                lower.append(float(np.frombuffer(f.read(dtype.itemsize), dtype=dtype)[0]))
                f.seek(offset + (length - 1) * dtype.itemsize)
                upper.append(float(np.frombuffer(f.read(dtype.itemsize), dtype=dtype)[0]))
        lo, hi = max(lower), min(upper)
        if not lo <= hi:
            raise ValueError(f"No common m/z interval for reference normalization: {path}")
        return {
            "path": str(path), "ibd_path": str(ibd), "ibd_uuid": uuid,
            "imzml_bytes": path.stat().st_size, "ibd_bytes": ibd.stat().st_size,
            "imzml_mtime_ns": path.stat().st_mtime_ns, "ibd_mtime_ns": ibd.stat().st_mtime_ns,
            "spectra": len(parser.coordinates),
            "intensity_points": sum(parser.intensityLengths),
            "mz_dtype": parser.mzPrecision, "intensity_dtype": parser.intensityPrecision,
            "reference": (lo + hi) / 2,
            # Match Cardinal's nearest-reference selection without a 0.1-Da cutoff.
            "ref_tolerance": max(upper) - min(lower) + 1.0,
        }
    finally:
        parser.m.close()


def file_identity(info):
    for kind, key in (("imzml", "path"), ("ibd", "ibd_path")):
        stat = Path(info[key]).stat()
        if stat.st_size != info[f"{kind}_bytes"] or stat.st_mtime_ns != info[f"{kind}_mtime_ns"]:
            raise ValueError(f"Input changed since init: {info[key]}")


def initialize(run, cfg):
    if (run / "manifest.json").exists():
        raise FileExistsError("Campaign exists. Use the six commands with --resume, or a new --run-dir.")
    inputs = {ds: inspect_input(cfg["datasets"][ds]) for ds in DATASETS}
    manifest = {
        "id": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "config": cfg, "source_sha256": source_hash(), "environment": environment(),
        "git_commit": command_output(["git", "rev-parse", "HEAD"]),
        "git_branch": command_output(["git", "branch", "--show-current"]),
        "git_dirty": bool(command_output(["git", "status", "--porcelain"])),
        "inputs": inputs,
    }
    write_json(run / "manifest.json", manifest)
    print("Initialized", run)
    for ds, info in inputs.items():
        print(ds, info["spectra"], "spectra;", info["intensity_points"], "points; ref=", info["reference"])


def validate_campaign(run, cfg):
    manifest = read_json(run / "manifest.json")
    if cfg != manifest["config"] or source_hash() != manifest["source_sha256"]:
        raise ValueError("Configuration/source changed after init; use a new --run-dir.")
    if environment() != manifest["environment"]:
        raise ValueError("Machine/software/thread environment changed after init.")
    for info in manifest["inputs"].values():
        file_identity(info)
    return manifest


def prepare(run, manifest, datasets, resume):
    from contextlib import ExitStack
    from python_bench import run_pipeline, output_info
    from massflow.preprocess.numba.numba_runtime import apply_numba_runtime

    cfg = manifest["config"]
    apply_numba_runtime(override_workers=cfg["numba_threads"])
    case = next(c for c in cfg["cases"] if c["id"] == "quantile")
    for ds in datasets:
        target = run / "alignment" / ds
        marker = target / "prepared.json"
        if marker.exists():
            if resume:
                file_identity(read_json(marker)["input"])
                print("Skip prepared", ds)
                continue
            raise FileExistsError(f"Already prepared: {ds}; add --resume.")
        target.mkdir(parents=True, exist_ok=True)
        job = {"backend": "numba", "case": case, "config": cfg,
               "input": manifest["inputs"][ds]["path"]}
        with tempfile.TemporaryDirectory(dir=target) as tmp, ExitStack() as stack:
            out, expected, _ = run_pipeline(job, stack, tmp)
            info = output_info(out, expected)
            for suffix in ("imzML", "ibd"):
                shutil.copyfile(Path(out.file_base_path).with_suffix("." + suffix), target / ("input." + suffix))
        # Alignment does not need a common ref-normalization interval, so retain
        # its source metadata separately rather than reusing inspect_input().
        picked = {
            "path": str(target / "input.imzML"), "ibd_path": str(target / "input.ibd"),
            "spectra": info["spectra"],
        }
        for kind, key in (("imzml", "path"), ("ibd", "ibd_path")):
            stat = Path(picked[key]).stat()
            picked[f"{kind}_bytes"] = stat.st_size
            picked[f"{kind}_mtime_ns"] = stat.st_mtime_ns
        write_json(marker, {"campaign_id": manifest["id"], "input": picked,
                            "source": manifest["inputs"][ds], "parameters": case["numba"]})
        print("Prepared common alignment input", ds, flush=True)


def wait_for(path, process):
    while not path.exists():
        if process.poll() is not None:
            raise RuntimeError(f"Worker exited before {path.name}; inspect its log.")
        time.sleep(0.005)


def launch(job, directory):
    directory.mkdir(parents=True, exist_ok=True)
    job = dict(job, output=str(directory / "worker.json"),
               scratch=str(directory / "scratch"), control=str(directory))
    write_json(directory / "job.json", job)
    if job["backend"] == "cardinal":
        command = ["Rscript", "--vanilla", str(HERE / "cardinal_bench.R"), str(directory / "job.json")]
    else:
        command = [sys.executable, str(HERE / "python_bench.py"), str(directory / "job.json")]
    with (directory / "worker.log").open("w") as log:
        process = subprocess.Popen(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        try:
            if job["mode"] == "memory":
                memory = []
                for round_number in range(1, job["config"]["rounds"] + 1):
                    wait_for(directory / f"ready-{round_number}", process)
                    worker = psutil.Process(process.pid)
                    baseline = peak = worker.memory_info().rss
                    timestamps = [time.perf_counter()]
                    (directory / f"go-{round_number}").touch()
                    while not (directory / f"done-{round_number}").exists():
                        if process.poll() is not None:
                            raise RuntimeError(f"Worker failed; see {directory / 'worker.log'}")
                        peak = max(peak, worker.memory_info().rss)
                        timestamps.append(time.perf_counter())
                        time.sleep(job["config"]["rss_interval_seconds"])
                    peak = max(peak, worker.memory_info().rss)
                    timestamps.append(time.perf_counter())
                    (directory / f"collected-{round_number}").touch()
                    memory.append({
                        "baseline_rss_mib": baseline / 2**20,
                        "sampled_peak_rss_mib": peak / 2**20,
                        "sample_count": len(timestamps),
                        "max_sample_gap_seconds": max(b - a for a, b in zip(timestamps, timestamps[1:])),
                    })
            code = process.wait()
            if code:
                raise RuntimeError(f"Worker exit {code}; see {directory / 'worker.log'}")
        finally:
            if process.poll() is None:
                process.terminate()
                process.wait()
    result = read_json(directory / "worker.json")
    if job["mode"] == "memory":
        result["memory"] = memory
    return result


def run_group(run, manifest, group, datasets, case_ids, resume):
    backend = group.split("-", 1)[0]
    mode = "memory" if group.endswith("memory") else "time"
    cfg = manifest["config"]
    if group == "numba-core":
        datasets = [ds for ds in datasets if ds in ("min", "mid")]
        if not datasets:
            raise ValueError("Numba Max/Ultra core rows reuse numba-pipeline; no core run is needed.")
    selected = [c for c in cfg["cases"] if backend in c and (not case_ids or c["id"] in case_ids)]
    if not selected:
        raise ValueError(f"No supported cases for {backend}: {case_ids}")
    total = len(selected) * len(datasets)
    done = 0
    for ds in datasets:
        for case in selected:
            path = run / group / f'{ds}-{case["id"]}.json'
            if path.exists():
                if resume:
                    saved = read_json(path)
                    if saved["campaign_id"] != manifest["id"]:
                        raise ValueError(f"Campaign mismatch: {path}")
                    print("Skip", path.name, flush=True)
                    continue
                raise FileExistsError(f"{path} exists; add --resume to skip completed cases.")
            info = manifest["inputs"][ds]
            if case["id"] == "align":
                prepared = read_json(run / "alignment" / ds / "prepared.json")
                if prepared["campaign_id"] != manifest["id"]:
                    raise ValueError(f"Wrong alignment input campaign for {ds}")
                info = prepared["input"]
                file_identity(info)
            scope = "cache_core" if group.endswith("core") and ds in ("min", "mid") else "pipeline"
            job = {
                "backend": backend, "mode": mode, "scope": scope, "case": case,
                "config": cfg, "dataset": ds, "input": info["path"],
                "expected_spectra": info["spectra"],
                "reference": manifest["inputs"][ds]["reference"],
                "ref_tolerance": manifest["inputs"][ds]["ref_tolerance"],
            }
            print(f'{group}: {ds} / {case["id"]} [{scope}]', flush=True)
            # Each case has its own process: one warmup, then two measurements.
            directory = run / "logs" / group / f'{ds}-{case["id"]}'
            # Remove only an incomplete worker's control files before retrying.
            if directory.exists():
                shutil.rmtree(directory)
            workers = [launch(job, directory)]
            if backend != "cardinal" and any(w["numba_threads"] != cfg["numba_threads"] for w in workers):
                raise ValueError("Unexpected Numba thread count")
            record = {"campaign_id": manifest["id"], "dataset": ds,
                      "case": case["id"], "stage": case["stage"], "backend": backend,
                      "scope": scope, "mode": mode, "parameters": parameters_for_record(job),
                      "workers": workers}
            values = ([m["sampled_peak_rss_mib"] for m in workers[0]["memory"]] if mode == "memory"
                      else workers[0]["elapsed_seconds"])
            record["stats"] = summarize_values(values)
            write_json(path, record)
            done += 1
            print(f'  saved mean={record["stats"]["mean"]:.6f} {"MiB" if mode == "memory" else "s"} ({done}/{total})', flush=True)


def parameters_for_record(job):
    p = dict(job["case"][job["backend"]])
    if job["case"]["id"] == "reference":
        p["ref"] = job["reference"]
        if job["backend"] == "numba":
            p["ref_tolerance"] = job["ref_tolerance"]
    return p


def summarize_values(values):
    return {"min": min(values), "mean": statistics.mean(values),
            "median": statistics.median(values), "max": max(values),
            "stddev": statistics.stdev(values), "rounds": len(values), "data": values}


def summarize(run, manifest):
    lines = ["# Unified benchmark results", "",
             f'Campaign: `{manifest["id"]}`. Raw results and provenance are in this directory.', "",
             "Max/Ultra core rows marked `pipeline_substitution` are pipeline measurements, not core timings.", ""]
    for group in GROUPS:
        rows = []
        backend = group.split("-", 1)[0]
        for ds in DATASETS:
            for case in manifest["config"]["cases"]:
                if backend not in case:
                    continue
                source_group = "numba-pipeline" if group == "numba-core" and ds in ("max", "ultra") else group
                path = run / source_group / f'{ds}-{case["id"]}.json'
                if not path.exists():
                    raise FileNotFoundError(f"Missing result: {path}. Finish all six campaigns (use --resume).")
                r = read_json(path)
                if r["campaign_id"] != manifest["id"]:
                    raise ValueError(f"Campaign mismatch: {path}")
                scope = r["scope"]
                if group.endswith("core") and ds in ("max", "ultra"):
                    scope = "pipeline_substitution"
                rows.append({"dataset": ds, "case": case["id"], "scope": scope,
                             "unit": "MiB" if r["mode"] == "memory" else "s",
                             **{k: v for k, v in r["stats"].items() if k != "data"},
                             "source": str(path.relative_to(run))})
        with (run / f"{group}.csv").open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        lines += [f"## {group}", "", "| Dataset | Method | Scope | Mean | Stddev | Unit | Rounds |",
                  "| --- | --- | --- | --- | --- | --- | --- |"]
        lines += [f'| {r["dataset"]} | {r["case"]} | {r["scope"]} | {r["mean"]:.6f} | {r["stddev"]:.6f} | {r["unit"]} | {r["rounds"]} |' for r in rows]
        lines.append("")
    (run / "results.md").write_text("\n".join(lines))
    print("Wrote six CSV tables and", run / "results.md")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("init", "prepare", *GROUPS, "summarize"))
    parser.add_argument("--run-dir", type=Path, default=HERE / "results" / "current")
    parser.add_argument("--dataset", nargs="+", choices=DATASETS, default=list(DATASETS))
    parser.add_argument("--case", nargs="+", choices=[c["id"] for c in read_json(HERE / "config.json")["cases"]])
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    cfg = read_json(HERE / "config.json")
    # Set before importing NumPy/Numba/R so BLAS never adds uncontrolled workers.
    for key in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        os.environ[key] = "1"
    os.environ["NUMBA_NUM_THREADS"] = str(cfg["numba_threads"])
    run = args.run_dir.resolve()
    if args.command == "init":
        initialize(run, cfg)
        return
    manifest = validate_campaign(run, cfg)
    if args.command == "prepare":
        prepare(run, manifest, args.dataset, args.resume)
    elif args.command == "summarize":
        summarize(run, manifest)
    else:
        run_group(run, manifest, args.command, args.dataset, args.case, args.resume)


if __name__ == "__main__":
    main()
