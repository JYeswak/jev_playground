"""Planted negative: an attempt before its phase must panic.

A function that returns ready instead fails this test.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from phase_gate import AttemptPanic, composed_phase_gate


class PhaseGateTest(unittest.TestCase):
    def test_ready_attempt_returns(self):
        self.assertEqual(composed_phase_gate(2, 2), "ready")

    def test_early_attempt_panics(self):
        with self.assertRaises(AttemptPanic):
            composed_phase_gate(2, 0)


if __name__ == "__main__":
    unittest.main()
