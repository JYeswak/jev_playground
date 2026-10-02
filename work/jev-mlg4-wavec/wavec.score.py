import json, glob, os, re

man = [json.loads(l) for l in open("var/agent-tmp/ab-wavec.main/manifest2.jsonl")]
seen = {}
for r in man:
    k = (r["task"], r["arm"], r["rep"])
    if k not in seen:
        seen[k] = r
print("rows=%d unique=%d" % (len(man), len(seen)))
tasks = {
    t["id"]: t["answer"] for t in json.load(open("var/agent-tmp/wavec.tasks.json"))
}
EXCLUDE = {"f07"}
res = []
for (t, a, r), rec in sorted(seen.items()):
    if t in EXCLUDE:
        continue
    sd = rec.get("sessdir") or ""
    files = sorted(glob.glob(sd + "/*.jsonl"), key=os.path.getmtime) if sd else []
    ans = None
    tin = tout = tools = findrows = 0
    sid = None
    if files:
        f = files[-1]
        sid = f.split("_")[-1].split(".")[0]
        pat = re.compile(r"(?<![\w./-])" + re.escape(tasks[t]) + r"(?![\w./-])")
        for line in open(f, encoding="utf-8", errors="replace"):
            try:
                x = json.loads(line)
            except Exception:
                continue
            if x.get("type") == "message":
                m = x.get("message", {})
                if m.get("role") == "assistant":
                    u = m.get("usage") or {}
                    tin += u.get("input", 0) or 0
                    tout += u.get("output", 0) or 0
                c = m.get("content")
                if isinstance(c, list):
                    for b in c:
                        if not isinstance(b, dict):
                            continue
                        if b.get("type") == "toolCall":
                            tools += 1
                        if b.get("type") == "text" and m.get("role") == "assistant":
                            if pat.search(b.get("text", "")):
                                ans = tasks[t]
            if (
                x.get("type") == "model_usage"
                and x.get("role") == "typesafe"
                and x.get("purpose") == "find"
            ):
                findrows += 1
    res.append(
        {
            "task": t,
            "arm": a,
            "rep": r,
            "pass": ans is not None,
            "t0": rec["t0"],
            "t1": rec["t1"],
            "in": tin,
            "out": tout,
            "tools": tools,
            "findrows": findrows,
            "sid": sid,
        }
    )
json.dump(res, open("var/agent-tmp/wavec.results.json", "w"))
for arm in ["ON", "OFF"]:
    ss = [x for x in res if x["arm"] == arm]
    print(
        arm,
        "%d/%d" % (sum(1 for x in ss if x["pass"]), len(ss)),
        "findrows=%d" % sum(x["findrows"] for x in ss),
    )
