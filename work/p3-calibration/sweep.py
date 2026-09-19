"""Sweep keep thresholds offline over cached keep-probs (no network, no key).

Oracle for 'needed later' (PROXY, not ground truth): novel tokens from the tool
result — lowercase alnum tokens len>=5 present in the result but absent from all
earlier assistant text — reappearing in later assistant text. A dropped result
with >=1 such token counts one retention mistake.

Retention rule mirrors the library (decideCall on the result answer): drop the
result iff keep_result < t. Call-text retention is out of scope; result bytes
dominate, disclosed in the receipt.

Usage: python sweep.py  (reads cand-*.jsonl + probs.jsonl, prints table)
"""

import json
import re

SESSIONS = ["grokbot", "harvest", "orch"]
TOKEN = re.compile(r"[a-z0-9]{5,}")


def toks(text):
    return set(TOKEN.findall(text.lower()))


def main():
    cands = {}
    for s in SESSIONS:
        with open(f"cand-{s}.jsonl") as fh:
            for line in fh:
                d = json.loads(line)
                d["session"] = s
                cands[d["id"]] = d
    probs = {}
    with open("probs.jsonl") as fh:
        for line in fh:
            d = json.loads(line)
            probs[d["id"]] = d
    rows = []
    for cid, c in cands.items():
        p = probs.get(cid)
        if p is None:
            continue
        novel = toks(c["result_text"]) - toks(c.get("earlier_text", ""))
        hit = novel & toks(c.get("later_text", ""))
        rows.append(
            {
                "session": c["session"],
                "tool": c["tool"],
                "chars": c["result_chars"],
                "p": p["keep_result"],
                "novel": len(novel),
                "needed": len(hit) > 0,
                "hits": len(hit),
            }
        )
    print(
        f"n={len(rows)} sessions="
        + ",".join(f"{s}={sum(1 for r in rows if r['session']==s)}" for s in SESSIONS)
    )
    print("t kept dropped mistakes mist_rate bytes_saved mist_per_10KB")
    for k in range(0, 11):
        t = k / 10
        kept = [r for r in rows if r["p"] >= t]
        dropped = [r for r in rows if r["p"] < t]
        mist = [r for r in dropped if r["needed"]]
        saved = sum(r["chars"] for r in dropped)
        rate = len(mist) / len(dropped) if dropped else 0.0
        mpkb = len(mist) / (saved / 10240) if saved else 0.0
        print(
            f"{t:.1f} {len(kept):4d} {len(dropped):4d} {len(mist):4d} "
            f"{rate:.3f} {saved:9d} {mpkb:.3f}"
        )
    # oracle sanity: what fraction of results does the oracle call needed at all?
    print(f"oracle-needed-rate={[r['needed'] for r in rows].count(True)}/{len(rows)}")


if __name__ == "__main__":
    main()
