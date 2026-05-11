# TestX7 Backtest Profiling Plan

This document describes how to test whether the `TestX7` optimization also
improves the backtesting path in a future NFI version.

Claim boundary:

```text
not production-ready
not a profit claim
not globally proven backtest speedup
external community report
```

This is a profiling plan, not a result claim.

## English

### Purpose

The current strongest proof for `TestX7` is the live-style `analyze(pairs)`
path. That path showed a large local speed improvement while the checked
trade surface stayed equal to original X7.

Backtesting is a different execution path. The next NFI-version rebase should
therefore measure backtest speed separately instead of assuming that the
live-style result transfers directly.

### Scope

Compare:

| Candidate | Purpose |
| --- | --- |
| Original `NostalgiaForInfinityX7` | Baseline |
| `TestX7` rebased on the same X7 version | Optimized candidate |

Keep these inputs identical:

- same Freqtrade version
- same NFI version
- same exchange and trading mode
- same config
- same timerange
- same pairlist and effective pair set
- same candle data
- same stake, leverage, and `max_open_trades`
- same cache policy, documented explicitly

### Measurements

Measure at least these timings:

| Area | What to record |
| --- | --- |
| Total wall time | Full command runtime from start to exit |
| `populate_indicators` | Time spent building indicators per pair/timeframe |
| Informative timeframes | Time spent on informative dataframe preparation |
| BTC informative | BTC informative build/reuse cost |
| Merge | Time spent merging informative data into base timeframe |
| Entry conditions | Time spent evaluating entry masks and tags |
| Exit conditions | Time spent evaluating exit masks and tags |
| Worker overhead | Process startup, serialization, IPC, scheduling, and result collection |

The profiler should make it clear whether time moved from strategy calculation
to worker overhead. A faster average runtime is not enough if worker overhead
creates worse small-machine behavior.

### Cache Conditions

Run with documented cache settings. At minimum:

1. Cold or no-cache run, such as `--cache none`, to measure full computation.
2. Repeat-run behavior, if relevant, to identify Freqtrade cache effects.
3. Clear notes about whether the exported result came from a fresh run or a
   reused cache.

Any backtest-speed claim must state the cache mode next to the result.

### Trade-Surface Parity

Speed must remain secondary to behavior.

After each comparison, export trades and compare the checked trade surface:

- trade count
- pair
- open time
- close time
- entry side
- exit reason
- enter tag
- profit summary
- drawdown summary

The expected gate is:

```text
trade_surface_equal=true
first_difference=null
```

If the trade surface does not match, the profiling result is not acceptable as
an equivalent optimization result, even if it is faster.

### Success Criteria

The backtest profiling result can be called successful only if all of these are
true:

- total wall time is lower for `TestX7`
- the main saved time is in strategy calculation, informative handling, merge,
  or condition evaluation
- worker overhead does not dominate the result
- checked trade-surface parity remains equal
- the result is repeatable enough to survive at least one re-run
- the report clearly names the machine, worker settings, pair count, timerange,
  cache policy, and Freqtrade/NFI versions

### Failure Criteria

Treat the candidate as failed or not ready if any of these happen:

- trade-surface mismatch
- worker overhead grows enough to erase the gain
- performance gets worse on a small VPS or low-CPU machine
- memory pressure or process churn makes the run unstable
- the result only works with a narrow cache condition that is not disclosed
- the output cannot be independently inspected from exported artifacts

### Report Template

Record each controlled run in this shape:

```text
Machine:
CPU/RAM:
OS/Docker:
Freqtrade version:
NFI version:
Trading mode:
Timerange:
Configured pairs:
Effective pairs:
Workers:
Cache policy:

Original X7 runtime:
TestX7 runtime:
Runtime delta:

trade_surface_equal:
first_difference:

Main profiler bottleneck before:
Main profiler bottleneck after:
Notes:
```

### Claim Boundary

Until this plan is executed with exported artifacts, the correct public wording
is:

```text
Backtest speed needs separate controlled profiling.
Current backtest speed evidence includes an external community report, but it is
not independently reproduced here and is not globally proven backtest speedup.
```

Do not describe the current repository as production-ready. Do not describe any
runtime difference as a profit improvement.

---

## 한국어

### 목적

현재 `TestX7`에서 가장 강하게 검증된 부분은 live-style `analyze(pairs)`
경로입니다. 이 경로에서는 로컬 기준 큰 속도 개선이 있었고, 검증한 trade
surface도 원본 X7과 같았습니다.

하지만 backtest는 실행 경로가 다릅니다. 그래서 다음 NFI 버전에 맞춰
리베이스한 뒤에는 backtest 속도도 따로 측정해야 합니다. live-style 결과가
그대로 backtest에도 적용된다고 가정하면 안 됩니다.

### 비교 범위

비교 대상:

| 대상 | 의미 |
| --- | --- |
| 원본 `NostalgiaForInfinityX7` | 기준본 |
| 같은 X7 버전에 맞춘 `TestX7` | 최적화 후보 |

아래 조건은 같게 맞춥니다.

- 같은 Freqtrade 버전
- 같은 NFI 버전
- 같은 exchange / trading mode
- 같은 config
- 같은 timerange
- 같은 pairlist와 실제 effective pair set
- 같은 candle data
- 같은 stake, leverage, `max_open_trades`
- 명확히 기록한 같은 cache 조건

### 측정 항목

최소한 아래 항목을 측정합니다.

| 영역 | 기록할 내용 |
| --- | --- |
| 전체 wall time | 명령 시작부터 종료까지 걸린 전체 시간 |
| `populate_indicators` | pair/timeframe별 indicator 계산 시간 |
| informative timeframe | informative dataframe 준비 시간 |
| BTC informative | BTC informative 생성/재사용 비용 |
| merge | informative data를 base timeframe에 합치는 시간 |
| entry condition | entry mask와 tag 평가 시간 |
| exit condition | exit mask와 tag 평가 시간 |
| worker overhead | process 시작, serialization, IPC, scheduling, 결과 수집 비용 |

단순히 평균 시간이 줄었다는 것만 보면 안 됩니다. 계산 시간이 줄었지만 worker
overhead가 커져서 작은 서버에서 나빠지는 구조라면 성공으로 보지 않습니다.

### Cache 조건

cache 설정은 결과 옆에 반드시 같이 적습니다.

1. `--cache none` 같은 cold/no-cache run으로 전체 계산 비용 측정
2. 필요하면 repeat-run으로 Freqtrade cache 영향을 별도 확인
3. export 결과가 새로 계산된 것인지 cache 재사용 결과인지 명시

backtest speed를 말할 때는 cache mode를 빼놓지 않습니다.

### Trade-Surface Parity

속도보다 중요한 것은 동작 동일성입니다.

각 비교가 끝나면 trades를 export하고 아래 surface를 비교합니다.

- trade count
- pair
- open time
- close time
- entry side
- exit reason
- enter tag
- profit summary
- drawdown summary

기대 gate는 아래입니다.

```text
trade_surface_equal=true
first_difference=null
```

trade surface가 다르면 더 빨라졌더라도 동일동작 최적화 결과로 받아들이면
안 됩니다.

### 성공 기준

아래를 모두 만족할 때만 backtest profiling 성공으로 봅니다.

- `TestX7`의 전체 wall time이 줄어듦
- 절약된 시간이 주로 strategy 계산, informative 처리, merge, condition 평가에서 나옴
- worker overhead가 결과를 지배하지 않음
- checked trade-surface parity가 유지됨
- 재실행해도 대체로 같은 경향이 유지됨
- machine, worker 설정, pair 수, timerange, cache policy, Freqtrade/NFI 버전이 같이 기록됨

### 실패 기준

아래 중 하나라도 나오면 실패 또는 아직 준비 안 된 상태로 봅니다.

- trade-surface mismatch
- worker overhead가 커져서 이득을 지움
- 작은 VPS나 낮은 CPU 환경에서 더 나빠짐
- memory pressure나 process churn으로 run이 불안정함
- 공개하지 않은 좁은 cache 조건에서만 좋아 보임
- exported artifact로 독립 검토가 어려움

### 기록 템플릿

controlled run마다 아래 형태로 남깁니다.

```text
Machine:
CPU/RAM:
OS/Docker:
Freqtrade version:
NFI version:
Trading mode:
Timerange:
Configured pairs:
Effective pairs:
Workers:
Cache policy:

Original X7 runtime:
TestX7 runtime:
Runtime delta:

trade_surface_equal:
first_difference:

Main profiler bottleneck before:
Main profiler bottleneck after:
Notes:
```

### 주장 범위

이 계획을 실제 artifact와 함께 수행하기 전까지는 아래 정도로만 말합니다.

```text
Backtest speed needs separate controlled profiling.
Current backtest speed evidence includes an external community report, but it is
not independently reproduced here and is not globally proven backtest speedup.
```

현재 repo를 production-ready라고 표현하지 않습니다. 속도 차이를 수익률 개선으로
표현하지도 않습니다.
