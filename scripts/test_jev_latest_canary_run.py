"""Offline tests for the installed jev-latest canary runner."""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "jev-latest-canary-run.sh"


class CanaryRunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR"))
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        self.home = self.work / "home"
        self.home.mkdir()
        self.notify_log = self.work / "notifications.log"
        self.python_args_log = self.work / "python-args.log"
        self.infisical = self.work / "infisical"
        self.infisical.write_text(
            "#!/bin/sh\n"
            'if [ "${CANARY_SECRET_MODE:-run}" = auth ]; then\n'
            "  echo 'Failed to automatically trigger login flow'\n"
            "  exit 1\n"
            "fi\n"
            '[ "$1" = run ] || exit 91\n'
            "shift\n"
            'while [ "$1" != -- ]; do shift; done\n'
            "shift\n"
            'exec "$@"\n'
        )
        self.infisical.chmod(0o755)
        self.python = self.work / "python-stub"
        self.python.write_text(
            "#!/bin/sh\n"
            'printf \'%s\\n\' "$@" > "$CANARY_PYTHON_ARGS_LOG"\n'
            "printf '%s\\n' \"${CANARY_SCRIPT_OUTPUT:-stub output}\"\n"
            'exit "${CANARY_SCRIPT_RC:-0}"\n'
        )
        self.python.chmod(0o755)
        self.notify = self.work / "notify"
        self.notify.write_text(
            "#!/bin/sh\n" 'printf \'%s\\n\' "$*" >> "$JEV_CANARY_NOTIFY_LOG"\n'
        )
        self.notify.chmod(0o755)

    def run_runner(
        self, *args: str, **extra_env: str
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env.update(
            {
                "HOME": str(self.home),
                "JEV_CANARY_INFISICAL_BIN": str(self.infisical),
                "JEV_CANARY_PYTHON_BIN": str(self.python),
                "JEV_CANARY_NOTIFY_BIN": str(self.notify),
                "JEV_CANARY_NOTIFY_LOG": str(self.notify_log),
                "CANARY_PYTHON_ARGS_LOG": str(self.python_args_log),
            }
        )
        env.update(extra_env)
        return subprocess.run(
            ["bash", str(RUNNER), *args],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
            timeout=30,
        )

    def notifications(self) -> list[str]:
        if not self.notify_log.exists():
            return []
        return self.notify_log.read_text().splitlines()

    def log_line(self) -> str:
        log = self.home / ".local/state/jev/jev-latest-canary.log"
        return log.read_text().splitlines()[-1]

    def test_infisical_login_failure_is_auth_not_moved(self):
        result = self.run_runner(CANARY_SECRET_MODE="auth")
        self.assertEqual(result.returncode, 4)
        self.assertEqual(len(self.notifications()), 1)
        self.assertIn("AUTH", self.notifications()[0])
        self.assertNotIn("moved off", self.notifications()[0])
        self.assertIn("Failed to automatically trigger login flow", self.log_line())
        self.assertRegex(self.log_line(), r"^\S+ rc=4 ")

    def test_each_nonzero_script_outcome_has_its_own_notification(self):
        expected = {
            1: ("MOVED", "moved off"),
            2: ("NOT_RUN", "NOT_RUN"),
            3: ("ERROR", "ERROR"),
        }
        for exit_code, (outcome, notice) in expected.items():
            with self.subTest(exit_code=exit_code):
                self.notify_log.unlink(missing_ok=True)
                result = self.run_runner(
                    CANARY_SCRIPT_RC=str(exit_code),
                    CANARY_SCRIPT_OUTPUT=f"{outcome}: captured result",
                )
                self.assertEqual(result.returncode, exit_code)
                self.assertEqual(len(self.notifications()), 1)
                self.assertIn(notice, self.notifications()[0])
                self.assertRegex(self.log_line(), rf"^\S+ rc={exit_code} ")
                self.assertTrue(self.log_line().endswith(f"{outcome}: captured result"))

    def test_success_is_logged_without_notification(self):
        result = self.run_runner(
            CANARY_SCRIPT_RC="0", CANARY_SCRIPT_OUTPUT="OK: pinned version"
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(self.notifications(), [])
        self.assertRegex(self.log_line(), r"^\S+ rc=0 OK: pinned version$")
        self.assertEqual(
            self.python_args_log.read_text().splitlines(),
            [str(ROOT / "scripts" / "jev-latest-canary.py")],
        )

    def test_help_is_offline_and_runner_has_no_checkout_path(self):
        result = self.run_runner("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("usage:", result.stdout.lower())
        self.assertNotIn(str(ROOT), RUNNER.read_text())
        self.assertFalse(self.notify_log.exists())


if __name__ == "__main__":
    unittest.main()
