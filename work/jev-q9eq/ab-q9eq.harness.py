#!/usr/bin/env python3
"""q9eq harness: interactive RPC sessions, ON = explicit project hooks/extensions.
Order per task: ON-r1, OFF-r1, ON-r2, OFF-r2. OFF pins thinking to ON-r1 level.
"""

import json, os, shutil, subprocess, sys, time, glob
from datetime import datetime, timezone

ROOT = "/Users/josh/Developer/jev"
SCR = os.path.join(ROOT, "var/agent-tmp/ab-q9eq.main")
TASKS = [("hard", "t%02d" % i) for i in range(1, 13)] + [
    ("hard3", "h%02d" % i) for i in range(1, 17)
]
TASKDIR = {
    "hard": "work/thinking-duel-hard/tasks",
    "hard3": "work/thinking-duel-hard3/tasks",
}
MANIFEST = os.path.join(SCR, "manifest.jsonl")
HOOKS = [
    ".omp/hooks/post/jev-gate-observe.ts",
    ".omp/hooks/post/jev-webscreen.ts",
    ".omp/hooks/post/jev-web-search-rerank.ts",
    ".omp/hooks/post/jev-injection-shadow.ts",
]
EXTS = [
    ".omp/extensions/jev-memory-filter.ts",
    ".omp/extensions/jev-skill-hint.ts",
    ".omp/extensions/jev-rerank.ts",
    ".omp/extensions/jev-flag.ts",
    ".omp/extensions/jev-screen.ts",
    ".omp/extensions/jev-gate.ts",
    ".omp/extensions/jev-claim-check.ts",
    ".omp/extensions/jev-classify.ts",
    ".omp/extensions/jev-review.ts",
    ".omp/extensions/kit-guard",
]
PROMPT = (
    "TASK-ID ab-q9eq-{tid}-{arm}-{rep}. Solve the coding task in $PWD: "
    "read prompt.md, fix the buggy file using only the standard library, "
    "verify with your own checks, then stop. Do not commit, push, or modify "
    "anything outside $PWD. When done, reply with DONE and the verification output."
)


def utcnow():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def setup(tid, setname, arm, rep):
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


def run(setname, tid, arm, rep, think=None):
    d, pf = setup(tid, setname, arm, rep)
    t0 = utcnow()
    cmd = ["python3", "var/agent-tmp/rpc_run.py", d, pf]
    if arm == "ON":
        for h in HOOKS:
            cmd += ["--hook", os.path.join(ROOT, h)]
        for e in EXTS:
            cmd += ["--hook", os.path.join(ROOT, e)]
    else:
        cmd += ["--no-extensions"]
        if think:
            cmd += ["--thinking", think]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=590, cwd=ROOT)
    t1 = utcnow()
    out = p.stdout + p.stderr
    sd = None
    for line in out.split("\n"):
        if line.startswith("sessdir="):
            sd = line.split("=", 1)[1].strip()
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
        "tail": out[-300:],
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
    print("Q9EQ HARNESS DONE", flush=True)


if __name__ == "__main__":
    main()
