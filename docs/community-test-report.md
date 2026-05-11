# TestX7 Community Test Report

This document records an external community report shared by Onur. It is useful
as a community test case, but it was not independently reproduced in this
repository.

Claim boundary:

```text
not production-ready
not a profit claim
not globally proven backtest speedup
external community report
```

This is a community test report, not a formal benchmark.

## English

### Status

This report captures one community-shared local backtest result for `TestX7`.
It should be treated as a data point to guide future profiling, not as a formal
benchmark.

The raw exported summary/artifact is not available in this repository yet, so
the result is recorded as reported by the user.

### Reported Environment

| Field | Reported value |
| --- | --- |
| Tester | Onur |
| Test machine | MacBook |
| CPU platform | Apple Silicon |
| Live server mentioned by tester | Hetzner CCX33 |
| Was Hetzner CCX33 the measured backtest machine? | No |
| Trading mode | Futures USDT |
| Timeframe | `5m` |
| Timerange | `20250101-20260101` |
| Configured pairlist | 15 coins |
| Initially described effective coins | 12 coins |
| `max_open_trades` | `6` |
| `stake_amount` | `unlimited` |
| Leverage | `3x` |
| Worker setting | default worker auto-detect |

### Reported Result

| Candidate | Runtime |
| --- | ---: |
| Original X7 | `214s` |
| `TestX7` | `137s` |

Reported runtime delta:

```text
214s -> 137s
about 36% faster
```

The user also reported that the results matched. Because no exported summary or
raw artifact is committed here yet, this repository records that as:

```text
Result surface matched according to the external community report.
Not independently reproduced here.
```

### Interpretation

This is a useful signal because it suggests that `TestX7` may improve at least
some backtest runs, not only the live-style `analyze(pairs)` loop.

It is not enough to claim a global backtest-speed improvement. Backtest speed
depends on the machine, worker count, pair count, timerange, cache state,
Freqtrade version, NFI version, and data layout.

### What To Collect Next

For this report to become independently reviewable, future testers should share:

- exact command
- Freqtrade version
- NFI version
- full config or sanitized config
- configured pairlist and effective pairlist
- worker setting or environment variables
- cache policy
- exported backtest summary
- exported trades or parity-comparison output
- profiler output, if available

### Safe Public Wording

Use wording like this:

```text
A community user reported a MacBook Apple Silicon backtest where Original X7
took 214s and TestX7 took 137s, about 36% faster, with matched results.
This is an external community report and has not been independently reproduced
in this repository.
```

Avoid wording like this:

```text
TestX7 is production-ready.
TestX7 improves profit.
TestX7 globally speeds up all backtests.
```

---

## 한국어

### 현재 상태

이 문서는 Onur가 공유한 외부 커뮤니티 backtest 결과를 기록한 것입니다.
공식 benchmark가 아니라, 다음 profiling을 설계할 때 참고할 community test
case로 봅니다.

아직 이 repo 안에는 exported summary/raw artifact가 없습니다. 그래서 이 결과는
검증 완료 사실이 아니라 사용자가 공유한 외부 보고로만 기록합니다.

### 보고된 환경

| 항목 | 보고된 값 |
| --- | --- |
| 테스트 공유자 | Onur |
| 테스트 머신 | MacBook |
| CPU 플랫폼 | Apple Silicon |
| 같이 언급된 live 서버 | Hetzner CCX33 |
| Hetzner CCX33이 이번 backtest 측정 머신인가? | 아님 |
| Trading mode | Futures USDT |
| Timeframe | `5m` |
| Timerange | `20250101-20260101` |
| 설정된 pairlist | 15 coins |
| 처음 설명한 effective coins | 12 coins |
| `max_open_trades` | `6` |
| `stake_amount` | `unlimited` |
| Leverage | `3x` |
| Worker 설정 | default worker auto-detect |

### 보고된 결과

| 대상 | Runtime |
| --- | ---: |
| 원본 X7 | `214s` |
| `TestX7` | `137s` |

보고된 runtime 차이:

```text
214s -> 137s
about 36% faster
```

사용자 보고에 따르면 결과도 matched였습니다. 다만 exported summary나 raw
artifact가 아직 repo에 없으므로, 이 문서에서는 아래처럼만 기록합니다.

```text
Result surface matched according to the external community report.
Not independently reproduced here.
```

### 해석

이 결과는 좋은 신호입니다. `TestX7`가 live-style `analyze(pairs)` loop뿐 아니라
일부 backtest에서도 빨라질 수 있다는 가능성을 보여줍니다.

하지만 이 한 사례만으로 모든 backtest에서 빨라진다고 말할 수는 없습니다.
Backtest speed는 machine, worker 수, pair 수, timerange, cache 상태,
Freqtrade 버전, NFI 버전, 데이터 구조에 영향을 받습니다.

### 다음에 받아야 할 자료

이 보고를 독립 검토 가능한 자료로 만들려면 다음 정보가 필요합니다.

- 정확한 command
- Freqtrade version
- NFI version
- 전체 config 또는 secret을 제거한 config
- configured pairlist와 effective pairlist
- worker 설정 또는 environment variables
- cache policy
- exported backtest summary
- exported trades 또는 parity-comparison output
- 가능하면 profiler output

### 안전한 공개 표현

아래처럼 말하는 것이 안전합니다.

```text
A community user reported a MacBook Apple Silicon backtest where Original X7
took 214s and TestX7 took 137s, about 36% faster, with matched results.
This is an external community report and has not been independently reproduced
in this repository.
```

아래처럼 말하면 안 됩니다.

```text
TestX7 is production-ready.
TestX7 improves profit.
TestX7 globally speeds up all backtests.
```
