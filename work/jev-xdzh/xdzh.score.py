import json

rows = [json.loads(l) for l in open("var/agent-tmp/xdzh.live.jsonl") if l.strip()]
ok = [r for r in rows if r.get("status") == "ok" and r.get("valid")]
print("rows=%d valid=%d" % (len(rows), len(ok)))
acc = sum(1 for r in ok if r["pred"] == r["label"]) / len(ok)
ri = [r for r in ok if r["label"] == "ign"]
rec = sum(1 for r in ri if r["pred"] == "ign") / len(ri)
print("acc=%.4f (bar 0.80) recall_ign=%.4f (bar 0.60) n_ign=%d" % (acc, rec, len(ri)))
from collections import Counter

print(Counter((r["pred"], r["label"]) for r in ok))
tok = sum((r.get("input_tokens") or 0) for r in rows)
print("tokens:", tok, "spend: %.5f" % (tok * 0.042 / 1e6))
