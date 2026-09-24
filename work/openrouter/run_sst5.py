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

--paced (bead jev-3e2i, run 2; bar and every change preregistered in
docs/demos/upstream-repro/openrouter-free-feasibility-2-20260924.md): runs FREE_STRUCTURED_RUN2 in
order, concurrency 1, at most 15 request starts per 60 s across the whole run, 120 s per attempt, 429
handled here (wait retry-after-ms / Retry-After, else 60 s; at most 3 waits per row), at most 599
requests in total, and a model stops after 5 consecutive failed rows of one class. Writes
work/openrouter/rows-sst5-<model>-run2.jsonl and skips any row already recorded there (one pass).
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
sys.path.insert(0, os.path.join(ROOT, "work", "anthropic-stop"))

import provider  # noqa: E402
from anthropic_stop import require_free_comparator  # noqa: E402  jev-lbgk

_spec = importlib.util.spec_from_file_location(
    "sst5_run", os.path.join(ROOT, "work/score-sst5/run.py")
)
sst5 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(
    sst5
)  # QUESTION, QNAME and row_from exactly as jev-zui committed them

from system_one_adapter import AsyncSystemOneAdapterClient  # noqa: E402
from typesafe_sdk import RetryPolicy, TypeSafeRateLimitError  # noqa: E402

N_ROWS = 50
CONCURRENCY = 2
TIMEOUT_S = (
    180  # whole call, retries included; RetryPolicy's own per-attempt timeout is 30 s
)

# --paced settings, as preregistered.
PACED_PER_MIN = 15
PACED_MAX_REQUESTS = 599
PACED_ATTEMPT_S = 120.0
PACED_CALL_S = 420.0  # whole call, adapter retries included, pacer holds excluded
PACED_429_WAITS = 3
PACED_429_DEFAULT_S = 60.0
PACED_STOP_AFTER = 5  # consecutive failed rows of one class
# RetryPolicy() with 429 removed from the retried statuses; the runner owns 429.
PACED_RETRY = RetryPolicy(http_statuses={408, *range(500, 600)})


def rows_path(model, suffix=""):
    return os.path.join(
        HERE,
        "rows-sst5-" + model.replace("/", "__").replace(":", "_") + suffix + ".jsonl",
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


def error_class(msg):
    """Same head as score_feasibility.error_class: the class plus status and message head."""
    return msg.split(" | ")[0][:160]


async def bounded(coro, limit_s, pacer):
    """Await `coro`, failing with TimeoutError once it has run `limit_s` seconds not counting the
    time the pacer held its requests back."""
    task = asyncio.ensure_future(coro)
    t0, w0 = time.monotonic(), pacer.waited_s()
    while True:
        left = limit_s - ((time.monotonic() - t0) - (pacer.waited_s() - w0))
        if left <= 0:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            raise asyncio.TimeoutError(f"whole call over {limit_s:.0f} s")
        done, _ = await asyncio.wait({task}, timeout=left)
        if done:
            return task.result()


async def run_model_paced(model, pacer):
    """One paced pass over the first N_ROWS rows. Returns False when the request cap stopped it."""
    require_free_comparator(model, "openrouter run_sst5 paced")
    path = rows_path(model, "-run2")
    sample = [
        json.loads(line)
        for line in open(os.path.join(ROOT, "work/score-sst5/sample.jsonl"))
        if line.strip()
    ]
    seen = set()
    if os.path.exists(path):
        seen = {json.loads(line)["i"] for line in open(path) if line.strip()}
    todo = [s for s in sample[:N_ROWS] if s["i"] not in seen]
    print(f"{model}: {len(todo)} to run (paced)", file=sys.stderr)
    prov = provider.PacedProvider(
        provider.openrouter_provider(model), pacer, PACED_ATTEMPT_S
    )
    ok = failed = 0
    streak_class, streak = None, 0
    capped = False
    async with AsyncSystemOneAdapterClient(
        structured_outputs=True,
        llm_answer_mode="probabilities",
        normalize_probabilities=True,
        retry=PACED_RETRY,
    ) as client:
        for s in todo:
            row = {"i": s["i"], "model": model}
            req0, waits, wait_s = pacer.requests, 0, 0.0
            while True:
                t0, w0 = time.time(), pacer.waited_s()
                try:
                    resp = await bounded(
                        client.system_one(
                            s["text"], {sst5.QNAME: sst5.QUESTION}, model=prov
                        ),
                        PACED_CALL_S,
                        pacer,
                    )
                except TypeSafeRateLimitError as e:
                    if waits < PACED_429_WAITS:
                        delay = (
                            e.retry_after_ms / 1000
                            if e.retry_after_ms is not None
                            else PACED_429_DEFAULT_S
                        )
                        waits += 1
                        wait_s += delay
                        await asyncio.sleep(delay)
                        continue
                    row["error"] = f"{type(e).__name__}: {str(e)[:300]}"
                    row.update(trace(getattr(e, "debug", None)))
                except provider.RequestCapReached as e:
                    row["error"] = f"{type(e).__name__}: {e}"
                    capped = True
                except Exception as e:  # noqa: BLE001 - recorded verbatim, scored as a failure
                    row["error"] = f"{type(e).__name__}: {str(e)[:300]}"
                    row.update(trace(getattr(e, "debug", None)))
                else:
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
                pacer_ms = int((pacer.waited_s() - w0) * 1000)
                row["latencyMs"] = int((time.time() - t0) * 1000) - pacer_ms
                break
            row["rateLimitWaits"] = waits
            row["waitMs"] = int(wait_s * 1000)
            row["pacerWaitMs"] = pacer_ms
            row["requests"] = pacer.requests - req0
            with open(path, "a") as f:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
            if "error" in row:
                failed += 1
                cls = error_class(row["error"])
                streak = streak + 1 if cls == streak_class else 1
                streak_class = cls
            else:
                ok += 1
                streak_class, streak = None, 0
            print(
                f"{model}: row {s['i']} {'ok' if 'error' not in row else 'FAIL ' + row['error'][:90]}"
                f" requests={pacer.requests}",
                file=sys.stderr,
            )
            if capped:
                break
            if streak >= PACED_STOP_AFTER:
                print(
                    f"{model}: STOPPED after {streak} consecutive failures of: {streak_class}",
                    file=sys.stderr,
                )
                break
    await prov.aclose()
    print(
        f"{model}: ok={ok} failed={failed} requests_total={pacer.requests}",
        file=sys.stderr,
    )
    return not capped


async def main_paced(models):
    pacer = provider.Pacer(PACED_PER_MIN, PACED_MAX_REQUESTS)
    for model in models:
        if not await run_model_paced(model, pacer):
            print("request cap reached: remaining models not run", file=sys.stderr)
            break
    print(f"paced run done: {pacer.requests} requests", file=sys.stderr)
    return 0


async def main(models):
    for model in models:
        await run_model(model)
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    paced = "--paced" in args
    args = [a for a in args if a != "--paced"]
    allowed = provider.FREE_STRUCTURED_RUN2 if paced else provider.FREE_STRUCTURED
    chosen = args or list(allowed)
    unknown = [m for m in chosen if m not in allowed]
    if unknown:
        raise SystemExit(f"not in the allowed list: {unknown}")
    for m in chosen:
        require_free_comparator(m, "openrouter run_sst5")
    if not os.environ.get(provider.KEY_ENV):
        raise SystemExit(f"unconfigured: {provider.KEY_ENV} is not set, no call made")
    sys.exit(asyncio.run(main_paced(chosen) if paced else main(chosen)))
