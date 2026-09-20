# jev-retransmit-killer — the falsifier, on record BEFORE any measurement

Committed before a single number in this section was produced, the same way `beb45d5` did it for
the consequence rewrite. If the falsifier fires, the doctrine in `SKILL.md` is wrong and this
section retracts rather than rationalises.

## Why a compaction section needs one more than the others

Every other unit tonight measured an honesty instrument, where the default outcome is unflattering.
This one measures a **cost lever**, where the default number flatters us: "we dropped 60% of the
transcript" reads like a win with no work. Every honesty instrument in this repo exists because a
flattering number went unchallenged for a while.

So the rule for this section, stated before the run:

> **A token-savings number may not be reported without a paired retention number on the same
> cases.** "We dropped X%" is not a result. "We dropped X% and the downstream reuse lost was Y%"
> is. Without the second clause a compaction Score is indistinguishable from deleting the
> transcript, which saves 100%.

## The claim under test

**CLAIM.** On this repo's real agent sessions, compaction cannot be adopted, because the
**ceiling** is below the adopt bar — not because Jev's keep-probability is mistuned.

The bar is preregistered in `work/compaction-proof/fair-oracle.mjs:22` and predates this section:

```
SAVE_BAR = 0.50, LOSS_BAR = 0.10
adopt if savings >= 50% of tool-result bytes AND substantive reuse lost <= 10%
```

## THE FALSIFIER

The decisive arm is `perfect`: an **omniscient** judge that drops exactly those tool results that
are never substantively reused later. No real policy can beat it, because it already knows the
future. So:

> **If `perfect` returns ADOPT on a fresh real session, the claim is FALSE** — a ceiling above the
> bar means some real policy might reach it, the question becomes "which policy", and this section
> must reopen instead of closing.
>
> **If `perfect` returns REJECT**, no policy can clear the bar on that session, and the argument
> needs no model call at all to make.

Two secondary falsifiers, both of which would also break the claim:

1. **If `drop-largest` (a dumb deterministic policy) clears the bar** where Jev did not, the
   finding is "Jev is the wrong judge", not "compaction cannot be adopted".
2. **If the sessions measured are not representative** — fewer than 40 scored tool results, or
   zero substantive reuse events — the run says nothing and must report INSUFFICIENT rather than a
   verdict. A confident verdict on a thin session is the `NaN%` failure in another costume.

## What this section is NOT allowed to do

- Re-derive the keep-probability distribution with fresh Jev calls. It is already measured twice,
  on two SDKs and two state shapes: `keep_p` 0.346/0.334, 0.342/0.371, 0.338/0.307 for
  needed/unneeded, AUC **0.522 / 0.348 / 0.648** — straddling chance. Re-running it to see it again
  is the re-measure-instead-of-pin habit this repo has already paid for four times tonight.
- Build a sibling oracle. `work/compaction-proof/` already holds `oracle.mjs` (strict),
  `oracle-selftest.mjs` (two planted negatives) and `fair-oracle.mjs` (preregistered bars). Section
  5's lesson was that we own things we do not reference.
- Report a savings figure alone, under any framing.
