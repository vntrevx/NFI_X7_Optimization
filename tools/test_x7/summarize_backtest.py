#!/usr/bin/env python3
"""Print a compact summary for a Freqtrade backtest zip."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import zipfile


FIELDS = (
  "strategy_name",
  "timerange",
  "backtest_days",
  "total_trades",
  "profit_total",
  "profit_total_abs",
  "profit_factor",
  "winrate",
  "max_drawdown_account",
  "max_relative_drawdown",
  "max_drawdown_abs",
  "best_pair",
  "worst_pair",
  "backtest_run_start_ts",
  "backtest_run_end_ts",
)


def _result_json_name(zip_file: zipfile.ZipFile) -> str:
  candidates = [
    name
    for name in zip_file.namelist()
    if name.endswith(".json") and not name.endswith("_config.json")
  ]
  if len(candidates) != 1:
    raise RuntimeError(f"Expected one result json in {zip_file.filename}, found {candidates}")
  return candidates[0]


def main() -> int:
  parser = argparse.ArgumentParser()
  parser.add_argument("zipfile", type=Path)
  args = parser.parse_args()

  with zipfile.ZipFile(args.zipfile) as zip_file:
    data = json.loads(zip_file.read(_result_json_name(zip_file)))
  strategy_name = next(iter(data["strategy"]))
  result = data["strategy"][strategy_name]
  summary = {field: result.get(field) for field in FIELDS}
  if summary["backtest_run_start_ts"] and summary["backtest_run_end_ts"]:
    summary["runtime_seconds"] = round(
      summary["backtest_run_end_ts"] - summary["backtest_run_start_ts"],
      3,
    )
  print(json.dumps(summary, indent=2, sort_keys=True))
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
