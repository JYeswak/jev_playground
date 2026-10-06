from __future__ import annotations

import json
import math
import os
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from core import (
    HOME,
    JEV_INPUT_USD_PER_MILLION,
    LEDGER_HISTORY_PATH,
    MEMORY_LOG,
    ROOT,
    STATE,
    LedgerInputError,
    memory_metrics,
    parse_instant,
    read_jsonl,
)
from policy import screen_rows, strict_failures


def _percentile(values: list[float], fraction: float) -> float | None:
    if not values:
        return None
    return sorted(values)[max(0, math.ceil(fraction * len(values)) - 1)]


def _session_files() -> list[Path]:
    roots = [HOME / ".omp" / "agent" / "sessions"]
    profiles = HOME / ".omp" / "profiles"
    if profiles.is_dir():
        roots.extend(
            path / "agent" / "sessions" for path in profiles.iterdir() if path.is_dir()
        )
    return sorted(
        {file for root in roots if root.is_dir() for file in root.glob("*/*.jsonl")}
    )


def native_usage(
    start: datetime, end: datetime
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, str]]:
    """Read actual model_usage events and their owning session cwd."""
    paths = _session_files()
    if not paths:
        raise LedgerInputError("no local omp session JSONL files are available")
    purposes: dict[str, list[dict[str, Any]]] = {}
    sessions: dict[str, str] = {}
    for path in paths:
        try:
            if path.stat().st_mtime < start.timestamp() - 86400:
                continue
            source = path.open(encoding="utf-8")
        except OSError as exc:
            raise LedgerInputError(f"cannot read session file {path}: {exc}") from exc
        with source:
            for line_number, line in enumerate(source, start=1):
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as exc:
                    if (
                        '"type":"model_usage"' in line
                        or '"type": "model_usage"' in line
                    ):
                        raise LedgerInputError(
                            f"invalid model_usage JSON at {path}:{line_number}"
                        ) from exc
                    continue
                if not isinstance(row, dict):
                    continue
                if row.get("type") == "session":
                    if isinstance(row.get("id"), str) and isinstance(
                        row.get("cwd"), str
                    ):
                        sessions[row["id"]] = row["cwd"]
                    continue
                if row.get("type") != "model_usage":
                    continue
                stamp = parse_instant(row.get("timestamp"))
                purpose = row.get("purpose")
                if start <= stamp < end and isinstance(purpose, str):
                    purposes.setdefault(purpose, []).append(row)
    return purposes, sessions


def _metrics(
    rows: list[dict[str, Any]],
    token_getter: Any,
    latency_getter: Any = None,
) -> dict[str, Any]:
    token_total = 0
    complete = True
    latencies: list[float] = []
    latency_complete = True
    for row in rows:
        value = token_getter(row)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            complete = False
        else:
            token_total += value
        if latency_getter is not None:
            latency = latency_getter(row)
            if (
                isinstance(latency, (int, float))
                and not isinstance(latency, bool)
                and math.isfinite(latency)
                and latency >= 0
            ):
                latencies.append(float(latency))
            else:
                latency_complete = False
    return {
        "calls": len(rows),
        "input_tokens": token_total if complete else None,
        "jev_spend_usd": round(token_total * JEV_INPUT_USD_PER_MILLION / 1_000_000, 12)
        if complete
        else None,
        "latency_ms_p50": _percentile(latencies, 0.50) if latency_complete else None,
        "latency_ms_p95": _percentile(latencies, 0.95) if latency_complete else None,
    }


def _live_state(surface: dict[str, Any]) -> str:
    surface_id = surface["id"]
    if surface_id in ("memory-jev", "memory-cap3"):
        switch = STATE / (
            "memory-filter-enforce" if surface_id == "memory-jev" else "memory-cap3"
        )
        return "on" if switch.exists() else "off"
    if surface_id == "gate-cascade":
        return "off" if (STATE / "cascade-off").exists() else "on"
    if surface_id in ("webscreen", "injection-shadow"):
        return "on" if (ROOT / surface.get("file", "")).is_file() else "unknown"
    if surface_id in ("webscreen-global", "injection-global"):
        hook = HOME / ".omp" / "hooks" / "post" / str(surface.get("hookfile", ""))
        return "on" if hook.is_file() else "off"
    process = surface.get("process")
    if isinstance(process, str):
        try:
            result = subprocess.run(
                ["pgrep", "-f", process],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
                timeout=2,
            )
        except subprocess.TimeoutExpired:
            return "unknown"
        return (
            "on"
            if result.returncode == 0
            else "off"
            if result.returncode == 1
            else "unknown"
        )
    return "unknown"


def _report_row(
    surface: dict[str, Any],
    costs: dict[str, Any],
    *,
    source: str,
    metrics: dict[str, Any] | None,
    live: str,
    reason: str,
    value_measure: Any = None,
    source_rows: int | None = None,
    attribution_errors: list[str] | None = None,
) -> dict[str, Any]:
    cost = costs.get(surface["id"])
    row = {
        "id": surface["id"],
        "name": surface.get("name"),
        "live": live,
        "source": source,
        "source_rows": source_rows,
        "calls": None if metrics is None else metrics["calls"],
        "input_tokens": None if metrics is None else metrics["input_tokens"],
        "jev_spend_usd": None if metrics is None else metrics["jev_spend_usd"],
        "clef_calls": None,
        "latency_ms_p50": None if metrics is None else metrics["latency_ms_p50"],
        "latency_ms_p95": None if metrics is None else metrics["latency_ms_p95"],
        "value_measure": surface.get("saving")
        if value_measure is None
        else value_measure,
        "value_source": surface.get("evidence"),
        "harm_cost_usd_per_prevented_harm": cost.get("usd_per_prevented_harm")
        if isinstance(cost, dict)
        else None,
        "harm_cost_source": cost.get("source") if isinstance(cost, dict) else None,
        "value_usd": None,
        "net_value_usd": None,
        "verdict": "UNMEASURED",
        "reason": reason,
    }
    if attribution_errors:
        row["attribution_errors"] = attribution_errors
    return row


def assemble_report(
    surfaces: list[dict[str, Any]],
    harm_table: dict[str, Any],
    *,
    days: float,
    end: datetime | None = None,
    history: Path = LEDGER_HISTORY_PATH,
    memory_path: Path | None = None,
) -> dict[str, Any]:
    end = (end or datetime.now(timezone.utc)).astimezone(timezone.utc)
    start = end - timedelta(days=days)
    costs = harm_table["surfaces"]
    required_costs = {
        surface["id"]
        for surface in surfaces
        if surface.get("group") in ("hook", "global")
    }
    missing = sorted(required_costs - set(costs))
    if missing:
        raise LedgerInputError(
            f"approved harm-cost table lacks surfaces: {', '.join(missing)}"
        )

    usage, sessions = native_usage(start, end)
    memory_source = memory_path or MEMORY_LOG
    memory = read_jsonl(memory_source, start, end)
    report_rows: list[dict[str, Any]] = []
    for surface in surfaces:
        surface_id = surface["id"]
        live = _live_state(surface)
        if surface.get("group") == "native":
            purpose = str(surface.get("purpose", ""))
            events = usage.get(purpose, [])
            jev_events = [
                event for event in events if event.get("provider") == "typesafe"
            ]
            metrics = _metrics(
                jev_events,
                lambda event: event.get("usage", {}).get("input")
                if isinstance(event.get("usage"), dict)
                else None,
            )
            metrics["clef_calls"] = sum(
                event.get("provider") == "ollama"
                and "clef" in str(event.get("model", "")).casefold()
                for event in events
            )
            reason = (
                "Jev requests are costed; classifier checks and continuation outcomes are unmeasured"
                if surface_id == "smart-stop"
                else "per-purpose model usage is recorded; monetary user value is not"
            )
            row = _report_row(
                surface,
                costs,
                source="omp session model_usage",
                metrics=metrics,
                live=live,
                reason=reason,
                source_rows=len(usage.get(purpose, [])),
            )
            row["clef_calls"] = metrics.get("clef_calls") if metrics else None
            report_rows.append(row)
            continue

        if surface_id in ("memory-jev", "memory-cap3"):
            measured = memory_metrics(memory)
            if surface_id == "memory-jev":
                metrics = {
                    "calls": measured["memory_jev_calls"],
                    "input_tokens": measured["memory_jev_input_tokens"],
                    "jev_spend_usd": measured["memory_jev_spend_usd"],
                    "latency_ms_p50": measured["memory_jev_latency_ms_p50"],
                    "latency_ms_p95": measured["memory_jev_latency_ms_p95"],
                }
                measure = {
                    "tokens_saved": measured["memory_jev_tokens"],
                    "drop_rows": measured["memory_jev_drop_rows"],
                }
                reason = "saved tokens are measured; no approved dollars-per-token conversion exists"
            else:
                count = measured["memory_cap3_rows"]
                metrics = {
                    "calls": count,
                    "input_tokens": 0,
                    "jev_spend_usd": 0.0,
                    "latency_ms_p50": None,
                    "latency_ms_p95": None,
                }
                measure = {
                    "tokens_saved": measured["memory_cap3_tokens"],
                    "rows": count,
                }
                reason = (
                    "cap-3 pruning is local; the X8 avoided-harm value is unavailable"
                )
            report_rows.append(
                _report_row(
                    surface,
                    costs,
                    source=str(memory_source),
                    metrics=metrics,
                    live=live,
                    reason=reason,
                    value_measure=measure,
                    source_rows=len(memory),
                )
            )
            continue

        log_name = surface.get("log")
        if surface_id == "needs-human":
            source_path = STATE / "fleet-needs-human-calls.jsonl"
        elif surface_id in ("webscreen-global", "injection-global"):
            filename = (
                "webscreen-shadow.jsonl"
                if surface_id == "webscreen-global"
                else "injection-shadow.jsonl"
            )
            source_path = STATE / filename
        elif surface_id == "gate-cascade":
            source_path = STATE / "gate-observe.jsonl"
        elif isinstance(log_name, str):
            source_path = STATE / log_name
        else:
            source_path = None
        if source_path is None or not source_path.is_file():
            report_rows.append(
                _report_row(
                    surface,
                    costs,
                    source=str(source_path or "no event log"),
                    metrics=None,
                    live=live,
                    reason="no timestamped per-surface source exists",
                )
            )
            continue
        source_rows = read_jsonl(source_path, start, end)

        if surface_id in (
            "injection-shadow",
            "webscreen",
            "webscreen-global",
            "injection-global",
        ):
            attributed, errors = screen_rows(source_rows, sessions)
            if errors:
                report_rows.append(
                    _report_row(
                        surface,
                        costs,
                        source=str(source_path),
                        metrics=None,
                        live=live,
                        reason="screen events cannot be joined to both repo and session; refusing attribution",
                        source_rows=len(source_rows),
                        attribution_errors=errors,
                    )
                )
            else:
                metrics = _metrics(
                    attributed,
                    lambda item: (
                        item.get("tokens", {}).get(
                            "input_tokens", item.get("tokens", {}).get("input")
                        )
                        if isinstance(item.get("tokens"), dict)
                        else item.get("input_tokens", item.get("inputTokens"))
                    ),
                    lambda item: item.get("latencyMs"),
                )
                report_rows.append(
                    _report_row(
                        surface,
                        costs,
                        source=str(source_path),
                        metrics=metrics,
                        live=live,
                        reason="usage is measured; dollars per prevented harm are not",
                        source_rows=len(source_rows),
                    )
                )
            continue

        if surface_id == "gate-cascade":
            if any("jevSkipped" not in item for item in source_rows):
                metrics = None
                measure = None
                reason = (
                    "gate log lacks a local-clear versus paid-fallback classification"
                )
            else:
                cleared = sum(item.get("jevSkipped") is True for item in source_rows)
                metrics = {
                    "calls": len(source_rows),
                    "input_tokens": None,
                    "jev_spend_usd": None,
                    "latency_ms_p50": None,
                    "latency_ms_p95": None,
                }
                measure = {
                    "screened_locally": cleared,
                    "total_commands": len(source_rows),
                    "free_screen_share": cleared / len(source_rows)
                    if source_rows
                    else None,
                }
                reason = "cascade measures local screening; paid fallback is counted by gate-observe"
            report_rows.append(
                _report_row(
                    surface,
                    costs,
                    source=str(source_path),
                    metrics=metrics,
                    live=live,
                    reason=reason,
                    value_measure=measure,
                    source_rows=len(source_rows),
                )
            )
            continue

        if surface_id == "gate-observe":
            calls = [item for item in source_rows if item.get("jevSkipped") is False]
            metrics = _metrics(
                calls,
                lambda item: item.get("tokens", {}).get("input")
                if isinstance(item.get("tokens"), dict)
                else item.get("input_tokens"),
                lambda item: item.get("latencyMs"),
            )
            report_rows.append(
                _report_row(
                    surface,
                    costs,
                    source=str(source_path),
                    metrics=metrics,
                    live=live,
                    reason="paid fallback usage is counted; prevented-harm value is not measured",
                    source_rows=len(source_rows),
                )
            )
            continue

        if surface_id == "needs-human":
            metrics = _metrics(
                source_rows,
                lambda item: item.get("input_tokens"),
                lambda item: item.get("latencyMs"),
            )
            report_rows.append(
                _report_row(
                    surface,
                    costs,
                    source=str(source_path),
                    metrics=metrics,
                    live=live,
                    reason="Jev call usage is reported; no approved operational-value conversion exists",
                    source_rows=len(source_rows),
                )
            )
            continue

        if surface_id == "vendor-shadow":
            calls = [
                item
                for item in source_rows
                if item.get("status") in ("scored", "called", "ok")
            ]
            metrics = _metrics(
                calls,
                lambda item: item.get("usage", {}).get("input_tokens")
                if isinstance(item.get("usage"), dict)
                else item.get("input_tokens"),
                lambda item: item.get("latencyMs"),
            )
            report_rows.append(
                _report_row(
                    surface,
                    costs,
                    source=str(source_path),
                    metrics=metrics,
                    live=live,
                    reason="logged usage is costed; no committed avoided-harm value is available",
                    source_rows=len(source_rows),
                )
            )
            continue

        report_rows.append(
            _report_row(
                surface,
                costs,
                source=str(source_path),
                metrics=None,
                live=live,
                reason="source schema is not mapped; per-surface usage is not inferred",
                source_rows=len(source_rows),
            )
        )

    failures = strict_failures(surfaces, report_rows)
    if history.is_file():
        previous = read_jsonl(history)
        if previous and end - parse_instant(
            previous[-1].get("generated_at")
        ) > timedelta(days=8):
            failures.append("previous ledger output is older than eight days")
    return {
        "schema": "jev-mvvh.ledger.v1",
        "window": {"start": start.isoformat(), "end": end.isoformat(), "days": days},
        "generated_at": end.isoformat(),
        "harm_costs_sha256": harm_table["_sha256"],
        "rows": report_rows,
        "strict_failures": failures,
    }


def append_history(path: Path, report: dict[str, Any]) -> None:
    data = json.dumps(
        {
            "ts": report["generated_at"],
            "generated_at": report["generated_at"],
            "schema": report["schema"],
            "report": report,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    with path.open("a", encoding="utf-8") as output:
        output.write(data + "\n")
        output.flush()
        os.fsync(output.fileno())


def render_report(report: dict[str, Any]) -> str:
    header = "id\tlive\tcalls\tinput_tokens\tjev_spend_usd\tvalue_usd\tverdict\treason"
    lines = [header]
    for row in report["rows"]:
        values = [
            row[key]
            for key in (
                "id",
                "live",
                "calls",
                "input_tokens",
                "jev_spend_usd",
                "value_usd",
                "verdict",
                "reason",
            )
        ]
        lines.append(
            "\t".join("—" if value is None else str(value) for value in values)
        )
    if report["strict_failures"]:
        lines.append("STRICT FAILURES:")
        lines.extend(f"- {failure}" for failure in report["strict_failures"])
    return "\n".join(lines)
