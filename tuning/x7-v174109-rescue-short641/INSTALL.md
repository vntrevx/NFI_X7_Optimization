# Direct Install Guide

This package has two layers:

- `configs/` and `docs/` are review material.
- `release/testx7-v174109-rescue-short641-install-20260523.tar.gz` is the
  installable bundle.

Use the release bundle if you want to load the checked `TestX7` v17.4.109
package in a Freqtrade user directory. Do not use the repository root
`user_data/strategies` folder for this package; the installable v17.4.109
strategy files are inside the release bundle.

## What The Bundle Contains

The bundle contains only `user_data` strategy/config files:

- `user_data/strategies/NostalgiaForInfinityX7.py`
- `user_data/strategies/TestX7.py`
- `user_data/strategies/test_x7_modules/*`
- `user_data/config-x7-futures3x-80pairs.example.json`
- `user_data/config-x7-futures3x-prodage-v2-risk-topmode-xplzen-v1-blockxpl142-zencap10-topmode-safeexpand-not142block-short641-tailblock-cap4-v1-no-fresh-top3-nousual-sui641block-h2tailfix-v3-maxopen4-blocklong44all-ondo63-v1.example.json`
- `user_data/config-test-x7-live-speed-safe.example.json`
- `user_data/config-x7-v174109-rescue-short641-paper-overlay.example.json`

It does not include exchange credentials, live bot state, database files, or
backtest archives.

## Install Safely

Run this in a clean test Freqtrade checkout first, not on a live bot.

```bash
curl -L \
  -o testx7-v174109-rescue-short641-install-20260523.tar.gz \
  https://raw.githubusercontent.com/vntrevx/NFI_X7_Optimization/main/tuning/x7-v174109-rescue-short641/release/testx7-v174109-rescue-short641-install-20260523.tar.gz

sha256sum testx7-v174109-rescue-short641-install-20260523.tar.gz
```

Expected sha256:

```text
c8803508f146254e1f553015f9ab37b20858004c120a8e6b749203c54382418a
```

Note: `evidence/local-status.json` records the sha256 of the original internal
transfer bundle used during local verification. This public install bundle is
sanitized to remove internal handoff notes, so it has the different sha256 shown
above.

Preview the files before extracting:

```bash
tar -tzf testx7-v174109-rescue-short641-install-20260523.tar.gz
```

Extract into a temporary preview directory:

```bash
mkdir -p /tmp/testx7-v174109-install-preview
tar -xzf testx7-v174109-rescue-short641-install-20260523.tar.gz \
  -C /tmp/testx7-v174109-install-preview
```

Then copy the previewed `user_data` tree into your Freqtrade checkout:

```bash
rsync -av /tmp/testx7-v174109-install-preview/user_data/ /path/to/freqtrade/user_data/
```

Replace `/path/to/freqtrade` with your own Freqtrade project path.

## Load Check

From your Freqtrade checkout, run a local Docker strategy-load check:

```bash
docker compose run --rm freqtrade list-strategies \
  --userdir /freqtrade/user_data \
  --config /freqtrade/user_data/config-x7-futures3x-80pairs.example.json \
  --config /freqtrade/user_data/config-x7-futures3x-prodage-v2-risk-topmode-xplzen-v1-blockxpl142-zencap10-topmode-safeexpand-not142block-short641-tailblock-cap4-v1-no-fresh-top3-nousual-sui641block-h2tailfix-v3-maxopen4-blocklong44all-ondo63-v1.example.json \
  --config /freqtrade/user_data/config-test-x7-live-speed-safe.example.json \
  --config /freqtrade/user_data/config-x7-v174109-rescue-short641-paper-overlay.example.json
```

`TestX7` should load. The expected strategy basis is:

```text
Test X7 based on v17.4.109
```

## Paper Mode Only First

The included overlay is a paper/tiny-canary surface:

- `dry_run=true`
- `dry_run_wallet=1000`
- `stake_amount=100`
- `max_open_trades=4`
- `trading_mode=futures`
- `margin_mode=isolated`
- `force_entry_enable=false`

Do not merge this into a live config without your own review, credentials kept
in a separate private config, and a fresh paper run.
