"""Extracted indicator and informative-timeframe logic for TestX7.

This file is a behavior-preserving extraction from the synced upstream
NostalgiaForInfinityX7 baseline. Keep changes mechanical and parity-checked.
"""

from __future__ import annotations

import logging
import os
import time

import numpy as np
import pandas as pd
import talib.abstract as ta
from pandas import DataFrame

from test_x7_modules.merge import fast_merge_informative_pair as merge_informative_pair
from test_x7_modules.masks import build_comparison_cache, build_expression_cache

log = logging.getLogger(__name__)
_TRUE_VALUES = {"1", "true", "yes", "on"}
_FALSE_VALUES = {"0", "false", "no", "off"}


def _drop_existing_columns(df: DataFrame, columns: list[str]) -> DataFrame:
  return df.drop(columns=df.columns.intersection(columns))


def _non_zero_range(high, low):
  diff = high - low
  if hasattr(diff, "eq"):
    has_zero = diff.eq(0).any().any()
  else:
    has_zero = np.equal(diff, 0).any()
  if has_zero:
    diff += np.finfo(float).eps
  return diff


def _stoch_k(high, low, close, k: int = 14, smooth_k: int = 3):
  lowest_low = low.rolling(k).min()
  highest_high = high.rolling(k).max()
  stoch = 100.0 * (close - lowest_low) / _non_zero_range(highest_high, lowest_low)
  return stoch.rolling(smooth_k).mean()


def _stochrsi_k_from_rsi(rsi, length: int = 14, smooth_k: int = 3):
  lowest_rsi = rsi.rolling(length).min()
  highest_rsi = rsi.rolling(length).max()
  stoch = 100.0 * (rsi - lowest_rsi) / _non_zero_range(highest_rsi, lowest_rsi)
  return stoch.rolling(smooth_k).mean()


def _cmf(dataframe: DataFrame, length: int = 20):
  money_flow_volume = (
    ((dataframe["close"] - dataframe["low"]) - (dataframe["high"] - dataframe["close"]))
    / _non_zero_range(dataframe["high"], dataframe["low"])
    * dataframe["volume"]
  )
  return money_flow_volume.rolling(length).sum() / dataframe["volume"].rolling(length).sum()


def _kst(close):
  rocma1 = (100.0 * (close / close.shift(10) - 1.0)).rolling(10).mean()
  rocma2 = (100.0 * (close / close.shift(15) - 1.0)).rolling(10).mean()
  rocma3 = (100.0 * (close / close.shift(20) - 1.0)).rolling(10).mean()
  rocma4 = (100.0 * (close / close.shift(30) - 1.0)).rolling(15).mean()
  kst = 100.0 * (rocma1 + 2.0 * rocma2 + 3.0 * rocma3 + 4.0 * rocma4)
  return kst, kst.rolling(9).mean()


class TestX7IndicatorLogicMixin:
  test_x7_indicator_tail_rows_env = "TEST_X7_INDICATOR_TAIL_ROWS"
  test_x7_base_indicator_tail_rows_env = "TEST_X7_BASE_INDICATOR_TAIL_ROWS"
  test_x7_indicator_return_tail_env = "TEST_X7_INDICATOR_RETURN_TAIL"
  test_x7_skip_spot_short_protection_calc_env = "TEST_X7_SKIP_SPOT_SHORT_PROTECTION_CALC"

  def _test_x7_is_backtest_like_runmode(self) -> bool:
    runmode = getattr(getattr(self, "dp", None), "runmode", None)
    value = str(getattr(runmode, "value", runmode))
    return value in {"backtest", "hyperopt", "plot", "webserver"}

  def _test_x7_indicator_tail_rows(self) -> int:
    config = getattr(self, "config", {})
    env_value = os.getenv(self.test_x7_indicator_tail_rows_env)
    config_value = config.get("test_x7_indicator_tail_rows", 0)
    try:
      rows = int(env_value if env_value is not None else config_value)
    except (TypeError, ValueError):
      return 0
    return max(0, rows)

  def _test_x7_base_indicator_tail_rows(self) -> int:
    config = getattr(self, "config", {})
    env_value = os.getenv(self.test_x7_base_indicator_tail_rows_env)
    config_value = config.get("test_x7_base_indicator_tail_rows", 0)
    try:
      rows = int(env_value if env_value is not None else config_value)
    except (TypeError, ValueError):
      return 0
    return max(0, rows)

  def _test_x7_indicator_return_tail_enabled(self) -> bool:
    env_value = os.getenv(self.test_x7_indicator_return_tail_env)
    if env_value is not None:
      return env_value.strip().lower() in _TRUE_VALUES
    return bool(getattr(self, "config", {}).get("test_x7_indicator_return_tail", False))

  def _test_x7_skip_spot_short_protection_calc_enabled(self) -> bool:
    config = getattr(self, "config", {})
    config_value = config.get("test_x7_skip_spot_short_protection_calc", True)
    env_value = os.getenv(self.test_x7_skip_spot_short_protection_calc_env)
    if env_value is not None:
      return env_value.strip().lower() not in _FALSE_VALUES
    return bool(config_value)

  def _test_x7_should_skip_short_protection_calc(self) -> bool:
    trading_mode = str(getattr(getattr(self, "config", {}).get("trading_mode", ""), "value", getattr(self, "config", {}).get("trading_mode", ""))).lower()
    return (
      self._test_x7_skip_spot_short_protection_calc_enabled()
      and trading_mode == "spot"
      and not bool(getattr(self, "can_short", False))
    )

  def _test_x7_maybe_tail_base_indicator_input(self, df: DataFrame) -> DataFrame:
    rows = self._test_x7_base_indicator_tail_rows()
    if rows <= 0 or self._test_x7_is_backtest_like_runmode() or len(df) <= rows:
      return df
    return df.tail(rows).copy(deep=False)

  def _test_x7_restore_tail_protections(self, full_df: DataFrame | None, tail_df: DataFrame) -> DataFrame:
    if full_df is None:
      return tail_df
    if self._test_x7_indicator_return_tail_enabled() and not self._test_x7_is_backtest_like_runmode():
      return tail_df

    protection_columns = [
      "protections_long_global",
      "global_protections_long_pump",
      "global_protections_long_dump",
      "protections_long_rebuy",
      "protections_short_global",
      "global_protections_short_pump",
      "global_protections_short_dump",
      "protections_short_rebuy",
    ]
    for column in protection_columns:
      if column in tail_df:
        full_df.loc[tail_df.index, column] = tail_df[column]
    return full_df

  def informative_pairs(self):
    # get access to all pairs available in whitelist.
    pairs = self.dp.current_whitelist()
    # Assign tf to each pair so they can be downloaded and cached for strategy.
    informative_pairs = []
    for info_timeframe in self.info_timeframes:
      informative_pairs.extend([(pair, info_timeframe) for pair in pairs])

    if self.config["stake_currency"] in [
      "USDT",
      "BUSD",
      "USDC",
      "DAI",
      "TUSD",
      "FDUSD",
      "PAX",
      "USD",
      "EUR",
      "GBP",
      "TRY",
    ]:
      if ("trading_mode" in self.config) and (self.config["trading_mode"] in ["futures", "margin"]):
        btc_info_pair = f"BTC/{self.config['stake_currency']}:{self.config['stake_currency']}"
      else:
        btc_info_pair = f"BTC/{self.config['stake_currency']}"
    else:
      if ("trading_mode" in self.config) and (self.config["trading_mode"] in ["futures", "margin"]):
        btc_info_pair = "BTC/USDT:USDT"
      else:
        btc_info_pair = "BTC/USDT"

    informative_pairs.extend([(btc_info_pair, btc_info_timeframe) for btc_info_timeframe in self.btc_info_timeframes])

    return informative_pairs

  # Informative 1d Timeframe Indicators
  # ---------------------------------------------------------------------------------------------
  def informative_1d_indicators(self, metadata: dict, info_timeframe) -> DataFrame:
    tik = time.perf_counter()
    assert self.dp, "DataProvider is required for multiple timeframes."
    # Get the informative pair
    informative_1d = self.dp.get_pair_dataframe(pair=metadata["pair"], timeframe=info_timeframe)

    # Indicators
    # -----------------------------------------------------------------------------------------
    # informative_1d_indicators_pandas_ta = pta.Strategy(
    #   name="informative_1d_indicators_pandas_ta",
    #   ta=[
    #     # RSI
    #     {"kind": "rsi", "length": 3},
    #     {"kind": "rsi", "length": 14},
    #     # {"kind": "rsi", "length": 20},
    #     # EMA
    #     # {"kind": "ema", "length": 12},
    #     # {"kind": "ema", "length": 16},
    #     # {"kind": "ema", "length": 20},
    #     # {"kind": "ema", "length": 26},
    #     # {"kind": "ema", "length": 50},
    #     # {"kind": "ema", "length": 100},
    #     # {"kind": "ema", "length": 200},
    #     # SMA
    #     # {"kind": "sma", "length": 16},
    #     # MFI
    #     {"kind": "mfi"},
    #     # CMF
    #     {"kind": "cmf"},
    #     # Williams %R
    #     {"kind": "willr", "length": 14},
    #     # STOCHRSI
    #     {"kind": "stochrsi"},
    #     # KST
    #     {"kind": "kst"},
    #     # ROC
    #     {"kind": "roc"},
    #     # AROON
    #     {"kind": "aroon"},
    #   ],
    # )
    # informative_1d.ta.study(informative_1d_indicators_pandas_ta, cores=self.num_cores_indicators_calc)
    # RSI
    informative_1d["RSI_3"] = ta.RSI(informative_1d, timeperiod=3)
    informative_1d["RSI_14"] = ta.RSI(informative_1d, timeperiod=14)
    informative_1d["RSI_3_change_pct"] = (
      informative_1d["RSI_3"].fillna(float("nan")).pct_change(fill_method=None) * 100.0
    )
    # MFI
    informative_1d["MFI_14"] = ta.MFI(informative_1d, timeperiod=14)
    # CMF
    informative_1d["CMF_20"] = _cmf(informative_1d, length=20)
    # Williams %R
    informative_1d["WILLR_14"] = ta.WILLR(informative_1d, timeperiod=14)
    # AROON
    aroon_14 = ta.AROON(informative_1d, timeperiod=14)
    informative_1d["AROONU_14"] = aroon_14["aroonup"] if isinstance(aroon_14, pd.DataFrame) else np.nan
    informative_1d["AROOND_14"] = aroon_14["aroondown"] if isinstance(aroon_14, pd.DataFrame) else np.nan
    # Stochastic
    try:
      informative_1d["STOCHk_14_3_3"] = _stoch_k(informative_1d["high"], informative_1d["low"], informative_1d["close"])
    except AttributeError:
      informative_1d["STOCHk_14_3_3"] = np.nan
    # Stochastic RSI
    informative_1d["STOCHRSIk_14_14_3_3"] = _stochrsi_k_from_rsi(informative_1d["RSI_14"])
    # ROC
    informative_1d["ROC_2"] = ta.ROC(informative_1d, timeperiod=2)
    informative_1d["ROC_9"] = ta.ROC(informative_1d, timeperiod=9)
    # Candle change
    informative_1d["change_pct"] = (informative_1d["close"] - informative_1d["open"]) / informative_1d["open"] * 100.0
    # Wicks
    informative_1d["top_wick_pct"] = (
      (informative_1d["high"] - np.maximum(informative_1d["open"], informative_1d["close"]))
      / np.maximum(informative_1d["open"], informative_1d["close"])
      * 100.0
    )
    informative_1d["bot_wick_pct"] = abs(
      (informative_1d["low"] - np.minimum(informative_1d["open"], informative_1d["close"]))
      / np.minimum(informative_1d["open"], informative_1d["close"])
      * 100.0
    )
    # Max highs
    informative_1d["high_max_6"] = informative_1d["high"].rolling(6).max()
    informative_1d["high_max_12"] = informative_1d["high"].rolling(12).max()
    informative_1d["high_max_20"] = informative_1d["high"].rolling(20).max()
    informative_1d["high_max_30"] = informative_1d["high"].rolling(30).max()
    # Max lows
    informative_1d["low_min_6"] = informative_1d["low"].rolling(6).min()
    informative_1d["low_min_12"] = informative_1d["low"].rolling(12).min()
    informative_1d["low_min_20"] = informative_1d["low"].rolling(20).min()
    informative_1d["low_min_30"] = informative_1d["low"].rolling(30).min()

    # Performance logging
    # -----------------------------------------------------------------------------------------
    tok = time.perf_counter()
    log.debug(f"[{metadata['pair']}] informative_1d_indicators took: {tok - tik:0.4f} seconds.")

    return informative_1d

  # Informative 4h Timeframe Indicators
  # ---------------------------------------------------------------------------------------------
  def informative_4h_indicators(self, metadata: dict, info_timeframe) -> DataFrame:
    tik = time.perf_counter()
    assert self.dp, "DataProvider is required for multiple timeframes."
    # Get the informative pair
    informative_4h = self.dp.get_pair_dataframe(pair=metadata["pair"], timeframe=info_timeframe)

    # Indicators
    # -----------------------------------------------------------------------------------------
    # informative_4h_indicators_pandas_ta = pta.Strategy(
    #   name="informative_4h_indicators_pandas_ta",
    #   ta=[
    #     # RSI
    #     {"kind": "rsi", "length": 3},
    #     {"kind": "rsi", "length": 14},
    #     # {"kind": "rsi", "length": 20},
    #     # EMA
    #     {"kind": "ema", "length": 12},
    #     # {"kind": "ema", "length": 16},
    #     # {"kind": "ema", "length": 20},
    #     {"kind": "ema", "length": 26},
    #     # {"kind": "ema", "length": 50},
    #     # {"kind": "ema", "length": 100},
    #     {"kind": "ema", "length": 200},
    #     # SMA
    #     # {"kind": "sma", "length": 16},
    #     # BB 20 - STD2
    #     {"kind": "bbands", "length": 20},
    #     # MFI
    #     {"kind": "mfi"},
    #     # CMF
    #     {"kind": "cmf"},
    #     # Williams %R
    #     {"kind": "willr", "length": 14},
    #     # CTI
    #     {"kind": "cti", "length": 20},
    #     # STOCHRSI
    #     {"kind": "stochrsi"},
    #     # KST
    #     {"kind": "kst"},
    #     # ROC
    #     {"kind": "roc"},
    #     # AROON
    #     {"kind": "aroon"},
    #     # UO
    #     {"kind": "uo"},
    #     # AO
    #     {"kind": "ao"},
    #   ],
    # )
    # informative_4h.ta.study(informative_4h_indicators_pandas_ta, cores=self.num_cores_indicators_calc)
    # RSI
    informative_4h["RSI_3"] = ta.RSI(informative_4h, timeperiod=3)
    informative_4h["RSI_14"] = ta.RSI(informative_4h, timeperiod=14)
    informative_4h["RSI_3_change_pct"] = (
      informative_4h["RSI_3"].fillna(float("nan")).pct_change(fill_method=None) * 100.0
    )
    informative_4h["RSI_14_change_pct"] = (
      informative_4h["RSI_14"].fillna(float("nan")).pct_change(fill_method=None) * 100.0
    )
    # EMA
    informative_4h["EMA_12"] = ta.EMA(informative_4h, timeperiod=12)
    informative_4h["EMA_200"] = ta.EMA(informative_4h, timeperiod=200).fillna(0.0)
    # MFI
    informative_4h["MFI_14"] = ta.MFI(informative_4h, timeperiod=14)
    # CMF
    informative_4h["CMF_20"] = _cmf(informative_4h, length=20)
    # Williams %R
    informative_4h["WILLR_14"] = ta.WILLR(informative_4h, timeperiod=14)
    # AROON
    aroon_14 = ta.AROON(informative_4h, timeperiod=14)
    informative_4h["AROONU_14"] = aroon_14["aroonup"] if isinstance(aroon_14, pd.DataFrame) else np.nan
    informative_4h["AROOND_14"] = aroon_14["aroondown"] if isinstance(aroon_14, pd.DataFrame) else np.nan
    # Stochastic
    try:
      informative_4h["STOCHk_14_3_3"] = _stoch_k(informative_4h["high"], informative_4h["low"], informative_4h["close"])
    except AttributeError:
      informative_4h["STOCHk_14_3_3"] = np.nan
    # Stochastic RSI
    informative_4h["STOCHRSIk_14_14_3_3"] = _stochrsi_k_from_rsi(informative_4h["RSI_14"])
    informative_4h["STOCHRSIk_14_14_3_3_change_pct"] = informative_4h["STOCHRSIk_14_14_3_3"].pct_change() * 100.0
    # KST
    informative_4h["KST_10_15_20_30_10_10_10_15"], informative_4h["KSTs_9"] = _kst(informative_4h["close"])
    # UO
    informative_4h["UO_7_14_28"] = ta.ULTOSC(informative_4h, timeperiod1=7, timeperiod2=14, timeperiod3=28)
    # ROC
    informative_4h["ROC_2"] = ta.ROC(informative_4h, timeperiod=2)
    informative_4h["ROC_9"] = ta.ROC(informative_4h, timeperiod=9)
    # CCI
    informative_4h["CCI_20"] = ta.CCI(informative_4h, timeperiod=20)
    informative_4h["CCI_20"] = (
      (informative_4h["CCI_20"]).astype(np.float64).replace(to_replace=[np.nan, None], value=(0.0))
    )
    informative_4h["CCI_20_change_pct"] = (informative_4h["CCI_20"].pct_change()) * 100.0

    # Candle change
    informative_4h["change_pct"] = (informative_4h["close"] - informative_4h["open"]) / informative_4h["open"] * 100.0
    # Candle change
    informative_4h["change_pct"] = (informative_4h["close"] - informative_4h["open"]) / informative_4h["open"] * 100.0
    # Wicks
    informative_4h["top_wick_pct"] = (
      (informative_4h["high"] - np.maximum(informative_4h["open"], informative_4h["close"]))
      / np.maximum(informative_4h["open"], informative_4h["close"])
      * 100.0
    )
    # Max highs
    informative_4h["high_max_6"] = informative_4h["high"].rolling(6).max()
    informative_4h["high_max_12"] = informative_4h["high"].rolling(12).max()
    informative_4h["high_max_24"] = informative_4h["high"].rolling(24).max()
    # Min lows
    informative_4h["low_min_12"] = informative_4h["low"].rolling(12).min()
    informative_4h["low_min_24"] = informative_4h["low"].rolling(24).min()

    # Performance logging
    # -----------------------------------------------------------------------------------------
    tok = time.perf_counter()
    log.debug(f"[{metadata['pair']}] informative_1d_indicators took: {tok - tik:0.4f} seconds.")

    return informative_4h

  # Informative 1h Timeframe Indicators
  # ---------------------------------------------------------------------------------------------
  def informative_1h_indicators(self, metadata: dict, info_timeframe) -> DataFrame:
    tik = time.perf_counter()
    assert self.dp, "DataProvider is required for multiple timeframes."
    # Get the informative pair
    informative_1h = self.dp.get_pair_dataframe(pair=metadata["pair"], timeframe=info_timeframe)

    # Indicators
    # -----------------------------------------------------------------------------------------
    # informative_1h_indicators_pandas_ta = pta.Strategy(
    #   name="informative_1h_indicators_pandas_ta",
    #   ta=[
    #     # RSI
    #     {"kind": "rsi", "length": 3},
    #     {"kind": "rsi", "length": 14},
    #     # {"kind": "rsi", "length": 20},
    #     # EMA
    #     {"kind": "ema", "length": 12},
    #     # {"kind": "ema", "length": 16},
    #     {"kind": "ema", "length": 20},
    #     {"kind": "ema", "length": 26},
    #     # {"kind": "ema", "length": 50},
    #     # {"kind": "ema", "length": 100},
    #     {"kind": "ema", "length": 200},
    #     # SMA
    #     # {"kind": "sma", "length": 16},
    #     # BB 20 - STD2
    #     {"kind": "bbands", "length": 20},
    #     # MFI
    #     {"kind": "mfi"},
    #     # CMF
    #     {"kind": "cmf"},
    #     # Williams %R
    #     {"kind": "willr", "length": 14},
    #     # CTI
    #     {"kind": "cti", "length": 20},
    #     # STOCHRSI
    #     {"kind": "stochrsi"},
    #     # KST
    #     {"kind": "kst"},
    #     # ROC
    #     {"kind": "roc"},
    #     # AROON
    #     {"kind": "aroon"},
    #     # UO
    #     {"kind": "uo"},
    #     # AO
    #     {"kind": "ao"},
    #   ],
    # )
    # informative_1h.ta.study(informative_1h_indicators_pandas_ta, cores=self.num_cores_indicators_calc)
    # RSI
    informative_1h["RSI_3"] = ta.RSI(informative_1h, timeperiod=3)
    informative_1h["RSI_14"] = ta.RSI(informative_1h, timeperiod=14)
    informative_1h["RSI_3_change_pct"] = (
      informative_1h["RSI_3"].fillna(float("nan")).pct_change(fill_method=None) * 100.0
    )
    informative_1h["RSI_14_change_pct"] = (
      informative_1h["RSI_14"].fillna(float("nan")).pct_change(fill_method=None) * 100.0
    )
    # EMA
    informative_1h["EMA_12"] = ta.EMA(informative_1h, timeperiod=12)
    informative_1h["EMA_200"] = ta.EMA(informative_1h, timeperiod=200).fillna(0.0)
    # SMA
    informative_1h["SMA_16"] = ta.SMA(informative_1h, timeperiod=16)
    # BB 20 - STD2
    upper, middle, lower = ta.BBANDS(informative_1h["close"], timeperiod=20, nbdevup=2.0, nbdevdn=2.0, matype=0)
    informative_1h["BBL_20_2.0"] = lower
    informative_1h["BBU_20_2.0"] = upper
    informative_1h["BBB_20_2.0"] = 100.0 * _non_zero_range(upper, lower) / middle
    # MFI
    informative_1h["MFI_14"] = ta.MFI(informative_1h, timeperiod=14)
    # CMF
    informative_1h["CMF_20"] = _cmf(informative_1h, length=20)
    # Williams %R
    informative_1h["WILLR_14"] = ta.WILLR(informative_1h, timeperiod=14)
    informative_1h["WILLR_84"] = ta.WILLR(informative_1h, timeperiod=84)
    # AROON
    aroon_14 = ta.AROON(informative_1h, timeperiod=14)
    informative_1h["AROONU_14"] = aroon_14["aroonup"] if isinstance(aroon_14, pd.DataFrame) else np.nan
    informative_1h["AROOND_14"] = aroon_14["aroondown"] if isinstance(aroon_14, pd.DataFrame) else np.nan
    # Stochastic
    informative_1h["STOCHk_14_3_3"] = _stoch_k(informative_1h["high"], informative_1h["low"], informative_1h["close"])
    # Stochastic RSI
    informative_1h["STOCHRSIk_14_14_3_3"] = _stochrsi_k_from_rsi(informative_1h["RSI_14"])
    # KST
    informative_1h["KST_10_15_20_30_10_10_10_15"], informative_1h["KSTs_9"] = _kst(informative_1h["close"])
    # UO
    informative_1h["UO_7_14_28"] = ta.ULTOSC(informative_1h, timeperiod1=7, timeperiod2=14, timeperiod3=28)
    informative_1h["UO_7_14_28"] = (
      (informative_1h["UO_7_14_28"]).astype(np.float64).replace(to_replace=[np.nan, None], value=(50.0))
    )
    # ROC
    informative_1h["ROC_2"] = ta.ROC(informative_1h, timeperiod=2)
    informative_1h["ROC_9"] = ta.ROC(informative_1h, timeperiod=9)
    # CCI
    informative_1h["CCI_20"] = ta.CCI(informative_1h, timeperiod=20)
    informative_1h["CCI_20"] = (
      (informative_1h["CCI_20"]).astype(np.float64).replace(to_replace=[np.nan, None], value=(0.0))
    )
    informative_1h["CCI_20_change_pct"] = informative_1h["CCI_20"].pct_change() * 100.0
    # Candle change
    informative_1h["change_pct"] = (informative_1h["close"] - informative_1h["open"]) / informative_1h["open"] * 100.0
    # Wicks
    # Max highs
    informative_1h["high_max_6"] = informative_1h["high"].rolling(6).max()
    informative_1h["high_max_12"] = informative_1h["high"].rolling(12).max()
    informative_1h["high_max_24"] = informative_1h["high"].rolling(24).max()
    # Min lows
    informative_1h["low_min_6"] = informative_1h["low"].rolling(6).min()
    informative_1h["low_min_12"] = informative_1h["low"].rolling(12).min()
    informative_1h["low_min_24"] = informative_1h["low"].rolling(24).min()

    # Performance logging
    # -----------------------------------------------------------------------------------------
    tok = time.perf_counter()
    log.debug(f"[{metadata['pair']}] informative_1h_indicators took: {tok - tik:0.4f} seconds.")

    return informative_1h

  # Informative 15m Timeframe Indicators
  # ---------------------------------------------------------------------------------------------
  def informative_15m_indicators(self, metadata: dict, info_timeframe) -> DataFrame:
    tik = time.perf_counter()
    assert self.dp, "DataProvider is required for multiple timeframes."

    # Get the informative pair
    informative_15m = self.dp.get_pair_dataframe(pair=metadata["pair"], timeframe=info_timeframe)

    # Indicators
    # -----------------------------------------------------------------------------------------
    # informative_15m_indicators_pandas_ta = pta.Strategy(
    #   name="informative_15m_indicators_pandas_ta",
    #   ta=[
    #     # RSI
    #     {"kind": "rsi", "length": 3},
    #     {"kind": "rsi", "length": 14},
    #     # {"kind": "rsi", "length": 20},
    #     # EMA
    #     {"kind": "ema", "length": 12},
    #     # {"kind": "ema", "length": 16},
    #     # {"kind": "ema", "length": 20},
    #     # {"kind": "ema", "length": 26},
    #     # {"kind": "ema", "length": 50},
    #     # {"kind": "ema", "length": 100},
    #     # {"kind": "ema", "length": 200},
    #     # SMA
    #     # {"kind": "sma", "length": 16},
    #     # BB 20 - STD2
    #     {"kind": "bbands", "length": 20},
    #     # Williams %R
    #     {"kind": "willr", "length": 14},
    #     # CTI
    #     {"kind": "cti", "length": 20},
    #     # STOCHRSI
    #     {"kind": "stochrsi"},
    #     # ROC
    #     {"kind": "roc"},
    #     # AROON
    #     {"kind": "aroon"},
    #     # UO
    #     {"kind": "uo"},
    #     # AO
    #     {"kind": "ao"},
    #   ],
    # )
    # informative_15m.ta.study(informative_15m_indicators_pandas_ta, cores=self.num_cores_indicators_calc)
    # RSI
    informative_15m["RSI_3"] = ta.RSI(informative_15m, timeperiod=3)
    informative_15m["RSI_14"] = ta.RSI(informative_15m, timeperiod=14)
    informative_15m["RSI_3_change_pct"] = informative_15m["RSI_3"].pct_change() * 100.0
    informative_15m["RSI_14_change_pct"] = informative_15m["RSI_14"].pct_change() * 100.0
    # EMA
    informative_15m["EMA_12"] = ta.EMA(informative_15m, timeperiod=12)
    informative_15m["EMA_20"] = ta.EMA(informative_15m, timeperiod=20)
    informative_15m["EMA_26"] = ta.EMA(informative_15m, timeperiod=26)
    # MFI
    informative_15m["MFI_14"] = ta.MFI(informative_15m, timeperiod=14)
    # CMF
    informative_15m["CMF_20"] = _cmf(informative_15m, length=20)
    # Williams %R
    informative_15m["WILLR_14"] = ta.WILLR(informative_15m, timeperiod=14)
    # AROON
    aroon_14 = ta.AROON(informative_15m, timeperiod=14)
    informative_15m["AROONU_14"] = aroon_14["aroonup"] if isinstance(aroon_14, pd.DataFrame) else np.nan
    informative_15m["AROOND_14"] = aroon_14["aroondown"] if isinstance(aroon_14, pd.DataFrame) else np.nan
    # Stochastic
    informative_15m["STOCHk_14_3_3"] = _stoch_k(informative_15m["high"], informative_15m["low"], informative_15m["close"])
    # Stochastic RSI
    informative_15m["STOCHRSIk_14_14_3_3"] = _stochrsi_k_from_rsi(informative_15m["RSI_14"])
    # UO
    informative_15m["UO_7_14_28"] = ta.ULTOSC(informative_15m, timeperiod1=7, timeperiod2=14, timeperiod3=28)
    informative_15m["UO_7_14_28_change_pct"] = informative_15m["UO_7_14_28"].pct_change() * 100.0
    # OBV
    obv_15m = ta.OBV(informative_15m)
    informative_15m["OBV_change_pct"] = obv_15m.pct_change() * 100.0
    # ROC
    informative_15m["ROC_9"] = ta.ROC(informative_15m, timeperiod=9)
    # CCI
    informative_15m["CCI_20"] = ta.CCI(informative_15m, timeperiod=20)
    informative_15m["CCI_20"] = (
      (informative_15m["CCI_20"]).astype(np.float64).replace(to_replace=[np.nan, None], value=(0.0))
    )
    informative_15m["CCI_20_change_pct"] = informative_15m["CCI_20"].pct_change() * 100.0
    # Performance logging
    # -----------------------------------------------------------------------------------------
    tok = time.perf_counter()
    log.debug(f"[{metadata['pair']}] informative_15m_indicators took: {tok - tik:0.4f} seconds.")

    return informative_15m

  # Coin Pair Base Timeframe Indicators
  # ---------------------------------------------------------------------------------------------
  def base_tf_5m_indicators(self, metadata: dict, df: DataFrame) -> DataFrame:
    tik = time.perf_counter()

    # Indicators
    # base_tf_5m_indicators_pandas_ta = pta.Strategy(
    #   name="base_tf_5m_indicators_pandas_ta",
    #   ta=[
    #     # RSI
    #     {"kind": "rsi", "length": 3},
    #     {"kind": "rsi", "length": 4},
    #     {"kind": "rsi", "length": 14},
    #     {"kind": "rsi", "length": 20},
    #     # EMA
    #     {"kind": "ema", "length": 3},
    #     {"kind": "ema", "length": 9},
    #     {"kind": "ema", "length": 12},
    #     {"kind": "ema", "length": 16},
    #     {"kind": "ema", "length": 20},
    #     {"kind": "ema", "length": 26},
    #     {"kind": "ema", "length": 50},
    #     {"kind": "ema", "length": 100},
    #     {"kind": "ema", "length": 200},
    #     # SMA
    #     {"kind": "sma", "length": 16},
    #     {"kind": "sma", "length": 30},
    #     {"kind": "sma", "length": 75},
    #     {"kind": "sma", "length": 200},
    #     # BB 20 - STD2
    #     {"kind": "bbands", "length": 20},
    #     # BB 40 - STD2
    #     {"kind": "bbands", "length": 40},
    #     # Williams %R
    #     {"kind": "willr", "length": 14},
    #     {"kind": "willr", "length": 480},
    #     # CTI
    #     {"kind": "cti", "length": 20},
    #     # MFI
    #     {"kind": "mfi"},
    #     # CMF
    #     {"kind": "cmf"},
    #     # CCI
    #     {"kind": "cci", "length": 20},
    #     # Hull Moving Average
    #     {"kind": "hma", "length": 55},
    #     {"kind": "hma", "length": 70},
    #     # ZL MA
    #     # {"kind": "zlma", "length": 50, "mamode":"linreg"},
    #     # Heiken Ashi
    #     # {"kind": "ha"},
    #     # STOCHRSI
    #     {"kind": "stochrsi"},
    #     # KST
    #     {"kind": "kst"},
    #     # ROC
    #     {"kind": "roc"},
    #     # AROON
    #     {"kind": "aroon"},
    #     # UO
    #     {"kind": "uo"},
    #     # AO
    #     {"kind": "ao"},
    #     # OBV
    #     {"kind": "obv"},
    #   ],
    # )
    # df.ta.study(base_tf_5m_indicators_pandas_ta, cores=self.num_cores_indicators_calc)
    # RSI
    df["RSI_3"] = ta.RSI(df, timeperiod=3)
    df["RSI_4"] = ta.RSI(df, timeperiod=4)
    df["RSI_14"] = ta.RSI(df, timeperiod=14)
    df["RSI_20"] = ta.RSI(df, timeperiod=20)
    df["RSI_14_change_pct"] = df["RSI_14"].pct_change() * 100.0
    # EMA
    df["EMA_9"] = ta.EMA(df, timeperiod=9)
    df["EMA_12"] = ta.EMA(df, timeperiod=12)
    df["EMA_16"] = ta.EMA(df, timeperiod=16)
    df["EMA_20"] = ta.EMA(df, timeperiod=20)
    df["EMA_26"] = ta.EMA(df, timeperiod=26)
    df["EMA_50"] = ta.EMA(df, timeperiod=50)
    df["EMA_100"] = ta.EMA(df, timeperiod=100).fillna(0.0)
    df["EMA_200"] = ta.EMA(df, timeperiod=200).fillna(0.0)
    # SMA
    df["SMA_9"] = ta.SMA(df, timeperiod=9)
    df["SMA_16"] = ta.SMA(df, timeperiod=16)
    df["SMA_21"] = ta.SMA(df, timeperiod=21)
    df["SMA_30"] = ta.SMA(df, timeperiod=30)
    df["SMA_200"] = ta.SMA(df, timeperiod=200)
    # BB 20 - STD2
    upper, middle, lower = ta.BBANDS(df["close"], timeperiod=20, nbdevup=2.0, nbdevdn=2.0, matype=0)
    df["BBL_20_2.0"] = lower
    df["BBU_20_2.0"] = upper
    df["BBB_20_2.0"] = 100.0 * _non_zero_range(upper, lower) / middle
    # BB 40 - STD2
    upper, middle, lower = ta.BBANDS(df["close"], timeperiod=40, nbdevup=2.0, nbdevdn=2.0, matype=0)
    df["BBL_40_2.0"] = lower
    df["BBD_40_2.0"] = np.abs(middle - lower)  # delta
    df["BBT_40_2.0"] = (df["close"] - df["BBL_40_2.0"]).abs()  # tail
    # MFI
    df["MFI_14"] = ta.MFI(df, timeperiod=14)
    # CMF
    df["CMF_20"] = _cmf(df, length=20)
    # Williams %R
    df["WILLR_14"] = ta.WILLR(df, timeperiod=14)
    df["WILLR_480"] = ta.WILLR(df, timeperiod=480)
    # AROON
    aroon_14 = ta.AROON(df, timeperiod=14)
    df["AROONU_14"] = aroon_14["aroonup"] if isinstance(aroon_14, pd.DataFrame) else np.nan
    df["AROOND_14"] = aroon_14["aroondown"] if isinstance(aroon_14, pd.DataFrame) else np.nan
    # Stochastic RSI
    df["STOCHRSIk_14_14_3_3"] = _stochrsi_k_from_rsi(df["RSI_14"])
    # KST
    df["KST_10_15_20_30_10_10_10_15"], df["KSTs_9"] = _kst(df["close"])
    # ROC
    df["ROC_2"] = ta.ROC(df, timeperiod=2)
    df["ROC_9"] = ta.ROC(df, timeperiod=9)
    # Candle change
    df["change_pct"] = (df["close"] - df["open"]) / df["open"] * 100.0
    # Close delta
    df["close_delta"] = (df["close"] - df["close"].shift()).abs()
    # Close max
    df["close_max_6"] = df["close"].rolling(6).max()
    df["close_max_12"] = df["close"].rolling(12).max()
    df["close_max_48"] = df["close"].rolling(48).max()
    # Close min
    df["close_min_6"] = df["close"].rolling(6).min()
    df["close_min_12"] = df["close"].rolling(12).min()
    df["close_min_48"] = df["close"].rolling(48).min()
    # Number of empty candles
    df["num_empty_288"] = (df["volume"] <= 0).rolling(window=288, min_periods=288).sum()

    # -----------------------------------------------------------------------------------------

    # Global protections
    # -----------------------------------------------------------------------------------------
    if self.config["runmode"].value not in ("live", "dry_run"):
      # Backtest age filter
      df["bt_agefilter_ok"] = False
      df.loc[df.index > (12 * 24 * self.bt_min_age_days), "bt_agefilter_ok"] = True
    else:
      # Exchange downtime protection
      df["live_data_ok"] = df["volume"].rolling(window=72, min_periods=72).min() > 0

    # Performance logging
    # -----------------------------------------------------------------------------------------
    tok = time.perf_counter()
    log.debug(f"[{metadata['pair']}] base_tf_5m_indicators took: {tok - tik:0.4f} seconds.")

    return df

  # Coin Pair Indicator Switch Case
  # ---------------------------------------------------------------------------------------------
  def info_switcher(self, metadata: dict, info_timeframe) -> DataFrame:
    if info_timeframe == "1d":
      return self.informative_1d_indicators(metadata, info_timeframe)
    elif info_timeframe == "4h":
      return self.informative_4h_indicators(metadata, info_timeframe)
    elif info_timeframe == "1h":
      return self.informative_1h_indicators(metadata, info_timeframe)
    elif info_timeframe == "15m":
      return self.informative_15m_indicators(metadata, info_timeframe)
    else:
      raise RuntimeError(f"{info_timeframe} not supported as informative timeframe for BTC pair.")

  # BTC 1D Indicators
  # ---------------------------------------------------------------------------------------------
  def btc_info_1d_indicators(self, btc_info_pair, btc_info_timeframe, metadata: dict) -> DataFrame:
    tik = time.perf_counter()
    btc_info_1d = self.dp.get_pair_dataframe(btc_info_pair, btc_info_timeframe)
    # Indicators
    # -----------------------------------------------------------------------------------------
    # btc_info_1d_indicators_pandas_ta = pta.Strategy(
    #   name="btc_info_1d_indicators_pandas_ta",
    #   ta=[
    #     # RSI
    #     # {"kind": "rsi", "length": 3},
    #     {"kind": "rsi", "length": 14},
    #     # {"kind": "rsi", "length": 20},
    #     # EMA
    #     # {"kind": "ema", "length": 12},
    #     # {"kind": "ema", "length": 16},
    #     # {"kind": "ema", "length": 20},
    #     # {"kind": "ema", "length": 26},
    #     # {"kind": "ema", "length": 50},
    #     # {"kind": "ema", "length": 100},
    #     # {"kind": "ema", "length": 200},
    #     # SMA
    #     # {"kind": "sma", "length": 16},
    #   ],
    # )
    # btc_info_1d.ta.study(btc_info_1d_indicators_pandas_ta, cores=self.num_cores_indicators_calc)

    # Add prefix
    # -----------------------------------------------------------------------------------------
    ignore_columns = ["date"]
    btc_info_1d.rename(columns=lambda s: f"btc_{s}" if s not in ignore_columns else s, inplace=True)

    tok = time.perf_counter()
    log.debug(f"[{metadata['pair']}] btc_info_1d_indicators took: {tok - tik:0.4f} seconds.")

    return btc_info_1d

  # BTC 4h Indicators
  # ---------------------------------------------------------------------------------------------
  def btc_info_4h_indicators(self, btc_info_pair, btc_info_timeframe, metadata: dict) -> DataFrame:
    tik = time.perf_counter()
    btc_info_4h = self.dp.get_pair_dataframe(btc_info_pair, btc_info_timeframe)
    # Indicators
    # -----------------------------------------------------------------------------------------

    # Add prefix
    # -----------------------------------------------------------------------------------------
    ignore_columns = ["date"]
    btc_info_4h.rename(columns=lambda s: f"btc_{s}" if s not in ignore_columns else s, inplace=True)

    tok = time.perf_counter()
    log.debug(f"[{metadata['pair']}] btc_info_4h_indicators took: {tok - tik:0.4f} seconds.")

    return btc_info_4h

  # BTC 1h Indicators
  # ---------------------------------------------------------------------------------------------
  def btc_info_1h_indicators(self, btc_info_pair, btc_info_timeframe, metadata: dict) -> DataFrame:
    tik = time.perf_counter()
    btc_info_1h = self.dp.get_pair_dataframe(btc_info_pair, btc_info_timeframe)
    # Indicators
    # -----------------------------------------------------------------------------------------

    # Add prefix
    # -----------------------------------------------------------------------------------------
    ignore_columns = ["date"]
    btc_info_1h.rename(columns=lambda s: f"btc_{s}" if s not in ignore_columns else s, inplace=True)

    tok = time.perf_counter()
    log.debug(f"[{metadata['pair']}] btc_info_1h_indicators took: {tok - tik:0.4f} seconds.")

    return btc_info_1h

  # BTC 15m Indicators
  # ---------------------------------------------------------------------------------------------
  def btc_info_15m_indicators(self, btc_info_pair, btc_info_timeframe, metadata: dict) -> DataFrame:
    tik = time.perf_counter()
    btc_info_15m = self.dp.get_pair_dataframe(btc_info_pair, btc_info_timeframe)
    # Indicators
    # -----------------------------------------------------------------------------------------

    # Add prefix
    # -----------------------------------------------------------------------------------------
    ignore_columns = ["date"]
    btc_info_15m.rename(columns=lambda s: f"btc_{s}" if s not in ignore_columns else s, inplace=True)

    tok = time.perf_counter()
    log.debug(f"[{metadata['pair']}] btc_info_15m_indicators took: {tok - tik:0.4f} seconds.")

    return btc_info_15m

  # BTC 5m Indicators
  # ---------------------------------------------------------------------------------------------
  def btc_info_5m_indicators(self, btc_info_pair, btc_info_timeframe, metadata: dict) -> DataFrame:
    tik = time.perf_counter()
    btc_info_5m = self.dp.get_pair_dataframe(btc_info_pair, btc_info_timeframe)
    # Indicators
    # -----------------------------------------------------------------------------------------

    # Add prefix
    # -----------------------------------------------------------------------------------------
    ignore_columns = ["date"]
    btc_info_5m.rename(columns=lambda s: f"btc_{s}" if s not in ignore_columns else s, inplace=True)

    tok = time.perf_counter()
    log.debug(f"[{metadata['pair']}] btc_info_5m_indicators took: {tok - tik:0.4f} seconds.")

    return btc_info_5m

  # BTC Indicator Switch Case
  # ---------------------------------------------------------------------------------------------
  def btc_info_switcher(self, btc_info_pair, btc_info_timeframe, metadata: dict) -> DataFrame:
    if btc_info_timeframe == "1d":
      return self.btc_info_1d_indicators(btc_info_pair, btc_info_timeframe, metadata)
    elif btc_info_timeframe == "4h":
      return self.btc_info_4h_indicators(btc_info_pair, btc_info_timeframe, metadata)
    elif btc_info_timeframe == "1h":
      return self.btc_info_1h_indicators(btc_info_pair, btc_info_timeframe, metadata)
    elif btc_info_timeframe == "15m":
      return self.btc_info_15m_indicators(btc_info_pair, btc_info_timeframe, metadata)
    elif btc_info_timeframe == "5m":
      return self.btc_info_5m_indicators(btc_info_pair, btc_info_timeframe, metadata)
    else:
      raise RuntimeError(f"{btc_info_timeframe} not supported as informative timeframe for BTC pair.")

  # Populate Indicators
  # ---------------------------------------------------------------------------------------------
  def populate_indicators(self, df: DataFrame, metadata: dict) -> DataFrame:
    tik = time.perf_counter()
    """
        --> BTC informative indicators
        ___________________________________________________________________________________________
        """
    if self.config["stake_currency"] in [
      "USDT",
      "BUSD",
      "USDC",
      "DAI",
      "TUSD",
      "FDUSD",
      "PAX",
      "USD",
      "EUR",
      "GBP",
      "TRY",
    ]:
      if ("trading_mode" in self.config) and (self.config["trading_mode"] in ["futures", "margin"]):
        btc_info_pair = f"BTC/{self.config['stake_currency']}:{self.config['stake_currency']}"
      else:
        btc_info_pair = f"BTC/{self.config['stake_currency']}"
    else:
      if ("trading_mode" in self.config) and (self.config["trading_mode"] in ["futures", "margin"]):
        btc_info_pair = "BTC/USDT:USDT"
      else:
        btc_info_pair = "BTC/USDT"

    for btc_info_timeframe in self.btc_info_timeframes:
      btc_informative = self.btc_info_switcher(btc_info_pair, btc_info_timeframe, metadata)
      # Customize what we drop - in case we need to maintain some BTC informative ohlcv data
      # Default drop all
      btc_informative = _drop_existing_columns(
        btc_informative, [f"btc_{s}" for s in ["open", "high", "low", "close", "volume"]]
      )
      df = merge_informative_pair(df, btc_informative, self.timeframe, btc_info_timeframe, ffill=True)
      drop_columns = {
        "1d": [],
        "4h": [],
        "1h": [],
        "15m": [],
        "5m": [],
      }.get(
        btc_info_timeframe,
        [f"{s}_{btc_info_timeframe}" for s in ["date", "open", "high", "low", "close", "volume"]],
      )
      drop_columns.append(f"date_{btc_info_timeframe}")
      df.drop(columns=df.columns.intersection(drop_columns), inplace=True)

    """
        --> Indicators on informative timeframes
        ___________________________________________________________________________________________
        """
    for info_timeframe in self.info_timeframes:
      info_indicators = self.info_switcher(metadata, info_timeframe)
      # Customize what we drop - in case we need to maintain some informative timeframe ohlcv data
      # Default drop all except base timeframe ohlcv data
      pre_drop_columns = {
        "1d": ["open", "high", "low", "close", "volume"],
        "4h": ["open", "high", "low", "close", "volume"],
        "1h": ["open", "high", "low", "close", "volume"],
        "15m": ["high", "low", "volume"],
      }.get(info_timeframe, ["open", "high", "low", "close", "volume"])
      info_indicators = _drop_existing_columns(info_indicators, pre_drop_columns)
      df = merge_informative_pair(df, info_indicators, self.timeframe, info_timeframe, ffill=True)
      drop_columns = {
        "1d": [],
        "4h": [],
        "1h": [],
        "15m": [],
      }.get(info_timeframe, [f"{s}_{info_timeframe}" for s in ["date", "open", "high", "low", "close", "volume"]])
      df.drop(columns=df.columns.intersection(drop_columns), inplace=True)

    """
        --> The indicators for the base timeframe  (5m)
        ___________________________________________________________________________________________
        """
    df = self.base_tf_5m_indicators(metadata, self._test_x7_maybe_tail_base_indicator_input(df))

    test_x7_full_df = None
    test_x7_tail_rows = self._test_x7_indicator_tail_rows()
    if (
      test_x7_tail_rows > 0
      and not self._test_x7_is_backtest_like_runmode()
      and len(df) > test_x7_tail_rows
    ):
      test_x7_full_df = df
      df = df.tail(test_x7_tail_rows).copy(deep=False)

    # df["zlma_50_1h"] = df["zlma_50_1h"].astype(np.float64).replace(to_replace=[np.nan, None], value=(0.0))
    # df["CTI_20_1d"] = df["CTI_20_1d"].astype(np.float64).replace(to_replace=[np.nan, None], value=(0.0))
    # df["WILLR_480_1h"] = df["WILLR_480_1h"].astype(np.float64).replace(to_replace=[np.nan, None], value=(-50.0))
    # df["WILLR_480_4h"] = df["WILLR_480_4h"].astype(np.float64).replace(to_replace=[np.nan, None], value=(-50.0))
    # df["RSI_14_1d"] = df["RSI_14_1d"].astype(np.float64).replace(to_replace=[np.nan, None], value=(50.0))
    df["RSI_14_1h"] = df["RSI_14_1h"].astype(np.float64).replace(to_replace=[np.nan, None], value=(50.0))
    _cmp = build_comparison_cache(df)
    _gt_mul, _range_lt = build_expression_cache(df)
    _cmp_cached_0 = _cmp("RSI_14_15m", "<", 30.0)
    _cmp_cached_1 = _cmp("RSI_14_1h", "<", 40.0)
    _cmp_cached_2 = _cmp("RSI_14_4h", "<", 50.0)
    _cmp_cached_3 = _cmp("RSI_14_15m", "<", 40.0)
    _cmp_cached_4 = _cmp("RSI_14_4h", "<", 40.0)
    _cmp_cached_5 = _cmp("RSI_14_1h", "<", 30.0)
    _cmp_cached_6 = _cmp("RSI_14_1h", "<", 50.0)
    _cmp_cached_7 = _cmp("RSI_3_15m", ">", 20.0)
    _cmp_cached_8 = _cmp("RSI_3_15m", ">", 15.0)
    _cmp_cached_9 = _cmp("RSI_3_15m", ">", 10.0)
    _cmp_cached_10 = _cmp("RSI_3_15m", ">", 25.0)
    _cmp_cached_11 = _cmp("AROONU_14_15m", "<", 60.0)
    _cmp_cached_12 = _cmp("RSI_14_4h", "<", 30.0)
    _cmp_cached_13 = _cmp("RSI_3_15m", ">", 30.0)
    _cmp_cached_14 = _cmp("RSI_3_1h", ">", 30.0)
    _cmp_cached_15 = _cmp("RSI_14_15m", "<", 20.0)
    _cmp_cached_16 = _cmp("AROONU_14_4h", "<", 100.0)
    _cmp_cached_17 = _cmp("AROONU_14_15m", "<", 50.0)
    _cmp_cached_18 = _cmp("RSI_3_4h", ">", 60.0)
    _cmp_cached_19 = _cmp("RSI_3_1h", ">", 40.0)
    _cmp_cached_20 = _cmp("AROONU_14_4h", "<", 80.0)
    _cmp_cached_21 = _cmp("RSI_3_1h", ">", 45.0)
    _cmp_cached_22 = _cmp("AROONU_14_1h", "<", 50.0)
    _cmp_cached_23 = _cmp("RSI_3_1h", ">", 35.0)
    _cmp_cached_24 = _cmp("RSI_3_1h", ">", 20.0)
    _cmp_cached_25 = _cmp("RSI_3_4h", ">", 45.0)
    _cmp_cached_26 = _cmp("RSI_3_15m", ">", 5.0)
    _cmp_cached_27 = _cmp("RSI_3_1h", ">", 25.0)
    _cmp_cached_28 = _cmp("STOCHRSIk_14_14_3_3_15m", "<", 50.0)
    _cmp_cached_29 = _cmp("RSI_14_4h", "<", 70.0)
    _cmp_cached_30 = _cmp("STOCHRSIk_14_14_3_3_1h", "<", 50.0)
    _cmp_cached_31 = _cmp("AROONU_14_1h", "<", 80.0)

    _cmp_cached_32 = _cmp("RSI_3_4h", ">", 40.0)
    _cmp_cached_33 = _cmp("RSI_3_4h", ">", 30.0)
    _cmp_cached_34 = _cmp("AROONU_14_4h", "<", 70.0)
    _cmp_cached_35 = _cmp("RSI_3_4h", ">", 25.0)
    _cmp_cached_36 = _cmp("RSI_14_4h", "<", 60.0)
    _cmp_cached_37 = _cmp("AROONU_14_4h", "<", 50.0)
    _cmp_cached_38 = _cmp("ROC_9_4h", "<", 20.0)
    _cmp_cached_39 = _cmp("RSI_3_4h", ">", 50.0)
    _cmp_cached_40 = _cmp("AROONU_14_1h", "<", 70.0)
    _cmp_cached_41 = _cmp("RSI_3_1h", ">", 55.0)
    _cmp_cached_42 = _cmp("RSI_3_4h", ">", 55.0)
    _cmp_cached_43 = _cmp("RSI_14_1h", "<", 20.0)
    _cmp_cached_44 = _cmp("RSI_3_4h", ">", 65.0)
    _cmp_cached_45 = _cmp("RSI_3_15m", ">", 35.0)
    _cmp_cached_46 = _cmp("RSI_3_1h", ">", 50.0)
    _cmp_cached_47 = _cmp("STOCHRSIk_14_14_3_3_4h", "<", 50.0)
    _cmp_cached_48 = _cmp("RSI_3_1h", ">", 15.0)
    _cmp_cached_49 = _cmp("ROC_9_4h", "<", 10.0)
    _cmp_cached_50 = _cmp("STOCHRSIk_14_14_3_3_15m", "<", 20.0)
    _cmp_cached_51 = _cmp("ROC_9_1d", "<", 50.0)
    _cmp_cached_52 = _cmp("RSI_3_4h", ">", 35.0)
    _cmp_cached_53 = _cmp("CMF_20_1h", ">", -0.20)
    _cmp_cached_54 = _cmp("RSI_3_4h", ">", 20.0)
    _cmp_cached_55 = _cmp("CMF_20_15m", ">", -0.20)
    _cmp_cached_56 = _cmp("AROONU_14_4h", "<", 85.0)
    _cmp_cached_57 = _cmp("RSI_3_1h", ">", 10.0)
    _cmp_cached_58 = _cmp("ROC_9_1d", "<", 100.0)
    _cmp_cached_59 = _cmp("STOCHRSIk_14_14_3_3_1h", "<", 40.0)
    _cmp_cached_60 = _cmp("RSI_3_1h", ">", 60.0)
    _cmp_cached_61 = _cmp("AROONU_14_15m", "<", 70.0)
    _cmp_cached_62 = _cmp("CMF_20_4h", ">", -0.10)
    _cmp_cached_63 = _cmp("AROONU_14_15m", "<", 30.0)
    _cmp_cached_64 = _cmp("CMF_20_1h", ">", -0.10)
    _cmp_cached_65 = _cmp("RSI_3_15m", ">", 40.0)
    _cmp_cached_66 = _cmp("STOCHRSIk_14_14_3_3_4h", "<", 80.0)
    _cmp_cached_67 = _cmp("ROC_9_1h", "<", 10.0)
    _cmp_cached_68 = _cmp("ROC_9_1d", "<", 80.0)
    _cmp_cached_69 = _cmp("AROONU_14_1h", "<", 85.0)
    _cmp_cached_70 = _cmp("STOCHRSIk_14_14_3_3_4h", "<", 70.0)
    _cmp_cached_71 = _cmp("CMF_20_4h", ">", -0.20)
    _cmp_cached_72 = _cmp("ROC_9_4h", "<", 25.0)
    _cmp_cached_73 = _cmp("CMF_20_15m", ">", -0.25)
    _cmp_cached_74 = _cmp("CMF_20_15m", ">", -0.30)
    _cmp_cached_75 = _cmp("AROONU_14_1h", "<", 40.0)
    _cmp_cached_76 = _cmp("AROONU_14_4h", "<", 90.0)
    _cmp_cached_77 = _cmp("ROC_9_4h", "<", 40.0)
    _cmp_cached_78 = _cmp("ROC_9_4h", ">", -30.0)
    _cmp_cached_79 = _cmp("AROONU_14_1h", "<", 100.0)
    _cmp_cached_80 = _cmp("STOCHRSIk_14_14_3_3_1h", "<", 70.0)
    _cmp_cached_81 = _cmp("STOCHRSIk_14_14_3_3_15m", "<", 30.0)
    _cmp_cached_82 = _cmp("RSI_3_1h", ">", 5.0)
    _cmp_cached_83 = _cmp("AROONU_14_1h", "<", 30.0)
    _cmp_cached_84 = _cmp("RSI_14_4h", "<", 80.0)
    # Global protections Long
    df["protections_long_global"] = (
      # 5m & 15m & 1h & 4h & 1d down move, 1h & 4h & 1d still not low enough
      (
        (_cmp("RSI_3", ">", 1.0))
        | (_cmp_cached_8)
        | (_cmp_cached_24)
        | (_cmp_cached_54)
        | (_cmp("RSI_3_1d", ">", 20.0))
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp("RSI_14_1d", "<", 30.0))
        | (_cmp("CCI_20_1h", "<", -250.0))
        | (_cmp("CCI_20_4h", "<", -200.0))
      )
      # 5m & 4h & 1d down move, 15m & 1h & 4h still not low enough, 1d still high
      & (
        (_cmp("RSI_3", ">", 1.0))
        | (_cmp("RSI_3_4h", ">", 10.0))
        | (_cmp("RSI_3_1d", ">", 35.0))
        | (_cmp_cached_0)
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp_cached_50)
        | (_cmp("STOCHRSIk_14_14_3_3_1d", "<", 50.0))
      )
      # 5m down move, 15m & 1h & 4h still high, 15m high
      & (
        (_cmp("RSI_3", ">", 3.0))
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp_cached_61)
        | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 70.0))
      )
      # 1h & 4h down move, 15m & 1h & 4h downtrend, 1h still high
      & (
        (_cmp("RSI_3", ">", 5.0))
        | (_cmp_cached_9)
        | (_cmp_cached_19)
        | (_cmp_cached_42)
        | (_cmp_cached_73)
        | (_cmp("AROONU_14_4h", "<", 60.0))
        | (_cmp_cached_68)
      )
      # 5m & 15m & 1h down move, 1h & 4h still high, 15m still high, 1h high
      & (
        (_cmp("RSI_3", ">", 5.0))
        | (_cmp_cached_9)
        | (_cmp_cached_19)
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp("AROONU_14_15m", "<", 40.0))
        | (_cmp_cached_69)
        | (_cmp_cached_80)
      )
      # 5m & 15m & 1h & 4h down move, 4h high
      & (
        (_cmp("RSI_3", ">", 5.0))
        | (_cmp_cached_8)
        | (_cmp_cached_21)
        | (_cmp_cached_42)
        | (_cmp_cached_2)
        | (_cmp_cached_20)
        | (_cmp_cached_70)
      )
      # 5m & 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 15m & 4h high
      & (
        (_cmp("RSI_3", ">", 5.0))
        | (_cmp_cached_13)
        | (_cmp_cached_19)
        | (_cmp_cached_32)
        | (_cmp_cached_0)
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp_cached_11)
        | (_cmp_cached_28)
        | (_cmp_cached_66)
      )
      # 5m & 15m & 4h down move, 15m & 1h & 4h still high, 15m & 1h still high
      & (
        (_cmp("RSI_3", ">", 5.0))
        | (_cmp_cached_13)
        | (_cmp_cached_33)
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp_cached_17)
        | (_cmp_cached_81)
        | (_cmp_cached_30)
      )
      # 5m & 4h & 1d down move, 15m high
      & (
        (_cmp("RSI_3", ">", 5.0))
        | (_cmp("RSI_3_4h", ">", 10.0))
        | (_cmp("RSI_3_1d", ">", 15.0))
        | (_cmp_cached_11)
        | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 70.0))
      )
      # 5m & 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h stil high, 15m & 4h high
      & (
        (_cmp("RSI_3", ">", 10.0))
        | (_cmp_cached_7)
        | (_cmp_cached_21)
        | (_cmp_cached_25)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 60.0))
        | (_cmp_cached_70)
      )
      # 5m & 15m & 1h & 4h down move, 15m & 1h & 4h still high, 15m & 4h high
      & (
        (_cmp("RSI_3", ">", 10.0))
        | (_cmp_cached_7)
        | (_cmp_cached_21)
        | (_cmp_cached_25)
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_11)
        | (_cmp_cached_34)
        | (_cmp_cached_28)
      )
      # 5m & 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 15m high
      & (
        (_cmp("RSI_3", ">", 10.0))
        | (_cmp_cached_7)
        | (_cmp_cached_46)
        | (_cmp_cached_39)
        | (_cmp_cached_0)
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp_cached_11)
        | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 60.0))
      )
      # 5m & 15m & 1h down move, 15m & 1h still high, 4h high, 15m still not low enough, 5h overbought
      & (
        (_cmp("RSI_3", ">", 10.0))
        | (_cmp_cached_10)
        | (_cmp_cached_41)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_29)
        | (_cmp("AROONU_14_1h", "<", 20.0))
        | (_cmp_cached_20)
        | (_cmp_cached_50)
        | (_cmp("ROC_9_4h", "<", 80.0))
      )
      # 5m & 15m & 1h & 1d down move, 1h & 4h still high, 1d downtrend
      & (
        (_cmp("RSI_3", ">", 10.0))
        | (_cmp_cached_10)
        | (_cmp("RSI_3_1h", ">", 65.0))
        | (_cmp("RSI_3_1d", ">", 25.0))
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp("CMF_20_1d", ">", -0.20))
        | (_cmp_cached_30)
        | (_cmp_cached_47)
        | (_cmp("ROC_9_1d", ">", -15.0))
      )
      # 5m & 15m & 4h down move, 15m & 1h still not low enough, 4h still high, 15m & 4h high
      & (
        (_cmp("RSI_3", ">", 10.0))
        | (_cmp_cached_10)
        | (_cmp_cached_35)
        | (_cmp_cached_0)
        | (_cmp_cached_5)
        | (_cmp_cached_4)
        | (_cmp_cached_11)
        | (_cmp("AROONU_14_4h", "<", 60.0))
        | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 60.0))
      )
      # 5m & 15m & 1h down move, 15m still not low enough, 1h still high, 4h high, 15m & 4h high
      & (
        (_cmp("RSI_3", ">", 10.0))
        | (_cmp_cached_13)
        | (_cmp_cached_23)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_29)
        | (_cmp_cached_11)
        | (_cmp("AROONU_14_4h", "<", 60.0))
        | (_cmp_cached_81)
        | (_cmp_cached_47)
      )
      # 5m & 15m & 1h down move, 15m still high, 1h & 4h high, 4h high & overbought
      & (
        (_cmp("RSI_3", ">", 15.0))
        | (_cmp_cached_13)
        | (_cmp_cached_60)
        | (_cmp_cached_3)
        | (_cmp("RSI_14_1h", "<", 60.0))
        | (_cmp_cached_36)
        | (_cmp("AROONU_14_15m", "<", 40.0))
        | (_cmp_cached_20)
        | (_cmp_cached_50)
        | (_cmp_cached_66)
        | (_cmp("ROC_9_4h", "<", 30.0))
      )
      # 15m & 1h & 4h down move, 1h still high, 15m & 1h downtrend
      & (
        (_cmp("RSI_3_15m", ">", 3.0))
        | (_cmp("RSI_3_1h", ">", 3.0))
        | (_cmp_cached_54)
        | (_cmp_cached_22)
        | (_cmp("ROC_9_15m", ">", -10.0))
        | (_cmp("ROC_9_1h", ">", -15.0))
      )
      # 15m & 1h & 4h down move, 15m downtrend, 1h still high, 4h still not low enough
      & (
        (_cmp("RSI_3_15m", ">", 3.0))
        | (_cmp_cached_82)
        | (_cmp_cached_33)
        | (_cmp_cached_55)
        | (_cmp_cached_22)
        | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 30.0))
      )
      # 15m & 1h & 4h down move, 15m downtrend, 1h & 4h still not low enough
      & (
        (_cmp("RSI_3_15m", ">", 3.0))
        | (_cmp_cached_57)
        | (_cmp("RSI_3_4h", ">", 15.0))
        | (_cmp_cached_74)
        | (_cmp("AROONU_14_1h", "<", 20.0))
        | (_cmp("AROONU_14_4h", "<", 20.0))
      )
      # 15m & 1h & 4h down move, 15m downtrend, 15m & 1h still not low enough
      & (
        (_cmp("RSI_3_15m", ">", 3.0))
        | (_cmp_cached_57)
        | (_cmp("RSI_3_4h", ">", 15.0))
        | (_cmp_cached_74)
        | (_cmp_cached_50)
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 20.0))
      )
      # 15m & 1h & 4h down move, 1h & 4h still high, 15m downtrend, 4h overbought
      & (
        (_cmp("RSI_3_15m", ">", 3.0))
        | (_cmp_cached_57)
        | (_cmp_cached_52)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_55)
        | (_cmp("ROC_9_4h", "<", 15.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h downtrend, 1h & 4h still not low enough
      & (
        (_cmp("RSI_3_15m", ">", 3.0))
        | (_cmp_cached_57)
        | (_cmp_cached_32)
        | (_cmp_cached_55)
        | (_cmp_cached_53)
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 30.0))
        | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 30.0))
      )
      # 15m & 1h & 4h down move, 4h still high, 1h downtrend, 4h still high
      & (
        (_cmp("RSI_3_15m", ">", 3.0))
        | (_cmp_cached_57)
        | (_cmp_cached_25)
        | (_cmp_cached_4)
        | (_cmp("CMF_20_1h", ">", -0.30))
        | (_cmp("AROONU_14_4h", "<", 40.0))
      )
      # 15m & 1h & 4h down move, 1h & 4h still not low enough, 15m downtrend
      & (
        (_cmp("RSI_3_15m", ">", 3.0))
        | (_cmp_cached_48)
        | (_cmp_cached_35)
        | (_cmp_cached_5)
        | (_cmp_cached_4)
        | (_cmp_cached_73)
        | (_cmp("AROONU_14_4h", "<", 25.0))
      )
      # 15m & 1h & 4h down move, 1h & 4h still not low enough, 15m still not low enough
      & (
        (_cmp("RSI_3_15m", ">", 3.0))
        | (_cmp_cached_48)
        | (_cmp_cached_25)
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp("AROONU_14_15m", "<", 25.0))
      )
      # 15m & 1h & 4h down move, 1h & 4h still not low enough, 15m & 1h & 4h downtrend, 1h still not low enough
      & (
        (_cmp("RSI_3_15m", ">", 3.0))
        | (_cmp_cached_24)
        | (_cmp_cached_54)
        | (_cmp_cached_43)
        | (_cmp("RSI_14_4h", "<", 20.0))
        | (_cmp_cached_55)
        | (_cmp("CMF_20_1h", ">", -0.25))
        | (_cmp("CMF_20_4h", ">", -0.25))
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 30.0))
      )
      # 15m & 1h & 4h & 1d down move, 1h still high, 1h & 4h still not low enough
      & (
        (_cmp("RSI_3_15m", ">", 3.0))
        | (_cmp_cached_14)
        | (_cmp_cached_33)
        | (_cmp("RSI_3_1d", ">", 50.0))
        | (_cmp_cached_22)
        | (_cmp("CCI_20_1h", "<", -250.0))
        | (_cmp("CCI_20_4h", "<", -250.0))
      )
      # 15m & 1h & 4h down move, 4h downtrend, 15m & 1h still not low enough
      & (
        (_cmp("RSI_3_15m", ">", 3.0))
        | (_cmp_cached_46)
        | (_cmp_cached_39)
        | (_cmp("CMF_20_4h", ">", -0.30))
        | (_cmp("AROONU_14_15m", "<", 20.0))
        | (_cmp_cached_83)
      )
      # 15m & 4h down move, 15m & 1h & 4h still not low enough, 1h still not low enough
      & (
        (_cmp("RSI_3_15m", ">", 3.0))
        | (_cmp("RSI_3_4h", ">", 10.0))
        | (_cmp_cached_15)
        | (_cmp_cached_43)
        | (_cmp("RSI_14_4h", "<", 20.0))
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 30.0))
      )
      # 15m & 4h down move, 1h & 4h still high, 15m still not low enough, 1h still high
      & (
        (_cmp("RSI_3_15m", ">", 3.0))
        | (_cmp_cached_33)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp("AROONU_14_15m", "<", 25.0))
        | (_cmp_cached_30)
      )
      # 15m down move, 15m & 1h high
      & (
        (_cmp("RSI_3_15m", ">", 3.0))
        | (_cmp_cached_61)
        | (_cmp("AROONU_14_1h", "<", 90.0))
        | (_cmp_cached_28)
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 90.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h downtrend, 1h & 4h still not low enough, 4h downtrend
      & (
        (_cmp_cached_26)
        | (_cmp_cached_82)
        | (_cmp_cached_54)
        | (_cmp("CMF_20_15m", ">", -0.15))
        | (_cmp("CMF_20_1h", ">", -0.15))
        | (_cmp("CMF_20_4h", ">", -0.15))
        | (_cmp("AROONU_14_1h", "<", 20.0))
        | (_cmp("AROONU_14_4h", "<", 20.0))
        | (_cmp("ROC_9_4h", ">", -20.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h downtrend, 1h still high, 15m still not low enough, 15m & 1h downtrend
      & (
        (_cmp_cached_26)
        | (_cmp_cached_82)
        | (_cmp_cached_54)
        | (_cmp_cached_55)
        | (_cmp("CMF_20_1h", ">", -0.15))
        | (_cmp_cached_62)
        | (_cmp_cached_75)
        | (_cmp_cached_81)
        | (_cmp("ROC_9_15m", ">", -15.0))
        | (_cmp("ROC_9_1h", ">", -15.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h downtrend, 15m & 4h still not low enough
      & (
        (_cmp_cached_26)
        | (_cmp_cached_82)
        | (_cmp_cached_54)
        | (_cmp_cached_55)
        | (_cmp("CMF_20_1h", ">", -0.25))
        | (_cmp_cached_50)
        | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 20.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h downtrend, 15m still not low enough
      & (
        (_cmp_cached_26)
        | (_cmp_cached_82)
        | (_cmp_cached_54)
        | (_cmp("CMF_20_15m", ">", -0.40))
        | (_cmp("CMF_20_1h", ">", -0.40))
        | (_cmp_cached_50)
      )
      # 5m & 1h & 4h down move, 1h & 4h downtrend, 15m still high, 4h still not low enough
      & (
        (_cmp_cached_26)
        | (_cmp_cached_82)
        | (_cmp_cached_54)
        | (_cmp_cached_53)
        | (_cmp("CMF_20_4h", ">", -0.25))
        | (_cmp_cached_28)
        | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 10.0))
      )
      # 15m & 1h & 4h & 1d down move, 15m downtrend, 15m still not low enough, 1h downtrend
      & (
        (_cmp_cached_26)
        | (_cmp_cached_82)
        | (_cmp_cached_35)
        | (_cmp("RSI_3_1d", ">", 30.0))
        | (_cmp_cached_55)
        | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 10.0))
        | (_cmp("ROC_9_1h", ">", -10.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h downtrend, 15m still not low enough
      & (
        (_cmp_cached_26)
        | (_cmp_cached_82)
        | (_cmp_cached_35)
        | (_cmp_cached_74)
        | (_cmp("CMF_20_1h", ">", -0.30))
        | (_cmp("CMF_20_4h", ">", -0.30))
        | (_cmp_cached_50)
      )
      # 15m & 1h & 4h down move, 15m & 1h downtrend, 15m still high
      & (
        (_cmp_cached_26)
        | (_cmp_cached_82)
        | (_cmp_cached_35)
        | (_cmp_cached_55)
        | (_cmp_cached_53)
        | (_cmp_cached_17)
      )
      # 15m & 1h & 4h & 1d down move, 15m downtrend, 1d overbought
      & (
        (_cmp_cached_26)
        | (_cmp_cached_82)
        | (_cmp_cached_33)
        | (_cmp("RSI_3_1d", ">", 40.0))
        | (_cmp_cached_74)
        | (_cmp_cached_58)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h downtrend, 15m & 4h still not low enough
      & (
        (_cmp_cached_26)
        | (_cmp_cached_82)
        | (_cmp_cached_33)
        | (_cmp("CMF_20_15m", ">", -0.15))
        | (_cmp("CMF_20_1h", ">", -0.15))
        | (_cmp_cached_71)
        | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 10.0))
        | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 20.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h downtrend, 1h still not low enugh, 4h still high
      & (
        (_cmp_cached_26)
        | (_cmp_cached_82)
        | (_cmp_cached_32)
        | (_cmp("CMF_20_15m", ">", -0.10))
        | (_cmp_cached_53)
        | (_cmp("CMF_20_4h", ">", -0.30))
        | (_cmp_cached_83)
        | (_cmp_cached_37)
      )
      # 15m & 1h & 4h down move, 15m & 1h downtrend, 4h still high
      & (
        (_cmp_cached_26)
        | (_cmp_cached_82)
        | (_cmp_cached_43)
        | (_cmp_cached_73)
        | (_cmp("CMF_20_1h", ">", -0.40))
        | (_cmp_cached_47)
      )
      # 15m & 1h & 4h down move, 15m & 1h downtrend, 1h still high
      & (
        (_cmp_cached_26)
        | (_cmp_cached_57)
        | (_cmp_cached_33)
        | (_cmp_cached_74)
        | (_cmp("CMF_20_1h", ">", -0.30))
        | (_cmp_cached_30)
      )
      # 15m & 1h & 4h & 1d down move, 15m downtrend, 1h still high, 1h & 4h still not low enough, 4h overbought
      & (
        (_cmp_cached_26)
        | (_cmp_cached_57)
        | (_cmp_cached_42)
        | (_cmp("RSI_3_1d", ">", 55.0))
        | (_cmp_cached_74)
        | (_cmp_cached_75)
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 20.0))
        | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 20.0))
        | (_cmp_cached_49)
      )
      # 15m & 1h down move, 1h & 4h still not low enough, 4h high
      & (
        (_cmp_cached_26)
        | (_cmp_cached_57)
        | (_cmp("AROONU_14_1h", "<", 20.0))
        | (_cmp("AROONU_14_4h", "<", 20.0))
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 20.0))
        | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 90.0))
      )
      # 15m & 1h & 4h down move, 1h & 4h still not low enough, 15m & 1h & 4h downtrend
      & (
        (_cmp_cached_26)
        | (_cmp_cached_48)
        | (_cmp_cached_35)
        | (_cmp_cached_43)
        | (_cmp_cached_12)
        | (_cmp_cached_73)
        | (_cmp("CMF_20_1h", ">", -0.25))
        | (_cmp("CMF_20_4h", ">", -0.15))
      )
      # 15m & 1h & 4h down move, 1h & 4h stil not low enough, 15m & 1h & 4h downtrend, 1h still high
      & (
        (_cmp_cached_26)
        | (_cmp_cached_48)
        | (_cmp_cached_33)
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp_cached_55)
        | (_cmp_cached_53)
        | (_cmp_cached_71)
        | (_cmp_cached_22)
      )
      # 15m & 1h & 4h down move, 1h & 4h still not low enough, 15m & 4h still not low enough, 15m & 4h still not low
      & (
        (_cmp_cached_26)
        | (_cmp_cached_48)
        | (_cmp_cached_52)
        | (_cmp_cached_43)
        | (_cmp_cached_12)
        | (_cmp("CMF_20_15m", ">", -0.10))
        | (_cmp_cached_71)
        | (_cmp_cached_50)
        | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 30.0))
      )
      # 15m & 1h & 4h down move, 1h & 4h still not low enough, 15m still high
      & (
        (_cmp_cached_26)
        | (_cmp_cached_48)
        | (_cmp_cached_42)
        | (_cmp_cached_5)
        | (_cmp_cached_4)
        | (_cmp_cached_17)
      )
      # 15m & 1h down move, 1h high, 4h high
      & (
        (_cmp_cached_26)
        | (_cmp_cached_48)
        | (_cmp_cached_31)
        | (_cmp_cached_66)
      )
      # 15m & 1h & 4h down move, 1h still not low enough, 4h still high, 15m still not low enough, 1d high & overbought
      & (
        (_cmp_cached_26)
        | (_cmp_cached_24)
        | (_cmp_cached_52)
        | (_cmp_cached_5)
        | (_cmp_cached_2)
        | (_cmp_cached_50)
        | (_cmp("STOCHRSIk_14_14_3_3_1d", "<", 90.0))
        | (_cmp_cached_68)
      )
      # 15m & 1h & 4h down move, 15m downtrend, 1h still high, 15m still not low enough
      & (
        (_cmp_cached_26)
        | (_cmp_cached_24)
        | (_cmp_cached_32)
        | (_cmp_cached_74)
        | (_cmp_cached_22)
        | (_cmp_cached_50)
      )
      # 15m & 1h down move, 1h & 4h high
      & (
        (_cmp_cached_26)
        | (_cmp_cached_24)
        | (_cmp_cached_6)
        | (_cmp_cached_29)
        | (_cmp_cached_31)
        | (_cmp_cached_16)
      )
      # 15m & 1h & 4h & 1d down move, 15m downtrend
      & (
        (_cmp_cached_26)
        | (_cmp_cached_24)
        | (_cmp_cached_35)
        | (_cmp("RSI_3_1d", ">", 5.0))
        | (_cmp("CMF_20_15m", ">", -0.40))
      )
      # 15m & 1h down move, 15m still not low enough, 1h still high, 4h high, 15m still high, 4h overbought
      & (
        (_cmp_cached_26)
        | (_cmp_cached_24)
        | (_cmp_cached_15)
        | (_cmp_cached_1)
        | (_cmp_cached_36)
        | (_cmp_cached_17)
        | (_cmp_cached_72)
      )
      # 15m & 1h & 4h down move, 15m downtrend, 4h high
      & (
        (_cmp_cached_26)
        | (_cmp_cached_27)
        | (_cmp_cached_35)
        | (_cmp_cached_74)
        | (_cmp_cached_20)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 4h downtrend, 4h high
      & (
        (_cmp_cached_26)
        | (_cmp_cached_14)
        | (_cmp_cached_32)
        | (_cmp_cached_15)
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp_cached_71)
        | (_cmp_cached_70)
      )
      # 15m & 1h & 4h down move, 1h high, 4h downtrend
      & (
        (_cmp_cached_26)
        | (_cmp_cached_14)
        | (_cmp_cached_32)
        | (_cmp_cached_40)
        | (_cmp("ROC_9_4h", ">", -40.0))
      )
      # 15m & 1h & 4h down move, 1h & 4h still high, 15m downtrend
      & (
        (_cmp_cached_26)
        | (_cmp_cached_14)
        | (_cmp_cached_39)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_73)
        | (_cmp_cached_37)
        | (_cmp_cached_47)
      )
      # 15m & 1h down move, 15m still not low enough, 1h & 4h high, 1h high, 4h overbought
      & (
        (_cmp_cached_26)
        | (_cmp_cached_14)
        | (_cmp_cached_15)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_31)
        | (_cmp_cached_49)
      )
      # 15m & 1h & 4h down move, 15m & 1h still not low enough, 4h still high, 1h & 4h still high, 15m still high
      & (
        (_cmp_cached_26)
        | (_cmp_cached_23)
        | (_cmp_cached_52)
        | (_cmp_cached_15)
        | (_cmp_cached_5)
        | (_cmp_cached_4)
        | (_cmp_cached_75)
        | (_cmp_cached_37)
        | (_cmp_cached_28)
      )
      # 15m & 1h & 4h down move, 1h & 4h still high, 4h high
      & (
        (_cmp_cached_26)
        | (_cmp_cached_14)
        | (_cmp_cached_18)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_20)
        | (_cmp_cached_66)
      )
      # 15m & 1h & 3h down move, 1h & 4h still not low enough, 15m downtrend, 1h still high
      & (
        (_cmp_cached_26)
        | (_cmp_cached_23)
        | (_cmp_cached_52)
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp_cached_74)
        | (_cmp_cached_30)
      )
      # 15m & 1h & 4h down move, 1h & 4h still high, 1d overbought
      & (
        (_cmp_cached_26)
        | (_cmp_cached_46)
        | (_cmp_cached_39)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_37)
        | (_cmp("ROC_9_1d", "<", 70.0))
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 1h high, 1d overbought
      & (
        (_cmp_cached_26)
        | (_cmp_cached_46)
        | (_cmp_cached_39)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp_cached_80)
        | (_cmp("ROC_9_1d", "<", 60.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 15m still not low enough
      & (
        (_cmp_cached_26)
        | (_cmp_cached_60)
        | (_cmp_cached_18)
        | (_cmp("RSI_14_15m", "<", 10.0))
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp_cached_63)
        | (_cmp_cached_50)
      )
      # 15m & 1h down move, 15m still not low enough, 1h & 4h high, 1h & 4h overbought
      & (
        (_cmp_cached_26)
        | (_cmp_cached_60)
        | (_cmp_cached_0)
        | (_cmp("RSI_14_1h", "<", 60.0))
        | (_cmp_cached_84)
        | (_cmp("AROONU_14_1h", "<", 75.0))
        | (_cmp_cached_76)
        | (_cmp_cached_67)
        | (_cmp_cached_49)
      )
      # 15m & 1h & 4h down move, 1h & 4h still high, 15m downtrend, 1h still high
      & (
        (_cmp_cached_26)
        | (_cmp("RSI_3_1h", ">", 65.0))
        | (_cmp_cached_44)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp("CMF_20_15m", ">", -0.40))
        | (_cmp_cached_22)
      )
      # 15m & 4h down move, 15m & 1h still not low enough, 4h still high, 1h & 4h still not low enough, 1d overbought
      & (
        (_cmp_cached_26)
        | (_cmp_cached_54)
        | (_cmp("RSI_14_15m", "<", 10.0))
        | (_cmp_cached_5)
        | (_cmp_cached_4)
        | (_cmp("AROONU_14_1h", "<", 20.0))
        | (_cmp("AROONU_14_4h", "<", 20.0))
        | (_cmp("ROC_9_1d", "<", 20.0))
      )
      # 15m down move, 15m still not low enough, 1h & 4h high, 1h overbought
      & (
        (_cmp_cached_26)
        | (_cmp_cached_0)
        | (_cmp("RSI_14_1h", "<", 60.0))
        | (_cmp_cached_36)
        | (_cmp_cached_31)
        | (_cmp_cached_16)
        | (_cmp_cached_67)
      )
      # 15m down move, 15m still not low enough, 1h & 4h high, 4h overbought
      & (
        (_cmp_cached_26)
        | (_cmp_cached_0)
        | (_cmp("RSI_14_1h", "<", 60.0))
        | (_cmp_cached_36)
        | (_cmp_cached_40)
        | (_cmp_cached_16)
        | (_cmp_cached_80)
        | (_cmp_cached_49)
      )
      # 15m & 1h & 4h down move, 1h & 4h still not low enough, 15m & 1h & 4h downtrend, 1h & 4h downtrend
      & (
        (_cmp_cached_9)
        | (_cmp_cached_57)
        | (_cmp("RSI_3_4h", ">", 10.0))
        | (_cmp("RSI_14_1h", "<", 10.0))
        | (_cmp("RSI_14_4h", "<", 20.0))
        | (_cmp("CMF_20_15m", ">", -0.15))
        | (_cmp("CMF_20_1h", ">", -0.15))
        | (_cmp("CMF_20_4h", ">", -0.15))
        | (_cmp("ROC_9_1h", ">", -20.0))
        | (_cmp("ROC_9_4h", ">", -20.0))
      )
      # 15m & 1h & 4h down move, 4h still high, 15m & 1h & 4h downtrend
      & (
        (_cmp_cached_9)
        | (_cmp_cached_57)
        | (_cmp("RSI_3_4h", ">", 15.0))
        | (_cmp_cached_4)
        | (_cmp_cached_55)
        | (_cmp_cached_53)
        | (_cmp_cached_71)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h downtrend, 4h still high
      & (
        (_cmp_cached_9)
        | (_cmp_cached_57)
        | (_cmp("RSI_3_4h", ">", 15.0))
        | (_cmp_cached_73)
        | (_cmp("CMF_20_1h", ">", -0.15))
        | (_cmp("CMF_20_4h", ">", -0.15))
        | (_cmp("AROONU_14_4h", "<", 40.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h downtrend, 15m still high
      & (
        (_cmp_cached_9)
        | (_cmp_cached_57)
        | (_cmp("RSI_3_4h", ">", 15.0))
        | (_cmp_cached_74)
        | (_cmp("CMF_20_1h", ">", -0.40))
        | (_cmp_cached_28)
      )
      # 15m & 1h & 4h down move, 1h & 4h downtrend, 1h still high, 1h downtrend
      & (
        (_cmp_cached_9)
        | (_cmp_cached_57)
        | (_cmp("RSI_3_4h", ">", 15.0))
        | (_cmp("CMF_20_1h", ">", -0.30))
        | (_cmp("CMF_20_4h", ">", -0.30))
        | (_cmp_cached_22)
        | (_cmp("ROC_9_1h", ">", -15.0))
      )
      # 15m & 1h & 4h down move, 1h & 4h still not low enough, 15m still high
      & (
        (_cmp_cached_9)
        | (_cmp_cached_57)
        | (_cmp("RSI_3_4h", ">", 15.0))
        | (_cmp_cached_83)
        | (_cmp("AROONU_14_4h", "<", 30.0))
        | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 40.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h downtrend, 15m still high, 4h still not low enough
      & (
        (_cmp_cached_9)
        | (_cmp_cached_57)
        | (_cmp_cached_54)
        | (_cmp_cached_55)
        | (_cmp("CMF_20_1h", ">", -0.25))
        | (_cmp("CMF_20_4h", ">", -0.25))
        | (_cmp_cached_28)
        | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 20.0))
      )
      # 15m & 1h & 4h down move, 1h & 15m still high, 1h downtrend
      & (
        (_cmp_cached_9)
        | (_cmp_cached_57)
        | (_cmp_cached_54)
        | (_cmp_cached_75)
        | (_cmp_cached_28)
        | (_cmp("ROC_9_1h", ">", -10.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h downtrend, 4h high
      & (
        (_cmp_cached_9)
        | (_cmp_cached_57)
        | (_cmp_cached_35)
        | (_cmp_cached_55)
        | (_cmp_cached_53)
        | (_cmp_cached_71)
        | (_cmp_cached_34)
      )
      # 15m & 1h & 4h down move, 4h still not low enough, 1h still high, 4h high
      & (
        (_cmp_cached_9)
        | (_cmp_cached_57)
        | (_cmp_cached_35)
        | (_cmp_cached_12)
        | (_cmp_cached_75)
        | (_cmp_cached_20)
        | (_cmp_cached_70)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 15m & 1h downtrend, 15m still not low enough
      & (
        (_cmp_cached_9)
        | (_cmp_cached_57)
        | (_cmp_cached_33)
        | (_cmp("RSI_14_15m", "<", 10.0))
        | (_cmp_cached_43)
        | (_cmp_cached_12)
        | (_cmp_cached_55)
        | (_cmp("CMF_20_1h", ">", -0.15))
        | (_cmp_cached_50)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 15m & 1h downtrend, 4h still high, 4h downtrend
      & (
        (_cmp_cached_9)
        | (_cmp_cached_57)
        | (_cmp_cached_33)
        | (_cmp_cached_15)
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp("CMF_20_15m", ">", -0.15))
        | (_cmp("CMF_20_1h", ">", -0.25))
        | (_cmp("AROONU_14_4h", "<", 40.0))
        | (_cmp("ROC_9_4h", ">", -20.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h still not low enough, 4h still high, 15m & 1h downtrend
      & (
        (_cmp_cached_9)
        | (_cmp_cached_57)
        | (_cmp_cached_33)
        | (_cmp_cached_15)
        | (_cmp_cached_5)
        | (_cmp_cached_4)
        | (_cmp("ROC_9_15m", ">", -10.0))
        | (_cmp("ROC_9_1h", ">", -20.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h still not low enough, 4h still high, 1d overbought
      & (
        (_cmp_cached_9)
        | (_cmp_cached_57)
        | (_cmp_cached_33)
        | (_cmp_cached_15)
        | (_cmp_cached_5)
        | (_cmp_cached_4)
        | (_cmp("ROC_9_1d", "<", 200.0))
      )
      # 15m & 1h down move, 1h still high, 4h high & overbought
      & (
        (_cmp_cached_9)
        | (_cmp_cached_57)
        | (_cmp_cached_1)
        | (_cmp_cached_84)
        | (_cmp_cached_20)
        | (_cmp_cached_66)
        | (_cmp("ROC_9_4h", "<", 80.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h still not low enough, 4h still high, 4h overbought
      & (
        (_cmp_cached_9)
        | (_cmp_cached_48)
        | (_cmp_cached_54)
        | (_cmp_cached_0)
        | (_cmp_cached_5)
        | (_cmp_cached_4)
        | (_cmp_cached_37)
        | (_cmp_cached_77)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 15m & 1h downtrend, 15m still not low enough
      & (
        (_cmp_cached_9)
        | (_cmp_cached_48)
        | (_cmp_cached_52)
        | (_cmp_cached_15)
        | (_cmp_cached_43)
        | (_cmp_cached_12)
        | (_cmp_cached_73)
        | (_cmp("CMF_20_1h", ">", -0.25))
        | (_cmp_cached_50)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 15m & 1h & 4h downtrend, 1h still not low enough
      & (
        (_cmp_cached_9)
        | (_cmp_cached_48)
        | (_cmp_cached_52)
        | (_cmp_cached_15)
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp_cached_73)
        | (_cmp("CMF_20_1h", ">", -0.25))
        | (_cmp("CMF_20_4h", ">", -0.25))
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 30.0))
      )
      # 15m & 1h & 4h down move, 1h still not low enough, 4h high, 1d overbought
      & (
        (_cmp_cached_9)
        | (_cmp_cached_48)
        | (_cmp_cached_25)
        | (_cmp_cached_5)
        | (_cmp_cached_36)
        | (_cmp("ROC_9_1d", "<", 200.0))
      )
      # 15m & 1h & 4h down move, 1h downtrend, 4h high
      & (
        (_cmp_cached_9)
        | (_cmp_cached_48)
        | (_cmp_cached_42)
        | (_cmp_cached_2)
        | (_cmp("CMF_20_1h", ">", -0.4))
        | (_cmp_cached_20)
        | (_cmp_cached_70)
      )
      # 15m & 1h & 4h down move, 1h & 4h still not low enough, 1h & 4h downtrend, 15m & 1h & 4h still not low enough
      & (
        (_cmp_cached_9)
        | (_cmp_cached_24)
        | (_cmp_cached_54)
        | (_cmp_cached_43)
        | (_cmp("RSI_14_4h", "<", 20.0))
        | (_cmp("CMF_20_1h", ">", -0.15))
        | (_cmp_cached_71)
        | (_cmp("AROONU_14_15m", "<", 25.0))
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 30.0))
        | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 30.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h downtrend, 15m still high
      & (
        (_cmp_cached_9)
        | (_cmp_cached_24)
        | (_cmp_cached_54)
        | (_cmp_cached_55)
        | (_cmp("CMF_20_1h", ">", -0.30))
        | (_cmp("CMF_20_4h", ">", -0.30))
        | (_cmp_cached_28)
      )
      # 15m & 1h & 4h down move, 1h still not low enough, 4h still high, 1h downtrend, 1d overbought
      & (
        (_cmp_cached_9)
        | (_cmp_cached_24)
        | (_cmp_cached_54)
        | (_cmp_cached_5)
        | (_cmp_cached_4)
        | (_cmp("CMF_20_1h", ">", -0.25))
        | (_cmp_cached_37)
        | (_cmp("CCI_20_1h", "<", -200.0))
        | (_cmp("CCI_20_4h", "<", -0.0))
        | (_cmp("ROC_9_1d", "<", 30.0))
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h high
      & (
        (_cmp_cached_9)
        | (_cmp_cached_24)
        | (_cmp_cached_35)
        | (_cmp_cached_63)
        | (_cmp("AROONU_14_1h", "<", 60.0))
        | (_cmp_cached_16)
      )
      # 15m & 1h & 4h & 1d down move, 1h still not low enough, 4h still high, 1d overbought
      & (
        (_cmp_cached_9)
        | (_cmp_cached_24)
        | (_cmp_cached_35)
        | (_cmp("RSI_3_1d", ">", 45.0))
        | (_cmp_cached_5)
        | (_cmp_cached_4)
        | (_cmp_cached_51)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 4h overbought
      & (
        (_cmp_cached_9)
        | (_cmp_cached_24)
        | (_cmp_cached_52)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp_cached_47)
        | (_cmp_cached_49)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 1h high
      & (
        (_cmp_cached_9)
        | (_cmp_cached_24)
        | (_cmp_cached_32)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp_cached_63)
        | (_cmp_cached_31)
        | (_cmp_cached_30)
        | (_cmp_cached_47)
      )
      # 15m & 1h & 4h down move, 15m & 1h still not low enough, 4h stil high, 1h & 4h downtrend, 1h & 4h still not low
      & (
        (_cmp_cached_9)
        | (_cmp_cached_24)
        | (_cmp_cached_25)
        | (_cmp("RSI_14_15m", "<", 10.0))
        | (_cmp_cached_5)
        | (_cmp_cached_4)
        | (_cmp_cached_53)
        | (_cmp("CMF_20_4h", ">", -0.30))
        | (_cmp_cached_83)
        | (_cmp("AROONU_14_4h", "<", 30.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h still not low enough, 1h & 4h still high, 1d overbought
      & (
        (_cmp_cached_9)
        | (_cmp_cached_24)
        | (_cmp_cached_44)
        | (_cmp_cached_0)
        | (_cmp_cached_5)
        | (_cmp_cached_2)
        | (_cmp_cached_59)
        | (_cmp_cached_58)
      )
      # 15m & 1h down move, 15m still not low enough, 1h still high, 4h high, 4h overbought
      & (
        (_cmp_cached_9)
        | (_cmp_cached_24)
        | (_cmp_cached_15)
        | (_cmp_cached_1)
        | (_cmp_cached_29)
        | (_cmp_cached_20)
        | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 90.0))
        | (_cmp_cached_72)
      )
      # 15m & 1h down move, 15m still not low enough, 1h & 4h high, 1h & 1d overbought
      & (
        (_cmp_cached_9)
        | (_cmp_cached_24)
        | (_cmp_cached_0)
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp_cached_22)
        | (_cmp_cached_16)
        | (_cmp_cached_49)
        | (_cmp("ROC_9_1d", "<", 20.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 1h & 4h downtrend, 1h & 4h still high
      & (
        (_cmp_cached_9)
        | (_cmp_cached_27)
        | (_cmp_cached_35)
        | (_cmp_cached_15)
        | (_cmp_cached_43)
        | (_cmp("RSI_14_4h", "<", 20.0))
        | (_cmp("CMF_20_1h", ">", -0.15))
        | (_cmp_cached_71)
        | (_cmp_cached_59)
        | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 40.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h still not low, 4h still high, 15m & 1h downtrend, 4h not low, 4h downtrend
      & (
        (_cmp_cached_9)
        | (_cmp_cached_27)
        | (_cmp_cached_35)
        | (_cmp_cached_15)
        | (_cmp_cached_5)
        | (_cmp_cached_4)
        | (_cmp("CMF_20_15m", ">", -0.10))
        | (_cmp_cached_53)
        | (_cmp("AROONU_14_4h", "<", 20.0))
        | (_cmp("ROC_9_4h", ">", -10.0))
      )
      # 15m & 1h & 4h down move, 1h & 4h not low enouhg, 15m downtrend, 4h high, 1d overbought
      & (
        (_cmp_cached_9)
        | (_cmp_cached_27)
        | (_cmp_cached_35)
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp_cached_74)
        | (_cmp("AROONU_14_4h", "<", 60.0))
        | (_cmp("ROC_9_1d", "<", 25.0))
      )
      # 15m & 1h & 4h & 1d down move, 15m & 1h still not low enough, 4h still high. 1d high & overbought
      & (
        (_cmp_cached_9)
        | (_cmp_cached_27)
        | (_cmp_cached_35)
        | (_cmp("RSI_3_1d", ">", 60.0))
        | (_cmp_cached_0)
        | (_cmp_cached_5)
        | (_cmp_cached_4)
        | (_cmp("AROONU_14_1d", "<", 70.0))
        | (_cmp_cached_68)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h downtrend, 1h & 4h still not low enough, 1h & 4h downtrend
      & (
        (_cmp_cached_9)
        | (_cmp_cached_27)
        | (_cmp_cached_35)
        | (_cmp_cached_55)
        | (_cmp_cached_53)
        | (_cmp_cached_71)
        | (_cmp("AROONU_14_1h", "<", 25.0))
        | (_cmp("AROONU_14_4h", "<", 25.0))
        | (_cmp("ROC_9_1h", ">", -10.0))
        | (_cmp_cached_78)
      )
      # 15m & 1h & 1d down move, 1h still not low enough, 4h high & overbought
      & (
        (_cmp_cached_9)
        | (_cmp_cached_27)
        | (_cmp("RSI_3_1d", ">", 25.0))
        | (_cmp_cached_5)
        | (_cmp_cached_36)
        | (_cmp_cached_75)
        | (_cmp_cached_76)
        | (_cmp("ROC_9_1h", ">", -20.0))
        | (_cmp("ROC_9_4h", "<", 30.0))
      )
      # 15m & 1h & 1d down move, 15m still not low enough, 1h & 4h still high, 1h high, 4h overbought
      & (
        (_cmp_cached_9)
        | (_cmp_cached_27)
        | (_cmp("RSI_3_1d", ">", 30.0))
        | (_cmp_cached_15)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_63)
        | (_cmp_cached_40)
        | (_cmp_cached_49)
      )
      # 15m & 1h & 4h down move, 15m & 1h still not low enough, 4h still high, 15m & 1h downtrend
      & (
        (_cmp_cached_9)
        | (_cmp_cached_14)
        | (_cmp_cached_33)
        | (_cmp_cached_15)
        | (_cmp_cached_5)
        | (_cmp_cached_4)
        | (_cmp_cached_74)
        | (_cmp("CMF_20_1h", ">", -0.25))
      )
      # 15m & 1h & 4h down move, 1h & 4h still high, 4h high, 4h & 1d overbought
      & (
        (_cmp_cached_9)
        | (_cmp_cached_14)
        | (_cmp_cached_25)
        | (_cmp("RSI_14_1h", "<", 45.0))
        | (_cmp("RSI_14_4h", "<", 55.0))
        | (_cmp_cached_34)
        | (_cmp_cached_72)
        | (_cmp_cached_51)
      )
      # 15m & 1h & 4h down move, 1h & 4h still high, 15m downtrend, 4h high
      & (
        (_cmp_cached_9)
        | (_cmp_cached_14)
        | (_cmp_cached_18)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_73)
        | (_cmp_cached_20)
      )
      # 15m & 1h down move, 4h high, 1d downtrend, 1h still not low enough, 1d overbought
      & (
        (_cmp_cached_9)
        | (_cmp_cached_14)
        | (_cmp_cached_29)
        | (_cmp("CMF_20_1d", ">", -0.3))
        | (_cmp_cached_83)
        | (_cmp_cached_58)
      )
      # 15m & 1h & 4h & 1d down move, 15m & 1h not low enough, 4h high
      & (
        (_cmp_cached_9)
        | (_cmp_cached_23)
        | (_cmp_cached_52)
        | (_cmp("RSI_3_1d", ">", 15.0))
        | (_cmp_cached_0)
        | (_cmp("RSI_14_1h", "<", 35.0))
        | (_cmp_cached_81)
        | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 85.0))
      )
      # 15m & 1h & 4h & 1d down move, 15m & 1 & 4h still not low enough, 1h still high, 4h high
      & (
        (_cmp_cached_9)
        | (_cmp_cached_23)
        | (_cmp_cached_52)
        | (_cmp("RSI_3_1d", ">", 35.0))
        | (_cmp_cached_0)
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp_cached_59)
        | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 60.0))
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h still high, 4h high & overbought
      & (
        (_cmp_cached_9)
        | (_cmp_cached_23)
        | (_cmp_cached_18)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_20)
        | (_cmp("ROC_9_4h", "<", 80.0))
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 1h still high, 4h high & overbought
      & (
        (_cmp_cached_9)
        | (_cmp_cached_23)
        | (_cmp_cached_44)
        | (_cmp_cached_15)
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp_cached_22)
        | (_cmp_cached_16)
        | (_cmp_cached_72)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 15m & 1h & 4h downtrend, 1h still high
      & (
        (_cmp_cached_9)
        | (_cmp_cached_19)
        | (_cmp_cached_32)
        | (_cmp_cached_15)
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp_cached_74)
        | (_cmp_cached_64)
        | (_cmp_cached_62)
        | (_cmp_cached_30)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 1h & 4h still high, 1d downtrend
      & (
        (_cmp_cached_9)
        | (_cmp_cached_19)
        | (_cmp_cached_18)
        | (_cmp_cached_0)
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp("AROONU_14_15m", "<", 10.0))
        | (_cmp_cached_30)
        | (_cmp_cached_47)
        | (_cmp("ROC_9_1d", ">", -50.0))
      )
      # 15m & 1h down move, 4h still high, 15m downtrend, 1h & 1d high
      & (
        (_cmp_cached_9)
        | (_cmp_cached_19)
        | (_cmp_cached_2)
        | (_cmp("CMF_20_15m", ">", -0.3))
        | (_cmp("AROONU_14_1h", "<", 60.0))
        | (_cmp("AROONU_14_1d", "<", 90.0))
        | (_cmp("STOCHRSIk_14_14_3_3_1d", "<", 80.0))
      )
      # 15m & 1h down move, 15m & 1h still high, 1h & 4h high, 1d overbought
      & (
        (_cmp_cached_9)
        | (_cmp_cached_19)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_29)
        | (_cmp_cached_31)
        | (_cmp_cached_16)
        | (_cmp_cached_51)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 1h & 4h high, 4h overbought
      & (
        (_cmp_cached_9)
        | (_cmp_cached_21)
        | (_cmp_cached_18)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp_cached_40)
        | (_cmp_cached_16)
        | (_cmp_cached_72)
      )
      # 15m & 1h & 4h down move, 1h & 4h sitll high, 15m & 1h & 4h downtrend, 1h & 4h still high
      & (
        (_cmp_cached_9)
        | (_cmp_cached_46)
        | (_cmp_cached_44)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp_cached_55)
        | (_cmp_cached_53)
        | (_cmp("CMF_20_4h", ">", -0.25))
        | (_cmp_cached_59)
        | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 40.0))
      )
      # 15m & 1h & 4h down move, 15m stil not low enough, 1h & 4h still high, 15m & 4h still high, 1d overbought
      & (
        (_cmp_cached_9)
        | (_cmp_cached_46)
        | (_cmp_cached_39)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_17)
        | (_cmp_cached_37)
        | (_cmp("ROC_9_1d", "<", 200.0))
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 1h & 4h downtrend, 1h high
      & (
        (_cmp_cached_9)
        | (_cmp_cached_46)
        | (_cmp_cached_39)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp_cached_64)
        | (_cmp("CMF_20_4h", ">", -0.25))
        | (_cmp_cached_80)
      )
      # 15m & 1h & 4h down move, 1h & 4h still not low enough, 15m & 4h downtrend, 1h & 4h still high
      & (
        (_cmp_cached_9)
        | (_cmp_cached_46)
        | (_cmp_cached_39)
        | (_cmp_cached_43)
        | (_cmp_cached_12)
        | (_cmp("CMF_20_15m", ">", -0.40))
        | (_cmp_cached_71)
        | (_cmp_cached_75)
        | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 40.0))
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 14h & 1d overbought
      & (
        (_cmp_cached_9)
        | (_cmp_cached_46)
        | (_cmp_cached_44)
        | (_cmp_cached_15)
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp_cached_38)
        | (_cmp_cached_68)
      )
      # 15m & 1h down move, 15m still not low enough, 1h & 4h high, 4h overbought
      & (
        (_cmp_cached_9)
        | (_cmp_cached_46)
        | (_cmp_cached_29)
        | (_cmp("AROONU_14_15m", "<", 20.0))
        | (_cmp_cached_31)
        | (_cmp_cached_16)
        | (_cmp("ROC_9_4h", "<", 30.0))
      )
      # 15m & 1h down move, 15m still not low enough, 1h & 4h high & overbought
      & (
        (_cmp_cached_9)
        | (_cmp_cached_46)
        | (_cmp_cached_0)
        | (_cmp("RSI_14_1h", "<", 70.0))
        | (_cmp_cached_29)
        | (_cmp("AROONU_14_1h", "<", 60.0))
        | (_cmp_cached_16)
        | (_cmp("ROC_9_1h", "<", 20.0))
        | (_cmp("ROC_9_4h", "<", 50.0))
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 1h & 4h downtrend, 4h high, 1h overbought
      & (
        (_cmp_cached_9)
        | (_cmp_cached_41)
        | (_cmp_cached_42)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_64)
        | (_cmp_cached_62)
        | (_cmp_cached_20)
        | (_cmp_cached_67)
      )
      # 15m & 1h & 4h down move, 1h & 4h downtrend, 15m still high, 1h high
      & (
        (_cmp_cached_9)
        | (_cmp_cached_41)
        | (_cmp_cached_42)
        | (_cmp("CMF_20_1h", ">", -0.0))
        | (_cmp("CMF_20_4h", ">", -0.4))
        | (_cmp_cached_17)
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 90.0))
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 1d overbought
      & (
        (_cmp_cached_9)
        | (_cmp_cached_41)
        | (_cmp_cached_44)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_75)
        | (_cmp("AROONU_14_4h", "<", 40.0))
        | (_cmp("ROC_9_1d", "<", 200.0))
      )
      # 15m & 1h down move, 15m still not low enough, 1h & 4h still high, 15m & 4h high, 4h & 1d overbought
      & (
        (_cmp_cached_9)
        | (_cmp_cached_41)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_36)
        | (_cmp_cached_11)
        | (_cmp_cached_20)
        | (_cmp_cached_49)
        | (_cmp_cached_51)
      )
      # 15m & 1h down move, 15m & 1h still high, 4h high, 15m still not low enough, 1h & 4h high, 4h overbought
      & (
        (_cmp_cached_9)
        | (_cmp_cached_41)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_36)
        | (_cmp("AROONU_14_15m", "<", 10.0))
        | (_cmp_cached_31)
        | (_cmp("AROONU_14_4h", "<", 60.0))
        | (_cmp_cached_77)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 1h & 4h downtrend, 15m & 1h high
      & (
        (_cmp_cached_9)
        | (_cmp_cached_60)
        | (_cmp_cached_18)
        | (_cmp_cached_0)
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp("CMF_20_1h", ">", -0.0))
        | (_cmp("CMF_20_4h", ">", -0.0))
        | (_cmp_cached_17)
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 80.0))
      )
      # 15m & 1h down move, 15m & 4h high, 4h overbought
      & (
        (_cmp_cached_9)
        | (_cmp("RSI_3_1h", ">", 65.0))
        | (_cmp("AROONU_14_15m", "<", 80.0))
        | (_cmp_cached_56)
        | (_cmp("ROC_9_4h", "<", 100.0))
      )
      # 15m & 1h down move, 15m & 1h & 4h still high, 1h & 4h high, 1h & 4h overbought
      & (
        (_cmp_cached_9)
        | (_cmp("RSI_3_1h", ">", 65.0))
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp_cached_40)
        | (_cmp_cached_16)
        | (_cmp("ROC_9_1h", "<", 20.0))
        | (_cmp("ROC_9_4h", "<", 30.0))
      )
      # 15m & 4h & 1d down move, 15m high, 15m & 4h still high
      & (
        (_cmp_cached_9)
        | (_cmp("RSI_3_4h", ">", 15.0))
        | (_cmp("RSI_3_1d", ">", 20.0))
        | (_cmp_cached_61)
        | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 40.0))
        | (_cmp_cached_47)
      )
      # 15m & 4h & 1d down move, 15m & 1h still not low enough, 1h still high, 4h & 1d downtrend
      & (
        (_cmp_cached_9)
        | (_cmp_cached_54)
        | (_cmp("RSI_3_1d", ">", 20.0))
        | (_cmp_cached_0)
        | (_cmp_cached_5)
        | (_cmp_cached_59)
        | (_cmp("ROC_9_4h", ">", -25.0))
        | (_cmp("ROC_9_1d", ">", -50.0))
      )
      # 15m & 4h down move, 1h & 4h stil high, 15m high, 4h overbought
      & (
        (_cmp_cached_9)
        | (_cmp_cached_18)
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp_cached_61)
        | (_cmp("ROC_9_4h", "<", 30.0))
      )
      # 15m down move, 15m still not low enough, 1h & 4h high & overbought
      & (
        (_cmp_cached_9)
        | (_cmp_cached_0)
        | (_cmp("RSI_14_1h", "<", 70.0))
        | (_cmp_cached_84)
        | (_cmp_cached_69)
        | (_cmp_cached_16)
        | (_cmp("ROC_9_1h", "<", 30.0))
        | (_cmp("ROC_9_4h", "<", 80.0))
      )
      # 15m down move, 15m & 1h & 4h still high, 15m still high, 4h high, 4h overbought
      & (
        (_cmp_cached_9)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_36)
        | (_cmp_cached_17)
        | (_cmp_cached_20)
        | (_cmp_cached_81)
        | (_cmp_cached_59)
        | (_cmp_cached_47)
        | (_cmp_cached_77)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 1h & 4h downtrend
      & (
        (_cmp_cached_8)
        | (_cmp_cached_48)
        | (_cmp("RSI_3_4h", ">", 15.0))
        | (_cmp_cached_15)
        | (_cmp_cached_43)
        | (_cmp("RSI_14_4h", "<", 20.0))
        | (_cmp("ROC_9_1h", ">", -20.0))
        | (_cmp("ROC_9_4h", ">", -35.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 1h high, 15m still not low enough
      & (
        (_cmp_cached_8)
        | (_cmp_cached_48)
        | (_cmp("RSI_3_4h", ">", 15.0))
        | (_cmp_cached_15)
        | (_cmp_cached_43)
        | (_cmp_cached_12)
        | (_cmp_cached_40)
        | (_cmp_cached_81)
      )
      # 15m & 1h & 4h & 1d down move, 1h & 4h still not low enough, 1h & 4h downtrend, 4h still high
      & (
        (_cmp_cached_8)
        | (_cmp_cached_48)
        | (_cmp_cached_35)
        | (_cmp("RSI_3_1d", ">", 25.0))
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp_cached_64)
        | (_cmp_cached_62)
        | (_cmp("AROONU_14_4h", "<", 40.0))
        | (_cmp("ROC_9_4h", ">", -20.0))
      )
      # 15m & 1h & 4h & 1d down move, 1h still not low enough, 4h still high, 4h downtrend, 1h still not low enough
      & (
        (_cmp_cached_8)
        | (_cmp_cached_48)
        | (_cmp_cached_52)
        | (_cmp("RSI_3_1d", ">", 50.0))
        | (_cmp_cached_43)
        | (_cmp_cached_4)
        | (_cmp("CMF_20_4h", ">", -0.30))
        | (_cmp("AROONU_14_1h", "<", 20.0))
      )
      # 15m & 1h & 4h & 1d down move, 15m downtrend, 15m & 4h high, 1d downtrend
      & (
        (_cmp_cached_8)
        | (_cmp_cached_48)
        | (_cmp_cached_52)
        | (_cmp("RSI_3_1d", ">", 50.0))
        | (_cmp_cached_55)
        | (_cmp_cached_11)
        | (_cmp_cached_34)
        | (_cmp("ROC_9_1d", ">", -40.0))
      )
      # 15m & 1h & 4h & 1d down move, 4h still not low enough, 15m & 1h & 4h downtrend
      & (
        (_cmp_cached_8)
        | (_cmp_cached_48)
        | (_cmp_cached_32)
        | (_cmp("RSI_3_1d", ">", 40.0))
        | (_cmp("RSI_14_15m", ">", 20.0))
        | (_cmp_cached_12)
        | (_cmp_cached_73)
        | (_cmp_cached_53)
        | (_cmp("CMF_20_4h", ">", -0.0))
        | (_cmp("AROONU_14_4h", "<", 20.0))
      )
      # 15m & 1h & 4h down move, 1h still not low enough, 4h high, 1h downtrend
      & (
        (_cmp_cached_8)
        | (_cmp_cached_48)
        | (_cmp_cached_25)
        | (_cmp_cached_5)
        | (_cmp("RSI_14_4h", "<", 45.0))
        | (_cmp_cached_75)
        | (_cmp_cached_76)
        | (_cmp("ROC_9_1h", ">", -30.0))
      )
      # 15m & 1h & 4h down move, 4h high, 1d overbought
      & (
        (_cmp_cached_8)
        | (_cmp_cached_48)
        | (_cmp_cached_25)
        | (_cmp_cached_20)
        | (_cmp("ROC_9_1d", "<", 150.0))
      )
      # 15m & 1h down move, 15m & 1h still not low enough, 4h still high, 4h high
      & (
        (_cmp_cached_8)
        | (_cmp_cached_48)
        | (_cmp_cached_15)
        | (_cmp_cached_43)
        | (_cmp_cached_2)
        | (_cmp_cached_63)
        | (_cmp_cached_83)
        | (_cmp("AROONU_14_4h", "<", 60.0))
        | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 90.0))
      )
      # 15m & 1h down move, 15m still not low enough, 1h still high, 4h high. 4h overbought
      & (
        (_cmp_cached_8)
        | (_cmp_cached_48)
        | (_cmp_cached_15)
        | (_cmp_cached_6)
        | (_cmp_cached_29)
        | (_cmp_cached_22)
        | (_cmp_cached_20)
        | (_cmp("ROC_9_4h", "<", 50.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h still not low enough, 4h still high, 15m downtrend
      & (
        (_cmp_cached_8)
        | (_cmp_cached_24)
        | (_cmp_cached_35)
        | (_cmp_cached_15)
        | (_cmp_cached_5)
        | (_cmp_cached_4)
        | (_cmp("CMF_20_15m", ">", -0.50))
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 15m high, 1h still high
      & (
        (_cmp_cached_8)
        | (_cmp_cached_24)
        | (_cmp_cached_35)
        | (_cmp_cached_0)
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp_cached_11)
        | (_cmp_cached_59)
      )
      # 15m & 1h & 4h down move, 15m & 1h still not low enough, 4h still high, 15m downtrend, 4h high, 1h downtrend
      & (
        (_cmp_cached_8)
        | (_cmp_cached_24)
        | (_cmp_cached_33)
        | (_cmp_cached_15)
        | (_cmp_cached_5)
        | (_cmp_cached_4)
        | (_cmp_cached_74)
        | (_cmp("AROONU_14_4h", "<", 60.0))
        | (_cmp("ROC_9_1h", ">", -10.0))
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 1h & 4h high
      & (
        (_cmp_cached_8)
        | (_cmp_cached_24)
        | (_cmp_cached_25)
        | (_cmp_cached_15)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp("AROONU_14_1h", "<", 60.0))
        | (_cmp_cached_56)
      )
      # 15m & 1h & 4h down move, 15m & 1h still not low enough, 4h still high, 1h & 4h downtrend, 1h high
      & (
        (_cmp_cached_8)
        | (_cmp_cached_24)
        | (_cmp_cached_18)
        | (_cmp_cached_0)
        | (_cmp_cached_5)
        | (_cmp_cached_4)
        | (_cmp("CMF_20_1h", ">", -0.40))
        | (_cmp_cached_62)
        | (_cmp_cached_40)
      )
      # 15m & 1h down move, 15m still not low enough, 1h & 4h still high, 15m downtrend, 1h still high, 4h high
      & (
        (_cmp_cached_8)
        | (_cmp_cached_24)
        | (_cmp_cached_0)
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp_cached_73)
        | (_cmp_cached_22)
        | (_cmp_cached_16)
        | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 90.0))
      )
      # 15m & 1h & 4h & 1d down move, 15m still not low enough, 1h & 4h still high, 4h high, 1d overbought
      & (
        (_cmp_cached_8)
        | (_cmp_cached_27)
        | (_cmp_cached_18)
        | (_cmp("RSI_3_1d", ">", 60.0))
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_20)
        | (_cmp_cached_47)
        | (_cmp("ROC_9_1d", "<", 30.0))
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 1d overbought
      & (
        (_cmp_cached_8)
        | (_cmp_cached_27)
        | (_cmp_cached_44)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_37)
        | (_cmp_cached_30)
        | (_cmp_cached_68)
      )
      # 15m & 1h & 1d down move, 15m & 1h still not low enough, 4h high, 1d downtrend, 4h overbought
      & (
        (_cmp_cached_8)
        | (_cmp_cached_27)
        | (_cmp("RSI_3_1d", ">", 25.0))
        | (_cmp_cached_15)
        | (_cmp_cached_5)
        | (_cmp_cached_36)
        | (_cmp_cached_56)
        | (_cmp("ROC_9_1h", ">", -10.0))
        | (_cmp("ROC_9_4h", "<", 30.0))
      )
      # 15m & 1h down move, 15m still not low enough, 1h still high, 4h high, 1h & 4h downtrend
      & (
        (_cmp_cached_8)
        | (_cmp_cached_27)
        | (_cmp_cached_15)
        | (_cmp_cached_6)
        | (_cmp_cached_29)
        | (_cmp_cached_64)
        | (_cmp_cached_62)
      )
      # 15m & 1h & 4h & 1d down move, 15m & 1h & 4h still not low enough, 15m still high 4h & 1d downtrend
      & (
        (_cmp_cached_8)
        | (_cmp_cached_14)
        | (_cmp_cached_33)
        | (_cmp("RSI_3_1d", ">", 30.0))
        | (_cmp("RSI_14_15m", "<", 25.0))
        | (_cmp("RSI_14_1h", "<", 25.0))
        | (_cmp("RSI_14_4h", "<", 25.0))
        | (_cmp_cached_17)
        | (_cmp("ROC_9_4h", ">", -15.0))
        | (_cmp("ROC_9_1d", ">", -15.0))
      )
      # 15m & 1h & 4h down move, 15m downtrend, 15m & 1h still not low enough, 1h & 4h downtrend
      & (
        (_cmp_cached_8)
        | (_cmp_cached_14)
        | (_cmp_cached_33)
        | (_cmp_cached_55)
        | (_cmp_cached_50)
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 20.0))
        | (_cmp("ROC_9_1h", ">", -10.0))
        | (_cmp("ROC_9_4h", ">", -15.0))
      )
      # 15m & 1h & 4h down move, 1h still high, 4h high, 4h & 1d overbought
      & (
        (_cmp_cached_8)
        | (_cmp_cached_14)
        | (_cmp_cached_25)
        | (_cmp("RSI_14_1h", "<", 35.0))
        | (_cmp_cached_2)
        | (_cmp_cached_34)
        | (_cmp_cached_72)
        | (_cmp_cached_58)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 15m & 4h still high, 4h & 1d overbought
      & (
        (_cmp_cached_8)
        | (_cmp_cached_14)
        | (_cmp_cached_25)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_17)
        | (_cmp_cached_37)
        | (_cmp_cached_72)
        | (_cmp("ROC_9_1d", "<", 30.0))
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 4h overbought
      & (
        (_cmp_cached_8)
        | (_cmp_cached_14)
        | (_cmp_cached_44)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp("RSI_14_4h", "<", 45.0))
        | (_cmp("ROC_9_4h", "<", 70.0))
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 4h overbought
      & (
        (_cmp_cached_8)
        | (_cmp_cached_14)
        | (_cmp_cached_44)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp("AROONU_14_15m", "<", 20.0))
        | (_cmp_cached_22)
        | (_cmp_cached_37)
        | (_cmp_cached_49)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h still high, 4h high, 4h high & overbought
      & (
        (_cmp_cached_8)
        | (_cmp_cached_14)
        | (_cmp_cached_44)
        | (_cmp_cached_0)
        | (_cmp_cached_6)
        | (_cmp_cached_29)
        | (_cmp_cached_83)
        | (_cmp_cached_56)
        | (_cmp("ROC_9_4h", "<", 15.0))
      )
      # 15m & 1h down move, 15m still not low enough, 1h still high, 4h high, 1d downtrend, 4h overbought
      & (
        (_cmp_cached_8)
        | (_cmp_cached_14)
        | (_cmp_cached_0)
        | (_cmp_cached_6)
        | (_cmp_cached_36)
        | (_cmp("CMF_20_1d", ">", -0.10))
        | (_cmp("AROONU_14_15m", "<", 20.0))
        | (_cmp("AROONU_14_1h", "<", 20.0))
        | (_cmp_cached_56)
        | (_cmp_cached_38)
      )
      # 15m & 1h down move, 15m still not low enough, 1h still high, 4h high
      & (
        (_cmp_cached_8)
        | (_cmp_cached_14)
        | (_cmp_cached_0)
        | (_cmp_cached_6)
        | (_cmp_cached_29)
        | (_cmp("AROONU_14_1h", "<", 60.0))
        | (_cmp_cached_16)
      )
      # 15m & 1h down move, 15m still high, 1h & dh high, 1d overbought
      & (
        (_cmp_cached_8)
        | (_cmp_cached_14)
        | (_cmp_cached_3)
        | (_cmp_cached_40)
        | (_cmp_cached_16)
        | (_cmp_cached_51)
      )
      # 15m & 1h & 4h & 1d down move, 15m & 1h & 4h still not low enough, 1d high, 4h downtrend
      & (
        (_cmp_cached_8)
        | (_cmp_cached_23)
        | (_cmp_cached_32)
        | (_cmp("RSI_3_1d", ">", 40.0))
        | (_cmp_cached_0)
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp("RSI_14_1d", "<", 40.0))
        | (_cmp("AROONU_14_1d", "<", 70.0))
        | (_cmp("ROC_9_4h", ">", -40.0))
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 4h high, 1d downtrend, 4h overbought
      & (
        (_cmp_cached_8)
        | (_cmp_cached_23)
        | (_cmp_cached_25)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_20)
        | (_cmp("ROC_9_1h", ">", -20.0))
        | (_cmp_cached_49)
      )
      # 15m & 1h & 4h down move, 15m & 1h still not low enough, 4h high & overbought, 1d overbought
      & (
        (_cmp_cached_8)
        | (_cmp_cached_23)
        | (_cmp_cached_42)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_20)
        | (_cmp_cached_38)
        | (_cmp_cached_51)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 1h & 4h high
      & (
        (_cmp_cached_8)
        | (_cmp_cached_23)
        | (_cmp_cached_18)
        | (_cmp_cached_0)
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp_cached_22)
        | (_cmp_cached_56)
        | (_cmp_cached_30)
        | (_cmp_cached_47)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 1h high, 1d downtrend
      & (
        (_cmp_cached_8)
        | (_cmp_cached_23)
        | (_cmp_cached_44)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp_cached_40)
        | (_cmp("ROC_9_1d", ">", -20.0))
      )
      # 15m & 1h down move, 15m still not low enough, 1h still high, 1h & 4h high, 1h & 4h overbought
      & (
        (_cmp_cached_8)
        | (_cmp_cached_23)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_29)
        | (_cmp_cached_31)
        | (_cmp_cached_16)
        | (_cmp("ROC_9_1h", "<", 20.0))
        | (_cmp_cached_77)
      )
      # 15m & 1h down move, 15m still not low enough, 1h & 4h still high, 1d downtrend, 1h & 4h high, 1d overbought
      & (
        (_cmp_cached_8)
        | (_cmp_cached_23)
        | (_cmp_cached_0)
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp("CMF_20_1d", ">", -0.1))
        | (_cmp("AROONU_14_1h", "<", 60.0))
        | (_cmp_cached_76)
        | (_cmp("ROC_9_1d", "<", 20.0))
      )
      # 15m & 1h down move, 15m & 1h still high, 4h high, 4h overbought
      & (
        (_cmp_cached_8)
        | (_cmp_cached_23)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_36)
        | (_cmp("AROONU_14_15m", "<", 40.0))
        | (_cmp_cached_75)
        | (_cmp_cached_56)
        | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 85.0))
        | (_cmp_cached_49)
      )
      # 15m & 1h & 4h & 1d down move, 1h still high, 4h still not low enough, 4h downtrend
      & (
        (_cmp_cached_8)
        | (_cmp_cached_19)
        | (_cmp_cached_54)
        | (_cmp("RSI_3_1d", ">", 30.0))
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp_cached_30)
        | (_cmp("CCI_20_1h", "<", -250.0))
        | (_cmp("CCI_20_4h", "<", -250.0))
        | (_cmp("ROC_9_4h", ">", -15.0))
      )
      # 15m & 1h & 4h & 1d down move, 15m & 1h & 4h downtrend, 1h & 4h still not low enough, 1d downtrend
      & (
        (_cmp_cached_8)
        | (_cmp_cached_19)
        | (_cmp_cached_52)
        | (_cmp("RSI_3_1d", ">", 30.0))
        | (_cmp("RSI_14_1h", "<", 35.0))
        | (_cmp("RSI_14_4h", "<", 35.0))
        | (_cmp_cached_74)
        | (_cmp("CMF_20_1h", ">", -0.30))
        | (_cmp("CMF_20_4h", ">", -0.30))
        | (_cmp("CCI_20_1h", "<", -200.0))
        | (_cmp("CCI_20_4h", "<", -200.0))
        | (_cmp("ROC_9_1d", ">", -25.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 1h overbought, 4h downtrend
      & (
        (_cmp_cached_8)
        | (_cmp_cached_19)
        | (_cmp_cached_32)
        | (_cmp_cached_0)
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 30.0))
        | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 30.0))
        | (_cmp_cached_67)
        | (_cmp("ROC_9_4h", ">", -10.0))
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 15m & 1h still high, 4h high
      & (
        (_cmp_cached_8)
        | (_cmp_cached_19)
        | (_cmp_cached_32)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp_cached_17)
        | (_cmp_cached_22)
        | (_cmp_cached_81)
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 30.0))
        | (_cmp_cached_66)
      )
      # 15m & 1h & 4h down move, 4h downtrend, 1h high, 4h downtrend
      & (
        (_cmp_cached_8)
        | (_cmp_cached_19)
        | (_cmp_cached_32)
        | (_cmp_cached_62)
        | (_cmp_cached_80)
        | (_cmp_cached_78)
      )
      # 15m & 1h & 4h down move, 15m & 1h still not low enough, 4h & 1d still high, 1h downtrend, 1d downtrend
      & (
        (_cmp_cached_8)
        | (_cmp_cached_19)
        | (_cmp_cached_25)
        | (_cmp_cached_15)
        | (_cmp_cached_5)
        | (_cmp_cached_4)
        | (_cmp("RSI_14_1d", "<", 40.0))
        | (_cmp("CMF_20_1h", ">", -0.15))
        | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 10.0))
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 20.0))
        | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 40.0))
        | (_cmp("ROC_9_1d", ">", -25.0))
      )
      # 15m down move, 15m still not low enough, 1h & 4h still high, 15m still high, 1h high
      & (
        (_cmp_cached_8)
        | (_cmp_cached_0)
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp_cached_17)
        | (_cmp_cached_69)
        | (_cmp_cached_81)
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 80.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 1h downtrend, 15m & 4h still not low, 1h high
      & (
        (_cmp_cached_7)
        | (_cmp_cached_21)
        | (_cmp_cached_25)
        | (_cmp_cached_0)
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp("CMF_20_1h", ">", -0.25))
        | (_cmp_cached_63)
        | (_cmp("AROONU_14_4h", "<", 30.0))
        | (_cmp_cached_80)
      )
      # 15m ^ 1h down move, 15m & 1h & 4h still not low enough, 1h & 4h high, 1h overbought
      & (
        (_cmp_cached_8)
        | (_cmp_cached_21)
        | (_cmp_cached_0)
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp_cached_80)
        | (_cmp_cached_66)
        | (_cmp_cached_67)
      )
      # 15m & 1h down move, 15m still not low enough, 1h still high, 4h high, 15m still high, 4h overbought
      & (
        (_cmp_cached_8)
        | (_cmp_cached_21)
        | (_cmp_cached_0)
        | (_cmp_cached_6)
        | (_cmp_cached_29)
        | (_cmp_cached_17)
        | (_cmp_cached_56)
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 30.0))
        | (_cmp_cached_70)
        | (_cmp_cached_38)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 15m still high, 1h & 4h high
      & (
        (_cmp_cached_8)
        | (_cmp_cached_46)
        | (_cmp_cached_18)
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp_cached_17)
        | (_cmp_cached_69)
        | (_cmp_cached_59)
        | (_cmp_cached_66)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h high, 4h overbought
      & (
        (_cmp_cached_8)
        | (_cmp_cached_41)
        | (_cmp_cached_44)
        | (_cmp_cached_0)
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp("AROONU_14_1h", "<", 60.0))
        | (_cmp("AROONU_14_4h", "<", 60.0))
        | (_cmp_cached_80)
        | (_cmp_cached_70)
        | (_cmp_cached_49)
      )
      # 15m & 1h & 1d down move, 15m still not low enough, 1h & 4h high, 1d overbought
      & (
        (_cmp_cached_8)
        | (_cmp_cached_41)
        | (_cmp("RSI_3_1d", ">", 55.0))
        | (_cmp_cached_0)
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp_cached_31)
        | (_cmp_cached_16)
        | (_cmp_cached_51)
      )
      # 14m & 1h down move, 15m & 1h still high, 4h high & overbought
      & (
        (_cmp_cached_8)
        | (_cmp_cached_41)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp("RSI_14_4h", "<", 65.0))
        | (_cmp("AROONU_14_15m", "<", 40.0))
        | (_cmp_cached_75)
        | (_cmp_cached_56)
        | (_cmp("ROC_9_4h", "<", 35.0))
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 5h still high, 15m still high, 4h & 1d overbought
      & (
        (_cmp_cached_8)
        | (_cmp_cached_60)
        | (_cmp_cached_18)
        | (_cmp_cached_0)
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp_cached_17)
        | (_cmp_cached_28)
        | (_cmp_cached_38)
        | (_cmp_cached_58)
      )
      # 15m & 1h & 1d down move, 15m still not low enough, 1h & 4h still high, 1d overbought
      & (
        (_cmp_cached_8)
        | (_cmp_cached_60)
        | (_cmp("RSI_3_1d", ">", 60.0))
        | (_cmp_cached_0)
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp_cached_40)
        | (_cmp_cached_68)
      )
      # 15m & 1h down move, 15m & 1h stil high, 4h high, 15m & 4h high, 4h overbought
      & (
        (_cmp_cached_8)
        | (_cmp_cached_60)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_29)
        | (_cmp_cached_61)
        | (_cmp_cached_34)
        | (_cmp("ROC_9_4h", "<", 100.0))
      )
      # 15m & 1h down move, 15m & 1h & 4h still high, 15m downtrend, 1h & 4h high, 4h overbought
      & (
        (_cmp_cached_8)
        | (_cmp_cached_60)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp_cached_73)
        | (_cmp_cached_31)
        | (_cmp_cached_16)
        | (_cmp_cached_72)
      )
      # 15m & 1h down move, 15m & 1h & 4h still high, 1h & 4h high, 1h overbought
      & (
        (_cmp_cached_8)
        | (_cmp("RSI_3_1h", ">", 65.0))
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp_cached_11)
        | (_cmp("AROONU_14_1h", "<", 90.0))
        | (_cmp_cached_16)
        | (_cmp("ROC_9_1h", "<", 15.0))
      )
      # 15m & 4h down move, 15m high, 4h downtrend
      & (
        (_cmp_cached_8)
        | (_cmp("RSI_3_4h", ">", 3.0))
        | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 70.0))
        | (_cmp("ROC_9_4h", ">", -15.0))
      )
      # 15m & 4h down move, 15m & 1h & 4h still not low enough, 15m & 4h downtrend, 1h & 4h downtrend
      & (
        (_cmp_cached_8)
        | (_cmp("RSI_3_4h", ">", 5.0))
        | (_cmp("RSI_14_15m", "<", 10.0))
        | (_cmp("RSI_14_1h", "<", 10.0))
        | (_cmp("RSI_14_4h", "<", 10.0))
        | (_cmp("CMF_20_15m", ">", -0.10))
        | (_cmp_cached_71)
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 30.0))
        | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 20.0))
        | (_cmp("ROC_9_1h", ">", -15.0))
        | (_cmp("ROC_9_4h", ">", -15.0))
      )
      # 15m & 4h & 1d down move, 15m & 1h & 4h still not low enough, 15m & 1d downtrend
      & (
        (_cmp_cached_8)
        | (_cmp("RSI_3_4h", ">", 15.0))
        | (_cmp("RSI_3_1d", ">", 25.0))
        | (_cmp("RSI_14_15m", ">", 25.0))
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp("CMF_20_15m", ">", -0.3))
        | (_cmp("CMF_20_1d", ">", -0.3))
        | (_cmp_cached_63)
      )
      # 15m & 4h down move, 15m & 1h still high, 1h high, 1h over
      & (
        (_cmp_cached_8)
        | (_cmp("RSI_3_4h", ">", 15.0))
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_31)
        | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 40.0))
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 90.0))
        | (_cmp_cached_67)
      )
      # 15m & 4h down move, 15m still not low enough, 1h & 4h still high, 15m & 1h downtrend
      & (
        (_cmp_cached_8)
        | (_cmp("RSI_3_4h", ">", 20))
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp_cached_55)
        | (_cmp_cached_53)
        | (_cmp_cached_50)
        | (_cmp_cached_59)
      )
      # 15m & 4h down move, 15m & 1h & 4h still not low enough, 15m & 4h high, 4h downtrend
      & (
        (_cmp_cached_8)
        | (_cmp_cached_52)
        | (_cmp_cached_0)
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp_cached_11)
        | (_cmp_cached_20)
        | (_cmp("ROC_9_4h", ">", -20.0))
      )
      # 15m & 4h down move, 1h high & overbought
      & (
        (_cmp_cached_8)
        | (_cmp_cached_25)
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 90.0))
        | (_cmp_cached_67)
      )
      # 15m & 4h down move, 15m & 1h & 4h still high, 4h high, 1h & 4h overbought
      & (
        (_cmp_cached_8)
        | (_cmp_cached_18)
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_37)
        | (_cmp_cached_67)
        | (_cmp_cached_49)
      )
      # 15m & 4h down move, 15m & 1h & 4h still high, 15m & 4h high, 4h overbought
      & (
        (_cmp_cached_8)
        | (_cmp_cached_18)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp_cached_61)
        | (_cmp_cached_34)
        | (_cmp_cached_28)
        | (_cmp_cached_49)
      )
      # 15m & 1d down move, 15m still not low enough, 1h & 4h high
      & (
        (_cmp_cached_8)
        | (_cmp("RSI_3_1d", ">", 5.0))
        | (_cmp_cached_0)
        | (_cmp_cached_80)
        | (_cmp_cached_70)
      )
      # 15m & 1d down move, 15m still not low enough, 1h & 4h high
      & (
        (_cmp_cached_8)
        | (_cmp("RSI_3_1d", ">", 60.0))
        | (_cmp_cached_0)
        | (_cmp("RSI_14_1h", "<", 60.0))
        | (_cmp_cached_36)
        | (_cmp_cached_63)
        | (_cmp("AROONU_14_1h", "<", 60.0))
        | (_cmp_cached_16)
        | (_cmp_cached_30)
        | (_cmp_cached_66)
      )
      # 15m down move, 15m & 1h & 4h still not low enough, 15m & 1h downtrend, 15m & 1h high
      & (
        (_cmp_cached_8)
        | (_cmp_cached_0)
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp_cached_55)
        | (_cmp_cached_53)
        | (_cmp_cached_11)
        | (_cmp_cached_79)
      )
      # 15m down move, 15m still not low enough, 1h & 4h high, 1d downtrend, 1h & 4h high
      & (
        (_cmp_cached_8)
        | (_cmp("RSI_14_15m", "<", 35.0))
        | (_cmp("RSI_14_1h", "<", 70.0))
        | (_cmp_cached_29)
        | (_cmp("CMF_20_1d", ">", -0.1))
        | (_cmp_cached_31)
        | (_cmp_cached_16)
      )
      # 15m down move, 15m still not low enough, 1h & 4h high, 1d overbought
      & (
        (_cmp_cached_8)
        | (_cmp_cached_63)
        | (_cmp_cached_69)
        | (_cmp_cached_16)
        | (_cmp("ROC_9_1d", "<", 250.0))
      )
      # 15m down move, 15m & 1h still high, 1h high, 1h overbought, 4h & 1d downtrend
      & (
        (_cmp_cached_8)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp("AROONU_14_15m", "<", 40.0))
        | (_cmp_cached_69)
        | (_cmp("ROC_9_1h", "<", 40.0))
        | (_cmp("ROC_9_4h", ">", -50.0))
        | (_cmp("ROC_9_1d", ">", -50.0))
      )
      # 15m down move, 15m still high, 1h & 4h high, 1h & 1d overbought
      & (
        (_cmp_cached_8)
        | (_cmp_cached_3)
        | (_cmp("RSI_14_1h", "<", 70.0))
        | (_cmp_cached_29)
        | (_cmp_cached_31)
        | (_cmp("ROC_9_1h", "<", 40.0))
        | (_cmp_cached_58)
      )
      # 15m down move, 15m still not low enough, 1h & 4h high, 4h & 1d overbought
      & (
        (_cmp_cached_8)
        | (_cmp_cached_0)
        | (_cmp("RSI_14_1h", "<", 60.0))
        | (_cmp_cached_29)
        | (_cmp_cached_63)
        | (_cmp_cached_69)
        | (_cmp_cached_38)
        | (_cmp_cached_51)
      )
      # 15m down move, 15m & 1h & 4h still high, 1h & 4h high, 1h & 4h overbought
      & (
        (_cmp_cached_8)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp_cached_31)
        | (_cmp_cached_16)
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 80.0))
        | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 90.0))
        | (_cmp("ROC_9_1h", "<", 20.0))
        | (_cmp_cached_38)
      )
      # 15m down move, 15m high, 1h & 4h overbought
      & ((_cmp_cached_8) | (_cmp("AROONU_14_15m", "<", 75.0)) | (_cmp("ROC_9_1h", "<", 50.0)) | (_cmp("ROC_9_4h", "<", 80.0)))
      # 15m & 1h & 4h down move, 1h still high, 15m still not low enough, 4h downtrend
      & (
        (_cmp_cached_7)
        | (_cmp_cached_48)
        | (_cmp("RSI_3_4h", ">", 5.0))
        | (_cmp_cached_22)
        | (_cmp_cached_50)
        | (_cmp_cached_78)
      )
      # 15m & 1h & 4h & 1d down move, 15m downtrend, 1h & 4h still not low enough
      & (
        (_cmp_cached_7)
        | (_cmp_cached_48)
        | (_cmp_cached_25)
        | (_cmp("RSI_3_1d", ">", 45.0))
        | (_cmp("CMF_20_15m", ">", -0.40))
        | (_cmp("AROONU_14_1h", "<", 20.0))
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 15.0))
        | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 15.0))
        | (_cmp("CCI_20_1h", "<", -350.0))
        | (_cmp("CCI_20_4h", "<", -200.0))
      )
      # 15m & 1h & 4h down move, 15m downtrend, 1h & 4h till high, 15m still high, 1d overbought
      & (
        (_cmp_cached_7)
        | (_cmp_cached_24)
        | (_cmp_cached_54)
        | (_cmp("CMF_20_15m", ">", -0.3))
        | (_cmp_cached_22)
        | (_cmp_cached_37)
        | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 40.0))
        | (_cmp_cached_58)
      )
      # 15m & 1h & 4h & 1d down move, 4h & 1d still not low enough, 1d downtrend, 1h & 4h still high, 1d downtrend
      & (
        (_cmp_cached_7)
        | (_cmp_cached_24)
        | (_cmp_cached_54)
        | (_cmp("RSI_3_1d", ">", 25.0))
        | (_cmp_cached_12)
        | (_cmp("RSI_14_1d", "<", 30.0))
        | (_cmp("CMF_20_1d", ">", -0.20))
        | (_cmp_cached_75)
        | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 40.0))
        | (_cmp("ROC_9_1d", ">", -15.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 1h & 4h downtrend, 1h high
      & (
        (_cmp_cached_7)
        | (_cmp_cached_24)
        | (_cmp_cached_33)
        | (_cmp_cached_15)
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp_cached_64)
        | (_cmp_cached_62)
        | (_cmp_cached_40)
        | (_cmp("CCI_20_1h", "<", -200.0))
        | (_cmp("CCI_20_4h", "<", -200.0))
      )
      # 15m & 1h & 4h down move, 1h still not low enough, 1d overbought
      & (
        (_cmp_cached_7)
        | (_cmp_cached_24)
        | (_cmp_cached_33)
        | (_cmp("AROONU_14_1h", "<", 25.0))
        | (_cmp("ROC_9_1d", "<", 200.0))
      )
      # 15m & 1h & 4h & 1d down move, 1h & 4h still not low enough, 1d still high, 1d downtrend, 1d overbought
      & (
        (_cmp_cached_7)
        | (_cmp_cached_24)
        | (_cmp_cached_52)
        | (_cmp("RSI_3_1d", ">", 45.0))
        | (_cmp_cached_12)
        | (_cmp("RSI_14_1d", "<", 50.0))
        | (_cmp("CMF_20_1d", ">", -0.0))
        | (_cmp("MFI_14_1d", "<", 70.0))
        | (_cmp("CCI_20_1h", "<", -250.0))
        | (_cmp("CCI_20_4h", "<", -200.0))
        | (_cmp("ROC_9_4h", ">", -10.0))
        | (_cmp("ROC_9_1d", "<", 15.0))
      )
      # 15m & 1h & 4h & 1d down move, 1h & 4h still not low enough, 15m & 1h downtrend, 1h & 4h still not low enough
      & (
        (_cmp_cached_7)
        | (_cmp_cached_24)
        | (_cmp_cached_39)
        | (_cmp("RSI_3_1d", ">", 50.0))
        | (_cmp_cached_43)
        | (_cmp_cached_12)
        | (_cmp("CMF_20_15m", ">", -0.40))
        | (_cmp("CMF_20_1h", ">", -0.25))
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 20.0))
        | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 20.0))
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 1h still high, 4h high & overbought
      & (
        (_cmp_cached_7)
        | (_cmp_cached_24)
        | (_cmp_cached_42)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_22)
        | (_cmp_cached_16)
        | (_cmp_cached_49)
      )
      # 15m & 1h down move, 15m & 1h still not low enough, 4h still high, 15m still not low enough, 1h & 4h high
      & (
        (_cmp_cached_7)
        | (_cmp_cached_24)
        | (_cmp_cached_0)
        | (_cmp_cached_5)
        | (_cmp_cached_2)
        | (_cmp_cached_63)
        | (_cmp_cached_69)
        | (_cmp_cached_16)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 15m & 1h & 4h downtrend, 1d overbought
      & (
        (_cmp_cached_7)
        | (_cmp_cached_27)
        | (_cmp_cached_35)
        | (_cmp_cached_0)
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp("CMF_20_15m", ">", -0.10))
        | (_cmp_cached_64)
        | (_cmp_cached_62)
        | (_cmp_cached_51)
      )
      # 15m & 1h & 4h down move, 1h still not low enough, 4h still high, 1h high, 1h & 4h downtrend, 1d overbought
      & (
        (_cmp_cached_7)
        | (_cmp_cached_27)
        | (_cmp_cached_35)
        | (_cmp_cached_5)
        | (_cmp_cached_4)
        | (_cmp_cached_40)
        | (_cmp("ROC_9_1h", ">", -10.0))
        | (_cmp("ROC_9_4h", ">", -10.0))
        | (_cmp_cached_68)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 15m & 1h downtrend
      & (
        (_cmp_cached_7)
        | (_cmp_cached_27)
        | (_cmp_cached_18)
        | (_cmp_cached_15)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp("CMF_20_15m", ">", -0.10))
        | (_cmp("CMF_20_1h", ">", -0.15))
        | (_cmp("AROONU_14_15m", "<", 20.0))
        | (_cmp_cached_83)
        | (_cmp_cached_37)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 15m & 1h & 4h downtrend, 4h high
      & (
        (_cmp_cached_7)
        | (_cmp_cached_27)
        | (_cmp_cached_44)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp("CMF_20_15m", ">", -0.15))
        | (_cmp("CMF_20_1h", ">", -0.15))
        | (_cmp("CMF_20_4h", ">", -0.15))
        | (_cmp_cached_66)
      )
      # 15m & 1h down move, 15m still not low enough, 1h & 4h still high, 15m & 4h high
      & (
        (_cmp_cached_7)
        | (_cmp_cached_27)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp("AROONU_14_15m", "<", 75.0))
        | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 90.0))
      )
      # 15m & 1h down move, 1h still not low enough, 1h still high, 4h high & overbought, 1d downtrend
      & (
        (_cmp_cached_7)
        | (_cmp_cached_27)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_20)
        | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 90.0))
        | (_cmp_cached_77)
        | (_cmp("ROC_9_1d", ">", -50.0))
      )
      # 15m & 1h down move, 15m still not low enough, 1h & 4h still high, 1d overbought
      & (
        (_cmp_cached_7)
        | (_cmp_cached_27)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_30)
        | (_cmp("ROC_9_1d", "<", 150.0))
      )
      # 15m & 1h & 1d down move, 1h & 4h still high, 15m downtrend, 1d overbought
      & (
        (_cmp_cached_7)
        | (_cmp_cached_27)
        | (_cmp("RSI_3_1d", ">", 55.0))
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp("CMF_20_15m", ">", -0.3))
        | (_cmp_cached_68)
      )
      # 15m & 1h & 4h & 1d down move, 15m & 1h still high, 4h downtrend
      & (
        (_cmp_cached_7)
        | (_cmp_cached_14)
        | (_cmp_cached_33)
        | (_cmp("RSI_3_1d", ">", 30.0))
        | (_cmp_cached_28)
        | (_cmp_cached_30)
        | (_cmp("ROC_9_4h", ">", -70.0))
      )
      # 15m & 1h & 4h & 1d down move, 15m & 1h & 4h still not low enough, 4h still high, 1h & 4h downtrend, 1d overbought
      & (
        (_cmp_cached_7)
        | (_cmp_cached_14)
        | (_cmp_cached_33)
        | (_cmp("RSI_3_1d", ">", 40.0))
        | (_cmp_cached_15)
        | (_cmp_cached_43)
        | (_cmp("RSI_14_4h", "<", 20.0))
        | (_cmp("AROONU_14_4h", "<", 40.0))
        | (_cmp("ROC_9_1h", ">", -15.0))
        | (_cmp_cached_78)
        | (_cmp("ROC_9_1d", "<", 40.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 15m stil high, 4h high
      & (
        (_cmp_cached_7)
        | (_cmp_cached_14)
        | (_cmp_cached_33)
        | (_cmp_cached_15)
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_34)
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 20.0))
        | (_cmp_cached_47)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 4h downtrend, 1h high, 4h downtrend
      & (
        (_cmp_cached_7)
        | (_cmp_cached_14)
        | (_cmp_cached_33)
        | (_cmp_cached_15)
        | (_cmp_cached_43)
        | (_cmp("RSI_14_4h", "<", 20.0))
        | (_cmp("CMF_20_4h", ">", -0.25))
        | (_cmp_cached_80)
        | (_cmp("ROC_9_4h", ">", -40.0))
      )
      # 15m & 1h & 4h down move, 1h & 4h still high, 15m & 1h downtrend, 1h & 4h high, 4h & 1d overbought
      & (
        (_cmp_cached_7)
        | (_cmp_cached_14)
        | (_cmp_cached_32)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_55)
        | (_cmp_cached_53)
        | (_cmp_cached_22)
        | (_cmp("AROONU_14_4h", "<", 60.0))
        | (_cmp_cached_38)
        | (_cmp("ROC_9_1d", "<", 25.0))
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 4h overbought
      & (
        (_cmp_cached_7)
        | (_cmp_cached_14)
        | (_cmp_cached_25)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_37)
        | (_cmp_cached_77)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h still high, 4h high, 4h & 1d overbought
      & (
        (_cmp_cached_7)
        | (_cmp_cached_14)
        | (_cmp_cached_18)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_56)
        | (_cmp_cached_38)
        | (_cmp_cached_51)
      )
      # 15m & 1h down move, 15m still not low enough, 1h & 4h still high, 15m & 1h high
      & (
        (_cmp_cached_7)
        | (_cmp_cached_14)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_36)
        | (_cmp_cached_11)
        | (_cmp_cached_79)
      )
      # 15m & 1h down move, 15m still not low enough, 1h still high, 4h high, 4h & 1d overbought
      & (
        (_cmp_cached_7)
        | (_cmp_cached_14)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_29)
        | (_cmp_cached_83)
        | (_cmp_cached_37)
        | (_cmp_cached_38)
        | (_cmp("ROC_9_1d", "<", 200.0))
      )
      # 15m & 1h down move, 15m still not low enough, 1h still high, 4h high, 4h overbought
      & (
        (_cmp_cached_7)
        | (_cmp_cached_14)
        | (_cmp_cached_0)
        | (_cmp_cached_6)
        | (_cmp_cached_29)
        | (_cmp_cached_34)
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 20.0))
        | (_cmp_cached_47)
        | (_cmp_cached_77)
      )
      # 15m & 1h down move, 1h still high, 1h & 4h high, 4h & 1d overbought
      & (
        (_cmp_cached_7)
        | (_cmp_cached_14)
        | (_cmp_cached_1)
        | (_cmp_cached_29)
        | (_cmp_cached_31)
        | (_cmp_cached_16)
        | (_cmp_cached_38)
        | (_cmp_cached_68)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 15m & 4h still not low enough, 4h downtrend
      & (
        (_cmp_cached_7)
        | (_cmp_cached_23)
        | (_cmp_cached_52)
        | (_cmp_cached_0)
        | (_cmp_cached_5)
        | (_cmp_cached_4)
        | (_cmp_cached_63)
        | (_cmp("AROONU_14_4h", "<", 30.0))
        | (_cmp("ROC_9_4h", ">", -50.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h downtrend, 4h still high, 15m still not low enough, 1h still high
      & (
        (_cmp_cached_7)
        | (_cmp_cached_23)
        | (_cmp_cached_32)
        | (_cmp("CMF_20_15m", ">", -0.10))
        | (_cmp_cached_53)
        | (_cmp_cached_71)
        | (_cmp("AROONU_14_4h", "<", 40.0))
        | (_cmp_cached_50)
        | (_cmp_cached_59)
        | (_cmp_cached_78)
      )
      # 15m & 1h & 4h & 1d down move, 1d still high, 1h still high, 4h high
      & (
        (_cmp_cached_7)
        | (_cmp_cached_23)
        | (_cmp_cached_25)
        | (_cmp("RSI_3_1d", ">", 25.0))
        | (_cmp("MFI_14_1d", "<", 50.0))
        | (_cmp_cached_22)
        | (_cmp_cached_56)
      )
      # 15m & 1h & 4h & 1d down move, 15m still not low enough, 1h & 4h still high, 15m downtrend, 4h high
      & (
        (_cmp_cached_7)
        | (_cmp_cached_23)
        | (_cmp_cached_42)
        | (_cmp("RSI_3_1d", ">", 55.0))
        | (_cmp("RSI_14_15m", "<", 25.0))
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp("CMF_20_15m", ">", -0.10))
        | (_cmp_cached_20)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 4h high & overbought
      & (
        (_cmp_cached_7)
        | (_cmp_cached_23)
        | (_cmp_cached_42)
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_20)
        | (_cmp_cached_38)
      )
      # 15m & 1h down move, 15m & 1h & 4h still not low enough, 15m still high, 1h high, 1h & 4h still high, 1d downtrend
      & (
        (_cmp_cached_7)
        | (_cmp_cached_23)
        | (_cmp_cached_0)
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp("AROONU_14_1h", "<", 90.0))
        | (_cmp_cached_30)
        | (_cmp_cached_47)
        | (_cmp("ROC_9_1d", ">", -50.0))
      )
      # 15m & 1h down move, 15m still not low enough, 1h & 4h still high, 15m still not lowenough, 1h high, 1d overbought
      & (
        (_cmp_cached_7)
        | (_cmp_cached_23)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp("AROONU_14_15m", "<", 25.0))
        | (_cmp_cached_31)
        | (_cmp_cached_68)
      )
      # 15m & 1h down move, 15m & 1h & 4h still high, 15m & 1h high, 4h overbought
      & (
        (_cmp_cached_7)
        | (_cmp_cached_23)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp_cached_11)
        | (_cmp_cached_79)
        | (_cmp_cached_49)
      )
      # 15m & 1h down move, 15m & 1h sitll high, 4h high, 1h & 4h high, 1h & 4h overbought
      & (
        (_cmp_cached_7)
        | (_cmp_cached_23)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_29)
        | (_cmp_cached_31)
        | (_cmp_cached_76)
        | (_cmp("ROC_9_1h", "<", 20.0))
        | (_cmp("ROC_9_4h", "<", 30.0))
      )
      # 15m & 4h down move, 15m & 1h & 4h still high, 4h downtrend, 15m & 1h still high, 4h downtrend
      & (
        (_cmp_cached_7)
        | (_cmp_cached_52)
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp("CMF_20_4h", ">", -0.25))
        | (_cmp_cached_17)
        | (_cmp_cached_50)
        | (_cmp_cached_30)
        | (_cmp("ROC_9_4h", ">", -20.0))
      )
      # 15m & 1h & 4h down move, 15m downtrend, 15m still high, 1h overbought
      & (
        (_cmp_cached_7)
        | (_cmp_cached_19)
        | (_cmp_cached_32)
        | (_cmp_cached_55)
        | (_cmp_cached_17)
        | (_cmp_cached_58)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 4h downtrend
      & (
        (_cmp_cached_7)
        | (_cmp_cached_19)
        | (_cmp_cached_32)
        | (_cmp_cached_17)
        | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 40.0))
        | (_cmp_cached_59)
        | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 40.0))
        | (_cmp("ROC_9_4h", ">", -20.0))
      )
      # 15m & 1h & 4h down move, 4d downtrend, 1h high, 4h downtrend
      & (
        (_cmp_cached_7)
        | (_cmp_cached_19)
        | (_cmp_cached_32)
        | (_cmp("CMF_20_4h", ">", -0.40))
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 80.0))
        | (_cmp_cached_78)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 4h downtrend, 15m high, 4h & 1d downtrend
      & (
        (_cmp_cached_7)
        | (_cmp_cached_19)
        | (_cmp_cached_39)
        | (_cmp_cached_0)
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp("CMF_20_4h", ">", -0.40))
        | (_cmp_cached_11)
        | (_cmp("ROC_9_4h", ">", -20.0))
        | (_cmp("ROC_9_1d", ">", -50.0))
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h still high, 4h high & overbought
      & (
        (_cmp_cached_7)
        | (_cmp_cached_19)
        | (_cmp_cached_18)
        | (_cmp_cached_0)
        | (_cmp_cached_63)
        | (_cmp_cached_22)
        | (_cmp_cached_56)
        | (_cmp("ROC_9_4h", "<", 30.0))
      )
      # 15m & 1h & 4h down move, 1h & 4h still high, 4h overbought
      & (
        (_cmp_cached_7)
        | (_cmp_cached_19)
        | (_cmp_cached_44)
        | (_cmp_cached_0)
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp_cached_22)
        | (_cmp_cached_37)
        | (_cmp("CCI_20_1h", "<", 0.0))
        | (_cmp("CCI_20_4h", "<", 0.0))
        | (_cmp_cached_77)
      )
      # 15m & 1h & 4h down move, 15m & 1h still high, 4h high, 15m stil high, 4h high & overbought
      & (
        (_cmp_cached_7)
        | (_cmp_cached_19)
        | (_cmp_cached_44)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_36)
        | (_cmp_cached_17)
        | (_cmp_cached_20)
        | (_cmp_cached_72)
      )
      # 15m & 1h down move, 15m still not low enough, 1h & 4h still high, 15m downtrend, 1h & 4h high, 4h overbought
      & (
        (_cmp_cached_7)
        | (_cmp_cached_19)
        | (_cmp_cached_0)
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp_cached_55)
        | (_cmp_cached_40)
        | (_cmp_cached_16)
        | (_cmp_cached_77)
      )
      # 15m & 1h & 4h & 1d down move, 15m & 1h & 4h still not low enough, 15m still high, 1h high, 4h & 1d downtrend
      & (
        (_cmp_cached_7)
        | (_cmp_cached_21)
        | (_cmp_cached_25)
        | (_cmp("RSI_3_1d", ">", 45.0))
        | (_cmp_cached_15)
        | (_cmp_cached_43)
        | (_cmp("RSI_14_4h", "<", 20.0))
        | (_cmp("AROONU_14_15m", "<", 40.0))
        | (_cmp_cached_80)
        | (_cmp("ROC_9_4h", ">", -25.0))
        | (_cmp("ROC_9_1d", ">", -30.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 15m high, 1h still high, 4h overbought
      & (
        (_cmp_cached_7)
        | (_cmp_cached_21)
        | (_cmp_cached_42)
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_11)
        | (_cmp_cached_59)
        | (_cmp_cached_49)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 15m & 4h high, 4h overbought
      & (
        (_cmp_cached_7)
        | (_cmp_cached_21)
        | (_cmp_cached_44)
        | (_cmp_cached_0)
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp_cached_61)
        | (_cmp_cached_20)
        | (_cmp_cached_77)
      )
      # 15m & 1h & 1d down move, 15m still not low enough, 1h & 4h still high, 1h high, 4h downtrend, 1d overbought
      & (
        (_cmp_cached_7)
        | (_cmp_cached_21)
        | (_cmp("RSI_3_1d", ">", 45.0))
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp_cached_40)
        | (_cmp("ROC_9_4h", ">", -20.0))
        | (_cmp_cached_51)
      )
      # 15m & 1h & 4h down move, 15m still not low, 1h & 4h sitll high, 15m & 1h downtrend, 15m still high, 4h high
      & (
        (_cmp_cached_7)
        | (_cmp_cached_46)
        | (_cmp_cached_39)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp("CMF_20_15m", ">", -0.10))
        | (_cmp_cached_53)
        | (_cmp_cached_28)
        | (_cmp_cached_70)
      )
      # 15m & 1h down move, 15m & 1h still high, 4h high, 15m still high, 1h & 4h high
      & (
        (_cmp_cached_7)
        | (_cmp_cached_46)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_36)
        | (_cmp("AROONU_14_15m", "<", 40.0))
        | (_cmp_cached_69)
        | (_cmp_cached_16)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 1h & 1d overbought
      & (
        (_cmp_cached_7)
        | (_cmp_cached_41)
        | (_cmp_cached_42)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_67)
        | (_cmp("ROC_9_1d", "<", 200.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 1h high & overbought
      & (
        (_cmp_cached_7)
        | (_cmp_cached_41)
        | (_cmp_cached_42)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp("AROONU_14_15m", "<", 40.0))
        | (_cmp_cached_69)
        | (_cmp_cached_67)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h downtrend, 15m & 1h high
      & (
        (_cmp_cached_7)
        | (_cmp_cached_41)
        | (_cmp_cached_42)
        | (_cmp_cached_73)
        | (_cmp_cached_64)
        | (_cmp_cached_62)
        | (_cmp_cached_11)
        | (_cmp("AROONU_14_1h", "<", 90.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 15m still high, 4h downtrend
      & (
        (_cmp_cached_7)
        | (_cmp_cached_41)
        | (_cmp_cached_42)
        | (_cmp_cached_0)
        | (_cmp_cached_5)
        | (_cmp_cached_4)
        | (_cmp_cached_17)
        | (_cmp_cached_28)
        | (_cmp("ROC_9_4h", ">", -40.0))
      )
      # 15m & 1h & 4h down move, 1h & 4h high, 4h & 1d overbought
      & (
        (_cmp_cached_7)
        | (_cmp_cached_41)
        | (_cmp_cached_18)
        | (_cmp_cached_1)
        | (_cmp_cached_36)
        | (_cmp("AROONU_14_4h", "<", 75.0))
        | (_cmp_cached_72)
        | (_cmp("ROC_9_1d", "<", 150.0))
      )
      # 15m & 1h down move, 15m & 1h stil high, 4h high, 1h & 4h overbought
      & (
        (_cmp_cached_7)
        | (_cmp_cached_41)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_29)
        | (_cmp_cached_34)
        | (_cmp("ROC_9_1h", "<", 40.0))
        | (_cmp("ROC_9_4h", "<", 50.0))
      )
      # 15m & 1h down move, 15m still not low enough, 1h still high, 4h high, 15m & 1h & 4h high
      & (
        (_cmp_cached_7)
        | (_cmp_cached_41)
        | (_cmp_cached_0)
        | (_cmp_cached_6)
        | (_cmp_cached_29)
        | (_cmp_cached_61)
        | (_cmp_cached_79)
        | (_cmp_cached_16)
      )
      # 15m & 1h down move, 15m & 1h still high, 4h high, 15m & 4h high, 15m & 1h still not low enough, 4h overbought
      & (
        (_cmp_cached_7)
        | (_cmp_cached_60)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp("RSI_14_4h", "<", 65.0))
        | (_cmp_cached_11)
        | (_cmp_cached_20)
        | (_cmp_cached_81)
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 30.0))
        | (_cmp("ROC_9_4h", "<", 30.0))
      )
      # 15m & 1h down move, 15m & 1h still high, 4h high, 1h & 4h high, 1h overbought
      & (
        (_cmp_cached_7)
        | (_cmp_cached_60)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_36)
        | (_cmp_cached_31)
        | (_cmp_cached_20)
        | (_cmp("ROC_9_1h", "<", 15.0))
      )
      # 15m & 1h down move, 15m still high, 1h high & overbought
      & (
        (_cmp_cached_7)
        | (_cmp_cached_60)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_40)
        | (_cmp("ROC_9_1h", "<", 80.0))
      )
      # 15m & 1h down move, 15m still not low enough, 1h still high, 4h high & overbought
      & (
        (_cmp_cached_7)
        | (_cmp("RSI_3_1h", ">", 65.0))
        | (_cmp("RSI_14_15m", "<", 35.0))
        | (_cmp_cached_6)
        | (_cmp("RSI_14_4h", "<", 75.0))
        | (_cmp_cached_34)
        | (_cmp_cached_50)
        | (_cmp_cached_70)
        | (_cmp("ROC_9_4h", "<", 100.0))
      )
      # 15m & 1h down move, 15m still not low enough, 1h & 4h still high, 15m downtrend, 4h high & overbought
      & (
        (_cmp_cached_7)
        | (_cmp("RSI_3_1h", ">", 65.0))
        | (_cmp_cached_0)
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp_cached_55)
        | (_cmp_cached_17)
        | (_cmp_cached_22)
        | (_cmp_cached_76)
        | (_cmp_cached_38)
      )
      # 15m & 1h down move, 15m still not low enough, 1h & 4h high, 15m still high, 1h & 4h high, 1d overbought
      & (
        (_cmp_cached_7)
        | (_cmp("RSI_3_1h", ">", 65.0))
        | (_cmp_cached_0)
        | (_cmp("RSI_14_1h", "<", 60.0))
        | (_cmp_cached_29)
        | (_cmp_cached_17)
        | (_cmp_cached_40)
        | (_cmp_cached_16)
        | (_cmp_cached_51)
      )
      # 15m & 4h down move, 15m & 1h & 4h sitll high, 4h high, 4h & 1d overbought
      & (
        (_cmp_cached_7)
        | (_cmp_cached_25)
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_17)
        | (_cmp("AROONU_14_4h", "<", 60.0))
        | (_cmp("ROC_9_4h", "<", 15.0))
        | (_cmp("ROC_9_1d", "<", 60.0))
      )
      # 15m & 4h & 1d down move, 15m & 1h & 4h s till high, 15m & 4h high
      & (
        (_cmp_cached_7)
        | (_cmp_cached_39)
        | (_cmp("RSI_3_1d", ">", 50.0))
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp_cached_11)
        | (_cmp("AROONU_14_4h", "<", 60.0))
        | (_cmp_cached_28)
      )
      # 15m & 4h down move, 15m & 1h still not low enough, 15m still high, 1h high, 4h downtrend
      & (
        (_cmp_cached_7)
        | (_cmp_cached_54)
        | (_cmp_cached_0)
        | (_cmp_cached_5)
        | (_cmp("AROONU_14_15m", "<", 40.0))
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 80.0))
        | (_cmp("ROC_9_4h", ">", -25.0))
      )
      # 15m & 4h down move, 15m & 1h still high, 4h downtrend
      & (
        (_cmp_cached_7)
        | (_cmp_cached_54)
        | (_cmp_cached_17)
        | (_cmp_cached_30)
        | (_cmp_cached_78)
      )
      # 15m &4d down move, 15m & 1h high, 4h downtrend
      & (
        (_cmp_cached_7)
        | (_cmp_cached_54)
        | (_cmp_cached_11)
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 80.0))
        | (_cmp_cached_78)
      )
      # 15m & 4h down move, 4h still high, 4h downtrend, 1d overbought
      & (
        (_cmp_cached_7)
        | (_cmp_cached_54)
        | (_cmp_cached_37)
        | (_cmp_cached_78)
        | (_cmp_cached_58)
      )
      # 15m & 4h down move, 15m & 1h & 4h still high, 15m still not low enough, 4h still high, 4h overbought
      & (
        (_cmp_cached_7)
        | (_cmp_cached_32)
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_63)
        | (_cmp_cached_37)
        | (_cmp_cached_77)
      )
      # 15m & 4h down move, 15m still not low enough, 1h & 4h still high, 15, & 4h still high, 1h high, 4h downtrend
      & (
        (_cmp_cached_7)
        | (_cmp_cached_32)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp_cached_17)
        | (_cmp_cached_37)
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 80.0))
        | (_cmp("ROC_9_4h", ">", -20.0))
      )
      # 15m & 4h down move, 15m & 1h & 4h still high, 15m still high, 1h high, 4h overbought
      & (
        (_cmp_cached_7)
        | (_cmp_cached_42)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp_cached_17)
        | (_cmp_cached_79)
        | (_cmp("ROC_9_4h", "<", 70.0))
      )
      # 15m & 4h down move, 15m & 1h still not low enough, 1h still high & overbought
      & (
        (_cmp_cached_7)
        | (_cmp_cached_18)
        | (_cmp("RSI_14_15m", "<", 35.0))
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_11)
        | (_cmp_cached_34)
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 30.0))
        | (_cmp_cached_47)
        | (_cmp_cached_49)
      )
      # 15m & 4h down move, 15m still high, 1h still high, 4h high & overbought
      & (
        (_cmp_cached_7)
        | (_cmp_cached_44)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_36)
        | (_cmp_cached_63)
        | (_cmp("AROONU_14_4h", "<", 60.0))
        | (_cmp("ROC_9_4h", "<", 100.0))
      )
      # 15m & 4h down move, 15m still not low enough, 1h & 4h high, 15m & 1h & 4h high
      & (
        (_cmp_cached_7)
        | (_cmp_cached_44)
        | (_cmp_cached_0)
        | (_cmp("RSI_14_1h", "<", 60.0))
        | (_cmp_cached_36)
        | (_cmp_cached_11)
        | (_cmp("AROONU_14_1h", "<", 90.0))
        | (_cmp_cached_76)
      )
      # 15m down move, 15m still not low enough, 1h & 4h high, 1h & 4h overbought
      & (
        (_cmp_cached_7)
        | (_cmp_cached_0)
        | (_cmp("RSI_14_1h", "<", 70.0))
        | (_cmp_cached_29)
        | (_cmp_cached_69)
        | (_cmp_cached_56)
        | (_cmp("ROC_9_1h", "<", 50.0))
        | (_cmp("ROC_9_4h", "<", 50.0))
      )
      # 15m down move, 15m still high, 1h & 4h high, 4h overbought
      & (
        (_cmp_cached_7)
        | (_cmp_cached_3)
        | (_cmp("RSI_14_1h", "<", 60.0))
        | (_cmp_cached_84)
        | (_cmp_cached_20)
        | (_cmp_cached_59)
        | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 90.0))
        | (_cmp("ROC_9_4h", "<", 75.0))
      )
      # 15m down move, 15m & 1h & 4h high, 1h & 4h overbought
      & (
        (_cmp_cached_7)
        | (_cmp("RSI_14_15m", "<", 50.0))
        | (_cmp("RSI_14_1h", "<", 60.0))
        | (_cmp_cached_36)
        | (_cmp_cached_40)
        | (_cmp_cached_16)
        | (_cmp("ROC_9_1h", "<", 50.0))
        | (_cmp("ROC_9_4h", "<", 50.0))
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 4h overbought
      & (
        (_cmp_cached_10)
        | (_cmp_cached_27)
        | (_cmp_cached_52)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_37)
        | (_cmp("ROC_9_4h", "<", 70.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h still not low enough, 4h still high, 1h high, 1d overbought
      & (
        (_cmp_cached_10)
        | (_cmp_cached_27)
        | (_cmp_cached_25)
        | (_cmp_cached_0)
        | (_cmp_cached_5)
        | (_cmp_cached_4)
        | (_cmp("AROONU_14_1h", "<", 60.0))
        | (_cmp_cached_58)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 15m high, 1h & 4h still high
      & (
        (_cmp_cached_10)
        | (_cmp_cached_27)
        | (_cmp_cached_25)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp_cached_61)
        | (_cmp_cached_22)
        | (_cmp("AROONU_14_4h", "<", 40.0))
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 15m & 1h & 4h high
      & (
        (_cmp_cached_10)
        | (_cmp_cached_27)
        | (_cmp_cached_18)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_61)
        | (_cmp_cached_69)
        | (_cmp_cached_56)
      )
      # 15m & 1h & 4h & 1d down move, 15m & 1h still not low enough, 4h still high, 1d overbought
      & (
        (_cmp_cached_10)
        | (_cmp_cached_27)
        | (_cmp_cached_35)
        | (_cmp("RSI_3_1d", ">", 55.0))
        | (_cmp("RSI_14_15m", "<", 25.0))
        | (_cmp_cached_5)
        | (_cmp_cached_4)
        | (_cmp_cached_50)
        | (_cmp("ROC_9_1d", "<", 30.0))
      )
      # 15m & 1h & 1d down move, 1h & 4h still high, 1d downtrend, 1h high, 1h & 4h still high, 1d downtrend
      & (
        (_cmp_cached_10)
        | (_cmp_cached_27)
        | (_cmp("RSI_3_1d", ">", 25.0))
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp("CMF_20_1d", ">", -0.20))
        | (_cmp("AROONU_14_1h", "<", 60.0))
        | (_cmp_cached_59)
        | (_cmp_cached_47)
        | (_cmp("ROC_9_1d", ">", -15.0))
      )
      # 15m & 1h down move, 15m still not low enough, 1h stil high, 4h high & overbought
      & (
        (_cmp_cached_10)
        | (_cmp_cached_27)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_29)
        | (_cmp_cached_75)
        | (_cmp_cached_56)
        | (_cmp("ROC_9_4h", "<", 70.0))
      )
      # 15m & 1h down move, 15m still not low enough, 1h still high, 4h high, 4h overbought
      & (
        (_cmp_cached_10)
        | (_cmp_cached_27)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_84)
        | (_cmp_cached_22)
        | (_cmp_cached_16)
        | (_cmp("ROC_9_4h", "<", 30.0))
      )
      # 15m & 1h & 4h & 1d down move, 15m & 1h still not low enough, 4h stil high, 15m still high, 1d overbought
      & (
        (_cmp_cached_10)
        | (_cmp_cached_14)
        | (_cmp_cached_33)
        | (_cmp("RSI_3_1d", ">", 60.0))
        | (_cmp_cached_0)
        | (_cmp_cached_5)
        | (_cmp_cached_4)
        | (_cmp_cached_28)
        | (_cmp_cached_51)
      )
      # 15m & 1h & 4h & 1d down move, 15m & 1h & 4h downtrend, 4h downtrend
      & (
        (_cmp_cached_10)
        | (_cmp_cached_14)
        | (_cmp_cached_33)
        | (_cmp("RSI_3_1d", ">", 30.0))
        | (_cmp_cached_74)
        | (_cmp("CMF_20_1h", ">", -0.40))
        | (_cmp("CMF_20_4h", ">", -0.40))
        | (_cmp("ROC_9_4h", ">", -40.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 1h still high, 1d overbought
      & (
        (_cmp_cached_10)
        | (_cmp_cached_14)
        | (_cmp_cached_33)
        | (_cmp_cached_0)
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp_cached_30)
        | (_cmp_cached_58)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 1h still high
      & (
        (_cmp_cached_10)
        | (_cmp_cached_14)
        | (_cmp_cached_32)
        | (_cmp_cached_0)
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp_cached_73)
        | (_cmp_cached_22)
        | (_cmp_cached_30)
      )
      # 15m & 1h & 4h down move, 1h still not low enough, 4h still high, 15m downtrend, 15m still not low enough
      & (
        (_cmp_cached_10)
        | (_cmp_cached_14)
        | (_cmp_cached_32)
        | (_cmp_cached_5)
        | (_cmp_cached_4)
        | (_cmp_cached_74)
        | (_cmp("AROONU_14_15m", "<", 20.0))
        | (_cmp_cached_83)
        | (_cmp_cached_37)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h stil high, 4h high, 4h overbought
      & (
        (_cmp_cached_10)
        | (_cmp_cached_14)
        | (_cmp_cached_39)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp_cached_22)
        | (_cmp_cached_81)
        | (_cmp_cached_66)
        | (_cmp_cached_72)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 15m still not low, 4h high, 1h still high
      & (
        (_cmp_cached_10)
        | (_cmp_cached_14)
        | (_cmp_cached_44)
        | (_cmp_cached_15)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp("AROONU_14_15m", "<", 20.0))
        | (_cmp_cached_34)
        | (_cmp_cached_59)
      )
      # 15m & 1h down move, 15m still not low enough, 1h still high, 4h high & overbought
      & (
        (_cmp_cached_10)
        | (_cmp_cached_14)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_29)
        | (_cmp_cached_40)
        | (_cmp_cached_16)
        | (_cmp("ROC_9_4h", "<", 50.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 15m still high, 4h downtrend, 1d overbought
      & (
        (_cmp_cached_10)
        | (_cmp_cached_23)
        | (_cmp_cached_52)
        | (_cmp_cached_0)
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp("ROC_9_4h", ">", -20.0))
        | (_cmp_cached_58)
      )
      # 15m & 1h & 4h down move, 15m & 1h still not low enough, 4h still high, 1h still high, 15m still high
      & (
        (_cmp_cached_10)
        | (_cmp_cached_23)
        | (_cmp_cached_52)
        | (_cmp_cached_0)
        | (_cmp_cached_5)
        | (_cmp_cached_4)
        | (_cmp_cached_22)
        | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 40.0))
      )
      # 15m & 1h & 4h down move, 1h still not low enough, 4h still high, 4h & 1d overbought
      & (
        (_cmp_cached_10)
        | (_cmp_cached_23)
        | (_cmp_cached_52)
        | (_cmp_cached_5)
        | (_cmp_cached_2)
        | (_cmp_cached_37)
        | (_cmp_cached_49)
        | (_cmp_cached_58)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h still high, 4h high & overbought
      & (
        (_cmp_cached_10)
        | (_cmp_cached_23)
        | (_cmp_cached_32)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_34)
        | (_cmp("ROC_9_4h", "<", 80.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 15m & 1h & 4h still high, 1d downtrend
      & (
        (_cmp_cached_10)
        | (_cmp_cached_23)
        | (_cmp_cached_32)
        | (_cmp_cached_0)
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp("AROONU_14_15m", "<", 40.0))
        | (_cmp_cached_22)
        | (_cmp_cached_30)
        | (_cmp_cached_47)
        | (_cmp("ROC_9_1d", ">", -40.0))
      )
      # 15m & 1h & 1d down move, 15m still not low enough, 1h & 4h still high, 1d downtrend, 1h high, 1d overbought
      & (
        (_cmp_cached_10)
        | (_cmp_cached_23)
        | (_cmp("RSI_3_1d", ">", 65.0))
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp("CMF_20_1d", ">", -0.20))
        | (_cmp_cached_17)
        | (_cmp_cached_69)
        | (_cmp("ROC_9_1d", "<", 20.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 4h & 1d overbought
      & (
        (_cmp_cached_10)
        | (_cmp_cached_23)
        | (_cmp_cached_44)
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_36)
        | (_cmp_cached_11)
        | (_cmp("AROONU_14_4h", "<", 60.0))
        | (_cmp_cached_38)
        | (_cmp("ROC_9_1d", "<", 20.0))
      )
      # 15m & 1h & 1d down move, 4h & 1d downtrend, 1h & 4h high, 1d downtrend
      & (
        (_cmp_cached_10)
        | (_cmp_cached_23)
        | (_cmp("RSI_3_1d", ">", 35.0))
        | (_cmp("CMF_20_4h", ">", -0.1))
        | (_cmp("CMF_20_1d", ">", -0.1))
        | (_cmp("AROONU_14_1h", "<", 75.0))
        | (_cmp_cached_70)
        | (_cmp("ROC_2_1d", ">", -20.0))
      )
      # 15m & 1h down move, 15m still not low enough, 1h & 4h still high, 15m & 1h & 4h downtrend, 4h high
      & (
        (_cmp_cached_10)
        | (_cmp_cached_23)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_73)
        | (_cmp_cached_64)
        | (_cmp_cached_62)
        | (_cmp_cached_83)
        | (_cmp_cached_20)
      )
      # 15m & 1h down move, 15m still not low enough, 1h still high, 4h high, 4h & 1d overbought
      & (
        (_cmp_cached_10)
        | (_cmp_cached_23)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_29)
        | (_cmp_cached_20)
        | (_cmp("ROC_9_4h", "<", 80.0))
        | (_cmp_cached_58)
      )
      # 15m & 1h down move, 15m still not low enough, 1h & 4h high, 1h & 4h overbought
      & (
        (_cmp_cached_10)
        | (_cmp_cached_23)
        | (_cmp_cached_0)
        | (_cmp_cached_6)
        | (_cmp_cached_84)
        | (_cmp_cached_22)
        | (_cmp_cached_76)
        | (_cmp_cached_81)
        | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 90.0))
        | (_cmp("ROC_9_1h", "<", 20.0))
        | (_cmp("ROC_9_4h", "<", 60.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 1h & 4h downtrend
      & (
        (_cmp_cached_10)
        | (_cmp_cached_19)
        | (_cmp("RSI_3_4h", ">", 10.0))
        | (_cmp_cached_15)
        | (_cmp_cached_43)
        | (_cmp("RSI_14_4h", "<", 20.0))
        | (_cmp("CMF_20_1h", ">", -0.15))
        | (_cmp_cached_71)
        | (_cmp_cached_63)
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 30.0))
        | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 30.0))
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 4h high, 4h overbought
      & (
        (_cmp_cached_10)
        | (_cmp_cached_19)
        | (_cmp_cached_18)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_22)
        | (_cmp_cached_56)
        | (_cmp_cached_81)
        | (_cmp("ROC_9_4h", "<", 30.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 4h high & overbought
      & (
        (_cmp_cached_10)
        | (_cmp_cached_19)
        | (_cmp_cached_18)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp("AROONU_14_4h", "<", 60.0))
        | (_cmp_cached_72)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 4h high, 4h & 1d overbought
      & (
        (_cmp_cached_10)
        | (_cmp_cached_19)
        | (_cmp_cached_18)
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_34)
        | (_cmp("ROC_9_4h", "<", 15.0))
        | (_cmp_cached_51)
      )
      # 15m & 1h down move, 15m sitll not low enough, 1h still high, 4h high, 15m & 1h downtrend, 15m & 1h still high
      & (
        (_cmp_cached_10)
        | (_cmp_cached_19)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_36)
        | (_cmp_cached_55)
        | (_cmp_cached_53)
        | (_cmp_cached_17)
        | (_cmp_cached_30)
      )
      # 15m & 1h down move, 15m still not low enough, 1h & 4h still high, 15m & 1h high, 1d overbought
      & (
        (_cmp_cached_10)
        | (_cmp_cached_19)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_36)
        | (_cmp_cached_11)
        | (_cmp_cached_79)
        | (_cmp_cached_68)
      )
      # 15m & 1h & 4h down move, 15m & 1h still not low enough, 4h still high, 4h overbought
      & (
        (_cmp_cached_10)
        | (_cmp_cached_21)
        | (_cmp_cached_25)
        | (_cmp_cached_15)
        | (_cmp_cached_5)
        | (_cmp_cached_2)
        | (_cmp_cached_37)
        | (_cmp_cached_81)
        | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 30.0))
        | (_cmp_cached_49)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 1h & 4h downtrend, 15m high, 4h downtrend
      & (
        (_cmp_cached_10)
        | (_cmp_cached_21)
        | (_cmp_cached_25)
        | (_cmp_cached_0)
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp_cached_53)
        | (_cmp("CMF_20_4h", ">", -0.30))
        | (_cmp_cached_11)
        | (_cmp_cached_28)
        | (_cmp_cached_78)
      )
      # 15m & 1h & 4h, 15m still not low enough, 1h & 4h still high, 15m downtrend, 15m & 4h high
      & (
        (_cmp_cached_10)
        | (_cmp_cached_21)
        | (_cmp_cached_25)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp_cached_73)
        | (_cmp_cached_17)
        | (_cmp_cached_70)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h still high, 4h high & overbought
      & (
        (_cmp_cached_10)
        | (_cmp_cached_21)
        | (_cmp_cached_25)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_22)
        | (_cmp_cached_56)
        | (_cmp("ROC_9_4h", "<", 70.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 15m still high, 4h high & overbought
      & (
        (_cmp_cached_10)
        | (_cmp_cached_21)
        | (_cmp_cached_42)
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp("AROONU_14_15m", "<", 40.0))
        | (_cmp_cached_20)
        | (_cmp_cached_70)
        | (_cmp_cached_49)
      )
      # 15m & 1h & 1d down move, 15m & 1h & 4h still high, 15m & 1d downtrend
      & (
        (_cmp_cached_10)
        | (_cmp_cached_21)
        | (_cmp("RSI_3_1d", ">", 55.0))
        | (_cmp_cached_3)
        | (_cmp("RSI_14_1h", "<", 45.0))
        | (_cmp("RSI_14_4h", "<", 45.0))
        | (_cmp("AROONU_14_15m", "<", 25.0))
        | (_cmp_cached_31)
        | (_cmp("ROC_9_15m", ">", -40.0))
        | (_cmp("ROC_9_1d", ">", -40.0))
      )
      # 15m & 1h down move, 15m & 1h & 4h stil high, 15m & 1h & 4h high, 1d downtrend
      & (
        (_cmp_cached_10)
        | (_cmp_cached_21)
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp_cached_11)
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 60.0))
        | (_cmp_cached_66)
        | (_cmp("ROC_9_1d", ">", -50.0))
      )
      # 15m & 1h down move, 15m & 1h & 4h still high, 1h & 4h high, 4h overbought
      & (
        (_cmp_cached_10)
        | (_cmp_cached_21)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp_cached_40)
        | (_cmp_cached_34)
        | (_cmp_cached_80)
        | (_cmp_cached_66)
        | (_cmp("ROC_9_4h", "<", 30.0))
      )
      # 15m & 1h & 4h & 1d down move, 15m & 1h still not low enough, 4h still high, 4h downtrend, 4h high, 1d overbought
      & (
        (_cmp_cached_10)
        | (_cmp_cached_46)
        | (_cmp_cached_39)
        | (_cmp("RSI_3_1d", ">", 50.0))
        | (_cmp_cached_15)
        | (_cmp_cached_43)
        | (_cmp_cached_4)
        | (_cmp_cached_62)
        | (_cmp_cached_40)
        | (_cmp("ROC_9_1d", "<", 30.0))
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h still high, 4h high
      & (
        (_cmp_cached_10)
        | (_cmp_cached_46)
        | (_cmp_cached_18)
        | (_cmp_cached_0)
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp("AROONU_14_15m", "<", 40.0))
        | (_cmp_cached_75)
        | (_cmp_cached_37)
        | (_cmp_cached_59)
        | (_cmp_cached_70)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 15m & 1h high, 4h overbought
      & (
        (_cmp_cached_10)
        | (_cmp_cached_46)
        | (_cmp_cached_18)
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp_cached_11)
        | (_cmp("AROONU_14_1h", "<", 90.0))
        | (_cmp_cached_49)
      )
      # 15m & 1h down move, 15m & 1h & 4h still high, 15m & 1h & 4h high, 4h overbought
      & (
        (_cmp_cached_10)
        | (_cmp_cached_46)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp_cached_11)
        | (_cmp("AROONU_14_1h", "<", 60.0))
        | (_cmp_cached_16)
        | (_cmp_cached_77)
      )
      # 15m & 1h down move, 15m & 1h still high, 4h high, 4h & 1d overbought
      & (
        (_cmp_cached_10)
        | (_cmp_cached_46)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_29)
        | (_cmp_cached_31)
        | (_cmp_cached_38)
        | (_cmp_cached_58)
      )
      # 15m & 1h down move, 15m & 1h & 4h still high, 15m & 1h high, 1h & 4h overbought
      & (
        (_cmp_cached_10)
        | (_cmp_cached_46)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp_cached_11)
        | (_cmp_cached_79)
        | (_cmp_cached_67)
        | (_cmp_cached_49)
      )
      # 15m & 1h down move, 15m still not low enough, 1h & 4h still high, 1h & 4h downtrend, 4h high & overbought
      & (
        (_cmp_cached_10)
        | (_cmp_cached_46)
        | (_cmp_cached_0)
        | (_cmp_cached_6)
        | (_cmp_cached_36)
        | (_cmp_cached_64)
        | (_cmp_cached_62)
        | (_cmp_cached_83)
        | (_cmp_cached_56)
        | (_cmp("ROC_9_4h", "<", 30.0))
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h high, 4h downtrend
      & (
        (_cmp_cached_10)
        | (_cmp_cached_41)
        | (_cmp_cached_42)
        | (_cmp_cached_81)
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 80.0))
        | (_cmp("ROC_9_4h", ">", -25.0))
      )
      # 15m & 1h down move, 15m still high, 1h & 4h high, 1h overbought, 1d downtrend
      & (
        (_cmp_cached_10)
        | (_cmp_cached_41)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp_cached_40)
        | (_cmp_cached_76)
        | (_cmp("ROC_9_1h", "<", 20.0))
        | (_cmp("ROC_9_1d", ">", -30.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h high, 4h downtrend
      & (
        (_cmp_cached_10)
        | (_cmp_cached_60)
        | (_cmp_cached_18)
        | (_cmp_cached_11)
        | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 40.0))
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 60.0))
        | (_cmp_cached_66)
        | (_cmp("ROC_9_4h", ">", -15.0))
      )
      # 15m & 1h down move, 15m & 1h still high, 4h high, 1h & 4h high, 4h overbought
      & (
        (_cmp_cached_10)
        | (_cmp_cached_60)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_29)
        | (_cmp_cached_31)
        | (_cmp_cached_16)
        | (_cmp_cached_30)
        | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 90.0))
        | (_cmp("ROC_9_4h", "<", 60.0))
      )
      # 15m & 1h down move, 15m & 1hstill high, 4h downtrend, 15m still high, 1h high
      & (
        (_cmp_cached_10)
        | (_cmp_cached_60)
        | (_cmp("RSI_14_15m", "<", 50.0))
        | (_cmp_cached_6)
        | (_cmp_cached_62)
        | (_cmp_cached_17)
        | (_cmp_cached_69)
        | (_cmp_cached_81)
        | (_cmp_cached_80)
      )
      # 15m & 1h down move, 1h & 4h high, 4h overbought
      & (
        (_cmp_cached_10)
        | (_cmp_cached_60)
        | (_cmp_cached_6)
        | (_cmp_cached_29)
        | (_cmp_cached_31)
        | (_cmp_cached_76)
        | (_cmp("ROC_9_4h", "<", 120.0))
      )
      # 15m & 1h down move, 15m still high, 1h & 4h high, 1h & 4h & 1d overbought
      & (
        (_cmp_cached_10)
        | (_cmp("RSI_3_1h", ">", 65.0))
        | (_cmp_cached_3)
        | (_cmp("RSI_14_1h", "<", 60.0))
        | (_cmp_cached_29)
        | (_cmp_cached_31)
        | (_cmp_cached_16)
        | (_cmp("ROC_9_1h", "<", 20.0))
        | (_cmp("ROC_9_4h", "<", 50.0))
        | (_cmp("ROC_9_1d", "<", 250.0))
      )
      # 15m & 4h down move, 15m high, 1h still not low enough, 4h downtrend
      & (
        (_cmp_cached_10)
        | (_cmp("RSI_3_4h", ">", 3.0))
        | (_cmp_cached_11)
        | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 40.0))
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 20.0))
        | (_cmp_cached_78)
      )
      # 15m & 4h down move, 15m & 1h high, 4h downtrend
      & (
        (_cmp_cached_10)
        | (_cmp("RSI_3_4h", ">", 10.0))
        | (_cmp_cached_61)
        | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 40.0))
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 80.0))
        | (_cmp_cached_78)
      )
      # 15m & 4h & 1d down move, 15m still high, 1h & 4h downtrend
      & (
        (_cmp_cached_10)
        | (_cmp("RSI_3_4h", ">", 15.0))
        | (_cmp("RSI_3_1d", ">", 15.0))
        | (_cmp_cached_3)
        | (_cmp_cached_53)
        | (_cmp_cached_71)
        | (_cmp_cached_17)
        | (_cmp_cached_28)
      )
      # 15m & 4h & 1d down move, 15m high, 1d overbought
      & (
        (_cmp_cached_10)
        | (_cmp_cached_35)
        | (_cmp("RSI_3_1d", ">", 30.0))
        | (_cmp_cached_11)
        | (_cmp_cached_51)
      )
      # 15m & 4h down move, 15m & 1h still high, 15m & 1h high, 4h downtrend
      & (
        (_cmp_cached_10)
        | (_cmp("RSI_3_4h", ">", 3.0))
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_11)
        | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 40.0))
        | (_cmp_cached_80)
        | (_cmp("ROC_9_4h", ">", -25.0))
      )
      # 15m & 4h down move, 15m & 1h still not low enough, 4h still high,  1h & 4h downtrend, 15m & 1h & 4h still high
      & (
        (_cmp_cached_10)
        | (_cmp_cached_35)
        | (_cmp_cached_15)
        | (_cmp_cached_5)
        | (_cmp_cached_4)
        | (_cmp_cached_64)
        | (_cmp_cached_62)
        | (_cmp_cached_63)
        | (_cmp_cached_83)
        | (_cmp("AROONU_14_4h", "<", 40.0))
      )
      # 15m & 4h down move, 15m & 1h & 4h still high, 1h & 4h downtrend
      & (
        (_cmp_cached_10)
        | (_cmp_cached_35)
        | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 40.0))
        | (_cmp_cached_59)
        | (_cmp_cached_47)
        | (_cmp("ROC_9_1h", ">", -20.0))
        | (_cmp_cached_78)
      )
      # 15m & 4h down move, 15m & 1h & 4h still high, 15m & 4h high, 1d overbought
      & (
        (_cmp_cached_10)
        | (_cmp_cached_33)
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp_cached_11)
        | (_cmp_cached_34)
        | (_cmp_cached_51)
      )
      # 15m & 4h down move, 15m & 1h & 4h still high, 15m & 1h high, 1h overbought
      & (
        (_cmp_cached_10)
        | (_cmp_cached_18)
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp_cached_17)
        | (_cmp_cached_69)
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 80.0))
        | (_cmp_cached_67)
      )
      # 15m & 4h down move, 15m & 1h & 4h still high, 15m & 4h high, 4h & 1d overbought
      & (
        (_cmp_cached_10)
        | (_cmp_cached_18)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp_cached_11)
        | (_cmp_cached_34)
        | (_cmp_cached_72)
        | (_cmp("ROC_9_1d", "<", 200.0))
      )
      # 15m & 4h down move, 15m still not low enough, 1h & 4h still high, 15m & 1h & 4h still high, 4h overbought
      & (
        (_cmp_cached_10)
        | (_cmp_cached_44)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp_cached_11)
        | (_cmp_cached_30)
        | (_cmp_cached_47)
        | (_cmp("ROC_9_4h", "<", 50.0))
      )
      # 15m & 1d down move, 1h & 4h still not low enough, 1h & 4h downtrend, 4h still high
      & (
        (_cmp_cached_10)
        | (_cmp("RSI_3_1d", ">", 25.0))
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp("MFI_14_1h", "<", 40.0))
        | (_cmp("MFI_14_4h", "<", 50.0))
        | (_cmp("CMF_20_1h", ">", -0.0))
        | (_cmp_cached_71)
        | (_cmp_cached_22)
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 20.0))
        | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 40.0))
      )
      # 15m down move, 15m & 1h & 4h still high, 15m & 1h & 4h high, 1h & 4h high, 4h overbought
      & (
        (_cmp_cached_10)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp_cached_61)
        | (_cmp_cached_40)
        | (_cmp_cached_34)
        | (_cmp_cached_30)
        | (_cmp_cached_66)
        | (_cmp_cached_38)
      )
      # 15m down move, 15m & 1h & 4h still high, 15m & 1h downtrend, 4h high, 15m & 1h still high
      & (
        (_cmp_cached_10)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp_cached_55)
        | (_cmp_cached_64)
        | (_cmp_cached_34)
        | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 40.0))
        | (_cmp_cached_59)
      )
      # 15m down move, 15m still high, 1h >& 4h high, 15m & 1h & 4h high, 4h overbought
      & (
        (_cmp_cached_10)
        | (_cmp_cached_3)
        | (_cmp("RSI_14_1h", "<", 60.0))
        | (_cmp_cached_36)
        | (_cmp_cached_11)
        | (_cmp_cached_40)
        | (_cmp_cached_16)
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 30.0))
        | (_cmp_cached_66)
        | (_cmp_cached_72)
      )
      # 15m down move, 15m still high, 1h & 4h high, 4h overbought
      & (
        (_cmp_cached_10)
        | (_cmp_cached_3)
        | (_cmp("RSI_14_1h", "<", 60.0))
        | (_cmp_cached_84)
        | (_cmp_cached_11)
        | (_cmp_cached_20)
        | (_cmp_cached_28)
        | (_cmp_cached_72)
      )
      # 15m down move, 15m still high, 1h & 4h high, 1d downtrend, 4h overbought
      & (
        (_cmp_cached_10)
        | (_cmp_cached_3)
        | (_cmp("RSI_14_1h", "<", 70.0))
        | (_cmp("RSI_14_4h", "<", 75.0))
        | (_cmp("CMF_20_1d", ">", -0.0))
        | (_cmp_cached_76)
        | (_cmp("ROC_9_4h", "<", 50.0))
      )
      # 15m down move, 15m & 1h high, 1h & 4h overbought
      & (
        (_cmp_cached_10)
        | (_cmp("AROONU_14_15m", "<", 80.0))
        | (_cmp_cached_79)
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 90.0))
        | (_cmp_cached_67)
        | (_cmp_cached_38)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 15m & 4h downtrend, 1h & 4h still not low enough
      & (
        (_cmp_cached_13)
        | (_cmp_cached_48)
        | (_cmp("RSI_3_4h", ">", 15.0))
        | (_cmp("RSI_14_15m", "<", 10.0))
        | (_cmp_cached_43)
        | (_cmp("RSI_14_4h", "<", 20.0))
        | (_cmp_cached_74)
        | (_cmp("CMF_20_4h", ">", -0.30))
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 30.0))
        | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 30.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enugh, 4h still high, 15m still high, 1h & 4h downtrend
      & (
        (_cmp_cached_13)
        | (_cmp_cached_48)
        | (_cmp("RSI_3_4h", ">", 15.0))
        | (_cmp_cached_15)
        | (_cmp_cached_43)
        | (_cmp_cached_12)
        | (_cmp("AROONU_14_1h", "<", 10.0))
        | (_cmp("AROONU_14_4h", "<", 40.0))
        | (_cmp_cached_28)
        | (_cmp("ROC_9_1h", ">", -20.0))
        | (_cmp_cached_78)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 1h downtrend
      & (
        (_cmp_cached_13)
        | (_cmp_cached_14)
        | (_cmp_cached_33)
        | (_cmp_cached_15)
        | (_cmp_cached_43)
        | (_cmp("RSI_14_4h", "<", 20.0))
        | (_cmp_cached_63)
        | (_cmp_cached_50)
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 30.0))
        | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 30.0))
        | (_cmp("ROC_9_1h", ">", -15.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h still not low enough, 4h still high, 15m & 1h & 4h downtrend
      & (
        (_cmp_cached_13)
        | (_cmp_cached_14)
        | (_cmp_cached_33)
        | (_cmp_cached_15)
        | (_cmp_cached_43)
        | (_cmp_cached_2)
        | (_cmp("CMF_20_15m", ">", -0.35))
        | (_cmp("ROC_9_1h", ">", -10.0))
        | (_cmp("ROC_9_4h", ">", -15.0))
      )
      # 15m & 1h & 4h & 1d down move, 15m & 1h & 4h still not low enough, 15m still high, 1h & 4h & 1d downtrend
      & (
        (_cmp_cached_13)
        | (_cmp_cached_14)
        | (_cmp_cached_33)
        | (_cmp("RSI_3_1d", ">", 30.0))
        | (_cmp("RSI_14_15m", "<", 25.0))
        | (_cmp("RSI_14_1h", "<", 25.0))
        | (_cmp("RSI_14_4h", "<", 25.0))
        | (_cmp("AROONU_14_15m", "<", 40.0))
        | (_cmp("ROC_9_1h", ">", -15.0))
        | (_cmp("ROC_9_4h", ">", -15.0))
        | (_cmp("ROC_9_1d", ">", -15.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 1h & 4h downtrend, 4h downtrend
      & (
        (_cmp_cached_13)
        | (_cmp_cached_14)
        | (_cmp_cached_33)
        | (_cmp_cached_0)
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp_cached_53)
        | (_cmp_cached_71)
        | (_cmp("AROONU_14_4h", "<", 40.0))
        | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 30.0))
        | (_cmp("ROC_9_4h", ">", -20.0))
      )
      # 15m & 1h & 4h & 1d down move, 15m still not low enough, 1h & 4h still high, 15m downtrend, 4h high
      & (
        (_cmp_cached_13)
        | (_cmp_cached_14)
        | (_cmp_cached_32)
        | (_cmp("RSI_3_1d", ">", 60.0))
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp("CMF_20_15m", ">", -0.15))
        | (_cmp_cached_34)
        | (_cmp("CCI_20_1h", "<", -100.0))
        | (_cmp("CCI_20_4h", "<", 0.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h still not low enough, 4h still high, 15m & 4h high, 4h overbought
      & (
        (_cmp_cached_13)
        | (_cmp_cached_14)
        | (_cmp_cached_32)
        | (_cmp_cached_0)
        | (_cmp_cached_5)
        | (_cmp_cached_4)
        | (_cmp_cached_11)
        | (_cmp_cached_20)
        | (_cmp_cached_72)
      )
      # 15m & 1h & 4h & 1d down move, 15m & 1h & 4h still not low enough, 4h downtrend, 1d high
      & (
        (_cmp_cached_13)
        | (_cmp_cached_14)
        | (_cmp_cached_25)
        | (_cmp("RSI_3_1d", ">", 45.0))
        | (_cmp_cached_0)
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp("CMF_20_4h", ">", -0.25))
        | (_cmp("AROONU_14_1d", "<", 90.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 15m still not low enough, 4h high & overbought
      & (
        (_cmp_cached_13)
        | (_cmp_cached_14)
        | (_cmp_cached_39)
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp("AROONU_14_15m", "<", 25.0))
        | (_cmp_cached_34)
        | (_cmp("ROC_9_4h", "<", 80.0))
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 1d overbought
      & (
        (_cmp_cached_13)
        | (_cmp_cached_14)
        | (_cmp_cached_18)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_81)
        | (_cmp_cached_68)
      )
      # 15m & 1h down move, 15m still not low enough, 1h & 4h still high, 15m & 1h downtrend, 15m & 4h high
      & (
        (_cmp_cached_13)
        | (_cmp_cached_14)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_73)
        | (_cmp("CMF_20_1h", ">", -0.30))
        | (_cmp_cached_11)
        | (_cmp("AROONU_14_4h", "<", 60.0))
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 1h & 4h high
      & (
        (_cmp_cached_13)
        | (_cmp_cached_23)
        | (_cmp_cached_52)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp_cached_40)
        | (_cmp_cached_16)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h stil high, 15m high, 4h downtrend
      & (
        (_cmp_cached_13)
        | (_cmp_cached_23)
        | (_cmp_cached_39)
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_11)
        | (_cmp("ROC_9_4h", ">", -40.0))
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 4h high, 4h & 1d overbought
      & (
        (_cmp_cached_13)
        | (_cmp_cached_23)
        | (_cmp_cached_42)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_83)
        | (_cmp_cached_56)
        | (_cmp_cached_38)
        | (_cmp_cached_68)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 15m & 4h high, 1h still not low enough, 4h high
      & (
        (_cmp_cached_13)
        | (_cmp_cached_23)
        | (_cmp_cached_18)
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_11)
        | (_cmp("AROONU_14_4h", "<", 60.0))
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 30.0))
        | (_cmp_cached_70)
      )
      # 15m & 1h down move, 15m & 1h & 4h still high, 1h & 4h downtrend, 15m & 1h high
      & (
        (_cmp_cached_13)
        | (_cmp_cached_23)
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp_cached_64)
        | (_cmp_cached_62)
        | (_cmp_cached_11)
        | (_cmp_cached_79)
      )
      # 15m & 1h down move, 15m still not low enough, 1h sitll high, 1h & 4h high, 4h overbought
      & (
        (_cmp_cached_13)
        | (_cmp_cached_23)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_84)
        | (_cmp_cached_31)
        | (_cmp_cached_16)
        | (_cmp_cached_38)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 15m & 1h still high, 4h high
      & (
        (_cmp_cached_13)
        | (_cmp_cached_19)
        | (_cmp_cached_32)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp_cached_17)
        | (_cmp_cached_22)
        | (_cmp_cached_28)
        | (_cmp_cached_70)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 15h & 4h high
      & (
        (_cmp_cached_13)
        | (_cmp_cached_19)
        | (_cmp_cached_32)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp_cached_11)
        | (_cmp_cached_34)
        | (_cmp_cached_28)
      )
      # 15m & 1h & 4h down move, 15m high
      & (
        (_cmp_cached_13)
        | (_cmp_cached_19)
        | (_cmp_cached_32)
        | (_cmp_cached_61)
        | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 70.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 1h high
      & (
        (_cmp_cached_13)
        | (_cmp_cached_19)
        | (_cmp_cached_39)
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp_cached_17)
        | (_cmp_cached_79)
        | (_cmp_cached_30)
        | (_cmp_cached_47)
      )
      # 15m & 1h & 4h down move, 15m still low, 1h & 4h still high, 4h high & overbought
      & (
        (_cmp_cached_13)
        | (_cmp_cached_19)
        | (_cmp_cached_39)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_20)
        | (_cmp("ROC_9_4h", "<", 100.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h stil high, 15m & 4h still high, 4h overbought
      & (
        (_cmp_cached_13)
        | (_cmp_cached_19)
        | (_cmp_cached_39)
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_17)
        | (_cmp_cached_37)
        | (_cmp_cached_38)
      )
      # 15m & 1h & 4h & 1d down move, 15m & 1h & 4h high, 1d downtrend
      & (
        (_cmp_cached_13)
        | (_cmp_cached_21)
        | (_cmp_cached_25)
        | (_cmp("RSI_3_1d", ">", 45.0))
        | (_cmp_cached_11)
        | (_cmp_cached_69)
        | (_cmp_cached_16)
        | (_cmp("ROC_9_1d", ">", -50.0))
      )
      # 15m & 1h & 4h & 1d down move, 15m still not low enough, 1h & 4h still high, 4h downtrend, 1d overbought
      & (
        (_cmp_cached_13)
        | (_cmp_cached_21)
        | (_cmp_cached_25)
        | (_cmp("RSI_3_1d", ">", 50.0))
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp("ROC_9_4h", ">", -20.0))
        | (_cmp_cached_51)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 15m high
      & (
        (_cmp_cached_13)
        | (_cmp_cached_21)
        | (_cmp_cached_39)
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp_cached_61)
        | (_cmp_cached_28)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h stil high, 15m & 4h still high, 4h overbought
      & (
        (_cmp_cached_13)
        | (_cmp_cached_21)
        | (_cmp_cached_18)
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_17)
        | (_cmp_cached_34)
        | (_cmp_cached_38)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 15m & 1h high, 4h & 1d overbought
      & (
        (_cmp_cached_13)
        | (_cmp_cached_21)
        | (_cmp_cached_44)
        | (_cmp_cached_0)
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp_cached_11)
        | (_cmp_cached_79)
        | (_cmp_cached_49)
        | (_cmp("ROC_9_1d", "<", 30.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 1d overbought
      & (
        (_cmp_cached_13)
        | (_cmp_cached_21)
        | (_cmp_cached_44)
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp("CCI_20_1h", "<", 0.0))
        | (_cmp("CCI_20_4h", "<", 0.0))
        | (_cmp("ROC_9_1d", "<", 200.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h still high, 1h & 4h high, 4h overbought
      & (
        (_cmp_cached_13)
        | (_cmp_cached_21)
        | (_cmp_cached_44)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_36)
        | (_cmp_cached_31)
        | (_cmp("ROC_9_4h", "<", 70.0))
      )
      # 15m & 1h down move, 15m still not low enough, 1h & 4h still high, 15m downtrend, 15m still high, 1h high
      & (
        (_cmp_cached_13)
        | (_cmp_cached_21)
        | (_cmp_cached_15)
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp_cached_73)
        | (_cmp_cached_17)
        | (_cmp_cached_79)
      )
      # 15m & 1h down move, 15m still not low enough, 1h stil high, 4h high, 1h downtrend
      & (
        (_cmp_cached_13)
        | (_cmp_cached_21)
        | (_cmp_cached_0)
        | (_cmp_cached_6)
        | (_cmp_cached_84)
        | (_cmp_cached_64)
        | (_cmp_cached_75)
        | (_cmp_cached_20)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 1h & 4h high, 1d overbought
      & (
        (_cmp_cached_13)
        | (_cmp_cached_46)
        | (_cmp_cached_39)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp("AROONU_14_1h", "<", 60.0))
        | (_cmp_cached_16)
        | (_cmp_cached_68)
      )
      # 15m & 1h down move, 15m still not low enough, 1h & 4h still high, 1h high, 1h & 1d overbought
      & (
        (_cmp_cached_13)
        | (_cmp_cached_46)
        | (_cmp_cached_0)
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp("AROONU_14_1h", "<", 60.0))
        | (_cmp("ROC_9_1h", "<", 20.0))
        | (_cmp_cached_68)
      )
      # 15m & 1h & 4h & 1d down move, 15m & 4h downtrend, 15m & 1h high
      & (
        (_cmp_cached_13)
        | (_cmp_cached_41)
        | (_cmp_cached_42)
        | (_cmp("RSI_3_1d", ">", 55.0))
        | (_cmp_cached_73)
        | (_cmp_cached_71)
        | (_cmp_cached_11)
        | (_cmp_cached_79)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 15m high
      & (
        (_cmp_cached_13)
        | (_cmp_cached_41)
        | (_cmp_cached_42)
        | (_cmp_cached_0)
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 80.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 1h & 4h downtrend, 1h high, 4h downtrend
      & (
        (_cmp_cached_13)
        | (_cmp_cached_41)
        | (_cmp_cached_44)
        | (_cmp_cached_0)
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp_cached_53)
        | (_cmp("CMF_20_4h", ">", -0.25))
        | (_cmp_cached_31)
        | (_cmp("ROC_9_4h", ">", -20.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 1h & 4h high, 4h overbought
      & (
        (_cmp_cached_13)
        | (_cmp_cached_41)
        | (_cmp_cached_44)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp("AROONU_14_1h", "<", 60.0))
        | (_cmp_cached_56)
        | (_cmp_cached_30)
        | (_cmp_cached_70)
        | (_cmp_cached_72)
      )
      # 15m & 1h & 4h down move, 15m & 1h still not low enough, 4h still high, 4h downtrend, 1h still high
      & (
        (_cmp_cached_13)
        | (_cmp_cached_60)
        | (_cmp_cached_18)
        | (_cmp_cached_15)
        | (_cmp_cached_5)
        | (_cmp_cached_4)
        | (_cmp("CMF_20_4h", ">", -0.30))
        | (_cmp_cached_75)
        | (_cmp_cached_30)
      )
      # 15m & 1h down move, 15m & 1h & 4h still high, 4h high, 4h & 1d overbought
      & (
        (_cmp_cached_13)
        | (_cmp_cached_60)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp_cached_34)
        | (_cmp("ROC_9_4h", "<", 50.0))
        | (_cmp("ROC_9_1d", "<", 150.0))
      )
      # 15m & 1h down move, 15m still high, 1h & 4h high & overbought
      & (
        (_cmp_cached_13)
        | (_cmp_cached_60)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_84)
        | (_cmp("AROONU_14_1h", "<", 60.0))
        | (_cmp_cached_76)
        | (_cmp("ROC_9_1h", "<", 50.0))
        | (_cmp("ROC_9_4h", "<", 100.0))
      )
      # 15m & 1h down move, 15m still high, 1h & 4h high, 4h overbought
      & (
        (_cmp_cached_13)
        | (_cmp("RSI_3_1h", ">", 65.0))
        | (_cmp_cached_3)
        | (_cmp("RSI_14_1h", "<", 60.0))
        | (_cmp_cached_84)
        | (_cmp_cached_76)
        | (_cmp("ROC_9_4h", "<", 130.0))
      )
      # 15m & 4h down move, 15m & 1h & 4h still high, 15m still high
      & (
        (_cmp_cached_13)
        | (_cmp("RSI_3_4h", ">", 5.0))
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp_cached_17)
        | (_cmp_cached_81)
      )
      # 15m & 4h down move, 15m & 1h high, 4h downtrend
      & (
        (_cmp_cached_13)
        | (_cmp("RSI_3_4h", ">", 15.0))
        | (_cmp_cached_17)
        | (_cmp_cached_50)
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 80.0))
        | (_cmp("ROC_9_4h", ">", -50.0))
      )
      # 15m & 4h down move, 15m & 1h still high, 1h & 4h downtrend, 15m & 1h still high
      & (
        (_cmp_cached_13)
        | (_cmp_cached_33)
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_64)
        | (_cmp("CMF_20_4h", ">", -0.30))
        | (_cmp_cached_11)
        | (_cmp_cached_28)
        | (_cmp_cached_30)
      )
      # 15m & 4h down move, 15m & 1h & 4h still high, 15m & 4h high
      & (
        (_cmp_cached_13)
        | (_cmp_cached_33)
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp_cached_11)
        | (_cmp_cached_34)
      )
      # 15m & 1h down move, 15m still high, 1h & 4h high & overbought
      & (
        (_cmp_cached_13)
        | (_cmp("RSI_3_1h", ">", 65.0))
        | (_cmp_cached_3)
        | (_cmp("RSI_14_1h", "<", 60.0))
        | (_cmp("RSI_14_4h", "<", 75.0))
        | (_cmp_cached_31)
        | (_cmp_cached_16)
        | (_cmp("ROC_9_1h", "<", 40.0))
        | (_cmp_cached_77)
      )
      # 15m & 4h down move, 15m & 1h & 4h still high, 15m high
      & (
        (_cmp_cached_13)
        | (_cmp_cached_25)
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp("AROONU_14_15m", "<", 80.0))
        | (_cmp_cached_28)
      )
      # 15m & 4h down move, 15m & 1h & 4h stil high, 14m & 4h high
      & (
        (_cmp_cached_13)
        | (_cmp_cached_42)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp_cached_61)
        | (_cmp_cached_76)
        | (_cmp_cached_28)
        | (_cmp_cached_66)
      )
      # 15m & 4h down move, 15m still not low enough, 1h & 4h still high, 15m & 4h high, 1d overbought
      & (
        (_cmp_cached_13)
        | (_cmp_cached_18)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_61)
        | (_cmp("AROONU_14_4h", "<", 30.0))
        | (_cmp("ROC_9_1d", "<", 200.0))
      )
      # 15m down move, 15m still not low enough, 1h & 4h high
      & (
        (_cmp_cached_13)
        | (_cmp_cached_0)
        | (_cmp("RSI_14_1h", "<", 70.0))
        | (_cmp_cached_29)
        | (_cmp_cached_31)
        | (_cmp_cached_16)
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 80.0))
        | (_cmp_cached_66)
      )
      # 15m down move, 15m & 1h & 4h still high, 15m high, 15m & 1h still high, 4h high, 4h overbought
      & (
        (_cmp_cached_13)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp_cached_61)
        | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 40.0))
        | (_cmp_cached_59)
        | (_cmp_cached_70)
        | (_cmp_cached_38)
      )
      # 15m & 1h down move, 15m & 1h still high, 1h & 4h high, 4h overbought
      & (
        (_cmp_cached_45)
        | (_cmp_cached_24)
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_36)
        | (_cmp_cached_31)
        | (_cmp_cached_16)
        | (_cmp_cached_38)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 15m & 4h still high, 1d downtrend
      & (
        (_cmp_cached_45)
        | (_cmp_cached_23)
        | (_cmp_cached_52)
        | (_cmp_cached_0)
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 40.0))
        | (_cmp_cached_47)
        | (_cmp("ROC_9_1d", ">", -50.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h still not low enough, 4h high, 1d overbought
      & (
        (_cmp_cached_45)
        | (_cmp_cached_23)
        | (_cmp_cached_25)
        | (_cmp_cached_15)
        | (_cmp_cached_5)
        | (_cmp_cached_36)
        | (_cmp("ROC_9_1d", "<", 200.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h still high, 4h high, 15m & 4h high, 4h overbought
      & (
        (_cmp_cached_45)
        | (_cmp_cached_23)
        | (_cmp_cached_44)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_29)
        | (_cmp_cached_11)
        | (_cmp_cached_34)
        | (_cmp_cached_38)
      )
      # 15m & 1h down move, 15m still not low enough, 1h still high, 15m high, 4h high & overbought
      & (
        (_cmp_cached_45)
        | (_cmp_cached_19)
        | (_cmp_cached_0)
        | (_cmp_cached_6)
        | (_cmp_cached_84)
        | (_cmp_cached_11)
        | (_cmp_cached_34)
        | (_cmp_cached_66)
        | (_cmp_cached_77)
      )
      # 15m & 1h & 4h down move, 15m & 1h high
      & (
        (_cmp_cached_45)
        | (_cmp_cached_21)
        | (_cmp_cached_25)
        | (_cmp_cached_61)
        | (_cmp_cached_79)
        | (_cmp_cached_81)
        | (_cmp_cached_80)
      )
      # 15m & 1h & 4h & 1d down move, 15m & 1h & 4h still high, 15m & 1h high, 1d overbought
      & (
        (_cmp_cached_45)
        | (_cmp_cached_21)
        | (_cmp_cached_25)
        | (_cmp("RSI_3_1d", ">", 45.0))
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp_cached_11)
        | (_cmp_cached_40)
        | (_cmp_cached_51)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still highm 15m & 1h high, 1h still high, 4h high
      & (
        (_cmp_cached_45)
        | (_cmp_cached_21)
        | (_cmp_cached_25)
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp_cached_11)
        | (_cmp_cached_69)
        | (_cmp_cached_59)
        | (_cmp_cached_70)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 15m & 4h high, 4h & 1d overbought
      & (
        (_cmp_cached_45)
        | (_cmp_cached_21)
        | (_cmp_cached_42)
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_11)
        | (_cmp("AROONU_14_4h", "<", 60.0))
        | (_cmp_cached_49)
        | (_cmp_cached_51)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 15m & 4h high, 1d overbought
      & (
        (_cmp_cached_45)
        | (_cmp_cached_21)
        | (_cmp_cached_42)
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_61)
        | (_cmp_cached_56)
        | (_cmp_cached_28)
        | (_cmp("ROC_9_1d", "<", 40.0))
      )
      # 15m & 1h down move, 15m still not low enough, 1h & 4h still high, 1h & 4h downtrend, 1h still high, 4h high
      & (
        (_cmp_cached_45)
        | (_cmp_cached_21)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp("CMF_20_1h", ">", -0.30))
        | (_cmp("CMF_20_1h", ">", -0.30))
        | (_cmp_cached_22)
        | (_cmp_cached_20)
      )
      # 15m & 1h down move, 15m still not low enough, 1h still high, 4h high & overbought
      & (
        (_cmp_cached_45)
        | (_cmp_cached_21)
        | (_cmp_cached_0)
        | (_cmp_cached_6)
        | (_cmp_cached_84)
        | (_cmp("STOCHk_14_3_3_1h", "<", 60.0))
        | (_cmp("STOCHk_14_3_3_4h", "<", 90.0))
        | (_cmp("ROC_9_4h", "<", 80.0))
      )
      # 15m & 1h & 4h down move, 15m high
      & (
        (_cmp_cached_45)
        | (_cmp_cached_46)
        | (_cmp_cached_39)
        | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 90.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 15m high, 1d overbought
      & (
        (_cmp_cached_45)
        | (_cmp_cached_46)
        | (_cmp_cached_18)
        | (_cmp("RSI_14_15m", "<", 50.0))
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp_cached_61)
        | (_cmp_cached_68)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 15m & 1h & 4h still high
      & (
        (_cmp_cached_45)
        | (_cmp_cached_41)
        | (_cmp_cached_35)
        | (_cmp_cached_0)
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 60.0))
        | (_cmp_cached_59)
        | (_cmp_cached_47)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h stil high, 1h & 4h high, 1h overbought
      & (
        (_cmp_cached_45)
        | (_cmp_cached_41)
        | (_cmp_cached_42)
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp_cached_63)
        | (_cmp_cached_31)
        | (_cmp_cached_20)
        | (_cmp_cached_67)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 15m still high, 4h overbought
      & (
        (_cmp_cached_45)
        | (_cmp_cached_41)
        | (_cmp_cached_42)
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_17)
        | (_cmp_cached_28)
        | (_cmp("ROC_9_4h", "<", 80.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 15m & 4h high, 1d overbought
      & (
        (_cmp_cached_45)
        | (_cmp_cached_41)
        | (_cmp_cached_18)
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_11)
        | (_cmp_cached_34)
        | (_cmp("ROC_9_1d", "<", 75.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 15m & 1h high
      & (
        (_cmp_cached_45)
        | (_cmp_cached_60)
        | (_cmp_cached_18)
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp_cached_61)
        | (_cmp("AROONU_14_1h", "<", 90.0))
        | (_cmp_cached_28)
        | (_cmp_cached_80)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 4h downtrend, 15m high
      & (
        (_cmp_cached_45)
        | (_cmp_cached_60)
        | (_cmp_cached_18)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_62)
        | (_cmp_cached_11)
        | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 70.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 15m still not low enough, 4h & 1h still high, 1d overbought
      & (
        (_cmp_cached_45)
        | (_cmp_cached_60)
        | (_cmp_cached_18)
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp("AROONU_14_15m", "<", 20.0))
        | (_cmp("AROONU_14_4h", "<", 40.0))
        | (_cmp_cached_30)
        | (_cmp("ROC_9_1d", "<", 150.0))
      )
      # 15m & 1h down move, 15m & 1h & 4h high, 1h overbought
      & (
        (_cmp_cached_45)
        | (_cmp("RSI_3_1h", ">", 65.0))
        | (_cmp("RSI_14_15m", "<", 50.0))
        | (_cmp_cached_31)
        | (_cmp_cached_76)
        | (_cmp("ROC_9_1h", "<", 20.0))
      )
      # 15m & 4h down move, 15m & 1h high, 4h downtrend
      & (
        (_cmp_cached_45)
        | (_cmp("RSI_3_4h", ">", 10.0))
        | (_cmp_cached_11)
        | (_cmp_cached_28)
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 80.0))
        | (_cmp_cached_78)
      )
      # 15m & 4h down move, 15m still high, 1h high, 15m & 1h high
      & (
        (_cmp_cached_45)
        | (_cmp_cached_52)
        | (_cmp_cached_3)
        | (_cmp("RSI_14_1h", "<", 70.0))
        | (_cmp_cached_11)
        | (_cmp_cached_79)
      )
      # 15m & 4h down move, 15m still not low enough, 1h & 4h still high, 15m & 1h high
      & (
        (_cmp_cached_45)
        | (_cmp_cached_52)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp_cached_61)
        | (_cmp_cached_79)
      )
      # 15m & 4h down move, 15m still not low enough, 1h & 4h still high, 1h & 4h downtrend, 15m & 1h still high
      & (
        (_cmp_cached_45)
        | (_cmp_cached_52)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp("CMF_20_1h", ">", -0.25))
        | (_cmp("CMF_20_4h", ">", -0.25))
        | (_cmp_cached_17)
        | (_cmp_cached_22)
        | (_cmp_cached_28)
      )
      # 15m & 4h down move, 15m & 1h & 4h still high, 15m & 1h high, 4h downtrend
      & (
        (_cmp_cached_45)
        | (_cmp_cached_25)
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp_cached_11)
        | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 40.0))
        | (_cmp_cached_80)
        | (_cmp("ROC_9_4h", ">", -20.0))
      )
      # 15m down move, 15m still high, 1h & 4h high, 1h & 4h overbought
      & (
        (_cmp_cached_45)
        | (_cmp("RSI_14_15m", "<", 50.0))
        | (_cmp("RSI_14_1h", "<", 60.0))
        | (_cmp_cached_29)
        | (_cmp_cached_31)
        | (_cmp_cached_16)
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 60.0))
        | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 60.0))
        | (_cmp("ROC_9_1h", "<", 20.0))
        | (_cmp_cached_38)
      )
      # 15m down move, 15m & 1h still high, 4h high, 15m downtrend, 15m high, 1h & 4h overbought
      & (
        (_cmp_cached_45)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_36)
        | (_cmp("CMF_20_15m", ">", -0.10))
        | (_cmp_cached_61)
        | (_cmp("ROC_9_1h", "<", 15.0))
        | (_cmp("ROC_9_4h", "<", 80.0))
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 15m downtrend, 4h high & overbought
      & (
        (_cmp_cached_65)
        | (_cmp_cached_19)
        | (_cmp_cached_32)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_74)
        | (_cmp_cached_34)
        | (_cmp("ROC_9_4h", "<", 70.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h sitll not low enough, 4h still high, 15m high
      & (
        (_cmp_cached_65)
        | (_cmp_cached_19)
        | (_cmp_cached_32)
        | (_cmp_cached_0)
        | (_cmp_cached_5)
        | (_cmp_cached_4)
        | (_cmp("AROONU_14_4h", "<", 40.0))
        | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 70.0))
      )
      # 15m & 1h & 4h & 1d down move, 1d downtrend, 4h still not low enough, 15m still high, 1h downtrend
      & (
        (_cmp_cached_65)
        | (_cmp_cached_19)
        | (_cmp_cached_25)
        | (_cmp("RSI_3_1d", ">", 45.0))
        | (_cmp("CMF_20_1d", ">", -0.40))
        | (_cmp("AROONU_14_4h", "<", 30.0))
        | (_cmp_cached_28)
        | (_cmp("ROC_9_1h", ">", -25.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h downtrend, 4h high
      & (
        (_cmp_cached_65)
        | (_cmp_cached_19)
        | (_cmp_cached_25)
        | (_cmp("CMF_20_15m", ">", -0.40))
        | (_cmp("CMF_20_1h", ">", -0.40))
        | (_cmp("CMF_20_4h", ">", -0.40))
        | (_cmp("AROONU_14_4h", "<", 75.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 4h high & overbought
      & (
        (_cmp_cached_65)
        | (_cmp_cached_19)
        | (_cmp_cached_18)
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_63)
        | (_cmp_cached_20)
        | (_cmp("ROC_9_4h", "<", 50.0))
      )
      # 15m & 1h down move, 15m still not low enough, 1h still high, 4h high & overbought
      & (
        (_cmp_cached_65)
        | (_cmp_cached_19)
        | (_cmp_cached_0)
        | (_cmp_cached_6)
        | (_cmp("RSI_14_4h", "<", 90.0))
        | (_cmp_cached_76)
        | (_cmp("ROC_9_4h", "<", 80.0))
      )
      # 15m & 1h down move, 15m still not low enough, 1h still high, 4h high, 15m still high, 4h high & overbought
      & (
        (_cmp_cached_9)
        | (_cmp_cached_46)
        | (_cmp_cached_0)
        | (_cmp_cached_6)
        | (_cmp_cached_29)
        | (_cmp("AROONU_14_15m", "<", 40.0))
        | (_cmp_cached_20)
        | (_cmp("ROC_9_4h", "<", 100.0))
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 15m high, 1h & 4h downtrend
      & (
        (_cmp_cached_65)
        | (_cmp_cached_21)
        | (_cmp_cached_25)
        | (_cmp_cached_15)
        | (_cmp_cached_43)
        | (_cmp_cached_12)
        | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 60.0))
        | (_cmp("ROC_9_1h", ">", -30.0))
        | (_cmp("ROC_9_4h", ">", -40.0))
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 15m & 1h high
      & (
        (_cmp_cached_65)
        | (_cmp_cached_21)
        | (_cmp_cached_25)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp_cached_11)
        | (_cmp_cached_79)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h high
      & (
        (_cmp_cached_65)
        | (_cmp_cached_21)
        | (_cmp_cached_42)
        | (_cmp_cached_11)
        | (_cmp_cached_79)
        | (_cmp_cached_16)
      )
      # 15m & 1h & 4h & 1d down move, 15m & 1h & 4h still high, 15m & 1h high, 1d overbought
      & (
        (_cmp_cached_65)
        | (_cmp_cached_46)
        | (_cmp_cached_18)
        | (_cmp("RSI_3_1d", ">", 60.0))
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp_cached_11)
        | (_cmp_cached_69)
        | (_cmp_cached_51)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 4h downtrend, 4h overbought
      & (
        (_cmp_cached_65)
        | (_cmp_cached_46)
        | (_cmp_cached_18)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp("CMF_20_4h", ">", -0.15))
        | (_cmp_cached_37)
        | (_cmp_cached_50)
        | (_cmp_cached_47)
        | (_cmp_cached_72)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 4h high & overbought
      & (
        (_cmp_cached_65)
        | (_cmp_cached_41)
        | (_cmp_cached_42)
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_20)
        | (_cmp("ROC_9_4h", "<", 50.0))
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 1h & 4h downtrend, 1h high, 4h overbought
      & (
        (_cmp_cached_65)
        | (_cmp("RSI_3_1h", ">", 65.0))
        | (_cmp_cached_44)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp_cached_64)
        | (_cmp("CMF_20_4h", ">", -0.30))
        | (_cmp("AROONU_14_15m", "<", 20.0))
        | (_cmp_cached_40)
        | (_cmp_cached_49)
      )
      # 15m & 1h down move, 15m & 1h & 4h still high, 15m still high, 1h high, 1h overbought
      & (
        (_cmp_cached_65)
        | (_cmp("RSI_3_1h", ">", 65.0))
        | (_cmp("RSI_14_15m", "<", 50.0))
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp_cached_17)
        | (_cmp_cached_69)
        | (_cmp_cached_50)
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 80.0))
        | (_cmp("ROC_9_1h", "<", 20.0))
      )
      # 15m &4h down move, 15m & 1h & 4h still high, 15m still high, 1h high, 15m & 1h overbought
      & (
        (_cmp_cached_65)
        | (_cmp_cached_39)
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp("AROONU_14_15m", "<", 40.0))
        | (_cmp_cached_31)
        | (_cmp("ROC_9_15m", "<", 10.0))
        | (_cmp("ROC_9_1h", "<", 40.0))
      )
      # 15m & 4h down move, 15m & 1h & 4h still high, 15m & 1h high, 1h overbought
      & (
        (_cmp_cached_65)
        | (_cmp_cached_42)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp_cached_11)
        | (_cmp_cached_80)
        | (_cmp("ROC_9_1h", "<", 20.0))
      )
      # 15m & 1d down move, 15m & 1h & 4h stil high, 4h high, 15m & 1h & 4h still high
      & (
        (_cmp_cached_65)
        | (_cmp("RSI_3_1d", ">", 20.0))
        | (_cmp("RSI_14_15m", "<", 50.0))
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp_cached_20)
        | (_cmp_cached_28)
        | (_cmp_cached_30)
        | (_cmp_cached_47)
      )
      # 15m down move, 15m & 1h still high, 4h high & overbought
      & (
        (_cmp_cached_65)
        | (_cmp("RSI_14_15m", "<", 50.0))
        | (_cmp_cached_6)
        | (_cmp("RSI_14_4h", "<", 90.0))
        | (_cmp_cached_75)
        | (_cmp_cached_56)
        | (_cmp("ROC_9_4h", "<", 100.0))
      )
      # 15m down move, 15m still high, 1h & 4h high & overbought
      & (
        (_cmp_cached_65)
        | (_cmp("RSI_14_15m", "<", 50.0))
        | (_cmp("RSI_14_1h", "<", 70.0))
        | (_cmp_cached_84)
        | (_cmp_cached_40)
        | (_cmp_cached_16)
        | (_cmp("ROC_9_1h", "<", 70.0))
        | (_cmp("ROC_9_4h", "<", 80.0))
      )
      # 15m down move, 15m & 1h & 4h still high, 15m & 1h & 4h high
      & (
        (_cmp_cached_65)
        | (_cmp("RSI_14_15m", "<", 50.0))
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp_cached_11)
        | (_cmp_cached_79)
        | (_cmp_cached_16)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 15m & 4h still high, 4h & 1d overbought
      & (
        (_cmp("RSI_3_15m", ">", 45.0))
        | (_cmp_cached_21)
        | (_cmp_cached_44)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp_cached_17)
        | (_cmp_cached_37)
        | (_cmp_cached_77)
        | (_cmp_cached_58)
      )
      # 15m & 1h down move, 15m & 1h & 4h still high, 15m & 1h & 4h downtrend, 4h high
      & (
        (_cmp("RSI_3_15m", ">", 45.0))
        | (_cmp_cached_21)
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp("CMF_20_15m", ">", -0.10))
        | (_cmp_cached_64)
        | (_cmp_cached_62)
        | (_cmp_cached_20)
        | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 90.0))
      )
      # 15m & 1h down move, 15m & 1h & 4h still high, 1h & 4h & 1d downtrend, 1h & 4h high
      & (
        (_cmp("RSI_3_15m", ">", 45.0))
        | (_cmp_cached_21)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp_cached_64)
        | (_cmp_cached_62)
        | (_cmp("CMF_20_1d", ">", -0.30))
        | (_cmp_cached_40)
        | (_cmp_cached_76)
      )
      # 15m & 1h down move, 1h & 4h still high, 4h high, 1h & 4h overbought
      & (
        (_cmp("RSI_3_15m", ">", 45.0))
        | (_cmp_cached_21)
        | (_cmp_cached_6)
        | (_cmp_cached_36)
        | (_cmp_cached_20)
        | (_cmp_cached_66)
        | (_cmp("ROC_9_1h", "<", 30.0))
        | (_cmp("ROC_9_4h", "<", 100.0))
      )
      # 15m & 1h & 4h & 1d down move, 15m still not low enough, 1h & 4h still high, 15m still high, 1d overbought
      & (
        (_cmp("RSI_3_15m", ">", 45.0))
        | (_cmp_cached_46)
        | (_cmp_cached_39)
        | (_cmp("RSI_3_1d", ">", 50.0))
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp_cached_28)
        | (_cmp_cached_68)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 15m still high, 4h high & overbought
      & (
        (_cmp("RSI_3_15m", ">", 45.0))
        | (_cmp_cached_41)
        | (_cmp_cached_39)
        | (_cmp_cached_0)
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_34)
        | (_cmp_cached_77)
      )
      # 15m & 1h down move, 15m & 1h still high, 4h high, 1h & 4h high, 1h & 4h overbought
      & (
        (_cmp("RSI_3_15m", ">", 45.0))
        | (_cmp_cached_60)
        | (_cmp("RSI_14_15m", "<", 50.0))
        | (_cmp_cached_6)
        | (_cmp_cached_29)
        | (_cmp_cached_40)
        | (_cmp_cached_76)
        | (_cmp("ROC_9_1h", "<", 30.0))
        | (_cmp("ROC_9_4h", "<", 80.0))
      )
      # 15m & 1h down move, 15m still high, 1h high, 15m overbought
      & (
        (_cmp("RSI_3_15m", ">", 45.0))
        | (_cmp_cached_60)
        | (_cmp_cached_17)
        | (_cmp_cached_79)
        | (_cmp_cached_28)
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 80.0))
        | (_cmp("ROC_9_15m", "<", 20.0))
      )
      # 15m & 4h down move, 15m & 1h & 4h still not low enough, 15m & 1h & 4h downtrend, 1h & 4h still high
      & (
        (_cmp("RSI_3_15m", ">", 45.0))
        | (_cmp_cached_25)
        | (_cmp_cached_0)
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp("CMF_20_15m", ">", -0.15))
        | (_cmp("CMF_20_1h", ">", -0.25))
        | (_cmp("CMF_20_4h", ">", -0.35))
        | (_cmp_cached_50)
        | (_cmp_cached_30)
        | (_cmp_cached_47)
      )
      # 15m down move, 15m & 1h & 4h high, 15m & 1h high, 4h & 1d overbought
      & (
        (_cmp("RSI_3_15m", ">", 45.0))
        | (_cmp("RSI_14_15m", "<", 50.0))
        | (_cmp("RSI_14_1h", "<", 60.0))
        | (_cmp_cached_29)
        | (_cmp_cached_61)
        | (_cmp_cached_79)
        | (_cmp_cached_49)
        | (_cmp("ROC_9_1d", "<", 40.0))
      )
      # 15m down move, 15m & 1h & 4h high, 1h & 4h high, 1h & 4h overbought
      & (
        (_cmp("RSI_3_15m", ">", 45.0))
        | (_cmp("RSI_14_15m", "<", 50.0))
        | (_cmp("RSI_14_1h", "<", 70.0))
        | (_cmp_cached_84)
        | (_cmp_cached_31)
        | (_cmp_cached_16)
        | (_cmp("ROC_9_1h", "<", 40.0))
        | (_cmp("ROC_9_4h", "<", 100.0))
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 15m downtrend, 15m & 4h high
      & (
        (_cmp("RSI_3_15m", ">", 55.0))
        | (_cmp_cached_41)
        | (_cmp_cached_18)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp("CMF_20_15m", ">", -0.10))
        | (_cmp_cached_83)
        | (_cmp_cached_56)
        | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 70.0))
      )
      # 15m & 1h down move, 15m & 1h & 4h high, 1h & 4h overbought
      & (
        (_cmp("RSI_3_15m", ">", 55.0))
        | (_cmp("RSI_3_1h", ">", 65.0))
        | (_cmp("RSI_14_15m", "<", 50.0))
        | (_cmp("RSI_14_1h", "<", 60.0))
        | (_cmp_cached_84)
        | (_cmp_cached_40)
        | (_cmp_cached_16)
        | (_cmp("ROC_9_1h", "<", 30.0))
        | (_cmp("ROC_9_4h", "<", 70.0))
      )
      # 1h & 4h down move, 15m high
      & ((_cmp("RSI_3_1h", ">", 3.0)) | (_cmp("RSI_3_4h", ">", 3.0)) | (_cmp_cached_28))
      # 1h & 4h down move, 4h still not low enough
      & ((_cmp("RSI_3_1h", ">", 3.0)) | (_cmp("RSI_3_4h", ">", 3.0)) | (_cmp("AROONU_14_4h", "<", 20.0)))
      # 1h & 4h down move, 15m still not low enough, 4h downtrend
      & ((_cmp("RSI_3_1h", ">", 3.0)) | (_cmp("RSI_3_4h", ">", 5.0)) | (_cmp_cached_0) | (_cmp("CMF_20_4h", ">", -0.30)))
      # 1h & 4h down move, 1h downtrend, 4h still high
      & ((_cmp("RSI_3_1h", ">", 3.0)) | (_cmp_cached_54) | (_cmp("CMF_20_1h", ">", -0.30)) | (_cmp_cached_37))
      # 1h & 4h down move, 1h still not low enough, 4h still high, 1d overbought
      & (
        (_cmp("RSI_3_1h", ">", 3.0))
        | (_cmp_cached_52)
        | (_cmp_cached_5)
        | (_cmp_cached_2)
        | (_cmp_cached_68)
      )
      # 1h & 4h & 1d down move, 1d still not low enough, 1d downtrend
      & (
        (_cmp_cached_82)
        | (_cmp("RSI_3_4h", ">", 5.0))
        | (_cmp("RSI_3_1d", ">", 10.0))
        | (_cmp("AROONU_14_1d", "<", 25.0))
        | (_cmp("ROC_9_1d", ">", -30.0))
      )
      # 1h & 4h down move, 1h & 4h downtrend
      & ((_cmp_cached_82) | (_cmp("RSI_3_4h", ">", 10.0)) | (_cmp("CMF_20_1h", ">", -0.5)) | (_cmp("CMF_20_4h", ">", -0.5)))
      # 1h & 4h down move, 15m & 1h & 4h downtrend, 1h & 4h still high
      & (
        (_cmp_cached_82)
        | (_cmp_cached_54)
        | (_cmp_cached_55)
        | (_cmp_cached_53)
        | (_cmp_cached_71)
        | (_cmp_cached_22)
        | (_cmp_cached_37)
      )
      # 1h & 4h down move, 15m & 1hg downtrend, 4h downtrend
      & (
        (_cmp_cached_82)
        | (_cmp_cached_54)
        | (_cmp("CMF_20_15m", ">", -0.40))
        | (_cmp("CMF_20_1h", ">", -0.40))
        | (_cmp("ROC_9_4h", ">", -20.0))
      )
      # 1h & 4h down move, 1h still high, 4h high, 1d overbought
      & (
        (_cmp_cached_82)
        | (_cmp_cached_33)
        | (_cmp_cached_22)
        | (_cmp_cached_56)
        | (_cmp_cached_51)
      )
      # 1h & 4h down move, 1h & 4h still high, 4h high, 15m & 1h downtrend
      & (
        (_cmp_cached_82)
        | (_cmp_cached_32)
        | (_cmp_cached_75)
        | (_cmp("AROONU_14_4h", "<", 40.0))
        | (_cmp_cached_70)
        | (_cmp("ROC_9_15m", ">", -10.0))
        | (_cmp("ROC_9_1h", ">", -20.0))
      )
      # 1h & 4h down move, 15m & 1h still not low enough, 4h high, 1d overbought
      & (
        (_cmp_cached_82)
        | (_cmp_cached_25)
        | (_cmp_cached_0)
        | (_cmp_cached_5)
        | (_cmp_cached_2)
        | (_cmp_cached_34)
        | (_cmp_cached_58)
      )
      # 1h & 4h down move, 15m & 1h & 4h downtrend, 1h high
      & (
        (_cmp_cached_57)
        | (_cmp_cached_54)
        | (_cmp("CMF_20_15m", ">", -0.0))
        | (_cmp("CMF_20_1h", ">", -0.30))
        | (_cmp("CMF_20_4h", ">", -0.30))
        | (_cmp("AROONU_14_1h", "<", 60.0))
      )
      # 1h & 4h down move, 1h & 4h downtrend, 1h high
      & (
        (_cmp_cached_57)
        | (_cmp_cached_54)
        | (_cmp("CMF_20_1h", ">", -0.40))
        | (_cmp("CMF_20_4h", ">", -0.40))
        | (_cmp("AROONU_14_1h", "<", 60.0))
      )
      # 1h & 4h & 1d down move, 1h & 4h still not low enough, 1h & 4h downtrend, 1h still not low enough
      & (
        (_cmp_cached_48)
        | (_cmp("RSI_3_4h", ">", 15.0))
        | (_cmp("RSI_3_1d", ">", 15.0))
        | (_cmp_cached_43)
        | (_cmp("RSI_14_4h", "<", 20.0))
        | (_cmp_cached_64)
        | (_cmp_cached_71)
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 20.0))
      )
      # 1h & 4h down move, 1h & 4h still not low enough, 15m high, 1h & 4h downtrend
      & (
        (_cmp_cached_48)
        | (_cmp("RSI_3_4h", ">", 15.0))
        | (_cmp("AROONU_14_1h", "<", 20.0))
        | (_cmp("AROONU_14_4h", "<", 20.0))
        | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 80.0))
        | (_cmp("ROC_9_1h", ">", -30.0))
        | (_cmp_cached_78)
      )
      # 1h & 4h down move, 15m & 1h still not low enough, 4h still high, 1h & 4h downtrend
      & (
        (_cmp_cached_48)
        | (_cmp_cached_18)
        | (_cmp_cached_15)
        | (_cmp_cached_43)
        | (_cmp_cached_4)
        | (_cmp_cached_53)
        | (_cmp_cached_62)
        | (_cmp_cached_83)
        | (_cmp_cached_59)
        | (_cmp("ROC_9_1h", ">", -10.0))
      )
      # 1h & 4h down move, 1h still not low enough, 4h downtrend
      & (
        (_cmp_cached_24)
        | (_cmp("RSI_3_4h", ">", 3.0))
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 30.0))
        | (_cmp("ROC_9_4h", ">", -25.0))
      )
      # 1h & 4h down move, 1h & 4h downtrend, 1h high, 4h downtrend
      & (
        (_cmp_cached_24)
        | (_cmp_cached_33)
        | (_cmp_cached_53)
        | (_cmp("CMF_20_4h", ">", -0.25))
        | (_cmp_cached_31)
        | (_cmp_cached_78)
      )
      # 1h & 4h & 1d down move, 1h & 4h still not low enough, 1d high & overbought
      & (
        (_cmp_cached_24)
        | (_cmp_cached_32)
        | (_cmp("RSI_3_1d", ">", 60.0))
        | (_cmp_cached_5)
        | (_cmp_cached_4)
        | (_cmp("AROONU_14_4h", "<", 40.0))
        | (_cmp("AROONU_14_1d", "<", 70.0))
        | (_cmp_cached_58)
      )
      # 1h & 1d down move, 15m & 1h & 4h still not low enough, 15m & 1h downtrend, 1h still high
      & (
        (_cmp_cached_24)
        | (_cmp("RSI_3_1d", ">", 30.0))
        | (_cmp("RSI_14_15m", "<", 10.0))
        | (_cmp_cached_43)
        | (_cmp_cached_12)
        | (_cmp_cached_74)
        | (_cmp("CMF_20_1h", ">", -0.30))
        | (_cmp_cached_59)
      )
      # 1h & 4h & 1d down move, 1h still not low enough, 4h still high, 1d downtrend
      & (
        (_cmp_cached_27)
        | (_cmp_cached_35)
        | (_cmp("RSI_3_1d", ">", 30.0))
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 30.0))
        | (_cmp_cached_47)
        | (_cmp("ROC_9_1d", ">", -30.0))
      )
      # 1h & 4h down move, 1h & 4h still not low enough, 4h still high, 1h & 4h downtrend, 1d overbought
      & (
        (_cmp_cached_27)
        | (_cmp_cached_35)
        | (_cmp_cached_15)
        | (_cmp_cached_43)
        | (_cmp_cached_4)
        | (_cmp("ROC_9_1h", ">", -20.0))
        | (_cmp("ROC_9_4h", ">", -20.0))
        | (_cmp_cached_68)
      )
      # 5m & 15m & 1h & 4h down move, 15m downtrend, 4h high, 1d overbought
      & (
        (_cmp_cached_27)
        | (_cmp_cached_35)
        | (_cmp("CMF_20_15m", ">", -0.5))
        | (_cmp("CMF_20_1h", ">", -0.3))
        | (_cmp("CMF_20_4h", ">", -0.3))
        | (_cmp_cached_22)
      )
      # 1h & 4h down move, 1h & 4h high, 4h overbought
      & (
        (_cmp_cached_27)
        | (_cmp_cached_18)
        | (_cmp_cached_6)
        | (_cmp_cached_29)
        | (_cmp_cached_20)
        | (_cmp_cached_66)
        | (_cmp("ROC_9_4h", "<", 80.0))
      )
      # 1h & 4h & 1d down move, 15m & 1h & 4h still not low enough, 4h still high
      & (
        (_cmp_cached_14)
        | (_cmp_cached_33)
        | (_cmp("RSI_3_1d", ">", 5.0))
        | (_cmp_cached_15)
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 40.0))
      )
      # 1h & 4h down move, 1h & 4h still high, 1h still not low enough, 4h still high, 1h downtrend, 4h & 1d overbought
      & (
        (_cmp_cached_14)
        | (_cmp_cached_39)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp("AROONU_14_1h", "<", 25.0))
        | (_cmp_cached_37)
        | (_cmp("ROC_9_1h", ">", -10.0))
        | (_cmp_cached_38)
        | (_cmp_cached_58)
      )
      # 1h & 4h down move, 1h & 4h still high, 4h high, 1h & 4h overbought
      & (
        (_cmp_cached_14)
        | (_cmp_cached_18)
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp_cached_22)
        | (_cmp_cached_56)
        | (_cmp_cached_67)
        | (_cmp_cached_72)
      )
      # 1h down move, 1h still high, 4h overbought
      & ((_cmp_cached_41) | (_cmp_cached_1) | (_cmp("ROC_9_4h", "<", 300.0)))
      # 1h & 1d down move, 1h & 4h & 1d still high, 1h & 4h high, 4h overbought
      & (
        (_cmp_cached_60)
        | (_cmp("RSI_3_1d", ">", 25.0))
        | (_cmp_cached_6)
        | (_cmp_cached_36)
        | (_cmp("MFI_14_1d", "<", 50.0))
        | (_cmp_cached_40)
        | (_cmp_cached_76)
        | (_cmp_cached_72)
      )
      # 4h down move, 15m & 1h & 4h still not low enough
      & ((_cmp("RSI_3_4h", ">", 3.0)) | (_cmp_cached_15) | (_cmp_cached_43) | (_cmp_cached_12))
      # 4h down move, 1h & 4h downtrend, 1h still not low enough
      & ((_cmp("RSI_3_4h", ">", 3.0)) | (_cmp_cached_53) | (_cmp("CMF_20_4h", ">", -0.25)) | (_cmp_cached_83))
      # 4h down move, 1h & 4h downtrend, 1h & 4h & 1d downtrend
      & (
        (_cmp("RSI_3_4h", ">", 3.0))
        | (_cmp_cached_53)
        | (_cmp("CMF_20_4h", ">", -0.35))
        | (_cmp("CCI_20_change_pct_4h", ">", 0.0))
        | (_cmp("ROC_9_1h", ">", -20.0))
        | (_cmp("ROC_9_4h", ">", -25.0))
        | (_cmp("ROC_9_1d", ">", -25.0))
      )
      # 4h down move, 15m downtrend, 15m still not low enough, 1h high
      & (
        (_cmp("RSI_3_4h", ">", 3.0))
        | (_cmp_cached_55)
        | (_cmp_cached_50)
        | (_cmp_cached_80)
      )
      # 4h down move, 1h & 4h downtrend, 15m high
      & (
        (_cmp("RSI_3_4h", ">", 3.0))
        | (_cmp("CMF_20_1h", ">", -0.25))
        | (_cmp("CMF_20_4h", ">", -0.30))
        | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 70.0))
      )
      # 4h down move, 15m & 1h high
      & ((_cmp("RSI_3_4h", ">", 3.0)) | (_cmp_cached_11) | (_cmp("AROONU_14_1h", "<", 90.0)))
      # 4h down move, 15m high, 4h still high
      & (
        (_cmp("RSI_3_4h", ">", 3.0))
        | (_cmp_cached_11)
        | (_cmp("AROONU_14_4h", "<", 40.0))
        | (_cmp_cached_28)
      )
      # 4h down move, 15m & 1h high, 4h downtrend
      & (
        (_cmp("RSI_3_4h", ">", 3.0))
        | (_cmp_cached_28)
        | (_cmp_cached_30)
        | (_cmp("ROC_9_4h", ">", -20.0))
      )
      # 4h & 1d down move, 15m still not low enough, 4h downtrend
      & (
        (_cmp("RSI_3_4h", ">", 5.0))
        | (_cmp("RSI_3_1d", ">", 5.0))
        | (_cmp_cached_50)
        | (_cmp("ROC_9_4h", ">", -40.0))
      )
      # 4h down move, 15m & 1h & 4h still not low enough, 1h & 4h downtrend, 4h & 15m still not low enough
      & (
        (_cmp("RSI_3_4h", ">", 5.0))
        | (_cmp_cached_15)
        | (_cmp_cached_43)
        | (_cmp("RSI_14_4h", "<", 20.0))
        | (_cmp_cached_53)
        | (_cmp_cached_71)
        | (_cmp("AROONU_14_4h", "<", 30.0))
        | (_cmp_cached_50)
      )
      # 4h down move, 1h & 4h downtrend, 1h still not low enough, 4h high
      & (
        (_cmp("RSI_3_4h", ">", 5.0))
        | (_cmp_cached_64)
        | (_cmp_cached_71)
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 20.0))
        | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 40.0))
      )
      # 4h down mnove, 15m & 1h & 4h downtrend, 15m high, 4h downtrend
      & (
        (_cmp("RSI_3_4h", ">", 10.0))
        | (_cmp_cached_73)
        | (_cmp_cached_64)
        | (_cmp_cached_62)
        | (_cmp_cached_11)
        | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 70.0))
        | (_cmp_cached_78)
      )
      # 4h down move, 15m & 1h & 4h still high, 15m high
      & (
        (_cmp("RSI_3_4h", ">", 10.0))
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp_cached_11)
        | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 70.0))
      )
      # 4h & 1d down move, 15m & 1h still not low enough, 4h still high, 4h downtrend, 1d overbought
      & (
        (_cmp("RSI_3_4h", ">", 15.0))
        | (_cmp("RSI_3_1d", ">", 65.0))
        | (_cmp_cached_15)
        | (_cmp_cached_43)
        | (_cmp_cached_4)
        | (_cmp("ROC_9_4h", ">", -40.0))
        | (_cmp("ROC_9_1d", "<", 200.0))
      )
      # 4h & 1d down move, 1h still high, 4h high, 1d downtrend
      & (
        (_cmp_cached_35)
        | (_cmp("RSI_3_1d", ">", 30.0))
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp_cached_22)
        | (_cmp_cached_16)
        | (_cmp("ROC_9_1d", ">", -40.0))
      )
      # 4h down move, 1h & 4h still not low enough, 15m high, 4h downtrend
      & (
        (_cmp_cached_35)
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_28)
        | (_cmp("ROC_9_4h", ">", -50.0))
      )
      # 4h & 1d down move, 15m & 1h & 4h still not low enough, 4h downtrend, 1h still high, 4h downtrend
      & (
        (_cmp_cached_33)
        | (_cmp("RSI_3_1d", ">", 40.0))
        | (_cmp_cached_15)
        | (_cmp_cached_43)
        | (_cmp("RSI_14_4h", "<", 20.0))
        | (_cmp("CMF_20_4h", ">", -0.25))
        | (_cmp_cached_30)
        | (_cmp("ROC_9_4h", ">", -60.0))
      )
      # 4h down move, 15m & 1h & 4h still high, 15m high, 4h still not low enough, 1d overbought
      & (
        (_cmp_cached_52)
        | (_cmp("RSI_14_15m", "<", 50.0))
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp_cached_11)
        | (_cmp("AROONU_14_4h", "<", 30.0))
        | (_cmp_cached_28)
        | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 30.0))
        | (_cmp_cached_51)
      )
      # 4h down move, 15m high, 15m & 1h & 4h high, 4h & 1d overbought
      & (
        (_cmp_cached_42)
        | (_cmp("AROONU_14_15m", "<", 80.0))
        | (_cmp_cached_28)
        | (_cmp_cached_30)
        | (_cmp_cached_66)
        | (_cmp_cached_38)
        | (_cmp("ROC_9_1d", "<", 30.0))
      )
      # 1d down move, 15m & 1h still not low enough, 4h & 1d downtrend
      & (
        (_cmp("RSI_3_1d", ">", 3.0))
        | (_cmp_cached_15)
        | (_cmp_cached_43)
        | (_cmp_cached_81)
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 30.0))
        | (_cmp_cached_78)
        | (_cmp("ROC_9_1d", ">", -50.0))
      )
      # 1d down move, 1h & 4h still not low enough, 1h still high & overbought, 1d downtrend
      & (
        (_cmp("RSI_3_1d", ">", 3.0))
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp_cached_22)
        | (_cmp_cached_30)
        | (_cmp_cached_67)
        | (_cmp("ROC_9_1d", ">", -30.0))
      )
      # 1d down move, 15m & 1h & 4h still not low enough, 15m still not low enough, 1h high
      & (
        (_cmp("RSI_3_1d", ">", 5.0))
        | (_cmp_cached_0)
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp_cached_63)
        | (_cmp_cached_69)
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 80.0))
      )
      # 1d down move, 15m still not low enough, 1h high, 1d downtrend
      & (
        (_cmp("RSI_3_1d", ">", 5.0))
        | (_cmp_cached_0)
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 80.0))
        | (_cmp("ROC_2_1d", ">", -40.0))
      )
      # 1d down move, 15m high, 1h & 4h downtrend
      & (
        (_cmp("RSI_3_1d", ">", 5.0))
        | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 70.0))
        | (_cmp("ROC_9_1h", ">", -60.0))
        | (_cmp("ROC_9_4h", ">", -60.0))
      )
      # 1d down move, 1h still high, 4h high
      & ((_cmp("RSI_3_1d", ">", 5.0)) | (_cmp_cached_75) | (_cmp_cached_34))
      # 1d down move, 4h high, 1h & 4h downtrend
      & (
        (_cmp("RSI_3_1d", ">", 5.0))
        | (_cmp_cached_70)
        | (_cmp("ROC_9_1h", ">", -10.0))
        | (_cmp("ROC_9_4h", ">", -10.0))
      )
      # 1d down move, 1h high & overbought, 4h & 1d downtrend
      & (
        (_cmp("RSI_3_1d", ">", 10.0))
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 80.0))
        | (_cmp_cached_67)
        | (_cmp("ROC_9_4h", ">", -40.0))
        | (_cmp("ROC_9_1d", ">", -40.0))
      )
      # 1d down move, 1h & 4h still high, 1h & 4h downtrend, 1h & 4h high, 1d downtrend
      & (
        (_cmp("RSI_3_1d", ">", 10.0))
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp("CMF_20_1h", ">", -0.40))
        | (_cmp_cached_62)
        | (_cmp_cached_22)
        | (_cmp_cached_56)
        | (_cmp("ROC_9_1d", ">", -40.0))
      )
      # 15m & 1h & 4h still high, 4h downtrend, 4h overbought
      & (
        (_cmp("RSI_14_15m", "<", 50.0))
        | (_cmp_cached_6)
        | (_cmp_cached_36)
        | (_cmp("CMF_20_4h", ">", -0.2))
        | (_cmp("ROC_9_4h", "<", 250.0))
      )
      # 4h red, 15m & 1h & 4h down move, 1h & 4h still high, 4h high
      & (
        (_cmp("change_pct_4h", ">", -30.0))
        | (_cmp_cached_9)
        | (_cmp_cached_24)
        | (_cmp_cached_33)
        | (_cmp_cached_5)
        | (_cmp_cached_4)
        | (_cmp_cached_34)
      )
      # 4h P&D, 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 1h & 4h high
      & (
        (_cmp("change_pct_4h", ">", -5.0))
        | (df["change_pct_4h"].shift(48) < 5.0)
        | (_cmp_cached_65)
        | (_cmp_cached_19)
        | (_cmp_cached_39)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp_cached_31)
        | (_cmp_cached_16)
      )
      # 4h green with top wick, 15m & 1h down move, 15m still not low enough, 1h & 4h high
      & (
        (_cmp("change_pct_4h", "<", 10.0))
        | (_cmp("top_wick_pct_4h", "<", 10.0))
        | (_cmp_cached_26)
        | (_cmp_cached_19)
        | (_cmp_cached_0)
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp("AROONU_14_1h", "<", 60.0))
        | (_cmp_cached_76)
      )
      # 4h green with top wick, 1h down move, 1h still high, 4h high, 1d overbought
      & (
        (_cmp("change_pct_4h", "<", 10.0))
        | (_cmp("top_wick_pct_4h", "<", 10.0))
        | (_cmp_cached_21)
        | (_cmp_cached_1)
        | (_cmp_cached_36)
        | (_cmp_cached_40)
        | (_cmp_cached_76)
        | (_cmp("ROC_9_1d", "<", 20.0))
      )
      # 4h green with top wick, 15m & 1h down move, 1h still high, 4h high
      & (
        (_cmp("change_pct_4h", "<", 15.0))
        | (_cmp("top_wick_pct_4h", "<", 15.0))
        | (_cmp_cached_9)
        | (_cmp_cached_23)
        | (_cmp_cached_22)
        | (_cmp_cached_16)
      )
      # 4h green with top wick, 15m & 1h down move, 1h & 4h high
      & (
        (_cmp("change_pct_4h", "<", 15.0))
        | (_cmp("top_wick_pct_4h", "<", 10.0))
        | (_cmp_cached_7)
        | (_cmp_cached_19)
        | (_cmp_cached_31)
        | (_cmp_cached_16)
      )
      # 4h green, 15m & 1h down move, 15m still not low enough, 1h & 4h high
      & (
        (_cmp("change_pct_4h", "<", 15.0))
        | (_cmp_cached_8)
        | (_cmp_cached_19)
        | (_cmp_cached_0)
        | (_cmp_cached_6)
        | (_cmp_cached_29)
        | (_cmp_cached_40)
        | (_cmp_cached_16)
      )
      # 1d red, 1h & 4h down move, 1h still high, 4d downtrend
      & (
        (_cmp("change_pct_1d", ">", -40.0))
        | (_cmp_cached_41)
        | (_cmp("RSI_3_4h", ">", 10.0))
        | (_cmp_cached_30)
        | (_cmp("ROC_9_4h", ">", -35.0))
      )
      # 1d P&D, 15m & 4h down move, 15m & 4h still high
      & (
        (_cmp("change_pct_1d", ">", -20.0))
        | (df["change_pct_1d"].shift(288) < 20.0)
        | (_cmp_cached_7)
        | (_cmp_cached_35)
        | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 40.0))
        | (_cmp_cached_47)
      )
      # 1d red, 15m & 1h & 4h down move, 1h still not low enough, 4h & 1d still high
      & (
        (_cmp("change_pct_1d", ">", -20.0))
        | (_cmp_cached_8)
        | (_cmp_cached_27)
        | (_cmp_cached_39)
        | (_cmp("RSI_14_1h", "<", 35.0))
        | (_cmp_cached_4)
        | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 40.0))
        | (_cmp("STOCHRSIk_14_14_3_3_1d", "<", 50.0))
      )
      # 1d red, 1h & 4h & 1d down move, 1h still not low enough, 4h & 1d still high, 1d downtrend
      & (
        (_cmp("change_pct_1d", ">", -20.0))
        | (_cmp_cached_24)
        | (_cmp_cached_39)
        | (_cmp("RSI_3_1d", ">", 50.0))
        | (_cmp_cached_5)
        | (_cmp_cached_4)
        | (_cmp("RSI_14_1d", "<", 40.0))
        | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 40.0))
        | (_cmp("ROC_9_1d", ">", -20.0))
      )
      # 1d red, 15m & 1h & 4h down move, 1d high, 15m & 1h still high
      & (
        (_cmp("change_pct_1d", ">", -20.0))
        | (_cmp_cached_13)
        | (_cmp_cached_41)
        | (_cmp_cached_42)
        | (_cmp("AROONU_14_1d", "<", 85.0))
        | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 40.0))
        | (_cmp_cached_30)
      )
      # 1d P&D, 15m & 1h & 4h down move, 15m & 1h & 4h still high, 15m & 4h still high
      & (
        (_cmp("change_pct_1d", ">", -15.0))
        | (df["change_pct_1d"].shift(288) < 15.0)
        | (_cmp("RSI_3_15m", ">", 50.0))
        | (_cmp_cached_46)
        | (_cmp_cached_39)
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp_cached_17)
        | (_cmp_cached_37)
      )
      # 1d P&D, 15m & 1h & 4h & 1d down move, 4h still not low enough
      & (
        (_cmp("change_pct_1d", ">", -10.0))
        | (df["change_pct_1d"].shift(288) < 10.0)
        | (_cmp_cached_9)
        | (_cmp_cached_27)
        | (_cmp("RSI_3_4h", ">", 10.0))
        | (_cmp("RSI_3_1d", ">", 40.0))
        | (_cmp_cached_12)
      )
      # 1d P&D, 15m & 1h down move, 1h still not low enough, 4h still high, 15m downtrend, 1h still high
      & (
        (_cmp("change_pct_1d", ">", -10.0))
        | (df["change_pct_1d"].shift(288) < 10.0)
        | (_cmp_cached_8)
        | (_cmp_cached_24)
        | (_cmp_cached_5)
        | (_cmp_cached_4)
        | (_cmp_cached_74)
        | (_cmp_cached_22)
      )
      # 1d P&D, 15m down move, 1h high
      & (
        (_cmp("change_pct_1d", ">", -10.0))
        | (df["change_pct_1d"].shift(288) < 20.0)
        | (df["top_wick_pct_1d"].shift(288) < 20.0)
        | (_cmp_cached_45)
        | (_cmp_cached_40)
      )
      # 1d P&D, 15m & 1h & 4h down move, 15m & 1h still not low enough, 4h still high, 1d overbought
      & (
        (_cmp("change_pct_1d", ">", -10.0))
        | (df["change_pct_1d"].shift(288) < 20.0)
        | (_cmp_cached_7)
        | (_cmp_cached_24)
        | (_cmp_cached_39)
        | (_cmp_cached_15)
        | (_cmp_cached_5)
        | (_cmp_cached_2)
        | (_cmp("ROC_9_1d", "<", 25.0))
      )
      # 1d P&D, 15m & 1h & 4h down move, 15m & 1h still not low enough, 4h still high, 1h & 4h downtrend, 1d overbought
      & (
        (_cmp("change_pct_1d", ">", -10.0))
        | (df["change_pct_1d"].shift(288) < 50.0)
        | (_cmp_cached_7)
        | (_cmp_cached_19)
        | (_cmp_cached_32)
        | (_cmp_cached_0)
        | (_cmp_cached_5)
        | (_cmp_cached_4)
        | (_cmp("ROC_9_1h", ">", -10.0))
        | (_cmp("ROC_9_4h", ">", -10.0))
        | (_cmp_cached_58)
      )
      # 1d red with top wick, 15m & 1h down move, 1h downtrend, 1h high
      & (
        (_cmp("change_pct_1d", ">", -10.0))
        | (_cmp("top_wick_pct_1d", "<", 10.0))
        | (_cmp_cached_9)
        | (_cmp_cached_27)
        | (_cmp("CMF_20_1h", ">", -0.2))
        | (_cmp_cached_40)
        | (_cmp_cached_59)
      )
      # 1d P&D, 15m & 1h down move, 15m still not low enough, 1h & 4h still high, 1d overbought
      & (
        (_cmp("change_pct_1d", ">", -5.0))
        | (df["change_pct_1d"].shift(288) < 10.0)
        | (_cmp_cached_7)
        | (_cmp_cached_21)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_58)
      )
      # 1d P&D, 15m & 1h & 4h down move, 1h & 4h still not low enough, 1h & 4h downtrend, 1d overbought
      & (
        (_cmp("change_pct_1d", ">", -5.0))
        | (df["change_pct_1d"].shift(288) < 10.0)
        | (_cmp_cached_10)
        | (_cmp_cached_14)
        | (_cmp_cached_33)
        | (_cmp_cached_83)
        | (_cmp("AROONU_14_4h", "<", 30.0))
        | (_cmp("ROC_9_1h", ">", -25.0))
        | (_cmp("ROC_9_4h", ">", -25.0))
        | (_cmp_cached_51)
      )
      # 1d red, 15m & 1h & 4h down move, 1h & 4h still not low enough, 1d high, 4h downtrend, 1d overbought
      & (
        (_cmp("change_pct_1d", ">", -5.0))
        | (_cmp_cached_7)
        | (_cmp_cached_19)
        | (_cmp_cached_32)
        | (_cmp_cached_5)
        | (_cmp_cached_4)
        | (_cmp("AROONU_14_1d", "<", 85.0))
        | (_cmp_cached_78)
        | (_cmp("ROC_9_1d", "<", 20.0))
      )
      # 1d green with top wick, 15m & 1h & 1d down move, 1h still not low enough, 4h still high, 1d overbought
      & (
        (_cmp("change_pct_1d", "<", 10.0))
        | (_cmp("top_wick_pct_1d", "<", 10.0))
        | (_cmp_cached_8)
        | (_cmp_cached_14)
        | (_cmp("RSI_3_1d", ">", 65.0))
        | (_cmp_cached_5)
        | (_cmp_cached_2)
        | (_cmp_cached_47)
        | (_cmp("ROC_9_1d", "<", 20.0))
      )
      # 1d green with top wick, 15m & 1h & 4h down move, 1h & 4h still high
      & (
        (_cmp("change_pct_1d", "<", 10.0))
        | (_cmp("top_wick_pct_1d", "<", 10.0))
        | (_cmp_cached_9)
        | (_cmp_cached_27)
        | (_cmp_cached_44)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_83)
        | (_cmp("AROONU_14_4h", "<", 60.0))
      )
      # 1d green with top wick, 15m down move, 1h & 4h high, 1d overbought
      & (
        (_cmp("change_pct_1d", "<", 10.0))
        | (_cmp("top_wick_pct_1d", "<", 10.0))
        | (_cmp_cached_9)
        | (_cmp("RSI_14_1h", "<", 70.0))
        | (_cmp_cached_84)
        | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 90.0))
        | (_cmp("ROC_9_1d", "<", 40.0))
      )
      # 1d green with top wick, 15m down move, 15m & 1h still high, 4h & 1d high, 4h overbought
      & (
        (_cmp("change_pct_1d", "<", 10.0))
        | (_cmp("top_wick_pct_1d", "<", 10.0))
        | (_cmp_cached_9)
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp("RSI_14_4h", "<", 75.0))
        | (_cmp_cached_20)
        | (_cmp("AROONU_14_1d", "<", 90.0))
        | (_cmp_cached_72)
      )
      # 1d green with top wick, 15m & 1h & 4h down move, 15m still not low enough, 1h still high, 4h high
      & (
        (_cmp("change_pct_1d", "<", 10.0))
        | (_cmp("top_wick_pct_1d", "<", 10.0))
        | (_cmp_cached_8)
        | (_cmp_cached_27)
        | (_cmp_cached_44)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_36)
        | (_cmp_cached_63)
        | (_cmp("AROONU_14_4h", "<", 60.0))
      )
      # 1d green with top wick, 15m down move, 15m & 1h still high, 4h high & overbought
      & (
        (_cmp("change_pct_1d", "<", 10.0))
        | (_cmp("top_wick_pct_1d", "<", 10.0))
        | (_cmp_cached_8)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_84)
        | (_cmp_cached_34)
        | (_cmp("ROC_9_4h", "<", 80.0))
      )
      # 1d green with top wick, 1h & 4h down move, 1h & 4h still high
      & (
        (_cmp("change_pct_1d", "<", 10.0))
        | (_cmp("top_wick_pct_1d", "<", 10.0))
        | (_cmp_cached_41)
        | (_cmp_cached_42)
        | (_cmp_cached_22)
        | (_cmp_cached_37)
      )
      # 1d green with top wick, 15m & 1h down move, 15m & 1h & 4h still high, 4h high & overbought
      & (
        (_cmp("change_pct_1d", "<", 20.0))
        | (_cmp("top_wick_pct_1d", "<", 20.0))
        | (_cmp_cached_8)
        | (_cmp_cached_21)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_2)
        | (_cmp_cached_34)
        | (_cmp_cached_38)
      )
      # 1d green with top wick, 1h & 4h down move, 1h still not low enough, 4h still high, 4h & 1d overbought
      & (
        (_cmp("change_pct_1d", "<", 20.0))
        | (_cmp("top_wick_pct_1d", "<", 20.0))
        | (_cmp_cached_21)
        | (_cmp_cached_39)
        | (_cmp_cached_5)
        | (_cmp_cached_2)
        | (_cmp_cached_37)
        | (_cmp_cached_49)
        | (_cmp_cached_51)
      )
      # 1d green with top wick, 15m down move, 15m & 1h & 4h still high, 4h & 1d overbought
      & (
        (_cmp("change_pct_1d", "<", 25.0))
        | (_cmp("top_wick_pct_1d", "<", 25.0))
        | (_cmp_cached_65)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_36)
        | (_cmp_cached_81)
        | (_cmp_cached_30)
        | (_cmp_cached_47)
        | (_cmp_cached_38)
        | (_cmp_cached_51)
      )
      # 1d green with top wick, 15m & 1h & 4h down move, 15m still not low enough, 4h high, 1d overbought
      & (
        (_cmp("change_pct_1d", "<", 30.0))
        | (_cmp("top_wick_pct_1d", "<", 10.0))
        | (_cmp_cached_13)
        | (_cmp_cached_14)
        | (_cmp("RSI_3_4h", ">", 70.0))
        | (_cmp_cached_36)
        | (_cmp("AROONU_14_15m", "<", 25.0))
        | (_cmp_cached_34)
        | (_cmp("ROC_9_1d", "<", 40.0))
      )
      # 1d green with top wick, 15m & 1h & 4h down move, 1h still not low enough, 4h still high, 1d overbought
      & (
        (_cmp("change_pct_1d", "<", 30.0))
        | (_cmp("top_wick_pct_1d", "<", 20.0))
        | (_cmp_cached_9)
        | (_cmp_cached_19)
        | (_cmp_cached_32)
        | (_cmp("AROONU_14_1h", "<", 20.0))
        | (_cmp_cached_37)
        | (_cmp_cached_58)
      )
      # 1d green with top wick, 15m down move, 15m & 1h still high, 4h high & overbought
      & (
        (_cmp("change_pct_1d", "<", 30.0))
        | (_cmp("top_wick_pct_1d", "<", 20.0))
        | (_cmp_cached_45)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_84)
        | (_cmp_cached_20)
        | (_cmp("ROC_9_4h", "<", 50.0))
      )
      # 1d green with top wick, 1h down move, 1h still high, 4h high & overbought, 1d overbought
      & (
        (_cmp("change_pct_1d", "<", 30.0))
        | (_cmp("top_wick_pct_1d", "<", 20.0))
        | (_cmp_cached_46)
        | (_cmp_cached_1)
        | (_cmp_cached_36)
        | (_cmp_cached_34)
        | (_cmp_cached_77)
        | (_cmp_cached_51)
      )
      # 1d green with top wick, 15m & 1h down move, 1h & 4h still high, 4h overbought
      & (
        (_cmp("change_pct_1d", "<", 30.0))
        | (_cmp("top_wick_pct_1d", "<", 30.0))
        | (_cmp_cached_10)
        | (_cmp_cached_27)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp_cached_20)
        | (_cmp("ROC_9_4h", "<", 30.0))
      )
      # 1d green with top wick, 15m & 4h down move, 15m & 1h still high, 1d overbought
      & (
        (_cmp("change_pct_1d", "<", 30.0))
        | (_cmp("top_wick_pct_1d", "<", 30.0))
        | (_cmp("RSI_3_15m", ">", 50.0))
        | (_cmp_cached_18)
        | (_cmp_cached_17)
        | (_cmp_cached_30)
        | (_cmp_cached_58)
      )
      # 1d green, 15m & 4h down move, 4h still high, 4h & 1d overbought
      & (
        (_cmp("change_pct_1d", "<", 50.0))
        | (_cmp_cached_8)
        | (_cmp_cached_35)
        | (_cmp_cached_2)
        | (_cmp_cached_77)
        | (_cmp_cached_58)
      )
      # 1d green with top wick, 15m & 1h & 4h down move, 1h & 4h still high, 4h high
      & (
        (_cmp("change_pct_1d", "<", 50.0))
        | (_cmp("top_wick_pct_1d", "<", 50.0))
        | (_cmp_cached_9)
        | (_cmp_cached_24)
        | (_cmp_cached_33)
        | (_cmp_cached_5)
        | (_cmp_cached_4)
        | (_cmp_cached_34)
      )
      # 1d green with top wick, 1d down move, 4h still high & overbought
      & (
        (_cmp("change_pct_1d", "<", 50.0))
        | (_cmp("top_wick_pct_1d", "<", 50.0))
        | (_cmp_cached_21)
        | (_cmp_cached_2)
        | (_cmp_cached_37)
        | (_cmp("ROC_9_4h", "<", 50.0))
      )
      # 1d green with top wick, 4h down move, 4h still high, 1d overbought
      & (
        (_cmp("change_pct_1d", "<", 50.0))
        | (_cmp("top_wick_pct_1d", "<", 50.0))
        | (_cmp_cached_32)
        | (_cmp_cached_4)
        | (_cmp("ROC_9_1d", "<", 200.0))
      )
      # 1d green, 15m & 4h down move, 15m & 1h & 4h still high, 15m high, 4h & 1d overbought
      & (
        (_cmp("change_pct_1d", "<", 50.0))
        | (_cmp("RSI_3_15m", ">", 50.0))
        | (_cmp_cached_39)
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_11)
        | (_cmp("ROC_9_4h", "<", 30.0))
        | (_cmp("ROC_9_1d", "<", 200.0))
      )
      # 4h top wick, 15m down move, 15m still not low enough, 1h & 4h still high, 4h overbought
      & (
        (_cmp("top_wick_pct_4h", "<", 20.0))
        | (_cmp_cached_10)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_30)
        | (_cmp_cached_47)
        | (_cmp("ROC_9_4h", "<", 50.0))
      )
      # 4h top wick, 15m & 1h down move, 15m & 1h still high, 1h & 4h high
      & (
        (_cmp("top_wick_pct_4h", "<", 20.0))
        | (_cmp_cached_65)
        | (_cmp_cached_41)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_36)
        | (_cmp("AROONU_14_15m", "<", 40.0))
        | (_cmp_cached_69)
        | (_cmp_cached_16)
      )
      # 1d top wick, 1h & 4h down move, 15m downtrend, 4h still high, 1d overbought
      & (
        (_cmp("top_wick_pct_1d", "<", 20.0))
        | (_cmp_cached_57)
        | (_cmp_cached_25)
        | (_cmp("CMF_20_15m", ">", -0.2))
        | (_cmp_cached_37)
        | (_cmp_cached_68)
      )
      # 1d top wick, 4h down move, 4h still high, 1d overbought
      & (
        (_cmp("top_wick_pct_1d", "<", 25.0))
        | (_cmp_cached_35)
        | (_cmp("RSI_14_4h", "<", 45.0))
        | (_cmp("AROONU_14_4h", "<", 40.0))
        | (_cmp("ROC_9_1d", "<", 200.0))
      )
      # 1d top wick, 15m & 1h & 4h down move, 15m & 1h downtrend, 4h still high
      & (
        (_cmp("top_wick_pct_1d", "<", 25.0))
        | (_cmp_cached_9)
        | (_cmp_cached_14)
        | (_cmp_cached_39)
        | (_cmp_cached_73)
        | (_cmp("CMF_20_1h", ">", -0.25))
        | (_cmp_cached_37)
      )
      # 1d top wick, 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high
      & (
        (_cmp("top_wick_pct_1d", "<", 25.0))
        | (_cmp_cached_13)
        | (_cmp_cached_60)
        | (_cmp_cached_18)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp_cached_63)
        | (_cmp_cached_37)
        | (_cmp_cached_50)
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 20.0))
      )
      # 1d top wick, 15m down move, 15m stil high, 1h & 4h high, 4h overbought
      & (
        (_cmp("top_wick_pct_1d", "<", 25.0))
        | (_cmp_cached_45)
        | (_cmp_cached_3)
        | (_cmp_cached_6)
        | (_cmp_cached_84)
        | (_cmp_cached_31)
        | (_cmp_cached_20)
        | (_cmp("ROC_9_4h", "<", 50.0))
      )
      # 1d top wick, 15m & 1h & 4h down move, 15m & 1h & 4h still high
      & (
        (_cmp("top_wick_pct_1d", "<", 80.0))
        | (_cmp_cached_65)
        | (_cmp("RSI_3_1h", ">", 65.0))
        | (_cmp_cached_44)
        | (_cmp_cached_3)
        | (_cmp_cached_1)
        | (_cmp_cached_4)
        | (_cmp_cached_37)
      )
      # pump, drop but not yet near the previous lows, 15m & 1h & 4h & 1d down move, 1d overbought
      & (
        _range_lt("high_max_6_1d", "low_min_6_1d", 1.5)
        | _gt_mul("close", "high_max_6_4h", 0.70)
        | (df["close"] < (df["low_min_6_1d"] * 1.25))
        | (_cmp_cached_8)
        | (_cmp_cached_27)
        | (_cmp_cached_35)
        | (_cmp("RSI_3_1d", ">", 45.0))
        | (_cmp("ROC_9_1d", "<", 20.0))
      )
      # pump, drop in lays days, 1h & 4h down move, 1h & 4h still not low enough, 1d overbought
      & (
        _range_lt("high_max_12_1d", "low_min_12_1d", 3.0)
        | _gt_mul("close", "high_max_24_4h", 0.70)
        | (_cmp_cached_48)
        | (_cmp("RSI_3_1d", ">", 50.0))
        | (_cmp_cached_5)
        | (_cmp_cached_4)
        | (_cmp("ROC_9_1d", "<", 20.0))
      )
      # pump, 15m & 1h & 4h down move, 15m & 1h still not low enough, 4h still high, 1h downtrend, 1h high
      & (
        _range_lt("high_max_12_1d", "low_min_12_1d", 3.0)
        | (_cmp_cached_7)
        | (_cmp_cached_14)
        | (_cmp_cached_32)
        | (_cmp_cached_15)
        | (_cmp_cached_5)
        | (_cmp_cached_4)
        | (_cmp_cached_64)
        | (_cmp_cached_40)
      )
      # pump, drop in last 6 days, 1h & 4h down move, 1h & 4h still not low enough, 4h downtrend, 4h & 1d downtrend
      & (
        _range_lt("high_max_30_1d", "low_min_30_1d", 10.0)
        | _gt_mul("close", "high_max_6_1d", 0.50)
        | (_cmp_cached_19)
        | (_cmp_cached_18)
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp_cached_62)
        | (_cmp("ROC_9_4h", ">", -15.0))
        | (_cmp("ROC_9_1d", ">", -25.0))
      )
      # drop in the last 4 hours, 1h & 4h high
      & (_gt_mul("close", "close_max_48", 0.30) | (_cmp_cached_69) | (_cmp_cached_56))
      # drop in last 12 hours, 14m & 1h & 4h down move, 15m still not low enough, 1h still high, 4h high & overbought
      & (
        _gt_mul("close", "high_max_12_1h", 0.50)
        | (_cmp_cached_7)
        | (_cmp_cached_23)
        | (_cmp_cached_42)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_20)
        | (_cmp_cached_72)
      )
      # drop in last 12 hours, 1h & 4h down move, 1h & 4h downtrend
      & (
        _gt_mul("close", "high_max_12_1h", 0.35)
        | (_cmp_cached_48)
        | (_cmp("RSI_3_4h", ">", 5.0))
        | (_cmp("ROC_9_1h", ">", -50.0))
        | (_cmp("ROC_9_4h", ">", -50.0))
      )
      # drop in last 4 days, 15m & 1h & 4h down move, 15m still not low enough, 1h still high, 4h overbought
      & (
        _gt_mul("close", "high_max_24_4h", 0.40)
        | (_cmp_cached_9)
        | (_cmp_cached_27)
        | (_cmp_cached_39)
        | (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_38)
      )
      # drop in last 4 days, 15m & 1h & 4h & 1d down move, 4h high
      & (
        _gt_mul("close", "high_max_24_4h", 0.40)
        | (_cmp_cached_9)
        | (_cmp_cached_19)
        | (_cmp_cached_18)
        | (_cmp("RSI_3_1d", ">", 10.0))
        | (_cmp_cached_66)
      )
      # drop in last 6 days, 15m & 1h & 4h & 1d down move, 1d high, 4h downtrend
      & (
        _gt_mul("close", "high_max_24_4h", 0.35)
        | (_cmp_cached_26)
        | (_cmp_cached_27)
        | (_cmp_cached_35)
        | (_cmp("RSI_3_1d", ">", 30.0))
        | (_cmp("AROONU_14_1d", "<", 80.0))
        | (_cmp("ROC_9_4h", ">", -40.0))
      )
      # drop in last 4 days, 15m & 1d down move, 15m still not low enough, 1h still high, 1d high, 4h downtrend
      & (
        _gt_mul("close", "high_max_24_4h", 0.35)
        | (_cmp_cached_8)
        | (_cmp("RSI_3_1d", ">", 30.0))
        | (_cmp("AROONU_14_15m", "<", 25.0))
        | (_cmp_cached_75)
        | (_cmp("AROONU_14_1d", "<", 80.0))
        | (_cmp("ROC_9_4h", ">", -50.0))
      )
      # drop in last 4 days, 1h & 5h & 1d down move, 1h still high, 1h & 4h downtrend
      & (
        _gt_mul("close", "high_max_24_4h", 0.25)
        | (_cmp_cached_24)
        | (_cmp_cached_35)
        | (_cmp("RSI_3_1d", ">", 25.0))
        | (_cmp_cached_22)
        | (_cmp("ROC_9_1h", ">", -20.0))
        | (_cmp("ROC_9_4h", ">", -35.0))
      )
      # drop in last 4 days, 1d down move, 1h & 4h downtrend, 15m & 4h downtrend
      & (
        _gt_mul("close", "high_max_24_4h", 0.25)
        | (_cmp("RSI_3_1d", ">", 15.0))
        | (_cmp_cached_53)
        | (_cmp_cached_71)
        | (_cmp("ROC_9_15m", ">", -15.0))
        | (_cmp("ROC_9_4h", ">", -20.0))
      )
      # drop in last 6 days, 15m & 1d down move, 1h still high, 4h high, 4h downtrend
      & (
        _gt_mul("close", "high_max_6_1d", 0.25)
        | (_cmp_cached_8)
        | (_cmp("RSI_3_1d", ">", 15.0))
        | (_cmp_cached_59)
        | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 60.0))
        | (_cmp("ROC_9_4h", ">", -25.0))
      )
      # drop in last 6 days, 15m & 1h down move, 15m & 1h still not low enough, 15m & 1h & 4h & 1d downtrend
      & (
        _gt_mul("close", "high_max_6_1d", 0.25)
        | (_cmp_cached_10)
        | (_cmp_cached_14)
        | (_cmp_cached_0)
        | (_cmp("CMF_20_15m", ">", -0.10))
        | (_cmp_cached_64)
        | (_cmp("CMF_20_4h", ">", -0.40))
        | (_cmp("CMF_20_1d", ">", -0.50))
        | (_cmp_cached_83)
      )
      # drop in last 4 days, 4h & 1d down move, 1h high
      & (
        _gt_mul("close", "high_max_24_4h", 0.15)
        | (_cmp_cached_35)
        | (_cmp("RSI_3_1d", ">", 25.0))
        | (_cmp_cached_80)
      )
      # drop in last 4 days, 1d down move, 1d downtrendm 1h still high, 1d downtrend
      & (
        _gt_mul("close", "high_max_24_4h", 0.15)
        | (_cmp("RSI_3_1d", ">", 20.0))
        | (_cmp("CMF_20_1d", ">", -0.30))
        | (_cmp_cached_22)
        | (_cmp("ROC_2_1d", ">", -40.0))
      )
      # drop in last 6 days, 1d down move, 1h & 4h & 1d downtrend, 1d still high, 4h downtrend
      & (
        _gt_mul("close", "high_max_6_1d", 0.15)
        | (_cmp("RSI_3_1d", ">", 20.0))
        | (_cmp_cached_64)
        | (_cmp("CMF_20_4h", ">", -0.40))
        | (_cmp("CMF_20_1d", ">", -0.50))
        | (_cmp("AROONU_14_1d", "<", 50.0))
        | (_cmp_cached_78)
      )
      # drop in last 12 days. 15m & 1h & 4h & 1d down move, 4h still high, 1d downtrend
      & (
        _gt_mul("close", "high_max_12_1d", 0.25)
        | (_cmp_cached_9)
        | (_cmp_cached_57)
        | (_cmp_cached_52)
        | (_cmp("RSI_3_1d", ">", 35.0))
        | (_cmp_cached_47)
        | (_cmp("ROC_9_1d", ">", -40.0))
      )
      # drop in last 12 days, 15m & 1h down move, 1h still not low enough, 4h high
      & (
        _gt_mul("close", "high_max_12_1d", 0.25)
        | (_cmp_cached_8)
        | (_cmp_cached_14)
        | (_cmp_cached_5)
        | (_cmp_cached_12)
        | (_cmp_cached_59)
        | (_cmp_cached_70)
      )
      # drop in last 20 days, 15m & 1h & 1d down move, 15m still not low enough, 1h high
      & (
        _gt_mul("close", "high_max_20_1d", 0.05)
        | (_cmp_cached_9)
        | (_cmp_cached_27)
        | (_cmp("RSI_3_1d", ">", 25.0))
        | (_cmp_cached_63)
        | (_cmp_cached_31)
      )
      # drop in last 20 days, 1h & 4h & 1d down move, 1h & 4h still not low enough, 1h & 4h & 1d downtrend
      & (
        _gt_mul("close", "high_max_20_1d", 0.01)
        | (_cmp_cached_21)
        | (_cmp_cached_18)
        | (_cmp("RSI_3_1d", ">", 15.0))
        | (_cmp("RSI_14_1h", "<", 15.0))
        | (_cmp("RSI_14_4h", "<", 20.0))
        | (_cmp("CMF_20_1h", ">", -0.0))
        | (_cmp_cached_62)
        | (_cmp("CMF_20_1d", ">", -0.40))
        | (_cmp("CCI_20_1h", "<", -150.0))
        | (_cmp("CCI_20_4h", "<", -200.0))
        | (_cmp("ROC_2_1d", ">", -25.0))
        | (_cmp("ROC_9_1d", ">", -60.0))
      )
      # drop in last 30 days, 15m & 1h down move, 1h still high, 4h high & overbought
      & (
        _gt_mul("close", "high_max_30_1d", 0.10)
        | (_cmp_cached_9)
        | (_cmp_cached_41)
        | (_cmp_cached_75)
        | (_cmp_cached_56)
        | (_cmp("ROC_9_4h", "<", 80.0))
      )
      # drop in last 30 days, 15m down move, 15m & 1h high
      & (
        _gt_mul("close", "high_max_30_1d", 0.05)
        | (_cmp_cached_8)
        | (_cmp_cached_39)
        | (_cmp("AROONU_14_15m", "<", 80.0))
        | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 85.0))
      )
      # drop in last 30 days, 15m & 1h & 4h down move, 15m still not low enough, 1h high
      & (
        _gt_mul("close", "high_max_30_1d", 0.05)
        | (_cmp_cached_10)
        | (_cmp_cached_27)
        | (_cmp_cached_32)
        | (_cmp_cached_50)
        | (_cmp_cached_59)
      )
    )

    df["global_protections_long_pump"] = True

    df["global_protections_long_dump"] = True

    df["protections_long_rebuy"] = True

    if self._test_x7_should_skip_short_protection_calc():
      df["protections_short_global"] = True
      df["global_protections_short_pump"] = True
      df["global_protections_short_dump"] = True
      df["protections_short_rebuy"] = True

      df = self._test_x7_restore_tail_protections(test_x7_full_df, df)

      tok = time.perf_counter()
      log.debug(f"[{metadata['pair']}] Populate indicators took a total of: {tok - tik:0.4f} seconds.")

      return df

    # Global protections Short
    df["protections_short_global"] = (
      # 5m & 15m & 1h & 4h up move, 15m & 1h & 4h still not high enough, 4h still low, 1h uptrend
      (
        (_cmp("RSI_3", "<", 90.0))
        | (_cmp("RSI_3_15m", "<", 75.0))
        | (_cmp("RSI_3_1h", "<", 75.0))
        | (_cmp("RSI_3_4h", "<", 75.0))
        | (_cmp("RSI_14_15m", ">", 90.0))
        | (_cmp("RSI_14_1h", ">", 85.0))
        | (_cmp("RSI_14_4h", ">", 70.0))
        | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 60.0))
        | (_cmp("ROC_9_1h", "<", 15.0))
      )
      # 5m & 15m up move, 15m & 1h & 4h still low, 15m & 1h low, 4h still low
      & (
        (_cmp("RSI_3", "<", 90.0))
        | (_cmp("RSI_3_15m", "<", 75.0))
        | (_cmp("RSI_14_15m", ">", 60.0))
        | (_cmp("RSI_14_1h", ">", 50.0))
        | (_cmp("RSI_14_4h", ">", 40.0))
        | (_cmp("AROONU_14_15m", ">", 20.0))
        | (_cmp("AROONU_14_1h", ">", 20.0))
        | (_cmp("AROONU_14_4h", ">", 40.0))
      )
      # 15m & 1h & 4h up move, 15m & 1h & 4h still not high enough, 1h & 4h still low, 4h low
      & (
        (_cmp("RSI_3_15m", "<", 90.0))
        | (_cmp("RSI_3_1h", "<", 60.0))
        | (_cmp("RSI_3_4h", "<", 60.0))
        | (_cmp("RSI_14_15m", ">", 80.0))
        | (_cmp("RSI_14_1h", ">", 70.0))
        | (_cmp("RSI_14_4h", ">", 70.0))
        | (_cmp("AROONU_14_1h", ">", 60.0))
        | (_cmp("AROONU_14_4h", ">", 60.0))
        | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 40.0))
      )
      # 15m & 1h & 4h up move, 15m still not high enough, 1h & 4h still low, 1h low
      & (
        (_cmp("RSI_3_15m", "<", 90.0))
        | (_cmp("RSI_3_1h", "<", 60.0))
        | (_cmp("RSI_3_4h", "<", 35.0))
        | (_cmp("RSI_14_15m", ">", 80.0))
        | (_cmp("RSI_14_1h", ">", 60.0))
        | (_cmp("RSI_14_4h", ">", 60.0))
        | (_cmp("AROONU_14_1h", ">", 40.0))
      )
      # 15m & 1h & 4h up move, 15m & 1h & 4h still not high enough, 4h uptrend
      & (
        (_cmp("RSI_3_15m", "<", 95.0))
        | (_cmp("RSI_3_1h", "<", 80.0))
        | (_cmp("RSI_3_4h", "<", 80.0))
        | (_cmp("RSI_14_15m", ">", 80.0))
        | (_cmp("RSI_14_1h", ">", 80.0))
        | (_cmp("RSI_14_4h", ">", 80.0))
        | (_cmp("CCI_20_1h", ">", 200.0))
        | (_cmp("CCI_20_4h", ">", 150.0))
        | (_cmp_cached_38)
      )
      # 15m & 1h & 4h up move, 1h & 4h still now high enough, 15m uptrend, 1h still not high enough
      & (
        (_cmp("RSI_3_15m", "<", 95.0))
        | (_cmp("RSI_3_1h", "<", 50.0))
        | (_cmp("RSI_3_4h", "<", 50.0))
        | (_cmp("RSI_14_1h", ">", 70.0))
        | (_cmp("RSI_14_4h", ">", 70.0))
        | (_cmp("CMF_20_15m", "<", 0.20))
        | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 70.0))
      )
      # 15m & 1h & 4h up move, 15m & 1h & 4h still not high enough, 1h & 4h & 1d uptrend
      & (
        (_cmp("RSI_3_15m", "<", 90.0))
        | (_cmp("RSI_3_1h", "<", 90.0))
        | (_cmp("RSI_3_4h", "<", 80.0))
        | (_cmp("RSI_14_15m", ">", 80.0))
        | (_cmp("RSI_14_1h", ">", 80.0))
        | (_cmp("RSI_14_4h", ">", 80.0))
        | (_cmp_cached_67)
        | (_cmp_cached_38)
        | (_cmp_cached_68)
      )
      # 15m & 1h & 4h up move, 15m & 1h & 4h still not high enough, 1h & 4h uptrend
      & (
        (_cmp("RSI_3_15m", "<", 90.0))
        | (_cmp("RSI_3_1h", "<", 80.0))
        | (_cmp("RSI_3_4h", "<", 80.0))
        | (_cmp("RSI_14_15m", ">", 80.0))
        | (_cmp("RSI_14_1h", ">", 80.0))
        | (_cmp("RSI_14_4h", ">", 80.0))
        | (_cmp("CCI_20_1h", ">", 250.0))
        | (_cmp("CCI_20_4h", ">", 200.0))
        | (_cmp_cached_67)
        | (_cmp_cached_77)
      )
      # 15m & 1h & 4h up move, 15m & 1h & 4h still not high enough, 15m uptrend, 4h still low
      & (
        (_cmp("RSI_3_15m", "<", 90.0))
        | (_cmp("RSI_3_1h", "<", 80.0))
        | (_cmp("RSI_3_4h", "<", 80.0))
        | (_cmp("RSI_14_15m", ">", 80.0))
        | (_cmp("RSI_14_1h", ">", 80.0))
        | (_cmp("RSI_14_4h", ">", 70.0))
        | (_cmp("CMF_20_15m", "<", 0.25))
        | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 60.0))
      )
      # 15m & 1h & 4h up move, 15m still not high enough, 1h & 4h still low, 4h still low
      & (
        (_cmp("RSI_3_15m", "<", 90.0))
        | (_cmp("RSI_3_1h", "<", 60.0))
        | (_cmp("RSI_3_4h", "<", 60.0))
        | (_cmp("RSI_14_15m", ">", 80.0))
        | (_cmp("RSI_14_1h", ">", 60.0))
        | (_cmp("RSI_14_4h", ">", 60.0))
        | (_cmp("AROONU_14_4h", ">", 50.0))
      )
      # 15m & 1h & 4h up move, 15m & 1h still not high enough, 1h & 4h uptrend
      & (
        (_cmp("RSI_3_15m", "<", 85.0))
        | (_cmp("RSI_3_1h", "<", 85.0))
        | (_cmp("RSI_3_4h", "<", 85.0))
        | (_cmp("AROONU_14_15m", ">", 70.0))
        | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 80.0))
        | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 80.0))
        | (_cmp_cached_67)
        | (_cmp("ROC_9_4h", "<", 30.0))
      )
      # 15m & 1h & 4h up move, 15m & 1h & 4h still not high enough, 15m & 1h & 4h uptrend
      & (
        (_cmp("RSI_3_15m", "<", 85.0))
        | (_cmp("RSI_3_1h", "<", 85.0))
        | (_cmp("RSI_3_4h", "<", 80.0))
        | (_cmp("RSI_14_15m", ">", 85.0))
        | (_cmp("RSI_14_1h", ">", 80.0))
        | (_cmp("RSI_14_4h", ">", 80.0))
        | (_cmp("CMF_20_15m", "<", 0.20))
        | (_cmp("CMF_20_1h", "<", 0.10))
        | (_cmp("CMF_20_4h", "<", 0.10))
      )
      # 15m & 1h & 4h up move, 1h still low, 4h & 1d uptrend
      & (
        (_cmp("RSI_3_15m", "<", 85.0))
        | (_cmp("RSI_3_1h", "<", 85.0))
        | (_cmp("RSI_3_4h", "<", 70.0))
        | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 50.0))
        | (_cmp("ROC_9_4h", "<", 80.0))
        | (_cmp_cached_58)
      )
      # 15m & 1h & 4h up move, 1h & 4h still not high enough, 4h overbought
      & (
        (_cmp("RSI_3_15m", "<", 85.0))
        | (_cmp("RSI_3_1h", "<", 80.0))
        | (_cmp("RSI_3_4h", "<", 80.0))
        | (_cmp("AROONU_14_4h", ">", 70.0))
        | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 80.0))
        | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 80.0))
        | (_cmp_cached_49)
      )
      # 15m & 1h & 4h up move, 1h still nt high enough, 1h & 4h uptrend
      & (
        (_cmp("RSI_3_15m", "<", 85.0))
        | (_cmp("RSI_3_1h", "<", 70.0))
        | (_cmp("RSI_3_4h", "<", 70.0))
        | (_cmp("AROONU_14_1h", ">", 70.0))
        | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 70.0))
        | (_cmp("ROC_9_1h", "<", 45.0))
        | (_cmp("ROC_9_4h", "<", 45.0))
      )
      # 15m & 1h & 4h up move, 15m & 1h & 4h still not high enough, 1h still low, 1h & 4h uptrend
      & (
        (_cmp("RSI_3_15m", "<", 85.0))
        | (_cmp("RSI_3_1h", "<", 70.0))
        | (_cmp("RSI_3_4h", "<", 70.0))
        | (_cmp("RSI_14_15m", ">", 70.0))
        | (_cmp("RSI_14_1h", ">", 80.0))
        | (_cmp("RSI_14_4h", ">", 80.0))
        | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 60.0))
        | (_cmp("ROC_9_1h", "<", 20.0))
        | (_cmp_cached_77)
      )
      # 15m & 1h & 4h up move, 4h still not high enough, 15m & 1h & 4h uptrend
      & (
        (_cmp("RSI_3_15m", "<", 80.0))
        | (_cmp("RSI_3_1h", "<", 80.0))
        | (_cmp("RSI_3_4h", "<", 80.0))
        | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 75.0))
        | (_cmp("ROC_9_15m", "<", 10.0))
        | (_cmp_cached_67)
        | (_cmp_cached_38)
      )
      # 15m & 1h & 4h up move, 15m & 1h & 4h still not high enough, 4h low, 1h & 4h uptrend
      & (
        (_cmp("RSI_3_15m", "<", 80.0))
        | (_cmp("RSI_3_1h", "<", 80.0))
        | (_cmp("RSI_3_4h", "<", 60.0))
        | (_cmp("RSI_14_15m", ">", 80.0))
        | (_cmp("RSI_14_1h", ">", 80.0))
        | (_cmp("RSI_14_4h", ">", 60.0))
        | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 40.0))
        | (_cmp("ROC_9_1h", "<", 20.0))
        | (_cmp_cached_38)
      )
      # 15m & 1h & 4h up move, 15m & 1h & 4h still not high enough, 4h still low, 15m & 1h & 4h uptrend
      & (
        (_cmp("RSI_3_15m", "<", 80.0))
        | (_cmp("RSI_3_1h", "<", 80.0))
        | (_cmp("RSI_3_4h", "<", 55.0))
        | (_cmp("RSI_14_15m", ">", 80.0))
        | (_cmp("RSI_14_1h", ">", 80.0))
        | (_cmp("RSI_14_4h", ">", 70.0))
        | (_cmp("AROONU_14_4h", ">", 70.0))
        | (_cmp("ROC_9_15m", "<", 10.0))
        | (_cmp_cached_67)
        | (_cmp_cached_38)
      )
      # 15m & 1h & 4h up move, 15m & 1h & 4h still not high enough, 15m uptrend
      & (
        (_cmp("RSI_3_15m", "<", 80.0))
        | (_cmp("RSI_3_1h", "<", 70.0))
        | (_cmp("RSI_3_4h", "<", 70.0))
        | (_cmp("RSI_14_15m", ">", 80.0))
        | (_cmp("RSI_14_1h", ">", 70.0))
        | (_cmp("RSI_14_4h", ">", 70.0))
        | (_cmp("AROONU_14_4h", ">", 70.0))
        | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 90.0))
        | (_cmp("ROC_9_15m", "<", 10.0))
      )
      # 15m & 1h & 4h up move, 15m & 1h & 4h still not high enough, 1h low, 4h overbought
      & (
        (_cmp("RSI_3_15m", "<", 80.0))
        | (_cmp("RSI_3_1h", "<", 70.0))
        | (_cmp("RSI_3_4h", "<", 70.0))
        | (_cmp("RSI_14_15m", ">", 80.0))
        | (_cmp("RSI_14_1h", ">", 80.0))
        | (_cmp("RSI_14_4h", ">", 80.0))
        | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 40.0))
        | (_cmp("ROC_9_4h", "<", 30.0))
      )
      # 15m & 1h & 4h up move, 15m & 1h & 4h still not high enough, 4h low
      & (
        (_cmp("RSI_3_15m", "<", 80.0))
        | (_cmp("RSI_3_1h", "<", 70.0))
        | (_cmp("RSI_3_4h", "<", 35.0))
        | (_cmp("RSI_14_15m", ">", 80.0))
        | (_cmp("RSI_14_1h", ">", 70.0))
        | (_cmp("RSI_14_4h", ">", 60.0))
        | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 30.0))
      )
      # 15m & 1h & 4h up move, 15m & 1h & 4h still not high enough, 4h low, 4h overbought
      & (
        (_cmp("RSI_3_15m", "<", 75.0))
        | (_cmp("RSI_3_1h", "<", 75.0))
        | (_cmp("RSI_3_4h", "<", 70.0))
        | (_cmp("RSI_14_15m", ">", 80.0))
        | (_cmp("RSI_14_1h", ">", 80.0))
        | (_cmp("RSI_14_4h", ">", 70.0))
        | (_cmp("AROONU_14_4h", ">", 30.0))
        | (_cmp_cached_49)
      )
      # 15m & 1h & 4h up move, 15m low, 1h uptrend
      & (
        (_cmp("RSI_3_15m", "<", 70.0))
        | (_cmp("RSI_3_1h", "<", 95.0))
        | (_cmp("RSI_3_4h", "<", 85.0))
        | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 30.0))
        | (_cmp("ROC_9_1h", "<", 25.0))
      )
      # 15m & 1h & 4h up move, 15m & 1h & 4h uptrend, 15m still low, 1h uptrend
      & (
        (_cmp("RSI_3_15m", "<", 70.0))
        | (_cmp("RSI_3_1h", "<", 70.0))
        | (_cmp("RSI_3_4h", "<", 70.0))
        | (_cmp("CMF_20_15m", "<", 0.20))
        | (_cmp("CMF_20_1h", "<", 0.20))
        | (_cmp("CMF_20_4h", "<", 0.20))
        | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 50.0))
        | (_cmp("ROC_9_1h", "<", 50.0))
      )
      # 15m & 1h & 4h up move, 15m & 1h & 4h still not high enough, 4h uptrend
      & (
        (_cmp("RSI_3_15m", "<", 70.0))
        | (_cmp("RSI_3_1h", "<", 60.0))
        | (_cmp("RSI_3_4h", "<", 60.0))
        | (_cmp("RSI_14_15m", ">", 70.0))
        | (_cmp("RSI_14_1h", ">", 70.0))
        | (_cmp("RSI_14_4h", ">", 70.0))
        | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 70.0))
        | (_cmp("ROC_9_4h", "<", 50.0))
      )
      # 1h & 4h up move, 1d still low, 15m & 4h still not high enough
      & (
        (_cmp("RSI_3_1h", "<", 95.0))
        | (_cmp("RSI_3_4h", "<", 80.0))
        | (_cmp("RSI_14_1d", ">", 50.0))
        | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 70.0))
        | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 70.0))
      )
      # 1h & 4h up move, 1d still low, 1h & 4h & 1d uptrend
      & (
        (_cmp("RSI_3_1h", "<", 90.0))
        | (_cmp("RSI_3_4h", "<", 90.0))
        | (_cmp("RSI_14_1d", ">", 50.0))
        | (_cmp("ROC_9_1h", "<", 20.0))
        | (_cmp_cached_38)
        | (_cmp("ROC_9_1d", "<", 20.0))
      )
      # 4h up move, 15m & 1h & 4h still not high enough, 1d still low, 4h still not high enough, 1d still low
      & (
        (_cmp("RSI_3_4h", "<", 90.0))
        | (_cmp("RSI_14_15m", ">", 80.0))
        | (_cmp("RSI_14_1h", ">", 80.0))
        | (_cmp("RSI_14_4h", ">", 80.0))
        | (_cmp("RSI_14_1d", ">", 50.0))
        | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 80.0))
        | (_cmp("STOCHRSIk_14_14_3_3_1d", ">", 50.0))
      )
      # 4h up move, 15m & 1h & 4h still not high enough, 15m low, 15m & 1h & 4h uptrend
      & (
        (_cmp("RSI_3_4h", "<", 90.0))
        | (_cmp("RSI_14_15m", ">", 80.0))
        | (_cmp("RSI_14_1h", ">", 80.0))
        | (_cmp("RSI_14_4h", ">", 80.0))
        | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 40.0))
        | (_cmp("ROC_9_15m", "<", 20.0))
        | (_cmp("ROC_9_1h", "<", 15.0))
        | (_cmp("ROC_9_4h", "<", 15.0))
      )
      # 4h up move, 15m & 1h & 4h still not high enough, 1h still low, 1h & 4h overbought
      & (
        (_cmp("RSI_3_4h", "<", 90.0))
        | (_cmp("RSI_14_15m", ">", 80.0))
        | (_cmp("RSI_14_1h", ">", 80.0))
        | (_cmp("RSI_14_4h", ">", 90.0))
        | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 60.0))
        | (_cmp("ROC_9_1h", "<", 20.0))
        | (_cmp("ROC_9_4h", "<", 60.0))
      )
    )

    df["global_protections_short_pump"] = (
      # 15m & 1h & 4h & 1d up move, 15m & 1h & 4h still not high enough, 1d still not high enough & uptrend
      (
        (_cmp("RSI_3_15m", "<", 40.0))
        | (_cmp("RSI_3_1h", "<", 40.0))
        | (_cmp("RSI_3_4h", "<", 85.0))
        | (_cmp("RSI_3_1d", "<", 85.0))
        | (_cmp("RSI_14_15m", ">", 70.0))
        | (_cmp("CCI_20_15m", ">", 350.0))
        | (_cmp("RSI_14_1h", ">", 75.0))
        | (_cmp("CCI_20_1h", ">", 250.0))
        | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 50.0))
        | (_cmp("RSI_14_4h", ">", 95.0))
        | (_cmp("AROOND_14_4h", "<", 50.0))
        | (_cmp("CCI_20_4h", ">", 250.0))
        | (_cmp("RSI_14_1d", ">", 60.0))
        | (_cmp("AROOND_14_1d", "<", 75.0))
        | (_cmp("STOCHRSIk_14_14_3_3_1d", ">", 70.0))
        | (_cmp("ROC_9_1d", "<", 40.0))
      )
      # 15m & 1h & 4h & 1d up move, 15m & 1h & 4h still not high enough, 1d still not high enough & uptrend
      & (
        (_cmp("RSI_3_15m", "<", 60.0))
        | (_cmp("RSI_3_1h", "<", 60.0))
        | (_cmp("RSI_3_4h", "<", 80.0))
        | (_cmp("RSI_3_1d", "<", 90.0))
        | (_cmp("RSI_14_15m", ">", 90.0))
        | (_cmp("CCI_20_15m", ">", 350.0))
        | (_cmp("RSI_14_1h", ">", 90.0))
        | (_cmp("CCI_20_1h", ">", 300.0))
        | (_cmp("RSI_14_4h", ">", 80.0))
        | (_cmp("CCI_20_4h", ">", 200.0))
        | (_cmp("RSI_14_1d", ">", 95.0))
        | (_cmp_cached_68)
      )
      # 1d green, 15m & 1h & 4h & 1d up move, 4h & 1d still not high enough & uptrend
      & (
        (_cmp("RSI_3_15m", "<", 60.0))
        | (_cmp("RSI_3_1h", "<", 70.0))
        | (_cmp("RSI_3_4h", "<", 70.0))
        | (_cmp("RSI_3_1d", "<", 80.0))
        | (_cmp("RSI_14_4h", ">", 70.0))
        | (_cmp("WILLR_14_4h", ">", -10.0))
        | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 80.0))
        | (_cmp_cached_77)
        | (_cmp("RSI_14_1d", ">", 80.0))
        | (_cmp_cached_58)
      )
      # 15m & 1h & 1d up move, 15m & 1h & 4h still not high enough, 1d still not high enough & uptrend
      & (
        (_cmp("RSI_3_15m", "<", 65.0))
        | (_cmp("RSI_3_1h", "<", 70.0))
        | (_cmp("RSI_3_1d", "<", 60.0))
        | (_cmp("RSI_14_15m", ">", 90.0))
        | (_cmp("CMF_20_15m", ">", 0.40))
        | (_cmp("WILLR_14_15m", ">", -10.0))
        | (_cmp("CCI_20_15m", ">", 450.0))
        | (_cmp("STOCHk_14_3_3_15m", ">", 90.0))
        | (_cmp("RSI_14_1h", ">", 90.0))
        | (_cmp("CMF_20_1h", ">", 0.20))
        | (_cmp("WILLR_14_1h", ">", -5.0))
        | (_cmp("CCI_20_1h", ">", 250.0))
        | (_cmp("RSI_14_4h", ">", 90.0))
        | (_cmp("CMF_20_4h", ">", 0.10))
        | (_cmp("CCI_20_4h", ">", 250.0))
        | (_cmp("RSI_14_1d", ">", 90.0))
        | (_cmp("ROC_9_1d", "<", 25.0))
      )
      # 15m & 1h & 4h & 1d up move, 15m & 1h & 4h & 1d still not high enough, 1d uptrend
      & (
        (_cmp("RSI_3_15m", "<", 70.0))
        | (_cmp("RSI_3_1h", "<", 80.0))
        | (_cmp("RSI_3_4h", "<", 80.0))
        | (_cmp("RSI_3_1d", "<", 80.0))
        | (_cmp("MFI_14_15m", ">", 90.0))
        | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 90.0))
        | (_cmp("MFI_14_1h", ">", 90.0))
        | (_cmp("MFI_14_4h", ">", 80.0))
        | (_cmp("WILLR_14_4h", ">", -5.0))
        | (_cmp("AROOND_14_4h", "<", 50.0))
        | (_cmp("ROC_9_1d", "<", 40.0))
      )
      # 15m & 1h up move, 15m & 1h & 4h still not high enough, 1d still not high enough & uptrend
      & (
        (_cmp("RSI_3_15m", "<", 70.0))
        | (_cmp("RSI_3_1h", "<", 85.0))
        | (_cmp("MFI_14_15m", ">", 90.0))
        | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 80.0))
        | (_cmp("RSI_14_1h", ">", 80.0))
        | (_cmp("MFI_14_1h", ">", 80.0))
        | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 70.0))
        | (_cmp("RSI_14_4h", ">", 80.0))
        | (_cmp("RSI_14_1d", ">", 80.0))
        | (_cmp("ROC_9_1d", "<", 40.0))
      )
      # 15m & 1h & 4h & 1d up move, 15m & 1h still not high enough, 4h & 1d stil not high enough & uptrend
      & (
        (_cmp("RSI_3_15m", "<", 80.0))
        | (_cmp("RSI_3_1h", "<", 80.0))
        | (_cmp("RSI_3_4h", "<", 80.0))
        | (_cmp("RSI_3_1d", "<", 95.0))
        | (_cmp("RSI_14_15m", ">", 85.0))
        | (_cmp("CCI_20_15m", ">", 250.0))
        | (_cmp("RSI_14_1h", ">", 85.0))
        | (_cmp("CCI_20_1h", ">", 250.0))
        | (_cmp("CCI_20_change_pct_1h", "<", -0.0))
        | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 90.0))
        | (_cmp("RSI_14_4h", ">", 85.0))
        | (_cmp("CCI_20_4h", ">", 250.0))
        | (_cmp("CCI_20_change_pct_4h", "<", -0.0))
        | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 90.0))
        | (_cmp("ROC_9_4h", "<", 30.0))
        | (_cmp("RSI_14_1d", ">", 90.0))
        | (_cmp("WILLR_14_1d", ">", -10.0))
        | (_cmp_cached_51)
      )
      # 15m & 1h & 4h up move, 15m & 1h still not high enough, 4h still not high enough & uptrend
      & (
        (_cmp("RSI_3_15m", "<", 80.0))
        | (_cmp("RSI_3_1h", "<", 80.0))
        | (_cmp("RSI_3_4h", "<", 90.0))
        | (_cmp("RSI_14_15m", ">", 90.0))
        | (_cmp("CCI_20_15m", ">", 400.0))
        | (_cmp("RSI_14_1h", ">", 90.0))
        | (_cmp("CCI_20_1h", ">", 400.0))
        | (_cmp("CCI_20_4h", ">", 400.0))
        | (_cmp("ROC_9_4h", "<", 200.0))
      )
      # 15m & 1h up move, 15m & 1h & 4h still not high enough, 1d still not high enough & uptrend
      & (
        (_cmp("RSI_3_15m", "<", 80.0))
        | (_cmp("RSI_3_1h", "<", 90.0))
        | (_cmp("RSI_14_15m", ">", 85.0))
        | (_cmp("CCI_20_15m", ">", 250.0))
        | (_cmp("RSI_14_1h", ">", 75.0))
        | (_cmp("AROOND_14_1h", "<", 50.0))
        | (_cmp("CCI_20_1h", ">", 350.0))
        | (_cmp("CCI_20_change_pct_1h", "<", -0.0))
        | (_cmp("RSI_14_4h", ">", 85.0))
        | (_cmp("CCI_20_4h", ">", 150.0))
        | (_cmp("CCI_20_change_pct_4h", "<", -0.0))
        | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 70.0))
        | (_cmp("RSI_14_1d", ">", 85.0))
        | (_cmp_cached_51)
      )
      # 15m & 1h & 4h & 1d up move, 15m & 1h & 4h & 1d still not high enough
      & (
        (_cmp("RSI_3_15m", "<", 80.0))
        | (_cmp("RSI_3_1h", "<", 90.0))
        | (_cmp("RSI_3_4h", "<", 70.0))
        | (_cmp("RSI_3_1d", "<", 70.0))
        | (_cmp("RSI_14_15m", ">", 85.0))
        | (_cmp("RSI_14_1h", ">", 85.0))
        | (_cmp("CCI_20_1h", ">", 250.0))
        | (_cmp("CCI_20_change_pct_1h", "<", -0.0))
        | (_cmp("RSI_14_4h", ">", 70.0))
        | (_cmp("AROOND_14_4h", "<", 75.0))
        | (_cmp("CCI_20_4h", ">", 200.0))
        | (_cmp("CCI_20_change_pct_4h", "<", -0.0))
        | (_cmp("STOCHk_14_3_3_4h", ">", 70.0))
        | (_cmp("RSI_14_1d", ">", 70.0))
      )
      # 15m & 1h & 4h & 1d up move, 1h still not high enough, 1d still low, 4h & 1d uptrend
      & (
        (_cmp("RSI_3_15m", "<", 80.0))
        | (_cmp("RSI_3_1h", "<", 85.0))
        | (_cmp("RSI_3_4h", "<", 90.0))
        | (_cmp("RSI_3_1d", "<", 95.0))
        | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 60.0))
        | (_cmp("AROOND_14_1d", "<", 50.0))
        | (_cmp("ROC_9_4h", "<", 100.0))
        | (_cmp_cached_58)
      )
      # 15m & 1h & 4h & 1d up move, 15m & 1h still not high enough, 4h & 1d still not high enough & uptrend
      & (
        (_cmp("RSI_3_15m", "<", 80.0))
        | (_cmp("RSI_3_1h", "<", 80.0))
        | (_cmp("RSI_3_4h", "<", 90.0))
        | (_cmp("RSI_3_1d", "<", 95.0))
        | (_cmp("RSI_14_15m", ">", 85.0))
        | (_cmp("STOCHk_14_3_3_15m", ">", 90.0))
        | (_cmp("RSI_14_1h", ">", 90.0))
        | (_cmp("STOCHk_14_3_3_1h", ">", 90.0))
        | (_cmp("RSI_14_4h", ">", 95.0))
        | (_cmp("STOCHk_14_3_3_4h", ">", 90.0))
        | (_cmp("ROC_9_4h", "<", 50.0))
        | (_cmp("RSI_14_1d", ">", 95.0))
        | (_cmp("STOCHk_14_3_3_1d", ">", 70.0))
        | (_cmp("AROOND_14_1d", "<", 50.0))
        | (_cmp_cached_51)
      )
      # 15m & 1h & 4h up move, 1h & 4h still not high enough, 1d uptrend
      & (
        (_cmp("RSI_3_15m", "<", 85.0))
        | (_cmp("RSI_3_1h", "<", 80.0))
        | (_cmp("RSI_3_4h", "<", 60.0))
        | (_cmp("WILLR_14_1h", ">", -5.0))
        | (_cmp("AROOND_14_1h", "<", 25.0))
        | (_cmp("WILLR_14_4h", ">", -10.0))
        | (_cmp("AROOND_14_4h", "<", 50.0))
        | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 60.0))
        | (_cmp_cached_51)
      )
      # 15m & 1h & 4h up move, 15m still not high enough, 1h & 4h still not high enough & uptrend, 1d still not high enough
      & (
        (_cmp("RSI_3_15m", "<", 85.0))
        | (_cmp("RSI_3_1h", "<", 85.0))
        | (_cmp("RSI_3_4h", "<", 90.0))
        | (_cmp("RSI_14_15m", ">", 95.0))
        | (_cmp("CMF_20_15m", ">", 0.50))
        | (_cmp("UO_7_14_28_15m", ">", 80.0))
        | (_cmp("UO_7_14_28_change_pct_15m", "<", -0.0))
        | (_cmp("CCI_20_15m", ">", 250.0))
        | (_cmp("STOCHk_14_3_3_15m", ">", 90.0))
        | (_cmp("RSI_14_1h", ">", 95.0))
        | (_cmp("CMF_20_1h", ">", 0.50))
        | (_cmp("UO_7_14_28_1h", ">", 80.0))
        | (_cmp("CCI_20_1h", ">", 350.0))
        | (_cmp_cached_67)
        | (_cmp("RSI_14_4h", ">", 90.0))
        | (_cmp("CMF_20_4h", ">", 0.35))
        | (_cmp("UO_7_14_28_4h", ">", 75.0))
        | (_cmp("CCI_20_4h", ">", 500.0))
        | (_cmp("ROC_2_4h", "<", 10.0))
        | (_cmp_cached_49)
        | (_cmp("RSI_14_1d", ">", 70.0))
      )
      # 15m & 1h & 4h up move, 15m & 1h & 4h still not high enough, 1d still not high enough & overbought
      & (
        (_cmp("RSI_3_15m", "<", 90.0))
        | (_cmp("RSI_3_1h", "<", 60.0))
        | (_cmp("RSI_3_4h", "<", 60.0))
        | (_cmp("RSI_14_15m", ">", 85.0))
        | (_cmp("CCI_20_15m", ">", 250.0))
        | (_cmp("RSI_14_1h", ">", 70.0))
        | (_cmp("CCI_20_1h", ">", 200.0))
        | (_cmp("STOCHk_14_3_3_1h", ">", 90.0))
        | (_cmp("RSI_14_4h", ">", 65.0))
        | (_cmp("CCI_20_4h", ">", 200.0))
        | (_cmp("STOCHk_14_3_3_4h", ">", 90.0))
        | (_cmp("RSI_14_1d", ">", 65.0))
        | (_cmp("STOCHk_14_3_3_1d", ">", 70.0))
        | (_cmp("ROC_9_1d", "<", 30.0))
      )
      # 15m & 1h & 4h & 1d up move, 15m & 1h & 4h still not high enough. 1d still not high enough & uptrend
      & (
        (_cmp("RSI_3_15m", "<", 95.0))
        | (_cmp("RSI_3_1h", "<", 80.0))
        | (_cmp("RSI_3_4h", "<", 80.0))
        | (_cmp("RSI_3_1d", "<", 80.0))
        | (_cmp("RSI_14_15m", ">", 90.0))
        | (_cmp("RSI_14_1h", ">", 90.0))
        | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 70.0))
        | (_cmp("RSI_14_4h", ">", 90.0))
        | (_cmp("WILLR_14_4h", ">", -5.0))
        | (_cmp("RSI_14_1d", ">", 80.0))
        | (_cmp("STOCHRSIk_14_14_3_3_1d", ">", 80.0))
        | (_cmp("ROC_9_1d", "<", 40.0))
      )
      # 15m & 1h & 4h up move, 15m & 1h still not high enough, 4h still not high enough & uptrend
      & (
        (_cmp("RSI_3_15m", "<", 95.0))
        | (_cmp("RSI_3_1h", "<", 90.0))
        | (_cmp("RSI_3_4h", "<", 90.0))
        | (_cmp("RSI_14_15m", ">", 90.0))
        | (_cmp("CCI_20_15m", ">", 250.0))
        | (_cmp("RSI_14_1h", ">", 90.0))
        | (_cmp("AROOND_14_1h", "<", 25.0))
        | (_cmp("CCI_20_1h", ">", 300.0))
        | (_cmp("STOCHk_14_3_3_1h", ">", 90.0))
        | (_cmp("RSI_14_4h", ">", 95.0))
        | (_cmp("CCI_20_4h", ">", 300.0))
        | (_cmp_cached_38)
      )
      # 1h & 4h & 1d up move, 15m still not high enough, 1h & 4h & 1d still not high enough, 1d uptrend
      & (
        (_cmp("RSI_3_1h", "<", 80.0))
        | (_cmp("RSI_3_4h", "<", 60.0))
        | (_cmp("RSI_3_1d", "<", 90.0))
        | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 80.0))
        | (_cmp("WILLR_14_1h", ">", -20.0))
        | (_cmp("WILLR_14_4h", ">", -25.0))
        | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 20.0))
        | (_cmp("AROOND_14_1d", "<", 50.0))
        | (_cmp("ROC_9_1d", "<", 20.0))
      )
    )

    df["global_protections_short_dump"] = (
      # 15m & 1h up move, 15m & 1h still not high enough, 4h still low, 1d still low & downtrend
      (
        (_cmp("RSI_3_15m", "<", 80.0))
        | (_cmp("RSI_3_1h", "<", 70.0))
        | (_cmp("RSI_14_15m", ">", 80.0))
        | (_cmp("CCI_20_15m", ">", 400.0))
        | (_cmp("RSI_14_1h", ">", 75.0))
        | (_cmp("CCI_20_1h", ">", 250.0))
        | (_cmp("RSI_14_4h", ">", 60.0))
        | (_cmp("AROOND_14_4h", "<", 50.0))
        | (_cmp("CCI_20_4h", ">", 200.0))
        | (_cmp("RSI_14_1d", ">", 50.0))
        | (_cmp("AROOND_14_1d", "<", 75.0))
        | (_cmp("ROC_9_1d", ">", -30.0))
      )
      # 15m up move, 15m still low, 1h & 4h & 1d still not high
      & (
        (_cmp("RSI_3_15m", "<", 85.0))
        | (_cmp("AROOND_14_15m", "<", 50.0))
        | (_cmp("RSI_14_1h", ">", 70.0))
        | (_cmp("WILLR_14_1h", ">", -50.0))
        | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 80.0))
        | (_cmp("AROOND_14_1h", "<", 75.0))
        | (_cmp("RSI_14_4h", ">", 70.0))
        | (_cmp("WILLR_14_4h", ">", -50.0))
        | (_cmp("AROOND_14_4h", "<", 25.0))
        | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 30.0))
        | (_cmp("RSI_14_1d", ">", 70.0))
      )
      # 1h & 4h up move, 15m & 1h & 4h still not high enough, 1d still low & downtrend
      & (
        (_cmp("RSI_3_1h", "<", 70.0))
        | (_cmp("RSI_3_4h", "<", 90.0))
        | (_cmp("RSI_14_15m", ">", 95.0))
        | (_cmp("CCI_20_15m", ">", 600.0))
        | (_cmp("RSI_14_1h", ">", 95.0))
        | (_cmp("CCI_20_1h", ">", 600.0))
        | (_cmp("RSI_14_4h", ">", 95.0))
        | (_cmp("WILLR_14_4h", ">", -10.0))
        | (_cmp("CCI_20_4h", ">", 600.0))
        | (_cmp("RSI_14_1d", ">", 40.0))
        | (_cmp("ROC_9_1d", ">", -20.0))
      )
    )

    df["protections_short_rebuy"] = True

    df = self._test_x7_restore_tail_protections(test_x7_full_df, df)

    tok = time.perf_counter()
    log.debug(f"[{metadata['pair']}] Populate indicators took a total of: {tok - tik:0.4f} seconds.")

    return df

  # Confirm Trade Entry
  # ---------------------------------------------------------------------------------------------
