"""Read-only L3 receipt planning and artifact audit. Never launches sessions or model calls."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def required_surfaces(inventory: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if inventory.get("schema") != "jev-inventory.expected.v1" or not isinstance(inventory.get("surfaces"), list):
        raise ValueError("unsupported inventory schema")
    result = {}
    seen = set()
    for row in inventory["surfaces"]:
        if (
            not isinstance(row, dict)
            or not isinstance(row.get("id"), str)
            or not row["id"].strip()
            or row["id"] in seen
        ):
            raise ValueError("inventory surfaces need non-empty unique IDs")
        seen.add(row["id"])
        if row.get("expect") not in {"on", "off", "inert"}:
            raise ValueError("inventory expected state is unknown")
        if row["expect"] != "on":
            continue
        decision = row.get("decision")
        if not isinstance(decision, str) or not decision.strip():
            raise ValueError("ON surface needs an explicit decision")
        if decision.strip().lower().startswith("none"):
            continue
        if str(row.get("verdict", "")).upper() in {"OFF", "REFUTED", "BROKEN", "FAIL", "FAILED"}:
            raise ValueError("inventory ON declaration contradicts its verdict")
        result[row["id"]] = row
    if not result:
        raise ValueError("no declared ON decision surfaces; empty coverage is not a pass")
    return result


def read_budget(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        value = json.loads(text)
    else:
        blocks = text.split("```json\n")
        if len(blocks) != 2 or "```" not in blocks[1]:
            raise ValueError("no single frozen JSON budget in preregistration")
        value = json.loads(blocks[1].split("```", 1)[0])
    if not isinstance(value, dict):
        raise ValueError("budget must be an object")
    return value


def make_plan(inventory: dict[str, Any], budget: dict[str, Any]) -> dict[str, Any]:
    surfaces = required_surfaces(inventory)
    profiles = inventory.get("profiles")
    if not isinstance(profiles, list) or any(not isinstance(p, str) or not p for p in profiles):
        raise ValueError("inventory profiles must be non-empty names")
    if "default" not in profiles or len(set(profiles)) != len(profiles):
        raise ValueError("inventory profiles need default and unique names")
    if budget.get("schema") != "jev-l3-budget.v1" or not isinstance(budget.get("surfaces"), dict):
        raise ValueError("unsupported budget schema")
    if set(budget["surfaces"]) != set(surfaces):
        raise ValueError("budget does not exactly cover inventory ON decision surfaces")
    total = budget.get("total_budget")
    spend = budget.get("spend_estimate_usd")
    if type(total) is not int or total < 0:
        raise ValueError("total budget is required and must be a nonnegative integer")
    if isinstance(spend, bool) or not isinstance(spend, (int, float)) or (isinstance(spend, float) and not math.isfinite(spend)) or spend < 0:
        raise ValueError("budget spend estimate is required and must be finite/nonnegative")
    sessions = []
    calculated = 0
    for surface_id, surface in surfaces.items():
        policy = budget["surfaces"][surface_id]
        if not isinstance(policy, dict) or type(policy.get("K_s")) is not int or policy["K_s"] < 0:
            raise ValueError("every surface budget needs an explicit nonnegative K_s")
        if not isinstance(policy.get("model"), str) or not policy["model"] or not isinstance(policy.get("model_field"), str):
            raise ValueError("every surface budget needs a pinned model and log model field")
        if surface.get("group") == "native":
            cases = [(profile, case) for profile in profiles for case in ("positive", "negative")]
        elif surface.get("group") == "fleet":
            cases = [("hub", "positive"), ("hub", "negative")]
        else:
            cases = [("default", "positive"), ("default", "negative")]
            cases += [(profile, "load") for profile in profiles if profile != "default"]
        for profile, case in cases:
            effect = policy.get(case)
            if not isinstance(effect, dict) or not isinstance(effect.get("field"), str) or "equals" not in effect:
                raise ValueError("each planned case needs a pinned observable log effect")
            sessions.append({"surface": surface_id, "profile": profile, "case": case,
                             "runner": "hub-observation" if surface.get("group") == "fleet" else "omp-rpc"})
        expected = len(cases) * policy["K_s"]
        if type(policy.get("B_s")) is not int or policy["B_s"] != expected:
            raise ValueError("per-surface budget must equal planned sessions times K_s")
        calculated += expected
    if calculated != total:
        raise ValueError("total budget does not equal the sum of per-surface budgets")
    return {"schema": "jev-l3-plan.v1", "sessions": sessions, "policies": budget["surfaces"],
            "total_budget": total, "spend_estimate_usd": spend, "model_calls": 0,
            "live_l3_proven": False}


def read_receipts(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError("receipt rows must be objects")
            rows.append(value)
    return rows


def evidence_path(root: Path, value: Any) -> Path:
    if not isinstance(value, str) or not value:
        raise ValueError("missing evidence path")
    path = (root / value).resolve(strict=True)
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError("evidence path escapes the authorized root")
    return path


def check_evidence(record: dict[str, Any], policy: dict[str, Any], root: Path) -> None:
    session = evidence_path(root, record.get("session_file"))
    if hashlib.sha256(session.read_bytes()).hexdigest() != record.get("session_sha256"):
        raise ValueError("session evidence hash mismatch")
    log = evidence_path(root, record.get("log_file"))
    line_number = record.get("log_line")
    if type(line_number) is not int or not 1 <= line_number <= 1_000_000:
        raise ValueError("missing or invalid log row")
    raw = None
    with log.open("rb") as stream:
        for index in range(line_number):
            current = stream.readline(65537)
            if not current or len(current) > 65536:
                raise ValueError("missing or oversized log row")
            if index + 1 == line_number:
                raw = current.rstrip(b"\r\n")
    if raw is None or hashlib.sha256(raw).hexdigest() != record.get("log_sha256"):
        raise ValueError("log row hash mismatch")
    observation = json.loads(raw)
    if not isinstance(observation, dict):
        raise ValueError("log row is not an object")
    if record.get("model") != policy["model"] or observation.get(policy["model_field"]) != policy["model"]:
        raise ValueError("answering model does not match the pinned model")
    spend = record.get("spend_usd")
    if isinstance(spend, bool) or not isinstance(spend, (int, float)) or (isinstance(spend, float) and not math.isfinite(spend)) or spend < 0:
        raise ValueError("receipt spend must be finite and nonnegative")
    effect = policy[record["case"]]
    observed = observation.get(effect["field"])
    if effect["field"] not in observation or type(observed) is not type(effect["equals"]) or observed != effect["equals"]:
        raise ValueError("log effect does not match the planned case")


def declaration_on(agents: str, surface: dict[str, Any]) -> bool:
    identity = surface.get("id")
    if not isinstance(identity, str) or not identity.strip():
        return False
    names = {identity.lower()}
    display_name = surface.get("name")
    if isinstance(display_name, str) and display_name.strip():
        names.add(display_name.strip().lower())
    matches = []
    for line in agents.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [cell.replace("`", "").replace("*", "").strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and cells[0].lower() in names:
            words = cells[-1].split()
            matches.append(bool(words) and words[0].strip(":;,.").upper() == "ON")
    return len(matches) == 1 and matches[0]


def audit_receipts(plan: dict[str, Any], inventory: dict[str, Any], records: list[dict[str, Any]],
                   agents: str, root: Path) -> dict[str, Any]:
    surfaces = required_surfaces(inventory)
    expected = {(row["surface"], row["profile"], row["case"]) for row in plan["sessions"]}
    by_key = {}
    rows = []
    duplicates = set()
    for record in records:
        key = tuple(record.get(field) for field in ("surface", "profile", "case"))
        if any(not isinstance(value, str) for value in key) or key not in expected:
            rows.append({"status": "FAIL", "reason": "receipt does not match inventory surface/profile/case"})
        elif key in by_key:
            duplicates.add(key)
        else:
            by_key[key] = record
    for planned in plan["sessions"]:
        key = tuple(planned[field] for field in ("surface", "profile", "case"))
        record = by_key.get(key)
        reason = None
        if key in duplicates:
            reason = "duplicate receipt"
        elif not record:
            reason = "missing receipt"
        elif record.get("schema") != "jev-l3-receipt.v1":
            reason = "unsupported receipt schema"
        elif not declaration_on(agents, surfaces[planned["surface"]]):
            reason = "AGENTS declaration does not match inventory ON state"
        else:
            try:
                check_evidence(record, plan["policies"][planned["surface"]], root)
            except (OSError, ValueError, TypeError, KeyError):
                # No raw log contents, credential values or exception bodies enter the report.
                reason = "invalid session/log row, model, spend or planned effect evidence"
        rows.append({**planned, "status": "FAIL" if reason else "PASS", "reason": reason})
    ok = bool(rows) and all(row["status"] == "PASS" for row in rows)
    return {"schema": "jev-l3-audit.v1", "operation": "artifact-audit", "status": "PASS" if ok else "FAIL",
            "exit_code": 0 if ok else 1, "rows": rows, "model_calls": 0, "live_l3_proven": False}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, default=ROOT / "work/jev-inventory/expected.json")
    parser.add_argument("--budget", type=Path, default=HERE / "PREREG.md")
    parser.add_argument("--receipts", type=Path, default=HERE / "receipts.jsonl")
    parser.add_argument("--agents", type=Path, default=ROOT / "AGENTS.md")
    parser.add_argument("--evidence-root", type=Path, default=ROOT)
    parser.add_argument("--json", action="store_true", required=True)
    parser.add_argument("--plan", action="store_true")
    args = parser.parse_args(argv)
    try:
        inventory = json.loads(args.inventory.read_text(encoding="utf-8"))
        plan = make_plan(inventory, read_budget(args.budget))
        result = plan if args.plan else audit_receipts(plan, inventory, read_receipts(args.receipts),
                                                     args.agents.read_text(encoding="utf-8"), args.evidence_root)
        print(json.dumps(result, sort_keys=True))
        return result.get("exit_code", 0)
    except (OSError, ValueError, TypeError, KeyError):
        print(json.dumps({"status": "REFUSED", "reason": "missing or invalid inventory, preregistered budget or evidence input",
                          "model_calls": 0, "live_l3_proven": False}, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
