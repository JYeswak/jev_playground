import json, re
from pathlib import Path

pairs = json.load(open(Path(__file__).with_name("6ngv.pairs.json")))
# baseline: skill-name (first token) appears in early text
tp = fp = fn = tn = 0
for p in pairs:
    tok = re.split(r"[-_]", p["skill"])[0]
    pred = bool(re.search(re.escape(tok), p["early"], re.I))
    y = p["follow"]
    if pred and y:
        tp += 1
    elif pred and not y:
        fp += 1
    elif not pred and y:
        fn += 1
    else:
        tn += 1
acc = (tp + tn) / len(pairs)
print("keyword baseline: tp=%d fp=%d fn=%d tn=%d acc=%.4f" % (tp, fp, fn, tn, acc))
print(
    "abstain(abandon-always) acc=%.4f"
    % (sum(1 for p in pairs if not p["follow"]) / len(pairs))
)
# conf AUC
import itertools

pos = [p["conf"] for p in pairs if p["follow"]]
neg = [p["conf"] for p in pairs if not p["follow"]]
auc = sum(1 for a, b in itertools.product(pos, neg) if a > b) / (len(pos) * len(neg))
print("hint-conf AUC=%.4f" % auc)
