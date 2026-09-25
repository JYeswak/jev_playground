"""Offline tests for state receipt size statistics."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

if sys.version_info < (3, 12):
    print("SKIP (missing prerequisite: Python >= 3.12)")
    raise SystemExit(8)

from capture_state import _stats  # noqa: E402


class StateStats(unittest.TestCase):
    def test_percentiles_sort_whole_rows_and_report_compact_state(self):
        rows = [
            {"state_bytes": 100, "state": {"n": "x"}, "state_text": "a"},
            {"state_bytes": 1000, "state": {"n": "x" * 10}, "state_text": "b"},
            {"state_bytes": 200, "state": {"n": "x" * 20}, "state_text": "c"},
            {"state_bytes": 300, "state": {"n": "x" * 30}, "state_text": "d"},
        ]

        result = _stats(rows)

        self.assertEqual(result["state_bytes"]["p50"], 250.0)
        self.assertEqual(result["state_bytes"]["p95"], 1000)
        self.assertEqual(result["compact_state_bytes"]["p50"], 23.0)
        self.assertEqual(result["compact_state_bytes"]["p95"], 38)


if __name__ == "__main__":
    unittest.main()
