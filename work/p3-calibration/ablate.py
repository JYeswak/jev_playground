"""Ablate-and-rerun class-D test (LOCAL model, zero marginal cost).

PREREGISTERED (printed before any model call): compaction is HARMLESS on a
turn if arm B (result replaced by fast-jev-compaction's real truncation note)
reproduces the reused fact as often as arm A (intact). Paired difference over
>=20 turns; discordant count reported (concordant pairs carry no information).
Verdict via e-process (Ville, conservative): e>=20 either way else
INCONCLUSIVE. HARMLESS / HARMFUL / INCONCLUSIVE.

Indexing is LINEAR (token -> first/last row maps, after oracle.mjs); an
earlier quadratic version OOM-stalled and was killed.

Per turn: transcript prefix (<=12 messages) from the real session file,
A intact, B with result -> head(300) + note. Local model produces the next
assistant message (temperature 0). Score: any oracle-identified reused token
in the output (deterministic check).
Model: Qwen3.6-27B-4bit-MTP-MLX-Serve @127.0.0.1:11238 (NOT the brief's
3.8-Splash: not serving on this machine; substitution disclosed).
Usage: python ablate.py [--prep-only]  (writes ablate_turns.jsonl always;
  with model arms, ablate_pairs.jsonl)
"""

import glob
import json
import os
import re
import sys
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


def ask(transcript):
    body = json.dumps(
        {
            "model": MODEL,
            "temperature": 0,
            "max_tokens": 800,
            "messages": [
                {
                    "role": "system",
                    "content": "You are continuing an agent transcript. Produce the next assistant message text for the task at hand.",
                },
                {"role": "user", "content": transcript},
            ],
        }
    )
    req = urllib.request.Request(
        URL, data=body.encode(), headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=300) as r:
        d = json.loads(r.read())
    return d["choices"][0]["message"]["content"] or ""


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
            outA = ask(base)
            baseB = "\n---\n".join(
                render(m, drop_result_id=t["tid"]) for m in t["prefix"]
            )
            outB = ask(baseB)
            lowA, lowB = outA.lower(), outB.lower()
            hitA = any(f in lowA for f in t["facts"])
            hitB = any(f in lowB for f in t["facts"])
            out.write(
                json.dumps(
                    {
                        "k": k,
                        "session": t["session"],
                        "tid": t["tid"],
                        "facts": t["facts"],
                        "hitA": hitA,
                        "hitB": hitB,
                    }
                )
                + "\n"
            )
            out.flush()
            print(f"turn {k}: A={hitA} B={hitB} facts={len(t['facts'])}", flush=True)
    print("done", flush=True)


if __name__ == "__main__":
    main()
