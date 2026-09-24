#!/usr/bin/env python3
"""First dogfood readout of the gate-observe hook log (bead jev-w2t).

The log (~/.local/state/jev/gate-observe.jsonl, written by .omp/hooks/post/jev-gate-observe.ts)
lives outside the repo. `extract` copies only redacted fields of rows stamped before CUTOFF into
work/gate-observe-dogfood/extract.jsonl; `score` (the default) reads only that committed extract.

What the extract keeps, per row: ts, session, whether that session has an omp transcript on disk
(`has_transcript`, computed at extract time), cmdSha, status, per-question probabilities, flag,
latency, skip reason and error. The command prefix is kept ONLY for scored rows, and only as the
hook already wrote it (home as ~, SECRET-shaped tokens scrubbed, 200 chars); a prefix matching
real-sample.py's PRIVATE or SECRET pattern is withheld as well. Not-run and skipped rows keep their
hash, never their text.

Fleet vs harness: a row counts as fleet traffic when its session has a transcript under
~/.omp/agent/sessions or ~/.omp/profiles/*/agent/sessions. Sessions with none were driven without
a saved session (omp -p / RPC probe runs), and their commands are test inputs, not use.

Usage:
  python3 work/gate-observe-dogfood/readout.py extract [LOG]   # needs the log; writes extract.jsonl
  python3 work/gate-observe-dogfood/readout.py [score]         # committed extract only
"""

import glob
import importlib.util
import json
import math
import os
import sys
from collections import Counter

CUTOFF = "2026-09-24T03:15:00Z"
HERE = os.path.dirname(os.path.abspath(__file__))
EXTRACT = os.path.join(HERE, "extract.jsonl")
HOME = os.path.expanduser("~")
LOG = f"{HOME}/.local/state/jev/gate-observe.jsonl"
MIN_SCORED_FLEET = (
    50  # the bead's stop rule: fewer scored rows than this -> report counts and stop
)
MEASURED_FA = (
    1,
    300,
)  # 8q7.12: criteria variant false alarms on labelled-routine commands


def filters():
    """PRIVATE and SECRET from real-sample.py, via the skill-routing harvester's ast reader."""
    path = os.path.join(HERE, "..", "skill-routing", "harvest.py")
    spec = importlib.util.spec_from_file_location("harvest", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.PRIVATE, mod.SECRET


def transcript_sessions():
    roots = [f"{HOME}/.omp/agent/sessions"] + glob.glob(
        f"{HOME}/.omp/profiles/*/agent/sessions"
    )
    ids = set()
    for root in roots:
        for f in glob.glob(f"{root}/**/*.jsonl", recursive=True):
            ids.add(os.path.basename(f)[:-6].rsplit("_", 1)[-1])
    return ids


def extract(log):
    private, secret = filters()
    have = transcript_sessions()
    rows = []
    for line in open(log, encoding="utf-8"):
        if not line.strip():
            continue
        r = json.loads(line)
        if str(r.get("ts") or "") >= CUTOFF:
            continue
        cmd = r.get("cmd") if r.get("status") == "scored" else None
        withheld = False
        if cmd is not None and (
            private.search(cmd) or secret.search(cmd) or HOME in cmd
        ):
            cmd, withheld = None, True
        rows.append(
            {
                "i": len(rows),
                "ts": r.get("ts"),
                "session": r.get("session"),
                "has_transcript": r.get("session") in have,
                "cmdSha": r.get("cmdSha"),
                "status": r.get("status"),
                "cmd": cmd,
                "cmdWithheld": withheld,
                "probs": r.get("probs"),
                "flag": r.get("flag"),
                "latencyMs": r.get("latencyMs"),
                "skipped": r.get("skipped"),
                "error": r.get("error"),
            }
        )
    with open(EXTRACT, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(json.dumps({"extract": EXTRACT, "rows": len(rows), "cutoff": CUTOFF}))


def wilson(k, n, z=1.96):
    if n == 0:
        return (math.nan, math.nan)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def score():
    rows = [
        json.loads(line) for line in open(EXTRACT, encoding="utf-8") if line.strip()
    ]
    out = []
    say = out.append
    say(
        f"extract: {len(rows)} rows stamped before {CUTOFF}, "
        f"{rows[0]['ts'] if rows else '-'} .. {rows[-1]['ts'] if rows else '-'}"
    )
    say("")
    say("| Rows | fleet (session has a transcript) | harness (no transcript) | all |")
    say("|---|---:|---:|---:|")
    for status in ("scored", "not-run", "skipped", "error"):
        f = sum(r["status"] == status and r["has_transcript"] for r in rows)
        h = sum(r["status"] == status and not r["has_transcript"] for r in rows)
        say(f"| {status} | {f} | {h} | {f + h} |")
    f = sum(r["has_transcript"] for r in rows)
    say(f"| total | {f} | {len(rows) - f} | {len(rows)} |")
    say("")
    errs = Counter(r["error"] for r in rows if r["error"])
    skips = Counter(r["skipped"] for r in rows if r["skipped"])
    say(f"errors: {dict(errs)}; skipped: {dict(skips)}")
    sessions = Counter((r["session"], r["has_transcript"]) for r in rows)
    say(
        f"sessions: {len(sessions)} ({sum(1 for (_, t) in sessions if t)} with a transcript)"
    )
    for (s, t), n in sorted(sessions.items(), key=lambda kv: (-kv[1], kv[0][0])):
        st = Counter(r["status"] for r in rows if r["session"] == s)
        say(
            f"  {s} {'fleet  ' if t else 'harness'} {n:3d} rows {dict(sorted(st.items()))}"
        )
    scored = [r for r in rows if r["status"] == "scored"]
    fleet_scored = [r for r in scored if r["has_transcript"]]
    flags = [r for r in scored if r["flag"]]
    maxp = sorted((max(r["probs"].values()), r["cmd"]) for r in scored if r["probs"])
    distinct = Counter(r["cmdSha"] for r in scored)
    say("")
    say(
        f"scored rows: {len(scored)} ({len(distinct)} distinct commands); fleet scored: {len(fleet_scored)}; "
        f"flagged: {len(flags)}"
    )
    lo, hi = wilson(len(flags), len(scored))
    say(
        f"flag rate over all scored rows: {len(flags)}/{len(scored)} (Wilson 95% {lo:.3f}-{hi:.3f}); "
        f"measured false-alarm rate 8q7.12: {MEASURED_FA[0]}/{MEASURED_FA[1]}"
    )
    if maxp:
        say(
            f"highest max-noul among scored rows: {maxp[-1][0]} ({maxp[-1][1]!r}); cut 0.5"
        )
    lat = sorted(
        r["latencyMs"] for r in scored if isinstance(r["latencyMs"], (int, float))
    )
    if lat:
        say(f"scored latency ms: p50 {lat[len(lat) // 2]}, max {lat[-1]}")
    say("")
    top = Counter(r["cmd"] for r in scored).most_common()
    say(
        "scored commands (hook-redacted prefix, count): "
        + "; ".join(f"{c!r} x{n}" for c, n in top)
    )
    say("")
    stop = len(fleet_scored) < MIN_SCORED_FLEET
    if stop:
        say(
            f"STOP: {len(fleet_scored)} scored fleet rows < {MIN_SCORED_FLEET} (bead jev-w2t stop rule). "
            "No labels drawn, no false-alarm rate on fleet traffic reported."
        )
    else:
        # Fail closed: an extract past the stop rule needs a committed label file first.
        say(
            f"REFUSED: {len(fleet_scored)} scored fleet rows reach the stop rule, but no label file is committed; "
            "commit labels before any rate is computed"
        )
    print("\n".join(out))
    return 0 if stop else 1


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "score"
    if mode == "extract":
        extract(sys.argv[2] if len(sys.argv) > 2 else LOG)
    elif mode == "score":
        sys.exit(score())
    else:
        print(__doc__)
        sys.exit(64)
