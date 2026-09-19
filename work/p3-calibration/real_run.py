"""P3-7: frozen supervision questions over REAL session windows (LIVE, budgeted).

Sampling (stated, deterministic): stuck windows preferred by named tools and
elapsed<7200s, spread across sessions, seed 7; healthy/ambiguous uniform spread.
Frozen stuck question VERBATIM from foreman_cal.py; feasibility = testfail
(requires both classes or HARNESS BLIND). Bar unchanged: AUC>=0.90,
false-stuck<=1/10 @0.80. Run: cd work/pysdk && uv run python
../p3-calibration/real_run.py. Writes ../p3-calibration/real_scores.jsonl.
"""

import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from typesafe_sdk import Noul, RetryPolicy, TypeSafeClient  # noqa: E402

STUCK_Q = (
    "This worker is stuck or off-track and a supervisor should intervene "
    "(interrupt, redirect, or reassign it). Do NOT flag a worker that is making "
    "steady progress, waiting briefly on a known dependency, or working through "
    "a long task with visible output."
)
TESTFAIL_Q = (
    "This observation mentions a test failure (a test that failed, an assertion "
    "error, or a failing test suite)."
)
THRESHOLD = 0.80


def render(w):
    lines = [
        f"Worker observation: {len(w['tools'])} tool calls spanning "
        f"{w['elapsed_s']:.0f}s: [{', '.join(w['tools'])}].",
        f"Longest run of identical tool+arguments: {w['max_repeat']}.",
        f"Write/edit tools fired: {'yes' if w['write_fired'] else 'no'}.",
    ]
    outs = [o for o in w["outputs"] if o.strip()][:3]
    for o in outs:
        lines.append("Output excerpt: " + o[:600])
    return "\n".join(lines)


def auc(scores, labels):
    pos = [s for s, l in zip(scores, labels) if l]
    neg = [s for s, l in zip(scores, labels) if not l]
    if not pos or not neg:
        return float("nan")
    wins = ties = 0
    for p in pos:
        for n in neg:
            if p > n:
                wins += 1
            elif p == n:
                ties += 1
    return (wins + 0.5 * ties) / (len(pos) * len(neg))


def pick(rows, seed):
    rng = random.Random(seed)
    st = [r for r in rows if r["label"] == "stuck"]
    st_named = [
        r for r in st if all(t != "?" for t in r["tools"]) and r["elapsed_s"] < 7200
    ]
    st_rest = [r for r in st if r not in st_named]
    by_sess = {}
    for r in st_named + st_rest:
        by_sess.setdefault(r["session"], []).append(r)
    sess_order = sorted(by_sess, key=lambda s: len(by_sess[s]), reverse=True)
    chosen = []
    i = 0
    while len(chosen) < 10 and any(by_sess.values()):
        for s in sess_order:
            if by_sess[s] and len(chosen) < 10:
                chosen.append(by_sess[s].pop(0))
        i += 1
        if i > 20:
            break
    he = [r for r in rows if r["label"] == "healthy"]
    am = [r for r in rows if r["label"] == "ambiguous"]
    rng.shuffle(he)
    rng.shuffle(am)

    # spread healthy/ambiguous across sessions too
    def spread(pool, n):
        seen, out, rest = set(), [], []
        for r in pool:
            (out if r["session"] not in seen else rest).append(r)
            seen.add(r["session"])
        return (out + rest)[:n]

    return chosen + spread(he, 10) + spread(am, 10)


def main():
    rows = [json.loads(l) for l in open("real_windows.jsonl")]
    sample = pick(rows, 7)
    print(
        "sample:",
        len(sample),
        {
            k: sum(1 for r in sample if r["label"] == k)
            for k in ("stuck", "healthy", "ambiguous")
        },
    )
    client = TypeSafeClient(
        retry=RetryPolicy(
            max_retries=3, timeout=60.0, http_statuses={429, 500, 502, 503, 504}
        )
    )
    n_req, models = 0, set()
    with open("real_scores.jsonl", "w") as out:
        for w in sample:
            q = {
                "stuck": Noul(instructions=STUCK_Q),
                "testfail": Noul(instructions=TESTFAIL_Q),
            }
            r = client.system_one({"observation": render(w)}, q, model="jev-latest")
            models.add(r.model)
            n_req += 1
            out.write(
                json.dumps(
                    {
                        "label": w["label"],
                        "testfail": w["testfail"],
                        "elapsed_s": w["elapsed_s"],
                        "max_repeat": w["max_repeat"],
                        "tools": w["tools"],
                        "session": w["session"].split("sessions/")[-1][:40],
                        "p_stuck": r.answers["stuck"].noul,
                        "p_testfail": r.answers["testfail"].noul,
                    }
                )
                + "\n"
            )
            out.flush()
    print(f"requests={n_req} models={sorted(models)}")
    rows = [json.loads(l) for l in open("real_scores.jsonl")]
    ev = [
        (r["p_stuck"], r["label"]) for r in rows if r["label"] in ("stuck", "healthy")
    ]
    sp = [p for p, l in ev if l == "stuck"]
    hp = [p for p, l in ev if l == "healthy"]
    a = auc(sp + hp, [True] * len(sp) + [False] * len(hp))
    fp = sum(1 for p in hp if p >= THRESHOLD)
    tf = [r["testfail"] for r in rows]
    fa = auc([r["p_testfail"] for r in rows], tf) if len(set(tf)) == 2 else float("nan")
    print(
        f"REAL AUC={a:.3f} (n={len(ev)}) false-stuck={fp}/{len(hp)} feas={fa:.3f} both={len(set(tf)) == 2}"
    )
    for r in rows:
        if r["label"] == "ambiguous":
            print(
                f"  amb p={r['p_stuck']:.2f} rep={r['max_repeat']} el={r['elapsed_s']:.0f} tools={','.join(r['tools'][:4])}"
            )
    if not (fa == fa and fa >= 0.80):
        print("HARNESS BLIND")
    elif a >= 0.90 and fp <= 1:
        print("REAL VERDICT: bar met — CAVEAT DISCHARGED")
    else:
        print("REAL VERDICT: bar missed — PROMOTION NARROWED")


if __name__ == "__main__":
    main()
