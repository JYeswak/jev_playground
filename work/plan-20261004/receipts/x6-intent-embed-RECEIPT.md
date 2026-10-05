# x6-intent-embed dogfood receipt

**Verdict: NOT-DECIDED.** The frozen embedding/head beats Jev and Kev-4B on the preregistered 600 rows, but loses to Clef-flash; the preregistered all-bars criterion is therefore not met. No product or DAG change recommended.

## Data, baselines, and fit

- `work/choice-banking77/full.jsonl`: 3,080 labeled Banking77 **test-split** rows. Held indices are the shared `random.Random(7)` 600-row sample; the other 2,480 test-split rows train the head. This is **not the official Banking77 train split**. Held-index SHA-256: `346213dd268223e993a1b89faadf71a0f5b84f4eed91fbfb3b5cb17a5cacc6d9` (`RESULT.json:30`; independently checked by `verify.py`).
- Majority constant: 14/600, 0.0233 (`RESULT.json:32-36`). Cheapest lexical baseline, frozen word unigram/bigram TF-IDF + LogisticRegression: 460/600, 0.7667 (`BASELINE.json:4-7`).
- Treatment: cached Qwen/Qwen3-Embedding-0.6B snapshot `97b0c614be4d77ee51c0cef4e5f07c00f9eb65b3`; normalized unprompted SentenceTransformer embeddings; LogisticRegression C=1, lbfgs, max_iter=1000. Model and 2,480/600 split recorded in `RESULT.json:27-42`; frozen treatment is specified in `PREREG.md:18-23`.

## Paired held-set results

- Embedding + head: 521/600 = **0.8683** (`RESULT.json:1-2,27`).
- Jev-1.13.0: 472/600 = 0.7867; embedding head is +49 correct, +8.17 percentage points. Exact two-sided McNemar: head-only correct 80, Jev-only correct 31, p = `3.6816e-6` (`RESULT.json:12-18`).
- Kev-4B: 486/600 = 0.8100; +35 correct, +5.83 points. McNemar discordances 75 vs 40, p = `0.001413` (`RESULT.json:19-24`).
- Clef-flash: 577/600 = 0.9617; -56 correct, -9.33 points. McNemar discordances 6 vs 62, p = `8.182e-13` (`RESULT.json:5-10`).
- Baseline sources: `work/local-decision-arms/rows-clefflash.jsonl`, `work/local-decision-arms/rows-kev4b.jsonl`, and `work/choice-banking77/rows-full-jev.jsonl`; the shared sampling and original bars are recorded in `work/local-decision-arms/BAR.md`. All 600 ID joins, truth labels, accuracy counts, and exact McNemar values independently reproduced by `verify.py`.

## Execution and scope

- Run: `nice -n 10 env HF_HOME=<specified cached HF store> HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 uv run --offline --no-project --python 3.12 --with torch --with transformers --with sentence-transformers --with scikit-learn python var/agent-tmp/dogfood/x6-intent-embed/run.py`.
- Device MPS; encoder + head elapsed 59.69 seconds (`RESULT.json:28-29`). Run used the already-cached model and offline package resolution. Jev/API calls: 0; spend: **$0** (`RESULT.json:3,40`).
- This is one fixed sample from the Banking77 test split, with training drawn from its remaining test-split examples. Do not claim official test performance, generalization, or production readiness.
- Artifacts: `PREREG.md`, `BASELINE.json`, `run.py`, `RESULT.json`, `predictions.jsonl`, `verify.py`, and `dag-input.jsonl`, all under this experiment directory.
