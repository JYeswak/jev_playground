"""Offline tests for work/jev-if/puct.py: stdlib unittest, no jericho, no key, no network.

python3 -m unittest work/jev-if/test_puct.py
"""

import math
import os
import random
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import puct  # noqa: E402


class TinyGame:
    """Deterministic fake game with MC-DML's env interface (src/env.py step/copy/close).

    hall: take key (+5 once), north -> vault, south -> pit (death). vault: open door (+10 with key,
    game over), south -> hall. Moving north prints a room text equal to its look text, which is the
    case MC-DML's node lookup never re-finds (mcts.py:179).
    """

    LOOK = {"hall": "hall. a vault lies north, a pit south.", "vault": "vault. a door."}

    def __init__(self, state=None):
        self.s = dict(state or {"loc": "hall", "key": False, "score": 0})

    def _info(self, done):
        if done:
            return {
                "look": "unknown",
                "inv": "unknown",
                "valid": ["wait", "yes", "no"],
                "score": self.s["score"],
            }
        valid = (
            ["north", "south", "take key"]
            if self.s["loc"] == "hall"
            else ["open door", "south"]
        )
        if self.s["key"]:
            valid = [a for a in valid if a != "take key"]
        inv = "you carry a key." if self.s["key"] else "you are empty-handed."
        return {
            "look": self.LOOK[self.s["loc"]],
            "inv": inv,
            "valid": valid,
            "score": self.s["score"],
        }

    def reset(self):
        return self.LOOK["hall"], self._info(False)

    def step(self, action):
        s = self.s
        reward, done, ob = 0, False, "nothing happens."
        if s["loc"] == "hall" and action == "take key" and not s["key"]:
            s["key"], reward, ob = True, 5, "taken."
        elif s["loc"] == "hall" and action == "north":
            s["loc"], ob = "vault", self.LOOK["vault"]
        elif s["loc"] == "hall" and action == "south":
            ob, done = "you fall. *** you have died ***", True
        elif s["loc"] == "vault" and action == "south":
            s["loc"], ob = "hall", "back in the hall."
        elif s["loc"] == "vault" and action == "open door" and s["key"]:
            reward, done, ob = 10, True, "the door opens. you win."
        s["score"] += reward
        return ob, reward, done, self._info(done)

    def copy(self):
        return TinyGame(self.s)

    def close(self):
        pass


def answer(probabilities, choice=None):
    choice = choice if choice is not None else max(probabilities, key=probabilities.get)
    return {"choice": choice, "confidence": 0.5, "probabilities": probabilities}


class ScriptedAsker:
    """Returns a fixed reply (or raises) and records every call."""

    def __init__(self, reply=None, error=None):
        self.reply = reply
        self.error = error
        self.calls = []

    def __call__(self, state, question, model):
        self.calls.append((state, question, model))
        if self.error is not None:
            raise self.error
        return self.reply(question) if callable(self.reply) else self.reply


def uniform_reply(question):
    options = list(question["criteria"])
    return {
        "model": puct.MODEL,
        "answer": answer({o: 1.0 / len(options) for o in options}, options[0]),
        "usage": {"input_tokens": 700, "output_tokens": 30},
    }


def run_search(
    prior_fn, seed=3, sims=4, max_inflight=1, prefetch=False, node_key="code"
):
    env = TinyGame()
    ob, info = env.reset()
    priors = puct.PriorService(prior_fn, "mcdml", 3, max_inflight)
    search = puct.PUCTSearch(
        env, priors, 50, random.Random(seed), sims, 0.95, (4, 4, 20), node_key, prefetch
    )
    root, action = search.search(ob, info, ())
    priors.close()
    stats = [(c.action, c.N, round(c.Q, 9)) for c in root.children]
    return action, stats, priors, root


class PuctMath(unittest.TestCase):
    def test_puct_value_matches_hand_computation(self):
        # Q + c * sqrt(N(s)+1) / (N(s,a)+1) * p with N(s)=3, c=2: sqrt(4) = 2.
        self.assertAlmostEqual(puct.puct_value(1.0, 3, 1, 0.2, 2), 1.4)
        self.assertAlmostEqual(puct.puct_value(0.0, 3, 0, 0.5, 2), 2.0)
        self.assertAlmostEqual(puct.puct_value(2.0, 3, 2, 0.3, 2), 2.0 + 4 / 3 * 0.3)

    def test_selection_picks_the_hand_computed_argmax(self):
        node = puct.StateNode()
        node.N = 3
        node.children = [puct.ActionNode(a) for a in ("a", "b", "c")]
        for child, (q, n) in zip(node.children, [(1.0, 1), (0.0, 0), (2.0, 2)]):
            child.Q, child.N = q, n
        node.prior = [0.2, 0.5, 0.3]  # values 1.4, 2.0, 2.4
        search = puct.PUCTSearch(None, None, 2, random.Random(0))
        search.priors = puct.PriorService(puct.uniform_prior)
        self.assertEqual(search.greedy_action_node(node, 2).action, "c")
        node.prior = [0.2, 0.9, 0.0]  # values 1.4, 3.6, 2.0
        self.assertEqual(search.greedy_action_node(node, 2).action, "b")
        # c = 0 is the real-action rule (mcts.py:106): argmax Q.
        self.assertEqual(search.greedy_action_node(node, 0).action, "c")

    def test_ties_are_broken_uniformly_at_random(self):
        node = puct.StateNode()
        node.children = [puct.ActionNode(a) for a in ("a", "b")]
        node.prior = [0.5, 0.5]
        search = puct.PUCTSearch(
            None, puct.PriorService(puct.uniform_prior), 1, random.Random(0)
        )
        picks = {search.greedy_action_node(node, 1).action for _ in range(50)}
        self.assertEqual(picks, {"a", "b"})

    def test_softmax_backup_weights_returns_at_temperature_10(self):
        e = math.e
        self.assertAlmostEqual(puct.softmax_backup([0.0, 10.0]), 10 * e / (1 + e))
        self.assertAlmostEqual(puct.softmax_backup([4.0]), 4.0)

    def test_mcdml_transform_matches_softmax_of_clamped_logprobs(self):
        p = puct.mcdml_transform([1.0, 0.0])  # logits 0 and -5, T = 5
        self.assertAlmostEqual(p[0], 1 / (1 + math.exp(-1)))
        self.assertAlmostEqual(p[1], math.exp(-1) / (1 + math.exp(-1)))
        # log p below -5 takes the absent-label value, so the map stays monotone.
        tiny = puct.mcdml_transform([0.999, 1e-4, 0.0])
        self.assertAlmostEqual(tiny[1], tiny[2])


class UniformArm(unittest.TestCase):
    def test_uniform_prior_is_one_over_the_number_of_actions(self):
        probs = puct.uniform_prior({}, ["north", "south", "take key", "open door"])[
            "probabilities"
        ]
        self.assertEqual(
            probs, {"north": 0.25, "south": 0.25, "take key": 0.25, "open door": 0.25}
        )

    def test_uniform_prior_survives_the_transform_unchanged(self):
        for n in (1, 2, 7, 200):
            self.assertTrue(
                all(abs(p - 1 / n) < 1e-12 for p in puct.mcdml_transform([1 / n] * n))
            )

    def test_uniform_arm_makes_no_network_call(self):
        _, _, priors, _ = run_search(puct.uniform_prior)
        self.assertGreater(priors.requested, 0)
        self.assertEqual((priors.calls, priors.failed, priors.input_tokens), (0, 0, 0))


class ValidatorRefusesHostileAnswers(unittest.TestCase):
    OPTIONS = ["north", "south", "take key"]
    GOOD = {"north": 0.6, "south": 0.1, "take key": 0.3}

    def refused(self, bad):
        with self.assertRaises(ValueError):
            puct.validate_choice(bad, self.OPTIONS)

    def test_well_formed_answer_is_accepted(self):
        self.assertIs(
            puct.validate_choice(answer(dict(self.GOOD)), self.OPTIONS)["choice"],
            "north",
        )

    def test_choice_not_in_options_is_refused_and_node_gets_uniform_prior(self):
        self.refused(answer(dict(self.GOOD), "xyzzy"))

    def test_missing_option_is_refused_and_node_gets_uniform_prior(self):
        self.refused(answer({"north": 0.7, "south": 0.3}))

    def test_extra_option_is_refused_and_node_gets_uniform_prior(self):
        self.refused(
            answer({"north": 0.5, "south": 0.1, "take key": 0.3, "xyzzy": 0.1})
        )

    def test_nan_probability_is_refused_and_node_gets_uniform_prior(self):
        self.refused(
            answer({"north": float("nan"), "south": 0.5, "take key": 0.5}, "south")
        )

    def test_probabilities_summing_to_half_are_refused_and_node_gets_uniform_prior(
        self,
    ):
        self.refused(answer({"north": 0.3, "south": 0.1, "take key": 0.1}))

    def test_out_of_range_and_non_numeric_values_are_refused(self):
        self.refused(answer({"north": 1.2, "south": -0.2, "take key": 0.0}))
        self.refused(answer({"north": True, "south": 0.0, "take key": 0.0}, "north"))
        self.refused(answer({"north": "0.6", "south": 0.1, "take key": 0.3}, "north"))
        self.refused(
            answer({"north": float("inf"), "south": 0.0, "take key": 0.0}, "north")
        )

    def test_choice_that_is_not_the_argmax_is_refused(self):
        self.refused(answer(dict(self.GOOD), "south"))

    def test_structurally_broken_answers_are_refused(self):
        for bad in (
            None,
            {},
            [],
            {"choice": "north"},
            {"choice": "north", "probabilities": self.GOOD},
            {"choice": "north", "confidence": 0.5, "probabilities": [0.6, 0.1, 0.3]},
        ):
            self.refused(bad)

    def test_refused_answer_falls_back_to_uniform_prior_and_is_counted(self):
        hostile = {
            "model": puct.MODEL,
            "answer": answer({"north": 0.9, "xyzzy": 0.1}),
            "usage": {},
        }
        asker = ScriptedAsker(reply=hostile)
        _, _, priors, root = run_search(puct.JevPrior(asker), sims=1)
        self.assertGreater(priors.failed, 0)
        self.assertEqual(priors.failed, priors.requested)
        self.assertEqual(root.prior, [1 / 3] * 3)
        self.assertIn("ValueError", priors.errors[0])

    def test_wrong_resolved_model_is_refused_and_node_gets_uniform_prior(self):
        def reply(question):
            r = uniform_reply(question)
            r["model"] = "jev-1.14.0"
            return r

        _, _, priors, _ = run_search(puct.JevPrior(ScriptedAsker(reply=reply)), sims=1)
        self.assertEqual(priors.failed, priors.requested)

    def test_transport_error_after_retries_falls_back_to_uniform_prior(self):
        _, _, priors, root = run_search(
            puct.JevPrior(ScriptedAsker(error=TimeoutError("read timed out"))), sims=1
        )
        self.assertEqual(priors.failed, priors.requested)
        self.assertEqual(root.prior, [1 / 3] * 3)

    def test_too_many_options_fall_back_to_uniform_without_a_call(self):
        asker = ScriptedAsker(reply=uniform_reply)
        prior = puct.JevPrior(asker)
        service = puct.PriorService(prior)
        node = puct.build_state(
            "ob",
            {
                "look": "l",
                "inv": "i",
                "score": 0,
                "valid": ["act %d" % i for i in range(256)],
            },
        )
        self.assertEqual(service.get(node), [1 / 256] * 256)
        self.assertEqual((service.failed, len(asker.calls)), (1, 0))


class KeyHandling(unittest.TestCase):
    def test_missing_key_raises_instead_of_falling_back_to_uniform(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(puct.MissingKeyError):
                puct.SdkAsker()(
                    {},
                    {"instructions": "x", "criteria": {"a": None, "b": None}},
                    puct.MODEL,
                )
            with self.assertRaises(puct.MissingKeyError):
                run_search(puct.JevPrior(puct.SdkAsker()), sims=1)

    def test_blank_key_counts_as_missing(self):
        with mock.patch.dict(os.environ, {"TYPESAFE_API_KEY": "   "}, clear=True):
            with self.assertRaises(puct.MissingKeyError):
                puct.SdkAsker()(
                    {}, {"instructions": "x", "criteria": {"a": None}}, puct.MODEL
                )

    def test_rejected_key_aborts_instead_of_falling_back_to_uniform(self):
        with self.assertRaises(puct.FatalPriorError):
            run_search(
                puct.JevPrior(ScriptedAsker(error=puct.FatalPriorError("HTTP 401"))),
                sims=1,
            )


class OneCodePath(unittest.TestCase):
    def test_jev_arm_with_a_uniform_answer_reproduces_the_uniform_arm_exactly(self):
        # Same seed, same game: if the jev answer is uniform, every tie-break, rollout and visit
        # count matches the uniform arm. The arms differ only in the prior.
        for seed in range(5):
            uniform = run_search(puct.uniform_prior, seed=seed)
            asker = ScriptedAsker(reply=uniform_reply)
            jev = run_search(puct.JevPrior(asker), seed=seed)
            self.assertEqual(uniform[:2], jev[:2])
            self.assertEqual(uniform[2].requested, jev[2].requested)
            self.assertEqual(jev[2].calls, len(asker.calls))
            self.assertEqual(jev[2].input_tokens, 700 * len(asker.calls))

    def test_prior_changes_the_search(self):
        def favour_south(question):
            options = list(question["criteria"])
            probs = {
                o: (0.98 if o == "south" else 0.02 / (len(options) - 1))
                for o in options
            }
            return {"model": puct.MODEL, "answer": answer(probs), "usage": {}}

        uniform = run_search(puct.uniform_prior, seed=1, sims=8)
        biased = run_search(
            puct.JevPrior(ScriptedAsker(reply=favour_south)), seed=1, sims=8
        )
        self.assertNotEqual(uniform[1], biased[1])

    def test_jev_state_carries_observation_look_inventory_last_three_actions_and_score(
        self,
    ):
        asker = ScriptedAsker(reply=uniform_reply)
        run_search(puct.JevPrior(asker), sims=6)
        state, question, model = asker.calls[0]
        self.assertEqual(
            set(state), {"observation", "look", "inventory", "last_actions", "score"}
        )
        self.assertEqual(model, "jev-1.13.0")
        self.assertEqual(question["type"], "choice")
        self.assertEqual(list(question["criteria"]), ["north", "south", "take key"])
        deep = [s for s, _, _ in asker.calls if len(s["last_actions"]) > 0]
        self.assertTrue(all(len(s["last_actions"]) <= 3 for s in deep))

    def test_single_valid_action_needs_no_call(self):
        asker = ScriptedAsker(reply=uniform_reply)
        result = puct.JevPrior(asker)({}, ["wait"])
        self.assertEqual(
            (result["probabilities"], result["calls"], asker.calls),
            ({"wait": 1.0}, 0, []),
        )

    def test_concurrency_and_prefetch_do_not_change_the_search(self):
        fake = puct.JevPrior(puct.FakeAsker())
        for seed in range(3):
            serial = run_search(fake, seed=seed, sims=6)
            pooled = run_search(fake, seed=seed, sims=6, max_inflight=4, prefetch=True)
            self.assertEqual(serial[:2], pooled[:2])
            self.assertEqual(serial[2].requested, pooled[2].requested)
            self.assertGreaterEqual(pooled[2].calls, serial[2].calls)


class SearchSemantics(unittest.TestCase):
    def test_death_is_scored_minus_ten(self):
        _, stats, _, _ = run_search(puct.uniform_prior, sims=10)
        south = dict((a, q) for a, _, q in stats)["south"]
        self.assertLess(south, 0)
        self.assertAlmostEqual(south, -10.0)

    def test_code_node_key_never_refinds_a_child_whose_text_equals_its_look(self):
        _, _, _, code_root = run_search(
            puct.uniform_prior, seed=0, sims=10, node_key="code"
        )
        _, _, _, fixed_root = run_search(
            puct.uniform_prior, seed=0, sims=10, node_key="fixed"
        )
        north_code = next(c for c in code_root.children if c.action == "north")
        north_fixed = next(c for c in fixed_root.children if c.action == "north")
        self.assertEqual(
            len(north_code.children), north_code.N
        )  # a new node on every visit
        self.assertEqual(len(north_fixed.children), 1)

    def test_simulation_budget_is_sims_per_act_times_valid_actions(self):
        _, stats, _, root = run_search(puct.uniform_prior, sims=7)
        self.assertEqual(sum(n for _, n, _ in stats), 7 * 3)
        self.assertEqual(root.N, 7 * 3)


if __name__ == "__main__":
    unittest.main()
