#!/usr/bin/env python3
"""Comparator arms for bead jev-3e2i: more incumbent families, through OpenRouter, on the five sets
whose Jev wins survived their checks. Bar: docs/demos/upstream-repro/openrouter-incumbents-20260924.md
(committed before any call).

Provider: system-one-adapter's own AsyncOpenAIProvider(base_url=https://openrouter.ai/api/v1,
api="chat_completions"), passed as the caller-owned `model=` (no adapter code edited), built by
work/openrouter/provider.py (jev-14qk's helper). Free models only: any id without ':free' refuses
before a client exists (work/anthropic-stop, jev-lbgk; AGENTS.md 'No paid comparisons'). The key is
OPENROUTER_API_KEY from the lane Infisical project; only its length is ever checked.

Inputs are the exact questions, states and rows of each unit, read with `git show` at the commits the
unit's incumbent arm used (work/second-incumbent/run.py PINS, plus FEVER here):
  sst5 500, banking77 400, clinc150 750, scifact 400, fever 400. Only public benchmark rows are sent.

Adapter settings copy the Haiku and grok arms: structured outputs, llm_answer_mode="probabilities",
normalize_probabilities=True, RetryPolicy(). --prompted switches that cell to the declared fallback
(structured_outputs=False, n_retry_malformed_structure=1) and writes a separate -prompted file.
--limit N runs only the first N rows still to do (the 16-row structured probe).

Pacing (Amendment 2): free models run exactly as jev-3e2i's paced run 2 (run_sst5.py --paced): one in
flight, at most 15 request starts per 60 s at the provider seam, 120 s per attempt, runner-owned 429
waits, a quota stop, a 5-row streak stop and a per-session --max-requests cap.

Run (live):
  infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
    upstream/typesafe-ai/system-one-adapter-python/.venv/bin/python \
    work/openrouter-incumbents/run.py <model id> <dataset> [--prompted] [--limit N] [--max-requests N] [--resume]
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
sys.path.insert(0, os.path.join(ROOT, "work", "anthropic-stop"))

from anthropic_stop import require_free_comparator  # noqa: E402  jev-lbgk


def _load(name, relpath):
    spec = importlib.util.spec_from_file_location(name, os.path.join(WORK, relpath))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SI = _load("second_incumbent_run", "second-incumbent/run.py")
OR = _load("openrouter_provider", "openrouter/provider.py")
# Run 2's paced settings and helpers, imported so the free arm runs exactly as run 2 did (Amendment 2).
RS = _load("openrouter_run_sst5", "openrouter/run_sst5.py")

DATASETS = ("sst5", "banking77", "clinc150", "scifact", "fever", "stsb")
FEVER_PIN = {
    "runner": ("834a569", "work/noul-scifact/run.py"),
    "sample": ("834a569", "work/noul-fever/sample.jsonl"),
}
# STS-B (jev-jzzs, amendment): runner as of its bar; sentences are fetched at run time from the
# sha256-pinned public CSV and never written to a row (their licenses do not allow committing them).
STSB_PIN = ("8e4bda9", "work/score-stsb/run.py")
STSB_INSTRUCTIONS = "How similar in meaning are these two sentences?"
MAX_REQUESTS_CEILING = 599


def _score_tuple(name):
    """A module-level tuple from score.py (QUOTA), read without importing its scorers."""
    import ast

    with open(os.path.join(HERE, "score.py"), encoding="utf-8") as fh:
        for node in ast.parse(fh.read()).body:
            if (
                isinstance(node, ast.Assign)
                and getattr(node.targets[0], "id", "") == name
            ):
                return tuple(ast.literal_eval(node.value))
    raise SystemExit(f"{name} not found in score.py")


QUOTA = _score_tuple("QUOTA")


def is_quota(message):
    """A daily-cap refusal, by score.py's own markers: such a row is a quota row, not a failure."""
    return any(t in message for t in QUOTA)


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
    """A :free id through jev-14qk's helper; any other id refuses before a client exists."""
    require_free_comparator(model, "openrouter-incumbents")
    return OR.openrouter_provider(model)


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


def free_todo(sample, path, resume):
    """Main pass: rows with no record, or whose last record is a quota row. Resume pass: rows whose
    only record is one non-quota failure (the bar's single resume)."""
    records = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    r = json.loads(line)
                    records.setdefault(r["i"], []).append(r)

    def answered_row(r):
        return "noul" in r or "choice" in r or "score" in r

    out = []
    for s in sample:
        rs = records.get(s["i"], [])
        if any(answered_row(r) for r in rs):
            continue
        failures = [r for r in rs if not is_quota(r.get("error", ""))]
        last_quota = bool(rs) and is_quota(rs[-1].get("error", ""))
        if resume:
            if len(failures) == 1 and not last_quota:
                out.append(s)
        elif not rs or (last_quota and not failures):
            out.append(s)
    return out


async def run_free(model, dataset, prompted, limit, max_requests, resume):
    """One paced session for a :free model, exactly run 2's paced mode (Amendment 2)."""
    from system_one_adapter import AsyncSystemOneAdapterClient
    from typesafe_sdk import TypeSafeRateLimitError

    require_free_comparator(model, "openrouter-incumbents run_free")
    sample, questions, state, to_row = setup(dataset)
    path = out_path(dataset, model, prompted)
    todo = free_todo(sample, path, resume)[:limit]
    mode = "prompted" if prompted else "structured"
    pacer = OR.Pacer(RS.PACED_PER_MIN, max_requests)
    prov = OR.PacedProvider(OR.openrouter_provider(model), pacer, RS.PACED_ATTEMPT_S)
    extra = {"n_retry_malformed_structure": 1} if prompted else {}
    print(
        f"{model} {dataset} {mode} paced: {len(todo)} to run{' (resume pass)' if resume else ''}, cap {max_requests} requests",
        file=sys.stderr,
    )
    ok = failed = 0
    streak_class, streak, stop = None, 0, None
    async with AsyncSystemOneAdapterClient(
        structured_outputs=not prompted,
        llm_answer_mode="probabilities",
        normalize_probabilities=True,
        retry=RS.PACED_RETRY,
        **extra,
    ) as client:
        for item in todo:
            row = {"i": item["i"], "model": model, "mode": mode}
            req0, waits, wait_s = pacer.requests, 0, 0.0
            while True:
                t0, w0 = time.perf_counter(), pacer.waited_s()
                try:
                    resp = await RS.bounded(
                        client.system_one(state(item), questions, model=prov),
                        RS.PACED_CALL_S,
                        pacer,
                    )
                except OR.RequestCapReached:
                    stop = (
                        f"request cap {max_requests} reached; row {item['i']} not sent"
                    )
                    break
                except TypeSafeRateLimitError as e:
                    message = f"{type(e).__name__}: {str(e)[:500]}"
                    if not is_quota(message) and waits < RS.PACED_429_WAITS:
                        delay = (
                            e.retry_after_ms / 1000
                            if e.retry_after_ms is not None
                            else RS.PACED_429_DEFAULT_S
                        )
                        waits, wait_s = waits + 1, wait_s + delay
                        await asyncio.sleep(delay)
                        continue
                    row["error"] = message
                    if is_quota(message):
                        stop = f"daily quota at row {item['i']}"
                except Exception as exc:  # noqa: BLE001 - recorded, scored by the bar's rules
                    row["error"] = f"{type(exc).__name__}: {str(exc)[:500]}"
                else:
                    row.update(to_row(item, resp))
                    row.update(SI.attempt_facts(resp))
                    # The upstream provider OpenRouter reports (the bar's row field), read the way
                    # run 2's rows read it; attempt_facts' `provider` is the adapter's label.
                    row["upstream"] = RS.trace(resp.debug).get("provider")
                    row["usage"] = {
                        "input_tokens": resp.usage.input_tokens_total,
                        "output_tokens": resp.usage.output_tokens_total,
                    }
                    row["nRetries"] = resp.usage.n_retries
                    row["nRetriesMalformed"] = resp.usage.n_retries_malformed_structure
                pacer_ms = int((pacer.waited_s() - w0) * 1000)
                row["latencyMs"] = int((time.perf_counter() - t0) * 1000) - pacer_ms
                break
            if stop and "error" not in row:
                break  # the request cap: nothing was sent for this row, so nothing is written
            row.update(
                rateLimitWaits=waits,
                waitMs=int(wait_s * 1000),
                pacerWaitMs=pacer_ms,
                requests=pacer.requests - req0,
            )
            with open(path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            if "error" in row:
                failed += 1
                cls = RS.error_class(row["error"])
                streak = streak + 1 if cls == streak_class else 1
                streak_class = cls
            else:
                ok += 1
                streak_class, streak = None, 0
            if (ok + failed) % 25 == 0:
                print(
                    f"  {ok + failed}/{len(todo)} ok={ok} failed={failed} requests={pacer.requests}",
                    file=sys.stderr,
                )
            if stop:
                break
            if streak >= RS.PACED_STOP_AFTER:
                stop = f"{streak} consecutive failures of: {streak_class}"
                break
    await prov.aclose()
    print(
        f"{model} {dataset} {mode} paced done: ok={ok} failed={failed} requests={pacer.requests}"
        + (f"; STOPPED: {stop}" if stop else ""),
        file=sys.stderr,
    )
    return 3 if failed or stop else 0


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
    max_requests = take(argv, "--max-requests", True)
    resume = take(argv, "--resume", False)
    if len(argv) != 2 or argv[1] not in DATASETS:
        raise SystemExit(
            "usage: run.py <model id> <"
            + "|".join(DATASETS)
            + "> [--prompted] [--limit N] [--max-requests N] [--resume]"
        )
    model, dataset = argv
    try:
        provider_for(model)  # refuses a paid id or a missing key before any work
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    limit = int(limit) if limit else None
    if not max_requests or not 0 < int(max_requests) <= MAX_REQUESTS_CEILING:
        print(
            f"refused: a :free session needs --max-requests between 1 and {MAX_REQUESTS_CEILING} (Amendment 2: remaining - 20)",
            file=sys.stderr,
        )
        return 2
    return asyncio.run(
        run_free(model, dataset, prompted, limit, int(max_requests), resume)
    )


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
