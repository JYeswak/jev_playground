"""jev-wbel enforcement replay: extract 7d real skill loads with request + usage (keyless)."""

import os, glob, json, random, datetime, re

BASE = datetime.datetime(2026, 9, 25, 15, 0, tzinfo=datetime.timezone.utc).timestamp()
SEED = 20261002
N = 200
FAKE = ("/tmp/", "/var/folders/", "/private-tmp", "/private/var/folders")


def is_skill_read(p):
    if not isinstance(p, str) or not p:
        return False
    if p.startswith(FAKE):
        return False
    if p.startswith("skill://"):
        rest = p[len("skill://") :]
        return bool(rest) and ".." not in rest
    return p.endswith("SKILL.md")


def skill_of(p):
    if p.startswith("skill://"):
        segs = p[len("skill://") :].split("/")
        if segs and segs[-1] in ("SKILL.md",):
            segs = segs[:-1]
        return "/".join(segs)
    m = re.search(r"/([^/]+)/SKILL\.md$", p)
    return m.group(1) if m else p


def text_of(msg):
    c = msg.get("content")
    if isinstance(c, list):
        return " ".join(
            b.get("text", "")
            for b in c
            if isinstance(b, dict)
            and b.get("type") == "text"
            and isinstance(b.get("text"), str)
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
            fp = os.path.join(d, n)
            try:
                if os.path.getmtime(fp) >= BASE:
                    files.append(fp)
            except OSError:
                pass
print("files=%d" % len(files), flush=True)

rows = []
for fp in files:
    ps = fp.split("/")
    prof = ps[ps.index("profiles") + 1] if "profiles" in ps else "root"
    try:
        fh = open(fp, errors="replace")
    except OSError:
        continue
    with fh:
        last_user = ""
        pending = []  # toolCalls seen since last user turn (for usage attribution below)
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
            if m.get("role") == "user":
                last_user = text_of(m)[:2000]
                pending = []
            elif m.get("role") == "assistant" and isinstance(m.get("content"), list):
                for b in m["content"]:
                    if not (isinstance(b, dict) and b.get("type") == "toolCall"):
                        continue
                    nm = b.get("name")
                    args = b.get("arguments") or {}
                    if nm == "read" and is_skill_read(args.get("path")):
                        rows.append(
                            {
                                "ts": o.get("timestamp"),
                                "profile": prof,
                                "session": os.path.basename(fp)[-40:],
                                "path": args.get("path"),
                                "skill": skill_of(args.get("path")),
                                "request": last_user,
                                "following": [],
                            }
                        )
                        pending.append(len(rows) - 1)
                    elif pending and nm in (
                        "bash",
                        "read",
                        "write",
                        "edit",
                        "eval",
                        "glob",
                        "grep",
                        "find",
                    ):
                        arg = args.get("command") or args.get("path") or ""
                        for ri in pending[-3:]:
                            if len(rows[ri]["following"]) < 6:
                                rows[ri]["following"].append(
                                    "%s %s" % (nm, str(arg)[:160])
                                )
print("loads=%d" % len(rows), flush=True)

rnd = random.Random(SEED)
idx = list(range(len(rows)))
rnd.shuffle(idx)
sample = [dict(rows[i], sample_id="r%03d" % k) for k, i in enumerate(idx[:N])]
with open("/Users/josh/Developer/jev/work/wbel/replay-corpus.json", "w") as fh:
    json.dump(sample, fh)
h = (
    __import__("hashlib")
    .sha256(json.dumps(sample, sort_keys=True).encode())
    .hexdigest()[:12]
)
print("sample=%d sha=%s" % (len(sample), h), flush=True)
