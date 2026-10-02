# CHANGELOG — jev lane

Scope: 3,683 commits on `main`, 2026-09-17 → 2026-10-02, distilled into
capability waves (not a commit dump). Every SHA below is verifiable with
`git show <sha>`. Workstream detail lives in bead records
(`.beads/issues.jsonl`) and `EVAL.md`. No GitHub releases exist; the lane
ships on `main` only.

## Version spine

- `session/2026-09-17-lane-substrate` (2026-09-17): lane substrate handoff —
  git init with allowlist ignore, six-stage gate suite, pinned upstream
  mirrors, ripwire 0.6.1.

## 2026-09-17 → 2026-09-24 — evaluation lane

Read-mostly evaluation of the public Jev ecosystem: vendored TypeSafe docs
and SDKs, SDK client work (`kit/`), gate suite growth, hook and pipeline
experiments (demos, dispatches, upstream reproductions), benchmark games
(Jericho, PokéJev). Representative: `b74704c9` (EVAL: Jev serves omp's
native judge role, 1,711 calls/24h), `34f95aae` (README stranger-run fixes,
claim coverage 110/111).

## 2026-09-25 → 2026-09-30 — mission pivot: Jev ON where we work

Joshua's pivot (doctrine: Jev turned ON in the tools we use and proven
live). Surfaces went live with both-ways proofs: native judge
(`b74704c9`), skill hint (`9b55da3f`), rerank shadow (`9aa0372b`),
TTSR claim rule (`60b7a338`), fleet needs-human paging (`be74fcf2`),
memory-filter shadow (`5e00575e`), gate cascade built (`2bcfaf7f`),
injection shadow (`9abe975b`), webscreen enforce on Jev-only flags
(`3ad7adfb`). Infrastructure: surface inventory with live-vs-claim
conformance (`b9df6d9d`, `3c062564`), key provider
(`c7a82107`), AGENTS.md rightsized, docs/LEDGER.md claim registry with
coverage floor, README claim coverage to 114/115 (`283aa72a`), stranger
runnable (`05b6c458`, `34f95aae`). Parked with receipts: game and benchmark
runs, free-comparator arms (see NEGATIVE_EVIDENCE.md).

## 2026-10-01 → present — hardening and rollout

- Cascade: paid fallback on local failure (`4fd0f367`), fence-tested live;
  deterministic pre-rule for the destructive class (`d5348d42`).
- Memory filter: removal path with file switch, verified live both ways
  (`5fc68a4e` work; switch ON by conductor decision).
- Skill hint N2: Noul-rank 0/48 misroutes but 0/48 hints — safe but useless,
  not re-registered (`8cc6b66d`).
- Machine-wide rollout (`jev-j0er`): webscreen + injection screens as
  shadow in five profiles (`7c36b2c7`; hardlinks, not symlinks — omp
  discovery skips symlinks), drift conformance on inode+sha (`0246dd45`),
  24h shadow sample with committed exclusions (`e6f68b4c`, `8ee3432b`).
- Duel (`jev-n4eu`): one orchestrating handler over both screens,
  EQ-600 agreement 600/600 with incumbent-exact rates (`ffae4c44`).
- Sweep repairs: npm test wiring restored (kit, jev-client), claim floor
  raised to match registered claims (`f19406be` + floor sync).
- Verifications closed with evidence: `jev-nbbm` (pre-rule), `jev-9q1g`
  filed (claim-gate removal arm brittle at perfect coverage).
