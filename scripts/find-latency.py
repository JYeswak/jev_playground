#!/usr/bin/env python3
"""Measure omp find's native usage and end-to-end tool-result latency from local sessions."""

from __future__ import annotations

import argparse
import glob
import json
from datetime import datetime
from pathlib import Path
from typing import Any

TOKEN_LIMIT = 32768
NEAR_TOKENS = 28000


def percentile(values: list[float], p: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = (len(ordered) - 1) * p
    lower = int(index)
    upper = min(lower + 1, len(ordered) - 1)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (index - lower)


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


def read_events(root: Path) -> list[list[dict[str, Any]]]:
    sessions: list[list[dict[str, Any]]] = []
    for path in glob.glob(str(root / "**/sessions/**/*.jsonl"), recursive=True):
        events: list[dict[str, Any]] = []
        for line in (
            Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
        ):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict):
                events.append(value)
        if events:
            events.sort(key=lambda event: timestamp(event.get("timestamp")) or 0)
            sessions.append(events)
    return sessions


def summarize(values: list[float]) -> dict[str, float | int | None]:
    return {
        "n": len(values),
        "p50": percentile(values, 0.5),
        "p95": percentile(values, 0.95),
        "max": max(values) if values else None,
    }


def analyze(sessions: list[list[dict[str, Any]]]) -> dict[str, Any]:
    usage_rows: list[dict[str, Any]] = []
    tool_rows: list[dict[str, Any]] = []
    for events in sessions:
        for index, event in enumerate(events):
            message_raw: Any = event.get("message")
            message = message_raw if isinstance(message_raw, dict) else {}
            if (
                event.get("type") == "model_usage"
                and event.get("provider") == "typesafe"
                and event.get("purpose") == "find"
            ):
                usage_raw: Any = event.get("usage")
                usage = usage_raw if isinstance(usage_raw, dict) else {}
                input_raw: Any = usage.get("input")
                input_tokens = (
                    float(input_raw) if isinstance(input_raw, (int, float)) else 0.0
                )
                cost_raw: Any = usage.get("cost")
                if isinstance(cost_raw, dict):
                    cost_raw = cost_raw.get("total")
                cost = (
                    float(cost_raw)
                    if isinstance(cost_raw, (int, float))
                    else input_tokens * 0.042 / 1_000_000
                )
                latency = None
                for follow in events[index + 1 :]:
                    follow_raw: Any = follow.get("message")
                    follow_message = follow_raw if isinstance(follow_raw, dict) else {}
                    if (
                        follow.get("type") == "message"
                        and follow_message.get("role") == "assistant"
                    ):
                        if isinstance(follow_message.get("duration"), (int, float)):
                            latency = float(follow_message["duration"])
                        else:
                            start = timestamp(event.get("timestamp"))
                            end = timestamp(follow.get("timestamp"))
                            if start is not None and end is not None:
                                latency = max(0.0, (end - start) * 1000)
                        break
                usage_rows.append(
                    {
                        "input_tokens": float(input_tokens),
                        "cost": cost,
                        "latency": latency,
                    }
                )
            if (
                event.get("type") == "message"
                and message.get("role") == "toolResult"
                and message.get("toolName") == "find"
            ):
                details_raw: Any = message.get("details")
                details = details_raw if isinstance(details_raw, dict) else {}
                stats_raw: Any = details.get("stats")
                stats = stats_raw if isinstance(stats_raw, dict) else {}
                tool_rows.append(
                    {
                        "elapsed": details.get("elapsedMs"),
                        "api": stats.get("apiMs"),
                        "input_tokens": stats.get("inputTokens"),
                        "file_bytes": stats.get("fileBytes"),
                        "requests": stats.get("requests"),
                        "errors": stats.get("errors"),
                        "cost": stats.get("cost"),
                    }
                )

    usage_latency = [
        float(row["latency"])
        for row in usage_rows
        if isinstance(row["latency"], (int, float))
    ]
    tool_elapsed = [
        float(row["elapsed"])
        for row in tool_rows
        if isinstance(row["elapsed"], (int, float))
    ]
    tool_api = [
        float(row["api"]) for row in tool_rows if isinstance(row["api"], (int, float))
    ]
    input_tokens = [
        float(row["input_tokens"])
        for row in usage_rows
        if isinstance(row["input_tokens"], (int, float))
    ]
    stats_input = [
        float(row["input_tokens"])
        for row in tool_rows
        if isinstance(row["input_tokens"], (int, float))
    ]
    usage_cost = sum(row["cost"] for row in usage_rows)
    return {
        "sessions": len(sessions),
        "model_usage_find": {
            "calls": len(usage_rows),
            "input_tokens": summarize(input_tokens),
            "latency_ms": summarize(usage_latency),
            "spend_usd": usage_cost,
            "near_32k_input_token_calls": sum(
                value >= NEAR_TOKENS for value in input_tokens
            ),
            "over_32k_input_token_calls": sum(
                value > TOKEN_LIMIT for value in input_tokens
            ),
        },
        "find_tool_results": {
            "calls": len(tool_rows),
            "elapsed_ms": summarize(tool_elapsed),
            "api_ms_aggregate_across_parallel_requests": summarize(tool_api),
            "input_tokens": summarize(stats_input),
            "file_bytes": summarize(
                [
                    float(row["file_bytes"])
                    for row in tool_rows
                    if isinstance(row["file_bytes"], (int, float))
                ]
            ),
            "cost_usd": sum(
                float(row["cost"])
                for row in tool_rows
                if isinstance(row["cost"], (int, float))
            ),
            "errors": sum(
                int(row["errors"])
                for row in tool_rows
                if isinstance(row["errors"], (int, float))
            ),
        },
        "documented_config": {
            "find_enabled": "auto|on|off",
            "default": "auto",
            "candidate_count": 128,
            "files_read": 20,
            "windows_per_file": 24,
            "window_bytes": 8192,
            "sketch_bytes": 384,
            "verified_passages": 40,
            "source": "omp://tools/find.md",
            "smaller_candidate_or_snippet_knob": "none documented; caps are fixed in cascade.ts",
        },
        "boundary": "Input-token values are the native model_usage/state proxy; raw query/session text is not emitted. API milliseconds aggregate parallel requests and are not added as wall time. Find outcome/ranking joins are not present in this receipt.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sessions-root", type=Path, default=Path.home() / ".omp/profiles"
    )
    parser.add_argument("--robot", action="store_true")
    args = parser.parse_args(argv)
    result = analyze(read_events(args.sessions_root))
    if args.robot:
        print(json.dumps(result, sort_keys=True))
    else:
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
