"""scripts/fleet-idle-watch.py's classifier on process evidence (bead jev-6con). No tmux, no ps.

Fixtures, all captured read-only from the jev session 2026-09-25 ~05:37Z:
  ps-panes-0-2-4-5.txt   `ps -axo pid=,ppid=,command=` rows of panes 0, 2, 4, 5's process trees:
                         pane 0 a bare zsh; pane 2 omp with a live `infisical run -- docker run`
                         (a Jericho run under a bash tool call); pane 4 omp with only its helpers;
                         pane 5 omp with only its helpers.
  pane2-idle-prompt-docker.screen   pane 2's screen at that moment: an idle `❯` prompt and a status
                         line with no spinner, while the docker run above was live.
  pane5-diff-todo-no-status.screen  pane 5's capture cut above its status line: an edit view and a
                         todo panel, the shape that hid the status line when the screen-only
                         classifier read panes 2 and 5 as 'no-agent' at 05:0xZ.
  pane4-unsubmitted-composer.screen  idle composer-box shape observed on pane 3 2026-10-01
                         with the real conductor resend packet
                         var/agent-tmp/dispatch-pane-4-resend.txt lines 1-5 typed inside.

Inbox pages (bead jev-lqfm): Agent Mail archive files written into a temp dir per test, in the
shape of the real AmberWillow inbox file ...__42478.md (`---json`, the JSON front matter, `---`,
the body). The send function is a list-appending stub, so no test pages pane 1.
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
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
FIX = HERE / "fixtures"
WATCH = HERE.parents[1] / "scripts" / "fleet-idle-watch.py"

spec = importlib.util.spec_from_file_location("fleet_idle_watch", WATCH)
fiw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fiw)

TABLE = fiw.parse_ps((FIX / "ps-panes-0-2-4-5.txt").read_text())
PANE2_SCREEN = (FIX / "pane2-idle-prompt-docker.screen").read_text()
PANE5_SCREEN = (FIX / "pane5-diff-todo-no-status.screen").read_text()
PANE_PID = {0: 1370, 2: 11832, 4: 45425, 5: 37332}
OLD = 600.0  # a session file last written 10 minutes ago
WAIT_SCREEN = PANE5_SCREEN + "\n⏳ waiting on 1 job\n"


def snapshot(pane, screen, command="bun", session_age=OLD, table=TABLE, cpu_tools=None):
    omp, tools = fiw.omp_processes(table, PANE_PID[pane])
    fields = {
        "command": command,
        "screen": screen,
        "omp": omp is not None,
        "tools": tuple(tools),
        "session_age": session_age,
    }
    if cpu_tools is not None:
        fields["cpu_tools"] = tuple(cpu_tools)
    return fiw.Snapshot(**fields)


class ShadowAdmission(unittest.TestCase):
    def test_env_flag_cannot_spawn_unapproved_provider_worker(self):
        with mock.patch.dict(os.environ, {"JEV_FLEET_SHADOW": "1"}):
            module_spec = importlib.util.spec_from_file_location(
                "fleet_shadow_refusal", WATCH
            )
            module = importlib.util.module_from_spec(module_spec)
            module_spec.loader.exec_module(module)
            self.assertFalse(module.SHADOW_ENABLED)
            with mock.patch.object(
                module.subprocess, "Popen", side_effect=AssertionError("child started")
            ):
                module.submit_shadow(
                    {2: ("working", "synthetic status", "private pane line")}
                )

    def test_direct_child_refuses_before_exporting_pane_state(self):
        status = "PRIVATE_PANE_STATE_31ca"
        fake_key = "-".join(("synthetic", "not", "for", "provider"))
        result = subprocess.run(
            ["node", "scripts/fleet-jev-shadow.mjs"],
            input=json.dumps({"pane_index": 2, "status_line": status}) + "\n",
            capture_output=True,
            text=True,
            env={**os.environ, "TYPESAFE_API_KEY": fake_key},
            cwd=HERE.parents[1],
            timeout=10,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("permission-required", result.stderr)
        self.assertNotIn(status, result.stdout + result.stderr)
        self.assertNotIn(fake_key, result.stdout + result.stderr)


class PollTimeout(unittest.TestCase):
    def poll_without_timeout_leak(self):
        try:
            return fiw.poll()
        except subprocess.TimeoutExpired as error:
            self.fail(f"poll leaked the recorded timeout: {error}")

    def test_ps_timeout_is_not_run_and_does_not_escape_poll(self):
        tmux_command = [
            "tmux",
            "list-panes",
            "-t",
            fiw.SESSION,
            "-F",
            "#{pane_index} #{pane_pid} #{pane_current_command}",
        ]
        ps_command = ["ps", "-axo", "pid=,ppid=,pcpu=,command="]

        def run(command, **kwargs):
            if command == tmux_command:
                return subprocess.CompletedProcess(command, 0, "2 11832 bun\n", "")
            if command == ps_command:
                self.assertEqual(kwargs["timeout"], 10)
                raise subprocess.TimeoutExpired(cmd=ps_command, timeout=10)
            self.fail(f"unexpected subprocess: {command!r}")

        output = io.StringIO()
        with mock.patch.object(fiw.subprocess, "run", side_effect=run):
            with contextlib.redirect_stdout(output):
                try:
                    states = fiw.poll()
                except subprocess.TimeoutExpired as error:
                    self.fail(f"poll leaked the recorded ps timeout: {error}")

        self.assertIsNone(states)
        self.assertIn("NOT_RUN", output.getvalue())
        self.assertIn("ps", output.getvalue())

    def test_tmux_list_panes_timeout_is_not_run(self):
        command = [
            "tmux",
            "list-panes",
            "-t",
            fiw.SESSION,
            "-F",
            "#{pane_index} #{pane_pid} #{pane_current_command}",
        ]

        def run(actual, **kwargs):
            self.assertEqual(actual, command)
            self.assertEqual(kwargs["timeout"], 10)
            raise subprocess.TimeoutExpired(cmd=command, timeout=10)

        output = io.StringIO()
        with mock.patch.object(fiw.subprocess, "run", side_effect=run):
            with contextlib.redirect_stdout(output):
                states = self.poll_without_timeout_leak()

        self.assertIsNone(states)
        self.assertIn("NOT_RUN", output.getvalue())
        self.assertIn("tmux list-panes", output.getvalue())

    def test_tmux_capture_pane_timeout_discards_partial_poll(self):
        list_command = [
            "tmux",
            "list-panes",
            "-t",
            fiw.SESSION,
            "-F",
            "#{pane_index} #{pane_pid} #{pane_current_command}",
        ]
        ps_command = ["ps", "-axo", "pid=,ppid=,pcpu=,command="]

        def run(command, **kwargs):
            if command == list_command:
                return subprocess.CompletedProcess(command, 0, "5 37332 bun\n", "")
            if command == ps_command:
                return subprocess.CompletedProcess(
                    command, 0, (FIX / "ps-panes-0-2-4-5.txt").read_text(), ""
                )
            if command[:2] == ["tmux", "capture-pane"]:
                self.assertEqual(kwargs["timeout"], 10)
                raise subprocess.TimeoutExpired(cmd=command, timeout=10)
            self.fail(f"unexpected subprocess: {command!r}")

        output = io.StringIO()
        with mock.patch.object(fiw.subprocess, "run", side_effect=run):
            with contextlib.redirect_stdout(output):
                states = self.poll_without_timeout_leak()

        self.assertIsNone(states)
        self.assertIn("NOT_RUN", output.getvalue())
        self.assertIn("tmux capture-pane", output.getvalue())

    def test_lsof_timeout_discards_partial_poll(self):
        list_command = [
            "tmux",
            "list-panes",
            "-t",
            fiw.SESSION,
            "-F",
            "#{pane_index} #{pane_pid} #{pane_current_command}",
        ]
        ps_command = ["ps", "-axo", "pid=,ppid=,pcpu=,command="]

        def run(command, **kwargs):
            if command == list_command:
                return subprocess.CompletedProcess(command, 0, "5 37332 bun\n", "")
            if command == ps_command:
                return subprocess.CompletedProcess(
                    command, 0, (FIX / "ps-panes-0-2-4-5.txt").read_text(), ""
                )
            if command[:2] == ["tmux", "capture-pane"]:
                return subprocess.CompletedProcess(command, 0, PANE5_SCREEN, "")
            if command[:2] == ["lsof", "-p"]:
                self.assertEqual(kwargs["timeout"], 10)
                raise subprocess.TimeoutExpired(cmd=command, timeout=10)
            self.fail(f"unexpected subprocess: {command!r}")

        output = io.StringIO()
        with mock.patch.object(fiw.subprocess, "run", side_effect=run):
            with contextlib.redirect_stdout(output):
                states = self.poll_without_timeout_leak()

        self.assertIsNone(states)
        self.assertIn("NOT_RUN", output.getvalue())
        self.assertIn("lsof", output.getvalue())

    def test_daemon_reports_surface_census_timeout_and_reaches_next_wait(self):
        class StopAfterRound(Exception):
            pass

        def run(command, **kwargs):
            self.assertTrue(any("surface-census.py" in part for part in command))
            self.assertEqual(kwargs["timeout"], 60)
            raise subprocess.TimeoutExpired(cmd=command, timeout=60)

        output = io.StringIO()
        with (
            mock.patch.object(fiw, "poll", return_value={2: ("working", "")}),
            mock.patch.object(fiw, "SHADOW_ONLY", False),
            mock.patch.object(fiw, "ci_lines", return_value=[]),
            mock.patch.object(fiw, "stranger_round", return_value=None),
            mock.patch.object(fiw, "inbox_round", return_value="Inbox: NOT_RUN test"),
            mock.patch.object(fiw.subprocess, "run", side_effect=run),
            mock.patch.object(fiw.time, "sleep", side_effect=StopAfterRound),
            mock.patch.object(sys, "argv", ["fleet-idle-watch.py"]),
            contextlib.redirect_stdout(output),
        ):
            with self.assertRaises(StopAfterRound):
                fiw.main()

        self.assertIn("NOT_RUN", output.getvalue())
        self.assertIn("surface-census.py", output.getvalue())

    def test_once_skips_the_round_after_poll_timeout(self):
        output = io.StringIO()
        with (
            mock.patch.object(fiw, "poll", return_value=None),
            mock.patch.object(
                fiw, "ci_lines", side_effect=AssertionError("round must skip")
            ),
            mock.patch.object(sys, "argv", ["fleet-idle-watch.py", "--once"]),
            contextlib.redirect_stdout(output),
        ):
            try:
                result = fiw.main()
            except Exception as error:
                self.fail(f"--once leaked the poll timeout sentinel: {error}")

        self.assertEqual(result, 2)

    def test_daemon_sleeps_and_continues_after_poll_timeout(self):
        class StopAfterWait(Exception):
            pass

        with (
            mock.patch.object(fiw, "poll", return_value=None),
            mock.patch.object(
                fiw, "ci_lines", side_effect=AssertionError("round must skip")
            ),
            mock.patch.object(fiw.time, "sleep", side_effect=StopAfterWait),
            mock.patch.object(sys, "argv", ["fleet-idle-watch.py"]),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            try:
                fiw.main()
            except StopAfterWait:
                pass
            except Exception as error:
                self.fail(f"daemon leaked the poll timeout: {error}")
            else:
                self.fail("daemon did not wait for the next round")


class NeedsHuman(unittest.TestCase):
    # Positive: controlled real OMP turn on the codex profile, 2026-10-01,
    # prompt_result completed sessionSettled true, stopReason stop.
    POSITIVE = "May I proceed with the harmless reversible formatting step now \u2014 yes or no?"
    # Negative: captured pane 6 session line 19945 (row 4c3d872b, 241 chars,
    # sha bd61a0ba965aab7500b0871613cb4bd218c64fd2632d5cb1a832d82d6ecf8b56).
    NEGATIVE = "The latest explicit instruction in the archived conversation parks new work until a concrete build/test packet arrives. I\u2019m not claiming from br ready or starting commands, tests, provider calls, edits, or commits. Waiting for that packet."

    def write_session(self, directory, texts):
        path = Path(directory) / "session.jsonl"
        with path.open("w", encoding="utf-8") as handle:
            for number, text in enumerate(texts):
                row = {
                    "id": f"row-{number}",
                    "message": {
                        "role": "assistant",
                        "content": [{"type": "text", "text": text}],
                        "stopReason": "stop",
                        "timestamp": 1790821507000 + number,
                    },
                }
                handle.write(json.dumps(row) + "\n")
        return path

    def isolated(self, tmp):
        paged = Path(tmp) / "paged.json"
        day = Path(tmp) / "day.json"
        log = Path(tmp) / "calls.jsonl"
        return {
            "JEV_WATCH_NEEDS_HUMAN_PAGED": str(paged),
            "JEV_WATCH_NEEDS_HUMAN_DAY": str(day),
            "JEV_WATCH_NEEDS_HUMAN_LOG": str(log),
        }

    def test_last_message_skips_toolcall_only_rows(self):
        tmp = tempfile.mkdtemp(prefix="fiw-needs-human-")
        path = Path(tmp) / "session.jsonl"
        tool_only = {
            "id": "tool-1",
            "message": {
                "role": "assistant",
                "content": [
                    {"type": "toolCall", "id": "1", "name": "bash", "arguments": {}}
                ],
                "stopReason": "stop",
            },
        }
        positive = {
            "id": "row-9",
            "message": {
                "role": "assistant",
                "content": [
                    {"type": "thinking"},
                    {"type": "text", "text": self.POSITIVE},
                ],
                "stopReason": "stop",
                "timestamp": 1790821507006,
            },
        }
        path.write_text(
            json.dumps(tool_only) + "\n" + json.dumps(positive) + "\n", encoding="utf-8"
        )
        found = fiw.last_assistant_message(path)
        self.assertEqual(found["text"], self.POSITIVE)
        self.assertEqual(found["row_id"], "row-9")

    def test_positive_pages_and_negative_stays_silent(self):
        tmp = tempfile.mkdtemp(prefix="fiw-needs-human-")
        with mock.patch.dict(os.environ, self.isolated(tmp)):
            positive_file = self.write_session(tmp, [self.NEGATIVE, self.POSITIVE])
            sent = []
            paged = fiw.check_idle_needs_human(
                6,
                97023,
                1790821600.0,
                send=sent.append,
                asker=lambda text: {
                    "ok": True,
                    "score": 0.91,
                    "model": "jev-1.13.0",
                    "latencyMs": 212,
                    "usage": {"input_tokens": 120, "output_tokens": 0},
                },
                session_file=positive_file,
            )
            self.assertTrue(paged)
            self.assertEqual(len(sent), 1)
            self.assertTrue(sent[0].startswith("NEEDS-HUMAN pane 6: "))
            self.assertIn("May I proceed", sent[0])
            negative_file = self.write_session(tmp, [self.NEGATIVE])
            sent.clear()
            calls = [0]

            def low_asker(text):
                calls[0] += 1
                return {
                    "ok": True,
                    "score": 0.05,
                    "model": "jev-1.13.0",
                    "latencyMs": 180,
                }

            paged = fiw.check_idle_needs_human(
                6,
                97023,
                1790821700.0,
                send=sent.append,
                asker=low_asker,
                session_file=negative_file,
            )
            self.assertFalse(paged)
            self.assertEqual(sent, [])
            self.assertEqual(calls[0], 1)

    def test_once_per_message_cap_auth_stop_and_fail_open(self):
        tmp = tempfile.mkdtemp(prefix="fiw-needs-human-")
        with mock.patch.dict(os.environ, self.isolated(tmp)):
            session_file = self.write_session(tmp, [self.POSITIVE])
            calls = []
            asker = lambda text: (
                calls.append(text),
                {"ok": True, "score": 0.95, "model": "jev-1.13.0", "latencyMs": 100},
            )[1]
            self.assertTrue(
                fiw.check_idle_needs_human(
                    6,
                    97023,
                    1790821600.0,
                    send=lambda message: True,
                    asker=asker,
                    session_file=session_file,
                )
            )
            self.assertEqual(len(calls), 1)
            self.assertFalse(
                fiw.check_idle_needs_human(
                    6,
                    97023,
                    1790821700.0,
                    send=lambda message: True,
                    asker=asker,
                    session_file=session_file,
                )
            )
            self.assertEqual(len(calls), 1)
            refused = fiw.check_idle_needs_human(
                6,
                97023,
                1790821800.0,
                send=lambda message: True,
                asker=lambda text: (_ for _ in ()).throw(
                    AssertionError("cap must stop the call")
                ),
                session_file=session_file,
                cap=1,
            )
            self.assertFalse(refused)
            failing = fiw.check_idle_needs_human(
                5,
                37332,
                1790821900.0,
                send=lambda message: True,
                asker=lambda text: {
                    "ok": False,
                    "reason": "transport",
                    "error": "helper TimeoutExpired",
                    "model": "jev-1.13.0",
                    "latencyMs": 0,
                },
                session_file=session_file,
            )
            self.assertFalse(failing)
            denied = fiw.check_idle_needs_human(
                4,
                78292,
                1790822000.0,
                send=lambda message: True,
                asker=lambda text: {
                    "ok": False,
                    "reason": "http",
                    "error": "systemOne HTTP 403: forbidden",
                    "model": "jev-1.13.0",
                    "latencyMs": 50,
                },
                session_file=session_file,
            )
            self.assertFalse(denied)
            after_stop = fiw.check_idle_needs_human(
                3,
                88558,
                1790822100.0,
                send=lambda message: True,
                asker=lambda text: (_ for _ in ()).throw(
                    AssertionError("auth stop must skip the call")
                ),
                session_file=session_file,
            )
            self.assertFalse(after_stop)


class ProcessTree(unittest.TestCase):
    def test_omp_found_under_the_pane_shell(self):
        self.assertEqual(fiw.omp_processes(TABLE, PANE_PID[2])[0], 43091)
        self.assertEqual(fiw.omp_processes(TABLE, PANE_PID[5])[0], 37384)

    def test_bare_shell_has_no_omp(self):
        self.assertEqual(fiw.omp_processes(TABLE, PANE_PID[0]), (None, []))

    def test_helpers_are_not_tools(self):
        # panes 4 and 5 carry the eval kernel, the omp workers and two MCP servers, nothing else
        self.assertEqual(fiw.omp_processes(TABLE, PANE_PID[4])[1], [])
        self.assertEqual(fiw.omp_processes(TABLE, PANE_PID[5])[1], [])

    def test_tool_call_and_its_child_are_tools(self):
        tools = fiw.omp_processes(TABLE, PANE_PID[2])[1]
        self.assertEqual(len(tools), 2, tools)
        self.assertTrue(tools[0].startswith("infisical run"), tools)
        self.assertTrue(tools[1].startswith("docker run"), tools)

    def test_subprocess_of_the_eval_kernel_is_a_tool(self):
        # a helper's descendants are still walked: pane 5's python kernel (32964) runs a script
        table = dict(TABLE)
        table[99001] = (32964, "python3 work/loss-depth/run.py selftest")
        self.assertEqual(
            fiw.omp_processes(table, PANE_PID[5])[1],
            ["python3 work/loss-depth/run.py selftest"],
        )

    def test_omp_worker_is_not_mistaken_for_omp_itself(self):
        table = {
            10: (1, "-zsh"),
            11: (
                10,
                "/opt/bun /x/pi-coding-agent/dist/cli.js __omp_worker_daemon_broker",
            ),
        }
        self.assertEqual(fiw.omp_processes(table, 10), (None, []))


class Classify(unittest.TestCase):
    def test_hidden_status_line_with_omp_is_never_no_agent(self):
        # measured false reading 1 (05:0xZ): omp live, status line hidden -> read 'no-agent'
        state, evidence = fiw.classify(snapshot(5, PANE5_SCREEN))
        self.assertEqual(state, "idle", evidence)
        self.assertIn("no status line on screen", evidence)

    def test_hidden_status_line_with_fresh_session_is_working(self):
        state, evidence = fiw.classify(snapshot(5, PANE5_SCREEN, session_age=12.0))
        self.assertEqual((state, evidence), ("working", "session written 12s ago"))

    def test_idle_prompt_over_a_live_docker_run_is_working(self):
        # measured false reading 2 (05:34Z): '❯', no spinner, docker run live -> read 'idle'
        state, evidence = fiw.classify(snapshot(2, PANE2_SCREEN))
        self.assertEqual(state, "working", evidence)
        self.assertTrue(evidence.startswith("child: docker run --rm"), evidence)
        self.assertTrue(evidence.endswith("(+1 more)"), evidence)

    def test_true_no_agent(self):
        state, evidence = fiw.classify(
            snapshot(0, "josh@studio jev % ", command="zsh", session_age=None)
        )
        self.assertEqual(state, "no-agent", evidence)

    def test_stale_wait_with_only_helpers_is_stalled(self):
        state, evidence = fiw.classify(
            snapshot(
                5,
                WAIT_SCREEN,
                session_age=fiw.IDLE_STALL_S,
                cpu_tools=[],
            )
        )
        self.assertEqual(state, "stalled-wait", evidence)
        self.assertIn("wait marker", evidence)
        self.assertIn("session idle 600s", evidence)

    def test_wait_with_running_descendant_is_working(self):
        state, evidence = fiw.classify(
            snapshot(
                5,
                WAIT_SCREEN,
                session_age=fiw.IDLE_STALL_S,
                cpu_tools=["docker run --rm battle"],
            )
        )
        self.assertEqual(state, "working", evidence)
        self.assertIn("child using CPU", evidence)

    def test_wait_under_stall_age_is_working(self):
        state, evidence = fiw.classify(
            snapshot(
                5,
                WAIT_SCREEN,
                session_age=fiw.IDLE_STALL_S - 1,
                cpu_tools=[],
            )
        )
        self.assertEqual(state, "working", evidence)
        self.assertIn("session written 599s ago", evidence)

    def test_wait_on_a_live_paced_child_at_idle_cpu_is_working(self):
        # jev-oxdq, 2026-09-25 ~10:40Z: pane 2 waited on a paced free-model client that sleeps
        # between requests (0.0 CPU); session idle 11 min -> paged STALLED while rows kept landing.
        table = dict(TABLE)
        table.update(
            fiw.parse_ps(
                "8741 37384 0.0 upstream/typesafe-ai/system-one-adapter-python/.venv/bin/python "
                "work/openrouter-incumbents/run.py nex-agi/nex-n2.5-mini:free sst5 "
                "--max-requests 200\n"
            )
        )
        cpu_tools = fiw.omp_cpu_tools(table, PANE_PID[5])
        self.assertEqual(cpu_tools, [])
        state, evidence = fiw.classify(
            snapshot(
                5, WAIT_SCREEN, session_age=900.0, table=table, cpu_tools=cpu_tools
            )
        )
        self.assertEqual(state, "working", evidence)
        self.assertIn("child alive, idle CPU", evidence)
        self.assertIn("python work/openrouter-incumbents/run.py", evidence)

    def test_wait_with_no_child_at_all_is_stalled(self):
        # jev-t54m's incidents: the waited-on run had exited, nothing under omp -> page (safe side)
        table = fiw.parse_ps(
            "10 1 0.0 -zsh\n11 10 0.3 bun /Users/josh/.bun/bin/omp --profile claude\n"
        )
        omp, tools = fiw.omp_processes(table, 10)
        snap = fiw.Snapshot(
            command="bun",
            screen=WAIT_SCREEN,
            omp=omp is not None,
            tools=tuple(tools),
            cpu_tools=tuple(fiw.omp_cpu_tools(table, 10)),
            session_age=900.0,
        )
        state, evidence = fiw.classify(snap)
        self.assertEqual(state, "stalled-wait", evidence)
        self.assertIn("session idle 900s", evidence)

    def test_stalled_wait_pages_once_per_episode(self):
        sent = []
        stalled_since = {}
        alerted = set()

        def send(message):
            sent.append(message)
            return True

        self.assertTrue(
            fiw.page_stalled_once(
                5,
                now=1800.0,
                session_age=1200.0,
                last_line="Wait: waiting on 1 job",
                stalled_since=stalled_since,
                alerted=alerted,
                send=send,
            )
        )
        self.assertFalse(
            fiw.page_stalled_once(
                5,
                now=1860.0,
                session_age=1260.0,
                last_line="Wait: waiting on 1 job",
                stalled_since=stalled_since,
                alerted=alerted,
                send=send,
            )
        )
        self.assertEqual(
            sent,
            [
                "STALLED pane 5: waiting 20 min, session idle 20 min, last line: "
                "Wait: waiting on 1 job"
            ],
        )

    def test_true_idle(self):
        # pane 4's tree (helpers only), pane 2's idle status line, old session file
        state, evidence = fiw.classify(snapshot(4, PANE2_SCREEN))
        self.assertEqual(state, "idle", evidence)
        self.assertEqual(
            evidence, "no spinner, no tool child, session written 600s ago"
        )

    def test_session_freshness_boundary(self):
        fresh = fiw.SESSION_FRESH
        self.assertEqual(
            fiw.classify(snapshot(4, PANE2_SCREEN, session_age=fresh - 1))[0], "working"
        )
        self.assertEqual(
            fiw.classify(snapshot(4, PANE2_SCREEN, session_age=fresh))[0], "idle"
        )

    def test_no_open_session_file_is_idle_not_working(self):
        state, evidence = fiw.classify(snapshot(4, PANE2_SCREEN, session_age=None))
        self.assertEqual(state, "idle")
        self.assertIn("no open session file", evidence)

    def test_status_line_selftest_still_holds(self):
        self.assertEqual(fiw.selftest(), 0)


def epoch(stamp):
    return (
        datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ")
        .replace(tzinfo=timezone.utc)
        .timestamp()
    )


STARTED = epoch("2026-09-25T06:00:00Z")  # watcher start; first-run cutoff is 05:45Z


def mail(inbox, msg_id, importance, created, subject, sender="WindyLantern", raw=None):
    """One archive file, named and shaped like the real one."""
    month = inbox / created[:4] / created[5:7]
    month.mkdir(parents=True, exist_ok=True)
    stamp = created[:19].replace(":", "-") + "Z"
    path = month / f"{stamp}__{subject.lower().replace(' ', '-')[:40]}__{msg_id}.md"
    front = {
        "id": msg_id,
        "from": sender,
        "to": ["AmberWillow"],
        "cc": [],
        "bcc": [],
        "subject": subject,
        "created": created,
        "thread_id": "jev-9gtw.4",
        "project": "/Users/josh/Developer/jev",
        "project_slug": "users-josh-developer-jev",
        "importance": importance,
        "ack_required": importance == "urgent",
        "attachments": [],
    }
    head = raw if raw is not None else json.dumps(front, indent=2)
    path.write_text(f"---json\n{head}\n---\n\nbody of {msg_id}\n")
    return path


URGENT_PAGE = (
    "MAIL urgent from WindyLantern: [URGENT] TypeSafe key emitted during MiniWoB env check"
    " (id 42478, 05:57Z)"
)
HIGH_PAGE = (
    "MAIL high from EmeraldFox: verify done: jev-6con CONFIRMED (id 42481, 06:05Z)"
)


class Inbox(unittest.TestCase):
    def setUp(self):
        # mkdtemp and left in place: this lane never deletes files (AGENTS.md RULE 1)
        self.root = Path(tempfile.mkdtemp(prefix="fiw-inbox-"))
        self.inbox = self.root / "AmberWillow" / "inbox"
        self.state = self.root / "state" / "inbox-paged.json"
        self.sent = []
        mail(
            self.inbox,
            42478,
            "urgent",
            "2026-09-25T05:57:22.203681Z",
            "[URGENT] TypeSafe key emitted during MiniWoB env check",
        )
        mail(
            self.inbox,
            42481,
            "high",
            "2026-09-25T06:05:10.000001Z",
            "verify done: jev-6con CONFIRMED",
            sender="EmeraldFox",
        )
        mail(self.inbox, 42482, "normal", "2026-09-25T06:06:00.5Z", "fyi")
        mail(
            self.inbox,
            42483,
            "urgent",
            "2026-09-25T06:07:00.1Z",
            "cut off",
            raw='{\n  "id": 42483,\n  "importance": "urgent",',
        )
        # older than start - 15 min: history on a first run, never paged
        mail(self.inbox, 42400, "urgent", "2026-09-25T05:40:00.0Z", "old incident")

    def send(self, message):
        self.sent.append(message)
        return True

    def round(self, module=None, send=None):
        return (module or fiw).inbox_round(
            self.inbox, self.state, STARTED, send or self.send
        )

    def test_urgent_and_high_page_once_each_normal_and_pre_start_never(self):
        line = self.round()
        self.assertEqual(self.sent, [URGENT_PAGE, HIGH_PAGE])
        self.assertTrue(
            line.startswith("Inbox: 2 urgent/high paged this round, 2 paged total"),
            line,
        )

    def test_a_second_poll_pages_nothing_new(self):
        self.round()
        line = self.round()
        self.assertEqual(self.sent, [URGENT_PAGE, HIGH_PAGE])
        self.assertTrue(
            line.startswith("Inbox: 0 urgent/high paged this round, 2 paged total"),
            line,
        )

    def test_a_restart_with_the_same_state_file_pages_nothing(self):
        self.round()
        spec2 = importlib.util.spec_from_file_location(
            "fleet_idle_watch_restart", WATCH
        )
        fresh = importlib.util.module_from_spec(spec2)
        spec2.loader.exec_module(fresh)
        restarted = []
        line = self.round(fresh, send=lambda m: restarted.append(m) or True)
        # the pre-start message included: the state file exists now, so no first-run cutoff
        self.assertEqual(restarted, [])
        self.assertIn("2 paged total", line)

    def test_a_new_high_after_the_first_round_is_paged(self):
        self.round()
        mail(
            self.inbox,
            42490,
            "high",
            "2026-09-25T06:30:00.0Z",
            "callback",
            sender="RedMaple",
        )
        self.round()
        self.assertEqual(
            self.sent[2:], ["MAIL high from RedMaple: callback (id 42490, 06:30Z)"]
        )

    def test_an_id_already_in_the_state_file_is_not_paged(self):
        self.state.parent.mkdir(parents=True)
        self.state.write_text(json.dumps({"paged": [42478], "history": [42400]}))
        line = self.round()
        self.assertEqual(self.sent, [HIGH_PAGE])
        self.assertIn("2 paged total", line)

    def test_malformed_front_matter_is_reported_in_the_line_not_raised(self):
        line = self.round()
        self.assertIn("1 malformed", line)
        self.assertIn("__42483.md", line)

    def test_a_failed_send_is_not_recorded_so_the_next_round_retries(self):
        line = self.round(send=lambda m: False)
        self.assertIn("2 send failed", line)
        self.round()
        self.assertEqual(self.sent, [URGENT_PAGE, HIGH_PAGE])

    def test_missing_inbox_dir_is_not_run_and_pages_nothing(self):
        line = fiw.inbox_round(
            self.root / "Nobody" / "inbox", self.state, STARTED, self.send
        )
        self.assertTrue(line.startswith("Inbox: NOT_RUN "), line)
        self.assertEqual(self.sent, [])

    def test_unreadable_state_file_is_not_run_and_pages_nothing(self):
        self.state.parent.mkdir(parents=True)
        self.state.write_text("{not json")
        line = self.round()
        self.assertTrue(line.startswith("Inbox: NOT_RUN "), line)
        self.assertEqual(self.sent, [])
        self.assertEqual(self.state.read_text(), "{not json")

    def test_once_prints_the_inbox_line_after_the_skills_line(self):
        self.state.parent.mkdir(parents=True)
        self.state.write_text(json.dumps({"paged": [42478, 42481], "history": [42400]}))
        env = {
            "JEV_WATCH_INBOX_ROOT": str(self.root),
            "JEV_WATCH_INBOX_AGENT": "AmberWillow",
            "JEV_WATCH_INBOX_STATE": str(self.state),
        }
        out = io.StringIO()
        with (
            mock.patch.dict(os.environ, env),
            mock.patch.object(fiw, "poll", return_value={2: ("working", "")}),
            mock.patch.object(fiw, "ci_lines", return_value=["CI main: green"]),
            mock.patch.object(
                fiw, "judge_lines", return_value=["Jev judge 24h: x", "Skills 24h: y"]
            ),
            mock.patch.object(fiw, "send_pane1", side_effect=self.send),
            mock.patch.object(sys, "argv", ["fleet-idle-watch.py", "--once"]),
            contextlib.redirect_stdout(out),
        ):
            rc = fiw.main()
        self.assertEqual(rc, 0)
        lines = out.getvalue().splitlines()
        self.assertEqual(lines[-2], "Skills 24h: y")
        self.assertTrue(
            lines[-1].startswith("Inbox: 0 urgent/high paged this round, 2 paged total")
        )
        self.assertEqual(self.sent, [])

    def test_daemon_first_run_uses_process_start_cutoff_when_inbox_arrives_later(self):
        class StopAfterSecondRound(Exception):
            pass

        inbox = self.root / "late" / "AmberWillow" / "inbox"
        state = self.root / "late-state" / "inbox-paged.json"
        clock = [STARTED]
        sent = []
        sleep_calls = 0

        def sleep(_interval):
            nonlocal sleep_calls
            sleep_calls += 1
            if sleep_calls == 1:
                mail(
                    inbox,
                    42495,
                    "urgent",
                    "2026-09-25T06:10:00.000000Z",
                    "startup lease",
                )
                clock[0] = STARTED + 1800
                return
            raise StopAfterSecondRound

        output = io.StringIO()
        with (
            mock.patch.object(fiw, "poll", return_value={}),
            mock.patch.object(fiw, "submit_shadow"),
            mock.patch.object(fiw, "SHADOW_ONLY", False),
            mock.patch.object(fiw, "hook_load_round", return_value=None),
            mock.patch.object(fiw, "ci_lines", return_value=[]),
            mock.patch.object(fiw, "stranger_round", return_value=None),
            mock.patch.object(fiw, "judge_lines", return_value=[]),
            mock.patch.object(fiw, "key_round", return_value=None),
            mock.patch.object(fiw, "stale_lock_round", return_value=None),
            mock.patch.object(fiw, "capture_lock_creator", return_value=None),
            mock.patch.object(fiw, "inbox_paths", return_value=(inbox, state)),
            mock.patch.object(
                fiw, "page", side_effect=lambda message: sent.append(message) or True
            ),
            mock.patch.object(fiw.ROUTER, "round", return_value=set()),
            mock.patch.object(fiw.time, "time", side_effect=lambda: clock[0]),
            mock.patch.object(fiw.time, "monotonic", return_value=1.0),
            mock.patch.object(fiw.time, "sleep", side_effect=sleep),
            mock.patch.object(sys, "argv", ["fleet-idle-watch.py"]),
            contextlib.redirect_stdout(output),
        ):
            with self.assertRaises(StopAfterSecondRound):
                fiw.main()

        self.assertEqual(
            sent,
            ["MAIL urgent from WindyLantern: startup lease (id 42495, 06:10Z)"],
        )
        self.assertIn("Inbox: NOT_RUN no inbox dir", output.getvalue())
        self.assertIn(
            "Inbox: 1 urgent/high paged this round, 1 paged total",
            output.getvalue(),
        )
        self.assertNotIn("router failed:", output.getvalue())
        saved = json.loads(state.read_text())
        self.assertEqual(saved["history"], [])
        self.assertEqual(saved["paged"], [42495])


class StrangerPager(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="fiw-stranger-"))
        self.state = self.root / "state" / "stranger-paged.json"
        self.sent = []

    def send(self, message):
        self.sent.append(message)
        return True

    def test_new_failure_pages_once_and_persists(self):
        lines = [
            "README stranger nightly: failure 36134076882 25m ago",
            "  FIRST MISMATCH row changed class: planted",
        ]
        note = fiw.stranger_round(lines, self.state, self.send)
        self.assertEqual(
            self.sent,
            [
                "README STRANGER FAILURE: run 36134076882 25m ago; "
                "row changed class: planted"
            ],
        )
        self.assertTrue(
            note.startswith("Stranger page: 1 new failures paged this round")
        )
        self.assertIn("36134076882", self.state.read_text())
        self.assertEqual(
            fiw.stranger_round(lines, self.state, self.send),
            "Stranger page: 0 new failures paged this round, 1 paged total",
        )
        self.assertEqual(len(self.sent), 1)

    def test_stale_failure_pages_and_failed_send_retries(self):
        lines = [
            "README stranger nightly: STALE failure 36131647900 2d ago",
            "  FIRST MISMATCH new README command: planted",
        ]
        self.assertIn(
            "1 send failed",
            fiw.stranger_round(lines, self.state, lambda _message: False),
        )
        note = fiw.stranger_round(lines, self.state, self.send)
        self.assertIn("1 new failures paged this round", note)
        self.assertEqual(len(self.sent), 1)

    def test_success_and_not_run_do_not_page(self):
        lines = ["README stranger nightly: success 36135948301 25m ago"]
        self.assertIsNone(fiw.stranger_round(lines, self.state, self.send))
        self.assertIsNone(
            fiw.stranger_round(
                ["README stranger nightly: NOT_RUN no completed run"],
                self.state,
                self.send,
            )
        )
        self.assertEqual(self.sent, [])


class ShadowFeatures(unittest.TestCase):
    def test_shadow_features_strip_screen_text_and_preserve_process_signals(self):
        words = "(child: secret-not-to-send)  user prompt with private text"
        self.assertEqual(fiw.shadow_features(words), ["child_alive"])

    def test_shadow_features_do_not_misread_no_spinner(self):
        self.assertNotIn(
            "spinner", fiw.shadow_features("(no spinner, no tool child)  hidden screen")
        )

    def test_shadow_features_keep_wait_and_cpu_signals(self):
        words = "(wait marker, child using CPU: command)  hidden screen line"
        self.assertEqual(fiw.shadow_features(words), ["wait_marker", "child_cpu"])

    def test_shadow_features_no_evidence_has_safe_marker(self):
        self.assertEqual(
            fiw.shadow_features("(no status line on screen)  user text"),
            ["unclassified_evidence"],
        )


class RealertBackoff(unittest.TestCase):
    """A pane that stays idle is paged at once, then at doubling gaps up to the cap.
    Measured 2026-10-01: a fixed 600 s re-page sent pane 1 300 pages for 56 idle episodes."""

    def test_first_page_is_immediate(self):
        self.assertTrue(fiw.realert_due(1000.0, None, 0))

    def test_gap_doubles_after_each_page(self):
        base = fiw.REALERT
        self.assertFalse(fiw.realert_due(base - 1, 0.0, 1))
        self.assertTrue(fiw.realert_due(base, 0.0, 1))
        self.assertFalse(fiw.realert_due(2 * base - 1, 0.0, 2))
        self.assertTrue(fiw.realert_due(2 * base, 0.0, 2))

    def test_gap_is_capped(self):
        self.assertTrue(fiw.realert_due(float(fiw.REALERT_MAX), 0.0, 30))

    def test_six_hour_idle_episode_pages_far_less_than_fixed_cadence(self):
        pages, last, now = 0, None, 0.0
        while now <= 6 * 3600:
            if fiw.realert_due(now, last, pages):
                pages, last = pages + 1, now
            now += 60
        self.assertLessEqual(pages, 7)  # fixed 600 s cadence would page 37 times


class StaleIndexLock(unittest.TestCase):
    """The observed shape (four times on 2026-10-01): an empty .git/index.lock, no git holder."""

    def make_repo(self, size=0, age=600):
        root = Path(tempfile.mkdtemp())
        (root / ".git").mkdir()
        lock = root / ".git" / "index.lock"
        lock.write_bytes(b"x" * size)
        then = 1_790_000_000.0
        os.utime(lock, (then, then))
        return root, lock, then + age

    def test_stale_empty_lock_is_moved_not_deleted_and_paged_once(self):
        root, lock, now = self.make_repo()
        pages = []
        note = fiw.stale_lock_round(root, now, pages.append, live_git=lambda repo: [])
        self.assertFalse(lock.exists())
        parked = list((root / "var" / "agent-tmp").glob("git-index.lock.stale-*"))
        self.assertEqual(len(parked), 1)
        self.assertEqual(parked[0].stat().st_size, 0)
        self.assertEqual(len(pages), 1)
        self.assertIn("STALE LOCK moved", pages[0])
        self.assertIn("moved to", note)
        self.assertIsNone(
            fiw.stale_lock_round(root, now, pages.append, live_git=lambda repo: [])
        )
        self.assertEqual(len(pages), 1)

    def test_live_git_holder_leaves_lock_in_place(self):
        root, lock, now = self.make_repo()
        pages = []
        note = fiw.stale_lock_round(
            root, now, pages.append, live_git=lambda repo: [4242]
        )
        self.assertIsNone(note)
        self.assertTrue(lock.exists())
        self.assertEqual(pages, [])

    def test_young_lock_is_left_for_a_commit_still_running(self):
        root, lock, now = self.make_repo(age=fiw.LOCK_STALE_S - 1)
        self.assertIsNone(
            fiw.stale_lock_round(root, now, lambda m: None, live_git=lambda repo: [])
        )
        self.assertTrue(lock.exists())

    def test_non_empty_lock_is_a_real_index_write_and_is_left(self):
        root, lock, now = self.make_repo(size=128)
        self.assertIsNone(
            fiw.stale_lock_round(root, now, lambda m: None, live_git=lambda repo: [])
        )
        self.assertTrue(lock.exists())

    def test_failed_process_probe_is_not_run_and_leaves_lock(self):
        root, lock, now = self.make_repo()
        pages = []
        note = fiw.stale_lock_round(root, now, pages.append, live_git=lambda repo: None)
        self.assertIn("NOT_RUN", note)
        self.assertTrue(lock.exists())


class UnsubmittedComposer(unittest.TestCase):
    """A packet typed into a worker composer but never submitted (pane 4, 3x).

    Fixtures: pane4-unsubmitted-composer.screen (idle box shape from pane 3
    2026-10-01, real resend packet lines 1-5 inside); pane2-title-above-empty-box
    .screen (exact pane-2 capture 2026-10-01: transcript incl. the right-aligned
    session title between a stale ╭ and a bottom ╰; must read empty, 08:58Z fire).
    """

    SCREEN = (FIX / "pane4-unsubmitted-composer.screen").read_text()

    def test_composer_text_extracts_packet_from_box(self):
        text = fiw.composer_text(self.SCREEN)
        self.assertIn("THIS IS YOUR EXPLICIT NEW PACKET", text)
        self.assertIn("checkpoint a row per call", text)

    def test_empty_box_and_bare_prompt_read_empty(self):
        self.assertEqual(fiw.composer_text(PANE2_SCREEN), "")
        self.assertEqual(fiw.composer_text(PANE5_SCREEN), "")
        self.assertEqual(fiw.composer_text("╭── idle ──╮\n╰─   ─╯"), "")

    def test_right_aligned_title_above_dangling_close_reads_empty(self):
        # 08:58Z false fire on pane 2: transcript (incl. the right-aligned
        # session title, no borders) between a stale ╭ and a bottom ╰.
        screen = (
            Path(__file__).resolve().parent
            / "fixtures"
            / "pane2-title-above-empty-box.screen"
        ).read_text()
        self.assertEqual(fiw.composer_text(screen), "")

    def test_fixture_screen_classifies_idle(self):
        state, _ = fiw.classify(snapshot(4, self.SCREEN))
        self.assertEqual(state, "idle")

    def test_working_pane_never_submits(self):
        submit, same = fiw.unsubmitted_ready("working", 4, "some text", "", 5, set())
        self.assertFalse(submit)

    def test_first_sighting_arms_without_submitting(self):
        submit, same = fiw.unsubmitted_ready("idle", 4, "packet text", "", 0, set())
        self.assertFalse(submit)
        self.assertEqual(same, 1)

    def test_same_text_second_poll_submits_once(self):
        submit, same = fiw.unsubmitted_ready("idle", 4, "packet", "packet", 1, set())
        self.assertTrue(submit)
        self.assertEqual(same, 2)
        submit, _ = fiw.unsubmitted_ready(
            "idle", 4, "packet", "packet", 2, {(4, "packet")}
        )
        self.assertFalse(submit)

    def test_changed_text_resets_counter(self):
        submit, same = fiw.unsubmitted_ready(
            "idle", 4, "new text", "old text", 3, set()
        )
        self.assertFalse(submit)
        self.assertEqual(same, 1)

    def test_empty_composer_resets(self):
        submit, same = fiw.unsubmitted_ready("idle", 4, "", "old text", 3, set())
        self.assertFalse(submit)
        self.assertEqual(same, 0)

    def test_submit_enter_reports_tmux_truthfully(self):
        with mock.patch.object(fiw.subprocess, "run") as run:
            run.return_value.returncode = 0
            self.assertTrue(fiw.submit_enter(4))
            args = run.call_args[0][0]
            self.assertEqual(args[:3], ["tmux", "send-keys", "-t"])
            self.assertIn("Enter", args)
            run.return_value.returncode = 1
            self.assertFalse(fiw.submit_enter(4))
            run.side_effect = subprocess.TimeoutExpired("tmux", 10)
            self.assertFalse(fiw.submit_enter(4))


class FleetRouter(unittest.TestCase):
    """jev-ara9: who gets what when panes are idle. Beads are br --json shapes (ready is slim)."""

    AGENTS = {2: "HazySpring", 3: "CyanPeak", 4: "WildCarp"}
    EMPTY = {"pane": {}, "verify": {}}

    def ready(self, bid, prio, created="2026-10-02T10:00:00Z"):
        return {
            "id": bid,
            "priority": prio,
            "created_at": created,
            "updated_at": created,
            "issue_type": "task",
            "status": "open",
            "title": bid,
        }

    def verify(self, bid, author, updated="2026-10-02T10:00:00Z"):
        return {
            "id": bid,
            "assignee": author,
            "updated_at": updated,
            "status": "in_progress",
            "title": bid,
        }

    def test_verification_never_goes_to_its_author(self):
        plans = fiw.plan_routes(
            [(4, 1.0), (3, 2.0)],
            self.AGENTS,
            [],
            [self.verify("jev-v", "WildCarp")],
            self.EMPTY,
            100.0,
        )
        self.assertEqual(
            [(p, a, k) for p, a, k, _ in plans], [(3, "CyanPeak", "verify")]
        )

    def test_one_ready_bead_is_assigned_to_one_pane_only(self):
        plans = fiw.plan_routes(
            [(2, 1.0), (3, 2.0)],
            self.AGENTS,
            [self.ready("jev-a", 1)],
            [],
            self.EMPTY,
            100.0,
        )
        self.assertEqual([(p, b["id"]) for p, _, _, b in plans], [(2, "jev-a")])

    def test_priority_then_age_order_and_longest_idle_first(self):
        ready = [
            self.ready("jev-p2", 2),
            self.ready("jev-p1-new", 1, "2026-10-02T12:00:00Z"),
            self.ready("jev-p1-old", 1, "2026-10-02T09:00:00Z"),
        ]
        plans = fiw.plan_routes(
            [(3, 50.0), (2, 10.0)], self.AGENTS, ready, [], self.EMPTY, 100.0
        )
        self.assertEqual(
            [(p, b["id"]) for p, _, _, b in plans],
            [(2, "jev-p1-old"), (3, "jev-p1-new")],
        )

    def test_verification_beats_new_work_and_cooldown_holds_a_routed_pane(self):
        state = {"pane": {"3": ["jev-x", 90.0]}, "verify": {}}
        plans = fiw.plan_routes(
            [(2, 1.0), (3, 2.0)],
            self.AGENTS,
            [self.ready("jev-a", 0)],
            [self.verify("jev-v", "WildCarp")],
            state,
            100.0,
        )
        self.assertEqual([(p, k) for p, _, k, _ in plans], [(2, "verify")])

    def test_reroute_waits_and_never_repeats_the_same_verifier(self):
        bead = [self.verify("jev-v", "WildCarp")]
        state = {"pane": {}, "verify": {"jev-v": ["CyanPeak", 0.0]}}
        self.assertEqual(
            fiw.plan_routes([(2, 1.0)], self.AGENTS, [], bead, state, 10.0), []
        )
        late = fiw.VERIFY_REROUTE_S + 1.0
        self.assertEqual(
            fiw.plan_routes([(3, 1.0)], self.AGENTS, [], bead, state, late), []
        )
        self.assertEqual(
            len(fiw.plan_routes([(2, 1.0)], self.AGENTS, [], bead, state, late)), 1
        )

    def test_refused_claim_sends_nothing_and_switch_stops_all_br_calls(self):
        calls, sent = [], []
        ready = json.dumps([self.ready("jev-a", 1)])

        def run(argv, **_):
            calls.append(argv)
            out = ready if argv[1] == "ready" else "[]"
            rc = 6 if argv[1] == "update" else 0
            return subprocess.CompletedProcess(argv, rc, out, "")

        with (
            tempfile.TemporaryDirectory() as home,
            mock.patch.dict(os.environ, {"HOME": home}),
        ):
            state = Path(home) / ".local/state/jev"
            state.mkdir(parents=True)
            (state / "pane-agents.json").write_text(json.dumps({"2": "HazySpring"}))
            router = fiw.Router(
                run=run, send=lambda p, m: sent.append(p) or True, pager=lambda m: None
            )
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(router.round([(2, 1.0)], 100.0), set())
                self.assertEqual(sent, [])
                (state / "fleet-router.off").write_text("")
                calls.clear()
                self.assertEqual(router.round([(2, 1.0)], 100.0), set())
            self.assertEqual(calls, [])


class SteeringQueue(unittest.TestCase):
    """jev-of3b: an idle pane with a queued steering message gets one turn-starting nudge."""

    SCREEN = (FIX / "pane4-steering-queued.screen").read_text(encoding="utf-8")

    def test_real_queued_screen_reads_the_message(self):
        text = fiw.steering_text(self.SCREEN)
        self.assertTrue(text.startswith("CONDUCTOR (pane 1) to WildCarp"), text)

    def test_no_steering_marker_reads_empty(self):
        self.assertEqual(
            fiw.steering_text(self.SCREEN.replace("Steering · 1", "Thinking")), ""
        )

    def test_nudge_once_while_idle_never_while_working(self):
        text = fiw.steering_text(self.SCREEN)
        done = set()
        self.assertTrue(fiw.steering_due("idle", 4, text, done))
        self.assertFalse(fiw.steering_due("working", 4, text, done))
        done.add((4, text))
        self.assertFalse(fiw.steering_due("idle", 4, text, done))
        self.assertTrue(fiw.steering_due("idle", 4, text + " v2", done))


if __name__ == "__main__":
    unittest.main()
