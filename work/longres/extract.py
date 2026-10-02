#!/usr/bin/env python3
"""longres corpus: 200 long toolResults with 3-probe reference labels (keyless)."""

import os, glob, json, re, random, datetime, hashlib

BASE = (
    datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=7)
).timestamp()
SEED = int(os.environ.get("LONGRES_SEED", "20261006"))
NDEV, NHELD = (
    int(os.environ.get("LONGRES_NDEV", "100")),
    int(os.environ.get("LONGRES_NHELD", "100")),
)
ZB = "/Users/josh/Developer/jev/work/longres"
OUT = os.environ.get("LONGRES_OUT", ZB + "/corpus.json")
EXCLUDE = os.environ.get("LONGRES_EXCLUDE", "")


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
            fp = os.path.join(d, n)
            try:
                if os.path.getmtime(fp) >= BASE:
                    files.append(fp)
            except OSError:
                pass
print("files=%d" % len(files), flush=True)

rows, volume = [], 0
for fp in files:
    try:
        with open(fp, errors="replace") as fh:
            content = fh.read().split("\n")
    except OSError:
        continue
    # collect user-task context: last user text before each result
    last_user = ""
    for i, line in enumerate(content):
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
        m = o.get("message")
        if not isinstance(m, dict):
            continue
        if m.get("role") == "user":
            last_user = text_of(m)[:500]
            continue
        if m.get("role") != "toolResult":
            continue
        txt = text_of(m)
        if len(txt) < 10000:
            continue
        volume += 1
        words = [w for w in txt.split() if len(w) >= 40]
        if len(words) < 6:
            continue
        n3 = len(words) // 3
        probes = [words[n3][:60], words[2 * n3][:60], words[-2][:60]]
        # reference: any probe later in this file
        rest = "\n".join(content[i + 1 : i + 400])
        ref = any(p in rest for p in probes)
        rows.append(
            {
                "file": fp,
                "tool": m.get("toolName", ""),
                "size": len(txt),
                "head": txt[:350],
                "tail": txt[-350:],
                "task": last_user,
                "ref": ref,
                "win_sha": hashlib.sha256(txt.encode()).hexdigest()[:12],
            }
        )
print("volume>=10k/week=%d rows=%d" % (volume, len(rows)), flush=True)

excluded = set()
if EXCLUDE == "corpus":
    with open(ZB + "/corpus.json", encoding="utf-8") as fh:
        old = json.load(fh)
    for r in old["dev"] + old["held"]:
        excluded.add(r["file"])
elif EXCLUDE:
    with open(EXCLUDE, encoding="utf-8") as fh:
        excluded = set(json.load(fh))
byfile = {}
for r in rows:
    if r["file"] in excluded:
        continue
    byfile.setdefault(r["file"], []).append(r)
flist = sorted(byfile)
rnd = random.Random(SEED)
rnd.shuffle(flist)
devfiles, heldfiles = set(flist[: len(flist) // 2]), set(flist[len(flist) // 2 :])
dev = [r for r in rows if r["file"] in devfiles]
held = [r for r in rows if r["file"] in heldfiles]
rnd.shuffle(dev)
rnd.shuffle(held)
dev, held = dev[:NDEV], held[:NHELD]
for i, r in enumerate(dev):
    r["sample_id"] = "d%03d" % i
for i, r in enumerate(held):
    r["sample_id"] = "h%03d" % i
out = {"dev": dev, "held": held, "volume": volume}
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(out, fh)
h = hashlib.sha256(json.dumps(out, sort_keys=True).encode()).hexdigest()[:12]
dp = sum(1 for r in dev if r["ref"])
hp = sum(1 for r in held if r["ref"])
print(
    "dev=%d held=%d sha=%s dev-ref=%d held-ref=%d" % (len(dev), len(held), h, dp, hp),
    flush=True,
)
