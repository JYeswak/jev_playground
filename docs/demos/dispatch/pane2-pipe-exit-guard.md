# P2 — queue of 2. Finish one, fire its callback, START THE NEXT YOURSELF.

Your pin-liveness review: **accepted, PASS, no changes.** One correction for your own record —
you wrote *"UP-R16 row already unpinned after the RED"*, but the row is pinned:
`receipt=docs/demos/upstream-repro/ubs-gate-ruling-20260920.md digest=3a4796428ddbd003`. The row
was **repointed at a stable extract**, not unpinned. Your `rc=0` is right; the reason is not.
Worth flagging because "it passes because there is nothing to check" and "it passes because the
thing checked is correct" are different states, and this lane has confused them before.

## Unit 1 — the pipe-exit misread, now at four instances and all of them mine

Honesty pass 8 names this the top unguarded class:

```
cmd | head   ->  reads head's rc=0
cmd | tail   ->  reads tail's rc=0
```

Four times tonight I read a pipeline's exit status as the command's, twice inside checks
verifying guards built to stop exactly this kind of misread. The tick file has warned about it
all session. **Prose has not stopped it; that is the whole argument.**

Apply the full Creation Gate before building — consumer, gate, **observed** defect (the four
instances, cite them), retirement condition. Then decide honestly between:

- **a wrapper** (`scripts/rcof.sh <cmd...>` that runs the command unpiped, prints its output and
  its true rc) — buildable, but is it *wired*, or is it opt-in prose-with-a-script like R46 and
  R47? If opt-in, say so and weigh it.
- **a refusal** (`R48`) if the honest finding is that nothing can see an agent's shell pipeline.
  **I expect this is where it lands**, because the misread happens in a tool call, not in a
  committed file — the same reason R47 refused. If so, say it plainly and record the trigger.

**A refusal here is the likely correct answer and is worth as much as a guard.** Do not build a
wrapper nobody will call just to have built something.

## Unit 2 — then the session's hardening summary, as one readable page

`docs/demos/upstream-repro/hardening-20260920.md`: what a reader outside this lane should take
from tonight's hardening. The four guards with what each fires on, the two (probably three)
refusals with their triggers, and **the measurement that justifies the whole exercise**:

```
GATED classes, recurrences     TESTS.md 1 · numerals 0 · readme-counts 3 caught
UNGATED classes                selector/silent-zero 26 · denominator drift 8
```

State the honest limits: *wired* means a command exits nonzero, not that a class is eradicated;
`vgrep` closes one of three selector failure shapes. **One page, no jargon, links to the four
selftests so a reader can run them.**

Exit codes unpiped — literally the subject of Unit 1. Commit on create. No formatters or
repo-wide gates; I verify at phase end.

`ntm --robot-send=jev --panes=1 --msg="CALLBACK-P2-<UNIT>-<DONE|BLOCKED>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."`
