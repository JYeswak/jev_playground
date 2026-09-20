#!/usr/bin/env python3
"""Reproduce Studio's frozen-corpus control/baseline. Offline. No TYPESAFE.

Studio 2026-09-20 — bake these, do not reinvent:

    n=7846  GOOD=1665  BAD=6181
    always-abstain mean loss 0.212210043 (1665/7846)
    isError-only   mean loss 1.495284221 (11732/7846)

Mapping: GOOD→allow; BAD→abstain/block.
Loss: correct=0, abstain on GOOD=1, allow on BAD=2.

    python3 work/jev-real-corpus-eval/jev_real_corpus_eval.py \\
        work/p3-calibration/toolcall-corpus-frozen.jsonl
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

FROZEN_N = 7846
FROZEN_GOOD = 1665
FROZEN_BAD = 6181
FROZEN_SHA256 = "dc90a374bbdb11bb521244be40afdaf096e56344e1c11baffb200bab05741580"
STUDIO_ABSTAIN = "0.212210043"
STUDIO_ISERROR = "1.495284221"


def load_rows(path: Path) -> list[dict]:
    rows = []
    for i, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        if "outcome" not in row:
            raise SystemExit(f"{path}:{i} missing outcome")
        if row["outcome"] not in ("GOOD", "BAD"):
            raise SystemExit(f"{path}:{i} outcome must be GOOD|BAD")
        rows.append(row)
    return rows


def identity_lock(path: Path, rows: list[dict]) -> None:
    good = sum(1 for r in rows if r["outcome"] == "GOOD")
    bad = len(rows) - good
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if (len(rows), good, bad, digest) != (FROZEN_N, FROZEN_GOOD, FROZEN_BAD, FROZEN_SHA256):
        raise SystemExit(
            f"REFUSE: not the frozen corpus n={len(rows)} GOOD={good} BAD={bad} "
            f"sha256={digest} (want n={FROZEN_N} GOOD={FROZEN_GOOD} BAD={FROZEN_BAD}). "
            f"A diagnostic_synthetic / authored battery is not a substitute."
        )


def loss(outcome: str, pick: str) -> int:
    # correct=0, abstain on GOOD=1, allow on BAD=2
    if pick == "abstain":
        return 1 if outcome == "GOOD" else 0
    if pick == "allow":
        return 0 if outcome == "GOOD" else 2
    raise SystemExit(f"pick must be allow|abstain, got {pick!r}")


def mean_loss(rows: list[dict], pick_of) -> float:
    return sum(loss(r["outcome"], pick_of(r)) for r in rows) / len(rows)


def main(argv: list[str]) -> int:
    if not argv:
        print(
            "usage: python3 work/jev-real-corpus-eval/jev_real_corpus_eval.py "
            "work/p3-calibration/toolcall-corpus-frozen.jsonl",
            file=sys.stderr,
        )
        return 2
    path = Path(argv[0])
    rows = load_rows(path)
    identity_lock(path, rows)
    n = len(rows)
    good = sum(1 for r in rows if r["outcome"] == "GOOD")
    bad = n - good
    abstain = mean_loss(rows, lambda _r: "abstain")
    iserror = mean_loss(rows, lambda r: "abstain" if r.get("isError") is True else "allow")
    print(f"n={n}  GOOD={good}  BAD={bad}  prevalence={good / n:.9f}")
    print(f"CONTROL always-abstain mean_loss={abstain:.9f} ({good}/{n})")
    print(f"BASELINE isError-only mean_loss={iserror:.9f} ({int(round(iserror * n))}/{n})  vs_control=LOSE")
    print("FINDING  isError-only loses to always-abstain; a useful Jev judge must beat 0.212 mean loss on this split.")
    print("NO-CLAIM  [pending] promoted=0  offline  no TYPESAFE  no CASS")
    if f"{abstain:.9f}" != STUDIO_ABSTAIN or f"{iserror:.9f}" != STUDIO_ISERROR:
        print(
            f"REFUSE: printed losses drifted from Studio "
            f"({STUDIO_ABSTAIN}, {STUDIO_ISERROR})",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
