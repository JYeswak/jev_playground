# Rust builtin coverage map — 2026-09-20 (P3 → P2)

Registry: `omp ttsr list` shows 35 rules: 27 builtins (8 go-*, 6 rs-*,
13 ts-*), 6 native ours, 2 agents system-wide. Every rs-* builtin is
`scope: tool:edit(*.rs), tool:write(*.rs)` — they fire when a Rust file is
opened for writing, which is exactly the per-file-type routing seat.

Doctrine sources: `fh techniques` (7 techniques, 14 exemplars),
`fh oracles` (18 domains, 18 oracles, mostly Rust crates),
`fh search` on unsafe discipline / error shape / newtype typestate.
Caveat: fh ledger_age_hours ≈ 307 (STALE per brief); these are structural
doctrine rows with pinned revisions, usable with that caveat stated.

## (a) Already caught free — DO NOT REBUILD (6)

| Thread | Builtin | Catches exactly |
|---|---|---|
| Box::leak | rs-box-leak (`Box::leak`) | the leak call itself |
| Future prelude | rs-future-prelude (`std::future::Future`) | fully-qualified path, use bare `Future` |
| LazyLock | rs-lazylock (`once_cell::`, `OnceLock::new`) | legacy/compat statics, prefer `LazyLock` |
| Match ergonomics | rs-match-ergonomics (`(ref mut`, `(ref [a-z_]`) | ref/ref-mut patterns, use ergonomics |
| parking_lot unwrap pattern | rs-parking-lot (`.lock().unwrap()` et al) | std Mutex/RwLock call sites that unwrap |
| Result alias default | rs-result-type (`type Result<X> =`) | alias missing a defaulted error param |

## (b) Partially caught — shippable named gaps (3)

1. **Unsafe discipline.** Covered: the `Box::leak` call. NOT covered:
   workspace `#![forbid(unsafe_code)]` policy (frankenterm sets it per
   crate with separately audited native/FFI exceptions), `unsafe impl
   Send/Sync` review (71 indexed sites), `PhantomData` invariant
   documentation (165 sites). A rule firing on `unsafe` blocks/impls that
   injects the forbid-plus-audited-exception ladder is not a duplicate.
2. **Error shape.** Covered: alias default-param syntax. NOT covered: the
   actual thread — thiserror for library errors, anyhow for application
   errors, `.context()` chaining (charmed_rust error-handling guide,
   meta_skill rust-error-handling). A rule firing on error-enum or
   anyhow-use sites is not a duplicate.
3. **parking_lot selection.** Covered: unwrap call sites. NOT covered:
   declaration-site choice (`std::sync::Mutex` vs `parking_lot::Mutex`)
   and lock-ordering discipline. A rule firing on std Mutex type
   positions is not a duplicate.

## (c) Uncovered (3)

1. **Newtype + typestate.** No builtin touches it. Evidence:
   newtype_struct serde patterns (fastmcp, frankenterm codec),
   `CapabilityToken<S>` typestate ladder + Lean proof
   (flywheel_connectors), linear obligation tokens
   (asupersync bead, Reserved→Committed/Aborted).
2. **Oracle-per-domain.** No builtin touches it. 18 domains with named
   external oracles (h2spec, RFC 6330/9000, NetworkX, pandas 2.2.3,
   rusqlite, Redis 7.2.4, NumPy, SciPy, CommonMark, ...). The thread is
   "this domain has a named external oracle — differentially test against
   it", which no syntax condition expresses; P2 must decide the trigger.
3. **Perf technique selection.** No builtin touches it. 7 recurring
   techniques (SIMD, arena/bump, lock-free publication, zero-copy views,
   const-generics, cache-line layout, branch-free hot paths).

## For P2's table

Carry only (b) + (c): unsafe-discipline, error-shape, parking_lot
selection, newtype/typestate, oracle-per-domain, perf-techniques.
Everything in (a) stays out. ts-*/go-* builtins are out of scope here;
the same pass should be run for .ts before its rule (13 ts-* builtins).
