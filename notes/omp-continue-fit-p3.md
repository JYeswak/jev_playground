# omp-continue fit (pane 3)

Read-only fit check of `omp-continue.sh` (member `omp-kit/scripts/omp-continue.sh`
of `/Users/josh/Downloads/omp-kit.zip`) against this repo. Nothing copied in,
nothing installed, `init.sh` not run.

## Assumption 1: `br ready` — HOLD

Opened: `br ready --json` (live run this turn).
`br` is on PATH and `br ready --json` returns rows (first row: parent drive
bead `jev-v8-kit-drive-m0e`, created_by RedMaple). The script's preferred
branch (`command -v br` + JSON id count) works here as written.

## Assumption 2: claim gate at `scripts/check-claim-discipline.sh` — MISS

Opened: `scripts/check-claim-discipline.sh` (absent), `foundation/kit/check-claim-discipline.sh` (present).
`ls scripts/check-claim-discipline.sh` → no such file. Our checker lives at
`foundation/kit/check-claim-discipline.sh` AND takes different argv
(`<claims.tsv> <README> <root>` vs the script's bare `sh scripts/check-claim-discipline.sh`
with no args). Both the path and the interface miss: run verbatim here, step 2
would report "gate missing" only by skipping (the `[ -f ... ]` guard), silently
dropping the honesty check rather than failing. A port must repoint the path
and pass the three args.

## Assumption 3: `init.sh` layout — MISS

Opened: `foundation/kit/init.sh` (absent), `foundation/kit/DRIVE.md` (line 12).
No `init.sh` exists under `foundation/kit/`. DRIVE.md records the decision:
"`init.sh` was not run. It would install a second pre-commit hook." There is
also no `.omp/loop-state` convention in this repo. The script's `STATE`
default (`.omp/loop-state`) would create fresh state rather than continue any,
and the human stop switch (`.omp/STOP`) has no documented producer here.

## Assumption 4: `.beads/issues.jsonl` — HOLD

Opened: `.beads/issues.jsonl` (live `head -c` this turn).
The file exists and holds rows (first row id `jev-0bp`). Only needed as the
step-1 fallback when `br` is absent; since assumption 1 holds, this path is
not exercised, but the file it would read is present and populated.
