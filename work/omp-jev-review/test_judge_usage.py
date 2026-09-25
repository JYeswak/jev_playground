"""The judge-role section of surface-census.py and its fleet line (bead jev-xpk1). No model calls.

Row shapes are copied from real omp 18.3.0 session files:
  SUCCESS_*     ~/.omp/profiles/claude/agent/sessions/-Developer-jev/... (2026-09-24, stop)
  FAILED_FIND   the planted failure, TYPESAFE_BASE_URL=http://127.0.0.1:9, 2026-09-25T00:27Z:
                31 rows (30 find, 1 auto-thinking), each stopReason error, zero usage
  OTHER_ERROR   a judge-role row from another provider (ollama 404, 2026-09-24; timestamp moved
                into the window), which is not Jev's
"""

import contextlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
CENSUS = HERE / "surface-census.py"
WATCH = HERE.parents[1] / "scripts" / "fleet-idle-watch.py"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


sc = load("surface_census", CENSUS)
fiw = load("fleet_idle_watch", WATCH)

ZERO = {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0, "totalTokens": 0}


def usage(tokens, cost):
    return {
        "input": tokens,
        "output": 0,
        "cacheRead": 0,
        "cacheWrite": 0,
        "totalTokens": tokens,
        "cost": {
            "input": cost,
            "output": 0,
            "cacheRead": 0,
            "cacheWrite": 0,
            "total": cost,
        },
    }


def jev_row(timestamp, purpose, stop="stop", tokens=0, cost=0.0, error=None):
    row = {
        "type": "model_usage",
        "id": "c3156992",
        "parentId": "a3ac44ac",
        "timestamp": timestamp,
        "purpose": purpose,
        "role": "typesafe",
        "api": "typesafe",
        "provider": "typesafe",
        "model": "jev-latest",
        "usage": usage(tokens, cost),
        "stopReason": stop,
    }
    if error is not None:
        row["errorMessage"] = error
    return row


UNABLE = "Unable to connect. Is the computer able to access the url?"
SUCCESS_AUTO = jev_row(
    "2026-09-24T23:52:57.244Z", "auto-thinking", tokens=1058, cost=4.4436e-05
)
SUCCESS_FIND = jev_row(
    "2026-09-24T23:58:10.001Z", "find", tokens=3208, cost=0.000134736
)
FAILED_FIND = jev_row("2026-09-25T00:27:45.238Z", "find", stop="error", error=UNABLE)
FAILED_AUTO = jev_row(
    "2026-09-25T00:27:38.406Z", "auto-thinking", stop="error", error=UNABLE
)
ABORTED = jev_row(
    "2026-09-25T00:10:00.000Z", "judge", stop="aborted", error="Request was aborted"
)
OLD_FAILURE = jev_row(
    "2026-09-23T12:00:00.000Z", "find", stop="error", error="402 Payment Required"
)
OTHER_ERROR = {
    "type": "model_usage",
    "id": "091ec6ee",
    "parentId": "459f96ce",
    "timestamp": "2026-09-24T23:39:23.999Z",
    "purpose": "auto-thinking",
    "role": "judge",
    "api": "openai-responses",
    "provider": "ollama",
    "model": "qwen3.8-uncensored:latest",
    "usage": dict(
        ZERO,
        cost={"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0, "total": 0},
    ),
    "stopReason": "error",
    "errorMessage": "404 model 'qwen3.8-uncensored:latest' not found",
}
NOW = datetime(2026, 9, 25, 0, 30, tzinfo=timezone.utc)


def write_session(home, profile, encoded, cwd, rows):
    folder = home / ".omp" / "profiles" / profile / "agent" / "sessions" / encoded
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{len(list(folder.iterdir()))}.jsonl"
    head = [
        {"type": "title", "title": "t"},
        {
            "type": "session",
            "version": 3,
            "id": "s",
            "timestamp": "2026-09-24T23:00:00Z",
            "cwd": cwd,
        },
    ]
    path.write_text(
        "".join(json.dumps(r, separators=(",", ":")) + "\n" for r in head + rows)
    )
    return path


class Census(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="judge-usage-")
        self.home = Path(self.tmp.name) / "home"

    def tearDown(self):
        self.tmp.cleanup()

    def real(self, rows):
        return write_session(
            self.home, "claude", "-Developer-jev", "/Users/josh/Developer/jev", rows
        )

    def probe(self, rows):
        return write_session(
            self.home,
            "claude",
            "--private-tmp-jev-xpk1-plant--",
            "/tmp/jev-xpk1-plant",
            rows,
        )

    def rows(self):
        return list(sc.judge_rows(sorted(self.home.rglob("*.jsonl"))))

    def test_success_rows_are_calls_and_cost(self):
        self.real([SUCCESS_AUTO, SUCCESS_FIND])
        self.assertEqual(
            sc.fleet_line(self.rows(), NOW, True),
            "Jev judge 24h: 2 calls, $0.0002, 0 failures",
        )
        report = sc.judge_report(self.rows())
        self.assertIn(
            "real\t2026-09-24\tfind\tclaude\tjev\t1\t3208\t0.000135\tstop=1", report
        )
        self.assertIn("# judge real calls 2 cost $0.000179 failures 0", report)

    def test_failure_rows_are_counted_and_the_last_reason_named(self):
        self.real([SUCCESS_FIND, ABORTED, FAILED_FIND])
        self.assertEqual(
            sc.fleet_line(self.rows(), NOW, True),
            f"Jev judge 24h: 3 calls, $0.0001, 2 failures; last 2026-09-25T00:27Z find claude: {UNABLE}",
        )
        report = sc.judge_report(self.rows())
        self.assertIn(
            "real\t2026-09-25\tfind\tclaude\tjev\t1\t0\t0.000000\terror=1", report
        )
        self.assertIn("# judge real calls 3 cost $0.000135 failures 2", report)
        self.assertEqual(
            report[-1],
            f"# last real failure 2026-09-25T00:27:45.238Z find claude/jev: {UNABLE}",
        )

    def test_probe_session_is_kept_apart(self):
        self.real([SUCCESS_FIND])
        self.probe([FAILED_AUTO] + [FAILED_FIND] * 30)
        self.assertEqual(
            sc.fleet_line(self.rows(), NOW, True),
            "Jev judge 24h: 1 calls, $0.0001, 0 failures",
        )
        report = sc.judge_report(self.rows())
        self.assertIn(
            "probe\t2026-09-25\tfind\tclaude\tjev-xpk1-plant\t30\t0\t0.000000\terror=30",
            report,
        )
        self.assertIn("# judge probe calls 31 cost $0.000000 failures 31", report)
        self.assertIn("# judge real calls 1 cost $0.000135 failures 0", report)

    def test_other_providers_and_rows_older_than_24h_are_not_counted(self):
        self.real([OTHER_ERROR, OLD_FAILURE, SUCCESS_AUTO])
        self.assertEqual(
            sc.fleet_line(self.rows(), NOW, True),
            "Jev judge 24h: 1 calls, $0.0000, 0 failures",
        )
        report = sc.judge_report(self.rows())
        self.assertIn("# judge real calls 2 cost $0.000044 failures 1", report)
        self.assertNotIn("ollama", "\n".join(report))

    def test_no_session_files_is_not_run_never_zero_failures(self):
        line = sc.fleet_line(self.rows(), NOW, False)
        self.assertTrue(
            line.startswith("Jev judge 24h: NOT_RUN no omp session files"), line
        )
        self.assertNotIn("0 failures", line)


class HomeUnderTmp(unittest.TestCase):
    """A HOME under /tmp (Linux CI tempdirs) must not turn real sessions into probes.

    CI run 36079745187 failed 5 of 7 here: is_probe matched '/tmp/' in the absolute path.
    """

    def test_real_session_counts_when_home_is_under_tmp(self):
        for home in ("/tmp/ci/home", "/private/tmp/ci/home", "/home/runner/probe-home"):
            real = Path(
                home, ".omp/profiles/claude/agent/sessions/-Developer-jev/s.jsonl"
            )
            planted = Path(home, ".omp/agent/sessions/--private-tmp-x--/s.jsonl")
            with self.subTest(home=home):
                self.assertFalse(sc.is_probe(real, "/Users/josh/Developer/jev"))
                self.assertTrue(sc.is_probe(planted, "/tmp/x"))
                self.assertEqual(sc.profile_of(real), "claude")
                self.assertEqual(sc.profile_of(planted), "default")
        if not Path("/tmp").is_dir():
            self.skipTest("no /tmp on this host; the path arm above still ran")
        with tempfile.TemporaryDirectory(prefix="judge-usage-", dir="/tmp") as tmp:
            home = Path(tmp) / "home"
            write_session(
                home,
                "claude",
                "-Developer-jev",
                "/Users/josh/Developer/jev",
                [SUCCESS_FIND],
            )
            rows = list(sc.judge_rows(sorted(home.rglob("*.jsonl"))))
            self.assertEqual(
                sc.fleet_line(rows, NOW, True),
                "Jev judge 24h: 1 calls, $0.0001, 0 failures",
            )


class Cli(unittest.TestCase):
    """The real --fleet-line path and fleet-idle-watch's --once, with HOME pointed at a temp tree."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="judge-usage-")
        self.home = Path(self.tmp.name) / "home"
        self.home.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def census(self):
        env = dict(os.environ, HOME=str(self.home))
        return subprocess.run(
            [sys.executable, str(CENSUS), "--fleet-line"],
            capture_output=True,
            text=True,
            env=env,
            timeout=60,
        )

    def test_empty_home_prints_not_run_exit_0(self):
        done = self.census()
        self.assertEqual(done.returncode, 0)
        self.assertTrue(done.stdout.startswith("Jev judge 24h: NOT_RUN"), done.stdout)

    def test_recent_failure_is_in_the_line_and_never_sets_the_watch_exit_code(self):
        hour_ago = (datetime.now(timezone.utc) - timedelta(hours=1)).strftime(
            "%Y-%m-%dT%H:%M:%S.000Z"
        )
        row = dict(FAILED_FIND, timestamp=hour_ago)
        write_session(
            self.home, "grok", "-Developer-jev", "/Users/josh/Developer/jev", [row]
        )
        done = self.census()
        self.assertEqual(done.returncode, 0)
        self.assertIn(
            f"1 failures; last {hour_ago[:16]}Z find grok: {UNABLE}", done.stdout
        )
        out = io.StringIO()
        with (
            mock.patch.dict(os.environ, {"HOME": str(self.home)}),
            mock.patch.object(fiw, "poll", return_value={2: ("working", "")}),
            mock.patch.object(fiw, "ci_lines", return_value=[]),
            mock.patch.object(sys, "argv", ["fleet-idle-watch.py", "--once"]),
            contextlib.redirect_stdout(out),
        ):
            rc = fiw.main()
        self.assertEqual(
            rc, 0, "a judge failure is informational, never the watch's exit code"
        )
        self.assertIn(
            "Jev judge 24h: 1 calls, $0.0000, 1 failures; last", out.getvalue()
        )


if __name__ == "__main__":
    unittest.main()
