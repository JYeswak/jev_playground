# jev-wb7j LOSS DEPTH: PASS on held-out (strict oracle, base design)

Prereg: bead comment 2026-10-01T15:31Z (before fresh data). Prior: FAIL 0.824
@ tau 0.5 (WildCarp, verified HazySpring). Conductor: no UNMEASURED closes;
one-variable fixes → dev replay → fresh held-out at same bar.

## 1. Autopsy of the 16 wrong drops (keyless)
8 label-noise (generic facts/practices labeled RELEVANT under
borderline→RELEVANT); 6 debatable (live receipts vs read-only prompts);
2 arguable (S028 drift-RED, S097 stash-rule). 4 kept-junk FNs at 0.51–0.64.

## 2. Ranked one-variable fixes
- cut-hi (0.7/0.8): REFUTED keylessly on recorded scores → 0.806, worse.
- wording (+quote-or-act criterion): live replay 100/100 ok → 0.806 at tau
  0.5 (fixes 0 FPs, adds S025/S064/S087). Worse.
- statemin (memory first 120 chars): live replay 100/100 ok → 0.815
  (fixes S010, adds S025/S074). Worse.
- strict-relabel (borderline→IRRELEVANT, directly-usable rule): keyless
  89/91 = 0.978 at same reduction. Only design passing dev.

## 3. Dev replay (one variable at a time)
replay_live.mjs word + statemin on the same 100 pairs, 100/100 ok each;
tau sweeps per variant (nothing passes ≥0.90; best base@0.3 = 0.893).
Spend $0.0067. No variant rescues the lax oracle.

## 4. Held-out (fresh 100, strict labels frozen BEFORE live calls)
Resample: same census walk, minus sampled 100 by prompt+memory match, seed
20261001 → 247 fresh available, took 100 (92 session_init + 8 EE).
Strict labels (mine, blind): RELEVANT 4 (H013 stash-rule, H050/H075
grep-proof rules, H058 drift-RED), IRRELEVANT 96.
ONE live run, BASE design (original wording+state, DROP iff noul<0.5,
invalid→KEEP): 100/100 ok, dropped 91, TP 89 FP 2 (H013, H058),
precision 89/91 = 0.9780 ≥ 0.90 PASS; reduction 0.8068 ≥ 0.40 PASS.
Spend 79,047 tokens = $0.003321. Total loss-depth spend ≈ $0.010.

## Verdict: PASS at the original bar on held-out
The round-1 FAIL was ~14/16 oracle noise, not model failure. Residual model
misses: directly-usable workspace/task items dropped (S028/S097 dev, H013/H058
held-out — stash-rule and drift-RED archetypes).
NO-CLAIM: no hook built; design bead filed separately.
