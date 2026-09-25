# PokéJev Leaf C r4: action-ranking leaf preregistration

**Status: `PREPARED-NOT-MEASURED`.** This note replaces the invalid r3 search-leaf
claim. No battle or Noul call is authorized by this note. The r3 partial is
`NOT-SCORED` in `loss-depth-pokejev-leaf-c-r3-partial-20250925.md`, and R109 in
`NEGATIVE_EVIDENCE.md` records why winner AUC was the wrong gate.

## Failure being fixed

The r3 leaf predicted the recorded winner, not the value of an action. Its
`ko_threat` feature was derived from the recorded action type in
`leaf_c.py:237`, then applied per candidate in `run.py:453`. The frozen coefficient
therefore gave every switch a fixed advantage (`-0.149221 / 0.323709`, about
`+0.461` logit relative to a move), while the remaining features described only
our side. Winner AUC cannot certify action ranking.

## Preregistered r4 feature contract

1. **Remove `ko_threat` entirely.** It is not a candidate outcome; it is a label
   leak from the winner-prediction corpus. It must not appear in the feature list,
   artifact, or live candidate vector.
2. Keep our-side `hp_weighted_remaining`, `status_count`, `hazard_count`, and
   `speed_order_rate`.
3. Add opponent-side post-candidate features:
   - `opponent_hp_remaining`: the sum of known opponent team HP fractions / 6;
   - `hp_differential`: our HP remaining minus opponent HP remaining.
   Replay and live code must compute both from the same team/event semantics.
   Candidate summaries must carry opponent active/bench HP after the simulated
   action; hidden/unseen opponent members are excluded consistently in both lanes.
4. Fit exactly the resulting six-feature code model and the same six-plus-three
   Noul model on dev only. Keep the existing StandardScaler and
   LogisticRegression(C=1.0, l2, liblinear, random_state=20260925). Do not tune
   after seeing held-out or battle results.

## Keyless action-ranking gates

Before any held-out refit is accepted or battle is considered:

- **Candidate sensitivity:** two recorded-turn move candidates with different
  post-candidate opponent HP and HP differential must receive different frozen
  leaf scores. A move-vs-switch difference caused solely by action type is a
  failure because that feature is removed.
- **Recorded-turn sanity:** on 100 recorded Stage B decisions with a switch
  offered, the r4 leaf's switch selection rate must be within 10 percentage points
  of the Stage B offered-switch reference `0.41`. This is a sanity gate, not a
  performance bar. The fixture and selected 100 rows are committed before the
  refit; no rows are authored after seeing r4 choices.
- **Parity:** at least three recorded turns must have live and replay vectors
  equal within `1e-6` for every r4 feature.

A failed gate is `NOT-SCORED`; no held-out or live battle is allowed until the
feature implementation is corrected and the gate is rerun from the same fixture.

## Dev fit and one held-out score

After the keyless gates pass, refit once on the committed dev split, freeze the
artifact, and score the committed held-out split exactly once. Record N, class
counts, AUC with interval, exclusions, model SHA, and the action-ranking gate
outputs. The held-out AUC is descriptive and subordinate to the action-ranking
sanity gates: a passing AUC with a failing action gate is a kill, not a model win.

No new Jev calls are needed for this refit if the cached Noul rows cover the
held-out set. If they do not, report code-only and `code+Noul NOT_RUN`; do not
spend Noul calls to fill the cache under this note.

## Experimental structure

The unit is the recorded decision, nested in battle. The dev/held-out battle split
is fixed and respected; no decision within a battle is treated as an independent
battle replicate. Both model variants use the same rows and frozen feature order.
The held-out score is a single confirmatory read, not sequential tuning. Action
ranking is checked on recorded turns before any new battle arm, preventing the
r3 failure from being hidden by a winner-prediction metric.

## Boundary and retry condition

This note does not authorize a battle. A new battle note is required after the
r4 artifact and held-out receipt are committed. Retry only with a further
preregistered feature change if the action-ranking gate fails; do not rerun the
same winner-prediction leaf or spend Noul calls to rescue it.
