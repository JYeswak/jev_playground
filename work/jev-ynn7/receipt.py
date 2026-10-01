#!/usr/bin/env python3
"""jev-ynn7: final receipt. Grades every scheduled run + pilot, sums spend.
Usage: receipt.py  (reads schedule.json, targets.json, sessions/)
"""

import glob
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
targets = json.load(open(os.path.join(ROOT, "targets.json")))
sched = json.load(open(os.path.join(ROOT, "schedule.json")))


def grade(rid, tid):
    sdir = os.path.join(ROOT, "sessions", rid)
    r = subprocess.run(
        ["python3", os.path.join(ROOT, "grade_run.py"), sdir, targets[tid]["file"]],
        capture_output=True,
        text=True,
    )
    return json.loads(r.stdout)


def spend(rid):
    total, n = 0.0, 0
    for path in glob.glob(os.path.join(ROOT, "sessions", rid, "*.jsonl")):
        with open(path, encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                if '"usage"' not in line:
                    continue
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                u = row.get("usage") or {}
                c = u.get("cost") or {}
                if isinstance(c.get("total"), (int, float)):
                    total += c["total"]
                    n += 1
    return round(total, 6), n


rows = []
for r in sorted(sched, key=lambda r: r["order"]):
    rid = "%s-%s" % (r["task"], r["arm"])
    g = grade(rid, r["task"])
    cost, nrows = spend(rid)
    rows.append(
        {
            "rid": rid,
            "task": r["task"],
            "arm": r["arm"],
            **g,
            "spend": cost,
            "usage_rows": nrows,
        }
    )
pilot = []
for rid, tid in (("f01-control-pilot", "f01"), ("f01-treat-pilot", "f01")):
    g = grade(rid, tid)
    cost, nrows = spend(rid)
    pilot.append({"rid": rid, **g, "spend": cost, "usage_rows": nrows})


def agg(rs, arm):
    s = [r for r in rs if r["arm"] == arm]
    succ = sum(1 for r in s if r["success"])
    tok = sum(r["tokens_locate"] for r in s if r["success"])
    finds = sum(r["per_tool"]["find"]["calls"] for r in s)
    greps = sum(r["per_tool"]["grep"]["calls"] for r in s)
    return {
        "n": len(s),
        "success": succ,
        "tokens_per_success": round(tok / succ, 1) if succ else None,
        "find_calls": finds,
        "grep_calls": greps,
        "spend": round(sum(r["spend"] for r in s), 6),
    }


out = {
    "pilot": pilot,
    "control": agg(rows, "control"),
    "treat": agg(rows, "treat"),
    "total_spend": round(sum(r["spend"] for r in rows + pilot), 6),
    "rows": rows,
}
print(json.dumps(out, indent=1))
c, t = out["control"], out["treat"]
if t["success"] and c["success"]:
    print(
        "BAR %s: treat %.1f vs control %.1f tok/success; success %d vs %d"
        % (
            "PASS"
            if (
                t["tokens_per_success"] <= 0.8 * c["tokens_per_success"]
                and t["success"] >= c["success"]
            )
            else "FAIL",
            t["tokens_per_success"],
            c["tokens_per_success"],
            t["success"],
            c["success"],
        )
    )
