import unittest

from conformal import (
    chronological_split,
    conformal_prediction_set,
    permute_labels,
    support_gated_prediction_set,
)


class ConformalPredictionSetTests(unittest.TestCase):
    LABELS = ("keep", "drop")

    def test_separated_scores_produce_singleton_class_actions(self):
        calibration = [("keep", {"keep": 0.95, "drop": 0.05}) for _ in range(49)]
        calibration += [("drop", {"keep": 0.05, "drop": 0.95}) for _ in range(49)]

        keep = conformal_prediction_set(
            calibration, {"keep": 0.95, "drop": 0.05}, self.LABELS, alpha=0.05
        )
        drop = conformal_prediction_set(
            calibration, {"keep": 0.05, "drop": 0.95}, self.LABELS, alpha=0.05
        )

        self.assertEqual(keep.labels, frozenset({"keep"}))
        self.assertEqual(drop.labels, frozenset({"drop"}))

    def test_missing_calibration_class_is_retained_so_result_abstains(self):
        result = conformal_prediction_set(
            [("keep", {"keep": 0.8, "drop": 0.2})],
            {"keep": 0.8, "drop": 0.2},
            self.LABELS,
            alpha=0.05,
        )

        self.assertEqual(result.labels, frozenset(self.LABELS))

    def test_one_sided_action_abstains_below_alpha_resolution_support(self):
        calibration = [("keep", {"keep": 0.99, "drop": 0.01}) for _ in range(80)]
        calibration += [("drop", {"keep": 0.01, "drop": 0.99}) for _ in range(48)]
        probabilities = {"keep": 0.01, "drop": 0.99}
        base = conformal_prediction_set(
            calibration, probabilities, self.LABELS, alpha=0.02
        )
        result = support_gated_prediction_set(
            calibration, probabilities, self.LABELS, alpha=0.02
        )

        self.assertEqual(base.labels, frozenset({"drop"}))
        self.assertEqual(result.labels, frozenset(self.LABELS))
        self.assertEqual(result.p_values, base.p_values)

    def test_support_gate_allows_action_at_minimum_resolvable_support(self):
        calibration = [("keep", {"keep": 0.99, "drop": 0.01}) for _ in range(80)]
        calibration += [("drop", {"keep": 0.01, "drop": 0.99}) for _ in range(49)]
        result = support_gated_prediction_set(
            calibration, {"keep": 0.01, "drop": 0.99}, self.LABELS, alpha=0.02
        )

        self.assertEqual(result.labels, frozenset({"drop"}))

    def test_tied_calibration_scores_are_included_conservatively(self):
        calibration = [("keep", {"keep": 0.5, "drop": 0.5}) for _ in range(9)]
        result = conformal_prediction_set(
            calibration, {"keep": 0.5, "drop": 0.5}, self.LABELS, alpha=0.1
        )

        self.assertEqual(result.p_values["keep"], 1.0)
        self.assertEqual(result.labels, frozenset(self.LABELS))

    def test_invalid_probability_vector_is_rejected(self):
        with self.assertRaises(ValueError):
            conformal_prediction_set(
                [], {"keep": 0.7, "drop": 0.1}, self.LABELS, alpha=0.05
            )

    def test_alpha_must_be_strictly_between_zero_and_one(self):
        for alpha in (0.0, 1.0, -0.1, 1.1):
            with self.subTest(alpha=alpha), self.assertRaises(ValueError):
                conformal_prediction_set(
                    [], {"keep": 0.5, "drop": 0.5}, self.LABELS, alpha=alpha
                )


class TemporalSplitTests(unittest.TestCase):
    def test_split_keeps_equal_timestamps_together_and_uses_nearest_half(self):
        rows = [
            {"id": "a", "ts": "2026-01-01T00:00:00Z"},
            {"id": "b", "ts": "2026-01-01T00:00:00Z"},
            {"id": "c", "ts": "2026-01-02T00:00:00Z"},
            {"id": "d", "ts": "2026-01-03T00:00:00Z"},
            {"id": "e", "ts": "2026-01-03T00:00:00Z"},
        ]

        calibration, holdout, cutoff = chronological_split(rows)

        self.assertEqual([row["id"] for row in calibration], ["a", "b"])
        self.assertEqual([row["id"] for row in holdout], ["c", "d", "e"])
        self.assertEqual(cutoff, "2026-01-01T00:00:00Z")
        self.assertLess(
            max(row["ts"] for row in calibration), min(row["ts"] for row in holdout)
        )

    def test_split_refuses_when_no_timestamp_boundary_exists(self):
        rows = [
            {"id": "a", "ts": "2026-01-01T00:00:00Z"},
            {"id": "b", "ts": "2026-01-01T00:00:00Z"},
        ]

        with self.assertRaises(ValueError):
            chronological_split(rows)

    def test_split_rejects_naive_or_missing_timestamps(self):
        for rows in (
            [
                {"id": "a", "ts": "2026-01-01T00:00:00"},
                {"id": "b", "ts": "2026-01-02T00:00:00Z"},
            ],
            [{"id": "a"}, {"id": "b", "ts": "2026-01-02T00:00:00Z"}],
        ):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                chronological_split(rows)


class PermutedLabelTests(unittest.TestCase):
    def test_permutation_is_seeded_and_preserves_class_counts(self):
        labels = ["keep", "keep", "drop", "drop", "drop"]

        first = permute_labels(labels, seed=20261003)
        second = permute_labels(labels, seed=20261003)

        self.assertEqual(first, second)
        self.assertCountEqual(first, labels)
        self.assertNotEqual(first, labels)


if __name__ == "__main__":
    unittest.main()
