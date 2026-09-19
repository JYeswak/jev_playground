# Honesty pass 2 — 2026-09-19, commits `61fb963..d1ec069` (42)

Boundary test, unchanged: **does running code branch on it, or can a non-lane reader consume it?**
USER = product a stranger can install/run/read, or a ruling that changes what we build.
ENABLER = infrastructure a shipped thing depends on. PROCESS = bookkeeping about our own work.

## Tally

| class | n | share |
|---|---|---|
| **USER** | **21** | 50% |
| ENABLER | 13 | 31% |
| PROCESS | 7 | 17% |
| UNKNOWN | 1 | 2% |

**Verdict: HEALTHY.** USER is a plurality and an outright majority of classified work, up from
29/16/9/3 (52%) at the last pass — held steady while the absolute count rose.

## What counted as USER (21)

The ships, the rulings that moved a build decision, and the retractions:

- `d1ec069` installer + README — **the single highest-value commit of the block.** Turned five
  receipts nobody outside the lane could use into an artifact a stranger installs and rolls back.
- `f7bcd9d` head-to-head RULE WINS · `268073e` second axis, baseline beats model on five surfaces
- `287f4b9` `658922f` `bb4fa4f` `6c9c8fc` the ship→co-presence→conformance→promotion chain
- `63f052c` `requireKey` — mechanical fix for a class that beat the written rule eight times
- `e27b536` R33 retraction · `702356c` R32 my void experiment · `d6b52ea` R31 refusal-with-trigger
- `b255b30` class-D NOT-ANSWERABLE · `f556b1f` proxy UNVALIDATABLE-by-generation
- `33aa633` corpus + 3.95% prevalence · `bf6b6dd` public prevalence chapter
- `6bb5e5a` README arc · `7b3ae92` honesty refresh · `c5966a5` `5be22f0` v3 scope freeze
- `fdd61ae` the autonomous-loop doctrine, which changed how every later tick behaved

## What counted as PROCESS (7)

`35633d6` (a NO-CLAIM about a README), `10abc7a` `ab38a5d` `a5c11fd` merges, `8eb34db` `9b9228a`
(class-D prep for a run later ruled void by construction), `e2c1bd0` — the 19% fire-rate receipt
that was superseded within two ticks.

**Note the shape of the PROCESS cluster:** five of seven are about work that was later voided,
retracted, or superseded. Process accumulates fastest around claims that were not yet true.

## The block's real finding, which no tally captures

**Eight wrong-selector failures in one session, one of them published** (`ccd63b5`, retracted by
`e27b536` within the hour). Every instance is the same: a lookup returned nothing and absence was
concluded. The written rule existed the whole time and prevented none of them.

The response was the right kind — `63f052c` made it mechanical rather than adding a ninth
doctrine line — but the honest scoring is that **this block contains a published false claim
against a correct artifact built by a pane that had done the right thing.** That is worse than any
PROCESS commit in the tally, and a class-based count cannot see it.

Second-order: two defects in my own installer (`d1ec069`) were found by *running* six arms, not by
reading — a backup a re-run could destroy, and a GREEN that copied nothing. Arms over review, again.

## Carried forward

1. `requireKey` is landed but **cannot force its own use**. The ninth instance will come from code
   that never imports it. The real test is whether a ninth published false-absence occurs.
2. Two instruments (`verify-other-reasons.sh`, `verify-reason-numerals.sh`) still gate nothing.
   Frozen, not retired — no new instrument without all four creation-gate answers.
3. `promoted 0` stays in the ledger. One integration is live on a working profile; that is a
   promotion of an artifact, not of a candidate, and conflating them would inflate the headline.
