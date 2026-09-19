# The ruling: every candidate that looked good on authored data failed on real data

**Date:** 2026-09-19 · **Level:** `[live]` · Derived from the committed receipts below, not recalled.

This lane exists to produce a defensible ruling on which ideas deserve deeply-planned projects.
After a day of measurement across nine candidates, the ruling is not about any one of them.

## The pattern

| candidate | on authored / synthetic data | on real data | receipt |
|---|---|---|---|
| tool-call gate (bicameral) | 0/20 false positives | **3/20 FP**, AUC 0.865 | `bicameral-gate-adoption` |
| worker supervision (foreman) | AUC **1.000** | **0.750** on 186k real windows | `foreman-supervision-adoption` |
| code-review ordering (jev-review) | **12/12** pair orderings | AUC **0.625** on 22 real diffs | `jev-review-real-diffs` |
| context compaction | — | Jev ≈ drop-everything; keeping all is **7× better** | `compaction-retention-oracle` |
| tier routing for cost | vendor: **−59.9%** | **+90.2%** vs flat mid-tier on our 643 sessions | `router-savings-inverts` |
| router tier signal | — | AUC 0.56–0.63, loses to **prompt length** | `router-tier-signal` |
| skill selection (skillranker) | their synthetic 12: **0.800** | *not yet run on real data* | `skillranker-corpus-measured` |

**Three candidates were measured both ways. All three fell.** Not one authored result survived
contact with real data, and the drops are large: −0.250 AUC, −0.375 AUC, and a precision collapse
from perfect to 15% false positives.

**Nothing has cleared a preregistered bar on real data.** One promotion was awarded and
**retracted by its own author** within two hours when the real-data number arrived.

## Why authored corpora inflate — the mechanism, not the moral

An authored case embeds the author's own phrasing of the distinction being tested. The model is
then asked to recover a distinction that was written *to be recoverable*. Real data does not
cooperate: the signal is entangled with noise the author would never think to include.

The sharpest instance: the gate's v2 questions were written **after reading its v1 misses**, so a
perfect 1.000 on that corpus measured the author's phrasing. Held-out data returned it to 0.865
with 3/20 false positives on ordinary daily commands.

## The second finding, which outranks every AUC here

**Prevalence decides deployability, and none of the vendor claims mention it.** Pane 3 mined
186,449 real windows and found **30 stuck ones — a 0.016% base rate** — then computed what the
measured separator does at that prevalence: at 80% recall, roughly **24 true catches against
~55,791 false alarms, about 1:2300**. Suppressing false alarms to parity requires a threshold
that also zeroes recall.

So the useful instruction is not "improve the threshold." It is **change the base rate** — trigger
only in already-suspicious contexts — or find a far stronger separator. An AUC without a
prevalence figure cannot tell you whether a detector is deployable, and every number in this
ecosystem is published without one.

## What this does NOT say

Jev is strong where it has been measured honestly: it ties a TF-IDF classifier trained on ~14,800
in-domain labels at **zero labels** (McNemar p=0.677) and holds 0.97–0.99 under distribution shift
where that classifier collapses to 0.70; prompt-injection detection with deployment context is
**96.5%** at AUC 0.993; and on skillranker's own corpus it scores **5× better than that repo's own
always-abstain control**, missing their 0.90 gate by a single case. Both of its failures there are
*cheap* ones — it declined rather than misled.

**The gap is not capability. It is that the decisions people are wiring Jev into are being
validated on data the wirer wrote.**

## Ruling for anyone reading this from outside the lane

1. **Decompose the decision into narrow typed questions**; never consume a monolithic verdict.
   Measured: a phishing verdict scores 63.8% while the *same call's* sub-question scores AUC 0.96.
2. **Keep a dumb baseline.** In this lane a two-line regex, a flat pricing tier, prompt length,
   and "keep everything" each beat the model at least once.
3. **Validate on data you did not author**, and state the **prevalence** beside every score.
4. **Pick thresholds from labels**, never at the shipped 0.5 — calibration is the recurring
   weakness (code-vulnerability ECE 0.19; the 0.5–0.6 band only 38% positive).

## NO-CLAIM

Nine candidates, one machine, one model version, one day; sample sizes from n=12 to n=96 per arm
with a measured re-run noise floor of ~0.006 AUC. Three of the real-data oracles use *proxies* for
ground truth — token reappearance, file-overlap-in-future-commits, and a predicate over tool-call
timing — and each proxy carries noise that biases against the model by an unmeasured amount.
"Failed on real data" here means *failed the bar we preregistered*, not *carries no signal*.

---

## SECOND AXIS, appended 2026-09-19 — a dumb baseline has now beaten the model on five surfaces

The ruling above is about *how* we measure. This is about *what we found*, and it is the stronger
claim because it is a clean sweep.

| surface | the dumb baseline | margin |
|---|---|---|
| phishing verdict | a two-line domain regex | **+27 points** (McNemar p=1.5e-8) |
| tier routing for cost | flat mid-tier pricing | Jev **+90.2% more expensive** on 643 real sessions |
| router tier signal | prompt **length** | length won 2 of 3 sessions |
| context compaction | **keep everything** | 7× fewer mistakes |
| tool-call harm detection | **four regexes** | rule **12/12** vs Jev 11/12, both FP 0/40 |

Five surfaces, five preregistered bars, five wins for the cheap thing. The last one is the
cleanest because all three arms ran on a held-out split neither scoring pane authored, with the
rule imported unmodified and shasum-verified (`toolcall-headtohead-20260919.md`).

**Jev was not bad on any of them.** 11/12 recall with zero false positives on 40 benign commands
is a strong result in isolation; 96.5% on prompt injection with context is excellent; it ties a
classifier trained on ~14,800 labels while using **zero**. The finding is narrower and more
useful: **it was never better than the cheap thing already available on that surface.**

### The rule this produces

**Where the harm is expressible, express it.** A judge earns its place only where a rule cannot
be written — and across five surfaces we did not find such a place. Before wiring a model into a
decision, write the regex first and make the model beat it. That test costs an hour and has now
changed the answer five times out of five.

### What would overturn this

A surface where the deterministic baseline is genuinely unwritable — open-ended semantic
judgement over text a rule cannot pattern-match, with ground truth we did not author. The spam
and injection benchmarks are the closest existing evidence *for* that case: there Jev matched a
trained classifier at zero labels and held under drift where the classifier collapsed. We have
not yet found such a surface **inside omp**, which is where the integration has to live.

## NO-CLAIM (second axis)

Five surfaces on one machine, one operator, one model version, in one day. Four of the five
baselines were chosen by us after seeing the model's failure mode, which biases toward the
baseline — the tool-call head-to-head is the exception, where the rule was frozen and
shasum-verified before the comparison. "Beaten" means *failed the preregistered bar against a
cheaper alternative*, not *carries no signal*.

---

## SHARPENING, appended 2026-09-19 — the compaction proxy is UNVALIDATABLE on this corpus, not merely unvalidated

Every compaction finding here rests on one proxy: *a tool result "was needed" if novel tokens it
introduced reappear later*. The ruling above carried that as a caveat. A zero-API ceiling sweep
now makes a stronger and less comfortable statement possible.

**The sweep** (`classd-ceiling-sweep-20260919.md`, `b255b30`): for each candidate scoring window,
what fraction of frozen turns does the **original agent's own continuation** reproduce the reused
fact? That is the ceiling — the best any ablation experiment could score.

| scoring window | ceiling (both fact definitions) |
|---|---|
| 1 → 80 messages | **≤ 0.083** |
| unbounded (rest of session) | 0.708 / 0.375 |

**Reuse in these transcripts is long-horizon — beyond 80 messages.** No generable window clears a
0.5 ceiling, so an ablate-and-re-run experiment cannot be scored on this corpus at any window we
could actually generate. Class D is **NOT ANSWERABLE this way here**, and no preregistration was
written because there was nothing to register against.

**What this changes, and what it does not.** It does not rescue compaction: the measured result
stands — Jev ≈ drop-everything, keep-everything 7× better, `keep_p` AUC 0.35–0.65 with a passing
positive control. What changes is the honesty of the caveat. We can no longer say "validating the
proxy is future work"; we must say **the proxy is unvalidatable on this corpus by generation**,
because the thing it proxies for happens too far in the future to regenerate.

**Trigger that reopens it:** a corpus with near-term reuse (facts reused within a generable
window), or a continuation method cheap enough to regenerate 80+ messages of context faithfully.
Absent either, class D stays closed here rather than deferred indefinitely.
