# Jev rule-class seat — low-noul veto only `[receipt]`

**Lane:** live, then offline analysis. **Model:** `jev-latest` → `jev-1.13.0`.
**Date:** 2026-09-20. **Noul question:** "this command shape is a DEFECT, not ordinary correct usage of the tool."
**Claim class:** statistical result on n=23 (semantic subset n=6). Not an invariant.

This receipt is the only claim that may be cited. It does not license a general meaning judge, a blocking gate, or an 18-vs-17 win.

---

## 1. The aggregate is retracted

hybrid @0.5 **18/23** vs numeric baseline **17/23** was quoted as a win. It is not.

McNemar on SHIP-vs-rest @0.5: **b=3, c=2, n_discordant=5, two-sided exact p=1.0** (Yates χ²=0). Five cells moved; net +1. That is noise, not a rounding detail. The 18-vs-17 headline is **RETRACTED**.

Discordant pairs: baseline right / hybrid wrong on `bash-structural-def-search` and `count-as-verdict`; hybrid right / baseline wrong on `digest-truncation`, `path-nonexistence`, `pipefail-anywhere`.

Evidence: `work/jev-triage/runs/mcnemar-loo-20260920.json`.

---

## 2. The real claim: semantic 3/6 vs 0/6, baseline structurally incapable

On the six classes whose numbers said SHIP and a human refused on **meaning**, Jev noul @0.5 is **3/6**. The numeric baseline is **0/6** because it **cannot answer the question**. It has no opinion on defect-vs-ordinary-usage. That incapability, not the 3/6 rate, is why a seat exists.

The three low-noul true negatives (Jev confidently "not a defect", gold agrees):

| class | noul |
|---|---:|
| digest-truncation | 0.09 |
| path-nonexistence | 0.24 |
| pipefail-anywhere | 0.23 |

---

## 3. n_semantic=6; one flip is a coin

Six rows. One relabel moves 3/6 → **2/6 or 4/6**. 2/6 is a coin. Do not cite 3/6 as a precision. Cite the structural gap (baseline cannot answer) and the three low-noul rows.

Most of NEGATIVE_EVIDENCE.md is not this shape. 54 R-headings are instrument/design/not-a-class (`work/jev-triage/r-classify.json`). R54 cass withdraw is semantic in the filing sense and **excluded** here (no hits/rate).

---

## 4. LOO-of-t lands on 0.25 every fold — and that is weaker than a held-out score

Resubstitution: pick t on all 23, **20/23** at t=0.25 (SHIP-vs-rest TP=6 FP=3 TN=14 FN=0).

Leave-one-out of the **threshold only**: for each row, pick t on the other 22 (max correct, then min FN, then min FP), score the held-out row. **Also 20/23.** Every fold selected t=0.25.

**NO-CLAIM:** LOO does not hold out the noul values. It only holds out the threshold pick. It is stability of t=0.25 on this sample, not an independent test of Jev. Weaker than a true held-out score. Both 20/23 numbers stay; they are labelled.

---

## 5. Confident-wrong rows (worse than uncertain)

A gate that is wrong while confident is worse than one that is uncertain.

| class | noul | gold | what happened @ t=0.25 |
|---|---:|---|---|
| pipefail-masked | **0.51** | not a defect (correct bash unless pipefail) | still SHIPS |
| R59-broad-backticks | **0.74** | not a defect (fence-extraction idiom) | still SHIPS |
| R56-bare-workaround | **0.89** | not a defect (meta-talk) | still SHIPS |

Catching all three requires t≈0.90, which blocks five gold-SHIP classes (FN=5). Not deployable.

SHIP-vs-rest FN=0 at t=0.25 means **no good class was blocked**. FP=3 means **three bad classes still ship**. Gate-to-stop-bad: veto TP=3 (the low-noul rows), veto FN=3 (these three), veto FP=0. Not "no bad class ships / three extra reviews."

---

## 6. Cost

**1 Noul per class that already passed hits≥50, rate≤5%, FP≤0.30-or-unlabelled, concentration<0.5.** Not per candidate ever mined. This set: 12/23 would be called cold; the last run spent 3.

---

## What may be claimed

**LOW-NOUL VETO.** When Jev is confidently low (noul 0.09 / 0.23 / 0.24 on this sample), it is worth logging as "would refuse: ordinary usage, not a defect."

**NOT a general meaning judge.** Confident-wrong at 0.74 and 0.89.

**NOT a blocking gate.** TTSR injects; this logger records. A block would ship the three high-noul misses into silence and the FN=5 threshold into the pack.

**NOT 18-vs-17.** Retracted, p=1.0.

---

## Dogfood (stage 4)

Stop re-scoring these 23 rows. The next mined class that clears the numeric bars runs:

```text
node --experimental-strip-types work/jev-triage/advisory-veto.mjs --file <class.json>
```

It **never blocks** (exit 0 even on would-veto, missing key, or transport failure). It appends one JSONL line to `work/jev-triage/advisory-veto.jsonl` (gitignored, machine state) recording `would_veto` at t=0.25. That is how n_semantic grows past 6 without us authoring the labels.

Wire: `askJev` in `work/jev-client/src/index.ts`. Key: `infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba --env=prod --silent --`.
