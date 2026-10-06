#!/usr/bin/env python3
"""Recompute the frozen d1-read cut on recorded rows; never calls a model."""

from __future__ import annotations

import json
import math
import sys
from collections import Counter
from pathlib import Path

CUT = 0.85


def score(path: Path) -> dict[str, object]:
    confusion = Counter()
    row_count = 0
    truth_read = 0

    with path.open(encoding="utf-8") as rows_file:
        for line_number, line in enumerate(rows_file, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"line {line_number}: invalid JSON") from exc
            if not isinstance(row, dict) or row.get("ok") is not True:
                raise ValueError(f"line {line_number}: expected a successful recorded answer")

            choice = row.get("choice")
            confidence = row.get("conf")
            label = row.get("label")
            if not isinstance(choice, str) or not choice:
                raise ValueError(f"line {line_number}: missing choice")
            if (
                isinstance(confidence, bool)
                or not isinstance(confidence, (int, float))
                or not math.isfinite(confidence)
                or not 0 <= confidence <= 1
            ):
                raise ValueError(f"line {line_number}: conf must be finite and in [0, 1]")
            if not isinstance(label, str) or not label:
                raise ValueError(f"line {line_number}: missing label")

            probability_read = confidence if choice == "read" else 1 - confidence
            predicted_read = probability_read >= CUT
            actual_read = label == "read"
            truth_read += actual_read
            row_count += 1
            if predicted_read and actual_read:
                confusion["TP"] += 1
            elif predicted_read:
                confusion["FP"] += 1
            elif actual_read:
                confusion["FN"] += 1
            else:
                confusion["TN"] += 1

    if not row_count:
        raise ValueError("no usable rows")
    tn, fn, fp, tp = (confusion[key] for key in ("TN", "FN", "FP", "TP"))
    return {
        "rows": row_count,
        "tn": tn,
        "fn": fn,
        "fp": fp,
        "tp": tp,
        "accuracy": (tn + tp) / row_count,
        "always_not_read": (row_count - truth_read) / row_count,
        "read_recall": tp / truth_read if truth_read else 0.0,
        "truth_read": truth_read,
        "cut": CUT,
    }


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {Path(sys.argv[0]).name} ROWS.jsonl", file=sys.stderr)
        return 64
    try:
        result = score(Path(sys.argv[1]))
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"rows={result['rows']}")
    print(f"cut={result['cut']:.2f}")
    print(
        "confusion(TN/FN/FP/TP)="
        f"{result['tn']}/{result['fn']}/{result['fp']}/{result['tp']}"
    )
    print(f"accuracy={result['accuracy']:.3f}")
    print(f"always_not_read={result['always_not_read']:.3f}")
    print(f"read_recall={result['tp']}/{result['truth_read']}={result['read_recall']:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
