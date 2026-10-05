#!/usr/bin/env python3
"""Recompute keyless and sanitized live same-pair stability."""

from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path.home() / ".local/state/jev/memory-filter.jsonl"
LIVE = ROOT / "work/jev-li3w/rows.jsonl"
THRESHOLD = 0.05
EXPECTED_PAIRS = 97
EXPECTED_REPEATS = 3
FROZEN_PATH = ROOT / "work/jev-li3w/frozen-pairs.jsonl"


def read_rows(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as stream:
        for line_no, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSON") from exc
    return rows


def groups(rows: list[dict[str, Any]]) -> dict[tuple[str, str], list[dict[str, Any]]]:
    result: dict[tuple[str, str], list[dict[str, Any]]] = collections.defaultdict(list)
    for row in rows:
        if row.get("status") != "scored":
            continue
        prompt, memory, decision = (
            row.get("promptHash"),
            row.get("memoryHash"),
            row.get("decision"),
        )
        if not isinstance(prompt, str) or not isinstance(memory, str):
            continue
        if decision not in {"drop", "keep"}:
            continue
        result[(prompt, memory)].append(row)
    return dict(result)


def summarize(grouped: dict[tuple[str, str], list[dict[str, Any]]]) -> dict[str, Any]:
    repeated = {key: rows for key, rows in grouped.items() if len(rows) >= 2}
    flips = sum(
        len({row["decision"] for row in rows}) > 1 for rows in repeated.values()
    )
    return {
        "scored_pairs": len(grouped),
        "repeated_pairs": len(repeated),
        "flipping_pairs": flips,
        "flip_rate": flips / len(repeated) if repeated else None,
        "verdict": "STABLE"
        if repeated and flips / len(repeated) <= THRESHOLD
        else "UNSTABLE",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--json", action="store_true", help="emit machine-readable JSON"
    )
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--live", type=Path, default=LIVE)
    args = parser.parse_args()

    source_groups = groups(read_rows(args.source))
    keyless = summarize(source_groups)
    frozen_rows = read_rows(FROZEN_PATH)
    frozen = [(row["promptHash"], row["memoryHash"]) for row in frozen_rows]
    if len(frozen) != EXPECTED_PAIRS:
        raise ValueError(
            f"frozen sample has {len(frozen)} pairs, expected {EXPECTED_PAIRS}"
        )
    live_rows = read_rows(args.live) if args.live.exists() else []
    live_groups = groups(live_rows)
    observed = {key: live_groups.get(key, []) for key in frozen}
    live_covered = all(len(rows) >= EXPECTED_REPEATS for rows in observed.values())
    live_complete = len(frozen) == EXPECTED_PAIRS and live_covered
    live_summary = (
        summarize({key: rows for key, rows in observed.items() if rows})
        if live_rows
        else None
    )
    if live_complete and live_summary:
        live_summary["verdict"] = (
            "STABLE" if live_summary["flip_rate"] <= THRESHOLD else "UNSTABLE"
        )
        live_status = "COMPLETE"
    else:
        live_status = "NOT_RUN" if not live_rows else "INCOMPLETE"
        if live_summary:
            live_summary["verdict"] = (
                "UNSTABLE"
                if live_summary["flip_rate"] is not None
                and live_summary["flip_rate"] > THRESHOLD
                else "NOT_CLAIMABLE"
            )

    output = {
        "protocol": "jev-li3w-v1",
        "model": "jev-1.13.0",
        "estimator": "flipping scored pairs / tested repeated pairs",
        "threshold": THRESHOLD,
        "keyless": keyless,
        "live": {
            "status": live_status,
            "frozen_pair_count": len(frozen),
            "covered_pair_count": sum(bool(rows) for rows in observed.values()),
            "expected_calls_max": EXPECTED_PAIRS * EXPECTED_REPEATS,
            "spend_usd": sum(
                (row.get("inputTokens") or 0)
                for rows in observed.values()
                for row in rows
            )
            * 0.042
            / 1_000_000,
            "summary": live_summary,
        },
        "frozen_pair_count": len(frozen),
        "not_run_count": len(read_rows(ROOT / "work/jev-li3w/not-run.jsonl")),
        "boundary": "Live analysis only covers exact-payload frozen pairs; the 29 NOT_RUN pairs are excluded. This does not establish relevance or safe-drop precision.",
    }
    print(
        json.dumps(output, sort_keys=True)
        if args.json
        else json.dumps(output, indent=2, sort_keys=True)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
