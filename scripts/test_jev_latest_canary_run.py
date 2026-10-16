"""Tests for scripts/jev-latest-canary-run.sh: secret-manager boundary, exit
mapping, AUTH override, real notifier delivery, log shape, and no repository
paths. Hermetic: the secret manager, the notifier, and the canary are injected
stubs (no live calls, no keys, no network, no real notifications); all state
lands in tmp dirs under TMPDIR. Follows jev-jh6f acceptance items 1-5."""

import os
import subprocess
import tempfile
import unittest
from unittest.mock import patch

RUNNER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jev-latest-canary-run.sh")

AUTH_TEXT = "Failed to automatically trigger login flow"

CANARY_STUB = """#!/usr/bin/env python3
import os, sys
print(os.environ.get("STUB_OUT", "ok"))
sys.exit(int(os.environ.get("STUB_RC", "0")))
"""

# Stub secret manager: SM_MODE=auth prints the Infisical login failure and
# exits 1 without running the canary; SM_MODE=silent-fail exits 1 with no
# output and no exec (an unknown-wording pre-child failure); SM_MODE=passthrough
# execs argv after the lone `--` (the canary), like `infisical run -- <canary>`.
SM_STUB = """#!/usr/bin/env bash
mode="${SM_MODE:-passthrough}"
if [ "$mode" = "auth" ]; then
  echo "%s. Please run login manually." >&2
  echo "%s"
  exit 1
fi
if [ "$mode" = "silent-fail" ]; then
  exit 1
fi
while [ "$#" -gt 0 ] && [ "$1" != "--" ]; do shift; done
[ "$1" = "--" ] && shift
exec "$@"
""" % (AUTH_TEXT, AUTH_TEXT)

# Stub notifier: records each invocation's argv joined by \x1f (so hostile
# payloads cannot blend across argument boundaries), exits $NOTIFY_RC.
NOTIFY_STUB = """#!/usr/bin/env bash
IFS=$'\\x1f'; echo "$*" >> "$NOTIFY_LOG"
exit "${NOTIFY_RC:-0}"
"""


def write_stub(directory, name, body):
    path = os.path.join(directory, name)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(body)
    os.chmod(path, 0o755)
    return path


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
        self.canary = write_stub(self.tmp, "stub-canary.py", CANARY_STUB)
        self.sm = write_stub(self.tmp, "stub-sm.sh", SM_STUB)
        self.notify_bin = write_stub(self.tmp, "stub-notify.sh", NOTIFY_STUB)
        self.log = os.path.join(self.tmp, "canary.log")
        self.notify_log = os.path.join(self.tmp, "notify.log")
        self.default_notify_log = os.path.join(self.tmp, "unexpected-notify.log")
        write_stub(
            self.tmp,
            "osascript",
            '#!/bin/sh\nprintf "unexpected default notifier\\n" >> "$CANARY_DEFAULT_NOTIFY_LOG"\nexit 97\n',
        )
        self.host_env = patch.dict(
            os.environ,
            {
                "PATH": self.tmp + os.pathsep + os.environ.get("PATH", os.defpath),
                "CANARY_DEFAULT_NOTIFY_LOG": self.default_notify_log,
            },
        )
        self.host_env.start()

    def tearDown(self):
        self.host_env.stop()
        self.assertFalse(
            os.path.exists(self.default_notify_log),
            "test escaped to the default notifier instead of the injected notifier",
        )
        import shutil

        shutil.rmtree(self.tmp, ignore_errors=True)

    def invoke(self, rc, out, sm_mode="passthrough", notify_rc="0"):
        return run_canary(
            {
                "STUB_RC": str(rc),
                "STUB_OUT": out,
                "SM_MODE": sm_mode,
                "NOTIFY_RC": notify_rc,
                "NOTIFY_LOG": self.notify_log,
                "TMPDIR": self.tmp,
            },
            "--secret-manager", self.sm,
            "--notify-bin", self.notify_bin,
            "--canary", self.canary,
            "--log-file", self.log,
        )

    def log_lines(self):
        with open(self.log, encoding="utf-8") as handle:
            return [line.rstrip("\n") for line in handle if line.strip()]

    def notify_calls(self):
        if not os.path.exists(self.notify_log):
            return []
        with open(self.notify_log, encoding="utf-8") as handle:
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

    def test_marker_creation_failure_notifies_and_logs_error(self):
        write_stub(self.tmp, "mktemp", "#!/bin/sh\nexit 1\n")
        self.log = os.path.join(self.tmp, "logs", "canary.log")
        proc = self.invoke(0, "OK: canary must not run")
        self.assertEqual(proc.returncode, 3)
        self.assertIn("NOTIFY ERROR:", proc.stdout)
        (notice,) = self.notify_calls()
        self.assertTrue(notice.split("\x1f")[-1].startswith("ERROR:"))
        (line,) = self.log_lines()
        self.assertEqual(line.split(" ", 2)[1], "rc=3")

    def test_notifier_called_once_per_outcome_with_silence_on_ok(self):
        proc = self.invoke(0, "OK: x")
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(self.notify_calls(), [])
        for rc, out, outcome in [
            (1, "MOVED: x", "MOVED"),
            (2, "NOT_RUN: x", "NOT_RUN"),
            (3, "ERROR: x", "ERROR"),
        ]:
            with self.subTest(outcome=outcome):
                proc = self.invoke(rc, out)
                self.assertEqual(proc.returncode, rc)
        calls = self.notify_calls()
        self.assertEqual(len(calls), 3)
        for outcome in ("MOVED", "NOT_RUN", "ERROR"):
            self.assertTrue(
                any(outcome in call for call in calls),
                f"no notifier call for {outcome}: {calls}",
            )

    def test_auth_manager_failure_reports_auth_with_own_code(self):
        proc = self.invoke(1, "canary must not run", sm_mode="auth")
        self.assertEqual(proc.returncode, 4)
        self.assertIn("NOTIFY AUTH:", proc.stdout)
        self.assertNotIn("MOVED", proc.stdout)
        calls = self.notify_calls()
        self.assertEqual(len(calls), 1)
        self.assertIn("AUTH", calls[0])
        (line,) = self.log_lines()
        self.assertIn("rc=4", line)

    def test_hostile_output_stays_argv_data(self):
        evil = 'MOVED: x" & quoted & "y\\z'
        proc = self.invoke(1, evil)
        self.assertEqual(proc.returncode, 1)
        (call,) = self.notify_calls()
        parts = call.split("\x1f")
        # Static AppleScript fragments, then the message verbatim as argv.
        self.assertEqual(len(parts), 7)
        self.assertEqual(parts[0], "-e")
        self.assertEqual(parts[-1], f"MOVED: {evil}")
        for code in parts[1:-1:2]:
            self.assertNotIn(evil, code)

    def test_prechild_silent_failure_reports_auth(self):
        # Unknown-wording pre-child exit 1: the canary never starts, so this
        # is failed acquisition (AUTH), never MOVED, whatever the message says.
        proc = self.invoke(1, "canary must not run", sm_mode="silent-fail")
        self.assertEqual(proc.returncode, 4)
        self.assertIn("NOTIFY AUTH:", proc.stdout)
        self.assertNotIn("MOVED", proc.stdout)
        (line,) = self.log_lines()
        self.assertIn("rc=4", line)

    def test_missing_tmpdir_refuses_without_tmp_files(self):
        env = {
            "STUB_RC": "0",
            "STUB_OUT": "ok",
            "SM_MODE": "passthrough",
            "NOTIFY_RC": "0",
            "NOTIFY_LOG": self.notify_log,
        }
        base = dict(os.environ)
        base.pop("TYPESAFE_API_KEY", None)
        base.pop("TMPDIR", None)
        base.update(env)
        proc = subprocess.run(
            ["bash", RUNNER,
             "--secret-manager", self.sm,
             "--notify-bin", self.notify_bin,
             "--canary", self.canary,
             "--log-file", self.log],
            capture_output=True, text=True, timeout=60, env=base,
        )
        self.assertEqual(proc.returncode, 3)
        self.assertIn("NOTIFY ERROR:", proc.stdout)
        self.assertIn("TMPDIR", proc.stdout)

    def test_auth_text_overrides_canary_exit_1(self):
        # The manager succeeds, then the child emits the AUTH diagnostic while
        # exiting 1. Keep this distinct from a pre-child acquisition failure.
        proc = self.invoke(1, AUTH_TEXT + ". Please run login manually.")
        self.assertEqual(proc.returncode, 4)
        self.assertIn("NOTIFY AUTH:", proc.stdout)
        self.assertNotIn("MOVED", proc.stdout)
        self.assertEqual(len(self.notify_calls()), 1)

    def test_failing_notifier_leaves_runner_outcome_unchanged(self):
        proc = self.invoke(1, "MOVED: x", notify_rc="1")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("NOTIFY MOVED:", proc.stdout)
        self.assertEqual(len(self.notify_calls()), 1)

    def test_unknown_exit_fails_closed(self):
        proc = self.invoke(9, "weird")
        self.assertEqual(proc.returncode, 3)
        self.assertIn("NOTIFY ERROR:", proc.stdout)

    def test_missing_secret_manager_fails_closed(self):
        proc = run_canary(
            {"NOTIFY_LOG": self.notify_log, "TMPDIR": self.tmp},
            "--secret-manager", os.path.join(self.tmp, "no-such-sm"),
            "--notify-bin", self.notify_bin,
            "--canary", self.canary,
            "--log-file", self.log,
        )
        self.assertEqual(proc.returncode, 3)
        self.assertIn("NOTIFY ERROR:", proc.stdout)
        (call,) = self.notify_calls()
        self.assertIn("ERROR", call)

    def test_help_has_no_repository_paths(self):
        proc = run_canary({}, "--help")
        self.assertEqual(proc.returncode, 0)
        body = proc.stdout
        self.assertIn("--secret-manager", body)
        self.assertIn("--notify-bin", body)
        for token in (os.getcwd(), os.path.expanduser("~"), ".local/state"):
            self.assertNotIn(token, body)

    def test_log_line_shape_matches_history(self):
        self.invoke(1, "MOVED: x")
        (line,) = self.log_lines()
        self.assertRegex(line, r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z rc=1 MOVED: x$")


if __name__ == "__main__":
    unittest.main()
