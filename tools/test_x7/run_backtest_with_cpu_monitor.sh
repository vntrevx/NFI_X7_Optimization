#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 8 ]; then
  echo "usage: $0 <container-name> <strategy> <timerange> <backtest-dir> <logfile> <cpu-log> <stdout-log> <config-extra>" >&2
  exit 2
fi

container_name="$1"
strategy="$2"
timerange="$3"
backtest_dir="$4"
logfile="$5"
cpu_log="$6"
stdout_log="$7"
config_extra="$8"

host_backtest_dir="$backtest_dir"
if [[ "$backtest_dir" == /freqtrade/* ]]; then
  host_backtest_dir="${backtest_dir#/freqtrade/}"
fi

host_logfile="$logfile"
if [[ "$logfile" == /freqtrade/* ]]; then
  host_logfile="${logfile#/freqtrade/}"
fi

mkdir -p "$(dirname "$cpu_log")" "$(dirname "$stdout_log")" "$(dirname "$host_logfile")" "$host_backtest_dir"
: > "$cpu_log"
: > "$stdout_log"
: > "$host_logfile"

docker compose run --rm --name "$container_name" \
  -e PYTHONWARNINGS="ignore::FutureWarning" \
  freqtrade backtesting \
  --userdir /freqtrade/user_data \
  --config /freqtrade/user_data/config-test-x7.example.json \
  --config "$config_extra" \
  --datadir /freqtrade/user_data/data/binance \
  --strategy "$strategy" \
  --timerange "$timerange" \
  --cache none \
  --export trades \
  --backtest-directory "$backtest_dir" \
  --logfile "$logfile" \
  > "$stdout_log" 2>&1 &

backtest_pid="$!"

while kill -0 "$backtest_pid" 2>/dev/null; do
  stats="$(docker stats --no-stream --format 'name={{.Name}} cpu={{.CPUPerc}} mem={{.MemUsage}}' "$container_name" 2>/dev/null || true)"
  if [ -n "$stats" ]; then
    printf 'ts=%s %s\n' "$(date -Is)" "$stats" >> "$cpu_log"
  fi
  sleep 15
done

wait "$backtest_pid"
