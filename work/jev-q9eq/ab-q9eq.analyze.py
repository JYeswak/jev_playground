import json, math, subprocess, glob, os
from collections import defaultdict

man = [json.loads(l) for l in open("var/agent-tmp/ab-q9eq.main/manifest.jsonl")]
print("runs:", len(man))
GRADE = {
    "hard": "work/thinking-duel-hard/grade.py",
    "hard3": "work/thinking-duel-hard3/grade.py",
}
res = []
for r in man:
    d = "var/agent-tmp/ab-q9eq.main/%s-%s-%s" % (r["task"], r["arm"], r["rep"])
    p = subprocess.run(
        ["python3", GRADE[r["set"]], r["task"], d],
        capture_output=True,
        text=True,
        timeout=150,
        cwd="/Users/josh/Developer/jev",
    )
    parts = p.stdout.split()
    ok = len(parts) > 1 and parts[1] == "PASS"
    res.append(
        {
            "task": r["task"],
            "rep": r["rep"],
            "arm": r["arm"],
            "pass": ok,
            "t0": r["t0"],
            "t1": r["t1"],
            "think": r.get("think"),
            "sessdir": r.get("sessdir"),
        }
    )
json.dump(res, open("var/agent-tmp/ab-q9eq.results.json", "w"))
pairs = defaultdict(dict)
for x in res:
    pairs[(x["task"], x["rep"])][x["arm"]] = x["pass"]
b = sum(1 for v in pairs.values() if v.get("ON") and not v.get("OFF"))
c = sum(1 for v in pairs.values() if v.get("OFF") and not v.get("ON"))
n = len(pairs)
print("pairs=%d ON-only=%d OFF-only=%d diff=%.4f" % (n, b, c, (b - c) / n))
if b + c:
    from math import comb

    pval = sum(comb(b + c, k) for k in range(0, min(b, c) + 1)) / 2 ** (b + c) * 2
    print("McNemar exact p=%.4f" % min(pval, 1.0))
else:
    print("McNemar: no discordants")
on_rate = sum(1 for x in res if x["arm"] == "ON" and x["pass"]) / sum(
    1 for x in res if x["arm"] == "ON"
)
off_rate = sum(1 for x in res if x["arm"] == "OFF" and x["pass"]) / sum(
    1 for x in res if x["arm"] == "OFF"
)
print("ON rate=%.4f OFF rate=%.4f" % (on_rate, off_rate))
