#!/usr/bin/env python3
"""P2 keyless organic gate-demand census (jev-p2-gate-demand-qdtl).

Reads the native gate-observe log and recounts, keylessly and hash-only:
eligible denominator, label coverage from the frozen jev-uncd / jev-1lim
sets, same-event incumbent joins, missing outcomes, and source digests.

Rules (acceptance-enforced):
- No provider/Jev calls, no key, no network. Stdlib only.
- No command text is printed, stored, or hashed beyond the cmdSha the
  log already carries; rows-hash-only.jsonl carries hashes and ids only.
- A same-event join requires BOTH a source event id AND incumbent
  provenance (tool call id / deterministic action) on the row. cmdSha
  alone NEVER joins; such rows count as missing. (--selftest proves it.)
- Window digest is sha256 over the exact selected raw JSONL bytes,
  each line including its newline (the 1005/1010 method).

Usage:
  python3 work/gate-family/demand/census.py --days 7 --json
  python3 work/gate-family/demand/census.py --days 7 --json --selftest
"""

import argparse
import hashlib
import json
import os
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
SRC_LOG = os.path.expanduser("~/.local/state/jev/gate-observe.jsonl")
UNCD_ITEMS = os.path.join(REPO, "work/jev-uncd/items.jsonl")
LIM_MANIFEST = os.path.join(REPO, "work/jev-1lim/manifest.jsonl")
LIM_A = os.path.join(REPO, "work/jev-1lim/labels-A.jsonl")
LIM_B = os.path.join(REPO, "work/jev-1lim/labels-B.jsonl")
LIM_ADJ = os.path.join(REPO, "work/jev-1lim/adjudicated.jsonl")

OUT_DIR = os.path.join(REPO, "work/gate-family/demand")
ROWS_OUT = os.path.join(OUT_DIR, "rows-hash-only.jsonl")
RECEIPT_OUT = os.path.join(OUT_DIR, "receipt.json")

VERSION = "p2-census-v1"


def parse_ts(s):
    try:
        dt = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except (ValueError, TypeError, AttributeError):
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def is_harm(label):
    return isinstance(label, str) and label.startswith("harm")


def load_label_sets():
    """Return cmdSha -> {'uncd': label|None, 'limA': ..., 'limB': ...,
    'limFinal': ...}. Independent recount of the frozen sets."""
    by_id_A, by_id_B, by_id_F = {}, {}, {}
    with open(LIM_A, encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            if "id" in r:
                by_id_A[r["id"]] = r.get("label")
    with open(LIM_B, encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            if "id" in r:
                by_id_B[r["id"]] = r.get("label")
    with open(LIM_ADJ, encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            if "id" in r:
                by_id_F[r["id"]] = r.get("final_label")
    cmd_labels = {}
    with open(LIM_MANIFEST, encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            cmd = r.get("cmdSha")
            lid = r.get("id")
            if not cmd:
                continue
            cmd_labels[cmd] = {
                "limA": by_id_A.get(lid),
                "limB": by_id_B.get(lid),
                "limFinal": by_id_F.get(lid),
            }
    with open(UNCD_ITEMS, encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            cmd = r.get("id")
            if not cmd:
                continue
            cmd_labels.setdefault(cmd, {}).update(
                {"uncd": r.get("label")})
    return cmd_labels


def try_join(row):
    """Same-event incumbent join. Returns (joined: bool, outcome|None).

    Joins ONLY when the row carries a source event id AND incumbent
    provenance (tool call id or deterministic action). cmdSha alone
    never joins.
    """
    event_id = row.get("event_id") or row.get("eventId")
    tool_call = row.get("tool_call_id") or row.get("toolCallId")
    action = row.get("dcg_action") or row.get("dcgAction")
    if event_id and (tool_call or action):
        return True, {
            "event_id": str(event_id),
            "tool_call_id": str(tool_call) if tool_call else None,
            "dcg_action": str(action) if action else None,
        }
    return False, None


def run_census(days, emit=True):
    with open(SRC_LOG, "rb") as f:
        raw_lines = f.read().splitlines(keepends=True)
    full_sha = hashlib.sha256(b"".join(raw_lines)).hexdigest()

    parsed = []
    for raw in raw_lines:
        try:
            r = json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        ts = parse_ts(r.get("ts"))
        if ts is None:
            continue
        parsed.append((ts, raw, r))
    if not parsed:
        raise SystemExit("no parseable rows with ts in source log")
    max_ts = max(t for t, _, _ in parsed)
    cutoff = max_ts - timedelta(days=days)
    window = [(t, raw, r) for (t, raw, r) in parsed if t >= cutoff]
    window.sort(key=lambda x: (x[0].isoformat(), str(x[2].get("cmdSha"))))
    window_sha = hashlib.sha256(b"".join(raw for _, raw, _ in window)).hexdigest()

    label_sets = load_label_sets()
    status_breakdown = Counter()
    eligible = 0
    covered = 0
    harm = 0
    undecidable = 0
    joins = 0
    missing = 0
    label_dist = Counter()
    covered_by_set = Counter()
    hash_rows = []

    for t, raw, r in window:
        status_breakdown[str(r.get("status"))] += 1
        if r.get("status") != "scored":
            continue
        eligible += 1
        cmd = r.get("cmdSha")
        labs = label_sets.get(cmd, {}) if cmd else {}
        flat = [(k, v) for k, v in labs.items() if v is not None]
        if flat:
            covered += 1
            for k, v in flat:
                label_dist[str(v)] += 1
                covered_by_set[k] += 1
            if any(is_harm(v) for _, v in flat):
                harm += 1
            elif any(str(v) == "undecidable" for _, v in flat):
                undecidable += 1
        joined, outcome = try_join(r)
        if joined:
            joins += 1
        else:
            missing += 1
        hash_rows.append({
            "ts": t.isoformat(),
            "cmdSha": cmd,
            "status": r.get("status"),
            "flag": r.get("flag"),
            "session": r.get("session"),
            "labels": {k: v for k, v in labs.items()} or None,
            "joined": joined,
            "outcome": outcome,
        })

    result = {
        "census": VERSION,
        "window": {
            "days": days,
            "cutoff": cutoff.isoformat(),
            "max_ts": max_ts.isoformat(),
            "rows": len(window),
        },
        "source_hashes": {
            "gate_observe_full_sha256": full_sha,
            "gate_observe_full_lines": len(raw_lines),
            "window_rows_sha256": window_sha,
            "uncd_items": "work/jev-uncd/items.jsonl",
            "lim_manifest": "work/jev-1lim/manifest.jsonl",
        },
        "status_breakdown": dict(status_breakdown),
        "eligible_denominator": eligible,
        "labels_recounted": {
            "covered_rows": covered,
            "covered_by_set": dict(covered_by_set),
            "assignments_by_label": dict(label_dist),
            "harm_rows": harm,
            "undecidable_rows": undecidable,
            "note": "assignments count label entries across sets, so "
                    "they sum above covered_rows; coverage is partial",
        },
        "prevalence": {
            "harm": harm,
            "of_covered_rows": covered,
            "note": "counts, not a rate; coverage is partial, not a "
                    "population estimate",
        },
        "same_event_joins": joins,
        "missing_outcomes": missing,
    }

    if emit:
        os.makedirs(OUT_DIR, exist_ok=True)
        with open(ROWS_OUT, "w", encoding="utf-8") as f:
            for h in hash_rows:
                f.write(json.dumps(h, sort_keys=True) + "\n")
        with open(RECEIPT_OUT, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, sort_keys=True)
            f.write("\n")
    return result


def selftest():
    # Planted negative: cmdSha alone (real schema shape) must NOT join.
    neg = {"cmdSha": "ab" * 32, "status": "scored",
           "session": "s", "ts": "2026-10-01T00:00:00Z"}
    joined, _ = try_join(neg)
    if joined:
        raise SystemExit("PLANTED NEGATIVE FAILED: cmdSha-only joined")
    # Positive control: event id + provenance joins.
    pos = dict(neg, event_id="e1", tool_call_id="call_1")
    joined, outcome = try_join(pos)
    if not (joined and outcome is not None
            and outcome["event_id"] == "e1"):
        raise SystemExit(
            "POSITIVE CONTROL FAILED: full-provenance row did not join")
    # Event id alone still misses.
    half = dict(neg, event_id="e1")
    joined, _ = try_join(half)
    if joined:
        raise SystemExit("HALF-PROVENANCE ROW JOINED")
    # Real-schema audit: current log union has no join fields at all.
    with open(SRC_LOG, encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= 2000:
                break
            try:
                r = json.loads(line)
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            if ("event_id" in r or "eventId" in r
                    or "tool_call_id" in r or "toolCallId" in r
                    or "dcg_action" in r or "dcgAction" in r):
                raise SystemExit("UNEXPECTED JOIN FIELD IN LOG SCHEMA")
    print("SELFTEST PASS: cmdSha-alone misses, full provenance joins, "
          "schema carries no join fields")
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest and not selftest():
        return 1
    result = run_census(args.days)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("eligible=%d covered=%d harm=%d joins=%d missing=%d" % (
            result["eligible_denominator"],
            result["labels_recounted"]["covered_rows"],
            result["labels_recounted"]["harm_rows"],
            result["same_event_joins"],
            result["missing_outcomes"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
