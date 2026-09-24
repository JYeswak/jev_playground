#!/usr/bin/env python3
"""Live arms for bead jev-2wc: jev-curate's code_quality Score over every QuixBugs program.

Bar: docs/demos/upstream-repro/score-quixbugs-20260924.md (committed before the first call).
  jev       -> official typesafe_sdk AsyncTypeSafeClient, jev-1.13.0, state {"text": canon}   (primary)
  haiku     -> system-one-adapter-python, anthropic/claude-haiku-4-5, probabilities mode, same state
               (primary incumbent); records debug.probability_errors / original_probabilities (jev-mly)
  jev-flat  -> Jev, state {"text": flat}: canon after jev-curate's own line-trimming (descriptive)
  jev-asis  -> Jev, state {"text": asis}: the file as shipped, docstrings included (descriptive)
Run (venv python has both packages):
  infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
    upstream/typesafe-ai/system-one-adapter-python/.venv/bin/python work/score-quixbugs/run.py <arm>
Appends to work/score-quixbugs/rows-<arm>.jsonl; rows that already hold an answer are skipped, so a
rerun retries only failed rows. Never prints a key.
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
QNAME = "code_quality"
# Frozen with the bar: jev-curate src/presets.rs:136-147 at d1a3a05, the five descriptions in key
# order "1".."5", sent as the ordered list the API requires (0-based levels 0..4).
QUESTION = Score(
    instructions="Rate the completeness, idiomacy, and correctness of this code snippet.",
    criteria=[
        "Broken, pseudo-code, or unrunnable syntax",
        "Partial implementation with obvious bugs",
        "Working implementation with minimal edge case handling",
        "Clean, idiomatic code with error handling",
        "Production-grade, fully typed, battle-tested implementation",
    ],
)
ARMS = {"jev": "canon", "haiku": "canon", "jev-flat": "flat", "jev-asis": "asis"}


def out_path(arm):
    return os.path.join(HERE, f"rows-{arm}.jsonl")


def answered(arm):
    ids = set()
    if os.path.exists(out_path(arm)):
        with open(out_path(arm)) as f:
            for line in f:
                if line.strip() and "score" in (r := json.loads(line)):
                    ids.add(r["i"])
    return ids


def row_from(answer, model, usage):
    probs = {str(int(k)): float(v) for k, v in answer.probabilities.items()}
    return {
        "score": float(answer.score),
        "confidence": float(answer.confidence),
        "probabilities": dict(sorted(probs.items(), key=lambda kv: int(kv[0]))),
        "model": model,
        "usage": usage,
    }


async def main(arm, concurrency=8):
    need = "ANTHROPIC_API_KEY" if arm == "haiku" else "TYPESAFE_API_KEY"
    if not os.environ.get(need):
        print(f"unconfigured: {need} is not set, no call made", file=sys.stderr)
        return 2
    with open(os.path.join(HERE, "sample.jsonl")) as f:
        sample = [json.loads(line) for line in f if line.strip()]
    have = answered(arm)
    todo = [s for s in sample if s["i"] not in have]
    print(f"{arm}: {len(todo)} to run, {len(have)} resumed", file=sys.stderr)
    sem = asyncio.Semaphore(concurrency)
    ok = failed = 0

    if arm != "haiku":
        client = AsyncTypeSafeClient(model=JEV_MODEL, retry=RetryPolicy())

        async def call(state):
            resp = await client.system_one(state, {QNAME: QUESTION})
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

        async def call(state):
            resp = await client.system_one(
                state, {QNAME: QUESTION}, provider=HAIKU[0], model=HAIKU[1]
            )
            u = {
                "input_tokens": int(resp.usage.input_tokens_total),
                "output_tokens": int(resp.usage.output_tokens_total),
            }
            debug = resp.debug or {}
            row = row_from(resp.answers[QNAME], "/".join(HAIKU), u)
            row["probabilityError"] = (debug.get("probability_errors") or {}).get(QNAME)
            row["originalProbabilities"] = (
                debug.get("original_probabilities") or {}
            ).get(QNAME)
            return row

    async with client:

        async def one(s):
            async with sem:
                t0 = time.time()
                row = {"i": s["i"], "arm": arm}
                try:
                    row.update(
                        await asyncio.wait_for(call({"text": s[ARMS[arm]]}), timeout=90)
                    )
                    row["latencyMs"] = int((time.time() - t0) * 1000)
                except Exception as e:  # noqa: BLE001 - recorded, scored as a failure
                    row["error"] = f"{type(e).__name__}: {str(e)[:200]}"
                return row

        for coro in asyncio.as_completed([one(s) for s in todo]):
            row = await coro
            with open(out_path(arm), "a") as f:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
            failed += "error" in row
            ok += "error" not in row
    print(f"done: ok={ok} failed={failed}", file=sys.stderr)
    return 3 if failed else 0


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ARMS:
        raise SystemExit("usage: run.py " + "|".join(ARMS))
    sys.exit(asyncio.run(main(sys.argv[1])))
