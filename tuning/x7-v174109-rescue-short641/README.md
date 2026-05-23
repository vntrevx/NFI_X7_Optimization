# TestX7 v17.4.109 Rescue Short641 Tuning Package

This folder is a public research package for a local TestX7 tuning run based on
`NostalgiaForInfinityX7` `v17.4.109`.

It is not an upstream replacement, not a merge request, and not financial
advice. The goal is to preserve the experiment in a reviewable form: candidate
selection, local verification evidence, speed-gate notes, and remaining risk.

## Summary

- Selected local candidate: `rescue-short641-paramkeys-v1`
- Upstream basis: `NostalgiaForInfinityX7` `v17.4.109`
- Status: locally verified, not live deployed
- Intended next stage: paper or tiny-canary observation
- Full-capital live approval: no

## Checked Results

| Area | Result |
| --- | --- |
| Production gate | `promotable=true`, `risk_level=low`, `failed_rules=[]` |
| Full timerange | `+191.866939%`, `269` trades |
| Fresh OOS | `+25.906538%`, `54` trades |
| No-top3 retention | `83.151154%` |
| Default live-cost retention | `82.441272%` |
| 80-pair speed gate | `PASS`, max loop `3.882162s`, over-5s loops `0` |
| Targeted verifier tests | `258`, `OK` |
| Local Docker full unittest discovery | `337`, `OK` |

## Important Boundary

The local baseline used for this package is based on upstream X7 `v17.4.109`,
but the local baseline file was not byte-identical to upstream. The checked local
baseline had `short_entry_condition_641_enable` and
`short_entry_condition_642_enable` explicitly set to `False`, while upstream
keeps those two example lines commented.

That boundary is documented in `docs/upstream-baseline-note.md`.

## Folder Contents

- `configs/candidate-config.example.json` - selected candidate config
- `configs/paper-overlay.example.json` - fixed paper/tiny-canary overlay
- `docs/final-report.md` - public final summary
- `docs/risk-audit.md` - residual risk summary
- `docs/effectiveness-retrospective.md` - what the tuning work improved
- `docs/upstream-baseline-note.md` - upstream version and local-diff note
- `evidence/local-status.json` - machine-readable local status snapshot

## Reproducibility Notes

The original local verifier command was:

```bash
tools/x7_tuning/verify_v174109_full_local.sh
```

The original local status command was:

```bash
python3 tools/x7_tuning/show_v174109_local_status.py
```

Those commands were run in the local tuning workspace where the full strategy,
test, and backtest evidence tree existed. This public package preserves the
reviewable summary and selected configs, not the entire large experimental
workspace.
