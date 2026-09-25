"""Keyless tests for the Emerald Choice request and budget builder."""

import json
import sys
import unittest
from pathlib import Path

if sys.version_info < (3, 12):
    print("SKIP (missing prerequisite: Python >= 3.12)")
    raise SystemExit(8)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from macro_choice import LEGAL_INPUTS, MODEL, build_choice_request, estimate_budget  # noqa: E402


class MacroChoice(unittest.TestCase):
    def sample_row(self):
        return {
            "state": {
                "visual": {"resolution": [240, 160], "screenshot_present": True},
                "player": {
                    "position": {"x": 2, "y": 2},
                    "location": "MOVING_VAN",
                    "party": None,
                },
                "game": {"game_state": "overworld", "is_in_battle": False},
                "map": {"visual_map": "hidden", "object_events": []},
            },
            "state_text": "must not be sent",
        }

    def test_request_is_pinned_choice_over_legal_inputs_and_excludes_text_image(self):
        request = build_choice_request(self.sample_row())
        self.assertEqual(request["model"], MODEL)
        question = request["questions"]["macro"]
        self.assertEqual(question["type"], "choice")
        self.assertEqual(tuple(question["criteria"]), LEGAL_INPUTS)
        self.assertNotIn("state_text", request["state"])
        self.assertNotIn("screenshot_present", request["state"]["visual"])

    def test_budget_reports_rate_time_tokens_and_cost_without_network(self):
        rows = [self.sample_row(), self.sample_row()]
        budget = estimate_budget(rows, macros=200)
        self.assertEqual(budget["request_limit_hz"], 20)
        self.assertFalse(budget["throttled"])
        self.assertEqual(budget["duration_s"], 45.0)
        self.assertGreater(budget["estimated_input_tokens"]["p95"], 0)
        self.assertGreater(budget["estimated_input_cost_usd"]["p95"], 0)
        json.dumps(budget)


if __name__ == "__main__":
    unittest.main()
