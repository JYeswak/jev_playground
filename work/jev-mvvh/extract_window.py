#!/usr/bin/env python3
"""Freeze a timestamp-bounded, schema-validated memory-filter JSONL window."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import BinaryIO

LOG_SCHEMA = "jev-memory-filter.v1"
DEFAULT_INPUT = Path("~/.local/state/jev/memory-filter.jsonl").expanduser()
DEFAULT_OUTPUT = Path(__file__).with_name("window-20261002.jsonl")


@dataclass(frozen=True)
class Extraction:
    rows: int
    byte_count: int
    sha256: str


def parse_instant(value: str) -> datetime:
    """Parse an ISO-8601/RFC3339 instant and refuse timezone-free values."""
    try:
        instant = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"invalid timestamp: {value!r}") from exc
    if instant.tzinfo is None or instant.utcoffset() is None:
        raise ValueError(f"timestamp must include a timezone: {value!r}")
    return instant


def _row_instant(raw_line: bytes, line_number: int) -> datetime:
    try:
        row = json.loads(raw_line)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid JSONL row at line {line_number}") from exc
    if not isinstance(row, dict):
        raise ValueError(f"expected JSON object at line {line_number}")
    if row.get("schema") != LOG_SCHEMA:
        raise ValueError(f"unexpected schema at line {line_number}")
    timestamp = row.get("ts")
    if not isinstance(timestamp, str):
        raise ValueError(f"missing string ts at line {line_number}")
    try:
        return parse_instant(timestamp)
    except ValueError as exc:
        raise ValueError(f"invalid ts at line {line_number}: {exc}") from exc


def _write_once_or_identical(path: Path, content: bytes) -> None:
    """Create a generated artifact once; allow identical deterministic reruns."""
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError:
        if path.read_bytes() != content:
            raise FileExistsError(f"refusing to replace non-identical artifact: {path}")
        return
    with os.fdopen(fd, "wb") as output:
        output.write(content)
        output.flush()
        os.fsync(output.fileno())


def _copy_selected_rows(
    source: BinaryIO, start: datetime, end: datetime
) -> tuple[bytes, int]:
    selected = bytearray()
    count = 0
    for line_number, raw_line in enumerate(source, start=1):
        if not raw_line.strip():
            continue
        timestamp = _row_instant(raw_line, line_number)
        if start <= timestamp < end:
            selected.extend(raw_line)
            count += 1
    return bytes(selected), count


def extract_window(
    input_path: Path, output_path: Path, start: datetime, end: datetime
) -> Extraction:
    if start.tzinfo is None or start.utcoffset() is None:
        raise ValueError("window start must include a timezone")
    if end.tzinfo is None or end.utcoffset() is None:
        raise ValueError("window end must include a timezone")
    if start >= end:
        raise ValueError("window start must precede window end")

    with input_path.open("rb") as source:
        payload, rows = _copy_selected_rows(source, start, end)

    digest = hashlib.sha256(payload).hexdigest()
    receipt_path = output_path.with_suffix(".sha256")
    receipt = f"{digest}  {output_path.name}\n".encode("ascii")
    _write_once_or_identical(output_path, payload)
    _write_once_or_identical(receipt_path, receipt)
    return Extraction(rows=rows, byte_count=len(payload), sha256=digest)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--from", dest="from_ts", required=True, help="inclusive ISO-8601 instant"
    )
    parser.add_argument(
        "--to", dest="to_ts", required=True, help="exclusive ISO-8601 instant"
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        result = extract_window(
            args.input,
            args.output,
            parse_instant(args.from_ts),
            parse_instant(args.to_ts),
        )
    except (OSError, ValueError) as exc:
        print(f"extract_window: {exc}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "rows": result.rows,
                "bytes": result.byte_count,
                "sha256": result.sha256,
                "output": str(args.output),
                "receipt": str(args.output.with_suffix(".sha256")),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
