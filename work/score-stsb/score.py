#!/usr/bin/env python3
"""Keyless scorer for bead jev-jzzs. Stdlib only. No key, no network.

The bar is docs/demos/upstream-repro/score-stsb-20260924.md. --bar checks the
committed labels against the floors fixed there and exits. A full run scores
every Jev run against every grok run.
"""

import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ALPHA = 0.05
LEVELS = 6
BOOT = 2000
BOOT_SEED = 20260924
N = 1500
# Floors computed from the pinned labels before any model call.
MEAN = 2.363908
MODE = 3
ROUNDED = (236, 241, 266, 353, 276, 128)
EXACT_MEAN = 266
EXACT_MODE = 353
MAE_MEAN = 1.293179
MAE_MODE = 1.339955
JEV_RUNS = ("jev", "jev-run2", "jev-run3")
GROK_RUNS = ("grok", "grok-run2", "grok-run3")
TEXT_KEYS = {"sentence1", "sentence2", "text", "state"}


def load_jsonl(path):
    if not os.path.exists(path):
        return []
    return [json.loads(line) for line in open(path, encoding="utf-8") if line.strip()]


def rounded(x):
    return min(LEVELS - 1, max(0, math.floor(x + 0.5)))


def binom_two_sided(k, n):
    """Exact two-sided binomial p at 0.5: 2 * P(X <= min(k, n-k)), capped at 1."""
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(min(k, n - k) + 1)) / (2**n)
    return min(1.0, 2 * tail)


def verdict(better, worse, p):
    if p < ALPHA and better > worse:
        return "WIN"
    if p < ALPHA and worse > better:
        return "LOSE"
    return "TIE"


def ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    out = [0.0] * len(xs)
    i = 0
    while i < len(xs):
        j = i
        while j + 1 < len(xs) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2 + 1
        for k in range(i, j + 1):
            out[order[k]] = avg
        i = j + 1
    return out


def pearson(a, b):
    n = len(a)
    ma = sum(a) / n
    mb = sum(b) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    da = math.sqrt(sum((x - ma) ** 2 for x in a))
    db = math.sqrt(sum((y - mb) ** 2 for y in b))
    if da == 0 or db == 0:
        return None
    return num / (da * db)


def spearman(pred, gold):
    return pearson(ranks(pred), ranks(gold))


def failed_score(gold):
    return 0.0 if gold >= 2.5 else 5.0


def arm_preds(labels, rows):
    """Last answered row per id. Missing or failed becomes the far endpoint."""
    by_i = {}
    for row in rows:
        if TEXT_KEYS & row.keys():
            raise SystemExit(f"row {row.get('i')} carries sentence text")
        by_i[row["i"]] = row
    pred = []
    exact = []
    answered = 0
    for lab in labels:
        row = by_i.get(lab["i"])
        gold = lab["label"]
        if row is None or "error" in row or "score" not in row:
            score = failed_score(gold)
        else:
            score = float(row["score"])
            answered += 1
        pred.append(score)
        exact.append(
            rounded(score) == rounded(gold)
            and row is not None
            and "error" not in row
            and "score" in row
        )
    return pred, exact, answered


def mae(pred, gold):
    return sum(abs(p - g) for p, g in zip(pred, gold)) / len(gold)


def sign_test(pred_a, pred_b, gold):
    a_better = b_better = 0
    for a, b, g in zip(pred_a, pred_b, gold):
        ea, eb = abs(a - g), abs(b - g)
        if ea < eb:
            a_better += 1
        elif eb < ea:
            b_better += 1
    n = a_better + b_better
    p = binom_two_sided(min(a_better, b_better), n)
    return a_better, b_better, p, verdict(a_better, b_better, p)


def mcnemar(exact_a, exact_b):
    a_only = sum(1 for a, b in zip(exact_a, exact_b) if a and not b)
    b_only = sum(1 for a, b in zip(exact_a, exact_b) if b and not a)
    n = a_only + b_only
    p = binom_two_sided(min(a_only, b_only), n)
    return a_only, b_only, p, verdict(a_only, b_only, p)


def bootstrap_spearman(pred_a, pred_b, gold):
    rng = random.Random(BOOT_SEED)
    n = len(gold)
    diffs = []
    for _ in range(BOOT):
        idx = [rng.randrange(n) for _ in range(n)]
        ga = [gold[i] for i in idx]
        sa = spearman([pred_a[i] for i in idx], ga)
        sb = spearman([pred_b[i] for i in idx], ga)
        if sa is None or sb is None:
            continue
        diffs.append(sa - sb)
    diffs.sort()
    if len(diffs) < BOOT:
        return None, None, "TIE"
    lo, hi = diffs[49], diffs[1949]
    if lo > 0:
        return lo, hi, "WIN"
    if hi < 0:
        return lo, hi, "LOSE"
    return lo, hi, "TIE"


def floors(labels):
    gold = [row["label"] for row in labels]
    rounded_counts = tuple(
        sum(1 for g in gold if rounded(g) == k) for k in range(LEVELS)
    )
    mean = sum(gold) / len(gold)
    mode = max(range(LEVELS), key=lambda k: (rounded_counts[k], -k))
    mean_level = rounded(mean)
    return {
        "n": len(gold),
        "mean": mean,
        "mode": mode,
        "rounded": rounded_counts,
        "exact_mean": sum(1 for g in gold if rounded(g) == mean_level),
        "exact_mode": rounded_counts[mode],
        "mae_mean": sum(abs(g - mean) for g in gold) / len(gold),
        "mae_mode": sum(abs(g - mode) for g in gold) / len(gold),
    }


def check_floors(labels):
    got = floors(labels)
    ok = (
        got["n"] == N
        and got["rounded"] == ROUNDED
        and got["mode"] == MODE
        and got["exact_mean"] == EXACT_MEAN
        and got["exact_mode"] == EXACT_MODE
        and abs(got["mean"] - MEAN) < 1e-5
        and abs(got["mae_mean"] - MAE_MEAN) < 1e-5
        and abs(got["mae_mode"] - MAE_MODE) < 1e-5
    )
    return ok, got


def rows_path(name):
    return os.path.join(HERE, f"rows-{name}.jsonl")


def main():
    labels = load_jsonl(os.path.join(HERE, "labels.jsonl"))
    ok, got = check_floors(labels)
    if "--bar" in sys.argv:
        print(
            json.dumps(
                {
                    "floors_match": ok,
                    **{
                        k: (list(v) if isinstance(v, tuple) else v)
                        for k, v in got.items()
                    },
                }
            )
        )
        return 0 if ok else 1
    if not ok:
        print("labels drifted from the bar", got, file=sys.stderr)
        return 1
    gold = [row["label"] for row in labels]
    arms = {}
    for name in JEV_RUNS + GROK_RUNS:
        rows = load_jsonl(rows_path(name))
        if not rows:
            print(f"missing {name}", file=sys.stderr)
            return 1
        pred, exact, answered = arm_preds(labels, rows)
        arms[name] = {
            "pred": pred,
            "exact": exact,
            "answered": answered,
            "spearman": spearman(pred, gold),
            "mae": mae(pred, gold),
            "exact_n": sum(exact),
        }
        print(
            f"{name} answered={answered}/{N} spearman={arms[name]['spearman']} "
            f"mae={arms[name]['mae']:.6f} exact={arms[name]['exact_n']}/{N}"
        )
    # Floors vs each Jev run.
    mean_pred = [MEAN] * N
    mode_pred = [float(MODE)] * N
    mean_exact = [rounded(g) == rounded(MEAN) for g in gold]
    mode_exact = [rounded(g) == MODE for g in gold]
    for name in JEV_RUNS:
        arm = arms[name]
        for label, pred, exact in (
            ("always-mean", mean_pred, mean_exact),
            ("always-mode", mode_pred, mode_exact),
        ):
            a, b, p, v = sign_test(arm["pred"], pred, gold)
            ea, eb, ep, ev = mcnemar(arm["exact"], exact)
            print(
                f"{name} vs {label} MAE {a}/{b} p={p:.4g} {v}; exact {ea}/{eb} p={ep:.4g} {ev}"
            )
    holds = {"spearman": 0, "mae": 0, "exact": 0}
    loses = {"spearman": 0, "mae": 0, "exact": 0}
    for jn in JEV_RUNS:
        for gn in GROK_RUNS:
            j, g = arms[jn], arms[gn]
            lo, hi, sv = bootstrap_spearman(j["pred"], g["pred"], gold)
            ma, mb, mp, mv = sign_test(j["pred"], g["pred"], gold)
            ea, eb, ep, ev = mcnemar(j["exact"], g["exact"])
            print(
                f"{jn} x {gn} spearman {sv} [{lo},{hi}] mae {ma}/{mb} p={mp:.4g} {mv} "
                f"exact {ea}/{eb} p={ep:.4g} {ev}"
            )
            for key, v in (("spearman", sv), ("mae", mv), ("exact", ev)):
                holds[key] += v == "WIN"
                loses[key] += v == "LOSE"
    print("WIN pairings", holds, "LOSE pairings", loses)
    return 0


if __name__ == "__main__":
    sys.exit(main())
