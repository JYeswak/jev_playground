#!/usr/bin/env python3
"""Score the preregistered MiniWoB AX-pruning row files.

This scorer does not call Jev or the MiniWoB environment. It validates one
complete 50-row file per arm, reports success counts and token/wall-time
summaries per arm, and reports how many tasks succeeded in at least one arm.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

ARMS = ("full", "code", "jev", "random")
SPLITS = ("dev", "heldout")
EPISODES_PER_ARM = 50
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
ROWS_DIR = HERE / "rows"


def _nearest_rank(values: list[float], quantile: float) -> float:
    if not values:
        raise ValueError("cannot compute a quantile over zero rows")
    rank = max(1, math.ceil(quantile * len(values)))
    return sorted(values)[rank - 1]


def _read_rows(split: str, arm: str) -> list[dict[str, Any]]:
    path = ROWS_DIR / f"{split}-{arm}.jsonl"
    if not path.is_file():
        raise FileNotFoundError(f"missing preregistered row file: {path}")
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as source:
        for line_number, line in enumerate(source, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"invalid JSON at {path}:{line_number}: {exc}"
                ) from exc
            if not isinstance(row, dict):
                raise ValueError(f"row at {path}:{line_number} is not an object")
            rows.append(row)
    if len(rows) != EPISODES_PER_ARM:
        raise ValueError(
            f"{path} has {len(rows)} rows; expected exactly {EPISODES_PER_ARM}"
        )
    tasks: set[str] = set()
    for index, row in enumerate(rows, 1):
        task = row.get("task")
        if not isinstance(task, str) or not task:
            raise ValueError(f"{path} row {index} has no task name")
        if task in tasks:
            raise ValueError(f"{path} repeats task {task!r}")
        tasks.add(task)
        if row.get("split") != split or row.get("arm") != arm:
            raise ValueError(f"{path} row {index} has mismatched split/arm metadata")
        for field in ("success", "wall_s", "planner_input_tokens"):
            value = row.get(field)
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise ValueError(f"{path} row {index} has invalid {field}")
    return rows


def _arm_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    successes = sum(float(row["success"]) > 0 for row in rows)
    tokens = [float(row["planner_input_tokens"]) for row in rows]
    wall = [float(row["wall_s"]) for row in rows]
    return {
        "episodes": len(rows),
        "successes": successes,
        "success_rate": successes / len(rows),
        "planner_input_tokens_total": sum(tokens),
        "planner_input_tokens_mean": sum(tokens) / len(tokens),
        "wall_s_p50": _nearest_rank(wall, 0.50),
        "wall_s_p95": _nearest_rank(wall, 0.95),
        "errors": sum(bool(row.get("error")) for row in rows),
    }


def score_split(split: str) -> dict[str, Any]:
    rows_by_arm = {arm: _read_rows(split, arm) for arm in ARMS}
    task_names = sorted(
        {str(row["task"]) for rows in rows_by_arm.values() for row in rows}
    )
    successful_tasks = sorted(
        task
        for task in task_names
        if any(
            any(str(row["task"]) == task and float(row["success"]) > 0 for row in rows)
            for rows in rows_by_arm.values()
        )
    )
    return {
        "split": split,
        "tasks": len(task_names),
        "arms": {arm: _arm_summary(rows_by_arm[arm]) for arm in ARMS},
        "ever_successful_tasks": len(successful_tasks),
        "ever_successful_task_names": successful_tasks,
    }


def selftest() -> int:
    rows = [
        {
            "task": f"task-{index}",
            "split": "heldout",
            "arm": "full",
            "success": index == 0,
            "wall_s": float(index + 1),
            "planner_input_tokens": 10,
        }
        for index in range(EPISODES_PER_ARM)
    ]
    assert _arm_summary(rows)["successes"] == 1
    assert _nearest_rank([1.0, 2.0, 3.0, 4.0], 0.95) == 4.0
    assert len({str(row["task"]) for row in rows}) == EPISODES_PER_ARM
    print("SELFTEST PASS: AX row validation helpers and nearest-rank summaries")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--split", choices=(*SPLITS, "all"), default="all")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    splits = SPLITS if args.split == "all" else (args.split,)
    print(json.dumps({split: score_split(split) for split in splits}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
