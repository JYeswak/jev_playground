"""Tests for scripts/git-commit-serialized.sh (jev-fxm2). Hermetic tmp repos only."""

import os
import subprocess
import tempfile
import time
import unittest

WRAPPER = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "git-commit-serialized.sh"
)


def sh(cwd, *args, env=None):
    e = dict(os.environ)
    if env:
        e.update(env)
    return subprocess.run(
        args, cwd=cwd, capture_output=True, text=True, env=e, timeout=120
    )


def init_repo():
    d = tempfile.mkdtemp(prefix="fxm2-")
    sh(d, "git", "init", "-q", ".")
    sh(d, "git", "config", "user.email", "t@t.t")
    sh(d, "git", "config", "user.name", "t")
    with open(os.path.join(d, "f.txt"), "w") as fh:
        fh.write("x\n")
    sh(d, "git", "add", "f.txt")
    return d


class TestSerializedCommit(unittest.TestCase):
    def test_sweep_stale_then_commit(self):
        d = init_repo()
        with open(os.path.join(d, "g.txt"), "w") as fh:
            fh.write("y\n")
        sh(d, "git", "add", "g.txt")
        lock = os.path.join(d, ".git", "index.lock")
        with open(lock, "w"):
            pass
        old = time.time() - 400
        os.utime(lock, (old, old))
        p = sh(d, "bash", WRAPPER, "-qm", "sweep test [test]")
        self.assertEqual(p.returncode, 0, p.stderr)
        moved = [
            f
            for f in os.listdir(os.path.join(d, "var", "agent-tmp"))
            if f.startswith("git-index.lock.stale-")
        ]
        self.assertEqual(len(moved), 1)
        log = sh(d, "git", "log", "--format=%s", "-1")
        self.assertIn("sweep test", log.stdout)

    def test_live_lock_untouched(self):
        d = init_repo()
        with open(os.path.join(d, "g.txt"), "w") as fh:
            fh.write("y\n")
        sh(d, "git", "add", "g.txt")
        lock = os.path.join(d, ".git", "index.lock")
        with open(lock, "w") as fh:
            fh.write("live-bytes")
        old = time.time() - 400
        os.utime(lock, (old, old))
        p = sh(d, "bash", WRAPPER, "-qm", "must fail through [test]")
        self.assertNotEqual(p.returncode, 0)
        self.assertTrue(os.path.exists(lock))

    def test_mutex_timeout(self):
        d = init_repo()
        os.mkdir(os.path.join(d, ".git", "fleet-commit.lockdir"))
        with open(os.path.join(d, "g.txt"), "w") as fh:
            fh.write("y\n")
        sh(d, "git", "add", "g.txt")
        p = sh(
            d,
            "bash",
            WRAPPER,
            "-qm",
            "blocked [test]",
            env={"JEV_COMMIT_MUTEX_TIMEOUT": "3"},
        )
        self.assertEqual(p.returncode, 3)

    def test_mutex_serializes_commits(self):
        d = init_repo()
        hook = os.path.join(d, ".git", "hooks", "pre-commit")
        with open(hook, "w") as fh:
            fh.write("#!/bin/sh\nsleep 2\n")
        os.chmod(hook, 0o755)
        with open(os.path.join(d, "a.txt"), "w") as fh:
            fh.write("a\n")
        sh(d, "git", "add", "a.txt")
        import threading

        os.mkdir(os.path.join(d, ".git", "fleet-commit.lockdir"))
        results = []

        def one():
            results.append(
                sh(d, "bash", WRAPPER, "-qm", "held commit [test]").returncode
            )

        t = threading.Thread(target=one)
        t.start()
        time.sleep(3)
        log = sh(d, "git", "log", "--format=%s")
        self.assertNotIn("held commit", log.stdout)
        self.assertTrue(t.is_alive())
        os.rmdir(os.path.join(d, ".git", "fleet-commit.lockdir"))
        t.join(timeout=100)
        self.assertEqual(results, [0])
        log = sh(d, "git", "log", "--format=%s")
        self.assertIn("held commit", log.stdout)


if __name__ == "__main__":
    unittest.main()
