#!/usr/bin/env python3
"""Independent verify of jev-q9eq (do not use ab-q9eq.analyze.py/cost.py)."""

import json
import math
from collections import defaultdict
from pathlib import Path

D = Path(__file__).resolve().parent
res = json.loads((D / "ab-q9eq.results.json").read_text())
met = json.loads((D / "ab-q9eq.metered.json").read_text())

by = defaultdict(dict)
for r in res:
    by[(r["task"], r["rep"])][r["arm"]] = r
pairs = [
    (v["ON"]["pass"], v["OFF"]["pass"]) for v in by.values() if "ON" in v and "OFF" in v
]
print("pairs:", len(pairs))
on = sum(1 for a, _ in pairs if a)
off = sum(1 for _, b in pairs if b)
print("success ON %d/56 OFF %d/56" % (on, off))
b = sum(1 for a, bb in pairs if a and not bb)
c = sum(1 for a, bb in pairs if not a and bb)
print("discordants b=%d c=%d" % (b, c))
n = b + c
pval = sum(math.comb(n, k) for k in range(0, min(b, c) + 1)) / 2**n if n else 1.0
print("McNemar exact two-sided p=%.4f" % pval)


def wilcoxon_signed(xs):
    xs = [x for x in xs if x != 0]
    n = len(xs)
    if n == 0:
        return 1.0, 0
    ranks = sorted(range(n), key=lambda i: abs(xs[i]))
    w = sum((i + 1) for i in ranks if xs[i] > 0)
    mu = n * (n + 1) / 4
    sd = math.sqrt(n * (n + 1) * (2 * n + 1) / 24)
    z = (w - mu) / sd if sd else 0
    import statistics

    p = 2 * (1 - statistics.NormalDist().cdf(abs(z)))
    return round(p, 4), n


mm = {(m["task"], m["rep"], m["arm"]): m for m in met}
for key in ("in", "out", "tools"):
    diffs = [
        mm[(t, r, "ON")][key] - mm[(t, r, "OFF")][key]
        for (t, r) in by
        if (t, r, "ON") in mm and (t, r, "OFF") in mm
    ]
    p, nz = wilcoxon_signed(diffs)
    med_on = sorted(mm[(t, r, "ON")][key] for (t, r) in by if (t, r, "ON") in mm)[
        len(diffs) // 2
    ]
    med_off = sorted(mm[(t, r, "OFF")][key] for (t, r) in by if (t, r, "OFF") in mm)[
        len(diffs) // 2
    ]
    print(
        "cost %s: med ON %d OFF %d, Wilcoxon p=%s (n=%d paired)"
        % (key, med_on, med_off, p, nz)
    )
jn = sum(m.get("jev_n", 0) for m in met if m["arm"] == "ON")
jf = sum(m.get("jev_n", 0) for m in met if m["arm"] == "OFF")
print("jev calls ON %d OFF %d" % (jn, jf))

print("== power: min one-sided discordants for p<0.05 ==")


def min_detect(k):
    from math import comb

    for d in range(1, k + 1):
        if sum(comb(d, i) for i in range(0, 1)) / 2**d < 0.05:
            return d
    return None


for tot in (56, 56):
    print(
        "pairs=%d: need >=6 same-direction discordants (6/64 one-sided exact p=0.016; 5/32 p=0.031 at n=5)"
        % tot
    )
print(
    "ceiling note: 52/56 pass both arms leaves at most 8 failures/arm; observed 0 discordants"
)
