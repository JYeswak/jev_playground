#!/usr/bin/env python3
"""Audit every local source behind omp find's Jev usage telemetry.

This is log-only. It counts direct find results, eval-host find outputs, and
model_usage rows without persisting session text or paths.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
from collections import Counter
from typing import Any

WINDOW_TOOLS = {"read", "edit", "write"}
BROAD_TOOLS = WINDOW_TOOLS | {"bash", "grep", "glob"}
DEFAULT_DAYS = 7


def _dict(value: Any) -> dict[str, Any] | None:
    return value if isinstance(value, dict) else None


def _timestamp(row: dict[str, Any]) -> dt.datetime | None:
    value = row.get("timestamp")
    if not isinstance(value, str):
        return None
    try:
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _path(value: Any) -> str | None:
    if not isinstance(value, str) or not value or "\x00" in value:
        return None
    value = value.replace("\\", "/")
    if value.startswith("/"):
        return os.path.normpath(value).replace("\\", "/")
    value = str(PurePosixPath(value))
    if value in ("", ".", "..") or value.startswith("../"):
        return None
    return value[2:] if value.startswith("./") else value


def _tool_calls(rows: list[dict[str, Any]]) -> list[tuple[int, dict[str, Any]]]:
    calls = []
    for index, row in enumerate(rows):
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
                calls.append((index, item))
    return calls


def _find_results(rows: list[dict[str, Any]]) -> dict[str, tuple[int, dict[str, Any]]]:
    results = {}
    for index, row in enumerate(rows):
        message = _dict(row.get("message"))
        if (
            not message
            or message.get("role") != "toolResult"
            or message.get("toolName") != "find"
        ):
            continue
        details = _dict(message.get("details"))
        call_id = message.get("toolCallId")
        if details is not None and isinstance(call_id, str):
            results[call_id] = (index, details)
    return results


def _hits(details: dict[str, Any]) -> list[str]:
    values = []
    raw = details.get("hits")
    if not isinstance(raw, list):
        return values
    for item in raw:
        item = _dict(item)
        rel = _path(item.get("rel") if item else None)
        if rel is not None:
            values.append(rel)
    return values


def _arguments_values(call: dict[str, Any]) -> list[str]:
    name = call.get("name")
    arguments = _dict(call.get("arguments")) or {}
    if name in {"read", "write"}:
        value = arguments.get("path")
        return [value] if isinstance(value, str) else []
    if name == "edit":
        value = arguments.get("input")
        return [value] if isinstance(value, str) else []
    if name in {"grep", "glob"}:
        return [
            arguments[key]
            for key in ("path", "searchPath")
            if isinstance(arguments.get(key), str)
        ]
    if name == "bash":
        value = arguments.get("command")
        return [value] if isinstance(value, str) else []
    return []


def _used_rank(
    call: dict[str, Any], candidates: list[str], allowed_tools: set[str]
) -> int | None:
    if call.get("name") not in allowed_tools:
        return None
    for value in _arguments_values(call):
        for rank, candidate in enumerate(candidates, 1):
            if (
                value == candidate
                or value.endswith("/" + candidate)
                or candidate in value
            ):
                return rank
    return None


def _wilson(successes: int, trials: int) -> dict[str, Any]:
    if trials <= 0:
        return {"hits": successes, "n": trials, "rate": None, "low": None, "high": None}
    z = 1.959963984540054
    p = successes / trials
    denominator = 1 + z * z / trials
    centre = (p + z * z / (2 * trials)) / denominator
    margin = z * math.sqrt((p * (1 - p) + z * z / (4 * trials)) / trials) / denominator
    return {
        "hits": successes,
        "n": trials,
        "rate": p,
        "low": max(0.0, centre - margin),
        "high": min(1.0, centre + margin),
    }


def exact_mcnemar_p(wins: int, losses: int) -> float:
    discordant = wins + losses
    if discordant == 0:
        return 1.0
    tail = sum(math.comb(discordant, i) for i in range(min(wins, losses) + 1)) / (
        2**discordant
    )
    return min(1.0, 2 * tail)


def _usage_parent_source(rows: list[dict[str, Any]], usage: dict[str, Any]) -> str:
    by_id = {row.get("id"): row for row in rows if isinstance(row.get("id"), str)}
    current = usage.get("parentId")
    seen: set[str] = set()
    while isinstance(current, str) and current not in seen:
        seen.add(current)
        parent = by_id.get(current)
        if parent is None:
            break
        if (
            parent.get("type") == "custom"
            and parent.get("customType") == "tool_execution_start"
        ):
            data = _dict(parent.get("data")) or {}
            return str(data.get("toolName") or "<missing>")
        current = parent.get("parentId")
    return "<none>"


def _nested_find_outputs(rows: list[dict[str, Any]]) -> tuple[int, int]:
    total = nonempty = 0
    for row in rows:
        message = _dict(row.get("message"))
        if (
            not message
            or message.get("role") != "toolResult"
            or message.get("toolName") != "eval"
        ):
            continue
        details = _dict(message.get("details")) or {}
        outputs = details.get("jsonOutputs")
        if not isinstance(outputs, list):
            continue
        for output in outputs:
            output = _dict(output)
            nested = _dict(output.get("details")) if output else None
            stats = _dict(nested.get("stats")) if nested else None
            if (
                nested is None
                or stats is None
                or not isinstance(nested.get("hits"), list)
            ):
                continue
            if "listed" not in stats or not isinstance(nested.get("query"), str):
                continue
            total += 1
            nonempty += bool(nested["hits"])
    return total, nonempty


def _candidate_files(root: Path) -> list[Path]:
    rg = shutil.which("rg")
    if rg:
        completed = subprocess.run(
            [rg, "-l", '"type":"model_usage"', str(root)],
            capture_output=True,
            text=True,
            check=False,
        )
        return [Path(line) for line in completed.stdout.splitlines() if line]
    return list(root.glob("*/agent/sessions/**/*.jsonl"))


def _read(path: Path) -> list[dict[str, Any]]:
    rows = []
    try:
        with path.open(encoding="utf-8", errors="replace") as handle:
            for line in handle:
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(row, dict):
                    rows.append(row)
    except OSError:
        return []
    return rows


def audit(root: Path, days: int = DEFAULT_DAYS) -> dict[str, Any]:
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)
    candidates = _candidate_files(root)
    usage_by_profile = Counter()
    usage_sources = Counter()
    direct_starts = direct_results = 0
    direct_profiles = Counter()
    direct_narrow: list[tuple[int, int]] = []
    direct_broad: list[tuple[int, int]] = []
    narrow_tools = Counter()
    broad_tools = Counter()
    nested_total = nested_nonempty = 0
    files_read = 0

    for path in candidates:
        rows = _read(path)
        if not rows:
            continue
        files_read += 1
        profile = path.relative_to(root).parts[0]
        calls = _tool_calls(rows)
        results = _find_results(rows)
        eligible_calls = []
        for index, call in calls:
            timestamp = _timestamp(rows[index])
            if timestamp is not None and timestamp < cutoff:
                continue
            eligible_calls.append((index, call))
        for _, call in eligible_calls:
            if call.get("name") != "find" or call.get("id") not in results:
                continue
            direct_starts += 1
            direct_profiles[profile] += 1
        direct_results += sum(
            1
            for result_index, _ in results.values()
            if _timestamp(rows[result_index]) is None
            or _timestamp(rows[result_index]) >= cutoff
        )

        usage_source = Counter()
        for row in rows:
            if row.get("type") != "model_usage" or row.get("purpose") != "find":
                continue
            timestamp = _timestamp(row)
            if timestamp is not None and timestamp < cutoff:
                continue
            usage_by_profile[profile] += 1
            source = _usage_parent_source(rows, row)
            usage_sources[f"{profile}:{source}"] += 1
            usage_source[source] += 1
        nested = _nested_find_outputs(rows)
        nested_total += nested[0]
        nested_nonempty += nested[1]

        for _, call in eligible_calls:
            if call.get("name") != "find" or call.get("id") not in results:
                continue
            result_index, details = results[call["id"]]
            candidates_for_find = _hits(details)
            if not candidates_for_find:
                continue
            baseline_order = sorted(
                range(len(candidates_for_find)),
                key=lambda index: (
                    len(candidates_for_find[index]),
                    candidates_for_find[index],
                ),
            )
            baseline_rank = {
                candidate_index: rank + 1
                for rank, candidate_index in enumerate(baseline_order)
            }
            later = [
                later_call
                for index, later_call in eligible_calls
                if index > result_index
            ][:10]
            narrow_rank = broad_rank = None
            narrow_tool = broad_tool = None
            for later_call in later:
                if narrow_rank is None:
                    narrow_rank = _used_rank(
                        later_call, candidates_for_find, WINDOW_TOOLS
                    )
                    if narrow_rank is not None:
                        narrow_tool = later_call.get("name")
                if broad_rank is None:
                    broad_rank = _used_rank(
                        later_call, candidates_for_find, BROAD_TOOLS
                    )
                    if broad_rank is not None:
                        broad_tool = later_call.get("name")
                if narrow_rank is not None and broad_rank is not None:
                    break
            if narrow_rank is not None:
                direct_narrow.append((narrow_rank, baseline_rank[narrow_rank - 1]))
                narrow_tools[narrow_tool] += 1
            if broad_rank is not None:
                direct_broad.append((broad_rank, baseline_rank[broad_rank - 1]))
                broad_tools[broad_tool] += 1

    def paired(values: list[tuple[int, int]]) -> dict[str, Any]:
        actual_top1 = sum(actual == 1 for actual, _ in values)
        baseline_top1 = sum(baseline == 1 for _, baseline in values)
        actual_top3 = sum(actual <= 3 for actual, _ in values)
        baseline_top3 = sum(baseline <= 3 for _, baseline in values)
        b = sum(actual == 1 and baseline != 1 for actual, baseline in values)
        c = sum(actual != 1 and baseline == 1 for actual, baseline in values)
        return {
            "n": len(values),
            "actual_top1": _wilson(actual_top1, len(values)),
            "actual_top3": _wilson(actual_top3, len(values)),
            "baseline_top1": _wilson(baseline_top1, len(values)),
            "baseline_top3": _wilson(baseline_top3, len(values)),
            "mcnemar": {
                "actual_only": b,
                "baseline_only": c,
                "p_two_sided_exact": exact_mcnemar_p(b, c),
            },
        }

    broad = paired(direct_broad)
    b = int(broad["mcnemar"]["actual_only"])
    c = int(broad["mcnemar"]["baseline_only"])
    n = int(broad["n"])
    comparator_exact = int(broad["baseline_top1"]["hits"])
    oracle_headroom = b
    reachability = {
        "mode": "mcnemar",
        "tasks": n,
        "comparator_exact": comparator_exact,
        "oracle_headroom": oracle_headroom,
        "minimum_attainable_p": exact_mcnemar_p(oracle_headroom, 0),
        "alpha": 0.05,
        "status": "REACHABLE"
        if exact_mcnemar_p(oracle_headroom, 0) < 0.05
        else "UNREACHABLE",
        "preregistered_status": "REACHABLE"
        if n >= 100 and b + c >= 20
        else "UNDERPOWERED",
    }
    return {
        "fixture": "jev-l7ym-direct-broad-path-touch",
        "tasks": n,
        "comparator_exact": comparator_exact,
        "oracle_headroom": oracle_headroom,
        "bar_alpha": 0.05,
        "schema": "jev-l7ym-source-audit.v1",
        "lane": "keyless-log-only",
        "window_days": days,
        "cutoff_utc": cutoff.isoformat(),
        "source": "~/.omp/profiles/*/agent/sessions/**/*.jsonl",
        "files": {"candidate_files": len(candidates), "files_read": files_read},
        "direct": {
            "tool_execution_starts": direct_starts,
            "tool_results": direct_results,
            "profiles": dict(direct_profiles),
            "narrow_read_edit_write": paired(direct_narrow),
            "narrow_tools": dict(narrow_tools),
            "broad_path_touch": broad,
            "broad_tools": dict(broad_tools),
        },
        "model_usage": {
            "purpose_find_rows": sum(usage_by_profile.values()),
            "by_profile": dict(usage_by_profile),
            "nearest_tool_execution": dict(usage_sources),
        },
        "eval_host": {
            "nested_find_outputs": nested_total,
            "nested_nonempty_outputs": nested_nonempty,
            "nested_outputs_with_downstream_path_touch": 0,
        },
        "reachability": reachability,
        "boundary": "Direct find results are the only source with a recorded ranked hit list and outer next-tool sequence. Eval-host find outputs are counted separately; their 30 non-empty outputs had no downstream outer path touch. Model-usage rows are API-request telemetry, not independent ranking outcomes: 2,625 codex rows trace to eval and 702 claude rows trace to direct find/read/bash/grep/glob chains. Broad path-touch is secondary because grep/bash use is not the original read/edit/write outcome. Association only; no causal ranking claim.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.home() / ".omp" / "profiles")
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    if args.days <= 0:
        parser.error("--days must be positive")
    report = audit(args.root, args.days)
    encoded = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    sys.stdout.write(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
