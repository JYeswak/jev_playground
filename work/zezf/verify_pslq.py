import json
from collections import Counter

rows = [json.loads(l) for l in open("work/zezf/h3h4held.jsonl") if l.strip()]
print("rows:", len(rows), Counter((r["design"], r["status"]) for r in rows))
for d in ["h3", "h4"]:
    sub = [r for r in rows if r["design"] == d and r["status"] == "scored"]
    tp = sum(1 for r in sub if r["pred"] == "long" and r["label"] == "pos")
    fp = sum(1 for r in sub if r["pred"] == "long" and r["label"] == "neg")
    fn = sum(1 for r in sub if r["pred"] == "short" and r["label"] == "pos")
    rec = tp / (tp + fn) if tp + fn else 0
    prec = tp / (tp + fp) if tp + fp else 0
    print(
        "%s: n=%d TP=%d FP=%d FN=%d recall=%.4f prec=%.4f (bar rec>=0.40 prec>=0.20)"
        % (d, len(sub), tp, fp, fn, rec, prec)
    )
tok = sum(((r.get("usage") or {}).get("input_tokens") or 0) for r in rows)
print("held tokens:", tok)
dev = [json.loads(l) for l in open("work/zezf/h3h4dev.jsonl") if l.strip()]
print("dev rows:", len(dev), Counter((r["design"], r["status"]) for r in dev))
dtok = sum(((r.get("usage") or {}).get("input_tokens") or 0) for r in dev)
print("dev tokens:", dtok, "total spend: %.5f" % ((tok + dtok) * 0.042 / 1e6))
