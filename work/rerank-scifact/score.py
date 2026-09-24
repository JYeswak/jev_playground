#!/usr/bin/env python3
"""Keyless scorer for bead jev-nssg: rerank BEIR SciFact's BM25 top-20 by Noul, three arms.

  python3 work/rerank-scifact/score.py              # score committed rows, verdicts under the bar
  python3 work/rerank-scifact/score.py --selftest   # decision machinery on planted arms, no rows

Stdlib only. Reads candidates.jsonl (ids, BM25 scores, qrels ids) and rows-<arm>.jsonl.

Policy, frozen with the bar (docs/demos/upstream-repro/rerank-beir-scifact-20260924.md):
- Rerank = the 20 candidates sorted by noul, highest first; equal nouls keep BM25 order.
- A pair with no answer after the run's resume pass is scored on the wrong side of its qrels label:
  noul 0 if the doc is relevant, noul 1 if not.
- nDCG@10 (binary gains, ideal DCG over every relevant doc in the qrels, as pytrec_eval
  ndcg_cut_10) and Recall@10 = relevant in the top 10 / relevant in the qrels.
- Paired over the 300 queries: bootstrap 95% percentile interval of the mean difference, 2,000
  resamples, random.Random(20260924). WIN if the interval is above 0, LOSE if below, else TIE.
- All-pairings rule: a WIN (or LOSE) claim STANDS only if every pairing has that label.
"""

import json
import math
import os
import random
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CANDIDATES = os.path.join(HERE, "candidates.jsonl")
CANDIDATES_SHA256 = "2cf3a9a96a12253a76095f5505dc475dcae5eb64b5dd29b2ed36de9290fe83e8"
JEV_ARMS = ("jev", "jev-run2", "jev-run3")
GROK_ARMS = ("grok", "grok-run2", "grok-run3")
METRICS = ("ndcg10", "recall10")
BOOT = 2000
SEED = 20260924
DEPTH = 20


def load_jsonl(path):
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def load_candidates(path=CANDIDATES, check=True):
    if check:
        import hashlib

        digest = hashlib.sha256(open(path, "rb").read()).hexdigest()
        if digest != CANDIDATES_SHA256:
            raise SystemExit(
                f"candidates.jsonl sha256 {digest} is not the frozen {CANDIDATES_SHA256}"
            )
    rows = load_jsonl(path)
    for r in rows:
        if len(r["cands"]) != DEPTH or not r["rel"]:
            raise SystemExit(f"malformed candidate row qid={r['qid']}")
    return rows


def ndcg10(ranked, rel):
    dcg = sum(1 / math.log2(i + 2) for i, d in enumerate(ranked[:10]) if d in rel)
    idcg = sum(1 / math.log2(i + 2) for i in range(min(10, len(rel))))
    return dcg / idcg


def recall10(ranked, rel):
    return sum(1 for d in ranked[:10] if d in rel) / len(rel)


def rerank(bm25_ids, noul):
    """Highest noul first; Python's sort is stable, so ties keep BM25 order."""
    return sorted(bm25_ids, key=lambda d: -noul[d])


def arm_nouls(cand_rows, rows):
    """{(qid, doc): noul} over every candidate pair, plus accounting.

    A success row wins over an error row for the same pair. A row for a pair outside the shortlist,
    a non-finite noul, or one outside [0, 1] is refused: the file is not this unit's.
    """
    wanted = {(r["qid"], d) for r in cand_rows for d, _ in r["cands"]}
    rel = {r["qid"]: set(r["rel"]) for r in cand_rows}
    got, stats = {}, {"models": set(), "latency": [], "tin": 0, "tout": 0, "errors": 0}
    for row in rows:
        key = (row["qid"], row["doc"])
        if key not in wanted:
            raise SystemExit(f"row for a pair outside the shortlist: {key}")
        if "error" in row:
            stats["errors"] += 1
            continue
        p = row["noul"]
        if not isinstance(p, (int, float)) or not math.isfinite(p) or not 0 <= p <= 1:
            raise SystemExit(f"noul out of range for {key}: {p!r}")
        if key in got:
            raise SystemExit(f"two answers for one pair: {key}")
        got[key] = float(p)
        stats["models"].add(row.get("model"))
        stats["latency"].append(row.get("latencyMs", 0))
        usage = row.get("usage") or {}
        stats["tin"] += usage.get("input_tokens") or 0
        stats["tout"] += usage.get("output_tokens") or 0
    failed = wanted - set(got)
    for qid, doc in failed:
        got[(qid, doc)] = 0.0 if doc in rel[qid] else 1.0
    stats["answered"] = len(wanted) - len(failed)
    stats["failed"] = len(failed)
    stats["distinct"] = len({p for k, p in got.items() if k not in failed})
    return got, stats


def per_query(cand_rows, pmap=None):
    """Per-query (nDCG@10, Recall@10); pmap=None is BM25 order."""
    out = {m: [] for m in METRICS}
    for r in cand_rows:
        ids = [d for d, _ in r["cands"]]
        ranked = (
            ids if pmap is None else rerank(ids, {d: pmap[(r["qid"], d)] for d in ids})
        )
        rel = set(r["rel"])
        out["ndcg10"].append(ndcg10(ranked, rel))
        out["recall10"].append(recall10(ranked, rel))
    return out


def boot_diff(a, b):
    """Paired bootstrap 95% percentile interval of mean(a) - mean(b) over queries."""
    rng = random.Random(SEED)
    n = len(a)
    vals = []
    for _ in range(BOOT):
        idx = [rng.randrange(n) for _ in range(n)]
        vals.append(sum(a[k] - b[k] for k in idx) / n)
    vals.sort()
    return vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]


def label(lo, hi):
    if lo > 0:
        return "WIN"
    if hi < 0:
        return "LOSE"
    return "TIE"


def compare(a, b):
    lo, hi = boot_diff(a, b)
    wins = sum(1 for x, y in zip(a, b) if x > y)
    losses = sum(1 for x, y in zip(a, b) if x < y)
    return {
        "diff": statistics.fmean(a) - statistics.fmean(b),
        "lo": lo,
        "hi": hi,
        "label": label(lo, hi),
        "q": (wins, losses, len(a) - wins - losses),
    }


def claim(labels, want):
    """All-pairings rule: STANDS only if every pairing carries the wanted label."""
    k = sum(1 for x in labels if x == want)
    return ("STANDS" if labels and k == len(labels) else "RETRACTED"), k, len(labels)


def verdicts(bm25, jev, grok):
    """jev, grok: {arm: per_query dict}. Returns the preregistered decisions."""
    out = {"vs_bm25": {}, "vs_grok": {}, "grok_vs_bm25": {}}
    for m in METRICS:
        out["vs_bm25"][m] = {a: compare(jev[a][m], bm25[m]) for a in jev}
        out["grok_vs_bm25"][m] = {g: compare(grok[g][m], bm25[m]) for g in grok}
        out["vs_grok"][m] = {
            (a, g): compare(jev[a][m], grok[g][m]) for a in jev for g in grok
        }
    beat = claim([c["label"] for c in out["vs_bm25"]["ndcg10"].values()], "WIN")
    grok_loses = [
        (m, pair)
        for m in METRICS
        for pair, c in out["vs_grok"][m].items()
        if c["label"] == "LOSE"
    ]
    out["pass"] = beat[0] == "STANDS" and not grok_loses
    out["beat_bm25_ndcg"] = beat
    out["grok_lose_pairings"] = grok_loses
    return out


def pctl(xs, q):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, max(0, math.ceil(q * len(xs)) - 1))] if xs else None


def report(cand_rows, arms_rows):
    bm25 = per_query(cand_rows)
    oracle = per_query(
        cand_rows,
        {
            (r["qid"], d): float(d in set(r["rel"]))
            for r in cand_rows
            for d, _ in r["cands"]
        },
    )
    print(f"queries={len(cand_rows)} pairs={len(cand_rows) * DEPTH}")
    print(
        "\nArm                  nDCG@10  Recall@10  answered  failed  distinct  p50/p95 ms  tokens in/out"
    )
    print(
        f"BM25 order (floor)   {statistics.fmean(bm25['ndcg10']):.4f}   {statistics.fmean(bm25['recall10']):.4f}"
    )
    print(
        f"oracle top-20        {statistics.fmean(oracle['ndcg10']):.4f}   {statistics.fmean(oracle['recall10']):.4f}   (ceiling, descriptive)"
    )
    scored = {}
    for arm, rows in arms_rows.items():
        pmap, st = arm_nouls(cand_rows, rows)
        scored[arm] = per_query(cand_rows, pmap)
        by_q = {}
        for row in rows:
            if "error" in row or "noul" not in row:
                continue
            bucket = by_q.setdefault(row["qid"], {"ms": 0, "tin": 0, "tout": 0})
            bucket["ms"] += row.get("latencyMs") or 0
            usage = row.get("usage") or {}
            bucket["tin"] += usage.get("input_tokens") or 0
            bucket["tout"] += usage.get("output_tokens") or 0
        q_ms = [b["ms"] for b in by_q.values()]
        q_tin = [b["tin"] for b in by_q.values()]
        print(
            f"{arm:<20} {statistics.fmean(scored[arm]['ndcg10']):.4f}   "
            f"{statistics.fmean(scored[arm]['recall10']):.4f}   {st['answered']:>8}  {st['failed']:>6}  "
            f"{st['distinct']:>8}  {pctl(st['latency'], 0.5)}/{pctl(st['latency'], 0.95)}  "
            f"{st['tin']:,}/{st['tout']:,}  models={sorted(map(str, st['models']))}"
        )
        if by_q:
            print(
                f"{'':20} per-query latency p50/p95 {pctl(q_ms, 0.5)}/{pctl(q_ms, 0.95)} ms; "
                f"mean tokens in/out {statistics.fmean(q_tin):.0f}/"
                f"{statistics.fmean([b['tout'] for b in by_q.values()]):.0f}"
            )
    return bm25, scored


def print_grid(v):
    for block in ("vs_bm25", "grok_vs_bm25", "vs_grok"):
        for m in METRICS:
            print(
                f"\n{block} {m}: pairing  diff  95% interval  label  queries better/worse/equal"
            )
            for pair, c in v[block][m].items():
                name = pair if isinstance(pair, str) else f"{pair[0]} vs {pair[1]}"
                print(
                    f"  {name:<22} {c['diff']:+.4f}  [{c['lo']:+.4f}, {c['hi']:+.4f}]  "
                    f"{c['label']:<4}  {c['q'][0]}/{c['q'][1]}/{c['q'][2]}"
                )


def summarize(v):
    print("\nClaims under the all-pairings rule")
    for block, want_list in (
        ("vs_bm25", ("WIN", "LOSE")),
        ("grok_vs_bm25", ("WIN", "LOSE")),
        ("vs_grok", ("WIN", "LOSE")),
    ):
        for m in METRICS:
            labels = [c["label"] for c in v[block][m].values()]
            for want in want_list:
                s, k, n = claim(labels, want)
                print(f"  {block} {m} {want}: {s} ({k}/{n})")
    s, k, n = v["beat_bm25_ndcg"]
    print(f"\nPASS (1) Jev beats BM25 on nDCG@10 in every run: {s} ({k}/{n})")
    print(
        f"PASS (2) no Jev-vs-grok pairing is LOSE on nDCG@10 or Recall@10: {'yes' if not v['grok_lose_pairings'] else 'no ' + str(v['grok_lose_pairings'])}"
    )
    print(f"overall: {'PASS' if v['pass'] else 'FAIL'}")


def selftest():
    """The decision machinery on planted arms over the real shortlists. No rows, no key."""
    cand = load_candidates()
    rel = {r["qid"]: set(r["rel"]) for r in cand}
    pairs = [(r["qid"], d) for r in cand for d, _ in r["cands"]]
    bm25 = per_query(cand)

    def arm(fn):
        return per_query(cand, {(q, d): fn(q, d) for q, d in pairs})

    oracle = arm(lambda q, d: float(d in rel[q]))
    anti = arm(lambda q, d: float(d not in rel[q]))
    flat = arm(lambda q, d: 0.5)
    bad = []
    if compare(oracle["ndcg10"], bm25["ndcg10"])["label"] != "WIN":
        bad.append("oracle arm is not a WIN over BM25")
    if compare(anti["ndcg10"], bm25["ndcg10"])["label"] != "LOSE":
        bad.append("anti-oracle arm is not a LOSE to BM25")
    c = compare(flat["ndcg10"], bm25["ndcg10"])
    if c["label"] != "TIE" or c["diff"] != 0 or (c["lo"], c["hi"]) != (0, 0):
        bad.append("constant-noul arm does not reproduce BM25 order exactly")
    # every pair failed: the wrong-side rule must make it no better than the anti-oracle
    pmap, st = arm_nouls(cand, [])
    if st["failed"] != len(pairs) or per_query(cand, pmap) != anti:
        bad.append("all-failed arm is not scored as the anti-oracle")
    # all-pairings: one TIE among nine WINs retracts the WIN
    if (
        claim(["WIN"] * 8 + ["TIE"], "WIN")[0] != "RETRACTED"
        or claim(["WIN"] * 9, "WIN")[0] != "STANDS"
    ):
        bad.append("all-pairings rule")
    for b in bad:
        print(f"SELFTEST RED: {b}")
    print(
        "SELFTEST "
        + (
            "FAIL"
            if bad
            else "PASS: oracle WIN, anti-oracle LOSE, constant = BM25, all-failed = anti-oracle, 8/9 retracts"
        )
    )
    return 1 if bad else 0


def main(argv):
    if "--selftest" in argv:
        return selftest()
    cand = load_candidates()
    present, missing = {}, []
    for arm in JEV_ARMS + GROK_ARMS:
        path = os.path.join(HERE, f"rows-{arm}.jsonl")
        if os.path.exists(path):
            present[arm] = load_jsonl(path)
        else:
            missing.append(arm)
    bm25, scored = report(cand, present)
    jev_missing = [a for a in JEV_ARMS if a not in present]
    grok_missing = [a for a in GROK_ARMS if a not in present]
    if not jev_missing and not grok_missing:
        v = verdicts(
            bm25, {a: scored[a] for a in JEV_ARMS}, {g: scored[g] for g in GROK_ARMS}
        )
        print_grid(v)
        summarize(v)
        return 0
    if jev_missing:
        print(
            "\nBLOCKED-until-credits: Jev arms absent ("
            + ", ".join(jev_missing)
            + "). Not FAIL. No Jev call in this scoring."
        )
    if grok_missing:
        print("NOT_RUN: no rows for " + ", ".join(grok_missing))
    if not grok_missing:
        print("\ngrok vs BM25 (3 runs; Jev pairings are not scored)")
        for m in METRICS:
            labels = []
            print(
                f"\ngrok_vs_bm25 {m}: pairing  diff  95% interval  label  queries better/worse/equal"
            )
            for g in GROK_ARMS:
                c = compare(scored[g][m], bm25[m])
                labels.append(c["label"])
                print(
                    f"  {g:<22} {c['diff']:+.4f}  [{c['lo']:+.4f}, {c['hi']:+.4f}]  "
                    f"{c['label']:<4}  {c['q'][0]}/{c['q'][1]}/{c['q'][2]}"
                )
            for want in ("WIN", "LOSE"):
                s, k, n = claim(labels, want)
                print(f"  grok_vs_bm25 {m} {want}: {s} ({k}/{n})")
    print("overall: BLOCKED" if jev_missing else "overall: NOT_RUN")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
