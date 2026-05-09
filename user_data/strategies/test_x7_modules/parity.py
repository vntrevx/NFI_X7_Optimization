"""Small helpers for comparing original X7 and TestX7 trade surfaces."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


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


@dataclass(frozen=True)
class ParityResult:
  equal: bool
  left_count: int
  right_count: int
  first_difference: dict[str, Any] | None


def normalize_trade(trade: dict[str, Any]) -> dict[str, Any]:
  normalized = {field: trade.get(field) for field in TRADE_FIELDS}
  for numeric_field in ("profit_ratio", "profit_abs"):
    value = normalized.get(numeric_field)
    if isinstance(value, (int, float)):
      normalized[numeric_field] = round(float(value), 10)
  return normalized


def compare_trades(left: list[dict[str, Any]], right: list[dict[str, Any]]) -> ParityResult:
  left_norm = [normalize_trade(trade) for trade in left]
  right_norm = [normalize_trade(trade) for trade in right]

  for index, (left_trade, right_trade) in enumerate(zip(left_norm, right_norm)):
    if left_trade != right_trade:
      return ParityResult(
        equal=False,
        left_count=len(left_norm),
        right_count=len(right_norm),
        first_difference={"index": index, "left": left_trade, "right": right_trade},
      )

  equal = len(left_norm) == len(right_norm)
  first_difference = None if equal else {"index": min(len(left_norm), len(right_norm)), "left": None, "right": None}
  return ParityResult(equal=equal, left_count=len(left_norm), right_count=len(right_norm), first_difference=first_difference)
