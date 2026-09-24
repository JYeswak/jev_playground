#!/usr/bin/env python3
"""Bead jev-mly, live arm: re-ask Haiku the exact jev-k3k question for the 14 rows that came
back uniform, plus 14 fixed control rows, 5 repeats each, capturing the raw Anthropic
response next to the adapter's answer. Bar: docs/demos/upstream-repro/adapter-uniform-20260924.md.

State, question, labels and client settings come from the jev-k3k runner and rows exactly as
committed at 3709ee6 (read with `git show`, because work/choice-banking77/run.py has since been
extended for jev-4jf), so they are byte-identical to the jev-k3k Haiku arm. The raw response is
captured by wrapping the caller-owned provider's SDK `messages.create`; the vendored clone is not
edited.

Run (live, needs ANTHROPIC_API_KEY; never prints it):
  infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
    upstream/typesafe-ai/system-one-adapter-python/.venv/bin/python work/adapter-uniform/live.py run
Re-score (keyless, from the committed rows):
  python3 work/adapter-uniform/live.py score
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
sys.path.insert(0, os.path.join(ROOT, "work", "anthropic-stop"))
from anthropic_stop import refuse_paid_comparator  # noqa: E402  jev-sybt, jev-lbgk

K3K = os.path.join(ROOT, "work/choice-banking77")
K3K_SHA = "3709ee6"  # the commit that recorded jev-k3k rows-haiku.jsonl
OUT = os.path.join(HERE, "live-raw.jsonl")
REPEATS = 5
CONCURRENCY = 8
HAIKU_MODEL = "claude-haiku-4-5"


def load_jsonl(path):
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def git_show(relpath):
    return subprocess.check_output(
        ["git", "-C", ROOT, "show", f"{K3K_SHA}:{relpath}"], text=True
    )


def k3k_jsonl(name):
    text = git_show(f"work/choice-banking77/{name}")
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def k3k_runner():
    """The jev-k3k runner module as committed at K3K_SHA."""
    module = types.ModuleType("k3k_run")
    module.__file__ = os.path.join(K3K, "run.py")
    exec(
        compile(git_show("work/choice-banking77/run.py"), module.__file__, "exec"),
        module.__dict__,
    )  # noqa: S102
    return module


def is_uniform(row):
    probs = row.get("probabilities") or {}
    return bool(probs) and len(set(probs.values())) == 1


def select_rows():
    """Targets: every jev-k3k Haiku row with an exactly uniform distribution.
    Controls: for each target, the next subset row (by i) with the same intent that was
    NOT uniform in jev-k3k, never reused."""
    k3k = {r["i"]: r for r in k3k_jsonl("rows-haiku.jsonl")}
    subset = sorted(k3k_jsonl("subset.jsonl"), key=lambda r: r["i"])
    targets = sorted(i for i, r in k3k.items() if is_uniform(r))
    used, controls = set(targets), []
    for t in targets:
        intent = k3k[t]["intent"]
        pick = next(
            r["i"]
            for r in subset
            if r["i"] > t
            and r["intent"] == intent
            and r["i"] not in used
            and not is_uniform(k3k[r["i"]])
        )
        used.add(pick)
        controls.append(pick)
    by_i = {r["i"]: r for r in subset}
    return [("target", by_i[i]) for i in targets] + [
        ("control", by_i[i]) for i in controls
    ]


def raw_distribution(text):
    """Parse the model's own JSON independently of the adapter; None if unparsable."""
    try:
        return json.loads(text)["answers"]["intent"]
    except (ValueError, KeyError, TypeError):
        return None


def run():
    refuse_paid_comparator("adapter-uniform live (claude-haiku-4-5)")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("unconfigured: ANTHROPIC_API_KEY unset, no call made", file=sys.stderr)
        return 2
    k3k_run = k3k_runner()  # question(), state(), labels() as committed at K3K_SHA
    from system_one_adapter import AsyncSystemOneAdapterClient
    from system_one_adapter.providers.anthropic import AsyncAnthropicProvider
    from typesafe_sdk import RetryPolicy

    label_map = k3k_run.labels(k3k_jsonl("subset.jsonl"))
    q = k3k_run.question(label_map)
    jobs = [(arm, row, rep) for arm, row in select_rows() for rep in range(REPEATS)]
    print(f"live: {len(jobs)} calls", file=sys.stderr)

    async def go():
        sem = asyncio.Semaphore(CONCURRENCY)
        async with AsyncSystemOneAdapterClient(
            structured_outputs=True,
            llm_answer_mode="probabilities",
            normalize_probabilities=True,
            retry=RetryPolicy(),
        ) as client:

            async def one(arm, row, rep):
                provider = AsyncAnthropicProvider(HAIKU_MODEL)
                captured = []
                real_create = provider._client.messages.create

                async def create(**kwargs):
                    response = await real_create(**kwargs)
                    captured.append(response.model_dump(mode="json"))
                    return response

                provider._client.messages.create = create
                out = {"i": row["i"], "intent": row["intent"], "arm": arm, "rep": rep}
                async with sem:
                    t0 = time.perf_counter()
                    try:
                        resp = await asyncio.wait_for(
                            client.system_one(k3k_run.state(row), q, model=provider),
                            timeout=90,
                        )
                        ans = resp.answers["intent"]
                        out.update(
                            adapter_choice=label_map.get(ans.choice, ans.choice),
                            adapter_confidence=float(ans.confidence),
                            adapter_probabilities={
                                label_map.get(k, k): float(v)
                                for k, v in ans.probabilities.items()
                            },
                            adapter_debug={
                                k: resp.debug[k]
                                for k in (
                                    "max_error",
                                    "invalid_probs",
                                    "probability_errors",
                                    "original_probabilities",
                                )
                                if k in resp.debug
                            },
                            n_attempts=len(resp.debug.get("llm_attempts", [])),
                        )
                    except Exception as exc:  # noqa: BLE001 - recorded, never hidden
                        out["error"] = f"{type(exc).__name__}: {str(exc)[:300]}"
                    finally:
                        await provider.aclose()
                    out["latencyMs"] = int((time.perf_counter() - t0) * 1000)
                out["raw_responses"] = [
                    {
                        "id": r.get("id"),
                        "model": r.get("model"),
                        "stop_reason": r.get("stop_reason"),
                        "text": "".join(
                            b.get("text", "")
                            for b in r.get("content", [])
                            if b.get("type") == "text"
                        ),
                        "usage": {
                            "input_tokens": r["usage"]["input_tokens"],
                            "output_tokens": r["usage"]["output_tokens"],
                        },
                    }
                    for r in captured
                ]
                return out

            with open(OUT, "w", encoding="utf-8") as fh:
                for coro in asyncio.as_completed([one(*job) for job in jobs]):
                    fh.write(json.dumps(await coro, ensure_ascii=False) + "\n")

    asyncio.run(go())
    return score()


def score():
    rows = load_jsonl(OUT)
    summary = {}
    zero_examples = []
    for arm in ("target", "control"):
        arm_rows = [r for r in rows if r["arm"] == arm]
        errors = [r for r in arm_rows if "error" in r]
        ok = [r for r in arm_rows if "error" not in r]
        uniform = [
            r for r in ok if is_uniform({"probabilities": r["adapter_probabilities"]})
        ]
        last_raw = [
            raw_distribution(r["raw_responses"][-1]["text"])
            if r["raw_responses"]
            else None
            for r in uniform
        ]
        zero_sum = [d for d in last_raw if d is not None and sum(d.values()) == 0]
        asserted_uniform = [
            d for d in last_raw if d is not None and sum(d.values()) > 0
        ]
        unparsable = [d for d in last_raw if d is None]
        rows_hit = sorted({r["i"] for r in uniform})
        summary[arm] = {
            "calls": len(arm_rows),
            "errors": len(errors),
            "adapter_uniform": len(uniform),
            "uniform_raw_all_zero": len(zero_sum),
            "uniform_raw_model_asserted": len(asserted_uniform),
            "uniform_raw_unparsable": len(unparsable),
            "rows": len({r["i"] for r in arm_rows}),
            "rows_with_any_uniform": len(rows_hit),
            "row_ids_with_any_uniform": rows_hit,
            "uniform_choice_is_first_criterion": sum(
                r["adapter_choice"] == "activate_my_card" for r in uniform
            ),
            "stop_reasons": sorted(
                {x["stop_reason"] for r in arm_rows for x in r["raw_responses"]}
            ),
        }
        for r in uniform[:3]:
            zero_examples.append(
                {
                    "i": r["i"],
                    "rep": r["rep"],
                    "raw_text": r["raw_responses"][-1]["text"],
                    "stop_reason": r["raw_responses"][-1]["stop_reason"],
                    "adapter_debug": r["adapter_debug"],
                }
            )
    usage_in = sum(x["usage"]["input_tokens"] for r in rows for x in r["raw_responses"])
    usage_out = sum(
        x["usage"]["output_tokens"] for r in rows for x in r["raw_responses"]
    )
    summary["tokens"] = {
        "input": usage_in,
        "output": usage_out,
        "usd_at_1_in_5_out_per_mtok": round(
            usage_in / 1e6 * 1 + usage_out / 1e6 * 5, 4
        ),
    }
    summary["examples"] = zero_examples
    print(json.dumps(summary, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "score"
    raise SystemExit(run() if cmd == "run" else score())
