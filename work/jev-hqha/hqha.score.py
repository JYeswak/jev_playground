import json

cut = json.load(open("var/agent-tmp/hqha.cut.json"))["cut"]
rows = [json.loads(l) for l in open("var/agent-tmp/hqha.held.jsonl") if l.strip()]
ok = [r for r in rows if r.get("noul") is not None]
print("held: %d/%d valid, cut=%.2f" % (len(ok), len(rows), cut))
tp = sum(1 for r in ok if r["noul"] >= cut and r["label"] == 1)
fp = sum(1 for r in ok if r["noul"] >= cut and r["label"] == 0)
fn = sum(1 for r in ok if r["noul"] < cut and r["label"] == 1)
tn = sum(1 for r in ok if r["noul"] < cut and r["label"] == 0)
prec = tp / (tp + fp) if tp + fp else 0
rec = tp / (tp + fn) if tp + fn else 0
f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0
print(
    "held: tp=%d fp=%d fn=%d tn=%d prec=%.4f rec=%.4f F1=%.4f (bar F1>=0.50 rec>=0.50, regex 0.162)"
    % (tp, fp, fn, tn, prec, rec, f1)
)
tok = sum((r.get("input_tokens") or 0) for r in rows)
print("held tokens:", tok)
