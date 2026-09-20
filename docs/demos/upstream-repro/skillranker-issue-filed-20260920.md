# Upstream filing: skillranker macOS defect (2026-09-20)

No new issue filed: `Dicklesworthstone/skillranker#3` ("macOS build fails:
coordinator calls Linux-gated storage module", jwross24, OPEN) already covers
it. Posted corroboration as
`issuecomment-5750779980`:

- Still broken at tip `abf909d` (E0433 now first fires at `src/replay.rs:13`).
- Blast radius 7 files, not 1 (cli, pipeline, readiness, replay, effects,
  cache/coordination, storage/ledger).
- Ungating-is-not-the-fix evidence: 20 deeper errors on linux-only
  `nix::sys::statfs` magics + StoreError/type mismatches.
- Their docs corroboration: reality-check-bridge-plan.md:56, :226, :328.
- Framing offered: promise (install.sh:158, README:267) vs gate — either
  half closeable, their choice. No patch, no PR.
- RCH context: our fleet is linux-only, noted as our infra fact.

skillranker untouched (clone diff clean). Level: `test` (comment posted,
URL returned).

## Ledger line

REPORT skillranker-macos — DONE — corroborated #3 at tip with ungating
evidence — NO-CLAIM: maintainer's call; no local binary still.
