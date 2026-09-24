#!/usr/bin/env python3
"""Extract the 24 in-place-edit hard-case commands with no labels and no arm scores.

The receipt names 24 in-place edits and does not list their indices. This script
selects them from the committed label reasons (the class marker), then copies
command text from the frozen sample. The output carries index and command only.

Run: python3 work/bicameral-gate/extract-inplace-blind.py
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LABELS = os.path.join(HERE, "hard-cases-labels.json")
SAMPLE = os.path.join(HERE, "hard-cases-sample.json")
OUT = os.path.join(HERE, "inplace-blind-commands.json")
EXPECTED = 24
FORBIDDEN = ("label", "reason", "reader1", "reader2", "flag", "score", "noul", "arm")


def is_inplace(reason):
    """The receipt's in-place-edit class, not deletes, crontab, or the container overwrite."""
    rl = reason.lower()
    if "crontab" in rl or "xss.py" in rl:
        return False
    if "cp overwrite" in rl or "cp overwrites" in rl:
        return False
    if (
        re.search(r"(^|[^a-z])rm( |`|-)", reason)
        and "in place" not in rl
        and "in-place" not in rl
    ):
        return False
    if "in place" in rl or "in-place" in rl:
        return True
    if "sed -i" in rl and "/tmp" not in rl:
        return True
    if re.search(r"clause\s*1\b", reason, re.I) and "rewrit" in rl:
        return True
    return False


def main():
    labels = json.load(open(LABELS))
    sample = json.load(open(SAMPLE))
    by_i = {row["i"]: row for row in sample["rows"]}
    chosen = [row["i"] for row in labels["rows"] if is_inplace(row["reason"])]
    if len(chosen) != EXPECTED or len(set(chosen)) != EXPECTED:
        print(
            f"selector yielded {len(chosen)} unique of {len(set(chosen))}, want {EXPECTED}",
            file=sys.stderr,
        )
        return 1
    missing = [i for i in chosen if i not in by_i]
    if missing:
        print(f"sample missing indices {missing}", file=sys.stderr)
        return 1
    rows = [{"i": i, "command": by_i[i]["command"]} for i in sorted(chosen)]
    for row in rows:
        extra = [k for k in row if k not in ("i", "command")]
        if extra or any(k in row for k in FORBIDDEN):
            print(f"refusing to write forbidden keys {extra}", file=sys.stderr)
            return 1
        if row["command"] != by_i[row["i"]]["command"]:
            print(f"command mismatch at {row['i']}", file=sys.stderr)
            return 1
    payload = {
        "source": "work/bicameral-gate/hard-cases-sample.json",
        "n": EXPECTED,
        "blind": True,
        "rows": rows,
    }
    blob = json.dumps(payload).lower()
    for key in ('"label"', '"reason"', '"reader1"', '"reader2"', '"flag"', '"score"'):
        if key in blob:
            print(f"refusing to write {key}", file=sys.stderr)
            return 1
    with open(OUT, "w") as fh:
        json.dump(payload, fh, indent=2)
        fh.write("\n")
    print(f"wrote {OUT} rows={len(rows)} keys=i,command")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
