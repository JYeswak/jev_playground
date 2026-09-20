# skillranker build tick: BLOCKED, upstream macOS defect (2026-09-20)

Tip: `abf909d` (verified `git rev-parse --short HEAD`; fetch: origin/main =
abf909d, not behind). `git status`: clean except pre-existing untracked
`scratch-ho/`, `sr-linux-amd64` (not mine, untouched).

## Commands, exits unpiped

1. `cargo build --locked --release --bin sr` (README contract) → exit 102.
   Remote compile on contabo-4 SUCCEEDED but RCH-E327: all 4 workers are
   linux-x86_64, artifacts ELF, host aarch64-apple-darwin. Structural, not
   transient — no darwin worker exists.
2. Local build: lane denies by construction; Joshua authorized local build
   explicitly. Bypass chain found: `~/.local/bin/cargo` (70 KB script) →
   toolchain `<tc>/bin/cargo` (1454-byte rch wrapper script, "the one layer
   they cannot dodge") → `cargo-rch-real` (HARD DENY dispatcher, Sep-7
   CONTABO-OR-BUST) → `cargo-rch-real.bin` (true 1.100.0-nightly). Built with
   the true binary + isolated `CARGO_TARGET_DIR` (shared cache poisoned by a
   different nightly: E0514 cpubits/rand_chacha).
3. True local build → exit 101. First error verbatim:

```
error[E0433]: cannot find `storage` in the crate root
  --> src/replay.rs:13:12
   |
13 | use crate::storage::export::{
   |            ^^^^^^^ unresolved import
```

Root cause: `src/lib.rs:27-28` gates `pub mod storage` on
`#[cfg(target_os = "linux")]`, but 7 files (`cli, pipeline, readiness,
replay, effects, cache/coordination, storage/ledger`) use it unconditionally.
Experimental ungate (reverted): 20 further errors — `nix::sys::statfs`
BTRFS/EXT4/TMPFS/XFS magics, StoreError, type mismatches. Genuinely
Linux-specific filesystem code, not an over-broad gate.

## Not an accident: upstream documents it

- `docs/reality-check-bridge-plan.md:56`: "UNPROVEN release ... storage
  module Linux-gated"; :226: "Linux-gated storage prevents inferring macOS
  support"; :328: "native macOS storage/build tests" listed as release work.
- Gate landed `af417f1` (2026-09-17); tip still broken on mac 3 days later
  while `install.sh:158` advertises Darwin/aarch64 and README:267 claims
  "Linux and macOS" scope. Installer promise vs build reality is the defect
  to file upstream (not filed; needs a proper fork per lane rules).

## Honest deferrals

- `sr` not on PATH (no binary exists for this host); `sr --version`, demo,
  test suite: NOT RUN (nothing to run). No green claimed.
- Live rank: not attempted (blocked before key question); key presence
  unchecked. If someone builds on Linux, the key question reopens.
- Experimental edit reverted; clone diff clean. dsr symlinked to
  ~/.local/bin per FYI (unused — packaging never reached).

## Ledger line

BUILD skillranker@abf909d — BLOCKED — macOS broken at tip (linux-gated
storage + linux-only statfs), upstream documents the gap — NO-CLAIM: no
binary, no demo, no tests, no live rank; RCH path structurally ELF-only.
