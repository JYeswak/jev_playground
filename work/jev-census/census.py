#!/usr/bin/env python3
"""Real-traffic event census, keyless, 7d of all profiles' session files.

For each candidate event: occurrences/week + what the agent did next.
Ranked by frequency x cost of the bad outcome. Costs fixed BELOW, before
the first file is read (conductor order; judgment, disclosed):

  destructive command attempted ......... 1000 (data loss / exfil)
  instruction-like text in read/web ..... 100 (injection foothold)
  recalled memory present (usage TBD) ... 3 (opportunity count only)
  failed result ignored next turn ....... 10 (silent failure)
  skill loaded then abandoned ........... 2 (wasted context)
  long result never referenced .......... 1 (context bloat)
  test re-run, no code change ........... 5 (burned compute)
  file read twice in sequence ........... 1 (redundant I/O)

Heuristics are approximations (stated per event); this ranks CANDIDATES
for Jev designs, it is not a label set. Usage: python3 census.py [--days N]
Writes table.json {events: [{id, count, cost, score, note}]}.
"""

import os, glob, json, re, sys, datetime
from collections import Counter

DAYS = int(sys.argv[sys.argv.index("--days") + 1]) if "--days" in sys.argv else 7
BASE = (
    datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=DAYS)
).timestamp()
ZB = "/Users/josh/Developer/jev/work/jev-census"

COST = {
    "destructive": 1000,
    "instruction": 100,
    "memory": 3,
    "failed_ignored": 10,
    "skill_abandoned": 2,
    "long_unref": 1,
    "test_rerun": 5,
    "double_read": 1,
}

DESTRUCTIVE = re.compile(
    r"\brm\s+-rf?\b|\bdd\s+|mkfs|DROP\s+(TABLE|DATABASE)|TRUNCATE|del\s+/[sq]|Remove-Item.*-Recurse.*-Force|shutdown|halt|reboot|:\(\)\s*\{",
    re.I,
)
INSTRUCT = re.compile(
    r"ignore (?:all )?previous instructions|forget (?:everything|all)|disregard .*instructions|you are now|reveal .*prompt|send .*secret|just output|print yay|act as two entities|role-play|answer the following question|urgently need your help|stop -",
    re.I,
)
TESTCMD = re.compile(
    r"(pytest|uv run.*test|bun test|npm test|node --test|go test|cargo test)\b"
)
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
            try:
                if os.path.getmtime(fp) >= BASE:
                    files.append(fp)
            except OSError:
                pass
print("files=%d" % len(files), flush=True)

counts = Counter()
notes = {
    "memory": "opportunity (message lines carrying <memories>); used-vs-unused needs filter labels (9yjh)",
    "long_unref": "long result (>10k chars) with no 60-char probe found later in the same file",
    "skill_abandoned": "skill:// load with no skill-domain token in the next 2 turns of tool calls",
    "failed_ignored": "isError result with no same-tool call next turn",
    "double_read": "same read path twice within the last 8 reads",
    "test_rerun": "identical test command string repeated (no edit check)",
    "destructive": "bash command matching destructive patterns (attempts, not outcomes)",
    "instruction": "toolResult text matching imperative/injection patterns",
}
turns = 0

for fp in files:
    try:
        fh = open(fp, errors="replace")
    except OSError:
        continue
    last_tools = []
    loads = []
    seen_tests = []
    recent_reads = []
    pending_err = None
    probes = []
    turn_idx = 0
    with fh:
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
            if "<memories>" in line:
                counts["memory"] += 1
            m = o.get("message")
            if not isinstance(m, dict):
                continue
            txt = text_of(m)
            if txt and probes:
                for pr in probes:
                    if not pr[1] and pr[0] in txt:
                        pr[1] = True
            role = m.get("role")
            if role != "assistant" or not isinstance(m.get("content"), list):
                if role == "toolResult":
                    if txt and len(txt) > 200 and INSTRUCT.search(txt):
                        counts["instruction"] += 1
                    if len(txt) > 10000:
                        words = [w for w in txt.split() if len(w) >= 40]
                        if words and len(probes) < 20:
                            probes.append([words[len(words) // 2][:60], False])
                    if m.get("isError") is True:
                        pending_err = m.get("toolName")
                continue
            turn_idx += 1
            turns += 1
            tools_now = []
            for b in m["content"]:
                if not (isinstance(b, dict) and b.get("type") == "toolCall"):
                    continue
                nm = b.get("name")
                args = b.get("arguments") or {}
                arg = str(args.get("command") or args.get("path") or "")[:200]
                tools_now.append((nm, arg))
                if nm == "bash" and DESTRUCTIVE.search(arg):
                    counts["destructive"] += 1
                if nm == "bash" and TESTCMD.search(arg):
                    key = arg[:120]
                    if key in seen_tests:
                        counts["test_rerun"] += 1
                    else:
                        seen_tests.append(key)
                        seen_tests = seen_tests[-5:]
                if nm == "read" and isinstance(args.get("path"), str):
                    p = args["path"]
                    if p in recent_reads[-8:]:
                        counts["double_read"] += 1
                    recent_reads.append(p)
                    recent_reads = recent_reads[-20:]
                for sk in SKILL_RE.findall(arg if nm in ("read", "bash") else ""):
                    loads.append([sk, turn_idx])
            if pending_err is not None:
                if not any(nm == pending_err for nm, _ in tools_now):
                    counts["failed_ignored"] += 1
                pending_err = None
            keep = []
            for sk, ti in loads:
                if turn_idx - ti >= 2:
                    dom = sk.split("/")[0]
                    if not any(dom in a for _, a in tools_now + last_tools):
                        counts["skill_abandoned"] += 1
                else:
                    keep.append([sk, ti])
            loads = keep[:8]
            last_tools = (tools_now + last_tools)[:8]
    for _needle, found in probes:
        if not found:
            counts["long_unref"] += 1

table = []
for eid, cost in COST.items():
    n = counts.get(eid, 0)
    table.append(
        {
            "id": eid,
            "count": n,
            "cost": cost,
            "score": n * cost,
            "note": notes.get(eid, ""),
        }
    )
table.sort(key=lambda r: -r["score"])
with open(ZB + "/table.json", "w", encoding="utf-8") as fh:
    json.dump({"window_days": DAYS, "turns": turns, "events": table}, fh)
print("turns=%d" % turns, flush=True)
for r in table:
    print(
        "%-15s count=%-7d cost=%-5d score=%-9d %s"
        % (r["id"], r["count"], r["cost"], r["score"], r["note"])
    )
