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
