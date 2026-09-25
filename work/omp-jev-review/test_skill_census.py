"""The skills line of surface-census.py --fleet-line (bead jev-yy7f). No model calls.

Row shapes are copied from real omp session files, 2026-09-23..25:
  read skill://    ~/.omp/profiles/claude/agent/sessions/-Developer-omp-test/2026-09-25T00-09-17-159Z_...
                   an assistant `message` whose content holds {"type":"toolCall","name":"read",
                   "arguments":{"path":"skill://zeststream-tmp",...}}
  read absolute    .../-Developer-omp-test/2026-09-25T00-03-13-684Z_... (codex): arguments.path
                   "/Users/josh/.claude/skills/private-document-librarian/SKILL.md:1-100"
  bash SKILL.md    a codex session: `grep -n ... ~/.agents/skills/cfs-google-ads/SKILL.md | head`;
                   the glob listing `ls -d /Users/josh/.claude/skills/*/ | wc -l; cat
                   /Users/josh/.claude/skills/*/SKILL.md` (2026-09-23) names no skill
  skill-prompt     ~/.omp/profiles/claude/agent/sessions/-Developer-clutterfreespaces.ios/...:
                   {"type":"custom_message","customType":"skill-prompt","content":"[IMPORTANT: User
                   invoked the \\"vibing-with-ntm\\" skill; ...", "attribution":"user", ...}
  tool result      a grep toolResult that quotes a skill-prompt row (SrCorpus.jsonl, 2026-09-24);
                   quoting the header is not invoking the skill
  failed read      this pane's own session, 2026-09-25T06:1xZ: `read skill://test-driven-development`
                   in a pane started before the skill was installed answered a toolResult with
                   "isError": true and "Unknown skill: test-driven-development"; that read nothing
  bash reader      pane 1, default profile, 2026-09-23T03:39Z, verbatim: `git -C ~/.claude/skills ...;
                   grep -n '^## Fast Triage Order' -A 12 ~/.claude/skills/rch/SKILL.md | head -16; ...`
  bash message     pane 1, 2026-09-25T06:06:45Z `ntm send jev --pane=3 '...read
                   /Users/josh/.claude/skills/systematic-debugging/SKILL.md and ...' >/dev/null 2>&1;
                   echo "p3 rc=$?"` and 06:12:39Z `br comments add ... "..."`: naming a path in a
                   message is not reading it (pane 1's non-author check of e9d037e found these)
  eval read        codex 2026-09-24T23-05-43-825Z, 06:11:53Z, python cell
                   `print(read('/Users/josh/.claude/skills/experimental-design/SKILL.md'))`; codex
                   2026-09-25T04-00-52-178Z, 06:14:00Z, JS cell
                   `const r=await tool.read({path:"/Users/josh/.claude/skills/webapp-testing/SKILL.md"}); ...`
  python -c open   constructed from pane 1's reader list, no real row seen yet
"""

import contextlib
import itertools
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

NOW = datetime(2026, 9, 25, 6, 0, tzinfo=timezone.utc)
IN_WINDOW = "2026-09-25T05:14:18.382Z"
TOO_OLD = "2026-09-24T05:14:18.382Z"
# Three rows of ~/.claude/skills/THIRD-PARTY-SKILLS.tsv, 2026-09-25 (sha columns trimmed).
LEDGER = (
    "skill\trepo\tsha\tpath\tlicense\tstars_at_install\tripwire_scan\tskill_md_sha256_16\tinstalled_at\n"
    "systematic-debugging\tobra/superpowers\tx\tskills/systematic-debugging\tMIT\t0\tclean\tx\t2026-09-25\n"
    "verification-before-completion\tobra/superpowers\tx\tskills/verification-before-completion\tMIT\t0\tclean\tx\t2026-09-25\n"
    "test-driven-development\tobra/superpowers\tx\tskills/test-driven-development\tMIT\t0\tclean\tx\t2026-09-25\n"
)
CALL_IDS = itertools.count(1)


def tool_call(name, arguments, timestamp=IN_WINDOW, call_id=None):
    return {
        "type": "message",
        "id": "6739cf61",
        "parentId": "5d090578",
        "timestamp": timestamp,
        "message": {
            "role": "assistant",
            "content": [
                {"type": "thinking", "thinking": "I want to check the skill first."},
                {
                    "type": "toolCall",
                    "id": call_id or f"toolu_01PVUCGywVhoRzdi8fQn{next(CALL_IDS):04d}",
                    "name": name,
                    "arguments": arguments,
                    "intent": "Reading scratch-dir skill",
                },
            ],
        },
    }


def read(path, timestamp=IN_WINDOW, call_id=None):
    return tool_call("read", {"path": path, "i": "Reading skill"}, timestamp, call_id)


def failed_result(call_id, name):
    return {
        "type": "message",
        "id": "9a1c4e20",
        "parentId": "6739cf61",
        "timestamp": IN_WINDOW,
        "message": {
            "role": "toolResult",
            "toolCallId": call_id,
            "toolName": "read",
            "content": [
                {
                    "type": "text",
                    "text": f"Unknown skill: {name}\nAvailable: ab-test-setup",
                }
            ],
            "details": {},
            "isError": True,
            "timestamp": 1790316617819,
        },
    }


def bash(command):
    return tool_call("bash", {"i": "Mapping skill structure", "command": command})


def eval_cell(language, code, call_id=None):
    return tool_call(
        "eval",
        {
            "language": language,
            "code": code,
            "title": "Read skill",
            "timeout": 30,
            "reset": False,
        },
        call_id=call_id,
    )


def skill_prompt(name, timestamp=IN_WINDOW):
    return {
        "type": "custom_message",
        "customType": "skill-prompt",
        "content": f'[IMPORTANT: User invoked the "{name}" skill; follow its instructions. '
        f"Full skill below.]\n\n# Heading\n",
        "display": True,
        "details": {
            "name": name,
            "path": f"/Users/josh/.agents/skills/{name}/SKILL.md",
            "args": "orchestrate this project",
            "prompt": f"/skill:{name} orchestrate this project",
            "lineCount": 120,
        },
        "attribution": "user",
        "id": "5bfb1f54",
        "parentId": "d0a51d50",
        "timestamp": timestamp,
    }


def quoting_tool_result(name):
    quoted = json.dumps(skill_prompt(name), separators=(",", ":"))
    return {
        "type": "message",
        "id": "24ce4fb0",
        "parentId": "8a4cdb60",
        "timestamp": IN_WINDOW,
        "message": {
            "role": "toolResult",
            "toolCallId": "toolu_013LQh7RBj6PQWMw1h1ADg1W",
            "toolName": "grep",
            "content": [{"type": "text", "text": f"*350:{quoted}"}],
        },
    }


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
            "timestamp": "2026-09-25T00:00:00Z",
            "cwd": cwd,
        },
    ]
    path.write_text(
        "".join(json.dumps(r, separators=(",", ":")) + "\n" for r in head + rows)
    )
    return path


class SkillsLine(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="skill-census-")
        self.home = Path(self.tmp.name) / "home"
        self.ledger = Path(self.tmp.name) / "THIRD-PARTY-SKILLS.tsv"
        self.ledger.write_text(LEDGER)

    def tearDown(self):
        self.tmp.cleanup()

    def real(self, rows, profile="claude"):
        return write_session(
            self.home, profile, "-Developer-jev", "/Users/josh/Developer/jev", rows
        )

    def line(self, ledger=None):
        files = sorted(self.home.rglob("*.jsonl"))
        reads = sc.skill_reads(files)
        return sc.skills_line(reads, NOW, bool(files), ledger or self.ledger)

    def test_skill_url_reads_count_including_a_nested_file(self):
        self.real(
            [
                read("skill://test-driven-development"),
                read(
                    "skill://test-driven-development/references/testing-anti-patterns.md"
                ),
            ]
        )
        self.assertEqual(
            self.line(),
            "Skills 24h: 2 skill reads in 1 sessions; third-party 1/3 read "
            "(top: test-driven-development x2); never read 2",
        )

    def test_absolute_path_reads_count_under_claude_and_agents_dirs(self):
        self.real(
            [
                read(
                    "/Users/josh/.claude/skills/verification-before-completion/SKILL.md:1-100"
                ),
                read(
                    "~/.agents/skills/systematic-debugging/references/root-cause-tracing.md"
                ),
            ]
        )
        self.assertEqual(
            self.line(),
            "Skills 24h: 2 skill reads in 1 sessions; third-party 2/3 read "
            "(top: systematic-debugging x1, verification-before-completion x1); never read 1",
        )

    def test_bash_on_a_named_skill_md_counts_but_a_glob_or_dir_listing_does_not(self):
        self.real(
            [
                bash(
                    'grep -n "^## " ~/.agents/skills/systematic-debugging/SKILL.md | head -n 80'
                ),
                bash(
                    "ls -d /Users/josh/.claude/skills/*/ | wc -l; "
                    "cat /Users/josh/.claude/skills/*/SKILL.md 2>/dev/null | wc -c"
                ),
                bash("ls -la /Users/josh/.claude/skills/zeststream-rch/ | head -8"),
            ]
        )
        self.assertEqual(
            self.line(),
            "Skills 24h: 1 skill reads in 1 sessions; third-party 1/3 read "
            "(top: systematic-debugging x1); never read 2",
        )

    def test_bash_naming_a_skill_md_inside_a_message_does_not_count(self):
        self.real(
            [
                bash(
                    "ntm send jev --pane=3 'From pane 1 to IvoryCreek: Use the two new skills by "
                    "file path (your running session cannot load them by skill:// until a "
                    "restart): read /Users/josh/.claude/skills/systematic-debugging/SKILL.md and "
                    "/Users/josh/.claude/skills/test-driven-development/SKILL.md first.' "
                    '>/dev/null 2>&1; echo "p3 rc=$?"'
                ),
                bash(
                    "cd /Users/josh/Developer/jev && br sync --import-only >/dev/null 2>&1; "
                    'br comments add jev-9gtw.1 --actor AmberWillow "NON-AUTHOR CHECK: read '
                    '/Users/josh/.claude/skills/verification-before-completion/SKILL.md next."'
                ),
            ]
        )
        self.assertEqual(
            self.line(),
            "Skills 24h: 0 skill reads in 0 sessions; third-party 0/3 read; never read 3",
        )

    def test_bash_reader_arguments_count_once_per_skill_per_call(self):
        self.real(
            [
                bash(
                    "git -C ~/.claude/skills rev-parse --show-toplevel 2>&1 | head -1; "
                    "git -C ~/.claude/skills status --porcelain -- rch zeststream-rch 2>&1 | head -5; "
                    "grep -n '^## Fast Triage Order' -A 12 ~/.claude/skills/rch/SKILL.md | head -16; "
                    "grep -n 'rch gc --workers <id>   ' ~/.claude/skills/rch/references/DISK_AND_PRESSURE.md"
                ),
                bash(
                    "python3 -c \"print(open('/Users/josh/.claude/skills/"
                    "test-driven-development/SKILL.md').read()[:400])\""
                ),
            ]
        )
        self.assertEqual(
            self.line(),
            "Skills 24h: 2 skill reads in 1 sessions; third-party 1/3 read "
            "(top: test-driven-development x1); never read 2",
        )

    def test_eval_cells_that_read_a_skill_count_and_an_errored_one_does_not(self):
        self.ledger.write_text(
            LEDGER
            + "experimental-design\tK-Dense-AI/scientific-agent-skills\tx\tskills/experimental-design\tMIT\t0\tclean\tx\t2026-09-25\n"
            + "webapp-testing\tanthropics/skills\tx\tskills/webapp-testing\tApache-2.0\t0\tclean\tx\t2026-09-25\n"
        )
        self.real(
            [
                eval_cell(
                    "py",
                    "print(read('/Users/josh/.claude/skills/experimental-design/SKILL.md'))",
                ),
                eval_cell(
                    "js",
                    'const r=await tool.read({path:"/Users/josh/.claude/skills/webapp-testing/SKILL.md"}); display(r);',
                ),
                eval_cell(
                    "py",
                    "print(read('/Users/josh/.claude/skills/systematic-debugging/SKILL.md'))",
                    call_id="call_KJeP2WMpN3Qze6DusumR8XXn",
                ),
                failed_result("call_KJeP2WMpN3Qze6DusumR8XXn", "systematic-debugging"),
                eval_cell(
                    "py",
                    "display('route: /Users/josh/.claude/skills/test-driven-development/SKILL.md')",
                ),
            ]
        )
        self.assertEqual(
            self.line(),
            "Skills 24h: 2 skill reads in 1 sessions; third-party 2/5 read "
            "(top: experimental-design x1, webapp-testing x1); never read 3",
        )

    def test_a_python_cell_that_only_quotes_a_read_call_does_not_count(self):
        # This pane's own prototype cell, 2026-09-25T06:2xZ: the read calls are string literals
        # handed to the census function under test, so the cell read no skill.
        self.real(
            [
                eval_cell(
                    "py",
                    "print(code_skills('const r=await tool.read({path:\"/Users/josh/.claude/skills/"
                    "test-driven-development/SKILL.md\"}); display(r);'), "
                    "code_skills(\"print(read('/Users/josh/.claude/skills/systematic-debugging/"
                    "SKILL.md'))\"))",
                ),
                eval_cell(
                    "py",
                    "text = await tool.read({'path': '/Users/josh/.claude/skills/"
                    "verification-before-completion/SKILL.md'})\nprint(text)",
                ),
            ]
        )
        self.assertEqual(
            self.line(),
            "Skills 24h: 1 skill reads in 1 sessions; third-party 1/3 read "
            "(top: verification-before-completion x1); never read 2",
        )

    def test_invocation_header_counts_and_a_tool_result_quoting_it_does_not(self):
        self.real(
            [
                skill_prompt("verification-before-completion"),
                quoting_tool_result("test-driven-development"),
            ]
        )
        self.assertEqual(
            self.line(),
            "Skills 24h: 1 skill reads in 1 sessions; third-party 1/3 read "
            "(top: verification-before-completion x1); never read 2",
        )

    def test_probe_session_does_not_count(self):
        write_session(
            self.home,
            "claude",
            "--private-tmp-jev-yy7f-plant--",
            "/tmp/jev-yy7f-plant",
            [
                read("skill://test-driven-development"),
                skill_prompt("systematic-debugging"),
            ],
        )
        self.assertEqual(
            self.line(),
            "Skills 24h: 0 skill reads in 0 sessions; third-party 0/3 read; never read 3",
        )

    def test_non_skill_reads_do_not_count(self):
        self.real(
            [
                read("AGENTS.md"),
                read("/Users/josh/.claude/skills/THIRD-PARTY-SKILLS.tsv"),
                read(
                    "/Users/josh/Developer/jev/work/omp-jev-review/surface-census.py:1-30"
                ),
                tool_call(
                    "grep", {"pattern": "x", "path": "skill://test-driven-development"}
                ),
            ]
        )
        self.assertEqual(
            self.line(),
            "Skills 24h: 0 skill reads in 0 sessions; third-party 0/3 read; never read 3",
        )

    def test_a_read_that_answered_an_error_does_not_count(self):
        self.real(
            [
                read(
                    "skill://test-driven-development",
                    call_id="toolu_012fDdBKAs72aBsqMxuUGQPT",
                ),
                failed_result(
                    "toolu_012fDdBKAs72aBsqMxuUGQPT", "test-driven-development"
                ),
                read("/Users/josh/.claude/skills/test-driven-development/SKILL.md"),
            ]
        )
        self.assertEqual(
            self.line(),
            "Skills 24h: 1 skill reads in 1 sessions; third-party 1/3 read "
            "(top: test-driven-development x1); never read 2",
        )

    def test_unlisted_skill_counts_in_the_total_not_the_third_party_figure(self):
        self.real([read("skill://zeststream-tmp"), skill_prompt("vibing-with-ntm")])
        self.real([read("skill://test-driven-development")], profile="grok")
        self.assertEqual(
            self.line(),
            "Skills 24h: 3 skill reads in 2 sessions; third-party 1/3 read "
            "(top: test-driven-development x1); never read 2",
        )

    def test_rows_older_than_24h_do_not_count(self):
        self.real(
            [
                read("skill://test-driven-development", timestamp=TOO_OLD),
                skill_prompt("systematic-debugging", timestamp=TOO_OLD),
                read("skill://verification-before-completion"),
            ]
        )
        self.assertEqual(
            self.line(),
            "Skills 24h: 1 skill reads in 1 sessions; third-party 1/3 read "
            "(top: verification-before-completion x1); never read 2",
        )

    def test_missing_ledger_is_not_run_never_zero(self):
        self.real([read("skill://test-driven-development")])
        line = self.line(ledger=Path(self.tmp.name) / "absent.tsv")
        self.assertEqual(
            line,
            "Skills 24h: 1 skill reads in 1 sessions; third-party NOT_RUN (no ledger)",
        )

    def test_no_session_files_is_not_run(self):
        line = self.line()
        self.assertTrue(
            line.startswith("Skills 24h: NOT_RUN no omp session files"), line
        )
        self.assertNotIn("0 skill reads", line)


class Cli(unittest.TestCase):
    """The real --fleet-line path and fleet-idle-watch's --once, with HOME pointed at a temp tree."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="skill-census-")
        self.home = Path(self.tmp.name) / "home"
        ledger = self.home / ".claude" / "skills" / "THIRD-PARTY-SKILLS.tsv"
        ledger.parent.mkdir(parents=True)
        ledger.write_text(LEDGER)

    def tearDown(self):
        self.tmp.cleanup()

    def test_fleet_line_prints_the_judge_skills_and_key_lines_and_the_watch_shows_them(
        self,
    ):
        hour_ago = (datetime.now(timezone.utc) - timedelta(hours=1)).strftime(
            "%Y-%m-%dT%H:%M:%S.000Z"
        )
        write_session(
            self.home,
            "grok",
            "-Developer-jev",
            "/Users/josh/Developer/jev",
            [read("skill://test-driven-development", timestamp=hour_ago)],
        )
        want = (
            "Skills 24h: 1 skill reads in 1 sessions; third-party 1/3 read "
            "(top: test-driven-development x1); never read 2"
        )
        done = subprocess.run(
            [sys.executable, str(CENSUS), "--fleet-line"],
            capture_output=True,
            text=True,
            env=dict(os.environ, HOME=str(self.home)),
            timeout=60,
        )
        self.assertEqual(done.returncode, 0, done.stderr)
        lines = done.stdout.splitlines()
        self.assertEqual(len(lines), 4, done.stdout)
        self.assertTrue(lines[0].startswith("Jev judge 24h: 0 calls"), lines[0])
        self.assertEqual(lines[1], want)
        self.assertEqual(
            lines[2],
            "Key exposure 24h: 0 session files hold an unmarked TypeSafe-shaped key "
            "(1 scanned; 0 hold only marked fakes)",
        )
        self.assertTrue(lines[3].startswith("Jev tools 24h: "), lines[3])
        out = io.StringIO()
        with (
            mock.patch.dict(os.environ, {"HOME": str(self.home)}),
            mock.patch.object(fiw, "poll", return_value={2: ("working", "")}),
            mock.patch.object(fiw, "ci_lines", return_value=[]),
            mock.patch.object(sys, "argv", ["fleet-idle-watch.py", "--once"]),
            contextlib.redirect_stdout(out),
        ):
            rc = fiw.main()
        self.assertEqual(rc, 0)
        self.assertIn("Jev judge 24h: 0 calls", out.getvalue())
        self.assertIn(want, out.getvalue())

    def test_a_census_timeout_is_not_run_for_every_line_in_the_watch(self):
        timeout = subprocess.TimeoutExpired(["surface-census.py"], 60)
        with mock.patch.object(fiw.subprocess, "run", side_effect=timeout):
            lines = fiw.judge_lines()
        self.assertEqual(
            [line.split(" NOT_RUN ")[0] for line in lines],
            ["Jev judge 24h:", "Skills 24h:", "Key exposure 24h:", "Jev tools 24h:"],
        )


if __name__ == "__main__":
    unittest.main()
