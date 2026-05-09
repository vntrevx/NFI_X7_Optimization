"""Fast informative-timeframe merge helpers for TestX7."""

from __future__ import annotations

import pandas as pd
from freqtrade.exchange import timeframe_to_minutes
from pandas import DataFrame


def fast_merge_informative_pair(
  dataframe: DataFrame,
  informative: DataFrame,
  timeframe: str,
  timeframe_inf: str,
  ffill: bool = True,
  append_timeframe: bool = True,
  date_column: str = "date",
  suffix: str | None = None,
) -> DataFrame:
  """Merge informative data with Freqtrade's no-lookahead date shift.

  This is a TestX7-local replacement for Freqtrade's merge_ordered-based helper.
  It assumes sorted candle data, which is true for Freqtrade OHLCV data, and
  aligns the shifted informative rows with the base timeframe by index reindex.
  """
  if not ffill:
    from freqtrade.strategy import merge_informative_pair

    return merge_informative_pair(
      dataframe,
      informative,
      timeframe,
      timeframe_inf,
      ffill=ffill,
      append_timeframe=append_timeframe,
      date_column=date_column,
      suffix=suffix,
    )

  if suffix and append_timeframe:
    raise ValueError("You can not specify `append_timeframe` as True and a `suffix`.")

  minutes_inf = timeframe_to_minutes(timeframe_inf)
  minutes = timeframe_to_minutes(timeframe)
  if minutes > minutes_inf:
    raise ValueError(
      "Tried to merge a faster timeframe to a slower timeframe."
      "This would create new rows, and can throw off your regular indicators."
    )

  if minutes == minutes_inf:
    date_merge_values = informative[date_column]
  elif timeframe_inf == "1M":
    date_merge_values = informative[date_column] + pd.offsets.MonthBegin(1) - pd.to_timedelta(minutes, "m")
  else:
    date_merge_values = informative[date_column] + pd.to_timedelta(minutes_inf - minutes, "m")

  date_merge = "date_merge"
  info = informative.copy(deep=False)
  info[date_merge] = date_merge_values

  if append_timeframe:
    date_merge = f"date_merge_{timeframe_inf}"
    info.columns = [f"{column}_{timeframe_inf}" for column in info.columns]
  elif suffix:
    date_merge = f"date_merge_{suffix}"
    info.columns = [f"{column}_{suffix}" for column in info.columns]

  if info.empty:
    aligned = info.drop(columns=[date_merge], errors="ignore")
    return pd.concat([dataframe.reset_index(drop=True), aligned], axis=1)

  info = info.sort_values(date_merge).drop_duplicates(date_merge, keep="last")
  aligned = info.set_index(date_merge).reindex(dataframe[date_column], method="ffill")
  aligned = aligned.drop(columns=[date_merge], errors="ignore")
  aligned.index = dataframe.index

  return pd.concat([dataframe, aligned], axis=1)
