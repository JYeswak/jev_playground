# Statistical rigor audit — 2026-09-20 `[receipt]`

**Lane:** offline. **Oracle:** `scipy 1.18.1` Clopper–Pearson (`binomtest.proportion_ci(method="exact")`) and `statsmodels 0.15.0` Wilson (`proportion_confint(method="wilson")`), cross-checked with the closed-form Wilson score. **Not** the conductor’s bisection.

Kill decisions are powered. Ship decisions are not. That orientation survives a different interval method.

## 1. Seven intervals, independently recomputed

Two-sided 95%. Claimed column is the conductor’s Clopper–Pearson.

| name | k/n | claimed CP | scipy CP | statsmodels Wilson | CP match |
|---|---|---|---|---|---|
| ft-rs bind | 0/25 | [0.000, 0.137] | [0.0000, 0.1372] | [0.0000, 0.1332] | yes |
| ft-md bind | 0/25 | [0.000, 0.137] | [0.0000, 0.1372] | [0.0000, 0.1332] | yes |
| ft-sh bind | 1/25 | [0.001, 0.204] | [0.0010, 0.2035] | [0.0071, 0.1954] | yes |
| absence FP | 4/20 | [0.057, 0.437] | [0.0573, 0.4366] | [0.0807, 0.4160] | yes |
| structural FP | 4/20 | [0.057, 0.437] | [0.0573, 0.4366] | [0.0807, 0.4160] | yes |
| callsite FP | 6/20 | [0.119, 0.543] | [0.1189, 0.5428] | [0.1455, 0.5190] | yes |
| Jev semantic | 3/6 | [0.118, 0.882] | [0.1181, 0.8819] | [0.1876, 0.8124] | yes |

**No OVERTURN of the claimed CP arithmetic.** All seven match scipy to the reported three decimals.

Wilson is the different method. Manual Wilson = statsmodels to 1e-6. Wilson uppers are tighter than CP (as expected). **No ship becomes certified under Wilson.** Absence/structural Wilson upper 0.416 still admits FP 0.42. Callsite Wilson upper 0.519 still admits FP 0.52.

Method split on **ft-sh only:** CP upper 0.204 touches the bind bar 0.20; Wilson upper 0.195 does not. Kill of bind≥0.20 still stands (see BH). Not an overturn of R64/R65/R66.

Certification of `FP ≤ 0.30` uses the **two-sided 95% upper bound ≤ 0.30** (same two-sided convention as the claimed CP). One-sided 95% uppers are looser on n, stricter on the claim; they do not change any of the three ship rulings.

## 2. Required n to certify FP ≤ 0.30 at 95%

Wilson two-sided 95% upper ≤ 0.30, future labels at the **observed rate**, `k = round(p̂ n)`.

| rule | observed | p̂ | n today | required n | at that n |
|---|---|---:|---:|---:|---|
| absence-from-one-probe | 4/20 | 0.20 | 20 | **77** | 15/77, Wilson upper 0.297 |
| bash-structural-def-search | 4/20 | 0.20 | 20 | **77** | same |
| bash-callsite-grep-exclusion | 6/20 | 0.30 | 20 | **∞** | Wilson upper of p̂=0.30 is always > 0.30 |
| pipe-exit v2 (R51 labels) | 3/20 | 0.15 | 20 | **30** | 4/30, upper 0.297 |
| hypothetical 0 FP | 0/n | 0 | — | **9** | 0/9, upper 0.299 |

One-sided 95% Wilson: 52 / 52 / ∞ / 22 / 7. Same qualitative result.

Callsite cannot be certified by labelling more at the same rate. The point estimate *is* the bar.

## 3. Benjamini–Hochberg

**Family size m = 17.** Every labelled binomial-vs-bar test I could name from today’s battery. q = 0.05.

Excluded from m (state them so the next round inherits): glob-silenced (no n=20 FP labels), R55 1-hit floor refuse (not a labelled rate), ft-py/ft-json bind (k/n not published), fire-rate vs 50-count (different sampling model).

| rank | p (exact binomial) | BH threshold i/m·q | BH | role | test |
|---:|---:|---:|---|---|---|
| 1–5 | 3.5e-11 | 0.0029–0.0147 | reject H0 | REFUSE | R57/R58/R62/R65-MD1/R65-SH2 20/20 vs FP≤0.30 |
| 6 | 1.7e-9 | 0.0176 | reject H0 | REFUSE | R56 19/20 |
| 7 | 1.1e-6 | 0.0206 | reject H0 | KILL | R64 pack 1/75 vs bind≥0.20 |
| 8–9 | 0.0038 | 0.0235–0.0265 | reject H0 | KILL | ft-rs, ft-md 0/25 |
| 10 | 0.0115 | 0.0294 | reject H0 | KILL | R66 error-shape 0/20 |
| 11 | 0.0274 | 0.0324 | reject H0 | KILL | ft-sh 1/25 |
| 12 | 0.107 | 0.0353 | retain H0 | SHIP | pipe-exit 3/20 certify FP≤0.30 |
| 13–14 | 0.238 | 0.0382–0.0412 | retain H0 | SHIP | absence, structural 4/20 |
| 15 | 0.607 | 0.0441 | retain H0 | — | jsm 6/15 vs 0.5 |
| 16 | 0.608 | 0.0471 | retain H0 | SHIP | callsite 6/20 |
| 17 | 1.000 | 0.0500 | retain H0 | — | Jev semantic 3/6 vs 0.5 |

max_i = 11. **FDR did not bite.** Every kill/refuse that was a kill/refuse uncorrected is still a reject after BH. Every ship-certify test still retains H0 — they were never significant. Jev 3/6 vs 0.5 is p=1. The “earned seat” is the baseline’s structural incapability (`jev-triage-seat-20260920.md`), not this rate.

## 4. Re-ruling the three shipped FP rules

All three: **shipped-on-underpowered-estimate.** Not certified.

| rule | pick | why |
|---|---|---|
| absence-from-one-probe | **relabel more to n=77** | Class is this lane’s actual exposure (R66). Independent recount this session 2/20 FP on a fresh seed, same order as 4/20. Finite n exists at p̂=0.20. Do not disable a real defect class because n=20 was cheap. |
| bash-structural-def-search | **relabel more to n=77** | Same math as absence. Keep live while labelling; do not treat live as certified. |
| bash-callsite-grep-exclusion | **disable** | p̂ sits on the bar. Required n is infinite at this rate. CI still admits 0.52 (Wilson) / 0.54 (CP). Relabelling more at 30% never certifies; narrowing without the six false labels is guessing. `ttsr.disabledRules` is reversible, same path as R64. |

Do not keep callsite live because it is already installed.

Glob-silenced still has **no labelled FP n**. It is a fourth underpowered ship, outside the three named above.

## 5. Standing rule (propose)

Every rate we report carries an exact interval (name the method). Every bar-decision states whether n could reject/certify the bar at 95%. The family size is declared before BH, and exclusions are named.

Mechanical:

1. For a SHIP bar `FP ≤ θ`, compute two-sided 95% Wilson upper on the labelled k/n. If upper > θ, the ship is **underpowered**, not certified. Required n is the smallest n with `k=round(p̂ n)` whose Wilson upper ≤ θ, or **∞** if p̂ ≥ θ.
2. For a KILL bar `bind ≥ θ`, the kill is certified only if the two-sided 95% upper is **< θ** (or the one-sided 95% upper is < θ — pick one and keep it). ft-rs/md pass both; ft-sh passes Wilson and BH, fails the “touching” CP reading.
3. Before the next battery, write **m** and the test list. Run BH at q=0.05. A decision that dies under BH does not ship.

This is cheap, it is mechanical, and it would have flagged all three ships today plus glob’s missing labels.

## NO-CLAIM

Not a disable of absence or structural. Not a new interval method bake-off. Not a claim that Wilson is “truer” than CP — only that it is independent and does not rescue the ships. Labels remain one-reader n=20; interval math cannot fix that. Family m=17 is the labelled-bar subset I could name; a later pass that finds three more tests should re-run BH with the new m, not reuse max_i=11.
