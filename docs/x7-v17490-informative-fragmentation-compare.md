# X7 v17.4.90 Informative Dataframe Fragmentation Compare

Generated: 2026-05-17 Asia/Seoul

This note records a same-version comparison between the official upstream
`NostalgiaForInfinityX7.py` v17.4.90 source and a maintainer-provided local
test file that changes informative dataframe construction to reduce pandas
fragmentation.

The maintainer-provided strategy file is not included in this repository. This
report records only comparison evidence and a file hash for traceability.

## Scope

Baseline:

- Official upstream `NostalgiaForInfinityX7.py`
- Version: `v17.4.90`
- Upstream commit used for the same-version baseline: `3c5fa8f4e`
- SHA256 of extracted baseline file:
  `1a3230ea4839ceb29e722c5608002d74ba6044234ab50910ba523a4e46b575e8`

Compared file:

- Maintainer-provided local `NostalgiaForInfinityX7.py`
- Version: `v17.4.90`
- SHA256:
  `b1dd7edcc621bf766b28504fb9c8a91ceb362a6f5744f0f3039efe3e9fd31f72`

## Static Review

Both files passed `py_compile`.

Same-version diff size:

```text
1 file changed, 944 insertions(+), 684 deletions(-)
```

The diff is mostly a structural rewrite around:

- `informative_pairs`
- informative timeframe dataframe construction
- base timeframe indicator dataframe construction
- `populate_indicators` informative merge/drop handling

I did not see entry, exit, grind, or protection logic changes in the
same-version diff.

The reviewed file builds new indicator columns in dictionaries and concatenates
them in fewer dataframe operations. That matches the intended anti-fragmentation
direction.

Observed caution points:

- The reviewed file enables `log.setLevel(logging.DEBUG)`, which adds stderr
  output and can affect runtime measurements.
- `informative_pairs` uses a set for de-duplication and returns `list(...)`.
  That should not change trading behavior, but the returned order is not stable.
- Some columns produced by the official file are not produced by the reviewed
  file. In this same-version source, these missing columns only appeared as
  assignments, not as signal references found by text search:
  `BBM_20_2.0`, `BBP_20_2.0`, `RSI_3_diff`, `RSI_14_diff`,
  `STOCHd_14_3_3`, `STOCHRSId_14_14_3_3`.

## Live-Style Analyze Benchmark

Command shape:

- Tool: `tools/test_x7/benchmark_live_analyze.py`
- Container image: `freqtradeorg/freqtrade:stable`
- Strategy: `NostalgiaForInfinityX7`
- Data: local Binance spot feather data
- Rows: `1200`
- Runmode: `dry_run`
- Repeat: `1`
- Prewarm: enabled
- Advance window: enabled

### 20-Pair Fingerprint Check

| File | Pairs | Seconds | Cached pairs | Emitted pairs |
| --- | ---: | ---: | ---: | ---: |
| Official upstream v17.4.90 | 20 | `50.979344` | 20 | 20 |
| Reviewed file v17.4.90 | 20 | `50.294281` | 20 | 20 |

Result:

```text
fingerprint_equal=True
delta_seconds=-0.685063
delta_pct=-1.344%
```

### 80-Pair Runtime Check

This run skipped fingerprint output to keep the 80-pair timing pass lighter.

| File | Pairs | Seconds | Cached pairs | Emitted pairs |
| --- | ---: | ---: | ---: | ---: |
| Official upstream v17.4.90 | 80 | `215.992392` | 80 | 80 |
| Reviewed file v17.4.90 | 80 | `209.742511` | 80 | 80 |

Result:

```text
delta_seconds=-6.249881
delta_pct=-2.894%
```

The reviewed file was modestly faster in this live-style harness.

## Populate Timing Signal

The reviewed file's DEBUG logs make the split visible. On the 80-pair run:

```text
indicator_subtotal_seconds=5.2651
populate_indicators_total_seconds=68.8826
unaccounted_populate_seconds=63.6175
unaccounted_avg_per_pair=0.7952
```

This supports the current working theory: the expensive part is not the raw
indicator calculations themselves. Most of the observed `populate_indicators`
time sits outside the individual indicator subtotals, consistent with dataframe
merge/copy/drop/reallocation overhead.

## Backtest Canary

I also ran a short trade-surface canary:

- Timerange: `20251025-20251111`
- Pairs: 10
- Cache: `none`
- Export: `trades`

Pairs:

```text
DASH/USDT ZEC/USDT FIL/USDT TIA/USDT INJ/USDT ICP/USDT ZK/USDT ZEN/USDT NEAR/USDT RENDER/USDT
```

Trade-surface comparison:

```text
trade_surface_equal=true
first_difference=null
left_total_trades=36
right_total_trades=36
```

Both runs produced the same summary surface:

```text
total_trades=36
profit_total=0.17413811022999998
profit_total_abs=174.13811022999997
winrate=1.0
max_drawdown_account=0.0
```

## Current Conclusion

On the checks above, the reviewed v17.4.90 file looks behavior-preserving and
shows a modest runtime improvement in the live-style analyze harness.

The strongest completed evidence so far:

- same-version comparison against official upstream v17.4.90
- `py_compile` passed
- 20-pair live-style fingerprint matched
- 80-pair live-style run was about `2.9%` faster
- short backtest canary trade surface matched exactly

This is still not a full proof. Before calling the change fully proven, the next
step should be a longer backtest parity run, ideally the full 80-pair timerange
used by the prior TestX7 proof package.
