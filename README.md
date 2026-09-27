# Jev — typed decisions for code

Jev is TypeSafe's System One model for typed judgments. Give it a JSON state and a typed question; get a choice, score, or true/false value with probabilities and confidence. Jev does not generate prose. Your code owns the threshold, the safe side, and the action taken when an answer is malformed or uncertain.

This repository turns measured Jev behavior into small, runnable tools. The full measurement ledger lives in [`docs/LEDGER.md`](docs/LEDGER.md); source receipts and preregistrations are linked there instead of being copied into this page.

## Quickstart

From a fresh clone:

```bash
git clone https://github.com/JYeswak/jev_playground.git
npm ci --prefix kit
npx --prefix kit --no-install jev doctor --robot
# Expected without a key: NOT_RUN and exit 2.
npx --prefix kit --no-install jev ask choice --fake --state kit/examples/state.json --question kit/examples/question.json --robot
npx --prefix kit --no-install jev verify --claim "A low percentage of hematopoietic progenitor cells are susceptible to HIV-1 infection ex vivo." --evidence kit/examples/scifact-evidence.txt --fake --robot
npx --prefix kit --no-install jev score --text "it represents better-than-average movie-making that does n't demand a dumb , distracted audience ." --levels kit/examples/sst5-levels.json --fake --robot
npx --prefix kit --no-install jev classify --text "How do I locate my card?" --labels kit/examples/banking77-labels.json --fake --robot
npx --prefix kit --no-install jev gate --command "npm publish --access public" --fake --robot
```

### Install Jev into omp

From this checkout, install the project-scoped omp tools into a disposable git repo. The command is keyless and exits 0:

```bash
python3 -c 'from pathlib import Path; Path("var/agent-tmp/jev-omp-demo").mkdir(parents=True, exist_ok=True)' && git init -q var/agent-tmp/jev-omp-demo && npx --prefix kit --no-install jev omp install --dir var/agent-tmp/jev-omp-demo --robot
```

Expected JSON has `status: READY` and `repo` set to the disposable directory. The installer refuses to overwrite files it did not create; it records template hashes in `.omp/jev-kit-manifest.json`.

The install currently writes six callable tools, one post-hook, five omp extensions, and the shared kit helpers:

| Installed tool | Measured basis / receipt | Limit to keep in mind |
|---|---|---|
| `jev_rerank` | BEIR SciFact and FiQA receipts: `work/rerank-scifact/receipt-fiqa-mkex.json`, `work/rerank-scifact/receipt-nfcorpus-v2.json` | Candidate list must fit the tool's preflight; measured result is top-1 reranking, not arbitrary ranking tasks. |
| `jev_claim_check` | `docs/demos/upstream-repro/jev-claim-check-20260924.md` | Qualitative claims only; numeric claims are refused before Jev. Verdict cuts are supported >=0.8, unsupported <=0.2, unsure between. |
| `jev_classify` | Banking77 measurement: `docs/demos/upstream-repro/choice-banking77-20260924.md` | The 80.1% result is the measured Banking77 corpus, not a general classification guarantee. |
| `jev_gate` | Held-out gate receipt: `work/jev-1lim/final-receipt.json` | Reported rates are stratified sample rates; the receipt contains 47 harm rows, not fleet-wide prevalence. |
| `jev_flag` | Related web/tool screening receipts in `work/hermes-webscreen-repro/RECEIPT.md` | Installed for the flag seam; no standalone universal flagging accuracy claim is made here. |
| `jev_screen` | Web-screen receipts: `work/hermes-webscreen-repro/RECEIPT.md` | The cited measurements are bounded corpora and specific states; no general clean-output claim. |

The installed tools load through project scope, so they apply to the throwaway repo regardless of the omp profile. To run the same command in a real project, replace `var/agent-tmp/jev-omp-demo` with that repository path.

`jev omp install` is an installer, not a model call. The tools return keyless `NOT_RUN`/safe results when no TypeSafe key is available.

The example state and Choice question are captured from committed rows: `work/pokeagent-emerald/segment2-request-states.jsonl:1` and `work/pokeagent-emerald/macro_choice.py:73-89`. The fake command uses no network.
The gate example is a captured public command (`work/jev-yru2-public/commands.jsonl` plus its committed `live-gate-question-retest-20260926.jsonl` answer); `jev gate --fake` uses that fixture offline and returns the frozen RISK decision. The fleet confirmations used the same design: sample rates, not fleet rates, with 47 harm rows in the held-out weighted population.
The fake command returns `lost_or_stolen_card` (confidence 0.86) for the captured row, while that source row's true label is `card_arrival`; this example shows the tool output, not a guaranteed-correct answer. The measured Banking77 result is 2,467/3,080 (80.1%), not 100%.


The stranger-runnable top-1 rerank verb uses one Choice over all candidate passages and refuses more than 20 or OVER/NEAR states:

`node kit/bin/jev.mjs rerank --query "Tax implications of holding EWU (or other such UK ETFs) as a US citizen?" --candidates kit/examples/rerank-candidates.json --fake --robot`
For a live call, set `TYPESAFE_API_KEY` outside the repository using the official [TypeSafe quickstart](https://docs.typesafe.ai/introduction/quickstart), then run the same command without `--fake`:

```bash
if [ -z "${TYPESAFE_API_KEY:-}" ]; then printf "NOT_RUN: no key\n"; fi; npx --prefix kit --no-install jev ask choice --state kit/examples/state.json --question kit/examples/question.json --robot || { rc=$?; exit "$rc"; }
```

The pinned model is `jev-1.13.0`.

## What Jev answers

| Decision shape | Return | Typical code use |
|---|---|---|
| Choice | one label plus probabilities | route, classify, select a tool |
| Score | rubric level plus probabilities | rank, filter, prioritize |
| Noul | a value in `[0, 1]` | verify a claim, flag a risk |

Every request is validated before code acts: the answer must name an offered option, probabilities must be finite and normalized, and low confidence must take the preregistered safe path.

## Measured wins

The table summarizes results whose receipts and bars are in [`docs/LEDGER.md`](docs/LEDGER.md). Values are not claims about an unpinned `jev-latest`; they are tied to `jev-1.13.0`, the named corpus, and the cited receipt.

<!-- BEGIN GENERATED: measured-wins -->
| Surface | Result | Shape | Evidence |
|---|---|---|---|
| Banking77 intent classification | Jev 2467/3080 (80.1%) vs Haiku 2267/3080 (73.6%) | Choice | `work/choice-banking77/score.py --set full-prompted` |
| SST-5 sentiment scoring | Jev 273/500, MAE 0.488 vs Haiku 251/500, MAE 0.556 | Score | `work/score-sst5/score.py` |
| SciFact claim verification | Jev 361/400 (90.2%, Brier 0.0709) vs Haiku 351/400 (87.8%, Brier 0.1002) | Noul | `work/noul-scifact/score.py` |
| Replicated web-screen | Jev+local 68/78 own attacks; 135/256 deepset; Hermes own 15/40 fresh S-Labs; 0/1,437 clean withheld; pinned jev-1.13.0 | Noul / web-screen | `work/hermes-webscreen-repro/RECEIPT.md; work/omp-hermes-screen/hermes-own-live-receipt-20260926.json; kerpopule/hermes-jev-skills@cf9e84c` |
| MiniWoB v3 held-out | v3 342/625 vs v1 321/625 (McNemar p=0.02203; spend $0.458563) | Computer-use | `work/miniwob-jev/live-20260925/receipt.json` |
| BEIR NFCorpus rerank | Jev top-1 70.9% vs BM25 58.1% (McNemar 45 vs 15, p=0.00013); free LLM 66.7% vs Jev 70.9% (McNemar 18 vs 28, p=0.184); nDCG free LLM 0.434 vs Jev 0.448; latency p50 25.9s; $0 by unchanged usage; 15+1 retries disclosed | Choice rerank / free incumbent | `work/rerank-scifact/receipt-nfcorpus-v2.json; work/rerank-scifact/receipt-jev-97bq.json` |
| BEIR FiQA rerank confirmation | Jev top-1 76.2% vs BM25 39.3% (McNemar 129 vs 10, p=1.65e-27); nDCG@10 delta +0.157; confirmatory top-1 bar passed; $0.119 | Choice rerank | `work/rerank-scifact/receipt-fiqa-mkex.json` |
| OMP judge usage | 1,711 calls, $0.3547; find 1,595, auto-thinking 113, judge_batch 2, judge 1 | OMP judge usage | `EVAL.md@b74704c9` |
| Jev gate question (blind fleet sample) | Jev catch 90/93 vs existing 92/93; precision 90/230 (39.1%) vs 92/359 (25.6%); harmless flagged 140/465 vs 267/465; McNemar b=128 c=1 p=3.82e-37; stratified sample rates, not fleet rates; jev-1.13.0 $0.018826; 52 pre-bar calls disclosed ($0.001774) | Noul / gate | `work/jev-uncd/final-receipt.json` |
| Jev held-out fleet confirmation | Jev caught 47/47 vs 47/47; sample precision 47/57 (82.5%) vs 47/196 (24.0%); weighted precision 67.3% vs 24.0%; weighted harmless flagged 1.4% vs 9.1%; McNemar b=141 c=2 p=1.8e-39; strata 196/1,488; 47 harm rows only (Wilson lower 0.924, reported not gated); jev-1.13.0 $0.0134 | Noul / gate | `work/jev-1lim/final-receipt.json` |
<!-- END GENERATED: measured-wins -->

Jev is already making approximately 1,711 decisions per day inside the omp fleet; the daily path and receipt boundary are documented in the ledger and the cited EVAL entry.

## Where it runs

- `work/jev-client/` — the current official-SDK client and policy surface.
- `foundation/` — keyless calibration and gate receipts.
- `demos/` — one-command examples using recorded answers first.
- `.omp/` — the integration seams: tools, hooks, and observation surfaces.

The next product step is `jev-kit`: a small TypeScript package with shared preflights, answer validation, fake-asker tests, receipts, `jev doctor`, and a robot JSON contract. It will replace duplicated caller-side guards without changing the official SDK wire contract.

## Read next

- [`docs/LEDGER.md`](docs/LEDGER.md) — complete measurements, boundaries, and receipts.
- [`docs-mirror/typesafe/introduction/quickstart.md`](docs-mirror/typesafe/introduction/quickstart.md) — official request shape.
- [`docs-mirror/typesafe/primitives.md`](docs-mirror/typesafe/primitives.md) — Choice, Score, and Noul.
- [`EVAL.md`](EVAL.md) — verification ledger with lane, N, model, and boundary.
