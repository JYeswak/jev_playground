#!/usr/bin/env python3
"""Run ax_prune.py against the planner and floor pinned at the preregistration commit.

jev-jy7t.1.6. ax_prune.py imports work/miniwob-jev/jev_arm.py and
work/game-floors/miniwob/run.py from the working tree, and pane 5 edits both files
there without committing. This launcher changes no arm, seed, bar, or row path. It
does three things:

1. Exports the bytes of both files, plus tasks.json, from PIN_COMMIT to a frozen tree
   under /tmp. The tree mirrors the repo layout, so jev_arm.py's own FLOOR_PATH
   resolves to the frozen run.py. It refuses to start if any sha256 differs from PINS.
2. Redirects ax_prune's two module loads to those frozen files, then calls
   ax_prune.main() unchanged. Rows still go to the preregistered paths.
3. Stops the run before the next episode after any HTTP 401/402/403. The floor records
   a request error in the row and moves on, so without this stop a 402 would repeat
   once per remaining task. It also counts HTTP attempts, SDK retries included, from
   the SDK's INFO log. Headers are logged only at DEBUG and are never captured.

Usage: run_frozen.py run --split dev --arm full --out work/miniwob-ax-prune/rows/dev-full.jsonl
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import logging
import os
import re
import signal
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
PIN_COMMIT = "dd04baf"
FROZEN_ROOT = Path("/tmp/jev-ax-prune-frozen") / PIN_COMMIT
PINS = {
    "work/miniwob-jev/jev_arm.py": "f6f712fe441cf3ac",
    "work/game-floors/miniwob/run.py": "e0b0c42886e4ba17",
    "work/game-floors/miniwob/tasks.json": "af8890bf4877515c",
}
HALT_STATUSES = {401, 402, 403}
ACCOUNT_PATH = FROZEN_ROOT / "http-accounting.jsonl"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def freeze() -> dict[str, str]:
    """Write the pinned bytes to FROZEN_ROOT; return full sha256 per repo path."""
    shas: dict[str, str] = {}
    for rel, prefix in PINS.items():
        data = subprocess.run(
            ["git", "-C", str(ROOT), "show", f"{PIN_COMMIT}:{rel}"],
            check=True,
            capture_output=True,
        ).stdout
        digest = _sha(data)
        if not digest.startswith(prefix):
            raise SystemExit(
                f"REFUSE: {PIN_COMMIT}:{rel} sha256 {digest[:16]} != {prefix}"
            )
        dest = FROZEN_ROOT / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists() or _sha(dest.read_bytes()) != digest:
            dest.write_bytes(data)
        if _sha(dest.read_bytes()) != digest:
            raise SystemExit(f"REFUSE: frozen copy {dest} does not match {digest[:16]}")
        shas[rel] = digest
    return shas


class _HttpCounter(logging.Handler):
    """Counts SDK response lines ('POST <url> <- <status> in ...') by status."""

    PATTERN = re.compile(r"<- (\d{3}) in ")

    def __init__(self):
        super().__init__(logging.INFO)
        self.by_status: dict[int, int] = {}
        self.connection_errors = 0

    def emit(self, record: logging.LogRecord) -> None:
        msg = record.getMessage()
        m = self.PATTERN.search(msg)
        if m:
            status = int(m.group(1))
            self.by_status[status] = self.by_status.get(status, 0) + 1
        elif " <- " in msg:
            self.connection_errors += 1


def main(argv: list[str]) -> int:
    if os.environ.get("MINIWOB_V3"):
        raise SystemExit("REFUSE: MINIWOB_V3 must be unset for the preregistered run")
    shas = freeze()
    redirect = {
        (ROOT / rel).resolve(): FROZEN_ROOT / rel
        for rel in ("work/miniwob-jev/jev_arm.py", "work/game-floors/miniwob/run.py")
    }
    real_spec = importlib.util.spec_from_file_location

    def pinned_spec(name, location=None, *args, **kwargs):
        if location is not None and Path(location).resolve() in redirect:
            location = redirect[Path(location).resolve()]
        return real_spec(name, location, *args, **kwargs)

    importlib.util.spec_from_file_location = pinned_spec
    try:
        spec = real_spec("miniwob_ax_prune", HERE / "ax_prune.py")
        ax = importlib.util.module_from_spec(spec)
        sys.modules["miniwob_ax_prune"] = ax
        spec.loader.exec_module(ax)
    finally:
        importlib.util.spec_from_file_location = real_spec

    for mod, rel in (
        (ax.floor, "work/game-floors/miniwob/run.py"),
        (ax.jev_v1, "work/miniwob-jev/jev_arm.py"),
        (ax.jev_v1.floor, "work/game-floors/miniwob/run.py"),
    ):
        loaded = Path(mod.__file__).resolve()
        if (
            loaded != (FROZEN_ROOT / rel).resolve()
            or _sha(loaded.read_bytes()) != shas[rel]
        ):
            raise SystemExit(
                f"REFUSE: {mod.__name__} loaded from {loaded}, not the frozen pin"
            )

    counter = _HttpCounter()
    sdk_log = logging.getLogger("typesafe_sdk")
    sdk_log.setLevel(logging.INFO)
    sdk_log.addHandler(counter)
    sdk_log.propagate = False

    real_episode = ax.floor.run_episode
    frozen = {rel: sha[:16] for rel, sha in shas.items()}

    stop_first = os.environ.get("AX_PRUNE_STOP_BEFORE_FIRST_EPISODE") == "1"
    episodes = 0

    def guarded_episode(*args, **kwargs):
        nonlocal episodes
        halted = sorted(s for s in counter.by_status if s in HALT_STATUSES)
        if halted:
            raise SystemExit(f"HALT: HTTP {halted} seen; no further episode started")
        if stop_first and episodes == 0:
            # The row file is open and no request has been sent: an operator can lsof
            # this pid, then `kill -CONT` it.
            print(f"STOPPED pid={os.getpid()}", file=sys.stderr, flush=True)
            os.kill(os.getpid(), signal.SIGSTOP)
        episodes += 1
        row = real_episode(*args, **kwargs)
        row["frozen_sources_sha256_16"] = frozen
        row["frozen_pin_commit"] = PIN_COMMIT
        return row

    ax.floor.run_episode = guarded_episode
    print(
        json.dumps({"pid": os.getpid(), "frozen": frozen, "pin": PIN_COMMIT}),
        file=sys.stderr,
        flush=True,
    )
    rc = 1
    try:
        rc = ax.main(argv)
        return rc
    finally:
        entry = {
            "argv": argv,
            "pid": os.getpid(),
            "rc": rc,
            "http_by_status": {str(k): v for k, v in sorted(counter.by_status.items())},
            "http_attempts": sum(counter.by_status.values())
            + counter.connection_errors,
            "connection_errors": counter.connection_errors,
        }
        with ACCOUNT_PATH.open("a", encoding="utf-8") as out:
            out.write(json.dumps(entry, sort_keys=True) + "\n")
        print(json.dumps(entry), file=sys.stderr, flush=True)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
