#!/usr/bin/env python3
"""Bounded Jev/free-comparator runner for jev-vg4s; refuses before the booked-date gate."""

from __future__ import annotations

import asyncio
import hashlib
import importlib.util
import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "work" / "jev-vg4s"
MODEL = "jev-1.13.0"
COMPARATOR = "dots-studio/dots-3-note-preview:free"
LAUNCH_AFTER = datetime(2026, 9, 30, tzinfo=timezone.utc)
QNAME = "supports"
QUESTION = {
    "type": "noul",
    "instructions": "Does the evidence support the claim?",
    "criteria": {
        "true": "The evidence states the claim or directly implies that it is true",
        "false": "The evidence contradicts the claim, or does not address what the claim asserts",
    },
}

sys.path.insert(0, str(ROOT / "upstream/typesafe-ai" / "typesafe-sdk-python" / "src"))
sys.path.insert(
    0, str(ROOT / "upstream/typesafe-ai" / "system-one-adapter-python" / "src")
)
from system_one_adapter import AsyncSystemOneAdapterClient  # noqa: E402
from typesafe_sdk import AsyncTypeSafeClient, Noul, RetryPolicy  # noqa: E402

_PROVIDER_SPEC = importlib.util.spec_from_file_location(
    "vg4s_openrouter_provider", ROOT / "work" / "openrouter" / "provider.py"
)
if _PROVIDER_SPEC is None or _PROVIDER_SPEC.loader is None:
    raise RuntimeError("could not load pinned OpenRouter provider")
_PROVIDER = importlib.util.module_from_spec(_PROVIDER_SPEC)
_PROVIDER_SPEC.loader.exec_module(_PROVIDER)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def usage_snapshot() -> dict[str, object]:
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY is not set")
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/key",
        headers={"Authorization": f"Bearer {key}", "User-Agent": "jev-vg4s/1"},
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        data = json.load(response).get("data", {})
    return {
        "captured_at": now(),
        **{key: data.get(key) for key in ("usage", "usage_daily", "limit_remaining")},
    }


def main() -> int:
    if datetime.now(timezone.utc) < LAUNCH_AFTER:
        print(f"NOT_RUN launch gate closed until {LAUNCH_AFTER.isoformat()}")
        return 2
    prereg = HERE / "PREREG.md"
    corpus = HERE / "corpus.jsonl"
    states = HERE / "states.jsonl"
    receipt_path = HERE / "reachability.json"
    receipt = json.loads(receipt_path.read_text())
    if receipt.get("prereg_sha256") != sha(prereg) or receipt.get(
        "items_sha256"
    ) != sha(corpus):
        raise RuntimeError("reach receipt does not bind prereg/corpus")
    if receipt.get("states_sha256") != sha(states):
        raise RuntimeError("reach receipt does not bind states")
    rows = [json.loads(line) for line in corpus.read_text().splitlines() if line]
    state_rows = {
        json.loads(line)["id"]: json.loads(line)["state"]
        for line in states.read_text().splitlines()
        if line
    }
    usage_before = usage_snapshot()
    jev = AsyncTypeSafeClient(model=MODEL, retry=RetryPolicy())
    comparator = AsyncSystemOneAdapterClient(
        structured_outputs=True,
        llm_answer_mode="probabilities",
        normalize_probabilities=True,
        retry=RetryPolicy(http_statuses={408, *range(500, 600)}),
    )
    provider = _PROVIDER.PacedProvider(
        _PROVIDER.openrouter_provider(COMPARATOR), _PROVIDER.Pacer(15, len(rows)), 120.0
    )
    out = HERE / "live-rows.jsonl"
    completed: list[dict[str, object]] = []
    stop_reason = None

    async def run_one(row: dict[str, object]) -> dict[str, object]:
        state = state_rows[row["id"]]
        result: dict[str, object] = {
            "id": row["id"],
            "source_row": row["source_row"],
            "label": row["label"],
        }
        for arm in ("jev", "comparator"):
            started = time.perf_counter()
            try:
                if arm == "jev":
                    answer = await asyncio.wait_for(
                        jev.system_one(
                            state,
                            {
                                QNAME: Noul(
                                    instructions=QUESTION["instructions"],
                                    criteria=QUESTION["criteria"],
                                )
                            },
                        ),
                        120,
                    )
                    result[arm] = {
                        "noul": float(answer.nouls[QNAME].noul),
                        "model": answer.model,
                        "usage": {
                            "input_tokens": answer.usage.input_tokens,
                            "output_tokens": answer.usage.output_tokens,
                        },
                    }
                else:
                    answer = await asyncio.wait_for(
                        comparator.system_one(
                            state,
                            {
                                QNAME: Noul(
                                    instructions=QUESTION["instructions"],
                                    criteria=QUESTION["criteria"],
                                )
                            },
                            model=provider,
                        ),
                        420,
                    )
                    result[arm] = {
                        "noul": float(answer.answers[QNAME].noul),
                        "model": COMPARATOR,
                        "usage": {
                            "input_tokens": int(answer.usage.input_tokens_total),
                            "output_tokens": int(answer.usage.output_tokens_total),
                        },
                    }
                result[f"{arm}_latency_ms"] = int(
                    (time.perf_counter() - started) * 1000
                )
            except Exception as error:  # noqa: BLE001
                result[f"{arm}_error"] = f"{type(error).__name__}: {str(error)[:300]}"
                result[f"{arm}_latency_ms"] = int(
                    (time.perf_counter() - started) * 1000
                )
                if (
                    "429" in str(error)
                    or "401" in str(error)
                    or "402" in str(error)
                    or "403" in str(error)
                ):
                    raise RuntimeError(f"{arm} hard stop: {error}") from error
        return result

    async def run_all() -> None:
        nonlocal stop_reason
        try:
            async with jev, comparator:
                for row in rows:
                    try:
                        result = await run_one(row)
                    except RuntimeError as error:
                        stop_reason = str(error)
                        break
                    completed.append(result)
                    out.write_text(
                        "".join(
                            json.dumps(item, ensure_ascii=False, separators=(",", ":"))
                            + "\n"
                            for item in completed
                        )
                    )
        finally:
            await provider.aclose()

    asyncio.run(run_all())
    usage_after = usage_snapshot()
    receipt = {
        "status": "NOT_RUN" if stop_reason else "LIVE_COMPLETE",
        "created_at": now(),
        "model": MODEL,
        "comparator": COMPARATOR,
        "prereg_sha256": sha(prereg),
        "corpus_sha256": sha(corpus),
        "state_sha256": sha(states),
        "rows": len(completed),
        "stop_reason": stop_reason,
        "usage_before": usage_before,
        "usage_after": usage_after,
    }
    (HERE / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))
    return 0 if not stop_reason else 3


if __name__ == "__main__":
    raise SystemExit(main())
