# Classify confirmation: unseen HWU64 intent set

Status: PREREGISTERED BEFORE LIVE CALLS
Bead: jev-gdhb
Date: 2026-09-27
Jev launch: after prereg approval.
Free-comparator launch: not before `2026-10-01T00:00:00Z`; free-tier allocations through 2026-09-30 are reserved by existing beads.
reach-mode: mcnemar

## Corpus and freshness

- Dataset: `FastFit/hwu_64`, pinned revision `9fb5bff1e37c4c5a6d46c1ff6f286b6d3f362222`.
- Source: public `data/test-00000-of-00001.parquet`, SHA-256 `29d218e4e54b790c59e868e48bd729857682da86dad2dee234bcd107f7e96221`, 27,207 bytes.
- Workspace freshness check before this preregistration: `work/choice-clinc150/` contains committed CLINC150 rows (`full.jsonl`, `rows-full-jev.jsonl`, and comparator rows), so CLINC150 is not unseen and is excluded. `work/` contains no HWU64 rows or source mention before this preregistration. FEVER/Climate-FEVER rows are also already present in `work/jev-oioo/` and are excluded.
- Exact corpus: `work/jev-gdhb/corpus.jsonl`, 784 rows, all 64 intent labels retained, corpus SHA-256 `d35b793a7a908d45f0b7c088fb3357557020945dcbbc52b23909b95c7047be98`.
- Selection: first up to 13 source-order test rows per intent label, preserving source text and label; no row or label was authored or rewritten. The resulting class counts are recorded in `work/jev-gdhb/CORPUS.json`.
- State source: `work/jev-gdhb/states.jsonl`, each state is `{ "text": row.text }`; state SHA-256 `29de5c4c596c53c4c0a9526675ac175189af2b1b67a5a3281de1287d0c68bed8`.

## Frozen classify design

- Jev model: exactly `jev-1.13.0`.
- Question: one `Choice` over the full 64-label set, using the dataset's exact intent names as labels. The state is only the utterance text; the gold label is never sent.
- Comparator: `dots-studio/dots-3-note-preview:free` through the pinned system-one-adapter path, same state and label set. No paid comparator, Anthropic, or xAI arm.
- Each row stores raw choice, probabilities, confidence, model, usage, latency, and validation status. Missing, malformed, or refused answers are invalid; no coercion or imputation.
- Every request must pass keyless state-size preflight. The compact classify request uses a 500-byte question allowance; all 784 states must be `FITS`.

## Preregistered metrics and numeric bar

Primary: paired exact McNemar on accuracy for Jev versus the free comparator, with both arms valid on the same row IDs. Report each arm accuracy, Wilson 95% interval, `b` (Jev-only correct), `c` (free-only correct), and exact two-sided p.

The frozen outcome rule follows the measured Banking77 classify bar:

1. An arm with more than 5% invalid, missing, malformed, or unparsed rows makes the run `NOT_SCORED` as a harness/arm failure. Accuracy below 50% is not itself a harness failure and remains part of the Jev-versus-free comparison.
2. Jev must beat the fixed majority-label constant on the corpus.
3. If `b > c` and exact McNemar `p < 0.05`, report `WIN`.
4. Otherwise, if Jev accuracy is no more than 3 percentage points below the free comparator **by point estimate**, report `NON_INFERIOR`; no interval is used for this margin.
5. Otherwise report `LOSE`.
6. `PASS` means `WIN` or `NON_INFERIOR` plus both refusal rates `<=5%`. Non-inferiority is not superiority; a non-significant difference alone is not a win.

No threshold, label list, corpus selection, or outcome rule changes after answers.

## Size, reach, spend, and date gates

- Planned N: 784 rows, below the free-tier daily capacity; no split or adaptive stopping.
- Planning reference: the earlier Banking77 classify bar used the same McNemar/3-point non-inferiority shape; this confirmation uses a fresh 64-intent set and keyless sizing for every request.
- Reach receipt: `work/jev-gdhb/reachability.json`, bound to this preregistration, corpus, and state hashes before calls.
- Jev may launch after pane-1 prereg approval. The comparator runner must refuse before `2026-10-02T00:00:00Z`, make no free-arm request before then, and stop on 401/402/403/429 with `NOT_RUN` rather than classifying remaining rows as model errors.
- Jev spend: record input/output tokens and compute input spend at `$0.042/M` input tokens, output free. Comparator OpenRouter usage and spend are recorded; expected comparator charge is `$0` for the `:free` model.

## Boundary

This preregistration measures one public HWU64 test subset, one 64-label Choice wording, one Jev version, and one free comparator. It makes no claim about CLINC150, FEVER, other languages, or general intent classification before live calls. Raw utterances remain in the committed public corpus only because they are the measured input; no API key or response is committed in this preparation pass.
