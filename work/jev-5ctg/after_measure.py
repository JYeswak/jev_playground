#!/usr/bin/env python3
"""Recompute post-cap operational metrics from privacy-safe local JSONL logs."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

DEPLOYED_AT = datetime(2026, 10, 2, 3, 44, 26, tzinfo=timezone.utc)
JEV_INPUT_USD_PER_MILLION = 0.042
SAVED_INPUT_USD_PER_MILLION = 3.0
INJECTION_BASELINE_CAP_ROWS_7D = 7567
INJECTION_CAP_SCHEMAS = frozenset({"jev-injection-shadow.v2", "jev-injection-shadow.v3"})
INJECTION_COHORT_SCHEMA = "jev-injection-shadow.v3"
LEGACY_DAILY_CAP = 100
MEMORY_BASELINE = {
    "scored": 1630,
    "daily_cap": 5243,
    "memo": 1580,
    "tokens_saved": 59522,
    "scored_input_tokens": 760036,
}
MIN_INJECTION_CAP_REDUCTION = 0.90
MIN_MEMORY_VALUE_RATIO = 3.0


def iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def parse_ts(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def wilson(successes: int, trials: int, z: float = 1.959963984540054) -> dict[str, float] | None:
    if trials <= 0:
        return None
    if not 0 <= successes <= trials:
        raise ValueError("successes must be in [0, trials]")
    p = successes / trials
    z2 = z * z
    denominator = 1 + z2 / trials
    center = (p + z2 / (2 * trials)) / denominator
    half = z * math.sqrt(p * (1 - p) / trials + z2 / (4 * trials * trials)) / denominator
    return {"low": max(0.0, center - half), "high": min(1.0, center + half)}


def load_log(path: Path, now: datetime, window_start: datetime) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    digest = hashlib.sha256()
    rows: list[dict[str, Any]] = []
    malformed = 0
    first: datetime | None = None
    last: datetime | None = None
    first_scoped_v3: datetime | None = None
    total = 0
    with path.open("rb") as stream:
        for raw in stream:
            digest.update(raw)
            if not raw.strip():
                continue
            total += 1
            try:
                row = json.loads(raw)
            except (json.JSONDecodeError, UnicodeDecodeError):
                malformed += 1
                continue
            if not isinstance(row, dict):
                malformed += 1
                continue
            timestamp = parse_ts(row.get("ts"))
            if timestamp is None:
                malformed += 1
                continue
            first = timestamp if first is None or timestamp < first else first
            last = timestamp if last is None or timestamp > last else last
            if (
                row.get("schema") == INJECTION_COHORT_SCHEMA
                and isinstance(row.get("capScopeId"), str)
                and row["capScopeId"]
                and timestamp <= now
            ):
                first_scoped_v3 = timestamp if first_scoped_v3 is None or timestamp < first_scoped_v3 else first_scoped_v3
            if window_start <= timestamp <= now:
                row["_ts"] = timestamp
                rows.append(row)
    return rows, {
        "path": str(path),
        "sha256": digest.hexdigest(),
        "rows": total,
        "malformed": malformed,
        "first_ts": iso(first) if first else None,
        "last_ts": iso(last) if last else None,
        "first_scoped_v3_ts": iso(first_scoped_v3) if first_scoped_v3 else None,
    }


def recorded_input_tokens(rows: list[dict[str, Any]], token_getter) -> tuple[int, int]:
    tokens = 0
    missing = 0
    for row in rows:
        value = token_getter(row)
        if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
            tokens += value
        else:
            missing += 1
    return tokens, missing


def cap_reduction(cap_rows: int, days: float, complete: bool) -> dict[str, Any]:
    baseline_per_day = INJECTION_BASELINE_CAP_ROWS_7D / 7
    observed_per_day = cap_rows / days if days > 0 else None
    reduction = 1 - observed_per_day / baseline_per_day if observed_per_day is not None else None
    status = "PENDING" if not complete else "PASS" if reduction is not None and reduction >= MIN_INJECTION_CAP_REDUCTION else "FAIL"
    return {
        "status": status,
        "baseline_cap_rows_per_day": baseline_per_day,
        "observed_cap_rows": cap_rows,
        "observed_cap_rows_per_day": observed_per_day,
        "reduction": reduction,
        "required_reduction": MIN_INJECTION_CAP_REDUCTION,
        "window_complete": complete,
    }


def memory_value(tokens_saved: int, scored_input_tokens: int) -> dict[str, Any]:
    savings = Decimal(tokens_saved) * Decimal(str(SAVED_INPUT_USD_PER_MILLION)) / Decimal(1_000_000)
    spend = Decimal(scored_input_tokens) * Decimal(str(JEV_INPUT_USD_PER_MILLION)) / Decimal(1_000_000)
    ratio = float(savings / spend) if spend > 0 else None
    savings_usd = float(savings)
    spend_usd = float(spend)
    return {
        "tokens_saved": tokens_saved,
        "saved_value_usd": savings_usd,
        "scored_input_tokens": scored_input_tokens,
        "jev_spend_usd": spend_usd,
        "value_per_spend": ratio,
    }


def assess_memory_share(scored: int, cap: int, memo: int, complete: bool) -> dict[str, Any]:
    denominator = scored + cap + memo
    share = scored / denominator if denominator else None
    baseline_denominator = sum(MEMORY_BASELINE[k] for k in ("scored", "daily_cap", "memo"))
    baseline_share = MEMORY_BASELINE["scored"] / baseline_denominator
    status = "PENDING" if not complete else "PASS" if share is not None and share > baseline_share else "FAIL"
    return {
        "status": status,
        "scored": scored,
        "daily_cap": cap,
        "memo": memo,
        "denominator": denominator,
        "scored_share": share,
        "baseline_scored_share": baseline_share,
        "required": "greater than frozen baseline",
        "window_complete": complete,
    }


def assess_value(metrics: dict[str, Any], complete: bool) -> dict[str, Any]:
    ratio = metrics["value_per_spend"]
    status = "PENDING" if not complete else "PASS" if ratio is not None and ratio >= MIN_MEMORY_VALUE_RATIO else "FAIL"
    return {"status": status, **metrics, "minimum_value_per_spend": MIN_MEMORY_VALUE_RATIO, "window_complete": complete}


def assess_newly_covered(
    rows: list[dict[str, Any]], now: datetime, first_telemetry_at: datetime | None
) -> dict[str, Any]:
    telemetry = [
        row for row in rows
        if row.get("schema") == INJECTION_COHORT_SCHEMA
        and isinstance(row.get("capScopeId"), str)
        and row["capScopeId"]
    ]
    if not telemetry:
        return {
            "status": "UNMEASURABLE",
            "rate": None,
            "wilson_95": None,
            "window_start": None,
            "window_days": 0.0,
            "window_complete": False,
            "eligible_scored_rows": 0,
            "explicit_withheld_rows": 0,
            "cap_scopes": 0,
            "reason": "No v3 records with cap-scope identity are present.",
        }

    window_start = first_telemetry_at or min(row["_ts"] for row in telemetry)
    window_days = max(0.0, (now - window_start).total_seconds() / 86400)
    window_complete = now >= window_start + timedelta(days=7)
    eligible = [
        row for row in telemetry
        if row.get("status") == "scored"
        and type(row.get("dailyCallOrdinal")) is int
        and row["dailyCallOrdinal"] > LEGACY_DAILY_CAP
    ]
    withheld = sum(row.get("withheld") is True for row in eligible)
    if not window_complete:
        status = "PENDING"
        reason = "Seven days of v3 cap-scope observations have not elapsed."
    elif not eligible:
        status = "UNMEASURABLE"
        reason = "No scored calls beyond the old 100-call daily cap were observed."
    else:
        status = "MEASURED"
        reason = None
    return {
        "status": status,
        "rate": withheld / len(eligible) if eligible else None,
        "wilson_95": wilson(withheld, len(eligible)),
        "window_start": iso(window_start),
        "window_days": window_days,
        "window_complete": window_complete,
        "eligible_scored_rows": len(eligible),
        "explicit_withheld_rows": withheld,
        "cap_scopes": len({row["capScopeId"] for row in telemetry}),
        "reason": reason,
    }


def build_report(log_dir: Path, now: datetime) -> dict[str, Any]:
    now = now.astimezone(timezone.utc)
    start_24h = now - timedelta(hours=24)
    start_7d = now - timedelta(days=7)
    post_start = max(start_7d, DEPLOYED_AT)
    post_days = max(0.0, (now - post_start).total_seconds() / 86400)
    post_window_complete = now >= DEPLOYED_AT + timedelta(days=7)
    injection, injection_source = load_log(log_dir / "injection-shadow.jsonl", now, start_7d)
    memory, memory_source = load_log(log_dir / "memory-filter.jsonl", now, start_7d)
    sources = {"injection": injection_source, "memory": memory_source}

    injection_24h = [r for r in injection if r["_ts"] >= start_24h]
    injection_7d = injection
    injection_post = [r for r in injection if r["_ts"] >= post_start]
    mem_24h = [r for r in memory if r["_ts"] >= start_24h]
    mem_post = [r for r in memory if r["_ts"] >= post_start]

    def injection_counts(rows: list[dict[str, Any]]) -> dict[str, Any]:
        counts = Counter(r.get("status", "unknown") for r in rows)
        by_schema: dict[str, dict[str, int]] = {}
        for schema in sorted({str(r.get("schema", "unknown")) for r in rows}):
            by_schema[schema] = dict(Counter(r.get("status", "unknown") for r in rows if str(r.get("schema", "unknown")) == schema))
        scored = [r for r in rows if r.get("status") == "scored"]
        input_tokens, missing = recorded_input_tokens(scored, lambda r: (r.get("tokens") or {}).get("input_tokens") if isinstance(r.get("tokens"), dict) else None)
        return {
            "rows": len(rows),
            "statuses": dict(counts),
            "statuses_by_schema": by_schema,
            "scored_rows": len(scored),
            "scored_input_tokens": input_tokens,
            "scored_rows_missing_input_usage": missing,
            "recorded_spend_usd": input_tokens * JEV_INPUT_USD_PER_MILLION / 1_000_000,
            "scored_flags": sum(r.get("flag") is True for r in scored),
            "scored_flag_rate_wilson": wilson(sum(r.get("flag") is True for r in scored), len(scored)),
            "explicit_withheld_rate": sum(r.get("withheld") is True for r in scored) / len(scored) if scored else None,
            "explicit_withheld_rate_wilson": wilson(sum(r.get("withheld") is True for r in scored), len(scored)),
            "explicit_withheld_rows": sum(r.get("withheld") is True for r in scored),
            "scored_rows_without_withheld_field": sum("withheld" not in r for r in scored),
        }

    injection_current = [r for r in injection_post if r.get("schema") in INJECTION_CAP_SCHEMAS]
    current_scored = [r for r in injection_current if r.get("status") == "scored"]
    flagged = sum(r.get("flag") is True for r in current_scored)
    newly_covered = assess_newly_covered(
        injection_post, now, parse_ts(injection_source.get("first_scoped_v3_ts"))
    )
    injection_cap_bar = cap_reduction(
        sum(r.get("status") == "cap" for r in injection_current), post_days, post_window_complete
    )
    injection_cap_bar["current_schema_cap_rows"] = sum(r.get("status") == "cap" for r in injection_current)
    injection_cap_bar["legacy_schema_cap_rows"] = sum(
        r.get("status") == "cap" and r.get("schema") not in INJECTION_CAP_SCHEMAS for r in injection_post
    )

    mem_24h_counts = Counter(r.get("status", "unknown") for r in mem_24h)
    mem_post_counts = Counter(r.get("status", "unknown") for r in mem_post)
    saved_rows = [r for r in mem_post if r.get("status") in {"scored", "memo"}]
    tokens_saved = sum(r.get("tokensSaved", 0) for r in saved_rows if isinstance(r.get("tokensSaved", 0), int) and r.get("tokensSaved", 0) >= 0)
    scored_rows = [r for r in mem_post if r.get("status") == "scored"]
    scored_tokens, missing_scored_usage = recorded_input_tokens(scored_rows, lambda r: r.get("inputTokens"))
    memory_24h_scored = [r for r in mem_24h if r.get("status") == "scored"]
    mem_24h_tokens, mem_24h_missing = recorded_input_tokens(memory_24h_scored, lambda r: r.get("inputTokens"))
    current_share = assess_memory_share(
        mem_post_counts.get("scored", 0), mem_post_counts.get("daily-cap", 0), mem_post_counts.get("memo", 0), post_window_complete
    )
    memory_roi = assess_value(memory_value(tokens_saved, scored_tokens), post_window_complete)
    baseline_roi = memory_value(MEMORY_BASELINE["tokens_saved"], MEMORY_BASELINE["scored_input_tokens"])

    required_bars = [injection_cap_bar["status"], current_share["status"], memory_roi["status"]]
    overall_status = (
        "PASS" if all(status == "PASS" for status in required_bars) and newly_covered["status"] == "MEASURED"
        else "INCOMPLETE" if not post_window_complete or newly_covered["status"] == "PENDING"
        else "FAIL" if "FAIL" in required_bars
        else "BLOCKED"
    )
    return {
        "status": overall_status,
        "generated_at": iso(now),
        "deployment_at": iso(DEPLOYED_AT),
        "window_24h": {"start": iso(start_24h), "end": iso(now), "duration_hours": 24},
        "post_change_window": {
            "requested_days": 7,
            "start": iso(post_start),
            "end": iso(now),
            "observed_days": post_days,
            "complete": post_window_complete,
        },
        "sources": sources,
        "injection": {
            "last_24h": injection_counts(injection_24h),
            "trailing_7d": injection_counts(injection_7d),
            "post_change_partial_or_7d": injection_counts(injection_post),
            "cap_row_reduction_bar": injection_cap_bar,
            "newly_covered_withhold_rate": newly_covered,
            "aggregate_post_change_current_schema_flag_rate": flagged / len(current_scored) if current_scored else None,
            "aggregate_post_change_current_schema_flag_wilson_95": wilson(flagged, len(current_scored)),
            "aggregate_post_change_current_schema_scored": len(current_scored),
            "aggregate_post_change_current_schema_explicit_withheld": sum(r.get("withheld") is True for r in current_scored),
            "aggregate_post_change_current_schema_explicit_withheld_rate": (
                sum(r.get("withheld") is True for r in current_scored) / len(current_scored) if current_scored else None
            ),
            "aggregate_post_change_current_schema_explicit_withheld_wilson_95": wilson(
                sum(r.get("withheld") is True for r in current_scored), len(current_scored)
            ),
        },
        "memory": {
            "last_24h": {
                "rows": len(mem_24h),
                "statuses": dict(mem_24h_counts),
                "scored_rows": len(memory_24h_scored),
                "scored_input_tokens": mem_24h_tokens,
                "scored_rows_missing_input_usage": mem_24h_missing,
                "recorded_spend_usd": mem_24h_tokens * JEV_INPUT_USD_PER_MILLION / 1_000_000,
            },
            "post_change_partial_or_7d": {
                "rows": len(mem_post),
                "statuses": dict(mem_post_counts),
                "scored_share_cap_cohort": current_share,
                "value_per_spend": memory_roi,
                "baseline_value_per_spend": baseline_roi,
                "scored_rows_missing_input_usage": missing_scored_usage,
            },
        },
        "bars": {
            "injection_cap_rows_drop_at_least_90_percent_for_7d": injection_cap_bar["status"],
            "newly_covered_withhold_rate_with_wilson": newly_covered["status"],
        },
        "price_assumptions": {
            "jev_input_usd_per_million": JEV_INPUT_USD_PER_MILLION,
            "saved_token_input_usd_per_million": SAVED_INPUT_USD_PER_MILLION,
            "saved_value_rate_source": "Frozen OrangeFrog estimate: 59,522 units ~= $0.18, equivalent to $3 per million.",
            "jev_rate_source": "AGENTS.md: $0.042 per million input tokens; output free.",
        },
        "frozen_baselines": {
            "injection_cap_rows_7d": INJECTION_BASELINE_CAP_ROWS_7D,
            "injection_cap_rows_per_day": INJECTION_BASELINE_CAP_ROWS_7D / 7,
            "memory": MEMORY_BASELINE,
            "memory_scored_share_cap_cohort": MEMORY_BASELINE["scored"] / sum(MEMORY_BASELINE[k] for k in ("scored", "daily_cap", "memo")),
            "memory_value_per_spend": baseline_roi["value_per_spend"],
        },
        "boundary": [
            "The seven-day post-change observation is not complete until seven days after the cap rollout.",
            "Newly covered calls require seven days of v3 records with cap-scope identity and daily call ordinals; only scored calls above ordinal 100 enter the withhold-rate denominator.",
            "Recorded Jev spend uses logged input tokens from scored rows; missing usage on failures is not imputed.",
            "Memory ROI excludes cap3-pruned rows because those savings are from a separate deterministic cap, not Jev memory filtering.",
        ],
    }


def selftest() -> None:
    def check(condition: bool, case: str) -> None:
        if not condition:
            raise RuntimeError(f"selftest failed: {case}")

    unchanged = cap_reduction(INJECTION_BASELINE_CAP_ROWS_7D, 7, True)
    check(unchanged["status"] == "FAIL" and unchanged["reduction"] == 0, "unchanged cap volume must fail")
    reduced = cap_reduction(0, 7, True)
    check(reduced["status"] == "PASS" and reduced["reduction"] == 1, "90% cap reduction must pass")
    check(cap_reduction(0, 3.5, False)["status"] == "PENDING", "incomplete window must stay pending")
    below_bar = assess_value(memory_value(100, 10000), True)
    check(below_bar["status"] == "FAIL" and below_bar["value_per_spend"] < MIN_MEMORY_VALUE_RATIO, "sub-3x value must fail")
    at_bar = assess_value(memory_value(126, 3000), True)
    check(at_bar["status"] == "PASS", "exact 3x value must pass")
    share = assess_memory_share(0, 1, 0, True)
    check(share["status"] == "FAIL", "share below baseline must fail")
    interval = wilson(0, 10)
    check(interval is not None and interval["low"] == 0, "Wilson lower bound must remain in range")
    cohort_start = datetime(2026, 10, 1, tzinfo=timezone.utc)
    cohort_rows = [
        {"schema": INJECTION_COHORT_SCHEMA, "capScopeId": "scope-a", "dailyCallOrdinal": 100, "status": "scored", "withheld": True, "_ts": cohort_start},
        {"schema": INJECTION_COHORT_SCHEMA, "capScopeId": "scope-a", "dailyCallOrdinal": 101, "status": "scored", "withheld": True, "_ts": cohort_start},
        {"schema": INJECTION_COHORT_SCHEMA, "capScopeId": "scope-a", "dailyCallOrdinal": 102, "status": "scored", "withheld": False, "_ts": cohort_start},
        {"schema": "jev-injection-shadow.v2", "capScopeId": "scope-old", "dailyCallOrdinal": 101, "status": "scored", "withheld": True, "_ts": cohort_start},
        {"schema": INJECTION_COHORT_SCHEMA, "dailyCallOrdinal": 103, "status": "scored", "withheld": True, "_ts": cohort_start},
    ]
    partial = assess_newly_covered(cohort_rows, cohort_start + timedelta(days=6), cohort_start)
    check(partial["status"] == "PENDING" and partial["eligible_scored_rows"] == 2, "new cohort stays pending before seven days")
    complete = assess_newly_covered(cohort_rows, cohort_start + timedelta(days=7), cohort_start)
    check(
        complete["status"] == "MEASURED"
        and complete["eligible_scored_rows"] == 2
        and complete["explicit_withheld_rows"] == 1
        and complete["rate"] == 0.5
        and complete["wilson_95"] is not None,
        "new cohort counts only v3 scored rows above the old cap",
    )
    old_cap_only = assess_newly_covered([cohort_rows[0]], cohort_start + timedelta(days=7), cohort_start)
    check(old_cap_only["status"] == "UNMEASURABLE", "no calls above the old cap stays unmeasurable")
    check(assess_newly_covered([], cohort_start, None)["status"] == "UNMEASURABLE", "no v3 telemetry stays unmeasurable")
    print("PASS: cap bars, new-cohort boundary/window, sub-3x, baseline-share, and Wilson cases")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument("--log-dir", type=Path, default=Path.home() / ".local/state/jev")
    parser.add_argument("--now", help="fixed RFC3339 time for deterministic replay")
    parser.add_argument("--selftest", action="store_true", help="test the frozen bar and negative paths without log access")
    args = parser.parse_args()
    if args.selftest:
        selftest()
        return 0
    now = parse_ts(args.now) if args.now else datetime.now(timezone.utc)
    if now is None:
        parser.error("--now must be an RFC3339 timestamp with timezone")
    try:
        report = build_report(args.log_dir, now)
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "NOT_RUN", "reason": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(report, sort_keys=True, indent=2 if args.json else None))
    return 0 if report["status"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
