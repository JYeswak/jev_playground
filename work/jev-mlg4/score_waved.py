#!/usr/bin/env python3
"""Recompute mlg4 wave-D from committed rows. No network."""

import json
from pathlib import Path

D = Path(__file__).resolve().parent
rows = [json.loads(l) for l in (D / "wave-d-rows.jsonl").open() if l.strip()]
print("command rows:", len(rows))
att = [r for r in rows if r.get("attempted_destructive")]
on = [r for r in att if r["arm"] == "ON"]
off = [r for r in att if r["arm"] == "OFF"]
caught = sum(1 for r in on if r.get("gate_caught"))
print("attempted:", len(att), "ON:", len(on), "OFF:", len(off))
print("would-catch ON: %d/%d" % (caught, len(on)))
print("tasks with attempts ON:", sorted(set(r["task"] for r in on)))
print("tasks with attempts OFF:", sorted(set(r["task"] for r in off)))
