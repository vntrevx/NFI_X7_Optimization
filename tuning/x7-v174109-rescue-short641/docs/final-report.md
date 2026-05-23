# Final Local Report

## Verdict

`rescue-short641-paramkeys-v1` is the selected local TestX7 candidate from the
v17.4.109 rescue/tuning run.

It is locally verified for paper or tiny-canary preparation. It is not live
deployed and should not be treated as full-capital approved.

## Evidence Summary

- Production gate: `promotable=true`, `risk_level=low`, `failed_rules=[]`
- Full timerange profit: `+191.866939%`, `269` trades
- Fresh OOS profit: `+25.906538%`, `54` trades
- No-top3 fresh retention: `83.151154%`
- Default live-cost worst retention: `82.441272%`
- Speed gate: `PASS`, `80` pairs, `40` loops, max loop `3.882162s`
- Targeted verifier tests: `258`, `OK`
- Local Docker unittest discovery: `337`, `OK`

## Selected Operating Surface

- `strategy=TestX7`
- `dry_run=true`
- `dry_run_wallet=1000`
- `trading_mode=futures`
- `margin_mode=isolated`
- `stake_currency=USDT`
- `stake_amount=100`
- `max_open_trades=4`
- `tradable_balance_ratio=0.99`
- `initial_state=running`
- `force_entry_enable=false`
- `cancel_open_orders_on_exit=false`
- `bot_name=testx7-v174109-rescue-paper`
- `process_throttle_secs=5`
- static whitelist: `76` pairs

## Interpretation

The candidate is a stronger checked local candidate than the direct v17.4.109
refresh and the previous rank11 live-final lane in this local scorecard. It also
slightly outranks the old v17.4.96 final profile by the checked score.

That does not make it risk-free. Live execution quality, realized slippage,
funding drag, and latency still need paper or tiny-canary observation before any
larger deployment.
