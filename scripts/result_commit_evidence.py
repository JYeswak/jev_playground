#!/usr/bin/env python3
"""Refuse staged result claims without commit-pinned rows, scorer, split/seed, and bar metadata.

For each changed result row, add a manifest line in that ledger section:

Evidence: per-call rows: `work/run/rows.jsonl`@<sha256>; scorer:
`work/run/score.py`@<sha256>; split/seed: `work/run/PREREG.md`@<sha256>
Measurement: ts=<RFC3339 timestamp>; bar file: `work/run/BAR.md`@<sha256>

Hashes are computed over the exact blobs that the commit would contain. Historical
commits can be replayed with --commit REV; the hook uses --staged.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path, PurePosixPath

RESULT_MARKER = re.compile(r"\b(?:result|verdict|outcome)\s*(?:\([^)]*\))?\s*:", re.IGNORECASE)
DECISION_MARKER = re.compile(
    r"\b(?:pass|fail|refuted|retracted|no-go|not.?run|not.?enough.?data|model-limit|win|loss)\b",
    re.IGNORECASE,
)
METRIC_LABEL = re.compile(r"^\s*[-*]\s*\*\*(?:live|measured|metrics?|counts?)\*\*\s*:", re.IGNORECASE)
METRIC_DETAIL = re.compile(
    r"\b(?:accuracy|agreement|precision|recall|auc|kappa|calls?|tokens?|rows?|files?|turns?|"
    r"episodes?|median|latency|spend|cost|top-\d+)\b",
    re.IGNORECASE,
)
EVAL_RESULT_HEADING = re.compile(
    r"^\s*#{2,4}\s+.*\b(?:pass|fail|close|refuted|retracted|no-go|model-limit|not enough data)\b",
    re.IGNORECASE,
)
NEGATIVE_ROW = re.compile(r"^\s*#{2,4}\s+R\d+\s*[—–-]", re.IGNORECASE)
DONE_RESULT_LINE = re.compile(
    r"^\s*(?:#{1,6}\s+DONE(?:\s|$)|(?:result|verdict)\s*:\s*DONE\b)", re.IGNORECASE
)
REFERENCE = re.compile(
    r"(?P<kind>per-call\s+rows|scorer|split/seed|bar\s+file)\s*:\s*"
    r"`(?P<path>[^`]+)`@(?P<sha>[0-9a-f]{64})",
    re.IGNORECASE,
)
TIMESTAMP_FIELD = re.compile(
    r"\bts\s*[:=]\s*(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2}))(?=$|[\s;,)])",
    re.IGNORECASE,
)
RESULT_ROWS_FILE = re.compile(
    r"^(?:labels(?:[-_.].*)?|.*\.live|.*\.results?(?:[-_.].*)?)\.(?:jsonl|ndjson|csv|tsv)$",
    re.IGNORECASE,
)
ROW_CODE_SUFFIXES = {".py", ".mjs", ".js", ".cjs", ".ts", ".sh", ".rs", ".go", ".r"}
ROW_DATA_SUFFIXES = {".json", ".jsonl", ".ndjson", ".csv", ".tsv"}


@dataclass(frozen=True)
class AddedLine:
    path: str
    number: int
    text: str


@dataclass(frozen=True)
class SourceReference:
    kind: str
    path: str
    sha256: str


class GateError(RuntimeError):
    """A Git or input failure that must fail the result-evidence gate closed."""


def git_bytes(repo: Path, *args: str) -> bytes:
    try:
        result = subprocess.run(
            ["git", *args], cwd=repo, capture_output=True, check=False, timeout=10
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise GateError(f"cannot run git: {exc}") from exc
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise GateError(f"git {' '.join(args)} failed: {detail or result.returncode}")
    return result.stdout


def repo_root() -> Path:
    try:
        value = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            check=True,
            text=True,
            timeout=10,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        raise GateError(f"not inside a Git worktree: {exc}") from exc
    return Path(value)


def changed_paths(repo: Path, commit: str | None) -> tuple[list[str], str | None]:
    if commit is None:
        raw = git_bytes(repo, "diff", "--cached", "--name-only", "-z", "--no-renames")
        return [p.decode("utf-8", errors="surrogateescape") for p in raw.split(b"\0") if p], None

    commit_ref = git_bytes(repo, "rev-parse", "--verify", f"{commit}^{{commit}}").decode().strip()
    parents = git_bytes(repo, "rev-list", "--parents", "-n", "1", commit_ref).decode().split()
    if len(parents) < 2:
        raise GateError(f"cannot replay root commit without a parent: {commit_ref}")
    parent_ref = parents[1]
    raw = git_bytes(
        repo, "diff", "--name-only", "-z", "--no-renames", parent_ref, commit_ref, "--"
    )
    return [p.decode("utf-8", errors="surrogateescape") for p in raw.split(b"\0") if p], commit_ref


def added_lines(repo: Path, path: str, commit: str | None) -> list[AddedLine]:
    literal_path = f":(literal){path}"
    if commit is None:
        args = ["diff", "--cached", "--no-ext-diff", "--no-color", "--unified=0", "--no-renames", "--", literal_path]
    else:
        parent_ref = git_bytes(repo, "rev-parse", "--verify", f"{commit}^1").decode().strip()
        args = ["diff", "--no-ext-diff", "--no-color", "--unified=0", "--no-renames", parent_ref, commit, "--", literal_path]
    diff = git_bytes(repo, *args).decode("utf-8", errors="replace").splitlines()
    line_number = 0
    additions: list[AddedLine] = []
    hunk = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")
    for line in diff:
        match = hunk.match(line)
        if match:
            line_number = int(match.group(1))
        elif line.startswith("+++"):
            continue
        elif line.startswith("+"):
            additions.append(AddedLine(path, line_number, line[1:]))
            line_number += 1
        elif line.startswith(" "):
            line_number += 1
    return additions


def tree_blob(repo: Path, path: str, commit: str | None) -> bytes:
    parsed = PurePosixPath(path)
    if parsed.is_absolute() or ".." in parsed.parts or not path or "\x00" in path:
        raise GateError(f"unsafe evidence path {path!r}")
    object_ref = f":{path}" if commit is None else f"{commit}:{path}"
    oid = git_bytes(repo, "rev-parse", "--verify", object_ref).decode().strip()
    return git_bytes(repo, "cat-file", "blob", oid)


def is_done_result_path(path: str) -> bool:
    name = PurePosixPath(path).name.casefold()
    suffixes = {".md", ".mdx", ".json", ".jsonl", ".ndjson", ".csv", ".tsv", ".txt"}
    suffix = PurePosixPath(name).suffix
    return (
        name == "done"
        or (
            name.startswith(("done.", "done-", "done_"))
            and suffix in suffixes
        )
        or any(
            name.endswith((f"-done{suffix}", f"_done{suffix}", f".done{suffix}"))
            for suffix in suffixes
        )
    )


def is_result_rows_path(path: str) -> bool:
    return path.startswith("work/") and bool(RESULT_ROWS_FILE.fullmatch(PurePosixPath(path).name))


def is_result_change(path: str, text: str) -> bool:
    if path in {"EVAL.md", "NEGATIVE_EVIDENCE.md"}:
        if path == "NEGATIVE_EVIDENCE.md" and NEGATIVE_ROW.search(text):
            return True
        if (
            path == "EVAL.md"
            and EVAL_RESULT_HEADING.search(text)
            and re.search(r"\d", text)
        ):
            return True
        if RESULT_MARKER.search(text):
            return bool(re.search(r"\d", text) or DECISION_MARKER.search(text))
        if path == "EVAL.md" and METRIC_LABEL.search(text):
            return bool(re.search(r"\d", text))
        return bool(
            path == "EVAL.md"
            and re.search(r"\d", text)
            and METRIC_DETAIL.search(text)
        )
    if is_done_result_path(path):
        return bool(text.strip()) and REFERENCE.search(text) is None
    if is_result_rows_path(path):
        return bool(text.strip())
    if path.startswith("work/") and PurePosixPath(path).suffix.casefold() in {".md", ".mdx", ".txt"}:
        return bool(DONE_RESULT_LINE.search(text))
    return False


def section_at(lines: list[str], line_number: int) -> int:
    section = 0
    for index, line in enumerate(lines[:line_number], start=1):
        if re.match(r"^#{1,2}\s+", line):
            section = index
    return section


def references_for(text: str) -> list[SourceReference]:
    found: list[SourceReference] = []
    for match in REFERENCE.finditer(text):
        kind = match.group("kind").casefold()
        if kind.startswith("per-call"):
            kind = "per-call rows"
        found.append(SourceReference(kind, match.group("path"), match.group("sha").lower()))
    return found


def has_timestamp(text: str) -> bool:
    match = TIMESTAMP_FIELD.search(text)
    if not match:
        return False
    try:
        stamp = datetime.fromisoformat(match.group(1).replace("Z", "+00:00"))
    except ValueError:
        return False
    return stamp.tzinfo is not None


def row_records_valid(path: str, payload: bytes) -> bool:
    suffix = PurePosixPath(path).suffix.casefold()
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError:
        return False
    if suffix in {".jsonl", ".ndjson"}:
        records: list[object] = []
        try:
            for line in text.splitlines():
                if line.strip():
                    records.append(json.loads(line))
        except json.JSONDecodeError:
            return False
        return bool(records) and all(isinstance(row, dict) for row in records)
    if suffix == ".json":
        try:
            value = json.loads(text)
        except json.JSONDecodeError:
            return False
        if isinstance(value, dict):
            value = next(
                (value[key] for key in ("rows", "calls", "records") if isinstance(value.get(key), list)),
                None,
            )
        return isinstance(value, list) and bool(value) and all(isinstance(row, dict) for row in value)
    if suffix in {".csv", ".tsv"}:
        try:
            delimiter = "\t" if suffix == ".tsv" else ","
            rows = list(csv.reader(io.StringIO(text), delimiter=delimiter))
        except csv.Error:
            return False
        return len(rows) >= 2 and bool(rows[0]) and any(any(cell.strip() for cell in row) for row in rows[1:])
    return False


def source_problem(
    repo: Path, source: SourceReference, commit: str | None
) -> str | None:
    try:
        payload = tree_blob(repo, source.path, commit)
    except GateError as exc:
        return f"{source.kind}:uncommitted-or-unreadable-path={source.path!r} ({exc})"
    actual = hashlib.sha256(payload).hexdigest()
    if actual != source.sha256:
        return f"{source.kind}:sha256-mismatch={source.path}"
    if source.kind == "per-call rows":
        if PurePosixPath(source.path).suffix.casefold() not in ROW_DATA_SUFFIXES or not row_records_valid(source.path, payload):
            return f"per-call rows:not-row-data={source.path}"
    elif source.kind == "split/seed":
        try:
            text = payload.decode("utf-8")
        except UnicodeDecodeError:
            return f"split/seed:not-utf8={source.path}"
        if not re.search(r"\b(?:seed|split|held.?out|development|stratif(?:y|ied))\b", text, re.IGNORECASE):
            return f"split/seed:not-described={source.path}"
    elif source.kind == "bar file":
        if PurePosixPath(source.path).suffix.casefold() not in {".md", ".mdx"} or not payload.strip():
            return f"bar file:not-markdown={source.path}"

    return None

def inspect(repo: Path, commit: str | None) -> tuple[int, list[str]]:
    paths, resolved_commit = changed_paths(repo, commit)
    sections: dict[tuple[str, int], list[AddedLine]] = {}
    evidence_sections: dict[tuple[str, int], list[SourceReference]] = {}
    added_sections: dict[tuple[str, int], list[str]] = {}
    for path in paths:
        done_path = is_done_result_path(path)
        result_rows = is_result_rows_path(path)
        work_report = (
            path.startswith("work/")
            and PurePosixPath(path).suffix.casefold() in {".md", ".mdx", ".txt"}
        )
        if path not in {"EVAL.md", "NEGATIVE_EVIDENCE.md"} and not done_path and not work_report and not result_rows:
            continue
        additions = added_lines(repo, path, resolved_commit)
        if not additions:
            continue
        if work_report and not done_path and not result_rows:
            additions = [
                line
                for line in additions
                if is_result_change(path, line.text) or references_for(line.text)
            ]
            if not any(is_result_change(path, line.text) for line in additions):
                continue
        if result_rows:
            current_lines: list[str] = []
        else:
            try:
                blob = tree_blob(repo, path, resolved_commit)
                current_lines = blob.decode("utf-8").splitlines()
            except (GateError, UnicodeDecodeError) as exc:
                raise GateError(f"cannot read changed result file {path}: {exc}") from exc
        for added in additions:
            section = section_at(current_lines, added.number)
            key = (path, section)
            added_sections.setdefault(key, []).append(added.text)
            if is_result_change(path, added.text):
                sections.setdefault(key, []).append(added)
            refs = [] if result_rows else references_for(added.text)
            if refs:
                evidence_sections.setdefault(key, []).extend(refs)

    violations: list[str] = []
    for (path, section), rows in sorted(sections.items()):
        if is_result_rows_path(path):
            evidence_groups = [
                refs
                for refs in evidence_sections.values()
                if any(source.kind == "per-call rows" and source.path == path for source in refs)
            ]
            if not evidence_groups:
                evidence_groups = [[]]
        else:
            evidence_groups = [evidence_sections.get((path, section), [])]

        best_details: list[str] | None = None
        for refs in evidence_groups:
            valid: set[str] = set()
            problems: list[str] = []
            for source in refs:
                problem = source_problem(repo, source, resolved_commit)
                if problem is None:
                    valid.add(source.kind)
                else:
                    problems.append(problem)
            missing = [
                kind
                for kind in ("per-call rows", "scorer", "split/seed")
                if kind not in valid
            ]
            if commit is None and (
                path in {"EVAL.md", "NEGATIVE_EVIDENCE.md"} or is_done_result_path(path)
            ):
                section_text = "\n".join(added_sections.get((path, section), []))
                if not has_timestamp(section_text):
                    missing.append("timestamp")
                if "bar file" not in valid:
                    missing.append("bar file")
            details = problems + ([f"missing={','.join(missing)}"] if missing else [])
            if not details:
                best_details = None
                break
            if best_details is None or len(details) < len(best_details):
                best_details = details

        if best_details:
            violation_line = min(row.number for row in rows)
            violations.append(
                f"{path}:{violation_line} " + "; ".join(best_details)
            )

    if violations:
        return 1, violations
    result_count = sum(len(rows) for rows in sections.values())
    return 0, [f"result-changes={result_count}" if result_count else "no-result-changes"]



def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--staged", action="store_true", help="check the index against HEAD (commit-hook mode)")
    mode.add_argument("--commit", metavar="REV", help="replay one commit against its first parent")
    args = parser.parse_args()
    try:
        repo = repo_root()
        code, details = inspect(repo, args.commit)
    except GateError as exc:
        print(f"result-commit-evidence REFUSE reason=checker-error detail={exc}", file=sys.stderr)
        return 1
    if code:
        for detail in details:
            print(f"result-commit-evidence REFUSE {detail}", file=sys.stderr)
        return code
    print(f"result-commit-evidence PASS {details[0] if details else 'no-result-changes'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
