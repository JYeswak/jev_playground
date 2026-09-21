#!/usr/bin/env python3
"""structural-def n=77 draw: enumerate fires, seeded sample with identities.

Condition is READ from the rule file frontmatter (not transcribed), compiled
with Python re (JS/Python caveat in prereg). Match surface: the bash command
string (args.command), falling back to the args blob. Seed 2026092105,
mulberry32, 77 without replacement. Emits sample rows with rank/fire_index/
file/line/match/snippet for hand labelling.
"""

import json
import os
import random
import re
from datetime import datetime, timezone

OMP_ROOT = "/Users/josh/.omp"
RULE = "/Users/josh/Developer/jev/.omp/rules/bash-structural-def-search.md"
SEED = 2026092105
N = 77
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "structural-n77-sample-20260920.jsonl")


def mulberry32(a):
    def f():
        nonlocal a
        a = (a + 0x6D2B79F5) & 0xFFFFFFFF
        t = a
        t = ((t ^ (t >> 15)) * (t | 1)) & 0xFFFFFFFF
        t ^= t + (((t ^ (t >> 7)) * (t | 61)) & 0xFFFFFFFF)
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296

    return f


with open(RULE, encoding="utf-8") as fh:
    first = fh.read(2000)
m = re.search(r"^condition: '(.*)'$", first, re.M)
cond = m.group(1)
rx = re.compile(cond)
print(f"condition_chars={len(cond)}")

ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
files = []
for dirpath, _d, filenames in os.walk(OMP_ROOT):
    for fn in filenames:
        if fn.endswith(".jsonl"):
            files.append(os.path.join(dirpath, fn))
print(f"corpus_files={len(files)} ts={ts} seed={SEED}")

fires = []
for fp in sorted(files):
    try:
        with open(fp, encoding="utf-8", errors="replace") as fh:
            for ln, line in enumerate(fh):
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if obj.get("type") != "message":
                    continue
                msg = obj.get("message") or {}
                if msg.get("role") != "assistant":
                    continue
                for c in msg.get("content") or []:
                    if not isinstance(c, dict) or c.get("type") != "toolCall":
                        continue
                    if str(c.get("name") or "").lower() != "bash":
                        continue
                    args = c.get("arguments") or {}
                    cmd = args.get("command") or ""
                    surface = cmd if isinstance(cmd, str) else json.dumps(args)
                    mm = rx.search(surface)
                    if mm:
                        fires.append(
                            {
                                "file": os.path.relpath(fp, OMP_ROOT),
                                "line": ln,
                                "command": surface[:2000],
                                "span": mm.group(0)[:200],
                            }
                        )
    except OSError:
        continue
print(f"fires={len(fires)}")

rng = mulberry32(SEED)
order = sorted(range(len(fires)), key=lambda _: rng())
sampled = [fires[i] for i in order[: min(N, len(fires))]]
print(f"sampled={len(sampled)}")
with open(OUT, "w", encoding="utf-8") as fh:
    for rank, row in enumerate(sampled):
        fh.write(
            json.dumps(
                {
                    "rank": rank,
                    "fire_index": order[rank],
                    "file": row["file"],
                    "line": row["line"],
                    "match": row["span"],
                    "snippet": row["command"][:280],
                },
                sort_keys=True,
            )
            + "\n"
        )
print(f"out={OUT}")
