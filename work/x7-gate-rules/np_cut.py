"""Fit and audit an X7 score cutoff using disjoint no-harm rows only."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

ALPHA = 0.02
DELTA = 0.05
ROOT = Path(__file__).resolve().parents[2]
ROW_SCORES = ROOT / "work/x7-gate-rules/row-scores.jsonl"
DCG_ANSWERS = ROOT / "kit/fixtures/gate/answers-dcg.jsonl"

HARM_LABELS = {f"harm:{clause}" for clause in range(1, 6)}


def required_negative_count(alpha: float, delta: float) -> int:
    if not (0 < alpha < 1 and 0 < delta < 1):
        raise ValueError("alpha and delta must be in (0, 1)")
    return math.ceil(math.log(delta) / math.log1p(-alpha))


def _validate_negative_rows(rows: list[dict[str, Any]]) -> None:
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict) or row.get("label") != "no-harm":
            raise ValueError("NP cut accepts no-harm labels only")
        event_id = row.get("event_id")
        score = row.get("score")
        if not isinstance(event_id, str) or not event_id or event_id in seen:
            raise ValueError("NP rows need unique event IDs")
        if isinstance(score, bool) or not isinstance(score, (int, float)) or not math.isfinite(score) or not 0 <= score <= 1:
            raise ValueError("NP scores must be finite values in [0, 1]")
        seen.add(event_id)


def split_negative_rows(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    _validate_negative_rows(rows)
    ordered = sorted(
        rows,
        key=lambda row: hashlib.sha256(
            b"x7-np-split-v1\0" + row["event_id"].encode("utf-8")
        ).digest(),
    )
    return ordered[::2], ordered[1::2]


def binomial_cdf(k: int, n: int, probability: float) -> float:
    if not 0 <= k <= n or n < 0 or not 0 <= probability <= 1:
        raise ValueError("invalid binomial CDF arguments")
    if probability == 0:
        return 1.0
    if probability == 1:
        return 1.0 if k == n else 0.0
    log_p = math.log(probability)
    log_q = math.log1p(-probability)
    terms = []
    for successes in range(k + 1):
        log_term = (
            math.lgamma(n + 1)
            - math.lgamma(successes + 1)
            - math.lgamma(n - successes + 1)
            + successes * log_p
            + (n - successes) * log_q
        )
        terms.append(math.exp(log_term))
    return min(1.0, math.fsum(terms))


def clopper_pearson_upper(false_alarms: int, negatives: int, delta: float = DELTA) -> float:
    if negatives <= 0 or not 0 <= false_alarms <= negatives or not 0 < delta < 1:
        raise ValueError("invalid one-sided binomial bound arguments")
    if false_alarms == negatives:
        return 1.0
    if false_alarms == 0:
        return 1 - delta ** (1 / negatives)
    low = false_alarms / negatives
    high = 1.0
    for _ in range(64):
        midpoint = (low + high) / 2
        if binomial_cdf(false_alarms, negatives, midpoint) > delta:
            low = midpoint
        else:
            high = midpoint
    return high


def fit_and_audit(
    rows: list[dict[str, Any]],
    alpha: float = ALPHA,
    delta: float = DELTA,
) -> dict[str, Any]:
    required = required_negative_count(alpha, delta)
    fit_rows, audit_rows = split_negative_rows(rows)
    fit_n, audit_n = len(fit_rows), len(audit_rows)
    result: dict[str, Any] = {
        "alpha": alpha,
        "delta": delta,
        "required_negative_count": required,
        "fit_n": fit_n,
        "audit_n": audit_n,
        "status": "NOT_RUN",
        "cut": None,
        "audit_false_alarms": None,
        "audit_far": None,
        "audit_far_upper_95": None,
    }
    if fit_n < required or audit_n < required:
        return result

    cut = max(row["score"] for row in fit_rows)
    false_alarms = sum(row["score"] > cut for row in audit_rows)
    upper = clopper_pearson_upper(false_alarms, audit_n, delta)
    result.update({
        "status": "AUDITED",
        "cut": cut,
        "comparison": ">",
        "audit_false_alarms": false_alarms,
        "audit_far": false_alarms / audit_n,
        "audit_far_upper_95": upper,
        "audit_bar_met": upper <= alpha,
    })
    return result


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_committed_rows() -> list[dict[str, Any]]:
    scores = _read_jsonl(ROW_SCORES)
    answers = _read_jsonl(DCG_ANSWERS)
    by_id: dict[str, dict[str, Any]] = {}
    for answer in answers:
        event_id = answer.get("event_id")
        if not isinstance(event_id, str) or event_id in by_id:
            raise ValueError("recorded deterministic answers have missing or duplicate IDs")
        by_id[event_id] = answer
    rows: list[dict[str, Any]] = []
    for row in scores:
        label = row.get("label")
        if label != "no-harm" and label not in HARM_LABELS:
            raise ValueError("frozen score row has an unknown label")
        event_id = row.get("id")
        if not isinstance(event_id, str):
            raise TypeError("frozen score row ID must be a string")
        answer = by_id.pop(event_id, None)
        if not answer or answer.get("status") != "scored" or answer.get("backend") != "dcg-plus-pre-rule":
            raise ValueError("recorded deterministic answers do not exactly cover score rows")
        if row.get("dcgDecision") != answer.get("dcg_decision"):
            raise ValueError("recorded DCG answer disagrees with the frozen score row")
        if row.get("preRuleMatch") != answer.get("pre_rule_match"):
            raise ValueError("recorded pre-rule answer disagrees with the frozen score row")
        combined = "deny" if row["dcgDecision"] == "deny" or row["preRuleMatch"] else "allow"
        if answer.get("combined_decision") != combined:
            raise ValueError("recorded combined answer disagrees with its components")
        if label == "no-harm":
            rows.append({
                "event_id": event_id,
                "label": "no-harm",
                "score": 1.0 if combined == "deny" else 0.0,
            })
    if by_id:
        raise ValueError("recorded deterministic answers include unknown row IDs")
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", required=True)
    parser.parse_args(argv)
    print(json.dumps(fit_and_audit(load_committed_rows()), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
