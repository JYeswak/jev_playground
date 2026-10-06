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
        self.registry = self.home / "surfaces.json"
        self.registry.write_text(
            json.dumps({"schema_version": "blast-radius-surfaces.v1", "surfaces": []}),
            encoding="utf-8",
        )

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
            mock.patch.object(fiw, "SURFACE_REGISTRY", self.registry),
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


class Scoreboard(unittest.TestCase):
    """Scoreboard input rows are cut from captured session and hook logs."""

    def test_daily_totals_and_observers_keep_unavailable_metrics_explicit(self):
        with tempfile.TemporaryDirectory(prefix="scoreboard-") as tmp:
            home = Path(tmp)
            session = write_session(
                home,
                "claude",
                "-Developer-jev",
                "/Users/josh/Developer/jev",
                [SUCCESS_AUTO, FAILED_FIND],
            )
            state = home / ".local" / "state" / "jev"
            state.mkdir(parents=True)
            find_row = {
                "schema": "jev-find-rank.v1",
                "ts": "2026-09-27T03:22:16.733Z",
                "session": "01a0e0c5-9ebf-70ea-b7e1-6c70b599a0db",
                "hits": [
                    "71812e7eb824cfc7e3cc5e5e380580a508bddcf1a7102bda296f1f1f71b5b1dd"
                ],
                "count": 1,
                "nextToolCalls": [
                    {"ordinal": 1, "tool": "eval", "touched": []},
                    {"ordinal": 2, "tool": "bash", "touched": []},
                    {"ordinal": 3, "tool": "eval", "touched": []},
                    {"ordinal": 4, "tool": "read", "touched": []},
                    {"ordinal": 5, "tool": "eval", "touched": []},
                    {"ordinal": 6, "tool": "read", "touched": []},
                    {"ordinal": 7, "tool": "eval", "touched": []},
                    {"ordinal": 8, "tool": "bash", "touched": []},
                    {"ordinal": 9, "tool": "eval", "touched": []},
                    {"ordinal": 10, "tool": "glob", "touched": []},
                ],
                "complete": True,
            }
            find_follow_through = {
                "schema": "jev-find-rank.v1",
                "ts": "2026-09-27T03:32:28.259Z",
                "session": "01a0e0d1-1967-72f7-a8d4-b946193213bb",
                "hits": [
                    "3529df3f561aead6ae72d2eea326f1e4ce08adab96228444a12313e3ce54bc8a",
                    "8a4a5ed7848204572eaf6630aea2e235ae9390a5ff00be9eaec4c2005f754795",
                    "abb1e1f3a283c224bb7fb8f6c8a9b554a2ccb0278dd3e31f020cdba6cda66e7d",
                ],
                "count": 3,
                "nextToolCalls": [
                    {
                        "ordinal": 5,
                        "tool": "read",
                        "touched": [
                            "3529df3f561aead6ae72d2eea326f1e4ce08adab96228444a12313e3ce54bc8a"
                        ],
                    }
                ],
                "complete": True,
            }
            (state / "find-rank.jsonl").write_text(
                json.dumps(find_row) + "\n" + json.dumps(find_follow_through) + "\n"
            )
            gate = {
                "ts": "2026-09-27T08:03:11.928Z",
                "status": "scored",
                "tokens": {"input_tokens": 746},
            }
            (state / "gate-shadow.jsonl").write_text(json.dumps(gate) + "\n")
            not_run = {
                "ts": "2026-09-24T02:19:17.240Z",
                "status": "not-run",
            }
            (state / "gate-observe.jsonl").write_text(json.dumps(not_run) + "\n")

            report = "\n".join(
                sc.scoreboard(
                    [session],
                    7,
                    now=datetime(2026, 9, 30, 12, tzinfo=timezone.utc),
                    state_roots=[state],
                )
            )
            self.assertIn("2026-09-24\tclaude\tauto-thinking\t1\t1058", report)
            self.assertIn("2026-09-25\tclaude\tfind\t1\t0", report)
            self.assertIn("# judge totals calls=2", report)
            self.assertIn("errors=1 error_rate=0.5000", report)
            self.assertIn("find-rank windows=2 complete=2 follow_through=1/2", report)
            self.assertIn("hook gate-shadow rows=1 scored=1 not_run=0 errors=0", report)
            self.assertIn("estimated_cost_usd=0.000031", report)
            self.assertIn("# promise-stop idle n=0", report)
            self.assertIn("session-start context tokens=NOT_RUN", report)

    def test_promise_stop_idle_uses_captured_next_user_row(self):
        with tempfile.TemporaryDirectory(prefix="promise-stop-") as tmp:
            home = Path(tmp)
            assistant = {
                "type": "message",
                "timestamp": "2026-09-23T05:02:58.352Z",
                "message": {
                    "role": "assistant",
                    "stopReason": "stop",
                    "content": [
                        {"type": "text", "text": "I'll run the full test suite"}
                    ],
                },
            }
            user = {
                "type": "message",
                "timestamp": "2026-09-23T05:04:03.918Z",
                "message": {"role": "user"},
            }
            path = write_session(
                home,
                "claude",
                "-Developer-jev",
                "/Users/josh/Developer/jev",
                [assistant, user],
            )
            _, _, _, _, idle, starts = sc.session_metric_stats(
                [path],
                datetime(2026, 9, 23, 5, tzinfo=timezone.utc),
                datetime(2026, 9, 23, 5, 10, tzinfo=timezone.utc),
            )
            self.assertEqual(len(idle), 1)
            self.assertAlmostEqual(idle[0], 65.566 / 60, places=6)
            self.assertEqual(starts, {})

    def test_session_start_adds_input_cache_read_and_cache_write(self):
        with tempfile.TemporaryDirectory(prefix="session-start-") as tmp:
            home = Path(tmp)
            zero_usage = {
                "type": "message",
                "timestamp": "2026-10-01T00:51:04.558Z",
                "message": {
                    "role": "assistant",
                    "usage": {"input": 0, "cacheRead": 0, "cacheWrite": 0},
                },
            }
            jev_call = {
                "type": "model_usage",
                "timestamp": "2026-10-01T00:57:03.167Z",
                "provider": "typesafe",
                "purpose": "auto-thinking",
            }
            first_nonzero_usage = {
                "type": "message",
                "timestamp": "2026-10-01T01:00:15.607Z",
                "message": {
                    "role": "assistant",
                    "usage": {"input": 4, "cacheRead": 0, "cacheWrite": 106236},
                },
            }
            path = write_session(
                home,
                "claude",
                "-Developer-jev",
                "/Users/josh/Developer/jev",
                [zero_usage, jev_call, first_nonzero_usage],
            )
            groups, _, _, _, _, starts = sc.session_metric_stats(
                [path],
                datetime(2026, 10, 1, tzinfo=timezone.utc),
                datetime(2026, 10, 1, 2, tzinfo=timezone.utc),
            )
            self.assertEqual(
                groups[("2026-10-01", "claude", "auto-thinking")]["calls"], 1
            )
            self.assertEqual(starts, {("2026-10-01", "claude"): [106240]})

    def test_non_jev_session_start_is_excluded(self):
        with tempfile.TemporaryDirectory(prefix="session-start-") as tmp:
            path = write_session(
                Path(tmp),
                "claude",
                "-Developer-jev",
                "/Users/josh/Developer/jev",
                [
                    {
                        "type": "message",
                        "timestamp": "2026-09-20T20:22:08.173Z",
                        "message": {
                            "role": "assistant",
                            "usage": {"input": 0, "cacheRead": 0, "cacheWrite": 0},
                        },
                    },
                    {
                        "type": "message",
                        "timestamp": "2026-09-20T20:22:33.021Z",
                        "message": {
                            "role": "assistant",
                            "usage": {
                                "input": 194,
                                "cacheRead": 90097,
                                "cacheWrite": 0,
                            },
                        },
                    },
                ],
            )
            groups, _, _, _, _, starts = sc.session_metric_stats(
                [path],
                datetime(2026, 9, 20, tzinfo=timezone.utc),
                datetime(2026, 9, 21, tzinfo=timezone.utc),
            )
            self.assertEqual(groups, {})
            self.assertEqual(starts, {})

    def test_days_argument_is_bounded_and_required(self):
        self.assertEqual(sc.scoreboard_days(["--scoreboard", "--days", "7"]), 7)
        for args in (
            ["--scoreboard"],
            ["--days", "0"],
            ["--days", "366"],
            ["--days", "x"],
        ):
            with self.subTest(args=args), self.assertRaises(ValueError):
                sc.scoreboard_days(args)

    def test_cli_scoreboard_runs_from_temp_home(self):
        with tempfile.TemporaryDirectory(prefix="scoreboard-cli-") as tmp:
            home = Path(tmp)
            stamp = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
            write_session(
                home,
                "claude",
                "-Developer-jev",
                "/Users/josh/Developer/jev",
                [dict(SUCCESS_AUTO, timestamp=stamp)],
            )
            done = subprocess.run(
                [sys.executable, str(CENSUS), "--scoreboard", "--days", "7"],
                capture_output=True,
                text=True,
                env=dict(os.environ, HOME=str(home)),
                timeout=60,
                check=False,
            )
            self.assertEqual(done.returncode, 0, done.stderr)
            self.assertIn("# judge totals calls=1", done.stdout)
            self.assertIn("# promise-stop idle n=0", done.stdout)
            self.assertIn("session-start context tokens=NOT_RUN", done.stdout)


if __name__ == "__main__":
    unittest.main()
