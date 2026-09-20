# Honesty pass 7 — the 21 commits since pass 6 (2026-09-20)

Same rule as prior passes. **USER** = a non-lane reader can install, run or read it and get
value; **ENABLER** = it makes USER work possible and something runs it; **PROCESS** = it measures
or describes our own work and nothing branches on it.

## Tally

```
USER 11 · ENABLER 4 · PROCESS 6 · UNKNOWN 0   (21 commits)
USER share 52%   verdict: HEALTHY
```

Pass 5 36% → pass 6 45% → pass 7 **52%**. The rise is real this time and not a granularity
artifact: ledger appends were already batched before this window opened, so the denominator did
not change shape. What changed is **what the window contained** — five rulings, two refusals, a
non-author review, and a stranger test, all of which produce documents an outsider can act on.

## The window's shape

**Seven of the eleven USER items are rulings or refusals, not features.** `vbh.4` refused live
action; `ubs` was refused as a gate; `m7r` ruled no real-danger corpus exists; the `vbh` program
closed with six shipped and one honestly blocked. A lane whose product is *"a defensible ruling
on which ideas deserve deeply-planned projects"* should look like this, and for the first time
tonight it does.

## What went wrong, and all of it was mine

**Three conductor defects in one window, each caught by someone or something else:**

1. **`docs/RULES.md` header said "Eight rules" over nine.** I introduced it merging rule 7 and
   adding rule 9 — and my commit message that turn read *"Still nine rules, no deletion, 85
   lines."* I verified the count and never read the sentence above it. Found by a stranger test
   I dispatched.
2. **`STATUS.tsv` was missing four verdicts, the second time tonight.** The tick rule is
   same-turn updates. Backfilled; passed first try only because the earlier rejections had taught
   me the three rules (no numerals in reasons, compute the digest, never cite the live ledger).
3. **My basename-collision estimate was wrong by an order of magnitude** — I wrote "a couple",
   the count is 11, and for those the rule degenerates into the proxy it replaces. Found by the
   non-author review I dispatched.

**And two narrow-selector misreads while auditing others' work**: grepping one caveat phrasing
and briefly doubting a correct report; earlier, running the wrong path and reading `rc=0` through
`tail`. Twenty-second instance of the same defect this session.

**The pattern worth naming:** every one of my three defects was found by a check I asked for.
That is the system working, but it also means **my self-verification is the weakest instrument in
the lane** — I verify what I measured and skip what I wrote around it.

## What improved

- **A named subset overturned an aggregate three times out of three**, always optimistically.
  That is now a rule on the public page.
- **Refusals got stronger.** `vbh.4` refused against a +15 aggregate that cleared the bar its own
  dispatch set. `br` refused to close the epic and I did not `--force` it.
- **Workers disclosed their own gaps unprompted** — "the shipped rule is untouched", "local
  sessions present", "toy mechanics". Each disclosure saved a verification round and two of them
  changed my ruling.

## Actions

1. **Read the prose around a number I change, not just the number.** Both the RULES header and
   the STATUS backfill were adjacent-text failures.
2. Keep dispatching adversarial review of my own artifacts — it is 3-for-3 on finding real
   defects.
3. Twenty-two selector instances: the only thing that has ever caught them mechanically is a
   zero-hit guard. Consider one for `grep`-based audits in the lane's own scripts.

## NO-CLAIM

One reader, classifying from commit subjects and memory of the window. I count public rulings as
USER when an outsider could act on them; scoring those as PROCESS would put this window near 25%.
Passes 5–7 share a judge and no anchored rubric, so the trend is directional, not metric.
