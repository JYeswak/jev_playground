"""locks census: raw vs serialized git commits by pane since 01:00Z (keyless)."""

import os, glob, json, re, datetime

BASE = datetime.datetime(2026, 10, 2, 1, 0, tzinfo=datetime.timezone.utc).timestamp()
ZB = "/Users/josh/Developer/jev/work/locks"

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
        if "jev" not in s.lower():
            continue
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

REC = {}


def rec(sid):
    return REC.setdefault(sid, {"agent": None, "pane": None, "raw": 0, "ser": 0})


for fp in files:
    sid = os.path.basename(fp)[:60]
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
            if m.get("role") == "user" and isinstance(m.get("content"), list):
                txt = " ".join(
                    b.get("text", "") for b in m["content"] if isinstance(b, dict)
                )
                mm = re.search(r"CONDUCTOR \(pane 1\) to ([A-Za-z]+)", txt)
                if mm:
                    rec(sid)["agent"] = mm.group(1)
                mm2 = re.search(r"\bIDLE pane (\d)\b", txt)
                if mm2:
                    rec(sid)["pane"] = mm2.group(1)
            if m.get("role") == "assistant" and isinstance(m.get("content"), list):
                for b in m["content"]:
                    if not (
                        isinstance(b, dict)
                        and b.get("type") == "toolCall"
                        and b.get("name") == "bash"
                    ):
                        continue
                    cmd = str((b.get("arguments") or {}).get("command", ""))
                    if "git-commit-serialized" in cmd:
                        rec(sid)["ser"] += 1
                    elif re.search(r"(^|[;&|]|&&|\$\()git commit\b", cmd):
                        rec(sid)["raw"] += 1
                    elif cmd.strip().startswith("git commit"):
                        rec(sid)["raw"] += 1

rows = [dict(session=k, **v) for k, v in sorted(REC.items()) if v["raw"] or v["ser"]]
with open(ZB + "/counts.json", "w", encoding="utf-8") as fh:
    json.dump(rows, fh)
tr = sum(r["raw"] for r in rows)
ts = sum(r["ser"] for r in rows)
print("sessions-with-commits=%d raw=%d serialized=%d" % (len(rows), tr, ts), flush=True)
by = {}
for r in rows:
    k = (r["agent"], r["pane"])
    b = by.setdefault(k, [0, 0])
    b[0] += r["raw"]
    b[1] += r["ser"]
for k in sorted(by, key=str):
    print("agent=%s pane=%s raw=%d ser=%d" % (k[0], k[1], by[k][0], by[k][1]))
