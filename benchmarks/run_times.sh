#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")/.."
run_dir="${1:-benchmarks/results/current}"
cooldown_seconds="${BENCH_COOLDOWN_SECONDS:-300}"
export R_MAX_VSIZE=32Gb

uv sync --frozen --extra r

if [[ ! -f "$run_dir/manifest.json" ]]; then
    uv run --frozen --extra r python benchmarks/run.py init --run-dir "$run_dir"
fi
Rscript --vanilla - "$run_dir/cardinal-runtime-32gb.json" <<'RS'
suppressPackageStartupMessages(library(Cardinal))
suppressPackageStartupMessages(library(jsonlite))
bp <- getCardinalBPPARAM()
registered <- BiocParallel::bpparam()
policy <- list(
    recorded_at = format(Sys.time(), tz = "UTC", usetz = TRUE),
    R_MAX_VSIZE = Sys.getenv("R_MAX_VSIZE"),
    vector_heap_limit_mib = mem.maxVSize(),
    cardinal_backend = if (is.null(bp)) "serial (BPPARAM=NULL)" else class(bp)[[1]],
    cardinal_workers = if (is.null(bp)) 1L else BiocParallel::bpworkers(bp),
    registered_backend = class(registered)[[1]],
    registered_workers = BiocParallel::bpworkers(registered),
    note = "32 GiB limit applies to remaining R jobs; completed results are retained. Legacy worker JSON reports the registered backend, not Cardinal's effective backend."
)
path <- commandArgs(trailingOnly = TRUE)[[1]]
if (!file.exists(path)) write_json(policy, path, auto_unbox = TRUE, pretty = TRUE)
cat("R vector heap limit:", policy$vector_heap_limit_mib, "MiB; Cardinal:",
    policy$cardinal_backend, "workers:", policy$cardinal_workers, "\n")
RS
uv run --frozen --extra r python benchmarks/reuse_python_core.py --run-dir "$run_dir"
uv run --frozen --extra r python benchmarks/run.py prepare --run-dir "$run_dir" --resume

run_step() {
    printf '\n[%s] Cooling down for %s seconds before %s\n' \
        "$(date '+%Y-%m-%d %H:%M:%S')" "$cooldown_seconds" "$*"
    sleep "$cooldown_seconds"
    printf '[%s] Starting %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
    uv run --frozen --extra r python benchmarks/run.py "$@" --run-dir "$run_dir" --resume
}

run_step numba-pipeline
run_step numba-core --dataset min mid
run_step cardinal-pipeline
run_step python-core --dataset min mid
run_step python-core --dataset max ultra
run_step numba-memory
run_step cardinal-memory

printf '\n[%s] All seven time and memory steps completed. JSON: %s/{python-core,numba-pipeline,numba-core,cardinal-pipeline,numba-memory,cardinal-memory}/\n' \
    "$(date '+%Y-%m-%d %H:%M:%S')" "$run_dir"
