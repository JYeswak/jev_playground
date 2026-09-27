#!/usr/bin/env python3
"""Audit whether web-search shadow rows can observe later opens, without raw text."""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

URL_RE = re.compile(r"https?://[^\s)\]}>\"']+")
HOOK_OPEN_TOOLS = {"read", "fetch", "web_extract", "open_url"}
BROWSER_OPEN_PREFIXES = ("browser.", "computer.")


def sha(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def parse_ts(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def paths(home: Path) -> list[Path]:
    roots = [home / ".omp/agent/sessions"] + list(
        (home / ".omp/profiles").glob("*/agent/sessions")
    )
    return [
        path for root in roots if root.exists() for path in root.glob("*/*_*.jsonl")
    ]


def text_content(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n".join(
            text_content(item.get("text", "") if isinstance(item, dict) else item)
            for item in value
        )
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    return ""


def event_args(part: dict[str, Any]) -> dict[str, Any]:
    value = part.get("arguments", part.get("input", {}))
    return value if isinstance(value, dict) else {}


def tool_values(args: dict[str, Any]) -> list[str]:
    return [
        str(value)
        for value in (
            args.get("url"),
            args.get("path"),
            args.get("query"),
            args.get("input"),
        )
        if isinstance(value, str)
    ]


def audit_file(path: Path, start: datetime) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    results: dict[str, str] = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    for line in lines:
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        timestamp = parse_ts(record.get("timestamp"))
        message = record.get("message")
        if not isinstance(message, dict):
            continue
        role = message.get("role")
        content = message.get("content") or []
        if role == "toolResult":
            call_id = message.get("toolCallId")
            if isinstance(call_id, str):
                results[call_id] = text_content(message.get("content"))
        if role != "assistant" or not isinstance(content, list):
            continue
        for part in content:
            if not isinstance(part, dict) or part.get("type") != "toolCall":
                continue
            name = part.get("name")
            call_id = part.get("id", part.get("toolCallId"))
            if not isinstance(name, str) or not isinstance(call_id, str):
                continue
            entries.append(
                {
                    "timestamp": timestamp,
                    "name": name,
                    "id": call_id,
                    "args": event_args(part),
                    "result": None,
                }
            )
    # Associate results after reading all records; call order remains transcript order.
    for entry in entries:
        entry["result"] = results.get(entry["id"], "")
    return [
        entry
        for entry in entries
        if entry["timestamp"] is None or entry["timestamp"] >= start
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument(
        "--out-dir", type=Path, default=Path("var/agent-tmp/web-open-audit")
    )
    args = parser.parse_args()
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=args.days)
    windows: list[dict[str, Any]] = []
    files = 0
    for path in paths(Path.home()):
        files += 1
        calls = audit_file(path, start)
        for index, call in enumerate(calls):
            if call["name"] != "web_search":
                continue
            urls = URL_RE.findall(call["result"] or "")
            if len(urls) < 2:
                continue
            follow = calls[index + 1 : index + 11]
            opened: list[dict[str, Any]] = []
            for item in follow:
                values = tool_values(item["args"])
                matched = [
                    url
                    for url in urls
                    if any(url.rstrip(".,") in value for value in values)
                ]
                broad = bool(matched) or item["name"].startswith(BROWSER_OPEN_PREFIXES)
                if broad:
                    opened.append(
                        {
                            "tool": item["name"],
                            "hook_detectable": item["name"] in HOOK_OPEN_TOOLS,
                            "matched_url_hashes": [
                                sha(url.rstrip(".,")) for url in matched
                            ],
                        }
                    )
            windows.append(
                {
                    "window_id": sha(f"{path}:{call['id']}"),
                    "session_hash": sha(str(path.parent)),
                    "query_hash": sha(str(call["args"].get("query", ""))),
                    "result_count": len(urls),
                    "url_hashes": [sha(url.rstrip(".,")) for url in urls],
                    "next_tool_names": [item["name"] for item in follow],
                    "opens": opened,
                    "opened_any": bool(opened),
                    "hook_detectable_open": any(
                        item["hook_detectable"] for item in opened
                    ),
                }
            )
    usable = sum(window["hook_detectable_open"] for window in windows)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "schema": "jev-web-open-audit.v1",
        "window_start": start.isoformat(),
        "window_end": now.isoformat(),
        "days": args.days,
        "session_files": files,
        "web_search_windows": len(windows),
        "usable_hook_windows": usable,
        "any_open_windows": sum(window["opened_any"] for window in windows),
        "expected_usable_windows_per_48h": usable * 2 / args.days,
        "boundary": "Hash-only session audit; no command, query, URL, or model call; usable means a read/fetch/web_extract/open_url within ten subsequent tool calls matched a returned URL.",
    }
    (args.out_dir / "report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n"
    )
    (args.out_dir / "windows.jsonl").write_text(
        "".join(json.dumps(window, sort_keys=True) + "\n" for window in windows)
    )
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
