# Unit 1 ee repair: BLOCKED `[receipt]`

Round trip unmade. Recall half dead, write half dead, repair surfaces
exhausted. Everything below is a command run, exit code unpiped.

## Chain (in order)

1. `ee doctor --fix-plan --json` → 5 issues, 4 fixable. Blocker:
   EE-E040 migration_drift (applied migration 122 drifted); others are
   warnings (embedding fallback, stale index, NUMA pin).
2. `ee doctor --fix --json` → rc=0, 1 action (index rebuild). Drift
   persists on re-check.
3. `ee migrate status` → up-to-date (compiled 121, 0 pending) — yet the
   DB carries migration 122, which the binary cannot even name
   (`expected <unknown>`). A newer writer touched this DB.
4. `ee migrate run` → rc=3, same EE-E040.
5. `ee update --dry-run` → blocked, no target (0.15.2 current).
6. `ee remember --level procedural` → **rc=3**, EE-E040. Writes dead.
7. Direct sqlite inspect of `~/.ee/ee.db` → `malformed database schema
   (idx_curation_candidates_workspace)` — corruption beneath the drift.
   Old binaries present (`ee.backup-20260724-0.13.0-preupgrade`) — the
   store has history I will not hand-edit.

## Verdict

BLOCKED. No loop gets built on this store tonight: a memory that cannot
be written to is not a component, and hand-repairing a corrupt shared
memory DB is out of scope and unsafe. Fresh-workspace init would sidestep
history rather than repair recall — not attempted, stated.

## NO-CLAIM

Did not touch `~/.ee/` contents (reads + documented mutators only).
`[receipt]` used.
