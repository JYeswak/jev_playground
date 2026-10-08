#!/usr/bin/env python3
"""Double-read waste measurement, committed definitions (jev-p55p).

DEFINITIONS (the WildCarp reconcile):
- ORANGE (mine): any two reads of the same path+full-args in one file whose
  full-text sha256 matches. Order-free, full text, args-sensitive.
- WILDCARP (his): CONSECUTIVE reads (adjacent read results, any path) whose
  TRUNCATED text matches. Adjacency-only, truncated, path-insensitive.
- CLEAN (reconciled waste): ORANGE pairs with no compaction event between
  the two reads. Compaction replaces context with a summary, so
  post-compaction repeats are justified, not waste.

Rows: same 7d all-profile session files, sorted traversal (deterministic),
seed-7 50-sample of CLEAN pairs to labels-50.jsonl with safe/unsafe flags
(unsafe = intervening edit/write to the path; safe otherwise).

Usage: python3 work/jev-p55p/measure-double-read.py [--days N]
Output: work/jev-p55p/labels-50.jsonl + stdout counts.
"""

from __future__ import annotations

import datetime
import glob
import hashlib
import json
import os
import random
import sys

DAYS = int(sys.argv[sys.argv.index("--days") + 1]) if "--days" in sys.argv else 7
NOW = datetime.datetime.now(datetime.timezone.utc).timestamp()
BASE = NOW - DAYS * 86400
HERE = os.path.dirname(os.path.abspath(__file__))
TRUNC = 4000


def text_of(m):
    c = m.get("content")
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        return "\n".join(
            p.get("text", "") for p in c if isinstance(p, dict) and isinstance(p.get("text"), str)
        )
    return ""


def files_sorted():
    roots = ["/Users/josh/.omp/agent/sessions"] + sorted(
        glob.glob("/Users/josh/.omp/profiles/*/agent/sessions")
    )
    out = []
    for r in sorted(roots):
        try:
            slugs = sorted(os.listdir(r))
        except OSError:
            continue
        for s in slugs:
            d = os.path.join(r, s)
            if not os.path.isdir(d):
                continue
            try:
                names = sorted(
                    x for x in os.listdir(d) if x.endswith(".jsonl") and not x.startswith(".")
                )
            except OSError:
                continue
            for n in names:
                fp = os.path.join(d, n)
                try:
                    if os.path.getmtime(fp) >= BASE:
                        out.append(fp)
                except OSError:
                    continue
    return out


def main():
    orange_pairs = []  # (chars, gap_turns, edited, compacted)
    wild_consec = 0
    wild_match = 0
    n_files = 0
    for fp in files_sorted():
        try:
            fh = open(fp, errors="replace")
        except OSError:
            continue
        n_files += 1
        calls = {}
        last = {}
        turn = 0
        comp_turn = -1
        edited = set()
        prev_result = None  # (key, sha_trunc) for WILDCARP adjacency
        with fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    o = json.loads(line)
                except ValueError:
                    continue
                if o.get("type") == "compaction":
                    comp_turn = turn
                    continue
                m = o.get("message")
                if not isinstance(m, dict):
                    continue
                if m.get("role") == "assistant" and isinstance(m.get("content"), list):
                    turn += 1
                    for b in m["content"]:
                        if not (isinstance(b, dict) and b.get("type") == "toolCall"):
                            continue
                        args = b.get("arguments") or {}
                        calls[b.get("id")] = (b.get("name"), args)
                        if b.get("name") in ("edit", "write") and isinstance(args.get("path"), str):
                            edited.add(args["path"])
                elif m.get("role") == "toolResult" and m.get("toolName") == "read":
                    if m.get("isError") is True:
                        prev_result = None
                        continue
                    nm, args = calls.get(m.get("toolCallId"), (None, {}))
                    if nm != "read" or not isinstance(args.get("path"), str):
                        prev_result = None
                        continue
                    key = (
                        args["path"],
                        json.dumps({k: v for k, v in args.items() if k != "i"}, sort_keys=True),
                    )
                    txt = text_of(m)
                    sha = hashlib.sha256(txt.encode()).hexdigest()[:16]
                    # WILDCARP: adjacent read results, truncated text, any path.
                    if prev_result is not None:
                        wild_consec += 1
                        if prev_result[1] == hashlib.sha256(txt[:TRUNC].encode()).hexdigest()[:16]:
                            wild_match += 1
                    prev_result = (key, hashlib.sha256(txt[:TRUNC].encode()).hexdigest()[:16])
                    # ORANGE: same path+args anywhere in file, full text.
                    if key in last and last[key][0] == sha:
                        orange_pairs.append(
                            {
                                "chars": len(txt),
                                "gap": turn - last[key][1],
                                "edited": args["path"] in edited,
                                "compacted": comp_turn > last[key][1],
                            }
                        )
                    last[key] = (sha, turn)
    n_orange = len(orange_pairs)
    n_ident = n_orange  # all orange pairs are identical by construction
    clean = [p for p in orange_pairs if not p["compacted"]]
    print("files=%d" % n_files)
    print("ORANGE identical=%d (any-distance, full-text, same path+args)" % n_ident)
    print("WILDCARP consecutive=%d match=%d share=%.3f" % (
        wild_consec, wild_match, wild_match / wild_consec if wild_consec else 0))
    print("CLEAN (no compaction between)=%d (%.3f of identical)" % (
        len(clean), len(clean) / n_ident if n_ident else 0))
    for bound in (20, 50):
        sel = [p for p in clean if p["gap"] <= bound]
        safe = [p for p in sel if not p["edited"]]
        tok = sum(p["chars"] for p in safe)
        print("bound<=%d: n=%d strict-safe=%d/%d=%.3f tok/day=%d" % (
            bound, len(sel), len(safe), len(sel),
            len(safe) / len(sel) if sel else 0, round(tok / 4 / DAYS)))
    random.seed(7)
    sample = random.sample(clean, min(50, len(clean)))
    with open(os.path.join(HERE, "labels-50.jsonl"), "w", encoding="utf-8") as fh:
        for i, p in enumerate(sample):
            fh.write(json.dumps({
                "id": "dd%02d" % i,
                "chars": p["chars"],
                "gap_turns": p["gap"],
                "edited_between": p["edited"],
                "label": "unsafe-edit" if p["edited"] else "safe",
            }) + "\n")
    print("wrote labels-50.jsonl n=%d" % len(sample))


if __name__ == "__main__":
    main()
