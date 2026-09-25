# PokéJev Leaf C r3: feature parity and refit preregistration

**Status: `PREPARED-NOT-MEASURED`.** This note is committed before any r3 battle
arm. The interrupted r2 code arm remains `NOT-SCORED` under
`loss-depth-pokejev-leaf-c-r2-partial-20250925.md`.

## Fixed feature contract

Use **full known team HP** in both lanes:

- Replay `|poke|` team-preview rows initialize every listed team member at `1.0`.
  Later `|switch|`, `|-damage|`, `|-heal|`, and `|faint|` events update that member.
  `hp_weighted_remaining = sum(known team HP fractions) / 6`.
- Live `_base_features` already sums the six `battle.team` HP fractions / 6.
- Candidate summaries parse integer post-action percentages with
  `re.findall(r"(\d+)%", ...)`; each candidate's post-move HP is scored rather
  than falling back to the pre-action base.
- Status, hazard, and speed features retain their existing definitions. No
  threshold or coefficient is tuned after inspecting r2 outcomes.

This is a training-feature definition change. The frozen logistic model MUST be
refit on the committed dev rows after this parser change and scored once on the
committed held-out rows before any live battle. The old `leaf-model-v1.json` is
not valid for r3 until replaced by that refit and its SHA is updated in `run.py`.

## Keyless tests before refit and before battle

Run from the repository root with no Jev key:

```bash
work/poke-jev/.venv/bin/python -m unittest \
  work/loss-depth/pokejev-components/battle/test_run.py
work/poke-jev/.venv/bin/python \
  work/loss-depth/pokejev-components/leaf_c.py --selftest
```

The suite must show all of the following:

1. Two move candidates with post-move summaries at different HP receive different
   frozen leaf scores.
2. On three recorded Stage B replay turns, the live full-team vector equals
   `leaf_c.snapshot_features` within `1e-6` for HP, status, hazards, and speed.
3. As a non-bar sanity arm, 100 recorded dev leaf decisions with a switch offered
   select a switch within 10 percentage points of the Stage B reference rate
   `0.41`. This is not a performance acceptance threshold.

## Refit and held-out gate

After the keyless tests pass, fit the frozen code and code+Noul logistic payload on
`decision-split-v1.json`'s dev rows only. Preserve the existing feature order and
regularization (`StandardScaler`, `LogisticRegression(C=1.0, penalty="l2",
solver="liblinear", random_state=20260925)`). Write the new frozen artifact to
`work/loss-depth/pokejev-components/leaf-model-v1.json`, update its SHA pin in
`battle/run.py`, and record the model artifact SHA in the receipt.

Then score the held-out split exactly once using the dev fit. Report N, positive /
negative counts, AUC and Wilson/bootstrap interval for code-only and code+Noul as
available, plus exclusions and the artifact SHA. A failed held-out score is
`NOT-SCORED`; do not regenerate the split or tune the model to recover a result.

The refit and held-out score are keyless with respect to Jev when using the
existing cached Noul rows. If the cache is incomplete, report code-only held-out
and `code+Noul NOT_RUN`; do not make paid calls as part of this gate.

## Battle authorization after the gate

No battle is authorized until this note, the refit artifact, and the held-out
receipt are committed. Only then may a new run note authorize fresh stems, with
`--run-id`, supervised stderr capture, and one arm at a time. Every row must carry
`run_py_sha256`, the feature/model hashes, `run_id`, and UTC start/recorded times.

## Boundary

This preregistration tests train/serve feature parity and preserves a held-out
model gate. It does not claim the r2 partial was a valid comparison, does not
claim the new model wins battles, and does not authorize `code+noul` live calls or
any battle until the keyless/refit/held-out gates above pass.
