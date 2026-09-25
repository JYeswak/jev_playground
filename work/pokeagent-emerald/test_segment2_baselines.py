"""Keyless tests for the source-derived Emerald segment-two baselines."""

import argparse
import json
import random
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

if sys.version_info < (3, 12):
    print("SKIP (missing prerequisite: Python >= 3.12)")
    raise SystemExit(8)

sys.path.insert(0, str(Path(__file__).resolve().parent))
import live_segment  # noqa: E402
import power_mwu  # noqa: E402
from segment2_baselines import (  # noqa: E402
    derive_segment_spec,
    _position,
    goal_reached,
    sample_state_blind_buttons,
    setup_position,
)


class SegmentTwoBaselines(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = derive_segment_spec(
            Path(__file__).with_name("states") / "emerald-boot.jsonl"
        )

    def test_segment_is_derived_from_recorded_reversible_transitions(self):
        self.assertEqual(self.spec["base_position"], {"x": 2, "y": 2})
        self.assertEqual(self.spec["left_position"], {"x": 1, "y": 2})
        self.assertEqual(self.spec["right_position"], {"x": 2, "y": 2})
        self.assertEqual(self.spec["evidence_rows"], [[299, "LEFT"], [303, "RIGHT"]])

    def test_seed_setup_alternates_the_observed_positions(self):
        self.assertEqual(setup_position(self.spec, 0), {"x": 2, "y": 2})
        self.assertEqual(setup_position(self.spec, 1), {"x": 1, "y": 2})
        self.assertEqual(setup_position(self.spec, 79), {"x": 1, "y": 2})

    def test_setup_replays_recorded_trace_to_each_position(self):
        self.assertEqual(self.spec["setup_to_left"][-1], "LEFT")
        self.assertEqual(self.spec["setup_to_base"][-1], "A")
        self.assertEqual(
            len(self.spec["setup_to_left"]), len(self.spec["setup_to_base"]) + 1
        )

    def test_position_accepts_the_runtime_compact_state(self):
        self.assertEqual(_position({"position": {"x": 2, "y": 2}}), {"x": 2, "y": 2})

    def test_goal_is_a_position_change_from_the_episode_start(self):
        self.assertFalse(goal_reached({"x": 2, "y": 2}, {"x": 2, "y": 2}))
        self.assertTrue(goal_reached({"x": 2, "y": 2}, {"x": 1, "y": 2}))
        self.assertTrue(goal_reached({"x": 1, "y": 2}, {"x": 2, "y": 2}))

    def test_state_blind_sampling_is_seeded_and_uses_segment_one_pool(self):
        rows = [
            json.loads(line)
            for line in (
                Path(__file__).with_name("live-results.jsonl").read_text().splitlines()
            )
            if line.strip()
        ]
        pool = [row["button"] for row in rows]
        first = sample_state_blind_buttons(random.Random(0), pool, 80)
        second = sample_state_blind_buttons(random.Random(0), pool, 80)
        self.assertEqual(first, second)
        self.assertEqual(len(first), 80)
        self.assertTrue(set(first) <= set(pool))

    def test_live_receipt_records_key_status(self):
        macro = {
            "kind": "macro",
            "code_sha256": "0" * 64,
            "recorded_at_utc": "2026-09-25T00:00:00+00:00",
            "seed": 0,
            "macro_index": 0,
            "button": "RIGHT",
            "probabilities": {button: 1 / 11 for button in live_segment.LEGAL_INPUTS},
            "input_tokens": 1,
            "model": "jev-1.13.0",
            "latency_ms": 1,
            "state_bytes": 1,
            "before": {"location": "MOVING_VAN", "position": {"x": 2, "y": 2}},
            "after": {"location": "LITTLEROOT TOWN", "position": {"x": 4, "y": 1}},
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scratch = root / "scratch"
            scratch.mkdir()
            (scratch / "seed-000.jsonl").write_text(json.dumps(macro) + "\n")
            args = argparse.Namespace(
                output=str(root / "rows.jsonl"),
                receipt=str(root / "receipt.md"),
                scratch=str(scratch),
                seeds=1,
                cap=1,
                start_seed=0,
                end_seed=1,
                rom="unused.gba",
            )
            with patch.object(
                live_segment.subprocess,
                "run",
                return_value=subprocess.CompletedProcess([], 0),
            ):
                self.assertEqual(live_segment.parent(args), 0)
            body = (
                (root / "receipt.md")
                .read_text()
                .split("```json\n", 1)[1]
                .split("\n```", 1)[0]
            )
            self.assertEqual(json.loads(body)["key_status"], "OK")

    def test_power_loader_selects_state_blind_rows(self):
        loader = getattr(power_mwu, "load_policy", None)
        self.assertIsNotNone(loader)
        values = loader(
            Path(__file__).with_name("state-blind-results.jsonl"),
            "state_blind",
            500,
        )
        self.assertEqual(len(values), 80)
        self.assertTrue(all(value >= 1 for value, _ in values))


if __name__ == "__main__":
    unittest.main()
