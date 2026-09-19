"""Ceiling sweep for class-D: can the ORIGINAL agent's continuation reproduce
the oracle facts at all? (OFFLINE, zero model calls, zero API.)

For each frozen turn (ablate_turns.jsonl) and each window W in {1, 3, 10,
inf} assistant messages after the result, fraction of turns where the
window's text contains:
  strict: any oracle fact token (novel len>=5 token reappearing later)
  loose:  any file/path/identifier from the result (path-like or dotted
          identifier tokens len>=4 found in the result text)
Usage: python ceiling_sweep.py
"""

import glob
import json
import os
import re

TOKEN = re.compile(r"[a-z0-9]{5,}")
LOOSE = re.compile(r"(?:[\w.\-]*\/[\w.\-]+)+|[a-z_][a-z0-9_]*\.[a-z_][a-z0-9_]+")
STOP = set(
    "the a an and or of to in is it for with on at by from this that not you your we as be are was".split()
)
SESS = {
    "grokbot": os.path.expanduser(
        "~/.omp/profiles/muse/agent/sessions/-Developer-grokbot/2026-09-11T22-19-20-324Z_01a0928d-c784-707b-9f38-ea88f280615c"
    ),
    "harvest": os.path.expanduser(
        "~/.omp/profiles/codex/agent/sessions/-Developer-franken-harvest/2026-09-13T04-17-55-579Z_01a098fc-6f7b-706c-ad4a-4e72f05c9aa5"
    ),
    "orch": os.path.expanduser(
        "~/.omp/profiles/claude/agent/sessions/-Developer-omp-orchestrator/2026-08-31T06-02-27-553Z_01a05669-7761-7429-b467-093ba8544ca2"
    ),
}


def toks(t, n=5):
    return set(re.findall(r"[a-z0-9]{%d,}" % n, t.lower())) - STOP


def load(sdir):
    rows = []
    for f in sorted(glob.glob(sdir + "/*.jsonl") + glob.glob(sdir + "/*.log")):
        with open(f, errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line.startswith("{"):
                    continue
                try:
                    r = json.loads(line)
                except Exception:
                    continue
                m = r.get("message")
                if isinstance(m, dict) and "role" in m:
                    rows.append(m)
    return rows


def atext(m):
    return "\n".join(
        p.get("text", "")
        for p in m.get("content") or []
        if isinstance(p, dict) and p.get("type") == "text"
    )


def main():
    turns = [json.loads(l) for l in open("ablate_turns.jsonl")]
    cache = {}
    for s in SESS:
        cache[s] = load(SESS[s])
    print(f"turns={len(turns)} API_CALLS=0", flush=True)
    for w in (1, 3, 10, 20, 50, 80, 10**9):
        s_hit = s_n = l_hit = l_n = 0
        for t in turns:
            msgs = cache[t["session"]]
            ri = next(
                (
                    i
                    for i, m in enumerate(msgs)
                    if m.get("role") == "toolResult" and m.get("toolCallId") == t["tid"]
                ),
                None,
            )
            if ri is None:
                continue
            foll = [m for m in msgs[ri + 1 :] if m.get("role") == "assistant"][
                : w if w < 10**9 else None
            ]
            wtxt = "\n".join(atext(m) for m in foll).lower()
            # strict facts from the frozen turn
            s_n += 1
            if any(f in wtxt for f in t["facts"]):
                s_hit += 1
            # loose: file/path/identifier tokens from the result row itself
            rtxt = next((atext(msgs[i]) for i in [ri]), "")
            loose = set(x.lower() for x in LOOSE.findall(rtxt) if len(x) >= 4)
            l_n += 1
            if loose and any(x in wtxt for x in loose):
                l_hit += 1
        wname = "inf" if w > 10**8 else str(w)
        print(
            f"window={wname}: strict {s_hit}/{s_n}={s_hit / max(1, s_n):.3f}  "
            f"loose {l_hit}/{l_n}={l_hit / max(1, l_n):.3f}",
            flush=True,
        )


if __name__ == "__main__":
    main()
