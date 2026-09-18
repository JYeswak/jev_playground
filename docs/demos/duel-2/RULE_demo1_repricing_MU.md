# Q102-U1 — Ruling: demo-1 kill repriced to 0.0447% (non-author arithmetic)

**Independent recomputation (mine, not relayed):** `0.0034228 / 7.658096908 = 0.00044695177…` →
**0.0446952%** → 0.0447% → 0.045%. Denominator-invariant: against actual spend
(`7.661519708`) the ratio is 0.044675% — identical at every cited precision. The conductor's
derivation is confirmed to the 5th decimal; the trivial difference (0.0446960 vs 0.0446952) is
input-rounding, immaterial.

## (1) RULED_OUT survives — a fortiori, and the direction is the reason.

The committed error **overstated** savings by ~5% relative (`(0.047−0.0447)/0.0447`); the correction
moves the number **away** from any behavior-change threshold, not toward one. The rung-4 gate asks
whether a stranger changes behaviour: thresholds in that class live at percent scale, and both
0.0447% and 0.047% sit near 10⁻⁴ relative — **no plausible threshold separates them.** Had the true
number been larger (toward material), survival would need re-argument; it is smaller. The kill's
second leg (zero Jev calls behind a hand-written heuristic) is untouched by any of this. **Kill
stands on the corrected number, on evidence that now disfavors the candidate more than before.**

## (2) Citation: the sibling alone — the excerpt is decited, not co-cited.

- **Correct citation for the figure:** `demos/routing-backtest/runs/backtest-20260918T020440Z.json`
  (30 turns, the derivation above recomputes from its fields).
- **The excerpt** (`backtest-real-excerpt.json`) is a *different measurement* (6 turns, negative
  savings), not a worse copy. Citing both would imply they corroborate; they disagree. The excerpt
  must be **decited for the figure** — co-citation would repeat the mispointer with a new number.
- **Concrete STATUS changes recommended** (conductor applies; column-collision rule respected):
  row receipt → the sibling file; reason `none-died-rung4-0.047pct` → `none-died-rung4-0.0447pct`.
  A reason string naming a number that does not derive is the defect; renaming it is the fix.

## (3) Citeable form: 0.0447% with the derivation attached.

Per the Q101 triple this scalar needs: (30 classifiable turns, savings/counterfactual-spend ratio,
percent). **0.0447%** (3 s.f.) matches input precision (5-s.f. savings) without over-claiming;
**0.045%** is honest rounding that discards a supported digit — acceptable in prose, not as the
record form. Either must carry `0.0034228/7.658096908` beside it: a scalar without its derivation
is how 0.047% survived this long (grep confirms the literal never existed in that directory — the
figure was computed once, written down wrong by one digit, and cited fourteen times from prose).

**Limit stated:** this rules the repriced kill only. The fourteen-site cleanup is UNIT 3; the gate
question is UNIT 2. Neither is prejudged here.
