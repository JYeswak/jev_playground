import glob, json, os, time

cutoff = time.time() - 7 * 86400
toks = n = 0
files = glob.glob(os.path.expanduser("~/.omp/agent/sessions/-Developer-jev/*.jsonl"))
for f in files:
    try:
        fp = open(f, encoding="utf-8", errors="replace")
    except Exception:
        continue
    with fp:
        for line in fp:
            if "jev-skill-hint" not in line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get("customType") == "jev-skill-hint":
                toks += len(r.get("content", "")) // 4
                n += 1
print("hint msgs(7d, one profile dir):", n, "est tokens:", toks)
