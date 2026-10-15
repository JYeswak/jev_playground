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
