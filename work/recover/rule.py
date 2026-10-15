"""N4 recover rule: observational error-class cohorts (jev-n4-recover-error-rule-1grh).

Rule R under test (frozen in work/recover/PREREG.md):
- bash timeout / network / lock errors -> retry the call.
- bash syntax / not-found / permission errors -> change the call.
- edit stale_tag -> re-read before acting.

Read-only over session rows. Never imputes outcomes: success 'under the
rule' for rows where the agent did not follow R raises Refused as
NOT_IDENTIFIABLE. All cohort figures are labelled OBSERVATIONAL.
No model calls, no keys, no network.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

CONSTANTS = {"next_call_ok_1": 0.853, "next_call_ok_2": 0.854}
MIN_N = 10
MARGIN = 0.10

TIMEOUT_RES = ["timed out", "timeout", "deadline exceeded", "timedout"]
NETWORK_RES = ["network", "econnrefused", "econnreset", "enotfound", "dns", "socket hang up", "fetch failed"]
LOCK_RES = ["lock", "locked", "ebusy", "resource busy", "try again"]
SYNTAX_RES = ["syntax error", "unexpected token", "parse error", "bad substitution"]
NOTFOUND_RES = ["command not found", "no such file", "not found", "enoent"]
PERMISSION_RES = ["permission denied", "eacces", "operation not permitted"]


def classify_bash_error(text: str) -> str | None:
    lowered = (text or "").lower()
    for token in TIMEOUT_RES:
        if token in lowered:
            return "timeout"
    for token in NETWORK_RES:
        if token in lowered:
            return "network"
    for token in LOCK_RES:
        if token in lowered:
            return "lock"
    for token in SYNTAX_RES:
        if token in lowered:
            return "syntax"
    for token in NOTFOUND_RES:
        if token in lowered:
            return "not-found"
    for token in PERMISSION_RES:
        if token in lowered:
            return "permission"
    return None


def classify_edit_error(arguments: dict) -> str | None:
    blob = json.dumps(arguments or {}).lower()
    if "stale_tag" in blob or "stale tag" in blob:
        return "stale-tag"
    return None


def prescribed_action(tool: str, error_class: str | None) -> str | None:
    """What rule R prescribes after an error, or None when R is silent."""
    if tool == "bash" and error_class in ("timeout", "network", "lock"):
        return "retry"
    if tool == "bash" and error_class in ("syntax", "not-found", "permission"):
        return "change"
    if tool == "edit" and error_class == "stale-tag":
        return "re-read"
    return None


def same_command(first: dict, second: dict) -> bool:
    return json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def next_action_kind(failed_call: dict, next_call: dict | None) -> str | None:
    """'retry' when the next call repeats the failed call, else 'change'."""
    if next_call is None:
        return None
    if next_call.get("name") != failed_call.get("name"):
        return "change"
    if same_command(failed_call.get("arguments", {}), next_call.get("arguments", {})):
        return "retry"
    return "change"


def flag_violation(tool: str, error_class: str | None, action: str | None) -> bool:
    """True when the observed next action disobeys R's prescription."""
    prescribed = prescribed_action(tool, error_class)
    if prescribed is None or action is None:
        return False
    return action != prescribed


def iter_calls(rows: list):
    """Yield (call, result, next_call, next_result) tuples in row order.

    Fixture schema is mixed: assistant tool calls arrive as content parts
    ({type: toolCall}), while tool results arrive at message level
    (role: toolResult with toolCallId/isError/content on the message).
    """
    pending: dict[str, dict] = {}
    order: list[str] = []
    for row in rows:
        if row.get("type") != "message":
            continue
        message = row.get("message", {})
        if message.get("role") == "toolResult":
            cid = message.get("toolCallId")
            entry = pending.get(cid) if isinstance(cid, str) else None
            if entry is not None:
                entry["result"] = {"is_error": bool(message.get("isError")),
                                   "text": json.dumps(message.get("content", []))}
            continue
        for part in message.get("content", []):
            if not isinstance(part, dict):
                continue
            if part.get("type") == "toolCall":
                cid = part.get("id")
                if not isinstance(cid, str):
                    continue
                pending[cid] = {
                    "call": {"name": part.get("name"), "arguments": part.get("arguments", {})},
                    "result": None,
                }
                order.append(cid)
    calls = [pending[cid] for cid in order]
    for i, entry in enumerate(calls):
        nxt = calls[i + 1] if i + 1 < len(calls) else None
        yield (entry["call"], entry["result"],
               nxt["call"] if nxt else None,
               nxt["result"] if nxt else None)


def error_text(result: dict | None) -> str:
    if not result or not result.get("is_error"):
        return ""
    return result.get("text", "")


def next_succeeded(next_result: dict | None) -> bool | None:
    if next_result is None:
        return None
    return not next_result.get("is_error", True)


def estimate_effect(_episodes: list) -> dict:
    """Refuse: success under the rule cannot be identified from agreement."""
    raise Refused("NOT_IDENTIFIABLE: agreement cohorts are observational; "
                  "untaken actions have no observed outcome")


class Refused(Exception):
    pass


def wilson_interval(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n <= 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2.0 * n)) / denom
    half = z * math.sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n)) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def score_rows(rows: list) -> dict:
    episodes: list[dict] = []
    for call, result, nxt, next_result in iter_calls(rows):
        if not result or not result.get("is_error"):
            continue
        tool = call.get("name")
        if tool == "bash":
            klass = classify_bash_error(error_text(result))
        elif tool == "edit":
            klass = classify_edit_error(call.get("arguments", {}))
        else:
            klass = None
        action = next_action_kind(call, nxt)
        prescribed = prescribed_action(tool, klass)
        episodes.append({"tool": tool, "class": klass, "action": action,
                         "agree": (action == prescribed) if (klass and action) else None,
                         "next_ok": next_succeeded(next_result)})
    return {"episodes": episodes}


def summarize(episodes: list) -> dict:
    classes: dict[str, dict] = {}
    for ep in episodes:
        if not ep["class"]:
            continue
        bucket = classes.setdefault(ep["class"], {"agree_n": 0, "agree_ok": 0, "disagree_n": 0, "disagree_ok": 0})
        if ep["agree"] is True:
            bucket["agree_n"] += 1
            if ep["next_ok"] is True:
                bucket["agree_ok"] += 1
        elif ep["agree"] is False:
            bucket["disagree_n"] += 1
            if ep["next_ok"] is True:
                bucket["disagree_ok"] += 1
    out = {}
    for klass, b in sorted(classes.items()):
        if min(b["agree_n"], b["disagree_n"]) < MIN_N:
            out[klass] = {"status": "NOT_POWERED", **b}
            continue
        lo_a, hi_a = wilson_interval(b["agree_ok"], b["agree_n"])
        lo_d, hi_d = wilson_interval(b["disagree_ok"], b["disagree_n"])
        out[klass] = {"status": "SCORED", **b,
                      "agree_rate": b["agree_ok"] / b["agree_n"],
                      "disagree_rate": b["disagree_ok"] / b["disagree_n"],
                      "difference": b["agree_ok"] / b["agree_n"] - b["disagree_ok"] / b["disagree_n"],
                      "agree_ci95": [lo_a, hi_a], "disagree_ci95": [lo_d, hi_d]}
    return out


def main(argv: list[str]) -> int:
    import argparse
    parser = argparse.ArgumentParser(description="N4 observational recover-rule cohorts")
    parser.add_argument("--rows", default="work/fleet-schema/fixtures/sessions.jsonl")
    parser.add_argument("--json", action="store_true",
                        help="emit the report as JSON (the sole output envelope)")
    args = parser.parse_args(argv)
    rows = [json.loads(line) for line in Path(args.rows).read_text(encoding="utf-8").splitlines() if line.strip()]
    scored = score_rows(rows)
    report = {"tool": "rule.py", "bead": "jev-n4-recover-error-rule-1grh",
              "estimand": "OBSERVATIONAL",
              "constants": CONSTANTS,
              "cohorts": summarize(scored["episodes"]),
              "unclassified_errors": sum(1 for e in scored["episodes"] if not e["class"])}
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
