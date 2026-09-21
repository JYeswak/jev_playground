#!/usr/bin/env python3
"""Re-extract labelled grep->read pairs with the query and a snippet per file.

notes/rerank-label-scan.py v2 discarded the lists after counting. This writes
one JSONL row per labelled pair so a live scorer can be audited. Same session
roots, same window, same basename label. Adds pattern, intent, and hit lines.
"""

import collections, datetime, glob, json, os, re, statistics as st, sys

BRACKET = re.compile(r"^\s*\[([^\]\s]+?)(?:#[0-9A-Fa-f]{4})?\]\s*$")
DIRHDR = re.compile(r"^#\s+(\S+/)\s*$")
FILEHDR = re.compile(r"^##\s+(\S+?)(?:#[0-9A-Fa-f]{4})?\s*$")
COLON = re.compile(r"^\s*([^\s:]+\.[A-Za-z0-9_]{1,6}):\d+:(.*)$")
CONTENT = re.compile(r"^\s*\*?\d+:(.*)$")
WINDOW = 6
SNIP_LINES = 8
SNIP_CHARS = 600


def base(p):
    p = (p or "").split(":")[0].strip()
    return os.path.basename(p) if p else ""


def parse_candidates(text):
    """Basename order matching v2, plus a short snippet of hit lines per file."""
    order, seen, snippets, forms = [], set(), {}, collections.Counter()
    curdir, cur = "", None

    def add(path, kind, extra=None):
        nonlocal cur
        b = base(path)
        if not b:
            return
        if b not in seen:
            seen.add(b)
            order.append(b)
            snippets[b] = []
            forms[kind] += 1
        cur = b
        if extra:
            snippets[b].append(extra.strip())

    for line in text.split("\n"):
        if not line.strip() or line.strip() == "...":
            cur = None
            continue
        m = BRACKET.match(line)
        if m:
            add(m.group(1), "bracket")
            continue
        m = DIRHDR.match(line)
        if m:
            curdir = m.group(1)
            cur = None
            continue
        m = FILEHDR.match(line)
        if m:
            add(curdir + m.group(1), "hdr2")
            continue
        m = COLON.match(line)
        if m:
            add(m.group(1), "colon", m.group(2))
            continue
        m = CONTENT.match(line)
        if m and cur:
            snippets[cur].append(m.group(1).strip())
    packed = []
    for b in order:
        snip = "\n".join(snippets.get(b, [])[:SNIP_LINES])[:SNIP_CHARS]
        packed.append({"file": b, "snippet": snip})
    return packed, forms


def session_files():
    files = glob.glob(
        os.path.expanduser("~/.omp/profiles/*/agent/sessions/**/*.jsonl"),
        recursive=True,
    )
    files += glob.glob(
        os.path.expanduser("~/.omp/agent/sessions/**/*.jsonl"), recursive=True
    )
    return [f for f in files if os.path.getsize(f) <= 25_000_000]


def events_of(path):
    events, pend = [], {}
    with open(path, encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if '"toolCall"' not in line and '"toolResult"' not in line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("type") != "message":
                continue
            msg = obj.get("message") or {}
            content = msg.get("content")
            if not isinstance(content, list):
                continue
            for item in content:
                if not isinstance(item, dict):
                    continue
                if item.get("type") == "toolCall":
                    name, tid = item.get("name"), item.get("id")
                    if name == "grep" and tid:
                        args = item.get("arguments") or {}
                        if isinstance(args, str):
                            try:
                                args = json.loads(args)
                            except json.JSONDecodeError:
                                args = {}
                        pend[tid] = args if isinstance(args, dict) else {}
                    elif name == "read":
                        args = item.get("arguments") or {}
                        if isinstance(args, str):
                            try:
                                args = json.loads(args)
                            except json.JSONDecodeError:
                                args = {}
                        events.append(
                            (
                                "read",
                                base(
                                    args.get("path") if isinstance(args, dict) else ""
                                ),
                            )
                        )
                else:
                    tid = (
                        msg.get("toolCallId")
                        or item.get("toolCallId")
                        or obj.get("toolCallId")
                    )
                    if tid and tid in pend:
                        args = pend.pop(tid)
                        events.append(("g", item.get("text") or "", args))
    return events


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else "work/nev-rerank/pairs.jsonl"
    rows, ranks, forms = [], [], collections.Counter()
    greps = big = reads = pairs = labelled = scanned = 0
    for path in session_files():
        try:
            ev = events_of(path)
        except Exception:
            continue
        scanned += 1
        for i, event in enumerate(ev):
            if event[0] == "read":
                reads += 1
                continue
            if event[0] != "g":
                continue
            greps += 1
            text, args = event[1], event[2]
            hit_lines = [ln for ln in text.split("\n") if ln.strip()]
            if len(hit_lines) < 10:
                continue
            big += 1
            cands, got = parse_candidates(text)
            forms.update(got)
            if len(cands) < 2:
                continue
            nxt = None
            for kind, name in ((e[0], e[1]) for e in ev[i + 1 : i + 1 + WINDOW]):
                if kind == "read" and name:
                    nxt = name
                    break
            if not nxt:
                continue
            pairs += 1
            if nxt not in {c["file"] for c in cands}:
                continue
            labelled += 1
            rank = next(n for n, c in enumerate(cands, 1) if c["file"] == nxt)
            ranks.append(rank)
            rows.append(
                {
                    "id": f"{os.path.basename(path)}:{i}",
                    "session": path,
                    "query": str(args.get("pattern") or ""),
                    "intent": str(args.get("i") or ""),
                    "path": str(args.get("path") or ""),
                    "candidates": cands,
                    "label": nxt,
                    "label_rank": rank,
                    "hits": len(hit_lines),
                }
            )
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    top1 = sum(1 for r in ranks if r == 1)
    summary = {
        "generated_at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "parser": "extract-pairs.py",
        "session_files_scanned": scanned,
        "grep_results_seen": greps,
        "grep_results_ge10_lines": big,
        "read_calls_seen": reads,
        "grep_then_read_pairs": pairs,
        "labelled_pairs": labelled,
        "grep_order_top1": top1,
        "grep_order_top1_pct": round(100 * top1 / labelled, 2) if labelled else None,
        "chosen_rank_median": st.median(ranks) if ranks else None,
        "header_forms": dict(forms),
        "corpus_path": out_path,
        "v2_target": {"labelled_pairs": 219, "grep_order_top1_pct": 26.48},
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
