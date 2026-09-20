# SKILL — `jev-retransmit-killer`: do not adopt compaction here, and here is the number that settles it

**When to use.** When tempted to adopt `fast-jev-compaction`, a retransmit heuristic, or any
drop-context Score; when a compaction threshold looks "obvious"; when a vendor page or a plan
quotes token savings.

**The one-line answer.** On this repo's real sessions an **omniscient** judge saves **20.8–31.0%**
of tool-result bytes against a preregistered **50%** bar. The ceiling is below the bar, so no
policy clears it, and the model's keep-probability is irrelevant to the decision.

## Rule 1 — a savings number without a paired retention number is not a result

"We dropped 60% of the transcript" is indistinguishable from deleting it, which drops 100%. The
only admissible form is **savings AND retention on the same cases**:

> save ≥ 50% of tool-result bytes **AND** lose ≤ 10% of substantive reuse
> — preregistered at `work/compaction-proof/fair-oracle.mjs:22`, before any run

This is the rule that makes the section safe, because compaction is the first lever tonight whose
default number flatters us. Every honesty instrument in this repo exists because a flattering
number went unchallenged for a while.

## Rule 2 — beat the CEILING, not the model

The useful arm is `perfect`: an omniscient judge that drops exactly the results never substantively
reused. Nothing real can beat it. If it fails the bar, the argument is finished without a single
API call — and it is finished for *every* policy, not just the one under review.

**Fresh beat, 2026-09-20, 12 largest real omp sessions, no Jev call, no API key:**

| session (KB) | scored results | reuse events | `perfect` saved | reuse lost | verdict |
|---|---|---|---|---|---|
| 338,427 | 11,307 | 7,617 | 30.5% | 0% | REJECT |
| 322,477 | 11,151 | 7,838 | 21.4% | 0% | REJECT |
| 298,719 | 14,309 | 10,398 | 29.3% | 0% | REJECT |
| 289,000 | 10,151 | 6,534 | 30.1% | 0% | REJECT |
| 284,740 | 11,824 | 8,553 | 27.2% | 0% | REJECT |
| 253,476 | 11,463 | 8,125 | 22.6% | 0% | REJECT |
| 234,414 | 9,986 | 6,860 | 23.9% | 0% | REJECT |
| 213,071 | 12,137 | 8,213 | 24.4% | 0% | REJECT |
| 191,849 | 7,134 | 4,756 | 31.0% | 0% | REJECT |
| 183,475 | 10,972 | 7,481 | 26.9% | 0% | REJECT |
| 181,005 | 8,342 | 5,823 | 20.8% | 0% | REJECT |
| 167,405 | 10,798 | 7,137 | 22.6% | 0% | REJECT |

**12 of 12 usable, `perfect` ADOPTED on 0.** `drop-largest` saved 71–88% but lost 28–36% of
substantive reuse — three times the loss bar — so the savings were real and the retention was not.
That pair is exactly why Rule 1 exists: read alone, the 88% looks like the best result on the page.

Command: `node work/jev-retransmit-killer/ceiling-beat.mjs 12`

## Rule 3 — the keep-probability does not rank future need, and re-measuring it is a waste

Already measured twice, on two SDKs and two state shapes:

| session | keep_p needed | keep_p unneeded | AUC |
|---|---|---|---|
| A | 0.346 | 0.334 | 0.522 |
| B | 0.342 | 0.371 | **0.348** |
| C | 0.338 | 0.307 | 0.648 |

Straddling chance, and B is *below* it. The finding is not "the threshold is mistuned" — **no
threshold can work, because the probability does not rank future need.** Re-deriving this
distribution with fresh calls is the re-measure-instead-of-pin habit this repo paid for four times
in one session.

## Rule 4 — read the margin before the headline

The generalisable finding from the question family killed in section 14c was that the
near-threshold count matters more than prevalence: there, 197 of 400 rows sat within ±0.10 of the
fire line, so half the verdicts were made by the threshold rather than the model.

The analogue here is the **margin to the bar**, and it is stated rather than assumed: `perfect`'s
best session is **31.0% against a 50% bar — a 19-point shortfall**, and its worst is 20.8%. This is
not a near-threshold result that a better policy might tip. **No Jev call was made in this section,
so there is no score distribution and no near-threshold count to report; the margin is the honest
translation of that column, and it is named as a translation.**

## Rule 5 — the gate, not the essay

`node work/jev-retransmit-killer/adopt-gate.mjs` exits non-zero if production compaction is
installed (1) or if the evidence behind this doctrine has drifted (2). It checks that both receipts
still carry their findings, that the preregistered bars are unchanged — moving the bar is the
cheapest way to turn REJECT into ADOPT — and that no compaction hook is installed under `~/.omp`.

Five planted-bad trees in `adopt-gate.test.mjs` prove it fires: moved bar, gutted receipt, missing
receipt, installed hook, and one clean tree. A gate nobody has seen fail is a decoration.

**How to defeat this gate honestly:** run `ceiling-beat.mjs` on fresh sessions and clear the
preregistered bar. That is the intended path, and it is the only one.

## NO-CLAIM

- **One corpus.** 12 sessions from `~/.omp/profiles`, this machine, largest-first — chosen because
  a ceiling argument is strongest where there is most to save, which also means these are not a
  random sample of sessions.
- **The reuse oracle is a proxy, and a lax one.** "Needed later" = novel tokens reappearing later.
  It is self-tested with two planted negatives (noise results → 0/200 needed; end-of-transcript
  results → 0/200) but it is still a proxy for what an agent actually required.
- **This says nothing about compaction in general** — only that on this corpus, against these
  preregistered bars, the ceiling is below the bar. A different workload with bulkier
  never-reused results could clear it, and the gate exists to let that case prove itself.
- **`drop-largest`'s 28–36% loss is measured against the same proxy**, so it inherits the same
  caveat.
- No token-savings figure in this document appears without its paired retention figure.
