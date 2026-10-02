import json

rows = [json.loads(l) for l in open("var/agent-tmp/pkn5.dev.live.jsonl") if l.strip()]
ok = [r for r in rows if r.get("noul") is not None]
print("dev: %d/%d" % (len(ok), len(rows)))
best = None
for i in range(0, 101):
    cut = i / 100
    tp = sum(1 for r in ok if r["noul"] >= cut and r["label"] == 1)
    fp = sum(1 for r in ok if r["noul"] >= cut and r["label"] == 0)
    fn = sum(1 for r in ok if r["noul"] < cut and r["label"] == 1)
    prec = tp / (tp + fp) if tp + fp else 0
    rec = tp / (tp + fn) if tp + fn else 0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0
    if best is None or f1 > best[0]:
        best = (f1, cut, prec, rec)
print("dev best: F1=%.4f cut=%.2f prec=%.3f rec=%.3f" % best)
json.dump({"cut": best[1]}, open("var/agent-tmp/pkn5.cut.json", "w"))
