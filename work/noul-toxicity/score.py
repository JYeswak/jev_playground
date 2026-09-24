#!/usr/bin/env python3
"""Keyless scorer for bead jev-1kv0. Imports the SciFact metric functions. No key, no network."""

import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SPEC = importlib.util.spec_from_file_location(
    "noul_scifact_score", os.path.join(ROOT, "work/noul-scifact/score.py")
)
sf = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sf)

CUT = 0.5
OP = 0.70
N = 2000
POS = 180
PREV = 0.09
ACC_ALWAYS0 = 0.91
BRIER_BASE = 0.0819
JEV_RUNS = ("jev", "jev-run2", "jev-run3")
GROK_RUNS = ("grok", "grok-run2", "grok-run3")


def load(name):
    path = name if os.path.isabs(name) else os.path.join(HERE, name)
    return [json.loads(line) for line in open(path, encoding="utf-8") if line.strip()]


def probs_for(sample, rows):
    by_i = {}
    for row in rows:
        if {"text", "sentence1", "sentence2"} & row.keys():
            raise SystemExit(f"row {row.get('i')} carries source text")
        by_i[row["i"]] = row
    out = []
    answered = 0
    for item in sample:
        row = by_i.get(item["i"])
        if row is None or "error" in row or "noul" not in row:
            # Far side, as in jev-jzzs row 457: the refusal is incorrect.
            out.append(0.0 if item["label"] == 1 else 1.0)
        else:
            out.append(float(row["noul"]))
            answered += 1
    return out, answered


def mcnemar(a_correct, b_correct):
    a_only = sum(1 for a, b in zip(a_correct, b_correct) if a and not b)
    b_only = sum(1 for a, b in zip(a_correct, b_correct) if b and not a)
    p = sf.binom_two_sided(min(a_only, b_only), a_only + b_only)
    verdict = (
        "WIN"
        if p < sf.ALPHA and a_only > b_only
        else "LOSE"
        if p < sf.ALPHA and b_only > a_only
        else "TIE"
    )
    return a_only, b_only, p, verdict


def side(lo, hi, lower_better=False):
    if lower_better:
        return "WIN" if hi < 0 else "LOSE" if lo > 0 else "TIE"
    return "WIN" if lo > 0 else "LOSE" if hi < 0 else "TIE"


def main():
    sample = load("sample.jsonl")
    y = [row["label"] for row in sample]
    if len(sample) != N or sum(y) != POS:
        print("sample drifted", len(sample), sum(y), file=sys.stderr)
        return 1
    if "--bar" in sys.argv:
        print(
            json.dumps(
                {
                    "n": N,
                    "pos": POS,
                    "acc_always0": ACC_ALWAYS0,
                    "brier_base": BRIER_BASE,
                }
            )
        )
        return 0
    arms = {}
    for name in JEV_RUNS + GROK_RUNS:
        rows = load(f"rows-{name}.jsonl")
        if not rows:
            print(f"missing {name}", file=sys.stderr)
            return 1
        p, answered = probs_for(sample, rows)
        arms[name] = p
        neg = [i for i, lab in enumerate(y) if lab == 0]
        fp = sum(1 for i in neg if p[i] >= OP)
        print(
            f"{name} answered={answered}/{N} auc={sf.auc(p, y):.4f} brier={sf.brier(p, y):.4f} "
            f"ece={sf.ece(p, y):.4f} acc={sf.accuracy(p, y):.4f} fpr={fp}/{len(neg)}"
        )
        if name.startswith("jev"):
            correct = [(v > CUT) == bool(lab) for v, lab in zip(p, y)]
            always = [not bool(lab) for lab in y]
            a, b, pv, verdict = mcnemar(correct, always)
            lo, hi = sf.boot(sf.auc, p, None, y)
            print(
                f"  vs always-non-toxic exact {a}/{b} p={pv:.4g} {verdict}; auc interval [{lo:.4f},{hi:.4f}]"
            )
    holds = {k: 0 for k in ("auc", "brier", "ece", "acc", "fpr")}
    loses = dict(holds)
    for jn in JEV_RUNS:
        for gn in GROK_RUNS:
            jp, gp = arms[jn], arms[gn]
            alo, ahi = sf.boot(sf.auc, jp, gp, y)
            blo, bhi = sf.boot(sf.brier, jp, gp, y)
            elo, ehi = sf.boot(sf.ece, jp, gp, y)
            jc = [(v > CUT) == bool(lab) for v, lab in zip(jp, y)]
            gc = [(v > CUT) == bool(lab) for v, lab in zip(gp, y)]
            ea, eb, ep, ev = mcnemar(jc, gc)
            neg = [i for i, lab in enumerate(y) if lab == 0]
            fa, fb, fp, fv = mcnemar(
                [jp[i] < OP for i in neg], [gp[i] < OP for i in neg]
            )
            verdicts = {
                "auc": side(alo, ahi),
                "brier": side(blo, bhi, True),
                "ece": side(elo, ehi, True),
                "acc": ev,
                "fpr": fv,
            }
            for key, verdict in verdicts.items():
                holds[key] += verdict == "WIN"
                loses[key] += verdict == "LOSE"
            print(
                f"{jn} x {gn} auc {verdicts['auc']} [{alo:.4f},{ahi:.4f}] "
                f"brier {verdicts['brier']} [{blo:.4f},{bhi:.4f}] "
                f"ece {verdicts['ece']} [{elo:.4f},{ehi:.4f}] "
                f"acc {ea}/{eb} p={ep:.4g} {ev} fpr {fa}/{fb} p={fp:.4g} {fv}"
            )
    print("WIN", holds, "LOSE", loses)
    return 0


if __name__ == "__main__":
    sys.exit(main())
