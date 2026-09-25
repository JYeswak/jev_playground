"""Offline tests for scripts/row-provenance-check.py (jev-b0b4)."""

from __future__ import annotations

import json
import hashlib
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
AFTER = "2026-09-25T03:01:00-0600"
BEFORE = "2026-09-25T02:59:00-0600"


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
        (self.repo / "scripts").mkdir()

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def install(
        self, fixture: str, commit_date: str, filename: str | None = None
    ) -> None:
        relative = Path("work/rows") / (filename or fixture)
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

    def write_exemption(self, relative: str, digest: str) -> None:
        (self.repo / "scripts" / "row-provenance-exempt.tsv").write_text(
            "path\tsha256\treason\n" f"{relative}\t{digest}\tlegacy test fixture\n",
            encoding="utf-8",
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

    def test_matching_exemption_skips_legacy_file_and_reports_count(self) -> None:
        self.install("missing-hash.jsonl", AFTER, filename="legacy.jsonl")
        path = self.repo / "work" / "rows" / "legacy.jsonl"
        self.write_exemption(
            "work/rows/legacy.jsonl", hashlib.sha256(path.read_bytes()).hexdigest()
        )
        result = self.run_checker()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("exempted 1 file", result.stdout)

    def test_changed_exempted_file_fails_hash_pin(self) -> None:
        self.install("missing-hash.jsonl", AFTER, filename="legacy.jsonl")
        path = self.repo / "work" / "rows" / "legacy.jsonl"
        self.write_exemption(
            "work/rows/legacy.jsonl", hashlib.sha256(path.read_bytes()).hexdigest()
        )
        path.write_bytes(path.read_bytes() + b"\n")
        result = self.run_checker()
        self.assertEqual(result.returncode, 1)
        self.assertIn("exemption sha256 mismatch", result.stderr)

    def test_unlisted_legacy_file_still_fails(self) -> None:
        self.install("missing-hash.jsonl", AFTER, filename="legacy.jsonl")
        result = self.run_checker()
        self.assertEqual(result.returncode, 1)
        self.assertIn("work/rows/legacy.jsonl", result.stderr)
        self.assertIn("code_sha256 or run_py_sha256", result.stderr)

    def test_decision_log_with_hash_and_timestamp_passes(self) -> None:
        self.install("decision-pass.jsonl", AFTER)
        result = self.run_checker()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("checked 1 experiment row file", result.stdout)
        self.assertIn("decision logs 1", result.stdout)

    def test_decision_log_missing_hash_fails_with_file_and_row(self) -> None:
        self.install("decision-missing-hash.jsonl", AFTER)
        result = self.run_checker()
        self.assertEqual(result.returncode, 1)
        self.assertIn("work/rows/decision-missing-hash.jsonl", result.stderr)
        self.assertIn("row 1", result.stderr)
        self.assertIn("code_sha256 or run_py_sha256", result.stderr)

    def test_decision_log_before_cutoff_is_skipped(self) -> None:
        self.install("decision-missing-hash.jsonl", BEFORE)
        result = self.run_checker()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("decision logs 0", result.stdout)

    def test_decision_log_exemption_pins_legacy_bytes(self) -> None:
        self.install(
            "decision-missing-hash.jsonl", AFTER, filename="legacy-decisions.jsonl"
        )
        path = self.repo / "work" / "rows" / "legacy-decisions.jsonl"
        self.write_exemption(
            "work/rows/legacy-decisions.jsonl",
            hashlib.sha256(path.read_bytes()).hexdigest(),
        )
        result = self.run_checker()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("decision logs exempted 1", result.stdout)

    def test_options_decision_missing_hash_fails(self) -> None:
        self.install("decision-options-missing-hash.jsonl", AFTER)
        result = self.run_checker()
        self.assertEqual(result.returncode, 1)
        self.assertIn("decision-options-missing-hash.jsonl", result.stderr)
        self.assertIn("row 1", result.stderr)
        self.assertIn("code_sha256 or run_py_sha256", result.stderr)

    def test_checker_skips_its_own_fixture_directory(self) -> None:
        relative = Path("work/row-provenance-check/fixtures/future-bad.jsonl")
        destination = self.repo / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps({"chosen": "move tackle", "candidates": ["move tackle"]}) + "\n",
            encoding="utf-8",
        )
        env = os.environ.copy()
        env["GIT_AUTHOR_DATE"] = AFTER
        env["GIT_COMMITTER_DATE"] = AFTER
        subprocess.run(
            ["git", "add", "--", str(relative)],
            cwd=self.repo,
            check=True,
            timeout=30,
        )
        subprocess.run(
            ["git", "commit", "-q", "-m", "future fixture"],
            cwd=self.repo,
            env=env,
            check=True,
            timeout=30,
        )
        result = self.run_checker()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("checked 0 experiment row file", result.stdout)


if __name__ == "__main__":
    unittest.main()
