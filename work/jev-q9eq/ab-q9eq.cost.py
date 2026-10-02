import json, glob, os, statistics

man = [json.loads(l) for l in open("var/agent-tmp/ab-q9eq.main/manifest.jsonl")]
out = []
for r in man:
    sd = r.get("sessdir") or ""
    files = sorted(glob.glob(sd + "/*.jsonl"), key=os.path.getmtime) if sd else []
    tin = tout = tools = jev_n = jev_in = gate = 0
    sid = None
    if files:
        f = files[-1]
        sid = f.split("_")[-1].split(".")[0]
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
                        if isinstance(b, dict) and b.get("type") == "toolCall":
                            tools += 1
            elif x.get("type") == "model_usage" and x.get("role") == "typesafe":
                jev_n += 1
                jev_in += (x.get("usage") or {}).get("input", 0) or 0
    out.append(
        {
            "task": r["task"],
            "arm": r["arm"],
            "rep": r["rep"],
            "t0": r["t0"],
            "t1": r["t1"],
            "in": tin,
            "out": tout,
            "tools": tools,
            "jev_n": jev_n,
            "jev_in": jev_in,
            "sid": sid,
        }
    )
# gate rows by FULL uuid
uuids = {}
for o in out:
    if o.get("sid"):
        uuids[o["sid"]] = o["arm"]
gate = {"ON": 0, "OFF": 0}
for line in open(
    "/Users/josh/.local/state/jev/gate-observe.jsonl",
    encoding="utf-8",
    errors="replace",
):
    try:
        x = json.loads(line)
    except Exception:
        continue
    s = x.get("session") or ""
    if s in uuids:
        gate[uuids[s]] += 1
print("gate rows by arm:", gate)
json.dump(out, open("var/agent-tmp/ab-q9eq.metered.json", "w"))
for arm in ["ON", "OFF"]:
    ss = [o for o in out if o["arm"] == arm]
    print(
        arm,
        "n=%d in_med=%d out_med=%d tools_med=%.1f jev_calls=%d"
        % (
            len(ss),
            statistics.median(o["in"] for o in ss),
            statistics.median(o["out"] for o in ss),
            statistics.median(o["tools"] for o in ss),
            sum(o["jev_n"] for o in ss),
        ),
    )


def wilcoxon(diffs):
    diffs = [d for d in diffs if d != 0]
    n = len(diffs)
    if n == 0:
        return 1.0, 0
    ranked = sorted(range(n), key=lambda i: abs(diffs[i]))
    ranks = [0] * n
    i = 0
    while i < n:
        j = i
        while j < n and abs(diffs[ranked[j]]) == abs(diffs[ranked[i]]):
            j += 1
        avg = (i + j + 1) / 2
        for k in range(i, j):
            ranks[ranked[k]] = avg
        i = j
    w = sum(r for r, d in zip(ranks, diffs) if d > 0)
    mu = n * (n + 1) / 4
    var = n * (n + 1) * (2 * n + 1) / 24
    import math

    z = (w - mu) / math.sqrt(var) if var else 0
    return math.erfc(abs(z) / math.sqrt(2)), n


from collections import defaultdict

pairs = defaultdict(dict)
for o in out:
    pairs[(o["task"], o["rep"])][o["arm"]] = o
for key in ["in", "out", "tools"]:
    diffs = [v["ON"][key] - v["OFF"][key] for v in pairs.values()]
    import statistics as st

    p, n = wilcoxon(diffs)
    print("%s: meddiff=%d Wilcoxon p=%.4f" % (key, st.median(diffs), p))
print(
    "main totals: in=%d out=%d jev_calls=%d"
    % (
        sum(o["in"] for o in out),
        sum(o["out"] for o in out),
        sum(o["jev_n"] for o in out),
    )
)
