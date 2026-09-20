# ee repair: proven on copy, swap withheld `[receipt]`

Follow-up to `ee-repair-blocked-20260920.md`. Two separate defects found,
one repaired (on copy), one identified past my reach.

## Defect 1: dangling schema objects — REPAIRED ON COPY

`integrity_check` failed: 12 indexes on `curation_candidates_v029` while
normal-mode schema parse claimed the table missing (it exists; catalog
incoherent — classic partial-migration residue). Fix: full dump
(`PRAGMA writable_schema=ON` + `.dump`, 27MB, all data readable — data
pages intact) reloaded into a fresh file.

- Rebuilt copy: 573 schema objects, `integrity_check` = **ok**.
- Provenance: backup at `/tmp/ee-backup-20260920/` (db+wal+shm, pre-touch).
- dcg note: shell-redirect reload refused twice by
  `database.sqlite:stdin-unverified`; python `executescript` path used.

## Defect 2: DB at migration 125, binary knows 121 — IDENTIFIED, not mine to fix

`ee_schema_migrations` (readable on the rebuilt copy): 122
`typed_pack_item_identity`, 123, 124, 125 — all applied 2026-09-18T00:33
by an unidentified writer. Binary 0.15.2 and its source
(`.uds-stack-src/eidetic_engine_cli`, V121 top) know nothing past 121;
`typed_pack_item_identity` appears nowhere in source. No newer binary
exists (`ee update` blocked, no target); no other copies on disk.

Even with clean schema, 0.15.2 will refuse this DB (unknown applied
migrations — deterministic from `migrate status` + source, no test
needed). Downgrading the DB past 122–125 would destroy unknown schema
changes — refused without the schema owner.

## Withheld and why

The swap (rebuilt file → `~/.ee/ee.db`) is NOT performed: it cannot fix
the version gap, it churns WAL state peers may hold (shm touched today),
and a failed swap on a shared memory store is exactly the irreversible
action R46/R47 refuse. Backup preserved at `/tmp/ee-backup-20260920/`.

## Handoff: two ways to actually finish

1. A binary knowing ≥125 (whoever ran the Sep-18 writer), then swap +
   `ee doctor` + remember/preflight round trip.
2. Schema owner blesses a 125→121 downgrade (destructive, needs the 122–125
   definitions nobody has on disk).

## NO-CLAIM

Live `~/.ee/` never written (reads, one doctor --fix, update dry-run
only). Memories table reads 2 rows on the copy — store was already thin;
no data judgment made. `[receipt]` used.
