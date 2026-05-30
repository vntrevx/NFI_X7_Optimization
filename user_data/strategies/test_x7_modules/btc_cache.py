"""BTC informative dataframe cache for TestX7.

The cache is deliberately conservative: the key includes pair, timeframe,
row count, last candle date, and the source column layout. If any of those
change, TestX7 misses the cache and rebuilds the informative dataframe.
"""

from __future__ import annotations

import logging
import os
import time
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

  def _btc_info_indicators(self, btc_info_pair: str, btc_info_timeframe: str, metadata: dict):
    dataframe = self.dp.get_pair_dataframe(btc_info_pair, btc_info_timeframe)
    key = self._test_x7_btc_cache_key(btc_info_pair, btc_info_timeframe, dataframe)
    store = self._test_x7_btc_cache_store()

    if self._test_x7_btc_cache_enabled() and key in store:
      return store[key]

    tik = time.perf_counter()
    informative = dataframe.copy()
    informative.rename(columns=lambda column: f"btc_{column}" if column != "date" else column, inplace=True)
    tok = time.perf_counter()
    log.debug("[%s] btc_info_%s_indicators took: %.4f seconds.", metadata["pair"], btc_info_timeframe, tok - tik)

    if self._test_x7_btc_cache_enabled():
      store[key] = informative
    return informative
