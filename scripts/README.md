# `scripts/` registry

Eleven scripts. Re-derive the count with `ls scripts/ | wc -l` rather than trusting this line; a
number written down goes stale silently, and two have already done so in this repo.

This file exists because `foundry/flywheel/stamp-check.sh` refuses an unregistered scripts folder:
*"scripts folder 'scripts' has 11 scripts but NO registry doc enumerates them"*. An unenumerated
tool directory is one where nobody can tell a live instrument from an abandoned one.

## Lane state

| Script | Does | Exit codes beyond 0/1 |
|---|---|---|
| `lane-status.sh` | renders `docs/demos/STATUS.tsv` and verifies every cited receipt exists and matches its pinned digest | 3 missing receipt, 6 untyped receipt, 10 transient, 11 spliced self |
| `selftest-lane-status-integrity.sh` | 18 arms against `lane-status.sh`, each with a planted bad input | 6 a transient counted, never passed |

## Sidecar and citation verifiers

| Script | Does | Exit codes beyond 0/1 |
|---|---|---|
| `verify-other-reasons.sh` | checks the `other`-reason sidecar against STATUS: exact coverage both ways, three-way digests, resolvable locators. Snapshots its inputs and verifies the copies | 10 inputs moved during both captures, 13 cited evidence resolves outside the repo |
| `selftest-other-reasons.sh` | 17 arms against the above, including symlink, hardlink and forced-transient policy | — |
| `verify-reason-numerals.sh` | checks that every numeral in a verdict's reason opens in the receipt cited for it. Hand-run by ruling; hits need a human | 12 a cited numeral cannot be opened |
| `selftest-reason-numerals.sh` | 9 arms, including two encoding real false negatives this gate once had | — |
| `audit-score-lineage.sh` | checks that score-bearing receipts are typed as such rather than inferred from a filename | — |
| `selftest-score-lineage.sh` | 8 type-driven arms against the above | — |

## Verification and publication

| Script | Does | Exit codes beyond 0/1 |
|---|---|---|
| `bootstrap-compaction.sh` | fetches the pinned `fast-jev-compaction` sibling, builds `dist/`, and `npm install`s `compaction/`. Idempotent. `--check` exits 1 when a fresh clone would fail stage 40 | — |
| `verify-frozen.sh` | runs `foundation/gates.sh`, every demo's tests and mutation harness, and the probe's offline replay inside a git worktree **pinned to a commit**, then `cmp`s the executables. Stage 40 is bootstrapped; stages 50/60 still need `LOOP_KIT` | — |
| `sync-docs.sh` | fetches the mirrored primary sources; `--check` verifies every byte against `MANIFEST.tsv` | — |
| `jev-probe.mjs` | one live Jev call, or `--replay` to decode a recorded response with no network and no key | 2 no key present |
| `render-results.py` | renders the README Measured wins table from committed scorer/receipt outputs; `--check` fails on drift | 1 on drift |
| `repro-commit-only-sweep.py [REV]` | jev-rknc acceptance: rebuilds the real e03ef53d state (1 owned bead row plus 2 peers' edited rows in `.beads/issues.jsonl`) in a throwaway repo. `git commit --only` must sweep the peers' rows; a private-index row overlay must land only the owned row with the worktree untouched. Retire the RAW arm when LAND1 ships | 1 defect not reproduced or control dirty, 2 refused before any git write |
| `selftest-fixture-isolation.sh` | jev-n3lx / jev-90id: runs `selftest-pin-liveness.sh`, `selftest-serialized-add.sh`, `gates.d/60`, the commit-msg hook `--selftest`, `run-registered-suites.py --selftest` and the FULL `publish-export.sh` (in a fixture repo that is its own caller) with a decoy repo exported as `GIT_DIR`/`GIT_WORK_TREE`/`GIT_INDEX_FILE`, plus a verbatim replay of miniwob's `check_provenance`; the decoy's config, refs, reflog and staged entries must not change. Each subject is also run with its scrub deleted and must change the decoy, as must a planted unscrubbed fixture (15 arms). Discovered by `gates.d/80` | — |
| `publish-export.sh [--check-only \| --scan DIR]` | builds the allowlisted, scrubbed, single-commit export of the public playground and scans it. Diagnostics are counts and `path:line` only, never matched text. Key-shaped lines are explained only by the AWS documentation example or an exact row in `docs/publish-key-exceptions.txt` (path + whole-line sha256 + hit count); opaque `thinkingSignature` values are redacted in the export copy only. `--scan DIR` scans any tree read-only. Never run it from the real repo without intending to replace `../jev_playground-export` | 1 findings, 2 usage or missing tool, 4 scanner error (a grep/git failure other than no-match, or a malformed exceptions row) |
| `selftest-publish-export-scan.sh` | jev-x5cy: 40 arms against `publish-export.sh`: six planted key shapes, a home path, `encrypted_content` and a signature blob are refused by `path:line` with no planted text printed; a no-match tree is clean (the original silent-abort defect); exact exceptions bind path, whole line and hit count; an unreadable file and a malformed row are exit 4, never a pass; the full build in a fixture repo redacts the blob in the export only and refuses a planted key before `git init`. `PES_SUBJECT` swaps in a mutated copy (six mutants recorded in `docs/evidence/jev-x5cy-key-hit-rulings-20261011.md`). Discovered by `gates.d/80` | — |

## Conventions these share

- **Test hooks over mutation.** `JEV_STATUS`, `JEV_SIDECAR`, `JEV_REPO`, `JEV_FORCE_MOVED` and
  `JEV_SELF_DIGEST_OVERRIDE` let a selftest drive a branch against copies. Every hook is
  fail-safe by construction or refused on a dirty verdict; none can manufacture a pass.
- **A transient is not a pass and not a failure.** Where an input can move mid-run, the script
  withholds its verdict rather than reporting one, and its foundation wrapper maps that to
  `UNMEASURED` rather than green.
- **Selftests are the load-bearing half.** A gate that cannot go red on a planted bad input is
  decoration, so every verifier here ships arms that fail when its rule is removed.
