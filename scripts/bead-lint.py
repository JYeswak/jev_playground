#!/usr/bin/env python3
"""bead-lint: is each bead self-contained enough for a fresh agent to work it alone?

beads-workflow quality checklist made executable: every non-epic bead needs WHAT and WHY,
an acceptance with a runnable command and a planted negative, at least one checkable source
(repo path, path:line, arXiv id, URL, or commit sha), and no dependency on a bead that does
not exist. Read-only: it never writes beads.

Usage: bead-lint.py [--epic ID | --ids ID,ID] [--all-open] [--json]
Exit: 0 no findings, 1 findings, 64 usage, 69 br unavailable.
"""

import argparse
import json
import os
import re
import sqlite3
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
# Linear patterns only (regex-engineering section 7: 50k near-miss < 50 ms each).
ARXIV = re.compile(r"arXiv:\d{4}\.\d{4,5}")
URL = re.compile(r"https?://[^\s)]{1,300}")
SHA = re.compile(
    r"\b(?=[0-9a-f]{0,39}[a-f])[0-9a-f]{8,40}\b|\bcommit[: ][0-9a-f]{7,40}\b"
)
SOURCE_EXT = (
    ".md",
    ".py",
    ".ts",
    ".mjs",
    ".sh",
    ".json",
    ".jsonl",
    ".rs",
    ".tsv",
    ".yml",
    ".yaml",
)
COMMAND_MARKERS = (
    "`",
    "python3 ",
    "node ",
    "npm ",
    "bash ",
    "br ",
    "classifier ",
    "jq ",
    " -> ",
)
NEGATIVE_MARKERS = (
    "plant",
    "negative",
    "refus",
    "must not",
    "never ",
    "fails",
    "red ",
)


def has_path(text):
    """A token that names a repo file, optionally with :line (checked with str ops, no regex)."""
    for token in text.split():
        base = token.strip("`'\"(),;[]").split(":", 1)[0]
        if base.endswith(SOURCE_EXT) and len(base) > 3:
            return True
    return False


def has_source(text):
    return bool(
        ARXIV.search(text) or has_path(text) or URL.search(text) or SHA.search(text)
    )


def backtick_spans(text):
    """Contents of `...` spans: the runnable commands a bead names (str ops, no regex)."""
    parts = text.split("`")
    return parts[1::2]


def declared_creates(text):
    """Paths the bead says it creates: tokens after 'creates:' up to the next sentence end."""
    out = set()
    low = text.lower()
    start = 0
    while (i := low.find("creates:", start)) != -1:
        tail = text[i + len("creates:") :].split(". ", 1)[0].split("\n", 1)[0]
        for token in tail.replace(",", " ").split():
            out.add(token.strip("`'\"();[]").rstrip("."))
        start = i + 1
    return out


def multiword_slot(span):
    """True when a `<...>` slot in the command contains a space and only words (not `<`/`>` operators)."""
    start = 0
    while (i := span.find("<", start)) != -1:
        j = span.find(">", i)
        if j == -1:
            return False
        inner = span[i + 1 : j].strip()
        if (
            " " in inner
            and inner.replace(" ", "").replace("-", "").replace("_", "").isalnum()
        ):
            return True
        start = i + 1
    return False


def path_exists(path):
    """exists() that treats an unstat-able path (too long, bad bytes) as missing instead of crashing."""
    try:
        return path.exists()
    except (OSError, ValueError):
        return False


def command_problems(acc, root=None):
    """(missing paths, placeholders) inside the acceptance's backtick commands.

    A repo-relative path in a command must exist at `root` or be declared with `creates:`;
    a `<two words>` slot inside a command stands in for a missing artifact (jev-mvvh, 2026-10-04);
    one-word slots (`<id>`, `<dir>`, `<sha>`) are usage parameters and stay allowed.
    """
    root = REPO if root is None else root
    created = declared_creates(acc)
    missing, placeholders = [], []
    for span in backtick_spans(acc):
        if multiword_slot(span):
            placeholders.append(span)
        for token in span.split():
            base = token.strip("'\"(),;[]").split(":", 1)[0]
            if base.startswith(("-", "~", "/", "$")) or "*" in base or "://" in base:
                continue
            if "/" in base and (base.endswith(SOURCE_EXT) or base.endswith("/")):
                if base not in created and not path_exists(root / base):
                    missing.append(base[:200])
    return missing, placeholders


def lint_bead(bead, ids, deps):
    """Findings for one bead. ids: every known bead id. deps: (dependent, prerequisite) pairs."""
    desc = bead.get("description") or ""
    acc = bead.get("acceptance_criteria") or ""
    if not acc and "ACCEPTANCE" in desc:
        acc = desc[desc.index("ACCEPTANCE") :]
    out = []

    def add(code, why):
        out.append({"id": bead["id"], "code": code, "why": why})

    if "WHAT" not in desc:
        add("no-what", "description has no WHAT: the observable change")
    if "WHY" not in desc:
        add("no-why", "description has no WHY: the measurement or failure behind it")
    if not acc.strip():
        add("no-acceptance", "no acceptance criteria")
    if bead.get("issue_type") != "epic":
        low = acc.lower()
        if not any(m in acc for m in COMMAND_MARKERS):
            add("no-command", "acceptance names no runnable command")
        if not any(m in low for m in NEGATIVE_MARKERS):
            add("no-negative", "acceptance has no planted negative or refusal case")
    if not has_source(desc + " " + acc):
        add(
            "no-source",
            "no checkable source: path, path:line, arXiv id, URL or commit sha",
        )
    missing, placeholders = command_problems(acc)
    if missing:
        add(
            "missing-path",
            f"command names {', '.join(sorted(set(missing)))}: not in the repo and not declared 'creates:'",
        )
    if placeholders:
        add("placeholder", f"command contains a placeholder: `{placeholders[0][:80]}`")
    for dependent, prereq in deps:
        if dependent == bead["id"] and prereq not in ids:
            add("dangling-dep", f"depends on {prereq}, which does not exist")
    return out


def load(epic, wanted, all_open):
    env = dict(os.environ, RUST_LOG="off")
    try:
        raw = subprocess.run(
            # --all: closed beads are valid prerequisites; without it every edge to a closed
            # bead read as dangling (2 false positives on jev-06wt, jev-ara9, 2026-10-04).
            ["br", "list", "--all", "--json", "--limit", "0"],
            cwd=REPO,
            capture_output=True,
            text=True,
            env=env,
            timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(
            f"bead-lint: br unavailable ({exc}); run from the jev checkout with br on PATH",
            file=sys.stderr,
        )
        sys.exit(69)
    try:
        issues = json.loads(raw.stdout)["issues"]
    except (ValueError, KeyError, TypeError):
        print(
            f"bead-lint: br list returned no issues (exit {raw.returncode}): {raw.stdout[:400].strip()}"
            " -- if SYNC_CONFLICT, run `br doctor` then `br doctor migrate-schema recover`",
            file=sys.stderr,
        )
        sys.exit(69)
    ids = {b["id"] for b in issues}
    # Read and close at once: a long-held read handle blocks br's WAL recovery (2026-10-04).
    db = sqlite3.connect(f"file:{REPO / '.beads/beads.db'}?mode=ro", uri=True)
    try:
        deps = list(
            db.execute(
                "select issue_id, depends_on_id from dependencies where type='blocks'"
            )
        )
    finally:
        db.close()
    live = [b for b in issues if b["status"] in ("open", "in_progress")]
    if epic:
        sel = [b for b in live if b["id"] == epic or b["id"].startswith(epic + ".")]
    elif wanted:
        sel = [b for b in issues if b["id"] in wanted]
    elif all_open:
        sel = live
    else:
        return None, ids, deps
    return sel, ids, deps


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--epic", help="lint the epic and its dotted children")
    p.add_argument("--ids", help="comma-separated bead ids")
    p.add_argument(
        "--all-open", action="store_true", help="lint every open or in-progress bead"
    )
    p.add_argument("--json", action="store_true", help="one JSON object on stdout")
    a = p.parse_args(argv)
    wanted = {i for i in (a.ids or "").split(",") if i}
    sel, ids, deps = load(a.epic, wanted, a.all_open)
    if sel is None:
        print(
            "bead-lint: name what to lint: --epic jev-b35c, --ids jev-a,jev-b, or --all-open",
            file=sys.stderr,
        )
        return 64
    findings = [f for b in sel for f in lint_bead(b, ids, deps)]
    if a.json:
        print(
            json.dumps(
                {"schema": "bead-lint.v1", "checked": len(sel), "findings": findings},
                sort_keys=True,
            )
        )
    else:
        for f in findings:
            print(f"{f['id']}\t{f['code']}\t{f['why']}")
        print(
            f"bead-lint: {len(sel)} checked, {len(findings)} findings", file=sys.stderr
        )
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
