# Non-author review: behaviour-label + score-register (2026-09-20)

Level: `test` (all offline; no Jev calls). Adversarial intent throughout; defects
found are filed with fixes + planted tests in the same commit as this receipt.

## Artifact 1 — behaviour-label.mjs (6 tests, green)

- 4/40 disagreements (10.0%): CONFIRMED — re-ran `node behaviour-label.mjs 40`,
  same count. The disagreements are real disagreements.
- Attack 2 (collisions) — REFUTED as "a couple", PROVEN live: 10 colliding
  basenames (`index.ts` ×20, `measure.mjs` ×17, plus 8 more). A commit touching
  `work/omp-jev-dispatch/src/index.ts` is labelled behaviour=true "referenced by
  `work/jev-client/measure-kit.mjs`", which imports a different `index.ts`
  entirely. The 4/40 figure survives (the 4 are genuine), but every TRUE in the
  other 36 rows for a colliding basename is suspect — agreements unexamined.
- Attack 3 (missed entry points) — REFUTED completeness: `.omp/hooks/*`
  (jev-compact.ts fires on real sessions) is not in the entry list, and
  `package.json` `scripts` targets (e.g. compaction `replay`) are not read —
  while the header comment line 19 CLAIMS `scripts` is covered. Doc/code
  mismatch, the exact class this lane kills.
- Attack 1 (the rule) — PARTIAL: computable, not right. Wrong classes named:
  (a) for colliding basenames the rule ≡ the mechanical proxy it replaces
  (always true when touched); (b) interface-compatible refactors count;
  (c) runtime-read non-code files (JSON configs) are invisible to it entirely.
- Attack 4 (fourth defect) — FOUND, two: (i) the `scripts` doc/code mismatch
  above; (ii) `by.slice(0, 3)` truncates the attribution evidence, so a reader
  cannot audit which referencers carried a verdict.

## Artifact 2 — jev-score-register (13 → 15 tests, green)

- Attack 1 (canonicalise collisions) — CONFIRMED unbroken over JSON values
  (order sorted, numbers canonical, null/str distinct; BigInt/circular throw
  rather than collide — fail-closed, acceptable boundary).
- Attack 2 (third shape misfiles) — REFUTED the old behavior, FIXED: `recording()`
  and `recordingChoice()` now file `shape-mismatch: expected result.<field>
  object` for ok:true wrong-shape results, distinct from transport failures.
  Planted test added (hypothetical Score shape through both wrappers).
- Attack 3 (concurrent appends) — CONFIRMED safe: 4 processes × 25 rows,
  100/100 lines parse (POSIX O_APPEND atomicity at these row sizes). New test
  pins it; caveat row size recorded in the test.

## Ledger line

REVIEW behaviour-label + register — MIXED — twin cross-attribution proven live + scripts/.omp entry gaps + shape-mismatch fix + append-safety proven — NO-CLAIM: one reader, offline only; agreement-side contamination unquantified.
