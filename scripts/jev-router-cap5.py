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

ROOT = Path(__file__).resolve().parents[1]
ROUTER_MODEL = "typesafe/jev-router"
FIXED_MODEL = "dots-studio/dots-3-note-preview:free"
MODEL = "jev-1.13.0"
CAP_USD = 5.0
STOP_MARGIN_USD = 4.95
DATASET = ROOT / "work/choice-banking77/subset.jsonl"
RECEIPT = ROOT / "work/jev-38qj/receipt.json"

import sys

sys.path.insert(0, str(ROOT / "upstream/typesafe-ai/system-one-adapter-python/src"))
from system_one_adapter import AsyncSystemOneAdapterClient  # noqa: E402
from system_one_adapter.providers.openai import AsyncOpenAIProvider  # noqa: E402
from typesafe_sdk import RetryPolicy  # noqa: E402


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
    return rows, module.question(label_map), module.state, label_map


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
    usage = {
        key: value
        for key, value in data.items()
        if key not in {"key", "label", "name", "hash"} and not isinstance(value, str)
    }
    return usage


def usage_amount(snapshot: dict) -> float:
    value = snapshot.get("usage")
    return float(value) if isinstance(value, (int, float)) else 0.0


def attempt_metadata(response) -> dict:
    debug = response.debug or {}
    attempts = debug.get("llm_attempts") or []
    last = attempts[-1] if attempts else {}
    raw = last.get("llm_response") or {}
    info = last.get("debug_info") or {}
    return {
        "provider": raw.get("provider") or info.get("provider"),
        "model": raw.get("model"),
        "finish_reason": info.get("finish_reason"),
        "attempts": len(attempts),
    }


def usage_metadata(response) -> dict:
    usage = getattr(response, "usage", None)
    return {
        "input_tokens": int(getattr(usage, "input_tokens_total", 0) or 0),
        "output_tokens": int(getattr(usage, "output_tokens_total", 0) or 0),
    }


async def main() -> int:
    rows, question, state, label_map = load_runner()
    before = usage_snapshot()
    before_amount = usage_amount(before)
    router = AsyncOpenAIProvider(
        ROUTER_MODEL,
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ["OPENROUTER_API_KEY"],
        api="chat_completions",
    )
    fixed = AsyncOpenAIProvider(
        FIXED_MODEL,
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ["OPENROUTER_API_KEY"],
        api="chat_completions",
    )
    results = []
    stopped = None
    started = time.time()
    async with AsyncSystemOneAdapterClient(
        structured_outputs=True,
        llm_answer_mode="probabilities",
        normalize_probabilities=True,
        retry=RetryPolicy(),
    ) as client:
        for item in rows:
            current = usage_snapshot()
            if usage_amount(current) - before_amount >= STOP_MARGIN_USD:
                stopped = "hard-stop-before-router"
                break
            row = {"i": item["i"], "intent": item["intent"]}
            for arm, provider in (("router", router), ("fixed", fixed)):
                call_started = time.perf_counter()
                try:
                    response = await client.system_one(
                        state(item), question, model=provider
                    )
                    answer = response.answers["intent"]
                    choice = label_map.get(answer.choice, answer.choice)
                    row[arm] = {
                        "choice": choice,
                        "correct": choice == item["intent"],
                        "latency_ms": int((time.perf_counter() - call_started) * 1000),
                        "usage": usage_metadata(response),
                        "metadata": attempt_metadata(response),
                    }
                except Exception as error:  # record, do not hide a row failure
                    row[arm] = {
                        "correct": False,
                        "latency_ms": int((time.perf_counter() - call_started) * 1000),
                        "error": f"{type(error).__name__}: {str(error)[:500]}",
                    }
                if arm == "router":
                    after_router = usage_snapshot()
                    row["router_usage_after"] = {
                        "usage": usage_amount(after_router),
                        "daily": after_router.get("usage_daily"),
                    }
                    if usage_amount(after_router) - before_amount >= CAP_USD:
                        stopped = "hard-stop-after-router"
                        break
            results.append(row)
            if stopped:
                break
    await router.aclose()
    await fixed.aclose()
    after = usage_snapshot()
    router_rows = [row["router"] for row in results if "router" in row]
    fixed_rows = [row["fixed"] for row in results if "fixed" in row]
    receipt = {
        "model": MODEL,
        "router_model": ROUTER_MODEL,
        "fixed_model": FIXED_MODEL,
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
                row.get("usage", {}).get("input_tokens", 0) for row in router_rows
            ),
        },
        "fixed": {
            "correct": sum(row.get("correct", False) for row in fixed_rows),
            "calls": len(fixed_rows),
            "input_tokens": sum(
                row.get("usage", {}).get("input_tokens", 0) for row in fixed_rows
            ),
        },
        "rows": results,
        "boundary": "Raw benchmark text and API keys are not emitted outside the request; score with the public Banking77 intent labels and the preregistered bar.",
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
