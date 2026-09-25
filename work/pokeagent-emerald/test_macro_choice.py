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

    def test_request_changes_with_position_and_carries_only_porymap_ascii(self):
        row1 = self.sample_row()
        row1["state_text"] = (
            "=== PORYMAP MAP LAYOUT ===\nLocation: InsideOfTruck\nASCII Map:\n#.P.SD\n(Legend: P=player, D=door)\nMap Data"
        )
        row2 = self.sample_row()
        row2["state_text"] = row1["state_text"].replace("#.P.SD", "#..PSD")
        row2["state"]["player"]["position"] = {"x": 3, "y": 2}

        request1 = build_choice_request(row1)
        request2 = build_choice_request(row2)

        self.assertNotEqual(request1["state"], request2["state"])
        self.assertEqual(request1["state"]["map"]["porymap_ascii"], "#.P.SD")
        self.assertNotIn("state_text", request1["state"])

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
