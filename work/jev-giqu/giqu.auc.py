import json

items = json.load(open("var/agent-tmp/giqu.items.json"))
want = {}
for it in items:
    want[(it["ts"], it["sess"])] = it["tight"]
scored = []
for line in open(
    "/Users/josh/.local/state/jev/gate-observe.jsonl",
    encoding="utf-8",
    errors="replace",
):
    try:
        r = json.loads(line)
    except Exception:
        continue
    if not r.get("flag"):
        continue
    k = (r.get("ts"), (r.get("session") or "")[:8])
    if k in want:
        np_ = r.get("nimbleProbs") or {}
        m = max(np_.values()) if np_ else 0
        scored.append((m, 1 if want[k] == "act" else 0))
print("joined:", len(scored))
import itertools

pos = [s for s, y in scored if y == 1]
neg = [s for s, y in scored if y == 0]
auc = sum(1 for a, b in itertools.product(pos, neg) if a > b) / (len(pos) * len(neg))
print("nimble-maxprob AUC=%.4f pos=%d neg=%d" % (auc, len(pos), len(neg)))
import statistics

print("pos med=%.4f neg med=%.4f" % (statistics.median(pos), statistics.median(neg)))
