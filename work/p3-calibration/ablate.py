"""Ablate-and-rerun class-D test (LOCAL model, zero marginal cost).

PREREGISTERED (printed before any model call): compaction is HARMLESS on a
turn if arm B (result replaced by fast-jev-compaction's real truncation note)
reproduces the reused fact as often as arm A (intact). Paired difference over
>=20 turns; discordant count reported (concordant pairs carry no information).
Verdict via e-process (Ville, conservative): e>=20 either way else
INCONCLUSIVE. HARMLESS / HARMFUL / INCONCLUSIVE.
Arm C (withheld context): same task with NO transcript — facts appearing here
come from the model's prior knowledge, not the transcript, bounding the
contamination reading.
Indexing is LINEAR (token first/last maps, after oracle.mjs).
Model: Qwen3.6-27B-4bit-MTP-MLX-Serve @127.0.0.1:11238 (NOT the brief's
3.8-Splash: not serving on this machine; substitution disclosed).
Usage: python ablate.py [--prep-only]  (always writes ablate_turns.jsonl;
  with model arms, ablate_pairs.jsonl with per-call wall-clock latencies)
"""

import glob
import json
import os
import re
import sys
import time
import urllib.request

TOKEN = re.compile(r"[a-z0-9]{5,}")
STOP = set(
    "the a an and or of to in is it for with on at by from this that not you your we as be are was".split()
)
SESS = {
    "grokbot": "/Users/josh/.omp/profiles/muse/agent/sessions/-Developer-grokbot/2026-09-11T22-19-20-324Z_01a0928d-c784-707b-9f38-ea88f280615c",
    "harvest": "/Users/josh/.omp/profiles/codex/agent/sessions/-Developer-franken-harvest/2026-09-13T04-17-55-579Z_01a098fc-6f7b-706c-ad4a-4e72f05c9aa5",
    "orch": "/Users/josh/.omp/profiles/claude/agent/sessions/-Developer-omp-orchestrator/2026-08-31T06-02-27-553Z_01a05669-7761-7429-b467-093ba8544ca2",
}
URL = "http://127.0.0.1:11238/v1/chat/completions"
MODEL = "Qwen3.6-27B-4bit-MTP-MLX-Serve"


def toks(t):
    return set(TOKEN.findall(t.lower())) - STOP


def msg_text(m):
    return "\n".join(
        p.get("text", "")
        for p in m.get("content") or []
        if isinstance(p, dict) and p.get("type") == "text"
    )


def load_messages(sdir):
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


def render(m, drop_result_id=None):
    role = m.get("role")
    parts = []
    for p in m.get("content") or []:
        if not isinstance(p, dict):
            continue
        if p.get("type") == "text" and p.get("text"):
            parts.append(p["text"][:3000])
        elif p.get("type") == "toolCall":
            parts.append(
                f"[tool call {p.get('name')}: {json.dumps(p.get('arguments', {}))[:500]}]"
            )
    if role == "toolResult" and drop_result_id == m.get("toolCallId"):
        full = "\n".join(parts)
        head = full[:300]
        return f"role=toolResult\n{head}\n[fast-jev-compaction truncated {max(0, len(full) - 300)} chars of this tool result; re-run the tool if needed]"
    return f"role={role}\n" + "\n".join(parts)


def ask_raw(messages, timeout=300):
    body = json.dumps(
        {"model": MODEL, "temperature": 0, "max_tokens": 800, "messages": messages}
    )
    req = urllib.request.Request(
        URL, data=body.encode(), headers={"Content-Type": "application/json"}
    )
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = json.loads(r.read())
    return (d["choices"][0]["message"]["content"] or ""), round(time.time() - t0, 1)


SYS = "You are continuing an agent transcript. Produce the next assistant message text for the task at hand."


def ask(transcript):
    out, _ = ask_raw(
        [{"role": "system", "content": SYS}, {"role": "user", "content": transcript}]
    )
    return out


def build_turns():
    turns = []
    for s, sdir in SESS.items():
        msgs = load_messages(sdir)
        first_seen, last_seen = {}, {}
        for i, m in enumerate(msgs):
            for t in toks(msg_text(m)):
                if t not in first_seen:
                    first_seen[t] = i
                last_seen[t] = i
        for i, m in enumerate(msgs):
            if m.get("role") != "toolResult":
                continue
            text = msg_text(m)
            novel = {t for t in toks(text) if first_seen.get(t, 0) >= i}
            facts = sorted(t for t in novel if last_seen.get(t, -1) > i)[:8]
            if len(facts) >= 2:
                turns.append(
                    {
                        "session": s,
                        "tid": m.get("toolCallId"),
                        "idx": i,
                        "facts": facts,
                        "prefix": msgs[max(0, i - 12) : i + 1],
                    }
                )
        print(
            f"{s}: messages={len(msgs)} candidates={len([t for t in turns if t['session'] == s])}",
            flush=True,
        )
    pick = []
    for s in SESS:
        cands = sorted(
            [t for t in turns if t["session"] == s], key=lambda t: -len(t["facts"])
        )[:8]
        pick += cands
    print(f"turns={len(pick)} (8 largest-signal per session)", flush=True)
    return pick


def main():
    print(
        "PREREGISTERED: HARMLESS iff arm B reproduces the reused fact as often as arm A; "
        "paired diff over >=20 turns; e>=20 either way else INCONCLUSIVE.",
        flush=True,
    )
    pick = build_turns()
    with open("ablate_turns.jsonl", "w") as fh:
        for t in pick:
            fh.write(
                json.dumps(
                    {
                        "session": t["session"],
                        "tid": t["tid"],
                        "idx": t["idx"],
                        "facts": t["facts"],
                        "promptA": "\n---\n".join(render(m) for m in t["prefix"]),
                        "promptB": "\n---\n".join(
                            render(m, drop_result_id=t["tid"]) for m in t["prefix"]
                        ),
                    }
                )
                + "\n"
            )
    print(f"prep wrote ablate_turns.jsonl n={len(pick)}", flush=True)
    if "--prep-only" in sys.argv:
        print("PREP ONLY: arms pending a quiet window", flush=True)
        return
    with open("ablate_pairs.jsonl", "w") as out:
        for k, t in enumerate(pick):
            base = "\n---\n".join(render(m) for m in t["prefix"])
            outA, latA = ask_raw(
                [{"role": "system", "content": SYS}, {"role": "user", "content": base}]
            )
            baseB = "\n---\n".join(
                render(m, drop_result_id=t["tid"]) for m in t["prefix"]
            )
            outB, latB = ask_raw(
                [{"role": "system", "content": SYS}, {"role": "user", "content": baseB}]
            )
            outC, latC = ask_raw(
                [
                    {"role": "system", "content": SYS},
                    {"role": "user", "content": "Continue the agent's task."},
                ]
            )
            lowA, lowB, lowC = outA.lower(), outB.lower(), outC.lower()
            hitA = any(f in lowA for f in t["facts"])
            hitB = any(f in lowB for f in t["facts"])
            hitC = any(f in lowC for f in t["facts"])
            out.write(
                json.dumps(
                    {
                        "k": k,
                        "session": t["session"],
                        "tid": t["tid"],
                        "facts": t["facts"],
                        "hitA": hitA,
                        "hitB": hitB,
                        "hitC": hitC,
                        "latA": latA,
                        "latB": latB,
                        "latC": latC,
                    }
                )
                + "\n"
            )
            out.flush()
            print(
                f"turn {k}: A={hitA} B={hitB} C={hitC} "
                f"lat={latA}/{latB}/{latC}s facts={len(t['facts'])}",
                flush=True,
            )
    print("done", flush=True)


if __name__ == "__main__":
    main()
