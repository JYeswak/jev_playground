#!/usr/bin/env python3
"""Keyless tests for scripts/key-status.py."""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "key-status.py"
PROBE = ROOT / "work/key-status/live_jev_guard_probe.py"
REVOKED_KEY = "fake-revoked-key-for-tests-only"
OTHER_KEY = "fake-other-key-for-tests-only"


class KeyStatusTests(unittest.TestCase):
    def run_status(self, key: str | None, revoked_file: Path):
        env = os.environ.copy()
        env.pop("TYPESAFE_API_KEY", None)
        if key is not None:
            env["TYPESAFE_API_KEY"] = key
        env["KEY_STATUS_REVOKED_FILE"] = str(revoked_file)
        return subprocess.run(
            ["python3", str(SCRIPT)],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )

    def test_revoked_fake_key_exits_three_without_emitting_key(self):
        with tempfile.TemporaryDirectory() as temp:
            revoked = Path(temp) / "revoked.tsv"
            fingerprint = hashlib.sha256(REVOKED_KEY.encode()).hexdigest()[:16]
            revoked.write_text(f"{fingerprint}\t2026-09-25\ttest leaked key\n")
            result = self.run_status(REVOKED_KEY, revoked)
        self.assertEqual(result.returncode, 3)
        self.assertIn("KEY: REVOKED", result.stdout)
        self.assertNotIn(REVOKED_KEY, result.stdout + result.stderr)
        self.assertNotIn(
            hashlib.sha256(REVOKED_KEY.encode()).hexdigest(),
            result.stdout + result.stderr,
        )

    def test_other_fake_key_is_ok(self):
        with tempfile.TemporaryDirectory() as temp:
            revoked = Path(temp) / "revoked.tsv"
            fingerprint = hashlib.sha256(REVOKED_KEY.encode()).hexdigest()[:16]
            revoked.write_text(f"{fingerprint}\t2026-09-25\ttest leaked key\n")
            result = self.run_status(OTHER_KEY, revoked)
        self.assertEqual(result.returncode, 0)
        self.assertIn("KEY: OK", result.stdout)
        self.assertNotIn(OTHER_KEY, result.stdout + result.stderr)

    def test_unset_key_is_not_run(self):
        with tempfile.TemporaryDirectory() as temp:
            result = self.run_status(None, Path(temp) / "empty.tsv")
        self.assertEqual(result.returncode, 2)
        self.assertIn("KEY: NOT_RUN", result.stdout)

    def write_revoked(self, path: Path, key: str) -> None:
        fingerprint = hashlib.sha256(key.encode()).hexdigest()[:16]
        path.write_text(f"{fingerprint}\t2026-09-25\ttest leaked key\n")

    def runner_env(self, revoked: Path, key: str) -> dict[str, str]:
        env = os.environ.copy()
        env["TYPESAFE_API_KEY"] = key
        env["KEY_STATUS_REVOKED_FILE"] = str(revoked)
        return env

    def test_miniwob_live_asker_refuses_revoked_fake_key(self):
        with tempfile.TemporaryDirectory() as temp:
            revoked = Path(temp) / "revoked.tsv"
            self.write_revoked(revoked, REVOKED_KEY)
            python = sys.executable
            result = subprocess.run(
                [python, str(PROBE)],
                cwd=ROOT,
                env=self.runner_env(revoked, REVOKED_KEY),
                capture_output=True,
                text=True,
                timeout=30,
            )
        if "No module named 'gymnasium'" in result.stderr:
            self.skipTest("prerequisite: gymnasium unavailable for MiniWoB runner")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("KEY: REVOKED", result.stderr)
        self.assertNotIn(REVOKED_KEY, result.stdout + result.stderr)

    def test_bestofn_live_runner_refuses_before_requests(self):
        with tempfile.TemporaryDirectory() as temp:
            revoked = Path(temp) / "revoked.tsv"
            state = Path(temp) / "empty.jsonl"
            output = Path(temp) / "receipt.json"
            state.write_text("")
            self.write_revoked(revoked, REVOKED_KEY)
            env = self.runner_env(revoked, REVOKED_KEY)
            env.update(
                {
                    "OSW_STATE_FILE": str(state),
                    "OSW_FLOOR_RECEIPT": str(
                        ROOT / "work/osw-bestofn/floor_receipt.json"
                    ),
                    "OSW_LIVE_RECEIPT": str(output),
                }
            )
            result = subprocess.run(
                [
                    "node",
                    "--experimental-strip-types",
                    "work/osw-bestofn/live_select.mjs",
                ],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                timeout=30,
            )
        self.assertEqual(result.returncode, 3)
        self.assertIn("KEY: REVOKED", result.stdout + result.stderr)
        self.assertNotIn(REVOKED_KEY, result.stdout + result.stderr)

    def test_gate_question_live_runner_refuses_before_requests(self):
        with tempfile.TemporaryDirectory() as temp:
            revoked = Path(temp) / "revoked.tsv"
            self.write_revoked(revoked, REVOKED_KEY)
            result = subprocess.run(
                [
                    "node",
                    "--experimental-strip-types",
                    "work/gate-question-gap/live-pass-5.mjs",
                    "--live",
                ],
                cwd=ROOT,
                env=self.runner_env(revoked, REVOKED_KEY),
                capture_output=True,
                text=True,
                timeout=30,
            )
        self.assertEqual(result.returncode, 3)
        self.assertIn("KEY: REVOKED", result.stdout + result.stderr)
        self.assertNotIn(REVOKED_KEY, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
