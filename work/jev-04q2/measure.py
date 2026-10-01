#!/usr/bin/env python3
"""jev-04q2: tokens spent per located file, find vs grep vs glob, from omp session files (keyless).

A call "locates" a file when a path present in its tool result is read or edited within the next
5 tool calls of the same session. Tokens = tool-result characters / 4. The shuffled control pairs
each call's result paths with a different call's follow-ups and must locate ~nothing.
Run: python3 work/jev-04q2/measure.py [--days 7]
"""

from __future__ import annotations

import json
import math
import random
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

HOME = Path.home()
TOOLS = ("find", "grep", "glob")
FOLLOW = ("read", "edit", "write")
PATH_RE = re.compile(r"(?:[\w.\-]+/)+[\w.\-]+\.\w{1,8}")
WINDOW = 5


def wilson(k: int, n: int) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    z, p = 1.96, k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)


def sessions(days: int):
    cutoff = time.time() - days * 86400
    roots = [HOME / ".omp/agent/sessions"] + list(
        (HOME / ".omp/profiles").glob("*/agent/sessions")
    )
    for root in roots:
        for path in root.glob("*/*.jsonl"):
            try:
                if path.stat().st_mtime >= cutoff:
                    yield path
            except FileNotFoundError:
                continue


def calls_in(path: Path) -> list[dict]:
    """Ordered tool calls of one session: name, target paths (follow-ups) and result paths/size."""
    order, by_id = [], {}
    with path.open(encoding="utf-8", errors="ignore") as fh:
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
                        target = str(args.get("path") or args.get("file_path") or "")
                        item = {
                            "name": c.get("name"),
                            "target": target.split(":")[0],
                            "chars": 0,
                            "paths": set(),
                        }
                        by_id[c.get("id")] = item
                        order.append(item)
            elif msg.get("role") == "toolResult":
                item = by_id.get(msg.get("toolCallId"))
                if item is None:
                    continue
                text = "".join(
                    c.get("text", "")
                    for c in msg.get("content") or []
                    if isinstance(c, dict)
                )
                item["chars"] = len(text)
                item["paths"] = set(PATH_RE.findall(text))
    return order


def located(item: dict, followers: list[dict]) -> bool:
    for f in followers:
        if f["name"] in FOLLOW and f["target"]:
            if any(
                f["target"].endswith(p) or p.endswith(f["target"].lstrip("./"))
                for p in item["paths"]
            ):
                return True
    return False


def main(argv: list[str]) -> int:
    days = int(argv[argv.index("--days") + 1]) if "--days" in argv else 7
    stats = defaultdict(lambda: {"n": 0, "loc": 0, "chars": 0, "ctrl_loc": 0})
    pool = []
    for path in sessions(days):
        seq = calls_in(path)
        for i, item in enumerate(seq):
            if item["name"] not in TOOLS or not item["paths"]:
                continue
            followers = seq[i + 1 : i + 1 + WINDOW]
            s = stats[item["name"]]
            s["n"] += 1
            s["chars"] += item["chars"]
            s["loc"] += located(item, followers)
            pool.append((item, followers))
    rng = random.Random(20261001)
    shuffled = [f for _, f in pool]
    rng.shuffle(shuffled)
    for (item, _), followers in zip(pool, shuffled):
        stats[item["name"]]["ctrl_loc"] += located(item, followers)
    out = {}
    for name in TOOLS:
        s = stats[name]
        tokens = s["chars"] / 4
        lo, hi = wilson(s["loc"], s["n"])
        out[name] = {
            "calls_with_paths": s["n"],
            "located": s["loc"],
            "located_rate": round(s["loc"] / s["n"], 4) if s["n"] else None,
            "located_ci95": [round(lo, 4), round(hi, 4)],
            "tokens_per_located": round(tokens / s["loc"], 1) if s["loc"] else None,
            "control_located": s["ctrl_loc"],
        }
    print(json.dumps({"days": days, "window": WINDOW, "tools": out}, indent=2))
    f, g = out["find"], out["grep"]
    if f["tokens_per_located"] and g["tokens_per_located"]:
        ok = f["tokens_per_located"] <= 0.8 * g["tokens_per_located"] and f[
            "located_ci95"
        ][1] >= (g["located_rate"] or 0)
        print(
            f"BAR {'PASS' if ok else 'FAIL'}: find {f['tokens_per_located']} vs grep {g['tokens_per_located']} tokens/located"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
