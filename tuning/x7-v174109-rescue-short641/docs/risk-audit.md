# Risk Audit

## Verdict

The selected candidate passes the local production gate, but it is not
risk-free. The main remaining risks are execution-cost/funding stress, thin
fresh monthly sampling, and long-duration multi-entry tail exposure.

## Passed Checks

- Promotion gate passed: `promotable=true`
- Risk level: `low`
- Failed rules: `[]`
- No-top3 retention: `83.151154%`
- Default live-cost retention: `82.441272%`
- 80-pair speed gate: `PASS`

## Material Residual Risks

| Risk | Status | Practical Meaning |
| --- | --- | --- |
| Parameter overfit | Checked, low by current gates | Future regime drift can still invalidate the result |
| Pair concentration | Acceptable by checked no-top3 gate | Top3 removal still leaves positive result above the retention floor |
| Execution cost | Material residual risk | Default cost passes; elevated and extreme cost stress fail |
| Funding drag | Material residual risk | Worse funding assumptions compress the fresh OOS edge quickly |
| Tail duration | Residual risk | Some trades can last weeks and use multiple entries |
| Monthly robustness | Partial risk | March 2026 had only `2` fresh trades |
| Speed | Checked pass | Local benchmark no longer shows a speed blocker |

## Live/Paper Caveat

This package is not live-proven. The next meaningful validation step is a small
paper or tiny-canary run with realized slippage, funding, and latency tracking.
