# Jev-seat power — 2026-09-20 `[receipt]`

**Lane:** offline. **Oracle:** scipy 1.18.1 `binomtest` (exact McNemar) + closed-form Wilson, checked against statsmodels 0.15.0. **Not** a new live Jev call. **Not** a rescoring of the 23.

This is NEED #4. The bar is written **before** any required-n. The numbers below that line are not inputs to the bar.

---

## 0. Preregistered bar (locked before the n)

The surviving seat is **not** “3/6 > 0/6”. The numeric baseline is structurally 0 on meaning, so any Jev accuracy > 0 “beats” it. That comparison cannot earn a paid call.

**Endpoint.** Accuracy of Jev @ t=0.5 on the *semantic set*: classes that already cleared the numeric bars and that a human refused on meaning. Gold = that human label. One row = one class. No peeking at noul to drop rows (the 3/3 low-noul slice is post-hoc and is not the endpoint).

**Effect size.** A veto that is a coin is worse than no Jev call: it spends money and injects false “ordinary usage” refusals. The smallest effect that is still a *seat* is: accuracy is not a coin.

**Bar, two levels, named so we cannot slide:**

| id | claim | mechanical |
|---|---|---|
| **WEAK** | not a coin | Wilson two-sided 95% **lower** bound on accuracy **≥ 0.50** |
| **STRONG** | usable veto | Wilson two-sided 95% **lower** bound on accuracy **≥ 0.70** |

WEAK is the necessity-gate bar (principled reason to keep Jev in the loop). STRONG is the deployable-veto bar. NEED #4 is WEAK. Asymmetric loss: a false low-noul veto of a real defect is worse than missing a non-defect; that is why STRONG exists and why WEAK is already the floor, not a gift.

**What would fail the bar.** Observed p̂ ≤ 0.50 cannot certify WEAK (Wilson lower is always < p̂). If the MLE stays 0.50, required n is **∞**. That is a legal outcome.

McNemar χ² is **not** the test at this n. See §2.

---

## 1. Required n (computed after the bar)

Today: **3/6**, Wilson [0.188, 0.812]. Lower 0.188. WEAK fail. STRONG fail.

| assumed future p̂ | WEAK (lower ≥ 0.50) | STRONG (lower ≥ 0.70) |
|---|---|---|
| **0.50 (today’s MLE)** | **∞** | **∞** |
| 0.60 | n=91 (55/91) | ∞ |
| 0.70 | n=21 (15/21) | ∞ |
| 0.80 | n=11 | n=77 (62/77) |
| 1.00 | n=4 (4/4, lower 0.51) | n=9 (9/9, lower 0.70) |

The 3/3 low-noul slice, if someone tried to promote it after seeing noul: Wilson [0.439, 1.000]. Lower 0.439. **Fails WEAK even as a selected 3/3.**

---

## 2. McNemar at n=6

**χ² McNemar is not valid.** Rule of thumb: expected discordant/2 ≥ 5 ⇒ n_discordant ≥ 10. Aggregate retraction used n_d=5 (expected 2.5). Semantic-vs-always-wrong-baseline would use n_d=3 (expected 1.5). Yates χ² on (b=3,c=2) is 0; that is a small-sample artifact, not evidence of equality.

**Exact conditional binomial on discordant pairs is required** (and is what the retraction already used).

| comparison | b | c | n_d | exact two-sided p | χ² valid? |
|---|---:|---:|---:|---:|---|
| aggregate SHIP-vs-rest @0.5 | 3 | 2 | 5 | **1.0** | no |
| semantic vs baseline 0/6 | 3 | 0 | 3 | **0.25** (one-sided 0.125) | no |

Even giving Jev the most favourable pairing against a baseline that cannot be right, p=0.25. Cannot reject a coin. The 3/6 vs 0/6 “seat” is a structural remark about the baseline, not a significant paired difference.

---

## 3. Growth plan (exposure, not a guess)

`r-classify.json`: **n_semantic_callable = 6**. That is the whole stock from 62 R-headings (54 `not_a_class`). All six are already scored. `advisory-veto.mjs` only logs a class that already `shipPredicate`s (numeric bars) and then spends one Noul. It cannot mint gold labels; a human meaning-refuse after the numbers said SHIP is the gold.

R66 closed doctrine-mining. Remaining arithmetic classes already failed FP/rate/floor. Unlabelled numeric-passers left in the live pack: glob-silenced (no FP n) — at most **one** extra cold call, not a labelled semantic row until a human refuses it on meaning.

Observed arrival of *new* semantic classes: **6 in the lifetime of the ledger**, produced in one mining day, then the vein was recorded exhausted. That is a stock of 6, not a Poisson rate of 6/day.

| if we pretend | time to WEAK at p̂=0.60 (n=91) |
|---|---|
| 1 new labelled semantic class / week | 85 weeks after today |
| 1 / month | 7 years |
| 0 / week (R66: stop mining doctrine) | never |

91 rows at p̂=0.60 is already **above** the observed 0.50. At the MLE, time is infinite at every rate.

Cost: 1 live Noul per cold class. Unreachable n is not a budget problem.

---

## 4. Verdict

**The last Jev seat cannot be certified here.** WEAK is ∞ at the observed rate. The semantic stock is 6 and already spent. Growth at fleet exposure is 0–1 new labelled meaning-row per week in the generous story, and 0 in the R66 story. I will not carry the seat on an assumed p̂=0.70 that the data do not show.

**Retire the low-noul veto as a Jev *seat*.** Keep the *necessity gate* as process: refuse a Jev integration that lacks a deterministic baseline on identical rows, a stated asymmetric-loss posture, and prevalence. That gate does not need a certified model; it needs the baseline to win, which it has four times.

`advisory-veto.mjs` may keep logging. Logging is not a seat.

## NO-CLAIM

Not a new noul run. Not a claim that Jev is useless on other questions. Not a disable of `advisory-veto.mjs`. Not McNemar χ². Family size for this decision: **1** (the WEAK bar on this endpoint).
