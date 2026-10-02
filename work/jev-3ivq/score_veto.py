#!/usr/bin/env python3
"""Recompute R149 veto (Choice+verify) from committed rows. No network."""

import json
from pathlib import Path

D = Path(__file__).resolve().parent
rows = [json.loads(l) for l in (D / "veto-rows.jsonl").open() if l.strip()]
ok = [r for r in rows if r.get("ok")]
print("rows:", len(rows), "ok:", len(ok))
tp = sum(1 for r in ok if r["veto"] == 1 and r["label"] == 1)
fp = sum(1 for r in ok if r["veto"] == 1 and r["label"] == 0)
print("recall: %d/17" % tp, "false-veto: %d/60" % fp)
print("precision:", round(tp / (tp + fp), 3) if tp + fp else "na")
