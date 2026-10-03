#!/usr/bin/env python3
"""Serialize shared-checkout Git index writes through one local daemon."""

from __future__ import annotations

import argparse
import json
import os
import queue
import socket
import socketserver
import subprocess
import sys
import threading
import time
import uuid
from concurrent.futures import Future
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import cast

# `sun_path` includes its NUL terminator: 104 bytes on Darwin, 108 on Linux.
MAX_UNIX_SOCKET_PATH_BYTES = 107 if sys.platform.startswith("linux") else 103
MAX_REQUEST_BYTES = 65536
MAX_PATHS = 50
REAL_GIT = "/usr/bin/git"


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [REAL_GIT, "-C", str(repo), *args],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


def repo_root(path: str) -> Path:
    result = subprocess.run(
        [REAL_GIT, "-C", path, "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    if result.returncode:
        raise ValueError(result.stderr.strip() or "not a git repository")
    return Path(result.stdout.strip()).resolve()


def state_paths(repo: Path) -> tuple[Path, Path]:
    git_dir_result = git(repo, "rev-parse", "--absolute-git-dir")
    if git_dir_result.returncode:
        raise ValueError(
            git_dir_result.stderr.strip() or "cannot resolve git directory"
        )
    git_dir = Path(git_dir_result.stdout.strip()).resolve()
    # Preserve the old address where it fits; deep roots need a compact socket name.
    socket_path = git_dir / "jev-commitd.sock"
    if len(os.fsencode(socket_path)) > MAX_UNIX_SOCKET_PATH_BYTES:
        socket_path = git_dir / "j.sock"
    if len(os.fsencode(socket_path)) > MAX_UNIX_SOCKET_PATH_BYTES:
        raise ValueError(
            "repository path is too long for the Unix-domain writer socket"
        )
    return socket_path, git_dir / "jev-commitd-receipts.jsonl"


def validate(request: object, repo: Path) -> str | None:
    if not isinstance(request, dict):
        return "request must be a JSON object"
    request_id = request.get("request_id")
    paths = request.get("paths")
    message = request.get("message")
    op = request.get("op")
    if op not in {"add", "commit"}:
        return "unsupported operation"
    if not isinstance(request_id, str) or not request_id or len(request_id) > 80:
        return "invalid request_id"
    if not isinstance(paths, list) or not paths or len(paths) > MAX_PATHS:
        return f"paths must be a non-empty list of at most {MAX_PATHS} entries"
    if any(
        not isinstance(path, str) or not path or path.startswith("-") for path in paths
    ):
        return "invalid path"
    if len(set(paths)) != len(paths):
        return "duplicate path"
    for raw in paths:
        path = PurePosixPath(raw)
        if path.is_absolute() or any(
            part in {".", "..", ".git"} for part in raw.split("/")
        ):
            return "path escapes or targets git metadata"
        if any(ord(char) < 32 for char in raw):
            return "control characters are not allowed in paths"
        resolved = (repo / raw).resolve()
        if not resolved.is_relative_to(repo) or not resolved.is_file():
            return "path is outside the repo or is not a file"
    if op == "commit" and (
        not isinstance(message, str) or not message.strip() or len(message) > 200
    ):
        return "invalid commit message"
    if op == "add" and message is not None:
        return "add does not accept a commit message"
    return None


class CommitServer(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, socket_path: Path, repo: Path, receipt_path: Path) -> None:
        self.repo = repo
        self.receipt_path = receipt_path
        self.jobs: queue.Queue[
            tuple[dict[str, object], Future[dict[str, object]]] | None
        ] = queue.Queue(maxsize=32)
        self.requests: dict[str, tuple[str, Future[dict[str, object]]]] = {}
        self.requests_lock = threading.Lock()
        super().__init__(str(socket_path), RequestHandler)


def execute_job(server: CommitServer, request: dict[str, object]) -> dict[str, object]:
    op = str(request["op"])
    paths = cast(list[str], request["paths"])  # validated at the socket boundary
    if op == "add":
        added = git(server.repo, "add", "--", *paths)
        if added.returncode:
            return {
                "status": "refused",
                "error": added.stderr.strip() or "git add failed",
            }
        staged = git(server.repo, "diff", "--cached", "--name-only", "-z")
        actual = sorted(path for path in staged.stdout.split("\0") if path)
        if staged.returncode or not set(paths).issubset(actual):
            return {
                "status": "refused",
                "error": f"requested paths not staged: {actual!r}",
            }
        return {"status": "staged", "request_id": request["request_id"], "paths": paths}

    untracked = git(
        server.repo, "ls-files", "--others", "--exclude-standard", "-z", "--", *paths
    )
    if untracked.returncode:
        return {
            "status": "refused",
            "error": untracked.stderr.strip() or "cannot inspect untracked paths",
        }
    new_paths = [path for path in untracked.stdout.split("\0") if path]
    if new_paths:
        staged = git(server.repo, "add", "--", *new_paths)
        if staged.returncode:
            return {
                "status": "refused",
                "error": staged.stderr.strip() or "git add failed",
            }
    committed = git(
        server.repo, "commit", "--only", "-m", str(request["message"]), "--", *paths
    )
    if committed.returncode:
        reason = (
            committed.stderr.strip() or committed.stdout.strip() or "git commit failed"
        )
        return {"status": "refused", "error": reason}
    result = git(server.repo, "rev-parse", "HEAD")
    if result.returncode:
        return {
            "status": "committed_unverified",
            "error": result.stderr.strip() or "cannot read commit SHA",
        }
    sha = result.stdout.strip()
    changed = git(
        server.repo, "diff-tree", "--no-commit-id", "--name-only", "-r", "-z", sha
    )
    actual = sorted(path for path in changed.stdout.split("\0") if path)
    if changed.returncode or actual != sorted(paths):
        return {
            "status": "committed_path_mismatch",
            "request_id": request["request_id"],
            "sha": sha,
            "expected_paths": sorted(paths),
            "actual_paths": actual,
        }
    receipt = {
        "request_id": request["request_id"],
        "sha": sha,
        "paths": sorted(paths),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    with server.receipt_path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(receipt, sort_keys=True) + "\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.chmod(server.receipt_path, 0o600)
    print(f"COMMITTED {request['request_id']} {sha}", flush=True)
    return {
        "status": "committed",
        "request_id": request["request_id"],
        "sha": sha,
        "paths": sorted(paths),
    }


def writer(server: CommitServer) -> None:
    while True:
        item = server.jobs.get()
        if item is None:
            return
        request, future = item
        try:
            future.set_result(execute_job(server, request))
        except (OSError, subprocess.SubprocessError, ValueError) as exc:
            future.set_result(
                {"status": "refused", "error": f"{type(exc).__name__}: {exc}"}
            )


class RequestHandler(socketserver.StreamRequestHandler):
    def handle(self) -> None:
        raw = self.rfile.readline(MAX_REQUEST_BYTES + 1)
        if len(raw) > MAX_REQUEST_BYTES:
            self.reply({"status": "refused", "error": "request too large"})
            return
        try:
            request = json.loads(raw)
        except (ValueError, TypeError):
            self.reply({"status": "refused", "error": "invalid JSON"})
            return
        server = cast(CommitServer, self.server)
        if isinstance(request, dict) and request.get("op") == "health":
            self.reply({"status": "ready"})
            return
        if isinstance(request, dict) and request.get("op") == "shutdown":
            self.reply({"status": "stopping"})
            server.jobs.put(None)
            threading.Thread(target=server.shutdown, daemon=True).start()
            return
        error = validate(request, server.repo)
        if error:
            self.reply({"status": "refused", "error": error})
            return
        if not isinstance(request, dict):
            self.reply({"status": "refused", "error": "request must be a JSON object"})
            return
        request = cast(dict[str, object], request)
        payload = {
            key: request[key] for key in ("op", "paths", "message") if key in request
        }
        fingerprint = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        with server.requests_lock:
            prior = server.requests.get(str(request["request_id"]))
            if prior and prior[0] != fingerprint:
                self.reply(
                    {
                        "status": "refused",
                        "error": "request_id reused with different payload",
                    }
                )
                return
            if prior:
                future = prior[1]
            else:
                future = Future()
                server.requests[str(request["request_id"])] = (fingerprint, future)
                try:
                    server.jobs.put_nowait((request, future))
                except queue.Full:
                    del server.requests[str(request["request_id"])]
                    self.reply({"status": "refused", "error": "commit queue full"})
                    return
        try:
            self.reply(future.result(timeout=180))
        except (TimeoutError, OSError) as exc:
            self.reply({"status": "refused", "error": f"writer wait failed: {exc}"})

    def reply(self, value: dict[str, object]) -> None:
        self.wfile.write(json.dumps(value, sort_keys=True).encode("utf-8") + b"\n")


def serve(repo_arg: str) -> None:
    repo = repo_root(repo_arg)
    socket_path, receipt_path = state_paths(repo)
    server = CommitServer(socket_path, repo, receipt_path)
    os.chmod(socket_path, 0o600)
    worker = threading.Thread(
        target=writer, args=(server,), name="jev-single-git-writer", daemon=True
    )
    worker.start()
    print(f"READY pid={os.getpid()}", flush=True)
    try:
        server.serve_forever(poll_interval=0.1)
    finally:
        server.server_close()
        worker.join(timeout=30)


def send(
    socket_path: Path, payload: dict[str, object], timeout: float = 180
) -> dict[str, object]:
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
        connection.settimeout(timeout)
        connection.connect(str(socket_path))
        connection.sendall(json.dumps(payload).encode("utf-8") + b"\n")
        with connection.makefile("rb") as stream:
            line = stream.readline(MAX_REQUEST_BYTES + 1)
    if not line or len(line) > MAX_REQUEST_BYTES:
        raise OSError("daemon returned no valid response")
    try:
        response = json.loads(line)
    except ValueError as exc:
        raise OSError("daemon returned malformed JSON") from exc
    if not isinstance(response, dict):
        raise TypeError("daemon response must be an object")
    return response


def ensure_daemon(repo: Path, socket_path: Path) -> None:
    try:
        if send(socket_path, {"op": "health"}, timeout=0.2).get("status") == "ready":
            return
    except (OSError, ValueError):
        pass
    if os.environ.get("JEV_COMMITD_AUTOSTART", "1") == "0":
        raise RuntimeError("commit daemon unavailable; raw Git fallback is disabled")

    log_path = socket_path.with_suffix(".log")
    log = log_path.open("a", encoding="utf-8")
    os.chmod(log_path, 0o600)
    secret_markers = (
        "API_KEY",
        "ACCESS_KEY",
        "TOKEN",
        "SECRET",
        "PASSWORD",
        "CREDENTIAL",
    )
    daemon_env = {
        key: value
        for key, value in os.environ.items()
        if not any(marker in key.upper() for marker in secret_markers)
    }
    try:
        daemon = subprocess.Popen(
            [
                sys.executable,
                str(Path(__file__).resolve()),
                "serve",
                "--repo",
                str(repo),
            ],
            env=daemon_env,
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
            close_fds=True,
            text=True,
            encoding="utf-8",
        )
        # A concurrent client may win the socket bind; the health probe decides readiness.
        try:
            daemon.wait(timeout=0)
        except subprocess.TimeoutExpired:
            pass
    finally:
        log.close()
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        try:
            if (
                send(socket_path, {"op": "health"}, timeout=0.2).get("status")
                == "ready"
            ):
                return
        except (OSError, ValueError):
            time.sleep(0.05)
    raise RuntimeError(
        f"commit daemon unavailable at {socket_path}; raw Git fallback is disabled"
    )


def client(repo_arg: str, args: list[str]) -> int:
    repo = repo_root(repo_arg)
    socket_path, _ = state_paths(repo)
    if not args or args[0] not in {"add", "commit", "stop"}:
        raise ValueError("expected add, commit, or stop")
    op = args.pop(0)
    if op == "stop":
        response = send(socket_path, {"op": "shutdown"}, timeout=5)
    else:
        message: str | None = None
        paths: list[str] = []
        if op == "add":
            if args and args[0] == "--":
                args = args[1:]
            paths = args
        else:
            index = 0
            while index < len(args):
                arg = args[index]
                if arg == "--only":
                    index += 1
                elif arg in {"-m", "--message"} and index + 1 < len(args):
                    message = args[index + 1]
                    index += 2
                elif arg == "--":
                    paths = args[index + 1 :]
                    break
                else:
                    raise ValueError(f"unsupported commit argument: {arg}")
            if not paths:
                raise ValueError("commit requires explicit --only paths")
        payload: dict[str, object] = {
            "op": op,
            "request_id": str(uuid.uuid4()),
            "paths": paths,
        }
        if message is not None:
            payload["message"] = message
        ensure_daemon(repo, socket_path)
        response = send(socket_path, payload)
    status = response.get("status")
    if status not in {"committed", "staged", "stopping"}:
        print(
            f"git-commit-serialized: {response.get('error', response)}", file=sys.stderr
        )
        return 1
    print(json.dumps(response, sort_keys=True))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="mode", required=True)
    serve_parser = subparsers.add_parser("serve")
    serve_parser.add_argument("--repo", required=True)
    client_parser = subparsers.add_parser("client")
    client_parser.add_argument("--repo", required=True)
    client_parser.add_argument("args", nargs=argparse.REMAINDER)
    stop_parser = subparsers.add_parser("stop")
    stop_parser.add_argument("--repo", required=True)
    args = parser.parse_args()
    try:
        if args.mode == "serve":
            serve(args.repo)
            return 0
        if args.mode == "stop":
            return client(args.repo, ["stop"])
        return client(args.repo, args.args)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        print(f"git-commitd: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
