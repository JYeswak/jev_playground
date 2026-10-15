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
import hashlib
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


def classify_edit_error(text: str) -> str | None:
    """Classify from the error result text (where real stale-tag failures
    surface), never from call arguments."""
    lowered = (text or "").lower()
    if "stale_tag" in lowered or "stale tag" in lowered:
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
    """Classify the observed next action: 'retry' for a repeated call,
    're-read' for an edit failure followed by a read of the same file,
    otherwise 'change'."""
    if next_call is None:
        return None
    if (failed_call.get("name") == "edit" and next_call.get("name") == "read"
            and isinstance(failed_call.get("arguments"), dict)
            and isinstance(next_call.get("arguments"), dict)
            and failed_call["arguments"].get("path") is not None
            and failed_call["arguments"].get("path") == next_call["arguments"].get("path")):
        return "re-read"
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
    """Yield (call, result, next_call, next_result, session) tuples.

    Joins never cross session markers: each session (plus the leading
    unmarked rows) is an independent partition, so a trailing failure
    cannot borrow the next session's first action, and duplicate call IDs
    in different sessions cannot overwrite each other.
    """
    partitions: list[tuple[str | None, dict, list]] = []

    def new_partition(session: str | None):
        partitions.append((session, {}, []))

    new_partition(None)
    current = 0
    for row in rows:
        if row.get("type") == "session" and isinstance(row.get("id"), str):
            new_partition(row["id"])
            current = len(partitions) - 1
            continue
        if row.get("type") != "message":
            continue
        _, pending, order = partitions[current]
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
    for session, pending, order in partitions:
        calls = [pending[cid] for cid in order]
        for i, entry in enumerate(calls):
            nxt = calls[i + 1] if i + 1 < len(calls) else None
            yield (entry["call"], entry["result"],
                   nxt["call"] if nxt else None,
                   nxt["result"] if nxt else None,
                   session)


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


def authorized_arm_designs(prereg_text: str) -> list:
    """Design ids explicitly preregistered, one per `design: <id>` line."""
    designs = []
    for line in (prereg_text or "").splitlines():
        stripped = line.strip()
        if stripped.startswith("design:"):
            designs.append(stripped[len("design:"):].strip())
    return designs


def authorize_arm(design_id: str, prereg_text: str) -> str:
    """Allow only preregistered model-arm designs; refuse everything else.
    The refuted R142 Choice design is refused UNCONDITIONALLY, even if a
    `design:` line ever names it: refuted stays refuted."""
    lowered = design_id.lower()
    if "r142" in lowered or ("retry_identical" in lowered and "fix_first" in lowered):
        raise Refused("REFUTED-ARM: R142 Choice design is refuted and never authorized")
    if design_id in authorized_arm_designs(prereg_text):
        return design_id
    raise Refused(f"NOT_PREREGISTERED: model arm '{design_id}' has no preregistered design")

def verify_receipt_block(block: dict, answers_rows: list, dev_ids: set, held_ids: set, answers_sha: str) -> dict:
    """Recompute the RECEIPT machine block from answers rows; raise Refused
    naming the first mismatching field. The tool itself calls this before
    printing any score, so a drifted receipt fails closed."""
    dev_rows = [r for r in answers_rows if r.get("session") in dev_ids]
    held_rows = [r for r in answers_rows if r.get("session") in held_ids]
    expected = {
        "answers_rows": len(answers_rows),
        "answers_sha256": answers_sha,
        "cohorts_dev": summarize(dev_rows),
        "cohorts_held": summarize(held_rows),
        "unclassified_errors": sum(1 for r in answers_rows if not r.get("class")),
    }
    mismatches = [k for k in expected if expected[k] != block.get(k)]
    if mismatches:
        raise Refused(f"RECEIPT_MISMATCH: fields differ: {', '.join(mismatches)}")
    return {"ok": True, "checked": sorted(expected)}

def check_receipt(answers_path, receipt_path, dev_ids: set, held_ids: set) -> dict:
    """Load answers + committed machine block and verify; raise Refused on
    any missing file, malformed JSON, or recompute mismatch. No UNVERIFIED
    path: absence fails closed with nonzero exit at the caller."""
    try:
        answers_bytes = Path(answers_path).read_bytes()
    except OSError as exc:
        raise Refused(f"MISSING answers file: {exc}")
    try:
        answers_rows = [json.loads(line) for line in answers_bytes.decode("utf-8").splitlines() if line.strip()]
    except ValueError as exc:
        raise Refused(f"MALFORMED answers file: {exc}")
    try:
        receipt_text = Path(receipt_path).read_text(encoding="utf-8")
        start = receipt_text.index("```json", receipt_text.index("## Machine block"))
        block = json.loads(receipt_text[start + len("```json"):receipt_text.index("```", start + 7)])
    except (OSError, ValueError) as exc:
        raise Refused(f"MISSING machine block: {exc}")
    return {"status": "VERIFIED", **verify_receipt_block(
        block, answers_rows, dev_ids, held_ids, hashlib.sha256(answers_bytes).hexdigest())}

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
    for call, result, nxt, next_result, session in iter_calls(rows):
        if not result or not result.get("is_error"):
            continue
        tool = call.get("name")
        if tool == "bash":
            klass = classify_bash_error(error_text(result))
        elif tool == "edit":
            klass = classify_edit_error(error_text(result))
        else:
            klass = None
        action = next_action_kind(call, nxt)
        prescribed = prescribed_action(tool, klass)
        episodes.append({"tool": tool, "class": klass, "action": action, "session": session,
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

def load_task(task_path: str):
    """Load N0's task envelope; refuse when it is missing or off-schema."""
    import argparse
    try:
        task = json.loads(Path(task_path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise SystemExit(f"task file unreadable: {exc}")
    if task.get("schema_version") != 1 or not task.get("fixture"):
        raise SystemExit("task file must carry schema_version 1 and a fixture path")
    rows_path = Path(task_path).parent / task["fixture"]
    try:
        raw = rows_path.read_bytes()
    except OSError as exc:
        raise SystemExit(f"task fixture unreadable: {exc}")
    rows = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    identity = {"path": str(task_path), "as_of": task.get("as_of"),
                "window_days": task.get("window_days"),
                "fixture": task["fixture"],
                "fixture_sha256": hashlib.sha256(raw).hexdigest()}
    return task, rows, identity


def split_sessions(rows: list) -> tuple[set, set]:
    """Mechanical dev/held split: first two sessions by (timestamp, id)."""
    seen: dict[str, str] = {}
    for row in rows:
        if row.get("type") == "session" and isinstance(row.get("id"), str):
            seen.setdefault(row["id"], str(row.get("timestamp", "")))
    ordered = sorted(seen, key=lambda sid: (seen[sid], sid))
    return set(ordered[:2]), set(ordered[2:])


def session_of(rows: list) -> dict[int, str | None]:
    """Map row index to its enclosing session id (None before any marker)."""
    current: str | None = None
    mapping: dict[int, str | None] = {}
    for i, row in enumerate(rows):
        if row.get("type") == "session" and isinstance(row.get("id"), str):
            current = row["id"]
        mapping[i] = current
    return mapping



def main(argv: list[str]) -> int:
    import argparse
    parser = argparse.ArgumentParser(description="N4 observational recover-rule cohorts")
    parser.add_argument("--task", default="work/fleet-schema/task.json",
                        help="N0 task envelope carrying the rows path")
    parser.add_argument("--json", action="store_true",
                        help="emit the report as JSON (the sole output envelope)")
    args = parser.parse_args(argv)
    _, rows, identity = load_task(args.task)
    dev_ids, held_ids = split_sessions(rows)
    scored = score_rows(rows)
    unmarked = [e for e in scored["episodes"] if e["session"] is None]
    dev_eps = [e for e in scored["episodes"] if (e["session"] or "") in dev_ids]
    held_eps = [e for e in scored["episodes"] if (e["session"] or "") in held_ids]
    root = Path(__file__).resolve().parent.parent.parent
    answers_path = root / "kit" / "fixtures" / "recover" / "answers-observed.jsonl"
    receipt_path = root / "work" / "recover" / "RECEIPT.md"
    try:
        receipt_check = check_receipt(answers_path, receipt_path, dev_ids, held_ids)
    except Refused as exc:
        print(str(exc), file=sys.stderr)
        return 2
    report = {"tool": "rule.py", "bead": "jev-n4-recover-error-rule-1grh",
              "estimand": "OBSERVATIONAL",
              "task": identity,
              "split": {"dev_sessions": sorted(dev_ids), "held_sessions": sorted(held_ids)},
              "constants": CONSTANTS,
              "cohorts_dev": summarize(dev_eps),
              "cohorts_held": summarize(held_eps),
              "unclassified_errors": sum(1 for e in scored["episodes"] if not e["class"]),
              "unmarked_session_errors": len(unmarked),
              "receipt_check": receipt_check}
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
