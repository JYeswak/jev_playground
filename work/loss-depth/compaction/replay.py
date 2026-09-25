#!/usr/bin/env python3
"""Keyless score of the compaction replay loop's dev pass (bead jev-9gtw.6).

  python3 work/loss-depth/compaction/replay.py   # REFUSED until replay.ts dev --live has written dev-answers.jsonl

Preregistered in docs/demos/upstream-repro/compaction-replay-20260925.md. Reads dev-answers.jsonl
(ids and scores), the two studies' committed labels, and this directory's features.jsonl and
codes.jsonl (the autopsy's subgroups). Dev slice only: this is never a held-out result.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "work" / "compaction-need"))
sys.path.insert(0, str(ROOT / "work" / "compaction-keep"))
import keep as K  # noqa: E402
import need as N  # noqa: E402

# Each arm's primary score: the Noul that decides whether a result is kept verbatim.
PRIMARY = {"A0": "keepResult", "H1": "use", "H2": "keepResult", "H3": "keepResult"}
CUT = 0.5
DROP_AT_LEAST = (
    0.50  # the bar's second half: at least half of the not-needed results dropped
)
HEAD = 500


def auc(pos: list[float], neg: list[float]) -> float:
    wins = sum((p > q) + 0.5 * (p == q) for p in pos for q in neg)
    return wins / (len(pos) * len(neg))


def rate(k: int, n: int) -> str:
    lo, hi = N.R1.wilson(k, n)
    return f"{k}/{n} (Wilson {max(0.0, lo):.3f}-{min(1.0, hi):.3f})"


def labels() -> dict:
    out = {}
    for mod in (N, K):
        keys = mod.calls()
        got = mod.final(keys)
        if isinstance(got, str):
            sys.exit(f"REFUSED: {got}")
        out.update(got[2])
    return out


def main() -> int:
    path = HERE / "dev-answers.jsonl"
    if not path.exists():
        print(
            "REFUSED: no dev pass yet (dev-answers.jsonl is written by `replay.ts dev --live`)"
        )
        return 1
    rows = N.read_jsonl(path)
    lab = labels()
    feats = {
        (f["session"], f["tool_use_id"]): f
        for f in N.read_jsonl(HERE / "features.jsonl")
    }
    codes = {
        (c["session"], c["tool_use_id"]): c for c in N.read_jsonl(HERE / "codes.jsonl")
    }
    by = {}
    for r in rows:
        by.setdefault(r["arm"], {})[(r["session"], r["tool_use_id"])] = r
    free = [k for k, r in by["A0"].items() if not r["pinned"]]
    pos = [k for k in free if lab[k] == "needed"]
    neg = [k for k in free if lab[k] == "not-needed"]
    und = [k for k in free if lab[k] == "undecidable"]
    print(
        f"dev slice: {len({k[0] for k in free})} sessions, unpinned needed {len(pos)}, not-needed {len(neg)}, undecidable {len(und)}"
    )
    print((HERE / "dev-pass.json").read_text().strip())

    print(
        "\n| arm | score | AUC | needed kept at 0.5 | not-needed dropped at 0.5 | dev cut | needed kept at dev cut | not-needed dropped at dev cut | dev bar |"
    )
    print("|---|---|---:|---|---:|---:|---|---:|---|")
    for arm, field in PRIMARY.items():
        s = {k: by[arm][k][field] for k in free}
        p, q = [s[k] for k in pos], [s[k] for k in neg]
        kept = sum(x >= CUT for x in p)
        dropped = sum(x < CUT for x in q)
        # The dev cut: the smallest observed score that drops at least half of the not-needed results.
        t = min(
            v
            for v in sorted(set(p + q))
            if sum(x < v for x in q) >= DROP_AT_LEAST * len(q)
        )
        kt, dt = sum(x >= t for x in p), sum(x < t for x in q)
        lo, _ = N.R1.wilson(kt, len(p))
        print(
            f"| {arm} | {field} | {auc(p, q):.3f} | {rate(kept, len(p))} | {dropped}/{len(q)} | {t} | {rate(kt, len(p))} | "
            f"{dt}/{len(q)} | {'MET' if lo >= 0.80 else 'not met'} |"
        )
    for arm in ("A0", "H2", "H3"):
        p = [by[arm][k]["keepCall"] for k in pos]
        q = [by[arm][k]["keepCall"] for k in neg]
        print(f"{arm} keepCall (descriptive): AUC {auc(p, q):.3f}")

    print("\n## Subgroups named in the prereg")
    shown = [k for k in pos if k in codes and codes[k]["visible"] == "goal"]
    inside = [
        k
        for k in pos
        if k in codes
        and codes[k]["reobtain"] != "stub"
        and feats[k]["use_min_offset"] is not None
        and feats[k]["use_min_offset"] < HEAD
    ]
    rest = [k for k in pos if k not in inside]
    for arm, field in PRIMARY.items():
        g = [by[arm][k][field] for k in shown]
        a = [by[arm][k][field] for k in inside]
        b = [by[arm][k][field] for k in rest]
        print(
            f"{arm}: the {len(g)} goal-named reads mean {sum(g) / len(g):.3f}, >= 0.5 on {sum(x >= 0.5 for x in g)}; "
            f"needed with a used token inside the first {HEAD} chars ({len(a)}) mean {sum(a) / len(a):.3f}, other needed ({len(b)}) mean {sum(b) / len(b):.3f}"
        )

    print("\n## A0 against the recorded studies (same request, same model pin)")
    same = diffs = 0
    worst = 0.0
    for study, d in (
        ("x86y", ROOT / "work/compaction-need"),
        ("jec6", ROOT / "work/compaction-keep"),
    ):
        rec = {
            (r["session"], r["tool_use_id"]): r
            for r in N.read_jsonl(d / "decisions.jsonl")
        }
        for k in free:
            if k not in rec:
                continue
            for f in ("keepCall", "keepResult"):
                delta = abs(rec[k][f] - by["A0"][k][f])
                same += delta == 0
                diffs += delta != 0
                worst = max(worst, delta)
    print(
        f"A0 nouls equal to the recorded ones: {same} of {same + diffs}; largest difference {worst:.2f}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
