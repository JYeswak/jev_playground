#!/usr/bin/env python3
"""Run the preregistered Jev arm for jev-gdhb; never invokes the free arm."""

from __future__ import annotations

import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "work" / "jev-gdhb"
sys.path.insert(0, str(ROOT / "upstream/typesafe-ai/typesafe-sdk-python/src"))
from typesafe_sdk import Choice, TypeSafeClient  # noqa: E402

MODEL = "jev-1.13.0"
QNAME = "intent"
OUT = HERE / "rows-jev.jsonl"


def main() -> int:
    if not os.environ.get("TYPESAFE_API_KEY"):
        print("NOT_RUN: TYPESAFE_API_KEY unset; no call made", file=sys.stderr)
        return 2
    items = [
        json.loads(line)
        for line in (HERE / "corpus.jsonl").read_text().splitlines()
        if line
    ]
    labels = sorted({item["label"] for item in items})
    question = {
        QNAME: Choice(
            instructions="What is the intent of this user request?",
            criteria={label: None for label in labels},
        )
    }
    done = set()
    if OUT.exists():
        done = {
            json.loads(line)["id"]
            for line in OUT.read_text().splitlines()
            if line and "choice" in json.loads(line)
        }
    todo = [item for item in items if item["id"] not in done]
    client = TypeSafeClient(timeout=30.0)

    def one(item):
        started = time.perf_counter()
        response = client.system_one({"text": item["text"]}, question, model=MODEL)
        answer = response.answers[QNAME]
        return {
            "id": item["id"],
            "source_row": item["source_row"],
            "gold": item["label"],
            "choice": answer.choice,
            "confidence": float(answer.confidence),
            "probabilities": {
                str(k): float(v) for k, v in answer.probabilities.items()
            },
            "model": response.model,
            "usage": {
                "input_tokens": int(response.usage.input_tokens),
                "output_tokens": int(response.usage.output_tokens),
            },
            "latency_ms": int((time.perf_counter() - started) * 1000),
        }

    with ThreadPoolExecutor(max_workers=16) as pool:
        futures = {pool.submit(one, item): item for item in todo}
        for future in as_completed(futures):
            row = future.result()
            with OUT.open("a") as fh:
                fh.write(
                    json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n"
                )
    print(
        json.dumps(
            {
                "status": "LIVE_COMPLETE",
                "model": MODEL,
                "rows": len(items),
                "completed": len(todo),
                "comparator": "NOT_RUN_BY_DESIGN",
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
