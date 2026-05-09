#!/usr/bin/env bash
set -euo pipefail

repeat="${TEST_X7_GATE_REPEAT:-40}"
rows="${TEST_X7_GATE_ROWS:-1200}"
max_seconds="${TEST_X7_GATE_MAX_SECONDS:-5.0}"
expected_pairs="${TEST_X7_GATE_EXPECTED_PAIRS:-80}"
output_dir="${TEST_X7_GATE_OUTPUT_DIR:-user_data/backtest_results/test_x7_v17459_80_1y}"
data_dir_host="${TEST_X7_GATE_DATA_DIR_HOST:-}"
timestamp="$(date +%Y%m%d-%H%M%S)"

host_cpus="$(nproc)"
docker_cpus="$(
  docker compose run --rm --entrypoint sh freqtrade -lc 'nproc' 2>&1 \
    | awk '/^[0-9]+$/ { value = $0 } END { if (value != "") print value; else exit 1 }'
)"
if (( docker_cpus >= 2 )); then
  default_workers=$((docker_cpus - 1))
else
  default_workers=1
fi
workers="${TEST_X7_GATE_WORKERS:-$default_workers}"
output_file="${output_dir}/testx7-live-loop-80pairs-${repeat}loops-workers${workers}-${timestamp}.txt"
data_mount_args=()
if [[ -n "$data_dir_host" ]]; then
  if [[ ! -d "$data_dir_host" ]]; then
    echo "gate=FAIL reason=missing_data_dir_host path=${data_dir_host}" >&2
    exit 2
  fi
  data_mount_args=(-v "${data_dir_host}:/work/user_data/data/binance:ro")
fi

mkdir -p "$output_dir"

echo "host_cpus=${host_cpus}"
echo "docker_cpus=${docker_cpus}"
echo "workers=${workers}"
echo "repeat=${repeat}"
echo "max_seconds=${max_seconds}"
echo "expected_pairs=${expected_pairs}"
echo "data_dir_host=${data_dir_host:-<repo-default>}"
echo "output_file=${output_file}"

docker compose run --rm \
  -e TEST_X7_STABLE_PROCESS_ANALYZE_WORKERS="$workers" \
  -v "$(pwd)":/work \
  "${data_mount_args[@]}" \
  -w /work \
  --entrypoint python3 \
  freqtrade tools/test_x7/benchmark_live_analyze.py \
  --config user_data/config-test-x7.example.json \
  --config-extra user_data/config-test-x7-80pairs.example.json \
  --config-extra user_data/config-test-x7-live-speed-safe.example.json \
  --data-dir user_data/data/binance \
  --rows "$rows" \
  --runmode dry_run \
  --repeat "$repeat" \
  --advance-window \
  --prewarm \
  --no-fingerprint \
  | tee "$output_file"

python3 - "$output_file" "$max_seconds" "$expected_pairs" <<'PY' | tee -a "$output_file"
from __future__ import annotations

import re
import statistics
import sys
from pathlib import Path

path = Path(sys.argv[1])
max_seconds = float(sys.argv[2])
expected_pairs = int(sys.argv[3])
text = path.read_text(encoding="utf-8", errors="ignore")
loops = [float(value) for value in re.findall(r"loop\d+=([0-9.]+)s", text)]
if not loops:
  print(f"gate=FAIL reason=no_loop_output file={path}")
  raise SystemExit(2)

pairs_match = re.search(r"strategy=\S+ pairs=([0-9]+)", text)
pairs = int(pairs_match.group(1)) if pairs_match else 0
if pairs < expected_pairs:
  print(f"gate=FAIL reason=insufficient_pairs pairs={pairs} expected_pairs={expected_pairs} file={path}")
  raise SystemExit(2)

over = [value for value in loops if value > max_seconds]
print(
  "gate_summary "
  f"pairs={pairs} "
  f"loops={len(loops)} "
  f"min={min(loops):.6f}s "
  f"avg={statistics.mean(loops):.6f}s "
  f"max={max(loops):.6f}s "
  f"over{max_seconds:g}={len(over)} "
  f"file={path}"
)
if over:
  print("gate=FAIL")
  raise SystemExit(1)

print("gate=PASS")
PY
