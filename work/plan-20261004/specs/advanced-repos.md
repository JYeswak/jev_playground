# Advanced repos and libraries for the `classifier` CLI

Date: 2026-10-03. Read-only. I made no live Jev or Clef calls and installed nothing. I fetched every URL below during this session through the `read` tool (GitHub API, raw README, or HF API). Line citations into this repo are `file:line`. Mirror citations are `/Volumes/ZestData/dicklesworthstone-mirror/<repo>@<short-sha>/<path>:<lines>`.

Excluded because the specs already cover them: the 42 local clones and every awesome-list row in `work/plan-20261004/specs/ideas-repos-{a,b,c}.md` (for example jevcal, Janus, jev-mcp/jkudish, jev-axi, jev-cli, system-one-adapter-python). This file adds only projects missing from those lists, plus the general ML/guardrail/eval libraries.

Verdicts: **ADOPT-IDEA** (copy the design, no code), **PORT-ALGO** (re-implement under 100 lines, zero deps), **USE-AS-BASELINE** (run as an incumbent arm in `eval`, never ship as a dependency), **SKIP**.

## 0. One local measurement made for this report (keyless)

`work/choice-banking77/rows-full-jev.jsonl`: 3,080 rows, 2,467 correct (this matches PRODUCT.md:58's Jev arm). **181/3,080 = 5.9% put exactly 0.00 on the gold intent**, and 1,180 rows have a top probability of exactly 1.00. I computed this by parsing the file in Python, with no calls. It matters for items 1, 4, 8 and 12 below: no rescaling can lift an exact 0, and a log-loss fit with a 1e-6 floor is dominated by these rows (source: item 1).

## 1. Ranked techniques (score = expected gain × feasibility on our data ÷ cost)

Scale 1–3 each. The gain is the upstream claim, and transfer to our data is UNVERIFIED until the named test runs.

|#|technique (source project)|verdict|family/verb|gain|feas.|cost|score|cheapest falsifiable test on data we have|
|---|---|---|---|---|---|---|---|---|
|1|Endpoint-aware log floor for quantised Jev probabilities (jev-ood-calibration)|PORT-ALGO|`calibrate`, `eval` (all Choice/Score)|3|3|1|9|`work/choice-banking77/rows-full-jev.jsonl`: fit temperature with floor 1e-6 vs 0.005. Predict T moves toward 1|
|2|ECE noise floor plus bootstrap CI on every ECE we print (jev-ood-calibration, jev-exploration, verified_calibration, franken_nlp)|PORT-ALGO|`eval`, `calibrate`, `explain`|3|3|1|9|`work/local-decision-arms/rows-clefflash.jsonl` (600) and B77 Jev rows: is .025 vs .102 (PRODUCT.md:58) outside both floors?|
|3|Slope-transfer Platt: keep the slope, refit only the intercept on ~50 labels (jev-exploration)|PORT-ALGO|`calibrate` (new task, few labels)|3|3|1|9|Fit slope on `work/choice-clinc150/rows-full-jev.jsonl`, refit intercept on 50 rows of B77 Jev, score held-out B77 ECE vs raw and vs full Platt|
|4|Calibration artifact lifecycle: split digests, validity window, shift policy, Calibrated/Uncalibrated/Invalidated/Stale (franken_nlp, frankensearch)|ADOPT-IDEA|`calibrate`, `doctor`, `explain`, exit codes|2|3|2|3.0|Planted: an expired or shifted map must yield `uncalibrated`/abstain (unit test against `kit/calibration/clef/banking77-intent.v1.json`)|
|5|Confident-learning label-issue finder (cleanlab)|PORT-ALGO|`cases`, `eval` (corpus hygiene)|2|3|1|6|Positive control: `work/jev-a9fv` has 68 input hashes with contradictory labels (EVAL.md:2978). The finder must flag most of them|
|6|Prediction-powered inference for prevalence/accuracy with few labels (ppi_py)|PORT-ALGO|`watch`, `eval --log`, exposure gate (PRODUCT.md:75-77)|3|2|1|6|`work/jev-wb7j/labels.jsonl` (100 labelled) + `work/jev-wb7j/rows.jsonl` (unlabelled): CI width, PPI vs labels-only|
|7|Dawid–Skene gold-free accuracy estimation (crowd-kit)|PORT-ALGO|`eval --log` (the Janus GAP, ideas-repos-a.md:57)|2|3|2|3.0|B77 overlap of Jev / Haiku-prompted / Clef rows. Estimated per-annotator accuracy vs true accuracy (gold exists, so this is falsifiable)|
|8|APS/RAPS conformal prediction sets for multiclass (MAPIE, TorchCP, crepes)|PORT-ALGO|`route` (set-valued output → ask/back-off)|2|2|1|4|B77 Jev full vectors: mean set size at α=0.1 on a 50/50 split. Compare with top-1 + abstain@0.60|
|9|Conformal risk control / Learn-then-Test thresholds (conformal-risk, ltt, MAPIE)|PORT-ALGO|`gate`, `memory`, `calibrate --target`|3|1|1|3|Already run as split-conformal in jev-9kmq: memory FAIL on 3 positives, gate PASS offline (EVAL.md:3729-3735). Rerun on vendor windows only|
|10|Expected-loss multi-action decision with a loss matrix (process_triage mirror)|ADOPT-IDEA|`gate`, `screen` (act/review/escalate GAP, ideas-repos-c.md:34)|2|2|1|4|`work/jev-a9fv/live-rows.jsonl`: replay 3 actions under a stated loss matrix vs a binary 0.5 cut|
|11|Two-sided confident-ends filter (jev-eval)|ADOPT-IDEA|all Noul families|2|3|1|6|`work/vendor-paste/vendor-rows.jsonl`: coverage at ≥0.99 precision on each tail separately|
|12|Isotonic (PAV) instead of Platt (Jev-Calibration, netcal, franken_nlp)|PORT-ALGO|`calibrate`|1|3|1|3|Already partly run: `work/jev-science/CALIBRATION.md:15-16` shows no consistent gain. Rerun on Clef B77 dev 200 → held 600|
|13|Venn-ABERS interval [p0,p1] → abstain when wide (venn-abers)|PORT-ALGO|`calibrate`, `explain`|1|2|1|2|`work/local-decision-arms/vendor-rows-clefflash{-dev,}.jsonl` (120 → 200)|
|14|Prevalence estimate by adjusted classify-and-count (QuaPy, label-shift BBSE)|PORT-ALGO|exposure gate before any bar|2|2|1|4|Gate rows: estimate positives in organic traffic from Jev scores + dev TPR/FPR. Compare with the 0/39 vendor organic count (PRODUCT.md:59)|
|15|Cascade threshold by target escalation share (RouteLLM, FrugalGPT)|ADOPT-IDEA|`effort`, `route`|1|3|1|3|Jev→Haiku on B77 rows. Overlaps jevcal/Janus, which we already tested (EVAL.md:1454-1460)|
|16|Anytime-valid e-process / confidence sequences for drift alarms (confseq, frankenjax mirror)|PORT-ALGO|`watch`|2|1|1|2|Replay the daily gate free-rate stream in `work/jev-jzgm/replay.py` output. An alarm must fire on a planted rate drop|
|17|Prompt-injection model baselines (Prompt Guard 2, protectai deberta v2)|USE-AS-BASELINE|`screen` eval arm|2|2|2|2|`upstream/Gaurav-Gosain/jev-sec-bench` (deepset/prompt-injections, 662). Local transformers in a throwaway venv, not shipped|
|18|WorkflowEvals datasets (TypeSafe)|USE-AS-BASELINE|`route`/`gate`/`score` eval|2|2|2|2|Needs HF download + keys. References are model consensus, not gold (see wuyoscar row)|
|19|Thompson/UCB1 bandits for arm selection (meta_skill, frankenterm mirror)|ADOPT-IDEA|`effort`|1|1|2|0.5|Our usage router LOST (PRODUCT.md:62). Without a dense reward there is nothing to learn from|

Top three this week: 1, 2, 3. Each is under 30 lines, uses rows already on disk, and can falsify a number already in PRODUCT.md.

## 2. Technique cards (for ranks 1–17)

**1. Endpoint-aware floor.** Jev returns probabilities rounded to 0.01, and Choice/Score use exactly 0 and 1. A correct answer at exactly 0 costs −log(1e-6) = 13.8 nats and dominates any temperature/Platt fit. Quantity: NLL = −Σ log max(p_y, 0.005), i.e. half a grid step. Data: existing rows, no new labels. Gain (upstream, n=900 synthetic tickets): Choice refit T fell from 3.29 to 1.30 and Score from 3.40 to 1.92 once the floor was 0.005. ECE barely moved (0.084 → 0.072) (https://github.com/scienthoon/jev-ood-calibration, README "Correction 2026-09-22"). jev-exploration finding 7 says the same: Noul never returned an exact 0 in 11,148 answers (https://github.com/SamuelSacco/jev-exploration). Our B77 exposure is 5.9% (§0). Risk: the floor is a convention, so print it in the receipt. A conflicting precedent: franken_nlp passes exact 0/1 through temperature unchanged (mirror franken_nlp@8f8ae35/src/calibration.rs:443-449) and refuses them at fit time (:393-395).

**2. Noise floor + bootstrap CI for ECE.** Binned ECE is biased upward at small n, so a perfectly calibrated model still shows ECE > 0. Quantity: floor = mean over B resamples of ECE(p, y*), where y*_i ~ Bernoulli(p_i). Report ECE/floor and a seeded percentile-bootstrap CI. Data: existing rows. Gain: honesty, not accuracy. jev-exploration shows a perfectly calibrated model scores ECE ≈ 0.045 at n=60, which is the range a widely cited 60-case benchmark reports (finding 5). jev-ood reports a floor of 0.024 for n=900. Library precedents: `cal.get_calibration_error_uncertainties` and a debiased estimator (https://github.com/p-lambda/verified_calibration README), seeded bootstrap in mirror franken_nlp/src/calibration.rs:583-748 (splitmix64 at :852), smECE with bootstrap CI (https://github.com/apple/ml-calibration README). Risk: none, but some current "calibration WIN" lines may become ties.

**3. Slope-transfer Platt.** On jev-1.13.0, Platt's slope was stable at 2.11–2.61 across difficulty tiers, while the intercept moved from −0.48 to +1.75 with the base rate. Quantity: p' = σ(a·logit(p) + b), with a fixed from a source task and b fitted by 1-D MLE on n target labels. Data: ≥50 labels per new task (fewer than 30 made calibration up to 4× worse than raw). Gain: −62% ECE on held-out items with 50 labels (jev-exploration finding 6). Upgrades `calibrate` for the many-tasks, few-labels case. Our clef spec currently fits a full map per `question_sha256` (clef-backend-spec.md:42). Risk: their slope was Noul-only and one model version. LEDGER.md:212 says thresholds do not transfer across datasets; the slope might, and test 3 decides which.

**4. Calibration artifact lifecycle.** A calibration map is a dated, digest-bound artifact with a validity window and a typed policy for distribution shift. Quantity: a state machine, not a statistic. Mirror: franken_nlp/src/calibration.rs:142-232 (disjoint Development/Calibration/LockedTest splits with SHA-256 digests), :1065-1116 (`ValidityWindow`, `ShiftPolicy::{RawScoresUncalibrated, ConservativeAbstain}`), :1119-1350 (`CalibrationArtifact::decide`), :1353-1384 (`CalibrationState`; "abstained remains a successful structured result with process exit zero"). frankensearch@d1cb86e1/crates/frankensearch-core/src/decision_plane.rs:262 (`CalibrationStatus` Uncalibrated/Calibrating/Calibrated/Stale), :337-344 (`max_ece` 0.05 fallback trigger), :410-416 (reason codes `calibration.fallback.{insufficient_data,distribution_shift,error_too_high,model_changed}`). Upgrades `doctor` (stale map = finding), `explain`, exit codes. Risk: ceremony. Adopt only the four states and reason codes, not the 15-column contract (docs/demos/upstream-repro/math-and-next-level-20260919.md:571-574 already warns about this).

**5. Confident learning.** Per class j, threshold t_j = mean p̂_j(x) over items labelled j. An item labelled i is suspect if some j ≠ i has p̂_j ≥ t_j (argmax among the classes above threshold). The issues are the off-diagonal cells of that confident joint. Data: labelled rows plus classifier probabilities, which we have. Gain: no number transfers. cleanlab claims label-issue finding "in ONE line" (https://github.com/cleanlab/cleanlab README, JAIR'21 paper). Upgrades `cases lint`. Risk: it flags the classifier's own blind spots as label errors, so a human must adjudicate. The a9fv conflict set is a built-in positive control.

**6. PPI.** Estimate a population mean (prevalence, accuracy, flag rate) from n gold labels plus N unlabeled model predictions. Quantity: θ̂ = mean_N f(x̃) − mean_n (f(x) − y), CI θ̂ ± z·√(σ²_f/N + σ²_Δ/n). Data: tens of labels + the unlabeled log. Gain: "tighter confidence intervals and more powerful p-values" (https://github.com/aangelopoulos/ppi_py README; `ppi_mean_ci(Y, Yhat, Yhat_unlabeled, alpha)`). Size on our data is UNVERIFIED. It addresses our recurring failure, "~0 organic positives" (PRODUCT.md:75-77): you get an honest CI on prevalence before spending labelling effort. Risk: if f is weakly correlated with y, the CI is no tighter than labels alone.

**7. Dawid–Skene.** EM over class priors π and per-annotator confusion matrices θ^(k). Posterior T_ic ∝ π_c Π_k θ^(k)[c, l_ik]. Data: ≥3 annotators on the same items, no gold. crowd-kit ships DS, GLAD, MACE, KOS, M-MSR, Wawa (https://github.com/Toloka/crowd-kit file tree; Apache-2.0 per LICENSE). Upgrades the `eval --log` agreement mode. Test it where gold exists so the estimate can be scored. Risk: DS assumes conditionally independent errors. Our `ensemble/README.md:24-34` shows correlated pairs (phi 0.34–0.53), which can make DS confidently wrong.

**8. APS/RAPS sets.** Nonconformity s(x,y) = Σ_{j: π_j ≥ π_y} π_j (randomised). q̂ = the ⌈(n+1)(1−α)⌉/n empirical quantile. Set = {y : s(x,y) ≤ q̂}. Data: a labelled calibration split with full probability vectors. Only Jev rows have these. Clef rows carry `p_choice` only (`work/local-decision-arms/rows-clefflash.jsonl` schema), so Clef supports only LAC on the top label. Gains reported upstream are coverage guarantees, not accuracy (https://github.com/scikit-learn-contrib/MAPIE README, https://github.com/ml-stat-Sustech/TorchCP tests `test_aps/raps/saps/lac/topk`). Risk: Jev's exact-0 rows (§0) put the gold label at the bottom of the ranking, which inflates set size. Jev-Calibration found Choice confidence uninformative below 95% (README takeaway 4), so sets may be wide.

**9. Conformal risk control / LTT.** Choose λ̂ = inf{λ : (n/(n+1))·R̂_n(λ) + B/(n+1) ≤ α} for a monotone loss (for example the false-drop rate). LTT generalises this to non-monotone risks through multiple testing (https://github.com/aangelopoulos/conformal-risk, https://github.com/aangelopoulos/ltt, both MIT). Data: labelled positives in the calibration split. Already tried (jev-9kmq). It failed for memory because the calibration split had 0 relevant rows (EVAL.md:3732), which is the exposure problem again. Use it only after #6/#14 show enough positives exist.

**10. Expected-loss decision.** a* = argmin_a Σ_s P(s|x)·L(s,a) over more than two actions. A kill-type action wins only with overwhelming posterior. Mirror process_triage@d06fa71/README.md:39 ("lowest expected loss under the policy's loss matrix"), :85 (robot mode needs `min_posterior` 0.95 + caps), :145-158 (8 actions; killing a useful process costs 500× leaving an abandoned one paused), :436 and :1270-1271 (e-BH/e-BY FDR across a batch of flags). Upgrades `gate`/`screen` to act/review/escalate (s1-rs GAP). Risk: the loss matrix is a policy input, not data, so expose it and never default it silently.

**11. Confident-ends filter.** Act only when p ≤ 0.1 or p ≥ 0.9 (or Choice confidence ≥ 0.9); the middle falls back to the incumbent. Upstream: accuracy when confident 99.6% (90% coverage) on Enron spam, 98.8% (82%) SST-2, 94.7% (88%) AG News, 89.9% (66%) Banking77. On their own pipeline, three "reject filter" decisions removed 25–60% of pages "with nothing lost", and a 135-row extraction question failed (68.6%) (https://github.com/onlyoneaman/jev-eval README). Labels come from outcomes, not another model. Risk: the sign of miscalibration decides whether a tail is safe. jev-exploration finding 4: p ≥ 0.9 hit 1.000 on their gradient but 73.9% on jev-phishing-bench.

**12. Isotonic.** PAV monotone step fit. Upstream: ECE of P(positive) 0.117 → 0.008 isotonic vs 0.052 Platt on 8,801 sentiment items; isotonic ≥ Platt from 20 to 5,280 calibration rows (https://github.com/AnthusAI/Jev-Calibration README takeaway 5). Our own small-n check was mixed (`work/jev-science/CALIBRATION.md:15-16`; msax AUC 0.35 → 0.65 only under Platt). Mirror implementations: franken_nlp/src/calibration.rs:463-545, frankensearch-fusion/src/calibration.rs:196-268. Risk: steps are flat on 0.01-quantised inputs; ties at 0.00/1.00 collapse bins.

**13. Venn-ABERS.** Fit isotonic twice with the test point labelled 0, then 1 → p0, p1. Merged p = p1/(1 − p0 + p1). The width p1 − p0 is the epistemic signal. Binary and multiclass (https://github.com/ip200/venn-abers, MIT). No gain number fetched (UNVERIFIED). Risk: it is computed per query, so cost is O(n log n) per call. That is fine at our corpus sizes.

**14. Prevalence by adjusted count.** p̂ = (q̂ − FPR)/(TPR − FPR), clipped to [0,1], where q̂ is the raw flag rate on organic traffic and TPR/FPR come from a dev split. QuaPy implements ACC/PACC/EMQ (https://github.com/HLT-ISTI/QuaPy README quickstart, BSD-3). BBSE is the multiclass analogue (https://github.com/flaviovdf/label-shift, BSD-3). Use it as the exposure pre-check so a bar is not written on ~0 positives. Risk: unstable when TPR ≈ FPR.

**15. Escalation-share threshold.** τ = the quantile of the router score that sends the target share to the strong model (`python -m routellm.calibrate_threshold --strong-model-pct 0.5` → τ = 0.11593 in their example; https://github.com/lm-sys/RouteLLM README). FrugalGPT cascade code: `src/FrugalGPT/llmcascade.py`, `scoring.py` (https://github.com/stanford-futuredata/FrugalGPT). The same output as the jevcal GAP (ideas-repos-b.md:49), so it adds little that is new.

**16. e-process / confidence sequences.** For a rate monitor, E_t = Π_{i≤t}(1 + λ(X_i − μ₀)); alarm when E_t ≥ 1/α. This is valid at any stopping time (https://github.com/gostevehoward/confseq README, Howard et al. 2021). Mirror: frankenjax@be8e83c3/crates/fj-ledger/src/lib.rs:378-388 (`EProcess { e_value, observations, rejection_threshold }`), frankensearch decision_plane.rs:8 (e-process gates). Our math doc already "copied the update" without gating on it (math-and-next-level-20260919.md:295). Risk: λ choice and a stated null are policy.

**17. Guard-model baselines.** PINT scores (Lakera's private 4,314-input set): Lakera Guard 95.22%, protectai deberta-v3-base-prompt-injection-v2 79.14%, Llama Prompt Guard 2 86M 78.76%, Prompt Guard v1 61.82% (https://github.com/lakeraai/pint-benchmark README). The PINT data is "a blend of public and proprietary data", so we cannot run it. Their YAML format (text/category/label) fits our corpus. Run the two open models against `upstream/Gaurav-Gosain/jev-sec-bench` (deepset/prompt-injections, 662 messages, README:12,27; jev-sec-bench's own result was 10 FP / 13 FN, README:40). Risk: contamination (the protectai v2 training list includes several public injection sets, HF card). Prompt Guard models are gated under the Llama license.

## 3. Per-project table (fetched URLs)

|project|URL|license (as fetched)|reuse: code vs idea|dep weight|maps to|verdict|
|---|---|---|---|---|---|---|
|**Jev-specific, not in our clones or awesome rows**|||||||
|jev-exploration (SamuelSacco)|https://github.com/SamuelSacco/jev-exploration|not shown in README fetch|idea: claims ledger; slope-transfer Platt; quantisation; noise floor; batching costs ~0.33 ms/question and questions cannot see each other (finding 8)|none|`calibrate`, `eval`, ask-bundle|ADOPT-IDEA|
|Jev-Calibration (AnthusAI)|https://github.com/AnthusAI/Jev-Calibration|none set (GitHub API `license: null`); do not copy code|idea: isotonic > Platt; binary `confidence` = 2·p_top − 1 (adds nothing beyond p_top); Choice raw confidence uninformative below 95%|none|`calibrate`, `explain`|ADOPT-IDEA|
|jev-ood-calibration (scienthoon)|https://github.com/scienthoon/jev-ood-calibration|MIT (API)|algo: endpoint floor, refit T per primitive (Noul T=0.66 underconfident, Choice/Score >1), ECE/noise-floor ratio|none|`calibrate`, `eval`|PORT-ALGO|
|jev-eval (onlyoneaman)|https://github.com/onlyoneaman/jev-eval|not checked (UNVERIFIED)|idea: confident-ends filter; outcome-joined labels; tail latency 10–35 s at 100 in flight|none|all Noul families; `doctor` timeout|ADOPT-IDEA|
|WorkflowEvals (typesafe-ai)|https://github.com/typesafe-ai/WorkflowEvals|not checked|data: 4 workflows, 705 cases on HF; `--reference` arm; resume and `--dry-run`|uv + HF hub (eval only)|`route`/`gate`/`score` eval|USE-AS-BASELINE|
|jev-skill calibration.md (wuyoscar)|https://github.com/wuyoscar/jev-skill/blob/main/skills/jev/references/calibration.md|not checked|idea: signal-naming table (Choice `probabilities` vs `confidence` vs Noul vs Score); record primitive/question/model/K with every threshold; workflow evals "use model-consensus references"|none|`explain`, `calibrate` receipts|ADOPT-IDEA|
|jev-harness (TypeSafeAI community org)|https://github.com/TypeSafeAI/jev-harness|MIT (README)|idea: receipt v1 with offline SHA-256 binding/replay; scripted mock totals labelled "not measurements of Jev"; fixed 0.8 threshold|pnpm/Node 22|`watch`/replay; `--fake` labelling|ADOPT-IDEA|
|jev-code (FrancoisChastel)|https://github.com/FrancoisChastel/jev-code|MIT (badge)|idea: peer product: same 5 tools (classify/check/score/rank/ask) across Claude Code, Codex, Pi, OpenCode + CLI; `setup` detects harnesses; hosts TypeSafe/OpenRouter/Vercel/OpenAI|npm|`install`, `--backend` hosts|ADOPT-IDEA (closest competitor)|
|jev-mcp (codaaiteam)|https://github.com/codaaiteam/jev-mcp|not checked|MCP classify/score/check/gate; third MCP peer|Node|MCP surface GAP (ideas-repos-b.md:51)|SKIP|
|cobusgreyling/Jev|https://github.com/cobusgreyling/Jev|MIT (search card)|showcase only|—|—|SKIP|
|stefafafan/jev (Go)|https://pkg.go.dev/github.com/stefafafan/jev@v0.1.2|MIT, published 2026-09-26|client; the page shows no synopsis|—|—|SKIP|
|**Calibration**|||||||
|net:cal|https://github.com/EFS-OpenSource/calibration-framework|Apache-2.0|algo list: HistogramBinning, IsotonicRegression, BBQ, ENIR, temperature/beta; metrics ECE/MCE/ACE/ENCE (doc tree)|numpy/scipy/torch|`calibrate`|PORT-ALGO (only BBQ if isotonic fails)|
|verified_calibration|https://github.com/p-lambda/verified_calibration|MIT|algo: debiased ECE, bootstrap uncertainties, scaling-binning; the paper shows "Platt scaling is less calibrated than reported"|numpy|`eval`|PORT-ALGO (#2)|
|venn-abers|https://github.com/ip200/venn-abers|MIT|algo #13|sklearn|`calibrate`|PORT-ALGO|
|relplot (Apple)|https://github.com/apple/ml-calibration|Apple sample-code license (custom)|idea: smECE (kernel-smoothed) with bootstrap CI|numpy/matplotlib|`eval` report|ADOPT-IDEA|
|**Conformal**|||||||
|MAPIE|https://github.com/scikit-learn-contrib/MAPIE|BSD-3|algo: conformal classification sets, risk control incl. LLM-as-judge, exchangeability tests|numpy ≥1.23, sklearn ≥1.4|`route`, `gate`|PORT-ALGO (#8, #9)|
|crepes|https://github.com/henrikbostrom/crepes|BSD-3|idea: Mondrian (class-conditional) categorizer, p-values per class, exchangeability-test module|numpy|`screen`/`gate` (imbalanced)|ADOPT-IDEA (jev-9kmq already class-conditional)|
|TorchCP|https://github.com/ml-stat-Sustech/TorchCP|LGPL-3.0|algo reference: APS/RAPS/SAPS/LAC/top-k scores; LLM example `llm_ConformalLM_TriviaQA.py`|torch|`route`|SKIP import (LGPL + torch); read for algos|
|puncc|https://github.com/deel-ai/puncc|MIT (badge)|same algo family as MAPIE|numpy/sklearn|—|SKIP (redundant)|
|conformal-risk|https://github.com/aangelopoulos/conformal-risk|MIT|algo #9|torch (examples)|`gate`, `memory`|PORT-ALGO|
|ltt|https://github.com/aangelopoulos/ltt|MIT|algo: Learn-then-Test multi-threshold risk control|notebooks|`calibrate --target`|PORT-ALGO (after #6/#14)|
|awesome-conformal-prediction|https://github.com/valeman/awesome-conformal-prediction|Other|index only|—|—|SKIP|
|**Labels / weak supervision / few-label inference**|||||||
|snorkel|https://github.com/snorkel-team/snorkel|Apache-2.0|idea: LabelModel over labelling functions; team "now focusing their efforts on Snorkel Flow"|heavy|`cases` bootstrapping|ADOPT-IDEA|
|cleanlab|https://github.com/cleanlab/cleanlab|Apache-2.0|algo #5|sklearn+|`cases lint`|PORT-ALGO|
|crowd-kit|https://github.com/Toloka/crowd-kit|Apache-2.0 (LICENSE)|algo #7 (DS, GLAD, MACE)|pandas/numpy|`eval --log`|PORT-ALGO|
|skweak|https://github.com/NorskRegnesentral/skweak|MIT|spaCy weak supervision for NER|spaCy|—|SKIP|
|WRENCH|https://github.com/JieyuZ2/wrench|Apache-2.0|weak-supervision benchmark|torch|—|SKIP|
|ppi_py|https://github.com/aangelopoulos/ppi_py|MIT|algo #6 (`ppi_mean_ci`, power analysis, label-shift tests)|numpy/scipy/statsmodels|`watch`, exposure|PORT-ALGO|
|QuaPy|https://github.com/HLT-ISTI/QuaPy|BSD-3|algo #14 (ACC, PACC, EMQ)|sklearn|exposure gate|PORT-ALGO|
|label-shift (BBSE)|https://github.com/flaviovdf/label-shift|BSD-3|algo: black-box shift estimation|notebooks|`watch` drift|ADOPT-IDEA|
|confseq|https://github.com/gostevehoward/confseq|MIT|algo #16|C++/pybind|`watch`|PORT-ALGO (math only)|
|**Routing / cascades**|||||||
|RouteLLM|https://github.com/lm-sys/RouteLLM|Apache-2.0|idea: `calibrate_threshold --strong-model-pct`; routers mf, sw_ranking, bert, causal_llm; claims "up to 85%" cost cut at 95% GPT-4 quality on MT Bench|litellm, embeddings|`effort`|ADOPT-IDEA|
|FrugalGPT|https://github.com/stanford-futuredata/FrugalGPT|Apache-2.0|idea: scorer + cascade + cache (`llmcascade.py`)|notebooks|`effort`, `route`|ADOPT-IDEA|
|RouterBench|https://github.com/withmartian/routerbench|MIT|multi-LLM routing benchmark|—|`effort` eval|SKIP (no Jev arm; our router evidence is LOST)|
|**Eval CLIs**|||||||
|promptfoo|https://github.com/promptfoo/promptfoo|MIT|idea: declarative YAML cases + assertions, `promptfoo eval`/`view`, CI integration|npm, large|`cases`, `eval` file format|ADOPT-IDEA|
|inspect_ai|https://github.com/UKGovernmentBEIS/inspect_ai|MIT|idea: model-graded scorers, extension packages|Python, large|`eval`|ADOPT-IDEA|
|lm-evaluation-harness|https://github.com/EleutherAI/lm-evaluation-harness|MIT|few-shot LM tasks; logprob-oriented|large|—|SKIP|
|deepeval|https://github.com/confident-ai/deepeval|Apache-2.0|LLM-judge metrics|large|—|SKIP|
|openai/evals|https://github.com/openai/evals|Other|registry-of-evals pattern|large|—|SKIP|
|**Guardrails**|||||||
|PurpleLlama|https://github.com/meta-llama/PurpleLlama|Other|"tools to assess and improve LLM security" (CodeShield visible in tree)|—|`screen`, `diff`|SKIP (models below are the reusable part)|
|Prompt-Guard-86M|https://huggingface.co/meta-llama/Prompt-Guard-86M|llama3.1, gated|baseline (PINT 61.8%)|transformers|`screen` eval|USE-AS-BASELINE (weak)|
|Llama-Prompt-Guard-2-86M|https://huggingface.co/meta-llama/Llama-Prompt-Guard-2-86M|other (Llama 4), gated; 8 languages|baseline (PINT 78.8%)|transformers|`screen` eval|USE-AS-BASELINE|
|protectai deberta-v3 injection v2|https://huggingface.co/protectai/deberta-v3-base-prompt-injection-v2|apache-2.0|baseline (PINT 79.1%), ONNX available|transformers/onnx|`screen` eval|USE-AS-BASELINE|
|rebuff|https://github.com/protectai/rebuff|Apache-2.0|idea: canary-token leak check alongside a classifier; README: "still a prototype"|TS|`screen`|ADOPT-IDEA (canary only)|
|llm-guard|https://github.com/protectai/llm-guard|MIT|README: "THIS PROJECT HAS BEEN ARCHIVED"|—|—|SKIP|
|NeMo Guardrails|https://github.com/NVIDIA-NeMo/Guardrails|Apache-2.0 (badge)|Colang rail framework|heavy|—|SKIP|
|PINT benchmark|https://github.com/lakeraai/pint-benchmark|MIT|YAML case format; leaderboard; data not public|notebook|`screen` eval format|ADOPT-IDEA|
|**Drift**|||||||
|alibi-detect|https://github.com/SeldonIO/alibi-detect|Business Source License (LICENSE: Apache only after a 4-year change date; production use limited)|idea only: KS/MMD/classifier drift|TF/torch|`watch`|SKIP (license)|
|evidently|https://github.com/evidentlyai/evidently|Apache-2.0|idea: reports vs test suites, "100+ metrics"|heavy|`watch`|SKIP (port a score-histogram KS/PSI instead)|

Count: 50 projects with URLs fetched this session. kataras/jev (Go client) appeared only as a search snippet and was not fetched.

## 4. Local mirror findings (Jeffrey Emanuel patterns)

I ran `fh suggest` (ledger STALE: `ledger_age_hours=625.8`, threshold 26). I then re-checked every path on disk at the commit shown.

- **Calibration module blueprint**: franken_nlp@8f8ae35/src/calibration.rs. Preregistered ECE bins (:18); disjoint digested splits (:142-232); temperature by golden-section (:385-456); PAV isotonic (:463-545); `SelectiveRisk` threshold/accepted/abstained (:570-580); seeded bootstrap CIs (:583-748); split-conformal that refuses without an `ExchangeabilityMemo` (:869-1030, "None is a typed refusal" :917); validity window + `ShiftPolicy` (:1065-1116); digest-bound artifact (:1119-1350); `CalibrationState` and abstain = exit 0 (:1353-1384). This is the closest existing design for `calibrate` + `explain`. Port the structure (#4), not the crate.
- **Calibrator trait + fallback reasons**: frankensearch@d1cb86e1/crates/frankensearch-fusion/src/calibration.rs:39 (`ScoreCalibrator`), :91/:138/:196 (Temperature/Platt/Isotonic), :363/:402 (ECE/Brier), :425-460 (serde-tagged `CalibratorConfig`). crates/frankensearch-core/src/decision_plane.rs:262-344 (status + `max_ece` 0.05) and :410-444 (reason-code namespace incl. `conformal.coverage.violation`).
- **Decision under a loss matrix + robot guardrails**: process_triage@d06fa71/README.md:39, 85, 110-116, 145-158, 436, 1270-1271 (#10).
- **Robot mode contract**: coding_agent_session_search@306d6e25/README.md:47-76 ("Never run bare `cass` in an agent context"; `capabilities --json`, `robot-docs guide|schemas`), :122 (JSON contract pinned by golden files under `tests/golden/robot/`; a field rename fails the suite), :909-919 (`robot-docs commands|schemas|examples|exit-codes`). beads_viewer@6c6efa15/README.md:117-133 (`--robot-*` only; TOON is "smaller only for wide tabular payloads… Check with --stats before adopting"). For our `--json`: a golden schema per verb + a `robot-docs exit-codes` page. That fits cli-ergonomics-spec without new deps.
- **Bandits**: meta_skill@2abb3035/src/suggestions/bandit/bandit.rs:13-26 (`observation_decay` 0.99), :67-81 (Beta-posterior Thompson draw), :149-183 (persisted state); contextual.rs:5, :95-102. frankenterm@fafa06e66/crates/frankenterm-core/src/ucb1_bandit.rs:1-30 (UCB1 r̄ + √(2 ln N / n_a), with when-not-to-use notes against static preference). Rank 19: no dense reward on our side.
- **Conformal + e-process primitives**: mcp_agent_mail_rust@21a25c2b/crates/mcp-agent-mail-core/src/conformal.rs:55-151 (windowed split conformal, quantile index ⌈(n+1)·coverage⌉ at :146-149, `empirical_coverage` :210). frankensqlite@fc1f6a537/crates/fsqlite-harness/src/score_engine.rs:391-400 (`ConformalBand`). frankenjax@be8e83c3/crates/fj-ledger/src/lib.rs:378-388 (`EProcess`).
- **Versioned eval fixtures**: eidetic_engine_cli@fdbe771d2/src/eval/runner.rs:1-36 (`ee.eval_fixture.v1`, `ee.eval.report.v2`, separate expectation schemas). Pattern for `cases` files: a schema string in every fixture and report.

## 5. Risks across the board

- Most upstream Jev calibration evidence is one model version (`jev-1.13.0`) with one dataset per repo. Every gain in §1 is UNVERIFIED on our tasks until the named test runs.
- The "~0 organic positives" failure (PRODUCT.md:75-77) blocks every label-hungry method (#3, #8, #9, #12, #13). Run #6/#14 first to learn whether positives exist.
- Jev's 0.01 quantisation and exact endpoints (§0) break log-based fits and rank-based conformal scores. Apply #1 before any of #3, #8, #12.
- Licences: alibi-detect is BSL, TorchCP LGPL, Jev-Calibration has no licence, relplot uses a custom Apple licence. Re-implement from the papers; do not vendor.
