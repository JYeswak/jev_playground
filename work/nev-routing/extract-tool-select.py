#!/usr/bin/env python3
"""Tool-select harvest extraction (k9z.3 retry input), v3 pattern.

Walks omp session JSONL. On each assistant toolCall block, takes the most
recent user text (else preceding assistant text/intent) within a 6-event
window as context; label = tool name called. Rows with no context in window
go to the unlabelled file (never scored as negatives).

Label is a PROXY ("called next", not "was correct"). P1 caveats carried:
basename collisions inflate; only contexts followed by a tool call yield rows.

PRIVACY: full-text pairs go to /tmp (local scoring only, never committed).
Committed: salted-hash rows (sha256(salt+context), label, len) + aggregates.
Salt is stored: anyone can verify a suspected context by recomputation
without reading the others.

Read-only over session logs. No network. No API key. Deterministic:
sorted files, no sampling, documented caps.
"""
import json, glob, os, re, sys, hashlib, secrets, collections

FILES = sorted(glob.glob(os.path.expanduser("~/.omp/profiles/*/agent/sessions/**/*.jsonl"), recursive=True))
FILES += sorted(glob.glob(os.path.expanduser("~/.omp/agent/sessions/**/*.jsonl"), recursive=True))
FILES = [f for f in FILES if os.path.getsize(f) <= 25_000_000]

TMP_PAIRS = "/tmp/tool-select-pairs.jsonl"
TMP_UNLAB = "/tmp/tool-select-unlabelled.jsonl"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))
HASHED = os.path.join(OUT_DIR, "tool-select-hashed.jsonl")
AGG = os.path.join(OUT_DIR, "tool-select-extract.json")

WINDOW = 6
CTX_CAP = 500
STOP = set("a an the and or of to in on for with is are was were be by as at it its this that what which who how when from into over under then than so such no not only own same too very can will just don should now".split())


def text_of_content(content):
    parts = []
    if isinstance(content, list):
        for b in content:
            if not isinstance(b, dict):
                continue
            if b.get("type") == "text" and isinstance(b.get("text"), str):
                parts.append(b["text"])
            elif b.get("type") in ("toolCall",):
                parts.append("")
    elif isinstance(content, str):
        parts.append(content)
    return "\n".join(p for p in parts if p)


def toks(s):
    return [t for t in re.findall(r"[a-z0-9]+", s.lower()) if t not in STOP]


def main():
    salt = secrets.token_hex(8)
    pairs, unlab = [], []
    files_scanned, toolcalls_seen = 0, 0
    for fp in FILES:
        files_scanned += 1
        recent = collections.deque(maxlen=WINDOW)
        try:
            fh = open(fp, errors="replace")
        except OSError:
            continue
        with fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                if d.get("type") != "message":
                    continue
                m = d.get("message") or {}
                role = m.get("role")
                content = m.get("content")
                calls = []
                if isinstance(content, list):
                    for b in content:
                        if isinstance(b, dict) and b.get("type") == "toolCall" and b.get("name"):
                            calls.append(b.get("name"))
                if role == "user":
                    t = text_of_content(content)
                    if t.strip():
                        recent.append(("user", t))
                elif role == "assistant":
                    t = text_of_content(content)
                    if t.strip():
                        recent.append(("assistant", t))
                for name in calls:
                    toolcalls_seen += 1
                    ctx = ""
                    for kind, text in reversed(recent):
                        if kind == "user" and text.strip():
                            ctx = text
                            break
                    if not ctx:
                        for kind, text in reversed(recent):
                            if text.strip():
                                ctx = text
                                break
                    if ctx.strip():
                        pairs.append({"file": fp, "context": ctx[:CTX_CAP], "label": name})
                    else:
                        unlab.append({"file": fp, "label": name})
                recent.append(("assistant-tool", ""))
    with open(TMP_PAIRS, "w") as fh:
        for p in pairs:
            fh.write(json.dumps(p) + "\n")
    with open(TMP_UNLAB, "w") as fh:
        for p in unlab:
            fh.write(json.dumps(p) + "\n")
    with open(HASHED, "w") as fh:
        fh.write(json.dumps({"salt": salt}) + "\n")
        for p in pairs:
            fh.write(json.dumps({
                "h": hashlib.sha256((salt + p["context"]).encode()).hexdigest()[:16],
                "label": p["label"], "len": len(p["context"]),
            }) + "\n")
    labels = collections.Counter(p["label"] for p in pairs)
    agg = {"files_scanned": files_scanned, "toolcalls_seen": toolcalls_seen,
           "labelled_pairs": len(pairs), "unlabelled": len(unlab),
           "label_counts": dict(labels.most_common()),
           "tmp_pairs": TMP_PAIRS, "hashed": HASHED,
           "no_claim": "labels are proxy (called-next); basename collisions inflate; yield over tool-followed contexts only"}
    with open(AGG, "w") as fh:
        json.dump(agg, fh, indent=2)
    print(json.dumps({k: v for k, v in agg.items() if k != "label_counts"}, indent=2))
    print("labels:", dict(labels.most_common(12)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
