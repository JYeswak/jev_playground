#!/usr/bin/env python3
"""Mine ranked features from the frozen toolcall corpus.

Prints a lift table: P(GOOD|feature) / P(GOOD), plus n / GOOD counts.
Offline. No invented rows. No TYPESAFE / CASS.

    python3 work/jev-real-corpus-eval/mine_features.py \
      work/p3-calibration/toolcall-corpus-frozen.jsonl
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

from jev_real_corpus_eval import FROZEN_BAD, FROZEN_GOOD, FROZEN_N, FROZEN_SHA256, identity_lock, load_rows


def cmd_of(row: dict) -> str:
    raw = row.get("args") or ""
    try:
        a = json.loads(raw)
        return a.get("command") or a.get("code") or ""
    except Exception:
        return raw


def sess_repo(sess: str) -> str:
    if not sess:
        return ""
    if sess.startswith("-Developer-"):
        return "-Developer-" + sess[len("-Developer-") :].split("/")[0]
    if sess.startswith("--"):
        return sess.split("/")[0]
    return sess.split("/")[0]


def features_for(row: dict) -> dict[str, bool]:
    c = cmd_of(row)
    cl = c.lower()
    s = row.get("sess") or ""
    repo = sess_repo(s)
    alen = len(row.get("args") or "")
    out: dict[str, bool] = {
        "isError": row.get("isError") is True,
        "args_len_lt_100": alen < 100,
        "args_len_eq_200": alen == 200,
        "sess_repo_grokbot": repo == "-Developer-grokbot",
        "sess_repo_control_plane": repo == "-Developer-control-plane",
        "sess_repo_omp": repo == "-Developer-omp-orchestrator",
        "sess_repo_franken": repo.startswith("-Developer-franken"),
        "sess_repo_jev": repo == "-Developer-jev",
        "sess_repo_WWJD": repo == "-Developer-WWJD",
        "sess_repo_cfs_ios": "clutterfreespaces" in repo,
        "sess_repo_private_tmp": repo.startswith("--private"),
        "cmd_has_pipefail": "pipefail" in cl,
        "cmd_has_skills": "skills" in cl,
        "cmd_has_mcp": bool(re.search(r"\bmcp\b", cl)),
        "cmd_curl": bool(re.search(r"\bcurl\b", cl)),
        "cmd_find": bool(re.search(r"\bfind\b", cl)),
        "cmd_ls": bool(re.search(r"(^|[|&;]\s*)ls\b", c)),
        "cmd_git": bool(re.search(r"\bgit\b", cl)),
        "cmd_git_status": "git status" in cl,
        "cmd_git_diff": "git diff" in cl,
        "cmd_git_commit": "git commit" in cl,
        "cmd_cargo": bool(re.search(r"\bcargo\b", cl)),
        "cmd_ntm": bool(re.search(r"\bntm\b", cl)),
        "cmd_omp": bool(re.search(r"\bomp\b", cl)),
        "cmd_python": bool(re.search(r"\bpython3?\b", cl)),
        "cmd_echo": bool(re.search(r"\becho\b", cl)),
        "cmd_sed": bool(re.search(r"\bsed\b", cl)),
        "cmd_grep": bool(re.search(r"\bgrep\b", cl)),
        "cmd_jq": bool(re.search(r"\bjq\b", cl)),
        "cmd_gh": bool(re.search(r"\bgh\b", cl)),
        "cmd_cp": bool(re.search(r"\bcp\b", cl)),
        "cmd_rm": bool(re.search(r"\brm\b", cl)),
        "cmd_ssh": bool(re.search(r"\bssh\b", cl)),
        "has_and": "&&" in c,
        "has_or": "||" in c,
        "has_pipe": "|" in c,
        "has_dollar": "$" in c,
        "has_Users": "/Users/" in c,
        "has_tmp": "/tmp" in c,
        "has_heredoc": "<<" in c,
        "has_secretish": bool(re.search(r"(api[_-]?key|token|password|secret|Bearer)", c, re.I)),
        "cmd_short_lt80": len(c) < 80,
        "cmd_long_ge150": len(c) >= 150,
    }
    # exact high-volume sessions (n is locked by frozen file; names are real)
    out["sess_exact_grokbot_0911"] = s.startswith(
        "-Developer-grokbot/2026-09-11T22-19-20-324Z_"
    )
    out["sess_exact_omp_0802"] = s.startswith(
        "-Developer-omp-orchestrator/2026-08-31T06-02-27-553Z_"
    )
    out["sess_exact_omp_0827"] = s.startswith(
        "-Developer-omp-orchestrator/2026-08-31T06-27-13-742Z_"
    )
    return out


def main(argv: list[str]) -> int:
    path = Path(argv[0] if argv else "work/p3-calibration/toolcall-corpus-frozen.jsonl")
    rows = load_rows(path)
    identity_lock(path, rows)
    n = len(rows)
    good = sum(1 for r in rows if r["outcome"] == "GOOD")
    p0 = good / n

    # tool / kind / isError census
    tools = Counter(r["tool"] for r in rows)
    kinds = Counter(r["kind"] for r in rows)
    print(f"n={n} GOOD={good} BAD={n - good} P(GOOD)={p0:.9f}")
    print(f"tools={dict(tools)}")
    print(f"kinds={dict(kinds)}")
    print(
        "isError×outcome: "
        + ", ".join(
            f"({ie},{out})={sum(1 for r in rows if (r['isError'] is ie) and r['outcome']==out)}"
            for ie in (True, False)
            for out in ("GOOD", "BAD")
        )
    )
    print()
    print(
        f"{'feature':32} {'n':>6} {'GOOD':>5} {'P(G|f)':>8} {'lift':>6} {'recall':>7}  note"
    )
    print("-" * 90)

    # aggregate feature fires
    cached = [features_for(r) for r in rows]
    names = list(cached[0].keys())
    scored = []
    for name in names:
        hit_idx = [i for i, f in enumerate(cached) if f[name]]
        c = len(hit_idx)
        if c == 0:
            continue
        g = sum(1 for i in hit_idx if rows[i]["outcome"] == "GOOD")
        pg = g / c
        lift = pg / p0
        recall = g / good
        note = ""
        if pg > 2 / 3 and c >= 15:
            note = "ALLOW-ELIGIBLE (P>2/3)"
        elif name == "isError" and g == 0 and c > 0:
            note = "perfect BAD precision; rare"
        scored.append((lift, pg, c, g, recall, name, note))

    scored.sort(key=lambda x: (-x[0], -x[2]))
    for lift, pg, c, g, recall, name, note in scored:
        print(f"{name:32} {c:6d} {g:5d} {pg:8.4f} {lift:6.3f} {recall:7.3f}  {note}")

    # sess-repo rates
    print()
    print("sess_repo rates (n>=40):")
    repo_c: Counter[str] = Counter()
    repo_g: Counter[str] = Counter()
    for r in rows:
        repo = sess_repo(r.get("sess") or "")
        repo_c[repo] += 1
        if r["outcome"] == "GOOD":
            repo_g[repo] += 1
    for repo, c in sorted(repo_c.items(), key=lambda kv: -repo_g[kv[0]] / kv[1]):
        if c < 40:
            continue
        pg = repo_g[repo] / c
        print(f"  lift={pg / p0:6.3f} P={pg:.4f} n={c:4d} GOOD={repo_g[repo]:4d}  {repo}")

    print()
    print(
        "ALLOW math: vs always-abstain, allowing saves 1 on GOOD and costs 2 on BAD; "
        "need P(GOOD|allow) > 2/3 to reduce mean loss."
    )
    print(f"FROZEN lock ok sha256={FROZEN_SHA256} n={FROZEN_N} GOOD={FROZEN_GOOD} BAD={FROZEN_BAD}")
    return 0


if __name__ == "__main__":
    # allow running as script from repo root with sibling import
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    raise SystemExit(main(sys.argv[1:]))
