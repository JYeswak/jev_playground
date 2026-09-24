#!/usr/bin/env python3
"""Feasibility run for bead jev-14qk: the committed SST-5 Score question through OpenRouter :free models.

Bar: docs/demos/upstream-repro/openrouter-free-feasibility-20260924.md (committed before any call).
Same question, same rows and same adapter settings as the jev-zui Haiku arm (work/score-sst5/run.py:
structured outputs, probabilities mode, normalized probabilities, RetryPolicy()), with the provider
swapped for OpenRouter (work/openrouter/provider.py). Rows: the first 50 of work/score-sst5/sample.jsonl
(public SST-5 test sentences). Nothing from this repo's sessions is sent.

Run:
  infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
    upstream/typesafe-ai/system-one-adapter-python/.venv/bin/python work/openrouter/run_sst5.py [model ...]
No model argument runs all six in FREE_STRUCTURED, one after another. Appends to
work/openrouter/rows-sst5-<model>.jsonl and skips rows that already hold an answer. Never prints a key.
"""

import asyncio
import importlib.util
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

import provider  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "sst5_run", os.path.join(ROOT, "work/score-sst5/run.py")
)
sst5 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(
    sst5
)  # QUESTION, QNAME and row_from exactly as jev-zui committed them

from system_one_adapter import AsyncSystemOneAdapterClient  # noqa: E402
from typesafe_sdk import RetryPolicy  # noqa: E402

N_ROWS = 50
CONCURRENCY = 2
TIMEOUT_S = (
    180  # whole call, retries included; RetryPolicy's own per-attempt timeout is 30 s
)


def rows_path(model):
    return os.path.join(
        HERE, "rows-sst5-" + model.replace("/", "__").replace(":", "_") + ".jsonl"
    )


def answered(path):
    if not os.path.exists(path):
        return set()
    return {
        r["i"] for r in map(json.loads, filter(str.strip, open(path))) if "score" in r
    }


def trace(debug):
    """What OpenRouter reported on the last attempt: upstream provider, finish reason, attempts."""
    debug = debug or {}
    attempts = debug.get("llm_attempts") or []
    last = attempts[-1] if attempts else {}
    resp = last.get("llm_response") or {}
    return {
        "provider": resp.get("provider"),
        "finishReason": (last.get("debug_info") or {}).get("finish_reason"),
        "attempts": len(attempts),
        "retryReasons": [list(r) for r in debug.get("retry_reasons") or []],
    }


async def run_model(model):
    path = rows_path(model)
    sample = [
        json.loads(line)
        for line in open(os.path.join(ROOT, "work/score-sst5/sample.jsonl"))
        if line.strip()
    ]
    todo = [s for s in sample[:N_ROWS] if s["i"] not in answered(path)]
    print(f"{model}: {len(todo)} to run", file=sys.stderr)
    prov = provider.openrouter_provider(model)
    sem = asyncio.Semaphore(CONCURRENCY)
    ok = failed = 0
    async with AsyncSystemOneAdapterClient(
        structured_outputs=True,
        llm_answer_mode="probabilities",
        normalize_probabilities=True,
        retry=RetryPolicy(),
    ) as client:

        async def one(s):
            async with sem:
                t0 = time.time()
                row = {"i": s["i"], "model": model}
                try:
                    resp = await asyncio.wait_for(
                        client.system_one(
                            s["text"], {sst5.QNAME: sst5.QUESTION}, model=prov
                        ),
                        timeout=TIMEOUT_S,
                    )
                    usage = {
                        "input_tokens": int(resp.usage.input_tokens_total),
                        "output_tokens": int(resp.usage.output_tokens_total),
                    }
                    row.update(sst5.row_from(resp.answers[sst5.QNAME], model, usage))
                    debug = resp.debug or {}
                    row["probabilityError"] = (
                        debug.get("probability_errors") or {}
                    ).get(sst5.QNAME)
                    row["originalProbabilities"] = (
                        debug.get("original_probabilities") or {}
                    ).get(sst5.QNAME)
                    row.update(trace(debug))
                except Exception as e:  # noqa: BLE001 - recorded verbatim, scored as a failure
                    row["error"] = f"{type(e).__name__}: {str(e)[:300]}"
                    row.update(trace(getattr(e, "debug", None)))
                row["latencyMs"] = int((time.time() - t0) * 1000)
                return row

        for coro in asyncio.as_completed([one(s) for s in todo]):
            row = await coro
            with open(path, "a") as f:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
            failed += "error" in row
            ok += "error" not in row
    await prov.aclose()
    print(f"{model}: ok={ok} failed={failed}", file=sys.stderr)


async def main(models):
    for model in models:
        await run_model(model)
    return 0


if __name__ == "__main__":
    if not os.environ.get(provider.KEY_ENV):
        raise SystemExit(f"unconfigured: {provider.KEY_ENV} is not set, no call made")
    chosen = sys.argv[1:] or list(provider.FREE_STRUCTURED)
    unknown = [m for m in chosen if m not in provider.FREE_STRUCTURED]
    if unknown:
        raise SystemExit(f"not in FREE_STRUCTURED: {unknown}")
    sys.exit(asyncio.run(main(chosen)))
