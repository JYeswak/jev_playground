#!/usr/bin/env python3
"""Sample real tool RESULT outputs from jev's own omp session transcripts (bead jev-k9z.5).

Results = what agents read all day (bash stdout, read outputs, grep/eval
output), which decides whether an injection flag gets switched off. This is
the dual of work/bicameral-gate/real-sample.py (which samples routine
COMMANDS): same session scope (every profile's sessions/-Developer-jev
dir), same PRIVATE/SECRET filters (copied verbatim, attributed here), same
seed+cutoff reproducibility contract. Only jev sessions are read, so no
other project's traffic is published. Home directory is written as ~.

Tool types sampled: bash, read, grep, eval (outputs agents read). Skipped:
write/edit (our own writes echoed back), todo/hub/glob/yield/task/goal
(harness plumbing, not read content), web_search (3 rows, out of scope).

Usage: python3 work/jev-injection-flag/sample_tool_results.py [N] [SEED] [CUTOFF] [OUT]
Writes OUT (default work/jev-injection-flag/tool-results-sample.json): a
JSON list of {tool, text, ts, session}. Each text capped at 2000 chars.
Only results stamped before CUTOFF (ISO-8601 UTC) count, because the
transcripts keep growing while agents work.

Filter source (do not fork): work/bicameral-gate/real-sample.py:29-37.
"""

import glob
import json
import os
import random
import re
import sys

N = int(sys.argv[1]) if len(sys.argv) > 1 else 300
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 20260924
CUTOFF = sys.argv[3] if len(sys.argv) > 3 else "2026-09-24T02:30:00Z"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = (
    sys.argv[4] if len(sys.argv) > 4 else os.path.join(HERE, "tool-results-sample.json")
)
TEXT_CAP = 2000
WANT = {"bash", "read", "grep", "eval"}

# From work/bicameral-gate/real-sample.py:29-37 (verbatim, attributed).
PRIVATE = re.compile(
    r"clutter|cfsios|cfs-|hubspot|phoenix|accountcenter|grokbot|zesttube|alps|"
    r"control-plane|omp-orchestrator|franken-harvest|josh-claude-config",
    re.I,
)
SECRET = re.compile(
    r"sk-[A-Za-z0-9_-]{20,}|xai-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{30,}|AKIA[0-9A-Z]{16}|"
    r"Bearer [A-Za-z0-9._-]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY",
)

HOME = os.path.expanduser("~")


def content_text(content):
    parts = []
    if isinstance(content, list):
        for c in content:
            if isinstance(c, dict) and isinstance(c.get("text"), str):
                parts.append(c["text"])
            elif isinstance(c, str):
                parts.append(c)
    elif isinstance(content, str):
        parts.append(content)
    return "\n".join(parts)


files = []
for root in [f"{HOME}/.omp/agent/sessions"] + glob.glob(
    f"{HOME}/.omp/profiles/*/agent/sessions"
):
    files += glob.glob(f"{root}/-Developer-jev/**/*.jsonl", recursive=True)

seen = {}
stats = {"files": len(files), "results": 0, "kept": 0, "private": 0, "secret": 0}
for f in sorted(files):
    try:
        fh = open(f, errors="replace")
    except OSError:
        continue
    with fh:
        for line in fh:
            try:
                r = json.loads(line)
            except ValueError:
                continue
            m = r.get("message") or {}
            if m.get("role") != "toolResult":
                continue
            tool = m.get("toolName") or "?"
            if tool not in WANT:
                continue
            stats["results"] += 1
            ts = m.get("timestamp") or r.get("timestamp") or ""
            if isinstance(ts, (int, float)):
                from datetime import datetime, timezone

                sec = ts / 1000 if ts > 1e12 else ts
                ts = datetime.fromtimestamp(sec, timezone.utc).strftime(
                    "%Y-%m-%dT%H:%M:%SZ"
                )
            if ts and ts > CUTOFF:
                continue
            text = content_text(m.get("content")).strip()
            if not text:
                continue
            if PRIVATE.search(text):
                stats["private"] += 1
                continue
            if SECRET.search(text):
                stats["secret"] += 1
                continue
            text = text.replace(HOME, "~")[:TEXT_CAP]
            key = (tool, text)
            if key not in seen:
                seen[key] = {
                    "tool": tool,
                    "text": text,
                    "ts": ts,
                    "session": os.path.basename(os.path.dirname(f)),
                }
                stats["kept"] += 1

pool = sorted(seen.values(), key=lambda d: (d["tool"], d["text"]))
stats["distinct"] = len(pool)
rng = random.Random(SEED)
sample = rng.sample(pool, min(N, len(pool)))
with open(OUT, "w") as fh:
    json.dump(
        {
            "seed": SEED,
            "cutoff": CUTOFF,
            "n": len(sample),
            "stats": stats,
            "rows": sample,
        },
        fh,
        indent=1,
    )
    fh.write("\n")
print(json.dumps({"out": OUT, "n": len(sample), **stats}))
