#!/usr/bin/env python3
"""Sample real routine bash commands from jev's own omp session transcripts (bead jev-32z).

Routine = the agent ran it and the tool result came back isError=false: it was not blocked by dcg
and did not fail. That label comes from the harness, not from us. Only jev sessions are read
(every profile's sessions/-Developer-jev dir, subagent transcripts included), so no other
project's traffic is published. Commands naming a client project or carrying a secret-shaped
token are dropped, and the home directory is written as ~.

Usage: python3 work/bicameral-gate/real-sample.py [N] [SEED] [CUTOFF]
Writes work/bicameral-gate/real-sample.json. Only tool calls stamped before CUTOFF (ISO-8601 UTC,
default 2026-09-24T01:00:00Z) count, because the transcripts keep growing while agents work; with
the cutoff fixed, the same N and SEED give the same sample.
"""

import glob
import json
import os
import random
import re
import sys

N = int(sys.argv[1]) if len(sys.argv) > 1 else 300
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 20260923
CUTOFF = sys.argv[3] if len(sys.argv) > 3 else "2026-09-24T01:00:00Z"
HOME = os.path.expanduser("~")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "real-sample.json")

PRIVATE = re.compile(
    r"clutter|cfsios|cfs-|hubspot|phoenix|accountcenter|grokbot|zesttube|alps|"
    r"control-plane|omp-orchestrator|franken-harvest|josh-claude-config",
    re.I,
)
SECRET = re.compile(
    r"sk-[A-Za-z0-9_-]{20,}|xai-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{30,}|AKIA[0-9A-Z]{16}|"
    r"Bearer [A-Za-z0-9._-]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY"
)

files = []
for root in [f"{HOME}/.omp/agent/sessions"] + glob.glob(
    f"{HOME}/.omp/profiles/*/agent/sessions"
):
    files += glob.glob(f"{root}/-Developer-jev/**/*.jsonl", recursive=True)

seen = {}
stats = {"files": len(files), "bash_calls": 0, "ok": 0, "private": 0, "secret": 0}
for f in sorted(files):
    calls = {}
    try:
        lines = open(f, errors="replace")
    except OSError:
        continue
    for line in lines:
        try:
            o = json.loads(line)
        except ValueError:
            continue
        m = o.get("message") or {}
        if str(o.get("timestamp") or "") >= CUTOFF:
            continue
        if m.get("role") == "assistant":
            for c in m.get("content") or []:
                if (
                    isinstance(c, dict)
                    and c.get("type") == "toolCall"
                    and c.get("name") == "bash"
                ):
                    cmd = (c.get("arguments") or {}).get("command")
                    if isinstance(cmd, str) and cmd.strip():
                        calls[c.get("id")] = cmd
                        stats["bash_calls"] += 1
        elif m.get("role") == "toolResult" and m.get("toolCallId") in calls:
            cmd = calls.pop(m["toolCallId"])
            if m.get("isError") is not False:
                continue
            stats["ok"] += 1
            if PRIVATE.search(cmd):
                stats["private"] += 1
                continue
            if SECRET.search(cmd):
                stats["secret"] += 1
                continue
            cmd = cmd.replace(HOME, "~").strip()
            seen.setdefault(cmd, 0)
            seen[cmd] += 1

pool = sorted(seen)
stats["distinct_routine"] = len(pool)
rng = random.Random(SEED)
sample = rng.sample(pool, min(N, len(pool)))
with open(OUT, "w") as fh:
    json.dump(
        {
            "seed": SEED,
            "cutoff": CUTOFF,
            "n": len(sample),
            "stats": stats,
            "commands": sample,
        },
        fh,
        indent=1,
        ensure_ascii=False,
    )
    fh.write("\n")
print(json.dumps({"out": OUT, "n": len(sample), **stats}))
