#!/usr/bin/env python3
"""Hard-case draw for jev-t2u. No Jev call.

Same pool as sample B (real-sample-b.py: cutoff, isError false, private/secret dropped, home as ~),
minus every sample-A command (real-sample.json) and every sample-B command
(real-sample-b-labelled.json risky + routine). Readers are the jev-xxy-fixed reader 1
(real-sample-b.py) and reader 2 (label-b.py). A disagreement is a command where exactly one reader
says the harm rule is met. Up to N are drawn by SEED; labels are added by hand in
hard-cases-labels.json.

Run: python3 work/bicameral-gate/hard-cases.py   (rewrites hard-cases-sample.json)
"""

import importlib.util
import json
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 20260925
N = 200
OUT = os.path.join(HERE, "hard-cases-sample.json")

_spec = importlib.util.spec_from_file_location(
    "label_b", os.path.join(HERE, "label-b.py")
)
lb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lb)


def disagreements():
    seen, stats = lb.pool()
    a = set(json.load(open(os.path.join(HERE, "real-sample.json")))["commands"])
    b_lab = json.load(open(os.path.join(HERE, "real-sample-b-labelled.json")))
    b = {r["command"] for r in b_lab["risky"] + b_lab["routine"]}
    remain = sorted(c for c in seen if c not in a and c not in b)
    rows = []
    for cmd in remain:
        r1, r2 = lb.reader1(cmd), lb.reader2(cmd)
        if bool(r1) != bool(r2):
            rows.append({"command": cmd, "reader1": r1, "reader2": r2})
    return stats, len(seen), len(a), len(b), len(remain), rows


def main():
    stats, n_pool, n_a, n_b, n_remain, rows = disagreements()
    draw = rows[:]
    random.Random(SEED).shuffle(draw)
    draw = draw[:N]
    out = {
        "seed": SEED,
        "cutoff": "2026-09-24T01:00:00Z",
        "readers": "jev-xxy fix 1e1833d",
        "pool": n_pool,
        "excluded_a": n_a,
        "excluded_b": n_b,
        "remain": n_remain,
        "disagreements": len(rows),
        "reader1_only": sum(1 for r in rows if r["reader1"]),
        "reader2_only": sum(1 for r in rows if r["reader2"]),
        "drawn": len(draw),
        "stats": stats,
        "rows": [dict(i=i, **r) for i, r in enumerate(draw)],
    }
    with open(OUT, "w") as fh:
        json.dump(out, fh, indent=1)
        fh.write("\n")
    print(json.dumps({k: v for k, v in out.items() if k not in ("rows", "stats")}))


if __name__ == "__main__":
    raise SystemExit(main())
