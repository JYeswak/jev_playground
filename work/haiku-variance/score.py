#!/usr/bin/env python3
"""Scorer for bead jev-x5k: run-to-run variance of the Haiku incumbent on three live units.

Bar: docs/demos/upstream-repro/haiku-variance-20260924.md (committed before any rerun call).
The Jev rows of each unit are one committed run and are held fixed; Haiku run 1 is the committed
rows-haiku.jsonl, runs 2 and 3 are rows-haiku-run2.jsonl / rows-haiku-run3.jsonl beside it. Every
metric and paired test is the owning unit's own committed function, imported from its score.py:
  SST-5 Score      work/score-sst5/score.py        (jev-zui)
  SciFact Noul     work/noul-scifact/score.py      (jev-9er)
  Banking77 Choice work/choice-banking77/score.py  (jev-k3k, 10 intents)

Run: python3 work/haiku-variance/score.py [--bar]
--bar prints only the run-1 reproduction and the headroom, from committed files. Exit 1 when run 1
does not reproduce the committed headline numbers. Stdlib only, no key, no network.
"""

import importlib.util
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(HERE)
RUNS = ("rows-haiku.jsonl", "rows-haiku-run2.jsonl", "rows-haiku-run3.jsonl")


def unit(dirname):
    spec = importlib.util.spec_from_file_location(
        f"score_{dirname.replace('-', '_')}", os.path.join(WORK, dirname, "score.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def rows_at(dirname, name):
    path = os.path.join(WORK, dirname, name)
    if not os.path.exists(path):
        return None
    return [json.loads(line) for line in open(path) if line.strip()]


def binom(k, n):
    if n == 0:
        return 1.0
    m = min(k, n - k)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(m + 1)) / 2**n)


def count_verdict(a, b):
    p = binom(a, a + b)
    return ("WIN" if a > b else "LOSE") if p < 0.05 else "TIE", p


def headroom(a, b, pool_a, pool_b, broken):
    """Fewest Haiku answer changes that make broken(a', b') true. A change either removes one
    Jev-only row (a-1, at most pool_a) or adds one Haiku-only row (b+1, at most pool_b); every
    split is tried, so the count is the adversarial minimum (a lower bound on real harm)."""
    for k in range(0, pool_a + pool_b + 1):
        for i in range(0, min(k, pool_a) + 1):
            if k - i <= pool_b and broken(a - i, b + (k - i)):
                return k
    return None


def spread(xs, fmt="{}"):
    """Range across the runs present, formatted; 'n/a' with fewer than two runs."""
    xs = [x for x in xs if x is not None]
    return fmt.format(max(xs) - min(xs)) if len(xs) > 1 else "n/a"


def flips(preds):
    """Rows whose answer differs, for each pair of runs present."""
    out = {}
    have = [k for k, p in enumerate(preds) if p is not None]
    for x in have:
        for y in have:
            if x < y:
                out[f"{x + 1}v{y + 1}"] = sum(
                    1 for u, v in zip(preds[x], preds[y]) if u != v
                )
    return out


# ---------------------------------------------------------------- SST-5 (jev-zui)
def sst5():
    m = unit("score-sst5")
    d = "score-sst5"
    sample = m.load_jsonl(os.path.join(WORK, d, "sample.jsonl"))
    jev = m.evaluate(sample, m.arm_preds(sample, rows_at(d, "rows-jev.jsonl")), "round")
    runs = []
    for name in RUNS:
        rows = rows_at(d, name)
        if rows is None:
            runs.append(None)
            continue
        preds = m.arm_preds(sample, rows)
        ev = m.evaluate(sample, preds, "round")
        ao, bo, pm, ab, bb, ps = m.paired(jev, ev)
        fin = [r for r in rows if "score" in r]
        runs.append(
            {
                "correct": sum(1 for c, _, _ in ev if c),
                "mae": sum(e for _, e, _ in ev) / len(ev),
                "acc": (ao, bo, pm, m.verdict(ao, bo, pm)),
                "mae_sign": (ab, bb, ps, m.verdict(ab, bb, ps)),
                "levels": [lv for _, _, lv in ev],
                "ok": [c for c, _, _ in ev],
                "answered": len({r["i"] for r in fin}),
                "errors": sum(1 for r in rows if "error" in r),
                "flat": sum(
                    1 for r in fin if len(set(r["probabilities"].values())) == 1
                ),
                "prob_err": sum(1 for r in fin if r.get("probabilityError")),
                "prob_err_recorded": any("probabilityError" in r for r in fin),
            }
        )
    return {"unit": "SST-5 Score (jev-zui)", "n": len(sample), "jev": jev, "runs": runs}


# ---------------------------------------------------------------- SciFact (jev-9er)
def scifact():
    m = unit("noul-scifact")
    d = "noul-scifact"
    sample = m.load_jsonl(os.path.join(WORK, d, "sample.jsonl"))
    y = [1 if s["truth"] else 0 for s in sample]

    def arm(rows):
        preds = m.arm_probs(sample, rows)
        p = [r["noul"] if r is not None else 0.5 for r in preds]
        ok = [m.correct(pp, r, bool(t)) for pp, r, t in zip(p, preds, y)]
        return p, ok

    jp, jok = arm(rows_at(d, "rows-jev.jsonl"))
    runs = []
    for name in RUNS:
        rows = rows_at(d, name)
        if rows is None:
            runs.append(None)
            continue
        p, ok = arm(rows)
        jo = sum(1 for a, b in zip(jok, ok) if a and not b)
        xo = sum(1 for a, b in zip(jok, ok) if b and not a)
        verdict, pm = count_verdict(jo, xo)
        v = {"acc": (jo, xo, pm, verdict)}
        for key, fn, higher in (
            ("auc", m.auc, True),
            ("brier", m.brier, False),
            ("ece", m.ece, False),
        ):
            lo, hi = m.boot(fn, jp, p, y)
            better = (lo > 0) if higher else (hi < 0)
            worse = (hi < 0) if higher else (lo > 0)
            v[key] = (lo, hi, "WIN" if better else "LOSE" if worse else "TIE")
        fin = [r for r in rows if "noul" in r]
        runs.append(
            {
                "correct": sum(ok),
                "auc": m.auc(p, y),
                "brier": m.brier(p, y),
                "ece": m.ece(p, y),
                "v": v,
                "decisions": [pp > m.CUT for pp in p],
                "ok": ok,
                "p": p,
                "answered": len({r["i"] for r in fin}),
                "errors": sum(1 for r in rows if "error" in r),
                "at_half": sum(1 for r in fin if r["noul"] == 0.5),
                "prob_err": sum(1 for r in fin if r.get("probabilityError")),
                "prob_err_recorded": any("probabilityError" in r for r in fin),
            }
        )
    return {
        "unit": "SciFact Noul (jev-9er)",
        "n": len(sample),
        "jok": jok,
        "runs": runs,
    }


# ---------------------------------------------------------------- Banking77 (jev-k3k)
def banking():
    m = unit("choice-banking77")
    d = "choice-banking77"
    subset = m.load("subset.jsonl")
    counts = {}
    for it in subset:
        counts[it["intent"]] = counts.get(it["intent"], 0) + 1
    const_k = max(counts.values())
    jev = m.arm_stats("jev", subset, m.load("rows-jev.jsonl"))
    runs = []
    for name in RUNS:
        rows = rows_at(d, name)
        if rows is None:
            runs.append(None)
            continue
        h = m.arm_stats("haiku", subset, rows)
        b = sum(1 for i in jev["per_i"] if jev["per_i"][i] and not h["per_i"][i])
        c = sum(1 for i in jev["per_i"] if h["per_i"][i] and not jev["per_i"][i])
        p = m.mcnemar_exact(b, c)
        diff_pp = 100 * (jev["acc"] - h["acc"])
        if not (jev["acc"] >= m.FEASIBLE and h["acc"] >= m.FEASIBLE):
            verdict = "NOT-SCORED"
        elif jev["correct"] <= const_k:
            verdict = "LOSE"
        elif diff_pp < -m.MARGIN_PP:
            verdict = "LOSE"
        elif b > c and p < m.ALPHA:
            verdict = "WIN"
        else:
            verdict = "NON-INFERIOR"
        fin = m.final_rows(rows)
        ans = [r for r in fin.values() if "choice" in r]
        runs.append(
            {
                "correct": h["correct"],
                "mc": (b, c, p, verdict),
                "choices": [fin.get(it["i"], {}).get("choice") for it in subset],
                "ok": [h["per_i"][it["i"]] for it in subset],
                "answered": len(ans),
                "errors": sum(1 for r in fin.values() if "choice" not in r),
                "flat": sum(1 for r in ans if m.is_flat(r)),
                "zero_mass": sum(1 for r in ans if r.get("rawSum") == 0),
                "prob_err": sum(1 for r in ans if r.get("probabilityError")),
                "prob_err_recorded": any("probabilityError" in r for r in ans),
            }
        )
    return {
        "unit": "Banking77 Choice, 10 intents (jev-k3k)",
        "n": len(subset),
        "jev": jev,
        "const_k": const_k,
        "ids": [it["i"] for it in subset],
        "runs": runs,
    }


def reproduces(s, f, b):
    r1s, r1f, r1b = s["runs"][0], f["runs"][0], b["runs"][0]
    checks = [
        ("SST-5 Haiku 251/500", r1s["correct"] == 251),
        ("SST-5 Haiku MAE 0.556", round(r1s["mae"], 3) == 0.556),
        (
            "SST-5 McNemar 89 vs 67 TIE",
            r1s["acc"][:2] == (89, 67) and r1s["acc"][3] == "TIE",
        ),
        (
            "SST-5 sign 109 vs 75 WIN",
            r1s["mae_sign"][:2] == (109, 75) and r1s["mae_sign"][3] == "WIN",
        ),
        ("SciFact Haiku 351/400", r1f["correct"] == 351),
        (
            "SciFact McNemar 19 vs 9 TIE",
            r1f["v"]["acc"][:2] == (19, 9) and r1f["v"]["acc"][3] == "TIE",
        ),
        (
            "SciFact AUC/Brier/ECE WIN",
            all(r1f["v"][k][2] == "WIN" for k in ("auc", "brier", "ece")),
        ),
        ("Banking77 Haiku 362/400", r1b["correct"] == 362),
        (
            "Banking77 McNemar 25 vs 3 WIN",
            r1b["mc"][:2] == (25, 3) and r1b["mc"][3] == "WIN",
        ),
    ]
    return checks


def both_wrong(jev_ok, haiku_ok):
    """Rows neither arm got right: the pool from which a Haiku change can add a Haiku-only row."""
    return sum(1 for j, h in zip(jev_ok, haiku_ok) if not j and not h)


def bar(s, f, b):
    r1s, r1f, r1b = s["runs"][0], f["runs"][0], b["runs"][0]
    ab, bb = r1s["mae_sign"][:2]
    ao, bo = r1s["acc"][:2]
    fa, fx = r1f["v"]["acc"][:2]
    ba, bc = r1b["mc"][:2]
    jev_b = [b["jev"]["per_i"][i] for i in b["ids"]]
    return [
        # One change on a Jev-lower-error row (set Haiku's level to the label; Jev's error there is
        # above 0) moves both counts, which is the most harmful single change.
        (
            "SST-5 headline: MAE sign test WIN vs Haiku",
            f"{ab} vs {bb}",
            min(k for k in range(ab + 1) if count_verdict(ab - k, bb + k)[0] != "WIN"),
        ),
        (
            "SST-5 pass rule: accuracy not LOSE vs Haiku",
            f"{ao} vs {bo}",
            headroom(
                ao,
                bo,
                ao,
                both_wrong([c for c, _, _ in s["jev"]], r1s["ok"]),
                lambda a, c: count_verdict(a, c)[0] == "LOSE",
            ),
        ),
        (
            "SciFact pass rule: accuracy not LOSE vs Haiku",
            f"{fa} vs {fx}",
            headroom(
                fa,
                fx,
                fa,
                both_wrong(f["jok"], r1f["ok"]),
                lambda a, c: count_verdict(a, c)[0] == "LOSE",
            ),
        ),
        (
            "Banking77 headline: McNemar WIN vs Haiku",
            f"{ba} vs {bc}",
            headroom(
                ba,
                bc,
                ba,
                both_wrong(jev_b, r1b["ok"]),
                lambda x, y: not (x > y and binom(x, x + y) < 0.05),
            ),
        ),
        # Every change adds one Haiku-correct row; LOSE is Haiku more than 3.0 pp (12 rows) above Jev.
        (
            "Banking77 PASS: not LOSE (Haiku more than 12 rows above Jev)",
            f"Jev {b['jev']['correct']}, Haiku {r1b['correct']}",
            b["jev"]["correct"] + 13 - r1b["correct"],
        ),
    ]


def main(argv):
    s, f, b = sst5(), scifact(), banking()
    checks = reproduces(s, f, b)
    print("Run 1 (committed Haiku rows) reproduces the committed numbers:")
    for name, ok in checks:
        print(f"  {'ok ' if ok else 'BAD'} {name}")
    if not all(ok for _, ok in checks):
        print("run 1 does not reproduce; nothing else is scored")
        return 1

    print(
        "\nHeadroom from run 1 (fewest Haiku answer changes that break the verdict, placed adversarially)"
    )
    print("| Verdict | Run 1 | Headroom (rows) |")
    print("|---|---|---:|")
    hr = bar(s, f, b)
    for name, base, k in hr:
        print(f"| {name} | {base} | {k} |")
    if "--bar" in argv:
        return 0

    status = {}
    # ------------------------------------------------ SST-5
    print(f"\n## {s['unit']}, N = {s['n']}")
    print(
        "| Haiku run | Answered | Errors | Correct | MAE | Accuracy vs Jev (Jev-only / Haiku-only, p) | MAE sign vs Jev (Jev lower / Haiku lower, p) | Flat rows | Rows with probabilityError |"
    )
    print("|---|---:|---:|---:|---:|---|---|---:|---:|")
    for k, r in enumerate(s["runs"]):
        if r is None:
            print(f"| {k + 1} | NOT_RUN | | | | | | | |")
            continue
        pe = r["prob_err"] if r["prob_err_recorded"] else "not recorded"
        print(
            f"| {k + 1} | {r['answered']}/{s['n']} | {r['errors']} | {r['correct']} | {r['mae']:.3f} | "
            f"{r['acc'][0]} / {r['acc'][1]}, p={r['acc'][2]:.3g} {r['acc'][3]} | "
            f"{r['mae_sign'][0]} / {r['mae_sign'][1]}, p={r['mae_sign'][2]:.3g} {r['mae_sign'][3]} | {r['flat']} | {pe} |"
        )
    have = [r for r in s["runs"] if r is not None]
    fl = flips([r["levels"] if r else None for r in s["runs"]])
    print(f"rounded-level flips between Haiku runs: {fl}")
    print(
        f"spread: correct {spread([r['correct'] for r in have])} rows (gap to Jev 22), MAE {spread([r['mae'] for r in have], '{:.3f}')} (gap 0.068)"
    )
    full = len(have) == 3
    status["SST-5 headline MAE WIN"] = (
        "PENDING"
        if not full
        else "HOLDS"
        if all(r["mae_sign"][3] == "WIN" for r in have)
        else "RETRACTED"
    )
    status["SST-5 PASS"] = (
        "RETRACTED"
        if any("LOSE" in (r["acc"][3], r["mae_sign"][3]) for r in have)
        else "PENDING"
        if not full
        else "HOLDS"
    )
    # ------------------------------------------------ SciFact
    print(f"\n## {f['unit']}, N = {f['n']}")
    print(
        "| Haiku run | Answered | Errors | Correct | AUC | Brier | ECE | Accuracy vs Jev (p) | AUC diff 95% | Brier diff 95% | ECE diff 95% | Rows at 0.500 | Rows with probabilityError |"
    )
    print("|---|---:|---:|---:|---:|---:|---:|---|---|---|---|---:|---:|")
    for k, r in enumerate(f["runs"]):
        if r is None:
            print(f"| {k + 1} | NOT_RUN | | | | | | | | | | | |")
            continue
        v = r["v"]
        pe = r["prob_err"] if r["prob_err_recorded"] else "not recorded"
        print(
            f"| {k + 1} | {r['answered']}/{f['n']} | {r['errors']} | {r['correct']} | {r['auc']:.3f} | {r['brier']:.4f} | {r['ece']:.4f} | "
            f"{v['acc'][0]} / {v['acc'][1]}, p={v['acc'][2]:.3g} {v['acc'][3]} | "
            + " | ".join(
                f"{v[x][0]:+.4f} to {v[x][1]:+.4f} {v[x][2]}"
                for x in ("auc", "brier", "ece")
            )
            + f" | {r['at_half']} | {pe} |"
        )
    have = [r for r in f["runs"] if r is not None]
    print(
        f"decision flips (>0.5) between Haiku runs: {flips([r['decisions'] if r else None for r in f['runs']])}"
    )
    pairs = [
        (x, y)
        for x in range(3)
        for y in range(3)
        if x < y and f["runs"][x] and f["runs"][y]
    ]
    for x, y in pairs:
        dd = [abs(a - c) for a, c in zip(f["runs"][x]["p"], f["runs"][y]["p"])]
        print(
            f"  runs {x + 1}v{y + 1}: mean |noul diff| {sum(dd) / len(dd):.4f}, rows moved > 0.10: {sum(1 for z in dd if z > 0.10)}"
        )
    print(
        f"spread: correct {spread([r['correct'] for r in have])} (gap 10), AUC {spread([r['auc'] for r in have], '{:.3f}')} (gap 0.028), "
        f"Brier {spread([r['brier'] for r in have], '{:.4f}')} (gap 0.0293), ECE {spread([r['ece'] for r in have], '{:.4f}')} (gap 0.0423)"
    )
    full = len(have) == 3
    for key in ("auc", "brier", "ece"):
        status[f"SciFact {key.upper()} WIN"] = (
            "PENDING"
            if not full
            else "HOLDS"
            if all(r["v"][key][2] == "WIN" for r in have)
            else "RETRACTED"
        )
    status["SciFact PASS"] = (
        "RETRACTED"
        if any(
            "LOSE"
            in (
                r["v"]["acc"][3],
                r["v"]["auc"][2],
                r["v"]["brier"][2],
                r["v"]["ece"][2],
            )
            for r in have
        )
        else "PENDING"
        if not full
        else "HOLDS"
    )
    # ------------------------------------------------ Banking77
    print(f"\n## {b['unit']}, N = {b['n']}")
    print(
        "| Haiku run | Answered | Errors | Correct | McNemar vs Jev (Jev-only / Haiku-only, p) | Verdict | Flat rows | rawSum == 0 | Rows with probabilityError |"
    )
    print("|---|---:|---:|---:|---|---|---:|---:|---:|")
    for k, r in enumerate(b["runs"]):
        if r is None:
            print(f"| {k + 1} | NOT_RUN | | | | | | | |")
            continue
        pe = r["prob_err"] if r["prob_err_recorded"] else "not recorded"
        print(
            f"| {k + 1} | {r['answered']}/{b['n']} | {r['errors']} | {r['correct']} | {r['mc'][0]} / {r['mc'][1]}, p={r['mc'][2]:.3g} | "
            f"{r['mc'][3]} | {r['flat']} | {r['zero_mass']} | {pe} |"
        )
    have = [r for r in b["runs"] if r is not None]
    print(
        f"chosen-intent flips between Haiku runs: {flips([r['choices'] if r else None for r in b['runs']])}"
    )
    print(
        f"spread: correct {spread([r['correct'] for r in have])} rows (gap to Jev 22)"
    )
    full = len(have) == 3
    vs = [r["mc"][3] for r in have]
    status["Banking77 headline WIN"] = (
        "RETRACTED (PASS)"
        if any(v in ("LOSE", "NOT-SCORED") for v in vs)
        else "PENDING"
        if not full
        else "HOLDS"
        if all(v == "WIN" for v in vs)
        else "DOWNGRADED to NON-INFERIOR"
    )

    print("\nR1, the verdict on every Haiku run:")
    for k, v in status.items():
        print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
