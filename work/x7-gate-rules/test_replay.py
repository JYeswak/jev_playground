"""Behavioral tests for isolated, offline command replay."""

from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import json
import os
import shlex
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import ModuleType
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRATCH_PARENT = REPO_ROOT / "var" / "agent-tmp"


@contextlib.contextmanager
def owned_scratch():
    with tempfile.TemporaryDirectory(prefix="x7-replay-test.", dir=SCRATCH_PARENT) as temp:
        root = Path(temp)
        root.chmod(0o700)
        (root / ".owner").write_text(f"pid={os.getpid()} label=x7-replay-test repo={REPO_ROOT}\n")
        yield root


def load_module(name: str) -> ModuleType | None:
    path = Path(__file__).with_name(f"{name}.py")
    if not path.exists():
        return None
    spec = importlib.util.spec_from_file_location(f"_x7_{name}", path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


replay = load_module("replay")


def make_repo(root: Path) -> tuple[Path, str]:
    repo = root / "source"
    repo.mkdir()
    subprocess.run(["git", "init", "--quiet", str(repo)], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "X7 test"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "x7@example.invalid"], check=True)
    (repo / "tracked.txt").write_text("committed source\n")
    subprocess.run(["git", "-C", str(repo), "add", "tracked.txt"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "--quiet", "-m", "fixture"], check=True)
    commit = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    return repo, commit


def write_pack(path: Path, commands: list[str]) -> None:
    with path.open("w", encoding="utf-8") as stream:
        for index, command in enumerate(commands):
            stream.write(json.dumps({
                "event_id": f"event-{index}",
                "command": command,
                "cmd_sha256": hashlib.sha256(command.encode()).hexdigest(),
            }, sort_keys=True) + "\n")
    path.chmod(0o600)


def docker_ready() -> bool:
    return bool(shutil.which("docker")) and subprocess.run(
        ["docker", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    ).returncode == 0 and subprocess.run(
        ["docker", "image", "inspect", "python:3.12-slim"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode == 0


class ReplaySandboxTests(unittest.TestCase):
    def require_replay(self) -> ModuleType:
        if replay is None:
            self.fail("replay.py must implement isolated X7 command replay")
        return replay

    def test_each_event_gets_fresh_copy_on_write_snapshot(self):
        module = self.require_replay()
        if not docker_ready():
            self.skipTest("Docker daemon and python:3.12-slim image are required")

        with owned_scratch() as scratch:
            repo, commit = make_repo(scratch)
            pack = scratch / "commands.jsonl"
            receipt = scratch / "receipt.jsonl"
            write_pack(pack, ["rm tracked.txt", "test -f tracked.txt"])

            results = module.run_pack(
                repo=repo,
                commit=commit,
                pack_path=pack,
                scratch_root=scratch,
                receipt_path=receipt,
                timeout_seconds=10,
                base_image="python:3.12-slim",
            )

            self.assertEqual([row["status"] for row in results], ["EXECUTED", "EXECUTED"])
            self.assertEqual(results[0]["effects"]["deleted"], 1)
            self.assertEqual(results[1]["effects"]["deleted"], 0)
            self.assertEqual((repo / "tracked.txt").read_text(), "committed source\n")
            self.assertEqual(len(receipt.read_text().splitlines()), 2)

    def test_container_has_no_host_files_or_credentials_and_is_offline(self):
        module = self.require_replay()
        if not docker_ready():
            self.skipTest("Docker daemon and python:3.12-slim image are required")

        with owned_scratch() as scratch:
            repo, commit = make_repo(scratch)
            host_canary = scratch / "host-canary.txt"
            host_canary.write_text("host-only sentinel")
            pack = scratch / "commands.jsonl"
            receipt = scratch / "receipt.jsonl"
            probe = (
                "import os,socket; "
                f"assert not os.path.exists({str(host_canary)!r}); "
                "assert 'TYPESAFE_API_KEY' not in os.environ; "
                "assert os.environ.get('HOME') == '/tmp'; "
                "assert socket.if_nameindex() == [(1, 'lo')]"
            )
            command = "python3 -c " + shlex.quote(probe)
            write_pack(pack, [command])

            with patch.dict(os.environ, {"TYPESAFE_API_KEY": "synthetic-test-sentinel"}):
                results = module.run_pack(
                    repo=repo,
                    commit=commit,
                    pack_path=pack,
                    scratch_root=scratch,
                    receipt_path=receipt,
                    timeout_seconds=10,
                    base_image="python:3.12-slim",
                )

            self.assertEqual(results[0]["status"], "EXECUTED")
            self.assertNotIn("command", results[0])
            self.assertNotIn(command, receipt.read_text())
            self.assertEqual(host_canary.read_text(), "host-only sentinel")

    def test_pack_digest_mismatch_refuses_before_container_run(self):
        module = self.require_replay()
        with owned_scratch() as scratch:
            repo, commit = make_repo(scratch)
            pack = scratch / "commands.jsonl"
            receipt = scratch / "receipt.jsonl"
            write_pack(pack, ["touch should-not-exist"])
            row = json.loads(pack.read_text())
            row["cmd_sha256"] = "0" * 64
            pack.write_text(json.dumps(row) + "\n")
            pack.chmod(0o600)

            with self.assertRaisesRegex(ValueError, "digest"):
                module.run_pack(
                    repo=repo,
                    commit=commit,
                    pack_path=pack,
                    scratch_root=scratch,
                    receipt_path=receipt,
                    timeout_seconds=10,
                    base_image="python:3.12-slim",
                )
            self.assertFalse(receipt.exists())
            self.assertFalse((repo / "should-not-exist").exists())


if __name__ == "__main__":
    unittest.main()

