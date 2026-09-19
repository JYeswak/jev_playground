"""Tests for the ensemble decorrelation predicate.

The central one is the PLANTED NEGATIVE: recipe 4 claims averaging pays because the errors are
decorrelated. If that mechanism is real, averaging a scorer WITH ITSELF -- perfect correlation --
must buy exactly nothing. A measurement that reported a gain there would be measuring arithmetic,
not decorrelation.
"""

import unittest

from decorrelation import analyze


def _oppositely_shaped():
    """20 items. `recall_guard` misses no spam but over-flags ham; `precision_guard` is the mirror.

    This is the Ling-Spam shape in miniature: same error count, opposite failure shapes.
    """
    truth, a, b = [], [], []
    for i in range(10):  # spam
        truth.append(True)
        a.append(0.9)  # recall_guard: catches all spam
        b.append(0.2 if i < 2 else 0.9)  # precision_guard: misses two
    for i in range(10):  # ham
        truth.append(False)
        a.append(0.8 if i < 2 else 0.1)  # recall_guard: two false alarms
        b.append(0.1)  # precision_guard: none
    return a, b, truth


class TestDecorrelation(unittest.TestCase):
    def test_opposite_failure_shapes_make_averaging_pay(self):
        a, b, truth = _oppositely_shaped()
        r = analyze(a, b, truth, a_name="recall_guard", b_name="precision_guard")

        self.assertEqual((r.a.false_negatives, r.a.false_positives), (0, 2))
        self.assertEqual((r.b.false_negatives, r.b.false_positives), (2, 0))
        self.assertGreater(
            r.gain_over_best_input, 0, "the average must beat both inputs"
        )
        self.assertEqual(r.averaged.errors, 0)
        self.assertEqual(r.verdict, "AVERAGE_PAID_AS_PREDICTED")
        self.assertLess(r.phi, 0.5, "oppositely-shaped errors are not correlated")

    def test_PLANTED_NEGATIVE_averaging_a_scorer_with_itself_buys_nothing(self):
        """The recipe's own falsifier. Perfect correlation => no gain, and it must SAY so."""
        a, _, truth = _oppositely_shaped()
        r = analyze(a, list(a), truth, a_name="x", b_name="x_again")

        self.assertEqual(
            r.gain_over_best_input, 0.0, "a scorer cannot ensemble with itself"
        )
        self.assertEqual(r.averaged.errors, r.a.errors)
        self.assertEqual(r.disagreement_rate, 0.0)
        self.assertEqual(r.phi, 1.0, "identical error vectors are perfectly correlated")
        self.assertEqual(r.verdict, "AVERAGE_DID_NOT_PAY")

    def test_a_flawless_scorer_reports_phi_zero_rather_than_dividing_by_zero(self):
        truth = [True, False, True, False]
        perfect = [0.9, 0.1, 0.9, 0.1]
        r = analyze(perfect, perfect, truth)
        self.assertEqual(
            r.phi, 0.0, "a constant error vector has no correlation to report"
        )
        self.assertEqual(r.averaged.errors, 0)

    def test_mismatched_lengths_are_refused_with_the_lengths_named(self):
        with self.assertRaises(ValueError) as ctx:
            analyze([0.5, 0.5], [0.5], [True, False], a_name="short")
        self.assertIn("short=2", str(ctx.exception))

    def test_empty_input_is_refused_rather_than_scored_as_perfect(self):
        with self.assertRaises(ValueError):
            analyze([], [], [])


if __name__ == "__main__":
    unittest.main()
