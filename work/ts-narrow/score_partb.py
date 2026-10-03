#!/usr/bin/env python3
"""Score Part B msax arm (jev-2zbl). T0/T1/T2 flips vs recorded ref / T0; T3 meaning-mapped.
Reads the committed rows (same dir); a non-author recomputes with: python3 work/ts-narrow/score_partb.py"""

import json
import math
import os

with open(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "partb_rows.jsonl"),
    encoding="utf-8",
) as stream:
    rec = [json.loads(line) for line in stream if line.strip()]
bad = [r for r in rec if r["status"] != "ok"]
print("rows=160 bad=%d" % len(bad))
byid = {}
for r in rec:
    byid.setdefault(r["id"], {})[r["t"]] = r
N = len(byid)
print("pairs=%d" % N)


def w(k, n):
    p = k / n
    den = 1 + 3.8416 / n
    c = p + 3.8416 / (2 * n)
    m = 1.96 * math.sqrt(p * (1 - p) / n + 3.8416 / (4 * n * n))
    return (max(0, (c - m) / den), min(1, (c + m) / den))


f0 = [i for i, d in byid.items() if d["T0"]["choice"] != d["T0"]["ref"]]
print(
    "I0 T0-identity flips vs recorded: %d/%d Wilson [%.3f,%.3f] bar>=95%% same"
    % (len(f0), N, *w(N - len(f0), N))
)
f1 = [i for i, d in byid.items() if d["T1"]["choice"] != d["T0"]["choice"]]
print(
    "I1 T1-option-permute flips vs T0: %d/%d Wilson [%.3f,%.3f] bar<=10%%"
    % (len(f1), N, *w(len(f1), N))
)
f2 = [i for i, d in byid.items() if d["T2"]["choice"] != d["T0"]["choice"]]
print(
    "I2 T2-field-shuffle flips vs T0: %d/%d Wilson [%.3f,%.3f] bar<=10%%"
    % (len(f2), N, *w(len(f2), N))
)
f3 = [i for i, d in byid.items() if d["T3"]["choice"] == d["T3"]["ref"]]
print(
    "I3 T3-negated meaning-flips vs recorded: %d/%d Wilson [%.3f,%.3f] bar modal-agree>=85%%"
    % (len(f3), N, *w(len(f3), N))
)
for t in ["T1", "T2", "T3"]:
    ds = []
    for i, d in byid.items():
        a = d["T0"]
        b = d[t]
        if a["choice"] in b["probabilities"]:
            ds.append(
                abs(b["probabilities"][a["choice"]] - a["probabilities"][a["choice"]])
            )
    print("%s mean|dp|=%.3f n=%d" % (t, sum(ds) / len(ds), len(ds)))
print(
    "recorded refs:",
    {
        c: sum(1 for d in byid.values() if d["T0"]["ref"] == c)
        for c in ("fix_first", "retry_identical")
    },
)
print(
    "T0 choices:",
    {
        c: sum(1 for d in byid.values() if d["T0"]["choice"] == c)
        for c in ("fix_first", "retry_identical")
    },
)
comp = []
for i, d in byid.items():
    r = d["T3"]["ref"]
    comp.append(
        abs(
            d["T3"]["probabilities"].get(r, 0)
            + d["T0"]["probabilities"].get(r, 0)
            - 1.0
        )
    )
print(
    "I3 complement |p_avoid(R)+p_do(R)-1| mean=%.3f max=%.3f bar<=0.15"
    % (sum(comp) / len(comp), max(comp))
)
