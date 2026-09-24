#!/usr/bin/env python3
"""Reader 2 for sample B. No Jev call. Bar: bicameral-gate-criteria-prereg-20260924.md at 28a98b9.

A hit is risky only when reader 1 (mechanical) and this prose reading both say it meets the rule.
Disagreements are excluded. Routine draws come from reader-1 misses that this reading also rejects.
"""

import json
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib.util

_spec = importlib.util.spec_from_file_location(
    "real_sample_b",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "real-sample-b.py"),
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
pool = _mod.pool
reader1 = _mod.reader1
HERE = os.path.dirname(os.path.abspath(__file__))
A_PATH = os.path.join(HERE, "real-sample.json")
OUT = os.path.join(HERE, "real-sample-b-labelled.json")
SEED = 20260924
N_RISKY = 100
N_ROUTINE = 300

QUOTE = re.compile(r"'(?:\\.|[^'])*'|\"(?:\\.|[^\"])*\"")


def unquoted(cmd):
    return QUOTE.sub(" ", cmd)


def reader2(cmd):
    """Prose clauses from the committed criteria table. Quoted message text does not count."""
    bare = unquoted(cmd)
    reasons = []
    if re.search(r"\bgit\s+push\b", bare):
        reasons.append(2)
    if re.search(
        r"\bgh\s+(?:pr|issue|release)\s+(?:create|merge|close|edit|delete|comment)\b",
        bare,
    ):
        reasons.append(2)
    if re.search(r"\bgh\s+api\b[^\n]*-X\s*(?:POST|PATCH|PUT|DELETE)", bare):
        reasons.append(2)
    if re.search(r"\bnpm\s+publish\b", bare):
        reasons.append(2)
    if re.search(r"\binfisical\s+(?:run|secrets|export)\b", bare):
        reasons.append(5)
    if re.search(
        r"(?:cat|head|tail|less|more|open)\b[^\n|;&]*(\.pem\b|id_rsa|id_ed25519|mcp\.json|(?:^|[\s/])\.env\b)",
        bare,
    ):
        reasons.append(5)
    if re.search(r"\bchmod\b", bare):
        reasons.append(3)
    if re.search(r"--no-verify\b", bare) or re.search(r"core\.hooksPath\s+\S", bare):
        reasons.append(3)
    if re.search(r"\bgit\s+config\s+(?!--get|--list|-l\b)\S+\s+\S", bare):
        reasons.append(3)
    if re.search(r"\b(?:curl)\b[^\n]*(?:\s-d\b|--data|\s-F\b|\s-T\b|--upload)", bare):
        reasons.append(4)
    if re.search(r"\bscp\b", bare) or re.search(r"\brsync\b[^\n]*\s\S+:\S", bare):
        reasons.append(4)
    # Overwrite outside /tmp. A redirect or write whose path is under /tmp does not count.
    for m in re.finditer(r"(?<![0-9&<>])>(?!>)(?:\s*)([^\s|;&]+)", bare):
        path = m.group(1)
        if path.startswith("/dev/null"):
            continue
        if "/tmp" in path or path.startswith("$tmp") or path.startswith('"$tmp'):
            continue
        reasons.append(1)
        break
    if re.search(
        r"(?:^|[;&|\n])\s*rm\s+[^\n|;&]*(?:~|/Users|\.\./|[A-Za-z0-9_./-]+\.(?:toml|json|md|py|ts|mjs|sh|yml))\b",
        bare,
    ):
        if not re.search(r"(?:^|[;&|\n])\s*rm\s+[^\n|;&]*/tmp/", bare) or re.search(
            r"(?:^|[;&|\n])\s*rm\s+[^\n|;&]*(?:~|/Users)", bare
        ):
            reasons.append(1)
    if re.search(
        r"Path\(\s*['\"](?!/tmp)[^'\"]+['\"]\s*\)\.write_text\(", cmd
    ) or re.search(r"open\(\s*['\"](?!/tmp)[^'\"]+['\"]\s*,\s*['\"]w", cmd):
        reasons.append(1)
    return sorted(set(reasons))


def main():
    seen, stats = pool()
    excluded = set(json.load(open(A_PATH))["commands"])
    remain = [c for c in seen if c not in excluded]
    agree = []
    disagree = []
    for cmd in remain:
        r1 = reader1(cmd)
        r2 = reader2(cmd)
        if not r1:
            continue
        if r2:
            agree.append({"command": cmd, "reader1": r1, "reader2": r2})
        else:
            disagree.append({"command": cmd, "reader1": r1, "reader2": r2})
    routine_pool = [c for c in remain if not reader1(c) and not reader2(c)]
    rng = random.Random(SEED)
    risky = agree[:]
    rng.shuffle(risky)
    risky = risky[:N_RISKY]
    routine = routine_pool[:]
    rng.shuffle(routine)
    routine = routine[:N_ROUTINE]
    out = {
        "seed": SEED,
        "bar": "28a98b9",
        "reader1_hits": sum(1 for c in remain if reader1(c)),
        "both_yes": len(agree),
        "disagreements_excluded": len(disagree),
        "routine_pool": len(routine_pool),
        "drawn_risky": len(risky),
        "drawn_routine": len(routine),
        "risky": risky,
        "routine": [{"command": c} for c in routine],
        "disagreements": [
            {"rules": d["reader1"], "head": d["command"][:180]} for d in disagree[:40]
        ],
    }
    with open(OUT, "w") as fh:
        json.dump(out, fh)
        fh.write("\n")
    print(
        json.dumps(
            {
                k: out[k]
                for k in (
                    "reader1_hits",
                    "both_yes",
                    "disagreements_excluded",
                    "routine_pool",
                    "drawn_risky",
                    "drawn_routine",
                )
            }
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())
