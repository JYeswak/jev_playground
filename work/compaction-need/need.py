#!/usr/bin/env python3
"""Compaction need measurement (bead jev-x86y): status, adjudication list, readiness, and score.

Rules are preregistered in docs/demos/upstream-repro/compaction-need-20260924.md. need.ts selects the
sessions and writes calls.json (ids only) and the labelling packets (under /tmp, never committed).

  python3 work/compaction-need/need.py status
  python3 work/compaction-need/need.py disagreements   # after both label files are committed
  python3 work/compaction-need/need.py ready           # exit 0 only when the live replay may run
  python3 work/compaction-need/need.py [score]         # REFUSED until decisions.jsonl exists
"""

import collections
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, os.path.join(ROOT, "work", "gate-observe-dogfood"))
import readout as R1  # noqa: E402  wilson()

CALLS = os.path.join(HERE, "calls.json")
LABELS = [
    os.path.join(HERE, f)
    for f in ("labels-1.jsonl", "labels-2.jsonl", "labels-adjudicated.jsonl")
]
DECISIONS = os.path.join(HERE, "decisions.jsonl")
PASS = os.path.join(HERE, "decisions-pass.json")
ALLOWED = {"needed", "not-needed", "undecidable"}


def read_jsonl(path):
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def committed(path):
    rel = os.path.relpath(path, ROOT)
    logged = subprocess.run(
        ["git", "-C", ROOT, "log", "-1", "--format=%h", "--", rel],
        capture_output=True,
        text=True,
    ).stdout.strip()
    clean = (
        subprocess.run(
            ["git", "-C", ROOT, "diff", "--quiet", "HEAD", "--", rel]
        ).returncode
        == 0
    )
    return bool(logged) and clean


def calls():
    with open(CALLS, encoding="utf-8") as fh:
        return {
            (s["session"], c["tool_use_id"]): c
            for s in json.load(fh)
            for c in s["calls"]
        }


def labels(path, keys):
    """{(session, tool_use_id): label}, or an error string."""
    if not os.path.exists(path):
        return {}
    got = {}
    for row in read_jsonl(path):
        key = (row.get("session"), row.get("tool_use_id"))
        if key not in keys:
            return f"{os.path.basename(path)}: {key} is not a prefix call in calls.json"
        if row.get("label") not in ALLOWED:
            return f"{os.path.basename(path)}: {key} has label {row.get('label')!r}"
        got[key] = row["label"]
    return got


def final(keys):
    for path in LABELS[:2]:
        if not os.path.exists(path) or not committed(path):
            return f"{os.path.basename(path)} is not committed and clean"
    one, two = labels(LABELS[0], keys), labels(LABELS[1], keys)
    for x in (one, two):
        if isinstance(x, str):
            return x
    missing = [k for k in keys if k not in one or k not in two]
    if missing:
        return f"{len(missing)} prefix calls lack a label from both labellers, e.g. {missing[:3]}"
    split = [k for k in keys if one[k] != two[k]]
    adj = {}
    if split:
        if not os.path.exists(LABELS[2]) or not committed(LABELS[2]):
            return f"{len(split)} disagreements and labels-adjudicated.jsonl is not committed and clean"
        adj = labels(LABELS[2], keys)
        if isinstance(adj, str):
            return adj
        if any(k not in adj for k in split):
            return f"{sum(k not in adj for k in split)} disagreements have no adjudicated label"
    return one, two, {k: (one[k] if one[k] == two[k] else adj[k]) for k in keys}, split


def kappa(one, two, keys):
    both = [k for k in keys if one[k] != "undecidable" and two[k] != "undecidable"]
    if not both:
        return 0, None
    po = sum(one[k] == two[k] for k in both) / len(both)
    pa = sum(one[k] == "needed" for k in both) / len(both)
    pb = sum(two[k] == "needed" for k in both) / len(both)
    pe = pa * pb + (1 - pa) * (1 - pb)
    return len(both), (None if pe == 1 else (po - pe) / (1 - pe))


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
            + ", ".join(f"{k} {c[k]}" for k in sorted(ALLOWED))
        )
    got = final(keys)
    if isinstance(got, str):
        print(f"final: not yet ({got})")
    else:
        one, two, fin, split = got
        n, k = kappa(one, two, list(keys))
        c = collections.Counter(fin.values())
        print(
            f"final: exact {len(keys) - len(split)}/{len(keys)}; kappa needed vs not-needed {('undefined' if k is None else f'{k:.3f}')} over {n}; "
            + ", ".join(f"{x} {c[x]}" for x in sorted(ALLOWED))
        )
    print(f"live replay: {'present' if os.path.exists(DECISIONS) else 'NOT_RUN'}")
    return 0


def disagreements():
    keys = calls()
    for path in LABELS[:2]:
        if not os.path.exists(path) or not committed(path):
            print(f"REFUSED: {os.path.basename(path)} is not committed and clean")
            return 1
    one, two = labels(LABELS[0], keys), labels(LABELS[1], keys)
    split = sorted(k for k in keys if k in one and k in two and one[k] != two[k])
    print(
        f"# {len(split)} disagreements (no Jev decision exists); packets are in /tmp/x86y-packets"
    )
    for s, t in split:
        print(f"{s} {t} L1={one[(s, t)]} L2={two[(s, t)]}")
    return 0


def ready():
    if not os.path.exists(CALLS) or not committed(CALLS):
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


def rate(k, n):
    lo, hi = R1.wilson(k, n)
    return (
        f"{k}/{n} (Wilson 95% {max(0.0, lo):.3f}-{min(1.0, hi):.3f})"
        if n
        else f"{k}/0 (undefined)"
    )


def score():
    if not os.path.exists(DECISIONS) or not os.path.exists(PASS):
        print(
            "REFUSED: no live replay yet (decisions.jsonl and decisions-pass.json are written by `need.ts replay --live`)"
        )
        return 1
    keys = calls()
    got = final(keys)
    if isinstance(got, str):
        print(f"REFUSED: {got}")
        return 1
    one, two, fin, split = got
    dec = {(d["session"], d["tool_use_id"]): d for d in read_jsonl(DECISIONS)}
    missing = [k for k in keys if k not in dec]
    if missing:
        print(f"REFUSED: {len(missing)} prefix calls have no decision")
        return 1
    with open(PASS, encoding="utf-8") as fh:
        receipt = json.load(fh)
    n, k = kappa(one, two, list(keys))
    print(
        f"prefix calls {len(keys)}; labellers exact {len(keys) - len(split)}/{len(keys)}, kappa {('undefined' if k is None else f'{k:.3f}')} over {n}"
    )
    print(f"replay: {receipt}")
    free = [x for x in keys if not keys[x]["pinned"]]
    pinned = [x for x in keys if keys[x]["pinned"]]
    by = {lab: [x for x in free if fin[x] == lab] for lab in sorted(ALLOWED)}
    kept = lambda xs: sum(dec[x]["action"] == "keep" for x in xs)  # noqa: E731
    any_kept = lambda xs: sum(dec[x]["action"] in ("keep", "drop_result") for x in xs)  # noqa: E731
    print(
        f"\nunpinned calls {len(free)} (pinned {len(pinned)}, always kept, in no rate)"
    )
    print(
        f"needed {len(by['needed'])}, not-needed {len(by['not-needed'])}, undecidable {len(by['undecidable'])}"
    )
    print(
        f"recall on needed calls, result kept verbatim: {rate(kept(by['needed']), len(by['needed']))}"
    )
    print(
        f"recall on needed calls, call kept (result verbatim or cut to its head): {rate(any_kept(by['needed']), len(by['needed']))}"
    )
    print(
        f"drop rate on not-needed calls, whole call dropped: {rate(sum(dec[x]['action'] == 'drop_call' for x in by['not-needed']), len(by['not-needed']))}"
    )
    print(
        f"decisions on undecidable calls: {dict(collections.Counter(dec[x]['action'] for x in by['undecidable']))}"
    )
    print(
        "\n| session | unpinned | needed | needed kept | needed call kept | not-needed | not-needed dropped |"
    )
    print("|---|---:|---:|---:|---:|---:|---:|")
    for s in sorted({x[0] for x in keys}):
        f = [x for x in free if x[0] == s]
        nd = [x for x in f if fin[x] == "needed"]
        nn = [x for x in f if fin[x] == "not-needed"]
        print(
            f"| {s} | {len(f)} | {len(nd)} | {kept(nd)} | {any_kept(nd)} | {len(nn)} | {sum(dec[x]['action'] == 'drop_call' for x in nn)} |"
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
