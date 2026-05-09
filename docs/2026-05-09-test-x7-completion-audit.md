# TestX7 Completion Audit

Date: 2026-05-09 KST

## Objective Restatement

Finish the NFI latest-sync, Test X7 modularization/optimization, CPU/multicore
fact-check, parity verification, and local one-year backtest work. Do not claim
completion unless every explicit requirement is backed by concrete local
evidence.

## Audit Verdict

Complete.

Every explicit requirement has concrete local evidence.

After WSL/Docker exposed the configured 10 CPUs, the final 80-pair TestX7
profile passed the strict 5-second gate with `8` stable process workers.

The final default gate result is `40` loops, `avg=3.283842s`, `max=3.830582s`,
`over5=0/40`, `gate=PASS`.

## Prompt-To-Artifact Checklist

| Requirement | Evidence | Status | Notes |
| --- | --- | --- | --- |
| Update NFI to latest upstream | `external/NostalgiaForInfinity HEAD == origin/main == 75c223b0f1a76731f4555aeb70fd0c92df9f30ea` | Complete | Rechecked on 2026-05-09. |
| Sync latest X7 locally | SHA256 match: `external/NostalgiaForInfinity/NostalgiaForInfinityX7.py` == `user_data/strategies/NostalgiaForInfinityX7.py` == `26ac1698b58bf8356cf67ea9874ba0eaed95fbebad80fb630366b3f39c00994c` | Complete | X7 version is `v17.4.59`. |
| Preserve original X7 baseline | `user_data/strategies/NostalgiaForInfinityX7.py` is byte-identical to upstream | Complete | No TestX7 optimization code was put into the original baseline. |
| Create copied strategy named Test X7 | `user_data/strategies/TestX7.py`; class `TestX7`; `version()` reports `Test X7 based on ...` | Complete | Freqtrade strategy class/file has no space, display/report name uses `Test X7`. |
| Load original X7 and TestX7 together | `docker compose run --rm freqtrade list-strategies --userdir /freqtrade/user_data` shows `NostalgiaForInfinityX7 OK` and `TestX7 OK` | Complete | Rechecked after latest docs/tooling changes. |
| Fact-check Freqtrade strategy/class behavior | `docs/2026-05-08-test-x7-fact-check.md` | Complete | One configured strategy class is used; multiple strategy files do not mix decisions. |
| Fact-check pair analysis sequential behavior | `docs/2026-05-08-test-x7-fact-check.md`; Freqtrade `IStrategy.analyze(pairs)` source inspection | Complete | Core pair loop is sequential in Freqtrade `2026.4`; TestX7 parallelizes inside strategy boundary for live/dry-run. |
| Modularize TestX7 | `user_data/strategies/TestX7.py`; `user_data/strategies/test_x7_modules/` | Complete | Entrypoint is thin; modules split indicator, entry, cache, merge, CPU, profiling, parity, and parallel analyze surfaces. |
| Preserve trading logic | `user_data/backtest_results/test_x7_v17459_final_5s_1y_required/compare.json`; `user_data/backtest_results/test_x7_v17459_80_1y/compare.json` | Complete | Both compare files have `trade_surface_equal=true` and `first_difference=null`. |
| Verify no hardcoded trade outputs | Strategy code contains no embedded trade result tables; parity uses real backtest artifacts | Complete | Worker prewarm discards results; it does not hardcode pair decisions. |
| Profile calculation bottlenecks | `docs/2026-05-09-test-x7-final-5s-report.md`; `docs/2026-05-09-test-x7-80pairs-local-report.md` | Complete | Main stages measured: `populate_indicators`, `populate_entry_trend`, worker timing, and rejected tuning candidates. |
| Fact-check CPU/core behavior | `nproc=10`; Docker `nproc=10`; `.wslconfig processors=10` | Complete | Final worker choice was measured after the configured CPU allocation became active. |
| Apply safe optimization | `test_x7_modules/` modules plus `user_data/config-test-x7-live-speed-safe.example.json` | Complete | Safe config uses 8 stable process workers, caches, short-side skips for spot, numeric thread limiting, and bounded result tails. |
| Create 80-pair configs | `user_data/config-test-x7-80pairs.example.json`; `user_data/config-original-x7-80pairs.example.json` | Complete | Used for 80-pair original/TestX7 parity and speed comparisons. |
| Local one-year backtest | 58-pair artifacts in `test_x7_v17459_final_5s_1y_required`; 80-pair artifacts in `test_x7_v17459_80_1y` | Complete | Both original/TestX7 comparisons pass parity. |
| Report one-year profit and risk metrics | `docs/2026-05-09-test-x7-final-5s-report.md`; `docs/2026-05-09-test-x7-80pairs-local-report.md` | Complete | Includes profit, trades, winrate, profit factor, max drawdown, best/worst pair. |
| Prove 58-pair 5-second gate | `user_data/backtest_results/test_x7_v17459_final_5s_1y_required/testx7-live-loop-58pairs-40loops-w4-tuned.txt` | Complete | 40 loops, min `3.345851s`, avg `3.776724s`, max `4.351102s`, over5 `0/40`. |
| Prove 80-pair speedup | `user_data/backtest_results/test_x7_v17459_80_1y/original-live-loop-80pairs-3loops.txt`; `testx7-live-loop-80pairs-40loops-workers8-20260509-182558.txt` | Complete | Original avg `238.833s`; TestX7 final avg `3.283842s`; about 72.7x faster; over5 `0/40`. |
| Prove 80-pair strict 5-second gate | `tools/test_x7/run_80pair_5s_gate.sh`; `testx7-live-loop-80pairs-40loops-workers8-20260509-182558.txt` | Complete | Final default gate file contains `gate=PASS`. |
| Provide repeatable post-restart gate | `tools/test_x7/run_80pair_5s_gate.sh` | Complete as tooling | Script prints CPU counts, chooses Docker CPU count minus two when Docker exposes at least 8 CPUs, runs 80-pair 40-loop gate, stores output, and exits non-zero on any loop over 5s. |
| Do not deploy to laptop live server | No laptop deploy/start/stop commands used for this TestX7 rollout | Complete | Work remains local. |
| Do not modify Freqtrade core | Changes are under local strategy/docs/tools/configs only | Complete | Freqtrade core not patched. |
| Do not claim future profit | Reports explicitly state backtest is not future profit guarantee | Complete | Trading risk caveat included. |

## Final Gate Evidence

Current CPU state:

```text
host nproc: 10
docker nproc: 10
/mnt/c/Users/0/.wslconfig:
[wsl2]
memory=26GB
processors=10
swap=32GB
localhostForwarding=true
```

Final accepted 80-pair safe config result:

```text
TestX7 80-pair safe config, 8 workers, 40 loops:
min=3.051825s
avg=3.283842s
max=3.830582s
over5=0/40
gate=PASS
```

Rejected 10-worker check:

```text
10 workers, 40 loops:
min=2.748103s
avg=3.900492s
max=7.591558s
over5=6/40
gate=FAIL
```

Closest rejected 4-vCPU tuning candidate:

```text
base=300, entry=6, 15m=64, 1h=200, 4h=200, 1d=40
40 loops:
min=4.663566s
avg=5.030852s
max=5.818261s
over5=16/40
```

Rejected low-worker check:

```text
3 workers with current safe config:
12 loops:
min=6.035240s
avg=6.456431s
max=6.877022s
over5=12/12
```

Rejected code prototype:

```text
Precomputed long-shift prototype with indicator tail 6:
avg=5.134s
max=6.063s
over5=27/40
```

The prototype was reverted because it worsened the 40-loop gate.

## Completion Command

```bash
tools/test_x7/run_80pair_5s_gate.sh
```

This command now defaults to `8` workers on the current 10-CPU Docker runtime
and prints `gate=PASS`.
