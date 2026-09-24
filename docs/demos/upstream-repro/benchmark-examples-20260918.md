# Reproduction: typesafe-ai-benchmark documented examples, run here

Pane 3 (muse), 2026-09-18. Vendored clone `upstream/iammrduncan/typesafe-ai-benchmark`
at pinned SHA — read and executed only, never edited (worktree verified clean;
`node_modules/` installed with `--no-save --no-package-lock` and is gitignored).

## What was run

```bash
npm run examples          # offline, deterministic fixtures, no key — 7/7 execute
```

`npm run examples:live` needs `CEREBRAS_API_KEY`, which this lane does not hold
(Infisical project is TYPESAFE-only). Live arms reported as unrunnable-here, not
as a defect. Note in their favor: live keys come from environment
(`process.env.CEREBRAS_API_KEY` in `packages/api/examples/run.ts:17`), not
exclusively from a `.env` file — no key material needs to touch disk.

## Against the documented examples

All seven documented workflows (E1–E7, `docs/examples.md`) execute at HEAD:
status 200 on every one, decisions recorded, report at
`/tmp/typesafe-examples-stub-results.json` (outside the repo). 31 planned
provider calls, $0.266 conservative ceiling stated.

## Upstream report (no patch — their file, their fix)

**Stale run instructions — the same defect class we caught in our own README
twice today.** `docs/examples.md` "Run and interpret" gives `npm run examples`
with no `npm install` first. Reproduced on a clean checkout state: `node
--import tsx` fails with `ERR_MODULE_NOT_FOUND: Cannot find package 'tsx'`
because `node_modules/` was never installed. Reproduction: delete
`node_modules`, run `npm run examples`, observe the ModuleLoader error.

- **Mechanism:** `packages/api` has no vendored toolchain; `tsx` resolves from
  the workspace `node_modules`, which only `npm install` creates.
- **Suggested fix (one line):** prefix the run block with `npm install`
  (workspace root), or document it as step zero in
  `packages/api/examples/README.md` alongside the existing CLI instructions.
- **Not a code defect:** after install, 7/7 green. The code is fine; the on-ramp
  is missing its first step.

## Rows committed — 2026-09-24

`/tmp/typesafe-examples-stub-results.json` copied byte-identical (`cmp`) to `work/tmp-rescue/typesafe-examples-stub-results.json`, sha256 `95182972a287f0160954e6b7398be31162ad839500138105522e220ac20710dc`. The `/tmp` copy was not deleted.
