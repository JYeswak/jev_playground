#!/usr/bin/env python3
"""Bead jev-k9z.9: the one-passage Noul of work/rerank-scifact/run.py on NevIR, paired with
the shipped jev_rerank rubric (tool.mjs) on the same 2,766 questions.

  PY=upstream/typesafe-ai/system-one-adapter-python/.venv/bin/python
  $PY work/rerank-nevir/nevir.py --selftest          # no key, no network
  python3 work/rerank-nevir/nevir.py score           # keyless, committed rows only
  infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \\
    $PY work/rerank-nevir/nevir.py {noul|noul-run2|noul-run3}

Preregistration and the fixed rule: docs/demos/upstream-repro/rerank-nevir-20260924.md.

The Noul arm imports run.py's QUESTION, QNAME, state_for, row_ok, billing_block, JEV_MODEL and
TIMEOUT_S and restates none of them. One request per (question, passage): the state holds that
passage only, in run.py's shape with an empty title (NevIR passages have none). Rows hold ids,
the noul, tokens and latency, never text. A pair that fails gets one more attempt in the same
invocation; a 402 stops dispatch.
"""

import asyncio
import collections
import gzip
import hashlib
import hmac
import importlib.util
import json
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PREREG = os.path.join(ROOT, "docs/demos/upstream-repro/rerank-nevir-20260924.md")
BENCH = os.path.join(ROOT, "jev-rerank-bench")
CANDIDATES = os.path.join(BENCH, "candidates", "nevir.jsonl")
CANDIDATES_SHA256 = "0c3acd0deda80e2cd9c31ed3b50e9fcef7380caa83f5b6cff313d7e441b92e07"
NEVIR_SHA256 = "5eb79ec32e82ff17ef6c2f47b75baca182013053ed74672d426bbc338af05d67"
NEVIR_PATH = os.environ.get("NEVIR_TEST", "/tmp/nevir/test.jsonl")
COMMITTED = os.path.join(BENCH, "cache", "jev-score-batch", "nevir.present.jsonl.gz")
NOUL_RUNS = ("noul", "noul-run2", "noul-run3")
TOOL_RUNS = ("tool", "tool-run2", "tool-run3")
CONCURRENCY = int(os.environ.get("NEVIR_CONCURRENCY", "4"))
# The fixed rule (preregistration): paired bootstrap over pairs.
BOOT_B = 2000
BOOT_SEED = 20260924
FAIL_CEILING = 27  # questions failed after the resume pass, per run (1% of 2,766)
F1_WANT = 984  # jev-rerank-bench's committed jev-score-batch: 984/1383 = 0.7115
F2_FLOOR = 0.65  # every tool run's paired accuracy


def rows_path(run):
    return os.path.join(HERE, f"rows-{run}.jsonl")


def read_rows(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    lines = text.split("\n")
    if text and not text.endswith("\n"):
        lines = lines[:-1]  # a crash's partial last line is ignored, never deleted
    return [json.loads(line) for line in lines if line.strip()]


def pinned(path, want):
    with open(path, "rb") as fh:
        data = fh.read()
    got = hashlib.sha256(data).hexdigest()
    if not hmac.compare_digest(got, want):
        raise SystemExit(f"{path} sha256 {got} != {want}")
    return [
        json.loads(line) for line in data.decode("utf-8").splitlines() if line.strip()
    ]


def questions():
    """The bench's 2,766 questions: qid, pair, query, relevant doc, [d1, d2]."""
    out = []
    for c in pinned(CANDIDATES, CANDIDATES_SHA256):
        out.append(
            {
                "qid": c["qid"],
                "pair": c["pair"],
                "query": c["query"],
                "rel": next(iter(c["relevant"])),
                "docs": [p["did"] for p in c["present"]],
            }
        )
    return out


def passages():
    text = {}
    for r in pinned(NEVIR_PATH, NEVIR_SHA256):
        text[f"{r['id']}-d1"] = r["doc1"]
        text[f"{r['id']}-d2"] = r["doc2"]
    return text


def scifact_run():
    spec = importlib.util.spec_from_file_location(
        "rerank_scifact_run", os.path.join(ROOT, "work/rerank-scifact/run.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --- Noul arm -------------------------------------------------------------------------------


async def run_noul(run, repo=None):
    R = scifact_run()
    sys.path.insert(0, os.path.join(ROOT, "work/sr-adopt"))
    from phase_gate import call_after_bar

    bar = PREREG
    call_after_bar(bar, lambda: None, repo=repo or ROOT)
    if not os.environ.get("TYPESAFE_API_KEY"):
        print(
            "unconfigured: TYPESAFE_API_KEY is not set, no call made", file=sys.stderr
        )
        return 2
    qs = questions()
    text = passages()
    corpus = {d: {"_id": d, "title": "", "text": t} for d, t in text.items()}
    query_of = {q["qid"]: q["query"] for q in qs}
    todo_all = [(q["qid"], d) for q in qs for d in q["docs"]]
    path = rows_path(run)
    existing = read_rows(path)

    from typesafe_sdk import AsyncTypeSafeClient, RetryPolicy

    stop = asyncio.Event()
    counts = collections.Counter()
    t_start = time.time()

    async with AsyncTypeSafeClient(model=R.JEV_MODEL, retry=RetryPolicy()) as client:
        sem = asyncio.Semaphore(CONCURRENCY)

        async def one(qid, doc, attempt):
            if stop.is_set():
                return None
            async with sem:
                if stop.is_set():
                    return None
                t0 = time.perf_counter()
                try:
                    resp = await asyncio.wait_for(
                        client.system_one(
                            R.state_for(corpus, query_of, qid, doc),
                            {R.QNAME: R.QUESTION},
                        ),
                        timeout=R.TIMEOUT_S,
                    )
                except Exception as exc:  # noqa: BLE001 - recorded, or stops the arm
                    message = f"{type(exc).__name__}: {str(exc)[:500]}"
                    row = {
                        "qid": qid,
                        "doc": doc,
                        "arm": run,
                        "attempt": attempt,
                        "error": message,
                        "latencyMs": int((time.perf_counter() - t0) * 1000),
                    }
                    if R.billing_block(message):
                        row["blocked"] = True
                        stop.set()
                    return row
                return R.row_ok(
                    qid,
                    doc,
                    run,
                    resp.model,
                    float(resp.nouls[R.QNAME].noul),
                    int((time.perf_counter() - t0) * 1000),
                    {
                        "input_tokens": resp.usage.input_tokens,
                        "output_tokens": resp.usage.output_tokens,
                    },
                    {"attempt": attempt},
                )

        with open(path, "a", encoding="utf-8") as fh:
            for attempt in (1, 2):
                if stop.is_set():
                    break
                seen = {
                    (r["qid"], r["doc"])
                    for r in existing
                    if r.get("attempt") == attempt
                }
                if attempt == 1:
                    todo = [p for p in todo_all if p not in seen]
                else:
                    failed = {
                        (r["qid"], r["doc"])
                        for r in existing
                        if r.get("attempt") == 1 and "error" in r
                    }
                    todo = [p for p in todo_all if p in failed and p not in seen]
                print(f"{run}: attempt {attempt}, {len(todo)} pairs", file=sys.stderr)
                tasks = [asyncio.create_task(one(q, d, attempt)) for q, d in todo]
                for fut in asyncio.as_completed(tasks):
                    row = await fut
                    if row is None:
                        continue
                    fh.write(json.dumps(row, ensure_ascii=False) + "\n")
                    fh.flush()
                    existing.append(row)
                    counts["error" if "error" in row else "ok"] += 1
                    if row.get("blocked"):
                        print("BLOCKED: " + row["error"], file=sys.stderr)
                        for task in tasks:
                            task.cancel()
                        break
                    if sum(counts.values()) % 500 == 0:
                        print(f"  {dict(counts)}", file=sys.stderr)
    s = summary_noul(read_rows(path), qs)
    print(
        f"{run} model={R.JEV_MODEL} start={time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(t_start))} "
        f"end={time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} wall_s={time.time() - t_start:.1f} "
        f"requests={s['requests']} failed_questions={s['failed_questions']} input_tokens={s['tokens']}"
    )
    if stop.is_set():
        return 4
    return 0 if s["failed_questions"] == 0 else 3


# --- Scoring (stdlib only) ------------------------------------------------------------------


def noul_scores(rows):
    """(qid, doc) -> noul, from the latest successful attempt."""
    got = {}
    for r in sorted(rows, key=lambda r: r.get("attempt", 1)):
        if "noul" in r:
            got[(r["qid"], r["doc"])] = r["noul"]
    return got


def summary_noul(rows, qs):
    got = noul_scores(rows)
    failed = sum(1 for q in qs if any((q["qid"], d) not in got for d in q["docs"]))
    return {
        "requests": len(rows),
        "failed_questions": failed,
        "tokens": sum((r.get("usage") or {}).get("input_tokens", 0) for r in rows),
    }


def verdicts_noul(rows, qs):
    """qid -> (right, top pick, failed). Strict: a tie or a missing score is wrong."""
    got = noul_scores(rows)
    out = {}
    for q in qs:
        s = {d: got.get((q["qid"], d)) for d in q["docs"]}
        failed = any(v is None for v in s.values())
        other = next(d for d in q["docs"] if d != q["rel"])
        right = not failed and s[q["rel"]] > s[other]
        top = (
            None
            if failed
            else max(q["docs"], key=lambda d: (s[d], -q["docs"].index(d)))
        )
        out[q["qid"]] = (right, top, failed)
    return out


def verdicts_tool(rows, qs):
    latest = {}
    for r in rows:
        if r["qid"] not in latest or r["attempt"] > latest[r["qid"]]["attempt"]:
            latest[r["qid"]] = r
    out = {}
    for q in qs:
        r = latest.get(q["qid"])
        failed = r is None or not r["ordered"]
        s = {} if failed else {x["doc"]: x["score"] for x in r["ranking"]}
        other = next(d for d in q["docs"] if d != q["rel"])
        right = not failed and s[q["rel"]] > s[other]
        top = (
            None
            if failed
            else max(q["docs"], key=lambda d: (s[d], -q["docs"].index(d)))
        )
        out[q["qid"]] = (right, top, failed)
    return out


def verdicts_committed(qs):
    """jev-rerank-bench's committed jev-score-batch cache (jev-1.13.0, 2026-09-16)."""
    rows = {}
    with gzip.open(COMMITTED, "rt", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            rows[r["qid"]] = r
    out = {}
    for q in qs:
        r = rows.get(q["qid"])
        failed = r is None or not r["ok"]
        s = {} if failed else dict(zip(r["dids"], r["scores"]))
        other = next(d for d in q["docs"] if d != q["rel"])
        right = not failed and s[q["rel"]] > s[other]
        top = (
            None
            if failed
            else max(q["docs"], key=lambda d: (s[d], -q["docs"].index(d)))
        )
        out[q["qid"]] = (right, top, failed)
    return out


def per_pair(verdicts, qs):
    """pair -> both questions right (nevir_eval.py's paired accuracy), in sorted pair order."""
    by = collections.defaultdict(list)
    for q in qs:
        by[q["pair"]].append(verdicts[q["qid"]][0])
    return [1.0 if all(by[p]) else 0.0 for p in sorted(by)]


def arm_stats(verdicts, qs):
    pp = per_pair(verdicts, qs)
    tops = collections.defaultdict(list)
    for q in qs:
        tops[q["pair"]].append(verdicts[q["qid"]][1])
    same = [1.0 if len(set(t)) == 1 and None not in t else 0.0 for t in tops.values()]
    return {
        "pairs_right": int(sum(pp)),
        "paired_accuracy": sum(pp) / len(pp),
        "question_accuracy": sum(v[0] for v in verdicts.values()) / len(verdicts),
        "same_top_pick": sum(same) / len(same),
        "failed_questions": sum(v[2] for v in verdicts.values()),
    }


def bootstrap(a, b):
    """Mean of a - b and its 95% percentile interval over pairs; fixed seed per call."""
    rng = random.Random(BOOT_SEED)
    n = len(a)
    diffs = []
    for _ in range(BOOT_B):
        idx = [rng.randrange(n) for _ in range(n)]
        diffs.append(sum(a[i] - b[i] for i in idx) / n)
    diffs.sort()
    lo, hi = diffs[int(0.025 * BOOT_B)], diffs[int(0.975 * BOOT_B) - 1]
    verdict = "WIN" if lo > 0 else "LOSE" if hi < 0 else "TIE"
    return sum(x - y for x, y in zip(a, b)) / n, lo, hi, verdict


def outcome(pairings_rerun, pairings_committed, f1_ok, f2_ok, not_scored):
    if not_scored:
        return "NOT-SCORED"
    if not (f1_ok and f2_ok):
        return "NO-RULING (feasibility failed)"
    rerun = [v for *_rest, v in pairings_rerun]
    committed = [v for *_rest, v in pairings_committed]
    if "LOSE" not in rerun and "LOSE" not in committed:
        return "NOT-WORSE (file the switch)"
    if rerun and all(v == "LOSE" for v in rerun):
        return "WORSE (no switch)"
    return "MIXED (numbers only, no switch)"


def score():
    qs = questions()
    missing = [r for r in NOUL_RUNS + TOOL_RUNS if not os.path.exists(rows_path(r))]
    if missing:
        print(
            f"REFUSED: no rows yet for {', '.join(missing)}; the live arms have not all run."
        )
        return 2
    arms = {}
    tokens = {}
    requests = {}
    for run in NOUL_RUNS:
        rows = read_rows(rows_path(run))
        arms[run] = verdicts_noul(rows, qs)
        tokens[run] = sum((r.get("usage") or {}).get("input_tokens", 0) for r in rows)
        requests[run] = len(rows)
    for run in TOOL_RUNS:
        rows = read_rows(rows_path(run))
        arms[run] = verdicts_tool(rows, qs)
        tokens[run] = sum(r["inputTokens"] for r in rows)
        requests[run] = sum(r["calls"] for r in rows)
    arms["committed"] = verdicts_committed(qs)
    stats = {k: arm_stats(v, qs) for k, v in arms.items()}
    print(
        "| arm | pairs right / 1383 | paired accuracy | question accuracy | same top pick | failed questions | requests | input tokens / question |"
    )
    print("|---|---:|---:|---:|---:|---:|---:|---:|")
    for k, s in stats.items():
        tq = f"{tokens[k] / len(qs):.0f}" if k in tokens else "-"
        rq = str(requests[k]) if k in requests else "-"
        print(
            f"| {k} | {s['pairs_right']} | {s['paired_accuracy']:.4f} | {s['question_accuracy']:.4f} | "
            f"{s['same_top_pick']:.4f} | {s['failed_questions']} | {rq} | {tq} |"
        )
    not_scored = [
        k for k in NOUL_RUNS + TOOL_RUNS if stats[k]["failed_questions"] > FAIL_CEILING
    ]
    f1_ok = stats["committed"]["pairs_right"] == F1_WANT
    f2_ok = all(stats[k]["paired_accuracy"] >= F2_FLOOR for k in TOOL_RUNS)
    print(
        f"\nf1 committed score-batch reproduces {F1_WANT}/1383: {'PASS' if f1_ok else 'FAIL'} ({stats['committed']['pairs_right']})"
    )
    print(f"f2 every tool run >= {F2_FLOOR}: {'PASS' if f2_ok else 'FAIL'}")
    print(
        f"runs over the {FAIL_CEILING}-question failure ceiling: {not_scored or 'none'}"
    )
    pp = {k: per_pair(v, qs) for k, v in arms.items()}
    print("\n| Noul run | vs | diff (Noul - rubric) | 95% interval | verdict |")
    print("|---|---|---:|---|---|")
    rerun, committed = [], []
    for n in NOUL_RUNS:
        for t in TOOL_RUNS + ("committed",):
            d, lo, hi, v = bootstrap(pp[n], pp[t])
            (committed if t == "committed" else rerun).append((n, t, d, lo, hi, v))
            print(f"| {n} | {t} | {d:+.4f} | [{lo:+.4f}, {hi:+.4f}] | {v} |")
    print("\nOUTCOME: " + outcome(rerun, committed, f1_ok, f2_ok, not_scored))
    return 0


# --- Selftest (no key, no network) ----------------------------------------------------------


def selftest():
    bad = []
    R = scifact_run()
    if (
        R.QUESTION.instructions
        != "Does this passage contain evidence relevant to the query?"
    ):
        bad.append("imported QUESTION drifted")
    qs = questions()
    if len(qs) != 2766 or len({q["pair"] for q in qs}) != 1383:
        bad.append("candidates: not 2,766 questions over 1,383 pairs")
    if not all(q["docs"] == [f"{q['pair']}-d1", f"{q['pair']}-d2"] for q in qs):
        bad.append("candidates: d1, d2 order")
    if os.path.exists(NEVIR_PATH):
        text = passages()
        corpus = {d: {"_id": d, "title": "", "text": t} for d, t in text.items()}
        q = qs[0]
        st = R.state_for(corpus, {q["qid"]: q["query"]}, q["qid"], q["docs"][1])
        if st != {
            "query": q["query"],
            "passage": {"id": q["docs"][1], "title": "", "text": text[q["docs"][1]]},
        }:
            bad.append("state is not run.py's one-passage shape")
        row = R.row_ok(
            q["qid"],
            q["docs"][1],
            "noul",
            "jev-1.13.0",
            0.5,
            1,
            {"input_tokens": 1},
            {"attempt": 1},
        )
        if text[q["docs"][1]][:30] in json.dumps(row) or q["query"] in json.dumps(row):
            bad.append("row carries text")
    else:
        bad.append(f"NevIR text absent at {NEVIR_PATH}")
    # f1: our strict scorer reproduces the bench's committed score-batch figure.
    s = arm_stats(verdicts_committed(qs), qs)
    if s["pairs_right"] != F1_WANT:
        bad.append(f"f1: committed score-batch {s['pairs_right']} != {F1_WANT}")
    # Scorer planted cases on one pair: a tie is wrong, a missing score is wrong, a fail is counted.
    two = [q for q in qs if q["pair"] == qs[0]["pair"]]
    rows = [
        {"qid": two[0]["qid"], "doc": two[0]["rel"], "noul": 0.9, "attempt": 1},
        {
            "qid": two[0]["qid"],
            "doc": next(d for d in two[0]["docs"] if d != two[0]["rel"]),
            "noul": 0.1,
            "attempt": 1,
        },
        {"qid": two[1]["qid"], "doc": two[1]["docs"][0], "noul": 0.5, "attempt": 1},
        {"qid": two[1]["qid"], "doc": two[1]["docs"][1], "noul": 0.5, "attempt": 1},
    ]
    v = verdicts_noul(rows, two)
    if not (v[two[0]["qid"]][0] and not v[two[1]["qid"]][0]):
        bad.append("scorer: right, then a tie that must be wrong")
    v2 = verdicts_noul(rows[:3], two)
    if not (v2[two[1]["qid"]][2] and not v2[two[1]["qid"]][0]):
        bad.append("scorer: a missing score must be failed and wrong")
    late = rows[:1] + [
        {"qid": two[0]["qid"], "doc": rows[1]["doc"], "error": "x", "attempt": 1},
        {"qid": two[0]["qid"], "doc": rows[1]["doc"], "noul": 0.2, "attempt": 2},
    ]
    if not verdicts_noul(late, two[:1])[two[0]["qid"]][0]:
        bad.append("scorer: the attempt-2 answer must be used")
    # Rule: planted pairings.
    same = [1.0, 0.0] * 50
    if bootstrap(same, same)[3] != "TIE":
        bad.append("bootstrap: identical arms must TIE")
    if (
        bootstrap([1.0] * 100, [0.0] * 100)[3] != "WIN"
        or bootstrap([0.0] * 100, [1.0] * 100)[3] != "LOSE"
    ):
        bad.append("bootstrap: WIN/LOSE direction")
    tie = [("n", "t", 0, 0, 0, "TIE")] * 9
    lose = [("n", "t", 0, 0, 0, "LOSE")] * 9
    ctie = [("n", "c", 0, 0, 0, "TIE")] * 3
    checks = [
        (outcome(tie, ctie, True, True, []), "NOT-WORSE (file the switch)"),
        (outcome(lose, ctie, True, True, []), "WORSE (no switch)"),
        (
            outcome(tie[:8] + lose[:1], ctie, True, True, []),
            "MIXED (numbers only, no switch)",
        ),
        (
            outcome(tie, ctie[:2] + [("n", "c", 0, 0, 0, "LOSE")], True, True, []),
            "MIXED (numbers only, no switch)",
        ),
        (outcome(tie, ctie, False, True, []), "NO-RULING (feasibility failed)"),
        (outcome(tie, ctie, True, True, ["noul"]), "NOT-SCORED"),
    ]
    for got, want in checks:
        if got != want:
            bad.append(f"rule: {got} != {want}")
    for item in bad:
        print("SELFTEST RED:", item)
    print(
        "SELFTEST "
        + (
            "FAIL"
            if bad
            else "PASS: imported question, NevIR shape, one-passage state, no text in rows, f1 984/1383, strict ties, attempt-2 use, bootstrap direction, 6 rule outcomes"
        )
    )
    return 1 if bad else 0


def main(argv):
    if argv == ["--selftest"]:
        return selftest()
    if argv == ["score"]:
        return score()
    if len(argv) == 1 and argv[0] in NOUL_RUNS:
        return asyncio.run(run_noul(argv[0]))
    raise SystemExit("usage: nevir.py --selftest | score | " + " | ".join(NOUL_RUNS))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
