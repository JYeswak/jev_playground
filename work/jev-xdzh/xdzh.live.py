#!/usr/bin/env python3
"""Live unaddressed-failure Noul (jev-xdzh). Bounded: 300 calls."""

from __future__ import annotations
import json, os, sys, time, urllib.request

MODEL = "jev-1.13.0"
URL = "https://api.typesafe.ai/v1/systemone"
TIMEOUT_S = 20
SCRATCH = os.path.dirname(os.path.abspath(__file__))
INSTRUCTIONS = (
    "A coding agent got a failed tool result, then took next steps. "
    "IGNORED means the next steps move on without addressing the failure: "
    "no retry, no fix, no edit of the failing target, no mention of the error. "
    "ADDRESSED means a retry, fix, target edit, or explicit handling."
)
CRITERIA = {
    "true": "The failure went unaddressed.",
    "false": "The failure was addressed.",
}


def main():
    key = os.environ.get("TYPESAFE_API_KEY", "")
    if not key:
        print("NOT_RUN: no key")
        return 2
    sample = json.load(open(os.path.join(SCRATCH, "xdzh.sample.json")))
    outp = os.path.join(SCRATCH, "xdzh.live.jsonl")
    done = set()
    if os.path.exists(outp):
        for l in open(outp):
            try:
                done.add(json.loads(l)["n"])
            except Exception:
                pass
    todo = [(n, it) for n, it in enumerate(sample) if n not in done]
    print(f"items={len(sample)} done={len(done)} todo={len(todo)}", flush=True)
    calls = 0
    with open(outp, "a") as fh:
        for n, it in todo:
            state = {"result": it["res"][:800], "next": it["nxt"][:600]}
            body = json.dumps(
                {
                    "model": MODEL,
                    "state": state,
                    "questions": {
                        "ign": {
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
                    json.dumps(
                        {
                            "n": n,
                            "label": "ign" if not it["addr"] else "addr",
                            "status": "error",
                        }
                    )
                    + "\n"
                )
                fh.flush()
                continue
            lat = int((time.time() - t0) * 1000)
            try:
                nl = float(payload["answers"]["ign"]["noul"])
                assert 0.0 <= nl <= 1.0
                valid = True
            except Exception:
                nl, valid = 0.0, False
            usage = payload.get("usage", {})
            fh.write(
                json.dumps(
                    {
                        "n": n,
                        "label": "ign" if not it["addr"] else "addr",
                        "status": "ok",
                        "noul": nl,
                        "pred": "ign" if (valid and nl >= 0.5) else "addr",
                        "valid": valid,
                        "input_tokens": usage.get("input_tokens"),
                        "latency_ms": lat,
                    }
                )
                + "\n"
            )
            fh.flush()
            calls += 1
    print(f"calls_this_run={calls}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
