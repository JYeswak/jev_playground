#!/usr/bin/env python3
from __future__ import annotations
import asyncio, hashlib, json, re, time
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "work/jev-vg4s"
sys.path.insert(0, str(ROOT / "upstream/typesafe-ai/typesafe-sdk-python/src"))
from typesafe_sdk import AsyncTypeSafeClient, RetryPolicy, Noul

MODEL = "jev-1.13.0"
QNAME = "supports"
OUT = HERE / "live-rows-jev.jsonl"
RECEIPT = HERE / "receipt-jev.json"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


async def main():
    prereg = HERE / "PREREG.md"
    corpus = HERE / "corpus.jsonl"
    states = HERE / "states.jsonl"
    reach = json.loads((HERE / "reachability.json").read_text())
    if (
        reach["prereg_sha256"] != sha(prereg)
        or reach["items_sha256"] != sha(corpus)
        or reach["states_sha256"] != sha(states)
    ):
        raise RuntimeError("reach binding mismatch")
    items = [json.loads(x) for x in corpus.read_text().splitlines() if x]
    state_by = {
        json.loads(x)["id"]: json.loads(x)["state"]
        for x in states.read_text().splitlines()
        if x
    }
    existing = []
    if OUT.exists():
        existing = [json.loads(x) for x in OUT.read_text().splitlines() if x]
    done = {r["id"] for r in existing}
    todo = [r for r in items if r["id"] not in done]
    q = {
        QNAME: Noul(
            instructions="Does the evidence support the claim?",
            criteria={
                "true": "The evidence states the claim or directly implies that it is true",
                "false": "The evidence contradicts the claim, or does not address what the claim asserts",
            },
        )
    }
    client = AsyncTypeSafeClient(model=MODEL, retry=RetryPolicy())
    sem = asyncio.Semaphore(8)

    async def one(item):
        async with sem:
            t = time.perf_counter()
            row = {
                "id": item["id"],
                "source_row": item["source_row"],
                "label": item["label"],
            }
            try:
                resp = await asyncio.wait_for(
                    client.system_one(state_by[item["id"]], q), 120
                )
                a = resp.nouls[QNAME]
                row.update(
                    {
                        "status": "scored",
                        "noul": float(a.noul),
                        "prediction": "SUPPORTS"
                        if float(a.noul) > 0.5
                        else "NOT_SUPPORTED",
                        "model": resp.model,
                        "usage": {
                            "input_tokens": int(resp.usage.input_tokens),
                            "output_tokens": int(resp.usage.output_tokens)
                            if resp.usage
                            else None,
                        },
                        "latency_ms": int((time.perf_counter() - t) * 1000),
                    }
                )
            except Exception as e:
                row.update(
                    {
                        "status": "invalid",
                        "error": f"{type(e).__name__}: {str(e)[:300]}",
                        "latency_ms": int((time.perf_counter() - t) * 1000),
                    }
                )
            return row

    async with client:
        for fut in asyncio.as_completed([one(x) for x in todo]):
            row = await fut
            existing.append(row)
            OUT.write_text(
                "".join(
                    json.dumps(x, ensure_ascii=False, separators=(",", ":")) + "\n"
                    for x in existing
                )
            )
    rows = [json.loads(x) for x in OUT.read_text().splitlines() if x]
    scored = [r for r in rows if r.get("status") == "scored"]
    tin = sum(r["usage"]["input_tokens"] for r in scored if r.get("usage"))
    tout = sum(r["usage"]["output_tokens"] or 0 for r in scored if r.get("usage"))
    from datetime import datetime, timezone

    receipt = {
        "status": "LIVE_COMPLETE" if len(rows) == len(items) else "NOT_RUN",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "model": MODEL,
        "comparator": "none",
        "prereg_sha256": sha(prereg),
        "corpus_sha256": sha(corpus),
        "states_sha256": sha(states),
        "rows": len(rows),
        "invalid": len(rows) - len(scored),
        "usage": {
            "input_tokens": tin,
            "output_tokens": tout,
            "spend_usd": tin * 0.042 / 1_000_000,
        },
        "boundary": "Jev-only arm; free comparator remains date-gated",
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
