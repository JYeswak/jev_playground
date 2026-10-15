# N4 recover rule receipt (jev-n4-recover-error-rule-1grh)

Lane: offline, synthetic N0 fixture only. No model calls, no keys, no network.
Date: 2026-10-15. Estimand throughout: OBSERVATIONAL (agreement cohorts).

## Commands (exact)

```
python3 -m unittest work.recover.test_rule -v  # 24 tests OK
python3 work/recover/rule.py --json            # rc=0, stderr empty
```

## Fixture input

- `work/fleet-schema/fixtures/sessions.jsonl` (38 rows, 3 synthetic sessions).
- PREREG `work/recover/PREREG.md` committed before scoring (commit 7069d217).

## Cohort result

No error episode in the fixture falls into a rule-R class (bash
timeout/network/lock/syntax/not-found/permission, edit stale-tag):

- `cohorts`: {} — every class NOT_POWERED by absence, not by small-n.
- `unclassified_errors`: 2 — bare `false` exit-code-1 (no class text) and
  a `task`-tool error (R covers bash/edit only).
- Constants beside cohorts: .853 / .854 next-call success. With zero
  classified episodes no rate comparison is computed or claimed.

## Planted negatives (in test_rule.py, all passing)

- Identical retry after a timeout/network class is not flagged.
- Identical retry after `command not found` is flagged.
- `estimate_effect` raises Refused NOT_IDENTIFIABLE (no imputation).

## Surface

No surface turned ON by this change (offline analysis only); AC4 vacuous.

## NO-CLAIM

Threshold/cohort machinery only. Not a rule-quality verdict, not
evidence any error class should be retried or changed in production,
and not a substitute for fleet-session measurement with real labels.

## Run v2 (PREREG amendment v2, task contract + session split)

- Command: `python3 work/recover/rule.py --json` -> rc=0 (task envelope
  `work/fleet-schema/task.json`, as_of 2026-10-04T00:48:27Z, window 14 d,
  fixture sha256 `37f802e49811b4d9051a203e57eb99aaa8f48bdffd74edc3eacb3bec06f57258`).
- Split: dev {synthetic-session-a, synthetic-session-b}, held
  {synthetic-session-c} (mechanical first-two rule, PREREG v2).
- `cohorts_dev`: {} — `cohorts_held`: {} — zero R-class episodes anywhere
  in fixture; unclassified 2, unmarked 0. Both halves NOT_POWERED by
  absence. No comparison computed or claimed.
- Unit suite: 27/27 (24 v1 + task-missing refusal, task resolution,
  deterministic split).

## Run v3 (session isolation + edit-text classification)

- Session-partitioned joins: trailing failures take no next action;
  duplicate call IDs across sessions stay independent (both tested).
- Edit errors classify from result text (stale_tag surfaces there), not
  call arguments.
- Fixture re-run rc=0: split dev{a,b}/held{c} unchanged; cohorts_dev {}
  + cohorts_held {} (still zero R-class rows); unclassified 2, unmarked 0.
- Unit suite: 29/29.

## Run v4 (re-read agreement)

- `next_action_kind` recognizes edit -> same-file read as `re-read`
  (unrelated read stays `change`); end-to-end stale-tag tests both ways.
- Unit suite: 31/31. Fixture re-run rc=0 unchanged.
