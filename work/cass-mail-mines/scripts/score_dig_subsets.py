#!/usr/bin/env python3
"""Named-subset breakdown of the locked n=138 dig-vs-invent export.

Slices and falsifier: docs/demos/upstream-repro/dig-subset-falsifier-20260920.md.
Loss frozen: invent-on-y1=1, dig-on-y0=2, else 0. Read-only; no store access.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SLICES = {
    "S_wrong_selector": re.compile(
        r"no such|missing field|does not exist|undefined|requireKey|"
        r"distribution|customType|keys present|wrong selector",
        re.I,
    ),
    "S_lexical_trap": re.compile(r"cass|robot|\bTUI\b|noul|AGENTS\.md", re.I),
    "S_control": re.compile(r"zzzz_cannot_exist|negative control", re.I),
    "S_pass_probes": re.compile(r" pass \d+$"),
}


def loss(y: int, pick: str) -> int:
    if pick == "abstain":
        return 1 if y == 1 else 0
    if pick == "invent":
        return 1 if y == 1 else 0
    if pick == "dig":
        return 2 if y == 0 else 0
    raise AssertionError(pick)


def main(path: str) -> int:
    rows = [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]
    print(f"n={len(rows)}")
    out: dict = {}
    for name, rx in SLICES.items():
        sub = [r for r in rows if rx.search(r["query"])]
        rest = [r for r in rows if not rx.search(r["query"])]
        inv = sum(loss(r["y"], "invent") for r in sub) / len(sub)
        dig = sum(
            loss(r["y"], "dig" if r["hit_count"] > 0 else "invent") for r in sub
        ) / len(sub)
        out[name] = {
            "n": len(sub),
            "y_dig": sum(r["y"] for r in sub),
            "always_invent": round(inv, 9),
            "dig_iff_count": round(dig, 9),
            "beats": dig < inv,
            "rest_n": len(rest),
        }
    topical = [
        r
        for r in rows
        if not any(
            rx.search(r["query"]) for n, rx in SLICES.items() if n != "S_topical"
        )
    ]
    # S_topical defined in falsifier as everything else (excl. pass probes too)
    top = [r for r in rows if not any(rx.search(r["query"]) for rx in SLICES.values())]
    inv = sum(loss(r["y"], "invent") for r in top) / len(top)
    dig = sum(
        loss(r["y"], "dig" if r["hit_count"] > 0 else "invent") for r in top
    ) / len(top)
    out["S_topical"] = {
        "n": len(top),
        "y_dig": sum(r["y"] for r in top),
        "always_invent": round(inv, 9),
        "dig_iff_count": round(dig, 9),
        "beats": dig < inv,
    }
    empty = [r for r in rows if r["hit_count"] > 0 and r["y"] == 0]
    out["empty_success"] = {"n": len(empty)}
    zzzz = [r for r in rows if "zzzz" in r["query"]]
    out["control_check"] = {
        "zzzz_rows": len(zzzz),
        "zzzz_max_count": max([r["hit_count"] for r in zzzz] or [0]),
        "zzzz_y1": sum(r["y"] for r in zzzz),
        "control_y1_anywhere": sum(
            1 for r in rows if SLICES["S_control"].search(r["query"]) and r["y"] == 1
        ),
    }
    fired = [
        n
        for n in (
            "S_wrong_selector",
            "S_lexical_trap",
            "S_control",
            "S_pass_probes",
            "S_topical",
        )
        if not out[n]["beats"]
    ]
    cc = out["control_check"]
    if cc["zzzz_max_count"] > 0 or cc["zzzz_y1"] > 0 or cc["control_y1_anywhere"] > 0:
        out["verdict"] = "BLOCKED-HARNESS"
    elif fired:
        out["verdict"] = "HELD"
    else:
        out["verdict"] = "DONE"
    out["verdict_detail"] = {
        "failed_slices": fired,
        "falsifier": "dig-subset-falsifier-20260920.md",
    }
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
