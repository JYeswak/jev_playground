"""Sample tool calls + results from omp session files for threshold calibration.

Reads a session dir's *.jsonl/*.log rows, keeps type:'message' rows, pairs
toolCall parts (assistant messages) with toolResult messages by toolCallId, and
uniform-samples N pairs across the session timeline. Each candidate carries the
preceding user text (task context), earlier assistant texts (novelty baseline),
and later assistant texts (needed-later oracle).

Usage: python sample.py <session-dir> <out.jsonl> <n> <seed>
"""

import glob
import json
import random
import sys


def iter_messages(session_dir):
    rows = []
    for f in sorted(
        glob.glob(session_dir + "/*.jsonl") + glob.glob(session_dir + "/*.log")
    ):
        with open(f, errors="replace") as fh:
            for i, line in enumerate(fh):
                line = line.strip()
                if not line.startswith("{"):
                    continue
                try:
                    r = json.loads(line)
                except Exception:
                    continue
                m = r.get("message")
                if not isinstance(m, dict) or "role" not in m:
                    continue
                rows.append((r.get("timestamp", ""), f, i, m))
    rows.sort(key=lambda t: (t[0], t[1], t[2]))
    return [m for _, _, _, m in rows]


def text_parts(content):
    return [
        p.get("text", "")
        for p in content
        if isinstance(p, dict) and p.get("type") == "text"
    ]


def main(session_dir, out_path, n, seed):
    messages = iter_messages(session_dir)
    calls = {}
    results = {}
    assistant_texts = []
    last_user_text = ""
    for order, m in enumerate(messages):
        role = m.get("role")
        content = m.get("content") or []
        if role == "user":
            texts = text_parts(content)
            if texts:
                last_user_text = "\n".join(texts)
        elif role == "assistant":
            texts = text_parts(content)
            if texts:
                assistant_texts.append((order, "\n".join(texts)))
            for p in content:
                if isinstance(p, dict) and p.get("type") == "toolCall":
                    calls[p.get("id")] = {
                        "tool": p.get("name", "?"),
                        "arguments": p.get("arguments", {}),
                        "order": order,
                        "task_context": last_user_text,
                    }
        elif role == "toolResult":
            tid = m.get("toolCallId")
            texts = text_parts(content)
            if tid and tid not in results:
                results[tid] = {
                    "text": "\n".join(texts),
                    "is_error": bool(m.get("isError")),
                    "order": order,
                }
    pairs = []
    for tid, c in calls.items():
        r = results.get(tid)
        if r is None or not r["text"].strip():
            continue
        later = [t for o, t in assistant_texts if o > r["order"]]
        earlier = [t for o, t in assistant_texts if o < r["order"]]
        pairs.append(
            {
                "id": tid,
                "tool": c["tool"],
                "arguments": c["arguments"],
                "result_chars": len(r["text"]),
                "is_error": r["is_error"],
                "result_text": r["text"][:20000],
                "task_context": c["task_context"][-4000:],
                "earlier_text": "\n".join(earlier)[-60000:],
                "later_text": "\n".join(later)[:60000],
                "n_later_turns": len(later),
            }
        )
    rng = random.Random(seed)
    if len(pairs) > n:
        step = len(pairs) / n
        pairs = [pairs[int(i * step)] for i in range(n)]
    rng.shuffle(pairs)
    with open(out_path, "w") as fh:
        for p in pairs:
            fh.write(json.dumps(p) + "\n")
    print(
        f"messages={len(messages)} calls={len(calls)} results={len(results)} "
        f"paired={len(pairs)} written={out_path}"
    )


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4] or 0))
