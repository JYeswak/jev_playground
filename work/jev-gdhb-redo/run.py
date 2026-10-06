#!/usr/bin/env python3
"""Frozen MASSIVE intent evaluation using only local Clef-Flash behind localbench."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import time
import unicodedata
import urllib.error
import urllib.request
from collections import Counter
from collections.abc import Callable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
WORK = Path(__file__).resolve().parent
CORPUS = WORK / "corpus.jsonl"
PREREG = WORK / "PREREG.md"
RESULTS = WORK / "rows.jsonl"
RECEIPT = WORK / "RECEIPT.md"

DATASET_REVISION = "AmazonScience/MASSIVE 1.1; en-US; test"
ARCHIVE_URL = "https://amazon-massive-nlu-dataset.s3.amazonaws.com/amazon-massive-dataset-1.1.tar.gz"
ARCHIVE_SHA256 = "4cba5faa11c71437928e17cb1b9b3d8b8e727e7ea363a3a9a8045e19c0491577"
ARCHIVE_MEMBER = "1.1/data/en-US.jsonl"
SAMPLE_SEED = "jev-gdhb-massive-1.1-en-US-test-cap18-v1"
PER_INTENT_CAP = 18
EXPECTED_ROWS = 954
EXPECTED_LABELS = 59

CLEF_MODEL = "clef-flash"
CLEF_IDENTITY_URL = "http://127.0.0.1:11300/jev/clef-flash/"
CLEF_ENDPOINT_URL = "http://127.0.0.1:11300/jev/clef-flash/classify"
CLEF_ROUTE = "classify"
LOCALBENCH_REQUEST_ID_HEADER = "X-Localbench-Request-Id"
QUESTION_NAME = "intent"
QUESTION_INSTRUCTIONS = "Which intent best matches this spoken voice-assistant request?"
MAX_INVALID_RATE = 0.05

PRIOR_CORPORA = (
    "work/choice-banking77/full.jsonl",
    "work/choice-clinc150/full.jsonl",
    "work/jev-gdhb/corpus.jsonl",
)

# Updated only with the preregistration and corpus before any Clef inference.
EXPECTED_CORPUS_SHA256 = "4909490e7a8efabfc4e97eee6a58bee04ac3d634cae02224f82ffdb9b9f9d5b1"
EXPECTED_SPEC_SHA256 = "5ec621e64ca404f372619361da1044c7bd440c234d4570cb0b77fd045a32e3f9"
EXPECTED_PREREG_SHA256 = "4295ac4d88132b7919829fb67bb8d42debd8163ed0d8354e5b2eda27eed911d5"


class PreflightError(RuntimeError):
    """A frozen artifact or local Clef readiness check failed."""


class RunStop(RuntimeError):
    """A single-pass run must stop without retries or fallback."""


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(
        self,
        req: urllib.request.Request,
        fp: Any,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> None:
        return None


# Explicitly bypass HTTP(S)_PROXY and refuse redirects: utterances stay on loopback.
LOCAL_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}), _NoRedirect())


IdentityRequest = Callable[[str], dict[str, Any]]
Transport = Callable[[str], dict[str, Any]]


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as source:
        for line_number, line in enumerate(source, 1):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as error:
                raise PreflightError(f"invalid JSON at {path}:{line_number}: {error.msg}") from error
            if not isinstance(item, dict):
                raise PreflightError(f"non-object row at {path}:{line_number}")
            rows.append(item)
    return rows


def normalize_text(text: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def collect_prior_texts(extra: set[str] | None = None) -> tuple[dict[str, str], set[str]]:
    hashes: dict[str, str] = {}
    texts = set(extra or ())
    for relative in PRIOR_CORPORA:
        path = ROOT / relative
        if not path.is_file():
            raise PreflightError(f"prior intent corpus required for overlap check is missing: {relative}")
        hashes[relative] = sha256_file(path)
        for row in load_jsonl(path):
            for key in ("text", "utterance", "utt"):
                value = row.get(key)
                if isinstance(value, str) and value.strip():
                    texts.add(normalize_text(value))
    return hashes, texts


def build_spec(rows: list[dict[str, Any]], corpus_sha: str, prior_hashes: dict[str, str]) -> dict[str, Any]:
    labels = sorted({row["gold"] for row in rows})
    counts = Counter(row["gold"] for row in rows)
    return {
        "dataset": {
            "name_revision_split": DATASET_REVISION,
            "archive_url": ARCHIVE_URL,
            "archive_sha256": ARCHIVE_SHA256,
            "archive_member": ARCHIVE_MEMBER,
            "license": "CC BY 4.0",
        },
        "sample": {
            "algorithm": "exclude NFKC/casefold/whitespace-normalized utterances matching the three frozen prior corpora; for each remaining observed intent, rank test rows by SHA-256(seed|source_id), then take the first cap",
            "seed": SAMPLE_SEED,
            "cap_per_intent": PER_INTENT_CAP,
            "row_count": len(rows),
            "labels": labels,
            "counts_by_label": dict(sorted(counts.items())),
            "corpus_sha256": corpus_sha,
        },
        "question": {
            "name": QUESTION_NAME,
            "instructions": QUESTION_INSTRUCTIONS,
            "state": {"customer_message": "<the verbatim MASSIVE utterance>"},
            "choice_labels": labels,
            "criteria_description_rule": "replace each choice label underscore with a space",
            "one_row_per_request": True,
        },
        "response_validation": "model id is exactly clef-flash; choice is offered; probability keys exactly match all offered labels; all probabilities are finite and in [0,1]; probabilities sum to 1 within 0.02; selected choice has maximum probability; supplied confidence is finite and in [0,1]",
        "models": {
            "clef": CLEF_MODEL,
            "endpoint": CLEF_ENDPOINT_URL,
            "jev_arm": "NOT_RUN",
        },
        "execution": {"concurrency": 1, "retries": 0},
        "cost_usd": 0.0,
        "guard": {
            "local_only": True,
            "request_id_header": LOCALBENCH_REQUEST_ID_HEADER,
            "route_feature": "jev-classify",
        },
        "scoring": {
            "primary_metric": "exact-match accuracy over the complete fixed corpus",
            "invalid_threshold": MAX_INVALID_RATE,
            "comparison": "descriptive Clef-only measurement; Jev arm is NOT_RUN",
        },
        "overlap_sources_sha256": prior_hashes,
    }


def parse_declared_spec_sha(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("SPEC_SHA256: "):
            value = line.partition(": ")[2].strip()
            if len(value) == 64:
                return value
    raise PreflightError("PREREG.md has no valid SPEC_SHA256 binding")


def request_identity(url: str = CLEF_IDENTITY_URL) -> dict[str, Any]:
    if url != CLEF_IDENTITY_URL:
        raise PreflightError("identity URL differs from the pinned local Clef endpoint")
    request = urllib.request.Request(url, method="GET")
    try:
        with LOCAL_OPENER.open(request, timeout=5) as response:
            if response.geturl() != url:
                raise PreflightError("Clef identity endpoint redirected")
            data = json.loads(response.read())
    except (OSError, urllib.error.URLError, json.JSONDecodeError, UnicodeDecodeError) as error:
        raise PreflightError(f"local Clef identity check failed: {type(error).__name__}") from error
    if not isinstance(data, dict):
        raise PreflightError("local Clef identity response is not an object")
    return data


def check_frozen(
    *,
    expected_prereg_sha: str = EXPECTED_PREREG_SHA256,
    extra_overlap: set[str] | None = None,
    identity_fn: IdentityRequest | None = None,
    results_path: Path | None = RESULTS,
) -> dict[str, Any]:
    if not CORPUS.is_file() or not PREREG.is_file():
        raise PreflightError("frozen corpus or preregistration file is missing")
    corpus_sha = sha256_file(CORPUS)
    prereg_text = PREREG.read_text(encoding="utf-8")
    prereg_sha = sha256_bytes(prereg_text.encode("utf-8"))
    if corpus_sha != EXPECTED_CORPUS_SHA256:
        raise PreflightError("corpus SHA-256 differs from the frozen runner pin")
    if prereg_sha != expected_prereg_sha or prereg_sha == "UNBOUND":
        raise PreflightError("PREREG.md SHA-256 differs from the frozen runner pin")

    rows = load_jsonl(CORPUS)
    if len(rows) != EXPECTED_ROWS:
        raise PreflightError(f"expected exactly {EXPECTED_ROWS} frozen rows, found {len(rows)}")
    ids = [row.get("id") for row in rows]
    if len(set(ids)) != len(ids):
        raise PreflightError("corpus contains duplicate row ids")
    if any(not isinstance(row.get("text"), str) or not row["text"].strip() for row in rows):
        raise PreflightError("corpus contains an empty or invalid utterance")
    if any(not isinstance(row.get("gold"), str) or not row["gold"].strip() for row in rows):
        raise PreflightError("corpus contains a missing or invalid intent label")
    labels = sorted({row["gold"] for row in rows})
    if len(labels) != EXPECTED_LABELS:
        raise PreflightError(f"expected {EXPECTED_LABELS} fixed intent labels, found {len(labels)}")

    prior_hashes, prior_texts = collect_prior_texts(extra_overlap)
    if set(prior_hashes) != set(PRIOR_CORPORA):
        raise PreflightError("overlap-source inventory changed")
    overlap = [row["id"] for row in rows if normalize_text(row["text"]) in prior_texts]
    if overlap:
        raise PreflightError(f"overlap with a prior intent corpus: {overlap[0]}")

    spec_sha = sha256_bytes(canonical_json(build_spec(rows, corpus_sha, prior_hashes)))
    if spec_sha != parse_declared_spec_sha(prereg_text) or spec_sha != EXPECTED_SPEC_SHA256:
        raise PreflightError("model, prompt, sample, guard, score, or overlap spec differs from its frozen hash")
    if results_path is not None and results_path.is_file() and results_path.stat().st_size:
        raise PreflightError("rows.jsonl is non-empty; refusing automatic retry or resume")

    identity = (identity_fn or request_identity)(CLEF_IDENTITY_URL)
    models = identity.get("models")
    if not isinstance(models, list) or not any(
        isinstance(model, dict) and model.get("id") == CLEF_MODEL for model in models
    ):
        raise PreflightError("local endpoint does not report the pinned clef-flash model")

    counts = Counter(row["gold"] for row in rows)
    return {
        "status": "READY",
        "rows": len(rows),
        "labels": len(labels),
        "corpus_sha256": corpus_sha,
        "prereg_sha256": prereg_sha,
        "spec_sha256": spec_sha,
        "runner_sha256": sha256_file(Path(__file__)),
        "prior_corpus_sha256": prior_hashes,
        "overlap_rows": 0,
        "clef_identity": CLEF_MODEL,
        "endpoint": CLEF_ENDPOINT_URL,
        "request_cap": len(rows),
        "concurrency": 1,
        "retries": 0,
        "cost_usd": 0.0,
        "jev_arm_status": "NOT_RUN",
        "majority_count": max(counts.values()),
        "majority_accuracy": max(counts.values()) / len(rows),
    }


def build_request_payload(utterance: str, labels: list[str]) -> dict[str, Any]:
    if not utterance.strip() or not labels or len(set(labels)) != len(labels):
        raise ValueError("request requires a non-empty utterance and unique offered labels")
    return {
        "model": CLEF_MODEL,
        "state": {"customer_message": utterance},
        "questions": {
            QUESTION_NAME: {
                "type": "choice",
                "criteria": {label: label.replace("_", " ") for label in labels},
                "instructions": QUESTION_INSTRUCTIONS,
            }
        },
    }


def validate_answer(
    choice: Any,
    probabilities: Any,
    labels: list[str],
    confidence: Any = None,
) -> str | None:
    if not isinstance(choice, str) or choice not in labels:
        return "choice_not_offered"
    if not isinstance(probabilities, dict) or set(probabilities) != set(labels):
        return "probability_keys_differ_from_offered_labels"
    values: list[float] = []
    for label in labels:
        value = probabilities[label]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return "probability_not_numeric"
        if not math.isfinite(value) or not 0 <= value <= 1:
            return "probability_out_of_range"
        values.append(float(value))
    if abs(math.fsum(values) - 1.0) > 0.02:
        return "probabilities_do_not_sum_to_one"
    if probabilities[choice] < max(values):
        return "choice_not_probability_maximum"
    if confidence is not None and (
        isinstance(confidence, bool)
        or not isinstance(confidence, (int, float))
        or not math.isfinite(confidence)
        or not 0 <= confidence <= 1
    ):
        return "confidence_out_of_range"
    return None


def request_local(utterance: str) -> dict[str, Any]:
    labels = sorted({row["gold"] for row in load_jsonl(CORPUS)})
    payload = build_request_payload(utterance, labels)
    body = json.dumps(payload, ensure_ascii=False, allow_nan=False).encode("utf-8")
    request = urllib.request.Request(
        CLEF_ENDPOINT_URL,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = time.perf_counter()
    with LOCAL_OPENER.open(request, timeout=30) as response:
        if response.geturl() != CLEF_ENDPOINT_URL:
            raise RunStop("localbench Clef endpoint redirected")
        request_id = response.headers.get(LOCALBENCH_REQUEST_ID_HEADER)
        if not isinstance(request_id, str) or not request_id.strip():
            raise RunStop("response lacks localbench guard request id")
        try:
            data = json.loads(response.read())
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise RunStop("local Clef response is not valid JSON") from error
    if not isinstance(data, dict):
        raise TypeError("Clef response is not an object")
    answers = data.get("answers")
    if not isinstance(answers, dict):
        raise TypeError("Clef response answers are not an object")
    answer = answers.get(QUESTION_NAME)
    if not isinstance(answer, dict):
        raise TypeError("Clef response intent answer is not an object")
    model = data.get("model")
    if not isinstance(model, str):
        raise TypeError("Clef response model id is missing or not a string")
    return {
        "choice": answer.get("choice"),
        "probabilities": answer.get("probabilities"),
        "confidence": answer.get("confidence"),
        "latency_ms": round((time.perf_counter() - started) * 1000),
        "model": model,
        "localbench_request_id": request_id,
    }


def append_result(row: dict[str, Any], path: Path) -> None:
    with path.open("a", encoding="utf-8", newline="\n") as target:
        target.write(json.dumps(row, ensure_ascii=False, sort_keys=True, allow_nan=False) + "\n")
        target.flush()
        os.fsync(target.fileno())


def run_predictions(
    rows: list[dict[str, Any]],
    transport: Transport,
    *,
    results_path: Path | None = None,
) -> list[dict[str, Any]]:
    if not rows or len(rows) > EXPECTED_ROWS:
        raise ValueError(f"request count must be between 1 and {EXPECTED_ROWS}")
    labels = sorted({row["gold"] for row in rows})
    predictions: list[dict[str, Any]] = []
    for row in rows:
        record: dict[str, Any] = {
            "row_id": row["id"],
            "gold": row["gold"],
            "arm": "clef",
            "model": CLEF_MODEL,
            "attempts": 1,
            "jev_arm_status": "NOT_RUN",
            "cost_usd": 0.0,
        }
        try:
            result = transport(row["text"])
            if not isinstance(result, dict):
                raise TypeError("Clef transport returned a non-object")
            if result.get("model") != CLEF_MODEL:
                raise RunStop("Clef response model differs from the frozen model id")
            invalid_reason = validate_answer(
                result.get("choice"),
                result.get("probabilities"),
                labels,
                result.get("confidence"),
            )
        except (OSError, urllib.error.URLError, ValueError, TypeError, KeyError, TimeoutError, RunStop) as error:
            record.update(
                status="ERROR",
                error_class=type(error).__name__,
                http_status=getattr(error, "code", None),
            )
            predictions.append(record)
            if results_path is not None:
                append_result(record, results_path)
            break

        record.update(
            status="invalid" if invalid_reason else "scored",
            latency_ms=result.get("latency_ms"),
            localbench_request_id=result.get("localbench_request_id"),
        )
        if invalid_reason:
            record["invalid_reason"] = invalid_reason
            choice = result.get("choice")
            record["choice"] = choice if isinstance(choice, str) else None
        else:
            record["choice"] = result["choice"]
            record["probabilities"] = result["probabilities"]
            record["confidence"] = result.get("confidence")
        predictions.append(record)
        if results_path is not None:
            append_result(record, results_path)
    return predictions


def score_completed(rows: list[dict[str, Any]], predictions: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows or len(predictions) != len(rows):
        raise RunStop("complete one-per-row Clef results are required before scoring")
    by_id: dict[str, dict[str, Any]] = {}
    expected_ids = {row["id"] for row in rows}
    for prediction in predictions:
        row_id = prediction.get("row_id")
        if not isinstance(row_id, str) or row_id not in expected_ids or row_id in by_id:
            raise RunStop("duplicate or unexpected row id in Clef results")
        by_id[row_id] = prediction
    if set(by_id) != expected_ids:
        raise RunStop("Clef results do not cover the frozen corpus")
    if any(prediction.get("status") == "ERROR" for prediction in predictions):
        raise RunStop("Clef request failed; refusing a partial accuracy result")
    if any(prediction.get("status") not in {"scored", "invalid"} for prediction in predictions):
        raise RunStop("Clef result has an unrecognized status")

    correct = sum(
        by_id[row["id"]].get("status") == "scored"
        and by_id[row["id"]].get("choice") == row["gold"]
        for row in rows
    )
    invalid = sum(by_id[row["id"]].get("status") == "invalid" for row in rows)
    invalid_rate = invalid / len(rows)
    majority_count = max(Counter(row["gold"] for row in rows).values())
    not_scored = invalid_rate > MAX_INVALID_RATE
    return {
        "outcome": "NOT_SCORED" if not_scored else "CLEF_ONLY_MEASURED",
        "n": len(rows),
        "labels": len({row["gold"] for row in rows}),
        "majority_count": majority_count,
        "majority_accuracy": majority_count / len(rows),
        "clef_correct": None if not_scored else correct,
        "clef_accuracy": None if not_scored else correct / len(rows),
        "invalid_answers": invalid,
        "invalid_rate": invalid_rate,
        "clef_requests": len(predictions),
        "concurrency": 1,
        "retries": 0,
        "cost_usd": 0.0,
        "jev_arm_status": "NOT_RUN",
        "jev_requests": 0,
    }


def write_receipt(
    status: str,
    reason: str,
    preflight: dict[str, Any] | None = None,
    metrics: dict[str, Any] | None = None,
) -> None:
    lines = [
        "# MASSIVE en-US local Clef-Flash intent measurement",
        "",
        f"Status: **{status}**",
        f"Reason: {reason}",
        "",
        f"Dataset: {DATASET_REVISION}; archive SHA-256 `{ARCHIVE_SHA256}`.",
        f"Clef model: `{CLEF_MODEL}` via `{CLEF_ENDPOINT_URL}`; localbench request-id guard required.",
        "Execution: concurrency 1, retries 0, no fallback; Jev arm NOT_RUN; experiment spend $0.00.",
        "",
    ]
    if preflight:
        lines.extend(
            [
                f"Frozen corpus SHA-256: `{preflight['corpus_sha256']}`",
                f"Frozen preregistration SHA-256: `{preflight['prereg_sha256']}`",
                f"Frozen spec SHA-256: `{preflight['spec_sha256']}`",
                f"Runner SHA-256: `{preflight['runner_sha256']}`",
                f"Keyless preflight: {preflight['rows']} rows / {preflight['labels']} labels; 0 prior-corpus overlaps; identity `{preflight['clef_identity']}`.",
                "",
            ]
        )
    if metrics:
        lines.extend(
            [
                f"Outcome: **{metrics['outcome']}**",
                f"Rows: {metrics['n']}; labels: {metrics['labels']}; majority baseline {metrics['majority_count']}/{metrics['n']} ({metrics['majority_accuracy']:.6f}).",
                f"Clef: correct={metrics['clef_correct']}; accuracy={metrics['clef_accuracy']!r}; invalid={metrics['invalid_answers']} ({metrics['invalid_rate']:.4%}).",
                f"Requests: Clef {metrics['clef_requests']}; Jev {metrics['jev_requests']}; retries {metrics['retries']}; concurrency {metrics['concurrency']}; experiment spend ${metrics['cost_usd']:.2f}.",
                "",
            ]
        )
    lines.extend(
        [
            "Per-row predictions, validated probability vectors, latency, and localbench request IDs are in `rows.jsonl`; utterance text remains only in the frozen public `corpus.jsonl`.",
            "This is a descriptive Clef-only measurement. Jev was NOT_RUN; no paired, comparative, superiority, or deployment claim is made.",
            "",
        ]
    )
    RECEIPT.write_text("\n".join(lines), encoding="utf-8")


def public_preflight(result: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in result.items() if not key.startswith("_")}


def selftest() -> dict[str, Any]:
    identity_calls: list[str] = []

    def fake_identity(url: str) -> dict[str, Any]:
        identity_calls.append(url)
        return {"models": [{"id": CLEF_MODEL}]}

    ready = check_frozen(identity_fn=fake_identity, results_path=None)
    if ready["status"] != "READY" or ready["jev_arm_status"] != "NOT_RUN":
        raise AssertionError("keyless positive preflight failed")

    def expect_refusal(check: Callable[[], Any]) -> None:
        try:
            check()
        except PreflightError:
            return
        raise AssertionError("planted preflight negative did not refuse")

    expect_refusal(
        lambda: check_frozen(
            expected_prereg_sha="0" * 64,
            identity_fn=fake_identity,
            results_path=None,
        )
    )
    expect_refusal(
        lambda: check_frozen(
            extra_overlap={normalize_text(load_jsonl(CORPUS)[0]["text"])},
            identity_fn=fake_identity,
            results_path=None,
        )
    )
    if len(identity_calls) != 1:
        raise AssertionError("a failed local gate reached the identity endpoint")

    def wrong_identity(url: str) -> dict[str, Any]:
        if url != CLEF_IDENTITY_URL:
            raise AssertionError("selftest identity URL changed")
        return {"models": [{"id": "wrong-model"}]}

    expect_refusal(lambda: check_frozen(identity_fn=wrong_identity, results_path=None))
    test_labels = sorted({row["gold"] for row in load_jsonl(CORPUS)})[:2]
    valid = {test_labels[0]: 0.8, test_labels[1]: 0.2}
    if validate_answer(test_labels[0], valid, test_labels) is not None:
        raise AssertionError("valid Choice response rejected")
    if validate_answer(test_labels[1], valid, test_labels) != "choice_not_probability_maximum":
        raise AssertionError("non-maximal selected label passed validation")
    return {
        "status": "PASS",
        "positive_rows": ready["rows"],
        "negative_cases": 3,
        "identity_gets": len(identity_calls) + 1,
        "inference_requests": 0,
        "jev_requests": 0,
        "spend_usd": 0.0,
    }


def spec_sha256() -> str:
    rows = load_jsonl(CORPUS)
    prior_hashes, _ = collect_prior_texts()
    return sha256_bytes(canonical_json(build_spec(rows, sha256_file(CORPUS), prior_hashes)))


def run_clef(preflight: dict[str, Any]) -> dict[str, Any]:
    if RESULTS.exists() and RESULTS.stat().st_size:
        raise RunStop("rows.jsonl is non-empty; refusing automatic retry or resume")
    rows = load_jsonl(CORPUS)
    predictions = run_predictions(
        rows,
        request_local,
        results_path=RESULTS,
    )
    metrics = score_completed(rows, predictions)
    status = "NOT_SCORED" if metrics["outcome"] == "NOT_SCORED" else "COMPLETE"
    write_receipt(status, "one guarded local Clef pass over all frozen rows", preflight, metrics)
    return metrics


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec-sha256", action="store_true", help="print the canonical frozen-spec hash")
    parser.add_argument("--preflight", action="store_true", help="verify pins, overlap, and local Clef identity without inference")
    parser.add_argument("--selftest", action="store_true", help="exercise frozen guards offline without inference")
    parser.add_argument("--run-clef", action="store_true", help="make one serial local Clef pass after all gates pass")
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    args = parser.parse_args()
    modes = (args.spec_sha256, args.preflight, args.selftest, args.run_clef)
    if sum(modes) != 1:
        parser.error("select exactly one operation")
    try:
        if args.spec_sha256:
            result: dict[str, Any] = {"spec_sha256": spec_sha256()}
        elif args.selftest:
            result = selftest()
        elif args.preflight:
            result = public_preflight(check_frozen())
        else:
            ready = check_frozen()
            result = run_clef(ready)
    except (PreflightError, RunStop, OSError, ValueError, TypeError, KeyError, TimeoutError, urllib.error.URLError) as error:
        if args.run_clef:
            recorded = load_jsonl(RESULTS) if RESULTS.is_file() else []
            terminal = "INCOMPLETE_NO_VERDICT" if recorded else "NOT_RUN"
            write_receipt(terminal, f"{error}; result rows recorded={len(recorded)}", locals().get("ready"))
        result = {"status": "REFUSED", "reason": str(error)}
        print(json.dumps(result, ensure_ascii=False, sort_keys=True) if args.json else result["reason"], file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True) if args.json else result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
