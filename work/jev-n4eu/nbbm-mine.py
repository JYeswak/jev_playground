import json

rows = [
    json.loads(line)
    for line in open("/Users/josh/.local/state/jev/gate-observe.jsonl")
    if line.strip()
]
mine = [r for r in rows if str(r.get("session", "")).startswith("01a0fa4")]
print("my rpc gate rows:", len(mine))
for r in mine[-8:]:
    print(r.get("ts"), r.get("status"), r.get("screen"), str(r.get("cmd"))[:50])
