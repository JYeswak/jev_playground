"""Tests for jev-3xt4: read-only git sets GIT_OPTIONAL_LOCKS=0; writers never do.

Part 1 is static (the edited call sites). Part 2 is live: a planted slow
read-only `git status` creates no index.lock with the env, and does without
it (proving the plant can catch a lock).
"""

import os
import re
import subprocess
import tempfile
import threading
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
READONLY_FILES = [
    "scripts/bootstrap-compaction.sh",
    "scripts/lane-status.sh",
    "scripts/noclaim-harvest.sh",
    "scripts/omp-continue.sh",
    "scripts/pin-liveness.sh",
    "scripts/publish-export.sh",
    "scripts/selftest-lane-status-integrity.sh",
    "scripts/sync-docs.sh",
    "scripts/verify-frozen.sh",
]
WRITER_VERBS = (
    "add",
    "commit",
    "rm ",
    "rm\t",
    "checkout",
    "clone",
    "fetch",
    "init",
    "config",
)


def git_calls(path):
    """(line, command) for shell git invocations, skipping comments."""
    out = []
    for i, line in enumerate(Path(path).read_text().splitlines(), 1):
        code = line.split("#", 1)[0]
        for m in re.finditer(
            r"(?:^|[;&|(`$])\s*(GIT_OPTIONAL_LOCKS=\S+\s+)?(git)\s+(\S+)", code
        ):
            out.append((i, bool(m.group(1)), m.group(3)))
    return out


class TestOptionalLocks(unittest.TestCase):
    def test_readonly_calls_carry_the_env(self):
        missing = []
        for rel in READONLY_FILES:
            for i, has_env, sub in git_calls(ROOT / rel):
                if sub in (
                    "status",
                    "diff",
                    "log",
                    "show",
                    "rev-parse",
                    "ls-files",
                    "grep",
                    "archive",
                ):
                    if not has_env:
                        missing.append(f"{rel}:{i} git {sub}")
        self.assertEqual(missing, [], f"read-only calls without env: {missing}")

    def test_writers_never_carry_the_env(self):
        bad = []
        roots = [ROOT / "scripts", ROOT / "foundation" / "gates.d"]
        for top in roots:
            for path in top.rglob("*.sh"):
                for i, line in enumerate(path.read_text().splitlines(), 1):
                    code = line.split("#", 1)[0]
                    if "GIT_OPTIONAL_LOCKS" in code and re.search(
                        r"GIT_OPTIONAL_LOCKS=\S+\s+git\s+(add|commit|rm|checkout|clone|fetch|init|config)\b",
                        code,
                    ):
                        bad.append(f"{path.name}:{i}")
        self.assertEqual(bad, [], f"writers with env: {bad}")

    def test_scripts_still_parse(self):
        for rel in READONLY_FILES:
            p = subprocess.run(
                ["bash", "-n", str(ROOT / rel)], capture_output=True, text=True
            )
            self.assertEqual(p.returncode, 0, f"{rel}: {p.stderr}")


def slow_repo(n=6000):
    d = Path(tempfile.mkdtemp(prefix="3xt4-"))
    subprocess.run(["git", "init", "-q", "."], cwd=d, check=True)
    subprocess.run(["git", "config", "user.email", "t@t.t"], cwd=d, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=d, check=True)
    names = [f"f{i}.txt" for i in range(n)]
    for i, name in enumerate(names):
        (d / name).write_text(f"x{i}\n")
    for j in range(0, n, 500):
        subprocess.run(["git", "add", "--", *names[j : j + 500]], cwd=d, check=True)
    subprocess.run(["git", "commit", "-qm", "init [test]"], cwd=d, check=True)
    for i, name in enumerate(names):
        (d / name).write_text(f"y{i}\n")
    return d


def lock_seen_during(cwd, *cmd, env=None):
    seen = []
    stop = False

    def watch():
        lock = os.path.join(cwd, ".git", "index.lock")
        while not stop:
            if os.path.exists(lock):
                seen.append(True)
                return

    t = threading.Thread(target=watch, daemon=True)
    t.start()
    try:
        e = dict(os.environ)
        if env:
            e.update(env)
        subprocess.run(cmd, cwd=cwd, capture_output=True, env=e, timeout=120)
    finally:
        stop = True
        t.join(timeout=5)
    return bool(seen)


class TestLiveNoLock(unittest.TestCase):
    def test_slow_status_without_env_can_take_the_lock(self):
        d = slow_repo()
        self.assertTrue(
            lock_seen_during(str(d), "git", "status", "--porcelain"),
            "plant invalid: no lock observed even without the env",
        )

    def test_slow_status_with_env_never_takes_the_lock(self):
        for _ in range(3):
            d = slow_repo()
            self.assertFalse(
                lock_seen_during(
                    str(d),
                    "git",
                    "status",
                    "--porcelain",
                    env={"GIT_OPTIONAL_LOCKS": "0"},
                ),
                "read-only git took index.lock despite GIT_OPTIONAL_LOCKS=0",
            )


if __name__ == "__main__":
    unittest.main()
