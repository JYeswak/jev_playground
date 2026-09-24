#!/usr/bin/env python3
"""Keyless re-score for bead jev-iwhh. No key, no network.

  python3 work/grok-incumbent-3/score.py

Prints answered counts, the first-attempt handling of b77-run2 i=1294, and
the three verdicts: FEVER ECE, Yelp exact/MAE, Banking77 accuracy on all
rows and with flat maps dropped.
"""

import importlib.util
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
ALPHA = 0.05


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_jsonl(path):
    return [json.loads(line) for line in open(path, encoding="utf-8") if line.strip()]


def first_rows(path):
    """First line per id. The bar is silent, so the first attempt counts."""
    out = {}
    order = []
    for row in load_jsonl(path):
        if row["i"] not in out:
            out[row["i"]] = row
            order.append(row["i"])
    return out, order


def answered(row):
    return (
        row is not None
        and "error" not in row
        and ("noul" in row or "score" in row or "choice" in row)
    )


def binom(k, n):
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(min(k, n - k) + 1)) / (2**n)
    return min(1.0, 2 * tail)


def verdict(a_better, b_better, p):
    if p < ALPHA and a_better > b_better:
        return "WIN"
    if p < ALPHA and b_better > a_better:
        return "LOSE"
    return "TIE"


def side(lo, hi, lower_better=False):
    if lo is None or hi is None:
        return "TIE"
    if lower_better:
        return "WIN" if hi < 0 else "LOSE" if lo > 0 else "TIE"
    return "WIN" if lo > 0 else "LOSE" if hi < 0 else "TIE"


def report_1294():
    path = os.path.join(HERE, "rows-b77-run2.jsonl")
    rows = [row for row in load_jsonl(path) if row["i"] == 1294]
    print(f"b77-run2 i=1294 lines={len(rows)}")
    for i, row in enumerate(rows, start=1):
        kind = row.get("error", "ok")[:80]
        print(f"  attempt {i}: {kind}")
    print("  counted: attempt 1 (first attempt; the bar is silent)")


def score_fever():
    sf = load_module("sf", os.path.join(ROOT, "work/noul-scifact/score.py"))
    sample = load_jsonl(os.path.join(ROOT, "work/noul-fever/sample.jsonl"))
    y = [1 if row["truth"] else 0 for row in sample]
    print(f"FEVER n={len(sample)} pos={sum(y)}")
    grok = {}
    for run in ("run1", "run2", "run3"):
        by_i, _ = first_rows(os.path.join(HERE, f"rows-fever-{run}.jsonl"))
        ok = sum(1 for row in by_i.values() if answered(row))
        print(f"  grok {run} answered {ok}/{len(sample)}")
        probs = []
        for i, row in enumerate(sample):
            got = by_i.get(row["i"])
            if answered(got):
                probs.append(float(got["noul"]))
            else:
                probs.append(0.0 if y[i] == 1 else 1.0)
        grok[run] = probs
        print(f"  grok {run} ECE {sf.ece(probs, y):.4f}")
    jev_files = [
        "rows-jev.jsonl",
        "rows-jev-rerun.jsonl",
        "rows-jev-run2.jsonl",
        "rows-jev-run3.jsonl",
    ]
    counts = {"WIN": 0, "TIE": 0, "LOSE": 0}
    for name in jev_files:
        by_i, _ = first_rows(os.path.join(ROOT, "work/noul-fever", name))
        jp = []
        for row in sample:
            got = by_i.get(row["i"])
            jp.append(float(got["noul"]) if answered(got) else 0.5)
        for run, gp in grok.items():
            lo, hi = sf.boot(sf.ece, jp, gp, y)
            got = side(lo, hi, True)
            counts[got] += 1
            print(f"  {name} x {run} ECE {got} [{lo:.4f},{hi:.4f}]")
    print(f"FEVER ECE WIN {counts['WIN']} TIE {counts['TIE']} LOSE {counts['LOSE']}")
    return counts["WIN"] == 12 and counts["TIE"] == 0 and counts["LOSE"] == 0


def score_yelp():
    ys = load_module("ys", os.path.join(ROOT, "work/score-yelp/score.py"))
    sample = load_jsonl(os.path.join(ROOT, "work/score-yelp/sample.jsonl"))
    print(f"Yelp n={len(sample)}")
    grok = {}
    for run in ("run1", "run2", "run3"):
        rows = load_jsonl(os.path.join(HERE, f"rows-yelp-{run}.jsonl"))
        by_i, _ = first_rows(os.path.join(HERE, f"rows-yelp-{run}.jsonl"))
        preds = ys.arm_preds(
            sample, [by_i[s["i"]] for s in sample if s["i"] in by_i] or rows
        )
        # arm_preds wants the raw row list and keeps the last answered row.
        # These files have one line per id, so last == first.
        preds = ys.arm_preds(sample, rows)
        ok = sum(1 for pred in preds if pred is not None)
        ev = ys.evaluate(sample, preds, "round")
        exact = sum(1 for item in ev if item[0])
        mae = sum(item[1] for item in ev) / len(ev)
        grok[run] = ev
        print(
            f"  grok {run} answered {ok}/{len(sample)} exact {exact}/{len(sample)} MAE {mae:.3f}"
        )
    counts = {
        "acc": {"WIN": 0, "TIE": 0, "LOSE": 0},
        "mae": {"WIN": 0, "TIE": 0, "LOSE": 0},
    }
    for name in ("rows-jev.jsonl", "rows-jev-run2.jsonl", "rows-jev-run3.jsonl"):
        rows = load_jsonl(os.path.join(ROOT, "work/score-yelp", name))
        je = ys.evaluate(sample, ys.arm_preds(sample, rows), "round")
        for run, ge in grok.items():
            a_only, b_only, p_mc, a_mae, b_mae, p_sign = ys.paired(je, ge)
            va = ys.verdict(a_only, b_only, p_mc)
            vm = ys.verdict(a_mae, b_mae, p_sign)
            counts["acc"][va] += 1
            counts["mae"][vm] += 1
            print(
                f"  {name} x {run} acc {a_only}/{b_only} p={p_mc:.4g} {va} mae {a_mae}/{b_mae} p={p_sign:.4g} {vm}"
            )
    print(
        f"Yelp exact WIN {counts['acc']['WIN']} TIE {counts['acc']['TIE']} LOSE {counts['acc']['LOSE']}; "
        f"MAE WIN {counts['mae']['WIN']} TIE {counts['mae']['TIE']} LOSE {counts['mae']['LOSE']}"
    )
    return counts["acc"]["WIN"] == 9 and counts["mae"]["WIN"] == 9


def is_flat(row):
    vals = []
    for value in (row.get("probabilities") or {}).values():
        if not isinstance(value, (int, float)):
            return False
        vals.append(float(value))
    return bool(vals) and max(vals) - min(vals) < 1e-9


def score_b77():
    full = load_jsonl(os.path.join(ROOT, "work/choice-banking77/full.jsonl"))
    label_map = {row["intent"].replace("_", " ").lower(): row["intent"] for row in full}
    print(f"Banking77 n={len(full)}")
    report_1294()

    def arm(path, map_choice):
        by_i, _ = first_rows(path)
        correct, flat, ok = {}, set(), 0
        for item in full:
            row = by_i.get(item["i"])
            if answered(row) and "choice" in row:
                ok += 1
                choice = (
                    label_map.get(row["choice"], row["choice"])
                    if map_choice
                    else row["choice"]
                )
                correct[item["i"]] = choice == item["intent"]
                if is_flat(row):
                    flat.add(item["i"])
            else:
                correct[item["i"]] = False
        return correct, ok, flat

    jev_files = [
        "rows-full-jev.jsonl",
        "rows-full-jev-run2.jsonl",
        "rows-full-jev-run3.jsonl",
    ]
    grok_files = ["rows-b77-run1.jsonl", "rows-b77-run2.jsonl", "rows-b77-run3.jsonl"]
    jev, grok = {}, {}
    for name in jev_files:
        correct, ok, flat = arm(
            os.path.join(ROOT, "work/choice-banking77", name), False
        )
        jev[name] = (correct, ok, flat)
        print(
            f"  {name} answered {ok}/{len(full)} correct {sum(correct.values())} flat {len(flat)}"
        )
    for name in grok_files:
        correct, ok, flat = arm(os.path.join(HERE, name), True)
        grok[name] = (correct, ok, flat)
        print(
            f"  {name} answered {ok}/{len(full)} correct {sum(correct.values())} flat {len(flat)} failed {len(full) - ok}"
        )

    def pairings(drop_flat):
        counts = {"WIN": 0, "TIE": 0, "LOSE": 0}
        label = "dropped" if drop_flat else "all-rows"
        for jn, (jc, _, jf) in jev.items():
            for gn, (gc, _, gf) in grok.items():
                drop = (jf | gf) if drop_flat else set()
                b = sum(1 for i in jc if i not in drop and jc[i] and not gc[i])
                c = sum(1 for i in jc if i not in drop and gc[i] and not jc[i])
                p = binom(min(b, c), b + c)
                got = verdict(b, c, p)
                counts[got] += 1
                print(f"  {jn} x {gn} {label} drop={len(drop)} {b}/{c} p={p:.4g} {got}")
        print(
            f"Banking77 {label} WIN {counts['WIN']} TIE {counts['TIE']} LOSE {counts['LOSE']}"
        )
        return counts["WIN"] == 9 and counts["TIE"] == 0 and counts["LOSE"] == 0

    return pairings(False) and pairings(True)


def main():
    fever_ok = score_fever()
    yelp_ok = score_yelp()
    b77_ok = score_b77()
    print(f"HOLDS fever={fever_ok} yelp={yelp_ok} b77={b77_ok}")
    return 0 if fever_ok and yelp_ok and b77_ok else 1


if __name__ == "__main__":
    sys.exit(main())
