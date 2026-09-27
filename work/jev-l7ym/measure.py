#!/usr/bin/env python3
"""Measure omp find rank against the next ten real tool calls.

The input is local omp session JSONL only. Output contains aggregates and
Wilson intervals; it never writes session rows or tool arguments.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import sys
import time
from collections import defaultdict
from typing import Any, Iterable

WINDOW_TOOL_NAMES = {"read", "edit", "write"}
DEFAULT_DAYS = 3


def _dict(value: Any) -> dict[str, Any] | None:
    return value if isinstance(value, dict) else None


def _tool_calls(rows: list[dict[str, Any]]) -> list[tuple[int, dict[str, Any]]]:
    calls: list[tuple[int, dict[str, Any]]] = []
    for line_no, row in enumerate(rows, 1):
        message = _dict(row.get("message"))
        if not message or message.get("role") != "assistant":
            continue
        content = message.get("content")
        if not isinstance(content, list):
            continue
        for item in content:
            item = _dict(item)
            if (
                item
                and item.get("type") == "toolCall"
                and isinstance(item.get("id"), str)
            ):
                calls.append((line_no, item))
    return calls


def _find_results(rows: list[dict[str, Any]]) -> dict[str, tuple[int, dict[str, Any]]]:
    results: dict[str, tuple[int, dict[str, Any]]] = {}
    for line_no, row in enumerate(rows, 1):
        message = _dict(row.get("message"))
        if (
            not message
            or message.get("role") != "toolResult"
            or message.get("toolName") != "find"
        ):
            continue
        call_id = message.get("toolCallId")
        details = _dict(message.get("details"))
        if isinstance(call_id, str) and details is not None:
            results[call_id] = (line_no, details)
    return results


def _clean_path(value: Any) -> str | None:
    if not isinstance(value, str) or not value or "\x00" in value:
        return None
    value = value.replace("\\", "/")
    if value.startswith("/"):
        return os.path.normpath(value).replace("\\", "/")
    value = str(PurePosixPath(value))
    if value in ("", ".", "..") or value.startswith("../"):
        return None
    return value[2:] if value.startswith("./") else value


def _candidates(details: dict[str, Any]) -> list[str]:
    hits = details.get("hits")
    if not isinstance(hits, list):
        return []
    paths: list[str] = []
    for hit in hits:
        hit = _dict(hit)
        rel = _clean_path(hit.get("rel") if hit else None)
        if rel is not None:
            paths.append(rel)
    return paths


def _path_forms(value: Any, details: dict[str, Any]) -> set[str]:
    raw = _clean_path(value)
    if raw is None:
        return set()
    forms = {raw}
    if raw.startswith("/"):
        for key in ("scopePath", "cwd"):
            base = _clean_path(details.get(key))
            if base and base.startswith("/"):
                try:
                    forms.add(os.path.relpath(raw, base).replace("\\", "/"))
                except ValueError:
                    pass
    return {form[2:] if form.startswith("./") else form for form in forms}


def _edit_text_paths(arguments: dict[str, Any]) -> list[str]:
    value = arguments.get("input")
    if not isinstance(value, str):
        return []
    # edit's public argument is a textual patch. Only path-like tokens are
    # considered; file contents are never emitted or treated as instructions.
    return re.findall(
        r"(?<![A-Za-z0-9_./-])(?:[A-Za-z0-9_.-]+/)+[A-Za-z0-9_.-]+", value
    )


def _used_rank(
    tool: dict[str, Any], details: dict[str, Any], candidates: list[str]
) -> int | None:
    name = tool.get("name")
    arguments = _dict(tool.get("arguments")) or {}
    values: list[str] = []
    if name in {"read", "write"}:
        if isinstance(arguments.get("path"), str):
            values.append(arguments["path"])
    elif name == "edit":
        values.extend(_edit_text_paths(arguments))
    if not values:
        return None
    candidate_forms = [
        _path_forms(candidate, details) | {candidate} for candidate in candidates
    ]
    for value in values:
        forms = _path_forms(value, details)
        for index, expected in enumerate(candidate_forms):
            if forms & expected:
                return index + 1
            if any(
                value == form or value.endswith("/" + form) for form in expected if form
            ):
                return index + 1
    return None


def wilson(successes: int, total: int, z: float = 1.959963984540054) -> dict[str, Any]:
    if total <= 0:
        return {"hits": successes, "n": total, "rate": None, "low": None, "high": None}
    p = successes / total
    denominator = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / denominator
    margin = z * math.sqrt((p * (1 - p) + z * z / (4 * total)) / total) / denominator
    return {
        "hits": successes,
        "n": total,
        "rate": p,
        "low": max(0.0, centre - margin),
        "high": min(1.0, centre + margin),
    }


def _empty() -> dict[str, Any]:
    return {
        "find_calls": 0,
        "find_results": 0,
        "ranked_calls": 0,
        "windowed_calls": 0,
        "used_returned_file": 0,
        "no_returned_file_used": 0,
        "actual_top1": 0,
        "actual_top3": 0,
        "baseline_top1": 0,
        "baseline_top3": 0,
        "actual_ranks": [],
        "baseline_ranks": [],
    }


def _public(stats: dict[str, Any], profile: str) -> dict[str, Any]:
    windowed = stats["windowed_calls"]
    actual = stats["actual_ranks"]
    baseline = stats["baseline_ranks"]
    return {
        "profile": profile,
        "find_calls": stats["find_calls"],
        "find_results": stats["find_results"],
        "ranked_calls": stats["ranked_calls"],
        "windowed_calls": windowed,
        "used_returned_file": stats["used_returned_file"],
        "no_returned_file_used": stats["no_returned_file_used"],
        "no_returned_file_used_share": (
            stats["no_returned_file_used"] / stats["find_results"]
            if stats["find_results"]
            else None
        ),
        "actual": {
            "top1": wilson(stats["actual_top1"], windowed),
            "top3": wilson(stats["actual_top3"], windowed),
            "median_rank": sorted(actual)[len(actual) // 2] if actual else None,
        },
        "baseline": {
            "top1": wilson(stats["baseline_top1"], windowed),
            "top3": wilson(stats["baseline_top3"], windowed),
            "median_rank": sorted(baseline)[len(baseline) // 2] if baseline else None,
        },
        "denominators": {
            "ranked_calls": stats["ranked_calls"],
            "windowed_calls": windowed,
        },
    }


def _analyze_raw(rows: list[dict[str, Any]]) -> dict[str, Any]:
    calls = _tool_calls(rows)
    results = _find_results(rows)
    stats = _empty()
    stats["find_calls"] = sum(1 for _, call in calls if call.get("name") == "find")
    for _, call in calls:
        if call.get("name") != "find":
            continue
        result = results.get(call.get("id"))
        if result is None:
            continue
        result_line, details = result
        stats["find_results"] += 1
        candidates = _candidates(details)
        if not candidates:
            stats["no_returned_file_used"] += 1
            continue
        stats["ranked_calls"] += 1
        baseline_order = sorted(
            range(len(candidates)),
            key=lambda index: (len(candidates[index]), candidates[index]),
        )
        baseline_rank = {
            candidate_index: rank + 1
            for rank, candidate_index in enumerate(baseline_order)
        }
        actual_rank = None
        for _, later_call in [entry for entry in calls if entry[0] > result_line][:10]:
            actual_rank = _used_rank(later_call, details, candidates)
            if actual_rank is not None:
                break
        if actual_rank is None:
            stats["no_returned_file_used"] += 1
            continue
        baseline_used_rank = baseline_rank[actual_rank - 1]
        stats["windowed_calls"] += 1
        stats["used_returned_file"] += 1
        stats["actual_ranks"].append(actual_rank)
        stats["baseline_ranks"].append(baseline_used_rank)
        stats["actual_top1"] += actual_rank == 1
        stats["actual_top3"] += actual_rank <= 3
        stats["baseline_top1"] += baseline_used_rank == 1
        stats["baseline_top3"] += baseline_used_rank <= 3
    return stats


def analyze_rows(
    rows: list[dict[str, Any]], profile: str = "fixture"
) -> dict[str, Any]:
    """Analyze one parsed session; pure and suitable for offline tests."""
    return _public(_analyze_raw(rows), profile)


def _iter_recent_files(root: Path, cutoff: float) -> Iterable[Path]:
    for path in root.glob("*/agent/sessions/**/*.jsonl"):
        try:
            if path.is_symlink() or not path.is_file() or path.stat().st_mtime < cutoff:
                continue
        except OSError:
            continue
        yield path


def _read_rows(path: Path) -> tuple[list[dict[str, Any]], int]:
    rows: list[dict[str, Any]] = []
    malformed = 0
    try:
        with path.open(encoding="utf-8", errors="replace") as handle:
            for line in handle:
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    malformed += 1
                    continue
                if isinstance(row, dict):
                    rows.append(row)
    except OSError:
        malformed += 1
    return rows, malformed


def _merge(raw_reports: list[dict[str, Any]], profile: str) -> dict[str, Any]:
    merged = _empty()
    for report in raw_reports:
        for key in (
            "find_calls",
            "find_results",
            "ranked_calls",
            "windowed_calls",
            "used_returned_file",
            "no_returned_file_used",
            "actual_top1",
            "actual_top3",
            "baseline_top1",
            "baseline_top3",
        ):
            merged[key] += report[key]
        merged["actual_ranks"].extend(report["actual_ranks"])
        merged["baseline_ranks"].extend(report["baseline_ranks"])
    return _public(merged, profile)


def run(root: Path, days: int = DEFAULT_DAYS) -> dict[str, Any]:
    cutoff = time.time() - days * 86400
    by_profile: dict[str, list[dict[str, Any]]] = defaultdict(list)
    files_seen = files_selected = malformed = 0
    for path in _iter_recent_files(root, cutoff):
        files_seen += 1
        rows, bad = _read_rows(path)
        malformed += bad
        profile = path.relative_to(root).parts[0]
        by_profile[profile].append(_analyze_raw(rows))
        files_selected += 1
    all_reports = [report for reports in by_profile.values() for report in reports]
    return {
        "schema": "jev-l7ym.v1",
        "lane": "keyless-log-only",
        "window_days": days,
        "cutoff_utc": dt.datetime.fromtimestamp(cutoff, dt.timezone.utc).isoformat(),
        "source": "~/.omp/profiles/*/agent/sessions/**/*.jsonl",
        "files": {
            "selected": files_selected,
            "seen": files_seen,
            "malformed_json_lines": malformed,
        },
        "baseline": {
            "name": "path-length-then-lexical",
            "definition": "same returned hits sorted by (len(rel), rel); no pre-rerank order was logged in inspected find result details",
        },
        "next_window": {"tool_calls": 10, "matched_tools": sorted(WINDOW_TOOL_NAMES)},
        "overall": _merge(all_reports, "all-profiles"),
        "per_profile": {
            profile: _merge(reports, profile)
            for profile, reports in sorted(by_profile.items())
        },
        "boundary": "Logs establish association, not causality. The baseline is a deterministic proxy because find's pre-rerank order is absent from recorded result details. Bash/eval/grep/glob path use is not counted; only read, edit, and write arguments are matched. Hit rates use find results with at least one returned file and a matched next-ten read/edit/write window; no-returned-file share uses all find results.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.home() / ".omp" / "profiles")
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    if args.days <= 0:
        parser.error("--days must be positive")
    report = run(args.root, args.days)
    encoded = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    sys.stdout.write(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
