import glob, json, os, re, time

cutoff = time.time() - 7 * 86400
files = [
    f
    for f in glob.glob(
        os.path.expanduser("~/.omp/agent/sessions/-Developer-jev/*.jsonl")
    )
    if os.path.getmtime(f) > cutoff
]
SKIP = re.compile(
    r"shaken ~|provider stream ended|socket connection was closed|context canceled",
    re.I,
)
FPATH = re.compile(r"([\w.\-][\w.\-/]*\.(?:ts|mjs|js|py|md|json|sh|yml|tsx|txt))")
pairs = []
for f in files:
    try:
        fp = open(f, encoding="utf-8", errors="replace")
    except Exception:
        continue
    with fp:
        evs = []
        for line in fp:
            try:
                r = json.loads(line)
            except Exception:
                continue
            if not isinstance(r, dict) or r.get("type") != "message":
                continue
            m = r.get("message", {})
            if m.get("role") == "toolResult" and m.get("isError") is True:
                c = m.get("content")
                t = (
                    c
                    if isinstance(c, str)
                    else " ".join(b.get("text", "") for b in c if isinstance(b, dict))
                    if isinstance(c, list)
                    else ""
                )
                if not SKIP.search(t):
                    evs.append(("res", t[:2000]))
            elif m.get("role") == "assistant":
                c = m.get("content")
                if isinstance(c, list):
                    tx = " ".join(
                        b.get("text", "")
                        for b in c
                        if isinstance(b, dict) and b.get("type") == "text"
                    )
                    calls = []
                    for b in c:
                        if isinstance(b, dict) and b.get("type") == "toolCall":
                            calls.append(
                                (
                                    b.get("name", ""),
                                    json.dumps(b.get("arguments", {}))[:300],
                                )
                            )
                    if tx.strip() or calls:
                        evs.append(("asst", tx[:800], calls))
        for i, e in enumerate(evs):
            if e[0] != "res":
                continue
            paths = set(p for p in FPATH.findall(e[1]) if len(p) > 4)
            nxt = [x for x in evs[i + 1 : i + 5] if x[0] == "asst"]
            if len(nxt) < 2:
                continue
            addressed = False
            for _, _, calls in nxt[:3]:
                for name, args in calls:
                    if name in ("edit", "write", "bash") and any(
                        p in args for p in paths
                    ):
                        addressed = True
            pairs.append(
                (
                    addressed,
                    e[1][:400],
                    " // ".join(n[1][:100] for n in nxt[:2]).replace("\n", " "),
                )
            )
from collections import Counter

print("n=%d" % len(pairs), Counter("addr" if a else "ign" for a, _, _ in pairs))
json.dump(
    [{"addr": a, "res": t, "nxt": n} for a, t, n in pairs],
    open("var/agent-tmp/xdzh.pairs5.json", "w"),
)
