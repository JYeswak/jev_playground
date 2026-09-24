#!/usr/bin/env python3
"""Bead jev-dsu: the incumbent arm of SciFact (jev-9er) and Banking77 10-intent (jev-k3k), re-run
through system-one-adapter-python with a non-Anthropic model. Bar:
docs/demos/upstream-repro/second-incumbent-20260924.md (committed before any call).

Model: xAI `grok-4.20-0309-non-reasoning` behind the adapter's own caller-owned
`AsyncOpenAIProvider(base_url="https://api.x.ai/v1")`, which selects the Chat Completions API for
a non-OpenAI host. Adapter settings copy the Haiku arms exactly: structured outputs,
llm_answer_mode="probabilities", normalize_probabilities=True, RetryPolicy().

Inputs are read with `git show` from the commits the Haiku arms used, so they are byte-identical:
  scifact    work/noul-scifact/run.py @ 30eb285 (QUESTION, state), sample.jsonl @ 83a7295
  banking77  work/choice-banking77/run.py @ 3709ee6 (question, labels, state), subset.jsonl @ 3709ee6
  sst5       work/score-sst5/run.py @ ae161b6 (QUESTION; state = the sentence), sample.jsonl @ ae161b6
             (bead jev-n4j)
  clinc150   work/choice-clinc150/run.py @ e0950ce (labels, question, state), subset.jsonl @ e0950ce
             (bead jev-n4j)

Run (live, needs XAI_API_KEY; never prints it):
  infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
    upstream/typesafe-ai/system-one-adapter-python/.venv/bin/python \
    work/second-incumbent/run.py {smoke|scifact|banking77|sst5|clinc150}
Resumes rows that already have an answer. Score with work/second-incumbent/score.py (keyless).
"""

import asyncio
import json
import os
import subprocess
import sys
import time
import types

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
MODEL = "grok-4.20-0309-non-reasoning"
BASE_URL = "https://api.x.ai/v1"
CONCURRENCY = 8
TIMEOUT_S = 90
PINS = {
    "scifact": {
        "runner": ("30eb285", "work/noul-scifact/run.py"),
        "sample": ("83a7295", "work/noul-scifact/sample.jsonl"),
    },
    "banking77": {
        "runner": ("3709ee6", "work/choice-banking77/run.py"),
        "sample": ("3709ee6", "work/choice-banking77/subset.jsonl"),
    },
    "sst5": {
        "runner": ("ae161b6", "work/score-sst5/run.py"),
        "sample": ("ae161b6", "work/score-sst5/sample.jsonl"),
    },
    "clinc150": {
        "runner": ("e0950ce", "work/choice-clinc150/run.py"),
        "sample": ("e0950ce", "work/choice-clinc150/subset.jsonl"),
    },
}


def git_show(sha, relpath):
    return subprocess.check_output(
        ["git", "-C", ROOT, "show", f"{sha}:{relpath}"], text=True
    )


def pinned_module(name, sha, relpath):
    module = types.ModuleType(name)
    module.__file__ = os.path.join(ROOT, relpath)
    exec(compile(git_show(sha, relpath), module.__file__, "exec"), module.__dict__)  # noqa: S102
    return module


def pinned_rows(sha, relpath):
    return [
        json.loads(line) for line in git_show(sha, relpath).splitlines() if line.strip()
    ]


def out_path(dataset):
    return os.path.join(HERE, f"rows-{dataset}-grok.jsonl")


def answered(dataset):
    ids = set()
    if os.path.exists(out_path(dataset)):
        with open(out_path(dataset), encoding="utf-8") as fh:
            for line in fh:
                r = json.loads(line) if line.strip() else {}
                if "noul" in r or "choice" in r or "score" in r:
                    ids.add(r["i"])
    return ids


def attempt_facts(resp):
    """What the provider actually returned on the final attempt, from the adapter's own debug."""
    attempts = resp.debug.get("llm_attempts") or []
    last = attempts[-1] if attempts else {}
    raw = last.get("llm_response") or {}
    choice0 = (raw.get("choices") or [{}])[0]
    return {
        "provider": (last.get("debug_info") or {}).get("provider"),
        "api": (last.get("debug_info") or {}).get("api"),
        "finishReason": (last.get("debug_info") or {}).get("finish_reason"),
        "modelReported": raw.get("model"),
        "rawText": (choice0.get("message") or {}).get("content"),
        "nAttempts": len(attempts),
    }


def setup(dataset):
    """Return (sample rows, question dict, state fn, answer->row fn)."""
    pin = PINS[dataset]
    runner = pinned_module(f"{dataset}_runner", *pin["runner"])
    sample = pinned_rows(*pin["sample"])
    if dataset == "scifact":
        qname = runner.QNAME
        questions = {qname: runner.QUESTION}

        def to_row(item, resp):
            return {"noul": float(resp.answers[qname].noul)}

        return sample, questions, runner.state, to_row

    if dataset == "sst5":
        qname = runner.QNAME
        questions = {qname: runner.QUESTION}

        def to_row(item, resp):
            ans = resp.answers[qname]
            debug = resp.debug or {}
            probs = {str(int(k)): float(v) for k, v in ans.probabilities.items()}
            return {
                "score": float(ans.score),
                "confidence": float(ans.confidence),
                "probabilities": dict(sorted(probs.items(), key=lambda kv: int(kv[0]))),
                "probabilityError": (debug.get("probability_errors") or {}).get(qname),
                "originalProbabilities": (
                    debug.get("original_probabilities") or {}
                ).get(qname),
            }

        return sample, questions, (lambda item: item["text"]), to_row

    label_map = runner.labels(sample)
    questions = runner.question(label_map)

    def to_row(item, resp):
        ans = resp.answers["intent"]
        errors = resp.debug.get("probability_errors") or {}
        originals = (resp.debug.get("original_probabilities") or {}).get("intent")
        returned = {label_map.get(k, k): float(v) for k, v in ans.probabilities.items()}
        return {
            "intent": item["intent"],
            "choice": label_map.get(ans.choice, ans.choice),
            "confidence": float(ans.confidence),
            "probabilities": returned,
            "probabilityError": float(errors.get("intent", 0.0)),
            "rawSum": sum(originals.values())
            if originals is not None
            else sum(returned.values()),
        }

    return sample, questions, runner.state, to_row


async def run(dataset):
    from system_one_adapter import AsyncSystemOneAdapterClient
    from system_one_adapter.providers.openai import AsyncOpenAIProvider
    from typesafe_sdk import RetryPolicy

    sample, questions, state, to_row = setup(dataset)
    have = answered(dataset)
    todo = [s for s in sample if s["i"] not in have]
    print(f"{dataset}: {len(todo)} to run, {len(have)} resumed", file=sys.stderr)
    provider = AsyncOpenAIProvider(
        MODEL, base_url=BASE_URL, api_key=os.environ["XAI_API_KEY"]
    )
    sem = asyncio.Semaphore(CONCURRENCY)
    ok = failed = 0
    async with AsyncSystemOneAdapterClient(
        structured_outputs=True,
        llm_answer_mode="probabilities",
        normalize_probabilities=True,
        retry=RetryPolicy(),
    ) as client:

        async def one(item):
            async with sem:
                t0 = time.perf_counter()
                row = {"i": item["i"], "arm": "grok", "model": f"xai/{MODEL}"}
                try:
                    resp = await asyncio.wait_for(
                        client.system_one(state(item), questions, model=provider),
                        timeout=TIMEOUT_S,
                    )
                    row.update(to_row(item, resp))
                    row.update(attempt_facts(resp))
                    row["usage"] = {
                        "input_tokens": resp.usage.input_tokens_total,
                        "output_tokens": resp.usage.output_tokens_total,
                    }
                    row["nRetries"] = resp.usage.n_retries
                except Exception as exc:  # noqa: BLE001 - recorded, scored as a failure
                    row["error"] = f"{type(exc).__name__}: {str(exc)[:500]}"
                row["latencyMs"] = int((time.perf_counter() - t0) * 1000)
                return row

        with open(out_path(dataset), "a", encoding="utf-8") as fh:
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
    print(f"{dataset} done: ok={ok} failed={failed}", file=sys.stderr)
    return 3 if failed else 0


async def smoke():
    """Feasibility, not scored: one synthetic state per question shape; prints the answer shape."""
    from system_one_adapter import AsyncSystemOneAdapterClient
    from system_one_adapter.providers.openai import AsyncOpenAIProvider
    from typesafe_sdk import RetryPolicy

    provider = AsyncOpenAIProvider(
        MODEL, base_url=BASE_URL, api_key=os.environ["XAI_API_KEY"]
    )
    async with AsyncSystemOneAdapterClient(
        structured_outputs=True,
        llm_answer_mode="probabilities",
        normalize_probabilities=True,
        retry=RetryPolicy(),
    ) as client:
        for dataset, st in (
            (
                "scifact",
                {
                    "claim": "Water boils at 100 C at sea level.",
                    "title": "Boiling",
                    "abstract": "At standard atmospheric pressure water boils at 100 degrees Celsius.",
                },
            ),
            (
                "banking77",
                {
                    "customer_message": "My card expires next month, how do I get a new one?"
                },
            ),
        ):
            _, questions, _, _ = setup(dataset)
            resp = await client.system_one(st, questions, model=provider)
            facts = attempt_facts(resp)
            print(
                json.dumps(
                    {
                        "dataset": dataset,
                        "answers": {k: v.model_dump() for k, v in resp.answers.items()},
                        "probability_errors": resp.debug.get("probability_errors"),
                        **{
                            k: facts[k]
                            for k in (
                                "provider",
                                "api",
                                "finishReason",
                                "modelReported",
                                "nAttempts",
                            )
                        },
                        "usage": [
                            resp.usage.input_tokens_total,
                            resp.usage.output_tokens_total,
                        ],
                    },
                    default=str,
                )
            )
    await provider.aclose()
    return 0


def main(argv):
    if len(argv) != 1 or argv[0] not in (
        "smoke",
        "scifact",
        "banking77",
        "sst5",
        "clinc150",
    ):
        raise SystemExit("usage: run.py smoke|scifact|banking77|sst5|clinc150")
    if not os.environ.get("XAI_API_KEY"):
        print("unconfigured: XAI_API_KEY is not set, no call made", file=sys.stderr)
        return 2
    return asyncio.run(smoke() if argv[0] == "smoke" else run(argv[0]))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
