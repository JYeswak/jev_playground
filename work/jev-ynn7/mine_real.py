#!/usr/bin/env python3
"""jev-ynn7 real-repo tasks: mine located-grep episodes from omp session files.

A located episode = grep call whose result paths include a file read/edited
within the next 5 tool calls (jev-04q2 definition). Emits candidates with the
original pattern, followed file, and session provenance.
Usage: mine_real.py [--days 7]  -> JSON lines on stdout.
"""

import glob
import json
import os
import re
import sys
import time

HOME = os.path.expanduser("~")
PATH_RE = re.compile(r"(?:[\w.\-]+/)+[\w.\-]+\.\w{1,8}")
FOLLOW = ("read", "edit", "write")
WINDOW = 5


def main() -> int:
    days = int(sys.argv[sys.argv.index("--days") + 1]) if "--days" in sys.argv else 7
    cutoff = time.time() - days * 86400
    roots = [os.path.join(HOME, ".omp", "agent", "sessions")] + glob.glob(
        os.path.join(HOME, ".omp", "profiles", "*", "agent", "sessions")
    )
    for root in roots:
        for path in glob.glob(os.path.join(root, "*", "*.jsonl")):
            try:
                if os.stat(path).st_mtime < cutoff:
                    continue
            except FileNotFoundError:
                continue
            order, by_id = [], {}
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
                                item = {
                                    "id": c.get("id"),
                                    "name": c.get("name"),
                                    "args": args,
                                    "target": str(
                                        args.get("path") or args.get("file_path") or ""
                                    ).split(":")[0],
                                    "paths": set(),
                                    "chars": 0,
                                }
                                by_id[c.get("id")] = item
                                order.append(item)
                    elif msg.get("role") == "toolResult":
                        item = by_id.get(msg.get("toolCallId"))
                        if item is None:
                            continue
                        text = "".join(
                            x.get("text", "")
                            for x in msg.get("content") or []
                            if isinstance(x, dict)
                        )
                        item["chars"] = len(text)
                        item["paths"] = set(PATH_RE.findall(text))
            for i, item in enumerate(order):
                if item["name"] != "grep" or not item["paths"]:
                    continue
                for f in order[i + 1 : i + 1 + WINDOW]:
                    if (
                        f["name"] in FOLLOW
                        and f["target"]
                        and any(
                            f["target"].endswith(p)
                            or p.endswith(f["target"].lstrip("./"))
                            for p in item["paths"]
                        )
                    ):
                        print(
                            json.dumps(
                                {
                                    "session": path,
                                    "tool_id": item["id"],
                                    "pattern": str(
                                        (item["args"] or {}).get("pattern") or ""
                                    ),
                                    "grep_path": str(
                                        (item["args"] or {}).get("path") or ""
                                    ),
                                    "file": f["target"],
                                    "result_chars": item["chars"],
                                }
                            )
                        )
                        break
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
