# Registered suite run (2026-09-24)

Command: `python3 scripts/run-registered-suites.py`

A Run command is used only when it contains the suite's own path. A missing
Run line falls back to that file's runner. It does not borrow the next row.
A missing prerequisite is a named SKIP, and the name is a command that fixes
it: `npm ci --prefix work/sdk`, `./scripts/bootstrap-compaction.sh`, or
`./scripts/sync-docs.sh --repos-only`. Compaction is not skipped from the
path. `adapter.test.ts` passes bare.

## Fresh clone

`git clone --local`, no installs. Table:
`docs/demos/upstream-repro/registered-suites-fresh-20260924.tsv`

87 suites. 64 pass, 23 skip, 0 fail. Suite time 30.52s. Exit 0.

`compaction/test/adapter.test.ts` is PASS (7 tests, no bootstrap).
`compaction/test/hook-compact.test.ts` is SKIP `./scripts/bootstrap-compaction.sh`
because the run says it cannot find package `fast-jev-compaction`. The two
openrouter suites are SKIP `./scripts/sync-docs.sh --repos-only`.

## Prerequisites installed

Same clone, then `npm ci --prefix work/sdk` and
`./scripts/bootstrap-compaction.sh`. Table:
`docs/demos/upstream-repro/registered-suites-prereq-20260924.tsv`

87 suites. 85 pass, 2 skip, 0 fail. Suite time 32.17s. Exit 0.
`hook-compact.test.ts` passes after bootstrap. The 2 skips are the openrouter
suites, still `./scripts/sync-docs.sh --repos-only`.


## Other

Planted failure: `python3 scripts/run-registered-suites.py --selftest`
names `work/plant/fail_test.py`, and also requires the typesafe-comment
suite to pass, the no-package.json demo to pass, and the missing venv to
be a named skip.

Node: this run used v22.22.0. `README.md:26` requires Node 22.18 or newer.
`.github/workflows/gates.yml:53` pins `node-version: 20`. Not changed here.

Gate to extend, not edited: `foundation/gates.d/70-tests-registry-sync.sh`.
Measured survey time with prerequisites installed: 32.17s of suite time,
87 files. A later `KIT_GATE_EDIT` can call this command from that stage.

The earlier table `registered-suites-20260924.tsv` is the `768fcd9` text-skip
run. Pane 1 did not close on it. These two tables replace that measurement.

## Named prerequisite (jev-w1js)

The 13 suites call `work/sdk/require-installed.mjs`. A fresh clone of that
tree: 62 pass, 25 skip, 0 fail, exit 0. Those 13 are SKIP
`npm ci --prefix work/sdk`. Table:
`docs/demos/upstream-repro/registered-suites-named-prereq-20260924.tsv`

With the SDK installed, the same 13 pass (102 tests, 0 fail). A planted
`assert.equal` regression in `default.test.mjs` with the SDK installed was
FAIL, not SKIP (runner exit 1, that file rc 1). The plant was only in /tmp.

## Borrowed Run line (jev-galx, pane 3)

`hook-compact.test.ts` has no Run line. The next row's command used to run
instead, so a planted `assert.fail` in that file stayed PASS. The selftest
plants `work/plant/borrowed_test.py` with no Run line, followed by `Run: true`,
and requires that file to FAIL.
