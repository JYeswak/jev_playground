# Gate-edit session 6 (`KIT_GATE_EDIT=1`) - CI is red; one assertion in one gate file

From pane 1 AmberWillow, 2026-09-24. Joshua approved this kind of session ("approval on all",
2026-09-24). The flag lets you edit kit gate paths (`.omp/kit-guard.json` gatePaths, which include
`githooks/*`). Do the one item below, then exit so the flag does not outlive the unit.

## 1. Mission

Validate Jev, build tools from what survives, liven an omp surface, dogfood it, keep the README a
stranger can run. CI on main is the backstop for every gate, and it is red now.

## 2. The defect (measured by pane 1)

`scripts/ci-main-status.py` changed its missing-gh message at 18f2c45 (bead jev-7lgx, closed on a
non-author check): `CI main NOT_RUN gh not installed; install it from https://cli.github.com, then
run: gh auth login`. The pre-push hook passes that reason through, so a push without gh now prints
`CI status NOT_RUN: gh not installed; install it from https://cli.github.com, then run: gh auth
login`. That is the intended behaviour: the stranger is told how to get gh.

`githooks/pre-push-ci-red-warning.sh` selftest arm 3 (lines 199-201 at cb1025d) requires stderr to
EQUAL `CI status NOT_RUN: gh not installed`, so arm 3 fails and the registered-suites job is red:
run 36067498925 on 75fd99b names `githooks/pre-push-ci-red-warning.sh --selftest ... FAIL`. The
packet that specified the arm (gate-edit-5.md item 3) only asked for "exit 0, stderr says NOT_RUN,
never green"; the exact-string pin is stricter than the contract and pins another script's wording.

## 3. The item

Change arm 3's assertion, and only that, so it holds the contract without pinning the wording:

- stderr is exactly ONE line;
- that line starts with `CI status NOT_RUN: gh not installed`;
- it contains no `CI on main is RED` and no success/green line (it is already required that the push
  landed and exited 0; keep those checks).

Update the arm's label text to match. Do not touch `scripts/ci-main-status.py`, its tests, arms 1,
2, 4, 5, or the hook body.

Prove it both ways in a `/tmp` clone: the fixed selftest passes 5/5 at current main; planting a
second line on the gh-absent path (for example an extra `notrun` call) makes arm 3 fail; planting a
reason that does not start with `gh not installed` makes arm 3 fail. Then
`python3 scripts/run-registered-suites.py` reads 0 fail, and `bash foundation/gates.sh --portable`
and `--selftest --portable` exit 0.

## 4. Rules

- Register with Agent Mail under a fresh name; reserve `githooks/pre-push-ci-red-warning.sh`,
  reason `jev-4a9s`.
- Path-limited commit (`git add -- <path>` then `git commit --only -- <path>`), no deletes, no
  amend, subject with a verification level (`[mutation]` only after both plants failed arm 3).
- If a hook refuses your commit, read its stderr and fix the cause; never skip or re-point a hook.
- No key, no model call.

## 5. Close

Comment on bead `jev-4a9s` with the selftest output, both plant results, the runner line and the
commit sha. Leave it open for pane 1's non-author check (pane 1 will confirm the next CI push run
is green). Callback `CALLBACK-GATE6-DONE` to pane 1 via `ntm send jev --pane=1`, then `/exit`.
