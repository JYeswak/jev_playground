#!/usr/bin/env python3
"""A12 local-refusal prototype scorer. Frozen rule R from
docs/demos/upstream-repro/a12-refusal-falsifier-20260920.md.
Read-only on the locked export; no store access.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ABSENCE = re.compile(
    r"no such|missing|does not exist|undefined|requireKey|no .* field|absent", re.I
)
ERROR_LIT = re.compile(
    r"error|traceback|no such|undefined|is not|null|missing|column", re.I
)
STOP = {
    "such",
    "field",
    "does",
    "exist",
    "what",
    "where",
    "with",
    "from",
    "that",
    "this",
    "have",
    "been",
    "there",
    "their",
    "key",
}
TOKEN = re.compile(r"[a-z0-9]{4,}")


def eligible(snippet: str, query: str) -> bool:
    toks = [t for t in TOKEN.findall(query.lower()) if t not in STOP]
    spans = [m.span() for m in ERROR_LIT.finditer(snippet)]
    ticked = [m.span() for m in re.finditer(r"`[^`]*`", snippet)]
    zones = spans + [(a - 40, b + 40) for a, b in ticked]
    low = snippet.lower()
    for t in toks:
        for i in [m.start() for m in re.finditer(re.escape(t), low)]:
            if any(a <= i <= b for a, b in zones):
                return True
    return False


def loss(y: int, dig: bool) -> int:
    if dig:
        return 2 if y == 0 else 0
    return 1 if y == 1 else 0


def main(rows_path: str, hits_path: str) -> int:
    rows = [
        json.loads(l) for l in Path(rows_path).read_text().splitlines() if l.strip()
    ]
    hits: dict[str, dict] = {}
    for l in Path(hits_path).read_text().splitlines():
        if l.strip():
            h = json.loads(l)
            hits.setdefault(h["source_path"], h)
    out: dict = {"n": len(rows)}
    refused_empty = refused_y1 = kept_y1 = 0
    r_loss_num = r_loss_den = 0
    dig_loss_num = 0
    ws_rows = [r for r in rows if ABSENCE.search(r["query"])]
    for r in rows:
        yol = r["y"]
        base_dig = r["hit_count"] > 0
        refuse = (
            base_dig
            and ABSENCE.search(r["query"] or "")
            and not eligible(
                hits.get(r["top_path"] or "", {}).get("snippet", ""), r["query"]
            )
        )
        dig = base_dig and not refuse
        if refuse and yol == 0 and base_dig:
            refused_empty += 1
        if refuse and yol == 1:
            refused_y1 += 1
        if not refuse and yol == 1 and base_dig:
            kept_y1 += 1
        if r in ws_rows or ABSENCE.search(r["query"] or ""):
            r_loss_num += loss(yol, dig)
            r_loss_den += 1
            dig_loss_num += loss(yol, base_dig)
    out["refused_empty_of_4"] = refused_empty
    out["refused_y1"] = refused_y1
    out["kept_y1_digs"] = kept_y1
    out["S_absence_shape"] = {
        "n": r_loss_den,
        "R_loss": round(r_loss_num / r_loss_den, 9),
        "dig_iff_loss": round(dig_loss_num / r_loss_den, 9),
    }
    if refused_y1 >= refused_empty:
        out["verdict"] = "REFUSE"
        out["why"] = "F1: refused-Y1 >= refused-empty"
    elif refused_empty == 0:
        out["verdict"] = "REFUSE"
        out["why"] = "F2: toothless, 0 of 4 empties refused"
    elif out["S_absence_shape"]["R_loss"] >= out["S_absence_shape"]["dig_iff_loss"]:
        out["verdict"] = "REFUSE"
        out["why"] = "F3: no gain on absence slice"
    else:
        out["verdict"] = "HELD"
        out["why"] = (
            "passes F1-F3 but post-hoc authored; "
            "fresh confirmation blocked (cass search down)"
        )
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
