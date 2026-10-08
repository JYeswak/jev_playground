import json
from collections import Counter

for name in ("webscreen-shadow", "injection-shadow", "memory-filter"):
    rows = [
        json.loads(line)
        for line in open(f"/Users/josh/.local/state/jev/{name}.jsonl")
        if line.strip()
    ]
    new = [r for r in rows if r.get("ts", "") >= "2026-10-02T03:40:39"]
    print(name, len(new), Counter((r.get("status"), r.get("model")) for r in new))
