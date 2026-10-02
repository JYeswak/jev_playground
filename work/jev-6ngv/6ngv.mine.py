import glob, json, os, re, time

cutoff = time.time() - 7 * 86400
files = [
    f
    for f in glob.glob(
        os.path.expanduser("~/.omp/agent/sessions/-Developer-jev/*.jsonl")
    )
    if os.path.getmtime(f) > cutoff
]
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
            t = r.get("type")
            if t == "custom_message" and r.get("customType") == "jev-skill-hint":
                d = r.get("details", {}) if isinstance(r.get("details"), dict) else {}
                sk = d.get("skill")
                if sk:
                    evs.append(
                        (
                            "hint",
                            sk,
                            float(d.get("confidence") or 0),
                            r.get("timestamp"),
                        )
                    )
            elif t == "message":
                m = r.get("message", {})
                c = m.get("content")
                if isinstance(c, list):
                    tx = " ".join(
                        b.get("text", "")
                        for b in c
                        if isinstance(b, dict) and b.get("type") == "text"
                    )
                    calls = [
                        b.get("name", "")
                        + ":"
                        + json.dumps(b.get("arguments", {}))[:200]
                        for b in c
                        if isinstance(b, dict) and b.get("type") == "toolCall"
                    ]
                    if tx.strip() or calls:
                        evs.append(("turn", tx[:800], calls))
        for i, e in enumerate(evs):
            if e[0] != "hint":
                continue
            sk = e[1]
            early = [x for x in evs[i + 1 : i + 4] if x[0] == "turn"]
            late = [x for x in evs[i + 1 : i + 12] if x[0] == "turn"]
            if len(early) < 2 or len(late) < 3:
                continue
            pat = re.compile(re.escape(sk[:20]), re.I)
            early_txt = " ".join(x[1] for x in early)
            late_txt = " ".join(x[1] for x in early[2:] + late)
            late_calls = " ".join(c for x in late for c in x[2])
            follow = bool(
                pat.search(late_txt)
                or ("skill" in late_calls and pat.search(late_calls))
            )
            pairs.append(
                {
                    "skill": sk,
                    "conf": e[2],
                    "early": " // ".join(x[1][:300] for x in early[:2]),
                    "follow": follow,
                }
            )
from collections import Counter

print("pairs:", len(pairs), Counter("fol" if p["follow"] else "aban" for p in pairs))
json.dump(pairs, open("var/agent-tmp/6ngv.pairs.json", "w"))
