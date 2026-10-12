"""Tests for scripts/jev-latest-canary-run.sh: exit mapping, AUTH override,
notifications, log shape, and no repository paths. Hermetic: the canary is an
injected stub (no live calls, no keys, no network); all state lands in tmp dirs
under TMPDIR. Follows jev-jh6f acceptance items 1-5."""

import os
import subprocess
import tempfile
import unittest

RUNNER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jev-latest-canary-run.sh")

AUTH_TEXT = "Failed to automatically trigger login flow"

STUB = """#!/usr/bin/env python3
import os, sys
print(os.environ.get("STUB_OUT", "ok"))
sys.exit(int(os.environ.get("STUB_RC", "0")))
"""


def run_canary(env_extra, *argv):
    env = dict(os.environ)
    env.pop("TYPESAFE_API_KEY", None)
    env.update(env_extra)
    proc = subprocess.run(
        ["bash", RUNNER, *argv], capture_output=True, text=True, timeout=60, env=env
    )
    return proc


class CanaryRunnerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="canary-run-")
        self.stub = os.path.join(self.tmp, "stub-canary.py")
        with open(self.stub, "w", encoding="utf-8") as handle:
            handle.write(STUB)
        os.chmod(self.stub, 0o755)
        self.log = os.path.join(self.tmp, "canary.log")

    def tearDown(self):
        import shutil

        shutil.rmtree(self.tmp, ignore_errors=True)

    def invoke(self, rc, out):
        return run_canary(
            {"STUB_RC": str(rc), "STUB_OUT": out},
            "--canary", self.stub, "--log-file", self.log,
        )

    def log_lines(self):
        with open(self.log, encoding="utf-8") as handle:
            return [line.rstrip("\n") for line in handle if line.strip()]

    def test_ok_records_no_notification(self):
        proc = self.invoke(0, "OK: jev-latest resolves to jev-1.13.0")
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout.strip(), "")
        (line,) = self.log_lines()
        self.assertRegex(line, r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z rc=0 OK: ")

    def test_moved_notifies(self):
        proc = self.invoke(1, "MOVED: jev-latest resolves to jev-9.9.9")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("NOTIFY MOVED:", proc.stdout)
        (line,) = self.log_lines()
        self.assertIn("rc=1", line)

    def test_not_run_notifies(self):
        proc = self.invoke(2, "NOT_RUN: no key")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("NOTIFY NOT_RUN:", proc.stdout)

    def test_error_notifies(self):
        proc = self.invoke(3, "ERROR: bad response")
        self.assertEqual(proc.returncode, 3)
        self.assertIn("NOTIFY ERROR:", proc.stdout)

    def test_auth_text_overrides_exit_1_with_own_code(self):
        proc = self.invoke(1, AUTH_TEXT + ". Please run login manually.")
        self.assertEqual(proc.returncode, 4)
        self.assertIn("NOTIFY AUTH:", proc.stdout)
        self.assertNotIn("MOVED", proc.stdout)

    def test_unknown_exit_fails_closed(self):
        proc = self.invoke(9, "weird")
        self.assertEqual(proc.returncode, 3)
        self.assertIn("NOTIFY ERROR:", proc.stdout)

    def test_help_has_no_repository_paths(self):
        proc = run_canary({}, "--help")
        self.assertEqual(proc.returncode, 0)
        for token in ("/Users/", "$PWD", os.getcwd()):
            self.assertNotIn(token, proc.stdout)
        with open(RUNNER, encoding="utf-8") as handle:
            body = handle.read()
        for token in ("/Users/", "$PWD"):
            self.assertNotIn(token, body)

    def test_log_line_shape_matches_history(self):
        self.invoke(1, "MOVED: x")
        (line,) = self.log_lines()
        self.assertRegex(line, r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z rc=1 MOVED: x$")


if __name__ == "__main__":
    unittest.main()
