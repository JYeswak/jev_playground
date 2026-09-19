# tool_call ground-truth corpus: 216k decisions mined, join yield 36.8%, error prevalence 3.95%

Pane 3 (muse), 2026-09-19. Zero API calls. Harness: `work/p3-calibration/mine_decisions.py`;
frozen corpus `work/p3-calibration/toolcall-corpus-frozen.jsonl` (7,846 rows,
every 10th time-ordered joinable row); full 216k-row `decisions_full.jsonl.gz`
left uncommitted (10MB) — reproducible via the script. ripwire exemplar checked
first (weak match: single-transcript pairing vs multi-file decision join, stated).

## Fail-open verified, not inherited (dcg-guard.ts:599-610)

Infrastructure failure + non-block classification returns `undefined` (= allow):
fail-open CONFIRMED. Exit 1 without a blocking decision still blocks (:615-617).
The UNVERIFIED fail-closed claim in `.flywheel/hook-certification-PROPOSED.toml:81-85`
must not be relied on. Same-origin evidence counted once (this check, not the brief).

## Extraction (both spellings)

Decision rows: `customType=com.zeststream.omp-dcg-bridge.decision.v1`,
payload exactly `{kind, toolCallId}` — no command (conductor correction
absorbed; BLOCKED would have been correct). Spaced `"kind" :` matches ZERO
decision rows; other spaced hits are non-decision customs. Counts: 216,507
decision rows (11,727 files); kinds occur ONLY as `dcg_allow` 215,219 and
`dcg_block` 1,288 — no unknown/deny kinds logged, so the "skip what dcg already
blocks" constraint IS enforceable (blocked = the 1,288 rows), with the caveat
that fail-open timeouts may allow WITHOUT logging (unverifiable from data).

## Join yield (stated explicitly)

Of 216,507 decisions, 79,743 resolve to a command AND an outcome (36.8%).
The 63.2% miss is ONE mechanistic class, not random loss: 136,718/136,764 miss
tids (99.997%) are `js-bash-<uuid>` — a foreign id namespace with no transcript
mapping (no toolCall part, no execution_start, no result row carries it
anywhere in session files). Consequence, stated as a finding: history can
recover barely a third of decisions; the logger should capture command text at
decision time (pane 2's extension already does).

## Outcome predicate (verbatim)

BAD iff the matching toolResult has isError true, OR any of the next 3 user
messages matches /(revert|undo that|you broke|not what I asked|wrong
command|stop doing|that broke|start over|didn't work|did not work)/i.
GOOD iff result exists, isError false, no revert signal. Blocked counted,
never scored. A laxer version (bare failed/wrong/stop) put 59k of 62k BAD
through coordination chatter ("revision, not revert", "repair the gate-runner
FAIL") — demonstrated with verbatim examples, WITHDRAWN, not reported.

## Prevalence (loud)

On joinable allowed commands (n=78,455): isError rate **3.95%** (3,098).
Frozen sample: 4.01% (315/7,846) — representative. True harm is strictly below
that (benign errors: grep-no-match etc.) and unmeasured without human review.
Against the 0.1% kill line: **the surface is NOT killed** — machine-observable
badness exceeds it ~40x; even if only 1-in-40 errors mattered, it would still
clear. Revert-signal prevalence is not reported (predicate invalid on
coordination traffic).

## Frozen split (time-ordered)

Boundary 2026-09-10T00:00:00Z. Older half: 36,955 (err 4.3%) = train/inspect.
Newer half: 41,500 (err 3.6%) = held-out. Stable across the cut.

## NO-CLAIM

Transcript-derived outcomes are a proxy for harm, not harm: isError ⊃ real harm,
revert-signal withdrawn as confounded, and the js-bash two-thirds are
unobservable — the corpus measures the joinable third, stated throughout.
