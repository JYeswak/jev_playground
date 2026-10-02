import json, math

man = [json.loads(l) for l in open("var/agent-tmp/ab-yp8k.main/manifest.jsonl")]
print("runs:", len(man))
# grades: re-read from grade outputs? re-grade quickly not needed; parse below via ab.gradeall rerun?
# Instead load grades by re-running grader silently:
import subprocess

GRADE = {
    "hard": "work/thinking-duel-hard/grade.py",
    "hard3": "work/thinking-duel-hard3/grade.py",
}
res = []
for r in man:
    d = "var/agent-tmp/ab-yp8k.main/%s-%s-%s" % (r["task"], r["arm"], r["rep"])
    p = subprocess.run(
        ["python3", GRADE[r["set"]], r["task"], d],
        capture_output=True,
        text=True,
        timeout=150,
        cwd="/Users/josh/Developer/jev",
    )
    ok = "PASS" in p.stdout.split()[1] if len(p.stdout.split()) > 1 else False
    res.append((r, ok))
on = sum(1 for _, o in res if o)
print("overall pass: %d/%d" % (on, len(res)))
# paired by (task, rep)
from collections import defaultdict

pairs = defaultdict(dict)
for r, o in res:
    pairs[(r["task"], r["rep"])][r["arm"]] = o
b = c = 0
for k, v in pairs.items():
    if v.get("ON") and not v.get("OFF"):
        b += 1
    elif v.get("OFF") and not v.get("ON"):
        c += 1
print("pairs:", len(pairs), "ON-only:", b, "OFF-only:", c)
# McNemar exact two-sided
pval = (
    sum(math.comb(b + c, k) for k in range(0, min(b, c) + 1)) * 2 ** (-(b + c)) * 2
    if (b + c)
    else 1.0
)
print("McNemar exact p=%.4f" % min(pval, 1.0))
d = (b - c) / len(pairs)
print("paired success diff (ON-OFF): %.4f" % d)
json.dump(
    [
        {
            "task": r["task"],
            "rep": r["rep"],
            "arm": r["arm"],
            "pass": o,
            "t0": r["t0"],
            "t1": r["t1"],
            "think": r.get("think"),
            "sessdir": r.get("sessdir"),
        }
        for r, o in res
    ],
    open("var/agent-tmp/ab.results.json", "w"),
)
