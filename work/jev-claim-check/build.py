#!/usr/bin/env python3
"""Build the jev_claim_check dogfood cases (bead jev-sp5). No key, no network.

One true case per row of foundation/kit/claims.tsv and one planted false case per row of
planted.tsv (same label). Output: cases.jsonl, one {"id","label","truth","kind","claim",
"evidence","proof_path","evidence_span"} per line, true cases first in claims.tsv order.

THE RULES, committed with the bar before any call:

CLAIM. The first README.md line containing the row's readme_pattern. Markdown is flattened:
a "([receipt](url))" citation is dropped, [text](url) -> text, ** and backticks dropped, a
leading list marker ("- ", "5. ") dropped, runs of spaces collapsed. The line is split into
units after every ".", "!" or "?" followed by whitespace, and at "; ". The claim is the unit
containing the pattern (matched on the flattened pattern). If that unit has fewer than 6
words, the next unit is appended.

EVIDENCE. The proof_path file's text. If it is at most 6000 characters, the whole file.
Otherwise a window of 3000 characters either side of the first occurrence of the row's
expected_substr, widened to whole lines; if widening pushes it past 9000 characters, the raw
character window is kept. A row whose expected_substr is absent from its proof file is refused
(the build exits 1): stage 15 already fails such a row.

PLANTED. planted.tsv: label <TAB> kind <TAB> false_claim. Each false claim is the row's true
claim with one number changed or one verdict flipped, written by hand before any call. It is
checked against the SAME evidence as its true twin. The build refuses a planted claim equal to
its true claim, and a label that is not in claims.tsv, and a claims.tsv label with no plant.

Run: python3 work/jev-claim-check/build.py        (writes cases.jsonl, prints sha256)
     python3 work/jev-claim-check/build.py --check (exit 1 if cases.jsonl would change)
"""

import csv
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
WHOLE_FILE_MAX = 6000
HALF_WINDOW = 3000
WIDENED_MAX = 9000
MIN_WORDS = 6


def flatten(text):
    text = re.sub(r"\s*\(\[receipt\]\([^)]*\)\)", "", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = text.replace("**", "").replace("`", "")
    text = re.sub(r"^\s*(?:[-*]|\d+\.)\s+", "", text)
    return re.sub(r"\s+", " ", text).strip()


def units(line):
    parts = re.split(r"(?<=[.!?])\s+|;\s+", line)
    return [p.strip() for p in parts if p.strip()]


def claim_for(readme_lines, pattern):
    pat = flatten(pattern)
    for raw in readme_lines:
        if pattern not in raw:
            continue
        us = units(flatten(raw))
        for i, u in enumerate(us):
            if pat in u:
                if len(u.split()) < MIN_WORDS and i + 1 < len(us):
                    return f"{u} {us[i + 1]}"
                return u
        raise SystemExit(f"pattern {pattern!r} lost in flattening")
    raise SystemExit(f"pattern {pattern!r} not in README.md")


def evidence_for(path, needle):
    text = open(os.path.join(ROOT, path), encoding="utf-8").read()
    at = text.find(needle)
    if at < 0:
        raise SystemExit(f"expected_substr {needle!r} absent from {path}")
    if len(text) <= WHOLE_FILE_MAX:
        return text, [0, len(text)]
    lo, hi = max(0, at - HALF_WINDOW), min(len(text), at + len(needle) + HALF_WINDOW)
    wlo = text.rfind("\n", 0, lo) + 1
    whi = text.find("\n", hi)
    whi = len(text) if whi < 0 else whi
    if whi - wlo <= WIDENED_MAX:
        lo, hi = wlo, whi
    return text[lo:hi], [lo, hi]


def build():
    rows = list(
        csv.DictReader(
            open(os.path.join(ROOT, "foundation/kit/claims.tsv"), encoding="utf-8"),
            delimiter="\t",
            quoting=csv.QUOTE_NONE,
        )
    )
    readme = open(os.path.join(ROOT, "README.md"), encoding="utf-8").read().split("\n")
    planted = {}
    for line in open(os.path.join(HERE, "planted.tsv"), encoding="utf-8"):
        line = line.rstrip("\n")
        if not line or line.startswith("#"):
            continue
        label, kind, claim = line.split("\t")
        if label in planted:
            raise SystemExit(f"duplicate plant {label}")
        planted[label] = (kind, claim)
    labels = [r["label"] for r in rows]
    for label in planted:
        if label not in labels:
            raise SystemExit(f"plant {label} not in claims.tsv")
    trues, falses = [], []
    for r in rows:
        if r["label"] not in planted:
            raise SystemExit(f"claims.tsv row {r['label']} has no plant")
        claim = claim_for(readme, r["readme_pattern"])
        evidence, span = evidence_for(r["proof_path"], r["expected_substr"])
        kind, false_claim = planted[r["label"]]
        if false_claim == claim:
            raise SystemExit(f"plant {r['label']} equals its true claim")
        base = {
            "label": r["label"],
            "evidence": evidence,
            "proof_path": r["proof_path"],
            "evidence_span": span,
        }
        trues.append(
            {
                "id": f"{r['label']}:true",
                "truth": True,
                "kind": "readme",
                "claim": claim,
                **base,
            }
        )
        falses.append(
            {
                "id": f"{r['label']}:planted",
                "truth": False,
                "kind": kind,
                "claim": false_claim,
                **base,
            }
        )
    return trues + falses


def main():
    cases = build()
    blob = "".join(
        json.dumps(c, ensure_ascii=False, sort_keys=True) + "\n" for c in cases
    )
    out = os.path.join(HERE, "cases.jsonl")
    if "--check" in sys.argv:
        same = os.path.exists(out) and open(out, encoding="utf-8").read() == blob
        print("cases.jsonl up to date" if same else "cases.jsonl STALE")
        return 0 if same else 1
    open(out, "w", encoding="utf-8").write(blob)
    n_true = sum(c["truth"] for c in cases)
    print(
        f"{len(cases)} cases ({n_true} true, {len(cases) - n_true} planted) sha256 {hashlib.sha256(blob.encode()).hexdigest()}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
