#!/usr/bin/env python3
"""Scorer for beads jev-k2q (SciFact) and jev-5jp (FEVER): do Noul outcome criteria lift claim
verification?

Run: python3 work/noul-scifact/compare-criteria.py [data_dir]   (stdlib only, no key, no network)
data_dir (default: this directory) holds sample.jsonl and the rows files below.
Primary pair  : rows-jev.jsonl (criteria, the committed arm) vs rows-jev-nocriteria.jsonl.
Control pair  : rows-jev-rerun.jsonl (criteria, run beside the ablation) vs rows-jev-nocriteria.jsonl,
                plus rows-jev vs rows-jev-rerun as the run-to-run noise floor.
Metric functions, failed-row handling, the 0.5 cut and the bootstrap are imported from score.py,
so every receipt uses the same arithmetic. Rules frozen in
docs/demos/upstream-repro/noul-scifact-criteria-20260924.md and noul-fever-criteria-20260924.md.
"""

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("score", os.path.join(HERE, "score.py"))
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)


def arm(sample, name, data):
    rows = S.load_jsonl(os.path.join(data, f"rows-{name}.jsonl"))
    preds = S.arm_probs(sample, rows)
    p = [r["noul"] if r is not None else 0.5 for r in preds]
    y = [1 if s["truth"] else 0 for s in sample]
    ok = [S.correct(pp, r, bool(t)) for pp, r, t in zip(p, preds, y)]
    return {"rows": rows, "preds": preds, "p": p, "ok": ok}


def compare(a, b, y):
    """Verdicts for a (criteria) against b: WIN means a is significantly better."""
    ao = sum(1 for x, z in zip(a["ok"], b["ok"]) if x and not z)
    bo = sum(1 for x, z in zip(a["ok"], b["ok"]) if z and not x)
    pm = S.binom_two_sided(ao, ao + bo)
    out = {
        "acc": (
            "WIN"
            if pm < S.ALPHA and ao > bo
            else "LOSE"
            if pm < S.ALPHA and bo > ao
            else "TIE",
            f"{ao} vs {bo}, p={pm:.3g}",
        )
    }
    for key, m, higher in (
        ("auc", S.auc, True),
        ("brier", S.brier, False),
        ("ece", S.ece, False),
    ):
        lo, hi = S.boot(m, a["p"], b["p"], y)
        better = lo > 0 if higher else hi < 0
        worse = hi < 0 if higher else lo > 0
        out[key] = (
            "WIN" if better else "LOSE" if worse else "TIE",
            f"{lo:+.4f} to {hi:+.4f}",
        )
    return out


def verdict(v):
    labels = [x[0] for x in v.values()]
    if "LOSE" in labels:
        return "HURT"
    if "WIN" in labels:
        return "LIFT"
    return "NO EFFECT"


def main(data=HERE):
    sample = S.load_jsonl(os.path.join(data, "sample.jsonl"))
    y = [1 if s["truth"] else 0 for s in sample]
    n = len(y)
    names = {
        "jev": "criteria (committed)",
        "jev-nocriteria": "no criteria (ablation)",
        "jev-rerun": "criteria (same-time rerun)",
    }
    arms = {k: arm(sample, k, data) for k in names}
    arms = {k: v for k, v in arms.items() if any(v["preds"])}

    print(f"data: {data}\nsample: {n} pairs, true {sum(y)}")
    print(
        "\n| Arm | Answered | Correct at >0.5 | Accuracy | AUC | Brier | ECE | p50 / p95 ms | Tokens in / out | Distinct values |"
    )
    print("|---|---:|---:|---:|---:|---:|---:|---|---|---:|")
    for k, a in arms.items():
        got = [r for r in a["preds"] if r is not None]
        lat = [r["latencyMs"] for r in got]
        tin = sum(r["usage"]["input_tokens"] or 0 for r in got)
        tout = sum(r["usage"]["output_tokens"] or 0 for r in got)
        c = sum(a["ok"])
        print(
            f"| {names[k]} | {len(got)}/{n} | {c}/{n} | {c / n:.1%} | {S.auc(a['p'], y):.3f} | "
            f"{S.brier(a['p'], y):.4f} | {S.ece(a['p'], y):.4f} | {S.pct(lat, 0.5)} / {S.pct(lat, 0.95)} | "
            f"{tin:,} / {tout:,} | {len({round(x, 4) for x in a['p']})} |"
        )

    pairs = [
        ("primary", "jev", "jev-nocriteria"),
        ("control", "jev-rerun", "jev-nocriteria"),
        ("noise floor", "jev", "jev-rerun"),
    ]
    results = {}
    print("\nPaired (first arm minus second; WIN = first arm significantly better)")
    print(
        "| Pair | First vs second | Accuracy (McNemar) | AUC diff 95% | Brier diff 95% | ECE diff 95% | Reading |"
    )
    print("|---|---|---|---|---|---|---|")
    for label, a, b in pairs:
        if a not in arms or b not in arms:
            continue
        v = compare(arms[a], arms[b], y)
        results[label] = v
        cells = " | ".join(
            f"{v[k][0]} ({v[k][1]})" for k in ("acc", "auc", "brier", "ece")
        )
        reading = (
            verdict(v)
            if label != "noise floor"
            else ("DIFFERENT" if verdict(v) != "NO EFFECT" else "SAME")
        )
        print(f"| {label} | {names[a]} vs {names[b]} | {cells} | {reading} |")

    if "primary" in results:
        pv = verdict(results["primary"])
        print(f"\nverdict (primary): criteria {pv}")
        if "control" in results:
            cv = verdict(results["control"])
            print(f"control agrees: {'YES' if cv == pv else 'NO'} (control reads {cv})")
        print(
            f"NEGATIVE_EVIDENCE row required: {'YES' if pv in ('HURT', 'NO EFFECT') else 'NO'}"
        )

    print(
        "\nBy gold label (correct at >0.5 / mean noul); McNemar criteria vs ablation within label"
    )
    print(
        "| Gold | Rows | "
        + " | ".join(names[k] for k in arms)
        + " | McNemar (committed vs ablation) |"
    )
    print("|---|---:|" + "---|" * len(arms) + "---|")
    true_golds = {s["gold"] for s in sample if s["truth"]}
    for g in sorted(
        {s["gold"] for s in sample}, key=lambda g: (g not in true_golds, g)
    ):
        idx = [i for i, s in enumerate(sample) if s["gold"] == g]
        cells = []
        for k, a in arms.items():
            c = sum(1 for i in idx if a["ok"][i])
            mp = sum(a["p"][i] for i in idx) / len(idx)
            cells.append(f"{c} ({c / len(idx):.1%}) / {mp:.3f}")
        mc = ""
        if "jev" in arms and "jev-nocriteria" in arms:
            ao = sum(
                1
                for i in idx
                if arms["jev"]["ok"][i] and not arms["jev-nocriteria"]["ok"][i]
            )
            bo = sum(
                1
                for i in idx
                if arms["jev-nocriteria"]["ok"][i] and not arms["jev"]["ok"][i]
            )
            mc = f"{ao} vs {bo}, p={S.binom_two_sided(ao, ao + bo):.3g}"
        print(f"| {g} | {len(idx)} | " + " | ".join(cells) + f" | {mc} |")
    return 0


if __name__ == "__main__":
    sys.exit(main(os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else HERE))
