#!/usr/bin/env python3
"""outcome-census instances: 50 per class with file+turn pointers (keyless).

Labeling display re-reads turn windows around each pointer, so instances stay
small. Reference/use judgments happen at label time from displayed text.
Memory instances anchor on tag-bearing LINES (memories arrive in system
context, not assistant text).
"""

import os, glob, json, re, random, datetime, hashlib

BASE = (
    datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=7)
).timestamp()
SEED = 20261005
N = 50
ZB = "/Users/josh/Developer/jev/work/outcome-census"

TESTCMD = re.compile(
    r"(pytest|uv run.*test|bun test|npm test|node --test|go test|cargo test)\b"
)
TARGETED = re.compile(r"\s-k\s|--filter|::|test_\w+\.(py|ts|js)$|\.test\.(ts|js|mjs)$")
SKILL_RE = re.compile(r"skill://([A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)?)")


def text_of(msg):
    c = msg.get("content")
    if isinstance(c, list):
        return "\n".join(
            b.get("text", "")
            for b in c
            if isinstance(b, dict) and isinstance(b.get("text"), str)
        )
    return c if isinstance(c, str) else ""


def skill_bytes(skill):
    segs = [x for x in skill.split("/") if x]
    for root in (
        os.path.expanduser("~/.claude/skills"),
        os.path.expanduser("~/.agents/skills"),
    ):
        try:
            return os.path.getsize(os.path.join(root, *segs, "SKILL.md"))
        except OSError:
            continue
    return 0


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

pool = {"skill": [], "long": [], "test": [], "memory": []}

for fp in files:
    try:
        with open(fp, errors="replace") as fh:
            lines = fh.read().split("\n")
    except OSError:
        continue
    parsed = []
    for line in lines:
        if not line.strip():
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
        parsed.append((line, o))
    for idx, (line, o) in enumerate(parsed):
        m = o.get("message")
        if not isinstance(m, dict):
            continue
        if "<memories>" in line:
            nxt = " ".join(
                l[:200]
                for _, p in parsed[idx : idx + 3]
                for l in [json.dumps(p.get("message", {}))[:200]]
            )
            pool["memory"].append(
                {"file": fp, "line": idx, "size": len(line), "peek": nxt[:600]}
            )
    turns = []
    for line, o in parsed:
        m = o.get("message")
        if not (
            isinstance(m, dict)
            and m.get("role") == "assistant"
            and isinstance(m.get("content"), list)
        ):
            continue
        tools = [
            (
                b.get("name"),
                str(
                    (b.get("arguments") or {}).get("command")
                    or (b.get("arguments") or {}).get("path")
                    or ""
                )[:200],
            )
            for b in m["content"]
            if isinstance(b, dict) and b.get("type") == "toolCall"
        ]
        turns.append({"tools": tools, "text": text_of(m)[:2000]})
        if "<memories>" in text_of(m):
            pool["memory"].append(
                {
                    "file": fp,
                    "size": len(text_of(m)),
                    "turn": len(turns) - 1,
                    "peek": "",
                }
            )
    # walk toolResults in order with turn positions
    ti = 0
    for line, o in parsed:
        m = o.get("message")
        if not isinstance(m, dict):
            continue
        if m.get("role") == "assistant" and isinstance(m.get("content"), list):
            ti += 1
            for nm, arg in [
                (
                    b.get("name"),
                    str(
                        (b.get("arguments") or {}).get("command")
                        or (b.get("arguments") or {}).get("path")
                        or ""
                    )[:200],
                )
                for b in m["content"]
                if isinstance(b, dict) and b.get("type") == "toolCall"
            ]:
                if nm == "bash" and TESTCMD.search(arg):
                    pool["test"].append(
                        {
                            "file": fp,
                            "cmd": arg[:200],
                            "full": not bool(TARGETED.search(arg)),
                            "turn": ti,
                        }
                    )
                if nm in ("read", "bash"):
                    for sk in SKILL_RE.findall(arg):
                        pool["skill"].append(
                            {
                                "file": fp,
                                "skill": sk,
                                "bytes": skill_bytes(sk),
                                "turn": ti,
                            }
                        )
            continue
        if m.get("role") == "toolResult":
            txt = text_of(m)
            if len(txt) > 10000:
                words = [w for w in txt.split() if len(w) >= 40]
                if words:
                    pool["long"].append(
                        {
                            "file": fp,
                            "size": len(txt),
                            "probe": words[len(words) // 2][:60],
                            "turn": ti,
                        }
                    )
print({k: len(v) for k, v in pool.items()}, flush=True)

rnd = random.Random(SEED)
out = {}
for cls, rows in pool.items():
    rnd.shuffle(rows)
    out[cls] = []
    for k, r in enumerate(rows[:N]):
        r = dict(r)
        r["sample_id"] = "%s%02d" % (cls[0], k)
        out[cls].append(r)
with open(ZB + "/instances.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh)
h = hashlib.sha256(json.dumps(out, sort_keys=True).encode()).hexdigest()[:12]
print("sampled 50x4 sha=%s" % h, flush=True)
