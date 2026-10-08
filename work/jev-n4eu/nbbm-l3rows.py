import json

rows = [
    json.loads(line)
    for line in open("/Users/josh/.local/state/jev/gate-observe.jsonl")
    if line.strip()
]
needle_a = "deleteme"
needle_b = "rm -rf /"
hits = []
for r in rows:
    cmd = str(r.get("cmd", ""))
    if needle_a in cmd or cmd.strip() == 'echo "' + needle_b + '"':
        hits.append(r)
print(len(hits))
for r in hits[-6:]:
    print(r.get("ts"), r.get("status"), r.get("screen"), r.get("model"), str(r.get("cmd"))[:60])
