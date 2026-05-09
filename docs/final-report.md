# TestX7 Final Report

This report is the single developer-facing summary for the `TestX7` proof package.

The goal was not to tune NFI X7 for higher profit. The goal was narrower and easier to verify:

> Keep the checked NFI X7 trading behavior the same, but make the live pair-analysis loop much faster.

## Final Result

The original `NostalgiaForInfinityX7.py` file was preserved. The optimized fork was added as a separate strategy named `TestX7`.

80-pair live-style analysis loop:

| Metric | Original X7 | TestX7 |
| --- | ---: | ---: |
| Pairs | `80` | `80` |
| Loops measured | `3` | `40` |
| Average loop time | `238.833499s` | `3.340671s` |
| Maximum loop time | `242.990876s` | `4.221486s` |
| Loops over 5 seconds | `3/3` | `0/40` |
| Gate result | failed | `PASS` |

The measured average speedup is about `71.5x`.

## Trading Parity

The important safety check is that `TestX7` still matches original X7 on the checked trading surface.

80-pair one-year comparison:

| Metric | Original X7 | TestX7 |
| --- | ---: | ---: |
| Total trades | `195` | `195` |
| Total profit | `1156.7473364 USDT` | `1156.7473364 USDT` |
| Profit factor | `67.18061450277237` | `67.18061450277237` |
| Max drawdown | `17.478643030000057 USDT` | `17.478643030000057 USDT` |
| Trade surface equal | `true` | `true` |
| First mismatch | `null` | `null` |

58-pair one-year comparison:

| Metric | Original X7 | TestX7 |
| --- | ---: | ---: |
| Total trades | `177` | `177` |
| Total profit | `829.12929377 USDT` | `829.12929377 USDT` |
| Profit factor | `5.02415619883808` | `5.02415619883808` |
| Max drawdown | `206.03804942 USDT` | `206.03804942 USDT` |
| Trade surface equal | `true` | `true` |
| First mismatch | `null` | `null` |

Plain meaning:

- Original X7 and `TestX7` opened the same checked trades.
- They closed the same checked trades.
- Trade count, profit summary, drawdown summary, and the exported trade surface matched.
- The measured change was performance and structure, not signal tuning.

## What Changed

`TestX7` separates the optimized work from the upstream baseline.

| Path | Purpose |
| --- | --- |
| `user_data/strategies/TestX7.py` | Freqtrade strategy entrypoint for the optimized fork |
| `user_data/strategies/test_x7_modules/indicator_logic.py` | Indicator and informative calculation logic |
| `user_data/strategies/test_x7_modules/entry_logic.py` | Entry-condition logic extracted from the strategy |
| `user_data/strategies/test_x7_modules/parallel_analyze.py` | Stable process-worker path for live pair analysis |
| `user_data/strategies/test_x7_modules/btc_cache.py` | BTC informative cache |
| `user_data/strategies/test_x7_modules/informative_cache.py` | Non-BTC informative cache |
| `user_data/strategies/test_x7_modules/merge.py` | Faster informative merge helper |
| `tools/test_x7/run_80pair_5s_gate.sh` | Final 80-pair 5-second speed gate |
| `tools/test_x7/compare_backtests.py` | Backtest parity comparison helper |

The main optimization is moving repeated expensive pair analysis into a stable process-worker path, while caching and reusing informative calculations where it is safe to do so.

## What Did Not Change

These were intentionally left unchanged:

- Original `NostalgiaForInfinityX7.py`
- Freqtrade core
- Entry and exit signal meaning
- DCA and grind meaning
- Position adjustment meaning
- Stake and leverage callback meaning
- Signal tag names
- Live laptop deployment

This repository should be read as a performance proof package, not as a new trading system.

## Why 9 Workers

The final local test machine exposed 10 CPUs to Docker.

Using all 10 workers looked attractive, but it was less stable:

| Setting | Result |
| --- | --- |
| `10 CPU / 10 workers` | Fast average, but max loop time reached `7.591558s`; failed the 5-second gate |
| `10 CPU / 8 workers` | Hardening recheck had spikes over 5 seconds; failed the 5-second gate |
| `10 CPU / 9 workers` | Max loop time stayed at `4.221486s`; passed the 5-second gate |

The practical reason is simple: Freqtrade, Python, Docker, and the operating system still need CPU time. In the final hardening run, leaving one CPU outside the worker pool gave the fastest stable result in this local test.

## Evidence Files

| File | What it proves |
| --- | --- |
| `user_data/backtest_results/test_x7_v17459_80_1y/compare.json` | 80-pair one-year parity |
| `user_data/backtest_results/test_x7_v17459_final_5s_1y_required/compare.json` | 58-pair one-year parity |
| `user_data/backtest_results/test_x7_v17459_80_1y/original-live-loop-80pairs-3loops.txt` | Original X7 live-loop timing |
| `user_data/backtest_results/test_x7_v17459_80_1y/testx7-live-loop-80pairs-40loops-workers9-20260509-204530.txt` | Final `TestX7` 80-pair speed gate |

## Reproduce

Check that both strategies load:

```bash
docker compose run --rm freqtrade list-strategies \
  --userdir /freqtrade/user_data \
  --config /freqtrade/user_data/config-test-x7.example.json
```

Run the final speed gate:

```bash
tools/test_x7/run_80pair_5s_gate.sh
```

If candle data is outside this checkout, mount it explicitly:

```bash
TEST_X7_GATE_DATA_DIR_HOST=/path/to/user_data/data/binance \
  tools/test_x7/run_80pair_5s_gate.sh
```

Expected final gate output:

```text
passes pairs=80 validation
gate=PASS
over5=0
max <= 5.0s
```

## Caveats

- This was validated locally, not deployed to the live laptop futures bot.
- Backtests do not prove future profitability.
- The 5-second result depends on the tested machine, Docker CPU visibility, pair count, data size, and system load.
- Upstream maintainers should review the process-worker boundary, cache invalidation rules, and Freqtrade callback assumptions before merging anything into NFI itself.

## Developer Summary

`TestX7` keeps original X7 as the baseline and adds a separate optimized strategy. In the checked local one-year comparisons, original X7 and `TestX7` produced the same trade surface. In the 80-pair live-style loop test, original X7 averaged `238.833499s`, while `TestX7` averaged `3.340671s` and passed `40/40` loops under the 5-second gate.

That makes this a strong candidate for review as a performance and maintainability improvement, not a profit-curve optimization.
