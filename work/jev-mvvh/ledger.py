#!/usr/bin/env python3
"""Build per-surface cost/value reports.

Use --memory-input for a frozen memory-filter JSONL source and --end for the exclusive
ISO-8601 window end.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sqlite3
import subprocess
import sys
from collections.abc import Iterable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core import (
    EXPECTED_PATH,
    HARM_COSTS_PATH,
    LEDGER_HISTORY_PATH,
    ROOT,
    LedgerInputError,
    parse_instant,
)


def verify_cost_commit_order(
    cost_commit_epoch: int, first_output_commit_epoch: int | None
) -> None:
    if (
        first_output_commit_epoch is not None
        and cost_commit_epoch > first_output_commit_epoch
    ):
        raise LedgerInputError(
            "harm-costs.json was committed after the first ledger output"
        )


def _git(
    root: Path, args: list[str], *, check: bool = True
) -> subprocess.CompletedProcess[bytes]:
    try:
        result = subprocess.run(
            ["git", *args], cwd=root, capture_output=True, check=False, timeout=10
        )
    except subprocess.TimeoutExpired as exc:
        raise LedgerInputError(f"git {' '.join(args)} timed out") from exc
    if check and result.returncode != 0:
        message = result.stderr.decode("utf-8", errors="replace").strip()
        raise LedgerInputError(f"git {' '.join(args)} failed: {message}")
    return result


def _commit_epoch(root: Path, path: str, *, first: bool = False) -> int | None:
    args = ["log", "--format=%ct", "--", path]
    if first:
        args.insert(1, "--reverse")
    result = _git(root, args, check=False)
    if result.returncode != 0:
        return None
    lines = result.stdout.decode("ascii", errors="strict").splitlines()
    if not lines:
        return None
    try:
        return int(lines[0])
    except ValueError as exc:
        raise LedgerInputError(f"invalid commit timestamp for {path}") from exc


def harm_costs_digest(table: dict[str, Any]) -> str:
    """Hash cost data only; approval metadata is excluded to avoid a hash/ID cycle."""
    canonical = {key: table[key] for key in ("schema", "surfaces")}
    encoded = json.dumps(
        canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _parse_beads_utc(value: object) -> datetime:
    if not isinstance(value, str):
        raise LedgerInputError("approval comment timestamp is not text")
    try:
        instant = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise LedgerInputError("approval comment has an invalid timestamp") from exc
    if instant.tzinfo is None:
        instant = instant.replace(tzinfo=timezone.utc)
    return instant.astimezone(timezone.utc)


def load_approved_harm_costs(
    path: Path = HARM_COSTS_PATH,
    *,
    root: Path = ROOT,
    database: Path | None = None,
) -> dict[str, Any]:
    """Require a committed, unchanged, explicitly approved cost table."""
    if not path.is_file():
        raise LedgerInputError(f"required approved harm-cost table is missing: {path}")
    raw = path.read_bytes()
    try:
        table = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LedgerInputError("harm-costs.json is not valid JSON") from exc
    if not isinstance(table, dict) or table.get("schema") != "jev-mvvh.harm-costs.v1":
        raise LedgerInputError("harm-costs.json has an unsupported schema")
    if table.get("approved_by") != "Joshua":
        raise LedgerInputError("harm-costs.json is not marked approved by Joshua")
    comment_id = table.get("approval_comment_id")
    if (
        isinstance(comment_id, bool)
        or not isinstance(comment_id, int)
        or comment_id <= 0
    ):
        raise LedgerInputError("harm-costs.json lacks an approval comment id")
    digest = harm_costs_digest(table)
    if table.get("approved_sha256") != digest:
        raise LedgerInputError(
            "harm-costs approval digest does not match canonical cost data"
        )
    costs = table.get("surfaces")
    if not isinstance(costs, dict) or not costs:
        raise LedgerInputError("harm-costs.json has no per-surface costs")
    for surface_id, entry in costs.items():
        if not isinstance(surface_id, str) or not isinstance(entry, dict):
            raise LedgerInputError("harm-costs.json has an invalid surface entry")
        value = entry.get("usd_per_prevented_harm")
        source = entry.get("source")
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            or value < 0
            or not isinstance(source, str)
            or not source.strip()
        ):
            raise LedgerInputError(
                f"invalid harm-cost value or source for {surface_id}"
            )

    relative = path.resolve().relative_to(root.resolve()).as_posix()
    tracked = _git(root, ["ls-files", "--error-unmatch", "--", relative], check=False)
    if tracked.returncode != 0:
        raise LedgerInputError(
            "harm-costs.json must be committed before the first ledger run"
        )
    changed = _git(root, ["status", "--porcelain", "--", relative]).stdout
    if changed.strip():
        raise LedgerInputError("harm-costs.json has uncommitted changes")
    committed = _git(root, ["show", f"HEAD:{relative}"]).stdout
    if committed != raw:
        raise LedgerInputError(
            "working harm-costs.json differs from its committed bytes"
        )

    db_path = database or root / ".beads" / "beads.db"
    try:
        with sqlite3.connect(f"file:{db_path}?mode=ro", uri=True) as connection:
            approval = connection.execute(
                "SELECT author, text, created_at FROM comments WHERE issue_id=? AND id=?",
                ("jev-mvvh", comment_id),
            ).fetchone()
    except sqlite3.Error as exc:
        raise LedgerInputError(
            "cannot read the approval comment from the Beads database"
        ) from exc
    if approval is None:
        raise LedgerInputError(
            "harm-costs approval comment id does not exist on jev-mvvh"
        )
    author, text, created_at = approval
    approval_phrase = f"APPROVE HARM-COSTS sha256={digest}"
    if str(author).casefold() != "josh" or approval_phrase not in str(text):
        raise LedgerInputError(
            "approval comment must explicitly approve this table digest"
        )

    cost_epoch = _commit_epoch(root, relative)
    if cost_epoch is None:
        raise LedgerInputError("harm-costs.json has no committed revision")
    first_output_epoch = _commit_epoch(
        root,
        LEDGER_HISTORY_PATH.resolve().relative_to(root.resolve()).as_posix(),
        first=True,
    )
    verify_cost_commit_order(cost_epoch, first_output_epoch)
    if first_output_epoch is not None:
        approval_time = _parse_beads_utc(created_at)
        output_time = datetime.fromtimestamp(first_output_epoch, tz=timezone.utc)
        if approval_time > output_time:
            raise LedgerInputError(
                "harm-cost approval was recorded after the first ledger output"
            )
    table["_sha256"] = digest
    table["_approval_comment_id"] = comment_id
    return table


def load_expected(path: Path = EXPECTED_PATH) -> list[dict[str, Any]]:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LedgerInputError(f"cannot read surface registry {path}: {exc}") from exc
    if not isinstance(document, dict) or not isinstance(document.get("surfaces"), list):
        raise LedgerInputError("surface registry has no surfaces list")
    surfaces = [row for row in document["surfaces"] if row.get("expect") == "on"]
    ids = [row.get("id") for row in surfaces]
    if any(not isinstance(surface_id, str) or not surface_id for surface_id in ids):
        raise LedgerInputError("surface registry has an expected-on row without an id")
    if len(ids) != len(set(ids)):
        raise LedgerInputError("surface registry has duplicate ids")
    return surfaces


def validate_harm_cost_coverage(
    expected_surfaces: Iterable[dict[str, Any]], harm_table: dict[str, Any]
) -> None:
    """Require approved cost data for every enabled gate or screen surface."""
    costs = harm_table.get("surfaces")
    if not isinstance(costs, dict):
        raise LedgerInputError("harm-costs.json has no surface cost mapping")
    required = {
        surface["id"]
        for surface in expected_surfaces
        if surface.get("expect") == "on"
        and surface.get("group") in {"hook", "global", "screen"}
    }
    missing = sorted(required - costs.keys())
    if missing:
        raise LedgerInputError(
            "harm-costs.json is missing gate/screen costs for: " + ", ".join(missing)
        )


def expand_memory_surfaces(surfaces: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    expanded: list[dict[str, Any]] = []
    for surface in surfaces:
        if surface.get("id") != "memory-filter":
            expanded.append(dict(surface))
            continue
        for suffix, name in (
            ("memory-jev", "memory Jev drops"),
            ("memory-cap3", "memory cap-3 cut"),
        ):
            split = dict(surface)
            split["id"] = suffix
            split["name"] = name
            split["memory_parent"] = "memory-filter"
            expanded.append(split)
    return expanded


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--days", type=float, default=7)
    parser.add_argument("--end", help="exclusive report window end in ISO-8601")
    parser.add_argument("--memory-input", type=Path, help="memory-filter JSONL source")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--expected", type=Path, default=EXPECTED_PATH)
    parser.add_argument("--harm-costs", type=Path, default=HARM_COSTS_PATH)
    parser.add_argument("--append", action="store_true")
    parser.add_argument("--history", type=Path, default=LEDGER_HISTORY_PATH)
    return parser


def main(argv: list[str] | None = None) -> int:
    from report import append_history, assemble_report, render_report

    args = _parser().parse_args(argv)
    if args.days <= 0 or not math.isfinite(args.days):
        print("ledger: --days must be a positive finite number", file=sys.stderr)
        return 2
    try:
        expected_surfaces = load_expected(args.expected)
        harm_table = load_approved_harm_costs(args.harm_costs)
        validate_harm_cost_coverage(expected_surfaces, harm_table)
        surfaces = expand_memory_surfaces(expected_surfaces)
        end = parse_instant(args.end) if args.end else None
        report = assemble_report(
            surfaces,
            harm_table,
            days=args.days,
            end=end,
            history=args.history,
            memory_path=args.memory_input,
        )
        if args.append:
            append_history(args.history, report)
    except (LedgerInputError, OSError) as exc:
        print(f"ledger: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    else:
        print(render_report(report))
    return 1 if args.strict and report["strict_failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
