#!/usr/bin/env python3
"""Live foreign-risky-dep Noul (jev-pkn5). Phase dev (cut fit) then held."""

from __future__ import annotations
import json, os, sys, time, urllib.request

MODEL = "jev-1.13.0"
URL = "https://api.typesafe.ai/v1/systemone"
TIMEOUT_S = 20
SCRATCH = os.path.dirname(os.path.abspath(__file__))
INSTRUCTIONS = (
    "A developer added a dependency to a manifest. RISKY means the addition "
    "looks foreign to the project's supply chain: a typosquat-like name, an "
    "unpinned git URL or branch, a new registry, an install script, or an "
    "unversioned latest tag. CLEAN means a versioned registry dependency with "
    "an ordinary name."
)
CRITERIA = {
    "true": "The addition looks foreign-risky.",
    "false": "The addition looks routine.",
}


def ask(key, text):
    body = json.dumps(
        {
            "model": MODEL,
            "state": {"addition": text[:500]},
            "questions": {
                "risk": {
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
        nl = float(payload["answers"]["risk"]["noul"])
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
    mode = sys.argv[1]
    items = json.load(open(os.path.join(SCRATCH, "pkn5.%s.json" % mode)))
    outp = os.path.join(SCRATCH, "pkn5.%s.live.jsonl" % mode)
    done = set()
    if os.path.exists(outp):
        for l in open(outp):
            try:
                done.add(json.loads(l)["n"])
            except Exception:
                pass
    calls = 0
    with open(outp, "a") as fh:
        for n, it in enumerate(items):
            if n in done:
                continue
            text = "%s: %s@%s (%s)" % (it["repo"], it["name"], it["ver"], it["file"])
            r, c = ask(key, text)
            if r == "STOP":
                print("STOP auth")
                break
            calls += c
            fh.write(
                json.dumps(
                    {
                        "n": n,
                        "label": 1 if it["removed_later"] else 0,
                        **(r or {"noul": None}),
                    }
                )
                + "\n"
            )
            fh.flush()
    print(f"calls_this_run={calls}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
