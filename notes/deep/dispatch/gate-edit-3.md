# Gate-edit session 3 (`KIT_GATE_EDIT=1`) - bead `jev-80lj`

From pane 1 AmberWillow, 2026-09-24. Joshua approved this kind of session ("approval on all",
2026-09-24). This pane runs on grok. The flag lets you edit kit gate paths
(`.omp/kit-guard.json` gatePaths: `foundation/gates.sh`, `foundation/gates.d/*`,
`foundation/kit/check-*.sh`, `githooks/*`, `.omp/config.yml`, `.omp/rules/kit-*.md`,
`.omp/extensions/kit-guard/*`). Do the four items below in order, then exit so the flag does not
outlive the unit.

## 1. Mission

Validate Jev, build tools from what survives, liven an omp surface, dogfood it, keep the README a
stranger can run. The gates are what make every published number trustworthy. A gate that passes
on nothing, or that fails at random, is worse than no gate.

## 2. Items

**(d) first. Stage 80 went RED once and the failing sub-check was never named.**
- Pane 1 measured one full `gates.sh` run with stage 80 RED (exit 1, 244 s). The same stage then
  passed standalone (rc 0, 164 s), and the whole suite passed 17/17 at `23ef548` (rc 0).
- `gates.sh` prints only the head of a RED stage's output, so the failing arm was never named.
- Fix: a RED row must print the failing sub-check's name and its last lines.
- Then run stage 80 at least 5 times. Report per run: rc, wall time, and any FAIL line.
- Say whether it is flaky, and which arm. One untested hypothesis: the omp ttsr arms near their
  time budget.

**(a) Silent pass.** In default mode, `scripts/selftest-ttsr-rules.sh` and
`scripts/selftest-ttsr-assert-disabled.sh` exit 0 when `omp` is absent. That is an empty scan set
wearing a PASS.
- Required behaviour: exit 8 with a named SKIP under `--portable`, RED otherwise.
- Prove both directions by running each script with `omp` hidden from PATH.
- These two scripts are under `scripts/`, not a gate path, but stage 80 calls them. Edit them here
  so the change and its gate land together.

**(b) False positive.** kit-guard's B5 regex fires on a `[ -n` shell test in the same command as a
commit.
- Add a quiet arm: a command containing both `[ -n "$x" ]` and a plain `git commit -m ... -- path`
  must not fire.
- Keep the fire arms: `--no-verify`, `-n` as a commit flag, `core.hooksPath` set, `-c` override,
  `--unset`.
- Fix the regex with the smallest change that satisfies both. Run the kit-guard test suite,
  `bun test ./.omp/extensions/kit-guard/kit-guard.test.ts`.

**(c) Two definitions of "portable".** `.github/workflows/gates.yml` maps skips after the fact
instead of running `bash foundation/gates.sh --portable`.
- Switch CI to `--portable`, so CI and a stranger see the same verdict.
- Do not push a workflow change you have not validated. Run `actionlint` if it is installed, and
  otherwise say so.

**Not yours: stage 44** is RED on the adapter pin (`jev-ygl7`, pane 1). Do not touch
`upstream/MANIFEST.tsv` or stage 44.

## 3. Acceptance

- Every fix has a planted RED arm and a green arm.
- `bash foundation/gates.sh --selftest` passes.
- `bash foundation/gates.sh` passes except stage 44; say so.
- `bash foundation/gates.sh --portable` passes.
- Stage 70 stays green: register any new test in `TESTS.md`.

## 4. Rules

- Path-limited commits only: `git commit -m "..." -- <paths>`. Other panes stage into the same
  index; two whole-index sweeps happened on 2026-09-24.
- Each commit subject carries a level tag.
- Reserve paths in Agent Mail under a registered adjective+noun name.
- No deletes of any kind, including `/tmp` scratch you created.
- Close `jev-80lj` with the reason first, or comment per item.
- Callback `CALLBACK-GATE3-DONE` to pane 1 via `ntm send jev --pane=1`, then `/exit`.
