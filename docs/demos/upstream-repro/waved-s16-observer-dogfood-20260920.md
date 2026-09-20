# §16 observer dogfood: FAIL — the shipped observer cannot fire (2026-09-20)

Level: `live` (4 omp sessions) + `test` (bun repro).

## What ran

- Dogfood session on omp-test (`--no-extensions -e work/.../observer.mjs -e dcg-tool-bridge.ts`,
  3 real bash calls): bridge 3 rows, observer **0 rows**.
- Control with the deployed lab copy (`extensions/omp-jev-observer.ts`): **2 observer rows**.
  The `-e` mechanism and `.mjs` loading both work (trivial `.mjs` probe: 1 row).
- Import chain under the loader works (probe: `recordScore` + `createSystemOneClassify`
  both `function`).

## Defect (file:line)

`work/omp-jev-observer/src/observer.mjs` calls `safeAppend` at lines 71, 88, 91
(and 61 inside default loggers). `safeAppend` is **defined nowhere in the package**
(grep over `src/` + `test/`). First tool_call → ReferenceError → outer catch
(line 93) → `undefined`. Deterministic total silence, reproduced under bun
(factory ok, handler yields 0 rows). The lab's n=1 claim ran against the older
deployed copy, not this tree — no shipped-tree run has ever produced a row.

## Consequences for the section

Co-presence and id-join are unmeasurable until this is fixed: 0 observer rows
against 3 bridge rows, 0/0 joins. The register wiring (`classify-systemone.mjs`)
was not reached live and is not implicated.

## Next command (FAIL carries it)

Define `safeAppend(pi, type, data)` in `observer.mjs` (or inline `pi.appendEntry`
in try/catch like the lab copy), add a test invoking the default-export handler
with a fake pi asserting ≥1 row (the current suite never calls it — that is how
this shipped), redeploy, and re-run this section's dogfood session.

## NO-CLAIM

Four sessions, one machine; the bun repro isolates the defect to the shipped file
independent of omp. I did not fix the sibling's package; the fix is one helper.
Claim stub `waved-s16-claim.md` stands as the section claim.
