# NFI X7 Optimization Proof Package

NostalgiaForInfinity X7 is a strong strategy, but the live analysis loop can get painfully slow when many pairs are enabled.
This repository is a proof package for a local optimized fork called `TestX7`.

The goal was simple:

> Keep the original X7 trading behavior, but make the live pair analysis finish much faster.

That goal passed locally.

## 결과 먼저 보기

최신 NFI X7 원본은 그대로 보존했고, 최적화 버전은 `TestX7`라는 별도 전략으로 만들었다.

80페어 기준 live-style analysis loop 결과:

| Item | Original X7 | TestX7 |
| --- | ---: | ---: |
| Pairs | `80` | `80` |
| Test loops | `3` | `40` |
| Average loop time | `238.833499s` | `3.283842s` |
| Max loop time | `242.990876s` | `3.830582s` |
| Loops over 5s | `3/3` | `0/40` |
| Gate | failed | `PASS` |

대략 `72.7x` 빨라졌다.

중요한 점은 속도만 빨라진 게 아니다. 1년 백테스트에서 원본 X7과 `TestX7`의 거래 결과가 같았다.

| Check | Result |
| --- | --- |
| Trade count | `195 == 195` |
| Total profit | `1156.7473364 USDT == 1156.7473364 USDT` |
| Profit factor | `67.1806145028 == 67.1806145028` |
| Max drawdown | `17.47864303 USDT == 17.47864303 USDT` |
| Trade-by-trade comparison | `trade_surface_equal=true` |
| First mismatch | `null` |

쉽게 말하면:

- 원본이 산 코인을 `TestX7`도 샀다.
- 원본이 판 시점에 `TestX7`도 팔았다.
- 수익, 태그, 거래 표면이 같았다.
- 계산만 훨씬 빨라졌다.

## 이게 뭔가?

`TestX7`는 원본 X7을 직접 덮어쓴 전략이 아니다.

원본은 `user_data/strategies/NostalgiaForInfinityX7.py`에 그대로 있다.
최적화 실험판은 `user_data/strategies/TestX7.py`와 `user_data/strategies/test_x7_modules/`에 따로 있다.

기존 X7은 거대한 단일 파일 구조라서 병목을 찾고 바꾸기 어렵다.
`TestX7`는 그 구조를 기능별 모듈로 나눴다.

주요 파일:

| Path | Purpose |
| --- | --- |
| `user_data/strategies/TestX7.py` | Freqtrade strategy entrypoint |
| `user_data/strategies/test_x7_modules/indicator_logic.py` | Indicator and informative calculations |
| `user_data/strategies/test_x7_modules/entry_logic.py` | Entry condition logic |
| `user_data/strategies/test_x7_modules/parallel_analyze.py` | Stable process-worker live analysis path |
| `user_data/strategies/test_x7_modules/btc_cache.py` | BTC informative cache |
| `user_data/strategies/test_x7_modules/informative_cache.py` | Non-BTC informative cache |
| `user_data/strategies/test_x7_modules/merge.py` | Faster informative merge helper |
| `tools/test_x7/run_80pair_5s_gate.sh` | Final 80-pair speed gate |

## 바꾸지 않은 것

이번 작업은 수익률을 높이려고 신호를 튜닝한 작업이 아니다.

의도적으로 건드리지 않은 것:

- entry / exit 의미
- DCA / grind 의미
- position adjustment 의미
- leverage / stake callbacks
- signal tags
- Freqtrade core
- live laptop deployment

이 저장소는 “매매 로직을 바꿔서 수익이 좋아졌다”가 아니라
“같은 매매 로직을 훨씬 빠르게 계산했다”를 보여주는 자료다.

## 왜 8 workers인가?

처음에는 “CPU가 10개면 workers도 10개 쓰면 되지 않나?”라고 볼 수 있다.
실제로는 그렇지 않았다.

| Setting | Result |
| --- | --- |
| `10 CPU / 10 workers` | average was fast, but max hit `7.591558s`; failed |
| `10 CPU / 8 workers` | max stayed at `3.830582s`; passed |

10개를 전부 계산 worker로 써버리면 Docker, Python, Freqtrade 본체, OS scheduler가 숨 쉴 공간이 줄어든다.
그래서 최종값은 CPU 10개 중 8개만 worker로 쓰는 쪽이 더 안정적이었다.

## 직접 다시 확인하기

### 1. Strategy loading

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

### 2. Final 80-pair speed gate

```bash
tools/test_x7/run_80pair_5s_gate.sh
```

Expected:

```text
gate=PASS
over5=0
max <= 5.0s
```

The recorded final run is here:

```text
user_data/backtest_results/test_x7_v17459_80_1y/testx7-live-loop-80pairs-40loops-workers8-20260509-182558.txt
```

## Evidence files

| File | What it proves |
| --- | --- |
| `user_data/backtest_results/test_x7_v17459_80_1y/compare.json` | 80-pair one-year parity |
| `user_data/backtest_results/test_x7_v17459_final_5s_1y_required/compare.json` | 58-pair one-year parity |
| `user_data/backtest_results/test_x7_v17459_80_1y/original-live-loop-80pairs-3loops.txt` | Original X7 live-loop speed |
| `user_data/backtest_results/test_x7_v17459_80_1y/testx7-live-loop-80pairs-40loops-workers8-20260509-182558.txt` | Final TestX7 speed gate |
| `docs/2026-05-09-test-x7-completion-audit.md` | Full completion checklist |
| `docs/2026-05-09-test-x7-final-bilingual-report.md` | Korean/English detailed report |

## Important caveats

This is not a promise of future profit.

Backtests are historical simulations. They do not guarantee live results.
The optimization was validated locally. It has not been deployed to the live laptop futures bot.

Before live use, check:

- the actual machine CPU count
- Docker CPU visibility
- futures config
- exchange/network latency
- live Freqtrade behavior

## English summary

This repository contains a local proof package for `TestX7`, an optimized fork of NFI X7.

The original `NostalgiaForInfinityX7.py` is preserved. `TestX7` keeps the same trading surface in the checked one-year backtests, while moving expensive live pair analysis into a stable process-worker path.

Final local result:

- Original X7 80-pair live-loop average: `238.833499s`
- Final TestX7 80-pair live-loop average: `3.283842s`
- Final TestX7 max loop time: `3.830582s`
- Over 5 seconds: `0/40`
- Final gate: `PASS`
- 80-pair backtest parity: `trade_surface_equal=true`
- First mismatch: `null`

This is not a trading-signal improvement. It is a performance and structure improvement that keeps the checked trading behavior unchanged.
