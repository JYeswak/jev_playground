# Gate-edit session 2 (`KIT_GATE_EDIT=1`) - jev-sx9, jev-fmy, ratify ae01091

From pane 1 AmberWillow, 2026-09-24. Joshua approved this kind of session ("approval on all",
2026-09-24) and later handed session decisions to pane 1 ("none of that seems like me - use data").
This pane was launched with `KIT_GATE_EDIT=1` for the three items below only. When they are done it
exits, and the flag does not outlive the unit.

Confirm first: session start printed `kit-guard: KIT_GATE_EDIT=1, gate files are writable this
session`. If not, stop and call back.

## 1. jev-sx9 - TTSR kit-no-verify read exemption

`br show jev-sx9`. `.omp/rules/kit-no-verify.md`'s `core.hooksPath` condition fires when tool output or
the model's own text merely mentions `core.hooksPath` (4 interrupts, 0 bypasses, in gate session 1).
Give it the read exemption `bashVerdict` got in W1.4 (`4954b50`): a read (`git config --get
core.hooksPath`, `git config --list`, file reads, test output) stays quiet; a real re-point
(`git config core.hooksPath <path>`, `--no-verify`) still fires. Add selftest arms in
`scripts/selftest-ttsr-rules.sh` for both directions. Test with `omp ttsr test --json --rule <file>
--source tool --tool bash '<command>'` (the result is in `triggered`). Acceptance: selftest green,
`foundation/gates.sh` stage 80 green.

## 2. jev-fmy - gates runnable on a stranger's clone

`br show jev-fmy`. On a fresh clone with an empty HOME and a minimal PATH, 4 of 17 stages are RED:
44 (ast-grep absent), 50 and 60 (foundry loop-kit absent), 80 (omp install absent). Each stage must
either run on a stranger clone or report `SKIP (missing prerequisite: <name>, install: <how>)` with
exit 0 under an explicit `--portable` mode of `foundation/gates.sh` (the default mode on this machine
keeps failing closed exactly as today). Prove both: `python3 work/readme-stranger-run/run.py --with
br` shows gates rc 0 or only named SKIPs in portable mode, and on this machine the default mode is
still 17/17 with each stage's `--selftest` RED arm intact. README names the prerequisites (README is
free: coordinate with ReadmeStrangerRun via hub before editing it).

## 3. Ratify ae01091

`ae01091` added one line to `.omp/config.yml` (`extensions: ./.omp/extensions/jev-claim-check.ts`),
made by a pane-1 background agent that ran without kit-guard. Review it: it must add only that
extension and touch no `ttsr.disabledRules`. If it holds, record the ratification in a commit message
and on jev-sx9; if not, revert that line.

## Rules

AGENTS.md binds. Never delete anything. Reserve paths in Agent Mail if the mailbox lock is free;
stage explicit paths, read back `git diff --cached --stat`, path-limited commits, no amend, push per
commit, level tag in each subject. Close beads reason-first. Callback `CALLBACK-GATE2-DONE` to pane 1
via `ntm send jev --pane=1`, then `/exit`.
