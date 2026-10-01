"""jev-m2c6: auto-thinking benefit from session files. Bar locked in-bead BEFORE outcomes."""

import json, os, re, sys, time

CORR = re.compile(r"\bno\b|\bwrong\b|that.s not", re.I)
NOW = time.time()
AUTO_PROFILES = ["claude", "codex", "muse", "grok"]
ROOT = "/Users/josh/.omp/agent/sessions"
PROF = "/Users/josh/.omp/profiles"


def user_text(msg):
    c = msg.get("content")
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        return " ".join(
            b.get("text", "")
            for b in c
            if isinstance(b, dict) and isinstance(b.get("text"), str)
        )
    return ""


def think_chars(msg):
    c = msg.get("content")
    if not isinstance(c, list):
        return 0
    return sum(
        len(b.get("thinking", ""))
        for b in c
        if isinstance(b, dict) and b.get("type") == "thinking"
    )


def analyze(files, default_level):
    turns = []
    for f in files:
        try:
            rows = [json.loads(l) for l in open(f, errors="replace")]
        except Exception:
            continue
        cur = default_level
        cur_turn = None
        fturns = []
        for r in rows:
            t = r.get("type")
            if t == "thinking_level_change":
                if cur_turn is not None:
                    fturns.append(cur_turn)
                cur = r.get("thinkingLevel", cur)
                cur_turn = None
            elif t == "message" and isinstance(r.get("message"), dict):
                m = r["message"]
                if m.get("role") == "user":
                    if cur_turn is not None:
                        fturns.append(cur_turn)
                    cur_turn = {"level": cur, "chars": 0, "user": user_text(m)}
                elif m.get("role") == "assistant" and cur_turn is not None:
                    cur_turn["chars"] += think_chars(m)
        if cur_turn is not None:
            fturns.append(cur_turn)
        for i, tr in enumerate(fturns):
            nxt = " ".join(t["user"] for t in fturns[i + 1 : i + 3])
            tr["corrected"] = bool(nxt.strip()) and bool(CORR.search(nxt))
        turns.extend(fturns)
    return turns


def walk_files(base, days=None):
    out = []
    for dirpath, _, names in os.walk(base):
        for n in names:
            if not n.endswith(".jsonl"):
                continue
            f = os.path.join(dirpath, n)
            try:
                if days is None or NOW - os.path.getmtime(f) <= days * 86400:
                    out.append(f)
            except OSError:
                pass
    return out


if __name__ == "__main__":
    auto_files = []
    for p in AUTO_PROFILES:
        auto_files += walk_files(f"{PROF}/{p}/agent/sessions", 7)
    auto_files += walk_files(ROOT, 7)
    fixed_files = walk_files(f"{PROF}/jev-lab/agent/sessions")
    print("auto files:", len(auto_files), "fixed files:", len(fixed_files))
    aturns = analyze(auto_files, "auto-unset")
    fturns = analyze(fixed_files, "xhigh")
    json.dump({"auto": aturns, "fixed": fturns}, open(sys.argv[1], "w"))
    print("auto turns:", len(aturns), "fixed turns:", len(fturns))
