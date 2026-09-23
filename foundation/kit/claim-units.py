#!/usr/bin/env python3
"""README claim units and their registration (plan W2.1(b) / W2.3).

The selection rule is the honesty census's, unchanged (notes/deep/honesty-census.md
"Preregistered" (b); first run from /tmp/jev-w1/census_claims.py): a README unit (a
sentence, or a table cell) is a candidate iff it matches NUM_RE (a numeral with a unit or
ratio) or WORD_RE (verified|passes|beats|wins|exits 0, case-insensitive), is at least 20
characters, and is outside a ``` fence. A candidate is covered iff some claims.tsv
readme_pattern is a case-insensitive substring of it.

Stage 15 pins this file's sha256 in foundation/kit/claim-coverage.floor: a change to the rule
changes what counts as a candidate, so the floor must be re-derived, never compared across.

Usage: claim-units.py [README] [claims.tsv]
Prints one TSV row per candidate (line, covered y/n, pattern, sentence), then a final
`# candidates=N covered=K` line on stdout.
"""

import csv
import re
import sys

NUM_RE = re.compile(
    r"\d+/\d+|\d+\.\d+|\d+\s*(%|ms\b|s\b|chars|rows|calls|jobs|bundles|"
    r"questions|docs?\b|claims?|passages?|pairs?|examples?|minutes?|hours?|"
    r"days?|samples?)"
)
WORD_RE = re.compile(r"verified|passes|beats|wins|exits 0", re.I)


def is_candidate(text):
    return NUM_RE.search(text) or WORD_RE.search(text)


def units(readme_lines):
    in_fence = False
    for i, line in enumerate(readme_lines, 1):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or not line.strip():
            continue
        for sent in re.split(r"(?<=[.!])\s+|\s*\|\s*", line):
            s = " ".join(sent.split())
            if len(s) >= 20 and is_candidate(s):
                yield i, s


def main():
    readme = sys.argv[1] if len(sys.argv) > 1 else "README.md"
    claims = sys.argv[2] if len(sys.argv) > 2 else "foundation/kit/claims.tsv"
    with open(claims) as f:
        pats = [row["readme_pattern"] for row in csv.DictReader(f, delimiter="\t")]
    with open(readme) as f:
        lines = f.read().split("\n")
    rows = []
    for i, s in units(lines):
        hit = next((p for p in pats if p.lower() in s.lower()), "-")
        rows.append((i, "y" if hit != "-" else "n", hit, s[:280]))
    print("line\tcovered\tpattern\tsentence")
    for i, cov, p, s in rows:
        print(f"{i}\t{cov}\t{p}\t{s}")
    print(f"# candidates={len(rows)} covered={sum(1 for r in rows if r[1] == 'y')}")


main()
