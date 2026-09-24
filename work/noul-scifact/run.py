#!/usr/bin/env python3
"""Live arms for beads jev-9er, jev-k2q and jev-wx5: one Noul question per claim/evidence pair.

Bars: docs/demos/upstream-repro/noul-scifact-20260924.md (jev, haiku),
noul-scifact-criteria-20260924.md (jev-nocriteria) and noul-fever-20260924.md (jev, haiku on
work/noul-fever), each committed before its first call.
  jev            -> official typesafe_sdk AsyncTypeSafeClient, model pinned jev-1.13.0 (TYPESAFE_API_KEY)
  jev-nocriteria -> same client and instructions, criteria removed (the jev-k2q ablation)
  jev-rerun      -> the jev question again, run beside jev-nocriteria (jev-k2q noise control)
  jev-run2/3     -> the jev question again, into its own rows file (jev-hg8 Jev variance)
  haiku          -> system-one-adapter-python, anthropic/claude-haiku-4-5, probabilities mode (ANTHROPIC_API_KEY)
  haiku-run2/3   -> the haiku arm again, same call, into its own rows file (jev-x5k Haiku variance)
Run (venv python has both packages):
  infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
    upstream/typesafe-ai/system-one-adapter-python/.venv/bin/python work/noul-scifact/run.py <arm> [data_dir]
data_dir (default: this directory) holds sample.jsonl; rows go to <data_dir>/rows-<arm>.jsonl. Rows
that already hold an answer are skipped, so a rerun retries only failed rows. Never prints a key.
Haiku rows also record the adapter's debug.probability_errors and debug.original_probabilities for
the question (jev-mly: the adapter can return a fabricated answer that only debug reveals).
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
sys.path.insert(0, os.path.join(ROOT, "work", "anthropic-stop"))

from system_one_adapter import AsyncSystemOneAdapterClient  # noqa: E402
from anthropic_stop import refuse_paid_comparator  # noqa: E402  jev-sybt, jev-lbgk
from typesafe_sdk import AsyncTypeSafeClient, Noul, RetryPolicy  # noqa: E402

JEV_MODEL = "jev-1.13.0"
HAIKU = ("anthropic", "claude-haiku-4-5")
QNAME = "supports"
# Frozen with the bar. Wording follows docs-mirror/typesafe/cookbooks/citation_check.md.
QUESTION = Noul(
    instructions="Does the abstract support the claim?",
    criteria={
        "true": "The abstract states the claim or directly implies that it is true",
        "false": "The abstract contradicts the claim, or does not address what the claim asserts",
    },
)
# jev-k2q ablation, frozen with its bar: identical instructions, no outcome criteria.
QUESTION_NO_CRITERIA = Noul(instructions=QUESTION.instructions)
ARMS = (
    "jev",
    "jev-nocriteria",
    "jev-rerun",
    "jev-run2",
    "jev-run3",
    "haiku",
    "haiku-run2",
    "haiku-run3",
)


DATA = HERE


def out_path(arm):
    return os.path.join(DATA, f"rows-{arm}.jsonl")


def answered(arm):
    ids = set()
    if os.path.exists(out_path(arm)):
        for line in open(out_path(arm)):
            if line.strip():
                r = json.loads(line)
                if "noul" in r:
                    ids.add(r["i"])
    return ids


def state(s):
    return {"claim": s["claim"], "title": s["title"], "abstract": s["abstract"]}


async def main(arm, concurrency=8):
    if arm.startswith("haiku"):
        refuse_paid_comparator(f"noul-scifact {arm} (claude-haiku-4-5)")
    need = "ANTHROPIC_API_KEY" if arm.startswith("haiku") else "TYPESAFE_API_KEY"
    if not os.environ.get(need):
        print(f"unconfigured: {need} is not set, no call made", file=sys.stderr)
        return 2
    sample = [
        json.loads(line)
        for line in open(os.path.join(DATA, "sample.jsonl"))
        if line.strip()
    ]
    have = answered(arm)
    todo = [s for s in sample if s["i"] not in have]
    print(f"{arm}: {len(todo)} to run, {len(have)} resumed", file=sys.stderr)
    sem = asyncio.Semaphore(concurrency)
    ok = failed = 0

    if not arm.startswith("haiku"):
        client = AsyncTypeSafeClient(model=JEV_MODEL, retry=RetryPolicy())
        question = QUESTION_NO_CRITERIA if arm == "jev-nocriteria" else QUESTION

        async def call(s):
            resp = await client.system_one(state(s), {QNAME: question})
            return {
                "noul": float(resp.nouls[QNAME].noul),
                "model": resp.model,
                "usage": {
                    "input_tokens": resp.usage.input_tokens,
                    "output_tokens": resp.usage.output_tokens,
                },
            }

    else:
        client = AsyncSystemOneAdapterClient(
            structured_outputs=True,
            llm_answer_mode="probabilities",
            normalize_probabilities=True,
            retry=RetryPolicy(),
        )

        async def call(s):
            resp = await client.system_one(
                state(s), {QNAME: QUESTION}, provider=HAIKU[0], model=HAIKU[1]
            )
            debug = resp.debug or {}
            return {
                "noul": float(resp.answers[QNAME].noul),
                "model": "/".join(HAIKU),
                "usage": {
                    "input_tokens": int(resp.usage.input_tokens_total),
                    "output_tokens": int(resp.usage.output_tokens_total),
                },
                "probabilityError": (debug.get("probability_errors") or {}).get(QNAME),
                "originalProbabilities": (
                    debug.get("original_probabilities") or {}
                ).get(QNAME),
            }

    async with client:

        async def one(s):
            async with sem:
                t0 = time.time()
                row = {"i": s["i"], "arm": arm}
                try:
                    row.update(await asyncio.wait_for(call(s), timeout=90))
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
    if len(sys.argv) not in (2, 3) or sys.argv[1] not in ARMS:
        raise SystemExit("usage: run.py " + "|".join(ARMS) + " [data_dir]")
    if len(sys.argv) == 3:
        DATA = os.path.abspath(sys.argv[2])
    sys.exit(asyncio.run(main(sys.argv[1])))
