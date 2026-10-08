"""Shared commit and digest primitives for the global Jev pin utility."""
from __future__ import annotations

import hashlib
import subprocess  # ubs:ignore — only runs the fixed git executable with argv and no shell.
from pathlib import Path

SOURCE_SUFFIXES = {".cjs", ".js", ".jsx", ".mjs", ".mts", ".cts", ".ts", ".tsx"}
SDK_REL = "work/sdk/node_modules/@typesafe-ai/sdk"
SDK_PACKAGE = "@typesafe-ai/sdk"
SDK_FALLBACK = "../node_modules/@typesafe-ai/sdk/dist/index.mjs"
SDK_PINNED = "../../work/sdk/node_modules/@typesafe-ai/sdk/dist/index.mjs"
SCHEMA = "jev-global-pin.v1"
MAX_SOURCE_BYTES = 4 * 1024 * 1024
MAX_CLOSURE_FILES = 200


class PinError(Exception):
    """An unsafe or incomplete pin operation."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run_git(repo: Path, *args: str, text: bool = True) -> str | bytes:
    try:
        result = subprocess.run(  # ubs:ignore — fixed git executable; repository arguments are passed without a shell.
            ["git", "-C", str(repo), *args],
            check=False,
            capture_output=True,
            text=text,
            timeout=30,
        )
    except subprocess.TimeoutExpired as error:
        raise PinError(f"git {' '.join(args[:3])} timed out") from error
    if result.returncode:
        detail = result.stderr.strip() if text else "git object read failed"
        raise PinError(f"git {' '.join(args[:3])} failed: {detail}")
    return result.stdout


def commit_id(repo: Path, requested: str) -> str:
    resolved = str(run_git(repo, "rev-parse", "--verify", f"{requested}^{{commit}}")).strip()
    if len(resolved) not in (40, 64) or any(ch not in "0123456789abcdef" for ch in resolved.lower()):
        raise PinError("commit did not resolve to a full Git object id")
    return resolved.lower()


def git_tree(repo: Path, commit: str) -> dict[str, str]:
    raw = run_git(repo, "ls-tree", "-r", "-z", commit, text=False)
    if not isinstance(raw, bytes):
        raise PinError("git returned text for a binary tree listing")
    files: dict[str, str] = {}
    for record in raw.split(b"\0"):
        if not record:
            continue
        metadata, encoded_path = record.split(b"\t", 1)
        mode, kind, _object = metadata.decode("ascii").split(" ", 2)
        rel = encoded_path.decode("utf-8")
        if kind == "blob" and mode != "120000":
            files[rel] = mode
    return files


def git_blob(repo: Path, commit: str, rel: str) -> bytes:
    data = run_git(repo, "show", f"{commit}:{rel}", text=False)
    if not isinstance(data, bytes):
        raise PinError("git returned text for a binary blob")
    if len(data) > MAX_SOURCE_BYTES:
        raise PinError(f"source file exceeds the {MAX_SOURCE_BYTES}-byte copy bound: {rel}")
    return data
