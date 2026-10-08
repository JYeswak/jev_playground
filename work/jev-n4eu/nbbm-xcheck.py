import json

rows = [
    json.loads(line)
    for line in open("var/agent-tmp/syje.51150/planted-rows.jsonl")
    if line.strip()
]
print("rows:", len(rows))
for r in rows:
    print(r["model"], "flag=" + str(r["flag"]), repr(r["cmd"][:60]))
