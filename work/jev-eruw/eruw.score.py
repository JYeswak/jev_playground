import json
from collections import Counter

rows = [json.loads(l) for l in open("var/agent-tmp/eruw.live.jsonl") if l.strip()]
print("rows:", len(rows))
print("status:", Counter(r.get("status") for r in rows))
ok = [r for r in rows if r.get("status") == "ok" and r.get("valid")]
print("valid:", len(ok))
acc = sum(1 for r in ok if r["choice"] == r["answer"]) / len(ok)
print(
    "accuracy: %d/%d = %.4f (bar 0.758)"
    % (sum(1 for r in ok if r["choice"] == r["answer"]), len(ok), acc)
)
# by kind: need kinds from items
items = json.load(open("var/agent-tmp/eruw.items.json"))["test"]
kindacc = Counter()
kindn = Counter()
for r in ok:
    it = items[r["n"]]
    kindn[it["kind"]] += 1
    if r["choice"] == r["answer"]:
        kindacc[it["kind"]] += 1
for k in kindn:
    print(" %s: %d/%d = %.4f" % (k, kindacc[k], kindn[k], kindacc[k] / kindn[k]))
# picks precision: when choice != none, how often right
picks = [r for r in ok if r["choice"] != "none"]
print(
    "pick precision: %d/%d = %.4f"
    % (
        sum(1 for r in picks if r["choice"] == r["answer"]),
        len(picks),
        sum(1 for r in picks if r["choice"] == r["answer"]) / len(picks)
        if picks
        else 0,
    )
)
tok = sum((r.get("input_tokens") or 0) for r in rows)
print("input tokens:", tok, "spend: %.5f" % (tok * 0.042 / 1e6))
lat = sorted(r.get("latency_ms", 0) for r in ok)
print("p50 latency: %dms" % lat[len(lat) // 2])
print("choice dist:", Counter(r["choice"] == "none" for r in ok))
