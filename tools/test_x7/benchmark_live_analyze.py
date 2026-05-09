#!/usr/bin/env python3
"""Benchmark one Freqtrade-style strategy analyze(pairs) loop.

This is a local harness for TestX7 optimization work.  It loads local feather
OHLCV data, provides the minimum DataProvider surface used by NFI X7, and calls
the real strategy ``analyze(pairs)`` method.  It is intentionally separate from
backtesting because Freqtrade backtesting does not exercise the live pair-loop
``IStrategy.analyze`` method that emits "Strategy analysis took ..." warnings.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import importlib
import json
import logging
from pathlib import Path
import sys
import time
from typing import Any

import pandas as pd
from freqtrade.enums import CandleType, RunMode

_WORKER_STRATEGY = None
_WORKER_DP = None
_WORKER_FINGERPRINT = True


class _RunModeValue:
  def __init__(self, value: str) -> None:
    self.value = value


def _patch_trade_methods_for_live_loop() -> None:
  """Avoid DB access when the local harness simulates a dry/live runmode."""
  from freqtrade.persistence import Trade

  Trade.get_open_trade_count = staticmethod(lambda: 0)
  Trade.get_trades_proxy = staticmethod(lambda *args, **kwargs: [])


class LocalDataProvider:
  def __init__(self, data_dir: Path, pairs: list[str], rows: int, runmode: str) -> None:
    self.data_dir = data_dir
    self._pairs = pairs
    self._rows = rows
    self.runmode = _RunModeValue(runmode)
    self.cached: dict[tuple[str, str], pd.DataFrame] = {}
    self.emitted: list[tuple[Any, int, bool]] = []
    self._raw_cache: dict[tuple[str, str], pd.DataFrame] = {}
    self._window_cache: dict[tuple[str, str, int, int], pd.DataFrame] = {}
    self._window_offset = 0

  def current_whitelist(self) -> list[str]:
    return list(self._pairs)

  def _filename(self, pair: str, timeframe: str) -> Path:
    pair_name = pair.split(":", 1)[0].replace("/", "_")
    return self.data_dir / f"{pair_name}-{timeframe}.feather"

  def _timeframe_window_offset(self, timeframe: str) -> int:
    timeframe_steps = {
      "5m": 1,
      "15m": 3,
      "1h": 12,
      "4h": 48,
      "1d": 288,
    }
    return self._window_offset // timeframe_steps.get(timeframe, 1)

  def _load(self, pair: str, timeframe: str) -> pd.DataFrame:
    key = (pair, timeframe)
    cached = self._raw_cache.get(key)
    if cached is None:
      path = self._filename(pair, timeframe)
      if not path.exists():
        raise FileNotFoundError(f"Missing local candle data: {path}")
      cached = pd.read_feather(path)
      self._raw_cache[key] = cached
    if self._rows > 0:
      window_offset = self._timeframe_window_offset(timeframe)
      window_key = (pair, timeframe, self._rows, window_offset)
      window = self._window_cache.get(window_key)
      if window is not None:
        return window.copy(deep=False)
      end = len(cached) - window_offset if window_offset > 0 else len(cached)
      start = max(0, end - self._rows)
      cached = cached.iloc[start:end].reset_index(drop=True)
      self._window_cache[window_key] = cached
    return cached.copy(deep=False)

  def set_window_offset(self, window_offset: int) -> None:
    self._window_offset = max(0, window_offset)

  def ohlcv(self, pair: str, timeframe: str, candle_type: CandleType | None = None) -> pd.DataFrame:
    return self._load(pair, timeframe)

  def get_pair_dataframe(self, pair: str, timeframe: str) -> pd.DataFrame:
    return self._load(pair, timeframe)

  def _set_cached_df(
    self,
    pair: str,
    timeframe: str,
    dataframe: pd.DataFrame,
    candle_type: CandleType | None = None,
  ) -> None:
    self.cached[(pair, timeframe)] = dataframe

  def _emit_df(self, key: Any, dataframe: pd.DataFrame, new_candle: bool) -> None:
    self.emitted.append((key, len(dataframe), new_candle))


def _deep_update(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
  for key, value in override.items():
    if isinstance(value, dict) and isinstance(base.get(key), dict):
      _deep_update(base[key], value)
    else:
      base[key] = value
  return base


def _load_config(path: Path, extra_paths: list[Path]) -> dict[str, Any]:
  config = json.loads(path.read_text(encoding="utf-8"))
  for extra_path in extra_paths:
    _deep_update(config, json.loads(extra_path.read_text(encoding="utf-8")))
  config["user_data_dir"] = path.parent
  config["runmode"] = RunMode.BACKTEST
  config["candle_type_def"] = CandleType.SPOT
  return config


def _strategy_class(strategy_name: str):
  module = importlib.import_module(strategy_name)
  return getattr(module, strategy_name)


def _available_pairs(
  config: dict[str, Any],
  data_dir: Path,
  required_timeframes: tuple[str, ...],
  limit: int,
) -> list[str]:
  pairs = []
  for pair in config["exchange"]["pair_whitelist"]:
    pair_name = pair.split(":", 1)[0].replace("/", "_")
    if all((data_dir / f"{pair_name}-{timeframe}.feather").exists() for timeframe in required_timeframes):
      pairs.append(pair)
    if limit > 0 and len(pairs) >= limit:
      break
  return pairs


def _fingerprint(dp: LocalDataProvider) -> dict[str, dict[str, Any]]:
  result = {}
  for (pair, timeframe), dataframe in sorted(dp.cached.items()):
    last = dataframe.iloc[-1]
    result[pair] = {
      "rows": int(len(dataframe)),
      "last_date": str(last.get("date")),
      "enter_long": int(last.get("enter_long", 0) or 0),
      "enter_short": int(last.get("enter_short", 0) or 0),
      "enter_tag": str(last.get("enter_tag", "") or ""),
      "exit_long": int(last.get("exit_long", 0) or 0),
      "exit_short": int(last.get("exit_short", 0) or 0),
    }
  return result


def _run_analyze_worker(
  strategy_name: str,
  config: dict[str, Any],
  strategy_dir: str,
  data_dir: str,
  pairs: list[str],
  rows: int,
  include_fingerprint: bool,
  runmode: str,
) -> dict[str, Any]:
  sys.path.insert(0, strategy_dir)
  if runmode not in {"backtest", "hyperopt", "plot", "webserver"}:
    _patch_trade_methods_for_live_loop()
  worker_config = dict(config)
  worker_config["exchange"] = dict(config["exchange"])
  worker_config["exchange"]["pair_whitelist"] = pairs
  worker_config["test_x7_parallel_analyze_workers"] = 1
  cls = _strategy_class(strategy_name)
  strategy = cls(worker_config)
  dp = LocalDataProvider(Path(data_dir), pairs, rows, runmode)
  strategy.dp = dp

  started = time.perf_counter()
  strategy.analyze(pairs)
  seconds = time.perf_counter() - started
  return {
    "pairs": len(pairs),
    "seconds": seconds,
    "cached_pairs": len(dp.cached),
    "emitted": len(dp.emitted),
    "fingerprint": _fingerprint(dp) if include_fingerprint else {},
  }


def _init_persistent_worker(
  strategy_name: str,
  config: dict[str, Any],
  strategy_dir: str,
  data_dir: str,
  rows: int,
  include_fingerprint: bool,
  runmode: str,
) -> None:
  global _WORKER_STRATEGY, _WORKER_DP, _WORKER_FINGERPRINT

  sys.path.insert(0, strategy_dir)
  if runmode not in {"backtest", "hyperopt", "plot", "webserver"}:
    _patch_trade_methods_for_live_loop()
  cls = _strategy_class(strategy_name)
  worker_config = dict(config)
  worker_config["exchange"] = dict(config["exchange"])
  worker_config["test_x7_parallel_analyze_workers"] = 1
  _WORKER_STRATEGY = cls(worker_config)
  _WORKER_DP = LocalDataProvider(Path(data_dir), config["exchange"]["pair_whitelist"], rows, runmode)
  _WORKER_STRATEGY.dp = _WORKER_DP
  _WORKER_FINGERPRINT = include_fingerprint


def _run_persistent_worker(pairs: list[str]) -> dict[str, Any]:
  if _WORKER_STRATEGY is None or _WORKER_DP is None:
    raise RuntimeError("Persistent worker was not initialized")

  # Re-running identical local candle data must simulate a fresh live candle
  # loop.  Otherwise Freqtrade's process_only_new_candles cache correctly skips
  # the second pass and hides the true compute cost.
  setattr(_WORKER_STRATEGY, "_IStrategy__last_candle_seen_per_pair", {})
  started = time.perf_counter()
  _WORKER_STRATEGY.analyze(pairs)
  seconds = time.perf_counter() - started
  return {
    "pairs": len(pairs),
    "seconds": seconds,
    "cached_pairs": len(_WORKER_DP.cached),
    "emitted": len(_WORKER_DP.emitted),
    "fingerprint": _fingerprint(_WORKER_DP) if _WORKER_FINGERPRINT else {},
    "profile": _WORKER_STRATEGY.test_x7_profile_summary()
    if hasattr(_WORKER_STRATEGY, "test_x7_profile_summary")
    else [],
  }


def _chunks(items: list[str], count: int) -> list[list[str]]:
  return [items[index::count] for index in range(count) if items[index::count]]


def _chunks_by_size(items: list[str], size: int) -> list[list[str]]:
  return [items[index : index + size] for index in range(0, len(items), size)]


def _aggregate_profiles(profiles: list[dict[str, Any]]) -> list[dict[str, Any]]:
  stages: dict[str, dict[str, float]] = {}
  for row in profiles:
    stage = str(row.get("stage", "unknown"))
    item = stages.setdefault(stage, {"count": 0.0, "total_seconds": 0.0, "max_seconds": 0.0})
    item["count"] += float(row.get("count", 0.0) or 0.0)
    item["total_seconds"] += float(row.get("total_seconds", 0.0) or 0.0)
    item["max_seconds"] = max(item["max_seconds"], float(row.get("max_seconds", 0.0) or 0.0))

  summary = []
  for stage, item in stages.items():
    count = item["count"] or 1.0
    summary.append(
      {
        "stage": stage,
        "count": int(item["count"]),
        "total_seconds": item["total_seconds"],
        "avg_seconds": item["total_seconds"] / count,
        "max_seconds": item["max_seconds"],
      }
    )
  return sorted(summary, key=lambda row: row["total_seconds"], reverse=True)


def main() -> int:
  parser = argparse.ArgumentParser()
  parser.add_argument("--strategy", default="TestX7")
  parser.add_argument("--config", type=Path, default=Path("user_data/config-test-x7.example.json"))
  parser.add_argument("--config-extra", type=Path, action="append", default=[])
  parser.add_argument("--strategy-dir", type=Path, default=Path("user_data/strategies"))
  parser.add_argument("--data-dir", type=Path, default=Path("user_data/data/binance"))
  parser.add_argument("--rows", type=int, default=1200)
  parser.add_argument("--limit-pairs", type=int, default=0)
  parser.add_argument("--process-workers", type=int, default=1)
  parser.add_argument("--persistent-process-workers", type=int, default=0)
  parser.add_argument("--chunk-size", type=int, default=0)
  parser.add_argument("--repeat", type=int, default=1)
  parser.add_argument("--runmode", default="backtest")
  parser.add_argument("--advance-window", action="store_true")
  parser.add_argument("--prewarm", action="store_true")
  parser.add_argument("--prewarm-wait-seconds", type=float, default=0.0)
  parser.add_argument("--no-fingerprint", action="store_true")
  parser.add_argument("--json", action="store_true")
  args = parser.parse_args()
  logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")

  sys.path.insert(0, str(args.strategy_dir.resolve()))
  if args.runmode not in {"backtest", "hyperopt", "plot", "webserver"}:
    _patch_trade_methods_for_live_loop()

  config = _load_config(args.config, args.config_extra)
  cls = _strategy_class(args.strategy)
  strategy = cls(config)
  required_timeframes = tuple(dict.fromkeys([strategy.timeframe, *strategy.info_timeframes]))
  pairs = _available_pairs(config, args.data_dir, required_timeframes, args.limit_pairs)
  config["exchange"]["pair_whitelist"] = pairs

  started = time.perf_counter()
  if args.persistent_process_workers > 1:
    workers = min(args.persistent_process_workers, len(pairs))
    chunks = _chunks_by_size(pairs, args.chunk_size) if args.chunk_size > 0 else _chunks(pairs, workers)
    loop_results = []
    with ProcessPoolExecutor(
      max_workers=workers,
      initializer=_init_persistent_worker,
      initargs=(
        args.strategy,
        config,
        str(args.strategy_dir.resolve()),
        str(args.data_dir),
        args.rows,
        not args.no_fingerprint,
        args.runmode,
      ),
    ) as executor:
      for loop_index in range(args.repeat):
        loop_started = time.perf_counter()
        worker_results = [future.result() for future in as_completed([executor.submit(_run_persistent_worker, chunk) for chunk in chunks])]
        loop_seconds = time.perf_counter() - loop_started
        loop_results.append({"loop": loop_index + 1, "seconds": loop_seconds, "workers": worker_results})
    seconds = time.perf_counter() - started
    fingerprint = {}
    cached_pairs = 0
    emitted = 0
    profiles = []
    for result in loop_results[-1]["workers"]:
      fingerprint.update(result["fingerprint"])
      cached_pairs += result["cached_pairs"]
      emitted += result["emitted"]
      profiles.extend(result.get("profile", []))
  elif args.process_workers > 1:
    workers = min(args.process_workers, len(pairs))
    worker_results = []
    with ProcessPoolExecutor(max_workers=workers) as executor:
      futures = [
        executor.submit(
          _run_analyze_worker,
          args.strategy,
          config,
          str(args.strategy_dir.resolve()),
          str(args.data_dir),
          chunk,
          args.rows,
          not args.no_fingerprint,
          args.runmode,
        )
        for chunk in _chunks(pairs, workers)
      ]
      for future in as_completed(futures):
        worker_results.append(future.result())
    seconds = time.perf_counter() - started
    fingerprint = {}
    cached_pairs = 0
    emitted = 0
    profiles = []
    for result in worker_results:
      fingerprint.update(result["fingerprint"])
      cached_pairs += result["cached_pairs"]
      emitted += result["emitted"]
  else:
    dp = LocalDataProvider(args.data_dir, pairs, args.rows, args.runmode)
    strategy.dp = dp
    if args.prewarm:
      if args.advance_window and args.repeat > 0:
        dp.set_window_offset(args.repeat - 1)
      strategy.bot_start()
      if args.prewarm_wait_seconds > 0:
        time.sleep(args.prewarm_wait_seconds)
    loop_results = []
    for loop_index in range(args.repeat):
      if args.advance_window:
        dp.set_window_offset(args.repeat - loop_index - 1)
      setattr(strategy, "_IStrategy__last_candle_seen_per_pair", {})
      loop_started = time.perf_counter()
      strategy.analyze(pairs)
      loop_results.append({"loop": loop_index + 1, "seconds": time.perf_counter() - loop_started})
    seconds = time.perf_counter() - started
    fingerprint = _fingerprint(dp) if not args.no_fingerprint else {}
    cached_pairs = len(dp.cached)
    emitted = len(dp.emitted)
    profiles = strategy.test_x7_profile_summary() if hasattr(strategy, "test_x7_profile_summary") else []

  output = {
    "strategy": args.strategy,
    "pairs": len(pairs),
    "rows": args.rows,
    "process_workers": args.process_workers,
    "persistent_process_workers": args.persistent_process_workers,
    "repeat": args.repeat,
    "seconds": round(seconds, 6),
    "cached_pairs": cached_pairs,
    "emitted": emitted,
    "profile_by_stage": _aggregate_profiles(profiles),
    "profile": profiles,
    "fingerprint": fingerprint,
  }

  if args.json:
    print(json.dumps(output, indent=2, sort_keys=True))
  else:
    if loop_results:
      loop_text = " ".join(f"loop{item['loop']}={item['seconds']:.6f}s" for item in loop_results)
      print(loop_text)
      if args.persistent_process_workers > 1:
        last_workers = sorted(loop_results[-1]["workers"], key=lambda item: item["seconds"], reverse=True)
        worker_text = " ".join(f"worker_pairs={item['pairs']}:{item['seconds']:.6f}s" for item in last_workers)
        print(worker_text)
    print(
      f"strategy={output['strategy']} pairs={output['pairs']} rows={output['rows']} "
      f"seconds={output['seconds']} cached_pairs={output['cached_pairs']} emitted={output['emitted']}"
    )
    for row in output["profile_by_stage"][:12]:
      print(
        f"profile stage={row['stage']} count={row['count']} "
        f"total={row['total_seconds']:.6f}s avg={row['avg_seconds']:.6f}s max={row['max_seconds']:.6f}s"
      )
    analyze_pairs = [row for row in profiles if row.get("stage") == "analyze_pair"]
    for row in sorted(analyze_pairs, key=lambda item: item.get("total_seconds", 0.0), reverse=True)[:12]:
      print(
        f"profile_pair pair={row['pair']} count={row['count']} "
        f"total={row['total_seconds']:.6f}s avg={row['avg_seconds']:.6f}s max={row['max_seconds']:.6f}s"
      )
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
