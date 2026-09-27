#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check-omp-judge-drift.py"


class JudgeDriftTest(unittest.TestCase):
    def run_check(
        self, rows: list[dict[str, object]]
    ) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "usage.jsonl"
            path.write_text("".join(json.dumps(row) + "\n" for row in rows))
            return subprocess.run(
                [sys.executable, str(SCRIPT), str(path)],
                capture_output=True,
                text=True,
                check=False,
                timeout=30,
            )

    def test_matching_model_passes(self) -> None:
        result = self.run_check([{"model_id": "jev-1.13.0"}, {"model": "jev-1.13.0"}])
        self.assertEqual(result.returncode, 0)
        self.assertIn("judge model pinned", result.stdout)

    def test_model_drift_fails(self) -> None:
        result = self.run_check([{"model_id": "jev-latest"}])
        self.assertEqual(result.returncode, 1)
        self.assertIn("judge model drift", result.stderr)

    def test_missing_model_fails(self) -> None:
        result = self.run_check([{"usage": 1}])
        self.assertEqual(result.returncode, 1)
        self.assertIn("judge model drift", result.stderr)

    def test_planted_selftest_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "unused.jsonl", "--selftest"],
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("SELFTEST PASS", result.stdout)


if __name__ == "__main__":
    unittest.main()
