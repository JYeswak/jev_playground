#!/usr/bin/env python3
"""Representative-sample dig-vs-invent re-run. Read-only; no locked files touched.

Frozen design: docs/demos/upstream-repro/repsample-falsifier-20260920.md
(seed 421337, n=1000 conversations, same 138 queries / token rule / Y / loss).
Outputs: exports/cass-dig-rep1000-{rows,hits,score,meta}.txt (distinct names).
"""

from __future__ import annotations

import hashlib
import json
import random
import re
import sqlite3
import sys
from pathlib import Path

CASS = "/Volumes/ZestData/cass-data/agent_search.db"
SEED = 421337
N = 1000
LIMIT = 10
OUT = Path("work/cass-mail-mines/exports")
TOKEN_SPLIT = re.compile(r"\W+")


def main() -> int:
    sys.path.insert(0, "work/cass-mail-mines/scripts")
    from cass_dig_y import y_for_row, hit_receipt_shaped

    con = sqlite3.connect(f"file:{CASS}?mode=ro", uri=True)
    ids = [r[0] for r in con.execute("select id from conversations")]
    rng = random.Random(SEED)
    sample = sorted(rng.sample(ids, N))
    print(f"frame=conversations pool={len(ids)} n={len(sample)} seed={SEED}")
    print(
        "sample_sha="
        + hashlib.sha256(",".join(map(str, sample)).encode()).hexdigest()[:16]
    )
    ph = ",".join("?" * len(sample))
    docs = [
        (r[0], r[1], r[2] or "")
        for r in con.execute(
            f"select conversation_id, id, content from messages where conversation_id in ({ph})",
            sample,
        )
    ]
    print(f"loaded_messages={len(docs)}")
    con.close()
    queries = [
        l.rstrip("\n")
        for l in open("work/cass-mail-mines/scripts/cass_dig_queries.txt")
        if l.strip()
    ]
    rows_out = OUT / "cass-dig-rep1000-rows.jsonl"
    hits_out = OUT / "cass-dig-rep1000-hits.jsonl"
    n_hits = 0
    with open(rows_out, "w") as rf, open(hits_out, "w") as hf:
        for q in queries:
            toks = [t for t in TOKEN_SPLIT.split(q) if len(t) >= 3][:3] or ["jev"]
            hits = []
            for cid, mid, content in docs:
                low = content.lower()
                if all(t.lower() in low for t in toks):
                    hits.append(
                        {
                            "source_path": f"conversation:{cid}",
                            "line_number": 0,
                            "snippet": content[:800],
                            "score": 0,
                            "message_id": mid,
                        }
                    )
                if len(hits) >= LIMIT:
                    break
            for i, h in enumerate(hits):
                h["score"] = max(0, LIMIT - i)
            for h in hits:
                hh = dict(h)
                hh["query"] = q
                hf.write(json.dumps(hh, separators=(",", ":")) + "\n")
                n_hits += 1
            hc = len(hits)
            y = y_for_row(q, hits, hc)
            rf.write(
                json.dumps(
                    {
                        "query": q,
                        "hit_count": hc,
                        "y": y,
                        "status": "sqlite_sampled",
                        "top_path": hits[0]["source_path"] if hits else None,
                        "top_score": hits[0]["score"] if hits else None,
                        "n_receipt_shaped": sum(
                            1 for h in hits if hit_receipt_shaped(h)
                        ),
                    },
                    separators=(",", ":"),
                )
                + "\n"
            )
    print(f"n_rows={len(queries)} n_hits={n_hits}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
