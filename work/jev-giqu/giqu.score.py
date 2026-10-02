import json, itertools

rows = [json.loads(l) for l in open("var/agent-tmp/giqu.live.jsonl") if l.strip()]
print("rows:", len(rows))
ok = [r for r in rows if r.get("status") == "ok" and r.get("valid")]
print("valid:", len(ok))
pos = [r["noul"] for r in ok if r["label"] == "act"]
neg = [r["noul"] for r in ok if r["label"] == "ignore"]
auc = sum(1 for a, b in itertools.product(pos, neg) if a > b) / (len(pos) * len(neg))
print("AUC=%.4f pos=%d neg=%d (bar 0.70, baseline 0.5455)" % (auc, len(pos), len(neg)))
for cut in [0.5]:
    tp = sum(1 for r in ok if r["noul"] >= cut and r["label"] == "act")
    fp = sum(1 for r in ok if r["noul"] >= cut and r["label"] == "ignore")
    print(
        "cut %.1f: recall %d/%d=%.3f prec %d/%d=%.3f"
        % (
            cut,
            tp,
            len(pos),
            tp / len(pos),
            tp,
            tp + fp,
            tp / (tp + fp) if tp + fp else 0,
        )
    )
tok = sum((r.get("input_tokens") or 0) for r in rows)
print("tokens:", tok, "spend: %.5f" % (tok * 0.042 / 1e6))
