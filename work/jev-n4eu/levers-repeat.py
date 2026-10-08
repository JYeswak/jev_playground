import json
from collections import Counter

ij = [
    json.loads(line)
    for line in open("/Users/josh/.local/state/jev/injection-shadow.jsonl")
    if line.strip()
]
recent = [r for r in ij if r.get("ts", "") >= "2026-09-25"]
print("cap rows:", sum(1 for r in recent if r.get("status") == "cap"))
print("cap by day:", Counter(r.get("ts", "")[:10] for r in recent if r.get("status") == "cap"))
scored = [r for r in recent if r.get("status") in ("scored", "cap")]
hashes = Counter(r.get("outputSha256") for r in scored if r.get("outputSha256"))
rep = sum(v - 1 for v in hashes.values() if v > 1)
print("scored+cap rows:", len(scored), "distinct hashes:", len(hashes), "repeat screenings:", rep)
mf = [
    json.loads(line)
    for line in open("/Users/josh/.local/state/jev/memory-filter.jsonl")
    if line.strip()
]
recent3 = [r for r in mf if r.get("ts", "") >= "2026-09-25"]
pairs = Counter((r.get("promptHash"), r.get("memoryHash")) for r in recent3 if r.get("status") in ("scored", "memo"))
rep3 = sum(v - 1 for v in pairs.values() if v > 1)
print("mem scored+memo rows:", sum(1 for r in recent3 if r.get("status") in ("scored", "memo")), "distinct pairs:", len(pairs), "repeats:", rep3)
