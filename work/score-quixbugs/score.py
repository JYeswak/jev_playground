#!/usr/bin/env python3
"""Scorer for bead jev-2wc (QuixBugs, jev-curate code_quality Score, Jev vs Haiku). Stdlib, no key.

Run: python3 work/score-quixbugs/score.py
Rules frozen in docs/demos/upstream-repro/score-quixbugs-20260924.md:
  pair outcome  = W if score(correct) > score(buggy), L if <, T if equal; a program with no answer
                  after the resume pass makes its pair T and enters AUC at 2.0 (the middle level)
  win rate      = (W + T/2) / pairs
  sign test     = exact two-sided binomial on W vs L, ties dropped
  AUC           = Mann-Whitney over all programs (correct = positive), ties averaged
  bootstrap     = resample pairs with replacement, 2000 draws, random.Random(20260924), 95% percentile
  vs Haiku      = McNemar exact on "pair ordered correctly" (strict W), and paired bootstrap of AUC diff
  zero-mass     = a Haiku row whose adapter original_probabilities sum to 0; its pair is dropped from
                  every arm in the "without" scoring
"""

import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ALPHA = 0.05
BOOT = 2000
SEED = 20260924
FLOOR = 3.0  # jev-curate's code_quality min_score (src/presets.rs:152), read on the API's 0-based scale
PRIMARY = (("jev", "Jev jev-1.13.0"), ("haiku", "Haiku 4.5 via adapter"))
DESCRIPTIVE = (
    ("jev-flat", "Jev, jev-curate line-trimmed text"),
    ("jev-asis", "Jev, files as shipped"),
)


def load(path):
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def binom_two_sided(k, n):
    if n == 0:
        return 1.0
    m = min(k, n - k)
    return min(1.0, 2 * sum(math.comb(n, j) for j in range(m + 1)) / 2**n)


def auc(pos, neg):
    if not pos or not neg:
        return float("nan")
    wins = sum((p > q) + 0.5 * (p == q) for p in pos for q in neg)
    return wins / (len(pos) * len(neg))


def pct(xs, q):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, max(0, math.ceil(q * len(xs)) - 1))]


def outcomes(pairs):
    return ["W" if c > b else "L" if c < b else "T" for c, b in pairs]


def boot_ci(stat, n):
    rng = random.Random(SEED)
    vals = sorted(stat([rng.randrange(n) for _ in range(n)]) for _ in range(BOOT))
    return vals[int(0.025 * BOOT)], vals[int(0.975 * BOOT) - 1]


def arm_pairs(names, idx, rows):
    by_i = {r["i"]: r for r in rows if "score" in r}
    out, missing = [], 0
    for n in names:
        c, b = by_i.get(idx[(n, "correct")]), by_i.get(idx[(n, "buggy")])
        if c is None or b is None:
            missing += 1
            out.append((2.0, 2.0))
        else:
            out.append((c["score"], b["score"]))
    return out, missing


def summarize(label, pairs, missing):
    o = outcomes(pairs)
    w, lo, t = o.count("W"), o.count("L"), o.count("T")
    n = len(pairs)
    p = binom_two_sided(w, w + lo)

    def auc_of(ix):
        return auc([pairs[k][0] for k in ix], [pairs[k][1] for k in ix])

    a = auc_of(range(n))
    ci = boot_ci(auc_of, n)
    cs = [c for c, _ in pairs]
    bs = [b for _, b in pairs]
    keep_c = sum(x >= FLOOR for x in cs)
    keep_b = sum(x >= FLOOR for x in bs)
    print(
        f"| {label} | {n} | {w} / {lo} / {t} | {(w + t / 2) / n:.3f} | {p:.3g} | {a:.3f} | {ci[0]:.3f}-{ci[1]:.3f} | "
        f"{sum(cs) / n:.3f} / {sum(bs) / n:.3f} | {keep_c} / {keep_b} | {missing} |"
    )
    return {"w": w, "l": lo, "t": t, "p": p, "auc": a, "ci": ci, "o": o}


HEADER = (
    "| Arm | Pairs | W / L / T | Win rate | Sign p | AUC | AUC 95% | Mean score correct / buggy | "
    f">= {FLOOR} correct / buggy | Unanswered pairs |\n|---|---:|---|---:|---:|---:|---|---|---|---:|"
)


def compare(names, idx, arms, keep):
    ks = [k for k, n in enumerate(names) if n in keep]
    print(HEADER)
    print(
        f"| constant (every program the same score) | {len(ks)} | 0 / 0 / {len(ks)} | 0.500 | 1 | 0.500 | 0.500-0.500 | - | - | 0 |"
    )
    res = {}
    for arm, label in PRIMARY + DESCRIPTIVE:
        if arm in arms:
            pairs = [arms[arm][0][k] for k in ks]
            res[arm] = summarize(
                label, pairs, sum(1 for k in ks if names[k] in arms[arm][2])
            )
    if "jev" in res and "haiku" in res:
        j, h = res["jev"], res["haiku"]
        jo = sum(1 for a, b in zip(j["o"], h["o"]) if a == "W" and b != "W")
        ho = sum(1 for a, b in zip(j["o"], h["o"]) if b == "W" and a != "W")
        pm = binom_two_sided(jo, jo + ho)
        jp = [arms["jev"][0][k] for k in ks]
        hp = [arms["haiku"][0][k] for k in ks]

        def diff(ix):
            return auc([jp[k][0] for k in ix], [jp[k][1] for k in ix]) - auc(
                [hp[k][0] for k in ix], [hp[k][1] for k in ix]
            )

        lo, hi = boot_ci(diff, len(ks))
        acc = (
            "WIN"
            if pm < ALPHA and jo > ho
            else "LOSE"
            if pm < ALPHA and ho > jo
            else "TIE"
        )
        av = "WIN" if lo > 0 else "LOSE" if hi < 0 else "TIE"
        print(
            f"\nJev vs Haiku, pairs ordered correctly: Jev-only {jo}, Haiku-only {ho}, McNemar p = {pm:.3g} -> {acc}"
        )
        print(
            f"Jev vs Haiku, AUC difference {diff(range(len(ks))):+.3f}, 95% {lo:+.3f} to {hi:+.3f} -> {av}"
        )
        sep = j["w"] > j["l"] and j["p"] < ALPHA and j["ci"][0] > 0.5
        lost = "LOSE" in (acc, av)
        print(
            f"bar 1 (Jev separates): W>L {j['w'] > j['l']}, sign p<0.05 {j['p'] < ALPHA}, AUC CI above 0.5 "
            f"{j['ci'][0] > 0.5} -> {'PASS' if sep else 'FAIL'}"
        )
        print(
            f"bar 2 (Jev does not lose to Haiku): {'NO LOSS' if not lost else 'LOSES'}"
        )
        print(f"overall: {'PASS' if sep and not lost else 'FAIL'}")


def main():
    sample = load(os.path.join(HERE, "sample.jsonl"))
    names = sorted({s["name"] for s in sample})
    idx = {(s["name"], s["variant"]): s["i"] for s in sample}
    print(f"sample: {len(sample)} programs, {len(names)} pairs")
    arms = {}
    for arm, _ in PRIMARY + DESCRIPTIVE:
        rows = load(os.path.join(HERE, f"rows-{arm}.jsonl"))
        if not rows:
            continue
        pairs, _ = arm_pairs(names, idx, rows)
        got = {r["i"] for r in rows if "score" in r}
        miss = {
            n
            for n in names
            if idx[(n, "correct")] not in got or idx[(n, "buggy")] not in got
        }
        arms[arm] = (pairs, rows, miss)

    print("\n## All pairs\n")
    compare(names, idx, arms, set(names))

    print(
        "\n| Arm | Answered | Error rows logged | Model(s) | p50 / p95 ms | Tokens in / out | Distinct scores |"
    )
    print("|---|---:|---:|---|---|---|---:|")
    for arm, (_, rows, _) in arms.items():
        got = [r for r in rows if "score" in r]
        lat = [r["latencyMs"] for r in got]
        tin = sum(r["usage"]["input_tokens"] or 0 for r in got)
        tout = sum(r["usage"]["output_tokens"] or 0 for r in got)
        print(
            f"| {arm} | {len({r['i'] for r in got})}/{len(sample)} | {sum('error' in r for r in rows)} | "
            f"{', '.join(sorted({r['model'] for r in got}))} | {pct(lat, 0.5)} / {pct(lat, 0.95)} | "
            f"{tin:,} / {tout:,} | {len({round(r['score'], 4) for r in got})} |"
        )

    if "haiku" in arms:
        rows = [r for r in arms["haiku"][1] if "score" in r]
        recorded = [r for r in rows if "probabilityError" in r]
        rescaled = {r["i"] for r in recorded if r["probabilityError"] is not None}
        zero = {
            r["i"]
            for r in recorded
            if isinstance(r.get("originalProbabilities"), dict)
            and sum(r["originalProbabilities"].values()) == 0
        }
        name_of = {s["i"]: s["name"] for s in sample}
        print(
            f"\nHaiku adapter debug (jev-mly): recorded on {len(recorded)}/{len(rows)} rows; probability_errors set "
            f"on {len(rescaled)}; zero-mass (original sum 0) on {len(zero)}"
        )
        for title, drop in (("zero-mass", zero), ("any probability_errors", rescaled)):
            gone = {name_of[i] for i in drop}
            if gone:
                print(
                    f"\n## Without the {len(gone)} pairs holding a {title} Haiku row ({', '.join(sorted(gone))})\n"
                )
                compare(names, idx, arms, set(names) - gone)
            else:
                print(
                    f"Without {title} rows: identical to All pairs (0 pairs dropped)."
                )
    return 0


if __name__ == "__main__":
    sys.exit(main())
