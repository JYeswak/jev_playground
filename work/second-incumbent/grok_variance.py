#!/usr/bin/env python3
"""Keyless all-pairings scorer for bead jev-wu6v: grok-4.20 run-to-run variance on the four sets where
grok is a published comparator. Stdlib only; needs git (pinned files are read with `git show`).

Every Jev run committed for a set is paired with every grok run (run 1 = the committed jev-n4j /
jev-dsu rows, runs 2 and 3 = rows-<set>-grok-run{2,3}.jsonl). Metrics and verdict rules are each
unit's own, from the commits its receipt scored. Bar:
docs/demos/upstream-repro/grok-variance-20260924.md (committed before any rerun call).

  python3 work/second-incumbent/grok_variance.py         exit 1 unless every (Jev run 1, grok run 1)
                                                         pairing reproduces its committed verdicts
  python3 work/second-incumbent/grok_variance.py --bar   the reproduction and the headroom only
"""

import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from score import local_rows, pinned_module, rows_at  # noqa: E402

RANK = {"LOSE": 0, "NOT-SCORED": 0, "TIE": 1, "NON-INFERIOR": 1, "WIN": 2}

JEV = {
    "sst5": [
        ("576e60e", "rows-jev.jsonl"),
        ("510e804", "rows-jev-run2.jsonl"),
        ("510e804", "rows-jev-run3.jsonl"),
    ],
    "clinc150": [
        ("2842340", "rows-jev.jsonl"),
        ("0516464", "rows-jev-run2.jsonl"),
        ("0516464", "rows-jev-run3.jsonl"),
    ],
    "scifact": [
        ("83a7295", "rows-jev.jsonl"),
        ("6ac0092", "rows-jev-rerun.jsonl"),
        ("3c006e2", "rows-jev-run2.jsonl"),
        ("3c006e2", "rows-jev-run3.jsonl"),
    ],
    "banking77": [
        ("3709ee6", "rows-jev.jsonl"),
        ("510e804", "rows-jev-run2.jsonl"),
        ("510e804", "rows-jev-run3.jsonl"),
    ],
}
UNIT_DIR = {
    "sst5": "work/score-sst5",
    "clinc150": "work/choice-clinc150",
    "scifact": "work/noul-scifact",
    "banking77": "work/choice-banking77",
}
GROK_RUN1 = {
    "sst5": "492d8d6",
    "clinc150": "492d8d6",
    "scifact": "a8cbf6e",
    "banking77": "a8cbf6e",
}

# (label, reading, committed verdict against grok run 1) -- the claims under test, from jev-n4j and jev-dsu.
CLAIMS = {
    "sst5": [
        ("MAE", "all rows", "WIN"),
        ("MAE", "zero-mass dropped", "WIN"),
        ("accuracy", "all rows", "WIN"),
        ("accuracy", "zero-mass dropped", "WIN"),
        ("PASS", "all rows", "PASS"),
        ("PASS", "zero-mass dropped", "PASS"),
    ],
    "clinc150": [
        ("handled at 0.60", "unit rule", "WIN"),
        ("handled at 0.60", "zero-mass dropped", "WIN"),
        ("overall", "unit rule", "WIN"),
        ("overall", "zero-mass dropped", "WIN"),
        ("PASS", "unit rule", "PASS"),
        ("PASS", "zero-mass dropped", "PASS"),
    ],
    "scifact": [
        ("accuracy", "all rows", "WIN"),
        ("AUC", "all rows", "WIN"),
        ("Brier", "all rows", "WIN"),
        ("ECE", "all rows", "WIN"),
        ("PASS", "all rows", "PASS"),
    ],
    "banking77": [
        ("McNemar", "as returned", "WIN"),
        ("McNemar", "zero-mass dropped", "NON-INFERIOR"),
        ("PASS", "as returned", "PASS"),
        ("PASS", "zero-mass dropped", "PASS"),
    ],
}


def grok_runs(dataset):
    runs = [
        rows_at(GROK_RUN1[dataset], f"work/second-incumbent/rows-{dataset}-grok.jsonl")
    ]
    size = {"sst5": 500, "clinc150": 750, "scifact": 400, "banking77": 400}[dataset]
    for tag in ("run2", "run3"):
        rows = local_rows(f"rows-{dataset}-grok-{tag}.jsonl")
        answered = {
            r["i"] for r in rows if "score" in r or "choice" in r or "noul" in r
        }
        # more than 1% unanswered after the resume pass: the run is incomplete, not scored
        runs.append(rows if rows and size - len(answered) <= 0.01 * size else None)
    return runs


def jev_runs(dataset):
    return [rows_at(sha, f"{UNIT_DIR[dataset]}/{name}") for sha, name in JEV[dataset]]


def binom(k, n):
    if n == 0:
        return 1.0
    m = min(k, n - k)
    return min(1.0, 2 * sum(math.comb(n, j) for j in range(m + 1)) / 2**n)


# ---------- SST-5 (jev-zui rules, score.py @ 576e60e) ----------
S = pinned_module("sst5_score", "576e60e", "work/score-sst5/score.py")
SST5_SAMPLE = rows_at("ae161b6", "work/score-sst5/sample.jsonl")


def sst5_zero(grok):
    return {
        r["i"]
        for r in grok
        if "score" in r
        and isinstance(r.get("originalProbabilities"), dict)
        and sum(r["originalProbabilities"].values()) == 0
    }


def sst5_pair(jev, grok):
    sample = SST5_SAMPLE
    ej = S.evaluate(sample, S.arm_preds(sample, jev), "round")
    eg = S.evaluate(sample, S.arm_preds(sample, grok), "round")
    counts = [sum(1 for s in sample if s["label"] == k) for k in range(S.LEVELS)]
    majority = max(range(S.LEVELS), key=lambda k: (counts[k], -k))
    zero = sst5_zero(grok)
    out = {"zero": len(zero)}
    for reading, keep in (("all rows", None), ("zero-mass dropped", zero)):
        idx = [k for k, s in enumerate(sample) if keep is None or s["i"] not in keep]
        sub = [sample[k] for k in idx]
        j = [ej[k] for k in idx]
        g = [eg[k] for k in idx]
        const = all(
            S.verdict(*S.paired(j, S.constant(sub, lv))[:3]) == "WIN"
            and S.verdict(*S.paired(j, S.constant(sub, lv))[3:]) == "WIN"
            for lv in (majority, 2)
        )
        ao, bo, pm, ab, bb, ps = S.paired(j, g)
        acc, mae = S.verdict(ao, bo, pm), S.verdict(ab, bb, ps)
        out[("accuracy", reading)] = (acc, f"{ao}/{bo} p={pm:.3g}")
        out[("MAE", reading)] = (mae, f"{ab}/{bb} p={ps:.3g}")
        passed = const and "LOSE" not in (acc, mae)
        out[("PASS", reading)] = ("PASS" if passed else "FAIL", "")
    return out


# ---------- CLINC150 (jev-qw8 rules, score.py @ 2842340) ----------
C = pinned_module("clinc_score", "2842340", "work/choice-clinc150/score.py")
CLINC_SUBSET = rows_at("e0950ce", "work/choice-clinc150/subset.jsonl")


def clinc_primaries(sub, jrows, grows, zero_as_none):
    pj, pg = C.preds(sub, jrows), C.preds(sub, grows, zero_as_none=zero_as_none)
    const = sum(1 for it in sub if it["intent"] == C.OOS)
    overall = C.verdict(C.correct(sub, pj), C.correct(sub, pg), const)
    gated = C.verdict(
        C.handled(sub, C.gate(sub, pj, 0.60, "peak")),
        C.handled(sub, C.gate(sub, pg, 0.60, "peak")),
        const,
    )
    ins = [k for k, it in enumerate(sub) if it["intent"] != C.OOS]
    feas = all(
        sum(C.correct(sub, p)[k] for k in ins) >= 0.5 * len(ins) for p in (pj, pg)
    )
    return overall, gated, feas


def clinc_pair(jev, grok):
    fin = C.final_rows(grok)
    zero = {i for i, r in fin.items() if "choice" in r and r.get("rawSum") == 0}
    out = {"zero": len(zero)}
    shipped = clinc_primaries(CLINC_SUBSET, jev, grok, False)
    as_none = clinc_primaries(CLINC_SUBSET, jev, grok, True)
    kept = [it for it in CLINC_SUBSET if it["i"] not in zero]
    dropped = clinc_primaries(kept, jev, grok, False)

    def cell(v):
        return f"{v[1]}/{v[2]} {v[3]}v{v[4]} p={v[5]:.3g}"

    for name, k in (("overall", 0), ("handled at 0.60", 1)):
        a, b = shipped[k], as_none[k]
        worse = a if RANK[a[0]] <= RANK[b[0]] else b
        out[(name, "unit rule")] = (worse[0], cell(worse))
        out[(name, "zero-mass dropped")] = (dropped[k][0], cell(dropped[k]))
    for reading, sets in (
        ("unit rule", (shipped, as_none)),
        ("zero-mass dropped", (dropped,)),
    ):
        ok = all(s[2] for s in sets) and all(
            out[(n, reading)][0] not in ("LOSE",)
            for n in ("overall", "handled at 0.60")
        )
        out[("PASS", reading)] = ("PASS" if ok else "FAIL", "")
    return out


# ---------- SciFact (jev-9er rules, score.py @ 15b0371; dsu scoring) ----------
F = pinned_module("scifact_score", "15b0371", "work/noul-scifact/score.py")
SCI_SAMPLE = rows_at("83a7295", "work/noul-scifact/sample.jsonl")
SCI_Y = [1 if r["truth"] else 0 for r in SCI_SAMPLE]


def sci_arm(rows):
    preds = F.arm_probs(SCI_SAMPLE, rows)
    p = [r["noul"] if r is not None else 0.5 for r in preds]
    ok = [F.correct(pp, r, bool(t)) for pp, r, t in zip(p, preds, SCI_Y)]
    return p, ok


def scifact_pair(jev, grok):
    pj, oj = sci_arm(jev)
    pg, og = sci_arm(grok)
    jo = sum(1 for a, b in zip(oj, og) if a and not b)
    go = sum(1 for a, b in zip(oj, og) if b and not a)
    pm = F.binom_two_sided(jo, jo + go)
    acc = (
        "WIN"
        if pm < F.ALPHA and jo > go
        else "LOSE"
        if pm < F.ALPHA and go > jo
        else "TIE"
    )
    out = {"zero": 0, ("accuracy", "all rows"): (acc, f"{jo}/{go} p={pm:.3g}")}
    for key, m, higher in (
        ("AUC", F.auc, True),
        ("Brier", F.brier, False),
        ("ECE", F.ece, False),
    ):
        lo, hi = F.boot(m, pj, pg, SCI_Y)
        better = (lo > 0) if higher else (hi < 0)
        worse = (hi < 0) if higher else (lo > 0)
        out[(key, "all rows")] = (
            "WIN" if better else "LOSE" if worse else "TIE",
            f"{lo:+.4f}..{hi:+.4f}",
        )
    lost = any(
        out[(k, "all rows")][0] == "LOSE" for k in ("accuracy", "AUC", "Brier", "ECE")
    )
    out[("PASS", "all rows")] = ("FAIL" if lost else "PASS", "")
    return out


# ---------- Banking77 10-intent (jev-k3k rules, score.py @ 3709ee6; dsu scoring) ----------
B = pinned_module("b77_score", "3709ee6", "work/choice-banking77/score.py")
B77_SUBSET = rows_at("3709ee6", "work/choice-banking77/subset.jsonl")


def b77_verdict(jper, gper, keep, const_k, n):
    jk = sum(jper[i] for i in keep)
    gk = sum(gper[i] for i in keep)
    m = len(keep)
    jo = sum(1 for i in keep if jper[i] and not gper[i])
    go = sum(1 for i in keep if gper[i] and not jper[i])
    p = B.mcnemar_exact(jo, go)
    diff = 100 * (jk - gk) / m
    if jk / m < B.FEASIBLE or gk / m < B.FEASIBLE:
        v = "NOT-SCORED"
    elif jk <= const_k * m / n or diff < -B.MARGIN_PP:
        v = "LOSE"
    elif jo > go and p < B.ALPHA:
        v = "WIN"
    else:
        v = "NON-INFERIOR"
    return v, f"{jk}/{gk} {jo}v{go} p={p:.3g}"


def banking77_pair(jev, grok):
    n = len(B77_SUBSET)
    counts = {}
    for r in B77_SUBSET:
        counts[r["intent"]] = counts.get(r["intent"], 0) + 1
    const_k = max(counts.values())
    js = B.arm_stats("jev", B77_SUBSET, jev)
    gs = B.arm_stats("grok", B77_SUBSET, grok)
    final = B.final_rows(grok)
    zero = {i for i, r in final.items() if "choice" in r and r.get("rawSum", 1.0) == 0}
    ids = list(js["per_i"])
    out = {"zero": len(zero)}
    for reading, keep in (
        ("as returned", ids),
        ("zero-mass dropped", [i for i in ids if i not in zero]),
    ):
        v = b77_verdict(js["per_i"], gs["per_i"], keep, const_k, n)
        out[("McNemar", reading)] = v
        out[("PASS", reading)] = (
            "PASS" if v[0] in ("WIN", "NON-INFERIOR") else "FAIL",
            "",
        )
    return out


PAIR = {
    "sst5": sst5_pair,
    "clinc150": clinc_pair,
    "scifact": scifact_pair,
    "banking77": banking77_pair,
}


def meets(got, committed):
    if committed == "PASS":
        return got == "PASS"
    return RANK[got] >= RANK[committed] and not (committed == "WIN" and got != "WIN")


def headroom_mcnemar(b, c, test=binom):
    """Fewest incumbent answer changes (each turns a Jev-only row concordant, b-1, or a both-wrong row
    incumbent-only, c+1) that end a WIN: p >= 0.05 or b <= c. Lower bound, placed adversarially."""
    for k in range(0, b + c + 1):
        for x in range(0, k + 1):
            bb, cc = b - x, c + (k - x)
            if bb < 0:
                continue
            if bb <= cc or test(bb, bb + cc) >= 0.05:
                return k
    return None


def headroom_sign(b, c):
    """Per-row error sign test: one incumbent level change can turn a Jev-lower row into an
    incumbent-lower row (b-1, c+1)."""
    for k in range(0, b + 1):
        bb, cc = b - k, c + k
        if bb <= cc or binom(bb, bb + cc) >= 0.05:
            return k
    return None


def main():
    bar_only = "--bar" in sys.argv
    expect = {
        "sst5": {("accuracy", "all rows"): "142/96", ("MAE", "all rows"): "168/101"},
        "clinc150": {
            ("overall", "unit rule"): "688/668 35v15",
            ("handled at 0.60", "unit rule"): "685/657 44v16",
        },
        "scifact": {("accuracy", "all rows"): "46/15"},
        "banking77": {
            ("McNemar", "as returned"): "384/366 24v6",
            ("McNemar", "zero-mass dropped"): "368/365 8v5",
        },
    }
    ok_all = True
    results = {}
    for ds in ("sst5", "clinc150", "scifact", "banking77"):
        jr, gr = jev_runs(ds), grok_runs(ds)
        base = PAIR[ds](jr[0], gr[0])
        repro = all(
            base[key][1].startswith(v) for key, v in expect[ds].items()
        ) and all(meets(base[(lab, rd)][0], com) for lab, rd, com in CLAIMS[ds])
        ok_all &= repro
        print(
            f"{ds}: (Jev run 1, grok run 1) reproduces the committed verdicts: {'yes' if repro else 'NO'}"
        )
        for lab, rd, com in CLAIMS[ds]:
            print(
                f"  {lab} [{rd}]: {base[(lab, rd)][0]} {base[(lab, rd)][1]} (committed {com})"
            )
        results[ds] = (jr, gr)
    if not ok_all:
        print("SELF-CHECK FAILED")
        return 1

    print(
        "\nHeadroom from the committed grok run vs Jev run 1 (fewest grok answer changes that end the WIN)"
    )
    b = PAIR["sst5"](results["sst5"][0][0], results["sst5"][1][0])
    ab, bb = (int(x) for x in b[("MAE", "all rows")][1].split()[0].split("/"))
    ao, bo = (int(x) for x in b[("accuracy", "all rows")][1].split()[0].split("/"))
    print(
        f"  SST-5 MAE sign WIN ({ab} vs {bb}): {headroom_sign(ab, bb)}; accuracy McNemar WIN ({ao} vs {bo}): {headroom_mcnemar(ao, bo)}"
    )
    c = PAIR["clinc150"](results["clinc150"][0][0], results["clinc150"][1][0])
    for name in ("handled at 0.60", "overall"):
        jo, go = (int(x) for x in c[(name, "unit rule")][1].split()[1].split("v"))
        print(
            f"  CLINC150 {name} McNemar WIN ({jo} vs {go}): {headroom_mcnemar(jo, go)}"
        )
    s = PAIR["scifact"](results["scifact"][0][0], results["scifact"][1][0])
    jo, go = (int(x) for x in s[("accuracy", "all rows")][1].split()[0].split("/"))
    print(
        f"  SciFact accuracy McNemar WIN ({jo} vs {go}): {headroom_mcnemar(jo, go)}; AUC/Brier/ECE are bootstrap intervals, no row headroom"
    )
    k = PAIR["banking77"](results["banking77"][0][0], results["banking77"][1][0])
    jo, go = (int(x) for x in k[("McNemar", "as returned")][1].split()[1].split("v"))
    print(
        f"  Banking77 as returned McNemar WIN ({jo} vs {go}): {headroom_mcnemar(jo, go)}"
    )
    if bar_only:
        return 0

    print("\n## All pairings (Jev run j x grok run h)")
    summary = []
    for ds in ("sst5", "clinc150", "scifact", "banking77"):
        jr, gr = results[ds]
        missing = [h + 1 for h, g in enumerate(gr) if g is None]
        print(
            f"\n### {ds}: {len(jr)} Jev runs x {len(gr)} grok runs"
            + (f" (grok runs missing: {missing})" if missing else "")
        )
        pairs = {}
        for j, jrows in enumerate(jr, 1):
            for h, grows in enumerate(gr, 1):
                if grows is None:
                    continue
                pairs[(j, h)] = PAIR[ds](jrows, grows)
        zero = {
            h: pairs[(1, h)]["zero"] for h in range(1, len(gr) + 1) if (1, h) in pairs
        }
        print(f"grok zero-mass rows per run: {zero}")
        labels = [(lab, rd) for lab, rd, _ in CLAIMS[ds]]
        print(
            "| Jev | grok | " + " | ".join(f"{lab} [{rd}]" for lab, rd in labels) + " |"
        )
        print("|---:|---:|" + "---|" * len(labels))
        for (j, h), p in sorted(pairs.items()):
            print(
                f"| {j} | {h} | "
                + " | ".join(f"{p[key][0]} {p[key][1]}".strip() for key in labels)
                + " |"
            )
        total = len(jr) * len(gr)
        for lab, rd, com in CLAIMS[ds]:
            hits = sum(1 for p in pairs.values() if meets(p[(lab, rd)][0], com))
            if len(pairs) < total:
                status = f"INCOMPLETE ({len(pairs)}/{total} pairings)"
            elif com == "PASS":
                status = "STANDS" if hits == total else "RETRACTED"
            else:
                status = "STANDS" if hits == total else "RETRACTED"
            line = f"{ds} {lab} [{rd}], committed {com}: meets it in {hits}/{len(pairs)} pairings -> {status}"
            summary.append(line)
    print("\n## Verdicts under the bar")
    for line in summary:
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
