#!/usr/bin/env python3
"""Measure think chars, tokens, cost per duel run from isolated session dirs."""

import json, glob, os, sys


def measure(sdir):
    think = 0
    tin = tout = 0
    cost = 0.0
    asst_texts = []
    files = glob.glob(os.path.join(sdir, "*.jsonl"))
    if not files:
        return None
    for f in files:
        fh = open(f, errors="replace")
        for line in fh:
            try:
                d = json.loads(line)
            except Exception:
                continue
            m = d.get("message")
            if not isinstance(m, dict):
                continue
            c = m.get("content")
            if isinstance(c, list):
                for p in c:
                    if not isinstance(p, dict):
                        continue
                    if p.get("type") == "thinking" and isinstance(
                        p.get("thinking"), str
                    ):
                        think += len(p["thinking"])
                    if (
                        p.get("type") == "text"
                        and isinstance(p.get("text"), str)
                        and m.get("role") == "assistant"
                    ):
                        asst_texts.append(p["text"])
            u = m.get("usage")
            if isinstance(u, dict):
                tin += u.get("input") or 0
                tout += u.get("output") or 0
                cc = u.get("cost")
                if isinstance(cc, dict):
                    cost += cc.get("total") or 0
                elif isinstance(cc, (int, float)):
                    cost += cc
        fh.close()
    return {
        "think_chars": think,
        "input": tin,
        "output": tout,
        "cost_usd": round(cost, 6),
        "answer": "\n".join(asst_texts)[-3000:],
    }


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else "work/thinking-duel/sessions"
    rows = {}
    for rid in sorted(os.listdir(root)):
        if not rid.startswith("p"):
            continue
        m = measure(os.path.join(root, rid))
        if m is not None:
            rows[rid] = m
    print(json.dumps(rows, indent=1)[:1500])
    print("... runs measured:", len(rows))
    json.dump(rows, open(os.path.join(root, "..", "metrics.json"), "w"), indent=1)
