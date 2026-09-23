# commit-miner — own suite via RCH (plan W7.2)

- **Repo:** vendored `commit-miner` @ `977617e` (unmodified; no local cargo
  build — RCH only; `git -C commit-miner status --porcelain` clean).
- **Command:** from `commit-miner/`,
  `env -u TYPESAFE_API_KEY RCH_VISIBILITY=verbose rch exec -- cargo test -j 2 --workspace`
- **Date / lane:** 2026-09-23T03:04Z, keyless.

## Proof lines (contabo-3, exit=101, 108s)

```
Selected worker: contabo-3 at root@94.72.121.48
test result: FAILED. 22 passed; 1 failed
thread 'tests::diffs_exceeding_old_file_and_commit_caps_keep_their_tails' (2865660)
  panicked at src/tests.rs:799:78:
  called `Result::unwrap()` on an `Err` value: Git operation failed.
  Check repository access, network, and available history.
Remote command finished: exit=101 in 108005ms
```

Single-test rerun on contabo-4: identical failure at the same line
(exit=101). Two workers → not worker-specific.

## Owner: commit-miner's own test assumption — file:line

- `commit-miner/src/tests.rs:799` is
  `git::evidence(temp.path(), &commit, &c).await.unwrap()` — the unwrap that
  panics.
- `commit-miner/src/git.rs:162` is the `ensure!(status.success(), "Git operation
  failed. ...")` — a git subprocess inside `evidence()`/`diff_sections()`
  (`git diff --no-ext-diff --no-textconv --no-color --no-renames --unified=20`,
  `git.rs:959+`) exits nonzero with empty stderr detail on the worker.
- Test setup is hermetic for identity (`tests.rs:277-281` sets local
  user.name/email) and the repo is a fresh tempdir, so neither identity nor
  history explains it. The test runs `git diff --unified=20` over three
  215,000-line files; the failing layer is inside the worker's git
  invocation, reproducible on contabo-3 and contabo-4 alike.
- Open: which exact git subcommand exits nonzero (stderr detail is empty in
  the surfaced message). Next step: rerun with the evidence stderr surfaced.

## Boundary

Did not run anything live (no key). Did not build locally. Did not modify
the clone. The 22 passing tests are the crate's offline suite; they say
nothing about Jev's answers.

## Correction after worker repair (2026-09-23T03:38Z): NOT the clone's fault

Re-ran the single test on repaired contabo-4: exit 0, 1 passed. The owner
above is withdrawn — the failure was the same `/dev/null`-regular-file
poisoning (pane 1, bead `jev-pkd`; `git` reads config from `/dev/null`),
not a commit-miner test assumption. Verdict corrected to environment,
owner RCH worker (repaired). The per-line analysis (tests.rs:799,
git.rs:162) stands as the failure path, not the fault.
