# Gate-edit session 4 (`KIT_GATE_EDIT=1`) - bead `jev-09qj`

From pane 1 AmberWillow, 2026-09-24. Joshua approved this kind of session ("approval on all",
2026-09-24). This pane runs on the `claude` profile (Anthropic). The flag lets you edit kit gate
paths (`.omp/kit-guard.json` gatePaths). Do the one item below, then exit so the flag does not
outlive the unit.

## 1. Mission

Validate Jev, build tools from what survives, liven an omp surface, dogfood it, keep the README a
stranger can run. The gates are what make every published number trustworthy. A gate that passes on
the wrong scope is worse than no gate, because the PASS line is read as covering files it never saw.

## 2. The item: stage 30 scans the wrong directory

`foundation/gates.d/30-no-secrets.sh:14` sets `here` to `foundation/` (the script's parent's
parent is `foundation`, not the repo root), and line 27 greps only there. You measured it: a planted
`apikey_` value under `work/` passes; the same plant under `foundation/` goes RED. Its selftest
passes because it plants inside the one directory it scans.

- Scan what can be committed: every tracked file plus every untracked file that is not ignored
  (`git ls-files --cached --others --exclude-standard`, or `git grep --untracked`), from the repo
  root, keeping the current exclusions and both patterns. Do not scan ignored trees (vendored
  clones, `node_modules`, `.venv`); they cannot be committed here.
- The selftest must plant OUTSIDE `foundation/` (for example under `work/`) and require RED naming
  the plant. Keep one plant under `foundation/` too, so neither scope can regress silently. Plants
  are removed afterwards, even on failure.
- Measure before and after: runtime of the stage on this tree, and whether the widened scan finds
  any real hit today. A real hit is a finding: report it with the path, do not print the value, and
  do not weaken the pattern to make it pass.
- Fix the header comment and `GATES.md:83` if they describe the scope wrongly.
- Show it both ways: `bash foundation/gates.d/30-no-secrets.sh` and `--selftest` exit 0; with the
  old line 14 planted back in a `/tmp` clone, the new selftest goes RED. Then `bash
  foundation/gates.sh --portable` and `--selftest --portable` exit 0.

## 3. Rules

- Path-limited commits (`git add -- <paths>` then `git commit --only -- <paths>`), no deletes, no
  amend, subject with a verification level.
- Touch only stage 30, its selftest, and the docs lines that describe it.

## 4. Close

Comment on `jev-09qj` with the before/after measurements and commit shas. Leave it open for a
non-author check by CopperHeron (pane 3). Callback `CALLBACK-GATE4-DONE` to pane 1 via
`ntm send jev --pane=1`, then `/exit`.
