#!/usr/bin/env python3
"""Dig-vs-invent on cass --robot (or sqlite-fallback) rows.

Each row: query, hit_count, y (mechanical — see cass_dig_y.py).
Choice: {dig, invent}. invent ≡ always-abstain on dig-vs-invent.
Loss: dig on y=0 → 2; invent on y=1 → 1; else 0.

Controls / baselines:
  always-invent          (always-abstain)
  dig-iff-count>0        (empty-success RED when y=0 & count>0)
  dig-iff-top-score>0    (cheap BM25/rank: dig when ranker returned a scored hit)
  always-first-hit       (same as dig-iff-count>0 when hits exist)

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
    empty_success = sum(
        1 for r in rows if int(r.get("hit_count") or 0) > 0 and int(r["y"]) == 0
    )
    c_abs = mean(rows, lambda r: "invent")
    c_hit = mean(
        rows, lambda r: "dig" if int(r.get("hit_count") or 0) > 0 else "invent"
    )
    c_score = mean(
        rows,
        lambda r: "dig"
        if (r.get("top_score") not in (None, "", 0, "0") and int(r.get("hit_count") or 0) > 0)
        or (int(r.get("hit_count") or 0) > 0 and r.get("top_path"))
        else "invent",
    )
    vs_hit = "BEAT" if c_hit < c_abs else "LOSE"
    vs_score = "BEAT" if c_score < c_abs else "LOSE"
    print(f"MINE cass-dig-vs-invent  store=cass  n={n}  y_dig={pos}  prevalence={pos/n:.9f}")
    print(f"  empty_success_rows (count>0 & y=0) = {empty_success}")
    print(f"CONTROL always-invent            mean_loss={c_abs:.9f}")
    print(f"BASELINE dig-iff-count>0         mean_loss={c_hit:.9f}  vs_control={vs_hit}")
    print(f"BASELINE dig-iff-BM25/rank-hit   mean_loss={c_score:.9f}  vs_control={vs_score}")
    print("Y  mechanical receipt-shaped / wrong-selector evidence (cass_dig_y.py) — not human edit-delta")
    print("LOSS  invent-on-y1=1  dig-on-y0=2  else=0")
    print("NO-CLAIM  [pending] promoted=0  no Jev call  no cass rebuild started")
    print(f"EXIT 0  (count>0 baseline {vs_hit}s always-invent; rank baseline {vs_score}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
