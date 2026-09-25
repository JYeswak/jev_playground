#!/usr/bin/env python3
"""Fail closed when a preregistered exact-completion bar is unreachable."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

Z_95 = 1.959963984540054


_DECODER = json.JSONDecoder()


def _decode_json(text: str, source: str) -> Any:
    try:
        return _DECODER.decode(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{source} is not valid JSON: {exc}") from exc


def _read_json(path: Path) -> Any:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"cannot read JSON {path}: {exc}") from exc
    return _decode_json(text, str(path))


def _task_id(value: Any, source: str) -> str:
    if isinstance(value, str) and value:
        return value
    if isinstance(value, dict) and isinstance(value.get("task"), str) and value["task"]:
        return value["task"]
    raise ValueError(f"{source} has a task entry without a non-empty task id")


def manifest_tasks(path: Path) -> list[str]:
    payload = _read_json(path)
    entries = payload.get("tasks") if isinstance(payload, dict) else payload
    if not isinstance(entries, list):
        raise ValueError(f"{path} has no task list")
    tasks = [_task_id(entry, str(path)) for entry in entries]
    if len(set(tasks)) != len(tasks):
        raise ValueError(f"{path} contains duplicate task ids")
    return tasks


def jsonl_tasks(path: Path) -> set[str]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ValueError(f"cannot read JSONL {path}: {exc}") from exc
    tasks: set[str] = set()
    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        row = _decode_json(line, f"{path}:{line_number}")
        tasks.add(_task_id(row, f"{path}:{line_number}"))
    return tasks


def heldout_tasks(manifest: Path, used_rows: Path) -> list[str]:
    all_tasks = set(manifest_tasks(manifest))
    used = jsonl_tasks(used_rows)
    missing = used - all_tasks
    if missing:
        raise ValueError(
            f"used rows contain {len(missing)} task ids absent from manifest"
        )
    result = sorted(all_tasks - used)
    if not result:
        raise ValueError("held-out split is empty")
    return result


def _exact(value: Any) -> bool:
    try:
        return float(value) >= 1.0
    except (TypeError, ValueError) as exc:
        raise ValueError(f"non-numeric official reward: {value!r}") from exc


def oracle_exact_from_preflight(path: Path) -> int:
    receipt = _read_json(path)
    try:
        offered = receipt["winning_archive_offered"]
        winners = int(offered["oracle_winner_tasks"])
        offered_tasks = int(offered["offered_tasks"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"{path} is missing oracle winner counts") from exc
    if winners != offered_tasks:
        raise ValueError(
            f"{path} reports only {winners}/{offered_tasks} oracle winners offered"
        )
    return winners


def comparator_exact_from_floor(
    floor_path: Path,
    tasks: list[str],
    archive: str | None,
    oracle_exact: int | None = None,
) -> tuple[int, int, str]:
    floor = _read_json(floor_path)
    results = floor.get("results_by_task") if isinstance(floor, dict) else None
    if not isinstance(results, dict):
        raise ValueError(f"{floor_path} has no results_by_task mapping")
    comparator = archive or floor.get("best_single_archive")
    if not isinstance(comparator, str) or not comparator:
        raise ValueError("comparator archive is not declared")
    selected = floor.get("selected_archives")
    candidates = selected if isinstance(selected, list) else []
    comparator_wins = 0
    oracle_wins = 0
    for task in tasks:
        row = results.get(task)
        if not isinstance(row, dict) or comparator not in row:
            raise ValueError(f"floor has no {comparator!r} reward for {task}")
        if not candidates:
            candidates = sorted(row)
        if not all(isinstance(name, str) and name in row for name in candidates):
            raise ValueError(f"floor candidate set is incomplete for {task}")
        comparator_wins += _exact(row[comparator])
        oracle_wins += any(_exact(row[name]) for name in candidates)
    if oracle_exact is not None:
        if not 0 <= oracle_exact <= len(tasks):
            raise ValueError("preflight oracle exact count is outside the task range")
        oracle_wins = oracle_exact
    return comparator_wins, oracle_wins - comparator_wins, comparator


def score_receipt_observed(path: Path) -> tuple[int, dict[str, int | float]]:
    receipt = _read_json(path)
    try:
        tasks = int(receipt["retained_task_count"])
        selected_exact = int(receipt["selected_exact_tasks"])
        observed = receipt["mcnemar_vs_best_single"]
        observed_b = int(observed["b"])
        observed_c = int(observed["c"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"{path} is missing the R112 score fields") from exc
    comparator_exact = selected_exact - observed_b + observed_c
    if not 0 <= comparator_exact <= tasks:
        raise ValueError(f"inconsistent R112 comparator count for {tasks} tasks")
    return tasks, {
        "observed_b": observed_b,
        "observed_c": observed_c,
        "observed_p": float(observed.get("p", math.nan)),
        "score_comparator_exact": comparator_exact,
    }


def exact_mcnemar_p(discordant_wins: int, discordant_losses: int) -> float:
    """Two-sided exact McNemar p using the smaller discordant tail."""
    if discordant_wins < 0 or discordant_losses < 0:
        raise ValueError("discordant counts must be non-negative")
    n = discordant_wins + discordant_losses
    if n == 0:
        return 1.0
    lower = min(discordant_wins, discordant_losses)
    tail = sum(math.comb(n, i) for i in range(lower + 1)) / (2**n)
    return min(1.0, 2 * tail)


def mcnemar_reachability(
    tasks: int, comparator_exact: int, oracle_headroom: int, alpha: float
) -> dict[str, Any]:
    if tasks <= 0 or not 0 <= comparator_exact <= tasks:
        raise ValueError("tasks and comparator_exact are inconsistent")
    if not 0 <= oracle_headroom <= tasks - comparator_exact:
        raise ValueError("oracle headroom exceeds the comparator's exact misses")
    if not 0 < alpha < 1:
        raise ValueError("alpha must be between 0 and 1")
    minimum_p = exact_mcnemar_p(oracle_headroom, 0)
    return {
        "mode": "mcnemar",
        "tasks": tasks,
        "comparator_exact": comparator_exact,
        "oracle_headroom": oracle_headroom,
        "max_discordant_wins": oracle_headroom,
        "best_case_discordant_losses": 0,
        "minimum_attainable_p": minimum_p,
        "alpha": alpha,
        "status": "REACHABLE" if minimum_p < alpha else "UNREACHABLE",
    }


def wilson_lower_bound(successes: int, trials: int) -> float:
    if trials <= 0 or not 0 <= successes <= trials:
        raise ValueError("successes and trials are inconsistent")
    z2 = Z_95**2
    p = successes / trials
    denominator = 1 + z2 / trials
    center = p + z2 / (2 * trials)
    spread = Z_95 * math.sqrt(p * (1 - p) / trials + z2 / (4 * trials**2))
    return (center - spread) / denominator


def rate_reachability(trials: int, threshold: float) -> dict[str, Any]:
    if not 0 < threshold <= 1:
        raise ValueError("rate threshold must be in (0, 1]")
    lower = wilson_lower_bound(trials, trials)
    return {
        "mode": "rate",
        "trials": trials,
        "perfect_successes": trials,
        "wilson_lower_bound_95": lower,
        "threshold": threshold,
        "status": "REACHABLE" if lower >= threshold else "UNREACHABLE",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("mcnemar", "rate"), default="mcnemar")
    parser.add_argument("--floor", type=Path, help="floor receipt with results_by_task")
    parser.add_argument(
        "--manifest", type=Path, help="manifest containing the full task list"
    )
    parser.add_argument(
        "--used-rows", type=Path, help="JSONL rows whose task ids form the used split"
    )
    parser.add_argument("--comparator-archive")
    parser.add_argument(
        "--preflight",
        type=Path,
        help="receipt carrying the fixed-candidate oracle winner count",
    )
    parser.add_argument(
        "--score-receipt",
        type=Path,
        help="committed score receipt with observed McNemar counts",
    )
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--trials", type=int)
    parser.add_argument("--threshold", type=float)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.mode == "rate":
            if args.trials is None or args.threshold is None:
                raise ValueError("rate mode requires --trials and --threshold")
            result = rate_reachability(args.trials, args.threshold)
        else:
            if args.score_receipt:
                if not args.floor or not args.used_rows:
                    raise ValueError(
                        "score receipt mode requires --score-receipt, --floor, and --used-rows"
                    )
                observed_tasks, observed = score_receipt_observed(args.score_receipt)
                tasks_list = sorted(jsonl_tasks(args.used_rows))
                if observed_tasks != len(tasks_list):
                    raise ValueError(
                        "score receipt and used rows have different task counts"
                    )
                comparator_exact, headroom, archive = comparator_exact_from_floor(
                    args.floor, tasks_list, args.comparator_archive
                )
                result = mcnemar_reachability(
                    len(tasks_list), comparator_exact, headroom, args.alpha
                )
                result["observed"] = observed
                result["comparator_archive"] = archive
                result["oracle_headroom_source"] = (
                    "floor.results_by_task fixed candidate pool"
                )
            else:
                if not args.floor or not args.manifest or not args.used_rows:
                    raise ValueError(
                        "McNemar floor mode requires --floor, --manifest, and --used-rows"
                    )
                tasks_list = heldout_tasks(args.manifest, args.used_rows)
                oracle_exact = (
                    oracle_exact_from_preflight(args.preflight)
                    if args.preflight
                    else None
                )
                comparator_exact, headroom, archive = comparator_exact_from_floor(
                    args.floor, tasks_list, args.comparator_archive, oracle_exact
                )
                result = mcnemar_reachability(
                    len(tasks_list), comparator_exact, headroom, args.alpha
                )
                result["comparator_archive"] = archive
                if args.preflight:
                    result["oracle_headroom_source"] = (
                        "committed preflight oracle winner count"
                    )
    except ValueError as exc:
        print(json.dumps({"status": "ERROR", "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "REACHABLE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
