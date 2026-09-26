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
```

The example state and Choice question are captured from committed rows: `work/pokeagent-emerald/segment2-request-states.jsonl:1` and `work/pokeagent-emerald/macro_choice.py:73-89`. The fake command uses no network.

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
| Replicated web-screen | Jev+local 68/78 own attacks; 135/256 deepset; Hermes own 15/40 fresh S-Labs; 0/1,437 clean withheld; pinned jev-1.13.0 | Noul / web-screen | `work/hermes-webscreen-repro/RECEIPT.md; kerpopule/hermes-jev-skills@cf9e84c` |
| MiniWoB v3 held-out | v3 342/625 vs v1 321/625 (McNemar p=0.02203; spend $0.458563) | Computer-use | `work/miniwob-jev/live-20260925/receipt.json` |
| OMP judge usage | 1,711 calls, $0.3547; find 1,595, auto-thinking 113, judge_batch 2, judge 1 | OMP judge usage | `EVAL.md@b74704c9` |
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
