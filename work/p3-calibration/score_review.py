"""P3-8: jev-review-style quality scores over REAL diffs (LIVE, budgeted, once).

Draw: review_draw.json (8 worse + 14 better, future-derived file-overlap
labels, author's own commits excluded). Per commit: full diff truncated to
~12k chars; Score 0-10 (expected value) + feasibility noul (touches a test
file?). One request per commit (22). Bar (preregistered in unit brief):
AUC >= 0.75 worse-vs-better; feasibility both-classes + >=0.80 else BLIND.
Run: cd work/pysdk && uv run python ../p3-calibration/score_review.py.
Writes ../p3-calibration/review_scores.jsonl.
"""

import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from typesafe_sdk import Noul, RetryPolicy, Score, TypeSafeClient  # noqa: E402

LEVELS = [
    "worthless, broken or harmful",
    "severely defective",
    "bad",
    "below average",
    "mediocre",
    "acceptable",
    "good",
    "very good",
    "excellent",
    "exemplary",
]


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
    rows = json.load(open("review_draw.json"))
    assert len([r for r in rows if r["label"] == "worse"]) >= 6, "need >=6 worse"
    assert len(rows) >= 20, "need >=20"
    client = TypeSafeClient(
        retry=RetryPolicy(
            max_retries=3, timeout=90.0, http_statuses={429, 500, 502, 503, 504}
        )
    )
    n_req, models = 0, set()
    with open("review_scores.jsonl", "w") as out:
        for r in rows:
            d = subprocess.run(
                ["git", "show", "--format=", r["sha"]],
                capture_output=True,
                text=True,
                cwd="~/Developer/jev",
            ).stdout[:12000]
            test_touch = bool(re.search(r"diff --git a/(\S*test\S*|\S*spec\S*)", d))
            q = {
                "quality": Score(
                    instructions=(
                        "Rate the quality of this code change on a 0-10 scale, "
                        "considering correctness, clarity, and whether it does what "
                        "its message claims. The diff:"
                    ),
                    criteria=LEVELS,
                ),
                "testfile": Noul(
                    instructions=(
                        "This diff touches a test file "
                        "(a path containing 'test' or 'spec')."
                    )
                ),
            }
            resp = client.system_one(
                {"subject": r["subject"], "diff": d}, q, model="jev-latest"
            )
            assert hasattr(
                resp.answers["quality"], "score"
            ), "Score missing .score field"
            assert hasattr(resp.answers["testfile"], "noul"), "Noul missing .noul field"
            models.add(resp.model)
            n_req += 1
            out.write(
                json.dumps(
                    {
                        "short": r["short"],
                        "label": r["label"],
                        "test_touch": test_touch,
                        "qscore": resp.answers["quality"].score,
                        "p_testfile": resp.answers["testfile"].noul,
                    }
                )
                + "\n"
            )
            out.flush()
    print(f"requests={n_req} models={sorted(models)}")
    rows = [json.loads(l) for l in open("review_scores.jsonl")]
    b = [r["qscore"] for r in rows if r["label"] == "better"]
    w = [r["qscore"] for r in rows if r["label"] == "worse"]
    a = auc(b + w, [True] * len(b) + [False] * len(w))
    tf = [r["test_touch"] for r in rows]
    fa = auc([r["p_testfile"] for r in rows], tf) if len(set(tf)) == 2 else float("nan")
    import statistics

    print(
        f"QUALITY AUC={a:.3f} (better n={len(b)} worse n={len(w)}) "
        f"mean better={statistics.mean(b):.2f} worse={statistics.mean(w):.2f}"
    )
    print(f"FEAS AUC={fa:.3f} n_pos={sum(tf)}/{len(tf)}")
    for r in sorted(rows, key=lambda r: r["qscore"]):
        print(f"  {r['qscore']:5.2f} {r['label']:7s} {r['short']} {r['test_touch']}")
    if not (fa == fa and fa >= 0.80):
        print("HARNESS BLIND")
    elif a >= 0.75:
        print("REVIEW VERDICT: bar met — PROMOTE")
    else:
        print("REVIEW VERDICT: bar missed — RULED_OUT")


if __name__ == "__main__":
    main()
