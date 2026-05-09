#!/usr/bin/env python3
"""Compare two Freqtrade backtest zip files at the trade surface."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import zipfile


TRADE_FIELDS = (
  "pair",
  "is_short",
  "open_date",
  "close_date",
  "enter_tag",
  "exit_reason",
  "profit_ratio",
  "profit_abs",
)


SUMMARY_FIELDS = (
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


def load_strategy_result(path: Path) -> tuple[str, dict]:
  with zipfile.ZipFile(path) as zip_file:
    data = json.loads(zip_file.read(_result_json_name(zip_file)))
  strategies = data.get("strategy", {})
  if len(strategies) != 1:
    raise RuntimeError(f"Expected one strategy in {path}, found {list(strategies)}")
  strategy_name = next(iter(strategies))
  return strategy_name, strategies[strategy_name]


def normalize_trade(trade: dict) -> dict:
  normalized = {field: trade.get(field) for field in TRADE_FIELDS}
  for field in ("profit_ratio", "profit_abs"):
    if isinstance(normalized[field], (int, float)):
      normalized[field] = round(float(normalized[field]), 10)
  return normalized


def compare(left: dict, right: dict) -> tuple[bool, dict | None]:
  left_trades = [normalize_trade(trade) for trade in left.get("trades", [])]
  right_trades = [normalize_trade(trade) for trade in right.get("trades", [])]
  for index, (left_trade, right_trade) in enumerate(zip(left_trades, right_trades)):
    if left_trade != right_trade:
      return False, {"index": index, "left": left_trade, "right": right_trade}
  if len(left_trades) != len(right_trades):
    return False, {"left_count": len(left_trades), "right_count": len(right_trades)}
  return True, None


def main() -> int:
  parser = argparse.ArgumentParser()
  parser.add_argument("left", type=Path)
  parser.add_argument("right", type=Path)
  parser.add_argument("--json", action="store_true", help="Print machine-readable output.")
  args = parser.parse_args()

  left_name, left = load_strategy_result(args.left)
  right_name, right = load_strategy_result(args.right)
  equal, first_difference = compare(left, right)
  result = {
    "left_strategy": left_name,
    "right_strategy": right_name,
    "trade_surface_equal": equal,
    "left_summary": {field: left.get(field) for field in SUMMARY_FIELDS},
    "right_summary": {field: right.get(field) for field in SUMMARY_FIELDS},
    "first_difference": first_difference,
  }

  if args.json:
    print(json.dumps(result, indent=2, sort_keys=True))
  else:
    print(f"left_strategy={left_name}")
    print(f"right_strategy={right_name}")
    print(f"trade_surface_equal={equal}")
    print(f"left_total_trades={left.get('total_trades')}")
    print(f"right_total_trades={right.get('total_trades')}")
    if first_difference is not None:
      print(json.dumps(first_difference, indent=2, sort_keys=True))
  return 0 if equal else 1


if __name__ == "__main__":
  sys.exit(main())
