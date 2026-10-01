#!/usr/bin/env python3
"""Keyless dry-run contract for the post-reset comparator-only resume."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIVE = ROOT / "work/jev-oioo/live.mjs"
# The pre-resume rows, captured from 5caf9f93^:work/jev-oioo/live-results.jsonl. The live file was
# rewritten in place when the resume ran (5caf9f93, 821 comparator answers filled), so reading it
# tested the post-resume state and failed 1 != 821 in CI from then on.
RESULTS = ROOT / "work/jev-oioo/fixture-live-results-pre-resume.jsonl"
RESET = "2026-09-28T00:00:00Z"


def run_live(output: Path, *, now: str, fake_429: bool = False, plant: bool = False):
    env = os.environ.copy()
    env.update(
        {
            "JEV_OIOO_OUT": str(output),
            "JEV_OIOO_COMPARATOR_ONLY": "1",
            "JEV_OIOO_DRY_RUN": "1",
            "JEV_OIOO_NOW": now,
        }
    )
    if fake_429:
        env["JEV_OIOO_FAKE_429"] = "1"
    if plant:
        env["JEV_OIOO_PLANT_SELECT"] = "1"
    else:
        env.pop("JEV_OIOO_PLANT_SELECT", None)
    return subprocess.run(
        ["node", "--experimental-strip-types", str(LIVE)],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def payload(result):
    return json.loads(result.stdout.strip().splitlines()[-1])


class ComparatorResumeTest(unittest.TestCase):
    def copy_results(self, directory: str) -> Path:
        target = Path(directory) / "resume.jsonl"
        target.write_bytes(RESULTS.read_bytes())
        self.assertEqual(len(target.read_text().splitlines()), 907)
        return target

    def test_before_reset_refuses_without_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            output = self.copy_results(directory)
            before = output.read_bytes()
            result = run_live(output, now="2026-09-27T12:00:00Z")
            self.assertEqual(result.returncode, 2)
            self.assertEqual(payload(result)["status"], "NOT_RUN")
            self.assertEqual(payload(result)["selected"], 821)
            self.assertEqual(payload(result)["sent"], 0)
            self.assertEqual(output.read_bytes(), before)

    def test_fake_429_stops_without_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            output = self.copy_results(directory)
            before = output.read_bytes()
            result = run_live(output, now="2026-09-28T00:00:01Z", fake_429=True)
            self.assertEqual(result.returncode, 0)
            body = payload(result)
            self.assertEqual(body["selected"], 821)
            self.assertEqual(body["sent"], 1)
            self.assertTrue(body["stopped"])
            self.assertEqual(output.read_bytes(), before)

    def test_planted_answered_row_would_fail_selection_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            output = self.copy_results(directory)
            result = run_live(
                output, now="2026-09-28T00:00:01Z", fake_429=True, plant=True
            )
            self.assertEqual(result.returncode, 0)
            with self.assertRaises(AssertionError):
                self.assertEqual(payload(result)["selected"], 821)


if __name__ == "__main__":
    unittest.main()
