#!/usr/bin/env python3
"""Say whether CI on main is green, and when it is red, name the failing row.

  python3 scripts/ci-main-status.py

Reads the latest COMPLETED gates.yml run on branch main with event push and prints one line:

  CI main <sha7> <conclusion> <run id> <age>

For a failure, each failed job follows, with the rows its log names: a registered-suites row
ending in a tab plus FAIL (or `RED named <row>` on a plant dispatch), and a gates `RED <stage>` row
plus the `FAIL  <check>` lines under it. When a newer run on another sha has not finished, a STALE
line says the result above is not for the latest push.

Exit 0 green, 1 red, 2 NOT_RUN: gh missing, unauthenticated, network error, a gh call past its
timeout (CI_MAIN_STATUS_TIMEOUT seconds, default 20), no completed run, or a conclusion that is
neither green nor red (cancelled, skipped). NOT_RUN never prints as green.

Why: 2026-09-24, registered-suites failed on every push to main from cf70e28 (15:19Z) to ff8316d
(21:10Z), about 55 runs, and no agent looked for six hours (bead jev-bfku).
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone

REPO = os.environ.get("JEV_CI_REPO", "JYeswak/jev_playground")
WORKFLOW = "gates.yml"
STRANGER_WORKFLOW = "stranger-run.yml"
STRANGER_EVENTS = {"schedule", "workflow_dispatch"}
STRANGER_STALE_SECONDS = 36 * 3600

TIMEOUT = float(os.environ.get("CI_MAIN_STATUS_TIMEOUT", "20"))
GREEN = {"success"}
RED = {"failure", "timed_out", "startup_failure"}
LIST_FIELDS = "databaseId,headSha,status,conclusion,createdAt,updatedAt,url"
STRANGER_LIST_FIELDS = f"{LIST_FIELDS},event"
# gh --log-failed line: <job>\t<step>\t<timestamp> <message>; the step's first line carries a BOM.
STAMP = re.compile(r"^\ufeff?\d{4}-\d\d-\d\dT[0-9:.]+Z ?")
ANSI = re.compile(r"(\x1b|\^\[)\[[0-9;]*m")
WIDTH = 220
STRANGER_MISMATCH = re.compile(r"\b(row changed|new README command)\b.*")


class GhError(Exception):
    pass


# `gh help exit-codes`: 4 means the command needs a login.
GH_NEEDS_LOGIN_EXIT = 4
GH_INSTALL = "install it from https://cli.github.com, then run: gh auth login"
GH_LOGIN = "log in: gh auth login"


def gh(args: list[str]) -> str:
    """Run gh with a hard timeout; any failure is a GhError naming what happened."""
    try:
        done = subprocess.run(
            ["gh", *args], capture_output=True, text=True, timeout=TIMEOUT
        )
    except FileNotFoundError:
        raise GhError(f"gh not installed; {GH_INSTALL}") from None
    except subprocess.TimeoutExpired:
        raise GhError(f"gh {args[0]} {args[1]} timed out after {TIMEOUT:g}s") from None
    if done.returncode != 0:
        said = (done.stderr.strip() or done.stdout.strip()).splitlines()
        hint = f" ({GH_LOGIN})" if done.returncode == GH_NEEDS_LOGIN_EXIT else ""
        raise GhError(
            f"gh exit {done.returncode}: {said[0] if said else 'no output'}{hint}"
        )
    return done.stdout


def epoch(stamp: str) -> float:
    return (
        datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ")
        .replace(tzinfo=timezone.utc)
        .timestamp()
    )


def age(stamp: str, now: float) -> str:
    seconds = max(0, int(now - epoch(stamp)))
    if seconds < 3600:
        return f"{seconds // 60}m ago"
    if seconds < 86400:
        return f"{seconds // 3600}h{seconds % 3600 // 60:02d}m ago"
    return f"{seconds // 86400}d ago"


def failing_rows(log: str) -> dict[str, list[str]]:
    """job name -> the rows its failed-step log names, in log order, each once."""
    rows: dict[str, list[str]] = {}
    under_red: set[str] = set()
    for line in log.splitlines():
        parts = line.split("\t", 2)
        if len(parts) < 3:
            continue
        job, _step, rest = parts
        message = ANSI.sub("", STAMP.sub("", rest, count=1)).rstrip()
        if re.match(r"RED\s", message):
            under_red.add(job)
            row = message
        elif job in under_red and message == "failing:":
            continue
        elif job in under_red and re.match(r"FAIL\s", message):
            row = "  " + message
        elif message.startswith("RED named ") or message.endswith("\tFAIL"):
            under_red.discard(job)
            row = message
        else:
            under_red.discard(job)
            continue
        seen = rows.setdefault(job, [])
        if row[:WIDTH] not in seen:
            seen.append(row[:WIDTH])
    return rows


def failure_detail(gh, run: dict) -> list[str]:
    rid = str(run["databaseId"])
    try:
        jobs = json.loads(gh(["run", "view", rid, "-R", REPO, "--json", "jobs"]))[
            "jobs"
        ]
        failed = [
            j["name"] for j in jobs if j.get("conclusion") not in ("success", "skipped")
        ]
    except (GhError, ValueError, KeyError, TypeError) as error:
        return [f"  jobs unavailable: {error}; see {run.get('url', rid)}"]
    try:
        rows = failing_rows(gh(["run", "view", rid, "-R", REPO, "--log-failed"]))
    except GhError as error:
        return [f"  FAILED JOB {name}" for name in failed] + [
            f"  log unavailable: {error}; see {run.get('url', rid)}"
        ]
    out = []
    for name in failed:
        out.append(f"  FAILED JOB {name}")
        named = rows.get(name) or [
            f"no RED or FAIL row in its log; see {run.get('url', rid)}"
        ]
        out += [f"    {row}" for row in named]
    return out


def status(gh, now: float) -> tuple[list[str], int]:
    try:
        runs = json.loads(
            gh(
                [
                    "run",
                    "list",
                    "-R",
                    REPO,
                    "--workflow",
                    WORKFLOW,
                    "--branch",
                    "main",
                    "--event",
                    "push",
                    "--limit",
                    "20",
                    "--json",
                    LIST_FIELDS,
                ]
            )
        )
    except (GhError, ValueError) as error:
        return [f"CI main NOT_RUN {error}"], 2
    done = next((r for r in runs if r.get("status") == "completed"), None)
    if done is None:
        return [
            f"CI main NOT_RUN no completed {WORKFLOW} push run on main among the newest {len(runs)}"
        ], 2
    sha7 = done["headSha"][:7]
    conclusion = done.get("conclusion") or "none"
    tail = f"{done['databaseId']} {age(done['updatedAt'], now)}"
    if conclusion in GREEN:
        lines, rc = [f"CI main {sha7} {conclusion} {tail}"], 0
    elif conclusion in RED:
        lines, rc = (
            [f"CI main {sha7} {conclusion} {tail}"] + failure_detail(gh, done),
            1,
        )
    else:
        lines, rc = [f"CI main {sha7} NOT_RUN conclusion={conclusion} {tail}"], 2
    pending = [r for r in runs[: runs.index(done)] if r["headSha"] != done["headSha"]]
    if pending:
        newest = pending[0]
        lines.append(
            f"STALE {len(pending)} newer run(s) not finished, newest {newest['databaseId']} "
            f"{newest.get('status')} on {newest['headSha'][:7]}; the {conclusion} above is for {sha7}"
        )
    return lines, rc


def stranger_mismatch(log: str) -> str | None:
    """Return the first README expectation mismatch named by a stranger-run log."""
    for line in log.splitlines():
        message = ANSI.sub("", STAMP.sub("", line, count=1))
        match = STRANGER_MISMATCH.search(message)
        if match:
            return message[match.start() :].strip()[:WIDTH]
    return None


def stranger_status(gh, now: float) -> list[str]:
    """Report the newest completed scheduled or manually dispatched README stranger run."""
    try:
        runs = json.loads(
            gh(
                [
                    "run",
                    "list",
                    "-R",
                    REPO,
                    "--workflow",
                    STRANGER_WORKFLOW,
                    "--branch",
                    "main",
                    "--limit",
                    "20",
                    "--json",
                    STRANGER_LIST_FIELDS,
                ]
            )
        )
    except (GhError, ValueError) as error:
        return [f"README stranger nightly: NOT_RUN {error}"]
    eligible = [r for r in runs if r.get("event") in STRANGER_EVENTS]
    done = next((r for r in eligible if r.get("status") == "completed"), None)
    if done is None:
        return [
            f"README stranger nightly: NOT_RUN no completed {STRANGER_WORKFLOW} run "
            f"on main among the newest {len(runs)}"
        ]
    conclusion = done.get("conclusion") or "none"
    run_id = done["databaseId"]
    run_age = age(done["updatedAt"], now)
    stale = now - epoch(done["updatedAt"]) > STRANGER_STALE_SECONDS
    prefix = "STALE " if stale else ""
    lines = [f"README stranger nightly: {prefix}{conclusion} {run_id} {run_age}"]
    if conclusion == "failure":
        try:
            mismatch = stranger_mismatch(
                gh(["run", "view", str(run_id), "-R", REPO, "--log-failed"])
            )
        except GhError as error:
            mismatch = f"NOT_RUN log unavailable: {error}"
        lines.append(f"  FIRST MISMATCH {mismatch or 'not named in failed log'}")
    return lines


def main() -> int:
    lines, rc = status(gh, time.time())
    lines += stranger_status(gh, time.time())
    print("\n".join(lines), flush=True)
    return rc


if __name__ == "__main__":
    sys.exit(main())
