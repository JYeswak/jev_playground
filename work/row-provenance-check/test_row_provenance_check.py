"""Offline tests for scripts/row-provenance-check.py (jev-b0b4)."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SCRIPT = ROOT / "scripts" / "row-provenance-check.py"
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
        self,
        fixture: str,
        commit_date: str,
        filename: str | None = None,
        *,
        format_as_array: bool = False,
        raw_bytes: bytes | None = None,
    ) -> None:
        relative = Path("work/rows") / (filename or fixture)
        destination = self.repo / relative
        if raw_bytes is not None:
            content: str | bytes = raw_bytes
        else:
            rows = [
                json.JSONDecoder().decode(line)
                for line in (FIXTURES / fixture).read_text().splitlines()
            ]
            if fixture == "missing-hash.jsonl":
                rows[-1].pop("code_sha256", None)
            if fixture == "missing-timestamp.jsonl":
                rows[-1].pop("finished_utc", None)
            if format_as_array:
                content = json.dumps(rows) + "\n"
            else:
                content = "\n".join(json.dumps(row) for row in rows) + "\n"
        if isinstance(content, bytes):
            destination.write_bytes(content)
        else:
            destination.write_text(content, encoding="utf-8")
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

    def write_exemption(
        self,
        relative: str,
        digest: str,
        bead: str = "jev-b0b4",
        mode: str = "provenance",
    ) -> None:
        path = self.repo / "scripts" / "row-provenance-exempt.tsv"
        path.write_text(
            "path\tsha256\treason\tbead\tmode\n"
            f"{relative}\t{digest}\tlegacy test fixture\t{bead}\t{mode}\n",
            encoding="utf-8",
        )
        subprocess.run(
            ["git", "add", "--", "scripts/row-provenance-exempt.tsv"],
            cwd=self.repo,
            check=True,
            timeout=30,
        )
        subprocess.run(
            ["git", "commit", "-q", "-m", "add test exemption"],
            cwd=self.repo,
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

    def test_single_line_json_array_is_rejected_as_jsonl(self) -> None:
        self.install("pass.jsonl", AFTER, format_as_array=True)
        result = self.run_checker()
        self.assertEqual(result.returncode, 1)
        self.assertIn("work/rows/pass.jsonl", result.stderr)
        self.assertIn("JSON array", result.stderr)

    def test_exemption_does_not_skip_jsonl_shape_validation(self) -> None:
        self.install(
            "missing-hash.jsonl",
            AFTER,
            filename="legacy.jsonl",
            format_as_array=True,
        )
        path = self.repo / "work" / "rows" / "legacy.jsonl"
        self.write_exemption(
            "work/rows/legacy.jsonl", hashlib.sha256(path.read_bytes()).hexdigest()
        )
        result = self.run_checker()
        self.assertEqual(result.returncode, 1)
        self.assertIn("JSON array", result.stderr)

    def test_hash_pinned_raw_fixture_allows_malformed_lines(self) -> None:
        relative = "work/thinking-duel-hard/tasks/t03/sample.jsonl"
        raw = (ROOT / relative).read_bytes()
        self.install(
            "pass.jsonl",
            AFTER,
            filename="raw-fixture.jsonl",
            raw_bytes=raw,
        )
        before_exemption = self.run_checker()
        self.assertEqual(before_exemption.returncode, 1)
        self.assertIn("invalid JSON", before_exemption.stderr)
        self.write_exemption(
            "work/rows/raw-fixture.jsonl",
            hashlib.sha256(raw).hexdigest(),
            bead="jev-77ow",
            mode="raw-fixture",
        )
        result = self.run_checker()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("exempted 1 file", result.stdout)
        fixture = self.repo / "work" / "rows" / "raw-fixture.jsonl"
        mutated = bytearray(raw)
        mutated[-1] ^= 1
        fixture.write_bytes(mutated)
        subprocess.run(
            ["git", "add", "--", "work/rows/raw-fixture.jsonl"],
            cwd=self.repo,
            check=True,
            timeout=30,
        )
        subprocess.run(
            ["git", "commit", "-q", "-m", "mutate raw fixture byte"],
            cwd=self.repo,
            check=True,
            timeout=30,
        )
        changed = self.run_checker()
        self.assertEqual(changed.returncode, 1)
        self.assertIn("exemption sha256 mismatch", changed.stderr)

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

    def test_untracked_experiment_file_is_ignored(self) -> None:
        self.install("non-experiment.jsonl", AFTER, filename="baseline.jsonl")
        path = self.repo / "work" / "rows" / "untracked.jsonl"
        path.write_text(
            (FIXTURES / "missing-hash.jsonl").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        result = self.run_checker()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("checked 0 experiment row file", result.stdout)

    def test_uncommitted_edit_does_not_change_committed_rows(self) -> None:
        self.install("pass.jsonl", AFTER)
        path = self.repo / "work" / "rows" / "pass.jsonl"
        path.write_text(
            (FIXTURES / "missing-hash.jsonl").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        result = self.run_checker()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("checked 1 experiment row file", result.stdout)

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
        original = bytearray(path.read_bytes())
        self.write_exemption(
            "work/rows/legacy.jsonl", hashlib.sha256(original).hexdigest()
        )
        index = original.index(b'"code_sha256"') + 2
        original[index] = ord("x")
        path.write_bytes(original)
        subprocess.run(
            ["git", "add", "--", "work/rows/legacy.jsonl"],
            cwd=self.repo,
            check=True,
            timeout=30,
        )
        subprocess.run(
            ["git", "commit", "-q", "-m", "change one exempt byte"],
            cwd=self.repo,
            check=True,
            timeout=30,
        )
        result = self.run_checker()
        self.assertEqual(result.returncode, 1)
        self.assertIn("exemption sha256 mismatch", result.stderr)

    def test_uncommitted_exemption_cannot_bypass_checker(self) -> None:
        self.install("missing-hash.jsonl", AFTER, filename="legacy.jsonl")
        path = self.repo / "work" / "rows" / "legacy.jsonl"
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        (self.repo / "scripts" / "row-provenance-exempt.tsv").write_text(
            "path\tsha256\treason\tbead\tmode\n"
            f"work/rows/legacy.jsonl\t{digest}\tlocal only\tjev-b0b4\tprovenance\n",
            encoding="utf-8",
        )
        result = self.run_checker()
        self.assertEqual(result.returncode, 1)
        self.assertIn("code_sha256 or run_py_sha256", result.stderr)

    def test_exemption_without_bead_is_rejected(self) -> None:
        self.install("missing-hash.jsonl", AFTER, filename="legacy.jsonl")
        path = self.repo / "work" / "rows" / "legacy.jsonl"
        self.write_exemption(
            "work/rows/legacy.jsonl",
            hashlib.sha256(path.read_bytes()).hexdigest(),
            bead="",
        )
        result = self.run_checker()
        self.assertEqual(result.returncode, 2)
        self.assertIn("row-provenance-exempt.tsv line 2 is malformed", result.stderr)

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

    def commit_raw(self, name: str, text: str) -> None:
        relative = Path("work/rows") / name
        (self.repo / relative).write_text(text, encoding="utf-8")
        env = os.environ.copy()
        env["GIT_AUTHOR_DATE"] = AFTER
        env["GIT_COMMITTER_DATE"] = AFTER
        subprocess.run(
            ["git", "add", "--", str(relative)], cwd=self.repo, check=True, timeout=30
        )
        subprocess.run(
            ["git", "commit", "-q", "-m", name],
            cwd=self.repo,
            env=env,
            check=True,
            timeout=30,
        )

    def test_a_file_whose_first_line_is_not_json_fails(self) -> None:
        # The shape db038a0 committed: rows joined by the two characters backslash-n on one line.
        good = json.dumps(
            {
                "won": 1,
                "code_sha256": "a" * 64,
                "recorded_at_utc": "2026-09-25T12:00:00Z",
            }
        )
        self.commit_raw("joined.jsonl", good + "\\n" + good + "\n")
        result = self.run_checker()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("work/rows/joined.jsonl row 1 invalid JSON", result.stderr)

    def test_a_bare_jev_answer_row_needs_provenance(self) -> None:
        # Shape of work/pokeagent-emerald/live-results.jsonl and work/osw-bestofn/live_rows_r3.jsonl.
        answer = {
            "seed": 0,
            "button": "RIGHT",
            "probabilities": {"RIGHT": 0.6, "UP": 0.4},
            "model": "jev-1.13.0",
        }
        self.commit_raw("answers.jsonl", json.dumps(answer) + "\n")
        result = self.run_checker()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn(
            "work/rows/answers.jsonl row 1 missing code_sha256 or run_py_sha256; UTC timestamp",
            result.stderr,
        )
        answer.update(code_sha256="b" * 64, recorded_at_utc="2026-09-25T12:00:00Z")
        self.commit_raw("answers.jsonl", json.dumps(answer) + "\n")
        self.assertEqual(self.run_checker().returncode, 0)


if __name__ == "__main__":
    unittest.main()
