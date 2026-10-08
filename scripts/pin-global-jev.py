#!/usr/bin/env python3
"""Pin global Jev loaders to a copy of a committed Git tree.

Use --plan --json to inspect, --install --commit <sha> to pin, --check to audit,
and --rollback --commit <sha> to restore. Installation rewrites global OMP
configuration and hook files; restart or verify affected sessions afterward.
--repo and --home select isolated roots for tests.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from pin_global_jev_common import PinError, commit_id, git_tree
from pin_global_jev_ops import check, install, rollback
from pin_global_jev_scan import discover


def json_print(value: Any) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--plan", action="store_true")
    mode.add_argument("--install", action="store_true")
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--rollback", action="store_true")
    parser.add_argument("--commit")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--home", type=Path, default=Path.home())
    args = parser.parse_args(argv)
    repo = args.repo.resolve()
    home = args.home.resolve()
    try:
        if args.plan:
            sha = commit_id(repo, args.commit or "HEAD")
            result = discover(repo, home, sha, git_tree(repo, sha))
            if not args.json:
                result["rollback_command"] = None
            json_print(result)
            return 0
        if args.install:
            if not args.commit:
                raise PinError("--install requires --commit <sha>")
            result = install(repo, home, args.commit)
            json_print(result)
            return 0
        if args.rollback:
            if not args.commit:
                raise PinError("--rollback requires --commit <sha>")
            json_print(rollback(home, repo, args.commit))
            return 0
        result = check(home, repo)
        json_print(result)
        return 0 if result["ok"] else 1
    except (PinError, OSError, UnicodeError, json.JSONDecodeError) as error:
        print(f"pin-global-jev: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
