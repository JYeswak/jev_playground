# P2 — queue of 2: land the mines on main, then make them readable by a stranger

The representative re-run is verified and the public page now carries it. **Your measurement
refuted my pre-registered prediction and strengthened the finding** — that is the best outcome
available from a re-run, and it only counted because the seed, the sha, and the sample size were
committed before you looked at any result.

**9 commits are ahead of `main` and unshipped**, including both corpus mines. By this lane's own
standard they do not exist yet.

## Unit 1 — land it

Merge `work/cass-dig-vs-invent` to `main` via PR. Before opening: `foundation/gates.sh`,
`scripts/lane-status.sh`, `scripts/pin-liveness.sh`, `scripts/denominator-sweep.sh` — all four,
**exit codes unpiped, at your tip, not mine.** No force-push, no history rewrite.

The PR body should lead with what a reader gets, not what we did: the dig-vs-invent ruling
replicated on a defensible frame, the full mail census, the commit-level finding.

## Unit 2 — one page for the three corpora

`docs/demos/upstream-repro/corpus-coverage-20260920.md`, stranger-readable, no lane jargon:

| corpus | size | mined | what it told us |
|---|---:|---|---|
| this repo's commits | ~1,046 | 100% | the verification level is decorative — `oracle` never touched a test file |
| agent-mail | 6,510 | 100% | **58 of 3,135 ack-required messages were ever acked (1.85%)** |
| CASS | 5,181,931 | 2.32%, now characterised + replicated at n=1,000 convs | dig beats invent overall; loses badly on absence-claims |

Each row links its receipt. Then the part that makes it worth reading: **what a person running
agents should do differently.** The 1.85% ack rate is the sharpest thing we measured tonight and
nobody outside this lane knows it — it says our coordination protocol asks for something it
almost never gets.

State the limits in the same breath: all three corpora are **live-monotonic** (commits moved
1,043 → 1,046 in thirty minutes), so every count carries an as-of date, and CASS remains 97.68%
untouched — characterised, not mined.

## Then

`br ready`, claim the highest-priority bead you did not author. If the frontier is still the
blocked epic, take the highest-value artifact you did not write and review it.

`[receipt]` for result-recording commits. Exit codes unpiped. Commit on create.

`ntm --robot-send=jev --panes=1 --msg="CALLBACK-P2-<UNIT>-<DONE|BLOCKED>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."`
