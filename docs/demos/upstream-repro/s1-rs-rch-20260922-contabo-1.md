# s1-rs — worker split decides it: contabo-1 passes, contabo-4 fails (plan W7.2)

- **Repo:** `AbdelStark/s1-rs` @ `b916897` (vendored clone, unmodified; no local
  cargo build ran — RCH only; `git -C s1-rs status --porcelain` clean).
- **Prior receipt:** `s1-rs-rch-20260922.md` (1661c73): contabo-4, 27 pass,
  trybuild `ui` 4/4 "Expected test case to fail to compile, but it succeeded".
- **This run:** from `s1-rs/`,
  `env -u TYPESAFE_API_KEY RCH_VISIBILITY=verbose rch exec -- cargo test -j 2 -p s1 --test ui`
- **Date / lane:** 2026-09-23T03:00Z, keyless, no `RCH_WORKER` (RCH chose).

## Proof lines

```
Selected worker: contabo-1 at root@89.117.22.43
test tests/ui/bool_without_noul.rs ... ok
test tests/ui/choice_fields.rs ... ok
test tests/ui/duplicate_labels.rs ... ok
test tests/ui/too_few_variants.rs ... ok
test result: ok. 1 passed; 0 failed   (46.08s)
Remote command finished: exit=0 in 92265ms
```

Two more contabo-1 runs (fresh `CARGO_TARGET_DIR`, rewritten by RCH to a
worker pool dir) also exit 0. Forced `RCH_WORKER=contabo-4` with fresh target:
exit=101, same 4/4 "succeeded". Toolchains identical both workers:
`rustc 1.98.0 (88d9e12ae 2026-08-18)`.

## Owner: RCH worker environment (contabo-4), not s1-rs — file:line

- `s1-rs/crates/s1-derive/src/choice.rs:32-37`: the `n < MIN_CHOICE_OPTIONS`
  rejection is unconditional (no feature gate, no cfg). `too_few_variants.rs`
  (one variant) cannot compile if this derive runs — and contabo-1 proves it
  fires (expected `.stderr` matches there).
- Same source + same lockfile (trybuild 1.0.119) + same rustc → opposite
  verdicts per worker. A source defect cannot do that.
- RCH rewrites `CARGO_TARGET_DIR` per run
  (`transfer.rs:1913`: `/tmp/s1fresh4` →
  `.rch-target-contabo-4-pool-f19517fa…`); pool dirs do not persist between
  runs (absent afterwards), so this is not a stale pool dir — the poison is
  in contabo-4's persistent build layer (registry/cache/toolchain state),
  exact layer still open.

## Boundary

Did not run anything live (no key). Did not build locally. Did not modify
the clone. Did not run `examples/`. The `--job`-rail direct scratch-crate
check was refused remotely (retries exhausted) — the worker split above is
the decisive experiment, not the direct case.
