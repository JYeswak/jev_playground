#!/usr/bin/env python3
"""Recompute factorial matrix arms from committed rows. No network."""

import json
from collections import defaultdict
from pathlib import Path

D = Path(__file__).resolve().parent
POS2 = {
    "retry": "retry_now",
    "d1read": "read_next",
    "diffrisk": "fails",
    "veto": "unsupported",
}


def y_of(task, label):
    return 1 if (label == "read" if task == "d1read" else label == 1) else 0


print("== ARM1 symmetrized ==")
a1 = defaultdict(list)
for line in (D / "arm1-sym.jsonl").open():
    if line.strip():
        r = json.loads(line)
        a1[r["id"].split("-")[0]].append(r)
for task, rs in sorted(a1.items()):
    ok = [
        r
        for r in rs
        if r.get("ok")
        and isinstance(r.get("ppos"), (int, float))
        and isinstance(r.get("pneg"), (int, float))
    ]
    gaps = [abs(r["ppos"] + r["pneg"] - 1) for r in ok]
    print(task, "n=", len(ok), "mean|gap|=%.3f" % (sum(gaps) / len(gaps)))
    dev, held = ok[:15], ok[15:]
    sdev = [
        (
            (p["ppos"] + (1 - p["pneg"])) / 2,
            1 if p["label"] == 1 or p["label"] == "read" else 0,
        )
        for p in dev
    ]
    best = max(
        ([c / 100 for c in range(5, 96, 5)]),
        key=lambda c: sum(1 for v, y in sdev if (v >= c) == bool(y)) / len(sdev),
    )
    sh = [
        (
            (p["ppos"] + (1 - p["pneg"])) / 2,
            1 if p["label"] == 1 or p["label"] == "read" else 0,
        )
        for p in held
    ]
    acc = sum(1 for v, y in sh if (v >= best) == bool(y)) / len(sh)
    print("  cut=%.2f held acc=%.3f n=%d" % (best, acc, len(sh)))

print("== ARM2 positive-only Choice ==")
a2 = defaultdict(list)
for line in (D / "arm2-choice.jsonl").open():
    if line.strip():
        r = json.loads(line)
        a2[r["id"].split("-")[0]].append(r)
for task, rs in sorted(a2.items()):
    ok = [r for r in rs if r.get("ok")]
    dev, held = ok[:15], ok[15:]
    pos = POS2[task]
    best = None
    for ci in range(0, 101, 5):
        c = ci / 100
        pred = [
            1 if (r.get("choice") == pos and (r.get("conf") or 0) >= c) else 0
            for r in dev
        ]
        labs = [y_of(task, r["label"]) for r in dev]
        acc = sum(1 for a, b in zip(pred, labs) if a == b) / len(dev)
        if best is None or acc > best[1]:
            best = (c, acc)
    pred = [
        1 if (r.get("choice") == pos and (r.get("conf") or 0) >= best[0]) else 0
        for r in held
    ]
    labs = [y_of(task, r["label"]) for r in held]
    acc = sum(1 for a, b in zip(pred, labs) if a == b) / len(held)
    tp = sum(1 for a, b in zip(pred, labs) if a == 1 and b == 1)
    fn = sum(1 for a, b in zip(pred, labs) if a == 0 and b == 1)
    print(
        task,
        "n=",
        len(ok),
        "devcut=%.2f held acc=%.3f rec=%.3f"
        % (best[0], acc, tp / (tp + fn) if tp + fn else 0),
    )
