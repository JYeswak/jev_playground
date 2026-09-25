# Codex reveal reactions to Claude's cross-score

Bead: `jev-jy7t.1`. Date: 2026-09-25. I read `WIZARD_SCORES_CC_ON_COD.md` after pulling
`main`, and I accept several of its criticisms. The most important correction is that my original
ranking treated “published target” and “runnable local experiment” as if they were the same. They
are not. A target can be a valid external reference while the proposed comparison is blocked by
observation type, benchmark infrastructure, or a forbidden paid comparator.

## Overall reaction

Claude's scores are directionally right. I was too generous to symbolic game loops and too loose
about browser benchmark protocol. Revised order:

1. MiniWoB++ DOM action lattice — **650**
2. Web step verifier, rebased to static verifier data — **545**
3. ReflexGate — **410**
4. BALROG relative-tree search on a local subset — **385**
5. ViZDoom symbolic controller as a latency probe, not a SOTA claim — **240**

The two largest factual corrections are accepted plainly:

- My MiniWoB experiment said “46 tasks x four seeds.” Claude checked the leaderboard and says the
  published BrowserGym/MiniWoB benchmark has 125 tasks. The 46-task bar is not like-for-like and is
  removed from the intended experiment.
- My Web-Shepherd bar used a live WebArena-lite policy-search lift, but WebArena's reference images
  are amd64-only here and the cited lift uses GPT-4o-mini, which this lane cannot use as a paid
  comparator. The idea survives only as a static WebRewardBench/WebPRMBench verifier experiment.

The l2o3 verifier closure also reinforces the distinction: a typed transport observation can be
proved locally without a paid call; it does not make an unrelated SOTA comparison valid.

## 1. ReflexGate — Claude 380; revised self-score 410; demote

### Where Claude is right

Claude correctly identifies that my published AgileThinker comparison does not prove the latency
claim. The paper's **0.88 / 0.45 / 0.89** Freeway/Snake/Overcooked numbers use six-minute steps,
so a 130 ms Jev call is not late. The same feedback catches my “beat AgileThinker or beat a
scripted reflex by 10%” escape hatch: the second bar could pass while beating no published agent.
The local environment was only “likely YES” in `research-sota.md`; `local-env-probe.md` did not run
Real-Time Reasoning Gym. That is MAC-PARTIAL, not local-verified.

### Where Claude is too harsh

The mechanism remains novel enough to test: AgileThinker, Lumine, Game-TARS and DPT-Agent use fixed
or learned fast/slow scheduling, but none of the cited abstracts exposes a calibrated typed
probability as the wait decision. The right claim is not “Jev beats AgileThinker at six minutes.”
It is “at a preregistered short interval, Jev's confidence gate trades score for wall-clock
progress, compared with the same deterministic reflex and a planner.” That is a new Pareto
experiment, not a SOTA win.

### Revised bar

Keep only if the environment can be installed and the timing regime is fixed before calls. Use
Freeway/Snake/Overcooked at 1 s, 250 ms and 100 ms intervals, with the same scripted reflex, planner,
no-op and random floors. Report score/second, missed deadlines and spend. Kill if Jev is never late
or if the scripted reflex wins by more than 10%. Revised score: **410/1000**. It moves below
MiniWoB and the verifier because the external reference does not constrain the relevant regime.

## 2. MiniWoB++ DOM action lattice — Claude 540; revised self-score 650; promote to first

### Where Claude is right

Claude caught the material split error. My “46 tasks x four seeds” line was not a published
MiniWoB++ split. The local environment probe confirms `miniwob==1.1.0`, Selenium 4.49 and local
Chrome run here, with 98–145 ms step p50. The cited OrbyAgent number **74.9 +/- 1.2** is real, but
Claude checked the leaderboard README and found OrbyAgent reads screenshot plus HTML. That is not a
like-for-like target for a Jev DOM-only agent.

Claude is also right that binary SR alone fails section 2's “only because fast” leg. The primary
metric must include MiniWoB's native time-scaled reward and success/$, not just task completion.
The browser step itself costs roughly the same order as Jev, so the speed hypothesis is still
reasonable, but it must be measured rather than asserted.

### Where Claude is wrong / what I correct

Claude calls this “not novel” because BrowserGym GenericAgent already chooses element IDs. That is
fair as a mechanism discount, but the Jev contribution is not simply replacing a language call:
parallel Choice over bounded `{element, operation}` options, precondition Noul, and a confidence
policy produce a typed action lattice whose uncertainty is inspectable. The right novelty claim is
“cheap typed action selection over a code-owned candidate set,” not “first candidate selector.”

I accept the protocol correction. The intended experiment is now **all 125 published tasks**, or a
clearly named official subset with its own published baseline; no invented 46-task split. Use the
text/HTML observation arm separately from OrbyAgent's screenshot+HTML arm. The clean reference is
GPT-5 GenericAgent **71.5 +/- 1.8** in the leaderboard, while OrbyAgent's 74.9 is a different
observation category.

### Revised bar

Run 125 tasks, fixed seeds and timer reward, with no-op/random/common-action/scripted floors. Compare
Jev DOM-only to the closest text/HTML baseline. Require binary SR above the matched baseline and
>=2x success/$; do not claim a win over 74.9 unless the observation protocol matches. Revised score:
**650/1000**. It becomes first because the Mac path and checker are real, the experiment is cheap,
and the correction makes the claim narrower rather than false.

## 3. Web Step Surgeon — Claude 340; revised self-score 545; rebase, do not drop

### Where Claude is right

The core verifier slot passes the fit test, but the original SOTA bar was not runnable. Web-
Shepherd's **23.64 -> 34.55** WebArena-lite lift is a live policy-search result using GPT-4o-mini,
and AGENTS.md forbids paid comparators. The research report says WebArena's reference stack is
amd64-only/AMI-based, so my proposed 300 live trajectories cannot reproduce it on this Mac. A
replay of trajectories measures verifier labels, not a policy success lift. Claude's critique is
correct and load-bearing.

### Where Claude is too harsh

The idea does not depend on WebArena. Web-Shepherd, AgentRewardBench and WebRewardBench provide
static trajectory/judge data. The corrected experiment can ask Jev whether a step progressed,
caused a side effect or is stuck, then compare those answers against external labels. The tool's
future omp form can be dogfooded on our own sessions, but that is a separate internal-outcome lane,
not the published SOTA claim.

The mechanism is still more than a copied classifier: three parallel Nouls plus a reversible repair
policy and an explicit no-LLM-judge checker. It is not Web-Shepherd's trained PRM, so the claim is
“zero-shot typed verifier at lower cost,” not “same system with no training.”

### Revised bar

First score WebRewardBench/WebPRMBench or AgentRewardBench on a fixed held-out split, with the
published verifier metrics as targets. Then run a 20-task MiniWoB transition replay locally. Require
F1 above a declared baseline, stable low false alarms, and no task-checker regression in the local
arm. Remove the 34.55 live-lift claim unless a free, like-for-like policy is available. Revised
score: **545/1000**; useful and potentially shippable, but not the direct WebArena SOTA idea I
originally wrote.

## 4. BALROG Relative-Tree — Claude 360; revised self-score 385; narrow to local subsets

### Where Claude is right

The BALROG aggregate is not computable on this Mac: the local probe says the NLE/MiniHack language
wrappers segfault. Crafter, TextWorld, BabyAI and BabaIsAI run, but “average progress over six
environments” cannot be claimed. Claude is also right that expanding a simulator tree changes the
protocol relative to a single-turn BALROG agent. The published **58.1** aggregate and Crafter
**76.8** row are not automatically a same-budget target for Jev-PUCT.

The “>=2x lower calls” escape hatch was too permissive. A cost Pareto result is useful, but it must
be labelled a Pareto result and cannot stand in for an SOTA win.

### Where Claude is too harsh

The local subset is still a legitimate experiment. The mechanism is not a generic classifier:
Jev's Choice distribution replaces unavailable token log-probs, and pairwise successor judgments
correct absolute-score saturation. MC-DML's checked Jericho results—Zork1 **48.66 +/- 1.89**,
Deephome **67.00 +/- 1.41**, Detective **346.67 +/- 9.43**—show a clean search reference. The
question is whether a typed prior adds value over uniform PUCT on a fixed game, not whether Jev
wins all BALROG.

### Revised bar

Drop the aggregate claim. Start with Crafter and TextWorld only, report progress and calls/episode,
and use the checked BALROG per-game row only if the exact version and action protocol match. The
first kill is +5 progress over uniform PUCT on all selected games, not “beat 58.1 aggregate.” If
that passes, a separate Docker/Jericho experiment can test MC-DML. Revised score: **385/1000**;
research value remains, product value is low.

## 5. ViZDoom symbolic controller — Claude 300; revised self-score 240; demote to latency probe

### Where Claude is right

The **12 kills/600 frames** number is correct for symbol-only Claude-4-Sonnet/Gemini-2.5-Pro, but
it is only two seeds and the game is paused every frame. The local probe confirms ViZDoom runs on
arm64, so feasibility is stronger than the score suggests. However, the scripted turn-and-fire
floor is likely strong, and NanoJev's author result is **128/128 on Basic vs Jev 56/128**. I
should not present a symbolic controller as overall game SOTA.

### Where Claude is too harsh

A carefully isolated event-triggered controller can still answer a meaningful latency question:
can a typed semantic target/danger gate sit above deterministic aim and remain useful when the game
is unpaused? The correct output is a Pareto/LLM-row result, never “Jev beats Doom.” The local
experiment can fail honestly and cheaply.

### Revised bar

Run paused symbol-only first to match the paper, then unpaused with the same seeds. Require Jev to
beat the deterministic turn/fire controller on the unpaused metric and report kills/sec; if it does
not, drop the idea. Do not use NanoJev or SauerkrautLM as if they were like-for-like SOTA. Revised
score: **240/1000**. This is no longer top-five material.

## Blind spot: AX-tree observation pruning for native Mac agents — 735/1000

Neither file made this the primary idea. Both mentioned AX candidate selection, memory selection, or
MacArena execution, but neither proposed **pruning the live accessibility observation before a
planner sees it** as the main Jev-controlled loop.

### Mechanism

A deterministic AX collector emits all visible nodes. Jev asks parallel Nouls per node:
`relevant_to_current_goal`, `contains_required_value`, and `safe_to_omit`; code retains a bounded
AX subgraph and passes only that state to a planner or deterministic executor. A Choice can select
one of multiple retained subgraphs when the node count exceeds the state budget. The planner's
output is not graded by Jev. The environment checker grades success.

Closest published work: MindAct/Laya element ranking, Prune4Web's candidate pruning, MacArena's
screenshot+AX agent, and the context-selection direction in RAG agents. Those rank clickable
candidates or retrieve history; this idea prunes the complete live AX observation to reduce planner
context and action latency.

### Section 2 fit

- **Defined answers:** yes; each question is a Noul over a code-owned AX node, and code enforces
  parent/child invariants and preserves required labels.
- **Only because cheap/fast/stable:** yes if it reduces a large AX tree before a slow planner. Jev's
  ~130 ms and low price permit asking over many nodes; the stability number makes a state-hash cache
  plausible. This must be measured on Mac-native state, not assumed from browser fixtures.
- **External outcome:** MacArena task checkers or MiniWoB task rewards grade success; token count and
  wall time are secondary metrics.

### SOTA to beat

MacArena's OpenAI CUA is **31.83%** on 421 native macOS tasks (Jun 2026),
<https://arxiv.org/abs/2606.06560>. The intended like-for-like bar is the same AX-tree observation
track, not screenshot-only OSWorld. A secondary efficiency reference is OSWorld-Human's finding
that agents use 2.7–4.3x necessary steps, <https://arxiv.org/abs/2506.16042> (Jun 2025).

### Local environment

MacArena is reported as runnable through Apple Virtualization/UTM, but the local probe did not boot
it; label that path MAC-PARTIAL. The first runnable control is MiniWoB++ 1.1.0 with local Chrome and
Selenium 4.49, which the probe executed at 98–145 ms p50. A second local path is a small native
macOS suite using AXUIElement over Calculator/TextEdit/Finder; no model is needed for the control.

### Cheapest falsifying experiment

Use 50 MiniWoB tasks and 20 native-app tasks on a dev split, then 50/20 held out. Arms: full AX tree,
code-only selector, Jev-pruned tree, and random-pruned tree. Freeze the questions before calls.
Cap 500 Jev calls, record token count, p50/p95 and cache hit rate; estimated spend is about
$0.015–$0.05 depending on AX-state length. Bar: Jev-pruned state must preserve task success within
one percentage point of the full-tree arm while reducing serialized planner-state tokens by >=40%
and not increasing p95 wall time. Kill if success drops, the deterministic selector matches Jev, or
there is no token reduction.

## Final revised ranking

1. MiniWoB++ DOM action lattice: **650** — local, cheap, corrected protocol.
2. Web transition verifier on static judge sets: **545** — rebase required, but direct omp payoff.
3. ReflexGate at a genuinely time-pressured interval: **410** — novel, no published short-interval
   SOTA yet.
4. BALROG relative search on Crafter/TextWorld: **385** — viable subset, not aggregate SOTA.
5. ViZDoom symbolic controller: **240** — latency demo only; scripted floor likely kills it.
6. AX-tree observation pruning: **735** — blind spot and the next experiment I would actually run,
   because it combines local Mac use, a concrete token-reduction metric, and a task checker without
   pretending a scripted game bot was beaten.

The score exchange changed my ranking. The high-level lesson is not that Claude's ideas were bad;
it is that every symbolic-game idea needs a stronger floor than “LLM SOTA,” and every browser idea
needs the exact observation type, task split and evaluator protocol before its SOTA number means
anything.

No API calls, local LLMs or model comparators were used for this reaction.
