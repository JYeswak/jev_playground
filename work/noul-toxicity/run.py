#!/usr/bin/env python3
"""Live arms for bead jev-1kv0. One toxicity Noul per Civil Comments row.

Invoke with the adapter venv, which has typesafe_sdk:
  upstream/typesafe-ai/system-one-adapter-python/.venv/bin/python work/noul-toxicity/run.py jev

Arms: jev | jev-run2 | jev-run3 | grok | grok-run2 | grok-run3.
"""

import asyncio
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(
    0, os.path.join(ROOT, "upstream/typesafe-ai/system-one-adapter-python/src")
)

JEV_MODEL = "jev-1.13.0"
GROK_MODEL = "grok-4.20-0309-non-reasoning"
GROK_URL = "https://api.x.ai/v1"
QNAME = "toxic"
ARMS = ("jev", "jev-run2", "jev-run3", "grok", "grok-run2", "grok-run3")

# Frozen with the bar. Cookbook Noul shape; the hazard is the bead's toxicity question.
INSTRUCTIONS = "Is this text toxic or abusive toward a person or group?"
CRITERIA = {
    "true": "It insults, threatens, or demeans a person or a group.",
    "false": "It does not insult, threaten, or demean a person or a group.",
}


def out_path(arm):
    return os.path.join(HERE, f"rows-{arm}.jsonl")


def answered(arm):
    path = out_path(arm)
    if not os.path.exists(path):
        return set()
    ids = set()
    for line in open(path, encoding="utf-8"):
        if line.strip():
            row = json.loads(line)
            if "error" not in row and "noul" in row:
                ids.add(row["i"])
    return ids


async def main(arm, concurrency=8):
    from system_one_adapter import AsyncSystemOneAdapterClient
    from system_one_adapter.providers.openai import AsyncOpenAIProvider
    from typesafe_sdk import AsyncTypeSafeClient, Noul, RetryPolicy

    question = Noul(instructions=INSTRUCTIONS, criteria=CRITERIA)
    need = "TYPESAFE_API_KEY" if arm.startswith("jev") else "XAI_API_KEY"
    if not os.environ.get(need):
        print(f"unconfigured: {need} is not set, no call made", file=sys.stderr)
        return 2
    sample = [
        json.loads(line)
        for line in open(os.path.join(HERE, "sample.jsonl"), encoding="utf-8")
        if line.strip()
    ]
    have = answered(arm)
    todo = [row for row in sample if row["i"] not in have]
    print(f"{arm}: {len(todo)} to run, {len(have)} resumed", file=sys.stderr)
    sem = asyncio.Semaphore(concurrency)
    ok = failed = 0

    if arm.startswith("jev"):
        client = AsyncTypeSafeClient(model=JEV_MODEL, retry=RetryPolicy())
        provider = None

        async def call(text):
            resp = await client.system_one(text, {QNAME: question})
            return (
                float(resp.nouls[QNAME].noul),
                resp.model,
                {
                    "input_tokens": resp.usage.input_tokens,
                    "output_tokens": resp.usage.output_tokens,
                },
                None,
                None,
            )

    else:
        provider = AsyncOpenAIProvider(
            GROK_MODEL, base_url=GROK_URL, api_key=os.environ["XAI_API_KEY"]
        )
        client = AsyncSystemOneAdapterClient(
            structured_outputs=True,
            llm_answer_mode="probabilities",
            normalize_probabilities=True,
            retry=RetryPolicy(),
        )

        async def call(text):
            resp = await client.system_one(text, {QNAME: question}, model=provider)
            debug = resp.debug or {}
            return (
                float(resp.answers[QNAME].noul),
                f"xai/{GROK_MODEL}",
                {
                    "input_tokens": int(resp.usage.input_tokens_total),
                    "output_tokens": int(resp.usage.output_tokens_total),
                },
                (debug.get("probability_errors") or {}).get(QNAME),
                (debug.get("original_probabilities") or {}).get(QNAME),
            )

    async with client:

        async def one(item):
            async with sem:
                t0 = time.perf_counter()
                row = {"i": item["i"], "arm": arm}
                try:
                    noul, model, usage, perr, orig = await asyncio.wait_for(
                        call(item["text"]), timeout=90
                    )
                    row.update(
                        {
                            "noul": noul,
                            "model": model,
                            "usage": usage,
                            "probabilityError": perr,
                            "originalProbabilities": orig,
                        }
                    )
                except Exception as exc:  # noqa: BLE001 - recorded, scored as a failure
                    row["error"] = f"{type(exc).__name__}: {str(exc)[:200]}"
                row["latencyMs"] = int((time.perf_counter() - t0) * 1000)
                return row

        with open(out_path(arm), "a", encoding="utf-8") as fh:
            for coro in asyncio.as_completed([one(item) for item in todo]):
                row = await coro
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
                fh.flush()
                if "error" in row:
                    failed += 1
                else:
                    ok += 1
                if (ok + failed) % 50 == 0:
                    print(
                        f"  {ok + failed}/{len(todo)} ok={ok} failed={failed}",
                        file=sys.stderr,
                    )
    if provider is not None:
        await provider.aclose()
    print(f"{arm} done: ok={ok} failed={failed}", file=sys.stderr)
    return 3 if failed else 0


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ARMS:
        raise SystemExit(f"usage: run.py {'|'.join(ARMS)}")
    raise SystemExit(asyncio.run(main(sys.argv[1])))
