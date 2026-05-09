"""Pair-level parallel analysis for TestX7 live loops."""

from __future__ import annotations

import atexit
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor, as_completed
import importlib
import logging
import multiprocessing
import os
import queue
import sys
import time
import traceback
from typing import Any

import pandas as pd
from freqtrade.enums import CandleType
from freqtrade.exceptions import StrategyError
from freqtrade.persistence import Trade
from freqtrade.strategy.strategy_validation import StrategyResultValidator
from pandas import DataFrame

from test_x7_modules.cpu import recommended_indicator_cores, recommended_process_workers

log = logging.getLogger(__name__)
_MIN_CALLBACK_RESULT_ROWS = 6
_FALSE_VALUES = {"0", "false", "no", "off"}
_NUMERIC_THREAD_ENV_VARS = (
  "NUMEXPR_NUM_THREADS",
  "OMP_NUM_THREADS",
  "OPENBLAS_NUM_THREADS",
  "MKL_NUM_THREADS",
)

_PROCESS_STRATEGY = None
_PROCESS_RUNMODE = "dry_run"
_PROCESS_OPEN_TRADE_COUNT = 0
_PROCESS_OPEN_TRADE_TAGS: list[str | None] = []
_PROCESS_DATAFRAME_CACHE: dict[tuple[str, str], DataFrame] = {}
_NUMERIC_THREAD_LIMITER = None
_NUMERIC_THREAD_LIMITER_THREADS = 0


class _RunModeValue:
  def __init__(self, value: str) -> None:
    self.value = value


class _StaticDataProvider:
  def __init__(self, dataframes: dict[tuple[str, str], DataFrame], whitelist: list[str], runmode: str) -> None:
    self._dataframes = dataframes
    self._whitelist = whitelist
    self.runmode = _RunModeValue(runmode)

  def current_whitelist(self) -> list[str]:
    return list(self._whitelist)

  def ohlcv(self, pair: str, timeframe: str, candle_type: CandleType | None = None) -> DataFrame:
    return self.get_pair_dataframe(pair, timeframe)

  def get_pair_dataframe(self, pair: str, timeframe: str) -> DataFrame:
    dataframe = self._dataframes[(pair, timeframe)]
    return dataframe.copy(deep=False)


class _FakeTrade:
  def __init__(self, enter_tag: str | None) -> None:
    self.enter_tag = enter_tag


def _patch_worker_trade_methods(open_trade_count: int, open_trade_tags: list[str | None]) -> None:
  Trade.get_open_trade_count = staticmethod(lambda: open_trade_count)
  Trade.get_trades_proxy = staticmethod(lambda *args, **kwargs: [_FakeTrade(tag) for tag in open_trade_tags])


def _positive_int(value) -> int | None:
  if value is None:
    return None
  try:
    parsed = int(value)
  except (TypeError, ValueError):
    return None
  return parsed if parsed > 0 else None


def _test_x7_configured_numeric_threads(config: dict[str, Any]) -> int:
  env_threads = _positive_int(os.getenv("TEST_X7_NUMERIC_THREADS"))
  config_threads = _positive_int(config.get("test_x7_numeric_threads"))
  return env_threads if env_threads is not None else (config_threads or 0)


def _test_x7_apply_numeric_thread_limit(config: dict[str, Any]) -> None:
  global _NUMERIC_THREAD_LIMITER, _NUMERIC_THREAD_LIMITER_THREADS

  threads = _test_x7_configured_numeric_threads(config)
  if threads <= 0:
    return

  value = str(threads)
  for name in _NUMERIC_THREAD_ENV_VARS:
    os.environ[name] = value

  try:
    import numexpr as ne

    ne.set_num_threads(threads)
  except Exception:
    pass

  if _NUMERIC_THREAD_LIMITER_THREADS == threads:
    return
  try:
    from threadpoolctl import threadpool_limits

    _NUMERIC_THREAD_LIMITER = threadpool_limits(limits=threads)
    _NUMERIC_THREAD_LIMITER_THREADS = threads
  except Exception:
    _NUMERIC_THREAD_LIMITER = None
    _NUMERIC_THREAD_LIMITER_THREADS = 0


def _init_process_worker(
  strategy_dir: str,
  strategy_module: str,
  strategy_name: str,
  config: dict[str, Any],
  runmode: str,
) -> None:
  global _PROCESS_STRATEGY, _PROCESS_RUNMODE

  _test_x7_apply_numeric_thread_limit(config)
  if strategy_dir not in sys.path:
    sys.path.insert(0, strategy_dir)
  module = importlib.import_module(strategy_module)
  strategy_cls = getattr(module, strategy_name)
  worker_config = dict(config)
  worker_config["test_x7_parallel_analyze_workers"] = 1
  worker_config["test_x7_process_analyze_workers"] = 1
  _PROCESS_STRATEGY = strategy_cls(worker_config)
  _PROCESS_RUNMODE = runmode


def _payload_dataframes(payload: dict[str, Any]) -> dict[tuple[str, str], DataFrame]:
  dataframe_updates = payload.get("dataframe_updates")
  if dataframe_updates is None:
    return payload["dataframes"]

  dataframes: dict[tuple[str, str], DataFrame] = {}
  for key, update in dataframe_updates.items():
    mode = update["mode"]
    if mode == "full":
      _PROCESS_DATAFRAME_CACHE[key] = update["dataframe"]
    elif mode == "append":
      cached = _PROCESS_DATAFRAME_CACHE.get(key)
      if cached is None:
        _PROCESS_DATAFRAME_CACHE[key] = update["dataframe"]
      else:
        combined = pd.concat([cached, update["dataframe"]], copy=False)
        if "date" in combined:
          combined = combined.drop_duplicates(subset=["date"], keep="last")
        max_rows = update.get("max_rows", 0)
        if max_rows > 0 and len(combined) > max_rows:
          combined = combined.tail(max_rows)
        _PROCESS_DATAFRAME_CACHE[key] = combined.reset_index(drop=True)
    elif mode == "reuse":
      pass
    else:
      raise RuntimeError(f"Unsupported TestX7 dataframe update mode: {mode}")

    cached = _PROCESS_DATAFRAME_CACHE.get(key)
    if cached is None:
      raise RuntimeError(f"Missing TestX7 worker dataframe cache for {key}")
    dataframes[key] = cached
  return dataframes


def _run_process_chunk(payload: dict[str, Any]) -> list[tuple[str, DataFrame]]:
  if _PROCESS_STRATEGY is None:
    raise RuntimeError("TestX7 process worker was not initialized")

  _patch_worker_trade_methods(payload["open_trade_count"], payload["open_trade_tags"])
  dp = _StaticDataProvider(_payload_dataframes(payload), payload["whitelist"], _PROCESS_RUNMODE)
  _PROCESS_STRATEGY.dp = dp

  results = []
  result_tail_rows = payload.get("result_tail_rows", 0)
  discard_results = bool(payload.get("discard_results", False))
  debug_pair_seconds = os.getenv("TEST_X7_PROCESS_DEBUG_PAIR_SECONDS", "").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
  }
  for pair in payload["pairs"]:
    dataframe = dp.ohlcv(pair, _PROCESS_STRATEGY.timeframe)
    started = time.perf_counter()
    analyzed = _PROCESS_STRATEGY.analyze_ticker(dataframe, {"pair": pair})
    if debug_pair_seconds:
      log.info("TestX7 process pair=%s seconds=%.6f", pair, time.perf_counter() - started)
    if discard_results:
      continue
    if result_tail_rows > 0 and len(analyzed) > result_tail_rows:
      analyzed = analyzed.tail(result_tail_rows).copy(deep=False)
    results.append((pair, analyzed))
  return results


def _stable_process_worker_loop(
  worker_index: int,
  request_queue,
  response_queue,
  initargs: tuple[Any, ...],
) -> None:
  _init_process_worker(*initargs)
  while True:
    item = request_queue.get()
    if item is None:
      return

    loop_id, payload = item
    try:
      started = time.perf_counter()
      result = _run_process_chunk(payload)
      seconds = time.perf_counter() - started
      if os.getenv("TEST_X7_PROCESS_DEBUG_WORKER_SECONDS", "").strip().lower() in {"1", "true", "yes", "on"}:
        log.info(
          "TestX7 stable worker loop=%s worker=%s pairs=%s seconds=%.6f",
          loop_id,
          worker_index,
          len(payload["pairs"]),
          seconds,
        )
      response_queue.put((loop_id, worker_index, result, None))
    except Exception:
      response_queue.put((loop_id, worker_index, None, traceback.format_exc()))


class TestX7ParallelAnalyzeMixin:
  """Override Freqtrade's sequential analyze(pairs) loop.

  Freqtrade 2026.4 calls ``analyze_pair(pair)`` sequentially.  TestX7 keeps the
  same per-pair strategy logic but can run independent pairs through a bounded
  thread pool.  This targets the live "Strategy analysis took ..." path; normal
  backtesting does not use this pair-loop method.
  """

  test_x7_analyze_workers_env = "TEST_X7_ANALYZE_WORKERS"
  test_x7_process_analyze_workers_env = "TEST_X7_PROCESS_ANALYZE_WORKERS"
  test_x7_stable_process_analyze_workers_env = "TEST_X7_STABLE_PROCESS_ANALYZE_WORKERS"
  test_x7_process_chunk_size_env = "TEST_X7_PROCESS_CHUNK_SIZE"
  test_x7_process_tail_rows_env = "TEST_X7_PROCESS_TAIL_ROWS"
  test_x7_process_tail_rows_prefix = "TEST_X7_PROCESS_TAIL_ROWS_"
  test_x7_process_result_tail_rows_env = "TEST_X7_PROCESS_RESULT_TAIL_ROWS"
  test_x7_stable_skip_unchanged_informative_env = "TEST_X7_STABLE_SKIP_UNCHANGED_INFORMATIVE"
  test_x7_stable_prewarm_dataframes_env = "TEST_X7_STABLE_PREWARM_DATAFRAMES"
  test_x7_stable_prewarm_compute_env = "TEST_X7_STABLE_PREWARM_COMPUTE"
  test_x7_stable_response_timeout_env = "TEST_X7_STABLE_RESPONSE_TIMEOUT_SECONDS"
  test_x7_stable_fallback_env = "TEST_X7_STABLE_FALLBACK_ON_FAILURE"
  test_x7_numeric_threads_env = "TEST_X7_NUMERIC_THREADS"

  def _test_x7_analyze_workers(self, pair_count: int) -> int:
    env_workers = _positive_int(os.getenv(self.test_x7_analyze_workers_env))
    if env_workers is not None:
      return max(1, min(pair_count, env_workers))

    config_workers = self.config.get("test_x7_parallel_analyze_workers", 1)
    if isinstance(config_workers, str) and config_workers.strip().lower() == "auto":
      config_workers = recommended_indicator_cores(self.test_x7_analyze_workers_env)

    workers = _positive_int(config_workers) or 1
    return max(1, min(pair_count, workers))

  def _test_x7_process_workers(self, pair_count: int) -> int:
    env_workers = _positive_int(os.getenv(self.test_x7_process_analyze_workers_env))
    config_workers = self.config.get("test_x7_process_analyze_workers", 1)
    if isinstance(config_workers, str) and config_workers.strip().lower() == "auto":
      config_workers = recommended_process_workers(self.test_x7_process_analyze_workers_env)
    workers = env_workers if env_workers is not None else (_positive_int(config_workers) or 1)
    return max(1, min(pair_count, workers))

  def _test_x7_stable_process_workers(self, pair_count: int) -> int:
    env_workers = _positive_int(os.getenv(self.test_x7_stable_process_analyze_workers_env))
    config_workers = self.config.get("test_x7_stable_process_analyze_workers", 1)
    if isinstance(config_workers, str) and config_workers.strip().lower() == "auto":
      config_workers = recommended_process_workers(self.test_x7_stable_process_analyze_workers_env)
    workers = env_workers if env_workers is not None else (_positive_int(config_workers) or 1)
    return max(1, min(pair_count, workers))

  def _test_x7_process_chunk_size(self) -> int:
    env_chunk_size = _positive_int(os.getenv(self.test_x7_process_chunk_size_env))
    config_chunk_size = self.config.get("test_x7_process_chunk_size", 0)
    return env_chunk_size if env_chunk_size is not None else (_positive_int(config_chunk_size) or 0)

  def _test_x7_process_tail_rows(self) -> int:
    env_tail_rows = _positive_int(os.getenv(self.test_x7_process_tail_rows_env))
    config_tail_rows = self.config.get("test_x7_process_tail_rows", 0)
    return env_tail_rows if env_tail_rows is not None else (_positive_int(config_tail_rows) or 0)

  def _test_x7_process_tail_rows_for_timeframe(self, timeframe: str) -> int:
    suffix = timeframe.upper().replace(" ", "_")
    env_tail_rows = _positive_int(os.getenv(f"{self.test_x7_process_tail_rows_prefix}{suffix}"))
    if env_tail_rows is not None:
      return env_tail_rows

    by_timeframe = self.config.get("test_x7_process_tail_rows_by_timeframe", {})
    if isinstance(by_timeframe, dict):
      config_tail_rows = _positive_int(by_timeframe.get(timeframe))
      if config_tail_rows is not None:
        return config_tail_rows

    return self._test_x7_process_tail_rows()

  def _test_x7_process_result_tail_rows(self) -> int:
    env_tail_rows = _positive_int(os.getenv(self.test_x7_process_result_tail_rows_env))
    config_tail_rows = self.config.get("test_x7_process_result_tail_rows", 0)
    rows = env_tail_rows if env_tail_rows is not None else (_positive_int(config_tail_rows) or 0)
    if rows <= 0:
      return 0
    return max(rows, _MIN_CALLBACK_RESULT_ROWS)

  def _test_x7_stable_skip_unchanged_informative_enabled(self) -> bool:
    env_value = os.getenv(self.test_x7_stable_skip_unchanged_informative_env)
    if env_value is not None:
      return env_value.strip().lower() not in {"0", "false", "no", "off"}
    return bool(self.config.get("test_x7_stable_skip_unchanged_informative", False))

  def _test_x7_stable_prewarm_dataframes_enabled(self) -> bool:
    env_value = os.getenv(self.test_x7_stable_prewarm_dataframes_env)
    if env_value is not None:
      return env_value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(self.config.get("test_x7_stable_prewarm_dataframes", False))

  def _test_x7_stable_prewarm_compute_enabled(self) -> bool:
    env_value = os.getenv(self.test_x7_stable_prewarm_compute_env)
    if env_value is not None:
      return env_value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(self.config.get("test_x7_stable_prewarm_compute", False))

  def _test_x7_stable_response_timeout_seconds(self) -> float:
    env_value = os.getenv(self.test_x7_stable_response_timeout_env)
    config_value = self.config.get("test_x7_stable_response_timeout_seconds", 300.0)
    try:
      timeout = float(env_value if env_value is not None else config_value)
    except (TypeError, ValueError):
      timeout = 300.0
    return max(1.0, timeout)

  def _test_x7_stable_fallback_enabled(self) -> bool:
    env_value = os.getenv(self.test_x7_stable_fallback_env)
    if env_value is not None:
      return env_value.strip().lower() not in _FALSE_VALUES
    return bool(self.config.get("test_x7_stable_fallback_on_failure", True))

  def _test_x7_apply_numeric_thread_limit(self) -> None:
    _test_x7_apply_numeric_thread_limit(self.config)

  def _test_x7_process_runmode(self) -> str:
    runmode = getattr(getattr(self, "dp", None), "runmode", None)
    return str(getattr(runmode, "value", runmode))

  def _test_x7_process_enabled(self, pair_count: int) -> bool:
    runmode = self._test_x7_process_runmode()
    if runmode in {"backtest", "hyperopt", "plot", "webserver"}:
      return False
    return self._test_x7_process_workers(pair_count) > 1

  def _test_x7_stable_process_enabled(self, pair_count: int) -> bool:
    runmode = self._test_x7_process_runmode()
    if runmode in {"backtest", "hyperopt", "plot", "webserver"}:
      return False
    return self._test_x7_stable_process_workers(pair_count) > 1

  def _test_x7_btc_info_pair(self) -> str:
    stable_stakes = [
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
    ]
    stake_currency = self.config["stake_currency"]
    trading_mode = str(getattr(self.config.get("trading_mode", ""), "value", self.config.get("trading_mode", "")))
    if stake_currency in stable_stakes:
      return f"BTC/{stake_currency}:{stake_currency}" if trading_mode in ["futures", "margin"] else f"BTC/{stake_currency}"
    return "BTC/USDT:USDT" if trading_mode in ["futures", "margin"] else "BTC/USDT"

  def _test_x7_timeframe_minutes(self, timeframe: str) -> int:
    if timeframe.endswith("m"):
      return int(timeframe[:-1])
    if timeframe.endswith("h"):
      return int(timeframe[:-1]) * 60
    if timeframe.endswith("d"):
      return int(timeframe[:-1]) * 24 * 60
    return 5

  def _test_x7_timeframe_bucket(self, date_value: Any, timeframe: str) -> int | None:
    if date_value is None:
      return None
    timestamp = pd.Timestamp(date_value)
    minutes = self._test_x7_timeframe_minutes(timeframe)
    return int(timestamp.value // (minutes * 60 * 1_000_000_000))

  def _test_x7_process_chunks(self, pairs: list[str], workers: int) -> list[list[str]]:
    chunk_size = self._test_x7_process_chunk_size()
    if chunk_size > 0:
      return [pairs[index : index + chunk_size] for index in range(0, len(pairs), chunk_size)]
    return [pairs[index::workers] for index in range(workers) if pairs[index::workers]]

  def _test_x7_stable_process_chunks(self, pairs: list[str], workers: int) -> list[list[str]]:
    return [pairs[index::workers] for index in range(workers) if pairs[index::workers]]

  def _test_x7_dead_stable_workers(self, pending: set[int]) -> list[str]:
    processes = getattr(self, "_test_x7_stable_processes", None) or []
    dead_workers = []
    for worker_index in sorted(pending):
      if worker_index >= len(processes):
        dead_workers.append(f"{worker_index}:missing")
        continue
      process, _request_queue = processes[worker_index]
      if not process.is_alive():
        dead_workers.append(f"{worker_index}:exitcode={process.exitcode}")
    return dead_workers

  def _test_x7_wait_stable_responses(self, loop_id: int, pending: set[int], phase: str):
    response_queue = self._test_x7_stable_response_queue
    timeout = self._test_x7_stable_response_timeout_seconds()
    while pending:
      try:
        response_loop_id, worker_index, result, error = response_queue.get(timeout=timeout)
      except queue.Empty as exc:
        dead_workers = self._test_x7_dead_stable_workers(pending)
        if dead_workers:
          raise RuntimeError(f"TestX7 stable {phase} worker died: {dead_workers}") from exc
        raise TimeoutError(
          f"TestX7 stable {phase} timed out after {timeout:.1f}s waiting for workers={sorted(pending)}"
        ) from exc

      if response_loop_id != loop_id or worker_index not in pending:
        continue
      pending.remove(worker_index)
      if error is not None:
        raise RuntimeError(f"TestX7 stable {phase} failed:\n{error}")
      yield worker_index, result

  def _test_x7_open_trade_snapshot(self) -> tuple[int, list[str | None]]:
    try:
      open_trades = Trade.get_trades_proxy(is_open=True)
      return len(open_trades), [getattr(trade, "enter_tag", None) for trade in open_trades]
    except Exception:
      log.exception("TestX7 failed to snapshot open trades for process analyze")
      return 0, []

  def _test_x7_maybe_tail_payload_dataframe(self, dataframe: DataFrame, timeframe: str) -> DataFrame:
    tail_rows = self._test_x7_process_tail_rows_for_timeframe(timeframe)
    if tail_rows <= 0 or len(dataframe) <= tail_rows:
      return dataframe
    return dataframe.tail(tail_rows).copy(deep=False)

  def _test_x7_pair_dataframes(self, pair: str, source_dataframe: DataFrame | None = None) -> dict[tuple[str, str], DataFrame]:
    dataframes: dict[tuple[str, str], DataFrame] = {}
    candle_type = self.config.get("candle_type_def", CandleType.SPOT)
    dataframes[(pair, self.timeframe)] = self._test_x7_maybe_tail_payload_dataframe(
      source_dataframe if source_dataframe is not None else self.dp.ohlcv(pair, self.timeframe, candle_type=candle_type),
      self.timeframe,
    )
    for timeframe in self.info_timeframes:
      dataframes[(pair, timeframe)] = self._test_x7_maybe_tail_payload_dataframe(
        self.dp.get_pair_dataframe(pair=pair, timeframe=timeframe),
        timeframe,
      )
    return dataframes

  def _test_x7_btc_dataframes(self) -> dict[tuple[str, str], DataFrame]:
    dataframes: dict[tuple[str, str], DataFrame] = {}
    btc_info_pair = self._test_x7_btc_info_pair()
    for timeframe in self.btc_info_timeframes:
      dataframes[(btc_info_pair, timeframe)] = self._test_x7_maybe_tail_payload_dataframe(
        self.dp.get_pair_dataframe(pair=btc_info_pair, timeframe=timeframe),
        timeframe,
      )
    return dataframes

  def _test_x7_process_payload(
    self,
    pairs: list[str],
    whitelist: list[str],
    open_trade_count: int,
    open_trade_tags: list[str | None],
    source_dataframes: dict[str, DataFrame],
  ) -> dict[str, Any]:
    dataframes = {}
    for pair in pairs:
      dataframes.update(self._test_x7_pair_dataframes(pair, source_dataframes[pair]))
    dataframes.update(self._test_x7_btc_dataframes())
    return {
      "pairs": pairs,
      "dataframes": dataframes,
      "whitelist": whitelist,
      "open_trade_count": open_trade_count,
      "open_trade_tags": open_trade_tags,
      "result_tail_rows": self._test_x7_process_result_tail_rows(),
    }

  def _test_x7_dataframe_signature(self, dataframe: DataFrame) -> tuple[int, Any, Any]:
    if dataframe.empty:
      return 0, None, None
    last = dataframe.iloc[-1]
    return len(dataframe), last.get("date"), last.get("close")

  def _test_x7_dataframe_update(
    self,
    worker_index: int,
    key: tuple[str, str],
    dataframe: DataFrame,
    base_date: Any | None = None,
    sync_timeframe: str | None = None,
  ) -> dict[str, Any]:
    signatures = self._test_x7_stable_dataframe_signatures.setdefault(worker_index, {})
    old_signature = signatures.get(key)
    new_signature = self._test_x7_dataframe_signature(dataframe)
    signatures[key] = new_signature
    if self._test_x7_stable_skip_unchanged_informative_enabled():
      self._test_x7_record_stable_time_bucket(worker_index, key, base_date, sync_timeframe)

    if old_signature == new_signature:
      return {"mode": "reuse"}

    old_len, old_date, _ = old_signature if old_signature is not None else (0, None, None)
    if old_signature is not None and new_signature[0] in {old_len, old_len + 1} and len(dataframe) >= 2:
      previous = dataframe.iloc[-2]
      if previous.get("date") == old_date:
        return {"mode": "append", "dataframe": dataframe.tail(1).copy(deep=False), "max_rows": len(dataframe)}

    return {"mode": "full", "dataframe": dataframe}

  def _test_x7_record_stable_time_bucket(
    self,
    worker_index: int,
    key: tuple[str, str],
    base_date: Any | None,
    timeframe: str | None,
  ) -> None:
    if base_date is None or timeframe is None:
      return
    bucket = self._test_x7_timeframe_bucket(base_date, timeframe)
    if bucket is None:
      return
    buckets = self._test_x7_stable_time_buckets.setdefault(worker_index, {})
    buckets[key] = bucket

  def _test_x7_can_reuse_stable_timeframe(
    self,
    worker_index: int,
    key: tuple[str, str],
    base_date: Any | None,
    timeframe: str,
  ) -> bool:
    if not self._test_x7_stable_skip_unchanged_informative_enabled():
      return False
    signatures = self._test_x7_stable_dataframe_signatures.setdefault(worker_index, {})
    if key not in signatures:
      return False
    bucket = self._test_x7_timeframe_bucket(base_date, timeframe)
    if bucket is None:
      return False
    buckets = self._test_x7_stable_time_buckets.setdefault(worker_index, {})
    return buckets.get(key) == bucket

  def _test_x7_last_date(self, dataframe: DataFrame) -> Any | None:
    if dataframe.empty:
      return None
    return dataframe.iloc[-1].get("date")

  def _test_x7_stable_process_payload(
    self,
    worker_index: int,
    pairs: list[str],
    whitelist: list[str],
    open_trade_count: int,
    open_trade_tags: list[str | None],
    source_dataframes: dict[str, DataFrame],
  ) -> dict[str, Any]:
    if not self._test_x7_stable_skip_unchanged_informative_enabled():
      dataframes = {}
      for pair in pairs:
        dataframes.update(self._test_x7_pair_dataframes(pair, source_dataframes[pair]))
      dataframes.update(self._test_x7_btc_dataframes())
      dataframe_updates = {
        key: self._test_x7_dataframe_update(worker_index, key, dataframe)
        for key, dataframe in dataframes.items()
      }
      if os.getenv("TEST_X7_PROCESS_DEBUG_UPDATES", "").strip().lower() in {"1", "true", "yes", "on"}:
        mode_counts: dict[str, int] = {}
        for update in dataframe_updates.values():
          mode = str(update.get("mode", "?"))
          mode_counts[mode] = mode_counts.get(mode, 0) + 1
        log.info("TestX7 stable payload worker=%s update_modes=%s", worker_index, mode_counts)
      return {
        "pairs": pairs,
        "dataframe_updates": dataframe_updates,
        "whitelist": whitelist,
        "open_trade_count": open_trade_count,
        "open_trade_tags": open_trade_tags,
        "result_tail_rows": self._test_x7_process_result_tail_rows(),
      }

    dataframe_updates = {}
    for pair in pairs:
      source_dataframe = source_dataframes[pair]
      base_date = self._test_x7_last_date(source_dataframe)
      base_key = (pair, self.timeframe)
      dataframe_updates[base_key] = self._test_x7_dataframe_update(
        worker_index,
        base_key,
        self._test_x7_maybe_tail_payload_dataframe(source_dataframe, self.timeframe),
        base_date,
        self.timeframe,
      )
      for timeframe in self.info_timeframes:
        key = (pair, timeframe)
        if self._test_x7_can_reuse_stable_timeframe(worker_index, key, base_date, timeframe):
          dataframe_updates[key] = {"mode": "reuse"}
          continue
        dataframe_updates[key] = self._test_x7_dataframe_update(
          worker_index,
          key,
          self._test_x7_maybe_tail_payload_dataframe(self.dp.get_pair_dataframe(pair=pair, timeframe=timeframe), timeframe),
          base_date,
          timeframe,
        )

    btc_info_pair = self._test_x7_btc_info_pair()
    base_date = self._test_x7_last_date(source_dataframes[pairs[0]]) if pairs else None
    for timeframe in self.btc_info_timeframes:
      key = (btc_info_pair, timeframe)
      if key in dataframe_updates:
        continue
      if self._test_x7_can_reuse_stable_timeframe(worker_index, key, base_date, timeframe):
        dataframe_updates[key] = {"mode": "reuse"}
        continue
      dataframe_updates[key] = self._test_x7_dataframe_update(
        worker_index,
        key,
        self._test_x7_maybe_tail_payload_dataframe(self.dp.get_pair_dataframe(pair=btc_info_pair, timeframe=timeframe), timeframe),
        base_date,
        timeframe,
      )
    return {
      "pairs": pairs,
      "dataframe_updates": dataframe_updates,
      "whitelist": whitelist,
      "open_trade_count": open_trade_count,
      "open_trade_tags": open_trade_tags,
      "result_tail_rows": self._test_x7_process_result_tail_rows(),
    }

  def _test_x7_stable_preload_payload(
    self,
    worker_index: int,
    pairs: list[str],
    whitelist: list[str],
    source_dataframes: dict[str, DataFrame],
  ) -> dict[str, Any]:
    dataframe_updates = {}
    for pair in pairs:
      source_dataframe = source_dataframes[pair]
      base_date = self._test_x7_last_date(source_dataframe)
      base_key = (pair, self.timeframe)
      dataframe_updates[base_key] = self._test_x7_dataframe_update(
        worker_index,
        base_key,
        self._test_x7_maybe_tail_payload_dataframe(source_dataframe, self.timeframe),
        base_date,
        self.timeframe,
      )
      for timeframe in self.info_timeframes:
        key = (pair, timeframe)
        dataframe_updates[key] = self._test_x7_dataframe_update(
          worker_index,
          key,
          self._test_x7_maybe_tail_payload_dataframe(self.dp.get_pair_dataframe(pair=pair, timeframe=timeframe), timeframe),
          base_date,
          timeframe,
        )

    btc_info_pair = self._test_x7_btc_info_pair()
    base_date = self._test_x7_last_date(source_dataframes[pairs[0]]) if pairs else None
    for timeframe in self.btc_info_timeframes:
      key = (btc_info_pair, timeframe)
      if key in dataframe_updates:
        continue
      dataframe_updates[key] = self._test_x7_dataframe_update(
        worker_index,
        key,
        self._test_x7_maybe_tail_payload_dataframe(self.dp.get_pair_dataframe(pair=btc_info_pair, timeframe=timeframe), timeframe),
        base_date,
        timeframe,
      )
    return {
      "pairs": [],
      "dataframe_updates": dataframe_updates,
      "whitelist": whitelist,
      "open_trade_count": 0,
      "open_trade_tags": [],
      "result_tail_rows": 0,
    }

  def _test_x7_stable_reuse_payload(
    self,
    pairs: list[str],
    whitelist: list[str],
  ) -> dict[str, Any]:
    dataframe_updates = {}
    for pair in pairs:
      dataframe_updates[(pair, self.timeframe)] = {"mode": "reuse"}
      for timeframe in self.info_timeframes:
        dataframe_updates[(pair, timeframe)] = {"mode": "reuse"}

    btc_info_pair = self._test_x7_btc_info_pair()
    for timeframe in self.btc_info_timeframes:
      dataframe_updates[(btc_info_pair, timeframe)] = {"mode": "reuse"}

    return {
      "pairs": pairs,
      "dataframe_updates": dataframe_updates,
      "whitelist": whitelist,
      "open_trade_count": 0,
      "open_trade_tags": [],
      "result_tail_rows": 0,
      "discard_results": True,
    }

  def _test_x7_rehydrate_analyzed_dataframe(self, source: DataFrame, analyzed: DataFrame) -> DataFrame:
    if len(source) == len(analyzed):
      return analyzed

    dataframe = source.copy(deep=False)
    for column in dict.fromkeys(str(column) for column in analyzed.columns):
      if column in source.columns:
        continue
      value = analyzed[column]
      if isinstance(value, DataFrame):
        value = value.iloc[:, -1]
      if column in {"enter_long", "enter_short", "exit_long", "exit_short"}:
        dataframe[column] = 0
      elif column in {"enter_tag", "exit_tag"}:
        dataframe[column] = ""
      else:
        dataframe[column] = pd.Series(index=dataframe.index, dtype=value.dtype)

      dataframe.loc[analyzed.index, column] = value.to_numpy(copy=False)
    return dataframe

  def _test_x7_validate_analyzed_dataframe(self, pair: str, source: DataFrame, dataframe: DataFrame) -> None:
    if len(source) == len(dataframe):
      validator = StrategyResultValidator(source, warn_only=not self.disable_dataframe_checks)
      validator.assert_df(dataframe)
      return

    message = ""
    if dataframe is None or dataframe.empty:
      message = "No dataframe returned (return statement missing?)."
    elif source["close"].iloc[-1] != dataframe["close"].iloc[-1]:
      message = "Dataframe returned from strategy has mismatching last close price."
    elif source["date"].iloc[-1] != dataframe["date"].iloc[-1]:
      message = "Dataframe returned from strategy has mismatching last date."
    if message:
      if not self.disable_dataframe_checks:
        log.warning("TestX7 process-tail validation warning for pair=%s: %s", pair, message)
      else:
        raise StrategyError(message)

  def _test_x7_store_analyzed_dataframe(self, pair: str, source: DataFrame, dataframe: DataFrame) -> None:
    if self._test_x7_process_tail_rows() <= 0 and self._test_x7_process_result_tail_rows() <= 0:
      dataframe = self._test_x7_rehydrate_analyzed_dataframe(source, dataframe)

    self._test_x7_validate_analyzed_dataframe(pair, source, dataframe)
    if dataframe.empty:
      log.warning("Empty dataframe for pair %s", pair)
      return

    last_seen = getattr(self, "_IStrategy__last_candle_seen_per_pair", None)
    if not isinstance(last_seen, dict):
      last_seen = {}
      setattr(self, "_IStrategy__last_candle_seen_per_pair", last_seen)
    last_seen[pair] = dataframe.iloc[-1]["date"]
    candle_type = self.config.get("candle_type_def", CandleType.SPOT)
    self.dp._set_cached_df(pair, self.timeframe, dataframe, candle_type=candle_type)
    self.dp._emit_df((pair, self.timeframe, candle_type), dataframe, True)

  def _test_x7_process_analyze(self, pairs: list[str]) -> None:
    workers = self._test_x7_process_workers(len(pairs))
    chunks = self._test_x7_process_chunks(pairs, workers)
    whitelist = self.dp.current_whitelist()
    open_trade_count, open_trade_tags = self._test_x7_open_trade_snapshot()
    source_dataframes = {
      pair: self.dp.ohlcv(pair, self.timeframe, candle_type=self.config.get("candle_type_def", CandleType.SPOT))
      for pair in pairs
    }

    filtered_chunks = []
    last_seen = getattr(self, "_IStrategy__last_candle_seen_per_pair", {})
    for chunk in chunks:
      filtered = []
      for pair in chunk:
        dataframe = source_dataframes[pair]
        if not isinstance(dataframe, DataFrame) or dataframe.empty:
          log.warning("Empty candle (OHLCV) data for pair %s", pair)
          continue
        new_candle = last_seen.get(pair, None) != dataframe.iloc[-1]["date"]
        if self.process_only_new_candles and not new_candle:
          continue
        filtered.append(pair)
      if filtered:
        filtered_chunks.append(filtered)

    if not filtered_chunks:
      return

    if not hasattr(self, "_test_x7_process_pool"):
      context = multiprocessing.get_context("fork")
      self._test_x7_process_pool = ProcessPoolExecutor(
        max_workers=workers,
        mp_context=context,
        initializer=_init_process_worker,
        initargs=(
          os.path.dirname(sys.modules[type(self).__module__].__file__ or ""),
          type(self).__module__,
          type(self).__name__,
          self.config,
          self._test_x7_process_runmode(),
        ),
      )

    futures = [
      self._test_x7_process_pool.submit(
        _run_process_chunk,
        self._test_x7_process_payload(chunk, whitelist, open_trade_count, open_trade_tags, source_dataframes),
      )
      for chunk in filtered_chunks
    ]
    for future in as_completed(futures):
      try:
        for item in future.result():
          pair, dataframe = item[:2]
          self._test_x7_store_analyzed_dataframe(pair, source_dataframes[pair], dataframe)
      except (StrategyError, Exception):
        log.exception("TestX7 process analyze failed")
        raise

  def _test_x7_stable_process_initargs(self) -> tuple[Any, ...]:
    return (
      os.path.dirname(sys.modules[type(self).__module__].__file__ or ""),
      type(self).__module__,
      type(self).__name__,
      self.config,
      self._test_x7_process_runmode(),
    )

  def _test_x7_ensure_stable_process_workers(self, workers: int) -> None:
    existing = getattr(self, "_test_x7_stable_processes", None)
    if existing is not None and len(existing) == workers:
      return

    self._test_x7_stop_stable_process_workers()
    self._test_x7_apply_numeric_thread_limit()
    context = multiprocessing.get_context("fork")
    response_queue = context.Queue()
    processes = []
    initargs = self._test_x7_stable_process_initargs()
    for worker_index in range(workers):
      request_queue = context.Queue()
      process = context.Process(
        target=_stable_process_worker_loop,
        args=(worker_index, request_queue, response_queue, initargs),
        daemon=True,
      )
      process.start()
      processes.append((process, request_queue))

    self._test_x7_stable_processes = processes
    self._test_x7_stable_response_queue = response_queue
    self._test_x7_stable_dataframe_signatures = {}
    self._test_x7_stable_time_buckets = {}
    self._test_x7_stable_loop_id = 0
    self._test_x7_stable_dataframes_prewarmed = False
    if not getattr(self, "_test_x7_stable_cleanup_registered", False):
      atexit.register(self._test_x7_stop_stable_process_workers)
      self._test_x7_stable_cleanup_registered = True

  def _test_x7_prewarm_stable_process_workers(self) -> None:
    if not hasattr(self, "dp"):
      return

    try:
      pairs = self.dp.current_whitelist()
    except Exception:
      return

    if not pairs or not self._test_x7_stable_process_enabled(len(pairs)):
      return

    workers = self._test_x7_stable_process_workers(len(pairs))
    chunks = self._test_x7_stable_process_chunks(pairs, workers)
    if chunks:
      self._test_x7_ensure_stable_process_workers(len(chunks))
      self._test_x7_prewarm_stable_process_dataframes(pairs, chunks)

  def _test_x7_prewarm_stable_process_dataframes(self, pairs: list[str], chunks: list[list[str]]) -> None:
    if not self._test_x7_stable_prewarm_dataframes_enabled():
      return
    if getattr(self, "_test_x7_stable_dataframes_prewarmed", False):
      return

    try:
      source_dataframes = {
        pair: self.dp.ohlcv(pair, self.timeframe, candle_type=self.config.get("candle_type_def", CandleType.SPOT))
        for pair in pairs
      }
      whitelist = self.dp.current_whitelist()
      self._test_x7_stable_loop_id += 1
      loop_id = self._test_x7_stable_loop_id
      processes = self._test_x7_stable_processes
      pending = set()
      for worker_index, chunk in enumerate(chunks):
        payload = self._test_x7_stable_preload_payload(worker_index, chunk, whitelist, source_dataframes)
        processes[worker_index][1].put((loop_id, payload))
        pending.add(worker_index)

      for _worker_index, _result in self._test_x7_wait_stable_responses(loop_id, pending, "dataframe prewarm"):
        pass
      self._test_x7_stable_dataframes_prewarmed = True
      if self._test_x7_stable_prewarm_compute_enabled():
        self._test_x7_stable_loop_id += 1
        loop_id = self._test_x7_stable_loop_id
        pending = set()
        for worker_index, chunk in enumerate(chunks):
          payload = self._test_x7_stable_reuse_payload(chunk, whitelist)
          processes[worker_index][1].put((loop_id, payload))
          pending.add(worker_index)

        for _worker_index, _result in self._test_x7_wait_stable_responses(loop_id, pending, "compute prewarm"):
          pass
    except Exception:
      log.exception("TestX7 stable dataframe prewarm failed")
      self._test_x7_stop_stable_process_workers()

  def bot_start(self, **kwargs) -> None:
    result = super().bot_start(**kwargs)
    self._test_x7_prewarm_stable_process_workers()
    return result

  def bot_loop_start(self, current_time, **kwargs) -> None:
    result = super().bot_loop_start(current_time, **kwargs)
    self._test_x7_prewarm_stable_process_workers()
    return result

  def _test_x7_stop_stable_process_workers(self) -> None:
    existing = getattr(self, "_test_x7_stable_processes", None)
    if not existing:
      return
    response_queue = getattr(self, "_test_x7_stable_response_queue", None)
    for process, request_queue in existing:
      try:
        request_queue.put(None)
      except Exception:
        pass
    for process, _ in existing:
      try:
        process.join(timeout=1)
      except Exception:
        pass
      if process.is_alive():
        try:
          process.terminate()
        except Exception:
          pass
      try:
        process.join(timeout=1)
      except Exception:
        pass
    for _process, request_queue in existing:
      try:
        request_queue.close()
      except Exception:
        pass
    if response_queue is not None:
      try:
        response_queue.close()
      except Exception:
        pass
    self._test_x7_stable_processes = None
    self._test_x7_stable_response_queue = None
    self._test_x7_stable_dataframe_signatures = {}
    self._test_x7_stable_time_buckets = {}
    self._test_x7_stable_dataframes_prewarmed = False

  def _test_x7_stable_process_analyze(self, pairs: list[str]) -> None:
    workers = self._test_x7_stable_process_workers(len(pairs))
    chunks = self._test_x7_stable_process_chunks(pairs, workers)
    self._test_x7_ensure_stable_process_workers(len(chunks))

    whitelist = self.dp.current_whitelist()
    open_trade_count, open_trade_tags = self._test_x7_open_trade_snapshot()
    source_dataframes = {
      pair: self.dp.ohlcv(pair, self.timeframe, candle_type=self.config.get("candle_type_def", CandleType.SPOT))
      for pair in pairs
    }

    filtered_chunks = []
    last_seen = getattr(self, "_IStrategy__last_candle_seen_per_pair", {})
    for worker_index, chunk in enumerate(chunks):
      filtered = []
      for pair in chunk:
        dataframe = source_dataframes[pair]
        if not isinstance(dataframe, DataFrame) or dataframe.empty:
          log.warning("Empty candle (OHLCV) data for pair %s", pair)
          continue
        new_candle = last_seen.get(pair, None) != dataframe.iloc[-1]["date"]
        if self.process_only_new_candles and not new_candle:
          continue
        filtered.append(pair)
      if filtered:
        filtered_chunks.append((worker_index, filtered))

    if not filtered_chunks:
      return

    self._test_x7_stable_loop_id += 1
    loop_id = self._test_x7_stable_loop_id
    processes = self._test_x7_stable_processes
    pending = set()
    for worker_index, chunk in filtered_chunks:
      payload = self._test_x7_stable_process_payload(
        worker_index,
        chunk,
        whitelist,
        open_trade_count,
        open_trade_tags,
        source_dataframes,
      )
      processes[worker_index][1].put((loop_id, payload))
      pending.add(worker_index)

    for _worker_index, result in self._test_x7_wait_stable_responses(loop_id, pending, "process analyze"):
      for item in result:
        pair, dataframe = item[:2]
        self._test_x7_store_analyzed_dataframe(pair, source_dataframes[pair], dataframe)

  def analyze(self, pairs: list[str]) -> None:
    if self._test_x7_stable_process_enabled(len(pairs)):
      try:
        return self._test_x7_stable_process_analyze(pairs)
      except Exception:
        self._test_x7_stop_stable_process_workers()
        if not self._test_x7_stable_fallback_enabled():
          raise
        log.exception("TestX7 stable process analyze failed; falling back to sequential Freqtrade analyze")
        return super().analyze(pairs)

    if self._test_x7_process_enabled(len(pairs)):
      return self._test_x7_process_analyze(pairs)

    workers = self._test_x7_analyze_workers(len(pairs))
    if workers <= 1 or len(pairs) <= 1:
      return super().analyze(pairs)

    with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="testx7-analyze") as executor:
      futures = {executor.submit(self.analyze_pair, pair): pair for pair in pairs}
      for future in as_completed(futures):
        pair = futures[future]
        try:
          future.result()
        except Exception:
          log.exception("TestX7 parallel analyze failed for pair=%s", pair)
          raise

  def bot_stop(self, **kwargs):
    self._test_x7_stop_stable_process_workers()
    parent = getattr(super(), "bot_stop", None)
    if callable(parent):
      return parent(**kwargs)
    return None
