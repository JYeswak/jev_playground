#!/usr/bin/env python3
"""Live Noul action-prediction (jev-giqu candidate B). Bounded: 98 calls."""

from __future__ import annotations
import json, os, sys, time, urllib.request

MODEL = "jev-1.13.0"
URL = "https://api.typesafe.ai/v1/systemone"
TIMEOUT_S = 20
SCRATCH = os.path.dirname(os.path.abspath(__file__))
ITEMS = os.path.join(SCRATCH, "giqu.items.json")
LIVE = os.path.join(SCRATCH, "giqu.live.jsonl")
INSTRUCTIONS = (
    "You triage flagged shell commands. ACT means the engineer will need "
    "to act on this command's target within minutes: edit the same file, "
    "re-run a modified retry, or revert it. IGNORE means the flag is "
    "informational and no follow-up touches the target."
)
CRITERIA = {
    "true": "Follow-up action on the target is likely.",
    "false": "No follow-up on the target.",
}


def main():
    key = os.environ.get("TYPESAFE_API_KEY", "")
    if not key:
        print("NOT_RUN: no key")
        return 2
    items = json.load(open(ITEMS))
    done = set()
    if os.path.exists(LIVE):
        for l in open(LIVE):
            try:
                done.add(json.loads(l)["n"])
            except Exception:
                pass
    todo = [(n, it) for n, it in enumerate(items) if n not in done]
    print(f"items={len(items)} done={len(done)} todo={len(todo)}", flush=True)
    n_calls = 0
    with open(LIVE, "a") as fh:
        for n, it in todo:
            body = json.dumps(
                {
                    "model": MODEL,
                    "state": {"command": it["cmd"][:800]},
                    "questions": {
                        "act": {
                            "type": "noul",
                            "instructions": INSTRUCTIONS,
                            "criteria": CRITERIA,
                        }
                    },
                }
            ).encode()
            req = urllib.request.Request(
                URL,
                data=body,
                headers={
                    "Authorization": "Bearer " + key,
                    "Content-Type": "application/json",
                },
            )
            t0 = time.time()
            try:
                with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
                    payload = json.loads(resp.read().decode())
            except Exception as e:
                s = str(e)
                if "401" in s or "402" in s or "403" in s:
                    print("STOP auth")
                    break
                fh.write(
                    json.dumps({"n": n, "label": it["tight"], "status": "error"}) + "\n"
                )
                fh.flush()
                continue
            lat = int((time.time() - t0) * 1000)
            try:
                ans = payload["answers"]["act"]
                nl = float(ans["noul"])
                assert 0.0 <= nl <= 1.0
                valid = True
            except Exception:
                nl, valid = 0.0, False
            usage = payload.get("usage", {})
            fh.write(
                json.dumps(
                    {
                        "n": n,
                        "label": it["tight"],
                        "status": "ok",
                        "noul": nl,
                        "valid": valid,
                        "input_tokens": usage.get("input_tokens"),
                        "latency_ms": lat,
                    }
                )
                + "\n"
            )
            fh.flush()
            n_calls += 1
    print(f"calls_this_run={n_calls}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
