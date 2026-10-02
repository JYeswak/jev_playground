import json, glob, os, math, statistics
from collections import defaultdict

man = [json.loads(l) for l in open("work/jev-mlg4-wavec/manifest2.jsonl")]
seen = {}
for r in man:
    k = (r["task"], r["arm"], r["rep"])
    if k not in seen:
        seen[k] = r
print("unique runs:", len(seen))
rows = []
missing = []
for (t, a, r), rec in sorted(seen.items()):
    if t == "f07":
        continue
    sd = rec.get("sessdir") or ""
    files = sorted(glob.glob(sd + "/*.jsonl"), key=os.path.getmtime) if sd else []
    if not files:
        missing.append((t, a, r))
        continue
    tr_chars = 0
    n_tr = 0
    for line in open(files[-1], encoding="utf-8", errors="replace"):
        try:
            x = json.loads(line)
        except Exception:
            continue
        if (
            x.get("type") == "message"
            and x.get("message", {}).get("role") == "toolResult"
        ):
            c = x["message"].get("content")
            s = (
                c
                if isinstance(c, str)
                else "".join(b.get("text", "") for b in c if isinstance(b, dict))
                if isinstance(c, list)
                else ""
            )
            tr_chars += len(s)
            n_tr += 1
    rows.append({"task": t, "arm": a, "rep": r, "tr_chars": tr_chars, "tr_n": n_tr})
print("metered:", len(rows), "missing sessions:", len(missing), missing[:4])
json.dump(rows, open("var/agent-tmp/wavec.tr.json", "w"))
pairs = defaultdict(dict)
for x in rows:
    pairs[(x["task"], x["rep"])][x["arm"]] = x


def wilcoxon(diffs):
    diffs = [d for d in diffs if d != 0]
    n = len(diffs)
    if n == 0:
        return 1.0, 0
    ranked = sorted(range(n), key=lambda i: abs(diffs[i]))
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j < n and abs(diffs[ranked[j]]) == abs(diffs[ranked[i]]):
            j += 1
        avg = (i + j + 1) / 2
        for k in range(i, j):
            ranks[ranked[k]] = avg
        i = j
    w = sum(r for r, d in zip(ranks, diffs) if d > 0)
    mu = n * (n + 1) / 4
    var = n * (n + 1) * (2 * n + 1) / 24
    z = (w - mu) / math.sqrt(var) if var else 0
    return math.erfc(abs(z) / math.sqrt(2)), n


for key, lab in [
    ("tr_chars", "toolResult chars (~tok/4)"),
    ("tr_n", "toolResult count"),
]:
    diffs = [
        v["ON"][key] - v["OFF"][key] for v in pairs.values() if "ON" in v and "OFF" in v
    ]
    p, n = wilcoxon(diffs)
    a = [v["ON"][key] for v in pairs.values() if "ON" in v and "OFF" in v]
    b = [v["OFF"][key] for v in pairs.values() if "ON" in v and "OFF" in v]
    print(
        "%s: medON=%d medOFF=%d Wilcoxon p=%.4f n=%d"
        % (lab, statistics.median(a), statistics.median(b), p, n)
    )
    print("  totals: ON=%d OFF=%d" % (sum(a), sum(b)))
