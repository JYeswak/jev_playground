#!/usr/bin/env python3
"""Reproducible offline scoring and bounded local Clef-Flash evaluation."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from collections.abc import Callable
from pathlib import Path
from typing import Any, Optional

ROOT = Path(__file__).resolve().parents[2]
DATA = Path("/Users/josh/Developer/omp-test/var/agent-tmp/planning-retro")
FILES = (
    "findings-omp-kit.jsonl",
    "findings-localbench.jsonl",
    "findings-cfsios.jsonl",
    "findings-uds.jsonl",
)
ENDPOINT = "http://127.0.0.1:8010/v1/systemone"
MODEL = "clef-flash"
SEED = 20261005
MAX_CALLS = 700
OPTIONS = (
    "SCOPE_GAP",
    "FALSE_CLAIM",
    "MISSING_EDGE",
    "PRIORITY",
    "PINNED_LIVE_VALUE",
    "UNDEFINED_TERM",
    "STALE_TEXT",
    "CYCLE",
    "DUPLICATE",
    "OVERSCOPE",
    "OTHER",
)
INSTRUCTIONS = (
    "Assign the single best canonical process-finding class to this one-sentence finding. "
    "Choose exactly one offered class. SCOPE_GAP means acceptance fails to test a promise; "
    "FALSE_CLAIM means stated status contradicts code or tracker; MISSING_EDGE means a needed "
    "dependency or behavior link is absent; PRIORITY means ordering or urgency is wrong; "
    "PINNED_LIVE_VALUE means a live value/model/threshold is stale or unpinned; UNDEFINED_TERM "
    "means implementers cannot act because a term is unclear; STALE_TEXT means docs or instructions "
    "are outdated; CYCLE means dependency cycle; DUPLICATE means duplicate work; OVERSCOPE means "
    "work exceeds its acceptance; OTHER means none of these fit."
)


def canonical(label: str) -> str:
    return "OTHER" if label.startswith("OTHER:") else label


def load_rows(data_dir: Path = DATA) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for filename in FILES:
        path = data_dir / filename
        with path.open(encoding="utf-8") as stream:
            for line_no, line in enumerate(stream, 1):
                if not line.strip():
                    continue
                raw = json.loads(line)
                text, label = raw.get("finding"), raw.get("class")
                if (
                    not isinstance(text, str)
                    or not text.strip()
                    or not isinstance(label, str)
                ):
                    raise ValueError(f"invalid source row {filename}:{line_no}")
                label = canonical(label)
                if label not in OPTIONS:
                    raise ValueError(f"unknown canonical class in {filename}:{line_no}")
                source_id = f"{filename}:{line_no}"
                row_id = hashlib.sha256(source_id.encode()).hexdigest()
                rows.append(
                    {
                        "row_id": row_id,
                        "source_repo": raw.get("repo")
                        or filename.removeprefix("findings-").removesuffix(".jsonl"),
                        "sentence_sha256": hashlib.sha256(
                            text.encode("utf-8")
                        ).hexdigest(),
                        "finding": text,
                        "truth": label,
                        "split": "",
                    }
                )
    return rows


def assign_split(rows: list[dict[str, Any]], seed: int = SEED) -> None:
    by_repo: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_repo[row["source_repo"]].append(row)
    for repo_rows in by_repo.values():
        repo_rows.sort(key=lambda row: row["row_id"])
        random.Random(seed).shuffle(repo_rows)  # nosec B311: seeded reproducible split, not security
        for index, row in enumerate(repo_rows):
            row["split"] = "dev" if index % 2 == 0 else "held-out"


def fit_majority(dev_rows: list[dict[str, Any]]) -> str:
    if not dev_rows or any(row.get("split") != "dev" for row in dev_rows):
        raise ValueError("majority incumbent must fit only on dev rows")
    counts = Counter(row["truth"] for row in dev_rows)
    return min(OPTIONS, key=lambda label: (-counts[label], OPTIONS.index(label)))


def tokens(text: str) -> list[str]:
    punctuation = ".,:;!?()[]{}\"'`"
    return [
        word.casefold().strip(punctuation)
        for word in text.split()
        if word.casefold().strip(punctuation)
    ]


def fit_keyword_rule(
    dev_rows: list[dict[str, Any]],
    heldout_rows: Optional[list[dict[str, Any]]] = None,  # noqa: UP045
) -> dict[str, Counter[str]]:
    held_ids = {row["row_id"] for row in heldout_rows or []}
    dev_ids = {row["row_id"] for row in dev_rows}
    if dev_ids & held_ids or any(row.get("split") != "dev" for row in dev_rows):
        raise ValueError("keyword rule leakage: fit rows must be disjoint dev rows")
    by_token: dict[str, Counter[str]] = defaultdict(Counter)
    for row in dev_rows:
        for token in set(tokens(row["finding"])):
            by_token[token][row["truth"]] += 1
    return dict(by_token)


def predict_keyword(text: str, rule: dict[str, Counter[str]], majority: str) -> str:
    scores: Counter[str] = Counter()
    for token in set(tokens(text)):
        scores.update(rule.get(token, {}))
    return (
        min(OPTIONS, key=lambda label: (-scores[label], OPTIONS.index(label)))
        if scores
        else majority
    )


def validate_answer(
    answer: Any, probabilities: Any
) -> tuple[Optional[str], Optional[dict[str, float]], Optional[str]]:  # noqa: UP045
    if not isinstance(answer, str) or answer not in OPTIONS:
        return None, None, "choice_not_offered"
    if not isinstance(probabilities, dict) or set(probabilities) != set(OPTIONS):
        return None, None, "probabilities_missing_or_incomplete"
    if any(
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or not math.isfinite(value)
        or not 0 <= value <= 1
        for value in probabilities.values()
    ):
        return None, None, "invalid_probability"
    total = sum(probabilities.values())
    if abs(total - 1) > 0.02:
        return None, None, "probabilities_do_not_sum_to_one"
    if probabilities[answer] < max(probabilities.values()):
        return None, None, "choice_not_probability_maximum"
    return answer, {key: float(value) for key, value in probabilities.items()}, None


def build_request_payload(finding: str) -> dict[str, Any]:
    return {
        "model": MODEL,
        "state": {"finding": finding},
        "questions": {
            "cls": {
                "type": "choice",
                "criteria": {label: None for label in OPTIONS},
                "instructions": INSTRUCTIONS,
            }
        },
    }


def request_local(finding: str, timeout: float = 30) -> dict[str, Any]:
    payload = build_request_payload(finding)
    request = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = time.monotonic()
    with urllib.request.urlopen(request, timeout=timeout) as response:  # nosec B310: endpoint is a pinned loopback URL
        body = json.loads(response.read())
    elapsed = (time.monotonic() - started) * 1000
    raw = body["answers"]["cls"]
    return {
        "choice": raw.get("choice"),
        "probabilities": raw.get("probabilities"),
        "latency_ms": elapsed,
        "model": body.get("model", MODEL),
    }


def run_predictions(
    heldout_rows: list[dict[str, Any]],
    transport: Callable[[str], dict[str, Any]],
    max_calls: int = MAX_CALLS,
) -> list[dict[str, Any]]:
    if max_calls < 0 or max_calls > MAX_CALLS:
        raise ValueError("call cap must be within 0..700")
    output = []
    for row in heldout_rows[:max_calls]:
        base = {
            key: row[key]
            for key in (
                "row_id",
                "sentence_sha256",
                "truth",
                "split",
                "source_repo",
                "keyword_pred",
                "majority_pred",
            )
        }
        base["offered_classes"] = list(OPTIONS)
        base["expected_heldout_n"] = len(heldout_rows)
        try:
            result = transport(row["finding"])
        except (
            OSError,
            ValueError,
            KeyError,
            TypeError,
            AttributeError,
            urllib.error.URLError,
            TimeoutError,
        ) as exc:
            output.append(
                {
                    **base,
                    "status": "ERROR",
                    "error_class": type(exc).__name__,
                    "model": MODEL,
                }
            )
            break
        choice, probabilities, refusal = validate_answer(
            result.get("choice"), result.get("probabilities")
        )
        output.append(
            {
                **base,
                "status": "NOT_SCORED" if refusal else "scored",
                "answer": choice,
                "probabilities": probabilities,
                "refusal": refusal,
                "latency_ms": result.get("latency_ms"),
                "model": result.get("model", MODEL),
            }
        )
    return output


def accuracy(y_true: list[str], y_pred: list[str]) -> float:
    return sum(a == b for a, b in zip(y_true, y_pred)) / len(y_true) if y_true else 0.0


def macro_f1(y_true: list[str], y_pred: list[str]) -> float:
    if not y_true:
        return 0.0
    values = []
    for label in OPTIONS:
        tp = sum(a == label and b == label for a, b in zip(y_true, y_pred))
        fp = sum(a != label and b == label for a, b in zip(y_true, y_pred))
        fn = sum(a == label and b != label for a, b in zip(y_true, y_pred))
        values.append(2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.0)
    return sum(values) / len(values)


def exact_mcnemar_p(y_true: list[str], clef: list[str], rule: list[str]) -> float:
    clef_only = sum(c == y and r != y for y, c, r in zip(y_true, clef, rule))
    rule_only = sum(r == y and c != y for y, c, r in zip(y_true, clef, rule))
    n = clef_only + rule_only
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, k) for k in range(min(clef_only, rule_only) + 1)) / (2**n)
    return min(1.0, 2 * tail)


def score_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    valid = [
        row
        for row in rows
        if row.get("status") == "scored" and isinstance(row.get("answer"), str)
    ]
    y = [row["truth"] for row in valid]
    predictions = {
        "clef": [row["answer"] for row in valid],
        "keyword": [row["keyword_pred"] for row in valid],
        "majority": [row["majority_pred"] for row in valid],
    }
    arms = {
        name: {
            "n": len(y),
            "accuracy": accuracy(y, pred),
            "macro_f1": macro_f1(y, pred),
        }
        for name, pred in predictions.items()
    }
    top5 = sorted(
        OPTIONS,
        key=lambda label: (-sum(actual == label for actual in y), OPTIONS.index(label)),
    )[:5]
    confusion = {
        actual: {
            pred: sum(row["truth"] == actual and row["answer"] == pred for row in valid)
            for pred in OPTIONS
        }
        for actual in top5
    }
    latencies = sorted(
        row["latency_ms"]
        for row in valid
        if isinstance(row.get("latency_ms"), (int, float))
    )
    median_latency = (
        (latencies[(len(latencies) - 1) // 2] + latencies[len(latencies) // 2]) / 2
        if latencies
        else None
    )
    expected = max((row.get("expected_heldout_n", 0) for row in rows), default=0)
    mcnemar = exact_mcnemar_p(y, predictions["clef"], predictions["keyword"])
    beats = (
        len(valid) == expected
        and arms["clef"]["accuracy"] > arms["keyword"]["accuracy"]
        and arms["clef"]["macro_f1"] > arms["keyword"]["macro_f1"]
        and mcnemar < 0.05
    )
    return {
        "arms": arms,
        "mcnemar_p": mcnemar,
        "expected_heldout_n": expected,
        "valid_rows": len(valid),
        "not_scored": len(rows) - len(valid),
        "top5_confusion": confusion,
        "median_latency_ms": median_latency,
        "verdict": "BEATS-BAR" if beats else "LOSES",
    }


def read_prior_attempts(
    path: Path, first_row_id: str, expected_n: int, recovery_authorized: bool
) -> list[dict[str, Any]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    prior = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if not recovery_authorized:
        raise FileExistsError(f"refusing to overwrite existing call ledger: {path}")
    if (
        len(prior) != 1
        or prior[0].get("status") != "ERROR"
        or prior[0].get("error_class") != "HTTPError"
        or prior[0].get("row_id") != first_row_id
        or prior[0].get("expected_heldout_n") != expected_n
    ):
        raise ValueError("recovery requires the single recorded first-row HTTP failure")
    return prior


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--score-only", type=Path)
    parser.add_argument("--recovery-authorized", action="store_true")
    args = parser.parse_args()
    if args.score_only:
        rows = [
            json.loads(line)
            for line in args.score_only.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        print(json.dumps(score_rows(rows), sort_keys=True))
        return 0
    rows = load_rows()
    assign_split(rows)
    dev = [row for row in rows if row["split"] == "dev"]
    heldout = [row for row in rows if row["split"] == "held-out"]
    majority = fit_majority(dev)
    rule = fit_keyword_rule(dev, heldout)
    for row in heldout:
        row["keyword_pred"] = predict_keyword(row["finding"], rule, majority)
        row["majority_pred"] = majority
    out = ROOT / "work/lesson-class/rows.jsonl"
    prior = read_prior_attempts(
        out, heldout[0]["row_id"], len(heldout), args.recovery_authorized
    )
    if len(prior) + len(heldout) > MAX_CALLS:
        raise ValueError("recovery plus held-out rows exceeds the total call cap")
    calls = run_predictions(heldout, request_local, MAX_CALLS - len(prior))
    with out.open("a" if out.exists() else "x", encoding="utf-8") as stream:
        for row in calls:
            stream.write(json.dumps(row, sort_keys=True, allow_nan=False) + "\n")
    attempts = prior + calls
    errors = sum(row["status"] == "ERROR" for row in attempts)
    print(
        json.dumps(
            {
                "new_calls": len(calls),
                "rows": len(heldout),
                "prior_attempts": len(prior),
                "total_attempts": len(attempts),
                "scored": sum(row["status"] == "scored" for row in attempts),
                "errors": errors,
            }
        )
    )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
