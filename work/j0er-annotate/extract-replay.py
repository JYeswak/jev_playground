"""j0er-annotate replay corpus: recent web/read toolResults from non-jev repos (keyless)."""

import os, glob, json, random, datetime, hashlib

BASE = datetime.datetime(2026, 9, 25, 17, 0, tzinfo=datetime.timezone.utc).timestamp()
SEED = 20261002
N = 100
TOOLS = ("web_search", "web_extract", "fetch", "open_url", "read")
ZB = "/Users/josh/Developer/jev/work/j0er-annotate"


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
        if "jev" in s.lower() or "private-tmp" in s or "nvtest" in s:
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
                    files.append((s, fp))
            except OSError:
                pass
print("files=%d" % len(files), flush=True)

rows = []
for slug, fp in files:
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
            if not (isinstance(m, dict) and m.get("role") == "toolResult"):
                continue
            if m.get("toolName") not in TOOLS:
                continue
            if m.get("isError") is True:
                continue
            txt = text_of(m)
            if len(txt.strip()) < 40:
                continue
            rows.append(
                {
                    "ts": o.get("timestamp"),
                    "slug": slug,
                    "session": os.path.basename(fp)[-40:],
                    "tool": m.get("toolName"),
                    "text": txt[:12000],
                }
            )
print("results=%d" % len(rows), flush=True)

rnd = random.Random(SEED)
idx = list(range(len(rows)))
rnd.shuffle(idx)
sample = [dict(rows[i], sample_id="w%03d" % k) for k, i in enumerate(idx[:N])]
with open(ZB + "/corpus.json", "w", encoding="utf-8") as fh:
    json.dump(sample, fh)
h = hashlib.sha256(json.dumps(sample, sort_keys=True).encode()).hexdigest()[:12]
print("sample=%d sha=%s" % (len(sample), h), flush=True)
