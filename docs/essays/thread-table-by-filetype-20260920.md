# Thread table keyed by file type — P2 drafting, P3 triggers

2026-09-20. No rules drafted here; P3 owns triggers and the carriable-type
call. Every number below states its denominator in the same sentence.

Fleet write distribution grounding the order (all git repos under
~/Developer, 30 days, by extension): json 17,915 / rs 17,416 / md 17,287 /
sh 7,199 / ts 6,538 / jsonl 4,249 / toml 3,470. Top .rs repos:
omp-orchestrator 2,782, franken-harvest 1,267, frankenmermaid 1,195,
zeststream-cast 1,153. Correction applied: an earlier jev-only 3-day count
said we barely write Rust; fleet-wide Rust is top-two, so .rs ranks FIRST.

Recurrence denominators: doc-index counts run over all 390,739 doc-index
records (generation `08457a25`) unless noted.

## .rs — exactly six threads (fleet 17,416 edits/30d)

Per P3 coverage map `work/skills-vein/rs-builtin-coverage-20260920.md`
(@1c2272f): NOTHING else in this section. Out entirely: Box::leak, Future
prelude, LazyLock, match ergonomics, parking_lot unwrap sites, Result
alias default (all free via omp builtins). Dropped from my draft:
general no-unwrap (map silent) and standalone zero-copy (folded into
perf selection below).

1. **Unsafe discipline beyond the leak call** — 898 hits / 87 repos
   (denominator: 390,739 doc-index records, generation `08457a25`).
   `frankensim@88a4819ab AGENTS.md:305`:
   "Keep unsafe leaves small, local, and behind safe facades."
   Gap beyond builtin: workspace `#![forbid(unsafe_code)]` policy
   (frankenterm sets it per crate with separately audited native/FFI
   exceptions), `unsafe impl Send/Sync` review (71 indexed sites),
   `PhantomData` invariant documentation (165 sites) — per coverage map.
2. **Error shape beyond the alias syntax** — 619 / 62.
   `asupersync@fa3c01aec6c77c6652c7a754e8e009287daa5323 docs/tokio_process_lifecycle_parity.md:67`:
   "### 2.3 Error Taxonomy" (`ProcessError::NotFound(program)` vs
   `io::Error(NotFound)`).
   Gap: thiserror for library errors, anyhow for applications,
   `.context()` chaining (charmed_rust error-handling guide, meta_skill
   rust-error-handling) — per coverage map.
3. **parking_lot declaration choice** — 183 / 15.
   `asupersync@fa3c01aec docs/wasm_api_surface_census.md:199`:
   "`parking_lot::Mutex` in evidence_sink.rs" (census instance;
   quote-weak — marks a declaration site, not the choice rule).
   Gap: `std::sync::Mutex` vs `parking_lot::Mutex` at declaration plus
   lock-ordering discipline — per coverage map.
4. **Newtype + typestate** — newtype 66 / 19, typestate 103 / 10.
   `frankensympy@f7966e637 docs/WORKSTREAM_GRAPH.md:146`:
   "distinct ID newtypes and canonical text/binary forms".
   `asupersync@fa3c01aec6c77c6652c7a754e8e009287daa5323 tests/conformance/session_types/COVERAGE.md:77`:
   "State transitions: Proper typestate progression".
   Plus per coverage map: `CapabilityToken<S>` typestate ladder + Lean
   proof (flywheel_connectors), linear obligation tokens (asupersync
   Reserved→Committed/Aborted).
5. **Oracle per domain** — 18 domains, 18 named oracles (`fh oracles`).
   D6 sqlite/rusqlite
   `frankensqlite@b482edddcdda05abe44475ccfd43202e629379f3:crates/fsqlite-e2e/tests/comparison_affinity_oracle_e2e.rs:1`;
   D4 graph/NetworkX
   `franken_networkx@a4c32c7ac5be018467eb028e0fc5988e690f5353:tests/python/conftest.py:231`;
   D5 dataframe/pandas-2.2.3
   `frankenpandas@debdf374987d4b673105a1ce24ae3f7a457616fb:crates/fp-conformance/TESTING_CONVENTION.md:52`.
   Coverage map: "no syntax condition expresses" the selection — trigger
   decision is P3's lane.
6. **Perf technique selection** — T1 SIMD, T2 arena/bump, T3 lock-free
   publication, T4 zero-copy views, T5 const-generics, T6 cache-line
   layout, T7 branch-free (2 repos each, `fh techniques`).
   e.g.
   `frankensqlite@b482edddcdda05abe44475ccfd43202e629379f3:crates/fsqlite-vdbe/src/vectorized.rs:228`:
   "pub fn into_bytes(self) -> Arc<[u8]> {".

## .json — 2 threads (fleet 17,915)

1. **Lock identity** (L7) —
   `frankensim@420081058af5a7cfa031fb408e29b56d111a3112:constellation.lock:6`:
   "`lock_hash` covers (lib, version, git_head) only — paths are
   per-machine".
2. **Claims lattice for receipt/report files** — same L1 thread as .md
   (applies wherever a claim is recorded, md or json).

## .md — 2 threads (fleet 17,287)

1. **Equal-or-weaker** (L1) — 24 hits / 5 repos.
   `frankengraphdb@a3c2bec22ca32720843f659c8dae341355541009:registries/constitution.toml:25`:
   "# equal-or-weaker: rank(justifier) >= rank(claim) or the build fails."
   Incident mark: UNAVAILABLE — file outside doctrine-history's
   AGENTS/CONTRACT set.
2. **No-claim boundaries** — 294 hits / 18 repos (concentrated).
   `asimposium.org@4d8d6cc0becea480a7898dd98277eb592b03814f AGENTS.md:413`:
   "Do not claim a surface is done unless the relevant Fable gate is
   actually green."

## .sh — 5 threads (fleet 7,199)

1. **Wrapper reports every verdict** (L1 exemplar) —
   `frankengraphdb@a3c2bec22...a009:scripts/check.sh:24`:
   "wrapper reports every verdict before exiting, and a green summary is
   possible". Recurrence: single known instance; full-mirror phrase sweep
   timed out at 180s — UNPROVEN beyond the exemplar. Incident mark:
   UNAVAILABLE (non-AGENTS file).
2. **check.sh convention** — 1,524 mentions / 45 repos.
3. **Planted-trip gates** (L4) — 275 / 40.
   `frankensim@420081058af5a7cfa031fb408e29b56d111a3112:.github/workflows/ci-self-test.yml:4`:
   "green here means 'the gates demonstrably trip'".
4. **run.sh single entry** — 148 / 15 (mentions only, weak).
5. **Capture-first, match-second** — lane-owned
   (`.omp/rules/bash-pipe-exit.md`): exit codes from an unpiped run.

## .ts — 0 new threads (fleet 6,538)

13 builtins already free (ts-no-any, ts-no-inline-cast-access,
ts-no-test-timers, ts-import-type, ts-bare-catch, ts-no-deprecated-
leftovers, ts-no-dynamic-import, ts-no-local-is-record, ts-no-return-type,
ts-no-tiny-functions, ts-promise-with-resolvers, ts-redundant-clear-guard,
ts-set-map). Mirror TS threads unmeasured — stated, not skipped silently.

## .toml — 1 thread (fleet 3,470)

Lock identity (L7), same citation as .json — the thread lives in lockfiles
regardless of serialization.

## Starters: verified or not

- Wrapper-verdict: VERIFIED as exemplar, recurrence UNPROVEN (1 instance,
  sweep timeout).
- Zero-.sh-outside-one-run.sh: UNVERIFIED — mirror search returned vendor
  noise only. Not asserted anywhere in this table.
- L1 lattice → .md receipts: VERIFIED (exemplar + 24/5).
- L3 oracle → test files: VERIFIED (18 domains, e.g. D6 rusqlite
  `frankensqlite@b482eddd…:crates/fsqlite-e2e/tests/comparison_affinity_oracle_e2e.rs:1`).
- Four-mandatory-gates → workflows: VERIFIED (L2 exemplar
  `asupersync@…:.github/workflows/methodology-gates.yml:3`, 24 hits/12 repos).

## doctrine-history as filter: works, bounded

~7s/repo; markdown_web_browser: 346 added / 107 removed / 118 rewritten;
frankengraphdb: 142 / 4 / 10. Sampled mechanizable rows traced to bulk-
import commit `f2e432e6` (2026-01-17) — weaker prior than incident-earned.
Limitation: only AGENTS.md/CONTRACT.md histories are inspected, so
constitution.toml/scripts/check.sh threads carry no mark.
