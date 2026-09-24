# skillranker#4 dogfood — 2026-09-24

Jeffrey closed the issue as fixed in `73b7ad1`. This unit rebuilt current tip and reran the issue's three arms. No source change. No comment posted.

## Build

Scratch clone `/Users/josh/Developer/sr-dogfood-20260924`, not the vendored tree. SHA built: `07286cf802a9b8e26a12a422a7bb61a5c7ed1b93` (`07286cf`, tip of `origin/HEAD` at build time). The packet's `2a16486` was already behind that tip.

Command, from that directory:

```text
RCH_VISIBILITY=verbose rch exec -- cargo build --release -j 2 \
  --config 'build.target="aarch64-apple-darwin"' \
  --config 'target.aarch64-apple-darwin.linker="/usr/local/bin/zigcc-aarch64-darwin"' \
  --config 'env.CC_aarch64_apple_darwin="/usr/local/bin/zigcc-aarch64-darwin"' \
  -p skillranker --bin sr
```

`Remote command finished: exit=0` on `contabo-1` in 1499389 ms. Artifact: `target/aarch64-apple-darwin/release/sr`. `file` says `Mach-O 64-bit executable arm64`. The arms ran on this Mac, not on the build host.

`73b7ad1` is not an object in the depth-50 clone, so this receipt does not cite a line from that commit. The contract at the SHA that was built is `docs/roster-resolution.md:60-71` and `src/roster/resolution/discovery_scope.rs:103-107`. The regression test Jeffrey named is `tests/rank_discovery_gaps.rs:157`.

## Arms

Same script as the issue, homes under `/Users/josh/Developer` because RCH refuses `/tmp`. Binary above. Offline. No key.

| arm | exit | roster.eligible | error.kind | symlinked-directory-skipped |
|---|---|---|---|---|
| control | 11 | 3 | cache-miss | absent |
| one symlinked dir | 11 | 3 | cache-miss | present |
| link removed | 11 | 3 | cache-miss | absent |

`empty-roster` does not appear in the one-link output. Before the fix, that arm was exit 5 and an empty roster. The link is still reported. It no longer empties the other three names.

Outputs left at `/Users/josh/Developer/sr4-dogfood-0BEm/{pass,fail,restored}.json`.

## Boundary

This confirms the reported fix on a source build of tip. It does not report any other defect. No live ranking call. No GitHub comment. `jev-k9z.1` was already closed by pane 4; this unit did not reopen it and did not write its ledger row.
