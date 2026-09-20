#!/usr/bin/env python3
"""A11 mail->cass join yield (A11 card order). Read-only, no cass search.

Keys:
  K1 mail.projects.human_key <-> cass.workspaces.path (exact, rstrip '/' only)
  K2 mail.messages.thread_id <-> cass conversation external_id/title tokens
  K3 mail.file_reservations (project path + path_pattern) <-> cass file-level
     column (snippets.file_path; introspected n=0, so K3 reports 0 + reason)

Falsifier: docs/demos/upstream-repro/a11-join-falsifier-20260920.md (6b0d404).
Outcome words: DONE / HELD / REFUSE per that file. No body_md/subject text
leaves the DBs; stdout is ids/counts/paths only.
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import sys

MAIL = "/Users/josh/.local/share/mcp-agent-mail-rust-live/storage.sqlite3"
CASS = "/Volumes/ZestData/cass-data/agent_search.db"


def norm(p: str) -> str:
    return p.rstrip("/")


def sha(items: list[str]) -> str:
    return hashlib.sha256("\n".join(sorted(items)).encode()).hexdigest()[:16]


def main() -> int:
    mail = sqlite3.connect(f"file://{MAIL}?mode=ro", uri=True)
    cass = sqlite3.connect(CASS)  # SELECT-only below; no writes issued
    out: dict = {"store": "mail+cass", "keys": {}}

    projects = {
        pid: (slug, hk)
        for pid, slug, hk in mail.execute("select id, slug, human_key from projects")
    }
    mail_paths = {norm(hk): pid for pid, (_, hk) in projects.items() if hk}
    workspaces = {
        wid: path for wid, path in cass.execute("select id, path from workspaces")
    }
    cass_paths = {norm(p): wid for wid, p in workspaces.items() if p}
    out["denominator"] = {
        "mail_projects": len(projects),
        "mail_messages": mail.execute("select count(*) from messages").fetchone()[0],
        "mail_thread_nonnull": mail.execute(
            "select count(*) from messages where thread_id is not null"
        ).fetchone()[0],
        "mail_reservations": mail.execute(
            "select count(*) from file_reservations"
        ).fetchone()[0],
        "cass_workspaces": len(workspaces),
        "cass_conversations": cass.execute(
            "select count(*) from conversations"
        ).fetchone()[0],
        "cass_snippets": cass.execute("select count(*) from snippets").fetchone()[0],
    }
    out["identity_lock"] = {
        "mail_paths_sha": sha(list(mail_paths)),
        "cass_paths_sha": sha(list(cass_paths)),
    }

    # K1: exact project<->workspace join
    joined = sorted(set(mail_paths) & set(cass_paths))
    k1 = {"id_join_paths": len(joined), "pairs": []}
    for path in joined:
        pid = mail_paths[path]
        wid = cass_paths[path]
        n_msg = mail.execute(
            "select count(*) from messages where project_id=?", (pid,)
        ).fetchone()[0]
        n_conv = cass.execute(
            "select count(*) from conversations where workspace_id=?", (wid,)
        ).fetchone()[0]
        k1["pairs"].append(
            {
                "path": path,
                "mail_project_id": pid,
                "mail_messages": n_msg,
                "cass_workspace_id": wid,
                "cass_conversations": n_conv,
            }
        )
    # Plant checks on K1
    tmp_joined = [p for p in joined if p.startswith("/private/tmp/")]
    from os.path import basename

    base_collisions = sorted(
        {
            basename(p)
            for p in joined
            if sum(1 for q in joined if basename(q) == basename(p)) > 1
        }
    )
    k1["plant_P1_distinct_tmp_joined"] = tmp_joined
    k1["plant_P2_basename_collisions_joined"] = base_collisions
    # Co-present (same basename, different parent, on either side)
    mail_bases: dict[str, set[str]] = {}
    for p in mail_paths:
        mail_bases.setdefault(basename(p), set()).add(p)
    cass_bases: dict[str, set[str]] = {}
    for p in cass_paths:
        cass_bases.setdefault(basename(p), set()).add(p)
    shared_bases = sorted(set(mail_bases) & set(cass_bases))
    k1["shared_basename_co_present"] = [
        {
            "basename": b,
            "mail_paths": sorted(mail_bases[b]),
            "cass_paths": sorted(cass_bases[b]),
            "exact_joined": sorted(set(mail_bases[b]) & set(cass_bases[b])),
        }
        for b in shared_bases
    ]
    k1["miss_paths_mail_only"] = len(set(mail_paths) - set(cass_paths))
    k1["miss_paths_cass_only"] = len(set(cass_paths) - set(mail_paths))
    out["keys"]["K1"] = k1

    # K2: thread_id tokens in cass external_id/title
    tids = [
        r[0]
        for r in mail.execute(
            "select distinct thread_id from messages where thread_id is not null"
        )
    ]
    out["keys"]["K2"] = {"distinct_thread_ids": len(tids)}
    tid_set = set(tids)
    tok_re = re.compile(r"[A-Za-z0-9]+")
    hits: dict[str, int] = {}
    for ext, title in cass.execute("select external_id, title from conversations"):
        toks = set(tok_re.findall(f"{ext or ''} {title or ''}"))
        for t in toks & tid_set:
            hits[t] = hits.get(t, 0) + 1
    out["keys"]["K2"]["id_join_thread_ids"] = len(hits)
    out["keys"]["K2"]["hit_counts"] = dict(sorted(hits.items())[:50])
    out["keys"]["K2"]["miss_thread_ids"] = len(tids) - len(hits)

    # K3: no file-level cass column in sqlite (snippets n=0)
    n_snip = out["denominator"]["cass_snippets"]
    out["keys"]["K3"] = {
        "id_join": 0,
        "reason": f"snippets n={n_snip}; conversations.source_path "
        "is the session file, not the repo file; message content "
        "needs FTS (index-busy). UNMEASURED via sqlite.",
    }

    total_join = (len(joined) > 0) or (len(hits) > 0)
    cheap_covers_all = (
        len(hits) == 0
        and tmp_joined == []
        and base_collisions == []
        and len(joined) > 0
    )
    if not total_join:
        out["verdict"] = "REFUSE"
    elif tmp_joined or base_collisions:
        out["verdict"] = "HELD"
    elif cheap_covers_all:
        out["verdict"] = "HELD"
    else:
        out["verdict"] = "DONE"
    out["verdict_reason"] = {
        "REFUSE": "F2: zero id-join on all keys -> UNMEASURED",
        "HELD": "F3/F4: cheap exact-match covers all joins, or plant RED",
        "DONE": "yield printed per key with denominator",
    }[out["verdict"]]
    out["falsifier_sha"] = "6b0d404"
    print(json.dumps(out, indent=1))
    mail.close()
    cass.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
