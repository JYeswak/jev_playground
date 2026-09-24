#!/usr/bin/env python3
"""Comparator arms for bead jev-3e2i: more incumbent families, through OpenRouter, on the five sets
whose Jev wins survived their checks. Bar: docs/demos/upstream-repro/openrouter-incumbents-20260924.md
(committed before any call).

Provider: system-one-adapter's own AsyncOpenAIProvider(base_url=https://openrouter.ai/api/v1,
api="chat_completions"), passed as the caller-owned `model=` (no adapter code edited). Free models go
through work/openrouter/provider.py (jev-14qk's helper, which refuses any id without ':free'); the two
cheap paid models are built here and refused unless the id is in PAID. The key is OPENROUTER_API_KEY
from the lane Infisical project; only its length is ever checked.

Inputs are the exact questions, states and rows of each unit, read with `git show` at the commits the
unit's incumbent arm used (work/second-incumbent/run.py PINS, plus FEVER here):
  sst5 500, banking77 400, clinc150 750, scifact 400, fever 400. Only public benchmark rows are sent.

Adapter settings copy the Haiku and grok arms: structured outputs, llm_answer_mode="probabilities",
normalize_probabilities=True, RetryPolicy(). --prompted switches that cell to the declared fallback
(structured_outputs=False, n_retry_malformed_structure=1) and writes a separate -prompted file.
--limit N runs only the first N rows still to do (the 16-row structured probe).

Pacing: free models share OpenRouter's account-wide caps (20 requests/minute, 1,000/day), so free calls
start at most FREE_RPM per minute, 2 in flight; paid models run 8 in flight.

Run (live):
  infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
    upstream/typesafe-ai/system-one-adapter-python/.venv/bin/python \
    work/openrouter-incumbents/run.py <model id> <sst5|banking77|clinc150|scifact|fever> [--prompted] [--limit N]
Rows: work/openrouter-incumbents/rows-<dataset>-<slug>[-prompted].jsonl. Resumes rows with an answer.
"""

import asyncio
import importlib.util
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(HERE)
ROOT = os.path.dirname(WORK)
sys.path.insert(0, os.path.join(ROOT, "upstream/typesafe-ai/typesafe-sdk-python/src"))
sys.path.insert(
    0, os.path.join(ROOT, "upstream/typesafe-ai/system-one-adapter-python/src")
)


def _load(name, relpath):
    spec = importlib.util.spec_from_file_location(name, os.path.join(WORK, relpath))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SI = _load("second_incumbent_run", "second-incumbent/run.py")
OR = _load("openrouter_provider", "openrouter/provider.py")

BASE_URL = "https://openrouter.ai/api/v1"
PAID = ("openai/gpt-5-nano", "deepseek/deepseek-v4-flash")
DATASETS = ("sst5", "banking77", "clinc150", "scifact", "fever", "stsb")
FEVER_PIN = {
    "runner": ("834a569", "work/noul-scifact/run.py"),
    "sample": ("834a569", "work/noul-fever/sample.jsonl"),
}
# STS-B (jev-jzzs, amendment): runner as of its bar; sentences are fetched at run time from the
# sha256-pinned public CSV and never written to a row (their licenses do not allow committing them).
STSB_PIN = ("8e4bda9", "work/score-stsb/run.py")
STSB_INSTRUCTIONS = "How similar in meaning are these two sentences?"
FREE_RPM = 15
FREE_INFLIGHT = 2
PAID_INFLIGHT = 8
TIMEOUT_FREE_S = 180
TIMEOUT_PAID_S = 90


def slug(model):
    return model.replace("/", "__").replace(":", "_")


def out_path(dataset, model, prompted=False):
    return os.path.join(
        HERE, f"rows-{dataset}-{slug(model)}{'-prompted' if prompted else ''}.jsonl"
    )


def answered(path):
    ids = set()
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                r = json.loads(line) if line.strip() else {}
                if "noul" in r or "choice" in r or "score" in r:
                    ids.add(r["i"])
    return ids


def provider_for(model):
    """Free ids through jev-14qk's guarded helper; paid ids only from PAID."""
    if model.endswith(":free"):
        return OR.openrouter_provider(model)
    if model not in PAID:
        raise ValueError(f"not an approved paid model: {model!r} (allowed: {PAID})")
    from system_one_adapter.providers.openai import AsyncOpenAIProvider

    key = os.environ.get(OR.KEY_ENV)
    if not key:
        raise RuntimeError(f"unconfigured: {OR.KEY_ENV} is not set, no call made")
    return AsyncOpenAIProvider(
        model, base_url=BASE_URL, api_key=key, api="chat_completions"
    )


def setup_stsb():
    """jev-jzzs's question and state, rebuilt from its pinned runner (the instructions literal sits
    inside that runner's main(); test_run.py checks it is the pinned source's string)."""
    from typesafe_sdk import Score

    runner = SI.pinned_module("stsb_runner", *STSB_PIN)
    pairs = runner.fetch_pairs()  # refuses a sha256 or row-count mismatch
    sample = [{"i": i, "s1": s1, "s2": s2} for i, (s1, s2, _) in enumerate(pairs)]
    qname = runner.QNAME
    question = Score(instructions=STSB_INSTRUCTIONS, criteria=runner.QUESTION_CRITERIA)

    def state(item):
        return {"sentence1": item["s1"], "sentence2": item["s2"]}

    def to_row(item, resp):
        ans = resp.answers[qname]
        debug = resp.debug or {}
        return {
            "score": float(ans.score),
            "confidence": float(ans.confidence) if ans.confidence is not None else None,
            "probabilities": {
                str(int(k)): float(v) for k, v in ans.probabilities.items()
            },
            "probabilityError": (debug.get("probability_errors") or {}).get(qname),
            "originalProbabilities": (debug.get("original_probabilities") or {}).get(
                qname
            ),
        }

    return sample, {qname: question}, state, to_row


def setup(dataset):
    """(rows, questions, state fn, answer->row fn), byte-identical to each unit's incumbent arm.
    Noul rows also keep the adapter's debug so zero-mass answers can be dropped in scoring."""
    if dataset in ("sst5", "banking77", "clinc150"):
        return SI.setup(dataset)
    if dataset == "stsb":
        return setup_stsb()
    pin = SI.PINS["scifact"] if dataset == "scifact" else FEVER_PIN
    runner = SI.pinned_module(f"{dataset}_runner", *pin["runner"])
    sample = SI.pinned_rows(*pin["sample"])
    qname = runner.QNAME

    def to_row(item, resp):
        debug = resp.debug or {}
        return {
            "noul": float(resp.answers[qname].noul),
            "probabilityError": (debug.get("probability_errors") or {}).get(qname),
            "originalProbabilities": (debug.get("original_probabilities") or {}).get(
                qname
            ),
        }

    return sample, {qname: runner.QUESTION}, runner.state, to_row


async def run(model, dataset, prompted, limit):
    from system_one_adapter import AsyncSystemOneAdapterClient
    from typesafe_sdk import RetryPolicy

    free = model.endswith(":free")
    provider = provider_for(model)
    sample, questions, state, to_row = setup(dataset)
    path = out_path(dataset, model, prompted)
    have = answered(path)
    todo = [s for s in sample if s["i"] not in have][:limit]
    mode = "prompted" if prompted else "structured"
    print(
        f"{model} {dataset} {mode}: {len(todo)} to run, {len(have)} resumed",
        file=sys.stderr,
    )
    sem = asyncio.Semaphore(FREE_INFLIGHT if free else PAID_INFLIGHT)
    pace = asyncio.Lock()
    last_start = [0.0]
    timeout = TIMEOUT_FREE_S if free else TIMEOUT_PAID_S
    extra = {"n_retry_malformed_structure": 1} if prompted else {}
    ok = failed = 0
    async with AsyncSystemOneAdapterClient(
        structured_outputs=not prompted,
        llm_answer_mode="probabilities",
        normalize_probabilities=True,
        retry=RetryPolicy(),
        **extra,
    ) as client:

        async def one(item):
            async with sem:
                if free:
                    async with pace:
                        wait = last_start[0] + 60.0 / FREE_RPM - time.monotonic()
                        if wait > 0:
                            await asyncio.sleep(wait)
                        last_start[0] = time.monotonic()
                t0 = time.perf_counter()
                row = {"i": item["i"], "model": model, "mode": mode}
                try:
                    resp = await asyncio.wait_for(
                        client.system_one(state(item), questions, model=provider),
                        timeout=timeout,
                    )
                    row.update(to_row(item, resp))
                    row.update(SI.attempt_facts(resp))
                    row["usage"] = {
                        "input_tokens": resp.usage.input_tokens_total,
                        "output_tokens": resp.usage.output_tokens_total,
                    }
                    row["nRetries"] = resp.usage.n_retries
                    row["nRetriesMalformed"] = resp.usage.n_retries_malformed_structure
                except Exception as exc:  # noqa: BLE001 - recorded, scored by the bar's rules
                    row["error"] = f"{type(exc).__name__}: {str(exc)[:500]}"
                row["latencyMs"] = int((time.perf_counter() - t0) * 1000)
                return row

        with open(path, "a", encoding="utf-8") as fh:
            for coro in asyncio.as_completed([one(s) for s in todo]):
                row = await coro
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
                fh.flush()
                failed += "error" in row
                ok += "error" not in row
                if (ok + failed) % 50 == 0:
                    print(
                        f"  {ok + failed}/{len(todo)} ok={ok} failed={failed}",
                        file=sys.stderr,
                    )
    await provider.aclose()
    print(f"{model} {dataset} {mode} done: ok={ok} failed={failed}", file=sys.stderr)
    return 3 if failed else 0


def take(argv, flag, has_value):
    if flag not in argv:
        return None if has_value else False
    at = argv.index(flag)
    value = argv[at + 1] if has_value else True
    del argv[at : at + (2 if has_value else 1)]
    return value


def main(argv):
    argv = list(argv)
    prompted = take(argv, "--prompted", False)
    limit = take(argv, "--limit", True)
    if len(argv) != 2 or argv[1] not in DATASETS:
        raise SystemExit(
            "usage: run.py <model id> <"
            + "|".join(DATASETS)
            + "> [--prompted] [--limit N]"
        )
    model, dataset = argv
    try:
        provider_for(model)  # refuses an unapproved id or a missing key before any work
    except (ValueError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return asyncio.run(run(model, dataset, prompted, int(limit) if limit else None))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
