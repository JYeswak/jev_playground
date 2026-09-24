#!/usr/bin/env python3
"""Scorer for bead jev-hg8: run-to-run variance of both arms on the two Noul claim-verification sets.

Bar: docs/demos/upstream-repro/noul-variance-20260924.md (committed before any new call).
Sets: work/noul-scifact (jev-9er) and work/noul-fever (jev-wx5). Every metric and test is imported
from work/noul-scifact/score.py, the scorer both units committed, so no rule is restated here.

Runs per set (a missing file is NOT_RUN):
  Jev    J1 rows-jev.jsonl (committed), JR rows-jev-rerun.jsonl (committed by jev-k2q / jev-5jp,
         identical question), J2 rows-jev-run2.jsonl, J3 rows-jev-run3.jsonl (new)
  Haiku  H1 rows-haiku.jsonl (committed), H2 rows-haiku-run2.jsonl, H3 rows-haiku-run3.jsonl
         (SciFact H2/H3 committed by jev-x5k; FEVER H2/H3 new)
Every Jev run is paired with every Haiku run.

Run: python3 work/noul-variance/score.py [--bar]
--bar prints only the reproduction of the committed verdicts and the headroom. Exit 1 when the
committed pairing does not reproduce. Stdlib only, no key, no network.
"""

import importlib.util
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(HERE)
SETS = (("SciFact", "noul-scifact", "jev-9er"), ("FEVER", "noul-fever", "jev-wx5"))
JEV_RUNS = (
    ("J1", "rows-jev.jsonl"),
    ("JR", "rows-jev-rerun.jsonl"),
    ("J2", "rows-jev-run2.jsonl"),
    ("J3", "rows-jev-run3.jsonl"),
)
HAIKU_RUNS = (
    ("H1", "rows-haiku.jsonl"),
    ("H2", "rows-haiku-run2.jsonl"),
    ("H3", "rows-haiku-run3.jsonl"),
)
METRICS = ("auc", "brier", "ece")
# The committed verdicts (receipts noul-scifact-20260924.md and noul-fever-20260924.md), J1 x H1.
COMMITTED = {
    "SciFact": {
        "jev": 361,
        "haiku": 351,
        "acc": (19, 9, "TIE"),
        "auc": "WIN",
        "brier": "WIN",
        "ece": "WIN",
    },
    "FEVER": {
        "jev": 379,
        "haiku": 376,
        "acc": (6, 3, "TIE"),
        "auc": "WIN",
        "brier": "WIN",
        "ece": "WIN",
    },
}

_spec = importlib.util.spec_from_file_location(
    "noul_score", os.path.join(WORK, "noul-scifact", "score.py")
)
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)


def binom(k, n):
    if n == 0:
        return 1.0
    m = min(k, n - k)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(m + 1)) / 2**n)


def count_verdict(a, b):
    p = binom(a, a + b)
    return ("WIN" if a > b else "LOSE") if p < S.ALPHA else "TIE", p


def interval_verdict(lo, hi, higher_better):
    if (lo > 0) if higher_better else (hi < 0):
        return "WIN"
    if (hi < 0) if higher_better else (lo > 0):
        return "LOSE"
    return "TIE"


def load_arm(d, name, sample, y):
    path = os.path.join(WORK, d, name)
    if not os.path.exists(path):
        return None
    rows = [json.loads(line) for line in open(path) if line.strip()]
    preds = S.arm_probs(sample, rows)
    p = [r["noul"] if r is not None else 0.5 for r in preds]
    ok = [S.correct(pp, r, bool(t)) for pp, r, t in zip(p, preds, y)]
    got = [r for r in preds if r is not None]
    flagged = {
        r["i"]
        for r in got
        if r.get("probabilityError") is not None
        or (
            isinstance(r.get("originalProbabilities"), dict)
            and sum(r["originalProbabilities"].values()) == 0
        )
    }
    return {
        "p": p,
        "ok": ok,
        "answered": len(got),
        "errors": sum(1 for r in rows if "error" in r),
        "models": sorted({r.get("model") for r in got}),
        "flagged": flagged,
        "debug_recorded": sum(1 for r in got if "probabilityError" in r),
    }


def pair(jev, haiku, y, keep=None):
    """Committed paired tests, Jev minus Haiku, on all rows or on the index list `keep`."""
    idx = keep if keep is not None else range(len(y))
    jp = [jev["p"][k] for k in idx]
    hp = [haiku["p"][k] for k in idx]
    jo_ok = [jev["ok"][k] for k in idx]
    ho_ok = [haiku["ok"][k] for k in idx]
    yy = [y[k] for k in idx]
    a = sum(1 for u, v in zip(jo_ok, ho_ok) if u and not v)
    b = sum(1 for u, v in zip(jo_ok, ho_ok) if v and not u)
    v, pm = count_verdict(a, b)
    out = {"acc": (a, b, pm, v)}
    for key, higher in (("auc", True), ("brier", False), ("ece", False)):
        lo, hi = S.boot(getattr(S, key), jp, hp, yy)
        out[key] = (lo, hi, interval_verdict(lo, hi, higher))
    return out


def bar1(jev, y):
    """Pass-rule part 1 on one Jev run: accuracy WIN over always-no, AUC interval above 0.5,
    Brier WIN over the base-rate constant."""
    n = len(y)
    prev = sum(y) / n
    no_ok = [t == 0 for t in y]
    a = sum(1 for u, v in zip(jev["ok"], no_ok) if u and not v)
    b = sum(1 for u, v in zip(jev["ok"], no_ok) if v and not u)
    acc = count_verdict(a, b)[0] == "WIN"
    lo, _ = S.boot(S.auc, jev["p"], None, y)
    auc = lo > 0.5
    _, hi = S.boot(S.brier, jev["p"], [prev] * n, y)
    return acc and auc and hi < 0, (acc, auc, hi < 0)


def headroom(a, b, pool_a, pool_b):
    """Fewest answer changes (either arm) turning accuracy into a Haiku LOSE-for-Jev: each change
    removes one Jev-only row or adds one Haiku-only row."""
    for k in range(pool_a + pool_b + 1):
        for i in range(min(k, pool_a) + 1):
            if k - i <= pool_b and count_verdict(a - i, b + k - i)[0] == "LOSE":
                return k
    return None


def spread(xs, fmt):
    xs = [x for x in xs if x is not None]
    return fmt.format(max(xs) - min(xs)) if len(xs) > 1 else "n/a"


def flips(runs):
    out = {}
    names = [n for n, r in runs if r is not None]
    arms = {n: r for n, r in runs if r is not None}
    for i, x in enumerate(names):
        for yname in names[i + 1 :]:
            dx = [u > S.CUT for u in arms[x]["p"]]
            dy = [u > S.CUT for u in arms[yname]["p"]]
            moved = [abs(u - v) for u, v in zip(arms[x]["p"], arms[yname]["p"])]
            out[f"{x}v{yname}"] = (
                sum(1 for u, v in zip(dx, dy) if u != v),
                sum(1 for m in moved if m > 0.10),
                sum(moved) / len(moved),
            )
    return out


def score_set(label, d, bead, bar_only):
    sample = S.load_jsonl(os.path.join(WORK, d, "sample.jsonl"))
    y = [1 if s["truth"] else 0 for s in sample]
    jev = [(n, load_arm(d, f, sample, y)) for n, f in JEV_RUNS]
    hk = [(n, load_arm(d, f, sample, y)) for n, f in HAIKU_RUNS]
    J = dict(jev)
    H = dict(hk)
    c = COMMITTED[label]
    base = pair(J["J1"], H["H1"], y)
    checks = [
        (f"{label} Jev J1 {c['jev']}/400", sum(J["J1"]["ok"]) == c["jev"]),
        (f"{label} Haiku H1 {c['haiku']}/400", sum(H["H1"]["ok"]) == c["haiku"]),
        (
            f"{label} accuracy {c['acc'][0]} vs {c['acc'][1]} {c['acc'][2]}",
            base["acc"][:2] == c["acc"][:2] and base["acc"][3] == c["acc"][2],
        ),
    ] + [(f"{label} {m.upper()} {c[m]}", base[m][2] == c[m]) for m in METRICS]
    print(f"\n## {label} ({bead}), N = {len(y)}")
    print("Committed pairing J1 x H1 reproduces:")
    for name, okk in checks:
        print(f"  {'ok ' if okk else 'BAD'} {name}")
    if not all(okk for _, okk in checks):
        return None, False
    ja = J["J1"]["ok"]
    ha = H["H1"]["ok"]
    both = sum(1 for u, v in zip(ja, ha) if u == v)
    hr = headroom(base["acc"][0], base["acc"][1], base["acc"][0], both)
    print(
        f"headroom, accuracy not-LOSE vs Haiku ({base['acc'][0]} vs {base['acc'][1]}): {hr} answer changes"
    )
    if bar_only:
        return None, True

    print(
        "\n| Run | Answered | Errors | Model(s) | Correct | AUC | Brier | ECE | Rows flagged by adapter debug |"
    )
    print("|---|---:|---:|---|---:|---:|---:|---:|---:|")
    for n, r in jev + hk:
        if r is None:
            print(f"| {n} | NOT_RUN | | | | | | | |")
            continue
        flag = len(r["flagged"]) if r["debug_recorded"] else "not recorded"
        print(
            f"| {n} | {r['answered']}/{len(y)} | {r['errors']} | {', '.join(r['models'])} | {sum(r['ok'])} | "
            f"{S.auc(r['p'], y):.3f} | {S.brier(r['p'], y):.4f} | {S.ece(r['p'], y):.4f} | {flag if n.startswith('H') else '-'} |"
        )

    print(
        "\nPass rule part 1 per Jev run (accuracy WIN vs always-no, AUC CI above 0.5, Brier WIN vs base rate):"
    )
    b1 = {}
    for n, r in jev:
        if r is None:
            continue
        passed, parts = bar1(r, y)
        b1[n] = passed
        print(f"  {n}: {'PASS' if passed else 'FAIL'} {parts}")

    print(
        "\n| Jev x Haiku | Accuracy (Jev-only / Haiku-only, p) | AUC diff 95% | Brier diff 95% | ECE diff 95% |"
    )
    print("|---|---|---|---|---|")
    tally = {k: [] for k in ("acc",) + METRICS}
    dropped_lose = False
    for jn, jr in jev:
        for hn, hr_ in hk:
            if jr is None or hr_ is None:
                continue
            v = pair(jr, hr_, y)
            for k in tally:
                tally[k].append(v[k][3] if k == "acc" else v[k][2])
            print(
                f"| {jn} x {hn} | {v['acc'][0]} / {v['acc'][1]}, p={v['acc'][2]:.3g} {v['acc'][3]} | "
                + " | ".join(
                    f"{v[m][0]:+.4f} to {v[m][1]:+.4f} {v[m][2]}" for m in METRICS
                )
                + " |"
            )
            if hr_["flagged"]:
                keep = [k for k, s in enumerate(sample) if s["i"] not in hr_["flagged"]]
                vd = pair(jr, hr_, y, keep)
                lose = "LOSE" in (vd["acc"][3],) + tuple(vd[m][2] for m in METRICS)
                dropped_lose = dropped_lose or lose
                print(
                    f"|   same, {len(hr_['flagged'])} flagged Haiku rows dropped | {vd['acc'][3]} | "
                    + " | ".join(vd[m][2] for m in METRICS)
                    + " |"
                )

    n_pairs = len(tally["acc"])
    full = n_pairs == len(JEV_RUNS) * len(HAIKU_RUNS)
    status = {}
    for m in METRICS:
        wins = sum(1 for v in tally[m] if v == "WIN")
        if not full:
            st = "PENDING"
        else:
            st = "HOLDS" if wins == n_pairs else "RETRACTED"
        status[f"{label} {m.upper()} WIN"] = (
            f"{st} ({wins}/{n_pairs} pairings WIN, {sum(1 for v in tally[m] if v == 'LOSE')} LOSE)"
        )
    acc_counts = {
        k: sum(1 for v in tally["acc"] if v == k) for k in ("WIN", "TIE", "LOSE")
    }
    any_lose = any("LOSE" in tally[k] for k in tally) or dropped_lose
    pass_ok = all(b1.values()) and not any_lose
    status[f"{label} accuracy vs Haiku"] = f"{acc_counts} over {n_pairs} pairings"
    status[f"{label} PASS"] = (
        "RETRACTED"
        if not pass_ok
        else "PENDING"
        if not full or len(b1) < len(JEV_RUNS)
        else "HOLDS"
    )

    print(
        "\nFlips between runs of the same arm (decision at > 0.5 / rows moved > 0.10 / mean |noul change|):"
    )
    for arm_name, runs in (("Jev", jev), ("Haiku", hk)):
        for k, (dec, moved, mean) in flips(runs).items():
            print(f"  {arm_name} {k}: {dec} / {moved} / {mean:.4f}")
    for arm_name, runs in (("Jev", jev), ("Haiku", hk)):
        have = [r for _, r in runs if r is not None]
        print(
            f"spread {arm_name}: correct {spread([sum(r['ok']) for r in have], '{}')}, "
            f"AUC {spread([S.auc(r['p'], y) for r in have], '{:.3f}')}, "
            f"Brier {spread([S.brier(r['p'], y) for r in have], '{:.4f}')}, "
            f"ECE {spread([S.ece(r['p'], y) for r in have], '{:.4f}')}"
        )
    return status, True


def main(argv):
    bar_only = "--bar" in argv
    allstatus = {}
    good = True
    for label, d, bead in SETS:
        st, ok = score_set(label, d, bead, bar_only)
        good = good and ok
        if st:
            allstatus.update(st)
    if not good:
        print("\ncommitted pairing does not reproduce; nothing else is scored")
        return 1
    if allstatus:
        print(
            "\nVerdicts under the bar (a WIN stands only if WIN on every Jev x Haiku pairing):"
        )
        for k, v in allstatus.items():
            print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
