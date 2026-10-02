#!/usr/bin/env python3
"""Score pslq H4 temporal confirm (reads committed rows).
Rebuilds FROZEN command table (rows.jsonl + jobs.json, first_token verbatim),
H4 metrics at frozen cut 0.04, table at cut matched to H4 precision (fallback:
matched flag rate), paired McNemar on disagreements.
Recompute: python3 work/pslq-confirm/score_confirm.py
"""

import hashlib
import json
import math
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
J = "/Users/josh/Developer/jev"
SKIP = {
    "cd",
    "sleep",
    "echo",
    "export",
    "set",
    "for",
    "if",
    "while",
    "true",
    "false",
    ":",
    "source",
    ".",
}


def first_token(cmd):
    s = (cmd or "").strip().replace("\n", " ")
    s = re.sub(r"\s+", " ", s)
    parts = re.split(r"&&|\|\||;|\|", s)
    for part in parts:
        toks = part.strip().split()
        toks = [t for t in toks if not re.match(r"^[A-Z_][A-Z0-9_]*=.*$", t)]
        if toks and toks[0] not in SKIP:
            return toks[0].split("/")[-1]
    return "(none)"


def grp_sync(cmd):
    return "cmd:" + hashlib.sha256((cmd or "").encode()).hexdigest()[:12]


sync = [
    json.loads(l) for l in open(os.path.join(J, "var/agent-tmp/lrpred-work/rows.jsonl"))
]
jobs = json.load(open(os.path.join(J, "var/agent-tmp/zezf/jobs.json")))
rows = []
for r in sync:
    rows.append(
        (first_token(r["cmd"]), r["wall_ms"] > 120000, grp_sync(r["cmd"] or ""))
    )
for jid, e in jobs.items():
    sess = sorted(e["sessions"])[0] if e["sessions"] else jid
    rows.append((first_token(e["label"]), e["max_ms"] > 120000, "sess:" + sess))
groups = sorted(set(g for _, _, g in rows))
test_g = set(
    g for g in groups if int(hashlib.sha256(g.encode()).hexdigest(), 16) % 5 == 0
)
train = [r for r in rows if r[2] not in test_g]
stat = {}
for tok, p, _ in train:
    c, k = stat.get(tok, (0, 0))
    stat[tok] = (c + 1, k + (1 if p else 0))
table = {t: k / c for t, (c, k) in stat.items()}
print("frozen table: train=%d tokens=%d" % (len(train), len(table)))
rows_c = json.load(open(os.path.join(HERE, "confirm_rows.jsonl")))
sample = [r for r in rows_c if r["phase"] == "held"]
print(
    "confirm held n=%d pos=%d"
    % (len(sample), sum(1 for r in sample if r["label"] == "pos"))
)
tp = fn = fp = tn = 0
for r in sample:
    if r["status"] != "scored":
        continue
    pred = r["pred"]
    if r["label"] == "pos" and pred == "long":
        tp += 1
    elif r["label"] == "pos":
        fn += 1
    elif pred == "long":
        fp += 1
    else:
        tn += 1


def wilson(k, n):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    den = 1 + 3.8416 / n
    c = p + 3.8416 / (2 * n)
    m = 1.96 * math.sqrt(p * (1 - p) / n + 3.8416 / (4 * n * n))
    return (max(0, (c - m) / den), min(1, (c + m) / den))


n = tp + fn + fp + tn
rec = tp / (tp + fn)
prec = tp / (tp + fp) if tp + fp else 0.0
print(
    "H4 tp=%d fn=%d fp=%d tn=%d rec=%.3f %s prec=%.3f flagrate=%.3f"
    % (tp, fn, fp, tn, rec, wilson(tp, tp + fn), prec, (tp + fp) / n)
)
# table at matched precision (fallback matched flag rate)
tscores = [table.get(r["tok"], 0.0) for r in sample]
best = None
for tc in sorted(set(tscores)):
    t2 = t3 = f2 = t4 = 0
    for r, s in zip(sample, tscores):
        if r["status"] != "scored":
            continue
        pr = "long" if s >= tc else "short"
        if r["label"] == "pos" and pr == "long":
            t2 += 1
        elif r["label"] == "pos":
            t3 += 1
        elif pr == "long":
            f2 += 1
        else:
            t4 += 1
    tp2 = t2 / (t2 + t3) if t2 + t3 else 0
    if abs(tp2 - prec) < 1e-9:
        best = (tc, t2, t3, f2, t4, "precision")
        break
if best is None:
    fr = (tp + fp) / n
    cand = [
        (
            abs(
                (
                    sum(
                        1
                        for r, s in zip(sample, tscores)
                        if r["status"] == "scored" and s >= tc
                    )
                    / n
                )
                - fr
            ),
            tc,
        )
        for tc in set(tscores)
    ]
    _, tc = min(cand)
    t2 = t3 = f2 = t4 = 0
    for r, s in zip(sample, tscores):
        if r["status"] != "scored":
            continue
        pr = "long" if s >= tc else "short"
        if r["label"] == "pos" and pr == "long":
            t2 += 1
        elif r["label"] == "pos":
            t3 += 1
        elif pr == "long":
            f2 += 1
        else:
            t4 += 1
    best = (tc, t2, t3, f2, t4, "flagrate")
tc, t2, t3, f2, t4, mode = best
trec = t2 / (t2 + t3) if t2 + t3 else 0
print(
    "TABLE@%s cut=%.4f tp=%d fn=%d fp=%d tn=%d rec=%.3f"
    % (mode, tc, t2, t3, f2, t4, trec)
)
# paired McNemar on disagreements (H4 vs table)
b = c = 0
for r, s in zip(sample, tscores):
    if r["status"] != "scored":
        continue
    hp = (r["pred"] == "long") == (r["label"] == "pos")
    tp_ = (s >= tc) == (r["label"] == "pos")
    if hp and not tp_:
        b += 1
    elif tp_ and not hp:
        c += 1
from math import erf, sqrt

if b + c == 0:
    pval = 1.0
else:
    z = (abs(b - c) - 1) / sqrt(b + c)
    pval = 1 - erf(z / sqrt(2))
print(
    "paired McNemar H4-correct/Table-wrong=%d Table-correct/H4-wrong=%d p=%.4f"
    % (b, c, pval)
)
print(
    "CONFIRM-HOLD iff rec>=0.40 AND table-matched H4 rec >= table rec with p<0.05 -> %s"
    % ("HOLD" if rec >= 0.40 and trec <= rec and pval < 0.05 and b > c else "NOT-HELD")
)
