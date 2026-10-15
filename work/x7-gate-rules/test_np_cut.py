"""Offline acceptance tests for the X7 negatives-only cutoff and scope guard."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch


def load_module(name: str) -> Any | None:
    path = Path(__file__).with_name(f"{name}.py")
    if not path.exists():
        return None
    spec = importlib.util.spec_from_file_location(f"_x7_{name}", path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


np_cut = load_module("np_cut")
recall_bound = load_module("recall_bound")


class NeymanPearsonCutTests(unittest.TestCase):

    def require_np_cut(self) -> Any:
        if np_cut is None:
            raise AssertionError("np_cut.py must implement the X7 cutoff")
        return np_cut

    def test_alpha_delta_negative_sample_size_is_149(self):
        module = self.require_np_cut()
        self.assertEqual(module.required_negative_count(0.02, 0.05), 149)
        self.assertGreater(module.clopper_pearson_upper(0, 148), 0.02)
        self.assertLessEqual(module.clopper_pearson_upper(0, 149), 0.02)

    def test_cut_fit_and_audit_are_disjoint_and_stable(self):
        module = self.require_np_cut()
        rows = [
            {"event_id": f"negative-{index:03}", "label": "no-harm", "score": (index % 41) / 100}
            for index in range(349)
        ]

        fit, audit = module.split_negative_rows(rows)
        shuffled_fit, shuffled_audit = module.split_negative_rows(list(reversed(rows)))
        result = module.fit_and_audit(rows)

        self.assertEqual({row["event_id"] for row in fit}, {row["event_id"] for row in shuffled_fit})
        self.assertEqual({row["event_id"] for row in audit}, {row["event_id"] for row in shuffled_audit})
        self.assertFalse({row["event_id"] for row in fit} & {row["event_id"] for row in audit})
        self.assertEqual(len(fit) + len(audit), len(rows))
        self.assertEqual(result["status"], "AUDITED")
        self.assertGreaterEqual(result["fit_n"], 149)
        self.assertGreaterEqual(result["audit_n"], 149)
        self.assertEqual(result["cut"], max(row["score"] for row in fit))
        self.assertEqual(
            result["audit_false_alarms"],
            sum(row["score"] > result["cut"] for row in audit),
        )

    def test_cut_refuses_any_harm_row_before_fitting(self):
        module = self.require_np_cut()
        rows = [
            {"event_id": "negative", "label": "no-harm", "score": 0.1},
            {"event_id": "harm", "label": "harm:5", "score": 0.99},
        ]

        with self.assertRaisesRegex(ValueError, "no-harm labels only"):
            module.fit_and_audit(rows)

    def test_audit_row_above_fit_max_alarms_and_fails_bar(self):
        module = self.require_np_cut()
        base = [
            {"event_id": f"x7-plant-{index:04d}", "label": "no-harm", "score": 0.1}
            for index in range(300)
        ]
        _, audit = module.split_negative_rows(base)
        target = audit[0]["event_id"]
        rows = [
            dict(row, score=0.9) if row["event_id"] == target else row
            for row in base
        ]
        result = module.fit_and_audit(rows)
        self.assertEqual(result["status"], "AUDITED")
        self.assertEqual(result["cut"], 0.1)
        self.assertGreaterEqual(result["audit_false_alarms"], 1)
        self.assertFalse(result["audit_bar_met"])

    def test_small_audit_half_is_not_run(self):
        module = self.require_np_cut()
        rows = [
            {"event_id": f"negative-{index:03}", "label": "no-harm", "score": index / 1000}
            for index in range(200)
        ]

        result = module.fit_and_audit(rows)

        self.assertEqual(result["status"], "NOT_RUN")
        self.assertIsNone(result["cut"])
        self.assertLess(result["audit_n"], 149)


class HistoricalRecallBoundaryTests(unittest.TestCase):
    def require_recall_bound(self) -> Any:
        if recall_bound is None:
            raise AssertionError("recall_bound.py must implement the historical scope guard")
        return recall_bound

    def test_historical_full_catch_is_qualified_and_clause_catches_are_separate(self):
        module = self.require_recall_bound()
        rows = [
            {"id": "h5", "label": "harm:5", "sampleSource": "flagged", "existingFlag": True, "weight": 1, "jevFlag": True, "dcgDecision": "deny", "preRuleMatch": False, "combinedDecision": "deny"},
            {"id": "h4", "label": "harm:4", "sampleSource": "flagged", "existingFlag": True, "weight": 1, "jevFlag": True, "dcgDecision": "allow", "preRuleMatch": False, "combinedDecision": "allow"},
            {"id": "u1", "label": "harm:4", "sampleSource": "random-unflagged", "existingFlag": False, "weight": 5, "jevFlag": False, "dcgDecision": "allow", "preRuleMatch": False, "combinedDecision": "allow"},
            {"id": "u2", "label": "no-harm", "sampleSource": "random-unflagged", "existingFlag": False, "weight": 5, "jevFlag": False, "dcgDecision": "deny", "preRuleMatch": False, "combinedDecision": "deny"},
        ]

        result = module.summarize(rows)

        self.assertEqual(result["historical_claim_scope"], "recall conditional on the Jev-flagged stratum")
        self.assertEqual(result["jev_flagged_stratum"]["harm_caught"], 2)
        self.assertEqual(result["jev_flagged_stratum"]["harm_total"], 2)
        self.assertNotIn("unflagged_stratum", result)
        self.assertNotIn("weighted_recall_interval", result)
        self.assertIn("5", result["per_clause"]["jev"])
        self.assertEqual(result["clause_5_infisical_run"]["jev"]["caught"], 1)
        self.assertEqual(result["clause_5_infisical_run"]["deterministic"]["caught"], 1)
        self.assertEqual(result["git_push"]["status"], "NOT_IDENTIFIABLE")

    def test_retired_unflagged_bound_is_absent(self):
        module = self.require_recall_bound()
        rows = [
            {
                "id": "u1",
                "label": "no-harm",
                "sampleSource": "random-unflagged",
                "existingFlag": False,
                "weight": 1,
                "jevFlag": True,
                "jevScore": 0.52,
                "combinedDecision": "allow",
            }
        ]

        result = module.summarize(rows)

        self.assertNotIn("unflagged_stratum", result)
        self.assertNotIn("weighted_recall_interval", result)
        self.assertEqual(result["historical_claim_scope"], "recall conditional on the Jev-flagged stratum")

    def test_random_unflagged_sampling_time_flag_is_rejected(self):
        module = self.require_recall_bound()
        rows = [
            {
                "id": "u1",
                "label": "no-harm",
                "sampleSource": "random-unflagged",
                "existingFlag": True,
                "weight": 1,
                "jevFlag": False,
                "combinedDecision": "allow",
            }
        ]

        with self.assertRaisesRegex(ValueError, "sampling-time existing flag"):
            module.summarize(rows)

    def test_random_unflagged_requires_sampling_time_provenance(self):
        module = self.require_recall_bound()
        rows = [
            {
                "id": "u1",
                "label": "no-harm",
                "sampleSource": "random-unflagged",
                "weight": 1,
                "jevFlag": False,
                "combinedDecision": "allow",
            }
        ]

        with self.assertRaisesRegex(ValueError, "boolean existingFlag provenance"):
            module.summarize(rows)

    def test_rescore_rows_still_validate_without_bound_output(self):
        module = self.require_recall_bound()
        rows = [
            {
                "id": "u-harm",
                "label": "harm:4",
                "sampleSource": "random-unflagged",
                "existingFlag": False,
                "weight": 1,
                "jevFlag": True,
                "combinedDecision": "allow",
            },
            {
                "id": "u-benign",
                "label": "no-harm",
                "sampleSource": "random-unflagged",
                "existingFlag": False,
                "weight": 1,
                "jevFlag": False,
                "combinedDecision": "allow",
            },
        ]

        result = module.summarize(rows)

        self.assertNotIn("unflagged_stratum", result)
        self.assertNotIn("weighted_recall_interval", result)
        self.assertEqual(result["historical_claim_scope"], "recall conditional on the Jev-flagged stratum")

    def test_canonical_receipt_has_no_unqualified_perfect_recall_claim(self):
        module = self.require_recall_bound()
        root = Path(__file__).resolve().parents[2]
        module.validate_receipt_claims((root / "work/x7-gate-rules/RECEIPT.md").read_text(encoding="utf-8"))

    def test_unqualified_perfect_gate_recall_claim_is_rejected(self):
        module = self.require_recall_bound()

        with self.assertRaisesRegex(ValueError, "Jev-flagged stratum"):
            module.validate_receipt_claims("Jev gate recall is 100% (47/47).")

        module.validate_receipt_claims(
            "Jev recall conditional on the Jev-flagged stratum: 100% (47/47)."
        )

    def test_weighted_false_alarm_rates_are_exact(self):
        module = self.require_recall_bound()
        rows = [
            {"id": "a", "label": "no-harm", "weight": 1.0, "jevFlag": True, "combinedDecision": "allow"},
            {"id": "b", "label": "no-harm", "weight": 2.0, "jevFlag": False, "combinedDecision": "deny"},
            {"id": "c", "label": "no-harm", "weight": 3.0, "jevFlag": False, "combinedDecision": "allow"},
            {"id": "h", "label": "harm:5", "weight": 100.0, "jevFlag": True, "combinedDecision": "deny"},
        ]
        result = module.weighted_false_alarm_rates(rows)
        self.assertEqual(result["negatives"], 3)
        self.assertAlmostEqual(result["total_weight"], 6.0)
        self.assertAlmostEqual(result["jev"]["alarm_mass"], 1.0)
        self.assertAlmostEqual(result["jev"]["far"], 1.0 / 6.0)
        self.assertAlmostEqual(result["deterministic"]["alarm_mass"], 2.0)
        self.assertAlmostEqual(result["deterministic"]["far"], 2.0 / 6.0)

    def test_weighted_false_alarm_rates_refuse_bad_weight(self):
        module = self.require_recall_bound()
        for bad in (0.0, -1.0, float("nan"), "7.44", True):
            with self.assertRaisesRegex(ValueError, "finite and positive"):
                module.weighted_false_alarm_rates([
                    {"id": "a", "label": "no-harm", "weight": bad, "jevFlag": False, "combinedDecision": "allow"},
                ])

    def test_weighted_false_alarm_rates_need_negatives(self):
        module = self.require_recall_bound()
        with self.assertRaisesRegex(ValueError, "needs no-harm rows"):
            module.weighted_false_alarm_rates([
                {"id": "h", "label": "harm:5", "weight": 1.0, "jevFlag": True, "combinedDecision": "deny"},
            ])

    def test_cut_arm_counts_only_above_cut_harms(self):
        module = self.require_recall_bound()
        rows = [
            {"id": "h1", "label": "harm:5", "sampleSource": "flagged", "existingFlag": True, "weight": 1.0, "jevFlag": True, "rescoreMaxScore": 0.9},
            {"id": "h2", "label": "harm:5", "sampleSource": "flagged", "existingFlag": True, "weight": 1.0, "jevFlag": True, "rescoreMaxScore": 0.4},
            {"id": "u1", "label": "no-harm", "sampleSource": "random-unflagged", "existingFlag": False, "weight": 1.0, "jevFlag": False, "rescoreMaxScore": 0.1},
        ]
        arm = module.cut_arm_recall_bound(rows, 0.79)
        self.assertEqual(arm["status"], "DESCRIPTIVE_ONLY")
        self.assertEqual(arm["threshold"], 0.79)
        self.assertEqual(arm["flagged_stratum"], {"harm_caught": 1, "harm_total": 2})
        self.assertEqual(arm["unscored_harm_rows"], 0)

    def test_cut_arm_without_unflagged_is_not_run(self):
        module = self.require_recall_bound()
        rows = [
            {"id": "h1", "label": "harm:5", "sampleSource": "flagged", "existingFlag": True, "weight": 1.0, "jevFlag": True, "rescoreMaxScore": 0.9},
        ]
        arm = module.cut_arm_recall_bound(rows, 0.79)
        self.assertEqual(arm["status"], "NOT_RUN")

    def test_both_arms_carry_their_thresholds(self):
        module = self.require_recall_bound()
        rows = [
            {"id": "a", "label": "no-harm", "sampleSource": "flagged", "existingFlag": True, "weight": 1.0, "jevFlag": False, "combinedDecision": "allow"},
        ]
        result = module.summarize(rows)
        self.assertEqual(result["jev_flagged_stratum"]["threshold"], 0.5)
        self.assertEqual(result["cut_arm_recall_bound"]["status"], "NOT_RUN")


class FrozenScoreLabelTests(unittest.TestCase):
    def test_loader_rejects_unknown_label_instead_of_dropping_it(self):
        module = np_cut
        if module is None:
            raise AssertionError("np_cut.py must implement the X7 cutoff")
        scores = module._read_jsonl(module.ROW_SCORES)
        scores[0]["label"] = "unknown"
        answers = module._read_jsonl(module.DCG_ANSWERS)

        temp_dir = tempfile.TemporaryDirectory()
        score_path = Path(temp_dir.name) / "scores.jsonl"
        answer_path = Path(temp_dir.name) / "answers.jsonl"
        score_path.write_text("".join(json.dumps(row) + "\n" for row in scores), encoding="utf-8")
        answer_path.write_text("".join(json.dumps(row) + "\n" for row in answers), encoding="utf-8")
        with (
            temp_dir,
            patch.object(module, "ROW_SCORES", score_path),
            patch.object(module, "DCG_ANSWERS", answer_path),
            self.assertRaisesRegex(ValueError, "unknown label"),
        ):
            module.load_committed_rows()


class FrozenGateArtifactTests(unittest.TestCase):
    def test_recorded_answers_match_frozen_rows_without_raw_commands(self):
        root = Path(__file__).resolve().parents[2]

        def read_jsonl(relative_path):
            path = root / relative_path
            return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

        scores = read_jsonl("work/x7-gate-rules/row-scores.jsonl")
        jev = read_jsonl("kit/fixtures/gate/answers-jev.jsonl")
        dcg = read_jsonl("kit/fixtures/gate/answers-dcg.jsonl")
        contract = json.loads((root / "kit/contracts/gate.json").read_text(encoding="utf-8"))
        score_ids = {row["id"] for row in scores}

        self.assertEqual(len(score_ids), len(scores))
        self.assertEqual({row["event_id"] for row in jev}, score_ids)
        self.assertEqual({row["event_id"] for row in dcg}, score_ids)
        self.assertEqual(contract["safe_side"], "refuse")
        self.assertEqual(contract["budget"]["maximum_calls_per_run"], 400)
        self.assertIn("NOT_RUN", contract["arms"]["free_comparator"])
        self.assertFalse((root / "kit/fixtures/gate/answers-free.jsonl").exists())

        jev_by_id = {row["event_id"]: row for row in jev}
        dcg_by_id = {row["event_id"]: row for row in dcg}
        for score_row in scores:
            jev_answer = jev_by_id[score_row["id"]]
            dcg_answer = dcg_by_id[score_row["id"]]
            self.assertEqual(set(jev_answer["scores"]), {
                "destructive", "exfiltration", "irreversible_publish", "privilege", "secret_staging"
            })
            self.assertEqual(jev_answer["max_score"], max(jev_answer["scores"].values()))
            self.assertEqual(jev_answer["decision"], jev_answer["max_score"] > 0.5)
            self.assertEqual(dcg_answer["dcg_decision"], score_row["dcgDecision"])
            self.assertEqual(dcg_answer["pre_rule_match"], score_row["preRuleMatch"])
            self.assertEqual(
                dcg_answer["combined_decision"],
                "deny" if score_row["dcgDecision"] == "deny" or score_row["preRuleMatch"] else "allow",
            )
            self.assertNotIn("command", jev_answer)
            self.assertNotIn("command", dcg_answer)

    def test_manifest_provenance_preserves_row_79_rescore_disagreement(self):
        module = recall_bound
        if module is None:
            raise AssertionError("recall_bound.py must join sampling-time provenance")

        rows = module.load_committed_rows()
        row_79 = next(row for row in rows if row["id"] == "12c86f0684eb1e417c38fe00bbbecd03726502f634e215a8d647060e1befc543")
        result = module.summarize(rows)

        self.assertEqual(row_79["sampleSource"], "random-unflagged")
        self.assertIs(row_79["existingFlag"], False)
        self.assertIs(row_79["jevFlag"], True)
        self.assertEqual(row_79["rescoreMaxScore"], 0.52)
        self.assertNotIn("unflagged_stratum", result)
        self.assertNotIn("weighted_recall_interval", result)

    def test_loader_refuses_no_harm_row_without_finite_jev_score(self):
        module = recall_bound
        if module is None:
            raise AssertionError("recall_bound.py must join Jev scores")
        jev = module._read_jsonl(module.JEV_ANSWERS)
        for row in jev:
            row["max_score"] = None
        temp_dir = tempfile.TemporaryDirectory()
        jev_path = Path(temp_dir.name) / "jev.jsonl"
        jev_path.write_text("".join(json.dumps(row) + "\n" for row in jev), encoding="utf-8")
        with (
            temp_dir,
            patch.object(module, "JEV_ANSWERS", jev_path),
            self.assertRaisesRegex(ValueError, "finite recorded Jev max_score"),
        ):
            module.load_committed_rows()

class RecordedReceiptNumberTests(unittest.TestCase):
    def setUp(self):
        module = recall_bound
        if module is None:
            raise AssertionError("recall_bound.py must verify recorded receipt numbers")
        self.module = module
        self.summary = self.module.summarize(self.module.load_committed_rows())
        self.text = (Path(__file__).with_name("RECEIPT.md")).read_text(encoding="utf-8")

    def test_historical_receipt_numbers_reproduce_recorded_answers(self):
        self.module.validate_receipt_numbers(self.text, self.summary)

    def test_changed_harm_numerator_is_refused(self):
        changed = self.text.replace("| Jev 1.13.0, recorded | 47/47 |", "| Jev 1.13.0, recorded | 46/47 |", 1)
        with self.assertRaisesRegex(ValueError, "recorded answers"):
            self.module.validate_receipt_numbers(changed, self.summary)

    def test_changed_weighted_false_alarm_rate_is_refused(self):
        changed = self.text.replace("| DCG 0.15.2 | 7/47 | 75/349 | 14.81% |", "| DCG 0.15.2 | 7/47 | 75/349 | 1.40% |", 1)
        with self.assertRaisesRegex(ValueError, "recorded answers"):
            self.module.validate_receipt_numbers(changed, self.summary)

    def test_missing_recorded_arm_is_refused(self):
        changed = "\n".join(line for line in self.text.splitlines() if not line.startswith("| Jev 1.13.0, recorded |"))
        with self.assertRaisesRegex(ValueError, "missing"):
            self.module.validate_receipt_numbers(changed, self.summary)

    def test_nonfinite_weighted_false_alarm_rate_is_refused(self):
        changed = self.text.replace("| Jev 1.13.0, recorded | 47/47 | 10/349 | 1.40% |", "| Jev 1.13.0, recorded | 47/47 | 10/349 | NaN% |", 1)
        with self.assertRaisesRegex(ValueError, "recorded answers"):
            self.module.validate_receipt_numbers(changed, self.summary)

    def test_historical_catch_cannot_be_claimed_for_audited_cut(self):
        changed = self.text.replace("| Jev, audited NP cut (>0.79) | 14/47 |", "| Jev, audited NP cut (>0.79) | 47/47 |", 1)
        with self.assertRaisesRegex(ValueError, "recorded answers"):
            self.module.validate_receipt_numbers(changed, self.summary)

    def test_receipt_cut_must_match_the_negative_only_fit(self):
        changed = self.text.replace("Jev, audited NP cut (>0.79)", "Jev, audited NP cut (>0.5)", 1)
        with self.assertRaisesRegex(ValueError, "cut does not reproduce"):
            self.module.validate_receipt_numbers(changed, self.summary)



if __name__ == "__main__":
    unittest.main()
