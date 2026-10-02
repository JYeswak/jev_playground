#!/usr/bin/env python3
"""Score recog-cand held rows (committed). Recompute: python3 work/recog-cands/score_held.py
Bars: A acc>=0.95 AND FPR<=0.10 (baseline regex 0.900); B acc>=0.82 AND FPR<=0.10 (baseline local 0.767).
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
for name, fname, acc_bar in (("A", "a_rows.jsonl", 0.95), ("B", "b_rows.jsonl", 0.82)):
    rows = json.load(open(os.path.join(HERE, fname)))
    held = [r for r in rows if r["phase"] == "held" and r["status"] == "ok"]
    tp = fn = fp = tn = 0
    for r in held:
        g, p = r["label"], r["decision"]
        if g == "pos" and p == "pos":
            tp += 1
        elif g == "pos":
            fn += 1
        elif p == "pos":
            fp += 1
        else:
            tn += 1
    n = len(held)
    acc = (tp + tn) / n
    fpr = fp / (fp + tn)
    print(
        "%s tp=%d fn=%d fp=%d tn=%d acc=%.3f fpr=%.3f bar(acc>=%.2f,fpr<=0.10) -> %s"
        % (
            name,
            tp,
            fn,
            fp,
            tn,
            acc,
            fpr,
            acc_bar,
            "PASS" if acc >= acc_bar and fpr <= 0.10 else "FAIL",
        )
    )
for name, fname in (("B-fresh", "b_rows.jsonl"),):
    rows = json.load(open(os.path.join(HERE, fname)))
    fresh = [r for r in rows if r["phase"] == "fresh" and r["status"] == "ok"]
    tp = fn = fp = tn = 0
    for r in fresh:
        g, p = r["label"], r["decision"]
        if g == "pos" and p == "pos":
            tp += 1
        elif g == "pos":
            fn += 1
        elif p == "pos":
            fp += 1
        else:
            tn += 1
    n = len(fresh)
    fpr = fp / (fp + tn)
    rec = tp / (tp + fn)
    print(
        "%s tp=%d fn=%d fp=%d tn=%d FPR=%.3f recall=%.3f LOCK-C([0.05,0.40],>=0.80) -> %s"
        % (
            name,
            tp,
            fn,
            fp,
            tn,
            fpr,
            rec,
            "PASS" if 0.05 <= fpr <= 0.40 and rec >= 0.80 else "FAIL",
        )
    )
