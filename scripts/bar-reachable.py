#!/usr/bin/env python3
"""Fail closed when a preregistered exact-completion bar is unreachable."""

from __future__ import annotations

import argparse
import hashlib
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


def _minority_status(minority_count: int | None, minimum: int | None) -> str | None:
    if minimum is None:
        return None
    if minimum < 1:
        raise ValueError("minimum minority class count must be positive")
    if minority_count is None:
        raise ValueError("minority class count is required when a minimum is set")
    if minority_count < 0:
        raise ValueError("minority class count must be non-negative")
    return "REACHABLE" if minority_count >= minimum else "UNDERPOWERED"


def rate_reachability(
    trials: int,
    threshold: float,
    minority_count: int | None = None,
    minimum_minority: int | None = None,
) -> dict[str, Any]:
    if not 0 < threshold <= 1:
        raise ValueError("rate threshold must be in (0, 1]")
    lower = wilson_lower_bound(trials, trials)
    minority_status = _minority_status(minority_count, minimum_minority)
    status = minority_status or ("REACHABLE" if lower >= threshold else "UNREACHABLE")
    return {
        "mode": "rate",
        "trials": trials,
        "perfect_successes": trials,
        "wilson_lower_bound_95": lower,
        "threshold": threshold,
        **(
            {"minority_count": minority_count, "minimum_minority": minimum_minority}
            if minimum_minority is not None
            else {}
        ),
        "status": status,
    }


def auc_reachability(
    positive_count: int,
    negative_count: int,
    threshold: float,
    minimum_minority: int | None = None,
) -> dict[str, Any]:
    if positive_count <= 0 or negative_count <= 0:
        raise ValueError("AUROC class counts must both be positive")
    if not 0 < threshold <= 1:
        raise ValueError("AUROC threshold must be in (0, 1]")
    minority_count = min(positive_count, negative_count)
    minority_status = _minority_status(minority_count, minimum_minority)
    return {
        "mode": "auc",
        "positive_count": positive_count,
        "negative_count": negative_count,
        "minority_count": minority_count,
        "threshold": threshold,
        "perfect_auc": 1.0,
        "status": minority_status or "REACHABLE",
    }


def flip_fixture_result(path: Path) -> dict[str, Any]:
    payload = _read_json(path)
    try:
        tasks = int(payload["tasks"])
        comparator_exact = int(payload["comparator_exact"])
        oracle_headroom = int(payload["oracle_headroom"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"{path} is missing flip fixture counts") from exc
    result = mcnemar_reachability(
        tasks, comparator_exact, oracle_headroom, float(payload.get("bar_alpha", 0.05))
    )
    result["fixture"] = payload.get("fixture", path.name)
    return result


def _receipt_metadata(prereg_path: Path, items_path: Path, mode: str) -> dict[str, str]:
    declared_mode = None
    for line in prereg_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("reach-mode:"):
            declared_mode = line.partition(":")[2].strip()
            break
    if declared_mode not in {"mcnemar", "rate", "auc"}:
        raise ValueError(f"{prereg_path} must declare reach-mode: mcnemar|rate|auc")
    if declared_mode != mode:
        raise ValueError(
            f"preregistration declares reach mode {declared_mode!r}, not {mode!r}"
        )
    return {
        "mode": mode,
        "prereg_path": str(prereg_path.resolve()),
        "prereg_sha256": hashlib.sha256(prereg_path.read_bytes()).hexdigest(),
        "items_sha256": hashlib.sha256(items_path.read_bytes()).hexdigest(),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("mcnemar", "rate", "auc"), default="mcnemar")
    parser.add_argument(
        "--prereg", type=Path, help="preregistration declaring reach-mode"
    )
    parser.add_argument(
        "--items", type=Path, help="exact items file hashed into the receipt"
    )
    parser.add_argument(
        "--flip-fixture",
        type=Path,
        help="committed boundary fixture for the reachability guard",
    )
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
    parser.add_argument("--minority-count", type=int)
    parser.add_argument("--min-minority-class", type=int)
    parser.add_argument("--positive-count", type=int)
    parser.add_argument("--negative-count", type=int)
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit the verdict as JSON (output is JSON either way)",
    )
    return parser

def _cohort_only_args(args: argparse.Namespace) -> bool:
    return (
        args.prereg is not None
        and args.items is None
        and args.floor is None
        and args.manifest is None
        and args.used_rows is None
        and args.score_receipt is None
        and args.trials is None
        and args.positive_count is None
        and args.negative_count is None
        and args.comparator_archive is None
        and args.preflight is None
        and args.threshold is None
        and args.min_minority_class is None
        and args.flip_fixture is None
    )


def _resolve_cohort_source(path_value: object, cohort_path: Path) -> Path | None:
    if not isinstance(path_value, str) or not path_value:
        return None
    candidate = Path.cwd() / path_value
    if candidate.is_file():
        return candidate
    sibling = cohort_path.parent / path_value
    return sibling if sibling.is_file() else None


def _bind_cohort_to_frozen_source(cohort: dict, cohort_path: Path) -> None:
    """Bind reach.json counts to the frozen demand source it cites. A cohort
    whose counts disagree with its own cited receipt/rows is refused: forged
    counts must not yield a verdict against a zero-harm source."""
    source = cohort.get("source")
    if not isinstance(source, dict):
        raise ValueError("reach.json must carry a source block with receipt and rows_file")
    rows_path = _resolve_cohort_source(source.get("rows_file"), cohort_path)
    if rows_path is None:
        raise ValueError(
            f"reach.json rows_file missing or unreadable: {source.get('rows_file')!r}"
        )
    try:
        rows_bytes = rows_path.read_bytes()
    except OSError as exc:
        raise ValueError(f"reach.json rows_file unreadable: {exc}") from exc
    row_count = sum(1 for line in rows_bytes.splitlines() if line.strip())
    actual_rows_digest = hashlib.sha256(rows_bytes).hexdigest()
    want_rows_digest = cohort.get("rows_sha256")
    if want_rows_digest is None:
        raise ValueError("reach.json must carry rows_sha256 (full-file digest)")
    if actual_rows_digest != want_rows_digest:
        raise ValueError("reach.json rows_sha256 disagrees with rows file bytes")
    receipt_path = _resolve_cohort_source(source.get("receipt"), cohort_path)
    if receipt_path is None:
        raise ValueError(f"reach.json receipt missing or unreadable: {source.get('receipt')!r}")
    demand = json.loads(receipt_path.read_text(encoding="utf-8"))
    if row_count != demand.get("eligible_denominator"):
        raise ValueError(
            f"rows file holds {row_count} rows, receipt eligible denominator "
            f"is {demand.get('eligible_denominator')!r}"
        )
    hashes = demand.get("source_hashes", {}) if isinstance(demand.get("source_hashes"), dict) else {}
    window = demand.get("window", {}) if isinstance(demand.get("window"), dict) else {}
    want_digest = (
        hashes.get("window_rows_sha256")
        or window.get("window_rows_sha256")
        or demand.get("window_rows_sha256")
    )
    if want_digest is None or source.get("window_rows_sha256") != want_digest:
        raise ValueError(
            "reach.json window_rows_sha256 disagrees with the demand receipt digest"
        )
    recount = demand.get("labels_recounted", {})
    expected = {
        "eligible_denominator": demand.get("eligible_denominator"),
        "covered_rows": recount.get("covered_rows"),
        "harm_rows": recount.get("harm_rows"),
        "missing_outcomes": demand.get("missing_outcomes"),
    }
    for key, want in expected.items():
        if want is None:
            raise ValueError(f"demand receipt lacks {key}")
        if cohort.get(key) != want:
            raise ValueError(
                f"reach.json {key}={cohort.get(key)!r} disagrees with frozen source {want!r}"
            )


def cohort_verdict(prereg_path: Path) -> dict:
    """Terminal cohort verdict driven by a preregistration and its sibling
    reach.json counts. Zero-class cohorts refuse as NOT_REACHABLE instead
    of raising; present classes run the same mode math as CLI arguments."""
    declared_mode = None
    for line in prereg_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("reach-mode:"):
            declared_mode = line.partition(":")[2].strip()
            break
    if declared_mode not in {"mcnemar", "rate", "auc"}:
        raise ValueError(f"{prereg_path} must declare reach-mode: mcnemar|rate|auc")
    cohort_path = prereg_path.parent / "reach.json"
    if not cohort_path.is_file():
        raise ValueError(f"cohort counts file missing: {cohort_path}")
    cohort = json.loads(cohort_path.read_text(encoding="utf-8"))
    _bind_cohort_to_frozen_source(cohort, cohort_path)
    meta = {
        "mode": declared_mode,
        "prereg_path": str(prereg_path.resolve()),
        "prereg_sha256": hashlib.sha256(prereg_path.read_bytes()).hexdigest(),
        "cohort_path": str(cohort_path.resolve()),
        "cohort_sha256": hashlib.sha256(cohort_path.read_bytes()).hexdigest(),
    }
    if declared_mode == "auc":
        harm = cohort.get("harm_rows")
        covered = cohort.get("covered_rows")
        if harm is None or covered is None:
            raise ValueError("reach.json must carry harm_rows and covered_rows")
        for key in ("positive_count", "negative_count"):
            if key in cohort:
                raise ValueError(
                    f"reach.json {key} overrides the source-bound split; remove it"
                )
        positive, negative = harm, covered - harm
        if negative < 0:
            raise ValueError("reach.json covered_rows below harm_rows")
        if positive == 0 or negative == 0:
            return {
                "status": "NOT_REACHABLE",
                "reason": (
                    f"auc minority class empty: positive={positive} "
                    f"negative={negative}; infeasible input: labelled "
                    f"{'harmful' if positive == 0 else 'clean'} outcomes"
                ),
                **meta,
            }
        threshold = cohort.get("threshold")
        if threshold is None:
            raise ValueError("reach.json needs threshold once both classes are present")
        return {
            **auc_reachability(positive, negative, threshold, cohort.get("min_minority_class")),
            **meta,
        }
    if declared_mode == "rate":
        for key in ("trials", "threshold"):
            if cohort.get(key) is None:
                raise ValueError(f"reach.json needs {key} for rate mode")
        return {
            **rate_reachability(
                cohort["trials"],
                cohort["threshold"],
                cohort.get("minority_count"),
                cohort.get("min_minority_class"),
            ),
            **meta,
        }
    raise ValueError("mcnemar cohort path needs floor/manifest inputs, not reach.json")

def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if _cohort_only_args(args):
            result = cohort_verdict(args.prereg)
        elif args.flip_fixture:
            result = flip_fixture_result(args.flip_fixture)
        elif args.mode == "rate":
            if args.trials is None or args.threshold is None:
                raise ValueError("rate mode requires --trials and --threshold")
            result = rate_reachability(
                args.trials,
                args.threshold,
                args.minority_count,
                args.min_minority_class,
            )
        elif args.mode == "auc":
            if (
                args.positive_count is None
                or args.negative_count is None
                or args.threshold is None
            ):
                raise ValueError(
                    "auc mode requires --positive-count, --negative-count, and --threshold"
                )
            result = auc_reachability(
                args.positive_count,
                args.negative_count,
                args.threshold,
                args.min_minority_class,
            )
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
        if "cohort_path" not in result and (args.prereg is not None or args.items is not None):
            if args.prereg is None or args.items is None:
                raise ValueError("--prereg and --items must be supplied together")
            result.update(_receipt_metadata(args.prereg, args.items, result["mode"]))
    except ValueError as exc:
        print(json.dumps({"status": "ERROR", "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "REACHABLE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
