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
for line in open("work/thinking-duel-hard3/pilot2.log"):
    mm = re.match(r"(pilot2-\w+-\w+) exit=\d+ wall=(\d+)s", line)
    if mm:
        walls[mm.group(1)] = int(mm.group(2))

PASS = {
    "pilot2-k01-auto",
    "pilot2-k02-auto",
    "pilot2-k03-auto",
    "pilot2-k04-auto",
    "pilot2-k05-auto",
    "pilot2-k06-auto",
    "pilot2-k08-auto",
    "pilot2-k09-auto",
    "pilot2-k10-auto",
    "pilot2-k12-auto",
    "pilot2-k13-auto",
    "pilot2-k14-auto",
    "pilot2-k15-auto",
    "pilot2-k16-auto",
    "pilot2-k01-high",
    "pilot2-k02-high",
    "pilot2-k03-high",
    "pilot2-k04-high",
    "pilot2-k05-high",
    "pilot2-k06-high",
    "pilot2-k08-high",
    "pilot2-k10-high",
    "pilot2-k11-high",
    "pilot2-k12-high",
    "pilot2-k13-high",
    "pilot2-k14-high",
    "pilot2-k15-high",
}
agg = {
    "auto": {"s": 0, "think": 0, "cost": 0.0, "wall": 0},
    "high": {"s": 0, "think": 0, "cost": 0.0, "wall": 0},
}
rows = {}
for rid in sorted(os.listdir("work/thinking-duel-hard3/sessions")):
    if not rid.startswith("pilot2-"):
        continue
    v = measure(os.path.join("work/thinking-duel-hard3/sessions", rid))
    if v is None:
        continue
    rows[rid] = v
json.dump(rows, open("work/thinking-duel-hard3/metrics-pilot2.json", "w"), indent=1)
for rid, v in sorted(rows.items()):
    arm = rid.split("-")[1]
    a = agg[arm]
    a["think"] += v["think"]
    a["cost"] += v["cost"]
    a["wall"] += walls.get(rid, 0)
    print(
        rid,
        "think=%d cost=%.4f wall=%d lvls=%s"
        % (v["think"], v["cost"], walls.get(rid, 0), v["lvls"]),
    )
print("runs:", len(rows))
for k, v in agg.items():
    print(k, v)
