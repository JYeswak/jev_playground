#!/usr/bin/env python3
"""Bind samples for the three proxy-vs-quantity proxies (seeded, n=20 each).

P1 bare-count: assistant text turn matching bare-count-not-denominator.
  Context stored: the turn itself (bind judges whether it generalizes).
P2 count-command: bash-looking toolCall args matching wc -l|grep -c.
  Context stored: command + the NEXT assistant text turn in file order
  (bind judges whether the output is quoted in prose as a quantity).
P3 fleet-words: assistant text turn matching fleet-generalizing words.
  Context stored: the turn + the PREVIOUS 3 assistant text turns
  (bind judges whether a narrow measurement precedes the general claim).
Seed 20260920. Bars: bind >= 20% to survive; else the proxy is not a
detectable defect signal and the class closes with the number.
"""

import json
import os
import random
import re
from datetime import datetime, timezone

OMP_ROOT = "/Users/josh/.omp"
SEED = 20260920
N = 20
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "proxy-bind-samples-20260920.jsonl")

P1_RX = re.compile(r"\b\d{3,}\b")
P1_NOT = re.compile(r"/|\bof\b|out of|%|denominator|N\s*=|n\s*=")
P2_RX = re.compile(r"wc -l|grep -c")
P3_RX = re.compile(
    r"fleet|fleet-wide|every repo|all \w+ repos|across \w+ repos|system-wide"
)

ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

files = []
for dirpath, _d, filenames in os.walk(OMP_ROOT):
    for fn in filenames:
        if fn.endswith(".jsonl"):
            files.append(os.path.join(dirpath, fn))

p1, p2, p3 = [], [], []
for fp in sorted(files):
    try:
        with open(fp, encoding="utf-8", errors="replace") as fh:
            lines = fh.read().splitlines()
    except OSError:
        continue
    texts = []  # (lineno, text) assistant text turns in order
    for ln, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if obj.get("type") != "message":
            continue
        msg = obj.get("message") or {}
        if msg.get("role") != "assistant":
            continue
        content = msg.get("content") or []
        t = "\n".join(
            c.get("text", "")
            for c in content
            if isinstance(c, dict) and c.get("type") == "text"
        )
        if t:
            texts.append((ln, t))
        for c in content:
            if (
                isinstance(c, dict)
                and c.get("type") == "toolCall"
                and str(c.get("name") or "").lower() == "bash"
            ):
                blob = json.dumps(c.get("arguments") or {}, sort_keys=True)
                if P2_RX.search(blob):
                    p2.append((fp, ln, blob[:600]))
    for ln, t in texts:
        if P1_RX.search(t) and not P1_NOT.search(t):
            p1.append((fp, ln, t[:1200]))
        if P3_RX.search(t):
            p3.append((fp, ln, t[:1200]))

# P2 context: next assistant text turn after the command line
p2rows = []
for fp, ln, blob in p2:
    nxt = ""
    try:
        with open(fp, encoding="utf-8", errors="replace") as fh:
            lines = fh.read().splitlines()
        for j in range(ln + 1, min(ln + 40, len(lines))):
            try:
                o = json.loads(lines[j].strip())
            except (ValueError, AttributeError):
                continue
            if o.get("type") == "message":
                m = o.get("message") or {}
                if m.get("role") == "assistant":
                    t = "\n".join(
                        c.get("text", "")
                        for c in (m.get("content") or [])
                        if isinstance(c, dict) and c.get("type") == "text"
                    )
                    if t.strip():
                        nxt = t[:1200]
                        break
    except OSError:
        pass
    p2rows.append((fp, ln, blob, nxt))

# P3 context: previous 3 assistant text turns in same file
byfile = {}
for fp, ln, t in p3:
    byfile.setdefault(fp, []).append((ln, t))
p3rows = []
for fp, turns in byfile.items():
    turns.sort()
    for k, (ln, t) in enumerate(turns):
        prev = "\n---\n".join(x[1][:400] for x in turns[max(0, k - 3) : k])
        p3rows.append((fp, ln, t, prev))

rng = random.Random(SEED)
samp = {
    "p1": rng.sample(p1, min(N, len(p1))),
    "p2": rng.sample(p2rows, min(N, len(p2rows))),
    "p3": rng.sample(p3rows, min(N, len(p3rows))),
}
print(f"pools: p1={len(p1)} p2={len(p2rows)} p3={len(p3rows)} ts={ts}")
rows = []
for proxy in ("p1", "p2", "p3"):
    for entry in samp[proxy]:
        if proxy == "p1":
            fp, ln, t = entry
            rows.append(
                {
                    "proxy": proxy,
                    "session": os.path.basename(fp),
                    "line": ln,
                    "hit": t,
                    "context": "",
                }
            )
        else:
            fp, ln, a, b = entry
            rows.append(
                {
                    "proxy": proxy,
                    "session": os.path.basename(fp),
                    "line": ln,
                    "hit": a[:1200],
                    "context": b[:1500],
                }
            )
with open(OUT, "w", encoding="utf-8") as fh:
    for r in rows:
        fh.write(json.dumps(r, sort_keys=True) + "\n")
print(f"rows={len(rows)} out={OUT}")
