#!/usr/bin/env python3
"""Run-to-run variance of the Yelp Score headline, bead jev-91u. Stdlib only, no key, no network.

Bar: docs/demos/upstream-repro/score-yelp-variance-20260924.md (committed before any rerun call).
Run 1 of each arm is the committed jev-76o rows (rows-jev.jsonl, rows-haiku.jsonl); runs 2 and 3
are rows-{jev,haiku}-run{2,3}.jsonl. Scoring rules are imported from score.py unchanged.

  python3 work/score-yelp/variance.py         full report; exit 1 unless run 1 reproduces jev-76o
  python3 work/score-yelp/variance.py --bar   headroom from run 1 only
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import score as S  # noqa: E402

RUN1 = {"jev": (341, 0.348), "haiku": (323, 0.384)}  # committed at df13f17
MAJORITY = 0  # jev-76o: label counts 117/107/100/90/86


def run_files(arm):
    return [f"rows-{arm}.jsonl", f"rows-{arm}-run2.jsonl", f"rows-{arm}-run3.jsonl"]


def load_run(sample, name):
    rows = S.load_jsonl(os.path.join(HERE, name))
    if not rows:
        return None
    preds = S.arm_preds(sample, rows)
    zero = {
        r["i"]
        for r in rows
        if "score" in r
        and isinstance(r.get("originalProbabilities"), dict)
        and sum(r["originalProbabilities"].values()) == 0
    }
    rescaled = {
        r["i"] for r in rows if "score" in r and r.get("probabilityError") is not None
    }
    return {
        "name": name,
        "ev": S.evaluate(sample, preds, "round"),
        "answered": sum(1 for p in preds if p is not None),
        "errors": sum(1 for r in rows if "error" in r),
        "zero": zero,
        "rescaled": rescaled,
        "tokens": (
            sum(p["usage"]["input_tokens"] or 0 for p in preds if p is not None),
            sum(p["usage"]["output_tokens"] or 0 for p in preds if p is not None),
        ),
    }


def acc_mae(ev):
    return sum(1 for c, _, _ in ev if c), sum(e for _, e, _ in ev) / len(ev)


def pairing(sample, jev, hk, drop=frozenset()):
    idx = [k for k, s in enumerate(sample) if s["i"] not in drop]
    sub = [sample[k] for k in idx]
    j = [jev["ev"][k] for k in idx]
    h = [hk["ev"][k] for k in idx]
    ao, bo, pm, ab, bb, ps = S.paired(j, h)
    acc_v, mae_v = S.verdict(ao, bo, pm), S.verdict(ab, bb, ps)
    beats = all(
        S.verdict(*S.paired(j, S.constant(sub, lv))[:3]) == "WIN"
        and S.verdict(*S.paired(j, S.constant(sub, lv))[3:]) == "WIN"
        for lv in (MAJORITY, 2)
    )
    passed = beats and "LOSE" not in (acc_v, mae_v)
    return {
        "n": len(idx),
        "acc": (ao, bo, pm, acc_v),
        "mae": (ab, bb, ps, mae_v),
        "pass": passed,
    }


def headroom(ab, bb):
    """Fewest Jev rows that, moved from 'Jev lower error' to 'Haiku lower error' (the most harmful
    single-row change), make the sign test non-significant or not in Jev's favour."""
    n = ab + bb
    k = 0
    while S.binom_two_sided(ab - k, n) < S.ALPHA and ab - k > bb + k:
        k += 1
    return k


def flips(a, b):
    return sum(1 for x, y in zip(a["ev"], b["ev"]) if x[2] != y[2])


def main():
    sample = S.load_jsonl(os.path.join(HERE, "sample.jsonl"))
    runs = {
        arm: [load_run(sample, f) for f in run_files(arm)] for arm in ("jev", "haiku")
    }
    r1 = {arm: acc_mae(runs[arm][0]["ev"]) for arm in ("jev", "haiku")}
    ok = all(
        r1[arm][0] == RUN1[arm][0] and round(r1[arm][1], 3) == RUN1[arm][1]
        for arm in r1
    )
    print(
        f"run 1 reproduces jev-76o (Jev {r1['jev'][0]}/500 MAE {r1['jev'][1]:.3f}, "
        f"Haiku {r1['haiku'][0]}/500 MAE {r1['haiku'][1]:.3f}): {'yes' if ok else 'NO'}"
    )
    if not ok:
        return 1
    p1 = pairing(sample, runs["jev"][0], runs["haiku"][0])
    ab, bb = p1["mae"][0], p1["mae"][1]
    print(
        f"\nHeadroom from run 1: MAE sign test {ab} vs {bb}, p = {p1['mae'][2]:.4f}; "
        f"{headroom(ab, bb)} row(s) moved from Jev-lower to Haiku-lower error make it a TIE; "
        f"accuracy McNemar {p1['acc'][0]} vs {p1['acc'][1]}, p = {p1['acc'][2]:.4f} (TIE already)."
    )
    if "--bar" in sys.argv:
        return 0

    print("\n## Per run\n")
    print(
        "| Arm | Run | File | Answered | Error rows | Exact correct | MAE | Zero-mass | probability_errors | Tokens in / out |"
    )
    print("|---|---:|---|---:|---:|---:|---:|---:|---:|---|")
    for arm in ("jev", "haiku"):
        for k, r in enumerate(runs[arm], 1):
            if r is None:
                print(
                    f"| {arm} | {k} | {run_files(arm)[k - 1]} | missing | | | | | | |"
                )
                continue
            c, m = acc_mae(r["ev"])
            print(
                f"| {arm} | {k} | {r['name']} | {r['answered']}/500 | {r['errors']} | {c}/500 | {m:.3f} "
                f"| {len(r['zero'])} | {len(r['rescaled'])} | {r['tokens'][0]:,} / {r['tokens'][1]:,} |"
            )
    have = {arm: [r for r in runs[arm] if r is not None] for arm in runs}

    print(
        "\n## R2: per-row level flips between runs of the same arm (headroom above)\n"
    )
    for arm in ("jev", "haiku"):
        rs = runs[arm]
        pairs = [(a, b) for a in range(3) for b in range(a + 1, 3) if rs[a] and rs[b]]
        cells = ", ".join(
            f"run {a + 1} vs {b + 1}: {flips(rs[a], rs[b])}" for a, b in pairs
        )
        print(f"- {arm}: {cells or 'fewer than two runs'}")

    print("\n## R3: three-run spread against the run-1 gap\n")
    gap_acc = r1["jev"][0] - r1["haiku"][0]
    gap_mae = r1["haiku"][1] - r1["jev"][1]
    for arm in ("jev", "haiku"):
        vals = [acc_mae(r["ev"]) for r in have[arm]]
        cs, ms = [v[0] for v in vals], [v[1] for v in vals]
        print(
            f"- {arm}: exact correct {cs} (range {max(cs) - min(cs)} vs gap {gap_acc}); "
            f"MAE {[round(m, 3) for m in ms]} (range {max(ms) - min(ms):.3f} vs gap {gap_mae:.3f})"
        )

    print("\n## R1: every Jev run x Haiku run pairing\n")
    print(
        "| Jev run | Haiku run | N | Acc Jev-only / Haiku-only | McNemar p | Acc | MAE Jev-lower / Haiku-lower | Sign p | MAE | Pass rule | Zero-mass dropped: MAE / pass |"
    )
    print("|---:|---:|---:|---|---:|---|---|---:|---|---|---|")
    wins = passes = total = 0
    wins_zero = passes_zero = loses = 0
    for a, jr in enumerate(runs["jev"], 1):
        for b, hr in enumerate(runs["haiku"], 1):
            if jr is None or hr is None:
                continue
            p = pairing(sample, jr, hr)
            pz = pairing(sample, jr, hr, frozenset(hr["zero"]))
            total += 1
            wins += p["mae"][3] == "WIN"
            passes += p["pass"]
            wins_zero += pz["mae"][3] == "WIN"
            passes_zero += pz["pass"]
            loses += "LOSE" in (p["acc"][3], p["mae"][3], pz["acc"][3], pz["mae"][3])
            print(
                f"| {a} | {b} | {p['n']} | {p['acc'][0]} / {p['acc'][1]} | {p['acc'][2]:.3f} | {p['acc'][3]} "
                f"| {p['mae'][0]} / {p['mae'][1]} | {p['mae'][2]:.3f} | {p['mae'][3]} | {'PASS' if p['pass'] else 'FAIL'} "
                f"| {pz['mae'][3]} ({pz['n']} rows) / {'PASS' if pz['pass'] else 'FAIL'} |"
            )

    # Descriptive, not a rule: per-row mean absolute error over each arm's runs.
    jm = [
        sum(r["ev"][k][1] for r in have["jev"]) / len(have["jev"])
        for k in range(len(sample))
    ]
    hm = [
        sum(r["ev"][k][1] for r in have["haiku"]) / len(have["haiku"])
        for k in range(len(sample))
    ]
    jl = sum(1 for x, y in zip(jm, hm) if x < y)
    hl = sum(1 for x, y in zip(jm, hm) if y < x)
    print(
        f"\nDescriptive: per-row error averaged over each arm's runs, sign test Jev lower {jl} vs "
        f"Haiku lower {hl}, p = {S.binom_two_sided(jl, jl + hl):.4f}; mean MAE Jev "
        f"{sum(jm) / len(jm):.3f}, Haiku {sum(hm) / len(hm):.3f}"
    )

    print(
        f"\nMAE WIN in {wins}/{total} pairings (zero-mass dropped: {wins_zero}/{total}); "
        f"pass rule PASS in {passes}/{total} (zero-mass dropped: {passes_zero}/{total}); "
        f"pairings with any LOSE: {loses}"
    )
    if total < 9:
        print(f"HEADLINE: INCOMPLETE ({total}/9 pairings available)")
        return 0
    if loses or passes < 9 or passes_zero < 9:
        print(
            "HEADLINE: PASS RETRACTED (a pairing fails the pass rule or loses to Haiku)"
        )
    elif wins == 9 and wins_zero == 9:
        print(
            "HEADLINE: HOLDS (MAE WIN in 9/9 pairings, with and without zero-mass rows)"
        )
    elif min(wins, wins_zero) >= 5:
        print(
            "HEADLINE: DOWNGRADED to 'Jev's MAE is lower in direction; significant in a majority "
            "of pairings, not in all' (PASS kept)"
        )
    else:
        print("HEADLINE: RETRACTED to 'MAE TIE with Haiku' (PASS kept: no LOSE)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
