"""Foreman adoption test, set B — authored AFTER set-A ran and the bar held.

Rules of this file: question strings copied VERBATIM from foreman_cal.py
(frozen); bar constants identical; scenarios all-new, deliberately harder and
less caricatured than set A (which separated perfectly at AUC 1.000 and is
therefore suspect as a measure). Reads foreman_A.jsonl only for the combined
report; never edits set A.

Usage: cd work/pysdk && uv run python ../p3-calibration/foreman_holdout.py
Writes ../p3-calibration/foreman_B.jsonl, prints combined verdict.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from typesafe_sdk import Noul, RetryPolicy, TypeSafeClient  # noqa: E402

THRESHOLD = 0.80
AUC_BAR = 0.90
FEAS_BAR = 0.80

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

SCENARIOS = [
    # ---- stuck (10): busy-looking, plausible, failing ----
    (
        "s11",
        "stuck",
        False,
        "Worker has tried 5 different fixes for a flaky deploy in 50 minutes (env var, region, instance size, retry count, timeout). Each attempt changed something real and each failed differently. Nothing has been measured twice; it is thrashing across the solution space, not converging.",
    ),
    (
        "s12",
        "stuck",
        True,
        "Unit tests fail on 3 unrelated modules after a merge. Worker has spent 30 minutes reformatting code and fixing lint warnings in files the failures do not touch. The failing assertions remain unread.",
    ),
    (
        "s13",
        "stuck",
        False,
        "Worker is editing vigorously (14 files touched in 25 minutes) but git diff shows only whitespace and import reorderings; the reported bug reproduces identically. Motion without progress.",
    ),
    (
        "s14",
        "stuck",
        True,
        "E2E fails at checkout with a 500 from the payments mock. Worker rebuilt the frontend bundle 4 times and cleared node_modules twice. The mock server config — the only thing between the test and green — unopened.",
    ),
    (
        "s15",
        "stuck",
        False,
        "Two panes are editing the same file; each keeps overwriting the other's fix and re-running the check, which alternately passes and fails. 40 minutes, three overwrite cycles, no coordination message sent.",
    ),
    (
        "s16",
        "stuck",
        True,
        "Benchmark regressed 18%. Worker has profiled 6 unrelated hot paths, all flat. The one commit in the window (a serialization change on the request path) has not been examined.",
    ),
    (
        "s17",
        "stuck",
        False,
        "Worker keeps asking for 'the failing command' in slightly different words although the log with the exact command was pasted twice already. Reading without absorbing, 20 minutes, 4 repeated questions.",
    ),
    (
        "s18",
        "stuck",
        True,
        "Migration test fails: foreign key violation on seed data. Worker regenerated the seed 3 times with the same generator that produced the violation, expecting different data. Same cause, same effect, third attempt running.",
    ),
    (
        "s19",
        "stuck",
        False,
        "Cache hit rate dropped to 12%. Worker raised the cache size twice and restarted the service twice; the eviction log (showing a hot-key pattern from one new endpoint) unread. Treating a workload change as a capacity problem.",
    ),
    (
        "s20",
        "stuck",
        True,
        "Snapshot tests fail across 9 files after a dependency bump. Worker updated 4 snapshots by hand to match the new (wrong) output instead of asking why the output changed. Baking the bug into the goldens.",
    ),
    # ---- healthy (10): slow, sparse, or failure-touched but sound ----
    (
        "h11",
        "healthy",
        False,
        "Single 55-minute compile-test cycle on a huge monorepo; worker used the wait to review the diff twice and found a real issue before the results landed. One cycle, well spent.",
    ),
    (
        "h12",
        "healthy",
        True,
        "Nightly suite failed on 2 tests; worker confirmed both fail on main without their branch (pre-existing), linked the upstream issue, moved on. Correct triage in 11 minutes.",
    ),
    (
        "h13",
        "healthy",
        False,
        "Worker has produced no tool calls for 12 minutes — writing a design doc the user explicitly asked for before any code. The deliverable is prose and it is growing (visible in the draft).",
    ),
    (
        "h14",
        "healthy",
        True,
        "Fuzz test found a crash; worker minimized the input (200KB to 40 bytes), filed it with the trace, added a regression test. A failure converted into an asset in 29 minutes.",
    ),
    (
        "h15",
        "healthy",
        False,
        "Deploy is gated on a teammate's review; worker prepared the rollout plan, the rollback commands, and the monitoring queries while waiting. Blocked time converted to readiness.",
    ),
    (
        "h16",
        "healthy",
        True,
        "Staging deploy failed (bad env var, worker's own typo). Fixed in 2 minutes, redeployed green, added the var to the deploy checklist so it cannot recur. Fastest possible failure loop.",
    ),
    (
        "h17",
        "healthy",
        False,
        "Worker is deleting code: removed a deprecated module (1,400 lines), all dependents migrated, full suite green. Negative diff, positive progress, 38 minutes.",
    ),
    (
        "h18",
        "healthy",
        True,
        "Canary analysis flagged elevated errors; worker paused the rollout at 5%, confirmed the errors predate the change (same rate on baseline), resumed. A scare handled by the book in 16 minutes.",
    ),
    (
        "h19",
        "healthy",
        False,
        "Three-day estimate task, day one: worker built the fixture harness and 40 test cases before touching implementation. No product code yet; the scaffolding is the progress.",
    ),
    (
        "h20",
        "healthy",
        False,
        "Pairing session: worker drove for 20 minutes while the user watched, narrating each step; now the user drives while the worker reviews. Sparse tool calls by design, engagement high.",
    ),
    # ---- ambiguous (10) ----
    (
        "a11",
        "ambiguous",
        False,
        "Worker switched from REST to GraphQL mid-task after reading a blog post, 30 minutes in. Genuine insight or shiny-object detour? The old path was working.",
    ),
    (
        "a12",
        "ambiguous",
        True,
        "Two tests fail intermittently (roughly 1 in 4 runs). Worker is collecting 10 samples before concluding anything. Disciplined or stalling? Depends on what the samples show.",
    ),
    (
        "a13",
        "ambiguous",
        False,
        "Velocity halved after lunch across every metric, no errors anywhere. Human afternoon, harder problem, or lost thread? No evidence either way.",
    ),
    (
        "a14",
        "ambiguous",
        False,
        "Worker proposed deleting the feature instead of fixing it, with a reasonable cost argument. Punt dressed as judgment, or judgment? Needs the user's call.",
    ),
    (
        "a15",
        "ambiguous",
        True,
        "A test fails only when the full suite runs, passes in isolation. Worker is bisecting suite order effects. Realistic investigation of a real confound — or a rabbit hole; hour one.",
    ),
    (
        "a16",
        "ambiguous",
        False,
        "Worker reverted a week's work on review feedback and restarted. Painful but possibly correct; no way to tell until the replacement takes shape.",
    ),
    (
        "a17",
        "ambiguous",
        True,
        "Coverage dropped 4 points after a refactor with zero test failures. Worker is deciding whether the dropped lines need tests or were dead code. The failure is informational; the response is pending.",
    ),
    (
        "a18",
        "ambiguous",
        False,
        "New dependency added for a trivial utility (left-pad class of decision). Worker is defending it in review rather than working. Stubbornness or justified taste? Small stakes, real signal about judgment.",
    ),
    (
        "a19",
        "ambiguous",
        False,
        "Worker went quiet for 18 minutes after the user criticized the approach. Thinking, sulking, or working offline in another checkout? First silence of the session.",
    ),
    (
        "a20",
        "ambiguous",
        True,
        "Fuzzing found nothing in 2 hours of compute. Worker proposes stopping. Correct call on diminishing returns, or giving up before the payoff? The budget says stop; instinct is uneasy.",
    ),
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
    client = TypeSafeClient(
        retry=RetryPolicy(
            max_retries=3, timeout=60.0, http_statuses={429, 500, 502, 503, 504}
        )
    )
    n_req, models = 0, set()
    with open("foreman_B.jsonl", "w") as out:
        for sid, lab, tf, obs in SCENARIOS:
            q = {
                "stuck": Noul(instructions=STUCK_Q),
                "testfail": Noul(instructions=TESTFAIL_Q),
            }
            r = client.system_one({"observation": obs}, q, model="jev-latest")
            models.add(r.model)
            n_req += 1
            out.write(
                json.dumps(
                    {
                        "id": sid,
                        "label": lab,
                        "testfail": tf,
                        "p_stuck": r.answers["stuck"].noul,
                        "p_testfail": r.answers["testfail"].noul,
                    }
                )
                + "\n"
            )
            out.flush()
    print(f"requests={n_req} models={sorted(models)}")
    rows = [json.loads(l) for l in open("foreman_A.jsonl")] + [
        json.loads(l) for l in open("foreman_B.jsonl")
    ]
    for name, subset in [("A", rows[:30]), ("B", rows[30:]), ("A+B", rows)]:
        ev = [
            (r["p_stuck"], r["label"])
            for r in subset
            if r["label"] in ("stuck", "healthy")
        ]
        sp = [p for p, l in ev if l == "stuck"]
        hp = [p for p, l in ev if l == "healthy"]
        a = auc(sp + hp, [True] * len(sp) + [False] * len(hp))
        fp = sum(1 for p in hp if p >= THRESHOLD)
        tf = [(r["p_testfail"], r["testfail"]) for r in subset]
        fa = auc([p for p, _ in tf], [l for _, l in tf])
        print(
            f"{name}: AUC={a:.3f} (n={len(ev)}) false-stuck={fp}/{len(hp)} feas={fa:.3f}"
        )
        amb = [(r["id"], r["p_stuck"]) for r in subset if r["label"] == "ambiguous"]
        print(
            f"  amb range: {min(p for _, p in amb):.2f}-{max(p for _, p in amb):.2f} "
            + " ".join(f"{i}={p:.2f}" for i, p in amb)
        )
    # combined verdict on the preregistered bar
    ev = [
        (r["p_stuck"], r["label"]) for r in rows if r["label"] in ("stuck", "healthy")
    ]
    sp = [p for p, l in ev if l == "stuck"]
    hp = [p for p, l in ev if l == "healthy"]
    a = auc(sp + hp, [True] * len(sp) + [False] * len(hp))
    fp = sum(1 for p in hp if p >= THRESHOLD)
    if a >= AUC_BAR and fp <= 2:
        print("COMBINED VERDICT: bar met (AUC>=0.90, FP<=2/20)")
    else:
        print("COMBINED VERDICT: bar missed")


if __name__ == "__main__":
    main()
