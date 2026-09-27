#!/usr/bin/env python3
"""Bounded Jev/free-comparator Score run for jev-dml3.

The outer command must be kit/experiment/run.py --detach --live, which verifies the
committed repo-relative preregistration, corpus hash, and REACHABLE mcnemar receipt
before this module opens either client.
"""

from __future__ import annotations

import asyncio
import hashlib
import importlib.util
import json
import math
import os
import random
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "work" / "score-amazon"
ROWS_PATH = Path(os.environ.get("SCORE_ROWS_PATH", HERE / "live-rows.jsonl"))
RECEIPT_PATH = Path(os.environ.get("SCORE_RECEIPT_PATH", HERE / "receipt.json"))
MODEL = "jev-1.13.0"
COMPARATOR = "dots-studio/dots-3-note-preview:free"
QNAME = "sentiment"
INSTRUCTIONS = "How positive is this movie review sentence?"
LEVELS = [
    "Very negative: strongly critical, scathing, or contemptuous",
    "Negative: somewhat critical or unfavorable",
    "Neutral: neither positive nor negative, or evenly mixed",
    "Positive: somewhat favorable or approving",
    "Very positive: strongly enthusiastic, glowing, or full of praise",
]
SEED = 20260927

sys.path.insert(0, str(ROOT / "upstream/typesafe-ai" / "typesafe-sdk-python" / "src"))
sys.path.insert(
    0, str(ROOT / "upstream/typesafe-ai" / "system-one-adapter-python" / "src")
)

from typesafe_sdk import AsyncTypeSafeClient, RetryPolicy, Score  # noqa: E402
from system_one_adapter import AsyncSystemOneAdapterClient  # noqa: E402
from kit.experiment.run import StopAfterRow, StopRun, run  # noqa: E402

_PROVIDER_SPEC = importlib.util.spec_from_file_location(
    "amazon_openrouter_provider", ROOT / "work" / "openrouter" / "provider.py"
)
if _PROVIDER_SPEC is None or _PROVIDER_SPEC.loader is None:
    raise RuntimeError("could not load the pinned OpenRouter provider")
_PROVIDER = importlib.util.module_from_spec(_PROVIDER_SPEC)
_PROVIDER_SPEC.loader.exec_module(_PROVIDER)


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def usage_snapshot() -> dict[str, object]:
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY is not set; no comparator call made")
    request = urllib.request.Request(
        "https://openrouter.ai/api/v1/key",
        headers={"Authorization": f"Bearer {key}", "User-Agent": "jev-dml3/1"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    data = payload.get("data", payload)
    return {
        "captured_at": now_utc(),
        "usage_daily": data.get("usage_daily"),
        "usage": data.get("usage"),
        "limit": data.get("limit"),
        "limit_remaining": data.get("limit_remaining"),
    }


def load_items() -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in (HERE / "corpus.jsonl").read_text().splitlines()
        if line
    ]


def score_answer(answer: object) -> dict[str, object]:
    score = float(answer.score)
    confidence = float(answer.confidence)
    probabilities = {str(int(k)): float(v) for k, v in answer.probabilities.items()}
    if not math.isfinite(score) or not 0 <= score <= 4:
        raise ValueError(f"score out of range: {score}")
    if not math.isfinite(confidence) or not 0 <= confidence <= 1:
        raise ValueError(f"confidence out of range: {confidence}")
    if set(probabilities) != {str(i) for i in range(5)}:
        raise ValueError("probability keys do not match five levels")
    if any(
        not math.isfinite(value) or value < 0 or value > 1
        for value in probabilities.values()
    ):
        raise ValueError("probability outside [0,1]")
    if abs(sum(probabilities.values()) - 1) >= 0.02:
        raise ValueError("probabilities do not sum to one")
    level = min(4, max(0, math.floor(score + 0.5)))
    return {
        "raw_score": score,
        "level": level,
        "confidence": confidence,
        "probabilities": probabilities,
    }


def usage_dict(usage: object, *, adapter: bool = False) -> dict[str, object]:
    if adapter:
        return {
            "input_tokens": int(usage.input_tokens_total),
            "output_tokens": int(usage.output_tokens_total),
        }
    return {
        "input_tokens": int(usage.input_tokens),
        "output_tokens": int(usage.output_tokens),
    }


def is_hard_stop(error: BaseException) -> bool:
    text = str(error).lower()
    return any(marker in text for marker in ("401", "402", "403"))


def paired_stats(rows: list[dict[str, object]]) -> dict[str, object]:
    paired = []
    invalid = {"jev": 0, "comparator": 0}
    for row in rows:
        label = int(row["label"])
        jev = row.get("jev")
        comparator = row.get("comparator")
        if not isinstance(jev, dict) or "level" not in jev:
            invalid["jev"] += 1
            continue
        if not isinstance(comparator, dict) or "level" not in comparator:
            invalid["comparator"] += 1
            continue
        paired.append((int(jev["level"]), int(comparator["level"]), label))
    if not paired:
        return {"paired_valid": 0, "invalid": invalid}
    differences = [abs(j - label) - abs(c - label) for j, c, label in paired]
    jev_mae = sum(abs(j - label) for j, _, label in paired) / len(paired)
    comparator_mae = sum(abs(c - label) for _, c, label in paired) / len(paired)
    jev_exact = sum(round(j) == label for j, _, label in paired) / len(paired)
    comparator_exact = sum(round(c) == label for _, c, label in paired) / len(paired)
    rng = random.Random(SEED)
    observed = sum(differences)
    extreme = 0
    iterations = 10_000
    for _ in range(iterations):
        signed = sum(value if rng.getrandbits(1) else -value for value in differences)
        if abs(signed) >= abs(observed):
            extreme += 1
    p_value = (extreme + 1) / (iterations + 1)
    return {
        "paired_valid": len(paired),
        "invalid": invalid,
        "jev_mae": jev_mae,
        "comparator_mae": comparator_mae,
        "mean_ae_difference_jev_minus_comparator": sum(differences) / len(differences),
        "jev_exact_accuracy": jev_exact,
        "comparator_exact_accuracy": comparator_exact,
        "permutation": {"seed": SEED, "flips": iterations, "p_value": p_value},
        "pass_bar": {
            "paired_valid_ge_278": len(paired) >= 278,
            "jev_mae_lt_comparator": jev_mae < comparator_mae,
            "p_lt_005": p_value < 0.05,
            "confirmation": len(paired) >= 278
            and jev_mae < comparator_mae
            and p_value < 0.05,
        },
    }


async def main() -> int:
    items = load_items()
    usage_before = usage_snapshot()
    question = {QNAME: Score(instructions=INSTRUCTIONS, criteria=LEVELS)}
    jev_client = AsyncTypeSafeClient(model=MODEL, retry=RetryPolicy())
    comparator_client = AsyncSystemOneAdapterClient(
        structured_outputs=True,
        llm_answer_mode="probabilities",
        normalize_probabilities=True,
        retry=RetryPolicy(http_statuses={408, *range(500, 600)}),
    )
    pacer = _PROVIDER.Pacer(15, len(items))
    provider = _PROVIDER.PacedProvider(
        _PROVIDER.openrouter_provider(COMPARATOR), pacer, 120.0
    )

    async def one(item: dict[str, object]) -> dict[str, object]:
        row: dict[str, object] = {
            "id": item["id"],
            "label": item["label"],
            "source_row": item["source_row"],
        }
        state = {"text": item["text"]}
        for arm in ("jev", "comparator"):
            started = time.perf_counter()
            try:
                if arm == "jev":
                    response = await asyncio.wait_for(
                        jev_client.system_one(state, question), timeout=120
                    )
                    row[arm] = {
                        **score_answer(response.scores[QNAME]),
                        "model": response.model,
                        "usage": usage_dict(response.usage),
                    }
                else:
                    response = await asyncio.wait_for(
                        comparator_client.system_one(state, question, model=provider),
                        timeout=420,
                    )
                    row[arm] = {
                        **score_answer(response.answers[QNAME]),
                        "model": COMPARATOR,
                        "usage": usage_dict(response.usage, adapter=True),
                    }
                row[f"{arm}_latency_ms"] = int((time.perf_counter() - started) * 1000)
            except (
                Exception
            ) as error:  # recorded as invalid; hard stops stop before the next row
                row[f"{arm}_error"] = f"{type(error).__name__}: {str(error)[:300]}"
                row[f"{arm}_latency_ms"] = int((time.perf_counter() - started) * 1000)
                if is_hard_stop(error):
                    raise StopAfterRow(row, f"{arm} hard stop: {type(error).__name__}")
        return row

    stop_reason = None
    try:
        async with jev_client, comparator_client:
            stop_reason = await run(
                items,
                one,
                ROWS_PATH,
                id_key="id",
                live=True,
                reach=HERE / "reach-receipt.json",
                items_path=HERE / "corpus.jsonl",
                prereg_path=HERE / "PREREG.md",
            )
    finally:
        await provider.aclose()
    usage_after = usage_snapshot()
    rows = [json.loads(line) for line in ROWS_PATH.read_text().splitlines() if line]
    receipt = {
        "status": "LIVE_COMPLETE",
        "created_at": now_utc(),
        "model": MODEL,
        "comparator": COMPARATOR,
        "corpus_sha256": hashlib.sha256(
            (HERE / "corpus.jsonl").read_bytes()
        ).hexdigest(),
        "prereg_sha256": hashlib.sha256((HERE / "PREREG.md").read_bytes()).hexdigest(),
        "rows": len(rows),
        "stop_reason": stop_reason,
        "usage_before": usage_before,
        "usage_after": usage_after,
        "stats": paired_stats(rows),
    }
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
