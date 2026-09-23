# v8 checker challenge (jev-v8-kit-drive-m0e.1, TopazRaven, 2026-09-23)

Zips: `/tmp/jev-rc-p1/fa48` (v8) vs `/tmp/jev-rc-p1/fa44` (v7).

## Hash compare (measured, not remembered)

- `diff -r fa48/starter-kit fa44/starter-kit` → no output: starter-kit **SAME**.
- `sha256sum` of both `RULEBOOK.md` → `034b8c23…b1d3696c4ea` both: RULEBOOK **SAME**.
- The v8 delta is elsewhere (`shareable/` pages per DRIVE.md); the enforced
  slice is byte-identical to v7.

## Four commands (exit codes pasted)

Plants live in `/tmp/v8plants/` (outside the repo, nothing to clean inside it).

1. v8 `check-claim-discipline.sh` on a matching `enforce=yes` plant
   (`planted-hit`, pattern present, proof exists — a working checker PASSes):
   exit **1**. Output: `0 passed, 1 failed, 2 skipped (0 enforced, 0 actually
   checked, 0 pattern-unmatched)`. The rowlist shows the whole TSV row
   collapsed into the label field — the tab→SOH `read` split fails on this
   `/bin/sh`, so the row is skipped, never checked, never named.
2. v8 `check-claim-discipline.sh` on an unmatched `enforce=yes` plant
   (`planted-miss`, pattern absent — a working checker FAILs naming the row):
   exit **1**, same `0 enforced` summary. It fails only via the decorative
   zero-enforced fallback and never names `planted-miss`.
3. v8 `check-readiness.sh` on a design-only sign-off plant (SIGN-OFF says
   "design" three times with a date): exit **0**,
   `READY: all 12 planning-packet sections present with substance.` A working
   checker refuses this packet.
4. `foundation/kit/check-claim-discipline.sh --selftest`: exit **0**,
   `SELFTEST_PASS: unmatched enforce=yes refused, matching row passed,
   missing file refused`.
5. `foundation/kit/check-readiness.sh --selftest`: exit **0**,
   `SELFTEST_PASS: design-only sign-off refused, relative path uses the
   given root, signed packet passed`.

Verdict: the v8 claim checker **fails to see a planted enforce=yes row**
(blind on this shell), and the v8 readiness checker **accepts a packet the
port refuses**. Adopting the zip scripts would restore both holes. Keep the
`cef0e02`/`a53190f` ports.

## Challenge on pane 3's gate (same turn)

`foundation/gates.d/17-kit-demotion.sh --selftest`: exit **0**,
`SELFTEST_PASS: plant demoted as …/stage-plant-proof.txt; …`. It **names the
plant**, so the challenge condition (pass without naming) is not met — no
mail to MistyTurtle sent.

## Boundary

Did not edit `foundation/kit/`. Did not run `init.sh`. DRIVE.md callback log
is pane 1's to append (this bead denies me `foundation/kit/` writes).

NO-CLAIM: a hash compare is not an application of the pack.
