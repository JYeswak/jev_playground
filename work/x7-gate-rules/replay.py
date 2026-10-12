from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


def _read_pack(path: Path) -> list[dict[str, Any]]:
    if path.stat().st_mode & 0o077:
        raise ValueError("command pack permissions must be private")
    rows = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"invalid command pack row {number}") from error
        command = row.get("command")
        digest = row.get("cmd_sha")
        if not isinstance(command, str) or not isinstance(digest, str) or hashlib.sha256(command.encode()).hexdigest() != digest:
            raise ValueError(f"command digest mismatch at row {number}")
        rows.append(row)
    return rows


def _effects(repo: Path, before: set[str]) -> dict[str, int]:
    after = {p.relative_to(repo).as_posix() for p in repo.rglob("*") if p.is_file() and ".git" not in p.parts}
    return {"deleted": len(before - after), "created": len(after - before)}


def run_pack(*, repo: Path, commit: str, pack_path: Path, scratch_root: Path, receipt_path: Path, timeout_seconds: int, base_image: str) -> list[dict[str, Any]]:
    """Replay private prepare.py packs with event_id, cmd_sha, and command fields."""
    docker = shutil.which("docker")
    if not docker:
        raise RuntimeError("docker is required for isolated replay")
    source = repo.resolve()
    scratch = scratch_root.resolve()
    if source == scratch or scratch not in receipt_path.resolve().parents:
        raise ValueError("repo and scratch/receipt paths must be isolated")
    check = subprocess.run(["git", "-C", str(source), "rev-parse", "HEAD"], check=True, capture_output=True, text=True, timeout=timeout_seconds).stdout.strip()
    if check != commit:
        raise ValueError("source commit mismatch")
    commands = _read_pack(pack_path)
    image = subprocess.run([docker, "image", "inspect", base_image], capture_output=True, timeout=timeout_seconds)
    if image.returncode:
        raise RuntimeError("base image is unavailable")
    results = []
    receipts = []
    for row in commands:
        command = row["command"]
        worktree = scratch / f"event-{row['event_id']}"
        subprocess.run(["git", "-C", str(source), "worktree", "add", "--detach", "--force", str(worktree), commit], check=True, capture_output=True, timeout=timeout_seconds)
        try:
            before = {p.relative_to(worktree).as_posix() for p in worktree.rglob("*") if p.is_file() and ".git" not in p.parts}
            proc = subprocess.run([docker, "run", "--rm", "--network=none", "--read-only", "--tmpfs", "/tmp:rw,noexec,nosuid,size=64m", "--mount", f"type=bind,src={worktree},dst=/workspace", "--workdir", "/workspace", "--env", "HOME=/tmp", base_image, "sh", "-lc", command], capture_output=True, timeout=timeout_seconds, check=False)
            effects = _effects(worktree, before)
            result = {"event_id": row["event_id"], "status": "EXECUTED", "exit_code": proc.returncode, "effects": effects}
            results.append(result)
            receipts.append(json.dumps(result, sort_keys=True) + "\n")
        finally:
            subprocess.run(["git", "-C", str(source), "worktree", "remove", "--force", str(worktree)], check=False, capture_output=True)
    receipt_path.write_text("".join(receipts), encoding="utf-8")
    receipt_path.chmod(0o600)
    return results
