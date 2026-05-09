# TestX7 Final Report

Date: 2026-05-09 KST

## Verdict

58페어 기준 5초 목표는 완료.

80페어 추가 검증도 로컬에서 끝까지 수행했고, 매매 결과 parity와 strict 5초 게이트를 모두 통과했다. WSL/Docker가 10 CPU를 노출한 뒤 최종 safe config는 `8` workers로 확정했다.

- NFI upstream은 `origin/main` 최신 커밋 `75c223b0f1a76731f4555aeb70fd0c92df9f30ea`로 확인했다.
- 최신 원본 X7은 `v17.4.59`이고, `external/NostalgiaForInfinity/NostalgiaForInfinityX7.py`와 `user_data/strategies/NostalgiaForInfinityX7.py`는 byte-identical이다.
- 원본 X7 파일은 기준본으로 보존했다. 최적화/모듈화 변경은 `TestX7`과 `test_x7_modules/`에만 들어갔다.
- `TestX7`은 Freqtrade에서 별도 strategy class/file로 로딩된다. 표시명은 보고서와 결과에서 `Test X7`로 사용한다.
- 로컬 7일 short parity와 로컬 1년 parity 모두 원본 X7과 `trade_surface_equal=true`로 통과했다.
- config-only live-loop 40회 벤치마크에서 58 pairs 전체 `strategy.analyze(pairs)`가 모두 5초 미만으로 끝났다. 최신 safe config 최고값은 `4.351102s`다.
- 80-pair local live-loop는 원본 X7 평균 `238.833s`에서 TestX7 최종 safe config 평균 `3.284s`로 약 `72.7x` 개선됐다. 최종 기본 게이트는 `max=3.830582s`, `over5=0/40`, `gate=PASS`다.
- 최종 1년 백테스트 로그에서 `ERROR`, `Traceback`, `KeyError`, `Unexpected error`, `Strategy analysis took`는 0건이다.
- laptop live 서버에는 배포하지 않았다.

이 결과는 로컬 백테스트와 로컬 live-loop 하네스 증거다. 미래 수익 보장이 아니다.

80페어 추가 상세 보고서:

- `docs/2026-05-09-test-x7-80pairs-local-report.md`

## Latest Baseline

| Item | Value |
| --- | --- |
| Upstream commit | `75c223b0f1a76731f4555aeb70fd0c92df9f30ea` |
| Commit title | `Merge branch 'dev-ngyun-fix/updater-race-condition'` |
| X7 version | `v17.4.59` |
| X6 version | `v16.8.798` |
| X7 SHA256 | `26ac1698b58bf8356cf67ea9874ba0eaed95fbebad80fb630366b3f39c00994c` |

Verified:

```bash
git -C external/NostalgiaForInfinity fetch --prune origin
git -C external/NostalgiaForInfinity rev-parse HEAD
git -C external/NostalgiaForInfinity rev-parse origin/main
sha256sum external/NostalgiaForInfinity/NostalgiaForInfinityX7.py user_data/strategies/NostalgiaForInfinityX7.py
```

## Freqtrade Facts

Documented in `docs/2026-05-08-test-x7-fact-check.md`.

- Freqtrade loads one configured strategy class for trading decisions.
- Multiple strategy files can exist under `user_data/strategies/`, but their decisions are not mixed.
- `NostalgiaForInfinityX7` and `TestX7` can be listed and loaded side by side.
- In Freqtrade `2026.4`, the strategy API pair loop is sequential: `IStrategy.analyze(pairs)` iterates pairs and calls `analyze_pair(pair)`.
- `analyze_ticker()` calls `populate_indicators()`, then `populate_entry_trend()`, then `populate_exit_trend()`.
- `custom_exit`, `adjust_trade_position`, `custom_stake_amount`, and `leverage` remain inherited from upstream X7 in this phase.

## Modular Structure

`user_data/strategies/TestX7.py` is a 38-line Freqtrade entrypoint. The extracted modules live under `user_data/strategies/test_x7_modules/`.

| Module | Role |
| --- | --- |
| `indicator_logic.py` | extracted indicator and informative-timeframe calculation |
| `entry_logic.py` | extracted entry-signal calculation |
| `btc_cache.py` | raw BTC informative dataframe cache |
| `informative_cache.py` | non-BTC informative dataframe cache |
| `parallel_analyze.py` | live/dry-run stable process pair-loop path |
| `cpu.py` | CPU topology and worker selection helpers |
| `merge.py` | fast no-lookahead informative merge |
| `masks.py` | reusable boolean comparison-mask cache |
| `entry_optimizations.py` | spot-only short-entry/protection skip switches |
| `profiling.py`, `entry_profile.py` | optional profiling |
| `parity.py` | parity helper surface |

Current size:

- Original X7 baseline: `78067` lines.
- `TestX7.py`: `38` lines.
- TestX7 modules combined: `24152` lines.

## Kept Optimizations

- Direct TA-Lib replacements for repeated pandas-ta wrapper calls where sample parity was checked.
- Direct CMF/KST/StochRSI helper calculations where sample parity matched.
- Raw BTC informative cache.
- Non-BTC informative dataframe cache.
- Fast no-lookahead informative merge using sorted OHLCV reindex/ffill semantics.
- Repeated comparison-mask cache.
- Spot-only short-entry and short-protection calculation skip when `trading_mode == spot` and `can_short == false`.
- Stable process-based live/dry-run `analyze(pairs)` path.
- Startup dataframe and compute prewarm for stable workers.
- Numeric thread limiting with `test_x7_numeric_threads: 1`.

The compute prewarm discards worker results. It does not hardcode trade outputs, pair decisions, tags, or result tables.

## Worker Decision

Local runtime still exposes 4 logical CPUs to WSL/Docker. The original backtest CPU monitor shows the classic single-core shape:

| Run | CPU avg | CPU max | Memory max | Monitor duration |
| --- | ---: | ---: | ---: | ---: |
| Original X7 1y | `95.00%` | `96.94%` | `16.74GiB` | `1123s` |
| Final TestX7 1y | `92.84%` | `94.18%` | `15.38GiB` | `1036s` |

For the live-loop stable process path, the earlier `5` worker setting passed the
58-pair target but oversubscribed the initial 4-vCPU WSL runtime for 80 pairs.
After WSL/Docker exposed 10 CPUs, `10` workers produced faster average runtime
but still had >5s spikes. The final safe config leaves two CPUs free and uses
`8` stable workers plus tighter informative payload tails:

```json
"test_x7_stable_process_analyze_workers": 8,
"test_x7_process_tail_rows_by_timeframe": {
  "15m": 128,
  "1h": 224,
  "4h": 208,
  "1d": 48
}
```

This was selected by measurement, not by assumption. It keeps the 58-pair target
green and finishes the 80-pair 5-second gate on the current 10 exposed CPUs.

Additional 80-pair tuning after the latest safe config:

| Experiment | Loops | Avg | Max | Over 5s | Result |
| --- | ---: | ---: | ---: | ---: | --- |
| 5 workers | `12` | `5.107s` | `5.553s` | `9/12` | rejected |
| 3 workers | `12` | `6.456s` | `6.877s` | `12/12` | rejected |
| 6 workers | `12` | `5.231s` | `5.487s` | `12/12` | rejected |
| 8 workers | `12` | `5.166s` | `5.570s` | `9/12` | rejected |
| Aggressive tails `15m=64,1h=200,4h=200,1d=40` | `40` | `5.143s` | `5.897s` | `26/40` | rejected |
| Base-first live-tail merge prototype | `40` | `5.115s` | `5.908s` | `27/40` | reverted |
| Entry tail `6` | `40` | `5.120s` | `6.042s` | `23/40` | rejected |
| Entry `6` + aggressive informative tails | `40` | `5.083s` | `5.875s` | `23/40` | rejected |
| Base `360` + entry `6` + aggressive informative tails | `40` | `5.038s` | `5.751s` | `17/40` | rejected |
| Base `300` + entry `6` + aggressive informative tails | `40` | `5.031s` | `5.818s` | `16/40` | rejected |
| Base `300` + entry `6` + aggressive informative tails + numeric threads `0` | `40` | `5.082s` | `5.756s` | `21/40` | rejected |
| Precomputed long-shift prototype with indicator tail `6` | `40` | `5.134s` | `6.063s` | `27/40` | reverted |
| 10 CPUs / 10 workers | `40` | `3.900s` | `7.592s` | `6/40` | rejected |
| 10 CPUs / 8 workers | `20` | `3.731s` | `4.849s` | `0/20` | candidate |
| 10 CPUs / 8 workers final gate | `40` | `3.422s` | `4.100s` | `0/40` | promoted |
| Default gate after script patch | `40` | `3.284s` | `3.831s` | `0/40` | final |

Both rejected code/config candidates kept an 80-pair one-loop live fingerprint
equal to the safe config before speed testing, but neither improved the 40-loop
gate enough to keep.

The later entry/base tail reductions also kept one-loop live fingerprint
equality, but still missed the 40-loop 5-second gate. The closest 4-vCPU result
was `avg=5.031s`, `max=5.818s`, `over5=16/40`.

The final 10-CPU run showed that using every logical CPU caused scheduling
spikes (`max=7.592s`). Leaving two CPUs free with `8` workers removed the
spikes in the final default gate (`max=3.831s`, `over5=0/40`).

The precomputed long-shift prototype was intended to reduce live indicator rows
from 289 to 6 while preserving long-period shift semantics. It kept one-loop
fingerprint equality, but the 40-loop speed gate got worse, so the code was
reverted.

## 5s Benchmark

Final 80-pair gate command:

```bash
tools/test_x7/run_80pair_5s_gate.sh
```

The script prints host/Docker CPU counts, uses Docker-visible CPU count minus two
as the default worker count when Docker exposes at least 8 CPUs, stores the loop output under
`user_data/backtest_results/test_x7_v17459_80_1y/`, and exits non-zero unless
every loop is `<= 5.0s`. Override examples:

```bash
TEST_X7_GATE_WORKERS=8 tools/test_x7/run_80pair_5s_gate.sh
TEST_X7_GATE_REPEAT=12 tools/test_x7/run_80pair_5s_gate.sh
```

Command:

```bash
docker compose run --rm \
  -v /home/user/project/freqtrade-nfi:/work \
  -w /work \
  --entrypoint python3 \
  freqtrade tools/test_x7/benchmark_live_analyze.py \
  --config user_data/config-test-x7.example.json \
  --config-extra user_data/config-test-x7-live-speed-safe.example.json \
  --runmode dry_run \
  --repeat 40 \
  --advance-window \
  --prewarm \
  --no-fingerprint
```

Result:

| Metric | Value |
| --- | ---: |
| Pairs | `58` |
| Rows | `1200` |
| Repeat loops | `40` |
| Min loop | `3.345851s` |
| Avg loop | `3.776724s` |
| Max loop | `4.351102s` |
| Loops over 5s | `0` |

Final loop output:

```text
loop1=3.479671s loop2=3.874848s loop3=3.830872s loop4=3.742951s loop5=4.099818s loop6=3.581119s loop7=3.877205s loop8=3.867905s loop9=3.664269s loop10=3.345851s loop11=3.973264s loop12=3.557086s loop13=3.587990s loop14=4.066340s loop15=3.929492s loop16=3.825253s loop17=4.351102s loop18=3.618106s loop19=3.670772s loop20=3.853853s loop21=3.502018s loop22=3.714895s loop23=3.815594s loop24=3.694238s loop25=3.678332s loop26=4.027643s loop27=3.776625s loop28=3.766383s loop29=4.178490s loop30=3.658793s loop31=3.613077s loop32=3.819259s loop33=3.681857s loop34=3.673655s loop35=3.932232s loop36=3.622289s loop37=3.687563s loop38=4.121690s loop39=3.551213s loop40=3.755334s
strategy=TestX7 pairs=58 rows=1200 seconds=157.366973 cached_pairs=58 emitted=2320
```

## Parity Evidence

Short parity:

| Item | Original X7 | TestX7 |
| --- | ---: | ---: |
| Trades | `2` | `2` |
| Profit abs | `5.55197935` | `5.55197935` |
| Profit factor | `80.6814588363` | `80.6814588363` |
| Trade surface equal | `true` | `true` |

Short artifacts:

- Original: `user_data/backtest_results/test_x7_v17459_short/original/backtest-result-2026-05-08_10-03-11.zip`
- TestX7: `user_data/backtest_results/test_x7_v17459_after_required_columns/testx7/backtest-result-2026-05-08_20-35-55.zip`

1-year parity:

| Item | Original X7 | TestX7 |
| --- | ---: | ---: |
| Timerange | `20250401-20260401` | `20250401-20260401` |
| Trades | `177` | `177` |
| Total profit USDT | `829.12929377` | `829.12929377` |
| Total profit % | `82.91%` | `82.91%` |
| Winrate | `98.8700564972%` | `98.8700564972%` |
| Profit factor | `5.0241561988` | `5.0241561988` |
| Max drawdown abs | `206.03804942` | `206.03804942` |
| Best pair | `DASH/USDT` | `DASH/USDT` |
| Worst pair | `FLOW/USDT` | `FLOW/USDT` |
| Trade surface equal | `true` | `true` |

1-year artifacts:

- Original: `user_data/backtest_results/test_x7_v17459_1y/original/backtest-result-2026-05-08_10-24-35.zip`
- TestX7 final accepted: `user_data/backtest_results/test_x7_v17459_final_5s_1y_required/testx7/backtest-result-2026-05-08_21-26-30.zip`

Verification:

```bash
python3 tools/test_x7/compare_backtests.py \
  user_data/backtest_results/test_x7_v17459_1y/original/backtest-result-2026-05-08_10-24-35.zip \
  user_data/backtest_results/test_x7_v17459_final_5s_1y_required/testx7/backtest-result-2026-05-08_21-26-30.zip \
  --json
```

Returned `first_difference=null` and `trade_surface_equal=true`.

## Log Cleanliness

Final accepted 1-year TestX7 logs:

- `user_data/logs/test_x7_v17459_final_5s_1y_required/testx7.log`
- `user_data/logs/test_x7_v17459_final_5s_1y_required/stdout.log`

Verification:

```bash
rg -n "ERROR|Traceback|KeyError|Unexpected error|Strategy analysis took" \
  user_data/logs/test_x7_v17459_final_5s_1y_required/testx7.log \
  user_data/logs/test_x7_v17459_final_5s_1y_required/stdout.log
```

Returned no matches.

## Remaining Risks

- This is local spot/dry-run style evidence with local candle data. It is not a live laptop deployment.
- The 5-second result is for the live-loop harness `strategy.analyze(pairs)` after startup prewarm. It is not the full backtest wall-clock time.
- The accepted worker count `4` is empirical for the current 4-vCPU local WSL runtime. Different pair counts, Docker CPU limits, or live laptop CPU topology should be rebenchmarked before deployment.
- `/mnt/c/Users/0/.wslconfig` currently asks for `processors=10`, but the active WSL session still reports `nproc=4`. The 80-pair 5-second target cannot be fairly re-tested on the intended 10 CPU allocation until WSL is restarted and Docker sees the additional CPUs.
- Freqtrade core itself was not modified. TestX7 parallelizes inside the strategy boundary for live/dry-run only.
- Futures/live 80-pair operation should get a separate validation pass before any laptop live rollout.
- Backtest profit is not a promise of future profit.
