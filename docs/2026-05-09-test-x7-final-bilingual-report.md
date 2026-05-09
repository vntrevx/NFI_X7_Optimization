# Test X7 Final Bilingual Report

Date: 2026-05-09 KST

## Korean Report

### 한 줄 결론

완료했다. 최신 NFI X7 원본은 그대로 보존했고, `TestX7`는 원본과 같은 매매 결과를 내면서 80페어 분석 시간을 원본 평균 약 `238.833초`에서 최종 평균 `3.283842초`로 줄였다. 최종 80페어 40회 게이트는 `gate=PASS`다.

쉽게 말하면 이렇다.

- 매매 판단 공식은 바꾸지 않았다.
- 같은 문제를 더 빨리 푸는 계산 구조로 바꿨다.
- 원본 X7은 그대로 남겨 두었다.
- 새 실험판은 `TestX7`라는 다른 전략 파일로 만들었다.
- 로컬 10 CPU / 8 workers 조건에서 80페어 전체 계산이 매번 5초 안에 끝났다.

### 무엇을 바꿨나

원본 `NostalgiaForInfinityX7.py`는 건드리지 않고 기준본으로 보존했다. 대신 `TestX7.py`를 만들고, 큰 단일 파일 구조를 아래 모듈들로 나눴다.

| 영역 | 파일 |
| --- | --- |
| Freqtrade 진입점 | `user_data/strategies/TestX7.py` |
| 지표 계산 | `user_data/strategies/test_x7_modules/indicator_logic.py` |
| 진입 조건 계산 | `user_data/strategies/test_x7_modules/entry_logic.py` |
| BTC informative cache | `user_data/strategies/test_x7_modules/btc_cache.py` |
| 일반 informative cache | `user_data/strategies/test_x7_modules/informative_cache.py` |
| 빠른 informative merge | `user_data/strategies/test_x7_modules/merge.py` |
| 멀티프로세스 pair 분석 | `user_data/strategies/test_x7_modules/parallel_analyze.py` |
| CPU/worker 선택 | `user_data/strategies/test_x7_modules/cpu.py` |
| 최종 5초 게이트 | `tools/test_x7/run_80pair_5s_gate.sh` |

### 무엇을 바꾸지 않았나

매매 로직은 의도적으로 바꾸지 않았다.

- entry/exit 조건 의미 변경 없음
- DCA/grind/position adjustment 의미 변경 없음
- leverage/stake callback 의미 변경 없음
- signal tag 의미 변경 없음
- Freqtrade core 수정 없음
- laptop live 서버 배포 없음

쉽게 말하면, 차의 엔진 세팅은 바꾸지 않고 계산하는 길만 넓힌 것이다.

### 팩트체크

| 체크 | 결과 |
| --- | --- |
| NFI upstream 최신 여부 | `HEAD == origin/main == 75c223b0f1a76731f4555aeb70fd0c92df9f30ea` |
| commit 제목 | `Merge branch 'dev-ngyun-fix/updater-race-condition'` |
| X7 version | `v17.4.59` |
| 원본 X7 보존 | upstream X7과 local X7 SHA256 동일 |
| SHA256 | `26ac1698b58bf8356cf67ea9874ba0eaed95fbebad80fb630366b3f39c00994c` |
| Freqtrade 로딩 | `NostalgiaForInfinityX7 OK`, `TestX7 OK` |
| host CPU | `10` |
| Docker CPU | `10` |
| 최종 worker 수 | `8` |

### 매매 결과가 같은가

같다. 이 부분이 가장 중요하다.

80페어 1년 백테스트 비교:

| 항목 | 원본 X7 | TestX7 |
| --- | ---: | ---: |
| Trades | `195` | `195` |
| Total profit | `1156.7473364 USDT` | `1156.7473364 USDT` |
| Winrate | `98.974%` | `98.974%` |
| Profit factor | `67.1806145028` | `67.1806145028` |
| Max drawdown | `17.47864303 USDT` | `17.47864303 USDT` |
| Trade surface equal | `true` | `true` |
| First difference | `null` | `null` |

뜻은 간단하다. 원본이 산 코인, 산 시간, 판 시간, 수익, 태그가 `TestX7`와 같았다.

58페어 1년 백테스트도 같은 방식으로 통과했다:

| 항목 | 결과 |
| --- | ---: |
| Trades | `177` |
| Total profit | `829.12929377 USDT` |
| Profit factor | `5.0241561988` |
| Max drawdown | `206.03804942 USDT` |
| Trade surface equal | `true` |
| First difference | `null` |

### 속도 결과

80페어 live-loop 비교:

| 항목 | 원본 X7 | TestX7 최종 |
| --- | ---: | ---: |
| Pairs | `80` | `80` |
| Loops | `3` | `40` |
| Min | `232.561062s` | `3.051825s` |
| Avg | `238.833499s` | `3.283842s` |
| Max | `242.990876s` | `3.830582s` |
| Over 5s | `3/3` | `0/40` |
| Gate | fail | `PASS` |

속도 개선:

```text
238.833499 / 3.283842 = about 72.7x faster
```

58페어도 40회 모두 5초 안에 끝났다. 최고값은 `4.351102s`였다.

### 왜 8 workers인가

10 CPU가 보인다고 workers도 10개를 쓰는 것이 항상 좋은 것은 아니었다.

테스트 결과:

| 설정 | 결과 |
| --- | --- |
| 10 CPU / 10 workers | 평균은 빨랐지만 max `7.591558s`, over5 `6/40`, 실패 |
| 10 CPU / 8 workers | max `3.830582s`, over5 `0/40`, 성공 |

이유는 단순하다. CPU를 전부 꽉 채우면 순간적으로 줄이 막힐 수 있다. 2개 CPU를 남겨두면 운영체제, Docker, Freqtrade 본체가 숨 쉴 공간이 생긴다. 그래서 최종 안전값은 `8 workers`다.

### 다시 검증하는 방법

```bash
cd /home/user/project/freqtrade-nfi
tools/test_x7/run_80pair_5s_gate.sh
```

성공 조건:

```text
gate=PASS
over5=0
max <= 5.0s
```

최종 증거 파일:

- `user_data/backtest_results/test_x7_v17459_80_1y/testx7-live-loop-80pairs-40loops-workers8-20260509-182558.txt`

최종 감사 문서:

- `docs/2026-05-09-test-x7-completion-audit.md`

### 남은 리스크

이 작업은 로컬 검증 완료다. 아직 laptop live/futures 서버에 배포한 것은 아니다.

남은 주의점:

- live laptop에서는 다시 CPU, Docker, futures config, exchange latency를 확인해야 한다.
- 백테스트 수익률은 미래 수익 보장이 아니다.
- 업스트림 NFI에 PR로 올리려면 코드 스타일, 테스트 범위, 설정 옵션 이름을 개발자 취향에 맞게 더 다듬어야 할 수 있다.

### 개발자에게 보여줄 짧은 설명

`TestX7` keeps the original X7 trading surface equal while moving the expensive live pair analysis into a stable process-worker path. On local 10-CPU Docker, 80 pairs complete in 40/40 loops under 5 seconds, with final average `3.283842s` and max `3.830582s`. Original X7 measured about `238.833s` average for the same 80-pair live-loop harness.

## English Report

### One-line verdict

Done. The latest original NFI X7 file is preserved, and `TestX7` produces the same trading result while reducing the 80-pair analysis loop from about `238.833s` average to `3.283842s` average. The final 80-pair 40-loop gate is `gate=PASS`.

In simple words:

- We did not change the trading decisions.
- We changed how the same calculations are organized and executed.
- The original X7 file stays untouched as the baseline.
- The optimized version is a separate strategy named `TestX7`.
- On local 10 CPU / 8 workers, all 80-pair loops finished under 5 seconds.

### What changed

The original `NostalgiaForInfinityX7.py` was preserved. The new strategy is `TestX7.py`, with the large strategy split into focused modules.

| Area | File |
| --- | --- |
| Freqtrade entrypoint | `user_data/strategies/TestX7.py` |
| Indicator calculation | `user_data/strategies/test_x7_modules/indicator_logic.py` |
| Entry calculation | `user_data/strategies/test_x7_modules/entry_logic.py` |
| BTC informative cache | `user_data/strategies/test_x7_modules/btc_cache.py` |
| General informative cache | `user_data/strategies/test_x7_modules/informative_cache.py` |
| Fast informative merge | `user_data/strategies/test_x7_modules/merge.py` |
| Multiprocess pair analysis | `user_data/strategies/test_x7_modules/parallel_analyze.py` |
| CPU and worker selection | `user_data/strategies/test_x7_modules/cpu.py` |
| Final 5-second gate | `tools/test_x7/run_80pair_5s_gate.sh` |

### What did not change

The trading logic was intentionally preserved.

- No entry/exit meaning change
- No DCA/grind/position adjustment meaning change
- No leverage/stake callback meaning change
- No signal tag meaning change
- No Freqtrade core patch
- No laptop live deployment

Simple explanation: the strategy still makes the same decisions. It just reaches those decisions faster.

### Fact check

| Check | Result |
| --- | --- |
| Latest NFI upstream | `HEAD == origin/main == 75c223b0f1a76731f4555aeb70fd0c92df9f30ea` |
| Commit title | `Merge branch 'dev-ngyun-fix/updater-race-condition'` |
| X7 version | `v17.4.59` |
| Original X7 preserved | upstream X7 and local X7 have the same SHA256 |
| SHA256 | `26ac1698b58bf8356cf67ea9874ba0eaed95fbebad80fb630366b3f39c00994c` |
| Freqtrade strategy loading | `NostalgiaForInfinityX7 OK`, `TestX7 OK` |
| Host CPU | `10` |
| Docker CPU | `10` |
| Final worker count | `8` |

### Is the trading result the same?

Yes. This is the most important point.

80-pair one-year backtest comparison:

| Metric | Original X7 | TestX7 |
| --- | ---: | ---: |
| Trades | `195` | `195` |
| Total profit | `1156.7473364 USDT` | `1156.7473364 USDT` |
| Winrate | `98.974%` | `98.974%` |
| Profit factor | `67.1806145028` | `67.1806145028` |
| Max drawdown | `17.47864303 USDT` | `17.47864303 USDT` |
| Trade surface equal | `true` | `true` |
| First difference | `null` | `null` |

This means the compared trades matched: pair, open time, close time, profit, and tags.

The 58-pair one-year comparison also passed:

| Metric | Result |
| --- | ---: |
| Trades | `177` |
| Total profit | `829.12929377 USDT` |
| Profit factor | `5.0241561988` |
| Max drawdown | `206.03804942 USDT` |
| Trade surface equal | `true` |
| First difference | `null` |

### Speed result

80-pair live-loop comparison:

| Metric | Original X7 | Final TestX7 |
| --- | ---: | ---: |
| Pairs | `80` | `80` |
| Loops | `3` | `40` |
| Min | `232.561062s` | `3.051825s` |
| Avg | `238.833499s` | `3.283842s` |
| Max | `242.990876s` | `3.830582s` |
| Over 5s | `3/3` | `0/40` |
| Gate | fail | `PASS` |

Speedup:

```text
238.833499 / 3.283842 = about 72.7x faster
```

The 58-pair benchmark also passed 40/40 loops under 5 seconds. Its max was `4.351102s`.

### Why 8 workers?

Seeing 10 CPUs does not mean using 10 workers is always best.

Measured result:

| Setting | Result |
| --- | --- |
| 10 CPU / 10 workers | Fast average, but max `7.591558s`, over5 `6/40`, failed |
| 10 CPU / 8 workers | max `3.830582s`, over5 `0/40`, passed |

Simple reason: if all CPUs are fully busy, the operating system, Docker, and Freqtrade itself can get delayed. Leaving two CPUs free removed the spikes. So the final safe worker count is `8`.

### How to verify again

```bash
cd /home/user/project/freqtrade-nfi
tools/test_x7/run_80pair_5s_gate.sh
```

Success condition:

```text
gate=PASS
over5=0
max <= 5.0s
```

Final evidence file:

- `user_data/backtest_results/test_x7_v17459_80_1y/testx7-live-loop-80pairs-40loops-workers8-20260509-182558.txt`

Final audit:

- `docs/2026-05-09-test-x7-completion-audit.md`

### Remaining risks

This is complete for local validation. It has not been deployed to the laptop live/futures server.

Remaining cautions:

- The laptop live environment needs its own CPU, Docker, futures config, and exchange-latency validation.
- Backtest profit is not a promise of future profit.
- If this becomes an upstream NFI PR, maintainers may still want changes to style, test scope, and configuration naming.

### Short developer summary

`TestX7` preserves the original X7 trading surface while moving the expensive live pair analysis into a stable process-worker path. On local 10-CPU Docker, 80 pairs complete 40/40 loops under 5 seconds, with final average `3.283842s` and max `3.830582s`. Original X7 measured about `238.833s` average for the same 80-pair live-loop harness.
