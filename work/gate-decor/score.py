#!/usr/bin/env python3
"""Score gate failure vectors with ensemble/decorrelation.py. Do not edit that file.

  python3 work/gate-decor/score.py

Reads docs/demos/upstream-repro/gate-error-decor-extract-20260924.tsv.
A constant failure vector is undefined, not the 0.0 that _phi returns.
The verdict alignment is one-per-sha. all-runs is reported beside it.
"""

import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ensemble.decorrelation import analyze  # noqa: E402

EXTRACT = ROOT / "docs/demos/upstream-repro/gate-error-decor-extract-20260924.tsv"


def load(path):
    groups = {"all-runs": defaultdict(dict), "one-per-sha": defaultdict(dict)}
    for line in open(path, encoding="utf-8"):
        if not line.strip() or line.startswith("alignment"):
            continue
        alignment, ts, sha, stage, rc = line.rstrip("\n").split("\t")
        key = (ts, sha) if alignment == "all-runs" else sha
        groups[alignment][key][stage] = int(rc) != 0
    return groups


def constant(vec):
    return len(set(vec)) < 2


def pair(name_a, name_b, fail_a, fail_b):
    if constant(fail_a) or constant(fail_b):
        return "undefined", None
    truth = [False] * len(fail_a)
    report = analyze(
        [1.0 if x else 0.0 for x in fail_a],
        [1.0 if x else 0.0 for x in fail_b],
        truth,
        a_name=name_a,
        b_name=name_b,
    )
    return "defined", report


def score(groups, alignment):
    by_key = groups[alignment]
    stages = sorted({s for row in by_key.values() for s in row})
    rows = []
    for i, a in enumerate(stages):
        for b in stages[i + 1 :]:
            keys = [k for k, row in by_key.items() if a in row and b in row]
            if not keys:
                rows.append((a, b, 0, "undefined", None))
                continue
            fa = [by_key[k][a] for k in keys]
            fb = [by_key[k][b] for k in keys]
            kind, report = pair(a, b, fa, fb)
            rows.append((a, b, len(keys), kind, report))
    return rows


def fmt(row):
    a, b, n, kind, report = row
    if kind == "undefined":
        return f"{a}\t{b}\tn={n}\tphi=undefined\tdisagree=undefined"
    return (
        f"{a}\t{b}\tn={n}\tphi={report.phi:.4f}\t"
        f"disagree={report.disagreement_rate:.4f}\t"
        f"gain={report.gain_over_best_input:.4f}\t{report.verdict}"
    )


def main():
    groups = load(EXTRACT)
    print("verdict_alignment=one-per-sha")
    for alignment in ("all-runs", "one-per-sha"):
        print(f"\n# {alignment}")
        for row in score(groups, alignment):
            print(fmt(row))
    return 0


if __name__ == "__main__":
    sys.exit(main())
