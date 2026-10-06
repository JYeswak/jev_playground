from __future__ import annotations

import json
import math
from collections.abc import Iterable
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
HOME = Path.home()
STATE = HOME / ".local" / "state" / "jev"
EXPECTED_PATH = ROOT / "work" / "jev-inventory" / "expected.json"
HARM_COSTS_PATH = ROOT / "work" / "jev-mvvh" / "harm-costs.json"
LEDGER_HISTORY_PATH = ROOT / "work" / "jev-mvvh" / "ledger-history.jsonl"
MEMORY_LOG = STATE / "memory-filter.jsonl"
JEV_INPUT_USD_PER_MILLION = 0.042
MEMORY_SCHEMA = "jev-memory-filter.v1"


class LedgerInputError(ValueError):
    """Input data is incomplete, malformed, or not independently attributable."""


def parse_instant(value: object) -> datetime:
    if not isinstance(value, str):
        raise LedgerInputError("timestamp must be a string")
    try:
        instant = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise LedgerInputError(f"invalid timestamp: {value!r}") from exc
    if instant.tzinfo is None or instant.utcoffset() is None:
        raise LedgerInputError(f"timestamp lacks timezone: {value!r}")
    return instant.astimezone(timezone.utc)


def read_jsonl(
    path: Path, start: datetime | None = None, end: datetime | None = None
) -> list[dict[str, Any]]:
    """Read strict JSONL; a missing or malformed required source never means zero."""
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as source:
        for line_number, line in enumerate(source, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise LedgerInputError(f"invalid JSON in {path}:{line_number}") from exc
            if not isinstance(row, dict):
                raise LedgerInputError(f"expected object in {path}:{line_number}")
            stamp_value = row.get("ts", row.get("timestamp"))
            if stamp_value is None:
                raise LedgerInputError(f"missing timestamp in {path}:{line_number}")
            stamp = parse_instant(stamp_value)
            if start is not None and stamp < start:
                continue
            if end is not None and stamp >= end:
                continue
            rows.append(row)
    return rows


def _tokens(row: dict[str, Any], path: str) -> int:
    value = row.get("tokensSaved")
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise LedgerInputError(f"invalid tokensSaved in {path}")
    return value


def _percentile(values: list[float], percentile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    return ordered[max(0, math.ceil(percentile * len(ordered)) - 1)]


def _sum_by_repo(rows: Iterable[dict[str, Any]]) -> tuple[dict[str, int], bool]:
    totals: dict[str, int] = {}
    complete = True
    for row in rows:
        repo = row.get("repo")
        if not isinstance(repo, str) or not repo.strip():
            complete = False
            continue
        totals[repo] = totals.get(repo, 0) + _tokens(row, "memory-filter.jsonl")
    return dict(sorted(totals.items())), complete


def memory_metrics(rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Count Jev drops only on enforced turns; report cap-3 and API usage separately."""
    materialized = list(rows)
    enforced: set[tuple[str, str]] = set()
    for row in materialized:
        if row.get("schema") != MEMORY_SCHEMA:
            raise LedgerInputError("memory row has an unknown schema")
        if row.get("status") == "enforced":
            instance = row.get("instance")
            prompt_hash = row.get("promptHash")
            if not isinstance(instance, str) or not instance:
                raise LedgerInputError("enforced row lacks instance")
            if not isinstance(prompt_hash, str) or not prompt_hash:
                raise LedgerInputError("enforced row lacks promptHash")
            enforced.add((instance, prompt_hash))

    jev_drop_rows = [
        row
        for row in materialized
        if row.get("status") in ("scored", "memo")
        and row.get("decision") == "drop"
        and (row.get("instance"), row.get("promptHash")) in enforced
    ]
    cap3_rows = [row for row in materialized if row.get("status") == "cap3-pruned"]
    request_rows = [
        row for row in materialized if row.get("status") in ("scored", "late-ignored")
    ]
    input_tokens = 0
    input_tokens_complete = True
    latencies: list[float] = []
    latency_complete = True
    for row in request_rows:
        tokens = row.get("inputTokens")
        if isinstance(tokens, bool) or not isinstance(tokens, int) or tokens < 0:
            input_tokens_complete = False
        else:
            input_tokens += tokens
        latency = row.get("latencyMs")
        if (
            isinstance(latency, bool)
            or not isinstance(latency, (int, float))
            or not math.isfinite(latency)
            or latency < 0
        ):
            latency_complete = False
        else:
            latencies.append(float(latency))
    jev_by_repo, jev_repo_complete = _sum_by_repo(jev_drop_rows)
    cap3_by_repo, cap3_repo_complete = _sum_by_repo(cap3_rows)
    jev_tokens = sum(_tokens(row, "memory-filter.jsonl") for row in jev_drop_rows)
    cap3_tokens = sum(_tokens(row, "memory-filter.jsonl") for row in cap3_rows)
    return {
        "memory_jev_tokens": jev_tokens,
        "memory_jev_drop_rows": len(jev_drop_rows),
        "memory_jev_tokens_by_repo": jev_by_repo,
        "memory_jev_repo_complete": jev_repo_complete,
        "memory_cap3_tokens": cap3_tokens,
        "memory_cap3_rows": len(cap3_rows),
        "memory_cap3_tokens_by_repo": cap3_by_repo,
        "memory_cap3_repo_complete": cap3_repo_complete,
        "memory_jev_calls": len(request_rows),
        "memory_jev_input_tokens": input_tokens if input_tokens_complete else None,
        "memory_jev_spend_usd": (
            float(Decimal(input_tokens) * Decimal("0.042") / Decimal(1_000_000))
            if input_tokens_complete
            else None
        ),
        "memory_jev_usage_complete": input_tokens_complete,
        "memory_jev_latency_ms_p50": (
            _percentile(latencies, 0.50) if latency_complete else None
        ),
        "memory_jev_latency_ms_p95": (
            _percentile(latencies, 0.95) if latency_complete else None
        ),
        "memory_jev_latency_complete": latency_complete,
    }
