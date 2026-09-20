# User-roots verdict CORRECTED + how our skills qualify, final (2026-09-20)

## Correction first

My closeout receipt claimed "user-config roots parse but yield nothing."
That verdict was WRONG — my test declared skill dirs (`.../focused-fix`)
where the mechanism expects collection dirs (`.../skills`). Re-tested
properly per his README/docs (`roster-discovery.md`, `config-contract.md`):

- User root = collection dir (1 skill): discovered as `configured.<hash>`,
  ranked #1 live (fits 0.89). WORKS.
- User root = 6-skill collection: `focused-fix` #1 (fits 0.88). WORKS.
- User root = whole `~/.claude/skills` (500+ mixed entries): empty-roster,
  all unverified. FAILS — likely entry limits or mixed-content poisoning;
  bounded open question, not pursued (curated subsets are better practice
  anyway and are proven).

## How our skills qualify (tested end to end, live Jev calls)

1. Skills must be `<name>/SKILL.md` layout (ours mostly are; flat `.md`
   files are `unsupported-layout`, correctly ignored).
2. Declare the COLLECTION dir (not skill dirs) in project `.sr/config.toml`
   (`roots=['custom']`) or user config (`roster.roots=[abs path]`).
   Both paths verified working.
3. `sr rank --context ... --allow-network` suggests them (reported
   `unverified` = honest state per his README, not a block).

Measured: `focused-fix` #1 (0.88/0.96/0.97, conf 0.95), `phish-guard` #1
(0.92/0.98/0.99, conf 0.98) on matching tasks — discrimination proven,
verdict USEFUL. Repeat spend identical pre-cache; post-live ranks hit.

## Machine state

No user config present (removed after each test). Ledger missing (restored).
Only inert orphan `-shm`/`-wal` remain. Installed `sr` untouched (pure
`0e61cc6` source build).

## Ledger line

USE user-roots — CORRECTED — collection dirs rank, skill dirs do not;
whole-library scale open — NO-CLAIM: mechanism inferred from behavior +
docs, not source proof; unfilable per native-binary rule.
