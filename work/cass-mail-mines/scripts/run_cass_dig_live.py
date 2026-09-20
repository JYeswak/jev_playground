#!/usr/bin/env python3
"""Studio live: cass dig-vs-invent export + score.

Do NOT start a cass rebuild. Prefer `cass search --robot` with per-query
timeout (default 60s). After 3 timeouts (or missing cass), fall back to
read-only sqlite sample from agent_search.db (schema introspected first).

    python3 work/cass-mail-mines/scripts/run_cass_dig_live.py
    # optional:
    CASS_DB=/Volumes/ZestData/cass-data/agent_search.db \\
    CASS_TIMEOUT_SEC=60 CASS_LIMIT=10 \\
      python3 work/cass-mail-mines/scripts/run_cass_dig_live.py
"""
from __future__ import annotations

import json
import os
import re
import sqlite3
import subprocess
import sys
import time
from pathlib import Path
from shutil import which

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
from cass_dig_y import hit_receipt_shaped, y_for_row  # noqa: E402

OUT = ROOT / "work/cass-mail-mines/exports"
QUERIES = SCRIPTS / "cass_dig_queries.txt"
ROWS = OUT / "cass-dig-rows.jsonl"
HITS = OUT / "cass-dig-hits.jsonl"
META = OUT / "cass-dig-run-meta.txt"
SCORE = OUT / "cass-dig-score.txt"

DB = os.environ.get("CASS_DB", "/Volumes/ZestData/cass-data/agent_search.db")
TIMEOUT = int(os.environ.get("CASS_TIMEOUT_SEC", "60"))
LIMIT = int(os.environ.get("CASS_LIMIT", "10"))
MAX_QUERIES = int(os.environ.get("CASS_MAX_QUERIES", "0"))  # 0 = all


def log(meta: list[str], msg: str) -> None:
    print(msg, flush=True)
    meta.append(msg)


def parse_robot(stdout: str) -> dict:
    stdout = (stdout or "").strip()
    if not stdout:
        return {"count": 0, "hits": []}
    try:
        obj = json.loads(stdout)
        if isinstance(obj, dict):
            hits = obj.get("hits") or obj.get("results") or obj.get("items") or []
            if not hits and isinstance(obj.get("data"), list):
                hits = obj["data"]
            return {"count": int(obj.get("count") or len(hits) or 0), "hits": hits}
        if isinstance(obj, list):
            return {"count": len(obj), "hits": obj}
    except json.JSONDecodeError:
        pass
    hits = []
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            hits.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    if hits:
        return {"count": len(hits), "hits": hits}
    return {"count": 0, "hits": [], "parse": "failed", "stdout_head": stdout[:300]}


def cass_search(q: str) -> tuple[dict | None, str]:
    if not which("cass"):
        return None, "no_cass"
    try:
        p = subprocess.run(
            ["cass", "search", q, "--robot", f"--limit={LIMIT}"],
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return None, "timeout"
    # also try --limit as separate argv if above fails oddly
    if p.returncode != 0:
        try:
            p = subprocess.run(
                ["cass", "search", q, "--robot", "--limit", str(LIMIT)],
                capture_output=True,
                text=True,
                timeout=TIMEOUT,
            )
        except subprocess.TimeoutExpired:
            return None, "timeout"
    if p.returncode != 0:
        return None, f"rc={p.returncode}:{(p.stderr or '')[:200]!r}"
    return parse_robot(p.stdout), "cass"


def sqlite_fallback(queries: list[str], meta: list[str]) -> list[tuple[str, dict]]:
    if not Path(DB).is_file():
        log(meta, f"FALLBACK_DB_MISSING {DB}")
        return [(q, {"count": 0, "hits": [], "status": "no_db"}) for q in queries]
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    tables = [r[0] for r in con.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY 1"
    )]
    log(meta, f"fallback_tables={tables}")
    schema = []
    text_table = text_col = path_col = line_col = score_col = None
    for t in tables:
        cols = [r[1] for r in con.execute(f"PRAGMA table_info({t})")]
        schema.append({t: cols})
        lower = {c.lower(): c for c in cols}
        if text_table:
            continue
        for name in ("snippet", "text", "content", "body", "message", "raw"):
            if name in lower:
                text_table, text_col = t, lower[name]
                break
        if not text_table:
            continue
        for name in ("source_path", "path", "file", "filepath"):
            if name in lower:
                path_col = lower[name]
                break
        for name in ("line_number", "line", "start_line"):
            if name in lower:
                line_col = lower[name]
                break
        for name in ("score", "rank", "bm25"):
            if name in lower:
                score_col = lower[name]
                break
    log(meta, f"fallback_pick table={text_table} text={text_col} path={path_col}")
    META_SCHEMA = OUT / "cass-dig-sqlite-schema.json"
    META_SCHEMA.write_text(json.dumps(schema, indent=2)[:50000])
    if not text_table:
        con.close()
        return [(q, {"count": 0, "hits": [], "status": "no_text_table"}) for q in queries]
    out = []
    for q in queries:
        tokens = [t for t in re.split(r"\W+", q) if len(t) >= 3][:3] or ["jev"]
        where = " AND ".join([f"{text_col} LIKE ?" for _ in tokens])
        params = [f"%{t}%" for t in tokens]
        sql = f"SELECT * FROM {text_table} WHERE {where} LIMIT {LIMIT}"
        try:
            got = list(con.execute(sql, params))
        except sqlite3.Error as e:
            log(meta, f"sql_err={e}")
            got = []
        hits = []
        for r in got:
            d = dict(r)
            hits.append({
                "source_path": (d.get(path_col) if path_col else d.get("source_path") or d.get("path") or ""),
                "line_number": (d.get(line_col) if line_col else d.get("line_number") or d.get("line") or 0),
                "snippet": str(d.get(text_col) or "")[:500],
                "score": (d.get(score_col) if score_col else d.get("score") or 0),
            })
        # cheap BM25-ish: keep order as returned; attach rank index as score if missing
        for i, h in enumerate(hits):
            if not h.get("score"):
                h["score"] = max(0, LIMIT - i)
        out.append((q, {"count": len(hits), "hits": hits, "status": "sqlite_fallback"}))
    con.close()
    return out


def write_outputs(results: list[tuple[str, dict]], mode: str, meta: list[str]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    n_hits = 0
    with ROWS.open("w") as rf, HITS.open("w") as hf:
        for q, parsed in results:
            hits = [h for h in (parsed.get("hits") or []) if isinstance(h, dict)]
            for h in hits:
                n_hits += 1
                hh = dict(h)
                hh["query"] = q
                hf.write(json.dumps(hh, separators=(",", ":")) + "\n")
            hc = int(parsed.get("count") or len(hits))
            y = y_for_row(q, hits, hc)
            row = {
                "query": q,
                "hit_count": hc,
                "y": y,
                "status": parsed.get("status"),
                "top_path": (hits[0].get("source_path") or hits[0].get("path")) if hits else None,
                "top_score": hits[0].get("score") if hits else None,
                "n_receipt_shaped": sum(1 for h in hits if hit_receipt_shaped(h)),
            }
            rf.write(json.dumps(row, separators=(",", ":")) + "\n")
    log(meta, f"mode={mode} n_rows={len(results)} n_hits={n_hits}")
    META.write_text("\n".join(meta) + "\n")


def score() -> str:
    from score_cass_dig import main as score_main
    # capture by re-invoking logic
    import io
    from contextlib import redirect_stdout
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = score_main([str(ROWS)])
    text = buf.getvalue()
    SCORE.write_text(text)
    print(text, end="")
    return text


def main() -> int:
    meta: list[str] = []
    log(meta, f"hostname_note=run_on_studio")
    log(meta, f"start_ts={time.time()}")
    log(meta, f"cass_bin={'yes' if which('cass') else 'no'}")
    log(meta, f"db_exists={Path(DB).is_file()} db={DB}")
    log(meta, f"timeout={TIMEOUT} limit={LIMIT}")
    queries = [
        ln.strip()
        for ln in QUERIES.read_text().splitlines()
        if ln.strip() and not ln.startswith("#")
    ]
    if MAX_QUERIES > 0:
        queries = queries[:MAX_QUERIES]
    log(meta, f'n_queries={len(queries)} max_queries={MAX_QUERIES or "all"}')
    if len(queries) < 2:
        print(f"REFUSE: only {len(queries)} queries", file=sys.stderr)
        return 2
    # n<100 ok when CASS_MAX_QUERIES set (timed subset)

    mode = "cass"
    results: list[tuple[str, dict]] = []
    timeouts = 0
    for i, q in enumerate(queries):
        parsed, status = cass_search(q)
        if status == "no_cass":
            mode = "sqlite_fallback"
            log(meta, "switch=sqlite_fallback reason=no_cass")
            break
        if status == "timeout":
            timeouts += 1
            log(meta, f"timeout_q={q!r}")
            results.append((q, {"count": 0, "hits": [], "status": "timeout"}))
            if timeouts >= 3:
                mode = "sqlite_fallback"
                log(meta, "switch=sqlite_fallback reason=timeouts>=3")
                break
            continue
        if parsed is None:
            results.append((q, {"count": 0, "hits": [], "status": status}))
            if i == 0 and status.startswith("rc="):
                # first query hard-failed — try fallback
                mode = "sqlite_fallback"
                log(meta, f"switch=sqlite_fallback reason={status}")
                break
            continue
        parsed["status"] = status
        results.append((q, parsed))
        if (i + 1) % 20 == 0:
            log(meta, f"progress={i+1}/{len(queries)}")

    if mode == "sqlite_fallback":
        results = sqlite_fallback(queries, meta)

    write_outputs(results, mode, meta)
    # update score_cass_dig import path by running as subprocess for cleanliness
    score_cmd = [sys.executable, str(SCRIPTS / "score_cass_dig.py")]
    if len(results) < 100:
        score_cmd.append("--allow-small")
    score_cmd.append(str(ROWS))
    p = subprocess.run(
        score_cmd,
        capture_output=True,
        text=True,
    )
    SCORE.write_text(p.stdout + (p.stderr or ""))
    print(p.stdout, end="")
    if p.returncode != 0:
        print(p.stderr, file=sys.stderr)
        return p.returncode
    log(meta, f"end_ts={time.time()}")
    META.write_text("\n".join(meta) + "\n")
    print(f"EXPORT {ROWS}")
    print(f"HITS {HITS}")
    print(f"SCORE {SCORE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
