#!/usr/bin/env python3
"""Compare action-type mixes between a live arm and its reference arm."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

ACTION_TYPES = {"click", "type", "select", "none", "switch", "move", "tera"}
ACTION_RE = re.compile(r"^\s*([a-z]+)\s*(?:\[|$)", re.IGNORECASE)


def action_type(value: object) -> str | None:
    """Return the normalized verb from a MiniWoB or PokéJev action string."""
    if not isinstance(value, str):
        return None
    text = value.strip().lower()
    if text.startswith("/choose "):
        text = text[8:].lstrip()
    match = ACTION_RE.match(text)
    if match:
        verb = match.group(1)
    else:
        verb = text.split(None, 1)[0] if text else ""
    return verb if verb in ACTION_TYPES else None


def _poke_actions(row: dict, allow_fallback: bool) -> list[str]:
    candidates = row.get("candidates")
    chosen = row.get("chosen") or row.get("tool")
    chosen_type = action_type(chosen)
    if isinstance(candidates, list):
        offered = {kind for kind in (action_type(item) for item in candidates) if kind}
        if len(offered) <= 1 or chosen_type not in offered:
            return []
        return [chosen_type]
    if (
        allow_fallback
        and isinstance(row.get("n_options"), int)
        and row["n_options"] > 1
    ):
        return [chosen_type] if chosen_type else []
    return []


def _miniwob_actions(row: dict) -> list[str]:
    out = []
    for decision in row.get("decisions", []):
        if not isinstance(decision, dict) or decision.get("n_action_options", 0) <= 1:
            continue
        kind = action_type(decision.get("action"))
        if kind:
            out.append(kind)
    return out


def read_rows(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as source:
        for line_number, line in enumerate(source, 1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"{path}:{line_number}: invalid JSON: {exc.msg}"
                ) from exc
    return rows


def mix_rows(rows: list[dict]) -> tuple[Counter[str], int]:
    poke_rows = [row for row in rows if not isinstance(row.get("decisions"), list)]
    has_offered_types = any(
        isinstance(row.get("candidates"), list) for row in poke_rows
    )
    counts: Counter[str] = Counter()
    for row in rows:
        actions = (
            _miniwob_actions(row)
            if isinstance(row.get("decisions"), list)
            else _poke_actions(row, allow_fallback=not has_offered_types)
        )
        counts.update(actions)
    return counts, sum(counts.values())


def load_mix(path: Path) -> tuple[Counter[str], int]:
    return mix_rows(read_rows(path))


def rate(count: int, total: int) -> float:
    return count / total if total else 0.0


def z_score(first: int, first_total: int, second: int, second_total: int) -> float:
    p_first = rate(first, first_total)
    p_second = rate(second, second_total)
    pooled = (first + second) / (first_total + second_total)
    denominator = math.sqrt(
        pooled * (1 - pooled) * (1 / first_total + 1 / second_total)
    )
    return 0.0 if denominator == 0 else (p_first - p_second) / denominator


def evaluate(
    arm_counts: Counter[str],
    arm_rows: int,
    reference_counts: Counter[str],
    reference_rows: int,
    min_rows: int,
    max_diff: float,
) -> tuple[int, list[str]]:
    if arm_rows < min_rows or reference_rows < min_rows:
        return 2, [
            f"NOT_RUN: eligible rows arm={arm_rows}, reference={reference_rows}; "
            f"need {min_rows} in each"
        ]

    bad = False
    output = []
    for kind in sorted(set(arm_counts) | set(reference_counts)):
        arm_rate = rate(arm_counts[kind], arm_rows)
        reference_rate = rate(reference_counts[kind], reference_rows)
        difference = abs(arm_rate - reference_rate)
        z = z_score(arm_counts[kind], arm_rows, reference_counts[kind], reference_rows)
        output.append(
            f"type={kind} arm={arm_rate:.3f} reference={reference_rate:.3f} "
            f"diff={difference:.3f} z={z:.2f} n={arm_rows}/{reference_rows}"
        )
        concentration = arm_rate >= 0.95 and reference_rate <= 0.80
        if (difference > max_diff and abs(z) > 4) or concentration:
            bad = True
    return (1 if bad else 0), output


def compare_records(
    arm_records: list[dict],
    reference: Path,
    min_rows: int = 200,
    max_diff: float = 0.25,
) -> dict:
    arm_counts, arm_rows = mix_rows(arm_records)
    reference_counts, reference_rows = load_mix(reference)
    exit_code, output = evaluate(
        arm_counts,
        arm_rows,
        reference_counts,
        reference_rows,
        min_rows,
        max_diff,
    )
    return {
        "exit_code": exit_code,
        "output": output,
        "arm_rows": arm_rows,
        "reference_rows": reference_rows,
    }


def compare(
    arm: Path, reference: Path, min_rows: int = 200, max_diff: float = 0.25
) -> int:
    result = compare_records(read_rows(arm), reference, min_rows, max_diff)
    print("\n".join(result["output"]))
    return result["exit_code"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arm", type=Path, required=True)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--min-rows", type=int, default=200)
    parser.add_argument("--max-diff", type=float, default=0.25)
    args = parser.parse_args(argv)
    try:
        return compare(args.arm, args.reference, args.min_rows, args.max_diff)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
