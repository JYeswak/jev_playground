# MU-H1 falsification design — cheapest observation that could sink demand

Status: falsification design, not a kill and not an executed experiment.
Candidate: MU-H1 TODO-judge, non-author demand score 820, author score 900.
Purpose: move a possible rung-4 operational failure into a rung-2-cost measurement before
implementing a broad scanner.

## Chosen falsifier

**Base-rate falsifier:** sample 200 TODO-like markers from real, unrelated repositories and have a
human label whether each marker is still actionable (`active`, `fulfilled`, `obsolete`, or
`contradicted`). If actionable markers are below 5% and the confidence interval's upper bound stays
below 10%, the candidate's central truth-judgment value is likely too rare to change maintenance
behavior; MU-H1 should not advance as a general product without a different high-value action.

This tests the strongest failure mode directly: real TODO markers may be overwhelmingly still true,
so a truth judge finds almost nothing stale and its output is a rounding error. It is the same
operational lesson as Demo-1's 0.047% lift: a real signal can be reproducible and still too small to
justify a new lane, cost, or review workflow.

The result is not a taste kill. The threshold is predeclared, the population is external to this
lane, the label rule is explicit, and the experiment returns HELD/UNASKABLE if the sampling or labels
are not trustworthy.

## Exact one-hour command

The proposed minimal harness command is:

```sh
todo-judge prevalence \
  --repo-manifest fixtures/muh1-real-repos.json \
  --sample 200 \
  --stratify repo \
  --exclude generated,vendor,node_modules \
  --human-labels runs/muh1-prevalence-labels.csv \
  --out runs/muh1-prevalence.json
```

The command is a design target, not a claimed existing binary. Its required behavior is part of this
falsification contract:

1. Read a committed manifest of at least 10 real repositories, each pinned to a Git revision and
   containing enough TODO/FIXME/HACK/BUG markers for proportional sampling.
2. Deterministically enumerate marker records with file, byte range, raw text, symbol, repository
   revision, and marker hash. Do not let a model choose the sample.
3. Select 200 records with a fixed seed, stratified by repository so one large codebase cannot
   dominate the result. Exclude generated/vendor/build trees using manifest rules recorded in the
   receipt.
4. Emit a review CSV with the raw marker and bounded code context. A human labels each record using
   only the fixed rubric below; no Jev call is made.
5. Compute actionable prevalence, per-repository rates, label disagreement/unknown counts, and a
   Wilson 95% interval. Write the input manifest hash, repository SHAs, seed, excluded paths, labels,
   denominators, and all failures to the receipt.

A reviewer can produce the first answer in roughly an hour: 200 short marker decisions, with a
second pass over disagreements and ambiguous cases. The experiment is deliberately cheaper than
writing the scanner, integrating an agent hook, or tuning a model.

## Fixed human-label rubric

Each marker receives exactly one primary label:

- **ACTIVE:** the marker's stated work/condition remains unresolved and a maintainer could still
  act on it.
- **FULFILLED:** the requested work appears complete in current code, tests, or configuration.
- **OBSOLETE:** the condition or workaround no longer applies, even if the requested action is not
  literally represented by one new line.
- **CONTRADICTED:** the current code or configuration conflicts with the marker's stated condition.
- **AMBIGUOUS:** the marker lacks enough context to distinguish the other labels.

For the primary falsifier:

```text
actionable = FULFILLED + OBSOLETE + CONTRADICTED
unknown = AMBIGUOUS
```

`ACTIVE` is not a success for a truth judge; it is the denominator's non-actionable majority. An
ambiguous marker is not silently counted as active or stale. The reviewer may attach a one-line
reason and evidence range, but may not ask the proposed model what the label should be.

The receipt must keep a per-repository breakdown. A global 4% driven by one repository with 40%
actionable markers is not the same demand signal as 4% uniformly across 10 repositories.

## Failure criterion

The predeclared failure rule is:

```text
actionable_rate < 0.05
AND Wilson95_upper(actionable_rate, N=200) < 0.10
AND AMBIGUOUS < 0.20
```

In plain terms: fewer than 10 of 200 sampled markers are actionable, the uncertainty interval still
keeps the plausible rate below 10%, and labels are sufficiently obtainable. This is the single
observation that sinks the broad “truth judge over hundreds of markers” demand claim. At that base
rate, a 200-marker run usually yields fewer than ten candidates for human follow-up; age/history
reports or ordinary maintenance review may be enough, and repeated Noul cost is unlikely to change
behavior for most repositories.

A failure does **not** mean no repository could benefit. It means the general product claim is too
weak for promotion. A narrower candidate could survive by targeting old/workaround markers,
security-sensitive code, a specific language, or repos with a demonstrated high stale rate—but that
would require a new demand score and a new sampling frame, not a silent exception.

## Non-failure outcomes

The experiment must not force a kill when evidence is unavailable:

- `AMBIGUOUS >= 20%` → **UNASKABLE/HELD**; improve the label rubric or gather context.
- Fewer than 10 pinned repositories or fewer than 200 eligible markers → **HELD**; the sample is
  not representative enough.
- Repository provenance cannot be re-derived → **HELD**; do not label a moving tree.
- Actionable rate ≥5% but most labels are concentrated in one repository → **HELD** for a stratified
  follow-up, not immediate promotion.
- Actionable rate ≥5% with clear per-repo spread → falsifier did not fire; proceed to a small Jev
  fixture and measure whether the judge ranks high-value cases correctly.

The only `RULED_OUT`-compatible result from this design is the predeclared low-base-rate condition
with usable labels. Everything else is missing evidence.

## Why this is cheaper than building MU-H1

The proposed truth judge would need a scanner, evidence envelope, model adapter, calibration set,
receipt, threshold policy, and an operator workflow. None of those is required to answer whether
there are enough actionable stale markers to warrant the product. Deterministic enumeration plus
human labels tests the demand base rate directly and avoids contaminating the result with the
candidate's own confidence scores.

It also avoids the circular failure mode “the model found ten stale TODOs, therefore stale TODOs are
valuable.” Human labels establish prevalence first. Only if the base rate clears the gate should a
Jev arm be added to test ranking/calibration.

## Secondary falsifiers considered

### Calibration cannot be labelled

If human reviewers cannot agree on the truth label after bounded context, or if the ambiguity rate
exceeds 20%, the candidate cannot honestly claim calibrated stale/active probabilities. That returns
**UNASKABLE/HELD**, not RULED_OUT, because the missing evidence may be fixable with better context or
a narrower TODO class.

### The receipt is the product nobody reads

After the base-rate sample, ask the same reviewers to identify which of the labelled markers they
would act on and what action they would take. If a high-confidence report does not change ordering,
review time, deletion decisions, or issue promotion, the measured signal may be operationally
inert. This is a follow-up falsifier; it is not cheaper or more decisive than the base-rate test, so
it is not the primary unit here.

### Fixed rubric makes ordinary chat good enough

A pinned chat/structured-output control with the same deterministic evidence envelope can be added
only after the base rate clears. If its calibration and ranking match Jev within the predeclared
operational margin at lower cost, MU-H1's Jev-specific story fails while the broader TODO judge may
survive as a non-Jev tool. This is a later baseline question, not a reason to skip the prevalence
measurement.

## Receipt schema

The falsification receipt should be append-only and contain:

```json
{
  "schema": "jev.muh1.falsify.v1",
  "manifest_sha256": "...",
  "repository_count": 10,
  "repository_shas": [],
  "sample_size": 200,
  "seed": 20260918,
  "eligible_markers": 0,
  "labels": {
    "active": 0,
    "fulfilled": 0,
    "obsolete": 0,
    "contradicted": 0,
    "ambiguous": 0
  },
  "actionable_rate": 0.0,
  "wilson95": {"lower": 0.0, "upper": 0.0},
  "failure_rule": "actionable_rate < 0.05 && wilson95.upper < 0.10 && ambiguous < 0.20",
  "verdict": "UNMEASURED",
  "failures": []
}
```

The zero values and `UNMEASURED` above are schema placeholders, not results. A receipt with an
empty eligible-marker denominator is an ERROR, never a low-base-rate pass. The final command must
write observed marker rows or a content-addressed label file so a reviewer can reproduce every
count.

## NO-CLAIM

No real repository sample, human labels, prevalence, confidence interval, or falsification result
was collected in this unit. The command and thresholds are a proposed cheap experiment. A low-base-
rate result would falsify the broad demand claim, not prove that no narrow TODO-truth workflow can
be useful. Until the experiment runs, MU-H1 remains rung-2 cleared and unmeasured at rung 4.
