"""Conservative informative dataframe cache for TestX7."""

from __future__ import annotations

import os
from typing import Any

_FALSE_VALUES = {"0", "false", "no", "off"}


def _disabled_from_env(name: str) -> bool:
  return os.getenv(name, "").strip().lower() in _FALSE_VALUES


class TestX7InformativeCacheMixin:
  """Cache non-BTC informative indicator dataframes by source candle state."""

  test_x7_informative_cache_env = "TEST_X7_INFORMATIVE_CACHE"

  def _test_x7_informative_cache_enabled(self) -> bool:
    config = getattr(self, "config", {})
    config_value = config.get("test_x7_informative_cache_enabled", True)
    return bool(config_value) and not _disabled_from_env(self.test_x7_informative_cache_env)

  def _test_x7_informative_cache_store(self) -> dict[tuple[Any, ...], Any]:
    store = getattr(self, "_test_x7_informative_cache", None)
    if store is None:
      store = {}
      self._test_x7_informative_cache = store
    return store

  def _test_x7_informative_cache_key(self, pair: str, timeframe: str) -> tuple[Any, ...]:
    dataframe = self.dp.get_pair_dataframe(pair=pair, timeframe=timeframe)
    if dataframe.empty:
      last_date = None
    else:
      last_date = dataframe.iloc[-1].get("date")
      if hasattr(last_date, "isoformat"):
        last_date = last_date.isoformat()
    return (pair, timeframe, len(dataframe), last_date, tuple(str(column) for column in dataframe.columns))

  def info_switcher(self, metadata: dict, info_timeframe):
    if not self._test_x7_informative_cache_enabled():
      return super().info_switcher(metadata, info_timeframe)

    key = self._test_x7_informative_cache_key(metadata["pair"], info_timeframe)
    store = self._test_x7_informative_cache_store()
    cached = store.get(key)
    if cached is not None:
      return cached

    informative = super().info_switcher(metadata, info_timeframe)
    store[key] = informative
    return informative
