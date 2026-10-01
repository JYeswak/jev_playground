#!/usr/bin/env python3
"""Fixed references for h09 (quoted tracking), h10 (evict-then-insert), h13 (non-dict target)."""

import os


def put(tid, fname, text):
    d = f"/tmp/g3/{tid}"
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, fname), "w").write(text)


put("h09", "delim.py", "PLACEHOLDER_H09")
put("h10", "c.py", "PLACEHOLDER_H10")
put("h13", "mpatch.py", "PLACEHOLDER_H13")
print("stubs written")
