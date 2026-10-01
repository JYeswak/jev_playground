#!/usr/bin/env python3
"""jev-wb7j Step 1 (keyless): census + sample (prompt, memory) pairs.

Population: session_init.systemPrompt <memories> blocks and
custom_message ee-task-context blocks in -Developer-jev session files,
mtime >= CUTOFF. Emits census.json + sample.jsonl (seed 42).
"""

import json, os, re, random, datetime, sys

CUTOFF = datetime.datetime(2026, 9, 24, 8, 30, tzinfo=datetime.timezone.utc).timestamp()
ROOT = "/Users/josh/.omp"
SEED = 42
OUT = os.path.dirname(os.path.abspath(__file__))


def est_tokens(s):
    return len(s) // 4


def mem_block_items(text):
    m = re.search(r"<memories>(.*?)</memories>", text, re.S)
    if not m:
        return []
    return [
        ln[2:].strip()
        for ln in m.group(1).splitlines()
        if ln.strip().startswith("- ") and len(ln.strip()) > 4
    ]


def ee_items(text):
    lines = [ln.strip() for ln in text.splitlines() if ln.strip().startswith("- ")]
    return [ln[2:].strip() for ln in lines if len(ln) > 6]


def user_text(msg):
    c = msg.get("content")
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        return "\n".join(
            b.get("text", "")
            for b in c
            if isinstance(b, dict) and b.get("type") == "text"
        )
    return ""


def main():
    pairs = []  # (prompt, memory, source)
    census = {
        "files": 0,
        "sessions": 0,
        "ee_blocks": 0,
        "ee_block_tokens": 0,
        "sysmem_blocks": 0,
        "sysmem_block_tokens": 0,
        "ee_items": 0,
        "sysmem_items": 0,
    }
    per_file = {}
    for prof in sorted(os.listdir(ROOT + "/profiles")):
        d = ROOT + "/profiles/" + prof + "/agent/sessions/-Developer-jev"
        if not os.path.isdir(d):
            continue
        for root, _, fns in os.walk(d):
            for fn in sorted(fns):
                if not fn.endswith(".jsonl"):
                    continue
                fp = root + "/" + fn
                if os.path.getmtime(fp) < CUTOFF:
                    continue
                census["files"] += 1
                recs = []
                with open(fp, errors="replace") as fh:
                    for line in fh:
                        try:
                            recs.append(json.loads(line))
                        except Exception:
                            pass
                users = [
                    (i, user_text(r["message"]))
                    for i, r in enumerate(recs)
                    if r.get("type") == "message"
                    and isinstance(r.get("message"), dict)
                    and r["message"].get("role") == "user"
                ]
                for i, r in enumerate(recs):
                    t = r.get("type")
                    if t == "session_init":
                        census["sessions"] += 1
                        sp = r.get("systemPrompt", "")
                        items = mem_block_items(sp)
                        if items:
                            census["sysmem_blocks"] += 1
                            blk_m = re.search(r"<memories>.*?</memories>", sp, re.S)
                            blk = blk_m.group(0) if blk_m else ""
                            census["sysmem_block_tokens"] += est_tokens(blk)
                            census["sysmem_items"] += len(items)
                            task = r.get("task", "")
                            for it in items:
                                pairs.append((task, it, "session_init"))
                    elif (
                        t == "custom_message"
                        and r.get("customType") == "ee-task-context"
                    ):
                        census["ee_blocks"] += 1
                        content = r.get("content", "")
                        census["ee_block_tokens"] += est_tokens(content)
                        items = ee_items(content)
                        census["ee_items"] += len(items)
                        prompt = ""
                        for j, u in reversed(users):
                            if j < i:
                                prompt = u
                                break
                        if not prompt and users:
                            prompt = users[0][1]
                        for it in items:
                            pairs.append((prompt, it, "ee-task-context"))
                per_file[fp] = True
    random.seed(SEED)
    idx = list(range(len(pairs)))
    random.shuffle(idx)
    sample = [pairs[i] for i in idx[:100]]
    with open(OUT + "/census.json", "w") as fh:
        json.dump(census, fh, indent=1)
    with open(OUT + "/sample.jsonl", "w") as fh:
        for k, (prompt, mem, src) in enumerate(sample):
            fh.write(
                json.dumps(
                    {
                        "id": "S%03d" % k,
                        "source": src,
                        "prompt": prompt,
                        "memory": mem,
                        "prompt_tokens": est_tokens(prompt),
                        "memory_tokens": est_tokens(mem),
                    }
                )
                + "\n"
            )
    census["total_pairs"] = len(pairs)
    census["sampled"] = len(sample)
    with open(OUT + "/census.json", "w") as fh:
        json.dump(census, fh, indent=1)
    print(json.dumps(census, indent=1))


if __name__ == "__main__":
    sys.exit(main())
