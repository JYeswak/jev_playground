from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


outcomes = load_module("gate_outcomes", ROOT / "scripts/gate-outcomes.py")
reporter = load_module("gate_report", ROOT / "scripts/gate-report.py")


class GateOutcomeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.command = "rm tracked.txt"
        self.digest = hashlib.sha256(self.command.encode()).hexdigest()
        self.row = {
            "ts": "2026-09-25T20:00:00Z",
            "session": "session-a",
            "cmdSha": self.digest,
            "cmd": "rm tracked.txt",
            "status": "scored",
            "flag": True,
            "probs": {"destructive": 0.91},
            "latencyMs": 100,
            "tokens": {"input_tokens": 100, "output_tokens": 10},
        }

    def event_stream(self, *events):
        return [{"type": "session", "id": "session-a", "timestamp": 0}, *events]

    def test_dcg_block_is_harm_evidence(self):
        events = self.event_stream(
            {
                "type": "custom",
                "customType": "tool_execution_start",
                "timestamp": 1_000,
                "data": {"toolCallId": "call-a", "args": {"command": self.command}},
            },
            {
                "type": "custom",
                "customType": "com.zeststream.omp-dcg-bridge.decision.v1",
                "timestamp": 2_000,
                "data": {"kind": "dcg_block"},
            },
        )
        joined = outcomes.join_row(self.row, events, self.command, max_events=2)
        self.assertEqual(joined["outcome"], "harm-evidence")
        self.assertEqual(joined["evidence"], ["dcg-deny"])

    def test_restore_same_path_is_harm_evidence(self):
        events = self.event_stream(
            {
                "type": "message",
                "timestamp": 1_000,
                "message": {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "toolCall",
                            "name": "bash",
                            "id": "call-a",
                            "arguments": {"command": self.command},
                        }
                    ],
                },
            },
            {
                "type": "message",
                "timestamp": 2_000,
                "message": {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "toolCall",
                            "name": "bash",
                            "id": "call-b",
                            "arguments": {"command": "git restore -- tracked.txt"},
                        }
                    ],
                },
            },
        )
        joined = outcomes.join_row(self.row, events, self.command, max_events=2)
        self.assertEqual(joined["outcome"], "harm-evidence")
        self.assertIn("restore-or-revert", joined["evidence"])

    def test_undo_phrase_is_harm_evidence(self):
        events = self.event_stream(
            {
                "type": "message",
                "timestamp": 1_000,
                "message": {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "toolCall",
                            "name": "bash",
                            "id": "call-a",
                            "arguments": {"command": self.command},
                        }
                    ],
                },
            },
            {
                "type": "message",
                "timestamp": 2_000,
                "message": {
                    "role": "user",
                    "content": [{"type": "text", "text": "undo that change"}],
                },
            },
        )
        joined = outcomes.join_row(self.row, events, self.command, max_events=2)
        self.assertEqual(joined["outcome"], "harm-evidence")
        self.assertIn("undo-phrase", joined["evidence"])

    def test_failed_follow_up_is_harm_evidence(self):
        events = self.event_stream(
            {
                "type": "message",
                "timestamp": 1_000,
                "message": {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "toolCall",
                            "name": "bash",
                            "id": "call-a",
                            "arguments": {"command": self.command},
                        }
                    ],
                },
            },
            {
                "type": "message",
                "timestamp": 2_000,
                "message": {
                    "role": "toolResult",
                    "toolName": "bash",
                    "toolCallId": "call-a",
                    "isError": True,
                },
            },
        )
        joined = outcomes.join_row(self.row, events, self.command, max_events=2)
        self.assertEqual(joined["outcome"], "harm-evidence")
        self.assertIn("failed-follow-up", joined["evidence"])

    def test_wrong_session_or_command_is_unknown(self):
        events = [{"type": "session", "id": "other", "timestamp": 0}]
        joined = outcomes.join_row(self.row, events, self.command, max_events=2)
        self.assertEqual(joined["outcome"], "unknown")
        self.assertEqual(joined["evidence"], [])

    def test_enough_observed_events_without_evidence_is_no_evidence(self):
        events = self.event_stream(
            {
                "type": "message",
                "timestamp": 1_000,
                "message": {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "toolCall",
                            "name": "bash",
                            "id": "call-a",
                            "arguments": {"command": self.command},
                        }
                    ],
                },
            },
            {
                "type": "message",
                "timestamp": 2_000,
                "message": {
                    "role": "toolResult",
                    "toolName": "bash",
                    "toolCallId": "call-a",
                    "isError": False,
                },
            },
        )
        joined = outcomes.join_row(self.row, events, self.command, max_events=1)
        self.assertEqual(joined["outcome"], "no-evidence")

    def test_report_contains_cost_latency_flags_and_confusion(self):
        rows = [
            {**self.row, "outcome": "harm-evidence"},
            {
                **self.row,
                "cmdSha": "b",
                "flag": False,
                "outcome": "no-evidence",
                "latencyMs": 300,
                "tokens": {"input_tokens": 900, "output_tokens": 20},
            },
        ]
        result = reporter.report(rows)
        self.assertEqual(result["scored"], 2)
        self.assertEqual(result["confusion"]["true_positive"], 1)
        self.assertEqual(result["confusion"]["true_negative"], 1)
        self.assertGreater(result["spend_usd_estimate"], 0)
        self.assertEqual(result["latency_ms"]["p50"], 200)

    def test_native_usage_groups_by_day_and_purpose(self):
        with tempfile.TemporaryDirectory() as directory:
            session = (
                Path(directory)
                / "profiles"
                / "codex"
                / "agent"
                / "sessions"
                / "test"
                / "session.jsonl"
            )
            session.parent.mkdir(parents=True)
            session.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "type": "message",
                                "id": "m1",
                                "message": {"role": "assistant"},
                                "duration": 123,
                            }
                        ),
                        json.dumps(
                            {
                                "type": "model_usage",
                                "id": "u1",
                                "parentId": "m1",
                                "provider": "typesafe",
                                "purpose": "find",
                                "timestamp": 1758800000000,
                                "usage": {
                                    "input": 100,
                                    "output": 20,
                                    "cost": {"total": 0.0012},
                                },
                            }
                        ),
                    ]
                )
                + "\n"
            )
            result = reporter.native_usage_report(Path(directory) / "profiles")
            values = result["days"]["2025-09-25"]["find"]
            self.assertEqual(result["calls"], 1)
            self.assertEqual(values["input_tokens"], 100)
            self.assertEqual(values["spend_usd"], 0.0012)
            self.assertEqual(values["latency_ms"]["p50"], 123.0)


if __name__ == "__main__":
    unittest.main()
