#!/usr/bin/env python3
"""Sample C draw for jev-p19. No Jev call.

Pool is label-b.py's pool. Excludes sample A, sample B, and the 200 hard-case commands.
Readers are the jev-xxy fix at 1e1833d (reader1, reader2). The in-place stratum is every
remaining command matching the marker below. Other risky and routine are seeded draws.
Human labels are not written here.

Run: python3 work/bicameral-gate/sample-c.py
"""

import importlib.util
import json
import os
import random
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 20260926
N_OTHER = 40
N_ROUTINE = 160
OUT = os.path.join(HERE, "sample-c.json")

_spec = importlib.util.spec_from_file_location(
    "label_b", os.path.join(HERE, "label-b.py")
)
lb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lb)


def inplace_marker(cmd):
    """Mechanical stratum marker. Not a label."""
    if re.search(r"sed\s+-[a-zA-Z]*i", cmd) and not re.search(
        r"sed\s+-[a-zA-Z]*i[^\n]*/tmp/", cmd
    ):
        return "sed-i"
    if re.search(r"\.write_text\(", cmd) and "/tmp" not in cmd:
        return "write_text"
    if re.search(r"open\([^)]*['\"]w['\"]", cmd) and "/tmp" not in cmd:
        return "open-w"
    if ".write(" in cmd and "open(" in cmd and "/tmp" not in cmd:
        return "open-write"
    return ""


def main():
    seen, stats = lb.pool()
    a = set(json.load(open(os.path.join(HERE, "real-sample.json")))["commands"])
    b_lab = json.load(open(os.path.join(HERE, "real-sample-b-labelled.json")))
    b = {r["command"] for r in b_lab["risky"] + b_lab["routine"]}
    hard = {
        r["command"]
        for r in json.load(open(os.path.join(HERE, "hard-cases-sample.json")))["rows"]
    }
    remain = [c for c in seen if c not in a and c not in b and c not in hard]
    marked = []
    both = []
    neither = []
    for cmd in remain:
        marker = inplace_marker(cmd)
        r1, r2 = bool(lb.reader1(cmd)), bool(lb.reader2(cmd))
        row = {
            "command": cmd,
            "reader1": r1,
            "reader2": r2,
            "marker": marker,
        }
        if marker:
            marked.append(row)
        elif r1 and r2:
            both.append(row)
        elif not r1 and not r2:
            neither.append(row)
    rng = random.Random(SEED)
    rng.shuffle(both)
    rng.shuffle(neither)
    other = both[:N_OTHER]
    routine = neither[:N_ROUTINE]
    rows = []
    for row in marked:
        rows.append(dict(stratum="inplace", **row))
    for row in other:
        rows.append(dict(stratum="other-risky", **row))
    for row in routine:
        rows.append(dict(stratum="routine", **row))
    for i, row in enumerate(rows):
        row["i"] = i
    out = {
        "seed": SEED,
        "cutoff": "2026-09-24T01:00:00Z",
        "readers": "jev-xxy fix 1e1833d",
        "pool": len(seen),
        "excluded_a": len(a),
        "excluded_b": len(b),
        "excluded_hard": len(hard),
        "remain": len(remain),
        "inplace_marked": len(marked),
        "other_risky_pool": len(both),
        "routine_pool": len(neither),
        "drawn_other_risky": len(other),
        "drawn_routine": len(routine),
        "drawn": len(rows),
        "stats": stats,
        "rows": rows,
    }
    with open(OUT, "w") as fh:
        json.dump(out, fh, indent=1)
        fh.write("\n")
    print(json.dumps({k: v for k, v in out.items() if k not in ("rows", "stats")}))


if __name__ == "__main__":
    raise SystemExit(main())
