#!/usr/bin/env python3
"""Importance mine — prevalence + optional length baseline.

Y: y=1 if importance in {high,urgent}, else 0.
Choice: {elevated, __none__}.
Loss: correct=0, false-abstain on elevated=1, elevated on normal=2.

When JSONL missing, prints Studio-confirmed aggregate control only (n=6510).

    python3 work/cass-mail-mines/scripts/score_importance.py \
      [--aggregate-only] [exports/importance-rows.jsonl]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Studio probe 2026-09-20 (parent ExternalShell) — bake, do not invent.
STUDIO_N = 6510
STUDIO_NORMAL = 5758
STUDIO_HIGH = 566
STUDIO_URGENT = 186
STUDIO_ELEVATED = STUDIO_HIGH + STUDIO_URGENT  # 752


def loss(y: int, pick: str) -> int:
    if pick == "abstain":
        return 1 if y == 1 else 0
    if pick == "elevated":
        return 0 if y == 1 else 2
    raise SystemExit(f"bad pick {pick!r}")


def mean(rows, pick_of) -> float:
    return sum(loss(int(r["y"]), pick_of(r)) for r in rows) / len(rows)


def print_aggregate() -> int:
    n, pos = STUDIO_N, STUDIO_ELEVATED
    prev = pos / n
    # always-abstain
    c_abs = prev  # = pos*1/n
    # always-elevated
    c_all = 2 * (n - pos) / n
    print(f"MINE importance-prevalence  store=mail  n={n}  elevated={pos}  prevalence={prev:.9f}")
    print(f"  mix  normal={STUDIO_NORMAL} high={STUDIO_HIGH} urgent={STUDIO_URGENT}")
    print(f"CONTROL always-abstain      mean_loss={c_abs:.9f}  ({pos}/{n})")
    print(f"BASELINE always-elevated    mean_loss={c_all:.9f}  vs_control=LOSE")
    print("LENGTH_BASELINE  NOT_RUN  (needs exports/importance-rows.jsonl)")
    print("SOURCE  Studio probe 2026-09-20 parent ExternalShell aggregates")
    print("NO-CLAIM  [pending] promoted=0  no subject/body rows in this arm")
    return 0


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


def length_baseline(rows: list[dict], thr: int) -> float:
    # predict elevated if subject_len+body_len >= thr
    def pick(r):
        L = int(r.get("subject_len") or 0) + int(r.get("body_len") or 0)
        return "elevated" if L >= thr else "abstain"

    return mean(rows, pick)


def main(argv: list[str]) -> int:
    if "--aggregate-only" in argv or not argv:
        return print_aggregate()
    path = Path(argv[0])
    if not path.is_file():
        print(f"MISSING_EXPORT  {path} — falling back to Studio aggregates", file=sys.stderr)
        return print_aggregate()
    rows = load(path)
    n = len(rows)
    pos = sum(1 for r in rows if int(r["y"]) == 1)
    prev = pos / n
    c_abs = mean(rows, lambda r: "abstain")
    c_all = mean(rows, lambda r: "elevated")
    # pick thr on a simple grid that beats abstain if any
    best_thr, best_loss = None, 1e9
    for thr in (50, 100, 200, 400, 800, 1600, 3200):
        ml = length_baseline(rows, thr)
        if ml < best_loss:
            best_loss, best_thr = ml, thr
    vs = "BEAT" if best_loss < c_abs else "LOSE"
    print(f"MINE importance+length  store=mail  n={n}  elevated={pos}  prevalence={prev:.9f}")
    print(f"CONTROL always-abstain           mean_loss={c_abs:.9f}")
    print(f"BASELINE always-elevated         mean_loss={c_all:.9f}")
    print(f"BASELINE len>=thr→elevated       thr={best_thr}  mean_loss={best_loss:.9f}  vs_control={vs}")
    print("NO-CLAIM  [pending] promoted=0  Y=importance high|urgent  mechanical")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
