"""Offline tests for scripts/row-provenance-check.py (jev-b0b4)."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SCRIPT = Path(
    os.environ.get("ROW_PROVENANCE_CHECK", ROOT / "scripts" / "row-provenance-check.py")
)
FIXTURES = HERE / "fixtures"
CUTOFF = "2026-09-25T09:00:00+0000"
AFTER = "2026-09-25T09:01:00+0000"
BEFORE = "2026-09-25T08:59:00+0000"


class RowProvenanceCheckerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.repo = Path(self.tempdir.name)
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True, timeout=30)
        subprocess.run(
            ["git", "config", "user.email", "tests@example.invalid"],
            cwd=self.repo,
            check=True,
            timeout=30,
        )
        subprocess.run(
            ["git", "config", "user.name", "row provenance tests"],
            cwd=self.repo,
            check=True,
            timeout=30,
        )
        subprocess.run(
            ["git", "config", "core.hooksPath", "/dev/null"],
            cwd=self.repo,
            check=True,
            timeout=30,
        )
        (self.repo / "work" / "rows").mkdir(parents=True)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def install(self, fixture: str, commit_date: str) -> None:
        relative = Path("work/rows") / fixture
        destination = self.repo / relative
        rows = [
            json.JSONDecoder().decode(line)
            for line in (FIXTURES / fixture).read_text().splitlines()
        ]
        if fixture == "missing-hash.jsonl":
            rows[-1].pop("code_sha256", None)
        if fixture == "missing-timestamp.jsonl":
            rows[-1].pop("finished_utc", None)
        destination.write_text(
            "\n".join(json.dumps(row) for row in rows) + "\n",
            encoding="utf-8",
        )
        env = os.environ.copy()
        env["GIT_AUTHOR_DATE"] = commit_date
        env["GIT_COMMITTER_DATE"] = commit_date
        subprocess.run(
            ["git", "add", "--", str(relative)],
            cwd=self.repo,
            check=True,
            timeout=30,
        )
        subprocess.run(
            ["git", "commit", "-q", "-m", f"fixture {fixture}"],
            cwd=self.repo,
            env=env,
            check=True,
            timeout=30,
        )

    def run_checker(self) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["JEV_REPO"] = str(self.repo)
        return subprocess.run(
            ["python3", str(SCRIPT)],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )

    def test_complete_experiment_file_passes_and_reports_count(self) -> None:
        self.install("pass.jsonl", AFTER)
        result = self.run_checker()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("checked 1 experiment row file", result.stdout)

    def test_missing_hash_fails_with_file_row_and_field(self) -> None:
        self.install("missing-hash.jsonl", AFTER)
        result = self.run_checker()
        self.assertEqual(result.returncode, 1)
        self.assertIn("work/rows/missing-hash.jsonl", result.stderr)
        self.assertIn("row 2", result.stderr)
        self.assertIn("code_sha256 or run_py_sha256", result.stderr)

    def test_missing_timestamp_fails_with_file_row_and_field(self) -> None:
        self.install("missing-timestamp.jsonl", AFTER)
        result = self.run_checker()
        self.assertEqual(result.returncode, 1)
        self.assertIn("work/rows/missing-timestamp.jsonl", result.stderr)
        self.assertIn("row 1", result.stderr)
        self.assertIn("UTC timestamp", result.stderr)

    def test_pre_cutoff_file_is_skipped(self) -> None:
        self.install("pre-cutoff.jsonl", BEFORE)
        result = self.run_checker()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("checked 0 experiment row", result.stdout)

    def test_non_experiment_jsonl_is_skipped(self) -> None:
        self.install("non-experiment.jsonl", AFTER)
        result = self.run_checker()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("checked 0 experiment row", result.stdout)


if __name__ == "__main__":
    unittest.main()
