#!/usr/bin/env python3
"""A18 off-bus ACK probe on precise K1 pair (mail proj 66 <-> cass ws 617).
Frozen in docs/demos/upstream-repro/a18-offbus-falsifier-20260920.md.
Read-only; prints ids/counts only, never message content.
Units: mail created_ts MICROseconds, cass started_at/ended_at MILLIseconds;
normalized to seconds against the frozen ±24h window.
"""

from __future__ import annotations

import json
import sqlite3
import sys

MAIL = "/Users/josh/.local/share/mcp-agent-mail-rust-live/storage.sqlite3"
CASS = "/Volumes/ZestData/cass-data/agent_search.db"
WIN = 24 * 3600
PROJ, WS = 66, 617


def main() -> int:
    mail = sqlite3.connect(f"file://{MAIL}?mode=ro", uri=True)
    cass = sqlite3.connect(CASS)  # SELECT-only below
    msgs = mail.execute(
        "select id, created_ts from messages where project_id=? "
        "and ack_required=1 and not exists (select 1 from message_recipients r "
        "where r.message_id=messages.id and r.ack_ts is not null)",
        (PROJ,),
    ).fetchall()
    convs = cass.execute(
        "select id, started_at, ended_at from conversations " "where workspace_id=?",
        (WS,),
    ).fetchall()
    # token-bearing conversations (timestamps kept raw-ms; content never
    # leaves the DB)
    tok_conv: dict[int, tuple] = {}
    for cid, started, ended in convs:
        hit = cass.execute(
            "select 1 from messages where conversation_id=? and "
            "(content like '%ACK%' collate nocase or content like '%reserv%' "
            "collate nocase) limit 1",
            (cid,),
        ).fetchone()
        if hit:
            tok_conv[cid] = (started, ended)
    out: dict = {
        "denominator": len(msgs),
        "cass_conversations_in_pair": len(convs),
        "token_conversations": len(tok_conv),
    }
    covered = cand = 0
    cand_ids: list[str] = []
    for mid, ts_us in msgs:
        ts = (ts_us or 0) / 1e6
        if not ts:
            continue
        t_lo, t_hi = (ts - WIN) * 1e3, (ts + WIN) * 1e3
        if cass.execute(
            "select 1 from conversations where workspace_id=? and "
            "started_at <= ? and (ended_at is null or ended_at >= ?) "
            "limit 1",
            (WS, t_hi, t_lo),
        ).fetchone():
            covered += 1
        inw = [
            c
            for c, (s, e) in tok_conv.items()
            if (s or 0) - WIN * 1e3 <= ts * 1e3 <= (e or s or 0) + WIN * 1e3
        ]
        if inw:
            cand += 1
            if len(cand_ids) < 5:
                cand_ids.append(str(mid))
    out["in_window_coverage"] = covered
    out["offbus_candidates"] = cand
    out["pi_candidate"] = round(cand / len(msgs), 9) if msgs else None
    out["sample_candidate_ids"] = cand_ids
    if covered == 0:
        out["verdict"] = "REFUSE"
        out["why"] = "F1: no in-window cass conversation for any of 287"
    elif cand / len(msgs) < 0.02:
        out["verdict"] = "HELD"
        out["why"] = "F2: candidate pi < 2%"
    else:
        out["verdict"] = "SAMPLE-READ"
        out["why"] = "candidates exist; top-5 sample read decides F3"
    print(json.dumps(out, indent=1))
    mail.close()
    cass.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
