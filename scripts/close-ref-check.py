#!/usr/bin/env python3
"""Check closed bead references against the committed origin/main tree."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import date, datetime, time, timezone
from pathlib import Path, PurePosixPath
from typing import Any

ORIGIN_MAIN = "origin/main"
REFERENCE_KINDS = {"commit", "investigation"}
TRAILING_PUNCTUATION = "`'\".,;)]}"
LEADING_PUNCTUATION = "`'\"([{<"


class CheckError(RuntimeError):
    """A missing or unreadable input that prevents a safe check."""


@dataclass(frozen=True)
class ReferenceResult:
    kind: str
    value: str
    status: str
    reason: str


@dataclass(frozen=True)
class BeadResult:
    bead_id: str
    status: str
    close_reason: str
    references: list[ReferenceResult]
    reason: str


def run_git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["git", *args],
            cwd=repo,
            capture_output=True,
            check=False,
            text=True,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise CheckError(f"cannot run git {' '.join(args)}: {exc}") from exc


def require_origin_main(repo: Path) -> None:
    result = run_git(repo, "rev-parse", "--verify", "--quiet", f"{ORIGIN_MAIN}^{{commit}}")
    if result.returncode != 0:
        raise CheckError(f"{ORIGIN_MAIN} is unavailable; fetch origin/main before checking")


def load_issues(repo: Path) -> list[dict[str, Any]]:
    path = repo / ".beads" / "issues.jsonl"
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise CheckError(f"cannot read {path.relative_to(repo)}: {exc}") from exc

    issues: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            issue = json.loads(line)
        except json.JSONDecodeError as exc:
            raise CheckError(f"invalid JSON in .beads/issues.jsonl:{line_number}: {exc}") from exc
        if not isinstance(issue, dict):
            raise CheckError(f"non-object row in .beads/issues.jsonl:{line_number}")
        issue_id = issue.get("id")
        if not isinstance(issue_id, str) or not issue_id:
            raise CheckError(f"missing bead id in .beads/issues.jsonl:{line_number}")
        if issue_id in seen_ids:
            raise CheckError(f"duplicate bead id {issue_id!r} in .beads/issues.jsonl")
        seen_ids.add(issue_id)
        issues.append(issue)
    return issues


def parse_timestamp(value: str) -> datetime:
    """Parse an ISO date or timestamp; dates and naive timestamps mean UTC."""
    if len(value) == 10:
        parsed_date = date.fromisoformat(value)
        return datetime.combine(parsed_date, time.min, tzinfo=timezone.utc)

    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def parse_references(close_reason: str) -> list[tuple[str, str]]:
    references: list[tuple[str, str]] = []
    for raw_token in close_reason.split():
        token = raw_token.strip(LEADING_PUNCTUATION + TRAILING_PUNCTUATION)
        kind, separator, value = token.partition(":")
        if kind not in REFERENCE_KINDS or not separator:
            continue
        references.append((kind, value))
    return references


def valid_commit_sha(value: str) -> bool:
    return 7 <= len(value) <= 40 and all(char in "0123456789abcdefABCDEF" for char in value)


def check_reference(repo: Path, kind: str, value: str) -> ReferenceResult:
    if not value:
        return ReferenceResult(kind, value, "REFUSED", "reference value is empty")

    if kind == "commit":
        if not valid_commit_sha(value):
            return ReferenceResult(kind, value, "REFUSED", "value is not a 7-40 character commit SHA")
        result = run_git(repo, "merge-base", "--is-ancestor", value, ORIGIN_MAIN)
        if result.returncode == 0:
            return ReferenceResult(kind, value, "PASS", "commit is an ancestor of origin/main")
        if result.returncode == 1:
            return ReferenceResult(kind, value, "REFUSED", "commit is not an ancestor of origin/main")
        detail = result.stderr.strip() or f"git exited {result.returncode}"
        return ReferenceResult(kind, value, "REFUSED", f"cannot verify commit reachability: {detail}")

    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or "\x00" in value:
        return ReferenceResult(kind, value, "REFUSED", "investigation path is not a safe repository-relative path")
    result = run_git(repo, "cat-file", "-e", f"{ORIGIN_MAIN}:{value}")
    if result.returncode == 0:
        return ReferenceResult(kind, value, "PASS", "path exists in the origin/main tree")
    return ReferenceResult(kind, value, "REFUSED", "path is not tracked on origin/main")


def check_bead(repo: Path, issue: dict[str, Any], selection_error: str | None = None) -> BeadResult:
    bead_id = str(issue["id"])
    close_reason = issue.get("close_reason")
    if not isinstance(close_reason, str):
        close_reason = ""

    if selection_error:
        return BeadResult(bead_id, "REFUSED", close_reason, [], selection_error)
    if issue.get("status") != "closed":
        return BeadResult(bead_id, "REFUSED", close_reason, [], "bead is not closed")

    references = [check_reference(repo, kind, value) for kind, value in parse_references(close_reason)]
    refused = [reference for reference in references if reference.status == "REFUSED"]
    if refused:
        reason = "; ".join(f"{ref.kind}:{ref.value}: {ref.reason}" for ref in refused)
        return BeadResult(bead_id, "REFUSED", close_reason, references, reason)
    if not references:
        return BeadResult(bead_id, "PASS", close_reason, [], "no commit or investigation references to check")
    return BeadResult(bead_id, "PASS", close_reason, references, "all typed references pass")


def select_issues(
    issues: list[dict[str, Any]], bead_id: str | None, since: datetime | None
) -> list[tuple[dict[str, Any], str | None]]:
    if bead_id is not None:
        matches = [issue for issue in issues if issue.get("id") == bead_id]
        if not matches:
            return [({"id": bead_id, "status": "missing", "close_reason": ""}, "bead not found")]
        return [(matches[0], None)]

    selected: list[tuple[dict[str, Any], str | None]] = []
    for issue in issues:
        if issue.get("status") != "closed":
            continue
        closed_at = issue.get("closed_at")
        if not isinstance(closed_at, str) or not closed_at:
            selected.append((issue, "closed bead has no usable closed_at timestamp"))
            continue
        try:
            closed_time = parse_timestamp(closed_at)
        except ValueError:
            selected.append((issue, f"invalid closed_at timestamp {closed_at!r}"))
            continue
        if since is None or closed_time > since:
            selected.append((issue, None))
    return selected


def result_payload(results: list[BeadResult]) -> dict[str, Any]:
    refused = sum(result.status == "REFUSED" for result in results)
    return {
        "schema_version": "close-ref-check.v1",
        "status": "REFUSED" if refused else "PASS",
        "summary": {"checked": len(results), "passed": len(results) - refused, "refused": refused},
        "results": [asdict(result) for result in results],
    }


def print_results(results: list[BeadResult], as_json: bool) -> int:
    payload = result_payload(results)
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        for result in results:
            print(f"{result.bead_id} {result.status}: {result.reason}")
            for reference in result.references:
                print(f"  {reference.kind}:{reference.value} {reference.status}: {reference.reason}")
        summary = payload["summary"]
        print(f"close-ref-check {payload['status']}: checked={summary['checked']} refused={summary['refused']}")
    return 1 if payload["status"] == "REFUSED" else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--bead", help="check one bead id")
    selection.add_argument("--since", help="check every close after an ISO date or timestamp")
    parser.add_argument("--json", action="store_true", help="emit a JSON result envelope")
    args = parser.parse_args(argv)

    try:
        since = parse_timestamp(args.since) if args.since else None
    except ValueError as exc:
        parser.error(f"invalid --since value: {exc}")

    repo = Path(__file__).resolve().parent.parent
    try:
        require_origin_main(repo)
        issues = load_issues(repo)
        selected = select_issues(issues, args.bead, since)
        results = [check_bead(repo, issue, error) for issue, error in selected]
    except CheckError as exc:
        if args.json:
            print(json.dumps({"schema_version": "close-ref-check.v1", "status": "ERROR", "error": str(exc)}))
        else:
            print(f"close-ref-check ERROR: {exc}", file=sys.stderr)
        return 2
    return print_results(results, args.json)


if __name__ == "__main__":
    raise SystemExit(main())
