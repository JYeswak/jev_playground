#!/usr/bin/env python3
"""jev-wb7j held-out sample: same population walk as census.py, exclude sampled 100, seed 20261001."""

import json, os, re, random, datetime

CUTOFF = datetime.datetime(2026, 9, 24, 8, 30, tzinfo=datetime.timezone.utc).timestamp()
ROOT = "/Users/josh/.omp"
SEED = 20261001
OUTDIR = os.path.dirname(os.path.abspath(__file__))


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
            if isinstance(b, dict) and isinstance(b.get("text"), str)
        )
    return ""


def main():
    pairs = []
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
                        items = mem_block_items(r.get("systemPrompt", ""))
                        task = r.get("task", "")
                        for it in items:
                            pairs.append((task, it, "session_init"))
                    elif (
                        t == "custom_message"
                        and r.get("customType") == "ee-task-context"
                    ):
                        items = ee_items(r.get("content", ""))
                        prompt = ""
                        for j, u in reversed(users):
                            if j < i:
                                prompt = u
                                break
                        if not prompt and users:
                            prompt = users[0][1]
                        for it in items:
                            pairs.append((prompt, it, "ee-task-context"))
    old = set()
    for line in open("work/jev-wb7j/sample.jsonl"):
        o = json.loads(line)
        old.add((o["prompt"], o["memory"]))
    fresh = [p for p in pairs if (p[0], p[1]) not in old]
    print(
        f"census pairs: {len(pairs)}, excluded sampled: {len(pairs)-len(fresh)}, fresh: {len(fresh)}"
    )
    random.seed(SEED)
    idx = list(range(len(fresh)))
    random.shuffle(idx)
    take = [fresh[i] for i in idx[:100]]
    with open(OUTDIR + "/heldout-sample.jsonl", "w") as fh:
        for k, (prompt, mem, src) in enumerate(take):
            fh.write(
                json.dumps(
                    {
                        "id": "H%03d" % k,
                        "source": src,
                        "prompt": prompt,
                        "memory": mem,
                        "prompt_tokens": est_tokens(prompt),
                        "memory_tokens": est_tokens(mem),
                    }
                )
                + "\n"
            )
    print(f"held-out: {len(take)}")


if __name__ == "__main__":
    main()
