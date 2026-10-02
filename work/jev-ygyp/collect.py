#!/usr/bin/env python3
"""jev-ygyp: collect (cass search -> opened hit) pairs from omp session files.
Search results are often truncated (piped through head), so hits come from
source_path regex in result order; query comes from the call command.
A search locates a hit when a follow-up cass view/read targets the hit's
source_path within the next 10 tool calls. Prints JSON lines.
Usage: collect.py [--days N]
"""

import glob
import json
import os
import re
import sys

HOME = os.path.expanduser("~")
WINDOW = 10
SRCPATH_RE = re.compile(r'"source_path"\s*:\s*"([^"]+)"')
QUERY_RE = re.compile(r'cass search\s+"([^"]+)"|cass search\s+(\S+)')


def main() -> int:
    days = int(sys.argv[sys.argv.index("--days") + 1]) if "--days" in sys.argv else 30
    import time

    cutoff = time.time() - days * 86400
    roots = [os.path.join(HOME, ".omp", "agent", "sessions")] + glob.glob(
        os.path.join(HOME, ".omp", "profiles", "*", "agent", "sessions")
    )
    for root in roots:
        for path in glob.glob(os.path.join(root, "*", "*.jsonl")):
            try:
                if os.stat(path).st_mtime < cutoff:
                    continue
            except OSError:
                continue
            order, by_id = [], {}
            try:
                lines = (
                    open(path, encoding="utf-8", errors="ignore").read().splitlines()
                )
            except OSError:
                continue
            for line in lines:
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
                            cmd = str(args.get("command") or "")
                            tgt = str(args.get("path") or args.get("file_path") or "")
                            by_id[c.get("id")] = {
                                "name": c.get("name"),
                                "cmd": cmd,
                                "target": tgt.split(":")[0],
                                "paths": [],
                            }
                            order.append(by_id[c.get("id")])
                elif msg.get("role") == "toolResult":
                    item = by_id.get(msg.get("toolCallId"))
                    if item is None:
                        continue
                    text = "".join(
                        x.get("text", "")
                        for x in msg.get("content") or []
                        if isinstance(x, dict)
                    )
                    if "cass search" in item["cmd"]:
                        m = QUERY_RE.search(item["cmd"])
                        item["query"] = (m.group(1) or m.group(2)) if m else ""
                        seen = set()
                        for p in SRCPATH_RE.findall(text):
                            if p not in seen:
                                seen.add(p)
                                item["paths"].append(p)
            for i, item in enumerate(order):
                if "cass search" not in item["cmd"] or not item["paths"]:
                    continue
                for f in order[i + 1 : i + 1 + WINDOW]:
                    t = f["target"] or ""
                    hit = next(
                        (
                            p
                            for p in item["paths"]
                            if p
                            and (
                                t.endswith(p)
                                or p.endswith(t.lstrip("./"))
                                or t in p
                                or ("cass view" in f["cmd"] and p in f["cmd"])
                            )
                        ),
                        None,
                    )
                    if hit is not None:
                        print(
                            json.dumps(
                                {
                                    "session": path,
                                    "query": item.get("query", ""),
                                    "hits": item["paths"],
                                    "opened": hit,
                                    "rank": item["paths"].index(hit) + 1,
                                }
                            )
                        )
                        break
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
