#!/usr/bin/env python3
"""Cheap keep-signal floors vs Jev's keep scores (bead jev-al06). Development sets only, keyless.

Definitions are preregistered in docs/demos/upstream-repro/compaction-floors-20260924.md.
features-<set>.jsonl comes from floors.ts; labels and Jev scores come from each readout's own files.

  python3 work/compaction-floors/floors.py
"""

import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, os.path.join(ROOT, "work", "compaction-need"))
sys.path.insert(0, os.path.join(ROOT, "work", "compaction-keep"))
import need as N  # noqa: E402
import keep as K  # noqa: E402

FLOORS = ["position", "tool_class", "result_chars", "later_overlap"]
REFERENCE = ["horizon_overlap"]  # reads the future: no compactor can use it
DROP_RATE = 0.40  # C1's measured not-needed drop rate on jec6
SEED = 20260924
RESAMPLES = 2000


def auc(pos, neg):
    """Mann-Whitney AUC by midranks: P(a needed score > a not-needed score), ties counted half."""
    if not pos or not neg:
        return None
    ranked = sorted([(v, 1) for v in pos] + [(v, 0) for v in neg])
    rank_sum, i = 0.0, 0
    while i < len(ranked):
        j = i
        while j < len(ranked) and ranked[j][0] == ranked[i][0]:
            j += 1
        mid = (i + 1 + j) / 2
        rank_sum += mid * sum(flag for _v, flag in ranked[i:j])
        i = j
    return (rank_sum - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))


def auc_ci(pos, neg):
    """Percentile bootstrap 95% interval, resampling each class, seeded."""
    rng = random.Random(SEED)
    vals = sorted(
        auc([rng.choice(pos) for _ in pos], [rng.choice(neg) for _ in neg])
        for _ in range(RESAMPLES)
    )
    return vals[int(0.025 * RESAMPLES)], vals[int(0.975 * RESAMPLES) - 1]


def at_drop_rate(pos, neg):
    """The cut that drops ~40% of not-needed calls (the 40th percentile of their scores); needed kept at it."""
    ordered = sorted(neg)
    cut = ordered[int(DROP_RATE * len(ordered))]
    return sum(p >= cut for p in pos), sum(n < cut for n in neg) / len(neg)


def load_set(name):
    if name == "x86y":
        keys = N.calls()
        got = N.final(keys)
        dec = {(d["session"], d["tool_use_id"]): d for d in N.read_jsonl(N.DECISIONS)}
    else:
        keys = K.calls()
        got = K.final(keys)
        dec = {(d["session"], d["tool_use_id"]): d for d in N.read_jsonl(K.DECISIONS)}
    if isinstance(got, str):
        raise SystemExit(f"REFUSED: {name} labels not final: {got}")
    final = got[2]
    feats = {
        (r["session"], r["tool_use_id"]): r
        for r in N.read_jsonl(os.path.join(HERE, f"features-{name}.jsonl"))
    }
    rows = []
    for k in keys:
        if keys[k]["pinned"] or final[k] == "undecidable":
            continue
        if k not in feats or feats[k]["pinned"] != keys[k]["pinned"]:
            raise SystemExit(f"REFUSED: {name} features do not match calls.json at {k}")
        row = dict(feats[k])
        row["needed"] = final[k] == "needed"
        row["keepResult"] = dec[k]["keepResult"]
        row["keepCall"] = dec[k]["keepCall"]
        if "need" in dec[k]:
            row["need"] = dec[k]["need"]
        rows.append(row)
    return rows


def main():
    print(
        "DEVELOPMENT-SET COMPARISON: every row below was labelled and scored before; nothing here is held out.\n"
    )
    for name in ("x86y", "jec6"):
        rows = load_set(name)
        pos = [r for r in rows if r["needed"]]
        neg = [r for r in rows if not r["needed"]]
        print(
            f"## {name}: {len(pos)} needed, {len(neg)} not-needed unpinned calls (undecidable and pinned left out)"
        )
        print(
            "| signal | kind | AUC | bootstrap 95% | needed kept at a 40% not-needed drop | actual drop |"
        )
        print("|---|---|---:|---|---:|---:|")
        jev = ["keepResult", "keepCall"] + (["need"] if "need" in rows[0] else [])
        for sig, kind in (
            [(s, "Jev") for s in jev]
            + [(s, "floor") for s in FLOORS]
            + [(s, "reference (uses the horizon)") for s in REFERENCE]
        ):
            p = [r[sig] for r in pos]
            n = [r[sig] for r in neg]
            a = auc(p, n)
            lo, hi = auc_ci(p, n)
            kept, drop = at_drop_rate(p, n)
            print(
                f"| {sig} | {kind} | {a:.3f} | {lo:.3f}-{hi:.3f} | {kept}/{len(p)} | {drop:.0%} |"
            )
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
