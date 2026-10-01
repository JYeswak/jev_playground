#!/usr/bin/env python3
"""Stage a bead-only issues.jsonl blob: HEAD content + only MINE_BEAD's worktree line.

Usage: blob.py <bead-id>  (prints blob hash; caller runs update-index)
Shared-file discipline: every other changed line reverts to HEAD; new beads
not mine are dropped. Verify with git diff --cached before committing.
"""

import json, subprocess, sys

bead = sys.argv[1]
head = subprocess.run(
    ["git", "show", "HEAD:.beads/issues.jsonl"], capture_output=True, text=True
).stdout.splitlines()
H = {json.loads(l)["id"]: l for l in head if l.strip()}
W = {}
for l in open(".beads/issues.jsonl"):
    l = l.rstrip("\n")
    if not l.strip():
        continue
    d = json.loads(l)
    W[d["id"]] = json.loads(l)
others = [k for k in H if H.get(k) != W.get(k) and k != bead]
newm = [k for k in W if k not in H and k != bead]
print("new-nonmine:", newm, "others-reverted:", len(others))
out = []
for l in open(".beads/issues.jsonl"):
    l = l.rstrip("\n")
    if not l.strip():
        continue
    d = json.loads(l)
    if d["id"] in others:
        out.append(H[d["id"]])
    elif d["id"] not in H and d["id"] != bead:
        continue
    else:
        out.append(l)
open("/tmp/issues-blob.jsonl", "w").write("\n".join(out) + "\n")
