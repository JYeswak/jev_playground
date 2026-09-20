# P3 (Muse) — finish the skillranker build to an installed, demonstrated binary

Target: `/Users/josh/Developer/jev/skillranker` (tip `abf909d`). **Note: `skillranker` is
gitignored by `/​*` in this repo's `.gitignore`, so it is NOT versioned here.** Do not try to
commit it into `jev`. Receipts about it go under `docs/demos/upstream-repro/`.

Last observed state: `skillranker/Cargo.toml` exists; **`sr` and `dsr` are not on PATH.**

## Units — finish one, fire its callback, then start the next YOURSELF

1. **Compile.** `cargo build --release` in `skillranker/`. If it fails, fix forward; report the
   first error verbatim if it is an upstream defect rather than a local one.
2. **Install `sr`** so it is on PATH (`cargo install --path .` or the repo's documented route —
   prefer whatever the repo itself specifies over inventing one). Prove it: `command -v sr` and
   `sr --version` both unpiped.
3. **Demo + tests.** Run the repo's own test suite and its demo path. Report per-file pass counts
   derived by running, never from a summary — a callback in this lane once reported 21 tests for a
   file that has 6.
4. **Live rank, only if the key is present.** `infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba --env=prod -- <sr rank command>`.
   If the key is absent, that is `UNVERIFIABLE (no key)` — **but ask whether someone else can run
   it before deferring.** A false UNVERIFIABLE cost this lane a stale published latency band
   tonight: "needs a key" was true of the reviewer and false of the lane.
5. **Packaging only if needed** — use `dsr` from the doodlestein_self_releaser mirror. Do not
   hand-roll a release path.

## Acceptance

`docs/demos/upstream-repro/skillranker-build-20260920.md`: the exact commands, unpiped exit codes,
`sr --version` output, per-file test counts, the demo output, and the live rank result or its
honest deferral. **`BLOCKED` with the first real error is a valid outcome; a green report that
skipped a step is not.**

Do not run formatters or repo-wide gates — I verify at phase end. Exit codes unpiped.

`ntm --robot-send=jev --panes=1 --msg="CALLBACK-P3-SKILLRANKER-<DONE|BLOCKED>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."`
