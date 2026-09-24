#!/usr/bin/env python3
"""Confidence-routing cascade scorer for bead jev-cav. Stdlib only, no model calls.

Jev answers first; when Jev's own confidence is below t the row escalates to Haiku. For every t
on the grid fixed in docs/demos/upstream-repro/confidence-cascade-20260924.md this prints
accuracy, share escalated, mean latency and tokens per request (from each row's recorded values),
correct per unit cost, Pareto marks, the 2-fold check, the flat-Haiku-row sensitivity, policy B,
and the verdict under that bar.

Run: python3 work/confidence-cascade/cascade.py [--set full]
"""

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROWS = os.path.join(HERE, "..", "choice-banking77")
SETS = {
    "subset": ("subset.jsonl", "rows-jev.jsonl", "rows-haiku.jsonl"),
    "full": ("full.jsonl", "rows-full-jev.jsonl", "rows-full-haiku-prompted.jsonl"),
}
GRID = [round(0.05 * k, 2) for k in range(21)] + ["always"]
ESC_CAP = 0.25
# [INFERENCE] list prices per 1M tokens (in, out), as in choice-banking77-20260924.md.
PRICE = {"jev": (0.042, 0.0), "haiku": (1.00, 5.00)}


def load(name):
    with open(os.path.join(ROWS, name), encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def final_rows(rows):
    """Last answered row per id; an id with only error rows keeps its last error row."""
    out = {}
    for r in rows:
        if "choice" in r or r["i"] not in out or "choice" not in out[r["i"]]:
            out[r["i"]] = r
    return out


def call(r):
    """(choice or None, confidence, latency ms, tokens in, tokens out) for one recorded call."""
    if r is None:
        return (None, 0.0, 0, 0, 0)
    u = r.get("usage") or {}
    return (
        r.get("choice"),
        float(r.get("confidence", 0.0)) if "choice" in r else 0.0,
        int(r.get("latencyMs") or 0),
        int(u.get("input_tokens") or 0),
        int(u.get("output_tokens") or 0),
    )


def is_flat(r):
    probs = (r or {}).get("probabilities") or {}
    vals = list(probs.values())
    return bool(vals) and "choice" in r and all(v == vals[0] for v in vals)


def dollars(arm, tin, tout):
    pin, pout = PRICE[arm]
    return (tin * pin + tout * pout) / 1e6


def build(set_name):
    items_f, jev_f, hk_f = SETS[set_name]
    items = load(items_f)
    jev, hk = final_rows(load(jev_f)), final_rows(load(hk_f))
    rows = []
    for it in items:
        j, h = jev.get(it["i"]), hk.get(it["i"])
        rows.append(
            {
                "i": it["i"],
                "label": it["intent"],
                "jev": call(j),
                "hk": call(h),
                "flat": is_flat(h),
            }
        )
    return rows


def escalates(row, t):
    jc = row["jev"]
    return t == "always" or jc[0] is None or jc[1] < t


def answer(row, t, policy):
    """(correct, escalated, latency ms, tokens, dollars) for one row at threshold t."""
    j, h = row["jev"], row["hk"]
    lat, tok, usd = j[2], j[3] + j[4], dollars("jev", j[3], j[4])
    if not escalates(row, t):
        return (j[0] == row["label"], False, lat, tok, usd)
    lat += h[2]
    tok += h[3] + h[4]
    usd += dollars("haiku", h[3], h[4])
    pick = h[0]
    if policy == "B" and j[0] is not None and (h[0] is None or j[1] >= h[1]):
        pick = j[0]
    return (pick == row["label"], True, lat, tok, usd)


def point(rows, t, policy="A"):
    res = [answer(r, t, policy) for r in rows]
    n = len(rows)
    return {
        "t": t,
        "n": n,
        "correct": sum(1 for c, *_ in res if c),
        "esc": sum(1 for _, e, *_ in res if e),
        "lat": sum(x[2] for x in res) / n,
        "tok": sum(x[3] for x in res) / n,
        "usd": 1000 * sum(x[4] for x in res) / n,
        "ok": [c for c, *_ in res],
    }


def haiku_alone(rows):
    n = len(rows)
    return {
        "t": "haiku",
        "n": n,
        "correct": sum(1 for r in rows if r["hk"][0] == r["label"]),
        "esc": n,
        "lat": sum(r["hk"][2] for r in rows) / n,
        "tok": sum(r["hk"][3] + r["hk"][4] for r in rows) / n,
        "usd": 1000 * sum(dollars("haiku", r["hk"][3], r["hk"][4]) for r in rows) / n,
        "ok": [r["hk"][0] == r["label"] for r in rows],
    }


def pareto(points, key):
    marks = set()
    for p in points:
        dominated = any(
            q is not p
            and q["correct"] >= p["correct"]
            and q[key] <= p[key]
            and (q["correct"] > p["correct"] or q[key] < p[key])
            for q in points
        )
        if not dominated:
            marks.add(id(p))
    return marks


def per_cost(p):
    return (p["correct"] / (p["lat"] / 1000), p["correct"] / (p["tok"] / 1000))


def mcnemar_exact(b, c):
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2**n)


def label(t):
    names = {"always": "always", "haiku": "Haiku alone"}
    if t in names:
        return names[t]
    return "0.00 (Jev alone)" if t == 0.0 else f"{t:.2f}"


def table(rows, policy="A"):
    pts = [point(rows, t, policy) for t in GRID]
    hk = haiku_alone(rows)
    allp = pts + [hk]
    pl, pt = pareto(allp, "lat"), pareto(allp, "tok")
    print(
        "| t | Correct | Accuracy | Escalated | ms/req | tokens/req | $/1k req [INF] "
        "| correct per s | correct per 1k tok | Pareto |"
    )
    print("|---|---:|---:|---:|---:|---:|---:|---:|---:|---|")
    for p in allp:
        cs, ck = per_cost(p)
        marks = "/".join(m for m, s in (("lat", pl), ("tok", pt)) if id(p) in s) or ""
        print(
            f"| {label(p['t'])} | {p['correct']}/{p['n']} | {100 * p['correct'] / p['n']:.2f}% "
            f"| {p['esc']} ({100 * p['esc'] / p['n']:.1f}%) | {p['lat']:.0f} | {p['tok']:.0f} "
            f"| {p['usd']:.3f} | {cs:.1f} | {ck:.2f} | {marks} |"
        )
    return pts, hk


def best_within_cap(rows, idx):
    sub = [rows[k] for k in idx]
    cands = [point(sub, t) for t in GRID]
    cands = [p for p in cands if p["esc"] <= ESC_CAP * len(sub)]
    return max(cands, key=lambda p: (p["correct"], -p["esc"]))["t"]


def two_fold(rows):
    a = [k for k, r in enumerate(rows) if r["i"] % 2 == 0]
    b = [k for k, r in enumerate(rows) if r["i"] % 2 == 1]
    out_cas = out_jev = 0
    picks = []
    for fit, test in ((a, b), (b, a)):
        t = best_within_cap(rows, fit)
        sub = [rows[k] for k in test]
        out_cas += point(sub, t)["correct"]
        out_jev += point(sub, 0.0)["correct"]
        picks.append(t)
    return picks, out_cas, out_jev


def verdict(rows, pts, hk):
    jev = pts[0]
    best_single = max(jev["correct"], hk["correct"])
    capped = [p for p in pts if p["esc"] <= ESC_CAP * len(rows)]
    top = max(capped, key=lambda p: (p["correct"], -p["esc"]))
    picks, oc, oj = two_fold(rows)
    b = sum(1 for x, y in zip(top["ok"], jev["ok"]) if x and not y)
    c = sum(1 for x, y in zip(top["ok"], jev["ok"]) if y and not x)
    print(
        f"\nBest point within the {int(ESC_CAP * 100)}% cap: t = {label(top['t'])}, "
        f"{top['correct']}/{top['n']}, escalated {top['esc']}; "
        f"Jev alone {jev['correct']}, Haiku alone {hk['correct']}, better single arm {best_single}."
    )
    print(
        f"Cascade vs Jev alone at that point: cascade-only correct {b}, Jev-only correct {c}, "
        f"McNemar exact p = {mcnemar_exact(b, c):.3g}."
    )
    print(
        f"2-fold (even/odd i): picked t = {label(picks[0])} on even -> odd, "
        f"{label(picks[1])} on odd -> even; out-of-fold cascade {oc} vs Jev alone {oj} "
        f"({oc - oj:+d})."
    )
    useful_pts = (
        [p for p in capped if p["correct"] > best_single] if oc - oj >= 1 else []
    )
    if not useful_pts:
        why = (
            "Jev alone is the most accurate point within the cap"
            if top["t"] == 0.0
            else "in-sample gain does not survive the 2-fold check"
            if top["correct"] > best_single
            else "no point beats the better single arm"
        )
        print(f"VERDICT: NOT USEFUL ({why}).")
        return
    cheap = [
        p
        for p in useful_pts
        if all(per_cost(p)[k] > per_cost(s)[k] for s in (jev, hk) for k in (0, 1))
    ]
    if cheap:
        ts = ", ".join(label(p["t"]) for p in cheap)
        print(f"VERDICT: USEFUL, BEATS BOTH PER UNIT COST (t = {ts}).")
    else:
        print(
            "VERDICT: USEFUL on accuracy, but does NOT beat both arms per unit cost "
            "(every useful point has fewer correct rows per second or per 1k tokens than Jev alone)."
        )


def spread(vals):
    """The values themselves when few, else min / quartiles / max (nearest rank)."""
    s = sorted(vals)
    if len(s) <= 10:
        return s
    q = [s[max(0, math.ceil(p * len(s)) - 1)] for p in (0.25, 0.5, 0.75)]
    return f"min {s[0]}, quartiles {q[0]} / {q[1]} / {q[2]}, max {s[-1]}"


def report(rows, title):
    print(
        f"\n## {title}: N = {len(rows)}\n\n### Policy A (primary): escalate, take Haiku\n"
    )
    pts, hk = table(rows, "A")
    verdict(rows, pts, hk)
    hk_only = [
        r for r in rows if r["hk"][0] == r["label"] and r["jev"][0] != r["label"]
    ]
    jev_only = [
        r for r in rows if r["jev"][0] == r["label"] and r["hk"][0] != r["label"]
    ]
    print(
        f"Why: Haiku-only-correct rows {len(hk_only)}, Jev confidence on them "
        f"{spread([r['jev'][1] for r in hk_only])}; Jev-only-correct rows {len(jev_only)}, "
        f"of which {sum(1 for r in jev_only if r['jev'][1] < 1.0)} have Jev confidence < 1.0 "
        f"and so escalate somewhere on the grid."
    )
    for t in (0.5, 0.7, 0.9, 1.0):
        esc = [r for r in rows if escalates(r, t)]
        print(
            f"Escalated at t = {t:.2f}: {len(esc)} rows; Jev right on "
            f"{sum(1 for r in esc if r['jev'][0] == r['label'])}, Haiku right on "
            f"{sum(1 for r in esc if r['hk'][0] == r['label'])}, flat Haiku rows among them "
            f"{sum(1 for r in esc if r['flat'])}."
        )
    print(
        "\n### Policy B (descriptive): escalate, keep the higher own-confidence answer\n"
    )
    table(rows, "B")


def main():
    set_name = "full" if "--set" in sys.argv and sys.argv[-1] == "full" else "subset"
    rows = build(set_name)
    flat = [r for r in rows if r["flat"]]
    jev_right_on_flat = sum(1 for r in flat if r["jev"][0] == r["label"])
    print(f"# jev-cav cascade, set = {set_name}")
    print(
        f"Flat Haiku rows (every probability equal): {len(flat)}; Jev correct on {jev_right_on_flat} of them; "
        f"Jev confidence on them: {sorted(r['jev'][1] for r in flat)}"
    )
    report(rows, "Primary: all rows, flat Haiku rows as recorded")
    report([r for r in rows if not r["flat"]], "Sensitivity: flat Haiku rows dropped")


if __name__ == "__main__":
    main()
