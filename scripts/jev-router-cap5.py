#!/usr/bin/env python3
"""Run the preregistered Jev router versus one fixed OpenRouter :free model."""
# pyright: reportMissingImports=false

from __future__ import annotations

import asyncio
import hashlib
import importlib.util
import json
import os
import time
import urllib.request
from pathlib import Path
from typing import Any

import httpx

ROOT = Path(__file__).resolve().parents[1]
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
    content = message.get("content", "")
    parsed = json.loads(content) if isinstance(content, str) else content
    choice = parsed.get("intent") if isinstance(parsed, dict) else None
    choice = labels.get(choice, choice) if isinstance(choice, str) else None
    usage_raw: Any = data.get("usage")
    usage = usage_raw if isinstance(usage_raw, dict) else {}
    return {
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
        return {
            "correct": False,
            "latency_ms": int((time.perf_counter() - started) * 1000),
            "error": f"{type(error).__name__}: {str(error)[:500]}",
        }


async def main() -> int:
    rows, state_fn, labels = load_runner()
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise SystemExit("OPENROUTER_API_KEY is not set; no benchmark call made")
    before = usage_snapshot()
    before_amount = usage_amount(before)
    results = []
    stopped = None
    started = time.time()
    async with httpx.AsyncClient(timeout=90) as client:
        for row in rows:
            if usage_amount(usage_snapshot()) - before_amount >= STOP_MARGIN_USD:
                stopped = "hard-stop-before-router"
                break
            item = {"i": row["i"], "intent": row["intent"]}
            state = state_fn(row)
            item["router"] = await call(client, key, ROUTER_MODEL, state, labels, row)
            after_router = usage_snapshot()
            item["router_usage_after"] = {
                "usage": usage_amount(after_router),
                "daily": after_router.get("usage_daily"),
            }
            if usage_amount(after_router) - before_amount >= CAP_USD:
                stopped = "hard-stop-after-router"
                results.append(item)
                break
            item["fixed"] = await call(client, key, FIXED_MODEL, state, labels, row)
            results.append(item)
    after = usage_snapshot()
    router_rows = [row["router"] for row in results if "router" in row]
    fixed_rows = [row["fixed"] for row in results if "fixed" in row]
    receipt = {
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
        "router": {
            "correct": sum(row.get("correct", False) for row in router_rows),
            "calls": len(router_rows),
            "input_tokens": sum(
                row.get("usage", {}).get("input_tokens", 0)
                for row in router_rows
                if isinstance(row.get("usage"), dict)
            ),
        },
        "fixed": {
            "correct": sum(row.get("correct", False) for row in fixed_rows),
            "calls": len(fixed_rows),
            "input_tokens": sum(
                row.get("usage", {}).get("input_tokens", 0)
                for row in fixed_rows
                if isinstance(row.get("usage"), dict)
            ),
        },
        "rows": results,
        "boundary": "Direct OpenRouter chat calls use the public Banking77 state; keys and raw benchmark text are not emitted outside requests.",
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
