# Skillranker PROCESS mirror — copy the loop, not the corpus

**Date:** 2026-09-20 · **Level:** `[test]` · **Upstream:** `Dicklesworthstone/skillranker` `origin/main` **`6a74cca`** (`6a74ccad279b5ee4a3973790ec01b47265307a54`) · MIT + OpenAI/Anthropic rider

**Product landing:** `work/omp-jev-route/` (extend the existing omp extension; no greenfield name)

**Not this pass:** re-measuring their 12-case corpus (already done:
[`skillranker-corpus-measured-20260919.md`](skillranker-corpus-measured-20260919.md), 8/10 under
their gate). This receipt maps the *process* from source and ships the smallest runnable slice.

**Claim:** unpromoted process mirror. No working-profile dogfood. No live Jev call.

## What their process actually is (source, `6a74cca`)

Read from a shallow clone of public `main` on 2026-09-20, not from memory.

```
live context → roster / explicit resolve → (optional Quill) → wide Choice+__none__
  → rerank Choice+__none__ + per-candidate fit Noul → local eligibility
  → ranked | explicit | abstain | unavailable → structured JSON
  → hook (fail-open, shadow) → ledger / feedback (adoption ≠ usefulness)
  → frozen eval contract (0/1/2 loss, always-abstain control, diagnostic_synthetic cannot promote)
```

| Step | What it does | File:line at `6a74cca` |
|---|---|---|
| 1. Context | Exact session, latest request, bounded tail, task anchor | `README.md:714-744`; `src/pipeline.rs:1-6` |
| 2. Roster | What the harness can actually load; `--roster FILE` replaces discovery | `README.md:763-783`; `src/pipeline.rs:3` |
| 3. Explicit first | Resolved locally; no provider call. Missing target → unavailable | `src/eligibility.rs:88-108,147-149` |
| 4. Wide pass | One Choice over candidates + typed `__none__` | `src/jev/wide.rs:1-6,35-46` |
| 5. Rerank | Shortlist Choice + `__none__` and `fits::<id>` Noul | `src/jev/rerank.rs:1-4,28-36` |
| 6. Eligibility | Empty roster → unavailable. Excluded / already-loaded / low-fit / not-above-none → **abstain**. Each candidate must beat `__none__`; **ties abstain** | `src/eligibility.rs:22-66,155-197,274-289` |
| 7. Local score | Softmax over survivors only; cannot rescue a rejected candidate | `docs/scoring.md:1-6`; `src/scoring.rs` |
| 8. Decision envelope | `ranked` / `explicit` / `abstain` / `unavailable` | `src/output/mod.rs:34-38`; fixtures `tests/fixtures/output-{ranked,abstain}.v1.json` |
| 9. Hook | Claude `UserPromptSubmit`. Ordinary abstention is silent. **Never blocks.** Shadow logs without injecting | `README.md:1569-1608`; `src/adapter.rs:22,593-608` |
| 10. Feedback | Observations ≠ usefulness. `sr stats` / `sr feedback` on a local ledger | `README.md:1061-1091`; `src/storage/ledger.rs:1-5,194,256` |
| 11. Eval contract | Frozen 0/1/2 loss, always-abstain control **required**, `diagnostic_synthetic` forbids promotion | `tests/eval/evaluation_policy.v1.json:1-13,58-72,133-153`; `tests/eval/README.md:1-21` |

Decision kinds on the ledger (`src/storage/ledger.rs:194`):

```text
decision TEXT NOT NULL CHECK(decision IN ('ranked', 'explicit', 'abstain', 'unavailable'))
```

Abstain reasons (`src/eligibility.rs:22-41`): `low-fit`, `already-loaded`, `excluded`, `no-shortlist-match`.

Unavailable reasons (`src/eligibility.rs:45-61`): `explicit-resolution`, `empty-roster`, `roster-changed`.

Loss table (`tests/eval/evaluation_policy.v1.json:58-71`) — copied verbatim into
`work/omp-jev-route/src/gate.mjs`:

| class | loss |
|---|---:|
| correct recommendation on positive | 0 |
| correct no-match abstention | 0 |
| false abstention on positive | 1 |
| incorrect recommendation on positive | 2 |
| needless recommendation on no-match | 2 |
| operationally unavailable on attempted case | 2 |

Their rationale, which we keep: *a loss that charges only wrong emitted suggestions is invalid
because always abstaining would minimize it without helping positive cases*
(`evaluation_policy.v1.json:70-71`). The always-abstain counterexample is
`tests/eval/expected_values.v1.json:56-74` (total 4 vs mixed-policy 2 on a 6-case cohort).

## Steps we copy

1. **Bounded Choice with a real `__none__` sentinel** — abstention is a first-class option, not a missing score.
2. **Local eligibility after scores** — empty roster is unavailable; excluded / already-loaded / low-fit / not-above-none abstain; ties against `__none__` abstain.
3. **Explicit resolution is local** — a named skill does not go to the provider.
4. **Structured JSON decision** — `decision`, `reason`, `skills[]`, `none_probability`, schema stamp.
5. **Fail-open / observe-only** — never `{block:true}`; a throwing sink still returns `undefined`.
6. **Preregistered eval gate** — their 0/1/2 table, always-abstain control, `diagnostic_synthetic` cannot promote.
7. **Adoption ≠ usefulness** — a logged decision is not a quality claim. `binding: log-only`.

## Steps we will NOT copy (and why)

| Upstream step | Why not | Cost / defect if copied |
|---|---|---|
| Quill / FrankenSearch 254-wide prefilter | Wrong harness. omp skill lists are small; we do not have a 254-option roster | A second retrieval stack for a problem we do not have |
| Two-stage wide + rerank Jev calls | Cost: 2 paid calls per turn. Their own `wide.rs:4-6` says a winning `__none__` still reranks | Doubles spend; our earlier corpus run already used one bounded Choice |
| Claude `UserPromptSubmit` / 1024-char `additionalContext` | Wrong harness. omp uses `pi.on` + `appendEntry` | A guessed-equivalent integration (AGENTS.md:592) |
| SQLite XDG ledger (`$XDG_DATA_HOME/sr/ledger.sqlite3`) | We already have `appendEntry` + JSONL (`jev-usage-router`, dogfood-logger) | Third store, Linux-only in their tree (`src/lib.rs` storage cfg) |
| FrankenTUI | No consumer in omp | Process porn |
| cass session source | omp `context` events already carry `messages[]` | Second transcript parser |
| EffectGate 128-flag matrix | Observe-only slice has no persist/network flags to compose | Ceremony without a consumer |
| 300-family promotion cohort | We do not have it; their policy forbids treating `diagnostic_synthetic` as holdout | Re-litigating a bar we cannot clear honestly |
| Re-running `synthetic_cases.v1.jsonl` | Already measured (8/10). This pass is process, not corpus | Same origin counted twice |

## Mapping onto omp

| Their step | Our seat | What this slice does |
|---|---|---|
| Context → rank | **`work/omp-jev-route`** | Hosts `decide` / `appendProcessDecision` / CLI. Existing hardness observer unchanged |
| Local exclusion / already-loaded | **`work/omp-jev-preaction`** | Deterministic regex exclusion; no Jev. Process `excluded` / `alreadyLoaded` fields are the join |
| Decision log | **`work/omp-jev-observer`** + route `appendEntry` | Process rows use `com.zeststream.omp-jev-route.process.v1` |
| Cheapest adequate action + bypass | **`work/jev-usage-router`** | Bypass ≈ abstain/unavailable. Not rewritten this pass |
| Local feedback ≠ usefulness | **`work/taste-loop`** | Observe-only dogfood. Process `binding: log-only` is the same rule |

## What shipped

| file | role |
|---|---|
| `work/omp-jev-route/src/process.mjs` | `decide` + `appendProcessDecision` (abstain path) |
| `work/omp-jev-route/src/gate.mjs` | Copied LOSS / POLICY / `evaluate` / `alwaysAbstain` |
| `work/omp-jev-route/src/cli.mjs` | ACCEPTANCE runner |
| `work/omp-jev-route/fixtures/process-cases.v1.jsonl` | **Our** 6-row class-coverage oracle — not their corpus |
| `work/omp-jev-route/test/process.test.mjs` | 14 tests |
| `work/omp-jev-route/test/gate.test.mjs` | 5 tests |
| `work/omp-jev-route/src/index.ts` | Calls `appendProcessDecision` on `context` when `event.roster` is present |

## ACCEPTANCE (run these)

Offline. No key. No network.

```bash
# 1. Abstention + structured JSON decision log
node work/omp-jev-route/src/cli.mjs decide --fixture work/omp-jev-route/fixtures/process-cases.v1.jsonl

# 2. Preregistered eval gate (copied contract). Must print promoted:false
#    and always_abstain_mean_loss. Exit 0 = contract shape holds, not a quality win.
node work/omp-jev-route/src/cli.mjs gate --fixture work/omp-jev-route/fixtures/process-cases.v1.jsonl

# 3. Unit tests for the slice
node --test work/omp-jev-route/test/process.test.mjs work/omp-jev-route/test/gate.test.mjs
```

Planted negatives the tests already encode:

- empty roster → `unavailable` / `empty-roster`, never a ranked guess
- `__none__` tie → `abstain` / `no-shortlist-match`
- always-abstain control must lose on their 6-case counterexample cohort (4 vs 2)
- a perfect authored fixture still prints `promoted: false`

## Ran here (2026-09-20, this checkout)

- `node --test work/omp-jev-route/test/process.test.mjs work/omp-jev-route/test/gate.test.mjs` → **19/19**
- `cli.mjs decide` → 6 rows: ranked / abstain / abstain / ranked / ranked / unavailable
- `cli.mjs gate` → mean loss **1.167**, always-abstain **0.667**, top-1 **0.333**, **`promoted: false`**

The class-coverage fixture is *supposed* to lose to always-abstain: it plants a wrong pick,
a needless suggestion, and an operational unavailable. That is the control working, not a
regression. The counterexample that proves always-abstain is the worse policy lives in
`test/gate.test.mjs` (their `expected_values.v1.json` cohort, not this fixture).

## NO-CLAIM

- Not a measurement of skillranker. Their binary, prompt construction, and two-stage Jev
  calls were not run.
- Not a re-score of `synthetic_cases.v1.jsonl`.
- Not working-profile dogfood. The omp handler fires only when `event.roster` is present;
  no profile was registered.
- Not promoted. `diagnostic_synthetic` cannot promote. Ledger stays **0 promoted**.
- Authored 6-row fixture is a contract oracle. R28 applies: do not cite its rates as quality.

## Boundary

No live Jev. No `sr` binary. Clone used for reading only (`/tmp/skillranker` @ `6a74cca`),
not vendored, not committed, not patched. `index.ts` still imports `askJev` from the
lab-absolute path; that pre-existing deploy note is untouched.
