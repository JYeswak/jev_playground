#!/usr/bin/env python3
"""Recompute the frozen smart-stop verdict from its sanitized case table."""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from pathlib import Path

HEADER = ["Case", "Timestamp UTC", "Original judge", "Noul", "Blind label", "Continued"]
POSITIVE_LABELS = {"promise", "promised-action"}
BORDERLINE_LABEL = "borderline-promise"
NEGATIVE_LABEL = "no-promise"


@dataclass(frozen=True)
class CaseRow:
    case: int
    noul: float
    label: str
    continued: bool


@dataclass(frozen=True)
class Summary:
    reasks: int
    p_strict: int
    p_loose: int
    y: int
    continued: int
    verdict: str


def parse_table(text: str) -> list[CaseRow]:
    """Parse the per-case Markdown table and reject incomplete or invalid rows."""
    lines = text.splitlines()
    header_index = next(
        (
            index
            for index, line in enumerate(lines)
            if line.lstrip().startswith("|")
            and [cell.strip() for cell in line.strip().strip("|").split("|")] == HEADER
        ),
        None,
    )
    if header_index is None or header_index + 1 >= len(lines):
        raise ValueError("per-case table header not found")

    separator = [
        cell.strip() for cell in lines[header_index + 1].strip().strip("|").split("|")
    ]
    if len(separator) != len(HEADER) or any(
        not cell or set(cell) - {"-", ":"} or "-" not in cell for cell in separator
    ):
        raise ValueError("per-case table separator is invalid")

    rows: list[CaseRow] = []
    for line_number, line in enumerate(
        lines[header_index + 2 :], start=header_index + 3
    ):
        if not line.strip():
            continue
        if not line.lstrip().startswith("|"):
            break
        parts = line.strip().strip("|").split("|")
        cells = [part.strip() for part in parts]
        if len(cells) != len(HEADER):
            raise ValueError(f"line {line_number}: expected 6 cells, got {len(cells)}")
        try:
            case = int(cells[0])
            noul = float(cells[3])
        except ValueError as error:
            raise ValueError(
                f"line {line_number}: invalid case number or Noul"
            ) from error
        if case != len(rows):
            raise ValueError(
                f"line {line_number}: expected case {len(rows)}, got {case}"
            )
        if not cells[1] or not cells[2]:
            raise ValueError(
                f"line {line_number}: timestamp and original judge are required"
            )
        if not math.isfinite(noul) or not 0 <= noul <= 1:
            raise ValueError(f"line {line_number}: Noul must be finite and in [0, 1]")
        if cells[4] not in {NEGATIVE_LABEL, BORDERLINE_LABEL, *POSITIVE_LABELS}:
            raise ValueError(f"line {line_number}: unknown blind label {cells[4]!r}")
        if cells[5] not in {"yes", "no"}:
            raise ValueError(f"line {line_number}: Continued must be yes or no")
        rows.append(CaseRow(case, noul, cells[4], cells[5] == "yes"))

    if not rows:
        raise ValueError("per-case table contains no data rows")
    return rows


def summarize_table(text: str) -> dict[str, int | str]:
    """Recompute P, Y, C and the preregistered verdict from table rows."""
    rows = parse_table(text)
    p_strict = sum(row.label in POSITIVE_LABELS for row in rows)
    p_loose = p_strict + sum(row.label == BORDERLINE_LABEL for row in rows)
    y = sum(row.noul >= 0.5 for row in rows)
    continued = sum(row.continued for row in rows)

    if y >= 5 and continued == 0:
        verdict = "(b)"
    elif p_strict >= 8 and y < p_strict / 2:
        verdict = "(c)"
    elif p_strict <= 3 and y <= 3:
        verdict = "(a)"
    else:
        verdict = "MIXED/UNDECIDED"

    return {
        "reasks": len(rows),
        "p_strict": p_strict,
        "p_loose": p_loose,
        "y": y,
        "continued": continued,
        "verdict": verdict,
    }


def render_report(result: dict[str, int | str]) -> str:
    """Render stable counts for the acceptance command and EVAL receipt."""
    report = (
        f"{result['reasks']} re-asks; P={result['p_strict']}"
        f" (loose={result['p_loose']}); Y={result['y']};"
        f" C={result['continued']}; verdict={result['verdict']}"
    )
    if result["p_strict"] == 0:
        report += (
            f"; recall unmeasured: 0 hand-labelled positives in {result['reasks']}"
        )
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "table", type=Path, help="sanitized smart-stop verdict Markdown"
    )
    args = parser.parse_args(argv)
    try:
        result = summarize_table(args.table.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(render_report(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
