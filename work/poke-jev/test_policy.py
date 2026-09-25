"""Offline tests for PokéJev's search policy and answer validator (no key, no network, no PokéChamp).

Run: cd work/poke-jev && python3 -m unittest test_policy
"""

import math
import unittest

import policy as p

DISPLAY = {"move a": "A", "move b": "B", "switch x": "Switch to X"}


class Validator(unittest.TestCase):
    def test_accepts_a_well_formed_distribution_and_maps_labels_back(self):
        out = p.validated({"A": 0.5, "B": 0.3, "Switch to X": 0.2}, DISPLAY)
        self.assertEqual(out, {"move a": 0.5, "move b": 0.3, "switch x": 0.2})

    def test_refuses_a_missing_or_extra_label(self):
        with self.assertRaises(ValueError):
            p.validated({"A": 0.6, "B": 0.4}, DISPLAY)
        with self.assertRaises(ValueError):
            p.validated({"A": 0.4, "B": 0.3, "Switch to X": 0.2, "Z": 0.1}, DISPLAY)

    def test_refuses_non_finite_negative_or_above_one(self):
        for bad in (math.nan, math.inf, -0.1, 1.5):
            with self.assertRaises(ValueError):
                p.validated({"A": bad, "B": 0.5, "Switch to X": 0.5}, DISPLAY)

    def test_refuses_a_sum_off_by_the_tolerance(self):
        with self.assertRaises(ValueError):
            p.validated({"A": 0.5, "B": 0.3, "Switch to X": 0.1}, DISPLAY)
        p.validated(
            {"A": 0.5, "B": 0.3, "Switch to X": 0.19}, DISPLAY
        )  # 0.99 is inside 0.02


class OpponentPick(unittest.TestCase):
    def test_takes_actions_until_the_mass_is_covered_then_renormalizes(self):
        got = p.pick_opponent({"a": 0.5, "b": 0.35, "c": 0.1, "d": 0.05})
        self.assertEqual(list(got), ["a", "b"])
        self.assertAlmostEqual(sum(got.values()), 1.0)
        self.assertAlmostEqual(got["a"], 0.5 / 0.85)

    def test_never_more_than_k(self):
        flat = {c: 0.1 for c in "abcdefghij"}
        self.assertEqual(len(p.pick_opponent(flat)), p.K_OPP)

    def test_all_zero_mass_becomes_uniform_not_a_division_error(self):
        got = p.pick_opponent({"a": 0.0, "b": 0.0})
        self.assertEqual(got, {"a": 0.5, "b": 0.5})


class PlayerPick(unittest.TestCase):
    PRIOR = {"a": 0.4, "b": 0.3, "c": 0.2, "d": 0.1}

    def test_top_k_by_prior_plus_the_damage_tool(self):
        self.assertEqual(p.pick_player(self.PRIOR, "d"), ["a", "b", "c", "d"])

    def test_tool_already_in_top_k_or_illegal_adds_nothing(self):
        self.assertEqual(p.pick_player(self.PRIOR, "a"), ["a", "b", "c"])
        self.assertEqual(p.pick_player(self.PRIOR, "not-legal"), ["a", "b", "c"])
        self.assertEqual(p.pick_player(self.PRIOR, None), ["a", "b", "c"])


class Expectimax(unittest.TestCase):
    def test_weights_each_branch_by_the_opponent_model(self):
        opp = {"o1": 0.8, "o2": 0.2}
        best_given = {"o1": {"a": 0.9, "b": 0.1}, "o2": {"a": 0.0, "b": 1.0}}
        best, values = p.expectimax(["a", "b"], opp, best_given, {"a": 0.5, "b": 0.5})
        self.assertEqual(best, "a")
        self.assertAlmostEqual(values["a"], 0.72)
        self.assertAlmostEqual(values["b"], 0.28)

    def test_a_likely_punish_flips_the_choice_the_prior_prefers(self):
        opp = {"o1": 0.3, "o2": 0.7}
        best_given = {"o1": {"a": 1.0, "b": 0.0}, "o2": {"a": 0.0, "b": 1.0}}
        best, _ = p.expectimax(["a", "b"], opp, best_given, {"a": 0.9, "b": 0.1})
        self.assertEqual(best, "b")

    def test_tie_goes_to_the_prior_and_missing_leaves_count_zero(self):
        best, values = p.expectimax(["a", "b"], {"o1": 1.0}, {}, {"a": 0.2, "b": 0.8})
        self.assertEqual(values, {"a": 0.0, "b": 0.0})
        self.assertEqual(best, "b")


if __name__ == "__main__":
    unittest.main()
