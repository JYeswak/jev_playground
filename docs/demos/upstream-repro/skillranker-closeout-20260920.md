# Fork gone + how our skills qualify (2026-09-20)

## Fork deletion: COMPLETE

`/Users/josh/Developer/skillranker-mac` no longer exists (Joshua deleted
it). My port branch (`8cca771` + `3d08d32` fix) went with it, unpushed, as
ordered. Surviving record: `docs/demos/upstream-repro/skillranker-*.md`
(lifecycle, rank-quality, issue draft, dogfood, use-process). Test user
config removed; machine at found state (ledger missing, no custom config).

## How our skills get qualified — answered empirically

**Q: why can't sr use our skills?**
A: Three stacked reasons, all measured:
1. Flat `.md` files are not skills to `sr` (`unsupported-layout`, 167) —
   only `SKILL.md` directories count. Our JSM library is invisible by shape.
2. Discovered skills are always Unverified → ineligible for ranking
   (needs provisional-Verified + agent-invocable). All 531 sit here.
3. The documented escape (declared roots → provisional label) works via
   **project** `.sr/config.toml` (proven twice live: `focused-fix` #1 at
   0.88/0.96/0.99, `phish-guard` #1 at 0.98 on matching tasks) but **not**
   via user config — declared absolute roots parse (`doctor --config`
   shows them from `trusted-user`) yet yield zero eligible skills in rank.
   Reproducible, mechanism unisolated, unfilable per native-binary rule.

**Q: so how do we use it?**
A: Per-repo project config declaring that repo's `SKILL.md` dirs, then
`sr rank --context ... --allow-network`. No harness changes, no library
reformat needed for skills already in `SKILL.md` layout. Verified end to
end with real Jev calls (jev-1.13.0, ~1800/330 tokens per rank).

His README corroborates the shape of this: every rank result carries
`"visibility": "unverified"` (precedence lacks conformance evidence), and
configured roots "can be suggested" while discovery alone cannot.

## Ledger line

FORK deleted by Joshua — USE process proven on project roots, user-roots
path broken-but-unfilable — NO-CLAIM: 3 ranking tasks judged; installed
binary remains pure `0e61cc6` source build.
