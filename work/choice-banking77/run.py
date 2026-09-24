#!/usr/bin/env python3
"""Live arms for beads jev-k3k (10 intents) and jev-4jf (all 77): one Choice, two models.

Bars: docs/demos/upstream-repro/choice-banking77-20260924.md (--set subset, the default) and
choice-banking77-full-20260924.md (--set full), each committed before its first call.
Arms:
  jev    typesafe-sdk-python TypeSafeClient, model pinned jev-1.13.0
  haiku  system-one-adapter-python, anthropic/claude-haiku-4-5, llm_answer_mode="probabilities"
Rows: subset -> rows-{jev,haiku}.jsonl; full -> rows-full-{jev,haiku}.jsonl.
Same state, same question, same labels in both arms. Resumes rows that already have a choice.

Run:
  infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
    upstream/typesafe-ai/system-one-adapter-python/.venv/bin/python \
    work/choice-banking77/run.py [--set full] [--out rows.jsonl] [jev|haiku]
--out replaces the rows path (repeat runs, bead jev-qbc) and needs exactly one arm.
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
SETS = {
    "subset": ("subset.jsonl", "rows-{arm}.jsonl"),
    "full": ("full.jsonl", "rows-full-{arm}.jsonl"),
}


def load_rows(fname):
    with open(os.path.join(HERE, fname), encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def fail_limit(rows):
    """More failed rows than 1% of the set is a failed run (4 of 400, 30 of 3080)."""
    return len(rows) // 100


def humanize(intent):
    """Underscores to spaces, lowercased (the source spells one intent Refund_not_showing_up)."""
    return intent.replace("_", " ").lower()


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


def answer_row(item, label_map, ans, model, elapsed_ms, usage, extra=None):
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
        **(extra or {}),
    }


def error_row(item, exc):
    """Kept verbatim up to 1,000 chars so an option-count or schema cap is recorded as sent."""
    return {
        "i": item["i"],
        "intent": item["intent"],
        "error": f"{type(exc).__name__}: {str(exc)[:1000]}",
    }


def haiku_diagnostics(resp):
    """What the adapter did to Haiku's raw map: retries, and the raw sum when it renormalized."""
    debug = getattr(resp, "debug", None) or {}
    if not isinstance(debug, dict):
        debug = dict(debug) if hasattr(debug, "keys") else {}
    original = (debug.get("original_probabilities") or {}).get("intent")
    return {
        "nRetries": int(getattr(resp.usage, "n_retries", 0) or 0),
        "normError": float(debug.get("max_error", 0.0) or 0.0),
        "rawSum": None if original is None else float(sum(original.values())),
    }


def run_jev(rows, label_map, path):
    if not os.environ.get("TYPESAFE_API_KEY"):
        print("unconfigured: TYPESAFE_API_KEY unset, no call made", file=sys.stderr)
        return 2
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
                row = error_row(item, exc)
                failed += 1
            record(path, row)
            if (ok + failed) % 50 == 0:
                print(
                    f"  jev {ok + failed}/{len(todo)} failed={failed}", file=sys.stderr
                )
    print(f"jev done ok={ok} failed={failed}", file=sys.stderr)
    return 3 if failed > fail_limit(rows) else 0


def run_haiku(rows, label_map, path):
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("unconfigured: ANTHROPIC_API_KEY unset, no call made", file=sys.stderr)
        return 2
    from system_one_adapter import AsyncSystemOneAdapterClient

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
                            haiku_diagnostics(resp),
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
                if (ok + failed) % 50 == 0:
                    print(
                        f"  haiku {ok + failed}/{len(todo)} failed={failed}",
                        file=sys.stderr,
                    )
        print(f"haiku done ok={ok} failed={failed}", file=sys.stderr)
        return 3 if failed > fail_limit(rows) else 0

    return asyncio.run(go())


def main(argv):
    argv = list(argv)
    name = "subset"
    if "--set" in argv:
        at = argv.index("--set")
        name = argv[at + 1]
        del argv[at : at + 2]
    out = None
    if "--out" in argv:
        at = argv.index("--out")
        out = os.path.abspath(argv[at + 1])
        del argv[at : at + 2]
    fname, rows_pattern = SETS[name]
    rows = load_rows(fname)
    label_map = labels(rows)
    arms = argv or ["jev", "haiku"]
    if out and len(arms) != 1:
        print("--out needs exactly one arm", file=sys.stderr)
        return 64
    code = 0
    for arm in arms:
        path = out or os.path.join(HERE, rows_pattern.format(arm=arm))
        if arm == "jev":
            code = run_jev(rows, label_map, path) or code
        elif arm == "haiku":
            code = run_haiku(rows, label_map, path) or code
        else:
            print(f"unknown arm {arm!r}", file=sys.stderr)
            return 64
    return code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
