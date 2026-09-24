#!/usr/bin/env python3
"""Audit that each bar's first commit precedes its rows file's first commit.

  python3 work/sr-adopt/audit_bars.py [pairs.tsv]

Uses git log --diff-filter=A. A reversed pair exits 1.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT = Path(__file__).resolve().parent / "prereg-pairs.tsv"


def first_add(repo, path):
    result = subprocess.run(
        ["git", "-C", repo, "log", "--diff-filter=A", "--format=%H", "--", path],
        capture_output=True,
        text=True,
    )
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    return lines[-1] if lines else ""


def audit(tsv, repo):
    bad = []
    for line in open(tsv, encoding="utf-8"):
        if not line.strip() or line.startswith("bead"):
            continue
        bead, bar, sha, rows = line.rstrip("\n").split("\t")
        bar_sha = first_add(repo, bar)
        rows_sha = first_add(repo, rows)
        if not bar_sha.startswith(sha):
            bad.append(f"{bead}: bar first commit {bar_sha[:12]} is not {sha}")
            continue
        if not rows_sha:
            bad.append(f"{bead}: rows file was never added")
            continue
        order = subprocess.run(
            ["git", "-C", repo, "merge-base", "--is-ancestor", bar_sha, rows_sha],
            capture_output=True,
        )
        if order.returncode != 0 or bar_sha == rows_sha:
            bad.append(
                f"{bead}: bar {bar_sha[:12]} does not precede rows {rows_sha[:12]}"
            )
    return bad


def main(argv):
    tsv = argv[1] if len(argv) > 1 else str(DEFAULT)
    repo = argv[2] if len(argv) > 2 else str(ROOT)
    bad = audit(tsv, repo)
    if bad:
        print("FAIL")
        for item in bad:
            print(item)
        return 1
    print(
        f"ok {sum(1 for line in open(tsv) if line.strip() and not line.startswith('bead'))}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
