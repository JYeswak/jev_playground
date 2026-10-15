"""Offline parser/planner controls; recorded answer fixtures are not live L3 proof."""
from __future__ import annotations

import ast
import copy
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
import uuid
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
        surface = next(row for row in canonical["surfaces"]
                       if row["group"] == "hook" and row["expect"] == "on"
                       and isinstance(row["decision"], str)
                       and not row["decision"].lower().startswith("none"))
        self.surface_id = surface["id"]
        self.inventory = {"schema": canonical["schema"], "profiles": ["default"], "surfaces": [surface]}
        self.policy = {"K_s": 1, "B_s": 2, "model": positive["backend"], "model_field": "backend",
                       "positive": {"field": "decision", "equals": True},
                       "negative": {"field": "decision", "equals": False}}
        self.budget = {"schema": "jev-l3-budget.v1", "total_budget": 2, "spend_estimate_usd": 0,
                       "surfaces": {surface["id"]: self.policy}}
        self.agents = f"| Surface | Status |\n|---|---|\n| {self.surface_id} | ON |\n"
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
            [(self.surface_id, "default", "positive", "PASS"),
             (self.surface_id, "default", "negative", "PASS")],
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
            extra = dict(inventory["surfaces"][0], id=uuid.uuid4().hex, **mutation)
            inventory["surfaces"].append(extra)
            with self.assertRaises(ValueError):
                RUN.make_plan(inventory, self.budget)

    def test_missing_per_surface_k_or_total_budget_refuses(self) -> None:
        for missing in ["K_s", "total_budget"]:
            budget = copy.deepcopy(self.budget)
            if missing == "K_s":
                del budget["surfaces"][self.surface_id][missing]
            else:
                del budget[missing]
            with self.assertRaises(ValueError):
                RUN.make_plan(self.inventory, budget)

    def test_budget_must_match_session_arithmetic(self) -> None:
        for change in ["per_surface", "total"]:
            budget = copy.deepcopy(self.budget)
            if change == "per_surface":
                budget["surfaces"][self.surface_id]["B_s"] = 3
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

    def test_empty_or_whitespace_identity_cannot_match_blank_on_declaration(self) -> None:
        original_id = self.inventory["surfaces"][0]["id"]
        for invalid_id in ("", " \t "):
            inventory = copy.deepcopy(self.inventory)
            inventory["surfaces"][0]["id"] = invalid_id
            budget = copy.deepcopy(self.budget)
            budget["surfaces"] = {invalid_id: budget["surfaces"][original_id]}
            with self.assertRaisesRegex(ValueError, "non-empty unique IDs"):
                RUN.make_plan(inventory, budget)
            self.assertFalse(RUN.declaration_on("| | ON |", inventory["surfaces"][0]))
            self.assertFalse(RUN.declaration_on(
                f'| {inventory["surfaces"][0]["name"]} | ON |', inventory["surfaces"][0]))

    def test_receipt_surface_or_profile_mismatch_fails(self) -> None:
        for field, value in [("surface", uuid.uuid4().hex), ("profile", "unregistered")]:
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
        self.budget["surfaces"][self.surface_id]["B_s"] = 4
        self.budget["total_budget"] = 4
        plan = RUN.make_plan(self.inventory, self.budget)
        self.assertEqual({(row["profile"], row["case"]) for row in plan["sessions"]},
                         {("default", "positive"), ("default", "negative"), ("codex", "positive"), ("codex", "negative")})

    def test_fleet_observations_never_schedule_profile_rpc_or_load_checks(self) -> None:
        canonical = json.loads((ROOT / "work/jev-inventory/expected.json").read_text())
        fleet = next(row for row in canonical["surfaces"]
                     if row["group"] == "fleet" and row["expect"] == "on"
                     and not row["decision"].lower().startswith("none"))
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


class InventoryEnumerationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.inventory = json.loads((ROOT / "work/jev-inventory/expected.json").read_text())
        self.identifiers = {row["id"] for row in self.inventory["surfaces"]}
        observations = [json.loads(line) for line in
                        (ROOT / "kit/fixtures/gate/answers-jev.jsonl").read_text().splitlines()]
        self.model = next(row["backend"] for row in observations if row["decision"] is True)

    @staticmethod
    def literal_ids(source: str, identifiers: set[str]) -> set[str]:
        """Inspect complete native Python ASTs, never execute the supplied source."""
        if len(source.encode()) > 131072:
            raise ValueError("source exceeds this finite architecture check")
        tree = ast.parse(source, mode="exec")
        return {node.value for node in ast.walk(tree)
                if isinstance(node, ast.Constant) and isinstance(node.value, str)
                and node.value in identifiers}

    @staticmethod
    def generated_table(inventory: dict[str, Any]) -> str:
        digest = hashlib.sha256(json.dumps(inventory, sort_keys=True).encode()).hexdigest()
        rows = ["| Surface | Expect |", "|---|---|"]
        rows += [f'| {row["id"]} | {row["expect"]} |' for row in inventory["surfaces"]]
        return f"<!-- generated inventory {digest} -->\n" + "\n".join(rows) + "\n<!-- end generated inventory -->"

    @classmethod
    def prereg_ids(cls, text: str, inventory: dict[str, Any]) -> set[str]:
        if len(text.encode()) > 131072:
            raise ValueError("document exceeds this finite architecture check")
        identifiers = {row["id"] for row in inventory["surfaces"]}
        text = text.replace(cls.generated_table(inventory), "")
        found: set[str] = set()
        example_level = None
        fence = None
        example_fence = False
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith(("```", "~~~")):
                marker = stripped[:3]
                if fence == marker:
                    fence, example_fence = None, False
                elif fence is None:
                    fence = marker
                    example_fence = stripped[3:].strip().lower() == "example"
                continue
            if fence is None and stripped.startswith("#"):
                level = len(stripped) - len(stripped.lstrip("#"))
                heading = stripped[level:].strip().lower()
                if example_level is not None and level <= example_level:
                    example_level = None
                if heading == "example" or heading.startswith(("example ", "example:")):
                    example_level = level
            if example_level is None and not example_fence:
                found.update(set(re.findall(r"[\w-]+", line)) & identifiers)
        return found

    def budget_for(self, inventory: dict[str, Any]) -> dict[str, Any]:
        surfaces = {}
        for identifier, surface in RUN.required_surfaces(inventory).items():
            if surface["group"] == "native":
                sessions = 2 * len(inventory["profiles"])
            elif surface["group"] == "fleet":
                sessions = 2
            else:
                sessions = 1 + len(inventory["profiles"])
            surfaces[identifier] = {
                "K_s": 1, "B_s": sessions,
                "model": self.model, "model_field": "backend",
                "positive": {"field": "decision", "equals": True},
                "negative": {"field": "decision", "equals": False},
                "load": {"field": "decision", "equals": True},
            }
        return {"schema": "jev-l3-budget.v1", "surfaces": surfaces,
                "total_budget": sum(row["B_s"] for row in surfaces.values()),
                "spend_estimate_usd": 0}

    def extended_inventory(self) -> tuple[dict[str, Any], str, str]:
        inventory = copy.deepcopy(self.inventory)
        on_id, none_id = uuid.uuid4().hex, uuid.uuid4().hex
        self.assertTrue({on_id, none_id}.isdisjoint(self.identifiers))
        template = next(row for row in inventory["surfaces"]
                        if row["expect"] == "on" and row["group"] == "native"
                        and not row["decision"].lower().startswith("none"))
        inventory["surfaces"] += [
            dict(template, id=on_id),
            dict(template, id=none_id, decision="none (enumeration control)"),
        ]
        return inventory, on_id, none_id

    def assert_nonce_plan(self, plan: dict[str, Any], on_id: str, none_id: str) -> None:
        expected = {(on_id, profile, case) for profile in self.inventory["profiles"]
                    for case in ("positive", "negative")}
        rows = [row for row in plan["sessions"] if row["surface"] == on_id]
        self.assertEqual({(row["surface"], row["profile"], row["case"]) for row in rows}, expected)
        self.assertEqual(len(rows), len(expected))
        self.assertFalse(any(row["surface"] == none_id for row in plan["sessions"]))

    def test_fixture_ids_are_loaded_from_the_runtime_inventory(self) -> None:
        self.assertFalse(self.literal_ids(Path(__file__).read_text(), self.identifiers),
                         "fixture pins an inventory identifier")

    def test_cli_enumerates_appended_on_identity_and_excludes_none_identity(self) -> None:
        inventory, on_id, none_id = self.extended_inventory()
        with tempfile.TemporaryDirectory(dir=os.environ["TMPDIR"]) as directory:
            root = Path(directory)
            source = root / "expected.json"
            budget = root / "budget.json"
            source.write_text(json.dumps(inventory))
            budget.write_text(json.dumps(self.budget_for(inventory)))
            result = subprocess.run(
                [sys.executable, str(Path(__file__).with_name("run.py")),
                 "--inventory", str(source), "--budget", str(budget), "--plan", "--json"],
                capture_output=True, text=True, timeout=15, check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assert_nonce_plan(json.loads(result.stdout), on_id, none_id)

    def test_fixed_inventory_plan_cannot_pass_the_nonce_consumer_check(self) -> None:
        _, on_id, none_id = self.extended_inventory()
        fixed_plan = RUN.make_plan(self.inventory, self.budget_for(self.inventory))
        with self.assertRaises(AssertionError):
            self.assert_nonce_plan(fixed_plan, on_id, none_id)

    def test_ast_guard_rejects_fixed_nonce_literal_and_invalid_suffix(self) -> None:
        inventory, nonce, _ = self.extended_inventory()
        identifiers = {row["id"] for row in inventory["surfaces"]}
        source = Path(__file__).with_name("run.py").read_text()
        self.assertEqual(self.literal_ids(source, identifiers), set())
        variant = source + f"\nFIXED_SURFACES = {[nonce]!r}\n"
        self.assertEqual(self.literal_ids(variant, identifiers), {nonce})
        with self.assertRaises(SyntaxError):
            self.literal_ids(variant + "\n)", identifiers)

    def test_prereg_ids_require_generated_table_or_marked_example(self) -> None:
        inventory, nonce, _ = self.extended_inventory()
        document = Path(__file__).with_name("PREREG.md").read_text()
        self.assertEqual(self.prereg_ids(document, inventory), set())
        self.assertEqual(self.prereg_ids(document + f"\n{nonce}\n", inventory), {nonce})
        self.assertEqual(self.prereg_ids(document + "\n" + self.generated_table(inventory), inventory), set())
        example = f"\n## Example\n```json\n{json.dumps({'surface': nonce})}\n```\n"
        self.assertEqual(self.prereg_ids(document + example, inventory), set())
        self.assertEqual(self.prereg_ids(document + example + f"\n## Live\n{nonce}", inventory), {nonce})



if __name__ == "__main__":
    unittest.main()
