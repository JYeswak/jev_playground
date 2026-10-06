#!/usr/bin/env python3
"""Measure the frozen 24-hour post-change gate fallback window.

Only aggregate metadata is emitted. The source log can contain raw command
text; this tool never copies or prints that field.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BEAD = "jev-fd5j"
DEFAULT_SOURCE = (
    Path.home()
    / ".local/state/jev/gate-observe.jsonl.1791212181640."
    "933c4079-d250-403f-b91c-c1abe0709405.archive"
)
EXPECTED_SOURCE_SHA256 = "e9c392befbe5e75dcfe448b30bb67adafe81de836c3941eec9132229ac75352c"
EXPECTED_SOURCE_BYTES = 26_534_295
EXPECTED_SOURCE_ROWS = 41_854

WINDOW_START = "2026-10-02T15:16:17Z"
WINDOW_END = "2026-10-03T15:16:17Z"
BASELINE_WINDOW_START = "2026-10-01T06:27:34Z"
BASELINE_WINDOW_END = "2026-10-02T06:27:34Z"
BASELINE_FALLBACKS = 1_032
BASELINE_SCREENED = 3_560
BASELINE_RATE = BASELINE_FALLBACKS / BASELINE_SCREENED
FALLBACK_PREFIX = "paid-fallback"
NO_SCREEN_ROUTES = {"prerule-paid", "unscreened", "gateway-alert"}


class MeasurementError(ValueError):
    """Raised when the source cannot support the registered measurement."""


def parse_timestamp(value: Any, line_number: int) -> datetime:
    if not isinstance(value, str):
        raise MeasurementError(f"line {line_number}: missing timestamp")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        timestamp = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise MeasurementError(f"line {line_number}: invalid timestamp") from exc
    if timestamp.tzinfo is None:
        raise MeasurementError(f"line {line_number}: timestamp has no timezone")
    return timestamp.astimezone(timezone.utc)


def new_window(start: str, end: str) -> dict[str, Any]:
    return {
        "start": start,
        "end": end,
        "raw_log_rows": 0,
        "screened_rows": 0,
        "fallback_rows": 0,
        "timeout_fallback_rows": 0,
        "cause_labeled_non_timeout_fallback_rows": 0,
        "legacy_untyped_fallback_rows": 0,
        "fallback_labels": {},
        "first_raw_row": None,
        "last_raw_row": None,
        "first_screened_row": None,
        "last_screened_row": None,
    }


def record_window_row(window: dict[str, Any], timestamp: datetime, row: dict[str, Any], line_number: int) -> None:
    window["raw_log_rows"] += 1
    stamp = timestamp.isoformat(timespec="milliseconds").replace("+00:00", "Z")
    if window["first_raw_row"] is None:
        window["first_raw_row"] = stamp
    window["last_raw_row"] = stamp

    marker = row.get("jevSkipped")
    if marker is not None and marker is not True and marker is not False:
        raise MeasurementError(f"line {line_number}: invalid cascade marker")
    screen = row.get("screen")
    if screen is not None and not isinstance(screen, str):
        raise MeasurementError(f"line {line_number}: invalid screen label")

    screened = marker is True or marker is False
    if screened and screen not in NO_SCREEN_ROUTES:
        window["screened_rows"] += 1
        if window["first_screened_row"] is None:
            window["first_screened_row"] = stamp
        window["last_screened_row"] = stamp

    labelled_fallback = isinstance(screen, str) and screen.startswith(FALLBACK_PREFIX)
    legacy_unlabelled_fallback = (
        screen is None
        and marker is False
        and row.get("nimbleProbs") is None
    )
    if not labelled_fallback and not legacy_unlabelled_fallback:
        return
    if marker is not False or not screened:
        raise MeasurementError(f"line {line_number}: fallback lacks a paid cascade decision")

    window["fallback_rows"] += 1
    if legacy_unlabelled_fallback or screen == FALLBACK_PREFIX:
        window["legacy_untyped_fallback_rows"] += 1
        label = "legacy-untyped"
    elif screen == f"{FALLBACK_PREFIX}-timeout":
        window["timeout_fallback_rows"] += 1
        label = "timeout"
    elif isinstance(screen, str):
        window["cause_labeled_non_timeout_fallback_rows"] += 1
        label = screen.removeprefix(f"{FALLBACK_PREFIX}-")
    else:
        raise MeasurementError(f"line {line_number}: fallback label is missing")
    labels = window["fallback_labels"]
    labels[label] = labels.get(label, 0) + 1


def finish_window(window: dict[str, Any]) -> dict[str, Any]:
    screened = window["screened_rows"]
    fallbacks = window["fallback_rows"]
    if screened == 0:
        raise MeasurementError("measurement window has no cascade screen rows")
    window["fallback_share"] = fallbacks / screened
    window["fallback_share_percent"] = 100 * fallbacks / screened
    window["non_timeout_or_untyped_fallback_rows"] = (
        window["cause_labeled_non_timeout_fallback_rows"]
        + window["legacy_untyped_fallback_rows"]
    )
    return window


def measure(source_arg: str) -> dict[str, Any]:
    source_path = None if source_arg == "-" else Path(source_arg).expanduser()
    try:
        source_bytes = sys.stdin.buffer.read() if source_path is None else source_path.read_bytes()
    except OSError as exc:
        raise MeasurementError(f"cannot read source: {exc.strerror or 'I/O error'}") from exc

    digest = hashlib.sha256(source_bytes).hexdigest()
    source_rows = 0
    post = new_window(WINDOW_START, WINDOW_END)
    baseline_replay = new_window(BASELINE_WINDOW_START, BASELINE_WINDOW_END)
    post_start = parse_timestamp(WINDOW_START, 0)
    post_end = parse_timestamp(WINDOW_END, 0)
    baseline_start = parse_timestamp(BASELINE_WINDOW_START, 0)
    baseline_end = parse_timestamp(BASELINE_WINDOW_END, 0)

    for line_number, line in enumerate(source_bytes.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise MeasurementError(f"line {line_number}: invalid JSON") from exc
        if not isinstance(row, dict):
            raise MeasurementError(f"line {line_number}: expected a JSON object")
        source_rows += 1
        timestamp = parse_timestamp(row.get("ts"), line_number)
        if post_start <= timestamp < post_end:
            record_window_row(post, timestamp, row, line_number)
        if baseline_start <= timestamp < baseline_end:
            record_window_row(baseline_replay, timestamp, row, line_number)

    is_pinned_source = source_path is not None and source_path.resolve() == DEFAULT_SOURCE.resolve()
    if is_pinned_source and (
        digest != EXPECTED_SOURCE_SHA256
        or len(source_bytes) != EXPECTED_SOURCE_BYTES
        or source_rows != EXPECTED_SOURCE_ROWS
    ):
        raise MeasurementError("pinned source snapshot changed; review before recalculating")

    post = finish_window(post)
    baseline_replay = finish_window(baseline_replay)
    passed = post["fallback_rows"] * BASELINE_SCREENED < BASELINE_FALLBACKS * post["screened_rows"]
    baseline_replay["matches_frozen_counts"] = (
        baseline_replay["fallback_rows"] == BASELINE_FALLBACKS
        and baseline_replay["screened_rows"] == BASELINE_SCREENED
    )
    baseline_replay["used_as_threshold"] = False

    if source_path is None:
        source_label = "<stdin>"
    else:
        try:
            source_label = "~/" + str(source_path.resolve().relative_to(Path.home().resolve()))
        except ValueError:
            source_label = str(source_path.resolve())

    return {
        "bead": BEAD,
        "status": "PASS" if passed else "FAIL",
        "acceptance": "fallback share must be strictly below frozen baseline",
        "frozen_baseline": {
            "fallback_rows": BASELINE_FALLBACKS,
            "screened_rows": BASELINE_SCREENED,
            "share": BASELINE_RATE,
            "share_percent": 100 * BASELINE_RATE,
            "source": "jev-fd5j comment 1382",
        },
        "measurement": post,
        "baseline_replay_diagnostic": baseline_replay,
        "source_snapshot": {
            "path": source_label,
            "sha256": digest,
            "bytes": len(source_bytes),
            "rows": source_rows,
        },
        "notes": [
            "Timeout fallback rows are included in fallback_rows and the denominator; a timeout without a paid cascade marker is an error.",
            "Generic paid-fallback rows lack a cause label; they remain in fallback_rows and are reported as legacy_untyped.",
            "The baseline replay uses a trailing 24-hour window ending at comment 1382 and is diagnostic only; its counts do not replace the frozen baseline.",
            "The post-change window starts at 2026-10-02T15:16:17Z, spans 24 hours, and ends 77 seconds after the scheduled 15:15Z horizon.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", required=True, help="emit the machine-readable receipt")
    parser.add_argument("--source", default=str(DEFAULT_SOURCE), help="JSONL snapshot path, or - to read JSONL from stdin")
    args = parser.parse_args()
    try:
        report = measure(args.source)
    except (MeasurementError, OSError) as exc:
        print(json.dumps({"bead": BEAD, "status": "ERROR", "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
