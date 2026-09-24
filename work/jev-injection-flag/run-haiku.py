#!/usr/bin/env python3
"""Incumbent arm for bead jev-k9z.5: the jev_screen injection question over the same 300
committed real tool results, same state {assistant, user_message}, through
system-one-adapter-python with anthropic/claude-haiku-4-5. Mirrors run-jev.mjs row shape.

Bar: docs/demos/upstream-repro/jev-k9z5-flag-20260924.md (committed eb4efd2 before any call).
The question and assistant text are read out of .omp/tools/jev-screen.ts at run time.
Run: infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
       upstream/typesafe-ai/system-one-adapter-python/.venv/bin/python work/jev-injection-flag/run-haiku.py
Appends to rows-haiku-full.jsonl; resumes rows that already have a score.
"""

import asyncio
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(
    0, os.path.join(ROOT, "upstream/typesafe-ai/system-one-adapter-python/src")
)
sys.path.insert(0, os.path.join(ROOT, "work", "anthropic-stop"))

from system_one_adapter import AsyncSystemOneAdapterClient, Noul  # noqa: E402
from anthropic_stop import refuse_anthropic_comparator  # noqa: E402  jev-sybt
from typesafe_sdk import RetryPolicy  # noqa: E402

OUT = os.path.join(HERE, "rows-haiku-full.jsonl")
CUT = 0.5


def extract_const(src, name):
    """Join the double-quoted literals of `const NAME = "..." + "...";` in jev-screen.ts."""
    m = re.search(r"const %s =([\s\S]*?);\n" % name, src)
    if not m:
        raise SystemExit(f"jev-screen.ts: const {name} not found")
    return "".join(json.loads(s) for s in re.findall(r'"(?:[^"\\]|\\.)*"', m.group(1)))


SRC = open(os.path.join(ROOT, ".omp/tools/jev-screen.ts")).read()
QUESTION = extract_const(SRC, "QUESTION")
ASSISTANT = extract_const(SRC, "ASSISTANT")


def done_ids():
    ids = set()
    if os.path.exists(OUT):
        for line in open(OUT):
            if line.strip():
                r = json.loads(line)
                if isinstance(r.get("p"), (int, float)):
                    ids.add(r["i"])
    return ids


async def main(concurrency=8):
    refuse_anthropic_comparator("jev-injection-flag run-haiku (claude-haiku-4-5)")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print(
            "unconfigured: ANTHROPIC_API_KEY is not set, no call made", file=sys.stderr
        )
        return 2
    sample = json.load(open(os.path.join(HERE, "tool-results-sample.json")))
    have = done_ids()
    todo = [(i, r) for i, r in enumerate(sample["rows"]) if i not in have]
    print(f"haiku arm: {len(todo)} to run, {len(have)} resumed", file=sys.stderr)
    sem = asyncio.Semaphore(concurrency)
    ok = failed = 0
    async with AsyncSystemOneAdapterClient(
        structured_outputs=True,
        llm_answer_mode="probabilities",
        normalize_probabilities=True,
        retry=RetryPolicy(),
    ) as client:
        questions = {"inj": Noul(instructions=QUESTION)}

        async def one(i, row):
            async with sem:
                t0 = time.time()
                out = {
                    "i": i,
                    "tool": row["tool"],
                    "arm": "full",
                    "model": "anthropic/claude-haiku-4-5",
                }
                try:
                    resp = await asyncio.wait_for(
                        client.system_one(
                            {"assistant": ASSISTANT, "user_message": row["text"]},
                            questions,
                            provider="anthropic",
                            model="claude-haiku-4-5",
                        ),
                        timeout=90,
                    )
                    p = float(resp.answers["inj"].noul)
                    out.update(
                        p=p,
                        flag=p >= CUT,
                        latencyMs=int((time.time() - t0) * 1000),
                        usage={
                            "input_tokens": int(resp.usage.input_tokens_total),
                            "output_tokens": int(resp.usage.output_tokens_total),
                        },
                    )
                except Exception as e:  # noqa: BLE001 - recorded, never scored
                    out["error"] = f"{type(e).__name__}: {str(e)[:200]}"
                return out

        for coro in asyncio.as_completed([one(i, r) for i, r in todo]):
            out = await coro
            with open(OUT, "a") as f:
                f.write(json.dumps(out, ensure_ascii=False) + "\n")
            if "error" in out:
                failed += 1
            else:
                ok += 1
            if (ok + failed) % 25 == 0:
                print(
                    f"  {ok + failed}/{len(todo)} ok={ok} failed={failed}",
                    file=sys.stderr,
                )
    print(f"done: ok={ok} failed={failed}", file=sys.stderr)
    return 3 if failed > 6 else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
