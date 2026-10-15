"""Describe the historical X7 sample without generalizing its Jev-flag stratum."""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
ROW_SCORES = ROOT / "work/x7-gate-rules/row-scores.jsonl"
JEV_ANSWERS = ROOT / "kit/fixtures/gate/answers-jev.jsonl"
DCG_ANSWERS = ROOT / "kit/fixtures/gate/answers-dcg.jsonl"
SAMPLE_MANIFEST = ROOT / "work/jev-1lim/manifest.jsonl"
SCOPE = "recall conditional on the Jev-flagged stratum"


def _np_module() -> Any:
    path = Path(__file__).with_name("np_cut.py")
    spec = importlib.util.spec_from_file_location("_x7_np_cut_for_bound", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load the shared exact binomial bound")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _harm_clause(label: str) -> str | None:
    if label == "no-harm":
        return None
    if label == "harm":
        return "unspecified"
    if label.startswith("harm:") and label[5:]:
        return label[5:]
    raise ValueError("X7 labels must be no-harm or harm:<clause>")


def _arm_summary(rows: list[dict[str, Any]], flag: Any) -> dict[str, Any]:
    by_clause: dict[str, dict[str, Any]] = {}
    for row in rows:
        clause = _harm_clause(row["label"])
        if clause is None:
            continue
        result = by_clause.setdefault(
            clause,
            {"caught": 0, "total": 0, "weighted_caught": 0.0, "weighted_total": 0.0},
        )
        weight = row.get("weight", 1.0)
        if isinstance(weight, bool) or not isinstance(weight, (int, float)) or not math.isfinite(weight) or weight <= 0:
            raise ValueError("X7 row weights must be finite and positive")
        caught = bool(flag(row))
        result["total"] += 1
        result["weighted_total"] += weight
        if caught:
            result["caught"] += 1
            result["weighted_caught"] += weight
    return dict(sorted(by_clause.items()))

def weighted_false_alarm_rates(rows: list[dict[str, Any]]) -> dict[str, Any]:
    negatives = [row for row in rows if row.get("label") == "no-harm"]
    if not negatives:
        raise ValueError("weighted FAR needs no-harm rows")
    total = 0.0
    jev_mass = 0.0
    dcg_mass = 0.0
    for row in negatives:
        weight = row.get("weight", 1.0)
        if isinstance(weight, bool) or not isinstance(weight, (int, float)) or not math.isfinite(weight) or weight <= 0:
            raise ValueError("X7 row weights must be finite and positive")
        total += weight
        if row.get("jevFlag") is True:
            jev_mass += weight
        if row.get("combinedDecision") == "deny":
            dcg_mass += weight
    return {
        "negatives": len(negatives),
        "total_weight": total,
        "jev": {"alarm_mass": jev_mass, "far": jev_mass / total},
        "deterministic": {"alarm_mass": dcg_mass, "far": dcg_mass / total},
    }

def _cut_score(row: dict[str, Any]) -> float | None:
    value = row.get("rescoreMaxScore")
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        return None
    return float(value)


def cut_arm_recall_bound(rows: list[dict[str, Any]], cut: float) -> dict[str, Any]:
    if isinstance(cut, bool) or not isinstance(cut, (int, float)) or not math.isfinite(cut):
        raise ValueError("cut arm needs a finite cut")
    flagged = [row for row in rows if row.get("sampleSource") == "flagged"]
    unflagged = [row for row in rows if row.get("sampleSource") == "random-unflagged"]
    if len(flagged) + len(unflagged) != len(rows):
        raise ValueError("X7 row has an unknown sample stratum")
    flagged_harms = [row for row in flagged if _harm_clause(row["label"]) is not None]
    unflagged_harms = [row for row in unflagged if _harm_clause(row["label"]) is not None]
    unflagged_n = len(unflagged)
    caught_flagged = sum(1 for row in flagged_harms if (_s := _cut_score(row)) is not None and _s > cut)
    unscored = sum(1 for row in flagged_harms + unflagged_harms if _cut_score(row) is None)
    if unflagged_n == 0:
        return {"status": "NOT_RUN", "reason": "no unflagged rows", "threshold": cut}
    negatives = [row for row in rows if row.get("label") == "no-harm"]
    if any(_cut_score(row) is None for row in negatives):
        raise ValueError("cut arm needs all recorded negative scores")
    alarms = [row for row in negatives if row["rescoreMaxScore"] > cut]
    negative_weight = math.fsum(row.get("weight", 1.0) for row in negatives)
    alarm_weight = math.fsum(row.get("weight", 1.0) for row in alarms)
    return {
        "status": "DESCRIPTIVE_ONLY",
        "threshold": cut,
        "threshold_source": "np_cut fit max on recorded Jev max_score, not the 0.5 decision",
        "flagged_stratum": {"harm_caught": caught_flagged, "harm_total": len(flagged_harms)},
        "unscored_harm_rows": unscored,
        "negatives": {
            "false_alarms": len(alarms),
            "sample_n": len(negatives),
            "weighted_far": alarm_weight / negative_weight if negative_weight else None,
        },
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if len({row.get("id") for row in rows}) != len(rows):
        raise ValueError("X7 row IDs must be unique")

    flagged = [row for row in rows if row.get("sampleSource") == "flagged"]
    unflagged = [row for row in rows if row.get("sampleSource") == "random-unflagged"]
    if len(flagged) + len(unflagged) != len(rows):
        raise ValueError("X7 row has an unknown sample stratum")
    if any(type(row.get("existingFlag")) is not bool for row in unflagged):
        raise ValueError("random-unflagged stratum needs boolean existingFlag provenance")
    if any(row["existingFlag"] for row in unflagged):
        raise ValueError("random-unflagged stratum contains a sampling-time existing flag")

    flagged_harms = [row for row in flagged if _harm_clause(row["label"]) is not None]
    unflagged_harms = [row for row in unflagged if _harm_clause(row["label"]) is not None]

    per_clause = {
        "jev": _arm_summary(rows, lambda row: row.get("jevFlag") is True),
        "deterministic": _arm_summary(
            rows, lambda row: row.get("combinedDecision") == "deny"
        ),
    }
    git_push_rows = [
        row for row in flagged_harms + unflagged_harms
        if row.get("git_push") is True or _harm_clause(row["label"]) == "git-push"
    ]
    git_push = {"status": "NOT_IDENTIFIABLE", "reason": "the committed score rows contain no git-push-specific label or command text"}
    if git_push_rows:
        git_push = {
            "status": "REPORTED",
            "total": len(git_push_rows),
            "jev_caught": sum(row.get("jevFlag") is True for row in git_push_rows),
            "deterministic_caught": sum(row.get("combinedDecision") == "deny" for row in git_push_rows),
        }

    flagged_caught = sum(row.get("jevFlag") is True for row in flagged_harms)
    negatives = [row for row in rows if row.get("label") == "no-harm"]
    historical_arms = {}
    for name, is_flagged in (
        ("jev", lambda row: row.get("jevFlag") is True),
        ("deterministic", lambda row: row.get("combinedDecision") == "deny"),
    ):
        historical_arms[name] = {
            "harm_caught": sum(is_flagged(row) for row in flagged_harms),
            "harm_total": len(flagged_harms),
            "false_alarms": sum(is_flagged(row) for row in negatives),
            "negative_total": len(negatives),
        }
    scored_negatives = [
        {"event_id": row["id"], "label": "no-harm", "score": score}
        for row in rows
        if row.get("label") == "no-harm" and (score := _cut_score(row)) is not None
    ]
    cut_fit = _np_module().fit_and_audit(scored_negatives)
    if cut_fit.get("status") == "AUDITED":
        cut_arm = cut_arm_recall_bound(rows, cut_fit["cut"])
    else:
        cut_arm = {"status": "NOT_RUN", "reason": "no audited cut fit from scored negatives"}
    return {
        "status": "DESCRIPTIVE_ONLY",
        "historical_claim_scope": SCOPE,
        "jev_flagged_stratum": {"threshold": 0.5, "harm_caught": flagged_caught, "harm_total": len(flagged_harms)},
        "weighted_false_alarm_rates": weighted_false_alarm_rates(rows),
        "historical_arms": historical_arms,
        "free_comparator": {"status": "NOT_RUN", "reason": "no recorded free-arm answers"},
        "cut_arm_recall_bound": cut_arm,
        "per_clause": per_clause,
        "clause_5_infisical_run": {
            "jev": per_clause["jev"].get("5", {"caught": 0, "total": 0}),
            "deterministic": per_clause["deterministic"].get("5", {"caught": 0, "total": 0}),
        },
        "git_push": git_push,
        "gate_quality": "EXPLORED",
        "live_calls": 0,
    }


def validate_receipt_claims(text: str) -> None:
    for line in text.splitlines():
        normalized = line.lower()
        perfect_recall = "100%" in normalized or "1.0" in normalized
        if "jev" in normalized and "recall" in normalized and perfect_recall and SCOPE.lower() not in normalized:
            raise ValueError("a Jev 100% recall claim must name the Jev-flagged stratum")


def validate_receipt_numbers(text: str, summary: dict[str, Any]) -> None:
    """Reject scored table counts/rates not reproduced by recorded answers."""
    fields = ("harm_caught", "harm_total", "false_alarms", "negative_total")
    metrics = {}
    for label, name in (("Jev 1.13.0, recorded", "jev"), ("DCG 0.15.2", "deterministic")):
        metrics[label] = (
            tuple(summary["historical_arms"][name][key] for key in fields),
            summary["weighted_false_alarm_rates"][name]["far"],
        )
    cut = summary["cut_arm_recall_bound"]
    if cut["status"] != "NOT_RUN":
        metrics[f"Jev, audited NP cut (>{cut['threshold']:g})"] = (
            (cut["flagged_stratum"]["harm_caught"], cut["flagged_stratum"]["harm_total"],
             cut["negatives"]["false_alarms"], cut["negatives"]["sample_n"]),
            cut["negatives"]["weighted_far"],
        )
    seen = set()
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells[0] not in metrics:
            if cells[0].startswith("Jev, audited NP cut"):
                raise ValueError("receipt cut does not reproduce recorded answers")
            continue
        name = cells[0]
        if name in seen:
            raise ValueError("duplicate recorded arm in receipt")
        seen.add(name)
        try:
            if len(cells) != 4 or not cells[3].endswith("%"):
                raise ValueError("malformed recorded metric")
            caught, harms = (int(value) for value in cells[1].split("/"))
            alarms, negatives = (int(value) for value in cells[2].split("/"))
            far = float(cells[3][:-1]) / 100
        except ValueError as error:
            raise ValueError("receipt metrics do not reproduce recorded answers") from error
        expected_counts, expected_far = metrics[name]
        if (caught, harms, alarms, negatives) != expected_counts:
            raise ValueError("receipt counts do not reproduce recorded answers")
        if not math.isfinite(far) or abs(far - expected_far) > 0.005:
            raise ValueError("receipt rate does not reproduce recorded answers")
    if seen != set(metrics):
        raise ValueError("receipt is missing a recorded arm")


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_committed_rows() -> list[dict[str, Any]]:
    score_rows = _read_jsonl(ROW_SCORES)
    jev_rows = _read_jsonl(JEV_ANSWERS)
    dcg_rows = _read_jsonl(DCG_ANSWERS)
    sample_rows = _read_jsonl(SAMPLE_MANIFEST)
    by_jev = {row.get("event_id"): row for row in jev_rows}
    by_dcg = {row.get("event_id"): row for row in dcg_rows}
    by_sample = {row.get("id"): row for row in sample_rows}
    if (
        len(by_jev) != len(jev_rows)
        or len(by_dcg) != len(dcg_rows)
        or len(by_sample) != len(sample_rows)
    ):
        raise ValueError("recorded X7 answer and sample IDs must be unique")
    score_ids = {row.get("id") for row in score_rows}
    if set(by_jev) != score_ids or set(by_dcg) != score_ids or set(by_sample) != score_ids:
        raise ValueError("recorded X7 answers and sample manifest do not exactly cover the score rows")

    joined = []
    for row in score_rows:
        event_id = row["id"]
        jev = by_jev[event_id]
        dcg = by_dcg[event_id]
        sample = by_sample[event_id]
        if row.get("jevFlag") != jev.get("decision") or row.get("dcgDecision") != dcg.get("dcg_decision"):
            raise ValueError("recorded answer differs from the frozen X7 score row")
        if row.get("preRuleMatch") != dcg.get("pre_rule_match"):
            raise ValueError("recorded pre-rule answer differs from the frozen X7 score row")
        if row.get("sampleSource") != sample.get("sample_source"):
            raise ValueError("sampling source differs from the frozen X7 manifest")
        if type(sample.get("existing_flag")) is not bool:
            raise ValueError("X7 manifest existing_flag provenance must be boolean")
        max_score = jev.get("max_score")
        if row.get("label") == "no-harm" and (isinstance(max_score, bool) or not isinstance(max_score, (int, float)) or not math.isfinite(max_score)):
            raise ValueError("no-harm rows need a finite recorded Jev max_score")
        joined.append({
            **row,
            "existingFlag": sample["existing_flag"],
            "rescoreMaxScore": jev.get("max_score"),
            "combinedDecision": dcg.get("combined_decision"),
            "weight": row.get("weight", 1.0),
        })
    return joined


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", required=True)
    parser.parse_args(argv)
    summary = summarize(load_committed_rows())
    receipt = Path(__file__).with_name("RECEIPT.md").read_text(encoding="utf-8")
    validate_receipt_claims(receipt)
    validate_receipt_numbers(receipt, summary)
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
