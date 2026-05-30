"""Extracted entry-signal logic for TestX7.

This file is synced from the current upstream NostalgiaForInfinityX7 baseline.
Keep changes mechanical and parity-checked before reapplying entry-cache optimizations.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from freqtrade.persistence import Trade
from pandas import DataFrame

from test_x7_modules.masks import build_comparison_cache


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
    _test_x7_short_entries_enabled = any(bool(value) for value in self.short_entry_signal_params.values())
    _cmp_cached_0 = _cmp("RSI_3", ">", 3.0)
    _cmp_cached_1 = _cmp("RSI_3_15m", ">", 3.0)
    _cmp_cached_2 = _cmp("RSI_3_change_pct_1h", ">", -50.0)
    _cmp_cached_3 = _cmp("RSI_3_15m", ">", 5.0)
    _cmp_cached_4 = _cmp("RSI_14_4h", "<", 60.0)
    _cmp_cached_5 = _cmp("RSI_3_15m", ">", 10.0)
    _cmp_cached_6 = _cmp("AROONU_14_4h", "<", 100.0)
    _cmp_cached_7 = _cmp("RSI_3_1h", ">", 5.0)
    _cmp_cached_8 = _cmp("RSI_3", ">", 5.0)
    _cmp_cached_9 = _cmp("RSI_3_1h", ">", 10.0)
    _cmp_cached_10 = _cmp("AROONU_14_15m", "<", 30.0)
    _cmp_cached_11 = _cmp("RSI_3_1h", ">", 25.0)
    _cmp_cached_12 = _cmp("STOCHRSIk_14_14_3_3_4h", "<", 80.0)
    _cmp_cached_13 = _cmp("RSI_3_1h", ">", 3.0)
    _cmp_cached_14 = _cmp("STOCHRSIk_14_14_3_3_1d", "<", 50.0)
    _cmp_cached_15 = _cmp("RSI_3_1h", ">", 15.0)
    _cmp_cached_16 = _cmp("RSI_3_4h", ">", 25.0)
    _cmp_cached_17 = _cmp("AROONU_14_4h", "<", 70.0)
    _cmp_cached_18 = _cmp("AROONU_14_15m", "<", 80.0)
    _cmp_cached_19 = _cmp("STOCHRSIk_14_14_3_3_1h", "<", 80.0)
    _cmp_cached_20 = _cmp("ROC_9_4h", "<", 20.0)
    _cmp_cached_21 = _cmp("RSI_3_4h", ">", 35.0)
    _cmp_cached_22 = _cmp("RSI_3_15m", ">", 1.0)
    _cmp_cached_23 = _cmp("CMF_20_1h", ">", -0.1)
    _cmp_cached_24 = _cmp("AROONU_14_1h", "<", 70.0)
    _cmp_cached_25 = _cmp("RSI_3_4h", ">", 15.0)
    _cmp_cached_26 = _cmp("AROONU_14_1h", "<", 50.0)
    _cmp_cached_27 = _cmp("AROONU_14_1d", "<", 100.0)
    _cmp_cached_28 = _cmp("STOCHRSIk_14_14_3_3_1h", "<", 40.0)
    _cmp_cached_29 = _cmp("RSI_3_1d", ">", 15.0)
    _cmp_cached_30 = _cmp("RSI_3_1h", ">", 20.0)
    _cmp_cached_31 = _cmp("AROONU_14_15m", "<", 40.0)
    _cmp_cached_32 = _cmp("RSI_3_1h", ">", 30.0)
    _cmp_cached_33 = _cmp("AROONU_14_1h", "<", 80.0)
    _cmp_cached_34 = _cmp("RSI_3_1h", ">", 35.0)
    _cmp_cached_35 = _cmp("STOCHRSIk_14_14_3_3_4h", "<", 50.0)
    _cmp_cached_36 = _cmp("RSI_3_1h", ">", 40.0)
    _cmp_cached_37 = _cmp("STOCHRSIk_14_14_3_3_1h", "<", 70.0)
    _cmp_cached_38 = _cmp("RSI_3_1h", ">", 45.0)
    _cmp_cached_39 = _cmp("STOCHRSIk_14_14_3_3_1d", "<", 90.0)
    _cmp_cached_40 = _cmp("AROONU_14_4h", "<", 60.0)
    _cmp_cached_41 = _cmp("RSI_3_4h", ">", 30.0)
    _cmp_cached_42 = _cmp("ROC_9_1d", ">", -50.0)
    _cmp_cached_43 = _cmp("CMF_20_15m", ">", -0.40)
    _cmp_cached_44 = _cmp("ROC_9_15m", ">", -20.0)
    _cmp_cached_45 = _cmp("AROONU_14_1h", "<", 85.0)
    _cmp_cached_46 = _cmp("AROONU_14_4h", "<", 90.0)
    _cmp_cached_47 = _cmp("AROONU_14_4h", "<", 85.0)
    _cmp_cached_48 = _cmp("ROC_9_1d", "<", 100.0)
    _cmp_cached_49 = _cmp("STOCHRSIk_14_14_3_3_1h", "<", 90.0)
    _cmp_cached_50 = _cmp("ROC_9_4h", "<", 10.0)
    _cmp_cached_51 = _cmp("ROC_9_4h", "<", 30.0)
    _cmp_cached_52 = _cmp("ROC_9_1d", "<", 40.0)
    _cmp_cached_53 = _cmp("RSI_3_1h", ">", 60.0)
    _cmp_cached_54 = _cmp("ROC_9_1h", "<", 40.0)
    _cmp_cached_55 = _cmp("RSI_3_4h", ">", 5.0)
    _cmp_cached_56 = _cmp("STOCHRSIk_14_14_3_3_1d", "<", 40.0)
    _cmp_cached_57 = _cmp("ROC_9_1d", ">", -20.0)
    _cmp_cached_58 = _cmp("RSI_3_4h", ">", 10.0)
    _cmp_cached_59 = _cmp("STOCHRSIk_14_14_3_3_1h", "<", 50.0)
    _cmp_cached_60 = _cmp("STOCHRSIk_14_14_3_3_1d", "<", 60.0)
    _cmp_cached_61 = _cmp("STOCHRSIk_14_14_3_3_15m", "<", 50.0)
    _cmp_cached_62 = _cmp("AROONU_14_15m", "<", 50.0)
    _cmp_cached_63 = _cmp("ROC_9_1d", "<", 80.0)
    _cmp_cached_64 = _cmp("STOCHRSIk_14_14_3_3_4h", "<", 70.0)
    _cmp_cached_65 = _cmp("ROC_9_1d", ">", -40.0)
    _cmp_cached_66 = _cmp("RSI_14_4h", "<", 80.0)
    _cmp_cached_67 = _cmp("ROC_9_4h", "<", 80.0)
    _cmp_cached_68 = _cmp("AROONU_14_1h", "<", 75.0)
    _cmp_cached_69 = _cmp("ROC_9_4h", ">", -20.0)
    _cmp_cached_70 = _cmp("ROC_9_1d", "<", 30.0)
    _cmp_cached_71 = _cmp("RSI_3_4h", ">", 60.0)
    _cmp_cached_72 = _cmp("STOCHRSIk_14_14_3_3_4h", "<", 90.0)
    _cmp_cached_73 = _cmp("RSI_3_1d", ">", 50.0)
    _cmp_cached_74 = _cmp("STOCHRSIk_14_14_3_3_1d", "<", 80.0)
    _cmp_cached_75 = _cmp("CMF_20_15m", ">", -0.3)
    _cmp_cached_76 = _cmp("AROONU_14_15m", "<", 70.0)
    _cmp_cached_77 = _cmp("AROONU_14_4h", "<", 80.0)
    _cmp_cached_78 = _cmp("AROONU_14_1h", "<", 90.0)
    _cmp_cached_79 = _cmp("ROC_9_1h", "<", 20.0)
    _cmp_cached_80 = _cmp("AROONU_14_1h", "<", 100.0)
    _cmp_cached_81 = _cmp("ROC_9_4h", ">", -25.0)
    _cmp_cached_82 = _cmp("ROC_9_1h", "<", 10.0)
    _cmp_cached_83 = _cmp("ROC_9_4h", "<", 60.0)
    _cmp_cached_84 = _cmp("RSI_3_15m", ">", 15.0)
    _cmp_cached_85 = _cmp("RSI_14_15m", "<", 50.0)
    _cmp_cached_86 = _cmp("ROC_9_4h", "<", 50.0)
    _cmp_cached_87 = _cmp("RSI_3_15m", ">", 20.0)
    _cmp_cached_88 = _cmp("RSI_3_15m", ">", 25.0)
    _cmp_cached_89 = _cmp("RSI_3_15m", ">", 30.0)
    _cmp_cached_90 = _cmp("RSI_3_15m", ">", 40.0)
    _cmp_cached_91 = _cmp("RSI_3_4h", ">", 45.0)
    _cmp_cached_92 = _cmp("STOCHRSIk_14_14_3_3_15m", "<", 70.0)
    _cmp_cached_93 = _cmp("ROC_9_4h", ">", -10.0)
    _cmp_cached_94 = _cmp("AROONU_14_1d", "<", 90.0)
    _cmp_cached_95 = _cmp("ROC_9_1d", "<", 10.0)
    _cmp_cached_96 = _cmp("AROONU_14_4h", "<", 40.0)
    _cmp_cached_97 = _cmp("CMF_20_1h", ">", -0.3)
    _cmp_cached_98 = _cmp("AROONU_14_4h", "<", 30.0)
    _cmp_cached_99 = _cmp("RSI_3_4h", ">", 50.0)
    _cmp_cached_100 = _cmp("RSI_3_4h", ">", 20.0)
    _cmp_cached_101 = _cmp("RSI_3_1d", ">", 5.0)
    _cmp_cached_102 = _cmp("ROC_9_1d", ">", -30.0)
    _cmp_cached_103 = _cmp("ROC_9_4h", ">", -30.0)
    _cmp_cached_104 = _cmp("RSI_3_1d", ">", 20.0)
    _cmp_cached_105 = _cmp("RSI_14_4h", "<", 75.0)
    _cmp_cached_106 = _cmp("AROONU_14_1d", "<", 70.0)
    _cmp_cached_107 = _cmp("ROC_9_1d", "<", 50.0)
    _cmp_cached_108 = _cmp("AROONU_14_1d", "<", 80.0)
    _cmp_cached_109 = _cmp("ROC_9_1h", ">", -30.0)
    _cmp_cached_110 = _cmp("AROONU_14_1h", "<", 40.0)
    _cmp_cached_111 = _cmp("ROC_9_1d", "<", 200.0)
    _cmp_cached_112 = _cmp("ROC_9_1d", "<", 60.0)
    _cmp_cached_113 = _cmp("ROC_9_4h", "<", 40.0)
    _cmp_cached_114 = _cmp("CMF_20_1h", ">", -0.25)
    _cmp_cached_115 = _cmp("AROONU_14_1h", "<", 60.0)
    _cmp_cached_116 = _cmp("ROC_9_15m", ">", -15.0)
    _cmp_cached_117 = _cmp("RSI_3_1h", ">", 50.0)
    _cmp_cached_118 = _cmp("RSI_14_4h", "<", 90.0)
    _cmp_cached_119 = _cmp("AROONU_14_1d", "<", 40.0)
    _cmp_cached_120 = _cmp("AROONU_14_4h", "<", 20.0)
    _cmp_cached_121 = _cmp("RSI_3_1d", ">", 25.0)
    _cmp_cached_122 = _cmp("AROONU_14_4h", "<", 50.0)
    _cmp_cached_123 = _cmp("STOCHRSIk_14_14_3_3_1h", "<", 60.0)
    _cmp_cached_124 = _cmp("STOCHRSIk_14_14_3_3_4h", "<", 30.0)
    _cmp_cached_125 = _cmp("RSI_3_1d", ">", 40.0)
    _cmp_cached_126 = _cmp("RSI_3_1d", ">", 60.0)
    _cmp_cached_127 = _cmp("RSI_3_change_pct_1h", ">", -75.0)
    _cmp_cached_128 = _cmp("CMF_20_4h", ">", -0.3)
    _cmp_cached_129 = _cmp("ROC_9_1h", ">", -20.0)
    _cmp_cached_130 = _cmp("ROC_9_1h", ">", -15.0)
    _cmp_cached_131 = _cmp("AROONU_14_1d", "<", 85.0)
    _cmp_cached_132 = _cmp("ROC_9_1h", ">", -10.0)
    _cmp_cached_133 = _cmp("ROC_2", ">", -10.0)
    _cmp_cached_134 = _cmp("ROC_9", ">", -15.0)
    _cmp_cached_135 = _cmp("ROC_9_1h", ">", -25.0)
    _cmp_cached_136 = _cmp("change_pct_1d", ">", -5.0)
    _cmp_cached_137 = _cmp("CMF_20_1d", ">", -0.0)
    _cmp_cached_138 = _cmp("change_pct_1d", "<", 20.0)
    _cmp_cached_139 = _cmp("top_wick_pct_1d", "<", 15.0)
    _cmp_cached_140 = _cmp("change_pct_1d", "<", 25.0)
    _cmp_cached_141 = _cmp("top_wick_pct_1d", "<", 25.0)
    _cmp_cached_142 = _cmp("change_pct_1d", "<", 40.0)
    _cmp_cached_143 = _cmp("CMF_20_1d", ">", -0.2)
    _cmp_cached_144 = _cmp("change_pct_1d", "<", 50.0)
    _cmp_cached_145 = _cmp("top_wick_pct_1d", "<", 30.0)
    _cmp_cached_146 = _cmp("CMF_20_15m", ">", -0.5)
    _cmp_cached_147 = _cmp("STOCHRSIk_14_14_3_3_1h", "<", 45.0)
    _cmp_cached_148 = _cmp("STOCHRSIk_14_14_3_3_1d", "<", 70.0)
    _cmp_cached_149 = _cmp("ROC_9_1d", ">", -15.0)
    _cmp_cached_150 = _cmp("AROONU_14_1h", "<", 30.0)
    _cmp_cached_151 = _cmp("RSI_3_4h", ">", 3.0)
    _cmp_cached_152 = _cmp("STOCHRSIk_14_14_3_3_15m", "<", 30.0)
    _cmp_cached_153 = _cmp("RSI_3_1d", ">", 10.0)
    _cmp_cached_154 = _cmp("CMF_20_1d", ">", -0.25)
    _cmp_cached_155 = _cmp("STOCHRSIk_14_14_3_3_15m", "<", 40.0)
    _cmp_cached_156 = _cmp("STOCHRSIk_14_14_3_3_4h", "<", 20.0)
    _cmp_cached_157 = _cmp("RSI_3", ">", 10.0)
    _cmp_cached_158 = _cmp("ROC_9_1h", "<", 30.0)
    _cmp_cached_159 = _cmp("CMF_20_15m", ">", -0.30)
    _cmp_cached_160 = _cmp("AROONU_14_1h", "<", 25.0)
    _cmp_cached_161 = _cmp("STOCHRSIk_14_14_3_3_1h", "<", 30.0)
    _cmp_cached_162 = _cmp("STOCHRSIk_14_14_3_3_4h", "<", 60.0)
    _cmp_cached_163 = _cmp("RSI_14_4h", "<", 30.0)
    _cmp_cached_164 = _cmp("CMF_20_4h", ">", -0.35)
    _cmp_cached_165 = _cmp("STOCHRSIk_14_14_3_3_4h", "<", 40.0)
    _cmp_cached_166 = _cmp("AROONU_14_15m", "<", 20.0)
    _cmp_cached_167 = _cmp("ROC_9_1d", "<", 20.0)
    _cmp_cached_168 = _cmp("CMF_20_15m", ">", -0.35)
    _cmp_cached_169 = _cmp("RSI_14_4h", "<", 40.0)
    _cmp_cached_170 = _cmp("RSI_14_1d", "<", 50.0)
    _cmp_cached_171 = _cmp("STOCHRSIk_14_14_3_3_15m", "<", 20.0)
    _cmp_cached_172 = _cmp("AROONU_14_4h", "<", 75.0)
    _cmp_cached_173 = _cmp("RSI_14_4h", "<", 50.0)
    _cmp_cached_174 = _cmp("RSI_3_1h", ">", 55.0)
    _cmp_cached_175 = _cmp("RSI_3_4h", ">", 55.0)
    _cmp_cached_176 = _cmp("RSI_14_1d", "<", 40.0)
    _cmp_cached_177 = _cmp("CMF_20_1h", ">", -0.30)
    _cmp_cached_178 = _cmp("RSI_3_1d", ">", 30.0)
    _cmp_cached_179 = _cmp("AROONU_14_15m", "<", 25.0)
    _cmp_cached_180 = _cmp("STOCHRSIk_14_14_3_3_15m", "<", 80.0)
    _cmp_cached_181 = _cmp("RSI_3_4h", ">", 40.0)
    _cmp_cached_182 = _cmp("ROC_9_1h", "<", 100.0)
    _cmp_cached_183 = _cmp("ROC_9_1h", "<", 50.0)
    _cmp_cached_184 = _cmp("RSI_3_15m", ">", 35.0)
    _cmp_cached_185 = _cmp("RSI_3_1h", ">", 1.0)
    _cmp_cached_186 = _cmp("ROC_9_1d", ">", -10.0)
    _cmp_cached_187 = _cmp("ROC_9_15m", ">", -30.0)
    _cmp_cached_188 = _cmp("AROONU_14_1h", "<", 20.0)
    _cmp_cached_189 = _cmp("CMF_20_4h", ">", -0.30)
    _cmp_cached_190 = _cmp("STOCHRSIk_14_14_3_3_1h", "<", 20.0)
    _cmp_cached_191 = _cmp("RSI_14_1d", "<", 60.0)
    _cmp_cached_192 = _cmp("RSI_3_1d", ">", 35.0)
    _cmp_cached_193 = _cmp("CMF_20_4h", ">", -0.50)
    _cmp_cached_194 = _cmp("ROC_9_1d", ">", -60.0)
    _cmp_cached_195 = _cmp("ROC_9_1d", ">", -25.0)
    _cmp_cached_196 = _cmp("ROC_9_4h", "<", 100.0)
    _cmp_cached_197 = _cmp("RSI_3_4h", ">", 65.0)
    _cmp_cached_198 = _cmp("RSI_3_1d", ">", 45.0)
    _cmp_cached_199 = _cmp("AROONU_14_1d", "<", 60.0)
    _cmp_cached_200 = _cmp("CMF_20_4h", ">", -0.40)
    _cmp_cached_201 = _cmp("ROC_9_1d", "<", 25.0)
    _cmp_cached_202 = _cmp("CMF_20_1d", ">", -0.40)
    _cmp_cached_203 = _cmp("ROC_9", ">", -40.0)
    _cmp_cached_204 = _cmp("ROC_9_4h", ">", -50.0)
    _cmp_cached_205 = _cmp("ROC_9_1h", "<", 25.0)
    _cmp_cached_206 = _cmp("ROC_9_1d", ">", -70.0)
    _cmp_cached_207 = _cmp("AROONU_14", "<", 30.0)
    _cmp_cached_208 = _cmp("STOCHRSIk_14_14_3_3", "<", 30.0)
    _cmp_cached_209 = _cmp("RSI_3", ">", 15.0)
    _cmp_cached_210 = _cmp("AROONU_14_15m", "<", 60.0)
    _cmp_cached_211 = _cmp("ROC_9_4h", "<", 25.0)
    _cmp_cached_212 = _cmp("AROONU_14_15m", "<", 75.0)
    _cmp_cached_213 = _cmp("ROC_9_4h", ">", -40.0)
    _cmp_cached_214 = _cmp("AROONU_14_1d", "<", 75.0)
    _cmp_cached_215 = _cmp("RSI_14_1d", "<", 70.0)
    _cmp_cached_216 = _cmp("ROC_9_1d", "<", 70.0)
    _cmp_cached_217 = _cmp("ROC_9_4h", "<", 70.0)
    _cmp_cached_218 = _cmp("ROC_9_1d", ">", -80.0)
    _cmp_cached_219 = _cmp("ROC_9_4h", ">", -15.0)
    _cmp_cached_220 = _cmp("CMF_20_1d", ">", -0.20)
    _cmp_cached_221 = _cmp("RSI_3_1h", ">", 65.0)
    _cmp_cached_222 = _cmp("STOCHRSIk_14_14_3_3_15m", "<", 60.0)
    _cmp_cached_223 = _cmp("RSI_3_1d", ">", 55.0)
    _cmp_cached_224 = _cmp("CMF_20_1d", ">", -0.30)
    _cmp_cached_225 = _cmp("RSI_3_1d", ">", 3.0)
    _cmp_cached_226 = _cmp("ROC_9_15m", "<", 10.0)
    _cmp_cached_227 = _cmp("STOCHRSIk_14_14_3_3_15m", "<", 90.0)
    _cmp_cached_228 = _cmp("change_pct_1d", ">", -50.0)
    _cmp_cached_229 = _cmp("change_pct_1d", ">", -20.0)
    _cmp_cached_230 = _cmp("top_wick_pct_1d", "<", 20.0)
    _cmp_cached_231 = _cmp("change_pct_1d", ">", -10.0)
    _cmp_cached_232 = _cmp("change_pct_1d", "<", 15.0)
    _cmp_cached_233 = _cmp("top_wick_pct_1d", "<", 50.0)
    _cmp_cached_234 = _cmp("RSI_4", "<", 45.0)
    _cmp_cached_235 = _cmp("RSI_14", ">", 30.0)
    _cmp_cached_236 = _cmp("AROONU_14", "<", 20.0)
    _cmp_cached_237 = _cmp("STOCHRSIk_14_14_3_3", "<", 20.0)
    _cmp_cached_238 = _cmp("AROONU_14_1d", "<", 50.0)
    _cmp_cached_239 = _cmp("ROC_9_1h", ">", -40.0)
    _cmp_cached_240 = _cmp("CMF_20_1h", ">", -0.40)
    _cmp_cached_241 = _cmp("ROC_9_15m", ">", -50.0)
    _cmp_cached_242 = _cmp("ROC_9_1h", "<", 80.0)
    _cmp_cached_243 = _cmp("AROONU_14", "<", 25.0)
    _cmp_cached_244 = _cmp("RSI_3_15m", "<", 30.0)
    _cmp_cached_245 = _cmp("RSI_3_15m", ">", 45.0)
    _cmp_cached_246 = _cmp("ROC_9_1d", "<", 15.0)
    _cmp_cached_247 = _cmp("RSI_3", "<", 50.0)
    _cmp_cached_248 = _cmp("ROC_9_1d", "<", 150.0)
    _cmp_cached_249 = _cmp("RSI_3_15m", ">", 50.0)
    _cmp_cached_250 = _cmp("RSI_14_1d", "<", 80.0)
    _cmp_cached_251 = _cmp("AROONU_14_1d", "<", 20.0)
    _cmp_cached_252 = _cmp("CMF_20_4h", ">", -0.25)
    _cmp_cached_253 = _cmp("CMF_20_4h", ">", -0.10)
    _cmp_cached_254 = _cmp("RSI_3", "<", 46.0)
    _cmp_cached_255 = _cmp("ROC_9_4h", "<", 200.0)
    _cmp_cached_256 = _cmp("ROC_9_1h", "<", 60.0)
    _cmp_cached_257 = _cmp("ROC_9_1d", "<", 250.0)
    _cmp_cached_258 = _cmp("RSI_3_1d", ">", 65.0)
    _cmp_cached_259 = _cmp("ROC_9_15m", ">", -40.0)
    _cmp_cached_260 = _cmp("STOCHRSIk_14_14_3_3_1h", "<", 75.0)
    _cmp_cached_261 = _cmp("ROC_9_15m", ">", -10.0)
    _cmp_cached_262 = _cmp("AROONU_14_4h", "<", 100.00)
    _cmp_cached_263 = _cmp("ROC_9_4h", "<", 15.0)
    _cmp_cached_264 = _cmp("ROC_9_1h", ">", -50.0)
    _cmp_cached_265 = _cmp("STOCHRSIk_14_14_3_3_1d", "<", 20.0)
    _cmp_cached_266 = _cmp("ROC_9_4h", ">", -35.0)
    _cmp_cached_267 = _cmp("ROC_9_1d", "<", 35.0)
    _cmp_cached_268 = _cmp("ROC_9_15m", ">", -25.0)
    _cmp_cached_269 = _cmp("AROONU_14_1d", "<", 30.0)
    _cmp_cached_270 = _cmp("ROC_9_1d", ">", -35.0)
    _cmp_cached_271 = _cmp("RSI_14", "<", 36.0)
    _cmp_cached_272 = _cmp("AROOND_14", ">", 75.0)
    _cmp_cached_273 = _cmp("STOCHRSIk_14_14_3_3_1d", "<", 30.0)
    _cmp_cached_274 = _cmp("AROONU_14_15m", "<", 90.0)
    _cmp_cached_275 = _cmp("CMF_20_1d", ">", -0.50)
    _cmp_cached_276 = _cmp("AROONU_14_15m", "<", 85.0)
    _cmp_cached_277 = _cmp("WILLR_14", "<", -50.0)
    _cmp_cached_278 = _cmp("WILLR_84_1h", "<", -70.0)
    _cmp_cached_279 = _cmp("BBB_20_2.0_1h", ">", 16.0)
    _cmp_cached_280 = _cmp("ROC_9_4h", ">", -70.0)
    _cmp_cached_281 = _cmp("STOCHRSIk_14_14_3_3_1h", "<", 85.0)
    _cmp_cached_282 = _cmp("RSI_14", "<", 40.0)
    _cmp_cached_283 = _cmp("MFI_14", "<", 40.0)
    _cmp_cached_284 = _cmp("ROC_9_1h", ">", -70.0)
    _cmp_cached_285 = _cmp("ROC_9_15m", ">", -60.0)
    _cmp_cached_286 = _cmp("ROC_9_1h", ">", -60.0)
    _cmp_cached_287 = _cmp("RSI_3", "<", 40.0)
    _cmp_cached_288 = _cmp("RSI_3_15m", "<", 50.0)
    _cmp_cached_289 = _cmp("RSI_14_4h", "<", 35.0)
    _cmp_cached_290 = _cmp("STOCHRSIk_14_14_3_3_1h", "<", 25.0)
    _cmp_cached_291 = _cmp("ROC_2", ">", -0.0)
    _cmp_cached_292 = _cmp("RSI_14_15m", "<", 40.0)
    _cmp_cached_293 = _cmp("top_wick_pct_1d", "<", 40.0)
    _cmp_cached_294 = _cmp("RSI_14_1h", "<", 30.0)
    _cmp_cached_295 = _cmp("AROONU_14_15m", "<", 15.0)
    _cmp_cached_296 = _cmp("RSI_14_1h", "<", 40.0)
    _cmp_cached_297 = _cmp("AROONU_14_4h", "<", 65.0)
    _cmp_cached_298 = _cmp("RSI_14_15m", "<", 30.0)
    _cmp_cached_299 = _cmp("top_wick_pct_4h", "<", 20.0)
    _cmp_cached_300 = _cmp("WILLR_14_15m", "<", -50.0)
    _cmp_cached_301 = _cmp("BBB_20_2.0_1h", ">", 12.0)
    _cmp_cached_302 = _cmp("CMF_20_15m", ">", -0.50)
    _cmp_cached_303 = _cmp("CMF_20_4h", ">", -0.20)
    _cmp_cached_304 = _cmp("RSI_3_15m", "<", 40.0)
    _cmp_cached_305 = _cmp("RSI_3_1h", ">", 2.0)
    _cmp_cached_306 = _cmp("CMF_20_1h", ">", -0.20)
    _cmp_cached_307 = _cmp("AROONU_14_15m", "<", 45.0)
    _cmp_cached_308 = _cmp("change_pct_1d", "<", 30.0)
    _cmp_cached_309 = _cmp("RSI_3", ">", 0.0)
    _cmp_cached_310 = _cmp("RSI_14_1h", "<", 80.0)
    _cmp_cached_311 = _cmp("STOCHRSIk_14_14_3_3_15m", "<", 10.0)
    _cmp_cached_312 = _cmp("STOCHRSIk_14_14_3_3_4h", "<", 75.0)
    _cmp_cached_313 = _cmp("change_pct_1d", ">", -30.0)
    _cmp_cached_314 = _cmp("STOCHRSIk_14_14_3_3_15m", "<", 25.0)
    _cmp_cached_315 = _cmp("RSI_14_15m", "<", 35.0)
    _cmp_cached_316 = _cmp("RSI_14_4h", "<", 85.0)
    _cmp_cached_317 = _cmp("STOCHRSIk_14_14_3_3_4h", "<", 85.0)
    _cmp_cached_318 = _cmp("change_pct", ">", -5.0)
    _cmp_cached_319 = _cmp("WILLR_14", "<", -95.0)
    _cmp_cached_320 = _cmp("STOCHRSIk_14_14_3_3", "<", 10.0)
    _cmp_cached_321 = _cmp("RSI_14_15m", "<", 45.0)
    _cmp_cached_322 = _cmp("RSI_14", ">", 35.0)
    _cmp_cached_323 = _cmp("CMF_20_15m", ">", -0.20)
    _cmp_cached_324 = _cmp("CCI_20_change_pct_1h", ">", -0.0)
    _cmp_cached_325 = _cmp("RSI_14_15m", "<", 10.0)
    _cmp_cached_326 = _cmp("RSI_14_1h", "<", 10.0)
    _cmp_cached_327 = _cmp("RSI_3", "<=", 50.0)
    _cmp_cached_328 = _cmp("RSI_3_15m", ">=", 20.0)
    _cmp_cached_329 = _cmp("RSI_3_1h", ">=", 10.0)
    _cmp_cached_330 = _cmp("RSI_3_4h", ">=", 10.0)
    _cmp_cached_331 = _cmp("WILLR_14", "<", -80.0)
    _cmp_cached_332 = _cmp("STOCHRSIk_14_14_3_3_4h", "<", 10.0)
    _cmp_cached_333 = _cmp("RSI_3", "<", 30.0)
    _cmp_cached_334 = _cmp("ROC_9_4h", "<", 5.0)
    _cmp_cached_335 = _cmp("RSI_4", "<", 46.0)
    _cmp_cached_336 = _cmp("RSI_14_4h", "<", 20.0)
    _cmp_cached_337 = _cmp("RSI_3_1d", ">", 70.0)
    _cmp_cached_338 = _cmp("STOCHRSIk_14_14_3_3_15m", "<", 45.0)
    _cmp_cached_339 = _cmp("RSI_3_15m", ">", 55.0)
    _cmp_cached_340 = _cmp("RSI_3", "<", 60.0)
    _cmp_cached_341 = _cmp("RSI_14_4h", "<", 70.0)
    _cmp_cached_342 = _cmp("CCI_20_change_pct_4h", ">", -0.0)
    _cmp_cached_343 = _cmp("RSI_14", "<", 50.0)
    _cmp_cached_344 = _cmp("BBB_20_2.0", ">", 1.5)
    _cmp_cached_345 = _cmp("BBB_20_2.0_1h", ">", 6.0)
    _cmp_cached_346 = _cmp("RSI_14_1h", "<", 50.0)
    _cmp_cached_347 = _cmp("change_pct_1h", ">", -10.0)
    _cmp_cached_348 = _cmp("change_pct_4h", ">", -15.0)
    _cmp_cached_349 = _cmp("change_pct_4h", "<", 10.0)
    _cmp_cached_350 = _cmp("change_pct_4h", "<", 40.0)
    _cmp_cached_351 = _cmp("change_pct_4h", "<", 50.0)
    _cmp_cached_352 = _cmp("change_pct_1d", "<", 10.0)
    _cmp_cached_353 = _cmp("top_wick_pct_1d", "<", 8.0)
    _cmp_cached_354 = _cmp("RSI_3", ">", 20.0)
    _cmp_cached_355 = _cmp("RSI_3_15m", ">", 12.0)
    _cmp_cached_356 = _cmp("CMF_20_1h", ">", -0.10)
    _cmp_cached_357 = _cmp("MFI_14_4h", "<", 85.0)
    _cmp_cached_358 = _cmp("RSI_3_4h", "<", 90.0)
    _cmp_cached_359 = _cmp("RSI_3_1d", "<", 80.0)
    _cmp_cached_360 = _cmp("CMF_20_4h", ">", -0.2)
    _cmp_cached_361 = _cmp("CMF_20_4h", ">", -0.0)
    _cmp_cached_362 = _cmp("CMF_20_15m", ">", -0.4)
    _cmp_cached_363 = _cmp("STOCHRSIk_14_14_3_3_4h", "<", 95.0)
    _cmp_cached_364 = _cmp("MFI_14_1h", "<", 80.0)
    _cmp_cached_365 = _cmp("AROONU_14_15m", "<", 65.0)
    _cmp_cached_366 = _cmp("CMF_20_4h", ">", -0.4)
    _cmp_cached_367 = _cmp("RSI_3_4h", ">", 70.0)
    _cmp_cached_368 = _cmp("RSI_3", "<", 45.0)
    _cmp_cached_369 = _cmp("RSI_14_15m", ">", 25.0)
    _cmp_cached_370 = _cmp("RSI_14_15m", ">", 30.0)
    _cmp_cached_371 = _cmp("CMF_20_1h", ">", -0.2)
    _cmp_cached_372 = _cmp("top_wick_pct_4h", "<", 10.0)
    _cmp_cached_373 = _cmp("change_pct_1d", ">", -15.0)
    _cmp_cached_374 = _cmp("CMF_20_1d", ">", -0.1)
    _cmp_cached_375 = _cmp("top_wick_pct_1d", "<", 10.0)
    _cmp_cached_376 = _cmp("RSI_14", "<", 30.0)
    _cmp_cached_377 = _cmp("volume", ">", 0)

    is_backtest = self.dp.runmode.value in ["backtest", "hyperopt", "plot", "webserver"]
    # Grind mode
    pair_coin = metadata["pair"].partition("/")[0]
    num_open_long_grind_mode = 0
    is_pair_long_grind_mode = pair_coin in self.grind_mode_coins
    if not is_backtest:
      open_trades = Trade.get_trades_proxy(is_open=True)
      for open_trade in open_trades:
        enter_tag = open_trade.enter_tag
        if enter_tag is not None:
          enter_tags = enter_tag.split()
          if all(c in self.long_grind_mode_tags for c in enter_tags):
            num_open_long_grind_mode += 1
    # Top Coins mode
    is_pair_long_top_coins_mode = pair_coin in self.top_coins_mode_coins
    is_pair_short_top_coins_mode = pair_coin in self.top_coins_mode_coins
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
      long_entry_condition_index = int(enabled_long_entry_signal.rsplit("_", 2)[1])
      item_buy_protection_list = [True]
      if self.long_entry_signal_params[enabled_long_entry_signal]:
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
            ((_cmp_cached_0) | (_cmp_cached_1) | (_cmp_cached_2))
            # 5m & 15m down move, 5h high
            & ((_cmp_cached_0) | (_cmp_cached_3) | (_cmp_cached_4))
            # 5m & 15m down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_5) | (_cmp_cached_6))
            # 5m & 1h down move
            & ((_cmp_cached_0) | (_cmp_cached_7))
            # 5m & 1h down move, 15m still not low enough
            & ((_cmp_cached_8) | (_cmp_cached_9) | (_cmp_cached_10))
            # 5m & 1h down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_11) | (_cmp_cached_12))
            # 15m & 1h down move, 1d still high
            & ((_cmp_cached_1) | (_cmp_cached_13) | (_cmp_cached_14))
            # 5m & 1h down move, 15m still not low enough
            & ((_cmp_cached_0) | (_cmp_cached_15) | (_cmp_cached_10))
            # 5m & 4h down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_16) | (_cmp_cached_17))
            # 5m down move, 15m high
            & ((_cmp_cached_0) | (_cmp_cached_18))
            # 5m down move, 1h high, 4h overbought
            & ((_cmp_cached_0) | (_cmp_cached_19) | (_cmp_cached_20))
            # 5m & 4h down move, 4h high
            & ((_cmp_cached_8) | (_cmp_cached_21) | (_cmp_cached_17))
            # 15m down move, 1h downtrend, 1h high
            & ((_cmp_cached_22) | (_cmp_cached_23) | (_cmp_cached_24))
            # 15m & 1h & 4h down move
            & ((_cmp_cached_1) | (_cmp_cached_9) | (_cmp_cached_25))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_1) | (_cmp_cached_9) | (_cmp_cached_26))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_1) | (_cmp_cached_9) | (_cmp_cached_27))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_1) | (_cmp_cached_9) | (_cmp_cached_28))
            # 15m & 1h & 4h & 1d down move
            & ((_cmp_cached_1) | (_cmp_cached_15) | (_cmp_cached_25) | (_cmp_cached_29))
            # 15m & 1h down move, 15m still high
            & ((_cmp_cached_1) | (_cmp_cached_30) | (_cmp_cached_31))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_1) | (_cmp_cached_30) | (_cmp_cached_24))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_1) | (_cmp_cached_32) | (_cmp_cached_33))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_1) | (_cmp_cached_34) | (_cmp_cached_35))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_1) | (_cmp_cached_36) | (_cmp_cached_37))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_1) | (_cmp_cached_38) | (_cmp_cached_33))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_1) | (_cmp_cached_25) | (_cmp_cached_39))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_1) | (_cmp_cached_16) | (_cmp_cached_40))
            # 15m & 4h down move, 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_41) | (_cmp_cached_42))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_1) | (_cmp_cached_21) | (_cmp_cached_35))
            # 15m down move, 15m downtrend
            & ((_cmp_cached_1) | (_cmp_cached_43) | (_cmp_cached_44))
            # 15m down move, 15m still high, 15m downtrend
            & ((_cmp_cached_1) | (_cmp_cached_31) | (_cmp_cached_44))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_1) | (_cmp_cached_45) | (_cmp_cached_46))
            # 15m down move, 4h high, 15m downtrend
            & ((_cmp_cached_1) | (_cmp_cached_17) | (_cmp_cached_44))
            # 15m down move, 4h high, 1d overbought
            & ((_cmp_cached_1) | (_cmp_cached_47) | (_cmp_cached_48))
            # 15m down move, 1h high, 4h overbought
            & ((_cmp_cached_1) | (_cmp_cached_49) | (_cmp_cached_50))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_1) | (_cmp_cached_12) | (_cmp_cached_51))
            # 15m down move, drop in last half hour, 15m downtrend
            & ((_cmp_cached_1) | (df["close"] > (df["close_max_6"] * 0.75)) | (_cmp_cached_44))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_3) | (_cmp_cached_7) | (_cmp_cached_26))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_7) | (_cmp_cached_17))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_3) | (_cmp_cached_7) | (_cmp_cached_52))
            # 5m & 1h down move, 1h overbought
            & ((_cmp_cached_3) | (_cmp_cached_53) | (_cmp_cached_54))
            # 15m & 4h down move, 1d still high
            & ((_cmp_cached_3) | (_cmp_cached_55) | (_cmp_cached_56))
            # 15m & 4h down move, 1d downtrend
            & ((_cmp_cached_3) | (_cmp_cached_55) | (_cmp_cached_57))
            # 15m & 4h down move, 1h still high
            & ((_cmp_cached_3) | (_cmp_cached_58) | (_cmp_cached_59))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_3) | (_cmp_cached_25) | (_cmp_cached_60))
            # 15m & 4h down move, 15m still high
            & ((_cmp_cached_3) | (_cmp_cached_41) | (_cmp_cached_61))
            # 15m down move, 15m & 4h still high
            & ((_cmp_cached_3) | (_cmp_cached_62) | (_cmp_cached_40))
            # 15m down move, 15m still high, 1d overbought
            & ((_cmp_cached_3) | (_cmp_cached_62) | (_cmp_cached_63))
            # 15m down move, 15m high
            & ((_cmp_cached_3) | (_cmp_cached_18))
            # 15m down move, 4h high, 1d overbought
            & ((_cmp_cached_3) | (_cmp_cached_40) | (_cmp_cached_63))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_5) | (_cmp_cached_9) | (_cmp_cached_28))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_9) | (_cmp_cached_64))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_5) | (_cmp_cached_15) | (_cmp_cached_59))
            # 15m & 1h down move, 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_15) | (_cmp_cached_65))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_30) | (_cmp_cached_66))
            # 15m & 1h down move, 15m still high
            & ((_cmp_cached_5) | (_cmp_cached_30) | (_cmp_cached_62))
            # 15m & 1h down move, 4h overbought
            & ((_cmp_cached_5) | (_cmp_cached_11) | (_cmp_cached_67))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_5) | (_cmp_cached_58) | (_cmp_cached_68))
            # 15m & 4h down move, 15m still high
            & ((_cmp_cached_5) | (_cmp_cached_58) | (_cmp_cached_61))
            # 15m & 4h down move, 1h still high
            & ((_cmp_cached_5) | (_cmp_cached_58) | (_cmp_cached_28))
            # 15m & 4h down move, 4h downtrend
            & ((_cmp_cached_5) | (_cmp_cached_58) | (_cmp_cached_69))
            # 15m & 4h down move, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_16) | (_cmp_cached_70))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_5) | (_cmp_cached_41) | (_cmp_cached_45))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_71) | (_cmp_cached_72))
            # 15m & 1d down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_73) | (_cmp_cached_74))
            # 15m down move & downtrend, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_75) | (_cmp_cached_6))
            # 15m down move, 15m & 4h high
            & ((_cmp_cached_5) | (_cmp_cached_76) | (_cmp_cached_77))
            # 15m down move, 1h high & overbought
            & ((_cmp_cached_5) | (_cmp_cached_78) | (_cmp_cached_79))
            # 15m down move, 1h high, 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_78) | (_cmp_cached_65))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_80) | (_cmp_cached_63))
            # 15m down move, 1h high, 4h downtrend
            & ((_cmp_cached_5) | (_cmp_cached_37) | (_cmp_cached_81))
            # 15m down move, 1h high, 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_37) | (_cmp_cached_42))
            # 15m down move, 1h high & overbought
            & ((_cmp_cached_5) | (_cmp_cached_49) | (_cmp_cached_79))
            # 15m down move, 1h & 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_82) | (_cmp_cached_63))
            # 15m down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_83))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_84) | (_cmp_cached_30) | (_cmp_cached_33))
            # 15m down move, 15m still high, 4h overbought
            & ((_cmp_cached_84) | (_cmp_cached_85) | (_cmp_cached_86))
            # 15m down move, 15m & 1h high
            & ((_cmp_cached_84) | (_cmp_cached_76) | (_cmp_cached_80))
            # 15m down move, 15m & 1h high
            & ((_cmp_cached_84) | (_cmp_cached_18) | (_cmp_cached_78))
            # 15m & 4h down move, 15m still high
            & ((_cmp_cached_87) | (_cmp_cached_21) | (_cmp_cached_31))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_87) | (_cmp_cached_80) | (_cmp_cached_6))
            # 15m down move, 1h high & overbought
            & ((_cmp_cached_87) | (_cmp_cached_80) | (_cmp_cached_79))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_88) | (_cmp_cached_6) | (_cmp_cached_50))
            # 15m down move, 1d overbought
            & ((_cmp_cached_89) | (_cmp_cached_63))
            # 15m & 4h down move, 15m high
            & ((_cmp_cached_90) | (_cmp_cached_91) | (_cmp_cached_92))
            # 1h & 4h down move, 4h downtrend
            & ((_cmp_cached_13) | (_cmp_cached_58) | (_cmp_cached_93))
            # 1h & 4h down move, 1h still high
            & ((_cmp_cached_13) | (_cmp_cached_25) | (_cmp_cached_26))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_13) | (_cmp_cached_25) | (_cmp_cached_94))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_13) | (_cmp_cached_16) | (_cmp_cached_27))
            # 1h & 1d down move, 4h still high
            & ((_cmp_cached_13) | (_cmp_cached_29) | (_cmp_cached_35))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_7) | (_cmp_cached_55) | (_cmp_cached_95))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_7) | (_cmp_cached_58) | (_cmp_cached_96))
            # 1h & 4h down move, 1h downtrend
            & ((_cmp_cached_7) | (_cmp_cached_58) | (_cmp_cached_97))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_7) | (_cmp_cached_58) | (_cmp_cached_65))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_7) | (_cmp_cached_25) | (_cmp_cached_98))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_7) | (_cmp_cached_99) | (_cmp_cached_17))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_7) | (_cmp_cached_100) | (_cmp_cached_52))
            # 1h & 1d down move, 1d downtrend
            & ((_cmp_cached_7) | (_cmp_cached_101) | (_cmp_cached_102))
            # 1h down move, 1h still high, 4h high
            & ((_cmp_cached_7) | (_cmp_cached_26) | (_cmp_cached_46))
            # 1h down move, 1d high, 4h downtrend
            & ((_cmp_cached_7) | (_cmp_cached_94) | (_cmp_cached_103))
            # 1h & 4h down move, 15m still not low enough
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_10))
            # 1h & 4h down move, 1h still high
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_59))
            # 1h & 1d down move, 4h high
            & ((_cmp_cached_9) | (_cmp_cached_104) | (_cmp_cached_77))
            # 1h down move, 4h high
            & ((_cmp_cached_9) | (_cmp_cached_105))
            # 1h down move, 15m downtrend, 1d high
            & ((_cmp_cached_9) | (_cmp_cached_43) | (_cmp_cached_106))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_9) | (_cmp_cached_24) | (_cmp_cached_50))
            # 1h down move, 4h overbought
            & ((_cmp_cached_9) | (_cmp_cached_86))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_15) | (_cmp_cached_25) | (_cmp_cached_96))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_15) | (_cmp_cached_100) | (_cmp_cached_77))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_15) | (_cmp_cached_16) | (_cmp_cached_52))
            # 15m down move, 1h high, 1d downtrend
            & ((_cmp_cached_15) | (_cmp_cached_24) | (_cmp_cached_57))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_15) | (_cmp_cached_24) | (_cmp_cached_107))
            # 1h down move, 1h high
            & ((_cmp_cached_15) | (_cmp_cached_33))
            # 1h down mve, 4h high, 1d overbought
            & ((_cmp_cached_15) | (_cmp_cached_77) | (_cmp_cached_70))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_15) | (_cmp_cached_108) | (_cmp_cached_52))
            # 1h down move, 1h & 4h downtrend
            & ((_cmp_cached_15) | (_cmp_cached_109) | (_cmp_cached_103))
            # 1h & 4h down move, 4h overbought
            & ((_cmp_cached_30) | (_cmp_cached_99) | (_cmp_cached_67))
            # 1h down move, 1h still high, 4h downtrend
            & ((_cmp_cached_30) | (_cmp_cached_110) | (_cmp_cached_103))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_30) | (_cmp_cached_17) | (_cmp_cached_111))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_30) | (_cmp_cached_46) | (_cmp_cached_112))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_30) | (_cmp_cached_6) | (_cmp_cached_86))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_30) | (_cmp_cached_39) | (_cmp_cached_63))
            # 1h down move, 1h high, 15n downtrend
            & ((_cmp_cached_11) | (_cmp_cached_24) | (_cmp_cached_44))
            # 1h down move, 1h still high, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_59) | (_cmp_cached_52))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_67) | (_cmp_cached_48))
            # 1h & 4h down move, 4h downtrend
            & ((_cmp_cached_32) | (_cmp_cached_41) | (_cmp_cached_69))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_34) | (_cmp_cached_46) | (_cmp_cached_57))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_34) | (_cmp_cached_94) | (_cmp_cached_63))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_34) | (_cmp_cached_113) | (_cmp_cached_63))
            # 1h down move, 1h downtrend, 1h high
            & ((_cmp_cached_36) | (_cmp_cached_114) | (_cmp_cached_78))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_36) | (_cmp_cached_115) | (_cmp_cached_6))
            # 1h down move, 1h high, 15m downtrend
            & ((_cmp_cached_36) | (_cmp_cached_33) | (_cmp_cached_116))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_36) | (_cmp_cached_33) | (_cmp_cached_48))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_36) | (_cmp_cached_19) | (_cmp_cached_20))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_38) | (_cmp_cached_33) | (_cmp_cached_6))
            # 1h down move, 1h high & overbought
            & ((_cmp_cached_117) | (_cmp_cached_78) | (_cmp_cached_79))
            # 1h down move, 1h still high, 4h high
            & ((_cmp_cached_53) | (_cmp_cached_26) | (_cmp_cached_118))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_55) | (_cmp_cached_104) | (_cmp_cached_119))
            # 4h down move, 4h & 1d downtrend
            & ((_cmp_cached_55) | (_cmp_cached_103) | (_cmp_cached_65))
            # 4h & 1d down move, 4h still not low enough
            & ((_cmp_cached_58) | (_cmp_cached_29) | (_cmp_cached_120))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_58) | (_cmp_cached_121) | (_cmp_cached_14))
            # 4h down move, 4h still high
            & ((_cmp_cached_58) | (_cmp_cached_122))
            # 4h down move, 1d high
            & ((_cmp_cached_58) | (_cmp_cached_27))
            # 4h down move, 1h high, 1d downtrend
            & ((_cmp_cached_58) | (_cmp_cached_123) | (_cmp_cached_65))
            # 4h down move, 4h still not low enough, 1d downtrend
            & ((_cmp_cached_58) | (_cmp_cached_124) | (_cmp_cached_57))
            # 4h down move, 1h & 4h downtrend
            & ((_cmp_cached_58) | (_cmp_cached_109) | (_cmp_cached_103))
            # 4h down move, 4h & 1d downtrend
            & ((_cmp_cached_25) | (_cmp_cached_69) | (_cmp_cached_102))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_100) | (_cmp_cached_108) | (_cmp_cached_63))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_16) | (_cmp_cached_122) | (_cmp_cached_65))
            # 4h down move, 4h high, 1d overbought
            & ((_cmp_cached_41) | (_cmp_cached_77) | (_cmp_cached_107))
            # 4h down move, 1d overbought
            & ((_cmp_cached_91) | (_cmp_cached_63))
            # 4h down move, 4h high, 1d overbought
            & ((_cmp_cached_99) | (_cmp_cached_17) | (_cmp_cached_52))
            # 4h down move, 1h high, 1d overbought
            & ((_cmp_cached_71) | (_cmp_cached_49) | (_cmp_cached_112))
            # 1d down move, 1h high, 1d downtrend
            & ((_cmp_cached_101) | (_cmp_cached_49) | (_cmp_cached_57))
            # 1d down move, 1h still high, 4h high
            & ((_cmp_cached_104) | (_cmp_cached_26) | (_cmp_cached_46))
            # 1d down move, 1h & 4h high
            & ((_cmp_cached_121) | (_cmp_cached_33) | (_cmp_cached_46))
            # 1d down move, 1d high
            & ((_cmp_cached_125) | (_cmp_cached_108))
            # 1d down move, 4h still high, 1d overbought
            & ((_cmp_cached_73) | (_cmp_cached_122) | (_cmp_cached_111))
            # 1d down move, 1d high & overbought
            & ((_cmp_cached_126) | (_cmp_cached_108) | (_cmp_cached_107))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_127) | (_cmp_cached_46) | (_cmp_cached_48))
            # 15m & 1h & 4h downtrend
            & ((_cmp_cached_75) | (_cmp_cached_97) | (_cmp_cached_128))
            # 15m high, 1d overbought
            & ((_cmp_cached_76) | (_cmp_cached_63))
            # 1h still high, 1h & 4h downtrend
            & ((_cmp_cached_110) | (_cmp_cached_129) | (_cmp_cached_103))
            # 1h & 4h high, 1h overbought
            & ((_cmp_cached_45) | (_cmp_cached_46) | (_cmp_cached_79))
            # 1h high, 1h & 4h overbought
            & ((_cmp_cached_45) | (_cmp_cached_82) | (_cmp_cached_70))
            # 1h high, 1h overbought, 1d downtrend
            & ((_cmp_cached_45) | (_cmp_cached_79) | (_cmp_cached_65))
            # 4h & 1d high, 1d overbought
            & ((_cmp_cached_77) | (_cmp_cached_27) | (_cmp_cached_107))
            # 4h high, 1h downtrend
            & ((_cmp_cached_77) | (_cmp_cached_130))
            # 4h high, 1d downtrend
            & ((_cmp_cached_77) | (_cmp_cached_65))
            # 1d high, 4h downtrend, 1d overbought
            & ((_cmp_cached_131) | (_cmp_cached_81) | (_cmp_cached_107))
            # 1d high, 1h & 4h downtrend
            & ((_cmp_cached_94) | (_cmp_cached_132) | (_cmp_cached_69))
            # 1d high, 4h & 1d overbought
            & ((_cmp_cached_94) | (_cmp_cached_113) | (_cmp_cached_63))
            # 1h high, 4h overbought
            & ((_cmp_cached_19) | (_cmp_cached_67))
            # 4h high, 1h downtrend
            & ((_cmp_cached_64) | (_cmp_cached_130))
            # 4h high, 1d downtrend
            & ((_cmp_cached_64) | (_cmp_cached_65))
            # 5m down move, 15m still not low enough, 1h high
            & ((_cmp_cached_133) | (_cmp_cached_10) | (_cmp_cached_33))
            # 5m down move, 15m still high
            & ((_cmp_cached_133) | (_cmp_cached_62))
            # 5m down move, 15m & 1h down move, 15m still high
            & (
              (_cmp_cached_134) | (_cmp_cached_3) | (_cmp_cached_34) | (_cmp_cached_62)
            )
            # 5m down move, 4h down move, 15m downtrend, 1h high
            & (
              (_cmp_cached_134) | (_cmp_cached_91) | (_cmp_cached_75) | (_cmp_cached_115)
            )
            # 1h downtrend, 4h high & overbought
            & ((_cmp_cached_135) | (_cmp_cached_77) | (_cmp_cached_67))
            # 1h & 4h overbought, 1d downtrend
            & ((_cmp_cached_79) | (_cmp_cached_20) | (_cmp_cached_65))
            # 1d P&D, 1d downtrend
            & ((_cmp_cached_136) | (df["change_pct_1d"].shift(288) < 30.0) | (_cmp_cached_137))
            # 1d green with top wick, 1h down move
            & ((_cmp_cached_138) | (_cmp_cached_139) | (_cmp_cached_30))
            # 1d green with top wick, 4h high
            & ((_cmp_cached_140) | (_cmp_cached_141) | (_cmp_cached_77))
            # 1d green, 1h down move, 1d downtrend
            & ((_cmp_cached_142) | (_cmp_cached_11) | (_cmp_cached_143))
            # 1d green with top wick, 4h overbought
            & ((_cmp_cached_144) | (_cmp_cached_145) | (_cmp_cached_67))
            # big drop in the last hour, 15m downtrend
            & ((df["close"] > (df["close_max_12"] * 0.65)) | (_cmp_cached_146))
            # big drop in the last 6 hours, 1h down move, 1h high
            & ((df["close"] > (df["high_max_6_1h"] * 0.60)) | (_cmp_cached_30) | (_cmp_cached_115))
            # big drop in the last 24 hours,  1h still high
            & ((df["close"] > (df["high_max_24_1h"] * 0.40)) | (_cmp_cached_147))
            # big drop in the last 4 days, 1h high
            & ((df["close"] > (df["high_max_24_4h"] * 0.20)) | (_cmp_cached_24))
            # big drop in the last 20 days, 1d high, 1d downtrend
            & (
              (df["close"] > (df["high_max_20_1d"] * 0.20))
              | (_cmp_cached_148)
              | (_cmp_cached_149)
            )
          )

          # Logic
          long_entry_logic.append(
            (df["EMA_26"] > df["EMA_12"])
            & ((df["EMA_26"] - df["EMA_12"]) > (df["open"] * 0.034))
            & ((df["EMA_26"].shift() - df["EMA_12"].shift()) > (df["open"] / 100.0))
            & (df["close"] < (df["BBL_20_2.0"] * 0.999))
          )

        # Condition #2 - Normal mode (Long).
        if long_entry_condition_index == 2:
          # Protections
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          long_entry_logic.append(df["protections_long_global"] == True)

          long_entry_logic.append(
            # 5m & 1h down move, 1h still not low enough
            ((_cmp_cached_0) | (_cmp_cached_9) | (_cmp_cached_150))
            # 5m & 1h down move, 1d high
            & ((_cmp_cached_0) | (_cmp_cached_30) | (_cmp_cached_27))
            # 5m & 1h down move, 1h still high
            & ((_cmp_cached_0) | (_cmp_cached_32) | (_cmp_cached_59))
            # 5m & 1h down move, 1d high
            & ((_cmp_cached_0) | (_cmp_cached_34) | (_cmp_cached_27))
            # 5m & 4h down move, 15m still not low enough
            & ((_cmp_cached_0) | (_cmp_cached_151) | (_cmp_cached_152))
            # 5m & 4h down move, 1d downtrend
            & ((_cmp_cached_0) | (_cmp_cached_25) | (_cmp_cached_102))
            # 5m & 4h down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_91) | (_cmp_cached_12))
            # 5m & 4h down move, 15m still high
            & ((_cmp_cached_8) | (_cmp_cached_16) | (_cmp_cached_61))
            # 5m & 1d down move, 1h still high
            & ((_cmp_cached_0) | (_cmp_cached_153) | (_cmp_cached_110))
            # 5m & 1d down move, 1h still high
            & ((_cmp_cached_0) | (_cmp_cached_153) | (_cmp_cached_59))
            # 5m & 1d down move, 1d downtrend
            & ((_cmp_cached_0) | (_cmp_cached_29) | (_cmp_cached_154))
            # 5m & 1d down move, 15m still high
            & ((_cmp_cached_0) | (_cmp_cached_104) | (_cmp_cached_155))
            # 5m down move, 1h high
            & ((_cmp_cached_0) | (_cmp_cached_33))
            # 5m down move, 4h high, 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_77) | (_cmp_cached_70))
            # 5m down move, 4h high & overbought
            & ((_cmp_cached_0) | (_cmp_cached_6) | (_cmp_cached_20))
            # 5m down move, 4h & 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_20) | (_cmp_cached_52))
            # 5m down move, 1d downtrend
            & ((_cmp_cached_0) | (_cmp_cached_65))
            # 5m & 15m down move, 15m still high
            & ((_cmp_cached_8) | (_cmp_cached_5) | (_cmp_cached_155))
            # 5m & 15m down move, 1h high
            & ((_cmp_cached_8) | (_cmp_cached_89) | (_cmp_cached_19))
            # 5m & 4h down move, 1d downtrend
            & ((_cmp_cached_8) | (_cmp_cached_58) | (_cmp_cached_57))
            # 5m & 4h down move, 4h still not low enough
            & ((_cmp_cached_8) | (_cmp_cached_25) | (_cmp_cached_156))
            # 5m down move, 4h high, 1h overbought
            & ((_cmp_cached_157) | (_cmp_cached_6) | (_cmp_cached_158))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_22) | (_cmp_cached_11) | (_cmp_cached_28))
            # 15m & 1h & 4h down move
            & ((_cmp_cached_1) | (_cmp_cached_13) | (_cmp_cached_25))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_1) | (_cmp_cached_13) | (_cmp_cached_122))
            # 15m & 1h down move, 15m downtrend
            & ((_cmp_cached_1) | (_cmp_cached_7) | (_cmp_cached_159))
            # 15m & 1h down move, 15m still not low enough
            & ((_cmp_cached_1) | (_cmp_cached_7) | (_cmp_cached_10))
            # 15m & 1h down move, 1h still not low enough
            & ((_cmp_cached_1) | (_cmp_cached_7) | (_cmp_cached_160))
            # 15m & 1h down move, 1h still not low enough
            & ((_cmp_cached_1) | (_cmp_cached_7) | (_cmp_cached_161))
            # 15m & 1h & 4h down move
            & ((_cmp_cached_1) | (_cmp_cached_9) | (_cmp_cached_58))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_1) | (_cmp_cached_9) | (_cmp_cached_161))
            # 15m & 1h down move, 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_9) | (_cmp_cached_65))
            # 15m & 1h down move, 15m downtrend
            & ((_cmp_cached_1) | (_cmp_cached_15) | (_cmp_cached_43))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_1) | (_cmp_cached_15) | (_cmp_cached_35))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_1) | (_cmp_cached_30) | (_cmp_cached_24))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_1) | (_cmp_cached_30) | (_cmp_cached_59))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_1) | (_cmp_cached_30) | (_cmp_cached_162))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_1) | (_cmp_cached_32) | (_cmp_cached_115))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_1) | (_cmp_cached_32) | (_cmp_cached_37))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_1) | (_cmp_cached_34) | (_cmp_cached_110))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_1) | (_cmp_cached_34) | (_cmp_cached_148))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_1) | (_cmp_cached_36) | (_cmp_cached_24))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_1) | (_cmp_cached_36) | (_cmp_cached_12))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_1) | (_cmp_cached_38) | (_cmp_cached_45))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_1) | (_cmp_cached_53) | (_cmp_cached_19))
            # 15m & 4h down move, 4h still not low enough
            & ((_cmp_cached_1) | (_cmp_cached_55) | (_cmp_cached_163))
            # 15m & 4h down move, 4h downtrend
            & ((_cmp_cached_1) | (_cmp_cached_55) | (_cmp_cached_164))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_1) | (_cmp_cached_58) | (_cmp_cached_108))
            # 15m & 4h down move, 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_58) | (_cmp_cached_57))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_1) | (_cmp_cached_41) | (_cmp_cached_165))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_1) | (_cmp_cached_21) | (_cmp_cached_35))
            # 15m down move, 15m still not low enough, 1h high
            & ((_cmp_cached_1) | (_cmp_cached_166) | (_cmp_cached_123))
            # 15m down move, 15m still not low enough, 1h still high
            & ((_cmp_cached_1) | (_cmp_cached_10) | (_cmp_cached_59))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_1) | (_cmp_cached_24) | (_cmp_cached_167))
            # 15m down move, 4h still high, 15m downtrend
            & ((_cmp_cached_1) | (_cmp_cached_96) | (_cmp_cached_168))
            # 15m down move, 4h high, 1d overbought
            & ((_cmp_cached_1) | (_cmp_cached_17) | (_cmp_cached_70))
            # 15m down move, 4h & 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_103) | (_cmp_cached_42))
            # 15m & 1h & 4h down move
            & ((_cmp_cached_3) | (_cmp_cached_7) | (_cmp_cached_58))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_3) | (_cmp_cached_9) | (_cmp_cached_169))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_3) | (_cmp_cached_9) | (_cmp_cached_110))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_9) | (_cmp_cached_6))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_15) | (_cmp_cached_162))
            # 1d down move, 1d still high, 4h still high
            & ((_cmp_cached_73) | (_cmp_cached_170) | (_cmp_cached_35))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_36) | (_cmp_cached_12))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_38) | (_cmp_cached_33))
            # 15m & 4h down move, 1d still high
            & ((_cmp_cached_3) | (_cmp_cached_55) | (_cmp_cached_56))
            # 15m & 4h down move, 15m still not low enough
            & ((_cmp_cached_3) | (_cmp_cached_58) | (_cmp_cached_152))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_3) | (_cmp_cached_58) | (_cmp_cached_148))
            # 15m & 4h down move, 15m still high
            & ((_cmp_cached_3) | (_cmp_cached_25) | (_cmp_cached_31))
            # 15m & 4h down move, 1h still high
            & ((_cmp_cached_3) | (_cmp_cached_25) | (_cmp_cached_59))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_3) | (_cmp_cached_25) | (_cmp_cached_35))
            # 15m & 4h down move, 1d overbought
            & ((_cmp_cached_3) | (_cmp_cached_100) | (_cmp_cached_95))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_3) | (_cmp_cached_91) | (_cmp_cached_96))
            # 15m & 1d down move, 15m still not low enough
            & ((_cmp_cached_3) | (_cmp_cached_153) | (_cmp_cached_10))
            # 15m & 1d down move, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_125) | (_cmp_cached_49))
            # 15m down move, 15m downtrend, 4h still not low enough
            & ((_cmp_cached_3) | (_cmp_cached_159) | (_cmp_cached_124))
            # 15m down move, 15m still not low enough, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_166) | (_cmp_cached_64))
            # 15m down move, 15m stil high, 1h still high
            & ((_cmp_cached_3) | (_cmp_cached_31) | (_cmp_cached_59))
            # 15m down move, 1d high & overbought
            & ((_cmp_cached_3) | (_cmp_cached_108) | (_cmp_cached_167))
            # 15m down move, 15m still not low enough, 1h still high
            & (
              (_cmp_cached_3) | (_cmp_cached_171) | (_cmp_cached_59)
            )
            # 15m down move, 1h still high, 4h overbought
            & ((_cmp_cached_3) | (_cmp_cached_59) | (_cmp_cached_51))
            # 15m down move, 1h high & overbought
            & ((_cmp_cached_3) | (_cmp_cached_19) | (_cmp_cached_79))
            # 15m & 1h down move, 15m high
            & ((_cmp_cached_5) | (_cmp_cached_9) | (_cmp_cached_61))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_5) | (_cmp_cached_9) | (_cmp_cached_26))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_9) | (_cmp_cached_40))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_9) | (_cmp_cached_148))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_5) | (_cmp_cached_15) | (_cmp_cached_33))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_30) | (_cmp_cached_64))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_11) | (_cmp_cached_172))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_5) | (_cmp_cached_11) | (_cmp_cached_122))
            # 15m & 1h down move, 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_11) | (_cmp_cached_42))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_32) | (_cmp_cached_70))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_5) | (_cmp_cached_34) | (_cmp_cached_173))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_5) | (_cmp_cached_34) | (_cmp_cached_123))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_36) | (_cmp_cached_12))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_5) | (_cmp_cached_117) | (_cmp_cached_37))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_117) | (_cmp_cached_12))
            # 16m & 1h down move, 1h high
            & ((_cmp_cached_5) | (_cmp_cached_174) | (_cmp_cached_37))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_174) | (_cmp_cached_72))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_5) | (_cmp_cached_36) | (_cmp_cached_24))
            # 15m & 4h down move, 4h still not low enough
            & ((_cmp_cached_5) | (_cmp_cached_58) | (_cmp_cached_124))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_58) | (_cmp_cached_74))
            # 15m & 4h down move, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_58) | (_cmp_cached_167))
            # 15m & 4h down move, 4h still not low enough
            & ((_cmp_cached_5) | (_cmp_cached_100) | (_cmp_cached_124))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_41) | (_cmp_cached_94))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_41) | (_cmp_cached_39))
            # 15m & 4h down move, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_41) | (_cmp_cached_70))
            # 15m & 4h down move, 4h overbought
            & ((_cmp_cached_5) | (_cmp_cached_175) | (_cmp_cached_86))
            # 15m & 1d down move, 1d still high
            & ((_cmp_cached_5) | (_cmp_cached_153) | (_cmp_cached_176))
            # 15m & 1d down move, 1h high
            & ((_cmp_cached_5) | (_cmp_cached_153) | (_cmp_cached_49))
            # 15m & 1d down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_29) | (_cmp_cached_72))
            # 15m down move, 15m downtrend, 1h high
            & ((_cmp_cached_5) | (_cmp_cached_43) | (_cmp_cached_33))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_33) | (_cmp_cached_167))
            # 15m down move, 4h & 1d high
            & ((_cmp_cached_5) | (_cmp_cached_17) | (_cmp_cached_27))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_5) | (_cmp_cached_17) | (_cmp_cached_50))
            # 15m down move, 15m still not low enough, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_171) | (_cmp_cached_17))
            # 15m down move, 15m sill high, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_155) | (_cmp_cached_40))
            # 15m down move, 4h high, 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_12) | (_cmp_cached_102))
            # 15m & 1h down move, 4h downtrend
            & ((_cmp_cached_84) | (_cmp_cached_15) | (_cmp_cached_69))
            # 15m & 1h down move, 1h downtrend
            & ((_cmp_cached_84) | (_cmp_cached_30) | (_cmp_cached_177))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_84) | (_cmp_cached_11) | (_cmp_cached_48))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_84) | (_cmp_cached_32) | (_cmp_cached_77))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_84) | (_cmp_cached_36) | (_cmp_cached_24))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_84) | (_cmp_cached_36) | (_cmp_cached_94))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_84) | (_cmp_cached_38) | (_cmp_cached_64))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_84) | (_cmp_cached_25) | (_cmp_cached_24))
            # 15m & 4h down move, 4h downtrend
            & ((_cmp_cached_84) | (_cmp_cached_25) | (_cmp_cached_69))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_84) | (_cmp_cached_100) | (_cmp_cached_94))
            # 15m & 1d down move, 1h still high
            & ((_cmp_cached_84) | (_cmp_cached_29) | (_cmp_cached_110))
            # 15m & 1d down move, 4h high
            & ((_cmp_cached_84) | (_cmp_cached_178) | (_cmp_cached_46))
            # 15m down move, 15m still not low enough, 4h high
            & ((_cmp_cached_84) | (_cmp_cached_179) | (_cmp_cached_40))
            # 15m down move, 15m still not low enough, 1h high
            & ((_cmp_cached_84) | (_cmp_cached_10) | (_cmp_cached_24))
            # 15m down move, 15m & 4h still high
            & ((_cmp_cached_84) | (_cmp_cached_31) | (_cmp_cached_96))
            # 15m down move, 1h still high, 4h overbought
            & ((_cmp_cached_84) | (_cmp_cached_26) | (_cmp_cached_83))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_84) | (_cmp_cached_115) | (_cmp_cached_46))
            # 15m down move, 1h & 1d high
            & ((_cmp_cached_84) | (_cmp_cached_24) | (_cmp_cached_94))
            # 15m down move, 4h high, 4h downtrend
            & ((_cmp_cached_84) | (_cmp_cached_40) | (_cmp_cached_69))
            # 15m down move, 4h & 1d high
            & ((_cmp_cached_84) | (_cmp_cached_172) | (_cmp_cached_27))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_84) | (_cmp_cached_77) | (_cmp_cached_50))
            # 15m down move, 15m still high, 1d overbought
            & ((_cmp_cached_84) | (_cmp_cached_61) | (_cmp_cached_48))
            # 15m down move, 1h high & overbought
            & ((_cmp_cached_84) | (_cmp_cached_49) | (_cmp_cached_82))
            # 15m down move, 4h high, 1d overbought
            & ((_cmp_cached_84) | (_cmp_cached_64) | (_cmp_cached_95))
            # 15m & 1h down move, 15m still not low enough
            & ((_cmp_cached_87) | (_cmp_cached_30) | (_cmp_cached_10))
            # 15m & 1h down move, 4h overbought
            & ((_cmp_cached_87) | (_cmp_cached_30) | (_cmp_cached_86))
            # 15m & 1h down move, 15m high
            & ((_cmp_cached_87) | (_cmp_cached_11) | (_cmp_cached_180))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_87) | (_cmp_cached_11) | (_cmp_cached_12))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_87) | (_cmp_cached_32) | (_cmp_cached_24))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_87) | (_cmp_cached_38) | (_cmp_cached_19))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_87) | (_cmp_cached_100) | (_cmp_cached_19))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_87) | (_cmp_cached_181) | (_cmp_cached_77))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_87) | (_cmp_cached_33) | (_cmp_cached_77))
            # 15m down move, 1h & 1d high
            & ((_cmp_cached_87) | (_cmp_cached_33) | (_cmp_cached_108))
            # 15m down move, 1h high, 1d downtrend
            & ((_cmp_cached_87) | (_cmp_cached_78) | (_cmp_cached_102))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_87) | (_cmp_cached_37) | (_cmp_cached_48))
            # 15m down move, 1h high, 1d downtrend
            & ((_cmp_cached_87) | (_cmp_cached_19) | (_cmp_cached_57))
            # 15m down move, 1h high & overbought
            & ((_cmp_cached_87) | (_cmp_cached_49) | (_cmp_cached_82))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_88) | (_cmp_cached_36) | (_cmp_cached_63))
            # 15m & 4h down move, 1h overbought
            & ((_cmp_cached_88) | (_cmp_cached_21) | (_cmp_cached_182))
            # 15m down move, 15m still not low enough, 1h high
            & ((_cmp_cached_88) | (_cmp_cached_166) | (_cmp_cached_49))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_88) | (_cmp_cached_24) | (_cmp_cached_6))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_88) | (_cmp_cached_24) | (_cmp_cached_107))
            # 15m down move, 4h high, 1d overbought
            & ((_cmp_cached_88) | (_cmp_cached_17) | (_cmp_cached_107))
            # 15m down move, 4h high, 1h overbought
            & ((_cmp_cached_88) | (_cmp_cached_77) | (_cmp_cached_183))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_89) | (_cmp_cached_17) | (_cmp_cached_86))
            # 15m down move, 1h high, 1d downtrend
            & ((_cmp_cached_89) | (_cmp_cached_19) | (_cmp_cached_57))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_89) | (_cmp_cached_12) | (_cmp_cached_51))
            # 15m down move, 1h high, 4h overbought
            & ((_cmp_cached_184) | (_cmp_cached_33) | (_cmp_cached_67))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_184) | (_cmp_cached_46) | (_cmp_cached_86))
            # 15m down move, 4h high, 1d overbought
            & ((_cmp_cached_184) | (_cmp_cached_6) | (_cmp_cached_79))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_184) | (_cmp_cached_19) | (_cmp_cached_63))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_90) | (_cmp_cached_6) | (_cmp_cached_113))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_185) | (_cmp_cached_25) | (_cmp_cached_186))
            # 1h down move, 15m downtrend, 1h still high
            & ((_cmp_cached_13) | (_cmp_cached_43) | (_cmp_cached_110))
            # 1h & 4h down move, 15m downtrend
            & ((_cmp_cached_13) | (_cmp_cached_151) | (_cmp_cached_187))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_13) | (_cmp_cached_55) | (_cmp_cached_96))
            # 1h & 4h down move, 1d still high
            & ((_cmp_cached_13) | (_cmp_cached_58) | (_cmp_cached_56))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_13) | (_cmp_cached_25) | (_cmp_cached_169))
            # 1h & 4h down move, 1h still not low enough
            & ((_cmp_cached_13) | (_cmp_cached_100) | (_cmp_cached_188))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_13) | (_cmp_cached_100) | (_cmp_cached_108))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_13) | (_cmp_cached_16) | (_cmp_cached_95))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_13) | (_cmp_cached_99) | (_cmp_cached_17))
            # 1h & 1d down move, 15m still high
            & ((_cmp_cached_13) | (_cmp_cached_153) | (_cmp_cached_61))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_7) | (_cmp_cached_55) | (_cmp_cached_165))
            # 1h & 4h down move, 1d still high
            & ((_cmp_cached_7) | (_cmp_cached_55) | (_cmp_cached_14))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_7) | (_cmp_cached_55) | (_cmp_cached_102))
            # 1h % 4h down move, 4h downtrend
            & ((_cmp_cached_7) | (_cmp_cached_58) | (_cmp_cached_189))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_7) | (_cmp_cached_71) | (_cmp_cached_35))
            # 1h & 4h down move, 15m high
            & ((_cmp_cached_7) | (_cmp_cached_58) | (_cmp_cached_92))
            # 1h & 4h down move, 1h still high
            & ((_cmp_cached_7) | (_cmp_cached_25) | (_cmp_cached_26))
            # 1h & 4h down move, 4h downtrend
            & ((_cmp_cached_7) | (_cmp_cached_25) | (_cmp_cached_103))
            # 1h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_7) | (_cmp_cached_35) | (_cmp_cached_42))
            # 1h & 4h & 1d down move
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_29))
            # 1h & 4h down move, 1d still high
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_119))
            # 1h & 4h down move, 1h still not low enough
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_190))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_57))
            # 1h & 4h down move, 15m high
            & ((_cmp_cached_9) | (_cmp_cached_25) | (_cmp_cached_92))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_9) | (_cmp_cached_25) | (_cmp_cached_65))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_9) | (_cmp_cached_41) | (_cmp_cached_35))
            # 1h & 1d down move, 15m still high
            & ((_cmp_cached_9) | (_cmp_cached_29) | (_cmp_cached_155))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_9) | (_cmp_cached_21) | (_cmp_cached_169))
            # 1h down move, 1h still not low enough 1d overbought
            & ((_cmp_cached_9) | (_cmp_cached_150) | (_cmp_cached_48))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_15) | (_cmp_cached_25) | (_cmp_cached_191))
            # 1h & 4h down move, 1h still not low enough
            & ((_cmp_cached_15) | (_cmp_cached_25) | (_cmp_cached_188))
            # 1h & 4h down move, 15m still high
            & ((_cmp_cached_15) | (_cmp_cached_25) | (_cmp_cached_61))
            # 1h & 4h down move, 4h downtrend
            & ((_cmp_cached_15) | (_cmp_cached_25) | (_cmp_cached_69))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_15) | (_cmp_cached_100) | (_cmp_cached_169))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_15) | (_cmp_cached_16) | (_cmp_cached_124))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_15) | (_cmp_cached_41) | (_cmp_cached_74))
            # 1h & 4h down move, 4h downtrend
            & ((_cmp_cached_15) | (_cmp_cached_41) | (_cmp_cached_103))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_15) | (_cmp_cached_181) | (_cmp_cached_17))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_15) | (_cmp_cached_181) | (_cmp_cached_35))
            # 1h & 1d down move, 1d high
            & ((_cmp_cached_15) | (_cmp_cached_121) | (_cmp_cached_108))
            # 1h & 1d down move, 1d overbought
            & ((_cmp_cached_15) | (_cmp_cached_192) | (_cmp_cached_95))
            # 1h down move, 1h still high, 1d downtrend
            & ((_cmp_cached_15) | (_cmp_cached_110) | (_cmp_cached_65))
            # 1h down move, 4h high, 1d high
            & ((_cmp_cached_15) | (_cmp_cached_40) | (_cmp_cached_27))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_15) | (_cmp_cached_40) | (_cmp_cached_107))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_15) | (_cmp_cached_162) | (_cmp_cached_50))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_15) | (_cmp_cached_39) | (_cmp_cached_52))
            # 1h down move, 4h & 1d downtrend
            & ((_cmp_cached_15) | (_cmp_cached_69) | (_cmp_cached_57))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_30) | (_cmp_cached_100) | (_cmp_cached_167))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_30) | (_cmp_cached_21) | (_cmp_cached_35))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_30) | (_cmp_cached_99) | (_cmp_cached_47))
            # 1h & 1d down move, 1h still high
            & ((_cmp_cached_30) | (_cmp_cached_178) | (_cmp_cached_59))
            # 1h down move, 1h high, 4h downtrend
            & ((_cmp_cached_30) | (_cmp_cached_24) | (_cmp_cached_93))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_30) | (_cmp_cached_24) | (_cmp_cached_50))
            # 1h down move, 1h high, 1h still not low enough
            & ((_cmp_cached_30) | (_cmp_cached_108) | (_cmp_cached_190))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_30) | (_cmp_cached_27) | (_cmp_cached_167))
            # 1h down move, 1d high, 4h downtrend
            & ((_cmp_cached_30) | (_cmp_cached_74) | (_cmp_cached_69))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_11) | (_cmp_cached_41) | (_cmp_cached_40))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_11) | (_cmp_cached_41) | (_cmp_cached_102))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_11) | (_cmp_cached_115) | (_cmp_cached_46))
            # 1h down move, 1h high
            & ((_cmp_cached_11) | (_cmp_cached_45))
            # 1h down move, 4h high, 4h downtrend
            & ((_cmp_cached_11) | (_cmp_cached_17) | (_cmp_cached_193))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_11) | (_cmp_cached_108) | (_cmp_cached_52))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_51) | (_cmp_cached_48))
            # 1h & 4h down move, 4h downtrend
            & ((_cmp_cached_32) | (_cmp_cached_41) | (_cmp_cached_69))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_32) | (_cmp_cached_115) | (_cmp_cached_6))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_32) | (_cmp_cached_24) | (_cmp_cached_50))
            # 1h down move, 4h & 1d high
            & ((_cmp_cached_32) | (_cmp_cached_77) | (_cmp_cached_27))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_32) | (_cmp_cached_77) | (_cmp_cached_70))
            # 1h down move, 4h downtrend, 1d overbought
            & ((_cmp_cached_32) | (_cmp_cached_103) | (_cmp_cached_111))
            # 1h down move, 4h & 1d downtrend
            & ((_cmp_cached_32) | (_cmp_cached_81) | (_cmp_cached_194))
            # 1h & 4h down move, 1h still high
            & ((_cmp_cached_34) | (_cmp_cached_21) | (_cmp_cached_28))
            # 1h down move, 1h still high, 4h downtrend
            & ((_cmp_cached_34) | (_cmp_cached_26) | (_cmp_cached_69))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_34) | (_cmp_cached_24) | (_cmp_cached_195))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_34) | (_cmp_cached_47) | (_cmp_cached_196))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_34) | (_cmp_cached_47) | (_cmp_cached_48))
            # 1h down move, 1d high, 4h overbought
            & ((_cmp_cached_34) | (_cmp_cached_27) | (_cmp_cached_113))
            # 1h down move, 1h still high, 1d overbought
            & ((_cmp_cached_34) | (_cmp_cached_59) | (_cmp_cached_111))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_36) | (_cmp_cached_24) | (_cmp_cached_6))
            # 1h down move, 1h & 1d high
            & ((_cmp_cached_36) | (_cmp_cached_33) | (_cmp_cached_108))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_36) | (_cmp_cached_33) | (_cmp_cached_95))
            # 1h down move, 4h still high, 1d overbought
            & ((_cmp_cached_36) | (_cmp_cached_96) | (_cmp_cached_48))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_38) | (_cmp_cached_71) | (_cmp_cached_6))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_38) | (_cmp_cached_197) | (_cmp_cached_111))
            # 1h down move, 1h high & overbought
            & ((_cmp_cached_117) | (_cmp_cached_33) | (_cmp_cached_82))
            # 1h down move, 4h high, 1h overbought
            & ((_cmp_cached_117) | (_cmp_cached_47) | (_cmp_cached_79))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_117) | (_cmp_cached_162) | (_cmp_cached_194))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_117) | (_cmp_cached_12) | (_cmp_cached_196))
            # 1h down move, 1h & 4h overbought
            & ((_cmp_cached_117) | (_cmp_cached_82) | (_cmp_cached_196))
            # 1h down move, 1h high & overbought
            & ((_cmp_cached_174) | (_cmp_cached_78) | (_cmp_cached_82))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_174) | (_cmp_cached_6) | (_cmp_cached_50))
            # 1h down move, 1h high & overbought
            & ((_cmp_cached_174) | (_cmp_cached_19) | (_cmp_cached_82))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_151) | (_cmp_cached_29) | (_cmp_cached_119))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_151) | (_cmp_cached_104) | (_cmp_cached_56))
            # 4h & 1d down move, 1d downtrend
            & ((_cmp_cached_55) | (_cmp_cached_29) | (_cmp_cached_57))
            # 4h down move, 15m still high
            & ((_cmp_cached_55) | (_cmp_cached_61))
            # 4h & 1d down move, 1h still not low enough
            & ((_cmp_cached_58) | (_cmp_cached_153) | (_cmp_cached_190))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_58) | (_cmp_cached_29) | (_cmp_cached_56))
            # 4h & 1d down move, 1d downtrend
            & ((_cmp_cached_58) | (_cmp_cached_104) | (_cmp_cached_195))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_58) | (_cmp_cached_192) | (_cmp_cached_27))
            # 4h & 1d down move, 1d overbought
            & ((_cmp_cached_58) | (_cmp_cached_198) | (_cmp_cached_95))
            # 4h down move, 1d still high, 1d downtrend
            & ((_cmp_cached_58) | (_cmp_cached_119) | (_cmp_cached_57))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_58) | (_cmp_cached_94) | (_cmp_cached_52))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_58) | (_cmp_cached_165) | (_cmp_cached_57))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_25) | (_cmp_cached_104) | (_cmp_cached_199))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_25) | (_cmp_cached_122) | (_cmp_cached_57))
            # 4h & 1d down move, 4h still high
            & ((_cmp_cached_100) | (_cmp_cached_104) | (_cmp_cached_165))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_100) | (_cmp_cached_104) | (_cmp_cached_74))
            # 4h down move, 1h high, 1d downtrend
            & ((_cmp_cached_25) | (_cmp_cached_78) | (_cmp_cached_186))
            # 4h down move, 4h still high, 4h downtrend
            & ((_cmp_cached_25) | (_cmp_cached_122) | (_cmp_cached_69))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_100) | (_cmp_cached_106) | (_cmp_cached_107))
            # 4h & 1d down move, 1d overbought
            & ((_cmp_cached_16) | (_cmp_cached_125) | (_cmp_cached_70))
            # 4h down move, 4h still high, 1d overbought
            & ((_cmp_cached_16) | (_cmp_cached_96) | (_cmp_cached_48))
            # 4h down move, 4h still high. 4h downtrend
            & ((_cmp_cached_16) | (_cmp_cached_122) | (_cmp_cached_200))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_16) | (_cmp_cached_122) | (_cmp_cached_65))
            # 4h down move, 4h high, 4h downtrend
            & ((_cmp_cached_16) | (_cmp_cached_17) | (_cmp_cached_103))
            # 4h & 1d down move, 1d overbought
            & ((_cmp_cached_41) | (_cmp_cached_126) | (_cmp_cached_112))
            # 4h down move, 1d downtrend
            & ((_cmp_cached_41) | (_cmp_cached_42))
            # 4h down move, 4h & 1d overbought
            & ((_cmp_cached_21) | (_cmp_cached_51) | (_cmp_cached_111))
            # 4h down move, 1h high, 1d overbought
            & ((_cmp_cached_181) | (_cmp_cached_24) | (_cmp_cached_52))
            # 4h down move, 4h & 1d downtrend
            & ((_cmp_cached_181) | (_cmp_cached_77) | (_cmp_cached_27))
            # 4h down move, 4h still high, 1d overbought
            & ((_cmp_cached_181) | (_cmp_cached_165) | (_cmp_cached_107))
            # 4h down move, 4h high, 1d downtrend
            & ((_cmp_cached_181) | (_cmp_cached_64) | (_cmp_cached_194))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_181) | (_cmp_cached_39) | (_cmp_cached_48))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_91) | (_cmp_cached_198) | (_cmp_cached_27))
            # 4h down move, 4h high, 1d downtrend
            & ((_cmp_cached_91) | (_cmp_cached_17) | (_cmp_cached_102))
            # 4h down move, 4h high & overbought
            & ((_cmp_cached_99) | (_cmp_cached_17) | (_cmp_cached_50))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_99) | (_cmp_cached_131) | (_cmp_cached_63))
            # 4h down move, 1d high, 4h overbought
            & ((_cmp_cached_175) | (_cmp_cached_39) | (_cmp_cached_50))
            # 4h down move, 4h high & overbought
            & ((_cmp_cached_71) | (_cmp_cached_17) | (_cmp_cached_20))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_71) | (_cmp_cached_27) | (_cmp_cached_111))
            # 4h down move, 4h & 1d overbought
            & ((_cmp_cached_71) | (_cmp_cached_20) | (_cmp_cached_167))
            # 4h down move, 4h overbought
            & ((_cmp_cached_71) | (_cmp_cached_83))
            # 1d down move, 1d high, 1d downtrend
            & ((_cmp_cached_101) | (_cmp_cached_108) | (_cmp_cached_57))
            # 1d down move, 1h & 4h high
            & ((_cmp_cached_153) | (_cmp_cached_26) | (_cmp_cached_46))
            # 1d down move, 1h high
            & ((_cmp_cached_153) | (_cmp_cached_24))
            # 1d down move, 1h high, 1d downtrend
            & ((_cmp_cached_153) | (_cmp_cached_19) | (_cmp_cached_57))
            # 1d down move, 1h overbought, 1d downtrend
            & ((_cmp_cached_29) | (_cmp_cached_79) | (_cmp_cached_42))
            # 1d down move, 1h high, 1d downtrend
            & ((_cmp_cached_104) | (_cmp_cached_49) | (_cmp_cached_186))
            # 1d down move, 1h high, 1d overbought
            & ((_cmp_cached_121) | (_cmp_cached_24) | (_cmp_cached_201))
            # 1d down move, 1d still high, 1d downtrend
            & ((_cmp_cached_121) | (_cmp_cached_14) | (_cmp_cached_57))
            # 1d down move, 1h high & overbought
            & ((_cmp_cached_125) | (_cmp_cached_106) | (_cmp_cached_63))
            # 1d down move, 4h high & overbought
            & ((_cmp_cached_198) | (_cmp_cached_72) | (_cmp_cached_83))
            # 1d downtrend, 1d high & overbought
            & ((_cmp_cached_202) | (_cmp_cached_131) | (_cmp_cached_167))
            # 1h high, 4h & 1d overbought
            & ((_cmp_cached_24) | (_cmp_cached_86) | (_cmp_cached_111))
            # 1h & 4h high, 1d overbought
            & ((_cmp_cached_24) | (_cmp_cached_46) | (_cmp_cached_107))
            # 1h & 4h high, 1d downtrend
            & ((_cmp_cached_24) | (_cmp_cached_6) | (_cmp_cached_65))
            # 1h high, 4h & 1d downtrend
            & ((_cmp_cached_24) | (_cmp_cached_103) | (_cmp_cached_42))
            # 1h & 4h high, 1h overbought
            & ((_cmp_cached_33) | (_cmp_cached_46) | (_cmp_cached_158))
            # 1h & 4high, 1d downtrend
            & ((_cmp_cached_33) | (_cmp_cached_6) | (_cmp_cached_57))
            # 1h & 4h high, 1d overbought
            & ((_cmp_cached_33) | (_cmp_cached_6) | (_cmp_cached_63))
            # 1h & 1d high, 1d overbought
            & ((_cmp_cached_33) | (_cmp_cached_27) | (_cmp_cached_70))
            # 1h high, 1d downtrend
            & ((_cmp_cached_33) | (_cmp_cached_65))
            # 1h & 4h high, 1d overbought
            & ((_cmp_cached_78) | (_cmp_cached_6) | (_cmp_cached_70))
            # 1h high, 4h & 1d overbought
            & ((_cmp_cached_78) | (_cmp_cached_113) | (_cmp_cached_52))
            # 4h still high, 5m downtrend
            & ((_cmp_cached_96) | (_cmp_cached_203))
            # 4h high & overbought
            & ((_cmp_cached_17) | (_cmp_cached_67))
            # 4h & 1d high, 1d overbought
            & ((_cmp_cached_77) | (_cmp_cached_27) | (_cmp_cached_52))
            # 4h high, 1h & 4h overbought
            & ((_cmp_cached_6) | (_cmp_cached_82) | (_cmp_cached_20))
            # 1d high, 1d downtrend
            & ((_cmp_cached_108) | (_cmp_cached_102))
            # 1d high, 1h & 4h downtrend
            & ((_cmp_cached_131) | (_cmp_cached_109) | (_cmp_cached_204))
            # 1d high, 4h & 1d overbought
            & ((_cmp_cached_131) | (_cmp_cached_83) | (_cmp_cached_112))
            # 1d high, 1h & 4h down move
            & ((_cmp_cached_27) | (_cmp_cached_205) | (_cmp_cached_83))
            # 15m high, 1d overbought
            & ((_cmp_cached_92) | (_cmp_cached_112))
            # 1h high, 1d downtrend
            & ((_cmp_cached_37) | (_cmp_cached_42))
            # 1h high, 1d overbought
            & ((_cmp_cached_37) | (_cmp_cached_52))
            # 1h high, 4h downtrend
            & ((_cmp_cached_19) | (_cmp_cached_69))
            # 1h high, 4h overbought
            & ((_cmp_cached_19) | (_cmp_cached_67))
            # 4h high, 1h & 4h overbought
            & ((_cmp_cached_12) | (_cmp_cached_82) | (_cmp_cached_20))
            # 1d high, 1h & 1d overbought
            & ((_cmp_cached_74) | (_cmp_cached_82) | (_cmp_cached_63))
            # 1d high, 4h & 1d overbought
            & ((_cmp_cached_74) | (_cmp_cached_83) | (_cmp_cached_112))
            # big drop in the last 20 days, 1d high, 1d downtrend
            & (
              (df["close"] > (df["high_max_20_1d"] * 0.20))
              | (_cmp_cached_148)
              | (_cmp_cached_149)
            )
            # drop in last 20 days, 1h high, 1d downtrend
            & ((df["close"] > (df["high_max_20_1d"] * 0.20)) | (_cmp_cached_24) | (_cmp_cached_206))
            # drop in last 20 days. 4h high
            & ((df["close"] > (df["high_max_20_1d"] * 0.10)) | (_cmp_cached_72))
          )

          # Logic
          long_entry_logic.append(
            # (_cmp_cached_8)
            (_cmp_cached_207)
            & (_cmp_cached_208)
            # & (_cmp_cached_3)
            & (_cmp_cached_62)
            & (df["close"] < (df["EMA_20"] * 0.948))
          )

        # Condition #3 - Normal mode (Long).
        if long_entry_condition_index == 3:
          # Protections
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          long_entry_logic.append(df["protections_long_global"] == True)

          long_entry_logic.append(
            # 5m & 4h down move, 1h still high
            ((_cmp_cached_8) | (_cmp_cached_25) | (_cmp_cached_59))
            # 5m down move, 15m high, 1d overbought
            & ((_cmp_cached_8) | (_cmp_cached_76) | (_cmp_cached_52))
            # 5m down move, 15m still high, 1d downtrend
            & ((_cmp_cached_8) | (_cmp_cached_61) | (_cmp_cached_57))
            # 5m down move, 1h still high, 4h downtrend
            & ((_cmp_cached_8) | (_cmp_cached_59) | (_cmp_cached_93))
            # 5m down move, 1h high. 1d downtrend
            & ((_cmp_cached_8) | (_cmp_cached_19) | (_cmp_cached_102))
            # 5m down move, 15m & 1h high
            & ((_cmp_cached_157) | (_cmp_cached_76) | (_cmp_cached_80))
            # 5m down move, 15m & 1d high
            & ((_cmp_cached_157) | (_cmp_cached_76) | (_cmp_cached_27))
            # 5m down move, 1h & 1d high
            & ((_cmp_cached_209) | (_cmp_cached_33) | (_cmp_cached_94))
            # 15m & 1h dowbn move, 1d high
            & ((_cmp_cached_3) | (_cmp_cached_11) | (_cmp_cached_39))
            # 15m & 1d down move, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_29) | (_cmp_cached_123))
            # 15m & 1h down move, 15m still high
            & ((_cmp_cached_5) | (_cmp_cached_34) | (_cmp_cached_62))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_5) | (_cmp_cached_58) | (_cmp_cached_28))
            # 15m & 4h down move, 15m still high
            & ((_cmp_cached_5) | (_cmp_cached_100) | (_cmp_cached_62))
            # 15m down move, 15m still high, 1h high
            & ((_cmp_cached_5) | (_cmp_cached_31) | (_cmp_cached_49))
            # 15m down move, 15m still high, 1h high
            & ((_cmp_cached_5) | (_cmp_cached_62) | (_cmp_cached_19))
            # 15m down move, 15m still high, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_62) | (_cmp_cached_48))
            # 15m down move, 15m high, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_210) | (_cmp_cached_107))
            # 15m down move, 4h high, 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_12) | (_cmp_cached_57))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_84) | (_cmp_cached_34) | (_cmp_cached_122))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_84) | (_cmp_cached_34) | (_cmp_cached_123))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_84) | (_cmp_cached_38) | (_cmp_cached_19))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_84) | (_cmp_cached_117) | (_cmp_cached_68))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_84) | (_cmp_cached_25) | (_cmp_cached_17))
            # 15m & 4h down move, 1d downtrend
            & ((_cmp_cached_84) | (_cmp_cached_25) | (_cmp_cached_102))
            # 15m & 4h down move, 15m still high
            & ((_cmp_cached_84) | (_cmp_cached_25) | (_cmp_cached_61))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_84) | (_cmp_cached_100) | (_cmp_cached_27))
            # 15m & 1d down move, 15m high
            & ((_cmp_cached_84) | (_cmp_cached_29) | (_cmp_cached_76))
            # 15m down move, 4h downtrend. 15m high
            & ((_cmp_cached_84) | (_cmp_cached_189) | (_cmp_cached_210))
            # 15m down move, 15m still high, 1h still high
            & ((_cmp_cached_84) | (_cmp_cached_31) | (_cmp_cached_26))
            # 15m down move, 15m high, 4h downtrend
            & ((_cmp_cached_84) | (_cmp_cached_210) | (_cmp_cached_69))
            # 15m down move, 15m high, 1d downtrend
            & ((_cmp_cached_84) | (_cmp_cached_210) | (_cmp_cached_206))
            # 15m down move, 15m high, 1d overbought
            & ((_cmp_cached_84) | (_cmp_cached_210) | (_cmp_cached_48))
            # 15m down move, 15m & 1h high
            & ((_cmp_cached_84) | (_cmp_cached_76) | (_cmp_cached_24))
            # 15m down move, 15m & 4h high
            & ((_cmp_cached_84) | (_cmp_cached_76) | (_cmp_cached_17))
            # 15m down move, 15m & 1d high
            & ((_cmp_cached_84) | (_cmp_cached_76) | (_cmp_cached_27))
            # 15m down move, 15m still high, 4h high
            & ((_cmp_cached_84) | (_cmp_cached_76) | (_cmp_cached_12))
            # 15m down move, 15m high, 1d overbought
            & ((_cmp_cached_84) | (_cmp_cached_76) | (_cmp_cached_107))
            # 15m down move, 4h high, 1d downtrend
            & ((_cmp_cached_84) | (_cmp_cached_122) | (_cmp_cached_65))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_84) | (_cmp_cached_19) | (_cmp_cached_167))
            # 15m down move, 4h & 1d overbought
            & ((_cmp_cached_84) | (_cmp_cached_211) | (_cmp_cached_48))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_87) | (_cmp_cached_11) | (_cmp_cached_110))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_87) | (_cmp_cached_38) | (_cmp_cached_45))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_87) | (_cmp_cached_38) | (_cmp_cached_77))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_87) | (_cmp_cached_38) | (_cmp_cached_27))
            # 15m & 4h down move, 15m high
            & ((_cmp_cached_87) | (_cmp_cached_100) | (_cmp_cached_210))
            # 15m & 4h down move, 15m high
            & ((_cmp_cached_87) | (_cmp_cached_41) | (_cmp_cached_212))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_87) | (_cmp_cached_41) | (_cmp_cached_39))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_87) | (_cmp_cached_71) | (_cmp_cached_17))
            # 15m & 1h down move, 15m still high
            & ((_cmp_cached_87) | (_cmp_cached_121) | (_cmp_cached_61))
            # 15m & 1d down move, 1h still high
            & ((_cmp_cached_87) | (_cmp_cached_121) | (_cmp_cached_59))
            # 15m & 1d down move, 1h high
            & ((_cmp_cached_87) | (_cmp_cached_125) | (_cmp_cached_78))
            # 15m &1d down move, 1d overbought
            & ((_cmp_cached_87) | (_cmp_cached_73) | (_cmp_cached_167))
            # 15m down move, 15m still not low enough, 4h overbought
            & ((_cmp_cached_87) | (_cmp_cached_10) | (_cmp_cached_83))
            # 15m down move, 15m still high, 4h high
            & ((_cmp_cached_87) | (_cmp_cached_31) | (_cmp_cached_72))
            # 15m down move, 15m still high, 1h high
            & ((_cmp_cached_87) | (_cmp_cached_62) | (_cmp_cached_80))
            # 15m down move, 15m still high, 4h high
            & ((_cmp_cached_87) | (_cmp_cached_62) | (_cmp_cached_17))
            # 15m down move, 15m still high, 1d overbought
            & ((_cmp_cached_87) | (_cmp_cached_62) | (_cmp_cached_107))
            # 15m down move, 15m high, 4h downtrend
            & ((_cmp_cached_87) | (_cmp_cached_210) | (_cmp_cached_213))
            # 15m down move, 15m high, 4h overbought
            & ((_cmp_cached_87) | (_cmp_cached_210) | (_cmp_cached_50))
            # 15m down move, 15m high, 4h overbought
            & ((_cmp_cached_87) | (_cmp_cached_76) | (_cmp_cached_20))
            # 15m down move, 15m high, 4h downtrend
            & ((_cmp_cached_87) | (_cmp_cached_76) | (_cmp_cached_93))
            # 15m down move, 15m high, 1d downtrend
            & ((_cmp_cached_87) | (_cmp_cached_76) | (_cmp_cached_57))
            # 15m down move, 15m high, 1d overbought
            & ((_cmp_cached_87) | (_cmp_cached_76) | (_cmp_cached_107))
            # 15m down move, 1h high, 4h overbought
            & ((_cmp_cached_87) | (_cmp_cached_33) | (_cmp_cached_20))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_87) | (_cmp_cached_17) | (_cmp_cached_86))
            # 15m down move, 1h high, 4h downtrend
            & ((_cmp_cached_87) | (_cmp_cached_123) | (_cmp_cached_69))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_87) | (_cmp_cached_19) | (_cmp_cached_70))
            # 15m down move, 1h high
            & ((_cmp_cached_87) | (_cmp_cached_49))
            # 15m down move, 4h still high, 1d downtrend
            & ((_cmp_cached_87) | (_cmp_cached_165) | (_cmp_cached_57))
            # 15m down move, 4h high, 1d downtrend
            & ((_cmp_cached_87) | (_cmp_cached_12) | (_cmp_cached_102))
            # 15m down move, 4h & 1d overbought
            & ((_cmp_cached_87) | (_cmp_cached_211) | (_cmp_cached_48))
            # 15m & 1h down move, 15m high
            & ((_cmp_cached_88) | (_cmp_cached_32) | (_cmp_cached_76))
            # 15m & 4h down move, 15m high
            & ((_cmp_cached_88) | (_cmp_cached_181) | (_cmp_cached_212))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_88) | (_cmp_cached_99) | (_cmp_cached_80))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_88) | (_cmp_cached_71) | (_cmp_cached_80))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_88) | (_cmp_cached_71) | (_cmp_cached_77))
            # 15m & 1d down move, 1d high
            & ((_cmp_cached_88) | (_cmp_cached_178) | (_cmp_cached_214))
            # 15m & 1d down move, 1d high
            & ((_cmp_cached_88) | (_cmp_cached_198) | (_cmp_cached_94))
            # 15m down move, 15m high, 4h downtrend
            & ((_cmp_cached_88) | (_cmp_cached_76) | (_cmp_cached_69))
            # 15m down move, 15m high, 4h overbought
            & ((_cmp_cached_88) | (_cmp_cached_76) | (_cmp_cached_50))
            # 15m down move, 15m high, 1d overbought
            & ((_cmp_cached_88) | (_cmp_cached_76) | (_cmp_cached_112))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_88) | (_cmp_cached_24) | (_cmp_cached_17))
            # 15m down move, 1h high, 1d downtrend
            & ((_cmp_cached_88) | (_cmp_cached_24) | (_cmp_cached_93))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_88) | (_cmp_cached_78) | (_cmp_cached_167))
            # 15m down move, 4h high, 1d high
            & ((_cmp_cached_88) | (_cmp_cached_40) | (_cmp_cached_39))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_88) | (_cmp_cached_77) | (_cmp_cached_50))
            # 15m down move, 15m still high, 1h still high
            & ((_cmp_cached_88) | (_cmp_cached_61) | (_cmp_cached_26))
            # 15m down move, 1h high, 4h high
            & ((_cmp_cached_88) | (_cmp_cached_37) | (_cmp_cached_6))
            # 15m down move, 4h & 1d overbought
            & ((_cmp_cached_88) | (_cmp_cached_86) | (_cmp_cached_107))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_89) | (_cmp_cached_32) | (_cmp_cached_33))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_89) | (_cmp_cached_32) | (_cmp_cached_52))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_89) | (_cmp_cached_21) | (_cmp_cached_17))
            # 15m down move, 1d high, 15m high
            & ((_cmp_cached_89) | (_cmp_cached_215) | (_cmp_cached_76))
            # 15m down move, 15m high, 1d downtrend
            & ((_cmp_cached_89) | (_cmp_cached_210) | (_cmp_cached_65))
            # 15m down move, 15m high, 15m downtrend
            & ((_cmp_cached_89) | (_cmp_cached_76) | (_cmp_cached_159))
            # 15m down move, 15m high, 1d overbought
            & ((_cmp_cached_89) | (_cmp_cached_76) | (_cmp_cached_216))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_89) | (_cmp_cached_80) | (_cmp_cached_70))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_89) | (_cmp_cached_17) | (_cmp_cached_83))
            # 15m down move, 15m high, 4h overbought
            & ((_cmp_cached_89) | (_cmp_cached_92) | (_cmp_cached_217))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_89) | (_cmp_cached_49) | (_cmp_cached_107))
            # 15m down move, 15m high, 4h high
            & ((_cmp_cached_184) | (_cmp_cached_210) | (_cmp_cached_72))
            # 15m down move, 15m high, 4h overbought
            & ((_cmp_cached_184) | (_cmp_cached_76) | (_cmp_cached_67))
            # 15m down move, 1h high, 4h overbought
            & ((_cmp_cached_184) | (_cmp_cached_78) | (_cmp_cached_196))
            # 15m down move, 4h high, 1d overbought
            & ((_cmp_cached_184) | (_cmp_cached_77) | (_cmp_cached_111))
            # 15m down move, 1h high, 1d downtrend
            & ((_cmp_cached_184) | (_cmp_cached_49) | (_cmp_cached_42))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_184) | (_cmp_cached_72) | (_cmp_cached_20))
            # 15m down move, 15m high, 1h downtrend
            & ((_cmp_cached_90) | (_cmp_cached_76) | (_cmp_cached_129))
            # 15m down move, 15m & 4h high
            & ((_cmp_cached_90) | (_cmp_cached_212) | (_cmp_cached_172))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_90) | (_cmp_cached_12) | (_cmp_cached_51))
            # 1h & 4h down move, 15m still high
            & ((_cmp_cached_7) | (_cmp_cached_58) | (_cmp_cached_61))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_122))
            # 1h down move, 4h still high, 4h downtrend
            & ((_cmp_cached_9) | (_cmp_cached_96) | (_cmp_cached_69))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_9) | (_cmp_cached_17) | (_cmp_cached_20))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_15) | (_cmp_cached_25) | (_cmp_cached_191))
            # 1h & 4h down move, 15m high
            & ((_cmp_cached_15) | (_cmp_cached_25) | (_cmp_cached_76))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_15) | (_cmp_cached_100) | (_cmp_cached_102))
            # 1h & 1d down move, 1d overbought
            & ((_cmp_cached_15) | (_cmp_cached_192) | (_cmp_cached_95))
            # 1h & 1d down move, 1d overbought
            & ((_cmp_cached_15) | (_cmp_cached_126) | (_cmp_cached_52))
            # 1h down move, 1h still not low enough, 1d downtrend
            & ((_cmp_cached_15) | (_cmp_cached_161) | (_cmp_cached_102))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_30) | (_cmp_cached_16) | (_cmp_cached_108))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_30) | (_cmp_cached_16) | (_cmp_cached_70))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_30) | (_cmp_cached_77) | (_cmp_cached_48))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_11) | (_cmp_cached_181) | (_cmp_cached_77))
            # 1h & 1d down move, 1d still high
            & ((_cmp_cached_11) | (_cmp_cached_125) | (_cmp_cached_14))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_24) | (_cmp_cached_167))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_11) | (_cmp_cached_108) | (_cmp_cached_167))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_11) | (_cmp_cached_162) | (_cmp_cached_57))
            # 1h down move, 4h downtrend, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_213) | (_cmp_cached_107))
            # 1h down move, 15m & 1h still high
            & ((_cmp_cached_32) | (_cmp_cached_31) | (_cmp_cached_26))
            # 1h down move, 1h still high 1d overbought
            & ((_cmp_cached_32) | (_cmp_cached_26) | (_cmp_cached_111))
            # 1h down move, 1h high, 4h downtrend
            & ((_cmp_cached_32) | (_cmp_cached_115) | (_cmp_cached_69))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_32) | (_cmp_cached_24) | (_cmp_cached_70))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_32) | (_cmp_cached_162) | (_cmp_cached_20))
            # 1h down move, 4h & 1h overbought
            & ((_cmp_cached_32) | (_cmp_cached_51) | (_cmp_cached_52))
            # 1h & 1d down move, 1h high
            & ((_cmp_cached_34) | (_cmp_cached_192) | (_cmp_cached_68))
            # 1h down move, 15m still high, 4h  high
            & ((_cmp_cached_34) | (_cmp_cached_31) | (_cmp_cached_77))
            # 1h down move, 15m still high, 4h high
            & ((_cmp_cached_34) | (_cmp_cached_31) | (_cmp_cached_64))
            # 1h down move, 15m still high, 4h high
            & ((_cmp_cached_34) | (_cmp_cached_62) | (_cmp_cached_17))
            # 1h down move, 15m & 1d high
            & ((_cmp_cached_34) | (_cmp_cached_210) | (_cmp_cached_108))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_34) | (_cmp_cached_24) | (_cmp_cached_72))
            # 1h down move, 1h & 1d high
            & ((_cmp_cached_34) | (_cmp_cached_33) | (_cmp_cached_94))
            # 1h down move, 1h downtrend, 4h overbought
            & ((_cmp_cached_34) | (_cmp_cached_177) | (_cmp_cached_20))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_34) | (_cmp_cached_24) | (_cmp_cached_218))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_34) | (_cmp_cached_33) | (_cmp_cached_107))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_34) | (_cmp_cached_12) | (_cmp_cached_42))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_36) | (_cmp_cached_99) | (_cmp_cached_37))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_36) | (_cmp_cached_99) | (_cmp_cached_162))
            # 1h down move, 15m still high, 4h downtrend
            & ((_cmp_cached_36) | (_cmp_cached_155) | (_cmp_cached_219))
            # 1h down move, 15m still high, 1d overbought
            & ((_cmp_cached_36) | (_cmp_cached_62) | (_cmp_cached_107))
            # 1h down move, 15m & 4h high
            & ((_cmp_cached_36) | (_cmp_cached_76) | (_cmp_cached_17))
            # 1h down move, 1h still high, 4h high
            & ((_cmp_cached_36) | (_cmp_cached_26) | (_cmp_cached_12))
            # 1h down move, 1h still high, 1d overbought
            & ((_cmp_cached_36) | (_cmp_cached_26) | (_cmp_cached_48))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_36) | (_cmp_cached_24) | (_cmp_cached_20))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_36) | (_cmp_cached_45) | (_cmp_cached_194))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_36) | (_cmp_cached_78) | (_cmp_cached_6))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_36) | (_cmp_cached_19) | (_cmp_cached_220))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_36) | (_cmp_cached_50) | (_cmp_cached_107))
            # 1h down move, 15m high, 4h overbought
            & ((_cmp_cached_38) | (_cmp_cached_76) | (_cmp_cached_51))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_38) | (_cmp_cached_80) | (_cmp_cached_20))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_38) | (_cmp_cached_77) | (_cmp_cached_20))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_38) | (_cmp_cached_77) | (_cmp_cached_113))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_38) | (_cmp_cached_27) | (_cmp_cached_70))
            # 1h down move, 1h still high, 1d overbought
            & ((_cmp_cached_38) | (_cmp_cached_28) | (_cmp_cached_111))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_38) | (_cmp_cached_74) | (_cmp_cached_95))
            # 1h down move, 15m & 1h high
            & ((_cmp_cached_117) | (_cmp_cached_76) | (_cmp_cached_80))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_117) | (_cmp_cached_33) | (_cmp_cached_50))
            # 1h down move, 4h still high, 1d overbought
            & ((_cmp_cached_117) | (_cmp_cached_122) | (_cmp_cached_111))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_117) | (_cmp_cached_6) | (_cmp_cached_86))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_117) | (_cmp_cached_19) | (_cmp_cached_6))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_117) | (_cmp_cached_64) | (_cmp_cached_50))
            # 1h down move, 1h high, 1d high
            & ((_cmp_cached_174) | (_cmp_cached_37) | (_cmp_cached_27))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_174) | (_cmp_cached_19) | (_cmp_cached_102))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_174) | (_cmp_cached_12) | (_cmp_cached_196))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_53) | (_cmp_cached_19) | (_cmp_cached_48))
            # 1h down move, 15m & 1h high
            & ((_cmp_cached_221) | (_cmp_cached_76) | (_cmp_cached_80))
            # 1h down move, 1h high & overbought
            & ((_cmp_cached_221) | (_cmp_cached_19) | (_cmp_cached_82))
            # 4h down move, 1h still high, 1d downtrend
            & ((_cmp_cached_151) | (_cmp_cached_28) | (_cmp_cached_102))
            # 4h down move, 1h still high, 4h downtrend
            & ((_cmp_cached_151) | (_cmp_cached_59) | (_cmp_cached_103))
            # 4h down move, 4h & 1d downtrend
            & ((_cmp_cached_151) | (_cmp_cached_69) | (_cmp_cached_57))
            # 4h down move, 15m high, 1h still high
            & ((_cmp_cached_55) | (_cmp_cached_76) | (_cmp_cached_59))
            # 4h down move, 15m high
            & ((_cmp_cached_55) | (_cmp_cached_92))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_55) | (_cmp_cached_165) | (_cmp_cached_57))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_58) | (_cmp_cached_104) | (_cmp_cached_14))
            # 4h & 1d down move, 1d downtrend
            & ((_cmp_cached_58) | (_cmp_cached_104) | (_cmp_cached_57))
            # 4h & 1d down move, 4h still high
            & ((_cmp_cached_58) | (_cmp_cached_178) | (_cmp_cached_35))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_58) | (_cmp_cached_192) | (_cmp_cached_56))
            # 4h down move, 15m still not low enough, 1d downtrend
            & ((_cmp_cached_58) | (_cmp_cached_152) | (_cmp_cached_65))
            # 4h down move, 15m high, 4h downtrend
            & ((_cmp_cached_58) | (_cmp_cached_222) | (_cmp_cached_204))
            # 4h down move, 15m high
            & ((_cmp_cached_58) | (_cmp_cached_92))
            # 4h & 1d down move, 15m high
            & ((_cmp_cached_25) | (_cmp_cached_192) | (_cmp_cached_92))
            # 4h & 1d down move, 4h high
            & ((_cmp_cached_25) | (_cmp_cached_192) | (_cmp_cached_64))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_25) | (_cmp_cached_125) | (_cmp_cached_106))
            # 4h down move, 15m still high, 1h high
            & ((_cmp_cached_25) | (_cmp_cached_62) | (_cmp_cached_123))
            # 4h down move, 15m & 1d high
            & ((_cmp_cached_25) | (_cmp_cached_76) | (_cmp_cached_108))
            # 4h down move, 15m high
            & ((_cmp_cached_25) | (_cmp_cached_180))
            # 4h down move, 1d high
            & ((_cmp_cached_25) | (_cmp_cached_74))
            # 4h down move, 1h & 4h downtrend
            & ((_cmp_cached_25) | (_cmp_cached_109) | (_cmp_cached_103))
            # 4h & 1d down move, 1h still high
            & ((_cmp_cached_100) | (_cmp_cached_104) | (_cmp_cached_110))
            # 4h & 1d down move, 15m high
            & ((_cmp_cached_100) | (_cmp_cached_121) | (_cmp_cached_92))
            # 4h & 1d down move, 1d overbought
            & ((_cmp_cached_100) | (_cmp_cached_223) | (_cmp_cached_107))
            # 4h down move, 15m & 4h still high
            & ((_cmp_cached_100) | (_cmp_cached_62) | (_cmp_cached_122))
            # 4h down move, 15m high, 1d high
            & ((_cmp_cached_100) | (_cmp_cached_76) | (_cmp_cached_148))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_100) | (_cmp_cached_122) | (_cmp_cached_65))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_100) | (_cmp_cached_94) | (_cmp_cached_95))
            # 4h down move, 15m high, 4h downtrend
            & ((_cmp_cached_100) | (_cmp_cached_180) | (_cmp_cached_204))
            # 4h down move, 1h high, 1d downtrend
            & ((_cmp_cached_100) | (_cmp_cached_123) | (_cmp_cached_65))
            # 4h down move, 4h still not low enough, 4h downtrend
            & ((_cmp_cached_100) | (_cmp_cached_124) | (_cmp_cached_93))
            # 4h down move, 4h high, 1d downtrend
            & ((_cmp_cached_100) | (_cmp_cached_162) | (_cmp_cached_194))
            # 4h & 1d down move, 1d overbought
            & ((_cmp_cached_16) | (_cmp_cached_125) | (_cmp_cached_70))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_16) | (_cmp_cached_198) | (_cmp_cached_108))
            # 4h down move, 15m still high, 1h high
            & ((_cmp_cached_16) | (_cmp_cached_62) | (_cmp_cached_80))
            # 4h down move, 15m & 4h still high
            & ((_cmp_cached_16) | (_cmp_cached_62) | (_cmp_cached_122))
            # 4h down move, 15m high, 1d overbought
            & ((_cmp_cached_16) | (_cmp_cached_76) | (_cmp_cached_48))
            # 4h down move, 1h high, 1d overbought
            & ((_cmp_cached_16) | (_cmp_cached_78) | (_cmp_cached_107))
            # 4h down move, 4h & 1d high
            & ((_cmp_cached_16) | (_cmp_cached_40) | (_cmp_cached_27))
            # 4h down move, 4h high, 1d downtrend
            & ((_cmp_cached_16) | (_cmp_cached_40) | (_cmp_cached_206))
            # 4h down move, 4h high, 1d downtrend
            & ((_cmp_cached_16) | (_cmp_cached_17) | (_cmp_cached_57))
            # 4h down move, 4h high, 1d overbought
            & ((_cmp_cached_16) | (_cmp_cached_17) | (_cmp_cached_52))
            # 4h down move, 1h still high, 1d overbought
            & ((_cmp_cached_16) | (_cmp_cached_59) | (_cmp_cached_48))
            # 4h down move, 4h high, 1d downtrend
            & ((_cmp_cached_16) | (_cmp_cached_12) | (_cmp_cached_42))
            # 4h down move, 1h high, 1h downtrend
            & ((_cmp_cached_41) | (_cmp_cached_24) | (_cmp_cached_132))
            # 4h & 1d down move, 1d overbought
            & ((_cmp_cached_41) | (_cmp_cached_73) | (_cmp_cached_48))
            # 4h down move, 1d downtrend, 1d overbought
            & ((_cmp_cached_41) | (_cmp_cached_224) | (_cmp_cached_52))
            # 4h down move, 15m high, 4h high
            & ((_cmp_cached_41) | (_cmp_cached_210) | (_cmp_cached_46))
            # 4h down move, 1h high, 1d downtrend
            & ((_cmp_cached_41) | (_cmp_cached_78) | (_cmp_cached_57))
            # 4h down move, 1h high, 1d downtrend
            & ((_cmp_cached_41) | (_cmp_cached_19) | (_cmp_cached_65))
            # 4h down move, 1h high, 1d overbought
            & ((_cmp_cached_41) | (_cmp_cached_49) | (_cmp_cached_107))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_41) | (_cmp_cached_74) | (_cmp_cached_95))
            # 4h down move, 15m still high, 1h high
            & ((_cmp_cached_21) | (_cmp_cached_31) | (_cmp_cached_49))
            # 4h down move, 15m still high, 4h high
            & ((_cmp_cached_21) | (_cmp_cached_62) | (_cmp_cached_77))
            # 4h down move, 15m high, 1h high
            & ((_cmp_cached_21) | (_cmp_cached_76) | (_cmp_cached_37))
            # 4h down move, 4h & 1d high
            & ((_cmp_cached_21) | (_cmp_cached_77) | (_cmp_cached_27))
            # 4h down move, 1d high, 1d downtrend
            & ((_cmp_cached_21) | (_cmp_cached_60) | (_cmp_cached_102))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_21) | (_cmp_cached_39) | (_cmp_cached_52))
            # 4h down move, 15m still high, 1d overbought
            & ((_cmp_cached_181) | (_cmp_cached_62) | (_cmp_cached_107))
            # 4h down move, 15m high, 1d overbought
            & ((_cmp_cached_181) | (_cmp_cached_76) | (_cmp_cached_111))
            # 4h down move, 1h & 4h high
            & ((_cmp_cached_181) | (_cmp_cached_24) | (_cmp_cached_77))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_181) | (_cmp_cached_27) | (_cmp_cached_167))
            # 4h down move, 15m high, 1h high
            & ((_cmp_cached_181) | (_cmp_cached_92) | (_cmp_cached_80))
            # 4h down move, 1h high, 1d overbought
            & ((_cmp_cached_181) | (_cmp_cached_37) | (_cmp_cached_112))
            # 4h down move, 4h & 1d overbought
            & ((_cmp_cached_181) | (_cmp_cached_50) | (_cmp_cached_70))
            # 4h down move, 15m still high, 4h high
            & ((_cmp_cached_91) | (_cmp_cached_31) | (_cmp_cached_46))
            # 45 down move, 15m high, 1h high
            & ((_cmp_cached_91) | (_cmp_cached_76) | (_cmp_cached_37))
            # 4h down move, 15m high, 4h high
            & ((_cmp_cached_91) | (_cmp_cached_76) | (_cmp_cached_64))
            # 4h down move, 4h high, 1d overbought
            & ((_cmp_cached_91) | (_cmp_cached_40) | (_cmp_cached_48))
            # 4h down move, 4h high & overbought
            & ((_cmp_cached_91) | (_cmp_cached_77) | (_cmp_cached_51))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_91) | (_cmp_cached_106) | (_cmp_cached_70))
            # 4h down move, 1d high, 1d downtrend
            & ((_cmp_cached_91) | (_cmp_cached_108) | (_cmp_cached_149))
            # 4h down move, 1d high, 4h overbought
            & ((_cmp_cached_91) | (_cmp_cached_94) | (_cmp_cached_50))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_91) | (_cmp_cached_39) | (_cmp_cached_167))
            # 4h down move, 4h & 1d overbought
            & ((_cmp_cached_91) | (_cmp_cached_51) | (_cmp_cached_111))
            # 4h down move, 15m & 1h high
            & ((_cmp_cached_99) | (_cmp_cached_76) | (_cmp_cached_80))
            # 4h down move, 4h still high, 1h high
            & ((_cmp_cached_99) | (_cmp_cached_96) | (_cmp_cached_37))
            # 4h down move, 4h high, 1d overbought
            & ((_cmp_cached_99) | (_cmp_cached_17) | (_cmp_cached_52))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_99) | (_cmp_cached_131) | (_cmp_cached_63))
            # 4h down move, 1d high, 4h overbought
            & ((_cmp_cached_99) | (_cmp_cached_94) | (_cmp_cached_50))
            # 4h down move, 4h high, 1d downtrend
            & ((_cmp_cached_99) | (_cmp_cached_162) | (_cmp_cached_57))
            # 4h down move, 4h downtrend, 1d overbought
            & ((_cmp_cached_99) | (_cmp_cached_69) | (_cmp_cached_167))
            # 4h down move, 1h high, 4h overbought
            & ((_cmp_cached_175) | (_cmp_cached_80) | (_cmp_cached_20))
            # 4h down move, 4h high & overbought
            & ((_cmp_cached_175) | (_cmp_cached_17) | (_cmp_cached_20))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_175) | (_cmp_cached_94) | (_cmp_cached_112))
            # 4h down move, 4h high & overbought
            & ((_cmp_cached_175) | (_cmp_cached_12) | (_cmp_cached_50))
            # 4h down move, 15m high, 1h high
            & ((_cmp_cached_71) | (_cmp_cached_210) | (_cmp_cached_49))
            # 4h down move, 4h high & overbought
            & ((_cmp_cached_71) | (_cmp_cached_17) | (_cmp_cached_51))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_71) | (_cmp_cached_35) | (_cmp_cached_102))
            # 4h down move, 4h & 1d overbought
            & ((_cmp_cached_71) | (_cmp_cached_51) | (_cmp_cached_107))
            # 4h down move, 15m high, 4h high
            & ((_cmp_cached_197) | (_cmp_cached_76) | (_cmp_cached_46))
            # 4h down move, 4h high & overbought
            & ((_cmp_cached_197) | (_cmp_cached_77) | (_cmp_cached_50))
            # 1d down move, 4h & 1d downtrend
            & ((_cmp_cached_225) | (_cmp_cached_213) | (_cmp_cached_42))
            # 1d down move, 15m still high, 4h high
            & ((_cmp_cached_153) | (_cmp_cached_76) | (_cmp_cached_12))
            # 1d down move, 4h & 1d downtrend
            & ((_cmp_cached_153) | (_cmp_cached_69) | (_cmp_cached_194))
            # 1d down move, 4h & 1d downtrend
            & ((_cmp_cached_153) | (_cmp_cached_103) | (_cmp_cached_42))
            # 1d down move, 1h high, 1d downtrend
            & ((_cmp_cached_29) | (_cmp_cached_45) | (_cmp_cached_102))
            # 1d down move, 4h & 1d downtrend
            & ((_cmp_cached_29) | (_cmp_cached_93) | (_cmp_cached_65))
            # 1d down move, 15m high, 1h high
            & ((_cmp_cached_104) | (_cmp_cached_210) | (_cmp_cached_19))
            # 1d down move, 15m high, 1h high
            & ((_cmp_cached_104) | (_cmp_cached_76) | (_cmp_cached_80))
            # 1d down move, 4h high, 4h downtrend
            & ((_cmp_cached_104) | (_cmp_cached_64) | (_cmp_cached_69))
            # 1d down move, 15m high, 4h high
            & ((_cmp_cached_121) | (_cmp_cached_76) | (_cmp_cached_12))
            # 1d down move, 15m high, 4h downtrend
            & ((_cmp_cached_121) | (_cmp_cached_76) | (_cmp_cached_103))
            # 1d down move, 1h & 1d high
            & ((_cmp_cached_121) | (_cmp_cached_33) | (_cmp_cached_108))
            # 1d down move, 1d still high, 1d downtrend
            & ((_cmp_cached_121) | (_cmp_cached_14) | (_cmp_cached_57))
            # 1d down move, 1d high & overbought
            & ((_cmp_cached_178) | (_cmp_cached_199) | (_cmp_cached_95))
            # 1d down move, 1h high, 1d downtrend
            & ((_cmp_cached_178) | (_cmp_cached_37) | (_cmp_cached_167))
            # 1d down move, 1h & 1d high
            & ((_cmp_cached_192) | (_cmp_cached_24) | (_cmp_cached_94))
            # 1d down move, 1h high, 1d overbought
            & ((_cmp_cached_125) | (_cmp_cached_78) | (_cmp_cached_63))
            # 1d down move, 1d high & overbought
            & ((_cmp_cached_125) | (_cmp_cached_27) | (_cmp_cached_70))
            # 1d down move, 1d high & overbought
            & ((_cmp_cached_125) | (_cmp_cached_108) | (_cmp_cached_95))
            # 1d down move, 1h high, 1d overbought
            & ((_cmp_cached_125) | (_cmp_cached_37) | (_cmp_cached_107))
            # 15m still high, 4h high, 1d overbought
            & ((_cmp_cached_62) | (_cmp_cached_4) | (_cmp_cached_216))
            # 15m still high, 1h downtrend, 4h overbought
            & ((_cmp_cached_62) | (_cmp_cached_132) | (_cmp_cached_113))
            # 15m high, 4h high & overbought
            & ((_cmp_cached_210) | (_cmp_cached_17) | (_cmp_cached_20))
            # 15m & 4h high, 1d overbought
            & ((_cmp_cached_210) | (_cmp_cached_17) | (_cmp_cached_95))
            # 15m high, 15m & 4h overbought
            & ((_cmp_cached_210) | (_cmp_cached_226) | (_cmp_cached_20))
            # 15m high, 4h downtrend
            & ((_cmp_cached_210) | (_cmp_cached_103))
            # 15m & 1h & 4h high
            & ((_cmp_cached_76) | (_cmp_cached_80) | (_cmp_cached_6))
            # 15m & 4h & 1d high
            & ((_cmp_cached_76) | (_cmp_cached_17) | (_cmp_cached_94))
            # 15m & 4h high, 4h overbought
            & ((_cmp_cached_76) | (_cmp_cached_17) | (_cmp_cached_50))
            # 15m & 4h high, 1d downtrend
            & ((_cmp_cached_76) | (_cmp_cached_17) | (_cmp_cached_57))
            # 15m & 1d high, 1d overbought
            & ((_cmp_cached_76) | (_cmp_cached_94) | (_cmp_cached_48))
            # 15m high, 4h downtrend, 1d overbought
            & ((_cmp_cached_76) | (_cmp_cached_103) | (_cmp_cached_111))
            # 4h down move, 1h still high, 1d downtrend
            & ((_cmp_cached_25) | (_cmp_cached_110) | (_cmp_cached_42))
            # 1h & 4h high, 4h overbought
            & ((_cmp_cached_33) | (_cmp_cached_6) | (_cmp_cached_50))
            # 1h high, 1d high & overbought
            & ((_cmp_cached_78) | (_cmp_cached_27) | (_cmp_cached_70))
            # 1h high, 4h downtrend
            & ((_cmp_cached_78) | (_cmp_cached_69))
            # 1h high, 4h & 1d overbought
            & ((_cmp_cached_78) | (_cmp_cached_50) | (_cmp_cached_167))
            # 4h & 1d high, 4h overbought
            & ((_cmp_cached_77) | (_cmp_cached_27) | (_cmp_cached_50))
            # 4h & 1d high, 1d downtrend
            & ((_cmp_cached_77) | (_cmp_cached_27) | (_cmp_cached_57))
            # 1d high, 4h & 1d downtrend
            & ((_cmp_cached_108) | (_cmp_cached_69) | (_cmp_cached_57))
            # 1d high, 1h & 4h downtrend
            & ((_cmp_cached_131) | (_cmp_cached_109) | (_cmp_cached_204))
            # 1d high, 4h downtrend
            & ((_cmp_cached_131) | (_cmp_cached_103))
            # 1d high, 4h downtrend, 1d overbought
            & ((_cmp_cached_131) | (_cmp_cached_103) | (_cmp_cached_216))
            # 1d high, 4h & 1d overbought
            & ((_cmp_cached_27) | (_cmp_cached_51) | (_cmp_cached_52))
            # 15m & 1h high, 1d overbought
            & (
              (_cmp_cached_92) | (_cmp_cached_37) | (_cmp_cached_107)
            )
            # 15m & 1d high
            & ((_cmp_cached_227) | (_cmp_cached_39))
            # 1h high, 4h & 1d downtrend
            & ((_cmp_cached_123) | (_cmp_cached_103) | (_cmp_cached_102))
            # 1h high, 4h downtrend
            & ((_cmp_cached_37) | (_cmp_cached_103))
            # 1h high, 1d downtrend
            & ((_cmp_cached_37) | (_cmp_cached_57))
            # 4h high, 4h overbought, 1d downtrend
            & ((_cmp_cached_72) | (_cmp_cached_20) | (_cmp_cached_57))
            # 1d still high, 4h & 1d downtrend
            & ((_cmp_cached_14) | (_cmp_cached_103) | (_cmp_cached_102))
            # 1d P&D, 4h downtrend
            & ((_cmp_cached_228) | (df["change_pct_1d"].shift(288) < 50.0) | (_cmp_cached_25))
            # 1d P&D, 15m high
            & ((_cmp_cached_229) | (df["change_pct_1d"].shift(288) < 20.0) | (_cmp_cached_76))
            # 1d red with top wick, 4h high
            & ((_cmp_cached_229) | (_cmp_cached_230) | (_cmp_cached_77))
            # 1d red, previous 1d top wick, 15m high
            & (
              (_cmp_cached_231) | (df["top_wick_pct_1d"].shift(288) < 40.0) | (_cmp_cached_76)
            )
            # 1d green with top wick, 4h overbought
            & ((_cmp_cached_232) | (_cmp_cached_139) | (_cmp_cached_20))
            # 1d green, 15m down move, 1h high
            & ((_cmp_cached_144) | (_cmp_cached_88) | (_cmp_cached_24))
            # 1d green, 4h down move, 4h still high
            & ((_cmp_cached_142) | (_cmp_cached_21) | (_cmp_cached_96))
            # 1d top wick, 4h down move, 1d overbought
            & ((_cmp_cached_233) | (_cmp_cached_21) | (_cmp_cached_112))
            # big drop in the last 20 days, 1d high, 1d downtrend
            & (
              (df["close"] > (df["high_max_20_1d"] * 0.20))
              | (_cmp_cached_148)
              | (_cmp_cached_149)
            )
          )

          # Logic
          long_entry_logic.append(
            (df["RSI_20"] < df["RSI_20"].shift(1))
            & (_cmp_cached_234)
            & (_cmp_cached_235)
            & (_cmp_cached_236)
            & (_cmp_cached_237)
            & (df["close"] < df["SMA_16"] * 0.965)
            & (df["close"] < df["SMA_16_1h"] * 0.985)
          )

        # Condition #4 - Normal mode (Long).
        if long_entry_condition_index == 4:
          # Protections
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          long_entry_logic.append(df["protections_long_global"] == True)

          long_entry_logic.append(
            (_cmp_cached_1)
            # 5m & 1h down move, 1d still high
            & ((_cmp_cached_0) | (_cmp_cached_13) | (_cmp_cached_119))
            # 5m & 1h & 4h down move
            & ((_cmp_cached_0) | (_cmp_cached_7) | (_cmp_cached_58))
            # 5m & 1h down move, 1h still not low enough
            & ((_cmp_cached_0) | (_cmp_cached_9) | (_cmp_cached_150))
            # 5m & 1h down move, 1d high
            & ((_cmp_cached_0) | (_cmp_cached_15) | (_cmp_cached_108))
            # 5m & 1h down move, 1d high
            & ((_cmp_cached_0) | (_cmp_cached_30) | (_cmp_cached_27))
            # 5m & 1h down move, 1h high
            & ((_cmp_cached_0) | (_cmp_cached_117) | (_cmp_cached_24))
            # 5m & 1h down move, 1h still high
            & ((_cmp_cached_0) | (_cmp_cached_32) | (_cmp_cached_59))
            # 5m & 1h down move, 1d downtrend
            & ((_cmp_cached_0) | (_cmp_cached_25) | (_cmp_cached_102))
            # 5m & 4h down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_16) | (_cmp_cached_17))
            # 5m & 1d down move, 15m still high
            & ((_cmp_cached_0) | (_cmp_cached_104) | (_cmp_cached_155))
            # 5m down move, 1h high, 4h overbought
            & ((_cmp_cached_0) | (_cmp_cached_19) | (_cmp_cached_20))
            # 5m & 4h down move, 15m still high
            & ((_cmp_cached_8) | (_cmp_cached_16) | (_cmp_cached_61))
            # 5m down move, 4h high, 1h overbought
            & ((_cmp_cached_157) | (_cmp_cached_6) | (_cmp_cached_158))
            # 15m & 1h down move, 1d still high
            & ((_cmp_cached_3) | (_cmp_cached_7) | (_cmp_cached_119))
            # 15m & 1h down move, 1d still high
            & ((_cmp_cached_3) | (_cmp_cached_9) | (_cmp_cached_238))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_3) | (_cmp_cached_32) | (_cmp_cached_28))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_3) | (_cmp_cached_32) | (_cmp_cached_107))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_36) | (_cmp_cached_64))
            # 15m & 4h down move, 1d overbought
            & ((_cmp_cached_3) | (_cmp_cached_25) | (_cmp_cached_216))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_3) | (_cmp_cached_41) | (_cmp_cached_27))
            # 15m & 1h down move, 15m stil high
            & ((_cmp_cached_5) | (_cmp_cached_9) | (_cmp_cached_61))
            # 15m & 1h down move, 4h downtrend
            & ((_cmp_cached_5) | (_cmp_cached_9) | (_cmp_cached_213))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_5) | (_cmp_cached_15) | (_cmp_cached_59))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_15) | (_cmp_cached_17))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_30) | (_cmp_cached_52))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_5) | (_cmp_cached_11) | (_cmp_cached_33))
            # 15m down move, 4h high, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_17) | (_cmp_cached_48))
            # 15m down move, 4h & 1d high
            & ((_cmp_cached_5) | (_cmp_cached_46) | (_cmp_cached_27))
            # 15m down move, 1h high, 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_37) | (_cmp_cached_42))
            # 15m down move, 1h high
            & ((_cmp_cached_5) | (_cmp_cached_19))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_84) | (_cmp_cached_11) | (_cmp_cached_28))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_84) | (_cmp_cached_25) | (_cmp_cached_74))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_84) | (_cmp_cached_17) | (_cmp_cached_20))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_84) | (_cmp_cached_72) | (_cmp_cached_50))
            # 15m down move, 4h & 1d downtrend
            & ((_cmp_cached_84) | (_cmp_cached_93) | (_cmp_cached_65))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_87) | (_cmp_cached_30) | (_cmp_cached_24))
            # 15m down move, 4h high, 1d overbought
            & ((_cmp_cached_87) | (_cmp_cached_46) | (_cmp_cached_48))
            # 15m down move, 4h high, 1h overbought
            & ((_cmp_cached_87) | (_cmp_cached_6) | (_cmp_cached_158))
            # 15m down move, 1h high & overbought
            & ((_cmp_cached_87) | (_cmp_cached_49) | (_cmp_cached_82))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_88) | (_cmp_cached_99) | (_cmp_cached_12))
            # 15m down move, 4h high, 4h overbought
            & ((_cmp_cached_88) | (_cmp_cached_40) | (_cmp_cached_86))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_89) | (_cmp_cached_36) | (_cmp_cached_47))
            # 15m & 1h down move, 4h overbought
            & ((_cmp_cached_90) | (_cmp_cached_117) | (_cmp_cached_86))
            # 1h & 4h down move, 15m downtrend
            & ((_cmp_cached_13) | (_cmp_cached_151) | (_cmp_cached_187))
            # 1h & 4h down move, 15m downtrend
            & ((_cmp_cached_13) | (_cmp_cached_58) | (_cmp_cached_43))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_13) | (_cmp_cached_100) | (_cmp_cached_148))
            # 1h down move, 1h high, 4h high
            & ((_cmp_cached_13) | (_cmp_cached_24) | (_cmp_cached_12))
            # 1h down move, 15m still high
            & ((_cmp_cached_13) | (_cmp_cached_61))
            # 1h down move, 1h still high, 4h overbought
            & ((_cmp_cached_13) | (_cmp_cached_59) | (_cmp_cached_20))
            # 1h & 4h & 1d down move
            & ((_cmp_cached_7) | (_cmp_cached_55) | (_cmp_cached_153))
            # 1h & 4h down move, 1h downtrend
            & ((_cmp_cached_7) | (_cmp_cached_55) | (_cmp_cached_129))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_7) | (_cmp_cached_58) | (_cmp_cached_65))
            # 1h down move, 4h high, 1h downtrend
            & ((_cmp_cached_7) | (_cmp_cached_64) | (_cmp_cached_239))
            # 1h down move, 4h high, 1h downtrend
            & ((_cmp_cached_7) | (_cmp_cached_64) | (_cmp_cached_240))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_7) | (_cmp_cached_39) | (_cmp_cached_167))
            # 1h down move, 1d overbought
            & ((_cmp_cached_7) | (_cmp_cached_48))
            # 1h & 4h & 1d down move
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_29))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_9) | (_cmp_cached_25) | (_cmp_cached_169))
            # 1h & 4h down move, 1h downtrend
            & ((_cmp_cached_9) | (_cmp_cached_25) | (_cmp_cached_129))
            # 1h & 4h down move, 1h still high
            & ((_cmp_cached_9) | (_cmp_cached_100) | (_cmp_cached_26))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_9) | (_cmp_cached_21) | (_cmp_cached_169))
            # 1h & 3h down move, 1d high
            & ((_cmp_cached_9) | (_cmp_cached_181) | (_cmp_cached_108))
            # 1h & 1d down move, 1d high
            & ((_cmp_cached_9) | (_cmp_cached_198) | (_cmp_cached_106))
            # 1h down move, 4h high
            & ((_cmp_cached_9) | (_cmp_cached_47))
            # 1h down move, 1d high, 15m downtrend
            & ((_cmp_cached_9) | (_cmp_cached_106) | (_cmp_cached_241))
            # 1h down move, 4h & 1d downtrend
            & ((_cmp_cached_9) | (_cmp_cached_219) | (_cmp_cached_102))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_15) | (_cmp_cached_25) | (_cmp_cached_169))
            # 1h & 4h down move, 1h still not low enough
            & ((_cmp_cached_15) | (_cmp_cached_25) | (_cmp_cached_188))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_15) | (_cmp_cached_16) | (_cmp_cached_124))
            # 1h & 1d down move, 1d still high
            & ((_cmp_cached_15) | (_cmp_cached_104) | (_cmp_cached_56))
            # 1h & 1d down move, 1d high
            & ((_cmp_cached_15) | (_cmp_cached_121) | (_cmp_cached_108))
            # 1h down move, 1h still high, 4h downtrend
            & ((_cmp_cached_15) | (_cmp_cached_110) | (_cmp_cached_103))
            # 1h down move, 1d high, 4h downtrend
            & ((_cmp_cached_15) | (_cmp_cached_94) | (_cmp_cached_69))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_15) | (_cmp_cached_39) | (_cmp_cached_52))
            # 1h down move, 1h still high, 4h downtrend
            & ((_cmp_cached_30) | (_cmp_cached_26) | (_cmp_cached_204))
            # 1h down move, 1h high
            & ((_cmp_cached_30) | (_cmp_cached_33))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_16) | (_cmp_cached_167))
            # 1h down move, 1h still high, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_59) | (_cmp_cached_52))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_32) | (_cmp_cached_24) | (_cmp_cached_17))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_32) | (_cmp_cached_77) | (_cmp_cached_70))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_32) | (_cmp_cached_108) | (_cmp_cached_111))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_32) | (_cmp_cached_41) | (_cmp_cached_52))
            # 1h & 4h down move, 15m high
            & ((_cmp_cached_32) | (_cmp_cached_181) | (_cmp_cached_180))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_32) | (_cmp_cached_99) | (_cmp_cached_37))
            # 1h down move, 15m still high, 1h high
            & ((_cmp_cached_32) | (_cmp_cached_155) | (_cmp_cached_115))
            # 1h down move, 1h still high, 4h high
            & ((_cmp_cached_32) | (_cmp_cached_28) | (_cmp_cached_64))
            # 1h down move, 4h & 1d downtrend
            & ((_cmp_cached_32) | (_cmp_cached_81) | (_cmp_cached_194))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_32) | (_cmp_cached_20) | (_cmp_cached_48))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_34) | (_cmp_cached_24) | (_cmp_cached_167))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_34) | (_cmp_cached_47) | (_cmp_cached_48))
            # 1h down move, 1h still high, 1d overbought
            & ((_cmp_cached_34) | (_cmp_cached_59) | (_cmp_cached_111))
            # 1h down move, 1h high, 4h downtrend
            & ((_cmp_cached_34) | (_cmp_cached_37) | (_cmp_cached_69))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_36) | (_cmp_cached_19) | (_cmp_cached_20))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_38) | (_cmp_cached_24) | (_cmp_cached_6))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_117) | (_cmp_cached_162) | (_cmp_cached_194))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_117) | (_cmp_cached_72) | (_cmp_cached_113))
            # 1h down move, 1h high & overbought
            & ((_cmp_cached_174) | (_cmp_cached_19) | (_cmp_cached_82))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_53) | (_cmp_cached_51) | (_cmp_cached_112))
            # 4h down move, 4h high, 4h downtrend
            & ((_cmp_cached_151) | (_cmp_cached_122) | (_cmp_cached_213))
            # 4h & 1d down move, 1h still not low enough
            & ((_cmp_cached_55) | (_cmp_cached_153) | (_cmp_cached_161))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_55) | (_cmp_cached_198) | (_cmp_cached_106))
            # 4h down move, 4h & 1d downtrend
            & ((_cmp_cached_55) | (_cmp_cached_219) | (_cmp_cached_57))
            # 4h & 1d down move, 1h still high
            & ((_cmp_cached_58) | (_cmp_cached_153) | (_cmp_cached_110))
            # 4h & 1d down move, 1h high
            & ((_cmp_cached_58) | (_cmp_cached_29) | (_cmp_cached_37))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_58) | (_cmp_cached_121) | (_cmp_cached_119))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_58) | (_cmp_cached_121) | (_cmp_cached_14))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_25) | (_cmp_cached_104) | (_cmp_cached_199))
            # 4h & 1d down move, 4h high
            & ((_cmp_cached_25) | (_cmp_cached_121) | (_cmp_cached_17))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_25) | (_cmp_cached_94) | (_cmp_cached_167))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_100) | (_cmp_cached_122) | (_cmp_cached_186))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_100) | (_cmp_cached_108) | (_cmp_cached_63))
            # 4h down move, 4h & 1d downtrend
            & ((_cmp_cached_100) | (_cmp_cached_69) | (_cmp_cached_102))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_41) | (_cmp_cached_122) | (_cmp_cached_65))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_181) | (_cmp_cached_39) | (_cmp_cached_111))
            # 4h down move, 4h high, 1d downtrend
            & ((_cmp_cached_91) | (_cmp_cached_17) | (_cmp_cached_102))
            # 4h down move, 4h high & overbought
            & ((_cmp_cached_71) | (_cmp_cached_17) | (_cmp_cached_50))
            # 4h down move, 4h & 1d overbought
            & ((_cmp_cached_71) | (_cmp_cached_20) | (_cmp_cached_167))
            # 1h still high, 4h & 1d downtrend
            & ((_cmp_cached_110) | (_cmp_cached_69) | (_cmp_cached_65))
            # 1h & 4h high, 1h overbought
            & ((_cmp_cached_24) | (_cmp_cached_6) | (_cmp_cached_242))
            # 1h high, 1d overbought
            & ((_cmp_cached_24) | (_cmp_cached_216))
            # 1h & 4h high, 1h overbought
            & ((_cmp_cached_33) | (_cmp_cached_46) | (_cmp_cached_158))
            # 1h & 1d high, 1h overbought
            & ((_cmp_cached_33) | (_cmp_cached_94) | (_cmp_cached_158))
            # 4h still not low enough, 4h & 1d downtrend
            & ((_cmp_cached_98) | (_cmp_cached_213) | (_cmp_cached_65))
            # 4h still high, 5m downtrend
            & ((_cmp_cached_96) | (_cmp_cached_203))
            # 4h high, 4h & 1d overbought
            & ((_cmp_cached_40) | (_cmp_cached_51) | (_cmp_cached_107))
            # 4h & 1d high, 4h overbought
            & ((_cmp_cached_77) | (_cmp_cached_27) | (_cmp_cached_86))
            # 4h high, 1h & 1d overbought
            & ((_cmp_cached_6) | (_cmp_cached_158) | (_cmp_cached_48))
            # 4h high, 1h & 4h high
            & ((_cmp_cached_6) | (_cmp_cached_183) | (_cmp_cached_196))
            # 1d high, 4h & 1d downtrend
            & ((_cmp_cached_106) | (_cmp_cached_213) | (_cmp_cached_65))
            # 1d high, 1h & 1d overbought
            & ((_cmp_cached_108) | (_cmp_cached_158) | (_cmp_cached_111))
            # 1d high, 4h & 1d overbought
            & ((_cmp_cached_94) | (_cmp_cached_20) | (_cmp_cached_107))
            # 1h high, 4h overbought
            & ((_cmp_cached_19) | (_cmp_cached_67))
            # 4h & 1d overbought
            & ((_cmp_cached_196) | (_cmp_cached_111))
            # big drop in the last 20 days, 1d high, 1d downtrend
            & (
              (df["close"] > (df["high_max_20_1d"] * 0.20))
              | (_cmp_cached_148)
              | (_cmp_cached_149)
            )
            # drop in last 20 days, 1h high, 1d downtrend
            & ((df["close"] > (df["high_max_20_1d"] * 0.20)) | (_cmp_cached_24) | (_cmp_cached_206))
          )

          # Logic
          long_entry_logic.append(
            (_cmp_cached_243)
            & (_cmp_cached_179)
            & (df["close"] < (df["EMA_9"] * 0.946))
            & (df["close"] < (df["EMA_20"] * 0.960))
          )

        # Condition #5 - Normal mode (Long).
        if long_entry_condition_index == 5:
          # Protections
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          long_entry_logic.append(df["protections_long_global"] == True)

          long_entry_logic.append(
            (_cmp_cached_87)
            # 5m & 1h down move, 1h still not low enough
            & ((_cmp_cached_0) | (_cmp_cached_9) | (_cmp_cached_150))
            # 5m & 1h down move, 1d high
            & ((_cmp_cached_0) | (_cmp_cached_30) | (_cmp_cached_27))
            # 5m & 1h down move, 1h still high
            & ((_cmp_cached_0) | (_cmp_cached_32) | (_cmp_cached_59))
            # 5m & 4h down move, 15m still high
            & ((_cmp_cached_0) | (_cmp_cached_151) | (_cmp_cached_155))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_32) | (_cmp_cached_162))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_88) | (_cmp_cached_11) | (_cmp_cached_59))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_88) | (_cmp_cached_11) | (_cmp_cached_12))
            # 15m & 1h down move, 4h overbought
            & ((_cmp_cached_88) | (_cmp_cached_32) | (_cmp_cached_217))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_88) | (_cmp_cached_36) | (_cmp_cached_33))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_88) | (_cmp_cached_117) | (_cmp_cached_45))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_88) | (_cmp_cached_174) | (_cmp_cached_19))
            # 15m down move, 15m stil not low enough, 4h high
            & ((_cmp_cached_88) | (_cmp_cached_10) | (_cmp_cached_40))
            # 15m down move, 15m high, 1h high
            & ((_cmp_cached_88) | (_cmp_cached_210) | (_cmp_cached_37))
            # 15m down move, 1h & 4h overbought
            & ((_cmp_cached_88) | (_cmp_cached_54) | (_cmp_cached_113))
            # 15m down move, 4h & 1d overbought
            & ((_cmp_cached_88) | (_cmp_cached_50) | (_cmp_cached_107))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_89) | (_cmp_cached_99) | (_cmp_cached_77))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_89) | (_cmp_cached_32) | (_cmp_cached_45))
            # 15m down move, 15m still high, 1d high
            & ((_cmp_cached_89) | (_cmp_cached_62) | (_cmp_cached_148))
            # 15m down move, 15m high, 4h high
            & ((_cmp_cached_89) | (_cmp_cached_210) | (_cmp_cached_64))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_89) | (_cmp_cached_45) | (_cmp_cached_6))
            # 15m down move, 4h & 1d high
            & ((_cmp_cached_89) | (_cmp_cached_77) | (_cmp_cached_27))
            # 15m down move, 4h high, 1h downtrend
            & ((_cmp_cached_244) | (_cmp_cached_47) | (_cmp_cached_239))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_89) | (_cmp_cached_6) | (_cmp_cached_211))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_184) | (_cmp_cached_21) | (_cmp_cached_12))
            # 15m down move, 15m high, 4h overbought
            & ((_cmp_cached_184) | (_cmp_cached_76) | (_cmp_cached_50))
            # 15m down move, 1h high, 4h overbought
            & ((_cmp_cached_184) | (_cmp_cached_45) | (_cmp_cached_67))
            # 15m down move, 4h high, 1h overbought
            & ((_cmp_cached_184) | (_cmp_cached_6) | (_cmp_cached_79))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_90) | (_cmp_cached_36) | (_cmp_cached_80))
            # 15m down move, 15m still high, 1h high
            & ((_cmp_cached_245) | (_cmp_cached_62) | (_cmp_cached_45))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_13) | (_cmp_cached_55) | (_cmp_cached_106))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_13) | (_cmp_cached_58) | (_cmp_cached_96))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_13) | (_cmp_cached_58) | (_cmp_cached_246))
            # 1h & 4h down move, 4h downtrend
            & ((_cmp_cached_13) | (_cmp_cached_25) | (_cmp_cached_213))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_13) | (_cmp_cached_16) | (_cmp_cached_42))
            # 1h & 1d down move, 1d high
            & ((_cmp_cached_13) | (_cmp_cached_121) | (_cmp_cached_108))
            # 1h & 4h down move, 1h downtrend
            & ((_cmp_cached_7) | (_cmp_cached_100) | (_cmp_cached_130))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_122))
            # 1h & 4h down move, 15m still high
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_61))
            # 1h & 4h down move, 1h downtrend
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_129))
            # 1h & 4h & 1d down move
            & ((_cmp_cached_9) | (_cmp_cached_25) | (_cmp_cached_29))
            # 1h & 4h down move, 15m high
            & ((_cmp_cached_9) | (_cmp_cached_25) | (_cmp_cached_92))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_9) | (_cmp_cached_25) | (_cmp_cached_40))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_9) | (_cmp_cached_41) | (_cmp_cached_48))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_9) | (_cmp_cached_91) | (_cmp_cached_165))
            # 1h down move, 4h downtrend. 4h still not low enough
            & ((_cmp_cached_9) | (_cmp_cached_69) | (_cmp_cached_98))
            # 1h down move, 15m still high, 4h high
            & ((_cmp_cached_9) | (_cmp_cached_31) | (_cmp_cached_72))
            # 1h down move, 15m high, 4h downtrend
            & ((_cmp_cached_9) | (_cmp_cached_76) | (_cmp_cached_93))
            # 1h down move, 1h still high, 15m downtrend
            & ((_cmp_cached_9) | (_cmp_cached_110) | (_cmp_cached_159))
            # 1h down move, 1d high, 4h overbought
            & ((_cmp_cached_9) | (_cmp_cached_27) | (_cmp_cached_20))
            # 1h down move, 1h still high, 1d downtrend
            & ((_cmp_cached_9) | (_cmp_cached_59) | (_cmp_cached_65))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_9) | (_cmp_cached_74) | (_cmp_cached_70))
            # 1h & 4h down move, 1h still high
            & ((_cmp_cached_15) | (_cmp_cached_25) | (_cmp_cached_26))
            # 1h & 4h down move, 1h still not low enough
            & ((_cmp_cached_15) | (_cmp_cached_25) | (_cmp_cached_161))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_15) | (_cmp_cached_100) | (_cmp_cached_65))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_15) | (_cmp_cached_99) | (_cmp_cached_6))
            # 1h & 1d down move, 4h high
            & ((_cmp_cached_15) | (_cmp_cached_29) | (_cmp_cached_12))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_15) | (_cmp_cached_40) | (_cmp_cached_107))
            # 1h down move, 4h high, 1d high
            & ((_cmp_cached_15) | (_cmp_cached_77) | (_cmp_cached_74))
            # 1h down move, 1d high, 1d downtrend
            & ((_cmp_cached_15) | (_cmp_cached_106) | (_cmp_cached_57))
            # 1h down move, 1d high, 4h overbought
            & ((_cmp_cached_15) | (_cmp_cached_27) | (_cmp_cached_83))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_15) | (_cmp_cached_27) | (_cmp_cached_95))
            # 1h down move, 1h downtrend, 1d overbought
            & ((_cmp_cached_15) | (_cmp_cached_109) | (_cmp_cached_63))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_15) | (_cmp_cached_50) | (_cmp_cached_112))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_30) | (_cmp_cached_100) | (_cmp_cached_17))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_30) | (_cmp_cached_181) | (_cmp_cached_77))
            # 1h & 1d down move, 1h still high
            & ((_cmp_cached_30) | (_cmp_cached_178) | (_cmp_cached_59))
            # 1h & 4h down move, 15m high
            & ((_cmp_cached_11) | (_cmp_cached_16) | (_cmp_cached_76))
            # 1h down move, 4h downtrend, 4h high
            & ((_cmp_cached_11) | (_cmp_cached_193) | (_cmp_cached_17))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_11) | (_cmp_cached_94) | (_cmp_cached_70))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_11) | (_cmp_cached_12) | (_cmp_cached_102))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_32) | (_cmp_cached_99) | (_cmp_cached_47))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_32) | (_cmp_cached_24) | (_cmp_cached_47))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_32) | (_cmp_cached_24) | (_cmp_cached_20))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_32) | (_cmp_cached_77) | (_cmp_cached_70))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_32) | (_cmp_cached_46) | (_cmp_cached_196))
            # 1h down move, 15m still high, 1h high
            & ((_cmp_cached_32) | (_cmp_cached_155) | (_cmp_cached_115))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_32) | (_cmp_cached_37) | (_cmp_cached_65))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_32) | (_cmp_cached_72) | (_cmp_cached_42))
            # 1h down move, 4h downtrend, 1d over
            & ((_cmp_cached_32) | (_cmp_cached_103) | (_cmp_cached_107))
            # 1h down move, 1h still high, 1d overbought
            & ((_cmp_cached_34) | (_cmp_cached_26) | (_cmp_cached_167))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_34) | (_cmp_cached_24) | (_cmp_cached_6))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_34) | (_cmp_cached_24) | (_cmp_cached_195))
            # 1h down move, 1h high, 4h downtrend
            & ((_cmp_cached_34) | (_cmp_cached_33) | (_cmp_cached_69))
            # 1h down move, 1h still high, 1d overbought
            & ((_cmp_cached_34) | (_cmp_cached_59) | (_cmp_cached_111))
            # 1h down move, 15m high, 1h high
            & ((_cmp_cached_36) | (_cmp_cached_210) | (_cmp_cached_24))
            # 1h down move, 1h still high, 1d overbought
            & ((_cmp_cached_36) | (_cmp_cached_110) | (_cmp_cached_48))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_36) | (_cmp_cached_33) | (_cmp_cached_6))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_36) | (_cmp_cached_108) | (_cmp_cached_107))
            # 1h down move, 1h & 4h overbought
            & ((_cmp_cached_36) | (_cmp_cached_79) | (_cmp_cached_20))
            # 1h down move, 1h overbought
            & ((_cmp_cached_36) | (_cmp_cached_158))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_38) | (_cmp_cached_197) | (_cmp_cached_111))
            # 1h down move, 15m still high, 1h high
            & ((_cmp_cached_38) | (_cmp_cached_62) | (_cmp_cached_45))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_38) | (_cmp_cached_33) | (_cmp_cached_86))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_38) | (_cmp_cached_37) | (_cmp_cached_107))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_117) | (_cmp_cached_78) | (_cmp_cached_102))
            # 1h down move, 4h high, 1h overbought
            & ((_cmp_cached_117) | (_cmp_cached_46) | (_cmp_cached_54))
            # 1h down move, 4h & 1d high
            & ((_cmp_cached_117) | (_cmp_cached_6) | (_cmp_cached_27))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_117) | (_cmp_cached_162) | (_cmp_cached_194))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_117) | (_cmp_cached_20) | (_cmp_cached_63))
            # 1h down move, 15m high, 1h high
            & ((_cmp_cached_174) | (_cmp_cached_210) | (_cmp_cached_19))
            # 1h down move, 1h high & overbought
            & ((_cmp_cached_174) | (_cmp_cached_123) | (_cmp_cached_95))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_53) | (_cmp_cached_50) | (_cmp_cached_52))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_53) | (_cmp_cached_77) | (_cmp_cached_52))
            # 4h & 1d down move, 4h downtrend
            & ((_cmp_cached_151) | (_cmp_cached_153) | (_cmp_cached_69))
            # 4h & 1d down move, 1h still not low enough
            & ((_cmp_cached_55) | (_cmp_cached_153) | (_cmp_cached_161))
            # 4h down move, 1d high, 4h downtrend
            & ((_cmp_cached_55) | (_cmp_cached_108) | (_cmp_cached_93))
            # 4h & 1d down move, 15m high
            & ((_cmp_cached_58) | (_cmp_cached_29) | (_cmp_cached_180))
            # 4h & 1d down move, 1d downtrend
            & ((_cmp_cached_58) | (_cmp_cached_29) | (_cmp_cached_149))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_58) | (_cmp_cached_121) | (_cmp_cached_14))
            # 4h down move, 15m downtrend, 1d high
            & ((_cmp_cached_58) | (_cmp_cached_159) | (_cmp_cached_108))
            # 4h down move, 15m still high, 1d downtrend
            & ((_cmp_cached_58) | (_cmp_cached_61) | (_cmp_cached_195))
            # 4h down move, 15m high
            & ((_cmp_cached_58) | (_cmp_cached_180))
            # 4h down move, 1h high, 1d downtrend
            & ((_cmp_cached_58) | (_cmp_cached_37) | (_cmp_cached_57))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_58) | (_cmp_cached_165) | (_cmp_cached_57))
            # 4h down move, 4h downtrend, 1d overbought
            & ((_cmp_cached_58) | (_cmp_cached_69) | (_cmp_cached_52))
            # 4h & 1d down move, 4h downtrend
            & ((_cmp_cached_25) | (_cmp_cached_104) | (_cmp_cached_213))
            # 4h down move, 1h high, 1d downtrend
            & ((_cmp_cached_25) | (_cmp_cached_78) | (_cmp_cached_186))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_25) | (_cmp_cached_35) | (_cmp_cached_57))
            # 4h down move, 1h & 4h downtrend
            & ((_cmp_cached_25) | (_cmp_cached_109) | (_cmp_cached_103))
            # 4h & 1ddown move, 1d high
            & ((_cmp_cached_100) | (_cmp_cached_104) | (_cmp_cached_108))
            # 4h down move, 1d high, 1d downtrend
            & ((_cmp_cached_100) | (_cmp_cached_108) | (_cmp_cached_102))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_100) | (_cmp_cached_108) | (_cmp_cached_216))
            # 4h down move, 4h still high. 4h downtrend
            & ((_cmp_cached_16) | (_cmp_cached_122) | (_cmp_cached_200))
            # 4h down move, 4h high, 1d downtrend
            & ((_cmp_cached_16) | (_cmp_cached_162) | (_cmp_cached_206))
            # 4h down move, 1h high, 4h downtrend
            & ((_cmp_cached_41) | (_cmp_cached_24) | (_cmp_cached_93))
            # 4h down move, 1h high, 1d downtrend
            & ((_cmp_cached_41) | (_cmp_cached_123) | (_cmp_cached_65))
            # 4h down move, 4h & 1d high
            & ((_cmp_cached_21) | (_cmp_cached_17) | (_cmp_cached_27))
            # 4h down move, 4h high & overbought
            & ((_cmp_cached_99) | (_cmp_cached_77) | (_cmp_cached_50))
            # 4h down move, 4h high, 1d overbought
            & ((_cmp_cached_99) | (_cmp_cached_77) | (_cmp_cached_52))
            # 4h down move, 4h & 1d overbought
            & ((_cmp_cached_99) | (_cmp_cached_50) | (_cmp_cached_52))
            # 1d down move, 1d high, 1d downtrend
            & ((_cmp_cached_153) | (_cmp_cached_106) | (_cmp_cached_186))
            # 1d down move, 1h high, 4h downtrend
            & ((_cmp_cached_178) | (_cmp_cached_49) | (_cmp_cached_103))
            # 15m & 1h & 4h downtrend
            & ((_cmp_cached_159) | (_cmp_cached_177) | (_cmp_cached_189))
            # 1d downtrend, 1d high & overbought
            & ((_cmp_cached_202) | (_cmp_cached_131) | (_cmp_cached_167))
            # 15m not low enough, 1h & 4h downtrend
            & ((_cmp_cached_166) | (_cmp_cached_109) | (_cmp_cached_204))
            # 15m high, 1h high & overbought
            & ((_cmp_cached_76) | (_cmp_cached_45) | (_cmp_cached_82))
            # 4h high, 4h & 1d overbought
            & ((_cmp_cached_17) | (_cmp_cached_83) | (_cmp_cached_63))
            # 1h & 4h high, 4h overbought
            & ((_cmp_cached_33) | (_cmp_cached_6) | (_cmp_cached_50))
            # 1h & 1d high, 1d overbought
            & ((_cmp_cached_33) | (_cmp_cached_108) | (_cmp_cached_111))
            # 1h high, 1h overbought
            & ((_cmp_cached_33) | (_cmp_cached_82))
            # 4h still high, 5m downtrend
            & ((_cmp_cached_96) | (_cmp_cached_203))
            # 4h & 1d high, 4h overbought
            & ((_cmp_cached_77) | (_cmp_cached_27) | (_cmp_cached_67))
            # 4h & 1d high, 1d overbought
            & ((_cmp_cached_77) | (_cmp_cached_27) | (_cmp_cached_63))
            # 4h high, 1h & 4h overbought
            & ((_cmp_cached_47) | (_cmp_cached_242) | (_cmp_cached_67))
            # 4h high, 4h & 1d overbought
            & ((_cmp_cached_47) | (_cmp_cached_50) | (_cmp_cached_52))
            # 4h & 1d high, 4h overbought
            & ((_cmp_cached_6) | (_cmp_cached_27) | (_cmp_cached_113))
            # 4h high, 1h & 1d overbought
            & ((_cmp_cached_6) | (_cmp_cached_54) | (_cmp_cached_48))
            # 4h high, 4h & 1d overbought
            & ((_cmp_cached_6) | (_cmp_cached_20) | (_cmp_cached_63))
            # 1d high, 1h & 4h down move
            & ((_cmp_cached_27) | (_cmp_cached_205) | (_cmp_cached_83))
            # 1d high, 1h downtrend, 1d overbought
            & ((_cmp_cached_27) | (_cmp_cached_109) | (_cmp_cached_48))
            # 1d high, 4h & 1d overbought
            & ((_cmp_cached_27) | (_cmp_cached_20) | (_cmp_cached_63))
            # 15m high, 4h & 1d downtrend
            & ((_cmp_cached_92) | (_cmp_cached_103) | (_cmp_cached_102))
            # 1h high, 4h & 1d overbought
            & ((_cmp_cached_49) | (_cmp_cached_20) | (_cmp_cached_48))
            # 4h high, 1h overbought, 1d downtrend
            & ((_cmp_cached_12) | (_cmp_cached_54) | (_cmp_cached_206))
            # 4h high, 4h & 1d overbought
            & ((_cmp_cached_12) | (_cmp_cached_67) | (_cmp_cached_48))
            # 4h high, 1h & 4h overbought
            & ((_cmp_cached_72) | (_cmp_cached_82) | (_cmp_cached_67))
            # 4h high, 1h & 4h overbought
            & ((_cmp_cached_72) | (_cmp_cached_79) | (_cmp_cached_86))
            # 1d high, 4h & 1d overbought
            & ((_cmp_cached_39) | (_cmp_cached_113) | (_cmp_cached_48))
            # 1d P&D, dh downtrend
            & ((_cmp_cached_228) | (df["change_pct_1d"].shift(288) < 50.0) | (_cmp_cached_25))
            # big drop in the last 20 days, 1d high, 1d downtrend
            & (
              (df["close"] > (df["high_max_20_1d"] * 0.20))
              | (_cmp_cached_148)
              | (_cmp_cached_149)
            )
            # drop in last 20 days, 1h high, 1d downtrend
            & ((df["close"] > (df["high_max_20_1d"] * 0.20)) | (_cmp_cached_24) | (_cmp_cached_206))
            # drop in last 20 days. 4h high
            & ((df["close"] > (df["high_max_20_1d"] * 0.10)) | (_cmp_cached_72))
          )

          # Logic
          long_entry_logic.append(
            (_cmp_cached_247)
            & (_cmp_cached_243)
            & (_cmp_cached_208)
            & (df["EMA_26"] > df["EMA_12"])
            & ((df["EMA_26"] - df["EMA_12"]) > (df["open"] * 0.020))
            & ((df["EMA_26"].shift() - df["EMA_12"].shift()) > (df["open"] / 100.0))
          )

        # Condition #6 - Normal mode (Long).
        if long_entry_condition_index == 6:
          # Protections
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          long_entry_logic.append(df["protections_long_global"] == True)

          long_entry_logic.append(
            # 5m & 15m down move, 15m still high
            ((_cmp_cached_0) | (_cmp_cached_5) | (_cmp_cached_155))
            # 5m & 15m down move, 15m still high
            & ((_cmp_cached_0) | (_cmp_cached_84) | (_cmp_cached_31))
            # 5m & 15m down move, 1d downtrend
            & ((_cmp_cached_0) | (_cmp_cached_84) | (_cmp_cached_57))
            # 5m & 15m down move, 1d downtrend
            & ((_cmp_cached_0) | (_cmp_cached_88) | (_cmp_cached_102))
            # 5m & 1h down move, 1h still not low enough
            & ((_cmp_cached_0) | (_cmp_cached_30) | (_cmp_cached_150))
            # 5m & 1h down move, 1h still high
            & ((_cmp_cached_0) | (_cmp_cached_32) | (_cmp_cached_59))
            # 5m & 4h down move, 4h still high
            & ((_cmp_cached_0) | (_cmp_cached_25) | (_cmp_cached_35))
            # 5m & 4h & 1d down move
            & ((_cmp_cached_0) | (_cmp_cached_100) | (_cmp_cached_192))
            # 5m & 4h down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_41) | (_cmp_cached_64))
            # 5m & 4h down move, 4h still high
            & ((_cmp_cached_0) | (_cmp_cached_175) | (_cmp_cached_122))
            # 5m & 1d down move, 15m still high
            & ((_cmp_cached_0) | (_cmp_cached_104) | (_cmp_cached_155))
            # 5m down move, 4h & 1d overbought
            & ((_cmp_cached_0) | (_cmp_cached_20) | (_cmp_cached_52))
            # 5m & 1h down move, 4h high
            & ((_cmp_cached_8) | (_cmp_cached_36) | (_cmp_cached_40))
            # 5m & 1h down move, 1h high
            & ((_cmp_cached_8) | (_cmp_cached_53) | (_cmp_cached_33))
            # 5m & 4h down move, 1d downtrend
            & ((_cmp_cached_8) | (_cmp_cached_55) | (_cmp_cached_57))
            # 5m & 4h down move, 4h still high
            & ((_cmp_cached_8) | (_cmp_cached_25) | (_cmp_cached_96))
            # 5m & 4h down move, 15m still high
            & ((_cmp_cached_8) | (_cmp_cached_16) | (_cmp_cached_61))
            # 5m & 4h down move, 1d overbought
            & ((_cmp_cached_8) | (_cmp_cached_41) | (_cmp_cached_112))
            # 5m & 4h down move, 4h high
            & ((_cmp_cached_8) | (_cmp_cached_71) | (_cmp_cached_77))
            # 5m down move, 15m still not low enough, 4h high
            & ((_cmp_cached_8) | (_cmp_cached_166) | (_cmp_cached_64))
            # 5m down move, 1h & 1d high
            & ((_cmp_cached_8) | (_cmp_cached_24) | (_cmp_cached_27))
            # 5m down move, 4h high & overbought
            & ((_cmp_cached_8) | (_cmp_cached_6) | (_cmp_cached_211))
            # 5m down move, 1h high
            & ((_cmp_cached_8) | (_cmp_cached_19))
            # 5m & 1d down move, 1d still high
            & ((_cmp_cached_157) | (_cmp_cached_29) | (_cmp_cached_56))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_1) | (_cmp_cached_30) | (_cmp_cached_26))
            # 15m & 1h down move, 4h still not low enough
            & ((_cmp_cached_1) | (_cmp_cached_30) | (_cmp_cached_120))
            # 15m & 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_11) | (_cmp_cached_169) | (_cmp_cached_186))
            # 15m & 1h down move, 1h still not low enough
            & ((_cmp_cached_1) | (_cmp_cached_11) | (_cmp_cached_188))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_1) | (_cmp_cached_11) | (_cmp_cached_165))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_1) | (_cmp_cached_36) | (_cmp_cached_17))
            # 15m & 4h down move, 1h still not low enough
            & ((_cmp_cached_1) | (_cmp_cached_58) | (_cmp_cached_161))
            # 15m & 4h down move, 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_25) | (_cmp_cached_186))
            # 15m & 4h down move, 4h still not low enough
            & ((_cmp_cached_1) | (_cmp_cached_100) | (_cmp_cached_120))
            # 15m & 4h down move, 15m still not low enough
            & ((_cmp_cached_1) | (_cmp_cached_41) | (_cmp_cached_179))
            # 15m & 4h down move, 1h still high
            & ((_cmp_cached_1) | (_cmp_cached_41) | (_cmp_cached_28))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_1) | (_cmp_cached_91) | (_cmp_cached_123))
            # 15m & 1d down move, 15m still not low enough
            & ((_cmp_cached_1) | (_cmp_cached_153) | (_cmp_cached_10))
            # 15m & 1d down move, 4h high
            & ((_cmp_cached_1) | (_cmp_cached_223) | (_cmp_cached_64))
            # 1h & 1d downtrend, 1d high
            & ((_cmp_cached_1) | (_cmp_cached_106) | (_cmp_cached_95))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_11) | (_cmp_cached_115))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_3) | (_cmp_cached_11) | (_cmp_cached_28))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_3) | (_cmp_cached_11) | (_cmp_cached_124))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_32) | (_cmp_cached_46))
            # 15m & 1h & 4h down move, 15m downtrend
            & (
              (_cmp_cached_3) | (_cmp_cached_36) | (_cmp_cached_99) | (_cmp_cached_159)
            )
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_3) | (_cmp_cached_36) | (_cmp_cached_59))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_174) | (_cmp_cached_6))
            # 15m & 4h down move, 15m still not low enough
            & ((_cmp_cached_3) | (_cmp_cached_100) | (_cmp_cached_10))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_21) | (_cmp_cached_162))
            # 15m down move, 15m still high, 1h still high
            & ((_cmp_cached_3) | (_cmp_cached_10) | (_cmp_cached_59))
            # 15m down move, 1h still high, 1d high
            & ((_cmp_cached_3) | (_cmp_cached_28) | (_cmp_cached_106))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_3) | (_cmp_cached_24) | (_cmp_cached_46))
            # 15m down move, 15m & 1h still not low enough
            & (
              (_cmp_cached_3) | (_cmp_cached_152) | (_cmp_cached_161)
            )
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_5) | (_cmp_cached_30) | (_cmp_cached_59))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_5) | (_cmp_cached_30) | (_cmp_cached_96))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_30) | (_cmp_cached_162))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_5) | (_cmp_cached_11) | (_cmp_cached_122))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_32) | (_cmp_cached_64))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_32) | (_cmp_cached_162))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_32) | (_cmp_cached_70))
            # 15m & 1h down move, 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_32) | (_cmp_cached_65))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_5) | (_cmp_cached_34) | (_cmp_cached_28))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_5) | (_cmp_cached_38) | (_cmp_cached_28))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_38) | (_cmp_cached_248))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_117) | (_cmp_cached_12))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_5) | (_cmp_cached_174) | (_cmp_cached_123))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_5) | (_cmp_cached_221) | (_cmp_cached_33))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_58) | (_cmp_cached_108))
            # 15m & 4h down move, 4h still not low enough
            & ((_cmp_cached_5) | (_cmp_cached_58) | (_cmp_cached_124))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_58) | (_cmp_cached_148))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_25) | (_cmp_cached_191))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_5) | (_cmp_cached_100) | (_cmp_cached_96))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_100) | (_cmp_cached_94))
            # 15m & 4h down move, 1h still high
            & ((_cmp_cached_5) | (_cmp_cached_100) | (_cmp_cached_59))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_5) | (_cmp_cached_100) | (_cmp_cached_165))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_100) | (_cmp_cached_39))
            # 15m & 4h down move, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_100) | (_cmp_cached_167))
            # 15m & 4h down move, 4h downtrend
            & ((_cmp_cached_5) | (_cmp_cached_16) | (_cmp_cached_189))
            # 15m & 4h down move, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_16) | (_cmp_cached_70))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_5) | (_cmp_cached_41) | (_cmp_cached_122))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_91) | (_cmp_cached_17))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_99) | (_cmp_cached_172))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_71) | (_cmp_cached_12))
            # 15m & 1d down move, 1h still high
            & ((_cmp_cached_5) | (_cmp_cached_153) | (_cmp_cached_28))
            # 15m & 1d down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_104) | (_cmp_cached_214))
            # 15m & 1d down move, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_73) | (_cmp_cached_167))
            # 15m down move, 15m downtrend, 4h still high
            & ((_cmp_cached_5) | (_cmp_cached_43) | (_cmp_cached_35))
            # 15m down move, 1h downtrend, 4h still high
            & ((_cmp_cached_5) | (_cmp_cached_177) | (_cmp_cached_165))
            # 15m down move, 15m still not low enough, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_10) | (_cmp_cached_40))
            # 15m down move, 15m still high, 1h still high
            & ((_cmp_cached_5) | (_cmp_cached_31) | (_cmp_cached_59))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_5) | (_cmp_cached_46) | (_cmp_cached_20))
            # 15m down move, 1h still not low enough, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_161) | (_cmp_cached_48))
            # 15m down move, 1h still high, 4h downtrend
            & ((_cmp_cached_5) | (_cmp_cached_59) | (_cmp_cached_69))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_5) | (_cmp_cached_64) | (_cmp_cached_50))
            # 15m down move, 4h high, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_64) | (_cmp_cached_95))
            # 15m & 1h & 4h down move
            & ((_cmp_cached_84) | (_cmp_cached_15) | (_cmp_cached_15))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_84) | (_cmp_cached_15) | (_cmp_cached_110))
            # 15m & 1h down move, 1h downtrend
            & ((_cmp_cached_84) | (_cmp_cached_30) | (_cmp_cached_177))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_84) | (_cmp_cached_11) | (_cmp_cached_26))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_84) | (_cmp_cached_11) | (_cmp_cached_17))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_84) | (_cmp_cached_11) | (_cmp_cached_28))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_84) | (_cmp_cached_11) | (_cmp_cached_48))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_84) | (_cmp_cached_32) | (_cmp_cached_74))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_84) | (_cmp_cached_117) | (_cmp_cached_6))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_84) | (_cmp_cached_174) | (_cmp_cached_78))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_84) | (_cmp_cached_100) | (_cmp_cached_94))
            # 15m & 4h down move, 15m still high
            & ((_cmp_cached_84) | (_cmp_cached_100) | (_cmp_cached_61))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_84) | (_cmp_cached_41) | (_cmp_cached_123))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_84) | (_cmp_cached_21) | (_cmp_cached_40))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_84) | (_cmp_cached_21) | (_cmp_cached_64))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_84) | (_cmp_cached_181) | (_cmp_cached_77))
            # 15m & 4h down move, 1d overbought
            & ((_cmp_cached_84) | (_cmp_cached_181) | (_cmp_cached_52))
            # 15m & 4h down move, 1d overbought
            & ((_cmp_cached_84) | (_cmp_cached_91) | (_cmp_cached_63))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_84) | (_cmp_cached_175) | (_cmp_cached_64))
            # 15m & 1d down move, 1h still high
            & ((_cmp_cached_84) | (_cmp_cached_29) | (_cmp_cached_161))
            # 15m & 1d down move, 1h still high
            & ((_cmp_cached_84) | (_cmp_cached_104) | (_cmp_cached_59))
            # 15m & 1d down move, 1d overbought
            & ((_cmp_cached_84) | (_cmp_cached_178) | (_cmp_cached_95))
            # 15m down move, 15m still not low enough, 1h high
            & ((_cmp_cached_84) | (_cmp_cached_179) | (_cmp_cached_19))
            # 15m down move, 15m still high, 4h high
            & ((_cmp_cached_84) | (_cmp_cached_31) | (_cmp_cached_17))
            # 15m down move, 1h still high, 1d overbought
            & ((_cmp_cached_84) | (_cmp_cached_26) | (_cmp_cached_63))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_84) | (_cmp_cached_115) | (_cmp_cached_46))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_84) | (_cmp_cached_33) | (_cmp_cached_47))
            # 15m down move, 1h & 1d high
            & ((_cmp_cached_84) | (_cmp_cached_24) | (_cmp_cached_106))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_84) | (_cmp_cached_45) | (_cmp_cached_72))
            # 15m down move, 4h high, 4h downtrend
            & ((_cmp_cached_84) | (_cmp_cached_40) | (_cmp_cached_69))
            # 15m down move, 4h & 1d high
            & ((_cmp_cached_84) | (_cmp_cached_17) | (_cmp_cached_27))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_84) | (_cmp_cached_17) | (_cmp_cached_51))
            # 15m down move, 4h high, 1h overbought
            & ((_cmp_cached_84) | (_cmp_cached_46) | (_cmp_cached_205))
            # 15m down move, 4h high, 1h overbought
            & ((_cmp_cached_84) | (_cmp_cached_6) | (_cmp_cached_82))
            # 15m down move, 1h still high, 4h overbought
            & ((_cmp_cached_84) | (_cmp_cached_59) | (_cmp_cached_50))
            # 15m down move, 1h high, 4h downtrend
            & ((_cmp_cached_84) | (_cmp_cached_19) | (_cmp_cached_69))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_84) | (_cmp_cached_72) | (_cmp_cached_20))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_87) | (_cmp_cached_30) | (_cmp_cached_190))
            # 15m & 1h down move, 1d downtrend
            & ((_cmp_cached_87) | (_cmp_cached_32) | (_cmp_cached_102))
            # 15m & 1h down move, 1h overbought
            & ((_cmp_cached_87) | (_cmp_cached_117) | (_cmp_cached_82))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_87) | (_cmp_cached_11) | (_cmp_cached_12))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_87) | (_cmp_cached_34) | (_cmp_cached_27))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_87) | (_cmp_cached_38) | (_cmp_cached_24))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_87) | (_cmp_cached_53) | (_cmp_cached_78))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_87) | (_cmp_cached_53) | (_cmp_cached_72))
            # 15m & 4h & 1d down move
            & ((_cmp_cached_87) | (_cmp_cached_100) | (_cmp_cached_104))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_87) | (_cmp_cached_100) | (_cmp_cached_39))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_87) | (_cmp_cached_91) | (_cmp_cached_39))
            # 15m & 1d down move, 1h high
            & ((_cmp_cached_87) | (_cmp_cached_104) | (_cmp_cached_24))
            # 15m & 1d down move, 15m still high
            & ((_cmp_cached_87) | (_cmp_cached_178) | (_cmp_cached_61))
            # 15m down move, 15m still not low enough, 1h high
            & ((_cmp_cached_87) | (_cmp_cached_179) | (_cmp_cached_49))
            # 15m down move, 15m still high, 1h high
            & ((_cmp_cached_87) | (_cmp_cached_31) | (_cmp_cached_24))
            # 15m down move, 15m still high, 4h high
            & ((_cmp_cached_87) | (_cmp_cached_31) | (_cmp_cached_17))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_87) | (_cmp_cached_33) | (_cmp_cached_77))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_87) | (_cmp_cached_33) | (_cmp_cached_95))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_87) | (_cmp_cached_17) | (_cmp_cached_51))
            # 15m down move, 4h high, 1h overbought
            & ((_cmp_cached_87) | (_cmp_cached_6) | (_cmp_cached_158))
            # 15m down move, 1d high, 4h downtrend
            & ((_cmp_cached_87) | (_cmp_cached_94) | (_cmp_cached_69))
            # 15m down move, 1d high, 4h overbought
            & ((_cmp_cached_87) | (_cmp_cached_27) | (_cmp_cached_20))
            # 15m down move, 1d high, 1d overbought
            & ((_cmp_cached_87) | (_cmp_cached_27) | (_cmp_cached_167))
            # 15m down move, 15m high, 4h downtrend
            & ((_cmp_cached_87) | (_cmp_cached_222) | (_cmp_cached_204))
            # 15 down move, 1h high, 1d overbought
            & ((_cmp_cached_87) | (_cmp_cached_37) | (_cmp_cached_95))
            # 15m down move, 4h high, 15m downtrend
            & ((_cmp_cached_87) | (_cmp_cached_64) | (_cmp_cached_43))
            # 15m & 1h down move, 15m high
            & ((_cmp_cached_88) | (_cmp_cached_11) | (_cmp_cached_92))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_88) | (_cmp_cached_34) | (_cmp_cached_59))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_88) | (_cmp_cached_36) | (_cmp_cached_39))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_88) | (_cmp_cached_36) | (_cmp_cached_63))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_88) | (_cmp_cached_117) | (_cmp_cached_45))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_88) | (_cmp_cached_53) | (_cmp_cached_6))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_88) | (_cmp_cached_53) | (_cmp_cached_72))
            # 15m & 4h down move, 4h overbought
            & ((_cmp_cached_88) | (_cmp_cached_175) | (_cmp_cached_51))
            # 15m & 1d down move, 1h high
            & ((_cmp_cached_88) | (_cmp_cached_121) | (_cmp_cached_33))
            # 15m down move, 15m still not low enough, 1h high
            & ((_cmp_cached_88) | (_cmp_cached_179) | (_cmp_cached_49))
            # 15m down move, 15m still high, 1h high
            & ((_cmp_cached_88) | (_cmp_cached_31) | (_cmp_cached_19))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_88) | (_cmp_cached_115) | (_cmp_cached_112))
            # 15m down move, 1h high, 4h overbought
            & ((_cmp_cached_88) | (_cmp_cached_24) | (_cmp_cached_113))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_88) | (_cmp_cached_45) | (_cmp_cached_6))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_88) | (_cmp_cached_78) | (_cmp_cached_46))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_88) | (_cmp_cached_17) | (_cmp_cached_86))
            # 15m down move, 4h high, 1d overbought
            & ((_cmp_cached_88) | (_cmp_cached_77) | (_cmp_cached_48))
            # 15m down move, 1h high, 1d downtrend
            & ((_cmp_cached_88) | (_cmp_cached_37) | (_cmp_cached_57))
            # 15m down move, 1h high & overbought
            & ((_cmp_cached_88) | (_cmp_cached_49) | (_cmp_cached_79))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_88) | (_cmp_cached_72) | (_cmp_cached_51))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_89) | (_cmp_cached_34) | (_cmp_cached_33))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_89) | (_cmp_cached_174) | (_cmp_cached_19))
            # 15m & 4h down move, 15m high
            & ((_cmp_cached_89) | (_cmp_cached_41) | (_cmp_cached_92))
            # 15m down move, 1h high & overbought
            & ((_cmp_cached_89) | (_cmp_cached_78) | (_cmp_cached_82))
            # 15m down move, 15m still high, 4h high
            & ((_cmp_cached_184) | (_cmp_cached_31) | (_cmp_cached_47))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_89) | (_cmp_cached_6) | (_cmp_cached_113))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_89) | (_cmp_cached_72) | (_cmp_cached_113))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_184) | (_cmp_cached_36) | (_cmp_cached_37))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_184) | (_cmp_cached_221) | (_cmp_cached_33))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_184) | (_cmp_cached_21) | (_cmp_cached_12))
            # 15m down move, 15m still not low enough, 1h high
            & ((_cmp_cached_184) | (_cmp_cached_179) | (_cmp_cached_33))
            # 15m down move, 15m still not low enough, 1h high
            & ((_cmp_cached_184) | (_cmp_cached_179) | (_cmp_cached_19))
            # 15m down move, 1m still high, 4h overbought
            & ((_cmp_cached_184) | (_cmp_cached_31) | (_cmp_cached_86))
            # 15m down move, 1h high, 4h overbought
            & ((_cmp_cached_184) | (_cmp_cached_33) | (_cmp_cached_50))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_184) | (_cmp_cached_6) | (_cmp_cached_217))
            # 15m down move, 1h high & overbought
            & ((_cmp_cached_184) | (_cmp_cached_49) | (_cmp_cached_54))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_90) | (_cmp_cached_36) | (_cmp_cached_6))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_90) | (_cmp_cached_91) | (_cmp_cached_49))
            # 15m down move, 15m still high, 1d high
            & ((_cmp_cached_90) | (_cmp_cached_155) | (_cmp_cached_48))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_90) | (_cmp_cached_6) | (_cmp_cached_113))
            # 15m down move, 1h high, 4h overbought
            & ((_cmp_cached_249) | (_cmp_cached_19) | (_cmp_cached_113))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_13) | (_cmp_cached_25) | (_cmp_cached_148))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_7) | (_cmp_cached_55) | (_cmp_cached_165))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_7) | (_cmp_cached_41) | (_cmp_cached_17))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_122))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_9) | (_cmp_cached_25) | (_cmp_cached_17))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_9) | (_cmp_cached_25) | (_cmp_cached_65))
            # 1h & 4h down move, 1h still high
            & ((_cmp_cached_9) | (_cmp_cached_41) | (_cmp_cached_26))
            # 1h & 4h down move, 15m still not low enough
            & ((_cmp_cached_9) | (_cmp_cached_181) | (_cmp_cached_152))
            # 1h down move, 1d high, 1d downtrend
            & ((_cmp_cached_9) | (_cmp_cached_106) | (_cmp_cached_57))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_9) | (_cmp_cached_35) | (_cmp_cached_65))
            # 1h & 4h down move, 15m high
            & ((_cmp_cached_15) | (_cmp_cached_25) | (_cmp_cached_92))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_15) | (_cmp_cached_100) | (_cmp_cached_124))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_15) | (_cmp_cached_100) | (_cmp_cached_102))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_15) | (_cmp_cached_21) | (_cmp_cached_24))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_15) | (_cmp_cached_21) | (_cmp_cached_35))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_15) | (_cmp_cached_108) | (_cmp_cached_95))
            # 1h down move, 1d high, 4h downtrend
            & ((_cmp_cached_15) | (_cmp_cached_94) | (_cmp_cached_69))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_30) | (_cmp_cached_21) | (_cmp_cached_64))
            # 1h & 1d down move, 1d high
            & ((_cmp_cached_30) | (_cmp_cached_73) | (_cmp_cached_60))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_30) | (_cmp_cached_115) | (_cmp_cached_107))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_30) | (_cmp_cached_24) | (_cmp_cached_167))
            # 1h down move, 1d high, 4h downtrend
            & ((_cmp_cached_30) | (_cmp_cached_74) | (_cmp_cached_69))
            # 1h down move, 4h downtrend, 1d overbought
            & ((_cmp_cached_30) | (_cmp_cached_93) | (_cmp_cached_167))
            # 1h & 4h down move, 1h still high
            & ((_cmp_cached_11) | (_cmp_cached_58) | (_cmp_cached_28))
            # 1h & 4h down move, 15m high
            & ((_cmp_cached_11) | (_cmp_cached_41) | (_cmp_cached_92))
            # 1h down move, 4h downtrend, 4h high
            & ((_cmp_cached_11) | (_cmp_cached_193) | (_cmp_cached_17))
            # 1h down move, 1h still high, 1d high
            & ((_cmp_cached_11) | (_cmp_cached_110) | (_cmp_cached_94))
            # 1h down move, 1h still high, 4h overbought
            & ((_cmp_cached_11) | (_cmp_cached_26) | (_cmp_cached_83))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_96) | (_cmp_cached_48))
            # 1h down move, 1d still high, 1d downtrend
            & ((_cmp_cached_11) | (_cmp_cached_14) | (_cmp_cached_57))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_32) | (_cmp_cached_21) | (_cmp_cached_250))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_32) | (_cmp_cached_181) | (_cmp_cached_40))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_32) | (_cmp_cached_71) | (_cmp_cached_12))
            # 1h & 1d down move, 1h high
            & ((_cmp_cached_32) | (_cmp_cached_178) | (_cmp_cached_115))
            # 1h down move, 4h & 1d down move
            & ((_cmp_cached_32) | (_cmp_cached_17) | (_cmp_cached_27))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_32) | (_cmp_cached_47) | (_cmp_cached_67))
            # 1h down move, 1d still high, 1d downtrend
            & ((_cmp_cached_32) | (_cmp_cached_119) | (_cmp_cached_57))
            # 1h down move, 1d high, 4h downtrend
            & ((_cmp_cached_32) | (_cmp_cached_27) | (_cmp_cached_103))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_32) | (_cmp_cached_39) | (_cmp_cached_167))
            # 1h down move, 4h & 1d downtrend
            & ((_cmp_cached_32) | (_cmp_cached_81) | (_cmp_cached_194))
            # 1h & 1d down move, 1h high
            & ((_cmp_cached_34) | (_cmp_cached_192) | (_cmp_cached_68))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_34) | (_cmp_cached_115) | (_cmp_cached_17))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_34) | (_cmp_cached_17) | (_cmp_cached_102))
            # 1h down move, 1d high, 4h overbought
            & ((_cmp_cached_34) | (_cmp_cached_94) | (_cmp_cached_113))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_34) | (_cmp_cached_50) | (_cmp_cached_107))
            # 1h & 1d down move, 1d high
            & ((_cmp_cached_34) | (_cmp_cached_198) | (_cmp_cached_94))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_36) | (_cmp_cached_99) | (_cmp_cached_123))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_36) | (_cmp_cached_115) | (_cmp_cached_52))
            # 1h down move, 1h still high, 1d high
            & ((_cmp_cached_36) | (_cmp_cached_26) | (_cmp_cached_131))
            # 1h down move, 1h still high, 1d overbought
            & ((_cmp_cached_36) | (_cmp_cached_26) | (_cmp_cached_167))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_36) | (_cmp_cached_24) | (_cmp_cached_51))
            # 1h down move, 1h high, 15m downtrend
            & ((_cmp_cached_36) | (_cmp_cached_33) | (_cmp_cached_116))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_36) | (_cmp_cached_108) | (_cmp_cached_107))
            # 1h down move, 1d high, 4h overbought
            & ((_cmp_cached_36) | (_cmp_cached_39) | (_cmp_cached_20))
            # 1h down move, 1h overbought
            & ((_cmp_cached_36) | (_cmp_cached_158))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_38) | (_cmp_cached_197) | (_cmp_cached_111))
            # 1h down move, 1h still not low enough, 1d downtrend
            & ((_cmp_cached_38) | (_cmp_cached_150) | (_cmp_cached_195))
            # 1h down move, 1h still high, 1d overbought
            & ((_cmp_cached_38) | (_cmp_cached_28) | (_cmp_cached_48))
            # 1h down move, 4h high, 1h overbought
            & ((_cmp_cached_117) | (_cmp_cached_47) | (_cmp_cached_79))
            # 1h down move, 1d high, 4h overbought
            & ((_cmp_cached_117) | (_cmp_cached_94) | (_cmp_cached_20))
            # 1h down move, 1h high & overbought
            & ((_cmp_cached_117) | (_cmp_cached_19) | (_cmp_cached_82))
            # 1h down move, 1h & 4h overbought
            & ((_cmp_cached_117) | (_cmp_cached_82) | (_cmp_cached_196))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_117) | (_cmp_cached_20) | (_cmp_cached_167))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_174) | (_cmp_cached_175) | (_cmp_cached_37))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_174) | (_cmp_cached_33) | (_cmp_cached_50))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_174) | (_cmp_cached_6) | (_cmp_cached_50))
            # 1h & 1d down move, 1h high
            & ((_cmp_cached_53) | (_cmp_cached_126) | (_cmp_cached_24))
            # 1h down move, 4 high, 1h overbought
            & ((_cmp_cached_53) | (_cmp_cached_6) | (_cmp_cached_82))
            # 1h down move, 1d high, 1h overbought
            & ((_cmp_cached_53) | (_cmp_cached_94) | (_cmp_cached_82))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_53) | (_cmp_cached_37) | (_cmp_cached_186))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_53) | (_cmp_cached_19) | (_cmp_cached_48))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_221) | (_cmp_cached_24) | (_cmp_cached_211))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_221) | (_cmp_cached_49) | (_cmp_cached_167))
            # 4h down move, 1h still not low enough, 4h downtrend
            & ((_cmp_cached_151) | (_cmp_cached_188) | (_cmp_cached_93))
            # 4h down move, 4h & 1d downtrend
            & ((_cmp_cached_151) | (_cmp_cached_93) | (_cmp_cached_186))
            # 4h & 1d down move, 15m still high
            & ((_cmp_cached_55) | (_cmp_cached_121) | (_cmp_cached_155))
            # 4h & 1d down move, 1h still not low enough
            & ((_cmp_cached_58) | (_cmp_cached_153) | (_cmp_cached_190))
            # 4h & 1d down move, 1d downtrend
            & ((_cmp_cached_58) | (_cmp_cached_29) | (_cmp_cached_65))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_58) | (_cmp_cached_104) | (_cmp_cached_14))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_58) | (_cmp_cached_192) | (_cmp_cached_27))
            # 4h & 1d down move, 1d overbought
            & ((_cmp_cached_58) | (_cmp_cached_198) | (_cmp_cached_95))
            # 4h down move, 15m high
            & ((_cmp_cached_58) | (_cmp_cached_92))
            # 4h & 1d down move, 4h high
            & ((_cmp_cached_25) | (_cmp_cached_121) | (_cmp_cached_17))
            # 4h & 1d down move, 1h still high
            & ((_cmp_cached_25) | (_cmp_cached_178) | (_cmp_cached_28))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_25) | (_cmp_cached_121) | (_cmp_cached_106))
            # 4h & 1d down move, 1d downtrend
            & ((_cmp_cached_25) | (_cmp_cached_121) | (_cmp_cached_149))
            # 4h & 1d down move, 4h still high
            & ((_cmp_cached_25) | (_cmp_cached_73) | (_cmp_cached_165))
            # 4h down move, 1d still high, 4h still not low enough
            & ((_cmp_cached_25) | (_cmp_cached_176) | (_cmp_cached_124))
            # 4h down move, 4h still not low enough, 1d downtrend
            & ((_cmp_cached_25) | (_cmp_cached_156) | (_cmp_cached_57))
            # 4h down move, 1h & 4h downtrend
            & ((_cmp_cached_25) | (_cmp_cached_109) | (_cmp_cached_103))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_100) | (_cmp_cached_104) | (_cmp_cached_199))
            # 4h & 1d down move, 4h still high
            & ((_cmp_cached_100) | (_cmp_cached_104) | (_cmp_cached_165))
            # 4h & 1d down move, 1d overbought
            & ((_cmp_cached_100) | (_cmp_cached_198) | (_cmp_cached_52))
            # 4h down move, 15m high
            & ((_cmp_cached_100) | (_cmp_cached_180))
            # 4h down move, 1h high, 4h downtrend
            & ((_cmp_cached_100) | (_cmp_cached_37) | (_cmp_cached_69))
            # 4h down move, 4h still high, 4h downtrend
            & ((_cmp_cached_16) | (_cmp_cached_122) | (_cmp_cached_200))
            # 4h down move, 4h high, 1d downtrend
            & ((_cmp_cached_16) | (_cmp_cached_64) | (_cmp_cached_102))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_41) | (_cmp_cached_73) | (_cmp_cached_94))
            # 4h down move, 1h high, 1h downtrend
            & ((_cmp_cached_41) | (_cmp_cached_24) | (_cmp_cached_132))
            # 4h down move, 1h high, 4h downtrend
            & ((_cmp_cached_41) | (_cmp_cached_24) | (_cmp_cached_93))
            # 4h down move, 1h still high, 1d overbought
            & ((_cmp_cached_41) | (_cmp_cached_28) | (_cmp_cached_70))
            # 4h & 1d down move, 1d overbought
            & ((_cmp_cached_21) | (_cmp_cached_73) | (_cmp_cached_48))
            # 4h down move, 4h & 1d high
            & ((_cmp_cached_21) | (_cmp_cached_77) | (_cmp_cached_27))
            # 4h down move, 4h high, 1d downtrend
            & ((_cmp_cached_91) | (_cmp_cached_17) | (_cmp_cached_102))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_181) | (_cmp_cached_126) | (_cmp_cached_27))
            # 4h down move, 4h high, 1d downtrend
            & ((_cmp_cached_181) | (_cmp_cached_64) | (_cmp_cached_194))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_91) | (_cmp_cached_106) | (_cmp_cached_167))
            # 4h down move, 4h high & overbought
            & ((_cmp_cached_91) | (_cmp_cached_162) | (_cmp_cached_20))
            # 4h down move, 4h high, 1d overbought
            & ((_cmp_cached_91) | (_cmp_cached_12) | (_cmp_cached_95))
            # 4h down move, 4h high & overbought
            & ((_cmp_cached_99) | (_cmp_cached_77) | (_cmp_cached_50))
            # 4h down move, 1h high, 1d downtrend
            & ((_cmp_cached_99) | (_cmp_cached_19) | (_cmp_cached_102))
            # 4h down move, 4h high & overbought
            & ((_cmp_cached_175) | (_cmp_cached_17) | (_cmp_cached_20))
            # 4h down move, 4h high, 1d overbought
            & ((_cmp_cached_175) | (_cmp_cached_17) | (_cmp_cached_48))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_175) | (_cmp_cached_94) | (_cmp_cached_112))
            # 4h down move, 4h & 1d high
            & ((_cmp_cached_71) | (_cmp_cached_17) | (_cmp_cached_106))
            # 4h down move, 1d high, 4h overbought
            & ((_cmp_cached_71) | (_cmp_cached_27) | (_cmp_cached_50))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_71) | (_cmp_cached_27) | (_cmp_cached_111))
            # 4h down move, 4h still high, 4h overbought
            & ((_cmp_cached_71) | (_cmp_cached_35) | (_cmp_cached_50))
            # 4h down move, 4h high, 1d overbought
            & ((_cmp_cached_197) | (_cmp_cached_172) | (_cmp_cached_70))
            # 4h down move, 4h high & overbought
            & ((_cmp_cached_197) | (_cmp_cached_77) | (_cmp_cached_20))
            # 1d down move, 1d still not low enough, 1d downtrend
            & ((_cmp_cached_101) | (_cmp_cached_251) | (_cmp_cached_57))
            # 1d down move, 15m still high
            & ((_cmp_cached_101) | (_cmp_cached_155))
            # 1d down move, 1h high
            & ((_cmp_cached_153) | (_cmp_cached_24))
            # 1d down move, 4h downtrend, 4h high
            & ((_cmp_cached_104) | (_cmp_cached_252) | (_cmp_cached_17))
            # 1d down move, 1d still high, 1d downtrend
            & ((_cmp_cached_121) | (_cmp_cached_14) | (_cmp_cached_57))
            # 1d down move, 4h & 1d high
            & ((_cmp_cached_125) | (_cmp_cached_17) | (_cmp_cached_27))
            # 1d down move, 1d high & overbought
            & ((_cmp_cached_125) | (_cmp_cached_108) | (_cmp_cached_95))
            # 1d down move, 1h high, 1d overbought
            & ((_cmp_cached_126) | (_cmp_cached_24) | (_cmp_cached_48))
            # 4h downtrend, 4h high & over
            & ((_cmp_cached_253) | (_cmp_cached_6) | (_cmp_cached_51))
            # 15m still high, 4h high, 1h overbought
            & ((_cmp_cached_31) | (_cmp_cached_47) | (_cmp_cached_79))
            # 15m still high, 4h high, 1h overbought
            & ((_cmp_cached_31) | (_cmp_cached_6) | (_cmp_cached_79))
            # 4h down move, 1h still high, 1d downtrend
            & ((_cmp_cached_25) | (_cmp_cached_110) | (_cmp_cached_42))
            # 1h high, 4h high & overbought
            & ((_cmp_cached_33) | (_cmp_cached_77) | (_cmp_cached_51))
            # 1h & 4h high, 1h overbought
            & ((_cmp_cached_33) | (_cmp_cached_46) | (_cmp_cached_158))
            # 1h & 4h & 1d high
            & ((_cmp_cached_33) | (_cmp_cached_6) | (_cmp_cached_27))
            # 1h & 4h high, 1d overbought
            & ((_cmp_cached_33) | (_cmp_cached_6) | (_cmp_cached_70))
            # 1h high, 1h overbought
            & ((_cmp_cached_33) | (_cmp_cached_82))
            # 1h & 1d high, 4h overbought
            & ((_cmp_cached_33) | (_cmp_cached_27) | (_cmp_cached_50))
            # 1h high, 1h & 4h overbought
            & ((_cmp_cached_33) | (_cmp_cached_82) | (_cmp_cached_50))
            # 1h high, 1h overbought, 1d downtrend
            & ((_cmp_cached_33) | (_cmp_cached_183) | (_cmp_cached_42))
            # 1h high, 4h &1d overbought
            & ((_cmp_cached_45) | (_cmp_cached_51) | (_cmp_cached_70))
            # 1h high, 4h & 1d overbought
            & ((_cmp_cached_78) | (_cmp_cached_50) | (_cmp_cached_246))
            # 4h & 1d high, 4h overbought
            & ((_cmp_cached_17) | (_cmp_cached_27) | (_cmp_cached_86))
            # 4h & 1d high, 1d overbought
            & ((_cmp_cached_17) | (_cmp_cached_27) | (_cmp_cached_167))
            # 4h & 1d high, 4h overbought
            & ((_cmp_cached_46) | (_cmp_cached_27) | (_cmp_cached_51))
            # 4h high, 4h overbought, 1d downtrend
            & ((_cmp_cached_46) | (_cmp_cached_20) | (_cmp_cached_65))
            # 1d high, 4h & 1d overbought
            & ((_cmp_cached_106) | (_cmp_cached_51) | (_cmp_cached_111))
            # 1d high, 1h & 1d overbought
            & ((_cmp_cached_108) | (_cmp_cached_79) | (_cmp_cached_107))
            # 1d high, 1d downtrend
            & ((_cmp_cached_108) | (_cmp_cached_102))
            # 1d high, 1h & 4h downtrend
            & ((_cmp_cached_131) | (_cmp_cached_109) | (_cmp_cached_204))
            # 1d high, 1h & 1d overbought
            & ((_cmp_cached_94) | (_cmp_cached_82) | (_cmp_cached_107))
            # 1d high, 4h & 1d overbought
            & ((_cmp_cached_27) | (_cmp_cached_50) | (_cmp_cached_167))
            # 15m still not low enough, 4h high, 1d overbought
            & ((_cmp_cached_152) | (_cmp_cached_6) | (_cmp_cached_70))
            # 15m still high, 4h high & overbought
            & (
              (_cmp_cached_155) | (_cmp_cached_12) | (_cmp_cached_51)
            )
            # 1h high, 1d overbought
            & ((_cmp_cached_37) | (_cmp_cached_52))
            # 1h high, 1h overbought, 4h downtrend
            & ((_cmp_cached_19) | (_cmp_cached_82) | (_cmp_cached_93))
            # 1h high, 4h & 1d downtrend
            & ((_cmp_cached_19) | (_cmp_cached_69) | (_cmp_cached_218))
            # 1h down move, 1h & 1d overbought
            & ((_cmp_cached_49) | (_cmp_cached_82) | (_cmp_cached_107))
            # 1h high & overbought
            & ((_cmp_cached_49) | (_cmp_cached_54))
            # 4h high, 1h & 4h overbought
            & ((_cmp_cached_64) | (_cmp_cached_82) | (_cmp_cached_20))
            # 4h high, 1h & 1d overbought
            & ((_cmp_cached_64) | (_cmp_cached_79) | (_cmp_cached_111))
            # 4h high, 4h & 1d overbought
            & ((_cmp_cached_12) | (_cmp_cached_51) | (_cmp_cached_70))
            # 4h high, 1d downtrend
            & ((_cmp_cached_12) | (_cmp_cached_42))
            # 4h high, 1h & 1d overbought
            & ((_cmp_cached_72) | (_cmp_cached_79) | (_cmp_cached_167))
            # 4h high, 4h & 1d overbought
            & ((_cmp_cached_72) | (_cmp_cached_50) | (_cmp_cached_95))
            # 1d hihg, 1h & 1d overbought
            & ((_cmp_cached_39) | (_cmp_cached_158) | (_cmp_cached_48))
            # 1d P&D, dh downtrend
            & ((_cmp_cached_228) | (df["change_pct_1d"].shift(288) < 50.0) | (_cmp_cached_25))
            # big drop in the last 20 days, 1d high, 1d downtrend
            & (
              (df["close"] > (df["high_max_20_1d"] * 0.20))
              | (_cmp_cached_148)
              | (_cmp_cached_149)
            )
            # drop in last 20 days, 1h high, 1d downtrend
            & ((df["close"] > (df["high_max_20_1d"] * 0.20)) | (_cmp_cached_24) | (_cmp_cached_206))
            # drop in last 20 days. 4h high
            & ((df["close"] > (df["high_max_20_1d"] * 0.10)) | (_cmp_cached_72))
          )

          # Logic
          long_entry_logic.append(
            (df["RSI_20"] < df["RSI_20"].shift(1))
            & (_cmp_cached_254)
            & (_cmp_cached_243)
            & (_cmp_cached_237)
            & (_cmp_cached_62)
            & (df["close"] < df["SMA_16"] * 0.960)
          )

        # Condition #21 - Pump mode (Long).
        if long_entry_condition_index == 21:
          # Protections
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          # long_entry_logic.append(df["protections_long_global"] == True)

          long_entry_logic.append(
            # 5m down move, 4h high, 1h overbought
            ((_cmp_cached_157) | (_cmp_cached_6) | (_cmp_cached_158))
            # 15m down move, 1h & 4h overbought
            & ((_cmp_cached_3) | (_cmp_cached_205) | (_cmp_cached_86))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_30) | (_cmp_cached_63))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_5) | (_cmp_cached_34) | (_cmp_cached_33))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_5) | (_cmp_cached_34) | (_cmp_cached_19))
            # 15m & 1h down move, 4h overbought
            & ((_cmp_cached_5) | (_cmp_cached_38) | (_cmp_cached_86))
            # 15m & 1h down move, 4h overbought
            & ((_cmp_cached_5) | (_cmp_cached_53) | (_cmp_cached_217))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_175) | (_cmp_cached_46))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_5) | (_cmp_cached_6) | (_cmp_cached_67))
            # 15m down move, 1h high, 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_37) | (_cmp_cached_42))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_5) | (_cmp_cached_12) | (_cmp_cached_51))
            # 15m down move, 1d high, 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_148) | (_cmp_cached_149))
            # 15m & 1h down move, 4h overbought
            & ((_cmp_cached_84) | (_cmp_cached_34) | (_cmp_cached_196))
            # 15m & 1d down move, 1h high
            & ((_cmp_cached_84) | (_cmp_cached_192) | (_cmp_cached_78))
            # 15m down move, 15m still high, 4h high
            & ((_cmp_cached_84) | (_cmp_cached_31) | (_cmp_cached_6))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_84) | (_cmp_cached_110) | (_cmp_cached_6))
            # 15m down move, 1h high, 4h overbought
            & ((_cmp_cached_84) | (_cmp_cached_115) | (_cmp_cached_67))
            # 15m down move, 4h high, 4h downtrend
            & ((_cmp_cached_84) | (_cmp_cached_46) | (_cmp_cached_252))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_84) | (_cmp_cached_158) | (_cmp_cached_86))
            # 15m down move, 4h & 1d overbought
            & ((_cmp_cached_84) | (_cmp_cached_83) | (_cmp_cached_63))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_87) | (_cmp_cached_115) | (_cmp_cached_6))
            # 15m down move, 4h high, 1h overbought
            & ((_cmp_cached_87) | (_cmp_cached_12) | (_cmp_cached_82))
            # 15m down move, 4h & 1d overbought
            & ((_cmp_cached_87) | (_cmp_cached_67) | (_cmp_cached_111))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_88) | (_cmp_cached_11) | (_cmp_cached_63))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_88) | (_cmp_cached_174) | (_cmp_cached_78))
            # 15m down move, 15m still high, 1d downtrend
            & ((_cmp_cached_88) | (_cmp_cached_31) | (_cmp_cached_195))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_88) | (_cmp_cached_78) | (_cmp_cached_6))
            # 15m down move, 4h high, 1h overbought
            & ((_cmp_cached_88) | (_cmp_cached_6) | (_cmp_cached_79))
            # 15m down move, 4h high, 1d overbought
            & ((_cmp_cached_88) | (_cmp_cached_6) | (_cmp_cached_48))
            # 15m down move, 1h high & overbought
            & ((_cmp_cached_88) | (_cmp_cached_49) | (_cmp_cached_79))
            # 15m down move, 1h & 4h overbought
            & ((_cmp_cached_88) | (_cmp_cached_54) | (_cmp_cached_113))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_89) | (_cmp_cached_72) | (_cmp_cached_255))
            # 15m down move, 1h & 4h overbought
            & ((_cmp_cached_89) | (_cmp_cached_256) | (_cmp_cached_67))
            # 15m down move, 4h & 1d overbought
            & ((_cmp_cached_90) | (_cmp_cached_196) | (_cmp_cached_48))
            # 1h down move, 4h overbought, 1d downtrend
            & ((_cmp_cached_15) | (_cmp_cached_86) | (_cmp_cached_102))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_30) | (_cmp_cached_86) | (_cmp_cached_77))
            # 1h & 4h down move, 1h still high
            & ((_cmp_cached_30) | (_cmp_cached_86) | (_cmp_cached_28))
            # 1h & 4h down move, 4h overbought
            & ((_cmp_cached_30) | (_cmp_cached_86) | (_cmp_cached_50))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_30) | (_cmp_cached_33) | (_cmp_cached_6))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_30) | (_cmp_cached_77) | (_cmp_cached_50))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_30) | (_cmp_cached_6) | (_cmp_cached_86))
            # 1h down move, 1h still high, 1d overbought
            & ((_cmp_cached_30) | (_cmp_cached_28) | (_cmp_cached_50))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_30) | (_cmp_cached_113) | (_cmp_cached_48))
            # 1h down move, 1d high, 4h overbought
            & ((_cmp_cached_11) | (_cmp_cached_27) | (_cmp_cached_83))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_32) | (_cmp_cached_77) | (_cmp_cached_51))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_34) | (_cmp_cached_33) | (_cmp_cached_65))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_34) | (_cmp_cached_12) | (_cmp_cached_42))
            # 1h down move, 1h & 1d overbought
            & ((_cmp_cached_36) | (_cmp_cached_158) | (_cmp_cached_112))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_38) | (_cmp_cached_33) | (_cmp_cached_211))
            # 1h down move, 4h high, 1h overbought
            & ((_cmp_cached_38) | (_cmp_cached_46) | (_cmp_cached_79))
            # 1h down move, 4h high, 1h overbought
            & ((_cmp_cached_38) | (_cmp_cached_6) | (_cmp_cached_82))
            # 1h down move, 1d high, 1d downtrend
            & ((_cmp_cached_38) | (_cmp_cached_27) | (_cmp_cached_195))
            # 1h down move, 1h high & overbought
            & ((_cmp_cached_117) | (_cmp_cached_78) | (_cmp_cached_82))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_117) | (_cmp_cached_37) | (_cmp_cached_57))
            # 1h down move, 1h & 1d overbought
            & ((_cmp_cached_117) | (_cmp_cached_205) | (_cmp_cached_111))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_174) | (_cmp_cached_24) | (_cmp_cached_113))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_174) | (_cmp_cached_47) | (_cmp_cached_67))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_53) | (_cmp_cached_77) | (_cmp_cached_196))
            # 1h down move, 1h & 1d overbought
            & ((_cmp_cached_53) | (_cmp_cached_82) | (_cmp_cached_257))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_221) | (_cmp_cached_33) | (_cmp_cached_51))
            # 1h down move, 1h overbought
            & ((_cmp_cached_221) | (_cmp_cached_54))
            # 4h down move, 1h high & overbought
            & ((_cmp_cached_151) | (_cmp_cached_45) | (_cmp_cached_256))
            # 1d down move, 4h high & overbought
            & ((_cmp_cached_101) | (_cmp_cached_46) | (_cmp_cached_86))
            # 1d down move, 1h high
            & ((_cmp_cached_153) | (_cmp_cached_24))
            # 1d down move, 4h high, 1h overbought
            & ((_cmp_cached_104) | (_cmp_cached_6) | (_cmp_cached_205))
            # 1d down move, 4h high, 4h overbought
            & ((_cmp_cached_104) | (_cmp_cached_6) | (_cmp_cached_113))
            # 1d down move, 1h & 4h overbought
            & ((_cmp_cached_178) | (_cmp_cached_158) | (_cmp_cached_83))
            # 1d down move, 4h high & overbought
            & ((_cmp_cached_192) | (_cmp_cached_6) | (_cmp_cached_20))
            # 1d down move, 1h & 4h high
            & ((_cmp_cached_125) | (_cmp_cached_33) | (_cmp_cached_6))
            # 1d down move, 4h & 1d high
            & ((_cmp_cached_125) | (_cmp_cached_17) | (_cmp_cached_27))
            # 1d down move, 4h high & overbought
            & ((_cmp_cached_198) | (_cmp_cached_77) | (_cmp_cached_51))
            # 1d down move, 1h high, 1d overbought
            & ((_cmp_cached_126) | (_cmp_cached_68) | (_cmp_cached_167))
            # 1d down move, 1h & 4h high
            & ((_cmp_cached_258) | (_cmp_cached_78) | (_cmp_cached_6))
            # 1d downtrend, 1d high & overbought
            & ((_cmp_cached_202) | (_cmp_cached_131) | (_cmp_cached_167))
            # 15m not low enough, 1h high, 1d overbought
            & ((_cmp_cached_179) | (_cmp_cached_49) | (_cmp_cached_111))
            # 1h still high, 1h & 4h overbought
            & ((_cmp_cached_26) | (_cmp_cached_54) | (_cmp_cached_113))
            # 1h & 4h high, 4h overbought
            & ((_cmp_cached_24) | (_cmp_cached_6) | (_cmp_cached_20))
            # 1h & 4h high, 4h overbought
            & ((_cmp_cached_33) | (_cmp_cached_77) | (_cmp_cached_51))
            # 1h & 4h high, 1h overbought
            & ((_cmp_cached_33) | (_cmp_cached_46) | (_cmp_cached_158))
            # 1h & 4h high, 1d overbought
            & ((_cmp_cached_33) | (_cmp_cached_46) | (_cmp_cached_48))
            # 1h & 1d high, 4h overbought
            & ((_cmp_cached_78) | (_cmp_cached_94) | (_cmp_cached_51))
            # 1h & 4h high, 1h overbought
            & ((_cmp_cached_33) | (_cmp_cached_72) | (_cmp_cached_82))
            # 1h high & overbought
            & ((_cmp_cached_33) | (_cmp_cached_242))
            # 1h high, 1h & 4h overbought
            & ((_cmp_cached_33) | (_cmp_cached_82) | (_cmp_cached_50))
            # 1h high, 4h overbought, 1d downtrend
            & ((_cmp_cached_33) | (_cmp_cached_50) | (_cmp_cached_42))
            # 1h & 4h high, 15m downtrend
            & ((_cmp_cached_45) | (_cmp_cached_47) | (_cmp_cached_259))
            # 1h & 4h high, 1h overbought
            & ((_cmp_cached_78) | (_cmp_cached_46) | (_cmp_cached_82))
            # 4h high, 1h overbought, 1d downtrend
            & ((_cmp_cached_77) | (_cmp_cached_158) | (_cmp_cached_102))
            # 4h & 1d high, 4h downtrend
            & ((_cmp_cached_47) | (_cmp_cached_27) | (_cmp_cached_189))
            # 4h & 1d high, 1h overbought
            & ((_cmp_cached_47) | (_cmp_cached_94) | (_cmp_cached_79))
            # 4h & 1d high, 4h overbought
            & ((_cmp_cached_47) | (_cmp_cached_94) | (_cmp_cached_83))
            # 4h high, 1h & 4h overbought
            & ((_cmp_cached_47) | (_cmp_cached_82) | (_cmp_cached_20))
            # 4h high, 1d high & overbought
            & ((_cmp_cached_46) | (_cmp_cached_27) | (_cmp_cached_70))
            # 4h high, 1h & 4h overbought
            & ((_cmp_cached_46) | (_cmp_cached_54) | (_cmp_cached_113))
            # 4h high, 4h & 1d overbought
            & ((_cmp_cached_46) | (_cmp_cached_51) | (_cmp_cached_48))
            # 4h high, 1h & 4h overbought
            & ((_cmp_cached_6) | (_cmp_cached_54) | (_cmp_cached_67))
            # 1d high, 1h & 4h overbought
            & ((_cmp_cached_27) | (_cmp_cached_82) | (_cmp_cached_20))
            # 1h high, 1h & 4h overbought
            & ((_cmp_cached_123) | (_cmp_cached_54) | (_cmp_cached_113))
            # 1h high, 1h overbought
            & ((_cmp_cached_19) | (_cmp_cached_82))
            # 1h high, 4h overbought. 1d downtrend
            & ((_cmp_cached_19) | (_cmp_cached_113) | (_cmp_cached_154))
            # 4h high, 1h & 4h overbought
            & ((_cmp_cached_72) | (_cmp_cached_82) | (_cmp_cached_20))
            # 4h high & 4h & 1d overbought
            & ((_cmp_cached_72) | (_cmp_cached_20) | (_cmp_cached_167))
            # 1d high, 1h & 4h overbought
            & ((_cmp_cached_74) | (_cmp_cached_82) | (_cmp_cached_20))
            # 1d hihg, 1h & 1d overbought
            & ((_cmp_cached_39) | (_cmp_cached_158) | (_cmp_cached_48))
            # 1d high, 4h & 1d overbought
            & ((_cmp_cached_39) | (_cmp_cached_113) | (_cmp_cached_48))
          )

          # Logic
          long_entry_logic.append(
            (_cmp_cached_243)
            & (_cmp_cached_237)
            & (_cmp_cached_62)
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
            ((_cmp_cached_209) | (_cmp_cached_178) | (_cmp_cached_96))
            # 15m & 1h down move, 1d still high
            & ((_cmp_cached_1) | (_cmp_cached_13) | (_cmp_cached_14))
            # 15m & 1h down move, 1h still not low enough
            & ((_cmp_cached_1) | (_cmp_cached_7) | (_cmp_cached_161))
            # 15m & 1h down move, 15m downtrend
            & ((_cmp_cached_1) | (_cmp_cached_9) | (_cmp_cached_43))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_1) | (_cmp_cached_9) | (_cmp_cached_77))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_1) | (_cmp_cached_9) | (_cmp_cached_28))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_1) | (_cmp_cached_9) | (_cmp_cached_162))
            # 15m & 1h down move, 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_15) | (_cmp_cached_57))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_1) | (_cmp_cached_30) | (_cmp_cached_26))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_1) | (_cmp_cached_11) | (_cmp_cached_115))
            # 15m & 1h down move, 1d still high
            & ((_cmp_cached_1) | (_cmp_cached_32) | (_cmp_cached_238))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_1) | (_cmp_cached_32) | (_cmp_cached_37))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_1) | (_cmp_cached_32) | (_cmp_cached_59))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_1) | (_cmp_cached_32) | (_cmp_cached_39))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_1) | (_cmp_cached_38) | (_cmp_cached_45))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_1) | (_cmp_cached_38) | (_cmp_cached_260))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_1) | (_cmp_cached_55) | (_cmp_cached_77))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_1) | (_cmp_cached_181) | (_cmp_cached_35))
            # 15m down move, 15m still high, 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_62) | (_cmp_cached_57))
            # 15m down move, 1h still high, 1d high
            & ((_cmp_cached_1) | (_cmp_cached_26) | (_cmp_cached_106))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_1) | (_cmp_cached_33) | (_cmp_cached_77))
            # 15m down move, 4h & 1d high
            & ((_cmp_cached_1) | (_cmp_cached_77) | (_cmp_cached_27))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_1) | (_cmp_cached_19) | (_cmp_cached_12))
            # 15m down move, 1h high, 4h overbought
            & ((_cmp_cached_1) | (_cmp_cached_49) | (_cmp_cached_50))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_1) | (_cmp_cached_12) | (_cmp_cached_50))
            # 15m down move, 4h & 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_69) | (_cmp_cached_57))
            # 15m & 1h down move, 1d downtrend
            & ((_cmp_cached_3) | (_cmp_cached_7) | (_cmp_cached_186))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_3) | (_cmp_cached_9) | (_cmp_cached_108))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_9) | (_cmp_cached_12))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_32) | (_cmp_cached_24))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_32) | (_cmp_cached_17))
            # 15m & 4h down move, 1h still high
            & ((_cmp_cached_3) | (_cmp_cached_55) | (_cmp_cached_59))
            # 15m & 4h down move, 1d downtrend
            & ((_cmp_cached_3) | (_cmp_cached_58) | (_cmp_cached_57))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_100) | (_cmp_cached_19))
            # 15m & 4h down move, 1d downtrend
            & ((_cmp_cached_3) | (_cmp_cached_16) | (_cmp_cached_206))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_3) | (_cmp_cached_80) | (_cmp_cached_6))
            # 15m down move, 1h still high, 1d downtrend
            & ((_cmp_cached_3) | (_cmp_cached_59) | (_cmp_cached_65))
            # 5m down move, 4h high, 1d downtrend
            & ((_cmp_cached_3) | (_cmp_cached_12) | (_cmp_cached_65))
            # 15m down move, 1h & 4h overbought
            & ((_cmp_cached_3) | (_cmp_cached_205) | (_cmp_cached_211))
            # 15m down move, 4h & 1d overbought
            & ((_cmp_cached_3) | (_cmp_cached_51) | (_cmp_cached_48))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_5) | (_cmp_cached_9) | (_cmp_cached_24))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_9) | (_cmp_cached_148))
            # 15m & 1h down move, 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_9) | (_cmp_cached_102))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_5) | (_cmp_cached_15) | (_cmp_cached_33))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_15) | (_cmp_cached_6))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_15) | (_cmp_cached_64))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_5) | (_cmp_cached_30) | (_cmp_cached_59))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_11) | (_cmp_cached_167))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_32) | (_cmp_cached_70))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_5) | (_cmp_cached_36) | (_cmp_cached_78))
            # 15m & 1d down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_121) | (_cmp_cached_6))
            # 15m & 1d down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_121) | (_cmp_cached_12))
            # 15m down move, 15m still high, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_62) | (_cmp_cached_70))
            # 15m down move, 15m high
            & ((_cmp_cached_5) | (_cmp_cached_76))
            # 15m down move, 1h high, 15m downtrend
            & ((_cmp_cached_5) | (_cmp_cached_33) | (_cmp_cached_261))
            # 15m down move, 1h high, 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_33) | (_cmp_cached_102))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_45) | (_cmp_cached_52))
            # 15m down move, 1h & 1d high
            & ((_cmp_cached_5) | (_cmp_cached_78) | (_cmp_cached_27))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_5) | (_cmp_cached_80) | (_cmp_cached_6))
            # 15m down move, 4h high, 1h downtrend
            & ((_cmp_cached_5) | (_cmp_cached_47) | (_cmp_cached_135))
            # 15m down move, 4h & 1d high
            & ((_cmp_cached_5) | (_cmp_cached_46) | (_cmp_cached_27))
            # 15m down move, 4h high, 15m downtrend
            & ((_cmp_cached_5) | (_cmp_cached_262) | (_cmp_cached_187))
            # 15m down move, 1h high & overbought
            & ((_cmp_cached_5) | (_cmp_cached_27) | (_cmp_cached_112))
            # 15m down move, 1d high, 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_131) | (_cmp_cached_202))
            # 15m down move, 1h high, 15m downtrend
            & ((_cmp_cached_5) | (_cmp_cached_19) | (_cmp_cached_261))
            # 15m down move, 1h high, 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_49) | (_cmp_cached_102))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_49) | (_cmp_cached_70))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_5) | (_cmp_cached_72) | (_cmp_cached_20))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_84) | (_cmp_cached_15) | (_cmp_cached_70))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_84) | (_cmp_cached_30) | (_cmp_cached_94))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_84) | (_cmp_cached_34) | (_cmp_cached_33))
            # 15m & 1d down move, 4h high
            & ((_cmp_cached_84) | (_cmp_cached_104) | (_cmp_cached_72))
            # 15m & 1d down move, 4h high
            & ((_cmp_cached_84) | (_cmp_cached_121) | (_cmp_cached_6))
            # 15m & 1d down move, 1d high
            & ((_cmp_cached_84) | (_cmp_cached_73) | (_cmp_cached_108))
            # 15m down move, 15m still high, 1h high
            & ((_cmp_cached_84) | (_cmp_cached_62) | (_cmp_cached_78))
            # 15m down move, 15m still high, 1h high
            & ((_cmp_cached_84) | (_cmp_cached_62) | (_cmp_cached_19))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_84) | (_cmp_cached_33) | (_cmp_cached_6))
            # 15m down move, 4h high, 4h downtrend
            & ((_cmp_cached_84) | (_cmp_cached_40) | (_cmp_cached_69))
            # 15m down move, 4h & 1d high
            & ((_cmp_cached_84) | (_cmp_cached_77) | (_cmp_cached_27))
            # 15m down move, 1h high, 4h downtrend
            & ((_cmp_cached_84) | (_cmp_cached_37) | (_cmp_cached_103))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_84) | (_cmp_cached_12) | (_cmp_cached_50))
            # 15m down move, 4h high, 1d downtrend
            & ((_cmp_cached_84) | (_cmp_cached_12) | (_cmp_cached_42))
            # 15m down move, 1d high, 4h overbought
            & ((_cmp_cached_84) | (_cmp_cached_39) | (_cmp_cached_113))
            # 15m down move, 1h downtrend, 4h overbought
            & ((_cmp_cached_84) | (_cmp_cached_129) | (_cmp_cached_67))
            # 15m down move, 4h & 1d downtrend
            & ((_cmp_cached_84) | (_cmp_cached_93) | (_cmp_cached_65))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_87) | (_cmp_cached_30) | (_cmp_cached_24))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_87) | (_cmp_cached_30) | (_cmp_cached_107))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_87) | (_cmp_cached_11) | (_cmp_cached_27))
            # 15m &4h down move, 4h still high
            & ((_cmp_cached_87) | (_cmp_cached_100) | (_cmp_cached_122))
            # 15m & 4h down move, 1d overbought
            & ((_cmp_cached_87) | (_cmp_cached_41) | (_cmp_cached_107))
            # 15m down move, 15m high, 1d overbought
            & ((_cmp_cached_87) | (_cmp_cached_76) | (_cmp_cached_52))
            # 15m down move, 1h high, 4h downtrend
            & ((_cmp_cached_87) | (_cmp_cached_33) | (_cmp_cached_219))
            # 15m down move, 1h high & overbought
            & ((_cmp_cached_87) | (_cmp_cached_80) | (_cmp_cached_183))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_87) | (_cmp_cached_17) | (_cmp_cached_20))
            # 15m down move, 4h high, 1d overbought
            & ((_cmp_cached_87) | (_cmp_cached_77) | (_cmp_cached_112))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_88) | (_cmp_cached_16) | (_cmp_cached_162))
            # 15m & 1d down move, 1h high
            & ((_cmp_cached_88) | (_cmp_cached_121) | (_cmp_cached_78))
            # 15m down move, 15m high, 1h high
            & ((_cmp_cached_89) | (_cmp_cached_210) | (_cmp_cached_78))
            # 15m down move, 15m high, 4h downtrend
            & ((_cmp_cached_88) | (_cmp_cached_210) | (_cmp_cached_69))
            # 15m down move, 1h high, 4h overbought
            & ((_cmp_cached_88) | (_cmp_cached_78) | (_cmp_cached_51))
            # 15m down move, 1h high, 4h overbought
            & ((_cmp_cached_88) | (_cmp_cached_80) | (_cmp_cached_263))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_88) | (_cmp_cached_80) | (_cmp_cached_167))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_88) | (_cmp_cached_6) | (_cmp_cached_50))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_89) | (_cmp_cached_78) | (_cmp_cached_46))
            # 1h & 4h down move, 1d still high
            & ((_cmp_cached_13) | (_cmp_cached_151) | (_cmp_cached_14))
            # 1h & 4h down move, 1h still high
            & ((_cmp_cached_13) | (_cmp_cached_16) | (_cmp_cached_110))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_13) | (_cmp_cached_91) | (_cmp_cached_64))
            # 1h down move, 15m & 1h downtrend
            & ((_cmp_cached_13) | (_cmp_cached_159) | (_cmp_cached_177))
            # 1h down move, 1h still high, 1h downtrend
            & ((_cmp_cached_13) | (_cmp_cached_26) | (_cmp_cached_129))
            # 1h down move, 1h high
            & ((_cmp_cached_13) | (_cmp_cached_24))
            # 1h down move, 4h high
            & ((_cmp_cached_13) | (_cmp_cached_17))
            # 1h down move, 1d high
            & ((_cmp_cached_13) | (_cmp_cached_106))
            # 1h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_13) | (_cmp_cached_35) | (_cmp_cached_129))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_13) | (_cmp_cached_60) | (_cmp_cached_167))
            # 1h & 4h & 1d down move
            & ((_cmp_cached_7) | (_cmp_cached_58) | (_cmp_cached_104))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_7) | (_cmp_cached_58) | (_cmp_cached_48))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_7) | (_cmp_cached_25) | (_cmp_cached_120))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_7) | (_cmp_cached_41) | (_cmp_cached_169))
            # 1h & 4h down move, 1h downtrend
            & ((_cmp_cached_7) | (_cmp_cached_41) | (_cmp_cached_177))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_7) | (_cmp_cached_99) | (_cmp_cached_17))
            # 1h & 1d down move, 1h still high
            & ((_cmp_cached_7) | (_cmp_cached_153) | (_cmp_cached_59))
            # 1h down move, 1d high, 1h downtrend
            & ((_cmp_cached_7) | (_cmp_cached_131) | (_cmp_cached_264))
            # 1h down move, 1d high, 4h downtrend
            & ((_cmp_cached_7) | (_cmp_cached_94) | (_cmp_cached_103))
            # 1h down move, 1d high, 1d downtrend
            & ((_cmp_cached_7) | (_cmp_cached_27) | (_cmp_cached_57))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_7) | (_cmp_cached_27) | (_cmp_cached_167))
            # 1h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_7) | (_cmp_cached_35) | (_cmp_cached_42))
            # 1h down move, 4h & 1d downtrend
            & ((_cmp_cached_7) | (_cmp_cached_81) | (_cmp_cached_42))
            # 1h & 4h & 1d down move
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_29))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_33))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_108))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_35))
            # 1h & 4h down move, 1d still not low enough
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_265))
            # 1h & 4h down move, 4h downtrend
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_266))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_57))
            # 1h & 4h down move, 15m downtrend
            & ((_cmp_cached_9) | (_cmp_cached_25) | (_cmp_cached_44))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_9) | (_cmp_cached_100) | (_cmp_cached_35))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_9) | (_cmp_cached_100) | (_cmp_cached_102))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_9) | (_cmp_cached_16) | (_cmp_cached_46))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_9) | (_cmp_cached_16) | (_cmp_cached_108))
            # 1h & 1d down move, 1d downtrend
            & ((_cmp_cached_9) | (_cmp_cached_153) | (_cmp_cached_102))
            # 1h & 1d down move, 4h still high
            & ((_cmp_cached_9) | (_cmp_cached_153) | (_cmp_cached_96))
            # 1h & 1d down move, 4h high
            & ((_cmp_cached_9) | (_cmp_cached_29) | (_cmp_cached_64))
            # 1h & 1d down move, 1h still not low enough
            & ((_cmp_cached_9) | (_cmp_cached_104) | (_cmp_cached_190))
            # 1h & 1d down move, 1h high
            & ((_cmp_cached_9) | (_cmp_cached_121) | (_cmp_cached_24))
            # 1h & 1d down move, 1h downtrend
            & ((_cmp_cached_9) | (_cmp_cached_178) | (_cmp_cached_240))
            # 1h down move, 1d downtrend, 4h high
            & ((_cmp_cached_9) | (_cmp_cached_224) | (_cmp_cached_72))
            # 1h down move, 1h still high, 4h overbought
            & ((_cmp_cached_9) | (_cmp_cached_26) | (_cmp_cached_20))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_9) | (_cmp_cached_115) | (_cmp_cached_40))
            # 1h down move, 1h high, 1d high
            & ((_cmp_cached_9) | (_cmp_cached_115) | (_cmp_cached_39))
            # 1h down move, 1d overbought
            & ((_cmp_cached_9) | (_cmp_cached_107))
            # 1h & 4h down move, 1h downtrend
            & ((_cmp_cached_15) | (_cmp_cached_25) | (_cmp_cached_130))
            # 1h & 4h down move, 4h downtrend
            & ((_cmp_cached_15) | (_cmp_cached_25) | (_cmp_cached_81))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_15) | (_cmp_cached_25) | (_cmp_cached_206))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_15) | (_cmp_cached_100) | (_cmp_cached_169))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_15) | (_cmp_cached_100) | (_cmp_cached_17))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_15) | (_cmp_cached_100) | (_cmp_cached_27))
            # 1h & 1d down move, 1h still high
            & ((_cmp_cached_15) | (_cmp_cached_178) | (_cmp_cached_28))
            # 1h & 1d down move, 1h high
            & ((_cmp_cached_15) | (_cmp_cached_178) | (_cmp_cached_33))
            # 1h down move, 1h downtrend, 1h still high
            & ((_cmp_cached_15) | (_cmp_cached_177) | (_cmp_cached_28))
            # 1h down move, 1d downtrend, 1d high
            & ((_cmp_cached_15) | (_cmp_cached_224) | (_cmp_cached_74))
            # 1h down move, 1h & 1d high
            & ((_cmp_cached_15) | (_cmp_cached_24) | (_cmp_cached_94))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_15) | (_cmp_cached_24) | (_cmp_cached_52))
            # 1h down move, 1h high, 1h downtrend
            & ((_cmp_cached_15) | (_cmp_cached_33) | (_cmp_cached_114))
            # 1h down move, 1h high, 4h downtrend
            & ((_cmp_cached_15) | (_cmp_cached_33) | (_cmp_cached_103))
            # 1h down move, 4h still high, 1d overbought
            & ((_cmp_cached_15) | (_cmp_cached_122) | (_cmp_cached_112))
            # 1h down move, 4h high, 15m downtrend
            & ((_cmp_cached_15) | (_cmp_cached_47) | (_cmp_cached_116))
            # 1h down move, 4h high, 1h downtrend
            & ((_cmp_cached_15) | (_cmp_cached_47) | (_cmp_cached_109))
            # 1h down move, 1d high, 4h overbought
            & ((_cmp_cached_15) | (_cmp_cached_27) | (_cmp_cached_50))
            # 1h down move, 4h still not low enough, 1d downtrend
            & ((_cmp_cached_15) | (_cmp_cached_124) | (_cmp_cached_102))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_15) | (_cmp_cached_12) | (_cmp_cached_196))
            # 1h down move, 1h downtrend, 1d overbought
            & ((_cmp_cached_15) | (_cmp_cached_109) | (_cmp_cached_267))
            # 1h down move, 4h downtrend, 1d overbought
            & ((_cmp_cached_15) | (_cmp_cached_81) | (_cmp_cached_48))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_30) | (_cmp_cached_100) | (_cmp_cached_108))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_30) | (_cmp_cached_99) | (_cmp_cached_64))
            # 1h & 1d down move, 4h high
            & ((_cmp_cached_30) | (_cmp_cached_104) | (_cmp_cached_46))
            # 1h & 1d down move, 1h high
            & ((_cmp_cached_30) | (_cmp_cached_121) | (_cmp_cached_24))
            # 1h & 1d down move, 4h overbought
            & ((_cmp_cached_30) | (_cmp_cached_178) | (_cmp_cached_51))
            # 1h down move, 1h still high, 4h high
            & ((_cmp_cached_30) | (_cmp_cached_26) | (_cmp_cached_46))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_30) | (_cmp_cached_24) | (_cmp_cached_48))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_30) | (_cmp_cached_27) | (_cmp_cached_112))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_30) | (_cmp_cached_37) | (_cmp_cached_50))
            # 1h down move, 1d high, 1d downtrend
            & ((_cmp_cached_30) | (_cmp_cached_74) | (_cmp_cached_42))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_30) | (_cmp_cached_39) | (_cmp_cached_52))
            # 1h down move, 1h & 4h overbought
            & ((_cmp_cached_30) | (_cmp_cached_79) | (_cmp_cached_113))
            # 1h down move, 4h & 1d downtrend
            & ((_cmp_cached_30) | (_cmp_cached_103) | (_cmp_cached_65))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_181) | (_cmp_cached_48))
            # 1h down move, 15m still high, 1h high
            & ((_cmp_cached_11) | (_cmp_cached_62) | (_cmp_cached_78))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_24) | (_cmp_cached_111))
            # 1h down move, 1h & 1d high
            & ((_cmp_cached_11) | (_cmp_cached_24) | (_cmp_cached_94))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_11) | (_cmp_cached_33) | (_cmp_cached_20))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_45) | (_cmp_cached_107))
            # 1h down move, 4h high
            & ((_cmp_cached_11) | (_cmp_cached_46))
            # 1h down move, 1h still high, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_59) | (_cmp_cached_52))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_11) | (_cmp_cached_12) | (_cmp_cached_65))
            # 1h down move, 15m downtrend, 4h overbought
            & ((_cmp_cached_11) | (_cmp_cached_268) | (_cmp_cached_51))
            # 1h down move, 1h & 1d downtrend
            & ((_cmp_cached_11) | (_cmp_cached_264) | (_cmp_cached_42))
            # 1h down move, 1h downtrend, 4h overbought
            & ((_cmp_cached_11) | (_cmp_cached_135) | (_cmp_cached_86))
            # 1h down move, 1h & 4h overbought
            & ((_cmp_cached_11) | (_cmp_cached_158) | (_cmp_cached_196))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_32) | (_cmp_cached_41) | (_cmp_cached_78))
            # 1h & 4h down move, 4h downtrend
            & ((_cmp_cached_32) | (_cmp_cached_41) | (_cmp_cached_69))
            # 1h down move, 1h downtrend, 1h high
            & ((_cmp_cached_32) | (_cmp_cached_114) | (_cmp_cached_37))
            # 1h down move, 4h downtrend, 4h high
            & ((_cmp_cached_32) | (_cmp_cached_193) | (_cmp_cached_6))
            # 1h down move, 1h high & overbought
            & ((_cmp_cached_32) | (_cmp_cached_24) | (_cmp_cached_82))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_32) | (_cmp_cached_24) | (_cmp_cached_194))
            # 1h down move, 4h high, 1h overbought
            & ((_cmp_cached_32) | (_cmp_cached_77) | (_cmp_cached_183))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_32) | (_cmp_cached_46) | (_cmp_cached_102))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_32) | (_cmp_cached_6) | (_cmp_cached_167))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_32) | (_cmp_cached_50) | (_cmp_cached_107))
            # 1h down move, 15m & 1h high
            & ((_cmp_cached_34) | (_cmp_cached_76) | (_cmp_cached_80))
            # 1h down move, 1h high, 4h downtrend
            & ((_cmp_cached_34) | (_cmp_cached_24) | (_cmp_cached_213))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_34) | (_cmp_cached_33) | (_cmp_cached_6))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_34) | (_cmp_cached_33) | (_cmp_cached_65))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_34) | (_cmp_cached_78) | (_cmp_cached_50))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_34) | (_cmp_cached_17) | (_cmp_cached_111))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_34) | (_cmp_cached_6) | (_cmp_cached_20))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_34) | (_cmp_cached_12) | (_cmp_cached_51))
            # 1h down move, 1h downtrend, 4h overbought
            & ((_cmp_cached_34) | (_cmp_cached_109) | (_cmp_cached_196))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_34) | (_cmp_cached_20) | (_cmp_cached_216))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_36) | (_cmp_cached_24) | (_cmp_cached_6))
            # 1h down move, 1h high & overbought
            & ((_cmp_cached_36) | (_cmp_cached_33) | (_cmp_cached_82))
            # 1h down move, 1h high, 1d high
            & ((_cmp_cached_36) | (_cmp_cached_45) | (_cmp_cached_63))
            # 1h down move, 1h high, 15m downtrend
            & ((_cmp_cached_36) | (_cmp_cached_78) | (_cmp_cached_261))
            # 1h down move, 1h  high & overbought
            & ((_cmp_cached_36) | (_cmp_cached_19) | (_cmp_cached_82))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_36) | (_cmp_cached_20) | (_cmp_cached_48))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_36) | (_cmp_cached_51) | (_cmp_cached_52))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_38) | (_cmp_cached_80) | (_cmp_cached_111))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_38) | (_cmp_cached_12) | (_cmp_cached_196))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_117) | (_cmp_cached_115) | (_cmp_cached_206))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_117) | (_cmp_cached_37) | (_cmp_cached_48))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_117) | (_cmp_cached_162) | (_cmp_cached_194))
            # 1h down move, 1h high
            & ((_cmp_cached_53) | (_cmp_cached_19))
            # 1h down move, 1h overbought
            & ((_cmp_cached_53) | (_cmp_cached_158))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_53) | (_cmp_cached_51) | (_cmp_cached_112))
            # 4h & 1d down move, 1d still not low enough
            & ((_cmp_cached_151) | (_cmp_cached_178) | (_cmp_cached_269))
            # 4h down move, 4h high, 1h downtrend
            & ((_cmp_cached_151) | (_cmp_cached_17) | (_cmp_cached_239))
            # 4h down move, 1h still high, 4h downtrend
            & ((_cmp_cached_151) | (_cmp_cached_59) | (_cmp_cached_103))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_55) | (_cmp_cached_104) | (_cmp_cached_238))
            # 4h down move, 15m still high, 1d downtrend
            & ((_cmp_cached_55) | (_cmp_cached_62) | (_cmp_cached_102))
            # 4h & 1d down move, 1d downtrend
            & ((_cmp_cached_58) | (_cmp_cached_121) | (_cmp_cached_42))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_58) | (_cmp_cached_108) | (_cmp_cached_63))
            # 4h down move, 1h & 4h downtrend
            & ((_cmp_cached_58) | (_cmp_cached_109) | (_cmp_cached_103))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_58) | (_cmp_cached_148) | (_cmp_cached_267))
            # 4h down move, 4h & 1d downtrend
            & ((_cmp_cached_58) | (_cmp_cached_219) | (_cmp_cached_270))
            # 4h down move, 4h still high, 1d overbought
            & ((_cmp_cached_25) | (_cmp_cached_96) | (_cmp_cached_52))
            # 4h down move, 1h still not low enough, 1d downtrend
            & ((_cmp_cached_25) | (_cmp_cached_190) | (_cmp_cached_57))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_100) | (_cmp_cached_104) | (_cmp_cached_148))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_100) | (_cmp_cached_108) | (_cmp_cached_111))
            # 4h down move, 4h & 1d downtrend
            & ((_cmp_cached_100) | (_cmp_cached_69) | (_cmp_cached_102))
            # 4h down move, 15m high, 1d overbought
            & ((_cmp_cached_16) | (_cmp_cached_76) | (_cmp_cached_48))
            # 4h down move, 4h high
            & ((_cmp_cached_16) | (_cmp_cached_77))
            # 4h down move, 1d high, 1h downtrend
            & ((_cmp_cached_16) | (_cmp_cached_27) | (_cmp_cached_239))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_41) | (_cmp_cached_122) | (_cmp_cached_65))
            # 4h down move, 4h still high, 1d overbought
            & ((_cmp_cached_41) | (_cmp_cached_122) | (_cmp_cached_111))
            # 4h down move, 4h still not low enough, 1d overbought
            & ((_cmp_cached_41) | (_cmp_cached_156) | (_cmp_cached_112))
            # 4h down move, 1d high, 1d downtrend
            & ((_cmp_cached_21) | (_cmp_cached_60) | (_cmp_cached_102))
            # 4h down move, 1h high, 1d overbought
            & ((_cmp_cached_91) | (_cmp_cached_45) | (_cmp_cached_107))
            # 4h down move, 1d high, 1d downtrend
            & ((_cmp_cached_91) | (_cmp_cached_108) | (_cmp_cached_149))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_91) | (_cmp_cached_39) | (_cmp_cached_201))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_99) | (_cmp_cached_169) | (_cmp_cached_102))
            # 4h down move, 4h high & overbought
            & ((_cmp_cached_99) | (_cmp_cached_77) | (_cmp_cached_50))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_99) | (_cmp_cached_35) | (_cmp_cached_102))
            # 4h down move, 4h & 1d overbought
            & ((_cmp_cached_99) | (_cmp_cached_50) | (_cmp_cached_52))
            # 1d down move, 4h still high, 1d downtrend
            & ((_cmp_cached_225) | (_cmp_cached_165) | (_cmp_cached_195))
            # 1d down move, 1h & 4h high
            & ((_cmp_cached_153) | (_cmp_cached_26) | (_cmp_cached_46))
            # 1d down move, 1d high, 1d downtrend
            & ((_cmp_cached_153) | (_cmp_cached_106) | (_cmp_cached_65))
            # 1d down move, 4h high, 1d downtrend
            & ((_cmp_cached_153) | (_cmp_cached_72) | (_cmp_cached_218))
            # 1d down move, 1h & 4h high
            & ((_cmp_cached_29) | (_cmp_cached_78) | (_cmp_cached_6))
            # 1d down move, 1h high, 1d downtrend
            & ((_cmp_cached_104) | (_cmp_cached_80) | (_cmp_cached_102))
            # 1d down move, 1h still high, 4h downtrend
            & ((_cmp_cached_121) | (_cmp_cached_59) | (_cmp_cached_103))
            # 1d down move, 1h high & overbought
            & ((_cmp_cached_192) | (_cmp_cached_49) | (_cmp_cached_82))
            # 15m downtrend, 4h & 1d high
            & ((_cmp_cached_159) | (_cmp_cached_77) | (_cmp_cached_27))
            # 15m & 1h high, 1h overbought
            & ((_cmp_cached_76) | (_cmp_cached_80) | (_cmp_cached_183))
            # 15m & 1d high, 1d overbought
            & ((_cmp_cached_76) | (_cmp_cached_94) | (_cmp_cached_70))
            # 1h & 4h high, 1h downtrend
            & ((_cmp_cached_24) | (_cmp_cached_6) | (_cmp_cached_177))
            # 1h high, 4h high, 1h overbought
            & ((_cmp_cached_24) | (_cmp_cached_6) | (_cmp_cached_79))
            # 1h & 1d high, 1h overbought
            & ((_cmp_cached_24) | (_cmp_cached_106) | (_cmp_cached_79))
            # 1h high, 1d high & overbought
            & ((_cmp_cached_24) | (_cmp_cached_27) | (_cmp_cached_111))
            # 1h high, 1h & 1d overbought
            & ((_cmp_cached_24) | (_cmp_cached_79) | (_cmp_cached_111))
            # 1h high, 4h downtrend, 1d overbought
            & ((_cmp_cached_24) | (_cmp_cached_213) | (_cmp_cached_48))
            # 1h high, 1h & 1d overbought
            & ((_cmp_cached_33) | (_cmp_cached_79) | (_cmp_cached_167))
            # 1h high, 1h overbought, 1d downtrend
            & ((_cmp_cached_33) | (_cmp_cached_158) | (_cmp_cached_65))
            # 1h high, 4h & 1d overbought
            & ((_cmp_cached_33) | (_cmp_cached_50) | (_cmp_cached_52))
            # 1h high, 4h & 1d downtrend
            & ((_cmp_cached_45) | (_cmp_cached_69) | (_cmp_cached_42))
            # 1h & 4h high, 1h overbought
            & ((_cmp_cached_80) | (_cmp_cached_6) | (_cmp_cached_82))
            # 4h high, 4h & 1d overbought
            & ((_cmp_cached_40) | (_cmp_cached_51) | (_cmp_cached_112))
            # 4h & 1d high, 4h overbought
            & ((_cmp_cached_77) | (_cmp_cached_27) | (_cmp_cached_51))
            # 4h high, 4h & 1d overbought
            & ((_cmp_cached_77) | (_cmp_cached_20) | (_cmp_cached_167))
            # 4h high, 15m downtrend, 4h overbought
            & ((_cmp_cached_6) | (_cmp_cached_187) | (_cmp_cached_51))
            # 4h high, 1h & 4h overbought
            & ((_cmp_cached_6) | (_cmp_cached_158) | (_cmp_cached_217))
            # 4h & 1d high, 1h overbought
            & ((_cmp_cached_6) | (_cmp_cached_27) | (_cmp_cached_183))
            # 1d still high, 4h & 1d downtrend
            & ((_cmp_cached_238) | (_cmp_cached_204) | (_cmp_cached_42))
            # 1d high, 1h & 4h downtrend
            & ((_cmp_cached_131) | (_cmp_cached_109) | (_cmp_cached_204))
            # 1d high, 4h downtrend, 1d overbought
            & ((_cmp_cached_131) | (_cmp_cached_81) | (_cmp_cached_107))
            # 1d high, 4h & 1d overbought
            & ((_cmp_cached_94) | (_cmp_cached_50) | (_cmp_cached_107))
            # 1h high, 1d overbought
            & ((_cmp_cached_37) | (_cmp_cached_52))
            # 1h high, 4h overbought
            & ((_cmp_cached_19) | (_cmp_cached_67))
            # 1h high, 1h overbought, 4h downtrend
            & ((_cmp_cached_49) | (_cmp_cached_82) | (_cmp_cached_219))
            # 4h high, 1h & 4h overbought
            & ((_cmp_cached_72) | (_cmp_cached_79) | (_cmp_cached_86))
            # 1d high, 4h & 1d overbought
            & ((_cmp_cached_39) | (_cmp_cached_196) | (_cmp_cached_48))
            # 1d P&D, 4h overbought
            & ((_cmp_cached_231) | (df["change_pct_1d"].shift(288) < 30.0) | (_cmp_cached_50))
            # big drop in the last 20 days, 1d high, 1d downtrend
            & (
              (df["close"] > (df["high_max_20_1d"] * 0.20))
              | (_cmp_cached_148)
              | (_cmp_cached_149)
            )
          )

          # Logic
          long_entry_logic.append(
            (_cmp_cached_8)
            & (_cmp_cached_271)
            & (_cmp_cached_243)
            & (_cmp_cached_272)
            & (df["EMA_9"] < (df["EMA_26"] * 0.960))
          )

        # Condition #42 - Quick mode (Long).
        if long_entry_condition_index == 42:
          # Protections
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          # long_entry_logic.append(df["protections_long_global"] == True)

          long_entry_logic.append(
            # 5m & 1h down move, 1d still high
            ((_cmp_cached_0) | (_cmp_cached_13) | (_cmp_cached_56))
            # 5m & 1h down move, 1d high
            & ((_cmp_cached_0) | (_cmp_cached_11) | (_cmp_cached_148))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_1) | (_cmp_cached_13) | (_cmp_cached_64))
            # 15m & 1h down move, 1h downtrend
            & ((_cmp_cached_1) | (_cmp_cached_13) | (_cmp_cached_264))
            # 15m & 1h down move, 1d still not low enough
            & ((_cmp_cached_1) | (_cmp_cached_7) | (_cmp_cached_273))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_1) | (_cmp_cached_9) | (_cmp_cached_122))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_1) | (_cmp_cached_9) | (_cmp_cached_199))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_1) | (_cmp_cached_15) | (_cmp_cached_115))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_1) | (_cmp_cached_41) | (_cmp_cached_165))
            # 15m & 4h down move, 1d still high
            & ((_cmp_cached_1) | (_cmp_cached_25) | (_cmp_cached_119))
            # 15m & 1h down move, 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_15) | (_cmp_cached_102))
            # 15m down move, 4h still high, 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_165) | (_cmp_cached_65))
            # 15m & 1h & 4h down move
            & ((_cmp_cached_3) | (_cmp_cached_7) | (_cmp_cached_100))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_3) | (_cmp_cached_7) | (_cmp_cached_110))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_3) | (_cmp_cached_7) | (_cmp_cached_106))
            # 15m & 1h & 4h down move
            & ((_cmp_cached_3) | (_cmp_cached_9) | (_cmp_cached_25))
            # 15m & 4h down move, 1h downtrend
            & ((_cmp_cached_3) | (_cmp_cached_58) | (_cmp_cached_129))
            # 15m & 4h down move, 1d downtrend
            & ((_cmp_cached_3) | (_cmp_cached_58) | (_cmp_cached_102))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_3) | (_cmp_cached_41) | (_cmp_cached_96))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_9) | (_cmp_cached_17))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_9) | (_cmp_cached_27))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_5) | (_cmp_cached_9) | (_cmp_cached_165))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_9) | (_cmp_cached_39))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_15) | (_cmp_cached_162))
            # 15m & 1h down move, 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_15) | (_cmp_cached_102))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_30) | (_cmp_cached_6))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_30) | (_cmp_cached_95))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_41) | (_cmp_cached_39))
            # 15m & 1d down move, 4h still high
            & ((_cmp_cached_5) | (_cmp_cached_153) | (_cmp_cached_165))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_5) | (_cmp_cached_58) | (_cmp_cached_165))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_100) | (_cmp_cached_148))
            # 15m & 4h down move, 4h still not low enough
            & ((_cmp_cached_5) | (_cmp_cached_100) | (_cmp_cached_124))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_100) | (_cmp_cached_74))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_84) | (_cmp_cached_15) | (_cmp_cached_24))
            # 15m & 1h down move, 15m still high
            & ((_cmp_cached_84) | (_cmp_cached_30) | (_cmp_cached_61))
            # 15m & 4h down move, 15m still high
            & ((_cmp_cached_84) | (_cmp_cached_25) | (_cmp_cached_61))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_84) | (_cmp_cached_100) | (_cmp_cached_40))
            # 15m & 1d down move, 1d high
            & ((_cmp_cached_84) | (_cmp_cached_125) | (_cmp_cached_148))
            # 15m down move, 15m high
            & ((_cmp_cached_84) | (_cmp_cached_76))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_87) | (_cmp_cached_16) | (_cmp_cached_17))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_87) | (_cmp_cached_24) | (_cmp_cached_6))
            # 15m down move, 15m still not low enough, 1d downtrend
            & ((_cmp_cached_88) | (_cmp_cached_179) | (_cmp_cached_42))
            # 15m down move, 15m still high, 4h high
            & ((_cmp_cached_88) | (_cmp_cached_62) | (_cmp_cached_77))
            # 15m down move, 4h high, 1d downtrend
            & ((_cmp_cached_88) | (_cmp_cached_12) | (_cmp_cached_65))
            # 15m down move, 4h high, 1d downtrend
            & ((_cmp_cached_88) | (_cmp_cached_72) | (_cmp_cached_186))
            # 15m down move, 15m still high, 4h high
            & ((_cmp_cached_184) | (_cmp_cached_62) | (_cmp_cached_77))
            # 1h & 4h down move
            & ((_cmp_cached_13) | (_cmp_cached_151))
            # 1h & 4h down move, 1d still high
            & ((_cmp_cached_13) | (_cmp_cached_25) | (_cmp_cached_238))
            # 1h & 4h down move, 1d still high
            & ((_cmp_cached_13) | (_cmp_cached_25) | (_cmp_cached_14))
            # 1h & 4h down move, 1h still high
            & ((_cmp_cached_13) | (_cmp_cached_100) | (_cmp_cached_110))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_13) | (_cmp_cached_100) | (_cmp_cached_124))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_13) | (_cmp_cached_16) | (_cmp_cached_17))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_13) | (_cmp_cached_16) | (_cmp_cached_106))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_13) | (_cmp_cached_16) | (_cmp_cached_162))
            # 1h down move, 1d high, 1d downtrend
            & ((_cmp_cached_13) | (_cmp_cached_106) | (_cmp_cached_264))
            # 1h & 4h down move, 15m still not low enough
            & ((_cmp_cached_7) | (_cmp_cached_55) | (_cmp_cached_171))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_7) | (_cmp_cached_55) | (_cmp_cached_102))
            # 1h & 4h down move, 1d still high
            & ((_cmp_cached_7) | (_cmp_cached_25) | (_cmp_cached_119))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_7) | (_cmp_cached_16) | (_cmp_cached_24))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_7) | (_cmp_cached_16) | (_cmp_cached_74))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_7) | (_cmp_cached_21) | (_cmp_cached_52))
            # 1h & 1d down move, 1h still high
            & ((_cmp_cached_7) | (_cmp_cached_101) | (_cmp_cached_26))
            # 1h down move, 4h high
            & ((_cmp_cached_7) | (_cmp_cached_46))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_214))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_74))
            # 1h & 4h down move, 4h downtrend
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_69))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_57))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_95))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_9) | (_cmp_cached_25) | (_cmp_cached_108))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_9) | (_cmp_cached_25) | (_cmp_cached_156))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_9) | (_cmp_cached_25) | (_cmp_cached_65))
            # 1h & 4h down move, 1h still high
            & ((_cmp_cached_9) | (_cmp_cached_100) | (_cmp_cached_110))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_9) | (_cmp_cached_100) | (_cmp_cached_17))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_9) | (_cmp_cached_100) | (_cmp_cached_94))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_9) | (_cmp_cached_16) | (_cmp_cached_52))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_9) | (_cmp_cached_21) | (_cmp_cached_27))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_9) | (_cmp_cached_21) | (_cmp_cached_64))
            # 1h & 1d down move, 1d still high
            & ((_cmp_cached_9) | (_cmp_cached_153) | (_cmp_cached_14))
            # 1h & 1d down move, 1d still high
            & ((_cmp_cached_9) | (_cmp_cached_121) | (_cmp_cached_170))
            # 1h & 1d down move, 1h high
            & ((_cmp_cached_9) | (_cmp_cached_121) | (_cmp_cached_24))
            # 1h & 1d down move, 1d high
            & ((_cmp_cached_9) | (_cmp_cached_198) | (_cmp_cached_106))
            # 1h down move, 1h downtrend, 1h high
            & ((_cmp_cached_9) | (_cmp_cached_177) | (_cmp_cached_24))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_9) | (_cmp_cached_110) | (_cmp_cached_57))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_9) | (_cmp_cached_115) | (_cmp_cached_17))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_9) | (_cmp_cached_115) | (_cmp_cached_167))
            # 1h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_9) | (_cmp_cached_96) | (_cmp_cached_65))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_9) | (_cmp_cached_17) | (_cmp_cached_57))
            # 1h down move, 1d still high, 1d downtrend
            & ((_cmp_cached_9) | (_cmp_cached_119) | (_cmp_cached_57))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_9) | (_cmp_cached_94) | (_cmp_cached_70))
            # 1h down move, 15m high
            & ((_cmp_cached_9) | (_cmp_cached_180))
            # 1h down move, 4h & 1d downtrend
            & ((_cmp_cached_9) | (_cmp_cached_69) | (_cmp_cached_65))
            # 1h & 4h down move, 1d still high, 1d downtrend
            & ((_cmp_cached_15) | (_cmp_cached_25) | (_cmp_cached_176) | (_cmp_cached_149))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_15) | (_cmp_cached_25) | (_cmp_cached_122))
            # 1h & 4h down move, 15m still high
            & ((_cmp_cached_15) | (_cmp_cached_25) | (_cmp_cached_155))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_15) | (_cmp_cached_25) | (_cmp_cached_156))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_15) | (_cmp_cached_25) | (_cmp_cached_148))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_15) | (_cmp_cached_16) | (_cmp_cached_65))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_15) | (_cmp_cached_41) | (_cmp_cached_40))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_15) | (_cmp_cached_41) | (_cmp_cached_74))
            # 1h & 4h down move, 4h overbought
            & ((_cmp_cached_15) | (_cmp_cached_21) | (_cmp_cached_50))
            # 1h & 1d down move, 4h high
            & ((_cmp_cached_15) | (_cmp_cached_104) | (_cmp_cached_162))
            # 1h & 1d down move, 1d overbought
            & ((_cmp_cached_15) | (_cmp_cached_192) | (_cmp_cached_95))
            # 1h down move, 1h downtrend, 1h high
            & ((_cmp_cached_15) | (_cmp_cached_177) | (_cmp_cached_24))
            # 1h down move, 1h still high, 4h downtrend
            & ((_cmp_cached_15) | (_cmp_cached_110) | (_cmp_cached_103))
            # 1h down move, 1h still high, 1d downtrend
            & ((_cmp_cached_15) | (_cmp_cached_26) | (_cmp_cached_65))
            # 1h down move, 1d still high, 4h downtrend
            & ((_cmp_cached_15) | (_cmp_cached_238) | (_cmp_cached_69))
            # 1h down move, 1d high, 1d downtrend
            & ((_cmp_cached_15) | (_cmp_cached_108) | (_cmp_cached_57))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_15) | (_cmp_cached_108) | (_cmp_cached_70))
            # 1h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_15) | (_cmp_cached_35) | (_cmp_cached_102))
            # 1h down move, 4h & 1d downtrend
            & ((_cmp_cached_15) | (_cmp_cached_69) | (_cmp_cached_57))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_30) | (_cmp_cached_100) | (_cmp_cached_24))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_30) | (_cmp_cached_100) | (_cmp_cached_27))
            # 1h & 4h down move, 15m high
            & ((_cmp_cached_30) | (_cmp_cached_100) | (_cmp_cached_222))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_30) | (_cmp_cached_100) | (_cmp_cached_70))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_30) | (_cmp_cached_99) | (_cmp_cached_12))
            # 1h & 1d down move, 1d high
            & ((_cmp_cached_30) | (_cmp_cached_104) | (_cmp_cached_60))
            # 1h & 1d down move, 1d high
            & ((_cmp_cached_30) | (_cmp_cached_178) | (_cmp_cached_27))
            # 1h & 1d down move, 1d overbought
            & ((_cmp_cached_30) | (_cmp_cached_198) | (_cmp_cached_167))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_30) | (_cmp_cached_115) | (_cmp_cached_70))
            # 1h down move, 1h high, 4h downtrend
            & ((_cmp_cached_30) | (_cmp_cached_24) | (_cmp_cached_69))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_30) | (_cmp_cached_27) | (_cmp_cached_70))
            # 1h down move, 1d high, 4h downtrend
            & ((_cmp_cached_30) | (_cmp_cached_74) | (_cmp_cached_69))
            # 1h & 4h down move, 15m high
            & ((_cmp_cached_11) | (_cmp_cached_16) | (_cmp_cached_92))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_11) | (_cmp_cached_181) | (_cmp_cached_17))
            # 1h & 1d down move, 1h high
            & ((_cmp_cached_11) | (_cmp_cached_121) | (_cmp_cached_33))
            # 1h & 1d down move, 1d high
            & ((_cmp_cached_11) | (_cmp_cached_198) | (_cmp_cached_74))
            # 1h down move, 4h downtrend, 4h high
            & ((_cmp_cached_11) | (_cmp_cached_193) | (_cmp_cached_17))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_115) | (_cmp_cached_107))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_11) | (_cmp_cached_115) | (_cmp_cached_65))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_11) | (_cmp_cached_17) | (_cmp_cached_50))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_11) | (_cmp_cached_108) | (_cmp_cached_111))
            # 1h down move, 1d high, 4h overbought
            & ((_cmp_cached_11) | (_cmp_cached_27) | (_cmp_cached_50))
            # 1h down move, 1h high & overbought
            & ((_cmp_cached_11) | (_cmp_cached_27) | (_cmp_cached_167))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_11) | (_cmp_cached_12) | (_cmp_cached_20))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_32) | (_cmp_cached_41) | (_cmp_cached_42))
            # 1h & 4h down move, 15m high
            & ((_cmp_cached_32) | (_cmp_cached_21) | (_cmp_cached_18))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_32) | (_cmp_cached_181) | (_cmp_cached_172))
            # 1h & 4h down move, 15m high
            & ((_cmp_cached_32) | (_cmp_cached_181) | (_cmp_cached_180))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_32) | (_cmp_cached_99) | (_cmp_cached_77))
            # 1h & 1d down move, 1d high
            & ((_cmp_cached_32) | (_cmp_cached_178) | (_cmp_cached_108))
            # 1h & 1d down move, 1d overbought
            & ((_cmp_cached_32) | (_cmp_cached_125) | (_cmp_cached_107))
            # 1h down move, 4h high, 4h downtrend
            & ((_cmp_cached_32) | (_cmp_cached_17) | (_cmp_cached_200))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_32) | (_cmp_cached_77) | (_cmp_cached_51))
            # 1h down move, 1d high, 4h overbought
            & ((_cmp_cached_32) | (_cmp_cached_27) | (_cmp_cached_50))
            # 1h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_32) | (_cmp_cached_165) | (_cmp_cached_218))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_32) | (_cmp_cached_50) | (_cmp_cached_70))
            # 1h & 4h down move, 15m high
            & ((_cmp_cached_34) | (_cmp_cached_91) | (_cmp_cached_274))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_34) | (_cmp_cached_91) | (_cmp_cached_46))
            # 1h down move, 15m high, 1d downtrend
            & ((_cmp_cached_34) | (_cmp_cached_210) | (_cmp_cached_65))
            # 1h down move, 1h still high, 1d high
            & ((_cmp_cached_34) | (_cmp_cached_26) | (_cmp_cached_94))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_34) | (_cmp_cached_24) | (_cmp_cached_6))
            # 1h down move, 1h & 1d high
            & ((_cmp_cached_34) | (_cmp_cached_24) | (_cmp_cached_27))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_34) | (_cmp_cached_46) | (_cmp_cached_57))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_34) | (_cmp_cached_72) | (_cmp_cached_50))
            # 1h down move, 4h & 1d downtrend
            & ((_cmp_cached_34) | (_cmp_cached_93) | (_cmp_cached_194))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_36) | (_cmp_cached_46) | (_cmp_cached_20))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_36) | (_cmp_cached_162) | (_cmp_cached_42))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_36) | (_cmp_cached_64) | (_cmp_cached_113))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_38) | (_cmp_cached_77) | (_cmp_cached_196))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_117) | (_cmp_cached_6) | (_cmp_cached_113))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_117) | (_cmp_cached_39) | (_cmp_cached_167))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_53) | (_cmp_cached_51) | (_cmp_cached_48))
            # 4h & 1d down move
            & ((_cmp_cached_151) | (_cmp_cached_29))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_151) | (_cmp_cached_121) | (_cmp_cached_60))
            # 4h down move, 1h downtrend, 4h still high
            & ((_cmp_cached_151) | (_cmp_cached_177) | (_cmp_cached_96))
            # 4h & 1d down move, 4h downtrend
            & ((_cmp_cached_55) | (_cmp_cached_29) | (_cmp_cached_93))
            # 4h & 1d down move, 1d downtrend
            & ((_cmp_cached_55) | (_cmp_cached_29) | (_cmp_cached_57))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_55) | (_cmp_cached_104) | (_cmp_cached_119))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_55) | (_cmp_cached_104) | (_cmp_cached_14))
            # 4h & 1d down move, 4h still not low enough
            & ((_cmp_cached_55) | (_cmp_cached_178) | (_cmp_cached_120))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_55) | (_cmp_cached_178) | (_cmp_cached_106))
            # 4h down move, 1h & 4h downtrend
            & ((_cmp_cached_55) | (_cmp_cached_130) | (_cmp_cached_69))
            # 4h down move, 4h & 1d downtrend
            & ((_cmp_cached_55) | (_cmp_cached_69) | (_cmp_cached_57))
            # 4h & 1d down move, 15m still not low enough
            & ((_cmp_cached_58) | (_cmp_cached_153) | (_cmp_cached_10))
            # 4h & 1d down move, 1d downtrend
            & ((_cmp_cached_58) | (_cmp_cached_153) | (_cmp_cached_57))
            # 15m & 1d down move, 15m still high
            & ((_cmp_cached_58) | (_cmp_cached_29) | (_cmp_cached_61))
            # 4h & 1d down move, 4h downtrend
            & ((_cmp_cached_58) | (_cmp_cached_178) | (_cmp_cached_69))
            # 4h & 1d down move, 1d overbought
            & ((_cmp_cached_58) | (_cmp_cached_198) | (_cmp_cached_95))
            # 4h & 1d down move, 4h still not low enough
            & ((_cmp_cached_58) | (_cmp_cached_73) | (_cmp_cached_156))
            # 4h down move, 15m high, 1h downtrend
            & ((_cmp_cached_58) | (_cmp_cached_222) | (_cmp_cached_132))
            # 4h down move, 15m high
            & ((_cmp_cached_58) | (_cmp_cached_180))
            # 4h down move, 4h still not low e nough, 1d downtrend
            & ((_cmp_cached_58) | (_cmp_cached_124) | (_cmp_cached_57))
            # 4h down move, 4h & 1d downtrend
            & ((_cmp_cached_58) | (_cmp_cached_69) | (_cmp_cached_65))
            # 4h & 1d down move, 1d downtrend
            & ((_cmp_cached_25) | (_cmp_cached_29) | (_cmp_cached_102))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_25) | (_cmp_cached_121) | (_cmp_cached_119))
            # 15m & 1d down move, 15m high
            & ((_cmp_cached_25) | (_cmp_cached_178) | (_cmp_cached_92))
            # 4h & 1d down move, 4h still high
            & ((_cmp_cached_25) | (_cmp_cached_178) | (_cmp_cached_35))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_25) | (_cmp_cached_192) | (_cmp_cached_170))
            # 4h down move, 1h still high, 1d downtrend
            & ((_cmp_cached_25) | (_cmp_cached_110) | (_cmp_cached_42))
            # 4h down move, 1h high, 1d downtrend
            & ((_cmp_cached_25) | (_cmp_cached_78) | (_cmp_cached_102))
            # 4h down move, 4h still high, 4h downtrend
            & ((_cmp_cached_25) | (_cmp_cached_96) | (_cmp_cached_69))
            # 4h down move, 4h still high, 1d high
            & ((_cmp_cached_25) | (_cmp_cached_122) | (_cmp_cached_106))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_25) | (_cmp_cached_122) | (_cmp_cached_57))
            # 4h down move, 1h & 4h downtrend
            & ((_cmp_cached_25) | (_cmp_cached_239) | (_cmp_cached_213))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_100) | (_cmp_cached_104) | (_cmp_cached_74))
            # 4h & 1d down move, 15m high
            & ((_cmp_cached_100) | (_cmp_cached_178) | (_cmp_cached_180))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_100) | (_cmp_cached_73) | (_cmp_cached_39))
            # 4h down move, 15m high, 4h downtrend
            & ((_cmp_cached_100) | (_cmp_cached_76) | (_cmp_cached_103))
            # 4h down move, 4h high
            & ((_cmp_cached_100) | (_cmp_cached_6))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_100) | (_cmp_cached_106) | (_cmp_cached_216))
            # 4h down move, 1d high, 4h downtrend
            & ((_cmp_cached_100) | (_cmp_cached_94) | (_cmp_cached_204))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_100) | (_cmp_cached_94) | (_cmp_cached_52))
            # 4h down move, 15m high
            & ((_cmp_cached_100) | (_cmp_cached_92))
            # 4h down move, 4h still not low enough, 1d downtrend
            & ((_cmp_cached_100) | (_cmp_cached_124) | (_cmp_cached_57))
            # 4h down move, 4h & 1d downtrend
            & ((_cmp_cached_100) | (_cmp_cached_69) | (_cmp_cached_57))
            # 4h down move, 1d high, 4h downtrend
            & ((_cmp_cached_100) | (_cmp_cached_74) | (_cmp_cached_69))
            # 4h & 1d down move, 1h high
            & ((_cmp_cached_16) | (_cmp_cached_121) | (_cmp_cached_78))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_16) | (_cmp_cached_121) | (_cmp_cached_94))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_16) | (_cmp_cached_96) | (_cmp_cached_57))
            # 4h down move, 4h high, 1h downtrend
            & ((_cmp_cached_16) | (_cmp_cached_40) | (_cmp_cached_132))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_16) | (_cmp_cached_108) | (_cmp_cached_70))
            # 4h down move, 1d high, 4h downtrend
            & ((_cmp_cached_16) | (_cmp_cached_27) | (_cmp_cached_69))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_16) | (_cmp_cached_165) | (_cmp_cached_102))
            # 4h down move, 4h high, 1d downtrend
            & ((_cmp_cached_16) | (_cmp_cached_64) | (_cmp_cached_57))
            # 4h down move, 1d overbought
            & ((_cmp_cached_16) | (_cmp_cached_48))
            # 4h down move, 1h high, 4h downtrend
            & ((_cmp_cached_41) | (_cmp_cached_115) | (_cmp_cached_93))
            # 4h down move, 4h still high, 1d high
            & ((_cmp_cached_41) | (_cmp_cached_122) | (_cmp_cached_27))
            # 4h down move, 4h high, 1h downtrend
            & ((_cmp_cached_41) | (_cmp_cached_77) | (_cmp_cached_239))
            # 4h down move, 4h high
            & ((_cmp_cached_41) | (_cmp_cached_6))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_41) | (_cmp_cached_106) | (_cmp_cached_112))
            # 4h down move, 15m still high, 4h high
            & ((_cmp_cached_21) | (_cmp_cached_62) | (_cmp_cached_77))
            # 4h down move, 1h high
            & ((_cmp_cached_21) | (_cmp_cached_24))
            # 4h down move, 4h high, 1d downtrend
            & ((_cmp_cached_21) | (_cmp_cached_77) | (_cmp_cached_57))
            # 4h down move, 4h high, 1d overbought
            & ((_cmp_cached_21) | (_cmp_cached_77) | (_cmp_cached_70))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_21) | (_cmp_cached_27) | (_cmp_cached_167))
            # 4h down move, 4h still high, 1d overbought
            & ((_cmp_cached_21) | (_cmp_cached_35) | (_cmp_cached_111))
            # 4h down move, 4h & 1d high
            & ((_cmp_cached_181) | (_cmp_cached_17) | (_cmp_cached_27))
            # 4h down move, 4h high, 1d overbought
            & ((_cmp_cached_181) | (_cmp_cached_17) | (_cmp_cached_167))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_181) | (_cmp_cached_35) | (_cmp_cached_65))
            # 4h down move, 4h overbought, 1d downtrend
            & ((_cmp_cached_181) | (_cmp_cached_50) | (_cmp_cached_65))
            # 4h down move, 4h & 1d overbought
            & ((_cmp_cached_181) | (_cmp_cached_83) | (_cmp_cached_63))
            # 4h down move, 4h & 1d high
            & ((_cmp_cached_91) | (_cmp_cached_77) | (_cmp_cached_27))
            # 4h down move, 4h overbought
            & ((_cmp_cached_175) | (_cmp_cached_51))
            # 4h down move, 4h high & overbought
            & ((_cmp_cached_71) | (_cmp_cached_12) | (_cmp_cached_50))
            # 1d down move, 1d high, 1d downtrend
            & ((_cmp_cached_29) | (_cmp_cached_106) | (_cmp_cached_57))
            # 1d down move, 1d still high
            & ((_cmp_cached_29) | (_cmp_cached_56))
            # 1d down move, 4h & 1d downtrend
            & ((_cmp_cached_29) | (_cmp_cached_93) | (_cmp_cached_65))
            # 1d down move, 15m high
            & ((_cmp_cached_104) | (_cmp_cached_18))
            # 1d down move, 4h high, 4h downtrend
            & ((_cmp_cached_104) | (_cmp_cached_122) | (_cmp_cached_213))
            # 1d down move, 1d high, 1d downtrend
            & ((_cmp_cached_121) | (_cmp_cached_108) | (_cmp_cached_102))
            # 1d down move, 1d still high, 1d downtrend
            & ((_cmp_cached_121) | (_cmp_cached_14) | (_cmp_cached_57))
            # 1d down move, 4h & 1d high
            & ((_cmp_cached_178) | (_cmp_cached_46) | (_cmp_cached_94))
            # 1h & 4h downtrend, 4h high
            & ((_cmp_cached_240) | (_cmp_cached_200) | (_cmp_cached_77))
            # 4h & 1d downtrend, 1d high
            & ((_cmp_cached_193) | (_cmp_cached_275) | (_cmp_cached_131))
            # 15m & 1d high, 4h overbought
            & ((_cmp_cached_76) | (_cmp_cached_27) | (_cmp_cached_20))
            # 15m & 4h high, 1d downtrend
            & ((_cmp_cached_276) | (_cmp_cached_47) | (_cmp_cached_57))
            # 1h still high, 1h & 4h downtrend
            & ((_cmp_cached_26) | (_cmp_cached_129) | (_cmp_cached_103))
            # 1h & 4h high, 4h overbought
            & ((_cmp_cached_33) | (_cmp_cached_6) | (_cmp_cached_50))
            # 4h high, 4h & 1d downtrend
            & ((_cmp_cached_40) | (_cmp_cached_103) | (_cmp_cached_102))
            # 4h & 1d high, 4h overbought
            & ((_cmp_cached_17) | (_cmp_cached_27) | (_cmp_cached_51))
            # 4h & 1d high, 1d overbought
            & ((_cmp_cached_17) | (_cmp_cached_27) | (_cmp_cached_63))
            # 4h high, 4h & 1d overbought
            & ((_cmp_cached_46) | (_cmp_cached_50) | (_cmp_cached_95))
            # 1d high, 4h & 1d overbought
            & ((_cmp_cached_106) | (_cmp_cached_51) | (_cmp_cached_111))
            # 1d high, 4h downtrend, 1d overbought
            & ((_cmp_cached_131) | (_cmp_cached_69) | (_cmp_cached_111))
            # 1d high, 1h & 4h downtrend
            & ((_cmp_cached_27) | (_cmp_cached_109) | (_cmp_cached_103))
            # 1d high, 1h & 1d overbought
            & ((_cmp_cached_27) | (_cmp_cached_82) | (_cmp_cached_70))
            # 1d high, 4h & 1d overbought
            & ((_cmp_cached_27) | (_cmp_cached_51) | (_cmp_cached_112))
            # 15m still high, 1h & 4h downtrend
            & ((_cmp_cached_61) | (_cmp_cached_129) | (_cmp_cached_69))
            # 4h high, 1h & 4h overbought
            & ((_cmp_cached_72) | (_cmp_cached_79) | (_cmp_cached_51))
            # 4h high, 4h & 1d overbought
            & ((_cmp_cached_72) | (_cmp_cached_20) | (_cmp_cached_63))
            # 1d still high, 4h & 1d downtrend
            & ((_cmp_cached_14) | (_cmp_cached_103) | (_cmp_cached_102))
            # big drop in the last 20 days, 1d high, 1d downtrend
            & (
              (df["close"] > (df["high_max_20_1d"] * 0.20))
              | (_cmp_cached_148)
              | (_cmp_cached_149)
            )
          )

          # Logic
          long_entry_logic.append(
            (_cmp_cached_277)
            & (_cmp_cached_237)
            & (_cmp_cached_278)
            & (_cmp_cached_190)
            & (_cmp_cached_279)
            & (df["close_max_48"] >= (df["close"] * 1.10))
          )

        # Condition #43 - Quick mode (Long).
        if long_entry_condition_index == 43:
          # Protections
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          # long_entry_logic.append(df["protections_long_global"] == True)

          long_entry_logic.append(
            # 5m & 15m down move, 15m still high
            ((_cmp_cached_0) | (_cmp_cached_3) | (_cmp_cached_31))
            # 5m & 1h down move, 1h still not low enough
            & ((_cmp_cached_0) | (_cmp_cached_9) | (_cmp_cached_150))
            # 5m & 1h down move, 1h still not low enough
            & ((_cmp_cached_0) | (_cmp_cached_15) | (_cmp_cached_161))
            # 5m & 1h down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_117) | (_cmp_cached_162))
            # 5m & 1d down move, 1d still not low enough
            & ((_cmp_cached_0) | (_cmp_cached_29) | (_cmp_cached_269))
            # 5m down move, 1h & 4h high
            & ((_cmp_cached_0) | (_cmp_cached_33) | (_cmp_cached_6))
            # 5m down move, 4h high & overbought
            & ((_cmp_cached_0) | (_cmp_cached_6) | (_cmp_cached_20))
            # 5m down move, 1h high, 4h overbought
            & ((_cmp_cached_0) | (_cmp_cached_19) | (_cmp_cached_20))
            # 5m down move, 1d high & overbought
            & ((_cmp_cached_0) | (_cmp_cached_39) | (_cmp_cached_167))
            # 5m & 1h down move, 1d overbought
            & ((_cmp_cached_8) | (_cmp_cached_11) | (_cmp_cached_48))
            # 5m & 1d down move, 1h high
            & ((_cmp_cached_8) | (_cmp_cached_104) | (_cmp_cached_78))
            # 5m & 1h down move, 1h high
            & ((_cmp_cached_157) | (_cmp_cached_15) | (_cmp_cached_45))
            # 15m & 1h down move
            & ((_cmp_cached_1) | (_cmp_cached_13))
            # 15m & 1h & 4h down move
            & ((_cmp_cached_1) | (_cmp_cached_7) | (_cmp_cached_58))
            # 15m & 1h & 1d down move
            & ((_cmp_cached_1) | (_cmp_cached_9) | (_cmp_cached_121))
            # 15m & 1h down move, 1d still high
            & ((_cmp_cached_1) | (_cmp_cached_9) | (_cmp_cached_170))
            # 15m & 1h down move, 15m still high
            & ((_cmp_cached_1) | (_cmp_cached_9) | (_cmp_cached_62))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_1) | (_cmp_cached_9) | (_cmp_cached_106))
            # 15m & 1d down move, 1d overbought
            & ((_cmp_cached_1) | (_cmp_cached_9) | (_cmp_cached_95))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_1) | (_cmp_cached_15) | (_cmp_cached_110))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_1) | (_cmp_cached_15) | (_cmp_cached_94))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_1) | (_cmp_cached_15) | (_cmp_cached_17))
            # 15m & 1h down move, 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_15) | (_cmp_cached_102))
            # 15m & 1h down move, 15m high
            & ((_cmp_cached_1) | (_cmp_cached_30) | (_cmp_cached_76))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_1) | (_cmp_cached_32) | (_cmp_cached_80))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_1) | (_cmp_cached_32) | (_cmp_cached_39))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_1) | (_cmp_cached_32) | (_cmp_cached_111))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_1) | (_cmp_cached_34) | (_cmp_cached_28))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_1) | (_cmp_cached_38) | (_cmp_cached_46))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_1) | (_cmp_cached_25) | (_cmp_cached_238))
            # 15m & 4h down move, 15m high
            & ((_cmp_cached_1) | (_cmp_cached_100) | (_cmp_cached_76))
            # 15m & 4h down move, 1d overbought
            & ((_cmp_cached_1) | (_cmp_cached_21) | (_cmp_cached_112))
            # 15m & 1d down move, 1d still high
            & ((_cmp_cached_1) | (_cmp_cached_153) | (_cmp_cached_119))
            # 15m & 1d down move, 4h still high
            & ((_cmp_cached_1) | (_cmp_cached_104) | (_cmp_cached_35))
            # 15m & 1d down move, 1d high
            & ((_cmp_cached_1) | (_cmp_cached_198) | (_cmp_cached_106))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_1) | (_cmp_cached_46) | (_cmp_cached_196))
            # 15m down move, 1d high & overbought
            & ((_cmp_cached_1) | (_cmp_cached_27) | (_cmp_cached_52))
            # 15m down move, 1h high, 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_19) | (_cmp_cached_57))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_1) | (_cmp_cached_12) | (_cmp_cached_113))
            # 15m down move, 4h high, 1d overbought
            & ((_cmp_cached_1) | (_cmp_cached_12) | (_cmp_cached_95))
            # 15m down move, 1h downtrend, 4h overbought
            & ((_cmp_cached_1) | (_cmp_cached_109) | (_cmp_cached_196))
            # 15m down move, 4h & 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_280) | (_cmp_cached_206))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_3) | (_cmp_cached_7) | (_cmp_cached_169))
            # 15m & 1h down move, 1h still not low enough
            & ((_cmp_cached_3) | (_cmp_cached_15) | (_cmp_cached_190))
            # 15m & 1h down move, 1d still high
            & ((_cmp_cached_3) | (_cmp_cached_30) | (_cmp_cached_14))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_3) | (_cmp_cached_11) | (_cmp_cached_216))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_32) | (_cmp_cached_17))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_38) | (_cmp_cached_33))
            # 15m & 4h down move, 1h still high
            & ((_cmp_cached_3) | (_cmp_cached_58) | (_cmp_cached_59))
            # 15m & 4h down move, 1h downtrend
            & ((_cmp_cached_3) | (_cmp_cached_58) | (_cmp_cached_129))
            # 15m & 4h down move, 15m still high
            & ((_cmp_cached_3) | (_cmp_cached_25) | (_cmp_cached_61))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_3) | (_cmp_cached_100) | (_cmp_cached_122))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_3) | (_cmp_cached_100) | (_cmp_cached_106))
            # 15m & 1d down move, 1h still high
            & ((_cmp_cached_3) | (_cmp_cached_104) | (_cmp_cached_59))
            # 15m down move, 15m & 1h still high
            & ((_cmp_cached_3) | (_cmp_cached_31) | (_cmp_cached_26))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_3) | (_cmp_cached_33) | (_cmp_cached_6))
            # 15m down move, 1h high, 4h overbought
            & ((_cmp_cached_3) | (_cmp_cached_33) | (_cmp_cached_50))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_3) | (_cmp_cached_77) | (_cmp_cached_86))
            # 15m down move, 1d still high, 1d downtrend
            & ((_cmp_cached_3) | (_cmp_cached_14) | (_cmp_cached_57))
            # 15m down move, 1d downtrend
            & ((_cmp_cached_3) | (_cmp_cached_194))
            # 15m & 1h down move, 15m high
            & ((_cmp_cached_5) | (_cmp_cached_9) | (_cmp_cached_76))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_5) | (_cmp_cached_15) | (_cmp_cached_28))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_15) | (_cmp_cached_39))
            # 15m & 1h down move, 4h downtrend
            & ((_cmp_cached_5) | (_cmp_cached_15) | (_cmp_cached_69))
            # 15m & 1h down move, 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_15) | (_cmp_cached_65))
            # 15m & 1h down move, 15m still high
            & ((_cmp_cached_5) | (_cmp_cached_30) | (_cmp_cached_62))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_5) | (_cmp_cached_30) | (_cmp_cached_24))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_30) | (_cmp_cached_108))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_30) | (_cmp_cached_63))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_11) | (_cmp_cached_46))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_11) | (_cmp_cached_12))
            # 15m & 1h down move, 4h overbought
            & ((_cmp_cached_5) | (_cmp_cached_11) | (_cmp_cached_20))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_5) | (_cmp_cached_32) | (_cmp_cached_123))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_36) | (_cmp_cached_94))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_5) | (_cmp_cached_36) | (_cmp_cached_49))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_117) | (_cmp_cached_72))
            # 15m & 4h down move, 15m still high
            & ((_cmp_cached_5) | (_cmp_cached_58) | (_cmp_cached_155))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_5) | (_cmp_cached_58) | (_cmp_cached_165))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_5) | (_cmp_cached_25) | (_cmp_cached_49))
            # 15m & 4h down move, 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_25) | (_cmp_cached_57))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_5) | (_cmp_cached_181) | (_cmp_cached_122))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_99) | (_cmp_cached_17))
            # 15m & 1d down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_104) | (_cmp_cached_64))
            # 15m down move, 15m still high, 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_31) | (_cmp_cached_102))
            # 15m down move, 15m still high, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_62) | (_cmp_cached_70))
            # 15m down move, 15m high, 1h high
            & ((_cmp_cached_5) | (_cmp_cached_210) | (_cmp_cached_33))
            # 15m down move, 15m high, 4h downtrend
            & ((_cmp_cached_5) | (_cmp_cached_210) | (_cmp_cached_93))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_5) | (_cmp_cached_78) | (_cmp_cached_6))
            # 15m down move, 1h high, 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_78) | (_cmp_cached_65))
            # 15m down move, 4h & 1d high
            & ((_cmp_cached_5) | (_cmp_cached_46) | (_cmp_cached_27))
            # 15m down move, 1d high & overbought
            & ((_cmp_cached_5) | (_cmp_cached_27) | (_cmp_cached_48))
            # 15m down move, 4h still high, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_35) | (_cmp_cached_70))
            # 15m down move, 4h & 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_50) | (_cmp_cached_111))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_84) | (_cmp_cached_15) | (_cmp_cached_78))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_84) | (_cmp_cached_15) | (_cmp_cached_39))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_84) | (_cmp_cached_30) | (_cmp_cached_80))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_84) | (_cmp_cached_30) | (_cmp_cached_6))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_84) | (_cmp_cached_181) | (_cmp_cached_17))
            # 15m down move. 15m still high, 1h high
            & ((_cmp_cached_84) | (_cmp_cached_62) | (_cmp_cached_19))
            # 15m down move, 15m & 4h high
            & ((_cmp_cached_84) | (_cmp_cached_76) | (_cmp_cached_6))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_84) | (_cmp_cached_33) | (_cmp_cached_52))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_84) | (_cmp_cached_40) | (_cmp_cached_51))
            # 15m down move, 4h high, 1d overbought
            & ((_cmp_cached_84) | (_cmp_cached_17) | (_cmp_cached_111))
            # 15m down move, 4h high, 1d overbought
            & ((_cmp_cached_84) | (_cmp_cached_6) | (_cmp_cached_48))
            # 15m down move, 1h high, 4h downtrend
            & ((_cmp_cached_84) | (_cmp_cached_37) | (_cmp_cached_103))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_84) | (_cmp_cached_72) | (_cmp_cached_211))
            # 15m down move, 4h high, 1d downtrend
            & ((_cmp_cached_84) | (_cmp_cached_72) | (_cmp_cached_65))
            # 15m down move, 4h high, 1d overbought
            & ((_cmp_cached_84) | (_cmp_cached_72) | (_cmp_cached_70))
            # 15m down move, 1d high & overbought
            & ((_cmp_cached_84) | (_cmp_cached_39) | (_cmp_cached_48))
            # 15m down move, 4h & 1d downtrend
            & ((_cmp_cached_84) | (_cmp_cached_93) | (_cmp_cached_65))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_87) | (_cmp_cached_30) | (_cmp_cached_12))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_87) | (_cmp_cached_11) | (_cmp_cached_48))
            # 15m & 1d down move, 4h high
            & ((_cmp_cached_87) | (_cmp_cached_104) | (_cmp_cached_46))
            # 15m down move, 15m & 1h high
            & ((_cmp_cached_87) | (_cmp_cached_76) | (_cmp_cached_80))
            # 15m down move, 1h high, 4h overbought
            & ((_cmp_cached_87) | (_cmp_cached_33) | (_cmp_cached_50))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_87) | (_cmp_cached_33) | (_cmp_cached_95))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_87) | (_cmp_cached_77) | (_cmp_cached_50))
            # 15m & 1h down move, 15m high
            & ((_cmp_cached_88) | (_cmp_cached_11) | (_cmp_cached_92))
            # 15m & 1h down move, 1h downtrend
            & ((_cmp_cached_88) | (_cmp_cached_11) | (_cmp_cached_109))
            # 15m down move, 1d high & overbought
            & ((_cmp_cached_89) | (_cmp_cached_27) | (_cmp_cached_107))
            # 1h & 4h down move, 1d still high
            & ((_cmp_cached_13) | (_cmp_cached_58) | (_cmp_cached_56))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_13) | (_cmp_cached_25) | (_cmp_cached_96))
            # 1h & 4h down move, 1d still high
            & ((_cmp_cached_13) | (_cmp_cached_25) | (_cmp_cached_119))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_13) | (_cmp_cached_100) | (_cmp_cached_199))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_13) | (_cmp_cached_16) | (_cmp_cached_106))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_13) | (_cmp_cached_16) | (_cmp_cached_167))
            # 1h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_13) | (_cmp_cached_35) | (_cmp_cached_57))
            # 1h & 4h down move, 1h still high
            & ((_cmp_cached_7) | (_cmp_cached_58) | (_cmp_cached_26))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_7) | (_cmp_cached_25) | (_cmp_cached_39))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_7) | (_cmp_cached_100) | (_cmp_cached_27))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_7) | (_cmp_cached_21) | (_cmp_cached_169))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_7) | (_cmp_cached_17) | (_cmp_cached_102))
            # 1h down move, 1d high, 1h downtrend
            & ((_cmp_cached_7) | (_cmp_cached_94) | (_cmp_cached_239))
            # 1h down move, 4h & 1d downtrend
            & ((_cmp_cached_7) | (_cmp_cached_69) | (_cmp_cached_57))
            # 1h & 4h & 1d down move
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_29))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_57))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_9) | (_cmp_cached_25) | (_cmp_cached_115))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_9) | (_cmp_cached_25) | (_cmp_cached_94))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_9) | (_cmp_cached_25) | (_cmp_cached_102))
            # 1h & 1d down move, 4h high
            & ((_cmp_cached_9) | (_cmp_cached_29) | (_cmp_cached_64))
            # 1h & 1d down move, 1d still high
            & ((_cmp_cached_9) | (_cmp_cached_178) | (_cmp_cached_14))
            # 1h down move, 15m downtrend, 1d high
            & ((_cmp_cached_9) | (_cmp_cached_43) | (_cmp_cached_106))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_9) | (_cmp_cached_33) | (_cmp_cached_50))
            # 1h down move, 1d high, 1d downtrend
            & ((_cmp_cached_9) | (_cmp_cached_106) | (_cmp_cached_57))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_9) | (_cmp_cached_162) | (_cmp_cached_102))
            # 1h & 4h down move, 1h still not low enough
            & ((_cmp_cached_15) | (_cmp_cached_25) | (_cmp_cached_188))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_15) | (_cmp_cached_25) | (_cmp_cached_40))
            # 1h & 4h down move, 1h downtrend
            & ((_cmp_cached_15) | (_cmp_cached_25) | (_cmp_cached_130))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_15) | (_cmp_cached_25) | (_cmp_cached_95))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_15) | (_cmp_cached_100) | (_cmp_cached_169))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_15) | (_cmp_cached_41) | (_cmp_cached_24))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_15) | (_cmp_cached_181) | (_cmp_cached_106))
            # 1h & 1d down move, 1d still high
            & ((_cmp_cached_15) | (_cmp_cached_121) | (_cmp_cached_238))
            # 1h down move, 1h still high, 1d downtrend
            & ((_cmp_cached_15) | (_cmp_cached_150) | (_cmp_cached_102))
            # 1h down move, 1h still high, 4h downtrend
            & ((_cmp_cached_15) | (_cmp_cached_110) | (_cmp_cached_103))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_15) | (_cmp_cached_77) | (_cmp_cached_50))
            # 1h & 4h down move, 1h still high
            & ((_cmp_cached_30) | (_cmp_cached_41) | (_cmp_cached_59))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_30) | (_cmp_cached_99) | (_cmp_cached_172))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_30) | (_cmp_cached_24) | (_cmp_cached_50))
            # 1h down move, 1h high & overbought
            & ((_cmp_cached_30) | (_cmp_cached_27) | (_cmp_cached_48))
            # 1h down move, 4h downtrend, 1d overbought
            & ((_cmp_cached_30) | (_cmp_cached_213) | (_cmp_cached_107))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_11) | (_cmp_cached_41) | (_cmp_cached_108))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_41) | (_cmp_cached_167))
            # 1h & 1d down move, 1h high
            & ((_cmp_cached_11) | (_cmp_cached_121) | (_cmp_cached_33))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_11) | (_cmp_cached_115) | (_cmp_cached_65))
            # 1h down move, 1h & 1d high
            & ((_cmp_cached_11) | (_cmp_cached_24) | (_cmp_cached_94))
            # 1h down move, 1h high & overbought
            & ((_cmp_cached_11) | (_cmp_cached_33) | (_cmp_cached_82))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_11) | (_cmp_cached_33) | (_cmp_cached_86))
            # 1h down move, 4h & 1d high
            & ((_cmp_cached_11) | (_cmp_cached_46) | (_cmp_cached_27))
            # 1h down move, 1d high, 4h downtrend
            & ((_cmp_cached_11) | (_cmp_cached_108) | (_cmp_cached_280))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_11) | (_cmp_cached_12) | (_cmp_cached_102))
            # 1h down move, 4h & 1d downtrend
            & ((_cmp_cached_11) | (_cmp_cached_103) | (_cmp_cached_194))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_32) | (_cmp_cached_181) | (_cmp_cached_24))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_32) | (_cmp_cached_33) | (_cmp_cached_95))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_32) | (_cmp_cached_17) | (_cmp_cached_52))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_32) | (_cmp_cached_77) | (_cmp_cached_51))
            # 1h down move, 1d high, 4h downtrend
            & ((_cmp_cached_32) | (_cmp_cached_94) | (_cmp_cached_213))
            # 1h down move, 1d high, 4h overbought
            & ((_cmp_cached_32) | (_cmp_cached_27) | (_cmp_cached_51))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_32) | (_cmp_cached_51) | (_cmp_cached_111))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_34) | (_cmp_cached_21) | (_cmp_cached_94))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_34) | (_cmp_cached_78) | (_cmp_cached_63))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_34) | (_cmp_cached_80) | (_cmp_cached_6))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_34) | (_cmp_cached_27) | (_cmp_cached_111))
            # 1h down move, 1h high, 4h downtrend
            & ((_cmp_cached_34) | (_cmp_cached_37) | (_cmp_cached_69))
            # 1h & 1d down move, 1h high
            & ((_cmp_cached_36) | (_cmp_cached_125) | (_cmp_cached_78))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_36) | (_cmp_cached_33) | (_cmp_cached_102))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_36) | (_cmp_cached_77) | (_cmp_cached_52))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_36) | (_cmp_cached_46) | (_cmp_cached_20))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_36) | (_cmp_cached_19) | (_cmp_cached_20))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_36) | (_cmp_cached_12) | (_cmp_cached_20))
            # 1h down move, 1d high, 4h overbought
            & ((_cmp_cached_38) | (_cmp_cached_27) | (_cmp_cached_113))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_117) | (_cmp_cached_115) | (_cmp_cached_206))
            # 1h down move, 1h & 1d high
            & ((_cmp_cached_117) | (_cmp_cached_33) | (_cmp_cached_27))
            # 4h & 1d down move, 15m still high
            & ((_cmp_cached_151) | (_cmp_cached_29) | (_cmp_cached_155))
            # 4h & 1d down move, 1h still not low enough
            & ((_cmp_cached_151) | (_cmp_cached_29) | (_cmp_cached_161))
            # 4h down move, 4h still high
            & ((_cmp_cached_151) | (_cmp_cached_122))
            # 4h down move, 1h still high, 4h downtrend
            & ((_cmp_cached_151) | (_cmp_cached_59) | (_cmp_cached_103))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_55) | (_cmp_cached_178) | (_cmp_cached_56))
            # 4h down move, 1h & 4h downtrend
            & ((_cmp_cached_55) | (_cmp_cached_132) | (_cmp_cached_93))
            # 4h & 1d down move, 4h downtrend
            & ((_cmp_cached_58) | (_cmp_cached_153) | (_cmp_cached_69))
            # 4h & 1d down move, 1d downtrend
            & ((_cmp_cached_58) | (_cmp_cached_153) | (_cmp_cached_102))
            # 4h down move, 4h still high
            & ((_cmp_cached_58) | (_cmp_cached_122))
            # 4h down move, 1d still high, 1d downtrend
            & ((_cmp_cached_58) | (_cmp_cached_238) | (_cmp_cached_102))
            # 4h down move, 4h still not low enough, 1d downtrend
            & ((_cmp_cached_58) | (_cmp_cached_124) | (_cmp_cached_57))
            # 4h down move, 4h & 1d  downtrend
            & ((_cmp_cached_58) | (_cmp_cached_69) | (_cmp_cached_102))
            # 4h down move, 1h still high
            & ((_cmp_cached_25) | (_cmp_cached_26))
            # 4h down move, 1h still high, 1d downtrend
            & ((_cmp_cached_25) | (_cmp_cached_59) | (_cmp_cached_102))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_25) | (_cmp_cached_35) | (_cmp_cached_57))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_100) | (_cmp_cached_122) | (_cmp_cached_65))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_100) | (_cmp_cached_106) | (_cmp_cached_107))
            # 4h & 1d down move, 1h high
            & ((_cmp_cached_16) | (_cmp_cached_121) | (_cmp_cached_78))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_41) | (_cmp_cached_122) | (_cmp_cached_65))
            # 4h down move, 1d high, 1d downtrend
            & ((_cmp_cached_21) | (_cmp_cached_60) | (_cmp_cached_102))
            # 4h down move, 1d high, 1d downtrend
            & ((_cmp_cached_91) | (_cmp_cached_108) | (_cmp_cached_149))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_99) | (_cmp_cached_169) | (_cmp_cached_102))
            # 1d down move, 4h high, 1d downtrend
            & ((_cmp_cached_29) | (_cmp_cached_64) | (_cmp_cached_206))
            # 1d down move, 1h high & overbought
            & ((_cmp_cached_192) | (_cmp_cached_49) | (_cmp_cached_82))
            # 1d down move, 1h high & overbought
            & ((_cmp_cached_125) | (_cmp_cached_106) | (_cmp_cached_63))
            # 4h downtrend, 1h & 4h high
            & ((_cmp_cached_189) | (_cmp_cached_24) | (_cmp_cached_6))
            # 15m still high, 1h & 4h overbought
            & ((_cmp_cached_62) | (_cmp_cached_182) | (_cmp_cached_196))
            # 15m & 1d high, 1d overbought
            & ((_cmp_cached_76) | (_cmp_cached_94) | (_cmp_cached_70))
            # 1h still high, 4h & 1d downtrend
            & ((_cmp_cached_110) | (_cmp_cached_69) | (_cmp_cached_65))
            # 1h & 4h high, 1d downtrend
            & ((_cmp_cached_24) | (_cmp_cached_6) | (_cmp_cached_57))
            # 1h & 4h high, 1d overbought
            & ((_cmp_cached_24) | (_cmp_cached_6) | (_cmp_cached_167))
            # 1h & 1d high, 1d overbought
            & ((_cmp_cached_24) | (_cmp_cached_94) | (_cmp_cached_111))
            # 1h high, 4h downtrend, 1d overbought
            & ((_cmp_cached_24) | (_cmp_cached_213) | (_cmp_cached_48))
            # 1h & 4h high, 4h overbought
            & ((_cmp_cached_33) | (_cmp_cached_6) | (_cmp_cached_51))
            # 1h high, 1d downtrend
            & ((_cmp_cached_33) | (_cmp_cached_194))
            # 1h high, 1h & 4h overbought
            & ((_cmp_cached_80) | (_cmp_cached_182) | (_cmp_cached_196))
            # 4h & 1d high, 1d overbought
            & ((_cmp_cached_40) | (_cmp_cached_27) | (_cmp_cached_216))
            # 4h high, 1h & 4h overbought
            & ((_cmp_cached_47) | (_cmp_cached_242) | (_cmp_cached_67))
            # 4h high, 1h downtrend, 4h overbought
            & ((_cmp_cached_46) | (_cmp_cached_239) | (_cmp_cached_196))
            # 4h & 1d high, 4h overbought
            & ((_cmp_cached_46) | (_cmp_cached_27) | (_cmp_cached_196))
            # 4h high, 1h & 4h overbought
            & ((_cmp_cached_46) | (_cmp_cached_82) | (_cmp_cached_20))
            # 4h & 1d high, 4h overbought
            & ((_cmp_cached_6) | (_cmp_cached_27) | (_cmp_cached_51))
            # 4h & 1d high, 1d overbought
            & ((_cmp_cached_6) | (_cmp_cached_27) | (_cmp_cached_52))
            # 1d high, 1h & 4h downtrend
            & ((_cmp_cached_27) | (_cmp_cached_109) | (_cmp_cached_103))
            # 1d high, 4h & 1d overbought
            & ((_cmp_cached_27) | (_cmp_cached_20) | (_cmp_cached_48))
            # 1h high, 1d overbought
            & ((_cmp_cached_37) | (_cmp_cached_52))
            # 1h high, 4h overbought
            & ((_cmp_cached_19) | (_cmp_cached_67))
            # 1h high, 4h & 1d downtrend
            & ((_cmp_cached_281) | (_cmp_cached_280) | (_cmp_cached_206))
            # 4h high, 1h & 4h overbought
            & ((_cmp_cached_12) | (_cmp_cached_54) | (_cmp_cached_196))
            # 1d high, 4h & 1d overbought
            & ((_cmp_cached_39) | (_cmp_cached_20) | (_cmp_cached_48))
            # 1h & 4h overbought, 1d downtrend
            & ((_cmp_cached_54) | (_cmp_cached_86) | (_cmp_cached_102))
            # big drop in the last 20 days, 1d high, 1d downtrend
            & (
              (df["close"] > (df["high_max_20_1d"] * 0.20))
              | (_cmp_cached_148)
              | (_cmp_cached_149)
            )
          )

          # Logic
          long_entry_logic.append(
            (_cmp_cached_282)
            & (_cmp_cached_283)
            & (_cmp_cached_243)
            & (df["EMA_26"] > df["EMA_12"])
            & ((df["EMA_26"] - df["EMA_12"]) > (df["open"] * 0.024))
            & ((df["EMA_26"].shift() - df["EMA_12"].shift()) > (df["open"] / 100.0))
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
            ((_cmp_cached_0) | (_cmp_cached_15) | (_cmp_cached_25))
            # 15m & 1h & 4h down move
            & ((_cmp_cached_1) | (_cmp_cached_13) | (_cmp_cached_58))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_1) | (_cmp_cached_13) | (_cmp_cached_115))
            # 15m & 1h & 4h down move
            & ((_cmp_cached_1) | (_cmp_cached_7) | (_cmp_cached_58))
            # 15m & 1h down move, 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_7) | (_cmp_cached_102))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_1) | (_cmp_cached_9) | (_cmp_cached_27))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_1) | (_cmp_cached_30) | (_cmp_cached_33))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_1) | (_cmp_cached_58) | (_cmp_cached_96))
            # 15m & 4h down move, 15m downtrend
            & ((_cmp_cached_1) | (_cmp_cached_58) | (_cmp_cached_187))
            # 15m & 4h down move, 1h downtrend
            & ((_cmp_cached_1) | (_cmp_cached_58) | (_cmp_cached_129))
            # 15m & 4h down move, 1h still high
            & ((_cmp_cached_1) | (_cmp_cached_25) | (_cmp_cached_26))
            # 15m & 4h down move, 1h still high
            & ((_cmp_cached_1) | (_cmp_cached_181) | (_cmp_cached_28))
            # 15m down move, 1h still high, 1d overbought
            & ((_cmp_cached_1) | (_cmp_cached_110) | (_cmp_cached_216))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_1) | (_cmp_cached_6) | (_cmp_cached_196))
            # 15m down move, 1h high
            & ((_cmp_cached_1) | (_cmp_cached_37))
            # 15m down move, 4h high, 15m downtrend
            & ((_cmp_cached_1) | (_cmp_cached_64) | (_cmp_cached_187))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_15) | (_cmp_cached_24))
            # 15m & 1h down move, 1h downtrend
            & ((_cmp_cached_5) | (_cmp_cached_9) | (_cmp_cached_129))
            # 15m & 4h down move, 1h still not low enough
            & ((_cmp_cached_5) | (_cmp_cached_58) | (_cmp_cached_161))
            # 15m down move, 4h overbought
            & ((_cmp_cached_5) | (_cmp_cached_51))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_84) | (_cmp_cached_16) | (_cmp_cached_17))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_84) | (_cmp_cached_181) | (_cmp_cached_172))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_84) | (_cmp_cached_91) | (_cmp_cached_46))
            # 15m down move, 4h & 1d downtrend
            & ((_cmp_cached_84) | (_cmp_cached_93) | (_cmp_cached_65))
            # 15m down move, 1h high & overbought
            & ((_cmp_cached_88) | (_cmp_cached_94) | (_cmp_cached_48))
            # 1h & 4h down move, 1h still not low enough
            & ((_cmp_cached_13) | (_cmp_cached_151) | (_cmp_cached_188))
            # 1h & 4h down move
            & ((_cmp_cached_13) | (_cmp_cached_55))
            # 1h & 4h down move, 1d still high
            & ((_cmp_cached_13) | (_cmp_cached_58) | (_cmp_cached_238))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_13) | (_cmp_cached_58) | (_cmp_cached_60))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_13) | (_cmp_cached_100) | (_cmp_cached_199))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_13) | (_cmp_cached_100) | (_cmp_cached_162))
            # 1h down move, 1h & 4h still high
            & ((_cmp_cached_13) | (_cmp_cached_26) | (_cmp_cached_122))
            # 1h down move, 1h still high, 1h downtrend
            & ((_cmp_cached_13) | (_cmp_cached_26) | (_cmp_cached_129))
            # 1h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_13) | (_cmp_cached_35) | (_cmp_cached_130))
            # 1h downtrend, 4h high
            & ((_cmp_cached_13) | (_cmp_cached_64))
            # 1h down move, 1h & 4h downtrend
            & ((_cmp_cached_13) | (_cmp_cached_129) | (_cmp_cached_69))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_7) | (_cmp_cached_58) | (_cmp_cached_122))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_7) | (_cmp_cached_58) | (_cmp_cached_39))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_7) | (_cmp_cached_41) | (_cmp_cached_169))
            # 1h & 1d down move, 1d downtrend
            & ((_cmp_cached_7) | (_cmp_cached_101) | (_cmp_cached_57))
            # 1h down move, 1h high
            & ((_cmp_cached_7) | (_cmp_cached_115))
            # 1h down move, 4h high
            & ((_cmp_cached_7) | (_cmp_cached_17))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_7) | (_cmp_cached_94) | (_cmp_cached_70))
            # 1h down move, 4h & 1d downtrend
            & ((_cmp_cached_7) | (_cmp_cached_69) | (_cmp_cached_195))
            # 1h down move, 1d overbought
            & ((_cmp_cached_7) | (_cmp_cached_48))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_57))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_9) | (_cmp_cached_25) | (_cmp_cached_169))
            # 1h & 4h down move, 1h still high
            & ((_cmp_cached_9) | (_cmp_cached_25) | (_cmp_cached_26))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_9) | (_cmp_cached_100) | (_cmp_cached_35))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_9) | (_cmp_cached_100) | (_cmp_cached_65))
            # 1h & 4h down move, 1h downtrend
            & ((_cmp_cached_9) | (_cmp_cached_100) | (_cmp_cached_135))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_9) | (_cmp_cached_16) | (_cmp_cached_17))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_9) | (_cmp_cached_71) | (_cmp_cached_24))
            # 1h & 1d down move, 4h still high
            & ((_cmp_cached_9) | (_cmp_cached_153) | (_cmp_cached_96))
            # 1h & 1d down move, 1h still high
            & ((_cmp_cached_9) | (_cmp_cached_29) | (_cmp_cached_26))
            # 1h & 1d down move, 1h high
            & ((_cmp_cached_9) | (_cmp_cached_125) | (_cmp_cached_24))
            # 1h down move, 1h still high, 4h downtrend
            & ((_cmp_cached_9) | (_cmp_cached_110) | (_cmp_cached_103))
            # 1h down move, 1h still high, 1d high
            & ((_cmp_cached_9) | (_cmp_cached_26) | (_cmp_cached_94))
            # 1h down move, 1h high, 1h downtrend
            & ((_cmp_cached_9) | (_cmp_cached_115) | (_cmp_cached_132))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_9) | (_cmp_cached_24) | (_cmp_cached_102))
            # 1h down move, 1h high
            & ((_cmp_cached_9) | (_cmp_cached_33))
            # 1h down move, 4h still high, 15m downtrend
            & ((_cmp_cached_9) | (_cmp_cached_122) | (_cmp_cached_43))
            # 1h down move, 4h still high, 4h downtrend
            & ((_cmp_cached_9) | (_cmp_cached_122) | (_cmp_cached_103))
            # 1h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_9) | (_cmp_cached_122) | (_cmp_cached_102))
            # 1h down move, 4h & 1d high
            & ((_cmp_cached_9) | (_cmp_cached_40) | (_cmp_cached_27))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_9) | (_cmp_cached_46) | (_cmp_cached_48))
            # 1h down move, 4h high
            & ((_cmp_cached_9) | (_cmp_cached_6))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_9) | (_cmp_cached_27) | (_cmp_cached_112))
            # 1h down move, 4h overbought
            & ((_cmp_cached_9) | (_cmp_cached_50))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_9) | (_cmp_cached_12) | (_cmp_cached_20))
            # 1h down move, 4h & 1d downtrend
            & ((_cmp_cached_9) | (_cmp_cached_103) | (_cmp_cached_42))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_15) | (_cmp_cached_91) | (_cmp_cached_77))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_15) | (_cmp_cached_26) | (_cmp_cached_65))
            # 1h down move, 1h & 1d high
            & ((_cmp_cached_15) | (_cmp_cached_115) | (_cmp_cached_131))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_15) | (_cmp_cached_115) | (_cmp_cached_102))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_15) | (_cmp_cached_115) | (_cmp_cached_107))
            # 1h down move, 1h high, 4h downtrend
            & ((_cmp_cached_15) | (_cmp_cached_24) | (_cmp_cached_93))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_15) | (_cmp_cached_77) | (_cmp_cached_196))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_15) | (_cmp_cached_108) | (_cmp_cached_48))
            # 1h down move, 1h & 4h downtrend
            & ((_cmp_cached_15) | (_cmp_cached_109) | (_cmp_cached_103))
            # 1h down move, 1h & 4h overbought
            & ((_cmp_cached_15) | (_cmp_cached_50) | (_cmp_cached_107))
            # 1h down move, 1h & 4h overbought
            & ((_cmp_cached_15) | (_cmp_cached_20) | (_cmp_cached_167))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_30) | (_cmp_cached_99) | (_cmp_cached_46))
            # 1h down move, 1h still high, 4h downtrend
            & ((_cmp_cached_30) | (_cmp_cached_110) | (_cmp_cached_103))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_30) | (_cmp_cached_12) | (_cmp_cached_65))
            # 1h down move, 4h & 1d downtrend
            & ((_cmp_cached_30) | (_cmp_cached_103) | (_cmp_cached_65))
            # 1h & 4h down ove, 4h high
            & ((_cmp_cached_11) | (_cmp_cached_91) | (_cmp_cached_46))
            # 1h down move, 1h & 1d high
            & ((_cmp_cached_11) | (_cmp_cached_24) | (_cmp_cached_108))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_11) | (_cmp_cached_77) | (_cmp_cached_57))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_11) | (_cmp_cached_94) | (_cmp_cached_48))
            # 1h down move, 1h still high, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_59) | (_cmp_cached_52))
            # 1h down move, 1h downtrend, 4h overbought
            & ((_cmp_cached_11) | (_cmp_cached_129) | (_cmp_cached_20))
            # 1h down move, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_111))
            # 1h down move, 4h high
            & ((_cmp_cached_32) | (_cmp_cached_6))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_32) | (_cmp_cached_12) | (_cmp_cached_50))
            # 4h down move, 4h still high, 1d high
            & ((_cmp_cached_151) | (_cmp_cached_122) | (_cmp_cached_27))
            # 4h down move, 1d still high, 4h downtrend
            & ((_cmp_cached_151) | (_cmp_cached_14) | (_cmp_cached_103))
            # 4h down move, 1d overbought
            & ((_cmp_cached_151) | (_cmp_cached_111))
            # 4h down move, 1h still high
            & ((_cmp_cached_55) | (_cmp_cached_28))
            # 4h down move, 1h & 4h downtrend
            & ((_cmp_cached_55) | (_cmp_cached_130) | (_cmp_cached_69))
            # 4h down move, 4h downtrend
            & ((_cmp_cached_55) | (_cmp_cached_213))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_58) | (_cmp_cached_104) | (_cmp_cached_108))
            # 4h down move, 1d high, 4h downtrend
            & ((_cmp_cached_58) | (_cmp_cached_94) | (_cmp_cached_69))
            # 4h down move, 1h & 4h downtrend
            & ((_cmp_cached_58) | (_cmp_cached_109) | (_cmp_cached_103))
            # 4h down move, 4h still not low enough, 1d overbought
            & ((_cmp_cached_25) | (_cmp_cached_98) | (_cmp_cached_107))
            # 4h down move, 4h high
            & ((_cmp_cached_25) | (_cmp_cached_40))
            # 4h down move, 4h still high, 1d overbought
            & ((_cmp_cached_25) | (_cmp_cached_96) | (_cmp_cached_52))
            # 15m down move, 4h still high, 1d downtrend
            & ((_cmp_cached_25) | (_cmp_cached_122) | (_cmp_cached_65))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_25) | (_cmp_cached_108) | (_cmp_cached_63))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_41) | (_cmp_cached_122) | (_cmp_cached_65))
            # 4h down move, 4h & 1d high
            & ((_cmp_cached_41) | (_cmp_cached_77) | (_cmp_cached_27))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_41) | (_cmp_cached_27) | (_cmp_cached_70))
            # 4h down move, 1h high & overbought
            & ((_cmp_cached_21) | (_cmp_cached_94) | (_cmp_cached_48))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_99) | (_cmp_cached_169) | (_cmp_cached_102))
            # 4h down move, 4h high, 1d overbought
            & ((_cmp_cached_99) | (_cmp_cached_17) | (_cmp_cached_52))
            # 4h down move, 4h high
            & ((_cmp_cached_99) | (_cmp_cached_64))
            # 4h down move, 4h overbought
            & ((_cmp_cached_99) | (_cmp_cached_83))
            # 4h downtrend, 4h high
            & ((_cmp_cached_193) | (_cmp_cached_17))
            # 1h & 1d high, 4h downtrend
            & ((_cmp_cached_110) | (_cmp_cached_106) | (_cmp_cached_69))
            # 1h still high, 1h & 4h downtrend
            & ((_cmp_cached_110) | (_cmp_cached_129) | (_cmp_cached_103))
            # 1h & 4h high, 1d overbought
            & ((_cmp_cached_24) | (_cmp_cached_6) | (_cmp_cached_167))
            # 1h high, 4h & 1d downtrend
            & ((_cmp_cached_24) | (_cmp_cached_69) | (_cmp_cached_42))
            # 1h high, 4h downtrend
            & ((_cmp_cached_24) | (_cmp_cached_213))
            # 1h & 1d high, 1d overbought
            & ((_cmp_cached_33) | (_cmp_cached_94) | (_cmp_cached_63))
            # 1h & 1d high, 1h downtrend
            & ((_cmp_cached_33) | (_cmp_cached_27) | (_cmp_cached_129))
            # 4h & 1d high, 1h downtrend
            & ((_cmp_cached_77) | (_cmp_cached_27) | (_cmp_cached_109))
            # 4h & 1d high, 4h overbought
            & ((_cmp_cached_77) | (_cmp_cached_27) | (_cmp_cached_113))
            # 4h high, 1h downtrend
            & ((_cmp_cached_77) | (_cmp_cached_239))
            # 4h high & overbought
            & ((_cmp_cached_77) | (_cmp_cached_196))
            # 4h high, 1d downtrend
            & ((_cmp_cached_77) | (_cmp_cached_102))
            # 1d still high, 1d downtrend
            & ((_cmp_cached_238) | (_cmp_cached_102))
            # 1d high, 15m downtrend
            & ((_cmp_cached_106) | (_cmp_cached_241))
            # 1d high, 1h downtrend
            & ((_cmp_cached_106) | (_cmp_cached_284))
            # 1d high, 4h downtrend
            & ((_cmp_cached_108) | (_cmp_cached_280))
            # 1d high, 4h downtrend
            & ((_cmp_cached_94) | (_cmp_cached_213))
            # 1d high & overbought
            & ((_cmp_cached_94) | (_cmp_cached_111))
            # 1d high, 4h & 1d overbought
            & ((_cmp_cached_27) | (_cmp_cached_20) | (_cmp_cached_63))
            # 1h still high, 4h & 1d downtrend
            & ((_cmp_cached_59) | (_cmp_cached_69) | (_cmp_cached_42))
            # 1h high, 15m downtrend
            & ((_cmp_cached_37) | (_cmp_cached_187))
            # 4h high, 1d downtrend
            & ((_cmp_cached_64) | (_cmp_cached_206))
            # 1d high, 1h downtrend
            & ((_cmp_cached_39) | (_cmp_cached_129))
            # 1d high, 1d downtrend
            & ((_cmp_cached_60) | (_cmp_cached_102))
            # 15m downtrend, 1d overbought
            & ((_cmp_cached_285) | (_cmp_cached_111))
            # 1h downtrend, 1d overbought
            & ((_cmp_cached_286) | (_cmp_cached_111))
            # big drop in the last 20 days, 1d high, 1d downtrend
            & (
              (df["close"] > (df["high_max_20_1d"] * 0.20))
              | (_cmp_cached_148)
              | (_cmp_cached_149)
            )
          )

          # Logic
          long_entry_logic.append(
            (_cmp_cached_287)
            & (_cmp_cached_288)
            & (_cmp_cached_179)
            & (_cmp_cached_171)
            & (df["EMA_26_15m"] > df["EMA_12_15m"])
            & ((df["EMA_26_15m"] - df["EMA_12_15m"]) > (df["open_15m"] * 0.050))
            & ((df["EMA_26_15m"].shift() - df["EMA_12_15m"].shift()) > (df["open_15m"] / 100.0))
          )

        # Condition #45 - Quick mode (Long).
        if long_entry_condition_index == 45:
          # Protections
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          long_entry_logic.append(df["protections_long_global"] == True)

          # 5m & 15m down move, 4h still high
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp_cached_84) | (_cmp_cached_35)
          )
          # 15m & 1h down move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_1) | (_cmp_cached_11) | (_cmp_cached_28)
          )
          # 5m & 4h & 1d down move
          long_entry_logic.append((_cmp_cached_0) | (_cmp_cached_100) | (_cmp_cached_104))
          # 15m & 1h down move, 4h high
          long_entry_logic.append(
            (_cmp_cached_1) | (_cmp_cached_32) | (_cmp_cached_162)
          )
          # 15m & 4h down move
          long_entry_logic.append((_cmp_cached_1) | (_cmp_cached_58))
          # 15m & 4h down move, 4h still not low enough
          long_entry_logic.append((_cmp_cached_1) | (_cmp_cached_41) | (_cmp_cached_289))
          # 15m down move, 4h still high, 15m downtrend
          long_entry_logic.append((_cmp_cached_1) | (_cmp_cached_96) | (_cmp_cached_168))
          # 15m & 1h down move
          long_entry_logic.append((_cmp_cached_3) | (_cmp_cached_15))
          # 15m & 1h down move, 4h high
          long_entry_logic.append(
            (_cmp_cached_3) | (_cmp_cached_36) | (_cmp_cached_12)
          )
          # 15m down move, 1h still not low enough
          long_entry_logic.append((_cmp_cached_3) | (_cmp_cached_150))
          # 15m down move, 4h high
          long_entry_logic.append((_cmp_cached_3) | (_cmp_cached_46))
          # 15m & 1h & 1d down move
          long_entry_logic.append((_cmp_cached_5) | (_cmp_cached_9) | (_cmp_cached_153))
          # 15m & 1h down move, 1d overbought
          long_entry_logic.append((_cmp_cached_5) | (_cmp_cached_30) | (_cmp_cached_70))
          # 15m & 1h down move, 1h high
          long_entry_logic.append((_cmp_cached_5) | (_cmp_cached_38) | (_cmp_cached_33))
          # 15m & 1h down move, 1h high
          long_entry_logic.append(
            (_cmp_cached_5) | (_cmp_cached_221) | (_cmp_cached_19)
          )
          # 15m & 4h down move, 4h still not low enough
          long_entry_logic.append(
            (_cmp_cached_5) | (_cmp_cached_58) | (_cmp_cached_124)
          )
          # 15m & 4h down move, 1d high
          long_entry_logic.append(
            (_cmp_cached_5) | (_cmp_cached_58) | (_cmp_cached_74)
          )
          # 15m & 4h down move, 4h still high
          long_entry_logic.append(
            (_cmp_cached_5) | (_cmp_cached_41) | (_cmp_cached_165)
          )
          # 15m down move, 1h & 4h high
          long_entry_logic.append(
            (_cmp_cached_5) | (_cmp_cached_24) | (_cmp_cached_6)
          )
          # 15m down move, 1h high & overbought
          long_entry_logic.append((_cmp_cached_5) | (_cmp_cached_24) | (_cmp_cached_82))
          # 15m down move, 1h high, 4h overbought
          long_entry_logic.append((_cmp_cached_5) | (_cmp_cached_24) | (_cmp_cached_20))
          # 15m down move, 4h & 1d high
          long_entry_logic.append(
            (_cmp_cached_5) | (_cmp_cached_172) | (_cmp_cached_27)
          )
          # 15m down move, 4h high, 1h overbought
          long_entry_logic.append((_cmp_cached_5) | (_cmp_cached_6) | (_cmp_cached_82))
          # 15m & 1h down move, 4h high
          long_entry_logic.append((_cmp_cached_84) | (_cmp_cached_15) | (_cmp_cached_17))
          # 15m down move, 1h & 4h high
          long_entry_logic.append(
            (_cmp_cached_84) | (_cmp_cached_24) | (_cmp_cached_72)
          )
          # 15m down move, 4h high, 1d overbought
          long_entry_logic.append((_cmp_cached_84) | (_cmp_cached_17) | (_cmp_cached_107))
          # 15m & 1h down move, 1d overbought
          long_entry_logic.append((_cmp_cached_88) | (_cmp_cached_36) | (_cmp_cached_63))
          # 15m down move, 4h high & overbought
          long_entry_logic.append((_cmp_cached_88) | (_cmp_cached_6) | (_cmp_cached_50))
          # 15m & 1h down move, 1h high
          long_entry_logic.append((_cmp_cached_89) | (_cmp_cached_32) | (_cmp_cached_24))
          # 1h down move, 4h still not low enough
          long_entry_logic.append((_cmp_cached_13) | (_cmp_cached_98))
          # 1h & 4h down move, 1h still not low enough
          long_entry_logic.append((_cmp_cached_7) | (_cmp_cached_41) | (_cmp_cached_188))
          # 1h down move, 1h still not low enough
          long_entry_logic.append((_cmp_cached_7) | (_cmp_cached_150))
          # 1h down move, 1h still not low enough
          long_entry_logic.append((_cmp_cached_7) | (_cmp_cached_290))
          # 1h & 4h down move
          long_entry_logic.append((_cmp_cached_9) | (_cmp_cached_25))
          # 1h & 4h down move, 4h still not low enough
          long_entry_logic.append(
            (_cmp_cached_9) | (_cmp_cached_100) | (_cmp_cached_124)
          )
          # 1h & 4h down move, 4h still high
          long_entry_logic.append((_cmp_cached_9) | (_cmp_cached_16) | (_cmp_cached_122))
          # 1h & 4h down move, 4h still not low enough
          long_entry_logic.append((_cmp_cached_9) | (_cmp_cached_41) | (_cmp_cached_169))
          # 1h & 4h down move, 4h high
          long_entry_logic.append((_cmp_cached_9) | (_cmp_cached_181) | (_cmp_cached_40))
          # 1h & 1d down move, 4h still high
          long_entry_logic.append((_cmp_cached_9) | (_cmp_cached_153) | (_cmp_cached_96))
          # 1h & 1d down move, 5m moving down
          long_entry_logic.append((_cmp_cached_9) | (_cmp_cached_29) | (_cmp_cached_291))
          # 1h & 1d down move, 4h still high
          long_entry_logic.append((_cmp_cached_9) | (_cmp_cached_178) | (_cmp_cached_122))
          # 15m & 1d down move, 1d high
          long_entry_logic.append(
            (_cmp_cached_5) | (_cmp_cached_178) | (_cmp_cached_148)
          )
          # 1h & 4h down move, 4h still not low enough
          long_entry_logic.append(
            (_cmp_cached_13) | (_cmp_cached_16) | (_cmp_cached_124)
          )
          # 1h down move, 1h still not low enough, 1d high
          long_entry_logic.append(
            (_cmp_cached_9) | (_cmp_cached_190) | (_cmp_cached_131)
          )
          # 1h down move, 1h still not low enough
          long_entry_logic.append((_cmp_cached_9) | (_cmp_cached_290))
          # 1h down move, 4h high
          long_entry_logic.append((_cmp_cached_9) | (_cmp_cached_47))
          # 1h down move, 1d high & overbought
          long_entry_logic.append((_cmp_cached_9) | (_cmp_cached_106) | (_cmp_cached_107))
          # 1h down move, 1d overbought
          long_entry_logic.append((_cmp_cached_9) | (_cmp_cached_48))
          # 1h & 4h down move, 4h still high
          long_entry_logic.append((_cmp_cached_15) | (_cmp_cached_25) | (_cmp_cached_96))
          # 1h & 4h down move, 1d high
          long_entry_logic.append(
            (_cmp_cached_15) | (_cmp_cached_100) | (_cmp_cached_148)
          )
          # 1h & 4h & 1d down move
          long_entry_logic.append((_cmp_cached_15) | (_cmp_cached_100) | (_cmp_cached_178))
          # 1h & 4h down move, 1d high
          long_entry_logic.append((_cmp_cached_15) | (_cmp_cached_41) | (_cmp_cached_27))
          # 1h down move, 1h still high
          long_entry_logic.append((_cmp_cached_15) | (_cmp_cached_26))
          # 1h down move, 1d high, 4h downtrend
          long_entry_logic.append((_cmp_cached_15) | (_cmp_cached_106) | (_cmp_cached_69))
          # 1h down move, 1h still high
          long_entry_logic.append((_cmp_cached_15) | (_cmp_cached_161))
          # 1h & 4h down move, 1d overbought
          long_entry_logic.append((_cmp_cached_30) | (_cmp_cached_100) | (_cmp_cached_167))
          # 1h down move, 4h high
          long_entry_logic.append((_cmp_cached_30) | (_cmp_cached_46))
          # 1h down move, 4h still high
          long_entry_logic.append((_cmp_cached_30) | (_cmp_cached_35))
          # 1h & 4h down move, 1h high
          long_entry_logic.append(
            (_cmp_cached_11) | (_cmp_cached_41) | (_cmp_cached_123)
          )
          # 1h & 4h down move, 4h high
          long_entry_logic.append((_cmp_cached_11) | (_cmp_cached_181) | (_cmp_cached_17))
          # 1h down move, 1h high
          long_entry_logic.append((_cmp_cached_11) | (_cmp_cached_24))
          # 1h down move, 4h high
          long_entry_logic.append((_cmp_cached_11) | (_cmp_cached_12))
          # 1h & 1d down move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_32) | (_cmp_cached_73) | (_cmp_cached_59)
          )
          # 1h down move, 4h high
          long_entry_logic.append((_cmp_cached_32) | (_cmp_cached_66))
          # 14 down move, 1h high
          long_entry_logic.append((_cmp_cached_32) | (_cmp_cached_33))
          # 1h down move, 4h high
          long_entry_logic.append((_cmp_cached_32) | (_cmp_cached_77))
          # 1h down move, 4h high
          long_entry_logic.append((_cmp_cached_32) | (_cmp_cached_12))
          # 1h down move, 4h & 1d high
          long_entry_logic.append(
            (_cmp_cached_34) | (_cmp_cached_12) | (_cmp_cached_74)
          )
          # 1h down move, 1h still high, 1d overbought
          long_entry_logic.append((_cmp_cached_36) | (_cmp_cached_26) | (_cmp_cached_107))
          # 1h down move, 1h & 4h high
          long_entry_logic.append((_cmp_cached_38) | (_cmp_cached_24) | (_cmp_cached_46))
          # 1h down move, 1h & 4h high
          long_entry_logic.append(
            (_cmp_cached_53) | (_cmp_cached_37) | (_cmp_cached_46)
          )
          # 4h down move, 1d high
          long_entry_logic.append((_cmp_cached_55) | (_cmp_cached_27))
          # 4h & 1d down move, 1d still high
          long_entry_logic.append(
            (_cmp_cached_58) | (_cmp_cached_121) | (_cmp_cached_14)
          )
          # 4h downmove, 4h still high
          long_entry_logic.append((_cmp_cached_58) | (_cmp_cached_96))
          # 4h down move, 1h still high, 1d downtrend
          long_entry_logic.append(
            (_cmp_cached_58) | (_cmp_cached_28) | (_cmp_cached_57)
          )
          # 4h down move, 1h & 1d downtrend
          long_entry_logic.append((_cmp_cached_58) | (_cmp_cached_129) | (_cmp_cached_57))
          # 4h & 1d down move, 1d still high
          long_entry_logic.append((_cmp_cached_25) | (_cmp_cached_192) | (_cmp_cached_170))
          # 4h down move, 1h still not low enough
          long_entry_logic.append((_cmp_cached_25) | (_cmp_cached_150))
          # 4h & 1d down move, 1d high
          long_entry_logic.append((_cmp_cached_100) | (_cmp_cached_104) | (_cmp_cached_108))
          # 4h down move, 4h still high, 1d high
          long_entry_logic.append((_cmp_cached_100) | (_cmp_cached_122) | (_cmp_cached_27))
          # 4h down move, 1d high
          long_entry_logic.append((_cmp_cached_16) | (_cmp_cached_39))
          # 4h down move, 4h & 1d downtrend
          long_entry_logic.append((_cmp_cached_16) | (_cmp_cached_69) | (_cmp_cached_57))
          # 4h down move, 4h & 1d high
          long_entry_logic.append((_cmp_cached_41) | (_cmp_cached_77) | (_cmp_cached_27))
          # 4h down move, 1h high
          long_entry_logic.append((_cmp_cached_181) | (_cmp_cached_37))
          # 4h down move, 4h still high
          long_entry_logic.append((_cmp_cached_99) | (_cmp_cached_35))
          # 4h down move, 1h high
          long_entry_logic.append((_cmp_cached_71) | (_cmp_cached_19))
          # 4h down move, 4h high
          long_entry_logic.append((_cmp_cached_71) | (_cmp_cached_12))
          # 1d down move, 1h still not low enough
          long_entry_logic.append((_cmp_cached_101) | (_cmp_cached_161))
          # 1d down move, 1h still not low enough
          long_entry_logic.append((_cmp_cached_29) | (_cmp_cached_161))
          # 1d down move, 4h still high
          long_entry_logic.append((_cmp_cached_29) | (_cmp_cached_35))
          # 1d down move, 1h high & overbought
          long_entry_logic.append(
            (_cmp_cached_192) | (_cmp_cached_49) | (_cmp_cached_82)
          )
          # 15m still high, 1h & 4h high
          long_entry_logic.append(
            (_cmp_cached_292) | (_cmp_cached_33) | (_cmp_cached_46)
          )
          # 1h & 4h high, 4h overbought
          long_entry_logic.append((_cmp_cached_24) | (_cmp_cached_6) | (_cmp_cached_20))
          # 4h high, 1d overbought
          long_entry_logic.append((_cmp_cached_17) | (_cmp_cached_63))
          # 4h high, 1h & 1d downtrend
          long_entry_logic.append((_cmp_cached_17) | (_cmp_cached_129) | (_cmp_cached_57))
          # 4h high, 1h & 4h overbought
          long_entry_logic.append((_cmp_cached_77) | (_cmp_cached_82) | (_cmp_cached_50))
          # 4h high & overbought
          long_entry_logic.append((_cmp_cached_46) | (_cmp_cached_67))
          # 1d high, 4h & 1d downtrend
          long_entry_logic.append((_cmp_cached_108) | (_cmp_cached_69) | (_cmp_cached_57))
          # 1h high, 4h overbought
          long_entry_logic.append((_cmp_cached_19) | (_cmp_cached_67))
          # 4h high, 1h & 1d downtrend
          long_entry_logic.append(
            (_cmp_cached_64) | (_cmp_cached_129) | (_cmp_cached_57)
          )
          # 4h high, 1h & 4h overbought
          long_entry_logic.append(
            (_cmp_cached_12) | (_cmp_cached_82) | (_cmp_cached_50)
          )
          # 4h high, 4h & 1d overbought
          long_entry_logic.append(
            (_cmp_cached_12) | (_cmp_cached_51) | (_cmp_cached_70)
          )
          # 1d top wick, 4h still high
          long_entry_logic.append((_cmp_cached_293) | (_cmp_cached_122))
          # pump, 4h still high
          long_entry_logic.append(
            (((df["high_max_24_4h"] - df["low_min_24_4h"]) / df["low_min_24_4h"]) < 2.0)
            | (_cmp_cached_35)
          )
          # pump, drop but not yet near the previous lows
          long_entry_logic.append(
            (((df["high_max_24_4h"] - df["low_min_24_4h"]) / df["low_min_24_4h"]) < 2.0)
            | (df["close"] > (df["high_max_6_4h"] * 0.75))
            | (df["close"] < (df["low_min_24_4h"] * 1.25))
          )
          # pump, drop but not yet near the previous lows
          long_entry_logic.append(
            (((df["high_max_12_1d"] - df["low_min_12_1d"]) / df["low_min_12_1d"]) < 2.0)
            | (df["close"] > (df["high_max_24_4h"] * 0.70))
            | (df["close"] < (df["low_min_12_1d"] * 1.25))
          )
          # big drop in last hour
          long_entry_logic.append(df["close"] > (df["close_max_12"] * 0.50))
          # big drop in last hour, 1d down move
          long_entry_logic.append((df["close"] > (df["close_max_12"] * 0.80)) | (_cmp_cached_29))
          # big drop in the last 12 hours, 4h still high
          long_entry_logic.append((df["close"] > (df["high_max_12_1h"] * 0.50)) | (_cmp_cached_122))
          # big drop in the last 6 days, 1h still high
          long_entry_logic.append((df["close"] > (df["high_max_6_1d"] * 0.25)) | (_cmp_cached_26))
          # big drop in the last 12 days, 1h down move
          long_entry_logic.append((df["close"] > (df["high_max_12_1d"] * 0.45)) | (_cmp_cached_7))
          # big drop in the last 12 days, 4h down move
          long_entry_logic.append((df["close"] > (df["high_max_12_1d"] * 0.40)) | (_cmp_cached_25))
          # big drop in the last 12 days, 1h still high
          long_entry_logic.append((df["close"] > (df["high_max_12_1d"] * 0.25)) | (_cmp_cached_68))
          # big drop in the last 20 days, 1h down move
          long_entry_logic.append((df["close"] > (df["high_max_20_1d"] * 0.35)) | (_cmp_cached_9))
          # big drop in the last 20 days, 1h down move
          long_entry_logic.append((df["close"] > (df["high_max_20_1d"] * 0.25)) | (_cmp_cached_15))
          # big drop in the last 20 days, 1h down move
          long_entry_logic.append((df["close"] > (df["high_max_20_1d"] * 0.10)) | (_cmp_cached_30))
          # big drop in the last 20 days, 1d high, 1d downtrend
          long_entry_logic.append(
            (df["close"] > (df["high_max_20_1d"] * 0.20))
            | (_cmp_cached_148)
            | (_cmp_cached_149)
          )
          # big drop in the last 30 days, 4h down move, 4h still high
          long_entry_logic.append(
            (df["close"] > (df["high_max_30_1d"] * 0.25)) | (_cmp_cached_91) | (_cmp_cached_169)
          )

          # Logic
          long_entry_logic.append(_cmp_cached_247)
          long_entry_logic.append(_cmp_cached_179)
          long_entry_logic.append(_cmp_cached_171)
          long_entry_logic.append(df["close_15m"] < (df["EMA_20_15m"] * 0.924))

        # Condition #46 - Quick mode (Long).
        if long_entry_condition_index == 46:
          # Protections
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          long_entry_logic.append(df["protections_long_global"] == True)

          # 5m & 1h down move
          long_entry_logic.append((_cmp_cached_1) | (_cmp_cached_7))
          # 15m & 4h down move, 4h still high
          long_entry_logic.append((_cmp_cached_1) | (_cmp_cached_100) | (_cmp_cached_96))
          # 15m & 4h down move
          long_entry_logic.append((_cmp_cached_3) | (_cmp_cached_58))
          # 15m & 4h down move, 4h still high
          long_entry_logic.append((_cmp_cached_3) | (_cmp_cached_100) | (_cmp_cached_96))
          # 15m & 4h down move, 4h still high
          long_entry_logic.append((_cmp_cached_3) | (_cmp_cached_41) | (_cmp_cached_122))
          # 15m & 1h & 4h down move
          long_entry_logic.append((_cmp_cached_5) | (_cmp_cached_9) | (_cmp_cached_41))
          # 15m & 1h down move, 4h still not low enough
          long_entry_logic.append((_cmp_cached_5) | (_cmp_cached_9) | (_cmp_cached_163))
          # 15m & 1h & 4h down move
          long_entry_logic.append((_cmp_cached_5) | (_cmp_cached_30) | (_cmp_cached_100))
          # 15m & 1h down move, 1h still high
          long_entry_logic.append((_cmp_cached_5) | (_cmp_cached_30) | (_cmp_cached_110))
          # 15m & 1h down move, 4h still high
          long_entry_logic.append(
            (_cmp_cached_5) | (_cmp_cached_11) | (_cmp_cached_165)
          )
          # 15m & 4h down move, 1d high
          long_entry_logic.append(
            (_cmp_cached_5) | (_cmp_cached_25) | (_cmp_cached_39)
          )
          # 15m & 4h down move, 4h downtrend
          long_entry_logic.append((_cmp_cached_5) | (_cmp_cached_25) | (_cmp_cached_69))
          # 15m & 4h down move, 4h still high
          long_entry_logic.append((_cmp_cached_5) | (_cmp_cached_100) | (_cmp_cached_122))
          # 15m & 4h down move, 4h still not low enough
          long_entry_logic.append(
            (_cmp_cached_5) | (_cmp_cached_100) | (_cmp_cached_124)
          )
          # 15m & 4h down move, 1d high
          long_entry_logic.append(
            (_cmp_cached_5) | (_cmp_cached_41) | (_cmp_cached_39)
          )
          # 15m down move, 4h still high, 1d high
          long_entry_logic.append((_cmp_cached_5) | (_cmp_cached_122) | (_cmp_cached_94))
          # 15m & 1h down move, 4h high
          long_entry_logic.append((_cmp_cached_84) | (_cmp_cached_30) | (_cmp_cached_40))
          # 15m & 4h down move, 1h still high
          long_entry_logic.append((_cmp_cached_84) | (_cmp_cached_25) | (_cmp_cached_110))
          # 15m & 1h & 1d down move, 1h still not low enough, 1d high
          long_entry_logic.append(
            (_cmp_cached_87)
            | (_cmp_cached_30)
            | (_cmp_cached_178)
            | (_cmp_cached_294)
            | (_cmp_cached_108)
          )
          # 15m & 1h down move, 4h still high, 4h overbought
          long_entry_logic.append(
            (_cmp_cached_87) | (_cmp_cached_30) | (_cmp_cached_122) | (_cmp_cached_50)
          )
          # 15m & 1h down move, 4h high
          long_entry_logic.append((_cmp_cached_87) | (_cmp_cached_30) | (_cmp_cached_17))
          # 15m down move, 1h & 4h still high
          long_entry_logic.append(
            (_cmp_cached_87) | (_cmp_cached_110) | (_cmp_cached_35)
          )
          # 15m & 1h & 4h down move, 1d high
          long_entry_logic.append(
            (_cmp_cached_88) | (_cmp_cached_11) | (_cmp_cached_16) | (_cmp_cached_216)
          )
          # 15m & 4h down move, 4h high
          long_entry_logic.append((_cmp_cached_88) | (_cmp_cached_91) | (_cmp_cached_47))
          # 15m & 1h down move, 15m still not low enough
          long_entry_logic.append((_cmp_cached_89) | (_cmp_cached_32) | (_cmp_cached_295))
          # 15m & 1h down move, 1h high
          long_entry_logic.append((_cmp_cached_89) | (_cmp_cached_34) | (_cmp_cached_33))
          # 1h down move, 1h still not low enough, 1d high
          long_entry_logic.append((_cmp_cached_13) | (_cmp_cached_188) | (_cmp_cached_94))
          # 1h & 4h down move
          long_entry_logic.append((_cmp_cached_7) | (_cmp_cached_58))
          # 1h & 4h down move, 4h downtrend
          long_entry_logic.append((_cmp_cached_7) | (_cmp_cached_25) | (_cmp_cached_103))
          # 1h & 4h down move, 4h still not low enough
          long_entry_logic.append(
            (_cmp_cached_7) | (_cmp_cached_41) | (_cmp_cached_124)
          )
          # 1h & 1d down move, 1d high
          long_entry_logic.append((_cmp_cached_7) | (_cmp_cached_198) | (_cmp_cached_108))
          # 1h down move, 4h high
          long_entry_logic.append((_cmp_cached_7) | (_cmp_cached_17))
          # 1h down move, 1d still high
          long_entry_logic.append((_cmp_cached_7) | (_cmp_cached_14))
          # 1h & 4h down move, 4h still not low enough
          long_entry_logic.append((_cmp_cached_9) | (_cmp_cached_100) | (_cmp_cached_163))
          # 1h & 4h down move, 4h still not low enough
          long_entry_logic.append((_cmp_cached_9) | (_cmp_cached_41) | (_cmp_cached_169))
          # 1h & 4h down move, 4h still not low enough
          long_entry_logic.append((_cmp_cached_9) | (_cmp_cached_41) | (_cmp_cached_98))
          # 1h & 4h & 1d down move
          long_entry_logic.append((_cmp_cached_9) | (_cmp_cached_41) | (_cmp_cached_178))
          # 1h & 4h down move, 1d overbought
          long_entry_logic.append((_cmp_cached_9) | (_cmp_cached_21) | (_cmp_cached_107))
          # 1h & 4h down move, 4h high
          long_entry_logic.append((_cmp_cached_9) | (_cmp_cached_91) | (_cmp_cached_17))
          # 1h & 4h down move, 4h still high
          long_entry_logic.append(
            (_cmp_cached_9) | (_cmp_cached_99) | (_cmp_cached_165)
          )
          # 1h & 1d down move, 4h still not low enough
          long_entry_logic.append(
            (_cmp_cached_9) | (_cmp_cached_121) | (_cmp_cached_124)
          )
          # 1h & 1d down move, 4h still high
          long_entry_logic.append((_cmp_cached_9) | (_cmp_cached_178) | (_cmp_cached_122))
          # 1h down move, 1h still high
          long_entry_logic.append((_cmp_cached_9) | (_cmp_cached_26))
          # 1h down move, 4h still high, 1d high
          long_entry_logic.append((_cmp_cached_9) | (_cmp_cached_40) | (_cmp_cached_94))
          # 1h down move, 1d high & overbought
          long_entry_logic.append((_cmp_cached_9) | (_cmp_cached_108) | (_cmp_cached_70))
          # 1h & 4h down move, 1d stll high
          long_entry_logic.append((_cmp_cached_15) | (_cmp_cached_25) | (_cmp_cached_176))
          # 1h & 4h & 1d down move
          long_entry_logic.append((_cmp_cached_15) | (_cmp_cached_100) | (_cmp_cached_178))
          # 1h & 4h down move, 4h still not low enough
          long_entry_logic.append((_cmp_cached_15) | (_cmp_cached_100) | (_cmp_cached_98))
          # 1h & 4h down move, 1d overbought
          long_entry_logic.append((_cmp_cached_15) | (_cmp_cached_100) | (_cmp_cached_107))
          # 1h & 4h & 1d down move
          long_entry_logic.append((_cmp_cached_15) | (_cmp_cached_16) | (_cmp_cached_121))
          # 1h & 4h down move, 1d high
          long_entry_logic.append(
            (_cmp_cached_15) | (_cmp_cached_41) | (_cmp_cached_74)
          )
          # 1h & 4h down move, 1h & 4h still high
          long_entry_logic.append(
            (_cmp_cached_15) | (_cmp_cached_181) | (_cmp_cached_296) | (_cmp_cached_173)
          )
          # 1h & 4h down move, 4h still high
          long_entry_logic.append(
            (_cmp_cached_15) | (_cmp_cached_91) | (_cmp_cached_35)
          )
          # 1h & 4h down move, 4h still high
          long_entry_logic.append((_cmp_cached_15) | (_cmp_cached_99) | (_cmp_cached_96))
          # 1h & 1d down move, 1d still high
          long_entry_logic.append((_cmp_cached_15) | (_cmp_cached_29) | (_cmp_cached_238))
          # 1h down move, 1h still high, 1d overbought
          long_entry_logic.append((_cmp_cached_15) | (_cmp_cached_110) | (_cmp_cached_107))
          # 1h down move, 1d high, 4h downtrend
          long_entry_logic.append((_cmp_cached_15) | (_cmp_cached_106) | (_cmp_cached_69))
          # 1h down move, 1d high & overbought
          long_entry_logic.append((_cmp_cached_15) | (_cmp_cached_108) | (_cmp_cached_70))
          # 1h down move, 4h high
          long_entry_logic.append((_cmp_cached_15) | (_cmp_cached_64))
          # 1h & 4h down move, 1h still not low enough
          long_entry_logic.append((_cmp_cached_30) | (_cmp_cached_100) | (_cmp_cached_150))
          # 1h & 4h down move, 4h still high
          long_entry_logic.append((_cmp_cached_30) | (_cmp_cached_100) | (_cmp_cached_169))
          # 1h & 4h down move, 4h still high
          long_entry_logic.append((_cmp_cached_30) | (_cmp_cached_100) | (_cmp_cached_122))
          # 1h & 4h down move, 1d downtrend
          long_entry_logic.append((_cmp_cached_30) | (_cmp_cached_100) | (_cmp_cached_102))
          # 1h & 4h down move, 1d high
          long_entry_logic.append((_cmp_cached_30) | (_cmp_cached_21) | (_cmp_cached_108))
          # 1h & 4h down move, 4h high
          long_entry_logic.append((_cmp_cached_30) | (_cmp_cached_91) | (_cmp_cached_297))
          # 1h & 1d down move, 1d high
          long_entry_logic.append((_cmp_cached_30) | (_cmp_cached_104) | (_cmp_cached_106))
          # 1h down move, 1h still high, 1d high
          long_entry_logic.append((_cmp_cached_30) | (_cmp_cached_110) | (_cmp_cached_94))
          # 4h down move, 4h still high, 1d high
          long_entry_logic.append((_cmp_cached_100) | (_cmp_cached_122) | (_cmp_cached_27))
          # 1h down move, 4h still high, 1d downtrend
          long_entry_logic.append(
            (_cmp_cached_30) | (_cmp_cached_165) | (_cmp_cached_195)
          )
          # 1h down move, 4h & 1d high
          long_entry_logic.append(
            (_cmp_cached_30) | (_cmp_cached_35) | (_cmp_cached_74)
          )
          # 1h & 4h down move, 1h still high
          long_entry_logic.append((_cmp_cached_11) | (_cmp_cached_21) | (_cmp_cached_110))
          # 1h & 4h down move, 4h high
          long_entry_logic.append((_cmp_cached_11) | (_cmp_cached_181) | (_cmp_cached_17))
          # 1h down move, 15m still not low enough, 4h high
          long_entry_logic.append(
            (_cmp_cached_11) | (_cmp_cached_298) | (_cmp_cached_162)
          )
          # 1h & 4h down move, 4h still high
          long_entry_logic.append(
            (_cmp_cached_11) | (_cmp_cached_21) | (_cmp_cached_35)
          )
          # 1h down move, 1h high
          long_entry_logic.append((_cmp_cached_11) | (_cmp_cached_115))
          # 1h down move, 4h high
          long_entry_logic.append((_cmp_cached_11) | (_cmp_cached_77))
          # 1h & 1d down move, 1d high
          long_entry_logic.append((_cmp_cached_32) | (_cmp_cached_198) | (_cmp_cached_108))
          # 1h down move, 4h & 1d high
          long_entry_logic.append((_cmp_cached_32) | (_cmp_cached_17) | (_cmp_cached_27))
          # 1h down move, 4h high, 1d downtrend
          long_entry_logic.append((_cmp_cached_32) | (_cmp_cached_6) | (_cmp_cached_102))
          # 1h down move, 4h high
          long_entry_logic.append((_cmp_cached_32) | (_cmp_cached_72))
          # 1h & 4h down move, 4h high
          long_entry_logic.append((_cmp_cached_34) | (_cmp_cached_175) | (_cmp_cached_77))
          # 1h down move, 1h & 4h high
          long_entry_logic.append((_cmp_cached_34) | (_cmp_cached_24) | (_cmp_cached_46))
          # 1h down move, 4h high, 4h downtrend
          long_entry_logic.append((_cmp_cached_34) | (_cmp_cached_17) | (_cmp_cached_189))
          # 1h down move, 1d high, 4h overbought
          long_entry_logic.append((_cmp_cached_34) | (_cmp_cached_94) | (_cmp_cached_113))
          # 1h down move, 1h high, 1d overbought
          long_entry_logic.append((_cmp_cached_36) | (_cmp_cached_24) | (_cmp_cached_167))
          # 1h down move, 1h & 4h high
          long_entry_logic.append((_cmp_cached_117) | (_cmp_cached_24) | (_cmp_cached_6))
          # 1h down move, 1h overbought
          long_entry_logic.append((_cmp_cached_117) | (_cmp_cached_54))
          # 4h & 1d down move, 1d high
          long_entry_logic.append((_cmp_cached_55) | (_cmp_cached_178) | (_cmp_cached_106))
          # 4h down move, 1h & 4h downtrend
          long_entry_logic.append((_cmp_cached_55) | (_cmp_cached_130) | (_cmp_cached_69))
          # 4h & 1d down move
          long_entry_logic.append((_cmp_cached_58) | (_cmp_cached_104))
          # 4h & 1d down move, 1d high
          long_entry_logic.append((_cmp_cached_58) | (_cmp_cached_73) | (_cmp_cached_94))
          # 4h down move, 4h & 1d still high
          long_entry_logic.append((_cmp_cached_58) | (_cmp_cached_122) | (_cmp_cached_238))
          # 4h & 1d down move, 1d low
          long_entry_logic.append((_cmp_cached_25) | (_cmp_cached_121) | (_cmp_cached_143))
          # 4h & 1d down move, 1d still high
          long_entry_logic.append((_cmp_cached_25) | (_cmp_cached_178) | (_cmp_cached_238))
          # 4h & 1d down move, 1d overbought
          long_entry_logic.append((_cmp_cached_100) | (_cmp_cached_198) | (_cmp_cached_52))
          # 4h down move, 4h still not low enough, 1d downtrend
          long_entry_logic.append(
            (_cmp_cached_100) | (_cmp_cached_124) | (_cmp_cached_57)
          )
          # 4h down move, 4h & 1d downtrend
          long_entry_logic.append((_cmp_cached_100) | (_cmp_cached_69) | (_cmp_cached_57))
          # 4h down move, 4h high
          long_entry_logic.append((_cmp_cached_41) | (_cmp_cached_46))
          # 4h down move, 4h & 1d high
          long_entry_logic.append(
            (_cmp_cached_21) | (_cmp_cached_40) | (_cmp_cached_39)
          )
          # 4h down move, 1d high, 4h overbought
          long_entry_logic.append((_cmp_cached_91) | (_cmp_cached_27) | (_cmp_cached_50))
          # 4h down move, 4h overbought
          long_entry_logic.append((_cmp_cached_71) | (_cmp_cached_113))
          # 1d down move, 4h & 1d downtrend
          long_entry_logic.append((_cmp_cached_153) | (_cmp_cached_69) | (_cmp_cached_57))
          # 15m down move, 1d high, 1d downtrend
          long_entry_logic.append((_cmp_cached_29) | (_cmp_cached_106) | (_cmp_cached_65))
          # 1d down move, 1d high, 1d downtrend
          long_entry_logic.append((_cmp_cached_121) | (_cmp_cached_108) | (_cmp_cached_102))
          # 4h & 1d high, 4h overbought
          long_entry_logic.append((_cmp_cached_77) | (_cmp_cached_27) | (_cmp_cached_20))
          # 4h high, 1h overbought
          long_entry_logic.append((_cmp_cached_77) | (_cmp_cached_54))
          # 4h high, 4h overbought
          long_entry_logic.append((_cmp_cached_77) | (_cmp_cached_113))
          # 4h high, 1h overbought
          long_entry_logic.append((_cmp_cached_64) | (_cmp_cached_54))
          # 4h high, 4h overbought
          long_entry_logic.append((_cmp_cached_64) | (_cmp_cached_113))
          # 4h high, 4h overbought, 1d downtrend
          long_entry_logic.append(
            (_cmp_cached_72) | (_cmp_cached_20) | (_cmp_cached_57)
          )
          # 1d green, 4h down move, 4h still high
          long_entry_logic.append((_cmp_cached_142) | (_cmp_cached_21) | (_cmp_cached_96))
          # 4h top wick, 1h down move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_299) | (_cmp_cached_38) | (_cmp_cached_26)
          )
          # pump, drop but not yet near the previous lows
          long_entry_logic.append(
            (((df["high_max_6_1d"] - df["low_min_6_1d"]) / df["low_min_6_1d"]) < 2.0)
            | (df["close"] > (df["high_max_12_4h"] * 0.50))
            | (df["close"] < (df["low_min_24_4h"] * 1.05))
          )
          # 1d overbought, drop but not yet near the previous lows
          long_entry_logic.append(
            (_cmp_cached_107)
            | (df["close"] > (df["high_max_6_1d"] * 0.70))
            | (df["close"] < (df["low_min_12_1d"] * 1.25))
          )
          # 1d overbought, drop but not yet near the previous lows
          long_entry_logic.append(
            (((df["high_max_12_1d"] - df["low_min_12_1d"]) / df["low_min_12_1d"]) < 2.5)
            | (df["close"] > (df["high_max_6_1d"] * 0.60))
            | (df["close"] < (df["low_min_12_1d"] * 1.25))
          )
          # big drop in the last 2 days, 1d down move
          long_entry_logic.append((df["close"] > (df["high_max_12_4h"] * 0.30)) | (_cmp_cached_178))
          # big drop in the last 12 days, 1h down move
          long_entry_logic.append((df["close"] > (df["high_max_12_1d"] * 0.30)) | (_cmp_cached_30))
          # big drop in the last 12 days, 4h still high
          long_entry_logic.append(
            (df["close"] > (df["high_max_12_1d"] * 0.40)) | (_cmp_cached_35)
          )
          # big drop in the last 20 days, 1h down move
          long_entry_logic.append((df["close"] > (df["high_max_20_1d"] * 0.40)) | (_cmp_cached_9))
          # big drop in the last 20 days, 4h down move
          long_entry_logic.append((df["close"] > (df["high_max_20_1d"] * 0.10)) | (_cmp_cached_16))
          # big drop in the last 30 days, 4h down move
          long_entry_logic.append((df["close"] > (df["high_max_30_1d"] * 0.40)) | (_cmp_cached_25))
          # big drop in the last 30 days, 4h still not low enough
          long_entry_logic.append(
            (df["close"] > (df["high_max_30_1d"] * 0.25)) | (_cmp_cached_124)
          )

          # Logic
          long_entry_logic.append(_cmp_cached_287)
          long_entry_logic.append(_cmp_cached_288)
          long_entry_logic.append(_cmp_cached_300)
          long_entry_logic.append(_cmp_cached_179)
          long_entry_logic.append(_cmp_cached_171)
          long_entry_logic.append(_cmp_cached_278)
          long_entry_logic.append(_cmp_cached_190)
          long_entry_logic.append(_cmp_cached_301)
          long_entry_logic.append(df["close_max_48"] >= (df["close"] * 1.10))

        # Condition #61 - Rebuy mode (Long).
        if long_entry_condition_index == 61:
          # Protections
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          long_entry_logic.append(df["protections_long_global"] == True)

          long_entry_logic.append(
            # 5m & 1h down move, 1h still not low enough
            ((_cmp_cached_0) | (_cmp_cached_9) | (_cmp_cached_150))
            # 5m & 1h down move, 1d high
            & ((_cmp_cached_0) | (_cmp_cached_30) | (_cmp_cached_27))
            # 5m & 4h down move, 4h high
            & ((_cmp_cached_0) | (_cmp_cached_16) | (_cmp_cached_17))
            # 5m down move, 1d high & overbought
            & ((_cmp_cached_0) | (_cmp_cached_39) | (_cmp_cached_167))
            # 15m & 1h & 4h down move
            & ((_cmp_cached_1) | (_cmp_cached_13) | (_cmp_cached_58))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_1) | (_cmp_cached_13) | (_cmp_cached_169))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_1) | (_cmp_cached_13) | (_cmp_cached_96))
            # 15m & 1h down move, 4h still not low enough
            & ((_cmp_cached_1) | (_cmp_cached_7) | (_cmp_cached_156))
            # 15m & 1h & 4h down move
            & ((_cmp_cached_1) | (_cmp_cached_9) | (_cmp_cached_151))
            # 15m & 1h down move, 1d still high
            & ((_cmp_cached_1) | (_cmp_cached_9) | (_cmp_cached_170))
            # 15m & 1h down move, 4h downtrend
            & ((_cmp_cached_1) | (_cmp_cached_9) | (_cmp_cached_189))
            # 15m & 1h down move, 1d still high
            & ((_cmp_cached_1) | (_cmp_cached_9) | (_cmp_cached_14))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_1) | (_cmp_cached_9) | (_cmp_cached_52))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_1) | (_cmp_cached_30) | (_cmp_cached_107))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_1) | (_cmp_cached_32) | (_cmp_cached_108))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_1) | (_cmp_cached_32) | (_cmp_cached_28))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_1) | (_cmp_cached_38) | (_cmp_cached_33))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_1) | (_cmp_cached_53) | (_cmp_cached_19))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_1) | (_cmp_cached_181) | (_cmp_cached_169))
            # 15m down move, 15m downtrend. 4h high
            & ((_cmp_cached_1) | (_cmp_cached_302) | (_cmp_cached_40))
            # 15m down move, 15m still not low enough
            & ((_cmp_cached_1) | (_cmp_cached_10))
            # 15m down move, 4h high
            & ((_cmp_cached_1) | (_cmp_cached_77))
            # 15m down move, 4h & 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_69) | (_cmp_cached_57))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_3) | (_cmp_cached_30) | (_cmp_cached_28))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_32) | (_cmp_cached_19))
            # 15m & 4h down move, 1h downtrend
            & ((_cmp_cached_3) | (_cmp_cached_58) | (_cmp_cached_129))
            # 15m & 4h down move, 1d overbought
            & ((_cmp_cached_3) | (_cmp_cached_25) | (_cmp_cached_216))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_100) | (_cmp_cached_19))
            # 15m down move, 15m still low, 4h still high
            & ((_cmp_cached_3) | (_cmp_cached_166) | (_cmp_cached_122))
            # 15m down move, 15m still high
            & ((_cmp_cached_3) | (_cmp_cached_62))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_9) | (_cmp_cached_148))
            # 15m & 1h down move, 4h downtrend
            & ((_cmp_cached_5) | (_cmp_cached_9) | (_cmp_cached_204))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_30) | (_cmp_cached_63))
            # 15m & 1h down move, 15m still high
            & ((_cmp_cached_5) | (_cmp_cached_32) | (_cmp_cached_62))
            # 15m & 1h down move, 4h overbought
            & ((_cmp_cached_5) | (_cmp_cached_32) | (_cmp_cached_86))
            # 15m & 4h down move, 4h still not low enough
            & ((_cmp_cached_5) | (_cmp_cached_58) | (_cmp_cached_124))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_16) | (_cmp_cached_17))
            # 15m & 4h down move, 4h overbought
            & ((_cmp_cached_5) | (_cmp_cached_175) | (_cmp_cached_86))
            # 15m down move, 15m still not low enough, 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_10) | (_cmp_cached_102))
            # 15m down move, 15m still high, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_62) | (_cmp_cached_70))
            # 15m down move, 4h & 1d high
            & ((_cmp_cached_5) | (_cmp_cached_40) | (_cmp_cached_27))
            # 15m down move, 1d high, 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_131) | (_cmp_cached_202))
            # 15m down move, 1h high & overbought
            & ((_cmp_cached_5) | (_cmp_cached_49) | (_cmp_cached_79))
            # 15m down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_64))
            # 15m down move, 4h & 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_50) | (_cmp_cached_52))
            # 15m & 1h down move, 15m high
            & ((_cmp_cached_84) | (_cmp_cached_15) | (_cmp_cached_210))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_84) | (_cmp_cached_15) | (_cmp_cached_59))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_84) | (_cmp_cached_11) | (_cmp_cached_33))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_84) | (_cmp_cached_34) | (_cmp_cached_33))
            # 15m down move, 15m still high, 1h high
            & ((_cmp_cached_84) | (_cmp_cached_62) | (_cmp_cached_33))
            # 15m down move, 4h high, 4h downtrend
            & ((_cmp_cached_84) | (_cmp_cached_40) | (_cmp_cached_69))
            # 15m down move, 1d high, 4h overbought
            & ((_cmp_cached_84) | (_cmp_cached_39) | (_cmp_cached_113))
            # 15m down move, 1h & 4h overbought
            & ((_cmp_cached_84) | (_cmp_cached_79) | (_cmp_cached_113))
            # 15m down move, 4h & 1d downtrend
            & ((_cmp_cached_84) | (_cmp_cached_93) | (_cmp_cached_65))
            # 15m down move, 4h & 1d overbought
            & ((_cmp_cached_84) | (_cmp_cached_20) | (_cmp_cached_112))
            # 15m & 1h down move, 15m high
            & ((_cmp_cached_87) | (_cmp_cached_30) | (_cmp_cached_210))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_87) | (_cmp_cached_30) | (_cmp_cached_24))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_87) | (_cmp_cached_11) | (_cmp_cached_46))
            # 15m down move, 1h high
            & ((_cmp_cached_87) | (_cmp_cached_78))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_87) | (_cmp_cached_17) | (_cmp_cached_20))
            # 15m down move, 1h high
            & ((_cmp_cached_87) | (_cmp_cached_19))
            # 15m down move, 4h high
            & ((_cmp_cached_87) | (_cmp_cached_72))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_88) | (_cmp_cached_80) | (_cmp_cached_167))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_89) | (_cmp_cached_117) | (_cmp_cached_80))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_89) | (_cmp_cached_117) | (_cmp_cached_6))
            # 15m down move, 15m high, 4h high
            & ((_cmp_cached_89) | (_cmp_cached_210) | (_cmp_cached_64))
            # 15m down move, 1h & 4h high
            & (
              (_cmp_cached_89) | (_cmp_cached_37) | (_cmp_cached_12)
            )
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_13) | (_cmp_cached_55) | (_cmp_cached_156))
            # 1h & 4h down move, 15m stil high
            & ((_cmp_cached_13) | (_cmp_cached_58) | (_cmp_cached_61))
            # 1h & 4h down move, 1d still high
            & ((_cmp_cached_13) | (_cmp_cached_58) | (_cmp_cached_56))
            # 1h down move, 1h still not low enough
            & ((_cmp_cached_13) | (_cmp_cached_188))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_7) | (_cmp_cached_58) | (_cmp_cached_65))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_7) | (_cmp_cached_25) | (_cmp_cached_98))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_7) | (_cmp_cached_25) | (_cmp_cached_52))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_7) | (_cmp_cached_100) | (_cmp_cached_124))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_7) | (_cmp_cached_40) | (_cmp_cached_95))
            # 1h down move, 1d high, 4h downtrend
            & ((_cmp_cached_7) | (_cmp_cached_94) | (_cmp_cached_103))
            # 1h down move, 1d high, 1d downtrend
            & ((_cmp_cached_7) | (_cmp_cached_27) | (_cmp_cached_57))
            # 1h & 4h down move, 1h still not low enough
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_190))
            # 1h & 4h down move, 15m downtrend
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_116))
            # 1h & 3h down move, 4h downtrend
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_204))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_9) | (_cmp_cached_25) | (_cmp_cached_169))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_9) | (_cmp_cached_41) | (_cmp_cached_63))
            # 1h down move, 15m still high, 4h high
            & ((_cmp_cached_9) | (_cmp_cached_31) | (_cmp_cached_72))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_9) | (_cmp_cached_27) | (_cmp_cached_95))
            # 1h down move, 4h still high, 4d downtrend
            & ((_cmp_cached_9) | (_cmp_cached_35) | (_cmp_cached_42))
            # 1h down move, 4h downtrend, 1d overbought
            & ((_cmp_cached_9) | (_cmp_cached_93) | (_cmp_cached_52))
            # 1h down move, 1d overbought
            & ((_cmp_cached_9) | (_cmp_cached_48))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_15) | (_cmp_cached_181) | (_cmp_cached_77))
            # 1h down move, 1d downtrend, 1d high
            & ((_cmp_cached_15) | (_cmp_cached_224) | (_cmp_cached_74))
            # 1h down move, 1h still high
            & ((_cmp_cached_15) | (_cmp_cached_26))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_15) | (_cmp_cached_40) | (_cmp_cached_107))
            # 1h down move, 4h & 1d high
            & ((_cmp_cached_15) | (_cmp_cached_17) | (_cmp_cached_94))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_30) | (_cmp_cached_100) | (_cmp_cached_167))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_30) | (_cmp_cached_41) | (_cmp_cached_77))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_30) | (_cmp_cached_24) | (_cmp_cached_50))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_181) | (_cmp_cached_48))
            # 1h down move, 1h & 1d high
            & ((_cmp_cached_11) | (_cmp_cached_24) | (_cmp_cached_94))
            # 1h down move, 1h still high, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_59) | (_cmp_cached_52))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_11) | (_cmp_cached_12) | (_cmp_cached_65))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_32) | (_cmp_cached_21) | (_cmp_cached_68))
            # 1h down move, 1h high, 4h downtrend
            & ((_cmp_cached_34) | (_cmp_cached_33) | (_cmp_cached_213))
            # 1h down move, 1h still high, 1d overbought
            & ((_cmp_cached_34) | (_cmp_cached_59) | (_cmp_cached_111))
            # 1h down move, 1h high, 4h downtrend
            & ((_cmp_cached_34) | (_cmp_cached_37) | (_cmp_cached_69))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_34) | (_cmp_cached_20) | (_cmp_cached_63))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_36) | (_cmp_cached_24) | (_cmp_cached_46))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_36) | (_cmp_cached_45) | (_cmp_cached_63))
            # 1h down move, 1h high, 4h downtrend
            & ((_cmp_cached_36) | (_cmp_cached_19) | (_cmp_cached_69))
            # 1h down move, 1h high, 1h overbought
            & ((_cmp_cached_117) | (_cmp_cached_24) | (_cmp_cached_205))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_117) | (_cmp_cached_162) | (_cmp_cached_194))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_53) | (_cmp_cached_51) | (_cmp_cached_112))
            # 4h & 1d down move, 15m still high
            & ((_cmp_cached_151) | (_cmp_cached_29) | (_cmp_cached_155))
            # 4h & 1d down move, 1h still not low enough
            & ((_cmp_cached_151) | (_cmp_cached_29) | (_cmp_cached_161))
            # 4h & 1d down move, 1d still not low enough
            & ((_cmp_cached_151) | (_cmp_cached_178) | (_cmp_cached_269))
            # 4h down move, 1d high
            & ((_cmp_cached_151) | (_cmp_cached_94))
            # 4h down move, 1h still high, 4h downtrend
            & ((_cmp_cached_151) | (_cmp_cached_59) | (_cmp_cached_103))
            # 4h down move, 1d high
            & ((_cmp_cached_151) | (_cmp_cached_39))
            # 4h down move, 1h & 4h downtrend
            & ((_cmp_cached_151) | (_cmp_cached_109) | (_cmp_cached_103))
            # 4h down move, 1d overbought
            & ((_cmp_cached_151) | (_cmp_cached_52))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_55) | (_cmp_cached_178) | (_cmp_cached_56))
            # 4h down move, 4h downtrend, 4h still high
            & ((_cmp_cached_55) | (_cmp_cached_303) | (_cmp_cached_96))
            # 4h & 1d down move, 1d downtrend
            & ((_cmp_cached_58) | (_cmp_cached_153) | (_cmp_cached_65))
            # 4h down move, 1h high, 1d downtrend
            & ((_cmp_cached_58) | (_cmp_cached_123) | (_cmp_cached_65))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_25) | (_cmp_cached_104) | (_cmp_cached_199))
            # 4h down move, 4h high, 1h downtrend
            & ((_cmp_cached_25) | (_cmp_cached_40) | (_cmp_cached_129))
            # 4h down move, 4h & 1d high
            & ((_cmp_cached_25) | (_cmp_cached_17) | (_cmp_cached_106))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_100) | (_cmp_cached_108) | (_cmp_cached_107))
            # 4h down move, 1h still not low enough, 1d downtrend
            & ((_cmp_cached_25) | (_cmp_cached_190) | (_cmp_cached_57))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_100) | (_cmp_cached_165) | (_cmp_cached_57))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_16) | (_cmp_cached_122) | (_cmp_cached_65))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_41) | (_cmp_cached_122) | (_cmp_cached_65))
            # 4h down move, 4h high, 1d overbought
            & ((_cmp_cached_41) | (_cmp_cached_77) | (_cmp_cached_107))
            # 4h down move, 4h & 1d overbought
            & ((_cmp_cached_181) | (_cmp_cached_50) | (_cmp_cached_107))
            # 4h down move, 1h high, 1d overbought
            & ((_cmp_cached_91) | (_cmp_cached_45) | (_cmp_cached_107))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_99) | (_cmp_cached_169) | (_cmp_cached_102))
            # 4h down move, 4h high & overbought
            & ((_cmp_cached_99) | (_cmp_cached_77) | (_cmp_cached_50))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_99) | (_cmp_cached_35) | (_cmp_cached_102))
            # 1d down move, 1h still high, 1d downtrend
            & ((_cmp_cached_101) | (_cmp_cached_59) | (_cmp_cached_102))
            # 1d down move, 1h high, 1d downtrend
            & ((_cmp_cached_153) | (_cmp_cached_33) | (_cmp_cached_186))
            # 1d down move, 1d high, 1d downtrend
            & ((_cmp_cached_153) | (_cmp_cached_106) | (_cmp_cached_65))
            # 1d down move, 1h high & overbought
            & ((_cmp_cached_192) | (_cmp_cached_49) | (_cmp_cached_82))
            # 1d downtrend, 1d high & overbought
            & ((_cmp_cached_224) | (_cmp_cached_131) | (_cmp_cached_48))
            # 15m high, 1h high & overbought
            & ((_cmp_cached_210) | (_cmp_cached_45) | (_cmp_cached_82))
            # 1h high, 4h high, 1h overbought
            & ((_cmp_cached_24) | (_cmp_cached_6) | (_cmp_cached_79))
            # 1h & 1d high, 1h overbought
            & ((_cmp_cached_24) | (_cmp_cached_106) | (_cmp_cached_79))
            # 1h & 4h high, 1d downtrend
            & ((_cmp_cached_45) | (_cmp_cached_6) | (_cmp_cached_218))
            # 4h still high, 5m downtrend
            & ((_cmp_cached_96) | (_cmp_cached_203))
            # 4h high, 4h & 1d overbought
            & ((_cmp_cached_40) | (_cmp_cached_51) | (_cmp_cached_112))
            # 4h & 1d high, 4h overbought
            & ((_cmp_cached_77) | (_cmp_cached_27) | (_cmp_cached_51))
            # 4h & 1d high, 1d overbought
            & ((_cmp_cached_77) | (_cmp_cached_27) | (_cmp_cached_107))
            # 4h high, 4h & 1d overbought
            & ((_cmp_cached_77) | (_cmp_cached_20) | (_cmp_cached_167))
            # 1d high, 1h & 4h downtrend
            & ((_cmp_cached_131) | (_cmp_cached_109) | (_cmp_cached_204))
            # 1d high, 1h & 1d overbought
            & ((_cmp_cached_131) | (_cmp_cached_79) | (_cmp_cached_48))
            # 1d high, 4h & 1d overbought
            & ((_cmp_cached_94) | (_cmp_cached_51) | (_cmp_cached_112))
            # 1h high, 1d overbought
            & ((_cmp_cached_37) | (_cmp_cached_52))
            # 4h high, 1h overbought, 1d downtrend
            & ((_cmp_cached_12) | (_cmp_cached_54) | (_cmp_cached_206))
            # 4h high, 1h & 4h overbought
            & ((_cmp_cached_72) | (_cmp_cached_79) | (_cmp_cached_86))
            # 1h & 4h overbought
            & ((_cmp_cached_182) | (_cmp_cached_196))
            # big drop in the last 20 days, 1d high, 1d downtrend
            & (
              (df["close"] > (df["high_max_20_1d"] * 0.20))
              | (_cmp_cached_148)
              | (_cmp_cached_149)
            )
          )

          # Logic
          long_entry_logic.append(
            (_cmp_cached_247)
            & (_cmp_cached_243)
            & (_cmp_cached_208)
            & (df["EMA_26"] > df["EMA_12"])
            & ((df["EMA_26"] - df["EMA_12"]) > (df["open"] * 0.030))
            & ((df["EMA_26"].shift() - df["EMA_12"].shift()) > (df["open"] / 100.0))
          )

        # Condition #62 - Rebuy mode (Long).
        if long_entry_condition_index == 62:
          # Protections
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          long_entry_logic.append(df["protections_long_global"] == True)

          long_entry_logic.append(
            # 5m & 4h down move, 1d high
            ((_cmp_cached_0) | (_cmp_cached_58) | (_cmp_cached_94))
            # 5m & 1d down move, 15m still high
            & ((_cmp_cached_0) | (_cmp_cached_104) | (_cmp_cached_155))
            # 5m & 4h down move, 15m still high
            & ((_cmp_cached_8) | (_cmp_cached_16) | (_cmp_cached_61))
            # 5m & 4h down move, 4h still not low enough
            & ((_cmp_cached_8) | (_cmp_cached_25) | (_cmp_cached_156))
            # 15m & 1h down move, 1h still not low enough
            & ((_cmp_cached_1) | (_cmp_cached_9) | (_cmp_cached_188))
            # 15m & 1h down move, 4h still not low enough
            & ((_cmp_cached_1) | (_cmp_cached_9) | (_cmp_cached_163))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_1) | (_cmp_cached_15) | (_cmp_cached_173))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_1) | (_cmp_cached_30) | (_cmp_cached_165))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_1) | (_cmp_cached_11) | (_cmp_cached_122))
            # 15m & 4h down move, 4h still not low enough
            & ((_cmp_cached_1) | (_cmp_cached_151) | (_cmp_cached_120))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_1) | (_cmp_cached_100) | (_cmp_cached_96))
            # 15m & 1h down move, 1h still not low enough
            & ((_cmp_cached_3) | (_cmp_cached_9) | (_cmp_cached_190))
            # 15m & 1h down move, 15m still not low enough
            & ((_cmp_cached_3) | (_cmp_cached_9) | (_cmp_cached_171))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_3) | (_cmp_cached_9) | (_cmp_cached_96))
            # 15m & 4h down move, 15m still not low enough
            & ((_cmp_cached_3) | (_cmp_cached_58) | (_cmp_cached_152))
            # 15m & 4h down move, 1h downtrend
            & ((_cmp_cached_3) | (_cmp_cached_58) | (_cmp_cached_129))
            # 15m & 4h down move, 1d overbought
            & ((_cmp_cached_3) | (_cmp_cached_58) | (_cmp_cached_167))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_3) | (_cmp_cached_25) | (_cmp_cached_169))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_5) | (_cmp_cached_9) | (_cmp_cached_165))
            # 15m & 1h down move, 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_9) | (_cmp_cached_57))
            # 15m & 1h down move, 15m high
            & ((_cmp_cached_5) | (_cmp_cached_9) | (_cmp_cached_76))
            # 15m & 1h down move, 1h still not low enough
            & ((_cmp_cached_5) | (_cmp_cached_9) | (_cmp_cached_150))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_5) | (_cmp_cached_15) | (_cmp_cached_110))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_9) | (_cmp_cached_27))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_15) | (_cmp_cached_40))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_34) | (_cmp_cached_46))
            # 15m & 4h down move, 15m still not low enough
            & ((_cmp_cached_5) | (_cmp_cached_25) | (_cmp_cached_166))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_100) | (_cmp_cached_39))
            # 15m & 4h down move, 4h still not low enough
            & ((_cmp_cached_5) | (_cmp_cached_100) | (_cmp_cached_124))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_100) | (_cmp_cached_148))
            # 15m & 4h down move, 4h downtrend
            & ((_cmp_cached_5) | (_cmp_cached_16) | (_cmp_cached_189))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_41) | (_cmp_cached_39))
            # 15m & 4h down move, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_181) | (_cmp_cached_111))
            # 15m & 1d down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_104) | (_cmp_cached_214))
            # 15m down move, 4h high, 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_17) | (_cmp_cached_195))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_84) | (_cmp_cached_15) | (_cmp_cached_172))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_84) | (_cmp_cached_100) | (_cmp_cached_40))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_84) | (_cmp_cached_16) | (_cmp_cached_165))
            # 15m down move, 15m downtrend, 4h high
            & ((_cmp_cached_84) | (_cmp_cached_159) | (_cmp_cached_122))
            # 15m down move, 15m still high, 4h overbought
            & ((_cmp_cached_84) | (_cmp_cached_31) | (_cmp_cached_113))
            # 15m down move, 4h & 1d high
            & ((_cmp_cached_84) | (_cmp_cached_77) | (_cmp_cached_27))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_87) | (_cmp_cached_24) | (_cmp_cached_6))
            # 15m down move, 15m still not low enough, 1d overbought
            & ((_cmp_cached_87) | (_cmp_cached_152) | (_cmp_cached_63))
            # 15m & 4h down move, 15m stil high
            & ((_cmp_cached_88) | (_cmp_cached_41) | (_cmp_cached_155))
            # 15m down move, 15m still not low enough, 1d downtrend
            & ((_cmp_cached_88) | (_cmp_cached_179) | (_cmp_cached_42))
            # 15m down move, 15m still high, 4h high
            & ((_cmp_cached_88) | (_cmp_cached_62) | (_cmp_cached_77))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_89) | (_cmp_cached_36) | (_cmp_cached_26))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_89) | (_cmp_cached_21) | (_cmp_cached_17))
            # 15m down move, 15m still high, 4h high
            & ((_cmp_cached_184) | (_cmp_cached_62) | (_cmp_cached_77))
            # 1h & 4h down move, 1d still high
            & ((_cmp_cached_13) | (_cmp_cached_58) | (_cmp_cached_56))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_13) | (_cmp_cached_181) | (_cmp_cached_35))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_13) | (_cmp_cached_99) | (_cmp_cached_17))
            # 1h down move, 15m still not low enough
            & ((_cmp_cached_13) | (_cmp_cached_171))
            # 1h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_13) | (_cmp_cached_35) | (_cmp_cached_57))
            # 1h & 4h down move, 15m still not low enough
            & ((_cmp_cached_7) | (_cmp_cached_55) | (_cmp_cached_152))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_7) | (_cmp_cached_55) | (_cmp_cached_124))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_7) | (_cmp_cached_58) | (_cmp_cached_120))
            # 1h & 4h down move, 4h downtrend
            & ((_cmp_cached_7) | (_cmp_cached_25) | (_cmp_cached_103))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_7) | (_cmp_cached_100) | (_cmp_cached_163))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_7) | (_cmp_cached_41) | (_cmp_cached_96))
            # 1h & 4h & 1d down move
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_29))
            # 1h & 4h down move, 15m high
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_222))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_98))
            # 1h & 4h down move, 1h downtrend
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_129))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_57))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_95))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_9) | (_cmp_cached_100) | (_cmp_cached_96))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_9) | (_cmp_cached_16) | (_cmp_cached_40))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_9) | (_cmp_cached_16) | (_cmp_cached_165))
            # 1h & 4h down move, 1h still not low enough
            & ((_cmp_cached_9) | (_cmp_cached_21) | (_cmp_cached_150))
            # 1h& 1d down move, 1h still high
            & ((_cmp_cached_9) | (_cmp_cached_121) | (_cmp_cached_110))
            # 1h & 1d down move, 1d high
            & ((_cmp_cached_9) | (_cmp_cached_126) | (_cmp_cached_108))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_15) | (_cmp_cached_25) | (_cmp_cached_191))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_15) | (_cmp_cached_25) | (_cmp_cached_96))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_15) | (_cmp_cached_25) | (_cmp_cached_148))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_15) | (_cmp_cached_100) | (_cmp_cached_165))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_15) | (_cmp_cached_100) | (_cmp_cached_39))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_15) | (_cmp_cached_41) | (_cmp_cached_74))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_15) | (_cmp_cached_91) | (_cmp_cached_65))
            # 1h & 1d down move, 4h high
            & ((_cmp_cached_15) | (_cmp_cached_29) | (_cmp_cached_12))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_15) | (_cmp_cached_17) | (_cmp_cached_48))
            # 1h down move, 1d high, 4h downtrend
            & ((_cmp_cached_15) | (_cmp_cached_94) | (_cmp_cached_69))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_30) | (_cmp_cached_16) | (_cmp_cached_148))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_30) | (_cmp_cached_181) | (_cmp_cached_64))
            # 1h & 4h down move, 4h overbought
            & ((_cmp_cached_30) | (_cmp_cached_181) | (_cmp_cached_50))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_30) | (_cmp_cached_91) | (_cmp_cached_27))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_30) | (_cmp_cached_99) | (_cmp_cached_12))
            # 1h down move, 1h high
            & ((_cmp_cached_30) | (_cmp_cached_24))
            # 1h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_30) | (_cmp_cached_96) | (_cmp_cached_57))
            # 1h down move, 4h high
            & ((_cmp_cached_30) | (_cmp_cached_47))
            # 1h down move, 1h still not low enough, 4h stil high
            & ((_cmp_cached_30) | (_cmp_cached_190) | (_cmp_cached_96))
            # 1h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_30) | (_cmp_cached_165) | (_cmp_cached_65))
            # 1h down move, 1d high, 4h downtrend
            & ((_cmp_cached_30) | (_cmp_cached_74) | (_cmp_cached_69))
            # 1h down move, 4h high
            & ((_cmp_cached_30) | (_cmp_cached_12))
            # 1h & 4h down move, 1h still not low enough
            & ((_cmp_cached_11) | (_cmp_cached_16) | (_cmp_cached_190))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_16) | (_cmp_cached_107))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_11) | (_cmp_cached_41) | (_cmp_cached_40))
            # 1h down move, 4h & 1d high
            & ((_cmp_cached_11) | (_cmp_cached_40) | (_cmp_cached_27))
            # 1h down move, 4h high, 4h downtrend
            & ((_cmp_cached_11) | (_cmp_cached_17) | (_cmp_cached_193))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_11) | (_cmp_cached_17) | (_cmp_cached_50))
            # 1h down move, 15m still high, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_61) | (_cmp_cached_70))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_32) | (_cmp_cached_41) | (_cmp_cached_35))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_32) | (_cmp_cached_41) | (_cmp_cached_48))
            # 1h & dh down move, 4h high
            & ((_cmp_cached_32) | (_cmp_cached_99) | (_cmp_cached_47))
            # 1h down move, 4h & 1d downtrend
            & ((_cmp_cached_32) | (_cmp_cached_81) | (_cmp_cached_194))
            # 1h down move, 4h & 1h overbought
            & ((_cmp_cached_32) | (_cmp_cached_51) | (_cmp_cached_52))
            # 1h down move, 4h high, 4h downtrend
            & ((_cmp_cached_32) | (_cmp_cached_17) | (_cmp_cached_200))
            # 1h down move, 1d high, 4h downtrend
            & ((_cmp_cached_32) | (_cmp_cached_108) | (_cmp_cached_103))
            # 1h down move, 1d high, 4h overbought
            & ((_cmp_cached_32) | (_cmp_cached_27) | (_cmp_cached_20))
            # 1h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_32) | (_cmp_cached_165) | (_cmp_cached_218))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_32) | (_cmp_cached_72) | (_cmp_cached_20))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_32) | (_cmp_cached_50) | (_cmp_cached_70))
            # 1h & 4h down move, 1h still high
            & ((_cmp_cached_34) | (_cmp_cached_21) | (_cmp_cached_26))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_34) | (_cmp_cached_181) | (_cmp_cached_77))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_34) | (_cmp_cached_24) | (_cmp_cached_6))
            # 1h down move, 1d high, 4h overbought
            & ((_cmp_cached_34) | (_cmp_cached_94) | (_cmp_cached_113))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_36) | (_cmp_cached_64) | (_cmp_cached_51))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_38) | (_cmp_cached_77) | (_cmp_cached_196))
            # 1h down move, 1h overbought
            & ((_cmp_cached_117) | (_cmp_cached_54))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_53) | (_cmp_cached_51) | (_cmp_cached_48))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_55) | (_cmp_cached_104) | (_cmp_cached_119))
            # 4h & 1d down move, 4h still not low enough
            & ((_cmp_cached_55) | (_cmp_cached_178) | (_cmp_cached_120))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_55) | (_cmp_cached_178) | (_cmp_cached_106))
            # 4h down move, 1h high, 4h downtrend
            & ((_cmp_cached_55) | (_cmp_cached_24) | (_cmp_cached_69))
            # 4h down move, 4h high
            & ((_cmp_cached_55) | (_cmp_cached_40))
            # 4h & 1d down move, 1d still not low enough
            & ((_cmp_cached_58) | (_cmp_cached_29) | (_cmp_cached_269))
            # 4h down move, 15m still high
            & ((_cmp_cached_58) | (_cmp_cached_155))
            # 4h down move, 1d still high, 1d downtrend
            & ((_cmp_cached_25) | (_cmp_cached_176) | (_cmp_cached_149))
            # 4h down move, 1h downtrend, 1d downtrend
            & ((_cmp_cached_25) | (_cmp_cached_240) | (_cmp_cached_57))
            # 4h down move, 15m high, 1d overbought
            & ((_cmp_cached_25) | (_cmp_cached_76) | (_cmp_cached_48))
            # 4h down move, 4h still high, 4h downtrend
            & ((_cmp_cached_25) | (_cmp_cached_96) | (_cmp_cached_69))
            # 4h down move, 15m still not low enough, 1d downtrend
            & ((_cmp_cached_25) | (_cmp_cached_152) | (_cmp_cached_57))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_25) | (_cmp_cached_39) | (_cmp_cached_167))
            # 4h & 1d down move, 1d overbought
            & ((_cmp_cached_100) | (_cmp_cached_198) | (_cmp_cached_52))
            # 4h down move, 15m high, 4h downtrend
            & ((_cmp_cached_100) | (_cmp_cached_76) | (_cmp_cached_103))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_100) | (_cmp_cached_108) | (_cmp_cached_70))
            # 4h & 1d down move, 1d overbought
            & ((_cmp_cached_16) | (_cmp_cached_198) | (_cmp_cached_95))
            # 4h down move, 15m high, 4h high
            & ((_cmp_cached_16) | (_cmp_cached_76) | (_cmp_cached_77))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_16) | (_cmp_cached_96) | (_cmp_cached_57))
            # 4h down move, 4h still high, 4h downtrend
            & ((_cmp_cached_16) | (_cmp_cached_122) | (_cmp_cached_200))
            # 4h down move, 4h high, 1d high
            & ((_cmp_cached_41) | (_cmp_cached_17) | (_cmp_cached_74))
            # 4h down move, 1d still high, 1d downtrend
            & ((_cmp_cached_41) | (_cmp_cached_119) | (_cmp_cached_57))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_41) | (_cmp_cached_27) | (_cmp_cached_167))
            # 4h down move, 4h still not low enough, 1d overbought
            & ((_cmp_cached_41) | (_cmp_cached_156) | (_cmp_cached_52))
            # 4h down move, 1h high
            & ((_cmp_cached_21) | (_cmp_cached_24))
            # 4h down move, 15m & 4h still high
            & (
              (_cmp_cached_181) | (_cmp_cached_61) | (_cmp_cached_35)
            )
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_181) | (_cmp_cached_39) | (_cmp_cached_111))
            # 4h down move, 4h high
            & ((_cmp_cached_181) | (_cmp_cached_6))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_99) | (_cmp_cached_169) | (_cmp_cached_102))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_99) | (_cmp_cached_35) | (_cmp_cached_102))
            # 4h down move, 4h overbought
            & ((_cmp_cached_175) | (_cmp_cached_51))
            # 4h down move, 4h overbought
            & ((_cmp_cached_71) | (_cmp_cached_113))
            # 1d down move, 4h & 1d downtrend
            & ((_cmp_cached_153) | (_cmp_cached_69) | (_cmp_cached_102))
            # 1d down move, 1d high, 1d downtrend
            & ((_cmp_cached_29) | (_cmp_cached_106) | (_cmp_cached_57))
            # 1d down move, 4h & 1d downtrend
            & ((_cmp_cached_29) | (_cmp_cached_93) | (_cmp_cached_65))
            # 4h & 1d downtrend, 1d high
            & ((_cmp_cached_193) | (_cmp_cached_275) | (_cmp_cached_131))
            # 4h still not low enough, 4h & 1d downtrend
            & ((_cmp_cached_98) | (_cmp_cached_69) | (_cmp_cached_195))
            # 4h & 1d high, 4h overbought
            & ((_cmp_cached_17) | (_cmp_cached_27) | (_cmp_cached_51))
            # 4h & 1d high, 1d overbought
            & ((_cmp_cached_17) | (_cmp_cached_27) | (_cmp_cached_63))
            # 4h high, 1h & 4h overbought
            & ((_cmp_cached_77) | (_cmp_cached_54) | (_cmp_cached_113))
            # 1d high, 4h downtrend, 1d overbought
            & ((_cmp_cached_131) | (_cmp_cached_69) | (_cmp_cached_111))
            # 1d high, 4h & 1d overbought
            & ((_cmp_cached_94) | (_cmp_cached_51) | (_cmp_cached_112))
            # 4h high, 1h & 4h overbought
            & ((_cmp_cached_64) | (_cmp_cached_54) | (_cmp_cached_113))
            # 4h high, 4h & 1d overbought
            & ((_cmp_cached_12) | (_cmp_cached_20) | (_cmp_cached_167))
            # 1d green, 4h down move, 4h still high
            & ((_cmp_cached_142) | (_cmp_cached_21) | (_cmp_cached_96))
          )

          # Logic
          long_entry_logic.append(
            (_cmp_cached_287)
            & (_cmp_cached_207)
            & (_cmp_cached_237)
            & (_cmp_cached_92)
            & (_cmp_cached_278)
            & (_cmp_cached_161)
            & (_cmp_cached_301)
            & (df["close_max_48"] >= (df["close"] * 1.10))
          )

        # Condition #63 - Rebuy mode (Long).
        if long_entry_condition_index == 63:
          # Protections
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          long_entry_logic.append(df["protections_long_global"] == True)

          long_entry_logic.append(
            (_cmp_cached_3)
            # 5m & 1h down move, 1h still not low enough
            & ((_cmp_cached_0) | (_cmp_cached_9) | (_cmp_cached_150))
            # 5m & 1d down move, 1d downtrend
            & ((_cmp_cached_0) | (_cmp_cached_29) | (_cmp_cached_154))
            # 5m down move, 1h high, 4h overbought
            & ((_cmp_cached_0) | (_cmp_cached_19) | (_cmp_cached_20))
            # 5m down move, 1d high & overbought
            & ((_cmp_cached_0) | (_cmp_cached_39) | (_cmp_cached_167))
            # 15m & 1h down move, 1h still not low enough
            & ((_cmp_cached_5) | (_cmp_cached_15) | (_cmp_cached_161))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_5) | (_cmp_cached_30) | (_cmp_cached_35))
            # 15m & 1h down move 1h still high
            & ((_cmp_cached_5) | (_cmp_cached_11) | (_cmp_cached_28))
            # 15m & 1h down move, 15m still high
            & ((_cmp_cached_5) | (_cmp_cached_32) | (_cmp_cached_62))
            # 15m & 1h down move 1h still high
            & ((_cmp_cached_5) | (_cmp_cached_32) | (_cmp_cached_59))
            # 15m & 1h down move, 4h overbought
            & ((_cmp_cached_5) | (_cmp_cached_32) | (_cmp_cached_50))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_5) | (_cmp_cached_117) | (_cmp_cached_49))
            # 15m & 4h down move, 4h still not low enough
            & ((_cmp_cached_5) | (_cmp_cached_58) | (_cmp_cached_124))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_58) | (_cmp_cached_74))
            # 15m & 4h down move, 4h still not low enough
            & ((_cmp_cached_5) | (_cmp_cached_25) | (_cmp_cached_124))
            # 15m & 4h down move, 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_25) | (_cmp_cached_57))
            # 1h & 4h down move, 15m still high
            & ((_cmp_cached_5) | (_cmp_cached_41) | (_cmp_cached_62))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_181) | (_cmp_cached_12))
            # 15m & 1d down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_153) | (_cmp_cached_106))
            # 15m & 1d down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_104) | (_cmp_cached_214))
            # 15m down move, 15m still high, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_62) | (_cmp_cached_77))
            # 15m down move, 1h still high, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_26) | (_cmp_cached_112))
            # 15m down move, 4h high, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_40) | (_cmp_cached_112))
            # 15m down move, 1d high & overbought
            & ((_cmp_cached_5) | (_cmp_cached_94) | (_cmp_cached_167))
            # 15m down move, 1d high, 4h overbought
            & ((_cmp_cached_5) | (_cmp_cached_39) | (_cmp_cached_50))
            # 15m & 1h & 4h down move
            & ((_cmp_cached_84) | (_cmp_cached_15) | (_cmp_cached_25))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_84) | (_cmp_cached_11) | (_cmp_cached_24))
            # 15m & 4h down move, 15m still high
            & ((_cmp_cached_84) | (_cmp_cached_16) | (_cmp_cached_31))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_84) | (_cmp_cached_21) | (_cmp_cached_39))
            # 15m & 4h down move, 15m high
            & ((_cmp_cached_84) | (_cmp_cached_21) | (_cmp_cached_210))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_84) | (_cmp_cached_21) | (_cmp_cached_40))
            # 15m & 1d down move, 4h high
            & ((_cmp_cached_84) | (_cmp_cached_121) | (_cmp_cached_6))
            # 15m down move, 15m still high, 4h high
            & ((_cmp_cached_84) | (_cmp_cached_62) | (_cmp_cached_12))
            # 15m down move, 4h high, 4h downtrend
            & ((_cmp_cached_84) | (_cmp_cached_40) | (_cmp_cached_69))
            # 15m down move, 4h & 1d high
            & ((_cmp_cached_84) | (_cmp_cached_172) | (_cmp_cached_27))
            # 15m down move, 15m still not low enough, 1h still high
            & (
              (_cmp_cached_84) | (_cmp_cached_152) | (_cmp_cached_59)
            )
            # 15m down move, 4h & 1d overbought
            & ((_cmp_cached_84) | (_cmp_cached_20) | (_cmp_cached_112))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_87) | (_cmp_cached_30) | (_cmp_cached_37))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_87) | (_cmp_cached_99) | (_cmp_cached_47))
            # 15m down move, 1h high
            & ((_cmp_cached_87) | (_cmp_cached_68))
            # 15m down move, 1d high & overbought
            & ((_cmp_cached_87) | (_cmp_cached_94) | (_cmp_cached_63))
            # 15m down move, 15m high, 4h downtrend
            & ((_cmp_cached_87) | (_cmp_cached_222) | (_cmp_cached_204))
            # 15m down move, 4h overbought
            & ((_cmp_cached_87) | (_cmp_cached_113))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_88) | (_cmp_cached_11) | (_cmp_cached_24))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_88) | (_cmp_cached_36) | (_cmp_cached_63))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_88) | (_cmp_cached_16) | (_cmp_cached_162))
            # 15m down move, 1d high, 4h overbought
            & ((_cmp_cached_88) | (_cmp_cached_108) | (_cmp_cached_50))
            # 15m down move, 4h & 1d overbought
            & ((_cmp_cached_88) | (_cmp_cached_50) | (_cmp_cached_107))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_89) | (_cmp_cached_36) | (_cmp_cached_33))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_89) | (_cmp_cached_38) | (_cmp_cached_19))
            # 15m down move, 15m downtrend, 4h high
            & ((_cmp_cached_89) | (_cmp_cached_159) | (_cmp_cached_6))
            # 15m down move, 15m still high, 1d high
            & ((_cmp_cached_89) | (_cmp_cached_62) | (_cmp_cached_148))
            # 15m down move, 15m high, 4h high
            & ((_cmp_cached_89) | (_cmp_cached_210) | (_cmp_cached_64))
            # 15m down move, 4h high, 1h downtrend
            & ((_cmp_cached_244) | (_cmp_cached_47) | (_cmp_cached_239))
            # 15m down move, 4h high
            & ((_cmp_cached_89) | (_cmp_cached_72))
            # 15m & 1h down move, 15m high
            & ((_cmp_cached_184) | (_cmp_cached_38) | (_cmp_cached_76))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_184) | (_cmp_cached_21) | (_cmp_cached_12))
            # 15m down move, 15m still high, 4h overbought
            & ((_cmp_cached_184) | (_cmp_cached_31) | (_cmp_cached_20))
            # 15m down move, 15m still high, 1d overbought
            & ((_cmp_cached_184) | (_cmp_cached_31) | (_cmp_cached_70))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_184) | (_cmp_cached_40) | (_cmp_cached_20))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_184) | (_cmp_cached_64) | (_cmp_cached_20))
            # 15m still high, 4h high
            & ((_cmp_cached_304) | (_cmp_cached_47))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_305) | (_cmp_cached_25) | (_cmp_cached_163))
            # 1h & 4h down move, 15m still not low enough
            & ((_cmp_cached_13) | (_cmp_cached_151) | (_cmp_cached_152))
            # 1h & 4h down move, 15m downtrend
            & ((_cmp_cached_13) | (_cmp_cached_151) | (_cmp_cached_187))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_13) | (_cmp_cached_58) | (_cmp_cached_165))
            # 1h & 4h down move, 1d still high
            & ((_cmp_cached_13) | (_cmp_cached_58) | (_cmp_cached_56))
            # 1h & 4h down move, 4h stil high
            & ((_cmp_cached_13) | (_cmp_cached_100) | (_cmp_cached_169))
            # 1h ^ 4h down move, 1d downtrend
            & ((_cmp_cached_13) | (_cmp_cached_16) | (_cmp_cached_42))
            # 1h & 1d down move, 4h still high
            & ((_cmp_cached_13) | (_cmp_cached_153) | (_cmp_cached_165))
            # 1h & 1d down move, 1h downtrend
            & ((_cmp_cached_13) | (_cmp_cached_29) | (_cmp_cached_239))
            # 1h down move, 15m downtrend, 1h still high
            & ((_cmp_cached_13) | (_cmp_cached_43) | (_cmp_cached_110))
            # 1h down move, 15m still not low enough, 4h still high
            & ((_cmp_cached_13) | (_cmp_cached_10) | (_cmp_cached_165))
            # 1h down move, 1h still not low enough
            & ((_cmp_cached_13) | (_cmp_cached_161))
            # 1h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_13) | (_cmp_cached_35) | (_cmp_cached_57))
            # 1h down move, 4h high
            & ((_cmp_cached_13) | (_cmp_cached_64))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_7) | (_cmp_cached_55) | (_cmp_cached_60))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_7) | (_cmp_cached_58) | (_cmp_cached_120))
            # 1h & 4h down move, 4h downtrend
            & ((_cmp_cached_7) | (_cmp_cached_58) | (_cmp_cached_69))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_7) | (_cmp_cached_25) | (_cmp_cached_98))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_7) | (_cmp_cached_21) | (_cmp_cached_169))
            # 1h down move, 1d high, 4h downtrend
            & ((_cmp_cached_7) | (_cmp_cached_94) | (_cmp_cached_103))
            # 1h down move, 4h downtrend
            & ((_cmp_cached_7) | (_cmp_cached_69))
            # 1h, 1d downtrend
            & ((_cmp_cached_7) | (_cmp_cached_42))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_163))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_98))
            # 1h & 4h down move, 15m still high
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_61))
            # 1h & 4h down move, 15m still not low enough
            & ((_cmp_cached_9) | (_cmp_cached_25) | (_cmp_cached_10))
            # 1h & 4h down move, 1h still not low enough
            & ((_cmp_cached_9) | (_cmp_cached_25) | (_cmp_cached_190))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_9) | (_cmp_cached_16) | (_cmp_cached_108))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_9) | (_cmp_cached_16) | (_cmp_cached_65))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_9) | (_cmp_cached_41) | (_cmp_cached_35))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_9) | (_cmp_cached_21) | (_cmp_cached_216))
            # 1h & 1d down move, 1h still high
            & ((_cmp_cached_9) | (_cmp_cached_153) | (_cmp_cached_28))
            # 1h & 1d down move, 4h high
            & ((_cmp_cached_9) | (_cmp_cached_29) | (_cmp_cached_64))
            # 1h & 1d downtrend, 1d overbought
            & ((_cmp_cached_9) | (_cmp_cached_198) | (_cmp_cached_95))
            # 1h down move, 1h downtrend, 1h still not low enough
            & ((_cmp_cached_9) | (_cmp_cached_306) | (_cmp_cached_150))
            # 1h down move, 1h downtrend, 1h still not low enough
            & ((_cmp_cached_9) | (_cmp_cached_306) | (_cmp_cached_161))
            # 1h down move, 1h downtrend
            & ((_cmp_cached_9) | (_cmp_cached_177))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_9) | (_cmp_cached_106) | (_cmp_cached_107))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_156))
            # 1h down move, 1d overbought
            & ((_cmp_cached_9) | (_cmp_cached_48))
            # 1h & 4h down move, 1h still not low enough
            & ((_cmp_cached_15) | (_cmp_cached_25) | (_cmp_cached_161))
            # 1h & 4h down move, 15m high
            & ((_cmp_cached_15) | (_cmp_cached_100) | (_cmp_cached_227))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_15) | (_cmp_cached_100) | (_cmp_cached_65))
            # 1h & 4h down mov, 1d overbought
            & ((_cmp_cached_15) | (_cmp_cached_41) | (_cmp_cached_48))
            # 1h down move, 1d downtrend, 1d high
            & ((_cmp_cached_15) | (_cmp_cached_224) | (_cmp_cached_74))
            # 1h down move, 1h still high
            & ((_cmp_cached_15) | (_cmp_cached_26))
            # 1h down move, 1d high, 4h downtrend
            & ((_cmp_cached_15) | (_cmp_cached_106) | (_cmp_cached_69))
            # 1h down move, 1d high, 1d downtrend
            & ((_cmp_cached_15) | (_cmp_cached_106) | (_cmp_cached_57))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_15) | (_cmp_cached_94) | (_cmp_cached_70))
            # 1h down move, 1h still high
            & ((_cmp_cached_15) | (_cmp_cached_28))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_30) | (_cmp_cached_16) | (_cmp_cached_108))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_30) | (_cmp_cached_91) | (_cmp_cached_115))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_30) | (_cmp_cached_24) | (_cmp_cached_48))
            # 1h down move, 4h still high
            & ((_cmp_cached_30) | (_cmp_cached_96))
            # 1h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_30) | (_cmp_cached_165) | (_cmp_cached_195))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_30) | (_cmp_cached_64) | (_cmp_cached_50))
            # 1h down move, 1h & 1d high
            & ((_cmp_cached_11) | (_cmp_cached_24) | (_cmp_cached_94))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_11) | (_cmp_cached_99) | (_cmp_cached_47))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_99) | (_cmp_cached_48))
            # 1h down move, 1h still not low enough, 4h still high
            & ((_cmp_cached_11) | (_cmp_cached_161) | (_cmp_cached_35))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_11) | (_cmp_cached_12) | (_cmp_cached_65))
            # 1h down move, 1h still high, 1h downtrend
            & ((_cmp_cached_11) | (_cmp_cached_110) | (_cmp_cached_264))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_11) | (_cmp_cached_46) | (_cmp_cached_20))
            # 1h down move, 1h still high, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_59) | (_cmp_cached_52))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_11) | (_cmp_cached_12) | (_cmp_cached_20))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_12) | (_cmp_cached_216))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_32) | (_cmp_cached_41) | (_cmp_cached_123))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_32) | (_cmp_cached_41) | (_cmp_cached_122))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_32) | (_cmp_cached_99) | (_cmp_cached_24))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_32) | (_cmp_cached_99) | (_cmp_cached_46))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_32) | (_cmp_cached_24) | (_cmp_cached_51))
            # 1h down move, 1h high
            & ((_cmp_cached_32) | (_cmp_cached_33))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_32) | (_cmp_cached_46) | (_cmp_cached_20))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_32) | (_cmp_cached_108) | (_cmp_cached_111))
            # 1h down move, 1d high, 4h downtrend
            & ((_cmp_cached_32) | (_cmp_cached_94) | (_cmp_cached_213))
            # 1h down move, 1d high, 4h overbought
            & ((_cmp_cached_32) | (_cmp_cached_27) | (_cmp_cached_67))
            # 1h down move, 1h & 4h still high
            & ((_cmp_cached_32) | (_cmp_cached_28) | (_cmp_cached_35))
            # 1h down move, 1h highm 1d overbought
            & ((_cmp_cached_32) | (_cmp_cached_123) | (_cmp_cached_70))
            # 1h down move, 4h overbought
            & ((_cmp_cached_32) | (_cmp_cached_86))
            # 4h down move, 1d downtrend
            & ((_cmp_cached_41) | (_cmp_cached_42))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_34) | (_cmp_cached_24) | (_cmp_cached_113))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_34) | (_cmp_cached_24) | (_cmp_cached_195))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_34) | (_cmp_cached_47) | (_cmp_cached_196))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_34) | (_cmp_cached_6) | (_cmp_cached_20))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_34) | (_cmp_cached_64) | (_cmp_cached_50))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_34) | (_cmp_cached_27) | (_cmp_cached_48))
            # 1h down move, 1h still high, 1d overbought
            & ((_cmp_cached_34) | (_cmp_cached_59) | (_cmp_cached_111))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_36) | (_cmp_cached_250) | (_cmp_cached_248))
            # 1h down move, 15m high, 1h high
            & ((_cmp_cached_36) | (_cmp_cached_210) | (_cmp_cached_24))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_36) | (_cmp_cached_33) | (_cmp_cached_63))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_36) | (_cmp_cached_19) | (_cmp_cached_20))
            # 1h down move, 1h & 4h overbought
            & ((_cmp_cached_36) | (_cmp_cached_82) | (_cmp_cached_50))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_38) | (_cmp_cached_197) | (_cmp_cached_111))
            # 1h down move, 1h high & overbought
            & ((_cmp_cached_38) | (_cmp_cached_24) | (_cmp_cached_82))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_38) | (_cmp_cached_6) | (_cmp_cached_113))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_117) | (_cmp_cached_78) | (_cmp_cached_102))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_117) | (_cmp_cached_6) | (_cmp_cached_196))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_117) | (_cmp_cached_162) | (_cmp_cached_194))
            # 1h down move, 15m high, 1h high
            & ((_cmp_cached_174) | (_cmp_cached_210) | (_cmp_cached_19))
            # 1h down move, 1h high & overbought
            & ((_cmp_cached_174) | (_cmp_cached_78) | (_cmp_cached_82))
            # 4h down move, 1h still not low enough, 4h downtrend
            & ((_cmp_cached_151) | (_cmp_cached_190) | (_cmp_cached_103))
            # 4h down move, 1h & 4h downtrend
            & ((_cmp_cached_151) | (_cmp_cached_109) | (_cmp_cached_103))
            # 4h down move, 1d high, 4h downtrend
            & ((_cmp_cached_55) | (_cmp_cached_108) | (_cmp_cached_93))
            # 4h down move, 1h still high
            & ((_cmp_cached_55) | (_cmp_cached_59))
            # 4h down move, 4h & 1d downtrend
            & ((_cmp_cached_55) | (_cmp_cached_219) | (_cmp_cached_57))
            # 4h & 1d down move, 1d overbought
            & ((_cmp_cached_58) | (_cmp_cached_198) | (_cmp_cached_95))
            # 4h down move, 1d still high, 1d downtrend
            & ((_cmp_cached_58) | (_cmp_cached_238) | (_cmp_cached_102))
            # 4h down move, 1d high, 4h downtrend
            & ((_cmp_cached_58) | (_cmp_cached_131) | (_cmp_cached_69))
            # 4h down move, 15m high, 15m downtrend
            & ((_cmp_cached_58) | (_cmp_cached_222) | (_cmp_cached_261))
            # 4h down move, 1h still high, 1d downtrend
            & ((_cmp_cached_58) | (_cmp_cached_28) | (_cmp_cached_57))
            # 4h down move, 1h high
            & ((_cmp_cached_58) | (_cmp_cached_37))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_58) | (_cmp_cached_165) | (_cmp_cached_57))
            # 4h down move, 4h downtrend, 1d overbought
            & ((_cmp_cached_58) | (_cmp_cached_103) | (_cmp_cached_52))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_25) | (_cmp_cached_104) | (_cmp_cached_199))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_25) | (_cmp_cached_125) | (_cmp_cached_108))
            # 4h down move, 1h high
            & ((_cmp_cached_25) | (_cmp_cached_26))
            # 4h down move, 1h still high, 1d downtrend
            & ((_cmp_cached_25) | (_cmp_cached_59) | (_cmp_cached_102))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_25) | (_cmp_cached_39) | (_cmp_cached_167))
            # 4h down move, 15m still high
            & ((_cmp_cached_100) | (_cmp_cached_307))
            # 4h down move, 1h still not low enough, 1d downtrend
            & ((_cmp_cached_100) | (_cmp_cached_150) | (_cmp_cached_57))
            # 4h down move, 4h still high, 1d high
            & ((_cmp_cached_100) | (_cmp_cached_122) | (_cmp_cached_27))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_100) | (_cmp_cached_108) | (_cmp_cached_63))
            # 4h down move, 15m still high, 4h high
            & ((_cmp_cached_16) | (_cmp_cached_31) | (_cmp_cached_17))
            # 4h down move, 1h & 4h still high
            & ((_cmp_cached_16) | (_cmp_cached_28) | (_cmp_cached_165))
            # 4h dowqn move, 4h still high, 1d downtrend
            & ((_cmp_cached_16) | (_cmp_cached_124) | (_cmp_cached_102))
            # 4h down move, 4h high, 1d overbought
            & ((_cmp_cached_41) | (_cmp_cached_77) | (_cmp_cached_107))
            # 4h down move, 1h high, 4h downtrend
            & ((_cmp_cached_41) | (_cmp_cached_24) | (_cmp_cached_93))
            # 4h down move, 4h & 1d downtrend
            & ((_cmp_cached_181) | (_cmp_cached_17) | (_cmp_cached_27))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_181) | (_cmp_cached_94) | (_cmp_cached_63))
            # 4h down move, 1h high, 1d downtrend
            & ((_cmp_cached_181) | (_cmp_cached_19) | (_cmp_cached_57))
            # 4h down move, 4h & 1d overbought
            & ((_cmp_cached_181) | (_cmp_cached_50) | (_cmp_cached_107))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_99) | (_cmp_cached_169) | (_cmp_cached_102))
            # 4h down move, 4h high, 1d overbought
            & ((_cmp_cached_99) | (_cmp_cached_17) | (_cmp_cached_52))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_99) | (_cmp_cached_35) | (_cmp_cached_102))
            # 4h down move, 1h high, 1d overbought
            & ((_cmp_cached_71) | (_cmp_cached_49) | (_cmp_cached_70))
            # 4h down move, 4h high & overbought
            & ((_cmp_cached_71) | (_cmp_cached_64) | (_cmp_cached_20))
            # 1d down move, 1h high & overbought
            & ((_cmp_cached_192) | (_cmp_cached_49) | (_cmp_cached_82))
            # 1d down move, 1h high & overbought
            & ((_cmp_cached_125) | (_cmp_cached_106) | (_cmp_cached_63))
            # 1d down move, 4h high & overbought
            & ((_cmp_cached_198) | (_cmp_cached_77) | (_cmp_cached_51))
            # 1h downtrend, 1h high
            & ((_cmp_cached_306) | (_cmp_cached_33))
            # 4h & 1d downtrend, 1d high
            & ((_cmp_cached_189) | (_cmp_cached_224) | (_cmp_cached_60))
            # 1d downtrend, 1d high & overbought
            & ((_cmp_cached_224) | (_cmp_cached_131) | (_cmp_cached_48))
            # 1d downtrend, 1d high & overbought
            & ((_cmp_cached_202) | (_cmp_cached_131) | (_cmp_cached_167))
            # 15m still high, 1h overbought
            & ((_cmp_cached_31) | (_cmp_cached_54))
            # 15m still high, 4h overbought
            & ((_cmp_cached_31) | (_cmp_cached_67))
            # 15m still high, 1h high
            & ((_cmp_cached_62) | (_cmp_cached_45))
            # 15m still high, 4h high & overbought
            & ((_cmp_cached_62) | (_cmp_cached_17) | (_cmp_cached_51))
            # 15m still high, 4h downtrend, 1d overbought
            & ((_cmp_cached_62) | (_cmp_cached_69) | (_cmp_cached_52))
            # 1h still high, 4h & 1d downtrend
            & ((_cmp_cached_110) | (_cmp_cached_69) | (_cmp_cached_65))
            # 1h high, 4h high, 1h overbought
            & ((_cmp_cached_24) | (_cmp_cached_6) | (_cmp_cached_79))
            # 1h & 4h high, 4h overbought
            & ((_cmp_cached_24) | (_cmp_cached_6) | (_cmp_cached_113))
            # 1h & 1d high, 1h overbought
            & ((_cmp_cached_24) | (_cmp_cached_106) | (_cmp_cached_79))
            # 1h high, 1h & 4h overbought
            & ((_cmp_cached_24) | (_cmp_cached_82) | (_cmp_cached_113))
            # 1h high, 1d downtrend
            & ((_cmp_cached_33) | (_cmp_cached_65))
            # 4h still not low enough, 4h & 1d downtrend
            & ((_cmp_cached_98) | (_cmp_cached_69) | (_cmp_cached_195))
            # 4h still high, 1d high, 4h downtrend
            & ((_cmp_cached_122) | (_cmp_cached_27) | (_cmp_cached_103))
            # 4h high, 1h & 1d downtrend
            & ((_cmp_cached_17) | (_cmp_cached_129) | (_cmp_cached_57))
            # 4h & 1d high, 1d overbought
            & ((_cmp_cached_77) | (_cmp_cached_27) | (_cmp_cached_107))
            # 4h & 1d high, 4h overbought
            & ((_cmp_cached_6) | (_cmp_cached_27) | (_cmp_cached_50))
            # 4h high, 1h & 4h overbought
            & ((_cmp_cached_6) | (_cmp_cached_82) | (_cmp_cached_113))
            # 1d high, 4h & 1d downtrend
            & ((_cmp_cached_108) | (_cmp_cached_69) | (_cmp_cached_57))
            # 1d high, 1h & 4h downtrend
            & ((_cmp_cached_131) | (_cmp_cached_109) | (_cmp_cached_204))
            # 1d high, 1h & 1d overbought
            & ((_cmp_cached_131) | (_cmp_cached_79) | (_cmp_cached_48))
            # 1d high, 1h & 4h down move
            & ((_cmp_cached_27) | (_cmp_cached_205) | (_cmp_cached_83))
            # 1d high, 4h & 1d overbought
            & ((_cmp_cached_27) | (_cmp_cached_20) | (_cmp_cached_70))
            # 1h high, 4h & 1d overbought
            & ((_cmp_cached_49) | (_cmp_cached_20) | (_cmp_cached_48))
            # 4h still high, 4h & 1d downtrend
            & ((_cmp_cached_165) | (_cmp_cached_69) | (_cmp_cached_65))
            # 4h high, 1h & 1d downtrend
            & ((_cmp_cached_64) | (_cmp_cached_129) | (_cmp_cached_57))
            # 4h high, 4h & 1d overbought
            & ((_cmp_cached_64) | (_cmp_cached_20) | (_cmp_cached_70))
            # 4h high, 1h overbought, 1d downtrend
            & ((_cmp_cached_12) | (_cmp_cached_54) | (_cmp_cached_206))
            # 4h high, 4h overbought
            & ((_cmp_cached_12) | (_cmp_cached_50))
            # 4h high, 1h & 4h overbought
            & ((_cmp_cached_72) | (_cmp_cached_79) | (_cmp_cached_86))
            # 1d high, 4h & 1d overbought
            & ((_cmp_cached_39) | (_cmp_cached_113) | (_cmp_cached_48))
            # 1h & 4h overbought
            & ((_cmp_cached_158) | (_cmp_cached_67))
            # 1d green with top wick, 4h high
            & ((_cmp_cached_308) | (_cmp_cached_230) | (_cmp_cached_77))
            # 1d top wick, 4h down move, 1d overbought
            & ((_cmp_cached_233) | (_cmp_cached_21) | (_cmp_cached_112))
            # drop in last 20 days, 4h high
            & ((df["close"] > (df["high_max_20_1d"] * 0.10)) | (_cmp_cached_72))
            # drop in last 20 days, 1h high, 1d downtrend
            & ((df["close"] > (df["high_max_20_1d"] * 0.20)) | (_cmp_cached_24) | (_cmp_cached_206))
            # drop in last 20 days, 1d high, 1d downtrend
            & (
              (df["close"] > (df["high_max_20_1d"] * 0.20))
              | (_cmp_cached_148)
              | (_cmp_cached_149)
            )
          )

          # Logic
          long_entry_logic.append(
            (_cmp_cached_309)
            & (_cmp_cached_247)
            & (_cmp_cached_243)
            & (df["EMA_26"] > df["EMA_12"])
            & ((df["EMA_26"] - df["EMA_12"]) > (df["open"] * 0.022))
            & ((df["EMA_26"].shift() - df["EMA_12"].shift()) > (df["open"] / 100.0))
          )

        # Condition #101 - Rapid mode (Long).
        if long_entry_condition_index == 101:
          # Protections
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          long_entry_logic.append(df["protections_long_global"] == True)

          long_entry_logic.append(_cmp_cached_310)
          long_entry_logic.append(_cmp_cached_66)
          long_entry_logic.append(_cmp_cached_250)
          # big drop in the last hour
          long_entry_logic.append(df["close"] > (df["close_max_12"] * 0.50))
          # 5m & 4h down move, 1d downtrend
          long_entry_logic.append((_cmp_cached_8) | (_cmp_cached_58) | (_cmp_cached_57))
          # 5m & 4h down move, 15m still high
          long_entry_logic.append(
            (_cmp_cached_8) | (_cmp_cached_16) | (_cmp_cached_61)
          )
          # 5 & 15m down move, 1h high
          long_entry_logic.append(
            (_cmp_cached_157) | (_cmp_cached_90) | (_cmp_cached_49)
          )
          # 5m down move, 1h & 4h high
          long_entry_logic.append((_cmp_cached_157) | (_cmp_cached_45) | (_cmp_cached_46))
          # 15m & 1h down move, 4h still not low enough
          long_entry_logic.append(
            (_cmp_cached_1) | (_cmp_cached_7) | (_cmp_cached_124)
          )
          # 15m & 1h down move, 1d still high
          long_entry_logic.append((_cmp_cached_1) | (_cmp_cached_7) | (_cmp_cached_119))
          # 15m & 1h down move, 4h still high
          long_entry_logic.append((_cmp_cached_1) | (_cmp_cached_15) | (_cmp_cached_169))
          # 15m & 4h down move, 4h high
          long_entry_logic.append((_cmp_cached_1) | (_cmp_cached_32) | (_cmp_cached_172))
          # 15m & 1h down move, 1h still not low enough
          long_entry_logic.append(
            (_cmp_cached_1) | (_cmp_cached_34) | (_cmp_cached_161)
          )
          # 15m & 4h down move, 4h still not low enough
          long_entry_logic.append(
            (_cmp_cached_1) | (_cmp_cached_58) | (_cmp_cached_156)
          )
          # 15m & 4h down move, 1d downtrend
          long_entry_logic.append((_cmp_cached_1) | (_cmp_cached_58) | (_cmp_cached_57))
          # 15m & 4h down move, 4h still not low enough
          long_entry_logic.append((_cmp_cached_1) | (_cmp_cached_16) | (_cmp_cached_98))
          # 15m & 4h down move, 4h still not low enough
          long_entry_logic.append(
            (_cmp_cached_1) | (_cmp_cached_16) | (_cmp_cached_124)
          )
          # 15m down move, 15m still not low enough, 1h high
          long_entry_logic.append(
            (_cmp_cached_1) | (_cmp_cached_166) | (_cmp_cached_123)
          )
          # 15m down move, 15m still not low enough, 4h high
          long_entry_logic.append(
            (_cmp_cached_1) | (_cmp_cached_10) | (_cmp_cached_64)
          )
          # 15m down move, 4h high, 1d overbought
          long_entry_logic.append((_cmp_cached_1) | (_cmp_cached_17) | (_cmp_cached_70))
          # 15m & 1h & 1d down move
          long_entry_logic.append((_cmp_cached_3) | (_cmp_cached_9) | (_cmp_cached_104))
          # 15m down move, 1h still not low enough, 1d high
          long_entry_logic.append(
            (_cmp_cached_3) | (_cmp_cached_161) | (_cmp_cached_94)
          )
          # 15m & 1h down move, 1h still not low enough
          long_entry_logic.append(
            (_cmp_cached_3) | (_cmp_cached_32) | (_cmp_cached_161)
          )
          # 15m & 1h down move, 4h high
          long_entry_logic.append(
            (_cmp_cached_3) | (_cmp_cached_32) | (_cmp_cached_12)
          )
          # 15m & 1h down move, 4h high
          long_entry_logic.append(
            (_cmp_cached_3) | (_cmp_cached_36) | (_cmp_cached_12)
          )
          # 15m & 1h down move, 1h high
          long_entry_logic.append(
            (_cmp_cached_3) | (_cmp_cached_117) | (_cmp_cached_37)
          )
          # 15m & 1h down move, 4h high
          long_entry_logic.append(
            (_cmp_cached_3) | (_cmp_cached_117) | (_cmp_cached_72)
          )
          # 15m & 4h down move, 1d still high
          long_entry_logic.append(
            (_cmp_cached_3) | (_cmp_cached_55) | (_cmp_cached_56)
          )
          # 15m & 4h down move, 4h still high
          long_entry_logic.append(
            (_cmp_cached_3) | (_cmp_cached_181) | (_cmp_cached_35)
          )
          # 15m & 1d down move
          long_entry_logic.append((_cmp_cached_3) | (_cmp_cached_101))
          # 15m & 1d down move, 4h still not low enough
          long_entry_logic.append(
            (_cmp_cached_3) | (_cmp_cached_178) | (_cmp_cached_124)
          )
          # 15m down move, 1h still high, 4h high
          long_entry_logic.append(
            (_cmp_cached_3) | (_cmp_cached_26) | (_cmp_cached_72)
          )
          # 15m down move, 1h high & overbought
          long_entry_logic.append((_cmp_cached_3) | (_cmp_cached_33) | (_cmp_cached_82))
          # 15m down move, 1h high & overbought
          long_entry_logic.append(
            (_cmp_cached_3) | (_cmp_cached_19) | (_cmp_cached_82)
          )
          # 15m & 1h down move, 4h still high
          long_entry_logic.append(
            (_cmp_cached_5) | (_cmp_cached_30) | (_cmp_cached_35)
          )
          # 15m & 1h down move, 1h still not low enough
          long_entry_logic.append((_cmp_cached_5) | (_cmp_cached_11) | (_cmp_cached_160))
          # 15m & 1h down move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_5) | (_cmp_cached_32) | (_cmp_cached_28)
          )
          # 15m & 1h down move, 4h still high
          long_entry_logic.append(
            (_cmp_cached_5) | (_cmp_cached_32) | (_cmp_cached_35)
          )
          # 15m & 1h down move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_5) | (_cmp_cached_34) | (_cmp_cached_59)
          )
          # 15m & 1h down move, 1h high
          long_entry_logic.append((_cmp_cached_5) | (_cmp_cached_117) | (_cmp_cached_33))
          # 15m & 1h down move, 1h high
          long_entry_logic.append(
            (_cmp_cached_5) | (_cmp_cached_117) | (_cmp_cached_19)
          )
          # 15m & 4h down move, 15m still not low enough
          long_entry_logic.append(
            (_cmp_cached_5) | (_cmp_cached_58) | (_cmp_cached_311)
          )
          # 15m & 4h down move, 1d downtrend
          long_entry_logic.append((_cmp_cached_5) | (_cmp_cached_100) | (_cmp_cached_195))
          # 15m & 4h down move, 1d high
          long_entry_logic.append((_cmp_cached_5) | (_cmp_cached_16) | (_cmp_cached_131))
          # 15m & 4h down move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_5) | (_cmp_cached_41) | (_cmp_cached_59)
          )
          # 15m & 4h down move, 4h high
          long_entry_logic.append(
            (_cmp_cached_5) | (_cmp_cached_41) | (_cmp_cached_64)
          )
          # 15m & 1d down move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_5) | (_cmp_cached_121) | (_cmp_cached_59)
          )
          # 15m down move, 15m still not low enough, 1h still high
          long_entry_logic.append(
            (_cmp_cached_5) | (_cmp_cached_10) | (_cmp_cached_59)
          )
          # 15m down move, 1h still high, 4h high
          long_entry_logic.append(
            (_cmp_cached_5) | (_cmp_cached_59) | (_cmp_cached_47)
          )
          # 15m down move, 1h & 4h high
          long_entry_logic.append(
            (_cmp_cached_5) | (_cmp_cached_37) | (_cmp_cached_312)
          )
          # 15m & 1h down move, 15m still not low enough
          long_entry_logic.append(
            (_cmp_cached_84) | (_cmp_cached_15) | (_cmp_cached_152)
          )
          # 15m & 1h down move, 4h high
          long_entry_logic.append(
            (_cmp_cached_84) | (_cmp_cached_30) | (_cmp_cached_72)
          )
          # 15m & 1h down move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_84) | (_cmp_cached_11) | (_cmp_cached_28)
          )
          # 15m & 1h down move, 1h still high
          long_entry_logic.append((_cmp_cached_84) | (_cmp_cached_36) | (_cmp_cached_26))
          # 15m & 4h & 1d down move
          long_entry_logic.append((_cmp_cached_84) | (_cmp_cached_25) | (_cmp_cached_29))
          # 15m & 4h down move, 1h high
          long_entry_logic.append(
            (_cmp_cached_84) | (_cmp_cached_25) | (_cmp_cached_19)
          )
          # 15m & 4h down move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_84) | (_cmp_cached_100) | (_cmp_cached_59)
          )
          # 15m & 4h down move, 15m still not low enough
          long_entry_logic.append((_cmp_cached_84) | (_cmp_cached_16) | (_cmp_cached_10))
          # 15m & 4h down move, 4h still high
          long_entry_logic.append((_cmp_cached_84) | (_cmp_cached_99) | (_cmp_cached_122))
          # 1h & 1d down move, 1d overbought
          long_entry_logic.append((_cmp_cached_15) | (_cmp_cached_192) | (_cmp_cached_95))
          # 15m down move, 15m still not low enough, 1h high
          long_entry_logic.append(
            (_cmp_cached_84) | (_cmp_cached_179) | (_cmp_cached_19)
          )
          # 15m down move, 4h high & overbought
          long_entry_logic.append((_cmp_cached_84) | (_cmp_cached_77) | (_cmp_cached_113))
          # 15m down move, 1h & 4h high
          long_entry_logic.append(
            (_cmp_cached_84) | (_cmp_cached_37) | (_cmp_cached_47)
          )
          # 15m & 1h down move, 4h high
          long_entry_logic.append(
            (_cmp_cached_87) | (_cmp_cached_32) | (_cmp_cached_72)
          )
          # 15m & 1d down move, 1h high
          long_entry_logic.append(
            (_cmp_cached_87) | (_cmp_cached_104) | (_cmp_cached_37)
          )
          # 15m down move, 1d high & overbought
          long_entry_logic.append((_cmp_cached_87) | (_cmp_cached_27) | (_cmp_cached_167))
          # 15m down move, 1h high, 1d downtrend
          long_entry_logic.append(
            (_cmp_cached_87) | (_cmp_cached_19) | (_cmp_cached_57)
          )
          # 15m down move, 1d high & overbought
          long_entry_logic.append(
            (_cmp_cached_87) | (_cmp_cached_19) | (_cmp_cached_167)
          )
          # 15m & 1h down move, 1h high
          long_entry_logic.append(
            (_cmp_cached_88) | (_cmp_cached_11) | (_cmp_cached_123)
          )
          # 15m & 1h down move, 1h high
          long_entry_logic.append((_cmp_cached_88) | (_cmp_cached_53) | (_cmp_cached_45))
          # 15m down move, 15m still not low enough, 4h high
          long_entry_logic.append(
            (_cmp_cached_88) | (_cmp_cached_179) | (_cmp_cached_40)
          )
          # 15m down move, 15m still not low enough, 1h high
          long_entry_logic.append(
            (_cmp_cached_88) | (_cmp_cached_152) | (_cmp_cached_33)
          )
          # 15m & 1h down move, 1h high
          long_entry_logic.append((_cmp_cached_89) | (_cmp_cached_38) | (_cmp_cached_24))
          # 1h & 4h down move, 15m downtrend
          long_entry_logic.append((_cmp_cached_13) | (_cmp_cached_151) | (_cmp_cached_187))
          # 1h & 4h & 1d down move
          long_entry_logic.append((_cmp_cached_13) | (_cmp_cached_25) | (_cmp_cached_121))
          # 1h & 4h down move, 4h high
          long_entry_logic.append((_cmp_cached_13) | (_cmp_cached_99) | (_cmp_cached_17))
          # 1h & 4h down move, 4h downtrend
          long_entry_logic.append((_cmp_cached_7) | (_cmp_cached_55) | (_cmp_cached_69))
          # 1h & 4h down move, 4h downtrend
          long_entry_logic.append((_cmp_cached_7) | (_cmp_cached_25) | (_cmp_cached_103))
          # 1h & 4h down move, 4h still not low enough
          long_entry_logic.append(
            (_cmp_cached_7) | (_cmp_cached_100) | (_cmp_cached_156)
          )
          # 1h & 4h down move, 1d low
          long_entry_logic.append((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_143))
          # 1h & 4h down move, 4h still not low enough
          long_entry_logic.append((_cmp_cached_9) | (_cmp_cached_25) | (_cmp_cached_120))
          # 1h & 4h down move, 4h still not low enough
          long_entry_logic.append(
            (_cmp_cached_9) | (_cmp_cached_16) | (_cmp_cached_124)
          )
          # 1h & 1d down move, 5m moving down
          long_entry_logic.append((_cmp_cached_9) | (_cmp_cached_29) | (_cmp_cached_291))
          # 1h down move, 4h downtrend
          long_entry_logic.append((_cmp_cached_9) | (_cmp_cached_103))
          # 1h down move, 1d downtrend
          long_entry_logic.append((_cmp_cached_9) | (_cmp_cached_102))
          # 1h & 4h & 1d down move
          long_entry_logic.append((_cmp_cached_15) | (_cmp_cached_100) | (_cmp_cached_178))
          # 1h & 4h down move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_15) | (_cmp_cached_41) | (_cmp_cached_28)
          )
          # 1h & 4h down move, 1h still not low enough
          long_entry_logic.append(
            (_cmp_cached_15) | (_cmp_cached_181) | (_cmp_cached_161)
          )
          # 1h & 4h down move, 1h still high
          long_entry_logic.append((_cmp_cached_15) | (_cmp_cached_153) | (_cmp_cached_110))
          # 1h down move, 1d high & overbought
          long_entry_logic.append((_cmp_cached_30) | (_cmp_cached_94) | (_cmp_cached_70))
          # 1h down move, 1h still not low enough, 4h high
          long_entry_logic.append(
            (_cmp_cached_30) | (_cmp_cached_190) | (_cmp_cached_77)
          )
          # 1h & 4h down move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_11) | (_cmp_cached_16) | (_cmp_cached_59)
          )
          # 1h & 4h down move, 1d high
          long_entry_logic.append(
            (_cmp_cached_11) | (_cmp_cached_41) | (_cmp_cached_74)
          )
          # 1h & 4h down move, 1h high
          long_entry_logic.append(
            (_cmp_cached_11) | (_cmp_cached_71) | (_cmp_cached_12)
          )
          # 1h & 4h down move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_32) | (_cmp_cached_181) | (_cmp_cached_59)
          )
          # 1h down move, 4h high, 1d overbought
          long_entry_logic.append((_cmp_cached_32) | (_cmp_cached_46) | (_cmp_cached_52))
          # 1h down move, 4h & 1d high
          long_entry_logic.append((_cmp_cached_32) | (_cmp_cached_77) | (_cmp_cached_27))
          # 1h down move, 15m high
          long_entry_logic.append((_cmp_cached_34) | (_cmp_cached_180))
          # 1h down move, 1h high, 1d overbought
          long_entry_logic.append((_cmp_cached_34) | (_cmp_cached_24) | (_cmp_cached_167))
          # 1h down move, 1h & 4h high
          long_entry_logic.append((_cmp_cached_36) | (_cmp_cached_33) | (_cmp_cached_6))
          # 1h down move, 1h high & overbought
          long_entry_logic.append(
            (_cmp_cached_174) | (_cmp_cached_19) | (_cmp_cached_82)
          )
          # 1h down move, 4h high
          long_entry_logic.append((_cmp_cached_53) | (_cmp_cached_46))
          # 4h down move, 15m still high
          long_entry_logic.append((_cmp_cached_55) | (_cmp_cached_155))
          # 4h down move, 1d still high, 1d downtrend
          long_entry_logic.append((_cmp_cached_58) | (_cmp_cached_119) | (_cmp_cached_57))
          # 4h down move, 15m 4h still high
          long_entry_logic.append(
            (_cmp_cached_58) | (_cmp_cached_155) | (_cmp_cached_122)
          )
          # 4h & 1d down move, 4h high
          long_entry_logic.append((_cmp_cached_25) | (_cmp_cached_121) | (_cmp_cached_17))
          # 4h down move, 1h still high
          long_entry_logic.append((_cmp_cached_25) | (_cmp_cached_26))
          # 4h down move, 4h still high
          long_entry_logic.append((_cmp_cached_25) | (_cmp_cached_122))
          # 4h down move, 1d high & overbought
          long_entry_logic.append(
            (_cmp_cached_25) | (_cmp_cached_39) | (_cmp_cached_167)
          )
          # 4h down move, 4h & 1d downtrend
          long_entry_logic.append((_cmp_cached_25) | (_cmp_cached_93) | (_cmp_cached_149))
          # 4h down move, 4h & 1d downtrend
          long_entry_logic.append((_cmp_cached_100) | (_cmp_cached_69) | (_cmp_cached_102))
          # 4h dowqn move, 4h still high, 1d downtrend
          long_entry_logic.append(
            (_cmp_cached_16) | (_cmp_cached_35) | (_cmp_cached_102)
          )
          # 4h down move, 4h & 1d high
          long_entry_logic.append((_cmp_cached_21) | (_cmp_cached_77) | (_cmp_cached_27))
          # 4h & 1d down move, 4h still high
          long_entry_logic.append(
            (_cmp_cached_181) | (_cmp_cached_153) | (_cmp_cached_35)
          )
          # 4h down move, 4h high, 1d downtrend
          long_entry_logic.append(
            (_cmp_cached_181) | (_cmp_cached_64) | (_cmp_cached_194)
          )
          # 4h down move, 4h still high
          long_entry_logic.append((_cmp_cached_71) | (_cmp_cached_165))
          # 4h down move, 4h overbought
          long_entry_logic.append((_cmp_cached_71) | (_cmp_cached_20))
          # 1d down move, 1h still high, 4h high
          long_entry_logic.append((_cmp_cached_104) | (_cmp_cached_26) | (_cmp_cached_47))
          # 1d down move, 1h high & overbought
          long_entry_logic.append(
            (_cmp_cached_192) | (_cmp_cached_49) | (_cmp_cached_82)
          )
          # 1d down move, 4h high, 1d overbought
          long_entry_logic.append(
            (_cmp_cached_198) | (_cmp_cached_72) | (_cmp_cached_95)
          )
          # 4h still high, 4h moving lower, 4h overbought
          long_entry_logic.append(
            (_cmp_cached_122) | (df["AROONU_14_4h"] > df["AROONU_14_4h"].shift(48)) | (_cmp_cached_113)
          )
          # 1h high, 1d downtrend
          long_entry_logic.append((_cmp_cached_106) | (_cmp_cached_102))
          # 1d high, 4h & 1d overbought
          long_entry_logic.append((_cmp_cached_131) | (_cmp_cached_83) | (_cmp_cached_112))
          # 1d high, 4h & 1d overbought
          long_entry_logic.append((_cmp_cached_27) | (_cmp_cached_50) | (_cmp_cached_167))
          # 1h high, 4h downtrend
          long_entry_logic.append((_cmp_cached_19) | (_cmp_cached_69))
          # 1h high, 4h overbought
          long_entry_logic.append((_cmp_cached_19) | (_cmp_cached_67))
          # 4h high, 4h & 1d overbought
          long_entry_logic.append(
            (_cmp_cached_12) | (_cmp_cached_51) | (_cmp_cached_70)
          )
          # 1d high, 4h & 1d overbought
          long_entry_logic.append(
            (_cmp_cached_74) | (_cmp_cached_83) | (_cmp_cached_112)
          )
          # 1d red, 4h down move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_313) | (_cmp_cached_41) | (_cmp_cached_59)
          )
          # pump, drop but not yet near the previous lows
          long_entry_logic.append(
            (((df["high_max_24_4h"] - df["low_min_24_4h"]) / df["low_min_24_4h"]) < 2.0)
            | (df["close"] > (df["high_max_6_4h"] * 0.75))
            | (df["close"] < (df["low_min_24_4h"] * 1.25))
          )
          # 4h high, drop but not yet near the previous lows
          long_entry_logic.append(
            (_cmp_cached_17)
            | (df["close"] > (df["high_max_6_4h"] * 0.80))
            | (df["close"] < (df["low_min_24_4h"] * 1.25))
          )
          # 4h high, drop but not yet near the previous lows
          long_entry_logic.append(
            (_cmp_cached_77)
            | (df["close"] > (df["high_max_6_4h"] * 0.85))
            | (df["close"] < (df["low_min_24_4h"] * 1.25))
          )
          # 1h down move, drop but not yet near the previous lows
          long_entry_logic.append(
            (_cmp_cached_32)
            | (df["close"] > (df["high_max_12_4h"] * 0.50))
            | (df["close"] < (df["low_min_24_4h"] * 1.25))
          )
          # 1d overbought, drop but not yet near the previous lows
          long_entry_logic.append(
            (_cmp_cached_107)
            | (df["close"] > (df["high_max_6_1d"] * 0.70))
            | (df["close"] < (df["low_min_12_1d"] * 1.25))
          )
          # big drop in last 6 hours, 1d overbought
          long_entry_logic.append((df["close"] > (df["high_max_6_1h"] * 0.65)) | (_cmp_cached_107))
          # big drop in last 4 hours, 4h still not low enough
          long_entry_logic.append(
            (df["close"] > (df["high_max_24_4h"] * 0.50)) | (_cmp_cached_124)
          )
          # big drop in the last 4 days, 4h down move
          long_entry_logic.append((df["close"] > (df["high_max_24_4h"] * 0.20)) | (_cmp_cached_100))
          # big drop in the last 6 days, 1d down move
          long_entry_logic.append((df["close"] > (df["high_max_6_1d"] * 0.30)) | (_cmp_cached_29))
          # big drop in the last 12 days, 4h high
          long_entry_logic.append(
            (df["close"] > (df["high_max_12_1d"] * 0.50)) | (_cmp_cached_72)
          )
          # big drop in the last 30 days, 4h down move
          long_entry_logic.append((df["close"] > (df["high_max_20_1d"] * 0.10)) | (_cmp_cached_41))
          # big drop in the last 20 days, 1h still high
          long_entry_logic.append((df["close"] > (df["high_max_20_1d"] * 0.05)) | (_cmp_cached_26))
          # big drop in the last 20 days, 1d high, 1d downtrend
          long_entry_logic.append(
            (df["close"] > (df["high_max_20_1d"] * 0.20))
            | (_cmp_cached_148)
            | (_cmp_cached_149)
          )
          # big drop in the last 30 days, 1h down move
          long_entry_logic.append((df["close"] > (df["high_max_30_1d"] * 0.25)) | (_cmp_cached_15))

          # Logic
          long_entry_logic.append(_cmp_cached_0)
          long_entry_logic.append(_cmp_cached_271)
          long_entry_logic.append(_cmp_cached_243)
          long_entry_logic.append(_cmp_cached_237)
          long_entry_logic.append(df["close"] < (df["SMA_16"] * 0.946))
          long_entry_logic.append(_cmp_cached_62)

        # Condition #102 - Rapid mode (Long).
        if long_entry_condition_index == 102:
          # Protections
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          long_entry_logic.append(df["protections_long_global"] == True)

          long_entry_logic.append(_cmp_cached_254)
          long_entry_logic.append(_cmp_cached_3)
          long_entry_logic.append(_cmp_cached_9)
          long_entry_logic.append(_cmp_cached_58)
          # 5m & 15m down move, 4h still high
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp_cached_84) | (_cmp_cached_35)
          )
          # 5m & 15m down move, 15m still high
          long_entry_logic.append((_cmp_cached_0) | (_cmp_cached_87) | (_cmp_cached_31))
          # 5m & 15m down move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp_cached_88) | (_cmp_cached_28)
          )
          # 5m & 1h down move, 4h still high
          long_entry_logic.append((_cmp_cached_0) | (_cmp_cached_11) | (_cmp_cached_122))
          # 5m & 4h & 1d down move
          long_entry_logic.append((_cmp_cached_0) | (_cmp_cached_100) | (_cmp_cached_104))
          # 5m & 1d down move, 15m still high
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp_cached_153) | (_cmp_cached_155)
          )
          # 5m down move, 15m high
          long_entry_logic.append((_cmp_cached_0) | (_cmp_cached_76))
          # 5m down move, 15m & 1h still high
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp_cached_155) | (_cmp_cached_110)
          )
          # 5m down move, 1h high
          long_entry_logic.append(
            (_cmp_cached_0) | (_cmp_cached_24) | (_cmp_cached_59)
          )
          # 5m & 1h down move, 1h high
          long_entry_logic.append(
            (_cmp_cached_8) | (_cmp_cached_36) | (_cmp_cached_123)
          )
          # 5m & 4h down move, 4h high
          long_entry_logic.append((_cmp_cached_8) | (_cmp_cached_99) | (_cmp_cached_17))
          # 5m down move, 15m still high, 1h high
          long_entry_logic.append((_cmp_cached_8) | (_cmp_cached_292) | (_cmp_cached_33))
          # 5m down move, 15m still high, 1h high
          long_entry_logic.append(
            (_cmp_cached_8) | (_cmp_cached_31) | (_cmp_cached_59)
          )
          # 5m down move, 15m & 4h high
          long_entry_logic.append(
            (_cmp_cached_8) | (_cmp_cached_92) | (_cmp_cached_72)
          )
          # 5m & 15m down move, 4h high
          long_entry_logic.append((_cmp_cached_157) | (_cmp_cached_87) | (_cmp_cached_46))
          # 5m & 15m down move, 1d high
          long_entry_logic.append(
            (_cmp_cached_157) | (_cmp_cached_87) | (_cmp_cached_74)
          )
          # 5m & 15m down move, 1h high
          long_entry_logic.append(
            (_cmp_cached_157) | (_cmp_cached_88) | (_cmp_cached_49)
          )
          # 5m & 1h down move, 4h still high
          long_entry_logic.append(
            (_cmp_cached_157) | (_cmp_cached_32) | (_cmp_cached_35)
          )
          # 5m down move, 1h & 4h high
          long_entry_logic.append((_cmp_cached_157) | (_cmp_cached_45) | (_cmp_cached_46))
          # 5m down move, 4h high, 1d high
          long_entry_logic.append(
            (_cmp_cached_157) | (_cmp_cached_40) | (_cmp_cached_39)
          )
          # 5m down move, 15m still high, 1h high
          long_entry_logic.append(
            (_cmp_cached_209) | (_cmp_cached_292) | (_cmp_cached_49)
          )
          # 5m down move, 15m still high, 4h high
          long_entry_logic.append(
            (_cmp_cached_209) | (_cmp_cached_292) | (_cmp_cached_72)
          )
          # 15m down move, 15m still not low enough, 1h high
          long_entry_logic.append(
            (_cmp_cached_1) | (_cmp_cached_166) | (_cmp_cached_123)
          )
          # 15m & 1h down move, 1d high
          long_entry_logic.append((_cmp_cached_5) | (_cmp_cached_30) | (_cmp_cached_106))
          # 15m & 1h down move, 1h still not low enough
          long_entry_logic.append(
            (_cmp_cached_5) | (_cmp_cached_30) | (_cmp_cached_190)
          )
          # 15m & 1h down move, 1h still not low enough
          long_entry_logic.append((_cmp_cached_5) | (_cmp_cached_11) | (_cmp_cached_150))
          # 15m & 1h down move, 1h still high
          long_entry_logic.append((_cmp_cached_5) | (_cmp_cached_34) | (_cmp_cached_26))
          # 15m & 1h down move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_5) | (_cmp_cached_34) | (_cmp_cached_59)
          )
          # 15m & 1h down move, 4h still high
          long_entry_logic.append((_cmp_cached_5) | (_cmp_cached_34) | (_cmp_cached_17))
          # 15m & 4h down move, 4h still not low enough
          long_entry_logic.append((_cmp_cached_5) | (_cmp_cached_25) | (_cmp_cached_98))
          # 15m& 4h down move, 15m still high
          long_entry_logic.append(
            (_cmp_cached_5) | (_cmp_cached_25) | (_cmp_cached_155)
          )
          # 15m & 4h down move, 15m still high
          long_entry_logic.append((_cmp_cached_5) | (_cmp_cached_100) | (_cmp_cached_62))
          # 15m & 4h down move, 4h still not low enough
          long_entry_logic.append(
            (_cmp_cached_5) | (_cmp_cached_100) | (_cmp_cached_124)
          )
          # 15m & 4h down move, 4h still high
          long_entry_logic.append((_cmp_cached_5) | (_cmp_cached_16) | (_cmp_cached_122))
          # 15m & 4h down move, 4h still high
          long_entry_logic.append(
            (_cmp_cached_5) | (_cmp_cached_41) | (_cmp_cached_165)
          )
          # 15m & 4h down move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_5) | (_cmp_cached_100) | (_cmp_cached_28)
          )
          # 15m & 4h down move, 1d high
          long_entry_logic.append((_cmp_cached_5) | (_cmp_cached_16) | (_cmp_cached_131))
          # 15m & 4h down move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_5) | (_cmp_cached_41) | (_cmp_cached_59)
          )
          # 15m & 4h down move, 4h high
          long_entry_logic.append((_cmp_cached_5) | (_cmp_cached_41) | (_cmp_cached_17))
          # 15m & 1d down move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_5) | (_cmp_cached_121) | (_cmp_cached_59)
          )
          # 15m down move, 15m still not low enough, 1h high
          long_entry_logic.append(
            (_cmp_cached_5) | (_cmp_cached_10) | (_cmp_cached_19)
          )
          # 15m down move, 1h high, 4h overbought
          long_entry_logic.append((_cmp_cached_5) | (_cmp_cached_24) | (_cmp_cached_86))
          # 15m down move, 1d high & overbought
          long_entry_logic.append((_cmp_cached_5) | (_cmp_cached_108) | (_cmp_cached_167))
          # 15m & 1h down move, 1h still high
          long_entry_logic.append((_cmp_cached_5) | (_cmp_cached_32) | (_cmp_cached_110))
          # 15m & 1h down move, 1h still high
          long_entry_logic.append((_cmp_cached_84) | (_cmp_cached_36) | (_cmp_cached_26))
          # 15m & 1h down move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_84) | (_cmp_cached_38) | (_cmp_cached_59)
          )
          # 15m & 1h down move, 4h high
          long_entry_logic.append((_cmp_cached_84) | (_cmp_cached_38) | (_cmp_cached_77))
          # 15m & 1h down move, 15m still not low enough
          long_entry_logic.append(
            (_cmp_cached_84) | (_cmp_cached_38) | (_cmp_cached_61)
          )
          # 15m & 4h & 1d down move
          long_entry_logic.append((_cmp_cached_84) | (_cmp_cached_25) | (_cmp_cached_29))
          # 15m & 4h down move, 4h still high
          long_entry_logic.append((_cmp_cached_84) | (_cmp_cached_100) | (_cmp_cached_122))
          # 15m & 4h down move, 15m still not low enough
          long_entry_logic.append(
            (_cmp_cached_84) | (_cmp_cached_41) | (_cmp_cached_314)
          )
          # 15m & 4h down move, 4h high
          long_entry_logic.append((_cmp_cached_84) | (_cmp_cached_21) | (_cmp_cached_40))
          # 15m & 4h down move, 4h high
          long_entry_logic.append(
            (_cmp_cached_84) | (_cmp_cached_21) | (_cmp_cached_64)
          )
          # 15m & 4h down move, 4h still high
          long_entry_logic.append(
            (_cmp_cached_84) | (_cmp_cached_91) | (_cmp_cached_35)
          )
          # 15m down move, 15m still not low enough, 4h high
          long_entry_logic.append(
            (_cmp_cached_84) | (_cmp_cached_315) | (_cmp_cached_72)
          )
          # 15m down move, 15m still not low enough, 4h high
          long_entry_logic.append(
            (_cmp_cached_84) | (_cmp_cached_10) | (_cmp_cached_72)
          )
          # 15m down move, 15m & 4h still high
          long_entry_logic.append(
            (_cmp_cached_84) | (_cmp_cached_62) | (_cmp_cached_122)
          )
          # 15m down move, 15m still high, 1h high
          long_entry_logic.append(
            (_cmp_cached_84) | (_cmp_cached_155) | (_cmp_cached_37)
          )
          # 15m down move, 1h still high, 4h high
          long_entry_logic.append(
            (_cmp_cached_84) | (_cmp_cached_59) | (_cmp_cached_162)
          )
          # 15m down move, 4h still high 1d overbought
          long_entry_logic.append((_cmp_cached_84) | (_cmp_cached_122) | (_cmp_cached_107))
          # 15m & 1h down move, 15m still not low enough
          long_entry_logic.append((_cmp_cached_87) | (_cmp_cached_30) | (_cmp_cached_10))
          # 15m & 1h down move, 4h high
          long_entry_logic.append(
            (_cmp_cached_87) | (_cmp_cached_32) | (_cmp_cached_72)
          )
          # 15m & 1h down move, 15m high
          long_entry_logic.append((_cmp_cached_87) | (_cmp_cached_36) | (_cmp_cached_210))
          # 15m & 4h down move, 1h high
          long_entry_logic.append(
            (_cmp_cached_87) | (_cmp_cached_100) | (_cmp_cached_123)
          )
          # 15m & 4h down move, 4h high
          long_entry_logic.append((_cmp_cached_87) | (_cmp_cached_71) | (_cmp_cached_77))
          # 15m & 1d down move, 4h high
          long_entry_logic.append(
            (_cmp_cached_87) | (_cmp_cached_104) | (_cmp_cached_72)
          )
          # 15m down move, 15m still not low enough, 4h high
          long_entry_logic.append((_cmp_cached_87) | (_cmp_cached_315) | (_cmp_cached_316))
          # 15m down move, 15m still not low enough, 1h high
          long_entry_logic.append(
            (_cmp_cached_87) | (_cmp_cached_10) | (_cmp_cached_19)
          )
          # 15m down move, 15m still not low enough, 4h high
          long_entry_logic.append(
            (_cmp_cached_87) | (_cmp_cached_10) | (_cmp_cached_64)
          )
          # 15m down move, 15m still high, 4d downtrend
          long_entry_logic.append((_cmp_cached_87) | (_cmp_cached_31) | (_cmp_cached_69))
          # 15m down move, 15m still not low enough, 1h still high
          long_entry_logic.append(
            (_cmp_cached_87) | (_cmp_cached_152) | (_cmp_cached_26)
          )
          # 15m down move, 15m & 1h still high
          long_entry_logic.append(
            (_cmp_cached_87) | (_cmp_cached_62) | (_cmp_cached_28)
          )
          # 15m down move, 1h & 4h high
          long_entry_logic.append((_cmp_cached_87) | (_cmp_cached_24) | (_cmp_cached_46))
          # 15m & 1h down move, 1h high
          long_entry_logic.append((_cmp_cached_88) | (_cmp_cached_11) | (_cmp_cached_33))
          # 15m & 1h down move, 4h high
          long_entry_logic.append(
            (_cmp_cached_88) | (_cmp_cached_34) | (_cmp_cached_12)
          )
          # 15m & 1h down move, 1d high
          long_entry_logic.append(
            (_cmp_cached_88) | (_cmp_cached_36) | (_cmp_cached_39)
          )
          # 15m & 1h down move, 1h high
          long_entry_logic.append((_cmp_cached_88) | (_cmp_cached_53) | (_cmp_cached_45))
          # 15m & 4h down move, 15m still high
          long_entry_logic.append((_cmp_cached_88) | (_cmp_cached_181) | (_cmp_cached_62))
          # 15m & 1d down move, 4h high
          long_entry_logic.append(
            (_cmp_cached_88) | (_cmp_cached_121) | (_cmp_cached_64)
          )
          # 15m & 1d down move, 1h high
          long_entry_logic.append(
            (_cmp_cached_88) | (_cmp_cached_178) | (_cmp_cached_19)
          )
          # 15m down move, 15m & 1h still high
          long_entry_logic.append(
            (_cmp_cached_88) | (_cmp_cached_62) | (_cmp_cached_59)
          )
          # 15m down move, 15m still high, 4h high
          long_entry_logic.append(
            (_cmp_cached_88) | (_cmp_cached_62) | (_cmp_cached_64)
          )
          # 15m down move, 15m high, 1d overbought
          long_entry_logic.append((_cmp_cached_88) | (_cmp_cached_76) | (_cmp_cached_48))
          # 15m down move, 15m high
          long_entry_logic.append((_cmp_cached_88) | (_cmp_cached_276))
          # 15m down move, 1h & 4h high
          long_entry_logic.append((_cmp_cached_88) | (_cmp_cached_33) | (_cmp_cached_46))
          # 15m down move, 1h & 4h high
          long_entry_logic.append(
            (_cmp_cached_88) | (_cmp_cached_37) | (_cmp_cached_46)
          )
          # 15m down move, 4h high, 1d overbought
          long_entry_logic.append((_cmp_cached_88) | (_cmp_cached_77) | (_cmp_cached_107))
          # 15m & 1h down move, 1h high
          long_entry_logic.append((_cmp_cached_89) | (_cmp_cached_38) | (_cmp_cached_115))
          # 15m down move, 15m high, 4h still high
          long_entry_logic.append(
            (_cmp_cached_89) | (_cmp_cached_76) | (_cmp_cached_122)
          )
          # 15m down move, 15m still not low enough, 1h high
          long_entry_logic.append(
            (_cmp_cached_89) | (_cmp_cached_152) | (_cmp_cached_19)
          )
          # 15m down move, 1h still high, 4h high
          long_entry_logic.append((_cmp_cached_89) | (_cmp_cached_26) | (_cmp_cached_46))
          # 15m down move, 15m & 1h high
          long_entry_logic.append(
            (_cmp_cached_184) | (_cmp_cached_76) | (_cmp_cached_37)
          )
          # 15m down move, 15m & 4h high
          long_entry_logic.append(
            (_cmp_cached_184) | (_cmp_cached_76) | (_cmp_cached_72)
          )
          # 15m down move, 15m high
          long_entry_logic.append((_cmp_cached_184) | (_cmp_cached_18))
          # 15m down move, 4h still high, 4h overbought
          long_entry_logic.append(
            (_cmp_cached_184) | (_cmp_cached_35) | (_cmp_cached_20)
          )
          # 15m down move, 15m still high, 1h high
          long_entry_logic.append((_cmp_cached_90) | (_cmp_cached_85) | (_cmp_cached_33))
          # 15m down move, 15m high, 1h high
          long_entry_logic.append(
            (_cmp_cached_90) | (_cmp_cached_76) | (_cmp_cached_78)
          )
          # 15m down move, 15m high
          long_entry_logic.append((_cmp_cached_245) | (_cmp_cached_274))
          # 1h & 4h down move, 4h still high
          long_entry_logic.append((_cmp_cached_15) | (_cmp_cached_100) | (_cmp_cached_169))
          # 1h & 4h down move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_15) | (_cmp_cached_41) | (_cmp_cached_59)
          )
          # 1h & 4h down move, 4h still high
          long_entry_logic.append((_cmp_cached_15) | (_cmp_cached_41) | (_cmp_cached_96))
          # 1h & 1d down move, 4h downtrend
          long_entry_logic.append((_cmp_cached_15) | (_cmp_cached_192) | (_cmp_cached_200))
          # 1h down move, 1d high & overbought
          long_entry_logic.append(
            (_cmp_cached_30) | (_cmp_cached_39) | (_cmp_cached_70)
          )
          # 1h & 4h down move, 4h still high
          long_entry_logic.append(
            (_cmp_cached_11) | (_cmp_cached_16) | (_cmp_cached_35)
          )
          # 1h & 4h down move, 4h high
          long_entry_logic.append((_cmp_cached_11) | (_cmp_cached_181) | (_cmp_cached_17))
          # 1h down move, 1h still not low enough, 4h high
          long_entry_logic.append(
            (_cmp_cached_11) | (_cmp_cached_161) | (_cmp_cached_64)
          )
          # 1h down move, 1d still high, 1d downtrend
          long_entry_logic.append(
            (_cmp_cached_11) | (_cmp_cached_14) | (_cmp_cached_57)
          )
          # 1h down move, 4h high & overbought
          long_entry_logic.append((_cmp_cached_32) | (_cmp_cached_17) | (_cmp_cached_50))
          # 1h down move, 4h high, 1d downtrend
          long_entry_logic.append((_cmp_cached_32) | (_cmp_cached_17) | (_cmp_cached_42))
          # 1h down move, 4h high, 1d overbought
          long_entry_logic.append((_cmp_cached_32) | (_cmp_cached_17) | (_cmp_cached_52))
          # 1h down move, 4h & 1d overbought
          long_entry_logic.append((_cmp_cached_32) | (_cmp_cached_50) | (_cmp_cached_52))
          # 1h & 4h down move, 4h high
          long_entry_logic.append(
            (_cmp_cached_34) | (_cmp_cached_175) | (_cmp_cached_12)
          )
          # 1h down move, 1h high, 1d overbought
          long_entry_logic.append((_cmp_cached_34) | (_cmp_cached_24) | (_cmp_cached_167))
          # 1h down move, 4h high, 1d overbought
          long_entry_logic.append((_cmp_cached_36) | (_cmp_cached_105) | (_cmp_cached_48))
          # 1h down move, 1h still high, 1d high
          long_entry_logic.append((_cmp_cached_36) | (_cmp_cached_26) | (_cmp_cached_131))
          # 1h down move, 1h still high, 1d overbought
          long_entry_logic.append((_cmp_cached_36) | (_cmp_cached_26) | (_cmp_cached_167))
          # 1h down move 1h high & overbought
          long_entry_logic.append((_cmp_cached_38) | (_cmp_cached_78) | (_cmp_cached_82))
          # 1h down move, 1h high & overbought
          long_entry_logic.append(
            (_cmp_cached_174) | (_cmp_cached_19) | (_cmp_cached_82)
          )
          # 1h down move, 1d high, 1h overbought
          long_entry_logic.append((_cmp_cached_53) | (_cmp_cached_94) | (_cmp_cached_82))
          # 4h down move, 4h still not low enough, 1d overbought
          long_entry_logic.append((_cmp_cached_25) | (_cmp_cached_98) | (_cmp_cached_48))
          # 4h down move, 15m still high, 1d downtrend
          long_entry_logic.append(
            (_cmp_cached_25) | (_cmp_cached_61) | (_cmp_cached_57)
          )
          # 4h & 1d down move, 15m still not low enough
          long_entry_logic.append(
            (_cmp_cached_100) | (_cmp_cached_104) | (_cmp_cached_152)
          )
          # 4h down move, 4h still not low enough, 1d downtrend
          long_entry_logic.append(
            (_cmp_cached_100) | (_cmp_cached_124) | (_cmp_cached_57)
          )
          # 4h down move, 1d high, 4h downtrend
          long_entry_logic.append(
            (_cmp_cached_41) | (_cmp_cached_39) | (_cmp_cached_69)
          )
          # 4h down move, 4h high, 1d downtrend
          long_entry_logic.append(
            (_cmp_cached_21) | (_cmp_cached_64) | (_cmp_cached_102)
          )
          # 4h & 1d down move, 1d high
          long_entry_logic.append((_cmp_cached_181) | (_cmp_cached_126) | (_cmp_cached_27))
          # 4h down move, 4h high, 1d downtrend
          long_entry_logic.append(
            (_cmp_cached_71) | (_cmp_cached_12) | (_cmp_cached_57)
          )
          # 4h down move, 15m high, 4h overbought
          long_entry_logic.append(
            (_cmp_cached_71) | (_cmp_cached_180) | (_cmp_cached_20)
          )
          # 4h down move, 4h & 1d overbought
          long_entry_logic.append((_cmp_cached_71) | (_cmp_cached_20) | (_cmp_cached_167))
          # 1d down move, 1h high, 1d downtrend
          long_entry_logic.append((_cmp_cached_153) | (_cmp_cached_45) | (_cmp_cached_102))
          # 1d down move, 15m still not low enough, 1h still high
          long_entry_logic.append(
            (_cmp_cached_29) | (_cmp_cached_10) | (_cmp_cached_59)
          )
          # 15m still not low enough, 1h high, 1d overbought
          long_entry_logic.append(
            (_cmp_cached_10) | (_cmp_cached_19) | (_cmp_cached_48)
          )
          # 15m still high, 4h high & overbought
          long_entry_logic.append(
            (_cmp_cached_31) | (_cmp_cached_12) | (_cmp_cached_51)
          )
          # 15m & 1h & 4h high
          long_entry_logic.append(
            (_cmp_cached_76) | (_cmp_cached_33) | (_cmp_cached_46)
          )
          # 15m & 1h high, 4h overbought
          long_entry_logic.append((_cmp_cached_76) | (_cmp_cached_78) | (_cmp_cached_20))
          # 15m & 1d high, 1d overbought
          long_entry_logic.append(
            (_cmp_cached_76) | (_cmp_cached_94) | (_cmp_cached_48)
          )
          # 15m high
          long_entry_logic.append((_cmp_cached_18) | (_cmp_cached_222))
          # 15m & 4h high
          long_entry_logic.append((_cmp_cached_18) | (_cmp_cached_64))
          # 15m high, 1d overbought
          long_entry_logic.append((_cmp_cached_18) | (_cmp_cached_107))
          # 15m & 4h high
          long_entry_logic.append((_cmp_cached_274) | (_cmp_cached_17))
          # 15m & 1h high
          long_entry_logic.append((_cmp_cached_274) | (_cmp_cached_78))
          # 1h still high, 4h high & overbought
          long_entry_logic.append((_cmp_cached_26) | (_cmp_cached_46) | (_cmp_cached_67))
          # 1h & 4h high, 1h overbought
          long_entry_logic.append((_cmp_cached_33) | (_cmp_cached_6) | (_cmp_cached_54))
          # 1h & 1d high, 1d overbought
          long_entry_logic.append((_cmp_cached_33) | (_cmp_cached_27) | (_cmp_cached_70))
          # 1h high, 4h & 1d overbought
          long_entry_logic.append((_cmp_cached_78) | (_cmp_cached_20) | (_cmp_cached_52))
          # 4h & 1d high, 4h overbought
          long_entry_logic.append((_cmp_cached_77) | (_cmp_cached_27) | (_cmp_cached_51))
          # 4h & 1d high, 1d overbought
          long_entry_logic.append((_cmp_cached_17) | (_cmp_cached_27) | (_cmp_cached_95))
          # 4h high & overbought
          long_entry_logic.append(
            (_cmp_cached_46) | (_cmp_cached_317) | (_cmp_cached_86)
          )
          # 1d high, 4h & 1d overbought
          long_entry_logic.append((_cmp_cached_27) | (_cmp_cached_50) | (_cmp_cached_107))
          # 1d high, 4h & 1d overbought
          long_entry_logic.append((_cmp_cached_27) | (_cmp_cached_20) | (_cmp_cached_52))
          # 4h high, 4h & 1d overbought
          long_entry_logic.append(
            (_cmp_cached_64) | (_cmp_cached_51) | (_cmp_cached_70)
          )
          # 5m red, 1h still high
          long_entry_logic.append((_cmp_cached_318) | (_cmp_cached_59))
          # 1d top wick, 4h down move, 4h still high
          long_entry_logic.append(
            (_cmp_cached_145) | (_cmp_cached_71) | (_cmp_cached_122)
          )
          # pump, drop but not yet near the previous lows
          long_entry_logic.append(
            (((df["high_max_24_4h"] - df["low_min_24_4h"]) / df["low_min_24_4h"]) < 2.0)
            | (df["close"] > (df["high_max_6_4h"] * 0.75))
            | (df["close"] < (df["low_min_24_4h"] * 1.25))
          )
          # 4h high, drop but not yet near the previous lows
          long_entry_logic.append(
            (_cmp_cached_72)
            | (df["close"] > (df["close_max_48"] * 0.85))
            | (df["close"] < (df["low_min_24_1h"] * 1.25))
          )
          # 4h high, drop but not yet near the previous lows
          long_entry_logic.append(
            (_cmp_cached_17)
            | (df["close"] > (df["high_max_6_4h"] * 0.80))
            | (df["close"] < (df["low_min_24_4h"] * 1.25))
          )
          # 1d overbought, drop but not yet near the previous lows
          long_entry_logic.append(
            (_cmp_cached_107)
            | (df["close"] > (df["high_max_6_1d"] * 0.70))
            | (df["close"] < (df["low_min_12_1d"] * 1.25))
          )
          # big drop in the last 4 days, 4h down move
          long_entry_logic.append((df["close"] > (df["high_max_24_4h"] * 0.20)) | (_cmp_cached_100))
          # big drop in the last 12 days, 1h high
          long_entry_logic.append(
            (df["close"] > (df["high_max_12_1d"] * 0.30)) | (_cmp_cached_49)
          )
          # big drop in the last 20 days, 1d down move
          long_entry_logic.append((df["close"] > (df["high_max_20_1d"] * 0.40)) | (_cmp_cached_178))
          # big drop in the last 30 days, 4h down move, 4h still high
          long_entry_logic.append(
            (df["close"] > (df["high_max_30_1d"] * 0.25)) | (_cmp_cached_91) | (_cmp_cached_169)
          )
          # big drop in the last 30 days, 1h high
          long_entry_logic.append(
            (df["close"] > (df["high_max_30_1d"] * 0.20)) | (_cmp_cached_19)
          )

          # Logic
          long_entry_logic.append(_cmp_cached_319)
          long_entry_logic.append(_cmp_cached_320)
          long_entry_logic.append(df["close"] < (df["BBL_20_2.0"] * 0.999))
          long_entry_logic.append(df["close"] < (df["EMA_20"] * 0.960))

        # Condition #103 - Rapid mode (Long).
        if long_entry_condition_index == 103:
          # Protections
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          long_entry_logic.append(df["protections_long_global"] == True)

          long_entry_logic.append(_cmp_cached_291)
          # 15m down move, 4h high, 1d overbought
          long_entry_logic.append(
            (_cmp_cached_5) | (_cmp_cached_64) | (_cmp_cached_63)
          )
          # 15m & 1h & 4h down move
          long_entry_logic.append((_cmp_cached_87) | (_cmp_cached_9) | (_cmp_cached_100))
          # 15m & 4h down move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_5) | (_cmp_cached_100) | (_cmp_cached_59)
          )
          # 15m & 1h down move, 1h high
          long_entry_logic.append((_cmp_cached_84) | (_cmp_cached_36) | (_cmp_cached_24))
          # 15m down move, 4h high & overbought
          long_entry_logic.append(
            (_cmp_cached_84) | (_cmp_cached_64) | (_cmp_cached_51)
          )
          # 15m & 1h down move, 15m high
          long_entry_logic.append((_cmp_cached_87) | (_cmp_cached_38) | (_cmp_cached_76))
          # 15m & 4h down move, 15m still high
          long_entry_logic.append(
            (_cmp_cached_87) | (_cmp_cached_100) | (_cmp_cached_61)
          )
          # 15m down move, 15m still high, 1h high
          long_entry_logic.append(
            (_cmp_cached_87) | (_cmp_cached_292) | (_cmp_cached_37)
          )
          # 15m down move, 15m still high, 4h high
          long_entry_logic.append((_cmp_cached_87) | (_cmp_cached_292) | (_cmp_cached_46))
          # 15m down move, 15m still high, 4h high
          long_entry_logic.append(
            (_cmp_cached_87) | (_cmp_cached_62) | (_cmp_cached_46)
          )
          # 15m down move, 15m & 1h high
          long_entry_logic.append(
            (_cmp_cached_87) | (_cmp_cached_210) | (_cmp_cached_24)
          )
          # 15m down move, 15m high, 4h still high
          long_entry_logic.append(
            (_cmp_cached_87) | (_cmp_cached_76) | (_cmp_cached_122)
          )
          # 15m down move, 15m & 1h still high
          long_entry_logic.append(
            (_cmp_cached_87) | (_cmp_cached_61) | (_cmp_cached_59)
          )
          # 15m down move, 4h overbought
          long_entry_logic.append((_cmp_cached_87) | (_cmp_cached_217))
          # 15m down move, 15m still high, 1h high
          long_entry_logic.append(
            (_cmp_cached_88) | (_cmp_cached_62) | (_cmp_cached_33)
          )
          # 15m down move, 4h & 1d high
          long_entry_logic.append(
            (_cmp_cached_88) | (_cmp_cached_46) | (_cmp_cached_39)
          )
          # 15m down move, 1h & 1d high
          long_entry_logic.append(
            (_cmp_cached_88) | (_cmp_cached_19) | (_cmp_cached_39)
          )
          # 15m down move, 1h high & overbought
          long_entry_logic.append(
            (_cmp_cached_88) | (_cmp_cached_19) | (_cmp_cached_79)
          )
          # 15m & 1h down move, 15m high
          long_entry_logic.append((_cmp_cached_89) | (_cmp_cached_32) | (_cmp_cached_76))
          # 15m down move, 15m & 1h high
          long_entry_logic.append(
            (_cmp_cached_89) | (_cmp_cached_76) | (_cmp_cached_78)
          )
          # 15m down move, 1h & 4h high
          long_entry_logic.append(
            (_cmp_cached_89) | (_cmp_cached_37) | (_cmp_cached_46)
          )
          # 15m & 1h down move, 1h high
          long_entry_logic.append(
            (_cmp_cached_184) | (_cmp_cached_38) | (_cmp_cached_19)
          )
          # 15m down move, 15m still high, 4h high
          long_entry_logic.append(
            (_cmp_cached_184) | (_cmp_cached_62) | (_cmp_cached_77)
          )
          # 15m down move, 15m & 1h high
          long_entry_logic.append(
            (_cmp_cached_184) | (_cmp_cached_76) | (_cmp_cached_19)
          )
          # 15m down move, 1h high, 4h overbought
          long_entry_logic.append((_cmp_cached_184) | (_cmp_cached_45) | (_cmp_cached_67))
          # 1h & 4h down move, 1h still high
          long_entry_logic.append((_cmp_cached_9) | (_cmp_cached_100) | (_cmp_cached_110))
          # 1h & 4h down move, 15m still not low enough
          long_entry_logic.append(
            (_cmp_cached_9) | (_cmp_cached_100) | (_cmp_cached_171)
          )
          # 1h down move, 1d high & overbought
          long_entry_logic.append((_cmp_cached_9) | (_cmp_cached_94) | (_cmp_cached_95))
          # 1h & 4h down move, 4h still high
          long_entry_logic.append((_cmp_cached_15) | (_cmp_cached_100) | (_cmp_cached_96))
          # 1h down move, 4h still high, 4h downtrend
          long_entry_logic.append((_cmp_cached_15) | (_cmp_cached_122) | (_cmp_cached_69))
          # 1h down move, 15m still not low enough, 4h high
          long_entry_logic.append((_cmp_cached_30) | (_cmp_cached_179) | (_cmp_cached_77))
          # 1h down move, 4h & 1d high
          long_entry_logic.append(
            (_cmp_cached_32) | (_cmp_cached_17) | (_cmp_cached_74)
          )
          # 1h down move, 4h high & overbought
          long_entry_logic.append((_cmp_cached_32) | (_cmp_cached_17) | (_cmp_cached_50))
          # 1h down move, 4h high, 1d overbought
          long_entry_logic.append((_cmp_cached_32) | (_cmp_cached_17) | (_cmp_cached_52))
          # 1h down move, 4h & 1d overbought
          long_entry_logic.append((_cmp_cached_32) | (_cmp_cached_50) | (_cmp_cached_52))
          # 1h down move, 4h & 1d overbought
          long_entry_logic.append((_cmp_cached_32) | (_cmp_cached_51) | (_cmp_cached_52))
          # 1h down move, 15m & 1h still high
          long_entry_logic.append(
            (_cmp_cached_36) | (_cmp_cached_62) | (_cmp_cached_59)
          )
          # 1h down move, 1h still high, 4h high
          long_entry_logic.append((_cmp_cached_36) | (_cmp_cached_26) | (_cmp_cached_46))
          # 1h down move, 1h overbought
          long_entry_logic.append((_cmp_cached_36) | (_cmp_cached_158))
          # 1h down move, 1d high & overbought
          long_entry_logic.append((_cmp_cached_38) | (_cmp_cached_27) | (_cmp_cached_70))
          # 1h down move, 15m & 1h still high
          long_entry_logic.append((_cmp_cached_117) | (_cmp_cached_62) | (_cmp_cached_45))
          # 1h & 4h down move, 4h high
          long_entry_logic.append((_cmp_cached_53) | (_cmp_cached_71) | (_cmp_cached_77))
          # 1h & 4h down move, 4h high
          long_entry_logic.append(
            (_cmp_cached_53) | (_cmp_cached_71) | (_cmp_cached_12)
          )
          # 4h down move, 1h & 4h downtrend
          long_entry_logic.append((_cmp_cached_55) | (_cmp_cached_109) | (_cmp_cached_103))
          # 1h down move, 4h high & overbought
          long_entry_logic.append(
            (_cmp_cached_117) | (_cmp_cached_72) | (_cmp_cached_20)
          )
          # 4h down move, 4h still high, 1d downtrend
          long_entry_logic.append((_cmp_cached_100) | (_cmp_cached_122) | (_cmp_cached_65))
          # 1h down move, 15m & 1h still high
          long_entry_logic.append(
            (_cmp_cached_100) | (_cmp_cached_155) | (_cmp_cached_59)
          )
          # 4h down move, 15m still high, 4h high
          long_entry_logic.append(
            (_cmp_cached_16) | (_cmp_cached_61) | (_cmp_cached_17)
          )
          # 4h down move, 15m still not low enough, 4h high
          long_entry_logic.append((_cmp_cached_21) | (_cmp_cached_10) | (_cmp_cached_17))
          # 4h down move, 1h high, 4h downtrend
          long_entry_logic.append((_cmp_cached_41) | (_cmp_cached_24) | (_cmp_cached_93))
          # 4h down move, 4h still high, 1d downtrend
          long_entry_logic.append((_cmp_cached_99) | (_cmp_cached_169) | (_cmp_cached_102))
          # 4h down move, 4h high & overbought
          long_entry_logic.append((_cmp_cached_99) | (_cmp_cached_77) | (_cmp_cached_20))
          # 4h down move, 4h still high, 1d downtrend
          long_entry_logic.append(
            (_cmp_cached_99) | (_cmp_cached_35) | (_cmp_cached_102)
          )
          # 4h down move, 15m still high, 1h high
          long_entry_logic.append((_cmp_cached_71) | (_cmp_cached_62) | (_cmp_cached_78))
          # 4h down move, 1h high, 1d overbought
          long_entry_logic.append(
            (_cmp_cached_71) | (_cmp_cached_49) | (_cmp_cached_70)
          )
          # 1d down move, 1h high, 1d downtrend
          long_entry_logic.append((_cmp_cached_153) | (_cmp_cached_33) | (_cmp_cached_186))
          # 1d down move, 4h high
          long_entry_logic.append((_cmp_cached_153) | (_cmp_cached_12))
          # 1d down move, 15m still high, 1h high
          long_entry_logic.append((_cmp_cached_29) | (_cmp_cached_62) | (_cmp_cached_45))
          # 1d down move, 1h & 1d overbought
          long_entry_logic.append((_cmp_cached_198) | (_cmp_cached_242) | (_cmp_cached_63))
          # 15m still high, 1h & 4h high
          long_entry_logic.append(
            (_cmp_cached_292) | (_cmp_cached_33) | (_cmp_cached_46)
          )
          # 15m & 1h still high, 4h high
          long_entry_logic.append(
            (_cmp_cached_321) | (_cmp_cached_110) | (_cmp_cached_64)
          )
          # 15m still high, 4h high & overbought
          long_entry_logic.append((_cmp_cached_85) | (_cmp_cached_46) | (_cmp_cached_67))
          # 15m still high, 1h high, 4h still high
          long_entry_logic.append(
            (_cmp_cached_62) | (_cmp_cached_78) | (_cmp_cached_35)
          )
          # 15m still high, 1d high
          long_entry_logic.append((_cmp_cached_62) | (_cmp_cached_39))
          # 15m & 1h
          long_entry_logic.append((_cmp_cached_76) | (_cmp_cached_78))
          # 15m & 1h & 4h high
          long_entry_logic.append(
            (_cmp_cached_76) | (_cmp_cached_37) | (_cmp_cached_46)
          )
          # 1h & 1d high, 4h downtrend
          long_entry_logic.append((_cmp_cached_110) | (_cmp_cached_106) | (_cmp_cached_69))
          # 1h & 4h high, 4h overbought
          long_entry_logic.append((_cmp_cached_24) | (_cmp_cached_46) | (_cmp_cached_50))
          # 1h high, 1h & 1d overbought
          long_entry_logic.append((_cmp_cached_78) | (_cmp_cached_82) | (_cmp_cached_70))
          # 4h & 1d high, 1d overbought
          long_entry_logic.append((_cmp_cached_17) | (_cmp_cached_27) | (_cmp_cached_95))
          # 4h high, 4h & 1d overbought
          long_entry_logic.append((_cmp_cached_77) | (_cmp_cached_67) | (_cmp_cached_48))
          # 1d high, 4h & 1d overbought
          long_entry_logic.append((_cmp_cached_27) | (_cmp_cached_50) | (_cmp_cached_107))
          # 15m still high, 1h high
          long_entry_logic.append(
            (_cmp_cached_155)
            | (_cmp_cached_78)
            | (_cmp_cached_49)
          )
          # 15m still high, 1d high
          long_entry_logic.append((_cmp_cached_61) | (_cmp_cached_39))
          # 4h high, 4h & 1d overbought
          long_entry_logic.append(
            (_cmp_cached_12) | (_cmp_cached_113) | (_cmp_cached_48)
          )
          # 1d green, 4h down move, 4h still high
          long_entry_logic.append((_cmp_cached_142) | (_cmp_cached_21) | (_cmp_cached_96))
          # 1d top wick, 4h high
          long_entry_logic.append((_cmp_cached_145) | (_cmp_cached_46))
          # pump, 4h overbought
          long_entry_logic.append(
            (((df["high_max_6_1h"] - df["low_min_6_1h"]) / df["low_min_6_1h"]) < 0.5) | (_cmp_cached_86)
          )
          # pump, drop but not yet near the previous lows
          long_entry_logic.append(
            (((df["high_max_24_4h"] - df["low_min_24_4h"]) / df["low_min_24_4h"]) < 2.0)
            | (df["close"] > (df["high_max_6_4h"] * 0.85))
            | (df["close"] < (df["low_min_24_4h"] * 1.25))
          )
          # pump, 1h high
          long_entry_logic.append(
            (((df["high_max_24_4h"] - df["low_min_24_4h"]) / df["low_min_24_4h"]) < 4.0)
            | (_cmp_cached_49)
          )
          # big drop in the last 2 days, 1d down move
          long_entry_logic.append((df["close"] > (df["high_max_12_4h"] * 0.30)) | (_cmp_cached_178))
          # big drop in the last 12 days, 1h still high
          long_entry_logic.append((df["close"] > (df["high_max_12_1d"] * 0.25)) | (_cmp_cached_26))
          # big drop in the last 12 days, 1h still not low enough
          long_entry_logic.append(
            (df["close"] > (df["high_max_12_1d"] * 0.10)) | (_cmp_cached_161)
          )
          # big drop in the last 12 days, 15m still high
          long_entry_logic.append((df["close"] > (df["high_max_12_1d"] * 0.20)) | (_cmp_cached_62))
          # big drop in the last 20 days, 4h down move
          long_entry_logic.append((df["close"] > (df["high_max_20_1d"] * 0.10)) | (_cmp_cached_100))

          # Logic
          long_entry_logic.append(_cmp_cached_234)
          long_entry_logic.append(_cmp_cached_322)
          long_entry_logic.append(df["RSI_20"] < df["RSI_20"].shift(1))
          long_entry_logic.append(_cmp_cached_243)
          long_entry_logic.append(df["close"] < df["SMA_16"] * 0.960)

        # Condition #104 - Rapid mode (Long).
        if long_entry_condition_index == 104:
          # Protections
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          long_entry_logic.append(df["protections_long_global"] == True)

          # 5m & 4h & 1d down move
          long_entry_logic.append((_cmp_cached_0) | (_cmp_cached_100) | (_cmp_cached_104))
          # 5m & 4h down move, 1d downtrend
          long_entry_logic.append((_cmp_cached_8) | (_cmp_cached_58) | (_cmp_cached_57))
          # 5m & 1h down move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_8) | (_cmp_cached_32) | (_cmp_cached_59)
          )
          # 15m & 4h & 1d down move
          long_entry_logic.append((_cmp_cached_1) | (_cmp_cached_58) | (_cmp_cached_29))
          # 15m & 1h down move
          long_entry_logic.append((_cmp_cached_1) | (_cmp_cached_13))
          # 15m & 1h down move, 4h still not low enough
          long_entry_logic.append((_cmp_cached_1) | (_cmp_cached_7) | (_cmp_cached_289))
          # 15m & 1h down move, 1d still high
          long_entry_logic.append((_cmp_cached_1) | (_cmp_cached_9) | (_cmp_cached_238))
          # 15m & 1h down move, 1h still not low enough
          long_entry_logic.append(
            (_cmp_cached_1) | (_cmp_cached_15) | (_cmp_cached_161)
          )
          # 15m & 4h down move, 4h still high
          long_entry_logic.append((_cmp_cached_1) | (_cmp_cached_41) | (_cmp_cached_169))
          # 15m & 1h & 4h down move
          long_entry_logic.append((_cmp_cached_3) | (_cmp_cached_15) | (_cmp_cached_25))
          # 15m & 1h & 4h down move, 15m downtrend
          long_entry_logic.append(
            (_cmp_cached_3) | (_cmp_cached_30) | (_cmp_cached_100) | (_cmp_cached_323)
          )
          # 15m & 1h down move, 4h still not low enough
          long_entry_logic.append((_cmp_cached_3) | (_cmp_cached_30) | (_cmp_cached_120))
          # 15m & 1h down move, 1h high
          long_entry_logic.append(
            (_cmp_cached_3) | (_cmp_cached_32) | (_cmp_cached_59)
          )
          # 15m & 4h down move, 4h still high
          long_entry_logic.append((_cmp_cached_3) | (_cmp_cached_25) | (_cmp_cached_122))
          # 15m & 1h down move, 15m & 1h downtrend
          long_entry_logic.append(
            (_cmp_cached_5) | (_cmp_cached_9) | (_cmp_cached_43) | (_cmp_cached_240)
          )
          # 15m & 1h down move, 1h still not low enough
          long_entry_logic.append(
            (_cmp_cached_5) | (_cmp_cached_9) | (_cmp_cached_190)
          )
          # 15m & 1h down move, 4h still high
          long_entry_logic.append(
            (_cmp_cached_5) | (_cmp_cached_30) | (_cmp_cached_35)
          )
          # 15m & 1h down move, 4h overbought
          long_entry_logic.append((_cmp_cached_5) | (_cmp_cached_36) | (_cmp_cached_86))
          # 15m & 1h down move, 1h high
          long_entry_logic.append((_cmp_cached_5) | (_cmp_cached_11) | (_cmp_cached_33))
          # 15m & 4h down move, 1h & 4h downtrend
          long_entry_logic.append(
            (_cmp_cached_5) | (_cmp_cached_58) | (_cmp_cached_306) | (_cmp_cached_303)
          )
          # 15m & 4h down move, 4h still not low enough
          long_entry_logic.append(
            (_cmp_cached_5) | (_cmp_cached_58) | (_cmp_cached_124)
          )
          # 15m & 4h down move, 4h still high
          long_entry_logic.append((_cmp_cached_5) | (_cmp_cached_58) | (_cmp_cached_96))
          # 15m & 4h down move, 1d high
          long_entry_logic.append(
            (_cmp_cached_5) | (_cmp_cached_25) | (_cmp_cached_39)
          )
          # 15m & 4h down move, 1h high
          long_entry_logic.append(
            (_cmp_cached_5) | (_cmp_cached_100) | (_cmp_cached_37)
          )
          # 15m & 4h down move, 4h still high
          long_entry_logic.append(
            (_cmp_cached_5) | (_cmp_cached_100) | (_cmp_cached_165)
          )
          # 15m & 4h down move, 1d downtrend
          long_entry_logic.append((_cmp_cached_5) | (_cmp_cached_100) | (_cmp_cached_195))
          # 15m & 4h down move, 15m still not low enough
          long_entry_logic.append(
            (_cmp_cached_5) | (_cmp_cached_16) | (_cmp_cached_171)
          )
          # 15m & 4h down move, 4h high
          long_entry_logic.append((_cmp_cached_5) | (_cmp_cached_181) | (_cmp_cached_77))
          # 15m & 1h down move, 4h still high
          long_entry_logic.append((_cmp_cached_84) | (_cmp_cached_30) | (_cmp_cached_96))
          # 15m & 1h down move, 4h high
          long_entry_logic.append((_cmp_cached_84) | (_cmp_cached_11) | (_cmp_cached_17))
          # 15m & 1h down move, 1h high
          long_entry_logic.append(
            (_cmp_cached_84) | (_cmp_cached_11) | (_cmp_cached_123)
          )
          # 15m & 1h down move, 1h still high
          long_entry_logic.append((_cmp_cached_84) | (_cmp_cached_32) | (_cmp_cached_110))
          # 15m down move, 4h still high, 4h downtrend
          long_entry_logic.append((_cmp_cached_84) | (_cmp_cached_96) | (_cmp_cached_69))
          # 15m down move, 1d high, 4h overbought
          long_entry_logic.append((_cmp_cached_84) | (_cmp_cached_27) | (_cmp_cached_86))
          # 15m & 3h down move, 15m still not low enough
          long_entry_logic.append(
            (_cmp_cached_87) | (_cmp_cached_100) | (_cmp_cached_171)
          )
          # 15m & 1h down move, 1h still high
          long_entry_logic.append((_cmp_cached_88) | (_cmp_cached_11) | (_cmp_cached_296))
          # 15m & 4h down move, 4h high
          long_entry_logic.append((_cmp_cached_88) | (_cmp_cached_16) | (_cmp_cached_17))
          # 15m down move, 15m still not low enough, 1d overbought
          long_entry_logic.append(
            (_cmp_cached_88) | (_cmp_cached_171) | (_cmp_cached_63)
          )
          # 1h & 4h down move
          long_entry_logic.append((_cmp_cached_13) | (_cmp_cached_58))
          # 1h & 4h down move, 4h still not low enough
          long_entry_logic.append(
            (_cmp_cached_13) | (_cmp_cached_16) | (_cmp_cached_124)
          )
          # 1h & 4h down move, 4h high
          long_entry_logic.append((_cmp_cached_13) | (_cmp_cached_99) | (_cmp_cached_17))
          # 1h & 4h down move
          long_entry_logic.append((_cmp_cached_7) | (_cmp_cached_55))
          # 1h & 4h down move, 4h still high
          long_entry_logic.append((_cmp_cached_7) | (_cmp_cached_41) | (_cmp_cached_122))
          # 1h down move, 1h still high
          long_entry_logic.append((_cmp_cached_7) | (_cmp_cached_26))
          # 1h down move, 4h high
          long_entry_logic.append((_cmp_cached_7) | (_cmp_cached_47))
          # 1h & 4h down move
          long_entry_logic.append((_cmp_cached_9) | (_cmp_cached_58))
          # 1h & 4h down move, 4h still not low enough
          long_entry_logic.append(
            (_cmp_cached_9) | (_cmp_cached_25) | (_cmp_cached_124)
          )
          # 1h & 4h down move, 1d still high
          long_entry_logic.append(
            (_cmp_cached_9) | (_cmp_cached_25) | (_cmp_cached_14)
          )
          # 1h & 1d down move, 1h still moving lower
          long_entry_logic.append(
            (_cmp_cached_9) | (_cmp_cached_29) | (_cmp_cached_324)
          )
          # 1h down move, 1d high, 4h downtrend
          long_entry_logic.append((_cmp_cached_9) | (_cmp_cached_131) | (_cmp_cached_93))
          # 1h & 4h down move, 1h still high
          long_entry_logic.append((_cmp_cached_15) | (_cmp_cached_25) | (_cmp_cached_26))
          # 1h & 4h & 1d down move
          long_entry_logic.append((_cmp_cached_15) | (_cmp_cached_100) | (_cmp_cached_178))
          # 1h & 4h down move, 1h still not low enough
          long_entry_logic.append(
            (_cmp_cached_15) | (_cmp_cached_100) | (_cmp_cached_190)
          )
          # 1h & 4h down move, 4h still not low enough
          long_entry_logic.append(
            (_cmp_cached_15) | (_cmp_cached_100) | (_cmp_cached_124)
          )
          # 1h & 4h & 1d down move
          long_entry_logic.append((_cmp_cached_15) | (_cmp_cached_16) | (_cmp_cached_121))
          # 1h & 4h down move, 1h high
          long_entry_logic.append((_cmp_cached_15) | (_cmp_cached_181) | (_cmp_cached_33))
          # 1h & 1d down move, 1d high
          long_entry_logic.append((_cmp_cached_15) | (_cmp_cached_121) | (_cmp_cached_106))
          # 1h & 1d down move, 1d high
          long_entry_logic.append(
            (_cmp_cached_15) | (_cmp_cached_121) | (_cmp_cached_148)
          )
          # 1h down move, 1h & 4h high
          long_entry_logic.append((_cmp_cached_15) | (_cmp_cached_115) | (_cmp_cached_40))
          # 1h & 4h down move, 1d overbought
          long_entry_logic.append((_cmp_cached_30) | (_cmp_cached_100) | (_cmp_cached_107))
          # 1h & 4h down move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_30) | (_cmp_cached_16) | (_cmp_cached_59)
          )
          # 1h & 1d down move, 1d high
          long_entry_logic.append((_cmp_cached_30) | (_cmp_cached_104) | (_cmp_cached_106))
          # 4h & 1d down move, 1d high
          long_entry_logic.append((_cmp_cached_30) | (_cmp_cached_125) | (_cmp_cached_108))
          # 1h down move, 1h still high, 4h high
          long_entry_logic.append((_cmp_cached_30) | (_cmp_cached_26) | (_cmp_cached_17))
          # 1h down move, 4h high
          long_entry_logic.append((_cmp_cached_30) | (_cmp_cached_72))
          # 1h down move, 1h & 1d high
          long_entry_logic.append((_cmp_cached_11) | (_cmp_cached_24) | (_cmp_cached_94))
          # 1h down move, 4h still high, 1d downtrend
          long_entry_logic.append((_cmp_cached_11) | (_cmp_cached_96) | (_cmp_cached_57))
          # 1h down move, 1h still high, 1d overbought
          long_entry_logic.append(
            (_cmp_cached_11) | (_cmp_cached_59) | (_cmp_cached_52)
          )
          # 1h & 4h down move, 4h high
          long_entry_logic.append((_cmp_cached_32) | (_cmp_cached_91) | (_cmp_cached_77))
          # 1h & dh down move, 4h high
          long_entry_logic.append((_cmp_cached_32) | (_cmp_cached_99) | (_cmp_cached_47))
          # 1h down move, 4h still not low enough, 1d overbought
          long_entry_logic.append((_cmp_cached_32) | (_cmp_cached_98) | (_cmp_cached_107))
          # 1h down move, 1h still not low enough, 4h downtrend
          long_entry_logic.append(
            (_cmp_cached_34) | (_cmp_cached_161) | (_cmp_cached_69)
          )
          # 1h down move, 4h still high, 1d downtrend
          long_entry_logic.append(
            (_cmp_cached_34) | (_cmp_cached_35) | (_cmp_cached_57)
          )
          # 1h down move, 4h & 1d overbought
          long_entry_logic.append((_cmp_cached_36) | (_cmp_cached_50) | (_cmp_cached_107))
          # 1h down move, 4h high & overbought
          long_entry_logic.append((_cmp_cached_117) | (_cmp_cached_46) | (_cmp_cached_20))
          # 1h down move, 4h high & overbought
          long_entry_logic.append(
            (_cmp_cached_117) | (_cmp_cached_12) | (_cmp_cached_20)
          )
          # 4h down move, 15m not low enough, 1h still high
          long_entry_logic.append(
            (_cmp_cached_151) | (_cmp_cached_171) | (_cmp_cached_28)
          )
          # 4h & 1d down move, 4h downtrend
          long_entry_logic.append((_cmp_cached_55) | (_cmp_cached_104) | (_cmp_cached_69))
          # 4h & 1d down move, 1d high
          long_entry_logic.append((_cmp_cached_55) | (_cmp_cached_178) | (_cmp_cached_106))
          # 4h down move, 4h still high, 1d downtrend
          long_entry_logic.append(
            (_cmp_cached_55) | (_cmp_cached_165) | (_cmp_cached_57)
          )
          # 4h down move, 1d still not low enough, 1d downtrend
          long_entry_logic.append(
            (_cmp_cached_55) | (_cmp_cached_273) | (_cmp_cached_57)
          )
          # 4h down move, 1h downtrend, 1h still not low enough
          long_entry_logic.append((_cmp_cached_58) | (_cmp_cached_114) | (_cmp_cached_150))
          # 4h down move, 1h & 1d downtrend
          long_entry_logic.append((_cmp_cached_58) | (_cmp_cached_129) | (_cmp_cached_57))
          # 4h & 1d down move, 4h still high
          long_entry_logic.append(
            (_cmp_cached_25) | (_cmp_cached_198) | (_cmp_cached_165)
          )
          # 4h & 1d down move, 1d high
          long_entry_logic.append(
            (_cmp_cached_100) | (_cmp_cached_121) | (_cmp_cached_60)
          )
          # 4h down move, 1d high & overbought
          long_entry_logic.append((_cmp_cached_100) | (_cmp_cached_106) | (_cmp_cached_107))
          # 4h down move, 1h still high, 1d downtrend
          long_entry_logic.append(
            (_cmp_cached_100) | (_cmp_cached_59) | (_cmp_cached_57)
          )
          # 4h down move, 1h high
          long_entry_logic.append((_cmp_cached_100) | (_cmp_cached_19))
          # 4h down move, 1d high, 1h downtrend
          long_entry_logic.append(
            (_cmp_cached_100) | (_cmp_cached_148) | (_cmp_cached_132)
          )
          # 4h down move, 4h still high, 1d overbought
          long_entry_logic.append((_cmp_cached_41) | (_cmp_cached_96) | (_cmp_cached_48))
          # 4h down move, 4h high, 1h downtrend
          long_entry_logic.append((_cmp_cached_41) | (_cmp_cached_77) | (_cmp_cached_109))
          # 4h down move, 4h still high, 1d overbought
          long_entry_logic.append((_cmp_cached_21) | (_cmp_cached_122) | (_cmp_cached_52))
          # 4h down move, 4h still high, 1d high
          long_entry_logic.append((_cmp_cached_181) | (_cmp_cached_122) | (_cmp_cached_27))
          # 4h down move, 4h & 1d overbought
          long_entry_logic.append((_cmp_cached_181) | (_cmp_cached_50) | (_cmp_cached_107))
          # 1d down move, 1h still not low enough
          long_entry_logic.append((_cmp_cached_101) | (_cmp_cached_190))
          # 1h & 4h high, 4h overbought
          long_entry_logic.append((_cmp_cached_115) | (_cmp_cached_6) | (_cmp_cached_51))
          # 4h & 1d high, 4h overbought
          long_entry_logic.append((_cmp_cached_40) | (_cmp_cached_27) | (_cmp_cached_113))
          # 4h & 1d high,1d overbought
          long_entry_logic.append((_cmp_cached_17) | (_cmp_cached_27) | (_cmp_cached_107))
          # 1d red, 4h down move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_313) | (_cmp_cached_41) | (_cmp_cached_59)
          )
          # pump, drop but not yet near the previous lows
          long_entry_logic.append(
            (((df["high_max_24_4h"] - df["low_min_24_4h"]) / df["low_min_24_4h"]) < 2.0)
            | (df["close"] > (df["high_max_12_4h"] * 0.60))
            | (df["close"] < (df["low_min_24_4h"] * 1.10))
          )
          # pump, drop but not yet near the previous lows
          long_entry_logic.append(
            (((df["high_max_12_1d"] - df["low_min_12_1d"]) / df["low_min_12_1d"]) < 5.0)
            | (df["close"] > (df["high_max_6_1d"] * 0.30))
            | (df["close"] < (df["low_min_12_1d"] * 1.25))
          )
          # big drop in the last hour
          long_entry_logic.append(df["close"] > (df["close_max_12"] * 0.50))
          # big drop in the last 12 days, 15m & 4h down move
          long_entry_logic.append(
            (df["close"] > (df["high_max_12_1d"] * 0.40)) | (_cmp_cached_5) | (_cmp_cached_58)
          )
          # big drop in the last 20 days, 15m & 1h down move
          long_entry_logic.append(
            (df["close"] > (df["high_max_20_1d"] * 0.40)) | (_cmp_cached_325) | (_cmp_cached_326)
          )
          # big drop in the last 20 days, 1d down move
          long_entry_logic.append((df["close"] > (df["high_max_20_1d"] * 0.25)) | (_cmp_cached_178))
          # big drop in the last 20 days, 4h still not low enough
          long_entry_logic.append((df["close"] > (df["high_max_20_1d"] * 0.10)) | (_cmp_cached_163))
          # big drop in the last 30 days, 4h down move
          long_entry_logic.append((df["close"] > (df["high_max_30_1d"] * 0.25)) | (_cmp_cached_100))

          # Logic
          long_entry_logic.append(_cmp_cached_287)
          long_entry_logic.append(_cmp_cached_243)
          long_entry_logic.append(_cmp_cached_237)
          long_entry_logic.append(_cmp_cached_179)
          long_entry_logic.append(_cmp_cached_152)
          long_entry_logic.append(df["close"] < df["EMA_16"] * 0.975)
          long_entry_logic.append(((df["EMA_50"] - df["EMA_200"]) / df["close"] * 100.0) < -5.5)

        # Condition #120 - Grind mode (Long).
        if long_entry_condition_index == 120:
          # Protections
          long_entry_logic.append(num_open_long_grind_mode < self.grind_mode_max_slots)
          long_entry_logic.append(df["protections_long_global"] == True)
          long_entry_logic.append(is_pair_long_grind_mode)
          long_entry_logic.append(_cmp_cached_327)
          long_entry_logic.append(_cmp_cached_328)
          long_entry_logic.append(_cmp_cached_329)
          long_entry_logic.append(_cmp_cached_330)
          long_entry_logic.append(_cmp_cached_310)
          long_entry_logic.append(_cmp_cached_66)
          long_entry_logic.append(_cmp_cached_250)
          long_entry_logic.append(_cmp_cached_76)
          long_entry_logic.append(_cmp_cached_80)
          long_entry_logic.append(_cmp_cached_6)
          long_entry_logic.append(_cmp_cached_27)
          long_entry_logic.append(_cmp_cached_39)

          # Logic
          long_entry_logic.append(
            (_cmp_cached_237)
            & (_cmp_cached_331)
            & (_cmp_cached_243)
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
            ((_cmp_cached_0) | (_cmp_cached_84) | (_cmp_cached_76))
            # 5m & 15m down move, 4h still high
            & ((_cmp_cached_0) | (_cmp_cached_84) | (_cmp_cached_35))
            # 5m & 15m down move, 15m high
            & ((_cmp_cached_0) | (_cmp_cached_87) | (_cmp_cached_76))
            # 5m & 1h down move, 15m still high
            & ((_cmp_cached_0) | (_cmp_cached_15) | (_cmp_cached_31))
            # 5m & 1h down move, 1h high
            & ((_cmp_cached_0) | (_cmp_cached_38) | (_cmp_cached_19))
            # 5m & 4h down move, 15m still high
            & ((_cmp_cached_0) | (_cmp_cached_55) | (_cmp_cached_31))
            # 5m & 4h down move, 15m still high
            & ((_cmp_cached_0) | (_cmp_cached_55) | (_cmp_cached_155))
            # 5m & 4h down move, 15m still high
            & ((_cmp_cached_0) | (_cmp_cached_100) | (_cmp_cached_61))
            # 5m & 4h down move, 1h high
            & ((_cmp_cached_0) | (_cmp_cached_91) | (_cmp_cached_19))
            # 5m & 1d down move, 15m high
            & ((_cmp_cached_0) | (_cmp_cached_153) | (_cmp_cached_76))
            # 5m & 1d down move, 15m stil high
            & ((_cmp_cached_0) | (_cmp_cached_153) | (_cmp_cached_155))
            # 5m & 1d down move, 4h still high
            & ((_cmp_cached_0) | (_cmp_cached_153) | (_cmp_cached_165))
            # 5m down move, 1h high
            & ((_cmp_cached_0) | (_cmp_cached_49))
            # 5m down move, 15m & 1d high
            & ((_cmp_cached_8) | (_cmp_cached_210) | (_cmp_cached_27))
            # 5m down move, 1h & 1d high
            & ((_cmp_cached_157) | (_cmp_cached_33) | (_cmp_cached_27))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_1) | (_cmp_cached_9) | (_cmp_cached_48))
            # 15m & 1h down move, 1h still not low enough
            & ((_cmp_cached_1) | (_cmp_cached_9) | (_cmp_cached_190))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_1) | (_cmp_cached_9) | (_cmp_cached_112))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_1) | (_cmp_cached_15) | (_cmp_cached_96))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_1) | (_cmp_cached_15) | (_cmp_cached_72))
            # 15m & 1h down move, 1d still high
            & ((_cmp_cached_1) | (_cmp_cached_30) | (_cmp_cached_14))
            # 15m & 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_11) | (_cmp_cached_169) | (_cmp_cached_186))
            # 15m & 1h down move, 15m still high
            & ((_cmp_cached_1) | (_cmp_cached_32) | (_cmp_cached_62))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_1) | (_cmp_cached_32) | (_cmp_cached_108))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_1) | (_cmp_cached_36) | (_cmp_cached_45))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_1) | (_cmp_cached_36) | (_cmp_cached_19))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_1) | (_cmp_cached_38) | (_cmp_cached_19))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_1) | (_cmp_cached_38) | (_cmp_cached_74))
            # 15m & 4h down move, 15m downtrend
            & ((_cmp_cached_1) | (_cmp_cached_151) | (_cmp_cached_159))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_1) | (_cmp_cached_16) | (_cmp_cached_96))
            # 15m down move, 1h high, 4h overbought
            & ((_cmp_cached_1) | (_cmp_cached_24) | (_cmp_cached_50))
            # 15m down move, 1d high & overbought
            & ((_cmp_cached_1) | (_cmp_cached_106) | (_cmp_cached_95))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_3) | (_cmp_cached_9) | (_cmp_cached_35))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_3) | (_cmp_cached_11) | (_cmp_cached_59))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_3) | (_cmp_cached_32) | (_cmp_cached_19))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_3) | (_cmp_cached_25) | (_cmp_cached_106))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_3) | (_cmp_cached_100) | (_cmp_cached_108))
            # 15m & 1d down move, 1d still high
            & ((_cmp_cached_3) | (_cmp_cached_153) | (_cmp_cached_119))
            # 15m down move, 15m downtrend, 1d high
            & ((_cmp_cached_3) | (_cmp_cached_43) | (_cmp_cached_27))
            # 15m down move, 4h high, 1h overbought
            & ((_cmp_cached_3) | (_cmp_cached_6) | (_cmp_cached_82))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_9) | (_cmp_cached_47))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_9) | (_cmp_cached_131))
            # 15m & 1h down move, 15m still high
            & ((_cmp_cached_5) | (_cmp_cached_15) | (_cmp_cached_61))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_5) | (_cmp_cached_15) | (_cmp_cached_59))
            # 15m & 1h down move, 1d still high
            & ((_cmp_cached_5) | (_cmp_cached_15) | (_cmp_cached_14))
            # 15m & 1h down move, 15m high
            & ((_cmp_cached_5) | (_cmp_cached_30) | (_cmp_cached_210))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_5) | (_cmp_cached_30) | (_cmp_cached_33))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_5) | (_cmp_cached_32) | (_cmp_cached_37))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_32) | (_cmp_cached_112))
            # 15m & 4h down move, 15m still high
            & ((_cmp_cached_5) | (_cmp_cached_58) | (_cmp_cached_31))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_58) | (_cmp_cached_108))
            # 15m & 4h down move, 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_58) | (_cmp_cached_57))
            # 15m & 4h down move, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_25) | (_cmp_cached_167))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_100) | (_cmp_cached_215))
            # 15m & 4h down move, 15m high
            & ((_cmp_cached_5) | (_cmp_cached_100) | (_cmp_cached_210))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_5) | (_cmp_cached_100) | (_cmp_cached_122))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_100) | (_cmp_cached_108))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_5) | (_cmp_cached_100) | (_cmp_cached_37))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_100) | (_cmp_cached_74))
            # 15m & 4h down move, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_100) | (_cmp_cached_107))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_41) | (_cmp_cached_70))
            # 15m & 4h down move, 15m high
            & ((_cmp_cached_5) | (_cmp_cached_181) | (_cmp_cached_76))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_91) | (_cmp_cached_17))
            # 15m down move, 1h high
            & ((_cmp_cached_5) | (_cmp_cached_49))
            # 15m & 1d down move, 1h still high
            & ((_cmp_cached_5) | (_cmp_cached_153) | (_cmp_cached_59))
            # 15m & 1d down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_178) | (_cmp_cached_60))
            # 15m down move, 15m & 1h high
            & ((_cmp_cached_5) | (_cmp_cached_210) | (_cmp_cached_80))
            # 15m down move, 15m & 4h high
            & ((_cmp_cached_5) | (_cmp_cached_210) | (_cmp_cached_17))
            # 15m down move, 15m high, 1h high
            & ((_cmp_cached_5) | (_cmp_cached_76) | (_cmp_cached_19))
            # 15m down move, 4h high, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_17) | (_cmp_cached_48))
            # 15m down move, 1d high & overbought
            & ((_cmp_cached_5) | (_cmp_cached_131) | (_cmp_cached_167))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_59) | (_cmp_cached_52))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_84) | (_cmp_cached_15) | (_cmp_cached_24))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_84) | (_cmp_cached_15) | (_cmp_cached_77))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_84) | (_cmp_cached_36) | (_cmp_cached_78))
            # 15m & 4h down move, 15m high
            & ((_cmp_cached_84) | (_cmp_cached_25) | (_cmp_cached_62))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_84) | (_cmp_cached_25) | (_cmp_cached_37))
            # 15m & 4h down move, 15m high
            & ((_cmp_cached_84) | (_cmp_cached_100) | (_cmp_cached_76))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_84) | (_cmp_cached_16) | (_cmp_cached_40))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_84) | (_cmp_cached_16) | (_cmp_cached_165))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_84) | (_cmp_cached_21) | (_cmp_cached_78))
            # 15m & 1d down move, 1h still high
            & ((_cmp_cached_84) | (_cmp_cached_29) | (_cmp_cached_161))
            # 15m down move, 15m downtrend, 1h high
            & ((_cmp_cached_84) | (_cmp_cached_43) | (_cmp_cached_115))
            # 15m down move, 15m still high, 4h high
            & ((_cmp_cached_84) | (_cmp_cached_62) | (_cmp_cached_12))
            # 15m down move, 15m high, 1d overbought
            & ((_cmp_cached_84) | (_cmp_cached_76) | (_cmp_cached_167))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_84) | (_cmp_cached_80) | (_cmp_cached_6))
            # 15m down move, 4h & 1d overbought
            & ((_cmp_cached_84) | (_cmp_cached_20) | (_cmp_cached_63))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_87) | (_cmp_cached_33) | (_cmp_cached_95))
            # 15m down move, 1h high, 1d downtrend
            & ((_cmp_cached_87) | (_cmp_cached_19) | (_cmp_cached_57))
            # 15m down move, 4h high, 1d downtrend
            & ((_cmp_cached_87) | (_cmp_cached_12) | (_cmp_cached_102))
            # 15m & 4h down move, 15m high
            & ((_cmp_cached_88) | (_cmp_cached_41) | (_cmp_cached_92))
            # 15m down move, 15m & 1h high
            & ((_cmp_cached_88) | (_cmp_cached_76) | (_cmp_cached_80))
            # 15m & 4h down mve, 1h high
            & ((_cmp_cached_89) | (_cmp_cached_41) | (_cmp_cached_19))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_89) | (_cmp_cached_91) | (_cmp_cached_12))
            # 15m down move, 15m & 1h high
            & ((_cmp_cached_89) | (_cmp_cached_76) | (_cmp_cached_78))
            # 15m down move, 1h high, 1d downtrend
            & ((_cmp_cached_89) | (_cmp_cached_78) | (_cmp_cached_186))
            # 15m down move, 15m high, 4h high
            & ((_cmp_cached_184) | (_cmp_cached_76) | (_cmp_cached_12))
            # 15m down move, 15m & 4h high
            & ((_cmp_cached_184) | (_cmp_cached_76) | (_cmp_cached_46))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_13) | (_cmp_cached_58) | (_cmp_cached_332))
            # 1h & 4h down move, 1d still high
            & ((_cmp_cached_13) | (_cmp_cached_58) | (_cmp_cached_56))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_13) | (_cmp_cached_16) | (_cmp_cached_95))
            # 1h & 1d down move, 1d still high
            & ((_cmp_cached_13) | (_cmp_cached_121) | (_cmp_cached_56))
            # 1h & 4h down move, 15m still not low enough
            & ((_cmp_cached_7) | (_cmp_cached_55) | (_cmp_cached_171))
            # 1h & 4h down move, 4h downtrend
            & ((_cmp_cached_7) | (_cmp_cached_58) | (_cmp_cached_93))
            # 1h & 4h down move, 15m high
            & ((_cmp_cached_7) | (_cmp_cached_16) | (_cmp_cached_222))
            # 1h & 4h down move, 1d still high
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_238))
            # 1h & 4h down move, 15m still high
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_92))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_9) | (_cmp_cached_25) | (_cmp_cached_98))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_9) | (_cmp_cached_100) | (_cmp_cached_96))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_9) | (_cmp_cached_16) | (_cmp_cached_162))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_9) | (_cmp_cached_181) | (_cmp_cached_17))
            # 1h & 1d down move, 1h still not low enough
            & ((_cmp_cached_9) | (_cmp_cached_29) | (_cmp_cached_188))
            # 1h & 1d down move, 1h still not low enough
            & ((_cmp_cached_9) | (_cmp_cached_104) | (_cmp_cached_150))
            # 1h down move, 15m downtrend, 1d high
            & ((_cmp_cached_9) | (_cmp_cached_43) | (_cmp_cached_106))
            # 1h down move, 1h high, 4h high
            & ((_cmp_cached_9) | (_cmp_cached_24) | (_cmp_cached_12))
            # 1h & 4h down move, 1h still high
            & ((_cmp_cached_15) | (_cmp_cached_25) | (_cmp_cached_110))
            # 1h & 4h down move, 1h still high
            & ((_cmp_cached_15) | (_cmp_cached_25) | (_cmp_cached_59))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_15) | (_cmp_cached_25) | (_cmp_cached_102))
            # 1h & 1d down move, 4h downtrend
            & ((_cmp_cached_15) | (_cmp_cached_29) | (_cmp_cached_103))
            # 1h & 1d down move, 1d still high
            & ((_cmp_cached_15) | (_cmp_cached_121) | (_cmp_cached_238))
            # 1h & 1d down move, 1d high
            & ((_cmp_cached_15) | (_cmp_cached_192) | (_cmp_cached_106))
            # 1h down move, 1h still high, 1d high
            & ((_cmp_cached_15) | (_cmp_cached_26) | (_cmp_cached_74))
            # 1h down move, 1h still high, 4h overbought
            & ((_cmp_cached_15) | (_cmp_cached_26) | (_cmp_cached_50))
            # 1h down move, 1h still high, 1d downtrend
            & ((_cmp_cached_15) | (_cmp_cached_26) | (_cmp_cached_102))
            # 1h down move, 4h still high, 1d overbought
            & ((_cmp_cached_15) | (_cmp_cached_122) | (_cmp_cached_52))
            # 1h down move, 1d high, 4h downtrend
            & ((_cmp_cached_15) | (_cmp_cached_106) | (_cmp_cached_69))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_30) | (_cmp_cached_16) | (_cmp_cached_108))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_30) | (_cmp_cached_41) | (_cmp_cached_48))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_30) | (_cmp_cached_21) | (_cmp_cached_24))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_30) | (_cmp_cached_99) | (_cmp_cached_6))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_30) | (_cmp_cached_121) | (_cmp_cached_102))
            # 1h down move, 15m still high, 1d high
            & ((_cmp_cached_30) | (_cmp_cached_31) | (_cmp_cached_94))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_30) | (_cmp_cached_115) | (_cmp_cached_95))
            # 1h & 4h down move, 15m high
            & ((_cmp_cached_11) | (_cmp_cached_16) | (_cmp_cached_92))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_11) | (_cmp_cached_41) | (_cmp_cached_33))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_11) | (_cmp_cached_41) | (_cmp_cached_40))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_32) | (_cmp_cached_21) | (_cmp_cached_250))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_32) | (_cmp_cached_131) | (_cmp_cached_52))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_32) | (_cmp_cached_74) | (_cmp_cached_167))
            # 1h down move, 15m still high, 1h high
            & ((_cmp_cached_32) | (_cmp_cached_62) | (_cmp_cached_45))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_32) | (_cmp_cached_46) | (_cmp_cached_52))
            # 1h & 4h down move, 1h still high
            & ((_cmp_cached_34) | (_cmp_cached_21) | (_cmp_cached_59))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_34) | (_cmp_cached_99) | (_cmp_cached_77))
            # 1h down move, 1h high , 1d overbought
            & ((_cmp_cached_34) | (_cmp_cached_19) | (_cmp_cached_70))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_34) | (_cmp_cached_17) | (_cmp_cached_48))
            # 1h & 1d down move, 1h high
            & ((_cmp_cached_38) | (_cmp_cached_198) | (_cmp_cached_33))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_38) | (_cmp_cached_68) | (_cmp_cached_6))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_117) | (_cmp_cached_72) | (_cmp_cached_211))
            # 1h & 1d down move, 1h high
            & ((_cmp_cached_53) | (_cmp_cached_126) | (_cmp_cached_24))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_151) | (_cmp_cached_104) | (_cmp_cached_176))
            # 4h down move, 1h still not low enough, 4h downtrend
            & ((_cmp_cached_151) | (_cmp_cached_188) | (_cmp_cached_93))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_55) | (_cmp_cached_178) | (_cmp_cached_56))
            # 4h down move, 1h high
            & ((_cmp_cached_55) | (_cmp_cached_49))
            # 4h down move, 4h & 1d downtrend
            & ((_cmp_cached_55) | (_cmp_cached_93) | (_cmp_cached_186))
            # 4h & 1d down move, 1h high
            & ((_cmp_cached_58) | (_cmp_cached_153) | (_cmp_cached_123))
            # 4h & 1d down move, 4h downtrend
            & ((_cmp_cached_58) | (_cmp_cached_153) | (_cmp_cached_69))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_58) | (_cmp_cached_29) | (_cmp_cached_119))
            # 4h & 1d down move, 1d downtrend
            & ((_cmp_cached_58) | (_cmp_cached_29) | (_cmp_cached_102))
            # 4h & 1d down move, 1h high
            & ((_cmp_cached_58) | (_cmp_cached_178) | (_cmp_cached_80))
            # 4h down move, 15m still high, 1h still high
            & ((_cmp_cached_58) | (_cmp_cached_31) | (_cmp_cached_59))
            # 4h down move, 4h still high, 4h downtrend
            & ((_cmp_cached_58) | (_cmp_cached_96) | (_cmp_cached_69))
            # 4h down move, 15m high
            & ((_cmp_cached_58) | (_cmp_cached_180))
            # 4h down move, 1h still not low enough, 4h downtrend
            & ((_cmp_cached_58) | (_cmp_cached_190) | (_cmp_cached_69))
            # 4h & 1d down move, 15m still high
            & ((_cmp_cached_25) | (_cmp_cached_29) | (_cmp_cached_61))
            # 4h & 1d down move, 1h still high
            & ((_cmp_cached_25) | (_cmp_cached_29) | (_cmp_cached_28))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_25) | (_cmp_cached_104) | (_cmp_cached_199))
            # 4h & 1d down move, 4h high
            & ((_cmp_cached_25) | (_cmp_cached_121) | (_cmp_cached_17))
            # 4h & 1d down move, 4h still high
            & ((_cmp_cached_25) | (_cmp_cached_178) | (_cmp_cached_35))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_25) | (_cmp_cached_125) | (_cmp_cached_106))
            # 4h & 1d down move, 4h still high
            & ((_cmp_cached_25) | (_cmp_cached_73) | (_cmp_cached_165))
            # 4h down move, 1d still high, 4h still not low enough
            & ((_cmp_cached_25) | (_cmp_cached_176) | (_cmp_cached_124))
            # 4h down move, 4h still high, 4h downtrend
            & ((_cmp_cached_25) | (_cmp_cached_122) | (_cmp_cached_93))
            # 4h down move, 1d still high, 1d downtrend
            & ((_cmp_cached_25) | (_cmp_cached_238) | (_cmp_cached_57))
            # 4h down move, 4h still not low enough, 1d downtrend
            & ((_cmp_cached_25) | (_cmp_cached_156) | (_cmp_cached_57))
            # 4h down move, 1h downtrend, 1d overbought
            & ((_cmp_cached_25) | (_cmp_cached_132) | (_cmp_cached_111))
            # 4h down move, 4h high, 4h downtrend
            & ((_cmp_cached_100) | (_cmp_cached_40) | (_cmp_cached_69))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_100) | (_cmp_cached_108) | (_cmp_cached_216))
            # 4h down move, 4h & 1d downtrend
            & ((_cmp_cached_16) | (_cmp_cached_93) | (_cmp_cached_186))
            # 1h down move, 4h still not low enough, 1d downtrend
            & ((_cmp_cached_100) | (_cmp_cached_124) | (_cmp_cached_57))
            # 4h & 1d down move, 1h high
            & ((_cmp_cached_16) | (_cmp_cached_121) | (_cmp_cached_19))
            # 4h down move, 1h high
            & ((_cmp_cached_16) | (_cmp_cached_37))
            # 4h & 1d down move, 1d overbought
            & ((_cmp_cached_16) | (_cmp_cached_125) | (_cmp_cached_70))
            # 4h & 1d down move, 4h still high
            & ((_cmp_cached_41) | (_cmp_cached_178) | (_cmp_cached_35))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_41) | (_cmp_cached_126) | (_cmp_cached_94))
            # 4h down move, 15m & 4h high
            & ((_cmp_cached_41) | (_cmp_cached_76) | (_cmp_cached_17))
            # 4h down move, 1h high, 1d downtrend
            & ((_cmp_cached_41) | (_cmp_cached_19) | (_cmp_cached_65))
            # 4h down move, 4h & 1d downtrend
            & ((_cmp_cached_41) | (_cmp_cached_69) | (_cmp_cached_65))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_21) | (_cmp_cached_165) | (_cmp_cached_102))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_21) | (_cmp_cached_74) | (_cmp_cached_167))
            # 4h down move, 15m still high, 1h high
            & ((_cmp_cached_21) | (_cmp_cached_62) | (_cmp_cached_80))
            # 4h down move, 1h high
            & ((_cmp_cached_181) | (_cmp_cached_33))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_91) | (_cmp_cached_106) | (_cmp_cached_167))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_175) | (_cmp_cached_39) | (_cmp_cached_63))
            # 1d down move, 1d high, 4h downtrend
            & ((_cmp_cached_29) | (_cmp_cached_106) | (_cmp_cached_213))
            # 1d down move, 1h & 4h high
            & ((_cmp_cached_178) | (_cmp_cached_24) | (_cmp_cached_6))
            # 1d down move, 4h high, 1d overbought
            & ((_cmp_cached_198) | (_cmp_cached_72) | (_cmp_cached_95))
            # 1d down move, 1d high & overbought
            & ((_cmp_cached_223) | (_cmp_cached_74) | (_cmp_cached_95))
            # 1d down move, 1d overbought
            & ((_cmp_cached_126) | (_cmp_cached_111))
            # 15m & 1h high, 4h overbought
            & ((_cmp_cached_76) | (_cmp_cached_80) | (_cmp_cached_263))
            # 15m & 1h high, 1d overbought
            & ((_cmp_cached_76) | (_cmp_cached_80) | (_cmp_cached_48))
            # 15m & 1h high, 1d downtrend
            & ((_cmp_cached_76) | (_cmp_cached_80) | (_cmp_cached_186))
            # 15m high, 1d high & overbought
            & ((_cmp_cached_76) | (_cmp_cached_94) | (_cmp_cached_70))
            # 15m high, 1d high & overbought
            & ((_cmp_cached_76) | (_cmp_cached_27) | (_cmp_cached_167))
            # 15m high, 1h high, 1d downtrend
            & ((_cmp_cached_76) | (_cmp_cached_19) | (_cmp_cached_57))
            # 1h & 4h high, 4h overbought
            & ((_cmp_cached_78) | (_cmp_cached_46) | (_cmp_cached_50))
            # 1h & 4h high, 1d overbought
            & ((_cmp_cached_78) | (_cmp_cached_6) | (_cmp_cached_107))
            # 1h & 1d high, 1d overbought
            & ((_cmp_cached_80) | (_cmp_cached_27) | (_cmp_cached_52))
            # 4h & 1d high, 4h overbought
            & ((_cmp_cached_6) | (_cmp_cached_27) | (_cmp_cached_86))
            # 4h & 1d high, 1d overbought
            & ((_cmp_cached_46) | (_cmp_cached_27) | (_cmp_cached_107))
            # 1h high, 1h & 4h overbought
            & ((_cmp_cached_19) | (_cmp_cached_79) | (_cmp_cached_20))
            # 4h & 1d overbought
            & ((_cmp_cached_196) | (_cmp_cached_111))
          )

          # Logic
          long_entry_logic.append(
            (df["RSI_20"] < df["RSI_20"].shift(1))
            & (_cmp_cached_333)
            & (_cmp_cached_243)
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
            ((_cmp_cached_157) | (_cmp_cached_58) | (_cmp_cached_31))
            # 5m & 1d down move, 15m high
            & ((_cmp_cached_157) | (_cmp_cached_178) | (_cmp_cached_18))
            # 5m down move, 1h & 1d high
            & ((_cmp_cached_157) | (_cmp_cached_33) | (_cmp_cached_27))
            # 5m down move, 15m & 1h high
            & ((_cmp_cached_157) | (_cmp_cached_276) | (_cmp_cached_80))
            # 15m & 1h & 4h down move
            & ((_cmp_cached_1) | (_cmp_cached_13) | (_cmp_cached_25))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_1) | (_cmp_cached_9) | (_cmp_cached_106))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_1) | (_cmp_cached_9) | (_cmp_cached_28))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_1) | (_cmp_cached_9) | (_cmp_cached_112))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_1) | (_cmp_cached_15) | (_cmp_cached_26))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_1) | (_cmp_cached_15) | (_cmp_cached_96))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_1) | (_cmp_cached_15) | (_cmp_cached_72))
            # 15m & 1h down move, 15m high
            & ((_cmp_cached_1) | (_cmp_cached_32) | (_cmp_cached_76))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_1) | (_cmp_cached_36) | (_cmp_cached_68))
            # 15m & 4h down move, 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_58) | (_cmp_cached_57))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_1) | (_cmp_cached_16) | (_cmp_cached_96))
            # 15m down move, 1h high, 4h overbought
            & ((_cmp_cached_1) | (_cmp_cached_24) | (_cmp_cached_50))
            # 15m down move, 4h high
            & ((_cmp_cached_1) | (_cmp_cached_46))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_1) | (_cmp_cached_123) | (_cmp_cached_167))
            # 15m down move, 4h high
            & ((_cmp_cached_1) | (_cmp_cached_12))
            # 15m & 1h down move, 15m still not low enough
            & ((_cmp_cached_3) | (_cmp_cached_7) | (_cmp_cached_152))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_3) | (_cmp_cached_9) | (_cmp_cached_35))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_3) | (_cmp_cached_25) | (_cmp_cached_106))
            # 15m & 4h down move, 15m high
            & ((_cmp_cached_3) | (_cmp_cached_100) | (_cmp_cached_210))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_15) | (_cmp_cached_47))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_15) | (_cmp_cached_162))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_3) | (_cmp_cached_100) | (_cmp_cached_108))
            # 15m down move, 4h high, 1h overbought
            & ((_cmp_cached_3) | (_cmp_cached_6) | (_cmp_cached_82))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_9) | (_cmp_cached_47))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_5) | (_cmp_cached_9) | (_cmp_cached_28))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_9) | (_cmp_cached_162))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_5) | (_cmp_cached_15) | (_cmp_cached_59))
            # 15m & 1h down move, 15m high
            & ((_cmp_cached_5) | (_cmp_cached_30) | (_cmp_cached_210))
            # 15m & 1h down move, 15m still high
            & ((_cmp_cached_5) | (_cmp_cached_11) | (_cmp_cached_31))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_5) | (_cmp_cached_32) | (_cmp_cached_37))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_32) | (_cmp_cached_112))
            # 15m & 4h down move, 1d still high
            & ((_cmp_cached_5) | (_cmp_cached_58) | (_cmp_cached_238))
            # 15m & 4h down move, 15m still high
            & ((_cmp_cached_5) | (_cmp_cached_25) | (_cmp_cached_62))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_25) | (_cmp_cached_108))
            # 15m & 4h down move, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_25) | (_cmp_cached_167))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_100) | (_cmp_cached_215))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_5) | (_cmp_cached_100) | (_cmp_cached_122))
            # 14m & 4h down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_100) | (_cmp_cached_108))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_5) | (_cmp_cached_100) | (_cmp_cached_37))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_100) | (_cmp_cached_74))
            # 15m & 4h down move, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_100) | (_cmp_cached_107))
            # 15m & 4h down move, 15m high
            & ((_cmp_cached_5) | (_cmp_cached_41) | (_cmp_cached_76))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_41) | (_cmp_cached_70))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_5) | (_cmp_cached_21) | (_cmp_cached_78))
            # 15m & 4h down move, 4h overbought
            & ((_cmp_cached_5) | (_cmp_cached_21) | (_cmp_cached_50))
            # 15m & 4h down move, 15m high
            & ((_cmp_cached_5) | (_cmp_cached_181) | (_cmp_cached_76))
            # 15m & 1d down move, 1h still high
            & ((_cmp_cached_5) | (_cmp_cached_153) | (_cmp_cached_59))
            # 15m down move, 15m high, 1h high
            & ((_cmp_cached_5) | (_cmp_cached_76) | (_cmp_cached_19))
            # 15m down move, 4h high, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_17) | (_cmp_cached_48))
            # 15m down move, 1d high & overbought
            & ((_cmp_cached_5) | (_cmp_cached_131) | (_cmp_cached_167))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_59) | (_cmp_cached_52))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_84) | (_cmp_cached_15) | (_cmp_cached_24))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_84) | (_cmp_cached_11) | (_cmp_cached_6))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_84) | (_cmp_cached_36) | (_cmp_cached_78))
            # 15m & 4h down move, 15m high
            & ((_cmp_cached_84) | (_cmp_cached_25) | (_cmp_cached_76))
            # 15m & 4h down move, 1d downtrend
            & ((_cmp_cached_84) | (_cmp_cached_25) | (_cmp_cached_57))
            # 15m & 4h down move, 1d overbought
            & ((_cmp_cached_84) | (_cmp_cached_100) | (_cmp_cached_107))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_84) | (_cmp_cached_21) | (_cmp_cached_78))
            # 15m & 1d down move, 4h high
            & ((_cmp_cached_84) | (_cmp_cached_104) | (_cmp_cached_12))
            # 15m down move, 15m downtrend, 1h high
            & ((_cmp_cached_84) | (_cmp_cached_43) | (_cmp_cached_115))
            # 15m down move, 15m still high, 4h high
            & ((_cmp_cached_84) | (_cmp_cached_62) | (_cmp_cached_12))
            # 15m down move, 15m high, 1d overbought
            & ((_cmp_cached_84) | (_cmp_cached_76) | (_cmp_cached_95))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_84) | (_cmp_cached_80) | (_cmp_cached_6))
            # 15m down move, 1d high & overbought
            & ((_cmp_cached_84) | (_cmp_cached_27) | (_cmp_cached_63))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_87) | (_cmp_cached_30) | (_cmp_cached_123))
            # 15m & 4h down move, 15m high
            & ((_cmp_cached_87) | (_cmp_cached_100) | (_cmp_cached_76))
            # 15m & 4h down move, 15m still high
            & ((_cmp_cached_87) | (_cmp_cached_100) | (_cmp_cached_61))
            # 15m down move, 15m & 1h high
            & ((_cmp_cached_87) | (_cmp_cached_76) | (_cmp_cached_80))
            # 15m down move, 15m high, 1d high
            & ((_cmp_cached_87) | (_cmp_cached_274) | (_cmp_cached_27))
            # 15m down move, 1h high, 1d downtrend
            & ((_cmp_cached_87) | (_cmp_cached_19) | (_cmp_cached_57))
            # 15m down move, 1h high & overbought
            & ((_cmp_cached_87) | (_cmp_cached_49) | (_cmp_cached_82))
            # 15m down move, 15m still high, 4h high
            & ((_cmp_cached_88) | (_cmp_cached_62) | (_cmp_cached_77))
            # 15m & 4h down mve, 1h high
            & ((_cmp_cached_89) | (_cmp_cached_41) | (_cmp_cached_19))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_89) | (_cmp_cached_91) | (_cmp_cached_12))
            # 15m down move, 1h high, 1d downtrend
            & ((_cmp_cached_89) | (_cmp_cached_78) | (_cmp_cached_186))
            # 15m down move, 15m high, 4h high
            & ((_cmp_cached_184) | (_cmp_cached_76) | (_cmp_cached_12))
            # 15m down move, 15m & 4h high
            & ((_cmp_cached_184) | (_cmp_cached_76) | (_cmp_cached_46))
            # 15m down move, 15m high, 1d overbought
            & ((_cmp_cached_184) | (_cmp_cached_18) | (_cmp_cached_107))
            # 15m down move, 1d high, 1h overbought
            & ((_cmp_cached_90) | (_cmp_cached_74) | (_cmp_cached_79))
            # 1h & 4h down move, 1d still high
            & ((_cmp_cached_13) | (_cmp_cached_58) | (_cmp_cached_238))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_13) | (_cmp_cached_16) | (_cmp_cached_95))
            # 1h & 4h down move, 1d still high
            & ((_cmp_cached_7) | (_cmp_cached_25) | (_cmp_cached_119))
            # 1h & 4h & 1d down move
            & ((_cmp_cached_7) | (_cmp_cached_100) | (_cmp_cached_121))
            # 1h & 4h down move, 15m high
            & ((_cmp_cached_7) | (_cmp_cached_16) | (_cmp_cached_222))
            # 1h & 4h & 1d down move
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_29))
            # 1h & 4h down move, 1d still not low enough
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_265))
            # 1h & 4h down move, 15m still high
            & ((_cmp_cached_9) | (_cmp_cached_25) | (_cmp_cached_61))
            # 1h & 4h down move, 1h still not low enough
            & ((_cmp_cached_9) | (_cmp_cached_100) | (_cmp_cached_150))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_9) | (_cmp_cached_100) | (_cmp_cached_48))
            # 1h & 1d downtrend, 1d high
            & ((_cmp_cached_9) | (_cmp_cached_198) | (_cmp_cached_106))
            # 1h & 4h down move, 1h still not low enough
            & ((_cmp_cached_15) | (_cmp_cached_25) | (_cmp_cached_188))
            # 1h & 4h down move. 4h high
            & ((_cmp_cached_15) | (_cmp_cached_25) | (_cmp_cached_40))
            # 1h & 4h down move, 1d still high
            & ((_cmp_cached_15) | (_cmp_cached_25) | (_cmp_cached_238))
            # 1h & 4h down move, 1h still not low enough
            & ((_cmp_cached_15) | (_cmp_cached_25) | (_cmp_cached_161))
            # 1h & 4h down move, 15m still not low enough
            & ((_cmp_cached_15) | (_cmp_cached_25) | (_cmp_cached_152))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_15) | (_cmp_cached_100) | (_cmp_cached_165))
            # 1h & 1d down move, 1d still high
            & ((_cmp_cached_15) | (_cmp_cached_104) | (_cmp_cached_56))
            # 1h & 1d down move, 1d high
            & ((_cmp_cached_15) | (_cmp_cached_192) | (_cmp_cached_106))
            # 1h down move, 15m & 1d high
            & ((_cmp_cached_15) | (_cmp_cached_76) | (_cmp_cached_27))
            # 1h down move, 1h still high, 4h overbought
            & ((_cmp_cached_15) | (_cmp_cached_26) | (_cmp_cached_50))
            # 1h down move, 1h still high, 1d downtrend
            & ((_cmp_cached_15) | (_cmp_cached_26) | (_cmp_cached_102))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_15) | (_cmp_cached_51) | (_cmp_cached_107))
            # 1h & 4h down move, 1h still high
            & ((_cmp_cached_30) | (_cmp_cached_100) | (_cmp_cached_26))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_30) | (_cmp_cached_16) | (_cmp_cached_108))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_30) | (_cmp_cached_41) | (_cmp_cached_48))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_30) | (_cmp_cached_21) | (_cmp_cached_24))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_30) | (_cmp_cached_99) | (_cmp_cached_6))
            # 1h & 4h down move, 15m high
            & ((_cmp_cached_11) | (_cmp_cached_16) | (_cmp_cached_92))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_11) | (_cmp_cached_41) | (_cmp_cached_40))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_51) | (_cmp_cached_112))
            # 1h & 1d down move, 1d still high
            & ((_cmp_cached_11) | (_cmp_cached_121) | (_cmp_cached_14))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_32) | (_cmp_cached_41) | (_cmp_cached_123))
            # 1h & 4g down move, 4h still high
            & ((_cmp_cached_32) | (_cmp_cached_41) | (_cmp_cached_35))
            # 1h down move, 15m still high, 1h high
            & ((_cmp_cached_32) | (_cmp_cached_62) | (_cmp_cached_45))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_34) | (_cmp_cached_17) | (_cmp_cached_48))
            # 1h down move, 4h & 1d high
            & ((_cmp_cached_34) | (_cmp_cached_6) | (_cmp_cached_27))
            # 1h down move, 1h still high, 1d downtrend
            & ((_cmp_cached_34) | (_cmp_cached_59) | (_cmp_cached_102))
            # 1h & 1d down move, 1h high
            & ((_cmp_cached_38) | (_cmp_cached_198) | (_cmp_cached_33))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_38) | (_cmp_cached_68) | (_cmp_cached_6))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_117) | (_cmp_cached_72) | (_cmp_cached_211))
            # 4h & 1d down move, 1d downtrend
            & ((_cmp_cached_151) | (_cmp_cached_153) | (_cmp_cached_57))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_151) | (_cmp_cached_104) | (_cmp_cached_176))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_55) | (_cmp_cached_198) | (_cmp_cached_106))
            # 4h down move, 4h still high, 4h downtrend
            & ((_cmp_cached_55) | (_cmp_cached_96) | (_cmp_cached_93))
            # 4h down move, 1h high
            & ((_cmp_cached_55) | (_cmp_cached_49))
            # 4h & 1d down move, 1h still high
            & ((_cmp_cached_58) | (_cmp_cached_153) | (_cmp_cached_59))
            # 4h & 1d down move, 1h high
            & ((_cmp_cached_58) | (_cmp_cached_29) | (_cmp_cached_37))
            # 4h down move, 15m still high, 1h still high
            & ((_cmp_cached_58) | (_cmp_cached_31) | (_cmp_cached_59))
            # 4h down move, 1d still high, 1d downtrend
            & ((_cmp_cached_58) | (_cmp_cached_238) | (_cmp_cached_102))
            # 4h down move, 15m high
            & ((_cmp_cached_58) | (_cmp_cached_180))
            # 4h down move, 15m still high, 1d downtrend
            & ((_cmp_cached_58) | (_cmp_cached_61) | (_cmp_cached_102))
            # 4h down move, 1h still high, 1d downtrend
            & ((_cmp_cached_58) | (_cmp_cached_59) | (_cmp_cached_102))
            # 4h down move, 1h high, 4h downtrend
            & ((_cmp_cached_58) | (_cmp_cached_37) | (_cmp_cached_69))
            # 4h down move, 4h & 1d downtrend
            & ((_cmp_cached_58) | (_cmp_cached_219) | (_cmp_cached_57))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_25) | (_cmp_cached_29) | (_cmp_cached_238))
            # 4h & 1d down move, 4h still high
            & ((_cmp_cached_25) | (_cmp_cached_104) | (_cmp_cached_96))
            # 4h & 1d down move, 4h high
            & ((_cmp_cached_25) | (_cmp_cached_121) | (_cmp_cached_17))
            # 4h & 1d down move, 15m high
            & ((_cmp_cached_25) | (_cmp_cached_178) | (_cmp_cached_180))
            # 4h & 1d down move, 4h still high
            & ((_cmp_cached_25) | (_cmp_cached_73) | (_cmp_cached_165))
            # 4h down move, 1d still high, 4h still not low enough
            & ((_cmp_cached_25) | (_cmp_cached_176) | (_cmp_cached_124))
            # 4h down move, 15m still not low enough, 1d high
            & ((_cmp_cached_25) | (_cmp_cached_10) | (_cmp_cached_106))
            # 4h down move, 4h still high, 4h downtrend
            & ((_cmp_cached_25) | (_cmp_cached_122) | (_cmp_cached_93))
            # 4h down move, 4h still not low enough, 1d downtrend
            & ((_cmp_cached_25) | (_cmp_cached_156) | (_cmp_cached_57))
            # 4h down move, 4h & 1d high
            & ((_cmp_cached_100) | (_cmp_cached_17) | (_cmp_cached_106))
            # 4h down move, 4h high
            & ((_cmp_cached_100) | (_cmp_cached_77))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_100) | (_cmp_cached_108) | (_cmp_cached_216))
            # 4h down move, 4h still high, 4h downtrend
            & ((_cmp_cached_100) | (_cmp_cached_35) | (_cmp_cached_69))
            # 4h down move, 4h high, 1d downtrend
            & ((_cmp_cached_100) | (_cmp_cached_64) | (_cmp_cached_57))
            # 4h down move, 1d overbought
            & ((_cmp_cached_100) | (_cmp_cached_63))
            # 4h & 1d down move, 4h overbought
            & ((_cmp_cached_16) | (_cmp_cached_198) | (_cmp_cached_334))
            # 4h & 1d down move, 1d overbought
            & ((_cmp_cached_16) | (_cmp_cached_198) | (_cmp_cached_95))
            # 4h down move, 15m still not low enough, 4h still high
            & ((_cmp_cached_16) | (_cmp_cached_10) | (_cmp_cached_165))
            # 4h down move, 1d high, 4h overbought
            & ((_cmp_cached_16) | (_cmp_cached_108) | (_cmp_cached_334))
            # 4h & 1d down move, 4h still high
            & ((_cmp_cached_41) | (_cmp_cached_178) | (_cmp_cached_35))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_41) | (_cmp_cached_126) | (_cmp_cached_94))
            # 4h down move, 4h high, 1d high
            & ((_cmp_cached_41) | (_cmp_cached_17) | (_cmp_cached_74))
            # 4h down move, 1d stil high, 1d downtrend
            & ((_cmp_cached_41) | (_cmp_cached_119) | (_cmp_cached_102))
            # 4h down move, 1h high, 1d downtrend
            & ((_cmp_cached_41) | (_cmp_cached_19) | (_cmp_cached_65))
            # 4h down move, 15m still high, 1h high
            & ((_cmp_cached_21) | (_cmp_cached_62) | (_cmp_cached_80))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_21) | (_cmp_cached_165) | (_cmp_cached_102))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_21) | (_cmp_cached_74) | (_cmp_cached_167))
            # 4h down move, 1h high
            & ((_cmp_cached_181) | (_cmp_cached_33))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_91) | (_cmp_cached_106) | (_cmp_cached_167))
            # 4h down move, 4h high, 1d downtrend
            & ((_cmp_cached_91) | (_cmp_cached_165) | (_cmp_cached_195))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_99) | (_cmp_cached_131) | (_cmp_cached_111))
            # 4h down move, 4h high & overbought
            & ((_cmp_cached_99) | (_cmp_cached_64) | (_cmp_cached_50))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_99) | (_cmp_cached_35) | (_cmp_cached_65))
            # 4h down move, 4h & 1d overbought
            & ((_cmp_cached_99) | (_cmp_cached_50) | (_cmp_cached_107))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_175) | (_cmp_cached_39) | (_cmp_cached_63))
            # 1d down move, 1d high, 4h downtrend
            & ((_cmp_cached_29) | (_cmp_cached_106) | (_cmp_cached_213))
            # 1d down move, 1d high, 1d downtrend
            & ((_cmp_cached_29) | (_cmp_cached_106) | (_cmp_cached_57))
            # 1d down move, 1h & 4h high
            & ((_cmp_cached_178) | (_cmp_cached_24) | (_cmp_cached_6))
            # 15m & 1h high, 4h overbought
            & ((_cmp_cached_76) | (_cmp_cached_80) | (_cmp_cached_263))
            # 15m & 1h high, 1d overbought
            & ((_cmp_cached_76) | (_cmp_cached_80) | (_cmp_cached_48))
            # 15m & 1h high, 1d downtrend
            & ((_cmp_cached_76) | (_cmp_cached_80) | (_cmp_cached_186))
            # 15m & 4h & 1d high
            & ((_cmp_cached_76) | (_cmp_cached_46) | (_cmp_cached_27))
            # 15m high, 1d high & overbought
            & ((_cmp_cached_76) | (_cmp_cached_27) | (_cmp_cached_167))
            # 15m high, 1h & 4h overbought
            & ((_cmp_cached_76) | (_cmp_cached_82) | (_cmp_cached_50))
            # 15m high, 4h overbought, 1d downtrend
            & ((_cmp_cached_18) | (_cmp_cached_20) | (_cmp_cached_102))
            # 15m & 1h high
            & ((_cmp_cached_274) | (_cmp_cached_80))
            # 15m & 4h high
            & ((_cmp_cached_274) | (_cmp_cached_6))
            # 1h & 1d high, 1d overbought
            & ((_cmp_cached_80) | (_cmp_cached_27) | (_cmp_cached_95))
            # 1h & 4h high, 1h overbought
            & ((_cmp_cached_80) | (_cmp_cached_6) | (_cmp_cached_82))
            # 1h & 4h high, 4h overbought
            & ((_cmp_cached_80) | (_cmp_cached_6) | (_cmp_cached_50))
            # 4h & 1d high, 4h overbought
            & ((_cmp_cached_6) | (_cmp_cached_27) | (_cmp_cached_20))
            # 4h & 1d high, 1d overbought
            & ((_cmp_cached_6) | (_cmp_cached_27) | (_cmp_cached_70))
            # 4h high, 1h & 4h overbought
            & ((_cmp_cached_6) | (_cmp_cached_79) | (_cmp_cached_113))
            # 1d high, 4h & 1d downtrend
            & ((_cmp_cached_199) | (_cmp_cached_69) | (_cmp_cached_102))
            # 1d high, 4h & 1d overbought
            & ((_cmp_cached_27) | (_cmp_cached_83) | (_cmp_cached_48))
            # 15m high, 4h & 1d overbought
            & ((_cmp_cached_92) | (_cmp_cached_20) | (_cmp_cached_167))
            # 1h high, 1h & 1d overbought
            & ((_cmp_cached_19) | (_cmp_cached_79) | (_cmp_cached_48))
            # 4h high, 4h overbought, 1d downtrend
            & ((_cmp_cached_72) | (_cmp_cached_20) | (_cmp_cached_57))
            # 1d high, 1h & 4h overbought
            & ((_cmp_cached_74) | (_cmp_cached_79) | (_cmp_cached_20))
          )

          # Logic
          long_entry_logic.append(
            (_cmp_cached_8)
            & (_cmp_cached_335)
            # & (_cmp_cached_237)
            & (df["RSI_20"] < df["RSI_20"].shift(1))
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
            ((_cmp_cached_0) | (_cmp_cached_58) | (_cmp_cached_153))
            # 5m & 4h down move, 4h still high
            & ((_cmp_cached_0) | (_cmp_cached_58) | (_cmp_cached_35))
            # 15m & 1h down move, 1h still not low enough
            & ((_cmp_cached_1) | (_cmp_cached_13) | (_cmp_cached_160))
            # 15m & 1h & 4h down move
            & ((_cmp_cached_1) | (_cmp_cached_7) | (_cmp_cached_58))
            # 15m & 1h down move, 15m still high
            & ((_cmp_cached_1) | (_cmp_cached_15) | (_cmp_cached_31))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_1) | (_cmp_cached_15) | (_cmp_cached_96))
            # 15m & 1h down move, 1h still high
            & ((_cmp_cached_1) | (_cmp_cached_15) | (_cmp_cached_59))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_1) | (_cmp_cached_15) | (_cmp_cached_72))
            # 15m & 1h down move, 15m high
            & ((_cmp_cached_1) | (_cmp_cached_32) | (_cmp_cached_76))
            # 15m & 1h down move, 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_34) | (_cmp_cached_102))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_1) | (_cmp_cached_36) | (_cmp_cached_45))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_1) | (_cmp_cached_25) | (_cmp_cached_122))
            # 15m & 4h down move, 15m still high
            & ((_cmp_cached_1) | (_cmp_cached_100) | (_cmp_cached_62))
            # 15m & 1d down move, 4h still high
            & ((_cmp_cached_1) | (_cmp_cached_104) | (_cmp_cached_35))
            # 15m & 4h down move, 1d still high
            & ((_cmp_cached_3) | (_cmp_cached_55) | (_cmp_cached_176))
            # 15m & 1h down move, 4h still high
            & ((_cmp_cached_3) | (_cmp_cached_9) | (_cmp_cached_169))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_3) | (_cmp_cached_15) | (_cmp_cached_27))
            # 15m & 4h down move, 15m still not low enough
            & ((_cmp_cached_3) | (_cmp_cached_58) | (_cmp_cached_10))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_58) | (_cmp_cached_77))
            # 15m & 4h down move, 1h still high
            & ((_cmp_cached_3) | (_cmp_cached_58) | (_cmp_cached_28))
            # 15m & 4h down move, 1d downtrend
            & ((_cmp_cached_3) | (_cmp_cached_58) | (_cmp_cached_57))
            # 15m & 1d down move, 1h still high
            & ((_cmp_cached_3) | (_cmp_cached_153) | (_cmp_cached_26))
            # 15m & 1d down move, 1h still high
            & ((_cmp_cached_1) | (_cmp_cached_121) | (_cmp_cached_59))
            # 15m down move, 1h high, 4h overbought
            & ((_cmp_cached_1) | (_cmp_cached_24) | (_cmp_cached_50))
            # 15m down move, 4h high, 1d downtrend
            & ((_cmp_cached_1) | (_cmp_cached_64) | (_cmp_cached_57))
            # 15m down move, 15m still high, 1d downtrend
            & ((_cmp_cached_3) | (_cmp_cached_62) | (_cmp_cached_57))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_3) | (_cmp_cached_59) | (_cmp_cached_52))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_5) | (_cmp_cached_9) | (_cmp_cached_115))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_9) | (_cmp_cached_40))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_5) | (_cmp_cached_30) | (_cmp_cached_33))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_5) | (_cmp_cached_11) | (_cmp_cached_37))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_5) | (_cmp_cached_32) | (_cmp_cached_37))
            # 15m & 4h down move, 1h still high
            & ((_cmp_cached_5) | (_cmp_cached_58) | (_cmp_cached_59))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_5) | (_cmp_cached_100) | (_cmp_cached_37))
            # 15m & 4h down move, 4h overbought
            & ((_cmp_cached_5) | (_cmp_cached_21) | (_cmp_cached_50))
            # 15m & 1d down move, 1h high
            & ((_cmp_cached_5) | (_cmp_cached_153) | (_cmp_cached_37))
            # 15m & 1d down move, 4h still high
            & ((_cmp_cached_5) | (_cmp_cached_153) | (_cmp_cached_165))
            # 15m & 4h down move, 15m high
            & ((_cmp_cached_5) | (_cmp_cached_181) | (_cmp_cached_76))
            # 15m down move, 15m high, 1d high
            & ((_cmp_cached_5) | (_cmp_cached_210) | (_cmp_cached_27))
            # 15m down move, 1h & 1d high
            & ((_cmp_cached_5) | (_cmp_cached_78) | (_cmp_cached_27))
            # 15m down move, 4h high, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_17) | (_cmp_cached_48))
            # 15m down move, 1h still high, 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_59) | (_cmp_cached_57))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_84) | (_cmp_cached_21) | (_cmp_cached_78))
            # 1h & 1d down move, 1d still high
            & ((_cmp_cached_13) | (_cmp_cached_121) | (_cmp_cached_56))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_7) | (_cmp_cached_55) | (_cmp_cached_102))
            # 1h & 4h down move, 1d still high
            & ((_cmp_cached_7) | (_cmp_cached_58) | (_cmp_cached_238))
            # 1h & 4h & 1d down move
            & ((_cmp_cached_7) | (_cmp_cached_58) | (_cmp_cached_104))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_7) | (_cmp_cached_25) | (_cmp_cached_98))
            # 1h down move, 4h & 1d downtrend
            & ((_cmp_cached_7) | (_cmp_cached_93) | (_cmp_cached_57))
            # 1h & 4h down move, 1d still not low enough
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_265))
            # 1h & 4h down move, 15m still not low enough
            & ((_cmp_cached_15) | (_cmp_cached_151) | (_cmp_cached_152))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_15) | (_cmp_cached_25) | (_cmp_cached_40))
            # 1h down move, 1h still not low enough, 1d overbought
            & ((_cmp_cached_15) | (_cmp_cached_161) | (_cmp_cached_107))
            # 1h down move, 1h still high, 1d downtrend
            & ((_cmp_cached_15) | (_cmp_cached_28) | (_cmp_cached_57))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_15) | (_cmp_cached_39) | (_cmp_cached_52))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_30) | (_cmp_cached_100) | (_cmp_cached_24))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_30) | (_cmp_cached_16) | (_cmp_cached_108))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_30) | (_cmp_cached_21) | (_cmp_cached_17))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_30) | (_cmp_cached_99) | (_cmp_cached_6))
            # 1h & 1d down move, 1d overbought
            & ((_cmp_cached_30) | (_cmp_cached_125) | (_cmp_cached_70))
            # 1h down move, 1d high, 1d downtrend
            & ((_cmp_cached_30) | (_cmp_cached_106) | (_cmp_cached_57))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_11) | (_cmp_cached_33) | (_cmp_cached_6))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_20) | (_cmp_cached_70))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_32) | (_cmp_cached_41) | (_cmp_cached_123))
            # 1h down move, 15m still high, 1h high
            & ((_cmp_cached_32) | (_cmp_cached_62) | (_cmp_cached_45))
            # 1h & 1d down move, 1h high
            & ((_cmp_cached_38) | (_cmp_cached_198) | (_cmp_cached_33))
            # 4h & 1d down move, 15m still not low enough
            & ((_cmp_cached_151) | (_cmp_cached_29) | (_cmp_cached_166))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_151) | (_cmp_cached_121) | (_cmp_cached_106))
            # 4h & 1d down move, 1d downtrend
            & ((_cmp_cached_55) | (_cmp_cached_101) | (_cmp_cached_102))
            # 4h & 1d down move, 1h still high
            & ((_cmp_cached_55) | (_cmp_cached_153) | (_cmp_cached_59))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_55) | (_cmp_cached_165) | (_cmp_cached_57))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_58) | (_cmp_cached_29) | (_cmp_cached_106))
            # 4h & 1d down move, 15m still high
            & ((_cmp_cached_58) | (_cmp_cached_104) | (_cmp_cached_155))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_58) | (_cmp_cached_27) | (_cmp_cached_95))
            # 4h down move, 1h high, 1d downtrend
            & ((_cmp_cached_58) | (_cmp_cached_59) | (_cmp_cached_102))
            # 4h down move, 4h & 1d downtrend
            & ((_cmp_cached_58) | (_cmp_cached_69) | (_cmp_cached_65))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_25) | (_cmp_cached_104) | (_cmp_cached_199))
            # 4h & 1d down move, 4h high
            & ((_cmp_cached_25) | (_cmp_cached_178) | (_cmp_cached_162))
            # 4h down move, 1d still high, 4h still not low enough
            & ((_cmp_cached_25) | (_cmp_cached_176) | (_cmp_cached_124))
            # 1h down move, 1h still high, 1d downtrend
            & ((_cmp_cached_15) | (_cmp_cached_26) | (_cmp_cached_102))
            # 4h down move, 4h & 1d high
            & ((_cmp_cached_25) | (_cmp_cached_17) | (_cmp_cached_106))
            # 4h down move, 1h still not low enough, 1d downtrend
            & ((_cmp_cached_25) | (_cmp_cached_190) | (_cmp_cached_57))
            # 4h down move, 1h high
            & ((_cmp_cached_25) | (_cmp_cached_19))
            # 4h down move, 1h downtrend, 1d overbought
            & ((_cmp_cached_25) | (_cmp_cached_132) | (_cmp_cached_111))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_100) | (_cmp_cached_104) | (_cmp_cached_238))
            # 4h down move, 4h & 1d high
            & ((_cmp_cached_100) | (_cmp_cached_17) | (_cmp_cached_106))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_100) | (_cmp_cached_108) | (_cmp_cached_216))
            # 4h down move, 4h high, 1d downtrend
            & ((_cmp_cached_100) | (_cmp_cached_162) | (_cmp_cached_57))
            # 4h & 1d down move, 1d overbought
            & ((_cmp_cached_16) | (_cmp_cached_125) | (_cmp_cached_70))
            # 4h down move, 1h high, 1d downtrend
            & ((_cmp_cached_16) | (_cmp_cached_123) | (_cmp_cached_57))
            # 4h down move, 15m still high, 1h high
            & ((_cmp_cached_21) | (_cmp_cached_62) | (_cmp_cached_80))
            # 4h down move, 1h high
            & ((_cmp_cached_181) | (_cmp_cached_33))
            # 4h down move, 4h high, 1d downtrend
            & ((_cmp_cached_91) | (_cmp_cached_12) | (_cmp_cached_57))
            # 1h high, 4h & 1d overbought
            & ((_cmp_cached_24) | (_cmp_cached_113) | (_cmp_cached_63))
            # 1h & 4h high, 1d overbought
            & ((_cmp_cached_45) | (_cmp_cached_6) | (_cmp_cached_52))
            # 1d high, 4h & 1d downtrend
            & ((_cmp_cached_199) | (_cmp_cached_69) | (_cmp_cached_102))
            # 4h high, 4h & 1d overbought
            & ((_cmp_cached_72) | (_cmp_cached_20) | (_cmp_cached_167))
          )

          # Logic
          long_entry_logic.append(
            (_cmp_cached_287)
            & (_cmp_cached_237)
            & (df["EMA_26"] > df["EMA_12"])
            & ((df["EMA_26"] - df["EMA_12"]) > (df["open"] * 0.020))
            & ((df["EMA_26"].shift() - df["EMA_12"].shift()) > (df["open"] / 100.0))
          )

        # Condition #144 - Top Coins mode (Long).
        if long_entry_condition_index == 144:
          # Protections
          long_entry_logic.append(is_pair_long_top_coins_mode)
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          long_entry_logic.append(df["protections_long_global"] == True)

          long_entry_logic.append(
            # 5m & 1h down move, 1h still not low enough
            ((_cmp_cached_0) | (_cmp_cached_9) | (_cmp_cached_150))
            # 5m & 4h down move, 15m still high
            & ((_cmp_cached_0) | (_cmp_cached_55) | (_cmp_cached_31))
            # 5m & 4h & 1d down move
            & ((_cmp_cached_0) | (_cmp_cached_58) | (_cmp_cached_153))
            # 5m & 4h down move, 1d downtrend
            & ((_cmp_cached_0) | (_cmp_cached_58) | (_cmp_cached_186))
            # 5m & 4h down move, 15m high
            & ((_cmp_cached_157) | (_cmp_cached_58) | (_cmp_cached_31))
            # 15m & 1h down move, 1h still not low enough
            & ((_cmp_cached_1) | (_cmp_cached_13) | (_cmp_cached_160))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_3) | (_cmp_cached_7) | (_cmp_cached_106))
            # 15m & 1h down move, 1d high
            & ((_cmp_cached_3) | (_cmp_cached_9) | (_cmp_cached_27))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_3) | (_cmp_cached_32) | (_cmp_cached_70))
            # 15m & 4h down move, 4h downtrend
            & ((_cmp_cached_3) | (_cmp_cached_55) | (_cmp_cached_69))
            # 15m & 4h down move, 4h still high
            & ((_cmp_cached_3) | (_cmp_cached_41) | (_cmp_cached_165))
            # 15m down move, 1d high & overbought
            & ((_cmp_cached_3) | (_cmp_cached_27) | (_cmp_cached_52))
            # 15m & 4h down move, 4h still not low enough
            & ((_cmp_cached_5) | (_cmp_cached_58) | (_cmp_cached_336))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_91) | (_cmp_cached_17))
            # 15m down move, 4h high, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_77) | (_cmp_cached_107))
            # 15m & 1h down move, 15m still high
            & ((_cmp_cached_84) | (_cmp_cached_15) | (_cmp_cached_61))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_84) | (_cmp_cached_30) | (_cmp_cached_70))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_84) | (_cmp_cached_34) | (_cmp_cached_6))
            # 15m & 4h down move, 15m still high
            & ((_cmp_cached_84) | (_cmp_cached_25) | (_cmp_cached_31))
            # 15m down move, 4h & 1d overbought
            & ((_cmp_cached_84) | (_cmp_cached_20) | (_cmp_cached_111))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_88) | (_cmp_cached_32) | (_cmp_cached_6))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_88) | (_cmp_cached_36) | (_cmp_cached_72))
            # 15m down move, 4h high, 1d downtrend
            & ((_cmp_cached_88) | (_cmp_cached_12) | (_cmp_cached_102))
            # 15m & 1h down move, 15m high
            & ((_cmp_cached_245) | (_cmp_cached_38) | (_cmp_cached_92))
            # 15m down move, 4h high, 1d overbought
            & ((_cmp_cached_5) | (_cmp_cached_17) | (_cmp_cached_48))
            # 15m & 4h down move, 1d downtrend
            & ((_cmp_cached_84) | (_cmp_cached_25) | (_cmp_cached_57))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_84) | (_cmp_cached_32) | (_cmp_cached_12))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_87) | (_cmp_cached_6) | (_cmp_cached_51))
            # 15m down move, 15m still high, 4h high
            & ((_cmp_cached_88) | (_cmp_cached_62) | (_cmp_cached_77))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_88) | (_cmp_cached_12) | (_cmp_cached_20))
            # 15m down move, 4h high, 1d downtrend
            & ((_cmp_cached_88) | (_cmp_cached_72) | (_cmp_cached_102))
            # 15m down move, 1h & 4h overbought
            & ((_cmp_cached_88) | (_cmp_cached_82) | (_cmp_cached_51))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_89) | (_cmp_cached_33) | (_cmp_cached_6))
            # 15m down move, 15m & 4h high
            & ((_cmp_cached_184) | (_cmp_cached_76) | (_cmp_cached_46))
            # 1h & 4h down move, 1h downtrend
            & ((_cmp_cached_13) | (_cmp_cached_58) | (_cmp_cached_306))
            # 1h & 4h down move, 1d still high
            & ((_cmp_cached_13) | (_cmp_cached_58) | (_cmp_cached_56))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_13) | (_cmp_cached_100) | (_cmp_cached_165))
            # 1h & 4h down move, 15m still high
            & ((_cmp_cached_13) | (_cmp_cached_41) | (_cmp_cached_61))
            # 1h & 4h down move, 15m still not low enough
            & ((_cmp_cached_7) | (_cmp_cached_55) | (_cmp_cached_171))
            # 1h & 4h down move, 1d still high
            & ((_cmp_cached_7) | (_cmp_cached_100) | (_cmp_cached_238))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_7) | (_cmp_cached_181) | (_cmp_cached_124))
            # 1h & 1d down move, 1h still high
            & ((_cmp_cached_7) | (_cmp_cached_101) | (_cmp_cached_110))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_7) | (_cmp_cached_94) | (_cmp_cached_167))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_9) | (_cmp_cached_25) | (_cmp_cached_124))
            # 1h & 4h down move, 15m still high
            & ((_cmp_cached_9) | (_cmp_cached_25) | (_cmp_cached_61))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_9) | (_cmp_cached_25) | (_cmp_cached_57))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_9) | (_cmp_cached_16) | (_cmp_cached_35))
            # 1h & 1d down move, 4h high
            & ((_cmp_cached_9) | (_cmp_cached_153) | (_cmp_cached_64))
            # 1h & 1d down move, 1d high
            & ((_cmp_cached_9) | (_cmp_cached_104) | (_cmp_cached_106))
            # 1h down move, 1d high, 1h downtrend
            & ((_cmp_cached_9) | (_cmp_cached_106) | (_cmp_cached_132))
            # 1h & 4h down move, 15m still not low enough
            & ((_cmp_cached_15) | (_cmp_cached_151) | (_cmp_cached_152))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_15) | (_cmp_cached_16) | (_cmp_cached_24))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_15) | (_cmp_cached_41) | (_cmp_cached_17))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_15) | (_cmp_cached_91) | (_cmp_cached_65))
            # 1h & 1d down move, 1d high
            & ((_cmp_cached_15) | (_cmp_cached_121) | (_cmp_cached_108))
            # 1h down move, 4h still high, 1d overbought
            & ((_cmp_cached_15) | (_cmp_cached_122) | (_cmp_cached_52))
            # 1h down move, 1d high, 4h downtrend
            & ((_cmp_cached_15) | (_cmp_cached_106) | (_cmp_cached_69))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_15) | (_cmp_cached_108) | (_cmp_cached_95))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_15) | (_cmp_cached_12) | (_cmp_cached_20))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_15) | (_cmp_cached_12) | (_cmp_cached_102))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_30) | (_cmp_cached_100) | (_cmp_cached_96))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_30) | (_cmp_cached_16) | (_cmp_cached_27))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_30) | (_cmp_cached_21) | (_cmp_cached_77))
            # 1h & 4h down move, 4h overbought
            & ((_cmp_cached_30) | (_cmp_cached_21) | (_cmp_cached_50))
            # 1h & 1d down move, 1h still high
            & ((_cmp_cached_30) | (_cmp_cached_121) | (_cmp_cached_26))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_30) | (_cmp_cached_77) | (_cmp_cached_217))
            # 1h down move, 1h high, 1h still not low enough
            & ((_cmp_cached_30) | (_cmp_cached_108) | (_cmp_cached_190))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_30) | (_cmp_cached_27) | (_cmp_cached_167))
            # 1h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_30) | (_cmp_cached_165) | (_cmp_cached_65))
            # 1h & 4h down move, 15m high
            & ((_cmp_cached_11) | (_cmp_cached_16) | (_cmp_cached_92))
            # 1h & 4h down move, 4h still not low enough
            & ((_cmp_cached_11) | (_cmp_cached_16) | (_cmp_cached_124))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_16) | (_cmp_cached_48))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_11) | (_cmp_cached_41) | (_cmp_cached_40))
            # 1h & 1d down move, 1d high
            & ((_cmp_cached_11) | (_cmp_cached_121) | (_cmp_cached_106))
            # 1h down move, 4h & 1d high
            & ((_cmp_cached_11) | (_cmp_cached_17) | (_cmp_cached_27))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_32) | (_cmp_cached_21) | (_cmp_cached_250))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_32) | (_cmp_cached_24) | (_cmp_cached_6))
            # 1h down move, 1h high, 4h high
            & ((_cmp_cached_32) | (_cmp_cached_33) | (_cmp_cached_12))
            # 1h down move, 4h high, 1h overbought
            & ((_cmp_cached_36) | (_cmp_cached_77) | (_cmp_cached_82))
            # 1h down move, 1h high, 15m high
            & ((_cmp_cached_117) | (_cmp_cached_24) | (_cmp_cached_92))
            # 4h & 1d down move, 15m still not low enough
            & ((_cmp_cached_151) | (_cmp_cached_29) | (_cmp_cached_166))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_151) | (_cmp_cached_104) | (_cmp_cached_56))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_151) | (_cmp_cached_121) | (_cmp_cached_106))
            # 4h down move, 15m high
            & ((_cmp_cached_151) | (_cmp_cached_222))
            # 4h down move, 15m still high, 4h still not low enough
            & ((_cmp_cached_55) | (_cmp_cached_61) | (_cmp_cached_98))
            # 4h & 1d down move, 15m still high
            & ((_cmp_cached_58) | (_cmp_cached_29) | (_cmp_cached_155))
            # 4h down move, 4h still not low enough, 1d downtrend
            & ((_cmp_cached_58) | (_cmp_cached_120) | (_cmp_cached_186))
            # 4h down move, 4h still high, 4h downtrend
            & ((_cmp_cached_58) | (_cmp_cached_96) | (_cmp_cached_69))
            # 4h down move, 1d still high, 1d downtrend
            & ((_cmp_cached_58) | (_cmp_cached_119) | (_cmp_cached_102))
            # 4h down move, 1d high, 15m high
            & ((_cmp_cached_58) | (_cmp_cached_108) | (_cmp_cached_222))
            # 4h down move, 1d high, 4h downtrend
            & ((_cmp_cached_58) | (_cmp_cached_27) | (_cmp_cached_93))
            # 4h down move, 4h & 1d downtrend
            & ((_cmp_cached_58) | (_cmp_cached_93) | (_cmp_cached_57))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_25) | (_cmp_cached_29) | (_cmp_cached_238))
            # 4h & 1d down move, 4h still high
            & ((_cmp_cached_25) | (_cmp_cached_178) | (_cmp_cached_35))
            # 4h & 1d down move, 4h still high
            & ((_cmp_cached_25) | (_cmp_cached_198) | (_cmp_cached_165))
            # 4h down move, 4h still not low enough, 1d high
            & ((_cmp_cached_25) | (_cmp_cached_98) | (_cmp_cached_106))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_25) | (_cmp_cached_27) | (_cmp_cached_70))
            # 4h down move, 15m high
            & ((_cmp_cached_25) | (_cmp_cached_92))
            # 4h & 1d down move, 1d downtrend
            & ((_cmp_cached_100) | (_cmp_cached_121) | (_cmp_cached_102))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_100) | (_cmp_cached_108) | (_cmp_cached_216))
            # 4h & 1d down move, 4h overbought
            & ((_cmp_cached_16) | (_cmp_cached_198) | (_cmp_cached_334))
            # 4h & 1d down move, 1d overbought
            & ((_cmp_cached_16) | (_cmp_cached_198) | (_cmp_cached_95))
            # 4h & 1d down move, 1d overbought
            & ((_cmp_cached_41) | (_cmp_cached_337) | (_cmp_cached_167))
            # 4h down move, 4h high, 1d high
            & ((_cmp_cached_41) | (_cmp_cached_17) | (_cmp_cached_74))
            # 4h down move, 1d stil high, 1d downtrend
            & ((_cmp_cached_41) | (_cmp_cached_119) | (_cmp_cached_102))
            # 4h down move, 4h still high, 4h downtrend
            & ((_cmp_cached_41) | (_cmp_cached_165) | (_cmp_cached_219))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_21) | (_cmp_cached_165) | (_cmp_cached_57))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_175) | (_cmp_cached_39) | (_cmp_cached_48))
            # 1d down move, 4h still not low enough, 4h downtrend
            & ((_cmp_cached_153) | (_cmp_cached_124) | (_cmp_cached_219))
            # 1d down move, 4h & 1d downtrend
            & ((_cmp_cached_153) | (_cmp_cached_69) | (_cmp_cached_57))
            # 1d down move, 1d high, 4h downtrend
            & ((_cmp_cached_29) | (_cmp_cached_106) | (_cmp_cached_69))
            # 1d down move, 1h & 4h high
            & ((_cmp_cached_121) | (_cmp_cached_24) | (_cmp_cached_6))
            # 1d down move, 1h & 4h high
            & ((_cmp_cached_178) | (_cmp_cached_24) | (_cmp_cached_6))
            # 1h high, 4h & 1d overbought
            & ((_cmp_cached_24) | (_cmp_cached_113) | (_cmp_cached_63))
            # 4h & 1d high, 1h overbought
            & ((_cmp_cached_47) | (_cmp_cached_27) | (_cmp_cached_82))
            # 4h high, 4h & 1d overbought
            & ((_cmp_cached_46) | (_cmp_cached_51) | (_cmp_cached_112))
            # 15m high, 4h & 1d overbought
            & ((_cmp_cached_180) | (_cmp_cached_20) | (_cmp_cached_167))
            # 15m still high, 4h & 1d overbought
            & ((_cmp_cached_61) | (_cmp_cached_113) | (_cmp_cached_48))
            # 4h high, 4h & 1d overbought
            & ((_cmp_cached_72) | (_cmp_cached_51) | (_cmp_cached_112))
            # 1d high, 4h & 1d overbought
            & ((_cmp_cached_39) | (_cmp_cached_51) | (_cmp_cached_48))
            # 4h & 1d overbought
            & ((_cmp_cached_196) | (_cmp_cached_111))
            # 1d P&D, 4h overbought
            & ((_cmp_cached_231) | (df["change_pct_1d"].shift(288) < 50.0) | (_cmp_cached_51))
          )

          # Logic
          long_entry_logic.append(
            (_cmp_cached_277)
            & (_cmp_cached_208)
            # & (_cmp_cached_155)
            & (_cmp_cached_28)
            & (_cmp_cached_301)
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
            ((_cmp_cached_0) | (_cmp_cached_151) | (_cmp_cached_57))
            # 5m down move, 15m & 1h high
            & ((_cmp_cached_157) | (_cmp_cached_276) | (_cmp_cached_80))
            # 15m & 1h & 4h down move
            & ((_cmp_cached_1) | (_cmp_cached_13) | (_cmp_cached_55))
            # 15m & 1h down move, 1h downtrend
            & ((_cmp_cached_1) | (_cmp_cached_13) | (_cmp_cached_129))
            # 15m & 1h down move, 1h still not low enough
            & ((_cmp_cached_1) | (_cmp_cached_9) | (_cmp_cached_190))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_3) | (_cmp_cached_9) | (_cmp_cached_17))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_5) | (_cmp_cached_34) | (_cmp_cached_24))
            # 15m & 4h down move, 4h still not low enough
            & ((_cmp_cached_5) | (_cmp_cached_58) | (_cmp_cached_98))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_84) | (_cmp_cached_15) | (_cmp_cached_24))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_84) | (_cmp_cached_36) | (_cmp_cached_78))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_84) | (_cmp_cached_25) | (_cmp_cached_94))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_84) | (_cmp_cached_21) | (_cmp_cached_78))
            # 15m down move, 15m downtrend, 1h high
            & ((_cmp_cached_84) | (_cmp_cached_43) | (_cmp_cached_115))
            # 15m down move, 15m still high, 4h high
            & ((_cmp_cached_84) | (_cmp_cached_31) | (_cmp_cached_162))
            # 15m down move, 1h high, 1d downtrend
            & ((_cmp_cached_84) | (_cmp_cached_78) | (_cmp_cached_102))
            # 15m & 1h down move, 1d downtrend
            & ((_cmp_cached_87) | (_cmp_cached_30) | (_cmp_cached_102))
            # 15m & 4h down move, 15m still high
            & ((_cmp_cached_87) | (_cmp_cached_100) | (_cmp_cached_61))
            # 15m down move, 15m & 1h high
            & ((_cmp_cached_87) | (_cmp_cached_76) | (_cmp_cached_80))
            # 15m & 1h down move, 15m still high
            & ((_cmp_cached_88) | (_cmp_cached_34) | (_cmp_cached_61))
            # 15m down move, 15m still high, 1d overbought
            & ((_cmp_cached_88) | (_cmp_cached_61) | (_cmp_cached_70))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_89) | (_cmp_cached_41) | (_cmp_cached_37))
            # 15m down move, 15m & 4h high
            & ((_cmp_cached_89) | (_cmp_cached_76) | (_cmp_cached_17))
            # 15m down move, 15m high, 1h high
            & ((_cmp_cached_89) | (_cmp_cached_76) | (_cmp_cached_37))
            # 15m down move, 15m high, 4h high
            & ((_cmp_cached_89) | (_cmp_cached_76) | (_cmp_cached_12))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_89) | (_cmp_cached_33) | (_cmp_cached_167))
            # 15m down move, 4h & 1d overbought
            & ((_cmp_cached_184) | (_cmp_cached_51) | (_cmp_cached_63))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_13) | (_cmp_cached_100) | (_cmp_cached_96))
            # 1h down move, 4h still high, 1d high
            & ((_cmp_cached_13) | (_cmp_cached_122) | (_cmp_cached_94))
            # 1h & 1d down move, 1d still high
            & ((_cmp_cached_7) | (_cmp_cached_104) | (_cmp_cached_119))
            # 1h & 1d down move, 1h still not low enough
            & ((_cmp_cached_7) | (_cmp_cached_121) | (_cmp_cached_188))
            # 1h & 4h & 1d down move
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_29))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_96))
            # 1h & 4h down move, 4h downtrend
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_93))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_102))
            # 1h & 4h down move, 15m high
            & ((_cmp_cached_9) | (_cmp_cached_100) | (_cmp_cached_180))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_9) | (_cmp_cached_16) | (_cmp_cached_42))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_9) | (_cmp_cached_21) | (_cmp_cached_46))
            # 1h & 1d down move, 1h still not low enough
            & ((_cmp_cached_9) | (_cmp_cached_104) | (_cmp_cached_150))
            # 1h down move, 15m downtrend, 1d high
            & ((_cmp_cached_9) | (_cmp_cached_43) | (_cmp_cached_106))
            # 1h down move, 4h still high, 1d overbought
            & ((_cmp_cached_9) | (_cmp_cached_96) | (_cmp_cached_52))
            # 1h down move, 1d still high, 1d downtrend
            & ((_cmp_cached_9) | (_cmp_cached_238) | (_cmp_cached_57))
            # 1h & 4h & 1d down move
            & ((_cmp_cached_15) | (_cmp_cached_25) | (_cmp_cached_104))
            # 1h & 4h down move, 15m still not low enough
            & ((_cmp_cached_15) | (_cmp_cached_25) | (_cmp_cached_152))
            # 1h & 4h down move, 15m still high
            & ((_cmp_cached_15) | (_cmp_cached_25) | (_cmp_cached_62))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_15) | (_cmp_cached_16) | (_cmp_cached_40))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_15) | (_cmp_cached_41) | (_cmp_cached_65))
            # 1h down move, 1h still high, 4h high
            & ((_cmp_cached_15) | (_cmp_cached_110) | (_cmp_cached_40))
            # 1h down move, 1h still high, 4h overbought
            & ((_cmp_cached_15) | (_cmp_cached_26) | (_cmp_cached_50))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_15) | (_cmp_cached_115) | (_cmp_cached_102))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_15) | (_cmp_cached_51) | (_cmp_cached_107))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_30) | (_cmp_cached_21) | (_cmp_cached_17))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_30) | (_cmp_cached_91) | (_cmp_cached_12))
            # 1h & 1d down move, 4h still high
            & ((_cmp_cached_30) | (_cmp_cached_104) | (_cmp_cached_35))
            # 1h & 1d down move, 1h still high
            & ((_cmp_cached_30) | (_cmp_cached_121) | (_cmp_cached_26))
            # 1h down move, 15m still high, 1h high
            & ((_cmp_cached_30) | (_cmp_cached_31) | (_cmp_cached_33))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_30) | (_cmp_cached_24) | (_cmp_cached_167))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_30) | (_cmp_cached_77) | (_cmp_cached_83))
            # 1h down move, 1h still not low enough, 1d downtrend
            & ((_cmp_cached_30) | (_cmp_cached_161) | (_cmp_cached_102))
            # 1h & 4h down move, 1h high
            & ((_cmp_cached_11) | (_cmp_cached_21) | (_cmp_cached_24))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_21) | (_cmp_cached_167))
            # 1h down move, 1h still high, 4h high
            & ((_cmp_cached_11) | (_cmp_cached_26) | (_cmp_cached_47))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_33) | (_cmp_cached_70))
            # 1h down move, 1h still high, 4h downtrend
            & ((_cmp_cached_11) | (_cmp_cached_59) | (_cmp_cached_69))
            # 1h down move, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_63))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_32) | (_cmp_cached_24) | (_cmp_cached_52))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_34) | (_cmp_cached_181) | (_cmp_cached_12))
            # 1h down move, 1h still high, 1d overbought
            & ((_cmp_cached_34) | (_cmp_cached_110) | (_cmp_cached_52))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_34) | (_cmp_cached_46) | (_cmp_cached_83))
            # 1h down move, 4h high, 1d downtrend
            & ((_cmp_cached_34) | (_cmp_cached_72) | (_cmp_cached_57))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_36) | (_cmp_cached_24) | (_cmp_cached_102))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_36) | (_cmp_cached_37) | (_cmp_cached_102))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_38) | (_cmp_cached_33) | (_cmp_cached_6))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_117) | (_cmp_cached_33) | (_cmp_cached_50))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_117) | (_cmp_cached_72) | (_cmp_cached_211))
            # 4h down move, 4h & 1d downtrend
            & ((_cmp_cached_55) | (_cmp_cached_219) | (_cmp_cached_57))
            # 4h & 1d down move, 1d still high
            & ((_cmp_cached_58) | (_cmp_cached_178) | (_cmp_cached_14))
            # 4h down move, 4h & 1d high
            & ((_cmp_cached_58) | (_cmp_cached_40) | (_cmp_cached_106))
            # 4h down move, 1d still high, 1d downtrend
            & ((_cmp_cached_58) | (_cmp_cached_238) | (_cmp_cached_102))
            # 4h down move, 15m & 1h still not low enough
            & (
              (_cmp_cached_58) | (_cmp_cached_152) | (_cmp_cached_161)
            )
            # 4h down move, 15m stil high, 4h downtrend
            & ((_cmp_cached_58) | (_cmp_cached_61) | (_cmp_cached_69))
            # 4h & 1d down move, 1d downtrend
            & ((_cmp_cached_25) | (_cmp_cached_121) | (_cmp_cached_102))
            # 4h & 1d down move, 1h still high
            & ((_cmp_cached_25) | (_cmp_cached_178) | (_cmp_cached_59))
            # 4h & 1d down move, 4h high
            & ((_cmp_cached_25) | (_cmp_cached_192) | (_cmp_cached_64))
            # 4h down move, 4h high
            & ((_cmp_cached_25) | (_cmp_cached_162))
            # 4h down move, 4h & 1d high
            & ((_cmp_cached_100) | (_cmp_cached_17) | (_cmp_cached_106))
            # 4h down move, 15m high
            & ((_cmp_cached_100) | (_cmp_cached_227))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_100) | (_cmp_cached_94) | (_cmp_cached_70))
            # 4h & 1d down move, 1d overbought
            & ((_cmp_cached_16) | (_cmp_cached_125) | (_cmp_cached_95))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_16) | (_cmp_cached_198) | (_cmp_cached_108))
            # 4h down move, 15m high, 1d overbought
            & ((_cmp_cached_41) | (_cmp_cached_227) | (_cmp_cached_95))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_21) | (_cmp_cached_165) | (_cmp_cached_102))
            # 4h down move, 4h high, 1d overbought
            & ((_cmp_cached_181) | (_cmp_cached_40) | (_cmp_cached_52))
            # 4h & 1d down move, 1h high
            & ((_cmp_cached_91) | (_cmp_cached_198) | (_cmp_cached_37))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_175) | (_cmp_cached_39) | (_cmp_cached_63))
            # 1d down move, 1d high, 1d downtrend
            & ((_cmp_cached_29) | (_cmp_cached_106) | (_cmp_cached_57))
            # 1d down move, 1h high
            & ((_cmp_cached_104) | (_cmp_cached_37))
            # 1d down move, 1h high, 1d downtrend
            & ((_cmp_cached_121) | (_cmp_cached_123) | (_cmp_cached_102))
            # 1d down move, 1d high, 4h downtrend
            & ((_cmp_cached_192) | (_cmp_cached_106) | (_cmp_cached_93))
            # 1d down move, 4h high, 1d overbought
            & ((_cmp_cached_126) | (_cmp_cached_17) | (_cmp_cached_52))
            # 15m high, 1d high & overbought
            & ((_cmp_cached_76) | (_cmp_cached_27) | (_cmp_cached_48))
            # 15m high, 4h overbought, 1d downtrend
            & ((_cmp_cached_18) | (_cmp_cached_20) | (_cmp_cached_102))
            # 1h & 4h high, 4h overbought
            & ((_cmp_cached_24) | (_cmp_cached_6) | (_cmp_cached_50))
            # 1h high, 1d overbought
            & ((_cmp_cached_45) | (_cmp_cached_63))
            # 1h high, 4h & 1d downtrend
            & ((_cmp_cached_80) | (_cmp_cached_93) | (_cmp_cached_195))
            # 4h & 1d high, 1d overbought
            & ((_cmp_cached_6) | (_cmp_cached_27) | (_cmp_cached_112))
            # 1h high, 4h & 1d downtrend
            & ((_cmp_cached_19) | (_cmp_cached_93) | (_cmp_cached_195))
          )

          # Logic
          long_entry_logic.append(
            (_cmp_cached_271)
            & (df["BBD_40_2.0"].gt(df["close"] * 0.020))
            & (df["close_delta"].gt(df["close"] * 0.02))
            & (df["BBT_40_2.0"].lt(df["BBD_40_2.0"] * 0.3))
            & (df["close"].lt(df["BBL_40_2.0"].shift()))
            & (df["close"].le(df["close"].shift()))
          )

        # Condition #161 - Scalp mode (Long).
        if long_entry_condition_index == 161:
          # Protections
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          long_entry_logic.append(df["protections_long_global"] == True)

          # 5m down move, 15m high
          long_entry_logic.append((_cmp_cached_209) | (_cmp_cached_18))
          # 15m & 1h down move, 4h high
          long_entry_logic.append((_cmp_cached_88) | (_cmp_cached_34) | (_cmp_cached_17))
          # 15m & 4h down move, 4h still high
          long_entry_logic.append((_cmp_cached_88) | (_cmp_cached_99) | (_cmp_cached_122))
          # 15m down move, 15m high
          long_entry_logic.append((_cmp_cached_88) | (_cmp_cached_18))
          # 15m down move, 4h still high, 1d high
          long_entry_logic.append(
            (_cmp_cached_88) | (_cmp_cached_35) | (_cmp_cached_94)
          )
          # 15m & 1h down move, 15m still high
          long_entry_logic.append((_cmp_cached_89) | (_cmp_cached_53) | (_cmp_cached_62))
          # 15m down move, 15m & 4h still high
          long_entry_logic.append(
            (_cmp_cached_89) | (_cmp_cached_61) | (_cmp_cached_35)
          )
          # 15m & 4h down move, 4h high
          long_entry_logic.append((_cmp_cached_184) | (_cmp_cached_71) | (_cmp_cached_77))
          # 15m & 1h down move, 1h high
          long_entry_logic.append((_cmp_cached_90) | (_cmp_cached_36) | (_cmp_cached_24))
          # 15m & 1h down move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_90) | (_cmp_cached_36) | (_cmp_cached_59)
          )
          # 15m & 1h down move, 4h high
          long_entry_logic.append((_cmp_cached_90) | (_cmp_cached_53) | (_cmp_cached_77))
          # 15m & 4h down move, 15m high
          long_entry_logic.append(
            (_cmp_cached_90) | (_cmp_cached_181) | (_cmp_cached_61)
          )
          # 15m & 4h down move, 15m high
          long_entry_logic.append(
            (_cmp_cached_90) | (_cmp_cached_71) | (_cmp_cached_92)
          )
          # 15m down move, 15m & 1h still high
          long_entry_logic.append(
            (_cmp_cached_90) | (_cmp_cached_62) | (_cmp_cached_59)
          )
          # 15m down move, 15m & 1h still high
          long_entry_logic.append(
            (_cmp_cached_90) | (_cmp_cached_61) | (_cmp_cached_59)
          )
          # 15m down move, 4h still high, 1d overbought
          long_entry_logic.append((_cmp_cached_90) | (_cmp_cached_122) | (_cmp_cached_48))
          # 15m & 1h down move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_245) | (_cmp_cached_38) | (_cmp_cached_28)
          )
          # 15m down move, 15m high, 1d overbought
          long_entry_logic.append((_cmp_cached_245) | (_cmp_cached_210) | (_cmp_cached_107))
          # 15m down move, 15m high, 4h still high
          long_entry_logic.append(
            (_cmp_cached_245) | (_cmp_cached_76) | (_cmp_cached_35)
          )
          # 15m down move, 15m still not low enough, 4h still high
          long_entry_logic.append(
            (_cmp_cached_245) | (_cmp_cached_152) | (_cmp_cached_35)
          )
          # 15m down move, 15m & 1h still high
          long_entry_logic.append(
            (_cmp_cached_245) | (_cmp_cached_338) | (_cmp_cached_28)
          )
          # 15m down move, 15m still not low enough, 4h high
          long_entry_logic.append(
            (_cmp_cached_249) | (_cmp_cached_152) | (_cmp_cached_72)
          )
          # 15m down move, 15m still high, 1d overbought
          long_entry_logic.append((_cmp_cached_249) | (_cmp_cached_62) | (_cmp_cached_107))
          # 15m down move, 15m still high, 1h high
          long_entry_logic.append(
            (_cmp_cached_339) | (_cmp_cached_155) | (_cmp_cached_37)
          )
          # 15m down move, 15m still high, 4h high
          long_entry_logic.append(
            (_cmp_cached_339) | (_cmp_cached_61) | (_cmp_cached_47)
          )
          # 15m down move, 15m & 1h still high
          long_entry_logic.append(
            (_cmp_cached_339) | (_cmp_cached_61) | (_cmp_cached_59)
          )
          # 1h down move, 4h still high, 1d high
          long_entry_logic.append(
            (_cmp_cached_11) | (_cmp_cached_122) | (_cmp_cached_39)
          )
          # 1h & 4h down move, 1h still high
          long_entry_logic.append((_cmp_cached_32) | (_cmp_cached_197) | (_cmp_cached_26))
          long_entry_logic.append(
            (_cmp_cached_32) | (_cmp_cached_28) | (_cmp_cached_39)
          )
          # 1h & 4h down move, 4h still high
          long_entry_logic.append(
            (_cmp_cached_34) | (_cmp_cached_175) | (_cmp_cached_35)
          )
          # 1h & 4h down move, 4h high
          long_entry_logic.append(
            (_cmp_cached_34) | (_cmp_cached_71) | (_cmp_cached_12)
          )
          # 1h down move, 15m & 1h still high
          long_entry_logic.append(
            (_cmp_cached_36) | (_cmp_cached_61) | (_cmp_cached_59)
          )
          # 1h down move, 1h still high, 4h high
          long_entry_logic.append(
            (_cmp_cached_36) | (_cmp_cached_59) | (_cmp_cached_64)
          )
          # 1h down move, 1h high
          long_entry_logic.append((_cmp_cached_36) | (_cmp_cached_123))
          # 1h down move, 4h & 1d high
          long_entry_logic.append((_cmp_cached_36) | (_cmp_cached_47) | (_cmp_cached_94))
          # 1h down move, 1h still high, 4h high
          long_entry_logic.append((_cmp_cached_38) | (_cmp_cached_26) | (_cmp_cached_46))
          # 1h down move, 1h still high, 1d high
          long_entry_logic.append((_cmp_cached_38) | (_cmp_cached_26) | (_cmp_cached_94))
          # 1h down move, 1h high
          long_entry_logic.append((_cmp_cached_38) | (_cmp_cached_123))
          # 1h & 4h down move, 15m high
          long_entry_logic.append((_cmp_cached_117) | (_cmp_cached_71) | (_cmp_cached_76))
          # 1h down move, 15m still high, 4h high
          long_entry_logic.append((_cmp_cached_117) | (_cmp_cached_62) | (_cmp_cached_77))
          # 1h down move, 15m high, 1h still high
          long_entry_logic.append(
            (_cmp_cached_117) | (_cmp_cached_76) | (_cmp_cached_28)
          )
          # 1h down move, 15m still high, 4h high
          long_entry_logic.append(
            (_cmp_cached_117) | (_cmp_cached_61) | (_cmp_cached_12)
          )
          # 1h down move, 15m & 1h high
          long_entry_logic.append(
            (_cmp_cached_117) | (_cmp_cached_222) | (_cmp_cached_115)
          )
          # 1h down move, 1h & 1d high
          long_entry_logic.append(
            (_cmp_cached_117) | (_cmp_cached_24) | (_cmp_cached_74)
          )
          # 1h down move, 4h still high, 1d high
          long_entry_logic.append(
            (_cmp_cached_117) | (_cmp_cached_35) | (_cmp_cached_39)
          )
          # 1h down move, 1h still high, 1d high
          long_entry_logic.append((_cmp_cached_117) | (_cmp_cached_26) | (_cmp_cached_94))
          # 1h down move, 4h overbought
          long_entry_logic.append((_cmp_cached_117) | (_cmp_cached_113))
          # 1h down move, 1h & 4h high
          long_entry_logic.append((_cmp_cached_174) | (_cmp_cached_24) | (_cmp_cached_6))
          # 1h down move, 5m up move, 1h still high
          long_entry_logic.append(
            (_cmp_cached_53) | (_cmp_cached_340) | (_cmp_cached_59)
          )
          # 1h down move, 15m still not low enough, 4h high
          long_entry_logic.append(
            (_cmp_cached_53) | (_cmp_cached_76) | (_cmp_cached_72)
          )
          # 1h down move, 15m still not low enough, 1h high
          long_entry_logic.append(
            (_cmp_cached_53) | (_cmp_cached_152) | (_cmp_cached_24)
          )
          # 1h down move, 15m still not low enough, 1h high
          long_entry_logic.append(
            (_cmp_cached_53) | (_cmp_cached_152) | (_cmp_cached_123)
          )
          # 1h down move, 15m & 4h still high
          long_entry_logic.append(
            (_cmp_cached_53) | (_cmp_cached_61) | (_cmp_cached_35)
          )
          # 1h down move, 15m & 1h high
          long_entry_logic.append((_cmp_cached_53) | (_cmp_cached_76) | (_cmp_cached_78))
          # 1h down move, 1h still high, 4h high
          long_entry_logic.append(
            (_cmp_cached_53) | (_cmp_cached_26) | (_cmp_cached_72)
          )
          # 1h down move, 1h high, 4h still high
          long_entry_logic.append((_cmp_cached_53) | (_cmp_cached_33) | (_cmp_cached_96))
          # 1h down move, 1h still high, 4h high
          long_entry_logic.append(
            (_cmp_cached_53) | (_cmp_cached_28) | (_cmp_cached_17)
          )
          # 1h down move, 1h & 1d high
          long_entry_logic.append(
            (_cmp_cached_53) | (_cmp_cached_37) | (_cmp_cached_94)
          )
          # 1h down move, 4h & 1d high
          long_entry_logic.append((_cmp_cached_53) | (_cmp_cached_341) | (_cmp_cached_250))
          # 15m & 1h & 4h down move, 4h high
          long_entry_logic.append(
            (_cmp_cached_249) | (_cmp_cached_221) | (_cmp_cached_197) | (_cmp_cached_47)
          )
          # 4h down move, 15m high
          long_entry_logic.append((_cmp_cached_100) | (_cmp_cached_18))
          # 4h down move, 1h high
          long_entry_logic.append((_cmp_cached_16) | (_cmp_cached_19))
          # 4h down move, 15m & 4h still high
          long_entry_logic.append((_cmp_cached_41) | (_cmp_cached_62) | (_cmp_cached_122))
          # 4h down move, 15m still high, 1d overbought
          long_entry_logic.append(
            (_cmp_cached_41) | (_cmp_cached_61) | (_cmp_cached_95)
          )
          # 4h down move, 1h & 4h still high
          long_entry_logic.append(
            (_cmp_cached_21) | (_cmp_cached_59) | (_cmp_cached_122)
          )
          # 4h down move, 1d high & overbought
          long_entry_logic.append(
            (_cmp_cached_21) | (_cmp_cached_74) | (_cmp_cached_52)
          )
          # 4h down move, 15m & 1h high
          long_entry_logic.append(
            (_cmp_cached_181) | (_cmp_cached_18) | (_cmp_cached_37)
          )
          # 4h down move, 1d high & overbought
          long_entry_logic.append((_cmp_cached_181) | (_cmp_cached_108) | (_cmp_cached_167))
          # 4h down move, 15m still high, 1h high
          long_entry_logic.append(
            (_cmp_cached_181) | (_cmp_cached_155) | (_cmp_cached_19)
          )
          # 4h down move, 1h & 4h still high
          long_entry_logic.append(
            (_cmp_cached_181) | (_cmp_cached_59) | (_cmp_cached_173)
          )
          # 4h down move, 1h still high, 4h still moving down
          long_entry_logic.append(
            (_cmp_cached_181) | (_cmp_cached_59) | (_cmp_cached_342)
          )
          # 4h down move, 1d high & overbought
          long_entry_logic.append(
            (_cmp_cached_181) | (_cmp_cached_74) | (_cmp_cached_95)
          )
          # 4h down move, 1h high, 4h still high
          long_entry_logic.append((_cmp_cached_91) | (_cmp_cached_24) | (_cmp_cached_122))
          # 4h down move, 15m high, 4h still high
          long_entry_logic.append(
            (_cmp_cached_99) | (_cmp_cached_76) | (_cmp_cached_165)
          )
          # 4h down move, 15m still high, 1h high
          long_entry_logic.append(
            (_cmp_cached_99) | (_cmp_cached_155) | (_cmp_cached_37)
          )
          # 4h down move, 15m & 4h still high
          long_entry_logic.append(
            (_cmp_cached_99) | (_cmp_cached_61) | (_cmp_cached_122)
          )
          # 4h down move, 15m high, 4h still not low enough
          long_entry_logic.append(
            (_cmp_cached_99) | (_cmp_cached_92) | (_cmp_cached_124)
          )
          # 4h down move, 1h still high, 4h high
          long_entry_logic.append(
            (_cmp_cached_99) | (_cmp_cached_59) | (_cmp_cached_17)
          )
          # 4h down move, 15m & 1d high
          long_entry_logic.append((_cmp_cached_99) | (_cmp_cached_76) | (_cmp_cached_94))
          # 4h down move, 1d high & overbought
          long_entry_logic.append((_cmp_cached_99) | (_cmp_cached_94) | (_cmp_cached_167))
          # 4h down move, 15m & 4h high
          long_entry_logic.append((_cmp_cached_71) | (_cmp_cached_76) | (_cmp_cached_17))
          # 4h down move, 15m high, 4h still high
          long_entry_logic.append((_cmp_cached_71) | (_cmp_cached_18) | (_cmp_cached_96))
          # 4h down move, 15m still high, 1h high
          long_entry_logic.append(
            (_cmp_cached_71) | (_cmp_cached_61) | (_cmp_cached_24)
          )
          # 4h down move, 15m still high, 4h high
          long_entry_logic.append(
            (_cmp_cached_71) | (_cmp_cached_61) | (_cmp_cached_64)
          )
          # 4h down move, 15m & 4h high
          long_entry_logic.append(
            (_cmp_cached_71) | (_cmp_cached_92) | (_cmp_cached_162)
          )
          # 4h down move, 1h & 4h high
          long_entry_logic.append(
            (_cmp_cached_71) | (_cmp_cached_37) | (_cmp_cached_17)
          )
          # 4h down move, 4h still high, 1d high
          long_entry_logic.append(
            (_cmp_cached_71) | (_cmp_cached_35) | (_cmp_cached_74)
          )
          # 15m still high, 1d high & overbought
          long_entry_logic.append(
            (_cmp_cached_62) | (_cmp_cached_27) | (_cmp_cached_48)
          )
          # 15m high, 4h high
          long_entry_logic.append((_cmp_cached_76) | (_cmp_cached_47))
          # 15m & 1d high, 1d overbought
          long_entry_logic.append((_cmp_cached_76) | (_cmp_cached_94) | (_cmp_cached_167))
          # 15m & 1d high, 4h overbought
          long_entry_logic.append(
            (_cmp_cached_76) | (_cmp_cached_27) | (_cmp_cached_50)
          )
          # 15m high, 4h still high
          long_entry_logic.append((_cmp_cached_18) | (_cmp_cached_35))
          # 4h & 1d high, 1d overbought
          long_entry_logic.append(
            (_cmp_cached_6) | (_cmp_cached_27) | (_cmp_cached_167)
          )
          # 4h high, 4h overbought
          long_entry_logic.append((_cmp_cached_17) | (_cmp_cached_113))
          # 4h high, 1d overbought
          long_entry_logic.append((_cmp_cached_17) | (_cmp_cached_52))
          # 1d high, 4h overbought
          long_entry_logic.append((_cmp_cached_94) | (_cmp_cached_113))
          # 1d high & overbought
          long_entry_logic.append((_cmp_cached_27) | (_cmp_cached_111))
          # 15m high, 1h still high
          long_entry_logic.append((_cmp_cached_92) | (_cmp_cached_28))
          # 15m & 4h high
          long_entry_logic.append((_cmp_cached_92) | (_cmp_cached_17))
          # 15m high, 1d overbought
          long_entry_logic.append((_cmp_cached_92) | (_cmp_cached_95))
          # 15m high, 1h still not low enough
          long_entry_logic.append((_cmp_cached_180) | (_cmp_cached_161))
          # 1d high, 4h overbought
          long_entry_logic.append((_cmp_cached_74) | (_cmp_cached_113))
          # 1d high & overbought
          long_entry_logic.append((_cmp_cached_39) | (_cmp_cached_70))
          # 4h & 1d overbought
          long_entry_logic.append((_cmp_cached_113) | (_cmp_cached_52))
          # 1d green with top wick, 1d overbought
          long_entry_logic.append(
            (_cmp_cached_140) | (_cmp_cached_141) | (_cmp_cached_107)
          )

          # Logic
          long_entry_logic.append(_cmp_cached_343)
          long_entry_logic.append(_cmp_cached_274)
          long_entry_logic.append(_cmp_cached_227)
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
          long_entry_logic.append(_cmp_cached_344)
          long_entry_logic.append(_cmp_cached_345)

        # Condition #162 - Scalp mode (Long).
        if long_entry_condition_index == 162:
          # Protections
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          long_entry_logic.append(df["protections_long_global"] == True)

          long_entry_logic.append(
            (_cmp_cached_8) & (_cmp_cached_3) & (_cmp_cached_261) & (_cmp_cached_111)
          )

          long_entry_logic.append(
            # 15m & 1h down move, 4h high
            ((_cmp_cached_5) | (_cmp_cached_30) | (_cmp_cached_64))
            # 15m & 4h down move, 1h still high
            & ((_cmp_cached_5) | (_cmp_cached_181) | (_cmp_cached_346))
            # 15m & 1d down move, 4h high
            & ((_cmp_cached_5) | (_cmp_cached_104) | (_cmp_cached_46))
            # 15m down move, 15m still high, 1h high
            & ((_cmp_cached_5) | (_cmp_cached_62) | (_cmp_cached_33))
            # 15m down move, 15m high
            & ((_cmp_cached_5) | (_cmp_cached_76))
            # 15m down move, 1h & 1d high
            & ((_cmp_cached_5) | (_cmp_cached_78) | (_cmp_cached_27))
            # 15m down move, 4h & 1d high
            & ((_cmp_cached_5) | (_cmp_cached_172) | (_cmp_cached_27))
            # 15m down move, 1d high, 1d downtrend
            & ((_cmp_cached_5) | (_cmp_cached_131) | (_cmp_cached_202))
            # 15m & 1h down move, 15m still not low enough
            & ((_cmp_cached_84) | (_cmp_cached_30) | (_cmp_cached_152))
            # 15m & 1h down nove, 1h still high
            & ((_cmp_cached_84) | (_cmp_cached_30) | (_cmp_cached_59))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_84) | (_cmp_cached_32) | (_cmp_cached_6))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_84) | (_cmp_cached_34) | (_cmp_cached_72))
            # 15m down move, 4h high, 4h downtrend
            & ((_cmp_cached_84) | (_cmp_cached_40) | (_cmp_cached_69))
            # 15m down move, 4h & 1d downtrend
            & ((_cmp_cached_84) | (_cmp_cached_93) | (_cmp_cached_65))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_87) | (_cmp_cached_11) | (_cmp_cached_24))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_87) | (_cmp_cached_17) | (_cmp_cached_20))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_88) | (_cmp_cached_11) | (_cmp_cached_72))
            # 15m down move, 15m high, 1d overbought
            & ((_cmp_cached_88) | (_cmp_cached_210) | (_cmp_cached_248))
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_184) | (_cmp_cached_33) | (_cmp_cached_66))
            # 1h & 4h down move, 15m stil high
            & ((_cmp_cached_13) | (_cmp_cached_58) | (_cmp_cached_61))
            # 1h & 4h down move, 1h still high
            & ((_cmp_cached_13) | (_cmp_cached_16) | (_cmp_cached_110))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_7) | (_cmp_cached_100) | (_cmp_cached_40))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_7) | (_cmp_cached_41) | (_cmp_cached_46))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_7) | (_cmp_cached_40) | (_cmp_cached_95))
            # 1h & 4h down move, 4h still high
            & ((_cmp_cached_9) | (_cmp_cached_58) | (_cmp_cached_122))
            # 1h & 3h down move, 1d high
            & ((_cmp_cached_9) | (_cmp_cached_181) | (_cmp_cached_108))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_15) | (_cmp_cached_100) | (_cmp_cached_17))
            # 1h down move, 1h downtrend, 1d overbought
            & ((_cmp_cached_15) | (_cmp_cached_109) | (_cmp_cached_63))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_30) | (_cmp_cached_21) | (_cmp_cached_17))
            # 1h & 4h down move, 1d downtrend
            & ((_cmp_cached_15) | (_cmp_cached_16) | (_cmp_cached_102))
            # 1h down move, 1h & 1d high
            & ((_cmp_cached_15) | (_cmp_cached_115) | (_cmp_cached_131))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_15) | (_cmp_cached_115) | (_cmp_cached_107))
            # 1h down move, 1d high & overbought
            & ((_cmp_cached_15) | (_cmp_cached_39) | (_cmp_cached_52))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_115) | (_cmp_cached_48))
            # 1h down move, 1h high
            & ((_cmp_cached_11) | (_cmp_cached_78))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_32) | (_cmp_cached_21) | (_cmp_cached_64))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_32) | (_cmp_cached_115) | (_cmp_cached_86))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_34) | (_cmp_cached_12) | (_cmp_cached_51))
            # 1h down move, 1h high, 4h downtrend
            & ((_cmp_cached_36) | (_cmp_cached_19) | (_cmp_cached_69))
            # 1h down move, 15m still high, 1d overbought
            & ((_cmp_cached_38) | (_cmp_cached_62) | (_cmp_cached_107))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_38) | (_cmp_cached_50) | (_cmp_cached_107))
            # 1h down move,  4h high, 1d overbought
            & ((_cmp_cached_117) | (_cmp_cached_72) | (_cmp_cached_248))
            # 4h down move, 1d high
            & ((_cmp_cached_151) | (_cmp_cached_94))
            # 4h down move, 15m still high
            & ((_cmp_cached_151) | (_cmp_cached_61))
            # 4h down move, 1d high
            & ((_cmp_cached_151) | (_cmp_cached_39))
            # 4h down move, 1d overbought
            & ((_cmp_cached_151) | (_cmp_cached_52))
            # 4h & 1d down move
            & ((_cmp_cached_55) | (_cmp_cached_153))
            # 4h down move, 1d high, 1h downtrend
            & ((_cmp_cached_58) | (_cmp_cached_131) | (_cmp_cached_109))
            # 4h down move, 1h & 4h downtrend
            & ((_cmp_cached_58) | (_cmp_cached_239) | (_cmp_cached_213))
            # 4h & 1d down move, 4h still not low enough
            & ((_cmp_cached_100) | (_cmp_cached_104) | (_cmp_cached_124))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_41) | (_cmp_cached_122) | (_cmp_cached_65))
            # 4h down move, 15m still high, 1d overbought
            & ((_cmp_cached_181) | (_cmp_cached_62) | (_cmp_cached_107))
            # 4h down move, 4h & 1d overbought
            & ((_cmp_cached_181) | (_cmp_cached_50) | (_cmp_cached_107))
            # 1d down move, 1h high
            & ((_cmp_cached_225) | (_cmp_cached_37))
            # 1d down move, 15m still high
            & ((_cmp_cached_225) | (_cmp_cached_62))
            # 1d down move, 15m still high, 1h high
            & ((_cmp_cached_153) | (_cmp_cached_31) | (_cmp_cached_37))
            # 1d down move, 1h & 4h high
            & ((_cmp_cached_153) | (_cmp_cached_24) | (_cmp_cached_46))
            # 1d down move, 4h high
            & ((_cmp_cached_104) | (_cmp_cached_66))
            # 1d downtrend, 1d high & overbought
            & ((_cmp_cached_224) | (_cmp_cached_131) | (_cmp_cached_48))
            # 1h & 4h high, 1d overbought
            & ((_cmp_cached_24) | (_cmp_cached_17) | (_cmp_cached_70))
            # 1h & 4h high, 1d overbought
            & ((_cmp_cached_78) | (_cmp_cached_46) | (_cmp_cached_167))
            # 1h & 4h high
            & ((_cmp_cached_80) | (_cmp_cached_6))
            # 4h & 1d high, 4h overbought
            & ((_cmp_cached_77) | (_cmp_cached_27) | (_cmp_cached_51))
            # 4h high, 4h & 1d overbought
            & ((_cmp_cached_77) | (_cmp_cached_20) | (_cmp_cached_167))
            # 1d still high, 1h & 4h downtrend
            & ((_cmp_cached_238) | (_cmp_cached_129) | (_cmp_cached_69))
            # 1h high, 1h overbought
            & ((_cmp_cached_19) | (_cmp_cached_183))
            # 1h high, 1d downtrend
            & ((_cmp_cached_19) | (_cmp_cached_194))
            # 4h high, 1h overbought, 1d downtrend
            & ((_cmp_cached_12) | (_cmp_cached_82) | (_cmp_cached_206))
            # 4h high, 1h & 4h overbought
            & ((_cmp_cached_72) | (_cmp_cached_79) | (_cmp_cached_86))
            # 1h & 4h overbought
            & ((_cmp_cached_182) | (_cmp_cached_196))
            # 1h P&D, 1h down move
            & ((_cmp_cached_347) | (df["change_pct_1h"].shift(12) < 10.0) | (_cmp_cached_117))
            # 4h P&D, 4h high
            & ((_cmp_cached_348) | (df["change_pct_4h"].shift(48) < 30.0) | (_cmp_cached_46))
            # 4h green, 15m & 1h down move
            & ((_cmp_cached_349) | (_cmp_cached_5) | (_cmp_cached_34))
            # 4h green, 1h down move
            & ((_cmp_cached_350) | (_cmp_cached_117))
            # 4h green with top wick
            & ((_cmp_cached_351) | (_cmp_cached_351))
            # 1d green with top wick, 15m still high
            & ((_cmp_cached_352) | (_cmp_cached_353) | (_cmp_cached_62))
            # 1d green, 4h down move, 4h still high
            & ((_cmp_cached_142) | (_cmp_cached_21) | (_cmp_cached_122))
            # 1d green with top wick, 4h down move
            & ((_cmp_cached_142) | (_cmp_cached_353) | (_cmp_cached_175))
            # 1d top wick, 4h still high
            & ((_cmp_cached_233) | (_cmp_cached_122))
            # big drop in last 4 days, 1d down move
            & ((df["close"] > (df["high_max_24_4h"] * 0.20)) | (_cmp_cached_104))
            # big drop in the last 20 days, 4h down move
            & ((df["close"] > (df["high_max_20_1d"] * 0.15)) | (_cmp_cached_100))
            # big drop in the last 20 days, 1d down move
            & ((df["close"] > (df["high_max_20_1d"] * 0.05)) | (_cmp_cached_104))
            # big drop in the last 20 days, 1h still high
            & ((df["close"] > (df["high_max_20_1d"] * 0.05)) | (_cmp_cached_147))
            # big drop in the last 20 days, 4h high
            & ((df["close"] > (df["high_max_20_1d"] * 0.05)) | (_cmp_cached_64))
          )

          # Logic
          long_entry_logic.append(
            (_cmp_cached_243)
            & (_cmp_cached_272)
            & (_cmp_cached_208)
            & (df["EMA_26"] > df["EMA_12"])
            & ((df["EMA_26"] - df["EMA_12"]) > (df["open"] * 0.030))
            & ((df["EMA_26"].shift() - df["EMA_12"].shift()) > (df["open"] / 100.0))
            & (df["close"] < df["SMA_9"])
          )

        # Condition #163 - Scalp mode (Long).
        if long_entry_condition_index == 163:
          # Protections
          long_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
          long_entry_logic.append(df["protections_long_global"] == True)

          long_entry_logic.append((_cmp_cached_157) & (_cmp_cached_5) & (_cmp_cached_30))

          long_entry_logic.append(
            # 5m & 15m & 4h down mnove, 4h high
            ((_cmp_cached_209) | (_cmp_cached_87) | (_cmp_cached_181) | (_cmp_cached_77))
            # 5m & 15m & 1d down move, 1h high
            & ((_cmp_cached_209) | (_cmp_cached_88) | (_cmp_cached_121) | (_cmp_cached_78))
            # 5m & 1h down move, 15m still high, 4h high
            & (
              (_cmp_cached_354) | (_cmp_cached_36) | (_cmp_cached_292) | (_cmp_cached_6)
            )
            # 5m & 1h & 15m down move, 1h still not low enough
            & ((_cmp_cached_209) | (_cmp_cached_32) | (_cmp_cached_29) | (_cmp_cached_150))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_209) | (_cmp_cached_21) | (_cmp_cached_64))
            # 5m & 4h down move, 15m high
            & ((_cmp_cached_209) | (_cmp_cached_91) | (_cmp_cached_210))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_355) | (_cmp_cached_36) | (_cmp_cached_80))
            # 15m & 1h & 4h & 1d down move
            & ((_cmp_cached_84) | (_cmp_cached_11) | (_cmp_cached_16) | (_cmp_cached_121))
            # 15m & 1h down move, 1h & 4h high
            & (
              (_cmp_cached_84)
              | (_cmp_cached_11)
              | (_cmp_cached_68)
              | (_cmp_cached_6)
            )
            # 15m & 1h & 4h down move, 1d overbought
            & ((_cmp_cached_84) | (_cmp_cached_32) | (_cmp_cached_21) | (_cmp_cached_52))
            # 15m & 1h & 4h down move, 1h downtrend, 4h high
            & (
              (_cmp_cached_84)
              | (_cmp_cached_32)
              | (_cmp_cached_175)
              | (_cmp_cached_356)
              | (_cmp_cached_77)
            )
            # 15m & 1h down move, 15m high
            & ((_cmp_cached_84) | (_cmp_cached_32) | (_cmp_cached_210))
            # 15m & 1h down move, 4h high
            & ((_cmp_cached_84) | (_cmp_cached_32) | (_cmp_cached_316))
            # 15m & 1h down move, 15m still high
            & ((_cmp_cached_84) | (_cmp_cached_32) | (_cmp_cached_31))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_84) | (_cmp_cached_32) | (_cmp_cached_24))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_84) | (_cmp_cached_32) | (_cmp_cached_37))
            # 15m & 1h down move, 1d overbought
            & ((_cmp_cached_84) | (_cmp_cached_32) | (_cmp_cached_70))
            # 15m & 1h & 4h down move, 4h high
            & ((_cmp_cached_84) | (_cmp_cached_34) | (_cmp_cached_197) | (_cmp_cached_357))
            # 15m & 1h & 1d down move, 15m high
            & (
              (_cmp_cached_84)
              | (_cmp_cached_34)
              | (_cmp_cached_125)
              | (_cmp_cached_210)
            )
            # 15m & 1h down move, 15m high
            & ((_cmp_cached_84) | (_cmp_cached_34) | (_cmp_cached_76))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_84) | (_cmp_cached_34) | (_cmp_cached_281))
            # 15m & 1h down move, 15m still not low enough, 1h & 4h high
            & (
              (_cmp_cached_84)
              | (_cmp_cached_36)
              | (_cmp_cached_10)
              | (_cmp_cached_33)
              | (_cmp_cached_77)
            )
            # 15m & 1h down move, 4h high & overbought
            & ((_cmp_cached_84) | (_cmp_cached_38) | (_cmp_cached_341) | (_cmp_cached_86))
            # 15m & 1h down move, 1h high
            & ((_cmp_cached_84) | (_cmp_cached_117) | (_cmp_cached_49))
            # 15m & 4h down move, 15m high
            & ((_cmp_cached_84) | (_cmp_cached_41) | (_cmp_cached_210))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_84) | (_cmp_cached_41) | (_cmp_cached_77))
            # 15m & 4h down move, 1h still high
            & ((_cmp_cached_84) | (_cmp_cached_181) | (_cmp_cached_110))
            # 15m & 4h down move, 1d high
            & ((_cmp_cached_84) | (_cmp_cached_21) | (_cmp_cached_39))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_84) | (_cmp_cached_21) | (_cmp_cached_123))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_84) | (_cmp_cached_99) | (_cmp_cached_19))
            # 15m down move, 4h & 1d up move, 1d downtrend
            & ((_cmp_cached_84) | (_cmp_cached_358) | (_cmp_cached_359) | (_cmp_cached_143))
            # 15m & 1d down move, 4h high
            & ((_cmp_cached_84) | (_cmp_cached_153) | (_cmp_cached_64))
            # 15m & 1h down move, 1h & 4h still high
            & (
              (_cmp_cached_84)
              | (_cmp_cached_29)
              | (_cmp_cached_26)
              | (_cmp_cached_122)
            )
            # 15m & 1d down move, 1h high
            & ((_cmp_cached_84) | (_cmp_cached_29) | (_cmp_cached_80))
            # 15m & 1d down move, 1d high
            & ((_cmp_cached_84) | (_cmp_cached_104) | (_cmp_cached_108))
            # 15m & 1d down move, 1d overbought
            & ((_cmp_cached_84) | (_cmp_cached_125) | (_cmp_cached_107))
            # 15m & 1d down move, 1d high
            & ((_cmp_cached_84) | (_cmp_cached_73) | (_cmp_cached_106))
            # 15m & 1d down move, 1d high
            & ((_cmp_cached_84) | (_cmp_cached_126) | (_cmp_cached_74))
            # 15m down move, 15m & 4h high
            & ((_cmp_cached_84) | (_cmp_cached_76) | (_cmp_cached_77))
            # 15m down move, 15m & 1h high
            & ((_cmp_cached_84) | (_cmp_cached_212) | (_cmp_cached_80))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_84) | (_cmp_cached_78) | (_cmp_cached_63))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_84) | (_cmp_cached_80) | (_cmp_cached_52))
            # 15m down move, 4h still high, 4h downtrend
            & ((_cmp_cached_84) | (_cmp_cached_96) | (_cmp_cached_69))
            # 15m down move, 1d high & overbought
            & ((_cmp_cached_84) | (_cmp_cached_27) | (_cmp_cached_48))
            # 15m down move, 15m still not low enough, 4h high
            & (
              (_cmp_cached_84) | (_cmp_cached_152) | (_cmp_cached_35)
            )
            # 15m down move, 15m & 1h high
            & (
              (_cmp_cached_84) | (_cmp_cached_61) | (_cmp_cached_59)
            )
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_84) | (_cmp_cached_37) | (_cmp_cached_70))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_84) | (_cmp_cached_37) | (_cmp_cached_248))
            # 15m down move, 1h high & overbought
            & ((_cmp_cached_84) | (_cmp_cached_19) | (_cmp_cached_79))
            # 15m down move, 1h high, 1d overbought
            & ((_cmp_cached_84) | (_cmp_cached_19) | (_cmp_cached_48))
            # 15m down move, 4h high, 1d overbought
            & ((_cmp_cached_84) | (_cmp_cached_12) | (_cmp_cached_201))
            # 15m down move, 4h high & overbought
            & ((_cmp_cached_84) | (_cmp_cached_72) | (_cmp_cached_211))
            # 15m down move, 4h high
            & (
              (_cmp_cached_84)
              | (_cmp_cached_341)
              | (_cmp_cached_72)
              | (df["EMA_9"] < (df["EMA_26"] * 0.972))
            )
            # 15m down move, 4h high and downtrend
            & ((_cmp_cached_84) | (_cmp_cached_360) | (_cmp_cached_77))
            # 15m down move, 1h high, 4h overbought
            & ((_cmp_cached_84) | (_cmp_cached_78) | (_cmp_cached_20))
            # 15m down move, 4h & 1d downtrend
            & ((_cmp_cached_84) | (_cmp_cached_69) | (_cmp_cached_57))
            # 16m & 1h down move, 1h still high
            & ((_cmp_cached_87) | (_cmp_cached_11) | (_cmp_cached_28))
            # 15m & 1h down move, 1h downtrend, 1h downtrend, 15m still high, 1h high
            & (
              (_cmp_cached_87)
              | (_cmp_cached_34)
              | (_cmp_cached_356)
              | (_cmp_cached_31)
              | (_cmp_cached_45)
            )
            # 15m & 1h down move, 4h high & overbought
            & ((_cmp_cached_87) | (_cmp_cached_38) | (_cmp_cached_341) | (_cmp_cached_86))
            # 15m & 4h down move, 15m high
            & ((_cmp_cached_87) | (_cmp_cached_16) | (_cmp_cached_210))
            # 15m & 4h down move, 1h high
            & ((_cmp_cached_87) | (_cmp_cached_21) | (_cmp_cached_80))
            # 15m & 1d down move, 4h high
            & ((_cmp_cached_87) | (_cmp_cached_104) | (_cmp_cached_64))
            # 15m down move, 15m still high, 4h high
            & (
              (_cmp_cached_87)
              | (_cmp_cached_292)
              | (_cmp_cached_105)
              | (_cmp_cached_6)
            )
            # 15m down move, 4h downtrend, 4h overbought
            & ((_cmp_cached_87) | (_cmp_cached_361) | (_cmp_cached_113))
            # 15m down move, 1h & 4h high, 1f overbought
            & (
              (_cmp_cached_87)
              | (_cmp_cached_45)
              | (_cmp_cached_341)
              | (_cmp_cached_63)
            )
            # 15m down move, 1h & 4h high
            & ((_cmp_cached_87) | (_cmp_cached_78) | (_cmp_cached_6))
            # 15m down move, 1d high, 4h overbought
            & ((_cmp_cached_87) | (_cmp_cached_27) | (_cmp_cached_51))
            # 15m down move, 1h high & overbought
            & ((_cmp_cached_87) | (_cmp_cached_19) | (_cmp_cached_82))
            # 15m & 1d down move, 1d high
            & ((_cmp_cached_88) | (_cmp_cached_125) | (_cmp_cached_108))
            # 15m down move, 4h high, 1d downtrend
            & ((_cmp_cached_88) | (_cmp_cached_72) | (_cmp_cached_102))
            # 15m & 1h down move, 15m still not low enough, 1h & 4h high
            & (
              (_cmp_cached_89)
              | (_cmp_cached_38)
              | (_cmp_cached_298)
              | (_cmp_cached_346)
              | (_cmp_cached_341)
              | (_cmp_cached_166)
              | (_cmp_cached_115)
              | (_cmp_cached_6)
            )
            # 15m & 4h down move, 4h overbought
            & ((_cmp_cached_89) | (_cmp_cached_71) | (_cmp_cached_83))
            # 15m & 4h down move, 4h high
            & ((_cmp_cached_184) | (_cmp_cached_21) | (_cmp_cached_12))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_11) | (_cmp_cached_41) | (_cmp_cached_74))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_11) | (_cmp_cached_181) | (_cmp_cached_17))
            # 1h & 4h down move, 4h high
            & ((_cmp_cached_11) | (_cmp_cached_91) | (_cmp_cached_12))
            # 1h & 4h down move, 1d high
            & ((_cmp_cached_11) | (_cmp_cached_197) | (_cmp_cached_27))
            # 1h & 1d down move, 1d high
            & ((_cmp_cached_11) | (_cmp_cached_125) | (_cmp_cached_106))
            # 1h down move, 15m downtrend, 4h still high
            & ((_cmp_cached_11) | (_cmp_cached_362) | (_cmp_cached_122))
            # 1h down move, 4h downtrend, 4h high
            & ((_cmp_cached_11) | (_cmp_cached_252) | (_cmp_cached_17))
            # 1h down move, 15m still high, 1d downtrend
            & ((_cmp_cached_11) | (_cmp_cached_31) | (_cmp_cached_57))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_11) | (_cmp_cached_115) | (_cmp_cached_6))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_11) | (_cmp_cached_78) | (_cmp_cached_143))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_11) | (_cmp_cached_46) | (_cmp_cached_20))
            # 1h down move, 1h still not low enough, 1d downtrend
            & ((_cmp_cached_11) | (_cmp_cached_161) | (_cmp_cached_65))
            # 1h down move, 4h high, 1d overbought
            & ((_cmp_cached_11) | (_cmp_cached_72) | (_cmp_cached_201))
            # 1h & 4h down move, 1h still high
            & ((_cmp_cached_32) | (_cmp_cached_41) | (_cmp_cached_110))
            # 1h & 1d down move, 1d still high
            & ((_cmp_cached_32) | (_cmp_cached_178) | (_cmp_cached_119))
            # 1h down move, 15m & 4h high
            & ((_cmp_cached_32) | (_cmp_cached_210) | (_cmp_cached_363))
            # 1h down move, 15m & 4h high
            & ((_cmp_cached_32) | (_cmp_cached_76) | (_cmp_cached_46))
            # 1h down move, 1h high
            & ((_cmp_cached_32) | (_cmp_cached_364) | (_cmp_cached_78))
            # 1h down move, 1h still high, 1d overbought
            & ((_cmp_cached_32) | (_cmp_cached_26) | (_cmp_cached_52))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_32) | (_cmp_cached_33) | (_cmp_cached_6))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_32) | (_cmp_cached_78) | (_cmp_cached_143))
            # 1h down move, 1h highm 1d overbought
            & ((_cmp_cached_32) | (_cmp_cached_78) | (_cmp_cached_52))
            # 1h down move, 4h high & overbought
            & ((_cmp_cached_32) | (_cmp_cached_6) | (_cmp_cached_51))
            # 1h down move, 1d high, 4h overbought
            & ((_cmp_cached_32) | (_cmp_cached_27) | (_cmp_cached_20))
            # 1h & 4h down move, 1h still high, 4h high
            & ((_cmp_cached_34) | (_cmp_cached_71) | (_cmp_cached_346) | (_cmp_cached_341))
            # 1h down move, 15m still not low enough, 1h high
            & ((_cmp_cached_34) | (_cmp_cached_10) | (_cmp_cached_33))
            # 1h down move, 1h & 1d high
            & ((_cmp_cached_34) | (_cmp_cached_115) | (_cmp_cached_27))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_34) | (_cmp_cached_24) | (_cmp_cached_211))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_34) | (_cmp_cached_24) | (_cmp_cached_46))
            # 1h down move, 1h & 1d high
            & ((_cmp_cached_34) | (_cmp_cached_78) | (_cmp_cached_94))
            # 1h down move, 4h & 1d overbought
            & ((_cmp_cached_34) | (_cmp_cached_20) | (_cmp_cached_63))
            # 1h & 1d down move, 1d high
            & ((_cmp_cached_36) | (_cmp_cached_223) | (_cmp_cached_27))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_36) | (_cmp_cached_24) | (_cmp_cached_113))
            # 1h down move, 1h & 4h high
            & ((_cmp_cached_36) | (_cmp_cached_33) | (_cmp_cached_77))
            # 1h down move, 1h high, 1d overbought
            & ((_cmp_cached_36) | (_cmp_cached_45) | (_cmp_cached_63))
            # 1h down move, 1h high, 15m downtrend
            & ((_cmp_cached_36) | (_cmp_cached_78) | (_cmp_cached_261))
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_36) | (_cmp_cached_19) | (_cmp_cached_65))
            # 1h & 4h down move, 1d overbought
            & ((_cmp_cached_38) | (_cmp_cached_197) | (_cmp_cached_111))
            # 1h & 1d down move, 4h high
            & ((_cmp_cached_38) | (_cmp_cached_73) | (_cmp_cached_72))
            # 1h down move, 1h high, 4h overbought
            & ((_cmp_cached_38) | (_cmp_cached_80) | (_cmp_cached_50))
            # 1h & 4h down move, 1h & 4h high
            & (
              (_cmp_cached_117)
              | (_cmp_cached_197)
              | (_cmp_cached_45)
              | (_cmp_cached_6)
            )
            # 1h down move, 15m & 1h high
            & ((_cmp_cached_117) | (_cmp_cached_210) | (_cmp_cached_19))
            # 1h down move, 4h & 1d high
            & ((_cmp_cached_117) | (_cmp_cached_46) | (_cmp_cached_94))
            # 1h down move, 4h high, 1h overbought
            & ((_cmp_cached_174) | (_cmp_cached_6) | (_cmp_cached_79))
            # 1h down move, 15m & 1h high, 1d downtrend
            & (
              (_cmp_cached_53)
              | (_cmp_cached_365)
              | (_cmp_cached_19)
              | (_cmp_cached_137)
            )
            # 1h down move, 1h high, 1d downtrend
            & ((_cmp_cached_53) | (_cmp_cached_49) | (_cmp_cached_57))
            # 4h down move, 15m high
            & ((_cmp_cached_151) | (_cmp_cached_62))
            # 4h & 1d down move, 1d high
            & ((_cmp_cached_58) | (_cmp_cached_73) | (_cmp_cached_94))
            # 4h down move, 15m still not low enough, 4h downtrend
            & ((_cmp_cached_58) | (_cmp_cached_10) | (_cmp_cached_189))
            # 4h down move, 15m & 1h still not low enough
            & ((_cmp_cached_58) | (_cmp_cached_10) | (_cmp_cached_290))
            # 4h down move, 4h still high
            & ((_cmp_cached_58) | (_cmp_cached_96))
            # 4h down move, 1h still high, 4h downtrend
            & ((_cmp_cached_58) | (_cmp_cached_59) | (_cmp_cached_128))
            # 4h down move, 1d still high, 1d downtrend
            & ((_cmp_cached_25) | (_cmp_cached_176) | (_cmp_cached_186))
            # 4h down move, 4h high
            & ((_cmp_cached_25) | (_cmp_cached_40))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_25) | (_cmp_cached_39) | (_cmp_cached_167))
            # 4h down move, 15m still high, 1d overbought
            & ((_cmp_cached_100) | (_cmp_cached_31) | (_cmp_cached_167))
            # 4h & 1d down move, 1h & 4h low
            & ((_cmp_cached_16) | (_cmp_cached_121) | (_cmp_cached_97) | (_cmp_cached_366))
            # 4h down move, 4h still high 1d downtrend
            & ((_cmp_cached_16) | (_cmp_cached_122) | (_cmp_cached_57))
            # 4h down move, 1d high & overbought
            & ((_cmp_cached_16) | (_cmp_cached_74) | (_cmp_cached_201))
            # 4h down move, 4h & 1d high
            & ((_cmp_cached_21) | (_cmp_cached_17) | (_cmp_cached_27))
            # 4h down move, 15m still high, 1d overbought
            & ((_cmp_cached_181) | (_cmp_cached_62) | (_cmp_cached_107))
            # 4h down move, 4h high, 1d overbought
            & ((_cmp_cached_181) | (_cmp_cached_77) | (_cmp_cached_167))
            # 4h down move, 1h high, 1d downtrend
            & ((_cmp_cached_181) | (_cmp_cached_19) | (_cmp_cached_57))
            # 4h down move, 4h & 1d overbought
            & ((_cmp_cached_181) | (_cmp_cached_50) | (_cmp_cached_107))
            # 4h down move, 4h high, 1d overbought
            & ((_cmp_cached_91) | (_cmp_cached_17) | (_cmp_cached_167))
            # 4h down move, 1d high, 4h overbought
            & ((_cmp_cached_91) | (_cmp_cached_94) | (_cmp_cached_50))
            # 4h down move, 4h still high, 1d downtrend
            & ((_cmp_cached_99) | (_cmp_cached_169) | (_cmp_cached_102))
            # 4h down move, 4h high & overbought
            & ((_cmp_cached_99) | (_cmp_cached_17) | (_cmp_cached_50))
            # 4h down move, 15m still high, 1d overbought
            & ((_cmp_cached_175) | (_cmp_cached_31) | (_cmp_cached_48))
            # 4h & 1d down move, 4h high, 1d overbought
            & (
              (_cmp_cached_71) | (_cmp_cached_126) | (_cmp_cached_172) | (_cmp_cached_52)
            )
            # 4h down move, 4h & 1d high
            & ((_cmp_cached_367) | (_cmp_cached_46) | (_cmp_cached_27))
            # 1d down move, 4h high
            & ((_cmp_cached_225) | (_cmp_cached_162))
            # 1d down move, 1h high
            & ((_cmp_cached_101) | (_cmp_cached_19))
            # 1d down move, 15m & 1h still high
            & ((_cmp_cached_153) | (_cmp_cached_292) | (_cmp_cached_59))
            # 1d down move, 1h & 4h high
            & ((_cmp_cached_153) | (_cmp_cached_33) | (_cmp_cached_46))
            # 1d down move, 1h & 4h still high
            & ((_cmp_cached_153) | (_cmp_cached_28) | (_cmp_cached_96))
            # 1d down move, 1h high & overbought
            & ((_cmp_cached_104) | (_cmp_cached_19) | (_cmp_cached_79))
            # 1d down move, 1d high & overbought
            & ((_cmp_cached_125) | (_cmp_cached_106) | (_cmp_cached_167))
            # 1d down move, 4h high & overbought
            & ((_cmp_cached_198) | (_cmp_cached_77) | (_cmp_cached_51))
            # 1d down move, 1h high, 1d overbought
            & ((_cmp_cached_126) | (_cmp_cached_33) | (_cmp_cached_63))
            # 1d down move, 15m still high, 1d overbought
            & ((_cmp_cached_258) | (_cmp_cached_31) | (_cmp_cached_48))
            # 1d down move, 4h & 1d high
            & ((_cmp_cached_258) | (_cmp_cached_50) | (_cmp_cached_95))
            # 5m still high, 1h down move, 15m still high, 1h high
            & (
              (_cmp_cached_287)
              | (_cmp_cached_32)
              | (_cmp_cached_62)
              | (_cmp_cached_46)
            )
            # 5m still high, 15m high
            & ((_cmp_cached_368) | (_cmp_cached_76))
            # 5m still high, 1h down move, 4h high
            & ((_cmp_cached_247) | (_cmp_cached_32) | (_cmp_cached_6))
            # 15m down move, 1h high
            & ((_cmp_cached_369) | (_cmp_cached_19))
            # 15m down move, 4h & 1d high
            & (
              (_cmp_cached_370) | (_cmp_cached_72) | (_cmp_cached_148)
            )
            # 1h downtrend, 4h high, 1d downtrend
            & ((_cmp_cached_371) | (_cmp_cached_72) | (_cmp_cached_154))
            # 15m & 1h high, 1d overbought
            & ((_cmp_cached_210) | (_cmp_cached_80) | (_cmp_cached_167))
            # 4h high, 4h & 1d overbought
            & ((_cmp_cached_77) | (_cmp_cached_20) | (_cmp_cached_167))
            # 4h & 1d high, 1d overbought
            & ((_cmp_cached_47) | (_cmp_cached_131) | (_cmp_cached_112))
            # 4h & 1d high, 1d overbought
            & ((_cmp_cached_6) | (_cmp_cached_27) | (_cmp_cached_70))
            # 1d still high, 4h & 1d downtrend
            & ((_cmp_cached_238) | (_cmp_cached_69) | (_cmp_cached_102))
            # 4h top wick, 15m & 1h down move
            & ((_cmp_cached_372) | (_cmp_cached_84) | (_cmp_cached_36))
            # 4h top wick, 1h down move, 1h high
            & ((_cmp_cached_372) | (_cmp_cached_32) | (_cmp_cached_24))
            # 1d red, 1h down move, 1h still high
            & ((_cmp_cached_373) | (_cmp_cached_11) | (_cmp_cached_26))
            # 1d P&D, 1h high
            & (
              (_cmp_cached_373)
              | (df["change_pct_1d"].shift(288) < 15.0)
              | (_cmp_cached_19)
            )
            # 1d P&D, 1d downtrend
            & ((_cmp_cached_136) | (df["change_pct_1d"].shift(288) < 30.0) | (_cmp_cached_374))
            # 1d P&D, 15m high
            & ((_cmp_cached_231) | (df["change_pct_1d"].shift(288) < 40.0) | (_cmp_cached_62))
            # 1d P&D, 1h high
            & (
              (_cmp_cached_231)
              | (df["change_pct_1d"].shift(288) < 40.0)
              | (_cmp_cached_37)
            )
            # 1d red with top wick, 1h high
            & ((_cmp_cached_231) | (_cmp_cached_375) | (_cmp_cached_33))
            # 1d green, 4m down move, 4h high
            & ((_cmp_cached_140) | (_cmp_cached_175) | (_cmp_cached_122))
            # 1d green with top wick, 1d low
            & ((_cmp_cached_140) | (_cmp_cached_375) | (_cmp_cached_143))
            # 1d top wick, 1h still high
            & ((_cmp_cached_141) | (_cmp_cached_26))
            # 1d top wick, 4h still high
            & ((_cmp_cached_145) | (_cmp_cached_35))
            # 1d top wick, 1h down move
            & ((_cmp_cached_233) | (_cmp_cached_32))
            # big drop in the last 12 days, 1h down move, 1h high
            & ((df["close"] > (df["high_max_12_1d"] * 0.35)) | (_cmp_cached_34) | (_cmp_cached_24))
            # big drop in the last 20 days, 1h down move, 1h high
            & (
              (df["close"] > (df["high_max_20_1d"] * 0.30))
              | (_cmp_cached_32)
              | (_cmp_cached_260)
            )
            # big drop in the last 20 days, 1d high, 1d downtrend
            & (
              (df["close"] > (df["high_max_20_1d"] * 0.20))
              | (_cmp_cached_148)
              | (_cmp_cached_149)
            )
          )

          # Logic
          long_entry_logic.append(
            (_cmp_cached_376)
            & (_cmp_cached_243)
            & (_cmp_cached_272)
            & (_cmp_cached_237)
            & (df["EMA_9"] < (df["EMA_26"] * 0.982))
            & (df["close"] < df["SMA_9"])
          )

        ###############################################################################################

        # LONG ENTRY CONDITIONS ENDS HERE

        ###############################################################################################

        long_entry_logic.append(_cmp_cached_377)
        item_long_entry = _and_conditions(long_entry_logic)
        _append_entry_tag(entry_tags, item_long_entry, f"{long_entry_condition_index} ")
        long_entry_conditions.append(item_long_entry)
        df.loc[:, "enter_long"] = item_long_entry.astype(int)

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

    if _test_x7_short_entries_enabled:
      _cmp_cached_378 = _cmp("RSI_3_1h", ">=", 5.0)
      _cmp_cached_379 = _cmp("RSI_3_4h", ">=", 20.0)
      _cmp_cached_380 = _cmp("RSI_3_1d", ">=", 20.0)
      _cmp_cached_381 = _cmp("RSI_14_1h", ">", 20.0)
      _cmp_cached_382 = _cmp("RSI_14_4h", ">", 20.0)
      _cmp_cached_383 = _cmp("RSI_14_1d", ">", 10.0)
      _cmp_cached_384 = _cmp("RSI_3", "<", 97.0)
      _cmp_cached_385 = _cmp("AROONU_14_4h", ">", 60.0)
      _cmp_cached_386 = _cmp("STOCHRSIk_14_14_3_3_4h", ">", 50.0)
      _cmp_cached_387 = _cmp("RSI_3", "<", 95.0)
      _cmp_cached_388 = _cmp("RSI_3_15m", "<", 95.0)
      _cmp_cached_389 = _cmp("RSI_3_1h", "<", 90.0)
      _cmp_cached_390 = _cmp("AROOND_14_15m", "<", 25.0)
      _cmp_cached_391 = _cmp("AROOND_14_1h", "<", 25.0)
      _cmp_cached_392 = _cmp("STOCHRSIk_14_14_3_3_1h", ">", 70.0)
      _cmp_cached_393 = _cmp("STOCHRSIk_14_14_3_3_4h", ">", 70.0)
      _cmp_cached_394 = _cmp("RSI_3", "<", 90.0)
      _cmp_cached_395 = _cmp("RSI_3_1h", "<", 80.0)
      _cmp_cached_396 = _cmp("STOCHRSIk_14_14_3_3_1h", ">", 50.0)
      _cmp_cached_397 = _cmp("AROONU_14_4h", ">", 20.0)
      _cmp_cached_398 = _cmp("CMF_20_15m", "<", 0.30)
      _cmp_cached_399 = _cmp("CMF_20_1h", "<", 0.30)
      _cmp_cached_400 = _cmp("AROONU_14_15m", ">", 50.0)
      _cmp_cached_401 = _cmp("STOCHRSIk_14_14_3_3_15m", ">", 60.0)
      _cmp_cached_402 = _cmp("STOCHRSIk_14_14_3_3_1h", ">", 75.0)
      _cmp_cached_403 = _cmp("RSI_3_15m", "<", 97.0)
      _cmp_cached_404 = _cmp("AROONU_14_1h", ">", 30.0)
      _cmp_cached_405 = _cmp("RSI_3_1h", "<", 95.0)
      _cmp_cached_406 = _cmp("CCI_20_change_pct_4h", "<", -0.0)
      _cmp_cached_407 = _cmp("STOCHRSIk_14_14_3_3_4h", ">", 80.0)
      _cmp_cached_408 = _cmp("RSI_3_1h", "<", 85.0)
      _cmp_cached_409 = _cmp("RSI_3_1h", "<", 70.0)
      _cmp_cached_410 = _cmp("RSI_3_4h", "<", 95.0)
      _cmp_cached_411 = _cmp("RSI_14_1d", ">", 40.0)
      _cmp_cached_412 = _cmp("AROONU_14_1h", ">", 40.0)
      _cmp_cached_413 = _cmp("STOCHRSIk_14_14_3_3_15m", ">", 70.0)
      _cmp_cached_414 = _cmp("STOCHRSIk_14_14_3_3_1h", ">", 10.0)
      _cmp_cached_415 = _cmp("AROONU_14_4h", ">", 70.0)
      _cmp_cached_416 = _cmp("RSI_3_change_pct_1h", "<", 80.0)
      _cmp_cached_417 = _cmp("RSI_3_15m", "<", 90.0)
      _cmp_cached_418 = _cmp("AROOND_14_1h", "<", 50.0)
      _cmp_cached_419 = _cmp("RSI_14_1h", ">", 80.0)
      _cmp_cached_420 = _cmp("STOCHRSIk_14_14_3_3_1h", ">", 80.0)
      _cmp_cached_421 = _cmp("STOCHRSIk_14_14_3_3_1h", ">", 90.0)
      _cmp_cached_422 = _cmp("AROOND_14_4h", "<", 50.0)
      _cmp_cached_423 = _cmp("RSI_3_4h", "<", 85.0)
      _cmp_cached_424 = _cmp("STOCHRSIk_14_14_3_3_1d", ">", 30.0)
      _cmp_cached_425 = _cmp("RSI_3_4h", "<", 70.0)
      _cmp_cached_426 = _cmp("STOCHRSIk_14_14_3_3_1h", ">", 20.0)
      _cmp_cached_427 = _cmp("RSI_3_4h", "<", 60.0)
      _cmp_cached_428 = _cmp("AROONU_14_4h", ">", 30.0)
      _cmp_cached_429 = _cmp("AROONU_14_4h", ">", 10.0)
      _cmp_cached_430 = _cmp("AROONU_14_1h", ">", 60.0)
      _cmp_cached_431 = _cmp("STOCHRSIk_14_14_3_3_4h", ">", 30.0)
      _cmp_cached_432 = _cmp("STOCHRSIk_14_14_3_3_1h", ">", 30.0)
      _cmp_cached_433 = _cmp("STOCHRSIk_14_14_3_3_1d", ">", 20.0)
      _cmp_cached_434 = _cmp("RSI_3_15m", "<", 85.0)
      _cmp_cached_435 = _cmp("STOCHRSIk_14_14_3_3_4h", ">", 20.0)
      _cmp_cached_436 = _cmp("STOCHRSIk_14_14_3_3_1d", ">", 60.0)
      _cmp_cached_437 = _cmp("STOCHRSIk_14_14_3_3_4h", ">", 75.0)
      _cmp_cached_438 = _cmp("STOCHRSIk_14_14_3_3_15m", ">", 50.0)
      _cmp_cached_439 = _cmp("RSI_14_15m", ">", 70.0)
      _cmp_cached_440 = _cmp("STOCHRSIk_14_14_3_3_4h", ">", 40.0)
      _cmp_cached_441 = _cmp("RSI_3_15m", "<", 80.0)
      _cmp_cached_442 = _cmp("RSI_3_4h", "<", 80.0)
      _cmp_cached_443 = _cmp("RSI_3_15m", "<", 70.0)
      _cmp_cached_444 = _cmp("STOCHRSIk_14_14_3_3_15m", ">", 90.0)
      _cmp_cached_445 = _cmp("UO_7_14_28_4h", ">", 60.0)
      _cmp_cached_446 = _cmp("RSI_3_1d", "<", 95.0)
      _cmp_cached_447 = _cmp("RSI_14_4h", ">", 60.0)
      _cmp_cached_448 = _cmp("RSI_14_1d", ">", 50.0)
      _cmp_cached_449 = _cmp("MFI_14_1h", "<", 95.0)
      _cmp_cached_450 = _cmp("STOCHRSIk_14_14_3_3_1d", ">", 50.0)
      _cmp_cached_451 = _cmp("CCI_20_change_pct_15m", "<", -0.0)
      _cmp_cached_452 = _cmp("STOCHRSIk_14_14_3_3_1d", ">", 70.0)
      _cmp_cached_453 = _cmp("STOCHRSIk_14_14_3_3_1h", ">", 60.0)
      _cmp_cached_454 = _cmp("ROC_9_15m", "<", 15.0)
      _cmp_cached_455 = _cmp("ROC_9_1h", "<", 15.0)
      _cmp_cached_456 = _cmp("AROOND_14_15m", "<", 50.0)
      _cmp_cached_457 = _cmp("STOCHRSIk_14_14_3_3_15m", ">", 80.0)
      _cmp_cached_458 = _cmp("ROC_9_15m", "<", 20.0)
      _cmp_cached_459 = _cmp("AROONU_14_1h", ">", 25.0)
      _cmp_cached_460 = _cmp("AROONU_14_1d", ">", 20.0)
      _cmp_cached_461 = _cmp("RSI_3_1d", "<", 90.0)
      _cmp_cached_462 = _cmp("RSI_14_4h", ">", 80.0)
      _cmp_cached_463 = _cmp("CCI_20_change_pct_4h", "<", 0.0)
      _cmp_cached_464 = _cmp("STOCHRSIk_14_14_3_3_4h", ">", 60.0)
      _cmp_cached_465 = _cmp("AROONU_14_15m", "<", 100.0)
      _cmp_cached_466 = _cmp("CCI_20_change_pct_1h", "<", 0.0)
      _cmp_cached_467 = _cmp("change_pct", "<", 5.0)
      _cmp_cached_468 = _cmp("STOCHRSIk_14_14_3_3_15m", ">", 40.0)
      _cmp_cached_469 = _cmp("STOCHRSIk_14_14_3_3_1h", ">", 40.0)
      _cmp_cached_470 = _cmp("STOCHRSIk_14_14_3_3_1d", ">", 40.0)
      _cmp_cached_471 = _cmp("AROONU_14_4h", ">", 50.0)
      _cmp_cached_472 = _cmp("AROONU_14_1h", ">", 50.0)
      _cmp_cached_473 = _cmp("AROONU_14_1d", ">", 30.0)
      _cmp_cached_474 = _cmp("RSI_3_1h", "<", 65.0)
      _cmp_cached_475 = _cmp("RSI_3_4h", "<", 75.0)
      _cmp_cached_476 = _cmp("AROONU_14_1h", ">", 10.0)
      _cmp_cached_477 = _cmp("RSI_3_15m", "<", 75.0)
      _cmp_cached_478 = _cmp("CCI_20_change_pct_1h", "<", -0.0)
      _cmp_cached_479 = _cmp("STOCHRSIk_14_14_3_3_1d", ">", 10.0)
      _cmp_cached_480 = _cmp("RSI_3_1h", "<", 75.0)
      _cmp_cached_481 = _cmp("RSI_14_4h", ">", 40.0)
      _cmp_cached_482 = _cmp("RSI_3_1h", "<", 60.0)
      _cmp_cached_483 = _cmp("RSI_3_4h", "<", 97.0)
      _cmp_cached_484 = _cmp("AROONU_14_15m", ">", 20.0)
      _cmp_cached_485 = _cmp("AROONU_14_1h", ">", 20.0)
      _cmp_cached_486 = _cmp("RSI_14_1d", ">", 65.0)
      _cmp_cached_487 = _cmp("AROOND_14", "<", 25.0)
      _cmp_cached_488 = _cmp("STOCHRSIk_14_14_3_3", ">", 80.0)
      _cmp_cached_489 = _cmp("RSI_3", "<", 98.0)
      _cmp_cached_490 = _cmp("ROC_9", "<", 50.0)
      _cmp_cached_491 = _cmp("MFI_14", ">", 10.0)
      _cmp_cached_492 = _cmp("UO_7_14_28_1h", ">", 40.0)
      _cmp_cached_493 = _cmp("RSI_14_change_pct", "<", 40.0)
      _cmp_cached_494 = _cmp("MFI_14_4h", ">", 50.0)
      _cmp_cached_495 = _cmp("RSI_14_4h", ">", 50.0)
      _cmp_cached_496 = _cmp("RSI_3_change_pct_1h", ">", -60.0)
      _cmp_cached_497 = _cmp("RSI_3_change_pct_4h", ">", -40.0)
      _cmp_cached_498 = _cmp("MFI_14_1d", "<", 90.0)
      _cmp_cached_499 = _cmp("RSI_14_change_pct_15m", ">", -40.0)
      _cmp_cached_500 = _cmp("RSI_14_1h", ">", 30.0)
      _cmp_cached_501 = _cmp("MFI_14_15m", "<", 85.0)
      _cmp_cached_502 = _cmp("UO_7_14_28_4h", ">", 50.0)
      _cmp_cached_503 = _cmp("RSI_3_change_pct_4h", "<", 65.0)
      _cmp_cached_504 = _cmp("AROOND_14_4h", "<", 25.0)
      _cmp_cached_505 = _cmp("ROC_9_1d", ">", -120.0)
      _cmp_cached_506 = _cmp("RSI_3_change_pct_1h", ">", -65.0)
      _cmp_cached_507 = _cmp("ROC_2_1d", "<", 20.0)
      _cmp_cached_508 = _cmp("RSI_3_change_pct_1h", "<", 50.0)
      _cmp_cached_509 = _cmp("STOCHRSIk_14_14_3_3_15m", ">", 30.0)
      _cmp_cached_510 = _cmp("UO_7_14_28_4h", ">", 55.0)
      _cmp_cached_511 = _cmp("RSI_3_change_pct_1d", "<", 50.0)
      _cmp_cached_512 = _cmp("ROC_2_1d", "<", 10.0)
      _cmp_cached_513 = _cmp("STOCHRSIk_14_14_3_3_1h", ">", 5.0)
      _cmp_cached_514 = _cmp("change_pct_1h", "<", 1.0)
      _cmp_cached_515 = _cmp("change_pct_1h", "<", 5.0)
      _cmp_cached_516 = _cmp("change_pct_4h", "<", 5.0)
      _cmp_cached_517 = _cmp("ROC_9_1d", ">", -100.0)
      _cmp_cached_518 = _cmp("RSI_4", ">", 54.0)
      _cmp_cached_519 = _cmp("MFI_14_15m", "<", 90.0)
      _cmp_cached_520 = _cmp("UO_7_14_28_1h", "<", 45.0)
      _cmp_cached_521 = _cmp("RSI_14_change_pct_1h", "<", 40.0)
      _cmp_cached_522 = _cmp("RSI_3_change_pct_4h", "<", 50.0)
      _cmp_cached_523 = _cmp("MFI_14_1h", ">", 5.0)
      _cmp_cached_524 = _cmp("RSI_3_change_pct_15m", "<", 50.0)
      _cmp_cached_525 = _cmp("STOCHRSIk_14_14_3_3_4h", ">", 10.0)
      _cmp_cached_526 = _cmp("CCI_20_change_pct_1h", ">", 0.0)
      _cmp_cached_527 = _cmp("RSI_14_change_pct_1h", "<", 70.0)
      _cmp_cached_528 = _cmp("RSI_3_change_pct_1h", "<", 30.0)
      _cmp_cached_529 = _cmp("RSI_3_change_pct_15m", "<", 70.0)
      _cmp_cached_530 = _cmp("RSI_14_change_pct_4h", "<", 40.0)
      _cmp_cached_531 = _cmp("RSI_3_change_pct_4h", "<", 70.0)
      _cmp_cached_532 = _cmp("ROC_2_1d", ">", -50.0)
      _cmp_cached_533 = _cmp("MFI_14_15m", "<", 80.0)
      _cmp_cached_534 = _cmp("RSI_3_change_pct_1h", "<", 65.0)
      _cmp_cached_535 = _cmp("ROC_2_1h", "<", 5.0)
      _cmp_cached_536 = _cmp("ROC_2_1h", "<", 10.0)
      _cmp_cached_537 = _cmp("ROC_9_1h", ">", -5.0)
      _cmp_cached_538 = _cmp("ROC_9_4h", ">", -200.0)
      _cmp_cached_539 = _cmp("change_pct_1h", "<", 2.0)
      _cmp_cached_540 = _cmp("change_pct_1h", "<", 10.0)
      _cmp_cached_541 = _cmp("MFI_14_1h", ">", 50.0)
      _cmp_cached_542 = _cmp("change_pct_1h", "<", 15.0)
      _cmp_cached_543 = _cmp("RSI_14", ">", 64.0)
      _cmp_cached_544 = _cmp("AROONU_14", ">", 75.0)
      _cmp_cached_545 = _cmp("AROONU_14_15m", ">", 60.0)
      _cmp_cached_546 = _cmp("AROONU_14_15m", ">", 40.0)
      _cmp_cached_547 = _cmp("AROONU_14_4h", ">", 40.0)
      _cmp_cached_548 = _cmp("RSI_3_1h", "<", 97.0)
      _cmp_cached_549 = _cmp("ROC_9_15m", "<", 30.0)
      _cmp_cached_550 = _cmp("AROONU_14_4h", ">", 80.0)
      _cmp_cached_551 = _cmp("AROONU_14_1d", ">", 50.0)
      _cmp_cached_552 = _cmp("AROOND_14_1d", "<", 75.0)
      _cmp_cached_553 = _cmp("STOCHRSIk_14_14_3_3_15m", ">", 45.0)
      _cmp_cached_554 = _cmp("RSI_3_1d", "<", 85.0)
      _cmp_cached_555 = _cmp("bot_wick_pct_1d", "<", 30.0)
      _cmp_cached_556 = _cmp("WILLR_14", ">", -50.0)
      _cmp_cached_557 = _cmp("WILLR_84_1h", ">", -30.0)
      _cmp_cached_558 = _cmp("BBB_20_2.0_1h", ">", 20.0)
      _cmp_cached_559 = _cmp("RSI_3_change_pct_1h", "<", 60.0)
      _cmp_cached_560 = _cmp("RSI_3_change_pct_1h", "<", 40.0)
      _cmp_cached_561 = _cmp("CMF_20_1h", "<", 0.2)
      _cmp_cached_562 = _cmp("OBV_change_pct_15m", "<", 50.0)
      _cmp_cached_563 = _cmp("MFI_14_1h", "<", 90.0)
      _cmp_cached_564 = _cmp("STOCHRSIk_14_14_3_3_4h", ">", 55.0)
      _cmp_cached_565 = _cmp("ROC_9_1h", "<", 5.0)
      _cmp_cached_566 = _cmp("RSI_14", ">", 60.0)
      _cmp_cached_567 = _cmp("MFI_14", ">", 60.0)
      _cmp_cached_568 = _cmp("RSI_3", "<=", 40.0)
      _cmp_cached_569 = _cmp("RSI_3_15m", ">=", 10.0)
      _cmp_cached_570 = _cmp("RSI_3_4h", ">=", 5.0)
      _cmp_cached_571 = _cmp("RSI_14_1h", "<", 85.0)
      _cmp_cached_572 = _cmp("RSI_14_1d", "<", 85.0)
      _cmp_cached_573 = _cmp("WILLR_14", ">", -20.0)
      _cmp_cached_574 = _cmp("STOCHRSIk_14_14_3_3_4h", ">", 90.0)
      _cmp_cached_575 = _cmp("STOCHRSIk_14_14_3_3_15m", ">", 75.0)
      _cmp_cached_576 = _cmp("RSI_3_4h", "<", 15.0)
      _cmp_cached_577 = _cmp("RSI_3", ">", 70.0)
      _cmp_cached_578 = _cmp("RSI_3", "<", 85.0)
      _cmp_cached_579 = _cmp("STOCHRSIk_14_14_3_3_1h", ">", 85.0)
      _cmp_cached_580 = _cmp("STOCHRSIk_14_14_3_3_4h", ">", 85.0)
      _cmp_cached_581 = _cmp("RSI_3_4h", "<", 25.0)
      _cmp_cached_582 = _cmp("change_pct_1d", "<", 5.0)
      _cmp_cached_583 = _cmp("AROOND_14_15m", "<", 80.0)
      _cmp_cached_584 = _cmp("RSI_3_1h", "<", 40.0)
      _cmp_cached_585 = _cmp("RSI_3_15m", "<", 60.0)
      _cmp_cached_586 = _cmp("AROOND_14_1h", "<", 70.0)
      _cmp_cached_587 = _cmp("AROOND_14_4h", "<", 80.0)
      _cmp_cached_588 = _cmp("RSI_3_4h", "<", 40.0)
      _cmp_cached_589 = _cmp("RSI_3_15m", "<", 55.0)
      _cmp_cached_590 = _cmp("AROOND_14_15m", ">", 30.0)
      _cmp_cached_591 = _cmp("STOCHRSIk_14_14_3_3_15m", ">", 55.0)
      _cmp_cached_592 = _cmp("AROOND_14_4h", "<", 85.0)
      _cmp_cached_593 = _cmp("AROOND_14_1d", "<", 90.0)
      _cmp_cached_594 = _cmp("RSI_3_1h", "<", 55.0)
      _cmp_cached_595 = _cmp("AROOND_14_4h", "<", 90.0)
      _cmp_cached_596 = _cmp("RSI_3_1h", "<", 50.0)
      _cmp_cached_597 = _cmp("AROOND_14_15m", "<", 70.0)
      _cmp_cached_598 = _cmp("AROOND_14_1h", "<", 60.0)
      _cmp_cached_599 = _cmp("RSI_3", ">", 40.0)
      _cmp_cached_600 = _cmp("AROOND_14_1h", "<", 90.0)
      _cmp_cached_601 = _cmp("AROOND_14_1h", "<", 80.0)
      _cmp_cached_602 = _cmp("AROOND_14_4h", "<", 40.0)
      _cmp_cached_603 = _cmp("AROOND_14_4h", "<", 70.0)
      _cmp_cached_604 = _cmp("RSI_14_4h", ">", 30.0)
      _cmp_cached_605 = _cmp("RSI_14_1d", ">", 20.0)
      _cmp_cached_606 = _cmp("RSI_3_4h", "<", 65.0)
      _cmp_cached_607 = _cmp("RSI_3_4h", "<", 55.0)
      _cmp_cached_608 = _cmp("RSI_3_4h", "<", 50.0)
      _cmp_cached_609 = _cmp("STOCHRSIk_14_14_3_3_15m", ">", 20.0)
      _cmp_cached_610 = _cmp("RSI_14", ">", 50.0)
      _cmp_cached_611 = _cmp("AROOND_14_15m", "<", 90.0)
      _cmp_cached_612 = _cmp("STOCHRSIk_14_14_3_3_15m", ">", 10.0)
      _cmp_cached_613 = _cmp("BBB_20_2.0_1h", ">", 4.0)
      for enabled_short_entry_signal in self.short_entry_signal_params:
        short_entry_condition_index = int(enabled_short_entry_signal.rsplit("_", 2)[1])
        item_short_buy_protection_list = [True]
        if self.short_entry_signal_params[enabled_short_entry_signal]:
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

            short_entry_logic.append(_cmp_cached_378)
            short_entry_logic.append(_cmp_cached_379)
            short_entry_logic.append(_cmp_cached_380)
            short_entry_logic.append(_cmp_cached_381)
            short_entry_logic.append(_cmp_cached_382)
            short_entry_logic.append(_cmp_cached_383)
            # 5m up move, 4h still not high enough
            short_entry_logic.append((_cmp_cached_384) | (_cmp_cached_385))
            # 5m up move, 4h still low
            short_entry_logic.append((_cmp_cached_384) | (_cmp_cached_386))
            # 5m & 15m strong up move
            short_entry_logic.append((_cmp_cached_387) | (_cmp_cached_388))
            # 5m & 1h up move, 1d uptrend
            short_entry_logic.append((_cmp_cached_387) | (_cmp_cached_389) | (_cmp_cached_48))
            # 5m up move, 15m & 1h still not high enough
            short_entry_logic.append((_cmp_cached_387) | (_cmp_cached_390) | (_cmp_cached_391))
            # 4m up move, 1h & 4h still low
            short_entry_logic.append(
              (_cmp_cached_387) | (_cmp_cached_392) | (_cmp_cached_393)
            )
            # 4m & 1h up move, 1h still low
            short_entry_logic.append(
              (_cmp_cached_394) | (_cmp_cached_395) | (_cmp_cached_396)
            )
            # 15m & 1h up move, 4h low
            short_entry_logic.append((_cmp_cached_394) | (_cmp_cached_395) | (_cmp_cached_397))
            # 5m up move, 15m & 1h uptrend
            short_entry_logic.append((_cmp_cached_394) | (_cmp_cached_398) | (_cmp_cached_399))
            # 5m up move, 15m stil low
            short_entry_logic.append((_cmp_cached_394) | (_cmp_cached_400))
            # 5m up move, 15m & 1h still not high enough
            short_entry_logic.append(
              (_cmp_cached_394) | (_cmp_cached_401) | (_cmp_cached_402)
            )
            # 15m up move, 1h low
            short_entry_logic.append((_cmp_cached_403) | (_cmp_cached_404))
            # 15m & 1h up move, 4h still going up
            short_entry_logic.append(
              (_cmp_cached_388) | (_cmp_cached_405) | (_cmp_cached_406)
            )
            # 15m & 1h up move, 4h still not high enough
            short_entry_logic.append(
              (_cmp_cached_388) | (_cmp_cached_389) | (_cmp_cached_407)
            )
            # 15m & 1h up move, 4h still not high enough
            short_entry_logic.append(
              (_cmp_cached_388) | (_cmp_cached_408) | (_cmp_cached_386)
            )
            # 15m & 1h up move, 1h still low
            short_entry_logic.append(
              (_cmp_cached_388) | (_cmp_cached_409) | (_cmp_cached_396)
            )
            # 15m & 4h up move, 1h still not high enough
            short_entry_logic.append(
              (_cmp_cached_388) | (_cmp_cached_410) | (_cmp_cached_402)
            )
            # 15m up move, 1d lost, 1h low
            short_entry_logic.append((_cmp_cached_388) | (_cmp_cached_411) | (_cmp_cached_412))
            # 15m up move, 15m & 4h uptrend
            short_entry_logic.append(
              (_cmp_cached_388) | (_cmp_cached_274) | (_cmp_cached_46)
            )
            # 15m up move, 15m stil not high enough, 1h low
            short_entry_logic.append(
              (_cmp_cached_388) | (_cmp_cached_413) | (_cmp_cached_414)
            )
            # 15m up move, 1h still not high enough, 4h low
            short_entry_logic.append(
              (_cmp_cached_388) | (_cmp_cached_392) | (_cmp_cached_397)
            )
            # 15m up move, 1h & 4h still not high enough
            short_entry_logic.append(
              (_cmp_cached_388) | (_cmp_cached_392) | (_cmp_cached_407)
            )
            # 15m up move, 4h still not high enough
            short_entry_logic.append((_cmp_cached_388) | (_cmp_cached_415))
            # 15m up move, 4h & 1d uptrend
            short_entry_logic.append((_cmp_cached_388) | (_cmp_cached_51) | (_cmp_cached_107))
            # 15m up move, 1h up move, 1h still not high enough
            short_entry_logic.append(
              (_cmp_cached_388) | (_cmp_cached_416) | (_cmp_cached_396)
            )
            # 15m & 1h up move, 1h still not high enough
            short_entry_logic.append(
              (_cmp_cached_417) | (_cmp_cached_408) | (_cmp_cached_392)
            )
            # 15m & 1h up move, 1h not high enough
            short_entry_logic.append((_cmp_cached_417) | (_cmp_cached_389) | (_cmp_cached_418))
            # 15m & 1h up move, 1d stil not high enough
            short_entry_logic.append((_cmp_cached_417) | (_cmp_cached_389) | (_cmp_cached_419))
            # 15m & 1h up move, 1d uptrend
            short_entry_logic.append((_cmp_cached_417) | (_cmp_cached_395) | (_cmp_cached_52))
            # 15m & 1h up move, 15m still not high enough
            short_entry_logic.append(
              (_cmp_cached_417) | (_cmp_cached_395) | (_cmp_cached_401)
            )
            # 15m & 4h up move, 1h still not high enough
            short_entry_logic.append(
              (_cmp_cached_417) | (_cmp_cached_358) | (_cmp_cached_420)
            )
            # 15m & 4h up move, 1h still not high enough
            short_entry_logic.append(
              (_cmp_cached_417) | (_cmp_cached_358) | (_cmp_cached_421)
            )
            # 15m & 4h up move, 4h not high enough
            short_entry_logic.append((_cmp_cached_417) | (_cmp_cached_358) | (_cmp_cached_422))
            # 15m & 4h up move, 1d low
            short_entry_logic.append(
              (_cmp_cached_417) | (_cmp_cached_423) | (_cmp_cached_424)
            )
            # 15m & 4h up move, 1h low
            short_entry_logic.append(
              (_cmp_cached_417) | (_cmp_cached_425) | (_cmp_cached_426)
            )
            # 15m & 4h up move, 4h low
            short_entry_logic.append((_cmp_cached_417) | (_cmp_cached_427) | (_cmp_cached_428))
            # 15m up move, 1h & 4h low
            short_entry_logic.append(
              (_cmp_cached_417) | (_cmp_cached_412) | (_cmp_cached_429)
            )
            # 15m up move, 1h still low, 4h low
            short_entry_logic.append(
              (_cmp_cached_417) | (_cmp_cached_430) | (_cmp_cached_431)
            )
            # 15m up move, 1h low, 4h still not high enough
            short_entry_logic.append(
              (_cmp_cached_417) | (_cmp_cached_432) | (_cmp_cached_393)
            )
            # 15m & 4h up move, 1d low
            short_entry_logic.append(
              (_cmp_cached_417) | (_cmp_cached_425) | (_cmp_cached_433)
            )
            # 15m & 1h up move, 4h low
            short_entry_logic.append(
              (_cmp_cached_434) | (_cmp_cached_408) | (_cmp_cached_435)
            )
            # 15m & 1h up move, 1d still low
            short_entry_logic.append(
              (_cmp_cached_434) | (_cmp_cached_408) | (_cmp_cached_436)
            )
            # 15m & 1h up move, 1h low
            short_entry_logic.append(
              (_cmp_cached_434) | (_cmp_cached_409) | (_cmp_cached_432)
            )
            # 15m & 1h up move, 4h low
            short_entry_logic.append(
              (_cmp_cached_434) | (_cmp_cached_409) | (_cmp_cached_431)
            )
            # 15m & 4h down move, 4h still not high enough
            short_entry_logic.append(
              (_cmp_cached_434) | (_cmp_cached_358) | (_cmp_cached_437)
            )
            # 15m & 4h up move, 15m low
            short_entry_logic.append(
              (_cmp_cached_434) | (_cmp_cached_423) | (_cmp_cached_438)
            )
            # 15m down move, 15m still not high enough, 4h low
            short_entry_logic.append(
              (_cmp_cached_434) | (_cmp_cached_439) | (_cmp_cached_440)
            )
            # 15m up move, 4h overbought
            short_entry_logic.append((_cmp_cached_434) | (_cmp_cached_86))
            # 15m & 1h up move, 1h still not high enough
            short_entry_logic.append((_cmp_cached_441) | (_cmp_cached_409) | (_cmp_cached_430))
            # 15m & 4h up move, 15m still low
            short_entry_logic.append((_cmp_cached_441) | (_cmp_cached_442) | (_cmp_cached_400))
            # 15m up move, 1h low
            short_entry_logic.append((_cmp_cached_441) | (_cmp_cached_426))
            # 15m & 1h up move, 1h low
            short_entry_logic.append((_cmp_cached_443) | (_cmp_cached_409) | (_cmp_cached_404))
            # 15m up move, 15m still not high enough, 1h still low
            short_entry_logic.append(
              (_cmp_cached_443) | (_cmp_cached_444) | (_cmp_cached_396)
            )
            # 1h & 4h up move, 1h still not high enough
            short_entry_logic.append(
              (_cmp_cached_405) | (_cmp_cached_410) | (_cmp_cached_392)
            )
            # 1h up move, 4h low
            short_entry_logic.append((_cmp_cached_405) | (_cmp_cached_431))
            # 1h & 4h up move, 4h still not high enough
            short_entry_logic.append((_cmp_cached_405) | (_cmp_cached_410) | (_cmp_cached_445))
            # 1h & 4h up move, 4h still low
            short_entry_logic.append(
              (_cmp_cached_405) | (_cmp_cached_423) | (_cmp_cached_386)
            )
            # 1h & 4h up move, 4h uptrend
            short_entry_logic.append((_cmp_cached_405) | (_cmp_cached_423) | (_cmp_cached_113))
            # 1h & 1d strong up move
            short_entry_logic.append((_cmp_cached_405) | (_cmp_cached_446))
            # 1h up move, 4h still low
            short_entry_logic.append((_cmp_cached_405) | (_cmp_cached_447))
            # 1h up move, 1d still low, 1h uptrend
            short_entry_logic.append((_cmp_cached_405) | (_cmp_cached_448) | (_cmp_cached_158))
            # 1h & 4h strong up move
            short_entry_logic.append((_cmp_cached_405) | (_cmp_cached_449) | (_cmp_cached_410))
            # 1h up move, 1d still low, 1h uptrend
            short_entry_logic.append(
              (_cmp_cached_405) | (_cmp_cached_450) | (_cmp_cached_79)
            )
            # 1h strong up move, 15m still move higher
            short_entry_logic.append((_cmp_cached_405) | (_cmp_cached_451))
            # 1h & 4h up move, 1h still low
            short_entry_logic.append(
              (_cmp_cached_389) | (_cmp_cached_358) | (_cmp_cached_396)
            )
            # 1h & 4h up move, 1d still not high enough
            short_entry_logic.append(
              (_cmp_cached_389) | (_cmp_cached_358) | (_cmp_cached_452)
            )
            # 1h up move, 4h low, 1d overbought
            short_entry_logic.append((_cmp_cached_389) | (_cmp_cached_397) | (_cmp_cached_107))
            # 1h up move, 1h still low, 1d uptrend
            short_entry_logic.append(
              (_cmp_cached_389) | (_cmp_cached_453) | (_cmp_cached_107)
            )
            # 1h up move, 1h still not high enough, 1d low
            short_entry_logic.append(
              (_cmp_cached_389) | (_cmp_cached_392) | (_cmp_cached_424)
            )
            # 1h up move, 4h low, 1h uptrend
            short_entry_logic.append(
              (_cmp_cached_389) | (_cmp_cached_435) | (_cmp_cached_82)
            )
            # 1h up move, 4h low, 1h overbought
            short_entry_logic.append(
              (_cmp_cached_389) | (_cmp_cached_440) | (_cmp_cached_158)
            )
            # 1h up move, 15m & 1h uptrend
            short_entry_logic.append((_cmp_cached_389) | (_cmp_cached_454) | (_cmp_cached_455))
            # 1h up move, 15m & 4h still low
            short_entry_logic.append(
              (_cmp_cached_408) | (_cmp_cached_438) | (_cmp_cached_386)
            )
            # 1h & 4h up move, 15m still not high enough
            short_entry_logic.append((_cmp_cached_408) | (_cmp_cached_423) | (_cmp_cached_456))
            # 1h & 4h up move, 15m still not high enough
            short_entry_logic.append(
              (_cmp_cached_408) | (_cmp_cached_423) | (_cmp_cached_444)
            )
            # 1h up move, 15m still not high enough, 1h still low
            short_entry_logic.append(
              (_cmp_cached_395) | (_cmp_cached_457) | (_cmp_cached_396)
            )
            # 1h up move, 1h still low
            short_entry_logic.append((_cmp_cached_395) | (_cmp_cached_453))
            # 4h & 1d strong up move
            short_entry_logic.append((_cmp_cached_410) | (_cmp_cached_446))
            # 4h up move, 15m still low, 1h not high enough
            short_entry_logic.append(
              (_cmp_cached_410) | (_cmp_cached_438) | (_cmp_cached_391)
            )
            # 4h up move, 15m still not high enough, 4h overbought
            short_entry_logic.append(
              (_cmp_cached_410) | (_cmp_cached_413) | (_cmp_cached_83)
            )
            # 4h up move, 15m uptrend
            short_entry_logic.append((_cmp_cached_410) | (_cmp_cached_458))
            # 4h up move, 1h uptrend
            short_entry_logic.append((_cmp_cached_410) | (_cmp_cached_79))
            # 4h up move, 1h & 4h overbought
            short_entry_logic.append((_cmp_cached_410) | (_cmp_cached_158) | (_cmp_cached_83))
            # 4h up move, 1h still low
            short_entry_logic.append((_cmp_cached_358) | (_cmp_cached_412))
            # 4h up move, 1d still low, 4h uptrend
            short_entry_logic.append((_cmp_cached_423) | (_cmp_cached_411) | (_cmp_cached_20))
            # 4h up move, 4h still low
            short_entry_logic.append((_cmp_cached_442) | (_cmp_cached_386))
            # 4h up move, 1h low
            short_entry_logic.append((_cmp_cached_425) | (_cmp_cached_459))
            # 4h up move, 1d low
            short_entry_logic.append((_cmp_cached_425) | (_cmp_cached_460))
            # 4h up move, 1h low
            short_entry_logic.append((_cmp_cached_425) | (_cmp_cached_426))
            # 4h up move, 1d low
            short_entry_logic.append((_cmp_cached_425) | (_cmp_cached_433))
            # 1d up move, 1h & 4h still not low enough
            short_entry_logic.append(
              (_cmp_cached_461) | (_cmp_cached_420) | (_cmp_cached_386)
            )
            # 4h still not high enough, 4h overbought, 4h uptrend
            short_entry_logic.append(
              (_cmp_cached_462) | (_cmp_cached_113) | (_cmp_cached_463)
            )
            # 15m & 1h uptrend, 4h still low
            short_entry_logic.append(
              (_cmp_cached_398) | (_cmp_cached_399) | (_cmp_cached_464)
            )
            # 15m uptrend, 1h low
            short_entry_logic.append((_cmp_cached_465) | (_cmp_cached_426))
            # 1h & 4h uptrend
            short_entry_logic.append((_cmp_cached_80) | (_cmp_cached_6))
            # 1h uptrend, 4h uptrend
            short_entry_logic.append((_cmp_cached_80) | (_cmp_cached_20))
            # 4h uptrend, 1d uptrend
            short_entry_logic.append((_cmp_cached_6) | (_cmp_cached_27))
            # 4h uptrend, 15m uptrend
            short_entry_logic.append((_cmp_cached_6) | (_cmp_cached_226))
            # 4h uptrend, 1h uptrend
            short_entry_logic.append((_cmp_cached_6) | (_cmp_cached_79))
            # 1d uptrend, 15m uptrend
            short_entry_logic.append((_cmp_cached_27) | (_cmp_cached_458))
            # 1d uptrend, 1h uptrend
            short_entry_logic.append((_cmp_cached_27) | (_cmp_cached_79))
            # 15m still not high enough, 1h & 4h overbought
            short_entry_logic.append(
              (_cmp_cached_413) | (_cmp_cached_158) | (_cmp_cached_83)
            )
            # 1h & 4h overbought, 1h uptrend
            short_entry_logic.append(
              (_cmp_cached_82) | (_cmp_cached_113) | (_cmp_cached_466)
            )
            # 1h & 4h overbought, 4h uptrend
            short_entry_logic.append(
              (_cmp_cached_82) | (_cmp_cached_113) | (_cmp_cached_463)
            )
            # 1h & 4h & 1d uptrend
            short_entry_logic.append((_cmp_cached_82) | (_cmp_cached_50) | (_cmp_cached_167))
            # 5m green, 15m still not high enough
            short_entry_logic.append((_cmp_cached_467) | (_cmp_cached_456))
            # 5m green, 15m still not high enough
            short_entry_logic.append((_cmp_cached_467) | (_cmp_cached_444))
            # pump in the last half hour, 1h low
            short_entry_logic.append((df["close"] < (df["close_min_6"] * 1.20)) | (_cmp_cached_404))
            # pump in the last half hour, 15m still low
            short_entry_logic.append((df["close"] < (df["close_min_6"] * 1.20)) | (_cmp_cached_468))
            # pump in the last half hour, 1d uptrend
            short_entry_logic.append((df["close"] < (df["close_min_6"] * 1.20)) | (_cmp_cached_167))
            # big pump in the last 4 hours, 15m still low
            short_entry_logic.append((df["close"] < (df["close_min_48"] * 1.50)) | (_cmp_cached_400))

            # Logic
            short_entry_logic.append(df["EMA_12"] > df["EMA_26"])
            short_entry_logic.append((df["EMA_12"] - df["EMA_26"]) > (df["open"] * 0.030))
            short_entry_logic.append((df["EMA_12"].shift() - df["EMA_26"].shift()) > (df["open"] / 100.0))
            short_entry_logic.append(df["close"] > (df["BBU_20_2.0"] * 1.004))

          # Condition #502 - Normal mode (Short).
          if short_entry_condition_index == 502:
            # Protections
            short_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
            short_entry_logic.append(df["protections_short_global"] == True)

            # 5m & 15m & 1h & 4h up move
            short_entry_logic.append(
              (_cmp_cached_384) | (_cmp_cached_417) | (_cmp_cached_389) | (_cmp_cached_442)
            )
            # 5m & 4h up move
            short_entry_logic.append((_cmp_cached_384) | (_cmp_cached_410))
            # 5m up move, 4h still not high enough
            short_entry_logic.append((_cmp_cached_384) | (_cmp_cached_407))
            # 5m & 15m strong up move
            short_entry_logic.append((_cmp_cached_387) | (_cmp_cached_388))
            # 5m & 15m up move, 4h low
            short_entry_logic.append((_cmp_cached_387) | (_cmp_cached_417) | (_cmp_cached_428))
            # 5m & 1h & 4h up move
            short_entry_logic.append((_cmp_cached_387) | (_cmp_cached_389) | (_cmp_cached_358))
            # 5m & 1h up move, 15m still not high enough
            short_entry_logic.append(
              (_cmp_cached_387) | (_cmp_cached_408) | (_cmp_cached_413)
            )
            # 5m up move, 15m still low
            short_entry_logic.append((_cmp_cached_387) | (_cmp_cached_438))
            # 5m up move, 4h low
            short_entry_logic.append((_cmp_cached_394) | (_cmp_cached_397))
            # 15m & 1h down move, 4h still not high enough
            short_entry_logic.append(
              (_cmp_cached_403) | (_cmp_cached_408) | (_cmp_cached_407)
            )
            # 15m up move, 1h still low
            short_entry_logic.append((_cmp_cached_403) | (_cmp_cached_453))
            # 15m & 1h & 4h up move
            short_entry_logic.append((_cmp_cached_388) | (_cmp_cached_389) | (_cmp_cached_423))
            # 15m & 1h up move, 4h still low
            short_entry_logic.append(
              (_cmp_cached_388) | (_cmp_cached_408) | (_cmp_cached_464)
            )
            # 15m up move, 1h still low
            short_entry_logic.append((_cmp_cached_388) | (_cmp_cached_469))
            # 15m up move, 4h still not high enough
            short_entry_logic.append((_cmp_cached_388) | (_cmp_cached_415))
            # 15m & 1h & 4h up move
            short_entry_logic.append((_cmp_cached_417) | (_cmp_cached_389) | (_cmp_cached_358))
            # 15m & 1h up move, 15m still not high enough
            short_entry_logic.append(
              (_cmp_cached_417) | (_cmp_cached_389) | (_cmp_cached_457)
            )
            # 15m & 1h up move, 1d low
            short_entry_logic.append(
              (_cmp_cached_417) | (_cmp_cached_389) | (_cmp_cached_470)
            )
            # 15m & 1h up move, 1h still not high enough
            short_entry_logic.append(
              (_cmp_cached_417) | (_cmp_cached_408) | (_cmp_cached_420)
            )
            # 15m & 1h up move, 4h stil low
            short_entry_logic.append((_cmp_cached_417) | (_cmp_cached_395) | (_cmp_cached_471))
            # 15m & 4h up move, 1d low
            short_entry_logic.append((_cmp_cached_417) | (_cmp_cached_423) | (_cmp_cached_411))
            # 15m & 4h up move, 1d low
            short_entry_logic.append(
              (_cmp_cached_417) | (_cmp_cached_423) | (_cmp_cached_424)
            )
            # 15m up move, 1h still low, 1d low
            short_entry_logic.append(
              (_cmp_cached_417) | (_cmp_cached_472) | (_cmp_cached_473)
            )
            # 15m up move, 1h high
            short_entry_logic.append((_cmp_cached_417) | (_cmp_cached_80))
            # 15m up move, 1h still low
            short_entry_logic.append((_cmp_cached_417) | (_cmp_cached_396))
            # 15m up move, 4h uptrend
            short_entry_logic.append((_cmp_cached_417) | (_cmp_cached_20))
            # 15m & 1h up move, 1h still low
            short_entry_logic.append(
              (_cmp_cached_434) | (_cmp_cached_474) | (_cmp_cached_453)
            )
            # 15m up move, 1h low
            short_entry_logic.append((_cmp_cached_434) | (_cmp_cached_432))
            # 15m & 4h up move, 15m still low
            short_entry_logic.append((_cmp_cached_441) | (_cmp_cached_475) | (_cmp_cached_400))
            # 15m up move, 1h low
            short_entry_logic.append((_cmp_cached_441) | (_cmp_cached_476))
            # 15m up move, 1h low, 1d uptrend
            short_entry_logic.append((_cmp_cached_441) | (_cmp_cached_412) | (_cmp_cached_48))
            # 15m up move, 4h low
            short_entry_logic.append((_cmp_cached_441) | (_cmp_cached_440))
            # 15m up move, 1h uptrend
            short_entry_logic.append((_cmp_cached_477) | (_cmp_cached_54))
            # 1h & 1d strong up move
            short_entry_logic.append((_cmp_cached_405) | (_cmp_cached_446))
            # 1h up move, 1h still not high enough
            short_entry_logic.append((_cmp_cached_405) | (_cmp_cached_392))
            # 1h up move, 4h still low, 1h moving higher
            short_entry_logic.append(
              (_cmp_cached_405) | (_cmp_cached_464) | (_cmp_cached_478)
            )
            # 1h up move, 1d low
            short_entry_logic.append((_cmp_cached_405) | (_cmp_cached_411))
            # 1h strong up move, 15m still move higher
            short_entry_logic.append((_cmp_cached_405) | (_cmp_cached_451))
            # 1h up move, relative stable before the hour
            short_entry_logic.append((_cmp_cached_405) | (df["close_min_12"] > (df["close_min_48"] * 1.10)))
            # 1h up move, 15m uptrend
            short_entry_logic.append((_cmp_cached_389) | (_cmp_cached_465))
            # 1h up move, 1d low
            short_entry_logic.append((_cmp_cached_389) | (_cmp_cached_479))
            # 1h up move, 1h & 4h uptrend
            short_entry_logic.append((_cmp_cached_389) | (_cmp_cached_158) | (_cmp_cached_51))
            # 1h up move, 4h uptrend
            short_entry_logic.append((_cmp_cached_389) | (_cmp_cached_20))
            # 1h up move, 4h still low
            short_entry_logic.append((_cmp_cached_408) | (_cmp_cached_471))
            # 1h & 4h up move, 1d low
            short_entry_logic.append(
              (_cmp_cached_395) | (_cmp_cached_442) | (_cmp_cached_424)
            )
            # 1h up move, 1h still not high enough
            short_entry_logic.append((_cmp_cached_395) | (_cmp_cached_392))
            # 1h up move, 4h still low, 1h still moving higher
            short_entry_logic.append(
              (_cmp_cached_395) | (_cmp_cached_447) | (_cmp_cached_478)
            )
            # 1h up move, 4h low
            short_entry_logic.append((_cmp_cached_395) | (_cmp_cached_435))
            # 1h up move, 4h low
            short_entry_logic.append((_cmp_cached_395) | (_cmp_cached_429))
            # 1h up move, 1h still low
            short_entry_logic.append((_cmp_cached_480) | (_cmp_cached_396))
            # 1h up move, 4h low
            short_entry_logic.append((_cmp_cached_409) | (_cmp_cached_481))
            # 1h up move, 4h low
            short_entry_logic.append((_cmp_cached_409) | (_cmp_cached_440))
            # 1h up move, 1h uptrend
            short_entry_logic.append((_cmp_cached_409) | (_cmp_cached_54))
            # 1h up move, 1h low
            short_entry_logic.append((_cmp_cached_482) | (_cmp_cached_426))
            # 4h up move, 1d still low
            short_entry_logic.append((_cmp_cached_483) | (_cmp_cached_448))
            # 4h up move, 1h still not high enough
            short_entry_logic.append((_cmp_cached_410) | (_cmp_cached_392))
            # 4h up move, 4h still not high enough
            short_entry_logic.append((_cmp_cached_410) | (_cmp_cached_407))
            # 4h up move, 15m still not high enough, 4h moving higher
            short_entry_logic.append(
              (_cmp_cached_358) | (_cmp_cached_457) | (_cmp_cached_463)
            )
            # 4h up move, 15m still low
            short_entry_logic.append((_cmp_cached_358) | (_cmp_cached_438))
            # 4h up move, 1h still low
            short_entry_logic.append((_cmp_cached_358) | (_cmp_cached_412))
            # 4h up move, 4h still not high enough
            short_entry_logic.append((_cmp_cached_358) | (_cmp_cached_437))
            # 4h up move, 4h still not high enough
            short_entry_logic.append((_cmp_cached_423) | (_cmp_cached_393))
            # 4h up move, 1d still low, 4h uptrend
            short_entry_logic.append((_cmp_cached_423) | (_cmp_cached_448) | (_cmp_cached_20))
            # 4h up move, 4h uptrend
            short_entry_logic.append((_cmp_cached_442) | (_cmp_cached_20))
            # 4h up move, 1h low
            short_entry_logic.append((_cmp_cached_475) | (_cmp_cached_426))
            # 4h up move, 4h low
            short_entry_logic.append((_cmp_cached_425) | (_cmp_cached_440))
            # 1d up move, 1h still not high enough
            short_entry_logic.append((_cmp_cached_446) | (_cmp_cached_421))
            # 1d up move, 1h still low
            short_entry_logic.append((_cmp_cached_461) | (_cmp_cached_396))
            # 1d up move, 4h still low
            short_entry_logic.append((_cmp_cached_359) | (_cmp_cached_440))
            # 15m low, 1h still low
            short_entry_logic.append((_cmp_cached_484) | (_cmp_cached_396))
            # 15m low, 4h low
            short_entry_logic.append((_cmp_cached_484) | (_cmp_cached_435))
            # 15m still low, 1h low
            short_entry_logic.append((_cmp_cached_400) | (_cmp_cached_432))
            # 15m still not high enough, 4h low
            short_entry_logic.append((_cmp_cached_413) | (_cmp_cached_429))
            # 1h & 4h low
            short_entry_logic.append((_cmp_cached_485) | (_cmp_cached_397))
            # 1h & 4h low
            short_entry_logic.append((_cmp_cached_485) | (_cmp_cached_435))
            # 1h low, 1d low
            short_entry_logic.append((_cmp_cached_404) | (_cmp_cached_424))
            # 4h still not high enough, 4h & 1d uptrend
            short_entry_logic.append((_cmp_cached_415) | (_cmp_cached_83) | (_cmp_cached_111))
            # 1h & 4h low
            short_entry_logic.append((_cmp_cached_426) | (_cmp_cached_397))
            # 1d big green, 1d still not high enough
            short_entry_logic.append((_cmp_cached_308) | (_cmp_cached_486))
            # rise in the last hour, relatively stable before the hour
            short_entry_logic.append(
              (df["close"] < (df["close_min_12"] * 1.10)) | (df["close_min_12"] > (df["close_min_48"] * 1.10))
            )
            # big pump in the last 6 days, 4h still not high enough
            short_entry_logic.append((df["close"] < (df["low_min_6_1d"] * 4.0)) | (_cmp_cached_407))
            # big pump in the last 20 days, 1h up move
            short_entry_logic.append((df["close"] < (df["low_min_20_1d"] * 6.0)) | (_cmp_cached_389))

            # Logic
            short_entry_logic.append(_cmp_cached_487)
            short_entry_logic.append(_cmp_cached_488)
            short_entry_logic.append(df["close"] > (df["EMA_20"] * 1.060))
            short_entry_logic.append(df["close"] > (df["BBU_20_2.0"] * 0.995))
            short_entry_logic.append(_cmp_cached_390)

          # Condition #503 - Normal mode (Short).
          if short_entry_condition_index == 503:
            # Protections
            short_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)

            short_entry_logic.append(_cmp_cached_378)
            short_entry_logic.append(_cmp_cached_379)
            short_entry_logic.append(_cmp_cached_380)
            short_entry_logic.append(_cmp_cached_381)
            short_entry_logic.append(_cmp_cached_382)
            short_entry_logic.append(_cmp_cached_383)
            # 5m strong down move
            short_entry_logic.append((_cmp_cached_489) | (_cmp_cached_490))
            # 5m down move, 4h still high
            short_entry_logic.append(
              (_cmp_cached_394) | (_cmp_cached_491) | (_cmp_cached_431)
            )
            # 5m & 1h down move, 1h still high
            short_entry_logic.append(
              (_cmp_cached_394) | (_cmp_cached_389) | (_cmp_cached_392)
            )
            # 5m down move, 4h downtrend, 1h still high
            short_entry_logic.append(
              (_cmp_cached_387) | (_cmp_cached_423) | (_cmp_cached_432)
            )
            # 5m & 4h strong down move, 4h still not low enough
            short_entry_logic.append(
              (_cmp_cached_387) | (_cmp_cached_405) | (_cmp_cached_464)
            )
            # 5m down move, 1h high, 1d overbought
            short_entry_logic.append((_cmp_cached_394) | (_cmp_cached_455) | (_cmp_cached_65))
            # 5m down move, 1h & 4h high
            short_entry_logic.append(
              (_cmp_cached_394) | (_cmp_cached_492) | (_cmp_cached_431)
            )
            # 5m down move, 1h high, 4h downtrend
            short_entry_logic.append(
              (_cmp_cached_489) | (_cmp_cached_414) | (_cmp_cached_50)
            )
            # 5m & 1h down move, 4h down
            short_entry_logic.append((_cmp_cached_394) | (_cmp_cached_408) | (_cmp_cached_360))
            # 5m down move, 1h high
            short_entry_logic.append((_cmp_cached_493) | (_cmp_cached_432))
            # 5m down move, 1h high
            short_entry_logic.append((_cmp_cached_493) | (_cmp_cached_431))
            # 15m & 1h down move, 4h still high
            short_entry_logic.append(
              (_cmp_cached_388) | (_cmp_cached_408) | (_cmp_cached_386)
            )
            # 15m down move, 15m still not low enough, 1h & 4h still not low enough
            short_entry_logic.append(
              (_cmp_cached_388)
              | (_cmp_cached_390)
              | (_cmp_cached_402)
              | (_cmp_cached_494)
            )
            # 5m & 1h down move, 1h still high
            short_entry_logic.append(
              (_cmp_cached_388) | (_cmp_cached_408) | (_cmp_cached_396)
            )
            # 15m & 4h down move, 1h still not low
            short_entry_logic.append(
              (_cmp_cached_388) | (_cmp_cached_358) | (_cmp_cached_392)
            )
            # 15m & 4h down move, 4h still not low enough
            short_entry_logic.append(
              (_cmp_cached_388) | (_cmp_cached_442) | (_cmp_cached_464)
            )
            # 15m down move, 1h & 4h still high
            short_entry_logic.append(
              (_cmp_cached_388) | (_cmp_cached_396) | (_cmp_cached_495)
            )
            # 15m & 1h & 4h down move
            short_entry_logic.append(
              (_cmp_cached_417) | (_cmp_cached_496) | (_cmp_cached_497)
            )
            # 15m down move, 1d downtrend, 1h still high
            short_entry_logic.append(
              (_cmp_cached_417) | (_cmp_cached_195) | (_cmp_cached_432)
            )
            # 15m & 1d down move, 1h still high
            short_entry_logic.append(
              (_cmp_cached_417) | (_cmp_cached_461) | (_cmp_cached_432)
            )
            # 15m & 4h down move, 1h still high
            short_entry_logic.append(
              (_cmp_cached_417) | (_cmp_cached_410) | (_cmp_cached_396)
            )
            # 15m down move, 15m still not low enough, 4h down move
            short_entry_logic.append((_cmp_cached_417) | (_cmp_cached_456) | (_cmp_cached_423))
            # 15m down move, 1h still high, 1d strong downtrend
            short_entry_logic.append((_cmp_cached_441) | (_cmp_cached_391) | (_cmp_cached_498))
            # 15m down move, 1h still high, 1d downtrend
            short_entry_logic.append(
              (_cmp_cached_434) | (_cmp_cached_432) | (_cmp_cached_107)
            )
            # 15m down move, 4h still high, 1d downtrend
            short_entry_logic.append(
              (_cmp_cached_434) | (_cmp_cached_431) | (_cmp_cached_107)
            )
            # 15m & 4h down move, 1d downtrend
            short_entry_logic.append((_cmp_cached_434) | (_cmp_cached_423) | (_cmp_cached_206))
            # 15m down move, 15m not low enough, 1h overbought
            short_entry_logic.append(
              (_cmp_cached_499) | (_cmp_cached_444) | (_cmp_cached_500)
            )
            # 15m strong down move, 1h still high
            short_entry_logic.append((_cmp_cached_454) | (_cmp_cached_396))
            # 15m downtrend, 1h & 4h still high
            short_entry_logic.append(
              (_cmp_cached_226) | (_cmp_cached_396) | (_cmp_cached_386)
            )
            # 15m & 1h & 4h down move
            short_entry_logic.append(
              (_cmp_cached_388) | (_cmp_cached_405) | (_cmp_cached_463)
            )
            # 15m strong down move
            short_entry_logic.append((_cmp_cached_417) | (_cmp_cached_501) | (_cmp_cached_390))
            # 14m down move, 4h still high
            short_entry_logic.append(
              (_cmp_cached_441) | (_cmp_cached_456) | (_cmp_cached_502)
            )
            # 15m down move, 1h stil high, 1d overbought
            short_entry_logic.append((_cmp_cached_434) | (_cmp_cached_391) | (_cmp_cached_218))
            # 15m down move, 1h high, 1d overbought
            short_entry_logic.append(
              (_cmp_cached_417) | (_cmp_cached_432) | (_cmp_cached_42)
            )
            # 1h & 4h down move, 4h still high
            short_entry_logic.append(
              (_cmp_cached_389) | (_cmp_cached_503) | (_cmp_cached_386)
            )
            # 1h & 4h down move, 4h still high
            short_entry_logic.append(
              (_cmp_cached_389) | (_cmp_cached_423) | (_cmp_cached_332)
            )
            # 1h down move, 4h still not low enough, 1d overbought
            short_entry_logic.append((_cmp_cached_389) | (_cmp_cached_504) | (_cmp_cached_505))
            # 1h down move, 1h still not low enough, 4h still not low
            short_entry_logic.append(
              (_cmp_cached_389) | (_cmp_cached_392) | (_cmp_cached_495)
            )
            # 1h down move, 4h still high
            short_entry_logic.append((_cmp_cached_405) | (_cmp_cached_447))
            # 1h down move, 4h still high, 1d downtrend
            short_entry_logic.append(
              (_cmp_cached_395) | (_cmp_cached_431) | (_cmp_cached_107)
            )
            # 1h down move, 4h still high, 1d downtrend
            short_entry_logic.append(
              (_cmp_cached_506) | (_cmp_cached_431) | (_cmp_cached_107)
            )
            # 4h & 1d down move, 1h still high
            short_entry_logic.append(
              (_cmp_cached_358) | (_cmp_cached_507) | (_cmp_cached_396)
            )
            # 15m still high, 1h down move, 4h high
            short_entry_logic.append(
              (_cmp_cached_456) | (_cmp_cached_508) | (_cmp_cached_431)
            )
            # 15m still high, 1h & 4h down move, 4h still high
            short_entry_logic.append(
              (_cmp_cached_456)
              | (_cmp_cached_408)
              | (_cmp_cached_442)
              | (_cmp_cached_407)
            )
            # 15m & 1h still high, 4h overbought
            short_entry_logic.append(
              (_cmp_cached_456) | (_cmp_cached_418) | (_cmp_cached_213)
            )
            # 15m still high, 1h down move, 1d downtrend
            short_entry_logic.append(
              (_cmp_cached_509) | (_cmp_cached_358) | (_cmp_cached_107)
            )
            # 1h & 4h still high, 1d strong down move
            short_entry_logic.append(
              (_cmp_cached_396) | (_cmp_cached_510) | (_cmp_cached_461)
            )
            # 1h still high, 4h & 1d downtrend
            short_entry_logic.append((_cmp_cached_391) | (_cmp_cached_20) | (_cmp_cached_107))
            # 4h moving down, 1d P&D
            short_entry_logic.append(
              (_cmp_cached_51) | (_cmp_cached_511) | (_cmp_cached_42)
            )
            # 1d strong downtrend, 4h still high
            short_entry_logic.append(
              (_cmp_cached_507) | (_cmp_cached_107) | (_cmp_cached_393)
            )
            # 1d P&D, 1d overbought
            short_entry_logic.append(
              (_cmp_cached_512) | (_cmp_cached_42) | (_cmp_cached_513)
            )
            # 1h red, previous 1h green, 1h overbought
            short_entry_logic.append(
              (_cmp_cached_514) | (df["change_pct_1h"].shift(12) > -5.0) | (df["RSI_14_1h"].shift(12) < 80.0)
            )
            # 1h red, 1h stil high, 4h downtrend
            short_entry_logic.append(
              (_cmp_cached_515) | (_cmp_cached_396) | (_cmp_cached_81)
            )
            # 4h red, 15m down move, 4h still high
            short_entry_logic.append(
              (_cmp_cached_516) | (_cmp_cached_417) | (_cmp_cached_431)
            )
            # 4h red, previous 4h green, 4h overbought
            short_entry_logic.append(
              (_cmp_cached_516) | (df["change_pct_4h"].shift(48) > -5.0) | (df["ROC_9_4h"].shift(48) > -25.0)
            )
            # 4h red, 4h still not low enough, 1h downtrend, 1h overbought
            short_entry_logic.append(
              (_cmp_cached_349)
              | (_cmp_cached_504)
              | (_cmp_cached_79)
              | (_cmp_cached_65)
            )
            # 4h red, 4h still high, 1d downtrend
            short_entry_logic.append(
              (_cmp_cached_349) | (_cmp_cached_431) | (_cmp_cached_52)
            )
            # 1d P&D, 1d overbought
            short_entry_logic.append(
              (_cmp_cached_352) | (df["change_pct_1d"].shift(288) > -10.0) | (_cmp_cached_517)
            )
            # 1d P&D, 4h still high
            short_entry_logic.append(
              (_cmp_cached_232) | (df["change_pct_1d"].shift(288) > -15.0) | (_cmp_cached_422)
            )
            short_entry_logic.append(
              (_cmp_cached_389) | (_cmp_cached_410) | (_cmp_cached_463)
            )

            # Logic
            short_entry_logic.append(df["RSI_20"] > df["RSI_20"].shift(1))
            short_entry_logic.append(_cmp_cached_518)
            short_entry_logic.append(_cmp_cached_487)
            short_entry_logic.append(df["close"] > df["SMA_16"] * 1.058)

          # Condition #504 - Normal mode (Short).
          if short_entry_condition_index == 504:
            # Protections
            short_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)

            short_entry_logic.append(_cmp_cached_378)
            short_entry_logic.append(_cmp_cached_379)
            short_entry_logic.append(_cmp_cached_380)
            short_entry_logic.append(_cmp_cached_381)
            short_entry_logic.append(_cmp_cached_382)
            short_entry_logic.append(_cmp_cached_383)
            # 15m & 1h down move, 4h still high
            short_entry_logic.append(
              (_cmp_cached_388)
              | (_cmp_cached_519)
              | (_cmp_cached_395)
              | (_cmp_cached_386)
            )
            # 15m & 1h down move, 4h still high
            short_entry_logic.append(
              (_cmp_cached_417) | (_cmp_cached_501) | (_cmp_cached_431)
            )
            # 14m & 4h down move, 4h still high
            short_entry_logic.append(
              (_cmp_cached_417) | (_cmp_cached_423) | (_cmp_cached_464)
            )
            # 15m down move, 1h & 4h still high
            short_entry_logic.append(
              (_cmp_cached_417) | (_cmp_cached_520) | (_cmp_cached_431)
            )
            # 1h strong down move, 4h still high
            short_entry_logic.append(
              (_cmp_cached_405) | (_cmp_cached_521) | (_cmp_cached_431)
            )
            # 1h strong down move, 4h down move, 4h still high
            short_entry_logic.append(
              (_cmp_cached_405) | (_cmp_cached_522) | (_cmp_cached_386)
            )
            # 1h & 4h down move, 4h still not low enough
            short_entry_logic.append(
              (_cmp_cached_405) | (_cmp_cached_358) | (_cmp_cached_437)
            )
            # 1h & 4h down move, 4h still not low enough
            short_entry_logic.append((_cmp_cached_405) | (_cmp_cached_475) | (_cmp_cached_422))
            # 15m down move, 1h strong downtrend
            short_entry_logic.append((_cmp_cached_388) | (_cmp_cached_405) | (_cmp_cached_523))
            # 15m downtrend, 4h down move, 4h stil high
            short_entry_logic.append(
              (_cmp_cached_44) | (_cmp_cached_475) | (_cmp_cached_431)
            )

            # Logic
            short_entry_logic.append(_cmp_cached_487)
            short_entry_logic.append(_cmp_cached_390)
            short_entry_logic.append(df["close"] > (df["EMA_9"] * 1.058))
            short_entry_logic.append(df["close"] > (df["EMA_20"] * 1.040))

          # Condition #541 - Quick mode (Short).
          if short_entry_condition_index == 541:
            # Protections
            short_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)

            # 5m & 15m down move, 4h still high
            short_entry_logic.append(
              (_cmp_cached_387) | (_cmp_cached_524) | (_cmp_cached_495)
            )
            # 5m & 15m & 1h down move
            short_entry_logic.append((_cmp_cached_387) | (_cmp_cached_388) | (_cmp_cached_405))
            # 5m strong down move
            short_entry_logic.append((_cmp_cached_489) | (_cmp_cached_490))
            # 15m & 1h strong down move & downtrend
            short_entry_logic.append((_cmp_cached_388) | (_cmp_cached_405) | (_cmp_cached_523))
            # 15m strong down move, 4h high
            short_entry_logic.append((_cmp_cached_388) | (_cmp_cached_525))
            # 15m & 1h down move
            short_entry_logic.append(
              (_cmp_cached_388) | (_cmp_cached_405) | (_cmp_cached_526)
            )
            # 15m & 1h down move, 4h high
            short_entry_logic.append(
              (_cmp_cached_388) | (_cmp_cached_408) | (_cmp_cached_431)
            )
            # 15m & 1h down move, 4h still high
            short_entry_logic.append(
              (_cmp_cached_388) | (_cmp_cached_508) | (_cmp_cached_494)
            )
            # 15m strong down move, 1h still high
            short_entry_logic.append(
              (_cmp_cached_388) | (_cmp_cached_519) | (_cmp_cached_396)
            )
            # 15m & 1h down move, 1h not low enough
            short_entry_logic.append(
              (_cmp_cached_388) | (_cmp_cached_405) | (_cmp_cached_420)
            )
            # 15m down move, 1h strong down move
            short_entry_logic.append((_cmp_cached_388) | (_cmp_cached_527))
            # 15m down move, 4h & 1d downtrend
            short_entry_logic.append((_cmp_cached_388) | (_cmp_cached_51) | (_cmp_cached_107))
            # 15m down move, 1h strong down move, 4h stil high
            short_entry_logic.append(
              (_cmp_cached_417) | (_cmp_cached_405) | (_cmp_cached_386)
            )
            # 15m down move, 1h & 4h still high
            short_entry_logic.append(
              (_cmp_cached_434) | (_cmp_cached_396) | (_cmp_cached_386)
            )
            # 15m down move, 1h downtrend, 4h still high
            short_entry_logic.append(
              (_cmp_cached_417) | (_cmp_cached_79) | (_cmp_cached_386)
            )
            # 15m & 1h down move, 4h high
            short_entry_logic.append(
              (_cmp_cached_417) | (_cmp_cached_408) | (_cmp_cached_431)
            )
            # 15m down move, 1h down move, 4h high
            short_entry_logic.append(
              (_cmp_cached_434) | (_cmp_cached_528) | (_cmp_cached_525)
            )
            # 1m down move, 1h still dropping, 4h overbought
            short_entry_logic.append(
              (_cmp_cached_417) | (_cmp_cached_466) | (_cmp_cached_382)
            )
            # 15m down move, 1h high
            short_entry_logic.append((_cmp_cached_529) | (_cmp_cached_414))
            # 1h strong down move, 4h high
            short_entry_logic.append((_cmp_cached_405) | (_cmp_cached_525))
            # 1h down move, 4h downtrend, 4h not low enough
            short_entry_logic.append(
              (_cmp_cached_405) | (_cmp_cached_252) | (_cmp_cached_393)
            )
            # 1h down move, 4h high, 1d overbought
            short_entry_logic.append((_cmp_cached_389) | (_cmp_cached_481) | (_cmp_cached_42))
            # 1h down move, 4h strong down move
            short_entry_logic.append((_cmp_cached_405) | (_cmp_cached_530))
            # 1h & 4h down move, 4h still going down
            short_entry_logic.append(
              (_cmp_cached_405) | (_cmp_cached_410) | (_cmp_cached_463)
            )
            # 1h & 4h down move, 4h still not low enough
            short_entry_logic.append(
              (_cmp_cached_405) | (_cmp_cached_503) | (_cmp_cached_393)
            )
            # 1h down move, 4h down move, 4h P&D
            short_entry_logic.append(
              (_cmp_cached_389) | (_cmp_cached_531) | (df["RSI_14_4h"].shift(48) > 30.0)
            )
            # 1h & 4h down move, 4h still not low enough, 1d still high
            short_entry_logic.append(
              (_cmp_cached_389)
              | (_cmp_cached_522)
              | (_cmp_cached_504)
              | (_cmp_cached_436)
            )
            # 1h down move, 1h still high, 1d going down
            short_entry_logic.append(
              (_cmp_cached_408) | (_cmp_cached_396) | (_cmp_cached_532)
            )
            # 4h downtrend, 4h still high, 1d strong downtrend
            short_entry_logic.append(
              (_cmp_cached_423) | (_cmp_cached_393) | (_cmp_cached_112)
            )
            # 15m down move, 1h strong down move, 1d overbought
            short_entry_logic.append(
              (_cmp_cached_533) | (_cmp_cached_416) | (_cmp_cached_42)
            )
            # 1h not low enough, 4h high, 1d strong downtrend
            short_entry_logic.append(
              (_cmp_cached_392) | (_cmp_cached_525) | (_cmp_cached_112)
            )
            # 1h down move, 4h still high, 1d downtrend
            short_entry_logic.append(
              (_cmp_cached_534) | (_cmp_cached_431) | (_cmp_cached_107)
            )
            # 15m strong down move, 1h still high
            short_entry_logic.append((_cmp_cached_454) | (_cmp_cached_432))
            # 15m downtrend, 4h down move, 4h stil high
            short_entry_logic.append(
              (_cmp_cached_454) | (_cmp_cached_475) | (_cmp_cached_431)
            )
            # 1h downtrend, 4h overbought
            short_entry_logic.append((_cmp_cached_535) | (_cmp_cached_382) | (_cmp_cached_81))
            # 1h P&D, 4h still high
            short_entry_logic.append(
              (_cmp_cached_536) | (_cmp_cached_537) | (_cmp_cached_431)
            )
            # 1h downtrend, 4h down move, 1d downtrend
            short_entry_logic.append((_cmp_cached_54) | (_cmp_cached_358) | (_cmp_cached_107))
            short_entry_logic.append((_cmp_cached_538) | (_cmp_cached_382))
            # 4h down move, 1d P&D
            short_entry_logic.append((_cmp_cached_20) | (_cmp_cached_507) | (_cmp_cached_42))
            # 1h P&D, 4h overbought
            short_entry_logic.append(
              (_cmp_cached_539) | (df["change_pct_1h"].shift(12) > 2.0) | (_cmp_cached_382)
            )
            # 1h P&D, 1d overbought
            short_entry_logic.append(
              (_cmp_cached_515) | (df["change_pct_1h"].shift(12) > -5.0) | (_cmp_cached_517)
            )
            # 1h & 4h red, 1h not low enough
            short_entry_logic.append(
              (_cmp_cached_540) | (_cmp_cached_349) | (_cmp_cached_541)
            )
            # 1h red, 1h still not low enough, 1d down move
            short_entry_logic.append((_cmp_cached_542) | (_cmp_cached_541) | (_cmp_cached_461))
            # 4h red, previous 4h green, 4h overbought
            short_entry_logic.append(
              (_cmp_cached_516) | (df["change_pct_4h"].shift(48) > -5.0) | (df["RSI_14_4h"].shift(48) > 20.0)
            )
            # 1d P&D, 1d overbought
            short_entry_logic.append(
              (_cmp_cached_352) | (df["change_pct_1d"].shift(288) > -10.0) | (_cmp_cached_517)
            )
            # 1d P&D, 4h still high
            short_entry_logic.append(
              (_cmp_cached_232) | (df["change_pct_1d"].shift(288) > -15.0) | (_cmp_cached_422)
            )

            # Logic
            short_entry_logic.append(_cmp_cached_543)
            short_entry_logic.append(_cmp_cached_487)
            short_entry_logic.append(_cmp_cached_544)
            short_entry_logic.append(df["EMA_9"] > (df["EMA_26"] * 1.040))

          # Condition #542 - Quick mode (Short).
          if short_entry_condition_index == 542:
            # Protections
            short_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)
            short_entry_logic.append(df["protections_short_global"] == True)

            # 5m & 15m up move, 15m stil low
            short_entry_logic.append((_cmp_cached_394) | (_cmp_cached_441) | (_cmp_cached_545))
            # 15m & 1h up move, 4h still low
            short_entry_logic.append((_cmp_cached_388) | (_cmp_cached_405) | (_cmp_cached_447))
            # 15m & 1h up move, 4h still not high enough
            short_entry_logic.append(
              (_cmp_cached_388) | (_cmp_cached_405) | (_cmp_cached_407)
            )
            # 15m & 1h up move, 1h still moving higher
            short_entry_logic.append(
              (_cmp_cached_388) | (_cmp_cached_389) | (_cmp_cached_478)
            )
            # 15m & 4h up move, 4h still moving higher
            short_entry_logic.append(
              (_cmp_cached_417) | (_cmp_cached_410) | (_cmp_cached_406)
            )
            # 15m & 1d up move, 4h uptrend
            short_entry_logic.append((_cmp_cached_417) | (_cmp_cached_359) | (_cmp_cached_20))
            # 15m up move, 15m & 4h high
            short_entry_logic.append(
              (_cmp_cached_417) | (_cmp_cached_465) | (_cmp_cached_6)
            )
            # 15m up move, 15m still not high enough, 1d uptrend
            short_entry_logic.append(
              (_cmp_cached_417) | (_cmp_cached_457) | (_cmp_cached_63)
            )
            # 15m & 4h up move, 15m still not high enough
            short_entry_logic.append(
              (_cmp_cached_434) | (_cmp_cached_358) | (_cmp_cached_413)
            )
            # 15m & 4h up move, 1d uptrend
            short_entry_logic.append((_cmp_cached_434) | (_cmp_cached_423) | (_cmp_cached_107))
            # 15m & 4h up move, 4h still not high enough
            short_entry_logic.append((_cmp_cached_434) | (_cmp_cached_442) | (_cmp_cached_447))
            # 15m up move, 15m still not high enough, 4h still low
            short_entry_logic.append(
              (_cmp_cached_434) | (_cmp_cached_457) | (_cmp_cached_471)
            )
            # 15m up move, 4h overbought
            short_entry_logic.append((_cmp_cached_434) | (_cmp_cached_86))
            # 15m & 1h up move, 15m still low
            short_entry_logic.append((_cmp_cached_443) | (_cmp_cached_409) | (_cmp_cached_546))
            # 15m & 1h up move, 15m still low
            short_entry_logic.append(
              (_cmp_cached_443) | (_cmp_cached_409) | (_cmp_cached_468)
            )
            # # 15m & 1h up move, 4h low
            short_entry_logic.append((_cmp_cached_443) | (_cmp_cached_482) | (_cmp_cached_547))
            # 1h & 1d up move, 1h still moving higher
            short_entry_logic.append(
              (_cmp_cached_548) | (_cmp_cached_446) | (_cmp_cached_478)
            )
            # 1h & 4h up move, 15m still not high enough
            short_entry_logic.append(
              (_cmp_cached_405) | (_cmp_cached_410) | (_cmp_cached_457)
            )
            # 1h & 4h up move, 1d uptrend
            short_entry_logic.append((_cmp_cached_405) | (_cmp_cached_410) | (_cmp_cached_48))
            # 1h & 4h up move, 1d still low
            short_entry_logic.append((_cmp_cached_405) | (_cmp_cached_423) | (_cmp_cached_448))
            # 1h up move, 4h still low, 1h still moving higher
            short_entry_logic.append(
              (_cmp_cached_405) | (_cmp_cached_447) | (_cmp_cached_478)
            )
            # 1h up move, 4h low
            short_entry_logic.append((_cmp_cached_405) | (_cmp_cached_429))
            # 1h & 4h up move, 1h still moving higher
            short_entry_logic.append(
              (_cmp_cached_389) | (_cmp_cached_423) | (_cmp_cached_478)
            )
            # 1h & 4h up move, 4h still not high enough
            short_entry_logic.append(
              (_cmp_cached_389) | (_cmp_cached_425) | (_cmp_cached_407)
            )
            # 1h & 1d up move, 15m still low
            short_entry_logic.append(
              (_cmp_cached_389) | (_cmp_cached_461) | (_cmp_cached_401)
            )
            # 1h up move, 15m high
            short_entry_logic.append((_cmp_cached_389) | (_cmp_cached_465))
            # 1h up move, 4h low
            short_entry_logic.append((_cmp_cached_389) | (_cmp_cached_431))
            # 1h up move, 4h still low, 1h still moving higher
            short_entry_logic.append(
              (_cmp_cached_389) | (_cmp_cached_464) | (_cmp_cached_478)
            )
            # 1h up move, 15m uptrend
            short_entry_logic.append((_cmp_cached_389) | (_cmp_cached_549))
            # 1h up move, 15m & 4h uptrend
            short_entry_logic.append((_cmp_cached_389) | (_cmp_cached_458) | (_cmp_cached_20))
            # 1h & 4h up move, 4h still moving higher
            short_entry_logic.append(
              (_cmp_cached_408) | (_cmp_cached_442) | (_cmp_cached_406)
            )
            # 1h up move, 15m low
            short_entry_logic.append((_cmp_cached_408) | (_cmp_cached_546))
            # 1h up move, 4h still not high enough, 1d low
            short_entry_logic.append((_cmp_cached_408) | (_cmp_cached_550) | (_cmp_cached_411))
            # 1h & 4h up move, 4h still low
            short_entry_logic.append((_cmp_cached_395) | (_cmp_cached_442) | (_cmp_cached_471))
            # 1h & 4h up move, 1d still low
            short_entry_logic.append((_cmp_cached_395) | (_cmp_cached_442) | (_cmp_cached_551))
            # 1h & 4h up move, 1d low
            short_entry_logic.append(
              (_cmp_cached_395) | (_cmp_cached_425) | (_cmp_cached_424)
            )
            # 1h up move, 1d still low, 1d uptrend
            short_entry_logic.append((_cmp_cached_395) | (_cmp_cached_551) | (_cmp_cached_70))
            # 1h up move, 1d low
            short_entry_logic.append((_cmp_cached_395) | (_cmp_cached_433))
            # 1h up move, 4h & 1d uptrend
            short_entry_logic.append((_cmp_cached_395) | (_cmp_cached_20) | (_cmp_cached_52))
            # 4h up move, 1d low
            short_entry_logic.append((_cmp_cached_410) | (_cmp_cached_411))
            # 4h down move, 15m still not high enough, 1d low
            short_entry_logic.append(
              (_cmp_cached_410) | (_cmp_cached_457) | (_cmp_cached_552)
            )
            # 4h up move, 1h & 4h uptrend
            short_entry_logic.append((_cmp_cached_410) | (_cmp_cached_79) | (_cmp_cached_20))
            # 4h up move, 15m low
            short_entry_logic.append((_cmp_cached_358) | (_cmp_cached_553))
            # 4h up move, 4h & 1d uptrend
            short_entry_logic.append((_cmp_cached_358) | (_cmp_cached_20) | (_cmp_cached_52))
            # 4h up move, 15m still not high enough
            short_entry_logic.append((_cmp_cached_423) | (_cmp_cached_545))
            # 4h up move, 15m low
            short_entry_logic.append((_cmp_cached_423) | (_cmp_cached_509))
            # 4h up move, 4h uptrend
            short_entry_logic.append((_cmp_cached_442) | (_cmp_cached_6) | (_cmp_cached_20))
            # 4h up move, 15m still low, 4h still not high enough
            short_entry_logic.append(
              (_cmp_cached_442) | (_cmp_cached_401) | (_cmp_cached_550)
            )
            # 4h up move, 15m still low, 4h still not high enough
            short_entry_logic.append(
              (_cmp_cached_475) | (_cmp_cached_401) | (_cmp_cached_407)
            )
            # 1d up move, 4h low
            short_entry_logic.append((_cmp_cached_554) | (_cmp_cached_440))
            # 4h still not high enough, 4h overbought, 4h uptrend
            short_entry_logic.append(
              (_cmp_cached_462) | (_cmp_cached_113) | (_cmp_cached_463)
            )
            # 15m & 1h high, 4h uptrend
            short_entry_logic.append(
              (_cmp_cached_465) | (_cmp_cached_80) | (_cmp_cached_20)
            )
            # 15m & 4h high, 1h uptrend
            short_entry_logic.append(
              (_cmp_cached_465) | (_cmp_cached_6) | (_cmp_cached_79)
            )
            # 15m high, 1d low
            short_entry_logic.append((_cmp_cached_465) | (_cmp_cached_433))
            # 15m high & uptrend
            short_entry_logic.append((_cmp_cached_465) | (_cmp_cached_549))
            # 15m high, 1h & 4h uptrend
            short_entry_logic.append((_cmp_cached_465) | (_cmp_cached_79) | (_cmp_cached_20))
            # 1h high, 15m uptrend
            short_entry_logic.append((_cmp_cached_80) | (_cmp_cached_458))
            # 15m & 4h still not high enough
            short_entry_logic.append((_cmp_cached_413) | (_cmp_cached_393))
            # 1h & 4h overbought, 1h uptrend
            short_entry_logic.append(
              (_cmp_cached_82) | (_cmp_cached_113) | (_cmp_cached_466)
            )
            # 1h & 4h overbought, 4h uptrend
            short_entry_logic.append(
              (_cmp_cached_82) | (_cmp_cached_113) | (_cmp_cached_463)
            )
            # 1d bot wick, 4h still not high enough
            short_entry_logic.append((_cmp_cached_555) | (_cmp_cached_407))
            # rise in the last 12 hours, relatively stable before the 12 hours
            short_entry_logic.append(
              (df["close"] < (df["low_min_12_1h"] * 1.30)) | (df["low_min_12_1h"] > (df["low_min_24_1h"] * 1.10))
            )
            # big pump in the last 30 days, 4h up move
            short_entry_logic.append((df["close"] < (df["low_min_30_1d"] * 4.0)) | (_cmp_cached_423))

            # Logic
            short_entry_logic.append(_cmp_cached_556)
            short_entry_logic.append(_cmp_cached_544)
            short_entry_logic.append(_cmp_cached_487)
            short_entry_logic.append(_cmp_cached_488)
            short_entry_logic.append(_cmp_cached_557)
            short_entry_logic.append(_cmp_cached_420)
            short_entry_logic.append(_cmp_cached_558)
            short_entry_logic.append(df["close_min_48"] <= (df["close"] * 0.90))

          # Condition #543 - Rapid mode (Short).
          if short_entry_condition_index == 543:
            # Protections
            short_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)

            short_entry_logic.append(_cmp_cached_381)
            short_entry_logic.append(_cmp_cached_382)
            short_entry_logic.append(_cmp_cached_383)
            # 5m strong down move
            short_entry_logic.append((_cmp_cached_489) | (_cmp_cached_490))
            # 15m down move, 1h down move, 1h still not low enough
            short_entry_logic.append(
              (_cmp_cached_388) | (_cmp_cached_559) | (_cmp_cached_396)
            )
            # 15m down move, 1h down move, 4h still not low enough
            short_entry_logic.append(
              (_cmp_cached_388) | (_cmp_cached_560) | (_cmp_cached_431)
            )
            # 5m down move, 1h down, 4h high
            short_entry_logic.append(
              (_cmp_cached_388) | (_cmp_cached_561) | (_cmp_cached_386)
            )
            # 15m down move, 1h still not low enough, 4h high
            short_entry_logic.append(
              (_cmp_cached_388) | (_cmp_cached_391) | (_cmp_cached_525)
            )
            # 15m down move, 1h still high
            short_entry_logic.append(
              (_cmp_cached_417) | (_cmp_cached_562) | (_cmp_cached_432)
            )
            # 5m & 1h strong down move, 1h still not low enough
            short_entry_logic.append(
              (_cmp_cached_388) | (_cmp_cached_405) | (_cmp_cached_392)
            )
            # 5m & 1h strong downtrend
            short_entry_logic.append((_cmp_cached_388) | (_cmp_cached_405) | (_cmp_cached_563))
            # 15m & 1h down move, 4h still high
            short_entry_logic.append(
              (_cmp_cached_388)
              | (_cmp_cached_395)
              | (_cmp_cached_393)
              | (_cmp_cached_422)
            )
            # 15m & 1h down move, 4h still high, 4h downtrend
            short_entry_logic.append(
              (_cmp_cached_388) | (_cmp_cached_389) | (_cmp_cached_445) | (_cmp_cached_20)
            )
            # 15m & 1h down move, 1d strong downtrend
            short_entry_logic.append((_cmp_cached_388) | (_cmp_cached_389) | (_cmp_cached_107))
            # 15m & 4h down move, 4h still not low enough
            short_entry_logic.append(
              (_cmp_cached_417) | (_cmp_cached_423) | (_cmp_cached_564)
            )
            # 15m down move, 15m still not low enough, 1h still high
            short_entry_logic.append(
              (_cmp_cached_434) | (_cmp_cached_438) | (_cmp_cached_432)
            )
            # 15m & 1h down move, 1h still high
            short_entry_logic.append(
              (_cmp_cached_434) | (_cmp_cached_480) | (_cmp_cached_432)
            )
            # 15m down move, 15m still not low enoug, 1h high
            short_entry_logic.append(
              (_cmp_cached_434) | (_cmp_cached_390) | (_cmp_cached_414)
            )
            # 15m down move, 1h downtrend, 4h overbought
            short_entry_logic.append((_cmp_cached_434) | (_cmp_cached_565) | (_cmp_cached_266))
            # 1h & 4h down move, 4h still not low enough
            short_entry_logic.append(
              (_cmp_cached_405) | (_cmp_cached_358) | (_cmp_cached_437)
            )
            # 1h & 4h down move, 4h still high
            short_entry_logic.append(
              (_cmp_cached_405) | (_cmp_cached_522) | (_cmp_cached_386)
            )
            # 1h & 4h down move, 4h still not low enough
            short_entry_logic.append(
              (_cmp_cached_405) | (_cmp_cached_503) | (_cmp_cached_393)
            )
            # 1h down move, 1h still not low enough, 4h still not low
            short_entry_logic.append(
              (_cmp_cached_389) | (_cmp_cached_392) | (_cmp_cached_495)
            )
            # 1h down move, 1h not low enough, 1h still high
            short_entry_logic.append(
              (_cmp_cached_408) | (_cmp_cached_418) | (_cmp_cached_386)
            )
            # 4h down move, 15m still not low enough, 1h still high
            short_entry_logic.append(
              (_cmp_cached_442) | (_cmp_cached_413) | (_cmp_cached_432)
            )
            # 4h down move, 4h still high, 1d downtrend
            short_entry_logic.append(
              (_cmp_cached_475) | (_cmp_cached_386) | (_cmp_cached_107)
            )
            # 4h & 1d down move, 1d strong downtrend
            short_entry_logic.append((_cmp_cached_358) | (_cmp_cached_461) | (_cmp_cached_112))
            # 4h overbought, 1h still high, 1d downtrend
            short_entry_logic.append(
              (_cmp_cached_204) | (_cmp_cached_392) | (_cmp_cached_107)
            )
            # 4h red, previous 4h green, 4h overbought
            short_entry_logic.append(
              (_cmp_cached_516) | (df["change_pct_4h"].shift(48) > -5.0) | (df["RSI_14_4h"].shift(48) > 20.0)
            )
            # 4h red, 4h moving down, 4h still high, 1d downtrend
            short_entry_logic.append(
              (_cmp_cached_349)
              | (_cmp_cached_463)
              | (_cmp_cached_386)
              | (_cmp_cached_52)
            )

            # Logic
            short_entry_logic.append(_cmp_cached_566)
            short_entry_logic.append(_cmp_cached_567)
            short_entry_logic.append(_cmp_cached_487)
            short_entry_logic.append(df["EMA_26"] < df["EMA_12"])
            short_entry_logic.append((df["EMA_26"] - df["EMA_12"]) > (df["open"] * 0.024))
            short_entry_logic.append((df["EMA_26"].shift() - df["EMA_12"].shift()) > (df["open"] / 100.0))
            short_entry_logic.append(df["close"] < (df["EMA_20"] * 0.958))
            short_entry_logic.append(df["close"] < (df["BBL_20_2.0"] * 0.992))

          # # Condition #620 - Grind mode (Short).
          # if short_entry_condition_index == 620:
          #   # Protections
          #   short_entry_logic.append(num_open_short_grind_mode < self.grind_mode_max_slots)
          #   short_entry_logic.append(is_pair_short_grind_mode)
          #   short_entry_logic.append(_cmp_cached_568)
          #   short_entry_logic.append(_cmp_cached_569)
          #   short_entry_logic.append(_cmp_cached_378)
          #   short_entry_logic.append(_cmp_cached_570)
          #   short_entry_logic.append(_cmp_cached_571)
          #   short_entry_logic.append(_cmp_cached_316)
          #   short_entry_logic.append(_cmp_cached_572)
          #   short_entry_logic.append(df["close_max_48"] >= (df["close"] * 1.10))

          #   # Logic
          #   short_entry_logic.append(_cmp_cached_488)
          #   short_entry_logic.append(_cmp_cached_573)
          #   short_entry_logic.append(_cmp_cached_487)

          # Condition #641 - Top Coins mode (Short).
          if short_entry_condition_index == 641:
            # Protections
            short_entry_logic.append(is_pair_short_top_coins_mode)

            short_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)

            short_entry_logic.append(_cmp_cached_378)
            short_entry_logic.append(_cmp_cached_379)
            short_entry_logic.append(_cmp_cached_380)
            short_entry_logic.append(_cmp_cached_381)
            short_entry_logic.append(_cmp_cached_382)
            short_entry_logic.append(_cmp_cached_383)
            # 5m down move, 1h still not low enough, 4h high
            short_entry_logic.append(
              (_cmp_cached_394) | (_cmp_cached_421) | (_cmp_cached_431)
            )
            # 5m down move, 1h high, 4h still not low enough
            short_entry_logic.append(
              (_cmp_cached_394) | (_cmp_cached_426) | (_cmp_cached_574)
            )
            # 15m down move, 15m still not low enough, 1h still high
            short_entry_logic.append(
              (_cmp_cached_388) | (_cmp_cached_390) | (_cmp_cached_396)
            )
            # 15m & 1h down move, 1d still not low enough
            short_entry_logic.append(
              (_cmp_cached_388) | (_cmp_cached_405) | (_cmp_cached_452)
            )
            # 15m & 1h down move, 1h still not low enough
            short_entry_logic.append(
              (_cmp_cached_434) | (_cmp_cached_408) | (_cmp_cached_392)
            )
            # 15m down move, 1h high, 4h still high
            short_entry_logic.append(
              (_cmp_cached_434) | (_cmp_cached_432) | (_cmp_cached_437)
            )
            # 15m & 1h down move, 4h still high
            short_entry_logic.append(
              (_cmp_cached_441) | (_cmp_cached_409) | (_cmp_cached_386)
            )
            # 15m down move, 1h still not low enough, 4h still high
            short_entry_logic.append(
              (_cmp_cached_477) | (_cmp_cached_420) | (_cmp_cached_464)
            )
            # 1h & 4h & 1d down move
            short_entry_logic.append((_cmp_cached_405) | (_cmp_cached_358) | (_cmp_cached_359))
            # 1h & 4h down move, 15m not low enough
            short_entry_logic.append(
              (_cmp_cached_389) | (_cmp_cached_358) | (_cmp_cached_575)
            )
            # 1h down move, 1h still not low enough, 4h still high
            short_entry_logic.append(
              (_cmp_cached_389) | (_cmp_cached_421) | (_cmp_cached_386)
            )
            # 1h & 4h down move, 1h still not low enough
            short_entry_logic.append(
              (_cmp_cached_408) | (_cmp_cached_475) | (_cmp_cached_421)
            )
            # 1h & 4h down move, 4h still high
            short_entry_logic.append(
              (_cmp_cached_408) | (_cmp_cached_475) | (_cmp_cached_386)
            )
            # 1h & 4h down move, 1h still not low enough
            short_entry_logic.append(
              (_cmp_cached_395) | (_cmp_cached_423) | (_cmp_cached_402)
            )
            # 1h & 4h down move, 4h still not low enough
            short_entry_logic.append(
              (_cmp_cached_395) | (_cmp_cached_423) | (_cmp_cached_437)
            )
            # 1h down move, 1h & 4h still not low enough
            short_entry_logic.append(
              (_cmp_cached_395) | (_cmp_cached_421) | (_cmp_cached_393)
            )
            # 4h down move, 15m still high, 1h still not low enough
            short_entry_logic.append(
              (_cmp_cached_423) | (_cmp_cached_438) | (_cmp_cached_402)
            )
            # 4h down move, 15m & 4h still not low enough
            short_entry_logic.append(
              (_cmp_cached_576) | (_cmp_cached_509) | (_cmp_cached_407)
            )

            # Logic
            short_entry_logic.append(df["RSI_20"] > df["RSI_20"].shift(1))
            short_entry_logic.append(_cmp_cached_577)
            short_entry_logic.append(_cmp_cached_487)
            short_entry_logic.append(df["close"] > df["SMA_16"] * 1.044)

          # Condition #642 - Top Coins mode (Short).
          if short_entry_condition_index == 642:
            # Protections
            short_entry_logic.append(is_pair_short_top_coins_mode)

            short_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)

            # 5m & 1h & 4h down move
            short_entry_logic.append((_cmp_cached_394) | (_cmp_cached_405) | (_cmp_cached_358))
            # 5m down move, 15m & 4h still high
            short_entry_logic.append(
              (_cmp_cached_394) | (_cmp_cached_401) | (_cmp_cached_464)
            )
            # 5m down move, 15m still high, 1h high
            short_entry_logic.append(
              (_cmp_cached_578) | (_cmp_cached_456) | (_cmp_cached_426)
            )
            # 15m & 1h down move, 1h still not low enough
            short_entry_logic.append(
              (_cmp_cached_388) | (_cmp_cached_405) | (_cmp_cached_421)
            )
            # 15m & 1h down move, 1d still not low enough
            short_entry_logic.append(
              (_cmp_cached_388) | (_cmp_cached_405) | (_cmp_cached_452)
            )
            # 15m strong down move, 4h high
            short_entry_logic.append((_cmp_cached_388) | (_cmp_cached_435))
            # 15m & 1h down move, 1h still not low enough
            short_entry_logic.append(
              (_cmp_cached_388) | (_cmp_cached_395) | (_cmp_cached_420)
            )
            # 15m down move, 15m stil high, 1h still not low enough
            short_entry_logic.append(
              (_cmp_cached_417) | (_cmp_cached_438) | (_cmp_cached_420)
            )
            # 15m down move, 1h & 4h still high
            short_entry_logic.append(
              (_cmp_cached_417) | (_cmp_cached_453) | (_cmp_cached_464)
            )
            # 15m & 1h down move, 4h still not low enough
            short_entry_logic.append(
              (_cmp_cached_388) | (_cmp_cached_409) | (_cmp_cached_386)
            )
            # 15m down move, 15m still not low enough, 4h high
            short_entry_logic.append(
              (_cmp_cached_434) | (_cmp_cached_457) | (_cmp_cached_435)
            )
            # 15m down move, 4h still high, 1d high
            short_entry_logic.append(
              (_cmp_cached_434) | (_cmp_cached_464) | (_cmp_cached_424)
            )
            # 15m & 4h down move, 1d still high
            short_entry_logic.append(
              (_cmp_cached_434) | (_cmp_cached_475) | (_cmp_cached_450)
            )
            # 15m & 1h down move, 4h still not low enough
            short_entry_logic.append(
              (_cmp_cached_441) | (_cmp_cached_395) | (_cmp_cached_393)
            )
            # 15m & 1h down move, 4h still not low enough
            short_entry_logic.append(
              (_cmp_cached_477) | (_cmp_cached_480) | (_cmp_cached_393)
            )
            # 15m & 4h down move, 4h still not low enough
            short_entry_logic.append(
              (_cmp_cached_477) | (_cmp_cached_475) | (_cmp_cached_407)
            )
            # 15m down move, 1h still high, 4h still high
            short_entry_logic.append(
              (_cmp_cached_477) | (_cmp_cached_420) | (_cmp_cached_464)
            )
            # 15m down move, 1h still not low enough, 4h high
            short_entry_logic.append(
              (_cmp_cached_477) | (_cmp_cached_421) | (_cmp_cached_431)
            )
            # 15m down move, 1h high, 4h still not low enough
            short_entry_logic.append(
              (_cmp_cached_477) | (_cmp_cached_426) | (_cmp_cached_574)
            )
            # 15m down move, 4h high, 1d stil high
            short_entry_logic.append(
              (_cmp_cached_477) | (_cmp_cached_435) | (_cmp_cached_450)
            )
            # 15m & 4h down move, 1h still not low enough
            short_entry_logic.append(
              (_cmp_cached_443) | (_cmp_cached_423) | (_cmp_cached_392)
            )
            # 15m & 4h down move, 1h still high
            short_entry_logic.append(
              (_cmp_cached_443) | (_cmp_cached_442) | (_cmp_cached_396)
            )
            # 15m down move, 15m still high 4h still high
            short_entry_logic.append(
              (_cmp_cached_443) | (_cmp_cached_413) | (_cmp_cached_386)
            )
            # 15m down move, 1h still high, 4h high
            short_entry_logic.append(
              (_cmp_cached_443) | (_cmp_cached_396) | (_cmp_cached_525)
            )
            # 1h & 4h down move, 1h still not low enough
            short_entry_logic.append(
              (_cmp_cached_405) | (_cmp_cached_410) | (_cmp_cached_421)
            )
            # 1h & 4h down move, 4h still not low enough
            short_entry_logic.append(
              (_cmp_cached_405) | (_cmp_cached_423) | (_cmp_cached_407)
            )
            # 1h & 4h down move, 1h still not low enough
            short_entry_logic.append(
              (_cmp_cached_389) | (_cmp_cached_358) | (_cmp_cached_421)
            )
            # 1h & 4h down move, 4h still not low enough
            short_entry_logic.append(
              (_cmp_cached_389) | (_cmp_cached_358) | (_cmp_cached_407)
            )
            # 1h & 4h down move, 1h still not low enough
            short_entry_logic.append(
              (_cmp_cached_389) | (_cmp_cached_423) | (_cmp_cached_579)
            )
            # 1h & 4h down move, 1d still high
            short_entry_logic.append(
              (_cmp_cached_389) | (_cmp_cached_423) | (_cmp_cached_450)
            )
            # 1h & 4h down move, 4h still not low enough
            short_entry_logic.append(
              (_cmp_cached_408) | (_cmp_cached_475) | (_cmp_cached_580)
            )
            # 1h down move, 4h still high, 1d high
            short_entry_logic.append(
              (_cmp_cached_395) | (_cmp_cached_464) | (_cmp_cached_424)
            )
            # 1h & 4h down move, 1h still not low enough
            short_entry_logic.append(
              (_cmp_cached_395) | (_cmp_cached_423) | (_cmp_cached_402)
            )
            # 1h & 4h down move, 15m still high
            short_entry_logic.append(
              (_cmp_cached_395) | (_cmp_cached_442) | (_cmp_cached_438)
            )
            # 1h & 4h down move, 4h still not low enough
            short_entry_logic.append(
              (_cmp_cached_480) | (_cmp_cached_358) | (_cmp_cached_402)
            )
            # 1h & 4h down move, 1h still high
            short_entry_logic.append(
              (_cmp_cached_409) | (_cmp_cached_423) | (_cmp_cached_453)
            )
            # 1h down move, 1h still not low enough, 4h still high
            short_entry_logic.append(
              (_cmp_cached_409) | (_cmp_cached_420) | (_cmp_cached_386)
            )
            # 4h down move, 15m still high, 1h still not low enough
            short_entry_logic.append(
              (_cmp_cached_423) | (_cmp_cached_401) | (_cmp_cached_420)
            )
            # 4h down move, 15m still high, 4h still not low enough
            short_entry_logic.append(
              (_cmp_cached_475) | (_cmp_cached_438) | (_cmp_cached_437)
            )
            # 4h down move, 1h still not low enough, 1d still high
            short_entry_logic.append(
              (_cmp_cached_581) | (_cmp_cached_392) | (_cmp_cached_450)
            )
            # 15m & 1h still high, 4h high
            short_entry_logic.append(
              (_cmp_cached_413)
              | (_cmp_cached_392)
              | (_cmp_cached_525)
            )
            # 15m still high, 1h & 1d high
            short_entry_logic.append(
              (_cmp_cached_401)
              | (_cmp_cached_432)
              | (_cmp_cached_424)
            )
            # 15m & 4h high
            short_entry_logic.append((_cmp_cached_438) | (_cmp_cached_435))
            # 15m high, 1h & 4h still not low enough
            short_entry_logic.append(
              (_cmp_cached_509)
              | (_cmp_cached_402)
              | (_cmp_cached_437)
            )
            # 15m & 4h high
            short_entry_logic.append((_cmp_cached_509) | (_cmp_cached_431))
            # 1h & 4h still high, 1d high
            short_entry_logic.append(
              (_cmp_cached_392)
              | (_cmp_cached_393)
              | (_cmp_cached_450)
            )
            # 1h & 4h high
            short_entry_logic.append((_cmp_cached_432) | (_cmp_cached_525))
            # 1h & 4h high
            short_entry_logic.append((_cmp_cached_426) | (_cmp_cached_435))
            # 4h & 1d high
            short_entry_logic.append((_cmp_cached_435) | (_cmp_cached_433))
            # 1d red, 1d high
            short_entry_logic.append((_cmp_cached_582) | (_cmp_cached_433))
            # 1d P&D, 1d high
            short_entry_logic.append(
              (_cmp_cached_352)
              | (df["change_pct_1d"].shift(288) > -10.0)
              | (_cmp_cached_450)
            )

            # Logic
            short_entry_logic.append(_cmp_cached_518)
            short_entry_logic.append(df["RSI_20"] > df["RSI_20"].shift(1))
            short_entry_logic.append(df["close"] > df["SMA_16"] * 1.042)

          # Condition #661 - Scalp mode (Short).
          if short_entry_condition_index == 661:
            # Protections
            short_entry_logic.append(df["num_empty_288"] <= allowed_empty_candles_288)

            # 15m down move, 15m high
            short_entry_logic.append((_cmp_cached_477) | (_cmp_cached_583))
            # 15m & 1h down move, 15m still high
            short_entry_logic.append((_cmp_cached_443) | (_cmp_cached_584) | (_cmp_cached_456))
            # 15m down move, 15m & 4h still high
            short_entry_logic.append(
              (_cmp_cached_443) | (_cmp_cached_438) | (_cmp_cached_386)
            )
            # 15m & 1h down move, 1h high
            short_entry_logic.append((_cmp_cached_585) | (_cmp_cached_482) | (_cmp_cached_586))
            # 15m & 1h down move, 1h still high
            short_entry_logic.append(
              (_cmp_cached_585) | (_cmp_cached_482) | (_cmp_cached_396)
            )
            # 15m & 1h down move, 4h high
            short_entry_logic.append((_cmp_cached_585) | (_cmp_cached_584) | (_cmp_cached_587))
            # 15m & 4h down move, 15m high
            short_entry_logic.append(
              (_cmp_cached_585) | (_cmp_cached_427) | (_cmp_cached_438)
            )
            # 15m & 4h down move, 15m high
            short_entry_logic.append(
              (_cmp_cached_585) | (_cmp_cached_588) | (_cmp_cached_509)
            )
            # 15m down move, 15m & 1h still high
            short_entry_logic.append(
              (_cmp_cached_585) | (_cmp_cached_456) | (_cmp_cached_396)
            )
            # 15m down move, 15m & 1h still high
            short_entry_logic.append(
              (_cmp_cached_585) | (_cmp_cached_438) | (_cmp_cached_396)
            )
            # 15m down move, 4h still high, 1d overbought
            short_entry_logic.append((_cmp_cached_585) | (_cmp_cached_422) | (_cmp_cached_517))
            # 15m down move, 15m high, 4h still high
            short_entry_logic.append(
              (_cmp_cached_589) | (_cmp_cached_590) | (_cmp_cached_386)
            )
            # 15m down move, 15m & 1h still high
            short_entry_logic.append(
              (_cmp_cached_589) | (_cmp_cached_591) | (_cmp_cached_453)
            )
            # 15m down move, 15m still not low enough, 4h high
            short_entry_logic.append(
              (_cmp_cached_288) | (_cmp_cached_413) | (_cmp_cached_525)
            )
            # 1h down move, 4h still high, 1d high
            short_entry_logic.append(
              (_cmp_cached_480) | (_cmp_cached_422) | (_cmp_cached_479)
            )
            short_entry_logic.append(
              (_cmp_cached_409) | (_cmp_cached_453) | (_cmp_cached_479)
            )
            # 1h & 4h down move, 4h high
            short_entry_logic.append(
              (_cmp_cached_474) | (_cmp_cached_588) | (_cmp_cached_435)
            )
            # 1h down move, 15m & 1h still high
            short_entry_logic.append(
              (_cmp_cached_482) | (_cmp_cached_438) | (_cmp_cached_396)
            )
            # 1h down move, 1h still high, 4h high
            short_entry_logic.append(
              (_cmp_cached_482) | (_cmp_cached_396) | (_cmp_cached_393)
            )
            # 1h down move, 1h high
            short_entry_logic.append((_cmp_cached_482) | (_cmp_cached_469))
            # 1h down move, 4h & 1d high
            short_entry_logic.append((_cmp_cached_482) | (_cmp_cached_592) | (_cmp_cached_593))
            # 1h down move, 1h still high, 4h high
            short_entry_logic.append((_cmp_cached_594) | (_cmp_cached_418) | (_cmp_cached_595))
            # 1h down move, 1h high
            short_entry_logic.append((_cmp_cached_594) | (_cmp_cached_469))
            # 1h & 4h down move, 15m high
            short_entry_logic.append((_cmp_cached_596) | (_cmp_cached_588) | (_cmp_cached_597))
            # 1h down move, 15m still high, 4h high
            short_entry_logic.append(
              (_cmp_cached_596) | (_cmp_cached_456) | (_cmp_cached_587)
            )
            # 1h down move, 15m high, 1h still high
            short_entry_logic.append(
              (_cmp_cached_596) | (_cmp_cached_597) | (_cmp_cached_453)
            )
            # 1h down move, 15m still high, 4h high
            short_entry_logic.append(
              (_cmp_cached_596) | (_cmp_cached_438) | (_cmp_cached_435)
            )
            # 1h down move, 15m & 1h high
            short_entry_logic.append(
              (_cmp_cached_596) | (_cmp_cached_468) | (_cmp_cached_598)
            )
            # 1h down move, 1h & 1d high
            short_entry_logic.append(
              (_cmp_cached_596) | (_cmp_cached_586) | (_cmp_cached_433)
            )
            # 1h down move, 4h still high, 1d high
            short_entry_logic.append(
              (_cmp_cached_596) | (_cmp_cached_386) | (_cmp_cached_479)
            )
            # 1h down move, 5m up move, 1h still high
            short_entry_logic.append(
              (_cmp_cached_584) | (_cmp_cached_599) | (_cmp_cached_396)
            )
            # 1h down move, 15m still not low enough, 1h high
            short_entry_logic.append(
              (_cmp_cached_584) | (_cmp_cached_413) | (_cmp_cached_586)
            )
            # 1h down move, 15m still not low enough, 1h high
            short_entry_logic.append(
              (_cmp_cached_584) | (_cmp_cached_413) | (_cmp_cached_469)
            )
            # 1h down move, 15m & 4h still high
            short_entry_logic.append(
              (_cmp_cached_584) | (_cmp_cached_438) | (_cmp_cached_386)
            )
            # 1h down move, 15m & 1h high
            short_entry_logic.append(
              (_cmp_cached_584) | (_cmp_cached_597) | (_cmp_cached_600)
            )
            # 1h down move, 1h still high, 4h high
            short_entry_logic.append(
              (_cmp_cached_584) | (_cmp_cached_418) | (_cmp_cached_525)
            )
            # 1h down move, 1h high, 4h still high
            short_entry_logic.append((_cmp_cached_584) | (_cmp_cached_601) | (_cmp_cached_602))
            # 1h down move, 1h still high, 4h high
            short_entry_logic.append(
              (_cmp_cached_584) | (_cmp_cached_453) | (_cmp_cached_603)
            )
            # 1h down move, 1h & 1d high
            short_entry_logic.append(
              (_cmp_cached_584) | (_cmp_cached_432) | (_cmp_cached_593)
            )
            # 1h down move, 4h & 1d high
            short_entry_logic.append((_cmp_cached_584) | (_cmp_cached_604) | (_cmp_cached_605))
            # 4h down move, 15m high
            short_entry_logic.append((_cmp_cached_442) | (_cmp_cached_583))
            # 4h down move, 1h high
            short_entry_logic.append((_cmp_cached_475) | (_cmp_cached_426))
            # 4h down move, 1h & 4h still high
            short_entry_logic.append(
              (_cmp_cached_606) | (_cmp_cached_396) | (_cmp_cached_422)
            )
            # 4h down move, 15m & 1h high
            short_entry_logic.append(
              (_cmp_cached_427) | (_cmp_cached_583) | (_cmp_cached_432)
            )
            # 4h down move, 15m still high, 1h high
            short_entry_logic.append(
              (_cmp_cached_427) | (_cmp_cached_401) | (_cmp_cached_426)
            )
            # 4h down move, 1h still high, 4h still moving down
            short_entry_logic.append(
              (_cmp_cached_427) | (_cmp_cached_396) | (_cmp_cached_463)
            )
            # 4h down move, 1h high, 4h still high
            short_entry_logic.append((_cmp_cached_607) | (_cmp_cached_586) | (_cmp_cached_422))
            # 4h down move, 15m high, 4h still high
            short_entry_logic.append(
              (_cmp_cached_608) | (_cmp_cached_597) | (_cmp_cached_464)
            )
            # 4h down move, 15m still high, 1h high
            short_entry_logic.append(
              (_cmp_cached_608) | (_cmp_cached_401) | (_cmp_cached_432)
            )
            # 4h down move, 15m & 4h still high
            short_entry_logic.append(
              (_cmp_cached_608) | (_cmp_cached_438) | (_cmp_cached_422)
            )
            # 4h down move, 15m high, 4h still not low enough
            short_entry_logic.append(
              (_cmp_cached_608) | (_cmp_cached_509) | (_cmp_cached_393)
            )
            # 4h down move, 1h still high, 4h high
            short_entry_logic.append(
              (_cmp_cached_608) | (_cmp_cached_396) | (_cmp_cached_603)
            )
            # 4h down move, 15m & 4h high
            short_entry_logic.append(
              (_cmp_cached_588) | (_cmp_cached_597) | (_cmp_cached_603)
            )
            # 4h down move, 15m high, 4h still high
            short_entry_logic.append(
              (_cmp_cached_588) | (_cmp_cached_583) | (_cmp_cached_602)
            )
            # 4h down move, 15m still high, 4h high
            short_entry_logic.append(
              (_cmp_cached_588) | (_cmp_cached_438) | (_cmp_cached_431)
            )
            # 4h down move, 15m & 4h high
            short_entry_logic.append(
              (_cmp_cached_588) | (_cmp_cached_509) | (_cmp_cached_440)
            )
            # 4h down move, 1h & 4h high
            short_entry_logic.append(
              (_cmp_cached_588) | (_cmp_cached_432) | (_cmp_cached_603)
            )
            # 4h down move, 4h still high, 1d high
            short_entry_logic.append(
              (_cmp_cached_588) | (_cmp_cached_386) | (_cmp_cached_433)
            )
            # 15m high, 4h high
            short_entry_logic.append((_cmp_cached_597) | (_cmp_cached_592))
            # 15m high, 4h still high
            short_entry_logic.append((_cmp_cached_583) | (_cmp_cached_386))
            # 15m high, 1h still high
            short_entry_logic.append((_cmp_cached_509) | (_cmp_cached_453))
            # 15m & 4h high
            short_entry_logic.append((_cmp_cached_509) | (_cmp_cached_603))
            # 15m high, 1h still not low enough
            short_entry_logic.append((_cmp_cached_609) | (_cmp_cached_392))

            # Logic
            short_entry_logic.append(_cmp_cached_610)
            short_entry_logic.append(_cmp_cached_611)
            short_entry_logic.append(_cmp_cached_612)
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
            short_entry_logic.append(_cmp_cached_613)

          ###############################################################################################

          # SHORT ENTRY CONDITIONS ENDS HERE

          ###############################################################################################

          short_entry_logic.append(_cmp_cached_377)
          item_short_entry = _and_conditions(short_entry_logic)
          _append_entry_tag(entry_tags, item_short_entry, f"{short_entry_condition_index} ")
          short_entry_conditions.append(item_short_entry)
          df.loc[:, "enter_short"] = item_short_entry.astype(int)

    if short_entry_conditions:
      df.loc[:, "enter_short"] = _or_conditions(short_entry_conditions).astype(int)

    df.loc[:, "enter_tag"] = entry_tags
    return df
