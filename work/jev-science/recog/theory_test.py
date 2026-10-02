#!/usr/bin/env python3
"""Part A retest: does RECOGNITION vs FORECASTING predict WIN vs NON-WIN?
Reads committed codes.csv (no outcomes), joins verdicts from table_draft.json +
new_verdicts.csv, prints 2x2 tables + Fisher exact (two-sided) + OR (Haldane) +
risk difference (Newcombe 95% CI). Recompute: python3 work/jev-science/recog/theory_test.py
"""

import csv
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
J = "/Users/josh/Developer/jev"
codes = {}
with open(os.path.join(HERE, "codes.csv")) as fh:
    for row in csv.DictReader(fh):
        codes[row["id"]] = row["code"]
table = json.load(open(os.path.join(J, "work/jev-science/table_draft.json")))
verdict = {x["id"]: x["verdict"] for x in table}
with open(os.path.join(HERE, "new_verdicts.csv")) as fh:
    for row in csv.DictReader(fh):
        verdict[row["id"]] = row["verdict"]
assert set(codes) == set(verdict), set(codes) ^ set(verdict)
flag = {x["id"]: x.get("future_counterfactual") for x in table}
agree = sum(
    1
    for i in table
    if ((codes[i["id"]] == "F") == bool(i.get("future_counterfactual")))
)
print("n=%d agree-with-table-flag=%d/%d" % (len(codes), agree, len(table)))
print(
    "disagreements:",
    [
        i["id"]
        for i in table
        if (codes[i["id"]] == "F") != bool(i.get("future_counterfactual"))
    ],
)


def fisher(a, b, c, d):
    # two-sided Fisher on [[a,b],[c,d]] via hypergeometric doubling
    n1, n2, m1 = a + b, c + d, a + c
    n = n1 + n2

    def hg(k):
        return math.comb(n1, k) * math.comb(n2, m1 - k) / math.comb(n, m1)

    p_obs = hg(a)
    return sum(
        hg(k) for k in range(max(0, m1 - n2), min(n1, m1) + 1) if hg(k) <= p_obs + 1e-12
    )


def or_haldane(a, b, c, d):
    a1, b1, c1, d1 = a + 0.5, b + 0.5, c + 0.5, d + 0.5
    OR = (a1 * d1) / (b1 * c1)
    se = math.sqrt(1 / a1 + 1 / b1 + 1 / c1 + 1 / d1)
    lo = math.exp(math.log(OR) - 1.96 * se)
    hi = math.exp(math.log(OR) + 1.96 * se)
    return OR, lo, hi


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    den = 1 + z * z / n
    c = p + z * z / (2 * n)
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0, (c - m) / den), min(1, (c + m) / den))


def newcombe(a, n1, c, n2):
    p1, p2 = a / n1, c / n2
    l1, u1 = wilson(a, n1)
    l2, u2 = wilson(c, n2)
    rd = p1 - p2
    lo = rd - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2)
    hi = rd + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)
    return rd, lo, hi


def report(name, pos):
    # pos(id) True means event; rows R/F
    a = sum(1 for i in codes if codes[i] == "R" and pos(i))
    b = sum(1 for i in codes if codes[i] == "R" and not pos(i))
    c = sum(1 for i in codes if codes[i] == "F" and pos(i))
    d = sum(1 for i in codes if codes[i] == "F" and not pos(i))
    p = fisher(a, b, c, d)
    OR, olo, ohi = or_haldane(a, b, c, d)
    rd, rlo, rhi = newcombe(a, a + b, c, c + d)
    print(
        "%s 2x2 [[R-event %d, R-no %d],[F-event %d, F-no %d]] p=%.4f OR=%.2f [%.2f,%.2f] RD=%.3f [%.3f,%.3f]"
        % (name, a, b, c, d, p, OR, olo, ohi, rd, rlo, rhi)
    )


report("PRIMARY win-vs-nonwin  ", lambda i: verdict[i] == "win")
report("SECONDARY loss-vs-rest ", lambda i: verdict[i] == "loss")
report("SECONDARY winTie-vs-loss", lambda i: verdict[i] in ("win", "tie"))
own = {i for i in codes if i not in ("R86b", "R89b", "R90b")}
sub = {i: codes[i] for i in own}
a = sum(1 for i in sub if sub[i] == "R" and verdict[i] == "win")
b = sum(1 for i in sub if sub[i] == "R" and verdict[i] != "win")
c = sum(1 for i in sub if sub[i] == "F" and verdict[i] == "win")
d = sum(1 for i in sub if sub[i] == "F" and verdict[i] != "win")
p = fisher(a, b, c, d)
print(
    "SENSITIVITY own-vein-only win-vs-nonwin [[%d,%d],[%d,%d]] p=%.4f" % (a, b, c, d, p)
)
