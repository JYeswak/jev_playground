#!/usr/bin/env python3
"""Bounded exact-state Jev rescore for PGTU stale answer hashes."""

from __future__ import annotations

import argparse
import asyncio
import json
import math
import os
import sys
import time
from datetime import datetime, timezone
from typing import Any, TextIO

from adapter_runner import (
    CUT,
    JEV_MODEL,
    PREREG_PATH,
    QUESTION_ID,
    REACH_PATH,
    RESCORE_OUTPUT_PATH,
    ROOT,
    approved_commit,
    load_preflight,
    read_json,
    run_rows,
)
from typesafe_sdk import (  # type: ignore[import-not-found]
    AsyncTypeSafeClient,
    Noul,
    RetryPolicy,
    SystemOneResponse,
    TypeSafeAPIError,
    TypeSafeError,
)

EXPECTED_STALE_ROWS = 491
MAX_REQUESTS = EXPECTED_STALE_ROWS
INPUT_PRICE_USD_PER_MILLION = 0.042
CHECKPOINT_PATH = ROOT / "var/agent-tmp/jev-pgtu/jev-rescore-checkpoint.jsonl"


def extract_answer(
    response: SystemOneResponse, *, question_id: str
) -> tuple[float, int, int | None]:
    """Refuse model drift, non-Noul answers, invalid probabilities, or unbillable usage."""
    if response.model != JEV_MODEL:
        raise ValueError("response model differs from the pinned model")
    answer = response.nouls.get(question_id)
    if answer is None:
        raise ValueError("response omitted the requested Noul answer")
    probability = answer.noul
    if (
        isinstance(probability, bool)
        or not isinstance(probability, (int, float))
        or not math.isfinite(float(probability))
        or not 0.0 <= float(probability) <= 1.0
    ):
        raise ValueError("response probability is outside [0, 1]")
    input_tokens = response.usage.input_tokens
    if (
        isinstance(input_tokens, bool)
        or not isinstance(input_tokens, int)
        or input_tokens < 0
    ):
        raise ValueError("input-token usage is missing or invalid")
    output_tokens = response.usage.output_tokens
    if output_tokens is not None and (
        isinstance(output_tokens, bool)
        or not isinstance(output_tokens, int)
        or output_tokens < 0
    ):
        raise ValueError("output-token usage is invalid")
    return float(probability), input_tokens, output_tokens


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_api_key(stream: TextIO) -> str | None:
    key = stream.readline().rstrip("\r\n")
    if not key or any(character.isspace() for character in key):
        return None
    return key


def checkpoint(record: dict[str, Any]) -> None:
    with CHECKPOINT_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def validate_plan(
    assistant: str, question: str
) -> tuple[dict[str, Any], list[dict[str, Any]], str | None]:
    try:
        counts, pairs = load_preflight(assistant, question, include_unmatched=True)
        reach = read_json(REACH_PATH)
    except (OSError, ValueError, TypeError):
        return {}, [], "prepared-artifact-read-failed"

    plan = reach.get("same_state_jev_rescore")
    expected_plan = {
        "status": "PREREGISTERED_NOT_RUN",
        "mismatched_rows": EXPECTED_STALE_ROWS,
        "max_requests": MAX_REQUESTS,
        "attempts_per_row": 1,
        "max_retries": 0,
        "model": JEV_MODEL,
        "question_id": QUESTION_ID,
        "output_path": RESCORE_OUTPUT_PATH.relative_to(ROOT).as_posix(),
        "input_price_usd_per_million": INPUT_PRICE_USD_PER_MILLION,
        "output_price_usd": 0,
        "items_sha256": counts.get("items_sha256"),
        "states_sha256": counts.get("states_sha256"),
        "question_sha256": counts.get("question_sha256"),
        "assistant_sha256": counts.get("assistant_sha256"),
        "seat_source_sha256": counts.get("seat_source_sha256"),
        "cut": CUT,
    }
    if not isinstance(plan, dict) or any(
        plan.get(key) != value for key, value in expected_plan.items()
    ):
        return counts, pairs, "rescore-preregistration-mismatch"
    if not approved_commit(
        PREREG_PATH.relative_to(ROOT).as_posix()
    ) or not approved_commit(REACH_PATH.relative_to(ROOT).as_posix()):
        return counts, pairs, "preregistration-or-reachability-not-committed"
    if counts.get("reason") != "same-state-pair-infeasible":
        return counts, pairs, str(counts.get("reason", "unexpected-preflight-state"))
    required_counts = {
        "clean_matched": 95,
        "planted_matched": 14,
        "missing_jev_rows": 0,
        "input_hash_mismatches": EXPECTED_STALE_ROWS,
        "invalid_jev_rows": 0,
        "state_manifest_mismatches": 0,
        "duplicate_join_keys": 0,
        "duplicate_rescore_keys": 0,
        "redactor_recheck_matches": 600,
        "redactor_recheck_hash_matches": True,
        "redactor_recheck_state_hash_matches": True,
        "state_size_status": "FITS",
        "seat_source_hash_matches_reachability": True,
        "assistant_hash_matches_reachability": True,
        "seat_cut_matches": True,
        "seat_model_matches": True,
    }
    if any(counts.get(key) != value for key, value in required_counts.items()):
        return counts, pairs, "exact-rescore-feasibility-changed"
    candidates = [pair for pair in pairs if pair.get("jev") is None]
    if len(pairs) != 600 or len(candidates) != MAX_REQUESTS:
        return counts, pairs, "exact-rescore-candidate-count-mismatch"
    return counts, candidates, None


def write_final_rows(rows: list[dict[str, Any]]) -> None:
    with RESCORE_OUTPUT_PATH.open("x", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def emit(record: dict[str, Any], exit_code: int) -> int:
    print(json.dumps(record, sort_keys=True, separators=(",", ":")))
    return exit_code


def run_live(
    candidates: list[dict[str, Any]],
    question: str,
    api_key: str,
    preflight: dict[str, Any],
) -> int:
    item_by_id = {pair["item"]["id"]: pair["item"] for pair in candidates}
    started_all = time.perf_counter()

    def persist_checkpoint(record: dict[str, Any]) -> None:
        entry: dict[str, Any] = {
            "schema_version": "jev-pgtu-rescore-checkpoint.v1",
            **record,
        }
        if record.get("event") == "request_started":
            item = item_by_id.get(record.get("id"))
            if isinstance(item, dict):
                for key in ("set", "baseIndex", "position", "inputSha256"):
                    if key in item:
                        entry[key] = item[key]
                entry["model"] = JEV_MODEL
                entry["started_utc"] = utc_now()
        else:
            entry["finished_utc"] = utc_now()
        checkpoint(entry)

    async def execute() -> dict[str, Any]:
        async with AsyncTypeSafeClient(
            api_key=api_key,
            model=JEV_MODEL,
            retry=RetryPolicy(max_retries=0),
            timeout=30.0,
        ) as client:
            with CHECKPOINT_PATH.open("x", encoding="utf-8") as handle:
                handle.flush()
                os.fsync(handle.fileno())

            async def ask(pair: dict[str, Any]) -> dict[str, Any]:
                started = time.perf_counter()
                try:
                    response = await client.system_one(
                        state=pair["state"],
                        questions={QUESTION_ID: Noul(instructions=question)},
                        model=JEV_MODEL,
                        retry=RetryPolicy(max_retries=0),
                        timeout=30.0,
                    )
                    probability, input_tokens, output_tokens = extract_answer(
                        response, question_id=QUESTION_ID
                    )
                except TypeSafeAPIError as error:
                    status = error.status
                    reason = (
                        f"http_{status}"
                        if status in {401, 402, 403, 429}
                        else "typesafe_api_error"
                    )
                    return {
                        "status": "not_run",
                        "reason": reason,
                        "http_status": status,
                    }
                except TypeSafeError as error:
                    return {
                        "status": "not_run",
                        "reason": "typesafe_request_failed",
                        "error_type": type(error).__name__,
                    }
                except ValueError:
                    return {"status": "not_run", "reason": "response_contract_rejected"}
                return {
                    "status": "answered",
                    "model": response.model,
                    "p": probability,
                    "flag": probability >= CUT,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "latency_ms": round((time.perf_counter() - started) * 1000, 3),
                }

            return await run_rows(candidates, ask, persist_checkpoint)

    try:
        result = asyncio.run(execute())
    except (OSError, ValueError, TypeSafeError) as error:
        return emit(
            {
                "status": "NOT_RUN",
                "reason": "runner_failed",
                "error_type": type(error).__name__,
                "provider_requests": 0,
                "preflight": preflight,
            },
            2,
        )

    attempts = result.get("request_attempts", 0)
    answer_rows = [
        row for row in result.get("rows", []) if row.get("status") == "answered"
    ]
    if (
        result.get("status") != "COMPLETE"
        or attempts != MAX_REQUESTS
        or len(answer_rows) != MAX_REQUESTS
    ):
        return emit(
            {
                "status": "NOT_RUN",
                "reason": result.get("stop_reason") or "request_count_mismatch",
                "provider_requests": attempts,
                "answered_rows": len(answer_rows),
                "preflight": preflight,
            },
            2,
        )
    rows = [
        {
            "schema_version": "jev-pgtu-row.v1",
            **{key: value for key, value in row.items() if key != "event"},
        }
        for row in answer_rows
    ]
    write_final_rows(rows)
    input_tokens = sum(row["input_tokens"] for row in rows)
    output_values = [row.get("output_tokens") for row in rows]
    output_complete = all(value is not None for value in output_values)
    output_tokens = sum(value for value in output_values if value is not None)
    spend = input_tokens * INPUT_PRICE_USD_PER_MILLION / 1_000_000
    return emit(
        {
            "status": "COMPLETE",
            "provider_requests": attempts,
            "answered_rows": len(rows),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens if output_complete else None,
            "input_token_usage_complete": True,
            "output_token_usage_complete": output_complete,
            "spend_usd": round(spend, 10),
            "latency_total_ms": round((time.perf_counter() - started_all) * 1000, 3),
            "preflight": preflight,
            "output_path": RESCORE_OUTPUT_PATH.relative_to(ROOT).as_posix(),
        },
        0,
    )


def run(
    assistant: str, question: str, *, live: bool, api_key: str | None = None
) -> int:
    counts, candidates, reason = validate_plan(assistant, question)
    if reason is not None:
        return emit({"status": "NOT_RUN", "reason": reason, "preflight": counts}, 2)
    if RESCORE_OUTPUT_PATH.exists() or CHECKPOINT_PATH.exists():
        return emit(
            {
                "status": "NOT_RUN",
                "reason": "existing-rescore-artifact-refuse-overwrite",
            },
            2,
        )
    if not live:
        return emit(
            {
                "status": "READY_TO_RESCORE",
                "candidate_rows": len(candidates),
                "max_requests": MAX_REQUESTS,
                "model": JEV_MODEL,
                "retry_max_retries": 0,
                "preflight": counts,
            },
            0,
        )
    if not api_key:
        return emit(
            {
                "status": "NOT_RUN",
                "reason": "typesafe-key-missing",
                "preflight": counts,
            },
            2,
        )
    return run_live(candidates, question, api_key, counts)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--preflight-only", action="store_true")
    group.add_argument("--live", action="store_true")
    parser.add_argument("--key-stdin", action="store_true")
    args = parser.parse_args(argv)
    assistant = os.environ.get("JEV_PGTU_ASSISTANT", "")
    question = os.environ.get("JEV_PGTU_QUESTION", "")
    if (
        not assistant
        or not question
        or os.environ.get("JEV_PGTU_JEV_MODEL") != JEV_MODEL
        or os.environ.get("JEV_PGTU_CUT") != str(CUT)
    ):
        return emit({"status": "NOT_RUN", "reason": "seat-contract-not-loaded"}, 2)
    if args.key_stdin != args.live:
        return emit({"status": "NOT_RUN", "reason": "key-stdin-mode-mismatch"}, 2)
    api_key = read_api_key(sys.stdin) if args.key_stdin else None
    return run(assistant, question, live=args.live, api_key=api_key)


if __name__ == "__main__":
    raise SystemExit(main())
