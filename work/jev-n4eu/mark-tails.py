import json

for name in ("webscreen-shadow", "injection-shadow", "memory-filter"):
    rows = [
        json.loads(line)
        for line in open(f"/Users/josh/.local/state/jev/{name}.jsonl")
        if line.strip()
    ]
    print(name, len(rows), rows[-1].get("ts"))
