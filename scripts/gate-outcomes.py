#!/usr/bin/env python3
"""Join local Jev gate rows to observable outcomes in the same omp session.

Raw session text stays local. The output contains only gate metadata, redacted command prefixes,
and a small outcome label: harm-evidence, no-evidence, or unknown.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

OUTCOME_LABELS = {"harm-evidence", "no-evidence", "unknown"}
DEFAULT_GATE_LOG = Path.home() / ".local/state/jev/gate-observe.jsonl"
DEFAULT_SIDECAR = Path.home() / ".local/state/jev/gate-observe-full.jsonl"
DEFAULT_SESSIONS = Path.home() / ".omp/profiles"
UNDO_RE = re.compile(
    r"\b(undo|revert|restore|roll\s+back|that was wrong|don.t do that|stop that)\b",
    re.I,
)
COMPENSATE_RE = re.compile(
    r"\bgit\s+(?:revert|restore|checkout\s+--|checkout\s+\.)\b", re.I
)
PATH_RE = re.compile(r"(?:^|\s)([^\s;&|]+(?:\.[A-Za-z0-9_-]+)?)(?=\s|$)")


def parse_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8", errors="replace").splitlines(), 1
    ):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            value["_line"] = line_number
            rows.append(value)
    return rows


def timestamp(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        number = float(value)
        return number / 1000 if number > 10_000_000_000 else number
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
        except ValueError:
            return None
    return None


def command_from_value(value: Any) -> str | None:
    if isinstance(value, str):
        return value if value.strip() else None
    if isinstance(value, dict):
        command = value.get("command")
        return command if isinstance(command, str) and command.strip() else None
    return None


def event_command(event: dict[str, Any]) -> tuple[str | None, str | None]:
    """Return command and tool-call id without exposing event text to callers."""
    event_type = event.get("type")
    if event_type == "custom":
        data = event.get("data") or {}
        if event.get("customType") == "tool_execution_start":
            return command_from_value(data.get("args")), data.get("toolCallId")
        if "command" in data:
            return command_from_value(data.get("command")), data.get("toolCallId")
    if event_type == "message":
        message = event.get("message") or {}
        if message.get("role") == "assistant":
            for item in message.get("content") or []:
                if isinstance(item, dict) and item.get("type") in {
                    "toolCall",
                    "tool_use",
                }:
                    name = item.get("name") or item.get("toolName")
                    if name == "bash":
                        return command_from_value(
                            item.get("arguments") or item.get("input")
                        ), item.get("id") or item.get("toolCallId")
        if message.get("role") == "toolResult" and message.get("toolName") == "bash":
            return None, message.get("toolCallId")
    return None, None


def event_texts(event: dict[str, Any]) -> Iterable[str]:
    if event.get("type") != "message":
        return ()
    message = event.get("message") or {}
    values: list[str] = []
    for item in message.get("content") or []:
        if isinstance(item, dict) and isinstance(item.get("text"), str):
            values.append(item["text"])
    return values


def is_error_result(event: dict[str, Any]) -> bool:
    if event.get("type") != "message":
        return False
    message = event.get("message") or {}
    return message.get("role") == "toolResult" and message.get("isError") is True


def outcome_kind(event: dict[str, Any]) -> str | None:
    if event.get("type") != "custom":
        return None
    custom_type = str(event.get("customType", ""))
    if not (
        "guard-rule.decision" in custom_type or "dcg-bridge.decision" in custom_type
    ):
        return None
    data = event.get("data") or {}
    values = " ".join(
        str(data.get(key, "")) for key in ("kind", "error", "reason", "decision")
    ).lower()
    if any(word in values for word in ("deny", "block", "refuse")):
        return "dcg-deny"
    return None


def normalize_paths(command: str | None) -> set[str]:
    if not command:
        return set()
    paths: set[str] = set()
    for token in PATH_RE.findall(command):
        token = token.strip("'\"`")
        if token.startswith(("-", "$", "http:", "https:")):
            continue
        if "/" in token or "." in token:
            paths.add(token)
    return paths


def load_session_events(
    root: Path,
) -> dict[
    str,
    tuple[
        list[dict[str, Any]], dict[str, list[tuple[int, dict[str, Any], str | None]]]
    ],
]:
    sessions: dict[str, list[dict[str, Any]]] = {}
    for path in sorted(root.glob("**/sessions/**/*.jsonl")):
        events = parse_jsonl(path)
        if not events:
            continue
        session_id = None
        for event in events[:10]:
            if event.get("type") == "session" and isinstance(event.get("id"), str):
                session_id = event["id"]
                break
        if session_id:
            sessions.setdefault(session_id, []).extend(events)
    indexed: dict[
        str,
        tuple[
            list[dict[str, Any]],
            dict[str, list[tuple[int, dict[str, Any], str | None]]],
        ],
    ] = {}
    for session_id, events in sessions.items():
        events.sort(
            key=lambda event: (
                timestamp(event.get("timestamp")) or 0,
                event.get("_line", 0),
            )
        )
        indexed[session_id] = (events, _command_index(events))
    return indexed


def _command_index(
    events: list[dict[str, Any]],
) -> dict[str, list[tuple[int, dict[str, Any], str | None]]]:
    indexed: dict[str, list[tuple[int, dict[str, Any], str | None]]] = {}
    for index, event in enumerate(events):
        command, tool_call_id = event_command(event)
        if command:
            digest = hashlib.sha256(command.encode()).hexdigest()
            indexed.setdefault(digest, []).append((index, event, tool_call_id))
    return indexed


def sidecar_commands(path: Path) -> dict[str, str]:
    return {
        str(row.get("cmdSha")): str(row.get("cmd"))
        for row in parse_jsonl(path)
        if row.get("cmdSha") and row.get("cmd")
    }


def join_row(
    row: dict[str, Any],
    session: tuple[
        list[dict[str, Any]], dict[str, list[tuple[int, dict[str, Any], str | None]]]
    ]
    | list[dict[str, Any]]
    | None,
    full_command: str | None,
    max_events: int,
) -> dict[str, Any]:
    result = {
        "ts": row.get("ts"),
        "session": row.get("session"),
        "cmdSha": row.get("cmdSha"),
        "cmd": row.get("cmd"),
        "status": row.get("status"),
        "flag": row.get("flag"),
        "probs": row.get("probs"),
        "latencyMs": row.get("latencyMs"),
        "tokens": row.get("tokens"),
        "outcome": "unknown",
        "evidence": [],
        "observedEvents": 0,
    }
    if session is None:
        return result
    if isinstance(session, tuple):
        events, by_hash = session
    else:
        events = session
        by_hash = _command_index(events)
    matches = by_hash.get(str(row.get("cmdSha")), [])
    if not matches:
        return result
    start, _, original_tool_id = min(
        matches,
        key=lambda item: abs(
            (timestamp(item[1].get("timestamp")) or 0) - (timestamp(row.get("ts")) or 0)
        ),
    )
    window = events[start + 1 :]
    seen_tool_results = 0
    evidence: list[str] = []
    original_paths = normalize_paths(full_command or row.get("cmd"))
    later_commands: list[str] = []
    for event in window:
        if (
            event.get("type") == "message"
            and (event.get("message") or {}).get("role") == "toolResult"
        ):
            seen_tool_results += 1
            if seen_tool_results > max_events:
                break
        if outcome_kind(event) == "dcg-deny":
            evidence.append("dcg-deny")
        command, tool_id = event_command(event)
        if command:
            later_commands.append(command)
            if COMPENSATE_RE.search(command):
                paths = normalize_paths(command)
                if original_paths and paths and original_paths & paths:
                    evidence.append("restore-or-revert")
        if is_error_result(event) and original_tool_id and tool_id == original_tool_id:
            evidence.append("failed-follow-up")
        if any(UNDO_RE.search(text) for text in event_texts(event)):
            evidence.append("undo-phrase")
        if seen_tool_results >= max_events:
            break
    evidence = list(dict.fromkeys(evidence))
    if evidence:
        result["outcome"] = "harm-evidence"
    elif seen_tool_results >= max_events:
        result["outcome"] = "no-evidence"
    result["evidence"] = evidence
    result["observedEvents"] = seen_tool_results
    return result


def join_rows(
    gate_rows: list[dict[str, Any]],
    sidecar: dict[str, str],
    sessions: dict[
        str,
        tuple[
            list[dict[str, Any]],
            dict[str, list[tuple[int, dict[str, Any], str | None]]],
        ],
    ],
    max_events: int = 20,
) -> list[dict[str, Any]]:
    return [
        join_row(
            row,
            sessions.get(str(row.get("session"))),
            sidecar.get(str(row.get("cmdSha"))),
            max_events,
        )
        for row in gate_rows
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gate-log", type=Path, default=DEFAULT_GATE_LOG)
    parser.add_argument("--sidecar", type=Path, default=DEFAULT_SIDECAR)
    parser.add_argument("--sessions-root", type=Path, default=DEFAULT_SESSIONS)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--max-events", type=int, default=20)
    parser.add_argument("--robot", action="store_true")
    args = parser.parse_args(argv)
    rows = join_rows(
        parse_jsonl(args.gate_log),
        sidecar_commands(args.sidecar),
        load_session_events(args.sessions_root),
        args.max_events,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        "".join(
            json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n"
            for row in rows
        ),
        encoding="utf-8",
    )
    summary = {
        "rows": len(rows),
        "outcomes": dict(Counter(row["outcome"] for row in rows)),
        "out": str(args.out),
    }
    print(
        json.dumps(summary, sort_keys=True)
        if args.robot
        else f"rows={summary['rows']} outcomes={summary['outcomes']} out={args.out}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
