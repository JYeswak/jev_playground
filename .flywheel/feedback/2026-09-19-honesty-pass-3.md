# Honesty pass 3 — 2026-09-19, commits `16be46c..77bf272` (28 non-merge)

Boundary test unchanged: **does running code branch on it, or can a non-lane reader consume it?**

## Tally

| class | n | share |
|---|---|---|
| **USER** | **19** | 68% |
| ENABLER | 6 | 21% |
| PROCESS | 3 | 11% |
| UNKNOWN | 0 | 0% |

**Verdict: HEALTHY.** Highest USER share of the three passes — 50% → 68%. All 28 classified.

## The shape of this block: it is almost entirely self-correction

Nineteen USER commits, and **eleven of them fix or retract something we had already published**:

| what we published | what was true |
|---|---|
| `FP 0/40` | two cases never committed → **`0/38`** (`ad9da04`, R34) |
| "extension cannot explain its own output" (R33) | `command` was on the row all along → **retracted** (`e27b536`) |
| `grep -cE … # 0` as proof | **exits 1** — proof-of-absence returned failure on success (`b194b55`) |
| installer works | corrupted inline-list configs, then reported GREEN (`fb137d2`) |
| five census rows deleted as unsupported | all five **had receipts** one `ls` away (`caf324d`) |
| `dcgVerdict: "unknown"` ×27 | every one a default, never an observation (`d8472cc`, R38) |
| registry entry cites the P2-29 callback | a callback is not a durable artifact (`b886a9c`) |

**Not one of these was found by reading.** Every single one was found by *running the thing*, by
*cloning fresh*, or by *a non-author grading it*. That is the block's finding, and it is worth
more than the tally.

## What counted as PROCESS (3)

`a0fe97d` (an audit receipt superseded by the README table two commits later), `835d61b` (a
registry entry I had to correct the same hour), `3b30957`/`2100286` counted as USER because each
carried a reproducible defect — a grade that finds a real defect is product, not bookkeeping.

## The conductor's ledger for this block, stated plainly

- **1 published false claim** (R33) — mine, retracted within the hour after both Jev and pane 3
  corrected me.
- **1 over-deletion caused by my packet wording** — I wrote that deletion was "preferred" and did
  not require an `ls` for a receipt first. *A preference without a check is an instruction to
  skip the check.*
- **1 relayed premise that was wrong** — Jev's "the residual keeps writing fiction"; `makeRecord`
  did not store it. Caught by reading the code before passing the packet on.
- **1 refuted prediction** (R36) — I named inline-corpus circularity as the likely defect in
  `verify-claim.mjs`; it was a real `import()` of three committed corpora.
- **1 fabricated file tag** rejected by the edit tool. Correct behaviour from the tool.

## Carried forward

1. **Two mechanical tripwires now exist where written rules had failed repeatedly**: `requireKey`
   (absence must be proven against the record's own keys) and R38's grep for `?? 'unknown'`.
   Neither can force its own use; the test is whether a ninth/third instance occurs.
2. `promoted 0` stays. One artifact is live on a working profile; that is not a promoted
   candidate and conflating them would inflate the headline.
3. A fresh clone still does not install end to end, **by design** — mirrors and the sibling
   upstream clone are not ours to ship. The bar is *actionable failure*, not *no failure*.
