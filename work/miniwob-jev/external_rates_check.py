#!/usr/bin/env python3
"""Validate external MiniWoB rates and print paired v1/v3 slice results.

The external table is keyed to the 125-task manifest in
``work/game-floors/miniwob/tasks.json``. Published values come only from
Humphreys et al. (2022), Table 3, PDF pages 14-15; missing tasks stay blank.
This command is keyless and offline: it reads committed JSONL rows and the
TSV, makes no network or Jev calls.

    python3 work/miniwob-jev/external_rates_check.py
"""

from __future__ import annotations

import csv
import glob
import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TASKS_PATH = ROOT / "work/game-floors/miniwob/tasks.json"
RATES_PATH = ROOT / "work/miniwob-jev/external-rates.tsv"
V1_GLOB = str(ROOT / "work/miniwob-jev/rows/miniwob-jev-v1-heldout.s*.jsonl")
V3_GLOB = str(ROOT / "work/miniwob-jev/live-20260925/rows/miniwob-jev-v3-*.s0.jsonl")
EXPECTED_FIELDS = {
    "task",
    "human_success_rate",
    "cc_net_mean_score",
    "aggregated_sota_bc_rl",
    "aggregated_sota_augmented",
    "human_source",
    "best_agent_source",
    "source_version_match",
    "metric",
    "absence_or_comparability_note",
}


def load_jsonl(paths: list[str]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for raw_path in sorted(paths):
        path = Path(raw_path)
        with path.open(encoding="utf-8") as stream:
            for line_number, raw in enumerate(stream, 1):
                if not raw.strip():
                    continue
                try:
                    value = json.JSONDecoder().decode(raw)
                except json.JSONDecodeError as exc:
                    raise ValueError(
                        f"{path}:{line_number}: invalid JSON: {exc.msg}"
                    ) from exc
                if not isinstance(value, dict):
                    raise ValueError(f"{path}:{line_number}: row is not an object")
                rows.append(value)
    return rows


def parse_rate(value: str, field: str, task: str) -> float:
    try:
        rate = float(value)
    except ValueError as exc:
        raise ValueError(f"{task}: {field} is not numeric: {value!r}") from exc
    if not math.isfinite(rate) or not -1.0 <= rate <= 1.0:
        raise ValueError(f"{task}: {field} outside [-1, 1]: {value!r}")
    return rate


def load_rates(task_order: list[str]) -> dict[str, dict[str, str]]:
    with RATES_PATH.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        if reader.fieldnames is None or set(reader.fieldnames) != EXPECTED_FIELDS:
            raise ValueError(
                f"{RATES_PATH}: expected fields {sorted(EXPECTED_FIELDS)}, "
                f"got {reader.fieldnames}"
            )
        rows = list(reader)
    by_task: dict[str, dict[str, str]] = {}
    for row in rows:
        task = row["task"]
        if not task or task in by_task:
            raise ValueError(f"duplicate or empty task row: {task!r}")
        by_task[task] = row
        human = row["human_success_rate"]
        cc_net = row["cc_net_mean_score"]
        aggregated_bc_rl = row["aggregated_sota_bc_rl"]
        aggregated_augmented = row["aggregated_sota_augmented"]
        if bool(human) != bool(cc_net):
            raise ValueError(
                f"{task}: human and CC-Net rates must be both blank or present"
            )
        if human:
            parse_rate(human, "human_success_rate", task)
            parse_rate(cc_net, "cc_net_mean_score", task)
            for field, value in (
                ("aggregated_sota_bc_rl", aggregated_bc_rl),
                ("aggregated_sota_augmented", aggregated_augmented),
            ):
                if value:
                    parse_rate(value, field, task)
            for field in ("human_source", "best_agent_source", "metric"):
                if not row[field]:
                    raise ValueError(f"{task}: published row missing {field}")
            source = f"{row['human_source']}{row['best_agent_source']}"
            for required in ("https://", "Table 3", "PDF pp. 14-15"):
                if required not in source:
                    raise ValueError(f"{task}: source lacks {required!r}")
            if row["source_version_match"] not in {"yes", "no"}:
                raise ValueError(f"{task}: invalid source_version_match")
        else:
            if row["source_version_match"] != "n/a":
                raise ValueError(f"{task}: blank row must use source_version_match=n/a")
            if not row["absence_or_comparability_note"].strip():
                raise ValueError(f"{task}: blank row needs an absence reason")
    expected = set(task_order)
    actual = set(by_task)
    if actual != expected:
        raise ValueError(
            f"rate task set differs: missing={sorted(expected - actual)}, "
            f"extra={sorted(actual - expected)}"
        )
    return by_task


def success(row: dict[str, object]) -> bool:
    value = row.get("success", 0.0)
    numeric = float(value) if isinstance(value, (int, float)) else 0.0
    return numeric > 0 and not row.get("error")


def aggregate(rows: list[dict[str, object]]) -> dict[str, tuple[int, int]]:
    totals: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for row in rows:
        task = row.get("task")
        if not isinstance(task, str):
            raise ValueError("result row has no string task")
        totals[task][1] += 1
        totals[task][0] += int(success(row))
    return {task: (values[0], values[1]) for task, values in totals.items()}


def fmt_rate(row: dict[str, str], field: str) -> str:
    return row[field] or "—"


def fmt_result(stats: dict[str, tuple[int, int]], task: str) -> str:
    successes, total = stats.get(task, (0, 0))
    return f"{successes}/{total}" if total else "—"


def main() -> int:
    try:
        manifest = json.JSONDecoder().decode(TASKS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{TASKS_PATH}: invalid JSON: {exc.msg}") from exc
    task_order = [item["task"] for item in manifest["tasks"]]
    if len(task_order) != len(set(task_order)):
        raise ValueError("task manifest contains duplicates")
    rates = load_rates(task_order)
    v1_paths = glob.glob(V1_GLOB)
    v3_paths = glob.glob(V3_GLOB)
    if not v1_paths:
        raise ValueError("no v1 heldout rows found")
    if not v3_paths:
        raise ValueError("no v3 slice rows found")
    v1_stats = aggregate(load_jsonl(v1_paths))
    v3_by_arm: dict[str, dict[str, tuple[int, int]]] = {}
    for path in sorted(v3_paths):
        name = Path(path).name
        prefix = "miniwob-jev-v3-"
        arm = name[len(prefix) : -len(".s0.jsonl")]
        rows = load_jsonl([path])
        stats = aggregate(rows)
        unknown = set(stats) - set(task_order)
        if unknown:
            raise ValueError(f"{name}: tasks absent from manifest: {sorted(unknown)}")
        v3_by_arm[arm] = stats

    published = sum(bool(row["human_success_rate"]) for row in rates.values())
    print(
        f"external-rates: {len(task_order)} manifest tasks; {published} published rows; {len(task_order) - published} blank rows"
    )
    print(
        "source: Humphreys et al. (2022), Table 3, PDF pp. 14-15; no network or Jev calls"
    )
    for arm, stats in v3_by_arm.items():
        print(f"\narm={arm}")
        print(
            "task\thuman\tcc_net\taggregated_sota_bc_rl\taggregated_sota_augmented\tv1_success\tv3_success\tversion_match"
        )
        for task in task_order:
            if task not in stats:
                continue
            row = rates[task]
            print(
                "\t".join(
                    (
                        task,
                        fmt_rate(row, "human_success_rate"),
                        fmt_rate(row, "cc_net_mean_score"),
                        fmt_rate(row, "aggregated_sota_bc_rl"),
                        fmt_rate(row, "aggregated_sota_augmented"),
                        fmt_result(v1_stats, task),
                        fmt_result(stats, task),
                        row["source_version_match"],
                    )
                )
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
