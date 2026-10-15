# N4 recorded answers provenance (jev-n4-recover-error-rule-1grh)

`answers-observed.jsonl` freezes the observed error episodes scored from the
synthetic N0 fixture. No model arms exist; no Jev calls were made.

- Source rows: `work/fleet-schema/fixtures/sessions.jsonl`, sha256
  `37f802e49811b4d9051a203e57eb99aaa8f48bdffd74edc3eacb3bec06f57258`
  (38 rows, 3 sessions; N0 task `work/fleet-schema/task.json`).
- Generation (deterministic, no randomness): `score_rows` from
  `work/recover/rule.py` over the source rows, episodes numbered `ep-001…`
  in row order with stable id, tool, class, action, session, agree, next_ok.
- Alignment: 2 episodes (ep-001 bash/change/next_ok true in
  synthetic-session-c; ep-002 task/unclassified/next_ok null in
  synthetic-session-c). Zero R-class episodes on this fixture.
- Privacy: rows carry classes and outcomes only; no raw command text, no
  transcripts, no keys. Safe to commit.
- Contract: `kit/contracts/recover.json` (family recover, rule-type
  question, advisory surface, zero-call budget — nothing is served).
- Recompute: `test_rule.py` Reloads this file and asserts the RECEIPT
  machine block (counts, empty cohorts, unclassified 2) within exact
  equality; any drift FAILs. Receipt numbers never come from live runs.
