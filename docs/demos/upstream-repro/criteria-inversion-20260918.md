# Criteria inversion in zero-label spam questions

## Finding

Adding criteria to a zero-label spam question is not monotonically helpful. On the
upstream `jev-spam-eval` runs, more elaborate criteria sometimes reduced accuracy,
while a different simplification sometimes improved it. This is not a claim that
plain questions always win. It is a claim that prompt elaboration is an empirical
variable, not a free accuracy multiplier.

## Three paired comparisons

All comparisons use the same messages and paired predictions within each dataset.
The deltas below are variant minus baseline.

| Dataset and pair | n | baseline | variant | delta | paired significance |
|---|---:|---:|---:|---:|---|
| Ling-Spam: plain → structured criteria | 2,876 | 98.57% | 97.01% | **−1.56 pp** | exact McNemar p = 1.36×10⁻⁹; significant |
| Modern mail: category → urgency/authority | 633 | 97.00% | 96.68% | **−0.32 pp** | exact McNemar p = 0.50; directional only |
| Modern mail: category → names-only | 633 | 97.00% | 98.58% | **+1.58 pp** | exact McNemar p = 0.00635; significant |

The Ling-Spam significance test was aligned to the tool's own 2,876 exact-duplicate-
filtered rows, not the raw 2,893-line saved result file. The modern comparisons use
the 633 rows in `ood_modern.jsonl`.

Recent phishing provides the surrounding context: category classified 91.3% of the
853 messages as phishing, urgency/authority 91.0%, and names-only 93.6%. Those are
variant rates, not a separate paired binary test in this receipt.

## Mechanism hypothesis

The likely mechanism is criterion-induced boundary movement. The extra wording tells
the model which cues to privilege and how to resolve ambiguous legitimate bulk mail,
urgency, authority, or solicitation. That can reduce one error class while creating
another. The result is prompt-sensitive decision behavior, not a simple “more
instructions gives a better classifier” curve.

Names-only improving over category on modern mail is consistent with removing harmful
criteria, while urgency/authority losing slightly is consistent with adding a brittle
semantic boundary. This remains a mechanism hypothesis, not a causal proof.

## Does the upstream README already know this?

Yes, partly. It says the 98.3% detailed-criteria result was written **after reading
mistakes in 1,000 sampled emails**, and it explicitly notes that the detailed wording
did worse than the plain question on Ling-Spam. Therefore the Ling inversion is not a
new discovery about the repository; it is an independent reproduction and a stronger
cross-domain confirmation of a caveat the README already records.

The modern result adds useful evidence: the same non-monotonic behavior appears on a
newly fetched 2026 corpus, with one elaboration losing and a names-only simplification
winning. That makes the README caveat operational rather than anecdotal, but it does
not turn it into a universal law.

## Falsifier

Pre-register the plain, detailed, urgency/authority, and names-only prompts before
looking at labels or error cases; run them on a fresh held-out mail source with paired
predictions; then apply paired significance tests. The inversion hypothesis is
falsified if the detailed/structured variants consistently match or exceed the plain
baseline across fresh sources, with no significant degradations and no reproducible
variant-order effect.

## Reproduction sources

- `jev-spam-eval/ood_test.py`
- `jev-spam-eval/results/results_lingspam_criteria_all.jsonl`
- `jev-spam-eval/results/ood_modern.jsonl`
- `docs/demos/upstream-repro/jev-spam-eval-ood-20260918.json`

The experiment used the upstream saved answers and a fresh 633-request modern run;
it did not spend additional calls for the Ling-Spam paired significance calculation.
