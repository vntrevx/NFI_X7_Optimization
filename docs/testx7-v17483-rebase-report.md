# TestX7 v17.4.83 Rebase Report

This report records the local rebase of the `TestX7` proof package onto
upstream `NostalgiaForInfinityX7` `v17.4.83`.

The goal did not change: keep the checked X7 trading behavior the same while
keeping the optimized live-style pair-analysis path fast enough for an 80-pair
setup.

## Status

`PASS`

Original X7 and `TestX7` now match exactly on the checked 80-pair one-year
trade surface.

```text
trade_surface_equal=true
first_difference=null
total_trades=317
```

## Scope

| Path | Change |
| --- | --- |
| `user_data/strategies/NostalgiaForInfinityX7.py` | Refreshed the upstream baseline to `v17.4.83` |
| `user_data/strategies/test_x7_modules/indicator_logic.py` | Matched upstream `pct_change(fill_method=None)` behavior |
| `user_data/strategies/test_x7_modules/indicator_logic.py` | Matched upstream EMA startup behavior where X7 uses `fillna=0.0` |
| `user_data/strategies/test_x7_modules/entry_logic.py` | Ported the `v17.4.83` entry-condition changes into the cached-expression form used by `TestX7` |

No Freqtrade core changes were made. No live bot was touched.

## Parity Check

The full 80-pair backtest comparison was rerun after the rebase and the EMA
startup parity fix.

| Metric | Original X7 | TestX7 |
| --- | ---: | ---: |
| Strategy version | `v17.4.83` | `v17.4.83` rebase |
| Backtest window | `2025-01-03 18:40` to `2026-03-31 23:55` | `2025-01-03 18:40` to `2026-03-31 23:55` |
| Total trades | `317` | `317` |
| Total profit | `2238.70937075 USDT` | `2238.70937075 USDT` |
| Total profit % | `223.87%` | `223.87%` |
| Profit factor | `180.12461170520245` | `180.12461170520245` |
| Max drawdown | `12.498055680000107 USDT` | `12.498055680000107 USDT` |
| Win rate | `99.68454258675079%` | `99.68454258675079%` |
| Trade surface equal | `true` | `true` |
| First mismatch | `null` | `null` |

Committed comparison artifact:

```text
user_data/backtest_results/test_x7_v17483_80_1y/compare.json
```

The comparison was generated from local exported backtest zips. The large zip
and log outputs are kept local and are not intended to be committed.

## Speed Gate

The 80-pair live-style gate was rerun after the rebase.

| Metric | TestX7 |
| --- | ---: |
| Pairs | `80` |
| Loops | `40` |
| Workers | `9` |
| Rows per pair | `1200` |
| Min loop time | `2.727310s` |
| Average loop time | `3.285929s` |
| Max loop time | `4.371312s` |
| Loops over 5 seconds | `0` |
| Gate result | `PASS` |

Committed speed artifact:

```text
user_data/backtest_results/test_x7_v17483_80_1y/testx7-live-loop-80pairs-40loops-workers9-20260515-040517.txt
```

## Verification Commands

Syntax and lint checks:

```bash
python3 -m py_compile \
  user_data/strategies/TestX7.py \
  user_data/strategies/test_x7_modules/*.py \
  tools/test_x7/*.py

python3 -m ruff check \
  user_data/strategies/TestX7.py \
  user_data/strategies/test_x7_modules \
  tools/test_x7
```

Both passed.

The final `TestX7` full-backtest log was also scanned for runtime failures:

```text
ERROR / Traceback / Unexpected error: none found
```

## Notes For Review

- This is still a proof package, not a live deployment.
- The result is not a profit-improvement claim.
- The important claim is narrower: after rebasing to X7 `v17.4.83`, the checked
  trade surface still matches exactly while the 80-pair live-style gate remains
  under 5 seconds.
- If this is turned into an upstream PR, it should be kept small and reviewable.
