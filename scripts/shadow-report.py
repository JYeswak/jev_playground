#!/usr/bin/env python3
"""Summarize Jev shadow logs without emitting command or query text."""

from __future__ import annotations

import argparse
import hashlib
import math
from datetime import datetime, timezone
import json
import random
from pathlib import Path
from typing import Any

INPUT_COST_PER_MILLION = 0.042
DEFAULT_GATE_SHADOW = Path.home() / ".local/state/jev/gate-shadow.jsonl"
DEFAULT_GATE_OBSERVE = Path.home() / ".local/state/jev/gate-observe.jsonl"
DEFAULT_WEB_SHADOW = Path.home() / ".local/state/jev/websearch-rerank.jsonl"
DEFAULT_INJECTION_SHADOW = Path.home() / ".local/state/jev/injection-shadow.jsonl"
DEFAULT_WEBSCREEN_SHADOW = Path.home() / ".local/state/jev/webscreen-shadow.jsonl"
WEBSCREEN_TEST_CUTOFF_UTC = "2026-09-27T00:52:00Z"
TEST_CLOCKS = {"2026-09-27T00:00:00.000Z"}


def rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    out: list[dict[str, Any]] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), 1
    ):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number} is not JSON") from exc
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number} is not an object")
        out.append(value)
    return out


def percentile(values: list[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(len(ordered) * fraction))]


def gate_report(
    shadow: list[dict[str, Any]],
    existing: list[dict[str, Any]],
    sample_size: int,
    seed: int,
) -> dict[str, Any]:
    existing_by_sha = {
        row["cmdSha"]: row
        for row in existing
        if isinstance(row.get("cmdSha"), str) and isinstance(row.get("flag"), bool)
    }
    scored = [row for row in shadow if row.get("status") == "scored"]
    matrix = {
        "jev_true_existing_true": 0,
        "jev_true_existing_false": 0,
        "jev_false_existing_true": 0,
        "jev_false_existing_false": 0,
    }
    disagreements: list[dict[str, Any]] = []
    agreements: list[dict[str, Any]] = []
    unmatched = 0
    for row in scored:
        cmd_sha = row.get("cmdSha")
        match = existing_by_sha.get(cmd_sha)
        if match is None:
            unmatched += 1
            continue
        key = f"jev_{'true' if row.get('jevFlag') else 'false'}_existing_{'true' if match['flag'] else 'false'}"
        matrix[key] += 1
        item = {
            "cmdSha": cmd_sha,
            "jevFlag": bool(row.get("jevFlag")),
            "existingFlag": bool(match["flag"]),
        }
        if row.get("jevFlag") != match["flag"]:
            disagreements.append(item)
        else:
            agreements.append(item)
    rng = random.Random(seed)
    rng.shuffle(agreements)
    scored_tokens = [row.get("tokens") or {} for row in scored]
    input_tokens = sum(int(token.get("input_tokens") or 0) for token in scored_tokens)
    output_tokens = sum(int(token.get("output_tokens") or 0) for token in scored_tokens)
    latency = [
        float(row["latencyMs"])
        for row in scored
        if isinstance(row.get("latencyMs"), (int, float))
    ]
    return {
        "shadow_rows": len(shadow),
        "status_counts": {
            status: sum(row.get("status") == status for row in shadow)
            for status in sorted({str(row.get("status")) for row in shadow})
        },
        "scored_rows": len(scored),
        "existing_flag_rows": len(existing_by_sha),
        "joined_rows": sum(matrix.values()),
        "unmatched_scored_rows": unmatched,
        "matrix_2x2": matrix,
        "disagreements": disagreements,
        "agreement_sample": agreements[:sample_size],
        "spend": {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "input_cost_usd": input_tokens * INPUT_COST_PER_MILLION / 1_000_000,
            "output_cost_usd": 0.0,
        },
        "latency_ms": {
            "p50": percentile(latency, 0.50),
            "p95": percentile(latency, 0.95),
            "count": len(latency),
        },
    }


def web_report(web: list[dict[str, Any]]) -> dict[str, Any]:
    answered = [row for row in web if row.get("status") == "answered"]
    return {
        "rows": len(web),
        "status_counts": {
            status: sum(row.get("status") == status for row in web)
            for status in sorted({str(row.get("status")) for row in web})
        },
        "answered": len(answered),
        "pick_equals_rank1": sum(
            row.get("pickIndex") == row.get("providerRank1Index") for row in answered
        ),
        "opened_pick": sum(row.get("openedPick") is True for row in answered),
        "opened_rank1": sum(row.get("openedRank1") is True for row in answered),
        "latency_ms": {
            "p50": percentile(
                [
                    float(row["latencyMs"])
                    for row in answered
                    if isinstance(row.get("latencyMs"), (int, float))
                ],
                0.50,
            ),
            "p95": percentile(
                [
                    float(row["latencyMs"])
                    for row in answered
                    if isinstance(row.get("latencyMs"), (int, float))
                ],
                0.95,
            ),
        },
    }


def injection_report(values: list[dict[str, Any]]) -> dict[str, Any]:
    excluded = [row for row in values if row.get("ts") in TEST_CLOCKS]
    usable = [row for row in values if row.get("ts") not in TEST_CLOCKS]
    scored = [row for row in usable if row.get("status") == "scored"]
    latencies = sorted(
        float(row["latencyMs"])
        for row in scored
        if isinstance(row.get("latencyMs"), (int, float))
    )
    return {
        "rows": len(usable),
        "excluded_test_rows": len(excluded),
        "status_counts": {
            status: sum(row.get("status") == status for row in usable)
            for status in sorted({str(row.get("status")) for row in usable})
        },
        "scored": len(scored),
        "flags": sum(row.get("flag") is True for row in scored),
        "latency_ms": {
            "p50": percentile(latencies, 0.5),
            "p95": percentile(latencies, 0.95),
        },
        "input_tokens": sum(
            int((row.get("tokens") or {}).get("input_tokens") or 0) for row in scored
        ),
    }


def _utc_timestamp(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(
                value[:-1] + "+00:00" if value.endswith("Z") else value
            )
        except ValueError:
            return None
    else:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed.astimezone(timezone.utc)


def _nonnegative_number(value: Any) -> float | None:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return None
    number = float(value)
    if not math.isfinite(number) or number < 0:
        return None
    return number


def _nonnegative_int(value: Any) -> int | None:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        return None
    return value


def webscreen_report(
    values: list[dict[str, Any]],
    as_of: datetime | str | None = None,
) -> dict[str, Any]:
    report_time = (
        _utc_timestamp(as_of) if as_of is not None else datetime.now(timezone.utc)
    )
    if report_time is None:
        raise ValueError("as_of must be a timezone-aware ISO timestamp")
    cutoff = _utc_timestamp(WEBSCREEN_TEST_CUTOFF_UTC)
    if cutoff is None:
        raise RuntimeError("invalid hard-coded webscreen test cutoff")
    eligible: list[tuple[dict[str, Any], datetime]] = []
    excluded_pre_fix = 0
    invalid_timestamp = 0
    for row in values:
        timestamp = _utc_timestamp(row.get("ts"))
        if timestamp is None:
            invalid_timestamp += 1
        elif timestamp < cutoff:
            excluded_pre_fix += 1
        else:
            eligible.append((row, timestamp))
    status_counts: dict[str, int] = {}
    tool_counts: dict[str, int] = {}
    model_counts: dict[str, int] = {}
    for row, _ in eligible:
        status = str(row.get("status") or "missing")
        tool = str(row.get("toolName") or "missing")
        model = str(row.get("model") or "missing")
        status_counts[status] = status_counts.get(status, 0) + 1
        tool_counts[tool] = tool_counts.get(tool, 0) + 1
        model_counts[model] = model_counts.get(model, 0) + 1
    answered = [row for row, _ in eligible if row.get("status") == "ok"]
    metric_rows: list[tuple[int, int]] = []
    invalid_flag_metrics = 0
    latencies: list[float] = []
    scores: list[float] = []
    for row in answered:
        units = _nonnegative_int(row.get("units"))
        flagged = _nonnegative_int(row.get("flagged"))
        if units is None or flagged is None or flagged > units:
            invalid_flag_metrics += 1
        else:
            metric_rows.append((units, flagged))
        latency = _nonnegative_number(row.get("latencyMs"))
        score = _nonnegative_number(row.get("topScore"))
        if latency is not None:
            latencies.append(latency)
        if score is not None:
            scores.append(score)
    input_tokens: list[int] = []
    output_tokens: list[int] = []
    usage_missing_rows = 0
    for row, _ in eligible:
        input_value = _nonnegative_int(row.get("input_tokens"))
        output_value = _nonnegative_int(row.get("output_tokens"))
        if input_value is not None:
            input_tokens.append(input_value)
        if output_value is not None:
            output_tokens.append(output_value)
        if (
            row.get("status") in {"ok", "fail_open", "billing-stop"}
            and input_value is None
        ):
            usage_missing_rows += 1
    answered_units = sum(units for units, _ in metric_rows)
    flagged_units = sum(flagged for _, flagged in metric_rows)
    flagged_rows = sum(flagged > 0 for _, flagged in metric_rows)
    first_event = min((timestamp for _, timestamp in eligible), default=None)
    last_event = max((timestamp for _, timestamp in eligible), default=None)
    event_span_hours = (
        max(0.0, (last_event - first_event).total_seconds() / 3600)
        if first_event is not None and last_event is not None
        else 0.0
    )
    report_age_hours = (
        max(0.0, (report_time - first_event).total_seconds() / 3600)
        if first_event is not None
        else 0.0
    )
    return {
        "rows": len(eligible),
        "excluded_pre_fix_rows": excluded_pre_fix,
        "invalid_timestamp_rows": invalid_timestamp,
        "legacy_test_cutoff_utc": WEBSCREEN_TEST_CUTOFF_UTC,
        "status_counts": dict(sorted(status_counts.items())),
        "tool_counts": dict(sorted(tool_counts.items())),
        "model_counts": dict(sorted(model_counts.items())),
        "answered_rows": len(answered),
        "flag_metric_rows": len(metric_rows),
        "invalid_flag_metric_rows": invalid_flag_metrics,
        "flagged_rows": flagged_rows,
        "flag_rate_per_row": flagged_rows / len(metric_rows) if metric_rows else None,
        "answered_units": answered_units,
        "flagged_units": flagged_units,
        "flag_rate_per_unit": flagged_units / answered_units
        if answered_units
        else None,
        "latency_ms": {
            "p50": percentile(latencies, 0.50),
            "p95": percentile(latencies, 0.95),
            "rows": len(latencies),
        },
        "top_score": {
            "p50": percentile(scores, 0.50),
            "p95": percentile(scores, 0.95),
            "max": max(scores) if scores else None,
            "rows": len(scores),
        },
        "input_tokens": sum(input_tokens),
        "output_tokens": sum(output_tokens),
        "input_cost_usd_known": sum(input_tokens) * INPUT_COST_PER_MILLION / 1_000_000,
        "usage_rows": len(input_tokens),
        "usage_missing_rows": usage_missing_rows,
        "spend_complete": usage_missing_rows == 0,
        "spend_basis": "known input tokens at $0.042/M; Jev output is free; missing usage means total spend is incomplete",
        "first_event_utc": first_event.isoformat().replace("+00:00", "Z")
        if first_event
        else None,
        "last_event_utc": last_event.isoformat().replace("+00:00", "Z")
        if last_event
        else None,
        "reported_at_utc": report_time.isoformat().replace("+00:00", "Z"),
        "window_elapsed_hours": round(event_span_hours, 3),
        "report_age_hours": round(report_age_hours, 3),
        "window_complete_24h": event_span_hours >= 24.0,
        "window_basis": "first-to-last eligible post-fix event span; report age is separate, and neither proves continuous hook uptime",
    }


def build_report(
    shadow_path: Path,
    existing_path: Path,
    web_path: Path,
    injection_path: Path,
    sample_size: int = 20,
    seed: int = 20260927,
    webscreen_path: Path | None = None,
) -> dict[str, Any]:
    webscreen_rows = rows(webscreen_path) if webscreen_path is not None else []
    webscreen = webscreen_report(webscreen_rows)
    webscreen["source_sha256"] = (
        hashlib.sha256(webscreen_path.read_bytes()).hexdigest()
        if webscreen_path is not None and webscreen_path.exists()
        else None
    )
    return {
        "schema": "jev-shadow-report.v1",
        "seed": seed,
        "gate": gate_report(rows(shadow_path), rows(existing_path), sample_size, seed),
        "web_search_rerank": web_report(rows(web_path)),
        "injection_shadow": injection_report(rows(injection_path)),
        "webscreen_shadow": webscreen,
    }


def write_outputs(
    report: dict[str, Any], out_dir: Path, stem: str
) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / f"{stem}.json"
    disagreements_path = out_dir / f"disagreements-{stem.removeprefix('report-')}.jsonl"
    report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    blind = [
        {
            "cmdSha": row["cmdSha"],
            "jevFlag": row["jevFlag"],
            "existingFlag": row["existingFlag"],
        }
        for row in report["gate"]["disagreements"]
    ]
    disagreements_path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in blind),
        encoding="utf-8",
    )
    return report_path, disagreements_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate-shadow", type=Path, default=DEFAULT_GATE_SHADOW)
    parser.add_argument("--gate-observe", type=Path, default=DEFAULT_GATE_OBSERVE)
    parser.add_argument(
        "--webscreen-shadow", type=Path, default=DEFAULT_WEBSCREEN_SHADOW
    )
    parser.add_argument(
        "--injection-shadow", type=Path, default=DEFAULT_INJECTION_SHADOW
    )
    parser.add_argument(
        "--out-dir", type=Path, default=Path("var/agent-tmp/shadow-report")
    )
    parser.add_argument(
        "--snapshot",
        metavar="DATE",
        help="write a deliberate work/jev-5ay4 dated snapshot",
    )
    parser.add_argument("--sample-size", type=int, default=20)
    args = parser.parse_args()
    report = build_report(
        args.gate_shadow,
        args.gate_observe,
        args.web_shadow,
        args.injection_shadow,
        args.sample_size,
        webscreen_path=args.webscreen_shadow,
    )
    if args.snapshot:
        out_dir, stem = Path("work/jev-5ay4"), f"report-{args.snapshot}"
    else:
        out_dir, stem = args.out_dir, "latest"
    report_path, disagreements_path = write_outputs(report, out_dir, stem)
    print(
        json.dumps(
            {
                "report": str(report_path),
                "disagreements": str(disagreements_path),
                "scored": report["gate"]["scored_rows"],
                "answered": report["web_search_rerank"]["answered"],
                "webscreen_rows": report["webscreen_shadow"]["rows"],
                "webscreen_window_complete_24h": report["webscreen_shadow"][
                    "window_complete_24h"
                ],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
