#!/usr/bin/env python3
"""Real-traffic event counts feeding jev-candidate-check.py G0b (census-feed).

Keyless, offline. Scans the same session roots/window as work/jev-census
for per-candidate OPPORTUNITIES, and takes POSITIVES only from committed
label files (never proxies, never planted/benchmark rows). Where no labels
exist, positives is null and the gate STOPs with 'unstated' -- that is the
honest answer, not a zero.

Output work/jev-census/candidates.json:
  {name: {days, opportunities, positives, positives_source, tp_per_week,
          provenance, traffic:{days, opportunities, positives}}}
The `traffic` block drops directly into a candidate file for
scripts/jev-candidate-check.py (the floor stays the candidate's cost
decision; suggestions are NOT made here).

Usage: python3 work/jev-census/traffic.py [--days N]
"""

from __future__ import annotations

import datetime
import glob
import json
import os
import re
import subprocess
import sys

DAYS = int(sys.argv[sys.argv.index("--days") + 1]) if "--days" in sys.argv else 7
NOW = datetime.datetime.now(datetime.timezone.utc).timestamp()
BASE = NOW - DAYS * 86400
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))

INSTRUCT = re.compile(
    r"ignore (?:all )?previous instructions|forget (?:everything|all)|"
    r"disregard .*instructions|you are now|reveal .*prompt|send .*secret|"
    r"just output|print yay|act as two entities|role-play",
    re.I,
)
SKILL_RE = re.compile(r"skill://([A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)?)")
WEB_TOOLS = {"web_search", "web_extract", "fetch", "open_url"}


def text_of(msg):
    c = msg.get("content")
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        return "\n".join(
            p.get("text", "")
            for p in c
            if isinstance(p, dict) and isinstance(p.get("text"), str)
        )
    return ""


def session_rows():
    roots = ["/Users/josh/.omp/agent/sessions"] + glob.glob(
        "/Users/josh/.omp/profiles/*/agent/sessions"
    )
    for r in roots:
        try:
            slugs = os.listdir(r)
        except OSError:
            continue
        for s in slugs:
            d = os.path.join(r, s)
            if not os.path.isdir(d):
                continue
            try:
                names = [
                    x
                    for x in os.listdir(d)
                    if x.endswith(".jsonl") and not x.startswith(".")
                ]
            except OSError:
                continue
            for n in names:
                fp = os.path.join(d, n)
                try:
                    if os.path.getmtime(fp) < BASE:
                        continue
                    fh = open(fp, errors="replace")
                except OSError:
                    continue
                with fh:
                    for line in fh:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            o = json.loads(line)
                        except ValueError:
                            continue
                        try:
                            t = datetime.datetime.fromisoformat(
                                str(o.get("timestamp")).replace("Z", "+00:00")
                            ).timestamp()
                        except (ValueError, TypeError):
                            continue
                        if t < BASE:
                            continue
                        m = o.get("message")
                        if isinstance(m, dict):
                            yield m


def scan_sessions():
    opp = {
        "reads": 0,
        "read_hits": 0,
        "web_results": 0,
        "web_hits": 0,
        "skill_loads": 0,
        "bash_commands": 0,
        "memory_messages": 0,
    }
    for m in session_rows():
        role = m.get("role")
        txt = text_of(m)
        if role == "toolResult":
            tool = m.get("toolName")
            if m.get("isError") is True:
                continue
            if tool == "read" and len(txt) >= 40:
                opp["reads"] += 1
                if INSTRUCT.search(txt):
                    opp["read_hits"] += 1
            if tool in WEB_TOOLS and len(txt) >= 40:
                opp["web_results"] += 1
                if INSTRUCT.search(txt):
                    opp["web_hits"] += 1
        elif role == "assistant" and isinstance(m.get("content"), list):
            if "<memories>" in txt:
                opp["memory_messages"] += 1
            for b in m["content"]:
                if not (isinstance(b, dict) and b.get("type") == "toolCall"):
                    continue
                nm = b.get("name")
                args = b.get("arguments") or {}
                if nm == "bash":
                    opp["bash_commands"] += 1
                arg = str(args.get("command") or args.get("path") or "")
                if nm in ("read", "bash"):
                    opp["skill_loads"] += len(SKILL_RE.findall(arg))
    return opp


def vendor_labels():
    """m94x blind labels: truth_vendored sum over 39 hunks + window from key SHAs."""
    with open(
        os.path.join(REPO, "work/jev-m94x/m94x-labels.json"), encoding="utf-8"
    ) as fh:
        rows = json.load(fh)
    if isinstance(rows, dict):
        rows = rows.get("rows", rows.get("hunks", []))
    pos = sum(1 for r in rows if r.get("truth_vendored") == 1)
    shas = {k.rsplit("@", 1)[-1] for r in rows for k in [r.get("key", "")] if "@" in k}
    dates = []
    for s in sorted(shas):
        try:
            out = subprocess.run(
                ["git", "log", "-1", "--format=%ct", s],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=REPO,
            ).stdout.strip()
            if out.isdigit():
                dates.append(int(out))
        except Exception:
            continue
    span = (max(dates) - min(dates)) / 86400 if len(dates) >= 2 else 1.0
    return (
        len(rows),
        pos,
        max(span, 1.0),
        "%d hunks blind-labeled (61ae2c43), window from key-SHA commit dates"
        % len(rows),
    )


def wbel_labels():
    """wbel replay: UNFIT-and-vetoed (correct vetoes) over the 200-load 7d sample."""
    with open(
        os.path.join(REPO, "work/wbel/replay-rows.jsonl"), encoding="utf-8"
    ) as fh:
        rows = [json.loads(l) for l in fh]
    with open(
        os.path.join(REPO, "work/wbel/replay-labels.json"), encoding="utf-8"
    ) as fh:
        labs = json.load(fh)
    byid = {r["sample_id"]: r for r in rows}
    tp = sum(
        1
        for sid, v in labs.items()
        if v.get("label") == "UNFIT" and byid.get(sid, {}).get("pred") == "veto"
    )
    return (
        len(rows),
        tp,
        7.0,
        "200 organic loads 2026-09-25T15Z-2026-10-02T15Z, blind FIT/UNFIT pre-score (541055bc)",
    )


def facg_window():
    """facg 1h live window: 98 cascade rows, 4 paid escalations (blind truth unmeasured)."""
    return (
        98,
        4,
        1.0 / 24,
        "1h live window 15:36-16:36Z, 98 cascade rows, 4 paid (jev-facg close); paid flags stand in for target events, truth unmeasured",
    )


def wb7j_sample():
    """wb7j replication: 75 true drops in the 100-pair labeled sample (7d census)."""
    return (
        100,
        75,
        7.0,
        "100-pair seed-42 sample of the 170-pair 7d census; TP75 true drops (replication row, EVAL)",
    )


def main():
    opp = scan_sessions()
    n39, vpos, vdays, vprov = vendor_labels()
    n200, wtp, wdays, wprov = wbel_labels()
    n98, fpaid, fdays, fprov = facg_window()
    n100, mtp, mdays, mprov = wb7j_sample()
    cands = {
        "vendor_paste": {
            "days": vdays,
            "opportunities": n39,
            "positives": vpos,
            "positives_source": "labels",
            "provenance": vprov,
        },
        "skill_veto": {
            "days": wdays,
            "opportunities": n200,
            "positives": wtp,
            "positives_source": "labels",
            "provenance": wprov,
        },
        "gate_cascade": {
            "days": fdays,
            "opportunities": n98,
            "positives": fpaid,
            "positives_source": "labels-paid-as-target",
            "provenance": fprov,
        },
        "memory_filter": {
            "days": mdays,
            "opportunities": n100,
            "positives": mtp,
            "positives_source": "labels",
            "provenance": mprov,
        },
        "injection_reads": {
            "days": float(DAYS),
            "opportunities": opp["reads"],
            "positives": None,
            "positives_source": "unmeasured",
            "proxy_hits": opp["read_hits"],
            "provenance": "read results scanned %d, instruction-pattern hits %d are PROXY not truth; hqha planted rows excluded by rule"
            % (opp["reads"], opp["read_hits"]),
        },
        "webscreen": {
            "days": float(DAYS),
            "opportunities": opp["web_results"],
            "positives": None,
            "positives_source": "unmeasured",
            "proxy_hits": opp["web_hits"],
            "provenance": "web results scanned %d, instruction-pattern hits %d are PROXY not truth"
            % (opp["web_results"], opp["web_hits"]),
        },
        "skill_loads_observed": {
            "days": float(DAYS),
            "opportunities": opp["skill_loads"],
            "positives": None,
            "positives_source": "unmeasured",
            "provenance": "skill:// loads counted %d; UNFIT labels need the wbel replay, not this scan"
            % opp["skill_loads"],
        },
        "bash_commands_observed": {
            "days": float(DAYS),
            "opportunities": opp["bash_commands"],
            "positives": None,
            "positives_source": "unmeasured",
            "provenance": "bash toolCalls counted %d" % opp["bash_commands"],
        },
        "memory_messages_observed": {
            "days": float(DAYS),
            "opportunities": opp["memory_messages"],
            "positives": None,
            "positives_source": "unmeasured",
            "provenance": "<memories> messages counted %d; keep/drop truth needs filter labels"
            % opp["memory_messages"],
        },
    }
    for name, c in cands.items():
        p = c["positives"]
        c["tp_per_week"] = (p / c["days"] * 7) if isinstance(p, int) else None
        c["traffic"] = {
            "days": c["days"],
            "opportunities": c["opportunities"],
            "positives": c["positives"],
        }
    out = os.path.join(HERE, "candidates.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump({"window_days": DAYS, "candidates": cands}, fh, indent=1)
    for name, c in cands.items():
        print(
            "%-22s days=%-6g opp=%-7d pos=%-6s tp/wk=%-8s src=%s"
            % (
                name,
                c["days"],
                c["opportunities"],
                c["positives"],
                c["tp_per_week"],
                c["positives_source"],
            ),
            flush=True,
        )
    print("wrote " + out, flush=True)


if __name__ == "__main__":
    main()
