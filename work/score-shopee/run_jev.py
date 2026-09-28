#!/usr/bin/env python3
from __future__ import annotations
import asyncio, hashlib, json, re, time
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "work/score-shopee"
sys.path.insert(0, str(ROOT / "upstream/typesafe-ai/typesafe-sdk-python/src"))
from typesafe_sdk import AsyncTypeSafeClient, RetryPolicy, Score

MODEL = "jev-1.13.0"
QNAME = "sentiment"
OUT = HERE / "live-rows-jev.jsonl"
RECEIPT = HERE / "receipt-jev.json"
LEVELS = [
    "Very negative: strongly critical, scathing, or contemptuous",
    "Negative: somewhat critical or unfavorable",
    "Neutral: neither positive nor negative, or evenly mixed",
    "Positive: somewhat favorable or approving",
    "Very positive: strongly enthusiastic, glowing, or full of praise",
]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def now():
    return time.time()


def hard(s):
    return bool(re.search(r"\b(?:401|402|403)\b", s))


async def main():
    prereg = HERE / "PREREG.md"
    corpus = HERE / "corpus.jsonl"
    reach = json.loads((HERE / "reach-receipt.json").read_text())
    if reach["prereg_sha256"] != sha(prereg) or reach["items_sha256"] != sha(corpus):
        raise RuntimeError("reach binding mismatch")
    items = [json.loads(x) for x in corpus.read_text().splitlines() if x]
    existing = []
    if OUT.exists():
        existing = [json.loads(x) for x in OUT.read_text().splitlines() if x]
    done = {r["id"] for r in existing}
    todo = [r for r in items if r["id"] not in done]
    q = {QNAME: Score(instructions="How positive is this review?", criteria=LEVELS)}
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
                    client.system_one({"text": item["text"]}, q), 120
                )
                a = resp.scores[QNAME]
                row.update(
                    {
                        "status": "scored",
                        "raw_score": float(a.score),
                        "level": max(0, min(4, int(float(a.score) + 0.5))),
                        "confidence": float(a.confidence),
                        "probabilities": {
                            str(k): float(v) for k, v in a.probabilities.items()
                        },
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
                if hard(str(e)):
                    raise
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
    receipt = {
        "status": "LIVE_COMPLETE" if len(rows) == len(items) else "NOT_RUN",
        "created_at": __import__("datetime")
        .datetime.now(__import__("datetime").timezone.utc)
        .isoformat(),
        "model": MODEL,
        "comparator": "none",
        "prereg_sha256": sha(prereg),
        "corpus_sha256": sha(corpus),
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
