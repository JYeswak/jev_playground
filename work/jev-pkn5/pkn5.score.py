import json

cut = json.load(open("var/agent-tmp/pkn5.cut.json"))["cut"]
rows = [json.loads(l) for l in open("var/agent-tmp/pkn5.held.live.jsonl") if l.strip()]
ok = [r for r in rows if r.get("noul") is not None]
print("held: %d/%d cut=%.2f" % (len(ok), len(rows), cut))
tp = sum(1 for r in ok if r["noul"] >= cut and r["label"] == 1)
fp = sum(1 for r in ok if r["noul"] >= cut and r["label"] == 0)
fn = sum(1 for r in ok if r["noul"] < cut and r["label"] == 1)
tn = sum(1 for r in ok if r["noul"] < cut and r["label"] == 0)
prec = tp / (tp + fp) if tp + fp else 0
rec = tp / (tp + fn) if tp + fn else 0
acc = (tp + tn) / len(ok)
print(
    "tp=%d fp=%d fn=%d tn=%d prec=%.4f rec=%.4f acc=%.4f (bar acc>=0.85 rec>=0.40; base 0.807/0.069)"
    % (tp, fp, fn, tn, prec, rec, acc)
)
tok = sum((r.get("input_tokens") or 0) for r in rows)
print("tokens:", tok)
