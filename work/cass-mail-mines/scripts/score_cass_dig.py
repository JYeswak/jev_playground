#!/usr/bin/env python3
"""Dig-vs-invent on cass --robot hits.

Each row: query, hits[], y_dig (1 if at least one hit is independently useful).
Choice: {dig, invent/__none__}. invent≡abstain on positive dig.
Loss: dig on y=0 → 2; invent on y=1 → 1; else 0.

Cheap baseline: dig iff count>0 (empty-success refusal is the RED plant).

    python3 work/cass-mail-mines/scripts/score_cass_dig.py \
      work/cass-mail-mines/exports/cass-dig-rows.jsonl
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def load(path: Path) -> list[dict]:
    rows = []
    for i, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip() or line.startswith("#"):
            continue
        r = json.loads(line)
        if "y" not in r:
            raise SystemExit(f"{path}:{i} missing y")
        rows.append(r)
    if len(rows) < 100:
        raise SystemExit(f"REFUSE: n={len(rows)} < 100")
    return rows


def loss(y: int, pick: str) -> int:
    if pick == "invent":
        return 1 if y == 1 else 0
    if pick == "dig":
        return 0 if y == 1 else 2
    raise SystemExit(pick)


def mean(rows, pick_of) -> float:
    return sum(loss(int(r["y"]), pick_of(r)) for r in rows) / len(rows)


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__, file=sys.stderr)
        return 2
    path = Path(argv[0])
    if not path.is_file():
        print(f"MISSING_EXPORT {path}", file=sys.stderr)
        return 2
    rows = load(path)
    n = len(rows)
    pos = sum(1 for r in rows if int(r["y"]) == 1)
    c_abs = mean(rows, lambda r: "invent")  # always invent = always-abstain
    c_hit = mean(rows, lambda r: "dig" if int(r.get("hit_count") or 0) > 0 else "invent")
    vs = "BEAT" if c_hit < c_abs else "LOSE"
    print(f"MINE cass-dig-vs-invent  store=cass  n={n}  y_dig={pos}  prevalence={pos/n:.9f}")
    print(f"CONTROL always-invent            mean_loss={c_abs:.9f}")
    print(f"BASELINE dig-iff-count>0         mean_loss={c_hit:.9f}  vs_control={vs}")
    print("NO-CLAIM  [pending] promoted=0  Y must be independent of count>0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
