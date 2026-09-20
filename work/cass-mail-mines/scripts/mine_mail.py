#!/usr/bin/env python3
"""Mine EVERY mail row into structured features. Read-only; JSONL to stdout.

Falsifier first: docs/demos/upstream-repro/mail-mine-falsifier-20260920.md.
Shape of work/commit-mine/mine.mjs. NEVER emits body_md or subject text —
ids, counts, enum/boolean/shape features and project paths only.

Usage: python3 work/cass-mail-mines/scripts/mine_mail.py > /tmp/mail.jsonl
"""

from __future__ import annotations

import json
import sqlite3
import sys

MAIL = "/Users/josh/.local/share/mcp-agent-mail-rust-live/storage.sqlite3"
WIN = (
    24 * 3600
)  # mail created_ts is MICROseconds; reservations created_ts? normalized below


def main() -> int:
    mail = sqlite3.connect(f"file://{MAIL}?mode=ro", uri=True)
    bead_ids = set()
    try:
        with open(".beads/issues.jsonl") as fh:
            for line in fh:
                line = line.strip()
                if line.startswith("{"):
                    bead_ids.add(json.loads(line).get("id"))
    except OSError:
        pass
    projects = {
        pid: (slug, hk)
        for pid, slug, hk in mail.execute("select id, slug, human_key from projects")
    }
    res = [
        (pid, ts)
        for pid, ts in mail.execute(
            "select project_id, created_ts from file_reservations"
        )
    ]

    # reservation ts unit: normalize by magnitude (s vs ms vs us)
    def tonorm(ts):
        if ts is None:
            return None
        v = float(ts)
        if v > 1e14:
            return v / 1e6
        if v > 1e11:
            return v / 1e3
        return v

    res_by_proj: dict[int, list] = {}
    for pid, ts in res:
        t = tonorm(ts)
        if t:
            res_by_proj.setdefault(pid, []).append(t)
    for r in res_by_proj.values():
        r.sort()
    out_n = 0
    for mid, pid, sid, tid, imp, ack_req, cts, recips, atts, body in mail.execute(
        "select id, project_id, sender_id, thread_id, importance, "
        "ack_required, created_ts, recipients_json, attachments, "
        "length(body_md) from messages"
    ):
        mts = tonorm(cts)
        rec = mail.execute(
            "select count(*), sum(ack_ts is not null) from message_recipients "
            "where message_id=?",
            (mid,),
        ).fetchone()
        acked = (rec[1] or 0) > 0
        linked_res = 0
        if mts and pid in res_by_proj:
            linked_res = sum(1 for t in res_by_proj[pid] if abs(t - mts) <= WIN)
        slug, hk = projects.get(pid, (None, None))
        print(
            json.dumps(
                {
                    "id": mid,
                    "project_id": pid,
                    "project_slug": slug,
                    "project_path": hk,
                    "sender_id": sid,
                    "thread_id": tid,
                    "importance": imp,
                    "ack_required": bool(ack_req),
                    "acked": acked,
                    "n_recipients": rec[0],
                    "body_len": body,
                    "has_attachments": atts not in (None, "", "[]", "null"),
                    "created_ts": cts,
                    "res_linked_24h": linked_res,
                    "bead_linked": tid in bead_ids,
                }
            )
        )
        out_n += 1
    print(f"mined {out_n} messages", file=sys.stderr)
    mail.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
