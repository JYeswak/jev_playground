#!/usr/bin/env python3
"""Scorer for bead jev-384m: does the full Banking77 77-intent WIN (jev-4jf) hold on 3 x 3 runs?

Bar: docs/demos/upstream-repro/choice-banking77-full-variance-20260924.md (committed before any
rerun call). Run 1 of each arm is jev-4jf's committed rows (rows-full-jev.jsonl and
rows-full-haiku-prompted.jsonl); runs 2 and 3 are -run2 / -run3 beside them. Every per-pairing
number uses this unit's own committed functions, imported from work/choice-banking77/score.py
(arm_stats, mcnemar_exact, is_flat and the FEASIBLE / MARGIN_PP / ALPHA constants); the verdict
rule is jev-4jf's, unchanged.

Run: python3 work/choice-banking77/variance_full.py [--bar]
--bar prints only the run-1 reproduction and the headroom. Exit 1 when run 1 x run 1 does not
reproduce jev-4jf's committed numbers (2467 vs 2267 of 3080, 326 vs 126, WIN); otherwise exit 0,
whatever the verdict. Stdlib only, no key, no network.
"""

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
JEV = ("rows-full-jev.jsonl", "rows-full-jev-run2.jsonl", "rows-full-jev-run3.jsonl")
HAIKU = (
    "rows-full-haiku-prompted.jsonl",
    "rows-full-haiku-prompted-run2.jsonl",
    "rows-full-haiku-prompted-run3.jsonl",
)
# jev-4jf committed (choice-banking77-full-20260924.md, Results).
COMMITTED = {"jev": 2467, "haiku": 2267, "b": 326, "c": 126, "verdict": "WIN"}


def load_unit():
    spec = importlib.util.spec_from_file_location(
        "score_choice_banking77", os.path.join(HERE, "score.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


m = load_unit()
FULL = m.load("full.jsonl")
CONST = max(
    sum(1 for it in FULL if it["intent"] == intent)
    for intent in {it["intent"] for it in FULL}
)
FAIL_LIMIT = (
    len(FULL) // 100
)  # jev-4jf: more than 1% failed rows (30) and the run is not scored


# The bar applies NOT-SCORED only "after resuming". Rows refused by the provider's account usage
# cap cannot be resumed until the cap lifts (Anthropic: "You have reached your specified API usage
# limits"), so such a run is BLOCKED, i.e. pending, and carries no verdict. Added after the first
# rerun calls, when the cap fired (2026-09-24); it changes no rule for runs that completed.
CAP_MESSAGE = "You have reached your specified API usage limits"


def blocked(s):
    errs = [r for r in s["final"].values() if "choice" not in r]
    return len(errs) > FAIL_LIMIT and all(
        CAP_MESSAGE in str(r.get("error", "")) for r in errs
    )


def verdict(jv, hv, b, c, p):
    """jev-4jf's rule, as score.py applies it: feasibility, constant, 3.0 pp margin, McNemar."""
    if blocked(jv) or blocked(hv):
        return "BLOCKED"
    if jv["failed"] > FAIL_LIMIT or hv["failed"] > FAIL_LIMIT:
        return "NOT-SCORED"
    if not (jv["acc"] >= m.FEASIBLE and hv["acc"] >= m.FEASIBLE):
        return "NOT-SCORED"
    if jv["correct"] <= CONST or 100 * (jv["acc"] - hv["acc"]) < -m.MARGIN_PP:
        return "LOSE"
    if b > c and p < m.ALPHA:
        return "WIN"
    return "NON-INFERIOR"


def discordant(jv, hv):
    b = sum(1 for i in jv["per_i"] if jv["per_i"][i] and not hv["per_i"][i])
    c = sum(1 for i in jv["per_i"] if hv["per_i"][i] and not jv["per_i"][i])
    return b, c


def sensitivity(jv, hv):
    """Descriptive, as jev-4jf reported: Haiku's flat rows dropped, then credited to Haiku."""
    flat = {i for i, r in hv["final"].items() if "choice" in r and m.is_flat(r)}
    keep = [i for i in jv["per_i"] if i not in flat]
    bd = sum(1 for i in keep if jv["per_i"][i] and not hv["per_i"][i])
    cd = sum(1 for i in keep if hv["per_i"][i] and not jv["per_i"][i])
    bc = sum(
        1 for i in jv["per_i"] if jv["per_i"][i] and not (hv["per_i"][i] or i in flat)
    )
    cc = sum(
        1 for i in jv["per_i"] if (hv["per_i"][i] or i in flat) and not jv["per_i"][i]
    )
    return (
        len(flat),
        (bd, cd, m.mcnemar_exact(bd, cd)),
        (bc, cc, m.mcnemar_exact(bc, cc)),
    )


def headroom_win(b, c, both_wrong):
    """Fewest Haiku answer changes that end the WIN (b <= c or McNemar p >= ALPHA). A change turns a
    Jev-only row into both-correct (b - 1) or a both-wrong row into Haiku-only (c + 1)."""
    for k in range(0, b + both_wrong + 1):
        for i in range(0, min(k, b) + 1):
            bb, cc = b - i, c + (k - i)
            if k - i <= both_wrong and (bb <= cc or m.mcnemar_exact(bb, cc) >= m.ALPHA):
                return k
    return None


def flips(finals):
    """Rows whose chosen intent differs, counted over ids answered in both runs."""
    have = [(n, f) for n, f in finals if f is not None]
    out = []
    for x in range(len(have)):
        for y in range(x + 1, len(have)):
            (nx, fx), (ny, fy) = have[x], have[y]
            both = [
                it["i"]
                for it in FULL
                if "choice" in fx.get(it["i"], {}) and "choice" in fy.get(it["i"], {})
            ]
            n = sum(1 for i in both if fx[i]["choice"] != fy[i]["choice"])
            out.append((nx, ny, n, len(both)))
    return out


def main(argv):
    bar_only = "--bar" in argv
    stats = {}
    for name in JEV + HAIKU:
        rows = m.load(name)
        stats[name] = m.arm_stats(name, FULL, rows) if rows else None

    j1, h1 = stats[JEV[0]], stats[HAIKU[0]]
    b, c = discordant(j1, h1)
    p = m.mcnemar_exact(b, c)
    v = verdict(j1, h1, b, c, p)
    got = {"jev": j1["correct"], "haiku": h1["correct"], "b": b, "c": c, "verdict": v}
    ok = got == COMMITTED
    print(
        f"run 1 x run 1 reproduces jev-4jf: {'yes' if ok else 'NO'} "
        f"(Jev {got['jev']}, Haiku {got['haiku']}, McNemar {b} / {c}, p = {p:.1e}, {v}; "
        f"committed {COMMITTED})"
    )
    both_wrong = sum(
        1 for i in j1["per_i"] if not j1["per_i"][i] and not h1["per_i"][i]
    )
    hw = headroom_win(b, c, both_wrong)
    lose_at = j1["correct"] + int(m.MARGIN_PP * len(FULL) / 100) + 1 - h1["correct"]
    print(
        f"headroom from run 1: WIN ends after {hw} Haiku answer changes "
        f"({100 * hw / len(FULL):.1f}% of {len(FULL)}); LOSE needs Haiku +{lose_at} correct "
        f"(above {j1['correct'] + int(m.MARGIN_PP * len(FULL) / 100)}); constant {CONST}/{len(FULL)}"
    )
    if not ok:
        print("FAIL: run 1 does not reproduce the committed jev-4jf numbers")
        return 1
    if bar_only:
        return 0

    print("\nPer run")
    print(
        "| Run | Arm | Answered | Failed | Correct | Accuracy | p50 / p95 ms | Tokens in / out | Flat |"
    )
    print("|---|---|---:|---:|---:|---:|---|---|---:|")
    for arm, names in (("Jev", JEV), ("Haiku-prompted", HAIKU)):
        for k, name in enumerate(names, 1):
            s = stats[name]
            if s is None:
                print(f"| {k} | {arm} | not run | | | | | | |")
                continue
            flat = sum(1 for r in s["final"].values() if "choice" in r and m.is_flat(r))
            print(
                f"| {k} | {arm} | {s['answered']} | {s['failed']} | {s['correct']} | "
                f"{100 * s['acc']:.1f}% | {s['p50']} / {s['p95']} | "
                f"{s['tokens'][0]:,} / {s['tokens'][1]:,} | {flat} |"
            )

    print("\nR1: all Jev-run x Haiku-run pairings, jev-4jf's rule")
    print(
        "| Jev | Haiku | Jev correct | Haiku correct | McNemar | p | verdict | "
        "flat dropped (b / c, p) | flat credited (b / c, p) |"
    )
    print("|---|---|---:|---:|---|---:|---|---|---|")
    verdicts = []
    for jk, jn in enumerate(JEV, 1):
        for hk, hn in enumerate(HAIKU, 1):
            jv, hv = stats[jn], stats[hn]
            if jv is None or hv is None:
                print(f"| {jk} | {hk} | | | | | PENDING | | |")
                verdicts.append("PENDING")
                continue
            bb, cc = discordant(jv, hv)
            pp = m.mcnemar_exact(bb, cc)
            vv = verdict(jv, hv, bb, cc, pp)
            verdicts.append(vv)
            nflat, drop, cred = sensitivity(jv, hv)
            print(
                f"| {jk} | {hk} | {jv['correct']} | {hv['correct']} | {bb} / {cc} | {pp:.1e} | {vv} | "
                f"{nflat}: {drop[0]} / {drop[1]}, {drop[2]:.1e} | "
                f"{cred[0]} / {cred[1]}, {cred[2]:.1e} |"
            )

    print(
        "\nR2: answer flips between runs of the same arm (chosen intent differs), against the "
        f"run-1 WIN headroom of {hw}"
    )
    for arm, names in (("Jev", JEV), ("Haiku-prompted", HAIKU)):
        finals = [
            (k + 1, stats[n]["final"] if stats[n] else None)
            for k, n in enumerate(names)
        ]
        for x, y, n, both in flips(finals):
            print(f"  {arm} run {x} vs run {y}: {n} of {both} answered in both")

    wins = verdicts.count("WIN")
    pending = verdicts.count("PENDING")
    held = verdicts.count("BLOCKED")
    bad = [x for x in verdicts if x in ("LOSE", "NOT-SCORED")]
    if pending or held:
        headline = (
            f"PENDING, no verdict ({held} pairing(s) BLOCKED-until-cap, {pending} not run; "
            f"WIN so far in {wins} of {9 - held - pending} scorable)"
        )
    elif bad:
        headline = (
            f"PASS RETRACTED ({len(bad)} pairing(s) {', '.join(sorted(set(bad)))})"
        )
    elif wins == 9:
        headline = "HOLDS (WIN in 9/9 pairings; PASS 9/9)"
    elif wins >= 5:
        headline = f"DOWNGRADED (WIN in {wins}/9 pairings, no LOSE; PASS kept)"
    else:
        headline = (
            f"RETRACTED to NON-INFERIOR (WIN in {wins}/9 pairings, no LOSE; PASS kept)"
        )
    print(f"\nVerdict under the bar: {headline}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
