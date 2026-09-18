# Held resolution — Demo-7 named user

Status: the specific “no named user voiced the pain” hold is **RESOLVED / RECOVERED**.
Candidate: Demo-7 signals starter, blind reconciled demand score **560**.
Evidence: Oscar Beijbom, Nyckel, “Calibrating LLM classification confidences,” August 2024.
Source: https://edge.nyckel.com/blog/calibrating-gpt-classifications/
Read state: this search occurred after the blind ranking; it does not rewrite the blind score.

## The held question

The §3d retry condition was narrow: name one practitioner who tried to use a model's verdict for
classification, found it inadequate, and said so publicly. Missing a voiced user was not evidence
that the problem did not exist; under §3c it was a **HELD** condition, not a kill.

## Named practitioner and direct fit

**Oscar Beijbom**, writing for Nyckel, evaluated GPT-4o on twelve real-world text-classification
datasets covering practical tasks such as spam filtering, moderation, sentiment, lead scoring, and
topic classification. His article is explicitly about calibrating LLM classification confidence,
not about an abstract language-model benchmark.

The public finding is the required pain statement in operational form:

- asking GPT to return a confidence score produced poorly calibrated probabilities;
- in several datasets, higher self-reported confidence was associated with being more likely to be
  wrong, while other datasets showed little relationship between confidence and correctness;
- raw GPT self/logprob confidence was materially worse than a supervised logistic-regression
  baseline on calibration error;
- post-hoc calibration on labelled data improved statistical calibration, but could collapse scores
toward an uninformative common value when the raw confidence had no predictive signal.

Source: [Oscar Beijbom, “Calibrating LLM classification confidences”](https://edge.nyckel.com/blog/calibrating-gpt-classifications/).
The article's comparison is the exact failure mode Demo-7 addresses: a model's verdict or claimed
confidence is not a reliable classification signal until a measured signal layer and calibration
procedure establish what the number means.

This is a named practitioner with a concrete attempted workflow and a public negative result. It is
stronger than a generic “LLMs can hallucinate” article because the post evaluates a classifier over
real task datasets, compares raw model confidence to a supervised baseline, and reports calibration
failure modes that a downloader can measure.

## Four-bar fit

### 1. Installable by a stranger

This citation does not prove Demo-7's installer, fixture, or command. It resolves only the held user
question. The existing demand artifact describes an offline template with a synthetic fixture;
that implementation claim remains a rung-3 proof obligation and is not upgraded by this article.

A stranger-facing Demo-7 must still run from a clean clone without a provider key, fit the declared
signal baseline, and emit the confidence/reliability report from a pinned generator and distribution.
The source's twelve real-world datasets are evidence that a practical user can supply task data;
they are not permission to substitute an unpinned corpus into the demo.

### 2. Benefit to AI usage as a whole

The benefit is broader than Jev: a team using an LLM for spam, moderation, sentiment, lead
scoring, topic assignment, routing, or triage should not mistake a prompt-returned confidence for a
calibrated probability. The named source demonstrates that this failure can reverse the intended
ranking—high confidence can correlate with wrong decisions—so a signal/calibration layer can change
whether a system abstains, escalates, or acts.

This does not claim that every classifier should become a Jev signal model or that a supervised
classifier always wins. Beijbom's post shows a reason to measure calibration and compare baselines;
Demo-7's whole-AI benefit is the reusable measurement procedure, not the lane's particular headline
number.

### 3. Who downloads it and why

The named downloader is an ML practitioner or product engineer who has deployed, or is preparing
to deploy, an LLM classifier and needs to know whether its confidence can safely drive routing,
moderation, lead handling, or human review. Oscar Beijbom is the named practitioner who publicly
demonstrates that the default model verdict is inadequate as a calibrated signal and that the issue
requires labelled calibration evidence.

The source does not prove a purchase decision, download count, or willingness to adopt this specific
CLI. It proves the previously missing external user pain. That is exactly what the hold asked for,
not a substitute for two non-author demand scores or a clean-clone demonstration.

### 4. Measurable improvement

The source supplies the correct before/after shape:

- **Before:** raw GPT self-reported or logprob confidence, calibration error, reliability curve,
  Brier/log loss, and selective accuracy.
- **After:** a calibrated signal layer evaluated on a separate holdout, with ECE/Brier/log loss,
  reliability bins, selective accuracy/coverage, abstention behavior, and calibration drift.
- **Command:** the Demo-7 fit/report command over a pinned task generator/distribution, with an
  injected negative control for shuffled labels, empty corpus, and out-of-distribution inputs.

The source's reported raw-versus-calibrated comparison makes the benefit measurable, but its exact
aggregate figures are not copied as Demo-7 acceptance thresholds. Demo-7 must pin its own corpus,
record denominator counts, and report refusal/unknown states instead of promising that every task
will reproduce the Nyckel numbers.

## What this resolves—and what it does not

### Resolved

The claim “nobody has named a user who voiced this pain” is no longer true. Oscar Beijbom's named,
public, task-grounded evaluation is one credible citation. It directly says that raw LLM
classification confidence is unreliable and that calibration plus a conventional baseline is
needed.

### Still open

This evidence does not establish:

1. Demo-7's exact 62.6% → 95.1% result; that source remains a local/unvendored claim until its
   generator and distribution are pinned.
2. That Demo-7's zero-label setup works without labels. Beijbom's calibration findings use labelled
   task data; the demo must state what is learned without labels and where calibration labels enter.
3. That Demo-7's offline installer works. Clean-clone proof remains rung 3.
4. That Demo-7 clears the §3c ≥700 score gate from two non-author graders. The blind scores and
   reconciled 560 are retained to prevent post-read anchoring.
5. That a signal model improves a real operator's behavior. Rung 4 still needs before/after lift and
   an absolute threshold, not merely a statistically significant calibration number.

## Adjudication

**Verdict: RECOVERED from the §3d named-user HELD condition; not ruled out.** The retry condition
fired with a named practitioner and a direct public source. The blind score remains **560**; I do
not silently replace it with a new score after reading the evidence. A future two-non-author
re-score may decide whether the citation lifts demand above the §3c threshold.

This is intentionally not “PROMOTED” and not “rung 1 fully cleared.” The correct epistemic result
is:

```text
named-user hold: resolved
blind demand score: 560, unchanged
remaining gate: independent non-author demand re-score plus later thin proof
```

The citation recovers the candidate from the anti-premature-kill hold. It does not make the
capability, install, calibration, or measured-lift claims true by association.

## Retry condition if later rejected

If a later non-author re-score still leaves Demo-7 below the demand gate, the rejection must name the
specific remaining reason—such as no differentiated buyer after calibration tools are considered,
no reproducible corpus, or no operational lift. It must not revert to “nobody voiced the pain.” If
future evidence shows Beijbom's task is not classification practice or the linked article is removed
and cannot be independently recovered, search for another named practitioner before declaring the
pain UNASKABLE. Absence of a second citation is not evidence that the problem is unreal.

## Source and uncertainty ledger

| Claim | Evidence | Status |
|---|---|---|
| Oscar Beijbom authored a public Nyckel article on LLM classification confidence | Nyckel article URL above | Observed source metadata |
| The work evaluated GPT classification over practical real-world datasets | Article description and experiment sections | Observed from source; no local reproduction |
| Raw GPT confidence can be poorly calibrated or inversely related to correctness | Article's reported findings | Observed source claim; not independently rerun |
| Calibration and supervised comparison are useful | Article's comparison | Observed source claim; not a Demo-7 threshold |
| Demo-7's exact installer, 62.6 → 95.1 result, or demand score changes | No external source in this resolution | Unproven / unchanged |

A second, independent public source points in the same direction—Shimon Rosenberg's “Why we don't
trust LLMs to classify the call they're about to make” at
https://reshimu.ai/blog/why-we-dont-trust-llms-to-classify—but it is not needed to satisfy the
one-citation retry condition and is not used to inflate the score.

## NO-CLAIM

This resolution did not install Demo-7, call a model, reproduce Nyckel's datasets, verify the
reported calibration percentages, or interview Oscar Beijbom. It resolves only the named-user
condition with one public practitioner source, preserves the blind 560 score, and leaves non-author
re-scoring, clean-clone proof, and measured lift open.
