import json

met = json.load(open("var/agent-tmp/ab.metered.json"))
want = {}
for o in met:
    if o.get("sid"):
        want[o["sid"]] = o["arm"]
print("want:", len(want))
hit = {"ON": 0, "OFF": 0}
flag = {"ON": 0, "OFF": 0}
for line in open(
    "/Users/josh/.local/state/jev/gate-observe.jsonl",
    encoding="utf-8",
    errors="replace",
):
    try:
        r = json.loads(line)
    except Exception:
        continue
    s = (r.get("session") or "")[:8]
    if s in want:
        hit[want[s]] += 1
        if r.get("flag"):
            flag[want[s]] += 1
print("gate rows by arm:", hit, "flagged:", flag)
