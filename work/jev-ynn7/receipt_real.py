#!/usr/bin/env python3
"""jev-ynn7 real-repo receipt. Grades every scheduled run + pilot, sums spend.
ALL locate tokens per arm (failures included) / successes (WildCarp fix).
Usage: receipt_real.py  (reads schedule_real.json, targets_real.json, sessions-real/)
"""

import glob
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = "/Users/josh/Developer/jev/var/agent-tmp/ynn7-real/repo"
targets = json.load(open(os.path.join(ROOT, "targets_real.json")))
sched = json.load(open(os.path.join(ROOT, "schedule_real.json")))


def grade(sdir, token):
    r = subprocess.run(
        ["python3", os.path.join(ROOT, "grade_real.py"), sdir, REPO, token],
        capture_output=True,
        text=True,
    )
    return json.loads(r.stdout)


def spend(sdir):
    total, n = 0.0, 0
    for path in glob.glob(os.path.join(sdir, "*.jsonl")):
        with open(path, encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                if '"usage"' not in line:
                    continue
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                c = (row.get("usage") or {}).get("cost") or {}
                if isinstance(c.get("total"), (int, float)):
                    total += c["total"]
                    n += 1
    return round(total, 6), n


def one(rid, tid):
    sdir = os.path.join(ROOT, "sessions-real", rid)
    g = grade(sdir, targets[tid]["token"])
    cost, nrows = spend(sdir)
    return {"rid": rid, "task": tid, **g, "spend": cost, "usage_rows": nrows}


rows = []
for r in sorted(sched, key=lambda r: r["order"]):
    rows.append(
        {"arm": r["arm"], **one("%s-%s-real" % (r["task"], r["arm"]), r["task"])}
    )
pilot = [one("r01-control-pilotreal", "r01"), one("r01-treat-pilotreal", "r01")]
pilot[0]["arm"], pilot[1]["arm"] = "control", "treat"


def agg(rs, arm):
    s = [r for r in rs if r["arm"] == arm]
    succ = sum(1 for r in s if r["success"])
    tok = sum(r["tokens_locate"] for r in s)
    return {
        "n": len(s),
        "success": succ,
        "tokens_per_success": round(tok / succ, 1) if succ else None,
        "find_calls": sum(r["per_tool"]["find"]["calls"] for r in s),
        "grep_calls": sum(r["per_tool"]["grep"]["calls"] for r in s),
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
