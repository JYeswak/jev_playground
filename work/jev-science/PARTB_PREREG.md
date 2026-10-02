# Part B prereg: metamorphic invariance on recorded inputs (jev-2zbl)

Committed pre-live 2026-10-02. Live only on conductor KEY OK (still holding).

## Inputs (real, recorded, not typed)
- Anomaly arm: `var/agent-tmp/msax-pairs.json` (175 deduped failed-bash+retry pairs,
  observed retry exits; R142: V2 Choice went 81/81 fix_first, accuracy 0.444).
- Win arm: `work/hermes-webscreen-repro/rows.jsonl` (scored web-result units, outcomes recorded).

## Transforms (meaning-preserving by construction)
- T1 option-order permuted (msax Choice criteria map order swapped).
- T2 state field order shuffled (exits-first vs cmd-first).
- T3 question negated (msax: "will identical retry succeed" vs "will it fail";
  webscreen Score has no negation: substituted paraphrase + repeated identical call for stability).
- T4 state truncated to the decision-relevant span (msax: cmd only, drop exits;
  webscreen: top-3 units only).
- T0 identity re-run (stability control).

## Expected invariances (falsifiable)
- I1: T1 flips choice on <=10% of items (order irrelevance).
- I2: T2 flips choice on <=10% of items (field-order irrelevance).
- I3: T3-negated probabilities complementary within 0.15 (p_succeed + p_fail = 1 +/- 0.15);
  modal decisions agree >=85%.
- I4: T4 keeps modal choice on >=80% (relevant span suffices); mean confidence drops.
- I0: T0 repeats identical choice on >=95% (stability ceiling; anything below is noise floor
  for all other invariances).

## Design
- 40 msax held-out pairs x {T0,T1,T2,T3} = 160 calls; 40 webscreen rows x {T0,T3-stability,T4}
  = 120 calls. Total <=280 calls, spend stated, stop on 401/402/403, key-fetch failure = NOT_RUN.
- Flip = modal choice differs from the recorded original answer on file (not from a fresh call).
- Report per-transform flip rates with Wilson CIs + mean |dp| shifts; verdict per invariance.
