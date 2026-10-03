"""Tests for the daemon-backed serialized Git writer. Hermetic repos only."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXECUTABLES = {
    name: executable
    for name, executable in (
        ("git", shutil.which("git")),
        ("bash", shutil.which("bash")),
    )
    if executable is not None
}
EXECUTABLES["python3"] = sys.executable
EXECUTABLES["git-dispatch"] = str(ROOT / "scripts" / "git")
DAEMON = ROOT / "scripts" / "git-commitd.py"
SCRATCH = ROOT / "var" / "agent-tmp"


def sh(
    cwd: Path,
    command: str,
    *args: str,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    if command not in EXECUTABLES:
        raise ValueError(f"unsupported test command: {command!r}")
    child_env = dict(os.environ)
    child_env["JEV_COMMITD_AUTOSTART"] = "1"
    if env:
        child_env.update(env)
    if command == "git-dispatch":
        child_env["JEV_COMMITD_TARGET_ROOT"] = str(cwd.resolve())
    return subprocess.run(
        (EXECUTABLES[command], *args),
        cwd=cwd,
        capture_output=True,
        text=True,
        env=child_env,
        timeout=120,
        check=False,
    )


def init_repo():
    SCRATCH.mkdir(parents=True, exist_ok=True)
    scratch = Path(tempfile.mkdtemp(prefix=f"git-writer.{os.getpid()}.", dir=SCRATCH))
    (scratch / ".owner").write_text(
        f"pid={os.getpid()}\n"
        "label=git-commit-serialized-tests\n"
        f"repo={ROOT}\n"
        f"created={datetime.now(timezone.utc).isoformat()}\n",
        encoding="utf-8",
    )
    repo = scratch / "repo"
    repo.mkdir()
    sh(repo, "git", "init", "-q", ".")
    sh(repo, "git", "config", "user.email", "writer-test@example.invalid")
    sh(repo, "git", "config", "user.name", "writer test")
    (repo / "base.txt").write_text("base\n", encoding="utf-8")
    sh(repo, "git", "add", "--", "base.txt")
    base = sh(repo, "git", "commit", "-qm", "baseline [selftest]")
    if base.returncode:
        raise AssertionError(base.stderr)
    return repo, sh(repo, "git", "rev-parse", "HEAD").stdout.strip()


def commit(repo, message, *paths, env=None):
    return sh(
        repo,
        "git-dispatch",
        "commit",
        "--only",
        "-m",
        message,
        "--",
        *paths,
        env=env,
    )


def install_pre_commit_hook(repo, log_path):
    hook_dir = repo / ".git" / "test-hooks"
    hook_dir.mkdir()
    hook = hook_dir / "pre-commit"
    hook.write_text(
        "#!/bin/sh\nprintf 'ran\\n' >> \"$JEV_TEST_HOOK_LOG\"\n",
        encoding="utf-8",
    )
    hook.chmod(0o755)
    sh(repo, "git", "config", "core.hooksPath", str(hook_dir))
    return {"JEV_TEST_HOOK_LOG": str(log_path)}


class TestSerializedCommit(unittest.TestCase):
    def setUp(self):
        self.repo, self.base = init_repo()
        self.addCleanup(
            sh,
            self.repo,
            "python3",
            str(DAEMON),
            "stop",
            "--repo",
            str(self.repo),
        )

    def test_concurrent_commits_are_path_isolated_and_run_repo_hook(self):
        hook_log = self.repo / ".git" / "hook.log"
        env = install_pre_commit_hook(self.repo, hook_log)
        for name in ("a.txt", "b with spaces.txt"):
            (self.repo / name).write_text(f"content: {name}\n", encoding="utf-8")

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(
                pool.map(
                    lambda item: commit(
                        self.repo, f"serialized {item} [selftest]", item, env=env
                    ),
                    ("a.txt", "b with spaces.txt"),
                )
            )

        self.assertEqual([result.returncode for result in results], [0, 0], results)
        commits = sh(
            self.repo, "git", "rev-list", "--reverse", f"{self.base}..HEAD"
        ).stdout.splitlines()
        self.assertEqual(len(commits), 2)
        committed_paths = []
        for sha in commits:
            paths = sh(
                self.repo,
                "git",
                "diff-tree",
                "--no-commit-id",
                "--name-only",
                "-r",
                sha,
            ).stdout.splitlines()
            self.assertEqual(len(paths), 1)
            committed_paths.extend(paths)
        self.assertCountEqual(committed_paths, ["a.txt", "b with spaces.txt"])
        self.assertEqual(
            hook_log.read_text(encoding="utf-8").splitlines(), ["ran", "ran"]
        )
        receipt_path = self.repo / ".git" / "jev-commitd-receipts.jsonl"
        try:
            receipts = [
                json.loads(line) for line in receipt_path.read_text().splitlines()
            ]
        except json.JSONDecodeError as exc:
            self.fail(f"daemon wrote malformed receipt: {exc}")
        self.assertEqual(len(receipts), 2)
        self.assertEqual(
            {tuple(row["paths"]) for row in receipts},
            {("a.txt",), ("b with spaces.txt",)},
        )
        self.assertEqual(sh(self.repo, "git", "status", "--porcelain").stdout, "")

    def test_daemon_commits_in_a_deep_clean_clone(self):
        scratch = Path(tempfile.mkdtemp(prefix=f"d{os.getpid()}.", dir=SCRATCH))
        (scratch / ".owner").write_text(
            f"pid={os.getpid()}\n"
            "label=git-commit-deep-socket-test\n"
            f"repo={ROOT}\n"
            f"created={datetime.now(timezone.utc).isoformat()}\n",
            encoding="utf-8",
        )
        socket_limit = 107 if sys.platform.startswith("linux") else 103
        suffix = "/repo/.git/j.sock"
        padding = (
            socket_limit - len(os.fsencode(str(scratch))) - 1 - len(os.fsencode(suffix))
        )
        self.assertGreaterEqual(padding, 0)

        seed = scratch / "seed"
        seed.mkdir()
        sh(seed, "git", "init", "-q", ".")
        sh(seed, "git", "config", "user.email", "writer-test@example.invalid")
        sh(seed, "git", "config", "user.name", "writer test")
        (seed / "base.txt").write_text("base\n", encoding="utf-8")
        sh(seed, "git", "add", "--", "base.txt")
        seed_commit = sh(seed, "git", "commit", "-qm", "baseline [test]")
        self.assertEqual(seed_commit.returncode, 0, seed_commit.stderr)

        repo = scratch / ("x" * padding) / "repo"
        repo.parent.mkdir(parents=True)
        cloned = sh(
            repo.parent, "git", "clone", "-q", "--no-hardlinks", str(seed), str(repo)
        )
        self.assertEqual(cloned.returncode, 0, cloned.stderr)
        for key, value in (
            ("user.email", "writer-test@example.invalid"),
            ("user.name", "writer test"),
        ):
            configured = sh(repo, "git", "config", key, value)
            self.assertEqual(configured.returncode, 0, configured.stderr)

        compact_socket = repo / ".git" / "j.sock"
        legacy_socket = repo / ".git" / "jev-commitd.sock"
        self.assertEqual(len(os.fsencode(compact_socket)), socket_limit)
        self.assertGreater(len(os.fsencode(legacy_socket)), socket_limit)
        self.addCleanup(sh, repo, "python3", str(DAEMON), "stop", "--repo", str(repo))

        (repo / "a.txt").write_text("a\n", encoding="utf-8")
        added = sh(repo, "git-dispatch", "add", "--", "a.txt")
        self.assertEqual(added.returncode, 0, added.stderr)
        committed = commit(repo, "deep path [test]", "a.txt")
        self.assertEqual(committed.returncode, 0, committed.stderr)
        self.assertEqual(
            sh(
                repo,
                "git",
                "diff-tree",
                "--no-commit-id",
                "--name-only",
                "-r",
                "HEAD",
            ).stdout.splitlines(),
            ["a.txt"],
        )
        self.assertEqual(sh(repo, "git", "status", "--porcelain").stdout, "")

    def test_add_request_stages_only_requested_path(self):
        (self.repo / "a.txt").write_text("a\n", encoding="utf-8")
        (self.repo / "b.txt").write_text("b\n", encoding="utf-8")
        result = sh(self.repo, "git-dispatch", "add", "--", "a.txt")
        self.assertEqual(result.returncode, 0, result.stderr)
        staged = sh(
            self.repo, "git", "diff", "--cached", "--name-only"
        ).stdout.splitlines()
        self.assertEqual(staged, ["a.txt"])

    def test_concurrent_adds_are_serialized_without_dropping_paths(self):
        for name in ("a.txt", "b.txt"):
            (self.repo / name).write_text(f"{name}\n", encoding="utf-8")

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(
                pool.map(
                    lambda name: sh(self.repo, "git-dispatch", "add", "--", name),
                    ("a.txt", "b.txt"),
                )
            )

        self.assertEqual([result.returncode for result in results], [0, 0], results)
        staged = sh(
            self.repo, "git", "diff", "--cached", "--name-only"
        ).stdout.splitlines()
        self.assertEqual(staged, ["a.txt", "b.txt"])

    def test_global_options_before_commit_fail_closed(self):
        (self.repo / "new.txt").write_text("new\n", encoding="utf-8")
        result = sh(
            self.repo,
            "git-dispatch",
            "-C",
            str(self.repo),
            "commit",
            "--only",
            "-m",
            "should refuse [selftest]",
            "--",
            "new.txt",
        )
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("without global options", result.stderr)
        self.assertEqual(
            sh(self.repo, "git", "rev-parse", "HEAD").stdout.strip(), self.base
        )

    def test_commit_does_not_capture_an_unrequested_staged_path(self):
        (self.repo / "a.txt").write_text("a\n", encoding="utf-8")
        (self.repo / "b.txt").write_text("b\n", encoding="utf-8")
        sh(self.repo, "git", "add", "--", "b.txt")

        result = commit(self.repo, "only a [selftest]", "a.txt")

        self.assertEqual(result.returncode, 0, result.stderr)
        sha = sh(self.repo, "git", "rev-parse", "HEAD").stdout.strip()
        committed_paths = sh(
            self.repo,
            "git",
            "diff-tree",
            "--no-commit-id",
            "--name-only",
            "-r",
            sha,
        ).stdout.splitlines()
        self.assertEqual(committed_paths, ["a.txt"])
        staged_paths = sh(
            self.repo, "git", "diff", "--cached", "--name-only"
        ).stdout.splitlines()
        self.assertEqual(staged_paths, ["b.txt"])

    def test_daemon_unavailable_refuses_without_git_fallback(self):
        (self.repo / "new.txt").write_text("new\n", encoding="utf-8")
        result = commit(
            self.repo,
            "must refuse [selftest]",
            "new.txt",
            env={"JEV_COMMITD_AUTOSTART": "0"},
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("commit daemon unavailable", result.stderr.lower())
        self.assertEqual(
            sh(self.repo, "git", "rev-parse", "HEAD").stdout.strip(), self.base
        )
        self.assertFalse((self.repo / ".git" / "jev-commitd-receipts.jsonl").exists())

    def test_request_rejects_path_escape(self):
        result = commit(self.repo, "unsafe path [selftest]", "../outside.txt")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(
            sh(self.repo, "git", "rev-parse", "HEAD").stdout.strip(), self.base
        )


if __name__ == "__main__":
    unittest.main()
