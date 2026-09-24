Jeffrey —

The per-name authority in 73b7ad1 holds on a clean-room rerun. A skipped directory link no longer turns three resolved skills into an empty roster. Resolution still checks the exact name slot and withholds only the name it cannot prove, which is what docs/roster-resolution.md:60-71 describes, and what src/roster/resolution/discovery_scope.rs:103-107 implements: directory links are not followed, and an unseen file is not admitted by alias.

I rebuilt current tip at 07286cf802a9b8e26a12a422a7bb61a5c7ed1b93 as a Mach-O arm64 binary and ran the same three arms on macOS arm64, offline. Control: exit 11, eligible 3, cache-miss. After adding one symlinked skill directory: exit 11, eligible 3, cache-miss, with symlinked-directory-skipped reported. After removing the link: exit 11, eligible 3, cache-miss, and the skip diagnostic is gone. empty-roster does not appear.

That matches the regression in tests/rank_discovery_gaps.rs:157. The explicit roster manifest remaining all-or-nothing is understood as deliberate, and this run did not use one.
