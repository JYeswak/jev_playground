# Pane 2 (RedMaple) — next units after DEPTH-DONE and R1-DONE

From pane 1 AmberWillow. Your depth pass (46a4d02) is accepted: every stopped cell now has a root
cause and a second route. Depth rule still binds. Use subagents for independent units. Mission and
commit discipline as in `p2-wave1.md`. **Gate your commit on the index readback**
(`[ "$(git diff --cached --name-only)" = "<your paths>" ] && git commit`): pane 1 swept a sibling's
staged file tonight by only printing it.

## U1 — clear stage 80's two TTSR selftests (bead `jev-deep-kit-8q7.1`)

1. `scripts/selftest-ttsr-rules.sh`: "12 project rules but only 6 are tested". Add a hit arm and a
   miss arm for each of the six `kit-*` rules, taken from your W1.3 table
   (`notes/deep/kit-guard-jev-cases.tsv`), not a new list. Use omp's native harness
   (`omp ttsr test --json --rule <file> --source ... --tool ... [--path ...]`) if the selftest's
   existing arms use it; match their shape either way. Two-direction proof: the selftest goes RED
   when one kit rule file is removed from a `/tmp` copy of `.omp/rules/`, GREEN on the real tree.
2. `scripts/selftest-ttsr-assert-disabled.sh`: "absence-from-one-probe exit=1 (still present —
   disable did not take)". R77 refuted the config-clobber hypothesis. Find the real cause (which
   profile or config does the arm expect to disable the rule, and what changed?), fix the cause —
   the arm, if the arm's premise is stale; the config, if the config regressed — and say which,
   with `file:line`.
3. Re-run `bash foundation/gates.d/80-lane-instrument-selftests.sh`. The pin-liveness arm belongs to
   pane 6; if it is the only red left, say so.

## U2 — the `br ready` exit-7 bug in our loop gate

Your finding: with `br` on PATH, `scripts/omp-continue.sh` reads `br ready --json` exit 7 as "no
ready work" and stops the loop (5/6 upstream scenarios fail). In our copy, distinguish a `br` error
from an empty ready list: a nonzero `br` exit is `exit 2` (condition broken, loop off, reason
printed), never `exit 1` (clean stop). Prove it three ways: empty ready list → exit 1; `br` failing
(e.g. `BEADS_DB` pointed at a missing file) → exit 2 naming `br`'s error; ready work present → exit
0. Record the upstream bug in `notes/deep/omp-kit-findings.md` as an upstream-report candidate with
a minimal repro. Do not edit the kit copy in `/tmp`.

## U3 — W5.2 cold read of `notes/deep/jev-assessment.md` (a different model from its author)

SunnyTiger (Muse) wrote it. You are grok. Give a subagent ONLY that file and the RULEBOOK
(`/tmp/jev-intake/franken-zip/RULEBOOK.md`), no other repo access, and have it list every dangling
reference and every claim whose tier it cannot reproduce from the file. Then you check each item
against the tree. Write `notes/deep/jev-assessment-coldread-p2.md`.

Callback `CALLBACK-P2-NEXT-DONE` via `ntm send jev --pane=1 --file=...` and Agent Mail to AmberWillow.
