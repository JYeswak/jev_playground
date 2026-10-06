from __future__ import annotations

import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent))
telemetry = importlib.import_module("telemetry")

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "family_cost_measure", Path(__file__).with_name("measure.py")
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load measurement module")
measure = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(measure)


class MeasureEvidenceTests(unittest.TestCase):
    def test_bead_ids_match_issue_tokens_not_embedded_words_or_model_versions(
        self,
    ) -> None:
        self.assertEqual(
            measure._bead_ids(
                "jev-ab12 jev-ab12.3 (notjev-cd34) jev-1.13.0 jev-n1-result-family-bakeoff-fcqw."
            ),
            ["jev-ab12", "jev-ab12.3", "jev-n1-result-family-bakeoff-fcqw"],
        )

    def test_missing_family_start_commit_refuses_to_measure(self) -> None:
        with (
            patch.object(measure, "_commits_for_path", return_value=[]),
            self.assertRaises(
                measure.MeasurementError,
            ) as caught,
        ):
            measure._family_candidates(ROOT)
        self.assertIn("contract start commit missing", str(caught.exception))

    def test_missing_ship_commit_refuses_to_measure(self) -> None:
        def commits_for_path(root: Path, path: str) -> list[tuple[str, int]]:
            return [("a" * 40, 1)] if path.startswith("kit/contracts/") else []

        with (
            patch.object(measure, "_commits_for_path", side_effect=commits_for_path),
            self.assertRaises(
                measure.MeasurementError,
            ) as caught,
        ):
            measure.measure(ROOT, families=3)
        self.assertIn("only 0", str(caught.exception))

    def test_missing_spend_log_refuses_instead_of_reporting_zero(self) -> None:
        with (
            patch.object(telemetry, "_session_files", return_value=[]),
            self.assertRaises(
                measure.MeasurementError,
            ) as caught,
        ):
            measure._session_metrics(
                ["jev-ab12"],
                1,
                2,
                root=ROOT,
                home=ROOT,
                state=ROOT / "missing-state",
            )
        self.assertIn("no attributable omp session logs", str(caught.exception))

    def test_late_preregistration_is_rejected_by_git_ancestry(self) -> None:
        commits = subprocess.run(
            ["git", "rev-list", "--max-count=2", "HEAD"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
            timeout=20,
        ).stdout.splitlines()
        head, parent = commits
        candidates = [
            {"family": "first", "start_sha": head},
            {"family": "second", "start_sha": parent},
        ]
        with (
            patch.object(measure, "_commits_for_path", return_value=[(head, 2)]),
            self.assertRaises(
                measure.MeasurementError,
            ) as caught,
        ):
            measure._verify_prereg(ROOT, candidates)
        self.assertIn(
            "after the second family's contract commit", str(caught.exception)
        )


if __name__ == "__main__":
    unittest.main()
