#!/usr/bin/env python3
"""Measure whether grep->read yields a FREE, unauthored labelled reranking corpus.

The agent's next `read` after a multi-hit `grep` is a relevance judgment nobody authored.
Candidates = distinct files named in the grep output; relevant = the file actually read next.

v2 — v1's regex assumed `path:line:text` and silently under-extracted (319 hit lines ->
4 candidates), producing a false n=3. omp's real grep output uses TWO header forms:
    [src/technical.rs#FF28]              bracketed path + snapshot tag
    # src/                               directory header
    ## technical.rs#FF28                 file header under it
followed by ` 5:` / `*6:` numbered content lines and `...` elision markers.
v2 parses both header forms and reports which form each hit came from, so a future
format change shows up as a drop in parsed candidates rather than as a silent zero.

Read-only. No network. No API key. Writes one JSON receipt to notes/.
"""

import json, glob, os, re, statistics as st, datetime, collections

files = glob.glob(
    os.path.expanduser("~/.omp/profiles/*/agent/sessions/**/*.jsonl"), recursive=True
)
files += glob.glob(
    os.path.expanduser("~/.omp/agent/sessions/**/*.jsonl"), recursive=True
)
files = [f for f in files if os.path.getsize(f) <= 25_000_000]

BRACKET = re.compile(
    r"^\s*\[([^\]\s]+?)(?:#[0-9A-Fa-f]{4})?\]\s*$"
)  # [src/foo.rs#FF28]
DIRHDR = re.compile(r"^#\s+(\S+/)\s*$")  # # src/
FILEHDR = re.compile(r"^##\s+(\S+?)(?:#[0-9A-Fa-f]{4})?\s*$")  # ## technical.rs#FF28
COLON = re.compile(r"^\s*([^\s:]+\.[A-Za-z0-9_]{1,6}):\d+:")  # path/foo.py:12: text

WINDOW = 6  # how many following events may contain the read


def base(p):
    p = (p or "").split(":")[0].strip()
    return os.path.basename(p) if p else ""


def candidates(text):
    """Distinct files named in a grep result, in output order. Returns (list, form_counter)."""
    out, seen, forms = [], set(), collections.Counter()
    curdir = ""
    for l in text.split("\n"):
        if not l.strip() or l.strip() == "...":
            continue
        f = None
        m = BRACKET.match(l)
        if m:
            f, k = m.group(1), "bracket"
        else:
            m = DIRHDR.match(l)
            if m:
                curdir = m.group(1)
                continue
            m = FILEHDR.match(l)
            if m:
                f, k = curdir + m.group(1), "hdr2"
            else:
                m = COLON.match(l)
                if m:
                    f, k = m.group(1), "colon"
        if not f:
            continue
        b = base(f)
        if b and b not in seen:
            seen.add(b)
            out.append(b)
            forms[k] += 1
    return out, forms


pairs = labeled = 0
greps_seen = greps_big = reads_seen = 0
distinct_counts, rank_of_pick, hit_counts = [], [], []
form_total = collections.Counter()
scanned = 0

for p in files:
    try:
        raw = open(p, errors="replace").readlines()
    except Exception:
        continue
    scanned += 1
    events, pend = [], {}
    for line in raw:
        if '"toolCall"' not in line and '"toolResult"' not in line:
            continue
        try:
            o = json.loads(line)
        except Exception:
            continue
        if o.get("type") != "message":
            continue
        msg = o.get("message") or {}
        content = msg.get("content")
        if not isinstance(content, list):
            continue
        for it in content:
            if not isinstance(it, dict):
                continue
            if it.get("type") == "toolCall":
                nm, tid = it.get("name"), it.get("id")
                if nm == "grep" and tid:
                    pend[tid] = 1
                elif nm == "read":
                    a = it.get("arguments") or {}
                    if isinstance(a, str):
                        try:
                            a = json.loads(a)
                        except Exception:
                            a = {}
                    events.append(("read", base(a.get("path"))))
            else:
                tid = (
                    msg.get("toolCallId") or it.get("toolCallId") or o.get("toolCallId")
                )
                if tid and tid in pend:
                    pend.pop(tid)
                    events.append(("g", it.get("text") or ""))

    for i in range(len(events)):
        k0, v0 = events[i]
        if k0 == "read":
            reads_seen += 1
            continue
        if k0 != "g":
            continue
        greps_seen += 1
        hl = [l for l in v0.split("\n") if l.strip()]
        if len(hl) < 10:
            continue
        greps_big += 1
        cands, forms = candidates(v0)
        form_total.update(forms)
        if len(cands) < 2:
            continue
        nxt = None
        for kk, w in events[i + 1 : i + 1 + WINDOW]:
            if kk == "read" and w:
                nxt = w
                break
        if not nxt:
            continue
        pairs += 1
        distinct_counts.append(len(cands))
        hit_counts.append(len(hl))
        if nxt in cands:
            labeled += 1
            rank_of_pick.append(cands.index(nxt) + 1)

out = {
    "generated_at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    "parser_version": 2,
    "session_files_scanned": scanned,
    "grep_results_seen": greps_seen,
    "grep_results_ge10_lines": greps_big,
    "read_calls_seen": reads_seen,
    "read_window_events": WINDOW,
    "candidate_header_forms": dict(form_total),
    "grep_then_read_pairs": pairs,
    "labelled_pairs": labeled,
    "label_yield_pct": round(100 * labeled / max(pairs, 1), 2),
}
if distinct_counts:
    out["candidates_per_grep_median"] = st.median(distinct_counts)
    out["candidates_per_grep_max"] = max(distinct_counts)
    out["hits_per_grep_median"] = st.median(hit_counts)
if rank_of_pick:
    top1 = sum(1 for r in rank_of_pick if r == 1)
    top3 = sum(1 for r in rank_of_pick if r <= 3)
    out["chosen_rank_median"] = st.median(rank_of_pick)
    out["chosen_rank_mean"] = round(st.mean(rank_of_pick), 2)
    out["grep_order_top1_pct"] = round(100 * top1 / len(rank_of_pick), 2)
    out["grep_order_top3_pct"] = round(100 * top3 / len(rank_of_pick), 2)
    out["baseline_note"] = (
        "grep_order_top1_pct is the deterministic baseline a reranker must beat"
    )

print(json.dumps(out, indent=2))
with open(
    os.path.expanduser("~/Developer/jev/notes/rerank-label-scan.json"), "w"
) as fh:
    json.dump(out, fh, indent=2)
