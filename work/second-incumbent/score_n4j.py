#!/usr/bin/env python3
"""Keyless scorer for bead jev-n4j: grok-4.20 as the incumbent on SST-5 (jev-zui) and CLINC150
15-intent + out-of-scope (jev-qw8). Stdlib only; needs git (reads pinned files with `git show`).

Metric functions and verdict rules are the original units' own scorers at the commits their
receipts scored; samples and Jev rows come from those same commits:
  SST-5     work/score-sst5/score.py @ 576e60e; sample.jsonl @ ae161b6; rows-jev/haiku @ 576e60e
  CLINC150  work/choice-clinc150/score.py @ 2842340; subset.jsonl @ e0950ce; rows-jev/haiku @ 2842340
The grok rows are this directory's rows-{sst5,clinc150}-grok.jsonl. Bar:
docs/demos/upstream-repro/grok-incumbent-sst5-clinc-20260924.md (committed before any call).

  python3 work/second-incumbent/score_n4j.py    exit 1 if a Haiku self-check fails to reproduce
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from score import local_rows, pinned_module, rows_at, usage_line  # noqa: E402

SST5_SCORER, SST5_SAMPLE, SST5_ROWS = "576e60e", "ae161b6", "576e60e"
CLINC_SCORER, CLINC_SUBSET, CLINC_ROWS = "2842340", "e0950ce", "2842340"
RANK = {"LOSE": 0, "NON-INFERIOR": 1, "WIN": 2}
FAIL_LIMIT = (
    0.01  # more than 1% unanswered after the resume pass: no verdict for that unit
)


def sst5():
    S = pinned_module("sst5_score", SST5_SCORER, "work/score-sst5/score.py")
    sample = rows_at(SST5_SAMPLE, "work/score-sst5/sample.jsonl")
    jev = rows_at(SST5_ROWS, "work/score-sst5/rows-jev.jsonl")
    haiku = rows_at(SST5_ROWS, "work/score-sst5/rows-haiku.jsonl")
    grok = local_rows("rows-sst5-grok.jsonl")
    ev = {
        name: S.evaluate(sample, S.arm_preds(sample, rows), "round")
        for name, rows in (("jev", jev), ("haiku", haiku), ("grok", grok))
    }
    counts = [sum(1 for s in sample if s["label"] == k) for k in range(S.LEVELS)]
    majority = max(range(S.LEVELS), key=lambda k: (counts[k], -k))

    def pair(keep, other):
        idx = [k for k, s in enumerate(sample) if s["i"] in keep]
        sub = [sample[k] for k in idx]
        j = [ev["jev"][k] for k in idx]
        o = [ev[other][k] for k in idx]
        const = all(
            S.verdict(*S.paired(j, S.constant(sub, lv))[:3]) == "WIN"
            and S.verdict(*S.paired(j, S.constant(sub, lv))[3:]) == "WIN"
            for lv in (majority, 2)
        )
        ao, bo, pm, ab, bb, ps = S.paired(j, o)
        acc_v, mae_v = S.verdict(ao, bo, pm), S.verdict(ab, bb, ps)
        _, ok, n, _, _, mae = S.summary(other, o)
        _, jk, _, _, _, jmae = S.summary("jev", j)
        return {
            "n": n,
            "jev": (jk, jmae),
            "other": (ok, mae),
            "acc": (ao, bo, pm, acc_v),
            "mae": (ab, bb, ps, mae_v),
            "pass": const and "LOSE" not in (acc_v, mae_v),
        }

    all_i = {s["i"] for s in sample}
    check = pair(all_i, "haiku")
    ok = (
        check["other"][0] == 251
        and check["jev"][0] == 273
        and check["mae"][:2] == (109, 75)
    )
    print("## SST-5 Score (jev-zui), N = 500")
    print(
        f"self-check, Haiku rows @ {SST5_ROWS}: Jev 273/500, Haiku 251/500, MAE sign 109 vs 75 -> "
        f"{'reproduces' if ok else 'DOES NOT reproduce'}"
    )
    if not grok:
        print("no grok rows")
        return ok, None
    usage_line("grok sst5", grok)
    got = [r for r in grok if "score" in r]
    zero = {
        r["i"]
        for r in got
        if isinstance(r.get("originalProbabilities"), dict)
        and sum(r["originalProbabilities"].values()) == 0
    }
    rescaled = {r["i"] for r in got if r.get("probabilityError") is not None}
    flat = {r["i"] for r in got if len(set(r["probabilities"].values())) == 1}
    print(
        f"adapter debug: probability_errors set on {len(rescaled)}, zero-mass (original sum 0) on "
        f"{len(zero)}, flat distributions {len(flat)}, answered {len({r['i'] for r in got})}/500"
    )
    failed = len(sample) - len({r["i"] for r in got})
    if failed > FAIL_LIMIT * len(sample):
        print(f"RUN FAILED: {failed} rows unanswered (> 1%), no SST-5 verdict")
        return ok, None
    print(
        "\n| Rows | N | Jev exact / MAE | grok exact / MAE | Accuracy: Jev-only / grok-only, p, verdict "
        "| MAE: Jev lower / grok lower, p, verdict | Pass rule |"
    )
    print("|---|---:|---|---|---|---|---|")
    res = {}
    for title, keep in (
        ("all rows", all_i),
        (f"zero-mass dropped ({len(zero)})", all_i - zero),
    ):
        p = pair(keep, "grok")
        res[title.split(" (")[0]] = p
        a, m = p["acc"], p["mae"]
        print(
            f"| {title} | {p['n']} | {p['jev'][0]} / {p['jev'][1]:.3f} | {p['other'][0]} / {p['other'][1]:.3f} "
            f"| {a[0]} / {a[1]}, {a[2]:.3g}, {a[3]} | {m[0]} / {m[1]}, {m[2]:.3g}, {m[3]} "
            f"| {'PASS' if p['pass'] else 'FAIL'} |"
        )
    holds = all(p["mae"][3] == "WIN" for p in res.values())
    passes = all(p["pass"] for p in res.values())
    print(
        f"\nSST-5 pass rule vs grok: {'PASS' if passes else 'FAIL'}; headline MAE WIN vs grok "
        f"(all rows and zero-mass dropped): {'HOLDS' if holds else 'DOES NOT HOLD'}"
    )
    return ok, (passes, holds)


def clinc150():
    C = pinned_module("clinc_score", CLINC_SCORER, "work/choice-clinc150/score.py")
    subset = rows_at(CLINC_SUBSET, "work/choice-clinc150/subset.jsonl")
    jev = rows_at(CLINC_ROWS, "work/choice-clinc150/rows-jev.jsonl")
    haiku = rows_at(CLINC_ROWS, "work/choice-clinc150/rows-haiku.jsonl")
    grok = local_rows("rows-clinc150-grok.jsonl")

    def primaries(sub, jrows, orows, zero_as_none):
        pj, po = C.preds(sub, jrows), C.preds(sub, orows, zero_as_none=zero_as_none)
        const = sum(1 for it in sub if it["intent"] == C.OOS)
        overall = C.verdict(C.correct(sub, pj), C.correct(sub, po), const)
        hj = C.handled(sub, C.gate(sub, pj, 0.60, "peak"))
        ho = C.handled(sub, C.gate(sub, po, 0.60, "peak"))
        gated = C.verdict(hj, ho, const)
        ins = [k for k, it in enumerate(sub) if it["intent"] != C.OOS]
        feas = all(
            sum(C.correct(sub, p)[k] for k in ins) >= 0.5 * len(ins) for p in (pj, po)
        )
        return overall, gated, feas, po

    print("\n## CLINC150 15 intents + out-of-scope (jev-qw8), N = 750")
    ov, ga, _, _ = primaries(subset, jev, haiku, False)
    ok = ov[1:3] == (688, 681) and ga[1:3] == (685, 650)
    print(
        f"self-check, Haiku rows @ {CLINC_ROWS}: overall 688 vs 681, handled at peak >= 0.60 685 vs 650 -> "
        f"{'reproduces' if ok else 'DOES NOT reproduce'}"
    )
    if not grok:
        print("no grok rows")
        return ok, None
    usage_line("grok clinc150", grok)
    fin = C.final_rows(grok)
    zero = {i for i, r in fin.items() if "choice" in r and r.get("rawSum") == 0}
    rescaled = {
        i for i, r in fin.items() if "choice" in r and r.get("probabilityError", 0) > 0
    }
    print(
        f"adapter debug: probability_errors set on {len(rescaled)}, zero-mass (rawSum 0) on {len(zero)}, "
        f"answered {sum(1 for r in fin.values() if 'choice' in r)}/750"
    )
    failed = len(subset) - sum(1 for r in fin.values() if "choice" in r)
    if failed > FAIL_LIMIT * len(subset):
        print(f"RUN FAILED: {failed} rows unanswered (> 1%), no CLINC150 verdict")
        return ok, None
    print(
        "\n| Arm | Overall correct | Wilson 95% | In-scope | OOS recall | OOS precision | Failed | Zero-mass |"
    )
    print("|---|---|---|---|---|---|---:|---:|")
    print(C.arm_table("Jev", subset, C.preds(subset, jev), jev))
    print(C.arm_table("grok as shipped", subset, C.preds(subset, grok), grok))
    print(
        C.arm_table(
            "grok zero-mass = none",
            subset,
            C.preds(subset, grok, zero_as_none=True),
            grok,
        )
    )

    print(
        "\n| Reading | N | Overall: Jev / grok, Jev-only / grok-only, p, verdict "
        "| Handled at peak >= 0.60: Jev / grok, Jev-only / grok-only, p, verdict | Feasible |"
    )
    print("|---|---:|---|---|---|")
    kept = [it for it in subset if it["i"] not in zero]
    readings = {}
    for title, sub, zn in (
        ("as shipped", subset, False),
        ("zero-mass = none", subset, True),
        (f"zero-mass dropped ({len(zero)})", kept, False),
    ):
        o, g, feas, _ = primaries(sub, jev, grok, zn)
        readings[title.split(" (")[0]] = (o, g, feas)
        print(
            f"| {title} | {len(sub)} | {o[1]} / {o[2]}, {o[3]} / {o[4]}, {o[5]:.3g}, {o[0]} "
            f"| {g[1]} / {g[2]}, {g[3]} / {g[4]}, {g[5]:.3g}, {g[0]} | {'yes' if feas else 'NO'} |"
        )

    def worse(a, b):
        return a if RANK[a] <= RANK[b] else b

    rule = [readings["as shipped"], readings["zero-mass = none"]]
    feasible = all(r[2] for r in rule)
    overall_v = worse(rule[0][0][0], rule[1][0][0])
    gated_v = worse(rule[0][1][0], rule[1][1][0])
    dropped = readings["zero-mass dropped"]
    passes = feasible and "LOSE" not in (overall_v, gated_v)
    holds = gated_v == "WIN" and dropped[1][0] == "WIN"
    print(
        f"\nunit rule (worse for Jev of as shipped / zero-mass = none): overall {overall_v}, "
        f"handled at 0.60 {gated_v}; feasibility {'met' if feasible else 'NOT met'}; "
        f"zero-mass dropped: overall {dropped[0][0]}, handled {dropped[1][0]}"
    )
    print(
        f"CLINC150 pass rule vs grok: {'PASS' if passes else 'FAIL'}; gated WIN vs grok "
        f"(unit rule and zero-mass dropped): {'HOLDS' if holds else 'DOES NOT HOLD'}"
    )
    return ok, (passes, holds)


def main():
    ok1, r1 = sst5()
    ok2, r2 = clinc150()
    if not (ok1 and ok2):
        print("\nSELF-CHECK FAILED: a committed Haiku result does not reproduce")
        return 1
    if r1 and r2:
        print(
            f"\nSummary: SST-5 pass {'PASS' if r1[0] else 'FAIL'}, MAE WIN {'HOLDS' if r1[1] else 'DOES NOT HOLD'}; "
            f"CLINC150 pass {'PASS' if r2[0] else 'FAIL'}, gated WIN {'HOLDS' if r2[1] else 'DOES NOT HOLD'}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
