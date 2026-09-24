#!/usr/bin/env python3
"""Grok-only arms for bead jev-iwhh. No Jev call. No OpenRouter call.

  upstream/typesafe-ai/system-one-adapter-python/.venv/bin/python \\
    work/grok-incumbent-3/run.py fever|yelp|b77 run1|run2|run3
"""

import asyncio
import hashlib
import importlib.util
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
from anthropic_stop import refuse_paid_comparator  # noqa: E402  jev-lbgk

GROK_MODEL = "grok-4.20-0309-non-reasoning"
GROK_URL = "https://api.x.ai/v1"
SETS = ("fever", "yelp", "b77")
RUNS = ("run1", "run2", "run3")


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def fever_items():
    mod = load_module("fever_run", os.path.join(ROOT, "work/noul-scifact/run.py"))
    sample = [
        json.loads(line)
        for line in open(
            os.path.join(ROOT, "work/noul-fever/sample.jsonl"), encoding="utf-8"
        )
        if line.strip()
    ]
    return [(row["i"], mod.state(row), {"toxic": mod.QUESTION}) for row in sample]


def yelp_items():
    mod = load_module("yelp_run", os.path.join(ROOT, "work/score-yelp/run.py"))
    sample, texts = mod.load_texts()
    return [(row["i"], texts[row["i"]], {"stars": mod.QUESTION}) for row in sample]


def b77_items():
    mod = load_module("b77_run", os.path.join(ROOT, "work/choice-banking77/run.py"))
    rows = [
        json.loads(line)
        for line in open(
            os.path.join(ROOT, "work/choice-banking77/full.jsonl"), encoding="utf-8"
        )
        if line.strip()
    ]
    label_map = mod.labels(rows)
    q = mod.question(label_map)
    return [(row["i"], mod.state(row), q) for row in rows]


LOADERS = {"fever": fever_items, "yelp": yelp_items, "b77": b77_items}


def out_path(set_name, run):
    return os.path.join(HERE, f"rows-{set_name}-{run}.jsonl")


def answered(path):
    if not os.path.exists(path):
        return set()
    ids = set()
    for line in open(path, encoding="utf-8"):
        if not line.strip():
            continue
        row = json.loads(line)
        if "error" not in row and ("noul" in row or "score" in row or "choice" in row):
            ids.add(row["i"])
    return ids


async def main(set_name, run, concurrency=8, bar_path=None, repo=None):
    # Preregistration is the phase. A dirty or untracked bar panics here,
    # before the provider exists, so no provider is constructed.
    sys.path.insert(0, os.path.join(ROOT, "work/sr-adopt"))
    from phase_gate import call_after_bar

    bar = bar_path or os.path.join(
        ROOT, "docs/demos/upstream-repro/grok-incumbent-fever-yelp-b77-20260924.md"
    )

    call_after_bar(bar, lambda: None, repo=repo or ROOT)
    # The bar gate stays first so work/sr-adopt/test_prereg.py still proves a dirty bar panics
    # through this runner; the refusal follows it, before any adapter import or provider (jev-lbgk).
    refuse_paid_comparator(f"grok-incumbent-3 {set_name} {run} ({GROK_MODEL})")

    from system_one_adapter import AsyncSystemOneAdapterClient
    from system_one_adapter.providers.openai import AsyncOpenAIProvider

    if not os.environ.get("XAI_API_KEY"):
        print("unconfigured: XAI_API_KEY is not set, no call made", file=sys.stderr)
        return 2
    items = LOADERS[set_name]()
    path = out_path(set_name, run)
    have = answered(path)
    todo = [item for item in items if item[0] not in have]
    print(f"{set_name} {run}: {len(todo)} to run, {len(have)} resumed", file=sys.stderr)
    provider = AsyncOpenAIProvider(
        GROK_MODEL, base_url=GROK_URL, api_key=os.environ["XAI_API_KEY"]
    )
    client = AsyncSystemOneAdapterClient(
        structured_outputs=True,
        llm_answer_mode="probabilities",
        normalize_probabilities=True,
    )
    sem = asyncio.Semaphore(concurrency)
    ok = failed = 0

    async with client:

        async def one(item):
            i, state, questions = item
            async with sem:
                t0 = time.perf_counter()
                row = {"i": i, "set": set_name, "run": run}
                try:
                    resp = await asyncio.wait_for(
                        client.system_one(state, questions, model=provider), timeout=90
                    )
                    name = next(iter(questions))
                    ans = resp.answers[name]
                    debug = resp.debug or {}
                    row.update(
                        {
                            "model": f"xai/{GROK_MODEL}",
                            "usage": {
                                "input_tokens": int(resp.usage.input_tokens_total),
                                "output_tokens": int(resp.usage.output_tokens_total),
                            },
                            "probabilityError": (
                                debug.get("probability_errors") or {}
                            ).get(name),
                            "originalProbabilities": (
                                debug.get("original_probabilities") or {}
                            ).get(name),
                        }
                    )
                    if hasattr(ans, "noul"):
                        row["noul"] = float(ans.noul)
                    elif hasattr(ans, "score"):
                        row["score"] = float(ans.score)
                        row["probabilities"] = {
                            str(k): float(v) for k, v in ans.probabilities.items()
                        }
                    else:
                        row["choice"] = ans.choice
                        row["probabilities"] = {
                            str(k): float(v) for k, v in ans.probabilities.items()
                        }
                except Exception as exc:  # noqa: BLE001 - recorded, scored as a refusal
                    row["error"] = f"{type(exc).__name__}: {str(exc)[:200]}"
                row["latencyMs"] = int((time.perf_counter() - t0) * 1000)
                return row

        with open(path, "a", encoding="utf-8") as fh:
            for coro in asyncio.as_completed([one(item) for item in todo]):
                row = await coro
                # never write the state text
                fh.write(
                    json.dumps(
                        {k: v for k, v in row.items() if k != "state"},
                        ensure_ascii=False,
                    )
                    + "\n"
                )
                fh.flush()
                if "error" in row:
                    failed += 1
                else:
                    ok += 1
                if (ok + failed) % 100 == 0:
                    print(
                        f"  {ok + failed}/{len(todo)} ok={ok} failed={failed}",
                        file=sys.stderr,
                    )
    await provider.aclose()
    print(f"{set_name} {run} done: ok={ok} failed={failed}", file=sys.stderr)
    return 3 if failed else 0


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in SETS or sys.argv[2] not in RUNS:
        raise SystemExit(f"usage: run.py {'|'.join(SETS)} {'|'.join(RUNS)}")
    raise SystemExit(asyncio.run(main(sys.argv[1], sys.argv[2])))
