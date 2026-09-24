#!/usr/bin/env python3
"""Run-to-run variance of the QuixBugs code-Score headline, bead jev-kz50. Stdlib, no key, no network.

Bar: docs/demos/upstream-repro/score-quixbugs-variance-20260924.md (committed before any rerun call).
Run 1 of each arm is the committed jev-2wc rows (rows-jev.jsonl, rows-haiku.jsonl); runs 2 and 3 are
rows-{jev,haiku}-run{2,3}.jsonl. Every scoring rule is imported from score.py unchanged: pair
outcomes, the sign test, AUC and its bootstrap, McNemar on "pair ordered correctly", the paired AUC
bootstrap, the pass rule and the zero-mass drop.

  python3 work/score-quixbugs/variance.py        full report; exit 1 unless run 1 x run 1 reproduces jev-2wc
  python3 work/score-quixbugs/variance.py --bar  run 1 reproduction and headroom only (no rerun rows needed)
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import score as S  # noqa: E402

COMMITTED = {
    "jev": (38, 2, 0),
    "haiku": (28, 10, 2),
    "mcnemar": (12, 2),
    "order": "WIN",
    "auc": "TIE",
    "pass": True,
}


def run_files(arm):
    return [f"rows-{arm}.jsonl", f"rows-{arm}-run2.jsonl", f"rows-{arm}-run3.jsonl"]


def load_run(names, idx, name):
    rows = S.load(os.path.join(HERE, name))
    if not rows:
        return None
    pairs, missing = S.arm_pairs(names, idx, rows)
    got = {r["i"] for r in rows if "score" in r}
    zero = {
        r["i"]
        for r in rows
        if "score" in r
        and isinstance(r.get("originalProbabilities"), dict)
        and sum(r["originalProbabilities"].values()) == 0
    }
    return {"pairs": pairs, "missing": missing, "rows": rows, "got": got, "zero": zero}


def judge(names, jev, hk, keep):
    """score.py's compare(), returned instead of printed."""
    ks = [k for k, n in enumerate(names) if n in keep]
    jp = [jev["pairs"][k] for k in ks]
    hp = [hk["pairs"][k] for k in ks]
    jo_, ho_ = S.outcomes(jp), S.outcomes(hp)
    jw, jl = jo_.count("W"), jo_.count("L")
    jsign = S.binom_two_sided(jw, jw + jl)
    jci = S.boot_ci(
        lambda ix: S.auc([jp[k][0] for k in ix], [jp[k][1] for k in ix]), len(ks)
    )
    jo = sum(1 for a, b in zip(jo_, ho_) if a == "W" and b != "W")
    ho = sum(1 for a, b in zip(jo_, ho_) if b == "W" and a != "W")
    pm = S.binom_two_sided(jo, jo + ho)
    order = (
        "WIN"
        if pm < S.ALPHA and jo > ho
        else "LOSE"
        if pm < S.ALPHA and ho > jo
        else "TIE"
    )

    def diff(ix):
        return S.auc([jp[k][0] for k in ix], [jp[k][1] for k in ix]) - S.auc(
            [hp[k][0] for k in ix], [hp[k][1] for k in ix]
        )

    lo, hi = S.boot_ci(diff, len(ks))
    aucv = "WIN" if lo > 0 else "LOSE" if hi < 0 else "TIE"
    sep = jw > jl and jsign < S.ALPHA and jci[0] > 0.5
    ok = sep and "LOSE" not in (order, aucv)
    return {
        "jev_wlt": (jw, jl, jo_.count("T")),
        "hk_wlt": (ho_.count("W"), ho_.count("L"), ho_.count("T")),
        "jo": jo,
        "ho": ho,
        "pm": pm,
        "order": order,
        "diff": diff(range(len(ks))),
        "ci": (lo, hi),
        "auc": aucv,
        "sep": sep,
        "pass": ok,
        "n": len(ks),
    }


def headroom(jo, ho):
    """Fewest Jev-only pairs that, moved to Haiku-only (the most harmful single change), end the WIN."""
    k = 0
    while jo - k > ho + k and S.binom_two_sided(jo - k, jo + ho) < S.ALPHA:
        k += 1
    return k


def flips(a, b):
    ao, bo = S.outcomes(a["pairs"]), S.outcomes(b["pairs"])
    pair_flips = sum(1 for x, y in zip(ao, bo) if x != y)
    score_flips = sum(
        1
        for (c1, b1), (c2, b2) in zip(a["pairs"], b["pairs"])
        for x, y in ((c1, c2), (b1, b2))
        if round(x) != round(y)
    )
    return pair_flips, score_flips


def main():
    sample = S.load(os.path.join(HERE, "sample.jsonl"))
    names = sorted({s["name"] for s in sample})
    idx = {(s["name"], s["variant"]): s["i"] for s in sample}
    runs = {
        arm: [load_run(names, idx, f) for f in run_files(arm)]
        for arm in ("jev", "haiku")
    }
    j1, h1 = runs["jev"][0], runs["haiku"][0]
    base = judge(names, j1, h1, set(names))
    ok = (
        base["jev_wlt"] == COMMITTED["jev"]
        and base["hk_wlt"] == COMMITTED["haiku"]
        and (base["jo"], base["ho"]) == COMMITTED["mcnemar"]
        and base["order"] == COMMITTED["order"]
        and base["auc"] == COMMITTED["auc"]
        and base["pass"] == COMMITTED["pass"]
    )
    print(
        f"run 1 x run 1: Jev W/L/T {base['jev_wlt']}, Haiku {base['hk_wlt']}, pair ordering {base['jo']} vs {base['ho']} "
        f"p={base['pm']:.3g} {base['order']}, AUC diff {base['diff']:+.3f} [{base['ci'][0]:+.3f}, {base['ci'][1]:+.3f}] {base['auc']}, "
        f"{'PASS' if base['pass'] else 'FAIL'} -> {'reproduces jev-2wc' if ok else 'DOES NOT reproduce jev-2wc'}"
    )
    if not ok:
        return 1
    print(
        f"headroom: {headroom(base['jo'], base['ho'])} pair(s) moved from Jev-only to Haiku-only ends the pair-ordering WIN"
    )
    if "--bar" in sys.argv:
        return 0

    present = {
        arm: [k for k, r in enumerate(rs) if r is not None] for arm, rs in runs.items()
    }
    print(
        f"runs present: Jev {[k + 1 for k in present['jev']]}, Haiku {[k + 1 for k in present['haiku']]}"
    )
    print(
        "\n| Arm | Run | W / L / T | Sign p | AUC | Mean correct / buggy | Unanswered pairs | Zero-mass rows |"
    )
    print("|---|---:|---|---:|---:|---|---:|---:|")
    for arm in ("jev", "haiku"):
        for k in present[arm]:
            r = runs[arm][k]
            o = S.outcomes(r["pairs"])
            w, lo = o.count("W"), o.count("L")
            a = S.auc([c for c, _ in r["pairs"]], [b for _, b in r["pairs"]])
            mc = sum(c for c, _ in r["pairs"]) / len(r["pairs"])
            mb = sum(b for _, b in r["pairs"]) / len(r["pairs"])
            print(
                f"| {arm} | {k + 1} | {w} / {lo} / {o.count('T')} | {S.binom_two_sided(w, w + lo):.3g} | {a:.3f} | {mc:.3f} / {mb:.3f} | {r['missing']} | {len(r['zero'])} |"
            )

    print(
        "\n| Jev run | Haiku run | Pairs | Pair ordering Jev-only / Haiku-only, p | Ordering | AUC diff [95%] | AUC | Jev separates | Pass | Without zero-mass: ordering / pass |"
    )
    print("|---:|---:|---:|---|---|---|---|---|---|---|")
    results = []
    name_of = {s["i"]: s["name"] for s in sample}
    for j in present["jev"]:
        for h in present["haiku"]:
            r = judge(names, runs["jev"][j], runs["haiku"][h], set(names))
            gone = {name_of[i] for i in runs["haiku"][h]["zero"]}
            r2 = (
                judge(names, runs["jev"][j], runs["haiku"][h], set(names) - gone)
                if gone
                else r
            )
            results.append((j, h, r, r2))
            print(
                f"| {j + 1} | {h + 1} | {r['n']} | {r['jo']} / {r['ho']}, {r['pm']:.3g} | {r['order']} | {r['diff']:+.3f} [{r['ci'][0]:+.3f}, {r['ci'][1]:+.3f}] | "
                f"{r['auc']} | {'yes' if r['sep'] else 'NO'} | {'PASS' if r['pass'] else 'FAIL'} | {r2['order']} / {'PASS' if r2['pass'] else 'FAIL'} |"
            )

    print(
        "\nR2 flips between runs of the same arm (pairs whose outcome changes / program scores whose rounded level changes):"
    )
    for arm in ("jev", "haiku"):
        ks = present[arm]
        for a in range(len(ks)):
            for b in range(a + 1, len(ks)):
                pf, sf = flips(runs[arm][ks[a]], runs[arm][ks[b]])
                print(
                    f"  {arm} run {ks[a] + 1} vs {ks[b] + 1}: {pf} pair outcomes, {sf} rounded levels"
                )

    n = len(results)
    wins = sum(
        1 for *_, r, r2 in results if r["order"] == "WIN" and r2["order"] == "WIN"
    )
    loses = sum(
        1
        for *_, r, r2 in results
        if "LOSE" in (r["order"], r2["order"], r["auc"], r2["auc"])
    )
    passes = sum(1 for *_, r, r2 in results if r["pass"] and r2["pass"])
    auc_wins = sum(
        1 for *_, r, r2 in results if r["auc"] == "WIN" and r2["auc"] == "WIN"
    )
    if n < 9:
        print(f"\nonly {n}/9 pairings present: no verdict")
        return 2
    if passes < n:
        order_v = "PASS RETRACTED"
    elif wins == n:
        order_v = "HOLDS"
    elif wins >= 5 and loses == 0:
        order_v = "DOWNGRADED"
    else:
        order_v = "RETRACTED to TIE"
    print(
        f"\nR1 pair-ordering WIN in {wins}/{n} pairings (both ways), any LOSE in {loses}, pass rule in {passes}/{n} -> {order_v}"
    )
    print(
        f"AUC (published TIE): WIN in {auc_wins}/{n}, LOSE in {sum(1 for *_, r, r2 in results if 'LOSE' in (r['auc'], r2['auc']))}/{n} -> {'TIE stands' if auc_wins < n else 'WIN in 9/9 (not claimed: the bar only tests the published verdicts)'}"
    )
    print(f"PASS (published): {'holds' if passes == n else 'RETRACTED'} ({passes}/{n})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
