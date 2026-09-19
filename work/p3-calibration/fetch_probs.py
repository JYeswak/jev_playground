"""Fetch keep-probabilities for sampled tool calls (LIVE, budgeted, run once).

One system_one request per batch of calls; each call contributes the library's
two noul questions (keep the call, keep the result verbatim) with the library's
own instruction wording (fast-jev-compaction/src/compact.ts questionsFor).
State per call is call-local (tool + input + truncated result), NOT the full
transcript window the library uses -- disclosed in the receipt; thresholds sweep
offline over these cached probs, so all arms share the same judgments.

Usage: TYPESAFE_API_KEY=... uv run --python 3.12 --with <sdk-dir> python fetch_probs.py
Writes probs.jsonl: {id, session, tool, result_chars, keep_call, keep_result}.
"""

import json
import sys
import time

BATCH_CALLS = 1

from typesafe_sdk import Noul, RetryPolicy, TypeSafeClient

SESSIONS = ["grokbot", "harvest", "orch"]


def load_all():
    out = []
    for s in SESSIONS:
        with open(f"cand-{s}.jsonl") as fh:
            for line in fh:
                d = json.loads(line)
                d["session"] = s
                out.append(d)
    return out


def state_of(c):
    return {
        "task": c.get("task_context", "")[:4000],
        "tool": c["tool"],
        "input": json.dumps(c["arguments"])[:2000],
        "result": c["result_text"][:4000],
    }


def main():
    calls = load_all()
    print(f"calls={len(calls)} sessions={SESSIONS}", flush=True)
    client = TypeSafeClient(
        retry=RetryPolicy(
            max_retries=3, timeout=60.0, http_statuses={429, 500, 502, 503, 504}
        )
    )
    n_req, t0, model_seen = 0, time.time(), set()
    with open("probs.jsonl", "w") as out:
        for i in range(0, len(calls), BATCH_CALLS):
            batch = calls[i : i + BATCH_CALLS]
            # One request per batch: the state is the LIST of this batch's call
            # states, questions namespaced per index. Cross-talk (judging call i
            # against state j) is possible; instructions pin the call identity and
            # the deviation is disclosed in the receipt.
            state = []
            questions = {}
            for j, c in enumerate(batch):
                state.append({"idx": j, **state_of(c)})
                questions[f"call_{j}"] = Noul(
                    instructions=(
                        f"Tool call idx {j} ({c['tool']}) should stay in the history: "
                        "knowing this call was made, with its input, still matters "
                        "for what the assistant does next"
                    )
                )
                questions[f"result_{j}"] = Noul(
                    instructions=(
                        f"The full output of tool call idx {j} ({c['tool']}, "
                        f"{c['result_chars']} chars) should stay in the history verbatim: "
                        "the assistant still needs its contents and re-running "
                        "the tool would not do"
                    )
                )
            resp = client.system_one(state, questions, model="jev-latest")
            model_seen.add(resp.model)
            n_req += 1
            for j, c in enumerate(batch):
                ans = resp.answers
                out.write(
                    json.dumps(
                        {
                            "id": c["id"],
                            "session": c["session"],
                            "tool": c["tool"],
                            "result_chars": c["result_chars"],
                            "keep_call": ans[f"call_{j}"].noul,
                            "keep_result": ans[f"result_{j}"].noul,
                        }
                    )
                    + "\n"
                )
            out.flush()
            print(f"batch done: reqs={n_req} elapsed={time.time()-t0:.0f}s", flush=True)
    print(f"requests={n_req} models={sorted(model_seen)} elapsed={time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
