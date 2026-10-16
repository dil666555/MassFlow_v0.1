"""Collect the existing benchmark groups through pytest."""
import os
from pathlib import Path

import pytest

from run import (
    DATASETS, HERE, make_job, parameters_for_record, read_json,
    validate_campaign, write_json,
)

CONFIG = read_json(HERE / "config.json")
for name in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[name] = "1"
os.environ["NUMBA_NUM_THREADS"] = str(CONFIG["numba_threads"])


def pytest_addoption(parser):
    group = parser.getgroup("massflow-benchmarks")
    group.addoption("--bench-group", choices=("python-core", "numba-pipeline", "numba-core", "python-pipeline"))
    group.addoption("--bench-run-dir", default=str(HERE / "results" / "current"))
    group.addoption("--bench-case", action="append", choices=[c["id"] for c in CONFIG["cases"]])
    group.addoption("--bench-dataset", action="append", choices=DATASETS)
    group.addoption("--bench-resume", action="store_true")


def pytest_generate_tests(metafunc):
    if "job" not in metafunc.fixturenames:
        return
    worker_file = os.getenv("MASSFLOW_BENCHMARK_JOB")
    if worker_file:
        single = read_json(worker_file)
        jobs = {f'{single["dataset"]}-{single["case"]["id"]}': single}
    else:
        group = metafunc.config.getoption("bench_group")
        if group is None:
            raise pytest.UsageError("Choose --bench-group python-core, numba-pipeline or numba-core")
        run = Path(metafunc.config.getoption("bench_run_dir")).resolve()
        manifest = validate_campaign(run, CONFIG)
        backend = group.split("-", 1)[0]
        selected = metafunc.config.getoption("bench_case")
        cases = [c for c in CONFIG["cases"] if backend in c and (not selected or c["id"] in selected)]
        if not cases:
            raise pytest.UsageError(f"No supported cases for {group}: {selected}")
        datasets = metafunc.config.getoption("bench_dataset") or DATASETS
        jobs = {}
        for ds in datasets:
            for case in cases:
                path = run / group / f'{ds}-{case["id"]}.json'
                if path.exists():
                    if metafunc.config.getoption("bench_resume"):
                        if read_json(path)["campaign_id"] != manifest["id"]:
                            raise pytest.UsageError(f"Campaign mismatch: {path}")
                        continue
                    raise pytest.UsageError(f"{path} exists; use --bench-resume")
                jobs[f'{ds}-{case["id"]}'] = make_job(run, manifest, group, ds, case)
    metafunc.config._massflow_jobs = jobs
    metafunc.parametrize("job", list(jobs), indirect=True, ids=list(jobs))


@pytest.fixture
def job(request):
    return request.config._massflow_jobs[request.param]


def pytest_benchmark_update_json(config, benchmarks, output_json):
    if os.getenv("MASSFLOW_BENCHMARK_JOB"):
        return  # The isolated-process controller saves this worker's result.
    jobs = getattr(config, "_massflow_jobs", {})
    for entry in output_json["benchmarks"]:
        job = jobs[entry["params"]["job"]]
        stats = entry["stats"]
        if stats["rounds"] != job["config"]["rounds"]:
            continue  # An interrupted case must not become a completed resume entry.
        worker = dict(entry["extra_info"]["worker"], elapsed_seconds=stats["data"])
        record = {
            "campaign_id": job["campaign_id"], "dataset": job["dataset"],
            "case": job["case"]["id"], "stage": job["case"]["stage"],
            "backend": job["backend"], "scope": job["scope"], "mode": "time",
            "parameters": parameters_for_record(job), "workers": [worker],
            "stats": {key: stats[key] for key in
                      ("min", "mean", "median", "max", "stddev", "rounds", "data")},
        }
        write_json(job["save_path"], record)
