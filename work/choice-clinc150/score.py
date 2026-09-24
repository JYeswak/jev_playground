#!/usr/bin/env python3
"""Scorer for beads jev-qw8 and jev-pm3 (CLINC150 with out-of-scope rows). Stdlib only, no key.

Run: python3 work/choice-clinc150/score.py [--set full]
subset (jev-qw8): subset.jsonl, rows-{jev,haiku}.jsonl; rules in choice-clinc150-20260924.md.
full (jev-pm3): full.jsonl, rows-full-jev.jsonl, and the Haiku file chosen by the rule in
choice-clinc150-full-20260924.md: rows-full-haiku-prompted.jsonl if any row of the structured
probe (rows-full-haiku.jsonl) was rejected with Anthropic's grammar cap, else rows-full-haiku.jsonl.
An arm with more than 1% failed rows is NOT-SCORED on the full set. Rules shared by both:
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
import sys

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
GRAMMAR_CAP = "compiled grammar is too large"
USAGE_CAP = "You have reached your specified API usage limits"
FAIL_LIMIT = 0.01  # full set only


def set_files(name):
    """(rows file, jev rows, haiku rows, note on which Haiku run is scored)."""
    if name == "subset":
        return "subset.jsonl", "rows-jev.jsonl", "rows-haiku.jsonl", "structured"
    probe = load("rows-full-haiku.jsonl")
    capped = sum(1 for r in probe if GRAMMAR_CAP in r.get("error", ""))
    if capped:
        note = f"prompted JSON (structured probe: {capped}/{len(probe)} rows rejected with the grammar cap)"
        return (
            "full.jsonl",
            "rows-full-jev.jsonl",
            "rows-full-haiku-prompted.jsonl",
            note,
        )
    return "full.jsonl", "rows-full-jev.jsonl", "rows-full-haiku.jsonl", "structured"


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


def main(argv):
    set_name = argv[argv.index("--set") + 1] if "--set" in argv else "subset"
    fname, jev_file, haiku_file, haiku_note = set_files(set_name)
    subset = load(fname)
    n = len(subset)
    n_oos = sum(1 for it in subset if it["intent"] == OOS)
    n_in = n - n_oos
    n_intents = len({it["intent"] for it in subset if it["intent"] != OOS})
    rows = {"jev": load(jev_file), "haiku": load(haiku_file)}
    print(f"rows: {n} ({n_in} in-scope over {n_intents} intents, {n_oos} out-of-scope)")
    print(
        f"constant always-none: overall {pct(n_oos, n)}, in-scope 0/{n_in}, OOS recall {n_oos}/{n_oos}"
    )
    if set_name != "subset":
        print(f"Haiku rows scored: {haiku_file}, {haiku_note}")

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

    print(
        "\nDescriptive: peak probability on in-scope rows each arm answered right (why a fixed"
    )
    print(
        "peak gate costs one arm more coverage than the other), and the commonest errors"
    )
    print(
        "| Arm | In-scope right | Peak p25 / median | Right rows with peak < 0.60 | Top 5 errors (truth->answer) |"
    )
    print("|---|---:|---|---:|---|")
    for name, arm in (("jev", "jev"), ("haiku", "haiku")):
        p = arms["jev" if arm == "jev" else "haiku (as shipped)"]
        peaks = [
            pr[1]
            for it, pr in zip(subset, p)
            if it["intent"] != OOS and pr[0] == it["intent"]
        ]
        errs = {}
        for it, pr in zip(subset, p):
            if pr[0] != it["intent"]:
                key = f"{it['intent']}->{pr[0]}"
                errs[key] = errs.get(key, 0) + 1
        top = sorted(errs.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
        print(
            f"| {name} | {len(peaks)} | {nearest_rank(peaks, 0.25):.3f} / {nearest_rank(peaks, 0.5):.3f} | "
            f"{sum(1 for x in peaks if x < PRIMARY_GATE)} | {', '.join(f'{k} x{v}' for k, v in top)} |"
        )
    fin = [r for r in final_rows(rows["haiku"]).values() if "choice" in r]
    sums = [r["rawSum"] for r in fin if r.get("rawSum") is not None]
    print(
        f"\nHaiku adapter debug: {len(sums)}/{len(fin)} rows renormalized (raw sum "
        f"{min(sums, default=float('nan')):.2f}-{max(sums, default=float('nan')):.2f}), "
        f"{sum(1 for s in sums if s == 0)} zero-mass, {sum(r.get('nRetries', 0) for r in fin)} retries"
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

    failed = {
        arm: sum(1 for pr in arms[k] if pr[0] is None)
        for arm, k in (("jev", "jev"), ("haiku", "haiku (as shipped)"))
    }
    if set_name != "subset":
        over = [a for a, f in failed.items() if f > FAIL_LIMIT * n]
        print(
            f"\nFailed rows: jev {failed['jev']}, haiku {failed['haiku']} "
            f"(limit {int(FAIL_LIMIT * n)}){'; over the limit: ' + ', '.join(over) if over else ''}"
        )
        blocked = over == ["haiku"] and all(
            USAGE_CAP in r.get("error", "")
            for r in final_rows(rows["haiku"]).values()
            if "choice" not in r
        )
        if blocked:
            print(
                "Haiku failed rows all carry Anthropic's account usage-limit message: the Haiku arm is "
                "BLOCKED-until-cap, not a result"
            )
        if over:
            label = "NOT-SCORED (Haiku BLOCKED-until-cap)" if blocked else "NOT-SCORED"
            RANK.setdefault(label, -1)
            finals = {m: [label] for m in finals}
        by_domain(subset, arms)
        versus_subset(subset, arms)
        both_answered(subset, arms)

    print("\nVerdicts (the worse for Jev over the two Haiku readings):")
    for measure, labs in finals.items():
        worst = min(labs, key=RANK.__getitem__)
        print(f"- {measure}: {worst}  ({' / '.join(labs)})")
    worst_all = min(
        (lab for labs in finals.values() for lab in labs), key=RANK.__getitem__
    )
    if worst_all.startswith("NOT-SCORED (Haiku BLOCKED"):
        print("pass: BLOCKED (Haiku arm stopped by Anthropic's usage cap; not a FAIL)")
    else:
        print(f"pass: {'PASS' if worst_all in ('WIN', 'NON-INFERIOR') else 'FAIL'}")
    return 0


def both_answered(subset, arms):
    """Descriptive, NOT preregistered, no verdict: only the rows both arms answered (jev-pm3's
    Haiku arm stopped on Anthropic's account usage limit, so its failed rows are not answers)."""
    j, h = arms["jev"], arms["haiku (as shipped)"]
    idx = [i for i in range(len(subset)) if j[i][0] is not None and h[i][0] is not None]
    if len(idx) == len(subset):
        return
    items = [subset[i] for i in idx]
    jp, hp = [j[i] for i in idx], [h[i] for i in idx]
    n_in = sum(1 for it in items if it["intent"] != OOS)
    print(
        f"\nDescriptive, not preregistered: the {len(idx)} rows both arms answered "
        f"({n_in} in-scope, {len(idx) - n_in} OOS)"
    )
    print("| Measure | Jev | Haiku | Jev-only | Haiku-only | McNemar p |")
    print("|---|---:|---:|---:|---:|---:|")
    jc, hc = correct(items, jp), correct(items, hp)
    jg = handled(items, gate(items, jp, PRIMARY_GATE, "peak"))
    hg = handled(items, gate(items, hp, PRIMARY_GATE, "peak"))
    ins = [k for k, it in enumerate(items) if it["intent"] != OOS]
    oos = [k for k, it in enumerate(items) if it["intent"] == OOS]
    for label, a, b in (
        ("overall correct", jc, hc),
        (f"handled at peak >= {PRIMARY_GATE:.2f}", jg, hg),
        ("in-scope correct", [jc[k] for k in ins], [hc[k] for k in ins]),
        ("OOS said none", [jc[k] for k in oos], [hc[k] for k in oos]),
    ):
        bb = sum(1 for x, y in zip(a, b) if x and not y)
        cc = sum(1 for x, y in zip(a, b) if y and not x)
        print(
            f"| {label} | {pct(sum(a), len(a))} | {pct(sum(b), len(b))} | {bb} | {cc} | {mcnemar(bb, cc):.3g} |"
        )


def by_domain(subset, arms):
    """Descriptive: in-scope accuracy per CLINC domain, each arm (Haiku as shipped)."""
    doms = sorted({it["domain"] for it in subset if it["intent"] != OOS})
    print("\nDescriptive: in-scope accuracy by domain (450 rows each)")
    print("| Domain | Jev | Haiku |")
    print("|---|---:|---:|")
    for d in doms:
        idx = [i for i, it in enumerate(subset) if it.get("domain") == d]
        cells = []
        for k in ("jev", "haiku (as shipped)"):
            ok = correct(subset, arms[k])
            cells.append(pct(sum(ok[i] for i in idx), len(idx)))
        print(f"| {d} | {cells[0]} | {cells[1]} |")


def versus_subset(subset, arms):
    """Descriptive: the 750 jev-qw8 rows (matched by text; CLINC texts are unique), answered with
    16 options there and 151 here. The instructions differ too (car-and-commute vs virtual
    assistant), so this is the whole question changing, not the option count alone."""
    small = load("subset.jsonl")
    if not small:
        return
    at = {it["text"]: i for i, it in enumerate(subset)}
    idx = [at[it["text"]] for it in small]
    big_items = [subset[i] for i in idx]
    print("\nDescriptive: the 750 jev-qw8 rows, 16 options (qw8) vs 151 options (here)")
    print(
        "| Arm | Overall correct, 16 / 151 | In-scope correct, 16 / 151 | OOS said none, 16 / 151 | Handled at peak >= 0.60, 16 / 151 |"
    )
    print("|---|---|---|---|---|")
    for arm, key, small_file in (
        ("jev", "jev", "rows-jev.jsonl"),
        ("haiku", "haiku (as shipped)", "rows-haiku.jsonl"),
    ):
        sp = preds(small, load(small_file))
        bp = [arms[key][i] for i in idx]
        cells = []
        for items, p in ((small, sp), (big_items, bp)):
            ok = correct(items, p)
            ins = [ok[i] for i, it in enumerate(items) if it["intent"] != OOS]
            oos = [ok[i] for i, it in enumerate(items) if it["intent"] == OOS]
            h = handled(items, gate(items, p, PRIMARY_GATE, "peak"))
            cells.append((sum(ok), sum(ins), sum(oos), sum(h)))
        a, b = cells
        print(
            f"| {arm} | {a[0]} / {b[0]} | {a[1]} / {b[1]} of 450 | {a[2]} / {b[2]} of 300 | {a[3]} / {b[3]} |"
        )


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
