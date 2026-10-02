#!/usr/bin/env python3
"""Live jev-1.13.0 dup-discriminate run (bead jev-eruw). Bounded: 292 calls max."""

from __future__ import annotations
import json, os, sys, time, urllib.request

MODEL = "jev-1.13.0"
URL = "https://api.typesafe.ai/v1/systemone"
MAX_CALLS = 292
TIMEOUT_S = 25
PRICE_PER_M = 0.042
SCRATCH = os.path.dirname(os.path.abspath(__file__))
ITEMS = os.path.join(SCRATCH, "eruw.items.json")
LIVE = os.path.join(SCRATCH, "eruw.live.jsonl")

INSTRUCTIONS = (
    "You judge whether a newly filed task bead duplicates an existing bead. "
    "DUPLICATE means the same work: same bug, same feature, same acceptance, "
    "already tracked. RELATED BUT DISTINCT means similar words, different work: "
    "different bug, different scope, different acceptance. "
    "Choose the existing bead that tracks the SAME work, or none if no candidate does."
)

_DESC_CACHE = {}


def desc(repo, i):
    if repo not in _DESC_CACHE:
        idx = {}
        try:
            for line in open(
                "/Users/josh/Developer/%s/.beads/issues.jsonl" % repo,
                encoding="utf-8",
                errors="replace",
            ):
                try:
                    x = json.loads(line)
                except Exception:
                    continue
                if x.get("id"):
                    t = x.get("title", "")
                    d = ""
                    for k in ("description", "body", "text"):
                        v = x.get(k)
                        if isinstance(v, str) and v.strip():
                            d = v
                            break
                    idx[x["id"]] = (t + "\n" + d)[:600] if d else t[:600]
        except Exception:
            pass
        _DESC_CACHE[repo] = idx
    return _DESC_CACHE[repo].get(i, "")


def main():
    key = os.environ.get("TYPESAFE_API_KEY", "")
    if not key:
        print("NOT_RUN: no key")
        return 2
    items = json.load(open(ITEMS))["test"]
    done = set()
    if os.path.exists(LIVE):
        for l in open(LIVE):
            try:
                done.add(json.loads(l)["n"])
            except Exception:
                pass
    todo = [(n, it) for n, it in enumerate(items) if n not in done]
    print(f"items={len(items)} done={len(done)} todo={len(todo)}")
    n_calls = 0
    with open(LIVE, "a") as fh:
        for n, it in todo:
            if n_calls >= MAX_CALLS:
                break
            state = {
                "new_bead": (it["dup_title"] + "\n" + desc(it["repo"], it["dup"]))[:800]
            }
            crit = {}
            for k, (cid, ctitle) in enumerate(it["cands"]):
                skey = "candidate_%d" % (k + 1)
                state[skey] = (ctitle + "\n" + desc(it["repo"], cid))[:600]
                crit[cid] = (
                    "Choose this iff %s (titled '%s') tracks the SAME work as new_bead."
                    % (skey, ctitle[:80])
                )
            crit["none"] = (
                "Choose this iff no candidate tracks the same work (related but distinct)."
            )
            q = {"type": "choice", "instructions": INSTRUCTIONS, "criteria": crit}
            body = json.dumps(
                {"model": MODEL, "state": state, "questions": {"dup": q}}
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
                    json.dumps({"n": n, "answer": it["answer"], "status": "error"})
                    + "\n"
                )
                fh.flush()
                continue
            lat = int((time.time() - t0) * 1000)
            try:
                ans = payload["answers"]["dup"]
                ch, conf, probs = (
                    ans["choice"],
                    float(ans["confidence"]),
                    ans["probabilities"],
                )
                assert (
                    ch in crit
                    and abs(sum(probs.values()) - 1.0) <= 0.05
                    and probs[ch] == max(probs.values())
                )
                valid = True
            except Exception:
                ch, conf, valid = None, 0.0, False
            usage = payload.get("usage", {})
            fh.write(
                json.dumps(
                    {
                        "n": n,
                        "answer": it["answer"],
                        "status": "ok",
                        "choice": ch,
                        "confidence": conf,
                        "valid": valid,
                        "input_tokens": usage.get("input_tokens"),
                        "latency_ms": lat,
                    }
                )
                + "\n"
            )
            fh.flush()
            n_calls += 1
    print(f"calls_this_run={n_calls}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
