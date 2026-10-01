#!/usr/bin/env python3
"""jev-ynn7 real-repo: grade one A/B run from its --session-dir. Prints JSON.
Success = agent read/edited a file under REPODIR whose content contains TOKEN.
Tokens = (find+grep+glob tool-result chars)/4 across the whole session.
Usage: grade_real.py <session-dir> <repodir> <token>
"""

import glob
import json
import os
import sys

TOOLS = ("find", "grep", "glob")
FOLLOW = ("read", "edit", "write")


def main() -> int:
    sdir, repodir, token = sys.argv[1], os.path.abspath(sys.argv[2]), sys.argv[3]
    files = glob.glob(os.path.join(sdir, "*.jsonl"))
    reads, results = [], {}
    calls = {}
    for path in files:
        with open(path, encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                if '"toolCall"' not in line and '"toolResult"' not in line:
                    continue
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                msg = row.get("message") or {}
                if msg.get("role") == "assistant":
                    for c in msg.get("content") or []:
                        if isinstance(c, dict) and c.get("type") == "toolCall":
                            args = c.get("arguments") or {}
                            tgt = str(
                                args.get("path") or args.get("file_path") or ""
                            ).split(":")[0]
                            calls[c.get("id")] = c.get("name")
                            if c.get("name") in FOLLOW and tgt:
                                reads.append(tgt)
                elif msg.get("role") == "toolResult":
                    name = calls.get(msg.get("toolCallId"))
                    if name is None:
                        continue
                    text = "".join(
                        x.get("text", "")
                        for x in msg.get("content") or []
                        if isinstance(x, dict)
                    )
                    results[msg.get("toolCallId")] = (name, len(text))
    success = False
    for tgt in reads:
        cand = tgt if os.path.isabs(tgt) else os.path.join(repodir, tgt.lstrip("./"))
        cand = os.path.normpath(cand)
        if os.path.isfile(cand) and os.path.commonpath([cand, repodir]) == repodir:
            try:
                with open(cand, encoding="utf-8", errors="ignore") as fh:
                    if token in fh.read():
                        success = True
                        break
            except OSError:
                continue
    per_tool = {t: {"calls": 0, "chars": 0} for t in TOOLS}
    for _, (name, chars) in results.items():
        if name in per_tool:
            per_tool[name]["calls"] += 1
            per_tool[name]["chars"] += chars
    print(
        json.dumps(
            {
                "success": success,
                "tokens_locate": round(
                    sum(v["chars"] for v in per_tool.values()) / 4, 1
                ),
                "per_tool": per_tool,
                "n_reads": len(reads),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
