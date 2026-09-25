# Leaf C r3 refit and held-out receipt

**Status: `offline-verified`; no r3 battle arm run.** Preregistration:
`loss-depth-pokejev-leaf-c-r3-prereg-20250925.md` (committed before this receipt).

## Code and model provenance

- Replay/live HP contract: full known team, initialized from `|poke|` at `1.0`,
  then updated by switch/damage/heal/faint events; live sums `battle.team` / 6.
- Candidate HP parser fixed to `re.findall(r"(\d+)%", ...)`.
- New frozen artifact:
  `work/loss-depth/pokejev-components/leaf-model-v1.json`.
- Artifact SHA256:
  `05e4ac31457665e478237be51741869cb7005b5911da17cfd33ae77b8cd3525f`.
- `battle/run.py` pins that exact SHA; a keyless loader check returned
  `sha_match True` and the expected five code features plus three Noul features.
- Fit: dev split only, 2,060 code rows and 2,060 cached-Noul rows, using the
  preregistered StandardScaler + LogisticRegression(C=1.0, l2, liblinear,
  random_state=20260925).
- Noul cache: 4,334 rows, 0 errors, model `jev-1.13.0`; no new Jev call was made
  for this receipt.

## Keyless gates

```text
work/poke-jev/.venv/bin/python -m unittest work/loss-depth/pokejev-components/battle/test_run.py
Ran 10 tests ... OK

work/poke-jev/.venv/bin/python work/loss-depth/pokejev-components/leaf_c.py --selftest
SELFTEST PASS 2/2
```

The three new checks passed: different post-move HP produces different leaf
scores; three recorded Stage B first turns match the full-team replay vector within
`1e-6`; and the 100-row recorded dev sanity arm stays within 10 percentage points
of the `0.41` Stage B switch reference. `ruff format --check`, `ruff check`, and
UBS all completed with zero critical findings; UBS reported only existing warning
classes (20 warnings on the three Python files).

## Dev fit

`leaf_c.py --part dev --score --json` after the full-team feature change:

| Arm | N | Positive | Negative | AUC | 95% interval |
|---|---:|---:|---:|---:|---:|
| C code-only | 2,060 | 1,192 | 868 | 0.658107 | [0.589267, 0.725393] |
| C code+Noul | 2,060 | 1,192 | 868 | 0.693879 | [0.630711, 0.754289] |

Dev exclusions: fallback 209, unusable 384, missing turn 0; 95 battles.

## Held-out score

Receipt JSON: `work/loss-depth/pokejev-components/leaf-c-r3-heldout-20250925.json`.
Command:

```bash
work/poke-jev/.venv/bin/python \
  work/loss-depth/pokejev-components/leaf_c.py \
  --part heldout --heldout --score --json \
  --nouls work/loss-depth/pokejev-components/leaf-c-nouls.jsonl
```

| Arm | N | Positive | Negative | AUC | 95% interval |
|---|---:|---:|---:|---:|---:|
| C code-only | 2,274 | 1,171 | 1,103 | 0.645815 | [0.544163, 0.740815] |
| C code+Noul | 2,274 | 1,171 | 1,103 | 0.717475 | [0.636331, 0.788383] |

Held-out exclusions: fallback 172, unusable 395, missing turn 0; 95 battles.
The held-out fit used the 2,060 dev rows only. All 2,274 held-out rows had cached
Noul values. The receipt's JSON also records action-prior and leaf-value baselines.

## Boundary

This is a keyless feature-parity and held-out model receipt, not a battle result.
The r2 code partial is separately `NOT-SCORED` as a harness bug. No r3 `code` or
`code+noul` battle was authorized or run under this receipt; a fresh supervised
battle note is required next.
