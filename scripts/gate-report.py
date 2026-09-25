#!/usr/bin/env python3
"""Report joined Jev gate outcomes without printing local session text."""

from __future__ import annotations

import argparse
import json
import glob
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def read_rows(path: Path) -> list[dict[str, Any]]:
    rows = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows


def percentile(values: list[float], p: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = (len(ordered) - 1) * p
    lower = int(index)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = index - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def native_usage_report(sessions_root: Path) -> dict[str, Any]:
    """Aggregate native omp model_usage rows by UTC day and purpose."""
    buckets: dict[str, dict[str, dict[str, Any]]] = {}
    total = 0
    for path in glob.glob(
        str(sessions_root / "**/sessions/**/*.jsonl"), recursive=True
    ):
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
        messages = {
            event.get("id"): event for event in events if event.get("type") == "message"
        }
        for event_index, event in enumerate(events):
            if (
                event.get("type") != "model_usage"
                or event.get("provider") != "typesafe"
            ):
                continue
            stamp = event.get("timestamp")
            if isinstance(stamp, (int, float)):
                stamp_seconds = (
                    float(stamp) / 1000 if stamp > 10_000_000_000 else float(stamp)
                )
                day = (
                    datetime.fromtimestamp(stamp_seconds, timezone.utc)
                    .date()
                    .isoformat()
                )
            elif isinstance(stamp, str):
                try:
                    stamp_seconds = datetime.fromisoformat(
                        stamp.replace("Z", "+00:00")
                    ).timestamp()
                    day = (
                        datetime.fromtimestamp(stamp_seconds, timezone.utc)
                        .date()
                        .isoformat()
                    )
                except ValueError:
                    continue
            else:
                continue
            purpose = str(event.get("purpose") or "unknown")
            bucket = buckets.setdefault(day, {}).setdefault(
                purpose,
                {
                    "calls": 0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "spend_usd": 0.0,
                    "latencies_ms": [],
                },
            )
            usage_raw: Any = event.get("usage")
            usage: dict[str, Any] = usage_raw if isinstance(usage_raw, dict) else {}
            input_raw: Any = usage.get("input")
            output_raw: Any = usage.get("output")
            input_tokens = (
                float(input_raw) if isinstance(input_raw, (int, float)) else 0.0
            )
            output_tokens = (
                float(output_raw) if isinstance(output_raw, (int, float)) else 0.0
            )
            cost: Any = usage.get("cost")
            if isinstance(cost, dict):
                cost = cost.get("total")
            if not isinstance(cost, (int, float)):
                cost = float(input_tokens) * 0.042 / 1_000_000
            latency = None
            parent = messages.get(event.get("parentId"))
            if isinstance(parent, dict) and isinstance(
                parent.get("duration"), (int, float)
            ):
                latency = float(parent["duration"])
            elif (
                isinstance(parent, dict)
                and isinstance(parent.get("timestamp"), (int, float))
                and isinstance(parent.get("completedAt"), (int, float))
            ):
                latency = max(0.0, float(parent["completedAt"] - parent["timestamp"]))
            bucket["calls"] += 1
            if latency is None:
                for follow in events[event_index + 1 :]:
                    follow_message = follow.get("message") or {}
                    if (
                        follow.get("type") != "message"
                        or follow_message.get("role") != "assistant"
                    ):
                        continue
                    if isinstance(follow_message.get("duration"), (int, float)):
                        latency = float(follow_message["duration"])
                    else:
                        follow_stamp = follow.get("timestamp")
                        if isinstance(follow_stamp, str):
                            try:
                                latency = max(
                                    0.0,
                                    (
                                        datetime.fromisoformat(
                                            follow_stamp.replace("Z", "+00:00")
                                        ).timestamp()
                                        - (
                                            stamp_seconds
                                            if isinstance(stamp, (int, float))
                                            else datetime.fromisoformat(
                                                stamp.replace("Z", "+00:00")
                                            ).timestamp()
                                        )
                                    )
                                    * 1000,
                                )
                            except ValueError:
                                pass
                    break
            bucket["input_tokens"] += int(input_tokens)
            bucket["output_tokens"] += int(output_tokens)
            bucket["spend_usd"] += float(cost)
            if latency is not None:
                bucket["latencies_ms"].append(latency)
            total += 1
    days: dict[str, Any] = {}
    for day, purposes in sorted(buckets.items()):
        days[day] = {}
        for purpose, bucket in sorted(purposes.items()):
            latencies = bucket.pop("latencies_ms")
            days[day][purpose] = {
                **bucket,
                "latency_ms": {
                    "p50": percentile(latencies, 0.5),
                    "p95": percentile(latencies, 0.95),
                },
            }
    return {
        "calls": total,
        "days": days,
        "source": "local omp model_usage rows; provider=typesafe",
        "boundary": "Find outcome joins are deferred; this section reports native usage metadata only.",
    }


def report(
    rows: list[dict[str, Any]], sessions_root: Path | None = None
) -> dict[str, Any]:
    scored = [row for row in rows if row.get("status") == "scored"]
    flags = [row for row in scored if row.get("flag") is True]
    latencies = [
        float(row["latencyMs"])
        for row in scored
        if isinstance(row.get("latencyMs"), (int, float))
    ]
    tokens = [row["tokens"] for row in scored if isinstance(row.get("tokens"), dict)]
    input_tokens = sum(float(item.get("input_tokens", 0)) for item in tokens)
    outcomes = {
        label: sum(row.get("outcome") == label for row in rows)
        for label in ("harm-evidence", "no-evidence", "unknown")
    }
    labeled = [
        row for row in scored if row.get("outcome") in {"harm-evidence", "no-evidence"}
    ]
    confusion = {
        "true_positive": sum(
            row.get("flag") is True and row.get("outcome") == "harm-evidence"
            for row in labeled
        ),
        "false_positive": sum(
            row.get("flag") is True and row.get("outcome") == "no-evidence"
            for row in labeled
        ),
        "false_negative": sum(
            row.get("flag") is not True and row.get("outcome") == "harm-evidence"
            for row in labeled
        ),
        "true_negative": sum(
            row.get("flag") is not True and row.get("outcome") == "no-evidence"
            for row in labeled
        ),
    }
    top_flags = [
        {
            "cmdSha": row.get("cmdSha"),
            "cmd": row.get("cmd"),
            "flag": row.get("flag"),
            "outcome": row.get("outcome"),
            "evidence": row.get("evidence", []),
        }
        for row in flags[:10]
    ]
    return {
        "rows": len(rows),
        "scored": len(scored),
        "calls": sum(row.get("status") == "scored" for row in rows),
        "spend_usd_estimate": input_tokens * 0.042 / 1_000_000,
        "input_tokens": input_tokens,
        "latency_ms": {
            "p50": percentile(latencies, 0.50),
            "p95": percentile(latencies, 0.95),
        },
        "flag_rate": (len(flags) / len(scored)) if scored else None,
        "outcomes": outcomes,
        "labeled_rows": len(labeled),
        "confusion": confusion,
        "top_flags": top_flags,
        "boundary": "Session text remains local; cmd is the gate's existing redacted prefix. Unknown outcomes are not imputed.",
        "native_jev": native_usage_report(sessions_root) if sessions_root else None,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("outcomes", type=Path)
    parser.add_argument(
        "--sessions-root", type=Path, default=Path.home() / ".omp/profiles"
    )
    parser.add_argument("--robot", action="store_true")
    args = parser.parse_args(argv)
    result = report(read_rows(args.outcomes), args.sessions_root)
    if args.robot:
        print(json.dumps(result, sort_keys=True))
    else:
        print(
            f"calls={result['calls']} scored={result['scored']} spend_usd=${result['spend_usd_estimate']:.6f}"
        )
        print(
            f"latency_p50_ms={result['latency_ms']['p50']} latency_p95_ms={result['latency_ms']['p95']} flag_rate={result['flag_rate']}"
        )
        print(f"outcomes={result['outcomes']} confusion={result['confusion']}")
        print("top_flags:")
        for row in result["top_flags"]:
            print(
                f"  {row['cmdSha']} {row['cmd']} outcome={row['outcome']} evidence={','.join(row['evidence'])}"
            )
        native = result["native_jev"]
        print("native_jev_model_usage_by_day_purpose:")
        for day, purposes in (native or {}).get("days", {}).items():
            for purpose, values in purposes.items():
                latency = values["latency_ms"]
                print(
                    "  {} purpose={} calls={} spend_usd={:.6f} input={} latency_p50_ms={} latency_p95_ms={}".format(
                        day,
                        purpose,
                        values["calls"],
                        values["spend_usd"],
                        values["input_tokens"],
                        latency["p50"],
                        latency["p95"],
                    )
                )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
