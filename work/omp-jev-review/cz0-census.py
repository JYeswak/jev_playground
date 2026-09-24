#!/usr/bin/env python3
"""jev-cz0 census: how many real decision rows do commit, review and rerank have?

Scans every omp session transcript this machine keeps (the default agent root and every profile
root). Counts a row only after parsing the JSON line; a substring match is not a row, because
source code pasted into tool output contains the same type strings (the 2026-09-19 receipt's
warning). Keyless and offline. Prints counts and, per extension, the verdict/status breakdown.

    python3 work/omp-jev-review/cz0-census.py
Exit 0 always; this is a census, not a gate.
"""

import collections
import glob
import json
import os

HOME = os.path.expanduser("~")
ROOTS = [f"{HOME}/.omp/agent/sessions"] + glob.glob(
    f"{HOME}/.omp/profiles/*/agent/sessions"
)
TYPES = {
    "com.zeststream.omp-jev-review.decision.v1": "review",
    "com.zeststream.omp-jev-commit.decision.v1": "commit",
}
TOOL = "jev_rerank"


def main():
    files = [f for r in ROOTS for f in glob.glob(f"{r}/**/*.jsonl", recursive=True)]
    decisions = collections.defaultdict(collections.Counter)
    rerank_calls = collections.Counter()
    rerank_results = collections.Counter()
    sessions = collections.defaultdict(set)
    for path in files:
        try:
            fh = open(path, encoding="utf-8", errors="replace")
        except OSError:
            continue
        with fh:
            for line in fh:
                if "omp-jev-" not in line and TOOL not in line:
                    continue
                try:
                    e = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(e, dict):
                    continue
                ct = e.get("customType")
                if isinstance(ct, str) and ct in TYPES:
                    data = e.get("data") or {}
                    decisions[TYPES[ct]][
                        str(
                            data.get("status")
                            or data.get("kind")
                            or data.get("outcome")
                            or "?"
                        )
                    ] += 1
                    sessions[TYPES[ct]].add(path)
                    continue
                msg = e.get("message") if isinstance(e.get("message"), dict) else e
                for part in (
                    msg.get("content") or []
                    if isinstance(msg.get("content"), list)
                    else []
                ):
                    if not isinstance(part, dict):
                        continue
                    if part.get("type") == "toolCall" and part.get("name") == TOOL:
                        rerank_calls["call"] += 1
                        sessions["rerank"].add(path)
                if msg.get("role") == "toolResult" and msg.get("toolName") == TOOL:
                    details = msg.get("details") or {}
                    rerank_results[
                        str(
                            details.get("reason")
                            or ("ordered" if details.get("ordered") else "?")
                        )
                    ] += 1
    print(f"session files scanned: {len(files)} under {len(ROOTS)} roots")
    for ext in ("commit", "review"):
        print(
            f"{ext}: {sum(decisions[ext].values())} decision rows in {len(sessions[ext])} sessions {dict(decisions[ext])}"
        )
    print(
        f"rerank: {rerank_calls['call']} tool calls, {sum(rerank_results.values())} results {dict(rerank_results)} in {len(sessions['rerank'])} sessions"
    )


if __name__ == "__main__":
    main()
