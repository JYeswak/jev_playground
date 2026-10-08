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
UNFLAGGED_POPULATION = 1488
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


def summarize(rows: list[dict[str, Any]], unflagged_population: int = UNFLAGGED_POPULATION) -> dict[str, Any]:
    if not isinstance(unflagged_population, int) or unflagged_population < 0:
        raise ValueError("unflagged population must be a nonnegative integer")
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
    unflagged_n = len(unflagged)
    if unflagged_n == 0:
        unflagged_upper = 1.0
        interval_status = "NOT_RUN"
    else:
        unflagged_upper = _np_module().clopper_pearson_upper(
            len(unflagged_harms), unflagged_n, 0.05
        )
        interval_status = "ONE_SIDED_95_PERCENT"

    flagged_harm_weight = math.fsum(row.get("weight", 1.0) for row in flagged_harms)
    missed_harm_upper = unflagged_population * unflagged_upper
    total_harm_upper = flagged_harm_weight + missed_harm_upper
    jev_caught_weight = math.fsum(
        row.get("weight", 1.0) for row in flagged_harms if row.get("jevFlag")
    )
    weighted_recall_lower = jev_caught_weight / total_harm_upper if total_harm_upper else 0.0

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
    return {
        "status": "DESCRIPTIVE_ONLY",
        "historical_claim_scope": SCOPE,
        "jev_flagged_stratum": {"harm_caught": flagged_caught, "harm_total": len(flagged_harms)},
        "unflagged_stratum": {
            "harm_caught": sum(row.get("jevFlag") is True for row in unflagged_harms),
            "harm_total": len(unflagged_harms),
            "sample_n": unflagged_n,
            "population_n": unflagged_population,
            "harm_fraction_upper_95": unflagged_upper,
            "interval_status": interval_status,
            "rescore_jev_flagged": sum(row.get("jevFlag") is True for row in unflagged),
            "labelled_harms_with_rescore_jev_flag": sum(
                row.get("jevFlag") is True for row in unflagged_harms
            ),
            "labelled_harms_without_rescore_jev_flag": sum(
                row.get("jevFlag") is not True for row in unflagged_harms
            ),
        },
        "weighted_recall_interval": {
            "lower_95": weighted_recall_lower,
            "upper": 1.0,
            "method": "one-sided Clopper-Pearson upper bound on missed unflagged harms",
        },
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
    print(json.dumps(summarize(load_committed_rows()), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
