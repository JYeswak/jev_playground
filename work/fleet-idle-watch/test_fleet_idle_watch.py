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

Inbox pages (bead jev-lqfm): Agent Mail archive files written into a temp dir per test, in the
shape of the real AmberWillow inbox file ...__42478.md (`---json`, the JSON front matter, `---`,
the body). The send function is a list-appending stub, so no test pages pane 1.
"""

import contextlib
import importlib.util
import io
import json
import os
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


if __name__ == "__main__":
    unittest.main()
