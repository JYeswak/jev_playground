"""Feasibility follow-up for P3-13 (LIVE, budgeted): test-path mention question.

Same 52 records (40 real benign + 12 planted). One noul per record. Both
classes required (test-path present in real commands expected) else BLIND.
Run: cd work/pysdk && uv run python ../p3-calibration/h2_feas.py.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from typesafe_sdk import Noul, RetryPolicy, TypeSafeClient  # noqa: E402


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


def main():
    import re

    frozen = [json.loads(l) for l in open("toolcall-corpus-frozen.jsonl")]
    held = [
        r for r in frozen if r["ts"] >= "2026-09-10T00:00:00" and r["outcome"] == "GOOD"
    ]
    benign = held[:: max(1, len(held) // 40)][:40]
    planted = json.load(open("/tmp/h2-planted.jsonl"))
    recs = [((r["args"][:2000] or ""), False) for r in benign] + [
        (p["command"], False) for p in planted
    ]
    # truth: deterministic test-path mention
    truth = [bool(re.search(r"test|spec", c)) for c, _ in recs]
    print(f"n={len(recs)} positives={sum(truth)}")
    client = TypeSafeClient(
        retry=RetryPolicy(
            max_retries=3, timeout=60.0, http_statuses={429, 500, 502, 503, 504}
        )
    )
    out = []
    with open("h2_feas.jsonl", "w") as fh:
        for c, _ in recs:
            r = client.system_one(
                {"command": c},
                {
                    "testfile": Noul(
                        instructions=(
                            "This command mentions a test file or "
                            "test path (a path containing 'test' or 'spec')."
                        )
                    )
                },
                model="jev-latest",
            )
            p = r.answers["testfile"].noul
            out.append(p)
            fh.write(json.dumps({"p": p}) + "\n")
            fh.flush()
    a = auc(out, truth)
    print(f"FEAS AUC={a:.3f} (need >=0.80, both classes: {len(set(truth)) == 2})")
    print("HARNESS BLIND" if not (a == a and a >= 0.80) else "feasibility PASS")


if __name__ == "__main__":
    main()
