# PokéJev LOSS DEPTH step 4: resumed Leaf C battle arms

**Status:** `PREPARED-NOT-MEASURED`. This note authorizes a new, clean run only after
this file is committed and the wrapper's keyless tests pass. It supersedes no prior
receipt: the earlier `results-abyssal-leaf-code-v1.jsonl` partial is untrusted and
`NOT-SCORED` because its writer revision was not established.

## Resume boundary

- **Resume `k`:** `0`. The old partial rows are not reused, appended to, or counted.
- **Fresh output stems:** `leaf-c-r2-code` and `leaf-c-r2-code-noul`, selected with
  `--run-id`; neither can collide with the old `-v1` paths.
- **Reason for restarting at zero:** the old partial contains rows from before and
  after the factory fix, and its wrapper revision is not attributable. A new stem
  makes every row attributable or makes the arm fail closed during analysis.

## Question and preregistered comparison

On the same 200 Stage B team pairings, does adding exactly three live Noul features
to the committed deterministic Leaf C model improve battle outcomes over the same
code-only leaf model?

- `code`: frozen dev-fit logistic leaf model; no leaf Jev requests.
- `code+noul`: the same frozen model plus exactly `ko_now`, `danger_now`, and
  `switch_needed` in one `jev-1.13.0` request per eligible leaf turn.
- Primary statistic: paired win difference
  `I(code+noul wins) - I(code wins)` over `k=0..199`; report the exact two-sided
  paired permutation p-value and confidence interval.
- Secondary reports: each arm's wins and Wilson 95% interval, time losses,
  completed/error/fallback rows by reason, latency, Jev calls, input tokens, and
  documented spend. The fixed 70% line remains a report-only kill criterion;
  it is not retuned after observing these arms.
- Pairing and model rules follow the committed preregistration
  `loss-depth-pokejev-leaf-c-battle-prereg-20250925.md` and its pinned artifacts.

## Provenance gate

`work/loss-depth/pokejev-components/battle/run.py` now records on every result or
decision row:

- `stage_b_import_sha256` and `frozen_alpha_sha256`;
- `run_py_sha256`, the wrapper source hash captured at process start;
- `run_started_at_utc`, `row_started_at_utc`, and `row_recorded_at_utc`.

Before scoring, independently verify that every row in each fresh result file has
all fields, valid UTC timestamps, the same `run_py_sha256`, the expected Stage B
and leaf-model hashes, and the expected arm/run-id. Any missing, mixed, or
mismatched provenance makes that arm `NOT-SCORED`; do not repair rows or regenerate
a receipt.

## Authorized commands

Run keyless checks first:

```bash
work/poke-jev/.venv/bin/python -m unittest \
  work/loss-depth/pokejev-components/battle/test_run.py
work/poke-jev/.venv/bin/python \
  work/loss-depth/pokejev-components/battle/run.py selftest
```

Then, and only then, run each live arm from the repository root with the explicit
model selected by the existing `leaf_c.py` client. Use the canonical Infisical
wrapper for the key; do not put the key in a command log or fixture:

```bash
infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
  work/poke-jev/.venv/bin/python \
  work/loss-depth/pokejev-components/battle/run.py battles abyssal 200 \
  --workers 8 --leaf code --run-id leaf-c-r2-code

infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
  work/poke-jev/.venv/bin/python \
  work/loss-depth/pokejev-components/battle/run.py battles abyssal 200 \
  --workers 8 --leaf code+noul --run-id leaf-c-r2-code-noul
```

The live arms stop immediately on HTTP 401, HTTP 402, or key rejection. A stopped
or partial arm is `NOT-SCORED` and may resume only in another committed note that
names its next `k`; never append to these paths. Record actual model version,
request count, input/output tokens, spend, latency, and all stop reasons.

## Acceptance and planted negative

Positive acceptance requires both fresh arms to contain exactly 200 completed rows,
zero unfinished or harness-error rows, and independently passing the provenance
gate above. The paired result is reported only after the two fresh arms pass.

The pre-run negative is the old partial itself: it lacks attributable wrapper
provenance and must be rejected rather than silently merged. A scorer that accepts
it fails this preregistration. No battle result is authorized before this note's
commit exists.

## Boundary

This is a same-pairing Leaf C battle comparison, not a general Jev benchmark. It
does not establish superiority over a paid LLM, does not reuse the old partial, and
does not prove the held-out AUC delta generalizes to battles. No live call or battle
run has been made under this note at authoring time.
