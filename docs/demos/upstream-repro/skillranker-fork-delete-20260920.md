# Fork deletion + pure-source install status (2026-09-20)

## Fork deletion: PARTIAL, blocked by live sibling work

Removed: my worktrees `/tmp/sr-portfix`, `/tmp/sr-upstream` (verified gone).
`/tmp` build/probe cleanup: BLOCKED by SLB (rm-rf needs approval) — left in
place, all mine, OS-reclaimable; locations: `/tmp/sr-mac-target`,
`/tmp/sr-portfix-target`, `/tmp/sqlflagprobe`, `/tmp/srprobe`,
`/tmp/srroster`, `/tmp/srqual`, `/tmp/srlive`, `/tmp/srtiming`.

RETAINED deliberately: `/Users/josh/Developer/skillranker-mac` itself. The
conductor has live work inside it (`probe-upstream` branch @0e61cc6 verified
intact, plus a running RCH build `skillranker-mac-c85367bf` synced from that
path). Deleting the clone now would destroy his in-flight work. Needs his
sign-off or build completion — do not delete unilaterally. My port branch
(`main` @3d08d32) remains in the clone, unpushed.

## Pure-source install: binary ready, needs your cp

`/tmp/sr-upstream-target/release/sr` — built from unmodified upstream
`0e61cc6`, Mach-O arm64, `sr --version` → 0.1.0, `demo --case useful` exit 0.
(SLB blocks my cp; same as before.)

```bash
cp /tmp/sr-upstream-target/release/sr ~/.local/bin/sr
```

## New residual finding (NOT filed, per native-binary rule)

Tip `fe5cacc` does NOT build — upstream broke itself after the mac fix:

```
error[E0560]: struct `RecordedRerankChoice` has no field named `stated_confidence`
    --> src/pipeline.rs:2304:17
```

Likely transient (hourly shipping; probably 1fe25b6's counterpart half).
Recorded here only, not upstream.

## Ledger line

DELETE fork — PARTIAL (worktrees gone, clone held for sibling) — source
binary ready at /tmp/sr-upstream-target — fe5cacc broken, 0e61cc6 green —
NO-CLAIM: nothing filed, nothing pushed, install needs your cp.
