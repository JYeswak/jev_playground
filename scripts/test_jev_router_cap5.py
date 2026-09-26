#!/usr/bin/env python3
"""Keyless tests for router 402 and fixed-arm error accounting."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "jev_router_cap5", ROOT / "scripts" / "jev-router-cap5.py"
)
assert SPEC and SPEC.loader
router = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(router)


class RouterErrorFixTests(unittest.TestCase):
    def test_parser_extracts_json_after_reasoning_prefix(self) -> None:
        answer = router.parse_answer(
            {
                "choices": [
                    {
                        "message": {
                            "content": 'Reasoning omitted. Final: {"intent":"card_payment_fee_charged"}'
                        }
                    }
                ]
            },
            {"card_payment_fee_charged": "card_payment_fee_charged"},
            {"intent": "card_payment_fee_charged"},
        )
        self.assertEqual(answer["choice"], "card_payment_fee_charged")
        self.assertNotIn("error", answer)

    def test_parser_marks_missing_choice_as_error(self) -> None:
        answer = router.parse_answer(
            {"choices": [{"message": {"content": "truncated reasoning"}}]},
            {"billing": "billing"},
            {"intent": "billing"},
        )
        self.assertIsNone(answer["choice"])
        self.assertEqual(answer["error_code"], "MISSING_CHOICE")

    def test_arm_summary_refuses_quality_when_errors_exceed_five_percent(self) -> None:
        rows = [
            {"router": {"choice": "billing", "correct": index != 0}}
            for index in range(20)
        ]
        rows[0]["router"]["error_code"] = "HTTP_402"
        rows[1]["router"]["error_code"] = "HTTP_402"
        summary = router.summarize_arm(rows, "router")
        self.assertEqual(summary["errors"], 2)
        self.assertEqual(summary["calls"], 20)
        self.assertFalse(summary["verdict_eligible"])

    def test_arm_summary_allows_quality_below_error_bar(self) -> None:
        rows = [
            {"fixed": {"choice": "billing", "correct": index % 2 == 0}}
            for index in range(20)
        ]
        summary = router.summarize_arm(rows, "fixed")
        self.assertEqual(summary["errors"], 0)
        self.assertTrue(summary["verdict_eligible"])


if __name__ == "__main__":
    unittest.main()
