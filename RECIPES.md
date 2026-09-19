# Six recipes that won today

Joshua, 2026-09-18: *"how has the team done so much today and not found a single winning recipe -
that seems like you all dont know what you're doing"*.

He is right that nothing was promoted, and wrong that nothing won. **Six things won, measured, and
none of them reached a verdict** — because the gauntlet in `docs/demos/STATUS.tsv` adjudicates ideas
*this lane proposes*, and every result below came from running somebody else's code. The evidence
never entered the machinery that would have ruled on it. That is a defect in the process, not an
absence of findings.

Each recipe below states what to do, the number that supports it, where that number came from, and
**when it stops being true**. Nothing here is a lane opinion; every figure is reproducible from a
receipt in [`docs/demos/upstream-repro/`](docs/demos/upstream-repro/README.md).

---

## 1. Ask a plain question instead of training a classifier, when your data will drift

**Do this:** for a classification job where tomorrow's inputs will not look like today's labels, ask
Jev in plain English rather than training on the labels you have.

| | zero-label question | TF-IDF trained on labels |
|---|---|---|
| in-distribution (Ling-Spam) | 98.57% | 99.41% (2,300 labels) |
| recent phishing | **91.3%** | 70.3% |
| modern legitimate-vs-not | **97.00%** | 72.51% |

**In-distribution the trained model wins.** Out of distribution it collapses by twenty-plus points
while the question holds. The recipe is not *"questions beat classifiers"*; it is **the labelled
model is better until your inputs move, and it has no warning that they have.**

**Stops being true when:** your inputs are stable and you have labels for them. Then train, and beat
the question by a point.
Source: [lingspam](docs/demos/upstream-repro/lingspam-20260918.md) ·
[ood](docs/demos/upstream-repro/jev-spam-eval-ood-20260918.json)

## 2. Use the short question. Elaborating it makes it worse

**Do this:** write the plainest question that states the task, then stop. Do not add criteria,
rationale, or worked definitions.

| comparison | plain / short | elaborated | p |
|---|---|---|---|
| Ling-Spam | **98.57%** | 97.01% | 1.4e-9 |
| modern mail, names-only vs category | **98.58%** | 97.00% | 0.0064 |
| modern mail, category vs urgency-authority | 97.00% | 96.68% | 0.50 (directional only) |

Two of three are significant, the third is directional. **The shortest question tested won
outright.** Upstream's own README concedes the same effect from the other side: its headline came
from a question *"written after reading the mistakes in 1,000 sampled emails."*

**Stops being true when:** the short question is ambiguous about the task itself, which is recipe 3.
Source: [criteria-inversion](docs/demos/upstream-repro/criteria-inversion-20260918.md)

## 3. Tell it what the system is for. Do not tell it what the answer is

**Do this:** put the deployment's purpose in the request. Keep the expected conclusion out of it.

| prompt-injection detection | bare | + context |
|---|---|---|
| recall | 74.9% | **95.1%** |
| accuracy | 89.7% | **96.5%** |

Twenty points of recall for one sentence about what the assistant does. The same sensitivity, pointed
the other way, produced this lane's only public retraction: a criterion worded *"reduce turns, since
each re-sends the whole context"* moved a verdict from 0.21 to 0.59.

**Context that states the task is state. Context that states the answer is leakage.**

**Stops being true when:** the "purpose" you add encodes the outcome. Test by running with the
framing stripped as a control.
Source: [sec-bench](docs/demos/upstream-repro/jev-sec-bench-20260918.md) ·
[framing leak](docs/demos/jev-probe/NOTE-framing-leak.md)

## 4. Average the question with the classifier rather than choosing

**Do this:** where you already have a trained model, average its score with a zero-label judgment
instead of picking a winner.

| | accuracy | false negatives | false positives |
|---|---|---|---|
| bare question alone | 98.57% | 2 | 39 |
| structured-criteria question alone | 97.01% | 8 | 78 |
| logreg alone (2,300 labels) | 98.57% | 40 | 1 |
| **averaged** (either question) | **99.83%** | **4** | **1** |

*Corrected 2026-09-19.* This table previously showed one "question alone" row at 98.57% beside an
average computed from the **other** question variant — the bare question's numbers next to the
structured-criteria average. Recomputed from upstream's committed out-of-fold scores: both
averages land on identical 99.83% / FN 4 / FP 1, so the headline survives, but the comparison as
written was between two different systems.

**And the predicate is now measured, which upstream never did.** The recipe's falsifier is "stops
being true when the two are correlated"; the phi coefficient between the scorers' error vectors is
**+0.013** (criteria) and **+0.035** (bare) — essentially zero. They fail on different emails, and
that is *why* the average pays. Reproduce with `python3 ensemble/run_lingspam.py` (no API key, no
training).

**Updated 2026-09-19 — the falsifier was tested and the rule survived it.** Three pairs from
upstream's committed scores, `python3 ensemble/run_all.py`:

| pair | phi | gain |
|---|---|---|
| bare question + logreg (Ling-Spam) | +0.035 | **+1.25 pp** |
| Jev choice + TF-IDF (phish, n=5,733) | +0.107 | **+0.38 pp** |
| logreg + naive Bayes, **same features** (Ling-Spam) | **+0.526** | **-0.14 pp** |

The correlated pair **loses accuracy when averaged** — two genuinely different algorithms, both
good, sharing a feature space, exactly the case the recipe predicts must fail.

**CORRECTED the same night, 2026-09-19 — low phi is NECESSARY BUT NOT SUFFICIENT.** A fourth pair
(`jev-sec-bench` injection with/without context, n=662, bootstrap B=2000) has phi **0.343**, CI
`[0.213, 0.469]` **entirely below the 0.5 line** — and it still did not pay: gain **-0.006**, CI
`[-0.0196, +0.0060]`. The rule as written above predicted a gain and there was none.

| pair | phi | accuracy gap | gain |
|---|---|---|---|
| bare question + logreg | +0.035 | **0.0 pp** | **+1.25 pp** |
| Jev + TF-IDF (phish) | +0.107 | 4.2 pp | **+0.38 pp** |
| with-context + no-context (sec-bench) | +0.343 | **6.8 pp** | **-0.60 pp** |
| logreg + naive Bayes | **+0.526** | 0.8 pp | **-0.14 pp** |

Two terms, not one. Averaging pays when the errors are decorrelated **and the scorers are close in
accuracy**; averaging a 96.5% scorer with an 89.7% one loses, because no amount of decorrelation
at 9% disagreement overcomes 6.8 points of gap. **Practical form: measure phi AND the accuracy
gap. Average only when phi is near zero and the gap is small — otherwise take the better scorer.**
Where the boundary in each term lies is unmeasured; four points do not locate a surface.

Source: [`phi-second-pair-20260919.md`](docs/demos/phi-second-pair-20260919.md), reproduced
independently by the conductor to the digit including the interval.

Identical headline accuracy, **opposite failure shapes** — the question protects recall, the
classifier protects precision — so the average is better than either at both.

**Stops being true when:** the two are correlated. This pair was not, which is exactly why the
average paid.
Source: [lingspam](docs/demos/upstream-repro/lingspam-20260918.md)

## 5. Pair your runs before you blame your sample size

**Do this:** when two variants score the same, compare them case by case before concluding
"underpowered".

An independent benchmark reported its two model versions *"not separable at this sample size"*
(n=60). Pairing the committed per-case results: **zero discordant pairs, identical choices on
60/60.** No increase in n on that task set can separate them, because no case discriminates them.
The limit was the task set, not the count.

**Stops being true when:** you have discordant pairs. Then n genuinely is the constraint.
Source: [pairing](docs/demos/upstream-repro/jev-benchmark-pairing-20260918.md)

---

## 6. Keep an open-model control arm, because it is free

**Do this:** before concluding that a typed-judgment result is about *the model*, re-ask the same
question of an open implementation. `simple-jev` serves the identical `choice`/`score`/`noul`
interface with no key and no login.

Asked the hardest classification this lane made all day — is a cited figure a stored literal, a
derived rollup, or absent — an open 35B classifier returned **`derived_rollup` at confidence 0.989**
with stored-literal at 0.0067, in **1.7 seconds** for 1,040 input tokens. That matches the verdict a
non-author pane reached after two of my own mechanisms were wrong.

**Stops being true when:** you need calibrated probabilities. Upstream states plainly that these
distributions are *"not calibrated probabilities of correctness"*, so this is a second opinion, not
an oracle.
Source: [simple-jev](docs/demos/upstream-repro/simple-jev-20260918.md)

---

## What this file does not claim

- **These are other people's measurements**, reproduced or re-analysed here. Recipes 1, 2 and 4 come
  from one email corpus family; recipe 3 from one security benchmark; recipe 5 from one n=60 set.
- **None has been promoted through this repo's gauntlet**, which requires held-out n, stated
  uncertainty and leakage controls that these runs mostly do not carry. They are recipes with
  evidence, not adjudicated verdicts, and `docs/demos/STATUS.tsv` still reads **0 promoted**.
- **Recipes 1 and 2 may be the same finding** seen twice: both say the elaborate thing loses to the
  simple thing. They are listed separately because the interventions differ, not because they are
  known to be independent.
- Live figures were single runs. Nothing here is a reliability measurement.
