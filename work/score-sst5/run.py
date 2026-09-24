#!/usr/bin/env python3
"""Both live arms for bead jev-zui: one Score question over each SST-5 sample sentence.

Bar: docs/demos/upstream-repro/score-sst5-20260924.md (committed before the first call).
  jev   -> official typesafe_sdk AsyncTypeSafeClient, model pinned jev-1.13.0 (TYPESAFE_API_KEY)
  haiku -> system-one-adapter-python, anthropic/claude-haiku-4-5, probabilities mode (ANTHROPIC_API_KEY)
Run (venv python has both packages):
  infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
    upstream/typesafe-ai/system-one-adapter-python/.venv/bin/python work/score-sst5/run.py jev|haiku
Appends to work/score-sst5/rows-<arm>.jsonl (or to the optional second argument, a path, used for
repeat runs); rows that already hold an answer are skipped, so a rerun retries only failed rows.
Never prints a key.
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

from system_one_adapter import AsyncSystemOneAdapterClient  # noqa: E402
from typesafe_sdk import AsyncTypeSafeClient, RetryPolicy, Score  # noqa: E402

JEV_MODEL = "jev-1.13.0"
HAIKU = ("anthropic", "claude-haiku-4-5")
QNAME = "sentiment"
# Frozen with the bar. Level index 0..4 equals the SST-5 label id.
QUESTION = Score(
    instructions="How positive is this movie review sentence?",
    criteria=[
        "Very negative: strongly critical, scathing, or contemptuous",
        "Negative: somewhat critical or unfavorable",
        "Neutral: neither positive nor negative, or evenly mixed",
        "Positive: somewhat favorable or approving",
        "Very positive: strongly enthusiastic, glowing, or full of praise",
    ],
)


OUT = None  # optional second CLI argument; None keeps the default rows-<arm>.jsonl


def out_path(arm):
    return OUT or os.path.join(HERE, f"rows-{arm}.jsonl")


def answered(arm):
    ids = set()
    if os.path.exists(out_path(arm)):
        for line in open(out_path(arm)):
            if line.strip():
                r = json.loads(line)
                if "score" in r:
                    ids.add(r["i"])
    return ids


def row_from(answer, resp_model, usage):
    probs = {str(int(k)): float(v) for k, v in answer.probabilities.items()}
    return {
        "score": float(answer.score),
        "confidence": float(answer.confidence),
        "probabilities": dict(sorted(probs.items(), key=lambda kv: int(kv[0]))),
        "model": resp_model,
        "usage": usage,
    }


async def main(arm, concurrency=8):
    need = {"jev": "TYPESAFE_API_KEY", "haiku": "ANTHROPIC_API_KEY"}[arm]
    if not os.environ.get(need):
        print(f"unconfigured: {need} is not set, no call made", file=sys.stderr)
        return 2
    sample = [
        json.loads(line)
        for line in open(os.path.join(HERE, "sample.jsonl"))
        if line.strip()
    ]
    have = answered(arm)
    todo = [s for s in sample if s["i"] not in have]
    print(f"{arm}: {len(todo)} to run, {len(have)} resumed", file=sys.stderr)
    sem = asyncio.Semaphore(concurrency)
    ok = failed = 0

    if arm == "jev":
        client = AsyncTypeSafeClient(model=JEV_MODEL, retry=RetryPolicy())

        async def call(text):
            resp = await client.system_one(text, {QNAME: QUESTION})
            u = {
                "input_tokens": resp.usage.input_tokens,
                "output_tokens": resp.usage.output_tokens,
            }
            return row_from(resp.scores[QNAME], resp.model, u)

    else:
        client = AsyncSystemOneAdapterClient(
            structured_outputs=True,
            llm_answer_mode="probabilities",
            normalize_probabilities=True,
            retry=RetryPolicy(),
        )

        async def call(text):
            resp = await client.system_one(
                text, {QNAME: QUESTION}, provider=HAIKU[0], model=HAIKU[1]
            )
            u = {
                "input_tokens": int(resp.usage.input_tokens_total),
                "output_tokens": int(resp.usage.output_tokens_total),
            }
            return row_from(resp.answers[QNAME], "/".join(HAIKU), u)

    async with client:

        async def one(s):
            async with sem:
                t0 = time.time()
                row = {"i": s["i"], "arm": arm}
                try:
                    row.update(await asyncio.wait_for(call(s["text"]), timeout=90))
                    row["latencyMs"] = int((time.time() - t0) * 1000)
                except Exception as e:  # noqa: BLE001 - recorded, scored as a failure
                    row["error"] = f"{type(e).__name__}: {str(e)[:200]}"
                return row

        for coro in asyncio.as_completed([one(s) for s in todo]):
            row = await coro
            with open(out_path(arm), "a") as f:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
            if "error" in row:
                failed += 1
            else:
                ok += 1
            if (ok + failed) % 50 == 0:
                print(
                    f"  {ok + failed}/{len(todo)} ok={ok} failed={failed}",
                    file=sys.stderr,
                )
    print(f"done: ok={ok} failed={failed}", file=sys.stderr)
    return 3 if failed else 0


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3) or sys.argv[1] not in ("jev", "haiku"):
        raise SystemExit("usage: run.py jev|haiku [out.jsonl]")
    if len(sys.argv) == 3:
        OUT = os.path.abspath(sys.argv[2])
    sys.exit(asyncio.run(main(sys.argv[1])))
