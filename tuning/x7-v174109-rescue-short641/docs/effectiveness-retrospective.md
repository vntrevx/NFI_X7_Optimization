# Work Effectiveness Retrospective

## Verdict

The tuning run was effective for the local engineering objective.

It did not prove live profitability. It did convert a broad, uncertain tuning
state into a selected local candidate with documented checks, speed evidence,
transfer readiness notes, and residual-risk boundaries.

## What Improved

### Candidate Selection

The final selected local candidate is `rescue-short641-paramkeys-v1`.

By the local readiness scorecard:

| Candidate | Promotable | Fresh Profit | Fresh Trades | No-Top3 Retention | Score |
| --- | --- | ---: | ---: | ---: | ---: |
| `v174109-rescue-short641-paramkeys` | yes | `+25.906538%` | `54` | `83.151154%` | `21.541585` |
| `old-final-v17496` | yes | `+24.760469%` | `52` | `82.371284%` | `20.395516` |
| `v174109-refresh` | no | `+19.951384%` | `43` | `78.122056%` | `13.404331` |
| `rank11-live-final` | no | `+7.967678%` | `15` | `33.535646%` | `0.161938` |

### Speed

Before the entry-mask cache patch:

- average loop: `4.539307s`
- max loop: `6.369433s`
- loops over `5s`: `10`

After the patch:

- average loop: `2.924533s`
- max loop: `3.882162s`
- loops over `5s`: `0`
- gate: `PASS`

That changed speed from a known blocker into a passing local gate.

### Verification

The final local verification surface included:

- targeted raw-Python verifier tests: `258`, `OK`
- local Freqtrade Docker full unittest discovery: `337`, `OK`
- no-touch verifier: `files=8/8`
- status snapshot: `ok=true`
- local Docker runtime: `strategy=TestX7`, `freqtrade=2026.4`,
  `show_config=OK`

## What Was Not Proven

- live execution profitability
- realized slippage/funding on an actual bot
- paper or tiny-canary stability
- full-capital readiness
