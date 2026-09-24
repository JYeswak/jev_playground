#!/usr/bin/env python3
"""Scorer for bead jev-qbc: run-to-run variance of the Jev arms of jev-zui (SST-5) and jev-k3k
(Banking77). Stdlib only, no key, no network.

Run:  python3 work/jev-variance/score.py          full report (reruns missing -> NOT_RUN)
      python3 work/jev-variance/score.py --bar    headroom only, from the committed run-1 files

Bar: docs/demos/upstream-repro/jev-variance-20260924.md (committed before the first rerun call).
Inputs, all committed:
  work/score-sst5/{sample,rows-haiku,rows-jev,rows-jev-run2,rows-jev-run3}.jsonl
  work/choice-banking77/{subset,rows-haiku,rows-jev,rows-jev-run2,rows-jev-run3}.jsonl
Scoring rules are the committed ones of each unit, restated here so this file stays runnable if
those scorers change; run 1 must reproduce the committed headline numbers or the script exits 1.
The Haiku rows are one run and are held fixed: every paired test is Jev run k vs that run.
"""

import json
import math
import os
import sys
from functools import cache
from itertools import combinations

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SST = os.path.join(ROOT, "work", "score-sst5")
B77 = os.path.join(ROOT, "work", "choice-banking77")
RUNS = ("rows-jev.jsonl", "rows-jev-run2.jsonl", "rows-jev-run3.jsonl")
ALPHA = 0.05
LEVELS = 5
FAILED = "FAILED"

# Committed headlines (receipts score-sst5-20260924.md, choice-banking77-20260924.md).
SST_RUN1 = {"correct": 273, "jev_better": 109, "haiku_better": 75, "haiku_mae": 0.556}
B77_RUN1 = {"correct": 384, "haiku": 362, "b": 25, "c": 3}
B77_MARGIN_ROWS = 12  # 3.0 pp of 400
B77_CONSTANT = 40  # always-activate_my_card


def load(path):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


@cache
def binom_p(k, n):
    """Exact two-sided binomial p at 0.5 (McNemar exact / sign test); both units use this."""
    if n == 0:
        return 1.0
    m = min(k, n - k)
    return min(1.0, 2 * sum(math.comb(n, j) for j in range(m + 1)) / 2**n)


def verdict(a, b):
    """a = rows favouring Jev, b = rows favouring the other; ties already dropped."""
    p = binom_p(a, a + b)
    if p < ALPHA and a > b:
        return "WIN", p
    if p < ALPHA and b > a:
        return "LOSE", p
    return "TIE", p


def headroom(a, b, t, still_holds, cross=True):
    """Fewest Jev rows whose answers must change to break still_holds(a, b).

    a = rows favouring Jev, b = rows favouring the other arm, t = rows that can move to b.
    Moves only ever hurt Jev, one row each: a->b (only when cross, i.e. an error-size comparison
    where one new Jev answer can turn a Jev-better row into an other-better row), a->tie, t->b.
    For a correctness test (cross=False) the other arm's answers are fixed, so a Jev-only-correct
    row can only become both-wrong and only a both-correct row can become other-only (t = both
    correct). Class moves are otherwise unrestricted, so this is a lower bound on the true
    minimum: a rerun that changes fewer Jev answers than this cannot change the verdict."""
    for k in range(1, a + t + 1):
        for x in range(k + 1 if cross else 1):  # a -> b
            for y in range(k - x + 1):  # a -> tie
                z = k - x - y  # t -> b
                if x + y <= a and z <= t and not still_holds(a - x - y, b + x + z):
                    return k
    return None


# ---------------------------------------------------------------- SST-5 (jev-zui)


def sst_level(score):
    return min(LEVELS - 1, max(0, math.floor(score + 0.5)))


def sst_eval(sample, rows):
    """Per row: (level or FAILED, correct, abs_error, raw score or None). Last answered row wins."""
    by_i = {r["i"]: r for r in rows if "score" in r}
    out = []
    for s in sample:
        y, r = s["label"], by_i.get(s["i"])
        if r is None:
            out.append((FAILED, False, max(y, LEVELS - 1 - y), None))
        else:
            lv = sst_level(r["score"])
            out.append((lv, lv == y, abs(lv - y), r["score"]))
    return out


def sst_paired(j, o):
    """(jev-only correct, other-only correct, jev lower err, other lower err, equal err)."""
    ao = sum(1 for x, y in zip(j, o) if x[1] and not y[1])
    bo = sum(1 for x, y in zip(j, o) if y[1] and not x[1])
    jb = sum(1 for x, y in zip(j, o) if x[2] < y[2])
    ob = sum(1 for x, y in zip(j, o) if y[2] < x[2])
    return ao, bo, jb, ob, len(j) - jb - ob


def sst_constant(sample, level):
    return [(level, s["label"] == level, abs(level - s["label"]), None) for s in sample]


def sst_run_verdict(sample, jev, haiku):
    """The committed jev-zui pass rule, plus the headline (MAE WIN vs Haiku)."""
    out = {}
    for name, other in (
        ("always 1", sst_constant(sample, 1)),
        ("always 2", sst_constant(sample, 2)),
        ("Haiku", haiku),
    ):
        ao, bo, jb, ob, _ = sst_paired(jev, other)
        out[name] = (verdict(ao, bo), verdict(jb, ob), (ao, bo, jb, ob))
    beats_constants = all(
        out[n][0][0] == "WIN" and out[n][1][0] == "WIN"
        for n in ("always 1", "always 2")
    )
    loses = "LOSE" in (out["Haiku"][0][0], out["Haiku"][1][0])
    return out, beats_constants and not loses


# ---------------------------------------------------------------- Banking77 (jev-k3k)


def b77_eval(subset, rows):
    """Per row: (choice or FAILED, correct). Last answered row per id wins."""
    by_i = {}
    for r in rows:
        if "choice" in r or r["i"] not in by_i or "choice" not in by_i[r["i"]]:
            by_i[r["i"]] = r
    out = []
    for s in subset:
        r = by_i.get(s["i"])
        if r is None or "choice" not in r:
            out.append((FAILED, False))
        else:
            out.append((r["choice"], r["choice"] == s["intent"]))
    return out


def b77_verdict(jev, haiku):
    """The committed jev-k3k rule. Returns (label, b, c, p, jev_correct)."""
    n = len(jev)
    jk = sum(1 for x in jev if x[1])
    hk = sum(1 for x in haiku if x[1])
    b = sum(1 for x, y in zip(jev, haiku) if x[1] and not y[1])
    c = sum(1 for x, y in zip(jev, haiku) if y[1] and not x[1])
    p = binom_p(b, b + c)
    if jk / n < 0.5 or hk / n < 0.5:
        label = "NOT-SCORED"
    elif jk <= B77_CONSTANT or jk < hk - B77_MARGIN_ROWS:
        label = "LOSE"
    elif b > c and p < ALPHA:
        label = "WIN"
    else:
        label = "NON-INFERIOR"
    return label, b, c, p, jk


# ---------------------------------------------------------------- shared reporting


def flips(x, y, key):
    return sum(1 for a, b in zip(x, y) if key(a) != key(b))


def cls(j, o, better):
    """Per-row class of Jev vs the other arm: J (Jev better), H (other better), T (equal)."""
    return [
        "J" if better(a, b) > 0 else "H" if better(a, b) < 0 else "T"
        for a, b in zip(j, o)
    ]


def pct(k, n):
    return f"{k}/{n} ({100 * k / n:.1f}%)"


def sst_report(bar_only):
    sample = load(os.path.join(SST, "sample.jsonl"))
    haiku = sst_eval(sample, load(os.path.join(SST, "rows-haiku.jsonl")))
    runs = [load(os.path.join(SST, f)) for f in RUNS]
    n = len(sample)
    ev1 = sst_eval(sample, runs[0])
    ao, bo, jb, ob, eq = sst_paired(ev1, haiku)
    got = {
        "correct": sum(1 for x in ev1 if x[1]),
        "jev_better": jb,
        "haiku_better": ob,
        "haiku_mae": round(sum(x[2] for x in haiku) / n, 3),
    }
    if got != SST_RUN1:
        print(
            f"SST-5 run 1 does not reproduce the committed receipt: {got}",
            file=sys.stderr,
        )
        sys.exit(1)

    print(
        "## SST-5 (jev-zui), N = 500, Jev Score rounded level vs committed Haiku rows\n"
    )
    h_mae = headroom(jb, ob, eq, lambda a, b: verdict(a, b)[0] == "WIN")
    both_ok = sum(1 for x, y in zip(ev1, haiku) if x[1] and y[1])
    h_acc = headroom(
        ao, bo, both_ok, lambda a, b: verdict(a, b)[0] != "LOSE", cross=False
    )
    h_const = []
    for lv in (1, 2):
        const = sst_constant(sample, lv)
        cao, cbo, cjb, cob, ceq = sst_paired(ev1, const)
        cboth = sum(1 for x, y in zip(ev1, const) if x[1] and y[1])
        h_const.append(
            min(
                headroom(
                    cao, cbo, cboth, lambda a, b: verdict(a, b)[0] == "WIN", cross=False
                ),
                headroom(cjb, cob, ceq, lambda a, b: verdict(a, b)[0] == "WIN"),
            )
        )
    print(
        "Headroom from run 1 (fewest changed Jev rows that could break it; lower bound):"
    )
    print(
        f"- headline, MAE sign test WIN vs Haiku ({jb} vs {ob}, {eq} equal): {h_mae} rows = {h_mae / n:.1%}"
    )
    print(
        f"- accuracy not LOSE vs Haiku ({ao} vs {bo}): {h_acc} rows = {h_acc / n:.1%}"
    )
    print(
        f"- beats always-1 / always-2 on accuracy and MAE: {h_const[0]} / {h_const[1]} rows"
    )
    if bar_only:
        return None

    evs = [sst_eval(sample, r) if r is not None else None for r in runs]
    print(
        "\n| Run | Rows file | Answered | Exact correct | MAE | Jev-only / Haiku-only correct | McNemar p | Acc verdict | Jev / Haiku lower err | Sign p | MAE verdict (headline) | Pass rule |"
    )
    print("|---|---|---:|---:|---:|---|---:|---|---|---:|---|---|")
    per_run = []
    for k, (f, ev) in enumerate(zip(RUNS, evs), 1):
        if ev is None:
            print(f"| {k} | {f} | NOT_RUN | | | | | | | | | |")
            per_run.append(None)
            continue
        out, passed = sst_run_verdict(sample, ev, haiku)
        (va, pa), (vm, pm), (a1, b1, j1, o1) = out["Haiku"]
        answered = sum(1 for x in ev if x[0] != FAILED)
        correct = sum(1 for x in ev if x[1])
        mae = sum(x[2] for x in ev) / n
        per_run.append((correct, mae, vm, passed))
        print(
            f"| {k} | {f} | {answered}/{n} | {correct}/{n} | {mae:.3f} | {a1} / {b1} | {pa:.3g} | {va} | "
            f"{j1} / {o1} | {pm:.3g} | {vm} | {'PASS' if passed else 'FAIL'} |"
        )

    done = [(k, ev) for k, ev in enumerate(evs, 1) if ev is not None]
    hcls = {k: cls(ev, haiku, lambda a, b: b[2] - a[2]) for k, ev in done}
    print("\nPairwise flips (rows that differ between two Jev runs, of 500):")
    print(
        "| Pair | Level flips | Correctness flips | Abs-error changes | Class vs Haiku changes (J/T/H) | Mean abs change of raw score | Level flips < headroom? |"
    )
    print("|---|---:|---:|---:|---:|---:|---|")
    for (k1, e1), (k2, e2) in combinations(done, 2):
        lf = flips(e1, e2, lambda x: x[0])
        raw = [
            abs(a[3] - b[3])
            for a, b in zip(e1, e2)
            if a[3] is not None and b[3] is not None
        ]
        cf = sum(1 for a, b in zip(hcls[k1], hcls[k2]) if a != b)
        print(
            f"| {k1} vs {k2} | {pct(lf, n)} | {pct(flips(e1, e2, lambda x: x[1]), n)} | "
            f"{pct(flips(e1, e2, lambda x: x[2]), n)} | {pct(cf, n)} | {sum(raw) / len(raw):.4f} | "
            f"{'yes, verdict cannot move' if lf < h_mae else 'no, decided by the test'} |"
        )
    if len(done) == 3:
        idx = [
            j
            for j, (a, b, c) in enumerate(zip(*(e for _, e in done)))
            if not (a[0] == b[0] == c[0])
        ]
        print(
            f"\nRows whose level is not identical in all three runs: {pct(len(idx), n)}"
        )
        print(
            "| i | Truth | Haiku level | Levels run 1 / 2 / 3 | Raw scores run 1 / 2 / 3 |"
        )
        print("|---:|---:|---:|---|---|")
        for j in idx:
            lv = " / ".join(str(e[j][0]) for _, e in done)
            raw = " / ".join(f"{e[j][3]:.3f}" for _, e in done)
            print(
                f"| {sample[j]['i']} | {sample[j]['label']} | {haiku[j][0]} | {lv} | {raw} |"
            )
    return per_run, h_mae


def b77_report(bar_only):
    subset = load(os.path.join(B77, "subset.jsonl"))
    haiku = b77_eval(subset, load(os.path.join(B77, "rows-haiku.jsonl")))
    runs = [load(os.path.join(B77, f)) for f in RUNS]
    n = len(subset)
    ev1 = b77_eval(subset, runs[0])
    label, b, c, _, jk = b77_verdict(ev1, haiku)
    hk = sum(1 for x in haiku if x[1])
    got = {"correct": jk, "haiku": hk, "b": b, "c": c}
    if got != B77_RUN1 or label != "WIN":
        print(
            f"Banking77 run 1 does not reproduce the committed receipt: {got} {label}",
            file=sys.stderr,
        )
        sys.exit(1)

    print(
        "\n## Banking77 10-intent (jev-k3k), N = 400, Jev Choice vs committed Haiku rows\n"
    )
    both = (
        n - b - c
    )  # both right + both wrong; only both-right rows can move to Haiku-only

    def still_win(bb, cc):
        # every harmful move costs Jev one correct row; the margin rule is far away (needs 34)
        lost = (b - bb) + (cc - c)
        return (
            bb > cc
            and binom_p(bb, bb + cc) < ALPHA
            and jk - lost >= hk - B77_MARGIN_ROWS
        )

    both_right = sum(1 for x, y in zip(ev1, haiku) if x[1] and y[1])
    h_win = headroom(b, c, both_right, still_win, cross=False)
    h_lose = (jk - (hk - B77_MARGIN_ROWS)) + 1
    print(
        "Headroom from run 1 (fewest changed Jev rows that could break it; lower bound):"
    )
    print(
        f"- headline WIN, McNemar {b} vs {c} ({both} concordant): {h_win} rows = {h_win / n:.1%}"
    )
    print(
        f"- PASS (not LOSE: within {B77_MARGIN_ROWS} rows of Haiku {hk}): {h_lose} rows = {h_lose / n:.1%}"
    )
    if bar_only:
        return None

    evs = [b77_eval(subset, r) if r is not None else None for r in runs]
    print(
        "\n| Run | Rows file | Answered | Correct | Accuracy | Jev-only / Haiku-only | McNemar p | Verdict (headline) |"
    )
    print("|---|---|---:|---:|---:|---|---:|---|")
    per_run = []
    for k, (f, ev) in enumerate(zip(RUNS, evs), 1):
        if ev is None:
            print(f"| {k} | {f} | NOT_RUN | | | | | |")
            per_run.append(None)
            continue
        lab, bb, cc, pp, kk = b77_verdict(ev, haiku)
        answered = sum(1 for x in ev if x[0] != FAILED)
        per_run.append((kk, lab))
        print(
            f"| {k} | {f} | {answered}/{n} | {kk}/{n} | {100 * kk / n:.1f}% | {bb} / {cc} | {pp:.3g} | {lab} |"
        )

    done = [(k, ev) for k, ev in enumerate(evs, 1) if ev is not None]

    def jcls(ev):
        return [(x[1], y[1]) for x, y in zip(ev, haiku)]

    print("\nPairwise flips (rows that differ between two Jev runs, of 400):")
    print(
        "| Pair | Choice flips | Correctness flips | Class vs Haiku changes | Choice flips < headroom? |"
    )
    print("|---|---:|---:|---:|---|")
    for (k1, e1), (k2, e2) in combinations(done, 2):
        cf = flips(e1, e2, lambda x: x[0])
        kc = sum(1 for a, b2 in zip(jcls(e1), jcls(e2)) if a != b2)
        print(
            f"| {k1} vs {k2} | {pct(cf, n)} | {pct(flips(e1, e2, lambda x: x[1]), n)} | {pct(kc, n)} | "
            f"{'yes, verdict cannot move' if cf < h_win else 'no, decided by the test'} |"
        )
    if len(done) == 3:
        idx = [
            j
            for j, (a, b2, c2) in enumerate(zip(*(e for _, e in done)))
            if not (a[0] == b2[0] == c2[0])
        ]
        print(
            f"\nRows whose choice is not identical in all three runs: {pct(len(idx), n)}"
        )
        print("| i | Truth | Haiku | Choice run 1 / 2 / 3 |")
        print("|---:|---|---|---|")
        for j in idx:
            ch = " / ".join(e[j][0] for _, e in done)
            print(
                f"| {subset[j]['i']} | {subset[j]['intent']} | {haiku[j][0]} | {ch} |"
            )
    return per_run, h_win


def main(argv):
    bar_only = "--bar" in argv
    sst = sst_report(bar_only)
    b77 = b77_report(bar_only)
    if bar_only:
        return 0

    print("\n## Verdicts under the committed bar\n")
    runs, _ = sst
    if None in runs:
        print("SST-5: INCOMPLETE (a rerun is NOT_RUN)")
    else:
        maes = [r[1] for r in runs]
        gap = SST_RUN1["haiku_mae"] - maes[0]
        spread = max(maes) - min(maes)
        mae_ok = all(r[2] == "WIN" for r in runs)
        pass_ok = all(r[3] for r in runs)
        print(
            f"- SST-5 MAE across runs: {', '.join(f'{m:.3f}' for m in maes)}; range {spread:.3f} vs committed gap {gap:.3f}"
        )
        print(
            f"  R1 headline (MAE WIN vs Haiku on every run): {'HOLDS' if mae_ok else 'RETRACTED'}"
        )
        print(
            f"  R1 pass rule (beats both constants, never loses to Haiku, every run): {'HOLDS' if pass_ok else 'RETRACTED'}"
        )
        print(
            f"  R3 magnitude (range < gap): {'REPORTABLE' if spread < gap else 'NOT REPORTABLE as a point estimate'}"
        )
        acc = [r[0] for r in runs]
        print(
            f"  exact correct across runs: {', '.join(map(str, acc))} (range {max(acc) - min(acc)})"
        )
    runs, _ = b77
    if None in runs:
        print("Banking77: INCOMPLETE (a rerun is NOT_RUN)")
    else:
        ks = [r[0] for r in runs]
        labs = [r[1] for r in runs]
        spread = max(ks) - min(ks)
        gap = B77_RUN1["correct"] - B77_RUN1["haiku"]
        if all(lab == "WIN" for lab in labs):
            head = "HOLDS"
        elif "LOSE" in labs or "NOT-SCORED" in labs:
            head = "RETRACTED (PASS retracted too)"
        else:
            head = "DOWNGRADED to NON-INFERIOR (PASS kept)"
        print(
            f"- Banking77 correct across runs: {', '.join(map(str, ks))}; range {spread} vs committed gap {gap}"
        )
        print(f"  R1 headline (WIN on every run): {head}")
        print(
            f"  R3 magnitude (range < gap): {'REPORTABLE' if spread < gap else 'NOT REPORTABLE as a point estimate'}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
