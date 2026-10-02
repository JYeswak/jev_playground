#!/usr/bin/env python3
"""Live error-triage Noul (jev-hqha C2v2). Dev cut fit then held eval."""

from __future__ import annotations
import json, os, sys, time, urllib.request

MODEL = "jev-1.13.0"
URL = "https://api.typesafe.ai/v1/systemone"
TIMEOUT_S = 20
SCRATCH = os.path.dirname(os.path.abspath(__file__))
INSTRUCTIONS = "Does this tool output indicate the action failed? FAIL means errors, failures, timeouts, denials, crashes, or nonzero-exit evidence in the text. OK means success output, listings, or benign text."
CRITERIA = {
    "true": "The output shows failure.",
    "false": "The output shows success or benign text.",
}


def ask(key, text):
    body = json.dumps(
        {
            "model": MODEL,
            "state": {"output": text[:600]},
            "questions": {
                "fail": {
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
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
    )
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
            payload = json.loads(resp.read().decode())
    except Exception as e:
        s = str(e)
        if "401" in s or "402" in s or "403" in s:
            return ("STOP", 0)
        return (None, 0)
    lat = int((time.time() - t0) * 1000)
    try:
        ans = payload["answers"]["fail"]
        nl = float(ans["noul"])
        assert 0.0 <= nl <= 1.0
    except Exception:
        return (None, 0)
    usage = payload.get("usage", {})
    return (
        {"noul": nl, "latency_ms": lat, "input_tokens": usage.get("input_tokens")},
        1,
    )


def main():
    key = os.environ.get("TYPESAFE_API_KEY", "")
    if not key:
        print("NOT_RUN: no key")
        return 2
    sample = json.load(open(os.path.join(SCRATCH, "hqha.errsample.json")))
    dev, held = sample[:120], sample[120:420]
    mode = sys.argv[1] if len(sys.argv) > 1 else "dev"
    rows = dev if mode == "dev" else held
    outp = os.path.join(SCRATCH, "hqha.%s.jsonl" % mode)
    done = set()
    if os.path.exists(outp):
        for l in open(outp):
            try:
                done.add(json.loads(l)["n"])
            except Exception:
                pass
    calls = 0
    with open(outp, "a") as fh:
        for n, it in enumerate(rows):
            if n in done:
                continue
            r, c = ask(key, it["t"])
            if r == "STOP":
                print("STOP auth")
                break
            calls += c
            fh.write(
                json.dumps(
                    {"n": n, "label": 1 if it["y"] else 0, **(r or {"noul": None})}
                )
                + "\n"
            )
            fh.flush()
    print(f"calls_this_run={calls}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
