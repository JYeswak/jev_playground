# Codex cross-score of `WIZARD_IDEAS_CC.md`

Bead: `jev-jy7t.1`. Date: 2026-09-24. This is a candid design score, not a Jev ruling.
No Jev calls, local LLMs, or comparator calls were made.

## Verdict first

Claude's five are materially better than ordinary “ask Jev to classify a game state” ideas. The
best is PokéJev because the clock is the actual failure mode, legal actions are code-owned, and the
published opponent is a real LLM-agent row rather than a toy classifier. The weakest is the
BrowseSafe shield: it is useful and cheap enough to test, but BrowseSafe already does the mechanism
with a trained model, and this lane's own injection-on-tool-output failures make the transfer risky.

| Rank | Idea | Score / 1000 | Decision |
|---:|---|---:|---|
| 1 | PokéJev clock-proof expectiminimax | **790** | Keep; first candidate to falsify |
| 2 | Jev-PUCT for Jericho / MC-DML replacement | **705** | Keep, but repair Mac/path and cost accounting |
| 3 | Training-free V-Droid verifier slot | **660** | Keep as a Pareto experiment, not a headline-SR claim |
| 4 | Certified semantic step monitor / CURA feed | **610** | Keep for omp, narrow the benchmark claim |
| 5 | BrowseSafe injection shield | **555** | Keep only as a cheap public-data probe; do not ship without a low-FP result |

The scores deliberately include deductions for unlike-for-like SOTA comparisons, scripted floors,
Mac blockers, and experiments whose proposed spend is not credible.

## Citation checks performed

I checked these CC citations against the source pages before scoring:

1. **PokéChamp, arXiv:2503.04094.** The source distinguishes the **84%** GPT-4o win rate
   against Abyssal from the **76%** result against PokéLLMon; they are not one combined benchmark.
   The paper is <https://arxiv.org/abs/2503.04094> and the OpenReview PDF is linked from the
   search result. CC is right on the two rates, but its “about a third of human-ladder games lost
   on time” needs the paper's ladder paragraph, not the 84/76 table.
2. **MC-DML, arXiv:2504.16855.** The paper reports Zork1 **48.66 +/- 1.89**, Deephome **67.00
   +/- 1.41**, and Detective **346.67 +/- 9.43** over three runs. CC's values are correct, but
   its cost arithmetic is an estimate, not a source number. Source:
   <https://arxiv.org/abs/2504.16855>.
3. **V-Droid, arXiv:2503.15937.** The source reports **59.5% AndroidWorld success**, **4.3 s
   per step** overall, and about **0.7 s per verifier decision**. CC's numbers are correct. Source:
   <https://arxiv.org/abs/2503.15937>.
4. **CURA, arXiv:2608.27808.** The source separates **42.3%** early failure detection at a
   realized **0.066** false-alarm rate from retrospective **0.828 AUROC**; CC correctly lists
   all three but should not combine them into one guarantee. Source:
   <https://arxiv.org/abs/2608.27808>.
5. **BrowseSafe, arXiv:2511.20597 / HF dataset card.** The test set is **3,680** rows and the
   published model reports **F1 0.904, precision 0.978, recall 0.841, balanced accuracy 0.912**.
   Source: <https://arxiv.org/abs/2511.20597> and
   <https://huggingface.co/perplexity-ai/browsesafe>.

These checks support the numerical inputs, not the proposed Jev outcomes.

## 1. PokéJev — 790/1000 — KEEP, first falsification

### Overall judgment

**Good and smart.** This is the only CC idea where the latency failure is directly documented in
the target agent: the proposed system does not merely make a classifier cheaper; it buys search
breadth inside a human game clock. It also has a clean local simulator, a non-authoritative game
engine, legal action sets, and a realistic 50% win-rate base rate. Deduct 210 points because the
CC proposal overstates cost precision, its stage-A replay bar is a policy-prediction proxy rather
than win rate, the local setup is not currently proven in this lane, and the claimed public-ladder
comparison has protocol risk.

### (a) Novel mechanism and closest published work

Mechanism novelty: **8.5/10.** PokéChamp already uses LLM action selection, opponent modelling and
value judgements; Monte Carlo search with a language prior is also established. The novel part is
the composition: Jev's calibrated Choice distribution becomes the chance-node prior, relative
Choice compares sibling leaves, and code uses the remaining clock to choose search depth. That is
meaningfully different from “one LLM call per turn.”

Closest work: PokéChamp (arXiv 2503.04094), MC-DML (arXiv 2504.16855), and the CC file's own
MC-DML-relative-search idea. The mechanism is not unexplored enough to claim invention; it is a
credible Jev-specific recombination.

### (b) Section 2 fit test

1. **Defined answers: decisive PASS.** The legal move list is constructed by poke-env; the
   opponent candidate list is bounded by revealed moves, legal switches and fixed usage priors;
   the sibling comparison options are `A/B/even`. Jev never invents a move or damage number.
2. **Only because cheap/fast/stable: decisive PASS, pending measurement.** The paper's stated
   failure mode is time, and Jev's ~130 ms request is plausibly inside the per-turn clock. The
   CC estimate of 300 leaves per turn is not measured and should be replaced by a hard call budget,
   token log, 429 count and wall-clock receipt. Stability matters for a transposition cache, but
   the good Jev stability numbers came from verification tasks, not Pokémon states.
3. **Outcome grades it: decisive PASS.** The Showdown engine grades win/loss, legal action and
   clock expiry. Public replays grade action prediction separately. No self-authored labels are
   required.

### (c) SOTA comparison

**Partly like-for-like; CC correctly exposes the problem but does not solve it.** The 84% Abyssal and
76% PokéLLMon numbers are source-backed and useful LLM-agent references, but they are separate
opponents/evaluations, not one SOTA point. The public ladder is a different population and clock
protocol. The proposed Stage B can fairly compare to PokéChamp only if it uses the same Gen 9 OU
rules, team set, opponent pools, action legality, timeout rules and battle count. “Beat 84%” is
plausible against Abyssal but not enough to claim a general SOTA break. The Metamon specialist
ceiling is explicitly a different class and should remain a stretch row.

### (d) Mac feasibility

**Conditional PASS.** The Node Showdown server is a plausible arm64 local environment, and the
state is JSON. The local-env probe did not run PokéChamp or Showdown, so “runs on this Mac” is not
yet evidenced by the probe. The install command in CC is concrete enough to try. No API key is
needed for the replay scorer; live battles require the key later.

### (e) Cheapest experiment

**Sound shape, unsound cost/sequence unless tightened.** Stage A is cheap and useful, but action
prediction does not prove search wins battles. Its 2,000-turn bar is a valid kill gate for the
prior; it must not be reported as a win. Stage B at 200 battles with several opponents is the
real experiment and should log calls/tokens, not use the rough “$30” estimate. A proper first
experiment is:

- 2,000 held-out replay turns, fixed questions, one Jev call per state, cost estimated before run;
- 50 local battles per opponent for plumbing only;
- preregister 200 battles only after Stage A passes;
- kill at <70% vs Abyssal, >1% timeout losses, or no gain over a deterministic legal-action floor.

The bar can fail. That is a strength.

### (f) Payoff vs complexity

**High payoff / medium-high complexity.** If it passes, this becomes a public demo with a compelling
clock metric and a reusable batched search engine. If it fails Stage A, the loss costs little. If it
passes Stage A but loses battles, the result still identifies whether the prior or value evaluator is
the dead component. Worth doing first.

## 2. Jev-PUCT for Jericho — 705/1000 — KEEP, but repair the path

### Overall judgment

**Strong research idea, less attractive product.** It targets a real API limitation—retired LLM
log-probabilities—and Jev natively returns distributions over valid actions. MC-DML supplies an
unusually clean same-protocol baseline. Deduct for the proposed 56M-token / $2.4 per run estimate,
the high total experiment spend, long-horizon sparse rewards, and a Mac feasibility conflict in the
research set.

### (a) Novel mechanism and closest published work

Mechanism novelty: **7.8/10.** MC-DML already uses a language-model prior in PUCT, and the CC idea
explicitly ports that slot. The Jev-specific novelty is replacing token log-probs with calibrated
Choice probabilities and batching 16 nodes in one request. Relative sibling evaluation is sensible
because the source and typesafe-chess both warn about absolute-score saturation.

Closest work: MC-DML (2504.16855), MC-LAVE-RL and typesafe-chess. This is a strong adaptation, not a
new search algorithm.

### (b) Section 2 fit test

1. **Defined answers: PASS.** Jericho supplies valid actions; Choice options are code-owned.
2. **Cheap/fast/stable: PASS with a serious cost caveat.** Jev is far cheaper than a large LLM
   prior, and batching makes search possible. But 80k node priors per game is not “cheap” by this
   lane's normal budget, and 130 ms still makes every real step multi-second. Stability may help
   caching, but identical text-state cache hits must be measured on this distribution.
3. **Outcome grades it: PASS.** Jericho score and walkthrough completion are external GT.

### (c) SOTA comparison

**The best of CC's five.** The MC-DML table is like-for-like if Jev uses the same valid-action
handicap, games, step limit, simulation budget, reward and seeds. CC correctly refuses to compare
directly to TALES/TextQuests protocols. The proposed bar is appropriately tiered: first match the
MC-DML no-memory ablation, then challenge MC-DML's full scores. It could beat the **no-logprob**
LLM row because Jev supplies the missing prior, but beating MC-DML itself is uncertain.

### (d) Mac feasibility

**Partial, not PASS.** The local probe says Jericho/TextQuests are Linux-only, while CC proposes
arm64 Docker. Docker is present, but that is not the same as the game assets, Jericho build and
score harness being verified on this Mac. The idea must carry `MAC-PARTIAL` until a no-key Docker
smoke runs. Do not call it local-ready from `docker info` alone.

### (e) Cheapest experiment

**Technically sound but too expensive as written.** Three games x three runs is a reasonable
falsifier, and the uniform/random/do-nothing floors are correct. The cost estimate should be
recomputed from actual state tokens after a 20-step probe; the proposed $21 can be wrong by an order
of magnitude if each node repeats 700-token context plus 16 questions. The clean first bar is:

- Zork1 only, 3 seeds, 50% of MC-DML simulations, 10k-answer hard cap;
- compare uniform PUCT, Jev prior, and Jev prior + relative leaf;
- kill if Jev is not +5 score over uniform on Zork1 and does not beat MC-DML's no-memory ablation.

### (f) Payoff vs complexity

**Medium-high payoff / very high complexity.** It could be a publishable result about typed
probability replacing unavailable log-probs, but it does not immediately become an omp tool. Keep as
a second experiment after PokéJev; do not spend the full $21 before the small Zork1 gate.

## 3. V-Droid verifier slot — 660/1000 — KEEP as a Pareto experiment

### (a) Novel mechanism and closest published work

Mechanism novelty: **5.5/10.** The closest published system already does the central thing: V-Droid
enumerates mobile candidates and uses a trained verifier to rank them. GTA1, GUI-Actor and the
step-level cascade also cover proposal selection or verification. Jev's real novelty is zero-shot,
typed Choice over the candidate set, parallel termination Noul, and selecting quoted input spans
without generation. That is a useful mechanism, but not a new verifier concept.

### (b) Section 2 fit test

1. **Defined answers: PASS.** Accessibility elements and code-extracted input spans are finite.
2. **Cheap/fast/stable: PASS for latency/cost, not yet for correctness.** V-Droid is 4.3 s/step
   overall and 0.7 s/decision; Jev can plausibly be 20–30x faster per decision. The text-only
   state is exactly the right Jev input. The 59.5% success target is not guaranteed; Jev's large
   Choice zero-mass risk (5.9% at 77 labels) warns against assuming all element lists work.
3. **Outcome grades it: PASS.** AndroidWorld checkers grade task completion.

### (c) SOTA comparison

**Mostly like-for-like if the observation and step budget are frozen.** V-Droid is text/accessibility
candidate verification and 59.5% on AndroidWorld, while the overall 2026 AndroidWorld board includes
screenshot systems and self-reported 100% rows. CC correctly separates those categories. It could
beat V-Droid on success/second even if it loses raw SR; its proposed “>=29.8% plus <=300ms” bar is a
Pareto floor, not a SOTA victory. That distinction should be headline text.

### (d) Mac feasibility

**Weak partial.** The report says AndroidWorld has a macOS emulator path but warns about ARM and the
probe did not run it. The proposed `brew install` and Android SDK changes also need a separate
approval and are not zero-risk. Do not claim this environment runs on the Mac until the emulator
boots and one task checker passes keyless. The underlying verifier can first be tested on a static
candidate/action fixture.

### (e) Cheapest experiment

**Sound but too large as first move.** 116 tasks x 3 seeds and 21M tokens is a serious spend for a
hypothesis whose mechanism is already close to V-Droid. Start with 20 tasks and a recorded
accessibility-tree replay, 300 calls, and a bar of >=90% candidate agreement with V-Droid labels
where available plus p50 <=300ms. Only then run all 116. A full run can fail on emulator setup
before testing Jev; that is an infrastructure blocker, not a green result.

### (f) Payoff vs complexity

**Medium payoff / high complexity.** A successful Android verifier would be a valuable product
surface, but it is not the best Mac-first path. Merge the mechanism with MacArena AX trees or
MiniWoB before paying for Android emulator setup. Score reflects that the stated first build is not
currently local-proven.

## 4. Certified semantic step monitor — 610/1000 — KEEP for omp, narrow the claim

### (a) Novel mechanism and closest published work

Mechanism novelty: **5/10.** CURA already supplies the sequential CUSUM alarm; the step-level
cascade already trains stuck/milestone detectors; Automata from traces is a stronger trained
trajectory predictor. The genuinely useful delta is typed semantic observations with no training
set feeding an existing certified alarm, plus a done-claim Noul.

### (b) Section 2 fit test

1. **Defined answers: PASS.** Stuck, progress and done are binary questions over trace text.
2. **Cheap/fast/stable: PASS conditionally.** The monitor runs at 130 ms while agents take seconds,
   and the API price is far below a frontier overseer. But the proposed 4k-token/step state is large
   and the 32k state budget constrains history. The state must be compacted deterministically.
3. **Outcome grades it: PASS.** OSWorld task checkers and released trajectories supply labels.

### (c) SOTA comparison

**Not fully like-for-like as written.** CURA's 0.828 AUROC, 42.3% early catch and 0.066 FAR are
three distinct metrics on its own pipeline. CC correctly says the proposed 361-task run must compare
token baseline, CURA reimplementation and Jev on the same trajectories. The Step-level Cascade's
93.9% accuracy/91.5 F1 is a trained classifier, not a zero-shot judge. Jev could beat tokens and
cost, but beating the trained SOTA is unlikely without a held-out, question-specific calibration.

### (d) Mac feasibility

**PASS for offline scoring; not PASS for live OSWorld.** The datasets can be downloaded and scored
on this Mac, but OSWorld itself needs a Linux VM and the report says the Mac path is partial. The
omp hook version is locally runnable, with later human action as GT; the benchmark claim must be
kept separate from dogfood.

### (e) Cheapest experiment

**Sound bar, wrong first N.** 361 tasks x 40 steps at 4k tokens is a $2.4 estimate and may be too
large before verifying the released records contain agent text. First inspect 20 records keyless;
if only screenshots exist, mark BLOCKED. If text exists, run 50 trajectories, compare tokens vs
three Nouls, and only then spend for the full holdout. The p<0.05 bar and FAR cap can fail cleanly.

### (f) Payoff vs complexity

**High omp payoff / medium research payoff.** This is the most directly dogfoodable CC idea: an
advisory post-hook can flag loops and false done claims. It should not block or claim benchmark SOTA
until the evaluator and grader error are audited. The complexity is low compared with Android or
PokéJev.

## 5. BrowseSafe streaming injection shield — 555/1000 — KEEP only as a public-data probe

### (a) Novel mechanism and closest published work

Mechanism novelty: **3.5/10.** BrowseSafe already provides a fine-tuned Qwen3-30B detector and
PromptGuard-2/LlamaFirewall are nearby. The only meaningful delta is chunked, decomposed Nouls with
an explicit benign-distractor false-positive bar and no fine-tuning.

### (b) Section 2 fit test

1. **Defined answers: PASS.** Each Noul is a fixed detection property.
2. **Only because cheap/fast: conditional PASS.** Every page-read is a real hook point, and Jev is
   much faster/cheaper than a frontier judge. But CC's page length (mean 53,769 chars) implies
   multiple chunks, and the 1,200/min rate cap makes a bursty crawler more than a trivial loop.
3. **Outcome grades it: PASS.** BrowseSafe labels are external and roughly balanced at 49.6%.

### (c) SOTA comparison

**Strongly like-for-like on the public test split.** The 3,680-row split and F1 0.904/precision
0.978/recall 0.841 are source-checked. Sonnet's reported F1 ~0.86 is a different latency/cost
reference, while BrowseSafe is the actual SOTA target. The claim could beat cost/latency but raw
F1 0.904 is ambitious for zero-shot Jev; the lane's R80/R82 injection failures are direct negative
prior, not a footnote.

### (d) Mac feasibility

**PASS for offline benchmark scoring.** The HF dataset and Jev client run on the Mac. No browser
attachment or local model is needed. The eventual omp post-hook is project/profile sensitive and
must remain advisory.

### (e) Cheapest experiment

**Sound data, inflated first spend.** Fit threshold on 1,000 rows and score 3,680 is a valid bar,
but 63M tokens/$2.6 is not a “cheap probe” relative to the chance of reproducing R82. First run
500 balanced dev/test rows with fixed question wording, keyword floor and one free comparator only
if approved; a fail at F1 <0.75 or benign FP >15% kills the path before full spend. The proposed
p95 <=1s is measurable and likely reachable; it cannot compensate for poor F1.

### (f) Payoff vs complexity

**Moderate payoff / low implementation complexity / high distribution risk.** It could become a
useful annotating hook if benign pages stay quiet. It should not become a blocking guard. The score
is below 600 because the closest published work already owns the mechanism and this lane's own
negative evidence is unusually close.

## Next ten: keep, merge, or kill

6. **Calibrated speculator for computer-use agents — MERGE.** Merge into the PokéJev/PUCT search
shape: a speculative branch is just a calibrated prior; do not maintain a separate idea until the
clock experiment shows branch-launch value.

7. **MiniWoB++ against the clock — KEEP.** It is the best low-cost Mac smoke and the environment
probe confirms it runs; require time-scaled reward, not only binary SR.

8. **Conformal element sets — KEEP, merge with V-Droid.** The coverage idea is distinct and useful,
but the candidate verifier and Android/Mac AX executor should share one implementation and one
calibration split.

9. **Web PRM slot — KEEP.** Public static labels and Web-Shepherd supply a clean comparison; this
is a better immediate experiment than full WebArena infrastructure.

10. **Real-time StarCraft II — KILL as a SOTA claim; keep only as a latency demo.** Every LLM scores
zero, but research-sota says a scripted controller beats the built-in AI, so it cannot support a
strong agent-SOTA claim.

11. **Real-Time Reasoning Gym — MERGE with a reflex/planner controller.** Good mechanism, but its
published six-minute-step regime is not like the intended 130ms loop; keep only with a new fixed
interval and wall-clock metric.

12. **ViZDoom Defend the Center — KILL as overall SOTA; KEEP as symbolic latency probe.** The
12-kill symbol row and NanoJev 128/128 warn that Jev is not the best gameplay policy and a script
is a strong floor.

13. **LLM Chess policy-only — KEEP with a strict class boundary.** It has an excellent external
engine oracle and cost metric, but score it against the LLM 1613.8 Elo row, never Stockfish or the
2895 specialist result.

14. **MacArena AX executor — KEEP, but mark MAC-PARTIAL.** It is the strongest native-Mac product
path, yet the local probe did not boot the emulator; first prove one AX task offline and one checker
before calling it runnable.

15. **Game-QA state oracle — MERGE with the CURA/step-monitor idea.** The state-transition oracle
and certified alarm share the same GT and CUSUM machinery; separate only if HackAtari exposes a
large, independent bug corpus.

## Overall judgment

Claude's file is smart and materially above the ordinary idea bar. Its best contribution is seeing
that Jev's probability distribution replaces unavailable LLM log-probs in search. Its main weakness
is overcommitting to expensive systems (AndroidWorld, Jericho, public ladder play) before a small
local replay falsifies the mechanism. It also occasionally compares different observation modes;
that is acceptable as a candidate list but not as a published SOTA claim. The first action I would
fund is a no-key MiniWoB/Web PRM replay and the first live candidate is PokéJev only after its
2,000-turn replay prior beats usage frequency and its local clock harness is proven.

No scores in this file are Jev scores. No API call was made.
