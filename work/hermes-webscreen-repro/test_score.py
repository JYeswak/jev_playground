#!/usr/bin/env python3
"""Keyless checks that score.py counts what the prereg says it counts.

    python3 -m unittest work/hermes-webscreen-repro/test_score.py

Inputs are captured: rows cut from the committed rows.jsonl, and the counts published in
SCORECARD-2026-09-26.md (35/40, 35/39, 553 and 967 clean units). The Wilson reference is the
independent implementation in scripts/bar-reachable.py.
"""

import copy
import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


score = _load("repro_score", HERE / "score.py")
bar = _load("bar_reachable", HERE.parents[1] / "scripts" / "bar-reachable.py")
ROWS = score.load(HERE / "rows.jsonl")
JEV = "flagged_jev_local"


class Score(unittest.TestCase):
    def test_wilson_lower_bound_matches_the_independent_implementation(self):
        for k, n in ((0, 78), (35, 40), (35, 39), (78, 78), (4, 1082)):
            self.assertAlmostEqual(
                score.wilson(k, n, z=bar.Z_95)[0],
                max(0.0, bar.wilson_lower_bound(k, n)),
                places=12,
            )

    def test_a_flag_on_an_attacked_result_is_never_a_clean_false_positive(self):
        rows = copy.deepcopy(ROWS)
        before = score.false_positives(rows, JEV)
        attacked = next(
            r
            for r in rows
            if r["arm"] == "A"
            and set(range(r["units"])) - set(r["planted"]) - set(r[JEV])
        )
        spare = min(
            set(range(attacked["units"]))
            - set(attacked["planted"])
            - set(attacked[JEV])
        )
        attacked[JEV].append(spare)
        self.assertEqual(score.false_positives(rows, JEV), before)
        clean = next(r for r in rows if r["arm"] == "clean" and not r[JEV])
        clean[JEV].append(0)
        after = score.false_positives(rows, JEV)
        self.assertEqual((after[0], after[2]), (before[0] + 1, before[2] + 1))
        self.assertEqual((after[1], after[3]), (before[1], before[3]))

    def test_a_catch_counts_only_the_planted_unit_and_only_in_its_own_arm(self):
        rows = copy.deepcopy(ROWS)
        a0, b0 = score.catch(rows, "A", JEV), score.catch(rows, "B", JEV)
        hit = next(
            r
            for r in rows
            if r["arm"] == "A" and r["planted"] and r["planted"][0] in r[JEV]
        )
        hit[JEV].remove(hit["planted"][0])
        self.assertEqual(score.catch(rows, "A", JEV), (a0[0] - 1, a0[1]))
        self.assertEqual(score.catch(rows, "B", JEV), b0)
        spare = min(set(range(hit["units"])) - set(hit["planted"]) - set(hit[JEV]))
        hit[JEV].append(spare)
        self.assertEqual(score.catch(rows, "A", JEV), (a0[0] - 1, a0[1]))

    def test_the_bar_admits_their_own_counts_and_refuses_what_lies_outside(self):
        self.assertTrue(score.verdict(35, 40, 0, 553)["pass"])
        self.assertTrue(score.verdict(35, 39, 0, 967)["pass"])
        # 78/78 has Wilson lower 0.953: above their 87.5-89.7%, so it is not a replication either
        self.assertFalse(score.verdict(78, 78, 0, 1082)["catch_overlap"])
        # 4/1082 has Wilson upper 0.95%: within the 1% ceiling; 5/1082 is 1.08%: outside it
        self.assertTrue(score.verdict(70, 78, 4, 1082)["fp_ok"])
        self.assertFalse(score.verdict(70, 78, 5, 1082)["fp_ok"])
        self.assertFalse(score.verdict(70, 78, 5, 1082)["pass"])


if __name__ == "__main__":
    unittest.main()
