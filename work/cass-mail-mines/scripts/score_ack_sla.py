#!/usr/bin/env python3
"""Ack-SLA mine — Jeff 0/1/2 + always-abstain.

Y: ack_required=1 rows; y=1 if any message_recipients.ack_ts set, else 0.
Choice: {expect_ack, __none__}. Positive = y=1 (handshake completed).
Loss: correct=0, false-abstain on y=1 → 1, expect_ack on y=0 → 2.

Controls:
  always-abstain  → mean = prevalence(y=1)
  high→expect_ack → expect_ack iff importance in {high,urgent} else abstain

    python3 work/cass-mail-mines/scripts/score_ack_sla.py \
      work/cass-mail-mines/exports/ack-sla-rows.jsonl
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
        raise SystemExit(f"REFUSE: n={len(rows)} < 100 (need real export, not a toy)")
    return rows


def loss(y: int, pick: str) -> int:
    # pick in {expect_ack, abstain}
    if pick == "abstain":
        return 1 if y == 1 else 0
    if pick == "expect_ack":
        return 0 if y == 1 else 2
    raise SystemExit(f"bad pick {pick!r}")


def mean(rows, pick_of) -> float:
    return sum(loss(int(r["y"]), pick_of(r)) for r in rows) / len(rows)


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__, file=sys.stderr)
        return 2
    path = Path(argv[0])
    if not path.is_file():
        print(f"MISSING_EXPORT  {path}", file=sys.stderr)
        print("Run STUDIO_EXPORT.md Ack-SLA block on Joshs-Mac-Studio.local", file=sys.stderr)
        return 2
    rows = load(path)
    n = len(rows)
    pos = sum(1 for r in rows if int(r["y"]) == 1)
    prev = pos / n
    c_abs = mean(rows, lambda r: "abstain")
    c_high = mean(
        rows,
        lambda r: "expect_ack" if str(r.get("importance", "")).lower() in ("high", "urgent") else "abstain",
    )
    c_always = mean(rows, lambda r: "expect_ack")
    vs = "BEAT" if c_high < c_abs else "LOSE"
    print(f"MINE ack-sla  store=mail  n={n}  y_acked={pos}  prevalence={prev:.9f}")
    print(f"CONTROL always-abstain           mean_loss={c_abs:.9f}  ({pos}/{n})")
    print(f"BASELINE high|urgent→expect_ack  mean_loss={c_high:.9f}  vs_control={vs}")
    print(f"BASELINE always-expect_ack       mean_loss={c_always:.9f}")
    print("NO-CLAIM  [pending] promoted=0  mechanical Y=any(ack_ts)  no Jev call")
    print(f"EXIT 0  (high-importance baseline {vs}s always-abstain)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
