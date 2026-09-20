# Should you dig into past work before inventing an answer? `[pending]`

We tested this on 138 real questions asked against CASS, our archive of
~59,800 past agent conversations (~5.2M messages). The question: when the
archive returns hits, should the agent reuse them ("dig") or write from
scratch ("invent")?

## The honest arc

Digging wins **in aggregate**: average loss 0.058 digging whenever any hit
exists, vs 0.159 always inventing (n=138 locked questions)
([receipt](./dig-subset-breakdown-20260920.md)).

That aggregate **inverts on the slice that matters**. On the 16 questions
that claim something is missing ("no such field", "undefined", …),
digging scores 0.500 vs 0.250 inventing — twice as bad **if you price a wrong
dig at twice a wrong invention, which is our assumption, not a measurement**.
Price them equally and the slice is a tie. What survives either pricing is the
direction: on these questions digging never beats inventing. The hits exist and
answer nothing. The pooled win was carried by the other 122 questions, where
digging was nearly perfect.

The obvious fix was built and **refused**: a rule that skips digging on
suspicious questions caught 2 of the 4 empty hits but killed 2 good digs
— a coin, not a policy. Worse, it keyed on the *wording* of the failing
slice rather than on *whether any hit actually answers*; a rule fitted to
16 rows will not generalize
([receipt](./a12-refusal-result-20260920.md)).

Separately, joining agent-mail threads to archive sessions works at the
project level (20 exact path matches, e.g. 465 mail messages ↔ 107 archive
sessions for one project) — but every match is captured by plain
string-equality, so there is no job here for a paid model
([receipt](./a11-join-yield-20260920.md)).

## What is unmeasurable, and why

We could not test whether agents acknowledge requests off-channel: all 20
project matches are **time-disjoint** — e.g. the richest pair's mail runs
2026-08-31→09-01 while its archive sessions run 2026-06-17→07-27, 35 days
apart. Say `UNMEASURED`, never `0`
([receipt](./a18-offbus-result-20260920.md)).

## Takeaway

**Dig by default, but never dig an absence-claim on hit-count alone —
demand evidence in the hit that it answers, or invent.**

## Caveats a reader needs

- `Y` (which digs were "right") is a **mechanical proxy** — receipt-shaped
  text / wrong-selector traces — not human labels.
- > **Pane-3 non-author review: LANDED, and it WEAKENS the headline.** Both numbers
  > recompute exactly, but the inversion is **fragile in two measured ways**, each
  > reproduced independently ([review](./mines-nonauthor-review-20260920.md)):
  > **(a) the "twice as bad" is a chosen constant.** A wrong dig is scored at 2× a wrong
  > invention. At a 1:1 cost the slice is an exact **tie** (0.250 vs 0.250), not a loss.
  > The *direction* — digging never beats inventing here — holds at every cost ≥1; the
  > magnitude does not exist without the 2.
  > **(b) the inversion hangs on ≤2 proxy labels.** Flip one mechanical `Y` zero to one
  > and digging still loses (0.375 vs 0.3125); flip two and **digging wins** (0.250 vs
  > 0.375). Sixteen rows decided by four labels from an uncalibrated proxy.
  > Snippets are not in the export, so human calibration is impossible from the pinned
  > file — that grading is the load-bearing next step, and until it exists **read the
  > takeaway below as a caution, not a measured law.**
- Practical warning, reproduced: the mail DB timestamps are in
  **microseconds**, the archive DB's in **milliseconds**. Compare them raw
  and every time-window join silently returns zero — the same zero a real
  disjointness finding produces. Normalize first.
- Nothing here cleared; no promotion. n=138 with 30 near-duplicate probe
  rows, one recent 120k-message window, no full-index search (index
  rebuilding at measurement time).
