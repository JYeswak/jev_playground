import json
from collections import defaultdict

met = json.load(open("var/agent-tmp/ab.metered.json"))
pairs = defaultdict(dict)
for o in met:
    pairs[(o["task"], o["rep"])][o["arm"]] = o


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
    import math

    z = (w - mu) / math.sqrt(var) if var else 0
    p = math.erfc(abs(z) / math.sqrt(2))
    return p, n


for key in ["in", "out", "tools"]:
    diffs = [
        v["ON"][key] - v["OFF"][key] for v in pairs.values() if "ON" in v and "OFF" in v
    ]
    import statistics

    p, n = wilcoxon(diffs)
    print(
        "%s: medON=%d medOFF=%d meddiff=%d Wilcoxon p=%.4f n=%d"
        % (
            key,
            statistics.median(
                v["ON"][key] for v in pairs.values() if "ON" in v and "OFF" in v
            ),
            statistics.median(
                v["OFF"][key] for v in pairs.values() if "ON" in v and "OFF" in v
            ),
            statistics.median(diffs),
            p,
            n,
        )
    )


# GPU overlap: window 06:05-06:55Z approx (localbench 50min from ~06:05Z per conductor 06:0xZ msg)
def overlap(t0, t1):
    return not (t1 < "2026-10-02T06:05Z" or t0 > "2026-10-02T06:55Z")


nov = [
    (k, v)
    for k, v in pairs.items()
    if not overlap(v["ON"]["t0"], v["ON"]["t1"])
    and not overlap(v["OFF"]["t0"], v["OFF"]["t1"])
]
print("non-overlapping pairs:", len(nov), "/", len(pairs))
bo = sum(1 for _, v in nov if v["ON"] and v["OFF"] and True)
import math

b = sum(1 for _, v in nov if v.get("ON") and v.get("OFF") and True and None)
# success among non-overlap: need grades; join results
res = json.load(open("var/agent-tmp/ab.results.json"))
g = {(r["task"], r["rep"], r["arm"]): r["pass"] for r in res}
bb = sum(
    1 for k, v in nov if g.get((k[0], k[1], "ON")) and not g.get((k[0], k[1], "OFF"))
)
cc = sum(
    1 for k, v in nov if g.get((k[0], k[1], "OFF")) and not g.get((k[0], k[1], "ON"))
)
print("non-overlap discordants ON-only=%d OFF-only=%d" % (bb, cc))
