#!/usr/bin/env python3
"""failtriage track A: deterministic failed-then-ignored detector (keyless).

A would-nudge fires when a tool result carries a failure signal AND the next
assistant turn neither retries (same tool), fixes (edit/write present), nor
mentions (error/command tokens in turn text) it. Heuristic, disclosed; the
blind labels (not this rule) decide the bar. Overlapping failures: a newer
failure replaces a still-open one (noted as looseness).

Failure signals: isError, nonzero exit (exit N / exitCode N / rc=N / Exit N,
N>0), Traceback, Error:/error:, FAILED/FAIL, Fatal, permission denied,
command not found, No such file, EACCES/ENOENT, panic.
"""

import os, glob, json, re, random, datetime, hashlib

BASE = (
    datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=7)
).timestamp()
SEED = 20261002
N = 100
ZB = "/Users/josh/Developer/jev/work/failtriage"

EXIT = re.compile(
    r"\b(?:exit(?: code)?|exitCode|rc)\s*[:=]?\s*([1-9]\d*)\b|\bExit ([1-9]\d*)\b"
)
TEXTFAIL = re.compile(
    r"Traceback \(most recent call last\)|Error:|error:|FAILED|\bFAIL\b|Fatal|permission denied|command not found|No such file|EACCES|ENOENT|panic\b",
    re.I,
)
TOK = lambda s: set(w for w in re.findall(r"[a-z0-9_.-]+", s.lower()) if len(w) > 4)


def text_of(msg):
    c = msg.get("content")
    if isinstance(c, list):
        return "\n".join(
            b.get("text", "")
            for b in c
            if isinstance(b, dict) and isinstance(b.get("text"), str)
        )
    return c if isinstance(c, str) else ""


def fail_span(txt):
    out = []
    for line in txt.split("\n"):
        if len(out) >= 5:
            break
        s = line.strip()
        if not s:
            continue
        if EXIT.search(s) or TEXTFAIL.search(s):
            out.append(s[:200])
    if not out:
        for line in txt.split("\n"):
            if line.strip():
                out.append(line.strip()[:200])
            if len(out) >= 5:
                break
    return out


roots = ["/Users/josh/.omp/agent/sessions"] + glob.glob(
    "/Users/josh/.omp/profiles/*/agent/sessions"
)
files = []
for r in roots:
    try:
        slugs = os.listdir(r)
    except OSError:
        continue
    for s in slugs:
        d = os.path.join(r, s)
        if not os.path.isdir(d):
            continue
        try:
            names = [
                x
                for x in os.listdir(d)
                if x.endswith(".jsonl") and not x.startswith(".")
            ]
        except OSError:
            continue
        for n in names:
            fp = os.path.join(d, n)
            try:
                if os.path.getmtime(fp) >= BASE:
                    files.append(fp)
            except OSError:
                pass
print("files=%d" % len(files), flush=True)

cands, turns = [], 0
for fp in files:
    try:
        fh = open(fp, errors="replace")
    except OSError:
        continue
    with fh:
        pending = None
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
            except json.JSONDecodeError:
                continue
            try:
                t = datetime.datetime.fromisoformat(
                    str(o.get("timestamp")).replace("Z", "+00:00")
                ).timestamp()
            except (ValueError, TypeError):
                continue
            if t < BASE:
                continue
            m = o.get("message")
            if not isinstance(m, dict):
                continue
            role = m.get("role")
            txt = text_of(m)
            if role == "toolResult" and txt:
                failed = (
                    m.get("isError") is True
                    or bool(EXIT.search(txt))
                    or bool(TEXTFAIL.search(txt))
                )
                if failed:
                    toks = TOK(txt[:2000])
                    pending = {
                        "tool": m.get("toolName", ""),
                        "span": fail_span(txt),
                        "errtoks": sorted(toks)[:20],
                        "collect": [],
                    }
                continue
            if role != "assistant" or not isinstance(m.get("content"), list):
                continue
            turn_idx_note = turns
            turns += 1
            if pending is None:
                continue
            if len(pending["collect"]) >= 2:
                continue
            tools = [
                (
                    b.get("name"),
                    str(
                        (b.get("arguments") or {}).get("command")
                        or (b.get("arguments") or {}).get("path")
                        or ""
                    )[:160],
                )
                for b in m["content"]
                if isinstance(b, dict) and b.get("type") == "toolCall"
            ]
            pending["collect"].append({"text": txt[:1500], "tools": tools})
            if len(pending["collect"]) == 2:
                t1, t2 = pending["collect"]
                retry = any(
                    nm == pending["tool"]
                    for turn in (t1, t2)
                    for nm, _ in turn["tools"]
                )
                fix = any(
                    nm in ("edit", "write")
                    for turn in (t1, t2)
                    for nm, _ in turn["tools"]
                )
                words = set()
                for turn in (t1, t2):
                    words |= set(re.findall(r"[a-z0-9_.-]+", turn["text"].lower()))
                mention = any(w in words for w in pending["errtoks"][:8])
                if not (retry or fix or mention):
                    cands.append(
                        {
                            "tool": pending["tool"],
                            "span": pending["span"],
                            "next2": pending["collect"],
                        }
                    )
                pending = None
print("turns=%d candidates=%d" % (turns, len(cands)), flush=True)

rnd = random.Random(SEED)
idx = list(range(len(cands)))
rnd.shuffle(idx)
sample = []
for k, i in enumerate(idx[:N]):
    c = cands[i]
    sample.append(
        {
            "sample_id": "f%03d" % k,
            "tool": c["tool"],
            "span": c["span"],
            "next2": c["next2"],
        }
    )
with open(ZB + "/candidates.json", "w", encoding="utf-8") as fh:
    json.dump(sample, fh)
h = hashlib.sha256(json.dumps(sample, sort_keys=True).encode()).hexdigest()[:12]
print("sample=%d sha=%s" % (len(sample), h), flush=True)
