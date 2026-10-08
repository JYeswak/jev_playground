"""Install, inspect, and safely roll back a commit-pinned global Jev copy."""
from __future__ import annotations

import json
import os
import shlex
import sys
import tempfile
from pathlib import Path
from typing import Any

from pin_global_jev_assets import (
    atomic_write,
    change_record,
    create_manifest,
    hook_wrapper,
    rewrite_config,
    sdk_files,
    write_pin_file,
)
from pin_global_jev_common import (
    SCHEMA,
    PinError,
    commit_id,
    git_tree,
    sha256,
)
from pin_global_jev_scan import discover, module_literals


def install(repo: Path, home: Path, requested_commit: str) -> dict[str, Any]:
    commit = commit_id(repo, requested_commit)
    tree = git_tree(repo, commit)
    plan = discover(repo, home, commit, tree)
    if not plan["closure"]:
        raise PinError("no global Jev entrypoint resolves into this checkout")
    omp_home = home / ".omp"
    pin_parent = omp_home / "jev-pinned"
    pin_parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    active_path = pin_parent / "active.json"
    if active_path.exists():
        try:
            active = json.loads(active_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise PinError("active pin marker is unreadable") from error
        if active.get("status") == "installed":
            if active.get("commit") == commit:
                checked = check(home, repo)
                if checked["ok"]:
                    return {"status": "already-installed", "commit": commit, "check": checked}
            raise PinError("another pin is active or has drift; rollback it before installing")
    pin_root = pin_parent / commit
    if pin_root.exists():
        raise PinError(f"pin directory already exists; refusing to overwrite: {pin_root}")
    sdk = sdk_files(repo, commit, tree) if plan["external_sdk"] else None
    temp_root = Path(tempfile.mkdtemp(prefix=f".{commit}.install.", dir=pin_parent))
    temp_root.chmod(0o700)
    try:
        manifest = create_manifest(repo, temp_root, plan, sdk)
        final_root = pin_root
        changes: list[tuple[str, Path, bytes, bytes, dict[str, Any]]] = []
        for config_row in plan["configs"]:
            config = Path(config_row["path"])
            before, after, _replaced = rewrite_config(config, repo, final_root / "repo", home)
            if before != after:
                record = change_record(repo, commit, config, before, after, home, temp_root)
                changes.append(("config", config, before, after, record))
        for hook in plan["hooks"]:
            target = Path(hook["path"])
            before = target.read_bytes()
            after = hook_wrapper(final_root, hook["source"])
            record = change_record(repo, commit, target, before, after, home, temp_root, hook["source"])
            changes.append(("hook", target, before, after, record))
        manifest["config_changes"] = [record for kind, _path, _before, _after, record in changes if kind == "config"]
        manifest["hook_changes"] = [record for kind, _path, _before, _after, record in changes if kind == "hook"]
        checksum_lines = [f"{digest}  {path}" for path, digest in sorted(manifest["files"].items())]
        write_pin_file(temp_root, "MANIFEST.sha256", ("\n".join(checksum_lines) + "\n").encode("utf-8"))
        write_pin_file(temp_root, "MANIFEST.json", json.dumps(manifest, indent=2, sort_keys=True).encode("utf-8") + b"\n")
        os.replace(temp_root, pin_root)
        changed: list[tuple[Path, bytes, int]] = []
        try:
            for _kind, path, before, after, record in changes:
                atomic_write(path, after, int(record["mode"]))
                changed.append((path, before, int(record["mode"])))
            marker = {"schema": SCHEMA, "status": "installed", "commit": commit}
            atomic_write(active_path, json.dumps(marker, indent=2, sort_keys=True).encode("utf-8") + b"\n", 0o600)
        except BaseException:
            for path, before, mode in reversed(changed):
                atomic_write(path, before, mode)
            raise
    except BaseException:
        if temp_root.exists():
            # Leave owned diagnostic files intact; installation has not changed active paths.
            pass
        raise
    return {
        "status": "installed",
        "commit": commit,
        "pin_root": str(pin_root),
        "closure_files": len(manifest["closure"]),
        "external_sdk_version": manifest["sdk_version"],
        "rollback_command": shlex.join(
            [
                sys.executable,
                str(Path(__file__).with_name("pin-global-jev.py").resolve()),
                "--home",
                str(home),
                "--repo",
                str(repo),
                "--rollback",
                "--commit",
                commit,
            ]
        ),
    }


def check(home: Path, repo: Path) -> dict[str, Any]:
    pin_parent = home / ".omp" / "jev-pinned"
    active_path = pin_parent / "active.json"
    problems: list[str] = []
    if not active_path.is_file():
        problems.append("no active pin marker")
        active: dict[str, Any] = {}
    else:
        try:
            loaded = json.loads(active_path.read_text(encoding="utf-8"))
            active = loaded if isinstance(loaded, dict) else {}
            if not active:
                problems.append("active pin marker is not an object")
        except (OSError, json.JSONDecodeError):
            active = {}
            problems.append("active pin marker is unreadable")
    if active.get("status") != "installed":
        problems.append("no installed pin is active")
    raw_commit = active.get("commit")
    commit: str | None = None
    if isinstance(raw_commit, str):
        try:
            commit = commit_id(repo, raw_commit)
            if commit != raw_commit:
                problems.append("active pin commit is not a full object id")
                commit = None
        except PinError as error:
            problems.append(f"active pin commit is invalid: {error}")
    pin_root = pin_parent / commit if commit else pin_parent / "unavailable"
    manifest: dict[str, Any] = {}
    if commit:
        manifest_path = pin_root / "MANIFEST.json"
        try:
            loaded = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest = loaded if isinstance(loaded, dict) else {}
            if not manifest:
                problems.append("pin manifest is not an object")
        except (OSError, json.JSONDecodeError):
            problems.append("pin manifest is missing or unreadable")
        if manifest.get("schema") != SCHEMA or manifest.get("commit") != commit:
            problems.append("pin manifest identity does not match active marker")
        files = manifest.get("files", {})
        if not isinstance(files, dict):
            files = {}
            problems.append("pin manifest files field is invalid")
        checksums_path = pin_root / "MANIFEST.sha256"
        expected_checksums = "".join(f"{digest}  {rel}\n" for rel, digest in sorted(files.items()))
        try:
            actual_checksums = checksums_path.read_text(encoding="utf-8")
        except OSError:
            actual_checksums = ""
            problems.append("MANIFEST.sha256 is missing")
        if actual_checksums != expected_checksums:
            problems.append("MANIFEST.sha256 does not match manifest entries")
        for rel, expected in files.items():
            path = (pin_root / rel).resolve(strict=False)
            if not path.is_relative_to(pin_root.resolve()):
                problems.append(f"pinned manifest path escapes root: {rel}")
                continue
            try:
                actual = sha256(path.read_bytes())
            except OSError:
                problems.append(f"pinned file missing: {rel}")
                continue
            if actual != expected:
                problems.append(f"pinned file digest mismatch: {rel}")
        for kind in ("config_changes", "hook_changes"):
            rows = manifest.get(kind, [])
            if not isinstance(rows, list):
                problems.append(f"pin manifest {kind} field is invalid")
                continue
            for row in rows:
                if not isinstance(row, dict) or not isinstance(row.get("path"), str):
                    problems.append(f"pin manifest contains an invalid {kind} row")
                    continue
                path = Path(row["path"])
                if not path.resolve(strict=False).is_relative_to(home):
                    problems.append(f"installed path escapes home: {path}")
                    continue
                try:
                    actual = sha256(path.read_bytes())
                except OSError:
                    problems.append(f"installed file missing: {path}")
                    continue
                if actual != row.get("after_sha256"):
                    problems.append(f"installed file drift: {path}")
        closure = manifest.get("closure", [])
        if not isinstance(closure, list):
            problems.append("pin manifest closure field is invalid")
            closure = []
        for rel in closure:
            if not isinstance(rel, str):
                problems.append("pin manifest contains an invalid closure path")
                continue
            path = (pin_root / "repo" / rel).resolve(strict=False)
            if not path.is_relative_to(pin_root.resolve()):
                problems.append(f"pinned closure path escapes root: {rel}")
                continue
            try:
                source = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                problems.append(f"pinned closure source is unreadable: {rel}")
                continue
            for spec, _start, _end in module_literals(source):
                if spec.startswith(str(repo) + "/"):
                    problems.append(f"pinned import resolves into working tree: {rel}: {spec}")
    try:
        scan_commit = commit or commit_id(repo, "HEAD")
        tree = git_tree(repo, scan_commit)
        current = discover(repo, home, scan_commit, tree)
        for config in current["configs"]:
            for entry in config["entries"]:
                if entry["source"] is not None:
                    problems.append(f"global extension still resolves into working tree: {config['path']}:{entry['line']}")
        for hook in current["hooks"]:
            problems.append(f"global hook still resolves into working tree: {hook['path']}")
    except PinError as error:
        problems.append(str(error))
    return {"ok": not problems, "commit": commit, "problems": problems, "pin_root": str(pin_root)}


def rollback(home: Path, repo: Path, requested_commit: str) -> dict[str, Any]:
    pin_parent = home / ".omp" / "jev-pinned"
    active_path = pin_parent / "active.json"
    try:
        active = json.loads(active_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise PinError("active pin marker is unreadable") from error
    if not isinstance(active, dict):
        raise PinError("active pin marker is not an object")
    commit = str(active.get("commit", ""))
    requested = commit_id(repo, requested_commit)
    if active.get("schema") != SCHEMA or active.get("status") != "installed" or commit != requested:
        raise PinError("requested commit is not the active pin")
    pin_root = pin_parent / commit
    try:
        manifest = json.loads((pin_root / "MANIFEST.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise PinError("pin manifest is unreadable") from error
    if not isinstance(manifest, dict) or manifest.get("schema") != SCHEMA or manifest.get("commit") != commit:
        raise PinError("pin manifest identity does not match active marker")
    config_changes = manifest.get("config_changes", [])
    hook_changes = manifest.get("hook_changes", [])
    if not isinstance(config_changes, list) or not isinstance(hook_changes, list):
        raise PinError("pin manifest rollback entries are invalid")
    restores: list[tuple[Path, bytes, int, dict[str, Any]]] = []
    for row in config_changes + hook_changes:
        if not isinstance(row, dict) or not isinstance(row.get("path"), str) or not isinstance(row.get("backup"), str):
            raise PinError("pin manifest contains an invalid rollback entry")
        path = Path(row["path"])
        backup_path = (pin_root / row["backup"]).resolve(strict=False)
        if not path.resolve(strict=False).is_relative_to(home) or not backup_path.is_relative_to(pin_root.resolve()):
            raise PinError(f"rollback path escapes its owned root: {path}")
        try:
            current = path.read_bytes()
            saved = backup_path.read_bytes()
        except OSError as error:
            raise PinError(f"rollback file is missing: {path}") from error
        if sha256(current) != row.get("after_sha256"):
            raise PinError(f"refusing to overwrite post-install change: {path}")
        if sha256(saved) != row.get("before_sha256"):
            raise PinError(f"rollback snapshot digest mismatch: {path}")
        restores.append((path, saved, int(row["mode"]), row))
    for path, saved, mode, row in restores:
        source_rel = row.get("source_rel")
        source = repo / source_rel if isinstance(source_rel, str) else None
        if source and source.is_file() and sha256(source.read_bytes()) == row.get("source_sha256") and row.get("original_nlink", 0) > 1:
            temporary = path.with_name(f".{path.name}.rollback.{os.getpid()}")
            try:
                os.link(source, temporary)
                os.replace(temporary, path)
            except OSError:
                if temporary.exists():
                    temporary.unlink()
                atomic_write(path, saved, mode)
        else:
            atomic_write(path, saved, mode)
    marker = {"schema": SCHEMA, "status": "rolled_back", "commit": commit}
    atomic_write(active_path, json.dumps(marker, indent=2, sort_keys=True).encode("utf-8") + b"\n", 0o600)
    return {"status": "rolled_back", "commit": commit, "restored_files": len(restores)}
