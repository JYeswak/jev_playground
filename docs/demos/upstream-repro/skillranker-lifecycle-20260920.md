# skillranker macOS port: full lifecycle (2026-09-20)

Upstream: `Dicklesworthstone/skillranker` @ `abf909d`. Fork-clone (never to
be pushed): `/Users/josh/Developer/skillranker-mac`, port committed locally
as `8cca771`. Installed: `~/.local/bin/sr` 0.1.0, byte-identical to the port
build (verified by `cmp`, conductor verified independently).

## 1. The blocker (verified at source, not taken on faith)

`cargo build --locked --release --bin sr` → exit 101, first error verbatim:

```
error[E0433]: cannot find `storage` in the crate root
  --> src/replay.rs:13:12
13 | use crate::storage::export::{
```

`src/lib.rs:27-28` gates `pub mod storage` on `#[cfg(target_os = "linux")]`
(gate landed `af417f1`, 2026-09-17) while `install.sh:158` serves
`Darwin/aarch64` and README:267 claims "Linux and macOS". 7 files use
`crate::storage::` unconditionally. RCH cannot cover it (all 4 workers
linux-x86_64 → E327 ELF on aarch64-apple-darwin host). Filed upstream as
corroboration on issue #3 (jwross24, OPEN), not a duplicate.

## 2. Why ungating alone fails (proven, not assumed)

Removing the cfg → 20 further errors: `nix::sys::statfs` BTRFS/EXT4/XFS/TMPFS
magics, `filesystem_type()` (absent on mac Statfs), `st_dev: i32` vs `u64`,
`StoreError` missing from the non-linux pipeline stub. The storage code is
genuinely Linux-specific. Reverted; ported instead.

## 3. The port, file by file (27 files, +308/-63)

**Product code (8 files):**

- `src/lib.rs`: ungated `pub mod storage` (1 line).
- `src/storage/filesystem.rs`, `src/storage/ledger.rs`: filesystem admission
  allowlist keyed on `filesystem_type_name()` on mac (apfs/hfs/ufs/exfat/
  msdos/cd9660/udf admit; network/synthetic/unknown refuse — same fail-closed
  posture as the Linux magic allowlist); `st_dev as u64` casts (dev_t is i32
  on mac); `filesystem_admitted(&impl AsFd)` helper replacing 4 call sites.
- `src/pipeline.rs`: (a) added the missing `StoreError` import to the
  non-linux stub (Jeff's own `UnqualifiedEngine` design — mac runs uncached);
  (b) stub honors `--no-cache` → reports `disabled` instead of `unavailable`
  (matches `Evaluated::persistence` contract; verified live).
- `src/cache/coordination.rs`, `src/storage/mod.rs`: `SQLITE_OPEN_NOFOLLOW`
  gated off Apple — bundled SQLite returns CANTOPEN 1550 with it (isolated
  with a 10-line rusqlite probe: NOFOLLOW FAIL, plain OK). Pre-open symlink
  refusal retained everywhere.
- `src/subprocess.rs`: killpg → EPERM on mac (session-isolated children;
  proven by control: raw setpgid+killpg works from a test harness,
  asupersync-spawned children fail) → fall back to direct leader SIGKILL.
  Overflow runs now report LimitExceeded instead of masking with Cleanup.

**Tests/fixtures (19 files):** canonicalized /tmp-based fixture roots (mac
/tmp is a symlink the validators correctly refuse); Apple user-config dir in
roster test (`~/Library/Application Support`, a real product difference
found by failing test); `socket.timeout` in retry fixture (py3.9 class
split); unique retry dirs; pre-warmed fake git (first-exec assessment ~1s
vs 250ms stage); non-UTF-8 tests gated off Apple (APFS rejects at VFS);
Linux-gated with reasons: 8 rank_acceptance + 6 real_rank_coordination +
3 trace_continuation + 5 roster_snapshot cache/store tests + 1 roster
snapshot tail (behavior absent by upstream design, not broken). mac branches
assert the designed miss where converted (cache_identity).

## 4. Verification (exits unpiped)

- `cargo check --locked --all-targets`: exit 0, 0 warnings.
- `cargo test --locked --no-fail-fast`: **821 pass, 1 fail** —
  `child_failure...` probe-setup DeadlineExceeded under full parallel load;
  green solo + in file runs. Load flake, documented, not product.
- `cargo build --locked --release --bin sr`: exit 0 (Mach-O arm64).
- `sr demo --case useful`: exit 0.
- Live (Infisical key + consent flags): jev_smoke capacity/rerank/contract/
  distribution **4/4 green** — real paid Jev evaluations through the mac
  binary's TLS + auth path (model `jev-1.13.0` both stages).
- Live ranking on real-format data: `ranked`, see rank-quality receipt.

## 5. Gaps proven true (not suspected)

1. mac runs UNCACHED by upstream design (pipeline stub → UnqualifiedEngine).
   Cost quantified in rank-quality receipt: every rank re-pays 2 calls.
2. Snapshot export refused off Linux by design (`export_snapshot` stub).
3. 22 tests gated to Linux with reasons (list §3); suite is green *with*
   documented scope holes, not universally.
4. asupersync-spawned children are session-isolated on mac: group kill
   EPERM (fallback covers the leader; descendants out of reach).
5. Bundled SQLite + NOFOLLOW broken on Apple (flag off; pre-checks retained).
6. First-exec assessment latency (~1s) exceeds the 250ms signals stage —
   test-only pre-warm, but real first runs of fresh binaries pay it too.
7. One parallel-load flake (probe-setup deadline) outstanding, documented.

## 6. Submission package (for Joshua's form decision)

- Patch set: `skillranker-mac@8cca771` vs `abf909d` (local branch, unpushed).
- Upstream state: issue #3 OPEN covers the defect; my corroboration comment
  posted with tip reproduction + ungating evidence + promise-vs-gate framing.
- Skill rule bars upstream PRs ("Jeff's agents implement fixes"); a 27-file
  port does not fit in an issue comment. Form decision needed: (a) issue
  offering the branch for pull, (b) fork + PR, or (c) hold local-only.

## Ledger line

PORT skillranker-mac@8cca771 — lifecycle documented — binary installed and
verified — gaps enumerated, all with commands — NO-CLAIM: store/cache
unqualified on mac by design; submission form undecided.
