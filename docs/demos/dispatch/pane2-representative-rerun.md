# P2 — re-run dig-vs-invent on a representative sample. This is the test your own audit forced.

Your sampling frame is verified. I re-derived two axes independently:

```
mean message length   window 3,616 chars   whole 764   = 4.73x
window date span      2026-01-31 .. 2026-07-27
whole  date span      2026-01-30 .. 2026-07-27
```

The second one is the finding. **The "recent 120k window" spans the entire corpus era** — message
ids are not chronological, so a `order by id desc limit 120000` slice is not a time window at
all. We published a caveat calling it "one recent 120k-message window" and **both words were
wrong**: it is neither recent nor a window in the sense a reader would assume.

(Small discrepancy, flagged not waved: you report 3,544 mean chars, I measure 3,616 — different
content column or null handling. Immaterial to the 4.6–4.7× conclusion; worth a line in the next
receipt so the next reader is not confused by two numbers.)

## The unit

Our dig-vs-invent finding — the one on the public page, human-calibrated, that survived two
attacks — rests entirely on that unrepresentative slice. **Re-run it on a defensible sample and
see whether it survives.**

1. **Draw a representative sample**: random over all 59,807 conversations (or all messages,
   justify which), sized so you can finish it tonight. `ORDER BY RANDOM()` with a **fixed seed
   recorded in the receipt**, so the draw is reproducible. State the size before you look at
   any result.
2. **Re-run the same 138-question protocol** — same queries, same mechanical `Y`, same loss at
   both 1:1 and 1:2. Change nothing else. If the questions cannot be re-asked without live
   search, say so and stop: `UNMEASURABLE` is a real outcome and better than substituting a
   different protocol and calling it the same test.
3. **Pre-register the falsifier first**, as you have all night. Mine, stated now so it is on the
   record before your draw: **I expect the aggregate direction to hold and the `S_wrong_selector`
   inversion to weaken**, because that slice's rows are long receipt-shaped messages and the
   window over-samples long messages by ~4.7×.

If the inversion vanishes on a representative sample, **the public page is wrong and we correct
it tonight**. That is the outcome I am most interested in.

## Do not

Do not rebuild the index. Do not regenerate the locked n=138 export — it stays pinned as the
window-based comparison arm. Read-only sqlite throughout.

Exit codes unpiped. `[receipt]` for result-recording commits. Commit on create.

`ntm --robot-send=jev --panes=1 --msg="CALLBACK-P2-REPSAMPLE-<DONE|UNMEASURABLE|BLOCKED>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."`
