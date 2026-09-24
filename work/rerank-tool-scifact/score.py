#!/usr/bin/env python3
"""Keyless scorer for bead jev-k9z.7: the shipped jev_rerank tool on BEIR SciFact.

  python3 work/rerank-tool-scifact/score.py                     # score committed rows
  python3 work/rerank-tool-scifact/score.py --selftest          # decision machinery, no rows
  python3 work/rerank-tool-scifact/score.py --check-receipt docs/demos/upstream-repro/rerank-tool-scifact-20260924.md

Stdlib only. The metric and test machinery is work/rerank-scifact/score.py (jev-nssg), imported,
not copied: ndcg10 and recall10 (binary gains, ideal DCG over every relevant doc), per_query for
BM25 order and the Noul arms, arm_nouls for the committed Noul rows, compare (paired bootstrap
95% percentile interval, 2,000 resamples, random.Random(20260924), WIN/LOSE/TIE).

Decision rule, verbatim from bead jev-k9z.7 and frozen in
docs/demos/upstream-repro/rerank-tool-scifact-prereg-20260924.md:
(a) tool vs BM25 order on each of 3 runs; (b) tool vs each committed Noul run (rows-jev,
rows-jev-run2, rows-jev-run3), 9 pairings. KEEP if (a) is WIN on all 3 and (b) is LOSE on none.
SWITCH if (a) is not WIN on all 3, or (b) is LOSE on all 9. Anything else is MIXED. A query the
tool cannot order after one resume pass is scored as the tool returns it (BM25 order,
ordered=false) and counted; more than 3 such queries in any run = that run NOT-SCORED.
"""

import importlib.util
import math
import os
import statistics
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
NOUL_DIR = os.path.join(os.path.dirname(HERE), "rerank-scifact")
_spec = importlib.util.spec_from_file_location(
    "noul_score", os.path.join(NOUL_DIR, "score.py")
)
ns = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ns)

TOOL_RUNS = ("tool", "tool-run2", "tool-run3")
NOUL_ARMS = ns.JEV_ARMS  # ("jev", "jev-run2", "jev-run3"), committed by jev-nssg
MAX_UNORDERED = 3
BEGIN, END = "<!-- rescore:begin -->", "<!-- rescore:end -->"


def tool_orders(cand_rows, rows, run):
    """{qid: (ordered doc ids, ordered flag)} from the latest attempt per query, plus accounting.

    Refuses a file that is not this unit's: a row for another run, an unknown qid, a ranking that
    is not a permutation of the shortlist, an attempt-2 row without a failed attempt 1, an
    ordered ranking whose scores are not finite in [0, 1] and non-increasing, or an unordered
    ranking that is not BM25 order.
    """
    cands = {r["qid"]: [d for d, _ in r["cands"]] for r in cand_rows}
    by_attempt = {1: {}, 2: {}}
    for row in rows:
        q, a = row["qid"], row["attempt"]
        if row["run"] != run or q not in cands or a not in (1, 2):
            raise SystemExit(
                f"{run}: row not from this run: qid={q} run={row['run']} attempt={a}"
            )
        if q in by_attempt[a]:
            raise SystemExit(f"{run}: two attempt-{a} rows for qid {q}")
        docs = [x["doc"] for x in row["ranking"]]
        if sorted(docs) != sorted(cands[q]) or len(docs) != len(cands[q]):
            raise SystemExit(
                f"{run}: qid {q} ranking is not a permutation of its shortlist"
            )
        if row["ordered"]:
            s = [x["score"] for x in row["ranking"]]
            if not all(
                isinstance(v, (int, float)) and math.isfinite(v) and 0 <= v <= 1
                for v in s
            ):
                raise SystemExit(f"{run}: qid {q} ordered with a score outside [0, 1]")
            if any(s[i] < s[i + 1] for i in range(len(s) - 1)):
                raise SystemExit(f"{run}: qid {q} ordered ranking is not by score")
        elif docs != cands[q]:
            raise SystemExit(f"{run}: qid {q} ordered=false but not BM25 order")
        by_attempt[a][q] = row
    for q, row in by_attempt[2].items():
        if q not in by_attempt[1] or by_attempt[1][q]["ordered"]:
            raise SystemExit(f"{run}: qid {q} has attempt 2 without a failed attempt 1")
    out = {}
    for q in cands:
        row = by_attempt[2].get(q) or by_attempt[1].get(q)
        if row is None:
            raise SystemExit(f"{run}: no row for qid {q}")
        out[q] = ([x["doc"] for x in row["ranking"]], row["ordered"])
    ends = [datetime.fromisoformat(r["ts"].replace("Z", "+00:00")) for r in rows]
    starts = [e.timestamp() - r["wallMs"] / 1000 for e, r in zip(ends, rows)]
    stats = {
        "unordered": sorted((q for q, (_, ok) in out.items() if not ok), key=int),
        "first_pass_unordered": sum(
            1 for r in by_attempt[1].values() if not r["ordered"]
        ),
        "resumed": len(by_attempt[2]),
        "calls": sum(r["calls"] for r in rows),
        "tin": sum(r["inputTokens"] for r in rows),
        "non200": sum(v for r in rows for k, v in r["status"].items() if k != "200"),
        "models": sorted({m for r in rows for m in r["models"]}),
        "reasons": sorted({r["reason"] for r in rows if r["reason"]}),
        "q_ms": [r["wallMs"] for r in rows],
        "window_s": (max(ends).timestamp() - min(starts)) if rows else 0.0,
        "window": (
            datetime.fromtimestamp(min(starts), timezone.utc).strftime("%H:%M:%S"),
            max(ends).strftime("%H:%M:%S"),
        )
        if rows
        else ("-", "-"),
    }
    return out, stats


def per_query_orders(cand_rows, orders):
    out = {m: [] for m in ns.METRICS}
    for r in cand_rows:
        ranked, _ = orders[r["qid"]]
        rel = set(r["rel"])
        out["ndcg10"].append(ns.ndcg10(ranked, rel))
        out["recall10"].append(ns.recall10(ranked, rel))
    return out


def decide(a_labels, b_labels):
    """The bead's rule. a_labels: 3 labels (WIN/LOSE/TIE/NOT-SCORED); b_labels: 9 labels."""
    a_all_win = len(a_labels) == 3 and all(x == "WIN" for x in a_labels)
    b_loses = sum(1 for x in b_labels if x == "LOSE")
    if a_all_win and b_loses == 0:
        return "KEEP"
    if not a_all_win or (len(b_labels) == 9 and b_loses == 9):
        return "SWITCH"
    return "MIXED"


def fmt(c):
    return f"{c['diff']:+.4f} [{c['lo']:+.4f}, {c['hi']:+.4f}] {c['label']:<4} {c['q'][0]}/{c['q'][1]}/{c['q'][2]}"


def score(cand_rows, tool_rows, noul_rows, out=print):
    bm25 = ns.per_query(cand_rows)
    noul = {}
    for arm in NOUL_ARMS:
        pmap, st = ns.arm_nouls(cand_rows, noul_rows[arm])
        if st["failed"]:
            raise SystemExit(f"Noul arm {arm} has {st['failed']} unanswered pairs")
        noul[arm] = ns.per_query(cand_rows, pmap)
    tool, stats, scored = {}, {}, {}
    for run in TOOL_RUNS:
        orders, stats[run] = tool_orders(cand_rows, tool_rows[run], run)
        tool[run] = per_query_orders(cand_rows, orders)
        scored[run] = len(stats[run]["unordered"]) <= MAX_UNORDERED

    out(f"queries={len(cand_rows)} candidates_sha256={ns.CANDIDATES_SHA256}")
    out("")
    out("arm            nDCG@10  Recall@10")
    out(
        f"BM25 order     {statistics.fmean(bm25['ndcg10']):.4f}   {statistics.fmean(bm25['recall10']):.4f}"
    )
    for arm in NOUL_ARMS:
        out(
            f"noul {arm:<10}{statistics.fmean(noul[arm]['ndcg10']):.4f}   {statistics.fmean(noul[arm]['recall10']):.4f}"
        )
    for run in TOOL_RUNS:
        out(
            f"{run:<15}{statistics.fmean(tool[run]['ndcg10']):.4f}   {statistics.fmean(tool[run]['recall10']):.4f}"
            + ("" if scored[run] else "   NOT-SCORED")
        )
    out("")
    out(
        "run        window(UTC)        span_s  http_calls  non200  input_tokens  q_ms p50/p95  first_pass_unordered  resumed  unordered_after_resume  models  reasons"
    )
    for run in TOOL_RUNS:
        s = stats[run]
        out(
            f"{run:<10} {s['window'][0]}-{s['window'][1]}  {s['window_s']:6.1f}  {s['calls']:>10}  {s['non200']:>6}  "
            f"{s['tin']:>12}  {ns.pctl(s['q_ms'], 0.5)}/{ns.pctl(s['q_ms'], 0.95)}  {s['first_pass_unordered']:>20}  "
            f"{s['resumed']:>7}  {len(s['unordered'])} [{','.join(s['unordered'])}]  {','.join(s['models']) or '-'}  "
            f"{','.join(s['reasons']) or '-'}"
        )

    a_labels, b_labels = [], []
    out("")
    out("(a) tool vs BM25 order: diff [95% interval] label queries better/worse/equal")
    for m in ns.METRICS:
        tag = "" if m == "ndcg10" else "  (reported, not in the rule)"
        out(f"  {m}{tag}")
        for run in TOOL_RUNS:
            if not scored[run]:
                out(f"    {run:<22} NOT-SCORED")
                if m == "ndcg10":
                    a_labels.append("NOT-SCORED")
                continue
            c = ns.compare(tool[run][m], bm25[m])
            out(f"    {run:<22} {fmt(c)}")
            if m == "ndcg10":
                a_labels.append(c["label"])
    out("")
    out("(b) tool vs Noul: diff [95% interval] label queries better/worse/equal")
    for m in ns.METRICS:
        tag = "" if m == "ndcg10" else "  (reported, not in the rule)"
        out(f"  {m}{tag}")
        for run in TOOL_RUNS:
            for arm in NOUL_ARMS:
                name = f"{run} vs {arm}"
                if not scored[run]:
                    out(f"    {name:<22} NOT-SCORED")
                    if m == "ndcg10":
                        b_labels.append("NOT-SCORED")
                    continue
                c = ns.compare(tool[run][m], noul[arm][m])
                out(f"    {name:<22} {fmt(c)}")
                if m == "ndcg10":
                    b_labels.append(c["label"])
    outcome = decide(a_labels, b_labels)
    out("")
    out(
        f"(a) nDCG@10 labels: {' '.join(a_labels)}  WIN on all 3: {'yes' if a_labels.count('WIN') == 3 else 'no'}"
    )
    out(f"(b) nDCG@10 labels: {' '.join(b_labels)}  LOSE {b_labels.count('LOSE')}/9")
    out(f"OUTCOME: {outcome}")
    return outcome


def load_all():
    cand = ns.load_candidates()
    noul_rows = {
        a: ns.load_jsonl(os.path.join(NOUL_DIR, f"rows-{a}.jsonl")) for a in NOUL_ARMS
    }
    tool_rows, missing = {}, []
    for run in TOOL_RUNS:
        path = os.path.join(HERE, f"rows-{run}.jsonl")
        if os.path.exists(path):
            tool_rows[run] = ns.load_jsonl(path)
        else:
            missing.append(run)
    return cand, tool_rows, noul_rows, missing


def selftest():
    """Planted tool rows over the real shortlists and committed Noul rows. No key, no tool rows."""
    cand = ns.load_candidates()
    noul_rows = {
        a: ns.load_jsonl(os.path.join(NOUL_DIR, f"rows-{a}.jsonl")) for a in NOUL_ARMS
    }
    rel = {r["qid"]: set(r["rel"]) for r in cand}
    bad = []

    def rows_for(run, key, unordered=()):
        rows = []
        for r in cand:
            ids = [d for d, _ in r["cands"]]
            if r["qid"] in unordered:
                ranking = [{"doc": d, "score": None} for d in ids]
                ok = False
            else:
                sc = {d: key(r["qid"], d) for d in ids}
                ranking = [
                    {"doc": d, "score": sc[d]}
                    for d in sorted(ids, key=lambda d: -sc[d])
                ]
                ok = True
            rows.append(
                {
                    "qid": r["qid"],
                    "run": run,
                    "attempt": 1,
                    "ordered": ok,
                    "reason": None if ok else "http",
                    "ranking": ranking,
                    "wallMs": 1,
                    "ts": "2026-09-24T00:00:00.000Z",
                    "calls": 20,
                    "status": {"200": 20},
                    "inputTokens": 0,
                    "models": ["jev-1.13.0"],
                }
            )
        return rows

    sink = lambda *_: None  # noqa: E731
    oracle = lambda q, d: float(d in rel[q])  # noqa: E731
    flat = lambda q, d: 0.5  # noqa: E731
    # oracle order: WIN vs BM25 on all 3; beats the Noul arms (ceiling), so KEEP
    got = score(cand, {r: rows_for(r, oracle) for r in TOOL_RUNS}, noul_rows, sink)
    if got != "KEEP":
        bad.append(f"oracle tool arms decide {got}, want KEEP")
    # constant scores reproduce BM25 order exactly: TIE vs BM25, so SWITCH
    orders, _ = tool_orders(cand, rows_for("tool", flat), "tool")
    if per_query_orders(cand, orders) != ns.per_query(cand):
        bad.append("constant-score tool arm does not reproduce BM25 order")
    got = score(cand, {r: rows_for(r, flat) for r in TOOL_RUNS}, noul_rows, sink)
    if got != "SWITCH":
        bad.append(f"BM25-order tool arms decide {got}, want SWITCH")
    # 3 unordered queries: scored; 4: that run NOT-SCORED, which is not WIN, so SWITCH
    three, four = {"1", "3", "5"}, {"1", "3", "5", "13"}
    arms = {r: rows_for(r, oracle) for r in TOOL_RUNS}
    arms["tool-run2"] = rows_for("tool-run2", oracle, three)
    if score(cand, arms, noul_rows, sink) != "KEEP":
        bad.append("3 unordered queries must still be scored")
    arms["tool-run2"] = rows_for("tool-run2", oracle, four)
    if score(cand, arms, noul_rows, sink) != "SWITCH":
        bad.append("4 unordered queries must make the run NOT-SCORED")
    # the rule on labels alone
    cases = [
        (["WIN"] * 3, ["TIE"] * 9, "KEEP"),
        (["WIN"] * 3, ["WIN"] * 9, "KEEP"),
        (["WIN", "WIN", "TIE"], ["TIE"] * 9, "SWITCH"),
        (["WIN"] * 3, ["LOSE"] + ["TIE"] * 8, "MIXED"),
        (["WIN"] * 3, ["LOSE"] * 8 + ["TIE"], "MIXED"),
        (["WIN"] * 3, ["LOSE"] * 9, "SWITCH"),
        (["LOSE"] * 3, ["LOSE"] * 9, "SWITCH"),
    ]
    for a, b, want in cases:
        if decide(a, b) != want:
            bad.append(f"decide({a}, {b}) != {want}")
    # a row outside the shortlist is refused
    broken = rows_for("tool", oracle)
    broken[0]["ranking"][0]["doc"] = "not-a-doc"
    try:
        tool_orders(cand, broken, "tool")
        bad.append("a ranking outside the shortlist was accepted")
    except SystemExit:
        pass
    for b in bad:
        print(f"SELFTEST RED: {b}")
    print(
        "SELFTEST "
        + (
            "FAIL"
            if bad
            else "PASS: oracle KEEP, BM25 order = BM25 and SWITCH, 3 unordered scored, 4 NOT-SCORED, rule table 7/7, foreign doc refused"
        )
    )
    return 1 if bad else 0


def check_receipt(path):
    text = open(path, encoding="utf-8").read()
    if BEGIN not in text or END not in text:
        print(f"no {BEGIN} ... {END} block in {path}")
        return 1
    block = text.split(BEGIN, 1)[1].split(END, 1)[0].strip("\n").split("\n")
    if block[0] != "```text" or block[-1] != "```":
        print("receipt block is not a ```text fence")
        return 1
    want = "\n".join(block[1:-1])
    lines = []
    cand, tool_rows, noul_rows, missing = load_all()
    if missing:
        print("NOT_RUN: no rows for " + ", ".join(missing))
        return 2
    score(cand, tool_rows, noul_rows, lines.append)
    got = "\n".join(lines)
    if got == want:
        print(f"RECEIPT MATCH: {len(lines)} lines byte-identical")
        return 0
    for i, (g, w) in enumerate(zip(got.split("\n"), want.split("\n"))):
        if g != w:
            print(f"RECEIPT DIFF at line {i + 1}:\n  scorer : {g}\n  receipt: {w}")
            break
    else:
        print("RECEIPT DIFF: line counts differ")
    return 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if argv[:1] == ["--check-receipt"]:
        return check_receipt(argv[1])
    cand, tool_rows, noul_rows, missing = load_all()
    if missing:
        print("NOT_RUN: no rows for " + ", ".join(missing))
        return 2
    score(cand, tool_rows, noul_rows)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
