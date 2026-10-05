from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import score

TABLE = HERE.parent / "jev-nwo1-verdict.md"


class SmartStopScoreTest(unittest.TestCase):
    def test_committed_table_reproduces_frozen_verdict(self) -> None:
        result = score.summarize_table(TABLE.read_text(encoding="utf-8"))
        report = score.render_report(result)

        self.assertEqual(result["reasks"], 100)
        self.assertEqual(result["p_strict"], 0)
        self.assertEqual(result["p_loose"], 1)
        self.assertEqual(result["y"], 0)
        self.assertEqual(result["continued"], 0)
        self.assertEqual(result["verdict"], "(a)")
        self.assertIn("100 re-asks", report)
        self.assertIn("Y=0", report)
        self.assertIn("verdict=(a)", report)

    def test_planted_continuation_changes_reported_count(self) -> None:
        original = TABLE.read_text(encoding="utf-8")
        lines = original.splitlines()
        for index, line in enumerate(lines):
            cells = line.split("|")
            if len(cells) == 8 and cells[1].strip() == "0":
                self.assertEqual(cells[6].strip(), "no")
                cells[6] = " yes "
                lines[index] = "|".join(cells)
                break
        else:
            self.fail("case 0 continuation cell was not found in the committed table")

        baseline = score.summarize_table(original)
        planted = score.summarize_table("\n".join(lines))

        self.assertEqual(baseline["continued"], 0)
        self.assertEqual(planted["continued"], 1)
        self.assertIn("C=1", score.render_report(planted))

    def test_cli_prints_committed_sample_result(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(HERE / "score.py"), str(TABLE)],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("100 re-asks", completed.stdout)
        self.assertIn("Y=0", completed.stdout)
        self.assertIn(
            "recall unmeasured: 0 hand-labelled positives in 100",
            completed.stdout,
        )
        self.assertIn("verdict=(a)", completed.stdout)


if __name__ == "__main__":
    unittest.main()
