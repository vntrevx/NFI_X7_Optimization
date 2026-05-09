"""Reusable boolean mask helpers for TestX7 vectorized logic."""

from __future__ import annotations

from pandas import DataFrame


def build_comparison_cache(df: DataFrame):
  cache = {}

  def _cmp(column: str, op: str, value: float):
    key = (column, op, value)
    result = cache.get(key)
    if result is not None:
      return result

    series = df[column]
    if op == ">":
      result = (series > value).to_numpy(dtype=bool, copy=False)
    elif op == ">=":
      result = (series >= value).to_numpy(dtype=bool, copy=False)
    elif op == "<":
      result = (series < value).to_numpy(dtype=bool, copy=False)
    elif op == "<=":
      result = (series <= value).to_numpy(dtype=bool, copy=False)
    else:
      raise ValueError(f"Unsupported comparison operator: {op}")

    cache[key] = result
    return result

  return _cmp


def build_expression_cache(df: DataFrame):
  cache = {}

  def _gt_mul(left_column: str, right_column: str, multiplier: float):
    key = ("gt_mul", left_column, right_column, float(multiplier))
    result = cache.get(key)
    if result is None:
      result = (df[left_column].to_numpy(copy=False) > (df[right_column].to_numpy(copy=False) * multiplier))
      cache[key] = result
    return result

  def _range_lt(high_column: str, low_column: str, value: float):
    key = ("range_lt", high_column, low_column, float(value))
    result = cache.get(key)
    if result is None:
      high = df[high_column].to_numpy(copy=False)
      low = df[low_column].to_numpy(copy=False)
      result = ((high - low) / low) < value
      cache[key] = result
    return result

  return _gt_mul, _range_lt
