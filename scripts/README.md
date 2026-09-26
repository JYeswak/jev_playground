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

## Conventions these share

- **Test hooks over mutation.** `JEV_STATUS`, `JEV_SIDECAR`, `JEV_REPO`, `JEV_FORCE_MOVED` and
  `JEV_SELF_DIGEST_OVERRIDE` let a selftest drive a branch against copies. Every hook is
  fail-safe by construction or refused on a dirty verdict; none can manufacture a pass.
- **A transient is not a pass and not a failure.** Where an input can move mid-run, the script
  withholds its verdict rather than reporting one, and its foundation wrapper maps that to
  `UNMEASURED` rather than green.
- **Selftests are the load-bearing half.** A gate that cannot go red on a planted bad input is
  decoration, so every verifier here ships arms that fail when its rule is removed.
