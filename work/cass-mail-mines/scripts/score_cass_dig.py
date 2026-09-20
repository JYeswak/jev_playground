#!/usr/bin/env python3
"""Dig-vs-invent on cass --robot (or sqlite-fallback) rows.

Each row: query, hit_count, y (mechanical — see cass_dig_y.py).
Choice: {dig, invent}. invent ≡ always-abstain on dig-vs-invent.
Loss: dig on y=0 → 2; invent on y=1 → 1; else 0.

Controls / baselines (documented 0/1/2 map):
  always-invent / always-abstain
  always-open-top1   (= dig iff hit_count>0 — open BM25 top-1)
  dig-iff-path-token (= dig iff top-1 source_path token appears in query tokens)
  dig-iff-BM25/rank  (= dig when a scored/path hit exists)

    python3 work/cass-mail-mines/scripts/score_cass_dig.py \
      work/cass-mail-mines/exports/cass-dig-rows.jsonl
    # timed Studio subset may be n<100:
    python3 .../score_cass_dig.py --allow-small exports/cass-dig-rows.jsonl
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def load(path: Path, allow_small: bool) -> list[dict]:
    rows = []
    for i, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip() or line.startswith("#"):
            continue
        r = json.loads(line)
        if "y" not in r:
            raise SystemExit(f"{path}:{i} missing y")
        rows.append(r)
    if len(rows) < 100 and not allow_small:
        raise SystemExit(f"REFUSE: n={len(rows)} < 100 (pass --allow-small for timed subset)")
    if len(rows) < 2:
        raise SystemExit(f"REFUSE: n={len(rows)} < 2")
    return rows


def loss(y: int, pick: str) -> int:
    if pick == "invent":
        return 1 if y == 1 else 0
    if pick == "dig":
        return 0 if y == 1 else 2
    raise SystemExit(pick)


def mean(rows, pick_of) -> float:
    return sum(loss(int(r["y"]), pick_of(r)) for r in rows) / len(rows)


def path_token_in_query(r: dict) -> bool:
    """Ranker feature: does top-1 hit path appear in query tokens?"""
    path = str(r.get("top_path") or "")
    q = str(r.get("query") or "").lower()
    if not path or not q:
        return False
    parts = re.split(r"[/\\._\-\s]+", path)
    tokens = [p.lower() for p in parts if len(p) >= 4 and p.isascii()]
    # drop ultra-common path noise
    noise = {"jsonl", "json", "users", "josh", "home", "var", "tmp", "sessions", "agent"}
    tokens = [t for t in tokens if t not in noise]
    return any(t in q for t in tokens)


def main(argv: list[str]) -> int:
    allow_small = "--allow-small" in argv
    argv = [a for a in argv if a != "--allow-small"]
    if not argv:
        print(__doc__, file=sys.stderr)
        return 2
    path = Path(argv[0])
    if not path.is_file():
        print(f"MISSING_EXPORT {path}", file=sys.stderr)
        return 2
    rows = load(path, allow_small=allow_small)
    n = len(rows)
    pos = sum(1 for r in rows if int(r["y"]) == 1)
    empty_success = sum(
        1 for r in rows if int(r.get("hit_count") or 0) > 0 and int(r["y"]) == 0
    )
    c_abs = mean(rows, lambda r: "invent")  # always-abstain
    c_top1 = mean(
        rows, lambda r: "dig" if int(r.get("hit_count") or 0) > 0 else "invent"
    )  # always-open-top1
    c_path = mean(
        rows, lambda r: "dig" if path_token_in_query(r) else "invent"
    )
    c_score = mean(
        rows,
        lambda r: "dig"
        if (
            (r.get("top_score") not in (None, "", 0, "0") and int(r.get("hit_count") or 0) > 0)
            or (int(r.get("hit_count") or 0) > 0 and r.get("top_path"))
        )
        else "invent",
    )
    vs_top1 = "BEAT" if c_top1 < c_abs else "LOSE"
    vs_path = "BEAT" if c_path < c_abs else "LOSE"
    vs_score = "BEAT" if c_score < c_abs else "LOSE"
    print(f"MINE cass-dig-vs-invent  store=cass  n={n}  y_dig={pos}  prevalence={pos/n:.9f}")
    print(f"  empty_success_rows (count>0 & y=0) = {empty_success}")
    print(f"CONTROL always-abstain/invent    mean_loss={c_abs:.9f}")
    print(f"BASELINE always-open-top1        mean_loss={c_top1:.9f}  vs_control={vs_top1}")
    print(f"BASELINE dig-iff-path-in-query   mean_loss={c_path:.9f}  vs_control={vs_path}")
    print(f"BASELINE dig-iff-BM25/rank-hit   mean_loss={c_score:.9f}  vs_control={vs_score}")
    print("Y  mechanical receipt-shaped / wrong-selector evidence (cass_dig_y.py) — not human edit-delta")
    print("LOSS  invent-on-y1=1  dig-on-y0=2  else=0")
    if allow_small and n < 100:
        print(f"NOTE  timed-subset n={n} < 100 (--allow-small)")
    print("NO-CLAIM  [pending] promoted=0  no Jev call  no cass rebuild started")
    print(f"EXIT 0  (open-top1 {vs_top1}s abstain; path-token {vs_path}s; rank {vs_score}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
