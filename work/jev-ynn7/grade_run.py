#!/usr/bin/env python3
"""jev-ynn7: grade one A/B run from its --session-dir. Prints JSON.
Success = target file read (read/edit/write call whose target endswith the file).
Tokens = (find+grep+glob tool-result chars)/4. Counts calls per tool.
Usage: grade_run.py <session-dir> <target-file>
"""

import glob
import json
import os
import sys

TOOLS = ("find", "grep", "glob")
FOLLOW = ("read", "edit", "write")


def main() -> int:
    sdir, target = sys.argv[1], sys.argv[2]
    files = glob.glob(os.path.join(sdir, "*", "*.jsonl")) or glob.glob(
        os.path.join(sdir, "*.jsonl")
    )
    calls, results = {}, {}
    success = False
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
                        if c.get("type") == "toolCall":
                            args = c.get("arguments") or {}
                            tgt = str(args.get("path") or args.get("file_path") or "")
                            calls[c.get("id")] = (c.get("name"), tgt.split(":")[0])
                            if c.get("name") in FOLLOW and tgt.replace(
                                "\\", "/"
                            ).endswith(target.replace("\\", "/")):
                                success = True
                elif msg.get("role") == "toolResult":
                    item = calls.get(msg.get("toolCallId"))
                    if item is None:
                        continue
                    text = "".join(
                        x.get("text", "")
                        for x in msg.get("content") or []
                        if isinstance(x, dict)
                    )
                    results[msg.get("toolCallId")] = (item[0], len(text))
    per_tool = {t: {"calls": 0, "chars": 0} for t in TOOLS}
    for _, (name, chars) in results.items():
        if name in per_tool:
            per_tool[name]["calls"] += 1
            per_tool[name]["chars"] += chars
    tokens = sum(v["chars"] for v in per_tool.values()) / 4
    print(
        json.dumps(
            {
                "success": success,
                "tokens_locate": round(tokens, 1),
                "per_tool": per_tool,
                "n_result_rows": len(results),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
