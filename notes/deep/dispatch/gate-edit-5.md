# Gate-edit session 5 (`KIT_GATE_EDIT=1`) - bead `jev-bfku` part 3

From subagent CiWatch (pane 1's session), 2026-09-24. Joshua approved this kind of session ("approval
on all", 2026-09-24). The flag lets you edit kit gate paths (`.omp/kit-guard.json` gatePaths, which
include `githooks/*`). Do the one item below, then exit so the flag does not outlive the unit.

## 1. Mission

Validate Jev, build tools from what survives, liven an omp surface, dogfood it, keep the README a
stranger can run. CI on main is the public backstop for every gate. A red CI result nobody reads
protects nothing: from cf70e28 (15:19Z) to ff8316d (21:10Z) on 2026-09-24, `registered-suites`
failed on every push to main, about 55 runs, on one test (`work/sr-adopt/test_runner_gates.py`), and
no agent noticed for six hours. PaidStop fixed it at 8373173.

## 2. What already exists (do not rebuild it)

- `scripts/ci-main-status.py` (commit 01fddd8): reads the latest completed `gates.yml` push run on
  main and prints `CI main <sha7> <conclusion> <run id> <age>`, then for a failure each failed job
  and its rows (`RED  <stage>` plus its `FAIL  <check>` lines, a runner row ending in a tab plus
  `FAIL`, or `RED named <row>`), and a `STALE ...` line when a newer push has not finished. Exit 0
  green, 1 red, 2 NOT_RUN. Each gh call has a 20 s timeout (`CI_MAIN_STATUS_TIMEOUT`).
- Its tests: `python3 -m unittest work/ci-main-status/test_ci_main_status.py` (13 tests, fixtures
  from real gh output, no network).
- `scripts/fleet-idle-watch.py --once` already prints the line every conductor round.

## 3. The item: a pre-push warning when main is red

Add `githooks/pre-push` (a thin wrapper, same `dirname "$0"` resolution as `githooks/commit-msg`)
and its impl `githooks/pre-push-ci-red-warning.sh`:

- Only when the push updates `refs/heads/main` (read the ref lines git gives the hook on stdin),
  run `python3 scripts/ci-main-status.py` from the repo root.
- Exit 1 (red): print to stderr, in this order: `CI on main is RED at <sha7> (run <id>)`, the
  script's job and row lines verbatim, then one line asking the pusher to fix it or say why in the
  commit being pushed before pushing more (`fix the RED row above, or name it in your subject`).
- Exit 0 (green): print nothing. A `STALE` line may be printed as one line of context; it must not
  change anything else.
- Exit 2 (NOT_RUN) or any other exit, or the script missing: print one line `CI status NOT_RUN:
  <reason>` so a missing check is visible, never silent and never read as green.
- **Warning only, never blocking.** The hook exits 0 in every case above. A push must never be
  refused because GitHub, gh, or the network is slow or down. Bound the whole hook: if the script
  runs past 45 s, print `CI status NOT_RUN: timed out` and exit 0.
- No model call and no key. gh is read-only here.

Selftest, the same RED-arm discipline as every gate (`githooks/pre-push-ci-red-warning.sh
--selftest`), with a stand-in `gh` on PATH so there is no network:

1. red stand-in (return `work/ci-main-status/fixtures/list-red.json`, `view-36059723283.json` and
   `log-36059723283.txt`): the hook exits 0 and its stderr names
   `work/sr-adopt/test_runner_gates.py` and the fix-or-say-why line.
2. green stand-in (`list-green.json`): exit 0, stderr empty.
3. gh absent from PATH: exit 0, stderr says `NOT_RUN`, never green.
4. a push that does not touch `refs/heads/main`: exit 0, script not run.
5. a gh stand-in that sleeps past the bound: exit 0 within the bound plus a few seconds.

Show it both ways in a `/tmp` clone: plant `exit 1` on the red path (making the warning block) and
the selftest must go RED; plant `exit 0` before the stderr print on the red path and the selftest
must go RED. Register the selftest as a TESTS.md table row with its `Run:` command, as
`githooks/commit-msg-verification-level.sh --selftest` is, so `python3
scripts/run-registered-suites.py` runs it. Then `bash foundation/gates.sh --portable` and
`--selftest --portable` exit 0, and the runner reads 0 fail.

Wiring: this repo's hooks come from `githooks/` via the stamp install. Say in the commit how a fresh
clone gets the pre-push hook (the same install step as commit-msg); do not change the hook path
setting itself.

## 4. Rules

- Path-limited commits (`git add -- <paths>` then `git commit --only -- <paths>`), no deletes, no
  amend, subject with a verification level (`[mutation]` only after both plants went RED).
- Touch only `githooks/pre-push`, `githooks/pre-push-ci-red-warning.sh`, the TESTS.md row, and
  the GATES.md line that lists hooks, if it lists them.
- If a hook refuses your commit, read its stderr and fix the cause; never skip or re-point a hook.

## 5. Close

Comment on `jev-rt33` (the bead for this item; `jev-bfku` is closed) with the selftest output, both
planted-mutation results, and commit shas. Leave it open for a non-author check. Callback
`CALLBACK-GATE5-DONE` to pane 1 via
`ntm send jev --pane=1`, then `/exit`.
