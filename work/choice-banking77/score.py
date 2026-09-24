#!/usr/bin/env python3
"""Scorer for bead jev-k3k. Stdlib only, no key, no network.

Reads subset.jsonl, rows-jev.jsonl, rows-haiku.jsonl (the last row per id that carries a
choice wins; an id with no such row is a failed row and is scored wrong). Prints every number
the receipt docs/demos/upstream-repro/choice-banking77-20260924.md reports, and the verdict
under the bar preregistered there.

Run: python3 work/choice-banking77/score.py
"""

import json
import math
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
THRESHOLDS = (0.5, 0.7, 0.9)
MARGIN_PP = 3.0  # non-inferiority margin, percentage points
ALPHA = 0.05
FEASIBLE = (
    0.5  # an arm below 50% accuracy means the harness, not the model, is measured
)


def load(name):
    path = os.path.join(HERE, name)
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def final_rows(rows):
    """Last answered row per id; ids with only error rows map to their last error row."""
    out = {}
    for r in rows:
        if "choice" in r or r["i"] not in out or "choice" not in out[r["i"]]:
            out[r["i"]] = r
    return out


def wilson(k, n, z=1.959964):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def mcnemar_exact(b, c):
    """Two-sided exact binomial test on discordant pairs (b, c), p = 0.5."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / 2**n
    return min(1.0, 2 * tail)


def nearest_rank(values, q):
    if not values:
        return None
    s = sorted(values)
    return s[max(0, math.ceil(q * len(s)) - 1)]


def peak_confidence(probs):
    """One formula for both arms: peak probability rescaled from uniform (1/k) to 1."""
    vals = list(probs.values())
    total = sum(vals)
    if not vals or total <= 0:
        return 0.0
    k = len(vals)
    return (max(vals) / total - 1 / k) / (1 - 1 / k)


def pct(k, n):
    return f"{100 * k / n:.1f}%" if n else "n/a"


def arm_stats(name, subset, rows):
    fin = final_rows(rows)
    n = len(subset)
    correct = {}
    answered = []
    for item in subset:
        r = fin.get(item["i"])
        ok = bool(r and "choice" in r and r["choice"] == item["intent"])
        correct[item["i"]] = ok
        if r and "choice" in r:
            answered.append(r)
    k = sum(correct.values())
    lo, hi = wilson(k, n)
    lat = [r["latencyMs"] for r in answered]
    tin = sum(r["usage"]["input_tokens"] for r in answered)
    tout = sum(r["usage"]["output_tokens"] for r in answered)
    models = Counter(r.get("model") for r in answered)
    cov = {}
    for field in ("confidence", "peak"):
        for t in THRESHOLDS:
            covered = [
                r
                for r in answered
                if (
                    r["confidence"]
                    if field == "confidence"
                    else peak_confidence(r["probabilities"])
                )
                >= t
            ]
            ck = sum(1 for r in covered if r["choice"] == r["intent"])
            cov[(field, t)] = (len(covered), ck)
    confusions = Counter(
        (r["intent"], r["choice"]) for r in answered if r["choice"] != r["intent"]
    )
    return {
        "name": name,
        "n": n,
        "answered": len(answered),
        "failed": n - len(answered),
        "correct": k,
        "acc": k / n if n else 0.0,
        "wilson": (lo, hi),
        "p50": nearest_rank(lat, 0.5),
        "p95": nearest_rank(lat, 0.95),
        "tokens": (tin, tout),
        "models": dict(models),
        "cov": cov,
        "per_i": correct,
        "confusions": confusions,
    }


def main():
    subset = load("subset.jsonl")
    if not subset:
        print("no subset.jsonl; run sample.py", file=sys.stderr)
        return 2
    counts = Counter(r["intent"] for r in subset)
    majority = sorted(counts, key=lambda c: (-counts[c], c.casefold(), c))[0]
    const_k = counts[majority]
    n = len(subset)
    print(f"corpus: {n} rows, {len(counts)} intents")
    print(f"constant: always-{majority} {const_k}/{n} ({pct(const_k, n)})")

    arms = [
        arm_stats("jev", subset, load("rows-jev.jsonl")),
        arm_stats("haiku", subset, load("rows-haiku.jsonl")),
    ]
    print()
    print(
        "| Arm | Answered | Failed | Correct | Accuracy | Wilson 95% | p50 / p95 ms | Tokens in / out | Model(s) |"
    )
    print("|---|---:|---:|---:|---:|---|---|---|---|")
    for a in arms:
        lo, hi = a["wilson"]
        print(
            f"| {a['name']} | {a['answered']} | {a['failed']} | {a['correct']}/{a['n']} | "
            f"{pct(a['correct'], a['n'])} | {100 * lo:.1f}-{100 * hi:.1f}% | "
            f"{a['p50']} / {a['p95']} | {a['tokens'][0]:,} / {a['tokens'][1]:,} | "
            f"{', '.join(f'{m} x{c}' for m, c in a['models'].items())} |"
        )
    print(
        f"| constant | {n} | 0 | {const_k}/{n} | {pct(const_k, n)} | | | | always-{majority} |"
    )

    for field, title in (
        ("confidence", "Coverage by each arm's returned `confidence` (preregistered)"),
        (
            "peak",
            "Coverage by one formula for both arms, (p_max - 1/10)/(1 - 1/10) (descriptive)",
        ),
    ):
        print()
        print(title)
        print(
            "| Arm | " + " | ".join(f">= {t}: covered, acc" for t in THRESHOLDS) + " |"
        )
        print("|---|" + "---|" * len(THRESHOLDS))
        for a in arms:
            cells = []
            for t in THRESHOLDS:
                c, ck = a["cov"][(field, t)]
                cells.append(
                    f"{c}/{a['n']} ({pct(c, a['n'])}), {ck}/{c} ({pct(ck, c)})"
                )
            print(f"| {a['name']} | " + " | ".join(cells) + " |")

    jev, haiku = arms
    b = sum(1 for i in jev["per_i"] if jev["per_i"][i] and not haiku["per_i"][i])
    c = sum(1 for i in jev["per_i"] if haiku["per_i"][i] and not jev["per_i"][i])
    both = sum(1 for i in jev["per_i"] if jev["per_i"][i] and haiku["per_i"][i])
    p = mcnemar_exact(b, c)
    print()
    print(
        f"paired: both correct {both}, jev-only {b}, haiku-only {c}, McNemar exact p = {p:.3g}"
    )

    for a in arms:
        top = ", ".join(
            f"{t}->{g} x{k}" for (t, g), k in a["confusions"].most_common(5)
        )
        print(f"top confusions {a['name']}: {top or 'none'}")

    print()
    feasible = all(a["acc"] >= FEASIBLE for a in arms)
    diff_pp = 100 * (jev["acc"] - haiku["acc"])
    if not feasible:
        verdict = "NOT-SCORED (an arm is below the 50% feasibility floor)"
    elif jev["correct"] <= const_k:
        verdict = "LOSE (Jev does not beat the constant)"
    elif diff_pp < -MARGIN_PP:
        verdict = (
            f"LOSE (Jev {diff_pp:+.1f} pp vs Haiku, beyond the -{MARGIN_PP} pp margin)"
        )
    elif b > c and p < ALPHA:
        verdict = f"WIN (Jev {diff_pp:+.1f} pp vs Haiku, McNemar p = {p:.3g})"
    else:
        verdict = (
            f"NON-INFERIOR (Jev {diff_pp:+.1f} pp vs Haiku, within -{MARGIN_PP} pp)"
        )
    print(f"verdict: {verdict}")
    print(f"pass: {'PASS' if verdict.startswith(('WIN', 'NON-INFERIOR')) else 'FAIL'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
