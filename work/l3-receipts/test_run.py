"""Offline parser/planner controls; recorded answer fixtures are not live L3 proof."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("l3_receipt_run", Path(__file__).with_name("run.py"))
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("receipt parser/planner module is unavailable")
RUN = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUN)


class ReceiptPrimitiveTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(dir=os.environ["TMPDIR"])
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        observations = [json.loads(line) for line in (ROOT / "kit/fixtures/gate/answers-jev.jsonl").read_text().splitlines()]
        positive = next(row for row in observations if row["decision"] is True)
        negative = next(row for row in observations if row["decision"] is False)
        self.log = self.root / "observations.jsonl"
        self.log.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in [positive, negative]))
        self.session = self.root / "fixture-session.jsonl"
        self.session.write_text(json.dumps({"type": "session", "fixture": True}) + "\n")
        canonical = json.loads((ROOT / "work/jev-inventory/expected.json").read_text())
        surface = next(row for row in canonical["surfaces"] if row["id"] == "gate-observe")
        self.inventory = {"schema": canonical["schema"], "profiles": ["default"], "surfaces": [surface]}
        self.policy = {"K_s": 1, "B_s": 2, "model": positive["backend"], "model_field": "backend",
                       "positive": {"field": "decision", "equals": True},
                       "negative": {"field": "decision", "equals": False}}
        self.budget = {"schema": "jev-l3-budget.v1", "total_budget": 2, "spend_estimate_usd": 0,
                       "surfaces": {surface["id"]: self.policy}}
        self.agents = "| Surface | Status |\n|---|---|\n| gate-observe | ON |\n"
        self.records = []
        for line, case in enumerate(["positive", "negative"], 1):
            raw = self.log.read_text().splitlines()[line - 1]
            self.records.append({"schema": "jev-l3-receipt.v1", "surface": surface["id"], "profile": "default",
                                 "case": case, "model": positive["backend"], "spend_usd": 0,
                                 "session_file": self.session.name,
                                 "session_sha256": hashlib.sha256(self.session.read_bytes()).hexdigest(),
                                 "log_file": self.log.name, "log_line": line,
                                 "log_sha256": hashlib.sha256(raw.encode()).hexdigest()})

    def audit(self, records: list[dict[str, Any]] | None = None, agents: str | None = None) -> dict[str, Any]:
        plan = RUN.make_plan(self.inventory, self.budget)
        return RUN.audit_receipts(plan, self.inventory, self.records if records is None else records,
                                  self.agents if agents is None else agents, self.root)

    def test_matching_recorded_artifacts_pass_only_the_offline_audit(self) -> None:
        result = self.audit()
        self.assertEqual(
            [(row["surface"], row["profile"], row["case"], row["status"]) for row in result["rows"]],
            [("gate-observe", "default", "positive", "PASS"), ("gate-observe", "default", "negative", "PASS")],
        )
        self.assertEqual((result["status"], result["exit_code"], result["live_l3_proven"]), ("PASS", 0, False))

    def test_positive_without_log_row_fails(self) -> None:
        records = copy.deepcopy(self.records)
        records[0]["log_line"] = 99
        result = self.audit(records)
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("log row", result["rows"][0]["reason"])

    def test_declared_on_surface_without_receipts_fails(self) -> None:
        result = self.audit([])
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(all(row["reason"] == "missing receipt" for row in result["rows"]))

    def test_malformed_surface_cannot_disappear_from_coverage(self) -> None:
        for mutation in [{"expect": "mystery"}, {"decision": None}]:
            inventory = copy.deepcopy(self.inventory)
            extra = dict(inventory["surfaces"][0], id="additional-observed-surface", **mutation)
            inventory["surfaces"].append(extra)
            with self.assertRaises(ValueError):
                RUN.make_plan(inventory, self.budget)

    def test_missing_per_surface_k_or_total_budget_refuses(self) -> None:
        for missing in ["K_s", "total_budget"]:
            budget = copy.deepcopy(self.budget)
            if missing == "K_s":
                del budget["surfaces"]["gate-observe"][missing]
            else:
                del budget[missing]
            with self.assertRaises(ValueError):
                RUN.make_plan(self.inventory, budget)

    def test_budget_must_match_session_arithmetic(self) -> None:
        for change in ["per_surface", "total"]:
            budget = copy.deepcopy(self.budget)
            if change == "per_surface":
                budget["surfaces"]["gate-observe"]["B_s"] = 3
            else:
                budget["total_budget"] = 3
            with self.assertRaisesRegex(ValueError, "budget"):
                RUN.make_plan(self.inventory, budget)

    def test_agents_off_declaration_cannot_pass_receipts_for_on_surface(self) -> None:
        result = self.audit(agents=self.agents.replace(" ON ", " OFF "))
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(all("declaration" in row["reason"] for row in result["rows"]))

    def test_blank_declaration_cannot_impersonate_surface_without_display_name(self) -> None:
        self.inventory["surfaces"][0].pop("name", None)
        self.assertEqual(self.audit(agents="| | ON |")["status"], "FAIL")

    def test_receipt_surface_or_profile_mismatch_fails(self) -> None:
        for field, value in [("surface", "webscreen"), ("profile", "unregistered")]:
            records = copy.deepcopy(self.records)
            records[0][field] = value
            self.assertEqual(self.audit(records)["status"], "FAIL")

    def test_receipt_cannot_claim_positive_from_negative_log(self) -> None:
        records = copy.deepcopy(self.records)
        records[0].update({key: self.records[1][key] for key in ["log_line", "log_sha256"]})
        result = self.audit(records)
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("effect", result["rows"][0]["reason"])

    def test_changed_log_or_session_hash_fails(self) -> None:
        for key in ["log_sha256", "session_sha256"]:
            records = copy.deepcopy(self.records)
            records[0][key] = "0" * 64
            self.assertEqual(self.audit(records)["status"], "FAIL")

    def test_wrong_answering_backend_fails(self) -> None:
        records = copy.deepcopy(self.records)
        records[0]["model"] = "session-chat-fallback"
        self.assertEqual(self.audit(records)["status"], "FAIL")

    def test_duplicate_receipt_fails(self) -> None:
        self.assertEqual(self.audit(self.records + [self.records[0]])["status"], "FAIL")

    def test_native_plan_covers_each_profile_in_both_directions(self) -> None:
        self.inventory["profiles"] = ["default", "codex"]
        self.inventory["surfaces"][0] = dict(self.inventory["surfaces"][0], group="native")
        self.budget["surfaces"]["gate-observe"]["B_s"] = 4
        self.budget["total_budget"] = 4
        plan = RUN.make_plan(self.inventory, self.budget)
        self.assertEqual({(row["profile"], row["case"]) for row in plan["sessions"]},
                         {("default", "positive"), ("default", "negative"), ("codex", "positive"), ("codex", "negative")})

    def test_fleet_observations_never_schedule_profile_rpc_or_load_checks(self) -> None:
        canonical = json.loads((ROOT / "work/jev-inventory/expected.json").read_text())
        fleet = next(row for row in canonical["surfaces"] if row["id"] == "needs-human")
        self.inventory.update(profiles=["default", "codex"], surfaces=[fleet])
        self.budget["surfaces"] = {fleet["id"]: self.policy}
        plan = RUN.make_plan(self.inventory, self.budget)
        self.assertEqual(
            {(row["profile"], row["case"], row["runner"]) for row in plan["sessions"]},
            {("hub", "positive", "hub-observation"), ("hub", "negative", "hub-observation")},
        )
        self.assertEqual(plan["total_budget"], 2)

    def test_markdown_without_frozen_json_budget_refuses(self) -> None:
        path = self.root / "PREREG.md"
        path.write_text("# No call budget is authorized\n")
        with self.assertRaisesRegex(ValueError, "budget"):
            RUN.read_budget(path)

    def test_markdown_budget_is_read_without_guessing_missing_fields(self) -> None:
        path = self.root / "PREREG.md"
        path.write_text("# Fixture-only plan\n```json\n" + json.dumps(self.budget) + "\n```\n")
        self.assertEqual(RUN.make_plan(self.inventory, RUN.read_budget(path))["total_budget"], 2)

    def test_empty_receipt_ledger_is_not_positive_evidence(self) -> None:
        path = self.root / "receipts.jsonl"
        path.write_text("")
        self.assertEqual(self.audit(RUN.read_receipts(path))["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
