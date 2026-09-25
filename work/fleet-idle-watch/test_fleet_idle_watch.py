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
"""

import importlib.util
import unittest
from pathlib import Path

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


def snapshot(pane, screen, command="bun", session_age=OLD, table=TABLE):
    omp, tools = fiw.omp_processes(table, PANE_PID[pane])
    return fiw.Snapshot(
        command=command,
        screen=screen,
        omp=omp is not None,
        tools=tuple(tools),
        session_age=session_age,
    )


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


if __name__ == "__main__":
    unittest.main()
