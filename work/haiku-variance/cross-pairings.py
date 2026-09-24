#!/usr/bin/env python3
"""Cross-pairings for SST-5 and Banking77: every Jev run against every Haiku run (9 per unit).

jev-qbc re-ran the Jev arm twice (rows-jev-run2/-run3.jsonl) against Haiku run 1, and jev-x5k
re-ran the Haiku arm twice (rows-haiku-run2/-run3.jsonl) against Jev run 1. Neither ran the four
crossed pairings (Jev run 2 or 3 vs Haiku run 2 or 3). This script scores all nine from committed
rows, using each unit's own committed functions imported from its score.py:
  SST-5 Score      work/score-sst5/score.py        (jev-zui): MAE sign test and accuracy McNemar
  Banking77 Choice work/choice-banking77/score.py  (jev-k3k): McNemar and the unit's verdict rule

DESCRIPTIVE: the jev-x5k bar did not preregister cross-pairings. Receipt section: "Cross-pairings
(9 per unit)" in docs/demos/upstream-repro/haiku-variance-20260924.md.

Run: python3 work/haiku-variance/cross-pairings.py
Exit 1 unless every pairing a committed receipt already reports reproduces its committed verdict and
counts (run 1 x run 1 included). Stdlib only, no key, no network.
"""

import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(HERE)
JEV = ("rows-jev.jsonl", "rows-jev-run2.jsonl", "rows-jev-run3.jsonl")
HAIKU = ("rows-haiku.jsonl", "rows-haiku-run2.jsonl", "rows-haiku-run3.jsonl")

# Pairings already committed, as (jev run, haiku run) -> the cell their receipt states.
# SST-5 MAE sign test: score-sst5-20260924.md (1x1), jev-variance-20260924.md:87 (2x1, 3x1: p only),
# haiku-variance-20260924.md:109 (1x2, 1x3). Banking77 McNemar: choice-banking77-20260924.md (1x1),
# jev-variance-20260924.md:89 (2x1, 3x1: p only), haiku-variance-20260924.md:116 (1x2, 1x3).
SST5_COMMITTED = {
    (1, 1): ((109, 75), "0.0148", "WIN"),
    (2, 1): (None, "0.0403", "WIN"),
    (3, 1): (None, "0.0190", "WIN"),
    (1, 2): ((118, 72), "0.0010", "WIN"),
    (1, 3): ((112, 72), "0.0039", "WIN"),
}
B77_COMMITTED = {
    (1, 1): ((25, 3), "2.7e-05", "WIN"),
    (2, 1): (None, "2.7e-05", "WIN"),
    (3, 1): (None, "3.0e-06", "WIN"),
    (1, 2): ((23, 4), "3.1e-04", "WIN"),
    (1, 3): ((24, 2), "1.1e-05", "WIN"),
}


def unit(dirname):
    spec = importlib.util.spec_from_file_location(
        f"score_{dirname.replace('-', '_')}", os.path.join(WORK, dirname, "score.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def rows(dirname, name):
    return [
        json.loads(line)
        for line in open(os.path.join(WORK, dirname, name))
        if line.strip()
    ]


def sst5():
    m = unit("score-sst5")
    d = "score-sst5"
    sample = m.load_jsonl(os.path.join(WORK, d, "sample.jsonl"))
    evs = {
        name: m.evaluate(sample, m.arm_preds(sample, rows(d, name)), "round")
        for name in JEV + HAIKU
    }
    out = {}
    for j, jn in enumerate(JEV, 1):
        for h, hn in enumerate(HAIKU, 1):
            ao, bo, pm, ab, bb, ps = m.paired(evs[jn], evs[hn])
            out[(j, h)] = {
                "mae": (ab, bb, ps, m.verdict(ab, bb, ps)),
                "acc": (ao, bo, pm, m.verdict(ao, bo, pm)),
            }
    return out


def banking():
    m = unit("choice-banking77")
    subset = m.load("subset.jsonl")
    counts = {}
    for it in subset:
        counts[it["intent"]] = counts.get(it["intent"], 0) + 1
    const_k = max(counts.values())
    stats = {name: m.arm_stats(name, subset, m.load(name)) for name in JEV + HAIKU}
    out = {}
    for j, jn in enumerate(JEV, 1):
        for h, hn in enumerate(HAIKU, 1):
            jv, hv = stats[jn], stats[hn]
            b = sum(1 for i in jv["per_i"] if jv["per_i"][i] and not hv["per_i"][i])
            c = sum(1 for i in jv["per_i"] if hv["per_i"][i] and not jv["per_i"][i])
            p = m.mcnemar_exact(b, c)
            # The unit's verdict rule, as jev-k3k and jev-x5k apply it.
            if not (jv["acc"] >= m.FEASIBLE and hv["acc"] >= m.FEASIBLE):
                verdict = "NOT-SCORED"
            elif (
                jv["correct"] <= const_k or 100 * (jv["acc"] - hv["acc"]) < -m.MARGIN_PP
            ):
                verdict = "LOSE"
            elif b > c and p < m.ALPHA:
                verdict = "WIN"
            else:
                verdict = "NON-INFERIOR"
            out[(j, h)] = {
                "mc": (b, c, p, verdict),
                "jev": jv["correct"],
                "haiku": hv["correct"],
            }
    return out


def check(label, got, committed, fmt):
    """Committed cells must reproduce: verdict exactly, counts exactly where the receipt gives them,
    and p within 6% of the receipt's rounded value. Exact p is fixed by the counts; the tolerance
    only absorbs rounding. Haiku-variance:116 prints 1.1e-5 for 24 / 2, whose exact p is 1.049e-5
    (double rounding via the scorer's 1.05e-05), so a string compare would fail on rounding alone."""
    bad = []
    for key, (counts, p_txt, verdict) in committed.items():
        a, b, p, v = got[key]
        ref = float(p_txt)
        if (
            v != verdict
            or abs(p - ref) > 0.06 * ref
            or (counts is not None and (a, b) != counts)
        ):
            bad.append(
                f"{label} jev run {key[0]} x haiku run {key[1]}: got {a}/{b} p={fmt(p)} {v}, "
                f"committed {counts} p={p_txt} {verdict}"
            )
    return bad


def main():
    s, b = sst5(), banking()
    print("DESCRIPTIVE: cross-pairings were not preregistered in the jev-x5k bar.\n")
    print(
        "SST-5 (500), Jev run x Haiku run: MAE sign test (Jev lower / Haiku lower) and accuracy McNemar"
    )
    print(
        "| Jev run | Haiku run | MAE sign test | p | verdict | accuracy McNemar | p | verdict | committed |"
    )
    print("|---|---|---|---:|---|---|---:|---|---|")
    for (j, h), r in sorted(s.items()):
        ab, bb, ps, vs = r["mae"]
        ao, bo, pm, va = r["acc"]
        print(
            f"| {j} | {h} | {ab} / {bb} | {ps:.4f} | {vs} | {ao} / {bo} | {pm:.3f} | {va} | "
            f"{'yes' if (j, h) in SST5_COMMITTED else 'no, new'} |"
        )
    mae_wins = sum(1 for r in s.values() if r["mae"][3] == "WIN")
    acc_lose = sum(1 for r in s.values() if r["acc"][3] == "LOSE")
    print(f"SST-5 MAE WIN in {mae_wins}/9 pairings; accuracy LOSE in {acc_lose}/9\n")
    print(
        "Banking77 10-intent (400), Jev run x Haiku run: McNemar (Jev-only / Haiku-only correct)"
    )
    print("| Jev run | Haiku run | Jev | Haiku | McNemar | p | verdict | committed |")
    print("|---|---|---:|---:|---|---:|---|---|")
    for (j, h), r in sorted(b.items()):
        bc, cc, p, v = r["mc"]
        print(
            f"| {j} | {h} | {r['jev']} | {r['haiku']} | {bc} / {cc} | {p:.1e} | {v} | "
            f"{'yes' if (j, h) in B77_COMMITTED else 'no, new'} |"
        )
    b_wins = sum(1 for r in b.values() if r["mc"][3] == "WIN")
    print(f"Banking77 McNemar WIN in {b_wins}/9 pairings\n")

    bad = check(
        "SST-5",
        {k: v["mae"] for k, v in s.items()},
        SST5_COMMITTED,
        lambda p: f"{p:.4f}",
    )
    bad += check(
        "Banking77",
        {k: v["mc"] for k, v in b.items()},
        B77_COMMITTED,
        lambda p: f"{p:.1e}",
    )
    if bad:
        print("FAIL: committed pairings do not reproduce:")
        for line in bad:
            print("  " + line)
        return 1
    print(
        f"committed pairings reproduce: {len(SST5_COMMITTED)}/5 SST-5, {len(B77_COMMITTED)}/5 Banking77"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
