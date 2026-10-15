#!/usr/bin/env python3
"""Offline D2 reference reconciliation authorized by J-2026-10-15-07.

Uses only frozen JSONL rows; never imports run.py or the JavaScript test.
Default: emit deterministic JSON. --output PATH: write it. --check PATH:
re-derive and compare every value and provenance field, without a tolerance.
This is post-observation reconciliation, not a prospective quality win.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
IMPLEMENTATION = Path(__file__).resolve()
SOURCE = "work/choice-banking77/full.jsonl"
JEV = "work/choice-banking77/rows-full-jev.jsonl"
CLEF_DEV = "work/local-decision-arms/rows-clefflash-dev.jsonl"
CLEF_HELD = "work/local-decision-arms/rows-clefflash.jsonl"
RUN = "work/local-decision-arms/run.py"
INPUTS = (SOURCE, JEV, CLEF_DEV, CLEF_HELD, RUN)
FLOOR = 0.005
CLIP = 0.0001
ITERATIONS = 2000
LEARNING_RATE = 0.1
BINS = 10
Row = dict[str, Any]
Pair = tuple[float, int]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def compact(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def unique_object(pairs: list[tuple[str, Any]]) -> Row:
    result: Row = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def rows(data: bytes, name: str) -> list[Row]:
    result = []
    for line in data.decode("utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line, object_pairs_hook=unique_object)
        if not isinstance(row, dict):
            raise TypeError(f"{name}: expected JSON objects")
        result.append(row)
    return result


def ids(records: list[Row], name: str, source: list[Row]) -> set[int]:
    found: set[int] = set()
    for row in records:
        index = row.get("i")
        if type(index) is not int or not 0 <= index < len(source):
            raise ValueError(f"{name}: invalid source index {index!r}")
        if index in found:
            raise ValueError(f"{name}: duplicate source index {index}")
        if row.get("intent") != source[index]["intent"]:
            raise ValueError(f"{name}: source intent mismatch at index {index}")
        if "error" in row:
            raise ValueError(f"{name}: error row at index {index}")
        found.add(index)
    return found


def probability(value: Any) -> float:
    if isinstance(value, bool) or value is None:
        raise ValueError("missing or boolean probability")
    p = float(value)
    if not math.isfinite(p) or not 0 <= p <= 1:
        raise ValueError("probability must be finite and within [0, 1]")
    return p


def logit(p: float) -> float:
    clipped = min(max(p, CLIP), 1 - CLIP)
    return math.log(clipped / (1 - clipped))


def fit(dev: list[Pair]) -> tuple[float, float]:
    # Precompute only DEV logits; full-batch updates retain file-order sums.
    xs = [(logit(p), correct) for p, correct in dev]
    a, b = 1.0, 0.0
    for _ in range(ITERATIONS):
        ga = gb = 0.0
        for x, correct in xs:
            predicted = 1 / (1 + math.exp(-(a * x + b)))
            residual = predicted - correct
            ga += residual * x
            gb += residual
        a -= LEARNING_RATE * ga / len(xs)
        b -= LEARNING_RATE * gb / len(xs)
    return a, b


def held_metrics(pairs: list[Pair]) -> Row:
    counts = [0] * BINS
    confidence_sums = [0.0] * BINS
    correct_counts = [0] * BINS
    for p, correct in pairs:
        index = min(math.floor(p * BINS), BINS - 1)
        counts[index] += 1
        confidence_sums[index] += p
        correct_counts[index] += correct
    ece = 0.0
    for count, total, correct in zip(counts, confidence_sums, correct_counts):
        if count:
            ece += count / len(pairs) * abs(total / count - correct / count)
    return {
        "held_ece": repr(ece),
        "bin_counts": counts,
        "bin_confidence_sums": [repr(value) for value in confidence_sums],
        "bin_correct_counts": correct_counts,
        "held_correct_count": sum(correct_counts),
    }


def calibrate(dev: list[Row], held: list[Row], labels: dict[str, str],
              intents: set[str], *, is_jev: bool) -> Row:
    floored_rows = 0
    floored_entries = 0

    def pair(row: Row) -> Pair:
        nonlocal floored_rows, floored_entries
        if is_jev:
            vector = row.get("probabilities")
            if not isinstance(vector, dict) or not vector:
                raise ValueError(f"Jev index {row['i']}: missing probability vector")
            normalized_keys = {labels.get(key, key) for key in vector}
            if len(vector) != len(intents) or normalized_keys != intents:
                raise ValueError(f"Jev index {row['i']}: incomplete label vector")
            # Dict insertion order is the frozen vector's JSON file order.
            total = 0.0
            maximum = -1.0
            bound = 0
            for raw in vector.values():
                p = probability(raw)
                value = max(p, FLOOR)
                bound += int(value != p)
                total += value
                maximum = max(maximum, value)
            confidence = maximum / total
            choice = labels.get(row["choice"], row["choice"])
        else:
            p = probability(row.get("p_choice"))
            confidence = max(p, FLOOR)
            bound = int(p < FLOOR)
            choice = row["choice"]
        if choice not in intents:
            raise ValueError(f"index {row['i']}: unknown chosen intent")
        floored_rows += int(bound > 0)
        floored_entries += bound
        # Correctness is the recorded choice, not a recomputed vector argmax.
        return confidence, int(choice == row["intent"])

    dev_pairs = [pair(row) for row in dev]
    a, b = fit(dev_pairs)
    # HELD is transformed only after the DEV fit has completed.
    held_pairs = []
    for row in held:
        confidence, correct = pair(row)
        calibrated = 1 / (1 + math.exp(-(a * logit(confidence) + b)))
        held_pairs.append((calibrated, correct))
    return {
        "platt_a": repr(a), "platt_b": repr(b),
        "dev_count": len(dev), "held_count": len(held),
        "dev_correct_count": sum(correct for _, correct in dev_pairs),
        "floored_rows": floored_rows, "floored_entries": floored_entries,
        **held_metrics(held_pairs),
    }


def derive() -> Row:
    data = {name: (ROOT / name).read_bytes() for name in INPUTS}
    source = rows(data[SOURCE], SOURCE)
    if len(source) != 3080 or any(row.get("i") != i for i, row in enumerate(source)):
        raise ValueError("expected 3080 source rows indexed in file order")
    intents = {row["intent"] for row in source}
    if len(intents) != 77:
        raise ValueError("expected Banking77's 77 intents")
    labels = {c.replace("_", " ").lower(): c
              for c in sorted(intents, key=lambda c: (c.casefold(), c))}
    jev = rows(data[JEV], JEV)
    dev = rows(data[CLEF_DEV], CLEF_DEV)
    held = rows(data[CLEF_HELD], CLEF_HELD)
    dev_ids = ids(dev, CLEF_DEV, source)
    held_ids = ids(held, CLEF_HELD, source)
    if ids(jev, JEV, source) != set(range(len(source))):
        raise ValueError("Jev rows do not cover the complete source")
    expected_held = set(random.Random(7).sample(range(len(source)), 600))
    remaining = sorted(set(range(len(source))) - expected_held)
    expected_dev = set(random.Random(8).sample(remaining, 200))
    if held_ids != expected_held or dev_ids != expected_dev or dev_ids & held_ids:
        raise ValueError("Clef ids disagree with seed7 SAMPLE600 / seed8 DEV200")
    jev_metrics = calibrate([r for r in jev if r["i"] in dev_ids],
                            [r for r in jev if r["i"] in held_ids],
                            labels, intents, is_jev=True)
    clef_metrics = calibrate(dev, held, labels, intents, is_jev=False)
    return {
        "schema_version": "d2-reference.v1",
        "authorization": {
            "decision": "J-2026-10-15-07",
            "source": "AM56011 / jev-9odh comment3695",
            "kind": "post_observation_reference_reconciliation",
        },
        "data_scope": {
            "population": "committed Banking77 record ids; not rolling fleet traffic",
            "event_window": None,
            "event_window_status": "event timestamps absent from these recorded schemas",
            "time_filter": "none; frozen source hashes and DEV/held ids define the population",
            "probability_source": "raw probability entries, not row.confidence; no pre-normalization",
            "jev_recorded_models": sorted({str(row.get("model")) for row in jev}),
            "clef_recorded_arms": sorted({str(row.get("arm")) for row in dev + held}),
            "clef_resolved_backend_model": "not recorded; arm name does not resolve serving identity",
        },
        "method": {
            "floor": "0.005", "renormalize": True,
            "platt_iterations": ITERATIONS, "platt_learning_rate": "0.1",
            "initial_a": "1", "initial_b": "0", "logit_clip": "0.0001",
            "ece_bins": BINS, "dev_count": 200, "held_count": 600,
            "held_seed": 7, "dev_seed": 8,
            "jev_confidence": "max(floor_each_vector_entry) / sum(floor_each_vector_entry)",
            "clef_confidence": "max(p_choice, 0.005); no vector available",
            "correctness": "normalized Jev row.choice == row.intent; Clef row.choice == row.intent",
            "fit_split": "DEV only", "sum_order": "input file order; ECE bins ascending",
            "arithmetic": "Python binary64; math.log and math.exp; decimal strings use repr",
            "id_hash_encoding": "UTF-8 compact JSON sorted integer id list; no newline",
        },
        "inputs": [{"path": name, "sha256": sha256(data[name])} for name in INPUTS],
        "derivation": {
            "implementation_path": IMPLEMENTATION.relative_to(ROOT).as_posix(),
            "implementation_sha256": sha256(IMPLEMENTATION.read_bytes()),
            "runtime": {
                "python": sys.version.split()[0],
                "implementation": sys.implementation.name,
                "platform": sys.platform,
                "cross_runtime_bit_identity": "not claimed; frozen .002 consumer tolerance unchanged",
            },
            "source_count": len(source), "intent_count": len(intents),
            "jev_source_count": len(jev), "seed_splits_verified": True,
            "dev_ids_sha256": sha256(compact(sorted(dev_ids)).encode("utf-8")),
            "held_ids_sha256": sha256(compact(sorted(held_ids)).encode("utf-8")),
            "jev": jev_metrics, "clef": clef_metrics,
        },
        "reference": {
            "jev_held_ece": jev_metrics["held_ece"], "absolute_tolerance": "0.002",
        },
        "historical": {
            "scalar_reference": "0.0276", "absolute_tolerance": "0.002",
            "prior_full_vector_held_ece_recorded": "0.0317",
            "prior_full_vector_result": "FAIL",
            "interpretation": "Historical FAIL remains; authorized post-observation reference reconciliation, not a prospective quality win.",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--output", type=Path, help="write derived JSON instead of stdout")
    mode.add_argument("--check", type=Path, help="re-derive and require exact artifact agreement")
    args = parser.parse_args()
    try:
        result = derive()
        if args.check is not None:
            artifact = json.loads(args.check.read_text(encoding="utf-8"),
                                  object_pairs_hook=unique_object)
            if compact(artifact) != compact(result):
                raise ValueError("reference/provenance disagreement with independent re-derivation")
            print(json.dumps({"status": "OK", "checked": args.check.as_posix(),
                              "jev_held_ece": result["reference"]["jev_held_ece"]},
                             sort_keys=True))
        else:
            rendered = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
            if args.output is None:
                sys.stdout.write(rendered)
            else:
                protected = {(ROOT / name).resolve() for name in INPUTS} | {IMPLEMENTATION}
                if args.output.resolve() in protected:
                    raise ValueError("output must not overwrite an input or this implementation")
                args.output.write_text(rendered, encoding="utf-8")
        return 0
    except (OSError, ValueError, KeyError, TypeError, OverflowError) as error:
        print(f"REFUSE: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
