"""BTC informative dataframe cache for TestX7.

The cache is deliberately conservative: the key includes pair, timeframe,
row count, last candle date, and the source column layout. If any of those
change, TestX7 misses the cache and rebuilds the informative dataframe.
"""

from __future__ import annotations

import logging
import os
from typing import Any

log = logging.getLogger(__name__)

_FALSE_VALUES = {"0", "false", "no", "off"}


def _disabled_from_env(name: str) -> bool:
  return os.getenv(name, "").strip().lower() in _FALSE_VALUES


class TestX7BtcInformativeCacheMixin:
  test_x7_btc_cache_disable_env = "TEST_X7_BTC_CACHE"

  def _test_x7_btc_cache_enabled(self) -> bool:
    config = getattr(self, "config", {})
    config_value = config.get("test_x7_btc_cache_enabled", True)
    return bool(config_value) and not _disabled_from_env(self.test_x7_btc_cache_disable_env)

  def _test_x7_btc_cache_store(self) -> dict[tuple[Any, ...], Any]:
    store = getattr(self, "_test_x7_btc_cache", None)
    if store is None:
      store = {}
      self._test_x7_btc_cache = store
    return store

  def _test_x7_btc_cache_key(self, pair: str, timeframe: str, dataframe) -> tuple[Any, ...]:
    if dataframe.empty:
      last_date = None
    else:
      last_date = dataframe.iloc[-1].get("date")
      if hasattr(last_date, "isoformat"):
        last_date = last_date.isoformat()
    return (pair, timeframe, len(dataframe), last_date, tuple(str(column) for column in dataframe.columns))

  def _test_x7_build_btc_informative(self, btc_info_pair: str, btc_info_timeframe: str):
    dataframe = self.dp.get_pair_dataframe(btc_info_pair, btc_info_timeframe)
    informative = dataframe.copy()
    informative.rename(columns=lambda s: f"btc_{s}" if s != "date" else s, inplace=True)
    return dataframe, informative

  def _test_x7_btc_informative(self, btc_info_pair: str, btc_info_timeframe: str):
    dataframe = self.dp.get_pair_dataframe(btc_info_pair, btc_info_timeframe)
    key = self._test_x7_btc_cache_key(btc_info_pair, btc_info_timeframe, dataframe)
    store = self._test_x7_btc_cache_store()

    if self._test_x7_btc_cache_enabled() and key in store:
      return store[key]

    informative = dataframe.copy()
    informative.rename(columns=lambda s: f"btc_{s}" if s != "date" else s, inplace=True)
    if self._test_x7_btc_cache_enabled():
      store[key] = informative
    return informative

  def btc_info_1d_indicators(self, btc_info_pair, btc_info_timeframe, metadata: dict):
    return self._test_x7_btc_informative(btc_info_pair, btc_info_timeframe)

  def btc_info_4h_indicators(self, btc_info_pair, btc_info_timeframe, metadata: dict):
    return self._test_x7_btc_informative(btc_info_pair, btc_info_timeframe)

  def btc_info_1h_indicators(self, btc_info_pair, btc_info_timeframe, metadata: dict):
    return self._test_x7_btc_informative(btc_info_pair, btc_info_timeframe)

  def btc_info_15m_indicators(self, btc_info_pair, btc_info_timeframe, metadata: dict):
    return self._test_x7_btc_informative(btc_info_pair, btc_info_timeframe)

  def btc_info_5m_indicators(self, btc_info_pair, btc_info_timeframe, metadata: dict):
    return self._test_x7_btc_informative(btc_info_pair, btc_info_timeframe)
