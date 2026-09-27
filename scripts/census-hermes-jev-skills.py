#!/usr/bin/env python3
"""Count keyless fleet reads/invocations of installed Hermes Jev skills."""

from __future__ import annotations
import argparse
import glob
import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


def ts(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def skill_names(roots: list[Path]) -> list[str]:
    names = set()
    for root in roots:
        if root.is_dir():
            names.update(p.name for p in root.glob("jev-*") if p.is_dir())
    return sorted(names)


def census(hours: int = 24) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=hours)
    roots = [Path.home() / ".agents/skills", Path.home() / ".claude/skills"]
    names = skill_names(roots)
    reads = Counter()
    invocations = Counter()
    purpose = Counter()
    by_profile = defaultdict(Counter)
    sessions = Counter()
    files = glob.glob(
        str(Path.home() / ".omp/profiles/*/agent/sessions/**/*.jsonl"), recursive=True
    )
    for path in files:
        profile = (
            Path(path).parts[Path(path).parts.index("profiles") + 1]
            if "profiles" in Path(path).parts
            else "unknown"
        )
        session_rows = []
        try:
            session_rows = (
                Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
            )
        except OSError:
            continue
        session_recent = False
        for line in session_rows:
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            event_ts = ts(event.get("timestamp"))
            if event_ts is not None and event_ts < cutoff:
                continue
            session_recent = True
            msg = event.get("message") or {}
            if msg.get("role") != "assistant":
                continue
            for item in msg.get("content") or []:
                if not isinstance(item, dict):
                    continue
                name = item.get("name") or item.get("toolName")
                args = item.get("arguments") or item.get("input") or {}
                if name == "read" and isinstance(args, dict):
                    target = str(args.get("path") or args.get("uri") or "")
                    for skill in names:
                        if skill in target:
                            reads[skill] += 1
                            purpose[skill + ":read"] += 1
                            by_profile[profile][skill + ":read"] += 1
                    if target.startswith("skill://jev-"):
                        skill = target.split("skill://", 1)[1].split("/", 1)[0]
                        reads[skill] += 1
                        purpose[skill + ":read"] += 1
                        by_profile[profile][skill + ":read"] += 1
                if (
                    name == "bash"
                    and isinstance(args, dict)
                    and "~/.local/bin/jev" in str(args.get("command", ""))
                ):
                    invocations["~/.local/bin/jev"] += 1
                    by_profile[profile]["jev-cli"] += 1
        if session_recent:
            sessions[profile] += 1
    skills = []
    for name in names:
        n = reads[name]
        skills.append(
            {"skill": name, "reads": n, "keep_or_prune": "keep" if n else "prune"}
        )
    return {
        "generated_at": now.isoformat(),
        "window_hours": hours,
        "cutoff": cutoff.isoformat(),
        "roots": [str(r) for r in roots],
        "skills": skills,
        "jev_cli_invocations": invocations["~/.local/bin/jev"],
        "purpose_counts": dict(sorted(purpose.items())),
        "by_profile": {
            k: dict(sorted(v.items())) for k, v in sorted(by_profile.items())
        },
        "recent_sessions_by_profile": dict(sorted(sessions.items())),
        "boundary": "Only tool-call metadata was scanned; session text and command payloads were not emitted.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--hours", type=int, default=24)
    args = parser.parse_args()
    result = census(args.hours)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
