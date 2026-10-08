# Conformance discrepancies

Migrated from `kit/test/wire-conformance-DISCREPANCIES.md` (source bead `jev-745g`). Its prior report of no known divergences and recorded-fixture provenance is retained below; the prior check covered the Jev wire clients only, not every adapter in this harness.

| ID | Backend | Clause | Status | Review date | Prior ID | Evidence and disposition |
|---|---|---|---|---|---|---|
| DISC-001 | regex-rule | C2 | ACCEPTED | 2026-10-06 | none | A regex rule emits a choice without a probability distribution. C2 is therefore XFAIL for this adapter; the other C1-C7 clauses remain required and run. |

## Migrated report (old ID: jev-745g)

The former register reported no known divergences among askJev, askJevChoice, askJevBundle, rerankTop1, and four validators, based on `kit/test/wire-conformance.test.mjs` (16/16). That is historical evidence for those clients, not a conformance claim for new adapters.

Recorded valid Jev 1.13.0 fixtures (never typed for the old tests):
- `kit/test/fixtures/recorded-answer-rows.json` (Choice; RecordedFakeAsker pattern)
- `kit/test/fixtures/banking77-answer.json` (Choice, 77-class)
- `kit/test/fixtures/scifact-answer.json` (Noul)
- `kit/test/fixtures/sst5-answer.json` (Score + legend)
- `kit/test/fixtures/rerank-fiqa-answer.json` (Choice, 7 candidates)

Hostile fixtures were boundary mutations of those recordings: choice outside offered ids, probabilities not summing to 1, chosen-below-max, invalid scalar values/types, dropped keys, and missing answers. Synthetic data stood in only for hostile paths.

The migrated out-of-scope notes (old ID `jev-745g`) are historical: `work/jev-client` was a cutover stub with callers importing kit directly; `.omp` `webscreen` and `skill-hint` hook askers used kit entry points with the live key and had no injection seam, so their validation relied on kit.
