# P2 — queue of 3. Finish one, fire its callback, then START THE NEXT YOURSELF.

Joshua's standing question tonight: *why are we not hardening the mistakes we keep making?* The
measurement says he is right and says where:

```
GATED classes, recurrences tonight    TESTS.md sync 1 · numerals 0 · readme-counts 3 caught
UNGATED classes                       selector/zero-hit 26 · denominator drift 8
```

**Classes turned into code stopped recurring. Classes turned into prose did not.** I shipped the
first guard (`scripts/vgrep.sh`, silent-zero, wired via stage 80's `scripts/selftest-*.sh` glob,
8 arms). You take the next one.

## Unit 1 — the denominator-drift guard

**Observed defect, 8 instances**: a published share whose denominator moved underneath it —
`77,767 → 78,242`, `matched=15525 → 15618`, `bv` actionable `23 → 20 → 19`, README `22 of 22` when
the census held 24 clones and 11 RUN rows. **A share whose denominator drifted is wrong even
though nobody edited the sentence.**

Build `scripts/pinned-denominator.sh` on the vgrep pattern:
- it takes a claimed denominator and the command that regenerates it, and **fails loudly when
  they disagree**;
- ship `scripts/selftest-pinned-denominator.sh` so stage 80 discovers it automatically — **do not
  add a new gate stage**, instruments are frozen at their arm counts;
- every arm plants the real defect and requires a FIRE. An arm that only proves the happy path is
  the thing this lane calls a gate that fires on everything.

**Answer all four Creation Gate questions in the file header** — consumer, gate, observed defect,
retirement condition — or it does not get built. Retirement must be measurable.

**State the boundary honestly, as vgrep does.** vgrep closes 1 of the 3 selector failures I
replayed through it and its header says so. If yours cannot catch a drift that happens between
two runs of the same command, say that in the header.

## Unit 2 — count what is still unguarded

With both guards landed, re-derive the table above: which defect classes from tonight's ledger
(`docs/demos/upstream-repro/commit-learnings-20260919.md`) now have a **wired** guard, and which
are still prose only? Rank the unguarded remainder by recurrence count. **Do not build a third
guard in this unit** — produce the ranked list so the next one is chosen by evidence.

## Unit 3 — the highest-ranked remaining class, if it is mechanizable

If the top unguarded class cannot be mechanized without false-positives-by-construction, **write
the R18-style refusal into `NEGATIVE_EVIDENCE.md` with its trigger instead** — use **R45 or
higher**, R41/R42/R43 have collisions and R44 is taken. A refusal with a trigger outranks a gate
that fires on everything.

## Standing rules

Exit codes unpiped. Use `scripts/vgrep.sh` for any grep used as proof. Commit on create — this
tree branch-switches under us and uncommitted work has been lost twice today. No formatters, no
repo-wide gates; I verify at phase end.

`ntm --robot-send=jev --panes=1 --msg="CALLBACK-P2-<UNIT>-<DONE|BLOCKED>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."`
