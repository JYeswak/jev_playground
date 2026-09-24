# WITHDRAWN 2026-09-24 (never posted): issue #3 follow-up comment — residual macOS gaps at 0e61cc6

> Withdrawn under jeff-issue-chain Phase −1 and Joshua's standing rule. #3 closed 2026-09-20T21:13Z
> after Jeffrey landed native macOS support (`6b5d17c`); upstream tip is `2a16486` (2026-09-24), so
> every finding below is from a stale build. skillranker still has no releases (`gh release list`
> empty, 2026-09-24T01:50Z), so the rule that skillranker findings come only from native binary
> downloads still blocks a source-build report. Reopen only if a native macOS release exists and a
> gap below reproduces from it.

> Status: draft only. Posting needs Joshua's explicit approval: his rule
> allows skillranker findings ONLY from native binary downloads, and no
> native darwin binary exists. Everything below was found building tip from
> source on macOS. Report-Test self-assessment at the end.

---

Verified `9c52a64` fixes the reported defect: tip builds clean on
aarch64-apple-darwin (`cargo build --locked --release --bin sr`, exit 0,
Mach-O arm64, `sr demo --case useful` green). But the suite does not pass:
**872 pass, 61 fail** on darwin, all in areas this thread's fix did not
touch. Four residual classes, each stranger-runnable:

**1. Bundled SQLite + `SQLITE_OPEN_NOFOLLOW` fails on Apple (CANTOPEN 1550).**
`src/cache/coordination.rs:645`, `src/storage/mod.rs:522` — both
unconditional. Every sqlite open through the lease/coordination/cache path
fails on macOS. Minimal repro (crates.io rusqlite only, no sr build):

```bash
# /tmp/sqlflagprobe with rusqlite =0.40.2 bundled; open with
# READWRITE|CREATE|NO_MUTEX|NOFOLLOW vs without NOFOLLOW.
# Observed macOS arm64: NOFOLLOW → SqliteFailure CannotOpen 1550;
# without → OK.
```

**2. `killpg` group-kill returns EPERM on session-isolated children.**
`src/subprocess.rs` `kill_group` treats any non-ESRCH error as Cleanup,
which masks the real error (an over-limit run reports Cleanup instead of
LimitExceeded). Repro: `cargo test --locked --test cass_adapter
child_failure` fails on mac tip; control experiment shows raw
setpgid+killpg works from a test harness while asupersync-spawned children
fail, implicating session isolation, not the OS.

**3. `retry_server.py` assumes `socket.timeout is TimeoutError`.**
`tests/fixtures/jev-tls/retry_server.py:92` — false on the Python 3.9 macOS
ships, so 9 `jev_retry` tests die with EOF instead of reporting. One-line,
version-portable fix exists (`except (TimeoutError, socket.timeout)`).

**4. Fixtures assume a non-symlinked `/tmp`.** `temp_ledger_dir` et al.
build under `/tmp`, which is a symlink on macOS that the store's
descriptor-walking validators correctly refuse (`UnsafePath`). Repro:
`cargo test --locked --test ledger_fencing_contract` (and migration,
quota, retention, schema, replay, save_case variants). Canonicalizing the
fixture root resolves all of them with no product change.

Adopt-or-fix is yours; reporting only, no patch attached. The `#[cfg(any(
target_os = "linux", target_os = "macos"))]` widening in `9c52a64` is
strictly safer than the outright ungate I tried first — adopted that read.

---

## Report-Test self-assessment (do not ship if any fail)

1. NOFOLLOW probe: PASS — crates.io dep only, paste-and-run, deterministic
   CANTOPEN 1550 on Apple.
2. killpg/control pair: PASS — `cargo test` invocation + 20-line control,
   both executed, deterministic EPERM vs OK split.
3. socket.timeout: PASS — one-line change, suite goes 6/15 → 15/15,
   executed before/after.
4. Canonicalization: PASS — `cargo test` invocations before/after across
   7 fixture files, all green after.

All four were executed, not inferred. What was NOT executed on a native
binary (none exists for darwin): everything above. That is the filing-rule
conflict, stated, not hidden.
