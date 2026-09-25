#!/usr/bin/env python3
"""Harvest (user message -> what the agent actually did) routing goals from jev's omp transcripts (jev-vbh.4).

The usage router (src/router.mjs) asks Jev to route a goal to local | research | browser, with
bypass as its abstain. The only goals it had seen were 6 authored demo prompts. This harvester
builds a non-authored set from real traffic: every user message in jev's sessions before CUTOFF,
labelled by the tool calls the agent made before the next user message, never by a person.

Label, highest first:
  browser   an eval call whose code drives browser./tab./computer., or a tool named browser
  research  web_search, a read of an http(s) URL, or bash running curl/wget against an http(s) URL
  local     anything else, including a turn answered with no tool call

Scope and privacy filters are work/skill-routing/harvest.py's (which reads real-sample.py's
PRIVATE and SECRET patterns): every profile's sessions/-Developer-jev dir, entries stamped before
CUTOFF, the home directory written as ~. Dropped and counted: empty messages, messages longer
than MAX_CHARS (pasted skill bodies and transcripts, not goals), PRIVATE/SECRET matches, and
repeats of an identical goal (a message broadcast to several panes is kept once, first seen).

Usage: python3 work/jev-usage-router/harvest_goals.py [CUTOFF]   (default 2026-09-25T13:00:00Z)
Writes work/jev-usage-router/goals-<cutoff date>.jsonl, prints counts and the file's sha256.
"""

import glob
import hashlib
import importlib.util
import json
import os
import re
import sys
from collections import Counter

CUTOFF = sys.argv[1] if len(sys.argv) > 1 else "2026-09-25T13:00:00Z"
HOME = os.path.expanduser("~")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, f"goals-{CUTOFF[:10]}.jsonl")
MAX_CHARS = 4000
SHORT_CHARS = 200

_spec = importlib.util.spec_from_file_location(
    "skill_harvest", os.path.join(HERE, "..", "skill-routing", "harvest.py")
)
_skill_harvest = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_skill_harvest)
PRIVATE, SECRET, text_of = (
    _skill_harvest.PRIVATE,
    _skill_harvest.SECRET,
    _skill_harvest.text_of,
)

BROWSER_CODE = re.compile(
    r"\bbrowser\.(open|tab|tabs|close)\b|\btab\.[a-z]+\(|\bcomputer\.[a-z]+"
)
URL = re.compile(r"^https?://")
FETCH = re.compile(r"\b(curl|wget)\b[^\n|;&]*https?://")
RANK = {"local": 0, "research": 1, "browser": 2}


def action_class(call):
    """The routing class one tool call evidences."""
    name = call.get("name")
    args = call.get("arguments") or {}
    if name == "browser":
        return "browser"
    if name == "eval" and BROWSER_CODE.search(str(args.get("code") or "")):
        return "browser"
    if name == "web_search":
        return "research"
    if name == "read" and URL.match(str(args.get("path") or "")):
        return "research"
    if name == "bash" and FETCH.search(str(args.get("command") or "")):
        return "research"
    return "local"


def label_turn(calls):
    """Highest class over a turn's tool calls; a turn with no tool call is local."""
    best = "local"
    for call in calls:
        cls = action_class(call)
        if RANK[cls] > RANK[best]:
            best = cls
    return best


def turns_of(path):
    """(timestamp, goal, tool calls) per user message in one transcript, before CUTOFF."""
    turns, cur = [], None
    with open(path, errors="replace") as fh:
        for line in fh:
            try:
                o = json.loads(line)
            except ValueError:
                continue
            if str(o.get("timestamp") or "") >= CUTOFF:
                continue
            m = o.get("message") or {}
            if m.get("role") == "user":
                if cur:
                    turns.append(cur)
                cur = {"ts": o.get("timestamp"), "goal": text_of(m), "calls": []}
            elif m.get("role") == "assistant" and cur is not None:
                for c in m.get("content") or []:
                    if isinstance(c, dict) and c.get("type") == "toolCall":
                        cur["calls"].append(c)
    if cur:
        turns.append(cur)
    return turns


def main():
    files = []
    for root in [f"{HOME}/.omp/agent/sessions"] + glob.glob(
        f"{HOME}/.omp/profiles/*/agent/sessions"
    ):
        files += glob.glob(f"{root}/-Developer-jev/**/*.jsonl", recursive=True)
    stats = Counter(files=len(files))
    rows, seen = [], set()
    for path in sorted(files):
        subagent = os.path.basename(os.path.dirname(path)) != "-Developer-jev"
        for t in turns_of(path):
            stats["user_messages"] += 1
            goal = t["goal"].strip()
            if not goal:
                stats["empty"] += 1
                continue
            if len(goal) > MAX_CHARS:
                stats["too_long"] += 1
                continue
            if PRIVATE.search(goal):
                stats["private"] += 1
                continue
            if SECRET.search(goal):
                stats["secret"] += 1
                continue
            goal = goal.replace(HOME, "~")
            if goal in seen:
                stats["duplicate"] += 1
                continue
            seen.add(goal)
            rows.append(
                {
                    "goal": goal,
                    "label": label_turn(t["calls"]),
                    "tool_calls": len(t["calls"]),
                    "short": len(goal) < SHORT_CHARS,
                    "from_pane1": goal.startswith("From pane 1"),
                    "subagent": subagent,
                    "ts": t["ts"],
                }
            )
    rows.sort(key=lambda r: (r["ts"] or "", r["goal"]))
    with open(OUT, "w", encoding="utf-8") as fh:
        for i, r in enumerate(rows):
            fh.write(json.dumps({"i": i, **r}, ensure_ascii=False) + "\n")
    with open(OUT, "rb") as fh:
        digest = hashlib.sha256(fh.read()).hexdigest()
    labels = Counter(r["label"] for r in rows)
    short = Counter(r["label"] for r in rows if r["short"])
    print(
        json.dumps(
            {
                "cutoff": CUTOFF,
                **stats,
                "goals": len(rows),
                "labels": dict(labels.most_common()),
                "short_labels": dict(short.most_common()),
                "from_pane1": sum(r["from_pane1"] for r in rows),
                "subagent": sum(r["subagent"] for r in rows),
                "out": os.path.relpath(OUT),
                "sha256": digest,
            },
            indent=1,
        )
    )


if __name__ == "__main__":
    main()
