"""Behavior-gated entry optimizations for TestX7."""

from __future__ import annotations

import os
from typing import Any

_FALSE_VALUES = {"0", "false", "no", "off"}
_TRUE_VALUES = {"1", "true", "yes", "on"}


def _disabled_from_env(name: str) -> bool:
  return os.getenv(name, "").strip().lower() in _FALSE_VALUES


class TestX7EntryOptimizationMixin:
  test_x7_skip_spot_short_entry_calc_env = "TEST_X7_SKIP_SPOT_SHORT_ENTRY_CALC"
  test_x7_entry_tail_rows_env = "TEST_X7_ENTRY_TAIL_ROWS"
  test_x7_entry_return_tail_env = "TEST_X7_ENTRY_RETURN_TAIL"

  def _test_x7_skip_spot_short_entry_calc_enabled(self) -> bool:
    config = getattr(self, "config", {})
    config_value = config.get("test_x7_skip_spot_short_entry_calc", True)
    return bool(config_value) and not _disabled_from_env(self.test_x7_skip_spot_short_entry_calc_env)

  def _test_x7_trading_mode_value(self) -> str:
    trading_mode: Any = getattr(self, "config", {}).get("trading_mode", "")
    return str(getattr(trading_mode, "value", trading_mode)).lower()

  def _test_x7_should_skip_short_entry_calc(self) -> bool:
    return (
      self._test_x7_skip_spot_short_entry_calc_enabled()
      and self._test_x7_trading_mode_value() == "spot"
      and not bool(getattr(self, "can_short", False))
    )

  def _test_x7_entry_tail_rows(self) -> int:
    env_value = os.getenv(self.test_x7_entry_tail_rows_env)
    config = getattr(self, "config", {})
    config_value = config.get("test_x7_entry_tail_rows", 0)
    try:
      rows = int(env_value if env_value is not None else config_value)
    except (TypeError, ValueError):
      return 0
    return max(0, rows)

  def _test_x7_entry_return_tail_enabled(self) -> bool:
    env_value = os.getenv(self.test_x7_entry_return_tail_env)
    if env_value is not None:
      return env_value.strip().lower() in _TRUE_VALUES
    return bool(getattr(self, "config", {}).get("test_x7_entry_return_tail", False))

  def _test_x7_entry_backtest_like_runmode(self) -> bool:
    checker = getattr(self, "_test_x7_is_backtest_like_runmode", None)
    if callable(checker):
      return bool(checker())
    runmode = getattr(getattr(self, "dp", None), "runmode", None)
    value = str(getattr(runmode, "value", runmode))
    return value in {"backtest", "hyperopt", "plot", "webserver"}

  def _test_x7_populate_entry_trend_tail(self, dataframe, metadata: dict):
    rows = self._test_x7_entry_tail_rows()
    if rows <= 0 or len(dataframe) <= rows:
      return super().populate_entry_trend(dataframe, metadata)

    tail = dataframe.tail(rows).copy(deep=False)
    tail = super().populate_entry_trend(tail, metadata)
    if self._test_x7_entry_return_tail_enabled() and not self._test_x7_entry_backtest_like_runmode():
      return tail

    if "enter_long" not in dataframe:
      dataframe.loc[:, "enter_long"] = 0
    if "enter_short" not in dataframe:
      dataframe.loc[:, "enter_short"] = 0
    if "enter_tag" not in dataframe:
      dataframe.loc[:, "enter_tag"] = ""

    for column in ("enter_long", "enter_short", "enter_tag"):
      if column in tail:
        dataframe.loc[tail.index, column] = tail[column]
    return dataframe

  def populate_entry_trend(self, dataframe, metadata: dict):
    original_short_params = getattr(self, "short_entry_signal_params", None)
    if not self._test_x7_should_skip_short_entry_calc() or not original_short_params:
      return self._test_x7_populate_entry_trend_tail(dataframe, metadata)

    self.short_entry_signal_params = {key: False for key in original_short_params}
    try:
      return self._test_x7_populate_entry_trend_tail(dataframe, metadata)
    finally:
      self.short_entry_signal_params = original_short_params
