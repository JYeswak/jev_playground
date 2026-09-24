#!/usr/bin/env python3
"""Scorer for bead jev-5fm: hierarchical (greedy and beam K=3) vs the committed flat Jev rows.

Stdlib only, no key. Reads full.jsonl, hierarchy.json, rows-hier-jev.jsonl (the four Choice
distributions per query) and rows-full-jev.jsonl (flat 77-way Jev, jev-4jf). Runs greedy and
beam search offline from the stored distributions, following
docs-mirror/typesafe/cookbooks/hierarchical_classification.md (geometric-mean edge probability,
EPSILON floor), and prints the numbers and verdict of
docs/demos/upstream-repro/choice-banking77-hier-20260924.md.

Run: python3 work/choice-banking77/score_hier.py
"""

import json
import math
import os
from collections import Counter

from score import mcnemar_exact, nearest_rank, pct, wilson

HERE = os.path.dirname(os.path.abspath(__file__))
EPSILON = 1e-9
BEAM = 3
THRESHOLDS = (0.5, 0.7, 0.9)
ALPHA = 0.05


def jsonl(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def last_complete(rows, key):
    out = {}
    for r in rows:
        if key in r or r["i"] not in out:
            out[r["i"]] = r
    return out


def edge(p):
    return max(p, EPSILON)


def greedy(row):
    root = row["root"]["probabilities"]
    parent = max(root, key=root.get)
    kids = row["children"][parent]["probabilities"]
    leaf = max(kids, key=kids.get)
    return leaf, math.sqrt(edge(root[parent]) * edge(kids[leaf])), parent


def beam(row):
    root = row["root"]["probabilities"]
    frontier = sorted(root, key=lambda p: -root[p])[:BEAM]
    cands = []
    for p in frontier:
        kids = row["children"][p]["probabilities"]
        for leaf, q in kids.items():
            cands.append((math.sqrt(edge(root[p]) * edge(q)), leaf, p))
    cands.sort(key=lambda c: -c[0])
    score, leaf, parent = cands[0]
    return leaf, score, parent


def main():
    subset = jsonl("full.jsonl")
    with open(os.path.join(HERE, "hierarchy.json"), encoding="utf-8") as fh:
        hier = json.load(fh)
    parent_of = {c: p for p, kids in hier["parents"].items() for c in kids}
    hrows = last_complete(jsonl("rows-hier-jev.jsonl"), "root")
    frows = last_complete(jsonl("rows-full-jev.jsonl"), "choice")
    n = len(subset)

    arms = {"flat": {}, "greedy": {}, "beam": {}}
    gate = {"flat p_max": {}, "flat confidence": {}, "greedy path": {}, "beam path": {}}
    lat = {"flat": [], "greedy": [], "beam": []}
    tok = {"flat": [0, 0], "greedy": [0, 0], "beam": [0, 0]}
    calls = {"flat": 0, "greedy": 0, "beam": 0}
    root_top1 = root_top3 = hfailed = ffailed = 0
    conf = {"flat": Counter(), "beam": Counter()}
    models = Counter()
    for item in subset:
        i, truth = item["i"], item["intent"]
        f = frows.get(i)
        if f and "choice" in f:
            arms["flat"][i] = f["choice"] == truth
            gate["flat p_max"][i] = max(f["probabilities"].values())
            gate["flat confidence"][i] = f["confidence"]
            lat["flat"].append(f["latencyMs"])
            tok["flat"][0] += f["usage"]["input_tokens"]
            tok["flat"][1] += f["usage"]["output_tokens"]
            calls["flat"] += 1
            if f["choice"] != truth:
                conf["flat"][(truth, f["choice"])] += 1
        else:
            arms["flat"][i] = False
            ffailed += 1
        h = hrows.get(i)
        if not (h and "root" in h):
            arms["greedy"][i] = arms["beam"][i] = False
            hfailed += 1
            continue
        g_leaf, g_score, g_parent = greedy(h)
        b_leaf, b_score, _ = beam(h)
        arms["greedy"][i] = g_leaf == truth
        arms["beam"][i] = b_leaf == truth
        gate["greedy path"][i] = g_score
        gate["beam path"][i] = b_score
        if b_leaf != truth:
            conf["beam"][(truth, b_leaf)] += 1
        root = h["root"]["probabilities"]
        ranked = sorted(root, key=lambda p: -root[p])
        root_top1 += ranked[0] == parent_of[truth]
        root_top3 += parent_of[truth] in ranked[:BEAM]
        models[h["root"]["model"]] += 1
        for c in h["children"].values():
            models[c["model"]] += 1
        g_calls = [h["root"], h["children"][g_parent]]
        b_calls = [h["root"], *h["children"].values()]
        lat["greedy"].append(sum(c["ms"] for c in g_calls))
        lat["beam"].append(h["wallMs"])
        for arm, cs in (("greedy", g_calls), ("beam", b_calls)):
            calls[arm] += len(cs)
            tok[arm][0] += sum(c["usage"]["input_tokens"] for c in cs)
            tok[arm][1] += sum(c["usage"]["output_tokens"] for c in cs)

    print(f"corpus: {n} rows, {len(parent_of)} intents, {len(hier['parents'])} parents")
    print(
        f"failed rows: hier {hfailed}, flat {ffailed}; models seen (hier calls): {dict(models)}"
    )
    print(
        f"parent step: true parent ranked 1st {root_top1}/{n} ({pct(root_top1, n)}), "
        f"in top {BEAM} {root_top3}/{n} ({pct(root_top3, n)}) = beam ceiling"
    )
    print()
    print(
        "| Arm | Correct | Accuracy | Wilson 95% | Calls/query | Tokens in / out per query | p50 / p95 ms per query |"
    )
    print("|---|---:|---:|---|---:|---|---|")
    for arm in ("flat", "greedy", "beam"):
        k = sum(arms[arm].values())
        lo, hi = wilson(k, n)
        q = max(1, len(lat[arm]))
        print(
            f"| {arm} | {k}/{n} | {pct(k, n)} | {100 * lo:.1f}-{100 * hi:.1f}% | "
            f"{calls[arm] / q:.2f} | {tok[arm][0] / q:,.0f} / {tok[arm][1] / q:,.0f} | "
            f"{nearest_rank(lat[arm], 0.5)} / {nearest_rank(lat[arm], 0.95)} |"
        )

    print()
    print("Coverage: rows with gate score >= t, then accuracy among them")
    print("| Gate | " + " | ".join(f">= {t}" for t in THRESHOLDS) + " |")
    print("|---|" + "---|" * len(THRESHOLDS))
    for name, scores in gate.items():
        arm = name.split()[0]
        cells = []
        for t in THRESHOLDS:
            cov = [i for i, s in scores.items() if s >= t]
            ck = sum(arms[arm][i] for i in cov)
            cells.append(f"{len(cov)} ({pct(len(cov), n)}), {pct(ck, len(cov))}")
        print(f"| {name} | " + " | ".join(cells) + " |")

    print()
    results = {}
    for arm in ("beam", "greedy"):
        b = sum(1 for i in arms[arm] if arms[arm][i] and not arms["flat"][i])
        c = sum(1 for i in arms[arm] if arms["flat"][i] and not arms[arm][i])
        p = mcnemar_exact(b, c)
        results[arm] = (b, c, p)
        print(
            f"paired {arm} vs flat: {arm}-only {b}, flat-only {c}, McNemar exact p = {p:.3g}"
        )
    b = sum(1 for i in arms["beam"] if arms["beam"][i] and not arms["greedy"][i])
    c = sum(1 for i in arms["beam"] if arms["greedy"][i] and not arms["beam"][i])
    print(
        f"paired beam vs greedy (descriptive): beam-only {b}, greedy-only {c}, p = {mcnemar_exact(b, c):.3g}"
    )
    for arm in ("flat", "beam"):
        top = ", ".join(f"{t}->{g} x{k}" for (t, g), k in conf[arm].most_common(5))
        print(f"top confusions {arm}: {top}")
        cross = sum(
            k for (t, g), k in conf[arm].items() if parent_of[t] != parent_of[g]
        )
        within = sum(conf[arm].values()) - cross
        print(f"  {arm} errors: {cross} cross parents, {within} within the true parent")

    print()
    b, c, p = results["beam"]
    beam_acc = sum(arms["beam"].values()) / n
    if beam_acc < 0.5:
        verdict = "NOT-SCORED (beam below the 50% feasibility floor)"
    elif b > c and p < ALPHA:
        verdict = f"BEATS FLAT (beam-only {b} vs flat-only {c}, p = {p:.3g})"
    elif c > b and p < ALPHA:
        verdict = f"WORSE THAN FLAT (beam-only {b} vs flat-only {c}, p = {p:.3g})"
    else:
        verdict = f"NO DIFFERENCE (beam-only {b} vs flat-only {c}, p = {p:.3g})"
    print(f"verdict: {verdict}")
    print(
        f"hypothesis (hierarchical beats flat): {'SUPPORTED' if verdict.startswith('BEATS') else 'REFUTED'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
