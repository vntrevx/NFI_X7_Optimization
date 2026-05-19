# NFI X7 Optimization Proof Package

This repository is a local proof package for `TestX7`, an optimized fork built
on top of the original `NostalgiaForInfinityX7` strategy from
[iterativv/NostalgiaForInfinity](https://github.com/iterativv/NostalgiaForInfinity).

The original X7 strategy remains the baseline. `TestX7` is the performance
proof layer on top: same checked trading surface, faster live pair analysis.

The work was not aimed at improving the profit curve. The goal was narrower:

> Keep the checked X7 trading behavior unchanged, while making the live pair
> analysis loop fast enough for a wide pairlist.

That goal passed in the local validation described below.

Community questions such as live readiness, dry-run status, backtest speed, and
worker count are answered in [docs/community-qa.md](docs/community-qa.md).
Korean version: [docs/community-qa-ko.md](docs/community-qa-ko.md).

Backtest follow-up documents:
[docs/backtest-profiling-plan.md](docs/backtest-profiling-plan.md),
[docs/community-test-report.md](docs/community-test-report.md), and
[docs/python-runtime-comparison.md](docs/python-runtime-comparison.md).

Latest rebase check:
[docs/testx7-v17483-rebase-report.md](docs/testx7-v17483-rebase-report.md).

## English

### How To Try TestX7

`TestX7` is experimental. Start with backtesting or dry-run before any live use.

Copy these files from this repository into your Freqtrade
`user_data/strategies/` folder:

- `user_data/strategies/TestX7.py`
- `user_data/strategies/NostalgiaForInfinityX7.py`
- `user_data/strategies/test_x7_modules/`

Then set your Freqtrade strategy to:

```json
"strategy": "TestX7"
```

To use the live-loop speed optimization, `TestX7.py` must be used together
with the matching `test_x7_modules/` folder and worker/config settings such as
`test_x7_stable_process_analyze_workers`.

If you run the original iterativ strategy file directly, it uses the original
strategy path, so the `TestX7` multi-process/caching acceleration is not active.

This repository currently publishes the optimized proof package as `TestX7`.
There is no separate optimized `TestX6.py` package here.

### Result At A Glance

The upstream `NostalgiaForInfinityX7.py` strategy is kept as the baseline.
The optimized version is a separate Freqtrade strategy named `TestX7`.

80-pair live-style analysis loop:

| Metric | Original X7 | TestX7 |
| --- | ---: | ---: |
| Pairs | `80` | `80` |
| Measured loops | `3` | `40` |
| Average loop time | `238.833499s` | `3.340671s` |
| Maximum loop time | `242.990876s` | `4.221486s` |
| Loops over 5 seconds | `3/3` | `0/40` |
| Gate result | failed | `PASS` |

Measured average speedup:

```text
238.833499 / 3.340671 = 71.5x
```

### Trading Parity

Speed alone is not enough. The important check is whether the optimized strategy
still makes the same checked trading decisions.

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

Plainly: in the checked backtests, original X7 and `TestX7` opened the same
trades, closed the same trades, and produced the same exported trade surface.
The measured change is performance and structure, not signal tuning.

### What Changed

`TestX7` keeps the optimized code outside the original strategy file.

| Path | Purpose |
| --- | --- |
| `user_data/strategies/TestX7.py` | Thin Freqtrade strategy entrypoint for `TestX7` |
| `user_data/strategies/test_x7_modules/indicator_logic.py` | Indicator and informative-timeframe calculations |
| `user_data/strategies/test_x7_modules/entry_logic.py` | Extracted entry-condition logic |
| `user_data/strategies/test_x7_modules/parallel_analyze.py` | Stable process-worker path for live pair analysis |
| `user_data/strategies/test_x7_modules/btc_cache.py` | BTC informative dataframe cache |
| `user_data/strategies/test_x7_modules/informative_cache.py` | Non-BTC informative dataframe cache |
| `user_data/strategies/test_x7_modules/merge.py` | Faster no-lookahead informative merge helper |
| `tools/test_x7/compare_backtests.py` | Trade-surface comparison helper |
| `tools/test_x7/run_80pair_5s_gate.sh` | Final 80-pair speed gate |

The main optimization is the live/dry-run analysis path. Repeated pair analysis
is split across stable worker processes, while informative dataframes and repeated
boolean masks are reused where the cache keys prove that the source candle state
has not changed.

### What Did Not Change

These were intentionally left alone:

- original `NostalgiaForInfinityX7.py` baseline
- Freqtrade core
- entry and exit signal meaning
- DCA and grind behavior
- position-adjustment behavior
- stake and leverage callback meaning
- signal tag names
- live laptop deployment

This repository should be read as a performance proof package, not as a new
trading system and not as a profit-curve optimization.

### Why 9 Workers

The final local test machine exposed 10 CPUs to Docker. Using all 10 workers was
not the best result.

| Setting | Result |
| --- | --- |
| `10 CPU / 10 workers` | Fast average, but the max loop reached `7.591558s`; failed the 5-second gate |
| `10 CPU / 8 workers` | Hardening recheck had spikes over 5 seconds; failed the 5-second gate |
| `10 CPU / 9 workers` | Max loop stayed at `4.221486s`; passed the 5-second gate |

Leaving CPU headroom for Freqtrade, Python, Docker, and the operating system was
more stable than assigning every visible CPU to a worker process. In the final
hardening run, 9 workers was the fastest setting that stayed under the 5-second
gate for all 40 loops.

### Reproduce

Check that both strategies load:

```bash
docker compose run --rm freqtrade list-strategies \
  --userdir /freqtrade/user_data \
  --config /freqtrade/user_data/config-test-x7.example.json
```

Expected:

```text
NostalgiaForInfinityX7 OK
TestX7 OK
```

Run the final 80-pair speed gate:

```bash
tools/test_x7/run_80pair_5s_gate.sh
```

If candle data is outside this checkout, mount it explicitly:

```bash
TEST_X7_GATE_DATA_DIR_HOST=/path/to/user_data/data/binance \
  tools/test_x7/run_80pair_5s_gate.sh
```

Expected:

```text
passes pairs=80 validation
gate=PASS
over5=0
max <= 5.0s
```

The recorded final run is:

```text
user_data/backtest_results/test_x7_v17459_80_1y/testx7-live-loop-80pairs-40loops-workers9-20260509-204530.txt
```

### Evidence Files

| File | What it proves |
| --- | --- |
| `docs/testx7-v17483-rebase-report.md` | `TestX7` rebase to upstream X7 `v17.4.83` |
| `user_data/backtest_results/test_x7_v17483_80_1y/compare.json` | 80-pair one-year `v17.4.83` trade-surface parity |
| `user_data/backtest_results/test_x7_v17483_80_1y/testx7-live-loop-80pairs-40loops-workers9-20260515-040517.txt` | `v17.4.83` 80-pair speed gate |
| `docs/final-report.md` | Developer-facing summary of the completed validation |
| `user_data/backtest_results/test_x7_v17459_80_1y/compare.json` | 80-pair one-year trade-surface parity |
| `user_data/backtest_results/test_x7_v17459_final_5s_1y_required/compare.json` | 58-pair one-year trade-surface parity |
| `user_data/backtest_results/test_x7_v17459_80_1y/original-live-loop-80pairs-3loops.txt` | Original X7 80-pair live-loop timing |
| `user_data/backtest_results/test_x7_v17459_80_1y/testx7-live-loop-80pairs-40loops-workers9-20260509-204530.txt` | Final `TestX7` 80-pair speed gate |

### Caveats

- This is local validation, not a live futures deployment.
- Backtests do not guarantee future profitability.
- The 5-second result depends on CPU count, Docker CPU visibility, pair count,
  data size, and system load.
- Before any upstream merge, the process-worker boundary, cache invalidation
  rules, and Freqtrade callback assumptions need careful review.

### Developer Summary

`TestX7` keeps original X7 as the baseline and adds a separate optimized strategy.
In the checked one-year comparisons, original X7 and `TestX7` produced the same
trade surface. In the 80-pair live-style loop test, original X7 averaged
`238.833499s`, while `TestX7` averaged `3.340671s` and passed `40/40` loops under
the 5-second gate.

This is a performance and maintainability improvement candidate. It is not a
claim that the strategy will be more profitable.

---

## 한국어

커뮤니티에서 자주 나오는 질문인 live 적용 가능 여부, dry-run 검증 여부, backtest 속도, worker 수 설정은
[docs/community-qa-ko.md](docs/community-qa-ko.md)에 한국어로 정리했습니다.
영어판은 [docs/community-qa.md](docs/community-qa.md)에 있습니다.

Backtest 관련 추가 문서:
[docs/backtest-profiling-plan.md](docs/backtest-profiling-plan.md),
[docs/community-test-report.md](docs/community-test-report.md),
[docs/python-runtime-comparison.md](docs/python-runtime-comparison.md).

최신 rebase 검증:
[docs/testx7-v17483-rebase-report.md](docs/testx7-v17483-rebase-report.md).

### 한 줄 요약

`TestX7`는 NFI X7의 수익률을 높이려고 만든 튜닝판이 아닙니다. 목표는 더 좁고 명확했습니다.

이 작업은 [iterativv/NostalgiaForInfinity](https://github.com/iterativv/NostalgiaForInfinity)의
원본 `NostalgiaForInfinityX7`를 기반으로 한 성능 proof package입니다. 원본 X7을 기준본으로
두고, `TestX7`는 같은 매매 판단을 더 빠르게 계산하는 별도 최적화 레이어로 만들었습니다.

> 검증된 X7 매매 판단은 그대로 유지하고, 많은 pair를 돌릴 때 느려지는 live 분석 루프를 크게 줄인다.

로컬 검증 기준으로 이 목표는 통과했습니다.

### TestX7 사용해보기

`TestX7`는 아직 실험용입니다. live 사용 전에는 backtest 또는 dry-run부터
시작하는 것을 권장합니다.

이 저장소에서 아래 파일과 폴더를 Freqtrade의 `user_data/strategies/` 폴더로
복사합니다.

- `user_data/strategies/TestX7.py`
- `user_data/strategies/NostalgiaForInfinityX7.py`
- `user_data/strategies/test_x7_modules/`

그 다음 Freqtrade 전략을 아래처럼 지정합니다.

```json
"strategy": "TestX7"
```

live-loop 속도 최적화를 쓰려면 `TestX7.py`와 같은 버전의
`test_x7_modules/` 폴더, 그리고 `test_x7_stable_process_analyze_workers`
같은 worker/config 설정을 함께 사용해야 합니다.

iterativ 원본 전략 파일을 직접 실행하면 원본 전략 경로를 사용하므로
`TestX7`의 multi-process/cache 가속은 활성화되지 않습니다.

현재 이 저장소의 최적화 proof package는 `TestX7`입니다. 별도의 최적화된
`TestX6.py` 패키지는 이 저장소에 없습니다.

### 결과 먼저 보기

원본 `NostalgiaForInfinityX7.py`는 기준본으로 보존했습니다. 최적화 버전은 `TestX7`라는 별도 전략으로 분리했습니다.

80페어 live-style analysis loop 결과:

| 항목 | 원본 X7 | TestX7 |
| --- | ---: | ---: |
| Pair 수 | `80` | `80` |
| 측정 loop | `3` | `40` |
| 평균 loop 시간 | `238.833499s` | `3.340671s` |
| 최대 loop 시간 | `242.990876s` | `4.221486s` |
| 5초 초과 | `3/3` | `0/40` |
| Gate 결과 | 실패 | `PASS` |

평균 기준 약 `71.5x` 빨라졌습니다.

### 매매 로직은 그대로인가?

이 작업에서 가장 중요한 부분입니다. 속도만 빨라지고 매매 판단이 바뀌면 의미가 없습니다.

80페어 1년 비교:

| 항목 | 원본 X7 | TestX7 |
| --- | ---: | ---: |
| 거래 수 | `195` | `195` |
| 총수익 | `1156.7473364 USDT` | `1156.7473364 USDT` |
| Profit factor | `67.18061450277237` | `67.18061450277237` |
| 최대 낙폭 | `17.478643030000057 USDT` | `17.478643030000057 USDT` |
| 거래 표면 비교 | `true` | `true` |
| 첫 불일치 | `null` | `null` |

58페어 1년 비교:

| 항목 | 원본 X7 | TestX7 |
| --- | ---: | ---: |
| 거래 수 | `177` | `177` |
| 총수익 | `829.12929377 USDT` | `829.12929377 USDT` |
| Profit factor | `5.02415619883808` | `5.02415619883808` |
| 최대 낙폭 | `206.03804942 USDT` | `206.03804942 USDT` |
| 거래 표면 비교 | `true` | `true` |
| 첫 불일치 | `null` | `null` |

쉽게 말하면, 검증한 백테스트 범위에서는 원본이 산 것을 `TestX7`도 샀고, 원본이 판 시점에 `TestX7`도 팔았습니다. 거래 수, 수익, drawdown, tag, exit reason까지 비교한 거래 표면이 같았습니다.

따라서 이번 결과는 “더 잘 벌도록 신호를 바꿨다”가 아니라 “같은 판단을 훨씬 빨리 계산하게 만들었다”에 가깝습니다.

### 무엇을 바꿨나

`TestX7`는 원본 파일을 직접 덮어쓰지 않습니다. 원본은 그대로 두고, 최적화 코드를 별도 전략과 모듈로 분리했습니다.

| 경로 | 역할 |
| --- | --- |
| `user_data/strategies/TestX7.py` | `TestX7` 전략 진입점 |
| `user_data/strategies/test_x7_modules/indicator_logic.py` | 지표 및 informative timeframe 계산 |
| `user_data/strategies/test_x7_modules/entry_logic.py` | entry 조건 로직 |
| `user_data/strategies/test_x7_modules/parallel_analyze.py` | live pair 분석용 stable process-worker 경로 |
| `user_data/strategies/test_x7_modules/btc_cache.py` | BTC informative dataframe cache |
| `user_data/strategies/test_x7_modules/informative_cache.py` | 일반 informative dataframe cache |
| `user_data/strategies/test_x7_modules/merge.py` | 더 빠른 no-lookahead informative merge helper |
| `tools/test_x7/compare_backtests.py` | 원본과 TestX7의 거래 표면 비교 도구 |
| `tools/test_x7/run_80pair_5s_gate.sh` | 최종 80페어 5초 게이트 |

핵심은 live/dry-run 분석 경로입니다. pair별로 반복되는 무거운 계산을 stable worker process로 나누고, candle 상태가 같다는 것이 확인되는 경우에만 informative dataframe과 반복 boolean mask를 재사용합니다.

### 의도적으로 건드리지 않은 것

다음 영역은 바꾸지 않았습니다.

- 원본 `NostalgiaForInfinityX7.py` 기준본
- Freqtrade core
- entry / exit 신호의 의미
- DCA / grind 동작 의미
- position adjustment 동작 의미
- stake / leverage callback 의미
- signal tag 이름
- live laptop 배포 상태

이 저장소는 새 매매 시스템이 아니라 성능 검증 패키지입니다. 수익률을 좋게 보이게 만든 최적화가 아닙니다.

### 왜 workers 9인가

최종 로컬 테스트에서는 Docker가 CPU 10개를 볼 수 있었습니다. 그렇다고 worker를 10개 쓰는 것이 가장 안정적인 선택은 아니었습니다.

| 설정 | 결과 |
| --- | --- |
| `10 CPU / 10 workers` | 평균은 빨랐지만 최대 loop가 `7.591558s`까지 튀어서 5초 게이트 실패 |
| `10 CPU / 8 workers` | hardening 재검증에서 5초 초과 spike가 발생해 5초 게이트 실패 |
| `10 CPU / 9 workers` | 최대 loop가 `4.221486s`로 유지되어 5초 게이트 통과 |

Freqtrade 본체, Python, Docker, OS scheduler도 CPU 시간이 필요합니다. 최종 hardening 재검증에서는 CPU 10개 중 9개를 worker로 쓰는 쪽이 40회 모두 5초 안에 들어왔습니다.

### 직접 확인하기

두 전략이 모두 로드되는지 확인:

```bash
docker compose run --rm freqtrade list-strategies \
  --userdir /freqtrade/user_data \
  --config /freqtrade/user_data/config-test-x7.example.json
```

예상 결과:

```text
NostalgiaForInfinityX7 OK
TestX7 OK
```

최종 80페어 speed gate 실행:

```bash
tools/test_x7/run_80pair_5s_gate.sh
```

예상 결과:

```text
pairs=80 검증 통과
gate=PASS
over5=0
max <= 5.0s
```

기록된 최종 실행 결과:

```text
user_data/backtest_results/test_x7_v17459_80_1y/testx7-live-loop-80pairs-40loops-workers9-20260509-204530.txt
```

### 증거 파일

| 파일 | 의미 |
| --- | --- |
| `docs/final-report.md` | 개발자 검토용 최종 요약 |
| `user_data/backtest_results/test_x7_v17459_80_1y/compare.json` | 80페어 1년 거래 표면 parity |
| `user_data/backtest_results/test_x7_v17459_final_5s_1y_required/compare.json` | 58페어 1년 거래 표면 parity |
| `user_data/backtest_results/test_x7_v17459_80_1y/original-live-loop-80pairs-3loops.txt` | 원본 X7 80페어 live-loop 시간 |
| `user_data/backtest_results/test_x7_v17459_80_1y/testx7-live-loop-80pairs-40loops-workers9-20260509-204530.txt` | 최종 `TestX7` 80페어 speed gate |

### 주의사항

- 이 결과는 로컬 검증입니다. live futures 서버에 배포한 결과가 아닙니다.
- 백테스트는 미래 수익을 보장하지 않습니다.
- 5초 결과는 CPU 수, Docker가 보는 CPU 수, pair 수, 데이터 크기, 현재 시스템 부하에 영향을 받습니다.
- upstream에 넣으려면 process-worker 경계, cache invalidation 규칙, Freqtrade callback 가정은 별도 코드 리뷰가 필요합니다.

### 한국어 요약

`TestX7`는 원본 X7을 기준본으로 남겨두고 별도 최적화 전략을 추가한 작업입니다. 검증한 1년 비교에서는 원본 X7과 `TestX7`의 거래 표면이 같았습니다. 80페어 live-style loop에서는 원본 X7 평균 `238.833499s`가 `TestX7` 평균 `3.340671s`로 줄었고, 40회 반복 모두 5초 안에 끝났습니다.

이 작업은 수익률을 높이기 위한 신호 튜닝이 아니라, 같은 매매 판단을 더 빠르고 구조적으로 계산하기 위한 성능 개선 후보입니다.
