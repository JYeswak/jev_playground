# Advanced techniques for typed LLM classifiers (Jev / Clef): a literature map ranked against our data

Research date: 2026-10-03. Repo `/Users/josh/Developer/jev` was read only. No live Jev or Clef calls, no installs, no repo writes.

**Conventions**
- `[Sn]` points to the numbered source list in §6. Every source in §6 was fetched in this session: the arXiv abstract through the arXiv API (`export.arxiv.org/api/query?id_list=…`), and full text (arXiv PDF through `pdftotext`, ar5iv HTML, or the publisher page) where the table needs more than the abstract.
- Repo citations are `file:line`. **BJ** = `.beads/issues.jsonl`. **NE** = `NEGATIVE_EVIDENCE.md`.
- `[DERIVED]` = my arithmetic on cited numbers, or a $0 recomputation on committed rows done in this session's Python kernel. Nothing was written to the repo, and no non-author has verified these numbers yet. §5 gives the code.
- `[INFERENCE]` = my judgement. `UNVERIFIED` = not checked.
- **Score** = G × F / C, where:
  - G = expected gain on our surfaces, 0–5.
  - F = feasibility on data we already hold, 1–5.
  - C = cost: 1 = keyless replay under an hour; 2 = keyless, but new code or a few labels; 3 = live calls or a labelling campaign; 4 = training a model; 5 = new infrastructure.
  - The ratings are `[INFERENCE]`. Each one is anchored to the cited evidence in its row.

---

## 1. Seven $0 recomputations from this session that change priorities

All of these are exploratory and were not preregistered. They read only committed rows. §5 has the code.

| # | Finding | Numbers `[DERIVED]` | Files read | What it changes |
|---|---|---|---|---|
| R1 | **The Clef-vs-Jev calibration "win" came from treating the arms differently.** `BAR-b77-platt.md` Platt-mapped Clef on 200 dev rows and compared it against *raw* Jev (`work/local-decision-arms/BAR-b77-platt.md:8-12`; `run.py:148,194`). Here the same `platt()` procedure (`run.py:161-195`) was applied to Jev's own answers on the same DEV indices (`run.py:26`) | **Banking77:**<br>• Jev ECE 0.1017 → **0.0276** after Platt; Clef+Platt is 0.0246.<br>• Jev runs 2 and 3: 0.1059 → 0.0423 and 0.1041 → 0.0469.<br>• The accuracy gap is real: Clef-only right 107 vs Jev-only right 2 discordant, exact McNemar p = 1.9e-29.<br>**Vendored code (same `vendor.py:145-185` procedure on `vendor-rows.jsonl` dev 120 / held 200):**<br>• Jev ECE 0.185 → **0.072**, vs Clef+Platt 0.083.<br>• AUC 0.839 vs 0.827. Paired bootstrap of the difference: +0.011, 95% CI [−0.044, +0.065] | `work/choice-banking77/rows-full-jev*.jsonl`, `work/local-decision-arms/rows-clefflash*.jsonl`, `work/vendor-paste/vendor-rows.jsonl`, `work/vendor-paste/sample.json` | The Banking77 accuracy win holds. The calibration win does not. "Clef beats Jev on vendored code (AUC .839 vs .827)" is not supported: the CI contains 0. Every BAR should give every arm the same recalibration (row A1) |
| R2 | **Split-conformal sets (LAC) on Jev's Banking77 probability vectors** (50 random 1,540/1,540 splits) | • α=0.10: coverage 0.903, mean set size 1.67. 58.5% of sets are singletons, and those are right 94.9% of the time.<br>• Worst class covered 0.152; 10th-percentile class 0.752.<br>• α=0.05: every set is all 77 labels, because the truth gets exactly 0 probability on 181/3,080 rows (NE:3646-3647).<br>• Jev outputs have 101 distinct probability values (two-decimal rounding) | `work/choice-banking77/rows-full-jev.jsonl` | Close to the coverage of the refuted top-3 list (0.903 vs 0.910, NE:3645), but with a mean set size of 1.67 instead of 3, plus a 58% auto-route lane. A 95% bar can never be met from Jev probabilities alone. The guarantee is marginal only, so per-class coverage must be reported (rows B1–B3) |
| R3 | **Label-free accuracy estimation (one-coin Dawid–Skene) on four arms over the same 600 Banking77 rows gets the ranking backwards** | **Estimated vs true accuracy:**<br>• Jev 0.924 vs 0.787<br>• Haiku 0.850 vs 0.722<br>• Clef 0.872 vs **0.962**<br>• Kev4b 0.847 vs 0.810<br>**Error correlation, P(both wrong) vs the independence product:**<br>• Jev–Haiku 0.182 vs 0.059<br>• Jev–Kev 0.118 vs 0.041<br>**Aggregates:** DS-aggregated labels 0.843; majority vote 0.837; best single arm 0.962 | same plus `rows-full-haiku-prompted.jsonl`, `rows-kev4b.jsonl` | Agreement-based accuracy, juries and DS label models are unsafe on our arms (rows D1, D2, G5). This replicates [S31]: DS put GPT-5.2 at 90.7% vs 71.0% against human gold, and reversed the model ranking |
| R4 | **The skill-veto drop 0.990 → 0.335 could have been projected before any organic label** | **D9 rates:** veto-on-UNFIT 199/240 = 0.829; veto-on-FIT 2/10 = 0.20 (EVAL.md:3468).<br>**Projected precision at organic prevalence 58/200 = 0.29:**<br>• 0.629 with D9 rates<br>• **0.399** with veto-on-FIT at its Wilson upper bound 0.510 (n=10)<br>• Observed: 0.335 (EVAL.md:3550)<br>**Label-free alarm:** the organic veto rate (0.790) almost equals D9's (0.804), although D9 was 96% UNFIT. BBSE inversion gives π̂(UNFIT) = 0.938 against a blind truth of 0.29.<br>KS test on the Noul scores, D9 vs organic: D = 0.181, p ≈ 0.001 | `work/skills-breadth/receipt.jsonl`, `work/wbel/replay-rows.jsonl`, `work/wbel/replay-labels.json` | Rows F1, F2 and K1 belong in `classifier ready` before any enforcement replay. D9 certified a false-alarm rate from 10 negatives; NP needs ≥59 for α=0.05 (row K1) |
| R5 | **A same-model, same-protocol rerun can "significantly degrade"** | • Jev run2 vs run3 on all 3,080 Banking77 rows: correct→wrong 27, wrong→correct 10, **exact McNemar p = 0.0076**.<br>• run1 vs run3: 23 vs 11, p = 0.058.<br>• Label flips between runs: 1.30–1.56% | `rows-full-jev.jsonl`, `-run2`, `-run3` (`variance_full.py:1-12`: same protocol) | A judge-drift alarm must be tested against the run-to-run null, not the textbook McNemar null (row F5). This also supports checklist #13 (≥3 runs) |
| R6 | **Repeat-sampling disagreement does not predict errors beyond Jev's confidence** | Error-detection AUROC on Banking77: 1−confidence 0.843; three-run disagreement 0.525. Disagreement fires on 2.1% of rows | same | Self-consistency is demoted for Jev (row G3) |
| R7 | **A BM25-margin cascade for the dominant cost surface (FiQA proxy)** | • Jev on everything: top-1 0.762.<br>• Jev on the 80% lowest-margin queries: 0.728.<br>• Jev on 50%: 0.628.<br>• BM25 alone: 0.393.<br>• BM25 margin predicts BM25 correctness with AUC 0.719 | `work/rerank-scifact/candidates-fiqa-fits.jsonl`, `rows-fiqa-mkex-jev.jsonl` | Lexical-confidence deferral is not free on the proxy: −3.4 pp for −20% calls (rows H1, H2) |

Two counts from the same session are used below:
- **Label-error candidates:** 9 of 600 Banking77 rows (1.5%) have all four arms agreeing against gold, for example #1722 gold `declined_transfer` vs all four `failed_transfer` `[DERIVED]`.
- **Spend:** the find surface is $6.63 of $7.00 over 7 days (94.8%). That is 32,301 calls, about 4,888 input tokens per call, $0.000205 per call. TTSR, auto-thinking and unexpected-stop are each ≤ $0.16 (`work/plan-20261004/specs/scoreboard-20261004T0230Z.txt`, summed) `[DERIVED]`.

---

## 2. Master ranking

| Rank | ID | Technique | Family / verb it upgrades | G | F | C | Score | Cheapest test (details in §3) |
|---|---|---|---|---|---|---|---|---|
| 1 | F1 | Label-shift projection + BBSE (precision at the target prevalence; π̂ from the flag rate) | `classifier ready`, watch, every enforcing family | 5 | 5 | 1 | 25 | R4 already ran it on skills; repeat on memory and gate |
| 2 | A1 | Symmetric per-task recalibration (Platt or temperature) on every arm | route, diff, verify, score, `--backend` | 4 | 5 | 1 | 20 | R1 already ran it; commit `--platt jev` legs |
| 3 | B1 | Split-conformal prediction sets (LAC) → `classify --set/--abstain` | route, rank | 4 | 5 | 1 | 20 | R2 already ran it; add per-class coverage |
| 4 | K1 | Neyman–Pearson umbrella threshold (false-alarm control from negatives alone) | gate, screen, diff, memory-drop, skill veto | 4 | 5 | 1 | 20 | 300 clean tool results → cut; planted catch rate |
| 5 | A7 | ECE estimator hygiene (equal-mass / debiased / sweep, bootstrap CI, Brier/NLL) | all scored claims | 3 | 5 | 1 | 15 | Recompute every BAR ECE with CI |
| 6 | B2 | APS / RAPS adaptive sets | route, rank | 3 | 5 | 1 | 15 | Same file as R2; compare per-class coverage |
| 7 | C1 | Risk–coverage curves, AUGRC, SGR risk-bound thresholds | route, verify, gate (abstain) | 3 | 5 | 1 | 15 | AUGRC per arm on stored rows |
| 8 | D6 | Confident learning on our gold labels | all labelled corpora | 3 | 5 | 1 | 15 | Review the 9 four-arm-vs-gold rows; jev-1lim A/B labels |
| 9 | F2 | Two-sample shift test on score distributions (BBSD / KS) | watch | 3 | 5 | 1 | 15 | R4 KS done; weekly KS on shadow logs |
| 10 | F4 | CUSUM on daily flag / drop / veto rates | watch | 3 | 5 | 1 | 15 | Retro-CUSUM on shadow logs |
| 11 | F5 | Per-sample paired degradation test on a frozen canary, against the run-to-run null | watch, `doctor` | 3 | 5 | 1 | 15 | R5 floor; permutation null from runs 1–3 |
| 12 | G1 | Chance-corrected judge validation (κ, multi-benchmark) | score / grade, watch | 3 | 5 | 1 | 15 | κ for Jev–Clef shadow and Jev–Haiku |
| 13 | A5 | Batch / contextual calibration, PriDe (remove the option prior) | route | 3 | 4 | 1 | 12 | Batch-mean divide on Banking77 Jev vectors |
| 14 | D3 | Average Thresholded Confidence (label-free accuracy under shift) | watch, `ready` | 3 | 4 | 1 | 12 | Memory m959 → 9kmq organic; skills D9 → organic |
| 15 | A2 | Beta calibration | diff, verify, screen (Noul) | 2 | 5 | 1 | 10 | Vendor dev → held NLL/ECE vs Platt |
| 16 | G4 | Verbalized vs model-native confidence comparison | `--backend llm` | 2 | 5 | 1 | 10 | Haiku confidence vs Jev on Banking77 |
| 17 | B4 | Conformal risk control (monotone loss, e.g. FNR) | gate (multi-Noul), memory | 3 | 3 | 1 | 9 | One cut over the 5 gate Nouls with planted FNR |
| 18 | A4 | Multiclass temperature / Dirichlet / invert-softmax for rounded vectors | route | 2 | 4 | 1 | 8 | Split-half NLL and classwise-ECE |
| 19 | E1 | PPI / PPI++ / AutoEval (valid CI from few labels + many predictions) | `ready`, watch, every eval | 4 | 4 | 2 | 8 | 30-label subsample of the 200 organic skill rows |
| 20 | E2 | Active inference / confidence-driven inference | labelling budget for every family | 4 | 4 | 2 | 8 | Simulated budgets on the same 200 rows |
| 21 | H1 | Confidence-deferral cascade (FrugalGPT-style) | rank, effort, gate | 2 | 4 | 1 | 8 | R7 done (negative); Clef→Jev on Banking77 |
| 22 | E5 | Guided search for positives instead of random labelling | gate, diff, screen (zero-positive surfaces) | 5 | 3 | 2 | 7.5 | Searched harmful commands, vendored hunks |
| 23 | A6 | Saerens EM / MLLS + bias-corrected calibration (re-prior without labels) | route, veto, memory | 4 | 3 | 2 | 6 | D9-calibrated Noul → organic π̂ vs 58/200 |
| 24 | B3 | Mondrian (class-conditional) / clustered conformal | route; memory and gate only with ≥⌈1/α−1⌉ per class | 3 | 2 | 1 | 6 | Banking77 at α=0.10 (9/class needed, 40 present) |
| 25 | C2 | Cascaded selective evaluation (Trust or Escalate) | route, score, verify | 4 | 3 | 2 | 6 | Clef+Platt → Jev → abstain on Banking77 dev/held |
| 26 | E3 | Stratified PPI | `ready`, watch | 3 | 4 | 2 | 6 | Memory rows stratified by source |
| 27 | E4 | Active testing / importance-sampled F-measure | gate, screen recall | 4 | 3 | 2 | 6 | Gate qunw sample reweighted by maxScore |
| 28 | G2 | Position / option-order debiasing (balanced positions, PriDe) | rank, score | 2 | 5 | 2 | 5 | Jev pick index vs BM25 rank on FiQA rows |
| 29 | B5 | Learn-then-Test (several risks at once, FWER) | skill veto, gate, memory | 3 | 3 | 2 | 4.5 | Organic skill rows 100/100: any valid cut? |
| 30 | B7 | Weighted / label-shift conformal | route under prevalence change | 3 | 3 | 2 | 4.5 | Resample Banking77 to a skewed prior |
| 31 | F3 | Sequential harmful-shift tracking (confidence sequences) | watch | 3 | 3 | 2 | 4.5 | Replay the 9kmq gate holdout in time order |
| 32 | K2 | Over-defense test set (NotInject-style benign trigger words) | screen | 3 | 3 | 2 | 4.5 | Trigger-word rows among the 300 clean |
| 33 | J1 | Logical-constraint joint decoding (weighted MaxSAT) and constraint-violation flags | ask-bundle, chain, gate | 3 | 3 | 2 | 4.5 | Negation coherence on the 40 stored msax rows |
| 34 | A3 | Isotonic / histogram binning / scaling-binning / Venn–Abers | diff, verify | 2 | 2 | 1 | 4 | Read `work/jev-science/calibration.json` first; Banking77 split halves |
| 35 | B6 | Conformal selection / Conformal Alignment (FDR-controlled keep/flag sets) | memory keep, skill veto, screen | 4 | 2 | 2 | 4 | m959 50 keeps (11 relevant) |
| 36 | H2 | Online cascade learning / neural caching (distil Jev into a local model) | rank (find), memory | 4 | 3 | 3 | 4 | TF-IDF LR on 2,480 Jev-labelled Banking77 rows |
| 37 | G3 | Self-consistency / repeat-sampling confidence | all | 1 | 4 | 1 | 4 | R6 done: AUROC 0.525 vs 0.843 |
| 38 | I1 | Instruction optimization (MIPROv2 / GEPA / OPRO / APE / contrastive reflection) | every Noul/Choice question | 3 | 3 | 3 | 3 | Wording-variance bound from stored variant runs |
| 39 | D4 | Semi-supervised multi-model evaluation (SSME) | `ready`, watch | 3 | 3 | 3 | 3 | Banking77 four arms + 20 labels |
| 40 | G6 | Criteria-drift re-label audit | score / TTSR | 2 | 3 | 2 | 3 | Blind re-label of TTSR samples |
| 41 | D5 | Weak-supervision label model (Snorkel / FlyingSquid / Alfred) | gate, extract | 2 | 2 | 2 | 2 | 5 gate Nouls as labelling functions |
| 42 | J2 | Task interference among co-asked questions | ask-bundle | 2 | 2 | 3 | 1.3 | Partial proxy: flips by era among repeated memory pairs; the true test is live |
| 43 | H3 | Learned routers (RouteLLM, Hybrid, AutoMix, cascade routing) | effort, route | 2 | 2 | 3 | 1.3 | Oracle-router bound on Banking77 four arms |
| 44 | H4 | Batch prompting (several items per call) | ask-bundle | 2 | 2 | 3 | 1.3 | Instruction share of stored input tokens |
| 45 | G5 | Panel-of-judges jury (PoLL) | score | 1 | 4 | 3 | 1.3 | Done in R3: majority 0.837 vs best 0.962 |
| 46 | C3 | Learning to defer with a trained rejector | route | 2 | 1 | 4 | 0.5 | Proxy: logistic deferral on (Jev confidence, Clef p, agreement), Banking77 DEV → held |
| 47 | A8 | Thermometer (universal LLM calibrator) | `--backend llm` | 2 | 1 | 4 | 0.5 | Cross-task Platt transfer Banking77 → CLINC150 |
| — | D1 | Dawid–Skene / agreement as an *accuracy estimate* | — | 0 | 5 | 1 | 0 | **Falsified on our arms (R3)** |
| — | D2 | Platanios agreement equations as an *accuracy estimate* | — | 0 | 4 | 1 | 0 | Needs independent errors; ours are 3× correlated (R3). The constraint-violation part survives as J1 |

---

## 3. Technique cards by area

Column key: **Quantity** = the exact number the technique computes. **Data** = what it needs (labels? how many?). **Gain** = the expected gain with its source. **Test** = the cheapest falsifiable test on data we already hold, with the file and the kill condition.

### 3A. Calibration beyond Platt

| ID | What it is | Quantity | Data | Gain (source) | Test (file) | Risk |
|---|---|---|---|---|---|---|
| A1 | Fit a monotone 1–2 parameter map (Platt `σ(a·logit p + b)`, or one temperature T for a vector) on a disjoint dev split. Apply it unchanged to held rows. Do this for **every** arm in a comparison | Calibrated p̂; held ECE / Brier / NLL | Labelled dev split; 120–200 rows was enough here | Temperature scaling is "surprisingly effective" on most datasets [S45]. Pre-trained transformers are calibrated in-domain and temperature scaling reduces error further [S59]. **Ours (R1):** Jev ECE 0.1017 → 0.0276 (Banking77) and 0.185 → 0.072 (vendored code). **Prior repo work:** `work/jev-science/calibrate.py` fitted isotonic/Platt maps on 7 Jev tasks with raw ECE 0.23–0.52, and the dev-fitted maps lowered held Brier on every task, e.g. webscreen 0.251 → 0.085 (`work/jev-science/CALIBRATION.md:3-17`) | Add a `--platt jev` leg to `work/local-decision-arms/run.py` and `vendor.py` that reads `rows-full-jev.jsonl` and `vendor-rows.jsonl`. Kill if held ECE is not below raw ECE on both sets | Under shift, post-hoc calibration "falls short" [S49]. Thresholds do not transfer across datasets (docs/LEDGER.md:212) |
| A2 | Beta calibration: `σ(a ln p − b ln(1−p) + c)`. The family contains the identity map and fits skewed score distributions | Calibrated p̂ | Same as A1; one extra parameter | Logistic calibration "can easily uncalibrate a perfectly calibrated classifier"; isotonic is "prone to overfitting on smaller datasets"; beta beats logistic on skewed scores [S46] | Vendor: fit Platt and beta on 120 dev rows, compare held NLL/ECE on 200 (`vendor-rows.jsonl`, `sample.json`). Repeat on SciFact (`work/noul-scifact/rows-jev.jsonl` + `sample.jsonl`). Kill if beta ≤ Platt on both | Overfitting at 120 rows; Noul outputs cluster at a few values |
| A3 | Non-parametric maps. Isotonic: PAV step function. Histogram / uniform-mass binning. Scaling-binning: fit a parametric map, then bin it. Venn–Abers: two isotonic fits give a calibrated interval [p0, p1] | Step-function p̂; Venn–Abers interval | Isotonic loses to Platt below about 200–1,000 calibration cases and ties or wins at ≥1,000 [S61]. Binning needs O(B/ε²) samples vs O(1/ε²+B) for scaling-binning [S48] | Scaling-binning: 35% lower calibration error than histogram binning, with a verifiable guarantee [S48]. Histogram binning has guarantees without sample splitting [S52]. Venn–Abers is calibrated under iid [S56] | Read `work/jev-science/calibration.json` first: it already holds isotonic and Platt per task (CALIBRATION.md:3-17). New test: Banking77 Jev (3,080 rows; split halves of 1,540 ≥ 1,000), isotonic vs Platt held NLL. Vendored code is too small; report the Venn–Abers interval width instead. Kill if isotonic ≥ Platt NLL | Our 101 distinct output values (R2) make B small but tie-heavy. Every dev set except Banking77 is under 1,000 |
| A4 | Multiclass temperature or Dirichlet map on log-probabilities. For rounded, verbalized-style vectors, "invert softmax" (z = log p) before scaling | Calibrated probability vector; classwise-ECE | Labelled dev split; a full probability vector (Jev Choice has one; Clef rows store only `p_choice`) | Dirichlet improves confidence-ECE, classwise-ECE, log-loss and Brier [S47]. Re-softmax of verbalized probabilities is a known failure; invert-softmax fixes it [S58] | `rows-full-jev.jsonl`, split halves. **Preview `[DERIVED]`:** fitted T ≈ 1.02, and ECE moved 0.089 → 0.057 only because of the ε=1e-3 smoothing needed for log 0. Kill if the gain disappears at ε→1e-6 | Zero-mass truths (181 rows) make log-likelihood depend on ε, so ε becomes the hidden parameter |
| A5 | Contextual / batch calibration: estimate the model's prior bias per label (content-free input, or the batch-mean prediction) and divide it out. PriDe estimates the option-ID prior by permuting options on a few samples | Debiased p̃(y\|x) ∝ p(y\|x)/p̄(y) | **No labels** (batch calibration); a few permuted calls (PriDe) | Up to 30.0% absolute accuracy for GPT-3 few-shot [S50]. Batch calibration is SOTA among calibration baselines on 10+ tasks [S51]. PriDe is label-free and transferable [S87] | Batch-mean divide on `rows-full-jev.jsonl` (Banking77 test is class-balanced); accuracy vs raw 0.801 on held halves. Kill if accuracy and NLL do not improve | It is a label-shift correction in disguise: on organic, imbalanced traffic it removes real prevalence. Our option-permute metamorphic test already found 0/40 flips (EVAL.md:3500), so option-ID bias may be small |
| A6 | Saerens EM / maximum-likelihood label shift (MLLS) with bias-corrected calibration. Re-estimates target class priors from unlabelled target predictions and re-weights posteriors | π̂_target; re-weighted p̂ | Calibrated source probabilities + unlabelled target scores | MLLS + bias-corrected calibration beats BBSL and RLLS; the objective is concave [S60] | Fit Platt on D9 Noul scores, run EM on organic `work/wbel/replay-rows.jsonl`, compare π̂(UNFIT) with the blind 58/200 (`replay-labels.json`). D9 per-row labels are needed: their location is UNVERIFIED (`work/skills-breadth/PREREG-d9.md` names the sample). Kill (= detected conditional shift) if \|π̂ − 0.29\| > 0.15 | Assumes p(x\|y) is fixed. R4 shows it was not (veto-on-FIT 0.20 → 0.739), which is exactly what the test exposes |
| A7 | Calibration-error estimation that is not biased at n = 200–600: equal-mass bins, the debiased estimator, ECE_sweep, and Kumar's estimator; always alongside Brier/NLL and a bootstrap CI | ECE with a CI | The existing scored rows | Equal-mass bins have lower bias; the debiased estimator and ECE_sweep are reliable [S55]. Plug-in ECE underestimates and needs O(B) vs O(√B) samples [S48] | Recompute every ECE in `BAR-b77-platt.md` / `BAR-vendor-platt.md` and docs/LEDGER.md:151-154 with equal-mass bins and a 1,000-sample bootstrap. Kill a calibration claim whose CI overlaps the comparator | None for correctness. Some published calibration "wins" may disappear |
| A8 | Thermometer: an auxiliary network, trained across many tasks, predicts a per-task temperature for an LLM without labels for the new task | Per-task T | Many labelled tasks plus model features | Better calibration on new tasks [S57] | No cheap test. Proxy: fit Platt on Banking77 dev, apply it to CLINC150 `work/choice-clinc150/rows-full-jev.jsonl`. Kill a cross-task-map idea if CLINC150 ECE with the Banking77 map ≥ raw | We do not own Jev internals; our rule is to refit per task (classifier-areas.md:129) |

### 3B. Conformal prediction and risk control

| ID | What it is | Quantity | Data | Gain (source) | Test (file) | Risk |
|---|---|---|---|---|---|---|
| B1 | Split conformal with score s = 1 − p̂(true). q̂ is the ⌈(n+1)(1−α)⌉/n empirical quantile of the calibration scores; the set is {y : 1 − p̂(y) ≤ q̂} | Set C(x) with P(Y∈C) ≥ 1−α (marginal) | n labelled exchangeable rows. "n = 1000 is sufficient for most purposes" [S1 §3.2]. Coverage given the calibration set ~ Beta(n+1−l, l), l = ⌊(n+1)α⌋ [S1 eq. 16] | Finite-sample marginal coverage for any model [S1]. CP uncertainty tracks LLM MCQA accuracy [S7]. Works without logits through sample frequency [S15]. Conformal abstention bounds the hallucination rate [S14]. **Ours (R2):** 0.903 coverage at mean size 1.67 vs the top-3 list's 91.0% at size 3 | `rows-full-jev.jsonl`: preregister α=0.10 and calibrate on the 2,480 non-sample rows, test on the 600 (indices from `run.py:25`). Kill if held coverage < 0.88 or mean size ≥ 3 | Marginal only: worst class 0.152 (R2). Fails under shift (exchangeability). The 94.1% ceiling from zero-mass truths |
| B2 | APS: score = cumulative sorted probability mass up to and including the true label, randomized. RAPS adds λ·(rank − k_reg)⁺ to shrink sets | Adaptive set | As B1, plus a small extra split to tune λ and k_reg | Better approximate conditional coverage than alternatives [S2]. RAPS sets are "factors of 5 to 10 smaller" than a stand-alone Platt baseline at equal coverage [S3]. APS score formula: [S1 eq. 4] | Same file as B1: compare set size and per-class coverage vs LAC at α=0.10. Kill if per-class 10th-percentile coverage does not beat LAC's 0.752 | Ties from two-decimal outputs need randomization; zero-mass classes |
| B3 | Mondrian / class-conditional conformal: a separate quantile per class, `q̂(k) = Quantile(⌈(n_k+1)(1−α)⌉/n_k)` [S1 §4.2 eq. 23-24]. Clustered CP pools classes whose score distributions are similar | Per-class coverage ≥ 1−α | **≥ ⌈1/α − 1⌉ labelled rows per class** to get a non-trivial set: 9 / 19 / 49 / 99 at α = .10 / .05 / .02 / .01 `[DERIVED]` | Clustered CP beats existing methods on class-conditional coverage and set size, up to 1,000 classes [S6] | Banking77 at α=0.10 (40 rows/class present). Memory and gate are infeasible: 9kmq had 0 relevant and 0 harmful calibration rows, and the support-gated variant abstained on 100% (`work/jev-9kmq/RESULTS.md:26-31`). Kill clustered CP if worst-class coverage < 0.80 | Vacuous sets when the rare class is thin, which is our usual case |
| B4 | Conformal risk control: `λ̂ = inf{λ : n/(n+1)·R̂_n(λ) + B/(n+1) ≤ α}` for any monotone bounded loss (FNR, false-drop share) [S4 eq. 4] | E[loss] ≤ α; tight to O(1/n) | n labelled rows; the loss must be monotone in λ | Generalizes split CP; worked FNR examples [S4] | One shared cut over the 5 gate Noul scores (`work/jev-1lim/live-results.jsonl`, labels `adjudicated.jsonl`) to keep the expected missed-harm share ≤ 0.10 on planted rows (`work/cascade-harm/planted-recall.jsonl`). Kill if λ̂ = λ_max (flag everything) | With few positives, the B/(n+1) term dominates and the result is conservative |
| B5 | Learn-then-Test: treat each candidate threshold as a hypothesis "risk(λ) > α", compute p-values, and use FWER-controlling testing to return every λ that controls *several* risks with probability 1−δ | Set of valid λ, possibly empty | n labelled rows | FDR control for multi-label tasks and simultaneous type-1 control [S5] | Organic skill veto: split `replay-rows.jsonl` + labels 100/100; LTT for precision ≥ 0.8 AND P(FIT\|allow) ≤ 0.10 at δ=0.1. Prediction `[INFERENCE]`: empty set (AUC 0.703, R4). Kill (= signal exists) if a λ survives | Low power at n=100. An empty set is the honest answer, not a bug |
| B6 | Conformal selection / Conformal Alignment: conformal p-values per unit + Benjamini–Hochberg-type threshold give a **selected subset whose false-selection proportion is ≤ q** | Selected set with FDR ≤ q | Labelled calibration units of the same population, including enough positives | Controls the proportion of falsely selected units under exchangeability [S12]. A prescribed fraction of selected units meet the criterion [S13] | Memory keeps: `work/jev-m959/labelled.json` (50 keeps: 11 relevant, 39 irrelevant; EVAL.md:3436). Report the selected-set size at q = 0.6 (keep precision ≥ 0.4). Kill if the selection is empty at q ≤ 0.6 | Empty selections at small n. Turns "keep precision 0.19" into an honest "cannot certify" |
| B7 | Weighted conformal: re-weight calibration scores by a likelihood ratio. Under label shift, w(y) = q(y)/p(y) estimated with BBSE | Coverage under the shifted distribution | Unlabelled target + an invertible confusion matrix | Label shift degrades coverage and calibration; re-weighting restores it [S11]. Covariate version [S10] | Resample `rows-full-jev.jsonl` test halves to a skewed prior (top 10 intents = 60%); compare plain vs weighted coverage. Kill if weighted coverage is not closer to 0.90 | Fixes only label shift; R4's skill drop was conditional shift |

### 3C. Selective classification and deferral

| ID | What it is | Quantity | Data | Gain (source) | Test (file) | Risk |
|---|---|---|---|---|---|---|
| C1 | Rank rows by confidence and report selective risk at every coverage (risk–coverage curve). AUGRC = area under the generalized risk–coverage curve (average risk of undetected failures). SGR picks the threshold whose selective risk ≤ r* with probability 1−δ through a binomial bound | AUGRC; threshold with certified selective risk | Labelled rows | SGR: 2% top-5 ImageNet error guaranteed with probability 99.9% at about 60% coverage [S16]. AUGRC changed metric rankings on 5 of 6 datasets [S17] | AUGRC for Jev / Clef / Kev / Haiku on Banking77 (600 shared rows) and SciFact (`work/noul-scifact/rows-*.jsonl`). SGR for 2% error on Banking77. Kill a "Jev confidence is useful" claim if Jev's AUGRC ≥ the arm with lower accuracy | A metric only; it creates no signal. Needs exchangeability |
| C2 | Cascaded selective evaluation: weak judge → stronger judge → abstain. Per-stage confidence thresholds come from fixed-sequence testing on a small calibration set, so agreement with humans ≥ 1−α is guaranteed | Coverage at guaranteed accuracy / agreement | Labelled calibration set (hundreds) | ">80% human agreement with almost 80% test coverage" with Mistral-7B as the first judge, where GPT-4 alone almost never reaches 80% [S19] | Banking77: Clef+Platt → Jev → abstain. Thresholds from `rows-clefflash-dev.jsonl` + DEV Jev rows (200) to guarantee accuracy ≥ 0.95; test on 600. Kill if held accuracy < 0.95 or coverage < 0.5 | Clef takes 3–4 s per call (README.md:132). The guarantee holds only under exchangeability |
| C3 | Learning to defer: train a classifier and a rejector jointly with a consistent cost-sensitive surrogate, using samples of the expert's decisions | Defer / predict policy | Training set with expert decisions + features | Consistent estimator; effective on several tasks [S18] | No cheap test. Proxy: logistic deferral on (Jev confidence, Clef p, agreement) using DEV 200 → held 600. Kill if not above C2 | We cannot train Jev; small data |

### 3D. Label-free accuracy and weak supervision

| ID | What it is | Quantity | Data | Gain (source) | Test (file) | Risk |
|---|---|---|---|---|---|---|
| D1 | Dawid–Skene: EM over latent true labels and per-annotator confusion matrices (spectral initialization gives optimal rates) | Per-annotator accuracy; posterior labels | No labels; ≥3 annotators | Optimal convergence up to a log factor [S21]. Bayesian DS for win rates [S32] | **Done (R3): falsified.** The ranking came out backwards (Clef 0.962 true → 0.872 estimated; Jev 0.787 → 0.924) | Correlated errors: Jev–Haiku both-wrong 0.182 vs 0.059 under independence. External replication: −19.7 pp and a rank reversal [S31] |
| D2 | Platanios: with ≥3 better-than-chance classifiers that make **independent** errors, accuracy is exactly identifiable from pairwise agreement rates. The 2017 logic version adds mutual-exclusion constraints | Error rates from agreements | No labels | Exact identification under independence [S22]. Estimates "within a few percent" of true accuracy on 4 datasets [S23] | Run the triplet equations [S22 eq. 7-8] on Jev / Clef / Kev Banking77 choices (R3 arrays). Prediction: wrong, because the errors are correlated. Kill the estimator if any estimate is off by > 0.05 | Same-family correlation (classifier-areas.md:134 already warns). Keep only the constraint-violation part (J1) |
| D3 | Average Thresholded Confidence: choose t so that the source fraction with confidence > t equals source accuracy; predicted target accuracy = target fraction with confidence > t. Agreement-on-the-line is the agreement-based relative | Predicted target accuracy, no target labels | Labelled source + unlabelled target scores | 2–4× more accurate than prior methods; but "identifying the accuracy is just as hard as identifying the optimal predictor" without assumptions [S29]. OOD agreement is linear in ID agreement [S28] | Memory: fit t on `work/jev-m959/labelled.json` scores, predict on the 9kmq organic population (`work/jev-9kmq/results.json`). Skills: D9 → organic (true organic accuracy (53+37)/200 = 0.45 `[DERIVED]`). Kill if \|predicted − true\| > 0.10 | Shift-type assumptions; a binary Noul with a 0.40 cut needs a margin-based "confidence" |
| D4 | SSME: a semi-supervised mixture model of (true label, every classifier's continuous scores), fitted on a few labels + many unlabelled rows; estimates any metric | Accuracy / ECE / subgroup metrics | A few labels + unlabelled rows + several classifiers | Error 5.1× lower than labelled-only and 2.4× lower than the next best method [S30] | Banking77 600 with four arms: 20 labelled rows + 580 unlabelled; compare SSME accuracy estimates with truth (R3 arrays). Kill if its error > the 20-label Wilson half-width | Mixture misspecification; the same correlation trap as D1 |
| D5 | Weak-supervision label model: several heuristic or LLM "labelling functions" vote; a label model (Snorkel / MeTaL / FlyingSquid closed form) estimates their accuracies without labels and trains an end model | Probabilistic labels; end classifier | No labels; ≥3 diverse sources | Snorkel comes within 3.60% of large hand-curated training sets [S24]. +6.8 points over majority vote [S25]. FlyingSquid is 170× faster [S26]. Prompted-LLM labelling functions: 19.5% error reduction vs zero-shot [S27] | The 5 gate Noul scores (`work/jev-1lim/live-results.jsonl` `scores`) as labelling functions → FlyingSquid → compare with `adjudicated.jsonl` and with the `maxScore` rule. Kill if the label model ≤ the maxScore rule | Labelling functions from one model are correlated (R3); positives are near zero |
| D6 | Confident learning: estimate the joint of given vs true labels from out-of-sample probabilities; flag likely label errors | Ranked candidate label errors; estimated noise rate | Labels + out-of-sample probabilities | Benchmark test sets average ≥3.3% label errors; 51% of algorithmically flagged candidates were real errors [S34]; method [S33] | Hand-review the 9 Banking77 rows where all four arms agree against gold (R3 arrays; e.g., #1722). Our own labels: `work/jev-1lim/labels-A.jsonl`, `labels-B.jsonl`, `disagreements.jsonl`. Kill as a fix if fewer than 3 of 9 are judged gold errors | Never relabel after scoring to pass a bar (generic rule 9); report only as a rater-noise bound |

### 3E. Label-efficient evaluation (labels are our binding cost)

| ID | What it is | Quantity | Data | Gain (source) | Test (file) | Risk |
|---|---|---|---|---|---|---|
| E1 | Prediction-powered inference: estimate on many model-scored rows, then correct the bias with a "rectifier" measured on a small labelled random sample. For a mean: θ̂ = mean f(X̃) − mean(f(X) − Y). PPI++ tunes the power so the interval is never wider than classical [S62, S63] | Valid CI for prevalence, precision or accuracy | Small **random** labelled sample + many unlabelled scored rows | Smaller intervals the better the predictor is [S62]; "always improve on classical intervals" [S63]; up to 50% more effective labelled sample size in evaluation [S68] | Organic skills: 1,000 resamples drawing n=30 labelled from the 200 (`replay-labels.json`) plus 170 unlabelled Jev verdicts (`replay-rows.jsonl`). Compare the PPI CI for UNFIT prevalence with Wilson on 30. Kill if PPI coverage < 0.93 or width ≥ Wilson | Small gain when the predictor is weak (AUC 0.703) |
| E2 | Active inference / confidence-driven inference: label rows with probability ∝ model uncertainty and inverse-probability weight them; valid CIs with fewer labels | CI at a fixed label budget | Scores for all rows; sampling probabilities logged | Same accuracy with "far fewer samples" [S64]; >25% fewer human annotations in three settings [S65] | Same 200 rows: budgets 20/40/60, sampling ∝ 1 − \|2p − 1\| with a floor of 0.05; compare CI width with uniform sampling. Kill if not narrower at every budget | Weights explode when the floor is too low; the sampling probabilities must be stored |
| E3 | Stratified PPI: run PPI inside strata (source, confidence bucket) and allocate labels across strata | Tighter CI when autorater quality varies by stratum | Stratum variable + labels per stratum | "Substantially tighter" CIs than unstratified PPI [S66] | Memory population by source (wb7j / m959 / s47b; `work/jev-9kmq/RESULTS.md:12`) × Noul bucket. Kill if not tighter than E1 | Strata with 0–3 positives |
| E4 | Active testing / active F-measure estimation: draw test rows from an instrumental distribution q(x) and use importance-weighted unbiased estimators; q is chosen to minimize variance | Unbiased precision / recall / F estimate at a fixed budget | Scores for the population; a labelling budget | Removes selection bias while reducing variance [S67]; derives the variance-optimal sampling distribution for F-measures [S69] | Gate: re-weight the qunw 453-row labelled sample by Jev `maxScore` (BJ:438) and compute the variance of a recall estimate under planted positives. Kill if variance ≥ uniform | Unbiased but high variance when q misses the rare positives |
| E5 | Guided learning: under extreme skew, have people **search** for positives (queries, logs, known-bad lists) instead of labelling random rows | Positives per labelling hour | Human search time; a source of candidates | Under extreme skew, even basic guided learning "can completely dominate" active strategies [S70]; search helps active learning with rare classes [S71] | Vendored code: positives from known third-party trees (the `work/vendor-paste/corpus.json` approach). Gate: commands that dcg blocked (log location UNVERIFIED). Kill if positives found per hour < 5 | Searched positives are not organic positives: use them for recall and threshold only, never for prevalence |

### 3F. Drift detection

| ID | What it is | Quantity | Data | Gain (source) | Test (file) | Risk |
|---|---|---|---|---|---|---|
| F1 | Black-box shift estimation: ŵ = Ĉ⁻¹ μ̂, where Ĉ is the source confusion matrix and μ̂ the target prediction rates. Binary: π̂ = (q − FPR)/(TPR − FPR). Then project precision = TPR·π / (TPR·π + FPR·(1 − π)) | Target prevalence; projected precision; inconsistency alarm | Source confusion matrix (labelled dev) + unlabelled target flag rate | Works "even when predictors are biased, inaccurate, or uncalibrated, so long as their confusion matrices are invertible"; includes a shift test [S72] | **Done for skills (R4).** Next: memory keep (m959 confusion → organic keep rate from `~/.local/state/jev/memory-filter-full.jsonl`, path from classifier-areas.md:155; UNVERIFIED that it is readable) and gate (jev-1lim → organic flag rate). Kill = π̂ outside [0, 1] or far from a 30-label PPI estimate | Assumes p(x\|y) is fixed. A violation is precisely the alarm we want |
| F2 | Two-sample tests on model outputs (BBSD: KS / MMD on classifier scores, source vs target window) | Shift p-value | Unlabelled scores from both windows | Two-sample tests on pretrained-classifier outputs performed best among detectors [S73] | **Done (R4):** KS D=0.181, p≈0.001. Weekly KS of `injection-shadow.jsonl` and `vendor-shadow.jsonl` scores vs the calibration window. Kill if it alarms on ≥ 2 of 4 known-stable weeks | Flags benign shifts too; pair it with F1 and F3 |
| F3 | Sequential tracking of a harmful risk increase: time-uniform confidence sequences on risk (accuracy, calibration), using labels as they arrive (possibly delayed). No false-alarm inflation from continuous peeking | Alarm time; CI on the risk increase | Labelled trickle over time | Detects harmful shifts and ignores benign ones; continuous monitoring without a higher false-alarm rate [S74] | Replay the 9kmq gate holdout (475 rows, time-ordered, `work/jev-9kmq/results.json`) as a stream; confidence sequence on the false-veto rate vs 2%. Kill if it alarms before the cutoff | Needs ongoing blind labels |
| F4 | CUSUM: S_t = max(0, S_{t−1} + x_t − μ0 − k); alarm at S_t > h | Alarm on a small mean shift | Daily rates; a stable reference period | More efficient than Shewhart charts for mean shifts ≤ 2σ [S75] | Retro-run on daily drop rate (memory), flag rate (injection) and the scored-row share (skill veto) over the shadow logs; k = 0.5σ, h = 4σ from the first stable week. Kill if it does not alarm on the documented skill-veto silent fail-open (rows with `reason: ask-unconfigured`, EVAL.md:3512-3514) | Traffic mix changes rates without a model change; autocorrelation |
| F5 | Per-sample paired test for model degradation on a frozen canary: McNemar on discordant rows, never aggregate accuracy. Same-name API models do change | Degradation p-value | Frozen canary inputs + stored answers | Per-sample McNemar detects degradations of 0.3% [S76]. GPT-4 accuracy on the same prime questions went 84% → 51% in 3 months [S77]. **Ours (R5):** same model, run2 vs run3, p = 0.0076 | Build the null from `rows-full-jev.jsonl` / `-run2` / `-run3` (all three pairings). The alarm rule is "discordance beyond the run-to-run envelope". `scripts/check-omp-judge-drift.py` checks only the model name (EVAL.md:2632-2635). Kill the textbook-McNemar rule if it fires on any same-model pairing | The canary must stay out of every optimization loop |

### 3G. LLM-judge reliability

| ID | What it is | Quantity | Data | Gain (source) | Test (file) | Risk |
|---|---|---|---|---|---|---|
| G1 | Validate judges with chance-corrected agreement (Cohen's κ / Krippendorff's α) on ≥2 benchmarks; never exact-match alone | κ with CI | Paired labels | Raw agreement overstates κ by 33–41 pp across 21 judges. Rankings shift by up to 14 positions across benchmarks. Test–retest > 0.95 coexists with position bias > 0.10 [S84]. GPT-4 matches humans at >80% agreement, the human–human level [S78] | κ for Jev–Haiku on Banking77 (raw agreement 0.823, R3), Jev–Clef in `~/.local/state/jev/vendor-shadow.jsonl` (EVAL.md:3725), and the two-labeller κ (EVAL.md:2443-2458). Kill any "agreement = quality" sentence where κ < 0.6 | None |
| G2 | Position and option-order bias: swap positions and aggregate (balanced position calibration), or estimate and remove the option-ID prior (PriDe) | Debiased verdict; position-consistency rate | Permuted calls (PriDe needs only a few) | Reordering alone made Vicuna-13B beat ChatGPT on 66 of 80 queries [S79]. Option order moves MCQ accuracy by 13–75%; calibration recovers up to 8 pp [S86]. Position bias is not random and varies by judge and task over 150,000 instances [S80]. 12 bias types quantified [S81] | $0 check: how often Jev's FiQA pick is candidate index 0 vs how often index 0 is relevant (`rows-fiqa-mkex-jev.jsonl` + `candidates-fiqa-fits.jsonl`). Kill the position-bias concern if the pick rate at index 0 ≤ the relevant rate at index 0 + 5 pp | Confounded by BM25 order. Our option-permute test already found 0/40 flips (EVAL.md:3500) |
| G3 | Self-consistency: sample several answers and use the vote, or the agreement, as the answer and confidence | Vote; dispersion | Repeated calls | +17.9% GSM8K with chain-of-thought sampling [S88]. Consistency helps black-box confidence [S54] | **Done (R6):** dispersion AUROC 0.525 vs 1−confidence 0.843. Demoted | Costs k× calls for no signal on Jev |
| G4 | Compare confidence channels: verbalized (output tokens) vs model-native probabilities, each after the same recalibration | AUROC for failure detection; ECE after Platt | Labelled rows with both channels | Verbalized confidence is often better calibrated than token probabilities for RLHF LMs (≈50% relative ECE reduction) [S53]. Verbalized confidence tends to be overconfident; the white-box vs black-box AUROC gap is 0.605 vs 0.522 [S54]. Larger models are calibrated on MC/TF "in the right format" [S20]. Jev claims probabilities calibrated by RLCD training (docs-mirror/typesafe/introduction/machine-learning-primer.md:37,49-61) | Banking77: Haiku `confidence` (`rows-full-haiku-prompted.jsonl`) vs Jev `probabilities`, both Platt-mapped on DEV 200. Kill `--backend llm` confidence if its AUROC < 0.70 | Haiku confidences pile at 1.0 (ties) |
| G5 | Panel of diverse smaller judges (PoLL) instead of one large judge | Panel vote | Several models | Beats a single large judge and is "over seven times less expensive" [S83] | **Done (R3):** four-arm majority 0.837 vs best single 0.962. Demoted | Correlated errors make the panel worse than its best member |
| G6 | Criteria drift (graders refine the rubric while grading) and self-preference (judges favour their own outputs) | Re-label κ over time | Re-labelled items | Criteria drift documented; some criteria depend on outputs already seen [S85]. Self-recognition correlates linearly with self-preference [S82] | Blindly re-label 30 TTSR-graded injections from EVAL.md:3326-3331 two weeks later; κ vs the original labels. Kill rubric-freeze claims if κ < 0.7 | Labour; small n |

### 3H. Cascades and routing (cost)

| ID | What it is | Quantity | Data | Gain (source) | Test (file) | Risk |
|---|---|---|---|---|---|---|
| H1 | Confidence-deferral cascade: a cheap model or rule answers; low-confidence rows are deferred to the expensive model | Cost vs accuracy curve | Paired outputs from both tiers | Match GPT-4 at up to 98% cost reduction, or +4% accuracy at equal cost [S35]. K=3 cascades save up to 88.93% compute with +2.18% accuracy [S41]. For classification, deferral by predicted-class uncertainty is favoured "theoretically and practically" [S37]. Self-verification + POMDP: >50% cost cut [S39] | **Done (R7) for find:** −3.4 pp at −20% calls. Next: Clef-first on Banking77 (Clef is more accurate, so the cascade is Clef → Jev on low Clef p). Kill if no setting reaches ≥ Clef accuracy at < 100% Clef latency | Cost is not our binding constraint except on find; the deferral signal is weak |
| H2 | Online cascade learning / neural caching: a small student (logistic regression on TF-IDF or embeddings) is trained continuously on the LLM's answers; a deferral policy (margin, query-by-committee) sends uncertain rows to the LLM | LLM-call share at a fixed accuracy | A stream of LLM-labelled rows | Parity with the LLM at up to 90% lower inference cost, robust to input shift [S40]. Margin sampling and QBC give consistent gains as deferral policies [S44] | Train TF-IDF LR on the 2,480 non-sample Banking77 rows labelled by **Jev's choices** (`full.jsonl` text + `rows-full-jev.jsonl`); defer low-margin rows on the 600 held rows. Kill if accuracy at 50% Jev share < 0.77 | The student copies Jev's errors. For find, the passages are in hashed logs (UNVERIFIED whether text is retained) |
| H3 | Learned routers (preference-trained, difficulty-predicting, POMDP, cascade routing, Markov-copula threshold tuning) | Route per query | Training pairs with outcomes | >2× cost cut [S36]; 40% fewer large-model calls [S38]; cascade routing beats routing and cascading alone [S42]; copula tuning +4.3% AUC (+10.2% at n ≤ 30) [S43] | $0 upper bound first: the share of Banking77 rows where some cheaper arm is right and Jev is wrong (R3 arrays). Kill if the oracle gain < 5 pp | Our one-Choice usage router lost to keywords, 12/94 vs 32/94 (NE:4505-4506) |
| H4 | Batch prompting: several items in one call share the instructions and demonstrations | Tokens per item | Live calls | Up to 5× token and time cut with 6 items per batch [S97]. Batched prompts lose accuracy and depend on position; permutation ensembling recovers it with 9–16% of the calls [S98] | $0: from stored `usage.input_tokens`, estimate the share that is fixed instruction (e.g., find rows average 4,888 tokens). Kill if the instruction share is < 10% | Cross-item contamination; position effects |

### 3I. Question / prompt optimization

| ID | What it is | Quantity | Data | Gain (source) | Test (file) | Risk |
|---|---|---|---|---|---|---|
| I1 | Search over the question text with an LLM proposer and a metric on a train split: MIPROv2 (Bayesian surrogate over instructions and demos), GEPA (reflective evolution + Pareto set), OPRO, APE, TextGrad, contrastive reflection | Held-out accuracy of the best wording | Labelled train/dev split + an untouched held-out set; live calls | DSPy: >25% over few-shot [S89]. MIPRO up to +13% [S90]. GEPA >10% over MIPROv2 [S91]. OPRO up to +8% GSM8K, +50% BBH [S92]. APE ≥ humans on 19/24 tasks [S93]. TextGrad GPQA 51→55% [S94]. **Classifier-like tasks are mixed:** "minor gains" on guardrails, 46.2→64.0 on prompt evaluation [S95]. One contrastive repair took exact match 51.4→60.4 vs MIPROv2 59.4 and GEPA 57.0 [S96]. Wording alone moved our spam seat by 0.25 (EVAL.md:1394-1395) | $0 first: the spread of stored wording variants is an upper-bound proxy for what search can find (`work/jev-9tkx` keep variants 0.190–0.242, EVAL.md:3443; `work/jev-question-writing/pass{4,5,7}-labels.json`). If the spread < bar gap, skip the live search. Live: GEPA on vendor dev 120, held 200 untouched | Overfitting to a 100–200-row dev set; moving the bar. On the keep side, a sweep found precision never > 0.23 at any cut (EVAL.md:3462), which is model-limited (NE R137) |

### 3J. Multi-question and joint decoding

| ID | What it is | Quantity | Data | Gain (source) | Test (file) | Risk |
|---|---|---|---|---|---|---|
| J1 | Joint inference over related answers: a weighted MaxSAT over per-question beliefs plus pairwise compatibility (BeliefBank, ConCoRD, Maieutic). A cheaper use: constraint violations as error flags (two exclusive Nouls both yes; p(Q) + p(¬Q) far from 1) | Consistent answer set; violation flag | Several questions over the same state | MaxSAT revision improves accuracy and consistency [S100]. +5% absolute on ConVQA [S101]. Maieutic up to +20% [S102]. Constraint violations imply at least one error [S23]. Our repo already prefers one Choice over a Noul map: Choice 11/11 vs Noul map 9/11 (TESTS.md:298). Our negation transform kept decisions but "redistributes mass incoherently" (EVAL.md:3500-3501) | $0: on the 40 stored msax rows (`var/agent-tmp/partb.001/partb_receipt.jsonl`, transforms identity/negated), score \|p(Q) + p(¬Q) − 1\| as an error flag against the stored labels and compare its AUROC with 1−confidence. Kill if AUROC ≤ 0.6. Then collect rows with ≥2 exclusive Nouls in the ask-bundle design (TESTS.md:298 has only n=11) | n=40; mostly mitigated already by the Choice shape |
| J2 | Interference when several questions or tasks share one context | Δ accuracy (co-asked vs alone) | Live paired calls | Task switches in conversational history cause significant degradation [S99]. Batched-data position effects [S98] | **Partial $0 proxy:** the 118 repeated (prompt, memory) pairs in `~/.local/state/jev/memory-filter-full.jsonl` span the serial era and the concurrent 4-wide era (EVAL.md:3420, 3427: 4 flips, 3.39%); split the flips by era. This tests concurrency, not co-asking. No existing co-asked vs alone pairs were found: jev-1lim and jev-uncd share only 4 commands, and both used the same 5-question bundle. The true test is live: 100 states × (alone vs co-asked) on one Noul. Kill if flips ≤ the 3.39% same-pair floor | UNVERIFIED whether Jev's parallel questions share decoding |

### 3K. Safety-specific thresholds

| ID | What it is | Quantity | Data | Gain (source) | Test (file) | Risk |
|---|---|---|---|---|---|---|
| K1 | Neyman–Pearson umbrella: take the cut as an order statistic of held-out **negative** scores, so P(type-I error > α) ≤ δ. Minimum negatives q ≥ log δ / log(1−α) [S103] | Cut with a certified false-alarm rate | **Negatives only:** 29 / 59 / 149 / 299 at α = .10 / .05 / .02 / .01, δ = .05 `[DERIVED]` | "Directly limit the empirical type I error to no more than α" does **not** control type I error [S103] | Screen: cut from the 300 clean tool results (`work/jev-injection-flag/rows-jev-full.jsonl`, field `p`) for α=0.02; then planted catch at that cut (`work/jev-29s4/live-rows.jsonl`). Gate: the 940 blind-clear rows. Kill if the out-of-time false-flag rate (j0er replay rows) exceeds α | Certifies only the population sampled; recall is not controlled; shift voids it |
| K2 | Over-defense benchmark: benign texts full of injection trigger words | False-flag rate on trigger-rich benign text | 339 benign samples (NotInject) | SOTA prompt guards drop to about 60% accuracy (near random) on NotInject; InjecGuard +30.8% [S104] | $0: tag trigger-word rows among the 300 clean results (`tool-results-sample.json` text) and compare false flags with and without triggers (`rows-jev-full.jsonl`). Kill the concern if the difference < 2 pp | Few trigger rows in our sample |

---

## 4. Directly relevant to our failures

| Failure (receipt) | Mechanism according to the literature | Technique IDs | Cheapest test (all $0 unless noted) | What would falsify the explanation |
|---|---|---|---|---|
| **Zero positives.** qunw: precision 0/403, "recall undefined: zero labelled positives" (BJ:438). Vendor-paste: 0/39 vendored (BJ:361). Gate wording: 1 target-harm row in 3,838 (classifier-areas.md:70) | • No method estimates recall without positives.<br>• Class-conditional conformal needs ≥⌈1/α−1⌉ positives per class [S1 §4.2], which is why 9kmq became vacuous.<br>• False alarms, however, can be certified from **negatives alone** [S103], and we have plenty: 940 blind-clear gate rows, 300 clean tool results.<br>• Positives should be **searched for**, not sampled [S70], and used only for recall and thresholds.<br>• If positives are rare but nonzero, importance sampling keeps estimates unbiased [S67, S69] | K1, E5, E4, B3 (as a refusal rule), E1 | K1 on gate and screen negatives plus planted catch rates (files in K1). Add the NP minimum-n check to `scripts/bar-reachable.py`'s pre-spend logic: refuse a positive-class claim when positives < ⌈1/α−1⌉ | A positive-class guarantee proven with fewer positives than the bound would contradict [S1, S103] |
| **Keep-side precision 0.19–0.24** (EVAL.md:3443; NE:4869; sweep never > 0.23 at any cut, EVAL.md:3462) | • Precision is capped by prevalence `[DERIVED]`. At the dev-slice prevalence of 9/170 and TPR 0.89, keep precision ≥ 0.39 needs a false-keep rate ≤ 7.8%; observed ≈ 21% (34/161). At the organic 9kmq prevalence of 3/167, it needs ≤ 2.9%.<br>• The cut sweep shows the score's ranking (AUC), not the cut, is the limit. No post-hoc calibration raises AUC [S29 caveat].<br>• Literature says: (a) control the **cost-bearing error** instead (false drops, via CRC [S4] or NP on the relevant class); (b) when precision must be certified, use FDR-controlled selection [S12, S13], which honestly returns an empty set when the signal is insufficient | B6, B4, K1, F1 | B6 on m959 keeps (q = 0.6). B4 for a false-drop ≤ 2% cut once ≥ 49 relevant rows exist (E5 to find them) | An FDR selection with q ≤ 0.6 returning a non-empty set on held rows would show signal the sweep missed |
| **Demo → organic drop 0.990 → 0.335** (EVAL.md:3468 vs 3550) | • Two shifts stacked `[DERIVED, R4]`:<br>• (1) Label shift: UNFIT prevalence 0.96 → 0.29. Same rates projected to 0.29 give 0.629.<br>• (2) Conditional shift: veto-on-FIT 0.20 (n=10) → 0.739. D9's FIT rate came from 10 rows; its Wilson upper bound 0.510 projects 0.399, close to the observed 0.335.<br>• The label-free alarm was visible: an unchanged veto rate (0.804 → 0.790) despite the prevalence change, π̂ = 0.938 [S72], KS p ≈ 0.001 [S73].<br>• Calibration maps do not survive shift [S49], and same-name models drift [S77] | F1, F2, K1, E1, A6, D3 | Make "project precision at the target prevalence using the dev confusion matrix and its CI" a mandatory row of `classifier ready` (bead jev-b35c.7, BJ:167). Require ≥59 negatives per class before certifying a false-alarm rate (K1). Use E1 with 30 organic labels to estimate prevalence before an enforcement replay | If a future demo→organic drop occurs with an organic flag rate matching the BBSE-projected rate and KS p > 0.2, the shift explanation is wrong for that case |
| **Judge drift.** Pin check covers the model name only (EVAL.md:2632-2635); retired rule still firing 125× (NE:4803); criteria drift risk for TTSR (classifier-areas.md:158) | • Same-name services change behaviour [S77].<br>• Paired per-sample tests catch 0.3% degradations [S76], **but our same-model reruns already differ at p = 0.0076 (R5)**, so the null must be the run-to-run envelope.<br>• Sequential confidence sequences avoid peeking inflation [S74]. CUSUM catches small mean shifts [S75].<br>• Human graders drift too [S85]. Agreement must be κ, not exact match [S84] | F5, F4, F3, G1, G6 | Frozen canary of stored Banking77 + SciFact states. Envelope from runs 1–3 (`rows-full-jev*.jsonl`; `work/noul-scifact/rows-jev{,-run2,-run3}.jsonl`). Weekly replay costs about $0.016 per 1,000 answers (docs/LEDGER.md:166) | If the weekly replay's discordance stays inside the run-to-run envelope while labelled accuracy drops, the canary is not representative |
| **Cost per surface.** find is $6.63 of $7.00 per 7 days, 4,888 tokens per call; the others are ≤ $0.16 (scoreboard, `[DERIVED]`) | • Only find has dollar cost worth optimizing.<br>• The literature's levers: cascades [S35, S37, S41], distilled students [S40, S44], fewer tokens per call (FrugalGPT "prompt adaptation" [S35]).<br>• The FiQA proxy shows lexical deferral costs accuracy (R7).<br>• For every other surface the binding cost is **labels and latency**, not dollars, so PPI and active inference [S62, S64, S65] reduce the real cost `[INFERENCE]` | H2, H1, E1, E2 | H2 on Banking77 as a public proxy. For find, measure the passage-token share that never affects the pick (truncate passages at 25/50/75% on stored FiQA candidates). That needs live calls (~$0.02 for 323 queries × 3 at 8,795 tokens), so C = 3 | If truncating to 50% tokens keeps FiQA top-1 within 1 pp, token reduction beats any cascade |
| **Forecasting 0/12** (EVAL.md:3528-3529) | The label is not in the tokens. No calibration, conformal or selection method adds signal [S29]. Conformal sets become full and AUGRC ≈ random | C1, B1 as kill tests | Compute the AUGRC and conformal set size on any forecasting rows before building | — |
| **Clef-vs-Jev claims** (README.md:132; classifier-areas.md:37-38) | The comparison gave one arm a dev-fitted Platt map and the other none (R1) | A1, A7 | Commit symmetric legs; report a bootstrap CI for every ECE and AUC difference | — |

---

## 5. Reproduction code for §1 (kernel-only; run from repo root; stdlib + numpy)

```python
# R1 symmetric Platt (Banking77). Mirrors run.py:25-26, 83-94, 110-124, 161-195.
import json, math, random, numpy as np
B='work/choice-banking77'; ROWS=[json.loads(l) for l in open(B+'/full.jsonl') if l.strip()]
S=sorted(random.Random(7).sample(range(len(ROWS)),600)); D=sorted(random.Random(8).sample(sorted(set(range(len(ROWS)))-set(S)),200))
INT=sorted({r['intent'] for r in ROWS},key=lambda c:(c.casefold(),c)); LAB={c.replace('_',' ').lower():c for c in INT}
def jr(keep,f='rows-full-jev.jsonl'): return [(r['probabilities'].get(r['choice']) or 0.0, LAB.get(r['choice'],r['choice'])==r['intent']) for r in map(json.loads,open(B+'/'+f)) if r['i'] in keep and r.get('choice')]
def ece(p):
    b=[[] for _ in range(10)]; [b[min(int(x*10),9)].append((x,o)) for x,o in p]
    return sum(len(v)/len(p)*abs(sum(x for x,_ in v)/len(v)-sum(o for _,o in v)/len(v)) for v in b if v)
lg=lambda p: math.log(min(max(p,1e-4),1-1e-4)/(1-min(max(p,1e-4),1-1e-4)))
def fit(xs):
    a,b=1.0,0.0
    for _ in range(2000):
        ga=sum((1/(1+math.exp(-(a*lg(p)+b)))-o)*lg(p) for p,o in xs); gb=sum(1/(1+math.exp(-(a*lg(p)+b)))-o for p,o in xs)
        a-=0.1*ga/len(xs); b-=0.1*gb/len(xs)
    return a,b
a,b=fit(jr(set(D))); h=jr(set(S)); print(ece(h), ece([(1/(1+math.exp(-(a*lg(p)+b))),o) for p,o in h]))  # 0.1017 0.0276
# Vendor: same fit on work/vendor-paste/vendor-rows.jsonl rows whose sample_id is in sample.json['dev'], apply to ['held']; labels via vendor.py:28-29 positive().
# R2: P = 3080x77 matrix from rows-full-jev.jsonl 'probabilities'; s = 1-P[i,y]; q = np.quantile(s_cal, ceil((n+1)(1-a))/n, method='higher'); set = 1-P <= q.
# R3: one-coin Dawid-Skene EM over A[600,4] choices (jev, haiku-prompted, clefflash, kev4b) on run.py SAMPLE; K=77; init acc 0.7.
# R4: arithmetic in §1 row R4 (inputs EVAL.md:3468, 3550; work/wbel/PREREG-replay.md:32 defines miss = P(FIT|allow)).
# R5: exact McNemar on discordant counts between rows-full-jev{,-run2,-run3}.jsonl choices.
# R7: candidates-fiqa-fits.jsonl BM25 scores (margin = s[0]-s[1]) x rows-fiqa-mkex-jev.jsonl choice; defer lowest-margin share to Jev.
```

---

## 6. Sources (fetched 2026-10-03)

arXiv entries: the abstract was fetched through the arXiv API. "(full)" means the full text was also fetched and read for the cited detail.

**Conformal / risk control**
- S1 Angelopoulos & Bates, A Gentle Introduction to Conformal Prediction, 2021. https://arxiv.org/abs/2107.07511 (full, ar5iv: §3.2 n=1000; eq. 4 APS; eq. 16 Beta coverage; §4.2 eq. 23-24; §4.3)
- S2 Romano, Sesia, Candès, Classification with Valid and Adaptive Coverage, 2020. https://arxiv.org/abs/2006.02544
- S3 Angelopoulos et al., Uncertainty Sets for Image Classifiers using Conformal Prediction (RAPS), 2020. https://arxiv.org/abs/2009.14193
- S4 Angelopoulos et al., Conformal Risk Control, 2022. https://arxiv.org/abs/2208.02814 (full: eq. 4, Thm 1)
- S5 Angelopoulos et al., Learn then Test, 2021. https://arxiv.org/abs/2110.01052
- S6 Ding et al., Class-Conditional Conformal Prediction with Many Classes, 2023. https://arxiv.org/abs/2306.09335
- S7 Kumar et al., Conformal Prediction with LLMs for Multi-Choice QA, 2023. https://arxiv.org/abs/2305.18404
- S8 Quach et al., Conformal Language Modeling, 2023. https://arxiv.org/abs/2306.10193
- S9 Mohri & Hashimoto, Language Models with Conformal Factuality Guarantees, 2024. https://arxiv.org/abs/2402.10978
- S10 Tibshirani et al., Conformal Prediction Under Covariate Shift, 2019. https://arxiv.org/abs/1904.06019
- S11 Podkopaev & Ramdas, Distribution-free UQ for classification under label shift, 2021. https://arxiv.org/abs/2103.03323
- S12 Jin & Candès, Selection by Prediction with Conformal p-values, 2022. https://arxiv.org/abs/2210.01408
- S13 Gui, Jin, Ren, Conformal Alignment, 2024. https://arxiv.org/abs/2405.10301
- S14 Yadkori et al., Mitigating LLM Hallucinations via Conformal Abstention, 2024. https://arxiv.org/abs/2405.01563
- S15 Su et al., API Is Enough: Conformal Prediction for LLMs Without Logit-Access, 2024. https://arxiv.org/abs/2403.01216

**Selective classification / deferral**
- S16 Geifman & El-Yaniv, Selective Classification for Deep Neural Networks, 2017. https://arxiv.org/abs/1705.08500
- S17 Traub et al., Overcoming Common Flaws in the Evaluation of Selective Classification Systems (AUGRC), 2024. https://arxiv.org/abs/2407.01032
- S18 Mozannar & Sontag, Consistent Estimators for Learning to Defer to an Expert, 2020. https://arxiv.org/abs/2006.01862
- S19 Jung, Brahman, Choi, Trust or Escalate, 2024. https://arxiv.org/abs/2407.18370 (full: fixed-sequence testing, cascade table)
- S20 Kadavath et al., Language Models (Mostly) Know What They Know, 2022. https://arxiv.org/abs/2207.05221

**Label-free accuracy / weak supervision / label quality**
- S21 Zhang et al., Spectral Methods meet EM (Dawid–Skene), 2014. https://arxiv.org/abs/1406.3824
- S22 Platanios, Blum, Mitchell, Estimating Accuracy from Unlabeled Data, UAI 2014. https://www.auai.org/uai2014/proceedings/individuals/313.pdf (full: ≥3 approximations, independent errors, eq. 7-8)
- S23 Platanios et al., Estimating Accuracy from Unlabeled Data: A Probabilistic Logic Approach, 2017. https://arxiv.org/abs/1705.07086
- S24 Ratner et al., Snorkel, 2017. https://arxiv.org/abs/1711.10160
- S25 Ratner et al., Training Complex Models with Multi-Task Weak Supervision, 2018. https://arxiv.org/abs/1810.02840
- S26 Fu et al., Fast and Three-rious (FlyingSquid), 2020. https://arxiv.org/abs/2002.11955
- S27 Smith et al., Language Models in the Loop (Alfred), 2022. https://arxiv.org/abs/2205.02318
- S28 Baek et al., Agreement-on-the-Line, 2022. https://arxiv.org/abs/2206.13089
- S29 Garg et al., Leveraging Unlabeled Data to Predict OOD Performance (ATC), 2022. https://arxiv.org/abs/2201.04234
- S30 Evaluating multiple models using labeled and unlabeled data (SSME), 2025. https://arxiv.org/abs/2501.11866
- S31 Multi-Source Emotion Annotation in Children's Language: When LLM Consensus Diverges from Human Judgment, LREC 2026 workshop. http://www.lrec-conf.org/proceedings/lrec2026/workshops/cas/pdf/2026.cas-1.11.pdf (full: Table 6)
- S32 Bayesian Calibration of Win Rate Estimation with LLM Evaluators, 2024. https://arxiv.org/abs/2411.04424
- S33 Northcutt et al., Confident Learning, 2019. https://arxiv.org/abs/1911.00068
- S34 Northcutt et al., Pervasive Label Errors in Test Sets, 2021. https://arxiv.org/abs/2103.14749

**Cascades / routing**
- S35 Chen, Zaharia, Zou, FrugalGPT, 2023. https://arxiv.org/abs/2305.05176
- S36 Ong et al., RouteLLM, 2024. https://arxiv.org/abs/2406.18665
- S37 Gupta et al., Language Model Cascades: Token-level uncertainty and beyond, 2024. https://arxiv.org/abs/2404.10136
- S38 Ding et al., Hybrid LLM, 2024. https://arxiv.org/abs/2404.14618
- S39 Aggarwal et al., AutoMix, 2023. https://arxiv.org/abs/2310.12963
- S40 Nie et al., Online Cascade Learning for Efficient Inference over Streams, 2024. https://arxiv.org/abs/2402.04513
- S41 Varshney & Baral, Model Cascading, 2022. https://arxiv.org/abs/2210.05528
- S42 Dekoninck et al., A Unified Approach to Routing and Cascading for LLMs, 2024. https://arxiv.org/abs/2410.10347
- S43 Rational Tuning of LLM Cascades via Probabilistic Modeling, 2025. https://arxiv.org/abs/2501.09345
- S44 Ramírez et al., Cache & Distil, 2023. https://arxiv.org/abs/2310.13561

**Calibration**
- S45 Guo et al., On Calibration of Modern Neural Networks, 2017. https://arxiv.org/abs/1706.04599
- S46 Kull, Silva Filho, Flach, Beta calibration, AISTATS 2017. https://proceedings.mlr.press/v54/kull17a.html (abstract page)
- S47 Kull et al., Dirichlet calibration, 2019. https://arxiv.org/abs/1910.12656
- S48 Kumar, Liang, Ma, Verified Uncertainty Calibration, 2019. https://arxiv.org/abs/1909.10155
- S49 Ovadia et al., Can You Trust Your Model's Uncertainty?, 2019. https://arxiv.org/abs/1906.02530
- S50 Zhao et al., Calibrate Before Use, 2021. https://arxiv.org/abs/2102.09690
- S51 Zhou et al., Batch Calibration, 2023. https://arxiv.org/abs/2309.17249
- S52 Gupta & Ramdas, Histogram binning without sample splitting, 2021. https://arxiv.org/abs/2105.04656
- S53 Tian et al., Just Ask for Calibration, 2023. https://arxiv.org/abs/2305.14975
- S54 Xiong et al., Can LLMs Express Their Uncertainty?, 2023. https://arxiv.org/abs/2306.13063
- S55 Roelofs et al., Mitigating Bias in Calibration Error Estimation, 2020. https://arxiv.org/abs/2012.08668
- S56 Vovk & Petej, Venn-Abers predictors, 2012. https://arxiv.org/abs/1211.0025
- S57 Shen et al., Thermometer, 2024. https://arxiv.org/abs/2403.08819
- S58 Calibrating Verbalized Probabilities for LLMs, 2024. https://arxiv.org/abs/2410.06707
- S59 Desai & Durrett, Calibration of Pre-trained Transformers, 2020. https://arxiv.org/abs/2003.07892
- S60 Alexandari et al., Maximum Likelihood with Bias-Corrected Calibration is Hard-To-Beat at Label Shift Adaptation, 2019. https://arxiv.org/abs/1901.06852
- S61 Niculescu-Mizil & Caruana, Predicting Good Probabilities With Supervised Learning, ICML 2005. https://www.cs.cornell.edu/~alexn/papers/calibration.icml05.crc.rev3.pdf (full: isotonic vs Platt below ~200–1,000)

**Label-efficient evaluation**
- S62 Angelopoulos et al., Prediction-Powered Inference, 2023. https://arxiv.org/abs/2301.09633 (full: rectifier, §1.3)
- S63 Angelopoulos et al., PPI++, 2023. https://arxiv.org/abs/2311.01453
- S64 Zrnic & Candès, Active Statistical Inference, 2024. https://arxiv.org/abs/2403.03208
- S65 Gligorić, Zrnic, Lee, Candès, Jurafsky, Can Unconfident LLM Annotations Be Used for Confident Conclusions?, NAACL 2025. https://arxiv.org/abs/2408.15204 (full: https://aclanthology.org/2025.naacl-long.179.pdf)
- S66 Fisch et al., Stratified Prediction-Powered Inference, 2024. https://arxiv.org/abs/2406.04291
- S67 Kossen et al., Active Testing, 2021. https://arxiv.org/abs/2103.05331
- S68 Boyeau et al., AutoEval Done Right, 2024. https://arxiv.org/abs/2403.07008
- S69 Sawade, Landwehr, Scheffer, Active Estimation of F-Measures, NeurIPS 2010. https://papers.neurips.cc/paper_files/paper/2010/hash/d7a728a67d909e714c0774e22cb806f2-Abstract.html
- S70 Attenberg & Provost, Why Label when you can Search?, KDD 2010. https://pages.stern.nyu.edu/~fprovost/Papers/guidedlearning-kdd2010.pdf (full)
- S71 Search Improves Label for Active Learning, NeurIPS 2016. https://papers.neurips.cc/paper_files/paper/2016/file/4f398cb9d6bc79ae567298335b51ba8a-Paper.pdf (full)

**Drift**
- S72 Lipton, Wang, Smola, Detecting and Correcting for Label Shift with Black Box Predictors (BBSE), 2018. https://arxiv.org/abs/1802.03916 (full: ŵ = Ĉ⁻¹μ̂)
- S73 Rabanser et al., Failing Loudly, 2018. https://arxiv.org/abs/1810.11953
- S74 Podkopaev & Ramdas, Tracking the risk of a deployed model and detecting harmful distribution shifts, 2021. https://arxiv.org/abs/2110.06177
- S75 NIST/SEMATECH e-Handbook, 6.3.2.3 CUSUM Control Charts. https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc323.htm
- S76 When LLMs get significantly worse: a statistical approach to detect model degradations, 2026. https://arxiv.org/abs/2602.10144
- S77 Chen, Zaharia, Zou, How is ChatGPT's behavior changing over time?, 2023. https://arxiv.org/abs/2307.09009

**LLM-judge reliability**
- S78 Zheng et al., Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena, 2023. https://arxiv.org/abs/2306.05685
- S79 Wang et al., Large Language Models are not Fair Evaluators, 2023. https://arxiv.org/abs/2305.17926
- S80 Judging the Judges: A Systematic Study of Position Bias in LLM-as-a-Judge, 2024. https://arxiv.org/abs/2406.07791
- S81 Ye et al., Justice or Prejudice? (CALM), 2024. https://arxiv.org/abs/2410.02736
- S82 Panickssery et al., LLM Evaluators Recognize and Favor Their Own Generations, 2024. https://arxiv.org/abs/2404.13076
- S83 Verga et al., Replacing Judges with Juries (PoLL), 2024. https://arxiv.org/abs/2404.18796
- S84 Reliability without Validity: a large-scale evaluation of LLM-as-a-Judge, 2026. https://arxiv.org/abs/2606.19544 (full: §5.1, §5.3)
- S85 Shankar et al., Who Validates the Validators?, 2024. https://arxiv.org/abs/2404.12272
- S86 Pezeshkpour & Hruschka, LLM Sensitivity to the Order of Options in MCQ, 2023. https://arxiv.org/abs/2308.11483
- S87 Zheng et al., LLMs Are Not Robust Multiple Choice Selectors (PriDe), 2023. https://arxiv.org/abs/2309.03882
- S88 Wang et al., Self-Consistency, 2022. https://arxiv.org/abs/2203.11171

**Prompt / question optimization**
- S89 Khattab et al., DSPy, 2023. https://arxiv.org/abs/2310.03714
- S90 Opsahl-Ong et al., MIPRO, 2024. https://arxiv.org/abs/2406.11695
- S91 Agrawal et al., GEPA, 2025 (rev. 2026-02). https://arxiv.org/abs/2507.19457
- S92 Yang et al., Large Language Models as Optimizers (OPRO), 2023. https://arxiv.org/abs/2309.03409
- S93 Zhou et al., APE, 2022. https://arxiv.org/abs/2211.01910
- S94 Yuksekgonul et al., TextGrad, 2024. https://arxiv.org/abs/2406.07496
- S95 Is It Time To Treat Prompts As Code? (DSPy multi-use-case study), 2025. https://arxiv.org/abs/2507.03620
- S96 Contrastive Reflection for Iterative Prompt Optimization, 2026. https://arxiv.org/abs/2606.30840

**Multi-question / joint decoding**
- S97 Cheng et al., Batch Prompting, 2023. https://arxiv.org/abs/2301.08721
- S98 Lin et al., BatchPrompt, 2023. https://arxiv.org/abs/2309.00384
- S99 Gupta et al., LLM Task Interference, 2024. https://arxiv.org/abs/2402.18216
- S100 Kassner et al., BeliefBank, 2021. https://arxiv.org/abs/2109.14723
- S101 Mitchell et al., ConCoRD, 2022. https://arxiv.org/abs/2211.11875
- S102 Jung et al., Maieutic Prompting, 2022. https://arxiv.org/abs/2205.11822

**Safety thresholds**
- S103 Tong, Feng, Li, Neyman-Pearson classification algorithms and NP-ROC, 2016. https://arxiv.org/abs/1608.03109 (full: minimum sample size q ≥ log δ / log(1−α), Algorithm 1)
- S104 Li, Liu, Xiao, InjecGuard / NotInject, 2024. https://arxiv.org/abs/2410.22770

Not counted: one search result could not be fetched (MDPI "Degradation of Multi-Task Prompting Across Six NLP Tasks", HTTP 403) and is not cited.

---

## 7. Unverified, and limits

- Every §1 number is a single-session recomputation by the author of this file: exploratory, not preregistered, not verified by a non-author. The verifying step is to commit the §5 legs and have a non-author run them.
- Whether Jev's probabilities are logit-derived or verbalized is UNVERIFIED. The docs say only that RLCD training targets calibrated probabilities (machine-learning-primer.md:37,49-61).
- Whether Jev's parallel questions over one state share decoding is UNVERIFIED (affects J2).
- Not located: the location of D9's per-row correct/wrong labels (needed for A6/D3), and whether the find and memory sidecar logs retain text (needed for H2 on real traffic).
- dcg block-log location (E5 gate positives) is UNVERIFIED.
- The G, F and C ratings are judgements. The ranking can change after the $0 tests in §3 run.
