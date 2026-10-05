import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from run import (  # noqa: E402
    MAX_CALLS,
    OPTIONS,
    fit_keyword_rule,
    run_predictions,
    validate_answer,
)


class LessonClassTests(unittest.TestCase):
    def setUp(self):
        self.probabilities = {label: 0.05 for label in OPTIONS}
        self.probabilities["OTHER"] = 0.5

    def test_answer_outside_offered_classes_is_not_scored(self):
        choice, probs, refusal = validate_answer("NOT_A_CLASS", self.probabilities)
        self.assertIsNone(choice)
        self.assertIsNone(probs)
        self.assertEqual(refusal, "choice_not_offered")

    def test_probability_mass_outside_tolerance_is_refused(self):
        bad = dict(self.probabilities)
        bad["OTHER"] = 0.7
        choice, probs, refusal = validate_answer("OTHER", bad)
        self.assertIsNone(choice)
        self.assertIsNone(probs)
        self.assertEqual(refusal, "probabilities_do_not_sum_to_one")

    def test_choice_not_at_probability_maximum_is_refused(self):
        choice, probs, refusal = validate_answer("SCOPE_GAP", self.probabilities)
        self.assertIsNone(choice)
        self.assertIsNone(probs)
        self.assertEqual(refusal, "choice_not_probability_maximum")

    def test_keyword_rule_rejects_heldout_labels_at_fit_time(self):
        dev = [
            {
                "row_id": "dev",
                "split": "dev",
                "finding": "scope gap",
                "truth": "SCOPE_GAP",
            }
        ]
        held = [
            {
                "row_id": "held",
                "split": "held-out",
                "finding": "false claim",
                "truth": "FALSE_CLAIM",
            }
        ]
        with self.assertRaisesRegex(ValueError, "leakage"):
            fit_keyword_rule(dev + held, held)

    def test_request_cap_never_sends_call_701(self):
        row = {
            "row_id": "r",
            "sentence_sha256": "s",
            "truth": "OTHER",
            "split": "held-out",
            "source_repo": "repo",
            "keyword_pred": "OTHER",
            "majority_pred": "OTHER",
            "finding": "text",
        }
        calls = 0

        def transport(_finding):
            nonlocal calls
            calls += 1
            return {
                "choice": "OTHER",
                "probabilities": self.probabilities,
                "latency_ms": 1,
                "model": "clef-flash",
            }

        rows = run_predictions([row] * (MAX_CALLS + 1), transport)
        self.assertEqual(calls, MAX_CALLS)
        self.assertEqual(len(rows), MAX_CALLS)
        self.assertTrue(all(row["status"] == "scored" for row in rows))

    def test_first_transport_error_stops_without_retry(self):
        row = {
            "row_id": "r",
            "sentence_sha256": "s",
            "truth": "OTHER",
            "split": "held-out",
            "source_repo": "repo",
            "keyword_pred": "OTHER",
            "majority_pred": "OTHER",
            "finding": "text",
        }
        calls = 0

        def transport(_finding):
            nonlocal calls
            calls += 1
            raise ConnectionError("offline")

        rows = run_predictions([row, row], transport)
        self.assertEqual(calls, 1)
        self.assertEqual([item["status"] for item in rows], ["ERROR"])


if __name__ == "__main__":
    unittest.main()
