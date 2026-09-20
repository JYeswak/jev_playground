# P2 — turn tonight's four rulings into the thing a stranger can read

`jev-vbh` BLOCKED is verified and accepted — third independent check, and not claiming
unadvancable work is right. Redirect below.

You produced four rulings tonight and **they exist only as four separate receipts.** A ruling is
only product when someone outside this lane can read it. That is the gap, and it outranks a fifth
mine.

| ruling | receipt |
|---|---|
| A11 join yield — HELD | `docs/demos/upstream-repro/a11-join-yield-20260920.md` |
| dig subset breakdown — HELD | `docs/demos/upstream-repro/dig-subset-breakdown-20260920.md` |
| A12 local refusal — REFUSE | `docs/demos/upstream-repro/a12-refusal-result-20260920.md` |
| A18 off-bus probe — REFUSE | `docs/demos/upstream-repro/a18-offbus-result-20260920.md` |

## The unit

Write `docs/demos/upstream-repro/cass-mountain-findings-20260920.md`: **one page, stranger
readable, no lane jargon.** It must answer, in this order:

1. **What we asked.** Does digging into CASS beat inventing an answer?
2. **The honest arc**, which is the actual finding and is more interesting than a win:
   digging beats inventing **in aggregate** (0.058 vs 0.159 on n=138) — and that aggregate
   **inverts on the slice that matters**, `S_wrong_selector` (n=16, 0.500 vs 0.250), where hits
   exist and answer nothing. The obvious fix (a local refusal) was built and **refused**: it
   fired on the slice regex rather than the condition, and traded 2 good digs for 2 bad.
3. **What is unmeasurable and why** — A18: all 20 K1 pairs are time-disjoint; mail proj 66 runs
   2026-08-31→09-01 while cass ws 617 runs 2026-06-17→07-27, **35 days apart**. Say
   `UNMEASURED`, never `0`.
4. **What a reader should take away.** State it as advice they can act on, not as our status.

## Rules for this page

- **Every number names its denominator**, and the denominator comes from the locked export
  (n=138), not from memory.
- **No claim without a linked receipt.** Link the four above.
- Flag prominently that `Y` is a **mechanical proxy**, not human labels, and that pane 3 is
  reviewing exactly that right now — if their review overturns the inversion, this page changes.
  **Write it so that is a one-line edit, not a rewrite.**
- Mark it `[pending]` until that review lands. Do not claim CLEARED anywhere; nothing here
  cleared.
- Include the unit bug you caught (microseconds vs milliseconds across the two DBs) as a
  practical warning — I reproduced it and it is the kind of detail that saves a reader a day.

## ACCEPTANCE

One page a person who has never read this repo can follow, with four working links, every number
carrying its denominator, and the arc ending in advice rather than status. **If you cannot state
the takeaway in one sentence, the page is not done.**

Do not run formatters or repo-wide gates. Exit codes unpiped. Commit on create.

`ntm --robot-send=jev --panes=1 --msg="CALLBACK-P2-WRITEUP-<DONE|BLOCKED>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."`
