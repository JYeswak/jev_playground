# P3 — BLOCKED accepted. File it, then take a unit that can actually ship.

I verified your blocker at source rather than taking the receipt:
`skillranker/src/lib.rs:27-28` is `#[cfg(target_os = "linux")] pub mod storage`, while
`install.sh:158` serves `Darwin/aarch64` and `README.md:267` says *"Linux and macOS"*. **The
installer promises a platform the build cannot produce.** That is a real upstream defect and
`BLOCKED` was the correct callback — a green report that skipped the binary would have been worse.

Your NO-CLAIM is exactly right and I am not asking you to soften it: no binary, no demo, no
tests, no live rank.

## Unit 1 — file the upstream issue (your stated NEXT), then stop touching skillranker

Report, do not patch. Include: tip `abf909d`, the verbatim `E0433`, the gate at `lib.rs:27-28`,
the seven files using `storage` unconditionally, **and the evidence that ungating is not the fix**
— your 20 further errors on `nix::sys::statfs` BTRFS/EXT4/TMPFS/XFS magics prove the code is
genuinely Linux-specific, so a naive "remove the cfg" suggestion would waste their time.

Quote their own docs back as corroboration, not accusation: `reality-check-bridge-plan.md:56`,
`:226`, `:328` already name this. **The defect worth their attention is the installer/README
promise, not the gate** — a maintainer may reasonably keep storage Linux-only and fix the advert
instead. Offer both readings and let them choose. No patch, no PR.

One line on the RCH finding: note that remote builds cannot cover this because all four workers
are `linux-x86_64` and the host is `aarch64-apple-darwin`. That is *our* infrastructure fact, not
their bug — keep it out of the issue body except as context for why we could not work around it.

## Unit 2 — then take a unit that can ship today

`skillranker` is gitignored here and cannot produce a binary on this machine, so further build
attempts are not product. Instead: **`br ready`, claim the highest-priority bead you did not
author, and work it.** If the frontier is empty, take the highest-value unreviewed artifact you
did not write — the honest-idle callback you have fired twice tonight is still better than
manufactured work, but check the graph first.

Finish one, fire its callback, then start the next YOURSELF.

Do not run formatters or repo-wide gates — I verify at phase end. Exit codes unpiped. Commit on
create.

`ntm --robot-send=jev --panes=1 --msg="CALLBACK-P3-<UNIT>-<DONE|BLOCKED>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."`
