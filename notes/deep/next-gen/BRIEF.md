# Brief: next-gen uses for Jev (bead `jev-jy7t`)

Pane 1 (AmberWillow), 2026-09-24. Input for a two-wizard duel: Claude (pane 3) and Codex
gpt-5.6-luna (pane 4). Read this whole file, then the two source reports it condenses:
[`ledger-20260924.md`](ledger-20260924.md) (what this repo measured, with path:line cites) and
[`outside-scan-20260924.md`](outside-scan-20260924.md) (what the ecosystem and the literature did,
with URLs). Numbers below are copied from those reports; go to them for the citation.

## 1. The ask

Joshua, verbatim: *"spend more time finding really next-gen uses for jev instead of running it
locally"*. Then, listing ten ecosystem projects: *"none of these ten generate a single word of text.
every one of them returns a number against an answer someone already defined"*.

**Next-gen means:** a use that only works, or only pays, because a calibrated, typed judgment costs
about $0.02 per 1,000 answers and about 130 ms, can be asked many times in parallel over one state,
and gives nearly the same answer twice. Asked per frame, per step, per row, per candidate, per
word, per commit. **Not** another benchmark where Jev re-labels a dataset a TF-IDF or a regex
already labels.

## 2. The fit test every idea must pass

Joshua refers to a "three-question test from the article". Nobody here has found that article
(two web searches, a doc-mirror grep, and a scout's 17-source search; X is not searchable from
here). **Until he supplies it, use this stand-in, which is ours, not the article's:**

1. **Defined answers.** Is every judgment a Choice, Score or Noul over options our code owns before
   the call? (If the value must be written, not chosen, it is not a Jev use.)
2. **Only because it is cheap, fast or stable.** Name the rate, latency, volume or stability the
   use needs, and show with the numbers in section 3 that an LLM (Haiku at $0.95-1.43 per 1,000
   answers, ~4 s p50 on a 77-way Choice, and 9-12 of 400 SciFact or 80-97 of 500 SST-5 answers
   flipped between identical runs) cannot meet it. "An LLM could do it
   too, just more slowly" is not next-gen.
3. **An outcome grades it.** Name the ground truth that someone other than us produced: a game
   score, a chess engine, a task checker, public qrels, a market fill, a test suite, a later human
   action. Labels we write ourselves are the weakest evidence this lane has (NEGATIVE_EVIDENCE R28).

Plus this lane's own filters, each learned the hard way:
- **Prevalence.** State the base rate. Jev lost at 9% (toxicity) and was unusable at 0.016%
  (vetoes). It wins on shortlists and sets with 40-50% positives.
- **Does the cheap baseline collapse?** Jev wins where BM25, keywords or TF-IDF collapse (negation,
  injection, distribution shift) and loses where the label lives in the tokens (phishing regex,
  keyword triage, always-bash).
- **Check NEGATIVE_EVIDENCE.md** for a killed version of your idea (R1-R100) and say what is
  different.

## 3. Jev, as measured here (ledger sections 1-3)

- **Latency:** p50 127-162 ms short state; live hook p50 141 ms with no measurable tool-path cost.
  Big states are slow: a 20-passage state is 8,435 input tokens per call.
- **Cost:** $0.042 per million input tokens, output free: $0.016-0.029 per 1,000 answers, 33-88x
  cheaper than Haiku at list price. 18,000 rerank calls cost $0.597.
- **Throughput:** ~80 calls/s at concurrency 16 with 0 failures over 18,000 calls.
- **Stability:** flipped answers between identical runs 0-2 on SciFact, 0-1 of 662 on injection,
  6-8 of 500 on SST-5, versus 9-97 for Haiku and grok on the same rows. Token counts are
  deterministic per request.
- **Calibration:** good on verification and injection (SciFact Brier 0.071 vs Haiku 0.100; FEVER
  ECE 0.038 vs 0.066; held-out ECE 0.061). Poor on phishing (0.161), code vulnerabilities (0.179),
  toxicity (0.267), and **pure chance**: it said "1" on all 400 die rolls at ~83% (outside scan).
  So probabilities need checking per question before a threshold or a guarantee rests on them.
- **Large label sets:** Choice takes up to 255 options. At 77 intents Jev won 2,467 vs 2,267 while
  Haiku's structured output failed 993 of 993 at that size; 150 options reached 90.2%.
- **Against LLM incumbents** it usually ties on accuracy and wins on calibration, stability, cost
  and label-set size. Cascading from Jev to Haiku was NOT USEFUL; escalate to a human instead.

## 4. What is already built and measured

- **Wins or ties:** injection (640 vs Haiku 584), SciFact and FEVER claim verification (accuracy
  tie, calibration win), BEIR SciFact rerank (nDCG@10 0.762-0.769 vs BM25 0.676), NevIR negation
  (replay 0.7115), Banking77 (77 intents), CLINC150 with abstention, SST-5/STS-B/Yelp scores,
  phishing as 5 probe features feeding a logistic fit (AUROC 0.987 vs 0.685 for one verdict).
- **Losses:** grep-corpus rerank, phishing verdict, toxicity, compaction keep rules (R99, R100),
  safety vetoes, tool selection vs always-bash, the gate on held-out fleet commands (recall 22/33,
  three unseen harm shapes caught 0 of 11), claim checks on numbers and close reasons.
- **Wired into omp:** tools `jev_rerank`, `jev_claim_check`, `jev_flag`, `jev_screen` (a handful
  of real calls between them); the bash gate hook (2,501 rows in one day); the compaction hook
  (report-only). None of the tools is used in daily agent work yet.
- **Use-case map coverage** (`docs-mirror/typesafe/concepts/use-case-map.md`): nearly everything
  tested sits in Harness Engineering and Universal Verification. **Untested categories:**
  Real-time applications (beyond smokes of N<=10) and AI Map Reduce over Big Data. **Untested
  automation cells:** Recruiting, Lead generation, Insurance claims, Financial crime, Legal and
  compliance, E-commerce marketplaces, Advertising, Gaming, Risk assessment, Demand forecasting.
  **Decision shapes tested only as smokes:** Search, Retrieval, Structured Data Extraction.

## 5. What others built (outside scan A0-A3)

Joshua's ten, with what each README actually measured (corrections checked by pane 1 where
marked):

| Project | Loop | Measured |
|---|---|---|
| jev-trader | one Monad block (~300 ms), Choice buy/sell | timings only, and **with the mock model**; no P&L, no Jev accuracy |
| jev-ultrafast | one browser step, operation + target Choices | 3/3 runs both versions; 1,092 -> 101 browser protocol calls; our oracle 20/20 |
| jev-drone | ~2.5 Hz tactical Choice inside faster loops | one run 17.7 m vs 77.5 m; an earlier 3-seed test showed no advantage |
| jev-doom-agent | 4 Choices every 400 ms | nothing |
| jev-t-rex-runner | Choice per obstacle | nothing |
| typesafe-chess | Choice per legal move as policy, Score as value, inside MCTS | search lost 25 cp/move to Stockfish vs 168-190 for one call; 9/20 best moves vs 5/20; won 2-0. No "overruled half" figure exists (pane 1 checked) |
| tax-doc-classifier | Choice over 230 forms per page | 0 wrong on 314 + 753 pages; 38 of 753 (5.05%) below its 0.95 gate, all correct; $0.00115 vs $0.039 per page (pane 1 checked) |
| killmyidea | 8 Scores per idea | nothing published |
| jev-curate | Noul/Score per dataset row | 24 rows/s on a mock bench; our run: its default rule rejected 30/30 |
| pg-jev | Noul per table row, 20 rows per request | 2,000 rows in 3.5 s for $0.012; accuracy 100% at 1-20 rows per request, 77-94% at 80 |

Beyond the ten (author claims unless noted): jev-skip (77% of SponsorBlock sponsor seconds, $0.0008
per video); NanoJev (128/128 on ViZDoom Basic vs Jev 56/128);
OpenRouter's Banking77 test (Jev 81.0% vs Opus 5 84.4% at 175 ms vs 2,266 ms p50); ayautomate
(answer at confidence >= 0.80, send the rest to a big model: the big model's accuracy at about a
quarter of the cost); streaming speech judged word by word (dasheng), a text box that becomes the
right UI as you type (shapeshift), GPT-6 reasoning effort picked per task (Astra-Ares). 637 repos
turned up in search; 578 are in neither awesome-jev list.

**TypeSafe's own numbers** (evals.typesafe.ai): Jev 67.8% / $0.0004 / 0.4 s against the best
comparator 74.1% / $0.0836 / 23.3 s. Jev is not the most accurate; it is the one you can afford to
ask thousands of times.

## 6. Leads from the two scouts (starting points, not answers)

**From the literature (outside scan B, C):**
1. **Jev as the policy and value inside a search** (typesafe-chess; Koh et al. +39.7% relative on
   VisualWebArena; Agent Q 18.6% -> 81.7%). One call gives a prior over up to 255 children plus a
   value. Trap: absolute Scores saturate once one side is ahead; judge relatively.
2. **"Ask when unsure" with a guarantee** (KnowNo-style conformal sets over Choice options). Nobody
   has done this with Jev; everyone picks thresholds by hand.
3. **Per-step reflexes in agent loops, aimed at frequent failures** (loops, false "done" claims;
   step-level blame is at 14.2% in Who&When, so there is headroom).
4. **Semantic cache hits:** "does this cached answer satisfy this new prompt?" (vCache: learned
   thresholds, up to 12.5x more hits). No Jev project does this.
5. **Phrase-by-phrase judgments on live media and voice** (sponsor skipping, streaming speech,
   reply / wait / backchannel turn-taking).
Also listed: adaptive retrieval (retrieve or not), weak supervision (each Noul as a labeling
function with a probability), FineWeb-Edu-style data curation at corpus scale, routing.

**From our own evidence (ledger section 6):** a probe-vector feature factory (many cheap Nouls per
item, fit a model on top); a deterministic judge as a regression oracle for agent or model
behaviour in CI, memoized by state hash; confident bulk automated, tail to a human; a cheap filter
in front of Jev to raise prevalence; corpus-scale map-reduce (a million answers ~ $29); negation
and contradiction checks between records; very large label sets (catalogues, taxonomies);
real-time control loops with an outcome label at N >= 100; live checking of claims in generated
text.

## 7. Constraints

- **Comparators:** a free OpenRouter model (`:free` id) or nothing. No Anthropic, no grok/xAI, no
  paid OpenRouter (AGENTS.md "No paid comparisons"). No local models (Joshua, this unit).
- **Jev live calls are allowed** on the TypeSafe credits; say what an experiment would spend.
- **Ground truth must exist today** or be produced by an outside process we do not grade
  (a game, an engine, a test suite, a later human action).
- Mission, from AGENTS.md: validate Jev, build tools from what survives, liven an omp surface,
  dogfood it, keep the README a stranger can run. An idea that also becomes something our own
  agents use every day is worth more, but it is not required.

## 8. What to write, per idea

For each of your top ideas:
1. **Name and one-sentence pitch.**
2. **The loop:** what triggers each judgment, how often, and the questions (type, options).
3. **Fit test:** answers to section 2's three questions, with numbers from section 3.
4. **Why this is next-gen:** what it makes possible that was not possible or not affordable before.
5. **Ground truth and prevalence:** the dataset, environment or outcome (URL or path), and the
   base rate.
6. **Cheapest falsifying experiment:** the preregistrable bar, N, calls, estimated spend, and what
   result would kill the idea.
7. **Map location:** use-case map category and decision shape.
8. **Nearest dead relative:** the NEGATIVE_EVIDENCE row or losing result it resembles, and why it is
   different.
9. **First build:** the smallest thing that would run, and whether it could become an omp surface.
