#!/usr/bin/env python3
"""Live arms for bead jev-jzzs. One Score question, six levels 0-5.

Arms: jev | jev-run2 | jev-run3 | grok | grok-run2 | grok-run3.
The grok arm is grok-4.20-0309-non-reasoning through system-one-adapter's
AsyncOpenAIProvider at https://api.x.ai/v1. Haiku is not called: Anthropic's
key is at its account cap (see the bar). Sentence text is fetched at runtime
and is not written into the row file.
"""

import asyncio
import csv
import hashlib
import io
import json
import os
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(
    0, os.path.join(ROOT, "upstream/typesafe-ai/system-one-adapter-python/src")
)

URL = (
    "https://raw.githubusercontent.com/PhilipMay/stsb-multi-mt/"
    "30de0dec4ee199b7f42351d3f1a0b19592955385/data/stsb-en-dev.csv"
)
SHA256 = "d29586e96558c4eb52cf5ea5d14e9c24d3bf0e44f111b017caba43a5adc33226"
JEV_MODEL = "jev-1.13.0"
GROK_MODEL = "grok-4.20-0309-non-reasoning"
GROK_URL = "https://api.x.ai/v1"
QNAME = "similarity"
ARMS = ("jev", "jev-run2", "jev-run3", "grok", "grok-run2", "grok-run3")

# Frozen with the bar. Index is the STS level. Wording is the SemEval-2015
# gold-standard interpretation, read from the task page on 2026-09-24.
QUESTION_CRITERIA = [
    "The two sentences are on different topics.",
    "The two sentences are not equivalent, but are on the same topic.",
    "The two sentences are not equivalent, but share some details.",
    "The two sentences are roughly equivalent, but some important information differs/missing.",
    "The two sentences are mostly equivalent, but some unimportant details differ.",
    "The two sentences are completely equivalent, as they mean the same thing.",
]


def fetch_pairs():
    req = urllib.request.Request(
        URL, headers={"User-Agent": "OpenAI File Downloader, XaiImageApiFetch/1.0"}
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read()
    if hashlib.sha256(data).hexdigest() != SHA256:
        raise SystemExit("sha256 mismatch; no call made")
    rows = list(csv.reader(io.StringIO(data.decode("utf-8"))))
    if len(rows) != 1500:
        raise SystemExit(f"expected 1500 pairs, got {len(rows)}; no call made")
    return rows


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
            if "error" not in row and "score" in row:
                ids.add(row["i"])
    return ids


def row_from(answer, model, usage):
    probs = {str(int(k)): float(v) for k, v in answer.probabilities.items()}
    return {
        "model": model,
        "score": float(answer.score),
        "confidence": float(answer.confidence)
        if answer.confidence is not None
        else None,
        "probabilities": probs,
        "usage": usage,
    }


async def main(arm, concurrency=8):
    from system_one_adapter import AsyncSystemOneAdapterClient
    from system_one_adapter.providers.openai import AsyncOpenAIProvider
    from typesafe_sdk import AsyncTypeSafeClient, RetryPolicy, Score

    question = Score(
        instructions="How similar in meaning are these two sentences?",
        criteria=QUESTION_CRITERIA,
    )
    need = "TYPESAFE_API_KEY" if arm.startswith("jev") else "XAI_API_KEY"
    if not os.environ.get(need):
        print(f"unconfigured: {need} is not set, no call made", file=sys.stderr)
        return 2
    pairs = fetch_pairs()
    have = answered(arm)
    todo = [i for i in range(len(pairs)) if i not in have]
    print(f"{arm}: {len(todo)} to run, {len(have)} resumed", file=sys.stderr)
    sem = asyncio.Semaphore(concurrency)
    ok = failed = 0

    if arm.startswith("jev"):
        client = AsyncTypeSafeClient(model=JEV_MODEL, retry=RetryPolicy())
        provider = None

        async def call(state):
            resp = await client.system_one(state, {QNAME: question})
            usage = {
                "input_tokens": resp.usage.input_tokens,
                "output_tokens": resp.usage.output_tokens,
            }
            return row_from(resp.scores[QNAME], resp.model, usage)

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

        async def call(state):
            resp = await client.system_one(state, {QNAME: question}, model=provider)
            usage = {
                "input_tokens": int(resp.usage.input_tokens_total),
                "output_tokens": int(resp.usage.output_tokens_total),
            }
            debug = resp.debug or {}
            row = row_from(resp.answers[QNAME], f"xai/{GROK_MODEL}", usage)
            row["probabilityError"] = (debug.get("probability_errors") or {}).get(QNAME)
            row["originalProbabilities"] = (
                debug.get("original_probabilities") or {}
            ).get(QNAME)
            return row

    async with client:

        async def one(i):
            async with sem:
                t0 = time.perf_counter()
                s1, s2, _label = pairs[i]
                state = {"sentence1": s1, "sentence2": s2}
                row = {"i": i, "arm": arm}
                try:
                    row.update(await asyncio.wait_for(call(state), timeout=90))
                except Exception as exc:  # noqa: BLE001 - recorded, scored as a failure
                    row["error"] = f"{type(exc).__name__}: {str(exc)[:200]}"
                row["latencyMs"] = int((time.perf_counter() - t0) * 1000)
                return row

        with open(out_path(arm), "a", encoding="utf-8") as fh:
            for coro in asyncio.as_completed([one(i) for i in todo]):
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
