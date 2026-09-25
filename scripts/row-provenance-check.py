#!/usr/bin/env python3
"""Check provenance on newly committed experiment JSONL rows.

Only tracked ``work/**/*.jsonl`` files whose first adding commit is after the
fixed cutoff are inspected.  Rows are considered experiment rows when they
carry one of the lane's result keys.  A checked row must carry a full SHA-256
code hash and an ISO-8601 timestamp with a UTC offset.

``JEV_REPO`` is an offline-test hook; the live invocation uses the repository
containing this script.  It changes the root only, never the cutoff or the
validation rules.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

CUTOFF = datetime(2026, 9, 25, 9, 0, tzinfo=timezone.utc)
EXPERIMENT_KEYS = {"won", "success", "reward", "score", "jev_calls", "decisions"}
CODE_HASH_KEYS = ("code_sha256", "run_py_sha256")
UTC_FIELD_NAMES = {
    "finished_utc",
    "row_recorded_at_utc",
    "started_utc",
    "run_started_at_utc",
    "finished_at_utc",
    "started_at_utc",
    "row_started_at_utc",
    "recorded_at_utc",
    "timestamp_utc",
}
SHA256 = re.compile(r"^[0-9a-fA-F]{64}$")
EXEMPTION_FILE = "scripts/row-provenance-exempt.tsv"


def git_output(repo: Path, *args: str) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(repo), *args],
            text=True,
            stderr=subprocess.PIPE,
            timeout=30,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = (
            exc.stderr.strip()
            if isinstance(exc, subprocess.CalledProcessError)
            else str(exc)
        )
        raise RuntimeError(f"git {args[0]} failed: {detail}") from exc


def tracked_jsonl(repo: Path) -> list[str]:
    output = git_output(repo, "ls-files", "-z", "--", "work")
    return sorted(path for path in output.split("\0") if path.endswith(".jsonl"))


def first_added_commits(repo: Path) -> dict[str, datetime]:
    """Return the first commit that added each tracked path below ``work``."""
    output = git_output(
        repo,
        "log",
        "--reverse",
        "--diff-filter=A",
        "--format=__ROW_PROVENANCE_COMMIT__%cI",
        "--name-only",
        "--",
        "work",
    )
    first: dict[str, datetime] = {}
    commit_date: datetime | None = None
    for line in output.splitlines():
        if line.startswith("__ROW_PROVENANCE_COMMIT__"):
            raw = line.split("__ROW_PROVENANCE_COMMIT__", 1)[1]
            commit_date = parse_timestamp(raw, require_utc=False)
            continue
        if commit_date is not None and line.endswith(".jsonl"):
            first.setdefault(line, commit_date)
    return first


def parse_timestamp(value: object, *, require_utc: bool = True) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    if require_utc and parsed.utcoffset() != timezone.utc.utcoffset(None):
        return None
    return parsed.astimezone(timezone.utc)


def has_code_hash(row: dict[str, object]) -> bool:
    return any(
        isinstance(row.get(key), str) and SHA256.fullmatch(row[key])
        for key in CODE_HASH_KEYS
    )


def utc_timestamp_present(row: dict[str, object]) -> bool:
    candidates = [
        (key, value)
        for key, value in row.items()
        if key in UTC_FIELD_NAMES or key.endswith(("_utc", "_at_utc"))
    ]
    return any(parse_timestamp(value) is not None for _, value in candidates)


def load_exemptions(repo: Path) -> dict[str, str]:
    path = repo / EXEMPTION_FILE
    if not path.is_file():
        return {}
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "path\tsha256\treason":
        raise RuntimeError(f"{EXEMPTION_FILE} must start with path, sha256, reason")
    exemptions: dict[str, str] = {}
    for line_number, line in enumerate(lines[1:], 2):
        fields = line.split("\t")
        if len(fields) != 3 or not all(fields):
            raise RuntimeError(f"{EXEMPTION_FILE} line {line_number} is malformed")
        relative, digest, _reason = fields
        if relative in exemptions:
            raise RuntimeError(
                f"{EXEMPTION_FILE} line {line_number} duplicates {relative}"
            )
        if SHA256.fullmatch(digest) is None:
            raise RuntimeError(
                f"{EXEMPTION_FILE} line {line_number} has an invalid sha256"
            )
        exemptions[relative] = digest
    return exemptions


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_file(path: Path, relative: str) -> tuple[int, str | None]:
    experiment_rows = 0
    first_error: tuple[int, list[str]] | None = None
    with path.open(encoding="utf-8") as stream:
        for row_number, raw in enumerate(stream, 1):
            if not raw.strip():
                continue
            try:
                row = json.JSONDecoder().decode(raw)
            except json.JSONDecodeError as exc:
                return (
                    experiment_rows,
                    f"{relative} row {row_number} invalid JSON: {exc.msg}",
                )
            if not isinstance(row, dict) or not EXPERIMENT_KEYS.intersection(row):
                continue
            experiment_rows += 1
            missing: list[str] = []
            if not has_code_hash(row):
                missing.append("code_sha256 or run_py_sha256")
            if not utc_timestamp_present(row):
                missing.append("UTC timestamp")
            if missing and first_error is None:
                first_error = (row_number, missing)
    if first_error is None:
        return experiment_rows, None
    row_number, missing = first_error
    return experiment_rows, f"{relative} row {row_number} missing {'; '.join(missing)}"


def main() -> int:
    repo = Path(
        os.environ.get("JEV_REPO", Path(__file__).resolve().parents[1])
    ).resolve()
    try:
        paths = tracked_jsonl(repo)
        first_added = first_added_commits(repo)
        exemptions = load_exemptions(repo)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    checked_files = 0
    checked_rows = 0
    exempted_files = 0
    errors: list[str] = []
    for relative in paths:
        added = first_added.get(relative)
        if added is None or added <= CUTOFF:
            continue
        if relative in exemptions:
            actual = sha256_file(repo / relative)
            expected = exemptions[relative]
            if actual != expected:
                errors.append(
                    f"{relative} exemption sha256 mismatch: expected {expected}, got {actual}"
                )
                continue
            exempted_files += 1
            continue
        rows, error = check_file(repo / relative, relative)
        if rows == 0:
            continue
        checked_files += 1
        checked_rows += rows
        if error is not None:
            errors.append(error)

    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    print(
        f"checked {checked_files} experiment row file(s), "
        f"{checked_rows} experiment rows, exempted {exempted_files} file(s)"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
