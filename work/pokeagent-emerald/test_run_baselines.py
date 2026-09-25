"""Keyless tests for Emerald baseline policy sampling."""

import random
import sys
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch

if sys.version_info < (3, 12):
    print("SKIP (missing prerequisite: Python >= 3.12)")
    raise SystemExit(8)

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_baselines  # noqa: E402
from run_baselines import (  # noqa: E402
    load_pooled_buttons,
    sample_state_blind_buttons,
)


class StateBlindBaseline(unittest.TestCase):
    def test_pool_is_derived_from_committed_live_rows(self):
        path = Path(__file__).with_name("live-results.jsonl")
        buttons = load_pooled_buttons(path)
        self.assertEqual(len(buttons), 6449)
        self.assertEqual(
            Counter(buttons),
            Counter(
                {
                    "A": 531,
                    "B": 74,
                    "DOWN": 628,
                    "LEFT": 591,
                    "R": 67,
                    "RIGHT": 1872,
                    "SELECT": 20,
                    "START": 293,
                    "UP": 1649,
                    "WAIT": 724,
                }
            ),
        )

    def test_sampling_is_seeded_and_uses_only_pooled_buttons(self):
        path = Path(__file__).with_name("live-results.jsonl")
        pool = load_pooled_buttons(path)
        first = sample_state_blind_buttons(random.Random(0), pool, 80)
        second = sample_state_blind_buttons(random.Random(0), pool, 80)
        self.assertEqual(first, second)
        self.assertEqual(len(first), 80)
        self.assertTrue(set(first) <= set(pool))

    def test_run_one_uses_state_blind_pool_for_each_macro(self):
        class FakeEnvironment:
            def __init__(self, *args, **kwargs):
                pass

            def initialize(self):
                pass

        start = {"location": "MOVING_VAN"}
        pressed: list[str] = []
        with (
            patch.object(run_baselines, "_boot_to_start", return_value=start),
            patch.object(run_baselines, "_state", return_value=start),
            patch.object(
                run_baselines,
                "_press",
                side_effect=lambda _env, button: pressed.append(button),
            ),
        ):
            row = run_baselines.run_one(
                FakeEnvironment,
                "unused.gba",
                "state_blind",
                0,
                8,
                [],
                ["RIGHT"] * 8,
            )

        self.assertEqual(pressed, ["RIGHT"] * 8)
        self.assertFalse(row["goal_reached"])


if __name__ == "__main__":
    unittest.main()
