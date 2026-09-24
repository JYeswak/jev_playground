#!/usr/bin/env python3
"""Scorer for beads jev-9er (SciFact) and jev-wx5 (FEVER): Jev Noul vs Haiku. Stdlib only, no key.

Run: python3 work/noul-scifact/score.py [data_dir]
Reads sample.jsonl and rows-{jev,haiku}.jsonl in data_dir (default: this directory) and prints
the receipt tables. Haiku rows whose adapter debug shows a rescaled or zero-mass distribution
(jev-mly) are counted, and when there are any the whole comparison is printed again without them.
Rules frozen in docs/demos/upstream-repro/noul-scifact-20260924.md:
  decision   = noul > 0.5 means "supports"
  failed row = counted incorrect for accuracy; noul 0.5 for AUC, Brier and ECE
  AUC        = Mann-Whitney with average ranks for ties
  ECE        = 10 equal-width bins on [0, 1], weighted by bin count, last bin closed
  paired     = McNemar exact on correct/incorrect; paired bootstrap (2000 resamples,
               random.Random(20260924)) 95% percentile intervals for AUC, Brier and ECE differences
"""

import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CUT = 0.5
ALPHA = 0.05
BOOT = 2000
SEED = 20260924
BINS = 10


def load_jsonl(path):
    if not os.path.exists(path):
        return []
    return [json.loads(line) for line in open(path) if line.strip()]


def auc(p, y):
    pos = sum(y)
    neg = len(y) - pos
    if pos == 0 or neg == 0:
        return float("nan")
    order = sorted(range(len(p)), key=lambda k: p[k])
    ranks = [0.0] * len(p)
    j = 0
    while j < len(order):
        k = j
        while k + 1 < len(order) and p[order[k + 1]] == p[order[j]]:
            k += 1
        avg = (j + k) / 2 + 1
        for m in range(j, k + 1):
            ranks[order[m]] = avg
        j = k + 1
    rsum = sum(r for r, t in zip(ranks, y) if t)
    return (rsum - pos * (pos + 1) / 2) / (pos * neg)


def brier(p, y):
    return sum((a - b) ** 2 for a, b in zip(p, y)) / len(y)


def ece(p, y):
    bins = [[] for _ in range(BINS)]
    for a, b in zip(p, y):
        bins[min(BINS - 1, int(a * BINS))].append((a, b))
    return sum(
        len(b)
        / len(y)
        * abs(sum(x for x, _ in b) / len(b) - sum(t for _, t in b) / len(b))
        for b in bins
        if b
    )


def accuracy(p, y):
    return sum(1 for a, b in zip(p, y) if (a > CUT) == bool(b)) / len(y)


def binom_two_sided(k, n):
    if n == 0:
        return 1.0
    m = min(k, n - k)
    return min(1.0, 2 * sum(math.comb(n, j) for j in range(m + 1)) / 2**n)


def wilson(k, n, z=1.959963984540054):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)


def pct(xs, q):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, max(0, math.ceil(q * len(xs)) - 1))]


def boot(metric, a, b, y):
    """Paired percentile 95% interval of metric(a) - metric(b); b=None gives metric(a) alone."""
    rng = random.Random(SEED)
    n = len(y)
    vals = []
    for _ in range(BOOT):
        idx = [rng.randrange(n) for _ in range(n)]
        yy = [y[k] for k in idx]
        if sum(yy) in (0, n):
            continue
        va = metric([a[k] for k in idx], yy)
        vals.append(va if b is None else va - metric([b[k] for k in idx], yy))
    vals.sort()
    return vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]


def arm_probs(sample, rows):
    by_i = {r["i"]: r for r in rows if "noul" in r}
    return [by_i.get(s["i"]) for s in sample]


def correct(p, row, truth):
    return row is not None and (p > CUT) == truth


def main(data=HERE, exclude=frozenset()):
    sample = [
        s
        for s in load_jsonl(os.path.join(data, "sample.jsonl"))
        if s["i"] not in exclude
    ]
    y = [1 if s["truth"] else 0 for s in sample]
    n = len(y)
    prev = sum(y) / n
    print(f"sample: {n} pairs, true {sum(y)}, prevalence {prev:.4f}")

    const = {
        "constant: always no (0)": [0.0] * n,
        f"constant: base rate ({prev:.3f})": [prev] * n,
    }
    arms = {}
    for arm, label in (("jev", "Jev jev-1.13.0"), ("haiku", "Haiku 4.5 via adapter")):
        rows = load_jsonl(os.path.join(data, f"rows-{arm}.jsonl"))
        preds = arm_probs(sample, rows)
        if not any(preds):
            continue
        p = [r["noul"] if r is not None else 0.5 for r in preds]
        ok = [correct(pp, r, bool(t)) for pp, r, t in zip(p, preds, y)]
        arms[arm] = {"label": label, "rows": rows, "preds": preds, "p": p, "ok": ok}

    print(
        "\n| Arm | Correct at >0.5 | Accuracy | Wilson 95% | AUC | Brier | ECE (10 bins) |"
    )
    print("|---|---:|---:|---|---:|---:|---:|")
    for name, p in const.items():
        k = sum(1 for a, t in zip(p, y) if (a > CUT) == bool(t))
        lo, hi = wilson(k, n)
        print(
            f"| {name} | {k}/{n} | {k / n:.1%} | {lo:.1%}-{hi:.1%} | 0.500 | {brier(p, y):.4f} | {ece(p, y):.4f} |"
        )
    for arm, a in arms.items():
        k = sum(a["ok"])
        lo, hi = wilson(k, n)
        print(
            f"| {a['label']} | {k}/{n} | {k / n:.1%} | {lo:.1%}-{hi:.1%} | "
            f"{auc(a['p'], y):.3f} | {brier(a['p'], y):.4f} | {ece(a['p'], y):.4f} |"
        )

    if arms:
        print(
            "\n| Arm | Answered | Model(s) | p50 / p95 latency ms | Tokens in / out | Error rows logged | "
            "AUC 95% | Brier 95% | ECE 95% | Distinct noul values |"
        )
        print("|---|---:|---|---|---|---:|---|---|---|---:|")
        for arm, a in arms.items():
            got = [r for r in a["preds"] if r is not None]
            lat = [r["latencyMs"] for r in got]
            tin = sum(r["usage"]["input_tokens"] or 0 for r in got)
            tout = sum(r["usage"]["output_tokens"] or 0 for r in got)
            models = sorted({r["model"] for r in got})
            errs = sum(1 for r in a["rows"] if "error" in r)
            ci = [boot(m, a["p"], None, y) for m in (auc, brier, ece)]
            print(
                f"| {arm} | {len(got)}/{n} | {', '.join(models)} | {pct(lat, 0.5)} / {pct(lat, 0.95)} | "
                f"{tin:,} / {tout:,} | {errs} | {ci[0][0]:.3f}-{ci[0][1]:.3f} | "
                f"{ci[1][0]:.4f}-{ci[1][1]:.4f} | {ci[2][0]:.4f}-{ci[2][1]:.4f} | "
                f"{len({round(x, 4) for x in a['p']})} |"
            )

    if "jev" in arms:
        j = arms["jev"]
        verdicts = {}
        print("\nPaired on the same rows (Jev vs X)")
        print(
            "| Jev vs | Jev-only correct | X-only correct | McNemar p | Accuracy | "
            "AUC diff 95% | AUC | Brier diff 95% | Brier | ECE diff 95% | ECE |"
        )
        print("|---|---:|---:|---:|---|---|---|---|---|---|---|")
        others = [
            ("always no", const["constant: always no (0)"], None),
            ("base rate", const[f"constant: base rate ({prev:.3f})"], None),
        ]
        if "haiku" in arms:
            others.append(("Haiku", arms["haiku"]["p"], arms["haiku"]["ok"]))
        for name, p, ok in others:
            if ok is None:
                ok = [(a > CUT) == bool(t) for a, t in zip(p, y)]
            jo = sum(1 for a, b in zip(j["ok"], ok) if a and not b)
            xo = sum(1 for a, b in zip(j["ok"], ok) if b and not a)
            pm = binom_two_sided(jo, jo + xo)
            va = (
                "WIN"
                if pm < ALPHA and jo > xo
                else "LOSE"
                if pm < ALPHA and xo > jo
                else "TIE"
            )
            cells = []
            vs = {"acc": va}
            for key, m, higher_better in (
                ("auc", auc, True),
                ("brier", brier, False),
                ("ece", ece, False),
            ):
                if name != "Haiku" and key == "auc":
                    lo, hi = boot(auc, j["p"], None, y)
                    lo, hi = lo - 0.5, hi - 0.5
                elif name == "base rate" and key == "ece":
                    cells += ["n/a (0 by construction)", "n/a"]
                    vs[key] = "n/a"
                    continue
                else:
                    lo, hi = boot(m, j["p"], p, y)
                better = (lo > 0) if higher_better else (hi < 0)
                worse = (hi < 0) if higher_better else (lo > 0)
                v = "WIN" if better else "LOSE" if worse else "TIE"
                vs[key] = v
                cells += [f"{lo:+.4f} to {hi:+.4f}", v]
            verdicts[name] = vs
            print(
                f"| {name} | {jo} | {xo} | {pm:.2e} | {va} | "
                + " | ".join(cells)
                + " |"
            )

        c1 = verdicts["always no"]["acc"] == "WIN"
        c2 = verdicts["always no"]["auc"] == "WIN"
        c3 = verdicts["base rate"]["brier"] == "WIN"
        beats = c1 and c2 and c3
        print(
            f"\nbar 1: accuracy WIN vs always-no {c1}; AUC CI above 0.5 {c2}; "
            f"Brier WIN vs base rate {c3} -> {'PASS' if beats else 'FAIL'}"
        )
        if "Haiku" in verdicts:
            h = verdicts["Haiku"]
            lost = "LOSE" in (h["acc"], h["auc"], h["brier"], h["ece"])
            print(
                f"bar 2: vs Haiku accuracy {h['acc']}, AUC {h['auc']}, Brier {h['brier']}, "
                f"ECE {h['ece']}; loses to incumbent: {'YES' if lost else 'NO'}"
            )
            print(f"overall: {'PASS' if beats and not lost else 'FAIL'}")

    for arm, a in arms.items():
        print(f"\nCalibration table, {arm} (10 equal-width bins)")
        print("| Bin | Rows | Mean noul | Fraction true |")
        print("|---|---:|---:|---:|")
        bins = [[] for _ in range(BINS)]
        for pp, t in zip(a["p"], y):
            bins[min(BINS - 1, int(pp * BINS))].append((pp, t))
        for b, rows in enumerate(bins):
            if rows:
                mp = sum(x for x, _ in rows) / len(rows)
                ft = sum(t for _, t in rows) / len(rows)
                print(
                    f"| {b / BINS:.1f}-{(b + 1) / BINS:.1f} | {len(rows)} | {mp:.3f} | {ft:.3f} |"
                )
        by_gold = {}
        for s, pp, ok in zip(sample, a["p"], a["ok"]):
            g = by_gold.setdefault(s["gold"], [0, 0, 0.0])
            g[0] += 1
            g[1] += ok
            g[2] += pp
        print(f"\nBy gold label, {arm}")
        print("| Gold | Rows | Correct | Mean noul |")
        print("|---|---:|---:|---:|")
        true_golds = {s["gold"] for s in sample if s["truth"]}
        for g in sorted(by_gold, key=lambda g: (g not in true_golds, g)):
            r = by_gold[g]
            print(f"| {g} | {r[0]} | {r[1]} ({r[1] / r[0]:.1%}) | {r[2] / r[0]:.3f} |")

    if "haiku" in arms and not exclude:
        got = [r for r in arms["haiku"]["preds"] if r is not None]
        recorded = [r for r in got if "probabilityError" in r]
        rescaled = {r["i"] for r in recorded if r["probabilityError"] is not None}
        zero = {
            r["i"]
            for r in recorded
            if isinstance(r.get("originalProbabilities"), dict)
            and sum(r["originalProbabilities"].values()) == 0
        }
        print(
            f"\nHaiku adapter debug (jev-mly): recorded on {len(recorded)}/{len(got)} answered rows; "
            f"probability_errors set on {len(rescaled)}; zero-mass (original sum 0) on {len(zero)}"
        )
        if rescaled | zero:
            print(
                f"\n=== Re-scored without the {len(rescaled | zero)} rescaled or zero-mass Haiku rows (both arms) ==="
            )
            main(data, frozenset(rescaled | zero))
        elif len(recorded) < len(got):
            print(
                f"Debug was not recorded on {len(got) - len(recorded)} rows: zero-mass is not ruled out for them."
            )
        else:
            print(
                "Re-score without them: identical to the tables above (0 rows to drop)."
            )
    return 0


if __name__ == "__main__":
    sys.exit(main(os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else HERE))
