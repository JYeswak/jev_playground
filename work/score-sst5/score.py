#!/usr/bin/env python3
"""Scorer for bead jev-zui (SST-5, Jev Score vs Haiku). Stdlib only, no key, no network.

Run: python3 work/score-sst5/score.py
Reads sample.jsonl and rows-{jev,haiku}.jsonl beside this file and prints the receipt tables.
Rules frozen in docs/demos/upstream-repro/score-sst5-20260924.md:
  level      = floor(expected score + 0.5), clamped to 0..4 (primary); argmax level also reported,
               ties broken toward the lower index
  failed row = scored incorrect, absolute error max(y, 4 - y) (the worst possible for that row)
  paired     = McNemar exact (two-sided binomial on discordant exact-correct pairs);
               MAE paired by an exact two-sided sign test on per-row absolute errors (ties dropped)
"""

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LEVELS = 5
ALPHA = 0.05


def load_jsonl(path):
    if not os.path.exists(path):
        return []
    return [json.loads(line) for line in open(path) if line.strip()]


def rounded(x):
    return min(LEVELS - 1, max(0, math.floor(x + 0.5)))


def argmax(probs):
    best = max(probs[str(k)] for k in range(LEVELS))
    return min(k for k in range(LEVELS) if probs[str(k)] == best)


def binom_two_sided(k, n):
    """Exact two-sided binomial p at 0.5: 2 * P(X <= min(k, n-k)), capped at 1."""
    if n == 0:
        return 1.0
    m = min(k, n - k)
    tail = sum(math.comb(n, j) for j in range(m + 1)) / 2**n
    return min(1.0, 2 * tail)


def wilson(k, n, z=1.959963984540054):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)


def pct(xs, q):
    xs = sorted(xs)
    if not xs:
        return float("nan")
    return xs[min(len(xs) - 1, max(0, math.ceil(q * len(xs)) - 1))]


def arm_preds(sample, rows):
    """Last answered row per sample id; missing or failed rows become None."""
    by_i = {}
    for r in rows:
        if "score" in r:
            by_i[r["i"]] = r
    return [by_i.get(s["i"]) for s in sample]


def evaluate(sample, preds, mode):
    """Per-row (correct, abs_error) under mode 'round' or 'argmax'."""
    out = []
    for s, p in zip(sample, preds):
        y = s["label"]
        if p is None:
            out.append((False, max(y, LEVELS - 1 - y), None))
            continue
        lv = rounded(p["score"]) if mode == "round" else argmax(p["probabilities"])
        out.append((lv == y, abs(lv - y), lv))
    return out


def constant(sample, level):
    return [(s["label"] == level, abs(level - s["label"]), level) for s in sample]


def paired(a, b):
    """Returns (a_only, b_only, p_mcnemar, a_better_mae, b_better_mae, p_sign)."""
    a_only = sum(1 for x, y in zip(a, b) if x[0] and not y[0])
    b_only = sum(1 for x, y in zip(a, b) if y[0] and not x[0])
    ab = sum(1 for x, y in zip(a, b) if x[1] < y[1])
    bb = sum(1 for x, y in zip(a, b) if y[1] < x[1])
    return (
        a_only,
        b_only,
        binom_two_sided(a_only, a_only + b_only),
        ab,
        bb,
        binom_two_sided(ab, ab + bb),
    )


def verdict(a_better, b_better, p):
    if p < ALPHA and a_better > b_better:
        return "WIN"
    if p < ALPHA and b_better > a_better:
        return "LOSE"
    return "TIE"


def summary(name, ev):
    n = len(ev)
    k = sum(1 for c, _, _ in ev if c)
    lo, hi = wilson(k, n)
    mae = sum(e for _, e, _ in ev) / n
    return name, k, n, lo, hi, mae


def main():
    sample = load_jsonl(os.path.join(HERE, "sample.jsonl"))
    counts = [sum(1 for s in sample if s["label"] == k) for k in range(LEVELS)]
    majority = max(range(LEVELS), key=lambda k: (counts[k], -k))
    print(
        f"sample: {len(sample)} rows, label counts {counts}, majority level {majority}"
    )

    arms = {}
    for arm in ("jev", "haiku"):
        rows = load_jsonl(os.path.join(HERE, f"rows-{arm}.jsonl"))
        preds = arm_preds(sample, rows)
        arms[arm] = {"preds": preds, "rows": rows}

    table = [
        summary(f"constant: majority (always {majority})", constant(sample, majority)),
        summary("constant: middle (always 2)", constant(sample, 2)),
    ]
    ev = {}
    for arm, label in (("jev", "Jev jev-1.13.0"), ("haiku", "Haiku 4.5 via adapter")):
        preds = arms[arm]["preds"]
        answered = sum(1 for p in preds if p is not None)
        if answered == 0:
            continue
        ev[arm] = evaluate(sample, preds, "round")
        table.append(summary(f"{label} (rounded expected)", ev[arm]))
        table.append(summary(f"{label} (argmax)", evaluate(sample, preds, "argmax")))
        raw = [
            abs(p["score"] - s["label"]) for s, p in zip(sample, preds) if p is not None
        ]
        lat = [p["latencyMs"] for p in preds if p is not None]
        tin = sum(p["usage"]["input_tokens"] or 0 for p in preds if p is not None)
        tout = sum(p["usage"]["output_tokens"] or 0 for p in preds if p is not None)
        models = sorted({p["model"] for p in preds if p is not None})
        errs = sum(1 for r in arms[arm]["rows"] if "error" in r)
        arms[arm]["meta"] = (
            answered,
            models,
            pct(lat, 0.5),
            pct(lat, 0.95),
            tin,
            tout,
            errs,
            sum(raw) / len(raw),
        )

    print("\n| Arm | Exact correct | Accuracy | Wilson 95% | MAE (levels) |")
    print("|---|---:|---:|---|---:|")
    for name, k, n, lo, hi, mae in table:
        print(f"| {name} | {k}/{n} | {k / n:.1%} | {lo:.1%}-{hi:.1%} | {mae:.3f} |")

    if arms["jev"].get("meta") or arms["haiku"].get("meta"):
        print(
            "\n| Arm | Answered | Model(s) | p50 / p95 latency ms | Tokens in / out | Error rows logged | MAE of raw expected score |"
        )
        print("|---|---:|---|---|---|---:|---:|")
        for arm in ("jev", "haiku"):
            m = arms[arm].get("meta")
            if m:
                print(
                    f"| {arm} | {m[0]}/{len(sample)} | {', '.join(m[1])} | {m[2]} / {m[3]} | "
                    f"{m[4]:,} / {m[5]:,} | {m[6]} | {m[7]:.3f} |"
                )

    if "jev" in ev:
        print(
            "\nPaired on the same rows (Jev rounded vs X): exact-correct McNemar, |error| sign test"
        )
        print(
            "| Jev vs | Jev-only correct | X-only correct | McNemar p | Accuracy verdict | Jev lower err | X lower err | Sign p | MAE verdict |"
        )
        print("|---|---:|---:|---:|---|---:|---:|---:|---|")
        others = [
            (f"always {majority}", constant(sample, majority)),
            ("always 2", constant(sample, 2)),
        ]
        if "haiku" in ev:
            others.append(("Haiku", ev["haiku"]))
        verdicts = {}
        for name, other in others:
            ao, bo, pm, ab, bb, ps = paired(ev["jev"], other)
            va, vm = verdict(ao, bo, pm), verdict(ab, bb, ps)
            verdicts[name] = (va, vm)
            print(
                f"| {name} | {ao} | {bo} | {pm:.2e} | {va} | {ab} | {bb} | {ps:.2e} | {vm} |"
            )

        beats_constants = all(verdicts[n] == ("WIN", "WIN") for n, _ in others[:2])
        print(
            f"\nbar: beats both constants on accuracy AND MAE: {'PASS' if beats_constants else 'FAIL'}"
        )
        if "Haiku" in verdicts:
            va, vm = verdicts["Haiku"]
            lost = "LOSE" in (va, vm)
            print(
                f"bar: vs Haiku accuracy {va}, MAE {vm}; loses to incumbent: {'YES' if lost else 'NO'}"
            )
            print(f"overall: {'PASS' if beats_constants and not lost else 'FAIL'}")

    for arm in ("jev", "haiku"):
        if arm not in ev:
            continue
        preds = arms[arm]["preds"]
        rowsc = [
            (p["confidence"], s["i"], c)
            for (c, _, _), p, s in zip(ev[arm], preds, sample)
            if p is not None
        ]
        rowsc.sort(key=lambda t: (-t[0], t[1]))
        print(
            f"\nCoverage by confidence, {arm} (answered rows ranked by the returned confidence; descriptive)"
        )
        print("| Coverage | Rows | Accuracy | Lowest confidence kept |")
        print("|---:|---:|---:|---:|")
        for cov in (0.25, 0.5, 0.75, 1.0):
            m = max(1, round(cov * len(rowsc)))
            kept = rowsc[:m]
            acc = sum(1 for t in kept if t[2]) / m
            print(f"| {cov:.0%} | {m} | {acc:.1%} | {kept[-1][0]:.3f} |")
        print(f"\nCalibration by confidence bin, {arm}")
        print("| Confidence bin | Rows | Mean confidence | Accuracy |")
        print("|---|---:|---:|---:|")
        for lo in (0.0, 0.2, 0.4, 0.6, 0.8):
            hi = lo + 0.2
            b = [t for t in rowsc if lo <= t[0] < hi or (hi >= 1.0 and t[0] == 1.0)]
            if b:
                mc = sum(t[0] for t in b) / len(b)
                acc = sum(1 for t in b if t[2]) / len(b)
                print(f"| {lo:.1f}-{hi:.1f} | {len(b)} | {mc:.3f} | {acc:.1%} |")

        conf = [[0] * LEVELS for _ in range(LEVELS)]
        for (_, _, lv), s in zip(ev[arm], sample):
            if lv is not None:
                conf[s["label"]][lv] += 1
        print(f"\nConfusion (rows = truth 0..4, cols = rounded level 0..4), {arm}")
        for k in range(LEVELS):
            print(f"  {k}: {conf[k]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
