#!/usr/bin/env python3
"""Summarize Jev shadow logs without emitting command or query text."""

from __future__ import annotations

import argparse
import json
import random
import statistics
from pathlib import Path
from typing import Any

INPUT_COST_PER_MILLION = 0.042
DEFAULT_GATE_SHADOW = Path.home() / ".local/state/jev/gate-shadow.jsonl"
DEFAULT_GATE_OBSERVE = Path.home() / ".local/state/jev/gate-observe.jsonl"
DEFAULT_WEB_SHADOW = Path.home() / ".local/state/jev/websearch-rerank.jsonl"


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


def build_report(
    shadow_path: Path,
    existing_path: Path,
    web_path: Path,
    sample_size: int = 20,
    seed: int = 20260927,
) -> dict[str, Any]:
    return {
        "schema": "jev-shadow-report.v1",
        "seed": seed,
        "gate": gate_report(rows(shadow_path), rows(existing_path), sample_size, seed),
        "web_search_rerank": web_report(rows(web_path)),
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
    parser.add_argument("--web-shadow", type=Path, default=DEFAULT_WEB_SHADOW)
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
        args.gate_shadow, args.gate_observe, args.web_shadow, args.sample_size
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
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
