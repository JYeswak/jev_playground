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
import plistlib
import subprocess
import sys
import tempfile
import time
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
            mock.patch.object(fiw, "_surface_heartbeat_round", return_value=0),
            mock.patch.object(fiw, "SHADOW_ONLY", False),
            mock.patch.object(fiw, "hook_load_round", return_value=None),
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
            mock.patch.object(fiw, "hook_load_round", return_value=None),
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

            def asker(text):
                calls.append(text)
                return {
                    "ok": True,
                    "score": 0.95,
                    "model": "jev-1.13.0",
                    "latencyMs": 100,
                }

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

    def test_mcp_and_language_servers_are_helpers(self):
        # captured from pane 5 (omp 84455) and panes 2/4/6 at 2026-10-05T16:12Z: after the math MCPs were
        # installed every pane carried these children, so every pane read 'working' and no idle alert
        # or steering nudge fired all afternoon
        servers = [
            "/opt/homebrew/bin/node /Users/josh/.local/share/infisical-mcp/0.0.24/node_modules/@infisical/mcp/dist/index.js",
            "/opt/homebrew/bin/uv tool uvx mcp-z3-prover",
            "/Users/josh/.cache/uv/archive-v0/xSMSnS2CCMWgCMtCiYSwX/bin/python /Users/josh/.cache/uv/archive-v0/xSMSnS2CCMWgCMtCiYSwX/bin/mcp-z3-prover",
            "/opt/homebrew/bin/uv run --no-project --with mcp[cli]<2 --with https://github.com/sdiehl/sympy-mcp/releases/download/0.1/sympy_mcp-0.1.0-py3-none-any.whl",
            "/Users/josh/.cache/uv/builds-v0/.tmpEFUYaf/bin/python -P -c import server; server.mcp.run()",
            "/opt/homebrew/bin/uv tool uvx --with sentence-transformers --with torch mathlas-mcp",
            "Python /Users/josh/Developer/formula-atlas/corpus/index/wolfram_llm_mcp.py",
            "node /opt/homebrew/bin/vscode-json-language-server --stdio",
            # second capture 16:15Z: pane 6's markdown language server, pane 5's zombie child
            "marksman server",
            "<defunct>",
        ]
        table = {10: (1, "-zsh"), 11: (10, "bun /x/bin/omp --auto-approve")}
        for n, command in enumerate(servers, start=20):
            table[n] = (11, command)
        self.assertEqual(fiw.omp_processes(table, 10), (11, []))
        state, evidence = fiw.classify(
            fiw.Snapshot(
                command="zsh",
                screen="",
                omp=True,
                tools=(),
                cpu_tools=(),
                session_age=300.0,
            )
        )
        self.assertEqual(state, "idle", evidence)

    def test_a_real_tool_call_beside_mcp_servers_is_still_a_tool(self):
        # planted negative: a bash tool call under the same omp must keep the pane 'working'
        table = {
            10: (1, "-zsh"),
            11: (10, "bun /x/bin/omp --auto-approve"),
            20: (
                11,
                "Python /Users/josh/Developer/formula-atlas/corpus/index/wolfram_llm_mcp.py",
            ),
            21: (
                11,
                "/bin/zsh -c nice -n 10 node --test work/vendor-paste/vendor-shadow.test.mjs",
            ),
        }
        self.assertEqual(
            fiw.omp_processes(table, 10)[1],
            [
                "/bin/zsh -c nice -n 10 node --test work/vendor-paste/vendor-shadow.test.mjs"
            ],
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


# Agent Mail's per-pane identity directory for this repo, observed 2026-10-04:
# ~/.config/agent-mail/identity/0427e59174bf/{56,18,26,27,32,29} held {"name":"BrownGoose"} etc.
REAL_REPO = Path("/Users/josh/Developer/jev")
REAL_PROJECT_DIR = "0427e59174bf"


def bind(root, bindings, project=None):
    """Write per-pane identity files {pane id without %: file text} under root."""
    folder = root / (project or fiw.agent_mail_project_dir(fiw.REPO_ROOT))
    folder.mkdir(parents=True, exist_ok=True)
    for pane, text in bindings.items():
        (folder / pane).write_text(text)


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

    def test_a_new_conductor_name_treats_its_backlog_as_history_but_pages_new_mail(
        self,
    ):
        # pane 1 restarted: the state was written for the previous owner of the conductor pane
        self.state.parent.mkdir(parents=True)
        self.state.write_text(
            json.dumps({"agent": "HazySpring", "paged": [], "history": []})
        )
        line = self.round()
        self.assertEqual(self.sent, [], line)
        saved = json.loads(self.state.read_text())
        self.assertEqual(saved["agent"], "AmberWillow")
        self.assertIn(42478, saved["history"])
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.0Z")
        mail(self.inbox, 42600, "high", now, "fresh after restart")
        self.round()
        self.assertEqual(len(self.sent), 1)
        self.assertIn("(id 42600,", self.sent[0])

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
            mock.patch.object(fiw, "_surface_heartbeat_round", return_value=0),
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
            mock.patch.object(fiw, "_surface_heartbeat_round", return_value=0),
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


class ConductorPaging(unittest.TestCase):
    """Conductor pages must not interrupt active pane-1 work (jev-06wt)."""

    def run_sender(self, screen):
        calls = []

        def run(argv, **_):
            calls.append(argv)
            if argv[:2] == ["tmux", "capture-pane"]:
                return subprocess.CompletedProcess(argv, 0, screen, "")
            return subprocess.CompletedProcess(argv, 0, "", "")

        return calls, run

    def test_busy_spinner_in_last_four_lines_queues_without_enter(self):
        screen = (
            "older line\nstatus\nprompt\n"
            "╭── ⠋ 1h > ◕ GPT-6-Luna > "
            "📁 ~/Developer/jev > ⑂ main *54 +18 ?855 > "
            "S0.68 ▶─────"
        )
        calls, run = self.run_sender(screen)
        with (
            mock.patch.object(fiw.surface_heartbeat, "DRY_RUN", False),
            mock.patch.object(fiw.subprocess, "run", side_effect=run),
            mock.patch.object(fiw, "PAGE_BUSY_LAST_SENT", None, create=True),
            mock.patch.object(fiw, "PAGE_BUSY_PENDING", [], create=True),
        ):
            self.assertTrue(fiw.send_pane1("alert text"))

        sends = [call for call in calls if call[:2] == ["tmux", "send-keys"]]
        self.assertEqual(
            sends[0][2:],
            ["-l", "-t", f"{fiw.SESSION}:0.1", "alert text"],
        )
        self.assertEqual(sends[1][2:], ["-t", f"{fiw.SESSION}:0.1", "C-q"])
        self.assertFalse(any(call[:2] == ["ntm", "send"] for call in calls))
        self.assertFalse(any("Enter" in call for call in calls))

    def test_spinner_above_last_four_lines_does_not_mark_pane_busy(self):
        screen = "⠋ old activity\none\ntwo\nthree\nprompt"
        calls, run = self.run_sender(screen)
        with (
            mock.patch.object(fiw.surface_heartbeat, "DRY_RUN", False),
            mock.patch.object(fiw.subprocess, "run", side_effect=run),
            mock.patch.object(fiw, "PAGE_BUSY_LAST_SENT", None, create=True),
            mock.patch.object(fiw, "PAGE_BUSY_PENDING", [], create=True),
        ):
            self.assertTrue(fiw.send_pane1("idle alert"))

        self.assertTrue(any(call[:2] == ["ntm", "send"] for call in calls))
        self.assertFalse(any(call[:2] == ["tmux", "send-keys"] for call in calls))

    def test_capture_failure_fails_closed_without_sending(self):
        calls = []

        def run(argv, **_):
            calls.append(argv)
            return subprocess.CompletedProcess(argv, 1, "", "pane unavailable")

        with (
            mock.patch.object(fiw.surface_heartbeat, "DRY_RUN", False),
            mock.patch.object(fiw.subprocess, "run", side_effect=run),
            mock.patch.object(fiw, "PAGE_BUSY_LAST_SENT", None, create=True),
            mock.patch.object(fiw, "PAGE_BUSY_PENDING", [], create=True),
        ):
            self.assertFalse(fiw.send_pane1("unverified pane"))

        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][:2], ["tmux", "capture-pane"])

    def test_failed_busy_queue_never_falls_back_to_ntm_send(self):
        calls = []

        def run(argv, **_):
            calls.append(argv)
            if argv[:2] == ["tmux", "capture-pane"]:
                return subprocess.CompletedProcess(argv, 0, "⠋ active", "")
            if argv[:2] == ["tmux", "send-keys"] and "-l" in argv:
                return subprocess.CompletedProcess(argv, 1, "", "send refused")
            return subprocess.CompletedProcess(argv, 0, "", "")

        with (
            mock.patch.object(fiw.surface_heartbeat, "DRY_RUN", False),
            mock.patch.object(fiw.subprocess, "run", side_effect=run),
            mock.patch.object(fiw, "PAGE_BUSY_LAST_SENT", None, create=True),
            mock.patch.object(fiw, "PAGE_BUSY_PENDING", [], create=True),
        ):
            self.assertFalse(fiw.send_pane1("busy alert"))

        self.assertFalse(any(call[:2] == ["ntm", "send"] for call in calls))
        self.assertFalse(
            any(call[:2] == ["tmux", "send-keys"] and "C-q" in call for call in calls)
        )

    def test_failed_busy_submit_is_not_retried_or_entered(self):
        calls = []

        def run(argv, **_):
            calls.append(argv)
            if argv[:2] == ["tmux", "capture-pane"]:
                return subprocess.CompletedProcess(argv, 0, "⠋ active", "")
            if argv[:2] == ["tmux", "send-keys"] and "C-q" in argv:
                return subprocess.CompletedProcess(argv, 1, "", "submit refused")
            return subprocess.CompletedProcess(argv, 0, "", "")

        with (
            mock.patch.object(fiw.surface_heartbeat, "DRY_RUN", False),
            mock.patch.object(fiw.subprocess, "run", side_effect=run),
            mock.patch.object(fiw, "PAGE_BUSY_LAST_SENT", 0.0, create=True),
            mock.patch.object(
                fiw, "PAGE_BUSY_PENDING", ["previous alert"], create=True
            ),
        ):
            self.assertFalse(fiw.flush_pending_page1(now=600.0))
            self.assertEqual(fiw.PAGE_BUSY_PENDING, [])
            self.assertFalse(fiw.flush_pending_page1(now=660.0))

        self.assertEqual(
            len(
                [
                    call
                    for call in calls
                    if call[:2] == ["tmux", "send-keys"] and "-l" in call
                ]
            ),
            1,
        )
        self.assertFalse(any(call[:2] == ["ntm", "send"] for call in calls))
        self.assertFalse(any("Enter" in call for call in calls))

    def test_failed_initial_busy_submit_discards_batch_without_enter(self):
        calls = []

        def run(argv, **_):
            calls.append(argv)
            if argv[:2] == ["tmux", "capture-pane"]:
                return subprocess.CompletedProcess(argv, 0, "⠋ active", "")
            if argv[:2] == ["tmux", "send-keys"] and "C-q" in argv:
                return subprocess.CompletedProcess(argv, 1, "", "submit refused")
            return subprocess.CompletedProcess(argv, 0, "", "")

        with (
            mock.patch.object(fiw.surface_heartbeat, "DRY_RUN", False),
            mock.patch.object(fiw.subprocess, "run", side_effect=run),
            mock.patch.object(fiw.time, "monotonic", return_value=600.0),
            mock.patch.object(fiw, "PAGE_BUSY_LAST_SENT", None, create=True),
            mock.patch.object(
                fiw, "PAGE_BUSY_PENDING", ["buffered alert"], create=True
            ),
        ):
            self.assertFalse(fiw.send_pane1("new alert"))
            self.assertEqual(fiw.PAGE_BUSY_PENDING, [])

        self.assertFalse(any(call[:2] == ["ntm", "send"] for call in calls))
        self.assertFalse(any("Enter" in call for call in calls))

    def test_busy_pages_coalesce_and_flush_no_more_than_once_per_ten_minutes(self):
        screen = "status\nprompt\n⠋ working"
        calls, run = self.run_sender(screen)
        with (
            mock.patch.object(fiw.surface_heartbeat, "DRY_RUN", False),
            mock.patch.object(fiw.subprocess, "run", side_effect=run),
            mock.patch.object(fiw.time, "monotonic", side_effect=[0.0, 30.0, 60.0]),
            mock.patch.object(fiw, "PAGE_BUSY_LAST_SENT", None, create=True),
            mock.patch.object(fiw, "PAGE_BUSY_PENDING", [], create=True),
        ):
            self.assertTrue(fiw.send_pane1("first alert"))
            self.assertTrue(fiw.send_pane1("second alert"))
            self.assertTrue(fiw.send_pane1("third alert"))
            queued_before_window = [
                call
                for call in calls
                if call[:2] == ["tmux", "send-keys"] and "-l" in call
            ]
            self.assertEqual(len(queued_before_window), 1)
            self.assertFalse(fiw.flush_pending_page1(now=599.9))
            self.assertTrue(fiw.flush_pending_page1(now=600.0))

        queued = [
            call for call in calls if call[:2] == ["tmux", "send-keys"] and "-l" in call
        ]
        self.assertEqual(len(queued), 2)
        self.assertEqual(queued[1][-1], "second alert; third alert")

    def test_buffered_batch_uses_idle_send_after_spinner_clears(self):
        screens = iter(["⠋ active", "⠋ active", "idle prompt"])
        calls = []

        def run(argv, **_):
            calls.append(argv)
            screen = next(screens) if argv[:2] == ["tmux", "capture-pane"] else ""
            return subprocess.CompletedProcess(argv, 0, screen, "")

        with (
            mock.patch.object(fiw.surface_heartbeat, "DRY_RUN", False),
            mock.patch.object(fiw.subprocess, "run", side_effect=run),
            mock.patch.object(fiw.time, "monotonic", side_effect=[0.0, 30.0]),
            mock.patch.object(fiw, "PAGE_BUSY_LAST_SENT", None, create=True),
            mock.patch.object(fiw, "PAGE_BUSY_PENDING", [], create=True),
        ):
            self.assertTrue(fiw.send_pane1("first alert"))
            self.assertTrue(fiw.send_pane1("deferred alert"))
            self.assertTrue(fiw.flush_pending_page1(now=600.0))

        idle_sends = [call for call in calls if call[:2] == ["ntm", "send"]]
        self.assertEqual(idle_sends[0][-1], "deferred alert")
        self.assertEqual(
            len(
                [
                    call
                    for call in calls
                    if call[:2] == ["tmux", "send-keys"] and "-l" in call
                ]
            ),
            1,
        )
        self.assertEqual(
            len(
                [
                    call
                    for call in calls
                    if call[:2] == ["tmux", "send-keys"] and "-l" in call
                ]
            ),
            1,
        )
        self.assertFalse(any("Enter" in call for call in calls))


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
            if argv[0] == "tmux":
                return subprocess.CompletedProcess(argv, 0, "1 %56\n2 %18\n", "")
            out = ready if argv[1] == "ready" else "[]"
            rc = 6 if argv[1] == "update" else 0
            return subprocess.CompletedProcess(argv, rc, out, "")

        with (
            tempfile.TemporaryDirectory() as home,
            mock.patch.dict(
                os.environ,
                {"HOME": home, "JEV_WATCH_IDENTITY_ROOT": f"{home}/identity"},
            ),
        ):
            state = Path(home) / ".local/state/jev"
            state.mkdir(parents=True)
            bind(Path(home) / "identity", {"18": '{"name":"HazySpring"}'})
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


class PaneAgents(unittest.TestCase):
    """The watcher resolves names from tmux pane ids, so a pane restart is followed, not pinned."""

    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="fiw-identity-"))
        self.env = mock.patch.dict(
            os.environ, {"JEV_WATCH_IDENTITY_ROOT": str(self.root)}
        )
        self.env.start()
        self.addCleanup(self.env.stop)
        repo = mock.patch.object(fiw, "REPO_ROOT", REAL_REPO)
        repo.start()
        self.addCleanup(repo.stop)

    @staticmethod
    def tmux(rows):
        return lambda argv, **_: subprocess.CompletedProcess(argv, 0, rows, "")

    def test_names_follow_the_pane_id_across_a_restart(self):
        bind(
            self.root,
            {
                "56": '{"name":"BrownGoose"}',
                "18": '{"name":"HazySpring"}',
                "26": "CyanPeak\n",
            },
            project=REAL_PROJECT_DIR,
        )
        run = self.tmux("1 %56\n2 %18\n3 %26\n4 %27\n")
        self.assertEqual(
            fiw.pane_agents(run), {1: "BrownGoose", 2: "HazySpring", 3: "CyanPeak"}
        )
        # pane %18 restarted and its new session registered under a new name
        bind(self.root, {"18": '{"name":"AmberWillow"}'}, project=REAL_PROJECT_DIR)
        self.assertEqual(fiw.pane_agents(run)[2], "AmberWillow")

    def test_unreachable_tmux_yields_no_agents_so_the_router_stays_off(self):
        bind(self.root, {"18": '{"name":"AmberWillow"}'}, project=REAL_PROJECT_DIR)

        def down(argv, **_):
            raise subprocess.TimeoutExpired(argv, 10)

        self.assertEqual(fiw.pane_agents(down), {})


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

    def test_steering_marker_rejects_embedded_prefix(self):
        screen = self.SCREEN.replace("Steering · 1", "xSteering · 1", 1)
        self.assertEqual(fiw.steering_text(screen), "")

    def test_steering_marker_long_near_miss_completes_within_bound(self):
        screen = "Steering · " + "9" * 100_000 + " " * 100_000 + "x"
        started = time.perf_counter()

        self.assertEqual(fiw.steering_text(screen), "")
        self.assertLess(time.perf_counter() - started, 1.0)

    def test_nudge_once_while_idle_never_while_working(self):
        text = fiw.steering_text(self.SCREEN)
        done = set()
        self.assertTrue(fiw.steering_due("idle", 4, text, "", done))
        self.assertFalse(fiw.steering_due("working", 4, text, "", done))
        self.assertFalse(fiw.steering_due("unknown", 4, text, "", done))
        self.assertFalse(fiw.steering_due("idle", 4, text, "composer", done))
        done.add((4, text))
        self.assertFalse(fiw.steering_due("idle", 4, text, "", done))
        self.assertTrue(fiw.steering_due("idle", 4, text + " v2", "", done))

    def test_nudge_sends_literal_dot_and_enter_only_after_fresh_safe_snapshot(self):
        text = fiw.steering_text(self.SCREEN)
        calls = []

        def completed(argv, **kwargs):
            calls.append(argv)
            return subprocess.CompletedProcess(argv, 0, stdout="", stderr="")

        fresh = {4: ("idle", "", "", True, "", text)}
        with (
            mock.patch.object(fiw, "poll", return_value=fresh) as check,
            mock.patch.object(fiw.subprocess, "run", side_effect=completed),
        ):
            self.assertTrue(
                fiw.nudge_steering(
                    4, state="idle", composer="", queued_steer=text
                )
            )

        check.assert_called_once_with()
        self.assertEqual(
            calls,
            [
                ["tmux", "send-keys", "-l", "-t", "jev:0.4", "."],
                ["tmux", "send-keys", "-t", "jev:0.4", "Enter"],
            ],
        )

    def test_nudge_refuses_working_unknown_composed_or_empty_queue(self):
        cases = (
            ("working", "", "queued"),
            ("unknown", "", "queued"),
            ("idle", "composer", "queued"),
            ("idle", "", ""),
        )
        for state, composer, queued_steer in cases:
            with self.subTest(state=state, composer=composer, steer=queued_steer):
                with (
                    mock.patch.object(fiw, "poll") as check,
                    mock.patch.object(fiw.subprocess, "run") as run,
                ):
                    self.assertFalse(
                        fiw.nudge_steering(
                            4,
                            state=state,
                            composer=composer,
                            queued_steer=queued_steer,
                        )
                    )
                check.assert_not_called()
                run.assert_not_called()

    def test_nudge_refuses_if_fresh_snapshot_is_unsafe_or_missing(self):
        text = fiw.steering_text(self.SCREEN)
        unsafe = (
            None,
            {},
            {4: ("idle",)},
            {4: ("working", "", "", True, "", text)},
            {4: ("unknown", "", "", True, "", text)},
            {4: ("idle", "", "", True, "composer", text)},
            {4: ("idle", "", "", True, "", "different queued message")},
        )
        for fresh in unsafe:
            with self.subTest(snapshot=fresh):
                with (
                    mock.patch.object(fiw, "poll", return_value=fresh) as check,
                    mock.patch.object(fiw.subprocess, "run") as run,
                ):
                    self.assertFalse(
                        fiw.nudge_steering(
                            4, state="idle", composer="", queued_steer=text
                        )
                    )
                check.assert_called_once_with()
                run.assert_not_called()


class SurfaceHeartbeat(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="surface-heartbeat-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "home"
        self.state_dir = self.root / "state"
        self.omp_root = self.root / "omp"
        self.session_file = (
            self.omp_root / "agent/sessions/-Developer-jev/session.jsonl"
        )
        self.session_file.parent.mkdir(parents=True)
        self.registry = self.root / "surfaces.json"
        self.telemetry_path = self.root / "telemetry.jsonl"
        self.switch = self.root / "surface.off"
        self.heartbeat = fiw.surface_heartbeat
        self.heartbeat.DRY_RUN = False
        self.heartbeat.DRY_RUN_SENDS.clear()
        self.current_end = (
            int(fiw.time.time() // self.heartbeat.HOUR) * self.heartbeat.HOUR
        )
        self.current_start = self.current_end - self.heartbeat.HOUR
        self.now = self.current_end + 1
        self.history_start = self.current_start - self.heartbeat.HISTORY_SECONDS

    def write_registry(self, polarity="presence-OFF", *, owner="jev-test"):
        entry = {
            "id": "test-surface",
            "owner": owner,
            "heartbeat": {
                "source": "jsonl",
                "eligible_event": "tool_result",
                "path": str(self.telemetry_path),
                "status_field": "status",
                "error_rate_ceiling": 0.25,
                "minimum_error_rows": 3,
            },
            "off_switch": None
            if polarity is None
            else {"path": str(self.switch), "polarity": polarity},
        }
        self.registry.write_text(
            json.dumps(
                {"schema_version": "blast-radius-surfaces.v1", "surfaces": [entry]}
            ),
            encoding="utf-8",
        )
        if polarity == "presence-ON":
            self.switch.write_text("enabled\n", encoding="utf-8")
        else:
            self.switch.unlink(missing_ok=True)
        return self.heartbeat.load_registry(self.registry)[0]

    def write_inputs(
        self, current_events=3, statuses=(), *, stale=False, invalid=False
    ):
        session_rows = []
        telemetry_rows = []
        for index in range(27):
            stamp = self.history_start + index * self.heartbeat.HOUR + 60
            session_rows.append(
                {
                    "type": "message",
                    "timestamp": stamp,
                    "message": {"role": "toolResult"},
                }
            )
            telemetry_rows.append({"ts": stamp, "status": "ok"})
        for index in range(current_events):
            stamp = self.current_start + 60 + index * 10
            session_rows.append(
                {
                    "type": "message",
                    "timestamp": stamp,
                    "message": {"role": "toolResult"},
                }
            )
        for index, status in enumerate(statuses):
            stamp = self.current_start + 60 + index * 10
            telemetry_rows.append({"ts": stamp, "status": status})
        if stale:
            telemetry_rows.append({"ts": self.current_start - 7200, "status": "ok"})
        lines = [json.dumps(row) for row in telemetry_rows]
        if invalid:
            lines.append(json.dumps({"ts": self.current_start + 5, "status": 7}))
        self.session_file.write_text(
            "\n".join(json.dumps(row) for row in session_rows) + "\n", encoding="utf-8"
        )
        self.telemetry_path.parent.mkdir(parents=True, exist_ok=True)
        self.telemetry_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def monitor(self, *, now=None, observe_only=False):
        messages = []
        kwargs = {"observe_only": True} if observe_only else {}
        result = self.heartbeat.monitor(
            self.registry,
            self.state_dir,
            now=self.now if now is None else now,
            omp_root=self.omp_root,
            send=messages.append,
            **kwargs,
        )
        return result[0], messages

    def test_watcher_observe_only_and_shadow_only_reach_monitor(self):
        cases = ((True, False, True), (False, True, True), (False, False, False))
        for surface_only, shadow_only, expected in cases:
            with self.subTest(surface_only=surface_only, shadow_only=shadow_only):
                monitor = mock.Mock(return_value=[])
                patches = (
                    mock.patch.object(
                        fiw, "SURFACE_OBSERVE_ONLY", surface_only, create=True
                    ),
                    mock.patch.object(fiw, "SHADOW_ONLY", shadow_only),
                    mock.patch.object(
                        fiw.surface_heartbeat,
                        "resolve_state_dir",
                        return_value=self.state_dir,
                    ),
                    mock.patch.object(
                        fiw.surface_heartbeat,
                        "real_omp_root",
                        return_value=self.omp_root,
                    ),
                    mock.patch.object(
                        fiw.surface_heartbeat, "monitor", monitor
                    ),
                )
                with contextlib.ExitStack() as stack:
                    for patcher in patches:
                        stack.enter_context(patcher)
                    with contextlib.redirect_stdout(io.StringIO()):
                        self.assertEqual(
                            fiw._surface_heartbeat_round(self.now), 0
                        )
                self.assertIs(monitor.call_args.kwargs["observe_only"], expected)

    def test_webscreen_counts_only_external_web_tool_results(self):
        self.write_registry()
        entry = json.loads(self.registry.read_text(encoding="utf-8"))["surfaces"][0]
        entry["id"] = "webscreen-global"
        entry["heartbeat"].update(
            {
                "eligible_tool_names": ["web_search", "web_extract"],
                "exclude_cwd_roots": ["/Users/josh/Developer/jev"],
            }
        )
        self.registry.write_text(
            json.dumps({"schema_version": "blast-radius-surfaces.v1", "surfaces": [entry]}),
            encoding="utf-8",
        )
        surface = self.heartbeat.load_registry(self.registry)[0]
        inside = [
            {"type": "session", "cwd": "/Users/josh/Developer/jev"},
            {
                "type": "message",
                "timestamp": self.current_start + 60,
                "message": {"role": "toolResult", "toolName": "web_search"},
            },
        ]
        outside = [
            {"type": "session", "cwd": "/Users/josh/Developer/other"},
            {
                "type": "message",
                "timestamp": self.current_start + 70,
                "message": {"role": "toolResult", "toolName": "eval"},
            },
            {
                "type": "message",
                "timestamp": self.current_start + 75,
                "message": {
                    "role": "toolResult",
                    "toolName": "web_search",
                    "isError": True,
                },
            },
            {
                "type": "message",
                "timestamp": self.current_start + 80,
                "message": {"role": "toolResult", "toolName": "web_extract"},
            },
        ]
        self.session_file.write_text(
            "\n".join(json.dumps(row) for row in inside) + "\n", encoding="utf-8"
        )
        external = self.session_file.parent / "external" / "session.jsonl"
        external.parent.mkdir(parents=True)
        external.write_text(
            "\n".join(json.dumps(row) for row in outside) + "\n", encoding="utf-8"
        )

        host_events, _, _ = self.heartbeat.scan_omp_sessions(
            self.omp_root,
            self.history_start,
            self.now,
            set(),
            [surface],
        )

        self.assertEqual(host_events[surface.id], [self.current_start + 80])

    def test_webscreen_paused_status_is_not_classified_as_silence(self):
        self.write_registry(polarity="presence-ON")
        entry = json.loads(self.registry.read_text(encoding="utf-8"))["surfaces"][0]
        entry["id"] = "webscreen-global"
        entry["heartbeat"]["paused_statuses"] = ["fail_open", "paused", "local-only"]
        self.registry.write_text(
            json.dumps({"schema_version": "blast-radius-surfaces.v1", "surfaces": [entry]}),
            encoding="utf-8",
        )
        self.write_inputs(statuses=[])
        with self.telemetry_path.open("a", encoding="utf-8") as handle:
            handle.write(
                json.dumps(
                    {
                        "ts": self.current_start + 10,
                        "status": "fail_open",
                        "reason": None,
                    }
                )
                + "\n"
            )

        assessment, messages = self.monitor()

        self.assertEqual(assessment.state, "paused")
        self.assertFalse(assessment.unhealthy)
        self.assertEqual(messages, [])
        self.assertTrue(self.switch.exists())

    def test_surface_without_telemetry_is_unmeasurable_not_silent(self):
        self.registry.write_text(
            json.dumps(
                {
                    "schema_version": "blast-radius-surfaces.v1",
                    "surfaces": [
                        {
                            "id": "harm-rule",
                            "owner": "jev-w2mf",
                            "telemetry": "none",
                            "off_switch": None,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        self.write_inputs(statuses=[])

        assessment, messages = self.monitor()

        self.assertEqual(assessment.state, "unmeasurable")
        self.assertFalse(assessment.unhealthy)
        self.assertEqual(messages, [])

    def test_silent_surface_pages_reason_and_turns_off_presence_off_switch(self):
        self.write_registry()
        self.write_inputs(statuses=[])

        assessment, messages = self.monitor()

        self.assertEqual(assessment.state, "silent")
        self.assertTrue(self.switch.is_file())
        self.assertIn("no current telemetry rows", self.switch.read_text())
        self.assertEqual(len(messages), 1)
        self.assertIn("test-surface", messages[0])
        self.assertIn("owner=jev-test", messages[0])
        self.assertIn("no current telemetry rows", messages[0])

    def test_session_error_spike_turns_off_presence_on_switch(self):
        custom_type = "test.surface.decision.v1"
        self.registry.write_text(
            json.dumps(
                {
                    "schema_version": "blast-radius-surfaces.v1",
                    "surfaces": [
                        {
                            "id": "test-surface",
                            "owner": "jev-test",
                            "heartbeat": {
                                "source": "omp_session",
                                "eligible_event": "tool_call",
                                "eligible_tool_names": ["bash"],
                                "custom_types": [custom_type],
                                "error_rate_ceiling": 0.25,
                                "minimum_error_rows": 3,
                            },
                            "off_switch": {
                                "path": str(self.switch),
                                "polarity": "presence-ON",
                            },
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        self.switch.write_text("enabled\n", encoding="utf-8")
        session_rows = []
        for index in range(27):
            stamp = self.history_start + index * self.heartbeat.HOUR + 60
            session_rows.extend(
                [
                    {
                        "type": "custom",
                        "customType": "tool_execution_start",
                        "timestamp": stamp,
                        "data": {"toolName": "bash"},
                    },
                    {
                        "type": "custom",
                        "customType": custom_type,
                        "timestamp": stamp,
                        "data": {"error": None},
                    },
                ]
            )
        for index in range(3):
            stamp = self.current_start + 60 + index * 10
            session_rows.extend(
                [
                    {
                        "type": "custom",
                        "customType": "tool_execution_start",
                        "timestamp": stamp,
                        "data": {"toolName": "bash"},
                    },
                    {
                        "type": "custom",
                        "customType": "tool_execution_start",
                        "timestamp": stamp,
                        "data": {"toolName": "web_search"},
                    },
                    {
                        "type": "custom",
                        "customType": custom_type,
                        "timestamp": stamp,
                        "data": {"error": "asker-failed"},
                    },
                ]
            )
        self.session_file.write_text(
            "\n".join(json.dumps(row) for row in session_rows) + "\n",
            encoding="utf-8",
        )

        assessment, messages = self.monitor()

        self.assertEqual(assessment.state, "error-rate")
        self.assertEqual(
            (assessment.host_events, assessment.rows, assessment.errors), (3, 3, 3)
        )
        self.assertFalse(self.switch.exists())
        self.assertEqual(len(messages), 1)
        self.assertIn("3/3 telemetry rows errored", messages[0])

    def test_error_spike_pages_reason_and_removes_presence_on_switch(self):
        self.write_registry("presence-ON")
        self.write_inputs(statuses=["error"] * 3)

        assessment, messages = self.monitor()

        self.assertEqual(assessment.state, "error-rate")
        self.assertFalse(self.switch.exists())
        self.assertEqual(len(messages), 1)
        self.assertIn("owner=jev-test", messages[0])
        self.assertIn("3/3 telemetry rows errored", messages[0])
        state = self.heartbeat.load_state(self.state_dir)
        self.assertTrue(state["surfaces"]["test-surface"]["auto_off"])
        self.assertIn(
            "3/3 telemetry rows errored", state["surfaces"]["test-surface"]["reason"]
        )

    def test_auto_off_is_scoped_to_failed_surface(self):
        self.write_registry()
        data = json.loads(self.registry.read_text(encoding="utf-8"))
        other_log = self.root / "other-telemetry.jsonl"
        other_switch = self.root / "other-surface.on"
        other = {
            "id": "other-surface",
            "owner": "jev-other",
            "heartbeat": {
                "source": "jsonl",
                "eligible_event": "tool_result",
                "path": str(other_log),
                "status_field": "status",
                "error_rate_ceiling": 0.25,
                "minimum_error_rows": 3,
            },
            "off_switch": {"path": str(other_switch), "polarity": "presence-ON"},
        }
        data["surfaces"].append(other)
        self.registry.write_text(json.dumps(data), encoding="utf-8")
        other_switch.write_text("enabled\n", encoding="utf-8")
        self.write_inputs(statuses=[])
        other_rows = [
            {
                "ts": self.history_start + index * self.heartbeat.HOUR + 60,
                "status": "ok",
            }
            for index in range(27)
        ]
        other_rows.extend(
            {"ts": self.current_start + 60 + index * 10, "status": "ok"}
            for index in range(3)
        )
        other_log.write_text(
            "\n".join(json.dumps(row) for row in other_rows) + "\n", encoding="utf-8"
        )

        messages = []
        assessments = self.heartbeat.monitor(
            self.registry,
            self.state_dir,
            now=self.now,
            omp_root=self.omp_root,
            send=messages.append,
        )

        by_id = {assessment.surface_id: assessment for assessment in assessments}
        self.assertEqual(by_id["test-surface"].state, "silent")
        self.assertEqual(by_id["other-surface"].state, "healthy")
        self.assertTrue(self.switch.is_file())
        self.assertTrue(other_switch.is_file())
        self.assertEqual(len(messages), 1)
        self.assertIn("test-surface", messages[0])

    def test_healthy_rows_inside_seven_day_ci_leave_surface_on(self):
        self.write_registry()
        self.write_inputs(statuses=["ok"] * 3)

        assessment, messages = self.monitor()

        self.assertEqual(assessment.state, "healthy")
        self.assertEqual(assessment.interval.lower, 1.0)
        self.assertEqual(assessment.interval.upper, 1.0)
        self.assertFalse(self.switch.exists())
        self.assertEqual(messages, [])

    def test_zero_host_traffic_for_three_hours_does_not_trip_switch(self):
        self.write_registry("presence-ON")
        self.write_inputs(current_events=0, statuses=[])

        messages = []
        for offset in (0, self.heartbeat.HOUR, 2 * self.heartbeat.HOUR):
            assessments = self.heartbeat.monitor(
                self.registry,
                self.state_dir,
                now=self.now + offset,
                omp_root=self.omp_root,
                send=messages.append,
            )
            self.assertEqual(assessments[0].state, "idle")

        self.assertTrue(self.switch.is_file())
        self.assertEqual(messages, [])

    def test_stale_rows_cannot_make_surface_healthy(self):
        self.write_registry()
        self.write_inputs(statuses=[], stale=True)

        assessment, messages = self.monitor()

        self.assertNotEqual(assessment.state, "healthy")
        self.assertTrue(assessment.unhealthy)
        self.assertTrue(self.switch.is_file())
        self.assertEqual(assessment.rows, 0)
        self.assertEqual(len(messages), 1)

    def test_invalid_row_makes_otherwise_healthy_telemetry_unhealthy(self):
        self.write_registry()
        self.write_inputs(statuses=["ok"] * 3, invalid=True)

        assessment, messages = self.monitor()

        self.assertEqual(assessment.state, "invalid-telemetry")
        self.assertTrue(assessment.unhealthy)
        self.assertTrue(self.switch.is_file())
        self.assertIn("invalid telemetry", assessment.reason)
        self.assertEqual(len(messages), 1)

    def test_surface_without_switch_alerts_but_is_never_reported_switched_off(self):
        self.write_registry(None)
        self.write_inputs(statuses=[])

        assessment, messages = self.monitor()
        state = self.heartbeat.load_state(self.state_dir)

        self.assertEqual(assessment.state, "silent")
        self.assertEqual(len(messages), 1)
        self.assertFalse(state["surfaces"]["test-surface"]["auto_off"])
        self.assertFalse(self.switch.exists())

    def test_off_surface_never_restores_without_probe(self):
        self.write_registry()
        self.switch.write_text("manual off\n", encoding="utf-8")
        self.write_inputs(statuses=["ok"] * 3)

        self.monitor()

        self.assertTrue(self.switch.is_file())

    def test_healthy_log_only_probe_restores_once_and_stays_on(self):
        surface = self.write_registry()
        self.write_inputs(statuses=[])
        self.monitor()
        self.assertTrue(self.switch.is_file())
        self.assertTrue(
            self.heartbeat.load_state(self.state_dir)["surfaces"]["test-surface"]["auto_off"]
        )
        self.write_inputs(statuses=["ok"] * 3)
        self.heartbeat.start_restore_probe(
            surface,
            self.state_dir,
            now=self.current_start,
            duration_seconds=self.heartbeat.HOUR,
        )

        _, first_messages = self.monitor()
        state = self.heartbeat.load_state(self.state_dir)
        self.assertFalse(self.switch.exists())
        self.assertEqual(state["probes"]["test-surface"]["status"], "restored")
        self.assertTrue(
            any("SURFACE RESTORED test-surface" in item for item in first_messages)
        )

        _, later_messages = self.monitor(now=self.now + self.heartbeat.HOUR)
        self.assertFalse(self.switch.exists())
        self.assertFalse(
            any("SURFACE RESTORE BLOCKED" in item for item in later_messages)
        )

    def test_failed_log_only_probe_keeps_surface_off(self):
        surface = self.write_registry()
        self.switch.write_text("manual off\n", encoding="utf-8")
        self.write_inputs(statuses=[])
        self.heartbeat.start_restore_probe(
            surface,
            self.state_dir,
            now=self.current_start,
            duration_seconds=self.heartbeat.HOUR,
        )

        _, messages = self.monitor()

        state = self.heartbeat.load_state(self.state_dir)
        self.assertTrue(self.switch.is_file())
        self.assertEqual(state["probes"]["test-surface"]["status"], "failed")
        self.assertTrue(
            any("SURFACE RESTORE BLOCKED test-surface" in item for item in messages)
        )

    def test_operator_off_marker_beats_healthy_restore_probe(self):
        self.write_registry("presence-ON")
        self.write_inputs(statuses=[])
        self.monitor()
        self.assertFalse(self.switch.exists())
        entry = json.loads(self.registry.read_text(encoding="utf-8"))["surfaces"][0]
        marker = self.root / "operator-off"
        entry["operator_off_marker"] = str(marker)
        self.registry.write_text(
            json.dumps({"schema_version": "blast-radius-surfaces.v1", "surfaces": [entry]}),
            encoding="utf-8",
        )
        surface = self.heartbeat.load_registry(self.registry)[0]
        marker.write_text("operator requested OFF\n", encoding="utf-8")
        self.write_inputs(statuses=["ok"] * 3)
        self.heartbeat.start_restore_probe(
            surface,
            self.state_dir,
            now=self.current_start,
            duration_seconds=self.heartbeat.HOUR,
        )

        _, messages = self.monitor()
        state = self.heartbeat.load_state(self.state_dir)

        self.assertFalse(self.switch.exists())
        self.assertEqual(state["probes"]["test-surface"]["status"], "failed")
        self.assertIn("operator OFF marker is present", state["probes"]["test-surface"]["reason"])
        self.assertTrue(
            any("SURFACE RESTORE BLOCKED test-surface" in item for item in messages)
        )

    def test_observe_only_alerts_on_unhealthy_surface_without_switching(self):
        self.write_registry("presence-ON")
        self.write_inputs(statuses=["error"] * 3)

        assessment, messages = self.monitor(observe_only=True)
        state = self.heartbeat.load_state(self.state_dir)
        record = state["surfaces"]["test-surface"]
        events = [
            json.loads(line)
            for line in (self.state_dir / self.heartbeat.EVENTS_NAME)
            .read_text(encoding="utf-8")
            .splitlines()
        ]

        self.assertEqual(assessment.state, "error-rate")
        self.assertTrue(assessment.unhealthy)
        self.assertTrue(any("SURFACE ANOMALY test-surface" in item for item in messages))
        self.assertTrue(self.switch.is_file())
        self.assertEqual(self.switch.read_text(encoding="utf-8"), "enabled\n")
        self.assertFalse(record.get("auto_off", False))
        self.assertEqual(events[-1]["action"], "alert")

    def test_observe_only_preserves_expired_restore_probe_and_operator_markers(self):
        self.write_registry("presence-OFF")
        entry = json.loads(self.registry.read_text(encoding="utf-8"))["surfaces"][0]
        operator_marker = self.root / "operator-off"
        entry["operator_off_marker"] = str(operator_marker)
        self.registry.write_text(
            json.dumps({"schema_version": "blast-radius-surfaces.v1", "surfaces": [entry]}),
            encoding="utf-8",
        )
        surface = self.heartbeat.load_registry(self.registry)[0]
        self.switch.write_text(
            "fleet heartbeat auto-off: prior error rate\n", encoding="utf-8"
        )
        operator_marker.write_text("operator requested OFF\n", encoding="utf-8")
        self.write_inputs(statuses=["ok"] * 3)
        self.heartbeat.save_state(
            self.state_dir,
            {
                "schema_version": "fleet-surface-heartbeat-state.v1",
                "surfaces": {
                    "test-surface": {"state": "error-rate", "auto_off": True}
                },
                "probes": {},
            },
        )
        self.heartbeat.start_restore_probe(
            surface,
            self.state_dir,
            now=self.current_start,
            duration_seconds=self.heartbeat.HOUR,
        )
        probe_before = self.heartbeat.load_state(self.state_dir)["probes"][
            "test-surface"
        ].copy()
        switch_before = self.switch.read_bytes()
        operator_before = operator_marker.read_bytes()

        assessment, messages = self.monitor(observe_only=True)
        state = self.heartbeat.load_state(self.state_dir)

        self.assertEqual(assessment.state, "healthy")
        self.assertEqual(messages, [])
        self.assertEqual(state["probes"]["test-surface"], probe_before)
        self.assertTrue(state["surfaces"]["test-surface"]["auto_off"])
        self.assertEqual(self.switch.read_bytes(), switch_before)
        self.assertEqual(operator_marker.read_bytes(), operator_before)

    def test_dry_run_refuses_unisolated_home_before_any_write(self):
        self.write_registry()
        self.write_inputs(statuses=["error"] * 3)

        with mock.patch.object(self.heartbeat, "DRY_RUN", True):
            with self.assertRaises(self.heartbeat.HeartbeatError):
                self.monitor()

        self.assertFalse(self.state_dir.exists())
        self.assertEqual(self.heartbeat.DRY_RUN_SENDS, [])

    def test_dry_run_records_pager_without_running_ntm_and_writes_liveness(self):
        self.home.mkdir()
        self.state_dir = self.home / ".local/state/jev"
        self.telemetry_path = self.state_dir / "webscreen-shadow.jsonl"
        self.switch = self.state_dir / "test-surface.off"
        self.write_registry()
        self.write_inputs(statuses=[])
        no_send = mock.Mock(side_effect=AssertionError("dry-run invoked a subprocess"))
        output = io.StringIO()
        patches = (
            mock.patch.dict(
                os.environ,
                {
                    "HOME": str(self.home),
                    "TMPDIR": str(self.root),
                    "JEV_FLEET_STATE_DIR": str(self.state_dir),
                    "JEV_OMP_ROOT": str(self.omp_root),
                },
            ),
            mock.patch.object(fiw, "SURFACE_REGISTRY", self.registry),
            mock.patch.object(fiw, "poll", return_value={}),
            mock.patch.object(fiw, "submit_shadow"),
            mock.patch.object(fiw, "ci_lines", return_value=[]),
            mock.patch.object(fiw, "stranger_round", return_value=None),
            mock.patch.object(fiw, "judge_lines", return_value=[]),
            mock.patch.object(fiw, "key_round", return_value=None),
            mock.patch.object(fiw, "inbox_paths", return_value=(self.root, self.root)),
            mock.patch.object(fiw, "inbox_round", return_value="no mail"),
            mock.patch.object(fiw, "stale_lock_round", return_value=None),
            mock.patch.object(fiw, "capture_lock_creator", return_value=None),
            mock.patch.object(fiw.time, "time", return_value=self.now),
            mock.patch.object(fiw.subprocess, "run", no_send),
            mock.patch.object(
                sys, "argv", ["fleet-idle-watch.py", "--once", "--dry-run"]
            ),
        )
        with contextlib.ExitStack() as stack:
            for patcher in patches:
                stack.enter_context(patcher)
            with contextlib.redirect_stdout(output):
                self.assertEqual(fiw.main(), 0)
            self.assertTrue(fiw.send_pane(3, "dry-run worker message"))

        self.assertTrue(self.switch.is_file())
        self.assertIn("no current telemetry rows", self.switch.read_text())
        self.assertEqual(self.heartbeat.DRY_RUN_SENDS[0][0], 1)
        self.assertIn((3, "dry-run worker message"), self.heartbeat.DRY_RUN_SENDS)
        no_send.assert_not_called()
        self.assertIn("would page", output.getvalue())
        self.assertNotIn("paged:", output.getvalue())
        liveness = self.state_dir / self.heartbeat.LIVENESS_NAME
        row = json.loads(liveness.read_text().splitlines()[-1])
        self.assertEqual(row["status"], "ok")

    def test_dry_run_healthy_traffic_keeps_switch_on_without_ntm(self):
        self.home.mkdir()
        self.state_dir = self.home / ".local/state/jev"
        self.telemetry_path = self.state_dir / "webscreen-shadow.jsonl"
        self.switch = self.state_dir / "test-surface.off"
        self.write_registry()
        self.write_inputs(statuses=["ok"] * 3)
        no_send = mock.Mock(side_effect=AssertionError("dry-run invoked a subprocess"))
        output = io.StringIO()
        patches = (
            mock.patch.dict(
                os.environ,
                {
                    "HOME": str(self.home),
                    "TMPDIR": str(self.root),
                    "JEV_FLEET_STATE_DIR": str(self.state_dir),
                    "JEV_OMP_ROOT": str(self.omp_root),
                },
            ),
            mock.patch.object(fiw, "SURFACE_REGISTRY", self.registry),
            mock.patch.object(fiw, "poll", return_value={}),
            mock.patch.object(fiw, "submit_shadow"),
            mock.patch.object(fiw, "ci_lines", return_value=[]),
            mock.patch.object(fiw, "stranger_round", return_value=None),
            mock.patch.object(fiw, "judge_lines", return_value=[]),
            mock.patch.object(fiw, "key_round", return_value=None),
            mock.patch.object(fiw, "inbox_paths", return_value=(self.root, self.root)),
            mock.patch.object(fiw, "inbox_round", return_value="no mail"),
            mock.patch.object(fiw, "stale_lock_round", return_value=None),
            mock.patch.object(fiw, "capture_lock_creator", return_value=None),
            mock.patch.object(fiw.time, "time", return_value=self.now),
            mock.patch.object(fiw.subprocess, "run", no_send),
            mock.patch.object(
                sys, "argv", ["fleet-idle-watch.py", "--once", "--dry-run"]
            ),
        )
        with contextlib.ExitStack() as stack:
            for patcher in patches:
                stack.enter_context(patcher)
            with contextlib.redirect_stdout(output):
                self.assertEqual(fiw.main(), 0)

        self.assertFalse(self.switch.exists())
        self.assertEqual(self.heartbeat.DRY_RUN_SENDS, [])
        no_send.assert_not_called()
        self.assertIn("healthy", output.getvalue())
        liveness = self.state_dir / self.heartbeat.LIVENESS_NAME
        row = json.loads(liveness.read_text().splitlines()[-1])
        self.assertEqual(row["status"], "ok")

    def test_scheduled_on_cannot_override_watcher_auto_off(self):
        path = HERE.parents[1] / "work/jev-qpv2/flip.py"
        spec = importlib.util.spec_from_file_location("jev_qpv2_flip", path)
        flip = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(flip)
        schedule = self.root / "schedule.json"
        heartbeat_state = self.root / "heartbeat-state.json"
        switch = self.root / "memory-filter-enforce"
        journal = self.root / "flips.jsonl"
        schedule.write_text(
            json.dumps(
                {
                    "blocks": [
                        {
                            "start": "2026-10-05T12:00:00Z",
                            "end": "2026-10-05T16:00:00Z",
                            "state": "ON",
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        heartbeat_state.write_text(
            json.dumps({"surfaces": {"memory-filter": {"auto_off": True}}}),
            encoding="utf-8",
        )
        output = io.StringIO()
        patches = (
            mock.patch.object(flip, "SCHED", str(schedule)),
            mock.patch.object(flip, "ENFORCE", str(switch)),
            mock.patch.object(flip, "JOURNAL", str(journal)),
            mock.patch.object(
                flip, "HEARTBEAT_STATE", str(heartbeat_state), create=True
            ),
            mock.patch.object(
                flip,
                "now",
                return_value=flip.datetime(
                    2026, 10, 5, 12, 5, tzinfo=flip.timezone.utc
                ),
            ),
        )
        with contextlib.ExitStack() as stack:
            for patcher in patches:
                stack.enter_context(patcher)
            with contextlib.redirect_stdout(output):
                self.assertEqual(flip.main(), 0)

        self.assertFalse(switch.exists())
        self.assertIn("watcher auto-off", output.getvalue())

    def test_operator_off_marker_beats_scheduled_on_when_heartbeat_is_healthy(self):
        path = HERE.parents[1] / "work/jev-qpv2/flip.py"
        spec = importlib.util.spec_from_file_location("jev_qpv2_operator_off", path)
        flip = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(flip)
        schedule = self.root / "schedule.json"
        heartbeat_state = self.root / "heartbeat-state.json"
        switch = self.root / "memory-filter-enforce"
        operator_off = self.root / "memory-filter.operator-off"
        journal = self.root / "flips.jsonl"
        schedule.write_text(json.dumps({"blocks": [{"start": "2026-10-05T12:00:00Z", "end": "2026-10-05T16:00:00Z", "state": "ON"}]}), encoding="utf-8")
        heartbeat_state.write_text(
            json.dumps({"surfaces": {"memory-filter": {"auto_off": False}}}),
            encoding="utf-8",
        )
        operator_off.write_text("operator requested OFF\n", encoding="utf-8")
        output = io.StringIO()
        patches = (
            mock.patch.object(flip, "SCHED", str(schedule)),
            mock.patch.object(flip, "ENFORCE", str(switch)),
            mock.patch.object(flip, "OPERATOR_OFF", str(operator_off)),
            mock.patch.object(flip, "JOURNAL", str(journal)),
            mock.patch.object(flip, "HEARTBEAT_STATE", str(heartbeat_state)),
            mock.patch.object(
                flip,
                "now",
                return_value=flip.datetime(
                    2026, 10, 5, 12, 5, tzinfo=flip.timezone.utc
                ),
            ),
        )
        with contextlib.ExitStack() as stack:
            for patcher in patches:
                stack.enter_context(patcher)
            with contextlib.redirect_stdout(output):
                self.assertEqual(flip.main(), 0)

        self.assertFalse(switch.exists())
        self.assertFalse(journal.exists())
        self.assertIn("operator OFF active", output.getvalue())

    def test_launchd_job_is_kept_alive_and_runs_this_watcher(self):
        service = plistlib.loads((HERE / "ai.jev.fleet-idle-watch.plist").read_bytes())

        self.assertEqual(service["Label"], "ai.jev.fleet-idle-watch")
        self.assertTrue(service["KeepAlive"])
        self.assertTrue(service["RunAtLoad"])
        watcher = Path(service["ProgramArguments"][1])
        self.assertEqual(
            Path(service["WorkingDirectory"]), watcher.resolve().parents[1]
        )
        self.assertEqual(
            watcher.resolve().parts[-2:], ("scripts", "fleet-idle-watch.py")
        )


if __name__ == "__main__":
    unittest.main()
