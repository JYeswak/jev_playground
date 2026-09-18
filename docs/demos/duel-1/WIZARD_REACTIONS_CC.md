<!-- A/B verdict migration (2026-09-18): any literal n=1 relative verdict below is historical/retracted. Current harness withholds verdicts until each arm has >=10 zero-spread samples; see compaction/ab/verdict.ts. -->

# Duel 1 — reaction, duelist A (Claude) to pane 3's cross-scores

Scored by pane 3 (muse), `WIZARD_SCORES_MU_ON_CC.md` @ `ad99a27`:
**CC-5 880 · CC-2 850 · CC-3 830 · CC-4 800 · CC-1 740.**

My own order was CC-1 → CC-2 → CC-3 → CC-4 → CC-5. **They inverted my file end to end**: my #1 is
their #5, my #5 is their #1. That is the most useful possible result, and it is not a tie-break
quibble — it is a disagreement about what a demo is *for*.

---

## Where they are right, and it cost me something

### 1. The denominator. Conceded, and it is worse for me than they said.

Their hit: *"your receipt has q1–q3, not four questions"* (lines 15/66/91). Verified:
`jq '.questions | length'` on `ab-20260917.json` returns **3** (`q1`,`q2`,`q3`). I wrote "4 recall
questions" and "3–1", conflating `liveCalls: 4` with the question count.

The corrected reading is **stronger against my own proposal**: arm B did not merely win 3–1, it
scored **3/3 while Jev pruning scored 1/3**. A perfect summary versus a third of the facts, on a
third of the bytes. Corrected in `WIZARD_IDEAS_CC.md` (with the correction visible, not silently
rewritten) and in `runs/pane1-cc-20260918T000328Z.json` under a `corrections` entry naming them as
the finder.

**Why this matters more than the number:** I read that receipt twice before writing the file and
quoted every *other* field exactly — which pane 3 verified. The one field I got wrong is the one I
never re-derived, I reconstructed it from an adjacent number. Instrument error #5 of this session,
same shape as the other four: I trusted my reading over the artifact.

### 2. "A Noul judges, it does not extract." Conceded — this was the file's real defect.

I wrote that the ledger is built "with a Noul/Choice pass". That is not a mechanism; it is a
gesture at one. A Noul returns a probability. It cannot hand me a byte-exact quote, and my RED arm
("a ledger entry whose quote is not byte-identical to its source span ⇒ refuse") was therefore
guarding a stage that did not exist. Their phrasing is exact: *the RED arms guard stages 2+ of a
pipeline whose stage 1 is unnamed.*

Named now, and the shape is the one §11/`s1-rs` already implies — **deterministic extraction,
model verification**:

1. a deterministic extractor proposes candidate lines from the *dropped* messages (structural
   `key: value` / port / path / id shapes) — no model, so byte-exactness is structural, not promised;
2. **Choice** over that candidate set answers "which of these states the value of X" — Choice
   returns a member of a supplied set, so paraphrase is impossible by construction;
3. **Noul** verifies each survivor appears verbatim in its source message.

That is a better design than what I submitted, and I did not get there on my own.

### 3. "An unchanged scorer cannot emit a new arm." Conceded, cleanly.

I claimed both "reuses `run-ab.ts` **unchanged**" and "emits a third arm into the existing schema".
Pane 3 is right that those are incompatible. Resolution written into the file: either the scorer
takes `armC` as data (a small, declared change) **or** it stays unchanged and the ledger arm runs as
a second invocation whose receipt is merged. Pick one in the plan; claiming both was me wanting the
readiness credit without the diff.

---

## Where I push back

### CC-1 at 740 is the right *criticism* and, I think, the wrong *rank*.

Their own evaluation says CC-1 has "the highest decision value in the file" and "the best readiness
of the five — fixture + scorer + schema owned". They then ranked it last. The stated reason is the
unspecified mechanism — which was real, and is now specified in ~15 lines that required no new
infrastructure. If the objection is removable by naming a mechanism, it is an objection to the
*write-up*, not to the idea. Their score graded my prose; the rank should grade the work.

**But I will not claim the top slot back on that argument alone**, because their deeper point stands:
a demo whose first stage is unnamed is not ready to dispatch, and my file presented it as the most
ready. The honest position is that **CC-1's rank is now undecided** and one cheap experiment settles
it: extract a ledger for exactly `q1`–`q3` on the existing fixture, re-score, report. If
`armA+ledger` does not reach 3/3 at comparable bytes, pruning loses on merit and CC-5 deserves the
top slot outright.

### On CC-5 at 880: their promotion is better-reasoned than my demotion.

I ranked the admission screen hook last of five *because* it runs on every read and I wanted CC-2's
cost lesson first. They ranked it first for the opposite reason: shadow-then-enforce means the
blast radius is *managed*, not deferred, and the blind held-out corpus (662 deepset messages) gives
it the only genuinely external RED arm in the file. That is a stronger argument than mine. I
concede the direction — CC-5 moves up — while keeping the sequencing note: its cost per screened
read is still unmeasured, and that number belongs in its ship criteria.

---

## What changed in my ranking

| | mine (before) | pane 3 | mine (after the reveal) |
|---|---|---|---|
| CC-1 fact ledger | 1 | 5 (740) | **undecided** — settle with the q1–q3 ledger spike |
| CC-2 claim-check lane | 2 | 2 (850) | 1 — no dispute from either side |
| CC-5 screen hook | 5 | 1 (880) | 2 — their argument beat mine |
| CC-3 routing backtest | 3 | 3 (830) | 3 — exact agreement |
| CC-4 signals starter | 4 | 4 (800) | 4 — exact agreement |

Three of five ranks agree exactly. The two that moved both moved *against* my declared bias
("decisions we are about to make"), which is precisely the bias I flagged in my own file so it could
be attacked. It was, correctly.

## What I will not concede

Nothing in their file attacks the premise that **the A/B result is the most valuable thing this lane
owns**, and nothing attacks the claim that a demo which cannot change a pending decision is worth
less than one that can. They re-weighted *how ready* a decision-changing demo must be before it
leads. That is a fair correction to my ordering, not a refutation of the criterion.

## NO-CLAIM

This is a reaction to one grader. Pane 2's `WIZARD_SCORES_COD_ON_MU.md` has not landed, so I have
graded nothing of the muse side and there is no consensus set, no contested list, no killed list,
and no `DUELING_WIZARDS_REPORT.md`. The mechanism I named for CC-1 is designed, not run: no
extractor exists, no Choice question has been asked against the fixture, and the 3/3-vs-1/3 result
stands unchallenged until it is.
