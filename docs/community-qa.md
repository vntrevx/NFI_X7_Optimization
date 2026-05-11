# TestX7 Community Q&A

Short answers for common Discord/community questions.

The main rule: do not overclaim. `TestX7` is a local proof package, not an
official NFI feature and not a production recommendation.

## Short Status

```text
TestX7 is a local performance proof package.

It targets the live-style analyze(pairs) path of NFI X7.
It does not intentionally change entries, exits, DCA, grind, leverage, or
position logic.

It is not official, not production-ready, and not a profit claim.
```

## Can It Be Applied To Live Trading?

Short answer:

```text
In principle, yes. The optimization targets the live-style analyze(pairs)
path, which is part of the live/dry-run analysis flow.

But I would not call it a production drop-in yet.
It still needs maintainer review, more dry-run/live observation, worker-limit
configuration, and testing on the next NFI version.
```

More careful answer:

```text
The idea is meant for the live analysis path, but the current repo is still a
proof package.

So far it has been validated with local live-style loop benchmarks and
backtest parity checks, not long real live trading.

Dry-run testing is the correct next step before anyone considers live use.
```

## Has Anyone Tested It On Live Or Dry-Run?

```text
Not yet from my side.

So far I tested:
- local live-style analyze(pairs) loop
- local backtest parity vs original X7
- local 80-pair speed gate

A community user also tested a local backtest and got matching results with a
faster runtime.

But I have not personally run TestX7 on real live trading or long dry-run yet.
For now it should still be treated as a proof package.
```

## Does It Change Trading Logic?

```text
No intentional trading-logic changes.

Entries, exits, DCA, grind, leverage, position adjustment, and signal tags are
intended to stay unchanged.

The checked one-year backtest trade surface matched original X7:
trade_surface_equal=true
first_difference=null
```

Plain version:

```text
The goal is not to make more profit by changing signals.
The goal is to calculate the same checked decisions much faster.
```

## What Was The Local Speed Result?

```text
Local 80-pair live-style analyze loop:

Original X7:
- avg 238.833499s
- max 242.990876s

TestX7:
- avg 3.340671s
- max 4.221486s
- 40/40 loops under 5s

Measured average speedup: about 71.5x
```

## Does It Speed Up Backtesting Too?

Careful answer:

```text
The strongest measured proof is still the live-style analyze(pairs) path.

There is also one external community backtest report showing a faster runtime
with matching results:

Original X7: 214s
TestX7: 137s
About 36% faster
Result surface matched

That is a useful signal, but not enough to claim global backtest speedup yet.
Backtest speed needs separate controlled profiling.
```

## How Many Workers / Threads Should Be Used?

```text
It depends on the machine.

Too many workers can make performance worse, especially on small VPS machines.

The long-term direction should be user configurable:
- auto = conservative CPU-based selection
- 1 = sequential / disabled
- N = user-defined worker limit
```

Local proof result:

```text
On the final local test machine, Docker exposed 10 CPUs.
9 workers passed the 5-second gate.
10 workers and 8 workers both showed worse max-loop spikes in testing.

That does not mean 9 is right for every machine.
```

## Does It Fix Market Data Fetch Timeouts?

```text
No, not directly.

It does not fix exchange/network fetch timeouts.

It targets CPU-bound strategy analysis delay. If the bot is delayed because
pair analysis takes too long after fresh candles arrive, using more CPU cores
and caching repeated work can reduce the Strategy analysis took ... delay.
```

## Can A Small VPS Use It?

```text
Maybe, but only carefully.

Small VPS machines need conservative worker limits.
If the VPS does not have CPU/RAM to spare, too many workers can hurt more than
help.

That is why worker/thread limits should be configurable before this is treated
as a real user-facing feature.
```

## What Should Testers Share?

If someone tests `TestX7`, ask for:

```text
- machine / CPU / RAM
- Docker CPU limit or visible CPU count
- OS / Docker environment
- exchange and trading mode
- spot or futures
- pairlist and effective pair count
- timerange
- exact command
- worker settings / env vars
- original X7 runtime
- TestX7 runtime
- whether result surface matched
- exported backtest summary if available
```

## Suggested Safe Test Order

```text
1. Confirm both strategies load.
2. Run a short backtest comparison.
3. Check trade-surface parity.
4. Run a longer backtest comparison.
5. Try dry-run observation.
6. Only consider real live testing after maintainer review and more hardening.
```

## Common Community Questions

### Is TestX7 Live-Ready?

```text
Not live-ready yet.

It is a local proof package. The optimization targets the live-style analysis
path, but it still needs maintainer review, dry-run testing, worker limits, and
more validation before anyone should treat it as production-ready.
```

### Should I Use TestX7?

```text
I would not recommend it as a production replacement yet.

If you want to test it, start with backtesting or dry-run only, compare against
original X7, and verify that the trade surface matches.
```

### What Should I Share If I Test It?

```text
Thanks, that is useful.

Could you also share the machine, pairlist/effective pair count, timerange,
command, worker settings, original runtime, TestX7 runtime, and whether the
result surface matched?
```

### Does It Use More CPU?

```text
Yes, that is the idea for the analysis bottleneck.

It tries to use more available CPU cores instead of leaving pair analysis stuck
mostly on one core. But worker count must be configurable because small VPS
machines can get worse if too many workers are used.
```

## Bottom Line

```text
Promising proof package.
Not official.
Not production-ready.
Not a profit claim.
Needs more testing, dry-run observation, maintainer review, and clean upstream
splitting.
```
