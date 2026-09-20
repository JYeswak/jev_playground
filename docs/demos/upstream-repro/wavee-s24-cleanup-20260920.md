# §24 infisical placeholder cleanup — PASS (2026-09-20)

Level: `test` (static hunt + error-path run, no key).

## Hunt

`projectId=<id>` across work/, docs/, scripts/, foundation/, probes/,
compaction/, .omp/, TESTS.md, AGENTS.md, README.md: exactly two hits, both the
known defect from the Pass 6 notes — `scripts/jev-probe.mjs:38` and
`README.md:700`. `<your-sessions.jsonl>` in `scripts/quickstart.sh:340-341` is a
genuine user-supplied-path parameter, not an infisical leftover; left alone.
Hits inside `real-allowed.json` are recorded real commands, not ours to edit.

## Fix

Both replaced with the working one-liner
(`--projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba`, flags otherwise untouched).

## Live row (P7)

Keyless run: `ERROR no key in env. Run under: infisical run
--projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba --env=prod -- node
scripts/jev-probe.mjs`, exit 2. The error path now injects the working command.

## Ledger line

SECTION 24 infisical placeholder cleanup — PASS — 2/2 leftovers replaced (`jev-probe.mjs:38`, `README.md:700`), error path exit 2 with working one-liner — NO-CLAIM: tree-wide grep only; corpus literals untouched by design.
