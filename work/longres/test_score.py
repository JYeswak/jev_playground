from __future__ import annotations

import json
import unittest
from pathlib import Path

from work.longres.score import score_data, score_files

ROOT = Path(__file__).resolve().parents[2]


def load_run(corpus_path: Path, rows_path: Path) -> tuple[object, list[object]]:
    try:
        corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
        rows = [
            json.loads(line)
            for line in rows_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    except json.JSONDecodeError as error:
        raise AssertionError(f"invalid committed long-result JSON: {error}") from error
    return corpus, rows


class LongresScorerTests(unittest.TestCase):
    def test_matched_prereg_recomputes_disjoint_corpus2_result(self) -> None:
        report = score_files(
            ROOT / "work/longres/corpus2.json",
            ROOT / "work/longres/choice-rows2.jsonl",
            fit_method="matched",
        )

        self.assertEqual(report.fit_threshold_chars, 51416)
        self.assertEqual(report.fit_referenced, 12)
        self.assertEqual(report.fit_reference_drops, 0)
        self.assertEqual(report.held_rows, 100)
        self.assertEqual(report.held_referenced, 22)
        self.assertEqual(report.jev.reference_drops, 6)
        self.assertEqual(report.baseline.reference_drops, 0)
        self.assertEqual(report.jev.savings_chars, 540857)
        self.assertEqual(report.baseline.savings_chars, 0)
        self.assertTrue(report.matched_savings_bar_pass)
        self.assertTrue(report.qualified)
        self.assertEqual(report.total_calls, 150)
        self.assertEqual(report.scored_calls, 150)
        self.assertEqual(report.calls_with_usage, 150)
        self.assertEqual(report.input_tokens, 108185)
        self.assertTrue(report.spend_complete)
        self.assertAlmostEqual(report.observed_spend_usd, 0.004544, places=6)
        self.assertEqual(report.weekly_tokens_saved_jev, 13344294)

    def test_youden_prereg_recomputes_original_fail_and_keep_fallback(self) -> None:
        report = score_files(
            ROOT / "work/longres/corpus.json",
            ROOT / "work/longres/choice-rows.jsonl",
            fit_method="youden",
        )

        self.assertEqual(report.fit_threshold_chars, 10154)
        self.assertEqual(report.held_rows, 100)
        self.assertEqual(report.held_referenced, 35)
        self.assertEqual(report.jev.reference_drops, 4)
        self.assertEqual(report.baseline.reference_drops, 31)
        self.assertEqual(report.jev.savings_chars, 588490)
        self.assertEqual(report.baseline.savings_chars, 1542184)
        self.assertFalse(report.primary_bar_pass)
        self.assertEqual(report.scored_calls, 199)
        self.assertEqual(report.fallback_keeps, 1)
        self.assertEqual(report.calls_with_usage, 199)
        self.assertFalse(report.spend_complete)
        self.assertAlmostEqual(report.observed_spend_usd, 0.00601, places=6)
        self.assertEqual(report.weekly_tokens_saved_jev, 14493037)

    def test_unscored_receipt_cannot_claim_non_keep_action(self) -> None:
        corpus, rows = load_run(
            ROOT / "work/longres/corpus.json",
            ROOT / "work/longres/choice-rows.jsonl",
        )
        altered_rows = [dict(row) for row in rows if isinstance(row, dict)]
        no_answer = next(
            row for row in altered_rows if row.get("status") == "no-answers"
        )
        no_answer["pred"] = "drop"

        with self.assertRaisesRegex(ValueError, "must fail safe to keep"):
            score_data(corpus, altered_rows, fit_method="youden")

    def test_incomplete_receipt_is_refused_instead_of_shrinking_denominator(
        self,
    ) -> None:
        corpus, rows = load_run(
            ROOT / "work/longres/corpus2.json",
            ROOT / "work/longres/choice-rows2.jsonl",
        )

        with self.assertRaisesRegex(ValueError, "missing 1 sample"):
            score_data(corpus, rows[:-1], fit_method="matched")


if __name__ == "__main__":
    unittest.main()
