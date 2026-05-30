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

from test_x7_modules.masks import build_comparison_cache
from test_x7_modules.merge import fast_merge_informative_pair as merge_informative_pair
log = logging.getLogger(__name__)
_TRUE_VALUES = {"1", "true", "yes", "on"}
_FALSE_VALUES = {"0", "false", "no", "off"}



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

    # Use set to automatically avoid duplicates
    informative_pairs = set()

    # Assign tf to each pair so they can be downloaded and cached for strategy.
    for info_timeframe in self.info_timeframes:
      informative_pairs.update((pair, info_timeframe) for pair in pairs)

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
      if self.config.get("trading_mode") in ["futures", "margin"]:
        btc_info_pair = f"BTC/{self.config['stake_currency']}:{self.config['stake_currency']}"
      else:
        btc_info_pair = f"BTC/{self.config['stake_currency']}"
    else:
      if self.config.get("trading_mode") in ["futures", "margin"]:
        btc_info_pair = "BTC/USDT:USDT"
      else:
        btc_info_pair = "BTC/USDT"

    informative_pairs.update((btc_info_pair, btc_info_timeframe) for btc_info_timeframe in self.btc_info_timeframes)

    return list(informative_pairs)

  def informative_1d_indicators(self, metadata: dict, info_timeframe) -> DataFrame:
    tik = time.perf_counter()

    assert self.dp, "DataProvider is required for multiple timeframes."

    # Get dataframe
    informative_1d = self.dp.get_pair_dataframe(pair=metadata["pair"], timeframe=info_timeframe)

    # Empty dataframe protection
    if informative_1d.empty:
      return informative_1d

    # =========================================================================
    # BASE DATA
    # =========================================================================

    close_np = informative_1d["close"].to_numpy(copy=False)
    high_np = informative_1d["high"].to_numpy(copy=False)
    low_np = informative_1d["low"].to_numpy(copy=False)
    open_np = informative_1d["open"].to_numpy(copy=False)
    volume_np = informative_1d["volume"].to_numpy(copy=False)

    # =========================================================================
    # CORE INDICATORS
    # =========================================================================
    rsi_3 = ta.RSI(close_np, timeperiod=3)
    rsi_14 = ta.RSI(close_np, timeperiod=14)
    # bb_upper, bb_middle, bb_lower = ta.BBANDS(close_np, timeperiod=20, nbdevup=2.0, nbdevdn=2.0, matype=0)
    # bb_middle_safe = np.where(bb_middle == 0, np.nan, bb_middle)
    aroon_down, aroon_up = ta.AROON(high_np, low_np, timeperiod=14)

    # =========================================================================
    # STOCH
    # =========================================================================
    stoch_k = self.stoch_k(high_np, low_np, close_np)

    # =========================================================================
    # STOCH RSI
    # =========================================================================
    stochrsi_k = self.stochrsi_k(rsi_14)

    # =========================================================================
    # MONEY FLOW
    # =========================================================================

    mfi_14 = ta.MFI(high_np, low_np, close_np, volume_np, timeperiod=14)
    cmf_20 = self.chaikin_money_flow(high_np, low_np, close_np, volume_np, timeperiod=20)

    # =========================================================================
    # MOMENTUM
    # =========================================================================
    willr_14 = ta.WILLR(high_np, low_np, close_np, timeperiod=14)
    roc_2 = ta.ROC(close_np, timeperiod=2)
    roc_9 = ta.ROC(close_np, timeperiod=9)

    # =========================================================================
    # RSI CHANGE %
    # =========================================================================
    rsi3_change = self.fast_pct_change(rsi_3)
    # rsi14_change = self.fast_pct_change(rsi_14)

    # =========================================================================
    # CANDLE %
    # =========================================================================
    open_safe = np.where(open_np == 0, np.nan, open_np)
    change_pct = ((close_np - open_np) / open_safe) * 100.0

    # =========================================================================
    # WICK %
    # =========================================================================
    max_oc = np.maximum(open_np, close_np)
    min_oc = np.minimum(open_np, close_np)
    max_oc_calc = np.where(max_oc == 0, np.nan, max_oc)
    min_oc_calc = np.where(min_oc == 0, np.nan, min_oc)
    top_wick_pct = ((high_np - max_oc) / max_oc_calc) * 100.0
    bot_wick_pct = np.abs(((low_np - min_oc) / min_oc_calc) * 100.0)

    # =========================================================================
    # HIGH / LOW ROLLING
    # =========================================================================
    high_max_6 = ta.MAX(high_np, timeperiod=6)
    high_max_12 = ta.MAX(high_np, timeperiod=12)
    high_max_20 = ta.MAX(high_np, timeperiod=20)
    high_max_30 = ta.MAX(high_np, timeperiod=30)
    low_min_6 = ta.MIN(low_np, timeperiod=6)
    low_min_12 = ta.MIN(low_np, timeperiod=12)
    low_min_20 = ta.MIN(low_np, timeperiod=20)
    low_min_30 = ta.MIN(low_np, timeperiod=30)

    # =========================================================================
    # ASSIGN DATAFRAME
    # =========================================================================
    new_cols = pd.DataFrame(
      {
        # Core indicators
        "RSI_3": rsi_3,
        "RSI_14": rsi_14,
        # "BBL_20_2.0": bb_lower,
        # "BBU_20_2.0": bb_upper,
        # "BBB_20_2.0": ((bb_upper - bb_lower) / bb_middle_safe) * 100.0,
        # Stoch
        "STOCHk_14_3_3": stoch_k,
        # Stoch RSI
        "STOCHRSIk_14_14_3_3": stochrsi_k,
        # Money Flow
        "MFI_14": mfi_14,
        "CMF_20": cmf_20,
        # Momentum
        "WILLR_14": willr_14,
        "AROONU_14": aroon_up,
        "AROOND_14": aroon_down,
        "ROC_2": roc_2,
        "ROC_9": roc_9,
        # Change %
        "RSI_3_change_pct": rsi3_change,
        # "RSI_14_change_pct": rsi14_change,
        # Candle %
        "change_pct": change_pct,
        # Wick %
        "top_wick_pct": top_wick_pct,
        "bot_wick_pct": bot_wick_pct,
        # Rolling
        "high_max_6": high_max_6,
        "high_max_12": high_max_12,
        "high_max_20": high_max_20,
        "high_max_30": high_max_30,
        "low_min_6": low_min_6,
        "low_min_12": low_min_12,
        "low_min_20": low_min_20,
        "low_min_30": low_min_30,
      },
      index=informative_1d.index,
    )

    informative_1d = pd.concat([informative_1d, new_cols], axis=1, copy=False)

    # Enable ONLY during debugging
    debug = False
    if debug:
      debug_cols = [
        # Core indicators
        "RSI_3",
        "RSI_14",
        # "BBL_20_2.0",
        # "BBU_20_2.0",
        # "BBB_20_2.0",
        # Stoch
        "STOCHk_14_3_3",
        # Stoch RSI
        "STOCHRSIk_14_14_3_3",
        # Money Flow
        "MFI_14",
        "CMF_20",
        # Momentum
        "WILLR_14",
        "AROONU_14",
        "AROOND_14",
        "ROC_2",
        "ROC_9",
        # Change %
        "RSI_3_change_pct",
        # "RSI_14_change_pct",
        # Candle %
        "change_pct",
        # Wick %
        "top_wick_pct",
        "bot_wick_pct",
        # Rolling
        "high_max_6",
        "high_max_12",
        "high_max_20",
        "high_max_30",
        "low_min_6",
        "low_min_12",
        "low_min_20",
        "low_min_30",
      ]

      self.validate_indicators(df=informative_1d, columns=debug_cols, pair=metadata["pair"], timeframe=info_timeframe)

    # =========================================================================
    # LOGGING
    # =========================================================================

    tok = time.perf_counter()

    log.debug("[%s] informative_1d_indicators took: %.4f seconds.", metadata["pair"], tok - tik)

    return informative_1d

  def informative_4h_indicators(self, metadata: dict, info_timeframe) -> DataFrame:
    tik = time.perf_counter()

    assert self.dp, "DataProvider is required for multiple timeframes."

    # Get dataframe
    informative_4h = self.dp.get_pair_dataframe(pair=metadata["pair"], timeframe=info_timeframe)

    # Empty dataframe protection
    if informative_4h.empty:
      return informative_4h

    # =========================================================================
    # BASE DATA
    # =========================================================================

    close_np = informative_4h["close"].to_numpy(copy=False)
    high_np = informative_4h["high"].to_numpy(copy=False)
    low_np = informative_4h["low"].to_numpy(copy=False)
    open_np = informative_4h["open"].to_numpy(copy=False)
    volume_np = informative_4h["volume"].to_numpy(copy=False)

    # =========================================================================
    # CORE INDICATORS
    # =========================================================================
    rsi_3 = ta.RSI(close_np, timeperiod=3)
    rsi_14 = ta.RSI(close_np, timeperiod=14)
    # bb_upper, bb_middle, bb_lower = ta.BBANDS(close_np, timeperiod=20, nbdevup=2.0, nbdevdn=2.0, matype=0)
    # bb_middle_safe = np.where(bb_middle == 0, np.nan, bb_middle)
    aroon_down, aroon_up = ta.AROON(high_np, low_np, timeperiod=14)

    # =========================================================================
    # STOCH
    # =========================================================================
    stoch_k = self.stoch_k(high_np, low_np, close_np)

    # =========================================================================
    # STOCH RSI
    # =========================================================================
    stochrsi_k = self.stochrsi_k(rsi_14)

    # =========================================================================
    # KST
    # =========================================================================
    kst1 = ta.SMA(ta.ROC(close_np, 10), 10)
    kst2 = ta.SMA(ta.ROC(close_np, 15), 10)
    kst3 = ta.SMA(ta.ROC(close_np, 20), 10)
    kst4 = ta.SMA(ta.ROC(close_np, 30), 15)
    kst_main = kst1 + (2.0 * kst2) + (3.0 * kst3) + (4.0 * kst4)
    kst_signal = ta.SMA(kst_main, 9)

    # =========================================================================
    # MONEY FLOW
    # =========================================================================
    mfi_14 = ta.MFI(high_np, low_np, close_np, volume_np, timeperiod=14)
    cmf_20 = self.chaikin_money_flow(high_np, low_np, close_np, volume_np, timeperiod=20)

    # =========================================================================
    # MOMENTUM
    # =========================================================================
    ema_12 = ta.EMA(close_np, timeperiod=12)
    ema_200 = ta.EMA(close_np, timeperiod=200)
    willr_14 = ta.WILLR(high_np, low_np, close_np, timeperiod=14)
    uo = ta.ULTOSC(high_np, low_np, close_np)
    obv = ta.OBV(close_np, volume_np)
    roc_2 = ta.ROC(close_np, timeperiod=2)
    roc_9 = ta.ROC(close_np, timeperiod=9)
    cci_20 = ta.CCI(high_np, low_np, close_np, timeperiod=20)

    # =========================================================================
    # CHANGE %
    # =========================================================================
    rsi_3_change = self.fast_pct_change(rsi_3)
    rsi_14_change = self.fast_pct_change(rsi_14)
    stochrsi_change = self.fast_pct_change(stochrsi_k)
    # uo_change = self.fast_pct_change(uo)
    obv_change = self.fast_pct_change(obv)
    cci_change = self.fast_pct_change(cci_20)

    # =========================================================================
    # CANDLE %
    # =========================================================================
    open_safe = np.where(open_np == 0, np.nan, open_np)
    change_pct = ((close_np - open_np) / open_safe) * 100.0

    # =========================================================================
    # WICK %
    # =========================================================================
    max_oc = np.maximum(open_np, close_np)
    # min_oc = np.minimum(open_np, close_np)
    max_oc_calc = np.where(max_oc == 0, np.nan, max_oc)
    # min_oc_calc = np.where(min_oc == 0, np.nan, min_oc)
    top_wick_pct = ((high_np - max_oc) / max_oc_calc) * 100.0
    # bot_wick_pct = np.abs(((low_np - min_oc) / min_oc_calc) * 100.0)

    # =========================================================================
    # ROLLING
    # =========================================================================

    high_max_6 = ta.MAX(high_np, timeperiod=6)
    high_max_12 = ta.MAX(high_np, timeperiod=12)
    high_max_24 = ta.MAX(high_np, timeperiod=24)
    # low_min_6 = ta.MIN(low_np, timeperiod=6)
    low_min_12 = ta.MIN(low_np, timeperiod=12)
    low_min_24 = ta.MIN(low_np, timeperiod=24)
    # change_pct_min_3 = ta.MIN(change_pct, timeperiod=3)
    # change_pct_min_6 = ta.MIN(change_pct, timeperiod=6)
    # change_pct_max_3 = ta.MAX(change_pct, timeperiod=3)
    # change_pct_max_6 = ta.MAX(change_pct, timeperiod=6)

    # =========================================================================
    # ASSIGN DATAFRAME
    # =========================================================================
    new_cols = pd.DataFrame(
      {
        # Core indicators
        "RSI_3": rsi_3,
        "RSI_14": rsi_14,
        # "BBL_20_2.0": bb_lower,
        # "BBU_20_2.0": bb_upper,
        # "BBB_20_2.0": ((bb_upper - bb_lower) / bb_middle_safe) * 100.0,
        "AROONU_14": aroon_up,
        "AROOND_14": aroon_down,
        # Stoch
        "STOCHk_14_3_3": stoch_k,
        # Stoch RSI
        "STOCHRSIk_14_14_3_3": stochrsi_k,
        # KST
        "KST_10_15_20_30_10_10_10_15": kst_main,
        "KSTs_9": kst_signal,
        # Money Flow
        "MFI_14": mfi_14,
        "CMF_20": cmf_20,
        # Momentum
        "EMA_12": ema_12,
        "EMA_200": ema_200,
        "WILLR_14": willr_14,
        "UO_7_14_28": uo,
        # "OBV": obv,
        "ROC_2": roc_2,
        "ROC_9": roc_9,
        "CCI_20": cci_20,
        # Change %
        "STOCHRSIk_14_14_3_3_change_pct": stochrsi_change,
        "CCI_20_change_pct": cci_change,
        "RSI_3_change_pct": rsi_3_change,
        "RSI_14_change_pct": rsi_14_change,
        # "UO_7_14_28_change_pct": uo_change,
        "OBV_change_pct": obv_change,
        # Candle %
        "change_pct": change_pct,
        # "change_pct_min_3": change_pct_min_3,
        # "change_pct_min_6": change_pct_min_6,
        # "change_pct_max_3": change_pct_max_3,
        # "change_pct_max_6": change_pct_max_6,
        #  Wicks %
        "top_wick_pct": top_wick_pct,
        # "bot_wick_pct": bot_wick_pct,
        # Rolling
        "high_max_6": high_max_6,
        "high_max_12": high_max_12,
        "high_max_24": high_max_24,
        # "low_min_6": low_min_6,
        "low_min_12": low_min_12,
        "low_min_24": low_min_24,
      },
      index=informative_4h.index,
    )

    informative_4h = pd.concat([informative_4h, new_cols], axis=1, copy=False)

    # Enable ONLY during debugging
    debug = False
    if debug:
      debug_cols = [
        # Core indicators
        "RSI_3",
        "RSI_14",
        # "BBL_20_2.0",
        # "BBU_20_2.0",
        # "BBB_20_2.0",
        "AROONU_14",
        "AROOND_14",
        # Stoch
        "STOCHk_14_3_3",
        # Stoch RSI
        "STOCHRSIk_14_14_3_3",
        # KST
        "KST_10_15_20_30_10_10_10_15",
        "KSTs_9",
        # Money Flow
        "MFI_14",
        "CMF_20",
        # Momentum
        "EMA_12",
        "EMA_200",
        "WILLR_14",
        "UO_7_14_28",
        # "OBV",
        "ROC_2",
        "ROC_9",
        "CCI_20",
        # Change %
        "STOCHRSIk_14_14_3_3_change_pct",
        "CCI_20_change_pct",
        "RSI_3_change_pct",
        "RSI_14_change_pct",
        # "UO_7_14_28_change_pct",
        "OBV_change_pct",
        # Candle %
        "change_pct",
        # "change_pct_min_3",
        # "change_pct_min_6",
        # "change_pct_max_3",
        # "change_pct_max_6",
        # Wicks %
        # "top_wick_pct",
        # "bot_wick_pct",
        # Rolling
        "high_max_6",
        "high_max_12",
        "high_max_24",
        # "low_min_6",
        "low_min_12",
        "low_min_24",
      ]

      self.validate_indicators(df=informative_4h, columns=debug_cols, pair=metadata["pair"], timeframe=info_timeframe)
    # =========================================================================
    # LOGGING
    # =========================================================================

    tok = time.perf_counter()

    log.debug("[%s] informative_4h_indicators took: %.4f seconds.", metadata["pair"], tok - tik)

    return informative_4h

  def informative_1h_indicators(self, metadata: dict, info_timeframe) -> DataFrame:
    tik = time.perf_counter()

    assert self.dp, "DataProvider is required for multiple timeframes."

    # =========================================================================
    # GET DATAFRAME
    # =========================================================================

    informative_1h = self.dp.get_pair_dataframe(pair=metadata["pair"], timeframe=info_timeframe)

    # Empty dataframe protection
    if informative_1h.empty:
      return informative_1h

    # =========================================================================
    # BASE DATA
    # =========================================================================

    close_np = informative_1h["close"].to_numpy(copy=False)
    high_np = informative_1h["high"].to_numpy(copy=False)
    low_np = informative_1h["low"].to_numpy(copy=False)
    open_np = informative_1h["open"].to_numpy(copy=False)
    volume_np = informative_1h["volume"].to_numpy(copy=False)

    # =========================================================================
    # CORE INDICATORS
    # =========================================================================
    rsi_3 = ta.RSI(close_np, timeperiod=3)
    rsi_14 = ta.RSI(close_np, timeperiod=14)
    bb_upper, bb_middle, bb_lower = ta.BBANDS(close_np, timeperiod=20, nbdevup=2.0, nbdevdn=2.0, matype=0)
    bb_middle_safe = np.where(bb_middle == 0, np.nan, bb_middle)
    aroon_down, aroon_up = ta.AROON(high_np, low_np, timeperiod=14)

    # =========================================================================
    # STOCH
    # =========================================================================
    stoch_k = self.stoch_k(high_np, low_np, close_np)

    # =========================================================================
    # STOCH RSI
    # =========================================================================
    stochrsi_k = self.stochrsi_k(rsi_14)

    # =========================================================================
    # KST
    # =========================================================================
    kst1 = ta.SMA(ta.ROC(close_np, 10), 10)
    kst2 = ta.SMA(ta.ROC(close_np, 15), 10)
    kst3 = ta.SMA(ta.ROC(close_np, 20), 10)
    kst4 = ta.SMA(ta.ROC(close_np, 30), 15)
    kst_main = kst1 + (2.0 * kst2) + (3.0 * kst3) + (4.0 * kst4)
    kst_signal = ta.SMA(kst_main, 9)

    # =========================================================================
    # MONEY FLOW
    # =========================================================================
    mfi_14 = ta.MFI(high_np, low_np, close_np, volume_np, timeperiod=14)
    cmf_20 = self.chaikin_money_flow(high_np, low_np, close_np, volume_np, timeperiod=20)

    # =========================================================================
    # MOMENTUM
    # =========================================================================
    ema_12 = ta.EMA(close_np, timeperiod=12)
    ema_200 = ta.EMA(close_np, timeperiod=200)
    sma_16 = ta.SMA(close_np, timeperiod=16)
    willr_14 = ta.WILLR(high_np, low_np, close_np, timeperiod=14)
    willr_84 = ta.WILLR(high_np, low_np, close_np, timeperiod=84)
    uo = ta.ULTOSC(high_np, low_np, close_np)
    # obv = ta.OBV(close_np, volume_np)
    roc_2 = ta.ROC(close_np, timeperiod=2)
    roc_9 = ta.ROC(close_np, timeperiod=9)
    cci_20 = ta.CCI(high_np, low_np, close_np, timeperiod=20)

    # =========================================================================
    # CHANGE %
    # =========================================================================
    rsi_3_change = self.fast_pct_change(rsi_3)
    rsi_14_change = self.fast_pct_change(rsi_14)
    # stochrsi_change = self.fast_pct_change(stochrsi_k)
    # uo_change = self.fast_pct_change(uo)
    # obv_change = self.fast_pct_change(obv)
    cci_change = self.fast_pct_change(cci_20)

    # =========================================================================
    # CANDLE %
    # =========================================================================
    open_safe = np.where(open_np == 0, np.nan, open_np)
    change_pct = ((close_np - open_np) / open_safe) * 100.0

    # =========================================================================
    # WICK %
    # =========================================================================
    # max_oc = np.maximum(open_np, close_np)
    # min_oc = np.minimum(open_np, close_np)
    # max_oc_calc = np.where(max_oc == 0, np.nan, max_oc)
    # min_oc_calc = np.where(min_oc == 0, np.nan, min_oc)
    # top_wick_pct = ((high_np - max_oc) / max_oc_calc) * 100.0
    # bot_wick_pct = np.abs(((low_np - min_oc) / min_oc_calc) * 100.0)

    # =========================================================================
    # ROLLING
    # =========================================================================
    high_max_6 = ta.MAX(high_np, timeperiod=6)
    high_max_12 = ta.MAX(high_np, timeperiod=12)
    high_max_24 = ta.MAX(high_np, timeperiod=24)
    low_min_6 = ta.MIN(low_np, timeperiod=6)
    low_min_12 = ta.MIN(low_np, timeperiod=12)
    low_min_24 = ta.MIN(low_np, timeperiod=24)

    new_cols = pd.DataFrame(
      {
        "RSI_3": rsi_3,
        "RSI_14": rsi_14,
        "RSI_3_change_pct": rsi_3_change,
        "RSI_14_change_pct": rsi_14_change,
        "EMA_12": ema_12,
        "EMA_200": ema_200,
        "SMA_16": sma_16,
        "BBL_20_2.0": bb_lower,
        "BBU_20_2.0": bb_upper,
        "BBB_20_2.0": ((bb_upper - bb_lower) / bb_middle_safe) * 100.0,
        "MFI_14": mfi_14,
        "CMF_20": cmf_20,
        "WILLR_14": willr_14,
        "WILLR_84": willr_84,
        "AROONU_14": aroon_up,
        "AROOND_14": aroon_down,
        "STOCHk_14_3_3": stoch_k,
        "STOCHRSIk_14_14_3_3": stochrsi_k,
        # "STOCHRSIk_14_14_3_3_change_pct": stochrsi_change,
        "KST_10_15_20_30_10_10_10_15": kst_main,
        "KSTs_9": kst_signal,
        "UO_7_14_28": uo,
        # "UO_7_14_28_change_pct": uo_change,
        # "OBV": obv,
        # "OBV_change_pct": obv_change,
        "ROC_2": roc_2,
        "ROC_9": roc_9,
        "CCI_20": cci_20,
        "CCI_20_change_pct": cci_change,
        "change_pct": change_pct,
        # "top_wick_pct": top_wick_pct,
        # "bot_wick_pct": bot_wick_pct,
        "high_max_6": high_max_6,
        "high_max_12": high_max_12,
        "high_max_24": high_max_24,
        "low_min_6": low_min_6,
        "low_min_12": low_min_12,
        "low_min_24": low_min_24,
      },
      index=informative_1h.index,
    )

    informative_1h = pd.concat([informative_1h, new_cols], axis=1, copy=False)

    # Enable ONLY during debugging
    debug = False
    if debug:
      debug_cols = [
        "RSI_3",
        "RSI_14",
        "RSI_3_change_pct",
        "RSI_14_change_pct",
        "EMA_12",
        "EMA_200",
        "SMA_16",
        "BBL_20_2.0",
        "BBU_20_2.0",
        "BBB_20_2.0",
        "MFI_14",
        "CMF_20",
        "WILLR_14",
        "WILLR_84",
        "AROONU_14",
        "AROOND_14",
        "STOCHk_14_3_3",
        "STOCHRSIk_14_14_3_3",
        # "STOCHRSIk_14_14_3_3_change_pct",
        "KST_10_15_20_30_10_10_10_15",
        "KSTs_9",
        "UO_7_14_28",
        # "UO_7_14_28_change_pct",
        # "OBV",
        # "OBV_change_pct",
        "ROC_2",
        "ROC_9",
        "CCI_20",
        "CCI_20_change_pct",
        "change_pct",
        # "top_wick_pct",
        # "bot_wick_pct",
        "high_max_6",
        "high_max_12",
        "high_max_24",
        "low_min_6",
        "low_min_12",
        "low_min_24",
      ]

      self.validate_indicators(df=informative_1h, columns=debug_cols, pair=metadata["pair"], timeframe=info_timeframe)

    # =========================================================================
    # LOGGING
    # =========================================================================

    tok = time.perf_counter()

    log.debug("[%s] informative_1h_indicators took: %.4f seconds.", metadata["pair"], tok - tik)

    return informative_1h

  def informative_15m_indicators(self, metadata: dict, info_timeframe) -> DataFrame:
    tik = time.perf_counter()

    assert self.dp, "DataProvider is required for multiple timeframes."

    # =========================================================================
    # GET DATAFRAME
    # =========================================================================

    informative_15m = self.dp.get_pair_dataframe(pair=metadata["pair"], timeframe=info_timeframe)

    # Empty dataframe protection
    if informative_15m.empty:
      return informative_15m

    # =========================================================================
    # BASE DATA
    # =========================================================================

    close_np = informative_15m["close"].to_numpy(copy=False)
    high_np = informative_15m["high"].to_numpy(copy=False)
    low_np = informative_15m["low"].to_numpy(copy=False)
    open_np = informative_15m["open"].to_numpy(copy=False)
    volume_np = informative_15m["volume"].to_numpy(copy=False)

    # =========================================================================
    # CORE INDICATORS
    # =========================================================================
    rsi_3 = ta.RSI(close_np, timeperiod=3)
    rsi_14 = ta.RSI(close_np, timeperiod=14)
    aroon_down, aroon_up = ta.AROON(high_np, low_np, timeperiod=14)

    # =========================================================================
    # STOCH
    # =========================================================================
    stoch_k = self.stoch_k(high_np, low_np, close_np)

    # =========================================================================
    # STOCH RSI
    # =========================================================================
    stochrsi_k = self.stochrsi_k(rsi_14)

    # =========================================================================
    # MONEY FLOW
    # =========================================================================
    mfi_14 = ta.MFI(high_np, low_np, close_np, volume_np, timeperiod=14)
    cmf_20 = self.chaikin_money_flow(high_np, low_np, close_np, volume_np, timeperiod=20)

    # =========================================================================
    # MOMENTUM
    # =========================================================================
    ema_12 = ta.EMA(close_np, timeperiod=12)
    ema_20 = ta.EMA(close_np, timeperiod=20)
    ema_26 = ta.EMA(close_np, timeperiod=26)
    willr_14 = ta.WILLR(high_np, low_np, close_np, timeperiod=14)
    uo = ta.ULTOSC(high_np, low_np, close_np)
    obv = ta.OBV(close_np, volume_np)
    roc_9 = ta.ROC(close_np, timeperiod=9)
    cci_20 = ta.CCI(high_np, low_np, close_np, timeperiod=20)

    # =========================================================================
    # CHANGE %
    # =========================================================================
    rsi_3_change = self.fast_pct_change(rsi_3)
    rsi_14_change = self.fast_pct_change(rsi_14)
    # stochrsi_change = self.fast_pct_change(stochrsi_k)
    uo_change = self.fast_pct_change(uo)
    obv_change = self.fast_pct_change(obv)
    cci_change = self.fast_pct_change(cci_20)

    # =========================================================================
    # CANDLE %
    # =========================================================================
    open_safe = np.where(open_np == 0, np.nan, open_np)
    change_pct = ((close_np - open_np) / open_safe) * 100.0

    # =========================================================================
    # WICK %
    # =========================================================================
    # max_oc = np.maximum(open_np, close_np)
    # min_oc = np.minimum(open_np, close_np)
    # max_oc_calc = np.where(max_oc == 0, np.nan, max_oc)
    # min_oc_calc = np.where(min_oc == 0, np.nan, min_oc)
    # top_wick_pct = ((high_np - max_oc) / max_oc_calc) * 100.0
    # bot_wick_pct = np.abs(((low_np - min_oc) / min_oc_calc) * 100.0)

    new_cols = pd.DataFrame(
      {
        "RSI_3": rsi_3,
        "RSI_14": rsi_14,
        "RSI_3_change_pct": rsi_3_change,
        "RSI_14_change_pct": rsi_14_change,
        "EMA_12": ema_12,
        "EMA_20": ema_20,
        "EMA_26": ema_26,
        "MFI_14": mfi_14,
        "CMF_20": cmf_20,
        "WILLR_14": willr_14,
        "AROONU_14": aroon_up,
        "AROOND_14": aroon_down,
        "STOCHk_14_3_3": stoch_k,
        "STOCHRSIk_14_14_3_3": stochrsi_k,
        # "STOCHRSIk_14_14_3_3_change_pct": stochrsi_change,
        "UO_7_14_28": uo,
        "UO_7_14_28_change_pct": uo_change,
        # "OBV": obv,
        "OBV_change_pct": obv_change,
        "ROC_9": roc_9,
        "CCI_20": cci_20,
        "CCI_20_change_pct": cci_change,
        "change_pct": change_pct,
        # "top_wick_pct": top_wick_pct,
        # "bot_wick_pct": bot_wick_pct,
      },
      index=informative_15m.index,
    )

    informative_15m = pd.concat([informative_15m, new_cols], axis=1, copy=False)

    # Enable ONLY during debugging
    debug = False
    if debug:
      debug_cols = [
        "RSI_3",
        "RSI_14",
        "RSI_3_change_pct",
        "RSI_14_change_pct",
        "EMA_12",
        "EMA_20",
        "EMA_26",
        "MFI_14",
        "CMF_20",
        "WILLR_14",
        "AROONU_14",
        "AROOND_14",
        "STOCHk_14_3_3",
        "STOCHRSIk_14_14_3_3",
        # "STOCHRSIk_14_14_3_3_change_pct",
        "UO_7_14_28",
        "UO_7_14_28_change_pct",
        # "OBV",
        "OBV_change_pct",
        "ROC_9",
        "CCI_20",
        "CCI_20_change_pct",
        "change_pct",
        # "top_wick_pct",
        # "bot_wick_pct",
      ]

      self.validate_indicators(df=informative_15m, columns=debug_cols, pair=metadata["pair"], timeframe=info_timeframe)

    # =========================================================================
    # LOGGING
    # =========================================================================

    tok = time.perf_counter()

    log.debug("[%s] informative_15m_indicators took: %.4f seconds.", metadata["pair"], tok - tik)

    return informative_15m

  def base_tf_5m_indicators(self, metadata: dict, df: DataFrame) -> DataFrame:
    tik = time.perf_counter()

    # =========================================================================
    # BASE DATA
    # =========================================================================
    close_np = df["close"].to_numpy(copy=False)
    high_np = df["high"].to_numpy(copy=False)
    low_np = df["low"].to_numpy(copy=False)
    open_np = df["open"].to_numpy(copy=False)
    volume_np = df["volume"].to_numpy(copy=False)

    # =========================================================================
    # CORE INDICATORS
    # =========================================================================
    rsi_3 = ta.RSI(close_np, timeperiod=3)
    rsi_4 = ta.RSI(close_np, timeperiod=4)
    rsi_14 = ta.RSI(close_np, timeperiod=14)
    rsi_20 = ta.RSI(close_np, timeperiod=20)
    bb_upper_20, bb_middle_20, bb_lower_20 = ta.BBANDS(close_np, timeperiod=20, nbdevup=2.0, nbdevdn=2.0, matype=0)
    bb_middle_20_safe = np.where(bb_middle_20 == 0, np.nan, bb_middle_20)
    bb_upper_40, bb_middle_40, bb_lower_40 = ta.BBANDS(close_np, timeperiod=40, nbdevup=2.0, nbdevdn=2.0, matype=0)
    # bb_middle_40_safe = np.where(bb_middle_40 == 0, np.nan, bb_middle_40)
    # bb_range_40 = np.where((bb_upper_40 - bb_lower_40) == 0, np.nan, (bb_upper_40 - bb_lower_40))
    aroon_down, aroon_up = ta.AROON(high_np, low_np, timeperiod=14)

    # =========================================================================
    # STOCH RSI
    # =========================================================================
    stochrsi_k = self.stochrsi_k(rsi_14)

    # =========================================================================
    # KST
    # =========================================================================
    kst1 = ta.SMA(ta.ROC(close_np, 10), 10)
    kst2 = ta.SMA(ta.ROC(close_np, 15), 10)
    kst3 = ta.SMA(ta.ROC(close_np, 20), 10)
    kst4 = ta.SMA(ta.ROC(close_np, 30), 15)
    kst_main = kst1 + (2.0 * kst2) + (3.0 * kst3) + (4.0 * kst4)
    kst_signal = ta.SMA(kst_main, 9)

    # =========================================================================
    # MONEY FLOW
    # =========================================================================
    mfi_14 = ta.MFI(high_np, low_np, close_np, volume_np, timeperiod=14)
    cmf_20 = self.chaikin_money_flow(high_np, low_np, close_np, volume_np, timeperiod=20)

    # =========================================================================
    # MOMENTUM
    # =========================================================================
    # ema_3 = ta.EMA(close_np, timeperiod=3)
    ema_9 = ta.EMA(close_np, timeperiod=9)
    ema_12 = ta.EMA(close_np, timeperiod=12)
    ema_16 = ta.EMA(close_np, timeperiod=16)
    ema_20 = ta.EMA(close_np, timeperiod=20)
    ema_26 = ta.EMA(close_np, timeperiod=26)
    ema_50 = ta.EMA(close_np, timeperiod=50)
    ema_100 = ta.EMA(close_np, timeperiod=100)
    ema_200 = ta.EMA(close_np, timeperiod=200)
    sma_9 = ta.SMA(close_np, timeperiod=9)
    sma_16 = ta.SMA(close_np, timeperiod=16)
    sma_21 = ta.SMA(close_np, timeperiod=21)
    sma_30 = ta.SMA(close_np, timeperiod=30)
    sma_200 = ta.SMA(close_np, timeperiod=200)
    willr_14 = ta.WILLR(high_np, low_np, close_np, timeperiod=14)
    willr_480 = ta.WILLR(high_np, low_np, close_np, timeperiod=480)
    # obv = ta.OBV(close_np, volume_np)
    roc_2 = ta.ROC(close_np, timeperiod=2)
    roc_9 = ta.ROC(close_np, timeperiod=9)

    # =========================================================================
    # CHANGE %
    # =========================================================================

    # rsi_3_change = self.fast_pct_change(rsi_3)
    rsi_14_change = self.fast_pct_change(rsi_14)
    # obv_change = self.fast_pct_change(obv)

    # =========================================================================
    # CANDLE %
    # =========================================================================

    open_safe = np.where(open_np == 0, np.nan, open_np)
    change_pct = ((close_np - open_np) / open_safe) * 100.0

    # =========================================================================
    # Close delta
    # =========================================================================

    # close_delta = (close - close.shift()).abs().to_numpy()
    close_delta = np.empty_like(close_np)
    close_delta[0] = np.nan
    close_delta[1:] = np.abs(close_np[1:] - close_np[:-1])

    # =========================================================================
    # Rolling values
    # =========================================================================

    close_max_6 = ta.MAX(close_np, timeperiod=6)
    close_max_12 = ta.MAX(close_np, timeperiod=12)
    close_max_48 = ta.MAX(close_np, timeperiod=48)
    close_min_6 = ta.MIN(close_np, timeperiod=6)
    close_min_12 = ta.MIN(close_np, timeperiod=12)
    close_min_48 = ta.MIN(close_np, timeperiod=48)
    num_empty_288 = ta.SUM((volume_np <= 0).astype(np.float64), timeperiod=288)

    new_cols = pd.DataFrame(
      {
        "RSI_3": rsi_3,
        "RSI_4": rsi_4,
        "RSI_14": rsi_14,
        "RSI_20": rsi_20,
        # "RSI_3_change_pct": rsi_3_change,
        "RSI_14_change_pct": rsi_14_change,
        # "EMA_3": ema_3,
        "EMA_9": ema_9,
        "EMA_12": ema_12,
        "EMA_16": ema_16,
        "EMA_20": ema_20,
        "EMA_26": ema_26,
        "EMA_50": ema_50,
        "EMA_100": ema_100,
        "EMA_200": ema_200,
        "SMA_9": sma_9,
        "SMA_16": sma_16,
        "SMA_21": sma_21,
        "SMA_30": sma_30,
        "SMA_200": sma_200,
        "BBL_20_2.0": bb_lower_20,
        "BBU_20_2.0": bb_upper_20,
        "BBB_20_2.0": ((bb_upper_20 - bb_lower_20) / bb_middle_20_safe) * 100.0,
        "BBL_40_2.0": bb_lower_40,
        # "BBM_40_2.0": bb_middle_40,
        # "BBU_40_2.0": bb_upper_40,
        # "BBB_40_2.0": ((bb_upper_40 - bb_lower_40) / bb_middle_40_safe) * 100.0,
        # "BBP_40_2.0": (close_np - bb_lower_40) / bb_range_40,
        "BBD_40_2.0": np.abs(bb_middle_40 - bb_lower_40),
        "BBT_40_2.0": np.abs(close_np - bb_lower_40),
        "MFI_14": mfi_14,
        "CMF_20": cmf_20,
        "WILLR_14": willr_14,
        "WILLR_480": willr_480,
        "AROONU_14": aroon_up,
        "AROOND_14": aroon_down,
        "STOCHRSIk_14_14_3_3": stochrsi_k,
        "KST_10_15_20_30_10_10_10_15": kst_main,
        "KSTs_9": kst_signal,
        # "OBV": obv,
        # "OBV_change_pct": obv_change,
        "ROC_2": roc_2,
        "ROC_9": roc_9,
        "change_pct": change_pct,
        "close_delta": close_delta,
        "close_max_6": close_max_6,
        "close_max_12": close_max_12,
        "close_max_48": close_max_48,
        "close_min_6": close_min_6,
        "close_min_12": close_min_12,
        "close_min_48": close_min_48,
        "num_empty_288": num_empty_288,
      },
      index=df.index,
    )

    df = pd.concat([df, new_cols], axis=1, copy=False)

    # Enable ONLY during debugging
    debug = False
    if debug:
      debug_cols = [
        "RSI_3",
        "RSI_4",
        "RSI_14",
        "RSI_20",
        # "RSI_3_change_pct",
        "RSI_14_change_pct",
        # "EMA_3",
        "EMA_9",
        "EMA_12",
        "EMA_16",
        "EMA_20",
        "EMA_26",
        "EMA_50",
        "EMA_100",
        "EMA_200",
        "SMA_9",
        "SMA_16",
        "SMA_21",
        "SMA_30",
        "SMA_200",
        "BBL_20_2.0",
        "BBU_20_2.0",
        "BBB_20_2.0",
        "BBL_40_2.0",
        # "BBM_40_2.0",
        # "BBU_40_2.0",
        # "BBB_40_2.0",
        # "BBP_40_2.0",
        "BBD_40_2.0",
        "BBT_40_2.0",
        "MFI_14",
        "CMF_20",
        "WILLR_14",
        "WILLR_480",
        "AROONU_14",
        "AROOND_14",
        "STOCHRSIk_14_14_3_3",
        "KST_10_15_20_30_10_10_10_15",
        "KSTs_9",
        # "OBV",
        # "OBV_change_pct",
        "ROC_2",
        "ROC_9",
        "change_pct",
        "close_delta",
        "close_max_6",
        "close_max_12",
        "close_max_48",
        "close_min_6",
        "close_min_12",
        "close_min_48",
        "num_empty_288",
      ]

      self.validate_indicators(df=df, columns=debug_cols, pair=metadata["pair"], timeframe=self.timeframe)

    # =========================================================================
    # GLOBAL PROTECTIONS
    # =========================================================================

    if self.config["runmode"].value not in ("live", "dry_run"):
      df["bt_agefilter_ok"] = False
      df.loc[df.index > (12 * 24 * self.bt_min_age_days), "bt_agefilter_ok"] = True
    else:
      df["live_data_ok"] = ta.MIN(volume_np, timeperiod=72) > 0

    # =========================================================================
    # LOGGING
    # =========================================================================

    tok = time.perf_counter()

    log.debug("[%s] base_tf_5m_indicators took: %.4f seconds.", metadata["pair"], tok - tik)

    return df

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

  def _btc_info_indicators(self, btc_info_pair: str, btc_info_timeframe: str, metadata: dict) -> DataFrame:
    tik = time.perf_counter()

    # -------------------------------------------------------------------------
    # LOAD DATA
    # -------------------------------------------------------------------------

    df = self.dp.get_pair_dataframe(btc_info_pair, btc_info_timeframe)

    # -------------------------------------------------------------------------
    # OPTIONAL INDICATORS
    # -------------------------------------------------------------------------

    # Example:
    #
    # if btc_info_timeframe == "1d":
    #     df["btc_RSI_14"] = ta.RSI(df, timeperiod=14)

    # -------------------------------------------------------------------------
    # FAST PREFIX RENAME
    # -------------------------------------------------------------------------

    df.rename(
      columns=lambda s: f"btc_{s}" if s != "date" else s,
      inplace=True,
    )

    # -------------------------------------------------------------------------
    # DEBUG TIMER
    # -------------------------------------------------------------------------

    tok = time.perf_counter()

    log.debug("[%s] btc_info_%s_indicators took: %.4f seconds.", metadata["pair"], btc_info_timeframe, tok - tik)

    return df

  def btc_info_switcher(self, btc_info_pair, btc_info_timeframe, metadata: dict) -> DataFrame:
    supported_timeframes = {
      "1d",
      "4h",
      "1h",
      "15m",
      "5m",
    }

    if btc_info_timeframe not in supported_timeframes:
      raise RuntimeError(f"{btc_info_timeframe} not supported as informative timeframe for BTC pair.")

    return self._btc_info_indicators(btc_info_pair, btc_info_timeframe, metadata)

  def populate_indicators(self, df: DataFrame, metadata: dict) -> DataFrame:
    tik = time.perf_counter()

    # =========================================================================
    # CONFIG
    # =========================================================================

    stake_currency = self.config["stake_currency"]
    trading_mode = self.config.get("trading_mode", "")
    is_futures = trading_mode in ("futures", "margin")

    debug = False

    # =========================================================================
    # BTC INFORMATIVE PAIR
    # =========================================================================

    stable_currencies = {
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
    }

    if stake_currency in stable_currencies:
      btc_info_pair = f"BTC/{stake_currency}:{stake_currency}" if is_futures else f"BTC/{stake_currency}"

    else:
      btc_info_pair = "BTC/USDT:USDT" if is_futures else "BTC/USDT"

    # =========================================================================
    # CONSTANTS
    # =========================================================================

    OHLCV_COLS = {"open", "high", "low", "close", "volume"}

    # =========================================================================
    # HELPER
    # =========================================================================

    def prepare_informative(informative: DataFrame, tf: str, keep_ohlcv: set[str] | None = None) -> DataFrame:
      if informative.empty:
        return informative

      keep_ohlcv = keep_ohlcv or set()
      keep_cols = [c for c in informative.columns if (c == "date" or c not in OHLCV_COLS or c in keep_ohlcv)]

      return informative[keep_cols]

    # =========================================================================
    # BTC INFORMATIVE LOOP
    # =========================================================================

    for btc_tf in self.btc_info_timeframes:
      btc_informative = self.btc_info_switcher(
        btc_info_pair,
        btc_tf,
        metadata,
      )

      # ---------------------------------------------------------------------
      # EMPTY CHECK
      # ---------------------------------------------------------------------

      if btc_informative.empty:
        log.warning(f"[{metadata['pair']}] BTC informative {btc_tf} EMPTY!")

        continue

      # ---------------------------------------------------------------------
      # DEBUG
      # ---------------------------------------------------------------------

      if debug:
        if not btc_informative.index.is_monotonic_increasing:
          log.warning(f"[{metadata['pair']}] BTC {btc_tf} index NOT monotonic!")

        if btc_informative.index.has_duplicates:
          log.warning(f"[{metadata['pair']}] BTC {btc_tf} index has DUPLICATES!")

      # ---------------------------------------------------------------------
      # REMOVE UNUSED OHLCV BEFORE MERGE
      # ---------------------------------------------------------------------

      btc_informative = prepare_informative(informative=btc_informative, tf=btc_tf, keep_ohlcv=set())  # Keep none

      # ---------------------------------------------------------------------
      # MERGE
      # ---------------------------------------------------------------------

      df = merge_informative_pair(df, btc_informative, self.timeframe, btc_tf, ffill=False)

      # ---------------------------------------------------------------------
      # CLEANUP
      # ---------------------------------------------------------------------

      merge_date_col = f"date_{btc_tf}"
      if merge_date_col in df.columns:
        df.drop(columns=merge_date_col, inplace=True)

    # =========================================================================
    # INFORMATIVE TF LOOP
    # =========================================================================

    for info_tf in self.info_timeframes:
      info_indicators = self.info_switcher(metadata, info_tf)

      # ---------------------------------------------------------------------
      # EMPTY CHECK
      # ---------------------------------------------------------------------

      if info_indicators.empty:
        if debug:
          log.warning(f"[{metadata['pair']}] {info_tf} informative EMPTY!")

        continue

      # ---------------------------------------------------------------------
      # DEBUG
      # ---------------------------------------------------------------------

      if debug:
        if not info_indicators.index.is_monotonic_increasing:
          log.warning(f"[{metadata['pair']}] {info_tf} index NOT monotonic!")

        if info_indicators.index.has_duplicates:
          log.warning(f"[{metadata['pair']}] {info_tf} index has DUPLICATES!")

        nan_cols = info_indicators.columns[info_indicators.isna().all()].tolist()
        if nan_cols:
          log.warning(f"[{metadata['pair']}] {info_tf} FULL NaN cols: {nan_cols}")

      # ---------------------------------------------------------------------
      # KEEP ONLY REQUIRED OHLCV
      # ---------------------------------------------------------------------

      if info_tf == "15m":
        keep_ohlcv = {"open", "close"}
      else:
        keep_ohlcv = set()

      info_indicators = prepare_informative(informative=info_indicators, tf=info_tf, keep_ohlcv=keep_ohlcv)

      # ---------------------------------------------------------------------
      # MERGE
      # ---------------------------------------------------------------------

      df = merge_informative_pair(df, info_indicators, self.timeframe, info_tf, ffill=False)

      # ---------------------------------------------------------------------
      # CLEANUP
      # ---------------------------------------------------------------------

      merge_date_col = f"date_{info_tf}"
      if merge_date_col in df.columns:
        df.drop(columns=merge_date_col, inplace=True)

    # =========================================================================
    # FINAL FORWARD FILL (ONCE)
    # =========================================================================
    df.ffill(inplace=True)

    # =========================================================================
    # FINAL DEBUG VALIDATION
    # =========================================================================
    if debug:
      if not df.index.is_monotonic_increasing:
        log.warning(f"[{metadata['pair']}] FINAL DF index NOT monotonic!")

      if df.index.has_duplicates:
        log.warning(f"[{metadata['pair']}] FINAL DF index has DUPLICATES!")

      # ---------------------------------------------------------------------
      # FULL NaN COLUMNS
      # ---------------------------------------------------------------------
      full_nan_cols = df.columns[df.isna().all()].tolist()
      if full_nan_cols:
        log.warning(f"[{metadata['pair']}] FINAL DF FULL NaN cols: {full_nan_cols}")

      # ---------------------------------------------------------------------
      # RECENT NaN CHECK
      # ---------------------------------------------------------------------
      recent_df = df.tail(50)

      recent_nan_cols = [col for col in recent_df.columns if recent_df[col].isna().any()]

      if recent_nan_cols:
        log.warning(f"[{metadata['pair']}] FINAL DF recent NaNs: {recent_nan_cols}")

    # =========================================================================
    # BASE TF INDICATORS LAST
    # =========================================================================
    # Base TF indicators may depend on informative columns.
    # Therefore this MUST happen AFTER informative merges.

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
    df["RSI_14_1h"] = df["RSI_14_1h"].fillna(50.0)

    _cmp = build_comparison_cache(df)

    _cmp_cached_0 = _cmp("RSI_3", ">", 1.0)
    _cmp_cached_1 = _cmp("RSI_3_15m", ">", 15.0)
    _cmp_cached_2 = _cmp("RSI_3_1h", ">", 20.0)
    _cmp_cached_3 = _cmp("RSI_3_4h", ">", 20.0)
    _cmp_cached_4 = _cmp("RSI_3_1d", ">", 20.0)
    _cmp_cached_5 = _cmp("RSI_14_1h", "<", 30.0)
    _cmp_cached_6 = _cmp("RSI_14_4h", "<", 30.0)
    _cmp_cached_7 = _cmp("RSI_14_1d", "<", 30.0)
    _cmp_cached_8 = _cmp("CCI_20_1h", "<", -250.0)
    _cmp_cached_9 = _cmp("CCI_20_4h", "<", -200.0)
    _cmp_cached_10 = _cmp("RSI_3_4h", ">", 10.0)
    _cmp_cached_11 = _cmp("RSI_3_1d", ">", 35.0)
    _cmp_cached_12 = _cmp("RSI_14_15m", "<", 30.0)
    _cmp_cached_13 = _cmp("STOCHRSIk_14_14_3_3_15m", "<", 20.0)
    _cmp_cached_14 = _cmp("STOCHRSIk_14_14_3_3_1d", "<", 50.0)
    _cmp_cached_15 = _cmp("RSI_3", ">", 3.0)
    _cmp_cached_16 = _cmp("RSI_14_15m", "<", 40.0)
    _cmp_cached_17 = _cmp("RSI_14_1h", "<", 40.0)
    _cmp_cached_18 = _cmp("RSI_14_4h", "<", 40.0)
    _cmp_cached_19 = _cmp("AROONU_14_15m", "<", 70.0)
    _cmp_cached_20 = _cmp("STOCHRSIk_14_14_3_3_15m", "<", 70.0)
    _cmp_cached_21 = _cmp("RSI_3", ">", 5.0)
    _cmp_cached_22 = _cmp("RSI_3_15m", ">", 10.0)
    _cmp_cached_23 = _cmp("RSI_3_1h", ">", 40.0)
    _cmp_cached_24 = _cmp("RSI_3_4h", ">", 55.0)
    _cmp_cached_25 = _cmp("CMF_20_15m", ">", -0.25)
    _cmp_cached_26 = _cmp("AROONU_14_4h", "<", 60.0)
    _cmp_cached_27 = _cmp("ROC_9_1d", "<", 80.0)
    _cmp_cached_28 = _cmp("RSI_14_1h", "<", 50.0)
    _cmp_cached_29 = _cmp("RSI_14_4h", "<", 50.0)
    _cmp_cached_30 = _cmp("AROONU_14_15m", "<", 40.0)
    _cmp_cached_31 = _cmp("AROONU_14_1h", "<", 85.0)
    _cmp_cached_32 = _cmp("STOCHRSIk_14_14_3_3_1h", "<", 70.0)
    _cmp_cached_33 = _cmp("RSI_3_1h", ">", 45.0)
    _cmp_cached_34 = _cmp("AROONU_14_4h", "<", 80.0)
    _cmp_cached_35 = _cmp("STOCHRSIk_14_14_3_3_4h", "<", 70.0)
    _cmp_cached_36 = _cmp("RSI_3_15m", ">", 30.0)
    _cmp_cached_37 = _cmp("RSI_3_4h", ">", 40.0)
    _cmp_cached_38 = _cmp("AROONU_14_15m", "<", 60.0)
    _cmp_cached_39 = _cmp("STOCHRSIk_14_14_3_3_15m", "<", 50.0)
    _cmp_cached_40 = _cmp("STOCHRSIk_14_14_3_3_4h", "<", 80.0)
    _cmp_cached_41 = _cmp("RSI_3_4h", ">", 30.0)
    _cmp_cached_42 = _cmp("AROONU_14_15m", "<", 50.0)
    _cmp_cached_43 = _cmp("STOCHRSIk_14_14_3_3_15m", "<", 30.0)
    _cmp_cached_44 = _cmp("STOCHRSIk_14_14_3_3_1h", "<", 50.0)
    _cmp_cached_45 = _cmp("RSI_3_1d", ">", 15.0)
    _cmp_cached_46 = _cmp("RSI_3", ">", 10.0)
    _cmp_cached_47 = _cmp("RSI_3_15m", ">", 20.0)
    _cmp_cached_48 = _cmp("RSI_3_4h", ">", 45.0)
    _cmp_cached_49 = _cmp("STOCHRSIk_14_14_3_3_15m", "<", 60.0)
    _cmp_cached_50 = _cmp("AROONU_14_4h", "<", 70.0)
    _cmp_cached_51 = _cmp("RSI_3_1h", ">", 50.0)
    _cmp_cached_52 = _cmp("RSI_3_4h", ">", 50.0)
    _cmp_cached_53 = _cmp("RSI_3_15m", ">", 25.0)
    _cmp_cached_54 = _cmp("RSI_3_1h", ">", 55.0)
    _cmp_cached_55 = _cmp("RSI_14_4h", "<", 70.0)
    _cmp_cached_56 = _cmp("AROONU_14_1h", "<", 20.0)
    _cmp_cached_57 = _cmp("ROC_9_4h", "<", 80.0)
    _cmp_cached_58 = _cmp("RSI_3_1h", ">", 65.0)
    _cmp_cached_59 = _cmp("RSI_3_1d", ">", 25.0)
    _cmp_cached_60 = _cmp("CMF_20_1d", ">", -0.20)
    _cmp_cached_61 = _cmp("STOCHRSIk_14_14_3_3_4h", "<", 50.0)
    _cmp_cached_62 = _cmp("ROC_9_1d", ">", -15.0)
    _cmp_cached_63 = _cmp("RSI_3_4h", ">", 25.0)
    _cmp_cached_64 = _cmp("RSI_3_1h", ">", 35.0)
    _cmp_cached_65 = _cmp("RSI_3", ">", 15.0)
    _cmp_cached_66 = _cmp("RSI_3_1h", ">", 60.0)
    _cmp_cached_67 = _cmp("RSI_14_1h", "<", 60.0)
    _cmp_cached_68 = _cmp("RSI_14_4h", "<", 60.0)
    _cmp_cached_69 = _cmp("ROC_9_4h", "<", 30.0)
    _cmp_cached_70 = _cmp("RSI_3_15m", ">", 3.0)
    _cmp_cached_71 = _cmp("RSI_3_1h", ">", 3.0)
    _cmp_cached_72 = _cmp("AROONU_14_1h", "<", 50.0)
    _cmp_cached_73 = _cmp("ROC_9_15m", ">", -10.0)
    _cmp_cached_74 = _cmp("ROC_9_1h", ">", -15.0)
    _cmp_cached_75 = _cmp("RSI_3_1h", ">", 5.0)
    _cmp_cached_76 = _cmp("CMF_20_15m", ">", -0.20)
    _cmp_cached_77 = _cmp("STOCHRSIk_14_14_3_3_4h", "<", 30.0)
    _cmp_cached_78 = _cmp("RSI_3_1h", ">", 10.0)
    _cmp_cached_79 = _cmp("RSI_3_4h", ">", 15.0)
    _cmp_cached_80 = _cmp("CMF_20_15m", ">", -0.30)
    _cmp_cached_81 = _cmp("AROONU_14_4h", "<", 20.0)
    _cmp_cached_82 = _cmp("STOCHRSIk_14_14_3_3_1h", "<", 20.0)
    _cmp_cached_83 = _cmp("RSI_3_4h", ">", 35.0)
    _cmp_cached_84 = _cmp("ROC_9_4h", "<", 15.0)
    _cmp_cached_85 = _cmp("CMF_20_1h", ">", -0.20)
    _cmp_cached_86 = _cmp("STOCHRSIk_14_14_3_3_1h", "<", 30.0)
    _cmp_cached_87 = _cmp("CMF_20_1h", ">", -0.30)
    _cmp_cached_88 = _cmp("AROONU_14_4h", "<", 40.0)
    _cmp_cached_89 = _cmp("RSI_3_1h", ">", 15.0)
    _cmp_cached_90 = _cmp("AROONU_14_4h", "<", 25.0)
    _cmp_cached_91 = _cmp("AROONU_14_15m", "<", 25.0)
    _cmp_cached_92 = _cmp("RSI_14_1h", "<", 20.0)
    _cmp_cached_93 = _cmp("RSI_14_4h", "<", 20.0)
    _cmp_cached_94 = _cmp("CMF_20_1h", ">", -0.25)
    _cmp_cached_95 = _cmp("CMF_20_4h", ">", -0.25)
    _cmp_cached_96 = _cmp("RSI_3_1h", ">", 30.0)
    _cmp_cached_97 = _cmp("RSI_3_1d", ">", 50.0)
    _cmp_cached_98 = _cmp("CCI_20_4h", "<", -250.0)
    _cmp_cached_99 = _cmp("CMF_20_4h", ">", -0.30)
    _cmp_cached_100 = _cmp("AROONU_14_15m", "<", 20.0)
    _cmp_cached_101 = _cmp("AROONU_14_1h", "<", 30.0)
    _cmp_cached_102 = _cmp("RSI_14_15m", "<", 20.0)
    _cmp_cached_103 = _cmp("AROONU_14_1h", "<", 90.0)
    _cmp_cached_104 = _cmp("STOCHRSIk_14_14_3_3_1h", "<", 90.0)
    _cmp_cached_105 = _cmp("RSI_3_15m", ">", 5.0)
    _cmp_cached_106 = _cmp("CMF_20_15m", ">", -0.15)
    _cmp_cached_107 = _cmp("CMF_20_1h", ">", -0.15)
    _cmp_cached_108 = _cmp("CMF_20_4h", ">", -0.15)
    _cmp_cached_109 = _cmp("ROC_9_4h", ">", -20.0)
    _cmp_cached_110 = _cmp("CMF_20_4h", ">", -0.10)
    _cmp_cached_111 = _cmp("AROONU_14_1h", "<", 40.0)
    _cmp_cached_112 = _cmp("ROC_9_15m", ">", -15.0)
    _cmp_cached_113 = _cmp("STOCHRSIk_14_14_3_3_4h", "<", 20.0)
    _cmp_cached_114 = _cmp("CMF_20_15m", ">", -0.40)
    _cmp_cached_115 = _cmp("CMF_20_1h", ">", -0.40)
    _cmp_cached_116 = _cmp("STOCHRSIk_14_14_3_3_4h", "<", 10.0)
    _cmp_cached_117 = _cmp("RSI_3_1d", ">", 30.0)
    _cmp_cached_118 = _cmp("STOCHRSIk_14_14_3_3_15m", "<", 10.0)
    _cmp_cached_119 = _cmp("ROC_9_1h", ">", -10.0)
    _cmp_cached_120 = _cmp("RSI_3_1d", ">", 40.0)
    _cmp_cached_121 = _cmp("ROC_9_1d", "<", 100.0)
    _cmp_cached_122 = _cmp("CMF_20_4h", ">", -0.20)
    _cmp_cached_123 = _cmp("CMF_20_15m", ">", -0.10)
    _cmp_cached_124 = _cmp("AROONU_14_4h", "<", 50.0)
    _cmp_cached_125 = _cmp("RSI_3_1d", ">", 55.0)
    _cmp_cached_126 = _cmp("ROC_9_4h", "<", 10.0)
    _cmp_cached_127 = _cmp("STOCHRSIk_14_14_3_3_4h", "<", 90.0)
    _cmp_cached_128 = _cmp("AROONU_14_1h", "<", 80.0)
    _cmp_cached_129 = _cmp("STOCHRSIk_14_14_3_3_1d", "<", 90.0)
    _cmp_cached_130 = _cmp("AROONU_14_4h", "<", 100.0)
    _cmp_cached_131 = _cmp("RSI_3_1d", ">", 5.0)
    _cmp_cached_132 = _cmp("ROC_9_4h", "<", 25.0)
    _cmp_cached_133 = _cmp("RSI_3_1h", ">", 25.0)
    _cmp_cached_134 = _cmp("AROONU_14_1h", "<", 70.0)
    _cmp_cached_135 = _cmp("ROC_9_4h", ">", -40.0)
    _cmp_cached_136 = _cmp("RSI_3_4h", ">", 60.0)
    _cmp_cached_137 = _cmp("ROC_9_1d", "<", 70.0)
    _cmp_cached_138 = _cmp("ROC_9_1d", "<", 60.0)
    _cmp_cached_139 = _cmp("RSI_14_15m", "<", 10.0)
    _cmp_cached_140 = _cmp("AROONU_14_15m", "<", 30.0)
    _cmp_cached_141 = _cmp("RSI_14_4h", "<", 80.0)
    _cmp_cached_142 = _cmp("AROONU_14_1h", "<", 75.0)
    _cmp_cached_143 = _cmp("AROONU_14_4h", "<", 90.0)
    _cmp_cached_144 = _cmp("ROC_9_1h", "<", 10.0)
    _cmp_cached_145 = _cmp("RSI_3_4h", ">", 65.0)
    _cmp_cached_146 = _cmp("ROC_9_1d", "<", 20.0)
    _cmp_cached_147 = _cmp("RSI_14_1h", "<", 10.0)
    _cmp_cached_148 = _cmp("ROC_9_1h", ">", -20.0)
    _cmp_cached_149 = _cmp("AROONU_14_4h", "<", 30.0)
    _cmp_cached_150 = _cmp("STOCHRSIk_14_14_3_3_15m", "<", 40.0)
    _cmp_cached_151 = _cmp("ROC_9_1d", "<", 200.0)
    _cmp_cached_152 = _cmp("ROC_9_4h", "<", 40.0)
    _cmp_cached_153 = _cmp("CMF_20_1h", ">", -0.4)
    _cmp_cached_154 = _cmp("CCI_20_1h", "<", -200.0)
    _cmp_cached_155 = _cmp("CCI_20_4h", "<", -0.0)
    _cmp_cached_156 = _cmp("ROC_9_1d", "<", 30.0)
    _cmp_cached_157 = _cmp("AROONU_14_1h", "<", 60.0)
    _cmp_cached_158 = _cmp("RSI_3_1d", ">", 45.0)
    _cmp_cached_159 = _cmp("ROC_9_1d", "<", 50.0)
    _cmp_cached_160 = _cmp("STOCHRSIk_14_14_3_3_1h", "<", 40.0)
    _cmp_cached_161 = _cmp("STOCHRSIk_14_14_3_3_4h", "<", 40.0)
    _cmp_cached_162 = _cmp("ROC_9_4h", ">", -10.0)
    _cmp_cached_163 = _cmp("ROC_9_1d", "<", 25.0)
    _cmp_cached_164 = _cmp("RSI_3_1d", ">", 60.0)
    _cmp_cached_165 = _cmp("AROONU_14_1d", "<", 70.0)
    _cmp_cached_166 = _cmp("AROONU_14_1h", "<", 25.0)
    _cmp_cached_167 = _cmp("ROC_9_4h", ">", -30.0)
    _cmp_cached_168 = _cmp("RSI_14_1h", "<", 45.0)
    _cmp_cached_169 = _cmp("RSI_14_4h", "<", 55.0)
    _cmp_cached_170 = _cmp("CMF_20_1d", ">", -0.3)
    _cmp_cached_171 = _cmp("RSI_14_1h", "<", 35.0)
    _cmp_cached_172 = _cmp("STOCHRSIk_14_14_3_3_4h", "<", 85.0)
    _cmp_cached_173 = _cmp("STOCHRSIk_14_14_3_3_4h", "<", 60.0)
    _cmp_cached_174 = _cmp("CMF_20_1h", ">", -0.10)
    _cmp_cached_175 = _cmp("AROONU_14_15m", "<", 10.0)
    _cmp_cached_176 = _cmp("ROC_9_1d", ">", -50.0)
    _cmp_cached_177 = _cmp("CMF_20_15m", ">", -0.3)
    _cmp_cached_178 = _cmp("AROONU_14_1d", "<", 90.0)
    _cmp_cached_179 = _cmp("STOCHRSIk_14_14_3_3_1d", "<", 80.0)
    _cmp_cached_180 = _cmp("ROC_9_4h", "<", 20.0)
    _cmp_cached_181 = _cmp("RSI_14_1h", "<", 70.0)
    _cmp_cached_182 = _cmp("ROC_9_1h", "<", 20.0)
    _cmp_cached_183 = _cmp("ROC_9_4h", "<", 50.0)
    _cmp_cached_184 = _cmp("CMF_20_1h", ">", -0.0)
    _cmp_cached_185 = _cmp("CMF_20_4h", ">", -0.4)
    _cmp_cached_186 = _cmp("CMF_20_4h", ">", -0.0)
    _cmp_cached_187 = _cmp("STOCHRSIk_14_14_3_3_1h", "<", 80.0)
    _cmp_cached_188 = _cmp("AROONU_14_15m", "<", 80.0)
    _cmp_cached_189 = _cmp("AROONU_14_4h", "<", 85.0)
    _cmp_cached_190 = _cmp("ROC_9_4h", "<", 100.0)
    _cmp_cached_191 = _cmp("ROC_9_4h", ">", -25.0)
    _cmp_cached_192 = _cmp("ROC_9_1h", "<", 30.0)
    _cmp_cached_193 = _cmp("ROC_9_4h", ">", -35.0)
    _cmp_cached_194 = _cmp("ROC_9_1d", ">", -40.0)
    _cmp_cached_195 = _cmp("RSI_14_15m", ">", 20.0)
    _cmp_cached_196 = _cmp("RSI_14_4h", "<", 45.0)
    _cmp_cached_197 = _cmp("ROC_9_1h", ">", -30.0)
    _cmp_cached_198 = _cmp("ROC_9_1d", "<", 150.0)
    _cmp_cached_199 = _cmp("CMF_20_15m", ">", -0.50)
    _cmp_cached_200 = _cmp("RSI_14_15m", "<", 25.0)
    _cmp_cached_201 = _cmp("RSI_14_1h", "<", 25.0)
    _cmp_cached_202 = _cmp("RSI_14_4h", "<", 25.0)
    _cmp_cached_203 = _cmp("ROC_9_4h", ">", -15.0)
    _cmp_cached_204 = _cmp("ROC_9_4h", "<", 70.0)
    _cmp_cached_205 = _cmp("CMF_20_1d", ">", -0.10)
    _cmp_cached_206 = _cmp("RSI_14_1d", "<", 40.0)
    _cmp_cached_207 = _cmp("ROC_9_1d", ">", -20.0)
    _cmp_cached_208 = _cmp("CMF_20_1d", ">", -0.1)
    _cmp_cached_209 = _cmp("RSI_14_4h", "<", 35.0)
    _cmp_cached_210 = _cmp("ROC_9_1d", ">", -25.0)
    _cmp_cached_211 = _cmp("RSI_14_4h", "<", 65.0)
    _cmp_cached_212 = _cmp("ROC_9_4h", "<", 35.0)
    _cmp_cached_213 = _cmp("ROC_9_1h", "<", 15.0)
    _cmp_cached_214 = _cmp("RSI_3_4h", ">", 3.0)
    _cmp_cached_215 = _cmp("RSI_3_4h", ">", 5.0)
    _cmp_cached_216 = _cmp("RSI_14_4h", "<", 10.0)
    _cmp_cached_217 = _cmp("RSI_14_15m", ">", 25.0)
    _cmp_cached_218 = _cmp("RSI_3_4h", ">", 20)
    _cmp_cached_219 = _cmp("AROONU_14_1h", "<", 100.0)
    _cmp_cached_220 = _cmp("RSI_14_15m", "<", 35.0)
    _cmp_cached_221 = _cmp("ROC_9_1d", "<", 250.0)
    _cmp_cached_222 = _cmp("ROC_9_1h", "<", 40.0)
    _cmp_cached_223 = _cmp("ROC_9_4h", ">", -50.0)
    _cmp_cached_224 = _cmp("AROONU_14_15m", "<", 75.0)
    _cmp_cached_225 = _cmp("ROC_9_1h", "<", 50.0)
    _cmp_cached_226 = _cmp("STOCHRSIk_14_14_3_3_1h", "<", 15.0)
    _cmp_cached_227 = _cmp("STOCHRSIk_14_14_3_3_4h", "<", 15.0)
    _cmp_cached_228 = _cmp("CCI_20_1h", "<", -350.0)
    _cmp_cached_229 = _cmp("RSI_14_1d", "<", 50.0)
    _cmp_cached_230 = _cmp("CMF_20_1d", ">", -0.0)
    _cmp_cached_231 = _cmp("MFI_14_1d", "<", 70.0)
    _cmp_cached_232 = _cmp("ROC_9_1d", "<", 15.0)
    _cmp_cached_233 = _cmp("ROC_9_4h", ">", -70.0)
    _cmp_cached_234 = _cmp("ROC_9_1d", "<", 40.0)
    _cmp_cached_235 = _cmp("MFI_14_1d", "<", 50.0)
    _cmp_cached_236 = _cmp("CMF_20_4h", ">", -0.40)
    _cmp_cached_237 = _cmp("CCI_20_1h", "<", 0.0)
    _cmp_cached_238 = _cmp("CCI_20_4h", "<", 0.0)
    _cmp_cached_239 = _cmp("ROC_9_1d", ">", -30.0)
    _cmp_cached_240 = _cmp("AROONU_14_4h", "<", 75.0)
    _cmp_cached_241 = _cmp("ROC_9_1h", "<", 80.0)
    _cmp_cached_242 = _cmp("RSI_14_4h", "<", 75.0)
    _cmp_cached_243 = _cmp("ROC_9_4h", "<", 75.0)
    _cmp_cached_244 = _cmp("RSI_14_15m", "<", 50.0)
    _cmp_cached_245 = _cmp("RSI_3_1d", ">", 65.0)
    _cmp_cached_246 = _cmp("CMF_20_4h", ">", -0.1)
    _cmp_cached_247 = _cmp("ROC_2_1d", ">", -20.0)
    _cmp_cached_248 = _cmp("ROC_9_4h", "<", 60.0)
    _cmp_cached_249 = _cmp("ROC_9_15m", ">", -40.0)
    _cmp_cached_250 = _cmp("STOCHRSIk_14_14_3_3_1h", "<", 60.0)
    _cmp_cached_251 = _cmp("ROC_9_4h", "<", 120.0)
    _cmp_cached_252 = _cmp("MFI_14_1h", "<", 40.0)
    _cmp_cached_253 = _cmp("MFI_14_4h", "<", 50.0)
    _cmp_cached_254 = _cmp("AROONU_14_1h", "<", 10.0)
    _cmp_cached_255 = _cmp("CMF_20_15m", ">", -0.35)
    _cmp_cached_256 = _cmp("CCI_20_1h", "<", -100.0)
    _cmp_cached_257 = _cmp("STOCHRSIk_14_14_3_3_15m", "<", 80.0)
    _cmp_cached_258 = _cmp("ROC_9_4h", "<", 130.0)
    _cmp_cached_259 = _cmp("RSI_3_15m", ">", 35.0)
    _cmp_cached_260 = _cmp("STOCHk_14_3_3_1h", "<", 60.0)
    _cmp_cached_261 = _cmp("STOCHk_14_3_3_4h", "<", 90.0)
    _cmp_cached_262 = _cmp("STOCHRSIk_14_14_3_3_15m", "<", 90.0)
    _cmp_cached_263 = _cmp("ROC_9_1d", "<", 75.0)
    _cmp_cached_264 = _cmp("RSI_3_15m", ">", 40.0)
    _cmp_cached_265 = _cmp("CMF_20_1d", ">", -0.40)
    _cmp_cached_266 = _cmp("ROC_9_1h", ">", -25.0)
    _cmp_cached_267 = _cmp("RSI_14_4h", "<", 90.0)
    _cmp_cached_268 = _cmp("ROC_9_15m", "<", 10.0)
    _cmp_cached_269 = _cmp("ROC_9_1h", "<", 70.0)
    _cmp_cached_270 = _cmp("RSI_3_15m", ">", 45.0)
    _cmp_cached_271 = _cmp("CMF_20_1d", ">", -0.30)
    _cmp_cached_272 = _cmp("ROC_9_15m", "<", 20.0)
    _cmp_cached_273 = _cmp("CMF_20_4h", ">", -0.35)
    _cmp_cached_274 = _cmp("RSI_3_15m", ">", 55.0)
    _cmp_cached_275 = _cmp("RSI_3_1d", ">", 10.0)
    _cmp_cached_276 = _cmp("AROONU_14_1d", "<", 25.0)
    _cmp_cached_277 = _cmp("CMF_20_1h", ">", -0.5)
    _cmp_cached_278 = _cmp("CMF_20_4h", ">", -0.5)
    _cmp_cached_279 = _cmp("CMF_20_15m", ">", -0.0)
    _cmp_cached_280 = _cmp("CMF_20_15m", ">", -0.5)
    _cmp_cached_281 = _cmp("CMF_20_1h", ">", -0.3)
    _cmp_cached_282 = _cmp("CMF_20_4h", ">", -0.3)
    _cmp_cached_283 = _cmp("ROC_9_4h", "<", 300.0)
    _cmp_cached_284 = _cmp("CCI_20_change_pct_4h", ">", 0.0)
    _cmp_cached_285 = _cmp("ROC_9_4h", ">", -60.0)
    _cmp_cached_286 = _cmp("RSI_3_1d", ">", 3.0)
    _cmp_cached_287 = _cmp("ROC_2_1d", ">", -40.0)
    _cmp_cached_288 = _cmp("ROC_9_1h", ">", -60.0)
    _cmp_cached_289 = _cmp("CMF_20_4h", ">", -0.2)
    _cmp_cached_290 = _cmp("ROC_9_4h", "<", 250.0)
    _cmp_cached_291 = _cmp("change_pct_4h", ">", -30.0)
    _cmp_cached_292 = _cmp("change_pct_4h", ">", -5.0)
    _cmp_cached_293 = _cmp("change_pct_4h", "<", 10.0)
    _cmp_cached_294 = _cmp("top_wick_pct_4h", "<", 10.0)
    _cmp_cached_295 = _cmp("change_pct_4h", "<", 15.0)
    _cmp_cached_296 = _cmp("top_wick_pct_4h", "<", 15.0)
    _cmp_cached_297 = _cmp("change_pct_1d", ">", -40.0)
    _cmp_cached_298 = _cmp("change_pct_1d", ">", -20.0)
    _cmp_cached_299 = _cmp("AROONU_14_1d", "<", 85.0)
    _cmp_cached_300 = _cmp("change_pct_1d", ">", -15.0)
    _cmp_cached_301 = _cmp("RSI_3_15m", ">", 50.0)
    _cmp_cached_302 = _cmp("change_pct_1d", ">", -10.0)
    _cmp_cached_303 = _cmp("top_wick_pct_1d", "<", 10.0)
    _cmp_cached_304 = _cmp("CMF_20_1h", ">", -0.2)
    _cmp_cached_305 = _cmp("change_pct_1d", ">", -5.0)
    _cmp_cached_306 = _cmp("change_pct_1d", "<", 10.0)
    _cmp_cached_307 = _cmp("change_pct_1d", "<", 20.0)
    _cmp_cached_308 = _cmp("top_wick_pct_1d", "<", 20.0)
    _cmp_cached_309 = _cmp("change_pct_1d", "<", 25.0)
    _cmp_cached_310 = _cmp("top_wick_pct_1d", "<", 25.0)
    _cmp_cached_311 = _cmp("change_pct_1d", "<", 30.0)
    _cmp_cached_312 = _cmp("RSI_3_4h", ">", 70.0)
    _cmp_cached_313 = _cmp("top_wick_pct_1d", "<", 30.0)
    _cmp_cached_314 = _cmp("change_pct_1d", "<", 50.0)
    _cmp_cached_315 = _cmp("top_wick_pct_1d", "<", 50.0)
    _cmp_cached_316 = _cmp("top_wick_pct_4h", "<", 20.0)
    _cmp_cached_317 = _cmp("CMF_20_15m", ">", -0.2)
    _cmp_cached_318 = _cmp("top_wick_pct_1d", "<", 80.0)
    _cmp_cached_319 = _cmp("ROC_9_1h", ">", -50.0)
    _cmp_cached_320 = _cmp("AROONU_14_1d", "<", 80.0)
    _cmp_cached_321 = _cmp("CMF_20_1d", ">", -0.50)
    _cmp_cached_322 = _cmp("AROONU_14_1d", "<", 50.0)
    _cmp_cached_323 = _cmp("RSI_14_1h", "<", 15.0)
    _cmp_cached_324 = _cmp("CCI_20_1h", "<", -150.0)
    _cmp_cached_325 = _cmp("ROC_2_1d", ">", -25.0)
    _cmp_cached_326 = _cmp("ROC_9_1d", ">", -60.0)
    _cmp_cached_327 = _cmp("STOCHRSIk_14_14_3_3_1h", "<", 85.0)
    tok_before_protections = time.perf_counter()

    # Global protections Long
    df["protections_long_global"] = (
      # 5m & 15m & 1h & 4h & 1d down move, 1h & 4h & 1d still not low enough
      (
        (_cmp_cached_0)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_3)
        | (_cmp_cached_4)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_7)
        | (_cmp_cached_8)
        | (_cmp_cached_9)
      )
      # 5m & 4h & 1d down move, 15m & 1h & 4h still not low enough, 1d still high
      & (
        (_cmp_cached_0)
        | (_cmp_cached_10)
        | (_cmp_cached_11)
        | (_cmp_cached_12)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_13)
        | (_cmp_cached_14)
      )
      # 5m down move, 15m & 1h & 4h still high, 15m high
      & (
        (_cmp_cached_15)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_19)
        | (_cmp_cached_20)
      )
      # 1h & 4h down move, 15m & 1h & 4h downtrend, 1h still high
      & (
        (_cmp_cached_21)
        | (_cmp_cached_22)
        | (_cmp_cached_23)
        | (_cmp_cached_24)
        | (_cmp_cached_25)
        | (_cmp_cached_26)
        | (_cmp_cached_27)
      )
      # 5m & 15m & 1h down move, 1h & 4h still high, 15m still high, 1h high
      & (
        (_cmp_cached_21)
        | (_cmp_cached_22)
        | (_cmp_cached_23)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_30)
        | (_cmp_cached_31)
        | (_cmp_cached_32)
      )
      # 5m & 15m & 1h & 4h down move, 4h high
      & (
        (_cmp_cached_21)
        | (_cmp_cached_1)
        | (_cmp_cached_33)
        | (_cmp_cached_24)
        | (_cmp_cached_29)
        | (_cmp_cached_34)
        | (_cmp_cached_35)
      )
      # 5m & 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 15m & 4h high
      & (
        (_cmp_cached_21)
        | (_cmp_cached_36)
        | (_cmp_cached_23)
        | (_cmp_cached_37)
        | (_cmp_cached_12)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_38)
        | (_cmp_cached_39)
        | (_cmp_cached_40)
      )
      # 5m & 15m & 4h down move, 15m & 1h & 4h still high, 15m & 1h still high
      & (
        (_cmp_cached_21)
        | (_cmp_cached_36)
        | (_cmp_cached_41)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_42)
        | (_cmp_cached_43)
        | (_cmp_cached_44)
      )
      # 5m & 4h & 1d down move, 15m high
      & (
        (_cmp_cached_21)
        | (_cmp_cached_10)
        | (_cmp_cached_45)
        | (_cmp_cached_38)
        | (_cmp_cached_20)
      )
      # 5m & 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h stil high, 15m & 4h high
      & (
        (_cmp_cached_46)
        | (_cmp_cached_47)
        | (_cmp_cached_33)
        | (_cmp_cached_48)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_49)
        | (_cmp_cached_35)
      )
      # 5m & 15m & 1h & 4h down move, 15m & 1h & 4h still high, 15m & 4h high
      & (
        (_cmp_cached_46)
        | (_cmp_cached_47)
        | (_cmp_cached_33)
        | (_cmp_cached_48)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_38)
        | (_cmp_cached_50)
        | (_cmp_cached_39)
      )
      # 5m & 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 15m high
      & (
        (_cmp_cached_46)
        | (_cmp_cached_47)
        | (_cmp_cached_51)
        | (_cmp_cached_52)
        | (_cmp_cached_12)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_38)
        | (_cmp_cached_49)
      )
      # 5m & 15m & 1h down move, 15m & 1h still high, 4h high, 15m still not low enough, 5h overbought
      & (
        (_cmp_cached_46)
        | (_cmp_cached_53)
        | (_cmp_cached_54)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_55)
        | (_cmp_cached_56)
        | (_cmp_cached_34)
        | (_cmp_cached_13)
        | (_cmp_cached_57)
      )
      # 5m & 15m & 1h & 1d down move, 1h & 4h still high, 1d downtrend
      & (
        (_cmp_cached_46)
        | (_cmp_cached_53)
        | (_cmp_cached_58)
        | (_cmp_cached_59)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_60)
        | (_cmp_cached_44)
        | (_cmp_cached_61)
        | (_cmp_cached_62)
      )
      # 5m & 15m & 4h down move, 15m & 1h still not low enough, 4h still high, 15m & 4h high
      & (
        (_cmp_cached_46)
        | (_cmp_cached_53)
        | (_cmp_cached_63)
        | (_cmp_cached_12)
        | (_cmp_cached_5)
        | (_cmp_cached_18)
        | (_cmp_cached_38)
        | (_cmp_cached_26)
        | (_cmp_cached_49)
      )
      # 5m & 15m & 1h down move, 15m still not low enough, 1h still high, 4h high, 15m & 4h high
      & (
        (_cmp_cached_46)
        | (_cmp_cached_36)
        | (_cmp_cached_64)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_55)
        | (_cmp_cached_38)
        | (_cmp_cached_26)
        | (_cmp_cached_43)
        | (_cmp_cached_61)
      )
      # 5m & 15m & 1h down move, 15m still high, 1h & 4h high, 4h high & overbought
      & (
        (_cmp_cached_65)
        | (_cmp_cached_36)
        | (_cmp_cached_66)
        | (_cmp_cached_16)
        | (_cmp_cached_67)
        | (_cmp_cached_68)
        | (_cmp_cached_30)
        | (_cmp_cached_34)
        | (_cmp_cached_13)
        | (_cmp_cached_40)
        | (_cmp_cached_69)
      )
      # 15m & 1h & 4h down move, 1h still high, 15m & 1h downtrend
      & (
        (_cmp_cached_70)
        | (_cmp_cached_71)
        | (_cmp_cached_3)
        | (_cmp_cached_72)
        | (_cmp_cached_73)
        | (_cmp_cached_74)
      )
      # 15m & 1h & 4h down move, 15m downtrend, 1h still high, 4h still not low enough
      & (
        (_cmp_cached_70)
        | (_cmp_cached_75)
        | (_cmp_cached_41)
        | (_cmp_cached_76)
        | (_cmp_cached_72)
        | (_cmp_cached_77)
      )
      # 15m & 1h & 4h down move, 15m downtrend, 1h & 4h still not low enough
      & (
        (_cmp_cached_70)
        | (_cmp_cached_78)
        | (_cmp_cached_79)
        | (_cmp_cached_80)
        | (_cmp_cached_56)
        | (_cmp_cached_81)
      )
      # 15m & 1h & 4h down move, 15m downtrend, 15m & 1h still not low enough
      & (
        (_cmp_cached_70)
        | (_cmp_cached_78)
        | (_cmp_cached_79)
        | (_cmp_cached_80)
        | (_cmp_cached_13)
        | (_cmp_cached_82)
      )
      # 15m & 1h & 4h down move, 1h & 4h still high, 15m downtrend, 4h overbought
      & (
        (_cmp_cached_70)
        | (_cmp_cached_78)
        | (_cmp_cached_83)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_76)
        | (_cmp_cached_84)
      )
      # 15m & 1h & 4h down move, 15m & 1h downtrend, 1h & 4h still not low enough
      & (
        (_cmp_cached_70)
        | (_cmp_cached_78)
        | (_cmp_cached_37)
        | (_cmp_cached_76)
        | (_cmp_cached_85)
        | (_cmp_cached_86)
        | (_cmp_cached_77)
      )
      # 15m & 1h & 4h down move, 4h still high, 1h downtrend, 4h still high
      & (
        (_cmp_cached_70)
        | (_cmp_cached_78)
        | (_cmp_cached_48)
        | (_cmp_cached_18)
        | (_cmp_cached_87)
        | (_cmp_cached_88)
      )
      # 15m & 1h & 4h down move, 1h & 4h still not low enough, 15m downtrend
      & (
        (_cmp_cached_70)
        | (_cmp_cached_89)
        | (_cmp_cached_63)
        | (_cmp_cached_5)
        | (_cmp_cached_18)
        | (_cmp_cached_25)
        | (_cmp_cached_90)
      )
      # 15m & 1h & 4h down move, 1h & 4h still not low enough, 15m still not low enough
      & (
        (_cmp_cached_70)
        | (_cmp_cached_89)
        | (_cmp_cached_48)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_91)
      )
      # 15m & 1h & 4h down move, 1h & 4h still not low enough, 15m & 1h & 4h downtrend, 1h still not low enough
      & (
        (_cmp_cached_70)
        | (_cmp_cached_2)
        | (_cmp_cached_3)
        | (_cmp_cached_92)
        | (_cmp_cached_93)
        | (_cmp_cached_76)
        | (_cmp_cached_94)
        | (_cmp_cached_95)
        | (_cmp_cached_86)
      )
      # 15m & 1h & 4h & 1d down move, 1h still high, 1h & 4h still not low enough
      & (
        (_cmp_cached_70)
        | (_cmp_cached_96)
        | (_cmp_cached_41)
        | (_cmp_cached_97)
        | (_cmp_cached_72)
        | (_cmp_cached_8)
        | (_cmp_cached_98)
      )
      # 15m & 1h & 4h down move, 4h downtrend, 15m & 1h still not low enough
      & (
        (_cmp_cached_70)
        | (_cmp_cached_51)
        | (_cmp_cached_52)
        | (_cmp_cached_99)
        | (_cmp_cached_100)
        | (_cmp_cached_101)
      )
      # 15m & 4h down move, 15m & 1h & 4h still not low enough, 1h still not low enough
      & (
        (_cmp_cached_70)
        | (_cmp_cached_10)
        | (_cmp_cached_102)
        | (_cmp_cached_92)
        | (_cmp_cached_93)
        | (_cmp_cached_86)
      )
      # 15m & 4h down move, 1h & 4h still high, 15m still not low enough, 1h still high
      & (
        (_cmp_cached_70)
        | (_cmp_cached_41)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_91)
        | (_cmp_cached_44)
      )
      # 15m down move, 15m & 1h high
      & (
        (_cmp_cached_70)
        | (_cmp_cached_19)
        | (_cmp_cached_103)
        | (_cmp_cached_39)
        | (_cmp_cached_104)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h downtrend, 1h & 4h still not low enough, 4h downtrend
      & (
        (_cmp_cached_105)
        | (_cmp_cached_75)
        | (_cmp_cached_3)
        | (_cmp_cached_106)
        | (_cmp_cached_107)
        | (_cmp_cached_108)
        | (_cmp_cached_56)
        | (_cmp_cached_81)
        | (_cmp_cached_109)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h downtrend, 1h still high, 15m still not low enough, 15m & 1h downtrend
      & (
        (_cmp_cached_105)
        | (_cmp_cached_75)
        | (_cmp_cached_3)
        | (_cmp_cached_76)
        | (_cmp_cached_107)
        | (_cmp_cached_110)
        | (_cmp_cached_111)
        | (_cmp_cached_43)
        | (_cmp_cached_112)
        | (_cmp_cached_74)
      )
      # 15m & 1h & 4h down move, 15m & 1h downtrend, 15m & 4h still not low enough
      & (
        (_cmp_cached_105)
        | (_cmp_cached_75)
        | (_cmp_cached_3)
        | (_cmp_cached_76)
        | (_cmp_cached_94)
        | (_cmp_cached_13)
        | (_cmp_cached_113)
      )
      # 15m & 1h & 4h down move, 15m & 1h downtrend, 15m still not low enough
      & (
        (_cmp_cached_105)
        | (_cmp_cached_75)
        | (_cmp_cached_3)
        | (_cmp_cached_114)
        | (_cmp_cached_115)
        | (_cmp_cached_13)
      )
      # 5m & 1h & 4h down move, 1h & 4h downtrend, 15m still high, 4h still not low enough
      & (
        (_cmp_cached_105)
        | (_cmp_cached_75)
        | (_cmp_cached_3)
        | (_cmp_cached_85)
        | (_cmp_cached_95)
        | (_cmp_cached_39)
        | (_cmp_cached_116)
      )
      # 15m & 1h & 4h & 1d down move, 15m downtrend, 15m still not low enough, 1h downtrend
      & (
        (_cmp_cached_105)
        | (_cmp_cached_75)
        | (_cmp_cached_63)
        | (_cmp_cached_117)
        | (_cmp_cached_76)
        | (_cmp_cached_118)
        | (_cmp_cached_119)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h downtrend, 15m still not low enough
      & (
        (_cmp_cached_105)
        | (_cmp_cached_75)
        | (_cmp_cached_63)
        | (_cmp_cached_80)
        | (_cmp_cached_87)
        | (_cmp_cached_99)
        | (_cmp_cached_13)
      )
      # 15m & 1h & 4h down move, 15m & 1h downtrend, 15m still high
      & (
        (_cmp_cached_105)
        | (_cmp_cached_75)
        | (_cmp_cached_63)
        | (_cmp_cached_76)
        | (_cmp_cached_85)
        | (_cmp_cached_42)
      )
      # 15m & 1h & 4h & 1d down move, 15m downtrend, 1d overbought
      & (
        (_cmp_cached_105)
        | (_cmp_cached_75)
        | (_cmp_cached_41)
        | (_cmp_cached_120)
        | (_cmp_cached_80)
        | (_cmp_cached_121)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h downtrend, 15m & 4h still not low enough
      & (
        (_cmp_cached_105)
        | (_cmp_cached_75)
        | (_cmp_cached_41)
        | (_cmp_cached_106)
        | (_cmp_cached_107)
        | (_cmp_cached_122)
        | (_cmp_cached_118)
        | (_cmp_cached_113)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h downtrend, 1h still not low enugh, 4h still high
      & (
        (_cmp_cached_105)
        | (_cmp_cached_75)
        | (_cmp_cached_37)
        | (_cmp_cached_123)
        | (_cmp_cached_85)
        | (_cmp_cached_99)
        | (_cmp_cached_101)
        | (_cmp_cached_124)
      )
      # 15m & 1h & 4h down move, 15m & 1h downtrend, 4h still high
      & (
        (_cmp_cached_105)
        | (_cmp_cached_75)
        | (_cmp_cached_92)
        | (_cmp_cached_25)
        | (_cmp_cached_115)
        | (_cmp_cached_61)
      )
      # 15m & 1h & 4h down move, 15m & 1h downtrend, 1h still high
      & (
        (_cmp_cached_105)
        | (_cmp_cached_78)
        | (_cmp_cached_41)
        | (_cmp_cached_80)
        | (_cmp_cached_87)
        | (_cmp_cached_44)
      )
      # 15m & 1h & 4h & 1d down move, 15m downtrend, 1h still high, 1h & 4h still not low enough, 4h overbought
      & (
        (_cmp_cached_105)
        | (_cmp_cached_78)
        | (_cmp_cached_24)
        | (_cmp_cached_125)
        | (_cmp_cached_80)
        | (_cmp_cached_111)
        | (_cmp_cached_82)
        | (_cmp_cached_113)
        | (_cmp_cached_126)
      )
      # 15m & 1h down move, 1h & 4h still not low enough, 4h high
      & (
        (_cmp_cached_105)
        | (_cmp_cached_78)
        | (_cmp_cached_56)
        | (_cmp_cached_81)
        | (_cmp_cached_82)
        | (_cmp_cached_127)
      )
      # 15m & 1h & 4h down move, 1h & 4h still not low enough, 15m & 1h & 4h downtrend
      & (
        (_cmp_cached_105)
        | (_cmp_cached_89)
        | (_cmp_cached_63)
        | (_cmp_cached_92)
        | (_cmp_cached_6)
        | (_cmp_cached_25)
        | (_cmp_cached_94)
        | (_cmp_cached_108)
      )
      # 15m & 1h & 4h down move, 1h & 4h stil not low enough, 15m & 1h & 4h downtrend, 1h still high
      & (
        (_cmp_cached_105)
        | (_cmp_cached_89)
        | (_cmp_cached_41)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_76)
        | (_cmp_cached_85)
        | (_cmp_cached_122)
        | (_cmp_cached_72)
      )
      # 15m & 1h & 4h down move, 1h & 4h still not low enough, 15m & 4h still not low enough, 15m & 4h still not low
      & (
        (_cmp_cached_105)
        | (_cmp_cached_89)
        | (_cmp_cached_83)
        | (_cmp_cached_92)
        | (_cmp_cached_6)
        | (_cmp_cached_123)
        | (_cmp_cached_122)
        | (_cmp_cached_13)
        | (_cmp_cached_77)
      )
      # 15m & 1h & 4h down move, 1h & 4h still not low enough, 15m still high
      & (
        (_cmp_cached_105)
        | (_cmp_cached_89)
        | (_cmp_cached_24)
        | (_cmp_cached_5)
        | (_cmp_cached_18)
        | (_cmp_cached_42)
      )
      # 15m & 1h down move, 1h high, 4h high
      & (
        (_cmp_cached_105)
        | (_cmp_cached_89)
        | (_cmp_cached_128)
        | (_cmp_cached_40)
      )
      # 15m & 1h & 4h down move, 1h still not low enough, 4h still high, 15m still not low enough, 1d high & overbought
      & (
        (_cmp_cached_105)
        | (_cmp_cached_2)
        | (_cmp_cached_83)
        | (_cmp_cached_5)
        | (_cmp_cached_29)
        | (_cmp_cached_13)
        | (_cmp_cached_129)
        | (_cmp_cached_27)
      )
      # 15m & 1h & 4h down move, 15m downtrend, 1h still high, 15m still not low enough
      & (
        (_cmp_cached_105)
        | (_cmp_cached_2)
        | (_cmp_cached_37)
        | (_cmp_cached_80)
        | (_cmp_cached_72)
        | (_cmp_cached_13)
      )
      # 15m & 1h down move, 1h & 4h high
      & (
        (_cmp_cached_105)
        | (_cmp_cached_2)
        | (_cmp_cached_28)
        | (_cmp_cached_55)
        | (_cmp_cached_128)
        | (_cmp_cached_130)
      )
      # 15m & 1h & 4h & 1d down move, 15m downtrend
      & (
        (_cmp_cached_105)
        | (_cmp_cached_2)
        | (_cmp_cached_63)
        | (_cmp_cached_131)
        | (_cmp_cached_114)
      )
      # 15m & 1h down move, 15m still not low enough, 1h still high, 4h high, 15m still high, 4h overbought
      & (
        (_cmp_cached_105)
        | (_cmp_cached_2)
        | (_cmp_cached_102)
        | (_cmp_cached_17)
        | (_cmp_cached_68)
        | (_cmp_cached_42)
        | (_cmp_cached_132)
      )
      # 15m & 1h & 4h down move, 15m downtrend, 4h high
      & (
        (_cmp_cached_105)
        | (_cmp_cached_133)
        | (_cmp_cached_63)
        | (_cmp_cached_80)
        | (_cmp_cached_34)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 4h downtrend, 4h high
      & (
        (_cmp_cached_105)
        | (_cmp_cached_96)
        | (_cmp_cached_37)
        | (_cmp_cached_102)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_122)
        | (_cmp_cached_35)
      )
      # 15m & 1h & 4h down move, 1h high, 4h downtrend
      & (
        (_cmp_cached_105)
        | (_cmp_cached_96)
        | (_cmp_cached_37)
        | (_cmp_cached_134)
        | (_cmp_cached_135)
      )
      # 15m & 1h & 4h down move, 1h & 4h still high, 15m downtrend
      & (
        (_cmp_cached_105)
        | (_cmp_cached_96)
        | (_cmp_cached_52)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_25)
        | (_cmp_cached_124)
        | (_cmp_cached_61)
      )
      # 15m & 1h down move, 15m still not low enough, 1h & 4h high, 1h high, 4h overbought
      & (
        (_cmp_cached_105)
        | (_cmp_cached_96)
        | (_cmp_cached_102)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_128)
        | (_cmp_cached_126)
      )
      # 15m & 1h & 4h down move, 15m & 1h still not low enough, 4h still high, 1h & 4h still high, 15m still high
      & (
        (_cmp_cached_105)
        | (_cmp_cached_64)
        | (_cmp_cached_83)
        | (_cmp_cached_102)
        | (_cmp_cached_5)
        | (_cmp_cached_18)
        | (_cmp_cached_111)
        | (_cmp_cached_124)
        | (_cmp_cached_39)
      )
      # 15m & 1h & 4h down move, 1h & 4h still high, 4h high
      & (
        (_cmp_cached_105)
        | (_cmp_cached_96)
        | (_cmp_cached_136)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_34)
        | (_cmp_cached_40)
      )
      # 15m & 1h & 3h down move, 1h & 4h still not low enough, 15m downtrend, 1h still high
      & (
        (_cmp_cached_105)
        | (_cmp_cached_64)
        | (_cmp_cached_83)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_80)
        | (_cmp_cached_44)
      )
      # 15m & 1h & 4h down move, 1h & 4h still high, 1d overbought
      & (
        (_cmp_cached_105)
        | (_cmp_cached_51)
        | (_cmp_cached_52)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_124)
        | (_cmp_cached_137)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 1h high, 1d overbought
      & (
        (_cmp_cached_105)
        | (_cmp_cached_51)
        | (_cmp_cached_52)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_32)
        | (_cmp_cached_138)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 15m still not low enough
      & (
        (_cmp_cached_105)
        | (_cmp_cached_66)
        | (_cmp_cached_136)
        | (_cmp_cached_139)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_140)
        | (_cmp_cached_13)
      )
      # 15m & 1h down move, 15m still not low enough, 1h & 4h high, 1h & 4h overbought
      & (
        (_cmp_cached_105)
        | (_cmp_cached_66)
        | (_cmp_cached_12)
        | (_cmp_cached_67)
        | (_cmp_cached_141)
        | (_cmp_cached_142)
        | (_cmp_cached_143)
        | (_cmp_cached_144)
        | (_cmp_cached_126)
      )
      # 15m & 1h & 4h down move, 1h & 4h still high, 15m downtrend, 1h still high
      & (
        (_cmp_cached_105)
        | (_cmp_cached_58)
        | (_cmp_cached_145)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_114)
        | (_cmp_cached_72)
      )
      # 15m & 4h down move, 15m & 1h still not low enough, 4h still high, 1h & 4h still not low enough, 1d overbought
      & (
        (_cmp_cached_105)
        | (_cmp_cached_3)
        | (_cmp_cached_139)
        | (_cmp_cached_5)
        | (_cmp_cached_18)
        | (_cmp_cached_56)
        | (_cmp_cached_81)
        | (_cmp_cached_146)
      )
      # 15m down move, 15m still not low enough, 1h & 4h high, 1h overbought
      & (
        (_cmp_cached_105)
        | (_cmp_cached_12)
        | (_cmp_cached_67)
        | (_cmp_cached_68)
        | (_cmp_cached_128)
        | (_cmp_cached_130)
        | (_cmp_cached_144)
      )
      # 15m down move, 15m still not low enough, 1h & 4h high, 4h overbought
      & (
        (_cmp_cached_105)
        | (_cmp_cached_12)
        | (_cmp_cached_67)
        | (_cmp_cached_68)
        | (_cmp_cached_134)
        | (_cmp_cached_130)
        | (_cmp_cached_32)
        | (_cmp_cached_126)
      )
      # 15m & 1h & 4h down move, 1h & 4h still not low enough, 15m & 1h & 4h downtrend, 1h & 4h downtrend
      & (
        (_cmp_cached_22)
        | (_cmp_cached_78)
        | (_cmp_cached_10)
        | (_cmp_cached_147)
        | (_cmp_cached_93)
        | (_cmp_cached_106)
        | (_cmp_cached_107)
        | (_cmp_cached_108)
        | (_cmp_cached_148)
        | (_cmp_cached_109)
      )
      # 15m & 1h & 4h down move, 4h still high, 15m & 1h & 4h downtrend
      & (
        (_cmp_cached_22)
        | (_cmp_cached_78)
        | (_cmp_cached_79)
        | (_cmp_cached_18)
        | (_cmp_cached_76)
        | (_cmp_cached_85)
        | (_cmp_cached_122)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h downtrend, 4h still high
      & (
        (_cmp_cached_22)
        | (_cmp_cached_78)
        | (_cmp_cached_79)
        | (_cmp_cached_25)
        | (_cmp_cached_107)
        | (_cmp_cached_108)
        | (_cmp_cached_88)
      )
      # 15m & 1h & 4h down move, 15m & 1h downtrend, 15m still high
      & (
        (_cmp_cached_22)
        | (_cmp_cached_78)
        | (_cmp_cached_79)
        | (_cmp_cached_80)
        | (_cmp_cached_115)
        | (_cmp_cached_39)
      )
      # 15m & 1h & 4h down move, 1h & 4h downtrend, 1h still high, 1h downtrend
      & (
        (_cmp_cached_22)
        | (_cmp_cached_78)
        | (_cmp_cached_79)
        | (_cmp_cached_87)
        | (_cmp_cached_99)
        | (_cmp_cached_72)
        | (_cmp_cached_74)
      )
      # 15m & 1h & 4h down move, 1h & 4h still not low enough, 15m still high
      & (
        (_cmp_cached_22)
        | (_cmp_cached_78)
        | (_cmp_cached_79)
        | (_cmp_cached_101)
        | (_cmp_cached_149)
        | (_cmp_cached_150)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h downtrend, 15m still high, 4h still not low enough
      & (
        (_cmp_cached_22)
        | (_cmp_cached_78)
        | (_cmp_cached_3)
        | (_cmp_cached_76)
        | (_cmp_cached_94)
        | (_cmp_cached_95)
        | (_cmp_cached_39)
        | (_cmp_cached_113)
      )
      # 15m & 1h & 4h down move, 1h & 15m still high, 1h downtrend
      & (
        (_cmp_cached_22)
        | (_cmp_cached_78)
        | (_cmp_cached_3)
        | (_cmp_cached_111)
        | (_cmp_cached_39)
        | (_cmp_cached_119)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h downtrend, 4h high
      & (
        (_cmp_cached_22)
        | (_cmp_cached_78)
        | (_cmp_cached_63)
        | (_cmp_cached_76)
        | (_cmp_cached_85)
        | (_cmp_cached_122)
        | (_cmp_cached_50)
      )
      # 15m & 1h & 4h down move, 4h still not low enough, 1h still high, 4h high
      & (
        (_cmp_cached_22)
        | (_cmp_cached_78)
        | (_cmp_cached_63)
        | (_cmp_cached_6)
        | (_cmp_cached_111)
        | (_cmp_cached_34)
        | (_cmp_cached_35)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 15m & 1h downtrend, 15m still not low enough
      & (
        (_cmp_cached_22)
        | (_cmp_cached_78)
        | (_cmp_cached_41)
        | (_cmp_cached_139)
        | (_cmp_cached_92)
        | (_cmp_cached_6)
        | (_cmp_cached_76)
        | (_cmp_cached_107)
        | (_cmp_cached_13)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 15m & 1h downtrend, 4h still high, 4h downtrend
      & (
        (_cmp_cached_22)
        | (_cmp_cached_78)
        | (_cmp_cached_41)
        | (_cmp_cached_102)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_106)
        | (_cmp_cached_94)
        | (_cmp_cached_88)
        | (_cmp_cached_109)
      )
      # 15m & 1h & 4h down move, 15m & 1h still not low enough, 4h still high, 15m & 1h downtrend
      & (
        (_cmp_cached_22)
        | (_cmp_cached_78)
        | (_cmp_cached_41)
        | (_cmp_cached_102)
        | (_cmp_cached_5)
        | (_cmp_cached_18)
        | (_cmp_cached_73)
        | (_cmp_cached_148)
      )
      # 15m & 1h & 4h down move, 15m & 1h still not low enough, 4h still high, 1d overbought
      & (
        (_cmp_cached_22)
        | (_cmp_cached_78)
        | (_cmp_cached_41)
        | (_cmp_cached_102)
        | (_cmp_cached_5)
        | (_cmp_cached_18)
        | (_cmp_cached_151)
      )
      # 15m & 1h down move, 1h still high, 4h high & overbought
      & (
        (_cmp_cached_22)
        | (_cmp_cached_78)
        | (_cmp_cached_17)
        | (_cmp_cached_141)
        | (_cmp_cached_34)
        | (_cmp_cached_40)
        | (_cmp_cached_57)
      )
      # 15m & 1h & 4h down move, 15m & 1h still not low enough, 4h still high, 4h overbought
      & (
        (_cmp_cached_22)
        | (_cmp_cached_89)
        | (_cmp_cached_3)
        | (_cmp_cached_12)
        | (_cmp_cached_5)
        | (_cmp_cached_18)
        | (_cmp_cached_124)
        | (_cmp_cached_152)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 15m & 1h downtrend, 15m still not low enough
      & (
        (_cmp_cached_22)
        | (_cmp_cached_89)
        | (_cmp_cached_83)
        | (_cmp_cached_102)
        | (_cmp_cached_92)
        | (_cmp_cached_6)
        | (_cmp_cached_25)
        | (_cmp_cached_94)
        | (_cmp_cached_13)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 15m & 1h & 4h downtrend, 1h still not low enough
      & (
        (_cmp_cached_22)
        | (_cmp_cached_89)
        | (_cmp_cached_83)
        | (_cmp_cached_102)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_25)
        | (_cmp_cached_94)
        | (_cmp_cached_95)
        | (_cmp_cached_86)
      )
      # 15m & 1h & 4h down move, 1h still not low enough, 4h high, 1d overbought
      & (
        (_cmp_cached_22)
        | (_cmp_cached_89)
        | (_cmp_cached_48)
        | (_cmp_cached_5)
        | (_cmp_cached_68)
        | (_cmp_cached_151)
      )
      # 15m & 1h & 4h down move, 1h downtrend, 4h high
      & (
        (_cmp_cached_22)
        | (_cmp_cached_89)
        | (_cmp_cached_24)
        | (_cmp_cached_29)
        | (_cmp_cached_153)
        | (_cmp_cached_34)
        | (_cmp_cached_35)
      )
      # 15m & 1h & 4h down move, 1h & 4h still not low enough, 1h & 4h downtrend, 15m & 1h & 4h still not low enough
      & (
        (_cmp_cached_22)
        | (_cmp_cached_2)
        | (_cmp_cached_3)
        | (_cmp_cached_92)
        | (_cmp_cached_93)
        | (_cmp_cached_107)
        | (_cmp_cached_122)
        | (_cmp_cached_91)
        | (_cmp_cached_86)
        | (_cmp_cached_77)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h downtrend, 15m still high
      & (
        (_cmp_cached_22)
        | (_cmp_cached_2)
        | (_cmp_cached_3)
        | (_cmp_cached_76)
        | (_cmp_cached_87)
        | (_cmp_cached_99)
        | (_cmp_cached_39)
      )
      # 15m & 1h & 4h down move, 1h still not low enough, 4h still high, 1h downtrend, 1d overbought
      & (
        (_cmp_cached_22)
        | (_cmp_cached_2)
        | (_cmp_cached_3)
        | (_cmp_cached_5)
        | (_cmp_cached_18)
        | (_cmp_cached_94)
        | (_cmp_cached_124)
        | (_cmp_cached_154)
        | (_cmp_cached_155)
        | (_cmp_cached_156)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h high
      & (
        (_cmp_cached_22)
        | (_cmp_cached_2)
        | (_cmp_cached_63)
        | (_cmp_cached_140)
        | (_cmp_cached_157)
        | (_cmp_cached_130)
      )
      # 15m & 1h & 4h & 1d down move, 1h still not low enough, 4h still high, 1d overbought
      & (
        (_cmp_cached_22)
        | (_cmp_cached_2)
        | (_cmp_cached_63)
        | (_cmp_cached_158)
        | (_cmp_cached_5)
        | (_cmp_cached_18)
        | (_cmp_cached_159)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 4h overbought
      & (
        (_cmp_cached_22)
        | (_cmp_cached_2)
        | (_cmp_cached_83)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_61)
        | (_cmp_cached_126)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 1h high
      & (
        (_cmp_cached_22)
        | (_cmp_cached_2)
        | (_cmp_cached_37)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_140)
        | (_cmp_cached_128)
        | (_cmp_cached_44)
        | (_cmp_cached_61)
      )
      # 15m & 1h & 4h down move, 15m & 1h still not low enough, 4h stil high, 1h & 4h downtrend, 1h & 4h still not low
      & (
        (_cmp_cached_22)
        | (_cmp_cached_2)
        | (_cmp_cached_48)
        | (_cmp_cached_139)
        | (_cmp_cached_5)
        | (_cmp_cached_18)
        | (_cmp_cached_85)
        | (_cmp_cached_99)
        | (_cmp_cached_101)
        | (_cmp_cached_149)
      )
      # 15m & 1h & 4h down move, 15m & 1h still not low enough, 1h & 4h still high, 1d overbought
      & (
        (_cmp_cached_22)
        | (_cmp_cached_2)
        | (_cmp_cached_145)
        | (_cmp_cached_12)
        | (_cmp_cached_5)
        | (_cmp_cached_29)
        | (_cmp_cached_160)
        | (_cmp_cached_121)
      )
      # 15m & 1h down move, 15m still not low enough, 1h still high, 4h high, 4h overbought
      & (
        (_cmp_cached_22)
        | (_cmp_cached_2)
        | (_cmp_cached_102)
        | (_cmp_cached_17)
        | (_cmp_cached_55)
        | (_cmp_cached_34)
        | (_cmp_cached_127)
        | (_cmp_cached_132)
      )
      # 15m & 1h down move, 15m still not low enough, 1h & 4h high, 1h & 1d overbought
      & (
        (_cmp_cached_22)
        | (_cmp_cached_2)
        | (_cmp_cached_12)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_72)
        | (_cmp_cached_130)
        | (_cmp_cached_126)
        | (_cmp_cached_146)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 1h & 4h downtrend, 1h & 4h still high
      & (
        (_cmp_cached_22)
        | (_cmp_cached_133)
        | (_cmp_cached_63)
        | (_cmp_cached_102)
        | (_cmp_cached_92)
        | (_cmp_cached_93)
        | (_cmp_cached_107)
        | (_cmp_cached_122)
        | (_cmp_cached_160)
        | (_cmp_cached_161)
      )
      # 15m & 1h & 4h down move, 15m & 1h still not low, 4h still high, 15m & 1h downtrend, 4h not low, 4h downtrend
      & (
        (_cmp_cached_22)
        | (_cmp_cached_133)
        | (_cmp_cached_63)
        | (_cmp_cached_102)
        | (_cmp_cached_5)
        | (_cmp_cached_18)
        | (_cmp_cached_123)
        | (_cmp_cached_85)
        | (_cmp_cached_81)
        | (_cmp_cached_162)
      )
      # 15m & 1h & 4h down move, 1h & 4h not low enouhg, 15m downtrend, 4h high, 1d overbought
      & (
        (_cmp_cached_22)
        | (_cmp_cached_133)
        | (_cmp_cached_63)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_80)
        | (_cmp_cached_26)
        | (_cmp_cached_163)
      )
      # 15m & 1h & 4h & 1d down move, 15m & 1h still not low enough, 4h still high. 1d high & overbought
      & (
        (_cmp_cached_22)
        | (_cmp_cached_133)
        | (_cmp_cached_63)
        | (_cmp_cached_164)
        | (_cmp_cached_12)
        | (_cmp_cached_5)
        | (_cmp_cached_18)
        | (_cmp_cached_165)
        | (_cmp_cached_27)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h downtrend, 1h & 4h still not low enough, 1h & 4h downtrend
      & (
        (_cmp_cached_22)
        | (_cmp_cached_133)
        | (_cmp_cached_63)
        | (_cmp_cached_76)
        | (_cmp_cached_85)
        | (_cmp_cached_122)
        | (_cmp_cached_166)
        | (_cmp_cached_90)
        | (_cmp_cached_119)
        | (_cmp_cached_167)
      )
      # 15m & 1h & 1d down move, 1h still not low enough, 4h high & overbought
      & (
        (_cmp_cached_22)
        | (_cmp_cached_133)
        | (_cmp_cached_59)
        | (_cmp_cached_5)
        | (_cmp_cached_68)
        | (_cmp_cached_111)
        | (_cmp_cached_143)
        | (_cmp_cached_148)
        | (_cmp_cached_69)
      )
      # 15m & 1h & 1d down move, 15m still not low enough, 1h & 4h still high, 1h high, 4h overbought
      & (
        (_cmp_cached_22)
        | (_cmp_cached_133)
        | (_cmp_cached_117)
        | (_cmp_cached_102)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_140)
        | (_cmp_cached_134)
        | (_cmp_cached_126)
      )
      # 15m & 1h & 4h down move, 15m & 1h still not low enough, 4h still high, 15m & 1h downtrend
      & (
        (_cmp_cached_22)
        | (_cmp_cached_96)
        | (_cmp_cached_41)
        | (_cmp_cached_102)
        | (_cmp_cached_5)
        | (_cmp_cached_18)
        | (_cmp_cached_80)
        | (_cmp_cached_94)
      )
      # 15m & 1h & 4h down move, 1h & 4h still high, 4h high, 4h & 1d overbought
      & (
        (_cmp_cached_22)
        | (_cmp_cached_96)
        | (_cmp_cached_48)
        | (_cmp_cached_168)
        | (_cmp_cached_169)
        | (_cmp_cached_50)
        | (_cmp_cached_132)
        | (_cmp_cached_159)
      )
      # 15m & 1h & 4h down move, 1h & 4h still high, 15m downtrend, 4h high
      & (
        (_cmp_cached_22)
        | (_cmp_cached_96)
        | (_cmp_cached_136)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_25)
        | (_cmp_cached_34)
      )
      # 15m & 1h down move, 4h high, 1d downtrend, 1h still not low enough, 1d overbought
      & (
        (_cmp_cached_22)
        | (_cmp_cached_96)
        | (_cmp_cached_55)
        | (_cmp_cached_170)
        | (_cmp_cached_101)
        | (_cmp_cached_121)
      )
      # 15m & 1h & 4h & 1d down move, 15m & 1h not low enough, 4h high
      & (
        (_cmp_cached_22)
        | (_cmp_cached_64)
        | (_cmp_cached_83)
        | (_cmp_cached_45)
        | (_cmp_cached_12)
        | (_cmp_cached_171)
        | (_cmp_cached_43)
        | (_cmp_cached_172)
      )
      # 15m & 1h & 4h & 1d down move, 15m & 1 & 4h still not low enough, 1h still high, 4h high
      & (
        (_cmp_cached_22)
        | (_cmp_cached_64)
        | (_cmp_cached_83)
        | (_cmp_cached_11)
        | (_cmp_cached_12)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_160)
        | (_cmp_cached_173)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h still high, 4h high & overbought
      & (
        (_cmp_cached_22)
        | (_cmp_cached_64)
        | (_cmp_cached_136)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_34)
        | (_cmp_cached_57)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 1h still high, 4h high & overbought
      & (
        (_cmp_cached_22)
        | (_cmp_cached_64)
        | (_cmp_cached_145)
        | (_cmp_cached_102)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_72)
        | (_cmp_cached_130)
        | (_cmp_cached_132)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 15m & 1h & 4h downtrend, 1h still high
      & (
        (_cmp_cached_22)
        | (_cmp_cached_23)
        | (_cmp_cached_37)
        | (_cmp_cached_102)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_80)
        | (_cmp_cached_174)
        | (_cmp_cached_110)
        | (_cmp_cached_44)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 1h & 4h still high, 1d downtrend
      & (
        (_cmp_cached_22)
        | (_cmp_cached_23)
        | (_cmp_cached_136)
        | (_cmp_cached_12)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_175)
        | (_cmp_cached_44)
        | (_cmp_cached_61)
        | (_cmp_cached_176)
      )
      # 15m & 1h down move, 4h still high, 15m downtrend, 1h & 1d high
      & (
        (_cmp_cached_22)
        | (_cmp_cached_23)
        | (_cmp_cached_29)
        | (_cmp_cached_177)
        | (_cmp_cached_157)
        | (_cmp_cached_178)
        | (_cmp_cached_179)
      )
      # 15m & 1h down move, 15m & 1h still high, 1h & 4h high, 1d overbought
      & (
        (_cmp_cached_22)
        | (_cmp_cached_23)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_55)
        | (_cmp_cached_128)
        | (_cmp_cached_130)
        | (_cmp_cached_159)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 1h & 4h high, 4h overbought
      & (
        (_cmp_cached_22)
        | (_cmp_cached_33)
        | (_cmp_cached_136)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_134)
        | (_cmp_cached_130)
        | (_cmp_cached_132)
      )
      # 15m & 1h & 4h down move, 1h & 4h sitll high, 15m & 1h & 4h downtrend, 1h & 4h still high
      & (
        (_cmp_cached_22)
        | (_cmp_cached_51)
        | (_cmp_cached_145)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_76)
        | (_cmp_cached_85)
        | (_cmp_cached_95)
        | (_cmp_cached_160)
        | (_cmp_cached_161)
      )
      # 15m & 1h & 4h down move, 15m stil not low enough, 1h & 4h still high, 15m & 4h still high, 1d overbought
      & (
        (_cmp_cached_22)
        | (_cmp_cached_51)
        | (_cmp_cached_52)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_42)
        | (_cmp_cached_124)
        | (_cmp_cached_151)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 1h & 4h downtrend, 1h high
      & (
        (_cmp_cached_22)
        | (_cmp_cached_51)
        | (_cmp_cached_52)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_174)
        | (_cmp_cached_95)
        | (_cmp_cached_32)
      )
      # 15m & 1h & 4h down move, 1h & 4h still not low enough, 15m & 4h downtrend, 1h & 4h still high
      & (
        (_cmp_cached_22)
        | (_cmp_cached_51)
        | (_cmp_cached_52)
        | (_cmp_cached_92)
        | (_cmp_cached_6)
        | (_cmp_cached_114)
        | (_cmp_cached_122)
        | (_cmp_cached_111)
        | (_cmp_cached_161)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 14h & 1d overbought
      & (
        (_cmp_cached_22)
        | (_cmp_cached_51)
        | (_cmp_cached_145)
        | (_cmp_cached_102)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_180)
        | (_cmp_cached_27)
      )
      # 15m & 1h down move, 15m still not low enough, 1h & 4h high, 4h overbought
      & (
        (_cmp_cached_22)
        | (_cmp_cached_51)
        | (_cmp_cached_55)
        | (_cmp_cached_100)
        | (_cmp_cached_128)
        | (_cmp_cached_130)
        | (_cmp_cached_69)
      )
      # 15m & 1h down move, 15m still not low enough, 1h & 4h high & overbought
      & (
        (_cmp_cached_22)
        | (_cmp_cached_51)
        | (_cmp_cached_12)
        | (_cmp_cached_181)
        | (_cmp_cached_55)
        | (_cmp_cached_157)
        | (_cmp_cached_130)
        | (_cmp_cached_182)
        | (_cmp_cached_183)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 1h & 4h downtrend, 4h high, 1h overbought
      & (
        (_cmp_cached_22)
        | (_cmp_cached_54)
        | (_cmp_cached_24)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_174)
        | (_cmp_cached_110)
        | (_cmp_cached_34)
        | (_cmp_cached_144)
      )
      # 15m & 1h & 4h down move, 1h & 4h downtrend, 15m still high, 1h high
      & (
        (_cmp_cached_22)
        | (_cmp_cached_54)
        | (_cmp_cached_24)
        | (_cmp_cached_184)
        | (_cmp_cached_185)
        | (_cmp_cached_42)
        | (_cmp_cached_104)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 1d overbought
      & (
        (_cmp_cached_22)
        | (_cmp_cached_54)
        | (_cmp_cached_145)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_111)
        | (_cmp_cached_88)
        | (_cmp_cached_151)
      )
      # 15m & 1h down move, 15m still not low enough, 1h & 4h still high, 15m & 4h high, 4h & 1d overbought
      & (
        (_cmp_cached_22)
        | (_cmp_cached_54)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_68)
        | (_cmp_cached_38)
        | (_cmp_cached_34)
        | (_cmp_cached_126)
        | (_cmp_cached_159)
      )
      # 15m & 1h down move, 15m & 1h still high, 4h high, 15m still not low enough, 1h & 4h high, 4h overbought
      & (
        (_cmp_cached_22)
        | (_cmp_cached_54)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_68)
        | (_cmp_cached_175)
        | (_cmp_cached_128)
        | (_cmp_cached_26)
        | (_cmp_cached_152)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 1h & 4h downtrend, 15m & 1h high
      & (
        (_cmp_cached_22)
        | (_cmp_cached_66)
        | (_cmp_cached_136)
        | (_cmp_cached_12)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_184)
        | (_cmp_cached_186)
        | (_cmp_cached_42)
        | (_cmp_cached_187)
      )
      # 15m & 1h down move, 15m & 4h high, 4h overbought
      & (
        (_cmp_cached_22)
        | (_cmp_cached_58)
        | (_cmp_cached_188)
        | (_cmp_cached_189)
        | (_cmp_cached_190)
      )
      # 15m & 1h down move, 15m & 1h & 4h still high, 1h & 4h high, 1h & 4h overbought
      & (
        (_cmp_cached_22)
        | (_cmp_cached_58)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_134)
        | (_cmp_cached_130)
        | (_cmp_cached_182)
        | (_cmp_cached_69)
      )
      # 15m & 4h & 1d down move, 15m high, 15m & 4h still high
      & (
        (_cmp_cached_22)
        | (_cmp_cached_79)
        | (_cmp_cached_4)
        | (_cmp_cached_19)
        | (_cmp_cached_150)
        | (_cmp_cached_61)
      )
      # 15m & 4h & 1d down move, 15m & 1h still not low enough, 1h still high, 4h & 1d downtrend
      & (
        (_cmp_cached_22)
        | (_cmp_cached_3)
        | (_cmp_cached_4)
        | (_cmp_cached_12)
        | (_cmp_cached_5)
        | (_cmp_cached_160)
        | (_cmp_cached_191)
        | (_cmp_cached_176)
      )
      # 15m & 4h down move, 1h & 4h stil high, 15m high, 4h overbought
      & (
        (_cmp_cached_22)
        | (_cmp_cached_136)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_19)
        | (_cmp_cached_69)
      )
      # 15m down move, 15m still not low enough, 1h & 4h high & overbought
      & (
        (_cmp_cached_22)
        | (_cmp_cached_12)
        | (_cmp_cached_181)
        | (_cmp_cached_141)
        | (_cmp_cached_31)
        | (_cmp_cached_130)
        | (_cmp_cached_192)
        | (_cmp_cached_57)
      )
      # 15m down move, 15m & 1h & 4h still high, 15m still high, 4h high, 4h overbought
      & (
        (_cmp_cached_22)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_68)
        | (_cmp_cached_42)
        | (_cmp_cached_34)
        | (_cmp_cached_43)
        | (_cmp_cached_160)
        | (_cmp_cached_61)
        | (_cmp_cached_152)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 1h & 4h downtrend
      & (
        (_cmp_cached_1)
        | (_cmp_cached_89)
        | (_cmp_cached_79)
        | (_cmp_cached_102)
        | (_cmp_cached_92)
        | (_cmp_cached_93)
        | (_cmp_cached_148)
        | (_cmp_cached_193)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 1h high, 15m still not low enough
      & (
        (_cmp_cached_1)
        | (_cmp_cached_89)
        | (_cmp_cached_79)
        | (_cmp_cached_102)
        | (_cmp_cached_92)
        | (_cmp_cached_6)
        | (_cmp_cached_134)
        | (_cmp_cached_43)
      )
      # 15m & 1h & 4h & 1d down move, 1h & 4h still not low enough, 1h & 4h downtrend, 4h still high
      & (
        (_cmp_cached_1)
        | (_cmp_cached_89)
        | (_cmp_cached_63)
        | (_cmp_cached_59)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_174)
        | (_cmp_cached_110)
        | (_cmp_cached_88)
        | (_cmp_cached_109)
      )
      # 15m & 1h & 4h & 1d down move, 1h still not low enough, 4h still high, 4h downtrend, 1h still not low enough
      & (
        (_cmp_cached_1)
        | (_cmp_cached_89)
        | (_cmp_cached_83)
        | (_cmp_cached_97)
        | (_cmp_cached_92)
        | (_cmp_cached_18)
        | (_cmp_cached_99)
        | (_cmp_cached_56)
      )
      # 15m & 1h & 4h & 1d down move, 15m downtrend, 15m & 4h high, 1d downtrend
      & (
        (_cmp_cached_1)
        | (_cmp_cached_89)
        | (_cmp_cached_83)
        | (_cmp_cached_97)
        | (_cmp_cached_76)
        | (_cmp_cached_38)
        | (_cmp_cached_50)
        | (_cmp_cached_194)
      )
      # 15m & 1h & 4h & 1d down move, 4h still not low enough, 15m & 1h & 4h downtrend
      & (
        (_cmp_cached_1)
        | (_cmp_cached_89)
        | (_cmp_cached_37)
        | (_cmp_cached_120)
        | (_cmp_cached_195)
        | (_cmp_cached_6)
        | (_cmp_cached_25)
        | (_cmp_cached_85)
        | (_cmp_cached_186)
        | (_cmp_cached_81)
      )
      # 15m & 1h & 4h down move, 1h still not low enough, 4h high, 1h downtrend
      & (
        (_cmp_cached_1)
        | (_cmp_cached_89)
        | (_cmp_cached_48)
        | (_cmp_cached_5)
        | (_cmp_cached_196)
        | (_cmp_cached_111)
        | (_cmp_cached_143)
        | (_cmp_cached_197)
      )
      # 15m & 1h & 4h down move, 4h high, 1d overbought
      & (
        (_cmp_cached_1)
        | (_cmp_cached_89)
        | (_cmp_cached_48)
        | (_cmp_cached_34)
        | (_cmp_cached_198)
      )
      # 15m & 1h down move, 15m & 1h still not low enough, 4h still high, 4h high
      & (
        (_cmp_cached_1)
        | (_cmp_cached_89)
        | (_cmp_cached_102)
        | (_cmp_cached_92)
        | (_cmp_cached_29)
        | (_cmp_cached_140)
        | (_cmp_cached_101)
        | (_cmp_cached_26)
        | (_cmp_cached_127)
      )
      # 15m & 1h down move, 15m still not low enough, 1h still high, 4h high. 4h overbought
      & (
        (_cmp_cached_1)
        | (_cmp_cached_89)
        | (_cmp_cached_102)
        | (_cmp_cached_28)
        | (_cmp_cached_55)
        | (_cmp_cached_72)
        | (_cmp_cached_34)
        | (_cmp_cached_183)
      )
      # 15m & 1h & 4h down move, 15m & 1h still not low enough, 4h still high, 15m downtrend
      & (
        (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_63)
        | (_cmp_cached_102)
        | (_cmp_cached_5)
        | (_cmp_cached_18)
        | (_cmp_cached_199)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 15m high, 1h still high
      & (
        (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_63)
        | (_cmp_cached_12)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_38)
        | (_cmp_cached_160)
      )
      # 15m & 1h & 4h down move, 15m & 1h still not low enough, 4h still high, 15m downtrend, 4h high, 1h downtrend
      & (
        (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_41)
        | (_cmp_cached_102)
        | (_cmp_cached_5)
        | (_cmp_cached_18)
        | (_cmp_cached_80)
        | (_cmp_cached_26)
        | (_cmp_cached_119)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 1h & 4h high
      & (
        (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_48)
        | (_cmp_cached_102)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_157)
        | (_cmp_cached_189)
      )
      # 15m & 1h & 4h down move, 15m & 1h still not low enough, 4h still high, 1h & 4h downtrend, 1h high
      & (
        (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_136)
        | (_cmp_cached_12)
        | (_cmp_cached_5)
        | (_cmp_cached_18)
        | (_cmp_cached_115)
        | (_cmp_cached_110)
        | (_cmp_cached_134)
      )
      # 15m & 1h down move, 15m still not low enough, 1h & 4h still high, 15m downtrend, 1h still high, 4h high
      & (
        (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_12)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_25)
        | (_cmp_cached_72)
        | (_cmp_cached_130)
        | (_cmp_cached_127)
      )
      # 15m & 1h & 4h & 1d down move, 15m still not low enough, 1h & 4h still high, 4h high, 1d overbought
      & (
        (_cmp_cached_1)
        | (_cmp_cached_133)
        | (_cmp_cached_136)
        | (_cmp_cached_164)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_34)
        | (_cmp_cached_61)
        | (_cmp_cached_156)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 1d overbought
      & (
        (_cmp_cached_1)
        | (_cmp_cached_133)
        | (_cmp_cached_145)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_124)
        | (_cmp_cached_44)
        | (_cmp_cached_27)
      )
      # 15m & 1h & 1d down move, 15m & 1h still not low enough, 4h high, 1d downtrend, 4h overbought
      & (
        (_cmp_cached_1)
        | (_cmp_cached_133)
        | (_cmp_cached_59)
        | (_cmp_cached_102)
        | (_cmp_cached_5)
        | (_cmp_cached_68)
        | (_cmp_cached_189)
        | (_cmp_cached_119)
        | (_cmp_cached_69)
      )
      # 15m & 1h down move, 15m still not low enough, 1h still high, 4h high, 1h & 4h downtrend
      & (
        (_cmp_cached_1)
        | (_cmp_cached_133)
        | (_cmp_cached_102)
        | (_cmp_cached_28)
        | (_cmp_cached_55)
        | (_cmp_cached_174)
        | (_cmp_cached_110)
      )
      # 15m & 1h & 4h & 1d down move, 15m & 1h & 4h still not low enough, 15m still high 4h & 1d downtrend
      & (
        (_cmp_cached_1)
        | (_cmp_cached_96)
        | (_cmp_cached_41)
        | (_cmp_cached_117)
        | (_cmp_cached_200)
        | (_cmp_cached_201)
        | (_cmp_cached_202)
        | (_cmp_cached_42)
        | (_cmp_cached_203)
        | (_cmp_cached_62)
      )
      # 15m & 1h & 4h down move, 15m downtrend, 15m & 1h still not low enough, 1h & 4h downtrend
      & (
        (_cmp_cached_1)
        | (_cmp_cached_96)
        | (_cmp_cached_41)
        | (_cmp_cached_76)
        | (_cmp_cached_13)
        | (_cmp_cached_82)
        | (_cmp_cached_119)
        | (_cmp_cached_203)
      )
      # 15m & 1h & 4h down move, 1h still high, 4h high, 4h & 1d overbought
      & (
        (_cmp_cached_1)
        | (_cmp_cached_96)
        | (_cmp_cached_48)
        | (_cmp_cached_171)
        | (_cmp_cached_29)
        | (_cmp_cached_50)
        | (_cmp_cached_132)
        | (_cmp_cached_121)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 15m & 4h still high, 4h & 1d overbought
      & (
        (_cmp_cached_1)
        | (_cmp_cached_96)
        | (_cmp_cached_48)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_42)
        | (_cmp_cached_124)
        | (_cmp_cached_132)
        | (_cmp_cached_156)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 4h overbought
      & (
        (_cmp_cached_1)
        | (_cmp_cached_96)
        | (_cmp_cached_145)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_196)
        | (_cmp_cached_204)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 4h overbought
      & (
        (_cmp_cached_1)
        | (_cmp_cached_96)
        | (_cmp_cached_145)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_100)
        | (_cmp_cached_72)
        | (_cmp_cached_124)
        | (_cmp_cached_126)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h still high, 4h high, 4h high & overbought
      & (
        (_cmp_cached_1)
        | (_cmp_cached_96)
        | (_cmp_cached_145)
        | (_cmp_cached_12)
        | (_cmp_cached_28)
        | (_cmp_cached_55)
        | (_cmp_cached_101)
        | (_cmp_cached_189)
        | (_cmp_cached_84)
      )
      # 15m & 1h down move, 15m still not low enough, 1h still high, 4h high, 1d downtrend, 4h overbought
      & (
        (_cmp_cached_1)
        | (_cmp_cached_96)
        | (_cmp_cached_12)
        | (_cmp_cached_28)
        | (_cmp_cached_68)
        | (_cmp_cached_205)
        | (_cmp_cached_100)
        | (_cmp_cached_56)
        | (_cmp_cached_189)
        | (_cmp_cached_180)
      )
      # 15m & 1h down move, 15m still not low enough, 1h still high, 4h high
      & (
        (_cmp_cached_1)
        | (_cmp_cached_96)
        | (_cmp_cached_12)
        | (_cmp_cached_28)
        | (_cmp_cached_55)
        | (_cmp_cached_157)
        | (_cmp_cached_130)
      )
      # 15m & 1h down move, 15m still high, 1h & dh high, 1d overbought
      & (
        (_cmp_cached_1)
        | (_cmp_cached_96)
        | (_cmp_cached_16)
        | (_cmp_cached_134)
        | (_cmp_cached_130)
        | (_cmp_cached_159)
      )
      # 15m & 1h & 4h & 1d down move, 15m & 1h & 4h still not low enough, 1d high, 4h downtrend
      & (
        (_cmp_cached_1)
        | (_cmp_cached_64)
        | (_cmp_cached_37)
        | (_cmp_cached_120)
        | (_cmp_cached_12)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_206)
        | (_cmp_cached_165)
        | (_cmp_cached_135)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 4h high, 1d downtrend, 4h overbought
      & (
        (_cmp_cached_1)
        | (_cmp_cached_64)
        | (_cmp_cached_48)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_34)
        | (_cmp_cached_148)
        | (_cmp_cached_126)
      )
      # 15m & 1h & 4h down move, 15m & 1h still not low enough, 4h high & overbought, 1d overbought
      & (
        (_cmp_cached_1)
        | (_cmp_cached_64)
        | (_cmp_cached_24)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_34)
        | (_cmp_cached_180)
        | (_cmp_cached_159)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 1h & 4h high
      & (
        (_cmp_cached_1)
        | (_cmp_cached_64)
        | (_cmp_cached_136)
        | (_cmp_cached_12)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_72)
        | (_cmp_cached_189)
        | (_cmp_cached_44)
        | (_cmp_cached_61)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 1h high, 1d downtrend
      & (
        (_cmp_cached_1)
        | (_cmp_cached_64)
        | (_cmp_cached_145)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_134)
        | (_cmp_cached_207)
      )
      # 15m & 1h down move, 15m still not low enough, 1h still high, 1h & 4h high, 1h & 4h overbought
      & (
        (_cmp_cached_1)
        | (_cmp_cached_64)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_55)
        | (_cmp_cached_128)
        | (_cmp_cached_130)
        | (_cmp_cached_182)
        | (_cmp_cached_152)
      )
      # 15m & 1h down move, 15m still not low enough, 1h & 4h still high, 1d downtrend, 1h & 4h high, 1d overbought
      & (
        (_cmp_cached_1)
        | (_cmp_cached_64)
        | (_cmp_cached_12)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_208)
        | (_cmp_cached_157)
        | (_cmp_cached_143)
        | (_cmp_cached_146)
      )
      # 15m & 1h down move, 15m & 1h still high, 4h high, 4h overbought
      & (
        (_cmp_cached_1)
        | (_cmp_cached_64)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_68)
        | (_cmp_cached_30)
        | (_cmp_cached_111)
        | (_cmp_cached_189)
        | (_cmp_cached_172)
        | (_cmp_cached_126)
      )
      # 15m & 1h & 4h & 1d down move, 1h still high, 4h still not low enough, 4h downtrend
      & (
        (_cmp_cached_1)
        | (_cmp_cached_23)
        | (_cmp_cached_3)
        | (_cmp_cached_117)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_44)
        | (_cmp_cached_8)
        | (_cmp_cached_98)
        | (_cmp_cached_203)
      )
      # 15m & 1h & 4h & 1d down move, 15m & 1h & 4h downtrend, 1h & 4h still not low enough, 1d downtrend
      & (
        (_cmp_cached_1)
        | (_cmp_cached_23)
        | (_cmp_cached_83)
        | (_cmp_cached_117)
        | (_cmp_cached_171)
        | (_cmp_cached_209)
        | (_cmp_cached_80)
        | (_cmp_cached_87)
        | (_cmp_cached_99)
        | (_cmp_cached_154)
        | (_cmp_cached_9)
        | (_cmp_cached_210)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 1h overbought, 4h downtrend
      & (
        (_cmp_cached_1)
        | (_cmp_cached_23)
        | (_cmp_cached_37)
        | (_cmp_cached_12)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_86)
        | (_cmp_cached_77)
        | (_cmp_cached_144)
        | (_cmp_cached_162)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 15m & 1h still high, 4h high
      & (
        (_cmp_cached_1)
        | (_cmp_cached_23)
        | (_cmp_cached_37)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_42)
        | (_cmp_cached_72)
        | (_cmp_cached_43)
        | (_cmp_cached_86)
        | (_cmp_cached_40)
      )
      # 15m & 1h & 4h down move, 4h downtrend, 1h high, 4h downtrend
      & (
        (_cmp_cached_1)
        | (_cmp_cached_23)
        | (_cmp_cached_37)
        | (_cmp_cached_110)
        | (_cmp_cached_32)
        | (_cmp_cached_167)
      )
      # 15m & 1h & 4h down move, 15m & 1h still not low enough, 4h & 1d still high, 1h downtrend, 1d downtrend
      & (
        (_cmp_cached_1)
        | (_cmp_cached_23)
        | (_cmp_cached_48)
        | (_cmp_cached_102)
        | (_cmp_cached_5)
        | (_cmp_cached_18)
        | (_cmp_cached_206)
        | (_cmp_cached_107)
        | (_cmp_cached_118)
        | (_cmp_cached_82)
        | (_cmp_cached_161)
        | (_cmp_cached_210)
      )
      # 15m down move, 15m still not low enough, 1h & 4h still high, 15m still high, 1h high
      & (
        (_cmp_cached_1)
        | (_cmp_cached_12)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_42)
        | (_cmp_cached_31)
        | (_cmp_cached_43)
        | (_cmp_cached_187)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 1h downtrend, 15m & 4h still not low, 1h high
      & (
        (_cmp_cached_47)
        | (_cmp_cached_33)
        | (_cmp_cached_48)
        | (_cmp_cached_12)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_94)
        | (_cmp_cached_140)
        | (_cmp_cached_149)
        | (_cmp_cached_32)
      )
      # 15m ^ 1h down move, 15m & 1h & 4h still not low enough, 1h & 4h high, 1h overbought
      & (
        (_cmp_cached_1)
        | (_cmp_cached_33)
        | (_cmp_cached_12)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_32)
        | (_cmp_cached_40)
        | (_cmp_cached_144)
      )
      # 15m & 1h down move, 15m still not low enough, 1h still high, 4h high, 15m still high, 4h overbought
      & (
        (_cmp_cached_1)
        | (_cmp_cached_33)
        | (_cmp_cached_12)
        | (_cmp_cached_28)
        | (_cmp_cached_55)
        | (_cmp_cached_42)
        | (_cmp_cached_189)
        | (_cmp_cached_86)
        | (_cmp_cached_35)
        | (_cmp_cached_180)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 15m still high, 1h & 4h high
      & (
        (_cmp_cached_1)
        | (_cmp_cached_51)
        | (_cmp_cached_136)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_42)
        | (_cmp_cached_31)
        | (_cmp_cached_160)
        | (_cmp_cached_40)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h high, 4h overbought
      & (
        (_cmp_cached_1)
        | (_cmp_cached_54)
        | (_cmp_cached_145)
        | (_cmp_cached_12)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_157)
        | (_cmp_cached_26)
        | (_cmp_cached_32)
        | (_cmp_cached_35)
        | (_cmp_cached_126)
      )
      # 15m & 1h & 1d down move, 15m still not low enough, 1h & 4h high, 1d overbought
      & (
        (_cmp_cached_1)
        | (_cmp_cached_54)
        | (_cmp_cached_125)
        | (_cmp_cached_12)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_128)
        | (_cmp_cached_130)
        | (_cmp_cached_159)
      )
      # 14m & 1h down move, 15m & 1h still high, 4h high & overbought
      & (
        (_cmp_cached_1)
        | (_cmp_cached_54)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_211)
        | (_cmp_cached_30)
        | (_cmp_cached_111)
        | (_cmp_cached_189)
        | (_cmp_cached_212)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 5h still high, 15m still high, 4h & 1d overbought
      & (
        (_cmp_cached_1)
        | (_cmp_cached_66)
        | (_cmp_cached_136)
        | (_cmp_cached_12)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_42)
        | (_cmp_cached_39)
        | (_cmp_cached_180)
        | (_cmp_cached_121)
      )
      # 15m & 1h & 1d down move, 15m still not low enough, 1h & 4h still high, 1d overbought
      & (
        (_cmp_cached_1)
        | (_cmp_cached_66)
        | (_cmp_cached_164)
        | (_cmp_cached_12)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_134)
        | (_cmp_cached_27)
      )
      # 15m & 1h down move, 15m & 1h stil high, 4h high, 15m & 4h high, 4h overbought
      & (
        (_cmp_cached_1)
        | (_cmp_cached_66)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_55)
        | (_cmp_cached_19)
        | (_cmp_cached_50)
        | (_cmp_cached_190)
      )
      # 15m & 1h down move, 15m & 1h & 4h still high, 15m downtrend, 1h & 4h high, 4h overbought
      & (
        (_cmp_cached_1)
        | (_cmp_cached_66)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_25)
        | (_cmp_cached_128)
        | (_cmp_cached_130)
        | (_cmp_cached_132)
      )
      # 15m & 1h down move, 15m & 1h & 4h still high, 1h & 4h high, 1h overbought
      & (
        (_cmp_cached_1)
        | (_cmp_cached_58)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_38)
        | (_cmp_cached_103)
        | (_cmp_cached_130)
        | (_cmp_cached_213)
      )
      # 15m & 4h down move, 15m high, 4h downtrend
      & (
        (_cmp_cached_1)
        | (_cmp_cached_214)
        | (_cmp_cached_20)
        | (_cmp_cached_203)
      )
      # 15m & 4h down move, 15m & 1h & 4h still not low enough, 15m & 4h downtrend, 1h & 4h downtrend
      & (
        (_cmp_cached_1)
        | (_cmp_cached_215)
        | (_cmp_cached_139)
        | (_cmp_cached_147)
        | (_cmp_cached_216)
        | (_cmp_cached_123)
        | (_cmp_cached_122)
        | (_cmp_cached_86)
        | (_cmp_cached_113)
        | (_cmp_cached_74)
        | (_cmp_cached_203)
      )
      # 15m & 4h & 1d down move, 15m & 1h & 4h still not low enough, 15m & 1d downtrend
      & (
        (_cmp_cached_1)
        | (_cmp_cached_79)
        | (_cmp_cached_59)
        | (_cmp_cached_217)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_177)
        | (_cmp_cached_170)
        | (_cmp_cached_140)
      )
      # 15m & 4h down move, 15m & 1h still high, 1h high, 1h over
      & (
        (_cmp_cached_1)
        | (_cmp_cached_79)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_128)
        | (_cmp_cached_150)
        | (_cmp_cached_104)
        | (_cmp_cached_144)
      )
      # 15m & 4h down move, 15m still not low enough, 1h & 4h still high, 15m & 1h downtrend
      & (
        (_cmp_cached_1)
        | (_cmp_cached_218)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_76)
        | (_cmp_cached_85)
        | (_cmp_cached_13)
        | (_cmp_cached_160)
      )
      # 15m & 4h down move, 15m & 1h & 4h still not low enough, 15m & 4h high, 4h downtrend
      & (
        (_cmp_cached_1)
        | (_cmp_cached_83)
        | (_cmp_cached_12)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_38)
        | (_cmp_cached_34)
        | (_cmp_cached_109)
      )
      # 15m & 4h down move, 1h high & overbought
      & (
        (_cmp_cached_1)
        | (_cmp_cached_48)
        | (_cmp_cached_104)
        | (_cmp_cached_144)
      )
      # 15m & 4h down move, 15m & 1h & 4h still high, 4h high, 1h & 4h overbought
      & (
        (_cmp_cached_1)
        | (_cmp_cached_136)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_124)
        | (_cmp_cached_144)
        | (_cmp_cached_126)
      )
      # 15m & 4h down move, 15m & 1h & 4h still high, 15m & 4h high, 4h overbought
      & (
        (_cmp_cached_1)
        | (_cmp_cached_136)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_19)
        | (_cmp_cached_50)
        | (_cmp_cached_39)
        | (_cmp_cached_126)
      )
      # 15m & 1d down move, 15m still not low enough, 1h & 4h high
      & (
        (_cmp_cached_1)
        | (_cmp_cached_131)
        | (_cmp_cached_12)
        | (_cmp_cached_32)
        | (_cmp_cached_35)
      )
      # 15m & 1d down move, 15m still not low enough, 1h & 4h high
      & (
        (_cmp_cached_1)
        | (_cmp_cached_164)
        | (_cmp_cached_12)
        | (_cmp_cached_67)
        | (_cmp_cached_68)
        | (_cmp_cached_140)
        | (_cmp_cached_157)
        | (_cmp_cached_130)
        | (_cmp_cached_44)
        | (_cmp_cached_40)
      )
      # 15m down move, 15m & 1h & 4h still not low enough, 15m & 1h downtrend, 15m & 1h high
      & (
        (_cmp_cached_1)
        | (_cmp_cached_12)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_76)
        | (_cmp_cached_85)
        | (_cmp_cached_38)
        | (_cmp_cached_219)
      )
      # 15m down move, 15m still not low enough, 1h & 4h high, 1d downtrend, 1h & 4h high
      & (
        (_cmp_cached_1)
        | (_cmp_cached_220)
        | (_cmp_cached_181)
        | (_cmp_cached_55)
        | (_cmp_cached_208)
        | (_cmp_cached_128)
        | (_cmp_cached_130)
      )
      # 15m down move, 15m still not low enough, 1h & 4h high, 1d overbought
      & (
        (_cmp_cached_1)
        | (_cmp_cached_140)
        | (_cmp_cached_31)
        | (_cmp_cached_130)
        | (_cmp_cached_221)
      )
      # 15m down move, 15m & 1h still high, 1h high, 1h overbought, 4h & 1d downtrend
      & (
        (_cmp_cached_1)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_30)
        | (_cmp_cached_31)
        | (_cmp_cached_222)
        | (_cmp_cached_223)
        | (_cmp_cached_176)
      )
      # 15m down move, 15m still high, 1h & 4h high, 1h & 1d overbought
      & (
        (_cmp_cached_1)
        | (_cmp_cached_16)
        | (_cmp_cached_181)
        | (_cmp_cached_55)
        | (_cmp_cached_128)
        | (_cmp_cached_222)
        | (_cmp_cached_121)
      )
      # 15m down move, 15m still not low enough, 1h & 4h high, 4h & 1d overbought
      & (
        (_cmp_cached_1)
        | (_cmp_cached_12)
        | (_cmp_cached_67)
        | (_cmp_cached_55)
        | (_cmp_cached_140)
        | (_cmp_cached_31)
        | (_cmp_cached_180)
        | (_cmp_cached_159)
      )
      # 15m down move, 15m & 1h & 4h still high, 1h & 4h high, 1h & 4h overbought
      & (
        (_cmp_cached_1)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_128)
        | (_cmp_cached_130)
        | (_cmp_cached_187)
        | (_cmp_cached_127)
        | (_cmp_cached_182)
        | (_cmp_cached_180)
      )
      # 15m down move, 15m high, 1h & 4h overbought
      & ((_cmp_cached_1) | (_cmp_cached_224) | (_cmp_cached_225) | (_cmp_cached_57))
      # 15m & 1h & 4h down move, 1h still high, 15m still not low enough, 4h downtrend
      & (
        (_cmp_cached_47)
        | (_cmp_cached_89)
        | (_cmp_cached_215)
        | (_cmp_cached_72)
        | (_cmp_cached_13)
        | (_cmp_cached_167)
      )
      # 15m & 1h & 4h & 1d down move, 15m downtrend, 1h & 4h still not low enough
      & (
        (_cmp_cached_47)
        | (_cmp_cached_89)
        | (_cmp_cached_48)
        | (_cmp_cached_158)
        | (_cmp_cached_114)
        | (_cmp_cached_56)
        | (_cmp_cached_226)
        | (_cmp_cached_227)
        | (_cmp_cached_228)
        | (_cmp_cached_9)
      )
      # 15m & 1h & 4h down move, 15m downtrend, 1h & 4h till high, 15m still high, 1d overbought
      & (
        (_cmp_cached_47)
        | (_cmp_cached_2)
        | (_cmp_cached_3)
        | (_cmp_cached_177)
        | (_cmp_cached_72)
        | (_cmp_cached_124)
        | (_cmp_cached_150)
        | (_cmp_cached_121)
      )
      # 15m & 1h & 4h & 1d down move, 4h & 1d still not low enough, 1d downtrend, 1h & 4h still high, 1d downtrend
      & (
        (_cmp_cached_47)
        | (_cmp_cached_2)
        | (_cmp_cached_3)
        | (_cmp_cached_59)
        | (_cmp_cached_6)
        | (_cmp_cached_7)
        | (_cmp_cached_60)
        | (_cmp_cached_111)
        | (_cmp_cached_161)
        | (_cmp_cached_62)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 1h & 4h downtrend, 1h high
      & (
        (_cmp_cached_47)
        | (_cmp_cached_2)
        | (_cmp_cached_41)
        | (_cmp_cached_102)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_174)
        | (_cmp_cached_110)
        | (_cmp_cached_134)
        | (_cmp_cached_154)
        | (_cmp_cached_9)
      )
      # 15m & 1h & 4h down move, 1h still not low enough, 1d overbought
      & (
        (_cmp_cached_47)
        | (_cmp_cached_2)
        | (_cmp_cached_41)
        | (_cmp_cached_166)
        | (_cmp_cached_151)
      )
      # 15m & 1h & 4h & 1d down move, 1h & 4h still not low enough, 1d still high, 1d downtrend, 1d overbought
      & (
        (_cmp_cached_47)
        | (_cmp_cached_2)
        | (_cmp_cached_83)
        | (_cmp_cached_158)
        | (_cmp_cached_6)
        | (_cmp_cached_229)
        | (_cmp_cached_230)
        | (_cmp_cached_231)
        | (_cmp_cached_8)
        | (_cmp_cached_9)
        | (_cmp_cached_162)
        | (_cmp_cached_232)
      )
      # 15m & 1h & 4h & 1d down move, 1h & 4h still not low enough, 15m & 1h downtrend, 1h & 4h still not low enough
      & (
        (_cmp_cached_47)
        | (_cmp_cached_2)
        | (_cmp_cached_52)
        | (_cmp_cached_97)
        | (_cmp_cached_92)
        | (_cmp_cached_6)
        | (_cmp_cached_114)
        | (_cmp_cached_94)
        | (_cmp_cached_82)
        | (_cmp_cached_113)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 1h still high, 4h high & overbought
      & (
        (_cmp_cached_47)
        | (_cmp_cached_2)
        | (_cmp_cached_24)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_72)
        | (_cmp_cached_130)
        | (_cmp_cached_126)
      )
      # 15m & 1h down move, 15m & 1h still not low enough, 4h still high, 15m still not low enough, 1h & 4h high
      & (
        (_cmp_cached_47)
        | (_cmp_cached_2)
        | (_cmp_cached_12)
        | (_cmp_cached_5)
        | (_cmp_cached_29)
        | (_cmp_cached_140)
        | (_cmp_cached_31)
        | (_cmp_cached_130)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 15m & 1h & 4h downtrend, 1d overbought
      & (
        (_cmp_cached_47)
        | (_cmp_cached_133)
        | (_cmp_cached_63)
        | (_cmp_cached_12)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_123)
        | (_cmp_cached_174)
        | (_cmp_cached_110)
        | (_cmp_cached_159)
      )
      # 15m & 1h & 4h down move, 1h still not low enough, 4h still high, 1h high, 1h & 4h downtrend, 1d overbought
      & (
        (_cmp_cached_47)
        | (_cmp_cached_133)
        | (_cmp_cached_63)
        | (_cmp_cached_5)
        | (_cmp_cached_18)
        | (_cmp_cached_134)
        | (_cmp_cached_119)
        | (_cmp_cached_162)
        | (_cmp_cached_27)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 15m & 1h downtrend
      & (
        (_cmp_cached_47)
        | (_cmp_cached_133)
        | (_cmp_cached_136)
        | (_cmp_cached_102)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_123)
        | (_cmp_cached_107)
        | (_cmp_cached_100)
        | (_cmp_cached_101)
        | (_cmp_cached_124)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 15m & 1h & 4h downtrend, 4h high
      & (
        (_cmp_cached_47)
        | (_cmp_cached_133)
        | (_cmp_cached_145)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_106)
        | (_cmp_cached_107)
        | (_cmp_cached_108)
        | (_cmp_cached_40)
      )
      # 15m & 1h down move, 15m still not low enough, 1h & 4h still high, 15m & 4h high
      & (
        (_cmp_cached_47)
        | (_cmp_cached_133)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_224)
        | (_cmp_cached_127)
      )
      # 15m & 1h down move, 1h still not low enough, 1h still high, 4h high & overbought, 1d downtrend
      & (
        (_cmp_cached_47)
        | (_cmp_cached_133)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_34)
        | (_cmp_cached_127)
        | (_cmp_cached_152)
        | (_cmp_cached_176)
      )
      # 15m & 1h down move, 15m still not low enough, 1h & 4h still high, 1d overbought
      & (
        (_cmp_cached_47)
        | (_cmp_cached_133)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_44)
        | (_cmp_cached_198)
      )
      # 15m & 1h & 1d down move, 1h & 4h still high, 15m downtrend, 1d overbought
      & (
        (_cmp_cached_47)
        | (_cmp_cached_133)
        | (_cmp_cached_125)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_177)
        | (_cmp_cached_27)
      )
      # 15m & 1h & 4h & 1d down move, 15m & 1h still high, 4h downtrend
      & (
        (_cmp_cached_47)
        | (_cmp_cached_96)
        | (_cmp_cached_41)
        | (_cmp_cached_117)
        | (_cmp_cached_39)
        | (_cmp_cached_44)
        | (_cmp_cached_233)
      )
      # 15m & 1h & 4h & 1d down move, 15m & 1h & 4h still not low enough, 4h still high, 1h & 4h downtrend, 1d overbought
      & (
        (_cmp_cached_47)
        | (_cmp_cached_96)
        | (_cmp_cached_41)
        | (_cmp_cached_120)
        | (_cmp_cached_102)
        | (_cmp_cached_92)
        | (_cmp_cached_93)
        | (_cmp_cached_88)
        | (_cmp_cached_74)
        | (_cmp_cached_167)
        | (_cmp_cached_234)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 15m stil high, 4h high
      & (
        (_cmp_cached_47)
        | (_cmp_cached_96)
        | (_cmp_cached_41)
        | (_cmp_cached_102)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_42)
        | (_cmp_cached_50)
        | (_cmp_cached_82)
        | (_cmp_cached_61)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 4h downtrend, 1h high, 4h downtrend
      & (
        (_cmp_cached_47)
        | (_cmp_cached_96)
        | (_cmp_cached_41)
        | (_cmp_cached_102)
        | (_cmp_cached_92)
        | (_cmp_cached_93)
        | (_cmp_cached_95)
        | (_cmp_cached_32)
        | (_cmp_cached_135)
      )
      # 15m & 1h & 4h down move, 1h & 4h still high, 15m & 1h downtrend, 1h & 4h high, 4h & 1d overbought
      & (
        (_cmp_cached_47)
        | (_cmp_cached_96)
        | (_cmp_cached_37)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_76)
        | (_cmp_cached_85)
        | (_cmp_cached_72)
        | (_cmp_cached_26)
        | (_cmp_cached_180)
        | (_cmp_cached_163)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 4h overbought
      & (
        (_cmp_cached_47)
        | (_cmp_cached_96)
        | (_cmp_cached_48)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_124)
        | (_cmp_cached_152)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h still high, 4h high, 4h & 1d overbought
      & (
        (_cmp_cached_47)
        | (_cmp_cached_96)
        | (_cmp_cached_136)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_189)
        | (_cmp_cached_180)
        | (_cmp_cached_159)
      )
      # 15m & 1h down move, 15m still not low enough, 1h & 4h still high, 15m & 1h high
      & (
        (_cmp_cached_47)
        | (_cmp_cached_96)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_68)
        | (_cmp_cached_38)
        | (_cmp_cached_219)
      )
      # 15m & 1h down move, 15m still not low enough, 1h still high, 4h high, 4h & 1d overbought
      & (
        (_cmp_cached_47)
        | (_cmp_cached_96)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_55)
        | (_cmp_cached_101)
        | (_cmp_cached_124)
        | (_cmp_cached_180)
        | (_cmp_cached_151)
      )
      # 15m & 1h down move, 15m still not low enough, 1h still high, 4h high, 4h overbought
      & (
        (_cmp_cached_47)
        | (_cmp_cached_96)
        | (_cmp_cached_12)
        | (_cmp_cached_28)
        | (_cmp_cached_55)
        | (_cmp_cached_50)
        | (_cmp_cached_82)
        | (_cmp_cached_61)
        | (_cmp_cached_152)
      )
      # 15m & 1h down move, 1h still high, 1h & 4h high, 4h & 1d overbought
      & (
        (_cmp_cached_47)
        | (_cmp_cached_96)
        | (_cmp_cached_17)
        | (_cmp_cached_55)
        | (_cmp_cached_128)
        | (_cmp_cached_130)
        | (_cmp_cached_180)
        | (_cmp_cached_27)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 15m & 4h still not low enough, 4h downtrend
      & (
        (_cmp_cached_47)
        | (_cmp_cached_64)
        | (_cmp_cached_83)
        | (_cmp_cached_12)
        | (_cmp_cached_5)
        | (_cmp_cached_18)
        | (_cmp_cached_140)
        | (_cmp_cached_149)
        | (_cmp_cached_223)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h downtrend, 4h still high, 15m still not low enough, 1h still high
      & (
        (_cmp_cached_47)
        | (_cmp_cached_64)
        | (_cmp_cached_37)
        | (_cmp_cached_123)
        | (_cmp_cached_85)
        | (_cmp_cached_122)
        | (_cmp_cached_88)
        | (_cmp_cached_13)
        | (_cmp_cached_160)
        | (_cmp_cached_167)
      )
      # 15m & 1h & 4h & 1d down move, 1d still high, 1h still high, 4h high
      & (
        (_cmp_cached_47)
        | (_cmp_cached_64)
        | (_cmp_cached_48)
        | (_cmp_cached_59)
        | (_cmp_cached_235)
        | (_cmp_cached_72)
        | (_cmp_cached_189)
      )
      # 15m & 1h & 4h & 1d down move, 15m still not low enough, 1h & 4h still high, 15m downtrend, 4h high
      & (
        (_cmp_cached_47)
        | (_cmp_cached_64)
        | (_cmp_cached_24)
        | (_cmp_cached_125)
        | (_cmp_cached_200)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_123)
        | (_cmp_cached_34)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 4h high & overbought
      & (
        (_cmp_cached_47)
        | (_cmp_cached_64)
        | (_cmp_cached_24)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_34)
        | (_cmp_cached_180)
      )
      # 15m & 1h down move, 15m & 1h & 4h still not low enough, 15m still high, 1h high, 1h & 4h still high, 1d downtrend
      & (
        (_cmp_cached_47)
        | (_cmp_cached_64)
        | (_cmp_cached_12)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_42)
        | (_cmp_cached_103)
        | (_cmp_cached_44)
        | (_cmp_cached_61)
        | (_cmp_cached_176)
      )
      # 15m & 1h down move, 15m still not low enough, 1h & 4h still high, 15m still not lowenough, 1h high, 1d overbought
      & (
        (_cmp_cached_47)
        | (_cmp_cached_64)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_91)
        | (_cmp_cached_128)
        | (_cmp_cached_27)
      )
      # 15m & 1h down move, 15m & 1h & 4h still high, 15m & 1h high, 4h overbought
      & (
        (_cmp_cached_47)
        | (_cmp_cached_64)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_38)
        | (_cmp_cached_219)
        | (_cmp_cached_126)
      )
      # 15m & 1h down move, 15m & 1h sitll high, 4h high, 1h & 4h high, 1h & 4h overbought
      & (
        (_cmp_cached_47)
        | (_cmp_cached_64)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_55)
        | (_cmp_cached_128)
        | (_cmp_cached_143)
        | (_cmp_cached_182)
        | (_cmp_cached_69)
      )
      # 15m & 4h down move, 15m & 1h & 4h still high, 4h downtrend, 15m & 1h still high, 4h downtrend
      & (
        (_cmp_cached_47)
        | (_cmp_cached_83)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_95)
        | (_cmp_cached_42)
        | (_cmp_cached_13)
        | (_cmp_cached_44)
        | (_cmp_cached_109)
      )
      # 15m & 1h & 4h down move, 15m downtrend, 15m still high, 1h overbought
      & (
        (_cmp_cached_47)
        | (_cmp_cached_23)
        | (_cmp_cached_37)
        | (_cmp_cached_76)
        | (_cmp_cached_42)
        | (_cmp_cached_121)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 4h downtrend
      & (
        (_cmp_cached_47)
        | (_cmp_cached_23)
        | (_cmp_cached_37)
        | (_cmp_cached_42)
        | (_cmp_cached_150)
        | (_cmp_cached_160)
        | (_cmp_cached_161)
        | (_cmp_cached_109)
      )
      # 15m & 1h & 4h down move, 4d downtrend, 1h high, 4h downtrend
      & (
        (_cmp_cached_47)
        | (_cmp_cached_23)
        | (_cmp_cached_37)
        | (_cmp_cached_236)
        | (_cmp_cached_187)
        | (_cmp_cached_167)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 4h downtrend, 15m high, 4h & 1d downtrend
      & (
        (_cmp_cached_47)
        | (_cmp_cached_23)
        | (_cmp_cached_52)
        | (_cmp_cached_12)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_236)
        | (_cmp_cached_38)
        | (_cmp_cached_109)
        | (_cmp_cached_176)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h still high, 4h high & overbought
      & (
        (_cmp_cached_47)
        | (_cmp_cached_23)
        | (_cmp_cached_136)
        | (_cmp_cached_12)
        | (_cmp_cached_140)
        | (_cmp_cached_72)
        | (_cmp_cached_189)
        | (_cmp_cached_69)
      )
      # 15m & 1h & 4h down move, 1h & 4h still high, 4h overbought
      & (
        (_cmp_cached_47)
        | (_cmp_cached_23)
        | (_cmp_cached_145)
        | (_cmp_cached_12)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_72)
        | (_cmp_cached_124)
        | (_cmp_cached_237)
        | (_cmp_cached_238)
        | (_cmp_cached_152)
      )
      # 15m & 1h & 4h down move, 15m & 1h still high, 4h high, 15m stil high, 4h high & overbought
      & (
        (_cmp_cached_47)
        | (_cmp_cached_23)
        | (_cmp_cached_145)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_68)
        | (_cmp_cached_42)
        | (_cmp_cached_34)
        | (_cmp_cached_132)
      )
      # 15m & 1h down move, 15m still not low enough, 1h & 4h still high, 15m downtrend, 1h & 4h high, 4h overbought
      & (
        (_cmp_cached_47)
        | (_cmp_cached_23)
        | (_cmp_cached_12)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_76)
        | (_cmp_cached_134)
        | (_cmp_cached_130)
        | (_cmp_cached_152)
      )
      # 15m & 1h & 4h & 1d down move, 15m & 1h & 4h still not low enough, 15m still high, 1h high, 4h & 1d downtrend
      & (
        (_cmp_cached_47)
        | (_cmp_cached_33)
        | (_cmp_cached_48)
        | (_cmp_cached_158)
        | (_cmp_cached_102)
        | (_cmp_cached_92)
        | (_cmp_cached_93)
        | (_cmp_cached_30)
        | (_cmp_cached_32)
        | (_cmp_cached_191)
        | (_cmp_cached_239)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 15m high, 1h still high, 4h overbought
      & (
        (_cmp_cached_47)
        | (_cmp_cached_33)
        | (_cmp_cached_24)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_38)
        | (_cmp_cached_160)
        | (_cmp_cached_126)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 15m & 4h high, 4h overbought
      & (
        (_cmp_cached_47)
        | (_cmp_cached_33)
        | (_cmp_cached_145)
        | (_cmp_cached_12)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_19)
        | (_cmp_cached_34)
        | (_cmp_cached_152)
      )
      # 15m & 1h & 1d down move, 15m still not low enough, 1h & 4h still high, 1h high, 4h downtrend, 1d overbought
      & (
        (_cmp_cached_47)
        | (_cmp_cached_33)
        | (_cmp_cached_158)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_134)
        | (_cmp_cached_109)
        | (_cmp_cached_159)
      )
      # 15m & 1h & 4h down move, 15m still not low, 1h & 4h sitll high, 15m & 1h downtrend, 15m still high, 4h high
      & (
        (_cmp_cached_47)
        | (_cmp_cached_51)
        | (_cmp_cached_52)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_123)
        | (_cmp_cached_85)
        | (_cmp_cached_39)
        | (_cmp_cached_35)
      )
      # 15m & 1h down move, 15m & 1h still high, 4h high, 15m still high, 1h & 4h high
      & (
        (_cmp_cached_47)
        | (_cmp_cached_51)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_68)
        | (_cmp_cached_30)
        | (_cmp_cached_31)
        | (_cmp_cached_130)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 1h & 1d overbought
      & (
        (_cmp_cached_47)
        | (_cmp_cached_54)
        | (_cmp_cached_24)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_144)
        | (_cmp_cached_151)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 1h high & overbought
      & (
        (_cmp_cached_47)
        | (_cmp_cached_54)
        | (_cmp_cached_24)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_30)
        | (_cmp_cached_31)
        | (_cmp_cached_144)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h downtrend, 15m & 1h high
      & (
        (_cmp_cached_47)
        | (_cmp_cached_54)
        | (_cmp_cached_24)
        | (_cmp_cached_25)
        | (_cmp_cached_174)
        | (_cmp_cached_110)
        | (_cmp_cached_38)
        | (_cmp_cached_103)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 15m still high, 4h downtrend
      & (
        (_cmp_cached_47)
        | (_cmp_cached_54)
        | (_cmp_cached_24)
        | (_cmp_cached_12)
        | (_cmp_cached_5)
        | (_cmp_cached_18)
        | (_cmp_cached_42)
        | (_cmp_cached_39)
        | (_cmp_cached_135)
      )
      # 15m & 1h & 4h down move, 1h & 4h high, 4h & 1d overbought
      & (
        (_cmp_cached_47)
        | (_cmp_cached_54)
        | (_cmp_cached_136)
        | (_cmp_cached_17)
        | (_cmp_cached_68)
        | (_cmp_cached_240)
        | (_cmp_cached_132)
        | (_cmp_cached_198)
      )
      # 15m & 1h down move, 15m & 1h stil high, 4h high, 1h & 4h overbought
      & (
        (_cmp_cached_47)
        | (_cmp_cached_54)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_55)
        | (_cmp_cached_50)
        | (_cmp_cached_222)
        | (_cmp_cached_183)
      )
      # 15m & 1h down move, 15m still not low enough, 1h still high, 4h high, 15m & 1h & 4h high
      & (
        (_cmp_cached_47)
        | (_cmp_cached_54)
        | (_cmp_cached_12)
        | (_cmp_cached_28)
        | (_cmp_cached_55)
        | (_cmp_cached_19)
        | (_cmp_cached_219)
        | (_cmp_cached_130)
      )
      # 15m & 1h down move, 15m & 1h still high, 4h high, 15m & 4h high, 15m & 1h still not low enough, 4h overbought
      & (
        (_cmp_cached_47)
        | (_cmp_cached_66)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_211)
        | (_cmp_cached_38)
        | (_cmp_cached_34)
        | (_cmp_cached_43)
        | (_cmp_cached_86)
        | (_cmp_cached_69)
      )
      # 15m & 1h down move, 15m & 1h still high, 4h high, 1h & 4h high, 1h overbought
      & (
        (_cmp_cached_47)
        | (_cmp_cached_66)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_68)
        | (_cmp_cached_128)
        | (_cmp_cached_34)
        | (_cmp_cached_213)
      )
      # 15m & 1h down move, 15m still high, 1h high & overbought
      & (
        (_cmp_cached_47)
        | (_cmp_cached_66)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_134)
        | (_cmp_cached_241)
      )
      # 15m & 1h down move, 15m still not low enough, 1h still high, 4h high & overbought
      & (
        (_cmp_cached_47)
        | (_cmp_cached_58)
        | (_cmp_cached_220)
        | (_cmp_cached_28)
        | (_cmp_cached_242)
        | (_cmp_cached_50)
        | (_cmp_cached_13)
        | (_cmp_cached_35)
        | (_cmp_cached_190)
      )
      # 15m & 1h down move, 15m still not low enough, 1h & 4h still high, 15m downtrend, 4h high & overbought
      & (
        (_cmp_cached_47)
        | (_cmp_cached_58)
        | (_cmp_cached_12)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_76)
        | (_cmp_cached_42)
        | (_cmp_cached_72)
        | (_cmp_cached_143)
        | (_cmp_cached_180)
      )
      # 15m & 1h down move, 15m still not low enough, 1h & 4h high, 15m still high, 1h & 4h high, 1d overbought
      & (
        (_cmp_cached_47)
        | (_cmp_cached_58)
        | (_cmp_cached_12)
        | (_cmp_cached_67)
        | (_cmp_cached_55)
        | (_cmp_cached_42)
        | (_cmp_cached_134)
        | (_cmp_cached_130)
        | (_cmp_cached_159)
      )
      # 15m & 4h down move, 15m & 1h & 4h sitll high, 4h high, 4h & 1d overbought
      & (
        (_cmp_cached_47)
        | (_cmp_cached_48)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_42)
        | (_cmp_cached_26)
        | (_cmp_cached_84)
        | (_cmp_cached_138)
      )
      # 15m & 4h & 1d down move, 15m & 1h & 4h s till high, 15m & 4h high
      & (
        (_cmp_cached_47)
        | (_cmp_cached_52)
        | (_cmp_cached_97)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_38)
        | (_cmp_cached_26)
        | (_cmp_cached_39)
      )
      # 15m & 4h down move, 15m & 1h still not low enough, 15m still high, 1h high, 4h downtrend
      & (
        (_cmp_cached_47)
        | (_cmp_cached_3)
        | (_cmp_cached_12)
        | (_cmp_cached_5)
        | (_cmp_cached_30)
        | (_cmp_cached_187)
        | (_cmp_cached_191)
      )
      # 15m & 4h down move, 15m & 1h still high, 4h downtrend
      & (
        (_cmp_cached_47)
        | (_cmp_cached_3)
        | (_cmp_cached_42)
        | (_cmp_cached_44)
        | (_cmp_cached_167)
      )
      # 15m &4d down move, 15m & 1h high, 4h downtrend
      & (
        (_cmp_cached_47)
        | (_cmp_cached_3)
        | (_cmp_cached_38)
        | (_cmp_cached_187)
        | (_cmp_cached_167)
      )
      # 15m & 4h down move, 4h still high, 4h downtrend, 1d overbought
      & (
        (_cmp_cached_47)
        | (_cmp_cached_3)
        | (_cmp_cached_124)
        | (_cmp_cached_167)
        | (_cmp_cached_121)
      )
      # 15m & 4h down move, 15m & 1h & 4h still high, 15m still not low enough, 4h still high, 4h overbought
      & (
        (_cmp_cached_47)
        | (_cmp_cached_37)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_140)
        | (_cmp_cached_124)
        | (_cmp_cached_152)
      )
      # 15m & 4h down move, 15m still not low enough, 1h & 4h still high, 15, & 4h still high, 1h high, 4h downtrend
      & (
        (_cmp_cached_47)
        | (_cmp_cached_37)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_42)
        | (_cmp_cached_124)
        | (_cmp_cached_187)
        | (_cmp_cached_109)
      )
      # 15m & 4h down move, 15m & 1h & 4h still high, 15m still high, 1h high, 4h overbought
      & (
        (_cmp_cached_47)
        | (_cmp_cached_24)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_42)
        | (_cmp_cached_219)
        | (_cmp_cached_204)
      )
      # 15m & 4h down move, 15m & 1h still not low enough, 1h still high & overbought
      & (
        (_cmp_cached_47)
        | (_cmp_cached_136)
        | (_cmp_cached_220)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_38)
        | (_cmp_cached_50)
        | (_cmp_cached_86)
        | (_cmp_cached_61)
        | (_cmp_cached_126)
      )
      # 15m & 4h down move, 15m still high, 1h still high, 4h high & overbought
      & (
        (_cmp_cached_47)
        | (_cmp_cached_145)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_68)
        | (_cmp_cached_140)
        | (_cmp_cached_26)
        | (_cmp_cached_190)
      )
      # 15m & 4h down move, 15m still not low enough, 1h & 4h high, 15m & 1h & 4h high
      & (
        (_cmp_cached_47)
        | (_cmp_cached_145)
        | (_cmp_cached_12)
        | (_cmp_cached_67)
        | (_cmp_cached_68)
        | (_cmp_cached_38)
        | (_cmp_cached_103)
        | (_cmp_cached_143)
      )
      # 15m down move, 15m still not low enough, 1h & 4h high, 1h & 4h overbought
      & (
        (_cmp_cached_47)
        | (_cmp_cached_12)
        | (_cmp_cached_181)
        | (_cmp_cached_55)
        | (_cmp_cached_31)
        | (_cmp_cached_189)
        | (_cmp_cached_225)
        | (_cmp_cached_183)
      )
      # 15m down move, 15m still high, 1h & 4h high, 4h overbought
      & (
        (_cmp_cached_47)
        | (_cmp_cached_16)
        | (_cmp_cached_67)
        | (_cmp_cached_141)
        | (_cmp_cached_34)
        | (_cmp_cached_160)
        | (_cmp_cached_127)
        | (_cmp_cached_243)
      )
      # 15m down move, 15m & 1h & 4h high, 1h & 4h overbought
      & (
        (_cmp_cached_47)
        | (_cmp_cached_244)
        | (_cmp_cached_67)
        | (_cmp_cached_68)
        | (_cmp_cached_134)
        | (_cmp_cached_130)
        | (_cmp_cached_225)
        | (_cmp_cached_183)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 4h overbought
      & (
        (_cmp_cached_53)
        | (_cmp_cached_133)
        | (_cmp_cached_83)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_124)
        | (_cmp_cached_204)
      )
      # 15m & 1h & 4h down move, 15m & 1h still not low enough, 4h still high, 1h high, 1d overbought
      & (
        (_cmp_cached_53)
        | (_cmp_cached_133)
        | (_cmp_cached_48)
        | (_cmp_cached_12)
        | (_cmp_cached_5)
        | (_cmp_cached_18)
        | (_cmp_cached_157)
        | (_cmp_cached_121)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 15m high, 1h & 4h still high
      & (
        (_cmp_cached_53)
        | (_cmp_cached_133)
        | (_cmp_cached_48)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_19)
        | (_cmp_cached_72)
        | (_cmp_cached_88)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 15m & 1h & 4h high
      & (
        (_cmp_cached_53)
        | (_cmp_cached_133)
        | (_cmp_cached_136)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_19)
        | (_cmp_cached_31)
        | (_cmp_cached_189)
      )
      # 15m & 1h & 4h & 1d down move, 15m & 1h still not low enough, 4h still high, 1d overbought
      & (
        (_cmp_cached_53)
        | (_cmp_cached_133)
        | (_cmp_cached_63)
        | (_cmp_cached_125)
        | (_cmp_cached_200)
        | (_cmp_cached_5)
        | (_cmp_cached_18)
        | (_cmp_cached_13)
        | (_cmp_cached_156)
      )
      # 15m & 1h & 1d down move, 1h & 4h still high, 1d downtrend, 1h high, 1h & 4h still high, 1d downtrend
      & (
        (_cmp_cached_53)
        | (_cmp_cached_133)
        | (_cmp_cached_59)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_60)
        | (_cmp_cached_157)
        | (_cmp_cached_160)
        | (_cmp_cached_61)
        | (_cmp_cached_62)
      )
      # 15m & 1h down move, 15m still not low enough, 1h stil high, 4h high & overbought
      & (
        (_cmp_cached_53)
        | (_cmp_cached_133)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_55)
        | (_cmp_cached_111)
        | (_cmp_cached_189)
        | (_cmp_cached_204)
      )
      # 15m & 1h down move, 15m still not low enough, 1h still high, 4h high, 4h overbought
      & (
        (_cmp_cached_53)
        | (_cmp_cached_133)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_141)
        | (_cmp_cached_72)
        | (_cmp_cached_130)
        | (_cmp_cached_69)
      )
      # 15m & 1h & 4h & 1d down move, 15m & 1h still not low enough, 4h stil high, 15m still high, 1d overbought
      & (
        (_cmp_cached_53)
        | (_cmp_cached_96)
        | (_cmp_cached_41)
        | (_cmp_cached_164)
        | (_cmp_cached_12)
        | (_cmp_cached_5)
        | (_cmp_cached_18)
        | (_cmp_cached_39)
        | (_cmp_cached_159)
      )
      # 15m & 1h & 4h & 1d down move, 15m & 1h & 4h downtrend, 4h downtrend
      & (
        (_cmp_cached_53)
        | (_cmp_cached_96)
        | (_cmp_cached_41)
        | (_cmp_cached_117)
        | (_cmp_cached_80)
        | (_cmp_cached_115)
        | (_cmp_cached_236)
        | (_cmp_cached_135)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 1h still high, 1d overbought
      & (
        (_cmp_cached_53)
        | (_cmp_cached_96)
        | (_cmp_cached_41)
        | (_cmp_cached_12)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_44)
        | (_cmp_cached_121)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 1h still high
      & (
        (_cmp_cached_53)
        | (_cmp_cached_96)
        | (_cmp_cached_37)
        | (_cmp_cached_12)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_25)
        | (_cmp_cached_72)
        | (_cmp_cached_44)
      )
      # 15m & 1h & 4h down move, 1h still not low enough, 4h still high, 15m downtrend, 15m still not low enough
      & (
        (_cmp_cached_53)
        | (_cmp_cached_96)
        | (_cmp_cached_37)
        | (_cmp_cached_5)
        | (_cmp_cached_18)
        | (_cmp_cached_80)
        | (_cmp_cached_100)
        | (_cmp_cached_101)
        | (_cmp_cached_124)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h stil high, 4h high, 4h overbought
      & (
        (_cmp_cached_53)
        | (_cmp_cached_96)
        | (_cmp_cached_52)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_72)
        | (_cmp_cached_43)
        | (_cmp_cached_40)
        | (_cmp_cached_132)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 15m still not low, 4h high, 1h still high
      & (
        (_cmp_cached_53)
        | (_cmp_cached_96)
        | (_cmp_cached_145)
        | (_cmp_cached_102)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_100)
        | (_cmp_cached_50)
        | (_cmp_cached_160)
      )
      # 15m & 1h down move, 15m still not low enough, 1h still high, 4h high & overbought
      & (
        (_cmp_cached_53)
        | (_cmp_cached_96)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_55)
        | (_cmp_cached_134)
        | (_cmp_cached_130)
        | (_cmp_cached_183)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 15m still high, 4h downtrend, 1d overbought
      & (
        (_cmp_cached_53)
        | (_cmp_cached_64)
        | (_cmp_cached_83)
        | (_cmp_cached_12)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_42)
        | (_cmp_cached_109)
        | (_cmp_cached_121)
      )
      # 15m & 1h & 4h down move, 15m & 1h still not low enough, 4h still high, 1h still high, 15m still high
      & (
        (_cmp_cached_53)
        | (_cmp_cached_64)
        | (_cmp_cached_83)
        | (_cmp_cached_12)
        | (_cmp_cached_5)
        | (_cmp_cached_18)
        | (_cmp_cached_72)
        | (_cmp_cached_150)
      )
      # 15m & 1h & 4h down move, 1h still not low enough, 4h still high, 4h & 1d overbought
      & (
        (_cmp_cached_53)
        | (_cmp_cached_64)
        | (_cmp_cached_83)
        | (_cmp_cached_5)
        | (_cmp_cached_29)
        | (_cmp_cached_124)
        | (_cmp_cached_126)
        | (_cmp_cached_121)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h still high, 4h high & overbought
      & (
        (_cmp_cached_53)
        | (_cmp_cached_64)
        | (_cmp_cached_37)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_50)
        | (_cmp_cached_57)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 15m & 1h & 4h still high, 1d downtrend
      & (
        (_cmp_cached_53)
        | (_cmp_cached_64)
        | (_cmp_cached_37)
        | (_cmp_cached_12)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_30)
        | (_cmp_cached_72)
        | (_cmp_cached_44)
        | (_cmp_cached_61)
        | (_cmp_cached_194)
      )
      # 15m & 1h & 1d down move, 15m still not low enough, 1h & 4h still high, 1d downtrend, 1h high, 1d overbought
      & (
        (_cmp_cached_53)
        | (_cmp_cached_64)
        | (_cmp_cached_245)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_60)
        | (_cmp_cached_42)
        | (_cmp_cached_31)
        | (_cmp_cached_146)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 4h & 1d overbought
      & (
        (_cmp_cached_53)
        | (_cmp_cached_64)
        | (_cmp_cached_145)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_68)
        | (_cmp_cached_38)
        | (_cmp_cached_26)
        | (_cmp_cached_180)
        | (_cmp_cached_146)
      )
      # 15m & 1h & 1d down move, 4h & 1d downtrend, 1h & 4h high, 1d downtrend
      & (
        (_cmp_cached_53)
        | (_cmp_cached_64)
        | (_cmp_cached_11)
        | (_cmp_cached_246)
        | (_cmp_cached_208)
        | (_cmp_cached_142)
        | (_cmp_cached_35)
        | (_cmp_cached_247)
      )
      # 15m & 1h down move, 15m still not low enough, 1h & 4h still high, 15m & 1h & 4h downtrend, 4h high
      & (
        (_cmp_cached_53)
        | (_cmp_cached_64)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_25)
        | (_cmp_cached_174)
        | (_cmp_cached_110)
        | (_cmp_cached_101)
        | (_cmp_cached_34)
      )
      # 15m & 1h down move, 15m still not low enough, 1h still high, 4h high, 4h & 1d overbought
      & (
        (_cmp_cached_53)
        | (_cmp_cached_64)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_55)
        | (_cmp_cached_34)
        | (_cmp_cached_57)
        | (_cmp_cached_121)
      )
      # 15m & 1h down move, 15m still not low enough, 1h & 4h high, 1h & 4h overbought
      & (
        (_cmp_cached_53)
        | (_cmp_cached_64)
        | (_cmp_cached_12)
        | (_cmp_cached_28)
        | (_cmp_cached_141)
        | (_cmp_cached_72)
        | (_cmp_cached_143)
        | (_cmp_cached_43)
        | (_cmp_cached_127)
        | (_cmp_cached_182)
        | (_cmp_cached_248)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 1h & 4h downtrend
      & (
        (_cmp_cached_53)
        | (_cmp_cached_23)
        | (_cmp_cached_10)
        | (_cmp_cached_102)
        | (_cmp_cached_92)
        | (_cmp_cached_93)
        | (_cmp_cached_107)
        | (_cmp_cached_122)
        | (_cmp_cached_140)
        | (_cmp_cached_86)
        | (_cmp_cached_77)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 4h high, 4h overbought
      & (
        (_cmp_cached_53)
        | (_cmp_cached_23)
        | (_cmp_cached_136)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_72)
        | (_cmp_cached_189)
        | (_cmp_cached_43)
        | (_cmp_cached_69)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 4h high & overbought
      & (
        (_cmp_cached_53)
        | (_cmp_cached_23)
        | (_cmp_cached_136)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_26)
        | (_cmp_cached_132)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 4h high, 4h & 1d overbought
      & (
        (_cmp_cached_53)
        | (_cmp_cached_23)
        | (_cmp_cached_136)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_50)
        | (_cmp_cached_84)
        | (_cmp_cached_159)
      )
      # 15m & 1h down move, 15m sitll not low enough, 1h still high, 4h high, 15m & 1h downtrend, 15m & 1h still high
      & (
        (_cmp_cached_53)
        | (_cmp_cached_23)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_68)
        | (_cmp_cached_76)
        | (_cmp_cached_85)
        | (_cmp_cached_42)
        | (_cmp_cached_44)
      )
      # 15m & 1h down move, 15m still not low enough, 1h & 4h still high, 15m & 1h high, 1d overbought
      & (
        (_cmp_cached_53)
        | (_cmp_cached_23)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_68)
        | (_cmp_cached_38)
        | (_cmp_cached_219)
        | (_cmp_cached_27)
      )
      # 15m & 1h & 4h down move, 15m & 1h still not low enough, 4h still high, 4h overbought
      & (
        (_cmp_cached_53)
        | (_cmp_cached_33)
        | (_cmp_cached_48)
        | (_cmp_cached_102)
        | (_cmp_cached_5)
        | (_cmp_cached_29)
        | (_cmp_cached_124)
        | (_cmp_cached_43)
        | (_cmp_cached_77)
        | (_cmp_cached_126)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 1h & 4h downtrend, 15m high, 4h downtrend
      & (
        (_cmp_cached_53)
        | (_cmp_cached_33)
        | (_cmp_cached_48)
        | (_cmp_cached_12)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_85)
        | (_cmp_cached_99)
        | (_cmp_cached_38)
        | (_cmp_cached_39)
        | (_cmp_cached_167)
      )
      # 15m & 1h & 4h, 15m still not low enough, 1h & 4h still high, 15m downtrend, 15m & 4h high
      & (
        (_cmp_cached_53)
        | (_cmp_cached_33)
        | (_cmp_cached_48)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_25)
        | (_cmp_cached_42)
        | (_cmp_cached_35)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h still high, 4h high & overbought
      & (
        (_cmp_cached_53)
        | (_cmp_cached_33)
        | (_cmp_cached_48)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_72)
        | (_cmp_cached_189)
        | (_cmp_cached_204)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 15m still high, 4h high & overbought
      & (
        (_cmp_cached_53)
        | (_cmp_cached_33)
        | (_cmp_cached_24)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_30)
        | (_cmp_cached_34)
        | (_cmp_cached_35)
        | (_cmp_cached_126)
      )
      # 15m & 1h & 1d down move, 15m & 1h & 4h still high, 15m & 1d downtrend
      & (
        (_cmp_cached_53)
        | (_cmp_cached_33)
        | (_cmp_cached_125)
        | (_cmp_cached_16)
        | (_cmp_cached_168)
        | (_cmp_cached_196)
        | (_cmp_cached_91)
        | (_cmp_cached_128)
        | (_cmp_cached_249)
        | (_cmp_cached_194)
      )
      # 15m & 1h down move, 15m & 1h & 4h stil high, 15m & 1h & 4h high, 1d downtrend
      & (
        (_cmp_cached_53)
        | (_cmp_cached_33)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_38)
        | (_cmp_cached_250)
        | (_cmp_cached_40)
        | (_cmp_cached_176)
      )
      # 15m & 1h down move, 15m & 1h & 4h still high, 1h & 4h high, 4h overbought
      & (
        (_cmp_cached_53)
        | (_cmp_cached_33)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_134)
        | (_cmp_cached_50)
        | (_cmp_cached_32)
        | (_cmp_cached_40)
        | (_cmp_cached_69)
      )
      # 15m & 1h & 4h & 1d down move, 15m & 1h still not low enough, 4h still high, 4h downtrend, 4h high, 1d overbought
      & (
        (_cmp_cached_53)
        | (_cmp_cached_51)
        | (_cmp_cached_52)
        | (_cmp_cached_97)
        | (_cmp_cached_102)
        | (_cmp_cached_92)
        | (_cmp_cached_18)
        | (_cmp_cached_110)
        | (_cmp_cached_134)
        | (_cmp_cached_156)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h still high, 4h high
      & (
        (_cmp_cached_53)
        | (_cmp_cached_51)
        | (_cmp_cached_136)
        | (_cmp_cached_12)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_30)
        | (_cmp_cached_111)
        | (_cmp_cached_124)
        | (_cmp_cached_160)
        | (_cmp_cached_35)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 15m & 1h high, 4h overbought
      & (
        (_cmp_cached_53)
        | (_cmp_cached_51)
        | (_cmp_cached_136)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_38)
        | (_cmp_cached_103)
        | (_cmp_cached_126)
      )
      # 15m & 1h down move, 15m & 1h & 4h still high, 15m & 1h & 4h high, 4h overbought
      & (
        (_cmp_cached_53)
        | (_cmp_cached_51)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_38)
        | (_cmp_cached_157)
        | (_cmp_cached_130)
        | (_cmp_cached_152)
      )
      # 15m & 1h down move, 15m & 1h still high, 4h high, 4h & 1d overbought
      & (
        (_cmp_cached_53)
        | (_cmp_cached_51)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_55)
        | (_cmp_cached_128)
        | (_cmp_cached_180)
        | (_cmp_cached_121)
      )
      # 15m & 1h down move, 15m & 1h & 4h still high, 15m & 1h high, 1h & 4h overbought
      & (
        (_cmp_cached_53)
        | (_cmp_cached_51)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_38)
        | (_cmp_cached_219)
        | (_cmp_cached_144)
        | (_cmp_cached_126)
      )
      # 15m & 1h down move, 15m still not low enough, 1h & 4h still high, 1h & 4h downtrend, 4h high & overbought
      & (
        (_cmp_cached_53)
        | (_cmp_cached_51)
        | (_cmp_cached_12)
        | (_cmp_cached_28)
        | (_cmp_cached_68)
        | (_cmp_cached_174)
        | (_cmp_cached_110)
        | (_cmp_cached_101)
        | (_cmp_cached_189)
        | (_cmp_cached_69)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h high, 4h downtrend
      & (
        (_cmp_cached_53)
        | (_cmp_cached_54)
        | (_cmp_cached_24)
        | (_cmp_cached_43)
        | (_cmp_cached_187)
        | (_cmp_cached_191)
      )
      # 15m & 1h down move, 15m still high, 1h & 4h high, 1h overbought, 1d downtrend
      & (
        (_cmp_cached_53)
        | (_cmp_cached_54)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_134)
        | (_cmp_cached_143)
        | (_cmp_cached_182)
        | (_cmp_cached_239)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h high, 4h downtrend
      & (
        (_cmp_cached_53)
        | (_cmp_cached_66)
        | (_cmp_cached_136)
        | (_cmp_cached_38)
        | (_cmp_cached_150)
        | (_cmp_cached_250)
        | (_cmp_cached_40)
        | (_cmp_cached_203)
      )
      # 15m & 1h down move, 15m & 1h still high, 4h high, 1h & 4h high, 4h overbought
      & (
        (_cmp_cached_53)
        | (_cmp_cached_66)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_55)
        | (_cmp_cached_128)
        | (_cmp_cached_130)
        | (_cmp_cached_44)
        | (_cmp_cached_127)
        | (_cmp_cached_248)
      )
      # 15m & 1h down move, 15m & 1hstill high, 4h downtrend, 15m still high, 1h high
      & (
        (_cmp_cached_53)
        | (_cmp_cached_66)
        | (_cmp_cached_244)
        | (_cmp_cached_28)
        | (_cmp_cached_110)
        | (_cmp_cached_42)
        | (_cmp_cached_31)
        | (_cmp_cached_43)
        | (_cmp_cached_32)
      )
      # 15m & 1h down move, 1h & 4h high, 4h overbought
      & (
        (_cmp_cached_53)
        | (_cmp_cached_66)
        | (_cmp_cached_28)
        | (_cmp_cached_55)
        | (_cmp_cached_128)
        | (_cmp_cached_143)
        | (_cmp_cached_251)
      )
      # 15m & 1h down move, 15m still high, 1h & 4h high, 1h & 4h & 1d overbought
      & (
        (_cmp_cached_53)
        | (_cmp_cached_58)
        | (_cmp_cached_16)
        | (_cmp_cached_67)
        | (_cmp_cached_55)
        | (_cmp_cached_128)
        | (_cmp_cached_130)
        | (_cmp_cached_182)
        | (_cmp_cached_183)
        | (_cmp_cached_221)
      )
      # 15m & 4h down move, 15m high, 1h still not low enough, 4h downtrend
      & (
        (_cmp_cached_53)
        | (_cmp_cached_214)
        | (_cmp_cached_38)
        | (_cmp_cached_150)
        | (_cmp_cached_82)
        | (_cmp_cached_167)
      )
      # 15m & 4h down move, 15m & 1h high, 4h downtrend
      & (
        (_cmp_cached_53)
        | (_cmp_cached_10)
        | (_cmp_cached_19)
        | (_cmp_cached_150)
        | (_cmp_cached_187)
        | (_cmp_cached_167)
      )
      # 15m & 4h & 1d down move, 15m still high, 1h & 4h downtrend
      & (
        (_cmp_cached_53)
        | (_cmp_cached_79)
        | (_cmp_cached_45)
        | (_cmp_cached_16)
        | (_cmp_cached_85)
        | (_cmp_cached_122)
        | (_cmp_cached_42)
        | (_cmp_cached_39)
      )
      # 15m & 4h & 1d down move, 15m high, 1d overbought
      & (
        (_cmp_cached_53)
        | (_cmp_cached_63)
        | (_cmp_cached_117)
        | (_cmp_cached_38)
        | (_cmp_cached_159)
      )
      # 15m & 4h down move, 15m & 1h still high, 15m & 1h high, 4h downtrend
      & (
        (_cmp_cached_53)
        | (_cmp_cached_214)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_38)
        | (_cmp_cached_150)
        | (_cmp_cached_32)
        | (_cmp_cached_191)
      )
      # 15m & 4h down move, 15m & 1h still not low enough, 4h still high,  1h & 4h downtrend, 15m & 1h & 4h still high
      & (
        (_cmp_cached_53)
        | (_cmp_cached_63)
        | (_cmp_cached_102)
        | (_cmp_cached_5)
        | (_cmp_cached_18)
        | (_cmp_cached_174)
        | (_cmp_cached_110)
        | (_cmp_cached_140)
        | (_cmp_cached_101)
        | (_cmp_cached_88)
      )
      # 15m & 4h down move, 15m & 1h & 4h still high, 1h & 4h downtrend
      & (
        (_cmp_cached_53)
        | (_cmp_cached_63)
        | (_cmp_cached_150)
        | (_cmp_cached_160)
        | (_cmp_cached_61)
        | (_cmp_cached_148)
        | (_cmp_cached_167)
      )
      # 15m & 4h down move, 15m & 1h & 4h still high, 15m & 4h high, 1d overbought
      & (
        (_cmp_cached_53)
        | (_cmp_cached_41)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_38)
        | (_cmp_cached_50)
        | (_cmp_cached_159)
      )
      # 15m & 4h down move, 15m & 1h & 4h still high, 15m & 1h high, 1h overbought
      & (
        (_cmp_cached_53)
        | (_cmp_cached_136)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_42)
        | (_cmp_cached_31)
        | (_cmp_cached_187)
        | (_cmp_cached_144)
      )
      # 15m & 4h down move, 15m & 1h & 4h still high, 15m & 4h high, 4h & 1d overbought
      & (
        (_cmp_cached_53)
        | (_cmp_cached_136)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_38)
        | (_cmp_cached_50)
        | (_cmp_cached_132)
        | (_cmp_cached_151)
      )
      # 15m & 4h down move, 15m still not low enough, 1h & 4h still high, 15m & 1h & 4h still high, 4h overbought
      & (
        (_cmp_cached_53)
        | (_cmp_cached_145)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_38)
        | (_cmp_cached_44)
        | (_cmp_cached_61)
        | (_cmp_cached_183)
      )
      # 15m & 1d down move, 1h & 4h still not low enough, 1h & 4h downtrend, 4h still high
      & (
        (_cmp_cached_53)
        | (_cmp_cached_59)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_252)
        | (_cmp_cached_253)
        | (_cmp_cached_184)
        | (_cmp_cached_122)
        | (_cmp_cached_72)
        | (_cmp_cached_82)
        | (_cmp_cached_161)
      )
      # 15m down move, 15m & 1h & 4h still high, 15m & 1h & 4h high, 1h & 4h high, 4h overbought
      & (
        (_cmp_cached_53)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_19)
        | (_cmp_cached_134)
        | (_cmp_cached_50)
        | (_cmp_cached_44)
        | (_cmp_cached_40)
        | (_cmp_cached_180)
      )
      # 15m down move, 15m & 1h & 4h still high, 15m & 1h downtrend, 4h high, 15m & 1h still high
      & (
        (_cmp_cached_53)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_76)
        | (_cmp_cached_174)
        | (_cmp_cached_50)
        | (_cmp_cached_150)
        | (_cmp_cached_160)
      )
      # 15m down move, 15m still high, 1h >& 4h high, 15m & 1h & 4h high, 4h overbought
      & (
        (_cmp_cached_53)
        | (_cmp_cached_16)
        | (_cmp_cached_67)
        | (_cmp_cached_68)
        | (_cmp_cached_38)
        | (_cmp_cached_134)
        | (_cmp_cached_130)
        | (_cmp_cached_86)
        | (_cmp_cached_40)
        | (_cmp_cached_132)
      )
      # 15m down move, 15m still high, 1h & 4h high, 4h overbought
      & (
        (_cmp_cached_53)
        | (_cmp_cached_16)
        | (_cmp_cached_67)
        | (_cmp_cached_141)
        | (_cmp_cached_38)
        | (_cmp_cached_34)
        | (_cmp_cached_39)
        | (_cmp_cached_132)
      )
      # 15m down move, 15m still high, 1h & 4h high, 1d downtrend, 4h overbought
      & (
        (_cmp_cached_53)
        | (_cmp_cached_16)
        | (_cmp_cached_181)
        | (_cmp_cached_242)
        | (_cmp_cached_230)
        | (_cmp_cached_143)
        | (_cmp_cached_183)
      )
      # 15m down move, 15m & 1h high, 1h & 4h overbought
      & (
        (_cmp_cached_53)
        | (_cmp_cached_188)
        | (_cmp_cached_219)
        | (_cmp_cached_104)
        | (_cmp_cached_144)
        | (_cmp_cached_180)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 15m & 4h downtrend, 1h & 4h still not low enough
      & (
        (_cmp_cached_36)
        | (_cmp_cached_89)
        | (_cmp_cached_79)
        | (_cmp_cached_139)
        | (_cmp_cached_92)
        | (_cmp_cached_93)
        | (_cmp_cached_80)
        | (_cmp_cached_99)
        | (_cmp_cached_86)
        | (_cmp_cached_77)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enugh, 4h still high, 15m still high, 1h & 4h downtrend
      & (
        (_cmp_cached_36)
        | (_cmp_cached_89)
        | (_cmp_cached_79)
        | (_cmp_cached_102)
        | (_cmp_cached_92)
        | (_cmp_cached_6)
        | (_cmp_cached_254)
        | (_cmp_cached_88)
        | (_cmp_cached_39)
        | (_cmp_cached_148)
        | (_cmp_cached_167)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 1h downtrend
      & (
        (_cmp_cached_36)
        | (_cmp_cached_96)
        | (_cmp_cached_41)
        | (_cmp_cached_102)
        | (_cmp_cached_92)
        | (_cmp_cached_93)
        | (_cmp_cached_140)
        | (_cmp_cached_13)
        | (_cmp_cached_86)
        | (_cmp_cached_77)
        | (_cmp_cached_74)
      )
      # 15m & 1h & 4h down move, 15m & 1h still not low enough, 4h still high, 15m & 1h & 4h downtrend
      & (
        (_cmp_cached_36)
        | (_cmp_cached_96)
        | (_cmp_cached_41)
        | (_cmp_cached_102)
        | (_cmp_cached_92)
        | (_cmp_cached_29)
        | (_cmp_cached_255)
        | (_cmp_cached_119)
        | (_cmp_cached_203)
      )
      # 15m & 1h & 4h & 1d down move, 15m & 1h & 4h still not low enough, 15m still high, 1h & 4h & 1d downtrend
      & (
        (_cmp_cached_36)
        | (_cmp_cached_96)
        | (_cmp_cached_41)
        | (_cmp_cached_117)
        | (_cmp_cached_200)
        | (_cmp_cached_201)
        | (_cmp_cached_202)
        | (_cmp_cached_30)
        | (_cmp_cached_74)
        | (_cmp_cached_203)
        | (_cmp_cached_62)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 1h & 4h downtrend, 4h downtrend
      & (
        (_cmp_cached_36)
        | (_cmp_cached_96)
        | (_cmp_cached_41)
        | (_cmp_cached_12)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_85)
        | (_cmp_cached_122)
        | (_cmp_cached_88)
        | (_cmp_cached_77)
        | (_cmp_cached_109)
      )
      # 15m & 1h & 4h & 1d down move, 15m still not low enough, 1h & 4h still high, 15m downtrend, 4h high
      & (
        (_cmp_cached_36)
        | (_cmp_cached_96)
        | (_cmp_cached_37)
        | (_cmp_cached_164)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_106)
        | (_cmp_cached_50)
        | (_cmp_cached_256)
        | (_cmp_cached_238)
      )
      # 15m & 1h & 4h down move, 15m & 1h still not low enough, 4h still high, 15m & 4h high, 4h overbought
      & (
        (_cmp_cached_36)
        | (_cmp_cached_96)
        | (_cmp_cached_37)
        | (_cmp_cached_12)
        | (_cmp_cached_5)
        | (_cmp_cached_18)
        | (_cmp_cached_38)
        | (_cmp_cached_34)
        | (_cmp_cached_132)
      )
      # 15m & 1h & 4h & 1d down move, 15m & 1h & 4h still not low enough, 4h downtrend, 1d high
      & (
        (_cmp_cached_36)
        | (_cmp_cached_96)
        | (_cmp_cached_48)
        | (_cmp_cached_158)
        | (_cmp_cached_12)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_95)
        | (_cmp_cached_178)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 15m still not low enough, 4h high & overbought
      & (
        (_cmp_cached_36)
        | (_cmp_cached_96)
        | (_cmp_cached_52)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_91)
        | (_cmp_cached_50)
        | (_cmp_cached_57)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 1d overbought
      & (
        (_cmp_cached_36)
        | (_cmp_cached_96)
        | (_cmp_cached_136)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_43)
        | (_cmp_cached_27)
      )
      # 15m & 1h down move, 15m still not low enough, 1h & 4h still high, 15m & 1h downtrend, 15m & 4h high
      & (
        (_cmp_cached_36)
        | (_cmp_cached_96)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_25)
        | (_cmp_cached_87)
        | (_cmp_cached_38)
        | (_cmp_cached_26)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 1h & 4h high
      & (
        (_cmp_cached_36)
        | (_cmp_cached_64)
        | (_cmp_cached_83)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_134)
        | (_cmp_cached_130)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h stil high, 15m high, 4h downtrend
      & (
        (_cmp_cached_36)
        | (_cmp_cached_64)
        | (_cmp_cached_52)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_38)
        | (_cmp_cached_135)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 4h high, 4h & 1d overbought
      & (
        (_cmp_cached_36)
        | (_cmp_cached_64)
        | (_cmp_cached_24)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_101)
        | (_cmp_cached_189)
        | (_cmp_cached_180)
        | (_cmp_cached_27)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 15m & 4h high, 1h still not low enough, 4h high
      & (
        (_cmp_cached_36)
        | (_cmp_cached_64)
        | (_cmp_cached_136)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_38)
        | (_cmp_cached_26)
        | (_cmp_cached_86)
        | (_cmp_cached_35)
      )
      # 15m & 1h down move, 15m & 1h & 4h still high, 1h & 4h downtrend, 15m & 1h high
      & (
        (_cmp_cached_36)
        | (_cmp_cached_64)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_174)
        | (_cmp_cached_110)
        | (_cmp_cached_38)
        | (_cmp_cached_219)
      )
      # 15m & 1h down move, 15m still not low enough, 1h sitll high, 1h & 4h high, 4h overbought
      & (
        (_cmp_cached_36)
        | (_cmp_cached_64)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_141)
        | (_cmp_cached_128)
        | (_cmp_cached_130)
        | (_cmp_cached_180)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 15m & 1h still high, 4h high
      & (
        (_cmp_cached_36)
        | (_cmp_cached_23)
        | (_cmp_cached_37)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_42)
        | (_cmp_cached_72)
        | (_cmp_cached_39)
        | (_cmp_cached_35)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 15h & 4h high
      & (
        (_cmp_cached_36)
        | (_cmp_cached_23)
        | (_cmp_cached_37)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_38)
        | (_cmp_cached_50)
        | (_cmp_cached_39)
      )
      # 15m & 1h & 4h down move, 15m high
      & (
        (_cmp_cached_36)
        | (_cmp_cached_23)
        | (_cmp_cached_37)
        | (_cmp_cached_19)
        | (_cmp_cached_20)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 1h high
      & (
        (_cmp_cached_36)
        | (_cmp_cached_23)
        | (_cmp_cached_52)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_42)
        | (_cmp_cached_219)
        | (_cmp_cached_44)
        | (_cmp_cached_61)
      )
      # 15m & 1h & 4h down move, 15m still low, 1h & 4h still high, 4h high & overbought
      & (
        (_cmp_cached_36)
        | (_cmp_cached_23)
        | (_cmp_cached_52)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_34)
        | (_cmp_cached_190)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h stil high, 15m & 4h still high, 4h overbought
      & (
        (_cmp_cached_36)
        | (_cmp_cached_23)
        | (_cmp_cached_52)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_42)
        | (_cmp_cached_124)
        | (_cmp_cached_180)
      )
      # 15m & 1h & 4h & 1d down move, 15m & 1h & 4h high, 1d downtrend
      & (
        (_cmp_cached_36)
        | (_cmp_cached_33)
        | (_cmp_cached_48)
        | (_cmp_cached_158)
        | (_cmp_cached_38)
        | (_cmp_cached_31)
        | (_cmp_cached_130)
        | (_cmp_cached_176)
      )
      # 15m & 1h & 4h & 1d down move, 15m still not low enough, 1h & 4h still high, 4h downtrend, 1d overbought
      & (
        (_cmp_cached_36)
        | (_cmp_cached_33)
        | (_cmp_cached_48)
        | (_cmp_cached_97)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_109)
        | (_cmp_cached_159)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 15m high
      & (
        (_cmp_cached_36)
        | (_cmp_cached_33)
        | (_cmp_cached_52)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_19)
        | (_cmp_cached_39)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h stil high, 15m & 4h still high, 4h overbought
      & (
        (_cmp_cached_36)
        | (_cmp_cached_33)
        | (_cmp_cached_136)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_42)
        | (_cmp_cached_50)
        | (_cmp_cached_180)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 15m & 1h high, 4h & 1d overbought
      & (
        (_cmp_cached_36)
        | (_cmp_cached_33)
        | (_cmp_cached_145)
        | (_cmp_cached_12)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_38)
        | (_cmp_cached_219)
        | (_cmp_cached_126)
        | (_cmp_cached_156)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 1d overbought
      & (
        (_cmp_cached_36)
        | (_cmp_cached_33)
        | (_cmp_cached_145)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_237)
        | (_cmp_cached_238)
        | (_cmp_cached_151)
      )
      # 15m & 1h & 4h down move, 15m & 1h still high, 1h & 4h high, 4h overbought
      & (
        (_cmp_cached_36)
        | (_cmp_cached_33)
        | (_cmp_cached_145)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_68)
        | (_cmp_cached_128)
        | (_cmp_cached_204)
      )
      # 15m & 1h down move, 15m still not low enough, 1h & 4h still high, 15m downtrend, 15m still high, 1h high
      & (
        (_cmp_cached_36)
        | (_cmp_cached_33)
        | (_cmp_cached_102)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_25)
        | (_cmp_cached_42)
        | (_cmp_cached_219)
      )
      # 15m & 1h down move, 15m still not low enough, 1h stil high, 4h high, 1h downtrend
      & (
        (_cmp_cached_36)
        | (_cmp_cached_33)
        | (_cmp_cached_12)
        | (_cmp_cached_28)
        | (_cmp_cached_141)
        | (_cmp_cached_174)
        | (_cmp_cached_111)
        | (_cmp_cached_34)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 1h & 4h high, 1d overbought
      & (
        (_cmp_cached_36)
        | (_cmp_cached_51)
        | (_cmp_cached_52)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_157)
        | (_cmp_cached_130)
        | (_cmp_cached_27)
      )
      # 15m & 1h down move, 15m still not low enough, 1h & 4h still high, 1h high, 1h & 1d overbought
      & (
        (_cmp_cached_36)
        | (_cmp_cached_51)
        | (_cmp_cached_12)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_157)
        | (_cmp_cached_182)
        | (_cmp_cached_27)
      )
      # 15m & 1h & 4h & 1d down move, 15m & 4h downtrend, 15m & 1h high
      & (
        (_cmp_cached_36)
        | (_cmp_cached_54)
        | (_cmp_cached_24)
        | (_cmp_cached_125)
        | (_cmp_cached_25)
        | (_cmp_cached_122)
        | (_cmp_cached_38)
        | (_cmp_cached_219)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 15m high
      & (
        (_cmp_cached_36)
        | (_cmp_cached_54)
        | (_cmp_cached_24)
        | (_cmp_cached_12)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_257)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 1h & 4h downtrend, 1h high, 4h downtrend
      & (
        (_cmp_cached_36)
        | (_cmp_cached_54)
        | (_cmp_cached_145)
        | (_cmp_cached_12)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_85)
        | (_cmp_cached_95)
        | (_cmp_cached_128)
        | (_cmp_cached_109)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 1h & 4h high, 4h overbought
      & (
        (_cmp_cached_36)
        | (_cmp_cached_54)
        | (_cmp_cached_145)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_157)
        | (_cmp_cached_189)
        | (_cmp_cached_44)
        | (_cmp_cached_35)
        | (_cmp_cached_132)
      )
      # 15m & 1h & 4h down move, 15m & 1h still not low enough, 4h still high, 4h downtrend, 1h still high
      & (
        (_cmp_cached_36)
        | (_cmp_cached_66)
        | (_cmp_cached_136)
        | (_cmp_cached_102)
        | (_cmp_cached_5)
        | (_cmp_cached_18)
        | (_cmp_cached_99)
        | (_cmp_cached_111)
        | (_cmp_cached_44)
      )
      # 15m & 1h down move, 15m & 1h & 4h still high, 4h high, 4h & 1d overbought
      & (
        (_cmp_cached_36)
        | (_cmp_cached_66)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_50)
        | (_cmp_cached_183)
        | (_cmp_cached_198)
      )
      # 15m & 1h down move, 15m still high, 1h & 4h high & overbought
      & (
        (_cmp_cached_36)
        | (_cmp_cached_66)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_141)
        | (_cmp_cached_157)
        | (_cmp_cached_143)
        | (_cmp_cached_225)
        | (_cmp_cached_190)
      )
      # 15m & 1h down move, 15m still high, 1h & 4h high, 4h overbought
      & (
        (_cmp_cached_36)
        | (_cmp_cached_58)
        | (_cmp_cached_16)
        | (_cmp_cached_67)
        | (_cmp_cached_141)
        | (_cmp_cached_143)
        | (_cmp_cached_258)
      )
      # 15m & 4h down move, 15m & 1h & 4h still high, 15m still high
      & (
        (_cmp_cached_36)
        | (_cmp_cached_215)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_42)
        | (_cmp_cached_43)
      )
      # 15m & 4h down move, 15m & 1h high, 4h downtrend
      & (
        (_cmp_cached_36)
        | (_cmp_cached_79)
        | (_cmp_cached_42)
        | (_cmp_cached_13)
        | (_cmp_cached_187)
        | (_cmp_cached_223)
      )
      # 15m & 4h down move, 15m & 1h still high, 1h & 4h downtrend, 15m & 1h still high
      & (
        (_cmp_cached_36)
        | (_cmp_cached_41)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_174)
        | (_cmp_cached_99)
        | (_cmp_cached_38)
        | (_cmp_cached_39)
        | (_cmp_cached_44)
      )
      # 15m & 4h down move, 15m & 1h & 4h still high, 15m & 4h high
      & (
        (_cmp_cached_36)
        | (_cmp_cached_41)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_38)
        | (_cmp_cached_50)
      )
      # 15m & 1h down move, 15m still high, 1h & 4h high & overbought
      & (
        (_cmp_cached_36)
        | (_cmp_cached_58)
        | (_cmp_cached_16)
        | (_cmp_cached_67)
        | (_cmp_cached_242)
        | (_cmp_cached_128)
        | (_cmp_cached_130)
        | (_cmp_cached_222)
        | (_cmp_cached_152)
      )
      # 15m & 4h down move, 15m & 1h & 4h still high, 15m high
      & (
        (_cmp_cached_36)
        | (_cmp_cached_48)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_188)
        | (_cmp_cached_39)
      )
      # 15m & 4h down move, 15m & 1h & 4h stil high, 14m & 4h high
      & (
        (_cmp_cached_36)
        | (_cmp_cached_24)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_19)
        | (_cmp_cached_143)
        | (_cmp_cached_39)
        | (_cmp_cached_40)
      )
      # 15m & 4h down move, 15m still not low enough, 1h & 4h still high, 15m & 4h high, 1d overbought
      & (
        (_cmp_cached_36)
        | (_cmp_cached_136)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_19)
        | (_cmp_cached_149)
        | (_cmp_cached_151)
      )
      # 15m down move, 15m still not low enough, 1h & 4h high
      & (
        (_cmp_cached_36)
        | (_cmp_cached_12)
        | (_cmp_cached_181)
        | (_cmp_cached_55)
        | (_cmp_cached_128)
        | (_cmp_cached_130)
        | (_cmp_cached_187)
        | (_cmp_cached_40)
      )
      # 15m down move, 15m & 1h & 4h still high, 15m high, 15m & 1h still high, 4h high, 4h overbought
      & (
        (_cmp_cached_36)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_19)
        | (_cmp_cached_150)
        | (_cmp_cached_160)
        | (_cmp_cached_35)
        | (_cmp_cached_180)
      )
      # 15m & 1h down move, 15m & 1h still high, 1h & 4h high, 4h overbought
      & (
        (_cmp_cached_259)
        | (_cmp_cached_2)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_68)
        | (_cmp_cached_128)
        | (_cmp_cached_130)
        | (_cmp_cached_180)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 15m & 4h still high, 1d downtrend
      & (
        (_cmp_cached_259)
        | (_cmp_cached_64)
        | (_cmp_cached_83)
        | (_cmp_cached_12)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_42)
        | (_cmp_cached_150)
        | (_cmp_cached_61)
        | (_cmp_cached_176)
      )
      # 15m & 1h & 4h down move, 15m & 1h still not low enough, 4h high, 1d overbought
      & (
        (_cmp_cached_259)
        | (_cmp_cached_64)
        | (_cmp_cached_48)
        | (_cmp_cached_102)
        | (_cmp_cached_5)
        | (_cmp_cached_68)
        | (_cmp_cached_151)
      )
      # 15m & 1h & 4h down move, 15m & 1h still high, 4h high, 15m & 4h high, 4h overbought
      & (
        (_cmp_cached_259)
        | (_cmp_cached_64)
        | (_cmp_cached_145)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_55)
        | (_cmp_cached_38)
        | (_cmp_cached_50)
        | (_cmp_cached_180)
      )
      # 15m & 1h down move, 15m still not low enough, 1h still high, 15m high, 4h high & overbought
      & (
        (_cmp_cached_259)
        | (_cmp_cached_23)
        | (_cmp_cached_12)
        | (_cmp_cached_28)
        | (_cmp_cached_141)
        | (_cmp_cached_38)
        | (_cmp_cached_50)
        | (_cmp_cached_40)
        | (_cmp_cached_152)
      )
      # 15m & 1h & 4h down move, 15m & 1h high
      & (
        (_cmp_cached_259)
        | (_cmp_cached_33)
        | (_cmp_cached_48)
        | (_cmp_cached_19)
        | (_cmp_cached_219)
        | (_cmp_cached_43)
        | (_cmp_cached_32)
      )
      # 15m & 1h & 4h & 1d down move, 15m & 1h & 4h still high, 15m & 1h high, 1d overbought
      & (
        (_cmp_cached_259)
        | (_cmp_cached_33)
        | (_cmp_cached_48)
        | (_cmp_cached_158)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_38)
        | (_cmp_cached_134)
        | (_cmp_cached_159)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still highm 15m & 1h high, 1h still high, 4h high
      & (
        (_cmp_cached_259)
        | (_cmp_cached_33)
        | (_cmp_cached_48)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_38)
        | (_cmp_cached_31)
        | (_cmp_cached_160)
        | (_cmp_cached_35)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 15m & 4h high, 4h & 1d overbought
      & (
        (_cmp_cached_259)
        | (_cmp_cached_33)
        | (_cmp_cached_24)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_38)
        | (_cmp_cached_26)
        | (_cmp_cached_126)
        | (_cmp_cached_159)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 15m & 4h high, 1d overbought
      & (
        (_cmp_cached_259)
        | (_cmp_cached_33)
        | (_cmp_cached_24)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_19)
        | (_cmp_cached_189)
        | (_cmp_cached_39)
        | (_cmp_cached_234)
      )
      # 15m & 1h down move, 15m still not low enough, 1h & 4h still high, 1h & 4h downtrend, 1h still high, 4h high
      & (
        (_cmp_cached_259)
        | (_cmp_cached_33)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_87)
        | (_cmp_cached_87)
        | (_cmp_cached_72)
        | (_cmp_cached_34)
      )
      # 15m & 1h down move, 15m still not low enough, 1h still high, 4h high & overbought
      & (
        (_cmp_cached_259)
        | (_cmp_cached_33)
        | (_cmp_cached_12)
        | (_cmp_cached_28)
        | (_cmp_cached_141)
        | (_cmp_cached_260)
        | (_cmp_cached_261)
        | (_cmp_cached_57)
      )
      # 15m & 1h & 4h down move, 15m high
      & (
        (_cmp_cached_259)
        | (_cmp_cached_51)
        | (_cmp_cached_52)
        | (_cmp_cached_262)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 15m high, 1d overbought
      & (
        (_cmp_cached_259)
        | (_cmp_cached_51)
        | (_cmp_cached_136)
        | (_cmp_cached_244)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_19)
        | (_cmp_cached_27)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 15m & 1h & 4h still high
      & (
        (_cmp_cached_259)
        | (_cmp_cached_54)
        | (_cmp_cached_63)
        | (_cmp_cached_12)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_49)
        | (_cmp_cached_160)
        | (_cmp_cached_61)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h stil high, 1h & 4h high, 1h overbought
      & (
        (_cmp_cached_259)
        | (_cmp_cached_54)
        | (_cmp_cached_24)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_140)
        | (_cmp_cached_128)
        | (_cmp_cached_34)
        | (_cmp_cached_144)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 15m still high, 4h overbought
      & (
        (_cmp_cached_259)
        | (_cmp_cached_54)
        | (_cmp_cached_24)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_42)
        | (_cmp_cached_39)
        | (_cmp_cached_57)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 15m & 4h high, 1d overbought
      & (
        (_cmp_cached_259)
        | (_cmp_cached_54)
        | (_cmp_cached_136)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_38)
        | (_cmp_cached_50)
        | (_cmp_cached_263)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 15m & 1h high
      & (
        (_cmp_cached_259)
        | (_cmp_cached_66)
        | (_cmp_cached_136)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_19)
        | (_cmp_cached_103)
        | (_cmp_cached_39)
        | (_cmp_cached_32)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 4h downtrend, 15m high
      & (
        (_cmp_cached_259)
        | (_cmp_cached_66)
        | (_cmp_cached_136)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_110)
        | (_cmp_cached_38)
        | (_cmp_cached_20)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 15m still not low enough, 4h & 1h still high, 1d overbought
      & (
        (_cmp_cached_259)
        | (_cmp_cached_66)
        | (_cmp_cached_136)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_100)
        | (_cmp_cached_88)
        | (_cmp_cached_44)
        | (_cmp_cached_198)
      )
      # 15m & 1h down move, 15m & 1h & 4h high, 1h overbought
      & (
        (_cmp_cached_259)
        | (_cmp_cached_58)
        | (_cmp_cached_244)
        | (_cmp_cached_128)
        | (_cmp_cached_143)
        | (_cmp_cached_182)
      )
      # 15m & 4h down move, 15m & 1h high, 4h downtrend
      & (
        (_cmp_cached_259)
        | (_cmp_cached_10)
        | (_cmp_cached_38)
        | (_cmp_cached_39)
        | (_cmp_cached_187)
        | (_cmp_cached_167)
      )
      # 15m & 4h down move, 15m still high, 1h high, 15m & 1h high
      & (
        (_cmp_cached_259)
        | (_cmp_cached_83)
        | (_cmp_cached_16)
        | (_cmp_cached_181)
        | (_cmp_cached_38)
        | (_cmp_cached_219)
      )
      # 15m & 4h down move, 15m still not low enough, 1h & 4h still high, 15m & 1h high
      & (
        (_cmp_cached_259)
        | (_cmp_cached_83)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_19)
        | (_cmp_cached_219)
      )
      # 15m & 4h down move, 15m still not low enough, 1h & 4h still high, 1h & 4h downtrend, 15m & 1h still high
      & (
        (_cmp_cached_259)
        | (_cmp_cached_83)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_94)
        | (_cmp_cached_95)
        | (_cmp_cached_42)
        | (_cmp_cached_72)
        | (_cmp_cached_39)
      )
      # 15m & 4h down move, 15m & 1h & 4h still high, 15m & 1h high, 4h downtrend
      & (
        (_cmp_cached_259)
        | (_cmp_cached_48)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_38)
        | (_cmp_cached_150)
        | (_cmp_cached_32)
        | (_cmp_cached_109)
      )
      # 15m down move, 15m still high, 1h & 4h high, 1h & 4h overbought
      & (
        (_cmp_cached_259)
        | (_cmp_cached_244)
        | (_cmp_cached_67)
        | (_cmp_cached_55)
        | (_cmp_cached_128)
        | (_cmp_cached_130)
        | (_cmp_cached_250)
        | (_cmp_cached_173)
        | (_cmp_cached_182)
        | (_cmp_cached_180)
      )
      # 15m down move, 15m & 1h still high, 4h high, 15m downtrend, 15m high, 1h & 4h overbought
      & (
        (_cmp_cached_259)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_68)
        | (_cmp_cached_123)
        | (_cmp_cached_19)
        | (_cmp_cached_213)
        | (_cmp_cached_57)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 15m downtrend, 4h high & overbought
      & (
        (_cmp_cached_264)
        | (_cmp_cached_23)
        | (_cmp_cached_37)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_80)
        | (_cmp_cached_50)
        | (_cmp_cached_204)
      )
      # 15m & 1h & 4h down move, 15m & 1h sitll not low enough, 4h still high, 15m high
      & (
        (_cmp_cached_264)
        | (_cmp_cached_23)
        | (_cmp_cached_37)
        | (_cmp_cached_12)
        | (_cmp_cached_5)
        | (_cmp_cached_18)
        | (_cmp_cached_88)
        | (_cmp_cached_20)
      )
      # 15m & 1h & 4h & 1d down move, 1d downtrend, 4h still not low enough, 15m still high, 1h downtrend
      & (
        (_cmp_cached_264)
        | (_cmp_cached_23)
        | (_cmp_cached_48)
        | (_cmp_cached_158)
        | (_cmp_cached_265)
        | (_cmp_cached_149)
        | (_cmp_cached_39)
        | (_cmp_cached_266)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h downtrend, 4h high
      & (
        (_cmp_cached_264)
        | (_cmp_cached_23)
        | (_cmp_cached_48)
        | (_cmp_cached_114)
        | (_cmp_cached_115)
        | (_cmp_cached_236)
        | (_cmp_cached_240)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 4h high & overbought
      & (
        (_cmp_cached_264)
        | (_cmp_cached_23)
        | (_cmp_cached_136)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_140)
        | (_cmp_cached_34)
        | (_cmp_cached_183)
      )
      # 15m & 1h down move, 15m still not low enough, 1h still high, 4h high & overbought
      & (
        (_cmp_cached_264)
        | (_cmp_cached_23)
        | (_cmp_cached_12)
        | (_cmp_cached_28)
        | (_cmp_cached_267)
        | (_cmp_cached_143)
        | (_cmp_cached_57)
      )
      # 15m & 1h down move, 15m still not low enough, 1h still high, 4h high, 15m still high, 4h high & overbought
      & (
        (_cmp_cached_22)
        | (_cmp_cached_51)
        | (_cmp_cached_12)
        | (_cmp_cached_28)
        | (_cmp_cached_55)
        | (_cmp_cached_30)
        | (_cmp_cached_34)
        | (_cmp_cached_190)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 15m high, 1h & 4h downtrend
      & (
        (_cmp_cached_264)
        | (_cmp_cached_33)
        | (_cmp_cached_48)
        | (_cmp_cached_102)
        | (_cmp_cached_92)
        | (_cmp_cached_6)
        | (_cmp_cached_49)
        | (_cmp_cached_197)
        | (_cmp_cached_135)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 15m & 1h high
      & (
        (_cmp_cached_264)
        | (_cmp_cached_33)
        | (_cmp_cached_48)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_38)
        | (_cmp_cached_219)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h high
      & (
        (_cmp_cached_264)
        | (_cmp_cached_33)
        | (_cmp_cached_24)
        | (_cmp_cached_38)
        | (_cmp_cached_219)
        | (_cmp_cached_130)
      )
      # 15m & 1h & 4h & 1d down move, 15m & 1h & 4h still high, 15m & 1h high, 1d overbought
      & (
        (_cmp_cached_264)
        | (_cmp_cached_51)
        | (_cmp_cached_136)
        | (_cmp_cached_164)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_38)
        | (_cmp_cached_31)
        | (_cmp_cached_159)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 4h downtrend, 4h overbought
      & (
        (_cmp_cached_264)
        | (_cmp_cached_51)
        | (_cmp_cached_136)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_108)
        | (_cmp_cached_124)
        | (_cmp_cached_13)
        | (_cmp_cached_61)
        | (_cmp_cached_132)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 4h high & overbought
      & (
        (_cmp_cached_264)
        | (_cmp_cached_54)
        | (_cmp_cached_24)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_34)
        | (_cmp_cached_183)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 1h & 4h downtrend, 1h high, 4h overbought
      & (
        (_cmp_cached_264)
        | (_cmp_cached_58)
        | (_cmp_cached_145)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_174)
        | (_cmp_cached_99)
        | (_cmp_cached_100)
        | (_cmp_cached_134)
        | (_cmp_cached_126)
      )
      # 15m & 1h down move, 15m & 1h & 4h still high, 15m still high, 1h high, 1h overbought
      & (
        (_cmp_cached_264)
        | (_cmp_cached_58)
        | (_cmp_cached_244)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_42)
        | (_cmp_cached_31)
        | (_cmp_cached_13)
        | (_cmp_cached_187)
        | (_cmp_cached_182)
      )
      # 15m &4h down move, 15m & 1h & 4h still high, 15m still high, 1h high, 15m & 1h overbought
      & (
        (_cmp_cached_264)
        | (_cmp_cached_52)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_30)
        | (_cmp_cached_128)
        | (_cmp_cached_268)
        | (_cmp_cached_222)
      )
      # 15m & 4h down move, 15m & 1h & 4h still high, 15m & 1h high, 1h overbought
      & (
        (_cmp_cached_264)
        | (_cmp_cached_24)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_38)
        | (_cmp_cached_32)
        | (_cmp_cached_182)
      )
      # 15m & 1d down move, 15m & 1h & 4h stil high, 4h high, 15m & 1h & 4h still high
      & (
        (_cmp_cached_264)
        | (_cmp_cached_4)
        | (_cmp_cached_244)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_34)
        | (_cmp_cached_39)
        | (_cmp_cached_44)
        | (_cmp_cached_61)
      )
      # 15m down move, 15m & 1h still high, 4h high & overbought
      & (
        (_cmp_cached_264)
        | (_cmp_cached_244)
        | (_cmp_cached_28)
        | (_cmp_cached_267)
        | (_cmp_cached_111)
        | (_cmp_cached_189)
        | (_cmp_cached_190)
      )
      # 15m down move, 15m still high, 1h & 4h high & overbought
      & (
        (_cmp_cached_264)
        | (_cmp_cached_244)
        | (_cmp_cached_181)
        | (_cmp_cached_141)
        | (_cmp_cached_134)
        | (_cmp_cached_130)
        | (_cmp_cached_269)
        | (_cmp_cached_57)
      )
      # 15m down move, 15m & 1h & 4h still high, 15m & 1h & 4h high
      & (
        (_cmp_cached_264)
        | (_cmp_cached_244)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_38)
        | (_cmp_cached_219)
        | (_cmp_cached_130)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still high, 15m & 4h still high, 4h & 1d overbought
      & (
        (_cmp_cached_270)
        | (_cmp_cached_33)
        | (_cmp_cached_145)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_42)
        | (_cmp_cached_124)
        | (_cmp_cached_152)
        | (_cmp_cached_121)
      )
      # 15m & 1h down move, 15m & 1h & 4h still high, 15m & 1h & 4h downtrend, 4h high
      & (
        (_cmp_cached_270)
        | (_cmp_cached_33)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_123)
        | (_cmp_cached_174)
        | (_cmp_cached_110)
        | (_cmp_cached_34)
        | (_cmp_cached_127)
      )
      # 15m & 1h down move, 15m & 1h & 4h still high, 1h & 4h & 1d downtrend, 1h & 4h high
      & (
        (_cmp_cached_270)
        | (_cmp_cached_33)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_174)
        | (_cmp_cached_110)
        | (_cmp_cached_271)
        | (_cmp_cached_134)
        | (_cmp_cached_143)
      )
      # 15m & 1h down move, 1h & 4h still high, 4h high, 1h & 4h overbought
      & (
        (_cmp_cached_270)
        | (_cmp_cached_33)
        | (_cmp_cached_28)
        | (_cmp_cached_68)
        | (_cmp_cached_34)
        | (_cmp_cached_40)
        | (_cmp_cached_192)
        | (_cmp_cached_190)
      )
      # 15m & 1h & 4h & 1d down move, 15m still not low enough, 1h & 4h still high, 15m still high, 1d overbought
      & (
        (_cmp_cached_270)
        | (_cmp_cached_51)
        | (_cmp_cached_52)
        | (_cmp_cached_97)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_39)
        | (_cmp_cached_27)
      )
      # 15m & 1h & 4h down move, 15m & 1h & 4h still not low enough, 15m still high, 4h high & overbought
      & (
        (_cmp_cached_270)
        | (_cmp_cached_54)
        | (_cmp_cached_52)
        | (_cmp_cached_12)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_42)
        | (_cmp_cached_50)
        | (_cmp_cached_152)
      )
      # 15m & 1h down move, 15m & 1h still high, 4h high, 1h & 4h high, 1h & 4h overbought
      & (
        (_cmp_cached_270)
        | (_cmp_cached_66)
        | (_cmp_cached_244)
        | (_cmp_cached_28)
        | (_cmp_cached_55)
        | (_cmp_cached_134)
        | (_cmp_cached_143)
        | (_cmp_cached_192)
        | (_cmp_cached_57)
      )
      # 15m & 1h down move, 15m still high, 1h high, 15m overbought
      & (
        (_cmp_cached_270)
        | (_cmp_cached_66)
        | (_cmp_cached_42)
        | (_cmp_cached_219)
        | (_cmp_cached_39)
        | (_cmp_cached_187)
        | (_cmp_cached_272)
      )
      # 15m & 4h down move, 15m & 1h & 4h still not low enough, 15m & 1h & 4h downtrend, 1h & 4h still high
      & (
        (_cmp_cached_270)
        | (_cmp_cached_48)
        | (_cmp_cached_12)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_106)
        | (_cmp_cached_94)
        | (_cmp_cached_273)
        | (_cmp_cached_13)
        | (_cmp_cached_44)
        | (_cmp_cached_61)
      )
      # 15m down move, 15m & 1h & 4h high, 15m & 1h high, 4h & 1d overbought
      & (
        (_cmp_cached_270)
        | (_cmp_cached_244)
        | (_cmp_cached_67)
        | (_cmp_cached_55)
        | (_cmp_cached_19)
        | (_cmp_cached_219)
        | (_cmp_cached_126)
        | (_cmp_cached_234)
      )
      # 15m down move, 15m & 1h & 4h high, 1h & 4h high, 1h & 4h overbought
      & (
        (_cmp_cached_270)
        | (_cmp_cached_244)
        | (_cmp_cached_181)
        | (_cmp_cached_141)
        | (_cmp_cached_128)
        | (_cmp_cached_130)
        | (_cmp_cached_222)
        | (_cmp_cached_190)
      )
      # 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 15m downtrend, 15m & 4h high
      & (
        (_cmp_cached_274)
        | (_cmp_cached_54)
        | (_cmp_cached_136)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_123)
        | (_cmp_cached_101)
        | (_cmp_cached_189)
        | (_cmp_cached_20)
      )
      # 15m & 1h down move, 15m & 1h & 4h high, 1h & 4h overbought
      & (
        (_cmp_cached_274)
        | (_cmp_cached_58)
        | (_cmp_cached_244)
        | (_cmp_cached_67)
        | (_cmp_cached_141)
        | (_cmp_cached_134)
        | (_cmp_cached_130)
        | (_cmp_cached_192)
        | (_cmp_cached_204)
      )
      # 1h & 4h down move, 15m high
      & ((_cmp_cached_71) | (_cmp_cached_214) | (_cmp_cached_39))
      # 1h & 4h down move, 4h still not low enough
      & ((_cmp_cached_71) | (_cmp_cached_214) | (_cmp_cached_81))
      # 1h & 4h down move, 15m still not low enough, 4h downtrend
      & ((_cmp_cached_71) | (_cmp_cached_215) | (_cmp_cached_12) | (_cmp_cached_99))
      # 1h & 4h down move, 1h downtrend, 4h still high
      & ((_cmp_cached_71) | (_cmp_cached_3) | (_cmp_cached_87) | (_cmp_cached_124))
      # 1h & 4h down move, 1h still not low enough, 4h still high, 1d overbought
      & (
        (_cmp_cached_71)
        | (_cmp_cached_83)
        | (_cmp_cached_5)
        | (_cmp_cached_29)
        | (_cmp_cached_27)
      )
      # 1h & 4h & 1d down move, 1d still not low enough, 1d downtrend
      & (
        (_cmp_cached_75)
        | (_cmp_cached_215)
        | (_cmp_cached_275)
        | (_cmp_cached_276)
        | (_cmp_cached_239)
      )
      # 1h & 4h down move, 1h & 4h downtrend
      & ((_cmp_cached_75) | (_cmp_cached_10) | (_cmp_cached_277) | (_cmp_cached_278))
      # 1h & 4h down move, 15m & 1h & 4h downtrend, 1h & 4h still high
      & (
        (_cmp_cached_75)
        | (_cmp_cached_3)
        | (_cmp_cached_76)
        | (_cmp_cached_85)
        | (_cmp_cached_122)
        | (_cmp_cached_72)
        | (_cmp_cached_124)
      )
      # 1h & 4h down move, 15m & 1hg downtrend, 4h downtrend
      & (
        (_cmp_cached_75)
        | (_cmp_cached_3)
        | (_cmp_cached_114)
        | (_cmp_cached_115)
        | (_cmp_cached_109)
      )
      # 1h & 4h down move, 1h still high, 4h high, 1d overbought
      & (
        (_cmp_cached_75)
        | (_cmp_cached_41)
        | (_cmp_cached_72)
        | (_cmp_cached_189)
        | (_cmp_cached_159)
      )
      # 1h & 4h down move, 1h & 4h still high, 4h high, 15m & 1h downtrend
      & (
        (_cmp_cached_75)
        | (_cmp_cached_37)
        | (_cmp_cached_111)
        | (_cmp_cached_88)
        | (_cmp_cached_35)
        | (_cmp_cached_73)
        | (_cmp_cached_148)
      )
      # 1h & 4h down move, 15m & 1h still not low enough, 4h high, 1d overbought
      & (
        (_cmp_cached_75)
        | (_cmp_cached_48)
        | (_cmp_cached_12)
        | (_cmp_cached_5)
        | (_cmp_cached_29)
        | (_cmp_cached_50)
        | (_cmp_cached_121)
      )
      # 1h & 4h down move, 15m & 1h & 4h downtrend, 1h high
      & (
        (_cmp_cached_78)
        | (_cmp_cached_3)
        | (_cmp_cached_279)
        | (_cmp_cached_87)
        | (_cmp_cached_99)
        | (_cmp_cached_157)
      )
      # 1h & 4h down move, 1h & 4h downtrend, 1h high
      & (
        (_cmp_cached_78)
        | (_cmp_cached_3)
        | (_cmp_cached_115)
        | (_cmp_cached_236)
        | (_cmp_cached_157)
      )
      # 1h & 4h & 1d down move, 1h & 4h still not low enough, 1h & 4h downtrend, 1h still not low enough
      & (
        (_cmp_cached_89)
        | (_cmp_cached_79)
        | (_cmp_cached_45)
        | (_cmp_cached_92)
        | (_cmp_cached_93)
        | (_cmp_cached_174)
        | (_cmp_cached_122)
        | (_cmp_cached_82)
      )
      # 1h & 4h down move, 1h & 4h still not low enough, 15m high, 1h & 4h downtrend
      & (
        (_cmp_cached_89)
        | (_cmp_cached_79)
        | (_cmp_cached_56)
        | (_cmp_cached_81)
        | (_cmp_cached_257)
        | (_cmp_cached_197)
        | (_cmp_cached_167)
      )
      # 1h & 4h down move, 15m & 1h still not low enough, 4h still high, 1h & 4h downtrend
      & (
        (_cmp_cached_89)
        | (_cmp_cached_136)
        | (_cmp_cached_102)
        | (_cmp_cached_92)
        | (_cmp_cached_18)
        | (_cmp_cached_85)
        | (_cmp_cached_110)
        | (_cmp_cached_101)
        | (_cmp_cached_160)
        | (_cmp_cached_119)
      )
      # 1h & 4h down move, 1h still not low enough, 4h downtrend
      & (
        (_cmp_cached_2)
        | (_cmp_cached_214)
        | (_cmp_cached_86)
        | (_cmp_cached_191)
      )
      # 1h & 4h down move, 1h & 4h downtrend, 1h high, 4h downtrend
      & (
        (_cmp_cached_2)
        | (_cmp_cached_41)
        | (_cmp_cached_85)
        | (_cmp_cached_95)
        | (_cmp_cached_128)
        | (_cmp_cached_167)
      )
      # 1h & 4h & 1d down move, 1h & 4h still not low enough, 1d high & overbought
      & (
        (_cmp_cached_2)
        | (_cmp_cached_37)
        | (_cmp_cached_164)
        | (_cmp_cached_5)
        | (_cmp_cached_18)
        | (_cmp_cached_88)
        | (_cmp_cached_165)
        | (_cmp_cached_121)
      )
      # 1h & 1d down move, 15m & 1h & 4h still not low enough, 15m & 1h downtrend, 1h still high
      & (
        (_cmp_cached_2)
        | (_cmp_cached_117)
        | (_cmp_cached_139)
        | (_cmp_cached_92)
        | (_cmp_cached_6)
        | (_cmp_cached_80)
        | (_cmp_cached_87)
        | (_cmp_cached_160)
      )
      # 1h & 4h & 1d down move, 1h still not low enough, 4h still high, 1d downtrend
      & (
        (_cmp_cached_133)
        | (_cmp_cached_63)
        | (_cmp_cached_117)
        | (_cmp_cached_86)
        | (_cmp_cached_61)
        | (_cmp_cached_239)
      )
      # 1h & 4h down move, 1h & 4h still not low enough, 4h still high, 1h & 4h downtrend, 1d overbought
      & (
        (_cmp_cached_133)
        | (_cmp_cached_63)
        | (_cmp_cached_102)
        | (_cmp_cached_92)
        | (_cmp_cached_18)
        | (_cmp_cached_148)
        | (_cmp_cached_109)
        | (_cmp_cached_27)
      )
      # 5m & 15m & 1h & 4h down move, 15m downtrend, 4h high, 1d overbought
      & (
        (_cmp_cached_133)
        | (_cmp_cached_63)
        | (_cmp_cached_280)
        | (_cmp_cached_281)
        | (_cmp_cached_282)
        | (_cmp_cached_72)
      )
      # 1h & 4h down move, 1h & 4h high, 4h overbought
      & (
        (_cmp_cached_133)
        | (_cmp_cached_136)
        | (_cmp_cached_28)
        | (_cmp_cached_55)
        | (_cmp_cached_34)
        | (_cmp_cached_40)
        | (_cmp_cached_57)
      )
      # 1h & 4h & 1d down move, 15m & 1h & 4h still not low enough, 4h still high
      & (
        (_cmp_cached_96)
        | (_cmp_cached_41)
        | (_cmp_cached_131)
        | (_cmp_cached_102)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_161)
      )
      # 1h & 4h down move, 1h & 4h still high, 1h still not low enough, 4h still high, 1h downtrend, 4h & 1d overbought
      & (
        (_cmp_cached_96)
        | (_cmp_cached_52)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_166)
        | (_cmp_cached_124)
        | (_cmp_cached_119)
        | (_cmp_cached_180)
        | (_cmp_cached_121)
      )
      # 1h & 4h down move, 1h & 4h still high, 4h high, 1h & 4h overbought
      & (
        (_cmp_cached_96)
        | (_cmp_cached_136)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_72)
        | (_cmp_cached_189)
        | (_cmp_cached_144)
        | (_cmp_cached_132)
      )
      # 1h down move, 1h still high, 4h overbought
      & ((_cmp_cached_54) | (_cmp_cached_17) | (_cmp_cached_283))
      # 1h & 1d down move, 1h & 4h & 1d still high, 1h & 4h high, 4h overbought
      & (
        (_cmp_cached_66)
        | (_cmp_cached_59)
        | (_cmp_cached_28)
        | (_cmp_cached_68)
        | (_cmp_cached_235)
        | (_cmp_cached_134)
        | (_cmp_cached_143)
        | (_cmp_cached_132)
      )
      # 4h down move, 15m & 1h & 4h still not low enough
      & ((_cmp_cached_214) | (_cmp_cached_102) | (_cmp_cached_92) | (_cmp_cached_6))
      # 4h down move, 1h & 4h downtrend, 1h still not low enough
      & ((_cmp_cached_214) | (_cmp_cached_85) | (_cmp_cached_95) | (_cmp_cached_101))
      # 4h down move, 1h & 4h downtrend, 1h & 4h & 1d downtrend
      & (
        (_cmp_cached_214)
        | (_cmp_cached_85)
        | (_cmp_cached_273)
        | (_cmp_cached_284)
        | (_cmp_cached_148)
        | (_cmp_cached_191)
        | (_cmp_cached_210)
      )
      # 4h down move, 15m downtrend, 15m still not low enough, 1h high
      & (
        (_cmp_cached_214)
        | (_cmp_cached_76)
        | (_cmp_cached_13)
        | (_cmp_cached_32)
      )
      # 4h down move, 1h & 4h downtrend, 15m high
      & (
        (_cmp_cached_214)
        | (_cmp_cached_94)
        | (_cmp_cached_99)
        | (_cmp_cached_20)
      )
      # 4h down move, 15m & 1h high
      & ((_cmp_cached_214) | (_cmp_cached_38) | (_cmp_cached_103))
      # 4h down move, 15m high, 4h still high
      & (
        (_cmp_cached_214)
        | (_cmp_cached_38)
        | (_cmp_cached_88)
        | (_cmp_cached_39)
      )
      # 4h down move, 15m & 1h high, 4h downtrend
      & (
        (_cmp_cached_214)
        | (_cmp_cached_39)
        | (_cmp_cached_44)
        | (_cmp_cached_109)
      )
      # 4h & 1d down move, 15m still not low enough, 4h downtrend
      & (
        (_cmp_cached_215)
        | (_cmp_cached_131)
        | (_cmp_cached_13)
        | (_cmp_cached_135)
      )
      # 4h down move, 15m & 1h & 4h still not low enough, 1h & 4h downtrend, 4h & 15m still not low enough
      & (
        (_cmp_cached_215)
        | (_cmp_cached_102)
        | (_cmp_cached_92)
        | (_cmp_cached_93)
        | (_cmp_cached_85)
        | (_cmp_cached_122)
        | (_cmp_cached_149)
        | (_cmp_cached_13)
      )
      # 4h down move, 1h & 4h downtrend, 1h still not low enough, 4h high
      & (
        (_cmp_cached_215)
        | (_cmp_cached_174)
        | (_cmp_cached_122)
        | (_cmp_cached_82)
        | (_cmp_cached_161)
      )
      # 4h down mnove, 15m & 1h & 4h downtrend, 15m high, 4h downtrend
      & (
        (_cmp_cached_10)
        | (_cmp_cached_25)
        | (_cmp_cached_174)
        | (_cmp_cached_110)
        | (_cmp_cached_38)
        | (_cmp_cached_20)
        | (_cmp_cached_167)
      )
      # 4h down move, 15m & 1h & 4h still high, 15m high
      & (
        (_cmp_cached_10)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_38)
        | (_cmp_cached_20)
      )
      # 4h & 1d down move, 15m & 1h still not low enough, 4h still high, 4h downtrend, 1d overbought
      & (
        (_cmp_cached_79)
        | (_cmp_cached_245)
        | (_cmp_cached_102)
        | (_cmp_cached_92)
        | (_cmp_cached_18)
        | (_cmp_cached_135)
        | (_cmp_cached_151)
      )
      # 4h & 1d down move, 1h still high, 4h high, 1d downtrend
      & (
        (_cmp_cached_63)
        | (_cmp_cached_117)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_72)
        | (_cmp_cached_130)
        | (_cmp_cached_194)
      )
      # 4h down move, 1h & 4h still not low enough, 15m high, 4h downtrend
      & (
        (_cmp_cached_63)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_42)
        | (_cmp_cached_39)
        | (_cmp_cached_223)
      )
      # 4h & 1d down move, 15m & 1h & 4h still not low enough, 4h downtrend, 1h still high, 4h downtrend
      & (
        (_cmp_cached_41)
        | (_cmp_cached_120)
        | (_cmp_cached_102)
        | (_cmp_cached_92)
        | (_cmp_cached_93)
        | (_cmp_cached_95)
        | (_cmp_cached_44)
        | (_cmp_cached_285)
      )
      # 4h down move, 15m & 1h & 4h still high, 15m high, 4h still not low enough, 1d overbought
      & (
        (_cmp_cached_83)
        | (_cmp_cached_244)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_38)
        | (_cmp_cached_149)
        | (_cmp_cached_39)
        | (_cmp_cached_77)
        | (_cmp_cached_159)
      )
      # 4h down move, 15m high, 15m & 1h & 4h high, 4h & 1d overbought
      & (
        (_cmp_cached_24)
        | (_cmp_cached_188)
        | (_cmp_cached_39)
        | (_cmp_cached_44)
        | (_cmp_cached_40)
        | (_cmp_cached_180)
        | (_cmp_cached_156)
      )
      # 1d down move, 15m & 1h still not low enough, 4h & 1d downtrend
      & (
        (_cmp_cached_286)
        | (_cmp_cached_102)
        | (_cmp_cached_92)
        | (_cmp_cached_43)
        | (_cmp_cached_86)
        | (_cmp_cached_167)
        | (_cmp_cached_176)
      )
      # 1d down move, 1h & 4h still not low enough, 1h still high & overbought, 1d downtrend
      & (
        (_cmp_cached_286)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_72)
        | (_cmp_cached_44)
        | (_cmp_cached_144)
        | (_cmp_cached_239)
      )
      # 1d down move, 15m & 1h & 4h still not low enough, 15m still not low enough, 1h high
      & (
        (_cmp_cached_131)
        | (_cmp_cached_12)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_140)
        | (_cmp_cached_31)
        | (_cmp_cached_187)
      )
      # 1d down move, 15m still not low enough, 1h high, 1d downtrend
      & (
        (_cmp_cached_131)
        | (_cmp_cached_12)
        | (_cmp_cached_187)
        | (_cmp_cached_287)
      )
      # 1d down move, 15m high, 1h & 4h downtrend
      & (
        (_cmp_cached_131)
        | (_cmp_cached_20)
        | (_cmp_cached_288)
        | (_cmp_cached_285)
      )
      # 1d down move, 1h still high, 4h high
      & ((_cmp_cached_131) | (_cmp_cached_111) | (_cmp_cached_50))
      # 1d down move, 4h high, 1h & 4h downtrend
      & (
        (_cmp_cached_131)
        | (_cmp_cached_35)
        | (_cmp_cached_119)
        | (_cmp_cached_162)
      )
      # 1d down move, 1h high & overbought, 4h & 1d downtrend
      & (
        (_cmp_cached_275)
        | (_cmp_cached_187)
        | (_cmp_cached_144)
        | (_cmp_cached_135)
        | (_cmp_cached_194)
      )
      # 1d down move, 1h & 4h still high, 1h & 4h downtrend, 1h & 4h high, 1d downtrend
      & (
        (_cmp_cached_275)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_115)
        | (_cmp_cached_110)
        | (_cmp_cached_72)
        | (_cmp_cached_189)
        | (_cmp_cached_194)
      )
      # 15m & 1h & 4h still high, 4h downtrend, 4h overbought
      & (
        (_cmp_cached_244)
        | (_cmp_cached_28)
        | (_cmp_cached_68)
        | (_cmp_cached_289)
        | (_cmp_cached_290)
      )
      # 4h red, 15m & 1h & 4h down move, 1h & 4h still high, 4h high
      & (
        (_cmp_cached_291)
        | (_cmp_cached_22)
        | (_cmp_cached_2)
        | (_cmp_cached_41)
        | (_cmp_cached_5)
        | (_cmp_cached_18)
        | (_cmp_cached_50)
      )
      # 4h P&D, 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high, 1h & 4h high
      & (
        (_cmp_cached_292)
        | (df["change_pct_4h"].shift(48) < 5.0)
        | (_cmp_cached_264)
        | (_cmp_cached_23)
        | (_cmp_cached_52)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_128)
        | (_cmp_cached_130)
      )
      # 4h green with top wick, 15m & 1h down move, 15m still not low enough, 1h & 4h high
      & (
        (_cmp_cached_293)
        | (_cmp_cached_294)
        | (_cmp_cached_105)
        | (_cmp_cached_23)
        | (_cmp_cached_12)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_157)
        | (_cmp_cached_143)
      )
      # 4h green with top wick, 1h down move, 1h still high, 4h high, 1d overbought
      & (
        (_cmp_cached_293)
        | (_cmp_cached_294)
        | (_cmp_cached_33)
        | (_cmp_cached_17)
        | (_cmp_cached_68)
        | (_cmp_cached_134)
        | (_cmp_cached_143)
        | (_cmp_cached_146)
      )
      # 4h green with top wick, 15m & 1h down move, 1h still high, 4h high
      & (
        (_cmp_cached_295)
        | (_cmp_cached_296)
        | (_cmp_cached_22)
        | (_cmp_cached_64)
        | (_cmp_cached_72)
        | (_cmp_cached_130)
      )
      # 4h green with top wick, 15m & 1h down move, 1h & 4h high
      & (
        (_cmp_cached_295)
        | (_cmp_cached_294)
        | (_cmp_cached_47)
        | (_cmp_cached_23)
        | (_cmp_cached_128)
        | (_cmp_cached_130)
      )
      # 4h green, 15m & 1h down move, 15m still not low enough, 1h & 4h high
      & (
        (_cmp_cached_295)
        | (_cmp_cached_1)
        | (_cmp_cached_23)
        | (_cmp_cached_12)
        | (_cmp_cached_28)
        | (_cmp_cached_55)
        | (_cmp_cached_134)
        | (_cmp_cached_130)
      )
      # 1d red, 1h & 4h down move, 1h still high, 4d downtrend
      & (
        (_cmp_cached_297)
        | (_cmp_cached_54)
        | (_cmp_cached_10)
        | (_cmp_cached_44)
        | (_cmp_cached_193)
      )
      # 1d P&D, 15m & 4h down move, 15m & 4h still high
      & (
        (_cmp_cached_298)
        | (df["change_pct_1d"].shift(288) < 20.0)
        | (_cmp_cached_47)
        | (_cmp_cached_63)
        | (_cmp_cached_150)
        | (_cmp_cached_61)
      )
      # 1d red, 15m & 1h & 4h down move, 1h still not low enough, 4h & 1d still high
      & (
        (_cmp_cached_298)
        | (_cmp_cached_1)
        | (_cmp_cached_133)
        | (_cmp_cached_52)
        | (_cmp_cached_171)
        | (_cmp_cached_18)
        | (_cmp_cached_161)
        | (_cmp_cached_14)
      )
      # 1d red, 1h & 4h & 1d down move, 1h still not low enough, 4h & 1d still high, 1d downtrend
      & (
        (_cmp_cached_298)
        | (_cmp_cached_2)
        | (_cmp_cached_52)
        | (_cmp_cached_97)
        | (_cmp_cached_5)
        | (_cmp_cached_18)
        | (_cmp_cached_206)
        | (_cmp_cached_161)
        | (_cmp_cached_207)
      )
      # 1d red, 15m & 1h & 4h down move, 1d high, 15m & 1h still high
      & (
        (_cmp_cached_298)
        | (_cmp_cached_36)
        | (_cmp_cached_54)
        | (_cmp_cached_24)
        | (_cmp_cached_299)
        | (_cmp_cached_150)
        | (_cmp_cached_44)
      )
      # 1d P&D, 15m & 1h & 4h down move, 15m & 1h & 4h still high, 15m & 4h still high
      & (
        (_cmp_cached_300)
        | (df["change_pct_1d"].shift(288) < 15.0)
        | (_cmp_cached_301)
        | (_cmp_cached_51)
        | (_cmp_cached_52)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_42)
        | (_cmp_cached_124)
      )
      # 1d P&D, 15m & 1h & 4h & 1d down move, 4h still not low enough
      & (
        (_cmp_cached_302)
        | (df["change_pct_1d"].shift(288) < 10.0)
        | (_cmp_cached_22)
        | (_cmp_cached_133)
        | (_cmp_cached_10)
        | (_cmp_cached_120)
        | (_cmp_cached_6)
      )
      # 1d P&D, 15m & 1h down move, 1h still not low enough, 4h still high, 15m downtrend, 1h still high
      & (
        (_cmp_cached_302)
        | (df["change_pct_1d"].shift(288) < 10.0)
        | (_cmp_cached_1)
        | (_cmp_cached_2)
        | (_cmp_cached_5)
        | (_cmp_cached_18)
        | (_cmp_cached_80)
        | (_cmp_cached_72)
      )
      # 1d P&D, 15m down move, 1h high
      & (
        (_cmp_cached_302)
        | (df["change_pct_1d"].shift(288) < 20.0)
        | (df["top_wick_pct_1d"].shift(288) < 20.0)
        | (_cmp_cached_259)
        | (_cmp_cached_134)
      )
      # 1d P&D, 15m & 1h & 4h down move, 15m & 1h still not low enough, 4h still high, 1d overbought
      & (
        (_cmp_cached_302)
        | (df["change_pct_1d"].shift(288) < 20.0)
        | (_cmp_cached_47)
        | (_cmp_cached_2)
        | (_cmp_cached_52)
        | (_cmp_cached_102)
        | (_cmp_cached_5)
        | (_cmp_cached_29)
        | (_cmp_cached_163)
      )
      # 1d P&D, 15m & 1h & 4h down move, 15m & 1h still not low enough, 4h still high, 1h & 4h downtrend, 1d overbought
      & (
        (_cmp_cached_302)
        | (df["change_pct_1d"].shift(288) < 50.0)
        | (_cmp_cached_47)
        | (_cmp_cached_23)
        | (_cmp_cached_37)
        | (_cmp_cached_12)
        | (_cmp_cached_5)
        | (_cmp_cached_18)
        | (_cmp_cached_119)
        | (_cmp_cached_162)
        | (_cmp_cached_121)
      )
      # 1d red with top wick, 15m & 1h down move, 1h downtrend, 1h high
      & (
        (_cmp_cached_302)
        | (_cmp_cached_303)
        | (_cmp_cached_22)
        | (_cmp_cached_133)
        | (_cmp_cached_304)
        | (_cmp_cached_134)
        | (_cmp_cached_160)
      )
      # 1d P&D, 15m & 1h down move, 15m still not low enough, 1h & 4h still high, 1d overbought
      & (
        (_cmp_cached_305)
        | (df["change_pct_1d"].shift(288) < 10.0)
        | (_cmp_cached_47)
        | (_cmp_cached_33)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_121)
      )
      # 1d P&D, 15m & 1h & 4h down move, 1h & 4h still not low enough, 1h & 4h downtrend, 1d overbought
      & (
        (_cmp_cached_305)
        | (df["change_pct_1d"].shift(288) < 10.0)
        | (_cmp_cached_53)
        | (_cmp_cached_96)
        | (_cmp_cached_41)
        | (_cmp_cached_101)
        | (_cmp_cached_149)
        | (_cmp_cached_266)
        | (_cmp_cached_191)
        | (_cmp_cached_159)
      )
      # 1d red, 15m & 1h & 4h down move, 1h & 4h still not low enough, 1d high, 4h downtrend, 1d overbought
      & (
        (_cmp_cached_305)
        | (_cmp_cached_47)
        | (_cmp_cached_23)
        | (_cmp_cached_37)
        | (_cmp_cached_5)
        | (_cmp_cached_18)
        | (_cmp_cached_299)
        | (_cmp_cached_167)
        | (_cmp_cached_146)
      )
      # 1d green with top wick, 15m & 1h & 1d down move, 1h still not low enough, 4h still high, 1d overbought
      & (
        (_cmp_cached_306)
        | (_cmp_cached_303)
        | (_cmp_cached_1)
        | (_cmp_cached_96)
        | (_cmp_cached_245)
        | (_cmp_cached_5)
        | (_cmp_cached_29)
        | (_cmp_cached_61)
        | (_cmp_cached_146)
      )
      # 1d green with top wick, 15m & 1h & 4h down move, 1h & 4h still high
      & (
        (_cmp_cached_306)
        | (_cmp_cached_303)
        | (_cmp_cached_22)
        | (_cmp_cached_133)
        | (_cmp_cached_145)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_101)
        | (_cmp_cached_26)
      )
      # 1d green with top wick, 15m down move, 1h & 4h high, 1d overbought
      & (
        (_cmp_cached_306)
        | (_cmp_cached_303)
        | (_cmp_cached_22)
        | (_cmp_cached_181)
        | (_cmp_cached_141)
        | (_cmp_cached_127)
        | (_cmp_cached_234)
      )
      # 1d green with top wick, 15m down move, 15m & 1h still high, 4h & 1d high, 4h overbought
      & (
        (_cmp_cached_306)
        | (_cmp_cached_303)
        | (_cmp_cached_22)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_242)
        | (_cmp_cached_34)
        | (_cmp_cached_178)
        | (_cmp_cached_132)
      )
      # 1d green with top wick, 15m & 1h & 4h down move, 15m still not low enough, 1h still high, 4h high
      & (
        (_cmp_cached_306)
        | (_cmp_cached_303)
        | (_cmp_cached_1)
        | (_cmp_cached_133)
        | (_cmp_cached_145)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_68)
        | (_cmp_cached_140)
        | (_cmp_cached_26)
      )
      # 1d green with top wick, 15m down move, 15m & 1h still high, 4h high & overbought
      & (
        (_cmp_cached_306)
        | (_cmp_cached_303)
        | (_cmp_cached_1)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_141)
        | (_cmp_cached_50)
        | (_cmp_cached_57)
      )
      # 1d green with top wick, 1h & 4h down move, 1h & 4h still high
      & (
        (_cmp_cached_306)
        | (_cmp_cached_303)
        | (_cmp_cached_54)
        | (_cmp_cached_24)
        | (_cmp_cached_72)
        | (_cmp_cached_124)
      )
      # 1d green with top wick, 15m & 1h down move, 15m & 1h & 4h still high, 4h high & overbought
      & (
        (_cmp_cached_307)
        | (_cmp_cached_308)
        | (_cmp_cached_1)
        | (_cmp_cached_33)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_29)
        | (_cmp_cached_50)
        | (_cmp_cached_180)
      )
      # 1d green with top wick, 1h & 4h down move, 1h still not low enough, 4h still high, 4h & 1d overbought
      & (
        (_cmp_cached_307)
        | (_cmp_cached_308)
        | (_cmp_cached_33)
        | (_cmp_cached_52)
        | (_cmp_cached_5)
        | (_cmp_cached_29)
        | (_cmp_cached_124)
        | (_cmp_cached_126)
        | (_cmp_cached_159)
      )
      # 1d green with top wick, 15m down move, 15m & 1h & 4h still high, 4h & 1d overbought
      & (
        (_cmp_cached_309)
        | (_cmp_cached_310)
        | (_cmp_cached_264)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_68)
        | (_cmp_cached_43)
        | (_cmp_cached_44)
        | (_cmp_cached_61)
        | (_cmp_cached_180)
        | (_cmp_cached_159)
      )
      # 1d green with top wick, 15m & 1h & 4h down move, 15m still not low enough, 4h high, 1d overbought
      & (
        (_cmp_cached_311)
        | (_cmp_cached_303)
        | (_cmp_cached_36)
        | (_cmp_cached_96)
        | (_cmp_cached_312)
        | (_cmp_cached_68)
        | (_cmp_cached_91)
        | (_cmp_cached_50)
        | (_cmp_cached_234)
      )
      # 1d green with top wick, 15m & 1h & 4h down move, 1h still not low enough, 4h still high, 1d overbought
      & (
        (_cmp_cached_311)
        | (_cmp_cached_308)
        | (_cmp_cached_22)
        | (_cmp_cached_23)
        | (_cmp_cached_37)
        | (_cmp_cached_56)
        | (_cmp_cached_124)
        | (_cmp_cached_121)
      )
      # 1d green with top wick, 15m down move, 15m & 1h still high, 4h high & overbought
      & (
        (_cmp_cached_311)
        | (_cmp_cached_308)
        | (_cmp_cached_259)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_141)
        | (_cmp_cached_34)
        | (_cmp_cached_183)
      )
      # 1d green with top wick, 1h down move, 1h still high, 4h high & overbought, 1d overbought
      & (
        (_cmp_cached_311)
        | (_cmp_cached_308)
        | (_cmp_cached_51)
        | (_cmp_cached_17)
        | (_cmp_cached_68)
        | (_cmp_cached_50)
        | (_cmp_cached_152)
        | (_cmp_cached_159)
      )
      # 1d green with top wick, 15m & 1h down move, 1h & 4h still high, 4h overbought
      & (
        (_cmp_cached_311)
        | (_cmp_cached_313)
        | (_cmp_cached_53)
        | (_cmp_cached_133)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_34)
        | (_cmp_cached_69)
      )
      # 1d green with top wick, 15m & 4h down move, 15m & 1h still high, 1d overbought
      & (
        (_cmp_cached_311)
        | (_cmp_cached_313)
        | (_cmp_cached_301)
        | (_cmp_cached_136)
        | (_cmp_cached_42)
        | (_cmp_cached_44)
        | (_cmp_cached_121)
      )
      # 1d green, 15m & 4h down move, 4h still high, 4h & 1d overbought
      & (
        (_cmp_cached_314)
        | (_cmp_cached_1)
        | (_cmp_cached_63)
        | (_cmp_cached_29)
        | (_cmp_cached_152)
        | (_cmp_cached_121)
      )
      # 1d green with top wick, 15m & 1h & 4h down move, 1h & 4h still high, 4h high
      & (
        (_cmp_cached_314)
        | (_cmp_cached_315)
        | (_cmp_cached_22)
        | (_cmp_cached_2)
        | (_cmp_cached_41)
        | (_cmp_cached_5)
        | (_cmp_cached_18)
        | (_cmp_cached_50)
      )
      # 1d green with top wick, 1d down move, 4h still high & overbought
      & (
        (_cmp_cached_314)
        | (_cmp_cached_315)
        | (_cmp_cached_33)
        | (_cmp_cached_29)
        | (_cmp_cached_124)
        | (_cmp_cached_183)
      )
      # 1d green with top wick, 4h down move, 4h still high, 1d overbought
      & (
        (_cmp_cached_314)
        | (_cmp_cached_315)
        | (_cmp_cached_37)
        | (_cmp_cached_18)
        | (_cmp_cached_151)
      )
      # 1d green, 15m & 4h down move, 15m & 1h & 4h still high, 15m high, 4h & 1d overbought
      & (
        (_cmp_cached_314)
        | (_cmp_cached_301)
        | (_cmp_cached_52)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_38)
        | (_cmp_cached_69)
        | (_cmp_cached_151)
      )
      # 4h top wick, 15m down move, 15m still not low enough, 1h & 4h still high, 4h overbought
      & (
        (_cmp_cached_316)
        | (_cmp_cached_53)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_44)
        | (_cmp_cached_61)
        | (_cmp_cached_183)
      )
      # 4h top wick, 15m & 1h down move, 15m & 1h still high, 1h & 4h high
      & (
        (_cmp_cached_316)
        | (_cmp_cached_264)
        | (_cmp_cached_54)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_68)
        | (_cmp_cached_30)
        | (_cmp_cached_31)
        | (_cmp_cached_130)
      )
      # 1d top wick, 1h & 4h down move, 15m downtrend, 4h still high, 1d overbought
      & (
        (_cmp_cached_308)
        | (_cmp_cached_78)
        | (_cmp_cached_48)
        | (_cmp_cached_317)
        | (_cmp_cached_124)
        | (_cmp_cached_27)
      )
      # 1d top wick, 4h down move, 4h still high, 1d overbought
      & (
        (_cmp_cached_310)
        | (_cmp_cached_63)
        | (_cmp_cached_196)
        | (_cmp_cached_88)
        | (_cmp_cached_151)
      )
      # 1d top wick, 15m & 1h & 4h down move, 15m & 1h downtrend, 4h still high
      & (
        (_cmp_cached_310)
        | (_cmp_cached_22)
        | (_cmp_cached_96)
        | (_cmp_cached_52)
        | (_cmp_cached_25)
        | (_cmp_cached_94)
        | (_cmp_cached_124)
      )
      # 1d top wick, 15m & 1h & 4h down move, 15m still not low enough, 1h & 4h still high
      & (
        (_cmp_cached_310)
        | (_cmp_cached_36)
        | (_cmp_cached_66)
        | (_cmp_cached_136)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_140)
        | (_cmp_cached_124)
        | (_cmp_cached_13)
        | (_cmp_cached_82)
      )
      # 1d top wick, 15m down move, 15m stil high, 1h & 4h high, 4h overbought
      & (
        (_cmp_cached_310)
        | (_cmp_cached_259)
        | (_cmp_cached_16)
        | (_cmp_cached_28)
        | (_cmp_cached_141)
        | (_cmp_cached_128)
        | (_cmp_cached_34)
        | (_cmp_cached_183)
      )
      # 1d top wick, 15m & 1h & 4h down move, 15m & 1h & 4h still high
      & (
        (_cmp_cached_318)
        | (_cmp_cached_264)
        | (_cmp_cached_58)
        | (_cmp_cached_145)
        | (_cmp_cached_16)
        | (_cmp_cached_17)
        | (_cmp_cached_18)
        | (_cmp_cached_124)
      )
      # pump, drop but not yet near the previous lows, 15m & 1h & 4h & 1d down move, 1d overbought
      & (
        (((df["high_max_6_1d"] - df["low_min_6_1d"]) / df["low_min_6_1d"]) < 1.5)
        | (df["close"] > (df["high_max_6_4h"] * 0.70))
        | (df["close"] < (df["low_min_6_1d"] * 1.25))
        | (_cmp_cached_1)
        | (_cmp_cached_133)
        | (_cmp_cached_63)
        | (_cmp_cached_158)
        | (_cmp_cached_146)
      )
      # pump, drop in lays days, 1h & 4h down move, 1h & 4h still not low enough, 1d overbought
      & (
        (((df["high_max_12_1d"] - df["low_min_12_1d"]) / df["low_min_12_1d"]) < 3.0)
        | (df["close"] > (df["high_max_24_4h"] * 0.70))
        | (_cmp_cached_89)
        | (_cmp_cached_97)
        | (_cmp_cached_5)
        | (_cmp_cached_18)
        | (_cmp_cached_146)
      )
      # pump, 15m & 1h & 4h down move, 15m & 1h still not low enough, 4h still high, 1h downtrend, 1h high
      & (
        (((df["high_max_12_1d"] - df["low_min_12_1d"]) / df["low_min_12_1d"]) < 3.0)
        | (_cmp_cached_47)
        | (_cmp_cached_96)
        | (_cmp_cached_37)
        | (_cmp_cached_102)
        | (_cmp_cached_5)
        | (_cmp_cached_18)
        | (_cmp_cached_174)
        | (_cmp_cached_134)
      )
      # pump, drop in last 6 days, 1h & 4h down move, 1h & 4h still not low enough, 4h downtrend, 4h & 1d downtrend
      & (
        (((df["high_max_30_1d"] - df["low_min_30_1d"]) / df["low_min_30_1d"]) < 10.0)
        | (df["close"] > (df["high_max_6_1d"] * 0.50))
        | (_cmp_cached_23)
        | (_cmp_cached_136)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_110)
        | (_cmp_cached_203)
        | (_cmp_cached_210)
      )
      # drop in the last 4 hours, 1h & 4h high
      & ((df["close"] > (df["close_max_48"] * 0.30)) | (_cmp_cached_31) | (_cmp_cached_189))
      # drop in last 12 hours, 14m & 1h & 4h down move, 15m still not low enough, 1h still high, 4h high & overbought
      & (
        (df["close"] > (df["high_max_12_1h"] * 0.50))
        | (_cmp_cached_47)
        | (_cmp_cached_64)
        | (_cmp_cached_24)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_29)
        | (_cmp_cached_34)
        | (_cmp_cached_132)
      )
      # drop in last 12 hours, 1h & 4h down move, 1h & 4h downtrend
      & (
        (df["close"] > (df["high_max_12_1h"] * 0.35))
        | (_cmp_cached_89)
        | (_cmp_cached_215)
        | (_cmp_cached_319)
        | (_cmp_cached_223)
      )
      # drop in last 4 days, 15m & 1h & 4h down move, 15m still not low enough, 1h still high, 4h overbought
      & (
        (df["close"] > (df["high_max_24_4h"] * 0.40))
        | (_cmp_cached_22)
        | (_cmp_cached_133)
        | (_cmp_cached_52)
        | (_cmp_cached_12)
        | (_cmp_cached_17)
        | (_cmp_cached_180)
      )
      # drop in last 4 days, 15m & 1h & 4h & 1d down move, 4h high
      & (
        (df["close"] > (df["high_max_24_4h"] * 0.40))
        | (_cmp_cached_22)
        | (_cmp_cached_23)
        | (_cmp_cached_136)
        | (_cmp_cached_275)
        | (_cmp_cached_40)
      )
      # drop in last 6 days, 15m & 1h & 4h & 1d down move, 1d high, 4h downtrend
      & (
        (df["close"] > (df["high_max_24_4h"] * 0.35))
        | (_cmp_cached_105)
        | (_cmp_cached_133)
        | (_cmp_cached_63)
        | (_cmp_cached_117)
        | (_cmp_cached_320)
        | (_cmp_cached_135)
      )
      # drop in last 4 days, 15m & 1d down move, 15m still not low enough, 1h still high, 1d high, 4h downtrend
      & (
        (df["close"] > (df["high_max_24_4h"] * 0.35))
        | (_cmp_cached_1)
        | (_cmp_cached_117)
        | (_cmp_cached_91)
        | (_cmp_cached_111)
        | (_cmp_cached_320)
        | (_cmp_cached_223)
      )
      # drop in last 4 days, 1h & 5h & 1d down move, 1h still high, 1h & 4h downtrend
      & (
        (df["close"] > (df["high_max_24_4h"] * 0.25))
        | (_cmp_cached_2)
        | (_cmp_cached_63)
        | (_cmp_cached_59)
        | (_cmp_cached_72)
        | (_cmp_cached_148)
        | (_cmp_cached_193)
      )
      # drop in last 4 days, 1d down move, 1h & 4h downtrend, 15m & 4h downtrend
      & (
        (df["close"] > (df["high_max_24_4h"] * 0.25))
        | (_cmp_cached_45)
        | (_cmp_cached_85)
        | (_cmp_cached_122)
        | (_cmp_cached_112)
        | (_cmp_cached_109)
      )
      # drop in last 6 days, 15m & 1d down move, 1h still high, 4h high, 4h downtrend
      & (
        (df["close"] > (df["high_max_6_1d"] * 0.25))
        | (_cmp_cached_1)
        | (_cmp_cached_45)
        | (_cmp_cached_160)
        | (_cmp_cached_173)
        | (_cmp_cached_191)
      )
      # drop in last 6 days, 15m & 1h down move, 15m & 1h still not low enough, 15m & 1h & 4h & 1d downtrend
      & (
        (df["close"] > (df["high_max_6_1d"] * 0.25))
        | (_cmp_cached_53)
        | (_cmp_cached_96)
        | (_cmp_cached_12)
        | (_cmp_cached_123)
        | (_cmp_cached_174)
        | (_cmp_cached_236)
        | (_cmp_cached_321)
        | (_cmp_cached_101)
      )
      # drop in last 4 days, 4h & 1d down move, 1h high
      & (
        (df["close"] > (df["high_max_24_4h"] * 0.15))
        | (_cmp_cached_63)
        | (_cmp_cached_59)
        | (_cmp_cached_32)
      )
      # drop in last 4 days, 1d down move, 1d downtrendm 1h still high, 1d downtrend
      & (
        (df["close"] > (df["high_max_24_4h"] * 0.15))
        | (_cmp_cached_4)
        | (_cmp_cached_271)
        | (_cmp_cached_72)
        | (_cmp_cached_287)
      )
      # drop in last 6 days, 1d down move, 1h & 4h & 1d downtrend, 1d still high, 4h downtrend
      & (
        (df["close"] > (df["high_max_6_1d"] * 0.15))
        | (_cmp_cached_4)
        | (_cmp_cached_174)
        | (_cmp_cached_236)
        | (_cmp_cached_321)
        | (_cmp_cached_322)
        | (_cmp_cached_167)
      )
      # drop in last 12 days. 15m & 1h & 4h & 1d down move, 4h still high, 1d downtrend
      & (
        (df["close"] > (df["high_max_12_1d"] * 0.25))
        | (_cmp_cached_22)
        | (_cmp_cached_78)
        | (_cmp_cached_83)
        | (_cmp_cached_11)
        | (_cmp_cached_61)
        | (_cmp_cached_194)
      )
      # drop in last 12 days, 15m & 1h down move, 1h still not low enough, 4h high
      & (
        (df["close"] > (df["high_max_12_1d"] * 0.25))
        | (_cmp_cached_1)
        | (_cmp_cached_96)
        | (_cmp_cached_5)
        | (_cmp_cached_6)
        | (_cmp_cached_160)
        | (_cmp_cached_35)
      )
      # drop in last 20 days, 15m & 1h & 1d down move, 15m still not low enough, 1h high
      & (
        (df["close"] > (df["high_max_20_1d"] * 0.05))
        | (_cmp_cached_22)
        | (_cmp_cached_133)
        | (_cmp_cached_59)
        | (_cmp_cached_140)
        | (_cmp_cached_128)
      )
      # drop in last 20 days, 1h & 4h & 1d down move, 1h & 4h still not low enough, 1h & 4h & 1d downtrend
      & (
        (df["close"] > (df["high_max_20_1d"] * 0.01))
        | (_cmp_cached_33)
        | (_cmp_cached_136)
        | (_cmp_cached_45)
        | (_cmp_cached_323)
        | (_cmp_cached_93)
        | (_cmp_cached_184)
        | (_cmp_cached_110)
        | (_cmp_cached_265)
        | (_cmp_cached_324)
        | (_cmp_cached_9)
        | (_cmp_cached_325)
        | (_cmp_cached_326)
      )
      # drop in last 30 days, 15m & 1h down move, 1h still high, 4h high & overbought
      & (
        (df["close"] > (df["high_max_30_1d"] * 0.10))
        | (_cmp_cached_22)
        | (_cmp_cached_54)
        | (_cmp_cached_111)
        | (_cmp_cached_189)
        | (_cmp_cached_57)
      )
      # drop in last 30 days, 15m down move, 15m & 1h high
      & (
        (df["close"] > (df["high_max_30_1d"] * 0.05))
        | (_cmp_cached_1)
        | (_cmp_cached_52)
        | (_cmp_cached_188)
        | (_cmp_cached_327)
      )
      # drop in last 30 days, 15m & 1h & 4h down move, 15m still not low enough, 1h high
      & (
        (df["close"] > (df["high_max_30_1d"] * 0.05))
        | (_cmp_cached_53)
        | (_cmp_cached_133)
        | (_cmp_cached_37)
        | (_cmp_cached_13)
        | (_cmp_cached_160)
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

      tok_after_protections = time.perf_counter()
      tok_total = time.perf_counter()
      log.debug(
        f"[{metadata['pair']}] "
        f"populate_indicators pre-protections: "
        f"{tok_before_protections - tik:0.4f}s | "
        f"protections: "
        f"{tok_after_protections - tok_before_protections:0.4f}s | "
        f"total: "
        f"{tok_total - tik:0.4f}s"
      )
      tok = time.perf_counter()
      log.debug("[%s] Populate indicators took a total of: %.4f seconds.", metadata["pair"], tok - tik)

      return df

    _cmp_cached_328 = _cmp("RSI_3", "<", 90.0)
    _cmp_cached_329 = _cmp("RSI_3_15m", "<", 75.0)
    _cmp_cached_330 = _cmp("RSI_3_1h", "<", 75.0)
    _cmp_cached_331 = _cmp("RSI_3_4h", "<", 75.0)
    _cmp_cached_332 = _cmp("RSI_14_15m", ">", 90.0)
    _cmp_cached_333 = _cmp("RSI_14_1h", ">", 85.0)
    _cmp_cached_334 = _cmp("RSI_14_4h", ">", 70.0)
    _cmp_cached_335 = _cmp("STOCHRSIk_14_14_3_3_4h", ">", 60.0)
    _cmp_cached_336 = _cmp("RSI_14_15m", ">", 60.0)
    _cmp_cached_337 = _cmp("RSI_14_1h", ">", 50.0)
    _cmp_cached_338 = _cmp("RSI_14_4h", ">", 40.0)
    _cmp_cached_339 = _cmp("AROONU_14_15m", ">", 20.0)
    _cmp_cached_340 = _cmp("AROONU_14_1h", ">", 20.0)
    _cmp_cached_341 = _cmp("AROONU_14_4h", ">", 40.0)
    _cmp_cached_342 = _cmp("RSI_3_15m", "<", 90.0)
    _cmp_cached_343 = _cmp("RSI_3_1h", "<", 60.0)
    _cmp_cached_344 = _cmp("RSI_3_4h", "<", 60.0)
    _cmp_cached_345 = _cmp("RSI_14_15m", ">", 80.0)
    _cmp_cached_346 = _cmp("RSI_14_1h", ">", 70.0)
    _cmp_cached_347 = _cmp("AROONU_14_1h", ">", 60.0)
    _cmp_cached_348 = _cmp("AROONU_14_4h", ">", 60.0)
    _cmp_cached_349 = _cmp("STOCHRSIk_14_14_3_3_4h", ">", 40.0)
    _cmp_cached_350 = _cmp("RSI_3_4h", "<", 35.0)
    _cmp_cached_351 = _cmp("RSI_14_1h", ">", 60.0)
    _cmp_cached_352 = _cmp("RSI_14_4h", ">", 60.0)
    _cmp_cached_353 = _cmp("AROONU_14_1h", ">", 40.0)
    _cmp_cached_354 = _cmp("RSI_3_15m", "<", 95.0)
    _cmp_cached_355 = _cmp("RSI_3_1h", "<", 80.0)
    _cmp_cached_356 = _cmp("RSI_3_4h", "<", 80.0)
    _cmp_cached_357 = _cmp("RSI_14_1h", ">", 80.0)
    _cmp_cached_358 = _cmp("RSI_14_4h", ">", 80.0)
    _cmp_cached_359 = _cmp("CCI_20_1h", ">", 200.0)
    _cmp_cached_360 = _cmp("CCI_20_4h", ">", 150.0)
    _cmp_cached_361 = _cmp("RSI_3_1h", "<", 50.0)
    _cmp_cached_362 = _cmp("RSI_3_4h", "<", 50.0)
    _cmp_cached_363 = _cmp("CMF_20_15m", "<", 0.20)
    _cmp_cached_364 = _cmp("STOCHRSIk_14_14_3_3_1h", ">", 70.0)
    _cmp_cached_365 = _cmp("RSI_3_1h", "<", 90.0)
    _cmp_cached_366 = _cmp("CCI_20_1h", ">", 250.0)
    _cmp_cached_367 = _cmp("CCI_20_4h", ">", 200.0)
    _cmp_cached_368 = _cmp("CMF_20_15m", "<", 0.25)
    _cmp_cached_369 = _cmp("AROONU_14_4h", ">", 50.0)
    _cmp_cached_370 = _cmp("RSI_3_15m", "<", 85.0)
    _cmp_cached_371 = _cmp("RSI_3_1h", "<", 85.0)
    _cmp_cached_372 = _cmp("RSI_3_4h", "<", 85.0)
    _cmp_cached_373 = _cmp("AROONU_14_15m", ">", 70.0)
    _cmp_cached_374 = _cmp("STOCHRSIk_14_14_3_3_15m", ">", 80.0)
    _cmp_cached_375 = _cmp("STOCHRSIk_14_14_3_3_1h", ">", 80.0)
    _cmp_cached_376 = _cmp("RSI_14_15m", ">", 85.0)
    _cmp_cached_377 = _cmp("CMF_20_1h", "<", 0.10)
    _cmp_cached_378 = _cmp("CMF_20_4h", "<", 0.10)
    _cmp_cached_379 = _cmp("RSI_3_4h", "<", 70.0)
    _cmp_cached_380 = _cmp("STOCHRSIk_14_14_3_3_1h", ">", 50.0)
    _cmp_cached_381 = _cmp("AROONU_14_4h", ">", 70.0)
    _cmp_cached_382 = _cmp("STOCHRSIk_14_14_3_3_4h", ">", 80.0)
    _cmp_cached_383 = _cmp("RSI_3_1h", "<", 70.0)
    _cmp_cached_384 = _cmp("AROONU_14_1h", ">", 70.0)
    _cmp_cached_385 = _cmp("ROC_9_1h", "<", 45.0)
    _cmp_cached_386 = _cmp("ROC_9_4h", "<", 45.0)
    _cmp_cached_387 = _cmp("RSI_14_15m", ">", 70.0)
    _cmp_cached_388 = _cmp("STOCHRSIk_14_14_3_3_1h", ">", 60.0)
    _cmp_cached_389 = _cmp("RSI_3_15m", "<", 80.0)
    _cmp_cached_390 = _cmp("STOCHRSIk_14_14_3_3_4h", ">", 75.0)
    _cmp_cached_391 = _cmp("RSI_3_4h", "<", 55.0)
    _cmp_cached_392 = _cmp("STOCHRSIk_14_14_3_3_15m", ">", 90.0)
    _cmp_cached_393 = _cmp("STOCHRSIk_14_14_3_3_1h", ">", 40.0)
    _cmp_cached_394 = _cmp("STOCHRSIk_14_14_3_3_4h", ">", 30.0)
    _cmp_cached_395 = _cmp("AROONU_14_4h", ">", 30.0)
    _cmp_cached_396 = _cmp("RSI_3_15m", "<", 70.0)
    _cmp_cached_397 = _cmp("RSI_3_1h", "<", 95.0)
    _cmp_cached_398 = _cmp("STOCHRSIk_14_14_3_3_15m", ">", 30.0)
    _cmp_cached_399 = _cmp("ROC_9_1h", "<", 25.0)
    _cmp_cached_400 = _cmp("CMF_20_1h", "<", 0.20)
    _cmp_cached_401 = _cmp("CMF_20_4h", "<", 0.20)
    _cmp_cached_402 = _cmp("STOCHRSIk_14_14_3_3_15m", ">", 50.0)
    _cmp_cached_403 = _cmp("RSI_14_1d", ">", 50.0)
    _cmp_cached_404 = _cmp("STOCHRSIk_14_14_3_3_15m", ">", 70.0)
    _cmp_cached_405 = _cmp("STOCHRSIk_14_14_3_3_4h", ">", 70.0)
    _cmp_cached_406 = _cmp("RSI_3_4h", "<", 90.0)
    _cmp_cached_407 = _cmp("STOCHRSIk_14_14_3_3_1d", ">", 50.0)
    _cmp_cached_408 = _cmp("STOCHRSIk_14_14_3_3_15m", ">", 40.0)
    _cmp_cached_409 = _cmp("RSI_14_4h", ">", 90.0)
    _cmp_cached_410 = _cmp("RSI_3_15m", "<", 40.0)
    _cmp_cached_411 = _cmp("RSI_3_1h", "<", 40.0)
    _cmp_cached_412 = _cmp("RSI_3_1d", "<", 85.0)
    _cmp_cached_413 = _cmp("CCI_20_15m", ">", 350.0)
    _cmp_cached_414 = _cmp("RSI_14_1h", ">", 75.0)
    _cmp_cached_415 = _cmp("RSI_14_4h", ">", 95.0)
    _cmp_cached_416 = _cmp("AROOND_14_4h", "<", 50.0)
    _cmp_cached_417 = _cmp("CCI_20_4h", ">", 250.0)
    _cmp_cached_418 = _cmp("RSI_14_1d", ">", 60.0)
    _cmp_cached_419 = _cmp("AROOND_14_1d", "<", 75.0)
    _cmp_cached_420 = _cmp("STOCHRSIk_14_14_3_3_1d", ">", 70.0)
    _cmp_cached_421 = _cmp("RSI_3_15m", "<", 60.0)
    _cmp_cached_422 = _cmp("RSI_3_1d", "<", 90.0)
    _cmp_cached_423 = _cmp("RSI_14_1h", ">", 90.0)
    _cmp_cached_424 = _cmp("CCI_20_1h", ">", 300.0)
    _cmp_cached_425 = _cmp("RSI_14_1d", ">", 95.0)
    _cmp_cached_426 = _cmp("RSI_3_1d", "<", 80.0)
    _cmp_cached_427 = _cmp("WILLR_14_4h", ">", -10.0)
    _cmp_cached_428 = _cmp("RSI_14_1d", ">", 80.0)
    _cmp_cached_429 = _cmp("RSI_3_15m", "<", 65.0)
    _cmp_cached_430 = _cmp("RSI_3_1d", "<", 60.0)
    _cmp_cached_431 = _cmp("CMF_20_15m", ">", 0.40)
    _cmp_cached_432 = _cmp("WILLR_14_15m", ">", -10.0)
    _cmp_cached_433 = _cmp("CCI_20_15m", ">", 450.0)
    _cmp_cached_434 = _cmp("STOCHk_14_3_3_15m", ">", 90.0)
    _cmp_cached_435 = _cmp("CMF_20_1h", ">", 0.20)
    _cmp_cached_436 = _cmp("WILLR_14_1h", ">", -5.0)
    _cmp_cached_437 = _cmp("CMF_20_4h", ">", 0.10)
    _cmp_cached_438 = _cmp("RSI_14_1d", ">", 90.0)
    _cmp_cached_439 = _cmp("MFI_14_15m", ">", 90.0)
    _cmp_cached_440 = _cmp("MFI_14_1h", ">", 90.0)
    _cmp_cached_441 = _cmp("MFI_14_4h", ">", 80.0)
    _cmp_cached_442 = _cmp("WILLR_14_4h", ">", -5.0)
    _cmp_cached_443 = _cmp("MFI_14_1h", ">", 80.0)
    _cmp_cached_444 = _cmp("RSI_3_1d", "<", 95.0)
    _cmp_cached_445 = _cmp("CCI_20_15m", ">", 250.0)
    _cmp_cached_446 = _cmp("CCI_20_change_pct_1h", "<", -0.0)
    _cmp_cached_447 = _cmp("STOCHRSIk_14_14_3_3_1h", ">", 90.0)
    _cmp_cached_448 = _cmp("RSI_14_4h", ">", 85.0)
    _cmp_cached_449 = _cmp("CCI_20_change_pct_4h", "<", -0.0)
    _cmp_cached_450 = _cmp("STOCHRSIk_14_14_3_3_4h", ">", 90.0)
    _cmp_cached_451 = _cmp("WILLR_14_1d", ">", -10.0)
    _cmp_cached_452 = _cmp("CCI_20_15m", ">", 400.0)
    _cmp_cached_453 = _cmp("CCI_20_1h", ">", 400.0)
    _cmp_cached_454 = _cmp("CCI_20_4h", ">", 400.0)
    _cmp_cached_455 = _cmp("ROC_9_4h", "<", 200.0)
    _cmp_cached_456 = _cmp("AROOND_14_1h", "<", 50.0)
    _cmp_cached_457 = _cmp("CCI_20_1h", ">", 350.0)
    _cmp_cached_458 = _cmp("RSI_14_1d", ">", 85.0)
    _cmp_cached_459 = _cmp("RSI_3_1d", "<", 70.0)
    _cmp_cached_460 = _cmp("AROOND_14_4h", "<", 75.0)
    _cmp_cached_461 = _cmp("STOCHk_14_3_3_4h", ">", 70.0)
    _cmp_cached_462 = _cmp("RSI_14_1d", ">", 70.0)
    _cmp_cached_463 = _cmp("AROOND_14_1d", "<", 50.0)
    _cmp_cached_464 = _cmp("STOCHk_14_3_3_1h", ">", 90.0)
    _cmp_cached_465 = _cmp("STOCHk_14_3_3_4h", ">", 90.0)
    _cmp_cached_466 = _cmp("STOCHk_14_3_3_1d", ">", 70.0)
    _cmp_cached_467 = _cmp("AROOND_14_1h", "<", 25.0)
    _cmp_cached_468 = _cmp("RSI_14_15m", ">", 95.0)
    _cmp_cached_469 = _cmp("CMF_20_15m", ">", 0.50)
    _cmp_cached_470 = _cmp("UO_7_14_28_15m", ">", 80.0)
    _cmp_cached_471 = _cmp("UO_7_14_28_change_pct_15m", "<", -0.0)
    _cmp_cached_472 = _cmp("RSI_14_1h", ">", 95.0)
    _cmp_cached_473 = _cmp("CMF_20_1h", ">", 0.50)
    _cmp_cached_474 = _cmp("UO_7_14_28_1h", ">", 80.0)
    _cmp_cached_475 = _cmp("CMF_20_4h", ">", 0.35)
    _cmp_cached_476 = _cmp("UO_7_14_28_4h", ">", 75.0)
    _cmp_cached_477 = _cmp("CCI_20_4h", ">", 500.0)
    _cmp_cached_478 = _cmp("ROC_2_4h", "<", 10.0)
    _cmp_cached_479 = _cmp("RSI_14_4h", ">", 65.0)
    _cmp_cached_480 = _cmp("RSI_14_1d", ">", 65.0)
    _cmp_cached_481 = _cmp("STOCHRSIk_14_14_3_3_1d", ">", 80.0)
    _cmp_cached_482 = _cmp("CCI_20_4h", ">", 300.0)
    _cmp_cached_483 = _cmp("WILLR_14_1h", ">", -20.0)
    _cmp_cached_484 = _cmp("WILLR_14_4h", ">", -25.0)
    _cmp_cached_485 = _cmp("STOCHRSIk_14_14_3_3_4h", ">", 20.0)
    _cmp_cached_486 = _cmp("AROOND_14_15m", "<", 50.0)
    _cmp_cached_487 = _cmp("WILLR_14_1h", ">", -50.0)
    _cmp_cached_488 = _cmp("AROOND_14_1h", "<", 75.0)
    _cmp_cached_489 = _cmp("WILLR_14_4h", ">", -50.0)
    _cmp_cached_490 = _cmp("AROOND_14_4h", "<", 25.0)
    _cmp_cached_491 = _cmp("CCI_20_15m", ">", 600.0)
    _cmp_cached_492 = _cmp("CCI_20_1h", ">", 600.0)
    _cmp_cached_493 = _cmp("CCI_20_4h", ">", 600.0)
    _cmp_cached_494 = _cmp("RSI_14_1d", ">", 40.0)

    # Global protections Short
    df["protections_short_global"] = (
      # 5m & 15m & 1h & 4h up move, 15m & 1h & 4h still not high enough, 4h still low, 1h uptrend
      (
        (_cmp_cached_328)
        | (_cmp_cached_329)
        | (_cmp_cached_330)
        | (_cmp_cached_331)
        | (_cmp_cached_332)
        | (_cmp_cached_333)
        | (_cmp_cached_334)
        | (_cmp_cached_335)
        | (_cmp_cached_213)
      )
      # 5m & 15m up move, 15m & 1h & 4h still low, 15m & 1h low, 4h still low
      & (
        (_cmp_cached_328)
        | (_cmp_cached_329)
        | (_cmp_cached_336)
        | (_cmp_cached_337)
        | (_cmp_cached_338)
        | (_cmp_cached_339)
        | (_cmp_cached_340)
        | (_cmp_cached_341)
      )
      # 15m & 1h & 4h up move, 15m & 1h & 4h still not high enough, 1h & 4h still low, 4h low
      & (
        (_cmp_cached_342)
        | (_cmp_cached_343)
        | (_cmp_cached_344)
        | (_cmp_cached_345)
        | (_cmp_cached_346)
        | (_cmp_cached_334)
        | (_cmp_cached_347)
        | (_cmp_cached_348)
        | (_cmp_cached_349)
      )
      # 15m & 1h & 4h up move, 15m still not high enough, 1h & 4h still low, 1h low
      & (
        (_cmp_cached_342)
        | (_cmp_cached_343)
        | (_cmp_cached_350)
        | (_cmp_cached_345)
        | (_cmp_cached_351)
        | (_cmp_cached_352)
        | (_cmp_cached_353)
      )
      # 15m & 1h & 4h up move, 15m & 1h & 4h still not high enough, 4h uptrend
      & (
        (_cmp_cached_354)
        | (_cmp_cached_355)
        | (_cmp_cached_356)
        | (_cmp_cached_345)
        | (_cmp_cached_357)
        | (_cmp_cached_358)
        | (_cmp_cached_359)
        | (_cmp_cached_360)
        | (_cmp_cached_180)
      )
      # 15m & 1h & 4h up move, 1h & 4h still now high enough, 15m uptrend, 1h still not high enough
      & (
        (_cmp_cached_354)
        | (_cmp_cached_361)
        | (_cmp_cached_362)
        | (_cmp_cached_346)
        | (_cmp_cached_334)
        | (_cmp_cached_363)
        | (_cmp_cached_364)
      )
      # 15m & 1h & 4h up move, 15m & 1h & 4h still not high enough, 1h & 4h & 1d uptrend
      & (
        (_cmp_cached_342)
        | (_cmp_cached_365)
        | (_cmp_cached_356)
        | (_cmp_cached_345)
        | (_cmp_cached_357)
        | (_cmp_cached_358)
        | (_cmp_cached_144)
        | (_cmp_cached_180)
        | (_cmp_cached_27)
      )
      # 15m & 1h & 4h up move, 15m & 1h & 4h still not high enough, 1h & 4h uptrend
      & (
        (_cmp_cached_342)
        | (_cmp_cached_355)
        | (_cmp_cached_356)
        | (_cmp_cached_345)
        | (_cmp_cached_357)
        | (_cmp_cached_358)
        | (_cmp_cached_366)
        | (_cmp_cached_367)
        | (_cmp_cached_144)
        | (_cmp_cached_152)
      )
      # 15m & 1h & 4h up move, 15m & 1h & 4h still not high enough, 15m uptrend, 4h still low
      & (
        (_cmp_cached_342)
        | (_cmp_cached_355)
        | (_cmp_cached_356)
        | (_cmp_cached_345)
        | (_cmp_cached_357)
        | (_cmp_cached_334)
        | (_cmp_cached_368)
        | (_cmp_cached_335)
      )
      # 15m & 1h & 4h up move, 15m still not high enough, 1h & 4h still low, 4h still low
      & (
        (_cmp_cached_342)
        | (_cmp_cached_343)
        | (_cmp_cached_344)
        | (_cmp_cached_345)
        | (_cmp_cached_351)
        | (_cmp_cached_352)
        | (_cmp_cached_369)
      )
      # 15m & 1h & 4h up move, 15m & 1h still not high enough, 1h & 4h uptrend
      & (
        (_cmp_cached_370)
        | (_cmp_cached_371)
        | (_cmp_cached_372)
        | (_cmp_cached_373)
        | (_cmp_cached_374)
        | (_cmp_cached_375)
        | (_cmp_cached_144)
        | (_cmp_cached_69)
      )
      # 15m & 1h & 4h up move, 15m & 1h & 4h still not high enough, 15m & 1h & 4h uptrend
      & (
        (_cmp_cached_370)
        | (_cmp_cached_371)
        | (_cmp_cached_356)
        | (_cmp_cached_376)
        | (_cmp_cached_357)
        | (_cmp_cached_358)
        | (_cmp_cached_363)
        | (_cmp_cached_377)
        | (_cmp_cached_378)
      )
      # 15m & 1h & 4h up move, 1h still low, 4h & 1d uptrend
      & (
        (_cmp_cached_370)
        | (_cmp_cached_371)
        | (_cmp_cached_379)
        | (_cmp_cached_380)
        | (_cmp_cached_57)
        | (_cmp_cached_121)
      )
      # 15m & 1h & 4h up move, 1h & 4h still not high enough, 4h overbought
      & (
        (_cmp_cached_370)
        | (_cmp_cached_355)
        | (_cmp_cached_356)
        | (_cmp_cached_381)
        | (_cmp_cached_375)
        | (_cmp_cached_382)
        | (_cmp_cached_126)
      )
      # 15m & 1h & 4h up move, 1h still nt high enough, 1h & 4h uptrend
      & (
        (_cmp_cached_370)
        | (_cmp_cached_383)
        | (_cmp_cached_379)
        | (_cmp_cached_384)
        | (_cmp_cached_364)
        | (_cmp_cached_385)
        | (_cmp_cached_386)
      )
      # 15m & 1h & 4h up move, 15m & 1h & 4h still not high enough, 1h still low, 1h & 4h uptrend
      & (
        (_cmp_cached_370)
        | (_cmp_cached_383)
        | (_cmp_cached_379)
        | (_cmp_cached_387)
        | (_cmp_cached_357)
        | (_cmp_cached_358)
        | (_cmp_cached_388)
        | (_cmp_cached_182)
        | (_cmp_cached_152)
      )
      # 15m & 1h & 4h up move, 4h still not high enough, 15m & 1h & 4h uptrend
      & (
        (_cmp_cached_389)
        | (_cmp_cached_355)
        | (_cmp_cached_356)
        | (_cmp_cached_390)
        | (_cmp_cached_268)
        | (_cmp_cached_144)
        | (_cmp_cached_180)
      )
      # 15m & 1h & 4h up move, 15m & 1h & 4h still not high enough, 4h low, 1h & 4h uptrend
      & (
        (_cmp_cached_389)
        | (_cmp_cached_355)
        | (_cmp_cached_344)
        | (_cmp_cached_345)
        | (_cmp_cached_357)
        | (_cmp_cached_352)
        | (_cmp_cached_349)
        | (_cmp_cached_182)
        | (_cmp_cached_180)
      )
      # 15m & 1h & 4h up move, 15m & 1h & 4h still not high enough, 4h still low, 15m & 1h & 4h uptrend
      & (
        (_cmp_cached_389)
        | (_cmp_cached_355)
        | (_cmp_cached_391)
        | (_cmp_cached_345)
        | (_cmp_cached_357)
        | (_cmp_cached_334)
        | (_cmp_cached_381)
        | (_cmp_cached_268)
        | (_cmp_cached_144)
        | (_cmp_cached_180)
      )
      # 15m & 1h & 4h up move, 15m & 1h & 4h still not high enough, 15m uptrend
      & (
        (_cmp_cached_389)
        | (_cmp_cached_383)
        | (_cmp_cached_379)
        | (_cmp_cached_345)
        | (_cmp_cached_346)
        | (_cmp_cached_334)
        | (_cmp_cached_381)
        | (_cmp_cached_392)
        | (_cmp_cached_268)
      )
      # 15m & 1h & 4h up move, 15m & 1h & 4h still not high enough, 1h low, 4h overbought
      & (
        (_cmp_cached_389)
        | (_cmp_cached_383)
        | (_cmp_cached_379)
        | (_cmp_cached_345)
        | (_cmp_cached_357)
        | (_cmp_cached_358)
        | (_cmp_cached_393)
        | (_cmp_cached_69)
      )
      # 15m & 1h & 4h up move, 15m & 1h & 4h still not high enough, 4h low
      & (
        (_cmp_cached_389)
        | (_cmp_cached_383)
        | (_cmp_cached_350)
        | (_cmp_cached_345)
        | (_cmp_cached_346)
        | (_cmp_cached_352)
        | (_cmp_cached_394)
      )
      # 15m & 1h & 4h up move, 15m & 1h & 4h still not high enough, 4h low, 4h overbought
      & (
        (_cmp_cached_329)
        | (_cmp_cached_330)
        | (_cmp_cached_379)
        | (_cmp_cached_345)
        | (_cmp_cached_357)
        | (_cmp_cached_334)
        | (_cmp_cached_395)
        | (_cmp_cached_126)
      )
      # 15m & 1h & 4h up move, 15m low, 1h uptrend
      & (
        (_cmp_cached_396)
        | (_cmp_cached_397)
        | (_cmp_cached_372)
        | (_cmp_cached_398)
        | (_cmp_cached_399)
      )
      # 15m & 1h & 4h up move, 15m & 1h & 4h uptrend, 15m still low, 1h uptrend
      & (
        (_cmp_cached_396)
        | (_cmp_cached_383)
        | (_cmp_cached_379)
        | (_cmp_cached_363)
        | (_cmp_cached_400)
        | (_cmp_cached_401)
        | (_cmp_cached_402)
        | (_cmp_cached_225)
      )
      # 15m & 1h & 4h up move, 15m & 1h & 4h still not high enough, 4h uptrend
      & (
        (_cmp_cached_396)
        | (_cmp_cached_343)
        | (_cmp_cached_344)
        | (_cmp_cached_387)
        | (_cmp_cached_346)
        | (_cmp_cached_334)
        | (_cmp_cached_364)
        | (_cmp_cached_183)
      )
      # 1h & 4h up move, 1d still low, 15m & 4h still not high enough
      & (
        (_cmp_cached_397)
        | (_cmp_cached_356)
        | (_cmp_cached_403)
        | (_cmp_cached_404)
        | (_cmp_cached_405)
      )
      # 1h & 4h up move, 1d still low, 1h & 4h & 1d uptrend
      & (
        (_cmp_cached_365)
        | (_cmp_cached_406)
        | (_cmp_cached_403)
        | (_cmp_cached_182)
        | (_cmp_cached_180)
        | (_cmp_cached_146)
      )
      # 4h up move, 15m & 1h & 4h still not high enough, 1d still low, 4h still not high enough, 1d still low
      & (
        (_cmp_cached_406)
        | (_cmp_cached_345)
        | (_cmp_cached_357)
        | (_cmp_cached_358)
        | (_cmp_cached_403)
        | (_cmp_cached_382)
        | (_cmp_cached_407)
      )
      # 4h up move, 15m & 1h & 4h still not high enough, 15m low, 15m & 1h & 4h uptrend
      & (
        (_cmp_cached_406)
        | (_cmp_cached_345)
        | (_cmp_cached_357)
        | (_cmp_cached_358)
        | (_cmp_cached_408)
        | (_cmp_cached_272)
        | (_cmp_cached_213)
        | (_cmp_cached_84)
      )
      # 4h up move, 15m & 1h & 4h still not high enough, 1h still low, 1h & 4h overbought
      & (
        (_cmp_cached_406)
        | (_cmp_cached_345)
        | (_cmp_cached_357)
        | (_cmp_cached_409)
        | (_cmp_cached_388)
        | (_cmp_cached_182)
        | (_cmp_cached_248)
      )
    )

    df["global_protections_short_pump"] = (
      # 15m & 1h & 4h & 1d up move, 15m & 1h & 4h still not high enough, 1d still not high enough & uptrend
      (
        (_cmp_cached_410)
        | (_cmp_cached_411)
        | (_cmp_cached_372)
        | (_cmp_cached_412)
        | (_cmp_cached_387)
        | (_cmp_cached_413)
        | (_cmp_cached_414)
        | (_cmp_cached_366)
        | (_cmp_cached_380)
        | (_cmp_cached_415)
        | (_cmp_cached_416)
        | (_cmp_cached_417)
        | (_cmp_cached_418)
        | (_cmp_cached_419)
        | (_cmp_cached_420)
        | (_cmp_cached_234)
      )
      # 15m & 1h & 4h & 1d up move, 15m & 1h & 4h still not high enough, 1d still not high enough & uptrend
      & (
        (_cmp_cached_421)
        | (_cmp_cached_343)
        | (_cmp_cached_356)
        | (_cmp_cached_422)
        | (_cmp_cached_332)
        | (_cmp_cached_413)
        | (_cmp_cached_423)
        | (_cmp_cached_424)
        | (_cmp_cached_358)
        | (_cmp_cached_367)
        | (_cmp_cached_425)
        | (_cmp_cached_27)
      )
      # 1d green, 15m & 1h & 4h & 1d up move, 4h & 1d still not high enough & uptrend
      & (
        (_cmp_cached_421)
        | (_cmp_cached_383)
        | (_cmp_cached_379)
        | (_cmp_cached_426)
        | (_cmp_cached_334)
        | (_cmp_cached_427)
        | (_cmp_cached_382)
        | (_cmp_cached_152)
        | (_cmp_cached_428)
        | (_cmp_cached_121)
      )
      # 15m & 1h & 1d up move, 15m & 1h & 4h still not high enough, 1d still not high enough & uptrend
      & (
        (_cmp_cached_429)
        | (_cmp_cached_383)
        | (_cmp_cached_430)
        | (_cmp_cached_332)
        | (_cmp_cached_431)
        | (_cmp_cached_432)
        | (_cmp_cached_433)
        | (_cmp_cached_434)
        | (_cmp_cached_423)
        | (_cmp_cached_435)
        | (_cmp_cached_436)
        | (_cmp_cached_366)
        | (_cmp_cached_409)
        | (_cmp_cached_437)
        | (_cmp_cached_417)
        | (_cmp_cached_438)
        | (_cmp_cached_163)
      )
      # 15m & 1h & 4h & 1d up move, 15m & 1h & 4h & 1d still not high enough, 1d uptrend
      & (
        (_cmp_cached_396)
        | (_cmp_cached_355)
        | (_cmp_cached_356)
        | (_cmp_cached_426)
        | (_cmp_cached_439)
        | (_cmp_cached_392)
        | (_cmp_cached_440)
        | (_cmp_cached_441)
        | (_cmp_cached_442)
        | (_cmp_cached_416)
        | (_cmp_cached_234)
      )
      # 15m & 1h up move, 15m & 1h & 4h still not high enough, 1d still not high enough & uptrend
      & (
        (_cmp_cached_396)
        | (_cmp_cached_371)
        | (_cmp_cached_439)
        | (_cmp_cached_374)
        | (_cmp_cached_357)
        | (_cmp_cached_443)
        | (_cmp_cached_364)
        | (_cmp_cached_358)
        | (_cmp_cached_428)
        | (_cmp_cached_234)
      )
      # 15m & 1h & 4h & 1d up move, 15m & 1h still not high enough, 4h & 1d stil not high enough & uptrend
      & (
        (_cmp_cached_389)
        | (_cmp_cached_355)
        | (_cmp_cached_356)
        | (_cmp_cached_444)
        | (_cmp_cached_376)
        | (_cmp_cached_445)
        | (_cmp_cached_333)
        | (_cmp_cached_366)
        | (_cmp_cached_446)
        | (_cmp_cached_447)
        | (_cmp_cached_448)
        | (_cmp_cached_417)
        | (_cmp_cached_449)
        | (_cmp_cached_450)
        | (_cmp_cached_69)
        | (_cmp_cached_438)
        | (_cmp_cached_451)
        | (_cmp_cached_159)
      )
      # 15m & 1h & 4h up move, 15m & 1h still not high enough, 4h still not high enough & uptrend
      & (
        (_cmp_cached_389)
        | (_cmp_cached_355)
        | (_cmp_cached_406)
        | (_cmp_cached_332)
        | (_cmp_cached_452)
        | (_cmp_cached_423)
        | (_cmp_cached_453)
        | (_cmp_cached_454)
        | (_cmp_cached_455)
      )
      # 15m & 1h up move, 15m & 1h & 4h still not high enough, 1d still not high enough & uptrend
      & (
        (_cmp_cached_389)
        | (_cmp_cached_365)
        | (_cmp_cached_376)
        | (_cmp_cached_445)
        | (_cmp_cached_414)
        | (_cmp_cached_456)
        | (_cmp_cached_457)
        | (_cmp_cached_446)
        | (_cmp_cached_448)
        | (_cmp_cached_360)
        | (_cmp_cached_449)
        | (_cmp_cached_405)
        | (_cmp_cached_458)
        | (_cmp_cached_159)
      )
      # 15m & 1h & 4h & 1d up move, 15m & 1h & 4h & 1d still not high enough
      & (
        (_cmp_cached_389)
        | (_cmp_cached_365)
        | (_cmp_cached_379)
        | (_cmp_cached_459)
        | (_cmp_cached_376)
        | (_cmp_cached_333)
        | (_cmp_cached_366)
        | (_cmp_cached_446)
        | (_cmp_cached_334)
        | (_cmp_cached_460)
        | (_cmp_cached_367)
        | (_cmp_cached_449)
        | (_cmp_cached_461)
        | (_cmp_cached_462)
      )
      # 15m & 1h & 4h & 1d up move, 1h still not high enough, 1d still low, 4h & 1d uptrend
      & (
        (_cmp_cached_389)
        | (_cmp_cached_371)
        | (_cmp_cached_406)
        | (_cmp_cached_444)
        | (_cmp_cached_388)
        | (_cmp_cached_463)
        | (_cmp_cached_190)
        | (_cmp_cached_121)
      )
      # 15m & 1h & 4h & 1d up move, 15m & 1h still not high enough, 4h & 1d still not high enough & uptrend
      & (
        (_cmp_cached_389)
        | (_cmp_cached_355)
        | (_cmp_cached_406)
        | (_cmp_cached_444)
        | (_cmp_cached_376)
        | (_cmp_cached_434)
        | (_cmp_cached_423)
        | (_cmp_cached_464)
        | (_cmp_cached_415)
        | (_cmp_cached_465)
        | (_cmp_cached_183)
        | (_cmp_cached_425)
        | (_cmp_cached_466)
        | (_cmp_cached_463)
        | (_cmp_cached_159)
      )
      # 15m & 1h & 4h up move, 1h & 4h still not high enough, 1d uptrend
      & (
        (_cmp_cached_370)
        | (_cmp_cached_355)
        | (_cmp_cached_344)
        | (_cmp_cached_436)
        | (_cmp_cached_467)
        | (_cmp_cached_427)
        | (_cmp_cached_416)
        | (_cmp_cached_335)
        | (_cmp_cached_159)
      )
      # 15m & 1h & 4h up move, 15m still not high enough, 1h & 4h still not high enough & uptrend, 1d still not high enough
      & (
        (_cmp_cached_370)
        | (_cmp_cached_371)
        | (_cmp_cached_406)
        | (_cmp_cached_468)
        | (_cmp_cached_469)
        | (_cmp_cached_470)
        | (_cmp_cached_471)
        | (_cmp_cached_445)
        | (_cmp_cached_434)
        | (_cmp_cached_472)
        | (_cmp_cached_473)
        | (_cmp_cached_474)
        | (_cmp_cached_457)
        | (_cmp_cached_144)
        | (_cmp_cached_409)
        | (_cmp_cached_475)
        | (_cmp_cached_476)
        | (_cmp_cached_477)
        | (_cmp_cached_478)
        | (_cmp_cached_126)
        | (_cmp_cached_462)
      )
      # 15m & 1h & 4h up move, 15m & 1h & 4h still not high enough, 1d still not high enough & overbought
      & (
        (_cmp_cached_342)
        | (_cmp_cached_343)
        | (_cmp_cached_344)
        | (_cmp_cached_376)
        | (_cmp_cached_445)
        | (_cmp_cached_346)
        | (_cmp_cached_359)
        | (_cmp_cached_464)
        | (_cmp_cached_479)
        | (_cmp_cached_367)
        | (_cmp_cached_465)
        | (_cmp_cached_480)
        | (_cmp_cached_466)
        | (_cmp_cached_156)
      )
      # 15m & 1h & 4h & 1d up move, 15m & 1h & 4h still not high enough. 1d still not high enough & uptrend
      & (
        (_cmp_cached_354)
        | (_cmp_cached_355)
        | (_cmp_cached_356)
        | (_cmp_cached_426)
        | (_cmp_cached_332)
        | (_cmp_cached_423)
        | (_cmp_cached_364)
        | (_cmp_cached_409)
        | (_cmp_cached_442)
        | (_cmp_cached_428)
        | (_cmp_cached_481)
        | (_cmp_cached_234)
      )
      # 15m & 1h & 4h up move, 15m & 1h still not high enough, 4h still not high enough & uptrend
      & (
        (_cmp_cached_354)
        | (_cmp_cached_365)
        | (_cmp_cached_406)
        | (_cmp_cached_332)
        | (_cmp_cached_445)
        | (_cmp_cached_423)
        | (_cmp_cached_467)
        | (_cmp_cached_424)
        | (_cmp_cached_464)
        | (_cmp_cached_415)
        | (_cmp_cached_482)
        | (_cmp_cached_180)
      )
      # 1h & 4h & 1d up move, 15m still not high enough, 1h & 4h & 1d still not high enough, 1d uptrend
      & (
        (_cmp_cached_355)
        | (_cmp_cached_344)
        | (_cmp_cached_422)
        | (_cmp_cached_374)
        | (_cmp_cached_483)
        | (_cmp_cached_484)
        | (_cmp_cached_485)
        | (_cmp_cached_463)
        | (_cmp_cached_146)
      )
    )

    df["global_protections_short_dump"] = (
      # 15m & 1h up move, 15m & 1h still not high enough, 4h still low, 1d still low & downtrend
      (
        (_cmp_cached_389)
        | (_cmp_cached_383)
        | (_cmp_cached_345)
        | (_cmp_cached_452)
        | (_cmp_cached_414)
        | (_cmp_cached_366)
        | (_cmp_cached_352)
        | (_cmp_cached_416)
        | (_cmp_cached_367)
        | (_cmp_cached_403)
        | (_cmp_cached_419)
        | (_cmp_cached_239)
      )
      # 15m up move, 15m still low, 1h & 4h & 1d still not high
      & (
        (_cmp_cached_370)
        | (_cmp_cached_486)
        | (_cmp_cached_346)
        | (_cmp_cached_487)
        | (_cmp_cached_375)
        | (_cmp_cached_488)
        | (_cmp_cached_334)
        | (_cmp_cached_489)
        | (_cmp_cached_490)
        | (_cmp_cached_394)
        | (_cmp_cached_462)
      )
      # 1h & 4h up move, 15m & 1h & 4h still not high enough, 1d still low & downtrend
      & (
        (_cmp_cached_383)
        | (_cmp_cached_406)
        | (_cmp_cached_468)
        | (_cmp_cached_491)
        | (_cmp_cached_472)
        | (_cmp_cached_492)
        | (_cmp_cached_415)
        | (_cmp_cached_427)
        | (_cmp_cached_493)
        | (_cmp_cached_494)
        | (_cmp_cached_207)
      )
    )

    df["protections_short_rebuy"] = True

    df = self._test_x7_restore_tail_protections(test_x7_full_df, df)

    tok_after_protections = time.perf_counter()
    tok_total = time.perf_counter()
    log.debug(
      f"[{metadata['pair']}] "
      f"populate_indicators pre-protections: "
      f"{tok_before_protections - tik:0.4f}s | "
      f"protections: "
      f"{tok_after_protections - tok_before_protections:0.4f}s | "
      f"total: "
      f"{tok_total - tik:0.4f}s"
    )
    tok = time.perf_counter()
    log.debug("[%s] Populate indicators took a total of: %.4f seconds.", metadata["pair"], tok - tik)

    return df
