#!/usr/bin/env python3
"""Live arms for bead jev-k3k: one Choice question over 10 Banking77 intents, two models.

Bar: docs/demos/upstream-repro/choice-banking77-20260924.md (committed before any call).
Arms:
  jev    typesafe-sdk-python TypeSafeClient, model pinned jev-1.13.0  -> rows-jev.jsonl
  haiku  system-one-adapter-python, anthropic/claude-haiku-4-5,
         llm_answer_mode="probabilities"                              -> rows-haiku.jsonl
Same state, same question, same labels in both arms. Resumes rows that already have a choice.

Run (both arms):
  infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
    upstream/typesafe-ai/system-one-adapter-python/.venv/bin/python work/choice-banking77/run.py [jev|haiku]
Never prints a key.
"""

import asyncio
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "upstream/typesafe-ai/typesafe-sdk-python/src"))
sys.path.insert(
    0, os.path.join(ROOT, "upstream/typesafe-ai/system-one-adapter-python/src")
)

from typesafe_sdk import Choice, RetryPolicy, TypeSafeClient  # noqa: E402

JEV_MODEL = "jev-1.13.0"
HAIKU_MODEL = "claude-haiku-4-5"
INSTRUCTIONS = "The primary intent of this customer banking message"
CONCURRENCY = 8
FAIL_LIMIT = 4


def load_rows():
    with open(os.path.join(HERE, "subset.jsonl"), encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def humanize(intent):
    return intent.replace("_", " ")


def labels(rows):
    """Sorted intent names -> humanized option labels (criteria described by name alone)."""
    intents = sorted({r["intent"] for r in rows}, key=lambda c: (c.casefold(), c))
    return {humanize(c): c for c in intents}


def question(label_map):
    return {
        "intent": Choice(
            instructions=INSTRUCTIONS, criteria={label: None for label in label_map}
        )
    }


def state(row):
    return {"customer_message": row["text"]}


def done_ids(path):
    ids = set()
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    r = json.loads(line)
                    if "choice" in r:
                        ids.add(r["i"])
    return ids


def record(path, row):
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def answer_row(item, label_map, ans, model, elapsed_ms, usage):
    return {
        "i": item["i"],
        "intent": item["intent"],
        "model": model,
        "choice": label_map.get(ans.choice, ans.choice),
        "confidence": float(ans.confidence),
        "probabilities": {
            label_map.get(k, k): float(v) for k, v in ans.probabilities.items()
        },
        "latencyMs": elapsed_ms,
        "usage": usage,
    }


def run_jev(rows, label_map):
    if not os.environ.get("TYPESAFE_API_KEY"):
        print("unconfigured: TYPESAFE_API_KEY unset, no call made", file=sys.stderr)
        return 2
    path = os.path.join(HERE, "rows-jev.jsonl")
    have = done_ids(path)
    todo = [r for r in rows if r["i"] not in have]
    print(f"jev: {len(todo)} to run, {len(have)} resumed", file=sys.stderr)
    client = TypeSafeClient(timeout=30.0)
    q = question(label_map)

    def one(item):
        t0 = time.perf_counter()
        resp = client.system_one(state(item), q, model=JEV_MODEL)
        ms = int((time.perf_counter() - t0) * 1000)
        usage = {
            "input_tokens": int(resp.usage.input_tokens),
            "output_tokens": int(resp.usage.output_tokens),
        }
        return answer_row(
            item, label_map, resp.answers["intent"], resp.model, ms, usage
        )

    ok = failed = 0
    with ThreadPoolExecutor(max_workers=CONCURRENCY) as pool:
        futs = {pool.submit(one, item): item for item in todo}
        for fut in as_completed(futs):
            item = futs[fut]
            try:
                row = fut.result()
                ok += 1
            except Exception as exc:  # noqa: BLE001 - recorded, scored as wrong
                row = {
                    "i": item["i"],
                    "intent": item["intent"],
                    "error": f"{type(exc).__name__}: {str(exc)[:200]}",
                }
                failed += 1
            record(path, row)
            if (ok + failed) % 50 == 0:
                print(
                    f"  jev {ok + failed}/{len(todo)} failed={failed}", file=sys.stderr
                )
    print(f"jev done ok={ok} failed={failed}", file=sys.stderr)
    return 3 if failed > FAIL_LIMIT else 0


def run_haiku(rows, label_map):
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("unconfigured: ANTHROPIC_API_KEY unset, no call made", file=sys.stderr)
        return 2
    from system_one_adapter import AsyncSystemOneAdapterClient

    path = os.path.join(HERE, "rows-haiku.jsonl")
    have = done_ids(path)
    todo = [r for r in rows if r["i"] not in have]
    print(f"haiku: {len(todo)} to run, {len(have)} resumed", file=sys.stderr)
    q = question(label_map)

    async def go():
        ok = failed = 0
        sem = asyncio.Semaphore(CONCURRENCY)
        async with AsyncSystemOneAdapterClient(
            structured_outputs=True,
            llm_answer_mode="probabilities",
            normalize_probabilities=True,
            retry=RetryPolicy(),
        ) as client:

            async def one(item):
                async with sem:
                    t0 = time.perf_counter()
                    try:
                        resp = await asyncio.wait_for(
                            client.system_one(
                                state(item), q, provider="anthropic", model=HAIKU_MODEL
                            ),
                            timeout=90,
                        )
                        ms = int((time.perf_counter() - t0) * 1000)
                        usage = {
                            "input_tokens": int(resp.usage.input_tokens_total),
                            "output_tokens": int(resp.usage.output_tokens_total),
                        }
                        return answer_row(
                            item,
                            label_map,
                            resp.answers["intent"],
                            f"anthropic/{HAIKU_MODEL}",
                            ms,
                            usage,
                        )
                    except Exception as exc:  # noqa: BLE001 - recorded, scored as wrong
                        return {
                            "i": item["i"],
                            "intent": item["intent"],
                            "error": f"{type(exc).__name__}: {str(exc)[:200]}",
                        }

            for coro in asyncio.as_completed([one(item) for item in todo]):
                row = await coro
                record(path, row)
                if "error" in row:
                    failed += 1
                else:
                    ok += 1
                if (ok + failed) % 50 == 0:
                    print(
                        f"  haiku {ok + failed}/{len(todo)} failed={failed}",
                        file=sys.stderr,
                    )
        print(f"haiku done ok={ok} failed={failed}", file=sys.stderr)
        return 3 if failed > FAIL_LIMIT else 0

    return asyncio.run(go())


def main(argv):
    rows = load_rows()
    label_map = labels(rows)
    arms = argv or ["jev", "haiku"]
    code = 0
    for arm in arms:
        if arm == "jev":
            code = run_jev(rows, label_map) or code
        elif arm == "haiku":
            code = run_haiku(rows, label_map) or code
        else:
            print(f"unknown arm {arm!r}", file=sys.stderr)
            return 64
    return code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
