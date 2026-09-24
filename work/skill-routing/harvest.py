#!/usr/bin/env python3
"""Harvest (user message -> first skill the agent read) pairs from jev's omp transcripts (jev-i8r).

Scope and filters are work/bicameral-gate/real-sample.py's: every profile's
sessions/-Developer-jev dir (subagent transcripts included), entries stamped before CUTOFF only,
the home directory written as ~, and a pair dropped when its prompt or its skill name matches
that file's PRIVATE or SECRET pattern. The two patterns are read out of real-sample.py's source
(ast, no execution), so there is one copy of each.

A pair: a message with role "user", and the first `read` tool call the agent made before the next
user message whose path is `skill://<name>...` or `.../skills/<name>/SKILL.md`. Messages followed
by no skill read are counted, not emitted. Identical (prompt, skill) pairs, from a message
broadcast to several panes, are kept once.

`names_skill` marks a prompt that contains the label's name: routing that prompt is string
matching, not judgment, so the bar scores those rows separately.

Usage: python3 work/skill-routing/harvest.py [CUTOFF]   (default 2026-09-24T03:00:00Z)
Writes work/skill-routing/pairs.jsonl and prints the counts. Deterministic for a fixed CUTOFF
while the transcripts before it are unchanged.
"""

import ast
import glob
import json
import os
import re
import sys
from collections import Counter

CUTOFF = sys.argv[1] if len(sys.argv) > 1 else "2026-09-24T03:00:00Z"
HOME = os.path.expanduser("~")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "pairs.jsonl")
SOURCE = os.path.join(HERE, "..", "bicameral-gate", "real-sample.py")
SKILL = re.compile(r"^skill://([^/:?#]+)|/skills/([^/]+)/SKILL\.md$")


def filters_from_source(path):
    """PRIVATE and SECRET exactly as real-sample.py compiles them."""
    found = {}
    for node in ast.parse(open(path).read()).body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            name = node.targets[0].id if isinstance(node.targets[0], ast.Name) else None
            if name in ("PRIVATE", "SECRET"):
                pattern = ast.literal_eval(node.value.args[0])
                flags = 0
                for arg in node.value.args[1:]:
                    if isinstance(arg, ast.Attribute) and arg.attr in (
                        "I",
                        "IGNORECASE",
                    ):
                        flags |= re.I
                found[name] = re.compile(pattern, flags)
    if set(found) != {"PRIVATE", "SECRET"}:
        raise SystemExit(f"filters not found in {path}: {sorted(found)}")
    return found["PRIVATE"], found["SECRET"]


PRIVATE, SECRET = filters_from_source(SOURCE)


def text_of(message):
    content = message.get("content")
    if isinstance(content, str):
        return content
    return "\n".join(
        c.get("text", "")
        for c in content or []
        if isinstance(c, dict) and c.get("type") == "text"
    )


def main():
    files = []
    for root in [f"{HOME}/.omp/agent/sessions"] + glob.glob(
        f"{HOME}/.omp/profiles/*/agent/sessions"
    ):
        files += glob.glob(f"{root}/-Developer-jev/**/*.jsonl", recursive=True)
    stats = Counter(files=len(files))
    raw = []
    for path in sorted(files):
        cur = None
        try:
            fh = open(path, errors="replace")
        except OSError:
            continue
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
                    raw.append(cur)
                stats["user_messages"] += 1
                cur = {"prompt": text_of(m), "ts": o.get("timestamp"), "skill": None}
            elif m.get("role") == "assistant" and cur and cur["skill"] is None:
                for c in m.get("content") or []:
                    if (
                        isinstance(c, dict)
                        and c.get("type") == "toolCall"
                        and c.get("name") == "read"
                    ):
                        p = (c.get("arguments") or {}).get("path")
                        hit = SKILL.search(p) if isinstance(p, str) else None
                        if hit:
                            cur["skill"] = (hit.group(1) or hit.group(2)).lower()
                            break
        if cur:
            raw.append(cur)

    pairs, seen = [], set()
    for r in raw:
        if not r["skill"]:
            stats["no_skill_read"] += 1
            continue
        stats["with_skill_read"] += 1
        if PRIVATE.search(r["prompt"]) or PRIVATE.search(r["skill"]):
            stats["private"] += 1
            continue
        if SECRET.search(r["prompt"]):
            stats["secret"] += 1
            continue
        prompt = r["prompt"].replace(HOME, "~").strip()
        if (prompt, r["skill"]) in seen:
            stats["duplicate"] += 1
            continue
        seen.add((prompt, r["skill"]))
        pairs.append(
            {
                "prompt": prompt,
                "skill": r["skill"],
                "ts": r["ts"],
                "names_skill": r["skill"] in prompt.lower(),
            }
        )
    pairs.sort(key=lambda p: (p["ts"] or "", p["skill"]))
    with open(OUT, "w", encoding="utf-8") as fh:
        for i, p in enumerate(pairs):
            fh.write(json.dumps({"i": i, **p}, ensure_ascii=False) + "\n")

    labels = Counter(p["skill"] for p in pairs)
    unnamed = Counter(p["skill"] for p in pairs if not p["names_skill"])
    print(
        json.dumps(
            {
                "cutoff": CUTOFF,
                **stats,
                "pairs": len(pairs),
                "names_skill": sum(p["names_skill"] for p in pairs),
                "unnamed": sum(unnamed.values()),
                "distinct_skills": len(labels),
                "labels": labels.most_common(),
                "unnamed_labels": unnamed.most_common(),
            },
            indent=1,
        )
    )


if __name__ == "__main__":
    main()
