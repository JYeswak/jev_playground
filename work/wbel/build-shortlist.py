"""wbel cookbook: inventory + per-row shortlists (keyless, frozen pre-call)."""

import os, json, re
from collections import Counter

ZB = "/Users/josh/Developer/jev/work/wbel"


def full_desc(skill):
    segs = [x for x in skill.split("/") if x]
    roots = [
        os.path.expanduser("~/.claude/skills"),
        os.path.expanduser("~/.agents/skills"),
    ]
    cands = []
    for root in roots:
        cands.append(os.path.join(root, *segs, "SKILL.md"))
        if len(segs) > 1:
            cands.append(os.path.join(root, segs[-1], "SKILL.md"))
    for f in cands:
        try:
            with open(f, encoding="utf-8") as fh:
                t = fh.read()
        except OSError:
            continue
        m = re.search(r"^description:\s*(.*?)\s*$", t, re.M)
        d = m.group(1).strip("\"'") if m else ""
        body = "---".join(t.split("---")[2:]).strip()[:700]
        if d or body:
            return (d + " — " + body)[:1200]
        return ""
    return ""


inv = {}
for root in [
    os.path.expanduser("~/.claude/skills"),
    os.path.expanduser("~/.agents/skills"),
]:
    for dirpath, dirnames, filenames in os.walk(root):
        if "SKILL.md" in filenames:
            name = os.path.relpath(dirpath, root)
            inv.setdefault(name, full_desc(name))
print(
    "inventory=%d with-desc=%d" % (len(inv), sum(1 for v in inv.values() if v)),
    flush=True,
)

tok = lambda s: set(w for w in re.findall(r"[a-z0-9]+", s.lower()) if len(w) > 3)
inv_tok = {n: tok(n + " " + d) for n, d in inv.items()}


def parent(skill):
    """Deepest leading prefix that owns a SKILL.md (reference/line-ranged loads
    map to their parent skill, per order). Falls back to the raw top segment."""
    segs = [x for x in skill.split("/") if x]
    if segs and segs[-1] in ("SKILL.md",):
        segs = segs[:-1]
    if segs and re.match(r"^.+:\d+(-\d+)?$", segs[-1]):
        segs[-1] = segs[-1].split(":")[0]
    while len(segs) > 1:
        if "/".join(segs) in inv:
            return "/".join(segs)
        segs = segs[:-1]
    return segs[0] if segs else skill


with open(ZB + "/replay-corpus.json", encoding="utf-8") as fh:
    corpus = json.load(fh)
short = {}
for r in corpus:
    p = parent(r["skill"])
    rt = tok(r["request"])
    scored = sorted(
        ((len(rt & t), n) for n, t in inv_tok.items() if n != p), reverse=True
    )
    names = [p] + [n for _, n in scored[:9]]
    short[r["sample_id"]] = {"shortlist": names, "resolved": p}
with open(ZB + "/shortlists.json", "w", encoding="utf-8") as fh:
    json.dump(short, fh)
sizes = Counter(len(v["shortlist"]) for v in short.values())
print("rows=%d sizes=%s" % (len(short), dict(sizes)), flush=True)
missing = [k for k, v in short.items() if v["resolved"] not in v["shortlist"]]
print("loaded-missing-from-shortlist=%d" % len(missing), flush=True)
nodesc = sum(1 for v in short.values() for n in v["shortlist"] if not inv.get(n))
print("shortlist slots without description=%d" % nodesc, flush=True)
