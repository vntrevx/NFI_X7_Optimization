"""Extracted entry-signal logic for TestX7.

This file is a behavior-preserving extraction from the synced upstream
NostalgiaForInfinityX7 baseline. Keep changes mechanical and parity-checked.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from freqtrade.persistence import Trade
from pandas import DataFrame

from test_x7_modules.masks import build_comparison_cache, build_expression_cache


def _is_bool_scalar(condition) -> bool:
  return isinstance(condition, (bool, np.bool_))


def _as_bool_array(condition):
  if isinstance(condition, np.ndarray):
    return condition.astype(bool, copy=False)
  if isinstance(condition, (pd.Series, pd.Index)):
    return condition.to_numpy(dtype=bool, copy=False)
  return np.asarray(condition, dtype=bool)


def _and_conditions(conditions):
  arrays = []
  has_false = False
  for condition in conditions:
    if _is_bool_scalar(condition):
      if not condition:
        has_false = True
      continue
    arrays.append(_as_bool_array(condition))
  if not arrays:
    return not has_false
  if has_false:
    return np.zeros_like(arrays[0], dtype=bool)
  if len(arrays) == 1:
    return arrays[0]
  return np.logical_and.reduce(arrays)


def _or_conditions(conditions):
  arrays = []
  has_true = False
  for condition in conditions:
    if _is_bool_scalar(condition):
      if condition:
        has_true = True
      continue
    arrays.append(_as_bool_array(condition))
  if not arrays:
    return has_true
  if has_true:
    return np.ones_like(arrays[0], dtype=bool)
  if len(arrays) == 1:
    return arrays[0]
  return np.logical_or.reduce(arrays)


def _append_entry_tag(entry_tags, mask, tag: str) -> None:
  if _is_bool_scalar(mask):
    if mask:
      entry_tags[:] = entry_tags + tag
    return
  entry_tags[mask] = entry_tags[mask] + tag


class TestX7EntryLogicMixin:
  def populate_entry_trend(self, df: DataFrame, metadata: dict) -> DataFrame:
    long_entry_conditions = []
    short_entry_conditions = []

    entry_tags = np.full(len(df), "", dtype=object)
    df.loc[:, "enter_long"] = 0
    df.loc[:, "enter_short"] = 0
    _cmp = build_comparison_cache(df)
    _gt_mul, _range_lt = build_expression_cache(df)
    _test_x7_short_entries_enabled = any(bool(value) for value in self.short_entry_signal_params.values())
    _ema_26_12_spread_gt_open_pct = ((df["EMA_26"].shift() - df["EMA_12"].shift()) > (df["open"] / 100.0))
    if _test_x7_short_entries_enabled:
      _ema_12_26_spread_gt_open_pct = ((df["EMA_12"].shift() - df["EMA_26"].shift()) > (df["open"] / 100.0))
    _ema_26_12_15m_spread_gt_open_pct = (
      (df["EMA_26_15m"].shift() - df["EMA_12_15m"].shift()) > (df["open_15m"] / 100.0)
    )
    _rsi_20_falling = df["RSI_20"] < df["RSI_20"].shift(1)
    if _test_x7_short_entries_enabled:
      _rsi_20_rising = df["RSI_20"] > df["RSI_20"].shift(1)
    _close_lt_bbl_40_prev = df["close"].lt(df["BBL_40_2.0"].shift())
    _close_lte_close_prev = df["close"].le(df["close"].shift())
    _cmp_cached_0 = _cmp("RSI_3_15m", ">", 10.0)
    _cmp_cached_1 = _cmp("RSI_3_1h", ">", 10.0)
    _cmp_cached_2 = _cmp("RSI_3_1h", ">", 15.0)
    _cmp_cached_3 = _cmp("RSI_3_15m", ">", 15.0)
    _cmp_cached_4 = _cmp("RSI_3_4h", ">", 10.0)
    _cmp_cached_5 = _cmp("RSI_3_4h", ">", 15.0)
    _cmp_cached_6 = _cmp("RSI_3_4h", ">", 20.0)
    _cmp_cached_7 = _cmp("RSI_3_15m", ">", 3.0)
    _cmp_cached_8 = _cmp("RSI_3_1h", ">", 30.0)
    _cmp_cached_9 = _cmp("AROONU_14_1d", "<", 100.0)
    _cmp_cached_10 = _cmp("RSI_3_1h", ">", 20.0)
    _cmp_cached_11 = _cmp("RSI_3_1h", ">", 25.0)
    _cmp_cached_12 = _cmp("AROONU_14_1h", "<", 70.0)
    _cmp_cached_13 = _cmp("AROONU_14_4h", "<", 70.0)
    _cmp_cached_14 = _cmp("AROONU_14_4h", "<", 100.0)
    _cmp_cached_15 = _cmp("ROC_9_1d", ">", -20.0)
    _cmp_cached_16 = _cmp("RSI_3_15m", ">", 20.0)
    _cmp_cached_17 = _cmp("RSI_3_15m", ">", 5.0)
    _cmp_cached_18 = _cmp("AROONU_14_1h", "<", 80.0)
    _cmp_cached_19 = _cmp("RSI_3_4h", ">", 30.0)
    _cmp_cached_20 = _cmp("AROONU_14_4h", "<", 80.0)
    _cmp_cached_21 = _cmp("RSI_3_4h", ">", 25.0)
    _cmp_cached_22 = _cmp("RSI_3_1h", ">", 5.0)
    _cmp_cached_23 = _cmp("ROC_9_1d", ">", -30.0)
    _cmp_cached_24 = _cmp("AROONU_14_15m", "<", 70.0)
    _cmp_cached_25 = _cmp("RSI_3_1h", ">", 35.0)
    _cmp_cached_26 = _cmp("ROC_9_4h", "<", 20.0)
    _cmp_cached_27 = _cmp("ROC_9_4h", "<", 10.0)
    _cmp_cached_28 = _cmp("RSI_3_15m", ">", 25.0)
    _cmp_cached_29 = _cmp("ROC_9_1d", "<", 100.0)
    _cmp_cached_30 = _cmp("STOCHRSIk_14_14_3_3_1h", "<", 50.0)
    _cmp_cached_31 = _cmp("ROC_9_4h", ">", -20.0)
    _cmp_cached_32 = _cmp("AROONU_14_4h", "<", 90.0)
    _cmp_cached_33 = _cmp("RSI_3_1h", ">", 40.0)
    _cmp_cached_34 = _cmp("STOCHRSIk_14_14_3_3_4h", "<", 80.0)
    _cmp_cached_35 = _cmp("ROC_9_1d", "<", 50.0)
    _cmp_cached_36 = _cmp("RSI_3_1h", ">", 3.0)
    _cmp_cached_37 = _cmp("STOCHRSIk_14_14_3_3_1h", "<", 80.0)
    _cmp_cached_38 = _cmp("AROONU_14_1d", "<", 90.0)
    _cmp_cached_39 = _cmp("ROC_9_1d", "<", 20.0)
    _cmp_cached_40 = _cmp("ROC_9_1d", "<", 40.0)
    _cmp_cached_41 = _cmp("RSI_3_4h", ">", 35.0)
    _cmp_cached_42 = _cmp("AROONU_14_1d", "<", 80.0)
    _cmp_cached_43 = _cmp("AROONU_14_4h", "<", 50.0)
    _cmp_cached_44 = _cmp("ROC_9_1d", ">", -40.0)
    _cmp_cached_45 = _cmp("AROONU_14_1d", "<", 70.0)
    _cmp_cached_46 = _cmp("AROONU_14_15m", "<", 50.0)
    _cmp_cached_47 = _cmp("RSI_3_4h", ">", 40.0)
    _cmp_cached_48 = _cmp("RSI_3", ">", 3.0)
    _cmp_cached_49 = _cmp("AROONU_14_1h", "<", 50.0)
    _cmp_cached_50 = _cmp("ROC_9_4h", "<", 30.0)
    _cmp_cached_51 = _cmp("ROC_9_1d", "<", 30.0)
    _cmp_cached_52 = _cmp("AROONU_14_1h", "<", 90.0)
    _cmp_cached_53 = _cmp("RSI_3_1d", ">", 20.0)
    _cmp_cached_54 = _cmp("STOCHRSIk_14_14_3_3_4h", "<", 50.0)
    _cmp_cached_55 = _cmp("STOCHRSIk_14_14_3_3_4h", "<", 90.0)
    _cmp_cached_56 = _cmp("STOCHRSIk_14_14_3_3_1h", "<", 70.0)
    _cmp_cached_57 = _cmp("RSI_3_4h", ">", 5.0)
    _cmp_cached_58 = _cmp("STOCHRSIk_14_14_3_3_4h", "<", 70.0)
    _cmp_cached_59 = _cmp("RSI_3_1d", ">", 15.0)
    _cmp_cached_60 = _cmp("RSI_3_4h", ">", 50.0)
    _cmp_cached_61 = _cmp("ROC_9_1h", "<", 10.0)
    _cmp_cached_62 = _cmp("STOCHRSIk_14_14_3_3_1d", "<", 90.0)
    _cmp_cached_63 = _cmp("RSI_3_1h", ">", 50.0)
    _cmp_cached_64 = _cmp("RSI_3_1d", ">", 25.0)
    _cmp_cached_65 = _cmp("RSI_3_1h", ">", 45.0)
    _cmp_cached_66 = _cmp("RSI_3_1d", ">", 10.0)
    _cmp_cached_67 = _cmp("AROONU_14_4h", "<", 40.0)
    _cmp_cached_68 = _cmp("AROONU_14_4h", "<", 60.0)
    _cmp_cached_69 = _cmp("ROC_9_1d", "<", 80.0)
    _cmp_cached_70 = _cmp("RSI_3_15m", ">", 30.0)
    _cmp_cached_71 = _cmp("AROONU_14_1h", "<", 100.0)
    _cmp_cached_72 = _cmp("ROC_9_4h", ">", -30.0)
    _cmp_cached_73 = _cmp("ROC_9_4h", "<", 40.0)
    _cmp_cached_74 = _cmp("ROC_9_1d", "<", 200.0)
    _cmp_cached_75 = _cmp("STOCHRSIk_14_14_3_3_15m", "<", 50.0)
    _cmp_cached_76 = _cmp("RSI_3_4h", ">", 45.0)
    _cmp_cached_77 = _cmp("RSI_3_1d", ">", 30.0)
    _cmp_cached_78 = _cmp("ROC_9_1d", "<", 10.0)
    _cmp_cached_79 = _cmp("STOCHRSIk_14_14_3_3_4h", "<", 40.0)
    _cmp_cached_80 = _cmp("RSI_3_4h", ">", 3.0)
    _cmp_cached_81 = _cmp("AROONU_14_15m", "<", 40.0)
    _cmp_cached_82 = _cmp("STOCHRSIk_14_14_3_3_1h", "<", 40.0)
    _cmp_cached_83 = _cmp("STOCHRSIk_14_14_3_3_1h", "<", 90.0)
    _cmp_cached_84 = _cmp("STOCHRSIk_14_14_3_3_1d", "<", 80.0)
    _cmp_cached_85 = _cmp("ROC_9_1h", "<", 20.0)
    _cmp_cached_86 = _cmp("AROONU_14_1h", "<", 40.0)
    _cmp_cached_87 = _cmp("RSI_3_4h", ">", 60.0)
    _cmp_cached_88 = _cmp("AROONU_14_1h", "<", 60.0)
    if _test_x7_short_entries_enabled:
      _cmp_cached_89 = _cmp("RSI_3_15m", "<", 95.0)
    _cmp_cached_90 = _cmp("AROONU_14_15m", "<", 60.0)
    if _test_x7_short_entries_enabled:
      _cmp_cached_91 = _cmp("RSI_3_1h", "<", 95.0)
    _cmp_cached_92 = _cmp("AROONU_14_1h", "<", 85.0)
    _cmp_cached_93 = _cmp("AROONU_14_4h", "<", 85.0)
    _cmp_cached_94 = _cmp("STOCHRSIk_14_14_3_3_4h", "<", 30.0)
    _cmp_cached_95 = _cmp("ROC_9_1d", ">", -50.0)
    if _test_x7_short_entries_enabled:
      _cmp_cached_96 = _cmp("RSI_3_15m", "<", 90.0)
    _cmp_cached_97 = _cmp("RSI_3_1h", ">", 60.0)
    _cmp_cached_98 = _cmp("ROC_9_4h", "<", 50.0)
    _cmp_cached_99 = _cmp("ROC_9_1d", "<", 60.0)
    _cmp_cached_100 = _cmp("RSI_3_15m", ">", 35.0)
    if _test_x7_short_entries_enabled:
      _cmp_cached_101 = _cmp("RSI_3_1h", "<", 90.0)

    _cmp_cached_102 = _cmp("ROC_9_4h", ">", -10.0)
    _cmp_cached_103 = _cmp("AROONU_14_1d", "<", 85.0)
    _cmp_cached_104 = _cmp("RSI_3", ">", 5.0)
    _cmp_cached_105 = _cmp("STOCHRSIk_14_14_3_3_4h", "<", 60.0)
    _cmp_cached_106 = _cmp("STOCHRSIk_14_14_3_3_1d", "<", 70.0)
    _cmp_cached_107 = _cmp("RSI_3_1d", ">", 45.0)
    _cmp_cached_108 = _cmp("STOCHRSIk_14_14_3_3_15m", "<", 70.0)
    _cmp_cached_109 = _cmp("STOCHRSIk_14_14_3_3_1h", "<", 30.0)
    _cmp_cached_110 = _cmp("RSI_14_4h", "<", 40.0)
    _cmp_cached_111 = _cmp("AROONU_14_15m", "<", 30.0)
    _cmp_cached_112 = _cmp("STOCHRSIk_14_14_3_3_1h", "<", 60.0)
    _cmp_cached_113 = _cmp("STOCHRSIk_14_14_3_3_15m", "<", 40.0)
    _cmp_cached_114 = _cmp("ROC_9_4h", "<", 80.0)
    _cmp_cached_115 = _cmp("ROC_9_4h", "<", 100.0)
    if _test_x7_short_entries_enabled:
      _cmp_cached_116 = _cmp("RSI_3_4h", "<", 85.0)
    _cmp_cached_117 = _cmp("STOCHRSIk_14_14_3_3_1d", "<", 50.0)
    _cmp_cached_118 = _cmp("RSI_3_1d", ">", 40.0)
    if _test_x7_short_entries_enabled:
      _cmp_cached_119 = _cmp("STOCHRSIk_14_14_3_3_1h", ">", 50.0)
    _cmp_cached_120 = _cmp("ROC_9_1h", ">", -20.0)
    _cmp_cached_121 = _cmp("AROONU_14_1d", "<", 50.0)
    if _test_x7_short_entries_enabled:
      _cmp_cached_122 = _cmp("STOCHRSIk_14_14_3_3_4h", ">", 50.0)
    _cmp_cached_123 = _cmp("ROC_9_4h", "<", 60.0)
    _cmp_cached_124 = _cmp("ROC_9_1h", ">", -30.0)
    _cmp_cached_125 = _cmp("STOCHRSIk_14_14_3_3_15m", "<", 30.0)
    _cmp_cached_126 = _cmp("RSI_3_4h", "<", 90.0)
    if _test_x7_short_entries_enabled:
      _cmp_cached_127 = _cmp("RSI_3_15m", "<", 85.0)
      _cmp_cached_128 = _cmp("RSI_3_1h", "<", 80.0)
    _cmp_cached_129 = _cmp("ROC_9_1h", "<", 30.0)
    _cmp_cached_130 = _cmp("RSI_3_1h", ">", 55.0)
    _cmp_cached_131 = _cmp("RSI_3_4h", ">", 55.0)
    _cmp_cached_132 = _cmp("STOCHRSIk_14_14_3_3_1h", "<", 20.0)
    _cmp_cached_133 = _cmp("RSI_3_1d", ">", 35.0)
    _cmp_cached_134 = _cmp("ROC_9_1h", "<", 40.0)
    _cmp_cached_135 = _cmp("AROONU_14_1d", "<", 40.0)
    if _test_x7_short_entries_enabled:
      _cmp_cached_136 = _cmp("RSI_3_1h", "<", 85.0)
      _cmp_cached_137 = _cmp("STOCHRSIk_14_14_3_3_4h", ">", 30.0)
    _cmp_cached_138 = _cmp("AROONU_14_1h", "<", 30.0)
    _cmp_cached_139 = _cmp("ROC_9_4h", ">", -40.0)
    _cmp_cached_140 = _cmp("RSI_3_15m", ">", 40.0)
    _cmp_cached_141 = _cmp("ROC_9_1d", ">", -15.0)
    _cmp_cached_142 = _cmp("ROC_9_1d", ">", -10.0)
    _cmp_cached_143 = _cmp("RSI_3", ">", 10.0)
    if _test_x7_short_entries_enabled:
      _cmp_cached_144 = _cmp("RSI_3_4h", "<", 95.0)
    _cmp_cached_145 = _cmp("AROONU_14_4h", "<", 30.0)
    _cmp_cached_146 = _cmp("ROC_9_1d", ">", -60.0)
    if _test_x7_short_entries_enabled:
      _cmp_cached_147 = _cmp("STOCHRSIk_14_14_3_3_1h", ">", 70.0)
      _cmp_cached_148 = _cmp("STOCHRSIk_14_14_3_3_1h", ">", 30.0)
    _cmp_cached_149 = _cmp("ROC_9_1d", ">", -25.0)
    _cmp_cached_150 = _cmp("ROC_9_1d", ">", -70.0)
    is_backtest = self.dp.runmode.value in ["backtest", "hyperopt", "plot", "webserver"]
    # Grind mode
    num_open_long_grind_mode = 0
    is_pair_long_grind_mode = metadata["pair"].split("/")[0] in self.grind_mode_coins
    if not is_backtest:
      open_trades = Trade.get_trades_proxy(is_open=True)
      for open_trade in open_trades:
        enter_tag = open_trade.enter_tag
        if enter_tag is not None:
          enter_tags = enter_tag.split()
          if all(c in self.long_grind_mode_tags for c in enter_tags):
            num_open_long_grind_mode += 1
    # Top Coins mode
    is_pair_long_top_coins_mode = metadata["pair"].split("/")[0] in self.top_coins_mode_coins
    is_pair_short_top_coins_mode = metadata["pair"].split("/")[0] in self.top_coins_mode_coins
    # if BTC/ETH stake
    is_btc_stake = self.config["stake_currency"] in self.btc_stakes
    allowed_empty_candles_288 = 144 if is_btc_stake else 60

    ###############################################################################################

    # LONG ENTRY CONDITIONS STARTS HERE

    ###############################################################################################

    #
    #  /$$       /$$$$$$ /$$   /$$ /$$$$$$        /$$$$$$$$/$$   /$$/$$$$$$$$/$$$$$$$$/$$$$$$$
    # | $$      /$$__  $| $$$ | $$/$$__  $$      | $$_____| $$$ | $|__  $$__| $$_____| $$__  $$
    # | $$     | $$  \ $| $$$$| $| $$  \__/      | $$     | $$$$| $$  | $$  | $$     | $$  \ $$
    # | $$     | $$  | $| $$ $$ $| $$ /$$$$      | $$$$$  | $$ $$ $$  | $$  | $$$$$  | $$$$$$$/
    # | $$     | $$  | $| $$  $$$| $$|_  $$      | $$__/  | $$  $$$$  | $$  | $$__/  | $$__  $$
    # | $$     | $$  | $| $$\  $$| $$  \ $$      | $$     | $$\  $$$  | $$  | $$     | $$  \ $$
    # | $$$$$$$|  $$$$$$| $$ \  $|  $$$$$$/      | $$$$$$$| $$ \  $$  | $$  | $$$$$$$| $$  | $$
    # |________/\______/|__/  \__/\______/       |________|__/  \__/  |__/  |________|__/  |__/
    #

    for enabled_long_entry_signal in self.long_entry_signal_params:
      long_entry_condition_index = int(enabled_long_entry_signal.split("_")[3])
      item_buy_protection_list = [True]
      if self.long_entry_signal_params[f"{enabled_long_entry_signal}"]:
        # Long Entry Conditions Starts Here
        # -----------------------------------------------------------------------------------------
        long_entry_logic = []
        long_entry_logic.append(_and_conditions(item_buy_protection_list))

        # Condition #1 - Normal mode (Long).
        if long_entry_condition_index == 1:
          # Protections
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          long_entry_logic.append(df["protections_long_global"] == True)

          long_entry_logic.append(
            # 5m & 15m & 1h down move
            ((_cmp_cached_48) | (_cmp_cached_7) | (_cmp("RSI_3_change_pct_1h", ">", -50.0)))
            # 5m & 15m down move, 5h high
            & ((_cmp_cached_48) | (_cmp_cached_17) | (_cmp("RSI_14_4h", "<", 60.0)))
            # 5m & 15m down move, 4h high
            & ((_cmp_cached_48) | (_cmp_cached_0) | (_cmp_cached_14))
            # 5m & 1h down move
            & ((_cmp_cached_48) | (_cmp_cached_22))
            # 5m & 1h down move, 15m still not low enough
            & ((_cmp_cached_104) | (_cmp_cached_1) | (_cmp_cached_111))
            # 5m & 1h down move, 4h high
            & ((_cmp_cached_48) | (_cmp_cached_11) | (_cmp_cached_34))
            # 15m & 1h down move, 1d still high
            & ((_cmp_cached_7) | (_cmp_cached_36) | (_cmp_cached_117))
            # 5m & 1h down move, 15m still not low enough
            & ((_cmp_cached_48) | (_cmp_cached_2) | (_cmp_cached_111))
            # 5m & 4h down move, 4h high
            & ((_cmp_cached_48) | (_cmp_cached_21) | (_cmp_cached_13))
            # 5m down move, 15m high
            & ((_cmp_cached_48) | (_cmp("AROONU_14_15m", "<", 80.0)))
            # 5m & 4h down move, 4h high
            & ((_cmp_cached_104) | (_cmp_cached_41) | (_cmp_cached_13))
            # 15m down move, 1h downtrend, 1h high
            & ((_cmp("RSI_3_15m", ">", 1.0)) | (_cmp("CMF_20_1h", ">", -0.1)) | (_cmp_cached_12))
            # 15m & 1h & 4h down move
            & ((_cmp_cached_7) | (_cmp_cached_1) | (_cmp_cached_5))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_7) | (_cmp_cached_1) | (_cmp_cached_49))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_7) | (_cmp_cached_1) | (_cmp_cached_9))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_7) | (_cmp_cached_1) | (_cmp_cached_82))
            # 15m & 1h & 4h & 1d down move
            & ((_cmp_cached_7) | (_cmp_cached_2) | (_cmp_cached_5) | (_cmp_cached_59))
            # 15m & 1h down move, 15m still high
            & ((_cmp_cached_7) | (_cmp_cached_10) | (_cmp_cached_81))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_7) | (_cmp_cached_10) | (_cmp_cached_12))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_7) | (_cmp_cached_8) | (_cmp_cached_18))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_7) | (_cmp_cached_25) | (_cmp_cached_54))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_7) | (_cmp_cached_33) | (_cmp_cached_56))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_7) | (_cmp_cached_65) | (_cmp_cached_18))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_7) | (_cmp_cached_5) | (_cmp_cached_62))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_7) | (_cmp_cached_21) | (_cmp_cached_68))
            # 15m & 4h down move, 1d downtrend
            & ((_cmp_cached_7) | (_cmp_cached_19) | (_cmp_cached_95))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_7) | (_cmp_cached_41) | (_cmp_cached_54))
            # 15m down move, 15m downtrend
            & ((_cmp_cached_7) | (_cmp("CMF_20_15m", ">", -0.40)) | (_cmp("ROC_9_15m", ">", -20.0)))
            # 15m down move, 15m still high, 15m downtrend
            & ((_cmp_cached_7) | (_cmp_cached_81) | (_cmp("ROC_9_15m", ">", -20.0)))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_7) | (_cmp_cached_92) | (_cmp_cached_32))
            # 15m down move, 4h high, 15m downtrend
            & ((_cmp_cached_7) | (_cmp_cached_13) | (_cmp("ROC_9_15m", ">", -20.0)))
            # 15m down move, 4h high, 1d overbought
            & ((_cmp_cached_7) | (_cmp_cached_93) | (_cmp_cached_29))
            # 15m down move, 1h high, 4h overbought
            & ((_cmp_cached_7) | (_cmp_cached_83) | (_cmp_cached_27))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_7) | (_cmp_cached_34) | (_cmp_cached_50))
            # 15m down move, drop in last half hour, 15m downtrend
            & ((_cmp_cached_7) | _gt_mul("close", "close_max_6", 0.75) | (_cmp("ROC_9_15m", ">", -20.0)))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_17) | (_cmp_cached_22) | (_cmp_cached_49))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_17) | (_cmp_cached_22) | (_cmp_cached_13))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_17) | (_cmp_cached_22) | (_cmp_cached_40))
            # 5m & 1h down move, 1h overbought
            & ((_cmp_cached_17) | (_cmp_cached_97) | (_cmp_cached_134))
            # 15m & 4h down move, 1d still high
            & ((_cmp_cached_17) | (_cmp_cached_57) | (_cmp("STOCHRSIk_14_14_3_3_1d", "<", 40.0)))
            # 15m & 4h down move, 1d downtrend
            & ((_cmp_cached_17) | (_cmp_cached_57) | (_cmp_cached_15))
            # 15m & 4h down move, 1h still high
            & ((_cmp_cached_17) | (_cmp_cached_4) | (_cmp_cached_30))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_17) | (_cmp_cached_5) | (_cmp("STOCHRSIk_14_14_3_3_1d", "<", 60.0)))
            # 15m & 4h down move, 15m still high
            & ((_cmp_cached_17) | (_cmp_cached_19) | (_cmp_cached_75))
            # 15m down move, 15m & 4h still high
            & ((_cmp_cached_17) | (_cmp_cached_46) | (_cmp_cached_68))
            # 15m down move, 15m still high, 1d overbought
            & ((_cmp_cached_17) | (_cmp_cached_46) | (_cmp_cached_69))
            # 15m down move, 15m high
            & ((_cmp_cached_17) | (_cmp("AROONU_14_15m", "<", 80.0)))
            # 15m down move, 4h high, 1d overbought
            & ((_cmp_cached_17) | (_cmp_cached_68) | (_cmp_cached_69))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_0) | (_cmp_cached_1) | (_cmp_cached_82))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_1) | (_cmp_cached_58))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_0) | (_cmp_cached_2) | (_cmp_cached_30))
            # 15m & 1h down move, 1d downtrend
            & ((_cmp_cached_0) | (_cmp_cached_2) | (_cmp_cached_44))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_10) | (_cmp("RSI_14_4h", "<", 80.0)))
            # 15m & 1h down move, 15m still high
            & ((_cmp_cached_0) | (_cmp_cached_10) | (_cmp_cached_46))
            # 15m & 1h down move, 4h overbought
            & ((_cmp_cached_0) | (_cmp_cached_11) | (_cmp_cached_114))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_0) | (_cmp_cached_4) | (_cmp("AROONU_14_1h", "<", 75.0)))
            # 15m & 4h down move, 15m still high
            & ((_cmp_cached_0) | (_cmp_cached_4) | (_cmp_cached_75))
            # 15m & 4h down move, 1h still high
            & ((_cmp_cached_0) | (_cmp_cached_4) | (_cmp_cached_82))
            # 15m & 4h down move, 4h downtrend
            & ((_cmp_cached_0) | (_cmp_cached_4) | (_cmp_cached_31))
            # 15m & 4h down move, 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_21) | (_cmp_cached_51))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_0) | (_cmp_cached_19) | (_cmp_cached_92))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_87) | (_cmp_cached_55))
            # 15m & 1d down move, 1d high
            & ((_cmp_cached_0) | (_cmp("RSI_3_1d", ">", 50.0)) | (_cmp_cached_84))
            # 15m down move & downtrend, 4h high
            & ((_cmp_cached_0) | (_cmp("CMF_20_15m", ">", -0.3)) | (_cmp_cached_14))
            # 15m down move, 15m & 4h high
            & ((_cmp_cached_0) | (_cmp_cached_24) | (_cmp_cached_20))
            # 15m down move, 1h high & overbought
            & ((_cmp_cached_0) | (_cmp_cached_52) | (_cmp_cached_85))
            # 15m down move, 1h high, 1d downtrend
            & ((_cmp_cached_0) | (_cmp_cached_52) | (_cmp_cached_44))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_71) | (_cmp_cached_69))
            # 15m down move, 1h high, 4h downtrend
            & ((_cmp_cached_0) | (_cmp_cached_56) | (_cmp("ROC_9_4h", ">", -25.0)))
            # 15m down move, 1h high, 1d downtrend
            & ((_cmp_cached_0) | (_cmp_cached_56) | (_cmp_cached_95))
            # 15m down move, 1h high & overbought
            & ((_cmp_cached_0) | (_cmp_cached_83) | (_cmp_cached_85))
            # 15m down move, 1h & 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_61) | (_cmp_cached_69))
            # 15m down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_123))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_10) | (_cmp_cached_18))
            # 15m down move, 15m still high, 4h overbought
            & ((_cmp_cached_3) | (_cmp("RSI_14_15m", "<", 50.0)) | (_cmp_cached_98))
            # 15m down move, 15m & 1h high
            & ((_cmp_cached_3) | (_cmp_cached_24) | (_cmp_cached_71))
            # 15m down move, 15m & 1h high
            & ((_cmp_cached_3) | (_cmp("AROONU_14_15m", "<", 80.0)) | (_cmp_cached_52))
            # 15m & 4h down move, 15m still high
            & ((_cmp_cached_16) | (_cmp_cached_41) | (_cmp_cached_81))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_16) | (_cmp_cached_71) | (_cmp_cached_14))
            # 15m down move, 1h high & overbought
            & ((_cmp_cached_16) | (_cmp_cached_71) | (_cmp_cached_85))
            # 15m down move, 1d overbought
            & ((_cmp_cached_70) | (_cmp_cached_69))
            # 15m & 4h down move, 15m high
            & ((_cmp_cached_140) | (_cmp_cached_76) | (_cmp_cached_108))
            # 1h & 4h down move, 4h downtrend
            & ((_cmp_cached_36) | (_cmp_cached_4) | (_cmp_cached_102))
            # 1h & 4h down move, 1h still high
            & ((_cmp_cached_36) | (_cmp_cached_5) | (_cmp_cached_49))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_36) | (_cmp_cached_5) | (_cmp_cached_38))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_36) | (_cmp_cached_21) | (_cmp_cached_9))
            # 1h & 1d down move, 4h still high
            & ((_cmp_cached_36) | (_cmp_cached_59) | (_cmp_cached_54))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_22) | (_cmp_cached_57) | (_cmp_cached_78))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_22) | (_cmp_cached_4) | (_cmp_cached_67))
            # 1h & 4h down move, 1h downtrend
            & ((_cmp_cached_22) | (_cmp_cached_4) | (_cmp("CMF_20_1h", ">", -0.3)))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_22) | (_cmp_cached_4) | (_cmp_cached_44))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_22) | (_cmp_cached_5) | (_cmp_cached_145))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_22) | (_cmp_cached_60) | (_cmp_cached_13))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_22) | (_cmp_cached_6) | (_cmp_cached_40))
            # 1h & 1d down move, 1d downtrend
            & ((_cmp_cached_22) | (_cmp("RSI_3_1d", ">", 5.0)) | (_cmp_cached_23))
            # 1h down move, 1h still high, 4h high
            & ((_cmp_cached_22) | (_cmp_cached_49) | (_cmp_cached_32))
            # 1h down move, 1d high, 4h downtrend
            & ((_cmp_cached_22) | (_cmp_cached_38) | (_cmp_cached_72))
            # 1h & 4h down move, 15m still not low enough
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp_cached_111))
            # 1h & 4h down move, 1h still high
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp_cached_30))
            # 1h & 1d down move, 4h high
            & ((_cmp_cached_1) | (_cmp_cached_53) | (_cmp_cached_20))
            # 1h down move, 4h high
            & ((_cmp_cached_1) | (_cmp("RSI_14_4h", "<", 75.0)))
            # 1h down move, 15m downtrend, 1d high
            & ((_cmp_cached_1) | (_cmp("CMF_20_15m", ">", -0.40)) | (_cmp_cached_45))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_1) | (_cmp_cached_12) | (_cmp_cached_27))
            # 1h down move, 4h overbought
            & ((_cmp_cached_1) | (_cmp_cached_98))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_2) | (_cmp_cached_5) | (_cmp_cached_67))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_2) | (_cmp_cached_6) | (_cmp_cached_20))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_2) | (_cmp_cached_21) | (_cmp_cached_40))
            # 15m down move, 1h high, 1d downtrend
            & ((_cmp_cached_2) | (_cmp_cached_12) | (_cmp_cached_15))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_2) | (_cmp_cached_12) | (_cmp_cached_35))
            # 1h down move, 1h high
            & ((_cmp_cached_2) | (_cmp_cached_18))
            # 1h down mve, 4h high, 1d overbought
            & ((_cmp_cached_2) | (_cmp_cached_20) | (_cmp_cached_51))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_2) | (_cmp_cached_42) | (_cmp_cached_40))
            # 1h down move, 1h & 4h downtrend
            & ((_cmp_cached_2) | (_cmp_cached_124) | (_cmp_cached_72))
            # 1h & 4h down move, 4h overbought
            & ((_cmp_cached_10) | (_cmp_cached_60) | (_cmp_cached_114))
            # 1h down move, 1h still high, 4h downtrend
            & ((_cmp_cached_10) | (_cmp_cached_86) | (_cmp_cached_72))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_10) | (_cmp_cached_13) | (_cmp_cached_74))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_10) | (_cmp_cached_32) | (_cmp_cached_99))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_10) | (_cmp_cached_14) | (_cmp_cached_98))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_10) | (_cmp_cached_62) | (_cmp_cached_69))
            # 1h down move, 1h high, 15n downtrend
            & ((_cmp_cached_11) | (_cmp_cached_12) | (_cmp("ROC_9_15m", ">", -20.0)))
            # 1h down move, 1h still high, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_30) | (_cmp_cached_40))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_114) | (_cmp_cached_29))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_25) | (_cmp_cached_32) | (_cmp_cached_15))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_25) | (_cmp_cached_38) | (_cmp_cached_69))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_25) | (_cmp_cached_73) | (_cmp_cached_69))
            # 1h down move, 1h downtrend, 1h high
            & ((_cmp_cached_33) | (_cmp("CMF_20_1h", ">", -0.25)) | (_cmp_cached_52))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_33) | (_cmp_cached_88) | (_cmp_cached_14))
            # 1h down move, 1h high, 15m downtrend
            & ((_cmp_cached_33) | (_cmp_cached_18) | (_cmp("ROC_9_15m", ">", -15.0)))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_33) | (_cmp_cached_18) | (_cmp_cached_29))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_65) | (_cmp_cached_18) | (_cmp_cached_14))
            # 1h down move, 1h high & overbought
            & ((_cmp_cached_63) | (_cmp_cached_52) | (_cmp_cached_85))
            # 1h down move, 1h still high, 4h high
            & ((_cmp_cached_97) | (_cmp_cached_49) | (_cmp("RSI_14_4h", "<", 90.0)))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_57) | (_cmp_cached_53) | (_cmp_cached_135))
            # 4h down move, 4h & 1d downtrend
            & ((_cmp_cached_57) | (_cmp_cached_72) | (_cmp_cached_44))
            # 4h & 1d down move, 4h still not low enough
            & ((_cmp_cached_4) | (_cmp_cached_59) | (_cmp("AROONU_14_4h", "<", 20.0)))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_4) | (_cmp_cached_64) | (_cmp_cached_117))
            # 4h down move, 4h still high
            & ((_cmp_cached_4) | (_cmp_cached_43))
            # 4h down move, 1d high
            & ((_cmp_cached_4) | (_cmp_cached_9))
            # 4h down move, 1h high, 1d downtrend
            & ((_cmp_cached_4) | (_cmp_cached_112) | (_cmp_cached_44))
            # 4h down move, 4h still not low enough, 1d downtrend
            & ((_cmp_cached_4) | (_cmp_cached_94) | (_cmp_cached_15))
            # 4h down move, 1h & 4h downtrend
            & ((_cmp_cached_4) | (_cmp_cached_124) | (_cmp_cached_72))
            # 4h down move, 4h & 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_31) | (_cmp_cached_23))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_6) | (_cmp_cached_42) | (_cmp_cached_69))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_21) | (_cmp_cached_43) | (_cmp_cached_44))
            # 4h down move, 4h high, 1d overbought
            & ((_cmp_cached_19) | (_cmp_cached_20) | (_cmp_cached_35))
            # 4h down move, 1d overbought
            & ((_cmp_cached_76) | (_cmp_cached_69))
            # 4h down move, 4h high, 1d overbought
            & ((_cmp_cached_60) | (_cmp_cached_13) | (_cmp_cached_40))
            # 4h down move, 1h high, 1d overbought
            & ((_cmp_cached_87) | (_cmp_cached_83) | (_cmp_cached_99))
            # 1d down move, 1h high, 1d downtrend
            & ((_cmp("RSI_3_1d", ">", 5.0)) | (_cmp_cached_83) | (_cmp_cached_15))
            # 1d down move, 1h still high, 4h high
            & ((_cmp_cached_53) | (_cmp_cached_49) | (_cmp_cached_32))
            # 1d down move, 1h & 4h high
            & ((_cmp_cached_64) | (_cmp_cached_18) | (_cmp_cached_32))
            # 1d down move, 1d high
            & ((_cmp_cached_118) | (_cmp_cached_42))
            # 1d down move, 4h still high, 1d overbought
            & ((_cmp("RSI_3_1d", ">", 50.0)) | (_cmp_cached_43) | (_cmp_cached_74))
            # 1d down move, 1d high & overbought
            & ((_cmp("RSI_3_1d", ">", 60.0)) | (_cmp_cached_42) | (_cmp_cached_35))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp("RSI_3_change_pct_1h", ">", -75.0)) | (_cmp_cached_32) | (_cmp_cached_29))
            # 15m & 1h & 4h downtrend
            & ((_cmp("CMF_20_15m", ">", -0.3)) | (_cmp("CMF_20_1h", ">", -0.3)) | (_cmp("CMF_20_4h", ">", -0.3)))
            # 15m high, 1d overbought
            & ((_cmp_cached_24) | (_cmp_cached_69))
            # 1h still high, 1h & 4h downtrend
            & ((_cmp_cached_86) | (_cmp_cached_120) | (_cmp_cached_72))
            # 1h & 4h high, 1h overbought
            & ((_cmp_cached_92) | (_cmp_cached_32) | (_cmp_cached_85))
            # 1h high, 1h & 4h overbought
            & ((_cmp_cached_92) | (_cmp_cached_61) | (_cmp_cached_51))
            # 1h high, 1h overbought, 1d downtrend
            & ((_cmp_cached_92) | (_cmp_cached_85) | (_cmp_cached_44))
            # 4h & 1d high, 1d overbought
            & ((_cmp_cached_20) | (_cmp_cached_9) | (_cmp_cached_35))
            # 4h high, 1h downtrend
            & ((_cmp_cached_20) | (_cmp("ROC_9_1h", ">", -15.0)))
            # 4h high, 1d downtrend
            & ((_cmp_cached_20) | (_cmp_cached_44))
            # 1d high, 4h downtrend, 1d overbought
            & ((_cmp_cached_103) | (_cmp("ROC_9_4h", ">", -25.0)) | (_cmp_cached_35))
            # 1d high, 1h & 4h downtrend
            & ((_cmp_cached_38) | (_cmp("ROC_9_1h", ">", -10.0)) | (_cmp_cached_31))
            # 1d high, 4h & 1d overbought
            & ((_cmp_cached_38) | (_cmp_cached_73) | (_cmp_cached_69))
            # 1h high, 4h overbought
            & ((_cmp_cached_37) | (_cmp_cached_114))
            # 4h high, 1h downtrend
            & ((_cmp_cached_58) | (_cmp("ROC_9_1h", ">", -15.0)))
            # 4h high, 1d downtrend
            & ((_cmp_cached_58) | (_cmp_cached_44))
            # 5m down move, 15m still not low enough, 1h high
            & ((_cmp("ROC_2", ">", -10.0)) | (_cmp_cached_111) | (_cmp_cached_18))
            # 5m down move, 15m still high
            & ((_cmp("ROC_2", ">", -10.0)) | (_cmp_cached_46))
            # 5m down move, 15m & 1h down move, 15m still high
            & (
              (_cmp("ROC_9", ">", -15.0)) | (_cmp_cached_17) | (_cmp_cached_25) | (_cmp_cached_46)
            )
            # 5m down move, 4h down move, 15m downtrend, 1h high
            & (
              (_cmp("ROC_9", ">", -15.0)) | (_cmp_cached_76) | (_cmp("CMF_20_15m", ">", -0.3)) | (_cmp_cached_88)
            )
            # 1h downtrend, 4h high & overbought
            & ((_cmp("ROC_9_1h", ">", -25.0)) | (_cmp_cached_20) | (_cmp_cached_114))
            # 1h & 4h overbought, 1d downtrend
            & ((_cmp_cached_85) | (_cmp_cached_26) | (_cmp_cached_44))
            # 1d P&D, 1d downtrend
            & ((_cmp("change_pct_1d", ">", -5.0)) | (df["change_pct_1d"].shift(288) < 30.0) | (_cmp("CMF_20_1d", ">", -0.0)))
            # 1d green with top wick, 1h down move
            & ((_cmp("change_pct_1d", "<", 20.0)) | (_cmp("top_wick_pct_1d", "<", 15.0)) | (_cmp_cached_10))
            # 1d green with top wick, 4h high
            & ((_cmp("change_pct_1d", "<", 25.0)) | (_cmp("top_wick_pct_1d", "<", 25.0)) | (_cmp_cached_20))
            # 1d green, 1h down move, 1d downtrend
            & ((_cmp("change_pct_1d", "<", 40.0)) | (_cmp_cached_11) | (_cmp("CMF_20_1d", ">", -0.2)))
            # 1d green with top wick, 4h overbought
            & ((_cmp("change_pct_1d", "<", 50.0)) | (_cmp("top_wick_pct_1d", "<", 30.0)) | (_cmp_cached_114))
            # big drop in the last hour, 15m downtrend
            & (_gt_mul("close", "close_max_12", 0.65) | (_cmp("CMF_20_15m", ">", -0.5)))
            # big drop in the last 6 hours, 1h down move, 1h high
            & (_gt_mul("close", "high_max_6_1h", 0.60) | (_cmp_cached_10) | (_cmp_cached_88))
            # big drop in the last 24 hours,  1h still high
            & (_gt_mul("close", "high_max_24_1h", 0.40) | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 45.0)))
            # big drop in the last 4 days, 1h high
            & (_gt_mul("close", "high_max_24_4h", 0.20) | (_cmp_cached_12))
            # big drop in the last 20 days, 1d high, 1d downtrend
            & (
              _gt_mul("close", "high_max_20_1d", 0.20)
              | (_cmp_cached_106)
              | (_cmp_cached_141)
            )
          )

          # Logic
          long_entry_logic.append(
            (df["EMA_26"] > df["EMA_12"])
            & ((df["EMA_26"] - df["EMA_12"]) > (df["open"] * 0.034))
            & _ema_26_12_spread_gt_open_pct
            & (df["close"] < (df["BBL_20_2.0"] * 0.999))
          )

        # Condition #2 - Normal mode (Long).
        if long_entry_condition_index == 2:
          # Protections
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          long_entry_logic.append(df["protections_long_global"] == True)

          long_entry_logic.append(
            # 5m & 1h down move, 1h still not low enough
            ((_cmp_cached_48) | (_cmp_cached_1) | (_cmp_cached_138))
            # 5m & 1h down move, 1d high
            & ((_cmp_cached_48) | (_cmp_cached_10) | (_cmp_cached_9))
            # 5m & 1h down move, 1h still high
            & ((_cmp_cached_48) | (_cmp_cached_8) | (_cmp_cached_30))
            # 5m & 1h down move, 1d high
            & ((_cmp_cached_48) | (_cmp_cached_25) | (_cmp_cached_9))
            # 5m & 4h down move, 15m still not low enough
            & ((_cmp_cached_48) | (_cmp_cached_80) | (_cmp_cached_125))
            # 5m & 4h down move, 1d downtrend
            & ((_cmp_cached_48) | (_cmp_cached_5) | (_cmp_cached_23))
            # 5m & 4h down move, 4h high
            & ((_cmp_cached_48) | (_cmp_cached_76) | (_cmp_cached_34))
            # 5m & 4h down move, 15m still high
            & ((_cmp_cached_104) | (_cmp_cached_21) | (_cmp_cached_75))
            # 5m & 1d down move, 1h still high
            & ((_cmp_cached_48) | (_cmp_cached_66) | (_cmp_cached_86))
            # 5m & 1d down move, 1h still high
            & ((_cmp_cached_48) | (_cmp_cached_66) | (_cmp_cached_30))
            # 5m & 1d down move, 1d downtrend
            & ((_cmp_cached_48) | (_cmp_cached_59) | (_cmp("CMF_20_1d", ">", -0.25)))
            # 5m & 1d down move, 15m still high
            & ((_cmp_cached_48) | (_cmp_cached_53) | (_cmp_cached_113))
            # 5m down move, 1h high
            & ((_cmp_cached_48) | (_cmp_cached_18))
            # 5m down move, 4h high, 1d overbought
            & ((_cmp_cached_48) | (_cmp_cached_20) | (_cmp_cached_51))
            # 5m down move, 4h high & overbought
            & ((_cmp_cached_48) | (_cmp_cached_14) | (_cmp_cached_26))
            # 5m down move, 4h & 1d overbought
            & ((_cmp_cached_48) | (_cmp_cached_26) | (_cmp_cached_40))
            # 5m down move, 1d downtrend
            & ((_cmp_cached_48) | (_cmp_cached_44))
            # 5m & 15m down move, 15m still high
            & ((_cmp_cached_104) | (_cmp_cached_0) | (_cmp_cached_113))
            # 5m & 15m down move, 1h high
            & ((_cmp_cached_104) | (_cmp_cached_70) | (_cmp_cached_37))
            # 5m & 4h down move, 1d downtrend
            & ((_cmp_cached_104) | (_cmp_cached_4) | (_cmp_cached_15))
            # 5m & 4h down move, 4h still not low enough
            & ((_cmp_cached_104) | (_cmp_cached_5) | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 20.0)))
            # 5m down move, 4h high, 1h overbought
            & ((_cmp_cached_143) | (_cmp_cached_14) | (_cmp_cached_129))
            # 15m & 1h down move, 1h still high
            & ((_cmp("RSI_3_15m", ">", 1.0)) | (_cmp_cached_11) | (_cmp_cached_82))
            # 15m & 1h & 4h down move
            & ((_cmp_cached_7) | (_cmp_cached_36) | (_cmp_cached_5))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_7) | (_cmp_cached_36) | (_cmp_cached_43))
            # 15m & 1h down move, 15m downtrend
            & ((_cmp_cached_7) | (_cmp_cached_22) | (_cmp("CMF_20_15m", ">", -0.30)))
            # 15m & 1h down move, 15m still not low enough
            & ((_cmp_cached_7) | (_cmp_cached_22) | (_cmp_cached_111))
            # 15m & 1h down move, 1h still not low enough
            & ((_cmp_cached_7) | (_cmp_cached_22) | (_cmp("AROONU_14_1h", "<", 25.0)))
            # 15m & 1h down move, 1h still not low enough
            & ((_cmp_cached_7) | (_cmp_cached_22) | (_cmp_cached_109))
            # 15m & 1h & 4h down move
            & ((_cmp_cached_7) | (_cmp_cached_1) | (_cmp_cached_4))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_7) | (_cmp_cached_1) | (_cmp_cached_109))
            # 15m & 1h down move, 1d downtrend
            & ((_cmp_cached_7) | (_cmp_cached_1) | (_cmp_cached_44))
            # 15m & 1h down move, 15m downtrend
            & ((_cmp_cached_7) | (_cmp_cached_2) | (_cmp("CMF_20_15m", ">", -0.40)))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_7) | (_cmp_cached_2) | (_cmp_cached_54))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_7) | (_cmp_cached_10) | (_cmp_cached_12))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_7) | (_cmp_cached_10) | (_cmp_cached_30))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_7) | (_cmp_cached_10) | (_cmp_cached_105))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_7) | (_cmp_cached_8) | (_cmp_cached_88))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_7) | (_cmp_cached_8) | (_cmp_cached_56))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_7) | (_cmp_cached_25) | (_cmp_cached_86))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_7) | (_cmp_cached_25) | (_cmp_cached_106))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_7) | (_cmp_cached_33) | (_cmp_cached_12))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_7) | (_cmp_cached_33) | (_cmp_cached_34))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_7) | (_cmp_cached_65) | (_cmp_cached_92))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_7) | (_cmp_cached_97) | (_cmp_cached_37))
            # 15m & 4h down move, 4h downtrend
            & ((_cmp_cached_7) | (_cmp_cached_57) | (_cmp("CMF_20_4h", ">", -0.35)))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_7) | (_cmp_cached_4) | (_cmp_cached_42))
            # 15m & 4h down move, 1d downtrend
            & ((_cmp_cached_7) | (_cmp_cached_4) | (_cmp_cached_15))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_7) | (_cmp_cached_19) | (_cmp_cached_79))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_7) | (_cmp_cached_41) | (_cmp_cached_54))
            # 15m down move, 15m still not low enough, 1h high
            & ((_cmp_cached_7) | (_cmp("AROONU_14_15m", "<", 20.0)) | (_cmp_cached_112))
            # 15m down move, 15m still not low enough, 1h still high
            & ((_cmp_cached_7) | (_cmp_cached_111) | (_cmp_cached_30))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_7) | (_cmp_cached_12) | (_cmp_cached_39))
            # 15m down move, 4h still high, 15m downtrend
            & ((_cmp_cached_7) | (_cmp_cached_67) | (_cmp("CMF_20_15m", ">", -0.35)))
            # 15m down move, 4h high, 1d overbought
            & ((_cmp_cached_7) | (_cmp_cached_13) | (_cmp_cached_51))
            # 15m down move, 4h & 1d downtrend
            & ((_cmp_cached_7) | (_cmp_cached_72) | (_cmp_cached_95))
            # 15m & 1h & 4h down move
            & ((_cmp_cached_17) | (_cmp_cached_22) | (_cmp_cached_4))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_17) | (_cmp_cached_1) | (_cmp_cached_110))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_17) | (_cmp_cached_1) | (_cmp_cached_86))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_17) | (_cmp_cached_1) | (_cmp_cached_14))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_17) | (_cmp_cached_2) | (_cmp_cached_105))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_17) | (_cmp_cached_33) | (_cmp_cached_34))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_17) | (_cmp_cached_65) | (_cmp_cached_18))
            # 15m & 4h down move, 1d still high
            & ((_cmp_cached_17) | (_cmp_cached_57) | (_cmp("STOCHRSIk_14_14_3_3_1d", "<", 40.0)))
            # 15m & 4h down move, 15m still not low enough
            & ((_cmp_cached_17) | (_cmp_cached_4) | (_cmp_cached_125))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_17) | (_cmp_cached_4) | (_cmp_cached_106))
            # 15m & 4h down move, 15m still high
            & ((_cmp_cached_17) | (_cmp_cached_5) | (_cmp_cached_81))
            # 15m & 4h down move, 1h still high
            & ((_cmp_cached_17) | (_cmp_cached_5) | (_cmp_cached_30))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_17) | (_cmp_cached_5) | (_cmp_cached_54))
            # 15m & 4h down move, 1d overbought
            & ((_cmp_cached_17) | (_cmp_cached_6) | (_cmp_cached_78))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_17) | (_cmp_cached_76) | (_cmp_cached_67))
            # 15m & 1d down move, 15m still not low enough
            & ((_cmp_cached_17) | (_cmp_cached_66) | (_cmp_cached_111))
            # 15m & 1d down move, 1h high
            & ((_cmp_cached_17) | (_cmp_cached_118) | (_cmp_cached_83))
            # 15m down move, 15m downtrend, 4h still not low enough
            & ((_cmp_cached_17) | (_cmp("CMF_20_15m", ">", -0.30)) | (_cmp_cached_94))
            # 15m down move, 15m still not low enough, 4h high
            & ((_cmp_cached_17) | (_cmp("AROONU_14_15m", "<", 20.0)) | (_cmp_cached_58))
            # 15m down move, 15m stil high, 1h still high
            & ((_cmp_cached_17) | (_cmp_cached_81) | (_cmp_cached_30))
            # 15m down move, 1d high & overbought
            & ((_cmp_cached_17) | (_cmp_cached_42) | (_cmp_cached_39))
            # 15m down move, 15m still not low enough, 1h still high
            & (
              (_cmp_cached_17) | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 20.0)) | (_cmp_cached_30)
            )
            # 15m down move, 1h still high, 4h overbought
            & ((_cmp_cached_17) | (_cmp_cached_30) | (_cmp_cached_50))
            # 15m down move, 1h high & overbought
            & ((_cmp_cached_17) | (_cmp_cached_37) | (_cmp_cached_85))
            # 15m & 1h down move, 15m high
            & ((_cmp_cached_0) | (_cmp_cached_1) | (_cmp_cached_75))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_0) | (_cmp_cached_1) | (_cmp_cached_49))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_1) | (_cmp_cached_68))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_0) | (_cmp_cached_1) | (_cmp_cached_106))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_0) | (_cmp_cached_2) | (_cmp_cached_18))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_10) | (_cmp_cached_58))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_11) | (_cmp("AROONU_14_4h", "<", 75.0)))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_0) | (_cmp_cached_11) | (_cmp_cached_43))
            # 15m & 1h down move, 1d downtrend
            & ((_cmp_cached_0) | (_cmp_cached_11) | (_cmp_cached_95))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_8) | (_cmp_cached_51))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_0) | (_cmp_cached_25) | (_cmp("RSI_14_4h", "<", 50.0)))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_0) | (_cmp_cached_25) | (_cmp_cached_112))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_33) | (_cmp_cached_34))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_0) | (_cmp_cached_63) | (_cmp_cached_56))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_63) | (_cmp_cached_34))
            # 16m & 1h down move, 1h high
            & ((_cmp_cached_0) | (_cmp_cached_130) | (_cmp_cached_56))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_130) | (_cmp_cached_55))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_0) | (_cmp_cached_33) | (_cmp_cached_12))
            # 15m & 4h down move, 4h still not low enough
            & ((_cmp_cached_0) | (_cmp_cached_4) | (_cmp_cached_94))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_0) | (_cmp_cached_4) | (_cmp_cached_84))
            # 15m & 4h down move, 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_4) | (_cmp_cached_39))
            # 15m & 4h down move, 4h still not low enough
            & ((_cmp_cached_0) | (_cmp_cached_6) | (_cmp_cached_94))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_0) | (_cmp_cached_19) | (_cmp_cached_38))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_0) | (_cmp_cached_19) | (_cmp_cached_62))
            # 15m & 4h down move, 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_19) | (_cmp_cached_51))
            # 15m & 4h down move, 4h overbought
            & ((_cmp_cached_0) | (_cmp_cached_131) | (_cmp_cached_98))
            # 15m & 1d down move, 1d still high
            & ((_cmp_cached_0) | (_cmp_cached_66) | (_cmp("RSI_14_1d", "<", 40.0)))
            # 15m & 1d down move, 1h high
            & ((_cmp_cached_0) | (_cmp_cached_66) | (_cmp_cached_83))
            # 15m & 1d down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_59) | (_cmp_cached_55))
            # 15m down move, 15m downtrend, 1h high
            & ((_cmp_cached_0) | (_cmp("CMF_20_15m", ">", -0.40)) | (_cmp_cached_18))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_18) | (_cmp_cached_39))
            # 15m down move, 4h & 1d high
            & ((_cmp_cached_0) | (_cmp_cached_13) | (_cmp_cached_9))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_0) | (_cmp_cached_13) | (_cmp_cached_27))
            # 15m down move, 15m still not low enough, 4h high
            & ((_cmp_cached_0) | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 20.0)) | (_cmp_cached_13))
            # 15m down move, 15m sill high, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_113) | (_cmp_cached_68))
            # 15m down move, 4h high, 1d downtrend
            & ((_cmp_cached_0) | (_cmp_cached_34) | (_cmp_cached_23))
            # 15m & 1h down move, 4h downtrend
            & ((_cmp_cached_3) | (_cmp_cached_2) | (_cmp_cached_31))
            # 15m & 1h down move, 1h downtrend
            & ((_cmp_cached_3) | (_cmp_cached_10) | (_cmp("CMF_20_1h", ">", -0.30)))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_3) | (_cmp_cached_11) | (_cmp_cached_29))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_8) | (_cmp_cached_20))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_33) | (_cmp_cached_12))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_3) | (_cmp_cached_33) | (_cmp_cached_38))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_65) | (_cmp_cached_58))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_5) | (_cmp_cached_12))
            # 15m & 4h down move, 4h downtrend
            & ((_cmp_cached_3) | (_cmp_cached_5) | (_cmp_cached_31))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_3) | (_cmp_cached_6) | (_cmp_cached_38))
            # 15m & 1d down move, 1h still high
            & ((_cmp_cached_3) | (_cmp_cached_59) | (_cmp_cached_86))
            # 15m & 1d down move, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_77) | (_cmp_cached_32))
            # 15m down move, 15m still not low enough, 4h high
            & ((_cmp_cached_3) | (_cmp("AROONU_14_15m", "<", 25.0)) | (_cmp_cached_68))
            # 15m down move, 15m still not low enough, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_111) | (_cmp_cached_12))
            # 15m down move, 15m & 4h still high
            & ((_cmp_cached_3) | (_cmp_cached_81) | (_cmp_cached_67))
            # 15m down move, 1h still high, 4h overbought
            & ((_cmp_cached_3) | (_cmp_cached_49) | (_cmp_cached_123))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_3) | (_cmp_cached_88) | (_cmp_cached_32))
            # 15m down move, 1h & 1d high
            & ((_cmp_cached_3) | (_cmp_cached_12) | (_cmp_cached_38))
            # 15m down move, 4h high, 4h downtrend
            & ((_cmp_cached_3) | (_cmp_cached_68) | (_cmp_cached_31))
            # 15m down move, 4h & 1d high
            & ((_cmp_cached_3) | (_cmp("AROONU_14_4h", "<", 75.0)) | (_cmp_cached_9))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_3) | (_cmp_cached_20) | (_cmp_cached_27))
            # 15m down move, 15m still high, 1d overbought
            & ((_cmp_cached_3) | (_cmp_cached_75) | (_cmp_cached_29))
            # 15m down move, 1h high & overbought
            & ((_cmp_cached_3) | (_cmp_cached_83) | (_cmp_cached_61))
            # 15m down move, 4h high, 1d overbought
            & ((_cmp_cached_3) | (_cmp_cached_58) | (_cmp_cached_78))
            # 15m & 1h down move, 15m still not low enough
            & ((_cmp_cached_16) | (_cmp_cached_10) | (_cmp_cached_111))
            # 15m & 1h down move, 4h overbought
            & ((_cmp_cached_16) | (_cmp_cached_10) | (_cmp_cached_98))
            # 15m & 1h down move, 15m high
            & ((_cmp_cached_16) | (_cmp_cached_11) | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 80.0)))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_16) | (_cmp_cached_11) | (_cmp_cached_34))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_16) | (_cmp_cached_8) | (_cmp_cached_12))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_16) | (_cmp_cached_65) | (_cmp_cached_37))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_16) | (_cmp_cached_6) | (_cmp_cached_37))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_16) | (_cmp_cached_47) | (_cmp_cached_20))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_16) | (_cmp_cached_18) | (_cmp_cached_20))
            # 15m down move, 1h & 1d high
            & ((_cmp_cached_16) | (_cmp_cached_18) | (_cmp_cached_42))
            # 15m down move, 1h high, 1d downtrend
            & ((_cmp_cached_16) | (_cmp_cached_52) | (_cmp_cached_23))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_16) | (_cmp_cached_56) | (_cmp_cached_29))
            # 15m down move, 1h high, 1d downtrend
            & ((_cmp_cached_16) | (_cmp_cached_37) | (_cmp_cached_15))
            # 15m down move, 1h high & overbought
            & ((_cmp_cached_16) | (_cmp_cached_83) | (_cmp_cached_61))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_28) | (_cmp_cached_33) | (_cmp_cached_69))
            # 15m & 4h down move, 1h overbought
            & ((_cmp_cached_28) | (_cmp_cached_41) | (_cmp("ROC_9_1h", "<", 100.0)))
            # 15m down move, 15m still not low enough, 1h high
            & ((_cmp_cached_28) | (_cmp("AROONU_14_15m", "<", 20.0)) | (_cmp_cached_83))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_28) | (_cmp_cached_12) | (_cmp_cached_14))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_28) | (_cmp_cached_12) | (_cmp_cached_35))
            # 15m down move, 4h high, 1d overbought
            & ((_cmp_cached_28) | (_cmp_cached_13) | (_cmp_cached_35))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_70) | (_cmp_cached_13) | (_cmp_cached_98))
            # 15m down move, 1h high, 1d downtrend
            & ((_cmp_cached_70) | (_cmp_cached_37) | (_cmp_cached_15))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_70) | (_cmp_cached_34) | (_cmp_cached_50))
            # 15m down move, 1h high, 4h overbought
            & ((_cmp_cached_100) | (_cmp_cached_18) | (_cmp_cached_114))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_100) | (_cmp_cached_32) | (_cmp_cached_98))
            # 15m down move, 4h high, 1d overbought
            & ((_cmp_cached_100) | (_cmp_cached_14) | (_cmp_cached_85))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_100) | (_cmp_cached_37) | (_cmp_cached_69))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_140) | (_cmp_cached_14) | (_cmp_cached_73))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp("RSI_3_1h", ">", 1.0)) | (_cmp_cached_5) | (_cmp_cached_142))
            # 1h down move, 15m downtrend, 1h still high
            & ((_cmp_cached_36) | (_cmp("CMF_20_15m", ">", -0.40)) | (_cmp_cached_86))
            # 1h & 4h down move, 15m downtrend
            & ((_cmp_cached_36) | (_cmp_cached_80) | (_cmp("ROC_9_15m", ">", -30.0)))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_36) | (_cmp_cached_57) | (_cmp_cached_67))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_36) | (_cmp_cached_5) | (_cmp_cached_110))
            # 1h & 4h down move, 1h still not low enough
            & ((_cmp_cached_36) | (_cmp_cached_6) | (_cmp("AROONU_14_1h", "<", 20.0)))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_36) | (_cmp_cached_6) | (_cmp_cached_42))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_36) | (_cmp_cached_21) | (_cmp_cached_78))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_36) | (_cmp_cached_60) | (_cmp_cached_13))
            # 1h & 1d down move, 15m still high
            & ((_cmp_cached_36) | (_cmp_cached_66) | (_cmp_cached_75))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_22) | (_cmp_cached_57) | (_cmp_cached_79))
            # 1h & 4h down move, 1d still high
            & ((_cmp_cached_22) | (_cmp_cached_57) | (_cmp_cached_117))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_22) | (_cmp_cached_57) | (_cmp_cached_23))
            # 1h % 4h down move, 4h downtrend
            & ((_cmp_cached_22) | (_cmp_cached_4) | (_cmp("CMF_20_4h", ">", -0.30)))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_22) | (_cmp_cached_87) | (_cmp_cached_54))
            # 1h & 4h down move, 15m high
            & ((_cmp_cached_22) | (_cmp_cached_4) | (_cmp_cached_108))
            # 1h & 4h down move, 1h still high
            & ((_cmp_cached_22) | (_cmp_cached_5) | (_cmp_cached_49))
            # 1h & 4h down move, 4h downtrend
            & ((_cmp_cached_22) | (_cmp_cached_5) | (_cmp_cached_72))
            # 1h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_22) | (_cmp_cached_54) | (_cmp_cached_95))
            # 1h & 4h & 1d down move
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp_cached_59))
            # 1h & 4h down move, 1d still high
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp_cached_135))
            # 1h & 4h down move, 1h still not low enough
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp_cached_132))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp_cached_15))
            # 1h & 4h down move, 15m high
            & ((_cmp_cached_1) | (_cmp_cached_5) | (_cmp_cached_108))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_5) | (_cmp_cached_44))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_1) | (_cmp_cached_19) | (_cmp_cached_54))
            # 1h & 1d down move, 15m still high
            & ((_cmp_cached_1) | (_cmp_cached_59) | (_cmp_cached_113))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_1) | (_cmp_cached_41) | (_cmp_cached_110))
            # 1h down move, 1h still not low enough 1d overbought
            & ((_cmp_cached_1) | (_cmp_cached_138) | (_cmp_cached_29))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_2) | (_cmp_cached_5) | (_cmp("RSI_14_1d", "<", 60.0)))
            # 1h & 4h down move, 1h still not low enough
            & ((_cmp_cached_2) | (_cmp_cached_5) | (_cmp("AROONU_14_1h", "<", 20.0)))
            # 1h & 4h down move, 15m still high
            & ((_cmp_cached_2) | (_cmp_cached_5) | (_cmp_cached_75))
            # 1h & 4h down move, 4h downtrend
            & ((_cmp_cached_2) | (_cmp_cached_5) | (_cmp_cached_31))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_2) | (_cmp_cached_6) | (_cmp_cached_110))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_2) | (_cmp_cached_21) | (_cmp_cached_94))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_2) | (_cmp_cached_19) | (_cmp_cached_84))
            # 1h & 4h down move, 4h downtrend
            & ((_cmp_cached_2) | (_cmp_cached_19) | (_cmp_cached_72))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_2) | (_cmp_cached_47) | (_cmp_cached_13))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_2) | (_cmp_cached_47) | (_cmp_cached_54))
            # 1h & 1d down move, 1d high
            & ((_cmp_cached_2) | (_cmp_cached_64) | (_cmp_cached_42))
            # 1h & 1d down move, 1d overbought
            & ((_cmp_cached_2) | (_cmp_cached_133) | (_cmp_cached_78))
            # 1h down move, 1h still high, 1d downtrend
            & ((_cmp_cached_2) | (_cmp_cached_86) | (_cmp_cached_44))
            # 1h down move, 4h high, 1d high
            & ((_cmp_cached_2) | (_cmp_cached_68) | (_cmp_cached_9))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_2) | (_cmp_cached_68) | (_cmp_cached_35))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_2) | (_cmp_cached_105) | (_cmp_cached_27))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_2) | (_cmp_cached_62) | (_cmp_cached_40))
            # 1h down move, 4h & 1d downtrend
            & ((_cmp_cached_2) | (_cmp_cached_31) | (_cmp_cached_15))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_10) | (_cmp_cached_6) | (_cmp_cached_39))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_10) | (_cmp_cached_41) | (_cmp_cached_54))
            # 1h & 1d down move, 1h still high
            & ((_cmp_cached_10) | (_cmp_cached_77) | (_cmp_cached_30))
            # 1h down move, 1h high, 4h downtrend
            & ((_cmp_cached_10) | (_cmp_cached_12) | (_cmp_cached_102))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_10) | (_cmp_cached_12) | (_cmp_cached_27))
            # 1h down move, 1h high, 1h still not low enough
            & ((_cmp_cached_10) | (_cmp_cached_42) | (_cmp_cached_132))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_10) | (_cmp_cached_9) | (_cmp_cached_39))
            # 1h down move, 1d high, 4h downtrend
            & ((_cmp_cached_10) | (_cmp_cached_84) | (_cmp_cached_31))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_11) | (_cmp_cached_19) | (_cmp_cached_68))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_11) | (_cmp_cached_19) | (_cmp_cached_23))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_11) | (_cmp_cached_88) | (_cmp_cached_32))
            # 1h down move, 1h high
            & ((_cmp_cached_11) | (_cmp_cached_92))
            # 1h down move, 4h high, 4h downtrend
            & ((_cmp_cached_11) | (_cmp_cached_13) | (_cmp("CMF_20_4h", ">", -0.50)))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_11) | (_cmp_cached_42) | (_cmp_cached_40))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_50) | (_cmp_cached_29))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_8) | (_cmp_cached_88) | (_cmp_cached_14))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_8) | (_cmp_cached_12) | (_cmp_cached_27))
            # 1h down move, 4h & 1d high
            & ((_cmp_cached_8) | (_cmp_cached_20) | (_cmp_cached_9))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_8) | (_cmp_cached_20) | (_cmp_cached_51))
            # 1h down move, 4h downtrend, 1d overbought
            & ((_cmp_cached_8) | (_cmp_cached_72) | (_cmp_cached_74))
            # 1h down move, 4h & 1d downtrend
            & ((_cmp_cached_8) | (_cmp("ROC_9_4h", ">", -25.0)) | (_cmp_cached_146))
            # 1h & 4h down move, 1h still high
            & ((_cmp_cached_25) | (_cmp_cached_41) | (_cmp_cached_82))
            # 1h down move, 1h still high, 4h downtrend
            & ((_cmp_cached_25) | (_cmp_cached_49) | (_cmp_cached_31))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_25) | (_cmp_cached_12) | (_cmp_cached_149))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_25) | (_cmp_cached_93) | (_cmp_cached_115))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_25) | (_cmp_cached_93) | (_cmp_cached_29))
            # 1h down move, 1d high, 4h overbought
            & ((_cmp_cached_25) | (_cmp_cached_9) | (_cmp_cached_73))
            # 1h down move, 1h still high, 1d overbought
            & ((_cmp_cached_25) | (_cmp_cached_30) | (_cmp_cached_74))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_33) | (_cmp_cached_12) | (_cmp_cached_14))
            # 1h down move, 1h & 1d high
            & ((_cmp_cached_33) | (_cmp_cached_18) | (_cmp_cached_42))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_33) | (_cmp_cached_18) | (_cmp_cached_78))
            # 1h down move, 4h still high, 1d overbought
            & ((_cmp_cached_33) | (_cmp_cached_67) | (_cmp_cached_29))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_65) | (_cmp_cached_87) | (_cmp_cached_14))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_65) | (_cmp("RSI_3_4h", ">", 65.0)) | (_cmp_cached_74))
            # 1h down move, 1h high & overbought
            & ((_cmp_cached_63) | (_cmp_cached_18) | (_cmp_cached_61))
            # 1h down move, 4h high, 1h overbought
            & ((_cmp_cached_63) | (_cmp_cached_93) | (_cmp_cached_85))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_63) | (_cmp_cached_105) | (_cmp_cached_146))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_63) | (_cmp_cached_34) | (_cmp_cached_115))
            # 1h down move, 1h & 4h overbought
            & ((_cmp_cached_63) | (_cmp_cached_61) | (_cmp_cached_115))
            # 1h down move, 1h high & overbought
            & ((_cmp_cached_130) | (_cmp_cached_52) | (_cmp_cached_61))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_130) | (_cmp_cached_14) | (_cmp_cached_27))
            # 1h down move, 1h high & overbought
            & ((_cmp_cached_130) | (_cmp_cached_37) | (_cmp_cached_61))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_80) | (_cmp_cached_59) | (_cmp_cached_135))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_80) | (_cmp_cached_53) | (_cmp("STOCHRSIk_14_14_3_3_1d", "<", 40.0)))
            # 4h & 1d down move, 1d downtrend
            & ((_cmp_cached_57) | (_cmp_cached_59) | (_cmp_cached_15))
            # 4h down move, 15m still high
            & ((_cmp_cached_57) | (_cmp_cached_75))
            # 4h & 1d down move, 1h still not low enough
            & ((_cmp_cached_4) | (_cmp_cached_66) | (_cmp_cached_132))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_4) | (_cmp_cached_59) | (_cmp("STOCHRSIk_14_14_3_3_1d", "<", 40.0)))
            # 4h & 1d down move, 1d downtrend
            & ((_cmp_cached_4) | (_cmp_cached_53) | (_cmp_cached_149))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_4) | (_cmp_cached_133) | (_cmp_cached_9))
            # 4h & 1d down move, 1d overbought
            & ((_cmp_cached_4) | (_cmp_cached_107) | (_cmp_cached_78))
            # 4h down move, 1d still high, 1d downtrend
            & ((_cmp_cached_4) | (_cmp_cached_135) | (_cmp_cached_15))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_4) | (_cmp_cached_38) | (_cmp_cached_40))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_4) | (_cmp_cached_79) | (_cmp_cached_15))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_53) | (_cmp("AROONU_14_1d", "<", 60.0)))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_43) | (_cmp_cached_15))
            # 4h & 1d down move, 4h still high
            & ((_cmp_cached_6) | (_cmp_cached_53) | (_cmp_cached_79))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_6) | (_cmp_cached_53) | (_cmp_cached_84))
            # 4h down move, 1h high, 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_52) | (_cmp_cached_142))
            # 4h down move, 4h still high, 4h downtrend
            & ((_cmp_cached_5) | (_cmp_cached_43) | (_cmp_cached_31))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_6) | (_cmp_cached_45) | (_cmp_cached_35))
            # 4h & 1d down move, 1d overbought
            & ((_cmp_cached_21) | (_cmp_cached_118) | (_cmp_cached_51))
            # 4h down move, 4h still high, 1d overbought
            & ((_cmp_cached_21) | (_cmp_cached_67) | (_cmp_cached_29))
            # 4h down move, 4h still high. 4h downtrend
            & ((_cmp_cached_21) | (_cmp_cached_43) | (_cmp("CMF_20_4h", ">", -0.40)))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_21) | (_cmp_cached_43) | (_cmp_cached_44))
            # 4h down move, 4h high, 4h downtrend
            & ((_cmp_cached_21) | (_cmp_cached_13) | (_cmp_cached_72))
            # 4h & 1d down move, 1d overbought
            & ((_cmp_cached_19) | (_cmp("RSI_3_1d", ">", 60.0)) | (_cmp_cached_99))
            # 4h down move, 1d downtrend
            & ((_cmp_cached_19) | (_cmp_cached_95))
            # 4h down move, 4h & 1d overbought
            & ((_cmp_cached_41) | (_cmp_cached_50) | (_cmp_cached_74))
            # 4h down move, 1h high, 1d overbought
            & ((_cmp_cached_47) | (_cmp_cached_12) | (_cmp_cached_40))
            # 4h down move, 4h & 1d downtrend
            & ((_cmp_cached_47) | (_cmp_cached_20) | (_cmp_cached_9))
            # 4h down move, 4h high, 1d downtrend
            & ((_cmp_cached_47) | (_cmp_cached_58) | (_cmp_cached_146))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_47) | (_cmp_cached_62) | (_cmp_cached_29))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_76) | (_cmp_cached_107) | (_cmp_cached_9))
            # 4h down move, 4h high, 1d downtrend
            & ((_cmp_cached_76) | (_cmp_cached_13) | (_cmp_cached_23))
            # 4h down move, 4h high & overbought
            & ((_cmp_cached_60) | (_cmp_cached_13) | (_cmp_cached_27))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_60) | (_cmp_cached_103) | (_cmp_cached_69))
            # 4h down move, 1d high, 4h overbought
            & ((_cmp_cached_131) | (_cmp_cached_62) | (_cmp_cached_27))
            # 4h down move, 4h high & overbought
            & ((_cmp_cached_87) | (_cmp_cached_13) | (_cmp_cached_26))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_87) | (_cmp_cached_9) | (_cmp_cached_74))
            # 4h down move, 4h & 1d overbought
            & ((_cmp_cached_87) | (_cmp_cached_26) | (_cmp_cached_39))
            # 4h down move, 4h overbought
            & ((_cmp_cached_87) | (_cmp_cached_123))
            # 1d down move, 1d high, 1d downtrend
            & ((_cmp("RSI_3_1d", ">", 5.0)) | (_cmp_cached_42) | (_cmp_cached_15))
            # 1d down move, 1h & 4h high
            & ((_cmp_cached_66) | (_cmp_cached_49) | (_cmp_cached_32))
            # 1d down move, 1h high
            & ((_cmp_cached_66) | (_cmp_cached_12))
            # 1d down move, 1h high, 1d downtrend
            & ((_cmp_cached_66) | (_cmp_cached_37) | (_cmp_cached_15))
            # 1d down move, 1h overbought, 1d downtrend
            & ((_cmp_cached_59) | (_cmp_cached_85) | (_cmp_cached_95))
            # 1d down move, 1h high, 1d downtrend
            & ((_cmp_cached_53) | (_cmp_cached_83) | (_cmp_cached_142))
            # 1d down move, 1h high, 1d overbought
            & ((_cmp_cached_64) | (_cmp_cached_12) | (_cmp("ROC_9_1d", "<", 25.0)))
            # 1d down move, 1d still high, 1d downtrend
            & ((_cmp_cached_64) | (_cmp_cached_117) | (_cmp_cached_15))
            # 1d down move, 1h high & overbought
            & ((_cmp_cached_118) | (_cmp_cached_45) | (_cmp_cached_69))
            # 1d down move, 4h high & overbought
            & ((_cmp_cached_107) | (_cmp_cached_55) | (_cmp_cached_123))
            # 1d downtrend, 1d high & overbought
            & ((_cmp("CMF_20_1d", ">", -0.40)) | (_cmp_cached_103) | (_cmp_cached_39))
            # 1h high, 4h & 1d overbought
            & ((_cmp_cached_12) | (_cmp_cached_98) | (_cmp_cached_74))
            # 1h & 4h high, 1d overbought
            & ((_cmp_cached_12) | (_cmp_cached_32) | (_cmp_cached_35))
            # 1h & 4h high, 1d downtrend
            & ((_cmp_cached_12) | (_cmp_cached_14) | (_cmp_cached_44))
            # 1h high, 4h & 1d downtrend
            & ((_cmp_cached_12) | (_cmp_cached_72) | (_cmp_cached_95))
            # 1h & 4h high, 1h overbought
            & ((_cmp_cached_18) | (_cmp_cached_32) | (_cmp_cached_129))
            # 1h & 4high, 1d downtrend
            & ((_cmp_cached_18) | (_cmp_cached_14) | (_cmp_cached_15))
            # 1h & 4h high, 1d overbought
            & ((_cmp_cached_18) | (_cmp_cached_14) | (_cmp_cached_69))
            # 1h & 1d high, 1d overbought
            & ((_cmp_cached_18) | (_cmp_cached_9) | (_cmp_cached_51))
            # 1h high, 1d downtrend
            & ((_cmp_cached_18) | (_cmp_cached_44))
            # 1h & 4h high, 1d overbought
            & ((_cmp_cached_52) | (_cmp_cached_14) | (_cmp_cached_51))
            # 1h high, 4h & 1d overbought
            & ((_cmp_cached_52) | (_cmp_cached_73) | (_cmp_cached_40))
            # 4h still high, 5m downtrend
            & ((_cmp_cached_67) | (_cmp("ROC_9", ">", -40.0)))
            # 4h high & overbought
            & ((_cmp_cached_13) | (_cmp_cached_114))
            # 4h & 1d high, 1d overbought
            & ((_cmp_cached_20) | (_cmp_cached_9) | (_cmp_cached_40))
            # 4h high, 1h & 4h overbought
            & ((_cmp_cached_14) | (_cmp_cached_61) | (_cmp_cached_26))
            # 1d high, 1d downtrend
            & ((_cmp_cached_42) | (_cmp_cached_23))
            # 1d high, 1h & 4h downtrend
            & ((_cmp_cached_103) | (_cmp_cached_124) | (_cmp("ROC_9_4h", ">", -50.0)))
            # 1d high, 4h & 1d overbought
            & ((_cmp_cached_103) | (_cmp_cached_123) | (_cmp_cached_99))
            # 1d high, 1h & 4h down move
            & ((_cmp_cached_9) | (_cmp("ROC_9_1h", "<", 25.0)) | (_cmp_cached_123))
            # 15m high, 1d overbought
            & ((_cmp_cached_108) | (_cmp_cached_99))
            # 1h high, 1d downtrend
            & ((_cmp_cached_56) | (_cmp_cached_95))
            # 1h high, 1d overbought
            & ((_cmp_cached_56) | (_cmp_cached_40))
            # 1h high, 4h downtrend
            & ((_cmp_cached_37) | (_cmp_cached_31))
            # 1h high, 4h overbought
            & ((_cmp_cached_37) | (_cmp_cached_114))
            # 4h high, 1h & 4h overbought
            & ((_cmp_cached_34) | (_cmp_cached_61) | (_cmp_cached_26))
            # 1d high, 1h & 1d overbought
            & ((_cmp_cached_84) | (_cmp_cached_61) | (_cmp_cached_69))
            # 1d high, 4h & 1d overbought
            & ((_cmp_cached_84) | (_cmp_cached_123) | (_cmp_cached_99))
            # big drop in the last 20 days, 1d high, 1d downtrend
            & (
              _gt_mul("close", "high_max_20_1d", 0.20)
              | (_cmp_cached_106)
              | (_cmp_cached_141)
            )
            # drop in last 20 days, 1h high, 1d downtrend
            & (_gt_mul("close", "high_max_20_1d", 0.20) | (_cmp_cached_12) | (_cmp_cached_150))
            # drop in last 20 days. 4h high
            & (_gt_mul("close", "high_max_20_1d", 0.10) | (_cmp_cached_55))
          )

          # Logic
          long_entry_logic.append(
            # (_cmp_cached_104)
            (_cmp("AROONU_14", "<", 30.0))
            & (_cmp("STOCHRSIk_14_14_3_3", "<", 30.0))
            # & (_cmp_cached_17)
            & (_cmp_cached_46)
            & (df["close"] < (df["EMA_20"] * 0.948))
          )

        # Condition #3 - Normal mode (Long).
        if long_entry_condition_index == 3:
          # Protections
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          long_entry_logic.append(df["protections_long_global"] == True)

          long_entry_logic.append(
            # 5m & 4h down move, 1h still high
            ((_cmp_cached_104) | (_cmp_cached_5) | (_cmp_cached_30))
            # 5m down move, 15m high, 1d overbought
            & ((_cmp_cached_104) | (_cmp_cached_24) | (_cmp_cached_40))
            # 5m down move, 15m still high, 1d downtrend
            & ((_cmp_cached_104) | (_cmp_cached_75) | (_cmp_cached_15))
            # 5m down move, 1h still high, 4h downtrend
            & ((_cmp_cached_104) | (_cmp_cached_30) | (_cmp_cached_102))
            # 5m down move, 1h high. 1d downtrend
            & ((_cmp_cached_104) | (_cmp_cached_37) | (_cmp_cached_23))
            # 5m down move, 15m & 1h high
            & ((_cmp_cached_143) | (_cmp_cached_24) | (_cmp_cached_71))
            # 5m down move, 15m & 1d high
            & ((_cmp_cached_143) | (_cmp_cached_24) | (_cmp_cached_9))
            # 5m down move, 1h & 1d high
            & ((_cmp("RSI_3", ">", 15.0)) | (_cmp_cached_18) | (_cmp_cached_38))
            # 15m & 1h dowbn move, 1d high
            & ((_cmp_cached_17) | (_cmp_cached_11) | (_cmp_cached_62))
            # 15m & 1d down move, 1h high
            & ((_cmp_cached_17) | (_cmp_cached_59) | (_cmp_cached_112))
            # 15m & 1h down move, 15m still high
            & ((_cmp_cached_0) | (_cmp_cached_25) | (_cmp_cached_46))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_0) | (_cmp_cached_4) | (_cmp_cached_82))
            # 15m & 4h down move, 15m still high
            & ((_cmp_cached_0) | (_cmp_cached_6) | (_cmp_cached_46))
            # 15m down move, 15m still high, 1h high
            & ((_cmp_cached_0) | (_cmp_cached_81) | (_cmp_cached_83))
            # 15m down move, 15m still high, 1h high
            & ((_cmp_cached_0) | (_cmp_cached_46) | (_cmp_cached_37))
            # 15m down move, 15m still high, 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_46) | (_cmp_cached_29))
            # 15m down move, 15m high, 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_90) | (_cmp_cached_35))
            # 15m down move, 4h high, 1d downtrend
            & ((_cmp_cached_0) | (_cmp_cached_34) | (_cmp_cached_15))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_3) | (_cmp_cached_25) | (_cmp_cached_43))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_25) | (_cmp_cached_112))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_65) | (_cmp_cached_37))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_63) | (_cmp("AROONU_14_1h", "<", 75.0)))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_5) | (_cmp_cached_13))
            # 15m & 4h down move, 1d downtrend
            & ((_cmp_cached_3) | (_cmp_cached_5) | (_cmp_cached_23))
            # 15m & 4h down move, 15m still high
            & ((_cmp_cached_3) | (_cmp_cached_5) | (_cmp_cached_75))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_3) | (_cmp_cached_6) | (_cmp_cached_9))
            # 15m & 1d down move, 15m high
            & ((_cmp_cached_3) | (_cmp_cached_59) | (_cmp_cached_24))
            # 15m down move, 4h downtrend. 15m high
            & ((_cmp_cached_3) | (_cmp("CMF_20_4h", ">", -0.30)) | (_cmp_cached_90))
            # 15m down move, 15m still high, 1h still high
            & ((_cmp_cached_3) | (_cmp_cached_81) | (_cmp_cached_49))
            # 15m down move, 15m high, 4h downtrend
            & ((_cmp_cached_3) | (_cmp_cached_90) | (_cmp_cached_31))
            # 15m down move, 15m high, 1d downtrend
            & ((_cmp_cached_3) | (_cmp_cached_90) | (_cmp_cached_150))
            # 15m down move, 15m high, 1d overbought
            & ((_cmp_cached_3) | (_cmp_cached_90) | (_cmp_cached_29))
            # 15m down move, 15m & 1h high
            & ((_cmp_cached_3) | (_cmp_cached_24) | (_cmp_cached_12))
            # 15m down move, 15m & 4h high
            & ((_cmp_cached_3) | (_cmp_cached_24) | (_cmp_cached_13))
            # 15m down move, 15m & 1d high
            & ((_cmp_cached_3) | (_cmp_cached_24) | (_cmp_cached_9))
            # 15m down move, 15m still high, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_24) | (_cmp_cached_34))
            # 15m down move, 15m high, 1d overbought
            & ((_cmp_cached_3) | (_cmp_cached_24) | (_cmp_cached_35))
            # 15m down move, 4h high, 1d downtrend
            & ((_cmp_cached_3) | (_cmp_cached_43) | (_cmp_cached_44))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_3) | (_cmp_cached_37) | (_cmp_cached_39))
            # 15m down move, 4h & 1d overbought
            & ((_cmp_cached_3) | (_cmp("ROC_9_4h", "<", 25.0)) | (_cmp_cached_29))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_16) | (_cmp_cached_11) | (_cmp_cached_86))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_16) | (_cmp_cached_65) | (_cmp_cached_92))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_16) | (_cmp_cached_65) | (_cmp_cached_20))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_16) | (_cmp_cached_65) | (_cmp_cached_9))
            # 15m & 4h down move, 15m high
            & ((_cmp_cached_16) | (_cmp_cached_6) | (_cmp_cached_90))
            # 15m & 4h down move, 15m high
            & ((_cmp_cached_16) | (_cmp_cached_19) | (_cmp("AROONU_14_15m", "<", 75.0)))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_16) | (_cmp_cached_19) | (_cmp_cached_62))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_16) | (_cmp_cached_87) | (_cmp_cached_13))
            # 15m & 1h down move, 15m still high
            & ((_cmp_cached_16) | (_cmp_cached_64) | (_cmp_cached_75))
            # 15m & 1d down move, 1h still high
            & ((_cmp_cached_16) | (_cmp_cached_64) | (_cmp_cached_30))
            # 15m & 1d down move, 1h high
            & ((_cmp_cached_16) | (_cmp_cached_118) | (_cmp_cached_52))
            # 15m &1d down move, 1d overbought
            & ((_cmp_cached_16) | (_cmp("RSI_3_1d", ">", 50.0)) | (_cmp_cached_39))
            # 15m down move, 15m still not low enough, 4h overbought
            & ((_cmp_cached_16) | (_cmp_cached_111) | (_cmp_cached_123))
            # 15m down move, 15m still high, 4h high
            & ((_cmp_cached_16) | (_cmp_cached_81) | (_cmp_cached_55))
            # 15m down move, 15m still high, 1h high
            & ((_cmp_cached_16) | (_cmp_cached_46) | (_cmp_cached_71))
            # 15m down move, 15m still high, 4h high
            & ((_cmp_cached_16) | (_cmp_cached_46) | (_cmp_cached_13))
            # 15m down move, 15m still high, 1d overbought
            & ((_cmp_cached_16) | (_cmp_cached_46) | (_cmp_cached_35))
            # 15m down move, 15m high, 4h downtrend
            & ((_cmp_cached_16) | (_cmp_cached_90) | (_cmp_cached_139))
            # 15m down move, 15m high, 4h overbought
            & ((_cmp_cached_16) | (_cmp_cached_90) | (_cmp_cached_27))
            # 15m down move, 15m high, 4h overbought
            & ((_cmp_cached_16) | (_cmp_cached_24) | (_cmp_cached_26))
            # 15m down move, 15m high, 1d downtrend
            & ((_cmp_cached_16) | (_cmp_cached_24) | (_cmp_cached_15))
            # 15m down move, 15m high, 1d overbought
            & ((_cmp_cached_16) | (_cmp_cached_24) | (_cmp_cached_35))
            # 15m down move, 1h high, 4h overbought
            & ((_cmp_cached_16) | (_cmp_cached_18) | (_cmp_cached_26))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_16) | (_cmp_cached_13) | (_cmp_cached_98))
            # 15m down move, 1h high, 4h downtrend
            & ((_cmp_cached_16) | (_cmp_cached_112) | (_cmp_cached_31))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_16) | (_cmp_cached_37) | (_cmp_cached_51))
            # 15m down move, 1h high
            & ((_cmp_cached_16) | (_cmp_cached_83))
            # 15m down move, 4h still high, 1d downtrend
            & ((_cmp_cached_16) | (_cmp_cached_79) | (_cmp_cached_15))
            # 15m down move, 4h high, 1d downtrend
            & ((_cmp_cached_16) | (_cmp_cached_34) | (_cmp_cached_23))
            # 15m down move, 4h & 1d overbought
            & ((_cmp_cached_16) | (_cmp("ROC_9_4h", "<", 25.0)) | (_cmp_cached_29))
            # 15m & 1h down move, 15m high
            & ((_cmp_cached_28) | (_cmp_cached_8) | (_cmp_cached_24))
            # 15m & 4h down move, 15m high
            & ((_cmp_cached_28) | (_cmp_cached_47) | (_cmp("AROONU_14_15m", "<", 75.0)))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_28) | (_cmp_cached_60) | (_cmp_cached_71))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_28) | (_cmp_cached_87) | (_cmp_cached_71))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_28) | (_cmp_cached_87) | (_cmp_cached_20))
            # 15m & 1d down move, 1d high
            & ((_cmp_cached_28) | (_cmp_cached_77) | (_cmp("AROONU_14_1d", "<", 75.0)))
            # 15m & 1d down move, 1d high
            & ((_cmp_cached_28) | (_cmp_cached_107) | (_cmp_cached_38))
            # 15m down move, 15m high, 4h downtrend
            & ((_cmp_cached_28) | (_cmp_cached_24) | (_cmp_cached_31))
            # 15m down move, 15m high, 4h overbought
            & ((_cmp_cached_28) | (_cmp_cached_24) | (_cmp_cached_27))
            # 15m down move, 15m high, 1d overbought
            & ((_cmp_cached_28) | (_cmp_cached_24) | (_cmp_cached_99))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_28) | (_cmp_cached_12) | (_cmp_cached_13))
            # 15m down move, 1h high, 1d downtrend
            & ((_cmp_cached_28) | (_cmp_cached_12) | (_cmp_cached_102))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_28) | (_cmp_cached_52) | (_cmp_cached_39))
            # 15m down move, 4h high, 1d high
            & ((_cmp_cached_28) | (_cmp_cached_68) | (_cmp_cached_62))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_28) | (_cmp_cached_20) | (_cmp_cached_27))
            # 15m down move, 15m still high, 1h still high
            & ((_cmp_cached_28) | (_cmp_cached_75) | (_cmp_cached_49))
            # 15m down move, 1h high, 4h high
            & ((_cmp_cached_28) | (_cmp_cached_56) | (_cmp_cached_14))
            # 15m down move, 4h & 1d overbought
            & ((_cmp_cached_28) | (_cmp_cached_98) | (_cmp_cached_35))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_70) | (_cmp_cached_8) | (_cmp_cached_18))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_70) | (_cmp_cached_8) | (_cmp_cached_40))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_70) | (_cmp_cached_41) | (_cmp_cached_13))
            # 15m down move, 1d high, 15m high
            & ((_cmp_cached_70) | (_cmp("RSI_14_1d", "<", 70.0)) | (_cmp_cached_24))
            # 15m down move, 15m high, 1d downtrend
            & ((_cmp_cached_70) | (_cmp_cached_90) | (_cmp_cached_44))
            # 15m down move, 15m high, 15m downtrend
            & ((_cmp_cached_70) | (_cmp_cached_24) | (_cmp("CMF_20_15m", ">", -0.30)))
            # 15m down move, 15m high, 1d overbought
            & ((_cmp_cached_70) | (_cmp_cached_24) | (_cmp("ROC_9_1d", "<", 70.0)))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_70) | (_cmp_cached_71) | (_cmp_cached_51))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_70) | (_cmp_cached_13) | (_cmp_cached_123))
            # 15m down move, 15m high, 4h overbought
            & ((_cmp_cached_70) | (_cmp_cached_108) | (_cmp("ROC_9_4h", "<", 70.0)))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_70) | (_cmp_cached_83) | (_cmp_cached_35))
            # 15m down move, 15m high, 4h high
            & ((_cmp_cached_100) | (_cmp_cached_90) | (_cmp_cached_55))
            # 15m down move, 15m high, 4h overbought
            & ((_cmp_cached_100) | (_cmp_cached_24) | (_cmp_cached_114))
            # 15m down move, 1h high, 4h overbought
            & ((_cmp_cached_100) | (_cmp_cached_52) | (_cmp_cached_115))
            # 15m down move, 4h high, 1d overbought
            & ((_cmp_cached_100) | (_cmp_cached_20) | (_cmp_cached_74))
            # 15m down move, 1h high, 1d downtrend
            & ((_cmp_cached_100) | (_cmp_cached_83) | (_cmp_cached_95))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_100) | (_cmp_cached_55) | (_cmp_cached_26))
            # 15m down move, 15m high, 1h downtrend
            & ((_cmp_cached_140) | (_cmp_cached_24) | (_cmp_cached_120))
            # 15m down move, 15m & 4h high
            & ((_cmp_cached_140) | (_cmp("AROONU_14_15m", "<", 75.0)) | (_cmp("AROONU_14_4h", "<", 75.0)))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_140) | (_cmp_cached_34) | (_cmp_cached_50))
            # 1h & 4h down move, 15m still high
            & ((_cmp_cached_22) | (_cmp_cached_4) | (_cmp_cached_75))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp_cached_43))
            # 1h down move, 4h still high, 4h downtrend
            & ((_cmp_cached_1) | (_cmp_cached_67) | (_cmp_cached_31))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_1) | (_cmp_cached_13) | (_cmp_cached_26))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_2) | (_cmp_cached_5) | (_cmp("RSI_14_1d", "<", 60.0)))
            # 1h & 4h down move, 15m high
            & ((_cmp_cached_2) | (_cmp_cached_5) | (_cmp_cached_24))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_2) | (_cmp_cached_6) | (_cmp_cached_23))
            # 1h & 1d down move, 1d overbought
            & ((_cmp_cached_2) | (_cmp_cached_133) | (_cmp_cached_78))
            # 1h & 1d down move, 1d overbought
            & ((_cmp_cached_2) | (_cmp("RSI_3_1d", ">", 60.0)) | (_cmp_cached_40))
            # 1h down move, 1h still not low enough, 1d downtrend
            & ((_cmp_cached_2) | (_cmp_cached_109) | (_cmp_cached_23))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_10) | (_cmp_cached_21) | (_cmp_cached_42))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_10) | (_cmp_cached_21) | (_cmp_cached_51))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_10) | (_cmp_cached_20) | (_cmp_cached_29))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_11) | (_cmp_cached_47) | (_cmp_cached_20))
            # 1h & 1d down move, 1d still high
            & ((_cmp_cached_11) | (_cmp_cached_118) | (_cmp_cached_117))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_12) | (_cmp_cached_39))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_11) | (_cmp_cached_42) | (_cmp_cached_39))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_11) | (_cmp_cached_105) | (_cmp_cached_15))
            # 1h down move, 4h downtrend, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_139) | (_cmp_cached_35))
            # 1h down move, 15m & 1h still high
            & ((_cmp_cached_8) | (_cmp_cached_81) | (_cmp_cached_49))
            # 1h down move, 1h still high 1d overbought
            & ((_cmp_cached_8) | (_cmp_cached_49) | (_cmp_cached_74))
            # 1h down move, 1h high, 4h downtrend
            & ((_cmp_cached_8) | (_cmp_cached_88) | (_cmp_cached_31))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_8) | (_cmp_cached_12) | (_cmp_cached_51))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_8) | (_cmp_cached_105) | (_cmp_cached_26))
            # 1h down move, 4h & 1h overbought
            & ((_cmp_cached_8) | (_cmp_cached_50) | (_cmp_cached_40))
            # 1h & 1d down move, 1h high
            & ((_cmp_cached_25) | (_cmp_cached_133) | (_cmp("AROONU_14_1h", "<", 75.0)))
            # 1h down move, 15m still high, 4h  high
            & ((_cmp_cached_25) | (_cmp_cached_81) | (_cmp_cached_20))
            # 1h down move, 15m still high, 4h high
            & ((_cmp_cached_25) | (_cmp_cached_81) | (_cmp_cached_58))
            # 1h down move, 15m still high, 4h high
            & ((_cmp_cached_25) | (_cmp_cached_46) | (_cmp_cached_13))
            # 1h down move, 15m & 1d high
            & ((_cmp_cached_25) | (_cmp_cached_90) | (_cmp_cached_42))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_25) | (_cmp_cached_12) | (_cmp_cached_55))
            # 1h down move, 1h & 1d high
            & ((_cmp_cached_25) | (_cmp_cached_18) | (_cmp_cached_38))
            # 1h down move, 1h downtrend, 4h overbought
            & ((_cmp_cached_25) | (_cmp("CMF_20_1h", ">", -0.30)) | (_cmp_cached_26))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_25) | (_cmp_cached_12) | (_cmp("ROC_9_1d", ">", -80.0)))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_25) | (_cmp_cached_18) | (_cmp_cached_35))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_25) | (_cmp_cached_34) | (_cmp_cached_95))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_33) | (_cmp_cached_60) | (_cmp_cached_56))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_33) | (_cmp_cached_60) | (_cmp_cached_105))
            # 1h down move, 15m still high, 4h downtrend
            & ((_cmp_cached_33) | (_cmp_cached_113) | (_cmp("ROC_9_4h", ">", -15.0)))
            # 1h down move, 15m still high, 1d overbought
            & ((_cmp_cached_33) | (_cmp_cached_46) | (_cmp_cached_35))
            # 1h down move, 15m & 4h high
            & ((_cmp_cached_33) | (_cmp_cached_24) | (_cmp_cached_13))
            # 1h down move, 1h still high, 4h high
            & ((_cmp_cached_33) | (_cmp_cached_49) | (_cmp_cached_34))
            # 1h down move, 1h still high, 1d overbought
            & ((_cmp_cached_33) | (_cmp_cached_49) | (_cmp_cached_29))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_33) | (_cmp_cached_12) | (_cmp_cached_26))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_33) | (_cmp_cached_92) | (_cmp_cached_146))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_33) | (_cmp_cached_52) | (_cmp_cached_14))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_33) | (_cmp_cached_37) | (_cmp("CMF_20_1d", ">", -0.20)))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_33) | (_cmp_cached_27) | (_cmp_cached_35))
            # 1h down move, 15m high, 4h overbought
            & ((_cmp_cached_65) | (_cmp_cached_24) | (_cmp_cached_50))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_65) | (_cmp_cached_71) | (_cmp_cached_26))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_65) | (_cmp_cached_20) | (_cmp_cached_26))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_65) | (_cmp_cached_20) | (_cmp_cached_73))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_65) | (_cmp_cached_9) | (_cmp_cached_51))
            # 1h down move, 1h still high, 1d overbought
            & ((_cmp_cached_65) | (_cmp_cached_82) | (_cmp_cached_74))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_65) | (_cmp_cached_84) | (_cmp_cached_78))
            # 1h down move, 15m & 1h high
            & ((_cmp_cached_63) | (_cmp_cached_24) | (_cmp_cached_71))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_63) | (_cmp_cached_18) | (_cmp_cached_27))
            # 1h down move, 4h still high, 1d overbought
            & ((_cmp_cached_63) | (_cmp_cached_43) | (_cmp_cached_74))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_63) | (_cmp_cached_14) | (_cmp_cached_98))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_63) | (_cmp_cached_37) | (_cmp_cached_14))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_63) | (_cmp_cached_58) | (_cmp_cached_27))
            # 1h down move, 1h high, 1d high
            & ((_cmp_cached_130) | (_cmp_cached_56) | (_cmp_cached_9))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_130) | (_cmp_cached_37) | (_cmp_cached_23))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_130) | (_cmp_cached_34) | (_cmp_cached_115))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_97) | (_cmp_cached_37) | (_cmp_cached_29))
            # 1h down move, 15m & 1h high
            & ((_cmp("RSI_3_1h", ">", 65.0)) | (_cmp_cached_24) | (_cmp_cached_71))
            # 1h down move, 1h high & overbought
            & ((_cmp("RSI_3_1h", ">", 65.0)) | (_cmp_cached_37) | (_cmp_cached_61))
            # 4h down move, 1h still high, 1d downtrend
            & ((_cmp_cached_80) | (_cmp_cached_82) | (_cmp_cached_23))
            # 4h down move, 1h still high, 4h downtrend
            & ((_cmp_cached_80) | (_cmp_cached_30) | (_cmp_cached_72))
            # 4h down move, 4h & 1d downtrend
            & ((_cmp_cached_80) | (_cmp_cached_31) | (_cmp_cached_15))
            # 4h down move, 15m high, 1h still high
            & ((_cmp_cached_57) | (_cmp_cached_24) | (_cmp_cached_30))
            # 4h down move, 15m high
            & ((_cmp_cached_57) | (_cmp_cached_108))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_57) | (_cmp_cached_79) | (_cmp_cached_15))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_4) | (_cmp_cached_53) | (_cmp_cached_117))
            # 4h & 1d down move, 1d downtrend
            & ((_cmp_cached_4) | (_cmp_cached_53) | (_cmp_cached_15))
            # 4h & 1d down move, 4h still high
            & ((_cmp_cached_4) | (_cmp_cached_77) | (_cmp_cached_54))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_4) | (_cmp_cached_133) | (_cmp("STOCHRSIk_14_14_3_3_1d", "<", 40.0)))
            # 4h down move, 15m still not low enough, 1d downtrend
            & ((_cmp_cached_4) | (_cmp_cached_125) | (_cmp_cached_44))
            # 4h down move, 15m high, 4h downtrend
            & ((_cmp_cached_4) | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 60.0)) | (_cmp("ROC_9_4h", ">", -50.0)))
            # 4h down move, 15m high
            & ((_cmp_cached_4) | (_cmp_cached_108))
            # 4h & 1d down move, 15m high
            & ((_cmp_cached_5) | (_cmp_cached_133) | (_cmp_cached_108))
            # 4h & 1d down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_133) | (_cmp_cached_58))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_118) | (_cmp_cached_45))
            # 4h down move, 15m still high, 1h high
            & ((_cmp_cached_5) | (_cmp_cached_46) | (_cmp_cached_112))
            # 4h down move, 15m & 1d high
            & ((_cmp_cached_5) | (_cmp_cached_24) | (_cmp_cached_42))
            # 4h down move, 15m high
            & ((_cmp_cached_5) | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 80.0)))
            # 4h down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_84))
            # 4h down move, 1h & 4h downtrend
            & ((_cmp_cached_5) | (_cmp_cached_124) | (_cmp_cached_72))
            # 4h & 1d down move, 1h still high
            & ((_cmp_cached_6) | (_cmp_cached_53) | (_cmp_cached_86))
            # 4h & 1d down move, 15m high
            & ((_cmp_cached_6) | (_cmp_cached_64) | (_cmp_cached_108))
            # 4h & 1d down move, 1d overbought
            & ((_cmp_cached_6) | (_cmp("RSI_3_1d", ">", 55.0)) | (_cmp_cached_35))
            # 4h down move, 15m & 4h still high
            & ((_cmp_cached_6) | (_cmp_cached_46) | (_cmp_cached_43))
            # 4h down move, 15m high, 1d high
            & ((_cmp_cached_6) | (_cmp_cached_24) | (_cmp_cached_106))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_6) | (_cmp_cached_43) | (_cmp_cached_44))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_6) | (_cmp_cached_38) | (_cmp_cached_78))
            # 4h down move, 15m high, 4h downtrend
            & ((_cmp_cached_6) | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 80.0)) | (_cmp("ROC_9_4h", ">", -50.0)))
            # 4h down move, 1h high, 1d downtrend
            & ((_cmp_cached_6) | (_cmp_cached_112) | (_cmp_cached_44))
            # 4h down move, 4h still not low enough, 4h downtrend
            & ((_cmp_cached_6) | (_cmp_cached_94) | (_cmp_cached_102))
            # 4h down move, 4h high, 1d downtrend
            & ((_cmp_cached_6) | (_cmp_cached_105) | (_cmp_cached_146))
            # 4h & 1d down move, 1d overbought
            & ((_cmp_cached_21) | (_cmp_cached_118) | (_cmp_cached_51))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_21) | (_cmp_cached_107) | (_cmp_cached_42))
            # 4h down move, 15m still high, 1h high
            & ((_cmp_cached_21) | (_cmp_cached_46) | (_cmp_cached_71))
            # 4h down move, 15m & 4h still high
            & ((_cmp_cached_21) | (_cmp_cached_46) | (_cmp_cached_43))
            # 4h down move, 15m high, 1d overbought
            & ((_cmp_cached_21) | (_cmp_cached_24) | (_cmp_cached_29))
            # 4h down move, 1h high, 1d overbought
            & ((_cmp_cached_21) | (_cmp_cached_52) | (_cmp_cached_35))
            # 4h down move, 4h & 1d high
            & ((_cmp_cached_21) | (_cmp_cached_68) | (_cmp_cached_9))
            # 4h down move, 4h high, 1d downtrend
            & ((_cmp_cached_21) | (_cmp_cached_68) | (_cmp_cached_150))
            # 4h down move, 4h high, 1d downtrend
            & ((_cmp_cached_21) | (_cmp_cached_13) | (_cmp_cached_15))
            # 4h down move, 4h high, 1d overbought
            & ((_cmp_cached_21) | (_cmp_cached_13) | (_cmp_cached_40))
            # 4h down move, 1h still high, 1d overbought
            & ((_cmp_cached_21) | (_cmp_cached_30) | (_cmp_cached_29))
            # 4h down move, 4h high, 1d downtrend
            & ((_cmp_cached_21) | (_cmp_cached_34) | (_cmp_cached_95))
            # 4h down move, 1h high, 1h downtrend
            & ((_cmp_cached_19) | (_cmp_cached_12) | (_cmp("ROC_9_1h", ">", -10.0)))
            # 4h & 1d down move, 1d overbought
            & ((_cmp_cached_19) | (_cmp("RSI_3_1d", ">", 50.0)) | (_cmp_cached_29))
            # 4h down move, 1d downtrend, 1d overbought
            & ((_cmp_cached_19) | (_cmp("CMF_20_1d", ">", -0.30)) | (_cmp_cached_40))
            # 4h down move, 15m high, 4h high
            & ((_cmp_cached_19) | (_cmp_cached_90) | (_cmp_cached_32))
            # 4h down move, 1h high, 1d downtrend
            & ((_cmp_cached_19) | (_cmp_cached_52) | (_cmp_cached_15))
            # 4h down move, 1h high, 1d downtrend
            & ((_cmp_cached_19) | (_cmp_cached_37) | (_cmp_cached_44))
            # 4h down move, 1h high, 1d overbought
            & ((_cmp_cached_19) | (_cmp_cached_83) | (_cmp_cached_35))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_19) | (_cmp_cached_84) | (_cmp_cached_78))
            # 4h down move, 15m still high, 1h high
            & ((_cmp_cached_41) | (_cmp_cached_81) | (_cmp_cached_83))
            # 4h down move, 15m still high, 4h high
            & ((_cmp_cached_41) | (_cmp_cached_46) | (_cmp_cached_20))
            # 4h down move, 15m high, 1h high
            & ((_cmp_cached_41) | (_cmp_cached_24) | (_cmp_cached_56))
            # 4h down move, 4h & 1d high
            & ((_cmp_cached_41) | (_cmp_cached_20) | (_cmp_cached_9))
            # 4h down move, 1d high, 1d downtrend
            & ((_cmp_cached_41) | (_cmp("STOCHRSIk_14_14_3_3_1d", "<", 60.0)) | (_cmp_cached_23))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_41) | (_cmp_cached_62) | (_cmp_cached_40))
            # 4h down move, 15m still high, 1d overbought
            & ((_cmp_cached_47) | (_cmp_cached_46) | (_cmp_cached_35))
            # 4h down move, 15m high, 1d overbought
            & ((_cmp_cached_47) | (_cmp_cached_24) | (_cmp_cached_74))
            # 4h down move, 1h & 4h high
            & ((_cmp_cached_47) | (_cmp_cached_12) | (_cmp_cached_20))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_47) | (_cmp_cached_9) | (_cmp_cached_39))
            # 4h down move, 15m high, 1h high
            & ((_cmp_cached_47) | (_cmp_cached_108) | (_cmp_cached_71))
            # 4h down move, 1h high, 1d overbought
            & ((_cmp_cached_47) | (_cmp_cached_56) | (_cmp_cached_99))
            # 4h down move, 4h & 1d overbought
            & ((_cmp_cached_47) | (_cmp_cached_27) | (_cmp_cached_51))
            # 4h down move, 15m still high, 4h high
            & ((_cmp_cached_76) | (_cmp_cached_81) | (_cmp_cached_32))
            # 45 down move, 15m high, 1h high
            & ((_cmp_cached_76) | (_cmp_cached_24) | (_cmp_cached_56))
            # 4h down move, 15m high, 4h high
            & ((_cmp_cached_76) | (_cmp_cached_24) | (_cmp_cached_58))
            # 4h down move, 4h high, 1d overbought
            & ((_cmp_cached_76) | (_cmp_cached_68) | (_cmp_cached_29))
            # 4h down move, 4h high & overbought
            & ((_cmp_cached_76) | (_cmp_cached_20) | (_cmp_cached_50))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_76) | (_cmp_cached_45) | (_cmp_cached_51))
            # 4h down move, 1d high, 1d downtrend
            & ((_cmp_cached_76) | (_cmp_cached_42) | (_cmp_cached_141))
            # 4h down move, 1d high, 4h overbought
            & ((_cmp_cached_76) | (_cmp_cached_38) | (_cmp_cached_27))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_76) | (_cmp_cached_62) | (_cmp_cached_39))
            # 4h down move, 4h & 1d overbought
            & ((_cmp_cached_76) | (_cmp_cached_50) | (_cmp_cached_74))
            # 4h down move, 15m & 1h high
            & ((_cmp_cached_60) | (_cmp_cached_24) | (_cmp_cached_71))
            # 4h down move, 4h still high, 1h high
            & ((_cmp_cached_60) | (_cmp_cached_67) | (_cmp_cached_56))
            # 4h down move, 4h high, 1d overbought
            & ((_cmp_cached_60) | (_cmp_cached_13) | (_cmp_cached_40))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_60) | (_cmp_cached_103) | (_cmp_cached_69))
            # 4h down move, 1d high, 4h overbought
            & ((_cmp_cached_60) | (_cmp_cached_38) | (_cmp_cached_27))
            # 4h down move, 4h high, 1d downtrend
            & ((_cmp_cached_60) | (_cmp_cached_105) | (_cmp_cached_15))
            # 4h down move, 4h downtrend, 1d overbought
            & ((_cmp_cached_60) | (_cmp_cached_31) | (_cmp_cached_39))
            # 4h down move, 1h high, 4h overbought
            & ((_cmp_cached_131) | (_cmp_cached_71) | (_cmp_cached_26))
            # 4h down move, 4h high & overbought
            & ((_cmp_cached_131) | (_cmp_cached_13) | (_cmp_cached_26))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_131) | (_cmp_cached_38) | (_cmp_cached_99))
            # 4h down move, 4h high & overbought
            & ((_cmp_cached_131) | (_cmp_cached_34) | (_cmp_cached_27))
            # 4h down move, 15m high, 1h high
            & ((_cmp_cached_87) | (_cmp_cached_90) | (_cmp_cached_83))
            # 4h down move, 4h high & overbought
            & ((_cmp_cached_87) | (_cmp_cached_13) | (_cmp_cached_50))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_87) | (_cmp_cached_54) | (_cmp_cached_23))
            # 4h down move, 4h & 1d overbought
            & ((_cmp_cached_87) | (_cmp_cached_50) | (_cmp_cached_35))
            # 4h down move, 15m high, 4h high
            & ((_cmp("RSI_3_4h", ">", 65.0)) | (_cmp_cached_24) | (_cmp_cached_32))
            # 4h down move, 4h high & overbought
            & ((_cmp("RSI_3_4h", ">", 65.0)) | (_cmp_cached_20) | (_cmp_cached_27))
            # 1d down move, 4h & 1d downtrend
            & ((_cmp("RSI_3_1d", ">", 3.0)) | (_cmp_cached_139) | (_cmp_cached_95))
            # 1d down move, 15m still high, 4h high
            & ((_cmp_cached_66) | (_cmp_cached_24) | (_cmp_cached_34))
            # 1d down move, 4h & 1d downtrend
            & ((_cmp_cached_66) | (_cmp_cached_31) | (_cmp_cached_146))
            # 1d down move, 4h & 1d downtrend
            & ((_cmp_cached_66) | (_cmp_cached_72) | (_cmp_cached_95))
            # 1d down move, 1h high, 1d downtrend
            & ((_cmp_cached_59) | (_cmp_cached_92) | (_cmp_cached_23))
            # 1d down move, 4h & 1d downtrend
            & ((_cmp_cached_59) | (_cmp_cached_102) | (_cmp_cached_44))
            # 1d down move, 15m high, 1h high
            & ((_cmp_cached_53) | (_cmp_cached_90) | (_cmp_cached_37))
            # 1d down move, 15m high, 1h high
            & ((_cmp_cached_53) | (_cmp_cached_24) | (_cmp_cached_71))
            # 1d down move, 4h high, 4h downtrend
            & ((_cmp_cached_53) | (_cmp_cached_58) | (_cmp_cached_31))
            # 1d down move, 15m high, 4h high
            & ((_cmp_cached_64) | (_cmp_cached_24) | (_cmp_cached_34))
            # 1d down move, 15m high, 4h downtrend
            & ((_cmp_cached_64) | (_cmp_cached_24) | (_cmp_cached_72))
            # 1d down move, 1h & 1d high
            & ((_cmp_cached_64) | (_cmp_cached_18) | (_cmp_cached_42))
            # 1d down move, 1d still high, 1d downtrend
            & ((_cmp_cached_64) | (_cmp_cached_117) | (_cmp_cached_15))
            # 1d down move, 1d high & overbought
            & ((_cmp_cached_77) | (_cmp("AROONU_14_1d", "<", 60.0)) | (_cmp_cached_78))
            # 1d down move, 1h high, 1d downtrend
            & ((_cmp_cached_77) | (_cmp_cached_56) | (_cmp_cached_39))
            # 1d down move, 1h & 1d high
            & ((_cmp_cached_133) | (_cmp_cached_12) | (_cmp_cached_38))
            # 1d down move, 1h high, 1d overbought
            & ((_cmp_cached_118) | (_cmp_cached_52) | (_cmp_cached_69))
            # 1d down move, 1d high & overbought
            & ((_cmp_cached_118) | (_cmp_cached_9) | (_cmp_cached_51))
            # 1d down move, 1d high & overbought
            & ((_cmp_cached_118) | (_cmp_cached_42) | (_cmp_cached_78))
            # 1d down move, 1h high, 1d overbought
            & ((_cmp_cached_118) | (_cmp_cached_56) | (_cmp_cached_35))
            # 15m still high, 4h high, 1d overbought
            & ((_cmp_cached_46) | (_cmp("RSI_14_4h", "<", 60.0)) | (_cmp("ROC_9_1d", "<", 70.0)))
            # 15m still high, 1h downtrend, 4h overbought
            & ((_cmp_cached_46) | (_cmp("ROC_9_1h", ">", -10.0)) | (_cmp_cached_73))
            # 15m high, 4h high & overbought
            & ((_cmp_cached_90) | (_cmp_cached_13) | (_cmp_cached_26))
            # 15m & 4h high, 1d overbought
            & ((_cmp_cached_90) | (_cmp_cached_13) | (_cmp_cached_78))
            # 15m high, 15m & 4h overbought
            & ((_cmp_cached_90) | (_cmp("ROC_9_15m", "<", 10.0)) | (_cmp_cached_26))
            # 15m high, 4h downtrend
            & ((_cmp_cached_90) | (_cmp_cached_72))
            # 15m & 1h & 4h high
            & ((_cmp_cached_24) | (_cmp_cached_71) | (_cmp_cached_14))
            # 15m & 4h & 1d high
            & ((_cmp_cached_24) | (_cmp_cached_13) | (_cmp_cached_38))
            # 15m & 4h high, 4h overbought
            & ((_cmp_cached_24) | (_cmp_cached_13) | (_cmp_cached_27))
            # 15m & 4h high, 1d downtrend
            & ((_cmp_cached_24) | (_cmp_cached_13) | (_cmp_cached_15))
            # 15m & 1d high, 1d overbought
            & ((_cmp_cached_24) | (_cmp_cached_38) | (_cmp_cached_29))
            # 15m high, 4h downtrend, 1d overbought
            & ((_cmp_cached_24) | (_cmp_cached_72) | (_cmp_cached_74))
            # 4h down move, 1h still high, 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_86) | (_cmp_cached_95))
            # 1h & 4h high, 4h overbought
            & ((_cmp_cached_18) | (_cmp_cached_14) | (_cmp_cached_27))
            # 1h high, 1d high & overbought
            & ((_cmp_cached_52) | (_cmp_cached_9) | (_cmp_cached_51))
            # 1h high, 4h downtrend
            & ((_cmp_cached_52) | (_cmp_cached_31))
            # 1h high, 4h & 1d overbought
            & ((_cmp_cached_52) | (_cmp_cached_27) | (_cmp_cached_39))
            # 4h & 1d high, 4h overbought
            & ((_cmp_cached_20) | (_cmp_cached_9) | (_cmp_cached_27))
            # 4h & 1d high, 1d downtrend
            & ((_cmp_cached_20) | (_cmp_cached_9) | (_cmp_cached_15))
            # 1d high, 4h & 1d downtrend
            & ((_cmp_cached_42) | (_cmp_cached_31) | (_cmp_cached_15))
            # 1d high, 1h & 4h downtrend
            & ((_cmp_cached_103) | (_cmp_cached_124) | (_cmp("ROC_9_4h", ">", -50.0)))
            # 1d high, 4h downtrend
            & ((_cmp_cached_103) | (_cmp_cached_72))
            # 1d high, 4h downtrend, 1d overbought
            & ((_cmp_cached_103) | (_cmp_cached_72) | (_cmp("ROC_9_1d", "<", 70.0)))
            # 1d high, 4h & 1d overbought
            & ((_cmp_cached_9) | (_cmp_cached_50) | (_cmp_cached_40))
            # 15m & 1h high, 1d overbought
            & (
              (_cmp_cached_108) | (_cmp_cached_56) | (_cmp_cached_35)
            )
            # 15m & 1d high
            & ((_cmp("STOCHRSIk_14_14_3_3_15m", "<", 90.0)) | (_cmp_cached_62))
            # 1h high, 4h & 1d downtrend
            & ((_cmp_cached_112) | (_cmp_cached_72) | (_cmp_cached_23))
            # 1h high, 4h downtrend
            & ((_cmp_cached_56) | (_cmp_cached_72))
            # 1h high, 1d downtrend
            & ((_cmp_cached_56) | (_cmp_cached_15))
            # 4h high, 4h overbought, 1d downtrend
            & ((_cmp_cached_55) | (_cmp_cached_26) | (_cmp_cached_15))
            # 1d still high, 4h & 1d downtrend
            & ((_cmp_cached_117) | (_cmp_cached_72) | (_cmp_cached_23))
            # 1d P&D, 4h downtrend
            & ((_cmp("change_pct_1d", ">", -50.0)) | (df["change_pct_1d"].shift(288) < 50.0) | (_cmp_cached_5))
            # 1d P&D, 15m high
            & ((_cmp("change_pct_1d", ">", -20.0)) | (df["change_pct_1d"].shift(288) < 20.0) | (_cmp_cached_24))
            # 1d red with top wick, 4h high
            & ((_cmp("change_pct_1d", ">", -20.0)) | (_cmp("top_wick_pct_1d", "<", 20.0)) | (_cmp_cached_20))
            # 1d red, previous 1d top wick, 15m high
            & (
              (_cmp("change_pct_1d", ">", -10.0)) | (df["top_wick_pct_1d"].shift(288) < 40.0) | (_cmp_cached_24)
            )
            # 1d green with top wick, 4h overbought
            & ((_cmp("change_pct_1d", "<", 15.0)) | (_cmp("top_wick_pct_1d", "<", 15.0)) | (_cmp_cached_26))
            # 1d green, 15m down move, 1h high
            & ((_cmp("change_pct_1d", "<", 50.0)) | (_cmp_cached_28) | (_cmp_cached_12))
            # 1d green, 4h down move, 4h still high
            & ((_cmp("change_pct_1d", "<", 40.0)) | (_cmp_cached_41) | (_cmp_cached_67))
            # 1d top wick, 4h down move, 1d overbought
            & ((_cmp("top_wick_pct_1d", "<", 50.0)) | (_cmp_cached_41) | (_cmp_cached_99))
            # big drop in the last 20 days, 1d high, 1d downtrend
            & (
              _gt_mul("close", "high_max_20_1d", 0.20)
              | (_cmp_cached_106)
              | (_cmp_cached_141)
            )
          )

          # Logic
          long_entry_logic.append(
            _rsi_20_falling
            & (_cmp("RSI_4", "<", 45.0))
            & (_cmp("RSI_14", ">", 30.0))
            & (_cmp("AROONU_14", "<", 20.0))
            & (_cmp("STOCHRSIk_14_14_3_3", "<", 20.0))
            & (df["close"] < df["SMA_16"] * 0.965)
            & (df["close"] < df["SMA_16_1h"] * 0.985)
          )

        # Condition #4 - Normal mode (Long).
        if long_entry_condition_index == 4:
          # Protections
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          long_entry_logic.append(df["protections_long_global"] == True)

          long_entry_logic.append(
            (_cmp_cached_7)
            # 5m & 1h down move, 1d still high
            & ((_cmp_cached_48) | (_cmp_cached_36) | (_cmp_cached_135))
            # 5m & 1h & 4h down move
            & ((_cmp_cached_48) | (_cmp_cached_22) | (_cmp_cached_4))
            # 5m & 1h down move, 1h still not low enough
            & ((_cmp_cached_48) | (_cmp_cached_1) | (_cmp_cached_138))
            # 5m & 1h down move, 1d high
            & ((_cmp_cached_48) | (_cmp_cached_2) | (_cmp_cached_42))
            # 5m & 1h down move, 1d high
            & ((_cmp_cached_48) | (_cmp_cached_10) | (_cmp_cached_9))
            # 5m & 1h down move, 1h high
            & ((_cmp_cached_48) | (_cmp_cached_63) | (_cmp_cached_12))
            # 5m & 1h down move, 1h still high
            & ((_cmp_cached_48) | (_cmp_cached_8) | (_cmp_cached_30))
            # 5m & 1h down move, 1d downtrend
            & ((_cmp_cached_48) | (_cmp_cached_5) | (_cmp_cached_23))
            # 5m & 4h down move, 4h high
            & ((_cmp_cached_48) | (_cmp_cached_21) | (_cmp_cached_13))
            # 5m & 1d down move, 15m still high
            & ((_cmp_cached_48) | (_cmp_cached_53) | (_cmp_cached_113))
            # 5m & 4h down move, 15m still high
            & ((_cmp_cached_104) | (_cmp_cached_21) | (_cmp_cached_75))
            # 5m down move, 4h high, 1h overbought
            & ((_cmp_cached_143) | (_cmp_cached_14) | (_cmp_cached_129))
            # 15m & 1h down move, 1d still high
            & ((_cmp_cached_17) | (_cmp_cached_22) | (_cmp_cached_135))
            # 15m & 1h down move, 1d still high
            & ((_cmp_cached_17) | (_cmp_cached_1) | (_cmp_cached_121))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_17) | (_cmp_cached_8) | (_cmp_cached_82))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_17) | (_cmp_cached_33) | (_cmp_cached_58))
            # 15m & 4h down move, 1d overbought
            & ((_cmp_cached_17) | (_cmp_cached_5) | (_cmp("ROC_9_1d", "<", 70.0)))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_17) | (_cmp_cached_19) | (_cmp_cached_9))
            # 15m & 1h down move, 15m stil high
            & ((_cmp_cached_0) | (_cmp_cached_1) | (_cmp_cached_75))
            # 15m & 1h down move, 4h downtrend
            & ((_cmp_cached_0) | (_cmp_cached_1) | (_cmp_cached_139))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_0) | (_cmp_cached_2) | (_cmp_cached_30))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_2) | (_cmp_cached_13))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_10) | (_cmp_cached_40))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_0) | (_cmp_cached_11) | (_cmp_cached_18))
            # 15m down move, 4h high, 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_13) | (_cmp_cached_29))
            # 15m down move, 4h & 1d high
            & ((_cmp_cached_0) | (_cmp_cached_32) | (_cmp_cached_9))
            # 15m down move, 1h high, 1d downtrend
            & ((_cmp_cached_0) | (_cmp_cached_56) | (_cmp_cached_95))
            # 15m down move, 1h high
            & ((_cmp_cached_0) | (_cmp_cached_37))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_3) | (_cmp_cached_11) | (_cmp_cached_82))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_3) | (_cmp_cached_5) | (_cmp_cached_84))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_3) | (_cmp_cached_13) | (_cmp_cached_26))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_3) | (_cmp_cached_55) | (_cmp_cached_27))
            # 15m down move, 4h & 1d downtrend
            & ((_cmp_cached_3) | (_cmp_cached_102) | (_cmp_cached_44))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_16) | (_cmp_cached_10) | (_cmp_cached_12))
            # 15m down move, 4h high, 1d overbought
            & ((_cmp_cached_16) | (_cmp_cached_32) | (_cmp_cached_29))
            # 15m down move, 4h high, 1h overbought
            & ((_cmp_cached_16) | (_cmp_cached_14) | (_cmp_cached_129))
            # 15m down move, 1h high & overbought
            & ((_cmp_cached_16) | (_cmp_cached_83) | (_cmp_cached_61))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_28) | (_cmp_cached_60) | (_cmp_cached_34))
            # 15m down move, 4h high, 4h overbought
            & ((_cmp_cached_28) | (_cmp_cached_68) | (_cmp_cached_98))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_70) | (_cmp_cached_33) | (_cmp_cached_93))
            # 15m & 1h down move, 4h overbought
            & ((_cmp_cached_140) | (_cmp_cached_63) | (_cmp_cached_98))
            # 1h & 4h down move, 15m downtrend
            & ((_cmp_cached_36) | (_cmp_cached_80) | (_cmp("ROC_9_15m", ">", -30.0)))
            # 1h & 4h down move, 15m downtrend
            & ((_cmp_cached_36) | (_cmp_cached_4) | (_cmp("CMF_20_15m", ">", -0.40)))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_36) | (_cmp_cached_6) | (_cmp_cached_106))
            # 1h down move, 1h high, 4h high
            & ((_cmp_cached_36) | (_cmp_cached_12) | (_cmp_cached_34))
            # 1h down move, 15m still high
            & ((_cmp_cached_36) | (_cmp_cached_75))
            # 1h down move, 1h still high, 4h overbought
            & ((_cmp_cached_36) | (_cmp_cached_30) | (_cmp_cached_26))
            # 1h & 4h & 1d down move
            & ((_cmp_cached_22) | (_cmp_cached_57) | (_cmp_cached_66))
            # 1h & 4h down move, 1h downtrend
            & ((_cmp_cached_22) | (_cmp_cached_57) | (_cmp_cached_120))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_22) | (_cmp_cached_4) | (_cmp_cached_44))
            # 1h down move, 4h high, 1h downtrend
            & ((_cmp_cached_22) | (_cmp_cached_58) | (_cmp("ROC_9_1h", ">", -40.0)))
            # 1h down move, 4h high, 1h downtrend
            & ((_cmp_cached_22) | (_cmp_cached_58) | (_cmp("CMF_20_1h", ">", -0.40)))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_22) | (_cmp_cached_62) | (_cmp_cached_39))
            # 1h down move, 1d overbought
            & ((_cmp_cached_22) | (_cmp_cached_29))
            # 1h & 4h & 1d down move
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp_cached_59))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_1) | (_cmp_cached_5) | (_cmp_cached_110))
            # 1h & 4h down move, 1h downtrend
            & ((_cmp_cached_1) | (_cmp_cached_5) | (_cmp_cached_120))
            # 1h & 4h down move, 1h still high
            & ((_cmp_cached_1) | (_cmp_cached_6) | (_cmp_cached_49))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_1) | (_cmp_cached_41) | (_cmp_cached_110))
            # 1h & 3h down move, 1d high
            & ((_cmp_cached_1) | (_cmp_cached_47) | (_cmp_cached_42))
            # 1h & 1d down move, 1d high
            & ((_cmp_cached_1) | (_cmp_cached_107) | (_cmp_cached_45))
            # 1h down move, 4h high
            & ((_cmp_cached_1) | (_cmp_cached_93))
            # 1h down move, 1d high, 15m downtrend
            & ((_cmp_cached_1) | (_cmp_cached_45) | (_cmp("ROC_9_15m", ">", -50.0)))
            # 1h down move, 4h & 1d downtrend
            & ((_cmp_cached_1) | (_cmp("ROC_9_4h", ">", -15.0)) | (_cmp_cached_23))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_2) | (_cmp_cached_5) | (_cmp_cached_110))
            # 1h & 4h down move, 1h still not low enough
            & ((_cmp_cached_2) | (_cmp_cached_5) | (_cmp("AROONU_14_1h", "<", 20.0)))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_2) | (_cmp_cached_21) | (_cmp_cached_94))
            # 1h & 1d down move, 1d still high
            & ((_cmp_cached_2) | (_cmp_cached_53) | (_cmp("STOCHRSIk_14_14_3_3_1d", "<", 40.0)))
            # 1h & 1d down move, 1d high
            & ((_cmp_cached_2) | (_cmp_cached_64) | (_cmp_cached_42))
            # 1h down move, 1h still high, 4h downtrend
            & ((_cmp_cached_2) | (_cmp_cached_86) | (_cmp_cached_72))
            # 1h down move, 1d high, 4h downtrend
            & ((_cmp_cached_2) | (_cmp_cached_38) | (_cmp_cached_31))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_2) | (_cmp_cached_62) | (_cmp_cached_40))
            # 1h down move, 1h still high, 4h downtrend
            & ((_cmp_cached_10) | (_cmp_cached_49) | (_cmp("ROC_9_4h", ">", -50.0)))
            # 1h down move, 1h high
            & ((_cmp_cached_10) | (_cmp_cached_18))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_21) | (_cmp_cached_39))
            # 1h down move, 1h still high, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_30) | (_cmp_cached_40))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_8) | (_cmp_cached_12) | (_cmp_cached_13))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_8) | (_cmp_cached_20) | (_cmp_cached_51))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_8) | (_cmp_cached_42) | (_cmp_cached_74))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_8) | (_cmp_cached_19) | (_cmp_cached_40))
            # 1h & 4h down move, 15m high
            & ((_cmp_cached_8) | (_cmp_cached_47) | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 80.0)))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_8) | (_cmp_cached_60) | (_cmp_cached_56))
            # 1h down move, 15m still high, 1h high
            & ((_cmp_cached_8) | (_cmp_cached_113) | (_cmp_cached_88))
            # 1h down move, 1h still high, 4h high
            & ((_cmp_cached_8) | (_cmp_cached_82) | (_cmp_cached_58))
            # 1h down move, 4h & 1d downtrend
            & ((_cmp_cached_8) | (_cmp("ROC_9_4h", ">", -25.0)) | (_cmp_cached_146))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_8) | (_cmp_cached_26) | (_cmp_cached_29))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_25) | (_cmp_cached_12) | (_cmp_cached_39))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_25) | (_cmp_cached_93) | (_cmp_cached_29))
            # 1h down move, 1h still high, 1d overbought
            & ((_cmp_cached_25) | (_cmp_cached_30) | (_cmp_cached_74))
            # 1h down move, 1h high, 4h downtrend
            & ((_cmp_cached_25) | (_cmp_cached_56) | (_cmp_cached_31))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_65) | (_cmp_cached_12) | (_cmp_cached_14))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_63) | (_cmp_cached_105) | (_cmp_cached_146))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_63) | (_cmp_cached_55) | (_cmp_cached_73))
            # 1h down move, 1h high & overbought
            & ((_cmp_cached_130) | (_cmp_cached_37) | (_cmp_cached_61))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_97) | (_cmp_cached_50) | (_cmp_cached_99))
            # 4h down move, 4h high, 4h downtrend
            & ((_cmp_cached_80) | (_cmp_cached_43) | (_cmp_cached_139))
            # 4h & 1d down move, 1h still not low enough
            & ((_cmp_cached_57) | (_cmp_cached_66) | (_cmp_cached_109))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_57) | (_cmp_cached_107) | (_cmp_cached_45))
            # 4h down move, 4h & 1d downtrend
            & ((_cmp_cached_57) | (_cmp("ROC_9_4h", ">", -15.0)) | (_cmp_cached_15))
            # 4h & 1d down move, 1h still high
            & ((_cmp_cached_4) | (_cmp_cached_66) | (_cmp_cached_86))
            # 4h & 1d down move, 1h high
            & ((_cmp_cached_4) | (_cmp_cached_59) | (_cmp_cached_56))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_4) | (_cmp_cached_64) | (_cmp_cached_135))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_4) | (_cmp_cached_64) | (_cmp_cached_117))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_53) | (_cmp("AROONU_14_1d", "<", 60.0)))
            # 4h & 1d down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_64) | (_cmp_cached_13))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_5) | (_cmp_cached_38) | (_cmp_cached_39))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_6) | (_cmp_cached_43) | (_cmp_cached_142))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_6) | (_cmp_cached_42) | (_cmp_cached_69))
            # 4h down move, 4h & 1d downtrend
            & ((_cmp_cached_6) | (_cmp_cached_31) | (_cmp_cached_23))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_19) | (_cmp_cached_43) | (_cmp_cached_44))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_47) | (_cmp_cached_62) | (_cmp_cached_74))
            # 4h down move, 4h high, 1d downtrend
            & ((_cmp_cached_76) | (_cmp_cached_13) | (_cmp_cached_23))
            # 4h down move, 4h high & overbought
            & ((_cmp_cached_87) | (_cmp_cached_13) | (_cmp_cached_27))
            # 4h down move, 4h & 1d overbought
            & ((_cmp_cached_87) | (_cmp_cached_26) | (_cmp_cached_39))
            # 1h still high, 4h & 1d downtrend
            & ((_cmp_cached_86) | (_cmp_cached_31) | (_cmp_cached_44))
            # 1h & 4h high, 1h overbought
            & ((_cmp_cached_12) | (_cmp_cached_14) | (_cmp("ROC_9_1h", "<", 80.0)))
            # 1h high, 1d overbought
            & ((_cmp_cached_12) | (_cmp("ROC_9_1d", "<", 70.0)))
            # 1h & 4h high, 1h overbought
            & ((_cmp_cached_18) | (_cmp_cached_32) | (_cmp_cached_129))
            # 1h & 1d high, 1h overbought
            & ((_cmp_cached_18) | (_cmp_cached_38) | (_cmp_cached_129))
            # 4h still not low enough, 4h & 1d downtrend
            & ((_cmp_cached_145) | (_cmp_cached_139) | (_cmp_cached_44))
            # 4h still high, 5m downtrend
            & ((_cmp_cached_67) | (_cmp("ROC_9", ">", -40.0)))
            # 4h high, 4h & 1d overbought
            & ((_cmp_cached_68) | (_cmp_cached_50) | (_cmp_cached_35))
            # 4h & 1d high, 4h overbought
            & ((_cmp_cached_20) | (_cmp_cached_9) | (_cmp_cached_98))
            # 4h high, 1h & 1d overbought
            & ((_cmp_cached_14) | (_cmp_cached_129) | (_cmp_cached_29))
            # 4h high, 1h & 4h high
            & ((_cmp_cached_14) | (_cmp("ROC_9_1h", "<", 50.0)) | (_cmp_cached_115))
            # 1d high, 4h & 1d downtrend
            & ((_cmp_cached_45) | (_cmp_cached_139) | (_cmp_cached_44))
            # 1d high, 1h & 1d overbought
            & ((_cmp_cached_42) | (_cmp_cached_129) | (_cmp_cached_74))
            # 1d high, 4h & 1d overbought
            & ((_cmp_cached_38) | (_cmp_cached_26) | (_cmp_cached_35))
            # 1h high, 4h overbought
            & ((_cmp_cached_37) | (_cmp_cached_114))
            # 4h & 1d overbought
            & ((_cmp_cached_115) | (_cmp_cached_74))
            # big drop in the last 20 days, 1d high, 1d downtrend
            & (
              _gt_mul("close", "high_max_20_1d", 0.20)
              | (_cmp_cached_106)
              | (_cmp_cached_141)
            )
            # drop in last 20 days, 1h high, 1d downtrend
            & (_gt_mul("close", "high_max_20_1d", 0.20) | (_cmp_cached_12) | (_cmp_cached_150))
          )

          # Logic
          long_entry_logic.append(
            (_cmp("AROONU_14", "<", 25.0))
            & (_cmp("AROONU_14_15m", "<", 25.0))
            & (df["close"] < (df["EMA_9"] * 0.946))
            & (df["close"] < (df["EMA_20"] * 0.960))
          )

        # Condition #5 - Normal mode (Long).
        if long_entry_condition_index == 5:
          # Protections
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          long_entry_logic.append(df["protections_long_global"] == True)

          long_entry_logic.append(
            (_cmp_cached_16)
            # 5m & 1h down move, 1h still not low enough
            & ((_cmp_cached_48) | (_cmp_cached_1) | (_cmp_cached_138))
            # 5m & 1h down move, 1d high
            & ((_cmp_cached_48) | (_cmp_cached_10) | (_cmp_cached_9))
            # 5m & 1h down move, 1h still high
            & ((_cmp_cached_48) | (_cmp_cached_8) | (_cmp_cached_30))
            # 5m & 4h down move, 15m still high
            & ((_cmp_cached_48) | (_cmp_cached_80) | (_cmp_cached_113))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_8) | (_cmp_cached_105))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_28) | (_cmp_cached_11) | (_cmp_cached_30))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_28) | (_cmp_cached_11) | (_cmp_cached_34))
            # 15m & 1h down move, 4h overbought
            & ((_cmp_cached_28) | (_cmp_cached_8) | (_cmp("ROC_9_4h", "<", 70.0)))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_28) | (_cmp_cached_33) | (_cmp_cached_18))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_28) | (_cmp_cached_63) | (_cmp_cached_92))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_28) | (_cmp_cached_130) | (_cmp_cached_37))
            # 15m down move, 15m stil not low enough, 4h high
            & ((_cmp_cached_28) | (_cmp_cached_111) | (_cmp_cached_68))
            # 15m down move, 15m high, 1h high
            & ((_cmp_cached_28) | (_cmp_cached_90) | (_cmp_cached_56))
            # 15m down move, 4h & 1d overbought
            & ((_cmp_cached_28) | (_cmp_cached_27) | (_cmp_cached_35))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_70) | (_cmp_cached_60) | (_cmp_cached_20))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_70) | (_cmp_cached_8) | (_cmp_cached_92))
            # 15m down move, 15m still high, 1d high
            & ((_cmp_cached_70) | (_cmp_cached_46) | (_cmp_cached_106))
            # 15m down move, 15m high, 4h high
            & ((_cmp_cached_70) | (_cmp_cached_90) | (_cmp_cached_58))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_70) | (_cmp_cached_92) | (_cmp_cached_14))
            # 15m down move, 4h & 1d high
            & ((_cmp_cached_70) | (_cmp_cached_20) | (_cmp_cached_9))
            # 15m down move, 4h high, 1h downtrend
            & ((_cmp("RSI_3_15m", "<", 30.0)) | (_cmp_cached_93) | (_cmp("ROC_9_1h", ">", -40.0)))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_70) | (_cmp_cached_14) | (_cmp("ROC_9_4h", "<", 25.0)))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_100) | (_cmp_cached_41) | (_cmp_cached_34))
            # 15m down move, 15m high, 4h overbought
            & ((_cmp_cached_100) | (_cmp_cached_24) | (_cmp_cached_27))
            # 15m down move, 1h high, 4h overbought
            & ((_cmp_cached_100) | (_cmp_cached_92) | (_cmp_cached_114))
            # 15m down move, 4h high, 1h overbought
            & ((_cmp_cached_100) | (_cmp_cached_14) | (_cmp_cached_85))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_140) | (_cmp_cached_33) | (_cmp_cached_71))
            # 15m down move, 15m still high, 1h high
            & ((_cmp("RSI_3_15m", ">", 45.0)) | (_cmp_cached_46) | (_cmp_cached_92))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_36) | (_cmp_cached_57) | (_cmp_cached_45))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_36) | (_cmp_cached_4) | (_cmp_cached_67))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_36) | (_cmp_cached_4) | (_cmp("ROC_9_1d", "<", 15.0)))
            # 1h & 4h down move, 4h downtrend
            & ((_cmp_cached_36) | (_cmp_cached_5) | (_cmp_cached_139))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_36) | (_cmp_cached_21) | (_cmp_cached_95))
            # 1h & 1d down move, 1d high
            & ((_cmp_cached_36) | (_cmp_cached_64) | (_cmp_cached_42))
            # 1h & 4h down move, 1h downtrend
            & ((_cmp_cached_22) | (_cmp_cached_6) | (_cmp("ROC_9_1h", ">", -15.0)))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp_cached_43))
            # 1h & 4h down move, 15m still high
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp_cached_75))
            # 1h & 4h down move, 1h downtrend
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp_cached_120))
            # 1h & 4h & 1d down move
            & ((_cmp_cached_1) | (_cmp_cached_5) | (_cmp_cached_59))
            # 1h & 4h down move, 15m high
            & ((_cmp_cached_1) | (_cmp_cached_5) | (_cmp_cached_108))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_1) | (_cmp_cached_5) | (_cmp_cached_68))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_1) | (_cmp_cached_19) | (_cmp_cached_29))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_1) | (_cmp_cached_76) | (_cmp_cached_79))
            # 1h down move, 4h downtrend. 4h still not low enough
            & ((_cmp_cached_1) | (_cmp_cached_31) | (_cmp_cached_145))
            # 1h down move, 15m still high, 4h high
            & ((_cmp_cached_1) | (_cmp_cached_81) | (_cmp_cached_55))
            # 1h down move, 15m high, 4h downtrend
            & ((_cmp_cached_1) | (_cmp_cached_24) | (_cmp_cached_102))
            # 1h down move, 1h still high, 15m downtrend
            & ((_cmp_cached_1) | (_cmp_cached_86) | (_cmp("CMF_20_15m", ">", -0.30)))
            # 1h down move, 1d high, 4h overbought
            & ((_cmp_cached_1) | (_cmp_cached_9) | (_cmp_cached_26))
            # 1h down move, 1h still high, 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_30) | (_cmp_cached_44))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_1) | (_cmp_cached_84) | (_cmp_cached_51))
            # 1h & 4h down move, 1h still high
            & ((_cmp_cached_2) | (_cmp_cached_5) | (_cmp_cached_49))
            # 1h & 4h down move, 1h still not low enough
            & ((_cmp_cached_2) | (_cmp_cached_5) | (_cmp_cached_109))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_2) | (_cmp_cached_6) | (_cmp_cached_44))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_2) | (_cmp_cached_60) | (_cmp_cached_14))
            # 1h & 1d down move, 4h high
            & ((_cmp_cached_2) | (_cmp_cached_59) | (_cmp_cached_34))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_2) | (_cmp_cached_68) | (_cmp_cached_35))
            # 1h down move, 4h high, 1d high
            & ((_cmp_cached_2) | (_cmp_cached_20) | (_cmp_cached_84))
            # 1h down move, 1d high, 1d downtrend
            & ((_cmp_cached_2) | (_cmp_cached_45) | (_cmp_cached_15))
            # 1h down move, 1d high, 4h overbought
            & ((_cmp_cached_2) | (_cmp_cached_9) | (_cmp_cached_123))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_2) | (_cmp_cached_9) | (_cmp_cached_78))
            # 1h down move, 1h downtrend, 1d overbought
            & ((_cmp_cached_2) | (_cmp_cached_124) | (_cmp_cached_69))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_2) | (_cmp_cached_27) | (_cmp_cached_99))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_10) | (_cmp_cached_6) | (_cmp_cached_13))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_10) | (_cmp_cached_47) | (_cmp_cached_20))
            # 1h & 1d down move, 1h still high
            & ((_cmp_cached_10) | (_cmp_cached_77) | (_cmp_cached_30))
            # 1h & 4h down move, 15m high
            & ((_cmp_cached_11) | (_cmp_cached_21) | (_cmp_cached_24))
            # 1h down move, 4h downtrend, 4h high
            & ((_cmp_cached_11) | (_cmp("CMF_20_4h", ">", -0.50)) | (_cmp_cached_13))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_11) | (_cmp_cached_38) | (_cmp_cached_51))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_11) | (_cmp_cached_34) | (_cmp_cached_23))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_8) | (_cmp_cached_60) | (_cmp_cached_93))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_8) | (_cmp_cached_12) | (_cmp_cached_93))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_8) | (_cmp_cached_12) | (_cmp_cached_26))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_8) | (_cmp_cached_20) | (_cmp_cached_51))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_8) | (_cmp_cached_32) | (_cmp_cached_115))
            # 1h down move, 15m still high, 1h high
            & ((_cmp_cached_8) | (_cmp_cached_113) | (_cmp_cached_88))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_8) | (_cmp_cached_56) | (_cmp_cached_44))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_8) | (_cmp_cached_55) | (_cmp_cached_95))
            # 1h down move, 4h downtrend, 1d over
            & ((_cmp_cached_8) | (_cmp_cached_72) | (_cmp_cached_35))
            # 1h down move, 1h still high, 1d overbought
            & ((_cmp_cached_25) | (_cmp_cached_49) | (_cmp_cached_39))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_25) | (_cmp_cached_12) | (_cmp_cached_14))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_25) | (_cmp_cached_12) | (_cmp_cached_149))
            # 1h down move, 1h high, 4h downtrend
            & ((_cmp_cached_25) | (_cmp_cached_18) | (_cmp_cached_31))
            # 1h down move, 1h still high, 1d overbought
            & ((_cmp_cached_25) | (_cmp_cached_30) | (_cmp_cached_74))
            # 1h down move, 15m high, 1h high
            & ((_cmp_cached_33) | (_cmp_cached_90) | (_cmp_cached_12))
            # 1h down move, 1h still high, 1d overbought
            & ((_cmp_cached_33) | (_cmp_cached_86) | (_cmp_cached_29))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_33) | (_cmp_cached_18) | (_cmp_cached_14))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_33) | (_cmp_cached_42) | (_cmp_cached_35))
            # 1h down move, 1h & 4h overbought
            & ((_cmp_cached_33) | (_cmp_cached_85) | (_cmp_cached_26))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_65) | (_cmp("RSI_3_4h", ">", 65.0)) | (_cmp_cached_74))
            # 1h down move, 15m still high, 1h high
            & ((_cmp_cached_65) | (_cmp_cached_46) | (_cmp_cached_92))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_65) | (_cmp_cached_18) | (_cmp_cached_98))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_65) | (_cmp_cached_56) | (_cmp_cached_35))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_63) | (_cmp_cached_52) | (_cmp_cached_23))
            # 1h down move, 4h high, 1h overbought
            & ((_cmp_cached_63) | (_cmp_cached_32) | (_cmp_cached_134))
            # 1h down move, 4h & 1d high
            & ((_cmp_cached_63) | (_cmp_cached_14) | (_cmp_cached_9))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_63) | (_cmp_cached_105) | (_cmp_cached_146))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_63) | (_cmp_cached_26) | (_cmp_cached_69))
            # 1h down move, 15m high, 1h high
            & ((_cmp_cached_130) | (_cmp_cached_90) | (_cmp_cached_37))
            # 1h down move, 1h high & overbought
            & ((_cmp_cached_130) | (_cmp_cached_112) | (_cmp_cached_78))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_97) | (_cmp_cached_27) | (_cmp_cached_40))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_97) | (_cmp_cached_20) | (_cmp_cached_40))
            # 4h & 1d down move, 4h downtrend
            & ((_cmp_cached_80) | (_cmp_cached_66) | (_cmp_cached_31))
            # 4h & 1d down move, 1h still not low enough
            & ((_cmp_cached_57) | (_cmp_cached_66) | (_cmp_cached_109))
            # 4h down move, 1d high, 4h downtrend
            & ((_cmp_cached_57) | (_cmp_cached_42) | (_cmp_cached_102))
            # 4h & 1d down move, 15m high
            & ((_cmp_cached_4) | (_cmp_cached_59) | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 80.0)))
            # 4h & 1d down move, 1d downtrend
            & ((_cmp_cached_4) | (_cmp_cached_59) | (_cmp_cached_141))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_4) | (_cmp_cached_64) | (_cmp_cached_117))
            # 4h down move, 15m downtrend, 1d high
            & ((_cmp_cached_4) | (_cmp("CMF_20_15m", ">", -0.30)) | (_cmp_cached_42))
            # 4h down move, 15m still high, 1d downtrend
            & ((_cmp_cached_4) | (_cmp_cached_75) | (_cmp_cached_149))
            # 4h down move, 15m high
            & ((_cmp_cached_4) | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 80.0)))
            # 4h down move, 1h high, 1d downtrend
            & ((_cmp_cached_4) | (_cmp_cached_56) | (_cmp_cached_15))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_4) | (_cmp_cached_79) | (_cmp_cached_15))
            # 4h down move, 4h downtrend, 1d overbought
            & ((_cmp_cached_4) | (_cmp_cached_72) | (_cmp_cached_40))
            # 4h & 1d down move, 4h downtrend
            & ((_cmp_cached_5) | (_cmp_cached_53) | (_cmp_cached_139))
            # 4h down move, 1h high, 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_52) | (_cmp_cached_142))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_54) | (_cmp_cached_15))
            # 4h down move, 1h & 4h downtrend
            & ((_cmp_cached_5) | (_cmp_cached_124) | (_cmp_cached_72))
            # 4h & 1ddown move, 1d high
            & ((_cmp_cached_6) | (_cmp_cached_53) | (_cmp_cached_42))
            # 4h down move, 1d high, 1d downtrend
            & ((_cmp_cached_6) | (_cmp_cached_42) | (_cmp_cached_23))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_6) | (_cmp_cached_42) | (_cmp("ROC_9_1d", "<", 70.0)))
            # 4h down move, 4h still high. 4h downtrend
            & ((_cmp_cached_21) | (_cmp_cached_43) | (_cmp("CMF_20_4h", ">", -0.40)))
            # 4h down move, 4h high, 1d downtrend
            & ((_cmp_cached_21) | (_cmp_cached_105) | (_cmp_cached_150))
            # 4h down move, 1h high, 4h downtrend
            & ((_cmp_cached_19) | (_cmp_cached_12) | (_cmp_cached_102))
            # 4h down move, 1h high, 1d downtrend
            & ((_cmp_cached_19) | (_cmp_cached_112) | (_cmp_cached_44))
            # 4h down move, 4h & 1d high
            & ((_cmp_cached_41) | (_cmp_cached_13) | (_cmp_cached_9))
            # 4h down move, 4h high & overbought
            & ((_cmp_cached_60) | (_cmp_cached_20) | (_cmp_cached_27))
            # 4h down move, 4h high, 1d overbought
            & ((_cmp_cached_60) | (_cmp_cached_20) | (_cmp_cached_40))
            # 4h down move, 4h & 1d overbought
            & ((_cmp_cached_60) | (_cmp_cached_27) | (_cmp_cached_40))
            # 1d down move, 1d high, 1d downtrend
            & ((_cmp_cached_66) | (_cmp_cached_45) | (_cmp_cached_142))
            # 1d down move, 1h high, 4h downtrend
            & ((_cmp_cached_77) | (_cmp_cached_83) | (_cmp_cached_72))
            # 15m & 1h & 4h downtrend
            & ((_cmp("CMF_20_15m", ">", -0.30)) | (_cmp("CMF_20_1h", ">", -0.30)) | (_cmp("CMF_20_4h", ">", -0.30)))
            # 1d downtrend, 1d high & overbought
            & ((_cmp("CMF_20_1d", ">", -0.40)) | (_cmp_cached_103) | (_cmp_cached_39))
            # 15m not low enough, 1h & 4h downtrend
            & ((_cmp("AROONU_14_15m", "<", 20.0)) | (_cmp_cached_124) | (_cmp("ROC_9_4h", ">", -50.0)))
            # 15m high, 1h high & overbought
            & ((_cmp_cached_24) | (_cmp_cached_92) | (_cmp_cached_61))
            # 4h high, 4h & 1d overbought
            & ((_cmp_cached_13) | (_cmp_cached_123) | (_cmp_cached_69))
            # 1h & 4h high, 4h overbought
            & ((_cmp_cached_18) | (_cmp_cached_14) | (_cmp_cached_27))
            # 1h & 1d high, 1d overbought
            & ((_cmp_cached_18) | (_cmp_cached_42) | (_cmp_cached_74))
            # 1h high, 1h overbought
            & ((_cmp_cached_18) | (_cmp_cached_61))
            # 4h still high, 5m downtrend
            & ((_cmp_cached_67) | (_cmp("ROC_9", ">", -40.0)))
            # 4h & 1d high, 4h overbought
            & ((_cmp_cached_20) | (_cmp_cached_9) | (_cmp_cached_114))
            # 4h & 1d high, 1d overbought
            & ((_cmp_cached_20) | (_cmp_cached_9) | (_cmp_cached_69))
            # 4h high, 1h & 4h overbought
            & ((_cmp_cached_93) | (_cmp("ROC_9_1h", "<", 80.0)) | (_cmp_cached_114))
            # 4h high, 4h & 1d overbought
            & ((_cmp_cached_93) | (_cmp_cached_27) | (_cmp_cached_40))
            # 4h & 1d high, 4h overbought
            & ((_cmp_cached_14) | (_cmp_cached_9) | (_cmp_cached_73))
            # 4h high, 1h & 1d overbought
            & ((_cmp_cached_14) | (_cmp_cached_134) | (_cmp_cached_29))
            # 4h high, 4h & 1d overbought
            & ((_cmp_cached_14) | (_cmp_cached_26) | (_cmp_cached_69))
            # 1d high, 1h & 4h down move
            & ((_cmp_cached_9) | (_cmp("ROC_9_1h", "<", 25.0)) | (_cmp_cached_123))
            # 1d high, 1h downtrend, 1d overbought
            & ((_cmp_cached_9) | (_cmp_cached_124) | (_cmp_cached_29))
            # 1d high, 4h & 1d overbought
            & ((_cmp_cached_9) | (_cmp_cached_26) | (_cmp_cached_69))
            # 15m high, 4h & 1d downtrend
            & ((_cmp_cached_108) | (_cmp_cached_72) | (_cmp_cached_23))
            # 1h high, 4h & 1d overbought
            & ((_cmp_cached_83) | (_cmp_cached_26) | (_cmp_cached_29))
            # 4h high, 1h overbought, 1d downtrend
            & ((_cmp_cached_34) | (_cmp_cached_134) | (_cmp_cached_150))
            # 4h high, 4h & 1d overbought
            & ((_cmp_cached_34) | (_cmp_cached_114) | (_cmp_cached_29))
            # 4h high, 1h & 4h overbought
            & ((_cmp_cached_55) | (_cmp_cached_61) | (_cmp_cached_114))
            # 4h high, 1h & 4h overbought
            & ((_cmp_cached_55) | (_cmp_cached_85) | (_cmp_cached_98))
            # 1d high, 4h & 1d overbought
            & ((_cmp_cached_62) | (_cmp_cached_73) | (_cmp_cached_29))
            # 1d P&D, dh downtrend
            & ((_cmp("change_pct_1d", ">", -50.0)) | (df["change_pct_1d"].shift(288) < 50.0) | (_cmp_cached_5))
            # big drop in the last 20 days, 1d high, 1d downtrend
            & (
              _gt_mul("close", "high_max_20_1d", 0.20)
              | (_cmp_cached_106)
              | (_cmp_cached_141)
            )
            # drop in last 20 days, 1h high, 1d downtrend
            & (_gt_mul("close", "high_max_20_1d", 0.20) | (_cmp_cached_12) | (_cmp_cached_150))
            # drop in last 20 days. 4h high
            & (_gt_mul("close", "high_max_20_1d", 0.10) | (_cmp_cached_55))
          )

          # Logic
          long_entry_logic.append(
            (_cmp("RSI_3", "<", 50.0))
            & (_cmp("AROONU_14", "<", 25.0))
            & (_cmp("STOCHRSIk_14_14_3_3", "<", 30.0))
            & (df["EMA_26"] > df["EMA_12"])
            & ((df["EMA_26"] - df["EMA_12"]) > (df["open"] * 0.020))
            & _ema_26_12_spread_gt_open_pct
          )

        # Condition #6 - Normal mode (Long).
        if long_entry_condition_index == 6:
          # Protections
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          long_entry_logic.append(df["protections_long_global"] == True)

          long_entry_logic.append(
            # 5m & 15m down move, 15m still high
            ((_cmp_cached_48) | (_cmp_cached_0) | (_cmp_cached_113))
            # 5m & 15m down move, 15m still high
            & ((_cmp_cached_48) | (_cmp_cached_3) | (_cmp_cached_81))
            # 5m & 15m down move, 1d downtrend
            & ((_cmp_cached_48) | (_cmp_cached_3) | (_cmp_cached_15))
            # 5m & 15m down move, 1d downtrend
            & ((_cmp_cached_48) | (_cmp_cached_28) | (_cmp_cached_23))
            # 5m & 1h down move, 1h still not low enough
            & ((_cmp_cached_48) | (_cmp_cached_10) | (_cmp_cached_138))
            # 5m & 1h down move, 1h still high
            & ((_cmp_cached_48) | (_cmp_cached_8) | (_cmp_cached_30))
            # 5m & 4h down move, 4h still high
            & ((_cmp_cached_48) | (_cmp_cached_5) | (_cmp_cached_54))
            # 5m & 4h & 1d down move
            & ((_cmp_cached_48) | (_cmp_cached_6) | (_cmp_cached_133))
            # 5m & 4h down move, 4h high
            & ((_cmp_cached_48) | (_cmp_cached_19) | (_cmp_cached_58))
            # 5m & 4h down move, 4h still high
            & ((_cmp_cached_48) | (_cmp_cached_131) | (_cmp_cached_43))
            # 5m & 1d down move, 15m still high
            & ((_cmp_cached_48) | (_cmp_cached_53) | (_cmp_cached_113))
            # 5m down move, 4h & 1d overbought
            & ((_cmp_cached_48) | (_cmp_cached_26) | (_cmp_cached_40))
            # 5m & 1h down move, 4h high
            & ((_cmp_cached_104) | (_cmp_cached_33) | (_cmp_cached_68))
            # 5m & 1h down move, 1h high
            & ((_cmp_cached_104) | (_cmp_cached_97) | (_cmp_cached_18))
            # 5m & 4h down move, 1d downtrend
            & ((_cmp_cached_104) | (_cmp_cached_57) | (_cmp_cached_15))
            # 5m & 4h down move, 4h still high
            & ((_cmp_cached_104) | (_cmp_cached_5) | (_cmp_cached_67))
            # 5m & 4h down move, 15m still high
            & ((_cmp_cached_104) | (_cmp_cached_21) | (_cmp_cached_75))
            # 5m & 4h down move, 1d overbought
            & ((_cmp_cached_104) | (_cmp_cached_19) | (_cmp_cached_99))
            # 5m & 4h down move, 4h high
            & ((_cmp_cached_104) | (_cmp_cached_87) | (_cmp_cached_20))
            # 5m down move, 15m still not low enough, 4h high
            & ((_cmp_cached_104) | (_cmp("AROONU_14_15m", "<", 20.0)) | (_cmp_cached_58))
            # 5m down move, 1h & 1d high
            & ((_cmp_cached_104) | (_cmp_cached_12) | (_cmp_cached_9))
            # 5m down move, 4h high & overbought
            & ((_cmp_cached_104) | (_cmp_cached_14) | (_cmp("ROC_9_4h", "<", 25.0)))
            # 5m down move, 1h high
            & ((_cmp_cached_104) | (_cmp_cached_37))
            # 5m & 1d down move, 1d still high
            & ((_cmp_cached_143) | (_cmp_cached_59) | (_cmp("STOCHRSIk_14_14_3_3_1d", "<", 40.0)))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_7) | (_cmp_cached_10) | (_cmp_cached_49))
            # 15m & 1h down move, 4h still not low enough
            & ((_cmp_cached_7) | (_cmp_cached_10) | (_cmp("AROONU_14_4h", "<", 20.0)))
            # 15m & 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_7) | (_cmp_cached_11) | (_cmp_cached_110) | (_cmp_cached_142))
            # 15m & 1h down move, 1h still not low enough
            & ((_cmp_cached_7) | (_cmp_cached_11) | (_cmp("AROONU_14_1h", "<", 20.0)))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_7) | (_cmp_cached_11) | (_cmp_cached_79))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_7) | (_cmp_cached_33) | (_cmp_cached_13))
            # 15m & 4h down move, 1h still not low enough
            & ((_cmp_cached_7) | (_cmp_cached_4) | (_cmp_cached_109))
            # 15m & 4h down move, 1d downtrend
            & ((_cmp_cached_7) | (_cmp_cached_5) | (_cmp_cached_142))
            # 15m & 4h down move, 4h still not low enough
            & ((_cmp_cached_7) | (_cmp_cached_6) | (_cmp("AROONU_14_4h", "<", 20.0)))
            # 15m & 4h down move, 15m still not low enough
            & ((_cmp_cached_7) | (_cmp_cached_19) | (_cmp("AROONU_14_15m", "<", 25.0)))
            # 15m & 4h down move, 1h still high
            & ((_cmp_cached_7) | (_cmp_cached_19) | (_cmp_cached_82))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_7) | (_cmp_cached_76) | (_cmp_cached_112))
            # 15m & 1d down move, 15m still not low enough
            & ((_cmp_cached_7) | (_cmp_cached_66) | (_cmp_cached_111))
            # 15m & 1d down move, 4h high
            & ((_cmp_cached_7) | (_cmp("RSI_3_1d", ">", 55.0)) | (_cmp_cached_58))
            # 1h & 1d downtrend, 1d high
            & ((_cmp_cached_7) | (_cmp_cached_45) | (_cmp_cached_78))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_17) | (_cmp_cached_11) | (_cmp_cached_88))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_17) | (_cmp_cached_11) | (_cmp_cached_82))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_17) | (_cmp_cached_11) | (_cmp_cached_94))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_17) | (_cmp_cached_8) | (_cmp_cached_32))
            # 15m & 1h & 4h down move, 15m downtrend
            & (
              (_cmp_cached_17) | (_cmp_cached_33) | (_cmp_cached_60) | (_cmp("CMF_20_15m", ">", -0.30))
            )
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_17) | (_cmp_cached_33) | (_cmp_cached_30))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_17) | (_cmp_cached_130) | (_cmp_cached_14))
            # 15m & 4h down move, 15m still not low enough
            & ((_cmp_cached_17) | (_cmp_cached_6) | (_cmp_cached_111))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_17) | (_cmp_cached_41) | (_cmp_cached_105))
            # 15m down move, 15m still high, 1h still high
            & ((_cmp_cached_17) | (_cmp_cached_111) | (_cmp_cached_30))
            # 15m down move, 1h still high, 1d high
            & ((_cmp_cached_17) | (_cmp_cached_82) | (_cmp_cached_45))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_17) | (_cmp_cached_12) | (_cmp_cached_32))
            # 15m down move, 15m & 1h still not low enough
            & (
              (_cmp_cached_17) | (_cmp_cached_125) | (_cmp_cached_109)
            )
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_0) | (_cmp_cached_10) | (_cmp_cached_30))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_0) | (_cmp_cached_10) | (_cmp_cached_67))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_10) | (_cmp_cached_105))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_0) | (_cmp_cached_11) | (_cmp_cached_43))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_8) | (_cmp_cached_58))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_8) | (_cmp_cached_105))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_8) | (_cmp_cached_51))
            # 15m & 1h down move, 1d downtrend
            & ((_cmp_cached_0) | (_cmp_cached_8) | (_cmp_cached_44))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_0) | (_cmp_cached_25) | (_cmp_cached_82))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_0) | (_cmp_cached_65) | (_cmp_cached_82))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_65) | (_cmp("ROC_9_1d", "<", 150.0)))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_63) | (_cmp_cached_34))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_0) | (_cmp_cached_130) | (_cmp_cached_112))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_0) | (_cmp("RSI_3_1h", ">", 65.0)) | (_cmp_cached_18))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_0) | (_cmp_cached_4) | (_cmp_cached_42))
            # 15m & 4h down move, 4h still not low enough
            & ((_cmp_cached_0) | (_cmp_cached_4) | (_cmp_cached_94))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_0) | (_cmp_cached_4) | (_cmp_cached_106))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_0) | (_cmp_cached_5) | (_cmp("RSI_14_1d", "<", 60.0)))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_0) | (_cmp_cached_6) | (_cmp_cached_67))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_0) | (_cmp_cached_6) | (_cmp_cached_38))
            # 15m & 4h down move, 1h still high
            & ((_cmp_cached_0) | (_cmp_cached_6) | (_cmp_cached_30))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_0) | (_cmp_cached_6) | (_cmp_cached_79))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_0) | (_cmp_cached_6) | (_cmp_cached_62))
            # 15m & 4h down move, 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_6) | (_cmp_cached_39))
            # 15m & 4h down move, 4h downtrend
            & ((_cmp_cached_0) | (_cmp_cached_21) | (_cmp("CMF_20_4h", ">", -0.30)))
            # 15m & 4h down move, 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_21) | (_cmp_cached_51))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_0) | (_cmp_cached_19) | (_cmp_cached_43))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_76) | (_cmp_cached_13))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_60) | (_cmp("AROONU_14_4h", "<", 75.0)))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_87) | (_cmp_cached_34))
            # 15m & 1d down move, 1h still high
            & ((_cmp_cached_0) | (_cmp_cached_66) | (_cmp_cached_82))
            # 15m & 1d down move, 1d high
            & ((_cmp_cached_0) | (_cmp_cached_53) | (_cmp("AROONU_14_1d", "<", 75.0)))
            # 15m & 1d down move, 1d overbought
            & ((_cmp_cached_0) | (_cmp("RSI_3_1d", ">", 50.0)) | (_cmp_cached_39))
            # 15m down move, 15m downtrend, 4h still high
            & ((_cmp_cached_0) | (_cmp("CMF_20_15m", ">", -0.40)) | (_cmp_cached_54))
            # 15m down move, 1h downtrend, 4h still high
            & ((_cmp_cached_0) | (_cmp("CMF_20_1h", ">", -0.30)) | (_cmp_cached_79))
            # 15m down move, 15m still not low enough, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_111) | (_cmp_cached_68))
            # 15m down move, 15m still high, 1h still high
            & ((_cmp_cached_0) | (_cmp_cached_81) | (_cmp_cached_30))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_0) | (_cmp_cached_32) | (_cmp_cached_26))
            # 15m down move, 1h still not low enough, 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_109) | (_cmp_cached_29))
            # 15m down move, 1h still high, 4h downtrend
            & ((_cmp_cached_0) | (_cmp_cached_30) | (_cmp_cached_31))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_0) | (_cmp_cached_58) | (_cmp_cached_27))
            # 15m down move, 4h high, 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_58) | (_cmp_cached_78))
            # 15m & 1h & 4h down move
            & ((_cmp_cached_3) | (_cmp_cached_2) | (_cmp_cached_2))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_3) | (_cmp_cached_2) | (_cmp_cached_86))
            # 15m & 1h down move, 1h downtrend
            & ((_cmp_cached_3) | (_cmp_cached_10) | (_cmp("CMF_20_1h", ">", -0.30)))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_3) | (_cmp_cached_11) | (_cmp_cached_49))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_11) | (_cmp_cached_13))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_3) | (_cmp_cached_11) | (_cmp_cached_82))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_3) | (_cmp_cached_11) | (_cmp_cached_29))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_3) | (_cmp_cached_8) | (_cmp_cached_84))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_63) | (_cmp_cached_14))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_130) | (_cmp_cached_52))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_3) | (_cmp_cached_6) | (_cmp_cached_38))
            # 15m & 4h down move, 15m still high
            & ((_cmp_cached_3) | (_cmp_cached_6) | (_cmp_cached_75))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_19) | (_cmp_cached_112))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_41) | (_cmp_cached_68))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_41) | (_cmp_cached_58))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_47) | (_cmp_cached_20))
            # 15m & 4h down move, 1d overbought
            & ((_cmp_cached_3) | (_cmp_cached_47) | (_cmp_cached_40))
            # 15m & 4h down move, 1d overbought
            & ((_cmp_cached_3) | (_cmp_cached_76) | (_cmp_cached_69))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_131) | (_cmp_cached_58))
            # 15m & 1d down move, 1h still high
            & ((_cmp_cached_3) | (_cmp_cached_59) | (_cmp_cached_109))
            # 15m & 1d down move, 1h still high
            & ((_cmp_cached_3) | (_cmp_cached_53) | (_cmp_cached_30))
            # 15m & 1d down move, 1d overbought
            & ((_cmp_cached_3) | (_cmp_cached_77) | (_cmp_cached_78))
            # 15m down move, 15m still not low enough, 1h high
            & ((_cmp_cached_3) | (_cmp("AROONU_14_15m", "<", 25.0)) | (_cmp_cached_37))
            # 15m down move, 15m still high, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_81) | (_cmp_cached_13))
            # 15m down move, 1h still high, 1d overbought
            & ((_cmp_cached_3) | (_cmp_cached_49) | (_cmp_cached_69))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_3) | (_cmp_cached_88) | (_cmp_cached_32))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_3) | (_cmp_cached_18) | (_cmp_cached_93))
            # 15m down move, 1h & 1d high
            & ((_cmp_cached_3) | (_cmp_cached_12) | (_cmp_cached_45))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_3) | (_cmp_cached_92) | (_cmp_cached_55))
            # 15m down move, 4h high, 4h downtrend
            & ((_cmp_cached_3) | (_cmp_cached_68) | (_cmp_cached_31))
            # 15m down move, 4h & 1d high
            & ((_cmp_cached_3) | (_cmp_cached_13) | (_cmp_cached_9))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_3) | (_cmp_cached_13) | (_cmp_cached_50))
            # 15m down move, 4h high, 1h overbought
            & ((_cmp_cached_3) | (_cmp_cached_32) | (_cmp("ROC_9_1h", "<", 25.0)))
            # 15m down move, 4h high, 1h overbought
            & ((_cmp_cached_3) | (_cmp_cached_14) | (_cmp_cached_61))
            # 15m down move, 1h still high, 4h overbought
            & ((_cmp_cached_3) | (_cmp_cached_30) | (_cmp_cached_27))
            # 15m down move, 1h high, 4h downtrend
            & ((_cmp_cached_3) | (_cmp_cached_37) | (_cmp_cached_31))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_3) | (_cmp_cached_55) | (_cmp_cached_26))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_16) | (_cmp_cached_10) | (_cmp_cached_132))
            # 15m & 1h down move, 1d downtrend
            & ((_cmp_cached_16) | (_cmp_cached_8) | (_cmp_cached_23))
            # 15m & 1h down move, 1h overbought
            & ((_cmp_cached_16) | (_cmp_cached_63) | (_cmp_cached_61))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_16) | (_cmp_cached_11) | (_cmp_cached_34))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_16) | (_cmp_cached_25) | (_cmp_cached_9))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_16) | (_cmp_cached_65) | (_cmp_cached_12))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_16) | (_cmp_cached_97) | (_cmp_cached_52))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_16) | (_cmp_cached_97) | (_cmp_cached_55))
            # 15m & 4h & 1d down move
            & ((_cmp_cached_16) | (_cmp_cached_6) | (_cmp_cached_53))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_16) | (_cmp_cached_6) | (_cmp_cached_62))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_16) | (_cmp_cached_76) | (_cmp_cached_62))
            # 15m & 1d down move, 1h high
            & ((_cmp_cached_16) | (_cmp_cached_53) | (_cmp_cached_12))
            # 15m & 1d down move, 15m still high
            & ((_cmp_cached_16) | (_cmp_cached_77) | (_cmp_cached_75))
            # 15m down move, 15m still not low enough, 1h high
            & ((_cmp_cached_16) | (_cmp("AROONU_14_15m", "<", 25.0)) | (_cmp_cached_83))
            # 15m down move, 15m still high, 1h high
            & ((_cmp_cached_16) | (_cmp_cached_81) | (_cmp_cached_12))
            # 15m down move, 15m still high, 4h high
            & ((_cmp_cached_16) | (_cmp_cached_81) | (_cmp_cached_13))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_16) | (_cmp_cached_18) | (_cmp_cached_20))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_16) | (_cmp_cached_18) | (_cmp_cached_78))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_16) | (_cmp_cached_13) | (_cmp_cached_50))
            # 15m down move, 4h high, 1h overbought
            & ((_cmp_cached_16) | (_cmp_cached_14) | (_cmp_cached_129))
            # 15m down move, 1d high, 4h downtrend
            & ((_cmp_cached_16) | (_cmp_cached_38) | (_cmp_cached_31))
            # 15m down move, 1d high, 4h overbought
            & ((_cmp_cached_16) | (_cmp_cached_9) | (_cmp_cached_26))
            # 15m down move, 1d high, 1d overbought
            & ((_cmp_cached_16) | (_cmp_cached_9) | (_cmp_cached_39))
            # 15m down move, 15m high, 4h downtrend
            & ((_cmp_cached_16) | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 60.0)) | (_cmp("ROC_9_4h", ">", -50.0)))
            # 15 down move, 1h high, 1d overbought
            & ((_cmp_cached_16) | (_cmp_cached_56) | (_cmp_cached_78))
            # 15m down move, 4h high, 15m downtrend
            & ((_cmp_cached_16) | (_cmp_cached_58) | (_cmp("CMF_20_15m", ">", -0.40)))
            # 15m & 1h down move, 15m high
            & ((_cmp_cached_28) | (_cmp_cached_11) | (_cmp_cached_108))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_28) | (_cmp_cached_25) | (_cmp_cached_30))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_28) | (_cmp_cached_33) | (_cmp_cached_62))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_28) | (_cmp_cached_33) | (_cmp_cached_69))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_28) | (_cmp_cached_63) | (_cmp_cached_92))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_28) | (_cmp_cached_97) | (_cmp_cached_14))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_28) | (_cmp_cached_97) | (_cmp_cached_55))
            # 15m & 4h down move, 4h overbought
            & ((_cmp_cached_28) | (_cmp_cached_131) | (_cmp_cached_50))
            # 15m & 1d down move, 1h high
            & ((_cmp_cached_28) | (_cmp_cached_64) | (_cmp_cached_18))
            # 15m down move, 15m still not low enough, 1h high
            & ((_cmp_cached_28) | (_cmp("AROONU_14_15m", "<", 25.0)) | (_cmp_cached_83))
            # 15m down move, 15m still high, 1h high
            & ((_cmp_cached_28) | (_cmp_cached_81) | (_cmp_cached_37))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_28) | (_cmp_cached_88) | (_cmp_cached_99))
            # 15m down move, 1h high, 4h overbought
            & ((_cmp_cached_28) | (_cmp_cached_12) | (_cmp_cached_73))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_28) | (_cmp_cached_92) | (_cmp_cached_14))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_28) | (_cmp_cached_52) | (_cmp_cached_32))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_28) | (_cmp_cached_13) | (_cmp_cached_98))
            # 15m down move, 4h high, 1d overbought
            & ((_cmp_cached_28) | (_cmp_cached_20) | (_cmp_cached_29))
            # 15m down move, 1h high, 1d downtrend
            & ((_cmp_cached_28) | (_cmp_cached_56) | (_cmp_cached_15))
            # 15m down move, 1h high & overbought
            & ((_cmp_cached_28) | (_cmp_cached_83) | (_cmp_cached_85))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_28) | (_cmp_cached_55) | (_cmp_cached_50))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_70) | (_cmp_cached_25) | (_cmp_cached_18))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_70) | (_cmp_cached_130) | (_cmp_cached_37))
            # 15m & 4h down move, 15m high
            & ((_cmp_cached_70) | (_cmp_cached_19) | (_cmp_cached_108))
            # 15m down move, 1h high & overbought
            & ((_cmp_cached_70) | (_cmp_cached_52) | (_cmp_cached_61))
            # 15m down move, 15m still high, 4h high
            & ((_cmp_cached_100) | (_cmp_cached_81) | (_cmp_cached_93))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_70) | (_cmp_cached_14) | (_cmp_cached_73))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_70) | (_cmp_cached_55) | (_cmp_cached_73))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_100) | (_cmp_cached_33) | (_cmp_cached_56))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_100) | (_cmp("RSI_3_1h", ">", 65.0)) | (_cmp_cached_18))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_100) | (_cmp_cached_41) | (_cmp_cached_34))
            # 15m down move, 15m still not low enough, 1h high
            & ((_cmp_cached_100) | (_cmp("AROONU_14_15m", "<", 25.0)) | (_cmp_cached_18))
            # 15m down move, 15m still not low enough, 1h high
            & ((_cmp_cached_100) | (_cmp("AROONU_14_15m", "<", 25.0)) | (_cmp_cached_37))
            # 15m down move, 1m still high, 4h overbought
            & ((_cmp_cached_100) | (_cmp_cached_81) | (_cmp_cached_98))
            # 15m down move, 1h high, 4h overbought
            & ((_cmp_cached_100) | (_cmp_cached_18) | (_cmp_cached_27))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_100) | (_cmp_cached_14) | (_cmp("ROC_9_4h", "<", 70.0)))
            # 15m down move, 1h high & overbought
            & ((_cmp_cached_100) | (_cmp_cached_83) | (_cmp_cached_134))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_140) | (_cmp_cached_33) | (_cmp_cached_14))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_140) | (_cmp_cached_76) | (_cmp_cached_83))
            # 15m down move, 15m still high, 1d high
            & ((_cmp_cached_140) | (_cmp_cached_113) | (_cmp_cached_29))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_140) | (_cmp_cached_14) | (_cmp_cached_73))
            # 15m down move, 1h high, 4h overbought
            & ((_cmp("RSI_3_15m", ">", 50.0)) | (_cmp_cached_37) | (_cmp_cached_73))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_36) | (_cmp_cached_5) | (_cmp_cached_106))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_22) | (_cmp_cached_57) | (_cmp_cached_79))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_22) | (_cmp_cached_19) | (_cmp_cached_13))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp_cached_43))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_1) | (_cmp_cached_5) | (_cmp_cached_13))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_5) | (_cmp_cached_44))
            # 1h & 4h down move, 1h still high
            & ((_cmp_cached_1) | (_cmp_cached_19) | (_cmp_cached_49))
            # 1h & 4h down move, 15m still not low enough
            & ((_cmp_cached_1) | (_cmp_cached_47) | (_cmp_cached_125))
            # 1h down move, 1d high, 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_45) | (_cmp_cached_15))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_54) | (_cmp_cached_44))
            # 1h & 4h down move, 15m high
            & ((_cmp_cached_2) | (_cmp_cached_5) | (_cmp_cached_108))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_2) | (_cmp_cached_6) | (_cmp_cached_94))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_2) | (_cmp_cached_6) | (_cmp_cached_23))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_2) | (_cmp_cached_41) | (_cmp_cached_12))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_2) | (_cmp_cached_41) | (_cmp_cached_54))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_2) | (_cmp_cached_42) | (_cmp_cached_78))
            # 1h down move, 1d high, 4h downtrend
            & ((_cmp_cached_2) | (_cmp_cached_38) | (_cmp_cached_31))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_10) | (_cmp_cached_41) | (_cmp_cached_58))
            # 1h & 1d down move, 1d high
            & ((_cmp_cached_10) | (_cmp("RSI_3_1d", ">", 50.0)) | (_cmp("STOCHRSIk_14_14_3_3_1d", "<", 60.0)))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_10) | (_cmp_cached_88) | (_cmp_cached_35))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_10) | (_cmp_cached_12) | (_cmp_cached_39))
            # 1h down move, 1d high, 4h downtrend
            & ((_cmp_cached_10) | (_cmp_cached_84) | (_cmp_cached_31))
            # 1h down move, 4h downtrend, 1d overbought
            & ((_cmp_cached_10) | (_cmp_cached_102) | (_cmp_cached_39))
            # 1h & 4h down move, 1h still high
            & ((_cmp_cached_11) | (_cmp_cached_4) | (_cmp_cached_82))
            # 1h & 4h down move, 15m high
            & ((_cmp_cached_11) | (_cmp_cached_19) | (_cmp_cached_108))
            # 1h down move, 4h downtrend, 4h high
            & ((_cmp_cached_11) | (_cmp("CMF_20_4h", ">", -0.50)) | (_cmp_cached_13))
            # 1h down move, 1h still high, 1d high
            & ((_cmp_cached_11) | (_cmp_cached_86) | (_cmp_cached_38))
            # 1h down move, 1h still high, 4h overbought
            & ((_cmp_cached_11) | (_cmp_cached_49) | (_cmp_cached_123))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_67) | (_cmp_cached_29))
            # 1h down move, 1d still high, 1d downtrend
            & ((_cmp_cached_11) | (_cmp_cached_117) | (_cmp_cached_15))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_8) | (_cmp_cached_41) | (_cmp("RSI_14_1d", "<", 80.0)))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_8) | (_cmp_cached_47) | (_cmp_cached_68))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_8) | (_cmp_cached_87) | (_cmp_cached_34))
            # 1h & 1d down move, 1h high
            & ((_cmp_cached_8) | (_cmp_cached_77) | (_cmp_cached_88))
            # 1h down move, 4h & 1d down move
            & ((_cmp_cached_8) | (_cmp_cached_13) | (_cmp_cached_9))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_8) | (_cmp_cached_93) | (_cmp_cached_114))
            # 1h down move, 1d still high, 1d downtrend
            & ((_cmp_cached_8) | (_cmp_cached_135) | (_cmp_cached_15))
            # 1h down move, 1d high, 4h downtrend
            & ((_cmp_cached_8) | (_cmp_cached_9) | (_cmp_cached_72))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_8) | (_cmp_cached_62) | (_cmp_cached_39))
            # 1h down move, 4h & 1d downtrend
            & ((_cmp_cached_8) | (_cmp("ROC_9_4h", ">", -25.0)) | (_cmp_cached_146))
            # 1h & 1d down move, 1h high
            & ((_cmp_cached_25) | (_cmp_cached_133) | (_cmp("AROONU_14_1h", "<", 75.0)))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_25) | (_cmp_cached_88) | (_cmp_cached_13))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_25) | (_cmp_cached_13) | (_cmp_cached_23))
            # 1h down move, 1d high, 4h overbought
            & ((_cmp_cached_25) | (_cmp_cached_38) | (_cmp_cached_73))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_25) | (_cmp_cached_27) | (_cmp_cached_35))
            # 1h & 1d down move, 1d high
            & ((_cmp_cached_25) | (_cmp_cached_107) | (_cmp_cached_38))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_33) | (_cmp_cached_60) | (_cmp_cached_112))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_33) | (_cmp_cached_88) | (_cmp_cached_40))
            # 1h down move, 1h still high, 1d high
            & ((_cmp_cached_33) | (_cmp_cached_49) | (_cmp_cached_103))
            # 1h down move, 1h still high, 1d overbought
            & ((_cmp_cached_33) | (_cmp_cached_49) | (_cmp_cached_39))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_33) | (_cmp_cached_12) | (_cmp_cached_50))
            # 1h down move, 1h high, 15m downtrend
            & ((_cmp_cached_33) | (_cmp_cached_18) | (_cmp("ROC_9_15m", ">", -15.0)))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_33) | (_cmp_cached_42) | (_cmp_cached_35))
            # 1h down move, 1d high, 4h overbought
            & ((_cmp_cached_33) | (_cmp_cached_62) | (_cmp_cached_26))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_65) | (_cmp("RSI_3_4h", ">", 65.0)) | (_cmp_cached_74))
            # 1h down move, 1h still not low enough, 1d downtrend
            & ((_cmp_cached_65) | (_cmp_cached_138) | (_cmp_cached_149))
            # 1h down move, 1h still high, 1d overbought
            & ((_cmp_cached_65) | (_cmp_cached_82) | (_cmp_cached_29))
            # 1h down move, 4h high, 1h overbought
            & ((_cmp_cached_63) | (_cmp_cached_93) | (_cmp_cached_85))
            # 1h down move, 1d high, 4h overbought
            & ((_cmp_cached_63) | (_cmp_cached_38) | (_cmp_cached_26))
            # 1h down move, 1h high & overbought
            & ((_cmp_cached_63) | (_cmp_cached_37) | (_cmp_cached_61))
            # 1h down move, 1h & 4h overbought
            & ((_cmp_cached_63) | (_cmp_cached_61) | (_cmp_cached_115))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_63) | (_cmp_cached_26) | (_cmp_cached_39))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_130) | (_cmp_cached_131) | (_cmp_cached_56))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_130) | (_cmp_cached_18) | (_cmp_cached_27))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_130) | (_cmp_cached_14) | (_cmp_cached_27))
            # 1h & 1d down move, 1h high
            & ((_cmp_cached_97) | (_cmp("RSI_3_1d", ">", 60.0)) | (_cmp_cached_12))
            # 1h down move, 4 high, 1h overbought
            & ((_cmp_cached_97) | (_cmp_cached_14) | (_cmp_cached_61))
            # 1h down move, 1d high, 1h overbought
            & ((_cmp_cached_97) | (_cmp_cached_38) | (_cmp_cached_61))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_97) | (_cmp_cached_56) | (_cmp_cached_142))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_97) | (_cmp_cached_37) | (_cmp_cached_29))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp("RSI_3_1h", ">", 65.0)) | (_cmp_cached_12) | (_cmp("ROC_9_4h", "<", 25.0)))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp("RSI_3_1h", ">", 65.0)) | (_cmp_cached_83) | (_cmp_cached_39))
            # 4h down move, 1h still not low enough, 4h downtrend
            & ((_cmp_cached_80) | (_cmp("AROONU_14_1h", "<", 20.0)) | (_cmp_cached_102))
            # 4h down move, 4h & 1d downtrend
            & ((_cmp_cached_80) | (_cmp_cached_102) | (_cmp_cached_142))
            # 4h & 1d down move, 15m still high
            & ((_cmp_cached_57) | (_cmp_cached_64) | (_cmp_cached_113))
            # 4h & 1d down move, 1h still not low enough
            & ((_cmp_cached_4) | (_cmp_cached_66) | (_cmp_cached_132))
            # 4h & 1d down move, 1d downtrend
            & ((_cmp_cached_4) | (_cmp_cached_59) | (_cmp_cached_44))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_4) | (_cmp_cached_53) | (_cmp_cached_117))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_4) | (_cmp_cached_133) | (_cmp_cached_9))
            # 4h & 1d down move, 1d overbought
            & ((_cmp_cached_4) | (_cmp_cached_107) | (_cmp_cached_78))
            # 4h down move, 15m high
            & ((_cmp_cached_4) | (_cmp_cached_108))
            # 4h & 1d down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_64) | (_cmp_cached_13))
            # 4h & 1d down move, 1h still high
            & ((_cmp_cached_5) | (_cmp_cached_77) | (_cmp_cached_82))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_64) | (_cmp_cached_45))
            # 4h & 1d down move, 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_64) | (_cmp_cached_141))
            # 4h & 1d down move, 4h still high
            & ((_cmp_cached_5) | (_cmp("RSI_3_1d", ">", 50.0)) | (_cmp_cached_79))
            # 4h down move, 1d still high, 4h still not low enough
            & ((_cmp_cached_5) | (_cmp("RSI_14_1d", "<", 40.0)) | (_cmp_cached_94))
            # 4h down move, 4h still not low enough, 1d downtrend
            & ((_cmp_cached_5) | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 20.0)) | (_cmp_cached_15))
            # 4h down move, 1h & 4h downtrend
            & ((_cmp_cached_5) | (_cmp_cached_124) | (_cmp_cached_72))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_6) | (_cmp_cached_53) | (_cmp("AROONU_14_1d", "<", 60.0)))
            # 4h & 1d down move, 4h still high
            & ((_cmp_cached_6) | (_cmp_cached_53) | (_cmp_cached_79))
            # 4h & 1d down move, 1d overbought
            & ((_cmp_cached_6) | (_cmp_cached_107) | (_cmp_cached_40))
            # 4h down move, 15m high
            & ((_cmp_cached_6) | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 80.0)))
            # 4h down move, 1h high, 4h downtrend
            & ((_cmp_cached_6) | (_cmp_cached_56) | (_cmp_cached_31))
            # 4h down move, 4h still high, 4h downtrend
            & ((_cmp_cached_21) | (_cmp_cached_43) | (_cmp("CMF_20_4h", ">", -0.40)))
            # 4h down move, 4h high, 1d downtrend
            & ((_cmp_cached_21) | (_cmp_cached_58) | (_cmp_cached_23))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_19) | (_cmp("RSI_3_1d", ">", 50.0)) | (_cmp_cached_38))
            # 4h down move, 1h high, 1h downtrend
            & ((_cmp_cached_19) | (_cmp_cached_12) | (_cmp("ROC_9_1h", ">", -10.0)))
            # 4h down move, 1h high, 4h downtrend
            & ((_cmp_cached_19) | (_cmp_cached_12) | (_cmp_cached_102))
            # 4h down move, 1h still high, 1d overbought
            & ((_cmp_cached_19) | (_cmp_cached_82) | (_cmp_cached_51))
            # 4h & 1d down move, 1d overbought
            & ((_cmp_cached_41) | (_cmp("RSI_3_1d", ">", 50.0)) | (_cmp_cached_29))
            # 4h down move, 4h & 1d high
            & ((_cmp_cached_41) | (_cmp_cached_20) | (_cmp_cached_9))
            # 4h down move, 4h high, 1d downtrend
            & ((_cmp_cached_76) | (_cmp_cached_13) | (_cmp_cached_23))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_47) | (_cmp("RSI_3_1d", ">", 60.0)) | (_cmp_cached_9))
            # 4h down move, 4h high, 1d downtrend
            & ((_cmp_cached_47) | (_cmp_cached_58) | (_cmp_cached_146))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_76) | (_cmp_cached_45) | (_cmp_cached_39))
            # 4h down move, 4h high & overbought
            & ((_cmp_cached_76) | (_cmp_cached_105) | (_cmp_cached_26))
            # 4h down move, 4h high, 1d overbought
            & ((_cmp_cached_76) | (_cmp_cached_34) | (_cmp_cached_78))
            # 4h down move, 4h high & overbought
            & ((_cmp_cached_60) | (_cmp_cached_20) | (_cmp_cached_27))
            # 4h down move, 1h high, 1d downtrend
            & ((_cmp_cached_60) | (_cmp_cached_37) | (_cmp_cached_23))
            # 4h down move, 4h high & overbought
            & ((_cmp_cached_131) | (_cmp_cached_13) | (_cmp_cached_26))
            # 4h down move, 4h high, 1d overbought
            & ((_cmp_cached_131) | (_cmp_cached_13) | (_cmp_cached_29))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_131) | (_cmp_cached_38) | (_cmp_cached_99))
            # 4h down move, 4h & 1d high
            & ((_cmp_cached_87) | (_cmp_cached_13) | (_cmp_cached_45))
            # 4h down move, 1d high, 4h overbought
            & ((_cmp_cached_87) | (_cmp_cached_9) | (_cmp_cached_27))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_87) | (_cmp_cached_9) | (_cmp_cached_74))
            # 4h down move, 4h still high, 4h overbought
            & ((_cmp_cached_87) | (_cmp_cached_54) | (_cmp_cached_27))
            # 4h down move, 4h high, 1d overbought
            & ((_cmp("RSI_3_4h", ">", 65.0)) | (_cmp("AROONU_14_4h", "<", 75.0)) | (_cmp_cached_51))
            # 4h down move, 4h high & overbought
            & ((_cmp("RSI_3_4h", ">", 65.0)) | (_cmp_cached_20) | (_cmp_cached_26))
            # 1d down move, 1d still not low enough, 1d downtrend
            & ((_cmp("RSI_3_1d", ">", 5.0)) | (_cmp("AROONU_14_1d", "<", 20.0)) | (_cmp_cached_15))
            # 1d down move, 15m still high
            & ((_cmp("RSI_3_1d", ">", 5.0)) | (_cmp_cached_113))
            # 1d down move, 1h high
            & ((_cmp_cached_66) | (_cmp_cached_12))
            # 1d down move, 4h downtrend, 4h high
            & ((_cmp_cached_53) | (_cmp("CMF_20_4h", ">", -0.25)) | (_cmp_cached_13))
            # 1d down move, 1d still high, 1d downtrend
            & ((_cmp_cached_64) | (_cmp_cached_117) | (_cmp_cached_15))
            # 1d down move, 4h & 1d high
            & ((_cmp_cached_118) | (_cmp_cached_13) | (_cmp_cached_9))
            # 1d down move, 1d high & overbought
            & ((_cmp_cached_118) | (_cmp_cached_42) | (_cmp_cached_78))
            # 1d down move, 1h high, 1d overbought
            & ((_cmp("RSI_3_1d", ">", 60.0)) | (_cmp_cached_12) | (_cmp_cached_29))
            # 4h downtrend, 4h high & over
            & ((_cmp("CMF_20_4h", ">", -0.10)) | (_cmp_cached_14) | (_cmp_cached_50))
            # 15m still high, 4h high, 1h overbought
            & ((_cmp_cached_81) | (_cmp_cached_93) | (_cmp_cached_85))
            # 15m still high, 4h high, 1h overbought
            & ((_cmp_cached_81) | (_cmp_cached_14) | (_cmp_cached_85))
            # 4h down move, 1h still high, 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_86) | (_cmp_cached_95))
            # 1h high, 4h high & overbought
            & ((_cmp_cached_18) | (_cmp_cached_20) | (_cmp_cached_50))
            # 1h & 4h high, 1h overbought
            & ((_cmp_cached_18) | (_cmp_cached_32) | (_cmp_cached_129))
            # 1h & 4h & 1d high
            & ((_cmp_cached_18) | (_cmp_cached_14) | (_cmp_cached_9))
            # 1h & 4h high, 1d overbought
            & ((_cmp_cached_18) | (_cmp_cached_14) | (_cmp_cached_51))
            # 1h high, 1h overbought
            & ((_cmp_cached_18) | (_cmp_cached_61))
            # 1h & 1d high, 4h overbought
            & ((_cmp_cached_18) | (_cmp_cached_9) | (_cmp_cached_27))
            # 1h high, 1h & 4h overbought
            & ((_cmp_cached_18) | (_cmp_cached_61) | (_cmp_cached_27))
            # 1h high, 1h overbought, 1d downtrend
            & ((_cmp_cached_18) | (_cmp("ROC_9_1h", "<", 50.0)) | (_cmp_cached_95))
            # 1h high, 4h &1d overbought
            & ((_cmp_cached_92) | (_cmp_cached_50) | (_cmp_cached_51))
            # 1h high, 4h & 1d overbought
            & ((_cmp_cached_52) | (_cmp_cached_27) | (_cmp("ROC_9_1d", "<", 15.0)))
            # 4h & 1d high, 4h overbought
            & ((_cmp_cached_13) | (_cmp_cached_9) | (_cmp_cached_98))
            # 4h & 1d high, 1d overbought
            & ((_cmp_cached_13) | (_cmp_cached_9) | (_cmp_cached_39))
            # 4h & 1d high, 4h overbought
            & ((_cmp_cached_32) | (_cmp_cached_9) | (_cmp_cached_50))
            # 4h high, 4h overbought, 1d downtrend
            & ((_cmp_cached_32) | (_cmp_cached_26) | (_cmp_cached_44))
            # 1d high, 4h & 1d overbought
            & ((_cmp_cached_45) | (_cmp_cached_50) | (_cmp_cached_74))
            # 1d high, 1h & 1d overbought
            & ((_cmp_cached_42) | (_cmp_cached_85) | (_cmp_cached_35))
            # 1d high, 1d downtrend
            & ((_cmp_cached_42) | (_cmp_cached_23))
            # 1d high, 1h & 4h downtrend
            & ((_cmp_cached_103) | (_cmp_cached_124) | (_cmp("ROC_9_4h", ">", -50.0)))
            # 1d high, 1h & 1d overbought
            & ((_cmp_cached_38) | (_cmp_cached_61) | (_cmp_cached_35))
            # 1d high, 4h & 1d overbought
            & ((_cmp_cached_9) | (_cmp_cached_27) | (_cmp_cached_39))
            # 15m still not low enough, 4h high, 1d overbought
            & ((_cmp_cached_125) | (_cmp_cached_14) | (_cmp_cached_51))
            # 15m still high, 4h high & overbought
            & (
              (_cmp_cached_113) | (_cmp_cached_34) | (_cmp_cached_50)
            )
            # 1h high, 1d overbought
            & ((_cmp_cached_56) | (_cmp_cached_40))
            # 1h high, 1h overbought, 4h downtrend
            & ((_cmp_cached_37) | (_cmp_cached_61) | (_cmp_cached_102))
            # 1h high, 4h & 1d downtrend
            & ((_cmp_cached_37) | (_cmp_cached_31) | (_cmp("ROC_9_1d", ">", -80.0)))
            # 1h down move, 1h & 1d overbought
            & ((_cmp_cached_83) | (_cmp_cached_61) | (_cmp_cached_35))
            # 1h high & overbought
            & ((_cmp_cached_83) | (_cmp_cached_134))
            # 4h high, 1h & 4h overbought
            & ((_cmp_cached_58) | (_cmp_cached_61) | (_cmp_cached_26))
            # 4h high, 1h & 1d overbought
            & ((_cmp_cached_58) | (_cmp_cached_85) | (_cmp_cached_74))
            # 4h high, 4h & 1d overbought
            & ((_cmp_cached_34) | (_cmp_cached_50) | (_cmp_cached_51))
            # 4h high, 1d downtrend
            & ((_cmp_cached_34) | (_cmp_cached_95))
            # 4h high, 1h & 1d overbought
            & ((_cmp_cached_55) | (_cmp_cached_85) | (_cmp_cached_39))
            # 4h high, 4h & 1d overbought
            & ((_cmp_cached_55) | (_cmp_cached_27) | (_cmp_cached_78))
            # 1d hihg, 1h & 1d overbought
            & ((_cmp_cached_62) | (_cmp_cached_129) | (_cmp_cached_29))
            # 1d P&D, dh downtrend
            & ((_cmp("change_pct_1d", ">", -50.0)) | (df["change_pct_1d"].shift(288) < 50.0) | (_cmp_cached_5))
            # big drop in the last 20 days, 1d high, 1d downtrend
            & (
              _gt_mul("close", "high_max_20_1d", 0.20)
              | (_cmp_cached_106)
              | (_cmp_cached_141)
            )
            # drop in last 20 days, 1h high, 1d downtrend
            & (_gt_mul("close", "high_max_20_1d", 0.20) | (_cmp_cached_12) | (_cmp_cached_150))
            # drop in last 20 days. 4h high
            & (_gt_mul("close", "high_max_20_1d", 0.10) | (_cmp_cached_55))
          )

          # Logic
          long_entry_logic.append(
            _rsi_20_falling
            & (_cmp("RSI_3", "<", 46.0))
            & (_cmp("AROONU_14", "<", 25.0))
            & (_cmp("STOCHRSIk_14_14_3_3", "<", 20.0))
            & (_cmp_cached_46)
            & (df["close"] < df["SMA_16"] * 0.960)
          )

        # Condition #21 - Pump mode (Long).
        if long_entry_condition_index == 21:
          # Protections
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          # long_entry_logic.append(df["protections_long_global"] == True)

          long_entry_logic.append(
            # 5m down move, 4h high, 1h overbought
            ((_cmp_cached_143) | (_cmp_cached_14) | (_cmp_cached_129))
            # 15m down move, 1h & 4h overbought
            & ((_cmp_cached_17) | (_cmp("ROC_9_1h", "<", 25.0)) | (_cmp_cached_98))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_10) | (_cmp_cached_69))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_0) | (_cmp_cached_25) | (_cmp_cached_18))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_0) | (_cmp_cached_25) | (_cmp_cached_37))
            # 15m & 1h down move, 4h overbought
            & ((_cmp_cached_0) | (_cmp_cached_65) | (_cmp_cached_98))
            # 15m & 1h down move, 4h overbought
            & ((_cmp_cached_0) | (_cmp_cached_97) | (_cmp("ROC_9_4h", "<", 70.0)))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_131) | (_cmp_cached_32))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_0) | (_cmp_cached_14) | (_cmp_cached_114))
            # 15m down move, 1h high, 1d downtrend
            & ((_cmp_cached_0) | (_cmp_cached_56) | (_cmp_cached_95))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_0) | (_cmp_cached_34) | (_cmp_cached_50))
            # 15m down move, 1d high, 1d downtrend
            & ((_cmp_cached_0) | (_cmp_cached_106) | (_cmp_cached_141))
            # 15m & 1h down move, 4h overbought
            & ((_cmp_cached_3) | (_cmp_cached_25) | (_cmp_cached_115))
            # 15m & 1d down move, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_133) | (_cmp_cached_52))
            # 15m down move, 15m still high, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_81) | (_cmp_cached_14))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_3) | (_cmp_cached_86) | (_cmp_cached_14))
            # 15m down move, 1h high, 4h overbought
            & ((_cmp_cached_3) | (_cmp_cached_88) | (_cmp_cached_114))
            # 15m down move, 4h high, 4h downtrend
            & ((_cmp_cached_3) | (_cmp_cached_32) | (_cmp("CMF_20_4h", ">", -0.25)))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_3) | (_cmp_cached_129) | (_cmp_cached_98))
            # 15m down move, 4h & 1d overbought
            & ((_cmp_cached_3) | (_cmp_cached_123) | (_cmp_cached_69))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_16) | (_cmp_cached_88) | (_cmp_cached_14))
            # 15m down move, 4h high, 1h overbought
            & ((_cmp_cached_16) | (_cmp_cached_34) | (_cmp_cached_61))
            # 15m down move, 4h & 1d overbought
            & ((_cmp_cached_16) | (_cmp_cached_114) | (_cmp_cached_74))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_28) | (_cmp_cached_11) | (_cmp_cached_69))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_28) | (_cmp_cached_130) | (_cmp_cached_52))
            # 15m down move, 15m still high, 1d downtrend
            & ((_cmp_cached_28) | (_cmp_cached_81) | (_cmp_cached_149))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_28) | (_cmp_cached_52) | (_cmp_cached_14))
            # 15m down move, 4h high, 1h overbought
            & ((_cmp_cached_28) | (_cmp_cached_14) | (_cmp_cached_85))
            # 15m down move, 4h high, 1d overbought
            & ((_cmp_cached_28) | (_cmp_cached_14) | (_cmp_cached_29))
            # 15m down move, 1h high & overbought
            & ((_cmp_cached_28) | (_cmp_cached_83) | (_cmp_cached_85))
            # 15m down move, 1h & 4h overbought
            & ((_cmp_cached_28) | (_cmp_cached_134) | (_cmp_cached_73))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_70) | (_cmp_cached_55) | (_cmp("ROC_9_4h", "<", 200.0)))
            # 15m down move, 1h & 4h overbought
            & ((_cmp_cached_70) | (_cmp("ROC_9_1h", "<", 60.0)) | (_cmp_cached_114))
            # 15m down move, 4h & 1d overbought
            & ((_cmp_cached_140) | (_cmp_cached_115) | (_cmp_cached_29))
            # 1h down move, 4h overbought, 1d downtrend
            & ((_cmp_cached_2) | (_cmp_cached_98) | (_cmp_cached_23))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_10) | (_cmp_cached_98) | (_cmp_cached_20))
            # 1h & 4h down move, 1h still high
            & ((_cmp_cached_10) | (_cmp_cached_98) | (_cmp_cached_82))
            # 1h & 4h down move, 4h overbought
            & ((_cmp_cached_10) | (_cmp_cached_98) | (_cmp_cached_27))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_10) | (_cmp_cached_18) | (_cmp_cached_14))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_10) | (_cmp_cached_20) | (_cmp_cached_27))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_10) | (_cmp_cached_14) | (_cmp_cached_98))
            # 1h down move, 1h still high, 1d overbought
            & ((_cmp_cached_10) | (_cmp_cached_82) | (_cmp_cached_27))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_10) | (_cmp_cached_73) | (_cmp_cached_29))
            # 1h down move, 1d high, 4h overbought
            & ((_cmp_cached_11) | (_cmp_cached_9) | (_cmp_cached_123))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_8) | (_cmp_cached_20) | (_cmp_cached_50))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_25) | (_cmp_cached_18) | (_cmp_cached_44))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_25) | (_cmp_cached_34) | (_cmp_cached_95))
            # 1h down move, 1h & 1d overbought
            & ((_cmp_cached_33) | (_cmp_cached_129) | (_cmp_cached_99))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_65) | (_cmp_cached_18) | (_cmp("ROC_9_4h", "<", 25.0)))
            # 1h down move, 4h high, 1h overbought
            & ((_cmp_cached_65) | (_cmp_cached_32) | (_cmp_cached_85))
            # 1h down move, 4h high, 1h overbought
            & ((_cmp_cached_65) | (_cmp_cached_14) | (_cmp_cached_61))
            # 1h down move, 1d high, 1d downtrend
            & ((_cmp_cached_65) | (_cmp_cached_9) | (_cmp_cached_149))
            # 1h down move, 1h high & overbought
            & ((_cmp_cached_63) | (_cmp_cached_52) | (_cmp_cached_61))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_63) | (_cmp_cached_56) | (_cmp_cached_15))
            # 1h down move, 1h & 1d overbought
            & ((_cmp_cached_63) | (_cmp("ROC_9_1h", "<", 25.0)) | (_cmp_cached_74))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_130) | (_cmp_cached_12) | (_cmp_cached_73))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_130) | (_cmp_cached_93) | (_cmp_cached_114))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_97) | (_cmp_cached_20) | (_cmp_cached_115))
            # 1h down move, 1h & 1d overbought
            & ((_cmp_cached_97) | (_cmp_cached_61) | (_cmp("ROC_9_1d", "<", 250.0)))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp("RSI_3_1h", ">", 65.0)) | (_cmp_cached_18) | (_cmp_cached_50))
            # 1h down move, 1h overbought
            & ((_cmp("RSI_3_1h", ">", 65.0)) | (_cmp_cached_134))
            # 4h down move, 1h high & overbought
            & ((_cmp_cached_80) | (_cmp_cached_92) | (_cmp("ROC_9_1h", "<", 60.0)))
            # 1d down move, 4h high & overbought
            & ((_cmp("RSI_3_1d", ">", 5.0)) | (_cmp_cached_32) | (_cmp_cached_98))
            # 1d down move, 1h high
            & ((_cmp_cached_66) | (_cmp_cached_12))
            # 1d down move, 4h high, 1h overbought
            & ((_cmp_cached_53) | (_cmp_cached_14) | (_cmp("ROC_9_1h", "<", 25.0)))
            # 1d down move, 4h high, 4h overbought
            & ((_cmp_cached_53) | (_cmp_cached_14) | (_cmp_cached_73))
            # 1d down move, 1h & 4h overbought
            & ((_cmp_cached_77) | (_cmp_cached_129) | (_cmp_cached_123))
            # 1d down move, 4h high & overbought
            & ((_cmp_cached_133) | (_cmp_cached_14) | (_cmp_cached_26))
            # 1d down move, 1h & 4h high
            & ((_cmp_cached_118) | (_cmp_cached_18) | (_cmp_cached_14))
            # 1d down move, 4h & 1d high
            & ((_cmp_cached_118) | (_cmp_cached_13) | (_cmp_cached_9))
            # 1d down move, 4h high & overbought
            & ((_cmp_cached_107) | (_cmp_cached_20) | (_cmp_cached_50))
            # 1d down move, 1h high, 1d overbought
            & ((_cmp("RSI_3_1d", ">", 60.0)) | (_cmp("AROONU_14_1h", "<", 75.0)) | (_cmp_cached_39))
            # 1d down move, 1h & 4h high
            & ((_cmp("RSI_3_1d", ">", 65.0)) | (_cmp_cached_52) | (_cmp_cached_14))
            # 1d downtrend, 1d high & overbought
            & ((_cmp("CMF_20_1d", ">", -0.40)) | (_cmp_cached_103) | (_cmp_cached_39))
            # 15m not low enough, 1h high, 1d overbought
            & ((_cmp("AROONU_14_15m", "<", 25.0)) | (_cmp_cached_83) | (_cmp_cached_74))
            # 1h still high, 1h & 4h overbought
            & ((_cmp_cached_49) | (_cmp_cached_134) | (_cmp_cached_73))
            # 1h & 4h high, 4h overbought
            & ((_cmp_cached_12) | (_cmp_cached_14) | (_cmp_cached_26))
            # 1h & 4h high, 4h overbought
            & ((_cmp_cached_18) | (_cmp_cached_20) | (_cmp_cached_50))
            # 1h & 4h high, 1h overbought
            & ((_cmp_cached_18) | (_cmp_cached_32) | (_cmp_cached_129))
            # 1h & 4h high, 1d overbought
            & ((_cmp_cached_18) | (_cmp_cached_32) | (_cmp_cached_29))
            # 1h & 1d high, 4h overbought
            & ((_cmp_cached_52) | (_cmp_cached_38) | (_cmp_cached_50))
            # 1h & 4h high, 1h overbought
            & ((_cmp_cached_18) | (_cmp_cached_55) | (_cmp_cached_61))
            # 1h high & overbought
            & ((_cmp_cached_18) | (_cmp("ROC_9_1h", "<", 80.0)))
            # 1h high, 1h & 4h overbought
            & ((_cmp_cached_18) | (_cmp_cached_61) | (_cmp_cached_27))
            # 1h high, 4h overbought, 1d downtrend
            & ((_cmp_cached_18) | (_cmp_cached_27) | (_cmp_cached_95))
            # 1h & 4h high, 15m downtrend
            & ((_cmp_cached_92) | (_cmp_cached_93) | (_cmp("ROC_9_15m", ">", -40.0)))
            # 1h & 4h high, 1h overbought
            & ((_cmp_cached_52) | (_cmp_cached_32) | (_cmp_cached_61))
            # 4h high, 1h overbought, 1d downtrend
            & ((_cmp_cached_20) | (_cmp_cached_129) | (_cmp_cached_23))
            # 4h & 1d high, 4h downtrend
            & ((_cmp_cached_93) | (_cmp_cached_9) | (_cmp("CMF_20_4h", ">", -0.30)))
            # 4h & 1d high, 1h overbought
            & ((_cmp_cached_93) | (_cmp_cached_38) | (_cmp_cached_85))
            # 4h & 1d high, 4h overbought
            & ((_cmp_cached_93) | (_cmp_cached_38) | (_cmp_cached_123))
            # 4h high, 1h & 4h overbought
            & ((_cmp_cached_93) | (_cmp_cached_61) | (_cmp_cached_26))
            # 4h high, 1d high & overbought
            & ((_cmp_cached_32) | (_cmp_cached_9) | (_cmp_cached_51))
            # 4h high, 1h & 4h overbought
            & ((_cmp_cached_32) | (_cmp_cached_134) | (_cmp_cached_73))
            # 4h high, 4h & 1d overbought
            & ((_cmp_cached_32) | (_cmp_cached_50) | (_cmp_cached_29))
            # 4h high, 1h & 4h overbought
            & ((_cmp_cached_14) | (_cmp_cached_134) | (_cmp_cached_114))
            # 1d high, 1h & 4h overbought
            & ((_cmp_cached_9) | (_cmp_cached_61) | (_cmp_cached_26))
            # 1h high, 1h & 4h overbought
            & ((_cmp_cached_112) | (_cmp_cached_134) | (_cmp_cached_73))
            # 1h high, 1h overbought
            & ((_cmp_cached_37) | (_cmp_cached_61))
            # 1h high, 4h overbought. 1d downtrend
            & ((_cmp_cached_37) | (_cmp_cached_73) | (_cmp("CMF_20_1d", ">", -0.25)))
            # 4h high, 1h & 4h overbought
            & ((_cmp_cached_55) | (_cmp_cached_61) | (_cmp_cached_26))
            # 4h high & 4h & 1d overbought
            & ((_cmp_cached_55) | (_cmp_cached_26) | (_cmp_cached_39))
            # 1d high, 1h & 4h overbought
            & ((_cmp_cached_84) | (_cmp_cached_61) | (_cmp_cached_26))
            # 1d hihg, 1h & 1d overbought
            & ((_cmp_cached_62) | (_cmp_cached_129) | (_cmp_cached_29))
            # 1d high, 4h & 1d overbought
            & ((_cmp_cached_62) | (_cmp_cached_73) | (_cmp_cached_29))
          )

          # Logic
          long_entry_logic.append(
            (_cmp("AROONU_14", "<", 25.0))
            & (_cmp("STOCHRSIk_14_14_3_3", "<", 20.0))
            & (_cmp_cached_46)
            & (df["close"] < df["EMA_16"] * 0.960)
            & (((df["EMA_50"] - df["EMA_200"]) / df["close"] * 100.0) > 6.0)
          )

        # Condition #41 - Quick mode (Long).
        if long_entry_condition_index == 41:
          # Protections
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          # long_entry_logic.append(df["protections_long_global"] == True)

          long_entry_logic.append(
            # 5m & 1d down move, 4h still high
            ((_cmp("RSI_3", ">", 15.0)) | (_cmp_cached_77) | (_cmp_cached_67))
            # 15m & 1h down move, 1d still high
            & ((_cmp_cached_7) | (_cmp_cached_36) | (_cmp_cached_117))
            # 15m & 1h down move, 1h still not low enough
            & ((_cmp_cached_7) | (_cmp_cached_22) | (_cmp_cached_109))
            # 15m & 1h down move, 15m downtrend
            & ((_cmp_cached_7) | (_cmp_cached_1) | (_cmp("CMF_20_15m", ">", -0.40)))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_7) | (_cmp_cached_1) | (_cmp_cached_20))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_7) | (_cmp_cached_1) | (_cmp_cached_82))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_7) | (_cmp_cached_1) | (_cmp_cached_105))
            # 15m & 1h down move, 1d downtrend
            & ((_cmp_cached_7) | (_cmp_cached_2) | (_cmp_cached_15))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_7) | (_cmp_cached_10) | (_cmp_cached_49))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_7) | (_cmp_cached_11) | (_cmp_cached_88))
            # 15m & 1h down move, 1d still high
            & ((_cmp_cached_7) | (_cmp_cached_8) | (_cmp_cached_121))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_7) | (_cmp_cached_8) | (_cmp_cached_56))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_7) | (_cmp_cached_8) | (_cmp_cached_30))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_7) | (_cmp_cached_8) | (_cmp_cached_62))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_7) | (_cmp_cached_65) | (_cmp_cached_92))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_7) | (_cmp_cached_65) | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 75.0)))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_7) | (_cmp_cached_57) | (_cmp_cached_20))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_7) | (_cmp_cached_47) | (_cmp_cached_54))
            # 15m down move, 15m still high, 1d downtrend
            & ((_cmp_cached_7) | (_cmp_cached_46) | (_cmp_cached_15))
            # 15m down move, 1h still high, 1d high
            & ((_cmp_cached_7) | (_cmp_cached_49) | (_cmp_cached_45))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_7) | (_cmp_cached_18) | (_cmp_cached_20))
            # 15m down move, 4h & 1d high
            & ((_cmp_cached_7) | (_cmp_cached_20) | (_cmp_cached_9))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_7) | (_cmp_cached_37) | (_cmp_cached_34))
            # 15m down move, 1h high, 4h overbought
            & ((_cmp_cached_7) | (_cmp_cached_83) | (_cmp_cached_27))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_7) | (_cmp_cached_34) | (_cmp_cached_27))
            # 15m down move, 4h & 1d downtrend
            & ((_cmp_cached_7) | (_cmp_cached_31) | (_cmp_cached_15))
            # 15m & 1h down move, 1d downtrend
            & ((_cmp_cached_17) | (_cmp_cached_22) | (_cmp_cached_142))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_17) | (_cmp_cached_1) | (_cmp_cached_42))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_17) | (_cmp_cached_1) | (_cmp_cached_34))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_17) | (_cmp_cached_8) | (_cmp_cached_12))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_17) | (_cmp_cached_8) | (_cmp_cached_13))
            # 15m & 4h down move, 1h still high
            & ((_cmp_cached_17) | (_cmp_cached_57) | (_cmp_cached_30))
            # 15m & 4h down move, 1d downtrend
            & ((_cmp_cached_17) | (_cmp_cached_4) | (_cmp_cached_15))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_17) | (_cmp_cached_6) | (_cmp_cached_37))
            # 15m & 4h down move, 1d downtrend
            & ((_cmp_cached_17) | (_cmp_cached_21) | (_cmp_cached_150))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_17) | (_cmp_cached_71) | (_cmp_cached_14))
            # 15m down move, 1h still high, 1d downtrend
            & ((_cmp_cached_17) | (_cmp_cached_30) | (_cmp_cached_44))
            # 5m down move, 4h high, 1d downtrend
            & ((_cmp_cached_17) | (_cmp_cached_34) | (_cmp_cached_44))
            # 15m down move, 1h & 4h overbought
            & ((_cmp_cached_17) | (_cmp("ROC_9_1h", "<", 25.0)) | (_cmp("ROC_9_4h", "<", 25.0)))
            # 15m down move, 4h & 1d overbought
            & ((_cmp_cached_17) | (_cmp_cached_50) | (_cmp_cached_29))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_0) | (_cmp_cached_1) | (_cmp_cached_12))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_0) | (_cmp_cached_1) | (_cmp_cached_106))
            # 15m & 1h down move, 1d downtrend
            & ((_cmp_cached_0) | (_cmp_cached_1) | (_cmp_cached_23))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_0) | (_cmp_cached_2) | (_cmp_cached_18))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_2) | (_cmp_cached_14))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_2) | (_cmp_cached_58))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_0) | (_cmp_cached_10) | (_cmp_cached_30))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_11) | (_cmp_cached_39))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_8) | (_cmp_cached_51))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_0) | (_cmp_cached_33) | (_cmp_cached_52))
            # 15m & 1d down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_64) | (_cmp_cached_14))
            # 15m & 1d down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_64) | (_cmp_cached_34))
            # 15m down move, 15m still high, 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_46) | (_cmp_cached_51))
            # 15m down move, 15m high
            & ((_cmp_cached_0) | (_cmp_cached_24))
            # 15m down move, 1h high, 15m downtrend
            & ((_cmp_cached_0) | (_cmp_cached_18) | (_cmp("ROC_9_15m", ">", -10.0)))
            # 15m down move, 1h high, 1d downtrend
            & ((_cmp_cached_0) | (_cmp_cached_18) | (_cmp_cached_23))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_92) | (_cmp_cached_40))
            # 15m down move, 1h & 1d high
            & ((_cmp_cached_0) | (_cmp_cached_52) | (_cmp_cached_9))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_0) | (_cmp_cached_71) | (_cmp_cached_14))
            # 15m down move, 4h high, 1h downtrend
            & ((_cmp_cached_0) | (_cmp_cached_93) | (_cmp("ROC_9_1h", ">", -25.0)))
            # 15m down move, 4h & 1d high
            & ((_cmp_cached_0) | (_cmp_cached_32) | (_cmp_cached_9))
            # 15m down move, 4h high, 15m downtrend
            & ((_cmp_cached_0) | (_cmp("AROONU_14_4h", "<", 100.00)) | (_cmp("ROC_9_15m", ">", -30.0)))
            # 15m down move, 1h high & overbought
            & ((_cmp_cached_0) | (_cmp_cached_9) | (_cmp_cached_99))
            # 15m down move, 1d high, 1d downtrend
            & ((_cmp_cached_0) | (_cmp_cached_103) | (_cmp("CMF_20_1d", ">", -0.40)))
            # 15m down move, 1h high, 15m downtrend
            & ((_cmp_cached_0) | (_cmp_cached_37) | (_cmp("ROC_9_15m", ">", -10.0)))
            # 15m down move, 1h high, 1d downtrend
            & ((_cmp_cached_0) | (_cmp_cached_83) | (_cmp_cached_23))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_83) | (_cmp_cached_51))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_0) | (_cmp_cached_55) | (_cmp_cached_26))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_3) | (_cmp_cached_2) | (_cmp_cached_51))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_3) | (_cmp_cached_10) | (_cmp_cached_38))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_25) | (_cmp_cached_18))
            # 15m & 1d down move, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_53) | (_cmp_cached_55))
            # 15m & 1d down move, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_64) | (_cmp_cached_14))
            # 15m & 1d down move, 1d high
            & ((_cmp_cached_3) | (_cmp("RSI_3_1d", ">", 50.0)) | (_cmp_cached_42))
            # 15m down move, 15m still high, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_46) | (_cmp_cached_52))
            # 15m down move, 15m still high, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_46) | (_cmp_cached_37))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_3) | (_cmp_cached_18) | (_cmp_cached_14))
            # 15m down move, 4h high, 4h downtrend
            & ((_cmp_cached_3) | (_cmp_cached_68) | (_cmp_cached_31))
            # 15m down move, 4h & 1d high
            & ((_cmp_cached_3) | (_cmp_cached_20) | (_cmp_cached_9))
            # 15m down move, 1h high, 4h downtrend
            & ((_cmp_cached_3) | (_cmp_cached_56) | (_cmp_cached_72))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_3) | (_cmp_cached_34) | (_cmp_cached_27))
            # 15m down move, 4h high, 1d downtrend
            & ((_cmp_cached_3) | (_cmp_cached_34) | (_cmp_cached_95))
            # 15m down move, 1d high, 4h overbought
            & ((_cmp_cached_3) | (_cmp_cached_62) | (_cmp_cached_73))
            # 15m down move, 1h downtrend, 4h overbought
            & ((_cmp_cached_3) | (_cmp_cached_120) | (_cmp_cached_114))
            # 15m down move, 4h & 1d downtrend
            & ((_cmp_cached_3) | (_cmp_cached_102) | (_cmp_cached_44))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_16) | (_cmp_cached_10) | (_cmp_cached_12))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_16) | (_cmp_cached_10) | (_cmp_cached_35))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_16) | (_cmp_cached_11) | (_cmp_cached_9))
            # 15m &4h down move, 4h still high
            & ((_cmp_cached_16) | (_cmp_cached_6) | (_cmp_cached_43))
            # 15m & 4h down move, 1d overbought
            & ((_cmp_cached_16) | (_cmp_cached_19) | (_cmp_cached_35))
            # 15m down move, 15m high, 1d overbought
            & ((_cmp_cached_16) | (_cmp_cached_24) | (_cmp_cached_40))
            # 15m down move, 1h high, 4h downtrend
            & ((_cmp_cached_16) | (_cmp_cached_18) | (_cmp("ROC_9_4h", ">", -15.0)))
            # 15m down move, 1h high & overbought
            & ((_cmp_cached_16) | (_cmp_cached_71) | (_cmp("ROC_9_1h", "<", 50.0)))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_16) | (_cmp_cached_13) | (_cmp_cached_26))
            # 15m down move, 4h high, 1d overbought
            & ((_cmp_cached_16) | (_cmp_cached_20) | (_cmp_cached_99))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_28) | (_cmp_cached_21) | (_cmp_cached_105))
            # 15m & 1d down move, 1h high
            & ((_cmp_cached_28) | (_cmp_cached_64) | (_cmp_cached_52))
            # 15m down move, 15m high, 1h high
            & ((_cmp_cached_70) | (_cmp_cached_90) | (_cmp_cached_52))
            # 15m down move, 15m high, 4h downtrend
            & ((_cmp_cached_28) | (_cmp_cached_90) | (_cmp_cached_31))
            # 15m down move, 1h high, 4h overbought
            & ((_cmp_cached_28) | (_cmp_cached_52) | (_cmp_cached_50))
            # 15m down move, 1h high, 4h overbought
            & ((_cmp_cached_28) | (_cmp_cached_71) | (_cmp("ROC_9_4h", "<", 15.0)))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_28) | (_cmp_cached_71) | (_cmp_cached_39))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_70) | (_cmp_cached_52) | (_cmp_cached_32))
            # 1h & 4h down move, 1d still high
            & ((_cmp_cached_36) | (_cmp_cached_80) | (_cmp_cached_117))
            # 1h & 4h down move, 1h still high
            & ((_cmp_cached_36) | (_cmp_cached_21) | (_cmp_cached_86))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_36) | (_cmp_cached_76) | (_cmp_cached_58))
            # 1h down move, 15m & 1h downtrend
            & ((_cmp_cached_36) | (_cmp("CMF_20_15m", ">", -0.30)) | (_cmp("CMF_20_1h", ">", -0.30)))
            # 1h down move, 1h still high, 1h downtrend
            & ((_cmp_cached_36) | (_cmp_cached_49) | (_cmp_cached_120))
            # 1h down move, 1h high
            & ((_cmp_cached_36) | (_cmp_cached_12))
            # 1h down move, 4h high
            & ((_cmp_cached_36) | (_cmp_cached_13))
            # 1h down move, 1d high
            & ((_cmp_cached_36) | (_cmp_cached_45))
            # 1h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_36) | (_cmp_cached_54) | (_cmp_cached_120))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_36) | (_cmp("STOCHRSIk_14_14_3_3_1d", "<", 60.0)) | (_cmp_cached_39))
            # 1h & 4h & 1d down move
            & ((_cmp_cached_22) | (_cmp_cached_4) | (_cmp_cached_53))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_22) | (_cmp_cached_4) | (_cmp_cached_29))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_22) | (_cmp_cached_5) | (_cmp("AROONU_14_4h", "<", 20.0)))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_22) | (_cmp_cached_19) | (_cmp_cached_110))
            # 1h & 4h down move, 1h downtrend
            & ((_cmp_cached_22) | (_cmp_cached_19) | (_cmp("CMF_20_1h", ">", -0.30)))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_22) | (_cmp_cached_60) | (_cmp_cached_13))
            # 1h & 1d down move, 1h still high
            & ((_cmp_cached_22) | (_cmp_cached_66) | (_cmp_cached_30))
            # 1h down move, 1d high, 1h downtrend
            & ((_cmp_cached_22) | (_cmp_cached_103) | (_cmp("ROC_9_1h", ">", -50.0)))
            # 1h down move, 1d high, 4h downtrend
            & ((_cmp_cached_22) | (_cmp_cached_38) | (_cmp_cached_72))
            # 1h down move, 1d high, 1d downtrend
            & ((_cmp_cached_22) | (_cmp_cached_9) | (_cmp_cached_15))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_22) | (_cmp_cached_9) | (_cmp_cached_39))
            # 1h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_22) | (_cmp_cached_54) | (_cmp_cached_95))
            # 1h down move, 4h & 1d downtrend
            & ((_cmp_cached_22) | (_cmp("ROC_9_4h", ">", -25.0)) | (_cmp_cached_95))
            # 1h & 4h & 1d down move
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp_cached_59))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp_cached_18))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp_cached_42))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp_cached_54))
            # 1h & 4h down move, 1d still not low enough
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp("STOCHRSIk_14_14_3_3_1d", "<", 20.0)))
            # 1h & 4h down move, 4h downtrend
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp("ROC_9_4h", ">", -35.0)))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp_cached_15))
            # 1h & 4h down move, 15m downtrend
            & ((_cmp_cached_1) | (_cmp_cached_5) | (_cmp("ROC_9_15m", ">", -20.0)))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_1) | (_cmp_cached_6) | (_cmp_cached_54))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_6) | (_cmp_cached_23))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_1) | (_cmp_cached_21) | (_cmp_cached_32))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_1) | (_cmp_cached_21) | (_cmp_cached_42))
            # 1h & 1d down move, 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_66) | (_cmp_cached_23))
            # 1h & 1d down move, 4h still high
            & ((_cmp_cached_1) | (_cmp_cached_66) | (_cmp_cached_67))
            # 1h & 1d down move, 4h high
            & ((_cmp_cached_1) | (_cmp_cached_59) | (_cmp_cached_58))
            # 1h & 1d down move, 1h still not low enough
            & ((_cmp_cached_1) | (_cmp_cached_53) | (_cmp_cached_132))
            # 1h & 1d down move, 1h high
            & ((_cmp_cached_1) | (_cmp_cached_64) | (_cmp_cached_12))
            # 1h & 1d down move, 1h downtrend
            & ((_cmp_cached_1) | (_cmp_cached_77) | (_cmp("CMF_20_1h", ">", -0.40)))
            # 1h down move, 1d downtrend, 4h high
            & ((_cmp_cached_1) | (_cmp("CMF_20_1d", ">", -0.30)) | (_cmp_cached_55))
            # 1h down move, 1h still high, 4h overbought
            & ((_cmp_cached_1) | (_cmp_cached_49) | (_cmp_cached_26))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_1) | (_cmp_cached_88) | (_cmp_cached_68))
            # 1h down move, 1h high, 1d high
            & ((_cmp_cached_1) | (_cmp_cached_88) | (_cmp_cached_62))
            # 1h down move, 1d overbought
            & ((_cmp_cached_1) | (_cmp_cached_35))
            # 1h & 4h down move, 1h downtrend
            & ((_cmp_cached_2) | (_cmp_cached_5) | (_cmp("ROC_9_1h", ">", -15.0)))
            # 1h & 4h down move, 4h downtrend
            & ((_cmp_cached_2) | (_cmp_cached_5) | (_cmp("ROC_9_4h", ">", -25.0)))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_2) | (_cmp_cached_5) | (_cmp_cached_150))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_2) | (_cmp_cached_6) | (_cmp_cached_110))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_2) | (_cmp_cached_6) | (_cmp_cached_13))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_2) | (_cmp_cached_6) | (_cmp_cached_9))
            # 1h & 1d down move, 1h still high
            & ((_cmp_cached_2) | (_cmp_cached_77) | (_cmp_cached_82))
            # 1h & 1d down move, 1h high
            & ((_cmp_cached_2) | (_cmp_cached_77) | (_cmp_cached_18))
            # 1h down move, 1h downtrend, 1h still high
            & ((_cmp_cached_2) | (_cmp("CMF_20_1h", ">", -0.30)) | (_cmp_cached_82))
            # 1h down move, 1d downtrend, 1d high
            & ((_cmp_cached_2) | (_cmp("CMF_20_1d", ">", -0.30)) | (_cmp_cached_84))
            # 1h down move, 1h & 1d high
            & ((_cmp_cached_2) | (_cmp_cached_12) | (_cmp_cached_38))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_2) | (_cmp_cached_12) | (_cmp_cached_40))
            # 1h down move, 1h high, 1h downtrend
            & ((_cmp_cached_2) | (_cmp_cached_18) | (_cmp("CMF_20_1h", ">", -0.25)))
            # 1h down move, 1h high, 4h downtrend
            & ((_cmp_cached_2) | (_cmp_cached_18) | (_cmp_cached_72))
            # 1h down move, 4h still high, 1d overbought
            & ((_cmp_cached_2) | (_cmp_cached_43) | (_cmp_cached_99))
            # 1h down move, 4h high, 15m downtrend
            & ((_cmp_cached_2) | (_cmp_cached_93) | (_cmp("ROC_9_15m", ">", -15.0)))
            # 1h down move, 4h high, 1h downtrend
            & ((_cmp_cached_2) | (_cmp_cached_93) | (_cmp_cached_124))
            # 1h down move, 1d high, 4h overbought
            & ((_cmp_cached_2) | (_cmp_cached_9) | (_cmp_cached_27))
            # 1h down move, 4h still not low enough, 1d downtrend
            & ((_cmp_cached_2) | (_cmp_cached_94) | (_cmp_cached_23))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_2) | (_cmp_cached_34) | (_cmp_cached_115))
            # 1h down move, 1h downtrend, 1d overbought
            & ((_cmp_cached_2) | (_cmp_cached_124) | (_cmp("ROC_9_1d", "<", 35.0)))
            # 1h down move, 4h downtrend, 1d overbought
            & ((_cmp_cached_2) | (_cmp("ROC_9_4h", ">", -25.0)) | (_cmp_cached_29))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_10) | (_cmp_cached_6) | (_cmp_cached_42))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_10) | (_cmp_cached_60) | (_cmp_cached_58))
            # 1h & 1d down move, 4h high
            & ((_cmp_cached_10) | (_cmp_cached_53) | (_cmp_cached_32))
            # 1h & 1d down move, 1h high
            & ((_cmp_cached_10) | (_cmp_cached_64) | (_cmp_cached_12))
            # 1h & 1d down move, 4h overbought
            & ((_cmp_cached_10) | (_cmp_cached_77) | (_cmp_cached_50))
            # 1h down move, 1h still high, 4h high
            & ((_cmp_cached_10) | (_cmp_cached_49) | (_cmp_cached_32))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_10) | (_cmp_cached_12) | (_cmp_cached_29))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_10) | (_cmp_cached_9) | (_cmp_cached_99))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_10) | (_cmp_cached_56) | (_cmp_cached_27))
            # 1h down move, 1d high, 1d downtrend
            & ((_cmp_cached_10) | (_cmp_cached_84) | (_cmp_cached_95))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_10) | (_cmp_cached_62) | (_cmp_cached_40))
            # 1h down move, 1h & 4h overbought
            & ((_cmp_cached_10) | (_cmp_cached_85) | (_cmp_cached_73))
            # 1h down move, 4h & 1d downtrend
            & ((_cmp_cached_10) | (_cmp_cached_72) | (_cmp_cached_44))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_47) | (_cmp_cached_29))
            # 1h down move, 15m still high, 1h high
            & ((_cmp_cached_11) | (_cmp_cached_46) | (_cmp_cached_52))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_12) | (_cmp_cached_74))
            # 1h down move, 1h & 1d high
            & ((_cmp_cached_11) | (_cmp_cached_12) | (_cmp_cached_38))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_11) | (_cmp_cached_18) | (_cmp_cached_26))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_92) | (_cmp_cached_35))
            # 1h down move, 4h high
            & ((_cmp_cached_11) | (_cmp_cached_32))
            # 1h down move, 1h still high, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_30) | (_cmp_cached_40))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_11) | (_cmp_cached_34) | (_cmp_cached_44))
            # 1h down move, 15m downtrend, 4h overbought
            & ((_cmp_cached_11) | (_cmp("ROC_9_15m", ">", -25.0)) | (_cmp_cached_50))
            # 1h down move, 1h & 1d downtrend
            & ((_cmp_cached_11) | (_cmp("ROC_9_1h", ">", -50.0)) | (_cmp_cached_95))
            # 1h down move, 1h downtrend, 4h overbought
            & ((_cmp_cached_11) | (_cmp("ROC_9_1h", ">", -25.0)) | (_cmp_cached_98))
            # 1h down move, 1h & 4h overbought
            & ((_cmp_cached_11) | (_cmp_cached_129) | (_cmp_cached_115))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_8) | (_cmp_cached_19) | (_cmp_cached_52))
            # 1h down move, 1h downtrend, 1h high
            & ((_cmp_cached_8) | (_cmp("CMF_20_1h", ">", -0.25)) | (_cmp_cached_56))
            # 1h down move, 4h downtrend, 4h high
            & ((_cmp_cached_8) | (_cmp("CMF_20_4h", ">", -0.50)) | (_cmp_cached_14))
            # 1h down move, 1h high & overbought
            & ((_cmp_cached_8) | (_cmp_cached_12) | (_cmp_cached_61))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_8) | (_cmp_cached_12) | (_cmp_cached_146))
            # 1h down move, 4h high, 1h overbought
            & ((_cmp_cached_8) | (_cmp_cached_20) | (_cmp("ROC_9_1h", "<", 50.0)))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_8) | (_cmp_cached_32) | (_cmp_cached_23))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_8) | (_cmp_cached_14) | (_cmp_cached_39))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_8) | (_cmp_cached_27) | (_cmp_cached_35))
            # 1h down move, 15m & 1h high
            & ((_cmp_cached_25) | (_cmp_cached_24) | (_cmp_cached_71))
            # 1h down move, 1h high, 4h downtrend
            & ((_cmp_cached_25) | (_cmp_cached_12) | (_cmp_cached_139))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_25) | (_cmp_cached_18) | (_cmp_cached_14))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_25) | (_cmp_cached_18) | (_cmp_cached_44))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_25) | (_cmp_cached_52) | (_cmp_cached_27))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_25) | (_cmp_cached_13) | (_cmp_cached_74))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_25) | (_cmp_cached_14) | (_cmp_cached_26))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_25) | (_cmp_cached_34) | (_cmp_cached_50))
            # 1h down move, 1h downtrend, 4h overbought
            & ((_cmp_cached_25) | (_cmp_cached_124) | (_cmp_cached_115))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_25) | (_cmp_cached_26) | (_cmp("ROC_9_1d", "<", 70.0)))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_33) | (_cmp_cached_12) | (_cmp_cached_14))
            # 1h down move, 1h high & overbought
            & ((_cmp_cached_33) | (_cmp_cached_18) | (_cmp_cached_61))
            # 1h down move, 1h high, 1d high
            & ((_cmp_cached_33) | (_cmp_cached_92) | (_cmp_cached_69))
            # 1h down move, 1h high, 15m downtrend
            & ((_cmp_cached_33) | (_cmp_cached_52) | (_cmp("ROC_9_15m", ">", -10.0)))
            # 1h down move, 1h  high & overbought
            & ((_cmp_cached_33) | (_cmp_cached_37) | (_cmp_cached_61))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_33) | (_cmp_cached_26) | (_cmp_cached_29))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_33) | (_cmp_cached_50) | (_cmp_cached_40))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_65) | (_cmp_cached_71) | (_cmp_cached_74))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_65) | (_cmp_cached_34) | (_cmp_cached_115))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_63) | (_cmp_cached_88) | (_cmp_cached_150))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_63) | (_cmp_cached_56) | (_cmp_cached_29))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_63) | (_cmp_cached_105) | (_cmp_cached_146))
            # 1h down move, 1h high
            & ((_cmp_cached_97) | (_cmp_cached_37))
            # 1h down move, 1h overbought
            & ((_cmp_cached_97) | (_cmp_cached_129))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_97) | (_cmp_cached_50) | (_cmp_cached_99))
            # 4h & 1d down move, 1d still not low enough
            & ((_cmp_cached_80) | (_cmp_cached_77) | (_cmp("AROONU_14_1d", "<", 30.0)))
            # 4h down move, 4h high, 1h downtrend
            & ((_cmp_cached_80) | (_cmp_cached_13) | (_cmp("ROC_9_1h", ">", -40.0)))
            # 4h down move, 1h still high, 4h downtrend
            & ((_cmp_cached_80) | (_cmp_cached_30) | (_cmp_cached_72))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_57) | (_cmp_cached_53) | (_cmp_cached_121))
            # 4h down move, 15m still high, 1d downtrend
            & ((_cmp_cached_57) | (_cmp_cached_46) | (_cmp_cached_23))
            # 4h & 1d down move, 1d downtrend
            & ((_cmp_cached_4) | (_cmp_cached_64) | (_cmp_cached_95))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_4) | (_cmp_cached_42) | (_cmp_cached_69))
            # 4h down move, 1h & 4h downtrend
            & ((_cmp_cached_4) | (_cmp_cached_124) | (_cmp_cached_72))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_4) | (_cmp_cached_106) | (_cmp("ROC_9_1d", "<", 35.0)))
            # 4h down move, 4h & 1d downtrend
            & ((_cmp_cached_4) | (_cmp("ROC_9_4h", ">", -15.0)) | (_cmp("ROC_9_1d", ">", -35.0)))
            # 4h down move, 4h still high, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_67) | (_cmp_cached_40))
            # 4h down move, 1h still not low enough, 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_132) | (_cmp_cached_15))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_6) | (_cmp_cached_53) | (_cmp_cached_106))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_6) | (_cmp_cached_42) | (_cmp_cached_74))
            # 4h down move, 4h & 1d downtrend
            & ((_cmp_cached_6) | (_cmp_cached_31) | (_cmp_cached_23))
            # 4h down move, 15m high, 1d overbought
            & ((_cmp_cached_21) | (_cmp_cached_24) | (_cmp_cached_29))
            # 4h down move, 4h high
            & ((_cmp_cached_21) | (_cmp_cached_20))
            # 4h down move, 1d high, 1h downtrend
            & ((_cmp_cached_21) | (_cmp_cached_9) | (_cmp("ROC_9_1h", ">", -40.0)))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_19) | (_cmp_cached_43) | (_cmp_cached_44))
            # 4h down move, 4h still high, 1d overbought
            & ((_cmp_cached_19) | (_cmp_cached_43) | (_cmp_cached_74))
            # 4h down move, 4h still not low enough, 1d overbought
            & ((_cmp_cached_19) | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 20.0)) | (_cmp_cached_99))
            # 4h down move, 1d high, 1d downtrend
            & ((_cmp_cached_41) | (_cmp("STOCHRSIk_14_14_3_3_1d", "<", 60.0)) | (_cmp_cached_23))
            # 4h down move, 1h high, 1d overbought
            & ((_cmp_cached_76) | (_cmp_cached_92) | (_cmp_cached_35))
            # 4h down move, 1d high, 1d downtrend
            & ((_cmp_cached_76) | (_cmp_cached_42) | (_cmp_cached_141))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_76) | (_cmp_cached_62) | (_cmp("ROC_9_1d", "<", 25.0)))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_60) | (_cmp_cached_110) | (_cmp_cached_23))
            # 4h down move, 4h high & overbought
            & ((_cmp_cached_60) | (_cmp_cached_20) | (_cmp_cached_27))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_60) | (_cmp_cached_54) | (_cmp_cached_23))
            # 4h down move, 4h & 1d overbought
            & ((_cmp_cached_60) | (_cmp_cached_27) | (_cmp_cached_40))
            # 1d down move, 4h still high, 1d downtrend
            & ((_cmp("RSI_3_1d", ">", 3.0)) | (_cmp_cached_79) | (_cmp_cached_149))
            # 1d down move, 1h & 4h high
            & ((_cmp_cached_66) | (_cmp_cached_49) | (_cmp_cached_32))
            # 1d down move, 1d high, 1d downtrend
            & ((_cmp_cached_66) | (_cmp_cached_45) | (_cmp_cached_44))
            # 1d down move, 4h high, 1d downtrend
            & ((_cmp_cached_66) | (_cmp_cached_55) | (_cmp("ROC_9_1d", ">", -80.0)))
            # 1d down move, 1h & 4h high
            & ((_cmp_cached_59) | (_cmp_cached_52) | (_cmp_cached_14))
            # 1d down move, 1h high, 1d downtrend
            & ((_cmp_cached_53) | (_cmp_cached_71) | (_cmp_cached_23))
            # 1d down move, 1h still high, 4h downtrend
            & ((_cmp_cached_64) | (_cmp_cached_30) | (_cmp_cached_72))
            # 1d down move, 1h high & overbought
            & ((_cmp_cached_133) | (_cmp_cached_83) | (_cmp_cached_61))
            # 15m downtrend, 4h & 1d high
            & ((_cmp("CMF_20_15m", ">", -0.30)) | (_cmp_cached_20) | (_cmp_cached_9))
            # 15m & 1h high, 1h overbought
            & ((_cmp_cached_24) | (_cmp_cached_71) | (_cmp("ROC_9_1h", "<", 50.0)))
            # 15m & 1d high, 1d overbought
            & ((_cmp_cached_24) | (_cmp_cached_38) | (_cmp_cached_51))
            # 1h & 4h high, 1h downtrend
            & ((_cmp_cached_12) | (_cmp_cached_14) | (_cmp("CMF_20_1h", ">", -0.30)))
            # 1h high, 4h high, 1h overbought
            & ((_cmp_cached_12) | (_cmp_cached_14) | (_cmp_cached_85))
            # 1h & 1d high, 1h overbought
            & ((_cmp_cached_12) | (_cmp_cached_45) | (_cmp_cached_85))
            # 1h high, 1d high & overbought
            & ((_cmp_cached_12) | (_cmp_cached_9) | (_cmp_cached_74))
            # 1h high, 1h & 1d overbought
            & ((_cmp_cached_12) | (_cmp_cached_85) | (_cmp_cached_74))
            # 1h high, 4h downtrend, 1d overbought
            & ((_cmp_cached_12) | (_cmp_cached_139) | (_cmp_cached_29))
            # 1h high, 1h & 1d overbought
            & ((_cmp_cached_18) | (_cmp_cached_85) | (_cmp_cached_39))
            # 1h high, 1h overbought, 1d downtrend
            & ((_cmp_cached_18) | (_cmp_cached_129) | (_cmp_cached_44))
            # 1h high, 4h & 1d overbought
            & ((_cmp_cached_18) | (_cmp_cached_27) | (_cmp_cached_40))
            # 1h high, 4h & 1d downtrend
            & ((_cmp_cached_92) | (_cmp_cached_31) | (_cmp_cached_95))
            # 1h & 4h high, 1h overbought
            & ((_cmp_cached_71) | (_cmp_cached_14) | (_cmp_cached_61))
            # 4h high, 4h & 1d overbought
            & ((_cmp_cached_68) | (_cmp_cached_50) | (_cmp_cached_99))
            # 4h & 1d high, 4h overbought
            & ((_cmp_cached_20) | (_cmp_cached_9) | (_cmp_cached_50))
            # 4h high, 4h & 1d overbought
            & ((_cmp_cached_20) | (_cmp_cached_26) | (_cmp_cached_39))
            # 4h high, 15m downtrend, 4h overbought
            & ((_cmp_cached_14) | (_cmp("ROC_9_15m", ">", -30.0)) | (_cmp_cached_50))
            # 4h high, 1h & 4h overbought
            & ((_cmp_cached_14) | (_cmp_cached_129) | (_cmp("ROC_9_4h", "<", 70.0)))
            # 4h & 1d high, 1h overbought
            & ((_cmp_cached_14) | (_cmp_cached_9) | (_cmp("ROC_9_1h", "<", 50.0)))
            # 1d still high, 4h & 1d downtrend
            & ((_cmp_cached_121) | (_cmp("ROC_9_4h", ">", -50.0)) | (_cmp_cached_95))
            # 1d high, 1h & 4h downtrend
            & ((_cmp_cached_103) | (_cmp_cached_124) | (_cmp("ROC_9_4h", ">", -50.0)))
            # 1d high, 4h downtrend, 1d overbought
            & ((_cmp_cached_103) | (_cmp("ROC_9_4h", ">", -25.0)) | (_cmp_cached_35))
            # 1d high, 4h & 1d overbought
            & ((_cmp_cached_38) | (_cmp_cached_27) | (_cmp_cached_35))
            # 1h high, 1d overbought
            & ((_cmp_cached_56) | (_cmp_cached_40))
            # 1h high, 4h overbought
            & ((_cmp_cached_37) | (_cmp_cached_114))
            # 1h high, 1h overbought, 4h downtrend
            & ((_cmp_cached_83) | (_cmp_cached_61) | (_cmp("ROC_9_4h", ">", -15.0)))
            # 4h high, 1h & 4h overbought
            & ((_cmp_cached_55) | (_cmp_cached_85) | (_cmp_cached_98))
            # 1d high, 4h & 1d overbought
            & ((_cmp_cached_62) | (_cmp_cached_115) | (_cmp_cached_29))
            # 1d P&D, 4h overbought
            & ((_cmp("change_pct_1d", ">", -10.0)) | (df["change_pct_1d"].shift(288) < 30.0) | (_cmp_cached_27))
            # big drop in the last 20 days, 1d high, 1d downtrend
            & (
              _gt_mul("close", "high_max_20_1d", 0.20)
              | (_cmp_cached_106)
              | (_cmp_cached_141)
            )
          )

          # Logic
          long_entry_logic.append(
            (_cmp_cached_104)
            & (_cmp("RSI_14", "<", 36.0))
            & (_cmp("AROONU_14", "<", 25.0))
            & (_cmp("AROOND_14", ">", 75.0))
            & (df["EMA_9"] < (df["EMA_26"] * 0.960))
          )

        # Condition #42 - Quick mode (Long).
        if long_entry_condition_index == 42:
          # Protections
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          # long_entry_logic.append(df["protections_long_global"] == True)

          long_entry_logic.append(
            # 5m & 1h down move, 1d still high
            ((_cmp_cached_48) | (_cmp_cached_36) | (_cmp("STOCHRSIk_14_14_3_3_1d", "<", 40.0)))
            # 5m & 1h down move, 1d high
            & ((_cmp_cached_48) | (_cmp_cached_11) | (_cmp_cached_106))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_7) | (_cmp_cached_36) | (_cmp_cached_58))
            # 15m & 1h down move, 1h downtrend
            & ((_cmp_cached_7) | (_cmp_cached_36) | (_cmp("ROC_9_1h", ">", -50.0)))
            # 15m & 1h down move, 1d still not low enough
            & ((_cmp_cached_7) | (_cmp_cached_22) | (_cmp("STOCHRSIk_14_14_3_3_1d", "<", 30.0)))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_7) | (_cmp_cached_1) | (_cmp_cached_43))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_7) | (_cmp_cached_1) | (_cmp("AROONU_14_1d", "<", 60.0)))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_7) | (_cmp_cached_2) | (_cmp_cached_88))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_7) | (_cmp_cached_19) | (_cmp_cached_79))
            # 15m & 4h down move, 1d still high
            & ((_cmp_cached_7) | (_cmp_cached_5) | (_cmp_cached_135))
            # 15m & 1h down move, 1d downtrend
            & ((_cmp_cached_7) | (_cmp_cached_2) | (_cmp_cached_23))
            # 15m down move, 4h still high, 1d downtrend
            & ((_cmp_cached_7) | (_cmp_cached_79) | (_cmp_cached_44))
            # 15m & 1h & 4h down move
            & ((_cmp_cached_17) | (_cmp_cached_22) | (_cmp_cached_6))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_17) | (_cmp_cached_22) | (_cmp_cached_86))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_17) | (_cmp_cached_22) | (_cmp_cached_45))
            # 15m & 1h & 4h down move
            & ((_cmp_cached_17) | (_cmp_cached_1) | (_cmp_cached_5))
            # 15m & 4h down move, 1h downtrend
            & ((_cmp_cached_17) | (_cmp_cached_4) | (_cmp_cached_120))
            # 15m & 4h down move, 1d downtrend
            & ((_cmp_cached_17) | (_cmp_cached_4) | (_cmp_cached_23))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_17) | (_cmp_cached_19) | (_cmp_cached_67))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_1) | (_cmp_cached_13))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_0) | (_cmp_cached_1) | (_cmp_cached_9))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_0) | (_cmp_cached_1) | (_cmp_cached_79))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_0) | (_cmp_cached_1) | (_cmp_cached_62))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_2) | (_cmp_cached_105))
            # 15m & 1h down move, 1d downtrend
            & ((_cmp_cached_0) | (_cmp_cached_2) | (_cmp_cached_23))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_10) | (_cmp_cached_14))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_10) | (_cmp_cached_78))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_0) | (_cmp_cached_19) | (_cmp_cached_62))
            # 15m & 1d down move, 4h still high
            & ((_cmp_cached_0) | (_cmp_cached_66) | (_cmp_cached_79))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_0) | (_cmp_cached_4) | (_cmp_cached_79))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_0) | (_cmp_cached_6) | (_cmp_cached_106))
            # 15m & 4h down move, 4h still not low enough
            & ((_cmp_cached_0) | (_cmp_cached_6) | (_cmp_cached_94))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_0) | (_cmp_cached_6) | (_cmp_cached_84))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_2) | (_cmp_cached_12))
            # 15m & 1h down move, 15m still high
            & ((_cmp_cached_3) | (_cmp_cached_10) | (_cmp_cached_75))
            # 15m & 4h down move, 15m still high
            & ((_cmp_cached_3) | (_cmp_cached_5) | (_cmp_cached_75))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_6) | (_cmp_cached_68))
            # 15m & 1d down move, 1d high
            & ((_cmp_cached_3) | (_cmp_cached_118) | (_cmp_cached_106))
            # 15m down move, 15m high
            & ((_cmp_cached_3) | (_cmp_cached_24))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_16) | (_cmp_cached_21) | (_cmp_cached_13))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_16) | (_cmp_cached_12) | (_cmp_cached_14))
            # 15m down move, 15m still not low enough, 1d downtrend
            & ((_cmp_cached_28) | (_cmp("AROONU_14_15m", "<", 25.0)) | (_cmp_cached_95))
            # 15m down move, 15m still high, 4h high
            & ((_cmp_cached_28) | (_cmp_cached_46) | (_cmp_cached_20))
            # 15m down move, 4h high, 1d downtrend
            & ((_cmp_cached_28) | (_cmp_cached_34) | (_cmp_cached_44))
            # 15m down move, 4h high, 1d downtrend
            & ((_cmp_cached_28) | (_cmp_cached_55) | (_cmp_cached_142))
            # 15m down move, 15m still high, 4h high
            & ((_cmp_cached_100) | (_cmp_cached_46) | (_cmp_cached_20))
            # 1h & 4h down move
            & ((_cmp_cached_36) | (_cmp_cached_80))
            # 1h & 4h down move, 1d still high
            & ((_cmp_cached_36) | (_cmp_cached_5) | (_cmp_cached_121))
            # 1h & 4h down move, 1d still high
            & ((_cmp_cached_36) | (_cmp_cached_5) | (_cmp_cached_117))
            # 1h & 4h down move, 1h still high
            & ((_cmp_cached_36) | (_cmp_cached_6) | (_cmp_cached_86))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_36) | (_cmp_cached_6) | (_cmp_cached_94))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_36) | (_cmp_cached_21) | (_cmp_cached_13))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_36) | (_cmp_cached_21) | (_cmp_cached_45))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_36) | (_cmp_cached_21) | (_cmp_cached_105))
            # 1h down move, 1d high, 1d downtrend
            & ((_cmp_cached_36) | (_cmp_cached_45) | (_cmp("ROC_9_1h", ">", -50.0)))
            # 1h & 4h down move, 15m still not low enough
            & ((_cmp_cached_22) | (_cmp_cached_57) | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 20.0)))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_22) | (_cmp_cached_57) | (_cmp_cached_23))
            # 1h & 4h down move, 1d still high
            & ((_cmp_cached_22) | (_cmp_cached_5) | (_cmp_cached_135))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_22) | (_cmp_cached_21) | (_cmp_cached_12))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_22) | (_cmp_cached_21) | (_cmp_cached_84))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_22) | (_cmp_cached_41) | (_cmp_cached_40))
            # 1h & 1d down move, 1h still high
            & ((_cmp_cached_22) | (_cmp("RSI_3_1d", ">", 5.0)) | (_cmp_cached_49))
            # 1h down move, 4h high
            & ((_cmp_cached_22) | (_cmp_cached_32))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp("AROONU_14_1d", "<", 75.0)))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp_cached_84))
            # 1h & 4h down move, 4h downtrend
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp_cached_31))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp_cached_15))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp_cached_78))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_1) | (_cmp_cached_5) | (_cmp_cached_42))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_1) | (_cmp_cached_5) | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 20.0)))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_5) | (_cmp_cached_44))
            # 1h & 4h down move, 1h still high
            & ((_cmp_cached_1) | (_cmp_cached_6) | (_cmp_cached_86))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_1) | (_cmp_cached_6) | (_cmp_cached_13))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_1) | (_cmp_cached_6) | (_cmp_cached_38))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_1) | (_cmp_cached_21) | (_cmp_cached_40))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_1) | (_cmp_cached_41) | (_cmp_cached_9))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_1) | (_cmp_cached_41) | (_cmp_cached_58))
            # 1h & 1d down move, 1d still high
            & ((_cmp_cached_1) | (_cmp_cached_66) | (_cmp_cached_117))
            # 1h & 1d down move, 1d still high
            & ((_cmp_cached_1) | (_cmp_cached_64) | (_cmp("RSI_14_1d", "<", 50.0)))
            # 1h & 1d down move, 1h high
            & ((_cmp_cached_1) | (_cmp_cached_64) | (_cmp_cached_12))
            # 1h & 1d down move, 1d high
            & ((_cmp_cached_1) | (_cmp_cached_107) | (_cmp_cached_45))
            # 1h down move, 1h downtrend, 1h high
            & ((_cmp_cached_1) | (_cmp("CMF_20_1h", ">", -0.30)) | (_cmp_cached_12))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_86) | (_cmp_cached_15))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_1) | (_cmp_cached_88) | (_cmp_cached_13))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_1) | (_cmp_cached_88) | (_cmp_cached_39))
            # 1h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_67) | (_cmp_cached_44))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_13) | (_cmp_cached_15))
            # 1h down move, 1d still high, 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_135) | (_cmp_cached_15))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_1) | (_cmp_cached_38) | (_cmp_cached_51))
            # 1h down move, 15m high
            & ((_cmp_cached_1) | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 80.0)))
            # 1h down move, 4h & 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_31) | (_cmp_cached_44))
            # 1h & 4h down move, 1d still high, 1d downtrend
            & ((_cmp_cached_2) | (_cmp_cached_5) | (_cmp("RSI_14_1d", "<", 40.0)) | (_cmp_cached_141))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_2) | (_cmp_cached_5) | (_cmp_cached_43))
            # 1h & 4h down move, 15m still high
            & ((_cmp_cached_2) | (_cmp_cached_5) | (_cmp_cached_113))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_2) | (_cmp_cached_5) | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 20.0)))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_2) | (_cmp_cached_5) | (_cmp_cached_106))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_2) | (_cmp_cached_21) | (_cmp_cached_44))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_2) | (_cmp_cached_19) | (_cmp_cached_68))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_2) | (_cmp_cached_19) | (_cmp_cached_84))
            # 1h & 4h down move, 4h overbought
            & ((_cmp_cached_2) | (_cmp_cached_41) | (_cmp_cached_27))
            # 1h & 1d down move, 4h high
            & ((_cmp_cached_2) | (_cmp_cached_53) | (_cmp_cached_105))
            # 1h & 1d down move, 1d overbought
            & ((_cmp_cached_2) | (_cmp_cached_133) | (_cmp_cached_78))
            # 1h down move, 1h downtrend, 1h high
            & ((_cmp_cached_2) | (_cmp("CMF_20_1h", ">", -0.30)) | (_cmp_cached_12))
            # 1h down move, 1h still high, 4h downtrend
            & ((_cmp_cached_2) | (_cmp_cached_86) | (_cmp_cached_72))
            # 1h down move, 1h still high, 1d downtrend
            & ((_cmp_cached_2) | (_cmp_cached_49) | (_cmp_cached_44))
            # 1h down move, 1d still high, 4h downtrend
            & ((_cmp_cached_2) | (_cmp_cached_121) | (_cmp_cached_31))
            # 1h down move, 1d high, 1d downtrend
            & ((_cmp_cached_2) | (_cmp_cached_42) | (_cmp_cached_15))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_2) | (_cmp_cached_42) | (_cmp_cached_51))
            # 1h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_2) | (_cmp_cached_54) | (_cmp_cached_23))
            # 1h down move, 4h & 1d downtrend
            & ((_cmp_cached_2) | (_cmp_cached_31) | (_cmp_cached_15))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_10) | (_cmp_cached_6) | (_cmp_cached_12))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_10) | (_cmp_cached_6) | (_cmp_cached_9))
            # 1h & 4h down move, 15m high
            & ((_cmp_cached_10) | (_cmp_cached_6) | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 60.0)))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_10) | (_cmp_cached_6) | (_cmp_cached_51))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_10) | (_cmp_cached_60) | (_cmp_cached_34))
            # 1h & 1d down move, 1d high
            & ((_cmp_cached_10) | (_cmp_cached_53) | (_cmp("STOCHRSIk_14_14_3_3_1d", "<", 60.0)))
            # 1h & 1d down move, 1d high
            & ((_cmp_cached_10) | (_cmp_cached_77) | (_cmp_cached_9))
            # 1h & 1d down move, 1d overbought
            & ((_cmp_cached_10) | (_cmp_cached_107) | (_cmp_cached_39))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_10) | (_cmp_cached_88) | (_cmp_cached_51))
            # 1h down move, 1h high, 4h downtrend
            & ((_cmp_cached_10) | (_cmp_cached_12) | (_cmp_cached_31))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_10) | (_cmp_cached_9) | (_cmp_cached_51))
            # 1h down move, 1d high, 4h downtrend
            & ((_cmp_cached_10) | (_cmp_cached_84) | (_cmp_cached_31))
            # 1h & 4h down move, 15m high
            & ((_cmp_cached_11) | (_cmp_cached_21) | (_cmp_cached_108))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_11) | (_cmp_cached_47) | (_cmp_cached_13))
            # 1h & 1d down move, 1h high
            & ((_cmp_cached_11) | (_cmp_cached_64) | (_cmp_cached_18))
            # 1h & 1d down move, 1d high
            & ((_cmp_cached_11) | (_cmp_cached_107) | (_cmp_cached_84))
            # 1h down move, 4h downtrend, 4h high
            & ((_cmp_cached_11) | (_cmp("CMF_20_4h", ">", -0.50)) | (_cmp_cached_13))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_88) | (_cmp_cached_35))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_11) | (_cmp_cached_88) | (_cmp_cached_44))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_11) | (_cmp_cached_13) | (_cmp_cached_27))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_11) | (_cmp_cached_42) | (_cmp_cached_74))
            # 1h down move, 1d high, 4h overbought
            & ((_cmp_cached_11) | (_cmp_cached_9) | (_cmp_cached_27))
            # 1h down move, 1h high & overbought
            & ((_cmp_cached_11) | (_cmp_cached_9) | (_cmp_cached_39))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_11) | (_cmp_cached_34) | (_cmp_cached_26))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_8) | (_cmp_cached_19) | (_cmp_cached_95))
            # 1h & 4h down move, 15m high
            & ((_cmp_cached_8) | (_cmp_cached_41) | (_cmp("AROONU_14_15m", "<", 80.0)))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_8) | (_cmp_cached_47) | (_cmp("AROONU_14_4h", "<", 75.0)))
            # 1h & 4h down move, 15m high
            & ((_cmp_cached_8) | (_cmp_cached_47) | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 80.0)))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_8) | (_cmp_cached_60) | (_cmp_cached_20))
            # 1h & 1d down move, 1d high
            & ((_cmp_cached_8) | (_cmp_cached_77) | (_cmp_cached_42))
            # 1h & 1d down move, 1d overbought
            & ((_cmp_cached_8) | (_cmp_cached_118) | (_cmp_cached_35))
            # 1h down move, 4h high, 4h downtrend
            & ((_cmp_cached_8) | (_cmp_cached_13) | (_cmp("CMF_20_4h", ">", -0.40)))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_8) | (_cmp_cached_20) | (_cmp_cached_50))
            # 1h down move, 1d high, 4h overbought
            & ((_cmp_cached_8) | (_cmp_cached_9) | (_cmp_cached_27))
            # 1h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_8) | (_cmp_cached_79) | (_cmp("ROC_9_1d", ">", -80.0)))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_8) | (_cmp_cached_27) | (_cmp_cached_51))
            # 1h & 4h down move, 15m high
            & ((_cmp_cached_25) | (_cmp_cached_76) | (_cmp("AROONU_14_15m", "<", 90.0)))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_25) | (_cmp_cached_76) | (_cmp_cached_32))
            # 1h down move, 15m high, 1d downtrend
            & ((_cmp_cached_25) | (_cmp_cached_90) | (_cmp_cached_44))
            # 1h down move, 1h still high, 1d high
            & ((_cmp_cached_25) | (_cmp_cached_49) | (_cmp_cached_38))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_25) | (_cmp_cached_12) | (_cmp_cached_14))
            # 1h down move, 1h & 1d high
            & ((_cmp_cached_25) | (_cmp_cached_12) | (_cmp_cached_9))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_25) | (_cmp_cached_32) | (_cmp_cached_15))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_25) | (_cmp_cached_55) | (_cmp_cached_27))
            # 1h down move, 4h & 1d downtrend
            & ((_cmp_cached_25) | (_cmp_cached_102) | (_cmp_cached_146))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_33) | (_cmp_cached_32) | (_cmp_cached_26))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_33) | (_cmp_cached_105) | (_cmp_cached_95))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_33) | (_cmp_cached_58) | (_cmp_cached_73))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_65) | (_cmp_cached_20) | (_cmp_cached_115))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_63) | (_cmp_cached_14) | (_cmp_cached_73))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_63) | (_cmp_cached_62) | (_cmp_cached_39))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_97) | (_cmp_cached_50) | (_cmp_cached_29))
            # 4h & 1d down move
            & ((_cmp_cached_80) | (_cmp_cached_59))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_80) | (_cmp_cached_64) | (_cmp("STOCHRSIk_14_14_3_3_1d", "<", 60.0)))
            # 4h down move, 1h downtrend, 4h still high
            & ((_cmp_cached_80) | (_cmp("CMF_20_1h", ">", -0.30)) | (_cmp_cached_67))
            # 4h & 1d down move, 4h downtrend
            & ((_cmp_cached_57) | (_cmp_cached_59) | (_cmp_cached_102))
            # 4h & 1d down move, 1d downtrend
            & ((_cmp_cached_57) | (_cmp_cached_59) | (_cmp_cached_15))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_57) | (_cmp_cached_53) | (_cmp_cached_135))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_57) | (_cmp_cached_53) | (_cmp_cached_117))
            # 4h & 1d down move, 4h still not low enough
            & ((_cmp_cached_57) | (_cmp_cached_77) | (_cmp("AROONU_14_4h", "<", 20.0)))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_57) | (_cmp_cached_77) | (_cmp_cached_45))
            # 4h down move, 1h & 4h downtrend
            & ((_cmp_cached_57) | (_cmp("ROC_9_1h", ">", -15.0)) | (_cmp_cached_31))
            # 4h down move, 4h & 1d downtrend
            & ((_cmp_cached_57) | (_cmp_cached_31) | (_cmp_cached_15))
            # 4h & 1d down move, 15m still not low enough
            & ((_cmp_cached_4) | (_cmp_cached_66) | (_cmp_cached_111))
            # 4h & 1d down move, 1d downtrend
            & ((_cmp_cached_4) | (_cmp_cached_66) | (_cmp_cached_15))
            # 15m & 1d down move, 15m still high
            & ((_cmp_cached_4) | (_cmp_cached_59) | (_cmp_cached_75))
            # 4h & 1d down move, 4h downtrend
            & ((_cmp_cached_4) | (_cmp_cached_77) | (_cmp_cached_31))
            # 4h & 1d down move, 1d overbought
            & ((_cmp_cached_4) | (_cmp_cached_107) | (_cmp_cached_78))
            # 4h & 1d down move, 4h still not low enough
            & ((_cmp_cached_4) | (_cmp("RSI_3_1d", ">", 50.0)) | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 20.0)))
            # 4h down move, 15m high, 1h downtrend
            & ((_cmp_cached_4) | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 60.0)) | (_cmp("ROC_9_1h", ">", -10.0)))
            # 4h down move, 15m high
            & ((_cmp_cached_4) | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 80.0)))
            # 4h down move, 4h still not low e nough, 1d downtrend
            & ((_cmp_cached_4) | (_cmp_cached_94) | (_cmp_cached_15))
            # 4h down move, 4h & 1d downtrend
            & ((_cmp_cached_4) | (_cmp_cached_31) | (_cmp_cached_44))
            # 4h & 1d down move, 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_59) | (_cmp_cached_23))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_5) | (_cmp_cached_64) | (_cmp_cached_135))
            # 15m & 1d down move, 15m high
            & ((_cmp_cached_5) | (_cmp_cached_77) | (_cmp_cached_108))
            # 4h & 1d down move, 4h still high
            & ((_cmp_cached_5) | (_cmp_cached_77) | (_cmp_cached_54))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_5) | (_cmp_cached_133) | (_cmp("RSI_14_1d", "<", 50.0)))
            # 4h down move, 1h still high, 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_86) | (_cmp_cached_95))
            # 4h down move, 1h high, 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_52) | (_cmp_cached_23))
            # 4h down move, 4h still high, 4h downtrend
            & ((_cmp_cached_5) | (_cmp_cached_67) | (_cmp_cached_31))
            # 4h down move, 4h still high, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_43) | (_cmp_cached_45))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_43) | (_cmp_cached_15))
            # 4h down move, 1h & 4h downtrend
            & ((_cmp_cached_5) | (_cmp("ROC_9_1h", ">", -40.0)) | (_cmp_cached_139))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_6) | (_cmp_cached_53) | (_cmp_cached_84))
            # 4h & 1d down move, 15m high
            & ((_cmp_cached_6) | (_cmp_cached_77) | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 80.0)))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_6) | (_cmp("RSI_3_1d", ">", 50.0)) | (_cmp_cached_62))
            # 4h down move, 15m high, 4h downtrend
            & ((_cmp_cached_6) | (_cmp_cached_24) | (_cmp_cached_72))
            # 4h down move, 4h high
            & ((_cmp_cached_6) | (_cmp_cached_14))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_6) | (_cmp_cached_45) | (_cmp("ROC_9_1d", "<", 70.0)))
            # 4h down move, 1d high, 4h downtrend
            & ((_cmp_cached_6) | (_cmp_cached_38) | (_cmp("ROC_9_4h", ">", -50.0)))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_6) | (_cmp_cached_38) | (_cmp_cached_40))
            # 4h down move, 15m high
            & ((_cmp_cached_6) | (_cmp_cached_108))
            # 4h down move, 4h still not low enough, 1d downtrend
            & ((_cmp_cached_6) | (_cmp_cached_94) | (_cmp_cached_15))
            # 4h down move, 4h & 1d downtrend
            & ((_cmp_cached_6) | (_cmp_cached_31) | (_cmp_cached_15))
            # 4h down move, 1d high, 4h downtrend
            & ((_cmp_cached_6) | (_cmp_cached_84) | (_cmp_cached_31))
            # 4h & 1d down move, 1h high
            & ((_cmp_cached_21) | (_cmp_cached_64) | (_cmp_cached_52))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_21) | (_cmp_cached_64) | (_cmp_cached_38))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_21) | (_cmp_cached_67) | (_cmp_cached_15))
            # 4h down move, 4h high, 1h downtrend
            & ((_cmp_cached_21) | (_cmp_cached_68) | (_cmp("ROC_9_1h", ">", -10.0)))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_21) | (_cmp_cached_42) | (_cmp_cached_51))
            # 4h down move, 1d high, 4h downtrend
            & ((_cmp_cached_21) | (_cmp_cached_9) | (_cmp_cached_31))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_21) | (_cmp_cached_79) | (_cmp_cached_23))
            # 4h down move, 4h high, 1d downtrend
            & ((_cmp_cached_21) | (_cmp_cached_58) | (_cmp_cached_15))
            # 4h down move, 1d overbought
            & ((_cmp_cached_21) | (_cmp_cached_29))
            # 4h down move, 1h high, 4h downtrend
            & ((_cmp_cached_19) | (_cmp_cached_88) | (_cmp_cached_102))
            # 4h down move, 4h still high, 1d high
            & ((_cmp_cached_19) | (_cmp_cached_43) | (_cmp_cached_9))
            # 4h down move, 4h high, 1h downtrend
            & ((_cmp_cached_19) | (_cmp_cached_20) | (_cmp("ROC_9_1h", ">", -40.0)))
            # 4h down move, 4h high
            & ((_cmp_cached_19) | (_cmp_cached_14))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_19) | (_cmp_cached_45) | (_cmp_cached_99))
            # 4h down move, 15m still high, 4h high
            & ((_cmp_cached_41) | (_cmp_cached_46) | (_cmp_cached_20))
            # 4h down move, 1h high
            & ((_cmp_cached_41) | (_cmp_cached_12))
            # 4h down move, 4h high, 1d downtrend
            & ((_cmp_cached_41) | (_cmp_cached_20) | (_cmp_cached_15))
            # 4h down move, 4h high, 1d overbought
            & ((_cmp_cached_41) | (_cmp_cached_20) | (_cmp_cached_51))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_41) | (_cmp_cached_9) | (_cmp_cached_39))
            # 4h down move, 4h still high, 1d overbought
            & ((_cmp_cached_41) | (_cmp_cached_54) | (_cmp_cached_74))
            # 4h down move, 4h & 1d high
            & ((_cmp_cached_47) | (_cmp_cached_13) | (_cmp_cached_9))
            # 4h down move, 4h high, 1d overbought
            & ((_cmp_cached_47) | (_cmp_cached_13) | (_cmp_cached_39))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_47) | (_cmp_cached_54) | (_cmp_cached_44))
            # 4h down move, 4h overbought, 1d downtrend
            & ((_cmp_cached_47) | (_cmp_cached_27) | (_cmp_cached_44))
            # 4h down move, 4h & 1d overbought
            & ((_cmp_cached_47) | (_cmp_cached_123) | (_cmp_cached_69))
            # 4h down move, 4h & 1d high
            & ((_cmp_cached_76) | (_cmp_cached_20) | (_cmp_cached_9))
            # 4h down move, 4h overbought
            & ((_cmp_cached_131) | (_cmp_cached_50))
            # 4h down move, 4h high & overbought
            & ((_cmp_cached_87) | (_cmp_cached_34) | (_cmp_cached_27))
            # 1d down move, 1d high, 1d downtrend
            & ((_cmp_cached_59) | (_cmp_cached_45) | (_cmp_cached_15))
            # 1d down move, 1d still high
            & ((_cmp_cached_59) | (_cmp("STOCHRSIk_14_14_3_3_1d", "<", 40.0)))
            # 1d down move, 4h & 1d downtrend
            & ((_cmp_cached_59) | (_cmp_cached_102) | (_cmp_cached_44))
            # 1d down move, 15m high
            & ((_cmp_cached_53) | (_cmp("AROONU_14_15m", "<", 80.0)))
            # 1d down move, 4h high, 4h downtrend
            & ((_cmp_cached_53) | (_cmp_cached_43) | (_cmp_cached_139))
            # 1d down move, 1d high, 1d downtrend
            & ((_cmp_cached_64) | (_cmp_cached_42) | (_cmp_cached_23))
            # 1d down move, 1d still high, 1d downtrend
            & ((_cmp_cached_64) | (_cmp_cached_117) | (_cmp_cached_15))
            # 1d down move, 4h & 1d high
            & ((_cmp_cached_77) | (_cmp_cached_32) | (_cmp_cached_38))
            # 1h & 4h downtrend, 4h high
            & ((_cmp("CMF_20_1h", ">", -0.40)) | (_cmp("CMF_20_4h", ">", -0.40)) | (_cmp_cached_20))
            # 4h & 1d downtrend, 1d high
            & ((_cmp("CMF_20_4h", ">", -0.50)) | (_cmp("CMF_20_1d", ">", -0.50)) | (_cmp_cached_103))
            # 15m & 1d high, 4h overbought
            & ((_cmp_cached_24) | (_cmp_cached_9) | (_cmp_cached_26))
            # 15m & 4h high, 1d downtrend
            & ((_cmp("AROONU_14_15m", "<", 85.0)) | (_cmp_cached_93) | (_cmp_cached_15))
            # 1h still high, 1h & 4h downtrend
            & ((_cmp_cached_49) | (_cmp_cached_120) | (_cmp_cached_72))
            # 1h & 4h high, 4h overbought
            & ((_cmp_cached_18) | (_cmp_cached_14) | (_cmp_cached_27))
            # 4h high, 4h & 1d downtrend
            & ((_cmp_cached_68) | (_cmp_cached_72) | (_cmp_cached_23))
            # 4h & 1d high, 4h overbought
            & ((_cmp_cached_13) | (_cmp_cached_9) | (_cmp_cached_50))
            # 4h & 1d high, 1d overbought
            & ((_cmp_cached_13) | (_cmp_cached_9) | (_cmp_cached_69))
            # 4h high, 4h & 1d overbought
            & ((_cmp_cached_32) | (_cmp_cached_27) | (_cmp_cached_78))
            # 1d high, 4h & 1d overbought
            & ((_cmp_cached_45) | (_cmp_cached_50) | (_cmp_cached_74))
            # 1d high, 4h downtrend, 1d overbought
            & ((_cmp_cached_103) | (_cmp_cached_31) | (_cmp_cached_74))
            # 1d high, 1h & 4h downtrend
            & ((_cmp_cached_9) | (_cmp_cached_124) | (_cmp_cached_72))
            # 1d high, 1h & 1d overbought
            & ((_cmp_cached_9) | (_cmp_cached_61) | (_cmp_cached_51))
            # 1d high, 4h & 1d overbought
            & ((_cmp_cached_9) | (_cmp_cached_50) | (_cmp_cached_99))
            # 15m still high, 1h & 4h downtrend
            & ((_cmp_cached_75) | (_cmp_cached_120) | (_cmp_cached_31))
            # 4h high, 1h & 4h overbought
            & ((_cmp_cached_55) | (_cmp_cached_85) | (_cmp_cached_50))
            # 4h high, 4h & 1d overbought
            & ((_cmp_cached_55) | (_cmp_cached_26) | (_cmp_cached_69))
            # 1d still high, 4h & 1d downtrend
            & ((_cmp_cached_117) | (_cmp_cached_72) | (_cmp_cached_23))
            # big drop in the last 20 days, 1d high, 1d downtrend
            & (
              _gt_mul("close", "high_max_20_1d", 0.20)
              | (_cmp_cached_106)
              | (_cmp_cached_141)
            )
          )

          # Logic
          long_entry_logic.append(
            (_cmp("WILLR_14", "<", -50.0))
            & (_cmp("STOCHRSIk_14_14_3_3", "<", 20.0))
            & (_cmp("WILLR_84_1h", "<", -70.0))
            & (_cmp_cached_132)
            & (_cmp("BBB_20_2.0_1h", ">", 16.0))
            & (df["close_max_48"] >= (df["close"] * 1.10))
          )

        # Condition #43 - Quick mode (Long).
        if long_entry_condition_index == 43:
          # Protections
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          # long_entry_logic.append(df["protections_long_global"] == True)

          long_entry_logic.append(
            # 5m & 15m down move, 15m still high
            ((_cmp_cached_48) | (_cmp_cached_17) | (_cmp_cached_81))
            # 5m & 1h down move, 1h still not low enough
            & ((_cmp_cached_48) | (_cmp_cached_1) | (_cmp_cached_138))
            # 5m & 1h down move, 1h still not low enough
            & ((_cmp_cached_48) | (_cmp_cached_2) | (_cmp_cached_109))
            # 5m & 1h down move, 4h high
            & ((_cmp_cached_48) | (_cmp_cached_63) | (_cmp_cached_105))
            # 5m & 1d down move, 1d still not low enough
            & ((_cmp_cached_48) | (_cmp_cached_59) | (_cmp("AROONU_14_1d", "<", 30.0)))
            # 5m down move, 1h & 4h high
            & ((_cmp_cached_48) | (_cmp_cached_18) | (_cmp_cached_14))
            # 5m down move, 4h high & overbought
            & ((_cmp_cached_48) | (_cmp_cached_14) | (_cmp_cached_26))
            # 5m down move, 1d high & overbought
            & ((_cmp_cached_48) | (_cmp_cached_62) | (_cmp_cached_39))
            # 5m & 1h down move, 1d overbought
            & ((_cmp_cached_104) | (_cmp_cached_11) | (_cmp_cached_29))
            # 5m & 1d down move, 1h high
            & ((_cmp_cached_104) | (_cmp_cached_53) | (_cmp_cached_52))
            # 5m & 1h down move, 1h high
            & ((_cmp_cached_143) | (_cmp_cached_2) | (_cmp_cached_92))
            # 15m & 1h down move
            & ((_cmp_cached_7) | (_cmp_cached_36))
            # 15m & 1h & 4h down move
            & ((_cmp_cached_7) | (_cmp_cached_22) | (_cmp_cached_4))
            # 15m & 1h & 1d down move
            & ((_cmp_cached_7) | (_cmp_cached_1) | (_cmp_cached_64))
            # 15m & 1h down move, 1d still high
            & ((_cmp_cached_7) | (_cmp_cached_1) | (_cmp("RSI_14_1d", "<", 50.0)))
            # 15m & 1h down move, 15m still high
            & ((_cmp_cached_7) | (_cmp_cached_1) | (_cmp_cached_46))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_7) | (_cmp_cached_1) | (_cmp_cached_45))
            # 15m & 1d down move, 1d overbought
            & ((_cmp_cached_7) | (_cmp_cached_1) | (_cmp_cached_78))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_7) | (_cmp_cached_2) | (_cmp_cached_86))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_7) | (_cmp_cached_2) | (_cmp_cached_38))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_7) | (_cmp_cached_2) | (_cmp_cached_13))
            # 15m & 1h down move, 1d downtrend
            & ((_cmp_cached_7) | (_cmp_cached_2) | (_cmp_cached_23))
            # 15m & 1h down move, 15m high
            & ((_cmp_cached_7) | (_cmp_cached_10) | (_cmp_cached_24))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_7) | (_cmp_cached_8) | (_cmp_cached_71))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_7) | (_cmp_cached_8) | (_cmp_cached_62))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_7) | (_cmp_cached_8) | (_cmp_cached_74))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_7) | (_cmp_cached_25) | (_cmp_cached_82))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_7) | (_cmp_cached_65) | (_cmp_cached_32))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_7) | (_cmp_cached_5) | (_cmp_cached_121))
            # 15m & 4h down move, 15m high
            & ((_cmp_cached_7) | (_cmp_cached_6) | (_cmp_cached_24))
            # 15m & 4h down move, 1d overbought
            & ((_cmp_cached_7) | (_cmp_cached_41) | (_cmp_cached_99))
            # 15m & 1d down move, 1d still high
            & ((_cmp_cached_7) | (_cmp_cached_66) | (_cmp_cached_135))
            # 15m & 1d down move, 4h still high
            & ((_cmp_cached_7) | (_cmp_cached_53) | (_cmp_cached_54))
            # 15m & 1d down move, 1d high
            & ((_cmp_cached_7) | (_cmp_cached_107) | (_cmp_cached_45))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_7) | (_cmp_cached_32) | (_cmp_cached_115))
            # 15m down move, 1d high & overbought
            & ((_cmp_cached_7) | (_cmp_cached_9) | (_cmp_cached_40))
            # 15m down move, 1h high, 1d downtrend
            & ((_cmp_cached_7) | (_cmp_cached_37) | (_cmp_cached_15))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_7) | (_cmp_cached_34) | (_cmp_cached_73))
            # 15m down move, 4h high, 1d overbought
            & ((_cmp_cached_7) | (_cmp_cached_34) | (_cmp_cached_78))
            # 15m down move, 1h downtrend, 4h overbought
            & ((_cmp_cached_7) | (_cmp_cached_124) | (_cmp_cached_115))
            # 15m down move, 4h & 1d downtrend
            & ((_cmp_cached_7) | (_cmp("ROC_9_4h", ">", -70.0)) | (_cmp_cached_150))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_17) | (_cmp_cached_22) | (_cmp_cached_110))
            # 15m & 1h down move, 1h still not low enough
            & ((_cmp_cached_17) | (_cmp_cached_2) | (_cmp_cached_132))
            # 15m & 1h down move, 1d still high
            & ((_cmp_cached_17) | (_cmp_cached_10) | (_cmp_cached_117))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_17) | (_cmp_cached_11) | (_cmp("ROC_9_1d", "<", 70.0)))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_17) | (_cmp_cached_8) | (_cmp_cached_13))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_17) | (_cmp_cached_65) | (_cmp_cached_18))
            # 15m & 4h down move, 1h still high
            & ((_cmp_cached_17) | (_cmp_cached_4) | (_cmp_cached_30))
            # 15m & 4h down move, 1h downtrend
            & ((_cmp_cached_17) | (_cmp_cached_4) | (_cmp_cached_120))
            # 15m & 4h down move, 15m still high
            & ((_cmp_cached_17) | (_cmp_cached_5) | (_cmp_cached_75))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_17) | (_cmp_cached_6) | (_cmp_cached_43))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_17) | (_cmp_cached_6) | (_cmp_cached_45))
            # 15m & 1d down move, 1h still high
            & ((_cmp_cached_17) | (_cmp_cached_53) | (_cmp_cached_30))
            # 15m down move, 15m & 1h still high
            & ((_cmp_cached_17) | (_cmp_cached_81) | (_cmp_cached_49))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_17) | (_cmp_cached_18) | (_cmp_cached_14))
            # 15m down move, 1h high, 4h overbought
            & ((_cmp_cached_17) | (_cmp_cached_18) | (_cmp_cached_27))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_17) | (_cmp_cached_20) | (_cmp_cached_98))
            # 15m down move, 1d still high, 1d downtrend
            & ((_cmp_cached_17) | (_cmp_cached_117) | (_cmp_cached_15))
            # 15m down move, 1d downtrend
            & ((_cmp_cached_17) | (_cmp_cached_146))
            # 15m & 1h down move, 15m high
            & ((_cmp_cached_0) | (_cmp_cached_1) | (_cmp_cached_24))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_0) | (_cmp_cached_2) | (_cmp_cached_82))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_0) | (_cmp_cached_2) | (_cmp_cached_62))
            # 15m & 1h down move, 4h downtrend
            & ((_cmp_cached_0) | (_cmp_cached_2) | (_cmp_cached_31))
            # 15m & 1h down move, 1d downtrend
            & ((_cmp_cached_0) | (_cmp_cached_2) | (_cmp_cached_44))
            # 15m & 1h down move, 15m still high
            & ((_cmp_cached_0) | (_cmp_cached_10) | (_cmp_cached_46))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_0) | (_cmp_cached_10) | (_cmp_cached_12))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_0) | (_cmp_cached_10) | (_cmp_cached_42))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_10) | (_cmp_cached_69))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_11) | (_cmp_cached_32))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_11) | (_cmp_cached_34))
            # 15m & 1h down move, 4h overbought
            & ((_cmp_cached_0) | (_cmp_cached_11) | (_cmp_cached_26))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_0) | (_cmp_cached_8) | (_cmp_cached_112))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_0) | (_cmp_cached_33) | (_cmp_cached_38))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_0) | (_cmp_cached_33) | (_cmp_cached_83))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_63) | (_cmp_cached_55))
            # 15m & 4h down move, 15m still high
            & ((_cmp_cached_0) | (_cmp_cached_4) | (_cmp_cached_113))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_0) | (_cmp_cached_4) | (_cmp_cached_79))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_0) | (_cmp_cached_5) | (_cmp_cached_83))
            # 15m & 4h down move, 1d downtrend
            & ((_cmp_cached_0) | (_cmp_cached_5) | (_cmp_cached_15))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_0) | (_cmp_cached_47) | (_cmp_cached_43))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_60) | (_cmp_cached_13))
            # 15m & 1d down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_53) | (_cmp_cached_58))
            # 15m down move, 15m still high, 1d downtrend
            & ((_cmp_cached_0) | (_cmp_cached_81) | (_cmp_cached_23))
            # 15m down move, 15m still high, 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_46) | (_cmp_cached_51))
            # 15m down move, 15m high, 1h high
            & ((_cmp_cached_0) | (_cmp_cached_90) | (_cmp_cached_18))
            # 15m down move, 15m high, 4h downtrend
            & ((_cmp_cached_0) | (_cmp_cached_90) | (_cmp_cached_102))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_0) | (_cmp_cached_52) | (_cmp_cached_14))
            # 15m down move, 1h high, 1d downtrend
            & ((_cmp_cached_0) | (_cmp_cached_52) | (_cmp_cached_44))
            # 15m down move, 4h & 1d high
            & ((_cmp_cached_0) | (_cmp_cached_32) | (_cmp_cached_9))
            # 15m down move, 1d high & overbought
            & ((_cmp_cached_0) | (_cmp_cached_9) | (_cmp_cached_29))
            # 15m down move, 4h still high, 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_54) | (_cmp_cached_51))
            # 15m down move, 4h & 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_27) | (_cmp_cached_74))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_2) | (_cmp_cached_52))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_3) | (_cmp_cached_2) | (_cmp_cached_62))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_10) | (_cmp_cached_71))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_10) | (_cmp_cached_14))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_47) | (_cmp_cached_13))
            # 15m down move. 15m still high, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_46) | (_cmp_cached_37))
            # 15m down move, 15m & 4h high
            & ((_cmp_cached_3) | (_cmp_cached_24) | (_cmp_cached_14))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_3) | (_cmp_cached_18) | (_cmp_cached_40))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_3) | (_cmp_cached_68) | (_cmp_cached_50))
            # 15m down move, 4h high, 1d overbought
            & ((_cmp_cached_3) | (_cmp_cached_13) | (_cmp_cached_74))
            # 15m down move, 4h high, 1d overbought
            & ((_cmp_cached_3) | (_cmp_cached_14) | (_cmp_cached_29))
            # 15m down move, 1h high, 4h downtrend
            & ((_cmp_cached_3) | (_cmp_cached_56) | (_cmp_cached_72))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_3) | (_cmp_cached_55) | (_cmp("ROC_9_4h", "<", 25.0)))
            # 15m down move, 4h high, 1d downtrend
            & ((_cmp_cached_3) | (_cmp_cached_55) | (_cmp_cached_44))
            # 15m down move, 4h high, 1d overbought
            & ((_cmp_cached_3) | (_cmp_cached_55) | (_cmp_cached_51))
            # 15m down move, 1d high & overbought
            & ((_cmp_cached_3) | (_cmp_cached_62) | (_cmp_cached_29))
            # 15m down move, 4h & 1d downtrend
            & ((_cmp_cached_3) | (_cmp_cached_102) | (_cmp_cached_44))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_16) | (_cmp_cached_10) | (_cmp_cached_34))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_16) | (_cmp_cached_11) | (_cmp_cached_29))
            # 15m & 1d down move, 4h high
            & ((_cmp_cached_16) | (_cmp_cached_53) | (_cmp_cached_32))
            # 15m down move, 15m & 1h high
            & ((_cmp_cached_16) | (_cmp_cached_24) | (_cmp_cached_71))
            # 15m down move, 1h high, 4h overbought
            & ((_cmp_cached_16) | (_cmp_cached_18) | (_cmp_cached_27))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_16) | (_cmp_cached_18) | (_cmp_cached_78))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_16) | (_cmp_cached_20) | (_cmp_cached_27))
            # 15m & 1h down move, 15m high
            & ((_cmp_cached_28) | (_cmp_cached_11) | (_cmp_cached_108))
            # 15m & 1h down move, 1h downtrend
            & ((_cmp_cached_28) | (_cmp_cached_11) | (_cmp_cached_124))
            # 15m down move, 1d high & overbought
            & ((_cmp_cached_70) | (_cmp_cached_9) | (_cmp_cached_35))
            # 1h & 4h down move, 1d still high
            & ((_cmp_cached_36) | (_cmp_cached_4) | (_cmp_cached_117))
            # 1h & 4h down move, 1d still high
            & ((_cmp_cached_36) | (_cmp_cached_5) | (_cmp_cached_135))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_36) | (_cmp_cached_6) | (_cmp("AROONU_14_1d", "<", 60.0)))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_36) | (_cmp_cached_21) | (_cmp_cached_45))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_36) | (_cmp_cached_21) | (_cmp_cached_39))
            # 1h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_36) | (_cmp_cached_54) | (_cmp_cached_15))
            # 1h & 4h down move, 1h still high
            & ((_cmp_cached_22) | (_cmp_cached_4) | (_cmp_cached_49))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_22) | (_cmp_cached_5) | (_cmp_cached_62))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_22) | (_cmp_cached_6) | (_cmp_cached_9))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_22) | (_cmp_cached_41) | (_cmp_cached_110))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_22) | (_cmp_cached_13) | (_cmp_cached_23))
            # 1h down move, 1d high, 1h downtrend
            & ((_cmp_cached_22) | (_cmp_cached_38) | (_cmp("ROC_9_1h", ">", -40.0)))
            # 1h down move, 4h & 1d downtrend
            & ((_cmp_cached_22) | (_cmp_cached_31) | (_cmp_cached_15))
            # 1h & 4h & 1d down move
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp_cached_59))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp_cached_15))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_1) | (_cmp_cached_5) | (_cmp_cached_88))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_1) | (_cmp_cached_5) | (_cmp_cached_38))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_5) | (_cmp_cached_23))
            # 1h & 1d down move, 4h high
            & ((_cmp_cached_1) | (_cmp_cached_59) | (_cmp_cached_58))
            # 1h & 1d down move, 1d still high
            & ((_cmp_cached_1) | (_cmp_cached_77) | (_cmp_cached_117))
            # 1h down move, 15m downtrend, 1d high
            & ((_cmp_cached_1) | (_cmp("CMF_20_15m", ">", -0.40)) | (_cmp_cached_45))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_1) | (_cmp_cached_18) | (_cmp_cached_27))
            # 1h down move, 1d high, 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_45) | (_cmp_cached_15))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_105) | (_cmp_cached_23))
            # 1h & 4h down move, 1h still not low enough
            & ((_cmp_cached_2) | (_cmp_cached_5) | (_cmp("AROONU_14_1h", "<", 20.0)))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_2) | (_cmp_cached_5) | (_cmp_cached_68))
            # 1h & 4h down move, 1h downtrend
            & ((_cmp_cached_2) | (_cmp_cached_5) | (_cmp("ROC_9_1h", ">", -15.0)))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_2) | (_cmp_cached_5) | (_cmp_cached_78))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_2) | (_cmp_cached_6) | (_cmp_cached_110))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_2) | (_cmp_cached_19) | (_cmp_cached_12))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_2) | (_cmp_cached_47) | (_cmp_cached_45))
            # 1h & 1d down move, 1d still high
            & ((_cmp_cached_2) | (_cmp_cached_64) | (_cmp_cached_121))
            # 1h down move, 1h still high, 1d downtrend
            & ((_cmp_cached_2) | (_cmp_cached_138) | (_cmp_cached_23))
            # 1h down move, 1h still high, 4h downtrend
            & ((_cmp_cached_2) | (_cmp_cached_86) | (_cmp_cached_72))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_2) | (_cmp_cached_20) | (_cmp_cached_27))
            # 1h & 4h down move, 1h still high
            & ((_cmp_cached_10) | (_cmp_cached_19) | (_cmp_cached_30))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_10) | (_cmp_cached_60) | (_cmp("AROONU_14_4h", "<", 75.0)))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_10) | (_cmp_cached_12) | (_cmp_cached_27))
            # 1h down move, 1h high & overbought
            & ((_cmp_cached_10) | (_cmp_cached_9) | (_cmp_cached_29))
            # 1h down move, 4h downtrend, 1d overbought
            & ((_cmp_cached_10) | (_cmp_cached_139) | (_cmp_cached_35))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_11) | (_cmp_cached_19) | (_cmp_cached_42))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_19) | (_cmp_cached_39))
            # 1h & 1d down move, 1h high
            & ((_cmp_cached_11) | (_cmp_cached_64) | (_cmp_cached_18))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_11) | (_cmp_cached_88) | (_cmp_cached_44))
            # 1h down move, 1h & 1d high
            & ((_cmp_cached_11) | (_cmp_cached_12) | (_cmp_cached_38))
            # 1h down move, 1h high & overbought
            & ((_cmp_cached_11) | (_cmp_cached_18) | (_cmp_cached_61))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_11) | (_cmp_cached_18) | (_cmp_cached_98))
            # 1h down move, 4h & 1d high
            & ((_cmp_cached_11) | (_cmp_cached_32) | (_cmp_cached_9))
            # 1h down move, 1d high, 4h downtrend
            & ((_cmp_cached_11) | (_cmp_cached_42) | (_cmp("ROC_9_4h", ">", -70.0)))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_11) | (_cmp_cached_34) | (_cmp_cached_23))
            # 1h down move, 4h & 1d downtrend
            & ((_cmp_cached_11) | (_cmp_cached_72) | (_cmp_cached_146))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_8) | (_cmp_cached_47) | (_cmp_cached_12))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_8) | (_cmp_cached_18) | (_cmp_cached_78))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_8) | (_cmp_cached_13) | (_cmp_cached_40))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_8) | (_cmp_cached_20) | (_cmp_cached_50))
            # 1h down move, 1d high, 4h downtrend
            & ((_cmp_cached_8) | (_cmp_cached_38) | (_cmp_cached_139))
            # 1h down move, 1d high, 4h overbought
            & ((_cmp_cached_8) | (_cmp_cached_9) | (_cmp_cached_50))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_8) | (_cmp_cached_50) | (_cmp_cached_74))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_25) | (_cmp_cached_41) | (_cmp_cached_38))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_25) | (_cmp_cached_52) | (_cmp_cached_69))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_25) | (_cmp_cached_71) | (_cmp_cached_14))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_25) | (_cmp_cached_9) | (_cmp_cached_74))
            # 1h down move, 1h high, 4h downtrend
            & ((_cmp_cached_25) | (_cmp_cached_56) | (_cmp_cached_31))
            # 1h & 1d down move, 1h high
            & ((_cmp_cached_33) | (_cmp_cached_118) | (_cmp_cached_52))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_33) | (_cmp_cached_18) | (_cmp_cached_23))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_33) | (_cmp_cached_20) | (_cmp_cached_40))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_33) | (_cmp_cached_32) | (_cmp_cached_26))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_33) | (_cmp_cached_34) | (_cmp_cached_26))
            # 1h down move, 1d high, 4h overbought
            & ((_cmp_cached_65) | (_cmp_cached_9) | (_cmp_cached_73))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_63) | (_cmp_cached_88) | (_cmp_cached_150))
            # 1h down move, 1h & 1d high
            & ((_cmp_cached_63) | (_cmp_cached_18) | (_cmp_cached_9))
            # 4h & 1d down move, 15m still high
            & ((_cmp_cached_80) | (_cmp_cached_59) | (_cmp_cached_113))
            # 4h & 1d down move, 1h still not low enough
            & ((_cmp_cached_80) | (_cmp_cached_59) | (_cmp_cached_109))
            # 4h down move, 4h still high
            & ((_cmp_cached_80) | (_cmp_cached_43))
            # 4h down move, 1h still high, 4h downtrend
            & ((_cmp_cached_80) | (_cmp_cached_30) | (_cmp_cached_72))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_57) | (_cmp_cached_77) | (_cmp("STOCHRSIk_14_14_3_3_1d", "<", 40.0)))
            # 4h down move, 1h & 4h downtrend
            & ((_cmp_cached_57) | (_cmp("ROC_9_1h", ">", -10.0)) | (_cmp_cached_102))
            # 4h & 1d down move, 4h downtrend
            & ((_cmp_cached_4) | (_cmp_cached_66) | (_cmp_cached_31))
            # 4h & 1d down move, 1d downtrend
            & ((_cmp_cached_4) | (_cmp_cached_66) | (_cmp_cached_23))
            # 4h down move, 4h still high
            & ((_cmp_cached_4) | (_cmp_cached_43))
            # 4h down move, 1d still high, 1d downtrend
            & ((_cmp_cached_4) | (_cmp_cached_121) | (_cmp_cached_23))
            # 4h down move, 4h still not low enough, 1d downtrend
            & ((_cmp_cached_4) | (_cmp_cached_94) | (_cmp_cached_15))
            # 4h down move, 4h & 1d  downtrend
            & ((_cmp_cached_4) | (_cmp_cached_31) | (_cmp_cached_23))
            # 4h down move, 1h still high
            & ((_cmp_cached_5) | (_cmp_cached_49))
            # 4h down move, 1h still high, 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_30) | (_cmp_cached_23))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_54) | (_cmp_cached_15))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_6) | (_cmp_cached_43) | (_cmp_cached_44))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_6) | (_cmp_cached_45) | (_cmp_cached_35))
            # 4h & 1d down move, 1h high
            & ((_cmp_cached_21) | (_cmp_cached_64) | (_cmp_cached_52))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_19) | (_cmp_cached_43) | (_cmp_cached_44))
            # 4h down move, 1d high, 1d downtrend
            & ((_cmp_cached_41) | (_cmp("STOCHRSIk_14_14_3_3_1d", "<", 60.0)) | (_cmp_cached_23))
            # 4h down move, 1d high, 1d downtrend
            & ((_cmp_cached_76) | (_cmp_cached_42) | (_cmp_cached_141))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_60) | (_cmp_cached_110) | (_cmp_cached_23))
            # 1d down move, 4h high, 1d downtrend
            & ((_cmp_cached_59) | (_cmp_cached_58) | (_cmp_cached_150))
            # 1d down move, 1h high & overbought
            & ((_cmp_cached_133) | (_cmp_cached_83) | (_cmp_cached_61))
            # 1d down move, 1h high & overbought
            & ((_cmp_cached_118) | (_cmp_cached_45) | (_cmp_cached_69))
            # 4h downtrend, 1h & 4h high
            & ((_cmp("CMF_20_4h", ">", -0.30)) | (_cmp_cached_12) | (_cmp_cached_14))
            # 15m still high, 1h & 4h overbought
            & ((_cmp_cached_46) | (_cmp("ROC_9_1h", "<", 100.0)) | (_cmp_cached_115))
            # 15m & 1d high, 1d overbought
            & ((_cmp_cached_24) | (_cmp_cached_38) | (_cmp_cached_51))
            # 1h still high, 4h & 1d downtrend
            & ((_cmp_cached_86) | (_cmp_cached_31) | (_cmp_cached_44))
            # 1h & 4h high, 1d downtrend
            & ((_cmp_cached_12) | (_cmp_cached_14) | (_cmp_cached_15))
            # 1h & 4h high, 1d overbought
            & ((_cmp_cached_12) | (_cmp_cached_14) | (_cmp_cached_39))
            # 1h & 1d high, 1d overbought
            & ((_cmp_cached_12) | (_cmp_cached_38) | (_cmp_cached_74))
            # 1h high, 4h downtrend, 1d overbought
            & ((_cmp_cached_12) | (_cmp_cached_139) | (_cmp_cached_29))
            # 1h & 4h high, 4h overbought
            & ((_cmp_cached_18) | (_cmp_cached_14) | (_cmp_cached_50))
            # 1h high, 1d downtrend
            & ((_cmp_cached_18) | (_cmp_cached_146))
            # 1h high, 1h & 4h overbought
            & ((_cmp_cached_71) | (_cmp("ROC_9_1h", "<", 100.0)) | (_cmp_cached_115))
            # 4h & 1d high, 1d overbought
            & ((_cmp_cached_68) | (_cmp_cached_9) | (_cmp("ROC_9_1d", "<", 70.0)))
            # 4h high, 1h & 4h overbought
            & ((_cmp_cached_93) | (_cmp("ROC_9_1h", "<", 80.0)) | (_cmp_cached_114))
            # 4h high, 1h downtrend, 4h overbought
            & ((_cmp_cached_32) | (_cmp("ROC_9_1h", ">", -40.0)) | (_cmp_cached_115))
            # 4h & 1d high, 4h overbought
            & ((_cmp_cached_32) | (_cmp_cached_9) | (_cmp_cached_115))
            # 4h high, 1h & 4h overbought
            & ((_cmp_cached_32) | (_cmp_cached_61) | (_cmp_cached_26))
            # 4h & 1d high, 4h overbought
            & ((_cmp_cached_14) | (_cmp_cached_9) | (_cmp_cached_50))
            # 4h & 1d high, 1d overbought
            & ((_cmp_cached_14) | (_cmp_cached_9) | (_cmp_cached_40))
            # 1d high, 1h & 4h downtrend
            & ((_cmp_cached_9) | (_cmp_cached_124) | (_cmp_cached_72))
            # 1d high, 4h & 1d overbought
            & ((_cmp_cached_9) | (_cmp_cached_26) | (_cmp_cached_29))
            # 1h high, 1d overbought
            & ((_cmp_cached_56) | (_cmp_cached_40))
            # 1h high, 4h overbought
            & ((_cmp_cached_37) | (_cmp_cached_114))
            # 1h high, 4h & 1d downtrend
            & ((_cmp("STOCHRSIk_14_14_3_3_1h", "<", 85.0)) | (_cmp("ROC_9_4h", ">", -70.0)) | (_cmp_cached_150))
            # 4h high, 1h & 4h overbought
            & ((_cmp_cached_34) | (_cmp_cached_134) | (_cmp_cached_115))
            # 1d high, 4h & 1d overbought
            & ((_cmp_cached_62) | (_cmp_cached_26) | (_cmp_cached_29))
            # 1h & 4h overbought, 1d downtrend
            & ((_cmp_cached_134) | (_cmp_cached_98) | (_cmp_cached_23))
            # big drop in the last 20 days, 1d high, 1d downtrend
            & (
              _gt_mul("close", "high_max_20_1d", 0.20)
              | (_cmp_cached_106)
              | (_cmp_cached_141)
            )
          )

          # Logic
          long_entry_logic.append(
            (_cmp("RSI_14", "<", 40.0))
            & (_cmp("MFI_14", "<", 40.0))
            & (_cmp("AROONU_14", "<", 25.0))
            & (df["EMA_26"] > df["EMA_12"])
            & ((df["EMA_26"] - df["EMA_12"]) > (df["open"] * 0.024))
            & _ema_26_12_spread_gt_open_pct
            & (df["close"] < (df["EMA_20"] * 0.960))
            & (df["close"] < (df["BBL_20_2.0"] * 0.999))
          )

        # Condition #44 - Quick mode (Long).
        if long_entry_condition_index == 44:
          # Protections
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          # long_entry_logic.append(df["protections_long_global"] == True)

          long_entry_logic.append(
            # 5m & 1h & 4h down move
            ((_cmp_cached_48) | (_cmp_cached_2) | (_cmp_cached_5))
            # 15m & 1h & 4h down move
            & ((_cmp_cached_7) | (_cmp_cached_36) | (_cmp_cached_4))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_7) | (_cmp_cached_36) | (_cmp_cached_88))
            # 15m & 1h & 4h down move
            & ((_cmp_cached_7) | (_cmp_cached_22) | (_cmp_cached_4))
            # 15m & 1h down move, 1d downtrend
            & ((_cmp_cached_7) | (_cmp_cached_22) | (_cmp_cached_23))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_7) | (_cmp_cached_1) | (_cmp_cached_9))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_7) | (_cmp_cached_10) | (_cmp_cached_18))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_7) | (_cmp_cached_4) | (_cmp_cached_67))
            # 15m & 4h down move, 15m downtrend
            & ((_cmp_cached_7) | (_cmp_cached_4) | (_cmp("ROC_9_15m", ">", -30.0)))
            # 15m & 4h down move, 1h downtrend
            & ((_cmp_cached_7) | (_cmp_cached_4) | (_cmp_cached_120))
            # 15m & 4h down move, 1h still high
            & ((_cmp_cached_7) | (_cmp_cached_5) | (_cmp_cached_49))
            # 15m & 4h down move, 1h still high
            & ((_cmp_cached_7) | (_cmp_cached_47) | (_cmp_cached_82))
            # 15m down move, 1h still high, 1d overbought
            & ((_cmp_cached_7) | (_cmp_cached_86) | (_cmp("ROC_9_1d", "<", 70.0)))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_7) | (_cmp_cached_14) | (_cmp_cached_115))
            # 15m down move, 1h high
            & ((_cmp_cached_7) | (_cmp_cached_56))
            # 15m down move, 4h high, 15m downtrend
            & ((_cmp_cached_7) | (_cmp_cached_58) | (_cmp("ROC_9_15m", ">", -30.0)))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_17) | (_cmp_cached_2) | (_cmp_cached_12))
            # 15m & 1h down move, 1h downtrend
            & ((_cmp_cached_0) | (_cmp_cached_1) | (_cmp_cached_120))
            # 15m & 4h down move, 1h still not low enough
            & ((_cmp_cached_0) | (_cmp_cached_4) | (_cmp_cached_109))
            # 15m down move, 4h overbought
            & ((_cmp_cached_0) | (_cmp_cached_50))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_21) | (_cmp_cached_13))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_47) | (_cmp("AROONU_14_4h", "<", 75.0)))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_76) | (_cmp_cached_32))
            # 15m down move, 4h & 1d downtrend
            & ((_cmp_cached_3) | (_cmp_cached_102) | (_cmp_cached_44))
            # 15m down move, 1h high & overbought
            & ((_cmp_cached_28) | (_cmp_cached_38) | (_cmp_cached_29))
            # 1h & 4h down move, 1h still not low enough
            & ((_cmp_cached_36) | (_cmp_cached_80) | (_cmp("AROONU_14_1h", "<", 20.0)))
            # 1h & 4h down move
            & ((_cmp_cached_36) | (_cmp_cached_57))
            # 1h & 4h down move, 1d still high
            & ((_cmp_cached_36) | (_cmp_cached_4) | (_cmp_cached_121))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_36) | (_cmp_cached_4) | (_cmp("STOCHRSIk_14_14_3_3_1d", "<", 60.0)))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_36) | (_cmp_cached_6) | (_cmp("AROONU_14_1d", "<", 60.0)))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_36) | (_cmp_cached_6) | (_cmp_cached_105))
            # 1h down move, 1h & 4h still high
            & ((_cmp_cached_36) | (_cmp_cached_49) | (_cmp_cached_43))
            # 1h down move, 1h still high, 1h downtrend
            & ((_cmp_cached_36) | (_cmp_cached_49) | (_cmp_cached_120))
            # 1h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_36) | (_cmp_cached_54) | (_cmp("ROC_9_1h", ">", -15.0)))
            # 1h downtrend, 4h high
            & ((_cmp_cached_36) | (_cmp_cached_58))
            # 1h down move, 1h & 4h downtrend
            & ((_cmp_cached_36) | (_cmp_cached_120) | (_cmp_cached_31))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_22) | (_cmp_cached_4) | (_cmp_cached_43))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_22) | (_cmp_cached_4) | (_cmp_cached_62))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_22) | (_cmp_cached_19) | (_cmp_cached_110))
            # 1h & 1d down move, 1d downtrend
            & ((_cmp_cached_22) | (_cmp("RSI_3_1d", ">", 5.0)) | (_cmp_cached_15))
            # 1h down move, 1h high
            & ((_cmp_cached_22) | (_cmp_cached_88))
            # 1h down move, 4h high
            & ((_cmp_cached_22) | (_cmp_cached_13))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_22) | (_cmp_cached_38) | (_cmp_cached_51))
            # 1h down move, 4h & 1d downtrend
            & ((_cmp_cached_22) | (_cmp_cached_31) | (_cmp_cached_149))
            # 1h down move, 1d overbought
            & ((_cmp_cached_22) | (_cmp_cached_29))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp_cached_15))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_1) | (_cmp_cached_5) | (_cmp_cached_110))
            # 1h & 4h down move, 1h still high
            & ((_cmp_cached_1) | (_cmp_cached_5) | (_cmp_cached_49))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_1) | (_cmp_cached_6) | (_cmp_cached_54))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_6) | (_cmp_cached_44))
            # 1h & 4h down move, 1h downtrend
            & ((_cmp_cached_1) | (_cmp_cached_6) | (_cmp("ROC_9_1h", ">", -25.0)))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_1) | (_cmp_cached_21) | (_cmp_cached_13))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_1) | (_cmp_cached_87) | (_cmp_cached_12))
            # 1h & 1d down move, 4h still high
            & ((_cmp_cached_1) | (_cmp_cached_66) | (_cmp_cached_67))
            # 1h & 1d down move, 1h still high
            & ((_cmp_cached_1) | (_cmp_cached_59) | (_cmp_cached_49))
            # 1h & 1d down move, 1h high
            & ((_cmp_cached_1) | (_cmp_cached_118) | (_cmp_cached_12))
            # 1h down move, 1h still high, 4h downtrend
            & ((_cmp_cached_1) | (_cmp_cached_86) | (_cmp_cached_72))
            # 1h down move, 1h still high, 1d high
            & ((_cmp_cached_1) | (_cmp_cached_49) | (_cmp_cached_38))
            # 1h down move, 1h high, 1h downtrend
            & ((_cmp_cached_1) | (_cmp_cached_88) | (_cmp("ROC_9_1h", ">", -10.0)))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_12) | (_cmp_cached_23))
            # 1h down move, 1h high
            & ((_cmp_cached_1) | (_cmp_cached_18))
            # 1h down move, 4h still high, 15m downtrend
            & ((_cmp_cached_1) | (_cmp_cached_43) | (_cmp("CMF_20_15m", ">", -0.40)))
            # 1h down move, 4h still high, 4h downtrend
            & ((_cmp_cached_1) | (_cmp_cached_43) | (_cmp_cached_72))
            # 1h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_43) | (_cmp_cached_23))
            # 1h down move, 4h & 1d high
            & ((_cmp_cached_1) | (_cmp_cached_68) | (_cmp_cached_9))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_1) | (_cmp_cached_32) | (_cmp_cached_29))
            # 1h down move, 4h high
            & ((_cmp_cached_1) | (_cmp_cached_14))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_1) | (_cmp_cached_9) | (_cmp_cached_99))
            # 1h down move, 4h overbought
            & ((_cmp_cached_1) | (_cmp_cached_27))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_1) | (_cmp_cached_34) | (_cmp_cached_26))
            # 1h down move, 4h & 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_72) | (_cmp_cached_95))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_2) | (_cmp_cached_76) | (_cmp_cached_20))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_2) | (_cmp_cached_49) | (_cmp_cached_44))
            # 1h down move, 1h & 1d high
            & ((_cmp_cached_2) | (_cmp_cached_88) | (_cmp_cached_103))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_2) | (_cmp_cached_88) | (_cmp_cached_23))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_2) | (_cmp_cached_88) | (_cmp_cached_35))
            # 1h down move, 1h high, 4h downtrend
            & ((_cmp_cached_2) | (_cmp_cached_12) | (_cmp_cached_102))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_2) | (_cmp_cached_20) | (_cmp_cached_115))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_2) | (_cmp_cached_42) | (_cmp_cached_29))
            # 1h down move, 1h & 4h downtrend
            & ((_cmp_cached_2) | (_cmp_cached_124) | (_cmp_cached_72))
            # 1h down move, 1h & 4h overbought
            & ((_cmp_cached_2) | (_cmp_cached_27) | (_cmp_cached_35))
            # 1h down move, 1h & 4h overbought
            & ((_cmp_cached_2) | (_cmp_cached_26) | (_cmp_cached_39))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_10) | (_cmp_cached_60) | (_cmp_cached_32))
            # 1h down move, 1h still high, 4h downtrend
            & ((_cmp_cached_10) | (_cmp_cached_86) | (_cmp_cached_72))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_10) | (_cmp_cached_34) | (_cmp_cached_44))
            # 1h down move, 4h & 1d downtrend
            & ((_cmp_cached_10) | (_cmp_cached_72) | (_cmp_cached_44))
            # 1h & 4h down ove, 4h high
            & ((_cmp_cached_11) | (_cmp_cached_76) | (_cmp_cached_32))
            # 1h down move, 1h & 1d high
            & ((_cmp_cached_11) | (_cmp_cached_12) | (_cmp_cached_42))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_11) | (_cmp_cached_20) | (_cmp_cached_15))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_11) | (_cmp_cached_38) | (_cmp_cached_29))
            # 1h down move, 1h still high, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_30) | (_cmp_cached_40))
            # 1h down move, 1h downtrend, 4h overbought
            & ((_cmp_cached_11) | (_cmp_cached_120) | (_cmp_cached_26))
            # 1h down move, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_74))
            # 1h down move, 4h high
            & ((_cmp_cached_8) | (_cmp_cached_14))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_8) | (_cmp_cached_34) | (_cmp_cached_27))
            # 4h down move, 4h still high, 1d high
            & ((_cmp_cached_80) | (_cmp_cached_43) | (_cmp_cached_9))
            # 4h down move, 1d still high, 4h downtrend
            & ((_cmp_cached_80) | (_cmp_cached_117) | (_cmp_cached_72))
            # 4h down move, 1d overbought
            & ((_cmp_cached_80) | (_cmp_cached_74))
            # 4h down move, 1h still high
            & ((_cmp_cached_57) | (_cmp_cached_82))
            # 4h down move, 1h & 4h downtrend
            & ((_cmp_cached_57) | (_cmp("ROC_9_1h", ">", -15.0)) | (_cmp_cached_31))
            # 4h down move, 4h downtrend
            & ((_cmp_cached_57) | (_cmp_cached_139))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_4) | (_cmp_cached_53) | (_cmp_cached_42))
            # 4h down move, 1d high, 4h downtrend
            & ((_cmp_cached_4) | (_cmp_cached_38) | (_cmp_cached_31))
            # 4h down move, 1h & 4h downtrend
            & ((_cmp_cached_4) | (_cmp_cached_124) | (_cmp_cached_72))
            # 4h down move, 4h still not low enough, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_145) | (_cmp_cached_35))
            # 4h down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_68))
            # 4h down move, 4h still high, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_67) | (_cmp_cached_40))
            # 15m down move, 4h still high, 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_43) | (_cmp_cached_44))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_5) | (_cmp_cached_42) | (_cmp_cached_69))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_19) | (_cmp_cached_43) | (_cmp_cached_44))
            # 4h down move, 4h & 1d high
            & ((_cmp_cached_19) | (_cmp_cached_20) | (_cmp_cached_9))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_19) | (_cmp_cached_9) | (_cmp_cached_51))
            # 4h down move, 1h high & overbought
            & ((_cmp_cached_41) | (_cmp_cached_38) | (_cmp_cached_29))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_60) | (_cmp_cached_110) | (_cmp_cached_23))
            # 4h down move, 4h high, 1d overbought
            & ((_cmp_cached_60) | (_cmp_cached_13) | (_cmp_cached_40))
            # 4h down move, 4h high
            & ((_cmp_cached_60) | (_cmp_cached_58))
            # 4h down move, 4h overbought
            & ((_cmp_cached_60) | (_cmp_cached_123))
            # 4h downtrend, 4h high
            & ((_cmp("CMF_20_4h", ">", -0.50)) | (_cmp_cached_13))
            # 1h & 1d high, 4h downtrend
            & ((_cmp_cached_86) | (_cmp_cached_45) | (_cmp_cached_31))
            # 1h still high, 1h & 4h downtrend
            & ((_cmp_cached_86) | (_cmp_cached_120) | (_cmp_cached_72))
            # 1h & 4h high, 1d overbought
            & ((_cmp_cached_12) | (_cmp_cached_14) | (_cmp_cached_39))
            # 1h high, 4h & 1d downtrend
            & ((_cmp_cached_12) | (_cmp_cached_31) | (_cmp_cached_95))
            # 1h high, 4h downtrend
            & ((_cmp_cached_12) | (_cmp_cached_139))
            # 1h & 1d high, 1d overbought
            & ((_cmp_cached_18) | (_cmp_cached_38) | (_cmp_cached_69))
            # 1h & 1d high, 1h downtrend
            & ((_cmp_cached_18) | (_cmp_cached_9) | (_cmp_cached_120))
            # 4h & 1d high, 1h downtrend
            & ((_cmp_cached_20) | (_cmp_cached_9) | (_cmp_cached_124))
            # 4h & 1d high, 4h overbought
            & ((_cmp_cached_20) | (_cmp_cached_9) | (_cmp_cached_73))
            # 4h high, 1h downtrend
            & ((_cmp_cached_20) | (_cmp("ROC_9_1h", ">", -40.0)))
            # 4h high & overbought
            & ((_cmp_cached_20) | (_cmp_cached_115))
            # 4h high, 1d downtrend
            & ((_cmp_cached_20) | (_cmp_cached_23))
            # 1d still high, 1d downtrend
            & ((_cmp_cached_121) | (_cmp_cached_23))
            # 1d high, 15m downtrend
            & ((_cmp_cached_45) | (_cmp("ROC_9_15m", ">", -50.0)))
            # 1d high, 1h downtrend
            & ((_cmp_cached_45) | (_cmp("ROC_9_1h", ">", -70.0)))
            # 1d high, 4h downtrend
            & ((_cmp_cached_42) | (_cmp("ROC_9_4h", ">", -70.0)))
            # 1d high, 4h downtrend
            & ((_cmp_cached_38) | (_cmp_cached_139))
            # 1d high & overbought
            & ((_cmp_cached_38) | (_cmp_cached_74))
            # 1d high, 4h & 1d overbought
            & ((_cmp_cached_9) | (_cmp_cached_26) | (_cmp_cached_69))
            # 1h still high, 4h & 1d downtrend
            & ((_cmp_cached_30) | (_cmp_cached_31) | (_cmp_cached_95))
            # 1h high, 15m downtrend
            & ((_cmp_cached_56) | (_cmp("ROC_9_15m", ">", -30.0)))
            # 4h high, 1d downtrend
            & ((_cmp_cached_58) | (_cmp_cached_150))
            # 1d high, 1h downtrend
            & ((_cmp_cached_62) | (_cmp_cached_120))
            # 1d high, 1d downtrend
            & ((_cmp("STOCHRSIk_14_14_3_3_1d", "<", 60.0)) | (_cmp_cached_23))
            # 15m downtrend, 1d overbought
            & ((_cmp("ROC_9_15m", ">", -60.0)) | (_cmp_cached_74))
            # 1h downtrend, 1d overbought
            & ((_cmp("ROC_9_1h", ">", -60.0)) | (_cmp_cached_74))
            # big drop in the last 20 days, 1d high, 1d downtrend
            & (
              _gt_mul("close", "high_max_20_1d", 0.20)
              | (_cmp_cached_106)
              | (_cmp_cached_141)
            )
          )

          # Logic
          long_entry_logic.append(
            (_cmp("RSI_3", "<", 40.0))
            & (_cmp("RSI_3_15m", "<", 50.0))
            & (_cmp("AROONU_14_15m", "<", 25.0))
            & (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 20.0))
            & (df["EMA_26_15m"] > df["EMA_12_15m"])
            & ((df["EMA_26_15m"] - df["EMA_12_15m"]) > (df["open_15m"] * 0.050))
            & _ema_26_12_15m_spread_gt_open_pct
          )

        # Condition #45 - Quick mode (Long).
        if long_entry_condition_index == 45:
          # Protections
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          long_entry_logic.append(df["protections_long_global"] == True)

          # 5m & 15m down move, 4h still high
          long_entry_logic.append(
            (_cmp_cached_48) | (_cmp_cached_3) | (_cmp_cached_54)
          )
          # 15m & 1h down move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_7) | (_cmp_cached_11) | (_cmp_cached_82)
          )
          # 5m & 4h & 1d down move
          long_entry_logic.append((_cmp_cached_48) | (_cmp_cached_6) | (_cmp_cached_53))
          # 15m & 1h down move, 4h high
          long_entry_logic.append(
            (_cmp_cached_7) | (_cmp_cached_8) | (_cmp_cached_105)
          )
          # 15m & 4h down move
          long_entry_logic.append((_cmp_cached_7) | (_cmp_cached_4))
          # 15m & 4h down move, 4h still not low enough
          long_entry_logic.append((_cmp_cached_7) | (_cmp_cached_19) | (_cmp("RSI_14_4h", "<", 35.0)))
          # 15m down move, 4h still high, 15m downtrend
          long_entry_logic.append((_cmp_cached_7) | (_cmp_cached_67) | (_cmp("CMF_20_15m", ">", -0.35)))
          # 15m & 1h down move
          long_entry_logic.append((_cmp_cached_17) | (_cmp_cached_2))
          # 15m & 1h down move, 4h high
          long_entry_logic.append(
            (_cmp_cached_17) | (_cmp_cached_33) | (_cmp_cached_34)
          )
          # 15m down move, 1h still not low enough
          long_entry_logic.append((_cmp_cached_17) | (_cmp_cached_138))
          # 15m down move, 4h high
          long_entry_logic.append((_cmp_cached_17) | (_cmp_cached_32))
          # 15m & 1h & 1d down move
          long_entry_logic.append((_cmp_cached_0) | (_cmp_cached_1) | (_cmp_cached_66))
          # 15m & 1h down move, 1d overbought
          long_entry_logic.append((_cmp_cached_0) | (_cmp_cached_10) | (_cmp_cached_51))
          # 15m & 1h down move, 1h high
          long_entry_logic.append((_cmp_cached_0) | (_cmp_cached_65) | (_cmp_cached_18))
          # 15m & 1h down move, 1h high
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp("RSI_3_1h", ">", 65.0)) | (_cmp_cached_37)
          )
          # 15m & 4h down move, 4h still not low enough
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp_cached_4) | (_cmp_cached_94)
          )
          # 15m & 4h down move, 1d high
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp_cached_4) | (_cmp_cached_84)
          )
          # 15m & 4h down move, 4h still high
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp_cached_19) | (_cmp_cached_79)
          )
          # 15m down move, 1h & 4h high
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp_cached_12) | (_cmp_cached_14)
          )
          # 15m down move, 1h high & overbought
          long_entry_logic.append((_cmp_cached_0) | (_cmp_cached_12) | (_cmp_cached_61))
          # 15m down move, 1h high, 4h overbought
          long_entry_logic.append((_cmp_cached_0) | (_cmp_cached_12) | (_cmp_cached_26))
          # 15m down move, 4h & 1d high
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp("AROONU_14_4h", "<", 75.0)) | (_cmp_cached_9)
          )
          # 15m down move, 4h high, 1h overbought
          long_entry_logic.append((_cmp_cached_0) | (_cmp_cached_14) | (_cmp_cached_61))
          # 15m down move, 4h high & overbought
          long_entry_logic.append((_cmp_cached_0) | (_cmp_cached_14) | (_cmp_cached_26))
          # 15m & 1h down move, 4h high
          long_entry_logic.append((_cmp_cached_3) | (_cmp_cached_2) | (_cmp_cached_13))
          # 15m down move, 1h & 4h high
          long_entry_logic.append(
            (_cmp_cached_3) | (_cmp_cached_12) | (_cmp_cached_55)
          )
          # 15m down move, 4h high, 1d overbought
          long_entry_logic.append((_cmp_cached_3) | (_cmp_cached_13) | (_cmp_cached_35))
          # 15m & 1h down move, 1d overbought
          long_entry_logic.append((_cmp_cached_28) | (_cmp_cached_33) | (_cmp_cached_69))
          # 15m & 1h down move, 1h high
          long_entry_logic.append((_cmp_cached_70) | (_cmp_cached_8) | (_cmp_cached_12))
          # 1h down move, 4h still not low enough
          long_entry_logic.append((_cmp_cached_36) | (_cmp_cached_145))
          # 1h & 4h down move, 1h still not low enough
          long_entry_logic.append((_cmp_cached_22) | (_cmp_cached_19) | (_cmp("AROONU_14_1h", "<", 20.0)))
          # 1h down move, 1h still not low enough
          long_entry_logic.append((_cmp_cached_22) | (_cmp_cached_138))
          # 1h down move, 1h still not low enough
          long_entry_logic.append((_cmp_cached_22) | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 25.0)))
          # 1h & 4h down move
          long_entry_logic.append((_cmp_cached_1) | (_cmp_cached_5))
          # 1h & 4h down move, 4h still not low enough
          long_entry_logic.append(
            (_cmp_cached_1) | (_cmp_cached_6) | (_cmp_cached_94)
          )
          # 1h & 4h down move, 4h still high
          long_entry_logic.append((_cmp_cached_1) | (_cmp_cached_21) | (_cmp_cached_43))
          # 1h & 4h down move, 4h still not low enough
          long_entry_logic.append((_cmp_cached_1) | (_cmp_cached_19) | (_cmp_cached_110))
          # 1h & 4h down move, 4h high
          long_entry_logic.append((_cmp_cached_1) | (_cmp_cached_47) | (_cmp_cached_68))
          # 1h & 1d down move, 4h still high
          long_entry_logic.append((_cmp_cached_1) | (_cmp_cached_66) | (_cmp_cached_67))
          # 1h & 1d down move, 5m moving down
          long_entry_logic.append((_cmp_cached_1) | (_cmp_cached_59) | (_cmp("ROC_2", ">", -0.0)))
          # 1h & 1d down move, 4h still high
          long_entry_logic.append((_cmp_cached_1) | (_cmp_cached_77) | (_cmp_cached_43))
          # 15m & 1d down move, 1d high
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp_cached_77) | (_cmp_cached_106)
          )
          # 1h & 4h down move, 4h still not low enough
          long_entry_logic.append(
            (_cmp_cached_36) | (_cmp_cached_21) | (_cmp_cached_94)
          )
          # 1h down move, 1h still not low enough, 1d high
          long_entry_logic.append(
            (_cmp_cached_1) | (_cmp_cached_132) | (_cmp_cached_103)
          )
          # 1h down move, 1h still not low enough
          long_entry_logic.append((_cmp_cached_1) | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 25.0)))
          # 1h down move, 4h high
          long_entry_logic.append((_cmp_cached_1) | (_cmp_cached_93))
          # 1h down move, 1d high & overbought
          long_entry_logic.append((_cmp_cached_1) | (_cmp_cached_45) | (_cmp_cached_35))
          # 1h & 4h down move, 4h still high
          long_entry_logic.append((_cmp_cached_2) | (_cmp_cached_5) | (_cmp_cached_67))
          # 1h & 4h down move, 1d high
          long_entry_logic.append(
            (_cmp_cached_2) | (_cmp_cached_6) | (_cmp_cached_106)
          )
          # 1h & 4h & 1d down move
          long_entry_logic.append((_cmp_cached_2) | (_cmp_cached_6) | (_cmp_cached_77))
          # 1h & 4h down move, 1d high
          long_entry_logic.append((_cmp_cached_2) | (_cmp_cached_19) | (_cmp_cached_9))
          # 1h down move, 1h still high
          long_entry_logic.append((_cmp_cached_2) | (_cmp_cached_49))
          # 1h down move, 1d high, 4h downtrend
          long_entry_logic.append((_cmp_cached_2) | (_cmp_cached_45) | (_cmp_cached_31))
          # 1h down move, 1h still high
          long_entry_logic.append((_cmp_cached_2) | (_cmp_cached_109))
          # 1h & 4h down move, 1d overbought
          long_entry_logic.append((_cmp_cached_10) | (_cmp_cached_6) | (_cmp_cached_39))
          # 1h down move, 4h high
          long_entry_logic.append((_cmp_cached_10) | (_cmp_cached_32))
          # 1h down move, 4h still high
          long_entry_logic.append((_cmp_cached_10) | (_cmp_cached_54))
          # 1h & 4h down move, 1h high
          long_entry_logic.append(
            (_cmp_cached_11) | (_cmp_cached_19) | (_cmp_cached_112)
          )
          # 1h & 4h down move, 4h high
          long_entry_logic.append((_cmp_cached_11) | (_cmp_cached_47) | (_cmp_cached_13))
          # 1h down move, 1h high
          long_entry_logic.append((_cmp_cached_11) | (_cmp_cached_12))
          # 1h down move, 4h high
          long_entry_logic.append((_cmp_cached_11) | (_cmp_cached_34))
          # 1h & 1d down move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_8) | (_cmp("RSI_3_1d", ">", 50.0)) | (_cmp_cached_30)
          )
          # 1h down move, 4h high
          long_entry_logic.append((_cmp_cached_8) | (_cmp("RSI_14_4h", "<", 80.0)))
          # 14 down move, 1h high
          long_entry_logic.append((_cmp_cached_8) | (_cmp_cached_18))
          # 1h down move, 4h high
          long_entry_logic.append((_cmp_cached_8) | (_cmp_cached_20))
          # 1h down move, 4h high
          long_entry_logic.append((_cmp_cached_8) | (_cmp_cached_34))
          # 1h down move, 4h & 1d high
          long_entry_logic.append(
            (_cmp_cached_25) | (_cmp_cached_34) | (_cmp_cached_84)
          )
          # 1h down move, 1h still high, 1d overbought
          long_entry_logic.append((_cmp_cached_33) | (_cmp_cached_49) | (_cmp_cached_35))
          # 1h down move, 1h & 4h high
          long_entry_logic.append((_cmp_cached_65) | (_cmp_cached_12) | (_cmp_cached_32))
          # 1h down move, 1h & 4h high
          long_entry_logic.append(
            (_cmp_cached_97) | (_cmp_cached_56) | (_cmp_cached_32)
          )
          # 4h down move, 1d high
          long_entry_logic.append((_cmp_cached_57) | (_cmp_cached_9))
          # 4h & 1d down move, 1d still high
          long_entry_logic.append(
            (_cmp_cached_4) | (_cmp_cached_64) | (_cmp_cached_117)
          )
          # 4h downmove, 4h still high
          long_entry_logic.append((_cmp_cached_4) | (_cmp_cached_67))
          # 4h down move, 1h still high, 1d downtrend
          long_entry_logic.append(
            (_cmp_cached_4) | (_cmp_cached_82) | (_cmp_cached_15)
          )
          # 4h down move, 1h & 1d downtrend
          long_entry_logic.append((_cmp_cached_4) | (_cmp_cached_120) | (_cmp_cached_15))
          # 4h & 1d down move, 1d still high
          long_entry_logic.append((_cmp_cached_5) | (_cmp_cached_133) | (_cmp("RSI_14_1d", "<", 50.0)))
          # 4h down move, 1h still not low enough
          long_entry_logic.append((_cmp_cached_5) | (_cmp_cached_138))
          # 4h & 1d down move, 1d high
          long_entry_logic.append((_cmp_cached_6) | (_cmp_cached_53) | (_cmp_cached_42))
          # 4h down move, 4h still high, 1d high
          long_entry_logic.append((_cmp_cached_6) | (_cmp_cached_43) | (_cmp_cached_9))
          # 4h down move, 1d high
          long_entry_logic.append((_cmp_cached_21) | (_cmp_cached_62))
          # 4h down move, 4h & 1d downtrend
          long_entry_logic.append((_cmp_cached_21) | (_cmp_cached_31) | (_cmp_cached_15))
          # 4h down move, 4h & 1d high
          long_entry_logic.append((_cmp_cached_19) | (_cmp_cached_20) | (_cmp_cached_9))
          # 4h down move, 1h high
          long_entry_logic.append((_cmp_cached_47) | (_cmp_cached_56))
          # 4h down move, 4h still high
          long_entry_logic.append((_cmp_cached_60) | (_cmp_cached_54))
          # 4h down move, 1h high
          long_entry_logic.append((_cmp_cached_87) | (_cmp_cached_37))
          # 4h down move, 4h high
          long_entry_logic.append((_cmp_cached_87) | (_cmp_cached_34))
          # 1d down move, 1h still not low enough
          long_entry_logic.append((_cmp("RSI_3_1d", ">", 5.0)) | (_cmp_cached_109))
          # 1d down move, 1h still not low enough
          long_entry_logic.append((_cmp_cached_59) | (_cmp_cached_109))
          # 1d down move, 4h still high
          long_entry_logic.append((_cmp_cached_59) | (_cmp_cached_54))
          # 1d down move, 1h high & overbought
          long_entry_logic.append(
            (_cmp_cached_133) | (_cmp_cached_83) | (_cmp_cached_61)
          )
          # 15m still high, 1h & 4h high
          long_entry_logic.append(
            (_cmp("RSI_14_15m", "<", 40.0)) | (_cmp_cached_18) | (_cmp_cached_32)
          )
          # 1h & 4h high, 4h overbought
          long_entry_logic.append((_cmp_cached_12) | (_cmp_cached_14) | (_cmp_cached_26))
          # 4h high, 1d overbought
          long_entry_logic.append((_cmp_cached_13) | (_cmp_cached_69))
          # 4h high, 1h & 1d downtrend
          long_entry_logic.append((_cmp_cached_13) | (_cmp_cached_120) | (_cmp_cached_15))
          # 4h high, 1h & 4h overbought
          long_entry_logic.append((_cmp_cached_20) | (_cmp_cached_61) | (_cmp_cached_27))
          # 4h high & overbought
          long_entry_logic.append((_cmp_cached_32) | (_cmp_cached_114))
          # 1d high, 4h & 1d downtrend
          long_entry_logic.append((_cmp_cached_42) | (_cmp_cached_31) | (_cmp_cached_15))
          # 1h high, 4h overbought
          long_entry_logic.append((_cmp_cached_37) | (_cmp_cached_114))
          # 4h high, 1h & 1d downtrend
          long_entry_logic.append(
            (_cmp_cached_58) | (_cmp_cached_120) | (_cmp_cached_15)
          )
          # 4h high, 1h & 4h overbought
          long_entry_logic.append(
            (_cmp_cached_34) | (_cmp_cached_61) | (_cmp_cached_27)
          )
          # 4h high, 4h & 1d overbought
          long_entry_logic.append(
            (_cmp_cached_34) | (_cmp_cached_50) | (_cmp_cached_51)
          )
          # 1d top wick, 4h still high
          long_entry_logic.append((_cmp("top_wick_pct_1d", "<", 40.0)) | (_cmp_cached_43))
          # pump, 4h still high
          long_entry_logic.append(
            _range_lt("high_max_24_4h", "low_min_24_4h", 2.0)
            | (_cmp_cached_54)
          )
          # pump, drop but not yet near the previous lows
          long_entry_logic.append(
            _range_lt("high_max_24_4h", "low_min_24_4h", 2.0)
            | _gt_mul("close", "high_max_6_4h", 0.75)
            | (df["close"] < (df["low_min_24_4h"] * 1.25))
          )
          # pump, drop but not yet near the previous lows
          long_entry_logic.append(
            _range_lt("high_max_12_1d", "low_min_12_1d", 2.0)
            | _gt_mul("close", "high_max_24_4h", 0.70)
            | (df["close"] < (df["low_min_12_1d"] * 1.25))
          )
          # big drop in last hour
          long_entry_logic.append(_gt_mul("close", "close_max_12", 0.50))
          # big drop in last hour, 1d down move
          long_entry_logic.append(_gt_mul("close", "close_max_12", 0.80) | (_cmp_cached_59))
          # big drop in the last 12 hours, 4h still high
          long_entry_logic.append(_gt_mul("close", "high_max_12_1h", 0.50) | (_cmp_cached_43))
          # big drop in the last 6 days, 1h still high
          long_entry_logic.append(_gt_mul("close", "high_max_6_1d", 0.25) | (_cmp_cached_49))
          # big drop in the last 12 days, 1h down move
          long_entry_logic.append(_gt_mul("close", "high_max_12_1d", 0.45) | (_cmp_cached_22))
          # big drop in the last 12 days, 4h down move
          long_entry_logic.append(_gt_mul("close", "high_max_12_1d", 0.40) | (_cmp_cached_5))
          # big drop in the last 12 days, 1h still high
          long_entry_logic.append(_gt_mul("close", "high_max_12_1d", 0.25) | (_cmp("AROONU_14_1h", "<", 75.0)))
          # big drop in the last 20 days, 1h down move
          long_entry_logic.append(_gt_mul("close", "high_max_20_1d", 0.35) | (_cmp_cached_1))
          # big drop in the last 20 days, 1h down move
          long_entry_logic.append(_gt_mul("close", "high_max_20_1d", 0.25) | (_cmp_cached_2))
          # big drop in the last 20 days, 1h down move
          long_entry_logic.append(_gt_mul("close", "high_max_20_1d", 0.10) | (_cmp_cached_10))
          # big drop in the last 20 days, 1d high, 1d downtrend
          long_entry_logic.append(
            _gt_mul("close", "high_max_20_1d", 0.20)
            | (_cmp_cached_106)
            | (_cmp_cached_141)
          )
          # big drop in the last 30 days, 4h down move, 4h still high
          long_entry_logic.append(
            _gt_mul("close", "high_max_30_1d", 0.25) | (_cmp_cached_76) | (_cmp_cached_110)
          )

          # Logic
          long_entry_logic.append(_cmp("RSI_3", "<", 50.0))
          long_entry_logic.append(_cmp("AROONU_14_15m", "<", 25.0))
          long_entry_logic.append(_cmp("STOCHRSIk_14_14_3_3_15m", "<", 20.0))
          long_entry_logic.append(df["close_15m"] < (df["EMA_20_15m"] * 0.924))

        # Condition #46 - Quick mode (Long).
        if long_entry_condition_index == 46:
          # Protections
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          long_entry_logic.append(df["protections_long_global"] == True)

          # 5m & 1h down move
          long_entry_logic.append((_cmp_cached_7) | (_cmp_cached_22))
          # 15m & 4h down move, 4h still high
          long_entry_logic.append((_cmp_cached_7) | (_cmp_cached_6) | (_cmp_cached_67))
          # 15m & 4h down move
          long_entry_logic.append((_cmp_cached_17) | (_cmp_cached_4))
          # 15m & 4h down move, 4h still high
          long_entry_logic.append((_cmp_cached_17) | (_cmp_cached_6) | (_cmp_cached_67))
          # 15m & 4h down move, 4h still high
          long_entry_logic.append((_cmp_cached_17) | (_cmp_cached_19) | (_cmp_cached_43))
          # 15m & 1h & 4h down move
          long_entry_logic.append((_cmp_cached_0) | (_cmp_cached_1) | (_cmp_cached_19))
          # 15m & 1h down move, 4h still not low enough
          long_entry_logic.append((_cmp_cached_0) | (_cmp_cached_1) | (_cmp("RSI_14_4h", "<", 30.0)))
          # 15m & 1h & 4h down move
          long_entry_logic.append((_cmp_cached_0) | (_cmp_cached_10) | (_cmp_cached_6))
          # 15m & 1h down move, 1h still high
          long_entry_logic.append((_cmp_cached_0) | (_cmp_cached_10) | (_cmp_cached_86))
          # 15m & 1h down move, 4h still high
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp_cached_11) | (_cmp_cached_79)
          )
          # 15m & 4h down move, 1d high
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp_cached_5) | (_cmp_cached_62)
          )
          # 15m & 4h down move, 4h downtrend
          long_entry_logic.append((_cmp_cached_0) | (_cmp_cached_5) | (_cmp_cached_31))
          # 15m & 4h down move, 4h still high
          long_entry_logic.append((_cmp_cached_0) | (_cmp_cached_6) | (_cmp_cached_43))
          # 15m & 4h down move, 4h still not low enough
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp_cached_6) | (_cmp_cached_94)
          )
          # 15m & 4h down move, 1d high
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp_cached_19) | (_cmp_cached_62)
          )
          # 15m down move, 4h still high, 1d high
          long_entry_logic.append((_cmp_cached_0) | (_cmp_cached_43) | (_cmp_cached_38))
          # 15m & 1h down move, 4h high
          long_entry_logic.append((_cmp_cached_3) | (_cmp_cached_10) | (_cmp_cached_68))
          # 15m & 4h down move, 1h still high
          long_entry_logic.append((_cmp_cached_3) | (_cmp_cached_5) | (_cmp_cached_86))
          # 15m & 1h & 1d down move, 1h still not low enough, 1d high
          long_entry_logic.append(
            (_cmp_cached_16)
            | (_cmp_cached_10)
            | (_cmp_cached_77)
            | (_cmp("RSI_14_1h", "<", 30.0))
            | (_cmp_cached_42)
          )
          # 15m & 1h down move, 4h still high, 4h overbought
          long_entry_logic.append(
            (_cmp_cached_16) | (_cmp_cached_10) | (_cmp_cached_43) | (_cmp_cached_27)
          )
          # 15m & 1h down move, 4h high
          long_entry_logic.append((_cmp_cached_16) | (_cmp_cached_10) | (_cmp_cached_13))
          # 15m down move, 1h & 4h still high
          long_entry_logic.append(
            (_cmp_cached_16) | (_cmp_cached_86) | (_cmp_cached_54)
          )
          # 15m & 1h & 4h down move, 1d high
          long_entry_logic.append(
            (_cmp_cached_28) | (_cmp_cached_11) | (_cmp_cached_21) | (_cmp("ROC_9_1d", "<", 70.0))
          )
          # 15m & 4h down move, 4h high
          long_entry_logic.append((_cmp_cached_28) | (_cmp_cached_76) | (_cmp_cached_93))
          # 15m & 1h down move, 15m still not low enough
          long_entry_logic.append((_cmp_cached_70) | (_cmp_cached_8) | (_cmp("AROONU_14_15m", "<", 15.0)))
          # 15m & 1h down move, 1h high
          long_entry_logic.append((_cmp_cached_70) | (_cmp_cached_25) | (_cmp_cached_18))
          # 1h down move, 1h still not low enough, 1d high
          long_entry_logic.append((_cmp_cached_36) | (_cmp("AROONU_14_1h", "<", 20.0)) | (_cmp_cached_38))
          # 1h & 4h down move
          long_entry_logic.append((_cmp_cached_22) | (_cmp_cached_4))
          # 1h & 4h down move, 4h downtrend
          long_entry_logic.append((_cmp_cached_22) | (_cmp_cached_5) | (_cmp_cached_72))
          # 1h & 4h down move, 4h still not low enough
          long_entry_logic.append(
            (_cmp_cached_22) | (_cmp_cached_19) | (_cmp_cached_94)
          )
          # 1h & 1d down move, 1d high
          long_entry_logic.append((_cmp_cached_22) | (_cmp_cached_107) | (_cmp_cached_42))
          # 1h down move, 4h high
          long_entry_logic.append((_cmp_cached_22) | (_cmp_cached_13))
          # 1h down move, 1d still high
          long_entry_logic.append((_cmp_cached_22) | (_cmp_cached_117))
          # 1h & 4h down move, 4h still not low enough
          long_entry_logic.append((_cmp_cached_1) | (_cmp_cached_6) | (_cmp("RSI_14_4h", "<", 30.0)))
          # 1h & 4h down move, 4h still not low enough
          long_entry_logic.append((_cmp_cached_1) | (_cmp_cached_19) | (_cmp_cached_110))
          # 1h & 4h down move, 4h still not low enough
          long_entry_logic.append((_cmp_cached_1) | (_cmp_cached_19) | (_cmp_cached_145))
          # 1h & 4h & 1d down move
          long_entry_logic.append((_cmp_cached_1) | (_cmp_cached_19) | (_cmp_cached_77))
          # 1h & 4h down move, 1d overbought
          long_entry_logic.append((_cmp_cached_1) | (_cmp_cached_41) | (_cmp_cached_35))
          # 1h & 4h down move, 4h high
          long_entry_logic.append((_cmp_cached_1) | (_cmp_cached_76) | (_cmp_cached_13))
          # 1h & 4h down move, 4h still high
          long_entry_logic.append(
            (_cmp_cached_1) | (_cmp_cached_60) | (_cmp_cached_79)
          )
          # 1h & 1d down move, 4h still not low enough
          long_entry_logic.append(
            (_cmp_cached_1) | (_cmp_cached_64) | (_cmp_cached_94)
          )
          # 1h & 1d down move, 4h still high
          long_entry_logic.append((_cmp_cached_1) | (_cmp_cached_77) | (_cmp_cached_43))
          # 1h down move, 1h still high
          long_entry_logic.append((_cmp_cached_1) | (_cmp_cached_49))
          # 1h down move, 4h still high, 1d high
          long_entry_logic.append((_cmp_cached_1) | (_cmp_cached_68) | (_cmp_cached_38))
          # 1h down move, 1d high & overbought
          long_entry_logic.append((_cmp_cached_1) | (_cmp_cached_42) | (_cmp_cached_51))
          # 1h & 4h down move, 1d stll high
          long_entry_logic.append((_cmp_cached_2) | (_cmp_cached_5) | (_cmp("RSI_14_1d", "<", 40.0)))
          # 1h & 4h & 1d down move
          long_entry_logic.append((_cmp_cached_2) | (_cmp_cached_6) | (_cmp_cached_77))
          # 1h & 4h down move, 4h still not low enough
          long_entry_logic.append((_cmp_cached_2) | (_cmp_cached_6) | (_cmp_cached_145))
          # 1h & 4h down move, 1d overbought
          long_entry_logic.append((_cmp_cached_2) | (_cmp_cached_6) | (_cmp_cached_35))
          # 1h & 4h & 1d down move
          long_entry_logic.append((_cmp_cached_2) | (_cmp_cached_21) | (_cmp_cached_64))
          # 1h & 4h down move, 1d high
          long_entry_logic.append(
            (_cmp_cached_2) | (_cmp_cached_19) | (_cmp_cached_84)
          )
          # 1h & 4h down move, 1h & 4h still high
          long_entry_logic.append(
            (_cmp_cached_2) | (_cmp_cached_47) | (_cmp("RSI_14_1h", "<", 40.0)) | (_cmp("RSI_14_4h", "<", 50.0))
          )
          # 1h & 4h down move, 4h still high
          long_entry_logic.append(
            (_cmp_cached_2) | (_cmp_cached_76) | (_cmp_cached_54)
          )
          # 1h & 4h down move, 4h still high
          long_entry_logic.append((_cmp_cached_2) | (_cmp_cached_60) | (_cmp_cached_67))
          # 1h & 1d down move, 1d still high
          long_entry_logic.append((_cmp_cached_2) | (_cmp_cached_59) | (_cmp_cached_121))
          # 1h down move, 1h still high, 1d overbought
          long_entry_logic.append((_cmp_cached_2) | (_cmp_cached_86) | (_cmp_cached_35))
          # 1h down move, 1d high, 4h downtrend
          long_entry_logic.append((_cmp_cached_2) | (_cmp_cached_45) | (_cmp_cached_31))
          # 1h down move, 1d high & overbought
          long_entry_logic.append((_cmp_cached_2) | (_cmp_cached_42) | (_cmp_cached_51))
          # 1h down move, 4h high
          long_entry_logic.append((_cmp_cached_2) | (_cmp_cached_58))
          # 1h & 4h down move, 1h still not low enough
          long_entry_logic.append((_cmp_cached_10) | (_cmp_cached_6) | (_cmp_cached_138))
          # 1h & 4h down move, 4h still high
          long_entry_logic.append((_cmp_cached_10) | (_cmp_cached_6) | (_cmp_cached_110))
          # 1h & 4h down move, 4h still high
          long_entry_logic.append((_cmp_cached_10) | (_cmp_cached_6) | (_cmp_cached_43))
          # 1h & 4h down move, 1d downtrend
          long_entry_logic.append((_cmp_cached_10) | (_cmp_cached_6) | (_cmp_cached_23))
          # 1h & 4h down move, 1d high
          long_entry_logic.append((_cmp_cached_10) | (_cmp_cached_41) | (_cmp_cached_42))
          # 1h & 4h down move, 4h high
          long_entry_logic.append((_cmp_cached_10) | (_cmp_cached_76) | (_cmp("AROONU_14_4h", "<", 65.0)))
          # 1h & 1d down move, 1d high
          long_entry_logic.append((_cmp_cached_10) | (_cmp_cached_53) | (_cmp_cached_45))
          # 1h down move, 1h still high, 1d high
          long_entry_logic.append((_cmp_cached_10) | (_cmp_cached_86) | (_cmp_cached_38))
          # 4h down move, 4h still high, 1d high
          long_entry_logic.append((_cmp_cached_6) | (_cmp_cached_43) | (_cmp_cached_9))
          # 1h down move, 4h still high, 1d downtrend
          long_entry_logic.append(
            (_cmp_cached_10) | (_cmp_cached_79) | (_cmp_cached_149)
          )
          # 1h down move, 4h & 1d high
          long_entry_logic.append(
            (_cmp_cached_10) | (_cmp_cached_54) | (_cmp_cached_84)
          )
          # 1h & 4h down move, 1h still high
          long_entry_logic.append((_cmp_cached_11) | (_cmp_cached_41) | (_cmp_cached_86))
          # 1h & 4h down move, 4h high
          long_entry_logic.append((_cmp_cached_11) | (_cmp_cached_47) | (_cmp_cached_13))
          # 1h down move, 15m still not low enough, 4h high
          long_entry_logic.append(
            (_cmp_cached_11) | (_cmp("RSI_14_15m", "<", 30.0)) | (_cmp_cached_105)
          )
          # 1h & 4h down move, 4h still high
          long_entry_logic.append(
            (_cmp_cached_11) | (_cmp_cached_41) | (_cmp_cached_54)
          )
          # 1h down move, 1h high
          long_entry_logic.append((_cmp_cached_11) | (_cmp_cached_88))
          # 1h down move, 4h high
          long_entry_logic.append((_cmp_cached_11) | (_cmp_cached_20))
          # 1h & 1d down move, 1d high
          long_entry_logic.append((_cmp_cached_8) | (_cmp_cached_107) | (_cmp_cached_42))
          # 1h down move, 4h & 1d high
          long_entry_logic.append((_cmp_cached_8) | (_cmp_cached_13) | (_cmp_cached_9))
          # 1h down move, 4h high, 1d downtrend
          long_entry_logic.append((_cmp_cached_8) | (_cmp_cached_14) | (_cmp_cached_23))
          # 1h down move, 4h high
          long_entry_logic.append((_cmp_cached_8) | (_cmp_cached_55))
          # 1h & 4h down move, 4h high
          long_entry_logic.append((_cmp_cached_25) | (_cmp_cached_131) | (_cmp_cached_20))
          # 1h down move, 1h & 4h high
          long_entry_logic.append((_cmp_cached_25) | (_cmp_cached_12) | (_cmp_cached_32))
          # 1h down move, 4h high, 4h downtrend
          long_entry_logic.append((_cmp_cached_25) | (_cmp_cached_13) | (_cmp("CMF_20_4h", ">", -0.30)))
          # 1h down move, 1d high, 4h overbought
          long_entry_logic.append((_cmp_cached_25) | (_cmp_cached_38) | (_cmp_cached_73))
          # 1h down move, 1h high, 1d overbought
          long_entry_logic.append((_cmp_cached_33) | (_cmp_cached_12) | (_cmp_cached_39))
          # 1h down move, 1h & 4h high
          long_entry_logic.append((_cmp_cached_63) | (_cmp_cached_12) | (_cmp_cached_14))
          # 1h down move, 1h overbought
          long_entry_logic.append((_cmp_cached_63) | (_cmp_cached_134))
          # 4h & 1d down move, 1d high
          long_entry_logic.append((_cmp_cached_57) | (_cmp_cached_77) | (_cmp_cached_45))
          # 4h down move, 1h & 4h downtrend
          long_entry_logic.append((_cmp_cached_57) | (_cmp("ROC_9_1h", ">", -15.0)) | (_cmp_cached_31))
          # 4h & 1d down move
          long_entry_logic.append((_cmp_cached_4) | (_cmp_cached_53))
          # 4h & 1d down move, 1d high
          long_entry_logic.append((_cmp_cached_4) | (_cmp("RSI_3_1d", ">", 50.0)) | (_cmp_cached_38))
          # 4h down move, 4h & 1d still high
          long_entry_logic.append((_cmp_cached_4) | (_cmp_cached_43) | (_cmp_cached_121))
          # 4h & 1d down move, 1d low
          long_entry_logic.append((_cmp_cached_5) | (_cmp_cached_64) | (_cmp("CMF_20_1d", ">", -0.2)))
          # 4h & 1d down move, 1d still high
          long_entry_logic.append((_cmp_cached_5) | (_cmp_cached_77) | (_cmp_cached_121))
          # 4h & 1d down move, 1d overbought
          long_entry_logic.append((_cmp_cached_6) | (_cmp_cached_107) | (_cmp_cached_40))
          # 4h down move, 4h still not low enough, 1d downtrend
          long_entry_logic.append(
            (_cmp_cached_6) | (_cmp_cached_94) | (_cmp_cached_15)
          )
          # 4h down move, 4h & 1d downtrend
          long_entry_logic.append((_cmp_cached_6) | (_cmp_cached_31) | (_cmp_cached_15))
          # 4h down move, 4h high
          long_entry_logic.append((_cmp_cached_19) | (_cmp_cached_32))
          # 4h down move, 4h & 1d high
          long_entry_logic.append(
            (_cmp_cached_41) | (_cmp_cached_68) | (_cmp_cached_62)
          )
          # 4h down move, 4h overbought
          long_entry_logic.append((_cmp_cached_87) | (_cmp_cached_73))
          # 1d down move, 4h & 1d downtrend
          long_entry_logic.append((_cmp_cached_66) | (_cmp_cached_31) | (_cmp_cached_15))
          # 15m down move, 1d high, 1d downtrend
          long_entry_logic.append((_cmp_cached_59) | (_cmp_cached_45) | (_cmp_cached_44))
          # 1d down move, 1d high, 1d downtrend
          long_entry_logic.append((_cmp_cached_64) | (_cmp_cached_42) | (_cmp_cached_23))
          # 4h & 1d high, 4h overbought
          long_entry_logic.append((_cmp_cached_20) | (_cmp_cached_9) | (_cmp_cached_26))
          # 4h high, 1h overbought
          long_entry_logic.append((_cmp_cached_20) | (_cmp_cached_134))
          # 4h high, 4h overbought
          long_entry_logic.append((_cmp_cached_20) | (_cmp_cached_73))
          # 4h high, 1h overbought
          long_entry_logic.append((_cmp_cached_58) | (_cmp_cached_134))
          # 4h high, 4h overbought
          long_entry_logic.append((_cmp_cached_58) | (_cmp_cached_73))
          # 4h high, 4h overbought, 1d downtrend
          long_entry_logic.append(
            (_cmp_cached_55) | (_cmp_cached_26) | (_cmp_cached_15)
          )
          # 1d green, 4h down move, 4h still high
          long_entry_logic.append((_cmp("change_pct_1d", "<", 40.0)) | (_cmp_cached_41) | (_cmp_cached_67))
          # 4h top wick, 1h down move, 1h still high
          long_entry_logic.append(
            (_cmp("top_wick_pct_4h", "<", 20.0)) | (_cmp_cached_65) | (_cmp_cached_49)
          )
          # pump, drop but not yet near the previous lows
          long_entry_logic.append(
            _range_lt("high_max_6_1d", "low_min_6_1d", 2.0)
            | _gt_mul("close", "high_max_12_4h", 0.50)
            | (df["close"] < (df["low_min_24_4h"] * 1.05))
          )
          # 1d overbought, drop but not yet near the previous lows
          long_entry_logic.append(
            (_cmp_cached_35)
            | _gt_mul("close", "high_max_6_1d", 0.70)
            | (df["close"] < (df["low_min_12_1d"] * 1.25))
          )
          # 1d overbought, drop but not yet near the previous lows
          long_entry_logic.append(
            _range_lt("high_max_12_1d", "low_min_12_1d", 2.5)
            | _gt_mul("close", "high_max_6_1d", 0.60)
            | (df["close"] < (df["low_min_12_1d"] * 1.25))
          )
          # big drop in the last 2 days, 1d down move
          long_entry_logic.append(_gt_mul("close", "high_max_12_4h", 0.30) | (_cmp_cached_77))
          # big drop in the last 12 days, 1h down move
          long_entry_logic.append(_gt_mul("close", "high_max_12_1d", 0.30) | (_cmp_cached_10))
          # big drop in the last 12 days, 4h still high
          long_entry_logic.append(
            _gt_mul("close", "high_max_12_1d", 0.40) | (_cmp_cached_54)
          )
          # big drop in the last 20 days, 1h down move
          long_entry_logic.append(_gt_mul("close", "high_max_20_1d", 0.40) | (_cmp_cached_1))
          # big drop in the last 20 days, 4h down move
          long_entry_logic.append(_gt_mul("close", "high_max_20_1d", 0.10) | (_cmp_cached_21))
          # big drop in the last 30 days, 4h down move
          long_entry_logic.append(_gt_mul("close", "high_max_30_1d", 0.40) | (_cmp_cached_5))
          # big drop in the last 30 days, 4h still not low enough
          long_entry_logic.append(
            _gt_mul("close", "high_max_30_1d", 0.25) | (_cmp_cached_94)
          )

          # Logic
          long_entry_logic.append(_cmp("RSI_3", "<", 40.0))
          long_entry_logic.append(_cmp("RSI_3_15m", "<", 50.0))
          long_entry_logic.append(_cmp("WILLR_14_15m", "<", -50.0))
          long_entry_logic.append(_cmp("AROONU_14_15m", "<", 25.0))
          long_entry_logic.append(_cmp("STOCHRSIk_14_14_3_3_15m", "<", 20.0))
          long_entry_logic.append(_cmp("WILLR_84_1h", "<", -70.0))
          long_entry_logic.append(_cmp_cached_132)
          long_entry_logic.append(_cmp("BBB_20_2.0_1h", ">", 12.0))
          long_entry_logic.append(df["close_max_48"] >= (df["close"] * 1.10))

        # Condition #61 - Rebuy mode (Long).
        if long_entry_condition_index == 61:
          # Protections
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          long_entry_logic.append(df["protections_long_global"] == True)

          long_entry_logic.append(
            # 5m & 1h down move, 1h still not low enough
            ((_cmp_cached_48) | (_cmp_cached_1) | (_cmp_cached_138))
            # 5m & 1h down move, 1d high
            & ((_cmp_cached_48) | (_cmp_cached_10) | (_cmp_cached_9))
            # 5m & 4h down move, 4h high
            & ((_cmp_cached_48) | (_cmp_cached_21) | (_cmp_cached_13))
            # 5m down move, 1d high & overbought
            & ((_cmp_cached_48) | (_cmp_cached_62) | (_cmp_cached_39))
            # 15m & 1h & 4h down move
            & ((_cmp_cached_7) | (_cmp_cached_36) | (_cmp_cached_4))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_7) | (_cmp_cached_36) | (_cmp_cached_110))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_7) | (_cmp_cached_36) | (_cmp_cached_67))
            # 15m & 1h down move, 4h still not low enough
            & ((_cmp_cached_7) | (_cmp_cached_22) | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 20.0)))
            # 15m & 1h & 4h down move
            & ((_cmp_cached_7) | (_cmp_cached_1) | (_cmp_cached_80))
            # 15m & 1h down move, 1d still high
            & ((_cmp_cached_7) | (_cmp_cached_1) | (_cmp("RSI_14_1d", "<", 50.0)))
            # 15m & 1h down move, 4h downtrend
            & ((_cmp_cached_7) | (_cmp_cached_1) | (_cmp("CMF_20_4h", ">", -0.30)))
            # 15m & 1h down move, 1d still high
            & ((_cmp_cached_7) | (_cmp_cached_1) | (_cmp_cached_117))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_7) | (_cmp_cached_1) | (_cmp_cached_40))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_7) | (_cmp_cached_10) | (_cmp_cached_35))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_7) | (_cmp_cached_8) | (_cmp_cached_42))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_7) | (_cmp_cached_8) | (_cmp_cached_82))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_7) | (_cmp_cached_65) | (_cmp_cached_18))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_7) | (_cmp_cached_97) | (_cmp_cached_37))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_7) | (_cmp_cached_47) | (_cmp_cached_110))
            # 15m down move, 15m downtrend. 4h high
            & ((_cmp_cached_7) | (_cmp("CMF_20_15m", ">", -0.50)) | (_cmp_cached_68))
            # 15m down move, 15m still not low enough
            & ((_cmp_cached_7) | (_cmp_cached_111))
            # 15m down move, 4h high
            & ((_cmp_cached_7) | (_cmp_cached_20))
            # 15m down move, 4h & 1d downtrend
            & ((_cmp_cached_7) | (_cmp_cached_31) | (_cmp_cached_15))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_17) | (_cmp_cached_10) | (_cmp_cached_82))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_17) | (_cmp_cached_8) | (_cmp_cached_37))
            # 15m & 4h down move, 1h downtrend
            & ((_cmp_cached_17) | (_cmp_cached_4) | (_cmp_cached_120))
            # 15m & 4h down move, 1d overbought
            & ((_cmp_cached_17) | (_cmp_cached_5) | (_cmp("ROC_9_1d", "<", 70.0)))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_17) | (_cmp_cached_6) | (_cmp_cached_37))
            # 15m down move, 15m still low, 4h still high
            & ((_cmp_cached_17) | (_cmp("AROONU_14_15m", "<", 20.0)) | (_cmp_cached_43))
            # 15m down move, 15m still high
            & ((_cmp_cached_17) | (_cmp_cached_46))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_0) | (_cmp_cached_1) | (_cmp_cached_106))
            # 15m & 1h down move, 4h downtrend
            & ((_cmp_cached_0) | (_cmp_cached_1) | (_cmp("ROC_9_4h", ">", -50.0)))
            # 15m & 1h down move, 15m still high
            & ((_cmp_cached_0) | (_cmp_cached_8) | (_cmp_cached_46))
            # 15m & 1h down move, 4h overbought
            & ((_cmp_cached_0) | (_cmp_cached_8) | (_cmp_cached_98))
            # 15m & 4h down move, 4h still not low enough
            & ((_cmp_cached_0) | (_cmp_cached_4) | (_cmp_cached_94))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_21) | (_cmp_cached_13))
            # 15m & 4h down move, 4h overbought
            & ((_cmp_cached_0) | (_cmp_cached_131) | (_cmp_cached_98))
            # 15m down move, 15m still not low enough, 1d downtrend
            & ((_cmp_cached_0) | (_cmp_cached_111) | (_cmp_cached_23))
            # 15m down move, 15m still high, 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_46) | (_cmp_cached_51))
            # 15m down move, 4h & 1d high
            & ((_cmp_cached_0) | (_cmp_cached_68) | (_cmp_cached_9))
            # 15m down move, 1d high, 1d downtrend
            & ((_cmp_cached_0) | (_cmp_cached_103) | (_cmp("CMF_20_1d", ">", -0.40)))
            # 15m down move, 1h high & overbought
            & ((_cmp_cached_0) | (_cmp_cached_83) | (_cmp_cached_85))
            # 15m down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_58))
            # 15m down move, 4h & 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_27) | (_cmp_cached_40))
            # 15m & 1h down move, 15m high
            & ((_cmp_cached_3) | (_cmp_cached_2) | (_cmp_cached_90))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_3) | (_cmp_cached_2) | (_cmp_cached_30))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_11) | (_cmp_cached_18))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_25) | (_cmp_cached_18))
            # 15m down move, 15m still high, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_46) | (_cmp_cached_18))
            # 15m down move, 4h high, 4h downtrend
            & ((_cmp_cached_3) | (_cmp_cached_68) | (_cmp_cached_31))
            # 15m down move, 1d high, 4h overbought
            & ((_cmp_cached_3) | (_cmp_cached_62) | (_cmp_cached_73))
            # 15m down move, 1h & 4h overbought
            & ((_cmp_cached_3) | (_cmp_cached_85) | (_cmp_cached_73))
            # 15m down move, 4h & 1d downtrend
            & ((_cmp_cached_3) | (_cmp_cached_102) | (_cmp_cached_44))
            # 15m down move, 4h & 1d overbought
            & ((_cmp_cached_3) | (_cmp_cached_26) | (_cmp_cached_99))
            # 15m & 1h down move, 15m high
            & ((_cmp_cached_16) | (_cmp_cached_10) | (_cmp_cached_90))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_16) | (_cmp_cached_10) | (_cmp_cached_12))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_16) | (_cmp_cached_11) | (_cmp_cached_32))
            # 15m down move, 1h high
            & ((_cmp_cached_16) | (_cmp_cached_52))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_16) | (_cmp_cached_13) | (_cmp_cached_26))
            # 15m down move, 1h high
            & ((_cmp_cached_16) | (_cmp_cached_37))
            # 15m down move, 4h high
            & ((_cmp_cached_16) | (_cmp_cached_55))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_28) | (_cmp_cached_71) | (_cmp_cached_39))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_70) | (_cmp_cached_63) | (_cmp_cached_71))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_70) | (_cmp_cached_63) | (_cmp_cached_14))
            # 15m down move, 15m high, 4h high
            & ((_cmp_cached_70) | (_cmp_cached_90) | (_cmp_cached_58))
            # 15m down move, 1h & 4h high
            & (
              (_cmp_cached_70) | (_cmp_cached_56) | (_cmp_cached_34)
            )
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_36) | (_cmp_cached_57) | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 20.0)))
            # 1h & 4h down move, 15m stil high
            & ((_cmp_cached_36) | (_cmp_cached_4) | (_cmp_cached_75))
            # 1h down move, 1h still not low enough
            & ((_cmp_cached_36) | (_cmp("AROONU_14_1h", "<", 20.0)))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_22) | (_cmp_cached_4) | (_cmp_cached_44))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_22) | (_cmp_cached_5) | (_cmp_cached_145))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_22) | (_cmp_cached_5) | (_cmp_cached_40))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_22) | (_cmp_cached_6) | (_cmp_cached_94))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_22) | (_cmp_cached_68) | (_cmp_cached_78))
            # 1h down move, 1d high, 4h downtrend
            & ((_cmp_cached_22) | (_cmp_cached_38) | (_cmp_cached_72))
            # 1h down move, 1d high, 1d downtrend
            & ((_cmp_cached_22) | (_cmp_cached_9) | (_cmp_cached_15))
            # 1h & 4h down move, 1h still not low enough
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp_cached_132))
            # 1h & 4h down move, 15m downtrend
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp("ROC_9_15m", ">", -15.0)))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_1) | (_cmp_cached_5) | (_cmp_cached_110))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_1) | (_cmp_cached_19) | (_cmp_cached_69))
            # 1h down move, 15m still high, 4h high
            & ((_cmp_cached_1) | (_cmp_cached_81) | (_cmp_cached_55))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_1) | (_cmp_cached_9) | (_cmp_cached_78))
            # 1h down move, 4h still high, 4d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_54) | (_cmp_cached_95))
            # 1h down move, 4h downtrend, 1d overbought
            & ((_cmp_cached_1) | (_cmp_cached_102) | (_cmp_cached_40))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_2) | (_cmp_cached_47) | (_cmp_cached_20))
            # 1h down move, 1d downtrend, 1d high
            & ((_cmp_cached_2) | (_cmp("CMF_20_1d", ">", -0.30)) | (_cmp_cached_84))
            # 1h down move, 1h still high
            & ((_cmp_cached_2) | (_cmp_cached_49))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_2) | (_cmp_cached_68) | (_cmp_cached_35))
            # 1h down move, 4h & 1d high
            & ((_cmp_cached_2) | (_cmp_cached_13) | (_cmp_cached_38))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_10) | (_cmp_cached_6) | (_cmp_cached_39))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_10) | (_cmp_cached_19) | (_cmp_cached_20))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_10) | (_cmp_cached_12) | (_cmp_cached_27))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_47) | (_cmp_cached_29))
            # 1h down move, 1h & 1d high
            & ((_cmp_cached_11) | (_cmp_cached_12) | (_cmp_cached_38))
            # 1h down move, 1h still high, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_30) | (_cmp_cached_40))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_11) | (_cmp_cached_34) | (_cmp_cached_44))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_8) | (_cmp_cached_41) | (_cmp("AROONU_14_1h", "<", 75.0)))
            # 1h down move, 1h high, 4h downtrend
            & ((_cmp_cached_25) | (_cmp_cached_18) | (_cmp_cached_139))
            # 1h down move, 1h still high, 1d overbought
            & ((_cmp_cached_25) | (_cmp_cached_30) | (_cmp_cached_74))
            # 1h down move, 1h high, 4h downtrend
            & ((_cmp_cached_25) | (_cmp_cached_56) | (_cmp_cached_31))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_25) | (_cmp_cached_26) | (_cmp_cached_69))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_33) | (_cmp_cached_12) | (_cmp_cached_32))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_33) | (_cmp_cached_92) | (_cmp_cached_69))
            # 1h down move, 1h high, 4h downtrend
            & ((_cmp_cached_33) | (_cmp_cached_37) | (_cmp_cached_31))
            # 1h down move, 1h high, 1h overbought
            & ((_cmp_cached_63) | (_cmp_cached_12) | (_cmp("ROC_9_1h", "<", 25.0)))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_63) | (_cmp_cached_105) | (_cmp_cached_146))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_97) | (_cmp_cached_50) | (_cmp_cached_99))
            # 4h & 1d down move, 15m still high
            & ((_cmp_cached_80) | (_cmp_cached_59) | (_cmp_cached_113))
            # 4h & 1d down move, 1h still not low enough
            & ((_cmp_cached_80) | (_cmp_cached_59) | (_cmp_cached_109))
            # 4h & 1d down move, 1d still not low enough
            & ((_cmp_cached_80) | (_cmp_cached_77) | (_cmp("AROONU_14_1d", "<", 30.0)))
            # 4h down move, 1d high
            & ((_cmp_cached_80) | (_cmp_cached_38))
            # 4h down move, 1h still high, 4h downtrend
            & ((_cmp_cached_80) | (_cmp_cached_30) | (_cmp_cached_72))
            # 4h down move, 1d high
            & ((_cmp_cached_80) | (_cmp_cached_62))
            # 4h down move, 1h & 4h downtrend
            & ((_cmp_cached_80) | (_cmp_cached_124) | (_cmp_cached_72))
            # 4h down move, 1d overbought
            & ((_cmp_cached_80) | (_cmp_cached_40))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_57) | (_cmp_cached_77) | (_cmp("STOCHRSIk_14_14_3_3_1d", "<", 40.0)))
            # 4h down move, 4h downtrend, 4h still high
            & ((_cmp_cached_57) | (_cmp("CMF_20_4h", ">", -0.20)) | (_cmp_cached_67))
            # 4h & 1d down move, 1d downtrend
            & ((_cmp_cached_4) | (_cmp_cached_66) | (_cmp_cached_44))
            # 4h down move, 1h high, 1d downtrend
            & ((_cmp_cached_4) | (_cmp_cached_112) | (_cmp_cached_44))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_53) | (_cmp("AROONU_14_1d", "<", 60.0)))
            # 4h down move, 4h high, 1h downtrend
            & ((_cmp_cached_5) | (_cmp_cached_68) | (_cmp_cached_120))
            # 4h down move, 4h & 1d high
            & ((_cmp_cached_5) | (_cmp_cached_13) | (_cmp_cached_45))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_6) | (_cmp_cached_42) | (_cmp_cached_69))
            # 4h down move, 1h still not low enough, 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_132) | (_cmp_cached_15))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_6) | (_cmp_cached_79) | (_cmp_cached_15))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_21) | (_cmp_cached_43) | (_cmp_cached_44))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_19) | (_cmp_cached_43) | (_cmp_cached_44))
            # 4h down move, 4h high, 1d overbought
            & ((_cmp_cached_19) | (_cmp_cached_20) | (_cmp_cached_35))
            # 4h down move, 4h & 1d overbought
            & ((_cmp_cached_47) | (_cmp_cached_27) | (_cmp_cached_35))
            # 4h down move, 1h high, 1d overbought
            & ((_cmp_cached_76) | (_cmp_cached_92) | (_cmp_cached_35))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_60) | (_cmp_cached_110) | (_cmp_cached_23))
            # 4h down move, 4h high & overbought
            & ((_cmp_cached_60) | (_cmp_cached_20) | (_cmp_cached_27))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_60) | (_cmp_cached_54) | (_cmp_cached_23))
            # 1d down move, 1h still high, 1d downtrend
            & ((_cmp("RSI_3_1d", ">", 5.0)) | (_cmp_cached_30) | (_cmp_cached_23))
            # 1d down move, 1h high, 1d downtrend
            & ((_cmp_cached_66) | (_cmp_cached_18) | (_cmp_cached_142))
            # 1d down move, 1d high, 1d downtrend
            & ((_cmp_cached_66) | (_cmp_cached_45) | (_cmp_cached_44))
            # 1d down move, 1h high & overbought
            & ((_cmp_cached_133) | (_cmp_cached_83) | (_cmp_cached_61))
            # 1d downtrend, 1d high & overbought
            & ((_cmp("CMF_20_1d", ">", -0.30)) | (_cmp_cached_103) | (_cmp_cached_29))
            # 15m high, 1h high & overbought
            & ((_cmp_cached_90) | (_cmp_cached_92) | (_cmp_cached_61))
            # 1h high, 4h high, 1h overbought
            & ((_cmp_cached_12) | (_cmp_cached_14) | (_cmp_cached_85))
            # 1h & 1d high, 1h overbought
            & ((_cmp_cached_12) | (_cmp_cached_45) | (_cmp_cached_85))
            # 1h & 4h high, 1d downtrend
            & ((_cmp_cached_92) | (_cmp_cached_14) | (_cmp("ROC_9_1d", ">", -80.0)))
            # 4h still high, 5m downtrend
            & ((_cmp_cached_67) | (_cmp("ROC_9", ">", -40.0)))
            # 4h high, 4h & 1d overbought
            & ((_cmp_cached_68) | (_cmp_cached_50) | (_cmp_cached_99))
            # 4h & 1d high, 4h overbought
            & ((_cmp_cached_20) | (_cmp_cached_9) | (_cmp_cached_50))
            # 4h & 1d high, 1d overbought
            & ((_cmp_cached_20) | (_cmp_cached_9) | (_cmp_cached_35))
            # 4h high, 4h & 1d overbought
            & ((_cmp_cached_20) | (_cmp_cached_26) | (_cmp_cached_39))
            # 1d high, 1h & 4h downtrend
            & ((_cmp_cached_103) | (_cmp_cached_124) | (_cmp("ROC_9_4h", ">", -50.0)))
            # 1d high, 1h & 1d overbought
            & ((_cmp_cached_103) | (_cmp_cached_85) | (_cmp_cached_29))
            # 1d high, 4h & 1d overbought
            & ((_cmp_cached_38) | (_cmp_cached_50) | (_cmp_cached_99))
            # 1h high, 1d overbought
            & ((_cmp_cached_56) | (_cmp_cached_40))
            # 4h high, 1h overbought, 1d downtrend
            & ((_cmp_cached_34) | (_cmp_cached_134) | (_cmp_cached_150))
            # 4h high, 1h & 4h overbought
            & ((_cmp_cached_55) | (_cmp_cached_85) | (_cmp_cached_98))
            # 1h & 4h overbought
            & ((_cmp("ROC_9_1h", "<", 100.0)) | (_cmp_cached_115))
            # big drop in the last 20 days, 1d high, 1d downtrend
            & (
              _gt_mul("close", "high_max_20_1d", 0.20)
              | (_cmp_cached_106)
              | (_cmp_cached_141)
            )
          )

          # Logic
          long_entry_logic.append(
            (_cmp("RSI_3", "<", 50.0))
            & (_cmp("AROONU_14", "<", 25.0))
            & (_cmp("STOCHRSIk_14_14_3_3", "<", 30.0))
            & (df["EMA_26"] > df["EMA_12"])
            & ((df["EMA_26"] - df["EMA_12"]) > (df["open"] * 0.030))
            & _ema_26_12_spread_gt_open_pct
          )

        # Condition #62 - Rebuy mode (Long).
        if long_entry_condition_index == 62:
          # Protections
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          long_entry_logic.append(df["protections_long_global"] == True)

          long_entry_logic.append(
            # 5m & 4h down move, 1d high
            ((_cmp_cached_48) | (_cmp_cached_4) | (_cmp_cached_38))
            # 5m & 1d down move, 15m still high
            & ((_cmp_cached_48) | (_cmp_cached_53) | (_cmp_cached_113))
            # 5m & 4h down move, 15m still high
            & ((_cmp_cached_104) | (_cmp_cached_21) | (_cmp_cached_75))
            # 5m & 4h down move, 4h still not low enough
            & ((_cmp_cached_104) | (_cmp_cached_5) | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 20.0)))
            # 15m & 1h down move, 1h still not low enough
            & ((_cmp_cached_7) | (_cmp_cached_1) | (_cmp("AROONU_14_1h", "<", 20.0)))
            # 15m & 1h down move, 4h still not low enough
            & ((_cmp_cached_7) | (_cmp_cached_1) | (_cmp("RSI_14_4h", "<", 30.0)))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_7) | (_cmp_cached_2) | (_cmp("RSI_14_4h", "<", 50.0)))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_7) | (_cmp_cached_10) | (_cmp_cached_79))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_7) | (_cmp_cached_11) | (_cmp_cached_43))
            # 15m & 4h down move, 4h still not low enough
            & ((_cmp_cached_7) | (_cmp_cached_80) | (_cmp("AROONU_14_4h", "<", 20.0)))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_7) | (_cmp_cached_6) | (_cmp_cached_67))
            # 15m & 1h down move, 1h still not low enough
            & ((_cmp_cached_17) | (_cmp_cached_1) | (_cmp_cached_132))
            # 15m & 1h down move, 15m still not low enough
            & ((_cmp_cached_17) | (_cmp_cached_1) | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 20.0)))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_17) | (_cmp_cached_1) | (_cmp_cached_67))
            # 15m & 4h down move, 15m still not low enough
            & ((_cmp_cached_17) | (_cmp_cached_4) | (_cmp_cached_125))
            # 15m & 4h down move, 1h downtrend
            & ((_cmp_cached_17) | (_cmp_cached_4) | (_cmp_cached_120))
            # 15m & 4h down move, 1d overbought
            & ((_cmp_cached_17) | (_cmp_cached_4) | (_cmp_cached_39))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_17) | (_cmp_cached_5) | (_cmp_cached_110))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_0) | (_cmp_cached_1) | (_cmp_cached_79))
            # 15m & 1h down move, 1d downtrend
            & ((_cmp_cached_0) | (_cmp_cached_1) | (_cmp_cached_15))
            # 15m & 1h down move, 15m high
            & ((_cmp_cached_0) | (_cmp_cached_1) | (_cmp_cached_24))
            # 15m & 1h down move, 1h still not low enough
            & ((_cmp_cached_0) | (_cmp_cached_1) | (_cmp_cached_138))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_0) | (_cmp_cached_2) | (_cmp_cached_86))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_0) | (_cmp_cached_1) | (_cmp_cached_9))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_2) | (_cmp_cached_68))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_25) | (_cmp_cached_32))
            # 15m & 4h down move, 15m still not low enough
            & ((_cmp_cached_0) | (_cmp_cached_5) | (_cmp("AROONU_14_15m", "<", 20.0)))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_0) | (_cmp_cached_6) | (_cmp_cached_62))
            # 15m & 4h down move, 4h still not low enough
            & ((_cmp_cached_0) | (_cmp_cached_6) | (_cmp_cached_94))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_0) | (_cmp_cached_6) | (_cmp_cached_106))
            # 15m & 4h down move, 4h downtrend
            & ((_cmp_cached_0) | (_cmp_cached_21) | (_cmp("CMF_20_4h", ">", -0.30)))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_0) | (_cmp_cached_19) | (_cmp_cached_62))
            # 15m & 4h down move, 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_47) | (_cmp_cached_74))
            # 15m & 1d down move, 1d high
            & ((_cmp_cached_0) | (_cmp_cached_53) | (_cmp("AROONU_14_1d", "<", 75.0)))
            # 15m down move, 4h high, 1d downtrend
            & ((_cmp_cached_0) | (_cmp_cached_13) | (_cmp_cached_149))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_2) | (_cmp("AROONU_14_4h", "<", 75.0)))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_6) | (_cmp_cached_68))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_3) | (_cmp_cached_21) | (_cmp_cached_79))
            # 15m down move, 15m downtrend, 4h high
            & ((_cmp_cached_3) | (_cmp("CMF_20_15m", ">", -0.30)) | (_cmp_cached_43))
            # 15m down move, 15m still high, 4h overbought
            & ((_cmp_cached_3) | (_cmp_cached_81) | (_cmp_cached_73))
            # 15m down move, 4h & 1d high
            & ((_cmp_cached_3) | (_cmp_cached_20) | (_cmp_cached_9))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_16) | (_cmp_cached_12) | (_cmp_cached_14))
            # 15m down move, 15m still not low enough, 1d overbought
            & ((_cmp_cached_16) | (_cmp_cached_125) | (_cmp_cached_69))
            # 15m & 4h down move, 15m stil high
            & ((_cmp_cached_28) | (_cmp_cached_19) | (_cmp_cached_113))
            # 15m down move, 15m still not low enough, 1d downtrend
            & ((_cmp_cached_28) | (_cmp("AROONU_14_15m", "<", 25.0)) | (_cmp_cached_95))
            # 15m down move, 15m still high, 4h high
            & ((_cmp_cached_28) | (_cmp_cached_46) | (_cmp_cached_20))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_70) | (_cmp_cached_33) | (_cmp_cached_49))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_70) | (_cmp_cached_41) | (_cmp_cached_13))
            # 15m down move, 15m still high, 4h high
            & ((_cmp_cached_100) | (_cmp_cached_46) | (_cmp_cached_20))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_36) | (_cmp_cached_47) | (_cmp_cached_54))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_36) | (_cmp_cached_60) | (_cmp_cached_13))
            # 1h down move, 15m still not low enough
            & ((_cmp_cached_36) | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 20.0)))
            # 1h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_36) | (_cmp_cached_54) | (_cmp_cached_15))
            # 1h & 4h down move, 15m still not low enough
            & ((_cmp_cached_22) | (_cmp_cached_57) | (_cmp_cached_125))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_22) | (_cmp_cached_57) | (_cmp_cached_94))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_22) | (_cmp_cached_4) | (_cmp("AROONU_14_4h", "<", 20.0)))
            # 1h & 4h down move, 4h downtrend
            & ((_cmp_cached_22) | (_cmp_cached_5) | (_cmp_cached_72))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_22) | (_cmp_cached_6) | (_cmp("RSI_14_4h", "<", 30.0)))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_22) | (_cmp_cached_19) | (_cmp_cached_67))
            # 1h & 4h & 1d down move
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp_cached_59))
            # 1h & 4h down move, 15m high
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 60.0)))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp_cached_145))
            # 1h & 4h down move, 1h downtrend
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp_cached_120))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp_cached_15))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp_cached_78))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_1) | (_cmp_cached_6) | (_cmp_cached_67))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_1) | (_cmp_cached_21) | (_cmp_cached_68))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_1) | (_cmp_cached_21) | (_cmp_cached_79))
            # 1h & 4h down move, 1h still not low enough
            & ((_cmp_cached_1) | (_cmp_cached_41) | (_cmp_cached_138))
            # 1h& 1d down move, 1h still high
            & ((_cmp_cached_1) | (_cmp_cached_64) | (_cmp_cached_86))
            # 1h & 1d down move, 1d high
            & ((_cmp_cached_1) | (_cmp("RSI_3_1d", ">", 60.0)) | (_cmp_cached_42))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_2) | (_cmp_cached_5) | (_cmp("RSI_14_1d", "<", 60.0)))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_2) | (_cmp_cached_5) | (_cmp_cached_67))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_2) | (_cmp_cached_5) | (_cmp_cached_106))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_2) | (_cmp_cached_6) | (_cmp_cached_79))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_2) | (_cmp_cached_6) | (_cmp_cached_62))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_2) | (_cmp_cached_19) | (_cmp_cached_84))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_2) | (_cmp_cached_76) | (_cmp_cached_44))
            # 1h & 1d down move, 4h high
            & ((_cmp_cached_2) | (_cmp_cached_59) | (_cmp_cached_34))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_2) | (_cmp_cached_13) | (_cmp_cached_29))
            # 1h down move, 1d high, 4h downtrend
            & ((_cmp_cached_2) | (_cmp_cached_38) | (_cmp_cached_31))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_10) | (_cmp_cached_21) | (_cmp_cached_106))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_10) | (_cmp_cached_47) | (_cmp_cached_58))
            # 1h & 4h down move, 4h overbought
            & ((_cmp_cached_10) | (_cmp_cached_47) | (_cmp_cached_27))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_10) | (_cmp_cached_76) | (_cmp_cached_9))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_10) | (_cmp_cached_60) | (_cmp_cached_34))
            # 1h down move, 1h high
            & ((_cmp_cached_10) | (_cmp_cached_12))
            # 1h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_10) | (_cmp_cached_67) | (_cmp_cached_15))
            # 1h down move, 4h high
            & ((_cmp_cached_10) | (_cmp_cached_93))
            # 1h down move, 1h still not low enough, 4h stil high
            & ((_cmp_cached_10) | (_cmp_cached_132) | (_cmp_cached_67))
            # 1h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_10) | (_cmp_cached_79) | (_cmp_cached_44))
            # 1h down move, 1d high, 4h downtrend
            & ((_cmp_cached_10) | (_cmp_cached_84) | (_cmp_cached_31))
            # 1h down move, 4h high
            & ((_cmp_cached_10) | (_cmp_cached_34))
            # 1h & 4h down move, 1h still not low enough
            & ((_cmp_cached_11) | (_cmp_cached_21) | (_cmp_cached_132))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_21) | (_cmp_cached_35))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_11) | (_cmp_cached_19) | (_cmp_cached_68))
            # 1h down move, 4h & 1d high
            & ((_cmp_cached_11) | (_cmp_cached_68) | (_cmp_cached_9))
            # 1h down move, 4h high, 4h downtrend
            & ((_cmp_cached_11) | (_cmp_cached_13) | (_cmp("CMF_20_4h", ">", -0.50)))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_11) | (_cmp_cached_13) | (_cmp_cached_27))
            # 1h down move, 15m still high, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_75) | (_cmp_cached_51))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_8) | (_cmp_cached_19) | (_cmp_cached_54))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_8) | (_cmp_cached_19) | (_cmp_cached_29))
            # 1h & dh down move, 4h high
            & ((_cmp_cached_8) | (_cmp_cached_60) | (_cmp_cached_93))
            # 1h down move, 4h & 1d downtrend
            & ((_cmp_cached_8) | (_cmp("ROC_9_4h", ">", -25.0)) | (_cmp_cached_146))
            # 1h down move, 4h & 1h overbought
            & ((_cmp_cached_8) | (_cmp_cached_50) | (_cmp_cached_40))
            # 1h down move, 4h high, 4h downtrend
            & ((_cmp_cached_8) | (_cmp_cached_13) | (_cmp("CMF_20_4h", ">", -0.40)))
            # 1h down move, 1d high, 4h downtrend
            & ((_cmp_cached_8) | (_cmp_cached_42) | (_cmp_cached_72))
            # 1h down move, 1d high, 4h overbought
            & ((_cmp_cached_8) | (_cmp_cached_9) | (_cmp_cached_26))
            # 1h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_8) | (_cmp_cached_79) | (_cmp("ROC_9_1d", ">", -80.0)))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_8) | (_cmp_cached_55) | (_cmp_cached_26))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_8) | (_cmp_cached_27) | (_cmp_cached_51))
            # 1h & 4h down move, 1h still high
            & ((_cmp_cached_25) | (_cmp_cached_41) | (_cmp_cached_49))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_25) | (_cmp_cached_47) | (_cmp_cached_20))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_25) | (_cmp_cached_12) | (_cmp_cached_14))
            # 1h down move, 1d high, 4h overbought
            & ((_cmp_cached_25) | (_cmp_cached_38) | (_cmp_cached_73))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_33) | (_cmp_cached_58) | (_cmp_cached_50))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_65) | (_cmp_cached_20) | (_cmp_cached_115))
            # 1h down move, 1h overbought
            & ((_cmp_cached_63) | (_cmp_cached_134))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_97) | (_cmp_cached_50) | (_cmp_cached_29))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_57) | (_cmp_cached_53) | (_cmp_cached_135))
            # 4h & 1d down move, 4h still not low enough
            & ((_cmp_cached_57) | (_cmp_cached_77) | (_cmp("AROONU_14_4h", "<", 20.0)))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_57) | (_cmp_cached_77) | (_cmp_cached_45))
            # 4h down move, 1h high, 4h downtrend
            & ((_cmp_cached_57) | (_cmp_cached_12) | (_cmp_cached_31))
            # 4h down move, 4h high
            & ((_cmp_cached_57) | (_cmp_cached_68))
            # 4h & 1d down move, 1d still not low enough
            & ((_cmp_cached_4) | (_cmp_cached_59) | (_cmp("AROONU_14_1d", "<", 30.0)))
            # 4h down move, 15m still high
            & ((_cmp_cached_4) | (_cmp_cached_113))
            # 4h down move, 1d still high, 1d downtrend
            & ((_cmp_cached_5) | (_cmp("RSI_14_1d", "<", 40.0)) | (_cmp_cached_141))
            # 4h down move, 1h downtrend, 1d downtrend
            & ((_cmp_cached_5) | (_cmp("CMF_20_1h", ">", -0.40)) | (_cmp_cached_15))
            # 4h down move, 15m high, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_24) | (_cmp_cached_29))
            # 4h down move, 4h still high, 4h downtrend
            & ((_cmp_cached_5) | (_cmp_cached_67) | (_cmp_cached_31))
            # 4h down move, 15m still not low enough, 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_125) | (_cmp_cached_15))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_5) | (_cmp_cached_62) | (_cmp_cached_39))
            # 4h & 1d down move, 1d overbought
            & ((_cmp_cached_6) | (_cmp_cached_107) | (_cmp_cached_40))
            # 4h down move, 15m high, 4h downtrend
            & ((_cmp_cached_6) | (_cmp_cached_24) | (_cmp_cached_72))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_6) | (_cmp_cached_42) | (_cmp_cached_51))
            # 4h & 1d down move, 1d overbought
            & ((_cmp_cached_21) | (_cmp_cached_107) | (_cmp_cached_78))
            # 4h down move, 15m high, 4h high
            & ((_cmp_cached_21) | (_cmp_cached_24) | (_cmp_cached_20))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_21) | (_cmp_cached_67) | (_cmp_cached_15))
            # 4h down move, 4h still high, 4h downtrend
            & ((_cmp_cached_21) | (_cmp_cached_43) | (_cmp("CMF_20_4h", ">", -0.40)))
            # 4h down move, 4h high, 1d high
            & ((_cmp_cached_19) | (_cmp_cached_13) | (_cmp_cached_84))
            # 4h down move, 1d still high, 1d downtrend
            & ((_cmp_cached_19) | (_cmp_cached_135) | (_cmp_cached_15))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_19) | (_cmp_cached_9) | (_cmp_cached_39))
            # 4h down move, 4h still not low enough, 1d overbought
            & ((_cmp_cached_19) | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 20.0)) | (_cmp_cached_40))
            # 4h down move, 1h high
            & ((_cmp_cached_41) | (_cmp_cached_12))
            # 4h down move, 15m & 4h still high
            & (
              (_cmp_cached_47) | (_cmp_cached_75) | (_cmp_cached_54)
            )
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_47) | (_cmp_cached_62) | (_cmp_cached_74))
            # 4h down move, 4h high
            & ((_cmp_cached_47) | (_cmp_cached_14))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_60) | (_cmp_cached_110) | (_cmp_cached_23))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_60) | (_cmp_cached_54) | (_cmp_cached_23))
            # 4h down move, 4h overbought
            & ((_cmp_cached_131) | (_cmp_cached_50))
            # 4h down move, 4h overbought
            & ((_cmp_cached_87) | (_cmp_cached_73))
            # 1d down move, 4h & 1d downtrend
            & ((_cmp_cached_66) | (_cmp_cached_31) | (_cmp_cached_23))
            # 1d down move, 1d high, 1d downtrend
            & ((_cmp_cached_59) | (_cmp_cached_45) | (_cmp_cached_15))
            # 1d down move, 4h & 1d downtrend
            & ((_cmp_cached_59) | (_cmp_cached_102) | (_cmp_cached_44))
            # 4h & 1d downtrend, 1d high
            & ((_cmp("CMF_20_4h", ">", -0.50)) | (_cmp("CMF_20_1d", ">", -0.50)) | (_cmp_cached_103))
            # 4h still not low enough, 4h & 1d downtrend
            & ((_cmp_cached_145) | (_cmp_cached_31) | (_cmp_cached_149))
            # 4h & 1d high, 4h overbought
            & ((_cmp_cached_13) | (_cmp_cached_9) | (_cmp_cached_50))
            # 4h & 1d high, 1d overbought
            & ((_cmp_cached_13) | (_cmp_cached_9) | (_cmp_cached_69))
            # 4h high, 1h & 4h overbought
            & ((_cmp_cached_20) | (_cmp_cached_134) | (_cmp_cached_73))
            # 1d high, 4h downtrend, 1d overbought
            & ((_cmp_cached_103) | (_cmp_cached_31) | (_cmp_cached_74))
            # 1d high, 4h & 1d overbought
            & ((_cmp_cached_38) | (_cmp_cached_50) | (_cmp_cached_99))
            # 4h high, 1h & 4h overbought
            & ((_cmp_cached_58) | (_cmp_cached_134) | (_cmp_cached_73))
            # 4h high, 4h & 1d overbought
            & ((_cmp_cached_34) | (_cmp_cached_26) | (_cmp_cached_39))
            # 1d green, 4h down move, 4h still high
            & ((_cmp("change_pct_1d", "<", 40.0)) | (_cmp_cached_41) | (_cmp_cached_67))
          )

          # Logic
          long_entry_logic.append(
            (_cmp("RSI_3", "<", 40.0))
            & (_cmp("AROONU_14", "<", 30.0))
            & (_cmp("STOCHRSIk_14_14_3_3", "<", 20.0))
            & (_cmp_cached_108)
            & (_cmp("WILLR_84_1h", "<", -70.0))
            & (_cmp_cached_109)
            & (_cmp("BBB_20_2.0_1h", ">", 12.0))
            & (df["close_max_48"] >= (df["close"] * 1.10))
          )

        # Condition #63 - Rebuy mode (Long).
        if long_entry_condition_index == 63:
          # Protections
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          long_entry_logic.append(df["protections_long_global"] == True)

          long_entry_logic.append(
            (_cmp_cached_17)
            # 5m & 1h down move, 1h still not low enough
            & ((_cmp_cached_48) | (_cmp_cached_1) | (_cmp_cached_138))
            # 5m & 1d down move, 1d downtrend
            & ((_cmp_cached_48) | (_cmp_cached_59) | (_cmp("CMF_20_1d", ">", -0.25)))
            # 5m down move, 1d high & overbought
            & ((_cmp_cached_48) | (_cmp_cached_62) | (_cmp_cached_39))
            # 15m & 1h down move, 1h still not low enough
            & ((_cmp_cached_0) | (_cmp_cached_2) | (_cmp_cached_109))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_0) | (_cmp_cached_10) | (_cmp_cached_54))
            # 15m & 1h down move 1h still high
            & ((_cmp_cached_0) | (_cmp_cached_11) | (_cmp_cached_82))
            # 15m & 1h down move, 15m still high
            & ((_cmp_cached_0) | (_cmp_cached_8) | (_cmp_cached_46))
            # 15m & 1h down move 1h still high
            & ((_cmp_cached_0) | (_cmp_cached_8) | (_cmp_cached_30))
            # 15m & 1h down move, 4h overbought
            & ((_cmp_cached_0) | (_cmp_cached_8) | (_cmp_cached_27))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_0) | (_cmp_cached_63) | (_cmp_cached_83))
            # 15m & 4h down move, 4h still not low enough
            & ((_cmp_cached_0) | (_cmp_cached_4) | (_cmp_cached_94))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_0) | (_cmp_cached_4) | (_cmp_cached_84))
            # 15m & 4h down move, 4h still not low enough
            & ((_cmp_cached_0) | (_cmp_cached_5) | (_cmp_cached_94))
            # 15m & 4h down move, 1d downtrend
            & ((_cmp_cached_0) | (_cmp_cached_5) | (_cmp_cached_15))
            # 1h & 4h down move, 15m still high
            & ((_cmp_cached_0) | (_cmp_cached_19) | (_cmp_cached_46))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_47) | (_cmp_cached_34))
            # 15m & 1d down move, 1d high
            & ((_cmp_cached_0) | (_cmp_cached_66) | (_cmp_cached_45))
            # 15m & 1d down move, 1d high
            & ((_cmp_cached_0) | (_cmp_cached_53) | (_cmp("AROONU_14_1d", "<", 75.0)))
            # 15m down move, 15m still high, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_46) | (_cmp_cached_20))
            # 15m down move, 1h still high, 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_49) | (_cmp_cached_99))
            # 15m down move, 4h high, 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_68) | (_cmp_cached_99))
            # 15m down move, 1d high & overbought
            & ((_cmp_cached_0) | (_cmp_cached_38) | (_cmp_cached_39))
            # 15m down move, 1d high, 4h overbought
            & ((_cmp_cached_0) | (_cmp_cached_62) | (_cmp_cached_27))
            # 15m & 1h & 4h down move
            & ((_cmp_cached_3) | (_cmp_cached_2) | (_cmp_cached_5))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_11) | (_cmp_cached_12))
            # 15m & 4h down move, 15m still high
            & ((_cmp_cached_3) | (_cmp_cached_21) | (_cmp_cached_81))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_3) | (_cmp_cached_41) | (_cmp_cached_62))
            # 15m & 4h down move, 15m high
            & ((_cmp_cached_3) | (_cmp_cached_41) | (_cmp_cached_90))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_41) | (_cmp_cached_68))
            # 15m & 1d down move, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_64) | (_cmp_cached_14))
            # 15m down move, 15m still high, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_46) | (_cmp_cached_34))
            # 15m down move, 4h high, 4h downtrend
            & ((_cmp_cached_3) | (_cmp_cached_68) | (_cmp_cached_31))
            # 15m down move, 4h & 1d high
            & ((_cmp_cached_3) | (_cmp("AROONU_14_4h", "<", 75.0)) | (_cmp_cached_9))
            # 15m down move, 15m still not low enough, 1h still high
            & (
              (_cmp_cached_3) | (_cmp_cached_125) | (_cmp_cached_30)
            )
            # 15m down move, 4h & 1d overbought
            & ((_cmp_cached_3) | (_cmp_cached_26) | (_cmp_cached_99))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_16) | (_cmp_cached_10) | (_cmp_cached_56))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_16) | (_cmp_cached_60) | (_cmp_cached_93))
            # 15m down move, 1h high
            & ((_cmp_cached_16) | (_cmp("AROONU_14_1h", "<", 75.0)))
            # 15m down move, 1d high & overbought
            & ((_cmp_cached_16) | (_cmp_cached_38) | (_cmp_cached_69))
            # 15m down move, 15m high, 4h downtrend
            & ((_cmp_cached_16) | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 60.0)) | (_cmp("ROC_9_4h", ">", -50.0)))
            # 15m down move, 4h overbought
            & ((_cmp_cached_16) | (_cmp_cached_73))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_28) | (_cmp_cached_11) | (_cmp_cached_12))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_28) | (_cmp_cached_33) | (_cmp_cached_69))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_28) | (_cmp_cached_21) | (_cmp_cached_105))
            # 15m down move, 1d high, 4h overbought
            & ((_cmp_cached_28) | (_cmp_cached_42) | (_cmp_cached_27))
            # 15m down move, 4h & 1d overbought
            & ((_cmp_cached_28) | (_cmp_cached_27) | (_cmp_cached_35))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_70) | (_cmp_cached_33) | (_cmp_cached_18))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_70) | (_cmp_cached_65) | (_cmp_cached_37))
            # 15m down move, 15m downtrend, 4h high
            & ((_cmp_cached_70) | (_cmp("CMF_20_15m", ">", -0.30)) | (_cmp_cached_14))
            # 15m down move, 15m still high, 1d high
            & ((_cmp_cached_70) | (_cmp_cached_46) | (_cmp_cached_106))
            # 15m down move, 15m high, 4h high
            & ((_cmp_cached_70) | (_cmp_cached_90) | (_cmp_cached_58))
            # 15m down move, 4h high, 1h downtrend
            & ((_cmp("RSI_3_15m", "<", 30.0)) | (_cmp_cached_93) | (_cmp("ROC_9_1h", ">", -40.0)))
            # 15m down move, 4h high
            & ((_cmp_cached_70) | (_cmp_cached_55))
            # 15m & 1h down move, 15m high
            & ((_cmp_cached_100) | (_cmp_cached_65) | (_cmp_cached_24))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_100) | (_cmp_cached_41) | (_cmp_cached_34))
            # 15m down move, 15m still high, 4h overbought
            & ((_cmp_cached_100) | (_cmp_cached_81) | (_cmp_cached_26))
            # 15m down move, 15m still high, 1d overbought
            & ((_cmp_cached_100) | (_cmp_cached_81) | (_cmp_cached_51))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_100) | (_cmp_cached_68) | (_cmp_cached_26))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_100) | (_cmp_cached_58) | (_cmp_cached_26))
            # 15m still high, 4h high
            & ((_cmp("RSI_3_15m", "<", 40.0)) | (_cmp_cached_93))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp("RSI_3_1h", ">", 2.0)) | (_cmp_cached_5) | (_cmp("RSI_14_4h", "<", 30.0)))
            # 1h & 4h down move, 15m still not low enough
            & ((_cmp_cached_36) | (_cmp_cached_80) | (_cmp_cached_125))
            # 1h & 4h down move, 15m downtrend
            & ((_cmp_cached_36) | (_cmp_cached_80) | (_cmp("ROC_9_15m", ">", -30.0)))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_36) | (_cmp_cached_4) | (_cmp_cached_79))
            # 1h & 4h down move, 4h stil high
            & ((_cmp_cached_36) | (_cmp_cached_6) | (_cmp_cached_110))
            # 1h ^ 4h down move, 1d downtrend
            & ((_cmp_cached_36) | (_cmp_cached_21) | (_cmp_cached_95))
            # 1h & 1d down move, 4h still high
            & ((_cmp_cached_36) | (_cmp_cached_66) | (_cmp_cached_79))
            # 1h & 1d down move, 1h downtrend
            & ((_cmp_cached_36) | (_cmp_cached_59) | (_cmp("ROC_9_1h", ">", -40.0)))
            # 1h down move, 15m downtrend, 1h still high
            & ((_cmp_cached_36) | (_cmp("CMF_20_15m", ">", -0.40)) | (_cmp_cached_86))
            # 1h down move, 15m still not low enough, 4h still high
            & ((_cmp_cached_36) | (_cmp_cached_111) | (_cmp_cached_79))
            # 1h down move, 1h still not low enough
            & ((_cmp_cached_36) | (_cmp_cached_109))
            # 1h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_36) | (_cmp_cached_54) | (_cmp_cached_15))
            # 1h down move, 4h high
            & ((_cmp_cached_36) | (_cmp_cached_58))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_22) | (_cmp_cached_57) | (_cmp("STOCHRSIk_14_14_3_3_1d", "<", 60.0)))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_22) | (_cmp_cached_4) | (_cmp("AROONU_14_4h", "<", 20.0)))
            # 1h & 4h down move, 4h downtrend
            & ((_cmp_cached_22) | (_cmp_cached_4) | (_cmp_cached_31))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_22) | (_cmp_cached_5) | (_cmp_cached_145))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_22) | (_cmp_cached_41) | (_cmp_cached_110))
            # 1h down move, 1d high, 4h downtrend
            & ((_cmp_cached_22) | (_cmp_cached_38) | (_cmp_cached_72))
            # 1h down move, 4h downtrend
            & ((_cmp_cached_22) | (_cmp_cached_31))
            # 1h, 1d downtrend
            & ((_cmp_cached_22) | (_cmp_cached_95))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp("RSI_14_4h", "<", 30.0)))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp_cached_145))
            # 1h & 4h down move, 15m still high
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp_cached_75))
            # 1h & 4h down move, 15m still not low enough
            & ((_cmp_cached_1) | (_cmp_cached_5) | (_cmp_cached_111))
            # 1h & 4h down move, 1h still not low enough
            & ((_cmp_cached_1) | (_cmp_cached_5) | (_cmp_cached_132))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_1) | (_cmp_cached_21) | (_cmp_cached_42))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_21) | (_cmp_cached_44))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_1) | (_cmp_cached_19) | (_cmp_cached_54))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_1) | (_cmp_cached_41) | (_cmp("ROC_9_1d", "<", 70.0)))
            # 1h & 1d down move, 1h still high
            & ((_cmp_cached_1) | (_cmp_cached_66) | (_cmp_cached_82))
            # 1h & 1d down move, 4h high
            & ((_cmp_cached_1) | (_cmp_cached_59) | (_cmp_cached_58))
            # 1h & 1d downtrend, 1d overbought
            & ((_cmp_cached_1) | (_cmp_cached_107) | (_cmp_cached_78))
            # 1h down move, 1h downtrend, 1h still not low enough
            & ((_cmp_cached_1) | (_cmp("CMF_20_1h", ">", -0.20)) | (_cmp_cached_138))
            # 1h down move, 1h downtrend, 1h still not low enough
            & ((_cmp_cached_1) | (_cmp("CMF_20_1h", ">", -0.20)) | (_cmp_cached_109))
            # 1h down move, 1h downtrend
            & ((_cmp_cached_1) | (_cmp("CMF_20_1h", ">", -0.30)))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_1) | (_cmp_cached_45) | (_cmp_cached_35))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 20.0)))
            # 1h down move, 1d overbought
            & ((_cmp_cached_1) | (_cmp_cached_74))
            # 1h & 4h down move, 1h still not low enough
            & ((_cmp_cached_2) | (_cmp_cached_5) | (_cmp_cached_109))
            # 1h & 4h down move, 15m high
            & ((_cmp_cached_2) | (_cmp_cached_6) | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 90.0)))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_2) | (_cmp_cached_6) | (_cmp_cached_44))
            # 1h & 4h down mov, 1d overbought
            & ((_cmp_cached_2) | (_cmp_cached_19) | (_cmp_cached_29))
            # 1h down move, 1d downtrend, 1d high
            & ((_cmp_cached_2) | (_cmp("CMF_20_1d", ">", -0.30)) | (_cmp_cached_84))
            # 1h down move, 1h still high
            & ((_cmp_cached_2) | (_cmp_cached_49))
            # 1h down move, 1d high, 4h downtrend
            & ((_cmp_cached_2) | (_cmp_cached_45) | (_cmp_cached_31))
            # 1h down move, 1d high, 1d downtrend
            & ((_cmp_cached_2) | (_cmp_cached_45) | (_cmp_cached_15))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_2) | (_cmp_cached_38) | (_cmp_cached_51))
            # 1h down move, 1h still high
            & ((_cmp_cached_2) | (_cmp_cached_82))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_10) | (_cmp_cached_21) | (_cmp_cached_42))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_10) | (_cmp_cached_76) | (_cmp_cached_88))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_10) | (_cmp_cached_12) | (_cmp_cached_29))
            # 1h down move, 4h still high
            & ((_cmp_cached_10) | (_cmp_cached_67))
            # 1h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_10) | (_cmp_cached_79) | (_cmp_cached_149))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_10) | (_cmp_cached_58) | (_cmp_cached_27))
            # 1h down move, 1h & 1d high
            & ((_cmp_cached_11) | (_cmp_cached_12) | (_cmp_cached_38))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_11) | (_cmp_cached_60) | (_cmp_cached_93))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_60) | (_cmp_cached_29))
            # 1h down move, 1h still not low enough, 4h still high
            & ((_cmp_cached_11) | (_cmp_cached_109) | (_cmp_cached_54))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_11) | (_cmp_cached_34) | (_cmp_cached_44))
            # 1h down move, 1h still high, 1h downtrend
            & ((_cmp_cached_11) | (_cmp_cached_86) | (_cmp("ROC_9_1h", ">", -50.0)))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_11) | (_cmp_cached_32) | (_cmp_cached_26))
            # 1h down move, 1h still high, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_30) | (_cmp_cached_40))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_11) | (_cmp_cached_34) | (_cmp_cached_26))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_34) | (_cmp("ROC_9_1d", "<", 70.0)))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_8) | (_cmp_cached_19) | (_cmp_cached_112))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_8) | (_cmp_cached_19) | (_cmp_cached_43))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_8) | (_cmp_cached_60) | (_cmp_cached_12))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_8) | (_cmp_cached_60) | (_cmp_cached_32))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_8) | (_cmp_cached_12) | (_cmp_cached_50))
            # 1h down move, 1h high
            & ((_cmp_cached_8) | (_cmp_cached_18))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_8) | (_cmp_cached_32) | (_cmp_cached_26))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_8) | (_cmp_cached_42) | (_cmp_cached_74))
            # 1h down move, 1d high, 4h downtrend
            & ((_cmp_cached_8) | (_cmp_cached_38) | (_cmp_cached_139))
            # 1h down move, 1d high, 4h overbought
            & ((_cmp_cached_8) | (_cmp_cached_9) | (_cmp_cached_114))
            # 1h down move, 1h & 4h still high
            & ((_cmp_cached_8) | (_cmp_cached_82) | (_cmp_cached_54))
            # 1h down move, 1h highm 1d overbought
            & ((_cmp_cached_8) | (_cmp_cached_112) | (_cmp_cached_51))
            # 1h down move, 4h overbought
            & ((_cmp_cached_8) | (_cmp_cached_98))
            # 4h down move, 1d downtrend
            & ((_cmp_cached_19) | (_cmp_cached_95))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_25) | (_cmp_cached_12) | (_cmp_cached_73))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_25) | (_cmp_cached_12) | (_cmp_cached_149))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_25) | (_cmp_cached_93) | (_cmp_cached_115))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_25) | (_cmp_cached_14) | (_cmp_cached_26))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_25) | (_cmp_cached_58) | (_cmp_cached_27))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_25) | (_cmp_cached_9) | (_cmp_cached_29))
            # 1h down move, 1h still high, 1d overbought
            & ((_cmp_cached_25) | (_cmp_cached_30) | (_cmp_cached_74))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_33) | (_cmp("RSI_14_1d", "<", 80.0)) | (_cmp("ROC_9_1d", "<", 150.0)))
            # 1h down move, 15m high, 1h high
            & ((_cmp_cached_33) | (_cmp_cached_90) | (_cmp_cached_12))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_33) | (_cmp_cached_18) | (_cmp_cached_69))
            # 1h down move, 1h & 4h overbought
            & ((_cmp_cached_33) | (_cmp_cached_61) | (_cmp_cached_27))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_65) | (_cmp("RSI_3_4h", ">", 65.0)) | (_cmp_cached_74))
            # 1h down move, 1h high & overbought
            & ((_cmp_cached_65) | (_cmp_cached_12) | (_cmp_cached_61))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_65) | (_cmp_cached_14) | (_cmp_cached_73))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_63) | (_cmp_cached_52) | (_cmp_cached_23))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_63) | (_cmp_cached_14) | (_cmp_cached_115))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_63) | (_cmp_cached_105) | (_cmp_cached_146))
            # 1h down move, 15m high, 1h high
            & ((_cmp_cached_130) | (_cmp_cached_90) | (_cmp_cached_37))
            # 1h down move, 1h high & overbought
            & ((_cmp_cached_130) | (_cmp_cached_52) | (_cmp_cached_61))
            # 4h down move, 1h still not low enough, 4h downtrend
            & ((_cmp_cached_80) | (_cmp_cached_132) | (_cmp_cached_72))
            # 4h down move, 1h & 4h downtrend
            & ((_cmp_cached_80) | (_cmp_cached_124) | (_cmp_cached_72))
            # 4h down move, 1d high, 4h downtrend
            & ((_cmp_cached_57) | (_cmp_cached_42) | (_cmp_cached_102))
            # 4h down move, 1h still high
            & ((_cmp_cached_57) | (_cmp_cached_30))
            # 4h down move, 4h & 1d downtrend
            & ((_cmp_cached_57) | (_cmp("ROC_9_4h", ">", -15.0)) | (_cmp_cached_15))
            # 4h & 1d down move, 1d overbought
            & ((_cmp_cached_4) | (_cmp_cached_107) | (_cmp_cached_78))
            # 4h down move, 1d still high, 1d downtrend
            & ((_cmp_cached_4) | (_cmp_cached_121) | (_cmp_cached_23))
            # 4h down move, 1d high, 4h downtrend
            & ((_cmp_cached_4) | (_cmp_cached_103) | (_cmp_cached_31))
            # 4h down move, 15m high, 15m downtrend
            & ((_cmp_cached_4) | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 60.0)) | (_cmp("ROC_9_15m", ">", -10.0)))
            # 4h down move, 1h still high, 1d downtrend
            & ((_cmp_cached_4) | (_cmp_cached_82) | (_cmp_cached_15))
            # 4h down move, 1h high
            & ((_cmp_cached_4) | (_cmp_cached_56))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_4) | (_cmp_cached_79) | (_cmp_cached_15))
            # 4h down move, 4h downtrend, 1d overbought
            & ((_cmp_cached_4) | (_cmp_cached_72) | (_cmp_cached_40))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_53) | (_cmp("AROONU_14_1d", "<", 60.0)))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_118) | (_cmp_cached_42))
            # 4h down move, 1h high
            & ((_cmp_cached_5) | (_cmp_cached_49))
            # 4h down move, 1h still high, 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_30) | (_cmp_cached_23))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_5) | (_cmp_cached_62) | (_cmp_cached_39))
            # 4h down move, 15m still high
            & ((_cmp_cached_6) | (_cmp("AROONU_14_15m", "<", 45.0)))
            # 4h down move, 1h still not low enough, 1d downtrend
            & ((_cmp_cached_6) | (_cmp_cached_138) | (_cmp_cached_15))
            # 4h down move, 4h still high, 1d high
            & ((_cmp_cached_6) | (_cmp_cached_43) | (_cmp_cached_9))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_6) | (_cmp_cached_42) | (_cmp_cached_69))
            # 4h down move, 15m still high, 4h high
            & ((_cmp_cached_21) | (_cmp_cached_81) | (_cmp_cached_13))
            # 4h down move, 1h & 4h still high
            & ((_cmp_cached_21) | (_cmp_cached_82) | (_cmp_cached_79))
            # 4h dowqn move, 4h still high, 1d downtrend
            & ((_cmp_cached_21) | (_cmp_cached_94) | (_cmp_cached_23))
            # 4h down move, 4h high, 1d overbought
            & ((_cmp_cached_19) | (_cmp_cached_20) | (_cmp_cached_35))
            # 4h down move, 1h high, 4h downtrend
            & ((_cmp_cached_19) | (_cmp_cached_12) | (_cmp_cached_102))
            # 4h down move, 4h & 1d downtrend
            & ((_cmp_cached_47) | (_cmp_cached_13) | (_cmp_cached_9))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_47) | (_cmp_cached_38) | (_cmp_cached_69))
            # 4h down move, 1h high, 1d downtrend
            & ((_cmp_cached_47) | (_cmp_cached_37) | (_cmp_cached_15))
            # 4h down move, 4h & 1d overbought
            & ((_cmp_cached_47) | (_cmp_cached_27) | (_cmp_cached_35))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_60) | (_cmp_cached_110) | (_cmp_cached_23))
            # 4h down move, 4h high, 1d overbought
            & ((_cmp_cached_60) | (_cmp_cached_13) | (_cmp_cached_40))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_60) | (_cmp_cached_54) | (_cmp_cached_23))
            # 4h down move, 1h high, 1d overbought
            & ((_cmp_cached_87) | (_cmp_cached_83) | (_cmp_cached_51))
            # 4h down move, 4h high & overbought
            & ((_cmp_cached_87) | (_cmp_cached_58) | (_cmp_cached_26))
            # 1d down move, 1h high & overbought
            & ((_cmp_cached_133) | (_cmp_cached_83) | (_cmp_cached_61))
            # 1d down move, 1h high & overbought
            & ((_cmp_cached_118) | (_cmp_cached_45) | (_cmp_cached_69))
            # 1d down move, 4h high & overbought
            & ((_cmp_cached_107) | (_cmp_cached_20) | (_cmp_cached_50))
            # 1h downtrend, 1h high
            & ((_cmp("CMF_20_1h", ">", -0.20)) | (_cmp_cached_18))
            # 4h & 1d downtrend, 1d high
            & ((_cmp("CMF_20_4h", ">", -0.30)) | (_cmp("CMF_20_1d", ">", -0.30)) | (_cmp("STOCHRSIk_14_14_3_3_1d", "<", 60.0)))
            # 1d downtrend, 1d high & overbought
            & ((_cmp("CMF_20_1d", ">", -0.30)) | (_cmp_cached_103) | (_cmp_cached_29))
            # 1d downtrend, 1d high & overbought
            & ((_cmp("CMF_20_1d", ">", -0.40)) | (_cmp_cached_103) | (_cmp_cached_39))
            # 15m still high, 1h overbought
            & ((_cmp_cached_81) | (_cmp_cached_134))
            # 15m still high, 4h overbought
            & ((_cmp_cached_81) | (_cmp_cached_114))
            # 15m still high, 1h high
            & ((_cmp_cached_46) | (_cmp_cached_92))
            # 15m still high, 4h high & overbought
            & ((_cmp_cached_46) | (_cmp_cached_13) | (_cmp_cached_50))
            # 15m still high, 4h downtrend, 1d overbought
            & ((_cmp_cached_46) | (_cmp_cached_31) | (_cmp_cached_40))
            # 1h still high, 4h & 1d downtrend
            & ((_cmp_cached_86) | (_cmp_cached_31) | (_cmp_cached_44))
            # 1h high, 4h high, 1h overbought
            & ((_cmp_cached_12) | (_cmp_cached_14) | (_cmp_cached_85))
            # 1h & 4h high, 4h overbought
            & ((_cmp_cached_12) | (_cmp_cached_14) | (_cmp_cached_73))
            # 1h & 1d high, 1h overbought
            & ((_cmp_cached_12) | (_cmp_cached_45) | (_cmp_cached_85))
            # 1h high, 1h & 4h overbought
            & ((_cmp_cached_12) | (_cmp_cached_61) | (_cmp_cached_73))
            # 1h high, 1d downtrend
            & ((_cmp_cached_18) | (_cmp_cached_44))
            # 4h still not low enough, 4h & 1d downtrend
            & ((_cmp_cached_145) | (_cmp_cached_31) | (_cmp_cached_149))
            # 4h still high, 1d high, 4h downtrend
            & ((_cmp_cached_43) | (_cmp_cached_9) | (_cmp_cached_72))
            # 4h high, 1h & 1d downtrend
            & ((_cmp_cached_13) | (_cmp_cached_120) | (_cmp_cached_15))
            # 4h & 1d high, 1d overbought
            & ((_cmp_cached_20) | (_cmp_cached_9) | (_cmp_cached_35))
            # 4h & 1d high, 4h overbought
            & ((_cmp_cached_14) | (_cmp_cached_9) | (_cmp_cached_27))
            # 4h high, 1h & 4h overbought
            & ((_cmp_cached_14) | (_cmp_cached_61) | (_cmp_cached_73))
            # 1d high, 4h & 1d downtrend
            & ((_cmp_cached_42) | (_cmp_cached_31) | (_cmp_cached_15))
            # 1d high, 1h & 4h downtrend
            & ((_cmp_cached_103) | (_cmp_cached_124) | (_cmp("ROC_9_4h", ">", -50.0)))
            # 1d high, 1h & 1d overbought
            & ((_cmp_cached_103) | (_cmp_cached_85) | (_cmp_cached_29))
            # 1d high, 1h & 4h down move
            & ((_cmp_cached_9) | (_cmp("ROC_9_1h", "<", 25.0)) | (_cmp_cached_123))
            # 1d high, 4h & 1d overbought
            & ((_cmp_cached_9) | (_cmp_cached_26) | (_cmp_cached_51))
            # 1h high, 4h & 1d overbought
            & ((_cmp_cached_83) | (_cmp_cached_26) | (_cmp_cached_29))
            # 4h still high, 4h & 1d downtrend
            & ((_cmp_cached_79) | (_cmp_cached_31) | (_cmp_cached_44))
            # 4h high, 1h & 1d downtrend
            & ((_cmp_cached_58) | (_cmp_cached_120) | (_cmp_cached_15))
            # 4h high, 4h & 1d overbought
            & ((_cmp_cached_58) | (_cmp_cached_26) | (_cmp_cached_51))
            # 4h high, 1h overbought, 1d downtrend
            & ((_cmp_cached_34) | (_cmp_cached_134) | (_cmp_cached_150))
            # 4h high, 4h overbought
            & ((_cmp_cached_34) | (_cmp_cached_27))
            # 4h high, 1h & 4h overbought
            & ((_cmp_cached_55) | (_cmp_cached_85) | (_cmp_cached_98))
            # 1d high, 4h & 1d overbought
            & ((_cmp_cached_62) | (_cmp_cached_73) | (_cmp_cached_29))
            # 1h & 4h overbought
            & ((_cmp_cached_129) | (_cmp_cached_114))
            # 1d green with top wick, 4h high
            & ((_cmp("change_pct_1d", "<", 30.0)) | (_cmp("top_wick_pct_1d", "<", 20.0)) | (_cmp_cached_20))
            # 1d top wick, 4h down move, 1d overbought
            & ((_cmp("top_wick_pct_1d", "<", 50.0)) | (_cmp_cached_41) | (_cmp_cached_99))
            # drop in last 20 days, 4h high
            & (_gt_mul("close", "high_max_20_1d", 0.10) | (_cmp_cached_55))
            # drop in last 20 days, 1h high, 1d downtrend
            & (_gt_mul("close", "high_max_20_1d", 0.20) | (_cmp_cached_12) | (_cmp_cached_150))
            # drop in last 20 days, 1d high, 1d downtrend
            & (
              _gt_mul("close", "high_max_20_1d", 0.20)
              | (_cmp_cached_106)
              | (_cmp_cached_141)
            )
          )

          # Logic
          long_entry_logic.append(
            (_cmp("RSI_3", ">", 0.0))
            & (_cmp("RSI_3", "<", 50.0))
            & (_cmp("AROONU_14", "<", 25.0))
            & (df["EMA_26"] > df["EMA_12"])
            & ((df["EMA_26"] - df["EMA_12"]) > (df["open"] * 0.022))
            & _ema_26_12_spread_gt_open_pct
          )

        # Condition #101 - Rapid mode (Long).
        if long_entry_condition_index == 101:
          # Protections
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          long_entry_logic.append(df["protections_long_global"] == True)

          long_entry_logic.append(_cmp("RSI_14_1h", "<", 80.0))
          long_entry_logic.append(_cmp("RSI_14_4h", "<", 80.0))
          long_entry_logic.append(_cmp("RSI_14_1d", "<", 80.0))
          # big drop in the last hour
          long_entry_logic.append(_gt_mul("close", "close_max_12", 0.50))
          # 5m & 4h down move, 1d downtrend
          long_entry_logic.append((_cmp_cached_104) | (_cmp_cached_4) | (_cmp_cached_15))
          # 5m & 4h down move, 15m still high
          long_entry_logic.append(
            (_cmp_cached_104) | (_cmp_cached_21) | (_cmp_cached_75)
          )
          # 5 & 15m down move, 1h high
          long_entry_logic.append(
            (_cmp_cached_143) | (_cmp_cached_140) | (_cmp_cached_83)
          )
          # 5m down move, 1h & 4h high
          long_entry_logic.append((_cmp_cached_143) | (_cmp_cached_92) | (_cmp_cached_32))
          # 15m & 1h down move, 4h still not low enough
          long_entry_logic.append(
            (_cmp_cached_7) | (_cmp_cached_22) | (_cmp_cached_94)
          )
          # 15m & 1h down move, 1d still high
          long_entry_logic.append((_cmp_cached_7) | (_cmp_cached_22) | (_cmp_cached_135))
          # 15m & 1h down move, 4h still high
          long_entry_logic.append((_cmp_cached_7) | (_cmp_cached_2) | (_cmp_cached_110))
          # 15m & 4h down move, 4h high
          long_entry_logic.append((_cmp_cached_7) | (_cmp_cached_8) | (_cmp("AROONU_14_4h", "<", 75.0)))
          # 15m & 1h down move, 1h still not low enough
          long_entry_logic.append(
            (_cmp_cached_7) | (_cmp_cached_25) | (_cmp_cached_109)
          )
          # 15m & 4h down move, 4h still not low enough
          long_entry_logic.append(
            (_cmp_cached_7) | (_cmp_cached_4) | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 20.0))
          )
          # 15m & 4h down move, 1d downtrend
          long_entry_logic.append((_cmp_cached_7) | (_cmp_cached_4) | (_cmp_cached_15))
          # 15m & 4h down move, 4h still not low enough
          long_entry_logic.append((_cmp_cached_7) | (_cmp_cached_21) | (_cmp_cached_145))
          # 15m & 4h down move, 4h still not low enough
          long_entry_logic.append(
            (_cmp_cached_7) | (_cmp_cached_21) | (_cmp_cached_94)
          )
          # 15m down move, 15m still not low enough, 1h high
          long_entry_logic.append(
            (_cmp_cached_7) | (_cmp("AROONU_14_15m", "<", 20.0)) | (_cmp_cached_112)
          )
          # 15m down move, 15m still not low enough, 4h high
          long_entry_logic.append(
            (_cmp_cached_7) | (_cmp_cached_111) | (_cmp_cached_58)
          )
          # 15m down move, 4h high, 1d overbought
          long_entry_logic.append((_cmp_cached_7) | (_cmp_cached_13) | (_cmp_cached_51))
          # 15m & 1h & 1d down move
          long_entry_logic.append((_cmp_cached_17) | (_cmp_cached_1) | (_cmp_cached_53))
          # 15m down move, 1h still not low enough, 1d high
          long_entry_logic.append(
            (_cmp_cached_17) | (_cmp_cached_109) | (_cmp_cached_38)
          )
          # 15m & 1h down move, 1h still not low enough
          long_entry_logic.append(
            (_cmp_cached_17) | (_cmp_cached_8) | (_cmp_cached_109)
          )
          # 15m & 1h down move, 4h high
          long_entry_logic.append(
            (_cmp_cached_17) | (_cmp_cached_8) | (_cmp_cached_34)
          )
          # 15m & 1h down move, 4h high
          long_entry_logic.append(
            (_cmp_cached_17) | (_cmp_cached_33) | (_cmp_cached_34)
          )
          # 15m & 1h down move, 1h high
          long_entry_logic.append(
            (_cmp_cached_17) | (_cmp_cached_63) | (_cmp_cached_56)
          )
          # 15m & 1h down move, 4h high
          long_entry_logic.append(
            (_cmp_cached_17) | (_cmp_cached_63) | (_cmp_cached_55)
          )
          # 15m & 4h down move, 1d still high
          long_entry_logic.append(
            (_cmp_cached_17) | (_cmp_cached_57) | (_cmp("STOCHRSIk_14_14_3_3_1d", "<", 40.0))
          )
          # 15m & 4h down move, 4h still high
          long_entry_logic.append(
            (_cmp_cached_17) | (_cmp_cached_47) | (_cmp_cached_54)
          )
          # 15m & 1d down move
          long_entry_logic.append((_cmp_cached_17) | (_cmp("RSI_3_1d", ">", 5.0)))
          # 15m & 1d down move, 4h still not low enough
          long_entry_logic.append(
            (_cmp_cached_17) | (_cmp_cached_77) | (_cmp_cached_94)
          )
          # 15m down move, 1h still high, 4h high
          long_entry_logic.append(
            (_cmp_cached_17) | (_cmp_cached_49) | (_cmp_cached_55)
          )
          # 15m down move, 1h high & overbought
          long_entry_logic.append((_cmp_cached_17) | (_cmp_cached_18) | (_cmp_cached_61))
          # 15m down move, 1h high & overbought
          long_entry_logic.append(
            (_cmp_cached_17) | (_cmp_cached_37) | (_cmp_cached_61)
          )
          # 15m & 1h down move, 4h still high
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp_cached_10) | (_cmp_cached_54)
          )
          # 15m & 1h down move, 1h still not low enough
          long_entry_logic.append((_cmp_cached_0) | (_cmp_cached_11) | (_cmp("AROONU_14_1h", "<", 25.0)))
          # 15m & 1h down move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp_cached_8) | (_cmp_cached_82)
          )
          # 15m & 1h down move, 4h still high
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp_cached_8) | (_cmp_cached_54)
          )
          # 15m & 1h down move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp_cached_25) | (_cmp_cached_30)
          )
          # 15m & 1h down move, 1h high
          long_entry_logic.append((_cmp_cached_0) | (_cmp_cached_63) | (_cmp_cached_18))
          # 15m & 1h down move, 1h high
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp_cached_63) | (_cmp_cached_37)
          )
          # 15m & 4h down move, 15m still not low enough
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp_cached_4) | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 10.0))
          )
          # 15m & 4h down move, 1d downtrend
          long_entry_logic.append((_cmp_cached_0) | (_cmp_cached_6) | (_cmp_cached_149))
          # 15m & 4h down move, 1d high
          long_entry_logic.append((_cmp_cached_0) | (_cmp_cached_21) | (_cmp_cached_103))
          # 15m & 4h down move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp_cached_19) | (_cmp_cached_30)
          )
          # 15m & 4h down move, 4h high
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp_cached_19) | (_cmp_cached_58)
          )
          # 15m & 1d down move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp_cached_64) | (_cmp_cached_30)
          )
          # 15m down move, 15m still not low enough, 1h still high
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp_cached_111) | (_cmp_cached_30)
          )
          # 15m down move, 1h still high, 4h high
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp_cached_30) | (_cmp_cached_93)
          )
          # 15m down move, 1h & 4h high
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp_cached_56) | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 75.0))
          )
          # 15m & 1h down move, 15m still not low enough
          long_entry_logic.append(
            (_cmp_cached_3) | (_cmp_cached_2) | (_cmp_cached_125)
          )
          # 15m & 1h down move, 4h high
          long_entry_logic.append(
            (_cmp_cached_3) | (_cmp_cached_10) | (_cmp_cached_55)
          )
          # 15m & 1h down move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_3) | (_cmp_cached_11) | (_cmp_cached_82)
          )
          # 15m & 1h down move, 1h still high
          long_entry_logic.append((_cmp_cached_3) | (_cmp_cached_33) | (_cmp_cached_49))
          # 15m & 4h & 1d down move
          long_entry_logic.append((_cmp_cached_3) | (_cmp_cached_5) | (_cmp_cached_59))
          # 15m & 4h down move, 1h high
          long_entry_logic.append(
            (_cmp_cached_3) | (_cmp_cached_5) | (_cmp_cached_37)
          )
          # 15m & 4h down move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_3) | (_cmp_cached_6) | (_cmp_cached_30)
          )
          # 15m & 4h down move, 15m still not low enough
          long_entry_logic.append((_cmp_cached_3) | (_cmp_cached_21) | (_cmp_cached_111))
          # 15m & 4h down move, 4h still high
          long_entry_logic.append((_cmp_cached_3) | (_cmp_cached_60) | (_cmp_cached_43))
          # 1h & 1d down move, 1d overbought
          long_entry_logic.append((_cmp_cached_2) | (_cmp_cached_133) | (_cmp_cached_78))
          # 15m down move, 15m still not low enough, 1h high
          long_entry_logic.append(
            (_cmp_cached_3) | (_cmp("AROONU_14_15m", "<", 25.0)) | (_cmp_cached_37)
          )
          # 15m down move, 4h high & overbought
          long_entry_logic.append((_cmp_cached_3) | (_cmp_cached_20) | (_cmp_cached_73))
          # 15m down move, 1h & 4h high
          long_entry_logic.append(
            (_cmp_cached_3) | (_cmp_cached_56) | (_cmp_cached_93)
          )
          # 15m & 1h down move, 4h high
          long_entry_logic.append(
            (_cmp_cached_16) | (_cmp_cached_8) | (_cmp_cached_55)
          )
          # 15m & 1d down move, 1h high
          long_entry_logic.append(
            (_cmp_cached_16) | (_cmp_cached_53) | (_cmp_cached_56)
          )
          # 15m down move, 1d high & overbought
          long_entry_logic.append((_cmp_cached_16) | (_cmp_cached_9) | (_cmp_cached_39))
          # 15m down move, 1h high, 1d downtrend
          long_entry_logic.append(
            (_cmp_cached_16) | (_cmp_cached_37) | (_cmp_cached_15)
          )
          # 15m down move, 1d high & overbought
          long_entry_logic.append(
            (_cmp_cached_16) | (_cmp_cached_37) | (_cmp_cached_39)
          )
          # 15m & 1h down move, 1h high
          long_entry_logic.append(
            (_cmp_cached_28) | (_cmp_cached_11) | (_cmp_cached_112)
          )
          # 15m & 1h down move, 1h high
          long_entry_logic.append((_cmp_cached_28) | (_cmp_cached_97) | (_cmp_cached_92))
          # 15m down move, 15m still not low enough, 4h high
          long_entry_logic.append(
            (_cmp_cached_28) | (_cmp("AROONU_14_15m", "<", 25.0)) | (_cmp_cached_68)
          )
          # 15m down move, 15m still not low enough, 1h high
          long_entry_logic.append(
            (_cmp_cached_28) | (_cmp_cached_125) | (_cmp_cached_18)
          )
          # 15m & 1h down move, 1h high
          long_entry_logic.append((_cmp_cached_70) | (_cmp_cached_65) | (_cmp_cached_12))
          # 1h & 4h down move, 15m downtrend
          long_entry_logic.append((_cmp_cached_36) | (_cmp_cached_80) | (_cmp("ROC_9_15m", ">", -30.0)))
          # 1h & 4h & 1d down move
          long_entry_logic.append((_cmp_cached_36) | (_cmp_cached_5) | (_cmp_cached_64))
          # 1h & 4h down move, 4h high
          long_entry_logic.append((_cmp_cached_36) | (_cmp_cached_60) | (_cmp_cached_13))
          # 1h & 4h down move, 4h downtrend
          long_entry_logic.append((_cmp_cached_22) | (_cmp_cached_57) | (_cmp_cached_31))
          # 1h & 4h down move, 4h downtrend
          long_entry_logic.append((_cmp_cached_22) | (_cmp_cached_5) | (_cmp_cached_72))
          # 1h & 4h down move, 4h still not low enough
          long_entry_logic.append(
            (_cmp_cached_22) | (_cmp_cached_6) | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 20.0))
          )
          # 1h & 4h down move, 1d low
          long_entry_logic.append((_cmp_cached_1) | (_cmp_cached_4) | (_cmp("CMF_20_1d", ">", -0.2)))
          # 1h & 4h down move, 4h still not low enough
          long_entry_logic.append((_cmp_cached_1) | (_cmp_cached_5) | (_cmp("AROONU_14_4h", "<", 20.0)))
          # 1h & 4h down move, 4h still not low enough
          long_entry_logic.append(
            (_cmp_cached_1) | (_cmp_cached_21) | (_cmp_cached_94)
          )
          # 1h & 1d down move, 5m moving down
          long_entry_logic.append((_cmp_cached_1) | (_cmp_cached_59) | (_cmp("ROC_2", ">", -0.0)))
          # 1h down move, 4h downtrend
          long_entry_logic.append((_cmp_cached_1) | (_cmp_cached_72))
          # 1h down move, 1d downtrend
          long_entry_logic.append((_cmp_cached_1) | (_cmp_cached_23))
          # 1h & 4h & 1d down move
          long_entry_logic.append((_cmp_cached_2) | (_cmp_cached_6) | (_cmp_cached_77))
          # 1h & 4h down move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_2) | (_cmp_cached_19) | (_cmp_cached_82)
          )
          # 1h & 4h down move, 1h still not low enough
          long_entry_logic.append(
            (_cmp_cached_2) | (_cmp_cached_47) | (_cmp_cached_109)
          )
          # 1h & 4h down move, 1h still high
          long_entry_logic.append((_cmp_cached_2) | (_cmp_cached_66) | (_cmp_cached_86))
          # 1h down move, 1d high & overbought
          long_entry_logic.append((_cmp_cached_10) | (_cmp_cached_38) | (_cmp_cached_51))
          # 1h down move, 1h still not low enough, 4h high
          long_entry_logic.append(
            (_cmp_cached_10) | (_cmp_cached_132) | (_cmp_cached_20)
          )
          # 1h & 4h down move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_11) | (_cmp_cached_21) | (_cmp_cached_30)
          )
          # 1h & 4h down move, 1d high
          long_entry_logic.append(
            (_cmp_cached_11) | (_cmp_cached_19) | (_cmp_cached_84)
          )
          # 1h & 4h down move, 1h high
          long_entry_logic.append(
            (_cmp_cached_11) | (_cmp_cached_87) | (_cmp_cached_34)
          )
          # 1h & 4h down move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_8) | (_cmp_cached_47) | (_cmp_cached_30)
          )
          # 1h down move, 4h high, 1d overbought
          long_entry_logic.append((_cmp_cached_8) | (_cmp_cached_32) | (_cmp_cached_40))
          # 1h down move, 4h & 1d high
          long_entry_logic.append((_cmp_cached_8) | (_cmp_cached_20) | (_cmp_cached_9))
          # 1h down move, 15m high
          long_entry_logic.append((_cmp_cached_25) | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 80.0)))
          # 1h down move, 1h high, 1d overbought
          long_entry_logic.append((_cmp_cached_25) | (_cmp_cached_12) | (_cmp_cached_39))
          # 1h down move, 1h & 4h high
          long_entry_logic.append((_cmp_cached_33) | (_cmp_cached_18) | (_cmp_cached_14))
          # 1h down move, 1h high & overbought
          long_entry_logic.append(
            (_cmp_cached_130) | (_cmp_cached_37) | (_cmp_cached_61)
          )
          # 1h down move, 4h high
          long_entry_logic.append((_cmp_cached_97) | (_cmp_cached_32))
          # 4h down move, 15m still high
          long_entry_logic.append((_cmp_cached_57) | (_cmp_cached_113))
          # 4h down move, 1d still high, 1d downtrend
          long_entry_logic.append((_cmp_cached_4) | (_cmp_cached_135) | (_cmp_cached_15))
          # 4h down move, 15m 4h still high
          long_entry_logic.append(
            (_cmp_cached_4) | (_cmp_cached_113) | (_cmp_cached_43)
          )
          # 4h & 1d down move, 4h high
          long_entry_logic.append((_cmp_cached_5) | (_cmp_cached_64) | (_cmp_cached_13))
          # 4h down move, 1h still high
          long_entry_logic.append((_cmp_cached_5) | (_cmp_cached_49))
          # 4h down move, 4h still high
          long_entry_logic.append((_cmp_cached_5) | (_cmp_cached_43))
          # 4h down move, 1d high & overbought
          long_entry_logic.append(
            (_cmp_cached_5) | (_cmp_cached_62) | (_cmp_cached_39)
          )
          # 4h down move, 4h & 1d downtrend
          long_entry_logic.append((_cmp_cached_5) | (_cmp_cached_102) | (_cmp_cached_141))
          # 4h down move, 4h & 1d downtrend
          long_entry_logic.append((_cmp_cached_6) | (_cmp_cached_31) | (_cmp_cached_23))
          # 4h dowqn move, 4h still high, 1d downtrend
          long_entry_logic.append(
            (_cmp_cached_21) | (_cmp_cached_54) | (_cmp_cached_23)
          )
          # 4h down move, 4h & 1d high
          long_entry_logic.append((_cmp_cached_41) | (_cmp_cached_20) | (_cmp_cached_9))
          # 4h & 1d down move, 4h still high
          long_entry_logic.append(
            (_cmp_cached_47) | (_cmp_cached_66) | (_cmp_cached_54)
          )
          # 4h down move, 4h high, 1d downtrend
          long_entry_logic.append(
            (_cmp_cached_47) | (_cmp_cached_58) | (_cmp_cached_146)
          )
          # 4h down move, 4h still high
          long_entry_logic.append((_cmp_cached_87) | (_cmp_cached_79))
          # 4h down move, 4h overbought
          long_entry_logic.append((_cmp_cached_87) | (_cmp_cached_26))
          # 1d down move, 1h still high, 4h high
          long_entry_logic.append((_cmp_cached_53) | (_cmp_cached_49) | (_cmp_cached_93))
          # 1d down move, 1h high & overbought
          long_entry_logic.append(
            (_cmp_cached_133) | (_cmp_cached_83) | (_cmp_cached_61)
          )
          # 1d down move, 4h high, 1d overbought
          long_entry_logic.append(
            (_cmp_cached_107) | (_cmp_cached_55) | (_cmp_cached_78)
          )
          # 4h still high, 4h moving lower, 4h overbought
          long_entry_logic.append(
            (_cmp_cached_43) | (df["AROONU_14_4h"] > df["AROONU_14_4h"].shift(48)) | (_cmp_cached_73)
          )
          # 1h high, 1d downtrend
          long_entry_logic.append((_cmp_cached_45) | (_cmp_cached_23))
          # 1d high, 4h & 1d overbought
          long_entry_logic.append((_cmp_cached_103) | (_cmp_cached_123) | (_cmp_cached_99))
          # 1d high, 4h & 1d overbought
          long_entry_logic.append((_cmp_cached_9) | (_cmp_cached_27) | (_cmp_cached_39))
          # 1h high, 4h downtrend
          long_entry_logic.append((_cmp_cached_37) | (_cmp_cached_31))
          # 1h high, 4h overbought
          long_entry_logic.append((_cmp_cached_37) | (_cmp_cached_114))
          # 4h high, 4h & 1d overbought
          long_entry_logic.append(
            (_cmp_cached_34) | (_cmp_cached_50) | (_cmp_cached_51)
          )
          # 1d high, 4h & 1d overbought
          long_entry_logic.append(
            (_cmp_cached_84) | (_cmp_cached_123) | (_cmp_cached_99)
          )
          # 1d red, 4h down move, 1h still high
          long_entry_logic.append(
            (_cmp("change_pct_1d", ">", -30.0)) | (_cmp_cached_19) | (_cmp_cached_30)
          )
          # pump, drop but not yet near the previous lows
          long_entry_logic.append(
            _range_lt("high_max_24_4h", "low_min_24_4h", 2.0)
            | _gt_mul("close", "high_max_6_4h", 0.75)
            | (df["close"] < (df["low_min_24_4h"] * 1.25))
          )
          # 4h high, drop but not yet near the previous lows
          long_entry_logic.append(
            (_cmp_cached_13)
            | _gt_mul("close", "high_max_6_4h", 0.80)
            | (df["close"] < (df["low_min_24_4h"] * 1.25))
          )
          # 4h high, drop but not yet near the previous lows
          long_entry_logic.append(
            (_cmp_cached_20)
            | _gt_mul("close", "high_max_6_4h", 0.85)
            | (df["close"] < (df["low_min_24_4h"] * 1.25))
          )
          # 1h down move, drop but not yet near the previous lows
          long_entry_logic.append(
            (_cmp_cached_8)
            | _gt_mul("close", "high_max_12_4h", 0.50)
            | (df["close"] < (df["low_min_24_4h"] * 1.25))
          )
          # 1d overbought, drop but not yet near the previous lows
          long_entry_logic.append(
            (_cmp_cached_35)
            | _gt_mul("close", "high_max_6_1d", 0.70)
            | (df["close"] < (df["low_min_12_1d"] * 1.25))
          )
          # big drop in last 6 hours, 1d overbought
          long_entry_logic.append(_gt_mul("close", "high_max_6_1h", 0.65) | (_cmp_cached_35))
          # big drop in last 4 hours, 4h still not low enough
          long_entry_logic.append(
            _gt_mul("close", "high_max_24_4h", 0.50) | (_cmp_cached_94)
          )
          # big drop in the last 4 days, 4h down move
          long_entry_logic.append(_gt_mul("close", "high_max_24_4h", 0.20) | (_cmp_cached_6))
          # big drop in the last 6 days, 1d down move
          long_entry_logic.append(_gt_mul("close", "high_max_6_1d", 0.30) | (_cmp_cached_59))
          # big drop in the last 12 days, 4h high
          long_entry_logic.append(
            _gt_mul("close", "high_max_12_1d", 0.50) | (_cmp_cached_55)
          )
          # big drop in the last 30 days, 4h down move
          long_entry_logic.append(_gt_mul("close", "high_max_20_1d", 0.10) | (_cmp_cached_19))
          # big drop in the last 20 days, 1h still high
          long_entry_logic.append(_gt_mul("close", "high_max_20_1d", 0.05) | (_cmp_cached_49))
          # big drop in the last 20 days, 1d high, 1d downtrend
          long_entry_logic.append(
            _gt_mul("close", "high_max_20_1d", 0.20)
            | (_cmp_cached_106)
            | (_cmp_cached_141)
          )
          # big drop in the last 30 days, 1h down move
          long_entry_logic.append(_gt_mul("close", "high_max_30_1d", 0.25) | (_cmp_cached_2))

          # Logic
          long_entry_logic.append(_cmp_cached_48)
          long_entry_logic.append(_cmp("RSI_14", "<", 36.0))
          long_entry_logic.append(_cmp("AROONU_14", "<", 25.0))
          long_entry_logic.append(_cmp("STOCHRSIk_14_14_3_3", "<", 20.0))
          long_entry_logic.append(df["close"] < (df["SMA_16"] * 0.946))
          long_entry_logic.append(_cmp_cached_46)

        # Condition #102 - Rapid mode (Long).
        if long_entry_condition_index == 102:
          # Protections
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          long_entry_logic.append(df["protections_long_global"] == True)

          long_entry_logic.append(_cmp("RSI_3", "<", 46.0))
          long_entry_logic.append(_cmp_cached_17)
          long_entry_logic.append(_cmp_cached_1)
          long_entry_logic.append(_cmp_cached_4)
          # 5m & 15m down move, 4h still high
          long_entry_logic.append(
            (_cmp_cached_48) | (_cmp_cached_3) | (_cmp_cached_54)
          )
          # 5m & 15m down move, 15m still high
          long_entry_logic.append((_cmp_cached_48) | (_cmp_cached_16) | (_cmp_cached_81))
          # 5m & 15m down move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_48) | (_cmp_cached_28) | (_cmp_cached_82)
          )
          # 5m & 1h down move, 4h still high
          long_entry_logic.append((_cmp_cached_48) | (_cmp_cached_11) | (_cmp_cached_43))
          # 5m & 4h & 1d down move
          long_entry_logic.append((_cmp_cached_48) | (_cmp_cached_6) | (_cmp_cached_53))
          # 5m & 1d down move, 15m still high
          long_entry_logic.append(
            (_cmp_cached_48) | (_cmp_cached_66) | (_cmp_cached_113)
          )
          # 5m down move, 15m high
          long_entry_logic.append((_cmp_cached_48) | (_cmp_cached_24))
          # 5m down move, 15m & 1h still high
          long_entry_logic.append(
            (_cmp_cached_48) | (_cmp_cached_113) | (_cmp_cached_86)
          )
          # 5m down move, 1h high
          long_entry_logic.append(
            (_cmp_cached_48) | (_cmp_cached_12) | (_cmp_cached_30)
          )
          # 5m & 1h down move, 1h high
          long_entry_logic.append(
            (_cmp_cached_104) | (_cmp_cached_33) | (_cmp_cached_112)
          )
          # 5m & 4h down move, 4h high
          long_entry_logic.append((_cmp_cached_104) | (_cmp_cached_60) | (_cmp_cached_13))
          # 5m down move, 15m still high, 1h high
          long_entry_logic.append((_cmp_cached_104) | (_cmp("RSI_14_15m", "<", 40.0)) | (_cmp_cached_18))
          # 5m down move, 15m still high, 1h high
          long_entry_logic.append(
            (_cmp_cached_104) | (_cmp_cached_81) | (_cmp_cached_30)
          )
          # 5m down move, 15m & 4h high
          long_entry_logic.append(
            (_cmp_cached_104) | (_cmp_cached_108) | (_cmp_cached_55)
          )
          # 5m & 15m down move, 4h high
          long_entry_logic.append((_cmp_cached_143) | (_cmp_cached_16) | (_cmp_cached_32))
          # 5m & 15m down move, 1d high
          long_entry_logic.append(
            (_cmp_cached_143) | (_cmp_cached_16) | (_cmp_cached_84)
          )
          # 5m & 15m down move, 1h high
          long_entry_logic.append(
            (_cmp_cached_143) | (_cmp_cached_28) | (_cmp_cached_83)
          )
          # 5m & 1h down move, 4h still high
          long_entry_logic.append(
            (_cmp_cached_143) | (_cmp_cached_8) | (_cmp_cached_54)
          )
          # 5m down move, 1h & 4h high
          long_entry_logic.append((_cmp_cached_143) | (_cmp_cached_92) | (_cmp_cached_32))
          # 5m down move, 4h high, 1d high
          long_entry_logic.append(
            (_cmp_cached_143) | (_cmp_cached_68) | (_cmp_cached_62)
          )
          # 5m down move, 15m still high, 1h high
          long_entry_logic.append(
            (_cmp("RSI_3", ">", 15.0)) | (_cmp("RSI_14_15m", "<", 40.0)) | (_cmp_cached_83)
          )
          # 5m down move, 15m still high, 4h high
          long_entry_logic.append(
            (_cmp("RSI_3", ">", 15.0)) | (_cmp("RSI_14_15m", "<", 40.0)) | (_cmp_cached_55)
          )
          # 15m down move, 15m still not low enough, 1h high
          long_entry_logic.append(
            (_cmp_cached_7) | (_cmp("AROONU_14_15m", "<", 20.0)) | (_cmp_cached_112)
          )
          # 15m & 1h down move, 1d high
          long_entry_logic.append((_cmp_cached_0) | (_cmp_cached_10) | (_cmp_cached_45))
          # 15m & 1h down move, 1h still not low enough
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp_cached_10) | (_cmp_cached_132)
          )
          # 15m & 1h down move, 1h still not low enough
          long_entry_logic.append((_cmp_cached_0) | (_cmp_cached_11) | (_cmp_cached_138))
          # 15m & 1h down move, 1h still high
          long_entry_logic.append((_cmp_cached_0) | (_cmp_cached_25) | (_cmp_cached_49))
          # 15m & 1h down move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp_cached_25) | (_cmp_cached_30)
          )
          # 15m & 1h down move, 4h still high
          long_entry_logic.append((_cmp_cached_0) | (_cmp_cached_25) | (_cmp_cached_13))
          # 15m & 4h down move, 4h still not low enough
          long_entry_logic.append((_cmp_cached_0) | (_cmp_cached_5) | (_cmp_cached_145))
          # 15m& 4h down move, 15m still high
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp_cached_5) | (_cmp_cached_113)
          )
          # 15m & 4h down move, 15m still high
          long_entry_logic.append((_cmp_cached_0) | (_cmp_cached_6) | (_cmp_cached_46))
          # 15m & 4h down move, 4h still not low enough
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp_cached_6) | (_cmp_cached_94)
          )
          # 15m & 4h down move, 4h still high
          long_entry_logic.append((_cmp_cached_0) | (_cmp_cached_21) | (_cmp_cached_43))
          # 15m & 4h down move, 4h still high
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp_cached_19) | (_cmp_cached_79)
          )
          # 15m & 4h down move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp_cached_6) | (_cmp_cached_82)
          )
          # 15m & 4h down move, 1d high
          long_entry_logic.append((_cmp_cached_0) | (_cmp_cached_21) | (_cmp_cached_103))
          # 15m & 4h down move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp_cached_19) | (_cmp_cached_30)
          )
          # 15m & 4h down move, 4h high
          long_entry_logic.append((_cmp_cached_0) | (_cmp_cached_19) | (_cmp_cached_13))
          # 15m & 1d down move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp_cached_64) | (_cmp_cached_30)
          )
          # 15m down move, 15m still not low enough, 1h high
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp_cached_111) | (_cmp_cached_37)
          )
          # 15m down move, 1h high, 4h overbought
          long_entry_logic.append((_cmp_cached_0) | (_cmp_cached_12) | (_cmp_cached_98))
          # 15m down move, 1d high & overbought
          long_entry_logic.append((_cmp_cached_0) | (_cmp_cached_42) | (_cmp_cached_39))
          # 15m & 1h down move, 1h still high
          long_entry_logic.append((_cmp_cached_0) | (_cmp_cached_8) | (_cmp_cached_86))
          # 15m & 1h down move, 1h still high
          long_entry_logic.append((_cmp_cached_3) | (_cmp_cached_33) | (_cmp_cached_49))
          # 15m & 1h down move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_3) | (_cmp_cached_65) | (_cmp_cached_30)
          )
          # 15m & 1h down move, 4h high
          long_entry_logic.append((_cmp_cached_3) | (_cmp_cached_65) | (_cmp_cached_20))
          # 15m & 1h down move, 15m still not low enough
          long_entry_logic.append(
            (_cmp_cached_3) | (_cmp_cached_65) | (_cmp_cached_75)
          )
          # 15m & 4h & 1d down move
          long_entry_logic.append((_cmp_cached_3) | (_cmp_cached_5) | (_cmp_cached_59))
          # 15m & 4h down move, 4h still high
          long_entry_logic.append((_cmp_cached_3) | (_cmp_cached_6) | (_cmp_cached_43))
          # 15m & 4h down move, 15m still not low enough
          long_entry_logic.append(
            (_cmp_cached_3) | (_cmp_cached_19) | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 25.0))
          )
          # 15m & 4h down move, 4h high
          long_entry_logic.append((_cmp_cached_3) | (_cmp_cached_41) | (_cmp_cached_68))
          # 15m & 4h down move, 4h high
          long_entry_logic.append(
            (_cmp_cached_3) | (_cmp_cached_41) | (_cmp_cached_58)
          )
          # 15m & 4h down move, 4h still high
          long_entry_logic.append(
            (_cmp_cached_3) | (_cmp_cached_76) | (_cmp_cached_54)
          )
          # 15m down move, 15m still not low enough, 4h high
          long_entry_logic.append(
            (_cmp_cached_3) | (_cmp("RSI_14_15m", "<", 35.0)) | (_cmp_cached_55)
          )
          # 15m down move, 15m still not low enough, 4h high
          long_entry_logic.append(
            (_cmp_cached_3) | (_cmp_cached_111) | (_cmp_cached_55)
          )
          # 15m down move, 15m & 4h still high
          long_entry_logic.append(
            (_cmp_cached_3) | (_cmp_cached_46) | (_cmp_cached_43)
          )
          # 15m down move, 15m still high, 1h high
          long_entry_logic.append(
            (_cmp_cached_3) | (_cmp_cached_113) | (_cmp_cached_56)
          )
          # 15m down move, 1h still high, 4h high
          long_entry_logic.append(
            (_cmp_cached_3) | (_cmp_cached_30) | (_cmp_cached_105)
          )
          # 15m down move, 4h still high 1d overbought
          long_entry_logic.append((_cmp_cached_3) | (_cmp_cached_43) | (_cmp_cached_35))
          # 15m & 1h down move, 15m still not low enough
          long_entry_logic.append((_cmp_cached_16) | (_cmp_cached_10) | (_cmp_cached_111))
          # 15m & 1h down move, 4h high
          long_entry_logic.append(
            (_cmp_cached_16) | (_cmp_cached_8) | (_cmp_cached_55)
          )
          # 15m & 1h down move, 15m high
          long_entry_logic.append((_cmp_cached_16) | (_cmp_cached_33) | (_cmp_cached_90))
          # 15m & 4h down move, 1h high
          long_entry_logic.append(
            (_cmp_cached_16) | (_cmp_cached_6) | (_cmp_cached_112)
          )
          # 15m & 4h down move, 4h high
          long_entry_logic.append((_cmp_cached_16) | (_cmp_cached_87) | (_cmp_cached_20))
          # 15m & 1d down move, 4h high
          long_entry_logic.append(
            (_cmp_cached_16) | (_cmp_cached_53) | (_cmp_cached_55)
          )
          # 15m down move, 15m still not low enough, 4h high
          long_entry_logic.append((_cmp_cached_16) | (_cmp("RSI_14_15m", "<", 35.0)) | (_cmp("RSI_14_4h", "<", 85.0)))
          # 15m down move, 15m still not low enough, 1h high
          long_entry_logic.append(
            (_cmp_cached_16) | (_cmp_cached_111) | (_cmp_cached_37)
          )
          # 15m down move, 15m still not low enough, 4h high
          long_entry_logic.append(
            (_cmp_cached_16) | (_cmp_cached_111) | (_cmp_cached_58)
          )
          # 15m down move, 15m still high, 4d downtrend
          long_entry_logic.append((_cmp_cached_16) | (_cmp_cached_81) | (_cmp_cached_31))
          # 15m down move, 15m still not low enough, 1h still high
          long_entry_logic.append(
            (_cmp_cached_16) | (_cmp_cached_125) | (_cmp_cached_49)
          )
          # 15m down move, 15m & 1h still high
          long_entry_logic.append(
            (_cmp_cached_16) | (_cmp_cached_46) | (_cmp_cached_82)
          )
          # 15m down move, 1h & 4h high
          long_entry_logic.append((_cmp_cached_16) | (_cmp_cached_12) | (_cmp_cached_32))
          # 15m & 1h down move, 1h high
          long_entry_logic.append((_cmp_cached_28) | (_cmp_cached_11) | (_cmp_cached_18))
          # 15m & 1h down move, 4h high
          long_entry_logic.append(
            (_cmp_cached_28) | (_cmp_cached_25) | (_cmp_cached_34)
          )
          # 15m & 1h down move, 1d high
          long_entry_logic.append(
            (_cmp_cached_28) | (_cmp_cached_33) | (_cmp_cached_62)
          )
          # 15m & 1h down move, 1h high
          long_entry_logic.append((_cmp_cached_28) | (_cmp_cached_97) | (_cmp_cached_92))
          # 15m & 4h down move, 15m still high
          long_entry_logic.append((_cmp_cached_28) | (_cmp_cached_47) | (_cmp_cached_46))
          # 15m & 1d down move, 4h high
          long_entry_logic.append(
            (_cmp_cached_28) | (_cmp_cached_64) | (_cmp_cached_58)
          )
          # 15m & 1d down move, 1h high
          long_entry_logic.append(
            (_cmp_cached_28) | (_cmp_cached_77) | (_cmp_cached_37)
          )
          # 15m down move, 15m & 1h still high
          long_entry_logic.append(
            (_cmp_cached_28) | (_cmp_cached_46) | (_cmp_cached_30)
          )
          # 15m down move, 15m still high, 4h high
          long_entry_logic.append(
            (_cmp_cached_28) | (_cmp_cached_46) | (_cmp_cached_58)
          )
          # 15m down move, 15m high, 1d overbought
          long_entry_logic.append((_cmp_cached_28) | (_cmp_cached_24) | (_cmp_cached_29))
          # 15m down move, 15m high
          long_entry_logic.append((_cmp_cached_28) | (_cmp("AROONU_14_15m", "<", 85.0)))
          # 15m down move, 1h & 4h high
          long_entry_logic.append((_cmp_cached_28) | (_cmp_cached_18) | (_cmp_cached_32))
          # 15m down move, 1h & 4h high
          long_entry_logic.append(
            (_cmp_cached_28) | (_cmp_cached_56) | (_cmp_cached_32)
          )
          # 15m down move, 4h high, 1d overbought
          long_entry_logic.append((_cmp_cached_28) | (_cmp_cached_20) | (_cmp_cached_35))
          # 15m & 1h down move, 1h high
          long_entry_logic.append((_cmp_cached_70) | (_cmp_cached_65) | (_cmp_cached_88))
          # 15m down move, 15m high, 4h still high
          long_entry_logic.append(
            (_cmp_cached_70) | (_cmp_cached_24) | (_cmp_cached_43)
          )
          # 15m down move, 15m still not low enough, 1h high
          long_entry_logic.append(
            (_cmp_cached_70) | (_cmp_cached_125) | (_cmp_cached_37)
          )
          # 15m down move, 1h still high, 4h high
          long_entry_logic.append((_cmp_cached_70) | (_cmp_cached_49) | (_cmp_cached_32))
          # 15m down move, 15m & 1h high
          long_entry_logic.append(
            (_cmp_cached_100) | (_cmp_cached_24) | (_cmp_cached_56)
          )
          # 15m down move, 15m & 4h high
          long_entry_logic.append(
            (_cmp_cached_100) | (_cmp_cached_24) | (_cmp_cached_55)
          )
          # 15m down move, 15m high
          long_entry_logic.append((_cmp_cached_100) | (_cmp("AROONU_14_15m", "<", 80.0)))
          # 15m down move, 4h still high, 4h overbought
          long_entry_logic.append(
            (_cmp_cached_100) | (_cmp_cached_54) | (_cmp_cached_26)
          )
          # 15m down move, 15m still high, 1h high
          long_entry_logic.append((_cmp_cached_140) | (_cmp("RSI_14_15m", "<", 50.0)) | (_cmp_cached_18))
          # 15m down move, 15m high, 1h high
          long_entry_logic.append(
            (_cmp_cached_140) | (_cmp_cached_24) | (_cmp_cached_52)
          )
          # 15m down move, 15m high
          long_entry_logic.append((_cmp("RSI_3_15m", ">", 45.0)) | (_cmp("AROONU_14_15m", "<", 90.0)))
          # 1h & 4h down move, 4h still high
          long_entry_logic.append((_cmp_cached_2) | (_cmp_cached_6) | (_cmp_cached_110))
          # 1h & 4h down move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_2) | (_cmp_cached_19) | (_cmp_cached_30)
          )
          # 1h & 4h down move, 4h still high
          long_entry_logic.append((_cmp_cached_2) | (_cmp_cached_19) | (_cmp_cached_67))
          # 1h & 1d down move, 4h downtrend
          long_entry_logic.append((_cmp_cached_2) | (_cmp_cached_133) | (_cmp("CMF_20_4h", ">", -0.40)))
          # 1h down move, 1d high & overbought
          long_entry_logic.append(
            (_cmp_cached_10) | (_cmp_cached_62) | (_cmp_cached_51)
          )
          # 1h & 4h down move, 4h still high
          long_entry_logic.append(
            (_cmp_cached_11) | (_cmp_cached_21) | (_cmp_cached_54)
          )
          # 1h & 4h down move, 4h high
          long_entry_logic.append((_cmp_cached_11) | (_cmp_cached_47) | (_cmp_cached_13))
          # 1h down move, 1h still not low enough, 4h high
          long_entry_logic.append(
            (_cmp_cached_11) | (_cmp_cached_109) | (_cmp_cached_58)
          )
          # 1h down move, 1d still high, 1d downtrend
          long_entry_logic.append(
            (_cmp_cached_11) | (_cmp_cached_117) | (_cmp_cached_15)
          )
          # 1h down move, 4h high & overbought
          long_entry_logic.append((_cmp_cached_8) | (_cmp_cached_13) | (_cmp_cached_27))
          # 1h down move, 4h high, 1d downtrend
          long_entry_logic.append((_cmp_cached_8) | (_cmp_cached_13) | (_cmp_cached_95))
          # 1h down move, 4h high, 1d overbought
          long_entry_logic.append((_cmp_cached_8) | (_cmp_cached_13) | (_cmp_cached_40))
          # 1h down move, 4h & 1d overbought
          long_entry_logic.append((_cmp_cached_8) | (_cmp_cached_27) | (_cmp_cached_40))
          # 1h & 4h down move, 4h high
          long_entry_logic.append(
            (_cmp_cached_25) | (_cmp_cached_131) | (_cmp_cached_34)
          )
          # 1h down move, 1h high, 1d overbought
          long_entry_logic.append((_cmp_cached_25) | (_cmp_cached_12) | (_cmp_cached_39))
          # 1h down move, 4h high, 1d overbought
          long_entry_logic.append((_cmp_cached_33) | (_cmp("RSI_14_4h", "<", 75.0)) | (_cmp_cached_29))
          # 1h down move, 1h still high, 1d high
          long_entry_logic.append((_cmp_cached_33) | (_cmp_cached_49) | (_cmp_cached_103))
          # 1h down move, 1h still high, 1d overbought
          long_entry_logic.append((_cmp_cached_33) | (_cmp_cached_49) | (_cmp_cached_39))
          # 1h down move 1h high & overbought
          long_entry_logic.append((_cmp_cached_65) | (_cmp_cached_52) | (_cmp_cached_61))
          # 1h down move, 1h high & overbought
          long_entry_logic.append(
            (_cmp_cached_130) | (_cmp_cached_37) | (_cmp_cached_61)
          )
          # 1h down move, 1d high, 1h overbought
          long_entry_logic.append((_cmp_cached_97) | (_cmp_cached_38) | (_cmp_cached_61))
          # 4h down move, 4h still not low enough, 1d overbought
          long_entry_logic.append((_cmp_cached_5) | (_cmp_cached_145) | (_cmp_cached_29))
          # 4h down move, 15m still high, 1d downtrend
          long_entry_logic.append(
            (_cmp_cached_5) | (_cmp_cached_75) | (_cmp_cached_15)
          )
          # 4h & 1d down move, 15m still not low enough
          long_entry_logic.append(
            (_cmp_cached_6) | (_cmp_cached_53) | (_cmp_cached_125)
          )
          # 4h down move, 4h still not low enough, 1d downtrend
          long_entry_logic.append(
            (_cmp_cached_6) | (_cmp_cached_94) | (_cmp_cached_15)
          )
          # 4h down move, 1d high, 4h downtrend
          long_entry_logic.append(
            (_cmp_cached_19) | (_cmp_cached_62) | (_cmp_cached_31)
          )
          # 4h down move, 4h high, 1d downtrend
          long_entry_logic.append(
            (_cmp_cached_41) | (_cmp_cached_58) | (_cmp_cached_23)
          )
          # 4h & 1d down move, 1d high
          long_entry_logic.append((_cmp_cached_47) | (_cmp("RSI_3_1d", ">", 60.0)) | (_cmp_cached_9))
          # 4h down move, 4h high, 1d downtrend
          long_entry_logic.append(
            (_cmp_cached_87) | (_cmp_cached_34) | (_cmp_cached_15)
          )
          # 4h down move, 15m high, 4h overbought
          long_entry_logic.append(
            (_cmp_cached_87) | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 80.0)) | (_cmp_cached_26)
          )
          # 4h down move, 4h & 1d overbought
          long_entry_logic.append((_cmp_cached_87) | (_cmp_cached_26) | (_cmp_cached_39))
          # 1d down move, 1h high, 1d downtrend
          long_entry_logic.append((_cmp_cached_66) | (_cmp_cached_92) | (_cmp_cached_23))
          # 1d down move, 15m still not low enough, 1h still high
          long_entry_logic.append(
            (_cmp_cached_59) | (_cmp_cached_111) | (_cmp_cached_30)
          )
          # 15m still not low enough, 1h high, 1d overbought
          long_entry_logic.append(
            (_cmp_cached_111) | (_cmp_cached_37) | (_cmp_cached_29)
          )
          # 15m still high, 4h high & overbought
          long_entry_logic.append(
            (_cmp_cached_81) | (_cmp_cached_34) | (_cmp_cached_50)
          )
          # 15m & 1h & 4h high
          long_entry_logic.append(
            (_cmp_cached_24) | (_cmp_cached_18) | (_cmp_cached_32)
          )
          # 15m & 1h high, 4h overbought
          long_entry_logic.append((_cmp_cached_24) | (_cmp_cached_52) | (_cmp_cached_26))
          # 15m & 1d high, 1d overbought
          long_entry_logic.append(
            (_cmp_cached_24) | (_cmp_cached_38) | (_cmp_cached_29)
          )
          # 15m high
          long_entry_logic.append((_cmp("AROONU_14_15m", "<", 80.0)) | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 60.0)))
          # 15m & 4h high
          long_entry_logic.append((_cmp("AROONU_14_15m", "<", 80.0)) | (_cmp_cached_58))
          # 15m high, 1d overbought
          long_entry_logic.append((_cmp("AROONU_14_15m", "<", 80.0)) | (_cmp_cached_35))
          # 15m & 4h high
          long_entry_logic.append((_cmp("AROONU_14_15m", "<", 90.0)) | (_cmp_cached_13))
          # 15m & 1h high
          long_entry_logic.append((_cmp("AROONU_14_15m", "<", 90.0)) | (_cmp_cached_52))
          # 1h still high, 4h high & overbought
          long_entry_logic.append((_cmp_cached_49) | (_cmp_cached_32) | (_cmp_cached_114))
          # 1h & 4h high, 1h overbought
          long_entry_logic.append((_cmp_cached_18) | (_cmp_cached_14) | (_cmp_cached_134))
          # 1h & 1d high, 1d overbought
          long_entry_logic.append((_cmp_cached_18) | (_cmp_cached_9) | (_cmp_cached_51))
          # 1h high, 4h & 1d overbought
          long_entry_logic.append((_cmp_cached_52) | (_cmp_cached_26) | (_cmp_cached_40))
          # 4h & 1d high, 4h overbought
          long_entry_logic.append((_cmp_cached_20) | (_cmp_cached_9) | (_cmp_cached_50))
          # 4h & 1d high, 1d overbought
          long_entry_logic.append((_cmp_cached_13) | (_cmp_cached_9) | (_cmp_cached_78))
          # 4h high & overbought
          long_entry_logic.append(
            (_cmp_cached_32) | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 85.0)) | (_cmp_cached_98)
          )
          # 1d high, 4h & 1d overbought
          long_entry_logic.append((_cmp_cached_9) | (_cmp_cached_27) | (_cmp_cached_35))
          # 1d high, 4h & 1d overbought
          long_entry_logic.append((_cmp_cached_9) | (_cmp_cached_26) | (_cmp_cached_40))
          # 4h high, 4h & 1d overbought
          long_entry_logic.append(
            (_cmp_cached_58) | (_cmp_cached_50) | (_cmp_cached_51)
          )
          # 5m red, 1h still high
          long_entry_logic.append((_cmp("change_pct", ">", -5.0)) | (_cmp_cached_30))
          # 1d top wick, 4h down move, 4h still high
          long_entry_logic.append(
            (_cmp("top_wick_pct_1d", "<", 30.0)) | (_cmp_cached_87) | (_cmp_cached_43)
          )
          # pump, drop but not yet near the previous lows
          long_entry_logic.append(
            _range_lt("high_max_24_4h", "low_min_24_4h", 2.0)
            | _gt_mul("close", "high_max_6_4h", 0.75)
            | (df["close"] < (df["low_min_24_4h"] * 1.25))
          )
          # 4h high, drop but not yet near the previous lows
          long_entry_logic.append(
            (_cmp_cached_55)
            | _gt_mul("close", "close_max_48", 0.85)
            | (df["close"] < (df["low_min_24_1h"] * 1.25))
          )
          # 4h high, drop but not yet near the previous lows
          long_entry_logic.append(
            (_cmp_cached_13)
            | _gt_mul("close", "high_max_6_4h", 0.80)
            | (df["close"] < (df["low_min_24_4h"] * 1.25))
          )
          # 1d overbought, drop but not yet near the previous lows
          long_entry_logic.append(
            (_cmp_cached_35)
            | _gt_mul("close", "high_max_6_1d", 0.70)
            | (df["close"] < (df["low_min_12_1d"] * 1.25))
          )
          # big drop in the last 4 days, 4h down move
          long_entry_logic.append(_gt_mul("close", "high_max_24_4h", 0.20) | (_cmp_cached_6))
          # big drop in the last 12 days, 1h high
          long_entry_logic.append(
            _gt_mul("close", "high_max_12_1d", 0.30) | (_cmp_cached_83)
          )
          # big drop in the last 20 days, 1d down move
          long_entry_logic.append(_gt_mul("close", "high_max_20_1d", 0.40) | (_cmp_cached_77))
          # big drop in the last 30 days, 4h down move, 4h still high
          long_entry_logic.append(
            _gt_mul("close", "high_max_30_1d", 0.25) | (_cmp_cached_76) | (_cmp_cached_110)
          )
          # big drop in the last 30 days, 1h high
          long_entry_logic.append(
            _gt_mul("close", "high_max_30_1d", 0.20) | (_cmp_cached_37)
          )

          # Logic
          long_entry_logic.append(_cmp("WILLR_14", "<", -95.0))
          long_entry_logic.append(_cmp("STOCHRSIk_14_14_3_3", "<", 10.0))
          long_entry_logic.append(df["close"] < (df["BBL_20_2.0"] * 0.999))
          long_entry_logic.append(df["close"] < (df["EMA_20"] * 0.960))

        # Condition #103 - Rapid mode (Long).
        if long_entry_condition_index == 103:
          # Protections
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          long_entry_logic.append(df["protections_long_global"] == True)

          long_entry_logic.append(_cmp("ROC_2", ">", -0.0))
          # 15m down move, 4h high, 1d overbought
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp_cached_58) | (_cmp_cached_69)
          )
          # 15m & 1h & 4h down move
          long_entry_logic.append((_cmp_cached_16) | (_cmp_cached_1) | (_cmp_cached_6))
          # 15m & 4h down move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp_cached_6) | (_cmp_cached_30)
          )
          # 15m & 1h down move, 1h high
          long_entry_logic.append((_cmp_cached_3) | (_cmp_cached_33) | (_cmp_cached_12))
          # 15m down move, 4h high & overbought
          long_entry_logic.append(
            (_cmp_cached_3) | (_cmp_cached_58) | (_cmp_cached_50)
          )
          # 15m & 1h down move, 15m high
          long_entry_logic.append((_cmp_cached_16) | (_cmp_cached_65) | (_cmp_cached_24))
          # 15m & 4h down move, 15m still high
          long_entry_logic.append(
            (_cmp_cached_16) | (_cmp_cached_6) | (_cmp_cached_75)
          )
          # 15m down move, 15m still high, 1h high
          long_entry_logic.append(
            (_cmp_cached_16) | (_cmp("RSI_14_15m", "<", 40.0)) | (_cmp_cached_56)
          )
          # 15m down move, 15m still high, 4h high
          long_entry_logic.append((_cmp_cached_16) | (_cmp("RSI_14_15m", "<", 40.0)) | (_cmp_cached_32))
          # 15m down move, 15m still high, 4h high
          long_entry_logic.append(
            (_cmp_cached_16) | (_cmp_cached_46) | (_cmp_cached_32)
          )
          # 15m down move, 15m & 1h high
          long_entry_logic.append(
            (_cmp_cached_16) | (_cmp_cached_90) | (_cmp_cached_12)
          )
          # 15m down move, 15m high, 4h still high
          long_entry_logic.append(
            (_cmp_cached_16) | (_cmp_cached_24) | (_cmp_cached_43)
          )
          # 15m down move, 15m & 1h still high
          long_entry_logic.append(
            (_cmp_cached_16) | (_cmp_cached_75) | (_cmp_cached_30)
          )
          # 15m down move, 4h overbought
          long_entry_logic.append((_cmp_cached_16) | (_cmp("ROC_9_4h", "<", 70.0)))
          # 15m down move, 15m still high, 1h high
          long_entry_logic.append(
            (_cmp_cached_28) | (_cmp_cached_46) | (_cmp_cached_18)
          )
          # 15m down move, 4h & 1d high
          long_entry_logic.append(
            (_cmp_cached_28) | (_cmp_cached_32) | (_cmp_cached_62)
          )
          # 15m down move, 1h & 1d high
          long_entry_logic.append(
            (_cmp_cached_28) | (_cmp_cached_37) | (_cmp_cached_62)
          )
          # 15m down move, 1h high & overbought
          long_entry_logic.append(
            (_cmp_cached_28) | (_cmp_cached_37) | (_cmp_cached_85)
          )
          # 15m & 1h down move, 15m high
          long_entry_logic.append((_cmp_cached_70) | (_cmp_cached_8) | (_cmp_cached_24))
          # 15m down move, 15m & 1h high
          long_entry_logic.append(
            (_cmp_cached_70) | (_cmp_cached_24) | (_cmp_cached_52)
          )
          # 15m down move, 1h & 4h high
          long_entry_logic.append(
            (_cmp_cached_70) | (_cmp_cached_56) | (_cmp_cached_32)
          )
          # 15m & 1h down move, 1h high
          long_entry_logic.append(
            (_cmp_cached_100) | (_cmp_cached_65) | (_cmp_cached_37)
          )
          # 15m down move, 15m still high, 4h high
          long_entry_logic.append(
            (_cmp_cached_100) | (_cmp_cached_46) | (_cmp_cached_20)
          )
          # 15m down move, 15m & 1h high
          long_entry_logic.append(
            (_cmp_cached_100) | (_cmp_cached_24) | (_cmp_cached_37)
          )
          # 15m down move, 1h high, 4h overbought
          long_entry_logic.append((_cmp_cached_100) | (_cmp_cached_92) | (_cmp_cached_114))
          # 1h & 4h down move, 1h still high
          long_entry_logic.append((_cmp_cached_1) | (_cmp_cached_6) | (_cmp_cached_86))
          # 1h & 4h down move, 15m still not low enough
          long_entry_logic.append(
            (_cmp_cached_1) | (_cmp_cached_6) | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 20.0))
          )
          # 1h down move, 1d high & overbought
          long_entry_logic.append((_cmp_cached_1) | (_cmp_cached_38) | (_cmp_cached_78))
          # 1h & 4h down move, 4h still high
          long_entry_logic.append((_cmp_cached_2) | (_cmp_cached_6) | (_cmp_cached_67))
          # 1h down move, 4h still high, 4h downtrend
          long_entry_logic.append((_cmp_cached_2) | (_cmp_cached_43) | (_cmp_cached_31))
          # 1h down move, 15m still not low enough, 4h high
          long_entry_logic.append((_cmp_cached_10) | (_cmp("AROONU_14_15m", "<", 25.0)) | (_cmp_cached_20))
          # 1h down move, 4h & 1d high
          long_entry_logic.append(
            (_cmp_cached_8) | (_cmp_cached_13) | (_cmp_cached_84)
          )
          # 1h down move, 4h high & overbought
          long_entry_logic.append((_cmp_cached_8) | (_cmp_cached_13) | (_cmp_cached_27))
          # 1h down move, 4h high, 1d overbought
          long_entry_logic.append((_cmp_cached_8) | (_cmp_cached_13) | (_cmp_cached_40))
          # 1h down move, 4h & 1d overbought
          long_entry_logic.append((_cmp_cached_8) | (_cmp_cached_27) | (_cmp_cached_40))
          # 1h down move, 4h & 1d overbought
          long_entry_logic.append((_cmp_cached_8) | (_cmp_cached_50) | (_cmp_cached_40))
          # 1h down move, 15m & 1h still high
          long_entry_logic.append(
            (_cmp_cached_33) | (_cmp_cached_46) | (_cmp_cached_30)
          )
          # 1h down move, 1h still high, 4h high
          long_entry_logic.append((_cmp_cached_33) | (_cmp_cached_49) | (_cmp_cached_32))
          # 1h down move, 1d high & overbought
          long_entry_logic.append((_cmp_cached_65) | (_cmp_cached_9) | (_cmp_cached_51))
          # 1h down move, 15m & 1h still high
          long_entry_logic.append((_cmp_cached_63) | (_cmp_cached_46) | (_cmp_cached_92))
          # 1h & 4h down move, 4h high
          long_entry_logic.append((_cmp_cached_97) | (_cmp_cached_87) | (_cmp_cached_20))
          # 1h & 4h down move, 4h high
          long_entry_logic.append(
            (_cmp_cached_97) | (_cmp_cached_87) | (_cmp_cached_34)
          )
          # 4h down move, 1h & 4h downtrend
          long_entry_logic.append((_cmp_cached_57) | (_cmp_cached_124) | (_cmp_cached_72))
          # 1h down move, 4h high & overbought
          long_entry_logic.append(
            (_cmp_cached_63) | (_cmp_cached_55) | (_cmp_cached_26)
          )
          # 4h down move, 4h still high, 1d downtrend
          long_entry_logic.append((_cmp_cached_6) | (_cmp_cached_43) | (_cmp_cached_44))
          # 1h down move, 15m & 1h still high
          long_entry_logic.append(
            (_cmp_cached_6) | (_cmp_cached_113) | (_cmp_cached_30)
          )
          # 4h down move, 15m still high, 4h high
          long_entry_logic.append(
            (_cmp_cached_21) | (_cmp_cached_75) | (_cmp_cached_13)
          )
          # 4h down move, 15m still not low enough, 4h high
          long_entry_logic.append((_cmp_cached_41) | (_cmp_cached_111) | (_cmp_cached_13))
          # 4h down move, 1h high, 4h downtrend
          long_entry_logic.append((_cmp_cached_19) | (_cmp_cached_12) | (_cmp_cached_102))
          # 4h down move, 4h still high, 1d downtrend
          long_entry_logic.append((_cmp_cached_60) | (_cmp_cached_110) | (_cmp_cached_23))
          # 4h down move, 4h high & overbought
          long_entry_logic.append((_cmp_cached_60) | (_cmp_cached_20) | (_cmp_cached_26))
          # 4h down move, 4h still high, 1d downtrend
          long_entry_logic.append(
            (_cmp_cached_60) | (_cmp_cached_54) | (_cmp_cached_23)
          )
          # 4h down move, 15m still high, 1h high
          long_entry_logic.append((_cmp_cached_87) | (_cmp_cached_46) | (_cmp_cached_52))
          # 4h down move, 1h high, 1d overbought
          long_entry_logic.append(
            (_cmp_cached_87) | (_cmp_cached_83) | (_cmp_cached_51)
          )
          # 1d down move, 1h high, 1d downtrend
          long_entry_logic.append((_cmp_cached_66) | (_cmp_cached_18) | (_cmp_cached_142))
          # 1d down move, 4h high
          long_entry_logic.append((_cmp_cached_66) | (_cmp_cached_34))
          # 1d down move, 15m still high, 1h high
          long_entry_logic.append((_cmp_cached_59) | (_cmp_cached_46) | (_cmp_cached_92))
          # 1d down move, 1h & 1d overbought
          long_entry_logic.append((_cmp_cached_107) | (_cmp("ROC_9_1h", "<", 80.0)) | (_cmp_cached_69))
          # 15m still high, 1h & 4h high
          long_entry_logic.append(
            (_cmp("RSI_14_15m", "<", 40.0)) | (_cmp_cached_18) | (_cmp_cached_32)
          )
          # 15m & 1h still high, 4h high
          long_entry_logic.append(
            (_cmp("RSI_14_15m", "<", 45.0)) | (_cmp_cached_86) | (_cmp_cached_58)
          )
          # 15m still high, 4h high & overbought
          long_entry_logic.append((_cmp("RSI_14_15m", "<", 50.0)) | (_cmp_cached_32) | (_cmp_cached_114))
          # 15m still high, 1h high, 4h still high
          long_entry_logic.append(
            (_cmp_cached_46) | (_cmp_cached_52) | (_cmp_cached_54)
          )
          # 15m still high, 1d high
          long_entry_logic.append((_cmp_cached_46) | (_cmp_cached_62))
          # 15m & 1h
          long_entry_logic.append((_cmp_cached_24) | (_cmp_cached_52))
          # 15m & 1h & 4h high
          long_entry_logic.append(
            (_cmp_cached_24) | (_cmp_cached_56) | (_cmp_cached_32)
          )
          # 1h & 1d high, 4h downtrend
          long_entry_logic.append((_cmp_cached_86) | (_cmp_cached_45) | (_cmp_cached_31))
          # 1h & 4h high, 4h overbought
          long_entry_logic.append((_cmp_cached_12) | (_cmp_cached_32) | (_cmp_cached_27))
          # 1h high, 1h & 1d overbought
          long_entry_logic.append((_cmp_cached_52) | (_cmp_cached_61) | (_cmp_cached_51))
          # 4h & 1d high, 1d overbought
          long_entry_logic.append((_cmp_cached_13) | (_cmp_cached_9) | (_cmp_cached_78))
          # 4h high, 4h & 1d overbought
          long_entry_logic.append((_cmp_cached_20) | (_cmp_cached_114) | (_cmp_cached_29))
          # 1d high, 4h & 1d overbought
          long_entry_logic.append((_cmp_cached_9) | (_cmp_cached_27) | (_cmp_cached_35))
          # 15m still high, 1h high
          long_entry_logic.append(
            (_cmp_cached_113)
            | (_cmp_cached_52)
            | (_cmp_cached_83)
          )
          # 15m still high, 1d high
          long_entry_logic.append((_cmp_cached_75) | (_cmp_cached_62))
          # 4h high, 4h & 1d overbought
          long_entry_logic.append(
            (_cmp_cached_34) | (_cmp_cached_73) | (_cmp_cached_29)
          )
          # 1d green, 4h down move, 4h still high
          long_entry_logic.append((_cmp("change_pct_1d", "<", 40.0)) | (_cmp_cached_41) | (_cmp_cached_67))
          # 1d top wick, 4h high
          long_entry_logic.append((_cmp("top_wick_pct_1d", "<", 30.0)) | (_cmp_cached_32))
          # pump, 4h overbought
          long_entry_logic.append(
            _range_lt("high_max_6_1h", "low_min_6_1h", 0.5) | (_cmp_cached_98)
          )
          # pump, drop but not yet near the previous lows
          long_entry_logic.append(
            _range_lt("high_max_24_4h", "low_min_24_4h", 2.0)
            | _gt_mul("close", "high_max_6_4h", 0.85)
            | (df["close"] < (df["low_min_24_4h"] * 1.25))
          )
          # pump, 1h high
          long_entry_logic.append(
            _range_lt("high_max_24_4h", "low_min_24_4h", 4.0)
            | (_cmp_cached_83)
          )
          # big drop in the last 2 days, 1d down move
          long_entry_logic.append(_gt_mul("close", "high_max_12_4h", 0.30) | (_cmp_cached_77))
          # big drop in the last 12 days, 1h still high
          long_entry_logic.append(_gt_mul("close", "high_max_12_1d", 0.25) | (_cmp_cached_49))
          # big drop in the last 12 days, 1h still not low enough
          long_entry_logic.append(
            _gt_mul("close", "high_max_12_1d", 0.10) | (_cmp_cached_109)
          )
          # big drop in the last 12 days, 15m still high
          long_entry_logic.append(_gt_mul("close", "high_max_12_1d", 0.20) | (_cmp_cached_46))
          # big drop in the last 20 days, 4h down move
          long_entry_logic.append(_gt_mul("close", "high_max_20_1d", 0.10) | (_cmp_cached_6))

          # Logic
          long_entry_logic.append(_cmp("RSI_4", "<", 45.0))
          long_entry_logic.append(_cmp("RSI_14", ">", 35.0))
          long_entry_logic.append(_rsi_20_falling)
          long_entry_logic.append(_cmp("AROONU_14", "<", 25.0))
          long_entry_logic.append(df["close"] < df["SMA_16"] * 0.960)

        # Condition #104 - Rapid mode (Long).
        if long_entry_condition_index == 104:
          # Protections
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          long_entry_logic.append(df["protections_long_global"] == True)

          # 5m & 4h & 1d down move
          long_entry_logic.append((_cmp_cached_48) | (_cmp_cached_6) | (_cmp_cached_53))
          # 5m & 4h down move, 1d downtrend
          long_entry_logic.append((_cmp_cached_104) | (_cmp_cached_4) | (_cmp_cached_15))
          # 5m & 1h down move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_104) | (_cmp_cached_8) | (_cmp_cached_30)
          )
          # 15m & 4h & 1d down move
          long_entry_logic.append((_cmp_cached_7) | (_cmp_cached_4) | (_cmp_cached_59))
          # 15m & 1h down move
          long_entry_logic.append((_cmp_cached_7) | (_cmp_cached_36))
          # 15m & 1h down move, 4h still not low enough
          long_entry_logic.append((_cmp_cached_7) | (_cmp_cached_22) | (_cmp("RSI_14_4h", "<", 35.0)))
          # 15m & 1h down move, 1d still high
          long_entry_logic.append((_cmp_cached_7) | (_cmp_cached_1) | (_cmp_cached_121))
          # 15m & 1h down move, 1h still not low enough
          long_entry_logic.append(
            (_cmp_cached_7) | (_cmp_cached_2) | (_cmp_cached_109)
          )
          # 15m & 4h down move, 4h still high
          long_entry_logic.append((_cmp_cached_7) | (_cmp_cached_19) | (_cmp_cached_110))
          # 15m & 1h & 4h down move
          long_entry_logic.append((_cmp_cached_17) | (_cmp_cached_2) | (_cmp_cached_5))
          # 15m & 1h & 4h down move, 15m downtrend
          long_entry_logic.append(
            (_cmp_cached_17) | (_cmp_cached_10) | (_cmp_cached_6) | (_cmp("CMF_20_15m", ">", -0.20))
          )
          # 15m & 1h down move, 4h still not low enough
          long_entry_logic.append((_cmp_cached_17) | (_cmp_cached_10) | (_cmp("AROONU_14_4h", "<", 20.0)))
          # 15m & 1h down move, 1h high
          long_entry_logic.append(
            (_cmp_cached_17) | (_cmp_cached_8) | (_cmp_cached_30)
          )
          # 15m & 4h down move, 4h still high
          long_entry_logic.append((_cmp_cached_17) | (_cmp_cached_5) | (_cmp_cached_43))
          # 15m & 1h down move, 15m & 1h downtrend
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp_cached_1) | (_cmp("CMF_20_15m", ">", -0.40)) | (_cmp("CMF_20_1h", ">", -0.40))
          )
          # 15m & 1h down move, 1h still not low enough
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp_cached_1) | (_cmp_cached_132)
          )
          # 15m & 1h down move, 4h still high
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp_cached_10) | (_cmp_cached_54)
          )
          # 15m & 1h down move, 4h overbought
          long_entry_logic.append((_cmp_cached_0) | (_cmp_cached_33) | (_cmp_cached_98))
          # 15m & 1h down move, 1h high
          long_entry_logic.append((_cmp_cached_0) | (_cmp_cached_11) | (_cmp_cached_18))
          # 15m & 4h down move, 1h & 4h downtrend
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp_cached_4) | (_cmp("CMF_20_1h", ">", -0.20)) | (_cmp("CMF_20_4h", ">", -0.20))
          )
          # 15m & 4h down move, 4h still not low enough
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp_cached_4) | (_cmp_cached_94)
          )
          # 15m & 4h down move, 4h still high
          long_entry_logic.append((_cmp_cached_0) | (_cmp_cached_4) | (_cmp_cached_67))
          # 15m & 4h down move, 1d high
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp_cached_5) | (_cmp_cached_62)
          )
          # 15m & 4h down move, 1h high
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp_cached_6) | (_cmp_cached_56)
          )
          # 15m & 4h down move, 4h still high
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp_cached_6) | (_cmp_cached_79)
          )
          # 15m & 4h down move, 1d downtrend
          long_entry_logic.append((_cmp_cached_0) | (_cmp_cached_6) | (_cmp_cached_149))
          # 15m & 4h down move, 15m still not low enough
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp_cached_21) | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 20.0))
          )
          # 15m & 4h down move, 4h high
          long_entry_logic.append((_cmp_cached_0) | (_cmp_cached_47) | (_cmp_cached_20))
          # 15m & 1h down move, 4h still high
          long_entry_logic.append((_cmp_cached_3) | (_cmp_cached_10) | (_cmp_cached_67))
          # 15m & 1h down move, 4h high
          long_entry_logic.append((_cmp_cached_3) | (_cmp_cached_11) | (_cmp_cached_13))
          # 15m & 1h down move, 1h high
          long_entry_logic.append(
            (_cmp_cached_3) | (_cmp_cached_11) | (_cmp_cached_112)
          )
          # 15m & 1h down move, 1h still high
          long_entry_logic.append((_cmp_cached_3) | (_cmp_cached_8) | (_cmp_cached_86))
          # 15m down move, 4h still high, 4h downtrend
          long_entry_logic.append((_cmp_cached_3) | (_cmp_cached_67) | (_cmp_cached_31))
          # 15m down move, 1d high, 4h overbought
          long_entry_logic.append((_cmp_cached_3) | (_cmp_cached_9) | (_cmp_cached_98))
          # 15m & 3h down move, 15m still not low enough
          long_entry_logic.append(
            (_cmp_cached_16) | (_cmp_cached_6) | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 20.0))
          )
          # 15m & 1h down move, 1h still high
          long_entry_logic.append((_cmp_cached_28) | (_cmp_cached_11) | (_cmp("RSI_14_1h", "<", 40.0)))
          # 15m & 4h down move, 4h high
          long_entry_logic.append((_cmp_cached_28) | (_cmp_cached_21) | (_cmp_cached_13))
          # 15m down move, 15m still not low enough, 1d overbought
          long_entry_logic.append(
            (_cmp_cached_28) | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 20.0)) | (_cmp_cached_69)
          )
          # 1h & 4h down move
          long_entry_logic.append((_cmp_cached_36) | (_cmp_cached_4))
          # 1h & 4h down move, 4h still not low enough
          long_entry_logic.append(
            (_cmp_cached_36) | (_cmp_cached_21) | (_cmp_cached_94)
          )
          # 1h & 4h down move, 4h high
          long_entry_logic.append((_cmp_cached_36) | (_cmp_cached_60) | (_cmp_cached_13))
          # 1h & 4h down move
          long_entry_logic.append((_cmp_cached_22) | (_cmp_cached_57))
          # 1h & 4h down move, 4h still high
          long_entry_logic.append((_cmp_cached_22) | (_cmp_cached_19) | (_cmp_cached_43))
          # 1h down move, 1h still high
          long_entry_logic.append((_cmp_cached_22) | (_cmp_cached_49))
          # 1h down move, 4h high
          long_entry_logic.append((_cmp_cached_22) | (_cmp_cached_93))
          # 1h & 4h down move
          long_entry_logic.append((_cmp_cached_1) | (_cmp_cached_4))
          # 1h & 4h down move, 4h still not low enough
          long_entry_logic.append(
            (_cmp_cached_1) | (_cmp_cached_5) | (_cmp_cached_94)
          )
          # 1h & 4h down move, 1d still high
          long_entry_logic.append(
            (_cmp_cached_1) | (_cmp_cached_5) | (_cmp_cached_117)
          )
          # 1h & 1d down move, 1h still moving lower
          long_entry_logic.append(
            (_cmp_cached_1) | (_cmp_cached_59) | (_cmp("CCI_20_change_pct_1h", ">", -0.0))
          )
          # 1h down move, 1d high, 4h downtrend
          long_entry_logic.append((_cmp_cached_1) | (_cmp_cached_103) | (_cmp_cached_102))
          # 1h & 4h down move, 1h still high
          long_entry_logic.append((_cmp_cached_2) | (_cmp_cached_5) | (_cmp_cached_49))
          # 1h & 4h & 1d down move
          long_entry_logic.append((_cmp_cached_2) | (_cmp_cached_6) | (_cmp_cached_77))
          # 1h & 4h down move, 1h still not low enough
          long_entry_logic.append(
            (_cmp_cached_2) | (_cmp_cached_6) | (_cmp_cached_132)
          )
          # 1h & 4h down move, 4h still not low enough
          long_entry_logic.append(
            (_cmp_cached_2) | (_cmp_cached_6) | (_cmp_cached_94)
          )
          # 1h & 4h & 1d down move
          long_entry_logic.append((_cmp_cached_2) | (_cmp_cached_21) | (_cmp_cached_64))
          # 1h & 4h down move, 1h high
          long_entry_logic.append((_cmp_cached_2) | (_cmp_cached_47) | (_cmp_cached_18))
          # 1h & 1d down move, 1d high
          long_entry_logic.append((_cmp_cached_2) | (_cmp_cached_64) | (_cmp_cached_45))
          # 1h & 1d down move, 1d high
          long_entry_logic.append(
            (_cmp_cached_2) | (_cmp_cached_64) | (_cmp_cached_106)
          )
          # 1h down move, 1h & 4h high
          long_entry_logic.append((_cmp_cached_2) | (_cmp_cached_88) | (_cmp_cached_68))
          # 1h & 4h down move, 1d overbought
          long_entry_logic.append((_cmp_cached_10) | (_cmp_cached_6) | (_cmp_cached_35))
          # 1h & 4h down move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_10) | (_cmp_cached_21) | (_cmp_cached_30)
          )
          # 1h & 1d down move, 1d high
          long_entry_logic.append((_cmp_cached_10) | (_cmp_cached_53) | (_cmp_cached_45))
          # 4h & 1d down move, 1d high
          long_entry_logic.append((_cmp_cached_10) | (_cmp_cached_118) | (_cmp_cached_42))
          # 1h down move, 1h still high, 4h high
          long_entry_logic.append((_cmp_cached_10) | (_cmp_cached_49) | (_cmp_cached_13))
          # 1h down move, 4h high
          long_entry_logic.append((_cmp_cached_10) | (_cmp_cached_55))
          # 1h down move, 1h & 1d high
          long_entry_logic.append((_cmp_cached_11) | (_cmp_cached_12) | (_cmp_cached_38))
          # 1h down move, 4h still high, 1d downtrend
          long_entry_logic.append((_cmp_cached_11) | (_cmp_cached_67) | (_cmp_cached_15))
          # 1h down move, 1h still high, 1d overbought
          long_entry_logic.append(
            (_cmp_cached_11) | (_cmp_cached_30) | (_cmp_cached_40)
          )
          # 1h & 4h down move, 4h high
          long_entry_logic.append((_cmp_cached_8) | (_cmp_cached_76) | (_cmp_cached_20))
          # 1h & dh down move, 4h high
          long_entry_logic.append((_cmp_cached_8) | (_cmp_cached_60) | (_cmp_cached_93))
          # 1h down move, 4h still not low enough, 1d overbought
          long_entry_logic.append((_cmp_cached_8) | (_cmp_cached_145) | (_cmp_cached_35))
          # 1h down move, 1h still not low enough, 4h downtrend
          long_entry_logic.append(
            (_cmp_cached_25) | (_cmp_cached_109) | (_cmp_cached_31)
          )
          # 1h down move, 4h still high, 1d downtrend
          long_entry_logic.append(
            (_cmp_cached_25) | (_cmp_cached_54) | (_cmp_cached_15)
          )
          # 1h down move, 4h & 1d overbought
          long_entry_logic.append((_cmp_cached_33) | (_cmp_cached_27) | (_cmp_cached_35))
          # 1h down move, 4h high & overbought
          long_entry_logic.append((_cmp_cached_63) | (_cmp_cached_32) | (_cmp_cached_26))
          # 1h down move, 4h high & overbought
          long_entry_logic.append(
            (_cmp_cached_63) | (_cmp_cached_34) | (_cmp_cached_26)
          )
          # 4h down move, 15m not low enough, 1h still high
          long_entry_logic.append(
            (_cmp_cached_80) | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 20.0)) | (_cmp_cached_82)
          )
          # 4h & 1d down move, 4h downtrend
          long_entry_logic.append((_cmp_cached_57) | (_cmp_cached_53) | (_cmp_cached_31))
          # 4h & 1d down move, 1d high
          long_entry_logic.append((_cmp_cached_57) | (_cmp_cached_77) | (_cmp_cached_45))
          # 4h down move, 4h still high, 1d downtrend
          long_entry_logic.append(
            (_cmp_cached_57) | (_cmp_cached_79) | (_cmp_cached_15)
          )
          # 4h down move, 1d still not low enough, 1d downtrend
          long_entry_logic.append(
            (_cmp_cached_57) | (_cmp("STOCHRSIk_14_14_3_3_1d", "<", 30.0)) | (_cmp_cached_15)
          )
          # 4h down move, 1h downtrend, 1h still not low enough
          long_entry_logic.append((_cmp_cached_4) | (_cmp("CMF_20_1h", ">", -0.25)) | (_cmp_cached_138))
          # 4h down move, 1h & 1d downtrend
          long_entry_logic.append((_cmp_cached_4) | (_cmp_cached_120) | (_cmp_cached_15))
          # 4h & 1d down move, 4h still high
          long_entry_logic.append(
            (_cmp_cached_5) | (_cmp_cached_107) | (_cmp_cached_79)
          )
          # 4h & 1d down move, 1d high
          long_entry_logic.append(
            (_cmp_cached_6) | (_cmp_cached_64) | (_cmp("STOCHRSIk_14_14_3_3_1d", "<", 60.0))
          )
          # 4h down move, 1d high & overbought
          long_entry_logic.append((_cmp_cached_6) | (_cmp_cached_45) | (_cmp_cached_35))
          # 4h down move, 1h still high, 1d downtrend
          long_entry_logic.append(
            (_cmp_cached_6) | (_cmp_cached_30) | (_cmp_cached_15)
          )
          # 4h down move, 1h high
          long_entry_logic.append((_cmp_cached_6) | (_cmp_cached_37))
          # 4h down move, 1d high, 1h downtrend
          long_entry_logic.append(
            (_cmp_cached_6) | (_cmp_cached_106) | (_cmp("ROC_9_1h", ">", -10.0))
          )
          # 4h down move, 4h still high, 1d overbought
          long_entry_logic.append((_cmp_cached_19) | (_cmp_cached_67) | (_cmp_cached_29))
          # 4h down move, 4h still high, 1d overbought
          long_entry_logic.append((_cmp_cached_41) | (_cmp_cached_43) | (_cmp_cached_40))
          # 4h down move, 4h still high, 1d high
          long_entry_logic.append((_cmp_cached_47) | (_cmp_cached_43) | (_cmp_cached_9))
          # 4h down move, 4h & 1d overbought
          long_entry_logic.append((_cmp_cached_47) | (_cmp_cached_27) | (_cmp_cached_35))
          # 1d down move, 1h still not low enough
          long_entry_logic.append((_cmp("RSI_3_1d", ">", 5.0)) | (_cmp_cached_132))
          # 1h & 4h high, 4h overbought
          long_entry_logic.append((_cmp_cached_88) | (_cmp_cached_14) | (_cmp_cached_50))
          # 4h & 1d high, 4h overbought
          long_entry_logic.append((_cmp_cached_68) | (_cmp_cached_9) | (_cmp_cached_73))
          # 1d red, 4h down move, 1h still high
          long_entry_logic.append(
            (_cmp("change_pct_1d", ">", -30.0)) | (_cmp_cached_19) | (_cmp_cached_30)
          )
          # pump, drop but not yet near the previous lows
          long_entry_logic.append(
            _range_lt("high_max_24_4h", "low_min_24_4h", 2.0)
            | _gt_mul("close", "high_max_12_4h", 0.60)
            | (df["close"] < (df["low_min_24_4h"] * 1.10))
          )
          # pump, drop but not yet near the previous lows
          long_entry_logic.append(
            _range_lt("high_max_12_1d", "low_min_12_1d", 5.0)
            | _gt_mul("close", "high_max_6_1d", 0.30)
            | (df["close"] < (df["low_min_12_1d"] * 1.25))
          )
          # big drop in the last hour
          long_entry_logic.append(_gt_mul("close", "close_max_12", 0.50))
          # big drop in the last 12 days, 15m & 4h down move
          long_entry_logic.append(
            _gt_mul("close", "high_max_12_1d", 0.40) | (_cmp_cached_0) | (_cmp_cached_4)
          )
          # big drop in the last 20 days, 15m & 1h down move
          long_entry_logic.append(
            _gt_mul("close", "high_max_20_1d", 0.40) | (_cmp("RSI_14_15m", "<", 10.0)) | (_cmp("RSI_14_1h", "<", 10.0))
          )
          # big drop in the last 20 days, 1d down move
          long_entry_logic.append(_gt_mul("close", "high_max_20_1d", 0.25) | (_cmp_cached_77))
          # big drop in the last 20 days, 4h still not low enough
          long_entry_logic.append(_gt_mul("close", "high_max_20_1d", 0.10) | (_cmp("RSI_14_4h", "<", 30.0)))
          # big drop in the last 30 days, 4h down move
          long_entry_logic.append(_gt_mul("close", "high_max_30_1d", 0.25) | (_cmp_cached_6))

          # Logic
          long_entry_logic.append(_cmp("RSI_3", "<", 40.0))
          long_entry_logic.append(_cmp("AROONU_14", "<", 25.0))
          long_entry_logic.append(_cmp("STOCHRSIk_14_14_3_3", "<", 20.0))
          long_entry_logic.append(_cmp("AROONU_14_15m", "<", 25.0))
          long_entry_logic.append(_cmp_cached_125)
          long_entry_logic.append(df["close"] < df["EMA_16"] * 0.975)
          long_entry_logic.append(((df["EMA_50"] - df["EMA_200"]) / df["close"] * 100.0) < -5.5)

        # Condition #120 - Grind mode (Long).
        if long_entry_condition_index == 120:
          # Protections
          long_entry_logic.append(num_open_long_grind_mode < self.grind_mode_max_slots)
          long_entry_logic.append(df["protections_long_global"] == True)
          long_entry_logic.append(is_pair_long_grind_mode)
          long_entry_logic.append(_cmp("RSI_3", "<=", 50.0))
          long_entry_logic.append(_cmp("RSI_3_15m", ">=", 20.0))
          long_entry_logic.append(_cmp("RSI_3_1h", ">=", 10.0))
          long_entry_logic.append(_cmp("RSI_3_4h", ">=", 10.0))
          long_entry_logic.append(_cmp("RSI_14_1h", "<", 80.0))
          long_entry_logic.append(_cmp("RSI_14_4h", "<", 80.0))
          long_entry_logic.append(_cmp("RSI_14_1d", "<", 80.0))
          long_entry_logic.append(_cmp_cached_24)
          long_entry_logic.append(_cmp_cached_71)
          long_entry_logic.append(_cmp_cached_14)
          long_entry_logic.append(_cmp_cached_9)
          long_entry_logic.append(_cmp_cached_62)

          # Logic
          long_entry_logic.append(
            (_cmp("STOCHRSIk_14_14_3_3", "<", 20.0))
            & (_cmp("WILLR_14", "<", -80.0))
            & (_cmp("AROONU_14", "<", 25.0))
            & (df["close"] < (df["EMA_20"] * 0.978))
          )

        # Condition #141 - Top Coins mode (Long).
        if long_entry_condition_index == 141:
          # Protections
          long_entry_logic.append(is_pair_long_top_coins_mode)
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          long_entry_logic.append(df["protections_long_global"] == True)

          long_entry_logic.append(
            # 5m & 15m down move, 15m high
            ((_cmp_cached_48) | (_cmp_cached_3) | (_cmp_cached_24))
            # 5m & 15m down move, 4h still high
            & ((_cmp_cached_48) | (_cmp_cached_3) | (_cmp_cached_54))
            # 5m & 15m down move, 15m high
            & ((_cmp_cached_48) | (_cmp_cached_16) | (_cmp_cached_24))
            # 5m & 1h down move, 15m still high
            & ((_cmp_cached_48) | (_cmp_cached_2) | (_cmp_cached_81))
            # 5m & 1h down move, 1h high
            & ((_cmp_cached_48) | (_cmp_cached_65) | (_cmp_cached_37))
            # 5m & 4h down move, 15m still high
            & ((_cmp_cached_48) | (_cmp_cached_57) | (_cmp_cached_81))
            # 5m & 4h down move, 15m still high
            & ((_cmp_cached_48) | (_cmp_cached_57) | (_cmp_cached_113))
            # 5m & 4h down move, 15m still high
            & ((_cmp_cached_48) | (_cmp_cached_6) | (_cmp_cached_75))
            # 5m & 4h down move, 1h high
            & ((_cmp_cached_48) | (_cmp_cached_76) | (_cmp_cached_37))
            # 5m & 1d down move, 15m high
            & ((_cmp_cached_48) | (_cmp_cached_66) | (_cmp_cached_24))
            # 5m & 1d down move, 15m stil high
            & ((_cmp_cached_48) | (_cmp_cached_66) | (_cmp_cached_113))
            # 5m & 1d down move, 4h still high
            & ((_cmp_cached_48) | (_cmp_cached_66) | (_cmp_cached_79))
            # 5m down move, 1h high
            & ((_cmp_cached_48) | (_cmp_cached_83))
            # 5m down move, 15m & 1d high
            & ((_cmp_cached_104) | (_cmp_cached_90) | (_cmp_cached_9))
            # 5m down move, 1h & 1d high
            & ((_cmp_cached_143) | (_cmp_cached_18) | (_cmp_cached_9))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_7) | (_cmp_cached_1) | (_cmp_cached_29))
            # 15m & 1h down move, 1h still not low enough
            & ((_cmp_cached_7) | (_cmp_cached_1) | (_cmp_cached_132))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_7) | (_cmp_cached_1) | (_cmp_cached_99))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_7) | (_cmp_cached_2) | (_cmp_cached_67))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_7) | (_cmp_cached_2) | (_cmp_cached_55))
            # 15m & 1h down move, 1d still high
            & ((_cmp_cached_7) | (_cmp_cached_10) | (_cmp_cached_117))
            # 15m & 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_7) | (_cmp_cached_11) | (_cmp_cached_110) | (_cmp_cached_142))
            # 15m & 1h down move, 15m still high
            & ((_cmp_cached_7) | (_cmp_cached_8) | (_cmp_cached_46))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_7) | (_cmp_cached_8) | (_cmp_cached_42))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_7) | (_cmp_cached_33) | (_cmp_cached_92))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_7) | (_cmp_cached_33) | (_cmp_cached_37))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_7) | (_cmp_cached_65) | (_cmp_cached_37))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_7) | (_cmp_cached_65) | (_cmp_cached_84))
            # 15m & 4h down move, 15m downtrend
            & ((_cmp_cached_7) | (_cmp_cached_80) | (_cmp("CMF_20_15m", ">", -0.30)))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_7) | (_cmp_cached_21) | (_cmp_cached_67))
            # 15m down move, 1h high, 4h overbought
            & ((_cmp_cached_7) | (_cmp_cached_12) | (_cmp_cached_27))
            # 15m down move, 1d high & overbought
            & ((_cmp_cached_7) | (_cmp_cached_45) | (_cmp_cached_78))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_17) | (_cmp_cached_1) | (_cmp_cached_54))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_17) | (_cmp_cached_11) | (_cmp_cached_30))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_17) | (_cmp_cached_8) | (_cmp_cached_37))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_17) | (_cmp_cached_5) | (_cmp_cached_45))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_17) | (_cmp_cached_6) | (_cmp_cached_42))
            # 15m & 1d down move, 1d still high
            & ((_cmp_cached_17) | (_cmp_cached_66) | (_cmp_cached_135))
            # 15m down move, 15m downtrend, 1d high
            & ((_cmp_cached_17) | (_cmp("CMF_20_15m", ">", -0.40)) | (_cmp_cached_9))
            # 15m down move, 4h high, 1h overbought
            & ((_cmp_cached_17) | (_cmp_cached_14) | (_cmp_cached_61))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_1) | (_cmp_cached_93))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_0) | (_cmp_cached_1) | (_cmp_cached_103))
            # 15m & 1h down move, 15m still high
            & ((_cmp_cached_0) | (_cmp_cached_2) | (_cmp_cached_75))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_0) | (_cmp_cached_2) | (_cmp_cached_30))
            # 15m & 1h down move, 1d still high
            & ((_cmp_cached_0) | (_cmp_cached_2) | (_cmp_cached_117))
            # 15m & 1h down move, 15m high
            & ((_cmp_cached_0) | (_cmp_cached_10) | (_cmp_cached_90))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_0) | (_cmp_cached_10) | (_cmp_cached_18))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_0) | (_cmp_cached_8) | (_cmp_cached_56))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_8) | (_cmp_cached_99))
            # 15m & 4h down move, 15m still high
            & ((_cmp_cached_0) | (_cmp_cached_4) | (_cmp_cached_81))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_0) | (_cmp_cached_4) | (_cmp_cached_42))
            # 15m & 4h down move, 1d downtrend
            & ((_cmp_cached_0) | (_cmp_cached_4) | (_cmp_cached_15))
            # 15m & 4h down move, 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_5) | (_cmp_cached_39))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_0) | (_cmp_cached_6) | (_cmp("RSI_14_1d", "<", 70.0)))
            # 15m & 4h down move, 15m high
            & ((_cmp_cached_0) | (_cmp_cached_6) | (_cmp_cached_90))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_0) | (_cmp_cached_6) | (_cmp_cached_43))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_0) | (_cmp_cached_6) | (_cmp_cached_42))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_0) | (_cmp_cached_6) | (_cmp_cached_56))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_0) | (_cmp_cached_6) | (_cmp_cached_84))
            # 15m & 4h down move, 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_6) | (_cmp_cached_35))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_0) | (_cmp_cached_19) | (_cmp_cached_51))
            # 15m & 4h down move, 15m high
            & ((_cmp_cached_0) | (_cmp_cached_47) | (_cmp_cached_24))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_76) | (_cmp_cached_13))
            # 15m down move, 1h high
            & ((_cmp_cached_0) | (_cmp_cached_83))
            # 15m & 1d down move, 1h still high
            & ((_cmp_cached_0) | (_cmp_cached_66) | (_cmp_cached_30))
            # 15m & 1d down move, 1d high
            & ((_cmp_cached_0) | (_cmp_cached_77) | (_cmp("STOCHRSIk_14_14_3_3_1d", "<", 60.0)))
            # 15m down move, 15m & 1h high
            & ((_cmp_cached_0) | (_cmp_cached_90) | (_cmp_cached_71))
            # 15m down move, 15m & 4h high
            & ((_cmp_cached_0) | (_cmp_cached_90) | (_cmp_cached_13))
            # 15m down move, 15m high, 1h high
            & ((_cmp_cached_0) | (_cmp_cached_24) | (_cmp_cached_37))
            # 15m down move, 4h high, 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_13) | (_cmp_cached_29))
            # 15m down move, 1d high & overbought
            & ((_cmp_cached_0) | (_cmp_cached_103) | (_cmp_cached_39))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_30) | (_cmp_cached_40))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_2) | (_cmp_cached_12))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_2) | (_cmp_cached_20))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_33) | (_cmp_cached_52))
            # 15m & 4h down move, 15m high
            & ((_cmp_cached_3) | (_cmp_cached_5) | (_cmp_cached_46))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_5) | (_cmp_cached_56))
            # 15m & 4h down move, 15m high
            & ((_cmp_cached_3) | (_cmp_cached_6) | (_cmp_cached_24))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_21) | (_cmp_cached_68))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_3) | (_cmp_cached_21) | (_cmp_cached_79))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_41) | (_cmp_cached_52))
            # 15m & 1d down move, 1h still high
            & ((_cmp_cached_3) | (_cmp_cached_59) | (_cmp_cached_109))
            # 15m down move, 15m downtrend, 1h high
            & ((_cmp_cached_3) | (_cmp("CMF_20_15m", ">", -0.40)) | (_cmp_cached_88))
            # 15m down move, 15m still high, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_46) | (_cmp_cached_34))
            # 15m down move, 15m high, 1d overbought
            & ((_cmp_cached_3) | (_cmp_cached_24) | (_cmp_cached_39))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_3) | (_cmp_cached_71) | (_cmp_cached_14))
            # 15m down move, 4h & 1d overbought
            & ((_cmp_cached_3) | (_cmp_cached_26) | (_cmp_cached_69))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_16) | (_cmp_cached_18) | (_cmp_cached_78))
            # 15m down move, 1h high, 1d downtrend
            & ((_cmp_cached_16) | (_cmp_cached_37) | (_cmp_cached_15))
            # 15m down move, 4h high, 1d downtrend
            & ((_cmp_cached_16) | (_cmp_cached_34) | (_cmp_cached_23))
            # 15m & 4h down move, 15m high
            & ((_cmp_cached_28) | (_cmp_cached_19) | (_cmp_cached_108))
            # 15m down move, 15m & 1h high
            & ((_cmp_cached_28) | (_cmp_cached_24) | (_cmp_cached_71))
            # 15m & 4h down mve, 1h high
            & ((_cmp_cached_70) | (_cmp_cached_19) | (_cmp_cached_37))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_70) | (_cmp_cached_76) | (_cmp_cached_34))
            # 15m down move, 15m & 1h high
            & ((_cmp_cached_70) | (_cmp_cached_24) | (_cmp_cached_52))
            # 15m down move, 1h high, 1d downtrend
            & ((_cmp_cached_70) | (_cmp_cached_52) | (_cmp_cached_142))
            # 15m down move, 15m high, 4h high
            & ((_cmp_cached_100) | (_cmp_cached_24) | (_cmp_cached_34))
            # 15m down move, 15m & 4h high
            & ((_cmp_cached_100) | (_cmp_cached_24) | (_cmp_cached_32))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_36) | (_cmp_cached_4) | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 10.0)))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_36) | (_cmp_cached_21) | (_cmp_cached_78))
            # 1h & 1d down move, 1d still high
            & ((_cmp_cached_36) | (_cmp_cached_64) | (_cmp("STOCHRSIk_14_14_3_3_1d", "<", 40.0)))
            # 1h & 4h down move, 15m still not low enough
            & ((_cmp_cached_22) | (_cmp_cached_57) | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 20.0)))
            # 1h & 4h down move, 4h downtrend
            & ((_cmp_cached_22) | (_cmp_cached_4) | (_cmp_cached_102))
            # 1h & 4h down move, 15m high
            & ((_cmp_cached_22) | (_cmp_cached_21) | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 60.0)))
            # 1h & 4h down move, 1d still high
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp_cached_121))
            # 1h & 4h down move, 15m still high
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp_cached_108))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_1) | (_cmp_cached_5) | (_cmp_cached_145))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_1) | (_cmp_cached_6) | (_cmp_cached_67))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_1) | (_cmp_cached_21) | (_cmp_cached_105))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_1) | (_cmp_cached_47) | (_cmp_cached_13))
            # 1h & 1d down move, 1h still not low enough
            & ((_cmp_cached_1) | (_cmp_cached_59) | (_cmp("AROONU_14_1h", "<", 20.0)))
            # 1h & 1d down move, 1h still not low enough
            & ((_cmp_cached_1) | (_cmp_cached_53) | (_cmp_cached_138))
            # 1h down move, 15m downtrend, 1d high
            & ((_cmp_cached_1) | (_cmp("CMF_20_15m", ">", -0.40)) | (_cmp_cached_45))
            # 1h down move, 1h high, 4h high
            & ((_cmp_cached_1) | (_cmp_cached_12) | (_cmp_cached_34))
            # 1h & 4h down move, 1h still high
            & ((_cmp_cached_2) | (_cmp_cached_5) | (_cmp_cached_86))
            # 1h & 4h down move, 1h still high
            & ((_cmp_cached_2) | (_cmp_cached_5) | (_cmp_cached_30))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_2) | (_cmp_cached_5) | (_cmp_cached_23))
            # 1h & 1d down move, 4h downtrend
            & ((_cmp_cached_2) | (_cmp_cached_59) | (_cmp_cached_72))
            # 1h & 1d down move, 1d still high
            & ((_cmp_cached_2) | (_cmp_cached_64) | (_cmp_cached_121))
            # 1h & 1d down move, 1d high
            & ((_cmp_cached_2) | (_cmp_cached_133) | (_cmp_cached_45))
            # 1h down move, 1h still high, 1d high
            & ((_cmp_cached_2) | (_cmp_cached_49) | (_cmp_cached_84))
            # 1h down move, 1h still high, 4h overbought
            & ((_cmp_cached_2) | (_cmp_cached_49) | (_cmp_cached_27))
            # 1h down move, 1h still high, 1d downtrend
            & ((_cmp_cached_2) | (_cmp_cached_49) | (_cmp_cached_23))
            # 1h down move, 4h still high, 1d overbought
            & ((_cmp_cached_2) | (_cmp_cached_43) | (_cmp_cached_40))
            # 1h down move, 1d high, 4h downtrend
            & ((_cmp_cached_2) | (_cmp_cached_45) | (_cmp_cached_31))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_10) | (_cmp_cached_21) | (_cmp_cached_42))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_10) | (_cmp_cached_19) | (_cmp_cached_29))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_10) | (_cmp_cached_41) | (_cmp_cached_12))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_10) | (_cmp_cached_60) | (_cmp_cached_14))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_10) | (_cmp_cached_64) | (_cmp_cached_23))
            # 1h down move, 15m still high, 1d high
            & ((_cmp_cached_10) | (_cmp_cached_81) | (_cmp_cached_38))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_10) | (_cmp_cached_88) | (_cmp_cached_78))
            # 1h & 4h down move, 15m high
            & ((_cmp_cached_11) | (_cmp_cached_21) | (_cmp_cached_108))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_11) | (_cmp_cached_19) | (_cmp_cached_18))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_11) | (_cmp_cached_19) | (_cmp_cached_68))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_8) | (_cmp_cached_41) | (_cmp("RSI_14_1d", "<", 80.0)))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_8) | (_cmp_cached_103) | (_cmp_cached_40))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_8) | (_cmp_cached_84) | (_cmp_cached_39))
            # 1h down move, 15m still high, 1h high
            & ((_cmp_cached_8) | (_cmp_cached_46) | (_cmp_cached_92))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_8) | (_cmp_cached_32) | (_cmp_cached_40))
            # 1h & 4h down move, 1h still high
            & ((_cmp_cached_25) | (_cmp_cached_41) | (_cmp_cached_30))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_25) | (_cmp_cached_60) | (_cmp_cached_20))
            # 1h down move, 1h high , 1d overbought
            & ((_cmp_cached_25) | (_cmp_cached_37) | (_cmp_cached_51))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_25) | (_cmp_cached_13) | (_cmp_cached_29))
            # 1h & 1d down move, 1h high
            & ((_cmp_cached_65) | (_cmp_cached_107) | (_cmp_cached_18))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_65) | (_cmp("AROONU_14_1h", "<", 75.0)) | (_cmp_cached_14))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_63) | (_cmp_cached_55) | (_cmp("ROC_9_4h", "<", 25.0)))
            # 1h & 1d down move, 1h high
            & ((_cmp_cached_97) | (_cmp("RSI_3_1d", ">", 60.0)) | (_cmp_cached_12))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_80) | (_cmp_cached_53) | (_cmp("RSI_14_1d", "<", 40.0)))
            # 4h down move, 1h still not low enough, 4h downtrend
            & ((_cmp_cached_80) | (_cmp("AROONU_14_1h", "<", 20.0)) | (_cmp_cached_102))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_57) | (_cmp_cached_77) | (_cmp("STOCHRSIk_14_14_3_3_1d", "<", 40.0)))
            # 4h down move, 1h high
            & ((_cmp_cached_57) | (_cmp_cached_83))
            # 4h down move, 4h & 1d downtrend
            & ((_cmp_cached_57) | (_cmp_cached_102) | (_cmp_cached_142))
            # 4h & 1d down move, 1h high
            & ((_cmp_cached_4) | (_cmp_cached_66) | (_cmp_cached_112))
            # 4h & 1d down move, 4h downtrend
            & ((_cmp_cached_4) | (_cmp_cached_66) | (_cmp_cached_31))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_4) | (_cmp_cached_59) | (_cmp_cached_135))
            # 4h & 1d down move, 1d downtrend
            & ((_cmp_cached_4) | (_cmp_cached_59) | (_cmp_cached_23))
            # 4h & 1d down move, 1h high
            & ((_cmp_cached_4) | (_cmp_cached_77) | (_cmp_cached_71))
            # 4h down move, 15m still high, 1h still high
            & ((_cmp_cached_4) | (_cmp_cached_81) | (_cmp_cached_30))
            # 4h down move, 4h still high, 4h downtrend
            & ((_cmp_cached_4) | (_cmp_cached_67) | (_cmp_cached_31))
            # 4h down move, 15m high
            & ((_cmp_cached_4) | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 80.0)))
            # 4h down move, 1h still not low enough, 4h downtrend
            & ((_cmp_cached_4) | (_cmp_cached_132) | (_cmp_cached_31))
            # 4h & 1d down move, 15m still high
            & ((_cmp_cached_5) | (_cmp_cached_59) | (_cmp_cached_75))
            # 4h & 1d down move, 1h still high
            & ((_cmp_cached_5) | (_cmp_cached_59) | (_cmp_cached_82))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_53) | (_cmp("AROONU_14_1d", "<", 60.0)))
            # 4h & 1d down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_64) | (_cmp_cached_13))
            # 4h & 1d down move, 4h still high
            & ((_cmp_cached_5) | (_cmp_cached_77) | (_cmp_cached_54))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_118) | (_cmp_cached_45))
            # 4h & 1d down move, 4h still high
            & ((_cmp_cached_5) | (_cmp("RSI_3_1d", ">", 50.0)) | (_cmp_cached_79))
            # 4h down move, 1d still high, 4h still not low enough
            & ((_cmp_cached_5) | (_cmp("RSI_14_1d", "<", 40.0)) | (_cmp_cached_94))
            # 4h down move, 4h still high, 4h downtrend
            & ((_cmp_cached_5) | (_cmp_cached_43) | (_cmp_cached_102))
            # 4h down move, 1d still high, 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_121) | (_cmp_cached_15))
            # 4h down move, 4h still not low enough, 1d downtrend
            & ((_cmp_cached_5) | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 20.0)) | (_cmp_cached_15))
            # 4h down move, 1h downtrend, 1d overbought
            & ((_cmp_cached_5) | (_cmp("ROC_9_1h", ">", -10.0)) | (_cmp_cached_74))
            # 4h down move, 4h high, 4h downtrend
            & ((_cmp_cached_6) | (_cmp_cached_68) | (_cmp_cached_31))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_6) | (_cmp_cached_42) | (_cmp("ROC_9_1d", "<", 70.0)))
            # 4h down move, 4h & 1d downtrend
            & ((_cmp_cached_21) | (_cmp_cached_102) | (_cmp_cached_142))
            # 1h down move, 4h still not low enough, 1d downtrend
            & ((_cmp_cached_6) | (_cmp_cached_94) | (_cmp_cached_15))
            # 4h & 1d down move, 1h high
            & ((_cmp_cached_21) | (_cmp_cached_64) | (_cmp_cached_37))
            # 4h down move, 1h high
            & ((_cmp_cached_21) | (_cmp_cached_56))
            # 4h & 1d down move, 1d overbought
            & ((_cmp_cached_21) | (_cmp_cached_118) | (_cmp_cached_51))
            # 4h & 1d down move, 4h still high
            & ((_cmp_cached_19) | (_cmp_cached_77) | (_cmp_cached_54))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_19) | (_cmp("RSI_3_1d", ">", 60.0)) | (_cmp_cached_38))
            # 4h down move, 15m & 4h high
            & ((_cmp_cached_19) | (_cmp_cached_24) | (_cmp_cached_13))
            # 4h down move, 1h high, 1d downtrend
            & ((_cmp_cached_19) | (_cmp_cached_37) | (_cmp_cached_44))
            # 4h down move, 4h & 1d downtrend
            & ((_cmp_cached_19) | (_cmp_cached_31) | (_cmp_cached_44))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_41) | (_cmp_cached_79) | (_cmp_cached_23))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_41) | (_cmp_cached_84) | (_cmp_cached_39))
            # 4h down move, 15m still high, 1h high
            & ((_cmp_cached_41) | (_cmp_cached_46) | (_cmp_cached_71))
            # 4h down move, 1h high
            & ((_cmp_cached_47) | (_cmp_cached_18))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_76) | (_cmp_cached_45) | (_cmp_cached_39))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_131) | (_cmp_cached_62) | (_cmp_cached_69))
            # 1d down move, 1d high, 4h downtrend
            & ((_cmp_cached_59) | (_cmp_cached_45) | (_cmp_cached_139))
            # 1d down move, 1h & 4h high
            & ((_cmp_cached_77) | (_cmp_cached_12) | (_cmp_cached_14))
            # 1d down move, 4h high, 1d overbought
            & ((_cmp_cached_107) | (_cmp_cached_55) | (_cmp_cached_78))
            # 1d down move, 1d high & overbought
            & ((_cmp("RSI_3_1d", ">", 55.0)) | (_cmp_cached_84) | (_cmp_cached_78))
            # 1d down move, 1d overbought
            & ((_cmp("RSI_3_1d", ">", 60.0)) | (_cmp_cached_74))
            # 15m & 1h high, 4h overbought
            & ((_cmp_cached_24) | (_cmp_cached_71) | (_cmp("ROC_9_4h", "<", 15.0)))
            # 15m & 1h high, 1d overbought
            & ((_cmp_cached_24) | (_cmp_cached_71) | (_cmp_cached_29))
            # 15m & 1h high, 1d downtrend
            & ((_cmp_cached_24) | (_cmp_cached_71) | (_cmp_cached_142))
            # 15m high, 1d high & overbought
            & ((_cmp_cached_24) | (_cmp_cached_38) | (_cmp_cached_51))
            # 15m high, 1d high & overbought
            & ((_cmp_cached_24) | (_cmp_cached_9) | (_cmp_cached_39))
            # 15m high, 1h high, 1d downtrend
            & ((_cmp_cached_24) | (_cmp_cached_37) | (_cmp_cached_15))
            # 1h & 4h high, 4h overbought
            & ((_cmp_cached_52) | (_cmp_cached_32) | (_cmp_cached_27))
            # 1h & 4h high, 1d overbought
            & ((_cmp_cached_52) | (_cmp_cached_14) | (_cmp_cached_35))
            # 1h & 1d high, 1d overbought
            & ((_cmp_cached_71) | (_cmp_cached_9) | (_cmp_cached_40))
            # 4h & 1d high, 4h overbought
            & ((_cmp_cached_14) | (_cmp_cached_9) | (_cmp_cached_98))
            # 4h & 1d high, 1d overbought
            & ((_cmp_cached_32) | (_cmp_cached_9) | (_cmp_cached_35))
            # 4h & 1d overbought
            & ((_cmp_cached_115) | (_cmp_cached_74))
          )

          # Logic
          long_entry_logic.append(
            _rsi_20_falling
            & (_cmp("RSI_3", "<", 30.0))
            & (_cmp("AROONU_14", "<", 25.0))
            & (df["close"] < df["SMA_16"] * 0.960)
          )

        # Condition #142 - Top Coins mode (Long).
        if long_entry_condition_index == 142:
          # Protections
          long_entry_logic.append(is_pair_long_top_coins_mode)
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          long_entry_logic.append(df["protections_long_global"] == True)

          long_entry_logic.append(
            # 5m & 4h down move, 15m high
            ((_cmp_cached_143) | (_cmp_cached_4) | (_cmp_cached_81))
            # 5m & 1d down move, 15m high
            & ((_cmp_cached_143) | (_cmp_cached_77) | (_cmp("AROONU_14_15m", "<", 80.0)))
            # 5m down move, 1h & 1d high
            & ((_cmp_cached_143) | (_cmp_cached_18) | (_cmp_cached_9))
            # 5m down move, 15m & 1h high
            & ((_cmp_cached_143) | (_cmp("AROONU_14_15m", "<", 85.0)) | (_cmp_cached_71))
            # 15m & 1h & 4h down move
            & ((_cmp_cached_7) | (_cmp_cached_36) | (_cmp_cached_5))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_7) | (_cmp_cached_1) | (_cmp_cached_45))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_7) | (_cmp_cached_1) | (_cmp_cached_82))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_7) | (_cmp_cached_1) | (_cmp_cached_99))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_7) | (_cmp_cached_2) | (_cmp_cached_49))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_7) | (_cmp_cached_2) | (_cmp_cached_67))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_7) | (_cmp_cached_2) | (_cmp_cached_55))
            # 15m & 1h down move, 15m high
            & ((_cmp_cached_7) | (_cmp_cached_8) | (_cmp_cached_24))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_7) | (_cmp_cached_33) | (_cmp("AROONU_14_1h", "<", 75.0)))
            # 15m & 4h down move, 1d downtrend
            & ((_cmp_cached_7) | (_cmp_cached_4) | (_cmp_cached_15))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_7) | (_cmp_cached_21) | (_cmp_cached_67))
            # 15m down move, 1h high, 4h overbought
            & ((_cmp_cached_7) | (_cmp_cached_12) | (_cmp_cached_27))
            # 15m down move, 4h high
            & ((_cmp_cached_7) | (_cmp_cached_32))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_7) | (_cmp_cached_112) | (_cmp_cached_39))
            # 15m down move, 4h high
            & ((_cmp_cached_7) | (_cmp_cached_34))
            # 15m & 1h down move, 15m still not low enough
            & ((_cmp_cached_17) | (_cmp_cached_22) | (_cmp_cached_125))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_17) | (_cmp_cached_1) | (_cmp_cached_54))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_17) | (_cmp_cached_5) | (_cmp_cached_45))
            # 15m & 4h down move, 15m high
            & ((_cmp_cached_17) | (_cmp_cached_6) | (_cmp_cached_90))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_17) | (_cmp_cached_2) | (_cmp_cached_93))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_17) | (_cmp_cached_2) | (_cmp_cached_105))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_17) | (_cmp_cached_6) | (_cmp_cached_42))
            # 15m down move, 4h high, 1h overbought
            & ((_cmp_cached_17) | (_cmp_cached_14) | (_cmp_cached_61))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_1) | (_cmp_cached_93))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_0) | (_cmp_cached_1) | (_cmp_cached_82))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_1) | (_cmp_cached_105))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_0) | (_cmp_cached_2) | (_cmp_cached_30))
            # 15m & 1h down move, 15m high
            & ((_cmp_cached_0) | (_cmp_cached_10) | (_cmp_cached_90))
            # 15m & 1h down move, 15m still high
            & ((_cmp_cached_0) | (_cmp_cached_11) | (_cmp_cached_81))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_0) | (_cmp_cached_8) | (_cmp_cached_56))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_8) | (_cmp_cached_99))
            # 15m & 4h down move, 1d still high
            & ((_cmp_cached_0) | (_cmp_cached_4) | (_cmp_cached_121))
            # 15m & 4h down move, 15m still high
            & ((_cmp_cached_0) | (_cmp_cached_5) | (_cmp_cached_46))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_0) | (_cmp_cached_5) | (_cmp_cached_42))
            # 15m & 4h down move, 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_5) | (_cmp_cached_39))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_0) | (_cmp_cached_6) | (_cmp("RSI_14_1d", "<", 70.0)))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_0) | (_cmp_cached_6) | (_cmp_cached_43))
            # 14m & 4h down move, 1d high
            & ((_cmp_cached_0) | (_cmp_cached_6) | (_cmp_cached_42))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_0) | (_cmp_cached_6) | (_cmp_cached_56))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_0) | (_cmp_cached_6) | (_cmp_cached_84))
            # 15m & 4h down move, 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_6) | (_cmp_cached_35))
            # 15m & 4h down move, 15m high
            & ((_cmp_cached_0) | (_cmp_cached_19) | (_cmp_cached_24))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_0) | (_cmp_cached_19) | (_cmp_cached_51))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_0) | (_cmp_cached_41) | (_cmp_cached_52))
            # 15m & 4h down move, 4h overbought
            & ((_cmp_cached_0) | (_cmp_cached_41) | (_cmp_cached_27))
            # 15m & 4h down move, 15m high
            & ((_cmp_cached_0) | (_cmp_cached_47) | (_cmp_cached_24))
            # 15m & 1d down move, 1h still high
            & ((_cmp_cached_0) | (_cmp_cached_66) | (_cmp_cached_30))
            # 15m down move, 15m high, 1h high
            & ((_cmp_cached_0) | (_cmp_cached_24) | (_cmp_cached_37))
            # 15m down move, 4h high, 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_13) | (_cmp_cached_29))
            # 15m down move, 1d high & overbought
            & ((_cmp_cached_0) | (_cmp_cached_103) | (_cmp_cached_39))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_30) | (_cmp_cached_40))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_2) | (_cmp_cached_12))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_11) | (_cmp_cached_14))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_33) | (_cmp_cached_52))
            # 15m & 4h down move, 15m high
            & ((_cmp_cached_3) | (_cmp_cached_5) | (_cmp_cached_24))
            # 15m & 4h down move, 1d downtrend
            & ((_cmp_cached_3) | (_cmp_cached_5) | (_cmp_cached_15))
            # 15m & 4h down move, 1d overbought
            & ((_cmp_cached_3) | (_cmp_cached_6) | (_cmp_cached_35))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_41) | (_cmp_cached_52))
            # 15m & 1d down move, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_53) | (_cmp_cached_34))
            # 15m down move, 15m downtrend, 1h high
            & ((_cmp_cached_3) | (_cmp("CMF_20_15m", ">", -0.40)) | (_cmp_cached_88))
            # 15m down move, 15m still high, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_46) | (_cmp_cached_34))
            # 15m down move, 15m high, 1d overbought
            & ((_cmp_cached_3) | (_cmp_cached_24) | (_cmp_cached_78))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_3) | (_cmp_cached_71) | (_cmp_cached_14))
            # 15m down move, 15m high, 1d overbought
            & ((_cmp_cached_3) | (_cmp_cached_24) | (_cmp_cached_35))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_16) | (_cmp_cached_10) | (_cmp_cached_112))
            # 15m & 4h down move, 15m high
            & ((_cmp_cached_16) | (_cmp_cached_6) | (_cmp_cached_24))
            # 15m & 4h down move, 15m still high
            & ((_cmp_cached_16) | (_cmp_cached_6) | (_cmp_cached_75))
            # 15m down move, 15m & 1h high
            & ((_cmp_cached_16) | (_cmp_cached_24) | (_cmp_cached_71))
            # 15m down move, 15m high, 1d high
            & ((_cmp_cached_16) | (_cmp("AROONU_14_15m", "<", 90.0)) | (_cmp_cached_9))
            # 15m down move, 1h high, 1d downtrend
            & ((_cmp_cached_16) | (_cmp_cached_37) | (_cmp_cached_15))
            # 15m down move, 1h high & overbought
            & ((_cmp_cached_16) | (_cmp_cached_83) | (_cmp_cached_61))
            # 15m down move, 15m still high, 4h high
            & ((_cmp_cached_28) | (_cmp_cached_46) | (_cmp_cached_20))
            # 15m & 4h down mve, 1h high
            & ((_cmp_cached_70) | (_cmp_cached_19) | (_cmp_cached_37))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_70) | (_cmp_cached_76) | (_cmp_cached_34))
            # 15m down move, 1h high, 1d downtrend
            & ((_cmp_cached_70) | (_cmp_cached_52) | (_cmp_cached_142))
            # 15m down move, 15m high, 4h high
            & ((_cmp_cached_100) | (_cmp_cached_24) | (_cmp_cached_34))
            # 15m down move, 15m & 4h high
            & ((_cmp_cached_100) | (_cmp_cached_24) | (_cmp_cached_32))
            # 15m down move, 15m high, 1d overbought
            & ((_cmp_cached_100) | (_cmp("AROONU_14_15m", "<", 80.0)) | (_cmp_cached_35))
            # 15m down move, 1d high, 1h overbought
            & ((_cmp_cached_140) | (_cmp_cached_84) | (_cmp_cached_85))
            # 1h & 4h down move, 1d still high
            & ((_cmp_cached_36) | (_cmp_cached_4) | (_cmp_cached_121))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_36) | (_cmp_cached_21) | (_cmp_cached_78))
            # 1h & 4h down move, 1d still high
            & ((_cmp_cached_22) | (_cmp_cached_5) | (_cmp_cached_135))
            # 1h & 4h & 1d down move
            & ((_cmp_cached_22) | (_cmp_cached_6) | (_cmp_cached_64))
            # 1h & 4h down move, 15m high
            & ((_cmp_cached_22) | (_cmp_cached_21) | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 60.0)))
            # 1h & 4h & 1d down move
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp_cached_59))
            # 1h & 4h down move, 1d still not low enough
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp("STOCHRSIk_14_14_3_3_1d", "<", 20.0)))
            # 1h & 4h down move, 15m still high
            & ((_cmp_cached_1) | (_cmp_cached_5) | (_cmp_cached_75))
            # 1h & 4h down move, 1h still not low enough
            & ((_cmp_cached_1) | (_cmp_cached_6) | (_cmp_cached_138))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_1) | (_cmp_cached_6) | (_cmp_cached_29))
            # 1h & 1d downtrend, 1d high
            & ((_cmp_cached_1) | (_cmp_cached_107) | (_cmp_cached_45))
            # 1h & 4h down move, 1h still not low enough
            & ((_cmp_cached_2) | (_cmp_cached_5) | (_cmp("AROONU_14_1h", "<", 20.0)))
            # 1h & 4h down move. 4h high
            & ((_cmp_cached_2) | (_cmp_cached_5) | (_cmp_cached_68))
            # 1h & 4h down move, 1d still high
            & ((_cmp_cached_2) | (_cmp_cached_5) | (_cmp_cached_121))
            # 1h & 4h down move, 1h still not low enough
            & ((_cmp_cached_2) | (_cmp_cached_5) | (_cmp_cached_109))
            # 1h & 4h down move, 15m still not low enough
            & ((_cmp_cached_2) | (_cmp_cached_5) | (_cmp_cached_125))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_2) | (_cmp_cached_6) | (_cmp_cached_79))
            # 1h & 1d down move, 1d still high
            & ((_cmp_cached_2) | (_cmp_cached_53) | (_cmp("STOCHRSIk_14_14_3_3_1d", "<", 40.0)))
            # 1h & 1d down move, 1d high
            & ((_cmp_cached_2) | (_cmp_cached_133) | (_cmp_cached_45))
            # 1h down move, 15m & 1d high
            & ((_cmp_cached_2) | (_cmp_cached_24) | (_cmp_cached_9))
            # 1h down move, 1h still high, 4h overbought
            & ((_cmp_cached_2) | (_cmp_cached_49) | (_cmp_cached_27))
            # 1h down move, 1h still high, 1d downtrend
            & ((_cmp_cached_2) | (_cmp_cached_49) | (_cmp_cached_23))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_2) | (_cmp_cached_50) | (_cmp_cached_35))
            # 1h & 4h down move, 1h still high
            & ((_cmp_cached_10) | (_cmp_cached_6) | (_cmp_cached_49))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_10) | (_cmp_cached_21) | (_cmp_cached_42))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_10) | (_cmp_cached_19) | (_cmp_cached_29))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_10) | (_cmp_cached_41) | (_cmp_cached_12))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_10) | (_cmp_cached_60) | (_cmp_cached_14))
            # 1h & 4h down move, 15m high
            & ((_cmp_cached_11) | (_cmp_cached_21) | (_cmp_cached_108))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_11) | (_cmp_cached_19) | (_cmp_cached_68))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_50) | (_cmp_cached_99))
            # 1h & 1d down move, 1d still high
            & ((_cmp_cached_11) | (_cmp_cached_64) | (_cmp_cached_117))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_8) | (_cmp_cached_19) | (_cmp_cached_112))
            # 1h & 4g down move, 4h still high
            & ((_cmp_cached_8) | (_cmp_cached_19) | (_cmp_cached_54))
            # 1h down move, 15m still high, 1h high
            & ((_cmp_cached_8) | (_cmp_cached_46) | (_cmp_cached_92))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_25) | (_cmp_cached_13) | (_cmp_cached_29))
            # 1h down move, 4h & 1d high
            & ((_cmp_cached_25) | (_cmp_cached_14) | (_cmp_cached_9))
            # 1h down move, 1h still high, 1d downtrend
            & ((_cmp_cached_25) | (_cmp_cached_30) | (_cmp_cached_23))
            # 1h & 1d down move, 1h high
            & ((_cmp_cached_65) | (_cmp_cached_107) | (_cmp_cached_18))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_65) | (_cmp("AROONU_14_1h", "<", 75.0)) | (_cmp_cached_14))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_63) | (_cmp_cached_55) | (_cmp("ROC_9_4h", "<", 25.0)))
            # 4h & 1d down move, 1d downtrend
            & ((_cmp_cached_80) | (_cmp_cached_66) | (_cmp_cached_15))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_80) | (_cmp_cached_53) | (_cmp("RSI_14_1d", "<", 40.0)))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_57) | (_cmp_cached_107) | (_cmp_cached_45))
            # 4h down move, 4h still high, 4h downtrend
            & ((_cmp_cached_57) | (_cmp_cached_67) | (_cmp_cached_102))
            # 4h down move, 1h high
            & ((_cmp_cached_57) | (_cmp_cached_83))
            # 4h & 1d down move, 1h still high
            & ((_cmp_cached_4) | (_cmp_cached_66) | (_cmp_cached_30))
            # 4h & 1d down move, 1h high
            & ((_cmp_cached_4) | (_cmp_cached_59) | (_cmp_cached_56))
            # 4h down move, 15m still high, 1h still high
            & ((_cmp_cached_4) | (_cmp_cached_81) | (_cmp_cached_30))
            # 4h down move, 1d still high, 1d downtrend
            & ((_cmp_cached_4) | (_cmp_cached_121) | (_cmp_cached_23))
            # 4h down move, 15m high
            & ((_cmp_cached_4) | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 80.0)))
            # 4h down move, 15m still high, 1d downtrend
            & ((_cmp_cached_4) | (_cmp_cached_75) | (_cmp_cached_23))
            # 4h down move, 1h still high, 1d downtrend
            & ((_cmp_cached_4) | (_cmp_cached_30) | (_cmp_cached_23))
            # 4h down move, 1h high, 4h downtrend
            & ((_cmp_cached_4) | (_cmp_cached_56) | (_cmp_cached_31))
            # 4h down move, 4h & 1d downtrend
            & ((_cmp_cached_4) | (_cmp("ROC_9_4h", ">", -15.0)) | (_cmp_cached_15))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_5) | (_cmp_cached_59) | (_cmp_cached_121))
            # 4h & 1d down move, 4h still high
            & ((_cmp_cached_5) | (_cmp_cached_53) | (_cmp_cached_67))
            # 4h & 1d down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_64) | (_cmp_cached_13))
            # 4h & 1d down move, 15m high
            & ((_cmp_cached_5) | (_cmp_cached_77) | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 80.0)))
            # 4h & 1d down move, 4h still high
            & ((_cmp_cached_5) | (_cmp("RSI_3_1d", ">", 50.0)) | (_cmp_cached_79))
            # 4h down move, 1d still high, 4h still not low enough
            & ((_cmp_cached_5) | (_cmp("RSI_14_1d", "<", 40.0)) | (_cmp_cached_94))
            # 4h down move, 15m still not low enough, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_111) | (_cmp_cached_45))
            # 4h down move, 4h still high, 4h downtrend
            & ((_cmp_cached_5) | (_cmp_cached_43) | (_cmp_cached_102))
            # 4h down move, 4h still not low enough, 1d downtrend
            & ((_cmp_cached_5) | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 20.0)) | (_cmp_cached_15))
            # 4h down move, 4h & 1d high
            & ((_cmp_cached_6) | (_cmp_cached_13) | (_cmp_cached_45))
            # 4h down move, 4h high
            & ((_cmp_cached_6) | (_cmp_cached_20))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_6) | (_cmp_cached_42) | (_cmp("ROC_9_1d", "<", 70.0)))
            # 4h down move, 4h still high, 4h downtrend
            & ((_cmp_cached_6) | (_cmp_cached_54) | (_cmp_cached_31))
            # 4h down move, 4h high, 1d downtrend
            & ((_cmp_cached_6) | (_cmp_cached_58) | (_cmp_cached_15))
            # 4h down move, 1d overbought
            & ((_cmp_cached_6) | (_cmp_cached_69))
            # 4h & 1d down move, 4h overbought
            & ((_cmp_cached_21) | (_cmp_cached_107) | (_cmp("ROC_9_4h", "<", 5.0)))
            # 4h & 1d down move, 1d overbought
            & ((_cmp_cached_21) | (_cmp_cached_107) | (_cmp_cached_78))
            # 4h down move, 15m still not low enough, 4h still high
            & ((_cmp_cached_21) | (_cmp_cached_111) | (_cmp_cached_79))
            # 4h down move, 1d high, 4h overbought
            & ((_cmp_cached_21) | (_cmp_cached_42) | (_cmp("ROC_9_4h", "<", 5.0)))
            # 4h & 1d down move, 4h still high
            & ((_cmp_cached_19) | (_cmp_cached_77) | (_cmp_cached_54))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_19) | (_cmp("RSI_3_1d", ">", 60.0)) | (_cmp_cached_38))
            # 4h down move, 4h high, 1d high
            & ((_cmp_cached_19) | (_cmp_cached_13) | (_cmp_cached_84))
            # 4h down move, 1d stil high, 1d downtrend
            & ((_cmp_cached_19) | (_cmp_cached_135) | (_cmp_cached_23))
            # 4h down move, 1h high, 1d downtrend
            & ((_cmp_cached_19) | (_cmp_cached_37) | (_cmp_cached_44))
            # 4h down move, 15m still high, 1h high
            & ((_cmp_cached_41) | (_cmp_cached_46) | (_cmp_cached_71))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_41) | (_cmp_cached_79) | (_cmp_cached_23))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_41) | (_cmp_cached_84) | (_cmp_cached_39))
            # 4h down move, 1h high
            & ((_cmp_cached_47) | (_cmp_cached_18))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_76) | (_cmp_cached_45) | (_cmp_cached_39))
            # 4h down move, 4h high, 1d downtrend
            & ((_cmp_cached_76) | (_cmp_cached_79) | (_cmp_cached_149))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_60) | (_cmp_cached_103) | (_cmp_cached_74))
            # 4h down move, 4h high & overbought
            & ((_cmp_cached_60) | (_cmp_cached_58) | (_cmp_cached_27))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_60) | (_cmp_cached_54) | (_cmp_cached_44))
            # 4h down move, 4h & 1d overbought
            & ((_cmp_cached_60) | (_cmp_cached_27) | (_cmp_cached_35))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_131) | (_cmp_cached_62) | (_cmp_cached_69))
            # 1d down move, 1d high, 4h downtrend
            & ((_cmp_cached_59) | (_cmp_cached_45) | (_cmp_cached_139))
            # 1d down move, 1d high, 1d downtrend
            & ((_cmp_cached_59) | (_cmp_cached_45) | (_cmp_cached_15))
            # 1d down move, 1h & 4h high
            & ((_cmp_cached_77) | (_cmp_cached_12) | (_cmp_cached_14))
            # 15m & 1h high, 4h overbought
            & ((_cmp_cached_24) | (_cmp_cached_71) | (_cmp("ROC_9_4h", "<", 15.0)))
            # 15m & 1h high, 1d overbought
            & ((_cmp_cached_24) | (_cmp_cached_71) | (_cmp_cached_29))
            # 15m & 1h high, 1d downtrend
            & ((_cmp_cached_24) | (_cmp_cached_71) | (_cmp_cached_142))
            # 15m & 4h & 1d high
            & ((_cmp_cached_24) | (_cmp_cached_32) | (_cmp_cached_9))
            # 15m high, 1d high & overbought
            & ((_cmp_cached_24) | (_cmp_cached_9) | (_cmp_cached_39))
            # 15m high, 1h & 4h overbought
            & ((_cmp_cached_24) | (_cmp_cached_61) | (_cmp_cached_27))
            # 15m high, 4h overbought, 1d downtrend
            & ((_cmp("AROONU_14_15m", "<", 80.0)) | (_cmp_cached_26) | (_cmp_cached_23))
            # 15m & 1h high
            & ((_cmp("AROONU_14_15m", "<", 90.0)) | (_cmp_cached_71))
            # 15m & 4h high
            & ((_cmp("AROONU_14_15m", "<", 90.0)) | (_cmp_cached_14))
            # 1h & 1d high, 1d overbought
            & ((_cmp_cached_71) | (_cmp_cached_9) | (_cmp_cached_78))
            # 1h & 4h high, 1h overbought
            & ((_cmp_cached_71) | (_cmp_cached_14) | (_cmp_cached_61))
            # 1h & 4h high, 4h overbought
            & ((_cmp_cached_71) | (_cmp_cached_14) | (_cmp_cached_27))
            # 4h & 1d high, 4h overbought
            & ((_cmp_cached_14) | (_cmp_cached_9) | (_cmp_cached_26))
            # 4h & 1d high, 1d overbought
            & ((_cmp_cached_14) | (_cmp_cached_9) | (_cmp_cached_51))
            # 4h high, 1h & 4h overbought
            & ((_cmp_cached_14) | (_cmp_cached_85) | (_cmp_cached_73))
            # 1d high, 4h & 1d downtrend
            & ((_cmp("AROONU_14_1d", "<", 60.0)) | (_cmp_cached_31) | (_cmp_cached_23))
            # 1d high, 4h & 1d overbought
            & ((_cmp_cached_9) | (_cmp_cached_123) | (_cmp_cached_29))
            # 15m high, 4h & 1d overbought
            & ((_cmp_cached_108) | (_cmp_cached_26) | (_cmp_cached_39))
            # 1h high, 1h & 1d overbought
            & ((_cmp_cached_37) | (_cmp_cached_85) | (_cmp_cached_29))
            # 4h high, 4h overbought, 1d downtrend
            & ((_cmp_cached_55) | (_cmp_cached_26) | (_cmp_cached_15))
            # 1d high, 1h & 4h overbought
            & ((_cmp_cached_84) | (_cmp_cached_85) | (_cmp_cached_26))
          )

          # Logic
          long_entry_logic.append(
            (_cmp_cached_104)
            & (_cmp("RSI_4", "<", 46.0))
            # & (_cmp("STOCHRSIk_14_14_3_3", "<", 20.0))
            & _rsi_20_falling
            & (df["close"] < df["SMA_16"] * 0.960)
          )

        # Condition #143 - Top Coins mode (Long).
        if long_entry_condition_index == 143:
          # Protections
          long_entry_logic.append(is_pair_long_top_coins_mode)
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          long_entry_logic.append(df["protections_long_global"] == True)

          long_entry_logic.append(
            # 5m & 4h & 1d down move
            ((_cmp_cached_48) | (_cmp_cached_4) | (_cmp_cached_66))
            # 5m & 4h down move, 4h still high
            & ((_cmp_cached_48) | (_cmp_cached_4) | (_cmp_cached_54))
            # 15m & 1h down move, 1h still not low enough
            & ((_cmp_cached_7) | (_cmp_cached_36) | (_cmp("AROONU_14_1h", "<", 25.0)))
            # 15m & 1h & 4h down move
            & ((_cmp_cached_7) | (_cmp_cached_22) | (_cmp_cached_4))
            # 15m & 1h down move, 15m still high
            & ((_cmp_cached_7) | (_cmp_cached_2) | (_cmp_cached_81))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_7) | (_cmp_cached_2) | (_cmp_cached_67))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_7) | (_cmp_cached_2) | (_cmp_cached_30))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_7) | (_cmp_cached_2) | (_cmp_cached_55))
            # 15m & 1h down move, 15m high
            & ((_cmp_cached_7) | (_cmp_cached_8) | (_cmp_cached_24))
            # 15m & 1h down move, 1d downtrend
            & ((_cmp_cached_7) | (_cmp_cached_25) | (_cmp_cached_23))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_7) | (_cmp_cached_33) | (_cmp_cached_92))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_7) | (_cmp_cached_5) | (_cmp_cached_43))
            # 15m & 4h down move, 15m still high
            & ((_cmp_cached_7) | (_cmp_cached_6) | (_cmp_cached_46))
            # 15m & 1d down move, 4h still high
            & ((_cmp_cached_7) | (_cmp_cached_53) | (_cmp_cached_54))
            # 15m & 4h down move, 1d still high
            & ((_cmp_cached_17) | (_cmp_cached_57) | (_cmp("RSI_14_1d", "<", 40.0)))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_17) | (_cmp_cached_1) | (_cmp_cached_110))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_17) | (_cmp_cached_2) | (_cmp_cached_9))
            # 15m & 4h down move, 15m still not low enough
            & ((_cmp_cached_17) | (_cmp_cached_4) | (_cmp_cached_111))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_17) | (_cmp_cached_4) | (_cmp_cached_20))
            # 15m & 4h down move, 1h still high
            & ((_cmp_cached_17) | (_cmp_cached_4) | (_cmp_cached_82))
            # 15m & 4h down move, 1d downtrend
            & ((_cmp_cached_17) | (_cmp_cached_4) | (_cmp_cached_15))
            # 15m & 1d down move, 1h still high
            & ((_cmp_cached_17) | (_cmp_cached_66) | (_cmp_cached_49))
            # 15m & 1d down move, 1h still high
            & ((_cmp_cached_7) | (_cmp_cached_64) | (_cmp_cached_30))
            # 15m down move, 1h high, 4h overbought
            & ((_cmp_cached_7) | (_cmp_cached_12) | (_cmp_cached_27))
            # 15m down move, 4h high, 1d downtrend
            & ((_cmp_cached_7) | (_cmp_cached_58) | (_cmp_cached_15))
            # 15m down move, 15m still high, 1d downtrend
            & ((_cmp_cached_17) | (_cmp_cached_46) | (_cmp_cached_15))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_17) | (_cmp_cached_30) | (_cmp_cached_40))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_0) | (_cmp_cached_1) | (_cmp_cached_88))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_1) | (_cmp_cached_68))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_0) | (_cmp_cached_10) | (_cmp_cached_18))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_0) | (_cmp_cached_11) | (_cmp_cached_56))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_0) | (_cmp_cached_8) | (_cmp_cached_56))
            # 15m & 4h down move, 1h still high
            & ((_cmp_cached_0) | (_cmp_cached_4) | (_cmp_cached_30))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_0) | (_cmp_cached_6) | (_cmp_cached_56))
            # 15m & 4h down move, 4h overbought
            & ((_cmp_cached_0) | (_cmp_cached_41) | (_cmp_cached_27))
            # 15m & 1d down move, 1h high
            & ((_cmp_cached_0) | (_cmp_cached_66) | (_cmp_cached_56))
            # 15m & 1d down move, 4h still high
            & ((_cmp_cached_0) | (_cmp_cached_66) | (_cmp_cached_79))
            # 15m & 4h down move, 15m high
            & ((_cmp_cached_0) | (_cmp_cached_47) | (_cmp_cached_24))
            # 15m down move, 15m high, 1d high
            & ((_cmp_cached_0) | (_cmp_cached_90) | (_cmp_cached_9))
            # 15m down move, 1h & 1d high
            & ((_cmp_cached_0) | (_cmp_cached_52) | (_cmp_cached_9))
            # 15m down move, 4h high, 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_13) | (_cmp_cached_29))
            # 15m down move, 1h still high, 1d downtrend
            & ((_cmp_cached_0) | (_cmp_cached_30) | (_cmp_cached_15))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_41) | (_cmp_cached_52))
            # 1h & 1d down move, 1d still high
            & ((_cmp_cached_36) | (_cmp_cached_64) | (_cmp("STOCHRSIk_14_14_3_3_1d", "<", 40.0)))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_22) | (_cmp_cached_57) | (_cmp_cached_23))
            # 1h & 4h down move, 1d still high
            & ((_cmp_cached_22) | (_cmp_cached_4) | (_cmp_cached_121))
            # 1h & 4h & 1d down move
            & ((_cmp_cached_22) | (_cmp_cached_4) | (_cmp_cached_53))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_22) | (_cmp_cached_5) | (_cmp_cached_145))
            # 1h down move, 4h & 1d downtrend
            & ((_cmp_cached_22) | (_cmp_cached_102) | (_cmp_cached_15))
            # 1h & 4h down move, 1d still not low enough
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp("STOCHRSIk_14_14_3_3_1d", "<", 20.0)))
            # 1h & 4h down move, 15m still not low enough
            & ((_cmp_cached_2) | (_cmp_cached_80) | (_cmp_cached_125))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_2) | (_cmp_cached_5) | (_cmp_cached_68))
            # 1h down move, 1h still not low enough, 1d overbought
            & ((_cmp_cached_2) | (_cmp_cached_109) | (_cmp_cached_35))
            # 1h down move, 1h still high, 1d downtrend
            & ((_cmp_cached_2) | (_cmp_cached_82) | (_cmp_cached_15))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_2) | (_cmp_cached_62) | (_cmp_cached_40))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_10) | (_cmp_cached_6) | (_cmp_cached_12))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_10) | (_cmp_cached_21) | (_cmp_cached_42))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_10) | (_cmp_cached_41) | (_cmp_cached_13))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_10) | (_cmp_cached_60) | (_cmp_cached_14))
            # 1h & 1d down move, 1d overbought
            & ((_cmp_cached_10) | (_cmp_cached_118) | (_cmp_cached_51))
            # 1h down move, 1d high, 1d downtrend
            & ((_cmp_cached_10) | (_cmp_cached_45) | (_cmp_cached_15))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_11) | (_cmp_cached_18) | (_cmp_cached_14))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_26) | (_cmp_cached_51))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_8) | (_cmp_cached_19) | (_cmp_cached_112))
            # 1h down move, 15m still high, 1h high
            & ((_cmp_cached_8) | (_cmp_cached_46) | (_cmp_cached_92))
            # 1h & 1d down move, 1h high
            & ((_cmp_cached_65) | (_cmp_cached_107) | (_cmp_cached_18))
            # 4h & 1d down move, 15m still not low enough
            & ((_cmp_cached_80) | (_cmp_cached_59) | (_cmp("AROONU_14_15m", "<", 20.0)))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_80) | (_cmp_cached_64) | (_cmp_cached_45))
            # 4h & 1d down move, 1d downtrend
            & ((_cmp_cached_57) | (_cmp("RSI_3_1d", ">", 5.0)) | (_cmp_cached_23))
            # 4h & 1d down move, 1h still high
            & ((_cmp_cached_57) | (_cmp_cached_66) | (_cmp_cached_30))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_57) | (_cmp_cached_79) | (_cmp_cached_15))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_4) | (_cmp_cached_59) | (_cmp_cached_45))
            # 4h & 1d down move, 15m still high
            & ((_cmp_cached_4) | (_cmp_cached_53) | (_cmp_cached_113))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_4) | (_cmp_cached_9) | (_cmp_cached_78))
            # 4h down move, 1h high, 1d downtrend
            & ((_cmp_cached_4) | (_cmp_cached_30) | (_cmp_cached_23))
            # 4h down move, 4h & 1d downtrend
            & ((_cmp_cached_4) | (_cmp_cached_31) | (_cmp_cached_44))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_53) | (_cmp("AROONU_14_1d", "<", 60.0)))
            # 4h & 1d down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_77) | (_cmp_cached_105))
            # 4h down move, 1d still high, 4h still not low enough
            & ((_cmp_cached_5) | (_cmp("RSI_14_1d", "<", 40.0)) | (_cmp_cached_94))
            # 1h down move, 1h still high, 1d downtrend
            & ((_cmp_cached_2) | (_cmp_cached_49) | (_cmp_cached_23))
            # 4h down move, 4h & 1d high
            & ((_cmp_cached_5) | (_cmp_cached_13) | (_cmp_cached_45))
            # 4h down move, 1h still not low enough, 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_132) | (_cmp_cached_15))
            # 4h down move, 1h high
            & ((_cmp_cached_5) | (_cmp_cached_37))
            # 4h down move, 1h downtrend, 1d overbought
            & ((_cmp_cached_5) | (_cmp("ROC_9_1h", ">", -10.0)) | (_cmp_cached_74))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_6) | (_cmp_cached_53) | (_cmp_cached_121))
            # 4h down move, 4h & 1d high
            & ((_cmp_cached_6) | (_cmp_cached_13) | (_cmp_cached_45))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_6) | (_cmp_cached_42) | (_cmp("ROC_9_1d", "<", 70.0)))
            # 4h down move, 4h high, 1d downtrend
            & ((_cmp_cached_6) | (_cmp_cached_105) | (_cmp_cached_15))
            # 4h & 1d down move, 1d overbought
            & ((_cmp_cached_21) | (_cmp_cached_118) | (_cmp_cached_51))
            # 4h down move, 1h high, 1d downtrend
            & ((_cmp_cached_21) | (_cmp_cached_112) | (_cmp_cached_15))
            # 4h down move, 15m still high, 1h high
            & ((_cmp_cached_41) | (_cmp_cached_46) | (_cmp_cached_71))
            # 4h down move, 1h high
            & ((_cmp_cached_47) | (_cmp_cached_18))
            # 4h down move, 4h high, 1d downtrend
            & ((_cmp_cached_76) | (_cmp_cached_34) | (_cmp_cached_15))
            # 1h high, 4h & 1d overbought
            & ((_cmp_cached_12) | (_cmp_cached_73) | (_cmp_cached_69))
            # 1h & 4h high, 1d overbought
            & ((_cmp_cached_92) | (_cmp_cached_14) | (_cmp_cached_40))
            # 1d high, 4h & 1d downtrend
            & ((_cmp("AROONU_14_1d", "<", 60.0)) | (_cmp_cached_31) | (_cmp_cached_23))
            # 4h high, 4h & 1d overbought
            & ((_cmp_cached_55) | (_cmp_cached_26) | (_cmp_cached_39))
          )

          # Logic
          long_entry_logic.append(
            (_cmp("RSI_3", "<", 40.0))
            & (_cmp("STOCHRSIk_14_14_3_3", "<", 20.0))
            & (df["EMA_26"] > df["EMA_12"])
            & ((df["EMA_26"] - df["EMA_12"]) > (df["open"] * 0.020))
            & _ema_26_12_spread_gt_open_pct
          )

        # Condition #144 - Top Coins mode (Long).
        if long_entry_condition_index == 144:
          # Protections
          long_entry_logic.append(is_pair_long_top_coins_mode)
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          long_entry_logic.append(df["protections_long_global"] == True)

          long_entry_logic.append(
            # 5m & 1h down move, 1h still not low enough
            ((_cmp_cached_48) | (_cmp_cached_1) | (_cmp_cached_138))
            # 5m & 4h down move, 15m still high
            & ((_cmp_cached_48) | (_cmp_cached_57) | (_cmp_cached_81))
            # 5m & 4h & 1d down move
            & ((_cmp_cached_48) | (_cmp_cached_4) | (_cmp_cached_66))
            # 5m & 4h down move, 1d downtrend
            & ((_cmp_cached_48) | (_cmp_cached_4) | (_cmp_cached_142))
            # 5m & 4h down move, 15m high
            & ((_cmp_cached_143) | (_cmp_cached_4) | (_cmp_cached_81))
            # 15m & 1h down move, 1h still not low enough
            & ((_cmp_cached_7) | (_cmp_cached_36) | (_cmp("AROONU_14_1h", "<", 25.0)))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_17) | (_cmp_cached_22) | (_cmp_cached_45))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_17) | (_cmp_cached_1) | (_cmp_cached_9))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_17) | (_cmp_cached_8) | (_cmp_cached_51))
            # 15m & 4h down move, 4h downtrend
            & ((_cmp_cached_17) | (_cmp_cached_57) | (_cmp_cached_31))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_17) | (_cmp_cached_19) | (_cmp_cached_79))
            # 15m down move, 1d high & overbought
            & ((_cmp_cached_17) | (_cmp_cached_9) | (_cmp_cached_40))
            # 15m & 4h down move, 4h still not low enough
            & ((_cmp_cached_0) | (_cmp_cached_4) | (_cmp("RSI_14_4h", "<", 20.0)))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_76) | (_cmp_cached_13))
            # 15m down move, 4h high, 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_20) | (_cmp_cached_35))
            # 15m & 1h down move, 15m still high
            & ((_cmp_cached_3) | (_cmp_cached_2) | (_cmp_cached_75))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_3) | (_cmp_cached_10) | (_cmp_cached_51))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_25) | (_cmp_cached_14))
            # 15m & 4h down move, 15m still high
            & ((_cmp_cached_3) | (_cmp_cached_5) | (_cmp_cached_81))
            # 15m down move, 4h & 1d overbought
            & ((_cmp_cached_3) | (_cmp_cached_26) | (_cmp_cached_74))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_28) | (_cmp_cached_8) | (_cmp_cached_14))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_28) | (_cmp_cached_33) | (_cmp_cached_55))
            # 15m down move, 4h high, 1d downtrend
            & ((_cmp_cached_28) | (_cmp_cached_34) | (_cmp_cached_23))
            # 15m & 1h down move, 15m high
            & ((_cmp("RSI_3_15m", ">", 45.0)) | (_cmp_cached_65) | (_cmp_cached_108))
            # 15m down move, 4h high, 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_13) | (_cmp_cached_29))
            # 15m & 4h down move, 1d downtrend
            & ((_cmp_cached_3) | (_cmp_cached_5) | (_cmp_cached_15))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_8) | (_cmp_cached_34))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_16) | (_cmp_cached_14) | (_cmp_cached_50))
            # 15m down move, 15m still high, 4h high
            & ((_cmp_cached_28) | (_cmp_cached_46) | (_cmp_cached_20))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_28) | (_cmp_cached_34) | (_cmp_cached_26))
            # 15m down move, 4h high, 1d downtrend
            & ((_cmp_cached_28) | (_cmp_cached_55) | (_cmp_cached_23))
            # 15m down move, 1h & 4h overbought
            & ((_cmp_cached_28) | (_cmp_cached_61) | (_cmp_cached_50))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_70) | (_cmp_cached_18) | (_cmp_cached_14))
            # 15m down move, 15m & 4h high
            & ((_cmp_cached_100) | (_cmp_cached_24) | (_cmp_cached_32))
            # 1h & 4h down move, 1h downtrend
            & ((_cmp_cached_36) | (_cmp_cached_4) | (_cmp("CMF_20_1h", ">", -0.20)))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_36) | (_cmp_cached_6) | (_cmp_cached_79))
            # 1h & 4h down move, 15m still high
            & ((_cmp_cached_36) | (_cmp_cached_19) | (_cmp_cached_75))
            # 1h & 4h down move, 15m still not low enough
            & ((_cmp_cached_22) | (_cmp_cached_57) | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 20.0)))
            # 1h & 4h down move, 1d still high
            & ((_cmp_cached_22) | (_cmp_cached_6) | (_cmp_cached_121))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_22) | (_cmp_cached_47) | (_cmp_cached_94))
            # 1h & 1d down move, 1h still high
            & ((_cmp_cached_22) | (_cmp("RSI_3_1d", ">", 5.0)) | (_cmp_cached_86))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_22) | (_cmp_cached_38) | (_cmp_cached_39))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_1) | (_cmp_cached_5) | (_cmp_cached_94))
            # 1h & 4h down move, 15m still high
            & ((_cmp_cached_1) | (_cmp_cached_5) | (_cmp_cached_75))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_5) | (_cmp_cached_15))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_1) | (_cmp_cached_21) | (_cmp_cached_54))
            # 1h & 1d down move, 4h high
            & ((_cmp_cached_1) | (_cmp_cached_66) | (_cmp_cached_58))
            # 1h & 1d down move, 1d high
            & ((_cmp_cached_1) | (_cmp_cached_53) | (_cmp_cached_45))
            # 1h down move, 1d high, 1h downtrend
            & ((_cmp_cached_1) | (_cmp_cached_45) | (_cmp("ROC_9_1h", ">", -10.0)))
            # 1h & 4h down move, 15m still not low enough
            & ((_cmp_cached_2) | (_cmp_cached_80) | (_cmp_cached_125))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_2) | (_cmp_cached_21) | (_cmp_cached_12))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_2) | (_cmp_cached_19) | (_cmp_cached_13))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_2) | (_cmp_cached_76) | (_cmp_cached_44))
            # 1h & 1d down move, 1d high
            & ((_cmp_cached_2) | (_cmp_cached_64) | (_cmp_cached_42))
            # 1h down move, 4h still high, 1d overbought
            & ((_cmp_cached_2) | (_cmp_cached_43) | (_cmp_cached_40))
            # 1h down move, 1d high, 4h downtrend
            & ((_cmp_cached_2) | (_cmp_cached_45) | (_cmp_cached_31))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_2) | (_cmp_cached_42) | (_cmp_cached_78))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_2) | (_cmp_cached_34) | (_cmp_cached_26))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_2) | (_cmp_cached_34) | (_cmp_cached_23))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_10) | (_cmp_cached_6) | (_cmp_cached_67))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_10) | (_cmp_cached_21) | (_cmp_cached_9))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_10) | (_cmp_cached_41) | (_cmp_cached_20))
            # 1h & 4h down move, 4h overbought
            & ((_cmp_cached_10) | (_cmp_cached_41) | (_cmp_cached_27))
            # 1h & 1d down move, 1h still high
            & ((_cmp_cached_10) | (_cmp_cached_64) | (_cmp_cached_49))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_10) | (_cmp_cached_20) | (_cmp("ROC_9_4h", "<", 70.0)))
            # 1h down move, 1h high, 1h still not low enough
            & ((_cmp_cached_10) | (_cmp_cached_42) | (_cmp_cached_132))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_10) | (_cmp_cached_9) | (_cmp_cached_39))
            # 1h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_10) | (_cmp_cached_79) | (_cmp_cached_44))
            # 1h & 4h down move, 15m high
            & ((_cmp_cached_11) | (_cmp_cached_21) | (_cmp_cached_108))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_11) | (_cmp_cached_21) | (_cmp_cached_94))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_21) | (_cmp_cached_29))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_11) | (_cmp_cached_19) | (_cmp_cached_68))
            # 1h & 1d down move, 1d high
            & ((_cmp_cached_11) | (_cmp_cached_64) | (_cmp_cached_45))
            # 1h down move, 4h & 1d high
            & ((_cmp_cached_11) | (_cmp_cached_13) | (_cmp_cached_9))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_8) | (_cmp_cached_41) | (_cmp("RSI_14_1d", "<", 80.0)))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_8) | (_cmp_cached_12) | (_cmp_cached_14))
            # 1h down move, 1h high, 4h high
            & ((_cmp_cached_8) | (_cmp_cached_18) | (_cmp_cached_34))
            # 1h down move, 4h high, 1h overbought
            & ((_cmp_cached_33) | (_cmp_cached_20) | (_cmp_cached_61))
            # 1h down move, 1h high, 15m high
            & ((_cmp_cached_63) | (_cmp_cached_12) | (_cmp_cached_108))
            # 4h & 1d down move, 15m still not low enough
            & ((_cmp_cached_80) | (_cmp_cached_59) | (_cmp("AROONU_14_15m", "<", 20.0)))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_80) | (_cmp_cached_53) | (_cmp("STOCHRSIk_14_14_3_3_1d", "<", 40.0)))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_80) | (_cmp_cached_64) | (_cmp_cached_45))
            # 4h down move, 15m high
            & ((_cmp_cached_80) | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 60.0)))
            # 4h down move, 15m still high, 4h still not low enough
            & ((_cmp_cached_57) | (_cmp_cached_75) | (_cmp_cached_145))
            # 4h & 1d down move, 15m still high
            & ((_cmp_cached_4) | (_cmp_cached_59) | (_cmp_cached_113))
            # 4h down move, 4h still not low enough, 1d downtrend
            & ((_cmp_cached_4) | (_cmp("AROONU_14_4h", "<", 20.0)) | (_cmp_cached_142))
            # 4h down move, 4h still high, 4h downtrend
            & ((_cmp_cached_4) | (_cmp_cached_67) | (_cmp_cached_31))
            # 4h down move, 1d still high, 1d downtrend
            & ((_cmp_cached_4) | (_cmp_cached_135) | (_cmp_cached_23))
            # 4h down move, 1d high, 4h downtrend
            & ((_cmp_cached_4) | (_cmp_cached_9) | (_cmp_cached_102))
            # 4h down move, 4h & 1d downtrend
            & ((_cmp_cached_4) | (_cmp_cached_102) | (_cmp_cached_15))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_5) | (_cmp_cached_59) | (_cmp_cached_121))
            # 4h & 1d down move, 4h still high
            & ((_cmp_cached_5) | (_cmp_cached_77) | (_cmp_cached_54))
            # 4h & 1d down move, 4h still high
            & ((_cmp_cached_5) | (_cmp_cached_107) | (_cmp_cached_79))
            # 4h down move, 4h still not low enough, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_145) | (_cmp_cached_45))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_5) | (_cmp_cached_9) | (_cmp_cached_51))
            # 4h down move, 15m high
            & ((_cmp_cached_5) | (_cmp_cached_108))
            # 4h & 1d down move, 1d downtrend
            & ((_cmp_cached_6) | (_cmp_cached_64) | (_cmp_cached_23))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_6) | (_cmp_cached_42) | (_cmp("ROC_9_1d", "<", 70.0)))
            # 4h & 1d down move, 1d overbought
            & ((_cmp_cached_21) | (_cmp_cached_107) | (_cmp_cached_78))
            # 4h & 1d down move, 1d overbought
            & ((_cmp_cached_19) | (_cmp("RSI_3_1d", ">", 70.0)) | (_cmp_cached_39))
            # 4h down move, 4h high, 1d high
            & ((_cmp_cached_19) | (_cmp_cached_13) | (_cmp_cached_84))
            # 4h down move, 1d stil high, 1d downtrend
            & ((_cmp_cached_19) | (_cmp_cached_135) | (_cmp_cached_23))
            # 4h down move, 4h still high, 4h downtrend
            & ((_cmp_cached_19) | (_cmp_cached_79) | (_cmp("ROC_9_4h", ">", -15.0)))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_41) | (_cmp_cached_79) | (_cmp_cached_15))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_131) | (_cmp_cached_62) | (_cmp_cached_29))
            # 1d down move, 4h still not low enough, 4h downtrend
            & ((_cmp_cached_66) | (_cmp_cached_94) | (_cmp("ROC_9_4h", ">", -15.0)))
            # 1d down move, 4h & 1d downtrend
            & ((_cmp_cached_66) | (_cmp_cached_31) | (_cmp_cached_15))
            # 1d down move, 1d high, 4h downtrend
            & ((_cmp_cached_59) | (_cmp_cached_45) | (_cmp_cached_31))
            # 4h & 1d down move, 4h overbought
            & ((_cmp_cached_21) | (_cmp_cached_107) | (_cmp("ROC_9_4h", "<", 5.0)))
            # 1d down move, 1h & 4h high
            & ((_cmp_cached_64) | (_cmp_cached_12) | (_cmp_cached_14))
            # 1d down move, 1h & 4h high
            & ((_cmp_cached_77) | (_cmp_cached_12) | (_cmp_cached_14))
            # 1h high, 4h & 1d overbought
            & ((_cmp_cached_12) | (_cmp_cached_73) | (_cmp_cached_69))
            # 4h & 1d high, 1h overbought
            & ((_cmp_cached_93) | (_cmp_cached_9) | (_cmp_cached_61))
            # 4h high, 4h & 1d overbought
            & ((_cmp_cached_32) | (_cmp_cached_50) | (_cmp_cached_99))
            # 15m high, 4h & 1d overbought
            & ((_cmp("STOCHRSIk_14_14_3_3_15m", "<", 80.0)) | (_cmp_cached_26) | (_cmp_cached_39))
            # 15m still high, 4h & 1d overbought
            & ((_cmp_cached_75) | (_cmp_cached_73) | (_cmp_cached_29))
            # 4h high, 4h & 1d overbought
            & ((_cmp_cached_55) | (_cmp_cached_50) | (_cmp_cached_99))
            # 1d high, 4h & 1d overbought
            & ((_cmp_cached_62) | (_cmp_cached_50) | (_cmp_cached_29))
            # 4h & 1d overbought
            & ((_cmp_cached_115) | (_cmp_cached_74))
            # 1d P&D, 4h overbought
            & ((_cmp("change_pct_1d", ">", -10.0)) | (df["change_pct_1d"].shift(288) < 50.0) | (_cmp_cached_50))
          )

          # Logic
          long_entry_logic.append(
            (_cmp("WILLR_14", "<", -50.0))
            & (_cmp("STOCHRSIk_14_14_3_3", "<", 30.0))
            # & (_cmp_cached_113)
            & (_cmp_cached_82)
            & (_cmp("BBB_20_2.0_1h", ">", 12.0))
            & (df["close_max_48"] >= (df["close"] * 1.10))
          )

        # Condition #145 - Top Coins mode (Long).
        if long_entry_condition_index == 145:
          # Protections
          long_entry_logic.append(is_pair_long_top_coins_mode)
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          long_entry_logic.append(df["protections_long_global"] == True)

          long_entry_logic.append(
            # 5m & 4h down move, 1d downtrend
            ((_cmp_cached_48) | (_cmp_cached_80) | (_cmp_cached_15))
            # 5m down move, 15m & 1h high
            & ((_cmp_cached_143) | (_cmp("AROONU_14_15m", "<", 85.0)) | (_cmp_cached_71))
            # 15m & 1h & 4h down move
            & ((_cmp_cached_7) | (_cmp_cached_36) | (_cmp_cached_57))
            # 15m & 1h down move, 1h downtrend
            & ((_cmp_cached_7) | (_cmp_cached_36) | (_cmp_cached_120))
            # 15m & 1h down move, 1h still not low enough
            & ((_cmp_cached_7) | (_cmp_cached_1) | (_cmp_cached_132))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_17) | (_cmp_cached_1) | (_cmp_cached_13))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_0) | (_cmp_cached_25) | (_cmp_cached_12))
            # 15m & 4h down move, 4h still not low enough
            & ((_cmp_cached_0) | (_cmp_cached_4) | (_cmp_cached_145))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_2) | (_cmp_cached_12))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_33) | (_cmp_cached_52))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_3) | (_cmp_cached_5) | (_cmp_cached_38))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_41) | (_cmp_cached_52))
            # 15m down move, 15m downtrend, 1h high
            & ((_cmp_cached_3) | (_cmp("CMF_20_15m", ">", -0.40)) | (_cmp_cached_88))
            # 15m down move, 15m still high, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_81) | (_cmp_cached_105))
            # 15m down move, 1h high, 1d downtrend
            & ((_cmp_cached_3) | (_cmp_cached_52) | (_cmp_cached_23))
            # 15m & 1h down move, 1d downtrend
            & ((_cmp_cached_16) | (_cmp_cached_10) | (_cmp_cached_23))
            # 15m & 4h down move, 15m still high
            & ((_cmp_cached_16) | (_cmp_cached_6) | (_cmp_cached_75))
            # 15m down move, 15m & 1h high
            & ((_cmp_cached_16) | (_cmp_cached_24) | (_cmp_cached_71))
            # 15m & 1h down move, 15m still high
            & ((_cmp_cached_28) | (_cmp_cached_25) | (_cmp_cached_75))
            # 15m down move, 15m still high, 1d overbought
            & ((_cmp_cached_28) | (_cmp_cached_75) | (_cmp_cached_51))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_70) | (_cmp_cached_19) | (_cmp_cached_56))
            # 15m down move, 15m & 4h high
            & ((_cmp_cached_70) | (_cmp_cached_24) | (_cmp_cached_13))
            # 15m down move, 15m high, 1h high
            & ((_cmp_cached_70) | (_cmp_cached_24) | (_cmp_cached_56))
            # 15m down move, 15m high, 4h high
            & ((_cmp_cached_70) | (_cmp_cached_24) | (_cmp_cached_34))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_70) | (_cmp_cached_18) | (_cmp_cached_39))
            # 15m down move, 4h & 1d overbought
            & ((_cmp_cached_100) | (_cmp_cached_50) | (_cmp_cached_69))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_36) | (_cmp_cached_6) | (_cmp_cached_67))
            # 1h down move, 4h still high, 1d high
            & ((_cmp_cached_36) | (_cmp_cached_43) | (_cmp_cached_38))
            # 1h & 1d down move, 1d still high
            & ((_cmp_cached_22) | (_cmp_cached_53) | (_cmp_cached_135))
            # 1h & 1d down move, 1h still not low enough
            & ((_cmp_cached_22) | (_cmp_cached_64) | (_cmp("AROONU_14_1h", "<", 20.0)))
            # 1h & 4h & 1d down move
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp_cached_59))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp_cached_67))
            # 1h & 4h down move, 4h downtrend
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp_cached_102))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp_cached_23))
            # 1h & 4h down move, 15m high
            & ((_cmp_cached_1) | (_cmp_cached_6) | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 80.0)))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_21) | (_cmp_cached_95))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_1) | (_cmp_cached_41) | (_cmp_cached_32))
            # 1h & 1d down move, 1h still not low enough
            & ((_cmp_cached_1) | (_cmp_cached_53) | (_cmp_cached_138))
            # 1h down move, 15m downtrend, 1d high
            & ((_cmp_cached_1) | (_cmp("CMF_20_15m", ">", -0.40)) | (_cmp_cached_45))
            # 1h down move, 4h still high, 1d overbought
            & ((_cmp_cached_1) | (_cmp_cached_67) | (_cmp_cached_40))
            # 1h down move, 1d still high, 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_121) | (_cmp_cached_15))
            # 1h & 4h & 1d down move
            & ((_cmp_cached_2) | (_cmp_cached_5) | (_cmp_cached_53))
            # 1h & 4h down move, 15m still not low enough
            & ((_cmp_cached_2) | (_cmp_cached_5) | (_cmp_cached_125))
            # 1h & 4h down move, 15m still high
            & ((_cmp_cached_2) | (_cmp_cached_5) | (_cmp_cached_46))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_2) | (_cmp_cached_21) | (_cmp_cached_68))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_2) | (_cmp_cached_19) | (_cmp_cached_44))
            # 1h down move, 1h still high, 4h high
            & ((_cmp_cached_2) | (_cmp_cached_86) | (_cmp_cached_68))
            # 1h down move, 1h still high, 4h overbought
            & ((_cmp_cached_2) | (_cmp_cached_49) | (_cmp_cached_27))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_2) | (_cmp_cached_88) | (_cmp_cached_23))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_2) | (_cmp_cached_50) | (_cmp_cached_35))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_10) | (_cmp_cached_41) | (_cmp_cached_13))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_10) | (_cmp_cached_76) | (_cmp_cached_34))
            # 1h & 1d down move, 4h still high
            & ((_cmp_cached_10) | (_cmp_cached_53) | (_cmp_cached_54))
            # 1h & 1d down move, 1h still high
            & ((_cmp_cached_10) | (_cmp_cached_64) | (_cmp_cached_49))
            # 1h down move, 15m still high, 1h high
            & ((_cmp_cached_10) | (_cmp_cached_81) | (_cmp_cached_18))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_10) | (_cmp_cached_12) | (_cmp_cached_39))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_10) | (_cmp_cached_20) | (_cmp_cached_123))
            # 1h down move, 1h still not low enough, 1d downtrend
            & ((_cmp_cached_10) | (_cmp_cached_109) | (_cmp_cached_23))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_11) | (_cmp_cached_41) | (_cmp_cached_12))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_41) | (_cmp_cached_39))
            # 1h down move, 1h still high, 4h high
            & ((_cmp_cached_11) | (_cmp_cached_49) | (_cmp_cached_93))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_18) | (_cmp_cached_51))
            # 1h down move, 1h still high, 4h downtrend
            & ((_cmp_cached_11) | (_cmp_cached_30) | (_cmp_cached_31))
            # 1h down move, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_69))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_8) | (_cmp_cached_12) | (_cmp_cached_40))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_25) | (_cmp_cached_47) | (_cmp_cached_34))
            # 1h down move, 1h still high, 1d overbought
            & ((_cmp_cached_25) | (_cmp_cached_86) | (_cmp_cached_40))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_25) | (_cmp_cached_32) | (_cmp_cached_123))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_25) | (_cmp_cached_55) | (_cmp_cached_15))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_33) | (_cmp_cached_12) | (_cmp_cached_23))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_33) | (_cmp_cached_56) | (_cmp_cached_23))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_65) | (_cmp_cached_18) | (_cmp_cached_14))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_63) | (_cmp_cached_18) | (_cmp_cached_27))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_63) | (_cmp_cached_55) | (_cmp("ROC_9_4h", "<", 25.0)))
            # 4h down move, 4h & 1d downtrend
            & ((_cmp_cached_57) | (_cmp("ROC_9_4h", ">", -15.0)) | (_cmp_cached_15))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_4) | (_cmp_cached_77) | (_cmp_cached_117))
            # 4h down move, 4h & 1d high
            & ((_cmp_cached_4) | (_cmp_cached_68) | (_cmp_cached_45))
            # 4h down move, 1d still high, 1d downtrend
            & ((_cmp_cached_4) | (_cmp_cached_121) | (_cmp_cached_23))
            # 4h down move, 15m & 1h still not low enough
            & (
              (_cmp_cached_4) | (_cmp_cached_125) | (_cmp_cached_109)
            )
            # 4h down move, 15m stil high, 4h downtrend
            & ((_cmp_cached_4) | (_cmp_cached_75) | (_cmp_cached_31))
            # 4h & 1d down move, 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_64) | (_cmp_cached_23))
            # 4h & 1d down move, 1h still high
            & ((_cmp_cached_5) | (_cmp_cached_77) | (_cmp_cached_30))
            # 4h & 1d down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_133) | (_cmp_cached_58))
            # 4h down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_105))
            # 4h down move, 4h & 1d high
            & ((_cmp_cached_6) | (_cmp_cached_13) | (_cmp_cached_45))
            # 4h down move, 15m high
            & ((_cmp_cached_6) | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 90.0)))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_6) | (_cmp_cached_38) | (_cmp_cached_51))
            # 4h & 1d down move, 1d overbought
            & ((_cmp_cached_21) | (_cmp_cached_118) | (_cmp_cached_78))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_21) | (_cmp_cached_107) | (_cmp_cached_42))
            # 4h down move, 15m high, 1d overbought
            & ((_cmp_cached_19) | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 90.0)) | (_cmp_cached_78))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_41) | (_cmp_cached_79) | (_cmp_cached_23))
            # 4h down move, 4h high, 1d overbought
            & ((_cmp_cached_47) | (_cmp_cached_68) | (_cmp_cached_40))
            # 4h & 1d down move, 1h high
            & ((_cmp_cached_76) | (_cmp_cached_107) | (_cmp_cached_56))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_131) | (_cmp_cached_62) | (_cmp_cached_69))
            # 1d down move, 1d high, 1d downtrend
            & ((_cmp_cached_59) | (_cmp_cached_45) | (_cmp_cached_15))
            # 1d down move, 1h high
            & ((_cmp_cached_53) | (_cmp_cached_56))
            # 1d down move, 1h high, 1d downtrend
            & ((_cmp_cached_64) | (_cmp_cached_112) | (_cmp_cached_23))
            # 1d down move, 1d high, 4h downtrend
            & ((_cmp_cached_133) | (_cmp_cached_45) | (_cmp_cached_102))
            # 1d down move, 4h high, 1d overbought
            & ((_cmp("RSI_3_1d", ">", 60.0)) | (_cmp_cached_13) | (_cmp_cached_40))
            # 15m high, 1d high & overbought
            & ((_cmp_cached_24) | (_cmp_cached_9) | (_cmp_cached_29))
            # 15m high, 4h overbought, 1d downtrend
            & ((_cmp("AROONU_14_15m", "<", 80.0)) | (_cmp_cached_26) | (_cmp_cached_23))
            # 1h & 4h high, 4h overbought
            & ((_cmp_cached_12) | (_cmp_cached_14) | (_cmp_cached_27))
            # 1h high, 1d overbought
            & ((_cmp_cached_92) | (_cmp_cached_69))
            # 1h high, 4h & 1d downtrend
            & ((_cmp_cached_71) | (_cmp_cached_102) | (_cmp_cached_149))
            # 4h & 1d high, 1d overbought
            & ((_cmp_cached_14) | (_cmp_cached_9) | (_cmp_cached_99))
            # 1h high, 4h & 1d downtrend
            & ((_cmp_cached_37) | (_cmp_cached_102) | (_cmp_cached_149))
          )

          # Logic
          long_entry_logic.append(
            (_cmp("RSI_14", "<", 36.0))
            & (df["BBD_40_2.0"].gt(df["close"] * 0.020))
            & (df["close_delta"].gt(df["close"] * 0.02))
            & (df["BBT_40_2.0"].lt(df["BBD_40_2.0"] * 0.3))
            & _close_lt_bbl_40_prev
            & _close_lte_close_prev
          )

        # Condition #161 - Scalp mode (Long).
        if long_entry_condition_index == 161:
          # Protections
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          long_entry_logic.append(df["protections_long_global"] == True)

          # 5m down move, 15m high
          long_entry_logic.append((_cmp("RSI_3", ">", 15.0)) | (_cmp("AROONU_14_15m", "<", 80.0)))
          # 15m & 1h down move, 4h high
          long_entry_logic.append((_cmp_cached_28) | (_cmp_cached_25) | (_cmp_cached_13))
          # 15m & 4h down move, 4h still high
          long_entry_logic.append((_cmp_cached_28) | (_cmp_cached_60) | (_cmp_cached_43))
          # 15m down move, 15m high
          long_entry_logic.append((_cmp_cached_28) | (_cmp("AROONU_14_15m", "<", 80.0)))
          # 15m down move, 4h still high, 1d high
          long_entry_logic.append(
            (_cmp_cached_28) | (_cmp_cached_54) | (_cmp_cached_38)
          )
          # 15m & 1h down move, 15m still high
          long_entry_logic.append((_cmp_cached_70) | (_cmp_cached_97) | (_cmp_cached_46))
          # 15m down move, 15m & 4h still high
          long_entry_logic.append(
            (_cmp_cached_70) | (_cmp_cached_75) | (_cmp_cached_54)
          )
          # 15m & 4h down move, 4h high
          long_entry_logic.append((_cmp_cached_100) | (_cmp_cached_87) | (_cmp_cached_20))
          # 15m & 1h down move, 1h high
          long_entry_logic.append((_cmp_cached_140) | (_cmp_cached_33) | (_cmp_cached_12))
          # 15m & 1h down move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_140) | (_cmp_cached_33) | (_cmp_cached_30)
          )
          # 15m & 1h down move, 4h high
          long_entry_logic.append((_cmp_cached_140) | (_cmp_cached_97) | (_cmp_cached_20))
          # 15m & 4h down move, 15m high
          long_entry_logic.append(
            (_cmp_cached_140) | (_cmp_cached_47) | (_cmp_cached_75)
          )
          # 15m & 4h down move, 15m high
          long_entry_logic.append(
            (_cmp_cached_140) | (_cmp_cached_87) | (_cmp_cached_108)
          )
          # 15m down move, 15m & 1h still high
          long_entry_logic.append(
            (_cmp_cached_140) | (_cmp_cached_46) | (_cmp_cached_30)
          )
          # 15m down move, 15m & 1h still high
          long_entry_logic.append(
            (_cmp_cached_140) | (_cmp_cached_75) | (_cmp_cached_30)
          )
          # 15m down move, 4h still high, 1d overbought
          long_entry_logic.append((_cmp_cached_140) | (_cmp_cached_43) | (_cmp_cached_29))
          # 15m & 1h down move, 1h still high
          long_entry_logic.append(
            (_cmp("RSI_3_15m", ">", 45.0)) | (_cmp_cached_65) | (_cmp_cached_82)
          )
          # 15m down move, 15m high, 1d overbought
          long_entry_logic.append((_cmp("RSI_3_15m", ">", 45.0)) | (_cmp_cached_90) | (_cmp_cached_35))
          # 15m down move, 15m high, 4h still high
          long_entry_logic.append(
            (_cmp("RSI_3_15m", ">", 45.0)) | (_cmp_cached_24) | (_cmp_cached_54)
          )
          # 15m down move, 15m still not low enough, 4h still high
          long_entry_logic.append(
            (_cmp("RSI_3_15m", ">", 45.0)) | (_cmp_cached_125) | (_cmp_cached_54)
          )
          # 15m down move, 15m & 1h still high
          long_entry_logic.append(
            (_cmp("RSI_3_15m", ">", 45.0)) | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 45.0)) | (_cmp_cached_82)
          )
          # 15m down move, 15m still not low enough, 4h high
          long_entry_logic.append(
            (_cmp("RSI_3_15m", ">", 50.0)) | (_cmp_cached_125) | (_cmp_cached_55)
          )
          # 15m down move, 15m still high, 1d overbought
          long_entry_logic.append((_cmp("RSI_3_15m", ">", 50.0)) | (_cmp_cached_46) | (_cmp_cached_35))
          # 15m down move, 15m still high, 1h high
          long_entry_logic.append(
            (_cmp("RSI_3_15m", ">", 55.0)) | (_cmp_cached_113) | (_cmp_cached_56)
          )
          # 15m down move, 15m still high, 4h high
          long_entry_logic.append(
            (_cmp("RSI_3_15m", ">", 55.0)) | (_cmp_cached_75) | (_cmp_cached_93)
          )
          # 15m down move, 15m & 1h still high
          long_entry_logic.append(
            (_cmp("RSI_3_15m", ">", 55.0)) | (_cmp_cached_75) | (_cmp_cached_30)
          )
          # 1h down move, 4h still high, 1d high
          long_entry_logic.append(
            (_cmp_cached_11) | (_cmp_cached_43) | (_cmp_cached_62)
          )
          # 1h & 4h down move, 1h still high
          long_entry_logic.append((_cmp_cached_8) | (_cmp("RSI_3_4h", ">", 65.0)) | (_cmp_cached_49))
          long_entry_logic.append(
            (_cmp_cached_8) | (_cmp_cached_82) | (_cmp_cached_62)
          )
          # 1h & 4h down move, 4h still high
          long_entry_logic.append(
            (_cmp_cached_25) | (_cmp_cached_131) | (_cmp_cached_54)
          )
          # 1h & 4h down move, 4h high
          long_entry_logic.append(
            (_cmp_cached_25) | (_cmp_cached_87) | (_cmp_cached_34)
          )
          # 1h down move, 15m & 1h still high
          long_entry_logic.append(
            (_cmp_cached_33) | (_cmp_cached_75) | (_cmp_cached_30)
          )
          # 1h down move, 1h still high, 4h high
          long_entry_logic.append(
            (_cmp_cached_33) | (_cmp_cached_30) | (_cmp_cached_58)
          )
          # 1h down move, 1h high
          long_entry_logic.append((_cmp_cached_33) | (_cmp_cached_112))
          # 1h down move, 4h & 1d high
          long_entry_logic.append((_cmp_cached_33) | (_cmp_cached_93) | (_cmp_cached_38))
          # 1h down move, 1h still high, 4h high
          long_entry_logic.append((_cmp_cached_65) | (_cmp_cached_49) | (_cmp_cached_32))
          # 1h down move, 1h still high, 1d high
          long_entry_logic.append((_cmp_cached_65) | (_cmp_cached_49) | (_cmp_cached_38))
          # 1h down move, 1h high
          long_entry_logic.append((_cmp_cached_65) | (_cmp_cached_112))
          # 1h & 4h down move, 15m high
          long_entry_logic.append((_cmp_cached_63) | (_cmp_cached_87) | (_cmp_cached_24))
          # 1h down move, 15m still high, 4h high
          long_entry_logic.append((_cmp_cached_63) | (_cmp_cached_46) | (_cmp_cached_20))
          # 1h down move, 15m high, 1h still high
          long_entry_logic.append(
            (_cmp_cached_63) | (_cmp_cached_24) | (_cmp_cached_82)
          )
          # 1h down move, 15m still high, 4h high
          long_entry_logic.append(
            (_cmp_cached_63) | (_cmp_cached_75) | (_cmp_cached_34)
          )
          # 1h down move, 15m & 1h high
          long_entry_logic.append(
            (_cmp_cached_63) | (_cmp("STOCHRSIk_14_14_3_3_15m", "<", 60.0)) | (_cmp_cached_88)
          )
          # 1h down move, 1h & 1d high
          long_entry_logic.append(
            (_cmp_cached_63) | (_cmp_cached_12) | (_cmp_cached_84)
          )
          # 1h down move, 4h still high, 1d high
          long_entry_logic.append(
            (_cmp_cached_63) | (_cmp_cached_54) | (_cmp_cached_62)
          )
          # 1h down move, 1h still high, 1d high
          long_entry_logic.append((_cmp_cached_63) | (_cmp_cached_49) | (_cmp_cached_38))
          # 1h down move, 4h overbought
          long_entry_logic.append((_cmp_cached_63) | (_cmp_cached_73))
          # 1h down move, 1h & 4h high
          long_entry_logic.append((_cmp_cached_130) | (_cmp_cached_12) | (_cmp_cached_14))
          # 1h down move, 5m up move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_97) | (_cmp("RSI_3", "<", 60.0)) | (_cmp_cached_30)
          )
          # 1h down move, 15m still not low enough, 4h high
          long_entry_logic.append(
            (_cmp_cached_97) | (_cmp_cached_24) | (_cmp_cached_55)
          )
          # 1h down move, 15m still not low enough, 1h high
          long_entry_logic.append(
            (_cmp_cached_97) | (_cmp_cached_125) | (_cmp_cached_12)
          )
          # 1h down move, 15m still not low enough, 1h high
          long_entry_logic.append(
            (_cmp_cached_97) | (_cmp_cached_125) | (_cmp_cached_112)
          )
          # 1h down move, 15m & 4h still high
          long_entry_logic.append(
            (_cmp_cached_97) | (_cmp_cached_75) | (_cmp_cached_54)
          )
          # 1h down move, 15m & 1h high
          long_entry_logic.append((_cmp_cached_97) | (_cmp_cached_24) | (_cmp_cached_52))
          # 1h down move, 1h still high, 4h high
          long_entry_logic.append(
            (_cmp_cached_97) | (_cmp_cached_49) | (_cmp_cached_55)
          )
          # 1h down move, 1h high, 4h still high
          long_entry_logic.append((_cmp_cached_97) | (_cmp_cached_18) | (_cmp_cached_67))
          # 1h down move, 1h still high, 4h high
          long_entry_logic.append(
            (_cmp_cached_97) | (_cmp_cached_82) | (_cmp_cached_13)
          )
          # 1h down move, 1h & 1d high
          long_entry_logic.append(
            (_cmp_cached_97) | (_cmp_cached_56) | (_cmp_cached_38)
          )
          # 1h down move, 4h & 1d high
          long_entry_logic.append((_cmp_cached_97) | (_cmp("RSI_14_4h", "<", 70.0)) | (_cmp("RSI_14_1d", "<", 80.0)))
          # 15m & 1h & 4h down move, 4h high
          long_entry_logic.append(
            (_cmp("RSI_3_15m", ">", 50.0)) | (_cmp("RSI_3_1h", ">", 65.0)) | (_cmp("RSI_3_4h", ">", 65.0)) | (_cmp_cached_93)
          )
          # 4h down move, 15m high
          long_entry_logic.append((_cmp_cached_6) | (_cmp("AROONU_14_15m", "<", 80.0)))
          # 4h down move, 1h high
          long_entry_logic.append((_cmp_cached_21) | (_cmp_cached_37))
          # 4h down move, 15m & 4h still high
          long_entry_logic.append((_cmp_cached_19) | (_cmp_cached_46) | (_cmp_cached_43))
          # 4h down move, 15m still high, 1d overbought
          long_entry_logic.append(
            (_cmp_cached_19) | (_cmp_cached_75) | (_cmp_cached_78)
          )
          # 4h down move, 1h & 4h still high
          long_entry_logic.append(
            (_cmp_cached_41) | (_cmp_cached_30) | (_cmp_cached_43)
          )
          # 4h down move, 1d high & overbought
          long_entry_logic.append(
            (_cmp_cached_41) | (_cmp_cached_84) | (_cmp_cached_40)
          )
          # 4h down move, 15m & 1h high
          long_entry_logic.append(
            (_cmp_cached_47) | (_cmp("AROONU_14_15m", "<", 80.0)) | (_cmp_cached_56)
          )
          # 4h down move, 1d high & overbought
          long_entry_logic.append((_cmp_cached_47) | (_cmp_cached_42) | (_cmp_cached_39))
          # 4h down move, 15m still high, 1h high
          long_entry_logic.append(
            (_cmp_cached_47) | (_cmp_cached_113) | (_cmp_cached_37)
          )
          # 4h down move, 1h & 4h still high
          long_entry_logic.append(
            (_cmp_cached_47) | (_cmp_cached_30) | (_cmp("RSI_14_4h", "<", 50.0))
          )
          # 4h down move, 1h still high, 4h still moving down
          long_entry_logic.append(
            (_cmp_cached_47) | (_cmp_cached_30) | (_cmp("CCI_20_change_pct_4h", ">", -0.0))
          )
          # 4h down move, 1d high & overbought
          long_entry_logic.append(
            (_cmp_cached_47) | (_cmp_cached_84) | (_cmp_cached_78)
          )
          # 4h down move, 1h high, 4h still high
          long_entry_logic.append((_cmp_cached_76) | (_cmp_cached_12) | (_cmp_cached_43))
          # 4h down move, 15m high, 4h still high
          long_entry_logic.append(
            (_cmp_cached_60) | (_cmp_cached_24) | (_cmp_cached_79)
          )
          # 4h down move, 15m still high, 1h high
          long_entry_logic.append(
            (_cmp_cached_60) | (_cmp_cached_113) | (_cmp_cached_56)
          )
          # 4h down move, 15m & 4h still high
          long_entry_logic.append(
            (_cmp_cached_60) | (_cmp_cached_75) | (_cmp_cached_43)
          )
          # 4h down move, 15m high, 4h still not low enough
          long_entry_logic.append(
            (_cmp_cached_60) | (_cmp_cached_108) | (_cmp_cached_94)
          )
          # 4h down move, 1h still high, 4h high
          long_entry_logic.append(
            (_cmp_cached_60) | (_cmp_cached_30) | (_cmp_cached_13)
          )
          # 4h down move, 15m & 1d high
          long_entry_logic.append((_cmp_cached_60) | (_cmp_cached_24) | (_cmp_cached_38))
          # 4h down move, 1d high & overbought
          long_entry_logic.append((_cmp_cached_60) | (_cmp_cached_38) | (_cmp_cached_39))
          # 4h down move, 15m & 4h high
          long_entry_logic.append((_cmp_cached_87) | (_cmp_cached_24) | (_cmp_cached_13))
          # 4h down move, 15m high, 4h still high
          long_entry_logic.append((_cmp_cached_87) | (_cmp("AROONU_14_15m", "<", 80.0)) | (_cmp_cached_67))
          # 4h down move, 15m still high, 1h high
          long_entry_logic.append(
            (_cmp_cached_87) | (_cmp_cached_75) | (_cmp_cached_12)
          )
          # 4h down move, 15m still high, 4h high
          long_entry_logic.append(
            (_cmp_cached_87) | (_cmp_cached_75) | (_cmp_cached_58)
          )
          # 4h down move, 15m & 4h high
          long_entry_logic.append(
            (_cmp_cached_87) | (_cmp_cached_108) | (_cmp_cached_105)
          )
          # 4h down move, 1h & 4h high
          long_entry_logic.append(
            (_cmp_cached_87) | (_cmp_cached_56) | (_cmp_cached_13)
          )
          # 4h down move, 4h still high, 1d high
          long_entry_logic.append(
            (_cmp_cached_87) | (_cmp_cached_54) | (_cmp_cached_84)
          )
          # 15m still high, 1d high & overbought
          long_entry_logic.append(
            (_cmp_cached_46) | (_cmp_cached_9) | (_cmp_cached_29)
          )
          # 15m high, 4h high
          long_entry_logic.append((_cmp_cached_24) | (_cmp_cached_93))
          # 15m & 1d high, 1d overbought
          long_entry_logic.append((_cmp_cached_24) | (_cmp_cached_38) | (_cmp_cached_39))
          # 15m & 1d high, 4h overbought
          long_entry_logic.append(
            (_cmp_cached_24) | (_cmp_cached_9) | (_cmp_cached_27)
          )
          # 15m high, 4h still high
          long_entry_logic.append((_cmp("AROONU_14_15m", "<", 80.0)) | (_cmp_cached_54))
          # 4h & 1d high, 1d overbought
          long_entry_logic.append(
            (_cmp_cached_14) | (_cmp_cached_9) | (_cmp_cached_39)
          )
          # 4h high, 4h overbought
          long_entry_logic.append((_cmp_cached_13) | (_cmp_cached_73))
          # 4h high, 1d overbought
          long_entry_logic.append((_cmp_cached_13) | (_cmp_cached_40))
          # 1d high, 4h overbought
          long_entry_logic.append((_cmp_cached_38) | (_cmp_cached_73))
          # 1d high & overbought
          long_entry_logic.append((_cmp_cached_9) | (_cmp_cached_74))
          # 15m high, 1h still high
          long_entry_logic.append((_cmp_cached_108) | (_cmp_cached_82))
          # 15m & 4h high
          long_entry_logic.append((_cmp_cached_108) | (_cmp_cached_13))
          # 15m high, 1d overbought
          long_entry_logic.append((_cmp_cached_108) | (_cmp_cached_78))
          # 15m high, 1h still not low enough
          long_entry_logic.append((_cmp("STOCHRSIk_14_14_3_3_15m", "<", 80.0)) | (_cmp_cached_109))
          # 1d high, 4h overbought
          long_entry_logic.append((_cmp_cached_84) | (_cmp_cached_73))
          # 1d high & overbought
          long_entry_logic.append((_cmp_cached_62) | (_cmp_cached_51))
          # 4h & 1d overbought
          long_entry_logic.append((_cmp_cached_73) | (_cmp_cached_40))
          # 1d green with top wick, 1d overbought
          long_entry_logic.append(
            (_cmp("change_pct_1d", "<", 25.0)) | (_cmp("top_wick_pct_1d", "<", 25.0)) | (_cmp_cached_35)
          )

          # Logic
          long_entry_logic.append(_cmp("RSI_14", "<", 50.0))
          long_entry_logic.append(_cmp("AROONU_14_15m", "<", 90.0))
          long_entry_logic.append(_cmp("STOCHRSIk_14_14_3_3_15m", "<", 90.0))
          long_entry_logic.append(
            (df["SMA_21"].shift(1) < df["SMA_200"].shift(1).infer_objects(copy=False).fillna(value=np.nan))
            & df["SMA_200"].shift(1).notna()
          )
          long_entry_logic.append(
            (df["SMA_21"] > df["SMA_200"].infer_objects(copy=False).fillna(value=np.nan)) & df["SMA_200"].notna()
          )
          long_entry_logic.append(
            (df["close"] > df["EMA_200_1h"].infer_objects(copy=False).fillna(value=np.nan)) & df["EMA_200_1h"].notna()
          )
          long_entry_logic.append(
            (df["close"] > df["EMA_200_4h"].infer_objects(copy=False).fillna(value=np.nan)) & df["EMA_200_4h"].notna()
          )
          long_entry_logic.append(_cmp("BBB_20_2.0", ">", 1.5))
          long_entry_logic.append(_cmp("BBB_20_2.0_1h", ">", 6.0))

        # Condition #162 - Scalp mode (Long).
        if long_entry_condition_index == 162:
          # Protections
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          long_entry_logic.append(df["protections_long_global"] == True)

          long_entry_logic.append(
            (_cmp_cached_104) & (_cmp_cached_17) & (_cmp("ROC_9_15m", ">", -10.0)) & (_cmp_cached_74)
          )

          long_entry_logic.append(
            # 15m & 1h down move, 4h high
            ((_cmp_cached_0) | (_cmp_cached_10) | (_cmp_cached_58))
            # 15m & 4h down move, 1h still high
            & ((_cmp_cached_0) | (_cmp_cached_47) | (_cmp("RSI_14_1h", "<", 50.0)))
            # 15m & 1d down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_53) | (_cmp_cached_32))
            # 15m down move, 15m still high, 1h high
            & ((_cmp_cached_0) | (_cmp_cached_46) | (_cmp_cached_18))
            # 15m down move, 15m high
            & ((_cmp_cached_0) | (_cmp_cached_24))
            # 15m down move, 1h & 1d high
            & ((_cmp_cached_0) | (_cmp_cached_52) | (_cmp_cached_9))
            # 15m down move, 4h & 1d high
            & ((_cmp_cached_0) | (_cmp("AROONU_14_4h", "<", 75.0)) | (_cmp_cached_9))
            # 15m down move, 1d high, 1d downtrend
            & ((_cmp_cached_0) | (_cmp_cached_103) | (_cmp("CMF_20_1d", ">", -0.40)))
            # 15m & 1h down move, 15m still not low enough
            & ((_cmp_cached_3) | (_cmp_cached_10) | (_cmp_cached_125))
            # 15m & 1h down nove, 1h still high
            & ((_cmp_cached_3) | (_cmp_cached_10) | (_cmp_cached_30))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_8) | (_cmp_cached_14))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_25) | (_cmp_cached_55))
            # 15m down move, 4h high, 4h downtrend
            & ((_cmp_cached_3) | (_cmp_cached_68) | (_cmp_cached_31))
            # 15m down move, 4h & 1d downtrend
            & ((_cmp_cached_3) | (_cmp_cached_102) | (_cmp_cached_44))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_16) | (_cmp_cached_11) | (_cmp_cached_12))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_16) | (_cmp_cached_13) | (_cmp_cached_26))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_28) | (_cmp_cached_11) | (_cmp_cached_55))
            # 15m down move, 15m high, 1d overbought
            & ((_cmp_cached_28) | (_cmp_cached_90) | (_cmp("ROC_9_1d", "<", 150.0)))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_100) | (_cmp_cached_18) | (_cmp("RSI_14_4h", "<", 80.0)))
            # 1h & 4h down move, 15m stil high
            & ((_cmp_cached_36) | (_cmp_cached_4) | (_cmp_cached_75))
            # 1h & 4h down move, 1h still high
            & ((_cmp_cached_36) | (_cmp_cached_21) | (_cmp_cached_86))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_22) | (_cmp_cached_6) | (_cmp_cached_68))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_22) | (_cmp_cached_19) | (_cmp_cached_32))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_22) | (_cmp_cached_68) | (_cmp_cached_78))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_1) | (_cmp_cached_4) | (_cmp_cached_43))
            # 1h & 3h down move, 1d high
            & ((_cmp_cached_1) | (_cmp_cached_47) | (_cmp_cached_42))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_2) | (_cmp_cached_6) | (_cmp_cached_13))
            # 1h down move, 1h downtrend, 1d overbought
            & ((_cmp_cached_2) | (_cmp_cached_124) | (_cmp_cached_69))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_10) | (_cmp_cached_41) | (_cmp_cached_13))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_2) | (_cmp_cached_21) | (_cmp_cached_23))
            # 1h down move, 1h & 1d high
            & ((_cmp_cached_2) | (_cmp_cached_88) | (_cmp_cached_103))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_2) | (_cmp_cached_88) | (_cmp_cached_35))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_2) | (_cmp_cached_62) | (_cmp_cached_40))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_88) | (_cmp_cached_29))
            # 1h down move, 1h high
            & ((_cmp_cached_11) | (_cmp_cached_52))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_8) | (_cmp_cached_41) | (_cmp_cached_58))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_8) | (_cmp_cached_88) | (_cmp_cached_98))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_25) | (_cmp_cached_34) | (_cmp_cached_50))
            # 1h down move, 1h high, 4h downtrend
            & ((_cmp_cached_33) | (_cmp_cached_37) | (_cmp_cached_31))
            # 1h down move, 15m still high, 1d overbought
            & ((_cmp_cached_65) | (_cmp_cached_46) | (_cmp_cached_35))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_65) | (_cmp_cached_27) | (_cmp_cached_35))
            # 1h down move,  4h high, 1d overbought
            & ((_cmp_cached_63) | (_cmp_cached_55) | (_cmp("ROC_9_1d", "<", 150.0)))
            # 4h down move, 1d high
            & ((_cmp_cached_80) | (_cmp_cached_38))
            # 4h down move, 15m still high
            & ((_cmp_cached_80) | (_cmp_cached_75))
            # 4h down move, 1d high
            & ((_cmp_cached_80) | (_cmp_cached_62))
            # 4h down move, 1d overbought
            & ((_cmp_cached_80) | (_cmp_cached_40))
            # 4h & 1d down move
            & ((_cmp_cached_57) | (_cmp_cached_66))
            # 4h down move, 1d high, 1h downtrend
            & ((_cmp_cached_4) | (_cmp_cached_103) | (_cmp_cached_124))
            # 4h down move, 1h & 4h downtrend
            & ((_cmp_cached_4) | (_cmp("ROC_9_1h", ">", -40.0)) | (_cmp_cached_139))
            # 4h & 1d down move, 4h still not low enough
            & ((_cmp_cached_6) | (_cmp_cached_53) | (_cmp_cached_94))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_19) | (_cmp_cached_43) | (_cmp_cached_44))
            # 4h down move, 15m still high, 1d overbought
            & ((_cmp_cached_47) | (_cmp_cached_46) | (_cmp_cached_35))
            # 4h down move, 4h & 1d overbought
            & ((_cmp_cached_47) | (_cmp_cached_27) | (_cmp_cached_35))
            # 1d down move, 1h high
            & ((_cmp("RSI_3_1d", ">", 3.0)) | (_cmp_cached_56))
            # 1d down move, 15m still high
            & ((_cmp("RSI_3_1d", ">", 3.0)) | (_cmp_cached_46))
            # 1d down move, 15m still high, 1h high
            & ((_cmp_cached_66) | (_cmp_cached_81) | (_cmp_cached_56))
            # 1d down move, 1h & 4h high
            & ((_cmp_cached_66) | (_cmp_cached_12) | (_cmp_cached_32))
            # 1d down move, 4h high
            & ((_cmp_cached_53) | (_cmp("RSI_14_4h", "<", 80.0)))
            # 1d downtrend, 1d high & overbought
            & ((_cmp("CMF_20_1d", ">", -0.30)) | (_cmp_cached_103) | (_cmp_cached_29))
            # 1h & 4h high, 1d overbought
            & ((_cmp_cached_12) | (_cmp_cached_13) | (_cmp_cached_51))
            # 1h & 4h high, 1d overbought
            & ((_cmp_cached_52) | (_cmp_cached_32) | (_cmp_cached_39))
            # 1h & 4h high
            & ((_cmp_cached_71) | (_cmp_cached_14))
            # 4h & 1d high, 4h overbought
            & ((_cmp_cached_20) | (_cmp_cached_9) | (_cmp_cached_50))
            # 4h high, 4h & 1d overbought
            & ((_cmp_cached_20) | (_cmp_cached_26) | (_cmp_cached_39))
            # 1d still high, 1h & 4h downtrend
            & ((_cmp_cached_121) | (_cmp_cached_120) | (_cmp_cached_31))
            # 1h high, 1h overbought
            & ((_cmp_cached_37) | (_cmp("ROC_9_1h", "<", 50.0)))
            # 1h high, 1d downtrend
            & ((_cmp_cached_37) | (_cmp_cached_146))
            # 4h high, 1h overbought, 1d downtrend
            & ((_cmp_cached_34) | (_cmp_cached_61) | (_cmp_cached_150))
            # 4h high, 1h & 4h overbought
            & ((_cmp_cached_55) | (_cmp_cached_85) | (_cmp_cached_98))
            # 1h & 4h overbought
            & ((_cmp("ROC_9_1h", "<", 100.0)) | (_cmp_cached_115))
            # 1h P&D, 1h down move
            & ((_cmp("change_pct_1h", ">", -10.0)) | (df["change_pct_1h"].shift(12) < 10.0) | (_cmp_cached_63))
            # 4h P&D, 4h high
            & ((_cmp("change_pct_4h", ">", -15.0)) | (df["change_pct_4h"].shift(48) < 30.0) | (_cmp_cached_32))
            # 4h green, 15m & 1h down move
            & ((_cmp("change_pct_4h", "<", 10.0)) | (_cmp_cached_0) | (_cmp_cached_25))
            # 4h green, 1h down move
            & ((_cmp("change_pct_4h", "<", 40.0)) | (_cmp_cached_63))
            # 4h green with top wick
            & ((_cmp("change_pct_4h", "<", 50.0)) | (_cmp("change_pct_4h", "<", 50.0)))
            # 1d green with top wick, 15m still high
            & ((_cmp("change_pct_1d", "<", 10.0)) | (_cmp("top_wick_pct_1d", "<", 8.0)) | (_cmp_cached_46))
            # 1d green, 4h down move, 4h still high
            & ((_cmp("change_pct_1d", "<", 40.0)) | (_cmp_cached_41) | (_cmp_cached_43))
            # 1d green with top wick, 4h down move
            & ((_cmp("change_pct_1d", "<", 40.0)) | (_cmp("top_wick_pct_1d", "<", 8.0)) | (_cmp_cached_131))
            # 1d top wick, 4h still high
            & ((_cmp("top_wick_pct_1d", "<", 50.0)) | (_cmp_cached_43))
            # big drop in last 4 days, 1d down move
            & (_gt_mul("close", "high_max_24_4h", 0.20) | (_cmp_cached_53))
            # big drop in the last 20 days, 4h down move
            & (_gt_mul("close", "high_max_20_1d", 0.15) | (_cmp_cached_6))
            # big drop in the last 20 days, 1d down move
            & (_gt_mul("close", "high_max_20_1d", 0.05) | (_cmp_cached_53))
            # big drop in the last 20 days, 1h still high
            & (_gt_mul("close", "high_max_20_1d", 0.05) | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 45.0)))
            # big drop in the last 20 days, 4h high
            & (_gt_mul("close", "high_max_20_1d", 0.05) | (_cmp_cached_58))
          )

          # Logic
          long_entry_logic.append(
            (_cmp("AROONU_14", "<", 25.0))
            & (_cmp("AROOND_14", ">", 75.0))
            & (_cmp("STOCHRSIk_14_14_3_3", "<", 30.0))
            & (df["EMA_26"] > df["EMA_12"])
            & ((df["EMA_26"] - df["EMA_12"]) > (df["open"] * 0.030))
            & _ema_26_12_spread_gt_open_pct
            & (df["close"] < df["SMA_9"])
          )

        # Condition #163 - Scalp mode (Long).
        if long_entry_condition_index == 163:
          # Protections
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          long_entry_logic.append(df["protections_long_global"] == True)

          long_entry_logic.append((_cmp_cached_143) & (_cmp_cached_0) & (_cmp_cached_10))

          long_entry_logic.append(
            # 5m & 15m & 4h down mnove, 4h high
            ((_cmp("RSI_3", ">", 15.0)) | (_cmp_cached_16) | (_cmp_cached_47) | (_cmp_cached_20))
            # 5m & 15m & 1d down move, 1h high
            & ((_cmp("RSI_3", ">", 15.0)) | (_cmp_cached_28) | (_cmp_cached_64) | (_cmp_cached_52))
            # 5m & 1h down move, 15m still high, 4h high
            & (
              (_cmp("RSI_3", ">", 20.0)) | (_cmp_cached_33) | (_cmp("RSI_14_15m", "<", 40.0)) | (_cmp_cached_14)
            )
            # 5m & 1h & 15m down move, 1h still not low enough
            & ((_cmp("RSI_3", ">", 15.0)) | (_cmp_cached_8) | (_cmp_cached_59) | (_cmp_cached_138))
            # 15m & 4h down move, 4h high
            & ((_cmp("RSI_3", ">", 15.0)) | (_cmp_cached_41) | (_cmp_cached_58))
            # 5m & 4h down move, 15m high
            & ((_cmp("RSI_3", ">", 15.0)) | (_cmp_cached_76) | (_cmp_cached_90))
            # 15m & 1h down move, 1h high
            & ((_cmp("RSI_3_15m", ">", 12.0)) | (_cmp_cached_33) | (_cmp_cached_71))
            # 15m & 1h & 4h & 1d down move
            & ((_cmp_cached_3) | (_cmp_cached_11) | (_cmp_cached_21) | (_cmp_cached_64))
            # 15m & 1h down move, 1h & 4h high
            & (
              (_cmp_cached_3)
              | (_cmp_cached_11)
              | (_cmp("AROONU_14_1h", "<", 75.0))
              | (_cmp_cached_14)
            )
            # 15m & 1h & 4h down move, 1d overbought
            & ((_cmp_cached_3) | (_cmp_cached_8) | (_cmp_cached_41) | (_cmp_cached_40))
            # 15m & 1h & 4h down move, 1h downtrend, 4h high
            & (
              (_cmp_cached_3)
              | (_cmp_cached_8)
              | (_cmp_cached_131)
              | (_cmp("CMF_20_1h", ">", -0.10))
              | (_cmp_cached_20)
            )
            # 15m & 1h down move, 15m high
            & ((_cmp_cached_3) | (_cmp_cached_8) | (_cmp_cached_90))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_8) | (_cmp("RSI_14_4h", "<", 85.0)))
            # 15m & 1h down move, 15m still high
            & ((_cmp_cached_3) | (_cmp_cached_8) | (_cmp_cached_81))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_8) | (_cmp_cached_12))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_8) | (_cmp_cached_56))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_3) | (_cmp_cached_8) | (_cmp_cached_51))
            # 15m & 1h & 4h down move, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_25) | (_cmp("RSI_3_4h", ">", 65.0)) | (_cmp("MFI_14_4h", "<", 85.0)))
            # 15m & 1h & 1d down move, 15m high
            & (
              (_cmp_cached_3)
              | (_cmp_cached_25)
              | (_cmp_cached_118)
              | (_cmp_cached_90)
            )
            # 15m & 1h down move, 15m high
            & ((_cmp_cached_3) | (_cmp_cached_25) | (_cmp_cached_24))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_25) | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 85.0)))
            # 15m & 1h down move, 15m still not low enough, 1h & 4h high
            & (
              (_cmp_cached_3)
              | (_cmp_cached_33)
              | (_cmp_cached_111)
              | (_cmp_cached_18)
              | (_cmp_cached_20)
            )
            # 15m & 1h down move, 4h high & overbought
            & ((_cmp_cached_3) | (_cmp_cached_65) | (_cmp("RSI_14_4h", "<", 70.0)) | (_cmp_cached_98))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_63) | (_cmp_cached_83))
            # 15m & 4h down move, 15m high
            & ((_cmp_cached_3) | (_cmp_cached_19) | (_cmp_cached_90))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_19) | (_cmp_cached_20))
            # 15m & 4h down move, 1h still high
            & ((_cmp_cached_3) | (_cmp_cached_47) | (_cmp_cached_86))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_3) | (_cmp_cached_41) | (_cmp_cached_62))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_41) | (_cmp_cached_112))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_60) | (_cmp_cached_37))
            # 15m down move, 4h & 1d up move, 1d downtrend
            & ((_cmp_cached_3) | (_cmp_cached_126) | (_cmp("RSI_3_1d", "<", 80.0)) | (_cmp("CMF_20_1d", ">", -0.2)))
            # 15m & 1d down move, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_66) | (_cmp_cached_58))
            # 15m & 1h down move, 1h & 4h still high
            & (
              (_cmp_cached_3)
              | (_cmp_cached_59)
              | (_cmp_cached_49)
              | (_cmp_cached_43)
            )
            # 15m & 1d down move, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_59) | (_cmp_cached_71))
            # 15m & 1d down move, 1d high
            & ((_cmp_cached_3) | (_cmp_cached_53) | (_cmp_cached_42))
            # 15m & 1d down move, 1d overbought
            & ((_cmp_cached_3) | (_cmp_cached_118) | (_cmp_cached_35))
            # 15m & 1d down move, 1d high
            & ((_cmp_cached_3) | (_cmp("RSI_3_1d", ">", 50.0)) | (_cmp_cached_45))
            # 15m & 1d down move, 1d high
            & ((_cmp_cached_3) | (_cmp("RSI_3_1d", ">", 60.0)) | (_cmp_cached_84))
            # 15m down move, 15m & 4h high
            & ((_cmp_cached_3) | (_cmp_cached_24) | (_cmp_cached_20))
            # 15m down move, 15m & 1h high
            & ((_cmp_cached_3) | (_cmp("AROONU_14_15m", "<", 75.0)) | (_cmp_cached_71))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_3) | (_cmp_cached_52) | (_cmp_cached_69))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_3) | (_cmp_cached_71) | (_cmp_cached_40))
            # 15m down move, 4h still high, 4h downtrend
            & ((_cmp_cached_3) | (_cmp_cached_67) | (_cmp_cached_31))
            # 15m down move, 1d high & overbought
            & ((_cmp_cached_3) | (_cmp_cached_9) | (_cmp_cached_29))
            # 15m down move, 15m still not low enough, 4h high
            & (
              (_cmp_cached_3) | (_cmp_cached_125) | (_cmp_cached_54)
            )
            # 15m down move, 15m & 1h high
            & (
              (_cmp_cached_3) | (_cmp_cached_75) | (_cmp_cached_30)
            )
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_3) | (_cmp_cached_56) | (_cmp_cached_51))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_3) | (_cmp_cached_56) | (_cmp("ROC_9_1d", "<", 150.0)))
            # 15m down move, 1h high & overbought
            & ((_cmp_cached_3) | (_cmp_cached_37) | (_cmp_cached_85))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_3) | (_cmp_cached_37) | (_cmp_cached_29))
            # 15m down move, 4h high, 1d overbought
            & ((_cmp_cached_3) | (_cmp_cached_34) | (_cmp("ROC_9_1d", "<", 25.0)))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_3) | (_cmp_cached_55) | (_cmp("ROC_9_4h", "<", 25.0)))
            # 15m down move, 4h high
            & (
              (_cmp_cached_3)
              | (_cmp("RSI_14_4h", "<", 70.0))
              | (_cmp_cached_55)
              | (df["EMA_9"] < (df["EMA_26"] * 0.972))
            )
            # 15m down move, 4h high and downtrend
            & ((_cmp_cached_3) | (_cmp("CMF_20_4h", ">", -0.2)) | (_cmp_cached_20))
            # 15m down move, 1h high, 4h overbought
            & ((_cmp_cached_3) | (_cmp_cached_52) | (_cmp_cached_26))
            # 15m down move, 4h & 1d downtrend
            & ((_cmp_cached_3) | (_cmp_cached_31) | (_cmp_cached_15))
            # 16m & 1h down move, 1h still high
            & ((_cmp_cached_16) | (_cmp_cached_11) | (_cmp_cached_82))
            # 15m & 1h down move, 1h downtrend, 1h downtrend, 15m still high, 1h high
            & (
              (_cmp_cached_16)
              | (_cmp_cached_25)
              | (_cmp("CMF_20_1h", ">", -0.10))
              | (_cmp_cached_81)
              | (_cmp_cached_92)
            )
            # 15m & 1h down move, 4h high & overbought
            & ((_cmp_cached_16) | (_cmp_cached_65) | (_cmp("RSI_14_4h", "<", 70.0)) | (_cmp_cached_98))
            # 15m & 4h down move, 15m high
            & ((_cmp_cached_16) | (_cmp_cached_21) | (_cmp_cached_90))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_16) | (_cmp_cached_41) | (_cmp_cached_71))
            # 15m & 1d down move, 4h high
            & ((_cmp_cached_16) | (_cmp_cached_53) | (_cmp_cached_58))
            # 15m down move, 15m still high, 4h high
            & (
              (_cmp_cached_16)
              | (_cmp("RSI_14_15m", "<", 40.0))
              | (_cmp("RSI_14_4h", "<", 75.0))
              | (_cmp_cached_14)
            )
            # 15m down move, 4h downtrend, 4h overbought
            & ((_cmp_cached_16) | (_cmp("CMF_20_4h", ">", -0.0)) | (_cmp_cached_73))
            # 15m down move, 1h & 4h high, 1f overbought
            & (
              (_cmp_cached_16)
              | (_cmp_cached_92)
              | (_cmp("RSI_14_4h", "<", 70.0))
              | (_cmp_cached_69)
            )
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_16) | (_cmp_cached_52) | (_cmp_cached_14))
            # 15m down move, 1d high, 4h overbought
            & ((_cmp_cached_16) | (_cmp_cached_9) | (_cmp_cached_50))
            # 15m down move, 1h high & overbought
            & ((_cmp_cached_16) | (_cmp_cached_37) | (_cmp_cached_61))
            # 15m & 1d down move, 1d high
            & ((_cmp_cached_28) | (_cmp_cached_118) | (_cmp_cached_42))
            # 15m down move, 4h high, 1d downtrend
            & ((_cmp_cached_28) | (_cmp_cached_55) | (_cmp_cached_23))
            # 15m & 1h down move, 15m still not low enough, 1h & 4h high
            & (
              (_cmp_cached_70)
              | (_cmp_cached_65)
              | (_cmp("RSI_14_15m", "<", 30.0))
              | (_cmp("RSI_14_1h", "<", 50.0))
              | (_cmp("RSI_14_4h", "<", 70.0))
              | (_cmp("AROONU_14_15m", "<", 20.0))
              | (_cmp_cached_88)
              | (_cmp_cached_14)
            )
            # 15m & 4h down move, 4h overbought
            & ((_cmp_cached_70) | (_cmp_cached_87) | (_cmp_cached_123))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_100) | (_cmp_cached_41) | (_cmp_cached_34))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_11) | (_cmp_cached_19) | (_cmp_cached_84))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_11) | (_cmp_cached_47) | (_cmp_cached_13))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_11) | (_cmp_cached_76) | (_cmp_cached_34))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_11) | (_cmp("RSI_3_4h", ">", 65.0)) | (_cmp_cached_9))
            # 1h & 1d down move, 1d high
            & ((_cmp_cached_11) | (_cmp_cached_118) | (_cmp_cached_45))
            # 1h down move, 15m downtrend, 4h still high
            & ((_cmp_cached_11) | (_cmp("CMF_20_15m", ">", -0.4)) | (_cmp_cached_43))
            # 1h down move, 4h downtrend, 4h high
            & ((_cmp_cached_11) | (_cmp("CMF_20_4h", ">", -0.25)) | (_cmp_cached_13))
            # 1h down move, 15m still high, 1d downtrend
            & ((_cmp_cached_11) | (_cmp_cached_81) | (_cmp_cached_15))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_11) | (_cmp_cached_88) | (_cmp_cached_14))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_11) | (_cmp_cached_52) | (_cmp("CMF_20_1d", ">", -0.2)))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_11) | (_cmp_cached_32) | (_cmp_cached_26))
            # 1h down move, 1h still not low enough, 1d downtrend
            & ((_cmp_cached_11) | (_cmp_cached_109) | (_cmp_cached_44))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_55) | (_cmp("ROC_9_1d", "<", 25.0)))
            # 1h & 4h down move, 1h still high
            & ((_cmp_cached_8) | (_cmp_cached_19) | (_cmp_cached_86))
            # 1h & 1d down move, 1d still high
            & ((_cmp_cached_8) | (_cmp_cached_77) | (_cmp_cached_135))
            # 1h down move, 15m & 4h high
            & ((_cmp_cached_8) | (_cmp_cached_90) | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 95.0)))
            # 1h down move, 15m & 4h high
            & ((_cmp_cached_8) | (_cmp_cached_24) | (_cmp_cached_32))
            # 1h down move, 1h high
            & ((_cmp_cached_8) | (_cmp("MFI_14_1h", "<", 80.0)) | (_cmp_cached_52))
            # 1h down move, 1h still high, 1d overbought
            & ((_cmp_cached_8) | (_cmp_cached_49) | (_cmp_cached_40))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_8) | (_cmp_cached_18) | (_cmp_cached_14))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_8) | (_cmp_cached_52) | (_cmp("CMF_20_1d", ">", -0.2)))
            # 1h down move, 1h highm 1d overbought
            & ((_cmp_cached_8) | (_cmp_cached_52) | (_cmp_cached_40))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_8) | (_cmp_cached_14) | (_cmp_cached_50))
            # 1h down move, 1d high, 4h overbought
            & ((_cmp_cached_8) | (_cmp_cached_9) | (_cmp_cached_26))
            # 1h & 4h down move, 1h still high, 4h high
            & ((_cmp_cached_25) | (_cmp_cached_87) | (_cmp("RSI_14_1h", "<", 50.0)) | (_cmp("RSI_14_4h", "<", 70.0)))
            # 1h down move, 15m still not low enough, 1h high
            & ((_cmp_cached_25) | (_cmp_cached_111) | (_cmp_cached_18))
            # 1h down move, 1h & 1d high
            & ((_cmp_cached_25) | (_cmp_cached_88) | (_cmp_cached_9))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_25) | (_cmp_cached_12) | (_cmp("ROC_9_4h", "<", 25.0)))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_25) | (_cmp_cached_12) | (_cmp_cached_32))
            # 1h down move, 1h & 1d high
            & ((_cmp_cached_25) | (_cmp_cached_52) | (_cmp_cached_38))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_25) | (_cmp_cached_26) | (_cmp_cached_69))
            # 1h & 1d down move, 1d high
            & ((_cmp_cached_33) | (_cmp("RSI_3_1d", ">", 55.0)) | (_cmp_cached_9))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_33) | (_cmp_cached_12) | (_cmp_cached_73))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_33) | (_cmp_cached_18) | (_cmp_cached_20))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_33) | (_cmp_cached_92) | (_cmp_cached_69))
            # 1h down move, 1h high, 15m downtrend
            & ((_cmp_cached_33) | (_cmp_cached_52) | (_cmp("ROC_9_15m", ">", -10.0)))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_33) | (_cmp_cached_37) | (_cmp_cached_44))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_65) | (_cmp("RSI_3_4h", ">", 65.0)) | (_cmp_cached_74))
            # 1h & 1d down move, 4h high
            & ((_cmp_cached_65) | (_cmp("RSI_3_1d", ">", 50.0)) | (_cmp_cached_55))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_65) | (_cmp_cached_71) | (_cmp_cached_27))
            # 1h & 4h down move, 1h & 4h high
            & (
              (_cmp_cached_63)
              | (_cmp("RSI_3_4h", ">", 65.0))
              | (_cmp_cached_92)
              | (_cmp_cached_14)
            )
            # 1h down move, 15m & 1h high
            & ((_cmp_cached_63) | (_cmp_cached_90) | (_cmp_cached_37))
            # 1h down move, 4h & 1d high
            & ((_cmp_cached_63) | (_cmp_cached_32) | (_cmp_cached_38))
            # 1h down move, 4h high, 1h overbought
            & ((_cmp_cached_130) | (_cmp_cached_14) | (_cmp_cached_85))
            # 1h down move, 15m & 1h high, 1d downtrend
            & (
              (_cmp_cached_97)
              | (_cmp("AROONU_14_15m", "<", 65.0))
              | (_cmp_cached_37)
              | (_cmp("CMF_20_1d", ">", -0.0))
            )
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_97) | (_cmp_cached_83) | (_cmp_cached_15))
            # 4h down move, 15m high
            & ((_cmp_cached_80) | (_cmp_cached_46))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_4) | (_cmp("RSI_3_1d", ">", 50.0)) | (_cmp_cached_38))
            # 4h down move, 15m still not low enough, 4h downtrend
            & ((_cmp_cached_4) | (_cmp_cached_111) | (_cmp("CMF_20_4h", ">", -0.30)))
            # 4h down move, 15m & 1h still not low enough
            & ((_cmp_cached_4) | (_cmp_cached_111) | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 25.0)))
            # 4h down move, 4h still high
            & ((_cmp_cached_4) | (_cmp_cached_67))
            # 4h down move, 1h still high, 4h downtrend
            & ((_cmp_cached_4) | (_cmp_cached_30) | (_cmp("CMF_20_4h", ">", -0.3)))
            # 4h down move, 1d still high, 1d downtrend
            & ((_cmp_cached_5) | (_cmp("RSI_14_1d", "<", 40.0)) | (_cmp_cached_142))
            # 4h down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_68))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_5) | (_cmp_cached_62) | (_cmp_cached_39))
            # 4h down move, 15m still high, 1d overbought
            & ((_cmp_cached_6) | (_cmp_cached_81) | (_cmp_cached_39))
            # 4h & 1d down move, 1h & 4h low
            & ((_cmp_cached_21) | (_cmp_cached_64) | (_cmp("CMF_20_1h", ">", -0.3)) | (_cmp("CMF_20_4h", ">", -0.4)))
            # 4h down move, 4h still high 1d downtrend
            & ((_cmp_cached_21) | (_cmp_cached_43) | (_cmp_cached_15))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_21) | (_cmp_cached_84) | (_cmp("ROC_9_1d", "<", 25.0)))
            # 4h down move, 4h & 1d high
            & ((_cmp_cached_41) | (_cmp_cached_13) | (_cmp_cached_9))
            # 4h down move, 15m still high, 1d overbought
            & ((_cmp_cached_47) | (_cmp_cached_46) | (_cmp_cached_35))
            # 4h down move, 4h high, 1d overbought
            & ((_cmp_cached_47) | (_cmp_cached_20) | (_cmp_cached_39))
            # 4h down move, 1h high, 1d downtrend
            & ((_cmp_cached_47) | (_cmp_cached_37) | (_cmp_cached_15))
            # 4h down move, 4h & 1d overbought
            & ((_cmp_cached_47) | (_cmp_cached_27) | (_cmp_cached_35))
            # 4h down move, 4h high, 1d overbought
            & ((_cmp_cached_76) | (_cmp_cached_13) | (_cmp_cached_39))
            # 4h down move, 1d high, 4h overbought
            & ((_cmp_cached_76) | (_cmp_cached_38) | (_cmp_cached_27))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_60) | (_cmp_cached_110) | (_cmp_cached_23))
            # 4h down move, 4h high & overbought
            & ((_cmp_cached_60) | (_cmp_cached_93) | (_cmp_cached_27))
            # 4h down move, 15m still high, 1d overbought
            & ((_cmp_cached_131) | (_cmp_cached_81) | (_cmp_cached_29))
            # 4h & 1d down move, 4h high, 1d overbought
            & (
              (_cmp_cached_87) | (_cmp("RSI_3_1d", ">", 60.0)) | (_cmp("AROONU_14_4h", "<", 75.0)) | (_cmp_cached_40)
            )
            # 4h down move, 4h & 1d high
            & ((_cmp("RSI_3_4h", ">", 70.0)) | (_cmp_cached_32) | (_cmp_cached_9))
            # 1d down move, 4h high
            & ((_cmp("RSI_3_1d", ">", 3.0)) | (_cmp_cached_105))
            # 1d down move, 1h high
            & ((_cmp("RSI_3_1d", ">", 5.0)) | (_cmp_cached_37))
            # 1d down move, 15m & 1h still high
            & ((_cmp_cached_66) | (_cmp("RSI_14_15m", "<", 40.0)) | (_cmp_cached_30))
            # 1d down move, 1h & 4h high
            & ((_cmp_cached_66) | (_cmp_cached_18) | (_cmp_cached_32))
            # 1d down move, 1h & 4h still high
            & ((_cmp_cached_66) | (_cmp_cached_82) | (_cmp_cached_67))
            # 1d down move, 1h high & overbought
            & ((_cmp_cached_53) | (_cmp_cached_37) | (_cmp_cached_85))
            # 1d down move, 1d high & overbought
            & ((_cmp_cached_118) | (_cmp_cached_45) | (_cmp_cached_39))
            # 1d down move, 4h high & overbought
            & ((_cmp_cached_107) | (_cmp_cached_20) | (_cmp_cached_50))
            # 1d down move, 1h high, 1d overbought
            & ((_cmp("RSI_3_1d", ">", 60.0)) | (_cmp_cached_18) | (_cmp_cached_69))
            # 1d down move, 15m still high, 1d overbought
            & ((_cmp("RSI_3_1d", ">", 65.0)) | (_cmp_cached_81) | (_cmp_cached_29))
            # 1d down move, 4h & 1d high
            & ((_cmp("RSI_3_1d", ">", 65.0)) | (_cmp_cached_27) | (_cmp_cached_78))
            # 5m still high, 1h down move, 15m still high, 1h high
            & (
              (_cmp("RSI_3", "<", 40.0))
              | (_cmp_cached_8)
              | (_cmp_cached_46)
              | (_cmp_cached_32)
            )
            # 5m still high, 15m high
            & ((_cmp("RSI_3", "<", 45.0)) | (_cmp_cached_24))
            # 5m still high, 1h down move, 4h high
            & ((_cmp("RSI_3", "<", 50.0)) | (_cmp_cached_8) | (_cmp_cached_14))
            # 15m down move, 1h high
            & ((_cmp("RSI_14_15m", ">", 25.0)) | (_cmp_cached_37))
            # 15m down move, 4h & 1d high
            & (
              (_cmp("RSI_14_15m", ">", 30.0)) | (_cmp_cached_55) | (_cmp_cached_106)
            )
            # 1h downtrend, 4h high, 1d downtrend
            & ((_cmp("CMF_20_1h", ">", -0.2)) | (_cmp_cached_55) | (_cmp("CMF_20_1d", ">", -0.25)))
            # 15m & 1h high, 1d overbought
            & ((_cmp_cached_90) | (_cmp_cached_71) | (_cmp_cached_39))
            # 4h high, 4h & 1d overbought
            & ((_cmp_cached_20) | (_cmp_cached_26) | (_cmp_cached_39))
            # 4h & 1d high, 1d overbought
            & ((_cmp_cached_93) | (_cmp_cached_103) | (_cmp_cached_99))
            # 4h & 1d high, 1d overbought
            & ((_cmp_cached_14) | (_cmp_cached_9) | (_cmp_cached_51))
            # 1d still high, 4h & 1d downtrend
            & ((_cmp_cached_121) | (_cmp_cached_31) | (_cmp_cached_23))
            # 4h top wick, 15m & 1h down move
            & ((_cmp("top_wick_pct_4h", "<", 10.0)) | (_cmp_cached_3) | (_cmp_cached_33))
            # 4h top wick, 1h down move, 1h high
            & ((_cmp("top_wick_pct_4h", "<", 10.0)) | (_cmp_cached_8) | (_cmp_cached_12))
            # 1d red, 1h down move, 1h still high
            & ((_cmp("change_pct_1d", ">", -15.0)) | (_cmp_cached_11) | (_cmp_cached_49))
            # 1d P&D, 1h high
            & (
              (_cmp("change_pct_1d", ">", -15.0))
              | (df["change_pct_1d"].shift(288) < 15.0)
              | (_cmp_cached_37)
            )
            # 1d P&D, 1d downtrend
            & ((_cmp("change_pct_1d", ">", -5.0)) | (df["change_pct_1d"].shift(288) < 30.0) | (_cmp("CMF_20_1d", ">", -0.1)))
            # 1d P&D, 15m high
            & ((_cmp("change_pct_1d", ">", -10.0)) | (df["change_pct_1d"].shift(288) < 40.0) | (_cmp_cached_46))
            # 1d P&D, 1h high
            & (
              (_cmp("change_pct_1d", ">", -10.0))
              | (df["change_pct_1d"].shift(288) < 40.0)
              | (_cmp_cached_56)
            )
            # 1d red with top wick, 1h high
            & ((_cmp("change_pct_1d", ">", -10.0)) | (_cmp("top_wick_pct_1d", "<", 10.0)) | (_cmp_cached_18))
            # 1d green, 4m down move, 4h high
            & ((_cmp("change_pct_1d", "<", 25.0)) | (_cmp_cached_131) | (_cmp_cached_43))
            # 1d green with top wick, 1d low
            & ((_cmp("change_pct_1d", "<", 25.0)) | (_cmp("top_wick_pct_1d", "<", 10.0)) | (_cmp("CMF_20_1d", ">", -0.2)))
            # 1d top wick, 1h still high
            & ((_cmp("top_wick_pct_1d", "<", 25.0)) | (_cmp_cached_49))
            # 1d top wick, 4h still high
            & ((_cmp("top_wick_pct_1d", "<", 30.0)) | (_cmp_cached_54))
            # 1d top wick, 1h down move
            & ((_cmp("top_wick_pct_1d", "<", 50.0)) | (_cmp_cached_8))
            # big drop in the last 12 days, 1h down move, 1h high
            & (_gt_mul("close", "high_max_12_1d", 0.35) | (_cmp_cached_25) | (_cmp_cached_12))
            # big drop in the last 20 days, 1h down move, 1h high
            & (
              _gt_mul("close", "high_max_20_1d", 0.30)
              | (_cmp_cached_8)
              | (_cmp("STOCHRSIk_14_14_3_3_1h", "<", 75.0))
            )
            # big drop in the last 20 days, 1d high, 1d downtrend
            & (
              _gt_mul("close", "high_max_20_1d", 0.20)
              | (_cmp_cached_106)
              | (_cmp_cached_141)
            )
          )

          # Logic
          long_entry_logic.append(
            (_cmp("RSI_14", "<", 30.0))
            & (_cmp("AROONU_14", "<", 25.0))
            & (_cmp("AROOND_14", ">", 75.0))
            & (_cmp("STOCHRSIk_14_14_3_3", "<", 20.0))
            & (df["EMA_9"] < (df["EMA_26"] * 0.982))
            & (df["close"] < df["SMA_9"])
          )

        ###############################################################################################

        # LONG ENTRY CONDITIONS ENDS HERE

        ###############################################################################################

        long_entry_logic.append(_cmp("volume", ">", 0))
        item_long_entry = _and_conditions(long_entry_logic)
        _append_entry_tag(entry_tags, item_long_entry, f"{long_entry_condition_index} ")
        long_entry_conditions.append(item_long_entry)

    if long_entry_conditions:
      df.loc[:, "enter_long"] = _or_conditions(long_entry_conditions).astype(int)

    ###############################################################################################

    # SHORT ENTRY CONDITIONS STARTS HERE

    ###############################################################################################

    #   ______  __    __  ______  _______ ________        ________ __    __ ________ ________ _______
    #  /      \|  \  |  \/      \|       |        \      |        |  \  |  |        |        |       \
    # |  $$$$$$| $$  | $|  $$$$$$| $$$$$$$\$$$$$$$$      | $$$$$$$| $$\ | $$\$$$$$$$| $$$$$$$| $$$$$$$\
    # | $$___\$| $$__| $| $$  | $| $$__| $$ | $$         | $$__   | $$$\| $$  | $$  | $$__   | $$__| $$
    #  \$$    \| $$    $| $$  | $| $$    $$ | $$         | $$  \  | $$$$\ $$  | $$  | $$  \  | $$    $$
    #  _\$$$$$$| $$$$$$$| $$  | $| $$$$$$$\ | $$         | $$$$$  | $$\$$ $$  | $$  | $$$$$  | $$$$$$$\
    # |  \__| $| $$  | $| $$__/ $| $$  | $$ | $$         | $$_____| $$ \$$$$  | $$  | $$_____| $$  | $$
    #  \$$    $| $$  | $$\$$    $| $$  | $$ | $$         | $$     | $$  \$$$  | $$  | $$     | $$  | $$
    #   \$$$$$$ \$$   \$$ \$$$$$$ \$$   \$$  \$$          \$$$$$$$$\$$   \$$   \$$   \$$$$$$$$\$$   \$$
    #

    for enabled_short_entry_signal in self.short_entry_signal_params:
      short_entry_condition_index = int(enabled_short_entry_signal.split("_")[3])
      item_short_buy_protection_list = [True]
      if self.short_entry_signal_params[f"{enabled_short_entry_signal}"]:
        # Short Entry Conditions Starts Here
        # -----------------------------------------------------------------------------------------
        # IMPORTANT: Short Condition Descriptions are not for shorts. These are for longs but completely mirrored opposite side
        # Please dont change these comment descriptions. With these descriptions we are comparing long/short positions.

        short_entry_logic = []
        short_entry_logic.append(_and_conditions(item_short_buy_protection_list))

        # Condition #501 - Normal mode (Short).
        if short_entry_condition_index == 501:
          # Protections
          short_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          short_entry_logic.append(df["protections_short_global"] == True)
          short_entry_logic.append(df["global_protections_short_pump"] == True)
          short_entry_logic.append(df["global_protections_short_dump"] == True)

          short_entry_logic.append(_cmp("RSI_3_1h", ">=", 5.0))
          short_entry_logic.append(_cmp("RSI_3_4h", ">=", 20.0))
          short_entry_logic.append(_cmp("RSI_3_1d", ">=", 20.0))
          short_entry_logic.append(_cmp("RSI_14_1h", ">", 20.0))
          short_entry_logic.append(_cmp("RSI_14_4h", ">", 20.0))
          short_entry_logic.append(_cmp("RSI_14_1d", ">", 10.0))
          # 5m up move, 4h still not high enough
          short_entry_logic.append((_cmp("RSI_3", "<", 97.0)) | (_cmp("AROONU_14_4h", ">", 60.0)))
          # 5m up move, 4h still low
          short_entry_logic.append((_cmp("RSI_3", "<", 97.0)) | (_cmp_cached_122))
          # 5m & 15m strong up move
          short_entry_logic.append((_cmp("RSI_3", "<", 95.0)) | (_cmp_cached_89))
          # 5m & 1h up move, 1d uptrend
          short_entry_logic.append((_cmp("RSI_3", "<", 95.0)) | (_cmp_cached_101) | (_cmp_cached_29))
          # 5m up move, 15m & 1h still not high enough
          short_entry_logic.append((_cmp("RSI_3", "<", 95.0)) | (_cmp("AROOND_14_15m", "<", 25.0)) | (_cmp("AROOND_14_1h", "<", 25.0)))
          # 4m up move, 1h & 4h still low
          short_entry_logic.append(
            (_cmp("RSI_3", "<", 95.0)) | (_cmp_cached_147) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 70.0))
          )
          # 4m & 1h up move, 1h still low
          short_entry_logic.append(
            (_cmp("RSI_3", "<", 90.0)) | (_cmp_cached_128) | (_cmp_cached_119)
          )
          # 15m & 1h up move, 4h low
          short_entry_logic.append((_cmp("RSI_3", "<", 90.0)) | (_cmp_cached_128) | (_cmp("AROONU_14_4h", ">", 20.0)))
          # 5m up move, 15m & 1h uptrend
          short_entry_logic.append((_cmp("RSI_3", "<", 90.0)) | (_cmp("CMF_20_15m", "<", 0.30)) | (_cmp("CMF_20_1h", "<", 0.30)))
          # 5m up move, 15m stil low
          short_entry_logic.append((_cmp("RSI_3", "<", 90.0)) | (_cmp("AROONU_14_15m", ">", 50.0)))
          # 5m up move, 15m & 1h still not high enough
          short_entry_logic.append(
            (_cmp("RSI_3", "<", 90.0)) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 60.0)) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 75.0))
          )
          # 15m up move, 1h low
          short_entry_logic.append((_cmp("RSI_3_15m", "<", 97.0)) | (_cmp("AROONU_14_1h", ">", 30.0)))
          # 15m & 1h up move, 4h still going up
          short_entry_logic.append(
            (_cmp_cached_89) | (_cmp_cached_91) | (_cmp("CCI_20_change_pct_4h", "<", -0.0))
          )
          # 15m & 1h up move, 4h still not high enough
          short_entry_logic.append(
            (_cmp_cached_89) | (_cmp_cached_101) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 80.0))
          )
          # 15m & 1h up move, 4h still not high enough
          short_entry_logic.append(
            (_cmp_cached_89) | (_cmp_cached_136) | (_cmp_cached_122)
          )
          # 15m & 1h up move, 1h still low
          short_entry_logic.append(
            (_cmp_cached_89) | (_cmp("RSI_3_1h", "<", 70.0)) | (_cmp_cached_119)
          )
          # 15m & 4h up move, 1h still not high enough
          short_entry_logic.append(
            (_cmp_cached_89) | (_cmp_cached_144) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 75.0))
          )
          # 15m up move, 1d lost, 1h low
          short_entry_logic.append((_cmp_cached_89) | (_cmp("RSI_14_1d", ">", 40.0)) | (_cmp("AROONU_14_1h", ">", 40.0)))
          # 15m up move, 15m & 4h uptrend
          short_entry_logic.append(
            (_cmp_cached_89) | (_cmp("AROONU_14_15m", "<", 90.0)) | (_cmp_cached_32)
          )
          # 15m up move, 15m stil not high enough, 1h low
          short_entry_logic.append(
            (_cmp_cached_89) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 70.0)) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 10.0))
          )
          # 15m up move, 1h still not high enough, 4h low
          short_entry_logic.append(
            (_cmp_cached_89) | (_cmp_cached_147) | (_cmp("AROONU_14_4h", ">", 20.0))
          )
          # 15m up move, 1h & 4h still not high enough
          short_entry_logic.append(
            (_cmp_cached_89) | (_cmp_cached_147) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 80.0))
          )
          # 15m up move, 4h still not high enough
          short_entry_logic.append((_cmp_cached_89) | (_cmp("AROONU_14_4h", ">", 70.0)))
          # 15m up move, 4h & 1d uptrend
          short_entry_logic.append((_cmp_cached_89) | (_cmp_cached_50) | (_cmp_cached_35))
          # 15m up move, 1h up move, 1h still not high enough
          short_entry_logic.append(
            (_cmp_cached_89) | (_cmp("RSI_3_change_pct_1h", "<", 80.0)) | (_cmp_cached_119)
          )
          # 15m & 1h up move, 1h still not high enough
          short_entry_logic.append(
            (_cmp_cached_96) | (_cmp_cached_136) | (_cmp_cached_147)
          )
          # 15m & 1h up move, 1h not high enough
          short_entry_logic.append((_cmp_cached_96) | (_cmp_cached_101) | (_cmp("AROOND_14_1h", "<", 50.0)))
          # 15m & 1h up move, 1d stil not high enough
          short_entry_logic.append((_cmp_cached_96) | (_cmp_cached_101) | (_cmp("RSI_14_1h", ">", 80.0)))
          # 15m & 1h up move, 1d uptrend
          short_entry_logic.append((_cmp_cached_96) | (_cmp_cached_128) | (_cmp_cached_40))
          # 15m & 1h up move, 15m still not high enough
          short_entry_logic.append(
            (_cmp_cached_96) | (_cmp_cached_128) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 60.0))
          )
          # 15m & 4h up move, 1h still not high enough
          short_entry_logic.append(
            (_cmp_cached_96) | (_cmp_cached_126) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 80.0))
          )
          # 15m & 4h up move, 1h still not high enough
          short_entry_logic.append(
            (_cmp_cached_96) | (_cmp_cached_126) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 90.0))
          )
          # 15m & 4h up move, 4h not high enough
          short_entry_logic.append((_cmp_cached_96) | (_cmp_cached_126) | (_cmp("AROOND_14_4h", "<", 50.0)))
          # 15m & 4h up move, 1d low
          short_entry_logic.append(
            (_cmp_cached_96) | (_cmp_cached_116) | (_cmp("STOCHRSIk_14_14_3_3_1d", ">", 30.0))
          )
          # 15m & 4h up move, 1h low
          short_entry_logic.append(
            (_cmp_cached_96) | (_cmp("RSI_3_4h", "<", 70.0)) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 20.0))
          )
          # 15m & 4h up move, 4h low
          short_entry_logic.append((_cmp_cached_96) | (_cmp("RSI_3_4h", "<", 60.0)) | (_cmp("AROONU_14_4h", ">", 30.0)))
          # 15m up move, 1h & 4h low
          short_entry_logic.append(
            (_cmp_cached_96) | (_cmp("AROONU_14_1h", ">", 40.0)) | (_cmp("AROONU_14_4h", ">", 10.0))
          )
          # 15m up move, 1h still low, 4h low
          short_entry_logic.append(
            (_cmp_cached_96) | (_cmp("AROONU_14_1h", ">", 60.0)) | (_cmp_cached_137)
          )
          # 15m up move, 1h low, 4h still not high enough
          short_entry_logic.append(
            (_cmp_cached_96) | (_cmp_cached_148) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 70.0))
          )
          # 15m & 4h up move, 1d low
          short_entry_logic.append(
            (_cmp_cached_96) | (_cmp("RSI_3_4h", "<", 70.0)) | (_cmp("STOCHRSIk_14_14_3_3_1d", ">", 20.0))
          )
          # 15m & 1h up move, 4h low
          short_entry_logic.append(
            (_cmp_cached_127) | (_cmp_cached_136) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 20.0))
          )
          # 15m & 1h up move, 1d still low
          short_entry_logic.append(
            (_cmp_cached_127) | (_cmp_cached_136) | (_cmp("STOCHRSIk_14_14_3_3_1d", ">", 60.0))
          )
          # 15m & 1h up move, 1h low
          short_entry_logic.append(
            (_cmp_cached_127) | (_cmp("RSI_3_1h", "<", 70.0)) | (_cmp_cached_148)
          )
          # 15m & 1h up move, 4h low
          short_entry_logic.append(
            (_cmp_cached_127) | (_cmp("RSI_3_1h", "<", 70.0)) | (_cmp_cached_137)
          )
          # 15m & 4h down move, 4h still not high enough
          short_entry_logic.append(
            (_cmp_cached_127) | (_cmp_cached_126) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 75.0))
          )
          # 15m & 4h up move, 15m low
          short_entry_logic.append(
            (_cmp_cached_127) | (_cmp_cached_116) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 50.0))
          )
          # 15m down move, 15m still not high enough, 4h low
          short_entry_logic.append(
            (_cmp_cached_127) | (_cmp("RSI_14_15m", ">", 70.0)) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 40.0))
          )
          # 15m up move, 4h overbought
          short_entry_logic.append((_cmp_cached_127) | (_cmp_cached_98))
          # 15m & 1h up move, 1h still not high enough
          short_entry_logic.append((_cmp("RSI_3_15m", "<", 80.0)) | (_cmp("RSI_3_1h", "<", 70.0)) | (_cmp("AROONU_14_1h", ">", 60.0)))
          # 15m & 4h up move, 15m still low
          short_entry_logic.append((_cmp("RSI_3_15m", "<", 80.0)) | (_cmp("RSI_3_4h", "<", 80.0)) | (_cmp("AROONU_14_15m", ">", 50.0)))
          # 15m up move, 1h low
          short_entry_logic.append((_cmp("RSI_3_15m", "<", 80.0)) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 20.0)))
          # 15m & 1h up move, 1h low
          short_entry_logic.append((_cmp("RSI_3_15m", "<", 70.0)) | (_cmp("RSI_3_1h", "<", 70.0)) | (_cmp("AROONU_14_1h", ">", 30.0)))
          # 15m up move, 15m still not high enough, 1h still low
          short_entry_logic.append(
            (_cmp("RSI_3_15m", "<", 70.0)) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 90.0)) | (_cmp_cached_119)
          )
          # 1h & 4h up move, 1h still not high enough
          short_entry_logic.append(
            (_cmp_cached_91) | (_cmp_cached_144) | (_cmp_cached_147)
          )
          # 1h up move, 4h low
          short_entry_logic.append((_cmp_cached_91) | (_cmp_cached_137))
          # 1h & 4h up move, 4h still not high enough
          short_entry_logic.append((_cmp_cached_91) | (_cmp_cached_144) | (_cmp("UO_7_14_28_4h", ">", 60.0)))
          # 1h & 4h up move, 4h still low
          short_entry_logic.append(
            (_cmp_cached_91) | (_cmp_cached_116) | (_cmp_cached_122)
          )
          # 1h & 4h up move, 4h uptrend
          short_entry_logic.append((_cmp_cached_91) | (_cmp_cached_116) | (_cmp_cached_73))
          # 1h & 1d strong up move
          short_entry_logic.append((_cmp_cached_91) | (_cmp("RSI_3_1d", "<", 95.0)))
          # 1h up move, 4h still low
          short_entry_logic.append((_cmp_cached_91) | (_cmp("RSI_14_4h", ">", 60.0)))
          # 1h up move, 1d still low, 1h uptrend
          short_entry_logic.append((_cmp_cached_91) | (_cmp("RSI_14_1d", ">", 50.0)) | (_cmp_cached_129))
          # 1h & 4h strong up move
          short_entry_logic.append((_cmp_cached_91) | (_cmp("MFI_14_1h", "<", 95.0)) | (_cmp_cached_144))
          # 1h up move, 1d still low, 1h uptrend
          short_entry_logic.append(
            (_cmp_cached_91) | (_cmp("STOCHRSIk_14_14_3_3_1d", ">", 50.0)) | (_cmp_cached_85)
          )
          # 1h strong up move, 15m still move higher
          short_entry_logic.append((_cmp_cached_91) | (_cmp("CCI_20_change_pct_15m", "<", -0.0)))
          # 1h & 4h up move, 1h still low
          short_entry_logic.append(
            (_cmp_cached_101) | (_cmp_cached_126) | (_cmp_cached_119)
          )
          # 1h & 4h up move, 1d still not high enough
          short_entry_logic.append(
            (_cmp_cached_101) | (_cmp_cached_126) | (_cmp("STOCHRSIk_14_14_3_3_1d", ">", 70.0))
          )
          # 1h up move, 4h low, 1d overbought
          short_entry_logic.append((_cmp_cached_101) | (_cmp("AROONU_14_4h", ">", 20.0)) | (_cmp_cached_35))
          # 1h up move, 1h still low, 1d uptrend
          short_entry_logic.append(
            (_cmp_cached_101) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 60.0)) | (_cmp_cached_35)
          )
          # 1h up move, 1h still not high enough, 1d low
          short_entry_logic.append(
            (_cmp_cached_101) | (_cmp_cached_147) | (_cmp("STOCHRSIk_14_14_3_3_1d", ">", 30.0))
          )
          # 1h up move, 4h low, 1h uptrend
          short_entry_logic.append(
            (_cmp_cached_101) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 20.0)) | (_cmp_cached_61)
          )
          # 1h up move, 4h low, 1h overbought
          short_entry_logic.append(
            (_cmp_cached_101) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 40.0)) | (_cmp_cached_129)
          )
          # 1h up move, 15m & 1h uptrend
          short_entry_logic.append((_cmp_cached_101) | (_cmp("ROC_9_15m", "<", 15.0)) | (_cmp("ROC_9_1h", "<", 15.0)))
          # 1h up move, 15m & 4h still low
          short_entry_logic.append(
            (_cmp_cached_136) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 50.0)) | (_cmp_cached_122)
          )
          # 1h & 4h up move, 15m still not high enough
          short_entry_logic.append((_cmp_cached_136) | (_cmp_cached_116) | (_cmp("AROOND_14_15m", "<", 50.0)))
          # 1h & 4h up move, 15m still not high enough
          short_entry_logic.append(
            (_cmp_cached_136) | (_cmp_cached_116) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 90.0))
          )
          # 1h up move, 15m still not high enough, 1h still low
          short_entry_logic.append(
            (_cmp_cached_128) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 80.0)) | (_cmp_cached_119)
          )
          # 1h up move, 1h still low
          short_entry_logic.append((_cmp_cached_128) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 60.0)))
          # 4h & 1d strong up move
          short_entry_logic.append((_cmp_cached_144) | (_cmp("RSI_3_1d", "<", 95.0)))
          # 4h up move, 15m still low, 1h not high enough
          short_entry_logic.append(
            (_cmp_cached_144) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 50.0)) | (_cmp("AROOND_14_1h", "<", 25.0))
          )
          # 4h up move, 15m still not high enough, 4h overbought
          short_entry_logic.append(
            (_cmp_cached_144) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 70.0)) | (_cmp_cached_123)
          )
          # 4h up move, 15m uptrend
          short_entry_logic.append((_cmp_cached_144) | (_cmp("ROC_9_15m", "<", 20.0)))
          # 4h up move, 1h uptrend
          short_entry_logic.append((_cmp_cached_144) | (_cmp_cached_85))
          # 4h up move, 1h & 4h overbought
          short_entry_logic.append((_cmp_cached_144) | (_cmp_cached_129) | (_cmp_cached_123))
          # 4h up move, 1h still low
          short_entry_logic.append((_cmp_cached_126) | (_cmp("AROONU_14_1h", ">", 40.0)))
          # 4h up move, 1d still low, 4h uptrend
          short_entry_logic.append((_cmp_cached_116) | (_cmp("RSI_14_1d", ">", 40.0)) | (_cmp_cached_26))
          # 4h up move, 4h still low
          short_entry_logic.append((_cmp("RSI_3_4h", "<", 80.0)) | (_cmp_cached_122))
          # 4h up move, 1h low
          short_entry_logic.append((_cmp("RSI_3_4h", "<", 70.0)) | (_cmp("AROONU_14_1h", ">", 25.0)))
          # 4h up move, 1d low
          short_entry_logic.append((_cmp("RSI_3_4h", "<", 70.0)) | (_cmp("AROONU_14_1d", ">", 20.0)))
          # 4h up move, 1h low
          short_entry_logic.append((_cmp("RSI_3_4h", "<", 70.0)) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 20.0)))
          # 4h up move, 1d low
          short_entry_logic.append((_cmp("RSI_3_4h", "<", 70.0)) | (_cmp("STOCHRSIk_14_14_3_3_1d", ">", 20.0)))
          # 1d up move, 1h & 4h still not low enough
          short_entry_logic.append(
            (_cmp("RSI_3_1d", "<", 90.0)) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 80.0)) | (_cmp_cached_122)
          )
          # 4h still not high enough, 4h overbought, 4h uptrend
          short_entry_logic.append(
            (_cmp("RSI_14_4h", ">", 80.0)) | (_cmp_cached_73) | (_cmp("CCI_20_change_pct_4h", "<", 0.0))
          )
          # 15m & 1h uptrend, 4h still low
          short_entry_logic.append(
            (_cmp("CMF_20_15m", "<", 0.30)) | (_cmp("CMF_20_1h", "<", 0.30)) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 60.0))
          )
          # 15m uptrend, 1h low
          short_entry_logic.append((_cmp("AROONU_14_15m", "<", 100.0)) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 20.0)))
          # 1h & 4h uptrend
          short_entry_logic.append((_cmp_cached_71) | (_cmp_cached_14))
          # 1h uptrend, 4h uptrend
          short_entry_logic.append((_cmp_cached_71) | (_cmp_cached_26))
          # 4h uptrend, 1d uptrend
          short_entry_logic.append((_cmp_cached_14) | (_cmp_cached_9))
          # 4h uptrend, 15m uptrend
          short_entry_logic.append((_cmp_cached_14) | (_cmp("ROC_9_15m", "<", 10.0)))
          # 4h uptrend, 1h uptrend
          short_entry_logic.append((_cmp_cached_14) | (_cmp_cached_85))
          # 1d uptrend, 15m uptrend
          short_entry_logic.append((_cmp_cached_9) | (_cmp("ROC_9_15m", "<", 20.0)))
          # 1d uptrend, 1h uptrend
          short_entry_logic.append((_cmp_cached_9) | (_cmp_cached_85))
          # 15m still not high enough, 1h & 4h overbought
          short_entry_logic.append(
            (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 70.0)) | (_cmp_cached_129) | (_cmp_cached_123)
          )
          # 1h & 4h overbought, 1h uptrend
          short_entry_logic.append(
            (_cmp_cached_61) | (_cmp_cached_73) | (_cmp("CCI_20_change_pct_1h", "<", 0.0))
          )
          # 1h & 4h overbought, 4h uptrend
          short_entry_logic.append(
            (_cmp_cached_61) | (_cmp_cached_73) | (_cmp("CCI_20_change_pct_4h", "<", 0.0))
          )
          # 1h & 4h & 1d uptrend
          short_entry_logic.append((_cmp_cached_61) | (_cmp_cached_27) | (_cmp_cached_39))
          # 5m green, 15m still not high enough
          short_entry_logic.append((_cmp("change_pct", "<", 5.0)) | (_cmp("AROOND_14_15m", "<", 50.0)))
          # 5m green, 15m still not high enough
          short_entry_logic.append((_cmp("change_pct", "<", 5.0)) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 90.0)))
          # pump in the last half hour, 1h low
          short_entry_logic.append((df["close"] < (df["close_min_6"] * 1.20)) | (_cmp("AROONU_14_1h", ">", 30.0)))
          # pump in the last half hour, 15m still low
          short_entry_logic.append((df["close"] < (df["close_min_6"] * 1.20)) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 40.0)))
          # pump in the last half hour, 1d uptrend
          short_entry_logic.append((df["close"] < (df["close_min_6"] * 1.20)) | (_cmp_cached_39))
          # big pump in the last 4 hours, 15m still low
          short_entry_logic.append((df["close"] < (df["close_min_48"] * 1.50)) | (_cmp("AROONU_14_15m", ">", 50.0)))

          # Logic
          short_entry_logic.append(df["EMA_12"] > df["EMA_26"])
          short_entry_logic.append((df["EMA_12"] - df["EMA_26"]) > (df["open"] * 0.030))
          short_entry_logic.append(_ema_12_26_spread_gt_open_pct)
          short_entry_logic.append(_gt_mul("close", "BBU_20_2.0", 1.004))

        # Condition #502 - Normal mode (Short).
        if short_entry_condition_index == 502:
          # Protections
          short_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          short_entry_logic.append(df["protections_short_global"] == True)

          # 5m & 15m & 1h & 4h up move
          short_entry_logic.append(
            (_cmp("RSI_3", "<", 97.0)) | (_cmp_cached_96) | (_cmp_cached_101) | (_cmp("RSI_3_4h", "<", 80.0))
          )
          # 5m & 4h up move
          short_entry_logic.append((_cmp("RSI_3", "<", 97.0)) | (_cmp_cached_144))
          # 5m up move, 4h still not high enough
          short_entry_logic.append((_cmp("RSI_3", "<", 97.0)) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 80.0)))
          # 5m & 15m strong up move
          short_entry_logic.append((_cmp("RSI_3", "<", 95.0)) | (_cmp_cached_89))
          # 5m & 15m up move, 4h low
          short_entry_logic.append((_cmp("RSI_3", "<", 95.0)) | (_cmp_cached_96) | (_cmp("AROONU_14_4h", ">", 30.0)))
          # 5m & 1h & 4h up move
          short_entry_logic.append((_cmp("RSI_3", "<", 95.0)) | (_cmp_cached_101) | (_cmp_cached_126))
          # 5m & 1h up move, 15m still not high enough
          short_entry_logic.append(
            (_cmp("RSI_3", "<", 95.0)) | (_cmp_cached_136) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 70.0))
          )
          # 5m up move, 15m still low
          short_entry_logic.append((_cmp("RSI_3", "<", 95.0)) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 50.0)))
          # 5m up move, 4h low
          short_entry_logic.append((_cmp("RSI_3", "<", 90.0)) | (_cmp("AROONU_14_4h", ">", 20.0)))
          # 15m & 1h down move, 4h still not high enough
          short_entry_logic.append(
            (_cmp("RSI_3_15m", "<", 97.0)) | (_cmp_cached_136) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 80.0))
          )
          # 15m up move, 1h still low
          short_entry_logic.append((_cmp("RSI_3_15m", "<", 97.0)) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 60.0)))
          # 15m & 1h & 4h up move
          short_entry_logic.append((_cmp_cached_89) | (_cmp_cached_101) | (_cmp_cached_116))
          # 15m & 1h up move, 4h still low
          short_entry_logic.append(
            (_cmp_cached_89) | (_cmp_cached_136) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 60.0))
          )
          # 15m up move, 1h still low
          short_entry_logic.append((_cmp_cached_89) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 40.0)))
          # 15m up move, 4h still not high enough
          short_entry_logic.append((_cmp_cached_89) | (_cmp("AROONU_14_4h", ">", 70.0)))
          # 15m & 1h & 4h up move
          short_entry_logic.append((_cmp_cached_96) | (_cmp_cached_101) | (_cmp_cached_126))
          # 15m & 1h up move, 15m still not high enough
          short_entry_logic.append(
            (_cmp_cached_96) | (_cmp_cached_101) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 80.0))
          )
          # 15m & 1h up move, 1d low
          short_entry_logic.append(
            (_cmp_cached_96) | (_cmp_cached_101) | (_cmp("STOCHRSIk_14_14_3_3_1d", ">", 40.0))
          )
          # 15m & 1h up move, 1h still not high enough
          short_entry_logic.append(
            (_cmp_cached_96) | (_cmp_cached_136) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 80.0))
          )
          # 15m & 1h up move, 4h stil low
          short_entry_logic.append((_cmp_cached_96) | (_cmp_cached_128) | (_cmp("AROONU_14_4h", ">", 50.0)))
          # 15m & 4h up move, 1d low
          short_entry_logic.append((_cmp_cached_96) | (_cmp_cached_116) | (_cmp("RSI_14_1d", ">", 40.0)))
          # 15m & 4h up move, 1d low
          short_entry_logic.append(
            (_cmp_cached_96) | (_cmp_cached_116) | (_cmp("STOCHRSIk_14_14_3_3_1d", ">", 30.0))
          )
          # 15m up move, 1h still low, 1d low
          short_entry_logic.append(
            (_cmp_cached_96) | (_cmp("AROONU_14_1h", ">", 50.0)) | (_cmp("AROONU_14_1d", ">", 30.0))
          )
          # 15m up move, 1h high
          short_entry_logic.append((_cmp_cached_96) | (_cmp_cached_71))
          # 15m up move, 1h still low
          short_entry_logic.append((_cmp_cached_96) | (_cmp_cached_119))
          # 15m up move, 4h uptrend
          short_entry_logic.append((_cmp_cached_96) | (_cmp_cached_26))
          # 15m & 1h up move, 1h still low
          short_entry_logic.append(
            (_cmp_cached_127) | (_cmp("RSI_3_1h", "<", 65.0)) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 60.0))
          )
          # 15m up move, 1h low
          short_entry_logic.append((_cmp_cached_127) | (_cmp_cached_148))
          # 15m & 4h up move, 15m still low
          short_entry_logic.append((_cmp("RSI_3_15m", "<", 80.0)) | (_cmp("RSI_3_4h", "<", 75.0)) | (_cmp("AROONU_14_15m", ">", 50.0)))
          # 15m up move, 1h low
          short_entry_logic.append((_cmp("RSI_3_15m", "<", 80.0)) | (_cmp("AROONU_14_1h", ">", 10.0)))
          # 15m up move, 1h low, 1d uptrend
          short_entry_logic.append((_cmp("RSI_3_15m", "<", 80.0)) | (_cmp("AROONU_14_1h", ">", 40.0)) | (_cmp_cached_29))
          # 15m up move, 4h low
          short_entry_logic.append((_cmp("RSI_3_15m", "<", 80.0)) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 40.0)))
          # 15m up move, 1h uptrend
          short_entry_logic.append((_cmp("RSI_3_15m", "<", 75.0)) | (_cmp_cached_134))
          # 1h & 1d strong up move
          short_entry_logic.append((_cmp_cached_91) | (_cmp("RSI_3_1d", "<", 95.0)))
          # 1h up move, 1h still not high enough
          short_entry_logic.append((_cmp_cached_91) | (_cmp_cached_147))
          # 1h up move, 4h still low, 1h moving higher
          short_entry_logic.append(
            (_cmp_cached_91) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 60.0)) | (_cmp("CCI_20_change_pct_1h", "<", -0.0))
          )
          # 1h up move, 1d low
          short_entry_logic.append((_cmp_cached_91) | (_cmp("RSI_14_1d", ">", 40.0)))
          # 1h strong up move, 15m still move higher
          short_entry_logic.append((_cmp_cached_91) | (_cmp("CCI_20_change_pct_15m", "<", -0.0)))
          # 1h up move, relative stable before the hour
          short_entry_logic.append((_cmp_cached_91) | (df["close_min_12"] > (df["close_min_48"] * 1.10)))
          # 1h up move, 15m uptrend
          short_entry_logic.append((_cmp_cached_101) | (_cmp("AROONU_14_15m", "<", 100.0)))
          # 1h up move, 1d low
          short_entry_logic.append((_cmp_cached_101) | (_cmp("STOCHRSIk_14_14_3_3_1d", ">", 10.0)))
          # 1h up move, 1h & 4h uptrend
          short_entry_logic.append((_cmp_cached_101) | (_cmp_cached_129) | (_cmp_cached_50))
          # 1h up move, 4h uptrend
          short_entry_logic.append((_cmp_cached_101) | (_cmp_cached_26))
          # 1h up move, 4h still low
          short_entry_logic.append((_cmp_cached_136) | (_cmp("AROONU_14_4h", ">", 50.0)))
          # 1h & 4h up move, 1d low
          short_entry_logic.append(
            (_cmp_cached_128) | (_cmp("RSI_3_4h", "<", 80.0)) | (_cmp("STOCHRSIk_14_14_3_3_1d", ">", 30.0))
          )
          # 1h up move, 1h still not high enough
          short_entry_logic.append((_cmp_cached_128) | (_cmp_cached_147))
          # 1h up move, 4h still low, 1h still moving higher
          short_entry_logic.append(
            (_cmp_cached_128) | (_cmp("RSI_14_4h", ">", 60.0)) | (_cmp("CCI_20_change_pct_1h", "<", -0.0))
          )
          # 1h up move, 4h low
          short_entry_logic.append((_cmp_cached_128) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 20.0)))
          # 1h up move, 4h low
          short_entry_logic.append((_cmp_cached_128) | (_cmp("AROONU_14_4h", ">", 10.0)))
          # 1h up move, 1h still low
          short_entry_logic.append((_cmp("RSI_3_1h", "<", 75.0)) | (_cmp_cached_119))
          # 1h up move, 4h low
          short_entry_logic.append((_cmp("RSI_3_1h", "<", 70.0)) | (_cmp("RSI_14_4h", ">", 40.0)))
          # 1h up move, 4h low
          short_entry_logic.append((_cmp("RSI_3_1h", "<", 70.0)) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 40.0)))
          # 1h up move, 1h uptrend
          short_entry_logic.append((_cmp("RSI_3_1h", "<", 70.0)) | (_cmp_cached_134))
          # 1h up move, 1h low
          short_entry_logic.append((_cmp("RSI_3_1h", "<", 60.0)) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 20.0)))
          # 4h up move, 1d still low
          short_entry_logic.append((_cmp("RSI_3_4h", "<", 97.0)) | (_cmp("RSI_14_1d", ">", 50.0)))
          # 4h up move, 1h still not high enough
          short_entry_logic.append((_cmp_cached_144) | (_cmp_cached_147))
          # 4h up move, 4h still not high enough
          short_entry_logic.append((_cmp_cached_144) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 80.0)))
          # 4h up move, 15m still not high enough, 4h moving higher
          short_entry_logic.append(
            (_cmp_cached_126) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 80.0)) | (_cmp("CCI_20_change_pct_4h", "<", 0.0))
          )
          # 4h up move, 15m still low
          short_entry_logic.append((_cmp_cached_126) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 50.0)))
          # 4h up move, 1h still low
          short_entry_logic.append((_cmp_cached_126) | (_cmp("AROONU_14_1h", ">", 40.0)))
          # 4h up move, 4h still not high enough
          short_entry_logic.append((_cmp_cached_126) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 75.0)))
          # 4h up move, 4h still not high enough
          short_entry_logic.append((_cmp_cached_116) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 70.0)))
          # 4h up move, 1d still low, 4h uptrend
          short_entry_logic.append((_cmp_cached_116) | (_cmp("RSI_14_1d", ">", 50.0)) | (_cmp_cached_26))
          # 4h up move, 4h uptrend
          short_entry_logic.append((_cmp("RSI_3_4h", "<", 80.0)) | (_cmp_cached_26))
          # 4h up move, 1h low
          short_entry_logic.append((_cmp("RSI_3_4h", "<", 75.0)) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 20.0)))
          # 4h up move, 4h low
          short_entry_logic.append((_cmp("RSI_3_4h", "<", 70.0)) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 40.0)))
          # 1d up move, 1h still not high enough
          short_entry_logic.append((_cmp("RSI_3_1d", "<", 95.0)) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 90.0)))
          # 1d up move, 1h still low
          short_entry_logic.append((_cmp("RSI_3_1d", "<", 90.0)) | (_cmp_cached_119))
          # 1d up move, 4h still low
          short_entry_logic.append((_cmp("RSI_3_1d", "<", 80.0)) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 40.0)))
          # 15m low, 1h still low
          short_entry_logic.append((_cmp("AROONU_14_15m", ">", 20.0)) | (_cmp_cached_119))
          # 15m low, 4h low
          short_entry_logic.append((_cmp("AROONU_14_15m", ">", 20.0)) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 20.0)))
          # 15m still low, 1h low
          short_entry_logic.append((_cmp("AROONU_14_15m", ">", 50.0)) | (_cmp_cached_148))
          # 15m still not high enough, 4h low
          short_entry_logic.append((_cmp("STOCHRSIk_14_14_3_3_15m", ">", 70.0)) | (_cmp("AROONU_14_4h", ">", 10.0)))
          # 1h & 4h low
          short_entry_logic.append((_cmp("AROONU_14_1h", ">", 20.0)) | (_cmp("AROONU_14_4h", ">", 20.0)))
          # 1h & 4h low
          short_entry_logic.append((_cmp("AROONU_14_1h", ">", 20.0)) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 20.0)))
          # 1h low, 1d low
          short_entry_logic.append((_cmp("AROONU_14_1h", ">", 30.0)) | (_cmp("STOCHRSIk_14_14_3_3_1d", ">", 30.0)))
          # 4h still not high enough, 4h & 1d uptrend
          short_entry_logic.append((_cmp("AROONU_14_4h", ">", 70.0)) | (_cmp_cached_123) | (_cmp_cached_74))
          # 1h & 4h low
          short_entry_logic.append((_cmp("STOCHRSIk_14_14_3_3_1h", ">", 20.0)) | (_cmp("AROONU_14_4h", ">", 20.0)))
          # 1d big green, 1d still not high enough
          short_entry_logic.append((_cmp("change_pct_1d", "<", 30.0)) | (_cmp("RSI_14_1d", ">", 65.0)))
          # rise in the last hour, relatively stable before the hour
          short_entry_logic.append(
            (df["close"] < (df["close_min_12"] * 1.10)) | (df["close_min_12"] > (df["close_min_48"] * 1.10))
          )
          # big pump in the last 6 days, 4h still not high enough
          short_entry_logic.append((df["close"] < (df["low_min_6_1d"] * 4.0)) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 80.0)))
          # big pump in the last 20 days, 1h up move
          short_entry_logic.append((df["close"] < (df["low_min_20_1d"] * 6.0)) | (_cmp_cached_101))

          # Logic
          short_entry_logic.append(_cmp("AROOND_14", "<", 25.0))
          short_entry_logic.append(_cmp("STOCHRSIk_14_14_3_3", ">", 80.0))
          short_entry_logic.append(_gt_mul("close", "EMA_20", 1.060))
          short_entry_logic.append(_gt_mul("close", "BBU_20_2.0", 0.995))
          short_entry_logic.append(_cmp("AROOND_14_15m", "<", 25.0))

        # Condition #503 - Normal mode (Short).
        if short_entry_condition_index == 503:
          # Protections
          short_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)

          short_entry_logic.append(_cmp("RSI_3_1h", ">=", 5.0))
          short_entry_logic.append(_cmp("RSI_3_4h", ">=", 20.0))
          short_entry_logic.append(_cmp("RSI_3_1d", ">=", 20.0))
          short_entry_logic.append(_cmp("RSI_14_1h", ">", 20.0))
          short_entry_logic.append(_cmp("RSI_14_4h", ">", 20.0))
          short_entry_logic.append(_cmp("RSI_14_1d", ">", 10.0))
          # 5m strong down move
          short_entry_logic.append((_cmp("RSI_3", "<", 98.0)) | (_cmp("ROC_9", "<", 50.0)))
          # 5m down move, 4h still high
          short_entry_logic.append(
            (_cmp("RSI_3", "<", 90.0)) | (_cmp("MFI_14", ">", 10.0)) | (_cmp_cached_137)
          )
          # 5m & 1h down move, 1h still high
          short_entry_logic.append(
            (_cmp("RSI_3", "<", 90.0)) | (_cmp_cached_101) | (_cmp_cached_147)
          )
          # 5m down move, 4h downtrend, 1h still high
          short_entry_logic.append(
            (_cmp("RSI_3", "<", 95.0)) | (_cmp_cached_116) | (_cmp_cached_148)
          )
          # 5m & 4h strong down move, 4h still not low enough
          short_entry_logic.append(
            (_cmp("RSI_3", "<", 95.0)) | (_cmp_cached_91) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 60.0))
          )
          # 5m down move, 1h high, 1d overbought
          short_entry_logic.append((_cmp("RSI_3", "<", 90.0)) | (_cmp("ROC_9_1h", "<", 15.0)) | (_cmp_cached_44))
          # 5m down move, 1h & 4h high
          short_entry_logic.append(
            (_cmp("RSI_3", "<", 90.0)) | (_cmp("UO_7_14_28_1h", ">", 40.0)) | (_cmp_cached_137)
          )
          # 5m down move, 1h high, 4h downtrend
          short_entry_logic.append(
            (_cmp("RSI_3", "<", 98.0)) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 10.0)) | (_cmp_cached_27)
          )
          # 5m & 1h down move, 4h down
          short_entry_logic.append((_cmp("RSI_3", "<", 90.0)) | (_cmp_cached_136) | (_cmp("CMF_20_4h", ">", -0.2)))
          # 5m down move, 1h high
          short_entry_logic.append((_cmp("RSI_14_change_pct", "<", 40.0)) | (_cmp_cached_148))
          # 5m down move, 1h high
          short_entry_logic.append((_cmp("RSI_14_change_pct", "<", 40.0)) | (_cmp_cached_137))
          # 15m & 1h down move, 4h still high
          short_entry_logic.append(
            (_cmp_cached_89) | (_cmp_cached_136) | (_cmp_cached_122)
          )
          # 15m down move, 15m still not low enough, 1h & 4h still not low enough
          short_entry_logic.append(
            (_cmp_cached_89)
            | (_cmp("AROOND_14_15m", "<", 25.0))
            | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 75.0))
            | (_cmp("MFI_14_4h", ">", 50.0))
          )
          # 5m & 1h down move, 1h still high
          short_entry_logic.append(
            (_cmp_cached_89) | (_cmp_cached_136) | (_cmp_cached_119)
          )
          # 15m & 4h down move, 1h still not low
          short_entry_logic.append(
            (_cmp_cached_89) | (_cmp_cached_126) | (_cmp_cached_147)
          )
          # 15m & 4h down move, 4h still not low enough
          short_entry_logic.append(
            (_cmp_cached_89) | (_cmp("RSI_3_4h", "<", 80.0)) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 60.0))
          )
          # 15m down move, 1h & 4h still high
          short_entry_logic.append(
            (_cmp_cached_89) | (_cmp_cached_119) | (_cmp("RSI_14_4h", ">", 50.0))
          )
          # 15m & 1h & 4h down move
          short_entry_logic.append(
            (_cmp_cached_96) | (_cmp("RSI_3_change_pct_1h", ">", -60.0)) | (_cmp("RSI_3_change_pct_4h", ">", -40.0))
          )
          # 15m down move, 1d downtrend, 1h still high
          short_entry_logic.append(
            (_cmp_cached_96) | (_cmp_cached_149) | (_cmp_cached_148)
          )
          # 15m & 1d down move, 1h still high
          short_entry_logic.append(
            (_cmp_cached_96) | (_cmp("RSI_3_1d", "<", 90.0)) | (_cmp_cached_148)
          )
          # 15m & 4h down move, 1h still high
          short_entry_logic.append(
            (_cmp_cached_96) | (_cmp_cached_144) | (_cmp_cached_119)
          )
          # 15m down move, 15m still not low enough, 4h down move
          short_entry_logic.append((_cmp_cached_96) | (_cmp("AROOND_14_15m", "<", 50.0)) | (_cmp_cached_116))
          # 15m down move, 1h still high, 1d strong downtrend
          short_entry_logic.append((_cmp("RSI_3_15m", "<", 80.0)) | (_cmp("AROOND_14_1h", "<", 25.0)) | (_cmp("MFI_14_1d", "<", 90.0)))
          # 15m down move, 1h still high, 1d downtrend
          short_entry_logic.append(
            (_cmp_cached_127) | (_cmp_cached_148) | (_cmp_cached_35)
          )
          # 15m down move, 4h still high, 1d downtrend
          short_entry_logic.append(
            (_cmp_cached_127) | (_cmp_cached_137) | (_cmp_cached_35)
          )
          # 15m & 4h down move, 1d downtrend
          short_entry_logic.append((_cmp_cached_127) | (_cmp_cached_116) | (_cmp_cached_150))
          # 15m down move, 15m not low enough, 1h overbought
          short_entry_logic.append(
            (_cmp("RSI_14_change_pct_15m", ">", -40.0)) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 90.0)) | (_cmp("RSI_14_1h", ">", 30.0))
          )
          # 15m strong down move, 1h still high
          short_entry_logic.append((_cmp("ROC_9_15m", "<", 15.0)) | (_cmp_cached_119))
          # 15m downtrend, 1h & 4h still high
          short_entry_logic.append(
            (_cmp("ROC_9_15m", "<", 10.0)) | (_cmp_cached_119) | (_cmp_cached_122)
          )
          # 15m & 1h & 4h down move
          short_entry_logic.append(
            (_cmp_cached_89) | (_cmp_cached_91) | (_cmp("CCI_20_change_pct_4h", "<", 0.0))
          )
          # 15m strong down move
          short_entry_logic.append((_cmp_cached_96) | (_cmp("MFI_14_15m", "<", 85.0)) | (_cmp("AROOND_14_15m", "<", 25.0)))
          # 14m down move, 4h still high
          short_entry_logic.append(
            (_cmp("RSI_3_15m", "<", 80.0)) | (_cmp("AROOND_14_15m", "<", 50.0)) | (_cmp("UO_7_14_28_4h", ">", 50.0))
          )
          # 15m down move, 1h stil high, 1d overbought
          short_entry_logic.append((_cmp_cached_127) | (_cmp("AROOND_14_1h", "<", 25.0)) | (_cmp("ROC_9_1d", ">", -80.0)))
          # 15m down move, 1h high, 1d overbought
          short_entry_logic.append(
            (_cmp_cached_96) | (_cmp_cached_148) | (_cmp_cached_95)
          )
          # 1h & 4h down move, 4h still high
          short_entry_logic.append(
            (_cmp_cached_101) | (_cmp("RSI_3_change_pct_4h", "<", 65.0)) | (_cmp_cached_122)
          )
          # 1h & 4h down move, 4h still high
          short_entry_logic.append(
            (_cmp_cached_101) | (_cmp_cached_116) | (_cmp("STOCHRSIk_14_14_3_3_4h", "<", 10.0))
          )
          # 1h down move, 4h still not low enough, 1d overbought
          short_entry_logic.append((_cmp_cached_101) | (_cmp("AROOND_14_4h", "<", 25.0)) | (_cmp("ROC_9_1d", ">", -120.0)))
          # 1h down move, 1h still not low enough, 4h still not low
          short_entry_logic.append(
            (_cmp_cached_101) | (_cmp_cached_147) | (_cmp("RSI_14_4h", ">", 50.0))
          )
          # 1h down move, 4h still high
          short_entry_logic.append((_cmp_cached_91) | (_cmp("RSI_14_4h", ">", 60.0)))
          # 1h down move, 4h still high, 1d downtrend
          short_entry_logic.append(
            (_cmp_cached_128) | (_cmp_cached_137) | (_cmp_cached_35)
          )
          # 1h down move, 4h still high, 1d downtrend
          short_entry_logic.append(
            (_cmp("RSI_3_change_pct_1h", ">", -65.0)) | (_cmp_cached_137) | (_cmp_cached_35)
          )
          # 4h & 1d down move, 1h still high
          short_entry_logic.append(
            (_cmp_cached_126) | (_cmp("ROC_2_1d", "<", 20.0)) | (_cmp_cached_119)
          )
          # 15m still high, 1h down move, 4h high
          short_entry_logic.append(
            (_cmp("AROOND_14_15m", "<", 50.0)) | (_cmp("RSI_3_change_pct_1h", "<", 50.0)) | (_cmp_cached_137)
          )
          # 15m still high, 1h & 4h down move, 4h still high
          short_entry_logic.append(
            (_cmp("AROOND_14_15m", "<", 50.0))
            | (_cmp_cached_136)
            | (_cmp("RSI_3_4h", "<", 80.0))
            | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 80.0))
          )
          # 15m & 1h still high, 4h overbought
          short_entry_logic.append(
            (_cmp("AROOND_14_15m", "<", 50.0)) | (_cmp("AROOND_14_1h", "<", 50.0)) | (_cmp_cached_139)
          )
          # 15m still high, 1h down move, 1d downtrend
          short_entry_logic.append(
            (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 30.0)) | (_cmp_cached_126) | (_cmp_cached_35)
          )
          # 1h & 4h still high, 1d strong down move
          short_entry_logic.append(
            (_cmp_cached_119) | (_cmp("UO_7_14_28_4h", ">", 55.0)) | (_cmp("RSI_3_1d", "<", 90.0))
          )
          # 1h still high, 4h & 1d downtrend
          short_entry_logic.append((_cmp("AROOND_14_1h", "<", 25.0)) | (_cmp_cached_26) | (_cmp_cached_35))
          # 4h moving down, 1d P&D
          short_entry_logic.append(
            (_cmp_cached_50) | (_cmp("RSI_3_change_pct_1d", "<", 50.0)) | (_cmp_cached_95)
          )
          # 1d strong downtrend, 4h still high
          short_entry_logic.append(
            (_cmp("ROC_2_1d", "<", 20.0)) | (_cmp_cached_35) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 70.0))
          )
          # 1d P&D, 1d overbought
          short_entry_logic.append(
            (_cmp("ROC_2_1d", "<", 10.0)) | (_cmp_cached_95) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 5.0))
          )
          # 1h red, previous 1h green, 1h overbought
          short_entry_logic.append(
            (_cmp("change_pct_1h", "<", 1.0)) | (df["change_pct_1h"].shift(12) > -5.0) | (df["RSI_14_1h"].shift(12) < 80.0)
          )
          # 1h red, 1h stil high, 4h downtrend
          short_entry_logic.append(
            (_cmp("change_pct_1h", "<", 5.0)) | (_cmp_cached_119) | (_cmp("ROC_9_4h", ">", -25.0))
          )
          # 4h red, 15m down move, 4h still high
          short_entry_logic.append(
            (_cmp("change_pct_4h", "<", 5.0)) | (_cmp_cached_96) | (_cmp_cached_137)
          )
          # 4h red, previous 4h green, 4h overbought
          short_entry_logic.append(
            (_cmp("change_pct_4h", "<", 5.0)) | (df["change_pct_4h"].shift(48) > -5.0) | (df["ROC_9_4h"].shift(48) > -25.0)
          )
          # 4h red, 4h still not low enough, 1h downtrend, 1h overbought
          short_entry_logic.append(
            (_cmp("change_pct_4h", "<", 10.0))
            | (_cmp("AROOND_14_4h", "<", 25.0))
            | (_cmp_cached_85)
            | (_cmp_cached_44)
          )
          # 4h red, 4h still high, 1d downtrend
          short_entry_logic.append(
            (_cmp("change_pct_4h", "<", 10.0)) | (_cmp_cached_137) | (_cmp_cached_40)
          )
          # 1d P&D, 1d overbought
          short_entry_logic.append(
            (_cmp("change_pct_1d", "<", 10.0)) | (df["change_pct_1d"].shift(288) > -10.0) | (_cmp("ROC_9_1d", ">", -100.0))
          )
          # 1d P&D, 4h still high
          short_entry_logic.append(
            (_cmp("change_pct_1d", "<", 15.0)) | (df["change_pct_1d"].shift(288) > -15.0) | (_cmp("AROOND_14_4h", "<", 50.0))
          )
          short_entry_logic.append(
            (_cmp_cached_101) | (_cmp_cached_144) | (_cmp("CCI_20_change_pct_4h", "<", 0.0))
          )

          # Logic
          short_entry_logic.append(_rsi_20_rising)
          short_entry_logic.append(_cmp("RSI_4", ">", 54.0))
          short_entry_logic.append(_cmp("AROOND_14", "<", 25.0))
          short_entry_logic.append(df["close"] > df["SMA_16"] * 1.058)

        # Condition #504 - Normal mode (Short).
        if short_entry_condition_index == 504:
          # Protections
          short_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)

          short_entry_logic.append(_cmp("RSI_3_1h", ">=", 5.0))
          short_entry_logic.append(_cmp("RSI_3_4h", ">=", 20.0))
          short_entry_logic.append(_cmp("RSI_3_1d", ">=", 20.0))
          short_entry_logic.append(_cmp("RSI_14_1h", ">", 20.0))
          short_entry_logic.append(_cmp("RSI_14_4h", ">", 20.0))
          short_entry_logic.append(_cmp("RSI_14_1d", ">", 10.0))
          # 15m & 1h down move, 4h still high
          short_entry_logic.append(
            (_cmp_cached_89)
            | (_cmp("MFI_14_15m", "<", 90.0))
            | (_cmp_cached_128)
            | (_cmp_cached_122)
          )
          # 15m & 1h down move, 4h still high
          short_entry_logic.append(
            (_cmp_cached_96) | (_cmp("MFI_14_15m", "<", 85.0)) | (_cmp_cached_137)
          )
          # 14m & 4h down move, 4h still high
          short_entry_logic.append(
            (_cmp_cached_96) | (_cmp_cached_116) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 60.0))
          )
          # 15m down move, 1h & 4h still high
          short_entry_logic.append(
            (_cmp_cached_96) | (_cmp("UO_7_14_28_1h", "<", 45.0)) | (_cmp_cached_137)
          )
          # 1h strong down move, 4h still high
          short_entry_logic.append(
            (_cmp_cached_91) | (_cmp("RSI_14_change_pct_1h", "<", 40.0)) | (_cmp_cached_137)
          )
          # 1h strong down move, 4h down move, 4h still high
          short_entry_logic.append(
            (_cmp_cached_91) | (_cmp("RSI_3_change_pct_4h", "<", 50.0)) | (_cmp_cached_122)
          )
          # 1h & 4h down move, 4h still not low enough
          short_entry_logic.append(
            (_cmp_cached_91) | (_cmp_cached_126) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 75.0))
          )
          # 1h & 4h down move, 4h still not low enough
          short_entry_logic.append((_cmp_cached_91) | (_cmp("RSI_3_4h", "<", 75.0)) | (_cmp("AROOND_14_4h", "<", 50.0)))
          # 15m down move, 1h strong downtrend
          short_entry_logic.append((_cmp_cached_89) | (_cmp_cached_91) | (_cmp("MFI_14_1h", ">", 5.0)))
          # 15m downtrend, 4h down move, 4h stil high
          short_entry_logic.append(
            (_cmp("ROC_9_15m", ">", -20.0)) | (_cmp("RSI_3_4h", "<", 75.0)) | (_cmp_cached_137)
          )

          # Logic
          short_entry_logic.append(_cmp("AROOND_14", "<", 25.0))
          short_entry_logic.append(_cmp("AROOND_14_15m", "<", 25.0))
          short_entry_logic.append(_gt_mul("close", "EMA_9", 1.058))
          short_entry_logic.append(_gt_mul("close", "EMA_20", 1.040))

        # Condition #541 - Quick mode (Short).
        if short_entry_condition_index == 541:
          # Protections
          short_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)

          # 5m & 15m down move, 4h still high
          short_entry_logic.append(
            (_cmp("RSI_3", "<", 95.0)) | (_cmp("RSI_3_change_pct_15m", "<", 50.0)) | (_cmp("RSI_14_4h", ">", 50.0))
          )
          # 5m & 15m & 1h down move
          short_entry_logic.append((_cmp("RSI_3", "<", 95.0)) | (_cmp_cached_89) | (_cmp_cached_91))
          # 5m strong down move
          short_entry_logic.append((_cmp("RSI_3", "<", 98.0)) | (_cmp("ROC_9", "<", 50.0)))
          # 15m & 1h strong down move & downtrend
          short_entry_logic.append((_cmp_cached_89) | (_cmp_cached_91) | (_cmp("MFI_14_1h", ">", 5.0)))
          # 15m strong down move, 4h high
          short_entry_logic.append((_cmp_cached_89) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 10.0)))
          # 15m & 1h down move
          short_entry_logic.append(
            (_cmp_cached_89) | (_cmp_cached_91) | (_cmp("CCI_20_change_pct_1h", ">", 0.0))
          )
          # 15m & 1h down move, 4h high
          short_entry_logic.append(
            (_cmp_cached_89) | (_cmp_cached_136) | (_cmp_cached_137)
          )
          # 15m & 1h down move, 4h still high
          short_entry_logic.append(
            (_cmp_cached_89) | (_cmp("RSI_3_change_pct_1h", "<", 50.0)) | (_cmp("MFI_14_4h", ">", 50.0))
          )
          # 15m strong down move, 1h still high
          short_entry_logic.append(
            (_cmp_cached_89) | (_cmp("MFI_14_15m", "<", 90.0)) | (_cmp_cached_119)
          )
          # 15m & 1h down move, 1h not low enough
          short_entry_logic.append(
            (_cmp_cached_89) | (_cmp_cached_91) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 80.0))
          )
          # 15m down move, 1h strong down move
          short_entry_logic.append((_cmp_cached_89) | (_cmp("RSI_14_change_pct_1h", "<", 70.0)))
          # 15m down move, 4h & 1d downtrend
          short_entry_logic.append((_cmp_cached_89) | (_cmp_cached_50) | (_cmp_cached_35))
          # 15m down move, 1h strong down move, 4h stil high
          short_entry_logic.append(
            (_cmp_cached_96) | (_cmp_cached_91) | (_cmp_cached_122)
          )
          # 15m down move, 1h & 4h still high
          short_entry_logic.append(
            (_cmp_cached_127) | (_cmp_cached_119) | (_cmp_cached_122)
          )
          # 15m down move, 1h downtrend, 4h still high
          short_entry_logic.append(
            (_cmp_cached_96) | (_cmp_cached_85) | (_cmp_cached_122)
          )
          # 15m & 1h down move, 4h high
          short_entry_logic.append(
            (_cmp_cached_96) | (_cmp_cached_136) | (_cmp_cached_137)
          )
          # 15m down move, 1h down move, 4h high
          short_entry_logic.append(
            (_cmp_cached_127) | (_cmp("RSI_3_change_pct_1h", "<", 30.0)) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 10.0))
          )
          # 1m down move, 1h still dropping, 4h overbought
          short_entry_logic.append(
            (_cmp_cached_96) | (_cmp("CCI_20_change_pct_1h", "<", 0.0)) | (_cmp("RSI_14_4h", ">", 20.0))
          )
          # 15m down move, 1h high
          short_entry_logic.append((_cmp("RSI_3_change_pct_15m", "<", 70.0)) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 10.0)))
          # 1h strong down move, 4h high
          short_entry_logic.append((_cmp_cached_91) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 10.0)))
          # 1h down move, 4h downtrend, 4h not low enough
          short_entry_logic.append(
            (_cmp_cached_91) | (_cmp("CMF_20_4h", ">", -0.25)) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 70.0))
          )
          # 1h down move, 4h high, 1d overbought
          short_entry_logic.append((_cmp_cached_101) | (_cmp("RSI_14_4h", ">", 40.0)) | (_cmp_cached_95))
          # 1h down move, 4h strong down move
          short_entry_logic.append((_cmp_cached_91) | (_cmp("RSI_14_change_pct_4h", "<", 40.0)))
          # 1h & 4h down move, 4h still going down
          short_entry_logic.append(
            (_cmp_cached_91) | (_cmp_cached_144) | (_cmp("CCI_20_change_pct_4h", "<", 0.0))
          )
          # 1h & 4h down move, 4h still not low enough
          short_entry_logic.append(
            (_cmp_cached_91) | (_cmp("RSI_3_change_pct_4h", "<", 65.0)) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 70.0))
          )
          # 1h down move, 4h down move, 4h P&D
          short_entry_logic.append(
            (_cmp_cached_101) | (_cmp("RSI_3_change_pct_4h", "<", 70.0)) | (df["RSI_14_4h"].shift(48) > 30.0)
          )
          # 1h & 4h down move, 4h still not low enough, 1d still high
          short_entry_logic.append(
            (_cmp_cached_101)
            | (_cmp("RSI_3_change_pct_4h", "<", 50.0))
            | (_cmp("AROOND_14_4h", "<", 25.0))
            | (_cmp("STOCHRSIk_14_14_3_3_1d", ">", 60.0))
          )
          # 1h down move, 1h still high, 1d going down
          short_entry_logic.append(
            (_cmp_cached_136) | (_cmp_cached_119) | (_cmp("ROC_2_1d", ">", -50.0))
          )
          # 4h downtrend, 4h still high, 1d strong downtrend
          short_entry_logic.append(
            (_cmp_cached_116) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 70.0)) | (_cmp_cached_99)
          )
          # 15m down move, 1h strong down move, 1d overbought
          short_entry_logic.append(
            (_cmp("MFI_14_15m", "<", 80.0)) | (_cmp("RSI_3_change_pct_1h", "<", 80.0)) | (_cmp_cached_95)
          )
          # 1h not low enough, 4h high, 1d strong downtrend
          short_entry_logic.append(
            (_cmp_cached_147) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 10.0)) | (_cmp_cached_99)
          )
          # 1h down move, 4h still high, 1d downtrend
          short_entry_logic.append(
            (_cmp("RSI_3_change_pct_1h", "<", 65.0)) | (_cmp_cached_137) | (_cmp_cached_35)
          )
          # 15m strong down move, 1h still high
          short_entry_logic.append((_cmp("ROC_9_15m", "<", 15.0)) | (_cmp_cached_148))
          # 15m downtrend, 4h down move, 4h stil high
          short_entry_logic.append(
            (_cmp("ROC_9_15m", "<", 15.0)) | (_cmp("RSI_3_4h", "<", 75.0)) | (_cmp_cached_137)
          )
          # 1h downtrend, 4h overbought
          short_entry_logic.append((_cmp("ROC_2_1h", "<", 5.0)) | (_cmp("RSI_14_4h", ">", 20.0)) | (_cmp("ROC_9_4h", ">", -25.0)))
          # 1h P&D, 4h still high
          short_entry_logic.append(
            (_cmp("ROC_2_1h", "<", 10.0)) | (_cmp("ROC_9_1h", ">", -5.0)) | (_cmp_cached_137)
          )
          # 1h downtrend, 4h down move, 1d downtrend
          short_entry_logic.append((_cmp_cached_134) | (_cmp_cached_126) | (_cmp_cached_35))
          short_entry_logic.append((_cmp("ROC_9_4h", ">", -200.0)) | (_cmp("RSI_14_4h", ">", 20.0)))
          # 4h down move, 1d P&D
          short_entry_logic.append((_cmp_cached_26) | (_cmp("ROC_2_1d", "<", 20.0)) | (_cmp_cached_95))
          # 1h P&D, 4h overbought
          short_entry_logic.append(
            (_cmp("change_pct_1h", "<", 2.0)) | (df["change_pct_1h"].shift(12) > 2.0) | (_cmp("RSI_14_4h", ">", 20.0))
          )
          # 1h P&D, 1d overbought
          short_entry_logic.append(
            (_cmp("change_pct_1h", "<", 5.0)) | (df["change_pct_1h"].shift(12) > -5.0) | (_cmp("ROC_9_1d", ">", -100.0))
          )
          # 1h & 4h red, 1h not low enough
          short_entry_logic.append(
            (_cmp("change_pct_1h", "<", 10.0)) | (_cmp("change_pct_4h", "<", 10.0)) | (_cmp("MFI_14_1h", ">", 50.0))
          )
          # 1h red, 1h still not low enough, 1d down move
          short_entry_logic.append((_cmp("change_pct_1h", "<", 15.0)) | (_cmp("MFI_14_1h", ">", 50.0)) | (_cmp("RSI_3_1d", "<", 90.0)))
          # 4h red, previous 4h green, 4h overbought
          short_entry_logic.append(
            (_cmp("change_pct_4h", "<", 5.0)) | (df["change_pct_4h"].shift(48) > -5.0) | (df["RSI_14_4h"].shift(48) > 20.0)
          )
          # 1d P&D, 1d overbought
          short_entry_logic.append(
            (_cmp("change_pct_1d", "<", 10.0)) | (df["change_pct_1d"].shift(288) > -10.0) | (_cmp("ROC_9_1d", ">", -100.0))
          )
          # 1d P&D, 4h still high
          short_entry_logic.append(
            (_cmp("change_pct_1d", "<", 15.0)) | (df["change_pct_1d"].shift(288) > -15.0) | (_cmp("AROOND_14_4h", "<", 50.0))
          )

          # Logic
          short_entry_logic.append(_cmp("RSI_14", ">", 64.0))
          short_entry_logic.append(_cmp("AROOND_14", "<", 25.0))
          short_entry_logic.append(_cmp("AROONU_14", ">", 75.0))
          short_entry_logic.append(df["EMA_9"] > (df["EMA_26"] * 1.040))

        # Condition #542 - Quick mode (Short).
        if short_entry_condition_index == 542:
          # Protections
          short_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          short_entry_logic.append(df["protections_short_global"] == True)

          # 5m & 15m up move, 15m stil low
          short_entry_logic.append((_cmp("RSI_3", "<", 90.0)) | (_cmp("RSI_3_15m", "<", 80.0)) | (_cmp("AROONU_14_15m", ">", 60.0)))
          # 15m & 1h up move, 4h still low
          short_entry_logic.append((_cmp_cached_89) | (_cmp_cached_91) | (_cmp("RSI_14_4h", ">", 60.0)))
          # 15m & 1h up move, 4h still not high enough
          short_entry_logic.append(
            (_cmp_cached_89) | (_cmp_cached_91) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 80.0))
          )
          # 15m & 1h up move, 1h still moving higher
          short_entry_logic.append(
            (_cmp_cached_89) | (_cmp_cached_101) | (_cmp("CCI_20_change_pct_1h", "<", -0.0))
          )
          # 15m & 4h up move, 4h still moving higher
          short_entry_logic.append(
            (_cmp_cached_96) | (_cmp_cached_144) | (_cmp("CCI_20_change_pct_4h", "<", -0.0))
          )
          # 15m & 1d up move, 4h uptrend
          short_entry_logic.append((_cmp_cached_96) | (_cmp("RSI_3_1d", "<", 80.0)) | (_cmp_cached_26))
          # 15m up move, 15m & 4h high
          short_entry_logic.append(
            (_cmp_cached_96) | (_cmp("AROONU_14_15m", "<", 100.0)) | (_cmp_cached_14)
          )
          # 15m up move, 15m still not high enough, 1d uptrend
          short_entry_logic.append(
            (_cmp_cached_96) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 80.0)) | (_cmp_cached_69)
          )
          # 15m & 4h up move, 15m still not high enough
          short_entry_logic.append(
            (_cmp_cached_127) | (_cmp_cached_126) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 70.0))
          )
          # 15m & 4h up move, 1d uptrend
          short_entry_logic.append((_cmp_cached_127) | (_cmp_cached_116) | (_cmp_cached_35))
          # 15m & 4h up move, 4h still not high enough
          short_entry_logic.append((_cmp_cached_127) | (_cmp("RSI_3_4h", "<", 80.0)) | (_cmp("RSI_14_4h", ">", 60.0)))
          # 15m up move, 15m still not high enough, 4h still low
          short_entry_logic.append(
            (_cmp_cached_127) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 80.0)) | (_cmp("AROONU_14_4h", ">", 50.0))
          )
          # 15m up move, 4h overbought
          short_entry_logic.append((_cmp_cached_127) | (_cmp_cached_98))
          # 15m & 1h up move, 15m still low
          short_entry_logic.append((_cmp("RSI_3_15m", "<", 70.0)) | (_cmp("RSI_3_1h", "<", 70.0)) | (_cmp("AROONU_14_15m", ">", 40.0)))
          # 15m & 1h up move, 15m still low
          short_entry_logic.append(
            (_cmp("RSI_3_15m", "<", 70.0)) | (_cmp("RSI_3_1h", "<", 70.0)) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 40.0))
          )
          # # 15m & 1h up move, 4h low
          short_entry_logic.append((_cmp("RSI_3_15m", "<", 70.0)) | (_cmp("RSI_3_1h", "<", 60.0)) | (_cmp("AROONU_14_4h", ">", 40.0)))
          # 1h & 1d up move, 1h still moving higher
          short_entry_logic.append(
            (_cmp("RSI_3_1h", "<", 97.0)) | (_cmp("RSI_3_1d", "<", 95.0)) | (_cmp("CCI_20_change_pct_1h", "<", -0.0))
          )
          # 1h & 4h up move, 15m still not high enough
          short_entry_logic.append(
            (_cmp_cached_91) | (_cmp_cached_144) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 80.0))
          )
          # 1h & 4h up move, 1d uptrend
          short_entry_logic.append((_cmp_cached_91) | (_cmp_cached_144) | (_cmp_cached_29))
          # 1h & 4h up move, 1d still low
          short_entry_logic.append((_cmp_cached_91) | (_cmp_cached_116) | (_cmp("RSI_14_1d", ">", 50.0)))
          # 1h up move, 4h still low, 1h still moving higher
          short_entry_logic.append(
            (_cmp_cached_91) | (_cmp("RSI_14_4h", ">", 60.0)) | (_cmp("CCI_20_change_pct_1h", "<", -0.0))
          )
          # 1h up move, 4h low
          short_entry_logic.append((_cmp_cached_91) | (_cmp("AROONU_14_4h", ">", 10.0)))
          # 1h & 4h up move, 1h still moving higher
          short_entry_logic.append(
            (_cmp_cached_101) | (_cmp_cached_116) | (_cmp("CCI_20_change_pct_1h", "<", -0.0))
          )
          # 1h & 4h up move, 4h still not high enough
          short_entry_logic.append(
            (_cmp_cached_101) | (_cmp("RSI_3_4h", "<", 70.0)) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 80.0))
          )
          # 1h & 1d up move, 15m still low
          short_entry_logic.append(
            (_cmp_cached_101) | (_cmp("RSI_3_1d", "<", 90.0)) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 60.0))
          )
          # 1h up move, 15m high
          short_entry_logic.append((_cmp_cached_101) | (_cmp("AROONU_14_15m", "<", 100.0)))
          # 1h up move, 4h low
          short_entry_logic.append((_cmp_cached_101) | (_cmp_cached_137))
          # 1h up move, 4h still low, 1h still moving higher
          short_entry_logic.append(
            (_cmp_cached_101) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 60.0)) | (_cmp("CCI_20_change_pct_1h", "<", -0.0))
          )
          # 1h up move, 15m uptrend
          short_entry_logic.append((_cmp_cached_101) | (_cmp("ROC_9_15m", "<", 30.0)))
          # 1h up move, 15m & 4h uptrend
          short_entry_logic.append((_cmp_cached_101) | (_cmp("ROC_9_15m", "<", 20.0)) | (_cmp_cached_26))
          # 1h & 4h up move, 4h still moving higher
          short_entry_logic.append(
            (_cmp_cached_136) | (_cmp("RSI_3_4h", "<", 80.0)) | (_cmp("CCI_20_change_pct_4h", "<", -0.0))
          )
          # 1h up move, 15m low
          short_entry_logic.append((_cmp_cached_136) | (_cmp("AROONU_14_15m", ">", 40.0)))
          # 1h up move, 4h still not high enough, 1d low
          short_entry_logic.append((_cmp_cached_136) | (_cmp("AROONU_14_4h", ">", 80.0)) | (_cmp("RSI_14_1d", ">", 40.0)))
          # 1h & 4h up move, 4h still low
          short_entry_logic.append((_cmp_cached_128) | (_cmp("RSI_3_4h", "<", 80.0)) | (_cmp("AROONU_14_4h", ">", 50.0)))
          # 1h & 4h up move, 1d still low
          short_entry_logic.append((_cmp_cached_128) | (_cmp("RSI_3_4h", "<", 80.0)) | (_cmp("AROONU_14_1d", ">", 50.0)))
          # 1h & 4h up move, 1d low
          short_entry_logic.append(
            (_cmp_cached_128) | (_cmp("RSI_3_4h", "<", 70.0)) | (_cmp("STOCHRSIk_14_14_3_3_1d", ">", 30.0))
          )
          # 1h up move, 1d still low, 1d uptrend
          short_entry_logic.append((_cmp_cached_128) | (_cmp("AROONU_14_1d", ">", 50.0)) | (_cmp_cached_51))
          # 1h up move, 1d low
          short_entry_logic.append((_cmp_cached_128) | (_cmp("STOCHRSIk_14_14_3_3_1d", ">", 20.0)))
          # 1h up move, 4h & 1d uptrend
          short_entry_logic.append((_cmp_cached_128) | (_cmp_cached_26) | (_cmp_cached_40))
          # 4h up move, 1d low
          short_entry_logic.append((_cmp_cached_144) | (_cmp("RSI_14_1d", ">", 40.0)))
          # 4h down move, 15m still not high enough, 1d low
          short_entry_logic.append(
            (_cmp_cached_144) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 80.0)) | (_cmp("AROOND_14_1d", "<", 75.0))
          )
          # 4h up move, 1h & 4h uptrend
          short_entry_logic.append((_cmp_cached_144) | (_cmp_cached_85) | (_cmp_cached_26))
          # 4h up move, 15m low
          short_entry_logic.append((_cmp_cached_126) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 45.0)))
          # 4h up move, 4h & 1d uptrend
          short_entry_logic.append((_cmp_cached_126) | (_cmp_cached_26) | (_cmp_cached_40))
          # 4h up move, 15m still not high enough
          short_entry_logic.append((_cmp_cached_116) | (_cmp("AROONU_14_15m", ">", 60.0)))
          # 4h up move, 15m low
          short_entry_logic.append((_cmp_cached_116) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 30.0)))
          # 4h up move, 4h uptrend
          short_entry_logic.append((_cmp("RSI_3_4h", "<", 80.0)) | (_cmp_cached_14) | (_cmp_cached_26))
          # 4h up move, 15m still low, 4h still not high enough
          short_entry_logic.append(
            (_cmp("RSI_3_4h", "<", 80.0)) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 60.0)) | (_cmp("AROONU_14_4h", ">", 80.0))
          )
          # 4h up move, 15m still low, 4h still not high enough
          short_entry_logic.append(
            (_cmp("RSI_3_4h", "<", 75.0)) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 60.0)) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 80.0))
          )
          # 1d up move, 4h low
          short_entry_logic.append((_cmp("RSI_3_1d", "<", 85.0)) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 40.0)))
          # 4h still not high enough, 4h overbought, 4h uptrend
          short_entry_logic.append(
            (_cmp("RSI_14_4h", ">", 80.0)) | (_cmp_cached_73) | (_cmp("CCI_20_change_pct_4h", "<", 0.0))
          )
          # 15m & 1h high, 4h uptrend
          short_entry_logic.append(
            (_cmp("AROONU_14_15m", "<", 100.0)) | (_cmp_cached_71) | (_cmp_cached_26)
          )
          # 15m & 4h high, 1h uptrend
          short_entry_logic.append(
            (_cmp("AROONU_14_15m", "<", 100.0)) | (_cmp_cached_14) | (_cmp_cached_85)
          )
          # 15m high, 1d low
          short_entry_logic.append((_cmp("AROONU_14_15m", "<", 100.0)) | (_cmp("STOCHRSIk_14_14_3_3_1d", ">", 20.0)))
          # 15m high & uptrend
          short_entry_logic.append((_cmp("AROONU_14_15m", "<", 100.0)) | (_cmp("ROC_9_15m", "<", 30.0)))
          # 15m high, 1h & 4h uptrend
          short_entry_logic.append((_cmp("AROONU_14_15m", "<", 100.0)) | (_cmp_cached_85) | (_cmp_cached_26))
          # 1h high, 15m uptrend
          short_entry_logic.append((_cmp_cached_71) | (_cmp("ROC_9_15m", "<", 20.0)))
          # 15m & 4h still not high enough
          short_entry_logic.append((_cmp("STOCHRSIk_14_14_3_3_15m", ">", 70.0)) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 70.0)))
          # 1h & 4h overbought, 1h uptrend
          short_entry_logic.append(
            (_cmp_cached_61) | (_cmp_cached_73) | (_cmp("CCI_20_change_pct_1h", "<", 0.0))
          )
          # 1h & 4h overbought, 4h uptrend
          short_entry_logic.append(
            (_cmp_cached_61) | (_cmp_cached_73) | (_cmp("CCI_20_change_pct_4h", "<", 0.0))
          )
          # 1d bot wick, 4h still not high enough
          short_entry_logic.append((_cmp("bot_wick_pct_1d", "<", 30.0)) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 80.0)))
          # rise in the last 12 hours, relatively stable before the 12 hours
          short_entry_logic.append(
            (df["close"] < (df["low_min_12_1h"] * 1.30)) | (df["low_min_12_1h"] > (df["low_min_24_1h"] * 1.10))
          )
          # big pump in the last 30 days, 4h up move
          short_entry_logic.append((df["close"] < (df["low_min_30_1d"] * 4.0)) | (_cmp_cached_116))

          # Logic
          short_entry_logic.append(_cmp("WILLR_14", ">", -50.0))
          short_entry_logic.append(_cmp("AROONU_14", ">", 75.0))
          short_entry_logic.append(_cmp("AROOND_14", "<", 25.0))
          short_entry_logic.append(_cmp("STOCHRSIk_14_14_3_3", ">", 80.0))
          short_entry_logic.append(_cmp("WILLR_84_1h", ">", -30.0))
          short_entry_logic.append(_cmp("STOCHRSIk_14_14_3_3_1h", ">", 80.0))
          short_entry_logic.append(_cmp("BBB_20_2.0_1h", ">", 20.0))
          short_entry_logic.append(df["close_min_48"] <= (df["close"] * 0.90))

        # Condition #543 - Rapid mode (Short).
        if short_entry_condition_index == 543:
          # Protections
          short_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)

          short_entry_logic.append(_cmp("RSI_14_1h", ">", 20.0))
          short_entry_logic.append(_cmp("RSI_14_4h", ">", 20.0))
          short_entry_logic.append(_cmp("RSI_14_1d", ">", 10.0))
          # 5m strong down move
          short_entry_logic.append((_cmp("RSI_3", "<", 98.0)) | (_cmp("ROC_9", "<", 50.0)))
          # 15m down move, 1h down move, 1h still not low enough
          short_entry_logic.append(
            (_cmp_cached_89) | (_cmp("RSI_3_change_pct_1h", "<", 60.0)) | (_cmp_cached_119)
          )
          # 15m down move, 1h down move, 4h still not low enough
          short_entry_logic.append(
            (_cmp_cached_89) | (_cmp("RSI_3_change_pct_1h", "<", 40.0)) | (_cmp_cached_137)
          )
          # 5m down move, 1h down, 4h high
          short_entry_logic.append(
            (_cmp_cached_89) | (_cmp("CMF_20_1h", "<", 0.2)) | (_cmp_cached_122)
          )
          # 15m down move, 1h still not low enough, 4h high
          short_entry_logic.append(
            (_cmp_cached_89) | (_cmp("AROOND_14_1h", "<", 25.0)) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 10.0))
          )
          # 15m down move, 1h still high
          short_entry_logic.append(
            (_cmp_cached_96) | (_cmp("OBV_change_pct_15m", "<", 50.0)) | (_cmp_cached_148)
          )
          # 5m & 1h strong down move, 1h still not low enough
          short_entry_logic.append(
            (_cmp_cached_89) | (_cmp_cached_91) | (_cmp_cached_147)
          )
          # 5m & 1h strong downtrend
          short_entry_logic.append((_cmp_cached_89) | (_cmp_cached_91) | (_cmp("MFI_14_1h", "<", 90.0)))
          # 15m & 1h down move, 4h still high
          short_entry_logic.append(
            (_cmp_cached_89)
            | (_cmp_cached_128)
            | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 70.0))
            | (_cmp("AROOND_14_4h", "<", 50.0))
          )
          # 15m & 1h down move, 4h still high, 4h downtrend
          short_entry_logic.append(
            (_cmp_cached_89) | (_cmp_cached_101) | (_cmp("UO_7_14_28_4h", ">", 60.0)) | (_cmp_cached_26)
          )
          # 15m & 1h down move, 1d strong downtrend
          short_entry_logic.append((_cmp_cached_89) | (_cmp_cached_101) | (_cmp_cached_35))
          # 15m & 4h down move, 4h still not low enough
          short_entry_logic.append(
            (_cmp_cached_96) | (_cmp_cached_116) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 55.0))
          )
          # 15m down move, 15m still not low enough, 1h still high
          short_entry_logic.append(
            (_cmp_cached_127) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 50.0)) | (_cmp_cached_148)
          )
          # 15m & 1h down move, 1h still high
          short_entry_logic.append(
            (_cmp_cached_127) | (_cmp("RSI_3_1h", "<", 75.0)) | (_cmp_cached_148)
          )
          # 15m down move, 15m still not low enoug, 1h high
          short_entry_logic.append(
            (_cmp_cached_127) | (_cmp("AROOND_14_15m", "<", 25.0)) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 10.0))
          )
          # 15m down move, 1h downtrend, 4h overbought
          short_entry_logic.append((_cmp_cached_127) | (_cmp("ROC_9_1h", "<", 5.0)) | (_cmp("ROC_9_4h", ">", -35.0)))
          # 1h & 4h down move, 4h still not low enough
          short_entry_logic.append(
            (_cmp_cached_91) | (_cmp_cached_126) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 75.0))
          )
          # 1h & 4h down move, 4h still high
          short_entry_logic.append(
            (_cmp_cached_91) | (_cmp("RSI_3_change_pct_4h", "<", 50.0)) | (_cmp_cached_122)
          )
          # 1h & 4h down move, 4h still not low enough
          short_entry_logic.append(
            (_cmp_cached_91) | (_cmp("RSI_3_change_pct_4h", "<", 65.0)) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 70.0))
          )
          # 1h down move, 1h still not low enough, 4h still not low
          short_entry_logic.append(
            (_cmp_cached_101) | (_cmp_cached_147) | (_cmp("RSI_14_4h", ">", 50.0))
          )
          # 1h down move, 1h not low enough, 1h still high
          short_entry_logic.append(
            (_cmp_cached_136) | (_cmp("AROOND_14_1h", "<", 50.0)) | (_cmp_cached_122)
          )
          # 4h down move, 15m still not low enough, 1h still high
          short_entry_logic.append(
            (_cmp("RSI_3_4h", "<", 80.0)) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 70.0)) | (_cmp_cached_148)
          )
          # 4h down move, 4h still high, 1d downtrend
          short_entry_logic.append(
            (_cmp("RSI_3_4h", "<", 75.0)) | (_cmp_cached_122) | (_cmp_cached_35)
          )
          # 4h & 1d down move, 1d strong downtrend
          short_entry_logic.append((_cmp_cached_126) | (_cmp("RSI_3_1d", "<", 90.0)) | (_cmp_cached_99))
          # 4h overbought, 1h still high, 1d downtrend
          short_entry_logic.append(
            (_cmp("ROC_9_4h", ">", -50.0)) | (_cmp_cached_147) | (_cmp_cached_35)
          )
          # 4h red, previous 4h green, 4h overbought
          short_entry_logic.append(
            (_cmp("change_pct_4h", "<", 5.0)) | (df["change_pct_4h"].shift(48) > -5.0) | (df["RSI_14_4h"].shift(48) > 20.0)
          )
          # 4h red, 4h moving down, 4h still high, 1d downtrend
          short_entry_logic.append(
            (_cmp("change_pct_4h", "<", 10.0))
            | (_cmp("CCI_20_change_pct_4h", "<", 0.0))
            | (_cmp_cached_122)
            | (_cmp_cached_40)
          )

          # Logic
          short_entry_logic.append(_cmp("RSI_14", ">", 60.0))
          short_entry_logic.append(_cmp("MFI_14", ">", 60.0))
          short_entry_logic.append(_cmp("AROOND_14", "<", 25.0))
          short_entry_logic.append(df["EMA_26"] < df["EMA_12"])
          short_entry_logic.append((df["EMA_26"] - df["EMA_12"]) > (df["open"] * 0.024))
          short_entry_logic.append(_ema_26_12_spread_gt_open_pct)
          short_entry_logic.append(df["close"] < (df["EMA_20"] * 0.958))
          short_entry_logic.append(df["close"] < (df["BBL_20_2.0"] * 0.992))

        # # Condition #620 - Grind mode (Short).
        # if short_entry_condition_index == 620:
        #   # Protections
        #   short_entry_logic.append(num_open_short_grind_mode < self.grind_mode_max_slots)
        #   short_entry_logic.append(is_pair_short_grind_mode)
        #   short_entry_logic.append(_cmp("RSI_3", "<=", 40.0))
        #   short_entry_logic.append(_cmp("RSI_3_15m", ">=", 10.0))
        #   short_entry_logic.append(_cmp("RSI_3_1h", ">=", 5.0))
        #   short_entry_logic.append(_cmp("RSI_3_4h", ">=", 5.0))
        #   short_entry_logic.append(_cmp("RSI_14_1h", "<", 85.0))
        #   short_entry_logic.append(_cmp("RSI_14_4h", "<", 85.0))
        #   short_entry_logic.append(_cmp("RSI_14_1d", "<", 85.0))
        #   short_entry_logic.append(df["close_max_48"] >= (df["close"] * 1.10))

        #   # Logic
        #   short_entry_logic.append(_cmp("STOCHRSIk_14_14_3_3", ">", 80.0))
        #   short_entry_logic.append(_cmp("WILLR_14", ">", -20.0))
        #   short_entry_logic.append(_cmp("AROOND_14", "<", 25.0))

        # Condition #641 - Top Coins mode (Short).
        if short_entry_condition_index == 641:
          # Protections
          short_entry_logic.append(is_pair_short_top_coins_mode)

          short_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)

          short_entry_logic.append(_cmp("RSI_3_1h", ">=", 5.0))
          short_entry_logic.append(_cmp("RSI_3_4h", ">=", 20.0))
          short_entry_logic.append(_cmp("RSI_3_1d", ">=", 20.0))
          short_entry_logic.append(_cmp("RSI_14_1h", ">", 20.0))
          short_entry_logic.append(_cmp("RSI_14_4h", ">", 20.0))
          short_entry_logic.append(_cmp("RSI_14_1d", ">", 10.0))
          # 5m down move, 1h still not low enough, 4h high
          short_entry_logic.append(
            (_cmp("RSI_3", "<", 90.0)) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 90.0)) | (_cmp_cached_137)
          )
          # 5m down move, 1h high, 4h still not low enough
          short_entry_logic.append(
            (_cmp("RSI_3", "<", 90.0)) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 20.0)) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 90.0))
          )
          # 15m down move, 15m still not low enough, 1h still high
          short_entry_logic.append(
            (_cmp_cached_89) | (_cmp("AROOND_14_15m", "<", 25.0)) | (_cmp_cached_119)
          )
          # 15m & 1h down move, 1d still not low enough
          short_entry_logic.append(
            (_cmp_cached_89) | (_cmp_cached_91) | (_cmp("STOCHRSIk_14_14_3_3_1d", ">", 70.0))
          )
          # 15m & 1h down move, 1h still not low enough
          short_entry_logic.append(
            (_cmp_cached_127) | (_cmp_cached_136) | (_cmp_cached_147)
          )
          # 15m down move, 1h high, 4h still high
          short_entry_logic.append(
            (_cmp_cached_127) | (_cmp_cached_148) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 75.0))
          )
          # 15m & 1h down move, 4h still high
          short_entry_logic.append(
            (_cmp("RSI_3_15m", "<", 80.0)) | (_cmp("RSI_3_1h", "<", 70.0)) | (_cmp_cached_122)
          )
          # 15m down move, 1h still not low enough, 4h still high
          short_entry_logic.append(
            (_cmp("RSI_3_15m", "<", 75.0)) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 80.0)) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 60.0))
          )
          # 1h & 4h & 1d down move
          short_entry_logic.append((_cmp_cached_91) | (_cmp_cached_126) | (_cmp("RSI_3_1d", "<", 80.0)))
          # 1h & 4h down move, 15m not low enough
          short_entry_logic.append(
            (_cmp_cached_101) | (_cmp_cached_126) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 75.0))
          )
          # 1h down move, 1h still not low enough, 4h still high
          short_entry_logic.append(
            (_cmp_cached_101) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 90.0)) | (_cmp_cached_122)
          )
          # 1h & 4h down move, 1h still not low enough
          short_entry_logic.append(
            (_cmp_cached_136) | (_cmp("RSI_3_4h", "<", 75.0)) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 90.0))
          )
          # 1h & 4h down move, 4h still high
          short_entry_logic.append(
            (_cmp_cached_136) | (_cmp("RSI_3_4h", "<", 75.0)) | (_cmp_cached_122)
          )
          # 1h & 4h down move, 1h still not low enough
          short_entry_logic.append(
            (_cmp_cached_128) | (_cmp_cached_116) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 75.0))
          )
          # 1h & 4h down move, 4h still not low enough
          short_entry_logic.append(
            (_cmp_cached_128) | (_cmp_cached_116) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 75.0))
          )
          # 1h down move, 1h & 4h still not low enough
          short_entry_logic.append(
            (_cmp_cached_128) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 90.0)) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 70.0))
          )
          # 4h down move, 15m still high, 1h still not low enough
          short_entry_logic.append(
            (_cmp_cached_116) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 50.0)) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 75.0))
          )
          # 4h down move, 15m & 4h still not low enough
          short_entry_logic.append(
            (_cmp("RSI_3_4h", "<", 15.0)) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 30.0)) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 80.0))
          )

          # Logic
          short_entry_logic.append(_rsi_20_rising)
          short_entry_logic.append(_cmp("RSI_3", ">", 70.0))
          short_entry_logic.append(_cmp("AROOND_14", "<", 25.0))
          short_entry_logic.append(df["close"] > df["SMA_16"] * 1.044)

        # Condition #642 - Top Coins mode (Short).
        if short_entry_condition_index == 642:
          # Protections
          short_entry_logic.append(is_pair_short_top_coins_mode)

          short_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)

          # 5m & 1h & 4h down move
          short_entry_logic.append((_cmp("RSI_3", "<", 90.0)) | (_cmp_cached_91) | (_cmp_cached_126))
          # 5m down move, 15m & 4h still high
          short_entry_logic.append(
            (_cmp("RSI_3", "<", 90.0)) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 60.0)) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 60.0))
          )
          # 5m down move, 15m still high, 1h high
          short_entry_logic.append(
            (_cmp("RSI_3", "<", 85.0)) | (_cmp("AROOND_14_15m", "<", 50.0)) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 20.0))
          )
          # 15m & 1h down move, 1h still not low enough
          short_entry_logic.append(
            (_cmp_cached_89) | (_cmp_cached_91) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 90.0))
          )
          # 15m & 1h down move, 1d still not low enough
          short_entry_logic.append(
            (_cmp_cached_89) | (_cmp_cached_91) | (_cmp("STOCHRSIk_14_14_3_3_1d", ">", 70.0))
          )
          # 15m strong down move, 4h high
          short_entry_logic.append((_cmp_cached_89) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 20.0)))
          # 15m & 1h down move, 1h still not low enough
          short_entry_logic.append(
            (_cmp_cached_89) | (_cmp_cached_128) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 80.0))
          )
          # 15m down move, 15m stil high, 1h still not low enough
          short_entry_logic.append(
            (_cmp_cached_96) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 50.0)) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 80.0))
          )
          # 15m down move, 1h & 4h still high
          short_entry_logic.append(
            (_cmp_cached_96) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 60.0)) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 60.0))
          )
          # 15m & 1h down move, 4h still not low enough
          short_entry_logic.append(
            (_cmp_cached_89) | (_cmp("RSI_3_1h", "<", 70.0)) | (_cmp_cached_122)
          )
          # 15m down move, 15m still not low enough, 4h high
          short_entry_logic.append(
            (_cmp_cached_127) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 80.0)) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 20.0))
          )
          # 15m down move, 4h still high, 1d high
          short_entry_logic.append(
            (_cmp_cached_127) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 60.0)) | (_cmp("STOCHRSIk_14_14_3_3_1d", ">", 30.0))
          )
          # 15m & 4h down move, 1d still high
          short_entry_logic.append(
            (_cmp_cached_127) | (_cmp("RSI_3_4h", "<", 75.0)) | (_cmp("STOCHRSIk_14_14_3_3_1d", ">", 50.0))
          )
          # 15m & 1h down move, 4h still not low enough
          short_entry_logic.append(
            (_cmp("RSI_3_15m", "<", 80.0)) | (_cmp_cached_128) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 70.0))
          )
          # 15m & 1h down move, 4h still not low enough
          short_entry_logic.append(
            (_cmp("RSI_3_15m", "<", 75.0)) | (_cmp("RSI_3_1h", "<", 75.0)) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 70.0))
          )
          # 15m & 4h down move, 4h still not low enough
          short_entry_logic.append(
            (_cmp("RSI_3_15m", "<", 75.0)) | (_cmp("RSI_3_4h", "<", 75.0)) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 80.0))
          )
          # 15m down move, 1h still high, 4h still high
          short_entry_logic.append(
            (_cmp("RSI_3_15m", "<", 75.0)) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 80.0)) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 60.0))
          )
          # 15m down move, 1h still not low enough, 4h high
          short_entry_logic.append(
            (_cmp("RSI_3_15m", "<", 75.0)) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 90.0)) | (_cmp_cached_137)
          )
          # 15m down move, 1h high, 4h still not low enough
          short_entry_logic.append(
            (_cmp("RSI_3_15m", "<", 75.0)) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 20.0)) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 90.0))
          )
          # 15m down move, 4h high, 1d stil high
          short_entry_logic.append(
            (_cmp("RSI_3_15m", "<", 75.0)) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 20.0)) | (_cmp("STOCHRSIk_14_14_3_3_1d", ">", 50.0))
          )
          # 15m & 4h down move, 1h still not low enough
          short_entry_logic.append(
            (_cmp("RSI_3_15m", "<", 70.0)) | (_cmp_cached_116) | (_cmp_cached_147)
          )
          # 15m & 4h down move, 1h still high
          short_entry_logic.append(
            (_cmp("RSI_3_15m", "<", 70.0)) | (_cmp("RSI_3_4h", "<", 80.0)) | (_cmp_cached_119)
          )
          # 15m down move, 15m still high 4h still high
          short_entry_logic.append(
            (_cmp("RSI_3_15m", "<", 70.0)) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 70.0)) | (_cmp_cached_122)
          )
          # 15m down move, 1h still high, 4h high
          short_entry_logic.append(
            (_cmp("RSI_3_15m", "<", 70.0)) | (_cmp_cached_119) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 10.0))
          )
          # 1h & 4h down move, 1h still not low enough
          short_entry_logic.append(
            (_cmp_cached_91) | (_cmp_cached_144) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 90.0))
          )
          # 1h & 4h down move, 4h still not low enough
          short_entry_logic.append(
            (_cmp_cached_91) | (_cmp_cached_116) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 80.0))
          )
          # 1h & 4h down move, 1h still not low enough
          short_entry_logic.append(
            (_cmp_cached_101) | (_cmp_cached_126) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 90.0))
          )
          # 1h & 4h down move, 4h still not low enough
          short_entry_logic.append(
            (_cmp_cached_101) | (_cmp_cached_126) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 80.0))
          )
          # 1h & 4h down move, 1h still not low enough
          short_entry_logic.append(
            (_cmp_cached_101) | (_cmp_cached_116) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 85.0))
          )
          # 1h & 4h down move, 1d still high
          short_entry_logic.append(
            (_cmp_cached_101) | (_cmp_cached_116) | (_cmp("STOCHRSIk_14_14_3_3_1d", ">", 50.0))
          )
          # 1h & 4h down move, 4h still not low enough
          short_entry_logic.append(
            (_cmp_cached_136) | (_cmp("RSI_3_4h", "<", 75.0)) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 85.0))
          )
          # 1h down move, 4h still high, 1d high
          short_entry_logic.append(
            (_cmp_cached_128) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 60.0)) | (_cmp("STOCHRSIk_14_14_3_3_1d", ">", 30.0))
          )
          # 1h & 4h down move, 1h still not low enough
          short_entry_logic.append(
            (_cmp_cached_128) | (_cmp_cached_116) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 75.0))
          )
          # 1h & 4h down move, 15m still high
          short_entry_logic.append(
            (_cmp_cached_128) | (_cmp("RSI_3_4h", "<", 80.0)) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 50.0))
          )
          # 1h & 4h down move, 4h still not low enough
          short_entry_logic.append(
            (_cmp("RSI_3_1h", "<", 75.0)) | (_cmp_cached_126) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 75.0))
          )
          # 1h & 4h down move, 1h still high
          short_entry_logic.append(
            (_cmp("RSI_3_1h", "<", 70.0)) | (_cmp_cached_116) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 60.0))
          )
          # 1h down move, 1h still not low enough, 4h still high
          short_entry_logic.append(
            (_cmp("RSI_3_1h", "<", 70.0)) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 80.0)) | (_cmp_cached_122)
          )
          # 4h down move, 15m still high, 1h still not low enough
          short_entry_logic.append(
            (_cmp_cached_116) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 60.0)) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 80.0))
          )
          # 4h down move, 15m still high, 4h still not low enough
          short_entry_logic.append(
            (_cmp("RSI_3_4h", "<", 75.0)) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 50.0)) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 75.0))
          )
          # 4h down move, 1h still not low enough, 1d still high
          short_entry_logic.append(
            (_cmp("RSI_3_4h", "<", 25.0)) | (_cmp_cached_147) | (_cmp("STOCHRSIk_14_14_3_3_1d", ">", 50.0))
          )
          # 15m & 1h still high, 4h high
          short_entry_logic.append(
            (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 70.0))
            | (_cmp_cached_147)
            | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 10.0))
          )
          # 15m still high, 1h & 1d high
          short_entry_logic.append(
            (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 60.0))
            | (_cmp_cached_148)
            | (_cmp("STOCHRSIk_14_14_3_3_1d", ">", 30.0))
          )
          # 15m & 4h high
          short_entry_logic.append((_cmp("STOCHRSIk_14_14_3_3_15m", ">", 50.0)) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 20.0)))
          # 15m high, 1h & 4h still not low enough
          short_entry_logic.append(
            (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 30.0))
            | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 75.0))
            | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 75.0))
          )
          # 15m & 4h high
          short_entry_logic.append((_cmp("STOCHRSIk_14_14_3_3_15m", ">", 30.0)) | (_cmp_cached_137))
          # 1h & 4h still high, 1d high
          short_entry_logic.append(
            (_cmp_cached_147)
            | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 70.0))
            | (_cmp("STOCHRSIk_14_14_3_3_1d", ">", 50.0))
          )
          # 1h & 4h high
          short_entry_logic.append((_cmp_cached_148) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 10.0)))
          # 1h & 4h high
          short_entry_logic.append((_cmp("STOCHRSIk_14_14_3_3_1h", ">", 20.0)) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 20.0)))
          # 4h & 1d high
          short_entry_logic.append((_cmp("STOCHRSIk_14_14_3_3_4h", ">", 20.0)) | (_cmp("STOCHRSIk_14_14_3_3_1d", ">", 20.0)))
          # 1d red, 1d high
          short_entry_logic.append((_cmp("change_pct_1d", "<", 5.0)) | (_cmp("STOCHRSIk_14_14_3_3_1d", ">", 20.0)))
          # 1d P&D, 1d high
          short_entry_logic.append(
            (_cmp("change_pct_1d", "<", 10.0))
            | (df["change_pct_1d"].shift(288) > -10.0)
            | (_cmp("STOCHRSIk_14_14_3_3_1d", ">", 50.0))
          )

          # Logic
          short_entry_logic.append(_cmp("RSI_4", ">", 54.0))
          short_entry_logic.append(_rsi_20_rising)
          short_entry_logic.append(df["close"] > df["SMA_16"] * 1.042)

        # Condition #661 - Scalp mode (Short).
        if short_entry_condition_index == 661:
          # Protections
          short_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)

          # 15m down move, 15m high
          short_entry_logic.append((_cmp("RSI_3_15m", "<", 75.0)) | (_cmp("AROOND_14_15m", "<", 80.0)))
          # 15m & 1h down move, 15m still high
          short_entry_logic.append((_cmp("RSI_3_15m", "<", 70.0)) | (_cmp("RSI_3_1h", "<", 40.0)) | (_cmp("AROOND_14_15m", "<", 50.0)))
          # 15m down move, 15m & 4h still high
          short_entry_logic.append(
            (_cmp("RSI_3_15m", "<", 70.0)) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 50.0)) | (_cmp_cached_122)
          )
          # 15m & 1h down move, 1h high
          short_entry_logic.append((_cmp("RSI_3_15m", "<", 60.0)) | (_cmp("RSI_3_1h", "<", 60.0)) | (_cmp("AROOND_14_1h", "<", 70.0)))
          # 15m & 1h down move, 1h still high
          short_entry_logic.append(
            (_cmp("RSI_3_15m", "<", 60.0)) | (_cmp("RSI_3_1h", "<", 60.0)) | (_cmp_cached_119)
          )
          # 15m & 1h down move, 4h high
          short_entry_logic.append((_cmp("RSI_3_15m", "<", 60.0)) | (_cmp("RSI_3_1h", "<", 40.0)) | (_cmp("AROOND_14_4h", "<", 80.0)))
          # 15m & 4h down move, 15m high
          short_entry_logic.append(
            (_cmp("RSI_3_15m", "<", 60.0)) | (_cmp("RSI_3_4h", "<", 60.0)) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 50.0))
          )
          # 15m & 4h down move, 15m high
          short_entry_logic.append(
            (_cmp("RSI_3_15m", "<", 60.0)) | (_cmp("RSI_3_4h", "<", 40.0)) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 30.0))
          )
          # 15m down move, 15m & 1h still high
          short_entry_logic.append(
            (_cmp("RSI_3_15m", "<", 60.0)) | (_cmp("AROOND_14_15m", "<", 50.0)) | (_cmp_cached_119)
          )
          # 15m down move, 15m & 1h still high
          short_entry_logic.append(
            (_cmp("RSI_3_15m", "<", 60.0)) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 50.0)) | (_cmp_cached_119)
          )
          # 15m down move, 4h still high, 1d overbought
          short_entry_logic.append((_cmp("RSI_3_15m", "<", 60.0)) | (_cmp("AROOND_14_4h", "<", 50.0)) | (_cmp("ROC_9_1d", ">", -100.0)))
          # 15m down move, 15m high, 4h still high
          short_entry_logic.append(
            (_cmp("RSI_3_15m", "<", 55.0)) | (_cmp("AROOND_14_15m", ">", 30.0)) | (_cmp_cached_122)
          )
          # 15m down move, 15m & 1h still high
          short_entry_logic.append(
            (_cmp("RSI_3_15m", "<", 55.0)) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 55.0)) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 60.0))
          )
          # 15m down move, 15m still not low enough, 4h high
          short_entry_logic.append(
            (_cmp("RSI_3_15m", "<", 50.0)) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 70.0)) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 10.0))
          )
          # 1h down move, 4h still high, 1d high
          short_entry_logic.append(
            (_cmp("RSI_3_1h", "<", 75.0)) | (_cmp("AROOND_14_4h", "<", 50.0)) | (_cmp("STOCHRSIk_14_14_3_3_1d", ">", 10.0))
          )
          short_entry_logic.append(
            (_cmp("RSI_3_1h", "<", 70.0)) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 60.0)) | (_cmp("STOCHRSIk_14_14_3_3_1d", ">", 10.0))
          )
          # 1h & 4h down move, 4h high
          short_entry_logic.append(
            (_cmp("RSI_3_1h", "<", 65.0)) | (_cmp("RSI_3_4h", "<", 40.0)) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 20.0))
          )
          # 1h down move, 15m & 1h still high
          short_entry_logic.append(
            (_cmp("RSI_3_1h", "<", 60.0)) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 50.0)) | (_cmp_cached_119)
          )
          # 1h down move, 1h still high, 4h high
          short_entry_logic.append(
            (_cmp("RSI_3_1h", "<", 60.0)) | (_cmp_cached_119) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 70.0))
          )
          # 1h down move, 1h high
          short_entry_logic.append((_cmp("RSI_3_1h", "<", 60.0)) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 40.0)))
          # 1h down move, 4h & 1d high
          short_entry_logic.append((_cmp("RSI_3_1h", "<", 60.0)) | (_cmp("AROOND_14_4h", "<", 85.0)) | (_cmp("AROOND_14_1d", "<", 90.0)))
          # 1h down move, 1h still high, 4h high
          short_entry_logic.append((_cmp("RSI_3_1h", "<", 55.0)) | (_cmp("AROOND_14_1h", "<", 50.0)) | (_cmp("AROOND_14_4h", "<", 90.0)))
          # 1h down move, 1h high
          short_entry_logic.append((_cmp("RSI_3_1h", "<", 55.0)) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 40.0)))
          # 1h & 4h down move, 15m high
          short_entry_logic.append((_cmp("RSI_3_1h", "<", 50.0)) | (_cmp("RSI_3_4h", "<", 40.0)) | (_cmp("AROOND_14_15m", "<", 70.0)))
          # 1h down move, 15m still high, 4h high
          short_entry_logic.append(
            (_cmp("RSI_3_1h", "<", 50.0)) | (_cmp("AROOND_14_15m", "<", 50.0)) | (_cmp("AROOND_14_4h", "<", 80.0))
          )
          # 1h down move, 15m high, 1h still high
          short_entry_logic.append(
            (_cmp("RSI_3_1h", "<", 50.0)) | (_cmp("AROOND_14_15m", "<", 70.0)) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 60.0))
          )
          # 1h down move, 15m still high, 4h high
          short_entry_logic.append(
            (_cmp("RSI_3_1h", "<", 50.0)) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 50.0)) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 20.0))
          )
          # 1h down move, 15m & 1h high
          short_entry_logic.append(
            (_cmp("RSI_3_1h", "<", 50.0)) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 40.0)) | (_cmp("AROOND_14_1h", "<", 60.0))
          )
          # 1h down move, 1h & 1d high
          short_entry_logic.append(
            (_cmp("RSI_3_1h", "<", 50.0)) | (_cmp("AROOND_14_1h", "<", 70.0)) | (_cmp("STOCHRSIk_14_14_3_3_1d", ">", 20.0))
          )
          # 1h down move, 4h still high, 1d high
          short_entry_logic.append(
            (_cmp("RSI_3_1h", "<", 50.0)) | (_cmp_cached_122) | (_cmp("STOCHRSIk_14_14_3_3_1d", ">", 10.0))
          )
          # 1h down move, 5m up move, 1h still high
          short_entry_logic.append(
            (_cmp("RSI_3_1h", "<", 40.0)) | (_cmp("RSI_3", ">", 40.0)) | (_cmp_cached_119)
          )
          # 1h down move, 15m still not low enough, 1h high
          short_entry_logic.append(
            (_cmp("RSI_3_1h", "<", 40.0)) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 70.0)) | (_cmp("AROOND_14_1h", "<", 70.0))
          )
          # 1h down move, 15m still not low enough, 1h high
          short_entry_logic.append(
            (_cmp("RSI_3_1h", "<", 40.0)) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 70.0)) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 40.0))
          )
          # 1h down move, 15m & 4h still high
          short_entry_logic.append(
            (_cmp("RSI_3_1h", "<", 40.0)) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 50.0)) | (_cmp_cached_122)
          )
          # 1h down move, 15m & 1h high
          short_entry_logic.append(
            (_cmp("RSI_3_1h", "<", 40.0)) | (_cmp("AROOND_14_15m", "<", 70.0)) | (_cmp("AROOND_14_1h", "<", 90.0))
          )
          # 1h down move, 1h still high, 4h high
          short_entry_logic.append(
            (_cmp("RSI_3_1h", "<", 40.0)) | (_cmp("AROOND_14_1h", "<", 50.0)) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 10.0))
          )
          # 1h down move, 1h high, 4h still high
          short_entry_logic.append((_cmp("RSI_3_1h", "<", 40.0)) | (_cmp("AROOND_14_1h", "<", 80.0)) | (_cmp("AROOND_14_4h", "<", 40.0)))
          # 1h down move, 1h still high, 4h high
          short_entry_logic.append(
            (_cmp("RSI_3_1h", "<", 40.0)) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 60.0)) | (_cmp("AROOND_14_4h", "<", 70.0))
          )
          # 1h down move, 1h & 1d high
          short_entry_logic.append(
            (_cmp("RSI_3_1h", "<", 40.0)) | (_cmp_cached_148) | (_cmp("AROOND_14_1d", "<", 90.0))
          )
          # 1h down move, 4h & 1d high
          short_entry_logic.append((_cmp("RSI_3_1h", "<", 40.0)) | (_cmp("RSI_14_4h", ">", 30.0)) | (_cmp("RSI_14_1d", ">", 20.0)))
          # 4h down move, 15m high
          short_entry_logic.append((_cmp("RSI_3_4h", "<", 80.0)) | (_cmp("AROOND_14_15m", "<", 80.0)))
          # 4h down move, 1h high
          short_entry_logic.append((_cmp("RSI_3_4h", "<", 75.0)) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 20.0)))
          # 4h down move, 1h & 4h still high
          short_entry_logic.append(
            (_cmp("RSI_3_4h", "<", 65.0)) | (_cmp_cached_119) | (_cmp("AROOND_14_4h", "<", 50.0))
          )
          # 4h down move, 15m & 1h high
          short_entry_logic.append(
            (_cmp("RSI_3_4h", "<", 60.0)) | (_cmp("AROOND_14_15m", "<", 80.0)) | (_cmp_cached_148)
          )
          # 4h down move, 15m still high, 1h high
          short_entry_logic.append(
            (_cmp("RSI_3_4h", "<", 60.0)) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 60.0)) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 20.0))
          )
          # 4h down move, 1h still high, 4h still moving down
          short_entry_logic.append(
            (_cmp("RSI_3_4h", "<", 60.0)) | (_cmp_cached_119) | (_cmp("CCI_20_change_pct_4h", "<", 0.0))
          )
          # 4h down move, 1h high, 4h still high
          short_entry_logic.append((_cmp("RSI_3_4h", "<", 55.0)) | (_cmp("AROOND_14_1h", "<", 70.0)) | (_cmp("AROOND_14_4h", "<", 50.0)))
          # 4h down move, 15m high, 4h still high
          short_entry_logic.append(
            (_cmp("RSI_3_4h", "<", 50.0)) | (_cmp("AROOND_14_15m", "<", 70.0)) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 60.0))
          )
          # 4h down move, 15m still high, 1h high
          short_entry_logic.append(
            (_cmp("RSI_3_4h", "<", 50.0)) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 60.0)) | (_cmp_cached_148)
          )
          # 4h down move, 15m & 4h still high
          short_entry_logic.append(
            (_cmp("RSI_3_4h", "<", 50.0)) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 50.0)) | (_cmp("AROOND_14_4h", "<", 50.0))
          )
          # 4h down move, 15m high, 4h still not low enough
          short_entry_logic.append(
            (_cmp("RSI_3_4h", "<", 50.0)) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 30.0)) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 70.0))
          )
          # 4h down move, 1h still high, 4h high
          short_entry_logic.append(
            (_cmp("RSI_3_4h", "<", 50.0)) | (_cmp_cached_119) | (_cmp("AROOND_14_4h", "<", 70.0))
          )
          # 4h down move, 15m & 4h high
          short_entry_logic.append(
            (_cmp("RSI_3_4h", "<", 40.0)) | (_cmp("AROOND_14_15m", "<", 70.0)) | (_cmp("AROOND_14_4h", "<", 70.0))
          )
          # 4h down move, 15m high, 4h still high
          short_entry_logic.append(
            (_cmp("RSI_3_4h", "<", 40.0)) | (_cmp("AROOND_14_15m", "<", 80.0)) | (_cmp("AROOND_14_4h", "<", 40.0))
          )
          # 4h down move, 15m still high, 4h high
          short_entry_logic.append(
            (_cmp("RSI_3_4h", "<", 40.0)) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 50.0)) | (_cmp_cached_137)
          )
          # 4h down move, 15m & 4h high
          short_entry_logic.append(
            (_cmp("RSI_3_4h", "<", 40.0)) | (_cmp("STOCHRSIk_14_14_3_3_15m", ">", 30.0)) | (_cmp("STOCHRSIk_14_14_3_3_4h", ">", 40.0))
          )
          # 4h down move, 1h & 4h high
          short_entry_logic.append(
            (_cmp("RSI_3_4h", "<", 40.0)) | (_cmp_cached_148) | (_cmp("AROOND_14_4h", "<", 70.0))
          )
          # 4h down move, 4h still high, 1d high
          short_entry_logic.append(
            (_cmp("RSI_3_4h", "<", 40.0)) | (_cmp_cached_122) | (_cmp("STOCHRSIk_14_14_3_3_1d", ">", 20.0))
          )
          # 15m high, 4h high
          short_entry_logic.append((_cmp("AROOND_14_15m", "<", 70.0)) | (_cmp("AROOND_14_4h", "<", 85.0)))
          # 15m high, 4h still high
          short_entry_logic.append((_cmp("AROOND_14_15m", "<", 80.0)) | (_cmp_cached_122))
          # 15m high, 1h still high
          short_entry_logic.append((_cmp("STOCHRSIk_14_14_3_3_15m", ">", 30.0)) | (_cmp("STOCHRSIk_14_14_3_3_1h", ">", 60.0)))
          # 15m & 4h high
          short_entry_logic.append((_cmp("STOCHRSIk_14_14_3_3_15m", ">", 30.0)) | (_cmp("AROOND_14_4h", "<", 70.0)))
          # 15m high, 1h still not low enough
          short_entry_logic.append((_cmp("STOCHRSIk_14_14_3_3_15m", ">", 20.0)) | (_cmp_cached_147))

          # Logic
          short_entry_logic.append(_cmp("RSI_14", ">", 50.0))
          short_entry_logic.append(_cmp("AROOND_14_15m", "<", 90.0))
          short_entry_logic.append(_cmp("STOCHRSIk_14_14_3_3_15m", ">", 10.0))
          if isinstance(df["SMA_200"].iloc[-1], np.float64):
            short_entry_logic.append(df["SMA_21"].shift(1) > df["SMA_200"].shift(1))
            short_entry_logic.append(df["SMA_21"] < df["SMA_200"])
          else:
            short_entry_logic.append(pd.Series([False]))
          if isinstance(df["EMA_200_1h"].iloc[-1], np.float64):
            short_entry_logic.append(df["close"] < df["EMA_200_1h"])
          else:
            short_entry_logic.append(pd.Series([False]))
          if isinstance(df["EMA_200_4h"].iloc[-1], np.float64):
            short_entry_logic.append(df["close"] < df["EMA_200_4h"])
          else:
            short_entry_logic.append(pd.Series([False]))
          short_entry_logic.append(_cmp("BBB_20_2.0_1h", ">", 4.0))

        ###############################################################################################

        # SHORT ENTRY CONDITIONS ENDS HERE

        ###############################################################################################

        short_entry_logic.append(_cmp("volume", ">", 0))
        item_short_entry = _and_conditions(short_entry_logic)
        _append_entry_tag(entry_tags, item_short_entry, f"{short_entry_condition_index} ")
        short_entry_conditions.append(item_short_entry)

    if short_entry_conditions:
      df.loc[:, "enter_short"] = _or_conditions(short_entry_conditions).astype(int)

    df.loc[:, "enter_tag"] = entry_tags
    return df

  ###############################################################################################

  # COMMON FUNCTIONS FOR BOTH LONG AND SHORT SIDE ENDS HERE

  ###############################################################################################

  #  /$$        /$$$$$$  /$$   /$$  /$$$$$$         /$$$$$$  /$$$$$$ /$$$$$$$  /$$$$$$$$
  # | $$       /$$__  $$| $$$ | $$ /$$__  $$       /$$__  $$|_  $$_/| $$__  $$| $$_____/
  # | $$      | $$  \ $$| $$$$| $$| $$  \__/      | $$  \__/  | $$  | $$  \ $$| $$
  # | $$      | $$  | $$| $$ $$ $$| $$ /$$$$      |  $$$$$$   | $$  | $$  | $$| $$$$$
  # | $$      | $$  | $$| $$  $$$$| $$|_  $$       \____  $$  | $$  | $$  | $$| $$__/
  # | $$      | $$  | $$| $$\  $$$| $$  \ $$       /$$  \ $$  | $$  | $$  | $$| $$
  # | $$$$$$$$|  $$$$$$/| $$ \  $$|  $$$$$$/      |  $$$$$$/ /$$$$$$| $$$$$$$/| $$$$$$$$
  # |________/ \______/ |__/  \__/ \______/        \______/ |______/|_______/ |________/

  # Long Side Functions for handling long orders
  # ---------------------------------------------------------------------------------------------

  ###############################################################################################

  # LONG EXIT FUNCTIONS STARTS HERE

  ###############################################################################################

  #
  #  /$$        /$$$$$$  /$$   /$$  /$$$$$$        /$$$$$$$$ /$$   /$$ /$$$$$$ /$$$$$$$$
  # | $$       /$$__  $$| $$$ | $$ /$$__  $$      | $$_____/| $$  / $$|_  $$_/|__  $$__/
  # | $$      | $$  \ $$| $$$$| $$| $$  \__/      | $$      |  $$/ $$/  | $$     | $$
  # | $$      | $$  | $$| $$ $$ $$| $$ /$$$$      | $$$$$    \  $$$$/   | $$     | $$
  # | $$      | $$  | $$| $$  $$$$| $$|_  $$      | $$__/     >$$  $$   | $$     | $$
  # | $$      | $$  | $$| $$\  $$$| $$  \ $$      | $$       /$$/\  $$  | $$     | $$
  # | $$$$$$$$|  $$$$$$/| $$ \  $$|  $$$$$$/      | $$$$$$$$| $$  \ $$ /$$$$$$   | $$
  # |________/ \______/ |__/  \__/ \______/       |________/|__/  |__/|______/   |__/
  #

  # Long Exit Normal
  # ---------------------------------------------------------------------------------------------
