#!/usr/bin/env python3
"""Recompute the D headroom and G blind-label STOP gates from hash-only JSONL."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

_FIELDS = {"unit_sha256", "labeller", "label"}
_HASH = re.compile(r"[0-9a-f]{64}\Z")


def load_rows(path: Path) -> list[dict[str, str]]:
    """Load strictly scrubbed labels; refuse raw text and unexpected fields."""
    rows: list[dict[str, str]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number}: invalid JSON: {exc.msg}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"{path}:{line_number}: expected a JSON object")
        missing = _FIELDS - row.keys()
        extra = row.keys() - _FIELDS
        if missing:
            raise ValueError(f"{path}:{line_number}: missing fields: {', '.join(sorted(missing))}")
        if extra:
            raise ValueError(f"{path}:{line_number}: unexpected fields: {', '.join(sorted(extra))}")
        unit_sha256 = row["unit_sha256"]
        labeller = row["labeller"]
        label = row["label"]
        if not isinstance(unit_sha256, str) or not _HASH.fullmatch(unit_sha256):
            raise ValueError(f"{path}:{line_number}: unit_sha256 must be 64 lowercase hex characters")
        if not isinstance(labeller, str) or not labeller:
            raise ValueError(f"{path}:{line_number}: labeller must be a non-empty string")
        if not isinstance(label, str) or not label:
            raise ValueError(f"{path}:{line_number}: label must be a non-empty string")
        rows.append({"unit_sha256": unit_sha256, "labeller": labeller, "label": label})
    if not rows:
        raise ValueError(f"{path}: no label rows")
    return rows


def grouped_labels(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    """Build a unique unit-to-label map for each labeller."""
    grouped: dict[str, dict[str, str]] = defaultdict(dict)
    for row in rows:
        units = grouped[row["labeller"]]
        unit_sha256 = row["unit_sha256"]
        if unit_sha256 in units:
            raise ValueError(f"duplicate label for {unit_sha256} from {row['labeller']}")
        units[unit_sha256] = row["label"]
    return grouped


def report_d(rows: list[dict[str, str]]) -> None:
    """Recompute D's mechanical outcome prevalence and headroom."""
    grouped = grouped_labels(rows)
    required = {"HazySpring", "WildCarp", "mechanical"}
    if set(grouped) != required:
        raise ValueError(f"D requires labellers {sorted(required)}; got {sorted(grouped)}")
    unit_sets = [set(grouped[name]) for name in sorted(required)]
    if not unit_sets[0] == unit_sets[1] == unit_sets[2]:
        raise ValueError("D labellers do not cover the same units")
    labels = list(grouped["mechanical"].values())
    if any(label not in {"relevant", "not-relevant"} for label in labels):
        raise ValueError("D mechanical labels must be relevant or not-relevant")
    n = len(labels)
    if n != 50:
        raise ValueError(f"D requires 50 units, got {n}")
    relevant = labels.count("relevant")
    prevalence = relevant / n
    headroom = min(prevalence, 1 - prevalence)
    verdict = "STOP" if headroom < 0.15 else "PASS"
    print(
        f"D mechanical_prevalence={prevalence:.6f} ({relevant}/{n}); "
        f"headroom={headroom:.6f}; gate={verdict} (required >=0.15)"
    )


def report_g(rows: list[dict[str, str]]) -> None:
    """Recompute Cohen's kappa for the paired G blind labels."""
    grouped = grouped_labels(rows)
    required = {"HazySpring", "WildCarp"}
    if set(grouped) != required:
        raise ValueError(f"G requires labellers {sorted(required)}; got {sorted(grouped)}")
    hazy = grouped["HazySpring"]
    wild = grouped["WildCarp"]
    if set(hazy) != set(wild):
        raise ValueError("G labellers do not cover the same units")
    if any(label not in {"act", "pass"} for label in (*hazy.values(), *wild.values())):
        raise ValueError("G labels must be act or pass")
    n = len(hazy)
    if n != 50:
        raise ValueError(f"G requires 50 units, got {n}")
    observed_agreements = sum(hazy[unit] == wild[unit] for unit in hazy)
    observed = observed_agreements / n
    hazy_counts = Counter(hazy.values())
    wild_counts = Counter(wild.values())
    expected = sum(hazy_counts[label] * wild_counts[label] for label in ("act", "pass")) / (n * n)
    if expected >= 1:
        raise ValueError("G kappa is undefined when expected agreement is 1")
    kappa = (observed - expected) / (1 - expected)
    verdict = "STOP" if kappa < 0.60 else "PASS"
    print(
        f"G cohen_kappa={kappa:.6f}; n={n}; "
        f"agree={observed_agreements}/{n}; gate={verdict} (required >=0.60)"
    )


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print(f"usage: {Path(sys.argv[0]).name} LABELS.jsonl", file=sys.stderr)
        return 2
    path = Path(args[0])
    try:
        rows = load_rows(path)
        if any(row["labeller"] == "mechanical" for row in rows):
            report_d(rows)
        else:
            report_g(rows)
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
