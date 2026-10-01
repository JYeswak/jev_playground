#!/usr/bin/env python3
"""jev-tnde: same-session memory re-injection measure (keyless, session files).

BAR (fixed before first run, 2026-10-01, bead jev-tnde): the cut is worth
doing iff >= 20% of injected memory tokens are same-session repeats, i.e.
REPEAT_RATIO = repeat_tokens / total_tokens >= 0.20.

METHOD (literal reading of the bead acceptance):
- Window: session *.jsonl under ~/.omp/agent/sessions and
  ~/.omp/profiles/*/agent/sessions with mtime in the last 24h.
- Per file, prompt snapshots = session_init rows carrying a systemPrompt, in
  file order. (Measured 2026-10-01: 0 files have >1 session_init; 241/374
  have none. The system prompt is snapshotted at most once per file.)
- Each snapshot's <memories>...</memories> blocks are split into items.
- An item in snapshot k>0 seen in an earlier snapshot of the SAME file is a
  repeat. tokens = chars/4.
- Memory text in toolResult/assistant/custom/compaction rows are echoes or
  quotes, NOT injections: excluded (echoes outnumber injections ~10:1).
"""

import glob
import json
import os
import re
import time

BAR = 0.20
WINDOW_S = 24 * 3600

ITEM_RE = re.compile(r"(?m)^- (.*?)(?=^\s*$|^- |\Z)", re.S)


def split_items(block):
    return [m.group(1).strip() for m in ITEM_RE.finditer(block) if m.group(1).strip()]


def norm(t):
    return re.sub(r"\s+", " ", t).strip()


def snapshots_of(path):
    snaps = []
    try:
        fh = open(path, encoding="utf-8", errors="ignore")
    except OSError:
        return snaps
    with fh:
        for line in fh:
            if '"session_init"' not in line:
                continue
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if row.get("type") != "session_init":
                continue
            sp = row.get("systemPrompt")
            if isinstance(sp, list):
                sp = "\n".join(x for x in sp if isinstance(x, str))
            if isinstance(sp, str) and "<memories>" in sp:
                snaps.append(sp)
    return snaps


def main():
    cut = time.time() - WINDOW_S
    roots = [os.path.expanduser("~/.omp/agent/sessions")] + glob.glob(
        os.path.expanduser("~/.omp/profiles/*/agent/sessions")
    )
    files = []
    for r in roots:
        for p in glob.glob(r + "/*/*.jsonl") + glob.glob(r + "/*/*/*.jsonl"):
            try:
                if os.stat(p).st_mtime >= cut:
                    files.append(p)
            except OSError:
                pass
    n_memfiles = 0
    total_items = total_tokens = 0.0
    repeat_items = repeat_tokens = 0.0
    asst_msgs = 0
    for p in files:
        snaps = snapshots_of(p)
        if snaps:
            n_memfiles += 1
        seen = set()
        for k, sp in enumerate(snaps):
            for m in re.finditer(r"<memories>(.*?)</memories>", sp, re.S):
                for it in split_items(m.group(1)):
                    t = len(it) / 4
                    total_items += 1
                    total_tokens += t
                    key = norm(it)
                    if k > 0 and key in seen:
                        repeat_items += 1
                        repeat_tokens += t
                    seen.add(key)
        try:
            fh = open(p, encoding="utf-8", errors="ignore")
        except OSError:
            continue
        with fh:
            for line in fh:
                if '"role":"assistant"' in line or '"role": "assistant"' in line:
                    asst_msgs += 1
    ratio = (repeat_tokens / total_tokens) if total_tokens else 0.0
    print("files_24h=%d files_with_memories=%d" % (len(files), n_memfiles))
    print("total_items=%.0f total_tokens=%.0f" % (total_items, total_tokens))
    print("repeat_items=%.0f repeat_tokens=%.0f" % (repeat_items, repeat_tokens))
    print(
        "REPEAT_RATIO=%.4f BAR=%.2f VERDICT=%s"
        % (ratio, BAR, "PASS" if ratio >= BAR else "FAIL")
    )
    print(
        "ESTIMATE per-turn re-send scale: %.0f memory tokens x %d asst msgs"
        % (total_tokens, asst_msgs)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
