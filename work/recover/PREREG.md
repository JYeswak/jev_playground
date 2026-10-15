# N4 recover rule — preregistration (jev-n4-recover-error-rule-1grh)

Committed before any scoring. Status: floor record + design freeze for this
pilot receipt on the synthetic N0 fixture.

## Estimand (labelled OBSERVATIONAL)

Per error class, next-call success rate in the cohort whose actual next
action agreed with rule R versus the cohort whose next action did not,
beside the published constants (.853 / .854 next-call success). Agreement
is observed from rows only; success "under the rule" is never imputed for
rows where the agent did not follow R (such rows are NOT_IDENTIFIABLE for
the rule effect, never assigned).

Rule R under test:

- bash timeout / network / lock errors -> retry the call.
- bash syntax / not-found / permission errors -> change the call.
- edit stale_tag -> re-read before acting.

Report per class: n(agree), n(disagree), success rate in each, the
agree-minus-disagree difference with an exact 95% interval, and the
constant. No superiority claim is made from observational agreement
(agreement is confounded with error easiness); differences are descriptive
flags only.

## Numeric margin

A class-level agree-minus-disagree difference of at least 0.10 is flagged
as worth following up. The margin is a descriptive flag, not a bar: nothing
passes or fails on it, and no KEEP/KILL verdict is derived.

## Minimum n per error class

10 rows in the smaller of the agree/disagree cohorts. A class below that
reports NOT_POWERED with its raw counts, never a rate comparison.

## Sessions: dev vs held

- Dev: `work/fleet-schema/fixtures/sessions.jsonl` (synthetic N0 fixture,
  38 rows, 3 sessions) — the only labelled rows available.
- Held: none yet. The fixture is too small to split; a future fleet-session
  held set is separate work, not claimed here.

## Model arms

None in this bead. No model calls, no keys, no network. A future model arm
would need its own design, max calls, and max USD recorded here first;
`rule.py` refuses to score any arm not named in this section.

## Frozen inputs

- `work/fleet-schema/task.json` (pointer; schema_version 1).
- `work/fleet-schema/fixtures/sessions.jsonl` as committed at scoring time
  (sha256 recorded in RECEIPT.md; any byte change voids this preregistration).

## Amendment v2 (2026-10-15, committed before any v2 scoring)

Supersedes the v1 "Held: none yet" section only; all v1 design (estimand,
margin 0.10, min_n 10, no model arms, frozen-inputs rule) stands unchanged.

### Task-file contract

`rule.py` reads N0's task file (default
`work/fleet-schema/task.json`) for schema_version, as_of, window_days and
the fixture path (resolved relative to the task file's directory). A
missing task file, unknown schema_version, or missing fixture refuses with
nonzero exit and no score. The task identity (as_of, window_days, fixture
sha256) is recorded in every report; rows never come from a bare --rows
path without the task envelope.

### Session split (dev vs held)

Sessions ordered by (timestamp, id); dev = first two sessions, held = the
rest. On the current 3-session fixture that is dev {a, b}, held {c}. The
rule is mechanical, not fitted: it may not be re-cut after seeing results.
Cohorts are reported separately for dev and held; the min_n gate applies
within each half. Expected on current data: NOT_POWERED everywhere (zero
R-class episodes in fixture); the split machinery itself is the deliverable
under test, with honest underpowered output.

## Amendment v3 (2026-10-15, committed before any v3 scoring)

Receipt self-verification: `rule.py --json` first recomputes the RECEIPT
machine block from the answers file and compares field-by-field; on any
mismatch it prints the reason to stderr and exits 2 with no score output
(fail closed on drifted receipt). A missing machine block skips
verification with `receipt_unverified` noted (bootstrapping must remain
possible). V1 design/MIN_N/margin/model-arm rules all stand.
