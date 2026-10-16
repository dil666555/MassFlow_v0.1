"""Reuse the two M5 Python SNIP core measurements from the original branch."""
import argparse
import json
import os
from pathlib import Path
import subprocess

from run import HERE, ROOT, read_json, validate_campaign, write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, default=HERE / "results" / "current")
    args = parser.parse_args()
    run = args.run_dir.resolve()
    cfg = read_json(HERE / "config.json")
    for key in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        os.environ[key] = "1"
    os.environ["NUMBA_NUM_THREADS"] = str(cfg["numba_threads"])
    manifest = validate_campaign(run, cfg)

    ref = "test/time_and_memory_of_three_version"
    source = "10-15-重测部分内容/S11-SNIP-min-mid-m5.json"
    commit = subprocess.check_output(
        ["git", "rev-parse", ref], cwd=ROOT, text=True,
    ).strip()
    report = json.loads(subprocess.check_output(
        ["git", "show", f"{commit}:{source}"], cwd=ROOT, text=True,
    ))
    machine = report["machine_info"]
    env = manifest["environment"]
    if (machine["node"] != env["host"] or machine["machine"] != env["machine"]
            or machine["cpu"]["count"] != env["logical_cpus"]
            or machine["python_version"] != env["python"].split()[0]):
        raise ValueError("The archived SNIP report is from a different machine/Python; do not reuse it.")
    case = next(c for c in cfg["cases"] if c["id"] == "snip")
    expected = {"method": "snip", "m": 5, "decreasing": True, "smooth": "none"}
    if case["python"] != expected or cfg["batch_size"] != 256 or cfg["warmup"] != 1:
        raise ValueError("Current SNIP parameters differ from the archived test.")

    archive = run / "imports" / "python-core-snip-m5.json"
    write_json(archive, report)
    for ds in ("min", "mid"):
        target = run / "python-core" / f"{ds}-snip.json"
        if target.exists():
            if read_json(target)["campaign_id"] != manifest["id"]:
                raise ValueError(f"Campaign mismatch: {target}")
            print("Keep completed", target)
            continue
        entry = next(e for e in report["benchmarks"]
                     if e["params"]["ms_raw_data"] == manifest["inputs"][ds]["path"]
                     and e["params"]["method"] == "snip")
        stats = entry["stats"]
        if stats["rounds"] != cfg["rounds"] or stats["iterations"] != 1:
            raise ValueError(f"Archived SNIP repeat count differs: {ds}")
        write_json(target, {
            "campaign_id": manifest["id"], "dataset": ds, "case": "snip",
            "stage": case["stage"], "backend": "python", "scope": "cache_core_legacy",
            "mode": "time", "parameters": dict(expected, width=5),
            "workers": [{"elapsed_seconds": stats["data"]}],
            "stats": {k: stats[k] for k in
                      ("min", "mean", "median", "max", "stddev", "rounds", "data")},
            "reused_result": True,
            "source": {"git_commit": commit, "path": source,
                       "archive": str(archive.relative_to(run)),
                       "measurement_datetime": report["datetime"],
                       "measurement_commit_info": report["commit_info"],
                       "machine_info": machine,
                       "timing_scope": "Original speed_process over preloaded spectra; includes batch-generator and runtime-setup overhead.",
                       "limitations": "Original report lacks library versions, input fingerprints, and thermal-state records."},
        })
        print("Reused M5 Python core SNIP", ds, flush=True)


if __name__ == "__main__":
    main()
