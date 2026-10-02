#!/usr/bin/env python3
"""Recompute m94x blind-label verdict from committed labels. No network."""

import json
from pathlib import Path

D = Path(__file__).resolve().parent
raw = (D / "m94x-labels.json").read_text().strip()
rows = (
    json.loads(raw)
    if raw.startswith("[")
    else [json.loads(l) for l in raw.splitlines() if l.strip()]
)
print("labelled:", len(rows))
tp = sum(1 for r in rows if r["pred_flag"] == 1 and r["truth_vendored"] == 1)
fp = sum(1 for r in rows if r["pred_flag"] == 1 and r["truth_vendored"] == 0)
pos = sum(1 for r in rows if r["truth_vendored"] == 1)
print("precision: %d/%d" % (tp, tp + fp) if tp + fp else "precision: na (0 flags)")
print("miss:", "undefined (%d positives)" % pos if pos == 0 else "check")
