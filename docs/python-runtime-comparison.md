# Python 3.13 vs 3.14 Runtime Comparison Report

This note answers the maintainer question: does the TestX7 speed result depend on Python 3.14?

Short answer: no. In this local live-style analyze benchmark, Python 3.14 was not the reason for the large speedup. TestX7 also passed the same 80-pair speed gate on Python 3.13.

## Maintainer Takeaway

- TestX7 was tested on Python 3.13.13 and Python 3.14.4.
- Both runtimes used Freqtrade 2026.4 and the same major dependency versions.
- TestX7 passed `40/40` 80-pair live-style analyze loops under 5 seconds on Python 3.13.
- Original X7 stayed around 206-209 seconds for one 80-pair live-style analyze loop on both runtimes.
- The large TestX7 speedup looks strategy-side, not Python-version-side.
- This is not a backtest-speed result and not a live production recommendation.

## Test Setup

The current default Freqtrade Docker image in this repo uses:

```text
freqtradeorg/freqtrade:stable
Freqtrade 2026.4
Python 3.14.3
```

For a cleaner runtime comparison, two local PyPI-based images were built from the same Dockerfile. This avoids comparing the official stable image against a custom Python 3.13 image with slightly different dependency patch versions.

| Runtime | Image | Freqtrade | Important packages |
| --- | --- | --- | --- |
| Python 3.13 | `nfi-x7-freqtrade:py313-2026.4` | `2026.4` | `pandas 3.0.2`, `numpy 2.4.4`, `pyarrow 24.0.0`, `TA-Lib 0.6.8`, `ft-pandas-ta 0.3.16`, `technical 1.6.0`, `ccxt 4.5.52` |
| Python 3.14 | `nfi-x7-freqtrade:py314-pypi-2026.4` | `2026.4` | `pandas 3.0.2`, `numpy 2.4.4`, `pyarrow 24.0.0`, `TA-Lib 0.6.8`, `ft-pandas-ta 0.3.16`, `technical 1.6.0`, `ccxt 4.5.52` |

Common benchmark conditions:

```text
Host CPUs: 10
Docker CPUs: 10
Workers: 9
Pairs: 80
Rows per dataframe: 1200
Runmode: dry_run
Data source: local Binance candle data mounted read-only from freqtrade-nfi
```

## TestX7 Live-Style Analyze Result

| Runtime | Loops | Average | Min | Max | Over 5s | Gate |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Python 3.13.13 | 40 | `2.946143s` | `2.782652s` | `3.378742s` | 0 | PASS |
| Python 3.14.4 | 40 | `2.969508s` | `2.761902s` | `3.489651s` | 0 | PASS |

Interpretation:

- TestX7 works on Python 3.13 and still stays under the 5-second 80-pair gate.
- In this run, Python 3.14 was not faster than Python 3.13 in a meaningful way.
- The difference is small enough that it should be treated as benchmark noise unless repeated on more machines.

## Original X7 One-Loop Reference

Original X7 is much slower, so only one live-style analyze loop was measured per runtime.

| Runtime | Strategy | Loops | Time |
| --- | --- | ---: | ---: |
| Python 3.13.13 | `NostalgiaForInfinityX7` | 1 | `206.224397s` |
| Python 3.14.4 | `NostalgiaForInfinityX7` | 1 | `208.610913s` |

Interpretation:

- The original strategy remained around 206-209 seconds for one 80-pair live-style loop.
- Python runtime version does not explain the gap between original X7 and TestX7.
- The large speedup is from the TestX7 strategy-side changes, not from moving from Python 3.13 to 3.14.

## What This Proves

This local benchmark supports one narrow claim:

```text
TestX7 still shows the live-style analyze speedup on Python 3.13.
```

It does not support a claim that Python 3.14 is faster for this strategy workload. In this measurement, Python 3.13 and Python 3.14 were effectively the same, with Python 3.13 slightly ahead by a small margin.

## What This Does Not Prove

- It does not prove Python 3.13 is generally faster than Python 3.14.
- It does not prove the same timing on every VPS or Docker host.
- It does not prove backtesting is faster. Backtest speed still needs its own benchmark.
- It does not prove production live safety. Process lifecycle, fallback, worker limits, and long-running dry-run/live tests still matter.

## Evidence Files

| File | What it contains |
| --- | --- |
| `user_data/backtest_results/test_x7_python313_80pair_gate/testx7-live-loop-80pairs-40loops-workers9-20260512-001929.txt` | TestX7, Python 3.13, 80-pair, 40-loop gate |
| `user_data/backtest_results/test_x7_python314_pypi_80pair_gate/testx7-live-loop-80pairs-40loops-workers9-20260512-003515.txt` | TestX7, Python 3.14 PyPI image, 80-pair, 40-loop gate |
| `user_data/backtest_results/runtime_compare_20260512/original-x7-python313-80pairs-1loop.txt` | Original X7, Python 3.13, 80-pair, 1 loop |
| `user_data/backtest_results/runtime_compare_20260512/original-x7-python314-pypi-80pairs-1loop.txt` | Original X7, Python 3.14 PyPI image, 80-pair, 1 loop |

## Reproduce

Build the Python 3.13 runtime:

```bash
docker compose -f docker-compose.yml -f docker-compose.python313.yml build freqtrade
```

Run the Python 3.13 TestX7 gate:

```bash
TEST_X7_GATE_DATA_DIR_HOST=/path/to/user_data/data/binance \
  tools/test_x7/run_80pair_5s_gate_python313.sh
```

Build the matching PyPI-based Python 3.14 runtime:

```bash
docker compose -f docker-compose.yml -f docker-compose.python314-pypi.yml build freqtrade
```

Run the matching Python 3.14 TestX7 gate:

```bash
TEST_X7_COMPOSE_FILES=docker-compose.yml:docker-compose.python314-pypi.yml \
TEST_X7_GATE_DATA_DIR_HOST=/path/to/user_data/data/binance \
TEST_X7_GATE_OUTPUT_DIR=user_data/backtest_results/test_x7_python314_pypi_80pair_gate \
  tools/test_x7/run_80pair_5s_gate.sh
```

## Caveats

- This is a local WSL/Docker benchmark, not a live deployment test.
- Original X7 was measured with one loop only because each loop takes several minutes.
- The result should be repeated before making a general claim about Python 3.13 vs 3.14.
- Backtest speed is a separate question and still needs a dedicated benchmark.

---

# Python 3.13 vs 3.14 런타임 확인

관리자가 물어본 핵심은 이것이었습니다:

> TestX7 속도 개선이 Python 3.14 덕분인가, 아니면 전략 구조 최적화 덕분인가?

이번 로컬 측정 기준 결론은 명확합니다.

- TestX7는 Python 3.13에서도 80페어 40-loop를 모두 5초 안에 통과했습니다.
- Python 3.14가 이번 측정에서 확실히 더 빠르다고 볼 근거는 없었습니다.
- 원본 X7은 Python 3.13/3.14 모두 80페어 1-loop가 약 206-209초였습니다.
- 따라서 큰 속도 차이는 Python 버전이 아니라 TestX7의 전략 내부 구조 최적화에서 나온 것으로 보는 게 맞습니다.
- 이 결과는 backtest 속도 개선 증명이 아니며, production live 추천도 아닙니다.

짧게 말하면:

```text
Python 3.13에서도 TestX7 최적화 효과는 유지된다.
Python 3.14 자체가 이 결과의 주된 이유는 아니다.
```
