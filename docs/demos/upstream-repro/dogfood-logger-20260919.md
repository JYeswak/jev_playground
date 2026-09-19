# Dogfood decision/outcome logger

## Schema

The implementation lives under `work/dogfood-logger/`.

Every decision record is JSONL with:

- `schemaVersion: 1`;
- `recordType: "decision"`;
- `decisionId` — UUID join key shared by exactly one outcome record;
- timestamp, session id, tool name;
- `argsDigest` — SHA-256 of stable canonical arguments, never raw command text;
- dcg verdict;
- Jev question set and probability object.

Every outcome record is JSONL with:

- `schemaVersion: 1`;
- `recordType: "outcome"`;
- the same `decisionId`;
- timestamp;
- `status`: `proceeded`, `cancelled`, or `failed`;
- nullable exit status and error field.

A decision may exist before its outcome. Replay reports unmatched decisions and orphan outcomes
instead of silently joining by order.

## Writer behavior

`JsonlDecisionLog` serializes appends through an internal promise tail, uses append-only file opens,
rotates after a size threshold, and catches all writer errors. Logger failures return `false`; they
never throw into the caller.

## Verification

```text
node --test work/dogfood-logger/test/logger.test.mjs
4 tests passed
```

Covered:

- joined decision/outcome fire and proceeded-false-positive rates;
- malformed records and orphan outcomes;
- 100 concurrent appends without loss;
- size rotation with multiple readable files.

The test is registered in `TESTS.md` in the same commit.

## Scope

Replay reports decision count, fire rate, joined outcome count, and false-positive rate against
`status=proceeded`. It uses `work/oracle-kit` for probability-field validation and optional AUC; it
does not infer task success from a Jev probability.

**NO-CLAIM:** this logger has not run in a live omp session. Its schema, join, writer, and replay
behavior are tested locally; it proves nothing yet about what a production hook will capture.
