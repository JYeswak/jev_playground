#!/usr/bin/env python3
"""Flip memory-filter enforce switch per committed schedule. Cron: 2,6,10,14,18,22 * * * * (5 min past each 4h boundary for clock safety). Exits quietly outside flip minutes."""
import json
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
SCHED = os.path.join(HERE, "schedule.json")
ENFORCE = os.path.expanduser("~/.local/state/jev/memory-filter-enforce")
JOURNAL = os.path.join(HERE, "flips.jsonl")


def now():
    return datetime.now(timezone.utc)


def main():
    sched = json.load(open(SCHED))["blocks"]
    t = now()
    cur = None
    for b in sched:
        s = datetime.fromisoformat(b["start"].replace("Z", "+00:00"))
        e = datetime.fromisoformat(b["end"].replace("Z", "+00:00"))
        if s <= t < e:
            cur = b
            break
    if cur is None:
        print("no active block")
        return 0
    want_on = cur["state"] == "ON"
    is_on = os.path.exists(ENFORCE)
    if want_on == is_on:
        print("already %s for block %s" % (cur["state"], cur["start"]))
        return 0
    if want_on:
        open(ENFORCE, "w").write("natexp jev-qpv2 %s\n" % cur["start"])
    else:
        os.remove(ENFORCE)
    with open(JOURNAL, "a") as fh:
        fh.write(json.dumps({"ts": t.strftime("%Y-%m-%dT%H:%M:%SZ"), "block": cur["start"], "state": cur["state"]}) + "\n")
    print("flipped to %s for block %s" % (cur["state"], cur["start"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
