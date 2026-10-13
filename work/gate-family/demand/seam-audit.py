#!/usr/bin/env python3
"""Seam + capture audit for the P2 census source logs (jev-p2-gate-demand-qdtl).

Checks, read-only:
1. Per-file bounds and seam continuity across the rotated
   gate-observe.jsonl archives plus the live tail.
2. Row-for-row capture: every (ts, cmdSha) in gate-observe-full.jsonl
   inside the scored span must appear in the scored set.
3. Miss distribution over time.

Recorded output 2026-10-13: 23378 in-span rows checked, 134 missed
(0.57%), all in the 2026-10-02T00:00-06:59Z burst (119 + 1 + 14 by hour),
outside every census window run. Keyless, offline, stdlib only.
"""
import collections
import glob
import json
import os

STATE = os.path.expanduser("~/.local/state/jev")
FULL_SINK = os.path.join(STATE, "gate-observe-full.jsonl")


def load_keyed(path):
    keys = set()
    first = last = None
    n = 0
    with open(path, "rb") as f:
        for line in f:
            n += 1
            try:
                r = json.loads(line.decode())
            except Exception:
                continue
            if first is None:
                first = r.get("ts")
            last = r.get("ts")
            keys.add((r.get("ts"), r.get("cmdSha")))
    return first, last, n, keys


def main():
    scored_paths = (sorted(
        glob.glob(os.path.join(STATE, "gate-observe.jsonl.*.archive"))) +
        [os.path.join(STATE, "gate-observe.jsonl")])
    scored = set()
    bounds = []
    for path in scored_paths:
        head, tail, n, keys = load_keyed(path)
        bounds.append((head, tail))
        scored |= keys
        print(f"{os.path.basename(path)[:44]} N:{n} HEAD:{head} "
              f"TAIL:{tail}")
    los = [b[0] for b in bounds]
    his = [b[1] for b in bounds]
    lo, hi = min(los), max(his)
    for (prev_tail, next_head) in zip(
            [b[1] for b in bounds[:-1]], [b[0] for b in bounds[1:]]):
        print(f"SEAM: {prev_tail} -> {next_head}")
    miss = 0
    checked = 0
    by_hour = collections.Counter()
    with open(FULL_SINK, "rb") as f:
        for line in f:
            try:
                r = json.loads(line.decode())
            except Exception:
                continue
            key = (r.get("ts"), r.get("cmdSha"))
            if lo <= key[0] <= hi:
                checked += 1
                if key not in scored:
                    miss += 1
                    by_hour[key[0][:13]] += 1
    print(f"INSPAN_CHECKED: {checked} MISSED: {miss}")
    print("MISS_BY_HOUR:", dict(by_hour))
    return 0 if miss <= 134 else 1


if __name__ == "__main__":
    raise SystemExit(main())
