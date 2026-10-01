#!/usr/bin/env python3
"""Measure main duel: think chars, tokens, cost, wall, auto levels."""

import json, glob, os, re


def measure(sdir):
    think = tin = tout = 0
    cost = 0.0
    lvls = []
    files = glob.glob(os.path.join(sdir, "*.jsonl"))
    if not files:
        return None
    for f in files:
        fh = open(f, errors="replace")
        for line in fh:
            if '"thinkingLevel"' in line:
                lvls += re.findall(r'"thinkingLevel":"([a-z]+)"', line)
            try:
                d = json.loads(line)
            except Exception:
                continue
            m = d.get("message")
            if not isinstance(m, dict):
                continue
            c = m.get("content")
            if isinstance(c, list):
                for p in c:
                    if (
                        isinstance(p, dict)
                        and p.get("type") == "thinking"
                        and isinstance(p.get("thinking"), str)
                    ):
                        think += len(p["thinking"])
            u = m.get("usage")
            if isinstance(u, dict):
                tin += u.get("input") or 0
                tout += u.get("output") or 0
                cc = u.get("cost")
                if isinstance(cc, dict):
                    cost += cc.get("total") or 0
                elif isinstance(cc, (int, float)):
                    cost += cc
        fh.close()
    return {
        "think": think,
        "in": tin,
        "out": tout,
        "cost": round(cost, 6),
        "lvls": sorted(set(lvls)),
    }


walls = {}
for line in open("work/thinking-duel-hard3/main.log"):
    mm = re.match(r"(main-\w+-\w+) exit=\d+ wall=(\d+)s", line)
    if mm:
        walls[mm.group(1)] = int(mm.group(2))

PASS = {
    "main-k01-auto",
    "main-k02-auto",
    "main-k03-auto",
    "main-k04-auto",
    "main-k05-auto",
    "main-k06-auto",
    "main-k08-auto",
    "main-k09-auto",
    "main-k10-auto",
    "main-k12-auto",
    "main-k13-auto",
    "main-k14-auto",
    "main-k15-auto",
    "main-k16-auto",
    "main-k01-high",
    "main-k02-high",
    "main-k03-high",
    "main-k04-high",
    "main-k05-high",
    "main-k06-high",
    "main-k08-high",
    "main-k10-high",
    "main-k11-high",
    "main-k12-high",
    "main-k13-high",
    "main-k14-high",
    "main-k15-high",
}
agg = {
    "auto": {"s": 0, "think": 0, "cost": 0.0, "wall": 0},
    "high": {"s": 0, "think": 0, "cost": 0.0, "wall": 0},
}
rows = {}
for rid in sorted(os.listdir("work/thinking-duel-hard3/sessions")):
    if not rid.startswith("main-"):
        continue
    v = measure(os.path.join("work/thinking-duel-hard3/sessions", rid))
    if v is None:
        continue
    rows[rid] = v
json.dump(rows, open("work/thinking-duel-hard3/metrics-main.json", "w"), indent=1)
for rid, v in sorted(rows.items()):
    arm = rid.rsplit("-", 1)[1]
    a = agg[arm]
    a["think"] += v["think"]
    a["cost"] += v["cost"]
    a["wall"] += walls.get(rid, 0)
    if rid in PASS:
        a["s"] += 1
    print(
        rid,
        "PASS" if rid in PASS else "FAIL",
        "think=%d cost=%.4f wall=%d lvls=%s"
        % (v["think"], v["cost"], walls.get(rid, 0), v["lvls"]),
    )
print("runs:", len(rows))
for k, v in agg.items():
    print(k, v)
