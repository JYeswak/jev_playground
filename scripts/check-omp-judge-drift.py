#!/usr/bin/env python3
"""Fail closed when recorded omp judge usage drifts from the pinned Jev model."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

EXPECTED_MODEL = "jev-1.13.0"


def read_models(path: Path) -> list[tuple[int, str | None]]:
    models: list[tuple[int, str | None]] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), 1
    ):
        if not line.strip():
            continue
        try:
            row: Any = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number} is not valid JSON") from exc
        if not isinstance(row, dict):
            raise TypeError(f"{path}:{line_number} is not an object")
        model = row.get("model_id", row.get("model"))
        models.append((line_number, model if isinstance(model, str) else None))
    return models


def check(path: Path, expected: str = EXPECTED_MODEL) -> tuple[bool, str]:
    models = read_models(path)
    if not models:
        return False, f"{path}: no model_usage rows"
    drift = [(line, model) for line, model in models if model != expected]
    if drift:
        details = ", ".join(f"line {line}: {model!r}" for line, model in drift)
        return False, f"judge model drift: expected {expected!r}; {details}"
    return True, f"judge model pinned: {expected} ({len(models)} rows)"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("usage", type=Path)
    parser.add_argument("--expected", default=EXPECTED_MODEL)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        cases = {
            "matching": json.dumps({"model_id": "jev-1.13.0"}) + "\n",
            "drift": json.dumps({"model_id": "jev-latest"}) + "\n",
            "missing": json.dumps({"usage": 1}) + "\n",
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "matching.jsonl").write_text(cases["matching"])
            (root / "drift.jsonl").write_text(cases["drift"])
            (root / "missing.jsonl").write_text(cases["missing"])
            for name, expected in (
                ("matching", True),
                ("drift", False),
                ("missing", False),
            ):
                actual = check(root / f"{name}.jsonl")[0]
                if actual != expected:
                    raise AssertionError(
                        f"selftest case {name} expected {expected}, got {actual}"
                    )
        print("SELFTEST PASS: matching, drift, and missing-model plants")
        return 0
    try:
        ok, message = check(args.usage, args.expected)
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        print(f"judge drift check error: {exc}", file=sys.stderr)
        return 2
    print(message, file=sys.stderr if not ok else sys.stdout)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
