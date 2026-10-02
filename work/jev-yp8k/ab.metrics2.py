import json, sys

f = (
    sys.argv[1]
    if len(sys.argv) > 1
    else "/Users/josh/.omp/agent/sessions/-Developer-jev/2026-10-02T06-10-12-473Z_01a0fb3c-0f79-7431-bbe7-15e043e5ca0f.jsonl"
)
from collections import Counter

types = Counter()
tools = Counter()
tin = tout = 0
think = None
nmsg = 0
model = None
for line in open(f, encoding="utf-8", errors="replace"):
    try:
        r = json.loads(line)
    except Exception:
        continue
    t = r.get("type")
    types[t] += 1
    if t == "message":
        m = r.get("message", {})
        nmsg += 1
        if m.get("role") == "assistant":
            model = model or m.get("model")
            u = m.get("usage") or {}
            tin += u.get("input", 0) or 0
            tout += u.get("output", 0) or 0
        c = m.get("content")
        if isinstance(c, list):
            for b in c:
                if isinstance(b, dict) and b.get("type") == "toolCall":
                    tools[b.get("name", "?")] += 1
    if t == "thinking_level_change":
        think = (r.get("thinkingLevel"), r.get("configured"))
    if t == "model_usage" and r.get("role") == "typesafe":
        pass
print("model:", model, "msgs:", nmsg, "think:", think)
print("main in/out:", tin, tout)
print("tools:", dict(tools))
