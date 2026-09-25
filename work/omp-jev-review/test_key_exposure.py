"""The `Key exposure 24h:` line of surface-census.py --fleet-line and its page (bead jev-9ov4).

Keyless, no model calls. At 2026-09-25T05:57Z a pane printed the live TypeSafe key into a tool
result; omp's session log stored it and a manual scan found it 50 minutes later. The census line
counts omp session .jsonl files modified in the last 24h (both session roots, probe sessions
included) holding an unmarked string of the shape in .omp/secrets.yml, and names the newest 3
paths. A match whose 35-character segment starts with `fakefake` is a fake one of our tools made
(scripts/omp-secret-probe.py fake_key()); it is reported separately and never pages.
scripts/fleet-idle-watch.py pages pane 1 once per new path.

Every key here is generated per run with the live shape (apikey_ + 35 + _ + 64 of [a-z0-9]) and
is never printed: each line is checked for key text before any other assertion, with a message
that does not quote it, so a planted "print the match" fails without writing a fake key into
this pane's own session log. The unmarked ones stand in for a real key, so they cannot carry
the marker; they never reach any output.
"""

import contextlib
import importlib.util
import io
import json
import os
import random
import string
import subprocess
import sys
import tempfile
import time
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
CENSUS = HERE / "surface-census.py"
WATCH = HERE.parents[1] / "scripts" / "fleet-idle-watch.py"
ALNUM = string.ascii_lowercase + string.digits


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


sc = load("surface_census_key", CENSUS)
fiw = load("fleet_idle_watch_key", WATCH)


def fake(n):
    return "".join(random.choice(ALNUM) for _ in range(n))


def fake_key(head=35, tail=64, marked=False):
    first = "fakefake" + fake(head - 8) if marked else fake(head)
    return f"apikey_{first}_{fake(tail)}"


def write_session(
    home, name, text, age_s, profile="claude", cwd="/Users/josh/Developer/jev"
):
    """A session file with one toolResult row per text (a str is one row), last modified
    `age_s` ago. profile None is the default root, ~/.omp/agent/sessions."""
    root = home / ".omp" / "agent" / "sessions"
    if profile is not None:
        root = home / ".omp" / "profiles" / profile / "agent" / "sessions"
    folder = root / ("-tmp-probe" if "/tmp/" in cwd else "-Developer-jev")
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{name}.jsonl"
    rows = [
        {
            "type": "session",
            "version": 3,
            "id": name,
            "timestamp": "2026-09-25T00:00:00Z",
            "cwd": cwd,
        },
    ] + [
        {
            "type": "message",
            "message": {
                "role": "toolResult",
                "toolName": "bash",
                "content": [{"type": "text", "text": f"env check\n{one}\nexit 0"}],
            },
        }
        for one in ([text] if isinstance(text, str) else text)
    ]
    path.write_text("".join(json.dumps(r, separators=(",", ":")) + "\n" for r in rows))
    stamp = time.time() - age_s
    os.utime(path, (stamp, stamp))
    return path


def hhmm(path):
    return time.strftime("%H:%M", time.gmtime(path.stat().st_mtime))


class Keyed(unittest.TestCase):
    def setUp(self):
        # mkdtemp and left in place: this lane never deletes files (AGENTS.md RULE 1)
        self.home = Path(tempfile.mkdtemp(prefix="key-exposure-")) / "home"
        self.home.mkdir()
        self.keys = []

    def key(self, head=35, tail=64, marked=False):
        made = fake_key(head, tail, marked)
        self.keys.append(made)
        return made

    def clean(self, text):
        """Fail, without quoting it, if any generated key or either random half is in text."""
        for made in self.keys:
            _, head, tail = made.split("_")
            leaked = made in text or head in text or tail in text
            self.assertFalse(leaked, "generated key text is in the output")
        return text

    def line(self, secrets=None, now=None):
        files = sorted(self.home.rglob("*.jsonl"))
        found = sc.key_exposure_line(
            files, now or datetime.now(timezone.utc), bool(files), secrets or sc.SECRETS
        )
        return self.clean(found)


class KeyExposureLine(Keyed):
    def test_a_key_shaped_string_counts_and_only_the_path_prints(self):
        path = write_session(self.home, "leak", f"TYPESAFE_API_KEY={self.key()}", 3600)
        write_session(self.home, "quiet", "nothing here", 60)
        line = self.line()
        self.assertEqual(
            line,
            "Key exposure 24h: 1 session files hold an unmarked TypeSafe-shaped key "
            f"(2 scanned; 0 hold only marked fakes); newest: {path} ({hhmm(path)}Z)",
        )

    def test_a_106_character_near_miss_does_not_count(self):
        short_head = self.key(head=34)
        short_tail = self.key(tail=63)
        self.assertEqual({len(short_head), len(short_tail)}, {106})
        write_session(self.home, "head", f"key={short_head}", 60)
        write_session(self.home, "tail", f'{{"key":"{short_tail}"}}', 60)
        self.assertEqual(
            self.line(),
            "Key exposure 24h: 0 session files hold an unmarked TypeSafe-shaped key "
            "(2 scanned; 0 hold only marked fakes)",
        )

    def test_a_file_last_modified_over_24h_ago_is_not_scanned(self):
        write_session(self.home, "old", self.key(), 25 * 3600)
        write_session(self.home, "new", "no key", 60)
        self.assertEqual(
            self.line(),
            "Key exposure 24h: 0 session files hold an unmarked TypeSafe-shaped key "
            "(1 scanned; 0 hold only marked fakes)",
        )

    def test_a_marked_fake_is_not_counted_and_is_reported_separately(self):
        write_session(self.home, "probe", f"cat line.txt\n{self.key(marked=True)}", 60)
        write_session(
            self.home, "twice", f"{self.key(marked=True)} {self.key(marked=True)}", 60
        )
        self.assertEqual(
            self.line(),
            "Key exposure 24h: 0 session files hold an unmarked TypeSafe-shaped key "
            "(2 scanned; 2 hold only marked fakes)",
        )

    def test_a_marked_fake_ahead_of_an_unmarked_key_still_counts(self):
        same_line = write_session(
            self.home, "same", f"{self.key(marked=True)} then {self.key()}", 60
        )
        later_line = write_session(
            self.home, "later", [self.key(marked=True), "later", self.key()], 30
        )
        self.assertEqual(len(later_line.read_text().splitlines()), 4)
        self.assertEqual(
            self.line(),
            "Key exposure 24h: 2 session files hold an unmarked TypeSafe-shaped key "
            "(2 scanned; 0 hold only marked fakes); newest: "
            f"{later_line} ({hhmm(later_line)}Z), {same_line} ({hhmm(same_line)}Z)",
        )

    def test_probe_sessions_and_the_default_root_count(self):
        probe = write_session(
            self.home, "probe", self.key(), 120, profile=None, cwd="/tmp/omp-probe"
        )
        self.assertEqual(sc.session_location(probe)[0], "default")
        self.assertTrue(sc.is_probe(probe, "/tmp/omp-probe"))
        line = self.line()
        self.assertTrue(line.startswith("Key exposure 24h: 1 session files hold"), line)
        self.assertIn(str(probe), line)

    def test_names_the_newest_three_paths_newest_first_with_mtimes(self):
        paths = [
            write_session(self.home, f"leak{i}", self.key(), age, profile=profile)
            for i, (age, profile) in enumerate(
                [(4000, "codex"), (300, "claude"), (9000, "grok"), (2000, None)]
            )
        ]
        newest = [paths[1], paths[3], paths[0]]
        self.assertEqual(
            self.line(),
            "Key exposure 24h: 4 session files hold an unmarked TypeSafe-shaped key "
            "(4 scanned; 0 hold only marked fakes); newest: "
            + ", ".join(f"{p} ({hhmm(p)}Z)" for p in newest),
        )

    def test_one_file_with_many_keys_is_one_file(self):
        write_session(self.home, "many", "\n".join(self.key() for _ in range(5)), 60)
        self.assertTrue(
            self.line().startswith("Key exposure 24h: 1 session files hold"),
        )

    def test_no_session_files_is_not_run_never_zero(self):
        self.assertEqual(
            self.line(),
            "Key exposure 24h: NOT_RUN no omp session files under "
            "~/.omp/agent/sessions, ~/.omp/profiles/*/agent/sessions",
        )

    def test_missing_secrets_yml_is_not_run_and_scans_nothing(self):
        write_session(self.home, "leak", self.key(), 60)
        missing = self.home / "nowhere" / "secrets.yml"
        line = self.line(secrets=missing)
        self.assertTrue(line.startswith("Key exposure 24h: NOT_RUN "), line)
        self.assertIn(str(missing), line)
        self.assertNotIn("session files hold", line)

    def test_unparsable_secrets_yml_is_not_run(self):
        write_session(self.home, "leak", self.key(), 60)
        bad = self.home / "secrets.yml"
        for text in (
            "",  # no entries
            "- type: plain\n  content: hunter2hunter2\n",  # no regex entry
            '- type: regex\n  content: "apikey_[a-z0-9"\n',  # does not compile
            "- type: regex\n  content: [unclosed\n  just words\n",  # not key: value
            '- type: regex\n  content: "bad \\q escape\n',  # bad double-quoted value
        ):
            bad.write_text(text)
            line = self.line(secrets=bad)
            self.assertTrue(line.startswith("Key exposure 24h: NOT_RUN "), (text, line))
            self.assertNotIn("hunter2", line)

    def test_flags_and_regex_literal_syntax_from_secrets_yml(self):
        write_session(self.home, "upper", self.key().upper(), 60)
        literal = self.home / "literal.yml"
        literal.write_text(
            '- type: regex\n  content: "/apikey_[a-z0-9]{35}_[a-z0-9]{64}/i"\n'
        )
        flagged = self.home / "flagged.yml"
        flagged.write_text(
            '- type: regex\n  content: "apikey_[a-z0-9]{35}_[a-z0-9]{64}"\n  flags: "i"\n'
        )
        for secrets in (literal, flagged):
            line = self.line(secrets=secrets)
            self.assertTrue(line.startswith("Key exposure 24h: 1 session files"), line)
        self.assertTrue(
            self.line().startswith("Key exposure 24h: 0 session files"),
            "the repo pattern is case-sensitive",
        )


class Cli(Keyed):
    def test_fleet_line_prints_the_key_line_third_and_never_the_key(self):
        path = write_session(self.home, "leak", self.key(), 600, profile="codex")
        done = subprocess.run(
            [sys.executable, str(CENSUS), "--fleet-line"],
            capture_output=True,
            text=True,
            env=dict(os.environ, HOME=str(self.home)),
            timeout=60,
        )
        out = self.clean(done.stdout + done.stderr)
        self.assertEqual(done.returncode, 0, out)
        lines = out.splitlines()
        self.assertEqual(len(lines), 4, out)
        self.assertTrue(lines[0].startswith("Jev judge 24h: "), lines[0])
        self.assertTrue(lines[1].startswith("Skills 24h: "), lines[1])
        self.assertEqual(
            lines[2],
            "Key exposure 24h: 1 session files hold an unmarked TypeSafe-shaped key "
            f"(1 scanned; 0 hold only marked fakes); newest: {path} ({hhmm(path)}Z)",
        )
        self.assertTrue(lines[3].startswith("Jev tools 24h: "), lines[3])


class KeyPage(Keyed):
    def setUp(self):
        super().setUp()
        self.state = self.home.parent / "state" / "key-exposure-paged.json"
        self.sent = []
        self.ok = True

    def send(self, message):
        self.clean(message)
        self.sent.append(message)
        return self.ok

    def census(self):
        return [
            "Jev judge 24h: 0 calls, $0.0000, 0 failures",
            "Skills 24h: x",
            self.line(),
        ]

    def round(self, module=None):
        note = (module or fiw).key_round(self.census(), self.state, self.send)
        return self.clean(note) if note else note

    def test_a_new_exposed_path_pages_pane_1_once(self):
        path = write_session(self.home, "leak", self.key(), 60)
        note = self.round()
        self.assertEqual(
            self.sent,
            [
                f"KEY EXPOSURE: {path} holds a TypeSafe-shaped key (modified {hhmm(path)}Z); "
                "1 session files in 24h. Rotate the key; never open that file into a pane."
            ],
        )
        self.assertEqual(note, "Key page: 1 new paths paged this round, 1 paged total")
        self.assertEqual(
            self.round(), "Key page: 0 new paths paged this round, 1 paged total"
        )
        self.assertEqual(len(self.sent), 1)

    def test_a_file_holding_only_marked_fakes_pages_nothing(self):
        write_session(self.home, "probe", self.key(marked=True), 60, cwd="/tmp/doc7")
        self.assertIsNone(self.round())
        self.assertEqual(self.sent, [])
        self.assertFalse(self.state.exists())

    def test_a_restart_with_the_same_state_file_pages_nothing(self):
        write_session(self.home, "leak", self.key(), 60)
        self.round()
        restarted = load("fleet_idle_watch_restarted", WATCH)
        self.round(restarted)
        self.assertEqual(len(self.sent), 1)

    def test_a_second_exposed_path_pages_only_itself(self):
        write_session(self.home, "first", self.key(), 600)
        self.round()
        second = write_session(self.home, "second", self.key(), 30)
        self.round()
        self.assertEqual(len(self.sent), 2)
        self.assertTrue(
            self.sent[1].startswith(f"KEY EXPOSURE: {second} holds"), self.sent[1]
        )
        self.assertIn("2 session files in 24h", self.sent[1])

    def test_a_failed_send_is_retried_next_round(self):
        write_session(self.home, "leak", self.key(), 60)
        self.ok = False
        note = self.round()
        self.assertIn("1 send failed, retried next round", note)
        self.ok = True
        self.round()
        self.round()
        self.assertEqual(len(self.sent), 2)

    def test_zero_or_not_run_pages_nothing_and_writes_no_state(self):
        write_session(self.home, "quiet", "no key", 60)
        self.assertIsNone(self.round())
        missing = ["Jev judge 24h: x", "Skills 24h: y"]
        self.assertIsNone(fiw.key_round(missing, self.state, self.send))
        not_run = ["Key exposure 24h: NOT_RUN surface-census.py timed out after 60s"]
        self.assertIsNone(fiw.key_round(not_run, self.state, self.send))
        self.assertEqual(self.sent, [])
        self.assertFalse(self.state.exists())

    def test_unreadable_state_file_is_not_run_and_pages_nothing(self):
        write_session(self.home, "leak", self.key(), 60)
        self.state.parent.mkdir(parents=True)
        self.state.write_text("{not json")
        note = self.round()
        self.assertTrue(note.startswith("Key page: NOT_RUN state file "), note)
        self.assertEqual(self.sent, [])
        self.assertEqual(self.state.read_text(), "{not json")

    def test_the_forever_loop_pages_in_its_first_round(self):
        path = write_session(self.home, "leak", self.key(), 60)
        lines = self.census()

        class Stop(Exception):
            pass

        env = {
            "JEV_WATCH_KEY_STATE": str(self.state),
            "JEV_WATCH_INBOX_ROOT": str(self.home / "no-inbox"),
            "JEV_WATCH_INBOX_STATE": str(self.home.parent / "state" / "inbox.json"),
        }
        out = io.StringIO()
        with (
            mock.patch.dict(os.environ, env),
            mock.patch.object(fiw, "poll", return_value={}),
            mock.patch.object(fiw, "judge_lines", return_value=lines),
            mock.patch.object(fiw, "send_pane1", side_effect=self.send),
            mock.patch.object(fiw.time, "sleep", side_effect=Stop),
            mock.patch.object(sys, "argv", ["fleet-idle-watch.py"]),
            contextlib.redirect_stdout(out),
        ):
            with self.assertRaises(Stop):
                fiw.main()
        self.clean(out.getvalue())
        self.assertEqual(len(self.sent), 1)
        self.assertTrue(self.sent[0].startswith(f"KEY EXPOSURE: {path} holds"))
        self.assertIn(lines[2], out.getvalue())


if __name__ == "__main__":
    unittest.main()
