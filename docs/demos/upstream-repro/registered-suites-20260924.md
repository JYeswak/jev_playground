# Registered suite run (2026-09-24)

Command: `python3 scripts/run-registered-suites.py`

A missing prerequisite is a named SKIP, never a pass. The skip is probed,
not matched on the word `typesafe`. A suite is skipped for the SDK only when
its own output says `npm ci --prefix work/sdk` or `sdk-missing`. `bun test`
paths get a `./` prefix, or bun treats the path as a name filter.
`npm test` in a directory with no dependencies runs; a directory with no
`package.json` is run as `node --test <file>`. `npm ci` is named only when
`package.json` has dependencies and a lockfile.

## Fresh clone

`git clone --local`, no installs. Table:
`docs/demos/upstream-repro/registered-suites-fresh-20260924.tsv`

87 suites. 62 pass, 12 skip, 13 fail. Suite time 31.59s. Exit 1.

The 13 fails are suites that pass once `npm ci --prefix work/sdk` is
installed (the other table). Their output does not name that install, so
they are not relabeled. 12 are `work/omp-jev-*`, already filed as `jev-xhr2`
and left for pane 3. This runner does not edit those tests.

Skips: `./scripts/bootstrap-compaction.sh` (5), `npm ci --prefix work/sdk`
(4, the output named it), vendored adapter clone absent (2), vendored
`fast-jev-compaction` absent (1).

Not skipped: `work/sr-adopt/test_prereg.py`, `test_runner_gates.py`, and
`work/jev-claim-check/claim-check.test.mjs` pass with no SDK install.
`kit-guard.test.ts` passes 79/0 via `bun test ./.omp/...`.
`demos/preaction-abstention` has no `package.json`; it is run with
`node --test` and passes. The routing, whatif, and usage-shape demos have
no dependencies, so `npm test` runs and passes. `npm ci in demos/<x>` is
not a working command and is not named.

## Prerequisites installed

Same clone command, then `npm ci --prefix work/sdk` and
`./scripts/bootstrap-compaction.sh`. The adapter clone is not in a git
clone, so it is not installed. Table:
`docs/demos/upstream-repro/registered-suites-prereq-20260924.tsv`

87 suites. 85 pass, 2 skip, 0 fail. Suite time 35.42s. Exit 0.

The 2 skips are the openrouter suites:
`vendored clone upstream/typesafe-ai/system-one-adapter-python absent`.
When that clone is present and only `.venv` is missing, the named command
is `uv sync --directory upstream/typesafe-ai/system-one-adapter-python`.

## Other

Planted failure: `python3 scripts/run-registered-suites.py --selftest`
names `work/plant/fail_test.py`, and also requires the typesafe-comment
suite to pass, the no-package.json demo to pass, and the missing venv to
be a named skip.

Node: this run used v22.22.0. `README.md:26` requires Node 22.18 or newer.
`.github/workflows/gates.yml:53` pins `node-version: 20`. Not changed here.

Gate to extend, not edited: `foundation/gates.d/70-tests-registry-sync.sh`.
Measured survey time with prerequisites installed: 35.42s of suite time,
87 files. A later `KIT_GATE_EDIT` can call this command from that stage.

The earlier table `registered-suites-20260924.tsv` is the `768fcd9` text-skip
run. Pane 1 did not close on it. These two tables replace that measurement.
