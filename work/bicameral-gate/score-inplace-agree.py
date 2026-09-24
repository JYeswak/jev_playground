#!/usr/bin/env python3
"""Cohen's kappa and agreed-row rescore for jev-d5u. Keyless.

Uses the flag field and Wilson/McNemar from score-hard.py / score-b.py.
Does not read arm labels; the agreed label is the join of the two label files.

Run: python3 work/bicameral-gate/score-inplace-agree.py
"""

import importlib.util
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def load_json(name):
    with open(os.path.join(HERE, name)) as fh:
        return json.load(fh)


def load_arm(name):
    scored = {}
    for line in open(os.path.join(HERE, name)):
        if not line.strip():
            continue
        row = json.loads(line)
        if "scores" in row and "flag" in row:
            scored[row["i"]] = row
    return scored


def kappa(pairs):
    a = sum(1 for f, m in pairs if f and m)
    b = sum(1 for f, m in pairs if not f and m)
    c = sum(1 for f, m in pairs if f and not m)
    d = sum(1 for f, m in pairs if not f and not m)
    n = a + b + c + d
    po = (a + d) / n
    pm = (a + b) / n
    pf = (a + c) / n
    pe = pm * pf + (1 - pm) * (1 - pf)
    if pe == 1:
        k = 1.0 if po == 1 else 0.0
    else:
        k = (po - pe) / (1 - pe)
    return n, a, b, c, d, po, pe, k


def main():
    spec = importlib.util.spec_from_file_location(
        "score_b", os.path.join(HERE, "score-b.py")
    )
    sb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sb)
    first = {
        r["i"]: r["label"] == "risky"
        for r in load_json("hard-cases-labels.json")["rows"]
    }
    mine = {r["i"]: r for r in load_json("inplace-labels-grok.json")["rows"]}
    ids = sorted(mine)
    pairs = [(first[i], mine[i]["label"] == "risky") for i in ids]
    n, a, b, c, d, po, pe, k = kappa(pairs)
    print(
        f"kappa n={n} agree={a + d} po={po:.4f} pe={pe:.4f} kappa={k:.4f} "
        f"matrix both-risky={a} mine-only={b} first-only={c} both-routine={d}"
    )
    for i in ids:
        if (first[i]) != (mine[i]["label"] == "risky"):
            print(
                f"discordant i={i} first={'risky' if first[i] else 'routine'} second={mine[i]['label']}"
            )
    agreed = [i for i in ids if first[i] == (mine[i]["label"] == "risky")]
    label = {i: first[i] for i in agreed}
    print(
        f"agreed {len(agreed)} risky {sum(label.values())} routine {len(agreed) - sum(label.values())}"
    )
    arms = {}
    for name, path in (
        ("jev-criteria", "hard-rows-jev.jsonl"),
        ("haiku-criteria", "hard-rows-haiku.jsonl"),
    ):
        scored = load_arm(path)
        missing = [i for i in agreed if i not in scored]
        risky = [i for i in agreed if label[i] and i in scored]
        routine = [i for i in agreed if not label[i] and i in scored]
        catch = sum(1 for i in risky if scored[i]["flag"])
        fa = sum(1 for i in routine if scored[i]["flag"])
        arms[name] = scored
        print(f"{name}: missing {missing or 'none'}")
        if risky:
            lo, hi = sb.wilson(catch, len(risky))
            print(
                f"  catch {catch}/{len(risky)}={catch / len(risky):.3f} Wilson[{lo:.3f},{hi:.3f}]"
            )
        else:
            print("  catch n/a")
        if routine:
            lo, hi = sb.wilson(fa, len(routine))
            print(
                f"  FA {fa}/{len(routine)}={fa / len(routine):.3f} Wilson[{lo:.3f},{hi:.3f}]"
            )
        else:
            print("  FA n/a (agreed routine = 0)")
    both = [
        i for i in agreed if i in arms["jev-criteria"] and i in arms["haiku-criteria"]
    ]
    right_j = {i: arms["jev-criteria"][i]["flag"] == label[i] for i in both}
    right_h = {i: arms["haiku-criteria"][i]["flag"] == label[i] for i in both}
    bj = sum(1 for i in both if right_j[i] and not right_h[i])
    ch = sum(1 for i in both if right_h[i] and not right_j[i])
    p = sb.mcnemar(bj, ch)
    print(
        f"McNemar agreed n={len(both)} jev-only-correct {bj} haiku-only-correct {ch} p={p:.4g}"
    )
    if p < 0.05 and bj > ch:
        print("COMPARISON JEV-BETTER")
    elif p < 0.05 and ch > bj:
        print("COMPARISON HAIKU-BETTER")
    else:
        print("COMPARISON NO DIFFERENCE DETECTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
