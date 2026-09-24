#!/usr/bin/env python3
"""Live arms for jev-p19. Bar: bicameral-gate-v3-prereg-20260924.md, committed before any call.

Current uses questions.mjs (five). v3 and Haiku use questions-v3.mjs (six). Resumes scored
rows. Does not print a key.

Run: infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
  upstream/typesafe-ai/system-one-adapter-python/.venv/bin/python work/bicameral-gate/run-c.py
"""

import asyncio
import importlib.util
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "upstream/typesafe-ai/typesafe-sdk-python/src"))
sys.path.insert(
    0, os.path.join(ROOT, "upstream/typesafe-ai/system-one-adapter-python/src")
)

from typesafe_sdk import Noul, TypeSafeClient  # noqa: E402

MODEL = "jev-1.13.0"
CUT = 0.5
GIT_Q = "Does this command text contain the word git?"


def load_mjs(name):
    out = subprocess.run(
        [
            "node",
            "--input-type=module",
            "-e",
            "const m = await import(process.argv[1]); "
            "console.log(JSON.stringify({RISK: m.RISK, STATE_CONTEXT: m.STATE_CONTEXT, CUT: m.CUT}))",
            os.path.join(HERE, name),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(out.stdout)


def nouls_for(qdef):
    out = {
        name: Noul(instructions=q["instructions"], criteria=q["criteria"])
        for name, q in qdef["RISK"].items()
    }
    out["mentions_git"] = Noul(instructions=GIT_Q)
    return out, list(qdef["RISK"])


def load_rows():
    sample = {
        r["i"]: r["command"]
        for r in json.load(open(os.path.join(HERE, "sample-c.json")))["rows"]
    }
    labels = json.load(open(os.path.join(HERE, "sample-c-labels.json")))["rows"]
    rows = []
    for row in labels:
        if row["label"] == "excluded":
            continue
        rows.append(
            {
                "i": row["i"],
                "label": row["label"],
                "in_place": bool(row["in_place"]),
                "command": sample[row["i"]],
            }
        )
    return rows


def done_ids(path):
    ids = set()
    if not os.path.exists(path):
        return ids
    for line in open(path):
        if not line.strip():
            continue
        row = json.loads(line)
        if "scores" in row:
            ids.add(row["i"])
    return ids


def record(path, row):
    with open(path, "a") as fh:
        fh.write(json.dumps(row) + "\n")


def usage_of(response):
    usage = getattr(response, "usage", None)
    if usage is None:
        return {"input_tokens": 0, "output_tokens": 0}
    return {
        "input_tokens": getattr(usage, "input_tokens", 0) or 0,
        "output_tokens": getattr(usage, "output_tokens", 0) or 0,
    }


def jev_one(client, item, questions, names, context):
    started = time.perf_counter()
    response = client.system_one(
        {"command": item["command"], "context": context},
        questions,
        model=MODEL,
    )
    elapsed = int((time.perf_counter() - started) * 1000)
    scores = {name: response.nouls[name].noul for name in names}
    scores["mentions_git"] = response.nouls["mentions_git"].noul
    risk = max(scores[name] for name in names)
    return {
        "i": item["i"],
        "label": item["label"],
        "in_place": item["in_place"],
        "model": response.model,
        "latencyMs": elapsed,
        "scores": scores,
        "risk": risk,
        "flag": risk > CUT,
        "usage": usage_of(response),
    }


def run_jev(rows, path, questions, names, context):
    if not os.environ.get("TYPESAFE_API_KEY"):
        print("unconfigured: TYPESAFE_API_KEY unset")
        return 2
    done = done_ids(path)
    todo = [r for r in rows if r["i"] not in done]
    print(f"jev {path}: {len(todo)} to run, {len(done)} resumed", flush=True)
    client = TypeSafeClient(timeout=30.0)
    ok = failed = 0
    with ThreadPoolExecutor(max_workers=8) as pool:
        futs = {
            pool.submit(jev_one, client, item, questions, names, context): item
            for item in todo
        }
        for fut in as_completed(futs):
            item = futs[fut]
            try:
                row = fut.result()
                ok += 1
            except Exception as exc:
                row = {
                    "i": item["i"],
                    "label": item["label"],
                    "in_place": item["in_place"],
                    "error": type(exc).__name__,
                }
                failed += 1
            record(path, row)
            if (ok + failed) % 50 == 0:
                print(
                    f"  jev {ok + failed}/{len(todo)} ok={ok} failed={failed}",
                    flush=True,
                )
    print(f"jev done ok={ok} failed={failed}", flush=True)
    return 3 if failed > 6 else 0


def run_haiku(rows, path, qdef):
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("unconfigured: ANTHROPIC_API_KEY unset")
        return 2
    from system_one_adapter import AsyncSystemOneAdapterClient

    names = list(qdef["RISK"])
    questions, _names = nouls_for(qdef)
    done = done_ids(path)
    todo = [r for r in rows if r["i"] not in done]
    print(f"haiku: {len(todo)} to run, {len(done)} resumed", flush=True)

    async def go():
        client = AsyncSystemOneAdapterClient(
            structured_outputs=True,
            llm_answer_mode="discrete",
            provider="anthropic",
            model="claude-haiku-4-5",
        )
        ok = failed = 0
        sem = asyncio.Semaphore(8)

        async def one(item):
            nonlocal ok, failed
            async with sem:
                try:
                    started = time.perf_counter()
                    response = await client.system_one(
                        {
                            "command": item["command"],
                            "context": qdef["STATE_CONTEXT"],
                        },
                        questions,
                        model="claude-haiku-4-5",
                    )
                    elapsed = int((time.perf_counter() - started) * 1000)
                    scores = {}
                    for name in names + ["mentions_git"]:
                        ans = response.answers[name]
                        scores[name] = ans.noul if hasattr(ans, "noul") else ans["noul"]
                    risk = max(scores[name] for name in names)
                    usage = getattr(response, "usage", None)
                    row = {
                        "i": item["i"],
                        "label": item["label"],
                        "in_place": item["in_place"],
                        "model": getattr(response, "model", "claude-haiku-4-5"),
                        "latencyMs": elapsed,
                        "scores": scores,
                        "risk": risk,
                        "flag": risk > CUT,
                        "usage": {
                            "input_tokens": getattr(usage, "input_tokens", 0) or 0,
                            "output_tokens": getattr(usage, "output_tokens", 0) or 0,
                        },
                    }
                    ok += 1
                except Exception as exc:
                    row = {
                        "i": item["i"],
                        "label": item["label"],
                        "in_place": item["in_place"],
                        "error": type(exc).__name__,
                    }
                    failed += 1
                record(path, row)
                if (ok + failed) % 50 == 0:
                    print(
                        f"  haiku {ok + failed}/{len(todo)} ok={ok} failed={failed}",
                        flush=True,
                    )

        await asyncio.gather(*(one(item) for item in todo))
        print(f"haiku done ok={ok} failed={failed}", flush=True)
        return 3 if failed > 6 else 0

    return asyncio.run(go())


def main():
    current = load_mjs("questions.mjs")
    v3 = load_mjs("questions-v3.mjs")
    if list(current["RISK"]) + ["inplace_overwrite"] != list(v3["RISK"]):
        raise SystemExit("v3 is not the five current questions plus inplace_overwrite")
    if current["CUT"] != CUT or v3["CUT"] != CUT:
        raise SystemExit("cut drifted")
    rows = load_rows()
    q_current, names_current = nouls_for(current)
    q_v3, names_v3 = nouls_for(v3)
    code = run_jev(
        rows,
        os.path.join(HERE, "sample-c-rows-current.jsonl"),
        q_current,
        names_current,
        current["STATE_CONTEXT"],
    )
    if code:
        return code
    code = run_jev(
        rows,
        os.path.join(HERE, "sample-c-rows-v3.jsonl"),
        q_v3,
        names_v3,
        v3["STATE_CONTEXT"],
    )
    if code:
        return code
    return run_haiku(rows, os.path.join(HERE, "sample-c-rows-haiku.jsonl"), v3)


if __name__ == "__main__":
    raise SystemExit(main())
