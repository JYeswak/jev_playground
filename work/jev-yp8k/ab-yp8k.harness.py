#!/usr/bin/env python3
"""Outcome A/B harness (jev-yp8k): ON vs OFF across 28 coding tasks.
Order per task: ON-r1 (auto thinking, records level), OFF-r1 (pinned),
ON-r2, OFF-r2. Logs UTC start/end + GPU overlap. Grade post-hoc (blind scripts).
"""

import json, os, shutil, subprocess, sys, time, glob
from datetime import datetime, timezone

ROOT = "/Users/josh/Developer/jev"
SCR = os.path.join(ROOT, "var/agent-tmp/ab-yp8k.main")
TASKS = [("hard", "t%02d" % i) for i in range(1, 13)] + [
    ("hard3", "h%02d" % i) for i in range(1, 17)
]
GRADE = {
    "hard": "work/thinking-duel-hard/grade.py",
    "hard3": "work/thinking-duel-hard3/grade.py",
}
TASKDIR = {
    "hard": "work/thinking-duel-hard/tasks",
    "hard3": "work/thinking-duel-hard3/tasks",
}
MANIFEST = os.path.join(SCR, "manifest.jsonl")
PROMPT = (
    "TASK-ID ab-yp8k-{tid}-{arm}-{rep}. Solve the coding task in $PWD: "
    "read prompt.md, fix the buggy file using only the standard library, "
    "verify with your own checks, then stop. Do not commit, push, or modify "
    "anything outside $PWD. When done, reply with DONE and the verification output."
)


def utcnow():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def setup(setname, tid, arm, rep):
    d = os.path.join(SCR, "%s-%s-%s" % (tid, arm, rep))
    os.makedirs(d, exist_ok=True)
    src = os.path.join(ROOT, TASKDIR[setname], tid)
    for f in os.listdir(src):
        s = os.path.join(src, f)
        if os.path.isfile(s):
            shutil.copy(s, d)
    pf = os.path.join(SCR, "prompt-%s-%s-%s.txt" % (tid, arm, rep))
    open(pf, "w").write(PROMPT.format(tid=tid, arm=arm, rep=rep))
    return d, pf


def think_of(sessdir):
    files = sorted(glob.glob(os.path.join(sessdir, "*.jsonl")), key=os.path.getmtime)
    if not files:
        return None
    for line in open(files[-1], encoding="utf-8", errors="replace"):
        try:
            r = json.loads(line)
        except Exception:
            continue
        if r.get("type") == "thinking_level_change":
            return r.get("thinkingLevel")
    return None


def sessdir_for(workdir, before):
    cands = glob.glob(os.path.expanduser("~/.omp/agent/sessions/-Developer-jev*"))
    best, bestmt = None, 0
    slug = workdir.replace("/", "-").replace("_", "-")
    for c in cands:
        if "ab-yp8k" not in c:
            continue
        try:
            mt = os.path.getmtime(c)
        except Exception:
            continue
        if mt > bestmt and mt > before:
            best, bestmt = c, mt
    return best


def run(setname, tid, arm, rep, think=None):
    d, pf = setup(setname, tid, arm, rep)
    t0 = utcnow()
    before = time.time()
    cmd = ["omp", "launch", "-p", "@" + pf, "--cwd", d]
    if arm == "OFF":
        cmd += ["--no-extensions"]
        if think:
            cmd += ["--thinking", think]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=590, cwd=ROOT)
    t1 = utcnow()
    sd = sessdir_for(d, before - 5)
    lvl = think_of(sd) if sd else None
    rec = {
        "task": tid,
        "set": setname,
        "arm": arm,
        "rep": rep,
        "t0": t0,
        "t1": t1,
        "think": lvl,
        "sessdir": sd,
        "rc": p.returncode,
        "tail": (p.stdout + p.stderr)[-300:],
    }
    open(MANIFEST, "a").write(json.dumps(rec) + "\n")
    print("%s %s %s rc=%d think=%s" % (tid, arm, rep, p.returncode, lvl), flush=True)
    return rec, lvl


def main():
    tasks = sys.argv[1:] or [t for _, t in TASKS]
    byset = {}
    for s, t in TASKS:
        byset[t] = s
    for tid in tasks:
        s = byset[tid]
        _, lvl = run(s, tid, "ON", "r1")
        run(s, tid, "OFF", "r1", think=lvl)
        run(s, tid, "ON", "r2")
        run(s, tid, "OFF", "r2", think=lvl)
    print("HARNESS DONE")


if __name__ == "__main__":
    main()
