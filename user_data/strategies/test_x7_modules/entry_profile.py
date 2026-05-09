"""Optional line-level profiler for TestX7 entry trend work.

This profiler is disabled by default. It is too expensive for normal backtests
or live trading, but it gives a safe diagnostic step for the very large
upstream ``populate_entry_trend`` method.
"""

from __future__ import annotations

from collections import defaultdict
import linecache
import logging
import os
from pathlib import Path
import sys
import time
from types import FrameType
from typing import Any, Callable

log = logging.getLogger(__name__)

_TRUE_VALUES = {"1", "true", "yes", "on"}


def _enabled_from_env(name: str) -> bool:
  return os.getenv(name, "").strip().lower() in _TRUE_VALUES


def _positive_int(value: Any, default: int) -> int:
  try:
    parsed = int(value)
  except (TypeError, ValueError):
    return default
  return parsed if parsed > 0 else default


class _EntryLineTimer:
  def __init__(self, target_filename: str, target_function: str) -> None:
    self.target_filename = Path(target_filename).name
    self.target_function = target_function
    self.timings: dict[int, float] = defaultdict(float)
    self._last_line: int | None = None
    self._last_ts: float | None = None

  def _is_target(self, frame: FrameType) -> bool:
    return (
      Path(frame.f_code.co_filename).name == self.target_filename
      and frame.f_code.co_name == self.target_function
    )

  def _record_elapsed(self, now: float) -> None:
    if self._last_line is not None and self._last_ts is not None:
      self.timings[self._last_line] += now - self._last_ts

  def trace(self, frame: FrameType, event: str, arg: Any) -> Callable | None:
    if event not in {"line", "return"}:
      return self.trace

    now = time.perf_counter()
    if self._is_target(frame):
      self._record_elapsed(now)
      if event == "line":
        self._last_line = frame.f_lineno
        self._last_ts = now
      else:
        self._last_line = None
        self._last_ts = None
    return self.trace


class TestX7EntryLineProfilerMixin:
  test_x7_entry_line_profile_env = "TEST_X7_ENTRY_LINE_PROFILE"
  test_x7_entry_line_profile_lines_env = "TEST_X7_ENTRY_LINE_PROFILE_LINES"
  test_x7_indicator_line_profile_env = "TEST_X7_INDICATOR_LINE_PROFILE"

  def _test_x7_entry_line_profile_enabled(self) -> bool:
    config = getattr(self, "config", {})
    config_enabled = bool(config.get("test_x7_entry_line_profile_enabled", False))
    return config_enabled or _enabled_from_env(self.test_x7_entry_line_profile_env)

  def _test_x7_entry_line_profile_top_n(self) -> int:
    config = getattr(self, "config", {})
    config_value = config.get("test_x7_entry_line_profile_top_n")
    env_value = os.getenv(self.test_x7_entry_line_profile_lines_env)
    return _positive_int(env_value, _positive_int(config_value, 20))

  def _test_x7_entry_source_file(self) -> str:
    for cls in type(self).mro():
      if cls.__name__ == "TestX7EntryLogicMixin":
        return sys.modules[cls.__module__].__file__
    for cls in type(self).mro():
      if cls.__name__ == "NostalgiaForInfinityX7":
        return sys.modules[cls.__module__].__file__
    raise RuntimeError("TestX7 entry logic source was not found in TestX7 MRO")

  def _test_x7_indicator_source_file(self) -> str:
    for cls in type(self).mro():
      if cls.__name__ == "TestX7IndicatorLogicMixin":
        return sys.modules[cls.__module__].__file__
    raise RuntimeError("TestX7 indicator logic source was not found in TestX7 MRO")

  def _test_x7_log_entry_line_profile(self, pair: str, source: str, timer: _EntryLineTimer, total_seconds: float) -> None:
    top_n = self._test_x7_entry_line_profile_top_n()
    ranked = sorted(timer.timings.items(), key=lambda item: item[1], reverse=True)[:top_n]
    log.info(
      "TestX7 entry-line-profile pair=%s total=%.6f tracked_lines=%d top_n=%d",
      pair,
      total_seconds,
      len(timer.timings),
      top_n,
    )
    for line_number, seconds in ranked:
      text = linecache.getline(source, line_number).strip()
      log.info(
        "TestX7 entry-line-profile pair=%s line=%d seconds=%.6f code=%s",
        pair,
        line_number,
        seconds,
        text,
      )

  def populate_entry_trend(self, dataframe, metadata: dict):
    if not self._test_x7_entry_line_profile_enabled():
      return super().populate_entry_trend(dataframe, metadata)

    source = self._test_x7_entry_source_file()
    timer = _EntryLineTimer(source, "populate_entry_trend")
    previous_trace = sys.gettrace()
    started = time.perf_counter()
    sys.settrace(timer.trace)
    try:
      return super().populate_entry_trend(dataframe, metadata)
    finally:
      sys.settrace(previous_trace)
      self._test_x7_log_entry_line_profile(metadata.get("pair", "?"), source, timer, time.perf_counter() - started)

  def populate_indicators(self, dataframe, metadata: dict):
    if not _enabled_from_env(self.test_x7_indicator_line_profile_env):
      return super().populate_indicators(dataframe, metadata)

    source = self._test_x7_indicator_source_file()
    timer = _EntryLineTimer(source, "populate_indicators")
    previous_trace = sys.gettrace()
    started = time.perf_counter()
    sys.settrace(timer.trace)
    try:
      return super().populate_indicators(dataframe, metadata)
    finally:
      sys.settrace(previous_trace)
      self._test_x7_log_entry_line_profile(metadata.get("pair", "?"), source, timer, time.perf_counter() - started)
