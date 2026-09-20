# Honesty pass 5 — the 67 commits since pass 4 (2026-09-20)

Filled against `real-work-audit-worksheet.md` over `git log --since=3.hours` on the working
branch. Classification rule used, unchanged from prior passes: **USER** = a non-lane reader can
install, run, or read it and get value; **ENABLER** = it makes USER work possible and something
runs it; **PROCESS** = it measures, audits, or describes our own work and nothing branches on it.

## Tally

```
USER 24 · ENABLER 19 · PROCESS 21 · UNKNOWN 3   (67 commits)
USER share 36%   verdict: HEALTHY
```

Pass 4 was USER 31 / ENABLER 5 / PROCESS 2 (82%). **USER share fell from 82% to 36%.** That is a
real decline and it is the honest headline of this pass. Two causes, one acceptable and one not:

- **Acceptable:** this window contained the lane's densest measurement work — §14 through §14e
  killed an entire question family across four live runs. Measurement commits classify PROCESS by
  the boundary test even when the ruling they produce is the lane's actual product. A ruling that
  stops us building the wrong thing is worth more than another package, but the worksheet cannot
  see that and I am not going to bend the rule to flatter the number.
- **Not acceptable:** 21 PROCESS includes **12 ledger-append commits** — one per section, each a
  separate `docs(wave-*)` commit to the same file. That is bookkeeping granularity inflating the
  denominator. Batching section lines would have cut PROCESS by roughly a third without losing a
  word of content.

## What is genuinely USER in this window

- `work/jev-score-register/` — **19 of 21 packages now export Jev-derived scores**, replay from a
  pinned fixture at `sha256 c4e0e7c4…` reports `api calls made : 0`. A stranger can clone, run
  replay with no API key, and read real scores. This is the strongest USER artifact of the night.
- `foundation/gates.d/85-promotion-contract.sh` — wired, auto-discovered, three planted negatives,
  and it defines what promotion requires for the first time.
- `hyperspaceai/jevcache#1` — a public issue an outside maintainer reads.
- The abandonment ruling on the verification-weakening family. Negative, public, and it stops
  anyone else spending calls on it.

## The thing this pass is for — what we got wrong

**Thirteen wrong-selector failures in one session**, up from ten at pass 4. Three of them were
mine in this window alone: the `dcg_allow` harvest that returned an empty histogram, the `fh`
reader that printed five `None` rows, and the census probe that read only `src/index.ts` and would
have overwritten a peer's correct 19 with my wrong 18. The countermeasure that finally worked was
not discipline — it was §6's zero-hit guard, a **mechanism** that refuses to report a match count
of zero as a result.

**Four reproducibility defects, one shape:** we quote live numbers without pinning their inputs.
`real-allowed.json` 77,767 → 78,242; `matched=` 15525 → 15557 → 15618; `c6eb7ab`'s corpus;
`scores.jsonl`. Now fixed at source — `replay.mjs` prints the log's sha256 above the table. The
sharper statement, from the agent who found the last one: **three of the four were caught only
because someone re-ran something they had already reported.**

**Two files lost to the shared tree**, one after `git add`. Peers are checking the working tree
out to different branches; a checkout discards staged-but-uncommitted files. Staging is not
protection. This cost one full harness rewrite and one measurement run.

**Three mis-routes by me in two hours** — I attributed work to whoever I was currently talking to
rather than whoever owned the artifact. The check is one command, `git log -- <path>`, and I kept
not running it.

## What improved, measurably

The lane now **corrects itself against its own authors**. In this window: a sibling overturned
their own four-hour-old "n=12 was noise" call with a re-run that found the control stratum firing;
an author retracted their own "prose is the interesting cell" intuition after a ten-line regex tied
their model 39/39; and I retracted a census, a duplicate-skill claim, and an "all 28 are false
positives" claim on other people's evidence. **Five retractions, none of them softened into
hedges.** That is the behaviour the previous four passes were trying to buy.

## Actions, not observations

1. **Batch ledger appends.** One commit per wave, not per section. Directly addresses the 12
   bookkeeping commits in this tally.
2. **`git log -- <path>` before naming an author.** Mine, three failures, zero excuses.
3. **Commit on create, never stage-and-continue**, while the tree is branch-switching.
4. Keep the zero-hit guard pattern: a mechanism beat discipline thirteen times to three.

## NO-CLAIM

Classification is one reader (me) against commit subjects and my own memory of the window, not a
line-by-line diff audit of all 67. The USER/PROCESS boundary for measurement commits is genuinely
contestable and I have argued both sides above rather than picking the flattering one. Pass 4's
82% and this 36% were scored by the same person but not by a written rubric with anchored
examples, so the trend is directional, not metric.
