#!/usr/bin/env python3
"""Keyless contract tests for scripts/arm-sanity.py."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "arm-sanity.py"
POKE_R3 = (
    ROOT
    / "work/loss-depth/pokejev-components/decisions-abyssal-leaf-code-leaf-c-r3-code.jsonl"
)
MIX_V1 = (
    ROOT
    / "work/loss-depth/pokejev-components/battle/stage-b/decisions-abyssal-mix-v1.jsonl"
)
MIX_V1_CONTROL = (
    ROOT
    / "work/loss-depth/pokejev-components/battle/stage-b/decisions-abyssal-mix-v1-control.jsonl"
)
MINIWOB_BAD = (
    ROOT
    / "work/miniwob-jev/rows/miniwob-jev-v3-contaminated-smoke-quoted-isolated-rerun.s0.jsonl"
)
MINIWOB_GOOD = (
    ROOT
    / "work/miniwob-jev/rows/miniwob-jev-v3-contaminated-smoke-quoted-exact.s0.jsonl"
)


class ArmSanityContract(unittest.TestCase):
    def run_check(self, arm, reference, *extra):
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--arm",
                str(arm),
                "--reference",
                str(reference),
                *extra,
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )

    def test_pokejev_r3_switch_mix_is_rejected(self):
        result = self.run_check(POKE_R3, MIX_V1)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("switch", result.stdout.lower())

    def test_pokejev_mix_control_matches_reference(self):
        result = self.run_check(MIX_V1, MIX_V1_CONTROL)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_miniwob_c7651c4_window_type_mix_is_rejected(self):
        result = self.run_check(MINIWOB_BAD, MINIWOB_GOOD, "--min-rows", "10")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("type", result.stdout.lower())

    def test_single_type_offers_do_not_count_as_eligible(self):
        result = self.run_check(MIX_V1, MIX_V1, "--min-rows", "3000")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("eligible rows arm=2217", result.stdout)

    def test_too_few_eligible_rows_is_not_run(self):
        result = self.run_check(POKE_R3, MIX_V1, "--min-rows", "6000")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("NOT_RUN", result.stdout)


if __name__ == "__main__":
    unittest.main()
