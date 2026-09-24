#!/usr/bin/env python3
"""Live arms for bead jev-nssg. One Noul per (query, BM25 top-20 passage).

  python3 work/rerank-scifact/run.py --selftest
  infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \\
    upstream/typesafe-ai/system-one-adapter-python/.venv/bin/python \\
    work/rerank-scifact/run.py {jev|jev-run2|jev-run3|grok|grok-run2|grok-run3}

Question and state are frozen with the bar
(docs/demos/upstream-repro/rerank-beir-scifact-20260924.md). One request per pair:
the state holds that pair only, so no candidate sees another
(docs-mirror/typesafe/cookbooks/rerank_typesafe.md).

A Jev HTTP 402 billing_error stops the arm after the failing call. It does not
retry the queue. Rows never contain query or passage text.
"""

import asyncio
import json
import os
import sys
import time
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(
    0, os.path.join(ROOT, "upstream/typesafe-ai/system-one-adapter-python/src")
)
sys.path.insert(0, os.path.join(ROOT, "work", "anthropic-stop"))

from typesafe_sdk import Noul, RetryPolicy  # noqa: E402
from anthropic_stop import refuse_paid_comparator  # noqa: E402  jev-lbgk

JEV_MODEL = "jev-1.13.0"
GROK_MODEL = "grok-4.20-0309-non-reasoning"
GROK_BASE = "https://api.x.ai/v1"
QNAME = "relevant"
ZIP_SHA256 = "536e14446a0ba56ed1398ab1055f39fe852686ecad24a6306c80c490fa8e0165"
ZIP_PATH = os.environ.get("BEIR_SCIFACT_ZIP", "/tmp/beir-scifact/scifact.zip")
DEPTH = 20
TIMEOUT_S = 120
# Frozen with the bar. Instructions are the bead's phrase as a Noul question.
# Criteria follow the rerank cookbook: true/false are defined, and relevance is
# not collapsed into support.
QUESTION = Noul(
    instructions="Does this passage contain evidence relevant to the query?",
    criteria={
        "true": (
            "The passage is on the query's subject and states evidence a reader "
            "could use in assessing it, whether or not that evidence supports the query."
        ),
        "false": "The passage is on a different subject, or states nothing about the query.",
    },
)
ARMS = ("jev", "jev-run2", "jev-run3", "grok", "grok-run2", "grok-run3")
BILLING = (
    "402 Your organization has no available TypeSafe API credits. "
    "Please add more credits and/or set up auto-reload at "
    "https://console.typesafe.ai/settings/billing"
)


def out_path(arm):
    return os.path.join(HERE, f"rows-{arm}.jsonl")


def repair_tail(path):
    """Drop one trailing partial line left by a crash. Does not delete the file."""
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    if text.endswith("\n"):
        last = text.rstrip("\n").split("\n")[-1]
    else:
        last = text.split("\n")[-1]
    try:
        json.loads(last)
    except json.JSONDecodeError:
        kept = text[: text.rfind("\n") + 1] if "\n" in text else ""
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(kept)


def answered(arm):
    repair_tail(out_path(arm))
    got = set()
    path = out_path(arm)
    if not os.path.exists(path):
        return got
    for line in open(path, encoding="utf-8"):
        if not line.strip():
            continue
        row = json.loads(line)
        if "noul" in row:
            got.add((row["qid"], row["doc"]))
    return got


def load_text():
    import hashlib

    digest = hashlib.sha256(open(ZIP_PATH, "rb").read()).hexdigest()
    if digest != ZIP_SHA256:
        raise SystemExit(f"scifact.zip sha256 {digest} != {ZIP_SHA256}")
    with zipfile.ZipFile(ZIP_PATH) as zf:
        corpus = {
            d["_id"]: d
            for d in (
                json.loads(line)
                for line in zf.read("scifact/corpus.jsonl").decode().splitlines()
                if line.strip()
            )
        }
        queries = {
            q["_id"]: q["text"]
            for q in (
                json.loads(line)
                for line in zf.read("scifact/queries.jsonl").decode().splitlines()
                if line.strip()
            )
        }
    return corpus, queries


def pairs():
    rows = [
        json.loads(line)
        for line in open(os.path.join(HERE, "candidates.jsonl"), encoding="utf-8")
        if line.strip()
    ]
    out = []
    for row in rows:
        if len(row["cands"]) != DEPTH:
            raise SystemExit(f"qid {row['qid']} does not have {DEPTH} candidates")
        for doc, _score in row["cands"]:
            out.append((row["qid"], doc))
    return out


def state_for(corpus, queries, qid, doc):
    passage = corpus[doc]
    return {
        "query": queries[qid],
        "passage": {
            "id": doc,
            "title": passage.get("title") or "",
            "text": passage.get("text") or "",
        },
    }


def row_ok(qid, doc, arm, model, noul, latency_ms, usage, extra=None):
    row = {
        "qid": qid,
        "doc": doc,
        "arm": arm,
        "model": model,
        "noul": noul,
        "latencyMs": latency_ms,
        "usage": usage,
    }
    if extra:
        row.update(extra)
    banned = {"query", "title", "text", "passage", "abstract"}
    if banned & set(row):
        raise SystemExit(f"row would commit passage text: {sorted(banned & set(row))}")
    return row


def billing_block(message):
    return "402" in message and "credits" in message.lower()


async def run_arm(arm, bar_path=None, repo=None):
    if not arm.startswith("jev"):
        refuse_paid_comparator(f"rerank-scifact {arm} ({GROK_MODEL})")
    sys.path.insert(0, os.path.join(ROOT, "work/sr-adopt"))
    from phase_gate import call_after_bar

    bar = bar_path or os.path.join(
        ROOT, "docs/demos/upstream-repro/rerank-beir-scifact-20260924.md"
    )
    call_after_bar(bar, lambda: None, repo=repo or ROOT)
    jev = arm.startswith("jev")
    need = "TYPESAFE_API_KEY" if jev else "XAI_API_KEY"
    if not os.environ.get(need):
        print(f"unconfigured: {need} is not set, no call made", file=sys.stderr)
        return 2
    corpus, queries = load_text()
    todo = [pair for pair in pairs() if pair not in answered(arm)]
    print(
        f"{arm}: {len(todo)} to run, {len(pairs()) - len(todo)} resumed",
        file=sys.stderr,
    )
    if not todo:
        return 0
    concurrency = int(os.environ.get("RERANK_CONCURRENCY", "16" if jev else "8"))
    sem = asyncio.Semaphore(concurrency)
    stop = asyncio.Event()
    ok = failed = 0

    if jev:
        from typesafe_sdk import AsyncTypeSafeClient

        client_cm = AsyncTypeSafeClient(model=JEV_MODEL, retry=RetryPolicy())

        async def call(qid, doc):
            resp = await client_cm.system_one(
                state_for(corpus, queries, qid, doc), {QNAME: QUESTION}
            )
            return {
                "noul": float(resp.nouls[QNAME].noul),
                "model": resp.model,
                "usage": {
                    "input_tokens": resp.usage.input_tokens,
                    "output_tokens": resp.usage.output_tokens,
                },
            }

    else:
        from system_one_adapter import AsyncSystemOneAdapterClient
        from system_one_adapter.providers.openai import AsyncOpenAIProvider

        provider = AsyncOpenAIProvider(
            GROK_MODEL, base_url=GROK_BASE, api_key=os.environ["XAI_API_KEY"]
        )
        client_cm = AsyncSystemOneAdapterClient(
            structured_outputs=True,
            llm_answer_mode="probabilities",
            normalize_probabilities=True,
            retry=RetryPolicy(),
        )

        async def call(qid, doc):
            resp = await client_cm.system_one(
                state_for(corpus, queries, qid, doc),
                {QNAME: QUESTION},
                model=provider,
            )
            debug = resp.debug or {}
            return {
                "noul": float(resp.answers[QNAME].noul),
                "model": f"xai/{GROK_MODEL}",
                "usage": {
                    "input_tokens": int(resp.usage.input_tokens_total),
                    "output_tokens": int(resp.usage.output_tokens_total),
                },
                "probabilityError": (debug.get("probability_errors") or {}).get(QNAME),
                "originalProbabilities": (
                    debug.get("original_probabilities") or {}
                ).get(QNAME),
            }

    blocked = False
    async with client_cm:
        lock = asyncio.Lock()

        async def one(qid, doc):
            if stop.is_set():
                return None
            async with sem:
                if stop.is_set():
                    return None
                t0 = time.perf_counter()
                try:
                    got = await asyncio.wait_for(call(qid, doc), timeout=TIMEOUT_S)
                except Exception as exc:  # noqa: BLE001 - recorded, or stops the arm
                    message = f"{type(exc).__name__}: {str(exc)[:500]}"
                    if jev and billing_block(message):
                        stop.set()
                        return {
                            "qid": qid,
                            "doc": doc,
                            "arm": arm,
                            "error": message,
                            "blocked": True,
                            "latencyMs": int((time.perf_counter() - t0) * 1000),
                        }
                    return {
                        "qid": qid,
                        "doc": doc,
                        "arm": arm,
                        "error": message,
                        "latencyMs": int((time.perf_counter() - t0) * 1000),
                    }
                extra = {
                    k: got[k]
                    for k in ("probabilityError", "originalProbabilities")
                    if k in got
                }
                return row_ok(
                    qid,
                    doc,
                    arm,
                    got["model"],
                    got["noul"],
                    int((time.perf_counter() - t0) * 1000),
                    got["usage"],
                    extra or None,
                )

        with open(out_path(arm), "a", encoding="utf-8") as fh:
            tasks = [asyncio.create_task(one(q, d)) for q, d in todo]
            for fut in asyncio.as_completed(tasks):
                row = await fut
                if row is None:
                    continue
                async with lock:
                    fh.write(json.dumps(row, ensure_ascii=False) + "\n")
                    fh.flush()
                if row.get("blocked"):
                    blocked = True
                    print(
                        "BLOCKED-until-credits: "
                        + row["error"]
                        + "\nverbatim expected: "
                        + BILLING,
                        file=sys.stderr,
                    )
                    for task in tasks:
                        task.cancel()
                    break
                failed += "error" in row
                ok += "error" not in row
                if (ok + failed) % 100 == 0:
                    print(
                        f"  {ok + failed}/{len(todo)} ok={ok} failed={failed}",
                        file=sys.stderr,
                    )
    if not jev:
        await provider.aclose()
    print(f"{arm} done: ok={ok} failed={failed} blocked={blocked}", file=sys.stderr)
    if blocked:
        return 4
    return 3 if failed else 0


def selftest():
    """Question and row shape. No key, no network, no passage text printed."""
    bad = []
    if (
        QUESTION.instructions
        != "Does this passage contain evidence relevant to the query?"
    ):
        bad.append("instructions drifted")
    criteria = QUESTION.criteria
    true = criteria["true"] if isinstance(criteria, dict) else criteria.true
    false = criteria["false"] if isinstance(criteria, dict) else criteria.false
    if "whether or not that evidence supports" not in true:
        bad.append("true criterion drifted")
    if not false.startswith("The passage is on a different subject"):
        bad.append("false criterion drifted")
    if os.path.exists(ZIP_PATH):
        corpus, queries = load_text()
        qid, doc = pairs()[0]
        st = state_for(corpus, queries, qid, doc)
        if set(st) != {"query", "passage"} or set(st["passage"]) != {
            "id",
            "title",
            "text",
        }:
            bad.append(f"state keys {set(st)} {set(st.get('passage', {}))}")
        if st["passage"]["id"] != doc or not st["query"] or not st["passage"]["text"]:
            bad.append("state missing the pair")
        row = row_ok(
            qid, doc, "jev", JEV_MODEL, 0.5, 1, {"input_tokens": 1, "output_tokens": 0}
        )
        if "text" in json.dumps(row) and st["passage"]["text"][:20] in json.dumps(row):
            bad.append("row contains passage text")
    else:
        bad.append(f"zip absent at {ZIP_PATH}")
    if not billing_block("TypeSafeBadRequestError: 402 " + BILLING):
        bad.append("402 detector")
    for item in bad:
        print("SELFTEST RED:", item)
    print("SELFTEST " + ("FAIL" if bad else "PASS"))
    return 1 if bad else 0


def main(argv):
    if argv == ["--selftest"]:
        return selftest()
    if len(argv) != 1 or argv[0] not in ARMS:
        raise SystemExit("usage: run.py " + "|".join(ARMS) + " | --selftest")
    return asyncio.run(run_arm(argv[0]))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
