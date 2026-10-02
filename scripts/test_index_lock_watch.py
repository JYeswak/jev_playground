"""Unit tests for scripts/index-lock-watch.py (offline; stubbed subprocess)."""

import importlib.util
import json
import os
import sys
import tempfile
import unittest

_spec = importlib.util.spec_from_file_location(
    "index_lock_watch",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "index-lock-watch.py"),
)
w = importlib.util.module_from_spec(_spec)
sys.modules["index_lock_watch"] = w
_spec.loader.exec_module(w)


class FakeRun:
    """Canned pgrep/lsof/ps/tmux answers for one git holder in a pane tree."""

    def __init__(self, lock):
        self.lock = lock
        self.calls = []

    def __call__(self, cmd, **kw):
        self.calls.append(cmd)
        prog = cmd[0]
        if prog == "pgrep":
            return Out("4242\n")
        if prog == "lsof":
            if cmd[1] == "-p":
                return Out(
                    "COMMAND PID\n"
                    + ("git 4242\n" + self.lock + "\n" if cmd[2] == "4242" else "")
                )
            return Out("4242\n")
        if prog == "ps":
            field = cmd[2].rstrip("=")
            table = {
                ("4242", "command"): "git commit -m x",
                ("4242", "ppid"): "111",
                ("111", "command"): "-zsh",
                ("111", "ppid"): "100",
                ("100", "command"): "tmux: client",
                ("100", "ppid"): "1",
            }
            return Out(table.get((cmd[4], field), ""))
        if prog == "tmux":
            return Out("111 %3\n999 %7\n")
        raise AssertionError(cmd)


class Out:
    def __init__(self, stdout):
        self.stdout = stdout


def mkrepo():
    d = tempfile.mkdtemp(prefix="ilw-")
    os.makedirs(os.path.join(d, ".git"))
    return d


class TestCapture(unittest.TestCase):
    def test_no_lock_no_row(self):
        d = mkrepo()
        log = os.path.join(d, "rows.jsonl")
        state = os.path.join(d, "state.json")
        self.assertIsNone(w.capture_once(d, log, state, run=FakeRun("L")))
        self.assertFalse(os.path.exists(log))

    def test_first_sight_captures_holder_chain_and_pane(self):
        d = mkrepo()
        lock = os.path.join(d, ".git", "index.lock")
        open(lock, "w").write("")
        log = os.path.join(d, "rows.jsonl")
        state = os.path.join(d, "state.json")
        row = w.capture_once(d, log, state, run=FakeRun(lock))
        self.assertIsNotNone(row)
        self.assertEqual(row["holders"][0]["pid"], "4242")
        self.assertEqual(row["holders"][0]["argv"], "git commit -m x")
        self.assertEqual(row["holders"][0]["parents"][0]["pid"], "111")
        self.assertEqual(row["pane"], "%3")
        self.assertEqual(row["trigger"], "event")
        logged = json.loads(open(log).read())
        self.assertEqual(logged["holders"][0]["pid"], "4242")

    def test_same_identity_captures_once(self):
        d = mkrepo()
        lock = os.path.join(d, ".git", "index.lock")
        open(lock, "w").write("")
        log = os.path.join(d, "rows.jsonl")
        state = os.path.join(d, "state.json")
        run = FakeRun(lock)
        self.assertIsNotNone(w.capture_once(d, log, state, run=run))
        self.assertIsNone(w.capture_once(d, log, state, run=run))

    def test_vanished_lock_resets_state(self):
        d = mkrepo()
        lock = os.path.join(d, ".git", "index.lock")
        open(lock, "w").write("")
        log = os.path.join(d, "rows.jsonl")
        state = os.path.join(d, "state.json")
        run = FakeRun(lock)
        w.capture_once(d, log, state, run=run)
        os.unlink(lock)
        self.assertIsNone(w.capture_once(d, log, state, run=run))
        open(lock, "w").write("")
        self.assertIsNotNone(w.capture_once(d, log, state, run=run))

    def test_lsof_fallback_finds_non_git_holder(self):
        d = mkrepo()
        lock = os.path.join(d, ".git", "index.lock")
        open(lock, "w").write("")

        class NoGit(FakeRun):
            def __call__(self, cmd, **kw):
                if cmd[0] == "pgrep":
                    return Out("")
                return super().__call__(cmd, **kw)

        log = os.path.join(d, "rows.jsonl")
        state = os.path.join(d, "state.json")
        row = w.capture_once(d, log, state, run=NoGit(lock))
        self.assertEqual(row["holders"][0]["pid"], "4242")

    def test_poll_once_writes_fs_event_before_capture(self):
        d = mkrepo()
        lock = os.path.join(d, ".git", "index.lock")
        open(lock, "w").write("")
        log = os.path.join(d, "rows.jsonl")
        state = os.path.join(d, "state.json")
        ops = os.path.join(d, "ops.jsonl")

        class FakeKQ:
            def control(self, changes, max_events, timeout):
                return ["evt"]

        events = w._poll_once(FakeKQ(), d, log, state, ops, FakeRun(lock), 0)
        self.assertEqual(events, 1)
        rows = [json.loads(l) for l in open(ops)]
        self.assertEqual(rows[0]["type"], "fs-event")
        self.assertEqual(rows[0]["nevents"], 1)
        cap = [json.loads(l) for l in open(log)]
        self.assertEqual(cap[0]["holders"][0]["pid"], "4242")

    def test_poll_once_quiet_when_no_event(self):
        d = mkrepo()
        ops = os.path.join(d, "ops.jsonl")

        class QuietKQ:
            def control(self, changes, max_events, timeout):
                return []

        events = w._poll_once(
            QuietKQ(),
            d,
            os.path.join(d, "r.jsonl"),
            os.path.join(d, "s.json"),
            ops,
            FakeRun("L"),
            0,
        )
        self.assertEqual(events, 0)
        self.assertFalse(os.path.exists(ops))


if __name__ == "__main__":
    unittest.main()
