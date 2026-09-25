#!/usr/bin/env python3
"""Keyless tests for the post-rotation MiniWoB v3 run sheet."""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHEET = ROOT / "work/miniwob-jev/run-after-rotation.sh"
FAKE_KEY = f"{'fake'}-{'run'}-{'sheet'}-{'key'}"


class RotationSheetTests(unittest.TestCase):
    def run_sheet(self, root: Path, *args: str, revoked: Path | None = None):
        env = os.environ.copy()
        env["TYPESAFE_API_KEY"] = FAKE_KEY
        default_venv = (
            Path(os.sep) / "tmp" / "jev-miniwob-jev" / "venv" / "bin" / "python"
        )
        candidate_value = os.environ.get("MINIWOB_TEST_VENV")
        candidate = Path(candidate_value) if candidate_value else default_venv
        env["PYTHON"] = str(candidate) if candidate.exists() else sys.executable
        if revoked is not None:
            env["KEY_STATUS_REVOKED_FILE"] = str(revoked)
        return subprocess.run(
            ["bash", str(SHEET), "--fake", "--run-root", str(root), *args],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=120,
        )

    def test_fake_sheet_runs_two_episodes_per_step(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            result = self.run_sheet(root, "--steps", "quoted,date_time")
            if (
                result.returncode != 0
                and "No module named 'gymnasium'" in result.stderr
            ):
                self.skipTest("prerequisite: gymnasium unavailable for rotation sheet")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for step in ("quoted", "date_time"):
                rows = root.joinpath(f"{step}.jsonl").read_text().splitlines()
                self.assertEqual(len(rows), 2, step)
                self.assertIn("code_sha256", rows[0])
                self.assertIn("started_utc", rows[0])

    def test_revoked_fake_key_stops_at_step_one_before_rows(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            revoked = root / "revoked.tsv"
            fingerprint = hashlib.sha256(FAKE_KEY.encode()).hexdigest()[:16]
            revoked.write_text(f"{fingerprint}\t2026-09-25\ttest revoked\n")
            result = self.run_sheet(
                root, "--steps", "quoted,date_time", revoked=revoked
            )
            self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
            self.assertIn("KEY: REVOKED", result.stdout + result.stderr)
            self.assertFalse(root.joinpath("quoted.jsonl").exists())


if __name__ == "__main__":
    unittest.main()
