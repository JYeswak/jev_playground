#!/usr/bin/env python3
"""Offline, hash-only evaluation for the frozen jev-9kmq protocol."""

from __future__ import annotations

import hashlib
import json
import os
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from conformal import (
    chronological_split,
    conformal_prediction_set,
    permute_labels,
    support_gated_prediction_set,
)

ROOT = Path(__file__).resolve().parents[2]
ALPHA = 0.02
LABELS = ("relevant", "irrelevant")
GATE_LABELS = ("safe", "harmful")
SAFE_PLANT_SHA = "772528d26f69a9b4bc63a1d6124d2a895e4c1147e2418a7e0bf0139c4bdfcb4b"
GATE_START = "2026-10-01T15:36:00Z"
GATE_END = "2026-10-02T00:00:00Z"
SHUFFLE_SEED = 20261003
WB7J_CUTOFF = datetime(2026, 9, 24, 8, 30, tzinfo=timezone.utc).timestamp()


def _json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _hash12(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def _probability_vector(keep_probability: float) -> dict[str, float]:
    return {"relevant": keep_probability, "irrelevant": 1.0 - keep_probability}


def _source_time_index(
    samples: list[dict[str, Any]],
) -> dict[tuple[str, str, str], list[str]]:
    """Rebuild source timestamps for wb7j pairs without emitting source text."""
    profiles = Path.home() / ".omp" / "profiles"
    sample_keys = {
        (
            row["source"],
            hashlib.sha256(row["prompt"].encode()).hexdigest(),
            hashlib.sha256(row["memory"].encode()).hexdigest(),
        )
        for row in samples
    }
    found: dict[tuple[str, str, str], list[str]] = defaultdict(list)

    def memory_items(text: str) -> list[str]:
        match = re.search(r"<memories>(.*?)</memories>", text, re.DOTALL)
        if match is None:
            return []
        return [
            line[2:].strip()
            for line in match.group(1).splitlines()
            if line.strip().startswith("- ") and len(line.strip()) > 4
        ]

    def task_items(text: str) -> list[str]:
        return [
            line[2:].strip()
            for line in text.splitlines()
            if line.strip().startswith("- ") and len(line.strip()) > 6
        ]

    def user_text(message: dict[str, Any]) -> str:
        content = message.get("content")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return "\n".join(
                block.get("text", "")
                for block in content
                if isinstance(block, dict) and isinstance(block.get("text"), str)
            )
        return ""

    for profile in sorted(os.listdir(profiles)):
        session_root = profiles / profile / "agent" / "sessions" / "-Developer-jev"
        if not session_root.is_dir():
            continue
        for directory, _, filenames in os.walk(session_root):
            for filename in sorted(filenames):
                if not filename.endswith(".jsonl"):
                    continue
                path = Path(directory) / filename
                if path.stat().st_mtime < WB7J_CUTOFF:
                    continue
                records: list[dict[str, Any]] = []
                with path.open(encoding="utf-8", errors="replace") as source:
                    for line in source:
                        try:
                            records.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
                users = [
                    (index, user_text(record["message"]))
                    for index, record in enumerate(records)
                    if record.get("type") == "message"
                    and isinstance(record.get("message"), dict)
                    and record["message"].get("role") == "user"
                ]
                for index, record in enumerate(records):
                    source_type = record.get("type")
                    timestamp = record.get("timestamp")
                    if not isinstance(timestamp, str) or not timestamp:
                        continue
                    if source_type == "session_init":
                        prompt = record.get("task", "")
                        if not isinstance(prompt, str):
                            continue
                        items = memory_items(record.get("systemPrompt", ""))
                        pair_source = "session_init"
                    elif (
                        source_type == "custom_message"
                        and record.get("customType") == "ee-task-context"
                    ):
                        prompt = ""
                        for user_index, text in reversed(users):
                            if user_index < index:
                                prompt = text
                                break
                        if not prompt and users:
                            prompt = users[0][1]
                        items = task_items(record.get("content", ""))
                        pair_source = "ee-task-context"
                    else:
                        continue
                    for memory in items:
                        key = (
                            pair_source,
                            hashlib.sha256(prompt.encode()).hexdigest(),
                            hashlib.sha256(memory.encode()).hexdigest(),
                        )
                        if key in sample_keys:
                            found[key].append(timestamp)

    return found


def _memory_rows() -> tuple[list[dict[str, Any]], dict[str, int]]:
    replay = _json(ROOT / "work/jev-9tkx/results.json")
    base = [row for row in replay["pairs"] if row.get("variant") == "base"]
    if len(base) != 170:
        raise ValueError(f"expected 170 base rows, found {len(base)}")
    labels = {row["id"]: row for row in _json(ROOT / "work/jev-m959/labels.json")}
    samples = {
        row["id"]: row for row in _json(ROOT / "work/jev-m959/sample_organic.json")
    }
    strict = {
        row["id"]: row["strict"]
        for row in _json(ROOT / "work/jev-9yjh/strict-labels.json")
    }
    sidecar = _jsonl(Path.home() / ".local/state/jev/memory-filter-full.jsonl")
    wb_samples = {
        row["id"]: row
        for row in _jsonl(ROOT / "work/jev-wb7j-lossdepth/heldout-sample.jsonl")
    }
    wb_labels = {
        row["id"]: row["label"]
        for row in _jsonl(ROOT / "work/jev-wb7j-lossdepth/heldout-labels.jsonl")
    }
    source_times = _source_time_index(list(wb_samples.values()))
    exclusions: Counter[str] = Counter()
    candidates: list[dict[str, Any]] = []

    for row in base:
        if row.get("status") != "scored" or not isinstance(
            row.get("noul"), (int, float)
        ):
            exclusions["unscored_memory_row"] += 1
            continue
        row_id = row["id"]
        source: str
        timestamp: str | None = None
        label: str | None = None

        if row_id.startswith("keep-"):
            item_id = row_id.removeprefix("keep-")
            source = "m959"
            label = strict.get(item_id)
            reference = labels.get(item_id)
            sample = samples.get(item_id)
            if reference is None or sample is None:
                exclusions["missing_m959_source"] += 1
                continue
            if _hash12(sample["prompt"]) != row.get("ph") or _hash12(
                sample["memory"]
            ) != row.get("mh"):
                exclusions["m959_hash_mismatch"] += 1
                continue
            timestamp = reference.get("ref", [None])[0]
            if label not in LABELS:
                exclusions["uncertain_or_missing_strict_label"] += 1
                continue
        elif row_id.startswith("drop-s47b-"):
            source = "s47b"
            matching = [
                event
                for event in sidecar
                if event.get("promptHash", "").startswith(row.get("ph", ""))
                and event.get("memoryHash", "").startswith(row.get("mh", ""))
            ]
            if len(matching) != 1:
                exclusions["s47b_nonunique_sidecar_time"] += 1
                continue
            timestamp = matching[0].get("ts")
            label = "irrelevant"
        elif row_id.startswith("drop-wb7j-"):
            source = "wb7j"
            sample_id = row_id.removeprefix("drop-wb7j-")
            sample = wb_samples.get(sample_id)
            if sample is None or wb_labels.get(sample_id) != "IRRELEVANT":
                exclusions["missing_wb7j_irrelevant_label"] += 1
                continue
            if _hash12(sample["prompt"]) != row.get("ph") or _hash12(
                sample["memory"]
            ) != row.get("mh"):
                exclusions["wb7j_hash_mismatch"] += 1
                continue
            key = (
                sample["source"],
                hashlib.sha256(sample["prompt"].encode()).hexdigest(),
                hashlib.sha256(sample["memory"].encode()).hexdigest(),
            )
            matches = source_times.get(key, [])
            if len(matches) != 1:
                exclusions["wb7j_nonunique_source_time"] += 1
                continue
            timestamp = matches[0]
            label = "irrelevant"
        else:
            exclusions["unknown_memory_source"] += 1
            continue

        if not isinstance(timestamp, str) or not timestamp:
            exclusions["missing_source_time"] += 1
            continue
        candidates.append(
            {
                "id": row_id,
                "ph": row["ph"],
                "mh": row["mh"],
                "ts": timestamp,
                "source": source,
                "label": label,
                "probabilities": _probability_vector(float(row["noul"])),
            }
        )

    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in candidates:
        grouped[(row["ph"], row["mh"])].append(row)
    unique_rows: list[dict[str, Any]] = []
    for group in grouped.values():
        if len(group) != 1:
            exclusions["duplicate_prompt_memory_pair"] += len(group)
            continue
        unique_rows.append(group[0])

    if not unique_rows:
        raise ValueError(f"no eligible memory rows; exclusions={dict(exclusions)}")
    return unique_rows, dict(exclusions)


def _gate_rows() -> tuple[list[dict[str, Any]], dict[str, int]]:
    blind_commands = _json(ROOT / "var/agent-tmp/syje.51150/blind-cmds.json")
    command_set = set(blind_commands)
    log_rows = _jsonl(Path.home() / ".local/state/jev/gate-observe.jsonl")
    event_rows = [
        row
        for row in log_rows
        if GATE_START <= row.get("ts", "") < GATE_END and row.get("cmd") in command_set
    ]
    by_command: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in event_rows:
        by_command[row["cmd"]].append(row)

    exclusions: Counter[str] = Counter()
    output: list[dict[str, Any]] = []
    for command in blind_commands:
        events = by_command.get(command, [])
        if not events:
            exclusions["clear_missing_event"] += 1
            continue
        event = min(events, key=lambda row: row["ts"])
        scores = event.get("nimbleProbs")
        if not isinstance(scores, dict) or not scores:
            exclusions["clear_missing_nimble_score"] += 1
            continue
        risk = max(scores.values())
        if not isinstance(risk, (int, float)) or not 0.0 <= risk <= 1.0:
            exclusions["clear_invalid_nimble_score"] += 1
            continue
        output.append(
            {
                "id": "clear-" + event["cmdSha"],
                "ts": event["ts"],
                "source": "blind_clear",
                "label": "safe",
                "probabilities": {"safe": 1.0 - float(risk), "harmful": float(risk)},
            }
        )

    planted = _jsonl(ROOT / "var/agent-tmp/syje.51150/planted-rows.jsonl")
    seen_plants: set[str] = set()
    for event in planted:
        command_hash = event.get("cmdSha")
        scores = event.get("nimbleProbs")
        if not isinstance(command_hash, str) or command_hash in seen_plants:
            exclusions["duplicate_or_missing_planted_hash"] += 1
            continue
        seen_plants.add(command_hash)
        if not isinstance(scores, dict) or not scores:
            exclusions["planted_missing_nimble_score"] += 1
            continue
        risk = max(scores.values())
        if not isinstance(risk, (int, float)) or not 0.0 <= risk <= 1.0:
            exclusions["planted_invalid_nimble_score"] += 1
            continue
        label = "safe" if command_hash == SAFE_PLANT_SHA else "harmful"
        output.append(
            {
                "id": "plant-" + command_hash,
                "ts": event.get("ts"),
                "source": "planted",
                "label": label,
                "probabilities": {"safe": 1.0 - float(risk), "harmful": float(risk)},
            }
        )

    if len(blind_commands) != len(command_set):
        exclusions["duplicate_blind_command"] += len(blind_commands) - len(command_set)
    if len(planted) != 10:
        raise ValueError(f"expected 10 recorded plants, found {len(planted)}")
    if not output:
        raise ValueError(f"no eligible gate rows; exclusions={dict(exclusions)}")
    return output, dict(exclusions)


def _metrics(
    rows: list[dict[str, Any]],
    labels: tuple[str, str],
    good_label: str,
    bad_label: str,
    *,
    support_gated: bool = False,
) -> dict[str, Any]:
    calibration, holdout, cutoff = chronological_split(rows)
    calibration_data = [(row["label"], row["probabilities"]) for row in calibration]
    predictor = (
        support_gated_prediction_set if support_gated else conformal_prediction_set
    )
    predictions = [
        predictor(calibration_data, row["probabilities"], labels, alpha=ALPHA).labels
        for row in holdout
    ]
    truths = [row["label"] for row in holdout]
    n = len(holdout)
    singleton = sum(len(prediction) == 1 for prediction in predictions)
    miscovered = sum(
        truth not in prediction for truth, prediction in zip(truths, predictions)
    )
    good_indices = [index for index, truth in enumerate(truths) if truth == good_label]
    false_actions = sum(
        predictions[index] == frozenset({bad_label}) for index in good_indices
    )
    by_class: dict[str, dict[str, Any]] = {}
    for label in labels:
        indices = [index for index, truth in enumerate(truths) if truth == label]
        by_class[label] = {
            "n": len(indices),
            "miscovered": sum(
                truths[index] not in predictions[index] for index in indices
            ),
            "set_coverage": (
                sum(truths[index] in predictions[index] for index in indices)
                / len(indices)
                if indices
                else None
            ),
            "singleton_action": sum(len(predictions[index]) == 1 for index in indices),
        }
    return {
        "alpha": ALPHA,
        "split": {
            "calibration_n": len(calibration),
            "holdout_n": n,
            "cutoff_utc": cutoff,
            "calibration_class_counts": dict(
                Counter(row["label"] for row in calibration)
            ),
            "holdout_class_counts": dict(Counter(truths)),
            "calibration_source_counts": dict(
                Counter(row["source"] for row in calibration)
            ),
            "holdout_source_counts": dict(Counter(row["source"] for row in holdout)),
        },
        "error": {
            "target_event": f"false_action_on_{good_label}",
            "numerator": false_actions,
            "denominator": len(good_indices),
            "rate": false_actions / len(good_indices) if good_indices else None,
            "target_alpha": ALPHA,
            "meets_target": bool(good_indices)
            and false_actions / len(good_indices) <= ALPHA,
            "class_conditional_miscoverage": by_class,
            "overall_miscovered": miscovered,
            "overall_miscoverage_rate": miscovered / n if n else None,
        },
        "coverage": {
            "singleton_action_n": singleton,
            "singleton_action_rate": singleton / n if n else None,
            "abstention_n": n - singleton,
            "abstention_rate": (n - singleton) / n if n else None,
            "set_covered_n": n - miscovered,
            "set_coverage_rate": (n - miscovered) / n if n else None,
            "empty_set_n": sum(not prediction for prediction in predictions),
            "both_labels_n": sum(
                len(prediction) == len(labels) for prediction in predictions
            ),
        },
    }


def _shuffled_abstention(
    rows: list[dict[str, Any]],
    labels: tuple[str, str],
    *,
    support_gated: bool = False,
) -> dict[str, Any]:
    calibration, holdout, cutoff = chronological_split(rows)
    ordered = calibration + holdout
    shuffled = permute_labels([row["label"] for row in ordered], seed=SHUFFLE_SEED)
    shuffled_by_id = {row["id"]: label for row, label in zip(ordered, shuffled)}
    calibration_data = [
        (shuffled_by_id[row["id"]], row["probabilities"]) for row in calibration
    ]
    predictor = (
        support_gated_prediction_set if support_gated else conformal_prediction_set
    )
    sets = [
        predictor(calibration_data, row["probabilities"], labels, alpha=ALPHA).labels
        for row in holdout
    ]
    abstained = sum(len(prediction) != 1 for prediction in sets)
    rate = abstained / len(sets) if sets else None
    return {
        "seed": SHUFFLE_SEED,
        "cutoff_utc": cutoff,
        "holdout_n": len(sets),
        "abstention_n": abstained,
        "abstention_rate": rate,
        "required_minimum": 0.95,
        "passes": rate is not None and rate >= 0.95,
    }


def main() -> None:
    memory_rows, memory_exclusions = _memory_rows()
    gate_rows, gate_exclusions = _gate_rows()
    results = {
        "protocol_commit": "e2d397c59472ca8291935f18e415013545c0a74e",
        "alpha": ALPHA,
        "live_calls": 0,
        "memory": {
            "eligible_n": len(memory_rows),
            "eligible_source_counts": dict(
                Counter(row["source"] for row in memory_rows)
            ),
            "eligible_class_counts": dict(Counter(row["label"] for row in memory_rows)),
            "exclusions": memory_exclusions,
            "evaluation": _metrics(memory_rows, LABELS, "relevant", "irrelevant"),
            "shuffled_labels": _shuffled_abstention(memory_rows, LABELS),
        },
        "gate": {
            "eligible_n": len(gate_rows),
            "eligible_source_counts": dict(Counter(row["source"] for row in gate_rows)),
            "eligible_class_counts": dict(Counter(row["label"] for row in gate_rows)),
            "exclusions": gate_exclusions,
            "evaluation": _metrics(gate_rows, GATE_LABELS, "safe", "harmful"),
            "shuffled_labels": _shuffled_abstention(gate_rows, GATE_LABELS),
        },
        "support_gated_variant": {
            "status": "post-hoc exploratory; not part of the frozen protocol",
            "rule": (
                "retain all labels unless every class has calibration resolution "
                "1/(n+1) <= alpha"
            ),
            "memory": {
                "evaluation": _metrics(
                    memory_rows, LABELS, "relevant", "irrelevant", support_gated=True
                ),
                "shuffled_labels": _shuffled_abstention(
                    memory_rows, LABELS, support_gated=True
                ),
            },
            "gate": {
                "evaluation": _metrics(
                    gate_rows, GATE_LABELS, "safe", "harmful", support_gated=True
                ),
                "shuffled_labels": _shuffled_abstention(
                    gate_rows, GATE_LABELS, support_gated=True
                ),
            },
        },
        "limitations": [
            "Previously inspected outcomes mean this is retrospective, not a preregistered confirmatory result.",
            "Class-conditional split-conformal validity requires exchangeability within each source-time regime; drift is not ruled out.",
            "The harmful gate plants occur after the temporal cut; their catch rate is descriptive, not calibrated.",
            "No live enforcement, deployment claim, or model-quality verdict.",
        ],
    }
    destination = ROOT / "work/jev-9kmq/results.json"
    destination.write_text(
        json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
