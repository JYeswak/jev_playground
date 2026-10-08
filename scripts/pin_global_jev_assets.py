"""Create and rewrite immutable pin artifacts and loader entries."""
from __future__ import annotations

import json
import os
import posixpath
import stat
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pin_global_jev_common import (
    MAX_SOURCE_BYTES,
    PinError,
    SCHEMA,
    SDK_FALLBACK,
    SDK_PACKAGE,
    SDK_PINNED,
    SDK_REL,
    git_blob,
    sha256,
)
from pin_global_jev_scan import (
    extension_refs,
    module_literals,
    normalize_repo_target,
    repo_rel,
    resolve_extension,
)


def sdk_files(repo: Path, commit: str, tree: dict[str, str]) -> tuple[dict[str, bytes], str] | None:
    lock_path = "work/sdk/package-lock.json"
    if lock_path not in tree:
        raise PinError(f"SDK package lock is absent from commit {commit}")
    try:
        lock = json.loads(git_blob(repo, commit, lock_path))
        version = lock["packages"]["node_modules/@typesafe-ai/sdk"]["version"]
    except (json.JSONDecodeError, KeyError, TypeError) as error:
        raise PinError(f"SDK version is not bound by {lock_path}") from error
    source = repo / SDK_REL
    if source.is_symlink() or not source.is_dir():
        raise PinError(f"pinned SDK dependency is not installed as a real directory: {source}")
    package_json = source / "package.json"
    if not package_json.is_file():
        raise PinError(f"installed SDK package lacks package.json: {source}")
    try:
        installed = json.loads(package_json.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as error:
        raise PinError("installed SDK package metadata is unreadable") from error
    if installed.get("name") != SDK_PACKAGE or installed.get("version") != version:
        raise PinError(f"installed SDK version does not match locked version {version}")
    files: dict[str, bytes] = {}
    for current, directories, names in os.walk(source, followlinks=False):
        current_path = Path(current)
        for directory in directories:
            if (current_path / directory).is_symlink():
                raise PinError(f"SDK package contains a symlink: {current_path / directory}")
        for name in names:
            path = current_path / name
            if path.is_symlink() or not path.is_file():
                raise PinError(f"SDK package contains a non-regular file: {path}")
            rel = path.relative_to(source).as_posix()
            data = path.read_bytes()
            if len(data) > MAX_SOURCE_BYTES:
                raise PinError(f"SDK package file exceeds the copy bound: {rel}")
            files[rel] = data
    if not files:
        raise PinError("installed SDK package is empty")
    return files, version


def rewritten_source(repo: Path, pin_repo: Path, rel: str, data: bytes) -> bytes:
    source = data.decode("utf-8")
    replacements: list[tuple[int, int, str]] = []
    for spec, start, end in module_literals(source):
        if not spec.startswith(str(repo) + "/"):
            continue
        target = normalize_repo_target(rel, spec, repo)
        if target is None:
            raise PinError(f"cannot rewrite absolute checkout import in {rel}: {spec}")
        if not (pin_repo / target).resolve(strict=False).is_relative_to(pin_repo):
            raise PinError(f"rewritten import escapes pinned root: {rel}: {spec}")
        relative = posixpath.relpath(target, posixpath.dirname(rel))
        if not relative.startswith("."):
            relative = "./" + relative
        replacements.append((start, end, relative))
    for start, end, value in reversed(replacements):
        source = source[:start] + value + source[end:]
    if rel == "kit/src/client.ts" and SDK_FALLBACK in source:
        source = source.replace(SDK_FALLBACK, SDK_PINNED)
    for spec, _start, _end in module_literals(source):
        if spec.startswith(str(repo) + "/"):
            raise PinError(f"checkout import remains after rewrite in {rel}: {spec}")
    return source.encode("utf-8")


def atomic_write(path: Path, data: bytes, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temp = Path(temp_name)
    try:
        os.fchmod(fd, mode)
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
        directory_fd = os.open(path.parent, os.O_RDONLY)  # ubs:ignore — closed in the finally block below.
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    except BaseException:
        try:
            os.close(fd)
        except OSError:
            pass
        try:
            temp.unlink()
        except FileNotFoundError:
            pass
        raise


def write_pin_file(root: Path, rel: str, data: bytes) -> None:
    path = root / rel
    if not path.resolve(strict=False).is_relative_to(root.resolve()):
        raise PinError(f"pin destination escapes pinned root: {rel}")
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.write_bytes(data)
    path.chmod(0o600 if "rollback/" in rel else 0o644)


def yaml_scalar(value: str, quote: str) -> str:
    if quote == "'":
        return value.replace("'", "''")
    if quote == '"':
        return json.dumps(value, ensure_ascii=False)[1:-1]
    if any(char.isspace() for char in value) or "#" in value or ":" in value:
        return json.dumps(value, ensure_ascii=False)
    return value


def rewrite_config(config: Path, repo: Path, pin_repo: Path, home: Path) -> tuple[bytes, bytes, list[str]]:
    before = config.read_bytes()
    text = before.decode("utf-8")
    refs = extension_refs(config, text)
    edits = []
    changes = []
    for ref in refs:
        target = resolve_extension(ref["value"], config, home, repo)
        source_rel = repo_rel(target, repo)
        if source_rel is None:
            continue
        replacement = str(pin_repo / source_rel)
        edits.append((ref["start"], ref["end"], yaml_scalar(replacement, ref["quote"])))
        changes.append(source_rel)
    for start, end, value in reversed(edits):
        text = text[:start] + value + text[end:]
    return before, text.encode("utf-8"), changes


def hook_wrapper(pin_root: Path, source_rel: str) -> bytes:
    target = pin_root / "repo" / source_rel
    return f"export {{ default }} from {json.dumps(str(target))};\n".encode()




def create_manifest(
    repo: Path,
    pin_root: Path,
    plan: dict[str, Any],
    sdk: tuple[dict[str, bytes], str] | None,
) -> dict[str, Any]:
    files: dict[str, str] = {}
    for rel in plan["closure"]:
        source = git_blob(repo, plan["commit"], rel)
        transformed = rewritten_source(repo, pin_root / "repo", rel, source)
        destination_rel = f"repo/{rel}"
        write_pin_file(pin_root, destination_rel, transformed)
        files[destination_rel] = sha256(transformed)
    sdk_version = None
    if plan["external_sdk"]:
        if sdk is None:
            raise PinError("SDK was detected in the import closure but cannot be copied")
        sdk_tree, sdk_version = sdk
        for rel, data in sorted(sdk_tree.items()):
            destination_rel = f"repo/{SDK_REL}/{rel}"
            write_pin_file(pin_root, destination_rel, data)
            files[destination_rel] = sha256(data)
    return {
        "schema": SCHEMA,
        "commit": plan["commit"],
        "repo": str(repo),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "closure": plan["closure"],
        "files": files,
        "sdk_version": sdk_version,
        "config_changes": [],
        "hook_changes": [],
    }

def change_record(
    repo: Path,
    commit: str,
    path: Path,
    before: bytes,
    after: bytes,
    home: Path,
    pin_root: Path,
    source_rel: str | None = None,
) -> dict[str, Any]:
    try:
        mode = stat.S_IMODE(path.stat().st_mode)
        info = path.stat()
    except OSError as error:
        raise PinError(f"cannot inspect installed target {path}: {error}") from error
    backup_rel = f"rollback/{sha256(str(path).encode())}.bin"
    write_pin_file(pin_root, backup_rel, before)
    return {
        "path": str(path),
        "home_relative": path.relative_to(home).as_posix(),
        "backup": backup_rel,
        "before_sha256": sha256(before),
        "after_sha256": sha256(after),
        "mode": mode,
        "source_rel": source_rel,
        "source_sha256": sha256(git_blob(repo, commit, source_rel)) if source_rel else None,
        "original_inode": info.st_ino,
        "original_device": info.st_dev,
        "original_nlink": info.st_nlink,
    }
