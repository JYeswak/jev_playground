#!/usr/bin/env python3
"""Incumbent cells for bead jev-qip: the same state {user_message} and the same question (plain,
or plus criteria.json) through system-one-adapter-python with anthropic/claude-haiku-4-5.
Mirrors run-jev.mjs row shape; all four cells (plain|criteria x attacks|toolout) are run here.

Bar: docs/demos/upstream-repro/jev-toolout-flag-20260924.md (committed before any call).
Run: infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
       upstream/typesafe-ai/system-one-adapter-python/.venv/bin/python \
       work/jev-toolout-flag/run-haiku.py criteria attacks
Appends to rows-haiku-<arm>-<corpus>.jsonl; resumes rows that already have a score.
"""

import asyncio
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

from system_one_adapter import AsyncSystemOneAdapterClient, Noul  # noqa: E402
from anthropic_stop import refuse_paid_comparator  # noqa: E402  jev-sybt, jev-lbgk
from typesafe_sdk import RetryPolicy  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "k9z5_haiku", os.path.join(ROOT, "work/jev-injection-flag/run-haiku.py")
)
_k9z5 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_k9z5)
QUESTION = _k9z5.QUESTION  # read from .omp/tools/jev-screen.ts at import
CUT = 0.5


def load_corpus(name):
    if name == "attacks":
        path = os.path.join(ROOT, "work/nev-injection/pairs.jsonl")
        rows = [json.loads(line) for line in open(path) if line.strip()]
        return [
            {"i": i, "id": r["id"], "label": r["label"], "text": r["text"]}
            for i, r in enumerate(rows)
        ]
    path = os.path.join(ROOT, "work/jev-injection-flag/tool-results-sample.json")
    rows = json.load(open(path))["rows"]
    return [
        {"i": i, "id": f"tool-{i}", "label": 0, "text": r["text"]}
        for i, r in enumerate(rows)
    ]


def done_ids(out):
    ids = set()
    if os.path.exists(out):
        for line in open(out):
            if line.strip():
                r = json.loads(line)
                if isinstance(r.get("p"), (int, float)):
                    ids.add(r["i"])
    return ids


async def main(arm, corpus, concurrency=8):
    refuse_paid_comparator(
        f"jev-toolout-flag run-haiku {arm}/{corpus} (claude-haiku-4-5)"
    )
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print(
            "unconfigured: ANTHROPIC_API_KEY is not set, no call made", file=sys.stderr
        )
        return 2
    out_path = os.path.join(HERE, f"rows-haiku-{arm}-{corpus}.jsonl")
    crit = json.load(open(os.path.join(HERE, "criteria.json")))
    question = (
        Noul(instructions=QUESTION)
        if arm == "plain"
        else Noul(
            instructions=QUESTION,
            criteria={"true": crit["true"], "false": crit["false"]},
        )
    )
    have = done_ids(out_path)
    todo = [r for r in load_corpus(corpus) if r["i"] not in have]
    print(
        f"haiku {arm}/{corpus}: {len(todo)} to run, {len(have)} resumed",
        file=sys.stderr,
    )
    sem = asyncio.Semaphore(concurrency)
    ok = failed = 0
    async with AsyncSystemOneAdapterClient(
        structured_outputs=True,
        llm_answer_mode="probabilities",
        normalize_probabilities=True,
        retry=RetryPolicy(),
    ) as client:

        async def one(row):
            async with sem:
                t0 = time.time()
                out = {
                    "i": row["i"],
                    "id": row["id"],
                    "label": row["label"],
                    "arm": arm,
                    "model": "anthropic/claude-haiku-4-5",
                }
                try:
                    resp = await asyncio.wait_for(
                        client.system_one(
                            {"user_message": row["text"]},
                            {"inj": question},
                            provider="anthropic",
                            model="claude-haiku-4-5",
                        ),
                        timeout=90,
                    )
                    p = float(resp.answers["inj"].noul)
                    out.update(
                        p=p,
                        flag=p >= CUT,
                        latencyMs=int((time.time() - t0) * 1000),
                        usage={
                            "input_tokens": int(resp.usage.input_tokens_total),
                            "output_tokens": int(resp.usage.output_tokens_total),
                        },
                    )
                except Exception as e:  # noqa: BLE001 - recorded, never scored
                    out["error"] = f"{type(e).__name__}: {str(e)[:200]}"
                return out

        for coro in asyncio.as_completed([one(r) for r in todo]):
            out = await coro
            with open(out_path, "a") as f:
                f.write(json.dumps(out, ensure_ascii=False) + "\n")
            if "error" in out:
                failed += 1
            else:
                ok += 1
            if (ok + failed) % 50 == 0:
                print(
                    f"  {ok + failed}/{len(todo)} ok={ok} failed={failed}",
                    file=sys.stderr,
                )
    print(f"done: ok={ok} failed={failed}", file=sys.stderr)
    return 3 if failed > 6 else 0


if __name__ == "__main__":
    if (
        len(sys.argv) != 3
        or sys.argv[1] not in ("plain", "criteria")
        or sys.argv[2] not in ("attacks", "toolout")
    ):
        print("usage: run-haiku.py plain|criteria attacks|toolout", file=sys.stderr)
        sys.exit(64)
    sys.exit(asyncio.run(main(sys.argv[1], sys.argv[2])))
