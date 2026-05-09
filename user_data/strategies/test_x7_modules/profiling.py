"""Low-overhead profiling mixin for TestX7.

Profiling is disabled unless the Freqtrade config sets
``test_x7_profile_enabled`` or the environment variable ``TEST_X7_PROFILE=1``.
"""

from __future__ import annotations

from collections import defaultdict
from contextlib import contextmanager
import logging
import os
import time
from typing import Any, Iterator

log = logging.getLogger(__name__)

_TRUE_VALUES = {"1", "true", "yes", "on"}


def _enabled_from_env(name: str) -> bool:
  return os.getenv(name, "").strip().lower() in _TRUE_VALUES


def _float_from_env(name: str, default: float) -> float:
  try:
    return float(os.getenv(name, ""))
  except ValueError:
    return default


class TestX7ProfilingMixin:
  test_x7_profile_env = "TEST_X7_PROFILE"
  test_x7_profile_slow_env = "TEST_X7_PROFILE_SLOW_SECONDS"

  def _test_x7_profile_enabled(self) -> bool:
    config_enabled = bool(getattr(self, "config", {}).get("test_x7_profile_enabled", False))
    return config_enabled or _enabled_from_env(self.test_x7_profile_env)

  def _test_x7_profile_slow_seconds(self) -> float:
    config_value = getattr(self, "config", {}).get("test_x7_profile_slow_seconds")
    if isinstance(config_value, (int, float)) and config_value >= 0:
      return float(config_value)
    return _float_from_env(self.test_x7_profile_slow_env, 0.0)

  def _test_x7_profile_store(self) -> dict[str, dict[str, float]]:
    store = getattr(self, "_test_x7_profile", None)
    if store is None:
      store = defaultdict(lambda: {"count": 0.0, "total": 0.0, "max": 0.0})
      self._test_x7_profile = store
    return store

  def _test_x7_record_stage(self, stage: str, pair: str, seconds: float) -> None:
    store = self._test_x7_profile_store()
    key = f"{stage}|{pair}"
    item = store[key]
    item["count"] += 1.0
    item["total"] += seconds
    item["max"] = max(item["max"], seconds)

    slow_seconds = self._test_x7_profile_slow_seconds()
    if slow_seconds <= 0 or seconds >= slow_seconds:
      log.info("TestX7 profile stage=%s pair=%s seconds=%.6f", stage, pair, seconds)

  @contextmanager
  def _test_x7_stage(self, stage: str, pair: str) -> Iterator[None]:
    started = time.perf_counter()
    try:
      yield
    finally:
      self._test_x7_record_stage(stage, pair, time.perf_counter() - started)

  def test_x7_profile_summary(self) -> list[dict[str, Any]]:
    summary = []
    for key, item in self._test_x7_profile_store().items():
      stage, pair = key.split("|", 1)
      count = item["count"] or 1.0
      summary.append(
        {
          "stage": stage,
          "pair": pair,
          "count": int(item["count"]),
          "total_seconds": item["total"],
          "avg_seconds": item["total"] / count,
          "max_seconds": item["max"],
        }
      )
    return sorted(summary, key=lambda row: row["total_seconds"], reverse=True)

  def analyze_pair(self, pair: str) -> None:
    if not self._test_x7_profile_enabled():
      return super().analyze_pair(pair)
    with self._test_x7_stage("analyze_pair", pair):
      return super().analyze_pair(pair)

  def populate_indicators(self, dataframe, metadata: dict):
    if not self._test_x7_profile_enabled():
      return super().populate_indicators(dataframe, metadata)
    with self._test_x7_stage("populate_indicators", metadata.get("pair", "?")):
      return super().populate_indicators(dataframe, metadata)

  def info_switcher(self, metadata: dict, info_timeframe):
    if not self._test_x7_profile_enabled():
      return super().info_switcher(metadata, info_timeframe)
    with self._test_x7_stage(f"informative_{info_timeframe}", metadata.get("pair", "?")):
      return super().info_switcher(metadata, info_timeframe)

  def btc_info_switcher(self, btc_info_pair, btc_info_timeframe, metadata: dict):
    if not self._test_x7_profile_enabled():
      return super().btc_info_switcher(btc_info_pair, btc_info_timeframe, metadata)
    with self._test_x7_stage(f"btc_informative_{btc_info_timeframe}", metadata.get("pair", "?")):
      return super().btc_info_switcher(btc_info_pair, btc_info_timeframe, metadata)

  def base_tf_5m_indicators(self, metadata: dict, dataframe):
    if not self._test_x7_profile_enabled():
      return super().base_tf_5m_indicators(metadata, dataframe)
    with self._test_x7_stage("base_5m", metadata.get("pair", "?")):
      return super().base_tf_5m_indicators(metadata, dataframe)

  def populate_entry_trend(self, dataframe, metadata: dict):
    if not self._test_x7_profile_enabled():
      return super().populate_entry_trend(dataframe, metadata)
    with self._test_x7_stage("populate_entry_trend", metadata.get("pair", "?")):
      return super().populate_entry_trend(dataframe, metadata)

  def populate_exit_trend(self, dataframe, metadata: dict):
    if not self._test_x7_profile_enabled():
      return super().populate_exit_trend(dataframe, metadata)
    with self._test_x7_stage("populate_exit_trend", metadata.get("pair", "?")):
      return super().populate_exit_trend(dataframe, metadata)
