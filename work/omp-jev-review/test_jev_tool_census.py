"""The Jev tools line of surface-census.py --fleet-line (bead jev-x28o). No model calls.

Row shapes follow real omp session files, 2026-09-24..25: a project tool is called as a `write`
(or `read`) tool call whose arguments.path is `xd://jev_rerank` etc., and its result is a
`toolResult` message carrying the same toolCallId; a failed call has `"isError": true`.
"""

import importlib.util
import itertools
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


sc = load("surface_census", HERE / "surface-census.py")

NOW = datetime(2026, 9, 25, 14, 0, tzinfo=timezone.utc)
IN_WINDOW = "2026-09-25T13:10:00.000Z"
TOO_OLD = "2026-09-24T13:10:00.000Z"
ROSTER = ["jev_claim_check", "jev_flag", "jev_rerank", "jev_screen"]
IDS = itertools.count(1)


def call(name, arguments, timestamp=IN_WINDOW):
    call_id = f"toolu_{next(IDS):06d}"
    row = {
        "type": "message",
        "timestamp": timestamp,
        "message": {
            "role": "assistant",
            "content": [
                {
                    "type": "toolCall",
                    "id": call_id,
                    "name": name,
                    "arguments": arguments,
                }
            ],
        },
    }
    return call_id, row


def xd(tool, verb="write", timestamp=IN_WINDOW):
    return call(verb, {"path": f"xd://{tool}", "content": "{}"}, timestamp)


def failed(call_id):
    return {
        "type": "message",
        "timestamp": IN_WINDOW,
        "message": {
            "role": "toolResult",
            "toolCallId": call_id,
            "toolName": "write",
            "isError": True,
            "content": [{"type": "text", "text": "schema error"}],
        },
    }


def write_session(home, profile, encoded, cwd, rows):
    folder = home / ".omp" / "profiles" / profile / "agent" / "sessions" / encoded
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{len(list(folder.iterdir()))}.jsonl"
    head = [
        {
            "type": "session",
            "version": 3,
            "id": "s",
            "timestamp": "2026-09-25T00:00:00Z",
            "cwd": cwd,
        }
    ]
    path.write_text(
        "".join(json.dumps(r, separators=(",", ":")) + "\n" for r in head + rows)
    )
    return path


class JevToolsLine(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="jev-tools-census-")
        self.home = Path(self.tmp.name) / "home"

    def tearDown(self):
        self.tmp.cleanup()

    def real(
        self,
        rows,
        profile="claude",
        encoded="-Developer-jev",
        cwd="/Users/josh/Developer/jev",
    ):
        return write_session(self.home, profile, encoded, cwd, rows)

    def line(self, roster=ROSTER):
        files = sorted(self.home.rglob("*.jsonl"))
        return sc.jev_tools_line(sc.jev_tool_calls(files), NOW, bool(files), roster)

    def test_write_and_read_calls_count_per_tool_and_unused_tools_are_named(self):
        self.real(
            [xd("jev_rerank")[1], xd("jev_rerank", "read")[1], xd("jev_claim_check")[1]]
        )
        self.real([xd("jev_rerank")[1]], profile="codex")
        self.assertEqual(
            self.line(),
            "Jev tools 24h: jev_rerank 3, jev_claim_check 1, jev_flag 0, jev_screen 0 in 2 sessions; "
            "never called: jev_flag, jev_screen",
        )

    def test_a_call_whose_result_failed_is_not_a_call(self):
        call_id, row = xd("jev_flag")
        self.real([row, failed(call_id)])
        self.assertIn("jev_flag 0", self.line())

    def test_probe_sessions_and_load_probes_are_not_calls(self):
        self.real([xd("jev_screen")[1]], profile="omp-test")
        self.real(
            [xd("jev_screen")[1]],
            encoded="-private-tmp-probe",
            cwd="/private/tmp/probe",
        )
        self.real([xd("jev_rerank_ext_probe")[1]])
        self.assertEqual(
            self.line(),
            "Jev tools 24h: jev_claim_check 0, jev_flag 0, jev_rerank 0, jev_screen 0 in 0 sessions; "
            "never called: jev_claim_check, jev_flag, jev_rerank, jev_screen",
        )

    def test_calls_older_than_24h_and_tools_outside_the_roster_do_not_count(self):
        self.real([xd("jev_rerank", timestamp=TOO_OLD)[1], xd("jev_unshipped")[1]])
        self.assertEqual(
            self.line(),
            "Jev tools 24h: jev_claim_check 0, jev_flag 0, jev_rerank 0, jev_screen 0 in 0 sessions; "
            "never called: jev_claim_check, jev_flag, jev_rerank, jev_screen",
        )

    def test_a_tool_called_by_its_own_name_counts(self):
        self.real([call("jev_screen", {"text": "hi"})[1]])
        self.assertIn("jev_screen 1", self.line())

    def test_every_tool_called(self):
        self.real([xd(t)[1] for t in ROSTER])
        self.assertTrue(self.line().endswith("; every tool called"), self.line())

    def test_not_run_without_sessions_or_without_a_roster(self):
        self.assertTrue(
            self.line().startswith("Jev tools 24h: NOT_RUN no omp session files")
        )
        self.real([xd("jev_rerank")[1]])
        self.assertTrue(
            self.line(roster=None).startswith(
                "Jev tools 24h: NOT_RUN no .omp/tools/jev-*.ts"
            )
        )

    def test_roster_comes_from_the_shipped_tool_file_names(self):
        tools = Path(self.tmp.name) / "tools"
        tools.mkdir()
        for name in ("jev-rerank.ts", "jev-claim-check.ts", "other.ts", "jev-notes.md"):
            (tools / name).write_text("")
        self.assertEqual(sc.jev_tool_roster(tools), ["jev_claim_check", "jev_rerank"])
        self.assertIsNone(sc.jev_tool_roster(Path(self.tmp.name) / "missing"))


if __name__ == "__main__":
    unittest.main()
