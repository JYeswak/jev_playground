#!/usr/bin/env python3
"""Keyless dry-run contract for the post-reset comparator-only resume."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESET = datetime.fromisoformat("2026-09-28T00:00:00+00:00")
RESULTS = ROOT / "work/jev-oioo/live-results.jsonl"
RUNNER = ROOT / "work/jev-oioo/live.mjs"


def load_rows() -> list[dict]:
    return [
        json.loads(line) for line in RESULTS.read_text().splitlines() if line.strip()
    ]


def dry_run(now: datetime, plant: bool) -> tuple[int, str]:
    rows = load_rows()
    assert len(rows) == 907, f"expected 907 rows, got {len(rows)}"
    jev_ids = {row["id"] for row in rows if row["jev"]["status"] == "scored"}
    assert len(jev_ids) == 907, "all Jev rows must remain scored and untouched"
    answered = [row for row in rows if row["comparator"]["status"] == "scored"]
    not_run = [row for row in rows if row["comparator"]["status"] == "not_run"]
    assert (
        len(answered) == 86
    ), f"expected 86 answered comparator rows, got {len(answered)}"
    assert (
        len(not_run) == 821
    ), f"expected 821 comparator rows to resume, got {len(not_run)}"
    selected = not_run + (answered[:1] if plant else [])
    selected_ids = {row["id"] for row in selected}
    assert selected_ids == {
        row["id"] for row in not_run
    }, "resume selected an answered row"
    assert not (
        selected_ids & jev_ids - {row["id"] for row in not_run}
    ), "resume changed Jev coverage"
    source = RUNNER.read_text()
    assert 'process.env.JEV_OIOO_COMPARATOR_ONLY === "1"' in source
    assert "response.status === 429" in source
    assert "stopped = true" in source
    if now < RESET:
        return 2, f"NOT_RUN: reset at {RESET.isoformat()}, selected={len(selected)}"
    return (
        0,
        f"READY: comparator-only selected={len(selected)} answered=0 Jev={len(jev_ids)}",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plant", action="store_true")
    parser.add_argument("--now", type=str)
    args = parser.parse_args()
    now = datetime.fromisoformat(args.now) if args.now else datetime.now(timezone.utc)
    code, message = dry_run(now, args.plant)
    print(message)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
