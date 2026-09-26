#!/usr/bin/env python3
"""Crash-safe JSONL checkpointing and detached command supervision."""

from __future__ import annotations

import argparse
import asyncio
import inspect
import hashlib
import json
import os
import subprocess
import sys
import threading
import time
from collections.abc import Awaitable, Callable, Iterable, Mapping
from pathlib import Path
from typing import Any, TypeVar

T = TypeVar("T", bound=Mapping[str, Any])


def _repair_trailing_line(path: Path) -> None:
    if not path.exists():
        return
    with path.open("r+b") as stream:
        data = stream.read()
        if not data or data.endswith(b"\n"):
            return
        newline = data.rfind(b"\n")
        stream.truncate(max(newline + 1, 0))


def _completed_ids(path: Path, id_key: str) -> set[str]:
    if not path.exists():
        return set()
    completed: set[str] = set()
    for line_number, line in enumerate(path.read_text().splitlines(), 1):
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid checkpoint row {path}:{line_number}") from exc
        if not isinstance(row, dict) or id_key not in row:
            raise ValueError(f"checkpoint row {path}:{line_number} has no {id_key!r}")
        completed.add(str(row[id_key]))
    return completed


def verify_reachability(
    reach_path: str | os.PathLike[str], items_path: str | os.PathLike[str]
) -> None:
    """Refuse live work unless a reachable receipt matches the exact items file."""
    receipt_path = Path(reach_path)
    if not receipt_path.exists():
        raise RuntimeError(f"live run requires --reach receipt: {receipt_path}")
    try:
        receipt = json.loads(receipt_path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"invalid --reach receipt: {receipt_path}") from exc
    if receipt.get("status") != "REACHABLE":
        raise RuntimeError(
            f"live run requires REACHABLE receipt, got {receipt.get('status')!r}"
        )
    expected = receipt.get("items_sha256")
    if not isinstance(expected, str) or not expected:
        raise RuntimeError("--reach receipt has no items_sha256")
    actual = hashlib.sha256(Path(items_path).read_bytes()).hexdigest()
    if actual != expected:
        raise RuntimeError("--reach receipt items_sha256 does not match the items file")


class StopRun(Exception):
    """Stop before the next item without writing a synthetic row."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


class StopAfterRow(Exception):
    """Write one completed row, then stop cleanly."""

    def __init__(self, row: Mapping[str, Any], reason: str) -> None:
        super().__init__(reason)
        self.row = row
        self.reason = reason


async def run(
    items: Iterable[T],
    fn: Callable[[T], Mapping[str, Any] | Awaitable[Mapping[str, Any]]],
    out_path: str | os.PathLike[str],
    *,
    id_key: str = "id",
    live: bool = False,
    reach: str | os.PathLike[str] | None = None,
    items_path: str | os.PathLike[str] | None = None,
) -> str | None:
    """Process items exactly once per checkpoint id and append each completed row.

    The completed row is flushed and fsynced before the next item starts. A restart
    repairs one trailing partial line and skips IDs already present in the file.
    """

    path = Path(out_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    _repair_trailing_line(path)
    if live:
        if reach is None or items_path is None:
            raise RuntimeError("live run requires --reach and items_path")
        verify_reachability(reach, items_path)
    completed = _completed_ids(path, id_key)
    with path.open("ab") as stream:
        for item in items:
            if id_key not in item:
                raise ValueError(f"item has no {id_key!r}")
            item_id = str(item[id_key])
            if item_id in completed:
                continue
            stop_reason: str | None = None
            try:
                result = fn(item)
                if inspect.isawaitable(result):
                    result = await result
            except StopRun as stop:
                return stop.reason
            except StopAfterRow as stop:
                result = stop.row
                stop_reason = stop.reason
            row = dict(result)
            row.setdefault(id_key, item[id_key])
            encoded = (
                json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n"
            ).encode()
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
            completed.add(item_id)
            if stop_reason is not None:
                return stop_reason


def run_sync(
    items: Iterable[T],
    fn: Callable[[T], Mapping[str, Any] | Awaitable[Mapping[str, Any]]],
    out_path: str | os.PathLike[str],
    *,
    id_key: str = "id",
) -> None:
    asyncio.run(run(items, fn, out_path, id_key=id_key))


def _looks_like_omp_child() -> bool:
    return any(os.environ.get(name) for name in ("OMP_SESSION_ID", "OMP_PANE_ID"))


def _write_heartbeat(path: Path, message: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{message} utc={time.time():.6f}\n")


def _child_main(pid_path: Path, heartbeat_path: Path, command: list[str]) -> int:
    pid_path.parent.mkdir(parents=True, exist_ok=True)
    pid_path.write_text(f"{os.getpid()}\n")
    stop = threading.Event()

    def heartbeat() -> None:
        while not stop.is_set():
            _write_heartbeat(heartbeat_path, "running")
            stop.wait(0.5)

    thread = threading.Thread(target=heartbeat, daemon=True)
    thread.start()
    try:
        return subprocess.run(command, check=False).returncode
    finally:
        stop.set()
        thread.join(timeout=1)
        _write_heartbeat(heartbeat_path, "stopped")


def run_detached(
    command: list[str],
    *,
    pid_path: str | os.PathLike[str],
    heartbeat_path: str | os.PathLike[str],
    attached: bool = False,
) -> int:
    """Launch a command in a new session with a PID and heartbeat contract."""

    if _looks_like_omp_child() and not attached:
        raise RuntimeError(
            "refusing detached launch from an omp pane; pass --attached explicitly"
        )
    if not command:
        raise ValueError("detached command is required")
    child = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--_child",
        "--pid-file",
        str(pid_path),
        "--heartbeat-file",
        str(heartbeat_path),
        "--",
        *command,
    ]
    process = subprocess.Popen(
        child,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
        close_fds=True,
    )
    Path(pid_path).parent.mkdir(parents=True, exist_ok=True)
    Path(pid_path).write_text(f"{process.pid}\n")
    return 0


def _main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--detach", action="store_true")
    parser.add_argument("--attached", action="store_true")
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--reach", type=Path)
    parser.add_argument("--items", type=Path)
    parser.add_argument("--pid-file", type=Path)
    parser.add_argument("--heartbeat-file", type=Path)
    parser.add_argument("--_child", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = list(args.command)
    if command and command[0] == "--":
        command = command[1:]
    if args.live:
        if args.reach is None or args.items is None:
            print("live run requires --reach RECEIPT and --items FILE", file=sys.stderr)
            return 2
        try:
            verify_reachability(args.reach, args.items)
        except RuntimeError as exc:
            print(str(exc), file=sys.stderr)
            return 2
    if not args.detach and not args._child:
        parser.error("pass --detach to supervise a command")
    if args.pid_file is None or args.heartbeat_file is None:
        parser.error("--pid-file and --heartbeat-file are required")
    if args._child:
        return _child_main(args.pid_file, args.heartbeat_file, command)
    try:
        return run_detached(
            command,
            pid_path=args.pid_file,
            heartbeat_path=args.heartbeat_file,
            attached=args.attached,
        )
    except (RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(_main())
