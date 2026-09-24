#!/usr/bin/env python3
"""Variance scorer for bead jev-kvw: do jev-qw8's two primary verdicts hold on every 3x3 pairing?

Run: python3 work/choice-clinc150/variance.py   (stdlib only, no key, no network)
Imports this unit's own score.py and uses its preds/correct/gate/handled/verdict unchanged. Step 1
re-derives the committed verdicts from rows-jev.jsonl x rows-haiku.jsonl and refuses to go on if they
differ from what jev-qw8 published (overall correct NON-INFERIOR, handled at peak >= 0.60 WIN).
Jev runs J1 rows-jev.jsonl (committed), J2 rows-jev-run2.jsonl, J3 rows-jev-run3.jsonl; Haiku runs H1
rows-haiku.jsonl (committed), H2 rows-haiku-run2.jsonl, H3 rows-haiku-run3.jsonl. Each pairing is
scored under both Haiku readings (as shipped; zero-mass = none) and keeps the worse label for Jev,
exactly as score.py does. Rules frozen in docs/demos/upstream-repro/choice-clinc150-variance-20260924.md.
"""

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("score", os.path.join(HERE, "score.py"))
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)

JEV = {"J1": "rows-jev.jsonl", "J2": "rows-jev-run2.jsonl", "J3": "rows-jev-run3.jsonl"}
HAIKU = {
    "H1": "rows-haiku.jsonl",
    "H2": "rows-haiku-run2.jsonl",
    "H3": "rows-haiku-run3.jsonl",
}
PUBLISHED = {"overall": "NON-INFERIOR", "handled": "WIN"}
MEASURES = ("overall", "handled")


def measure_vectors(subset, p):
    return {
        "overall": S.correct(subset, p),
        "handled": S.handled(subset, S.gate(subset, p, S.PRIMARY_GATE, "peak")),
    }


def feasible(subset, p):
    c = S.correct(subset, p)
    ins = [i for i, it in enumerate(subset) if it["intent"] != S.OOS]
    return sum(c[i] for i in ins) / len(ins) >= S.FEASIBLE


def pairing(subset, jp, hrows, n_oos):
    """Worse-for-Jev label per measure over the two Haiku readings, plus the raw tuples."""
    out = {}
    jv = measure_vectors(subset, jp)
    for zero in (False, True):
        hp = S.preds(subset, hrows, zero_as_none=zero)
        hv = measure_vectors(subset, hp)
        ok = feasible(subset, jp) and feasible(subset, hp)
        for m in MEASURES:
            lab, jk, hk, b, c, p, diff = S.verdict(jv[m], hv[m], n_oos)
            if not ok:
                lab = "NOT-SCORED"
            prev = out.get(m)
            if prev is None or S.RANK[lab] < S.RANK[prev[0]]:
                out[m] = (
                    lab,
                    jk,
                    hk,
                    b,
                    c,
                    p,
                    diff,
                    "zero-mass=none" if zero else "as shipped",
                )
    return out


def headroom(jk, hk, b, c, n):
    """Fewest one-arm answer changes, each placed adversarially, that end a WIN, and that make a LOSE."""
    end_win = None
    for k in range(0, n + 1):
        # each change moves one discordant count: b down (Jev-only -> both wrong) or c up
        for down in range(0, k + 1):
            bb, cc = b - down, c + (k - down)
            if bb < 0:
                continue
            if not (bb > cc and S.mcnemar(bb, cc) < S.ALPHA):
                end_win = k
                break
        if end_win is not None:
            break
    margin = S.MARGIN_PP * n / 100
    lose = 0
    while 100 * ((jk - hk) - lose) / n >= -S.MARGIN_PP:
        lose += 1
    return end_win, lose, margin


def main():
    subset = S.load("subset.jsonl")
    n = len(subset)
    n_oos = sum(1 for it in subset if it["intent"] == S.OOS)
    jrows = {
        k: S.load(v) for k, v in JEV.items() if os.path.exists(os.path.join(HERE, v))
    }
    hrows = {
        k: S.load(v) for k, v in HAIKU.items() if os.path.exists(os.path.join(HERE, v))
    }
    jp = {k: S.preds(subset, r) for k, r in jrows.items()}

    base = pairing(subset, jp["J1"], hrows["H1"], n_oos)
    print("Step 1: committed J1 x H1 through score.py's own functions")
    for m in MEASURES:
        lab, jk, hk, b, c, p, diff, rd = base[m]
        print(
            f"  {m}: {lab} (Jev {jk}, Haiku {hk}, {b} vs {c}, p={p:.3g}, worse reading {rd})"
        )
        if lab != PUBLISHED[m]:
            print(f"REFUSED: {m} re-derives as {lab}, jev-qw8 published {PUBLISHED[m]}")
            return 4
    print("  reproduces the published verdicts")

    lab, jk, hk, b, c, p, diff, _ = base["handled"]
    ew, _, _ = headroom(jk, hk, b, c, n)
    lab, jk, hk, b, c, p, diff, _ = base["overall"]
    _, lose, _ = headroom(jk, hk, b, c, n)
    print(
        f"  headroom (J1 x H1): handled WIN ends after {ew} adversarial answer changes; "
        f"overall NON-INFERIOR becomes LOSE after {lose}"
    )

    print("\nPer run (score.py's arm numbers; Haiku as shipped)")
    print(
        "| Run | Answered | Overall correct | Handled at peak >= 0.60 | In-scope right | OOS said none | Zero-mass rows | p50 / p95 ms | Tokens in / out |"
    )
    print("|---|---:|---:|---:|---:|---:|---:|---|---|")
    ins = [i for i, it in enumerate(subset) if it["intent"] != S.OOS]
    oos = [i for i in range(n) if i not in set(ins)]
    for k, rows in list(jrows.items()) + list(hrows.items()):
        p = S.preds(subset, rows)
        v = measure_vectors(subset, p)
        fin = [r for r in S.final_rows(rows).values() if "choice" in r]
        lat = [r["latencyMs"] for r in fin]
        tin = sum(r["usage"]["input_tokens"] for r in fin)
        tout = sum(r["usage"]["output_tokens"] for r in fin)
        zero = sum(1 for r in fin if r.get("rawSum") == 0)
        c = S.correct(subset, p)
        print(
            f"| {k} | {len(fin)}/{n} | {sum(v['overall'])} | {sum(v['handled'])} | "
            f"{sum(c[i] for i in ins)}/{len(ins)} | {sum(c[i] for i in oos)}/{len(oos)} | {zero} | "
            f"{S.nearest_rank(lat, 0.5)} / {S.nearest_rank(lat, 0.95)} | {tin:,} / {tout:,} |"
        )

    print("\nAll pairings (worse-for-Jev label over the two Haiku readings)")
    print(
        "| Pairing | Overall: Jev / Haiku, discordant, p | Overall label | Handled: Jev / Haiku, discordant, p | Handled label |"
    )
    print("|---|---|---|---|---|")
    labels = {m: [] for m in MEASURES}
    for jk_ in jp:
        for hk_ in hrows:
            r = pairing(subset, jp[jk_], hrows[hk_], n_oos)
            cells = []
            for m in MEASURES:
                lab, jk, hk, b, c, p, diff, rd = r[m]
                labels[m].append(lab)
                cells.append(f"{jk} / {hk}, {b} vs {c}, p={p:.3g} | {lab}")
            print(f"| {jk_} x {hk_} | " + " | ".join(cells) + " |")

    total = len(labels["overall"])
    if total != len(JEV) * len(HAIKU):
        print(
            f"\nINCOMPLETE: {total} of {len(JEV) * len(HAIKU)} pairings present; no verdict issued"
        )
        return 5
    print("\nVerdicts under the all-pairings rule")
    win = labels["handled"].count("WIN")
    handled_ok = win == total
    print(
        f"- handled at peak >= 0.60 WIN: WIN on {win}/{total} pairings -> "
        f"{'STANDS' if handled_ok else 'RETRACTED'}"
    )
    lose_any = any(lab in ("LOSE", "NOT-SCORED") for m in MEASURES for lab in labels[m])
    ni = sum(1 for lab in labels["overall"] if S.RANK[lab] >= S.RANK["NON-INFERIOR"])
    print(
        f"- overall NON-INFERIOR: NON-INFERIOR or better on {ni}/{total} pairings -> "
        f"{'STANDS' if ni == total else 'RETRACTED'}"
    )
    print(
        f"- PASS: {'STANDS' if not lose_any else 'RETRACTED'} "
        f"(a LOSE or NOT-SCORED on any pairing, either measure, retracts it)"
    )

    print(
        "\nDescriptive: answer changes between runs of the same arm (chosen label, 750 rows)"
    )
    for group in (jrows, hrows):
        keys = list(group)
        for a in range(len(keys)):
            for b_ in range(a + 1, len(keys)):
                pa = S.preds(subset, group[keys[a]])
                pb = S.preds(subset, group[keys[b_]])
                ch = sum(1 for x, y in zip(pa, pb) if x[0] != y[0])
                ga = S.gate(subset, pa, S.PRIMARY_GATE, "peak")
                gb = S.gate(subset, pb, S.PRIMARY_GATE, "peak")
                gc = sum(1 for x, y in zip(ga, gb) if x != y)
                print(
                    f"  {keys[a]} vs {keys[b_]}: {ch} answers differ, {gc} gate outcomes differ"
                )
    return 0


if __name__ == "__main__":
    sys.exit(main())
