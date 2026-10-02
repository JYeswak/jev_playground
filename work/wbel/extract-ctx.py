"""wbel fix ctx: preceding task tool calls per dev corpus row (keyless, deployable context)."""

import os, glob, json

ZB = "/Users/josh/Developer/jev/work/wbel"
with open(ZB + "/replay-corpus.json") as fh:
    corpus = json.load(fh)

roots = ["/Users/josh/.omp/agent/sessions"] + glob.glob(
    "/Users/josh/.omp/profiles/*/agent/sessions"
)
index = {}
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
            index.setdefault(n[-40:], []).append(os.path.join(d, n))

TASK = ("bash", "read", "write", "edit", "eval", "glob", "grep", "find")
out = {}
for row in corpus:
    sid = row["sample_id"]
    cands = index.get(row["session"], [])
    prec = []
    for fp in cands:
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
                if o.get("timestamp") != row["ts"]:
                    m = o.get("message")
                    if (
                        isinstance(m, dict)
                        and m.get("role") == "assistant"
                        and isinstance(m.get("content"), list)
                    ):
                        for b in m["content"]:
                            if (
                                isinstance(b, dict)
                                and b.get("type") == "toolCall"
                                and b.get("name") in TASK
                            ):
                                a = b.get("arguments") or {}
                                arg = a.get("command") or a.get("path") or ""
                                prec.append("%s %s" % (b.get("name"), str(arg)[:160]))
                                prec = prec[-6:]
                    continue
                break
    out[sid] = prec
with open(ZB + "/replay-devctx.json", "w") as fh:
    json.dump(out, fh)
n = len(out)
cov = sum(1 for v in out.values() if v)
print("rows=%d with-preceding=%d" % (n, cov), flush=True)
