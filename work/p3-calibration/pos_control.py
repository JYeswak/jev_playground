"""Positive control: can this harness detect signal at all? (LIVE, budgeted, once).

Same sessions, same single-request batching, same SDK path as fetch_probs.py.
Two deterministic-label questions per tool result:
  err:  is this result an error/failure message (regex truth, 58/150)?
  read: did this call read a file (toolName == read, 23/150)?
AUC of Jev's p against each deterministic label, via the same AUC code used for
keep_p-vs-needed. Run from work/pysdk for the pinned env:
  cd work/pysdk && uv run python ../p3-calibration/pos_control.py
Writes ../p3-calibration/control_probs.jsonl.
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from typesafe_sdk import Noul, RetryPolicy, TypeSafeClient  # noqa: E402

SESSIONS = ["grokbot", "harvest", "orch"]
ERR = re.compile(r"error|failed|exit status|traceback|rc=[1-9]|Traceback|FAILED|Error:")


def auc(scores, labels):
    pos = [s for s, l in zip(scores, labels) if l]
    neg = [s for s, l in zip(scores, labels) if not l]
    if not pos or not neg:
        return float("nan")
    wins = ties = 0
    for p in pos:
        for n in neg:
            if p > n:
                wins += 1
            elif p == n:
                ties += 1
    return (wins + 0.5 * ties) / (len(pos) * len(neg))


def main():
    calls = []
    for s in SESSIONS:
        with open(f"cand-{s}.jsonl") as fh:
            for line in fh:
                d = json.loads(line)
                d["session"] = s
                calls.append(d)
    client = TypeSafeClient(
        retry=RetryPolicy(
            max_retries=3, timeout=60.0, http_statuses={429, 500, 502, 503, 504}
        )
    )
    n_req, model_seen = 0, set()
    with open("control_probs.jsonl", "w") as out:
        for c in calls:
            state = {
                "tool": c["tool"],
                "input": json.dumps(c["arguments"])[:2000],
                "result": c["result_text"][:4000],
            }
            q = {
                "err": Noul(
                    instructions=(
                        "This tool result is an error or failure message: it reports "
                        "an error, a failure, a traceback, or a nonzero exit status."
                    )
                ),
                "read": Noul(
                    instructions=(
                        "This tool call reads a file: its tool is a file-reading "
                        "operation such as reading a file from disk."
                    )
                ),
            }
            resp = client.system_one(state, q, model="jev-latest")
            model_seen.add(resp.model)
            n_req += 1
            out.write(
                json.dumps(
                    {
                        "id": c["id"],
                        "session": c["session"],
                        "p_err": resp.answers["err"].noul,
                        "p_read": resp.answers["read"].noul,
                    }
                )
                + "\n"
            )
            out.flush()
    print(f"requests={n_req} models={sorted(model_seen)}")
    # score offline (same code paths as the sweep)
    labels_err, labels_read, pe, pr, pk, need = [], [], [], [], [], []
    probs = {}
    with open("probs.jsonl") as fh:
        for line in fh:
            d = json.loads(line)
            probs[d["id"]] = d["keep_result"]
    tok = re.compile(r"[a-z0-9]{5,}")
    for c in calls:
        t = lambda s: set(tok.findall(s.lower()))
        labels_err.append(bool(ERR.search(c["result_text"])) or c["is_error"])
        labels_read.append(c["tool"] == "read")
        need.append(
            len(
                (t(c["result_text"]) - t(c.get("earlier_text", "")))
                & t(c.get("later_text", ""))
            )
            > 0
        )
    cp = [json.loads(l) for l in open("control_probs.jsonl")]
    pe = [r["p_err"] for r in cp]
    pr = [r["p_read"] for r in cp]
    pk = [probs[c["id"]] for c in calls]
    print(f"err:  AUC={auc(pe, labels_err):.3f} n_pos={sum(labels_err)}/{len(calls)}")
    print(f"read: AUC={auc(pr, labels_read):.3f} n_pos={sum(labels_read)}/{len(calls)}")
    print(f"keep-vs-needed: AUC={auc(pk, need):.3f} n_pos={sum(need)}/{len(calls)}")


if __name__ == "__main__":
    main()
