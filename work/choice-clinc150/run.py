#!/usr/bin/env python3
"""Live arms for beads jev-qw8 (15 intents) and jev-pm3 (all 150): one Choice with "none of the above".

Bars: docs/demos/upstream-repro/choice-clinc150-20260924.md (--set subset, the default) and
choice-clinc150-full-20260924.md (--set full), each committed before its first call.
Rows: subset -> subset.jsonl, rows-{arm}.jsonl; full -> full.jsonl, rows-full-{arm}.jsonl.
Arms, same state, same question, same labels:
  jev             typesafe-sdk-python TypeSafeClient, model pinned jev-1.13.0
  haiku           system-one-adapter-python, anthropic/claude-haiku-4-5, probabilities mode, native
                  structured outputs
  haiku-prompted  the same with structured_outputs=False (the adapter puts the JSON schema in the
                  prompt and validates the reply) and one corrective retry on malformed output; the
                  fallback jev-4jf needed when Anthropic rejected a 77-option strict grammar
Haiku rows also record the adapter's debug (probability_errors, raw sum), so an all-zero map the
adapter turned into a uniform answer is visible; see adapter-uniform-20260924.md.
--limit N runs only the first N rows still to do (the full set's structured-output probe).
Resumes rows that already have a choice.

Run:
  infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
    upstream/typesafe-ai/system-one-adapter-python/.venv/bin/python \
    work/choice-clinc150/run.py [--set full] [--limit N] [jev|haiku|haiku-prompted]
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
sys.path.insert(0, os.path.join(ROOT, "work", "anthropic-stop"))

from typesafe_sdk import Choice, RetryPolicy, TypeSafeClient
from anthropic_stop import refuse_anthropic_comparator  # noqa: E402  jev-sybt

JEV_MODEL = "jev-1.13.0"
HAIKU_MODEL = "claude-haiku-4-5"
QNAME = "intent"
NONE_LABEL = "none of the above"
NONE_TEXT = "A request that fits none of the above"  # docs-mirror/typesafe/primitives/choice.md:388
OOS = "oos"
# set -> (rows file, rows-file pattern, instructions, concurrency)
SETS = {
    "subset": (
        "subset.jsonl",
        "rows-{arm}.jsonl",
        "The intent of this request to a car and commute assistant",
        8,
    ),
    "full": (
        "full.jsonl",
        "rows-full-{arm}.jsonl",
        "The intent of this request to a virtual assistant",
        16,
    ),
}


def load_rows(fname="subset.jsonl"):
    with open(os.path.join(HERE, fname), encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def labels(rows):
    """Option label -> dataset label: the 15 intents humanized and sorted, then the none option last
    (so an adapter tie, which resolves to the first criterion, never lands on the none option)."""
    intents = sorted({r["intent"] for r in rows if r["intent"] != OOS})
    out = {c.replace("_", " "): c for c in intents}
    out[NONE_LABEL] = OOS
    return out


def question(label_map, instructions=SETS["subset"][2]):
    criteria = {label: None for label in label_map if label != NONE_LABEL}
    criteria[NONE_LABEL] = NONE_TEXT
    return {QNAME: Choice(instructions=instructions, criteria=criteria)}


def state(row):
    return {"user_request": row["text"]}


def done_ids(path):
    ids = set()
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                if line.strip() and "choice" in (r := json.loads(line)):
                    ids.add(r["i"])
    return ids


def record(path, row):
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def answer_row(item, label_map, ans, model, ms, usage, extra=None):
    return {
        "i": item["i"],
        "intent": item["intent"],
        "model": model,
        "choice": label_map.get(ans.choice, ans.choice),
        "confidence": float(ans.confidence),
        "probabilities": {
            label_map.get(k, k): float(v) for k, v in ans.probabilities.items()
        },
        "latencyMs": ms,
        "usage": usage,
        **(extra or {}),
    }


def error_row(item, exc):
    return {
        "i": item["i"],
        "intent": item["intent"],
        "error": f"{type(exc).__name__}: {str(exc)[:1000]}",
    }


def adapter_debug(resp):
    """The adapter's own record of what it did to Haiku's map (probability_normalization.py:21-54)."""
    debug = getattr(resp, "debug", None) or {}
    if not isinstance(debug, dict):
        debug = dict(debug) if hasattr(debug, "keys") else {}
    original = (debug.get("original_probabilities") or {}).get(QNAME)
    return {
        "nRetries": int(getattr(resp.usage, "n_retries", 0) or 0),
        "nRetriesMalformed": int(
            getattr(resp.usage, "n_retries_malformed_structure", 0) or 0
        ),
        "probabilityError": float(
            (debug.get("probability_errors") or {}).get(QNAME, 0.0)
        ),
        "rawSum": None if original is None else float(sum(original.values())),
    }


def run_jev(rows, label_map, path, q, concurrency, limit=None):
    if not os.environ.get("TYPESAFE_API_KEY"):
        print("unconfigured: TYPESAFE_API_KEY unset, no call made", file=sys.stderr)
        return 2
    have = done_ids(path)
    todo = [r for r in rows if r["i"] not in have][:limit]
    print(f"jev: {len(todo)} to run, {len(have)} resumed", file=sys.stderr)
    client = TypeSafeClient(timeout=30.0)

    def one(item):
        t0 = time.perf_counter()
        resp = client.system_one(state(item), q, model=JEV_MODEL)
        ms = int((time.perf_counter() - t0) * 1000)
        usage = {
            "input_tokens": int(resp.usage.input_tokens),
            "output_tokens": int(resp.usage.output_tokens),
        }
        return answer_row(item, label_map, resp.answers[QNAME], resp.model, ms, usage)

    ok = failed = 0
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futs = {pool.submit(one, item): item for item in todo}
        for fut in as_completed(futs):
            try:
                row = fut.result()
                ok += 1
            except Exception as exc:  # noqa: BLE001 - recorded, scored as wrong
                row = error_row(futs[fut], exc)
                failed += 1
            record(path, row)
    print(f"jev done ok={ok} failed={failed}", file=sys.stderr)
    return 3 if failed else 0


def run_haiku(rows, label_map, path, q, concurrency, limit=None, prompted=False):
    refuse_anthropic_comparator(
        f"choice-clinc150 Haiku {'prompted' if prompted else 'native'} arm (claude-haiku-4-5)"
    )
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("unconfigured: ANTHROPIC_API_KEY unset, no call made", file=sys.stderr)
        return 2
    from system_one_adapter import AsyncSystemOneAdapterClient

    have = done_ids(path)
    todo = [r for r in rows if r["i"] not in have][:limit]
    mode = "prompted" if prompted else "structured"
    print(f"haiku {mode}: {len(todo)} to run, {len(have)} resumed", file=sys.stderr)
    extra_opts = {"n_retry_malformed_structure": 1} if prompted else {}

    async def go():
        ok = failed = 0
        sem = asyncio.Semaphore(concurrency)
        async with AsyncSystemOneAdapterClient(
            structured_outputs=not prompted,
            llm_answer_mode="probabilities",
            normalize_probabilities=True,
            retry=RetryPolicy(),
            **extra_opts,
        ) as client:

            async def one(item):
                async with sem:
                    t0 = time.perf_counter()
                    try:
                        resp = await asyncio.wait_for(
                            client.system_one(
                                state(item), q, provider="anthropic", model=HAIKU_MODEL
                            ),
                            timeout=120 if prompted else 90,
                        )
                        ms = int((time.perf_counter() - t0) * 1000)
                        usage = {
                            "input_tokens": int(resp.usage.input_tokens_total),
                            "output_tokens": int(resp.usage.output_tokens_total),
                        }
                        return answer_row(
                            item,
                            label_map,
                            resp.answers[QNAME],
                            f"anthropic/{HAIKU_MODEL}",
                            ms,
                            usage,
                            adapter_debug(resp),
                        )
                    except Exception as exc:  # noqa: BLE001 - recorded, scored as wrong
                        return error_row(item, exc)

            for coro in asyncio.as_completed([one(item) for item in todo]):
                row = await coro
                record(path, row)
                if "error" in row:
                    failed += 1
                else:
                    ok += 1
        print(f"haiku {mode} done ok={ok} failed={failed}", file=sys.stderr)
        return 3 if failed else 0

    return asyncio.run(go())


def take(argv, flag):
    if flag not in argv:
        return None
    at = argv.index(flag)
    value = argv[at + 1]
    del argv[at : at + 2]
    return value


def main(argv):
    argv = list(argv)
    name = take(argv, "--set") or "subset"
    limit = take(argv, "--limit")
    limit = int(limit) if limit else None
    fname, pattern, instructions, concurrency = SETS[name]
    rows = load_rows(fname)
    label_map = labels(rows)
    q = question(label_map, instructions)
    code = 0
    for arm in argv or ["jev", "haiku"]:
        path = os.path.join(HERE, pattern.format(arm=arm))
        if arm == "jev":
            code = run_jev(rows, label_map, path, q, concurrency, limit) or code
        elif arm in ("haiku", "haiku-prompted"):
            prompted = arm == "haiku-prompted"
            code = (
                run_haiku(rows, label_map, path, q, concurrency, limit, prompted)
                or code
            )
        else:
            print(f"unknown arm {arm!r}", file=sys.stderr)
            return 64
    return code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
