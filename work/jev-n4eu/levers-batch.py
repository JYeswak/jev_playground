import json
from collections import Counter

rows = [
    json.loads(line)
    for line in open("/Users/josh/.local/state/jev/gate-observe.jsonl")
    if line.strip()
]
cap = [r for r in rows if r.get("error") == "NOT_RUN reason=daily-cap"]
print("cap sessions:", Counter(str(r.get("session", "?"))[:8] for r in cap).most_common(5))
print("cap has screen key:", Counter("screen" in r for r in cap))
print("cap hours today:", Counter(r.get("ts", "")[:13] for r in cap if r.get("ts", "").startswith("2026-10-01")).most_common(5))

ws = [
    json.loads(line)
    for line in open("/Users/josh/.local/state/jev/webscreen-shadow.jsonl")
    if line.strip()
]
recent = [r for r in ws if r.get("ts", "") >= "2026-09-25"]
print("ws 7d:", len(recent), Counter(r.get("status") for r in recent))

ij = [
    json.loads(line)
    for line in open("/Users/josh/.local/state/jev/injection-shadow.jsonl")
    if line.strip()
]
recent2 = [r for r in ij if r.get("ts", "") >= "2026-09-25"]
print("inj 7d:", len(recent2), Counter(r.get("status") for r in recent2))

mf = [
    json.loads(line)
    for line in open("/Users/josh/.local/state/jev/memory-filter.jsonl")
    if line.strip()
]
recent3 = [r for r in mf if r.get("ts", "") >= "2026-09-25"]
print("mem 7d:", len(recent3), Counter(r.get("status") for r in recent3))
saved = sum(r.get("tokensSaved", 0) for r in recent3)
paid_in = sum((r.get("inputTokens") or 0) for r in recent3 if r.get("status") == "scored")
print("tokensSaved:", saved, "scored in-tok:", paid_in)
