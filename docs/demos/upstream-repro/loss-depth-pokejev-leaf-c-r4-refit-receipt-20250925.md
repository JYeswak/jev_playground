# Leaf C r4 action-ranking refit receipt

**Status: `offline-verified`; no r4 battle and no new Noul call.** Preregistration:
`loss-depth-pokejev-leaf-c-r4-prereg-20250925.md`, committed before the code and
model change.

## Feature and artifact provenance

- `ko_threat` is removed from replay rows, live candidate vectors, and the frozen
  artifact. It was a recorded-action label, not an action outcome.
- Frozen feature order:
  `hp_weighted_remaining`, `status_count`, `hazard_count`,
  `speed_order_rate`, `opponent_hp_remaining`, `hp_differential`.
- `opponent_hp_remaining` is known opponent team HP / 6; `hp_differential` is our
  full-team HP remaining minus that value. Candidate summaries now include the
  existing opponent active and seen-bench lines.
- Artifact:
  `work/loss-depth/pokejev-components/leaf-model-v1.json`.
- Artifact SHA256:
  `ad8cd16482eb41e409409c94c968d0b2857f736bd6258b9afd556d785273c49b`.
- Dev fit: 2,060 rows for code-only and 2,060 rows with cached Nouls. The exact
  preregistered StandardScaler + LogisticRegression(C=1.0, l2, liblinear,
  random_state=20260925) was used.

## Keyless action-ranking gates

```text
work/poke-jev/.venv/bin/python -m unittest work/loss-depth/pokejev-components/battle/test_run.py
Ran 11 tests ... OK

work/poke-jev/.venv/bin/python work/loss-depth/pokejev-components/leaf_c.py --selftest
SELFTEST PASS 2/2
```

The action-ranking checks passed:

- two move summaries with different opponent HP / HP differential receive
  different frozen scores;
- three recorded Stage B first turns match live full-team and opponent-team
  replay features within `1e-6`;
- 100 recorded decision rows with a switch offered select 33 switches (`0.330`),
  within 10 points of the Stage B reference `0.410`.

The 100-row sanity fixture is the committed recorded-decision fixture
`decisions-abyssal-leaf-code-v1.jsonl`; it is a sanity arm, not a battle result or
an AUC bar. The r3 live choices are not reused as a passing fixture.

`ruff format --check`, `ruff check`, and UBS completed with zero critical findings;
UBS reported only its existing warning classes. The model hash loader returned
`R4_MODEL_PIN_PASS`.

## Held-out score: one read

Receipt JSON:
`work/loss-depth/pokejev-components/leaf-c-r4-heldout-20250925.json`.
Command:

```bash
work/poke-jev/.venv/bin/python \
  work/loss-depth/pokejev-components/leaf_c.py \
  --part heldout --heldout --score --json \
  --nouls work/loss-depth/pokejev-components/leaf-c-nouls.jsonl
```

| Arm | N | Positive | Negative | AUC | 95% interval |
|---|---:|---:|---:|---:|---:|
| C code-only | 2,274 | 1,171 | 1,103 | 0.826888 | [0.754631, 0.883540] |
| C code+Noul | 2,274 | 1,171 | 1,103 | 0.824212 | [0.753697, 0.881981] |

Held-out exclusions: fallback 172, unusable 395, missing turn 0; 95 battles.
All 2,274 held-out rows had cached Noul values. The held-out score is one
winner-prediction read; it does not authorize a battle or prove action ranking
beyond the keyless gates above.

## Boundary

The r2 and r3 live arms remain `NOT-SCORED` harness-bug receipts. No r4 code or
code+Noul battle has run, and no new Noul calls were made. A separate committed
battle note is required if these action-ranking gates remain acceptable for a
future supervised battle; this receipt itself does not authorize one.
