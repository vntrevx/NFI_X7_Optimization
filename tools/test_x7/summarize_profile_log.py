#!/usr/bin/env python3
"""Summarize TestX7 profile lines from a Freqtrade log file."""

from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import re


PROFILE_RE = re.compile(r"TestX7 profile stage=(?P<stage>\S+) pair=(?P<pair>.+?) seconds=(?P<seconds>[0-9.]+)")


def main() -> int:
  parser = argparse.ArgumentParser()
  parser.add_argument("logfile", type=Path)
  parser.add_argument("--json", action="store_true")
  args = parser.parse_args()

  rows = defaultdict(lambda: {"count": 0, "total_seconds": 0.0, "max_seconds": 0.0, "max_pair": ""})
  for line in args.logfile.read_text(encoding="utf-8", errors="ignore").splitlines():
    match = PROFILE_RE.search(line)
    if not match:
      continue
    stage = match.group("stage")
    pair = match.group("pair")
    seconds = float(match.group("seconds"))
    row = rows[stage]
    row["count"] += 1
    row["total_seconds"] += seconds
    if seconds > row["max_seconds"]:
      row["max_seconds"] = seconds
      row["max_pair"] = pair

  summary = []
  for stage, row in rows.items():
    count = row["count"] or 1
    summary.append(
      {
        "stage": stage,
        "count": row["count"],
        "total_seconds": round(row["total_seconds"], 6),
        "avg_seconds": round(row["total_seconds"] / count, 6),
        "max_seconds": round(row["max_seconds"], 6),
        "max_pair": row["max_pair"],
      }
    )
  summary.sort(key=lambda item: item["total_seconds"], reverse=True)

  if args.json:
    print(json.dumps(summary, indent=2, sort_keys=True))
  else:
    for row in summary:
      print(
        f"{row['stage']}: count={row['count']} total={row['total_seconds']:.3f}s "
        f"avg={row['avg_seconds']:.3f}s max={row['max_seconds']:.3f}s pair={row['max_pair']}"
      )
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
