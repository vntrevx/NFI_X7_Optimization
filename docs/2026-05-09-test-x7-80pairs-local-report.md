# TestX7 80-Pair Local Report

Date: 2026-05-09 KST

## One-Line Verdict

80페어 작업은 로컬에서 끝까지 검증했다.

매매 결과는 원본 X7과 같았다. 속도는 원본보다 크게 빨라졌고, WSL/Docker가 10 CPU를 노출한 뒤 최종 8-worker 설정에서 80페어 40회 모두 5초 안에 끝났다.

## Easy Explanation

어렵게 말하지 않으면 이렇다.

- 원본 X7은 80개 코인을 한 바퀴 계산하는 데 약 4분이 걸렸다.
- TestX7은 같은 일을 최종 safe config 기준 평균 약 3.28초에 끝냈다.
- 그래서 속도 개선은 매우 크다.
- 목표였던 "무조건 5초 안"도 최종 40회 게이트에서 통과했다.
- 대신 58페어에서는 이미 40번 모두 5초 안에 끝났다.

## Did We Keep The Trading Logic?

Yes. 원본 전략의 매매 로직은 유지했다.

증거는 백테스트 결과다. 원본 X7과 TestX7을 같은 기간, 같은 페어, 같은 설정으로 돌린 뒤 거래 하나하나를 비교했다.

80페어 1년 결과:

| Check | Original X7 | TestX7 |
| --- | ---: | ---: |
| Timerange | `20250401-20260401` | `20250401-20260401` |
| Trades | `195` | `195` |
| Total profit | `1156.7473364 USDT` | `1156.7473364 USDT` |
| Total profit % | `115.67%` | `115.67%` |
| Winrate | `98.974%` | `98.974%` |
| Profit factor | `67.1806145028` | `67.1806145028` |
| Max drawdown | `17.47864303 USDT` | `17.47864303 USDT` |
| Best pair | `DASH/USDT` | `DASH/USDT` |
| Worst pair | `SAHARA/USDT` | `SAHARA/USDT` |
| Trade-by-trade equal | `true` | `true` |

비교 파일:

- `user_data/backtest_results/test_x7_v17459_80_1y/compare.json`

핵심 값:

```json
"first_difference": null,
"trade_surface_equal": true
```

뜻은 간단하다.

원본이 산 시간, 판 시간, 코인, 수익, 태그가 TestX7과 같았다.

## 80-Pair Speed Result

After WSL restart, use this gate command instead of hand-parsing loops:

```bash
tools/test_x7/run_80pair_5s_gate.sh
```

It leaves two CPUs free when Docker exposes at least 8 CPUs and fails unless all
40 loops are `<= 5.0s`.

### Original X7

원본 X7 live-loop 80페어 3회:

| Metric | Value |
| --- | ---: |
| Loops | `3` |
| Min | `232.561s` |
| Avg | `238.833s` |
| Max | `242.991s` |
| Over 5s | `3/3` |

원본은 80페어 한 바퀴가 약 4분이다.

### TestX7

TestX7 live-loop 80페어 40회:

| Metric | Value |
| --- | ---: |
| Loops | `40` |
| Min | `3.052s` |
| Avg | `3.284s` |
| Max | `3.831s` |
| Over 5s | `0/40` |

TestX7은 원본보다 약 `72.7x` 빠르다.

계산:

```text
238.833 / 3.284 = 72.7x
```

최종 5초 목표도 통과했다.

## Why 8 Workers Was Selected

초기 로컬 WSL/Docker는 4 logical CPU 조건이라 80페어 5초 게이트를 통과하지 못했다.

이후 WSL/Docker가 10 CPU를 노출한 뒤 다시 측정했다:

- `/mnt/c/Users/0/.wslconfig`에는 `processors=10`이 설정되어 있다.
- 현재 `nproc`와 Docker `nproc`는 `10` CPU를 보여준다.
- `10` workers는 평균은 빨랐지만 순간 스파이크로 5초를 넘었다.
- `8` workers는 CPU 2개를 남겨 스케줄링 스파이크를 줄였고 최종 게이트를 통과했다.

80페어는 각 페어마다 다음 작업을 한다.

- 5m 기본 지표 계산
- 15m/1h/4h/1d 보조 시간봉 계산
- BTC 보조 시간봉 병합
- 진입 조건 계산
- Freqtrade가 쓰는 최신 분석 dataframe 저장

TestX7은 이 작업을 worker process로 나눴고, 최종적으로 8개 stable worker가 가장 안정적이었다.

그래서 결론은 이렇다.

- 58페어: 5초 안에 안정적으로 들어온다.
- 80페어: 10 CPU / 8 workers에서 5초 안에 안정적으로 들어온다.

## Extra 80-Pair Tuning Attempts

80페어 5초를 끝까지 밀어보기 위해 추가 실험도 했다. 결과는 아래와 같다.

| Experiment | Loops | Min | Avg | Max | Over 5s | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 5 workers | `12` | `4.874s` | `5.107s` | `5.553s` | `9/12` | worse |
| 6 workers | `12` | `5.018s` | `5.231s` | `5.487s` | `12/12` | worse |
| 8 workers | `12` | `4.864s` | `5.166s` | `5.570s` | `9/12` | worse |
| More aggressive informative tails `15m=64,1h=200,4h=200,1d=40` | `40` | `4.719s` | `5.143s` | `5.897s` | `26/40` | rejected |
| Live-tail base-first merge reorder prototype | `40` | `4.770s` | `5.115s` | `5.908s` | `27/40` | reverted |
| Entry tail `6` only | `40` | `4.740s` | `5.120s` | `6.042s` | `23/40` | rejected |
| Entry tail `6` + aggressive informative tails | `40` | `4.648s` | `5.083s` | `5.875s` | `23/40` | rejected |
| Base tail `360` + entry tail `6` + aggressive informative tails | `40` | `4.681s` | `5.038s` | `5.751s` | `17/40` | rejected |
| Base tail `300` + entry tail `6` + aggressive informative tails | `40` | `4.664s` | `5.031s` | `5.818s` | `16/40` | rejected |
| Same as above with numeric thread limit disabled | `40` | `4.690s` | `5.082s` | `5.756s` | `21/40` | rejected |
| Precomputed long-shift prototype with indicator tail `6` | `40` | `4.710s` | `5.134s` | `6.063s` | `27/40` | reverted |
| 10 CPU / 10 workers | `40` | `2.748s` | `3.900s` | `7.592s` | `6/40` | rejected |
| 10 CPU / 8 workers | `20` | `3.078s` | `3.731s` | `4.849s` | `0/20` | candidate |
| 10 CPU / 8 workers final gate | `40` | `3.142s` | `3.422s` | `4.100s` | `0/40` | promoted |
| Default gate after script patch | `40` | `3.052s` | `3.284s` | `3.831s` | `0/40` | final |

The more aggressive tail candidate kept the current live fingerprint equal for
80 pairs in a one-loop check, but it did not improve the 40-loop gate. The
base-first merge reorder also kept fingerprint equality, but did not improve
the gate and was reverted to avoid keeping complexity without benefit.

Later tail-reduction candidates also kept a one-loop 80-pair live fingerprint
equal to the safe config, but none cleared the 40-loop 5-second gate. The best
4-vCPU local result was `base=300, entry=6, 15m=64, 1h=200, 4h=200, 1d=40`:
`avg=5.031s`, `max=5.818s`, `over5=16/40`. That was closer than the 4-vCPU
safe config at the time, but it still missed the gate, so it was not promoted.

A code prototype that precomputed long-period shifts before reducing the live
indicator tail to 6 rows also kept one-loop fingerprint equality, but the
40-loop gate got worse. That prototype was reverted.

Worker timing showed that stable 4-worker execution is already reasonably
balanced. The remaining >5s misses are mostly total CPU budget and host
scheduling jitter under the current 4 exposed CPUs, not a single obviously
misassigned pair.

After CPU 10 became active, worker timing showed that `10` workers could spike
when all logical CPUs were saturated. `8` workers was the measured stable point.

## CPU And Memory Evidence

80페어 1년 백테스트 CPU monitor:

| Run | CPU avg | CPU max | Max memory |
| --- | ---: | ---: | ---: |
| Original X7 1y | `92.54%` | `94.07%` | `20.77GiB` |
| TestX7 1y | `92.44%` | `94.53%` | `19.23GiB` |

이 숫자는 백테스트가 로컬에서 실제로 무겁게 돌았다는 뜻이다.

## Files Added For 80 Pairs

- `user_data/config-test-x7-80pairs.example.json`
- `user_data/config-original-x7-80pairs.example.json`

이 두 파일은 80페어를 고정해서 원본과 TestX7을 같은 조건으로 비교하기 위해 만들었다.

## Artifacts

80페어 1년 원본:

- `user_data/backtest_results/test_x7_v17459_80_1y/original/backtest-result-2026-05-08_23-39-05.zip`
- `user_data/logs/test_x7_v17459_80_1y/original.stdout.log`
- `user_data/logs/test_x7_v17459_80_1y/original.cpu.log`

80페어 1년 TestX7:

- `user_data/backtest_results/test_x7_v17459_80_1y/testx7/backtest-result-2026-05-08_23-53-27.zip`
- `user_data/logs/test_x7_v17459_80_1y/testx7.stdout.log`
- `user_data/logs/test_x7_v17459_80_1y/testx7.cpu.log`

80페어 live-loop:

- `user_data/backtest_results/test_x7_v17459_80_1y/original-live-loop-80pairs-3loops.txt`
- `user_data/backtest_results/test_x7_v17459_80_1y/testx7-live-loop-80pairs-40loops.txt`
- `user_data/backtest_results/test_x7_v17459_80_1y/testx7-live-loop-80pairs-40loops-w4-tuned.txt`
- `user_data/backtest_results/test_x7_v17459_80_1y/testx7-live-loop-80pairs-40loops-workers8-20260509-181651.txt`
- `user_data/backtest_results/test_x7_v17459_80_1y/testx7-live-loop-80pairs-40loops-workers8-20260509-182153.txt`
- `user_data/backtest_results/test_x7_v17459_80_1y/testx7-live-loop-80pairs-40loops-workers8-20260509-182558.txt`

## Would An NFI Developer Be Shocked?

Blunt answer: 숫자만 보면 놀랄 만하다.

이유:

- 원본 80페어 live-loop가 약 239초다.
- TestX7 80페어 live-loop가 최종 safe config 기준 평균 약 3.28초다.
- 1년 백테스트 거래 결과가 원본과 완전히 같다.
- 원본 77k 줄 단일 파일을 Freqtrade entrypoint와 모듈들로 분리했다.

하지만 아직 "그대로 업스트림 PR" 수준이라고 말하면 안 된다.

이유:

- 업스트림 개발자는 이 구조를 자기 배포 방식과 유지보수 방식에 맞게 다시 검토할 것이다.
- futures/live laptop 조건은 별도 검증이 필요하다.
- 업스트림 개발자는 성능 숫자뿐 아니라 코드 유지보수성, 테스트, 설정 안전성도 볼 것이다.

정직한 판정:

이건 개발자가 관심을 가질 만한 강한 성능 패치다. 80페어 5초 목표도 로컬 10 CPU / 8 workers 조건에서 끝낸 상태다.

## Final Status

Done:

- NFI 최신 X7 기준으로 TestX7 생성
- 원본 X7 보존
- TestX7 모듈화
- 80페어 데이터 준비
- 80페어 short parity 통과
- 80페어 1년 parity 통과
- 원본 vs TestX7 live-loop 속도 비교
- 80페어용 4-worker/timeframe-tail safe config 재검증
- 5/6/8 worker oversubscription 실험
- 더 공격적인 tail/merge-order 실험 후 효과 없는 변경 revert
- entry/base tail 축소와 numeric thread 실험 후 80페어 5초 미통과 확인
- WSL/Docker 10 CPU 활성화 후 10-worker spike 확인
- 8-worker 최종 safe config 확정
- 80페어 40-loop strict 5초 게이트 통과
- 보고서 작성

Not done:

- laptop live/futures 배포
- Freqtrade core 수정
- 수익률 개선을 위한 매매 로직 변경
