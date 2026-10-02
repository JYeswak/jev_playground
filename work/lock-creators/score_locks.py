#!/usr/bin/env python3
"""Scorer: nearest capture rows around each block report + creator chains.
Recompute: python3 work/lock-creators/score_locks.py (reads zeststream watch log).
"""

import datetime
import json

LOG = "/Users/josh/.local/state/zeststream/index-lock-watch.jsonl"
WANT = ["2026-10-02T16:29", "2026-10-02T16:34", "2026-10-02T16:38", "2026-10-02T16:42"]


def pt(ts):
    s = ts[:19] if len(ts) > 16 else ts + ":00"
    return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S").replace(
        tzinfo=datetime.timezone.utc
    )


evs = []
for line in open(LOG, errors="ignore"):
    try:
        r = json.loads(line)
    except ValueError:
        continue
    if r.get("repo") == "/Users/josh/Developer/jev" and r.get("event") == "new":
        evs.append(r)
for w in WANT:
    wt = pt(w)
    near = sorted(evs, key=lambda r: abs((pt(r["ts"]) - wt).total_seconds()))[:2]
    print("== block report %sZ" % w)
    for r in near:
        dt = (pt(r["ts"]) - wt).total_seconds()
        procs = r.get("git_procs") or []
        if not procs:
            print(
                "  %+.0fs event size=%s creator=UNSEEN-holder-gone"
                % (dt, r.get("lock_size"))
            )
            continue
        g = procs[0]
        chain = " <- ".join(
            (p.get("command") or "")[:90] for p in (g.get("chain") or [])[:3]
        )
        print(
            "  %+.0fs event size=%s pid=%s :: %s"
            % (dt, r.get("lock_size"), g.get("git_pid"), chain)
        )
print("rows: work/lock-creators/creator_rows.jsonl")
