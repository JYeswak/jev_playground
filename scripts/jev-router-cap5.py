#!/usr/bin/env python3
"""Run the preregistered Jev router versus one fixed OpenRouter :free model."""
# pyright: reportMissingImports=false

from __future__ import annotations

import asyncio
import hashlib
import importlib.util
import json
import os
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any

import httpx

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from kit.experiment.run import StopAfterRow, StopRun, run as checkpoint_run

ROUTER_MODEL = "typesafe/jev-router"
FIXED_MODEL = "dots-studio/dots-3-note-preview:free"
MODEL = "jev-1.13.0"
CAP_USD = 5.0
STOP_MARGIN_USD = 4.95
MAX_TOKENS = 256
DATASET = ROOT / "work/choice-banking77/subset.jsonl"
RECEIPT = ROOT / "work/jev-38qj/receipt.json"
ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"


def load_runner():
    path = ROOT / "work/choice-banking77/run.py"
    spec = importlib.util.spec_from_file_location("choice_banking77_runner", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rows = [
        json.loads(line) for line in DATASET.read_text().splitlines() if line.strip()
    ]
    label_map = module.labels(rows)
    return rows, module.state, label_map


def usage_snapshot() -> dict:
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY is not set; no benchmark call made")
    request = urllib.request.Request(
        "https://openrouter.ai/api/v1/key",
        headers={"Authorization": f"Bearer {key}"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.load(response)["data"]
    return {
        key: value
        for key, value in data.items()
        if key not in {"key", "label", "name", "hash"} and not isinstance(value, str)
    }


def usage_amount(snapshot: dict) -> float:
    value = snapshot.get("usage")
    return float(value) if isinstance(value, (int, float)) else 0.0


def extract_json_object(content: Any) -> dict[str, Any] | None:
    if isinstance(content, dict):
        return content
    if not isinstance(content, str):
        return None
    try:
        parsed = json.loads(content)
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        decoder = json.JSONDecoder()
        for index, character in enumerate(content):
            if character != "{":
                continue
            try:
                parsed, _ = decoder.raw_decode(content[index:])
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, dict):
                return parsed
    return None


def parse_answer(
    data: dict[str, Any], labels: dict[str, str], row: dict[str, Any]
) -> dict[str, Any]:
    choices_raw: Any = data.get("choices")
    first: dict[str, Any] = (
        choices_raw[0]
        if isinstance(choices_raw, list)
        and choices_raw
        and isinstance(choices_raw[0], dict)
        else {}
    )
    message_raw: Any = first.get("message")
    message = message_raw if isinstance(message_raw, dict) else {}
    parsed = extract_json_object(message.get("content", ""))
    choice = parsed.get("intent") if isinstance(parsed, dict) else None
    choice = labels.get(choice, choice) if isinstance(choice, str) else None
    usage_raw: Any = data.get("usage")
    usage = usage_raw if isinstance(usage_raw, dict) else {}
    answer = {
        "choice": choice,
        "correct": choice == row["intent"],
        "usage": {
            "input_tokens": usage.get("prompt_tokens", usage.get("input_tokens", 0)),
            "output_tokens": usage.get(
                "completion_tokens", usage.get("output_tokens", 0)
            ),
            "cost": usage.get("cost"),
        },
        "metadata": {"model": data.get("model"), "provider": data.get("provider")},
    }
    if choice is None:
        answer["error_code"] = "MISSING_CHOICE"
    return answer


def summarize_arm(rows: list[dict[str, Any]], arm: str) -> dict[str, Any]:
    arm_rows = [row[arm] for row in rows if arm in row]
    errors = sum(
        bool(
            answer.get("error")
            or answer.get("error_code")
            or answer.get("choice") is None
        )
        for answer in arm_rows
    )
    calls = len(arm_rows)
    return {
        "correct": sum(bool(answer.get("correct")) for answer in arm_rows),
        "calls": calls,
        "answered": calls - errors,
        "errors": errors,
        "error_rate": errors / calls if calls else 1.0,
        "verdict_eligible": calls > 0 and errors / calls <= 0.05,
        "input_tokens": sum(
            answer.get("usage", {}).get("input_tokens", 0)
            for answer in arm_rows
            if isinstance(answer.get("usage"), dict)
        ),
    }


async def call(
    client: httpx.AsyncClient,
    key: str,
    model: str,
    state: dict[str, Any],
    labels: dict[str, str],
    row: dict[str, Any],
) -> dict[str, Any]:
    system = "Return only one JSON object with exactly one key intent. Its value must be one of the labels listed in the user message."
    user = json.dumps(
        {"labels": sorted(labels), "customer_message": state["customer_message"]},
        ensure_ascii=False,
    )
    started = time.perf_counter()
    try:
        response = await client.post(
            ENDPOINT,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "max_tokens": MAX_TOKENS,
            },
        )
        response.raise_for_status()
        answer = parse_answer(response.json(), labels, row)
        answer["latency_ms"] = int((time.perf_counter() - started) * 1000)
        return answer
    except Exception as error:
        status = getattr(getattr(error, "response", None), "status_code", None)
        return {
            "correct": False,
            "latency_ms": int((time.perf_counter() - started) * 1000),
            "error_code": f"HTTP_{status}" if status else type(error).__name__,
            "error": f"{type(error).__name__}: {str(error)[:500]}",
        }


async def main() -> int:
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise SystemExit("OPENROUTER_API_KEY is not set; no benchmark call made")
    rows, state_fn, labels = load_runner()
    before = usage_snapshot()
    before_amount = usage_amount(before)
    started = time.time()
    checkpoint = ROOT / "work/jev-38qj/rows.jsonl"
    async with httpx.AsyncClient(timeout=90) as client:

        async def process(row: dict[str, Any]) -> dict[str, Any]:
            if usage_amount(usage_snapshot()) - before_amount >= STOP_MARGIN_USD:
                raise StopRun("hard-stop-before-router")
            item = {"i": row["i"], "intent": row["intent"]}
            state = state_fn(row)
            item["router"] = await call(client, key, ROUTER_MODEL, state, labels, row)
            if item["router"].get("error_code") == "HTTP_402":
                raise StopAfterRow(item, "router-402-payment-required")
            after_router = usage_snapshot()
            item["router_usage_after"] = {
                "usage": usage_amount(after_router),
                "daily": after_router.get("usage_daily"),
            }
            if usage_amount(after_router) - before_amount >= CAP_USD:
                raise StopAfterRow(item, "hard-stop-after-router")
            item["fixed"] = await call(client, key, FIXED_MODEL, state, labels, row)
            return item

        stopped = await checkpoint_run(
            rows,
            process,
            checkpoint,
            id_key="i",
            live=True,
            reach=ROOT / "work/jev-38qj/reach-receipt.json",
            items_path=DATASET,
        )
    results = (
        [
            json.loads(line)
            for line in checkpoint.read_text().splitlines()
            if line.strip()
        ]
        if checkpoint.exists()
        else []
    )
    after = usage_snapshot()
    router_summary = summarize_arm(results, "router")
    fixed_summary = summarize_arm(results, "fixed")
    error_refusal_arms = [
        arm
        for arm, summary in (("router", router_summary), ("fixed", fixed_summary))
        if not summary["verdict_eligible"]
    ]
    receipt = {
        "status": "QUALITY_REFUSED_ERROR_RATE" if error_refusal_arms else "COMPLETE",
        "quality_verdict_refused": bool(error_refusal_arms),
        "error_rate_bar": 0.05,
        "error_refusal_arms": error_refusal_arms,
        "model": MODEL,
        "router_model": ROUTER_MODEL,
        "fixed_model": FIXED_MODEL,
        "max_tokens": MAX_TOKENS,
        "dataset": str(DATASET.relative_to(ROOT)),
        "dataset_sha256": hashlib.sha256(DATASET.read_bytes()).hexdigest(),
        "n_rows": len(rows),
        "rows_run": len(results),
        "stopped": stopped,
        "before_usage": before,
        "after_usage": after,
        "incremental_openrouter_usage_usd": usage_amount(after) - before_amount,
        "wall_seconds": time.time() - started,
        "router": router_summary,
        "fixed": fixed_summary,
        "quality": None,
        "rows": results,
        "boundary": "No quality or router-vs-fixed verdict is valid when either arm exceeds the 5% error bar; HTTP 402 is classified before further router calls. Direct OpenRouter chat calls use the public Banking77 state; keys and raw benchmark text are not emitted outside requests.",
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(
        json.dumps(
            {
                k: receipt[k]
                for k in (
                    "rows_run",
                    "stopped",
                    "incremental_openrouter_usage_usd",
                    "router",
                    "fixed",
                    "wall_seconds",
                )
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
