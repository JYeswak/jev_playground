#!/usr/bin/env python3
"""Flip memory-filter enforce switch per committed schedule. Cron: 2,6,10,14,18,22 * * * * (5 min past each 4h boundary for clock safety). Exits quietly outside flip minutes."""

import json
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.abspath(os.path.join(HERE, "..", "..", "scripts"))
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

from fleet_surface_heartbeat import STATE_NAME  # noqa: E402

SCHED = os.path.join(HERE, "schedule.json")
ENFORCE = os.path.expanduser("~/.local/state/jev/memory-filter-enforce")
STATE_DIR = os.path.expanduser(
    os.environ.get("JEV_FLEET_STATE_DIR", "~/.local/state/jev")
)
HEARTBEAT_STATE = os.path.join(STATE_DIR, STATE_NAME)
JOURNAL = os.path.join(HERE, "flips.jsonl")


def now():
    return datetime.now(timezone.utc)


def watcher_auto_off(surface_id="memory-filter"):
    try:
        with open(HEARTBEAT_STATE, encoding="utf-8") as fh:
            state = json.load(fh)
    except FileNotFoundError:
        return False
    except (OSError, ValueError):
        return None
    if not isinstance(state, dict):
        return None
    if "surfaces" not in state:
        return None
    records = state["surfaces"]
    if not isinstance(records, dict):
        return None
    record = records.get(surface_id)
    if record is None:
        return False
    if not isinstance(record, dict):
        return None
    if "auto_off" not in record:
        return False
    marker = record.get("auto_off")
    return marker if isinstance(marker, bool) else None


def main():
    with open(SCHED, encoding="utf-8") as fh:
        sched = json.load(fh)["blocks"]
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
    auto_off = watcher_auto_off()
    if want_on and auto_off is not False:
        if auto_off is True and is_on:
            os.remove(ENFORCE)
        status = "watcher auto-off active" if auto_off else "watcher state unavailable"
        print("%s; blocked scheduled ON for block %s" % (status, cur["start"]))
        return 0
    if want_on == is_on:
        print("already %s for block %s" % (cur["state"], cur["start"]))
        return 0
    if want_on:
        with open(ENFORCE, "w", encoding="utf-8") as fh:
            fh.write("natexp jev-qpv2 %s\n" % cur["start"])
    else:
        os.remove(ENFORCE)
    with open(JOURNAL, "a", encoding="utf-8") as fh:
        fh.write(
            json.dumps(
                {
                    "ts": t.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "block": cur["start"],
                    "state": cur["state"],
                }
            )
            + "\n"
        )
    print("flipped to %s for block %s" % (cur["state"], cur["start"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
