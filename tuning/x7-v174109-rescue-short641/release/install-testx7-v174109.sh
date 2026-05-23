#!/usr/bin/env bash
set -euo pipefail

BUNDLE_URL="${TESTX7_BUNDLE_URL:-https://raw.githubusercontent.com/vntrevx/NFI_X7_Optimization/main/tuning/x7-v174109-rescue-short641/release/testx7-v174109-rescue-short641-install-20260523.tar.gz}"
EXPECTED_SHA="${TESTX7_EXPECTED_SHA:-c8803508f146254e1f553015f9ab37b20858004c120a8e6b749203c54382418a}"

usage() {
  cat <<'USAGE'
Usage:
  ./install-testx7-v174109.sh /path/to/freqtrade

This installs the sanitized TestX7 v17.4.109 user_data files into a local
Freqtrade checkout. Run it on a test/paper checkout first, not a live bot.
USAGE
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" || "$#" -ne 1 ]]; then
  usage
  exit 1
fi

TARGET_ROOT="${1%/}"
TARGET_USER_DATA="$TARGET_ROOT/user_data"

if [[ ! -d "$TARGET_ROOT" ]]; then
  echo "Target Freqtrade path does not exist: $TARGET_ROOT" >&2
  exit 1
fi

if [[ ! -d "$TARGET_USER_DATA" ]]; then
  echo "Target does not look like a Freqtrade checkout. Missing: $TARGET_USER_DATA" >&2
  exit 1
fi

command -v curl >/dev/null || { echo "curl is required" >&2; exit 1; }
command -v sha256sum >/dev/null || { echo "sha256sum is required" >&2; exit 1; }
command -v tar >/dev/null || { echo "tar is required" >&2; exit 1; }
command -v rsync >/dev/null || { echo "rsync is required" >&2; exit 1; }

TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

ARCHIVE="$TMPDIR/testx7-v174109-rescue-short641-install-20260523.tar.gz"

echo "Downloading TestX7 v17.4.109 install bundle..."
curl -fsSL -o "$ARCHIVE" "$BUNDLE_URL"

ACTUAL_SHA="$(sha256sum "$ARCHIVE" | awk '{print $1}')"
if [[ "$ACTUAL_SHA" != "$EXPECTED_SHA" ]]; then
  echo "SHA mismatch." >&2
  echo "Expected: $EXPECTED_SHA" >&2
  echo "Actual:   $ACTUAL_SHA" >&2
  exit 1
fi

tar -xzf "$ARCHIVE" -C "$TMPDIR"

BACKUP_DIR="$TARGET_USER_DATA/testx7-v174109-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

rsync -a --backup --backup-dir="$BACKUP_DIR" "$TMPDIR/user_data/" "$TARGET_USER_DATA/"

echo
echo "Installed TestX7 v17.4.109 files into:"
echo "  $TARGET_USER_DATA"
echo
echo "Overwritten files, if any, were backed up under:"
echo "  $BACKUP_DIR"
echo
echo "Next load-check command:"
cat <<'NEXT'
cd /path/to/freqtrade
CANDIDATE="$(basename "$(ls user_data/config-x7-futures3x-prodage-v2-risk-topmode-*.example.json | head -n 1)")"
docker compose run --rm freqtrade list-strategies \
  --userdir /freqtrade/user_data \
  --config /freqtrade/user_data/config-x7-futures3x-80pairs.example.json \
  --config "/freqtrade/user_data/$CANDIDATE" \
  --config /freqtrade/user_data/config-test-x7-live-speed-safe.example.json \
  --config /freqtrade/user_data/config-x7-v174109-rescue-short641-paper-overlay.example.json
NEXT
echo
echo "Replace /path/to/freqtrade with: $TARGET_ROOT"
echo "Use paper/dry-run first. Do not attach this directly to a live bot."
