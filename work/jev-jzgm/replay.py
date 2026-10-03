#!/usr/bin/env python3
"""Read-only replay of recorded memory-filter and gate-cascade decisions."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from cap3_reference import cap3_reference_report, cap3_turn_rows

HOME = Path.home()
STATE = HOME / ".local/state/jev"
ROOT = Path(__file__).resolve().parents[2]
BANK = ROOT / "work/jev-i20b/n60-rows.json"
Row = dict[str, Any]


def parse_time(value: str | None) -> dt.datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(dt.timezone.utc)


def load_jsonl(path: Path) -> tuple[list[Row], int, str]:
    rows = []
    malformed = 0
    try:
        with path.open(encoding="utf-8") as stream:
            for line in stream:
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    malformed += 1
                    continue
                if isinstance(row, dict):
                    rows.append(row)
                else:
                    malformed += 1
    except FileNotFoundError:
        return [], 0, "missing"
    return rows, malformed, "read"


def in_window(row: Row, start: dt.datetime, end: dt.datetime) -> bool:
    stamp = parse_time(row.get("ts"))
    return stamp is not None and start <= stamp < end


def coverage(rows: list[Row]) -> dict[str, Any]:
    stamps = [parse_time(row.get("ts")) for row in rows]
    stamps = [stamp for stamp in stamps if stamp is not None]
    if not stamps:
        return {"first": None, "last": None, "rows": 0}
    return {
        "first": min(stamps).isoformat(),
        "last": max(stamps).isoformat(),
        "rows": len(stamps),
    }


def wilson(successes: int, total: int) -> list[float] | None:
    if total == 0:
        return None
    z = 1.959963984540054
    p = successes / total
    den = 1 + z * z / total
    center = (p + z * z / (2 * total)) / den
    margin = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / den
    return [center - margin, center + margin]


def read_main_memory(
    path: Path, start: dt.datetime, end: dt.datetime
) -> dict[str, Any]:
    all_rows, malformed, source = load_jsonl(path)
    rows = [r for r in all_rows if in_window(r, start, end)]
    latency_sum = latency_n = 0
    for row in rows:
        latency = row.get("latencyMs")
        if isinstance(latency, (int, float)) and latency >= 0:
            latency_sum += latency
            latency_n += 1
    statuses = {
        (r.get("instance"), r.get("promptHash"), r.get("memoryHash")): r.get("status")
        for r in rows
    }
    return {
        "all": all_rows,
        "rows": rows,
        "malformed": malformed,
        "source": source,
        "coverage": coverage(rows),
        "statuses": statuses,
        "observed_latency_ms_sum": latency_sum,
        "observed_latency_rows": latency_n,
    }


def sidecar_memory(
    path: Path, start: dt.datetime, end: dt.datetime
) -> tuple[list[Row], list[Row], int, str]:
    all_rows, malformed, source = load_jsonl(path)
    selected = [r for r in all_rows if in_window(r, start, end)]
    return all_rows, selected, malformed, source


def memory_totals(
    rows: list[Row], statuses: dict[tuple[Any, ...], Any]
) -> tuple[dict[tuple[Any, ...], dict[str, int]], int, int]:
    turns = defaultdict(lambda: {"received": 0, "cut": 0, "items": 0})
    for row in rows:
        item = (row.get("instance"), row.get("promptHash"), row.get("memoryHash"))
        status = statuses.get(item)
        if status is None:
            status = row.get("status")
        memory = row.get("memory", "")
        amount = (
            len(memory.encode("utf-16-le", errors="surrogatepass")) // 8
            if isinstance(memory, str)
            else 0
        )
        turn = turns[item[:2]]
        turn["items"] += 1
        if status in ("enforced", "cap3-pruned") or row.get("decision") == "prune":
            turn["cut"] += amount
        else:
            turn["received"] += amount
    return (
        turns,
        sum(turn["received"] for turn in turns.values()),
        sum(turn["cut"] for turn in turns.values()),
    )


def metric_delta(baseline: float | None, replayed: float | None) -> float | None:
    if baseline == replayed:
        return 0.0
    if (
        isinstance(baseline, (int, float))
        and not isinstance(baseline, bool)
        and isinstance(replayed, (int, float))
        and not isinstance(replayed, bool)
    ):
        return float(replayed - baseline)
    return None


def memory_report(
    main_path: Path,
    sidecar_path: Path,
    bank_path: Path,
    reference_path: Path,
    legacy_reference_path: Path,
    start: dt.datetime,
    end: dt.datetime,
    noop: bool,
) -> dict[str, Any]:
    main = read_main_memory(main_path, start, end)
    _, full_rows, full_bad, _ = sidecar_memory(sidecar_path, start, end)
    turns, total_received, observed_cut = memory_totals(full_rows, main["statuses"])
    observed_turn_rows = cap3_turn_rows(turns)
    policy_off = None
    if noop:
        replayed_turns, replayed_received, replayed_cut = memory_totals(
            [dict(row) for row in full_rows], main["statuses"]
        )
        replayed_latency = sum(
            row["latencyMs"]
            for row in (dict(row) for row in main["rows"])
            if isinstance(row.get("latencyMs"), (int, float)) and row["latencyMs"] >= 0
        )
        baseline = {
            "turns": len(turns),
            "sidecar_items": len(full_rows),
            "received_tokens": total_received,
            "cut_tokens": observed_cut,
            "misses": None,
            "labeled_miss_rows": 0,
            "latency_ms": main["observed_latency_ms_sum"],
        }
        replayed = {
            "turns": len(replayed_turns),
            "sidecar_items": sum(turn["items"] for turn in replayed_turns.values()),
            "received_tokens": replayed_received,
            "cut_tokens": replayed_cut,
            "misses": None,
            "labeled_miss_rows": 0,
            "latency_ms": replayed_latency,
        }
        policy_off = {
            "baseline": baseline,
            "replayed": replayed,
            "misses_status": "unobserved: source logs have no blind harm labels",
            "delta": {
                key: metric_delta(baseline[key], replayed[key])
                for key in (
                    "received_tokens",
                    "cut_tokens",
                    "misses",
                    "latency_ms",
                )
            },
        }
    bank = json.loads(bank_path.read_text(encoding="utf-8"))
    if (
        not isinstance(bank, dict)
        or not isinstance(bank.get("pooled"), dict)
        or not isinstance(bank.get("tokens_per_turn"), dict)
    ):
        raise TypeError("decision bank must contain pooled and tokens_per_turn objects")
    observed = {
        "turns": len(turns),
        "received_tokens": total_received,
        "cut_tokens": observed_cut,
    }
    reference_reports = cap3_reference_report(
        reference_path, legacy_reference_path, observed_turn_rows, start, end
    )
    pooled = bank["pooled"]
    n60 = bank["tokens_per_turn"]
    c3 = n60.get("C3_top3_chars4")
    on = n60.get("ON_8_chars4")
    expected_saved = (
        on - c3
        if isinstance(c3, (int, float)) and isinstance(on, (int, float))
        else None
    )
    n = pooled.get("n")
    c3_pass = pooled.get("c3_pass")
    on_pass = pooled.get("on_pass")
    pass_diff = pooled.get("diff")
    pass_se = pooled.get("se")
    miss_ci = None
    if isinstance(pass_diff, (int, float)) and isinstance(pass_se, (int, float)):
        miss_delta = -pass_diff
        miss_margin = 1.96 * pass_se
        miss_ci = [miss_delta - miss_margin, miss_delta + miss_margin]
    latency = {
        "sum_ms": main["observed_latency_ms_sum"],
        "rows_with_latency": main["observed_latency_rows"],
        "counterfactual_latency": "not identifiable for cap-pruned rows; they have no call latency",
    }
    report = {
        "source": {
            "main": str(main_path),
            "sidecar": str(sidecar_path),
            "decision_bank": str(bank_path),
            "cap3_reference": str(reference_path),
            "legacy_aggregate_reference": str(legacy_reference_path),
        },
        "coverage": {"main": main["coverage"], "sidecar": coverage(full_rows)},
        "valid_window_rows": {
            "main": len(main["rows"]),
            "sidecar": len(full_rows),
            "malformed": main["malformed"] + full_bad,
        },
        "cap3": {
            "observed": {
                **observed,
                "received_tokens_per_turn": total_received / len(turns)
                if turns
                else None,
            },
            **reference_reports,
            "n60_reference": {
                "n": n,
                "on_tokens_per_turn": on,
                "cap3_tokens_per_turn": c3,
                "estimated_savings_per_turn": expected_saved,
                "on_misses": n - on_pass
                if isinstance(n, int) and isinstance(on_pass, int)
                else None,
                "cap3_misses": n - c3_pass
                if isinstance(n, int) and isinstance(c3_pass, int)
                else None,
                "miss_difference_c3_minus_on": (n - c3_pass) - (n - on_pass)
                if isinstance(n, int)
                and isinstance(c3_pass, int)
                and isinstance(on_pass, int)
                else None,
                "miss_difference_rate_c3_minus_on": ((n - c3_pass) - (n - on_pass)) / n
                if isinstance(n, int)
                and n
                and isinstance(c3_pass, int)
                and isinstance(on_pass, int)
                else None,
                "miss_ci95_c3_minus_on": miss_ci,
            },
            "latency": latency,
            "n60_metric_boundary": "The bank's C3/ON token estimates are 3-task calibration applied to 60 fixed tasks; not observed session-token usage.",
        },
    }
    if noop and policy_off is not None:
        report["cap3"]["policy_off"] = policy_off
        report["cap3"]["noop_delta"] = {
            key: (
                metric_delta(
                    policy_off["baseline"]["labeled_miss_rows"],
                    policy_off["replayed"]["labeled_miss_rows"],
                )
                if key == "misses"
                else policy_off["delta"][key]
            )
            for key in (
                "received_tokens",
                "cut_tokens",
                "misses",
                "latency_ms",
            )
        }
    return report


def gate_report(
    path: Path, start: dt.datetime, end: dt.datetime, noop: bool
) -> dict[str, Any]:
    all_rows, malformed, _ = load_jsonl(path)
    rows = [r for r in all_rows if in_window(r, start, end)]
    eligible = [r for r in rows if isinstance(r.get("jevSkipped"), bool)]
    free = sum(r.get("jevSkipped") is True for r in eligible)
    paid = len(eligible) - free
    paid_latency = [
        r["latencyMs"]
        for r in eligible
        if r.get("jevSkipped") is False
        and isinstance(r.get("latencyMs"), (int, float))
        and not isinstance(r.get("latencyMs"), bool)
    ]
    local_latency = [
        r["latencyMs"]
        for r in eligible
        if r.get("jevSkipped") is True
        and isinstance(r.get("latencyMs"), (int, float))
        and not isinstance(r.get("latencyMs"), bool)
    ]
    total = len(eligible)
    share = free / total if total else None
    interval = wilson(free, total)
    result = {
        "source": str(path),
        "window_utc": {
            "from_inclusive": start.isoformat(),
            "to_exclusive": end.isoformat(),
        },
        "coverage": coverage(rows),
        "window_rows": len(rows),
        "rows_without_boolean_screen_outcome": len(rows) - total,
        "eligible_screens": total,
        "free_screens": free,
        "free_screen_share": share,
        "free_screen_wilson95": interval,
        "reference_96pct_in_wilson95": interval is not None
        and interval[0] <= 0.96 <= interval[1],
        "would_reach_paid_jev": paid,
        "misses": None,
        "misses_reason": "gate log has no blind harm labels; screen share is not a miss-rate measure",
        "observed_latency_ms": {
            "paid_result_rows_sum": sum(paid_latency),
            "paid_result_rows_n": len(paid_latency),
            "local_clear_rows_sum": sum(local_latency),
            "local_clear_rows_n": len(local_latency),
            "counterfactual_latency": "not identifiable when local-screen latency or an alternative paid result is absent",
        },
        "malformed": malformed,
    }
    if noop:
        replayed_rows = [dict(row) for row in eligible]
        replayed_total = len(replayed_rows)
        replayed_free = sum(row.get("jevSkipped") is True for row in replayed_rows)
        replayed_share = replayed_free / replayed_total if replayed_total else None
        replayed_paid = replayed_total - replayed_free
        replayed_latency = sum(
            row["latencyMs"]
            for row in replayed_rows
            if isinstance(row.get("latencyMs"), (int, float))
            and not isinstance(row.get("latencyMs"), bool)
        )
        baseline = {
            "eligible_screens": total,
            "free_screens": free,
            "free_screen_share": share,
            "would_reach_paid_jev": paid,
            "misses": None,
            "labeled_miss_rows": 0,
            "latency_ms": sum(paid_latency) + sum(local_latency),
        }
        replayed = {
            "eligible_screens": replayed_total,
            "free_screens": replayed_free,
            "free_screen_share": replayed_share,
            "would_reach_paid_jev": replayed_paid,
            "misses": None,
            "labeled_miss_rows": 0,
            "latency_ms": replayed_latency,
        }
        delta = {
            key: metric_delta(baseline[key], replayed[key])
            for key in (
                "free_screen_share",
                "would_reach_paid_jev",
                "latency_ms",
            )
        }
        delta["misses"] = metric_delta(
            baseline["labeled_miss_rows"], replayed["labeled_miss_rows"]
        )
        result["policy_off"] = {
            "baseline": baseline,
            "replayed": replayed,
            "misses_status": "unobserved: source logs have no blind harm labels",
            "delta": delta,
        }
        result["noop_delta"] = delta
    return result


def event_span(
    coverage_data: dict[str, Any], start: dt.datetime, end: dt.datetime
) -> dict[str, Any]:
    first = parse_time(coverage_data.get("first"))
    last = parse_time(coverage_data.get("last"))
    if first is None or last is None:
        return {"status": "NO_ROWS", "span_days": 0, "covers_requested_bounds": False}
    requested = end - start
    tolerance = min(dt.timedelta(days=1), requested / 10)
    span = last - first
    return {
        "status": "SPANS_REQUESTED_BOUNDS"
        if first <= start + tolerance and last >= end - tolerance
        else "SHORTER_THAN_REQUESTED",
        "span_days": round(span.total_seconds() / 86400, 2),
        "covers_requested_bounds": first <= start + tolerance
        and last >= end - tolerance,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Replay logged Jev policies over a bounded UTC window; no API calls or writes."
    )
    parser.add_argument(
        "--days", type=int, default=30, help="trailing UTC days; max 30"
    )
    parser.add_argument(
        "--from",
        dest="from_ts",
        help="inclusive UTC start (ISO-8601); overrides --days",
    )
    parser.add_argument(
        "--to", dest="to_ts", help="exclusive UTC end (ISO-8601); defaults to now"
    )
    parser.add_argument(
        "--gate-from",
        help="inclusive UTC gate start; must be paired with --gate-to for a custom interval",
    )
    parser.add_argument(
        "--gate-to",
        help="exclusive UTC gate end; defaults to the last completed UTC hour",
    )
    parser.add_argument("--policy", choices=("cap3", "noop"), default="cap3")
    parser.add_argument(
        "--memory-cap",
        type=int,
        default=3,
        help="cap to replay; only logged cap 3 is identifiable",
    )
    parser.add_argument(
        "--memory-log", type=Path, default=STATE / "memory-filter.jsonl"
    )
    parser.add_argument(
        "--memory-sidecar", type=Path, default=STATE / "memory-filter-full.jsonl"
    )
    parser.add_argument("--gate-log", type=Path, default=STATE / "gate-observe.jsonl")
    parser.add_argument("--decision-bank", type=Path, default=BANK)
    parser.add_argument(
        "--memory-reference",
        type=Path,
        default=ROOT / "work/jev-jzgm/cap3-reference.json",
    )
    parser.add_argument(
        "--legacy-memory-reference",
        type=Path,
        default=ROOT / "work/jev-i20b/cap3-before.json",
    )
    args = parser.parse_args()
    if args.days < 1 or args.days > 30:
        parser.error("--days must be between 1 and 30")
    if args.memory_cap != 3:
        parser.error(
            "only --memory-cap 3 is supported; other caps lack recorded rank/order evidence"
        )
    if bool(args.gate_from) != bool(args.gate_to):
        parser.error("--gate-from and --gate-to must be supplied together")
    end = parse_time(args.to_ts) if args.to_ts else dt.datetime.now(dt.timezone.utc)
    start = (
        parse_time(args.from_ts) if args.from_ts else end - dt.timedelta(days=args.days)
    )
    if args.gate_from:
        gate_start = parse_time(args.gate_from)
        gate_end = parse_time(args.gate_to)
    else:
        gate_end = end.replace(minute=0, second=0, microsecond=0)
        gate_start = gate_end - dt.timedelta(hours=1)
    if start is None or end is None or gate_start is None or gate_end is None:
        parser.error("window bounds must be valid timezone-aware ISO timestamps")
    if start >= end or gate_start >= gate_end:
        parser.error("window start must precede window end")
    if max(end - start, gate_end - gate_start) > dt.timedelta(days=30):
        parser.error("requested replay window exceeds 30 days")
    try:
        noop = args.policy == "noop"
        memory = memory_report(
            args.memory_log,
            args.memory_sidecar,
            args.decision_bank,
            args.memory_reference,
            args.legacy_memory_reference,
            start,
            end,
            noop,
        )
        gate = gate_report(args.gate_log, gate_start, gate_end, noop)
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        print(
            json.dumps({"status": "INPUT_ERROR", "error": str(exc)[:160]}),
            file=sys.stderr,
        )
        return 2
    coverage_report = {
        "memory_main": event_span(memory["coverage"]["main"], start, end),
        "memory_sidecar": event_span(memory["coverage"]["sidecar"], start, end),
        "gate": event_span(gate["coverage"], gate_start, gate_end),
        "notice": "First/last timestamps do not prove continuous logging; the replay can only report event-span coverage.",
    }
    coverage_sufficient = (
        all(
            coverage_report[key]["covers_requested_bounds"]
            for key in ("memory_main", "memory_sidecar", "gate")
        )
        and gate["eligible_screens"] > 0
    )
    payload = {
        "schema": "jev-jzgm-replay-v1",
        "status": "REPLAYED" if coverage_sufficient else "INSUFFICIENT_COVERAGE",
        "policy": args.policy,
        "memory_cap": args.memory_cap,
        "window_utc": {
            "memory": {
                "from_inclusive": start.isoformat(),
                "to_exclusive": end.isoformat(),
            },
            "gate": {
                "from_inclusive": gate_start.isoformat(),
                "to_exclusive": gate_end.isoformat(),
            },
            "requested_days_max": max(
                (end - start).total_seconds(), (gate_end - gate_start).total_seconds()
            )
            / 86400,
        },
        "event_span_coverage": coverage_report,
        "acceptance_checks": {
            "cap3_per_turn_reference": memory["cap3"]["frozen_reference"][
                "matches_exactly"
            ],
            "cap3_legacy_aggregate_reference": memory["cap3"][
                "legacy_aggregate_reference"
            ]["matches_exactly"],
            "gate_96pct_in_wilson95": gate["reference_96pct_in_wilson95"],
            "noop_zero_delta": not noop
            or (
                all(value == 0 for value in memory["cap3"]["noop_delta"].values())
                and all(value == 0 for value in gate["noop_delta"].values())
            ),
        },
        "memory": memory,
        "gate_cascade": gate,
        "no_live_calls": True,
        "raw_text_emitted": False,
    }
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
