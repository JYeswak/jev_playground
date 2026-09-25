# Jev — typed decisions for code

Jev is TypeSafe's System One model for typed judgments. Give it a JSON state and a typed question; get a choice, score, or true/false value with probabilities and confidence. Jev does not generate prose. Your code owns the threshold, the safe side, and the action taken when an answer is malformed or uncertain.

This repository turns measured Jev behavior into small, runnable tools. The full measurement ledger lives in [`docs/LEDGER.md`](docs/LEDGER.md); source receipts and preregistrations are linked there instead of being copied into this page.

## Quickstart

```bash
git clone https://github.com/JYeswak/jev_playground.git
cd jev_playground
node demos/guard/demo.mjs
bash scripts/quickstart.sh
```

The first two commands use recorded answers and require no key. For a live call, install the documented dependencies, set `TYPESAFE_API_KEY` outside the repository, and run the same decision with the live flag. The pinned model is `jev-1.13.0`.

## What Jev answers

| Decision shape | Return | Typical code use |
|---|---|---|
| Choice | one label plus probabilities | route, classify, select a tool |
| Score | rubric level plus probabilities | rank, filter, prioritize |
| Noul | a value in `[0, 1]` | verify a claim, flag a risk |

Every request is validated before code acts: the answer must name an offered option, probabilities must be finite and normalized, and low confidence must take the preregistered safe path.

## Measured wins

The table summarizes results whose receipts and bars are in [`docs/LEDGER.md`](docs/LEDGER.md). Values are not claims about an unpinned `jev-latest`; they are tied to `jev-1.13.0`, the named corpus, and the cited receipt.

| Surface | Result | Shape | Evidence |
|---|---:|---|---|
| Banking77 intent classification | Jev 2,467/3,080 vs LLM 2,267/3,080 | Choice | [`EVAL.md`](EVAL.md), `docs/demos/upstream-repro/choice-banking77-full-20260924.md` |
| SST-5 sentiment scoring | Jev beats the free/LLM comparison on the preregistered MAE bar | Score | `docs/demos/upstream-repro/score-sst5-20260924.md` |
| SciFact claim verification | Jev wins the preregistered verification comparison | Noul | `docs/demos/upstream-repro/noul-scifact-20260924.md` |
| BEIR SciFact reranking | Jev improves the preregistered ranking metric | Choice/rerank | `docs/demos/upstream-repro/jev-rerank-l3-scifact-20260924.md` |

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
