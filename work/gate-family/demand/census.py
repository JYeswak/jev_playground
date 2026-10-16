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
  python3 work/gate-family/demand/census.py --days 7 --as-of 2026-10-13T16:00:00Z --json
  python3 work/gate-family/demand/census.py --days 7 --json --selftest
"""

import argparse
import glob
import hashlib
import json
import os
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
STATE_DIR = os.path.expanduser("~/.local/state/jev")
SRC_LOG = os.path.join(STATE_DIR, "gate-observe.jsonl")
UNCD_ITEMS = os.path.join(REPO, "work/jev-uncd/items.jsonl")
LIM_MANIFEST = os.path.join(REPO, "work/jev-1lim/manifest.jsonl")
LIM_A = os.path.join(REPO, "work/jev-1lim/labels-A.jsonl")
LIM_B = os.path.join(REPO, "work/jev-1lim/labels-B.jsonl")
LIM_ADJ = os.path.join(REPO, "work/jev-1lim/adjudicated.jsonl")

OUT_DIR = os.path.join(REPO, "work/gate-family/demand")
ROWS_OUT = os.path.join(OUT_DIR, "rows-hash-only.jsonl")
RECEIPT_OUT = os.path.join(OUT_DIR, "receipt.json")

VERSION = "p2-census-v2"


def parse_ts(s):
    try:
        dt = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except (ValueError, TypeError, AttributeError):
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def discover_sources():
    archives = sorted(glob.glob(os.path.join(STATE_DIR, "gate-observe.jsonl.*.archive")))
    paths = archives + [SRC_LOG]
    missing = [p for p in paths if not os.path.isfile(p)]
    if missing:
        raise SystemExit("missing census source files: " + ", ".join(missing))
    return paths


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


def _raw_ts(raw):
    try:
        return parse_ts(json.loads(raw.decode("utf-8")).get("ts"))
    except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
        return None

def run_census(days, emit=True, asof=None):
    sources = discover_sources()
    contents = []
    for path in sources:
        with open(path, "rb") as f:
            contents.append(f.read().splitlines(keepends=True))
    raw_lines = [raw for content in contents for raw in content]
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
        raise SystemExit("no parseable rows with ts in source logs")
    max_ts = max(t for t, _, _ in parsed)
    anchor = asof if asof is not None else max_ts
    cutoff = anchor - timedelta(days=days)
    window = [(t, raw, r) for (t, raw, r) in parsed if cutoff <= t <= anchor]
    window_sha = hashlib.sha256(b"".join(raw for _, raw, _ in window)).hexdigest()
    actual_start = min(t for t, _, _ in window).isoformat() if window else None
    start_gap_s = (min(t for t, _, _ in window) - cutoff).total_seconds() if window else None
    covers_span = bool(window) and start_gap_s is not None and start_gap_s <= 300
    span_hours = round((anchor - min(t for t, _, _ in window)).total_seconds() / 3600, 1) if window else 0.0
    file_records = []
    for path, content in zip(sources, contents):
        kept = []
        for raw in content:
            ts = _raw_ts(raw)
            if ts is not None and ts <= anchor:
                kept.append(raw)
        file_records.append({
            "path": os.path.basename(path),
            "lines": len(content),
            "kept_lines": len(kept),
            "kept_sha256": hashlib.sha256(b"".join(kept)).hexdigest(),
        })

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
            "anchor": anchor.isoformat(),
            "file_max_ts": max_ts.isoformat(),
            "actual_start": actual_start,
            "actual_span_hours": span_hours,
            "rows": len(window),
            "covers_requested_span": covers_span,
            "span_note": "window fully covers the requested span" if covers_span else f"source holds {span_hours}h; a trailing-{days}d window covers the file, not {days} days of demand",
        },
        "source_hashes": {
            "source_files": file_records,
            "concatenated_sha256": full_sha,
            "concatenated_lines": len(raw_lines),
            "window_rows_sha256": window_sha,
            "window_row_order": "file order across epoch-ordered archives plus live log",
            "uncd_items": "work/jev-uncd/items.jsonl",
            "lim_manifest": "work/jev-1lim/manifest.jsonl",
            "source_note": "scored logs: rotated gate-observe.jsonl archives in epoch order plus the live tail; gate-observe-full.jsonl carries no outcomes and is not a source",
            "historic_9bae04e5": "reproduced 2026-10-13 from archive 1 (2750 rows, file order): sha256 9bae04e5fc6a2e81d5ee9982f0be0657b88d119cef92d7a00b7d89efc055b12a",
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
    ap.add_argument("--as-of", default=None,
                    help="pin window end to this ISO timestamp; default: file max ts")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest and not selftest():
        return 1
    asof = parse_ts(args.as_of) if args.as_of else None
    if args.as_of and asof is None:
        print("unparseable --as-of timestamp", file=sys.stderr)
        return 2
    result = run_census(args.days, asof=asof)
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
