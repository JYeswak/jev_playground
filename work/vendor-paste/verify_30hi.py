import json

sample = json.load(open("work/vendor-paste/sample.json"))
lab = {}
lic = {}
for part in ["dev", "held"]:
    for s in sample[part]:
        lab[s["sample_id"]] = 1 if s["label"] == "pos" else 0
        lic[s["sample_id"]] = 1 if str(s.get("lic")) == "True" else 0
rows = [json.loads(l) for l in open("work/vendor-paste/vendor-rows.jsonl") if l.strip()]
dev = [
    (r["noul"], lab[r["sample_id"]])
    for r in rows
    if r.get("split") == "dev"
    and r.get("sample_id") in lab
    and isinstance(r.get("noul"), (int, float))
]
held = [
    (r["noul"], lab[r["sample_id"]])
    for r in rows
    if r.get("split") == "held"
    and r.get("sample_id") in lab
    and isinstance(r.get("noul"), (int, float))
]
print("dev=%d held=%d" % (len(dev), len(held)))
best = None
for i in range(0, 101):
    cut = i / 100
    tp = sum(1 for s, y in dev if s >= cut and y == 1)
    fn = sum(1 for s, y in dev if s < cut and y == 1)
    fp = sum(1 for s, y in dev if s >= cut and y == 0)
    tn = sum(1 for s, y in dev if s < cut and y == 0)
    sens = tp / (tp + fn) if tp + fn else 0
    spec = tn / (tn + fp) if tn + fp else 0
    j = sens + spec - 1
    if (
        best is None
        or j > best[0] + 1e-9
        or (abs(j - best[0]) < 1e-9 and cut < best[1])
    ):
        best = (j, cut)
print("dev Youden cut=%.2f J=%.4f" % (best[1], best[0]))
cut = best[1]
tp = sum(1 for s, y in held if s >= cut and y == 1)
fp = sum(1 for s, y in held if s >= cut and y == 0)
fn = sum(1 for s, y in held if s < cut and y == 1)
tn = sum(1 for s, y in held if s < cut and y == 0)
prec = tp / (tp + fp) if tp + fp else 0
rec = tp / (tp + fn) if tp + fn else 0
acc = (tp + tn) / len(held)
print(
    "jev held: tp=%d fp=%d fn=%d tn=%d prec=%.4f rec=%.4f acc=%.4f"
    % (tp, fp, fn, tn, prec, rec, acc)
)
# baseline lic on same held
hids = [
    r["sample_id"]
    for r in rows
    if r.get("split") == "held" and r.get("sample_id") in lab
]
btp = sum(1 for i in hids if lic[i] == 1 and lab[i] == 1)
bfp = sum(1 for i in hids if lic[i] == 1 and lab[i] == 0)
bfn = sum(1 for i in hids if lic[i] == 0 and lab[i] == 1)
btn = sum(1 for i in hids if lic[i] == 0 and lab[i] == 0)
bprec = btp / (btp + bfp) if btp + bfp else 0
brec = btp / (btp + bfn) if btp + bfn else 0
bacc = (btp + btn) / len(hids)
print(
    "lic held: tp=%d fp=%d fn=%d tn=%d prec=%.4f rec=%.4f acc=%.4f"
    % (btp, bfp, bfn, btn, bprec, brec, bacc)
)
print("delta acc=%.4f (lock 0.20)" % (acc - bacc))
# McNemar Jev vs baseline (paired on same rows)
jp = {}
for r in rows:
    if (
        r.get("split") == "held"
        and r.get("sample_id") in lab
        and isinstance(r.get("noul"), (int, float))
    ):
        jp[r["sample_id"]] = 1 if r["noul"] >= cut else 0
b01 = sum(1 for i in hids if jp.get(i) == 1 and lic[i] == 0 and lab[i] == jp.get(i))
j_only = sum(1 for i in hids if jp.get(i) != lic[i])
jw = sum(1 for i in hids if jp.get(i) == lab[i] and lic[i] != lab[i])
bw = sum(1 for i in hids if lic[i] == lab[i] and jp.get(i) != lab[i])
print("McNemar: jev-right-base-wrong=%d base-right-jev-wrong=%d" % (jw, bw))
import math

n = jw + bw
pval = sum(math.comb(n, k) for k in range(0, min(jw, bw) + 1)) / 2**n * 2 if n else 1.0
print("McNemar exact p=%.4f" % min(pval, 1.0))
