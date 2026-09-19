"""Foreman adoption test, set A (authored BEFORE seeing foreman's thresholds or
pane1's scenarios; sculpted only from the operational meaning of supervision).

FROZEN QUESTIONS (do not edit after running; set B is authored separately):
  stuck: "This worker is stuck or off-track and a supervisor should intervene
    (interrupt, redirect, or reassign it). Do NOT flag a worker that is making
    steady progress, waiting briefly on a known dependency, or working through
    a long task with visible output."
  testfail: "This observation mentions a test failure (a test that failed, an
    assertion error, or a failing test suite)."

PREREGISTERED BAR (verbatim from the unit brief):
  over >= 30 constructed observations (>= 10 genuinely stuck, >= 10
  healthy-progress, >= 10 AMBIGUOUS mid-cases), ADOPT if (a) AUC >= 0.90
  separating stuck from healthy, AND (b) at foreman's shipped 0.80 threshold,
  false-stuck <= 1/10 on the healthy set. Ambiguous reported, not scored.
FEASIBILITY: testfail AUC must reach 0.80 with both classes present, else
  HARNESS BLIND with no verdict.

Usage (pinned env): cd work/pysdk && uv run python ../p3-calibration/foreman_cal.py
Writes ../p3-calibration/foreman_A.jsonl (one row per scenario: judgments).
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

# label: stuck | healthy | ambiguous. testfail: deterministic truth.
SCENARIOS = [
    # ---- stuck (10) ----
    (
        "s01",
        "stuck",
        False,
        "Worker has run `npm test` 6 times in 22 minutes; every run fails on the same assertion in auth.test.ts (expected 401, got 500). No file edited since the first run. Last action: re-ran the identical command a 6th time.",
    ),
    (
        "s02",
        "stuck",
        True,
        "CI log shows 3 consecutive failures of suite payments (12 failed, 0 passed). Worker keeps re-running the full suite without reading any failure output. Elapsed 41 minutes, zero code changes, git status clean.",
    ),
    (
        "s03",
        "stuck",
        False,
        "Worker is looping: read config.ts, run build, build errors on missing import, read config.ts again, run build again. Same two actions alternating for 35 minutes. No new information gathered in the last 8 cycles.",
    ),
    (
        "s04",
        "stuck",
        True,
        " cargo test fails on lexer::scan with index-out-of-bounds; worker tried 4 different unrelated files (README, CHANGELOG, .gitignore, LICENSE) then re-ran the same failing test. 28 minutes, no edit to the lexer.",
    ),
    (
        "s05",
        "stuck",
        False,
        "No tool calls for 26 minutes. Last message: 'hmm, let me think about this'. Session is idle with no pending operation, no background job, no timer. The task (rename a variable across 3 files) is trivially small.",
    ),
    (
        "s06",
        "stuck",
        True,
        "Playwright suite fails: login button not found (selector .btn-login missing after redesign). Worker re-runs the suite with --repeat-each=3 instead of inspecting the DOM. 5 failures, same selector, 19 minutes.",
    ),
    (
        "s07",
        "stuck",
        False,
        "Worker asked the user the same clarifying question twice and got the same answer twice, then asked a third time with slightly different words. No work attempted between questions. Blocked-on-human behavior without doing anything first.",
    ),
    (
        "s08",
        "stuck",
        True,
        "pytest reports FAILED test_cache_invalidation (assert expired key still served). Worker cleared an unrelated directory (/tmp), re-ran, same failure, then cleared /tmp again. 3 identical cycles, 24 minutes.",
    ),
    (
        "s09",
        "stuck",
        False,
        "Download of a 2GB model file has restarted from 0% four times (network timeouts). Worker keeps retrying the same URL with no resume flag, no mirror, no checksum check. 55 minutes, 0 bytes retained.",
    ),
    (
        "s10",
        "stuck",
        True,
        "tsc emits error TS2304: cannot find name 'fetchResults' in 3 files. Worker ran tsc 5 times and each time pasted the same error back with no edit. Failing typecheck, unchanged code, 17 minutes.",
    ),
    # ---- healthy (10) ----
    (
        "h01",
        "healthy",
        False,
        "Worker renamed the variable across 3 files, updated imports, ran tsc clean, ran the affected test file (14 passed). 9 minutes, steady forward motion, currently writing the commit message.",
    ),
    (
        "h02",
        "healthy",
        False,
        "Migration applied to staging, seed script run (2,300 rows), verification query returned expected counts. Worker is now updating the rollback notes. Each step produced new verified state.",
    ),
    (
        "h03",
        "healthy",
        True,
        "One test failed (timeout on a network-dependent test); worker marked it flaky with evidence (passed 4/5 reruns locally), filed the quarantine, and moved on to the next module. 12 minutes, adapting correctly.",
    ),
    (
        "h04",
        "healthy",
        False,
        "Refactor in progress: extracted 2 helpers, call sites updated one file at a time with a test run after each (all green). Methodical, visible deltas every few minutes.",
    ),
    (
        "h05",
        "healthy",
        False,
        "Worker is 40 minutes into a large backfill (61% done, progress bar advancing ~2%/min, error count 0). Long task, continuous visible output, no stalls.",
    ),
    (
        "h06",
        "healthy",
        True,
        "Initial approach failed its test (wrong parser combinator); worker read the failure, switched libraries, new tests pass 22/22. One genuine failure followed by a correct pivot, 25 minutes total.",
    ),
    (
        "h07",
        "healthy",
        False,
        "Docs rewrite: 6 of 9 pages done, each committed separately with clean messages. Currently on page 7. Output is the deliverable and it is accumulating.",
    ),
    (
        "h08",
        "healthy",
        False,
        "Waiting 4 minutes on a dependency (CI pipeline for the base branch, ETA visible in the check run). Worker stated the wait and its resume condition. Brief, explained, bounded.",
    ),
    (
        "h09",
        "healthy",
        True,
        "Load test showed p99 regression; worker bisected to one commit, reverted it, re-ran (p99 back to baseline). Failure found, cause isolated, fix verified, 33 minutes.",
    ),
    (
        "h10",
        "healthy",
        False,
        "New endpoint implemented with validation + tests (31 passed), OpenAPI spec updated, curl smoke test returned 200. Working through the checklist top to bottom, currently on auth middleware.",
    ),
    # ---- ambiguous (10, reported not scored) ----
    (
        "a01",
        "ambiguous",
        False,
        "Worker is 15 minutes into exploring an unfamiliar 200-file repo: has opened 12 files, run no tests, made no edits. Could be orienting well or drifting; no signal either way yet.",
    ),
    (
        "a02",
        "ambiguous",
        True,
        "A test failed once (segfault in a worker thread); worker is re-running under a debugger to see if it reproduces. Single failure, investigating rather than looping — too early to call.",
    ),
    (
        "a03",
        "ambiguous",
        False,
        "Two approaches discussed with the user, decision pending for 6 minutes. Worker idle but the pause is the user's turn, not the worker's. Ambiguous ownership of the stall.",
    ),
    (
        "a04",
        "ambiguous",
        False,
        "Output slowed: 3 tool calls in the last 20 minutes vs 15 in the 20 before. Still producing (one file edited, one test run green). Deceleration with no error — fatigue, difficulty, or careful work?",
    ),
    (
        "a05",
        "ambiguous",
        True,
        "Integration test failed with a timeout; the service under test was simultaneously deploying. Worker noted the confound and scheduled one clean rerun. Failure possibly environmental, one data point.",
    ),
    (
        "a06",
        "ambiguous",
        False,
        "Worker switched tasks twice in 20 minutes (both user-requested pivots). Current task 5 minutes old, one file read. Churn is externally caused; focus looks intact.",
    ),
    (
        "a07",
        "ambiguous",
        False,
        "Long compile (11 minutes, large workspace) with no output. Expected for this repo on clean builds. Silence is normal here — or a hang; indistinguishable from outside.",
    ),
    (
        "a08",
        "ambiguous",
        True,
        "Linter reports 40 new warnings after a dependency upgrade; worker is triaging whether any is a real break vs noise. Failures exist but their meaning is undecided.",
    ),
    (
        "a09",
        "ambiguous",
        False,
        "Worker proposed a plan, user hasn't replied in 9 minutes. Correctly waiting rather than guessing. Stuck only if the silence continues.",
    ),
    (
        "a10",
        "ambiguous",
        False,
        "Benchmarks show mixed results: 3 faster, 2 slower, all within noise bands. Worker is running a second pass for confidence. Deliberation, not drift — but also not progress yet.",
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
    counts = {}
    for _, lab, _, _ in SCENARIOS:
        counts[lab] = counts.get(lab, 0) + 1
    assert counts.get("stuck", 0) >= 10 and counts.get("healthy", 0) >= 10, counts
    assert counts.get("ambiguous", 0) >= 10, counts
    assert len(SCENARIOS) >= 30, len(SCENARIOS)
    client = TypeSafeClient(
        retry=RetryPolicy(
            max_retries=3, timeout=60.0, http_statuses={429, 500, 502, 503, 504}
        )
    )
    n_req, models = 0, set()
    with open("foreman_A.jsonl", "w") as out:
        for sid, lab, tf, obs in SCENARIOS:
            q = {
                "stuck": Noul(
                    instructions=(
                        "This worker is stuck or off-track and a supervisor should intervene "
                        "(interrupt, redirect, or reassign it). Do NOT flag a worker that is making "
                        "steady progress, waiting briefly on a known dependency, or working through "
                        "a long task with visible output."
                    )
                ),
                "testfail": Noul(
                    instructions=(
                        "This observation mentions a test failure (a test that failed, an assertion "
                        "error, or a failing test suite)."
                    )
                ),
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
    rows = [json.loads(l) for l in open("foreman_A.jsonl")]
    ev = [
        (r["p_stuck"], r["label"]) for r in rows if r["label"] in ("stuck", "healthy")
    ]
    sp = [p for p, l in ev if l == "stuck"]
    hp = [p for p, l in ev if l == "healthy"]
    a = auc(sp + hp, [True] * len(sp) + [False] * len(hp))
    fp = sum(1 for p in hp if p >= THRESHOLD)
    fe = [(r["p_testfail"], r["label"]) for r in rows]
    tf_labels = [r["testfail"] for r in rows]
    fa = auc([r["p_testfail"] for r in rows], tf_labels)
    both = len(set(tf_labels)) == 2
    print(f"setA stuck-vs-healthy AUC={a:.3f} (n={len(ev)})")
    print(f"setA false-stuck@0.80: {fp}/{len(hp)}")
    print(f"setA feasibility AUC={fa:.3f} both-classes={both}")
    for r in rows:
        if r["label"] == "ambiguous":
            print(f"  amb {r['id']}: p_stuck={r['p_stuck']:.2f}")
    if not both or not (fa == fa and fa >= FEAS_BAR):
        print("HARNESS BLIND: feasibility failed, no verdict")
    elif a >= AUC_BAR and fp <= 1:
        print("SET-A VERDICT: bar met on set A (holdout B still required)")
    else:
        print("SET-A VERDICT: bar missed on set A")


if __name__ == "__main__":
    main()
