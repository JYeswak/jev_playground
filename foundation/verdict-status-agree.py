#!/usr/bin/env python3
"""Does the hand-written VERDICT.md still agree with STATUS.tsv, the state of record?

Authorized by pane 2's ruling (docs/demos/duel-2/runs/ruling-verdict-status-coupling-20260918T171000Z.json,
e448f00): "STATUS.tsv remains sole state of record; VERDICT.md stays hand-written for outsider
persuasion, but requires a deterministic agreement gate."

WHY BOTH FILES EXIST. STATUS.tsv is a 10-column TSV keyed on candidate ids — correct, and unreadable
to anyone outside the lane. VERDICT.md is prose written to persuade a stranger, and a fresh-clone
outsider grade returned PERSUADES on it. Neither replaces the other, so the duplication is deliberate
and the risk is drift.

THE OBSERVED DEFECTS ARE BOTH REAL AND BOTH SHIPPED PUBLICLY TODAY, which is what earned this gate:
  - "283,786 KLOC" for 283.786 KLOC: a unit wrong by 1000x, sitting next to the density figure that
    refuted it, in two documents at once.
  - demo-1's kill citing 0.047% when the receipt basis gives 0.0447% — a retracted basis surviving in
    a kill notice because the number was never load-bearing for the kill.

WHAT IS CHECKED, all of it derived from STATUS.tsv, never written down here:
  1. every candidate in STATUS appears in VERDICT exactly once
  2. each appears under the section matching its verdict (RULED_OUT / CLEARED / HELD)
  3. the per-category counts VERDICT states in prose equal the counts in STATUS
  4. VERDICT states zero promotions, and STATUS agrees there are none

NOT CHECKED, deliberately: whether the prose is PERSUASIVE, or whether a candidate's narrative is
accurate. A gate cannot grade writing; that is what a non-author outsider read is for.

Usage: verdict-status-agree.py <STATUS.tsv> <VERDICT.md>
Exit 0 agreement, 1 drift (every disagreement printed), 2 usage/missing input.
"""

import re
import sys

# A verdict's section is identified by a phrase in its heading, not by heading order, so reordering
# the document does not silently break the mapping.
SECTION_FOR = {
    "RULED_OUT": re.compile(r"^##\s+.*\bkills?\b", re.I),
    "CLEARED": re.compile(r"^##\s+.*\bCLEARED\b"),
    "HELD": re.compile(r"^##\s+.*\bHELD\b"),
}
# Candidates are cited in prose by their SHORT id ("**demo-1", "**COD-H5"), while STATUS carries the
# full slug. Deriving the short form from the slug keeps STATUS authoritative for the set.
SHORT = re.compile(r"^((?:demo-\d+)|(?:[A-Z]+-H\d+))")
NUM_WORDS = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}


def load_status(path):
    rows = []
    with open(path, encoding="utf-8") as fh:
        for i, line in enumerate(fh):
            cols = line.rstrip("\n").split("\t")
            if i == 0 or len(cols) < 4 or not cols[0] or cols[0].startswith("#"):
                continue
            if cols[3] not in SECTION_FOR:
                continue
            m = SHORT.match(cols[0])
            if m:
                rows.append((cols[0], m.group(1), cols[3]))
    return rows


def sections_of(lines):
    """Map each line index to the verdict whose section contains it, or None."""
    owner = [None] * len(lines)
    current = None
    for i, line in enumerate(lines):
        if line.startswith("## "):
            current = next(
                (v for v, rx in SECTION_FOR.items() if rx.search(line)), None
            )
        owner[i] = current
    return owner


def stated_count(lines, verdict):
    """The count VERDICT states in prose for a category heading, as digits or an English word."""
    for line in lines:
        if line.startswith("## ") and SECTION_FOR[verdict].search(line):
            # EARLIEST number wins, digit or word. Taking the first dict hit instead read "one"
            # out of "each blocked on exactly one named thing" and reported the HELD count as 1
            # against STATUS's 8 — a gate failing on its own parser, which is worse than no gate
            # because it teaches a reader to ignore a red.
            cands = [
                (m.start(), int(m.group(1))) for m in re.finditer(r"\b(\d+)\b", line)
            ]
            for word, n in NUM_WORDS.items():
                for m in re.finditer(rf"\b{word}\b", line, re.I):
                    cands.append((m.start(), n))
            if cands:
                return min(cands)[1]
    return None


def main(argv):
    if len(argv) != 3:
        print(__doc__.strip().splitlines()[-2], file=sys.stderr)
        return 2
    status_path, verdict_path = argv[1], argv[2]
    try:
        rows = load_status(status_path)
        lines = open(verdict_path, encoding="utf-8").read().splitlines()
    except OSError as exc:
        print(f"FAIL  input unreadable: {exc}")
        return 2
    if not rows:
        print(
            "FAIL  STATUS.tsv yielded NO candidates — an empty scan set is not agreement"
        )
        return 1

    owner = sections_of(lines)
    problems = []

    for slug, short, verdict in rows:
        hits = [i for i, line in enumerate(lines) if f"**{short}" in line]
        if not hits:
            problems.append(f"{slug}: absent from VERDICT.md (STATUS says {verdict})")
            continue
        if len(hits) > 1:
            problems.append(
                f"{slug}: cited {len(hits)} times in VERDICT.md; expected exactly one"
            )
            continue
        got = owner[hits[0]]
        if got != verdict:
            problems.append(
                f"{slug}: STATUS says {verdict} but VERDICT.md places it under "
                f"{got or 'no category section'} (line {hits[0] + 1})"
            )

    for verdict in SECTION_FOR:
        actual = sum(1 for _, _, v in rows if v == verdict)
        stated = stated_count(lines, verdict)
        if stated is None:
            problems.append(
                f"{verdict}: VERDICT.md heading states no count; STATUS has {actual}"
            )
        elif stated != actual:
            problems.append(
                f"{verdict}: VERDICT.md heading says {stated}, STATUS has {actual}"
            )

    promoted = sum(1 for _, _, v in rows if v == "PROMOTED")
    claims_zero = re.search(
        r"\b0 promotions?\b|\bzero promotions?\b", "\n".join(lines), re.I
    )
    if promoted == 0 and not claims_zero:
        problems.append(
            "VERDICT.md never states zero promotions, and STATUS has none — say it"
        )
    if promoted and claims_zero:
        problems.append(f"VERDICT.md claims zero promotions but STATUS has {promoted}")

    if problems:
        print("FAIL  VERDICT.md and STATUS.tsv disagree:")
        for p in problems:
            print(f"        {p}")
        return 1
    print(
        f"PASS  {len(rows)} candidates agree; per-category counts and the zero-promotions "
        "claim match STATUS"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
