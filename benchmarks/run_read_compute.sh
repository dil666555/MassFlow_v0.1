#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")/.."
run_dir="${1:-benchmarks/results/read-compute}"
cooldown_seconds="${BENCH_COOLDOWN_SECONDS:-300}"
export R_MAX_VSIZE=32Gb

uv sync --frozen --extra r
if [[ ! -f "$run_dir/manifest.json" ]]; then
    uv run --frozen --extra r python benchmarks/run.py init --run-dir "$run_dir"
fi
uv run --frozen --extra r python benchmarks/verify_snip.py --run-dir "$run_dir"
uv run --frozen --extra r python benchmarks/run.py prepare \
    --run-dir "$run_dir" --dataset max ultra --resume \
    --alignment-source benchmarks/results/current

run_step() {
    printf '\n[%s] Cooling down for %s seconds before %s\n' \
        "$(date '+%Y-%m-%d %H:%M:%S')" "$cooldown_seconds" "$*"
    sleep "$cooldown_seconds"
    printf '[%s] Starting %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
    uv run --frozen --extra r python benchmarks/run.py "$@" --run-dir "$run_dir" --resume
}

run_step numba-pipeline --dataset ultra --case snip
run_step python-pipeline --dataset ultra --case snip
run_step cardinal-pipeline --dataset ultra --case snip
run_step numba-core --dataset max ultra
run_step python-core --dataset max ultra

uv run --frozen --extra r python benchmarks/summarize_read_compute.py --run-dir "$run_dir"
printf '\n[%s] Read/compute and Ultra SNIP retests completed. Results: %s\n' \
    "$(date '+%Y-%m-%d %H:%M:%S')" "$run_dir"
