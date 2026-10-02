#!/usr/bin/env python3
"""jev-r8dp: per-hook per-day census of Jev calls vs per-process caps.
Reads ~/.local/state/jev/*.jsonl (last 7d by UTC day) + native typesafe
model_usage spend from omp session files. Prints JSON.
"""

import datetime
import glob
import json
import os

HOME = os.path.expanduser("~")
RATE = 0.042 / 1e6
HOOKS = {
    "gate-observe": ("gate-observe.jsonl", 1000),
    "injection-shadow": ("injection-shadow.jsonl", 100),
    "webscreen-shadow": ("webscreen-shadow.jsonl", 25),
    "memory-filter": ("memory-filter.jsonl", 200),
    "websearch-rerank": ("websearch-rerank.jsonl", 100),
    "needs-human": ("fleet-needs-human-calls.jsonl", 100),
    "skill-hint": ("skill-hint-calls.jsonl", 100),
}


def day(ts):
    try:
        return ts[:10]
    except (TypeError, IndexError):
        return None


def main() -> int:
    today = datetime.datetime.now(datetime.timezone.utc).date()
    days = sorted(str(today - datetime.timedelta(days=i)) for i in range(7))
    out = {}
    for hook, (fname, cap) in HOOKS.items():
        per = {d: {"rows": 0, "paid": 0, "in_tok": 0, "inst": set()} for d in days}
        try:
            fh = open(
                os.path.join(HOME, ".local", "state", "jev", fname),
                encoding="utf-8",
                errors="ignore",
            )
        except OSError:
            out[hook] = {"cap": cap, "error": "no log"}
            continue
        for line in fh:
            try:
                r = json.loads(line)
            except ValueError:
                continue
            d = day(r.get("ts", ""))
            if d not in per:
                continue
            s = per[d]
            s["rows"] += 1
            inst = (
                r.get("instance")
                or r.get("session")
                or r.get("sessionHash")
                or r.get("pane")
            )
            if inst is not None:
                s["inst"].add(str(inst))
            # Only new billed calls count: memo/daily-cap/cap/not-run/error/
            # skipped/observed rows made no new Jev call (or were refused).
            status = str(r.get("status") or "")
            tok = (
                r.get("input_tokens")
                or r.get("inputTokens")
                or ((r.get("tokens") or {}).get("input_tokens"))
            )
            mdl = str(r.get("model") or "")
            new_call = isinstance(tok, (int, float)) and status not in (
                "memo",
                "daily-cap",
                "cap",
                "not-run",
                "error",
                "skipped",
                "observed",
            )
            if hook == "gate-observe":
                paid_row = new_call and mdl == "jev-1.13.0"
            else:
                paid_row = new_call
            if paid_row:
                s["paid"] += 1
                s["in_tok"] += tok
            if status in ("daily-cap", "cap"):
                s["cap_hit"] = s.get("cap_hit", 0) + 1
        out[hook] = {
            "cap": cap,
            "days": {d: {**v, "inst": len(v["inst"])} for d, v in per.items()},
        }
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
