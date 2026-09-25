"""Keyless tests for the preregistration reachability gate."""

from __future__ import annotations

import json
import subprocess  # nosec B404 - fixed local test script only
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "bar-reachable.py"
FLOOR = ROOT / "work" / "osw-bestofn" / "floor_receipt.json"
MANIFEST = ROOT / "work" / "osw-bestofn" / "heldout_valid_slice.json"
USED_ROWS = ROOT / "work" / "osw-bestofn" / "live_rows_r3.jsonl"
R112_SCORE = ROOT / "work" / "osw-bestofn" / "live_score_check_r3.json"
PREFLIGHT = ROOT / "work" / "osw-bestofn" / "r112_retry_preflight.json"


def run_checker(*args: str) -> tuple[int, dict]:
    completed = subprocess.run(  # nosec B603 - fixed argv and bounded timeout
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return completed.returncode, json.JSONDecoder().decode(completed.stdout)


class BarReachabilityTests(unittest.TestCase):
    def test_jev_jjwt_split_is_refused_before_spend(self):
        code, receipt = run_checker(
            "--floor",
            str(FLOOR),
            "--preflight",
            str(PREFLIGHT),
            "--manifest",
            str(MANIFEST),
            "--used-rows",
            str(USED_ROWS),
        )
        self.assertEqual(code, 1)
        self.assertEqual(receipt["status"], "UNREACHABLE")
        self.assertEqual(receipt["tasks"], 24)
        self.assertEqual(receipt["comparator_exact"], 22)
        self.assertEqual(receipt["max_discordant_wins"], 2)
        self.assertEqual(receipt["minimum_attainable_p"], 0.5)

    def test_r112_split_has_room_beyond_observed_discordance(self):
        code, receipt = run_checker(
            "--score-receipt",
            str(R112_SCORE),
            "--floor",
            str(FLOOR),
            "--used-rows",
            str(USED_ROWS),
        )
        self.assertEqual(code, 0)
        self.assertEqual(receipt["status"], "REACHABLE")
        self.assertEqual(receipt["tasks"], 337)
        self.assertEqual(receipt["comparator_exact"], 139)
        self.assertEqual(receipt["max_discordant_wins"], 74)
        self.assertLess(receipt["minimum_attainable_p"], 0.05)
        self.assertEqual(receipt["observed"]["observed_b"], 2)
        self.assertEqual(receipt["observed"]["observed_c"], 8)

    def test_rate_bar_uses_perfect_score_wilson_bound(self):
        code, receipt = run_checker(
            "--mode",
            "rate",
            "--trials",
            "337",
            "--threshold",
            "0.99",
        )
        self.assertEqual(code, 1)
        self.assertEqual(receipt["status"], "UNREACHABLE")
        self.assertLess(receipt["wilson_lower_bound_95"], 0.99)


if __name__ == "__main__":
    unittest.main()
