#!/usr/bin/env python3
"""Recompute diffrisk dev (Noul suite-failure) from committed rows."""

import json
from pathlib import Path

D = Path(__file__).resolve().parent
rows = [json.loads(l) for l in (D / "diffrisk-rows.jsonl").open() if l.strip()]
ok = [r for r in rows if r.get("ok") and isinstance(r.get("noul"), (int, float))]
pos = [r["noul"] for r in ok if r["label"] == 1]
neg = [r["noul"] for r in ok if r["label"] == 0]
conc = sum(1 for a in pos for b in neg if a > b)
ties = sum(1 for a in pos for b in neg if a == b)
print("dev n:", len(ok), "AUC:", round((conc + 0.5 * ties) / (len(pos) * len(neg)), 3))
