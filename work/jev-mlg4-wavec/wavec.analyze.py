import json, statistics
from collections import defaultdict

res = json.load(open("var/agent-tmp/wavec.results.json"))
pairs = defaultdict(dict)
for x in res:
    pairs[(x["task"], x["rep"])][x["arm"]] = x
b = sum(
    1
    for v in pairs.values()
    if v.get("ON", {}).get("pass") and not v.get("OFF", {}).get("pass")
)
c = sum(
    1
    for v in pairs.values()
    if v.get("OFF", {}).get("pass") and not v.get("ON", {}).get("pass")
)
print(
    "pairs=%d ON-only=%d OFF-only=%d diff=%.4f"
    % (len(pairs), b, c, (b - c) / len(pairs))
)
import math

n = b + c
if n:
    pval = sum(math.comb(n, k) for k in range(0, min(b, c) + 1)) / 2**n * 2
    print("McNemar exact p=%.4f" % min(pval, 1.0))


def wilcoxon(diffs):
    diffs = [d for d in diffs if d != 0]
    n = len(diffs)
    if n == 0:
        return 1.0, 0
    ranked = sorted(range(n), key=lambda i: abs(diffs[i]))
    ranks = [0] * n
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


for key in ["in", "out"]:
    diffs = [v["ON"][key] - v["OFF"][key] for v in pairs.values()]
    p, nn = wilcoxon(diffs)
    print(
        "%s: medON=%d medOFF=%d Wilcoxon p=%.4f"
        % (
            key,
            statistics.median(v["ON"][key] for v in pairs.values()),
            statistics.median(v["OFF"][key] for v in pairs.values()),
            p,
        )
    )
print(
    "main totals: in=%d out=%d"
    % (sum(x["in"] for x in res), sum(x["out"] for x in res))
)
# misses audit
for x in res:
    if not x["pass"]:
        print("MISS", x["task"], x["arm"], x["rep"])
