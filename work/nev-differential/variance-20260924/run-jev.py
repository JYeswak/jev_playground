#!/usr/bin/env python3
"""Third Jev run for bead jev-rf57: the 662 jev-sec-bench injection rows, jev-1.13.0.

Questions, state and corpus come from work/nev-differential/run_diff.py, imported and not edited:
build_questions() (the upstream InjectionBattery Noul + Score), ASSISTANT, and SRC
(jev-sec-bench/results/injection.json). The client is the official typesafe_sdk AsyncTypeSafeClient
pinned to jev-1.13.0 with RetryPolicy(), concurrency 8. Rows go to rows-jev-run3.jsonl beside this
file, one per id, in the fresh-20260923 row shape (id, label, p, sev, sev_conf, lat_ms, in_tok,
out_tok, model). A rerun resumes rows that have no answer. Never prints a key.
Bar: docs/demos/upstream-repro/injection-variance-20260924.md (committed before any call).

Run:
  infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
    upstream/typesafe-ai/system-one-adapter-python/.venv/bin/python \
    work/nev-differential/variance-20260924/run-jev.py
"""

import asyncio
import importlib.util
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "run_diff", os.path.join(os.path.dirname(HERE), "run_diff.py")
)
RD = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(RD)

from typesafe_sdk import AsyncTypeSafeClient, RetryPolicy  # noqa: E402

MODEL = "jev-1.13.0"
OUT = os.path.join(HERE, "rows-jev-run3.jsonl")


def done():
    ids = set()
    if os.path.exists(OUT):
        for line in open(OUT):
            if line.strip():
                r = json.loads(line)
                if "p" in r:
                    ids.add(r["id"])
    return ids


async def main(concurrency=8, bar_path=None, repo=None):
    root = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
    sys.path.insert(0, os.path.join(root, "work/sr-adopt"))
    from phase_gate import call_after_bar

    bar = bar_path or os.path.join(
        root, "docs/demos/upstream-repro/injection-variance-20260924.md"
    )
    call_after_bar(bar, lambda: None, repo=repo or root)
    if not os.environ.get("TYPESAFE_API_KEY"):
        print(
            "unconfigured: TYPESAFE_API_KEY is not set, no call made", file=sys.stderr
        )
        return 2
    samples = json.load(open(RD.SRC))["samples"]
    rows = [(f"inj-{i:04d}", s["text"], int(s["label"])) for i, s in enumerate(samples)]
    assert len(rows) == 662, f"corpus drift: {len(rows)}"
    have = done()
    todo = [r for r in rows if r[0] not in have]
    print(f"jev run3: {len(todo)} to run, {len(have)} resumed", file=sys.stderr)
    questions = RD.build_questions()
    sem = asyncio.Semaphore(concurrency)
    ok = failed = 0
    async with AsyncTypeSafeClient(model=MODEL, retry=RetryPolicy()) as client:

        async def one(rid, text, label):
            async with sem:
                t0 = time.time()
                rec = {"id": rid, "label": label}
                try:
                    resp = await asyncio.wait_for(
                        client.system_one(
                            {"assistant": RD.ASSISTANT, "user_message": text}, questions
                        ),
                        timeout=90,
                    )
                    sev = resp.scores["severity"]
                    rec.update(
                        p=float(resp.nouls["injection"].noul),
                        sev=float(sev.score),
                        sev_conf=float(sev.confidence),
                        lat_ms=int((time.time() - t0) * 1000),
                        in_tok=resp.usage.input_tokens,
                        out_tok=resp.usage.output_tokens,
                        model=resp.model,
                    )
                except Exception as e:  # noqa: BLE001 - recorded, never scored as an answer
                    rec["error"] = f"{type(e).__name__}: {str(e)[:200]}"
                return rec

        for coro in asyncio.as_completed([one(*r) for r in todo]):
            rec = await coro
            with open(OUT, "a") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            if "error" in rec:
                failed += 1
            else:
                ok += 1
    print(f"done: ok={ok} failed={failed}", file=sys.stderr)
    return 3 if failed else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
