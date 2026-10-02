#!/usr/bin/env python3
"""Recompute testrerun lever verdict from committed rows. No network."""

import json
from pathlib import Path

D = Path(__file__).resolve().parent
rows = [json.loads(l) for l in (D / "testrerun-rows.jsonl").open() if l.strip()]
print("rows:", len(rows))
skippable = [r for r in rows if r["first_err"] is False]
wasted = sum(1 for r in skippable if r["second_err"] is False)
hidden = sum(1 for r in skippable if r["second_err"] is True)
print(
    "skippable (prev passed):",
    len(skippable),
    "wasted:",
    wasted,
    "would-hide-failures:",
    hidden,
)
print("skip precision:", round(wasted / len(skippable), 3) if skippable else "na")
