# Demo-7 contract — signals-not-verdicts classifier starter

Status: **contract only; not implemented**
Plan source: `docs/demos/PLAN.md` §5.7
Owner: pane 2 / WindyJaguar owns `demos/signals-starter/**` when emitted.
Rank: mean 712.5 from four graders; lowest of the converged demos.
Verification posture: offline synthetic fixture first; no live Jev call is authorized here.

## Goal and ownership

Build a reusable starter that asks several constrained signal questions, fits a tiny local
classifier on user labels, reports calibration, and compares the fitted head against both a fixed
rule floor and a verdict-only baseline. The product is a falsifiable answer to “does this
classification surface improve when Jev supplies signals instead of one verdict?” It is a template,
not an opaque hosted model and not a promise that Jev's raw verdict is accurate.

The owned boundary is `demos/signals-starter/**`: schema declaration, question manifest, offline
fixture, fit/report/refuse CLI, calibration metrics, and receipts. It must not modify the Jev
provider, add an online training loop, install a new daemon, or turn a calibration score into an
automatic production action. The first implementation may target CSV/JSONL labels, but the input
schema must be explicit and versioned.

This contract does not authorize applying the template to the local resume-quality A/B. That corpus
is one transcript and a handful of questions, and arm B is stochastic. The local application is
blocked until its property gate is satisfied, not merely until a count reaches N.

Non-goals:

- no live Jev calls in the first offline bead;
- no verdict field that claims a classifier is good without a baseline and calibration report;
- no fitting on unlabeled data, no post-hoc segment fishing, and no train/test contamination;
- no use of a synthetic result as evidence about a user corpus;
- no automatic merge, close, block, or customer-facing decision from the starter;
- no copy of the upstream benchmark's numbers into a local receipt as if rederived;
- no second general-purpose ML framework when a deterministic tiny head suffices.

## Product context and guardrails

> **Product scope.** The jev lane evaluates community repositories built on **Jev** (TypeSafe's
> System One judgment model) and converts proven capabilities into individually installable,
> tested demos wired into the omp harness. Jev is the only judgment engine; it returns typed
> verdicts with probabilities, and it **judges — it does not extract, generate, or summarize.**
>
> **Effects are bounded.** Claims about Jev come from live calls; the receipt states the calls made and what they cost.
> The API key lives only in the environment as `TYPESAFE_API_KEY` and its value is never recorded
> in any artifact — names are expected, values are not.
>
> **Evidence rules.** A claim with no re-derivation path is not evidence. An empty scan set is an
> **ERROR**, never a pass. A one-item scan set is not a demonstration. A timeout is not a verdict.
> Exit code must agree with verdict text. These are implementation requirements, **not statements
> that any code or gate has passed.**
>
> **Shared worktree.** Three agents share this checkout and all commit as the same git identity,
> so `%an` cannot attribute a commit. Stage explicit paths, own files only, never `git add -A`,
> never amend, never rewrite shared history. Preserve peer changes: if a file you need belongs to
> another lane, message its owner with the exact replacement text rather than editing it.
>
> **Blocker protocol.** If a prerequisite is unavailable, report the exact blocker with the command
> and its verbatim output. Never substitute a stub for evidence, never weaken an adversarial
> assertion, and never let a missing capability be reported as a passing check.

These are implementation requirements, not statements that any code or behavioral gate has passed.

## Embedded contract

The following defines the template's data contract, staged mechanism, thresholds, and refusal
semantics. An implementer should be able to build and test it without opening PLAN.md.

### 1. Input schema and labels

The input is JSONL or CSV with one row per item. Required fields:

```json
{
  "id": "case-001",
  "text": "the item presented to the classifier",
  "label": "positive",
  "signals": {"signal_a": true, "signal_b": false},
  "split": "train"
}
```

The schema validator must require `id`, `text`, `label`, and declared signal fields. Labels are
binary for the first implementation and must be present before fitting. `split` is assigned by a
committed deterministic seed or is read from a frozen fixture; rows cannot move between train and
held-out sets after the report begins. Duplicate ids are an error. Empty text is allowed only when
the declared signal set can stand without it, and that exception must be explicit in the receipt.

The signal manifest declares 3–7 signal questions. A signal is a constrained fact or judgment
about the item, never the final class label. The manifest records each question id, wording, type,
criteria, and expected answer domain. It also records whether the signal is supplied in the input
fixture or obtained by a later live Jev adapter. The offline starter uses recorded signals only.

### 2. Stage-by-stage mechanism

Stage 0 — validate the corpus and manifest. Check schema, duplicate ids, labels, split integrity,
minimum rows, and that every signal is in the declared domain. Refuse before fitting on any error.

Stage 1 — build the signal matrix. Convert each signal to a deterministic numeric feature using
the manifest's declared encoding. Do not extract prose with a model during fit. Missing signal
values are explicit missingness, not false; the first implementation refuses a missing required
signal rather than silently imputing it.

Stage 2 — fit a tiny local head. Logistic regression is the initial head, with a fixed random seed,
fixed regularization, and the declared train split. The implementation records coefficients and
fit configuration, but the receipt is the evidence artifact rather than a claim that coefficients
are universally valid.

Stage 3 — evaluate three named baselines on the held-out split:

1. the fitted signal head;
2. the best fixed rule declared in the manifest, which is the net-floor control;
3. the verdict-only baseline, if recorded verdicts exist.

The verdict-only baseline is not the oracle. It is a comparison arm that must be allowed to lose,
tie, or win. If the signal model does not beat the committed synthetic fixture's declared
verdict-only baseline by the pre-registered criterion, the template refuses to publish a winning
claim.

Stage 4 — calibrate. Emit accuracy, AUROC when both classes are present, ECE, Brier score when
probabilities are available, reliability bins, and flip rates between repeated passes. Every metric
names its denominator and split. A missing metric is `UNAVAILABLE`, never zero.

Stage 5 — policy output. The CLI emits `REPORT`, `REFUSE`, or `ERROR` as a process state, not a
classifier verdict string. `REFUSE` means the evidence did not satisfy the pre-registered gate;
it does not mean the item is negative.

### 3. Measured prior art and the delta claim

Usage Map §9 records `jev-phishing-bench@1d56e8c`: verdict-only accuracy 62.6% versus a signal
question head at 95.1%, with five signals, AUROC 0.988, and ECE 0.027. The fixed strong rule is
reported at 89.5%. The delta between 95.1 and 62.6 is **32.5 percentage points**. Do not round
that to a vague “33 points” claim without naming both endpoints and the denominator.

Those are source claims, not local measurements. The local synthetic fixture must carry its own
sha and report its own metrics. The README and EVAL row must distinguish the upstream benchmark
from the fixture reproduction. If the reproduction does not match its committed report within
tolerance, the template refuses rather than silently refreshing the golden result.

### 4. The gate is a property, not N≥50 alone

The original local proposal said to apply the starter after A/B receipts accumulate past N≥50.
R11 invalidated that count-only gate: arm B scored 3, 1, 3 on a byte-identical fixture because
`runOmp` has no pinned temperature. Fifty samples of that arm would fit noise and call it
calibration.

The replacement gate is:

```text
READY_FOR_LOCAL_RESUME_FIT iff
  (N >= 50 AND generator_is_pinned)
  OR published_distribution_exists
```

`generator_is_pinned` requires fixed model, fixed temperature, and fixed seed when the provider
exposes one. A published distribution must include N per arm, spread, generator/model identity,
and the full receipt set. A raw receipt count with no distribution is insufficient. The gate must
emit `CALIBRATION_BLOCKED_UNPINNED_GENERATOR` rather than fit.

This property is a hard boundary for the local A/B. The synthetic fixture can prove the template
mechanism at N below 50; it cannot authorize fitting on the resume-quality corpus.

### 5. Four ship artifacts

Install script: `bash demos/signals-starter/install.sh` from a clean clone. It must install no
runtime service, use the canonical `uv` path, run the offline suite, and print the exact command:

```sh
uv run python -m signals_starter.cli fit \
  --manifest demos/signals-starter/fixtures/signals.json \
  --data demos/signals-starter/fixtures/synthetic.jsonl \
  --out demos/signals-starter/runs/signals.json
```

Tests: injected, deterministic, and no network. The suite must include the refusal arms below,
fixture golden comparison, split/hash validation, calibration denominator checks, and the property
gate for unpinned generator distributions.

Receipt: `demos/signals-starter/runs/signals-<ISO>.json`. Required fields: schema, input and
manifest SHA-256, row counts, label counts, split counts, signal ids, fit seed, head/fit version,
baseline metrics, fitted metrics, calibration bins, flip rates, generator pin state, `failures`,
and policy state. It must not contain secret values or a verdict field that collapses the report
into one word.

EVAL row: verification level `[test]` for synthetic offline reproduction; cite the exact receipt,
prior art and license, and state that no user corpus or live model behavior was evaluated. A later
live signal run gets a new receipt and a new EVAL row; it never mutates the synthetic evidence.

## Focused verification

The stranger runs `bash demos/signals-starter/install.sh`. The satisfying synthetic fixture must
reproduce the committed report within tolerance. The command exits 0 only for a report that names
all denominators and has `failures: []`; a refusal is a nonzero, named outcome.

RED arm 1 — shuffled labels. Permute labels with a committed seed while leaving features intact.
The fitted signal head must return `no signal found`, nonzero exit, and no fitted-model artifact.
The output must name the seed, row count, and refusal code. A model object written anyway is RED.

RED arm 2 — empty corpus. An empty JSONL must return `EMPTY_CORPUS` nonzero. It must not emit
accuracy 0, AUROC 0, ECE 0, or a green empty receipt.

RED arm 3 — insufficient labels. Fewer than the declared minimum labelled rows must return
`INSUFFICIENT_LABELS`, nonzero, without a confident report. The threshold and row denominator must
appear in stderr and the receipt failure.

RED arm 4 — verdict-only baseline wins. Modify the committed synthetic fixture or baseline answer
so the signal head does not beat the verdict-only baseline. The template must return
`THESIS_NOT_REPRODUCED` and refuse to publish a winner. It must not lower the threshold after
observing the result.

RED arm 5 — miscalibrated probabilities. Feed a deliberately inverted probability column. ECE or
the declared calibration bound must fail and the process must refuse. A missing calibration metric
is not a pass.

RED arm 6 — unpinned local A/B generator. Supply N≥50-looking rows with no fixed model/temperature
metadata or distribution. Return `CALIBRATION_BLOCKED_UNPINNED_GENERATOR`; never fit the resume
head merely because N is large.

Denominator in every run: rows read, rows accepted, label counts, train/held-out counts, missing
signals, discarded duplicates, class counts in each split, and each metric's denominator. A one-row
corpus and a one-class held-out split must be visibly non-demonstrative.

Who verifies: the implementer runs offline tests; two non-author graders score the contract before
this demo is built. No author of the original signal proposal may be the sole grader of its own
scaffold.

## Evidence and logging

Receipt schema: `jev.signals-starter.receipt.v1`. Never retro-edit a receipt. A changed fixture,
manifest, model, or fit seed creates a new receipt. The receipt records `failures` as an array even
on success, where it is `[]`.

Do not record `TYPESAFE_API_KEY`, source secrets, operator home paths, or raw private corpus text.
Synthetic examples are committed only when they are intentionally public and license-safe. Live
signal calls, if separately approved, use `TYPESAFE_API_KEY` from the environment and record model,
request count, and budget, not the value.

Verification level: `[test]` for the synthetic offline artifact. A live calibration claim requires
at least an `oracle` or `live` subject only after the property gate, distribution, and external
review are present. The receipt must not contain a `verdict` field over a stochastic arm.

EVAL Boundary: the starter proves a tiny signal head can be fit, compared with fixed/verdict-only
baselines, and calibrated on the named synthetic fixture. It does not prove upstream benchmark
numbers locally, model quality on a user corpus, stable arm-B behavior, causal classification
accuracy, or safe automatic action.

## Open risks with concrete resolution

Risk: a synthetic fixture is too easy. Resolution: require a held-out split, record feature/class
counts, and add a shifted fixture before any local claim. A fixture whose result changes under a
seed must refuse until the seed is fixed and the spread is published.

Risk: a fixed-rule floor is selected after seeing test results. Resolution: commit the rule and
threshold in the manifest before fitting; include its hash in the receipt; make changing it create
a new fixture identity.

Risk: AUROC is reported with one class. Resolution: emit `UNAVAILABLE_ONE_CLASS` and keep the
other metrics' denominators explicit; never print 0.0.

Risk: the head looks calibrated only because it copied the verdict. Resolution: RED arm with
shuffled labels and a feature-ablation report. The head must refuse if no signal survives.

Risk: the N≥50 property is interpreted as permission to use unstable generators. Resolution: make
`generator_is_pinned` a required serialized field, and require a published distribution alternative.
A count alone is never a pass.

Risk: template expands into online training. Resolution: refuse unknown modes and accept only
`fit`, `report`, and `refuse` offline commands until a new contract is approved.

**Contract status:** implementation not started. Numbers above are source measurements or explicit
requirements; none assert that this demo has passed.
