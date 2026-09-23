# omp-continue fit v2 (TopazRaven executing, pane-3 unit, 2026-09-23)

Old: `/Users/josh/Downloads/omp-kit.zip` (17,730 B, 19:44).
New: `/Users/josh/Downloads/omp-kit (1).zip` (25,314 B, 20:01).

Member `omp-kit/scripts/omp-continue.sh`:
- old sha256 `ccf23ff9…77410`, new sha256 `fbfb966e…1ffa3c`: DIFFERENT.
- The only hunk: git-root handling. Old line 21
  `git rev-parse --git-dir`; new lines 21-22 resolve
  `top=$(git rev-parse --show-toplevel)` and `cd "$top"`, because `/loop`
  runs the condition in the session cwd, which may be a subdirectory.

Claim-gate path and argv: STILL THE OLD ONES. Both zips call
`sh scripts/check-claim-discipline.sh` with no argv (lines 42-46), a
relative path resolved against whatever cwd the loop runs in — which is
exactly what the new `cd "$top"` hunk now pins to the repo root. The
MISS on `scripts/check-claim-discipline.sh` in this tree stands: the gate
only fires when that relative path exists, and nothing was installed.

Boundary: nothing installed, `init.sh` not run. Compared extracted copies
under `/tmp/ompfit/`; the repo tree is untouched except for this note.

NO-CLAIM: a member diff is not a fit decision.
