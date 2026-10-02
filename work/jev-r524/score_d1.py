#!/usr/bin/env python3
"""Recompute R147 (D1 next-tool) from committed rows. No network, no key."""

import json
from collections import Counter
from pathlib import Path

D = Path(__file__).resolve().parent
rows = [json.loads(l) for l in (D / "d1-rows.jsonl").open() if l.strip()]
ok = [r for r in rows if r.get("ok")]
print("rows:", len(rows), "ok:", len(ok))
acc = sum(1 for r in ok if r["choice"] == r["label"]) / len(ok)
print("accuracy:", round(acc, 3))
print(Counter((r["choice"], r["label"]) for r in ok).most_common(6))
gated = [r for r in ok if isinstance(r.get("conf"), (int, float))]
gated.sort(key=lambda r: -r["conf"])
top = gated[: len(gated) // 4]
print(
    "top-quartile-conf acc:",
    round(sum(1 for r in top if r["choice"] == r["label"]) / len(top), 3),
)
