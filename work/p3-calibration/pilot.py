"""Pilot: 6 enriched single-request judgments (LIVE, tiny)."""

import json
import sys

sys.path.insert(0, ".")
from fetch_probs import load_all, state_of
from typesafe_sdk import Noul, RetryPolicy, TypeSafeClient

calls = load_all()
pilot = []
for s in ["grokbot", "harvest", "orch"]:
    pilot += [c for c in calls if c["session"] == s][:2]
client = TypeSafeClient(
    retry=RetryPolicy(
        max_retries=2, timeout=60.0, http_statuses={429, 500, 502, 503, 504}
    )
)
for c in pilot:
    q = {
        "call": Noul(
            instructions=f"Tool call ({c['tool']}) should stay in the history: knowing this call was made, with its input, still matters for what the assistant does next"
        ),
        "result": Noul(
            instructions=f"The full output of this tool call ({c['tool']}, {c['result_chars']} chars) should stay in the history verbatim: the assistant still needs its contents and re-running the tool would not do"
        ),
    }
    r = client.system_one(state_of(c), q, model="jev-latest")
    print(
        c["session"],
        c["tool"],
        "call=",
        round(r.answers["call"].noul, 3),
        "result=",
        round(r.answers["result"].noul, 3),
        "model=",
        r.model,
    )
