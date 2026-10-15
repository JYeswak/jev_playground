"""Keyless tests for the preregistration reachability gate."""

from __future__ import annotations

import hashlib
import json
import subprocess  # nosec B404 - fixed local test script only
import sys
from tempfile import TemporaryDirectory
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "bar-reachable.py"
FLOOR = ROOT / "work" / "osw-bestofn" / "floor_receipt.json"
MANIFEST = ROOT / "work" / "osw-bestofn" / "heldout_valid_slice.json"
USED_ROWS = ROOT / "work" / "osw-bestofn" / "live_rows_r3.jsonl"
R112_SCORE = ROOT / "work" / "osw-bestofn" / "live_score_check_r3.json"
PREFLIGHT = ROOT / "work" / "osw-bestofn" / "r112_retry_preflight.json"
HEADROOM_UNREACHABLE_MANIFEST = (
    ROOT / "work" / "osw-bestofn" / "headroom_unreachable_slice.json"
)
EMPTY_USED_ROWS = ROOT / "work" / "osw-bestofn" / "empty_used_rows.jsonl"


def run_checker(*args: str) -> tuple[int, dict]:
    completed = subprocess.run(  # nosec B603 - fixed argv and bounded timeout
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return completed.returncode, json.JSONDecoder().decode(completed.stdout)


class BarReachabilityTests(unittest.TestCase):
    def test_jev_jjwt_split_is_refused_before_spend(self):
        code, receipt = run_checker(
            "--floor",
            str(FLOOR),
            "--preflight",
            str(PREFLIGHT),
            "--manifest",
            str(MANIFEST),
            "--used-rows",
            str(USED_ROWS),
        )
        self.assertEqual(code, 1)
        self.assertEqual(receipt["status"], "UNREACHABLE")
        self.assertEqual(receipt["tasks"], 24)
        self.assertEqual(receipt["comparator_exact"], 22)
        self.assertEqual(receipt["max_discordant_wins"], 2)
        self.assertEqual(receipt["minimum_attainable_p"], 0.5)

    def test_r112_split_has_room_beyond_observed_discordance(self):
        code, receipt = run_checker(
            "--score-receipt",
            str(R112_SCORE),
            "--floor",
            str(FLOOR),
            "--used-rows",
            str(USED_ROWS),
        )
        self.assertEqual(code, 0)
        self.assertEqual(receipt["status"], "REACHABLE")
        self.assertEqual(receipt["tasks"], 337)
        self.assertEqual(receipt["comparator_exact"], 139)
        self.assertEqual(receipt["max_discordant_wins"], 74)
        self.assertLess(receipt["minimum_attainable_p"], 0.05)
        self.assertEqual(receipt["observed"]["observed_b"], 2)
        self.assertEqual(receipt["observed"]["observed_c"], 8)

    def test_rate_bar_uses_perfect_score_wilson_bound(self):
        code, receipt = run_checker(
            "--mode",
            "rate",
            "--trials",
            "337",
            "--threshold",
            "0.99",
        )
        self.assertEqual(code, 1)
        self.assertEqual(receipt["status"], "UNREACHABLE")
        self.assertLess(receipt["wilson_lower_bound_95"], 0.99)

    def test_rate_receipt_records_preregistration_identity(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            prereg = root / "prereg.md"
            items = root / "items.jsonl"
            prereg.write_text("reach-mode: rate\nn: 10\n")
            items.write_text('{"id":"a"}\n')
            code, receipt = run_checker(
                "--mode",
                "rate",
                "--trials",
                "10",
                "--threshold",
                "0.5",
                "--prereg",
                str(prereg),
                "--items",
                str(items),
            )
            self.assertEqual(code, 0)
            self.assertEqual(receipt["mode"], "rate")
            self.assertEqual(receipt["prereg_path"], str(prereg.resolve()))
            self.assertEqual(
                receipt["items_sha256"], hashlib.sha256(items.read_bytes()).hexdigest()
            )
            self.assertEqual(
                receipt["prereg_sha256"],
                hashlib.sha256(prereg.read_bytes()).hexdigest(),
            )

    def test_oracle_headroom_unreachable_when_comparator_misses_would_pass(self):
        code, receipt = run_checker(
            "--floor",
            str(FLOOR),
            "--manifest",
            str(HEADROOM_UNREACHABLE_MANIFEST),
            "--used-rows",
            str(EMPTY_USED_ROWS),
        )
        self.assertEqual(code, 1)
        self.assertEqual(receipt["status"], "UNREACHABLE")
        self.assertEqual(receipt["tasks"], 30)
        self.assertEqual(receipt["comparator_exact"], 20)
        self.assertEqual(receipt["oracle_headroom"], 3)
        self.assertEqual(receipt["max_discordant_wins"], 3)
        self.assertEqual(receipt["minimum_attainable_p"], 0.25)

    def test_auc_minority_class_refuses_70_3(self):
        code, receipt = run_checker(
            "--mode",
            "auc",
            "--positive-count",
            "70",
            "--negative-count",
            "3",
            "--threshold",
            "0.70",
            "--min-minority-class",
            "5",
        )
        self.assertEqual(code, 1)
        self.assertEqual(receipt["status"], "UNDERPOWERED")
        self.assertEqual(receipt["minority_count"], 3)

    def test_auc_minority_class_allows_40_30(self):
        code, receipt = run_checker(
            "--mode",
            "auc",
            "--positive-count",
            "40",
            "--negative-count",
            "30",
            "--threshold",
            "0.70",
            "--min-minority-class",
            "5",
        )
        self.assertEqual(code, 0)
        self.assertEqual(receipt["status"], "REACHABLE")
        self.assertEqual(receipt["minority_count"], 30)

    @staticmethod
    def _cohort_tree(root, *, rows, covered, harm, extra=None):
        lines = [f'{{"id": {i}}}' for i in range(rows)]
        (root / "rows.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
        digest = hashlib.sha256("\n".join(lines).encode() + b"\n").hexdigest()
        demand = {
            "eligible_denominator": rows,
            "labels_recounted": {"covered_rows": covered, "harm_rows": harm},
            "missing_outcomes": rows - covered,
            "source_hashes": {"window_rows_sha256": digest},
        }
        (root / "demand.json").write_text(json.dumps(demand), encoding="utf-8")
        cohort = {
            "eligible_denominator": rows,
            "covered_rows": covered,
            "harm_rows": harm,
            "missing_outcomes": rows - covered,
            "rows_sha256": digest,
            "source": {
                "rows_file": "rows.jsonl",
                "window_rows_sha256": digest,
                "receipt": "demand.json",
            },
        }
        if extra:
            cohort.update(extra)
        (root / "reach.json").write_text(json.dumps(cohort), encoding="utf-8")
        (root / "PREREG.md").write_text("reach-mode: auc\n", encoding="utf-8")
        return root

    def test_cohort_zero_class_is_terminal_not_reachable(self):
        with TemporaryDirectory() as tmp:
            root = self._cohort_tree(Path(tmp), rows=100, covered=45, harm=0)
            code, receipt = run_checker("--prereg", str(root / "PREREG.md"), "--json")
            self.assertEqual(code, 1)
            self.assertEqual(receipt["status"], "NOT_REACHABLE")
            self.assertIn("harmful", receipt["reason"])
            self.assertEqual(receipt["mode"], "auc")

    def test_cohort_healthy_classes_reach(self):
        with TemporaryDirectory() as tmp:
            root = self._cohort_tree(Path(tmp), rows=100, covered=70, harm=40)
            reach_path = root / "reach.json"
            cohort = json.loads(reach_path.read_text(encoding="utf-8"))
            cohort["threshold"] = 0.70
            cohort["min_minority_class"] = 5
            reach_path.write_text(json.dumps(cohort), encoding="utf-8")
            code, receipt = run_checker("--prereg", str(root / "PREREG.md"))
            self.assertEqual(code, 0)
            self.assertEqual(receipt["status"], "REACHABLE")

    def test_cohort_override_keys_refused(self):
        with TemporaryDirectory() as tmp:
            root = self._cohort_tree(Path(tmp), rows=100, covered=70, harm=40)
            reach_path = root / "reach.json"
            cohort = json.loads(reach_path.read_text(encoding="utf-8"))
            cohort["positive_count"] = 40
            cohort["threshold"] = 0.70
            reach_path.write_text(json.dumps(cohort), encoding="utf-8")
            code, receipt = run_checker("--prereg", str(root / "PREREG.md"))
            self.assertEqual(code, 2)
            self.assertEqual(receipt["status"], "ERROR")

    def test_cohort_forged_counts_refuse(self):
        with TemporaryDirectory() as tmp:
            root = self._cohort_tree(Path(tmp), rows=100, covered=45, harm=0)
            reach_path = root / "reach.json"
            forged = json.loads(reach_path.read_text(encoding="utf-8"))
            forged["harm_rows"] = 40
            forged["threshold"] = 0.70
            reach_path.write_text(json.dumps(forged), encoding="utf-8")
            code, receipt = run_checker("--prereg", str(root / "PREREG.md"))
            self.assertEqual(code, 2)
            self.assertEqual(receipt["status"], "ERROR")
            self.assertIn("disagrees with frozen source", receipt["error"])

    def test_cohort_same_count_byte_tamper_refuses(self):
        with TemporaryDirectory() as tmp:
            root = self._cohort_tree(Path(tmp), rows=100, covered=45, harm=0)
            rows_path = root / "rows.jsonl"
            raw = rows_path.read_bytes().replace(b'"id": 7}', b'"id": 8}', 1)
            rows_path.write_bytes(raw)
            code, receipt = run_checker("--prereg", str(root / "PREREG.md"))
            self.assertEqual(code, 2)
            self.assertEqual(receipt["status"], "ERROR")
            self.assertIn("rows_sha256 disagrees", receipt["error"])


    def test_cohort_missing_counts_refuses(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "PREREG.md").write_text("reach-mode: auc\n", encoding="utf-8")
            (root / "reach.json").write_text(json.dumps({}), encoding="utf-8")
            code, receipt = run_checker("--prereg", str(root / "PREREG.md"))
            self.assertEqual(code, 2)
            self.assertEqual(receipt["status"], "ERROR")

    def test_cohort_missing_file_refuses(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "PREREG.md").write_text("reach-mode: auc\n", encoding="utf-8")
            code, receipt = run_checker("--prereg", str(root / "PREREG.md"))
            self.assertEqual(code, 2)
            self.assertEqual(receipt["status"], "ERROR")




if __name__ == "__main__":
    unittest.main()
