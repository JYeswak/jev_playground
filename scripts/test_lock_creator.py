"""Tests for capture_lock_creator in scripts/fleet-idle-watch.py (jev-5hw1).

Hermetic tmp repos only. Uses real git/lsof/ps processes, never the jev tree.
"""

import importlib.util
import json
import os
import stat
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "fleet_idle_watch", HERE / "fleet-idle-watch.py"
)
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)


def sh(cwd, *args, timeout=60):
    return subprocess.run(
        args, cwd=cwd, capture_output=True, text=True, timeout=timeout
    )


def init_repo():
    d = Path(tempfile.mkdtemp(prefix="5hw1-"))
    sh(d, "git", "init", "-q", ".")
    sh(d, "git", "config", "user.email", "t@t.t")
    sh(d, "git", "config", "user.name", "t")
    (d / "f.txt").write_text("x\n")
    sh(d, "git", "add", "f.txt")
    return d


def paths(d):
    base = Path(tempfile.mkdtemp(prefix="5hw1log-"))
    return base / "creators.jsonl", base / "watch.json"


class TestCaptureLockCreator(unittest.TestCase):
    def test_no_lock_returns_none_and_writes_nothing(self):
        d = init_repo()
        log, state = paths(d)
        self.assertIsNone(w.capture_lock_creator(d, time.time(), str(log), str(state)))
        self.assertFalse(log.exists())

    def test_abandoned_lock_captured_once_with_empty_holders(self):
        d = init_repo()
        log, state = paths(d)
        lock = d / ".git" / "index.lock"
        lock.write_text("")
        row = w.capture_lock_creator(d, time.time(), str(log), str(state))
        self.assertIsNotNone(row)
        self.assertEqual(row["holders"], [])
        self.assertTrue(lock.exists(), "capture must never move the lock")
        self.assertEqual(stat.S_IMODE(log.stat().st_mode), 0o600)
        again = w.capture_lock_creator(d, time.time(), str(log), str(state))
        self.assertIsNone(again, "same lock must not log twice")
        self.assertEqual(len(log.read_text().strip().splitlines()), 1)

    def test_live_git_holder_captured_and_lock_untouched(self):
        d = init_repo()
        log, state = paths(d)
        fifo = d / "stdin.fifo"
        os.mkfifo(fifo)
        fw = os.open(fifo, os.O_RDWR | os.O_NONBLOCK)
        try:
            with open(fifo) as stdin_fh:
                proc = subprocess.Popen(
                    ["git", "update-index", "--stdin"],
                    cwd=d,
                    stdin=stdin_fh,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                try:
                    lock = d / ".git" / "index.lock"
                    for _ in range(200):
                        if lock.exists():
                            break
                        time.sleep(0.05)
                    self.assertTrue(lock.exists(), "planted holder left no lock")
                    row = w.capture_lock_creator(d, time.time(), str(log), str(state))
                    self.assertIsNotNone(row)
                    self.assertTrue(row["holders"], "live holder missing from capture")
                    self.assertTrue(
                        any("git" in (h["argv"] or "") for h in row["holders"]),
                        row["holders"],
                    )
                    self.assertTrue(lock.exists(), "capture moved a held lock")
                finally:
                    proc.kill()
                    proc.wait()
        finally:
            os.close(fw)

    def test_vanished_lock_resets_state(self):
        d = init_repo()
        log, state = paths(d)
        lock = d / ".git" / "index.lock"
        lock.write_text("")
        self.assertIsNotNone(
            w.capture_lock_creator(d, time.time(), str(log), str(state))
        )
        lock.unlink()
        self.assertIsNone(w.capture_lock_creator(d, time.time(), str(log), str(state)))
        lock.write_text("")
        row = w.capture_lock_creator(d, time.time(), str(log), str(state))
        self.assertIsNotNone(row, "reappeared lock must capture again")
        self.assertEqual(len(log.read_text().strip().splitlines()), 2)

    def test_stale_rule_still_moves_only_holderless_old_locks(self):
        d = init_repo()
        (d / "g.txt").write_text("y\n")
        sh(d, "git", "add", "g.txt")
        lock = d / ".git" / "index.lock"
        lock.write_text("")
        old = time.time() - 400
        os.utime(lock, (old, old))
        sent = []
        note = w.stale_lock_round(d, time.time(), sent.append, park_dir=str(d / "park"))
        self.assertIsNotNone(note)
        self.assertFalse(lock.exists())
        self.assertEqual(len(list((d / "park").glob("git-index.lock.stale-*"))), 1)


if __name__ == "__main__":
    unittest.main()
