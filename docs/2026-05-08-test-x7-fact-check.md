# Test X7 Fact Check

Date: 2026-05-08 KST

## NFI Baseline

- Upstream repo: `https://github.com/iterativv/NostalgiaForInfinity`
- Local external checkout updated to upstream `origin/main` commit `75c223b0f1a76731f4555aeb70fd0c92df9f30ea`.
- The latest upstream delta after the previous `049216fc319f9be38077019bb4641d09696f51df` baseline changed only `docker/updater/update_nfi.sh`, not the X6/X7 strategy files.
- Active local `user_data/strategies/NostalgiaForInfinityX7.py` is byte-identical to `external/NostalgiaForInfinity/NostalgiaForInfinityX7.py`.
- Latest synced X7 `version()` is `v17.4.59`.
- Active local NFI strategy family versions after sync:
  - `NostalgiaForInfinityX`: `v11.3.133`
  - `NostalgiaForInfinityX2`: `v12.0.640`
  - `NostalgiaForInfinityX3`: `v13.2.9`
  - `NostalgiaForInfinityX4`: `v14.2.9`
  - `NostalgiaForInfinityX5`: `v15.1.399`
  - `NostalgiaForInfinityX6`: `v16.8.798`
  - `NostalgiaForInfinityX7`: `v17.4.59`

## Freqtrade Strategy Loading

Official docs:

- Strategy customization: `https://docs.freqtrade.io/en/latest/strategy-customization/`
- Strategy callbacks: `https://docs.freqtrade.io/en/latest/strategy-callbacks/`

Local runtime source checked from Docker image `freqtradeorg/freqtrade:stable`, Freqtrade `2026.4`.

`freqtrade.resolvers.strategy_resolver.StrategyResolver.load_strategy()` requires one configured strategy name:

```python
if not config.get("strategy"):
    raise OperationalException(
        "No strategy set. Please use `--strategy` to specify the strategy class to use."
    )

strategy_name = config["strategy"]
strategy: IStrategy = StrategyResolver._load_strategy(
    strategy_name, config=config, extra_dir=config.get("strategy_path")
)
```

Conclusion:

- `user_data/strategies/` is a discovery path.
- `list-strategies` lists loadable classes, but trading uses the one configured `strategy` class.
- Multiple strategy files in the folder do not combine trading decisions.
- `NostalgiaForInfinityX7` and `TestX7` can coexist; the active one is selected by config or CLI.

## Freqtrade Analysis Flow

Runtime source checked from `/freqtrade/freqtrade/strategy/interface.py`:

```python
def analyze(self, pairs: list[str]) -> None:
    for pair in pairs:
        self.analyze_pair(pair)
```

Runtime source checked from `/freqtrade/freqtrade/freqtradebot.py`:

```python
with self._measure_execution:
    self.strategy.analyze(self.active_pair_whitelist)
```

Conclusion:

- In Freqtrade `2026.4`, pair analysis in `IStrategy.analyze(pairs)` is sequential at the core strategy API level.
- `analyze_pair(pair)` fetches the dataframe, calls the strategy analysis path, validates the result, and stores the analyzed dataframe.
- `analyze_ticker()` calls:
  1. `advise_indicators()`
  2. `advise_entry()`
  3. `advise_exit()`
- `advise_indicators()` calls strategy `populate_indicators()`.
- `advise_entry()` calls strategy `populate_entry_trend()`.
- `advise_exit()` calls strategy `populate_exit_trend()`.

## Strategy Analysis Warning

Runtime source checked from `/freqtrade/freqtrade/freqtradebot.py`:

```python
self._measure_execution = MeasureTime(log_took_too_long, timeframe_secs * 0.25)
```

For X7's required `5m` timeframe, `timeframe_secs * 0.25` is `75s`.

Conclusion:

- A logged `Strategy analysis took ...` warning means the whole pairlist analysis took more than 25% of the timeframe.
- For `5m`, the warning threshold is about `75s`.
- 60s/70s analysis loops are still operationally slow, but this specific Freqtrade warning should normally appear at roughly 75s+ for 5m.

## CPU And Parallelism

Local WSL CPU view:

- Logical CPUs available: `4`
- Physical cores visible: `2`
- Thread(s) per core: `2`

NFI X7 source facts:

- `num_cores_indicators_calc = 0`
- `num_cores_indicators_calc` is listed in `NFI_SAFE_PARAMETERS`.
- The historical `df.ta.study(..., cores=self.num_cores_indicators_calc)` calls are currently commented out in X7.
- Current X7 mostly calls direct `pandas_ta` functions, so that `cores` setting does not materially parallelize the active indicator path.

Conclusion:

- The major core-level pair loop is sequential in Freqtrade `2026.4`.
- Current X7 does not actively use its commented pandas-ta `study(..., cores=...)` blocks.
- A safe first optimization boundary is inside `TestX7`: mechanically extract indicator/informative and entry logic, cache repeated BTC informative data, and add profiling without changing entry/exit/DCA/grind meaning.
- The local conservative worker default is `2` because WSL reports `4` logical CPUs and `2` physical cores.
- Short worker benchmark for `TEST_X7_WORKERS=1`, `2`, `3`, and `4` produced the same `13s` runtime and identical trade surface on `BTC/USDT`, `ETH/USDT`, `OP/USDT`, and `FLOW/USDT` over `20260301-20260308`.
- Worker conclusion: `2` remains the safe default, but worker count is not a meaningful speed lever until the active indicator path uses worker-aware pandas-ta calls or another explicit parallel execution boundary.

## TestX7 Cleanup Plan

Behavior lock:

- Keep upstream `NostalgiaForInfinityX7` as the immutable baseline.
- Load `NostalgiaForInfinityX7` and `TestX7` side by side.
- Compare short backtests before accepting any performance change.

Pass order:

1. Create thin `TestX7` strategy entrypoint.
2. Move CPU sizing, profiling, BTC informative cache, entry optimization, indicator/informative logic, entry logic, and parity helpers into `test_x7_modules`.
3. Add conservative BTC informative cache, keyed by pair, timeframe, source row count, last date, and source columns.
4. Run syntax/list-strategy checks.
5. Run original X7 vs TestX7 parity backtests.
6. Run 1-year local backtests and compare result/performance.
7. Run short worker/core benchmark for 1/2/3/4 workers before claiming worker-based speed-up.
8. After mechanical extraction, rerun short parity and 364-day local parity before treating TestX7 as equivalent.
9. For each hot-path optimization, change one narrow behavior-preserving slice, then rerun short parity and 364-day local parity before accepting it.
