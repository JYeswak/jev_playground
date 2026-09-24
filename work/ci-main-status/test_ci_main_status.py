"""scripts/ci-main-status.py against saved gh output, no network (bead jev-bfku).

Fixtures are trimmed real gh responses from JYeswak/jev_playground, 2026-09-24:
  list-red.json            `gh run list` slice whose newest completed run is 36059723283 (ff8316d,
                           failure), the last red push before the 8373173 fix
  log-36059723283.txt      `gh run view 36059723283 --log-failed` excerpt: the runner's script
                           source (its `echo "RED named $row"` line is a trap), TSV rows, the FAIL row
  view-*.json              `gh run view <id> --json jobs`, steps dropped
  log-36059356737.txt      a run where both jobs failed: gates `RED  15-kit-claim` plus its FAIL
                           sub-checks, and a `RED-ROW SELFTEST PASS` line that is not a RED row
  log-36002632785-dispatch.txt  a plant dispatch whose runner printed `RED named <row>`
  list-green.json          newest completed 36063055143 (914298b, success), nothing newer
  list-newer-in-progress.json   the same green with three newer in_progress pushes above it
"""

import importlib.util
import json
import stat
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIX = HERE / "fixtures"
SCRIPT = HERE.parents[1] / "scripts" / "ci-main-status.py"

spec = importlib.util.spec_from_file_location("ci_main_status", SCRIPT)
cms = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cms)

GREEN_DONE = cms.epoch("2026-09-24T21:44:16Z")  # 36063055143 updatedAt
RED_DONE = cms.epoch("2026-09-24T21:13:29Z")  # 36059723283 updatedAt
FAIL_ROW = "work/sr-adopt/test_runner_gates.py\t1\t3\t71.31\t\tFAIL"


def fake_gh(listing, views=None, logs=None, broken=()):
    """A gh transport over fixture files; `broken` names calls ('list', 'jobs', 'log') that fail."""
    calls = []

    def gh(args):
        calls.append(args)
        kind = (
            "list" if args[1] == "list" else "log" if "--log-failed" in args else "jobs"
        )
        if kind in broken:
            raise cms.GhError(f"gh exit 1: planted {kind} failure")
        if kind == "list":
            return (FIX / listing).read_text()
        table = views if kind == "jobs" else logs
        return (FIX / table[args[2]]).read_text(encoding="utf-8")

    gh.calls = calls
    return gh


RED_VIEWS = {"36059723283": "view-36059723283.json"}
RED_LOGS = {"36059723283": "log-36059723283.txt"}


class Status(unittest.TestCase):
    def test_green_is_one_quiet_line_exit_0(self):
        gh = fake_gh("list-green.json")
        lines, rc = cms.status(gh, GREEN_DONE + 25 * 60)
        self.assertEqual(lines, ["CI main 914298b success 36063055143 25m ago"])
        self.assertEqual(rc, 0)
        self.assertEqual(len(gh.calls), 1, "a green run must not fetch jobs or logs")

    def test_red_names_the_failed_job_and_its_row_exit_1(self):
        gh = fake_gh("list-red.json", RED_VIEWS, RED_LOGS)
        lines, rc = cms.status(gh, RED_DONE + 6 * 3600 + 5 * 60)
        self.assertEqual(rc, 1)
        self.assertEqual(
            lines,
            [
                "CI main ff8316d failure 36059723283 6h05m ago",
                "  FAILED JOB registered-suites",
                f"    {FAIL_ROW}",
            ],
        )

    def test_red_stays_red_when_the_log_cannot_be_read(self):
        gh = fake_gh("list-red.json", RED_VIEWS, RED_LOGS, broken=("log",))
        lines, rc = cms.status(gh, RED_DONE)
        self.assertEqual(rc, 1)
        self.assertEqual(
            lines[:2],
            [
                "CI main ff8316d failure 36059723283 0m ago",
                "  FAILED JOB registered-suites",
            ],
        )
        self.assertIn("log unavailable: gh exit 1: planted log failure", lines[2])

    def test_newer_unfinished_push_labels_the_green_stale(self):
        lines, rc = cms.status(fake_gh("list-newer-in-progress.json"), GREEN_DONE + 60)
        self.assertEqual(rc, 0)
        self.assertEqual(lines[0], "CI main 914298b success 36063055143 1m ago")
        self.assertEqual(
            lines[1],
            "STALE 3 newer run(s) not finished, newest 36063215977 in_progress on 29ae9b3; "
            "the success above is for 914298b",
        )

    def test_gh_failure_is_not_run_exit_2(self):
        lines, rc = cms.status(fake_gh("list-green.json", broken=("list",)), GREEN_DONE)
        self.assertEqual(
            (lines, rc), (["CI main NOT_RUN gh exit 1: planted list failure"], 2)
        )

    def test_no_completed_run_is_not_run(self):
        runs = json.loads((FIX / "list-newer-in-progress.json").read_text())[:3]
        lines, rc = cms.status(lambda args: json.dumps(runs), GREEN_DONE)
        self.assertEqual(rc, 2)
        self.assertEqual(
            lines,
            [
                "CI main NOT_RUN no completed gates.yml push run on main among the newest 3"
            ],
        )

    def test_cancelled_is_neither_green_nor_red(self):
        runs = json.loads((FIX / "list-green.json").read_text())
        runs[0]["conclusion"] = "cancelled"
        lines, rc = cms.status(lambda args: json.dumps(runs), GREEN_DONE)
        self.assertEqual(rc, 2)
        self.assertEqual(
            lines, ["CI main 914298b NOT_RUN conclusion=cancelled 36063055143 0m ago"]
        )


class LogRows(unittest.TestCase):
    def test_gates_red_row_and_its_fail_checks_both_jobs(self):
        rows = cms.failing_rows(
            (FIX / "log-36059356737.txt").read_text(encoding="utf-8")
        )
        self.assertEqual(
            rows["registered-suites"],
            ["work/sr-adopt/test_runner_gates.py\t1\t3\t124.77\t\tFAIL"],
        )
        self.assertEqual(rows["gates"][0], "RED  15-kit-claim (exit=1, 0s)")
        self.assertEqual(len(rows["gates"]), 3)
        self.assertTrue(rows["gates"][1].startswith("  FAIL  inj-var-haiku-blocked: "))
        self.assertTrue(rows["gates"][2].startswith("  FAIL  limits-haiku-two-runs: "))

    def test_script_source_echo_is_not_a_row(self):
        rows = cms.failing_rows(
            (FIX / "log-36059723283.txt").read_text(encoding="utf-8")
        )
        self.assertEqual(rows, {"registered-suites": [FAIL_ROW]})

    def test_red_named_line_from_a_plant_dispatch(self):
        rows = cms.failing_rows(
            (FIX / "log-36002632785-dispatch.txt").read_text(encoding="utf-8")
        )
        self.assertEqual(
            rows["registered-suites"],
            [
                "scripts/selftest-ttsr-rules.sh\t1\t\t34.59\t\tFAIL",
                "RED named scripts/selftest-ttsr-rules.sh",
            ],
        )


class Cli(unittest.TestCase):
    """The real gh wrapper and exit code, with PATH pointing at no gh or a local stand-in."""

    def run_cli(self, gh_body=None, timeout="20"):
        with tempfile.TemporaryDirectory() as bin_dir:
            if gh_body is not None:
                fake = Path(bin_dir) / "gh"
                fake.write_text("#!/bin/sh\n" + gh_body)
                fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
            env = {"PATH": bin_dir, "HOME": bin_dir, "CI_MAIN_STATUS_TIMEOUT": timeout}
            started = time.monotonic()
            done = subprocess.run(
                [sys.executable, str(SCRIPT)],
                capture_output=True,
                text=True,
                env=env,
                timeout=60,
            )
            return done, time.monotonic() - started

    def test_gh_missing_is_not_run(self):
        done, _ = self.run_cli()
        self.assertEqual(
            (done.stdout, done.returncode), ("CI main NOT_RUN gh not installed\n", 2)
        )

    def test_gh_unauthenticated_is_not_run(self):
        # stderr and exit code of gh 2.94.0 with an empty GH_CONFIG_DIR and no GH_TOKEN, 2026-09-24.
        done, _ = self.run_cli(
            "echo 'gh: To use GitHub CLI in automation, set the GH_TOKEN environment variable.' >&2\nexit 4\n"
        )
        self.assertEqual(done.returncode, 2)
        self.assertEqual(
            done.stdout,
            "CI main NOT_RUN gh exit 4: gh: To use GitHub CLI in automation, set the GH_TOKEN environment variable.\n",
        )

    def test_gh_hang_hits_the_timeout(self):
        done, seconds = self.run_cli("exec /bin/sleep 30\n", timeout="1")
        self.assertEqual(
            (done.stdout, done.returncode),
            ("CI main NOT_RUN gh run list timed out after 1s\n", 2),
        )
        self.assertLess(seconds, 10)


if __name__ == "__main__":
    unittest.main()
