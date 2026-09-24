#!/usr/bin/env python3
"""Top-k recall and short-list curve for bead jev-zfn. Offline: stdlib, no key, no calls.

Reads full.jsonl, rows-full-jev.jsonl (jev-1.13.0, jev-4jf) and rows-full-haiku-prompted.jsonl
(Haiku 4.5 via the adapter, prompted JSON, jev-4jf second bar). Bar:
docs/demos/upstream-repro/choice-banking77-topk-20260924.md (committed before this was first run).

Rank rule (pessimistic on ties): the truth's rank = 1 + number of other labels whose probability
is >= the truth's. So a tie never helps, and a flat (uniform) distribution misses at every k < 77.

Run: python3 work/choice-banking77/score_topk.py
"""

import json
import os

from score import mcnemar_exact, pct, wilson

HERE = os.path.dirname(os.path.abspath(__file__))
KS = (1, 2, 3, 5)
SHORTLIST = 3
THRESHOLDS = (0.0, 0.5, 0.7, 0.8, 0.9, 0.95, 0.99, 1.01)
DECISION_RECALL = 0.95
ALPHA = 0.05


def jsonl(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def by_id(rows):
    out = {}
    for r in rows:
        if "choice" in r or r["i"] not in out:
            out[r["i"]] = r
    return out


def rank(row, truth):
    probs = row["probabilities"]
    p = probs.get(truth, -1.0)
    return 1 + sum(1 for k, v in probs.items() if k != truth and v >= p)


def holm(pvals):
    """Holm step-down adjusted p-values, same order as the input."""
    order = sorted(range(len(pvals)), key=lambda j: pvals[j])
    adj = [0.0] * len(pvals)
    running = 0.0
    for pos, j in enumerate(order):
        running = max(running, min(1.0, (len(pvals) - pos) * pvals[j]))
        adj[j] = running
    return adj


def arm_ranks(subset, rows):
    fin = by_id(rows)
    ranks, confs, committed = {}, {}, {}
    for item in subset:
        r = fin.get(item["i"])
        if r and "choice" in r:
            ranks[item["i"]] = rank(r, item["intent"])
            confs[item["i"]] = r["confidence"]
            committed[item["i"]] = r["choice"] == item["intent"]
        else:
            ranks[item["i"]] = 10**9
            confs[item["i"]] = 0.0
            committed[item["i"]] = False
    return ranks, confs, committed, fin


def report(title, ids, arms):
    n = len(ids)
    print(f"\n## {title} (N = {n})")
    print(
        "| k | "
        + " | ".join(f"{a} recall" for a in arms)
        + " | a-only / b-only | McNemar p | Holm p |"
    )
    print("|---:|" + "---|" * (len(arms) + 3))
    names = list(arms)
    rows, pvals = [], []
    for k in KS:
        hit = {a: {i: arms[a]["ranks"][i] <= k for i in ids} for a in names}
        b = sum(1 for i in ids if hit[names[0]][i] and not hit[names[1]][i])
        c = sum(1 for i in ids if hit[names[1]][i] and not hit[names[0]][i])
        p = mcnemar_exact(b, c)
        pvals.append(p)
        rows.append((k, hit, b, c, p))
    for (k, hit, b, c, p), hp in zip(rows, holm(pvals)):
        cells = []
        for a in names:
            kk = sum(hit[a].values())
            lo, hi = wilson(kk, n)
            cells.append(f"{kk} ({pct(kk, n)}, {100 * lo:.1f}-{100 * hi:.1f})")
        print(f"| {k} | " + " | ".join(cells) + f" | {b} / {c} | {p:.3g} | {hp:.3g} |")
    for a in names:
        committed = sum(arms[a]["committed"][i] for i in ids)
        top1 = sum(arms[a]["ranks"][i] <= 1 for i in ids)
        need = next(
            (
                k
                for k in range(1, 78)
                if sum(arms[a]["ranks"][i] <= k for i in ids) >= DECISION_RECALL * n
            ),
            None,
        )
        print(
            f"{a}: committed-choice accuracy {committed}/{n}; pessimistic top-1 {top1}/{n}; "
            f"smallest k with recall >= {DECISION_RECALL:.0%}: {need}"
        )
    return rows


def curve(title, ids, arms):
    n = len(ids)
    print(
        f"\n### {title}: top-1 if confidence >= t, else top-{SHORTLIST} shown to a human (N = {n})"
    )
    print(
        "| Arm | t | auto-routed | auto correct | wrong auto-routes | to human | truth in short list | total success |"
    )
    print("|---|---:|---:|---:|---:|---:|---:|---:|")
    for a, arm in arms.items():
        for t in THRESHOLDS:
            auto = [i for i in ids if arm["confs"][i] >= t]
            human = [i for i in ids if arm["confs"][i] < t]
            ac = sum(arm["ranks"][i] <= 1 for i in auto)
            hs = sum(arm["ranks"][i] <= SHORTLIST for i in human)
            print(
                f"| {a} | {t} | {len(auto)} ({pct(len(auto), n)}) | {ac} ({pct(ac, len(auto))}) | "
                f"{len(auto) - ac} | {len(human)} ({pct(len(human), n)}) | {hs} ({pct(hs, len(human))}) | "
                f"{ac + hs} ({pct(ac + hs, n)}) |"
            )


def main():
    subset = jsonl("full.jsonl")
    arms = {}
    for name, fname in (
        ("jev", "rows-full-jev.jsonl"),
        ("haiku", "rows-full-haiku-prompted.jsonl"),
    ):
        ranks, confs, committed, fin = arm_ranks(subset, jsonl(fname))
        arms[name] = {
            "ranks": ranks,
            "confs": confs,
            "committed": committed,
            "final": fin,
        }
    all_ids = [item["i"] for item in subset]
    zero = sorted(i for i, r in arms["haiku"]["final"].items() if r.get("rawSum") == 0)
    print(f"Haiku zero-mass rows (rawSum == 0): {len(zero)} {zero}")
    main_rows = report("All rows", all_ids, arms)
    kept = [i for i in all_ids if i not in set(zero)]
    report("Zero-mass Haiku rows dropped from both arms", kept, arms)
    curve("All rows", all_ids, arms)

    print()
    k3 = next(r for r in main_rows if r[0] == SHORTLIST)
    jev3 = sum(k3[1]["jev"].values()) / len(all_ids)
    print(
        f"decision: Jev top-{SHORTLIST} recall {jev3:.1%} "
        f"{'>=' if jev3 >= DECISION_RECALL else '<'} {DECISION_RECALL:.0%} -> short list "
        f"{'WORTH BUILDING' if jev3 >= DECISION_RECALL else 'NOT SUFFICIENT'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
