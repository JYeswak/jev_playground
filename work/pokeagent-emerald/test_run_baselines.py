"""Keyless tests for Emerald baseline policy sampling."""

import random
import sys
import subprocess
import tempfile
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

    def test_receipt_refuses_child_error_and_null_final(self):
        writer = getattr(run_baselines, "write_receipt", None)
        self.assertIsNotNone(writer)
        invalid_rows = [
            {
                "policy": "state_blind",
                "seed": 0,
                "child_error": "exit_1",
                "final": None,
            }
        ]
        with tempfile.TemporaryDirectory() as directory:
            receipt = Path(directory) / "receipt.md"
            with self.assertRaises(ValueError):
                writer(receipt, invalid_rows, {"policy": "state_blind"})
            self.assertFalse(receipt.exists())

    def test_parent_refuses_child_error_without_output_or_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "rows.jsonl"
            receipt = Path(directory) / "receipt.md"
            argv = [
                "run_baselines.py",
                "--rom",
                "unused.gba",
                "--output",
                str(output),
                "--fixed-sequence",
                "0",
                "--random",
                "0",
                "--state-blind",
                "1",
                "--pooled-rows",
                str(Path(__file__).with_name("live-results.jsonl")),
                "--receipt",
                str(receipt),
                "--harness-sha",
                "harness",
                "--rom-sha1",
                "rom",
            ]
            failure = subprocess.CalledProcessError(
                1, ["child"], stderr="ModuleNotFoundError: pokemon_env"
            )
            with (
                patch.object(run_baselines.subprocess, "run", side_effect=failure),
                patch.object(sys, "argv", argv),
            ):
                self.assertEqual(run_baselines.main(), 2)
            self.assertFalse(output.exists())
            self.assertFalse(receipt.exists())


if __name__ == "__main__":
    unittest.main()
