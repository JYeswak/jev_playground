import glob, json, os, re, time, random

cutoff = time.time() - 7 * 86400
files = [
    f
    for f in glob.glob(
        os.path.expanduser("~/.omp/agent/sessions/-Developer-jev/*.jsonl")
    )
    if os.path.getmtime(f) > cutoff
]
RX = re.compile(
    r"error|fail|exception|traceback|E\d{3,4}|denied|fatal|not found|timed?\s*out|killed|abort|invalid|panic",
    re.I,
)
items = []
for f in files:
    try:
        fp = open(f, encoding="utf-8", errors="replace")
    except Exception:
        continue
    with fp:
        for line in fp:
            try:
                r = json.loads(line)
            except Exception:
                continue
            if not isinstance(r, dict) or r.get("type") != "message":
                continue
            m = r.get("message", {})
            if m.get("role") != "toolResult":
                continue
            c = m.get("content")
            t = (
                c
                if isinstance(c, str)
                else " ".join(b.get("text", "") for b in c if isinstance(b, dict))
                if isinstance(c, list)
                else ""
            )
            if len(t) < 20:
                continue
            items.append((bool(m.get("isError")), t[:600]))
print("items:", len(items))
random.seed(5)
sample = random.sample(items, min(2000, len(items)))
tp = fp = fn = tn = 0
for y, t in sample:
    p = bool(RX.search(t))
    if p and y:
        tp += 1
    elif p and not y:
        fp += 1
    elif not p and y:
        fn += 1
    else:
        tn += 1
prec = tp / (tp + fp) if tp + fp else 0
rec = tp / (tp + fn) if tp + fn else 0
f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0
print(
    "regex: tp=%d fp=%d fn=%d tn=%d prec=%.4f rec=%.4f F1=%.4f"
    % (tp, fp, fn, tn, prec, rec, f1)
)
json.dump(
    [{"y": y, "t": t} for y, t in sample],
    open("var/agent-tmp/hqha.errsample.json", "w"),
)
