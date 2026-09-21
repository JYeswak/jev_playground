#!/usr/bin/env python3
"""v3 — PERSIST the labelled reranking pairs, not just aggregates.

v2 (notes/rerank-label-scan.py) computed candidate lists in memory, counted them and threw
them away, and never captured the grep query at all. That is R70: a number nobody but its
author can audit, and in this case one that could not have been scored even in principle
because a reranker needs something to rank AGAINST.

v3 writes one JSONL row per labelled pair containing the four things a scorer needs:
    query       the grep `pattern` argument
    intent      the grep `i` argument (natural-language ask) — this is the real query
    candidates  [{file, lines[]}] in the order grep emitted them
    label       basename the agent read next, plus its 1-indexed rank

Label is a PROXY: "the agent read it next", not "it was relevant". Rows where the read target
is absent from the candidates are UNLABELLED and are written to a separate file — they are not
negatives and must not be scored as misses.

Read-only over session logs. No network. No API key. Writes only under notes/.
"""

import json, glob, os, re, statistics as st, datetime, collections

FILES = glob.glob(
    os.path.expanduser("~/.omp/profiles/*/agent/sessions/**/*.jsonl"), recursive=True
)
FILES += glob.glob(
    os.path.expanduser("~/.omp/agent/sessions/**/*.jsonl"), recursive=True
)
FILES = [f for f in FILES if os.path.getsize(f) <= 25_000_000]

OUT_DIR = os.path.expanduser("~/Developer/jev/notes")
PAIRS = os.path.join(OUT_DIR, "rerank-labelled-pairs.jsonl")
UNLAB = os.path.join(OUT_DIR, "rerank-unlabelled-pairs.jsonl")
AGG = os.path.join(OUT_DIR, "rerank-label-scan.json")

BRACKET = re.compile(r"^\s*\[([^\]\s]+?)(?:#[0-9A-Fa-f]{4})?\]\s*$")
DIRHDR = re.compile(r"^#\s+(\S+/)\s*$")
FILEHDR = re.compile(r"^##\s+(\S+?)(?:#[0-9A-Fa-f]{4})?\s*$")
COLON = re.compile(r"^\s*([^\s:]+\.[A-Za-z0-9_]{1,6}):\d+:")
WINDOW = 6
MAX_LINES_PER_CAND = (
    12  # cap passage size; a reranker does not need 300 lines of one file
)


def base(p):
    p = (p or "").split(":")[0].strip()
    return os.path.basename(p) if p else ""


def parse_grep(text):
    """-> ([{file, lines[]}] in emission order, form Counter). Content lines attach to the
    most recent file header, which is how omp's grep output is structured."""
    order, byfile, forms = [], {}, collections.Counter()
    curdir, cur = "", None
    for l in text.split("\n"):
        s = l.strip()
        if not s or s == "...":
            continue
        f = k = None
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
        if f:
            b = base(f)
            if not b:
                continue
            forms[k] += 1
            cur = b
            if b not in byfile:
                byfile[b] = {"file": b, "path": f, "lines": []}
                order.append(b)
            if k == "colon":
                # colon form carries its content on the same line
                if len(byfile[b]["lines"]) < MAX_LINES_PER_CAND:
                    byfile[b]["lines"].append(l.rstrip()[:400])
            continue
        if cur and len(byfile[cur]["lines"]) < MAX_LINES_PER_CAND:
            byfile[cur]["lines"].append(l.rstrip()[:400])
    return [byfile[b] for b in order], forms


rows, unlab_rows = [], []
greps_seen = greps_big = reads_seen = pairs = 0
form_total = collections.Counter()
scanned = 0

for p in FILES:
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
                a = it.get("arguments") or {}
                if isinstance(a, str):
                    try:
                        a = json.loads(a)
                    except Exception:
                        a = {}
                if nm == "grep" and tid:
                    pend[tid] = {
                        "pattern": a.get("pattern"),
                        "intent": it.get("intent") or a.get("i"),
                        "path": a.get("path"),
                    }
                elif nm == "read":
                    events.append(("read", base(a.get("path"))))
            else:
                tid = (
                    msg.get("toolCallId") or it.get("toolCallId") or o.get("toolCallId")
                )
                if tid and tid in pend:
                    meta = pend.pop(tid)
                    events.append(("g", (it.get("text") or "", meta)))

    for i in range(len(events)):
        k0, v0 = events[i]
        if k0 == "read":
            reads_seen += 1
            continue
        if k0 != "g":
            continue
        greps_seen += 1
        text, meta = v0
        hl = [l for l in text.split("\n") if l.strip()]
        if len(hl) < 10:
            continue
        greps_big += 1
        cands, forms = parse_grep(text)
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
        names = [c["file"] for c in cands]
        row = {
            "session": p.replace(os.path.expanduser("~"), "~"),
            "query": meta.get("pattern"),
            "intent": meta.get("intent"),
            "scope": meta.get("path"),
            "candidates": cands,
            "n_candidates": len(cands),
            "hits": len(hl),
            "label": nxt,
        }
        if nxt in names:
            row["label_rank"] = names.index(nxt) + 1
            rows.append(row)
        else:
            row["label_rank"] = None
            row["note"] = (
                "UNLABELLED: read target absent from candidates. NOT a negative."
            )
            unlab_rows.append(row)

with open(PAIRS, "w") as fh:
    for r in rows:
        fh.write(json.dumps(r) + "\n")
with open(UNLAB, "w") as fh:
    for r in unlab_rows:
        fh.write(json.dumps(r) + "\n")

ranks = [r["label_rank"] for r in rows]
ncand = [r["n_candidates"] for r in rows]
top1 = sum(1 for r in ranks if r == 1)
top3 = sum(1 for r in ranks if r <= 3)
with_query = sum(1 for r in rows if r.get("query"))
with_intent = sum(1 for r in rows if r.get("intent"))

agg = {
    "generated_at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    "parser_version": 3,
    "corpus_path": PAIRS.replace(os.path.expanduser("~"), "~"),
    "unlabelled_path": UNLAB.replace(os.path.expanduser("~"), "~"),
    "session_files_scanned": scanned,
    "grep_results_seen": greps_seen,
    "grep_results_ge10_lines": greps_big,
    "read_calls_seen": reads_seen,
    "candidate_header_forms": dict(form_total),
    "grep_then_read_pairs": pairs,
    "labelled_pairs": len(rows),
    "unlabelled_pairs": len(unlab_rows),
    "label_yield_pct": round(100 * len(rows) / max(pairs, 1), 2),
    "rows_with_query": with_query,
    "rows_with_intent": with_intent,
    "candidates_per_grep_median": st.median(ncand) if ncand else None,
    "candidates_per_grep_max": max(ncand) if ncand else None,
    "grep_order_top1_pct": round(100 * top1 / max(len(ranks), 1), 2),
    "grep_order_top3_pct": round(100 * top3 / max(len(ranks), 1), 2),
    "chosen_rank_median": st.median(ranks) if ranks else None,
    "chosen_rank_mean": round(st.mean(ranks), 2) if ranks else None,
    "random_baseline_pct": round(100 * st.mean([1 / c for c in ncand]), 2)
    if ncand
    else None,
    "baseline_note": "grep_order_top1_pct is the deterministic baseline a reranker must beat, "
    "measured on the SAME rows persisted in corpus_path",
    "label_is_proxy": "label = file the agent read next, NOT a relevance judgment. "
    "unlabelled_pairs are NOT negatives.",
}
print(json.dumps(agg, indent=2))
with open(AGG, "w") as fh:
    json.dump(agg, fh, indent=2)
