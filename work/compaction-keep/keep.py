#!/usr/bin/env python3
"""Compaction keep rule (bead jev-jec6): status, adjudication list, readiness, and the three-rule score.

Rules are preregistered in docs/demos/upstream-repro/compaction-keep-20260924.md. keep.ts selects and
screens the sessions and writes calls.json (ids only) and the labelling packets (/tmp only).

  python3 work/compaction-keep/keep.py status
  python3 work/compaction-keep/keep.py disagreements
  python3 work/compaction-keep/keep.py ready      # exit 0 only when the live replay may run
  python3 work/compaction-keep/keep.py [score]    # REFUSED until decisions.jsonl exists
"""

import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, os.path.join(ROOT, "work", "compaction-need"))
import need as N  # noqa: E402  read_jsonl, committed, kappa, rate, ALLOWED (jev-x86y's label set)

CALLS = os.path.join(HERE, "calls.json")
LABELS = [
    os.path.join(HERE, f)
    for f in ("labels-1.jsonl", "labels-2.jsonl", "labels-adjudicated.jsonl")
]
DECISIONS = os.path.join(HERE, "decisions.jsonl")
PASS = os.path.join(HERE, "decisions-pass.json")
# The three rules, each keeping a call's result verbatim when its score reaches the cut.
RULES = {
    "C0 current: library questions, keepResult >= 0.5": ("keepResult", 0.5),
    "C1 lower cut: library questions, keepResult >= 0.15": ("keepResult", 0.15),
    "C2 reworded: NEED question with criteria, need >= 0.5": ("need", 0.5),
}
BAR_RECALL_LOWER = 0.80
BAR_NOT_NEEDED_CUT = 0.50


def calls():
    with open(CALLS, encoding="utf-8") as fh:
        return {
            (s["session"], c["tool_use_id"]): c
            for s in json.load(fh)
            for c in s["calls"]
        }


def labels(path, keys):
    if not os.path.exists(path):
        return {}
    got = {}
    for row in N.read_jsonl(path):
        key = (row.get("session"), row.get("tool_use_id"))
        if key not in keys:
            return f"{os.path.basename(path)}: {key} is not a prefix call in calls.json"
        if row.get("label") not in N.ALLOWED:
            return f"{os.path.basename(path)}: {key} has label {row.get('label')!r}"
        got[key] = row["label"]
    return got


def final(keys):
    for path in LABELS[:2]:
        if not os.path.exists(path) or not N.committed(path):
            return f"{os.path.basename(path)} is not committed and clean"
    one, two = labels(LABELS[0], keys), labels(LABELS[1], keys)
    for x in (one, two):
        if isinstance(x, str):
            return x
    missing = [k for k in keys if k not in one or k not in two]
    if missing:
        return f"{len(missing)} prefix calls lack a label from both labellers"
    split = [k for k in keys if one[k] != two[k]]
    adj = {}
    if split:
        if not os.path.exists(LABELS[2]) or not N.committed(LABELS[2]):
            return f"{len(split)} disagreements and labels-adjudicated.jsonl is not committed and clean"
        adj = labels(LABELS[2], keys)
        if isinstance(adj, str):
            return adj
        if any(k not in adj for k in split):
            return f"{sum(k not in adj for k in split)} disagreements have no adjudicated label"
    return one, two, {k: (one[k] if one[k] == two[k] else adj[k]) for k in keys}, split


def status():
    keys = calls()
    per = collections.Counter(s for s, _ in keys)
    print(
        f"calls.json: {len(keys)} prefix calls in {len(per)} sessions: "
        + ", ".join(f"{s} {n}" for s, n in sorted(per.items()))
    )
    for path in LABELS[:2]:
        got = labels(path, keys)
        if isinstance(got, str):
            print(f"{os.path.basename(path)}: INVALID: {got}")
            return 1
        c = collections.Counter(got.values())
        print(
            f"{os.path.basename(path)}: {len(got)}/{len(keys)} labelled; "
            + ", ".join(f"{k} {c[k]}" for k in sorted(N.ALLOWED))
        )
    got = final(keys)
    print(
        f"final: {'not yet (' + got + ')' if isinstance(got, str) else 'ready to replay'}"
    )
    print(f"live replay: {'present' if os.path.exists(DECISIONS) else 'NOT_RUN'}")
    return 0


def disagreements():
    keys = calls()
    for path in LABELS[:2]:
        if not os.path.exists(path) or not N.committed(path):
            print(f"REFUSED: {os.path.basename(path)} is not committed and clean")
            return 1
    one, two = labels(LABELS[0], keys), labels(LABELS[1], keys)
    split = sorted(k for k in keys if k in one and k in two and one[k] != two[k])
    print(
        f"# {len(split)} disagreements (no Jev decision exists); packets are in /tmp/jec6-packets"
    )
    for s, t in split:
        print(f"{s} {t} L1={one[(s, t)]} L2={two[(s, t)]}")
    return 0


def ready():
    if not os.path.exists(CALLS) or not N.committed(CALLS):
        print("NOT READY: calls.json is not committed")
        return 1
    got = final(calls())
    if isinstance(got, str):
        print(f"NOT READY: {got}")
        return 1
    if os.path.exists(DECISIONS):
        print("NOT READY: decisions.jsonl exists; the replay has run")
        return 1
    print("READY")
    return 0


def score():
    if not os.path.exists(DECISIONS) or not os.path.exists(PASS):
        print(
            "REFUSED: no live replay yet (decisions.jsonl and decisions-pass.json are written by `keep.ts replay --live`)"
        )
        return 1
    keys = calls()
    got = final(keys)
    if isinstance(got, str):
        print(f"REFUSED: {got}")
        return 1
    one, two, fin, split = got
    dec = {(d["session"], d["tool_use_id"]): d for d in N.read_jsonl(DECISIONS)}
    if any(k not in dec for k in keys):
        print("REFUSED: some prefix calls have no decision")
        return 1
    with open(PASS, encoding="utf-8") as fh:
        print(f"replay: {json.load(fh)}")
    n, k = N.kappa(one, two, list(keys))
    print(
        f"prefix calls {len(keys)}; labellers exact {len(keys) - len(split)}/{len(keys)}, kappa {('undefined' if k is None else f'{k:.3f}')} over {n}"
    )
    free = [x for x in keys if not keys[x]["pinned"]]
    print(
        f"unpinned {len(free)} (pinned {len(keys) - len(free)}, always kept, in no rate)"
    )
    for label_name, lab in (
        ("FINAL labels", fin),
        ("labeller 1 alone", one),
        ("labeller 2 alone", two),
    ):
        needed = [x for x in free if lab[x] == "needed"]
        not_needed = [x for x in free if lab[x] == "not-needed"]
        print(f"\n## {label_name}: needed {len(needed)}, not-needed {len(not_needed)}")
        for rule, (field, cutoff) in RULES.items():
            kept = sum((dec[x][field] or 0) >= cutoff for x in needed)
            cut_nn = sum((dec[x][field] or 0) < cutoff for x in not_needed)
            lo, _ = N.R1.wilson(kept, len(needed)) if needed else (0.0, 0.0)
            met = (
                bool(needed)
                and lo >= BAR_RECALL_LOWER
                and (cut_nn / len(not_needed) if not_needed else 0)
                >= BAR_NOT_NEEDED_CUT
            )
            print(
                f"{rule}: needed kept verbatim {N.rate(kept, len(needed))}; not-needed results not kept {N.rate(cut_nn, len(not_needed))}; bar {'MET' if met else 'NOT MET'}"
            )
    return 0


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "score"
    fn = {
        "status": status,
        "disagreements": disagreements,
        "ready": ready,
        "score": score,
    }.get(mode)
    if not fn:
        print(__doc__)
        sys.exit(64)
    sys.exit(fn())
