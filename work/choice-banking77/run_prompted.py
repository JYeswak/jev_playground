#!/usr/bin/env python3
"""Haiku arm for bead jev-4jf, prompted-JSON variant (second preregistration).

Under the first bar (909278f), every Haiku request for the 77-option Choice with native structured
outputs was rejected by Anthropic, verbatim: "400 The compiled grammar is too large, which would
cause performance issues. Simplify your tool schemas or reduce the number of strict tools."
The cap is on the constrained-decoding grammar, not the option count. So this variant sends the
same state and the same single 77-option Choice through the same adapter with
structured_outputs=False: the adapter puts the output JSON schema in the system prompt and
validates the reply. One corrective retry is allowed for malformed output
(n_retry_malformed_structure=1). Every other setting matches run.py.

Bar: docs/demos/upstream-repro/choice-banking77-full-20260924.md, "Second preregistration".
Rows: rows-full-haiku-prompted.jsonl, or --out <path> (repeat runs, bead jev-384m). Resumes rows
that already have a choice.
Run:
  infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
    upstream/typesafe-ai/system-one-adapter-python/.venv/bin/python work/choice-banking77/run_prompted.py
"""

import asyncio
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import run  # noqa: E402  (also puts the vendored SDK and adapter on sys.path)
from typesafe_sdk import RetryPolicy  # noqa: E402

sys.path.insert(0, os.path.join(run.ROOT, "work", "anthropic-stop"))
from anthropic_stop import refuse_anthropic_comparator  # noqa: E402  jev-sybt

OUT = os.path.join(run.HERE, "rows-full-haiku-prompted.jsonl")


def main(argv, bar_path=None, repo=None):
    refuse_anthropic_comparator(
        "choice-banking77 run_prompted Haiku arm (claude-haiku-4-5)"
    )
    sys.path.insert(0, os.path.join(run.ROOT, "work/sr-adopt"))
    from phase_gate import call_after_bar

    bar = bar_path or os.path.join(
        run.ROOT, "docs/demos/upstream-repro/choice-banking77-full-variance-20260924.md"
    )
    call_after_bar(bar, lambda: None, repo=repo or run.ROOT)
    # --out replaces the rows path for repeat runs (bead jev-384m), as run.py --out does.
    out = OUT
    if "--out" in argv:
        out = os.path.abspath(argv[argv.index("--out") + 1])
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("unconfigured: ANTHROPIC_API_KEY unset, no call made", file=sys.stderr)
        return 2
    from system_one_adapter import AsyncSystemOneAdapterClient

    rows = run.load_rows("full.jsonl")
    label_map = run.labels(rows)
    q = run.question(label_map)
    have = run.done_ids(out)
    todo = [r for r in rows if r["i"] not in have]
    print(f"haiku prompted: {len(todo)} to run, {len(have)} resumed", file=sys.stderr)

    async def go():
        ok = failed = 0
        sem = asyncio.Semaphore(run.CONCURRENCY)
        async with AsyncSystemOneAdapterClient(
            structured_outputs=False,
            llm_answer_mode="probabilities",
            normalize_probabilities=True,
            n_retry_malformed_structure=1,
            retry=RetryPolicy(),
        ) as client:

            async def one(item):
                async with sem:
                    t0 = time.perf_counter()
                    try:
                        resp = await asyncio.wait_for(
                            client.system_one(
                                run.state(item),
                                q,
                                provider="anthropic",
                                model=run.HAIKU_MODEL,
                            ),
                            timeout=120,
                        )
                        ms = int((time.perf_counter() - t0) * 1000)
                        usage = {
                            "input_tokens": int(resp.usage.input_tokens_total),
                            "output_tokens": int(resp.usage.output_tokens_total),
                        }
                        extra = run.haiku_diagnostics(resp)
                        extra["nRetriesMalformed"] = int(
                            getattr(resp.usage, "n_retries_malformed_structure", 0) or 0
                        )
                        return run.answer_row(
                            item,
                            label_map,
                            resp.answers["intent"],
                            f"anthropic/{run.HAIKU_MODEL}",
                            ms,
                            usage,
                            extra,
                        )
                    except Exception as exc:  # noqa: BLE001 - recorded, scored as wrong
                        return run.error_row(item, exc)

            for coro in asyncio.as_completed([one(item) for item in todo]):
                row = await coro
                run.record(out, row)
                if "error" in row:
                    failed += 1
                else:
                    ok += 1
                if (ok + failed) % 100 == 0:
                    print(
                        f"  haiku prompted {ok + failed}/{len(todo)} failed={failed}",
                        file=sys.stderr,
                    )
        print(f"haiku prompted done ok={ok} failed={failed}", file=sys.stderr)
        return 3 if failed > run.fail_limit(rows) else 0

    return asyncio.run(go())


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
