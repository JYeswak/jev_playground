#!/usr/bin/env python3
"""Recompute R142 (msax retry-worthiness V1 Noul + V2 Choice) from committed rows."""

import json
from pathlib import Path

D = Path(__file__).resolve().parent
rows = [json.loads(l) for l in (D / "retry-rows.jsonl").open() if l.strip()]
print("rows:", len(rows))
v1 = [r for r in rows if r.get("v1_ok") and isinstance(r.get("v1_noul"), (int, float))]
pos = [r["v1_noul"] for r in v1 if r["label"] == 1]
neg = [r["v1_noul"] for r in v1 if r["label"] == 0]
conc = sum(1 for a in pos for b in neg if a > b)
ties = sum(1 for a in pos for b in neg if a == b)
print("V1 n:", len(v1), "AUC:", round((conc + 0.5 * ties) / (len(pos) * len(neg)), 3))
acc1 = sum(1 for r in v1 if (r["v1_noul"] >= 0.5) == bool(r["label"])) / len(v1)
print("V1 acc@0.5:", round(acc1, 3))
v2 = [r for r in rows if r.get("v2_ok")]
acc2 = sum(
    1 for r in v2 if (r["v2_choice"] == "retry_identical") == bool(r["label"])
) / len(v2)
print("V2 n:", len(v2), "acc:", round(acc2, 3))
