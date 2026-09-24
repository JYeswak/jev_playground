# Registered suite run (2026-09-24)

Command: `python3 scripts/run-registered-suites.py`

Clean clone: `git clone --local` of this repo, then the command with that
clone as the argument. README bootstrap is the clone itself (`README.md:20`).
Compaction's extra bootstrap is a named SKIP, not a pass. No key.

Result table: `docs/demos/upstream-repro/registered-suites-20260924.tsv`

87 tracked first-party suites. 47 pass, 40 skip, 0 fail. Wall time 10.96s.
Exit 0.

SKIP is a missing prerequisite, never a pass: `npm ci --prefix work/sdk` (26;
a suite whose first 4000 bytes mention typesafe, and the clone has no SDK
install), `./scripts/bootstrap-compaction.sh` (5), `npm ci` in three demo
directories (8), vendored `fast-jev-compaction` absent from a fresh clone (1,
`probes/fast-jev-probe.mts`). No suite under `work/sr-adopt/` failed.

Planted failure: `python3 scripts/run-registered-suites.py --selftest` names
`work/plant/fail_test.py`. The planted suite is a fail. The harness exits 0
only when that path is the failure.

Node: this run used v22.22.0. `README.md:26` requires Node 22.18 or newer.
`.github/workflows/gates.yml:53` pins `node-version: 20`. Not changed here.

Gate to extend, not edited: `foundation/gates.d/70-tests-registry-sync.sh`.
It enumerates this set and only checks registration. Measured runtime of the
survey it would wrap: 10.96s on a clean clone, 87 files. A later
`KIT_GATE_EDIT` can call this command from that stage. This commit does not.
