#!/usr/bin/env python3
"""Scorer for bead jev-qw8 (CLINC150 with out-of-scope rows). Stdlib only, no key, no network.

Run: python3 work/choice-clinc150/score.py
Reads subset.jsonl and rows-{jev,haiku}.jsonl beside this file. Rules frozen in
docs/demos/upstream-repro/choice-clinc150-20260924.md:
  prediction   = the chosen option mapped back to its dataset label ("none of the above" -> "oos");
                 last answered row per id; a row with no answer is wrong everywhere
  Haiku        = scored twice: as shipped, and with every zero-mass row (adapter debug rawSum == 0,
                 the all-zero map the adapter turns into a uniform answer for option #1) read as
                 "none of the above"; the verdict is the worse of the two for Jev
  gate         = route only when the chosen option is an intent and the arm's peak probability is
                 >= t (primary t = 0.60, the vendor's MIN_CHOICE_PROBABILITY); otherwise abstain
  paired tests = McNemar exact (two-sided binomial on discordant pairs)
"""

import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OOS = "oos"
ALPHA = 0.05
MARGIN_PP = 3.0
FEASIBLE = 0.5
PRIMARY_GATE = 0.60
PEAK_GATES = (0.60, 0.80, 0.90)
CONF_GATES = (0.5, 0.7, 0.9)
SHIP_MISROUTE = 0.02
SHIP_COVERAGE = 0.80
RANK = {"NOT-SCORED": -1, "LOSE": 0, "NON-INFERIOR": 1, "WIN": 2}


def load(name):
    path = os.path.join(HERE, name)
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def wilson(k, n, z=1.959964):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def mcnemar(b, c):
    n = b + c
    if n == 0:
        return 1.0
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(min(b, c) + 1)) / 2**n)


def nearest_rank(values, q):
    s = sorted(values)
    return s[max(0, math.ceil(q * len(s)) - 1)] if s else None


def final_rows(rows):
    out = {}
    for r in rows:
        if "choice" in r or r["i"] not in out or "choice" not in out[r["i"]]:
            out[r["i"]] = r
    return out


def preds(subset, rows, zero_as_none=False):
    """Per subset row: (pred label or None, peak probability, returned confidence, zero-mass)."""
    fin = final_rows(rows)
    out = []
    for item in subset:
        r = fin.get(item["i"])
        if r is None or "choice" not in r:
            out.append((None, 0.0, 0.0, False))
            continue
        zero = r.get("rawSum") == 0
        if zero and zero_as_none:
            out.append((OOS, 0.0, 0.0, True))
        else:
            out.append(
                (r["choice"], max(r["probabilities"].values()), r["confidence"], zero)
            )
    return out


def correct(subset, p):
    return [pr[0] is not None and pr[0] == it["intent"] for it, pr in zip(subset, p)]


def gate(subset, p, t, field):
    """Per row: 'route-right', 'route-wrong', or 'abstain' ('failed' for a row with no answer)."""
    out = []
    for it, (pred, peak, conf, _) in zip(subset, p):
        score = peak if field == "peak" else conf
        if pred is None:
            out.append("failed")
        elif pred != OOS and score >= t:
            out.append("route-right" if pred == it["intent"] else "route-wrong")
        else:
            out.append("abstain")
    return out


def handled(subset, g):
    """A row is handled when an in-scope request is routed right or an out-of-scope one is not routed."""
    return [
        (x == "route-right") if it["intent"] != OOS else (x == "abstain")
        for it, x in zip(subset, g)
    ]


def verdict(j, h, const_k):
    """jev-k3k's rule on two per-row correctness vectors (feasibility checked by the caller)."""
    n = len(j)
    jk, hk = sum(j), sum(h)
    b = sum(1 for x, y in zip(j, h) if x and not y)
    c = sum(1 for x, y in zip(j, h) if y and not x)
    p = mcnemar(b, c)
    diff = 100 * (jk - hk) / n
    if jk <= const_k or diff < -MARGIN_PP:
        lab = "LOSE"
    elif b > c and p < ALPHA:
        lab = "WIN"
    else:
        lab = "NON-INFERIOR"
    return lab, jk, hk, b, c, p, diff


def pct(k, n):
    return f"{k}/{n} ({100 * k / n:.1f}%)" if n else "n/a"


def arm_table(name, subset, p, rows):
    ins = [i for i, it in enumerate(subset) if it["intent"] != OOS]
    oos = [i for i, it in enumerate(subset) if it["intent"] == OOS]
    ok = correct(subset, p)
    n = len(subset)
    said_none = [i for i, pr in enumerate(p) if pr[0] == OOS]
    tp = sum(1 for i in said_none if subset[i]["intent"] == OOS)
    lo, hi = wilson(sum(ok), n)
    return (
        f"| {name} | {pct(sum(ok), n)} | {100 * lo:.1f}-{100 * hi:.1f}% | "
        f"{pct(sum(ok[i] for i in ins), len(ins))} | {pct(tp, len(oos))} | {pct(tp, len(said_none))} | "
        f"{sum(1 for pr in p if pr[0] is None)} | {sum(1 for pr in p if pr[3])} |"
    )


def main():
    subset = load("subset.jsonl")
    n = len(subset)
    n_oos = sum(1 for it in subset if it["intent"] == OOS)
    n_in = n - n_oos
    rows = {"jev": load("rows-jev.jsonl"), "haiku": load("rows-haiku.jsonl")}
    print(f"rows: {n} ({n_in} in-scope over 15 intents, {n_oos} out-of-scope)")
    print(
        f"constant always-none: overall {pct(n_oos, n)}, in-scope 0/{n_in}, OOS recall {n_oos}/{n_oos}"
    )

    arms = {"jev": preds(subset, rows["jev"])}
    arms["haiku (as shipped)"] = preds(subset, rows["haiku"])
    arms["haiku (zero-mass = none)"] = preds(subset, rows["haiku"], zero_as_none=True)
    if not rows["jev"] or not rows["haiku"]:
        print("NOT_RUN: an arm has no rows")
        return 0

    print(
        "\n| Arm | Overall correct | Wilson 95% | In-scope accuracy | OOS recall | OOS precision | Failed | Zero-mass rows |"
    )
    print("|---|---:|---|---:|---:|---:|---:|---:|")
    for name, p in arms.items():
        print(arm_table(name, subset, p, rows))

    print("\n| Arm | Answered | p50 / p95 ms | Tokens in / out | Model(s) |")
    print("|---|---:|---|---|---|")
    for arm in ("jev", "haiku"):
        fin = [r for r in final_rows(rows[arm]).values() if "choice" in r]
        lat = [r["latencyMs"] for r in fin]
        tin = sum(r["usage"]["input_tokens"] for r in fin)
        tout = sum(r["usage"]["output_tokens"] for r in fin)
        models = sorted({r["model"] for r in fin})
        print(
            f"| {arm} | {len(fin)}/{n} | {nearest_rank(lat, 0.5)} / {nearest_rank(lat, 0.95)} | "
            f"{tin:,} / {tout:,} | {', '.join(models)} |"
        )

    for field, gates, title in (
        (
            "peak",
            PEAK_GATES,
            "peak probability (one formula for both arms; 0.60 is primary)",
        ),
        ("confidence", CONF_GATES, "each arm's returned `confidence` (descriptive)"),
    ):
        print(f"\nGate on {title}: route only an intent at score >= t, else abstain")
        print(
            "| Arm | t | Routed right | Misrouted (in-scope / OOS) | Misroute rate | In-scope coverage | OOS abstained | Handled | Shippable (misroute <= 2%, coverage >= 80%) |"
        )
        print("|---|---:|---:|---|---:|---:|---:|---:|---|")
        for name, p in arms.items():
            for t in gates:
                g = gate(subset, p, t, field)
                rr = g.count("route-right")
                wi = sum(
                    1
                    for it, x in zip(subset, g)
                    if x == "route-wrong" and it["intent"] != OOS
                )
                wo = sum(
                    1
                    for it, x in zip(subset, g)
                    if x == "route-wrong" and it["intent"] == OOS
                )
                ab_o = sum(
                    1
                    for it, x in zip(subset, g)
                    if x == "abstain" and it["intent"] == OOS
                )
                mis = (wi + wo) / n
                cov = rr / n_in
                ship = mis <= SHIP_MISROUTE and cov >= SHIP_COVERAGE
                print(
                    f"| {name} | {t:.2f} | {rr} | {wi} / {wo} | {100 * mis:.1f}% | {100 * cov:.1f}% | "
                    f"{ab_o}/{n_oos} | {sum(handled(subset, g))}/{n} | {'yes' if ship else 'no'} |"
                )

    print("\nPaired, Jev vs each Haiku reading (McNemar exact):")
    print(
        "| Measure | Haiku reading | Jev | Haiku | Jev-only | Haiku-only | p | Verdict |"
    )
    print("|---|---|---:|---:|---:|---:|---:|---|")
    j = arms["jev"]
    finals = {}
    for reading in ("haiku (as shipped)", "haiku (zero-mass = none)"):
        h = arms[reading]
        jc, hc = correct(subset, j), correct(subset, h)
        ins = [i for i, it in enumerate(subset) if it["intent"] != OOS]
        feasible = (
            sum(jc[i] for i in ins) / n_in >= FEASIBLE
            and sum(hc[i] for i in ins) / n_in >= FEASIBLE
        )
        jg = handled(subset, gate(subset, j, PRIMARY_GATE, "peak"))
        hg = handled(subset, gate(subset, h, PRIMARY_GATE, "peak"))
        for measure, a, b2, const_k, primary in (
            ("overall correct (primary)", jc, hc, n_oos, True),
            (f"handled at peak >= {PRIMARY_GATE:.2f} (primary)", jg, hg, n_oos, True),
            ("in-scope correct", [jc[i] for i in ins], [hc[i] for i in ins], -1, False),
            (
                "OOS said none",
                [jc[i] for i in range(n) if i not in set(ins)],
                [hc[i] for i in range(n) if i not in set(ins)],
                -1,
                False,
            ),
        ):
            lab, jk, hk, b, c, p, _ = verdict(a, b2, const_k)
            if primary and not feasible:
                lab = "NOT-SCORED"
            if not primary:
                lab = "descriptive: " + (
                    "Jev better"
                    if b > c and p < ALPHA
                    else "Haiku better"
                    if c > b and p < ALPHA
                    else "no difference at alpha"
                )
            else:
                finals.setdefault(measure, []).append(lab)
            print(
                f"| {measure} | {reading} | {jk} | {hk} | {b} | {c} | {p:.3g} | {lab} |"
            )

    print("\nVerdicts (the worse for Jev over the two Haiku readings):")
    for measure, labs in finals.items():
        worst = min(labs, key=RANK.__getitem__)
        print(f"- {measure}: {worst}  ({' / '.join(labs)})")
    worst_all = min(
        (lab for labs in finals.values() for lab in labs), key=RANK.__getitem__
    )
    print(f"pass: {'PASS' if worst_all in ('WIN', 'NON-INFERIOR') else 'FAIL'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
