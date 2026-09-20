# Jobhunt × Jev — scientifically validatable ideas

**Date:** 2026-09-20 · **Level:** `[pending]` — research memo, zero live Jev calls,
zero apply-side wiring. Every numeral below is quoted from a committed receipt in
this repo, or is a *preregistered* formula that a later pilot must fill in.

**Mission this memo serves:** Validate Jev → build tools from what survives →
liven omp surfaces → dogfood → share findings. Applies are **paused**. This file
is idea generation plus validation recipes, not a product spec.

**Constraint already on the record (Path / Joshua):** deep job-match is **not** a
finished product. Any apply-gate needs labels **and** an always-abstain control
that beats baseline. This memo treats that as settled doctrine, not a question
to re-litigate.

**NO-CLAIM (leads, does not trail):** nothing here is measured on a resume or a
job application. `n≈28` historical applications plus a resume/claim ledger are
assumed as the *pilot corpus that could exist*, not as data already scored.
This repo has no jobhunt labels. Every idea below is a transfer of a *measured
method* from another surface. Transfer is a hypothesis; the receipts are about
tool-calls, spam, skill selection, and calibration, not hiring.

---

## How to read this file

Each idea is a **Decision Contract** in the shape this lane already uses
(`docs/demos/upstream-repro/math-and-next-level-20260919.md` §2.1):

- finite states \(S\), actions \(A\), non-negative loss \(L(s,a)\)
- a named cheap baseline \(a_0\)
- a named negative control that *must be able to win* if the table is broken
- a numeric success bar, written **before** any Jev call
- a reopen / kill condition

Question kinds follow the installed SDK, not memory
(`docs/demos/SDK-SURFACE.md`):

| kind | answers | use when |
|---|---|---|
| **Noul** | `.noul` only (no `.confidence`) | one yes/no condition on visible state |
| **Choice** | `.choice`, `.confidence`, `.probabilities` | mutually exclusive labels; include a real `__none__` |
| **Score** | `.score` (expected value, may sit between levels), `.confidence`, `.legend`, `.probabilities` | degree on a stated rubric |

Forbidden selectors: `.probability`, `.distribution`. A missing field that
silently becomes a constant score fabricates AUC **exactly 0.500**
(`SDK-SURFACE.md`; `work/oracle-kit/index.mjs` `auc().constant`).

---

## Shared math (do not re-derive)

### Skillranker 0/1/2 decision loss

From `work/skillranker-eval/contract/evaluation_policy.v1.json:58–71` and
`work/oracle-kit/index.mjs` `decisionLoss`:

| outcome | \(L\) |
|---|---:|
| correct recommendation on a positive | 0 |
| correct no-match abstention | 0 |
| **false abstention on a positive** | **1** |
| incorrect recommendation on a positive | 2 |
| needless recommendation on a no-match | 2 |

Always-abstain identity (required control):

\[
\bar L_{\text{always-abstain}} = \frac{n_{\text{pos}}}{n}
\]

On skillranker's 12-case diagnostic: \(10/12 = 0.833\). Live Jev mean loss
**0.167** (two cheap abstentions, zero wrong picks) — 5× better than
always-abstain, still **fails** their 0.90 top-1 gate
(`docs/demos/upstream-repro/skillranker-corpus-measured-20260919.md`).

`emissionOnlyLoss` (silence costs 0) makes always-abstain win. A gate that
uses it is broken (`work/oracle-kit/index.mjs`).

### Prevalence and the Bayes cut

\[
\frac{\text{FP}}{\text{TP}} \approx \frac{(1-\pi)\,\text{FPR}}{\pi\,\text{TPR}},
\qquad
t^\star(\pi) = \frac{L_{\text{FP}}(1-\pi)}{L_{\text{FP}}(1-\pi)+L_{\text{FN}}\pi}
\]

Foreman receipt: \(\pi = 30/186{,}449 = 0.016\%\). At 80% recall that is
**~24 TP vs ~55,791 FP ≈ 1:2300**
(`docs/demos/upstream-repro/prevalence-retrofit-20260919.md`,
`work/oracle-kit/prevalence_threshold.py`). An AUC without \(\pi\) is not a
deployability number. If \(\pi\) is unknown, write `PREVALENCE-UNKNOWN` and
do not ship a threshold.

### Proper scores already implemented

- Mann–Whitney AUC, ties half, both classes required, constant scores flagged
  (`work/oracle-kit/index.mjs` `auc`)
- 10-bin ECE and Brier (`foundation/CALIBRATION.md`; receipt
  `foundation/runs/20260917T224444Z.json`: ECE **0.061**, Brier **0.020**,
  n=60 noul, `jev-1.13.0` — *easy authored items, not transferable*)
- e-process, anytime-valid under optional stopping (`oracle-kit` `eProcess`;
  reject at \(e \ge 20\) for \(\alpha=0.05\))
- Feasibility arm: an obvious pair the pipeline *must* detect, else
  `auc ≥ 0.8` fails and **no verdict issues**

### What n≈28 can and cannot do

Assume 28 independently labelled historical applications. Wilson 95% CI for
a 14/28 = 0.50 rate is roughly **[0.33, 0.67]**. McNemar exact needs
discordant pairs; \(b=8,c=2\) is already \(p \approx 0.11\). Skillranker's
own promotion contract wants **300** primary families, top-1 ≥ 0.90 with
Wilson lower ≥ 0.80 (`evaluation_policy.v1.json:133–153`).

So at n=28 a pilot can **kill** (lose to always-abstain, lose to keyword,
fail the feasibility arm, go constant) and can report **descriptive** loss.
It **cannot promote** a deep-match product. That is a feature of the sample,
not a temporary inconvenience.

The claim ledger is the escape hatch: if one resume has \(C\) atomic claims,
citation-check n is \(C\), not 28.

---

## The 15 ideas

### 1. Ledger-backed claim citation

1. **Name.** Claim citation (does this resume sentence have a supporting ledger row?).
2. **Mathematical framing.** Binary Noul scored with Brier + ECE; decision
   layer is 0/1/2 on {cite, abstain}. Prevalence \(\pi =\) fraction of
   resume sentences that *do* have a ledger row (measure it; do not guess).
   Always-abstain mean loss \(= \pi\). This is the citation-check / “visible
   property only” transfer (`work/jev-question-writing/SKILL-SHORT.md` rule 3:
   judge what the state *shows*).
3. **Jev question shape.** **Noul:** “The resume sentence is supported by
   the attached ledger excerpt (same fact, compatible numbers/dates).”
   State = `{sentence, ledger_rows[]}` with the actual excerpt bytes, not a
   pointer. Optional parallel **Choice** over `{cite_row_id…, __none__}`
   when several rows are candidates.
4. **Required labels / data.** For each resume sentence: human (or
   deterministic id-join) label `supported ∈ {0,1}` plus the supporting
   row id if any. Planted unsupported sentences required (feasibility).
5. **Cheap baseline to beat.** Exact / fuzzy string overlap onto ledger
   titles and fact strings (token Jaccard, date equality). If the baseline
   already cites correctly, VOI of Jev is ≤ 0 (`work/oracle-kit/voi_harm_rule.py`
   shape).
6. **Required negative control.** Always-abstain (loss \(\pi\)). Coin-flip
   cite/abstain. A planted sentence that *discusses* a claim without
   asserting it (mention-vs-use; `docs/RULES.md` rule 7) must not count as
   supported.
7. **Success criterion.** (a) Feasibility arm AUC ≥ 0.80 and `constant=false`.
   (b) Mean 0/1/2 loss **strictly below** always-abstain. (c) On the residual
   the lexical baseline gets wrong, Jev mean loss < lexical mean loss.
   (d) Report ECE; do not ship a 0.5 cut. At n=C claims, also report Wilson
   interval on precision-of-citations.
8. **Failure / reopen.** Constant noul, or lexical baseline mean loss ≤ Jev,
   or mention-vs-use plant fires as “supported.” Reopen only with a new
   residual class the lexical join cannot see (paraphrase of a real ledger
   row) **and** a held-out set not authored by the question writer (R28).
9. **Receipt / doc.** `SKILL-SHORT.md` (visible property); `SDK-SURFACE.md`
   (`.noul`); `judgment-quality-20260919.md` (decompose; never take the
   monolithic verdict); `docs/RULES.md` rule 7 (text about a thing).

---

### 2. Dig-vs-invent on resume claims

1. **Name.** Dig vs invent (do not write a claim the ledger cannot support).
2. **Mathematical framing.** Skillranker / cass overflow analogue
   (`docs/demos/upstream-repro/jev-task-tests-cass-20260920.md` CASS-04/05):
   Y nonempty → must pick a supporting row (dig); Y empty → must `__none__`
   (invent is the correct *action*, not a resume sentence). Needless pick
   is loss 2. False abstention on a buried gold row is loss 1.
3. **Jev question shape.** **Choice** over shortlist row ids + `__none__`.
   Instructions: “Which ledger row, if any, supports writing this claim?
   Pick `__none__` if none does.” State = `{draft_claim, candidate_rows[≤5]}`.
   Do **not** add a second `helpful` Noul gate — that moved skillranker
   mean loss 0.750 → 0.167 by forcing abstention
   (`skillranker-corpus-measured-20260919.md`;
   `oracle-kit` `refuseInventedNoulGate`).
4. **Required labels / data.** Per draft claim: acceptable row set Y
   (possibly empty). Include overflow cases (gold at rank 4/5) and
   no-match cases (Y empty, lexical traps present).
5. **Cheap baseline to beat.** First-hit / BM25 on the shortlist. On
   CASS-04 the receipt says first-hit → loss 2, always-abstain → 1.
6. **Required negative control.** Always-abstain. Coin-flip among options
   including `__none__`. Empty-success plant: `count>0` hits that do not
   answer (CASS-07) must still be `__none__`.
7. **Success criterion.** Mean 0/1/2 < always-abstain **and** < BM25.
   Needless-suggestion rate on Y-empty cases ≤ 0.05 *descriptive* at
   small n (Wilson upper will be wide; do not claim the 0.02 Clopper–Pearson
   harm bar — that wants ~150 families). Both failures, if any, should be
   loss-1 abstentions, not loss-2 inventions (skillranker’s cheap-error
   pattern).
8. **Failure / reopen.** Any invented claim that would have gone on a
   resume (loss 2) at a rate ≥ always-apply-keyword. Reopen if a new
   paraphrase class appears that BM25 ranks last and Jev still invents.
9. **Receipt / doc.** `jev-task-tests-cass-20260920.md` CASS-04/05/07;
   `skillranker-process-mirror-20260919.md` (Choice+`__none__`, ties
   abstain); R42 / `NEGATIVE_EVIDENCE.md` (do not copy their corpus as
   ours).

---

### 3. Atomic JD must-have Nouls (never a monolithic “fit”)

1. **Name.** Atomic requirement presence.
2. **Mathematical framing.** Phishing-verdict lesson: end-to-end
   “is this phishing?” was **63.8%** while the same call’s
   `sig_free_hosting` sub-question was AUROC **0.96**; a two-line domain
   regex beat the verdict by **27 points** (McNemar p = 1.5e-8)
   (`judgment-quality-20260919.md`, `RULING-authored-vs-real-20260919.md`).
   Job-match as one Score is that verdict. Atomic Nouls are the
   sub-questions. Combine *in our code*.
3. **Jev question shape.** One **Noul** per must-have, one request or
   fan-out: “The resume/ledger shows evidence of <requirement X>.”
   State = `{requirement_text, resume_excerpt, matching_ledger_rows[]}`.
   Not “how good a match is this job.”
4. **Required labels / data.** Independent label per (application,
   requirement) pair: present / absent / unknown. Unknown excluded from
   the denominator (skillranker `unjudged_label`). Must-haves extracted
   *before* scoring, by a frozen rule (section headers, “required”,
   years-of-experience regex) — not by Jev.
5. **Cheap baseline to beat.** Keyword / canonical-skill alias hit on
   resume + ledger (e.g. `TypeScript|TS`). Years-of-experience: parse
   numbers, do not ask Jev for arithmetic.
6. **Required negative control.** Always-“present” (the commit-`describes`
   death: 31/31 yes, DEGENERATE — `SKILL-KILL-LIST.md`). Always-“absent.”
   Planted JD that names a skill the ledger does not have.
7. **Success criterion.** Per-requirement: `gradeQuestion` DISCRIMINATES
   (correct > best_constant + near-threshold count;
   `work/jev-client/measure-kit.mjs`). Across requirements, McNemar vs
   keyword on the *paired* (app, requirement) cells. Jev earns a seat
   only on the residual keyword misses. Feasibility: planted present and
   planted absent must flip (`auc ≥ 0.8`, `!constant`).
8. **Failure / reopen.** Constant “yes” on ordinary JDs (nag /
   `irreversible_publication` 12/12 noise). Keyword already ≥ Jev on the
   residual. Reopen if a new residual is *semantic equivalence* the alias
   table cannot encode (and the alias table was frozen first).
9. **Receipt / doc.** `judgment-quality-20260919.md`;
   `criteria-inversion-20260918.md` (elaboration can *hurt*; McNemar);
   `SKILL-KILL-LIST.md`; `SKILL-SHORT.md` (one judgment per question).

---

### 4. Apply-gate Choice + `__none__` with 0/1/2 loss

1. **Name.** Apply / abstain gate (advisory, observe-only).
2. **Mathematical framing.** Exact skillranker advisory contract. Actions
   `{apply, abstain}`. Y = “this historical application was a *correct*
   apply under a frozen label rule” (see labels). Always-abstain mean
   loss \(= n_{\text{pos}}/28\). Path already said: this is not a finished
   product; the control must be able to beat us.
3. **Jev question shape.** **Choice** `{apply, __none__}` — not a Noul
   “should I apply?” with a 0.5 cut. State = `{jd_must_haves[],
   resume_atomic_hits[], ledger_coverage[], constraints[]}` — measured
   shape in the state, no “this is a great fit because…” rationale
   (`docs/demos/jev-probe/NOTE-framing-leak.md`: framing flipped
   `router_pays` 0.21 → 0.59).
4. **Required labels / data.** Frozen *before* questions: a primary label
   that is **not** “we applied.” Options, pick one and write it down:
   (A) later interview/screen happened; (B) independent human “would apply
   again”; (C) all must-haves present by the atomic labels from idea 3.
   (A) is confounded by market/timing/ATS. (C) is the only label this
   repo’s methods can defend at n=28. State the confounder if you use A.
5. **Cheap baseline to beat.** Always-abstain. Always-apply. Keyword:
   apply iff every must-have aliases hits. That keyword rule is \(a_0\).
6. **Required negative control.** Always-abstain (identity \(n_{\text{pos}}/n\)).
   Coin-flip. `emissionOnlyLoss` plant: if the table lets silence win,
   the gate is invalid. `diagnostic_synthetic` (hand-written jobs)
   **cannot promote**.
7. **Success criterion.** Mean 0/1/2 < always-abstain **and** < keyword.
   Feasibility arm (idea 13) must pass first. At n=28 this is a **kill
   test**, not a promotion bar. Write `promoted: false` even if it wins.
   Wilson interval on apply-precision among emissions. Do not use
   skillranker’s 0.90 / n=300 bar as if 28 were 300.
8. **Failure / reopen.** Lose to always-abstain *or* keyword. Invented
   second-Noul override. Authored vignettes used as holdout (R28).
   Reopen only with a new non-authored label source (future outcomes
   with stated confounders) **and** n large enough for a pre-registered
   Wilson lower bound.
9. **Receipt / doc.** `evaluation_policy.v1.json`;
   `skillranker-corpus-measured-20260919.md`;
   `skillranker-process-mirror-20260919.md` (fail-open, shadow, adoption
   ≠ usefulness); Path constraint in the header of this file.

---

### 5. Wide lexical shortlist + Jev rerank

1. **Name.** Wide + rerank (skillranker process, not their corpus).
2. **Mathematical framing.** Two-stage ranker. Stage 1 (free): lexical /
   alias / embedding-free overlap produces a shortlist of size \(m\)
   (e.g. 8–20) from a wide pool. Stage 2 (paid): Choice+`__none__` or
   per-candidate Score/Noul. Metrics: coverage@\(m\) (shortlist ∩ Y
   nonempty), end-to-end top-1 precision among emissions, mean 0/1/2,
   optional nDCG@k if graded relevance exists. Rerank “tie” in this lane
   was a weighting artefact: dataset-macro +0.0009 vs per-query bootstrap
   **−0.0184, 95% CI [−0.026, −0.011]**
   (`judgment-quality-20260919.md`) — pair on the same jobs.
3. **Jev question shape.** Wide: **Choice** over candidate job ids +
   `__none__` (or skip Jev on wide if the roster is huge — skillranker
   uses Quill/254; we should not copy that stack
   (`skillranker-process-mirror-20260919.md` “Steps we will NOT copy”)).
   Rerank: **Score** with a frozen legend
   `{0: no must-have overlap, 1: some, 2: all must-haves evidenced}`
   and/or per-id `fits::<id>` **Noul**. Local eligibility after scores:
   ties against `__none__` abstain.
4. **Required labels / data.** For each historical search session (or
   reconstructed “jobs considered that week”): acceptable-apply set Y.
   If you only have the 28 *applied* jobs and no rejected-consideration
   set, **Y is one-class and `auc` must throw** (`requireBoth`). You
   then need labelled non-applies or you do not have a ranking problem.
5. **Cheap baseline to beat.** BM25 / keyword overlap ranking. First-hit.
   Always-abstain on the rerank Choice.
6. **Required negative control.** Always-abstain. Random permutation of
   the shortlist (coin-flip rank). Planted overflow: gold at rank 4 of 5.
7. **Success criterion.** Coverage@\(m\) ≥ keyword coverage@\(m\).
   Paired per-query comparison (bootstrap or exact McNemar on
   top-1-correct) beats keyword. Mean 0/1/2 < always-abstain. Asking
   strategy dominates model: freeze the question; do not tune criteria
   after seeing the 28 (criteria inversion: structured criteria
   **−1.56 pp**, McNemar p = 1.36×10⁻⁹ on Ling-Spam —
   `criteria-inversion-20260918.md`).
8. **Failure / reopen.** One-class labels. Jev ≈ drop-everything /
   random rank (`auc().constant` or value ≈ 0.5 flagged). Keyword nDCG
   ≥ Jev on the paired bootstrap. Reopen with a real considered-set
   (applied ∪ rejected ∪ never-opened) labelled independently.
9. **Receipt / doc.** `skillranker-process-mirror-20260919.md`;
   `judgment-quality-20260919.md` (rerank weighting artefact;
   asking-strategy spread nDCG 0.580 → 0.692); R42 (do not re-score
   their corpus and call it ours).

---

### 6. Prevalence-conditioned apply threshold

1. **Name.** \(t^\star(\pi)\) from historical callback/interview rate.
2. **Mathematical framing.** Do not ship 0.5. Compute \(\pi\) from the
   *same* label rule as idea 4, then
   \(t^\star = L_{\text{FP}}(1-\pi)/(L_{\text{FP}}(1-\pi)+L_{\text{FN}}\pi)\).
   Declare \((L_{\text{FP}}, L_{\text{FN}})\) **before** looking at
   scores (`prevalence_threshold.py` SIGNED triples). At \(\pi=0.5\),
   \(t^\star = L_{\text{FP}}/(L_{\text{FP}}+L_{\text{FN}})\). At equal
   loss, \(t^\star = 1-\pi\).
3. **Jev question shape.** Whatever Score/Noul emits \(p\); the
   *threshold* is ours. Noul has no `.confidence` — do not invent one.
4. **Required labels / data.** The 28 outcomes under the frozen rule,
   plus an explicit statement whether \(\pi_{\text{sample}}\) is the
   population of *future* jobs (it almost certainly is not: you applied
   to a selected 28). If the population of scraped JDs has a different
   \(\pi\), write PREVALENCE-UNKNOWN for deployment.
5. **Cheap baseline to beat.** Fixed 0.5 cut. Always-abstain (which is
   \(t=1\)). The keyword rule of idea 4.
6. **Required negative control.** \(\pi=0\) must refuse
   (`prevalence_threshold.py` planted). A shipped 0.80 cut at
   foreman-like \(\pi\) implies absurd \(L_{\text{FN}}/L_{\text{FP}}\);
   print the implied ratio and reject if it is not in the signed set.
7. **Success criterion.** The chosen \(t\) is the Bayes cut of a
   **pre-declared** loss pair at the **measured** \(\pi\). Threshold
   sweep (as in `foundation/CALIBRATION.md`) reports accuracy and
   coverage at 0.25/0.5/0.75/0.8/0.9. Ship only if, at \(t^\star\),
   mean decision loss < always-abstain. At n=28 the sweep is
   descriptive; per-bin Wilson CIs will be huge.
8. **Failure / reopen.** Using 0.5 “because that’s what the docs use.”
   Inventing a population \(\pi\) for jobs not in the 28. Reopen when
   a larger, less selected job stream exists (scraped inbox, not
   already-applied).
9. **Receipt / doc.** `work/oracle-kit/prevalence_threshold.py`;
   `prevalence-retrofit-20260919.md`; `foundation/CALIBRATION.md`
   (t≥0.75 → acc 1.0 at 95% coverage *on easy items*);
   `judgment-quality-20260919.md` (code-vuln ECE 0.19; 0.5–0.6 band
   only 38% positive).

---

### 7. VOI of paid Jev vs free keyword overlap

1. **Name.** Value of information (call Jev only if it can beat \(a_0\)).
2. **Mathematical framing.** Declare before printing
   (`voi_harm_rule.py`): \(L_{\text{miss}}\), \(L_{\text{FP}}\),
   \(c_{\text{call}}\).
   \(\mathrm{VOI}(Z) = \mathbb{E}[L|a_0] - \mathbb{E}[L|a(Z)]\).
   If \(a(Z)\) does not beat \(a_0\), \(\mathrm{VOI} \le -c_{\text{call}} \le 0\).
   Two policies: Jev-always, and keyword-then-Jev-on-keyword-allow
   (the harm-rule finding: regex already 12/12, so Jev never saw a
   remaining miss; VOI of the cascade ≤ 0).
3. **Jev question shape.** Any of ideas 1–4; VOI is about *whether to
   spend the call*, not a new primitive. State must include the
   keyword decision so a later analyst can split “Jev overturned
   keyword” vs “Jev agreed.”
4. **Required labels / data.** Same labels as the underlying idea,
   plus a frozen keyword/alias decision per row, plus a call-cost in
   the same units as \(L\).
5. **Cheap baseline to beat.** The free keyword / alias / years parser.
   That *is* \(a_0\).
6. **Required negative control.** A cascade that never overturns
   keyword must report VOI ≤ 0 (plant this). Do not mix FP
   denominators (R34 / the VOI script’s NO-CLAIM: 38 vs 40).
7. **Success criterion.** \(\mathrm{VOI} > 0\) after \(c_{\text{call}}\)
   on the residual keyword-allow set. If VOI ≤ 0, the honest result is
   **cost-benefit kill**: keep the measurement, drop the paid call
   (`math-and-next-level-20260919.md` §1.5). That is a success of the
   *method*.
8. **Failure / reopen.** Reporting 11/12 recall as a win when the
   regex was 12/12. Mixing denominators. Reopen if a residual class
   appears where keyword FNR is high and Jev TPR on that class is
   high at acceptable FPR.
9. **Receipt / doc.** `work/oracle-kit/voi_harm_rule.py`;
   `RULING-authored-vs-real-20260919.md` second axis (five surfaces,
   cheap thing won); `math-and-next-level-20260919.md` §1.5.

---

### 8. Calibration of “fit” Score vs delayed outcomes

1. **Name.** Fit-score calibration (Brier / ECE), not accuracy theatre.
2. **Mathematical framing.** Brier
   \(\frac{1}{n}\sum (p_i-y_i)^2\) is a proper score (calibration +
   refinement). ECE is reported *alongside* accuracy, never instead.
   Skillranker names `fit_brier` and does not run it
   (`math-and-next-level-20260919.md` §1.3) — we should actually run
   it. Constant \(p\) ⇒ `auc().constant`. One-class \(y\) ⇒ throw.
3. **Jev question shape.** **Score** with a frozen 3-level legend
   (e.g. 0 = no evidenced must-have, 1 = partial, 2 = all evidenced).
   Read `.score` as an expected value, **not** an index
   (`SDK-SURFACE.md`). Map to a probability via
   \(\hat p = \mathrm{score}/2\) *only if that map is declared in
   advance*. Better: use a Noul “all must-haves evidenced” as the
   probability to calibrate.
4. **Required labels / data.** Delayed \(y\): interview / screen /
   offer, with the confounder written on every row (week of apply,
   source, referral). n=28 ⇒ 10-bin ECE is mostly empty bins — use
   3–4 bins or report Brier only. Both classes required.
5. **Cheap baseline to beat.** Constant \(\hat p = \pi\) (the best
   constant; Brier = \(\pi(1-\pi)\)). Keyword-implied probability
   (1 if all aliases hit, else 0).
6. **Required negative control.** Constant-score plant flagged.
   Authored “easy” calibration (foundation ECE 0.061) is **not** a
   transfer proof (`CALIBRATION.md` limits).
7. **Success criterion.** Brier < \(\pi(1-\pi)\) (beats the best
   constant). ECE reported with bin counts. Thresholds taken from
   *these* labels, not from 0.75 on the foundation fixture. Coverage
   at the Bayes \(t^\star\) stated.
8. **Failure / reopen.** ECE cited without bin counts. 0.5 cut
   shipped because foundation t=0.75 looked good on spam items.
   Reopen with n≥50 outcomes and a conformal / e-process wrapper
   (`math-and-next-level-20260919.md` §2.5: we copied the e-process
   update and do not yet gate on it).
9. **Receipt / doc.** `foundation/CALIBRATION.md`;
   `foundation/runs/20260917T224444Z.json`; `oracle-kit` `ece`/`auc`;
   `judgment-quality-20260919.md` (calibration is the recurring
   weakness).

---

### 9. McNemar paired comparison on the same 28

1. **Name.** Exact McNemar: Jev vs keyword vs always-abstain, same rows.
2. **Mathematical framing.** Two classifiers, same cases. Let \(b\) =
   Jev right / other wrong, \(c\) = Jev wrong / other right. Exact
   McNemar (binomial mid-p or exact) on \(b+c\). Aggregates without
   pairing are how this lane almost published a rerank “tie”
   (`judgment-quality-20260919.md`;
   `jev-benchmark-pairing-20260918.md`: two versions never disagreed
   — McNemar has nothing to test). Spam: Jev 0.9833 vs TF-IDF 0.9839,
   466 disagreements, **p = 0.677** (statistical tie against ~14,800
   labels).
3. **Jev question shape.** Whatever idea 3 or 4 emits; McNemar is the
   *comparison*, not a new question. Freeze both policies before the
   first call.
4. **Required labels / data.** The same 28 (or the same (app,
   requirement) cells) labelled once. Discordant-pair count reported
   even when p is large.
5. **Cheap baseline to beat.** Keyword. Always-abstain (as a
   classifier: always predict “no apply”).
6. **Required negative control.** Two identical policies ⇒ \(b=c=0\),
   refuse to report a p-value (`jev-benchmark-pairing-20260918.md`).
   Authored vs real: do not McNemar Jev-against-itself on vignettes.
7. **Success criterion.** To *claim* Jev beats keyword: exact p < 0.05
   **and** \(\bar L\) also lower (loss, not just accuracy). At n=28
   this bar will usually **not** be met even if Jev is slightly
   better — then the result is `NOT SEPARABLE`, which is a real
   outcome (RULE 13: `jev-benchmark` n=60 models “not separable”).
8. **Failure / reopen.** Publishing two accuracies without the
   contingency table. Reopen when discordant pairs ≥ ~20 or n grows.
9. **Receipt / doc.** `judgment-quality-20260919.md`;
   `criteria-inversion-20260918.md`;
   `jev-benchmark-pairing-20260918.md`; README RULE 13.

---

### 10. Cross-document contradiction Noul

1. **Name.** Contradiction (resume vs ledger vs JD vs older resume).
2. **Mathematical framing.** Binary condition, high-value because a
   true contradiction is rare and costly (needless invention / date
   clash). Prevalence of *true* contradictions among sentence pairs
   will be low — state it. At low \(\pi\), even a strong separator
   nags (foreman 1:2300). Prefer precision-at-emission + abstain.
3. **Jev question shape.** **Noul:** “These two excerpts assert
   incompatible facts (dates, titles, counts, employers).” State =
   `{excerpt_a, excerpt_b}` only — no “this would look bad to a
   recruiter.” Pair types: resume↔ledger, resume↔older-resume,
   resume↔JD (overclaim: resume asserts a JD requirement the ledger
   does not support — that is idea 2, do not double-count).
4. **Required labels / data.** Human labels on a sample of pairs,
   plus planted incompatibles (2022–2024 vs 2019–2020 at the same
   employer with no overlap story) and planted compatibles
   (rephrase of the same tenure).
5. **Cheap baseline to beat.** Date-interval overlap; numeric
   equality; employer-name alias. Most real contradictions that
   matter are date/count clashes a parser sees.
6. **Required negative control.** Always-“contradiction” (nag).
   Mention-vs-use: a sentence *discussing* a date bug is not a
   contradiction (`docs/RULES.md` rule 7). Always-abstain for the
   decision layer.
7. **Success criterion.** Feasibility AUC ≥ 0.80 `!constant`. On
   organic pairs, precision among emissions (noul ≥ \(t^\star\))
   beats the parser residual. If the parser residual is empty, VOI
   ≤ 0 — do not pay Jev to re-find date clashes.
8. **Failure / reopen.** Fires on ordinary compatible paraphrases
   (commit-`overstates` WEAK: 14/31 FP). Reopen only for a residual
   of *semantic* clashes the parser cannot see (title inflation
   “Staff” vs ledger “Senior”) with held-out labels.
9. **Receipt / doc.** `SKILL-KILL-LIST.md` (`overstates`,
   `describes`); `docs/RULES.md` rule 7; prevalence retrofit.

---

### 11. Composite scoring in our code (weights are not a Jev question)

1. **Name.** Composite must-have / nice-to-have / constraint score.
2. **Mathematical framing.** Official pattern: atomic questions,
   compose in code (`AGENTS.md` Pattern Catalogue; TypeSafe
   composite-scoring). Weights \(w\) are a **policy**, not a model
   output. Declare \(w\) and \(L\) first. The phishing lesson again:
   do not ask one “overall fit” Score and then pretend the weights
   were principled.
3. **Jev question shape.** Parallel **Nouls** (must-haves, constraints
   like visa/location/salary-band *if those facts are in the state*)
   plus optional **Score** on nice-to-haves with a legend. Combine:

   \[
   s = \sum_i w_i\,\mathbf{1}[\mathrm{noul}_i \ge t_i]
   \]

   with \(t_i\) from idea 6, not from vibes. Missing state ⇒ that
   term is *unknown*, not zero (`jev-review` `applicable: false`
   transfer: insufficient context must not become a fabricated
   score — `AGENTS.md` design decision 4).
4. **Required labels / data.** Per-dimension labels from idea 3.
   Outcome labels only for a *secondary* check; do not fit \(w\) on
   the same 28 you report (train/validation/final_holdout split
   rules in `evaluation_policy.v1.json:40–56`). At n=28, **do not
   fit weights**. Use equal weights or a pre-declared hierarchy
   (must-have is a hard gate; nice-to-have is a sort key).
5. **Cheap baseline to beat.** Unweighted must-have count. Lexical
   must-have count. Always-abstain if any must-have is missing.
6. **Required negative control.** Fitting \(w\) on the same 28 then
   reporting the fit as a result (same-origin / train-on-test).
   A composite that is a single hidden “overall” Score.
7. **Success criterion.** Hard-gate (any must-have missing ⇒
   abstain) mean 0/1/2 < always-apply. Nice-to-have Score ranks
   the 28 with AUC vs the frozen label, `!constant`, both classes.
   Weights unchanged after seeing scores.
8. **Failure / reopen.** Weight search after looking at outcomes.
   Unknown-as-zero. Reopen when n supports a held-out weight fit
   (skillranker would want hundreds of families; we do not pretend
   28 is that).
9. **Receipt / doc.** `AGENTS.md` (compose in code);
   `evaluation_policy.v1.json` splits; `NOTE-framing-leak.md`;
   `RULING-authored-vs-real-20260919.md` (decompose).

---

### 12. Overflow / missing-skill abstention (do not invent coverage)

1. **Name.** Coverage honesty (JD asks for a skill the ledger does not
   have).
2. **Mathematical framing.** Skillranker `overflow_retrieval` +
   `loaded_reference_empty_y`: when the roster cannot satisfy the
   request, correct action is abstain (loss 0 on empty Y), not a
   nearest-neighbor skill (loss 2). Live Jev on their corpus: both
   misses were **false abstentions**, never wrong picks — the cheap
   error. For resumes, inventing “I have used Kubernetes” from a
   ledger that never says so is the expensive error.
3. **Jev question shape.** **Choice** `{covered, __none__}` or Noul
   “the ledger contains evidence of this JD skill.” State = the
   skill + ledger rows only. If the JD skill is not in a frozen
   alias table, `__none__` / uncovered — do not ask Jev to invent
   an alias.
4. **Required labels / data.** Per (JD skill, ledger) pair: covered
   / not. Overflow plants: gold buried; and true-empty (skill
   absent). Explicit-name hits resolved **locally** (skillranker
   step 3: no provider call for exact alias).
5. **Cheap baseline to beat.** Alias-table membership. Exact name
   match. That baseline should get all explicit requests; Jev is
   only for paraphrase residual.
6. **Required negative control.** Always-“covered” (invent).
   Always-abstain. A loaded-reference plant: the skill appears in
   the JD’s *nice-to-have blog link*, not as a requirement — Y
   empty if we are scoring must-haves.
7. **Success criterion.** Zero loss-2 inventions on true-empty
   (descriptive at small n; one-sided 95% upper on 0/k is
   \(1-0.05^{1/k}\); 0/28 ≈ 10.1%, which **fails** a 5% needless
   bar — say so). Mean loss < always-“covered.”
8. **Failure / reopen.** Any invented coverage that would have
   shipped on a resume. Reopen with a paraphrase residual the
   alias table cannot see, table frozen first.
9. **Receipt / doc.** `skillranker-corpus-measured-20260919.md`
   (overflow + operational_failure both abstained); process
   mirror eligibility (`not-above-none` ⇒ abstain);
   `evaluation_policy.v1.json` zero-of-n formula.

---

### 13. Feasibility-arm planted jobs (harness-blindness test)

1. **Name.** Feasibility arm before any jobhunt verdict.
2. **Mathematical framing.** `oracle-kit` `feasibility()`: an arm
   that *ought* to pass must clear AUC ≥ 0.8 and `!constant`, else
   the instrument is broken and **no verdict issues**. Compaction’s
   keep_p null was believable *because* the positive control was
   0.941 (`math-and-next-level-20260919.md` §2.4). A job-match
   suite with only hard near-misses and no obvious pair cannot tell
   a dead client from a real null.
3. **Jev question shape.** Same questions as the idea under test,
   on two plants: (P) JD that copies the resume’s headline skills
   verbatim + ledger rows that match; (N) JD for a disjoint
   occupation (e.g. commercial diving) with no overlapping ledger
   rows. Both plants committed **before** the first call
   (`docs/RULES.md` rule 3: commit the falsifier first).
4. **Required labels / data.** The two plants, plus at least one
   near-miss so a constant “apply” cannot sneak through. Labels
   obvious by construction; this arm is **not** evidence about
   real jobs (skillranker `diagnostic_synthetic` cannot promote).
5. **Cheap baseline to beat.** Keyword will also pass this arm.
   That is fine — the arm proves the *harness*, not Jev-over-keyword.
6. **Required negative control.** Shuffle labels on the plants →
   must fail the bar. Constant scores → `constant=true`, refuse.
   One-class plants → throw.
7. **Success criterion.** `feasibility.ok === true` on the planted
   pair. Until that is true, every other idea in this file is
   `PREPARED-NOT-MEASURED`.
8. **Failure / reopen.** Using the plants as the promotion
   corpus (R28). Reopen the *harness* if the client, field names,
   or question keys change.
9. **Receipt / doc.** `work/oracle-kit/index.mjs` `feasibility`;
   `work/oracle-kit/test.mjs`; `docs/RULES.md` rules 3 and 6;
   `evaluation_policy.v1.json` `diagnostic_synthetic`.

---

### 14. Cover-letter / resume-edit fact gate

1. **Name.** Emission gate for drafted sentences (confidence-gated
   keep/drop).
2. **Mathematical framing.** Compaction transfer: drop only when
   safe; unknown ⇒ keep the *draft off the page* here, because the
   safe side of a *published claim* is the opposite of compaction’s
   keep. Name the safe side in the test name (`AGENTS.md` testing
   policy). Loss: emitting an unsupported sentence = 2; withholding
   a supported one = 1; correct emit/withhold = 0. Always-withhold
   mean loss \(= \pi_{\text{supported}}\).
3. **Jev question shape.** **Choice** `{emit, __none__}` over each
   drafted sentence, state = `{sentence, supporting_ledger_rows[]}`.
   Optional Noul “supported” for calibration. No second gate.
4. **Required labels / data.** Per drafted sentence: supported /
   unsupported from the ledger (idea 1). Include planted
   invented sentences (idea 2).
5. **Cheap baseline to beat.** Emit iff lexical citation succeeds.
   Always-withhold.
6. **Required negative control.** Always-emit. Always-withhold.
   `emissionOnlyLoss` plant (withhold costs 0 ⇒ silence wins).
7. **Success criterion.** Mean 0/1/2 < always-withhold **and** <
   always-emit **and** ≤ lexical, with zero loss-2 on planted
   inventions. Near-threshold count reported (`docs/RULES.md`
   rule 4): if most noul sit in ±0.10 of \(t\), the threshold
   decided, not the model.
8. **Failure / reopen.** Safe-side inverted (emitting when
   unknown). Framing in the criterion (“since this will impress
   them”). Reopen after a real draft batch not written by the
   question author.
9. **Receipt / doc.** `AGENTS.md` fail-safe / name the safe side;
   `NOTE-framing-leak.md`; `docs/RULES.md` rule 4;
   compaction keep/drop polarity contrast
   (`RULING-authored-vs-real-20260919.md`: keep-everything 7×
   better — polarity is domain-specific).

---

### 15. Anytime-valid e-process on sequential apply decisions

1. **Name.** Sequential honesty (optional stopping on a live job
   stream, later).
2. **Mathematical framing.** \(e_t = e_{t-1}\cdot\max(10^{-15},
   1+\lambda(x_t-p_0))\), reject \(H_0:\) “no better than \(p_0\)”
   if \(e \ge 1/\alpha\). Type I controlled under optional
   stopping (Ville). Kit defaults \(\lambda=0.5\), \(p_0=0.5\),
   \(\alpha=0.05\) ⇒ reject at 20. Self-test: 8 unanimous
   observations do **not** reject; 40 do
   (`work/oracle-kit/test.mjs`). This is how you *keep looking*
   at incoming applications without p-hacking a growing n.
3. **Jev question shape.** Any binary correct/incorrect from
   ideas 3–4, one bit \(x_t\) per scored application as labels
   arrive. Not a Jev question of its own.
4. **Required labels / data.** A time-ordered stream of labelled
   decisions. n=28 historical can *start* the product (\(e_{28}\)
   under a pre-declared \(p_0\)), but 28 ones do not reject
   \(p_0=0.5\) at these defaults — do not “look significant.”
5. **Cheap baseline to beat.** Fixed-n McNemar without optional
   stopping (invalid if you peeked). Best constant \(p_0=\pi\).
6. **Required negative control.** 8 planted successes must not
   reject. Shuffled labels should rarely reject (Type I).
7. **Success criterion.** Pre-declare \(p_0\) (e.g. keyword
   accuracy, or 0.5). Report \(e_t\) and `reject` after the
   historical 28 **and** after each future labelled apply.
   A reject is evidence against “no better than \(p_0\).”
   Absence of reject is **not** a ship.
8. **Failure / reopen.** Peeking at a running t-test and
   stopping when p<0.05. Reopen when the stream exists
   (applies currently paused).
9. **Receipt / doc.** `work/oracle-kit/index.mjs` `eProcess`;
   `math-and-next-level-20260919.md` §2.5; `docs/RULES.md`
   rule 3 (falsifier first).

---

## Do NOT do

Honesty norms already earned in this repo. Doing any of these makes
the pilot the same-origin inflator R28 already killed three times
in one day.

| Don’t | Why, with a receipt |
|---|---|
| **Vibes / monolithic “job fit” Score** | Phishing verdict 63.8% vs sub-question AUROC 0.96; regex +27 pp (McNemar p=1.5e-8). `judgment-quality-20260919.md`, `RULING-authored-vs-real-20260919.md`. |
| **Same-origin confirmation** | Jev shown your summary reads it back; framing leak flipped `router_pays` 0.21→0.59. `README.md` “Agreement from a model shown your own summary is same-origin and counts once”; `NOTE-framing-leak.md`. |
| **Single-run verdicts** | Same question 0.21 / 0.26 / 0.36 across three states. A/B harness refuses relative verdicts below ten zero-spread samples. `README.md`; `compaction/ab/verdict.ts`. |
| **Authored vignettes as holdout** | Tool-call 0/20 FP → 3/20; foreman AUC 1.000 → 0.750. R28. `diagnostic_synthetic` cannot promote. |
| **Always-abstain-free loss** | `emissionOnlyLoss` ⇒ silence wins. Skillranker rationale quoted in `evaluation_policy.v1.json:70–71`. |
| **Invented second Noul on a Choice** | `helpful≥0.5` moved mean loss 0.750→0.167 by forcing 11/12 abstentions. `refuseInventedNoulGate`. |
| **AUC without prevalence** | 0.750 at \(\pi=0.016\%\) ⇒ ~1:2300. `prevalence-retrofit-20260919.md`. |
| **Guessed SDK fields** | `.distribution` / `.probability` ⇒ constant 0.500 wearing a null’s face. `SDK-SURFACE.md`. |
| **Criteria / question tuned on the scored set** | Structured criteria −1.56 pp (McNemar p=1.36e-9). `criteria-inversion-20260918.md`. `jev-spam-eval` already warned its headline was written after reading 1,000 mistakes. |
| **Empty scan set as a pass** | A hook / join that saw zero rows did not pass. `AGENTS.md`; `work/jev-eval-honesty/NEGATIVES.md` zero-hit refusal. |
| **Keyword-expressible harm asked as Jev** | Five surfaces, cheap baseline won. Write the regex/alias table first. `RULING` second axis. |
| **Promote at n=28** | Skillranker contract: 300 families, Wilson lower ≥0.80. 0/28 needless-suggestion upper ≈ 10%, not 5%. This memo’s apply-gate is a kill test. |
| **Unlabelled “it looked right”** | `gradeQuestion` DEGENERATE / WEAK / DISCRIMINATES against own constant. `SKILL-KILL-LIST.md`. |
| **Safe-side unnamed** | Compaction: unknown ⇒ keep. Published claim: unknown ⇒ do not emit. Name it in the test name. `AGENTS.md`. |
| **Mutual grading of our own memo** | RULE 13: two panes agreeing about our artifact is one origin counted twice. An external label (ledger, later outcome) outranks this file. |

---

## Ranked top-5 for a ~28-application + claim-ledger pilot

Selection used the lane’s autonomous ranking
(`AGENTS.md` THE AUTONOMOUS LOOP), not taste:

1. ground truth exists today
2. prevalence of the positive class (higher first)
3. cost to measure (offline / lexical first)
4. decision leverage (act only if not already killed by FP)

Applies are paused, so “act” here means *emit a sentence or record an
advisory apply/abstain in a shadow ledger*, never submit an application.

| Rank | Idea | Why this is next | What n=28 + ledger actually buys | What would kill it this week |
|---:|---|---|---|---|
| **1** | **#1 Claim citation** | Ledger **is** ground truth you did not need Jev to invent. n = number of claims \(C\), often ≫ 28. Highest \(\pi\) you can measure today (many sentences *should* cite). | A labelled (sentence, row) file; lexical Jaccard already runnable at zero API; planted unsupported sentences. | Lexical join mean loss ≤ Jev (VOI ≤ 0). Constant noul. Mention-vs-use plant fires. |
| **2** | **#2 Dig-vs-invent** | Same ledger. Empty-Y cases exist by construction (draft a claim with no row). Cass/skillranker already have the loss table and the overflow plant. | Shortlists of 5 rows; BM25 vs Choice+`__none__`; cheap error should be abstain, not invention. | Any loss-2 invented resume sentence. Invented `helpful` Noul gate. |
| **3** | **#3 Atomic must-have Nouls** | Decomposes the match Path already refused as a product. Labels are (app × requirement) so n can be 28×k. Keyword alias table is the mandatory \(a_0\). | Frozen must-have extractor + alias table + present/absent labels. Feasibility plants. McNemar vs keyword on cells. | Constant yes. Keyword wins the residual. Requirements extracted by Jev (circular). |
| **4** | **#7 + #5 VOI / wide+rerank** | Decides whether a paid call is *worth making* on this corpus. Five surfaces in this repo already died here. Needs a considered-set; if you only have 28 applies, `requireBoth` throws and that is the finding. | Keyword rank of whatever pool you actually had; Jev only on the shortlist; VOI after \(c_{\text{call}}\). | One-class labels. VOI ≤ 0. `auc().constant`. |
| **5** | **#4 Apply-gate 0/1/2** | Path’s own question, run as a **kill test**. Always-abstain identity is \(n_{\text{pos}}/28\). Shadow / fail-open only. `promoted: false` even if it wins. | Frozen label rule (prefer #3 coverage, not “we applied”). Always-abstain + keyword + coin-flip. Idea 13 first. | Lose to always-abstain or keyword. Using the 28 as promotion. Authored “great fit” vignettes. |

**Ideas 6, 8, 9, 15 are instrumentation** — run them *on* the top-5,
do not treat them as separate products. Ideas 10, 12, 14 are
second-wave once citation and invention are scored. Idea 11
(composite weights) waits until idea 3 has per-dimension labels
and still must not fit weights on the same 28.

**Pilot acceptance shape (all five share this):**

- Positive observable: mean 0/1/2 < always-abstain, feasibility
  `ok`, residual vs lexical reported.
- Planted negative: unsupported / disjoint-occupation / empty-Y /
  mention-vs-use / `emissionOnlyLoss` table.
- NO-CLAIM: n≈28 cannot promote a deep job-match product; delayed
  interview labels are confounded; this memo is not a measurement.

**Handoff (next concrete lever, not a plan to make a plan):**
export the claim ledger to a jsonl of `{claim_id, sentence, ledger_row_ids,
y_supported}` and run the **zero-API lexical Jaccard** plus the
always-abstain identity. That number is \(a_0\). Only then is a
budgeted Jev citation pass (idea 1) licensed. Deep match stays
unwired until that residual exists and always-abstain does not win.

---

## Pointer index (receipts this memo leaned on)

| Path | What it contributed |
|---|---|
| `work/oracle-kit/index.mjs` | AUC, ECE, e-process, `decisionLoss`, `emissionOnlyLoss`, `feasibility`, SDK field lock |
| `work/oracle-kit/prevalence_threshold.py` | \(t^\star(\pi)\), 1:2300 identity, planted \(\pi=0\) refuse |
| `work/oracle-kit/voi_harm_rule.py` | VOI ≤ 0 vs free regex on frozen harm-rule |
| `work/skillranker-eval/contract/evaluation_policy.v1.json` | 0/1/2, always-abstain required, splits, n=300 promotion (do not copy the n; copy the refusal) |
| `docs/demos/upstream-repro/skillranker-corpus-measured-20260919.md` | Live 0.167 vs 0.833; cheap errors; invented noul gate |
| `docs/demos/upstream-repro/skillranker-process-mirror-20260919.md` | Wide+rerank+`__none__`+eligibility; fail-open |
| `docs/demos/upstream-repro/RULING-authored-vs-real-20260919.md` | Authored collapse; prevalence; cheap baselines win 5/5 |
| `docs/demos/upstream-repro/judgment-quality-20260919.md` | McNemar tie vs TF-IDF; decompose; calibration weakness; rerank artefact |
| `docs/demos/upstream-repro/math-and-next-level-20260919.md` | Decision contract, e-process, capability vs cost-benefit kill |
| `docs/demos/upstream-repro/prevalence-retrofit-20260919.md` | No verdict inverted; UNKNOWN flagged |
| `docs/demos/upstream-repro/criteria-inversion-20260918.md` | Elaboration can lose; exact McNemar |
| `docs/demos/upstream-repro/jev-task-tests-cass-20260920.md` | Dig-vs-invent, overflow, empty-success |
| `docs/demos/upstream-repro/jev-benchmark-pairing-20260918.md` | Pair or do not McNemar |
| `foundation/CALIBRATION.md` + `runs/20260917T224444Z.json` | ECE 0.061 / Brier 0.020 on *easy* items |
| `docs/demos/SDK-SURFACE.md` | `.noul` / `.probabilities` / `.score` expected value |
| `docs/demos/jev-probe/NOTE-framing-leak.md` | Same-origin / implication-tracking |
| `work/jev-question-writing/SKILL-{SHORT,PURPOSE,KILL-LIST}.md` | One judgment; kind picker; dead forms |
| `docs/RULES.md` | Ceiling, paired retention, falsifier-first, near-threshold, mention-vs-use |
| `NEGATIVE_EVIDENCE.md` R28 | Authored corpora inflate |
| `README.md` | Same-origin, single-run, `__none__`, latency honesty |
| `AGENTS.md` | Claim discipline, offline/live split, compose in code, Path/mission |

**Boundary of this memo:** no Jev API call, no resume bytes committed, no
apply submitted, no threshold fitted, no promotion. If a later pane
scores these ideas, append a receipt — do not edit the numbered success
bars after seeing scores.
