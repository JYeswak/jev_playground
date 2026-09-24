#!/usr/bin/env python3
"""Keyless scorer for bead jev-dsu. Stdlib only; needs git (reads pinned files with `git show`).

Jev rows, samples, metric functions and pass rules are the ones the original receipts used,
read from the commits those receipts scored:
  SciFact   work/noul-scifact/score.py @ 15b0371, sample.jsonl + rows-jev.jsonl + rows-haiku.jsonl @ 83a7295
  Banking77 work/choice-banking77/score.py @ 3709ee6, subset.jsonl + rows-jev.jsonl + rows-haiku.jsonl @ 3709ee6
The second incumbent's rows are this directory's rows-{scifact,banking77}-grok.jsonl.

  python3 work/second-incumbent/score.py
"""

import json
import os
import subprocess
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SCIFACT = "83a7295"
SCIFACT_SCORER = "15b0371"
B77 = "3709ee6"


def git_show(sha, relpath):
    return subprocess.check_output(
        ["git", "-C", ROOT, "show", f"{sha}:{relpath}"], text=True
    )


def pinned_module(name, sha, relpath):
    module = types.ModuleType(name)
    module.__file__ = os.path.join(ROOT, relpath)
    exec(compile(git_show(sha, relpath), module.__file__, "exec"), module.__dict__)  # noqa: S102
    return module


def rows_at(sha, relpath):
    return [
        json.loads(line) for line in git_show(sha, relpath).splitlines() if line.strip()
    ]


def local_rows(name):
    path = os.path.join(HERE, name)
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def usage_line(label, rows):
    got = [r for r in rows if "error" not in r]
    tin = sum(r["usage"]["input_tokens"] or 0 for r in got)
    tout = sum(r["usage"]["output_tokens"] or 0 for r in got)
    lat = sorted(r["latencyMs"] for r in got)
    p50 = lat[len(lat) // 2] if lat else None
    p95 = lat[max(0, int(0.95 * len(lat)) - 1)] if lat else None
    models = sorted({r.get("modelReported") for r in got})
    finish = sorted({str(r.get("finishReason")) for r in got})
    retries = sum(r.get("nRetries", 0) for r in got)
    multi = sum(1 for r in got if r.get("nAttempts", 1) > 1)
    errors = sum(1 for r in rows if "error" in r)
    print(
        f"{label}: answered {len(got)}, error rows {errors}, model reported {models}, finish {finish}, "
        f"transient retries {retries}, rows with >1 attempt {multi}, p50/p95 {p50}/{p95} ms, "
        f"tokens {tin:,} in / {tout:,} out"
    )


def scifact():
    s = pinned_module("scifact_score", SCIFACT_SCORER, "work/noul-scifact/score.py")
    sample = rows_at(SCIFACT, "work/noul-scifact/sample.jsonl")
    y = [1 if r["truth"] else 0 for r in sample]
    n = len(y)
    grok_rows = local_rows("rows-scifact-grok.jsonl")
    if not grok_rows:
        print("scifact: no grok rows")
        return
    arms = {}
    for arm, rows in (
        ("jev", rows_at(SCIFACT, "work/noul-scifact/rows-jev.jsonl")),
        ("haiku", rows_at(SCIFACT, "work/noul-scifact/rows-haiku.jsonl")),
        ("grok", grok_rows),
    ):
        preds = s.arm_probs(sample, rows)
        p = [r["noul"] if r is not None else 0.5 for r in preds]
        ok = [s.correct(pp, r, bool(t)) for pp, r, t in zip(p, preds, y)]
        arms[arm] = {"p": p, "ok": ok, "answered": sum(r is not None for r in preds)}
    print(f"\n## SciFact ({n} pairs, prevalence {sum(y) / n:.3f})")
    usage_line("grok", grok_rows)
    print(
        "\n| Arm | Answered | Correct at >0.5 | Accuracy | Wilson 95% | AUC | Brier | ECE |"
    )
    print("|---|---:|---:|---:|---|---:|---:|---:|")
    for arm, a in arms.items():
        k = sum(a["ok"])
        lo, hi = s.wilson(k, n)
        print(
            f"| {arm} | {a['answered']}/{n} | {k}/{n} | {k / n:.1%} | {lo:.1%}-{hi:.1%} | "
            f"{s.auc(a['p'], y):.3f} | {s.brier(a['p'], y):.4f} | {s.ece(a['p'], y):.4f} |"
        )
    print(
        "\n| Jev vs | Jev-only | Other-only | McNemar p | Acc | AUC diff 95% | AUC | Brier diff 95% | Brier | ECE diff 95% | ECE |"
    )
    print("|---|---:|---:|---:|---|---|---|---|---|---|---|")
    verdicts = {}
    for other in ("haiku", "grok"):
        j, o = arms["jev"], arms[other]
        jo = sum(1 for a, b in zip(j["ok"], o["ok"]) if a and not b)
        xo = sum(1 for a, b in zip(j["ok"], o["ok"]) if b and not a)
        pm = s.binom_two_sided(jo, jo + xo)
        vs = {
            "acc": "WIN"
            if pm < s.ALPHA and jo > xo
            else "LOSE"
            if pm < s.ALPHA and xo > jo
            else "TIE"
        }
        cells = []
        for key, m, higher in (
            ("auc", s.auc, True),
            ("brier", s.brier, False),
            ("ece", s.ece, False),
        ):
            lo, hi = s.boot(m, j["p"], o["p"], y)
            better = (lo > 0) if higher else (hi < 0)
            worse = (hi < 0) if higher else (lo > 0)
            vs[key] = "WIN" if better else "LOSE" if worse else "TIE"
            cells += [f"{lo:+.4f} to {hi:+.4f}", vs[key]]
        verdicts[other] = vs
        print(
            f"| {other} | {jo} | {xo} | {pm:.2e} | {vs['acc']} | "
            + " | ".join(cells)
            + " |"
        )
    g = verdicts["grok"]
    lost = "LOSE" in g.values()
    print(
        f"\nSciFact bar 2 vs grok: accuracy {g['acc']}, AUC {g['auc']}, Brier {g['brier']}, ECE {g['ece']}; "
        f"loses to incumbent: {'YES' if lost else 'NO'} -> {'FAIL' if lost else 'PASS'}"
    )
    distinct = len({round(x, 4) for x in arms["grok"]["p"]})
    print(
        f"grok distinct noul values: {distinct}; zero-mass rows: n/a (a Noul answer is one probability)"
    )


def banking77():
    b = pinned_module("b77_score", B77, "work/choice-banking77/score.py")
    subset = rows_at(B77, "work/choice-banking77/subset.jsonl")
    grok_rows = local_rows("rows-banking77-grok.jsonl")
    if not grok_rows:
        print("banking77: no grok rows")
        return
    n = len(subset)
    counts = {}
    for r in subset:
        counts[r["intent"]] = counts.get(r["intent"], 0) + 1
    const_k = max(counts.values())
    jev = b.arm_stats(
        "jev", subset, rows_at(B77, "work/choice-banking77/rows-jev.jsonl")
    )
    haiku = b.arm_stats(
        "haiku", subset, rows_at(B77, "work/choice-banking77/rows-haiku.jsonl")
    )
    grok = b.arm_stats("grok", subset, grok_rows)
    print(f"\n## Banking77 10-intent ({n} rows, constant {const_k}/{n})")
    usage_line("grok", grok_rows)
    print("\n| Arm | Answered | Failed | Correct | Accuracy | Wilson 95% |")
    print("|---|---:|---:|---:|---:|---|")
    for a in (jev, haiku, grok):
        lo, hi = a["wilson"]
        print(
            f"| {a['name']} | {a['answered']} | {a['failed']} | {a['correct']}/{n} | {100 * a['acc']:.1f}% | {100 * lo:.1f}-{100 * hi:.1f}% |"
        )

    final = b.final_rows(grok_rows)
    zero = {i for i, r in final.items() if "choice" in r and r.get("rawSum", 1.0) == 0}
    flagged = {
        i
        for i, r in final.items()
        if "choice" in r and r.get("probabilityError", 0.0) > 1e-6
    }
    print(
        f"\ngrok zero-mass rows (raw map summed to 0): {len(zero)}/{n}; rows with any probability_errors > 1e-6: "
        f"{len(flagged)}/{n}; zero-mass rows grok scored correct: {sum(grok['per_i'][i] for i in zero)}; "
        f"Jev correct on them: {sum(jev['per_i'][i] for i in zero)}"
    )

    def verdict(label, keep, grok_ok):
        jk = sum(jev["per_i"][i] for i in keep)
        gk = sum(grok_ok[i] for i in keep)
        m = len(keep)
        jo = sum(1 for i in keep if jev["per_i"][i] and not grok_ok[i])
        go = sum(1 for i in keep if grok_ok[i] and not jev["per_i"][i])
        p = b.mcnemar_exact(jo, go)
        diff = 100 * (jk - gk) / m
        if jk / m < b.FEASIBLE or gk / m < b.FEASIBLE:
            v = "NOT-SCORED (an arm is below the 50% feasibility floor)"
        elif jk <= const_k * m / n:
            v = "LOSE (Jev does not beat the constant)"
        elif diff < -b.MARGIN_PP:
            v = f"LOSE (Jev {diff:+.1f} pp vs grok, beyond -{b.MARGIN_PP} pp)"
        elif jo > go and p < b.ALPHA:
            v = f"WIN (Jev {diff:+.1f} pp vs grok, McNemar p = {p:.3g})"
        else:
            v = f"NON-INFERIOR (Jev {diff:+.1f} pp vs grok, within -{b.MARGIN_PP} pp)"
        print(f"| {label} | {m} | {jk} | {gk} | {jo} | {go} | {p:.3g} | {v} |")
        return v

    print(
        "\n| Scoring | Rows | Jev correct | grok correct | Jev-only | grok-only | McNemar p | Verdict (k3k rule) |"
    )
    print("|---|---:|---:|---:|---:|---:|---:|---|")
    all_ids = list(jev["per_i"])
    primary = verdict("as returned (preregistered primary)", all_ids, grok["per_i"])
    verdict(
        "zero-mass rows dropped from both arms",
        [i for i in all_ids if i not in zero],
        grok["per_i"],
    )
    verdict(
        "zero-mass rows scored wrong for grok",
        all_ids,
        {i: (False if i in zero else v) for i, v in grok["per_i"].items()},
    )
    print(f"\nBanking77 primary verdict: {primary}")
    hb = sum(1 for i in all_ids if haiku["per_i"][i] and not grok["per_i"][i])
    gb = sum(1 for i in all_ids if grok["per_i"][i] and not haiku["per_i"][i])
    print(
        f"descriptive, Haiku vs grok: haiku-only {hb}, grok-only {gb}, McNemar p = {b.mcnemar_exact(hb, gb):.3g}"
    )
    top = ", ".join(f"{t}->{g} x{k}" for (t, g), k in grok["confusions"].most_common(5))
    print(f"top confusions grok: {top or 'none'}")


def main():
    scifact()
    banking77()
    return 0


if __name__ == "__main__":
    sys.exit(main())
