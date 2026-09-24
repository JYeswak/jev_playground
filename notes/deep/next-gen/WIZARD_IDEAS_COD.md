# Codex wizard: Jev for computer use and games

Bead: `jev-jy7t.1`. Status: **PREPARED-NOT-MEASURED**. No Jev calls, local LLM calls, or
comparator calls were made while writing this file. All proposed numbers below are preregistration
bars or published targets, not results from this lane.

## Scope and evidence boundary

Joshua's focus change is authoritative: computer use and games, with environments runnable on this
M3 Ultra/macOS arm64 and Jev called through the TypeSafe API. Jev is text-only; these designs feed it
DOM/A11y trees, engine/RAM/object state, or deterministic before/after diffs. None asks Jev to read a
raw screenshot or generate text.

I read the complete `BRIEF.md` and its `ledger-20260924.md` and `outside-scan-20260924.md`, then
read the four incoming reports: `research-classifier-uses.md`, `research-sota.md`,
`research-guidance.md`, and `local-env-probe.md` (all dated 2026-09-24). I also checked the cited
2025-2026 papers/leaderboard pages below. The incoming reports are scout research and have not been
independently re-run by this pane.

### SOTA anchors used below

- **OSWorld-Verified:** official leaderboard snapshot: Claude Fable 5, **85.96%** at 100 steps
  (Aug 1 2026); framework Intelligence-Indeed reports **90.19%** (Jul 2026). Official leaderboard:
  <https://os-world.github.io/>. OSWorld-Human warns agents use 2.7–4.3x necessary steps:
  <https://arxiv.org/abs/2506.16042> (Jun 2025).
- **MacArena:** OpenAI CUA **31.83%** on 421 native-macOS tasks (Jun 2026):
  <https://arxiv.org/abs/2606.06560>. This is the cleanest native-Mac target.
- **WebArena:** WebTactix **74.3%** on the 812-task board (Jun 2026):
  <https://leaderboard.steel.dev/leaderboards/webarena>. OpenAI CUA was **58.1%** in the
  Jan 23 2025 report: <https://openai.com/index/computer-using-agent/>.
- **MiniWoB++:** OrbyAgent/Claude 3.5 **74.9 +/- 1.2 binary success** (Feb 2025), with the
  benchmark's time-scaled reward as the native metric; leaderboard/source:
  <https://huggingface.co/spaces/ServiceNow/browsergym-leaderboard> and
  <https://miniwob.farama.org/content/reward>.
- **Web step judging:** Web-Shepherd lifts WebArena-lite from **23.64% to 34.55%**, and is
  reported about **10x cheaper** than a GPT-4o verifier (May 2025),
  <https://arxiv.org/abs/2505.15277>. AgentRewardBench has 1,302 expert-rated trajectories;
  GPT-4o judge F1 is **75.9** and rules reach precision **83.8** (Apr 2025),
  <https://arxiv.org/abs/2504.08942>.
- **GUI grounding:** ScreenSpot-Pro is **82.7** for Indeed-UI-32B (Sep 2026) on the verified
  leaderboard <https://gui-agent.github.io/grounding-leaderboard/index.html>; the 2025 benchmark
  paper is <https://arxiv.org/abs/2504.07981>. A text-only AX-tree idea must not claim pixel
  grounding parity without a like-for-like observation arm.
- **BALROG:** checked leaderboard best **58.1% average progress** (Gemini-3-Pro, Feb 2026),
  with per-environment bests including Crafter **76.8%**, TextWorld **75.7%**, and NetHack
  **13.2%**; <https://balrogai.com/> and <https://arxiv.org/abs/2411.13543> (ICLR 2025).
- **Real-time games:** VideoGameBench's best 2025 full real-time score is **0.48%**, paused Lite
  **1.6%**, <https://arxiv.org/abs/2505.18134> (May 23 2025). The 2026 board reports **4.6%**
  full real-time for VG-Agent with Claude Opus 4.6/Gemini 3.1 Pro,
  <https://antimlabs.com/vgbench>. Real-Time Reasoning Gym reports AgileThinker
  **0.88 / 0.45 / 0.89** on Freeway/Snake/Overcooked under six-minute steps,
  <https://arxiv.org/abs/2511.04898> (Nov 2025, ICLR 2026).
- **Orak real-time StarCraft II:** every tested LLM scored **0 on hard real-time**, with
  per-step latency **19.6 / 27.2 / 99.2 seconds**, <https://arxiv.org/html/2506.03610>
  (Jun 2025). This is a latency target, not evidence that a scripted controller is weak.
- **LLM Chess:** current LLM Chess row: **1613.8 Elo** at about **$0.058/move** (Sep 9
  2026 CSV), <https://raw.githubusercontent.com/maxim-saplin/llm_chess/main/data/elo_refined.csv>.
  A 270M searchless model's 2895 Lichess result is a non-LLM specialist ceiling,
  <https://arxiv.org/abs/2402.04494>; it is not the fair LLM comparator.
- **Classifier/verifier research:** GUI step verification in STEVE,
  <https://arxiv.org/abs/2503.12532> (Mar 2025); GUI-Actor's grounding verifier,
  <https://arxiv.org/abs/2506.03143> (Jun 2025); GTA1 proposal selection,
  <https://arxiv.org/abs/2507.05791> (Jul 2025); Agent Alpha's step-level MCTS,
  <https://arxiv.org/abs/2602.02995> (Feb 2026); MacArena,
  <https://arxiv.org/abs/2606.06560> (Jun 2026); and the 2026 Step-level Cascade,
  <https://arxiv.org/abs/2604.27151>.

Jev facts used as inputs, not re-measured here: pinned `jev-1.13.0`, about 127–162 ms p50 for
short states, about $0.016–$0.029 per 1,000 answers, about 0–2 repeated-answer flips on the good
verification sets, and a documented API limit of 1,200 requests/minute (about 20 requests/s). The
rate limit, not the local simulator, is the loop constraint. Batch independent questions over one
state; set retries to zero and count timeout/429/529 as failed steps.

## Thirty candidate mechanisms

Every row has: loop, fit decision, the published target, outside ground truth, and a falsifiable
first experiment. `Cost` is a proposal estimate at the ledger's 683-token/answer rate, not a quote.
All rows require the four floors: no-op, random, most-common action, and a deterministic scripted
bot. A row is not a Jev win if it only beats those floors.

| # | Candidate / loop | Fit and nearest dead relative | SOTA target; outside ground truth; cheapest falsifier |
|---:|---|---|---|
| 1 | **Orak real-time action prior.** Serialize the 72-action StarCraft-II observation; Choice picks the action, Score rates tactical value, and code enforces legal actions. Invoke only at the game tick, never after a stale observation. | Defined Choice/Score; 130 ms is the point, not prose quality; engine win/damage is external GT. Nearest relative is the 0-score Orak LLM row, but a scripted bot is a mandatory stronger floor. | Beat Orak's **0 hard-real-time win rate** and report win rate plus seconds/step against built-in AI; 30 matched games, roughly 3,000 calls, about $0.09. Kill if Jev cannot beat the scripted bot or misses the 20 req/s budget. Source: `arxiv.org/html/2506.03610`. |
| 2 | **MiniWoB++ semantic action lattice.** DOM/A11y extraction produces at most 255 candidate element actions; one Choice selects a candidate and a parallel Noul checks its precondition. | Strong fit: the answer set is code-owned and DOM is text; task reward is GT. Nearest relative is MindAct/Laya element ranking and R85's failed hierarchical Choice; this uses a real candidate set plus action execution, not two-stage taxonomy. | Beat **74.9 +/- 1.2** binary SR on the same MiniWoB++ split, while also reporting time-scaled reward; 46 tasks x 4 seeds, about 1,000 calls, $0.03. Kill if it does not beat 74.9 or its exact DOM observation differs from the published arm. |
| 3 | **Web step verifier and self-healer.** After every browser action, serialize expected and observed AX-tree/DOM deltas; ask Nouls for `goal_progress`, `side_effect`, and `stuck`, then Choice `continue/retry/undo/escalate`. | Strong: Web-Shepherd already establishes the verifier slot; Jev's parallel typed checks remove per-criterion serial judge calls. Nearest dead relative is the fleet gate (unseen harm shapes); this has exact task-state checkers and high action prevalence. | Beat Web-Shepherd's **23.64 -> 34.55** WebArena-lite lift and its reported 10x verifier-cost advantage; 300 held-out tasks, 1,500 calls, $0.04. GT is the benchmark checker plus hand-audited PASS/FAIL sample. |
| 4 | **MacArena AX-tree action critic.** Use macOS Accessibility tree plus before/after tree diff, not pixels. Jev checks whether the last action satisfied the requested transition and selects a deterministic repair. | Defined answers; latency matters because MacArena averages 14 steps; native AX tree is a text state. Nearest relative is OSWorld screenshot SOTA, which is not like-for-like; compare only to MacArena AX-tree rows. | Beat OpenAI CUA's **31.83%** MacArena SR on the same 421 tasks, or Pareto-dominate it at equal SR with fewer steps; 100-task dev then 421-task test, 6,000 calls, $0.17. Kill if AX-tree-only state cannot recover native app changes. |
| 5 | **Conformal AX candidate sets.** Calibrate Choice probabilities on held-out tasks; execute automatically only when the conformal set has one element, otherwise pass a small set to a deterministic resolver or human. | Novelty is a coverage-bearing set of element IDs, not a hand-tuned top-k. Nearest relative is SafeGround/CORA and R86's failed top-3; this tests per-app exchangeability rather than assuming global confidence. | Target WebArena's **74.3%** board result while requiring >=95% held-out action coverage and mean set size <=1.4; 200 dev + 300 test tasks, 2,500 calls, $0.07. Kill on coverage failure or no success/$ gain. |
| 6 | **Speculative browser action launch.** Jev predicts the large planner's next Choice and gives launch/hold probability; only high-probability branches execute speculatively. | Directly maps to Speculative Actions' selective branching; unlike confidence cascade R? it launches a reversible browser read, not a second model. | Beat Speculative Actions' **55% next-action accuracy / 20% latency reduction** on the same task family; 500 tasks, 1,000 calls, $0.03; GT is next action and task wall time. |
| 7 | **AX-tree affordance shortlist.** A deterministic parser keeps 50 candidates; Jev Choice selects the intended affordance and Noul checks that text/role matches the instruction. | It is a text-state version of GUI-Actor's verifier and MindAct, not raw pixel grounding. | Beat MindAct's published **85–89% top-50 recall** on Mind2Web, or beat Laya's cross-task **50.3%** element accuracy on the exact split; 1,000 actions, $0.03; GT annotated element IDs. |
| 8 | **Action-transition regression oracle for Mac apps.** Record AX-tree transitions for Calculator, TextEdit, Finder and Safari; Jev verifies whether a code change preserves each transition. | External GT is the deterministic UI test suite, not Jev self-report. Nearest relative is STEVE; this is regression testing, not agent training. | Beat the published OSWorld-Human efficiency target by reducing unnecessary steps while preserving task success; 500 replayed transitions, 1,500 calls, $0.04; kill if F1 < .90 on hand-checked diffs. |
| 9 | **Browser retrieval gate.** Choice `no retrieval/single page/multi-hop retrieval`; code runs the selected path, then a checker grades answer correctness. | Fit is action routing with an outcome, unlike the failed generic model cascade. | Beat an all-retrieval baseline at equal answer accuracy and >=15% fewer page loads on 300 WebArena-lite tasks; 600 calls, $0.02; GT checker. |
| 10 | **GUI macro-boundary judge.** Noul decides whether the current stable AX state permits a deterministic macro; code executes the macro and verifies its final state. | Nearest is jev-ultrafast's 1,092 -> 101 browser-protocol reduction, but this tests real task success and macro reuse. | Beat **101 protocol calls** on the same six-run browser task while retaining 3/3 success; 100 episodes, 1,000 calls, $0.03; kill on any task loss. |
| 11 | **Done-claim alarm.** Three Nouls judge milestone reached, side effect present, and agent's “done” claim supported; a CUSUM in code decides whether to stop. | Directly addresses CURA's 64/71 failed trajectories claiming success; code, not Jev, owns the alarm. | Beat CURA's **42.3% failure catch at 0.066 false alarms** on a held-out MacArena/OSWorld trace set; 1,000 steps, $0.03; GT environment checker. |
| 12 | **GUI failure attribution.** Choice picks the failing agent and step from a compact trace, then Noul labels the failure mode. | Exact Who&When shape; high-value because step accuracy is low, not because prose is hard. | Beat Who&When's **53.5% agent / 14.2% step accuracy** on the same public data; 1,000 traces, 2,000 calls, $0.06; GT labels. |
| 13 | **No-training step reward model.** Parallel Noul checklist over action progress, reversibility and goal distance feeds a fixed running reward; no GPT-4o distillation. | Replaces Web-Shepherd/STEP training with zero-shot typed questions; external GT remains WebRewardBench. | Match or beat Web-Shepherd's **34.55** WebArena-lite SR and 10x verifier-cost claim; 300 tasks, 1,500 calls, $0.04. |
| 14 | **Browser memory selector.** Noul per history item asks whether it changes the next legal action; code keeps only selected snippets. | Compaction R99/R100 killed guessed “keep” judgments; this is a task-state memory selector with action-conditioned GT and no summary. | Preserve WebArena-lite SR while cutting serialized state tokens >=40% on 300 tasks; 1,500 calls, $0.04; kill if checker success drops >1 pp. |
| 15 | **Reversible-action shield.** Choice `execute/preview/ask` over known UI actions, with Noul for reversibility and target match. | Avoids the 0.016% safety-veto prevalence trap by operating on the common reversible-action stream; GT is task completion plus side-effect diff. | Match MacArena CUA **31.83%** while reducing unrecoverable side effects to zero in 100 seeded tasks; 1,000 calls, $0.03. |
| 16 | **Real-Time Reasoning Gym confidence gate.** A fast deterministic reflex acts every tick; Jev Choice decides `reflex/wait-for-planner/ask-human` from symbolic state and confidence. | This is the missing bridge between fixed-thread AgileThinker and learned “reason only when necessary”; action labels are code-owned. | Beat AgileThinker's **0.88/0.45/0.89** Freeway/Snake/Overcooked scores at a shorter fixed interval, with success/second preregistered; 3 games x 100 episodes, 10,000 calls, $0.29. |
| 17 | **ViZDoom symbolic reflex controller.** OCAtari/labels buffer becomes JSON; Choice picks aim/fire/turn and Noul detects danger. | Text-symbol state is explicitly supported by the 2026 paper; no pixels or invented coordinates. | Beat **12 kills/600 frames** from symbol agents in Defend the Center while running unpaused, and report kills/sec; 100 episodes, 5,000 calls, $0.14. |
| 18 | **ViZDoom action-candidate verifier.** Deterministic CV emits legal aim candidates; Jev chooses the target and verifies hit-state transition. | It isolates Jev's semantic selection from perception; NanoJev's 128/128 Basic result is the nearest specialist ceiling, so use Defend Center. | Beat 12 kills/600 paused-frame reference in a matched symbolic setting; 100 episodes, 4,000 calls, $0.11; kill if the scripted turn/fire floor wins. |
| 19 | **BALROG policy/value beam search.** Choice is a policy prior over legal text actions; pairwise Choice compares child states; Score is only a logged diagnostic. | Agent Alpha/WebDreamer show search; typesafe-chess shows absolute Score saturation, so relative comparisons are the mechanism. | Beat checked BALROG **58.1% average progress** and report Crafter **76.8%** as the per-game target; 100 episodes capped at 20,000 calls, $0.57. |
| 20 | **BALROG Crafter resource-risk judge.** Parallel Nouls for hunger, hostile proximity, craft prerequisite and irreversible death risk choose a safe macro. | The structured Crafter state is small and local; unlike generic toxicity, prevalence of each event is measurable. | Beat BALROG Crafter **76.8% progress** and improve progress/$ over a planner; 100 episodes, 10,000 calls, $0.29. |
| 21 | **NetHack text tactical shield.** NLE `message/blstats/inventory/glyphs` feed Choice flee/fight/search and Noul lethal-risk. | BALROG wrapper segfaults on arm64, but plain NLE works; this is a local Mac-specific research seam, not a claim that the broken wrapper works. | Beat checked NetHack **13.2% progress**; 50 episodes, 15,000 calls, $0.43; count crashes as zero. |
| 22 | **Craftax symbolic milestone selector.** Score structured inventory/health/achievement state and Choice the next milestone; batch 1,024 simulator states offline through Jev-sized strata. | More than a raw game policy: Jev judges sparse natural-language goals over symbolic states; local CPU env is ready. | Beat MBRL's **69.66% Craftax-Classic reward** is a stretch; first kill bar is > scripted floor with cost/episode logged. 500 episodes, 10,000 calls, $0.29. |
| 23 | **TextWorld goal-progress comparer.** Pairwise Choice compares two successor states, avoiding absolute Score saturation; code runs admissible commands. | Directly matches Motif/ONI's progress-reward slot without a distillation model; GT is game objective. | Beat BALROG TextWorld **75.7% progress** on fixed generated seeds; 200 episodes, 12,000 calls, $0.34. |
| 24 | **Orak/StarCraft tactical veto.** Do not ask Jev to plan all 72 actions; a deterministic macro proposes actions and Jev vetoes stale/illegal tactical transitions. | This is the honest alternative to the tempting raw Orak idea: code handles timing, Jev handles semantic action choice. | Beat the published **0 hard-real-time LLM score** at 19.6–99.2 s/step, then compare against a scripted controller; 30 games, 3,000 calls, $0.09. |
| 25 | **LLM Chess candidate selector.** `python-chess` enumerates legal moves; Jev Choice selects among top Stockfish candidates and Noul checks tactical blunder, with Stockfish held only as GT. | Defined answer space, strong external oracle, and a cost hypothesis; do not claim to beat Stockfish. | Beat LLM Chess **1613.8 Elo at $0.058/move** while reporting the specialist-model ceiling separately; 100 games, 5,000 calls, $0.14. |
| 26 | **Chess search-depth allocator.** Jev Score/Noul decides whether a position needs one-ply, shallow Stockfish, or deep search; code owns the budget. | Novel use is deciding compute, not playing chess by free-form text; GT is Stockfish move agreement and game result. | Match 1613.8 LLM Elo with >=50% fewer deep-search calls; 100 games, 2,000 calls, $0.06. |
| 27 | **ALE/OCAtari real-time object policy.** Serialize RAM/object list, Choice action, and confidence gate decides whether to call Jev again or hold the reflex. | Local probe found 0.22–1 ms simulator steps, so Jev is the bottleneck and the experiment directly measures the latency tradeoff. | Beat VideoGameBench's **4.6% full-real-time** only on a matched Atari subset if the observation/task split is accepted; otherwise use ALE score and label it a new Pareto point. 10 games, 10,000 calls, $0.29. |
| 28 | **2048/Tetris semantic critic.** Jev judges after-state quality/risk; deterministic game code executes action, and a small beam retains candidates. | The external board has much stronger non-LLM records, so this is explicitly an LLM-row-only test, not an overall SOTA claim. | Beat the LLM rows in lmgame-Bench on 2048/Tetris, not TD n-tuple or 51M-line records; 200 games, 4,000 calls, $0.11. Source: <https://arxiv.org/abs/2505.15146>. |
| 29 | **Game QA state-transition oracle.** Parallel Nouls check milestone, collision, score consistency and visual-temporal glitch from engine state; code files a bug. | TempGlitch finds VLMs near chance; TITAN reaches 95% task completion and found four bugs. Jev gets symbolic state, not unreliable pixels. | Beat TITAN's **4 previously unknown bugs / 95% completion** only on a fixed seeded local game QA suite; 2,000 transitions, $0.06; hand-audit every PASS/FAIL sample. |
| 30 | **Adaptive judge cache for GUI/game states.** Hash normalized AX/RAM state; Jev judges only changed semantic fields and reuses stable answers, with Noul cache-validity checks. | Jev's 0–2 flips and deterministic token counts make memoization meaningful; unlike compaction, the environment checker grades every action. | Preserve the selected benchmark's SR while cutting judge calls >=50% and p95 loop latency; 500 episodes, 5,000 uncached calls, $0.14. |

## Five best, ordered

The ordering favors a clean Mac environment, a text-state like-for-like comparator, an external
checker, and a Jev-specific advantage that is not merely “ask the same classifier again.” Each is a
proposal; none has been measured.

### 1. Confidence-gated reflex/planner on Real-Time Reasoning Gym

1. **Name and pitch.** **Jev ReflexGate:** use a typed Jev Choice as the calibrated switch between a
   sub-millisecond deterministic reflex, a slower planner, and a safe hold action. The novelty is
   not “Jev plays”; it is using a probability to decide when the slow planner is worth waiting for
   while the world continues.
2. **Loop.** At every environment tick, code serializes the symbolic state and the last action. One
   batched request asks:
   - Choice `next_action` over the legal action set plus `hold`;
   - Noul `reflex_safe`;
   - Noul `planner_needed`;
   - Noul `milestone_reached`.
   Code executes the reflex when the action is safe and the model is confident, holds or invokes a
   planner when uncertainty exceeds the preregistered regime threshold. One request per tick is
   capped at the API's 1,200 requests/minute; no SDK retries. A late response is a failed step, not
   silently dropped.
3. **Fit test.** (a) Answers are fully defined by legal actions and booleans. (b) The advantage is
   real-time latency: Jev's measured ~130 ms is about three tokens of the Gym's reported 0.047 s/token
   regime, while multi-second planners miss ticks and receive default actions. Stability matters
   because a flip changes whether the planner is launched. (c) The environment emits score and
   survival ground truth; no label is written by this lane. This is a stronger fit than a generic
   route because latency is the outcome variable.
4. **Why next-gen.** Existing systems use a fixed fast/slow split (DPT-Agent), learned “reason when
   necessary” (Lumine), or a trained bridge (Latent Bridge). None of the cited work exposes a
   calibrated typed confidence as the online wait decision. Jev makes that decision cheap enough to
   ask every tick and inspect its uncertainty rather than hiding it in a learned router.
5. **Ground truth and prevalence.** Local environment: Real-Time Reasoning Gym's Freeway, Snake and
   Overcooked tasks, with score per episode and default-action counts as GT. Published baseline
   prevalence is not a binary class; log the fraction of ticks where a planner was actually needed,
   with the dev estimate held out from the test episodes. Run fixed seeds and the four floors.
6. **Cheapest falsifying experiment.** Freeze questions, thresholds and seeds in a prereg file.
   Run 100 episodes per game on a 50-episode dev split and 50-episode test split. Four arms: no-op,
   random, most-common, deterministic reflex, and Jev ReflexGate; include an always-planner arm.
   Cap at 10,000 Jev calls, roughly $0.29 at 683 tokens/answer, and report p50/p95 plus 429s. Bar:
   on the test split, beat the published **AgileThinker 0.88/0.45/0.89 Freeway/Snake/Overcooked**
   numbers at the same scoring regime, or beat the deterministic reflex by >=10% progress while
   staying under the 20 req/s cap. Kill if latency causes default-action loss, if Jev does not beat
   the scripted floor, or if a fixed threshold beats it at lower cost.
7. **Map location.** Real-time applications; Routing, Detection and Scoring.
8. **Nearest dead relative.** `jev-drone` and `neo4jev` were only N<=3 smokes/floors, and the brief
   says no control-loop result is measured. The difference is a preregistered repeated-episode
   wall-clock benchmark with an outcome at every tick. `NEGATIVE_EVIDENCE` R69/R79-style “last
   seat retired on arithmetic” remains a kill condition, not a reason to call a smoke a win.
9. **First build.** Start with a local symbolic Freeway/Snake adapter and an `omp` tool that logs
   only state hash, Choice, confidence, response latency, chosen arm and environment score. A
   later omp surface could use the same confidence switch for browser loops, but no agent-facing
   automation ships until the test split clears the bar.
10. **Novel mechanism.** A confidence-triggered reflex/planner handoff under a live deadline; closest
    work is AgileThinker/Lumine's fixed or learned thread selection, not a typed calibrated gate.
11. **SOTA to beat.** AgileThinker: **0.88 Freeway, 0.45 Snake, 0.89 Overcooked**, six-minute-step
    setting, Nov 2025/ICLR 2026, <https://arxiv.org/abs/2511.04898>. The exact timing regime must be
    matched or the result is only a new Pareto point.
12. **Local example.** The report says `pip install -e .` is the first install path; run the
    repository's Gym entry point on this Mac with `uv`/Python 3.12, then add `demo_reflexgate.py`.
    The local env probe already confirms the analogous symbolic simulators run on arm64; this idea
    must first confirm the Gym itself before any Jev spend.

### 2. MiniWoB++ DOM action lattice

1. **Name and pitch.** **Jev DOM-Lattice:** let deterministic code enumerate the only legal DOM
   actions, then let one Choice select the element and one Noul validate the precondition. Jev is a
   semantic selector over a small typed action space, not a pixel coordinate predictor.
2. **Loop.** At each task step, serialize the utterance, goal, DOM elements, current values and a
   short action history. Ask Choice `action` over up to 255 `{element, operation}` options and Noul
   `precondition_holds`; code rejects disabled/stale candidates, executes through Selenium or
   BrowserGym, then asks the next step. Candidate text is generated by code; Jev never writes text.
3. **Fit test.** (a) The options are element IDs and operations owned by code. (b) MiniWoB++ is a
   high-frequency loop: the sibling measured 98–145 ms Selenium steps and BrowserGym 707 ms with
   observation delay zero; Jev's ~130 ms fits Selenium and is not the bottleneck in BrowserGym.
   (c) MiniWoB's timer-scaled reward and binary task checker are external GT. This is a sharper fit
   than raw GUI grounding because the state is text and the action set is explicit.
4. **Why next-gen.** Existing Explorer/OrbyAgent-style agents emit or ground actions through a
   large multimodal policy. This mechanism converts GUI use into bounded typed search: candidate
   enumeration is deterministic, semantic choice is cheap, and uncertainty can cause a safe
   retry rather than a coordinate click.
5. **Ground truth and prevalence.** The canonical MiniWoB++ task split and browser reward are GT.
   Measure the positive rate (task success) and the invalid-candidate rate separately; do not
   author a “good action” label. The report says OrbyAgent's binary SR is **74.9 +/- 1.2**, so the
   target population is not rare.
6. **Cheapest falsifying experiment.** Use the sibling-probed local tasks first: click-test-2,
   click-button, enter-text and click-checkboxes. Then freeze the published split, 46 tasks x four
   seeds = 184 episodes. Run no-op, random, most-common, deterministic DOM script, greedy Jev and
   Jev beam=2. Cap at 1,200 calls (the API rate cap) and about $0.035; report steps, p50/p95,
   time-scaled reward, binary SR and crashes. Bar: **binary SR >74.9** with a 95% CI that does not
   overlap the published +/-1.2 interval, or equal SR at >=2x success/$; otherwise kill.
7. **Map location.** Real-time applications and Harness Engineering; Classification, Routing and
   Ranking.
8. **Nearest dead relative.** Hierarchical Choice R85 lost flat Banking77, and the old browser
   ultrafast probe is only an N<=10 smoke. This is not a hierarchy and not a fixture replay: it
   chooses among code-enumerated legal DOM actions and is graded by task timers.
9. **First build.** Install the sibling-probed stack: `uv venv --python 3.12 /tmp/jev-miniwob`,
   `uv pip install --python /tmp/jev-miniwob/bin/python "miniwob==1.1.0" "selenium==4.49.0"`,
   use the already-present local Chrome, and run four random/scripted controls before wiring Jev.
   A first omp surface would be advisory `jev_dom_action`, not an autonomous clicker.
10. **Novel mechanism.** A typed, bounded action lattice whose semantic Choice is over candidate
    element-operation pairs, plus a precondition Noul; the nearest published components are
    Explorer's exploration synthesis, MindAct/Laya element ranking and GUI-Actor's verifier.
11. **SOTA to beat.** OrbyAgent/Claude 3.5: **74.9 +/- 1.2 binary SR**, Feb 2025, leaderboard
    <https://huggingface.co/spaces/ServiceNow/browsergym-leaderboard>. Treat this as a reference
    only until the observation/action protocol is confirmed identical.
12. **Local example.** `miniwob 1.1.0` and Selenium were installed successfully on this M3 Ultra;
    Chrome tasks executed locally. BrowserGym 0.14.3 is a second local path, with
    `pre_observation_delay=0.0` to avoid the default 0.5 s delay. First demo: four tasks, one
    trace JSONL, no key; then the live Jev arm.

### 3. Web action transition verifier and self-healer

1. **Name and pitch.** **Jev Step Surgeon:** replace a large visual judge after every browser action
   with parallel Nouls over the expected DOM/AX transition, side effects and repetition; a code
   policy chooses retry, undo, alternate candidate or escalation.
2. **Loop.** The executor supplies `before_state`, `action`, `expected_delta`, `after_state` and
   task goal. Ask `made_progress`, `side_effect_matches`, `is_stuck` and `done_claim_is_true` in
   one request. Choice selects `continue/retry/undo/alternate/escalate`; only deterministic
   reversible actions are auto-retried.
3. **Fit test.** (a) All answers are booleans or a fixed action Choice. (b) Web-Shepherd already
   proves step verification is a useful slot; Jev's 130 ms and $0.02/1k answers are small enough
   for every step and parallel criteria. (c) WebArena-lite checkers, not Jev, grade task success.
   The state is DOM/AX text, so no raw image mismatch is hidden.
4. **Why next-gen.** Published GUI verifiers mostly train a reward model or use GPT-4o/GPT-5 as a
   judge. Jev makes a no-training, typed, multi-criterion verifier cheap enough to run before and
   after every reversible action, converting vague reflection into a bounded repair loop.
5. **Ground truth and prevalence.** Use WebArena-lite/WebPRMBench trajectories and the official
   task checker. Track prevalence of wrong action, true recovery opportunity, and false success;
   CURA reports 64/71 failures ending in a false success claim, so the latter is not hypothetical.
6. **Cheapest falsifying experiment.** 300 held-out trajectories, 1,500 Jev calls (about $0.04),
   zero retries, same base policy across arms: no verifier, Web-Shepherd reference rows, Jev. Bar:
   reproduce or exceed the published Web-Shepherd **23.64 -> 34.55** WebArena-lite lift, with
   action-level F1 >= the published verifier and at least 5x lower judge spend; kill if the
   deterministic checker says Jev repairs no more than the no-verifier arm.
7. **Map location.** Universal Verification and Harness Engineering; Verification, Detection and
   Routing.
8. **Nearest dead relative.** The tool-call gate failed on unseen harm shapes and the injection
   detector failed on clean tool output (R80/R82). This differs: expected state transitions are
   narrow, action-conditioned, and directly checked by the environment; it is not a broad safety
   veto over adversarial prose.
9. **First build.** Use BrowserGym MiniWoB locally first, then a static WebPRMBench replay. Build a
   pure function `repair_decision(before, after, expected, answer)` with injected Jev transport;
   only after the offline policy passes, expose an advisory omp tool that never executes a repair.
10. **Novel mechanism.** A zero-shot multi-Noul transition verifier feeding a reversible-action
    repair policy; closest published works are STEVE (GPT-4o before/after labels), Web-Shepherd
    (trained step reward) and GUI-Critic-R1.
11. **SOTA to beat.** Web-Shepherd's **34.55% WebArena-lite** result from **23.64%**, and its
    reported roughly **10x verifier-cost advantage** over GPT-4o, May 2025,
    <https://arxiv.org/abs/2505.15277>. Same trajectory split and checker are mandatory.
12. **Local example.** BrowserGym 0.14.3 with Playwright Chromium is locally runnable. Install via
    the sibling-probed `uv` environment, set `pre_observation_delay=0.0`, run click-button and
    click-checkboxes, and record AX/DOM before/after states. First demo is replay-only and no-key.

### 4. BALROG policy/value search with relative comparisons

1. **Name and pitch.** **Jev Relative-Tree:** use Jev Choice for a policy prior over legal text
   actions and pairwise Choice for child-state comparisons; use Score only as telemetry, never as
   the sole absolute value.
2. **Loop.** Serialize the compact environment state, legal action list and a candidate successor
   summary generated by code. Ask one Choice over actions and parallel pairwise Choices over a
   small beam. Expand only the top two candidates, with a fixed call budget. Code owns all game
   transitions and the final score.
3. **Fit test.** (a) Legal actions are finite and text-state; (b) BALROG turns are slow enough for
   130 ms while repeated parallel judgments make shallow search affordable; (c) environment score
   and progress are external GT. Relative comparison directly addresses the documented absolute
   Score saturation trap in typesafe-chess.
4. **Why next-gen.** Agent Alpha and WebDreamer use search, but their evaluator is an expensive
   model or trained reward. Jev makes pairwise search over 255-or-fewer actions a cheap API primitive
   and keeps the search policy inspectable. This is not pretending a classifier is a pixel policy.
5. **Ground truth and prevalence.** Use BALROG's fixed six-environment board and environment
   progress. Start Crafter and TextWorld, where the local probe works; do not claim the BALROG NLE
   wrapper works on arm64 until its segfault is fixed. Positive “progressing action” prevalence is
   measured from the checker after the run, not authored.
6. **Cheapest falsifying experiment.** 100 episodes, 50 dev/50 held-out, cap 20,000 calls (about
   $0.57), same seeds and action budgets for no-op, random, common-action, deterministic script,
   greedy Jev and Relative-Tree. Bar: average progress > the checked BALROG **58.1%** aggregate
   reference and Crafter > **76.8%**, or a Pareto win of equal progress at >=2x lower calls; kill
   if relative Choice does not beat greedy Jev or the scripted floor.
7. **Map location.** Real-time applications and AI Map Reduce over game trajectories; Classification,
   Ranking and Scoring.
8. **Nearest dead relative.** `typesafe-chess` MCTS improved to 25 cp loss but had only 20 positions,
   while neo4jev/drone were smokes. This design transfers the successful relative comparison to
   text-state games and preregisters 100 episodes, rather than citing a two-game demo.
9. **First build.** Install Crafter in a fresh uv environment (`uv pip install crafter`) and use
   its inventory, achievements and semantic map JSON. Add TextWorld after that. Run random/scripted
   controls without Jev; then add a pinned `jev-1.13.0` client with zero retries. BALROG's NLE and
   MiniHack wrappers segfault on this Mac; plain NLE is a separate later experiment, not a hidden
   dependency.
10. **Novel mechanism.** Direct typed pairwise successor comparison as a search evaluator, no
    distillation and no absolute-score action policy. Closest work is Agent Alpha's step MCTS,
    WebDreamer, Motif/ONI and typesafe-chess.
11. **SOTA to beat.** Checked BALROG board **58.1% average progress** (Gemini-3-Pro, Feb 2026),
    Crafter per-environment **76.8%**, <https://balrogai.com/>; benchmark paper
    <https://arxiv.org/abs/2411.13543>. The board's later 68.3 row is marked unverified in the
    report; do not use it as the bar until independently checked.
12. **Local example.** Crafter and TextWorld both ran on arm64 in the local probe. Use the exact
    CMake workaround only for BALROG itself; do not spend on that path before the plain env arm is
    green. First demo is one Crafter episode with all candidate states logged and no API key.

### 5. ViZDoom symbolic real-time tactical controller

1. **Name and pitch.** **Jev Symbolic Doom:** run an unpaused ViZDoom Defend-the-Center controller
   over labels, game variables and object state; Jev chooses a legal action and confidence gates
   whether to act, hold or call a deterministic aim routine.
2. **Loop.** Every 4–8 game frames, code emits enemy labels, relative boxes, health, ammo and last
   action. Ask Choice `turn_left/turn_right/fire/hold` plus Noul `target_visible`, `dangerous_now`
   and `shot_would_be_wasted`. Code computes coordinates and cooldowns; Jev never sees pixels or
   performs arithmetic.
3. **Fit test.** (a) The answer space is four legal actions and three booleans. (b) ViZDoom steps
   cost under 1 ms locally while Jev costs about 130 ms, so the research question is explicitly
   whether event-triggered judging can beat the slow VLM latency regime, not whether Jev is a
   frame-rate policy. (c) kills, survival and damage are engine GT. This is a clean text-symbol
   comparison; raw VideoGameBench is not like-for-like and is not used for the primary claim.
4. **Why next-gen.** Current visual agents are either paused per frame or too slow. A symbolic
   event-triggered Jev layer can act at a tactical cadence and let deterministic code handle
   high-rate aim. The mechanism tests the boundary between a fast typed semantic judge and a slow
   pixel planner.
5. **Ground truth and prevalence.** ViZDoom's kill count over 600 frames, survival, ammo and
   episode time are GT. `target_visible` prevalence is measured from the bundled labels, not
   authored. Use fixed seeds and count a crash or API timeout as zero.
6. **Cheapest falsifying experiment.** Run 100 episodes of Defend the Center, 50 dev/50 test, with
   no-op, random, turn/fire script, Jev event-trigger and Jev every-event arms. Cap 5,000 calls
   (about $0.14). Bar: beat the published **12 kills/600 frames** symbol-agent reference while
   unpaused, with p95 action-decision latency <=250 ms; kill if the deterministic script wins or
   Jev's target parsing cannot beat random.
7. **Map location.** Real-time applications; Classification, Detection and Routing.
8. **Nearest dead relative.** NanoJev reports 128/128 on ViZDoom Basic while raw Jev reports 56/128,
   and the drone work had no seed-matched advantage. This proposal is narrower: symbolic Defend
   Center, event-triggered, with a deterministic aim floor and a wall-clock bar. It must not claim
   raw visual generality.
9. **First build.** Install the arm64 wheel `uv pip install "vizdoom==1.3.1"` and use the bundled
   scenario. The local probe ran `basic`, `defend_the_center` and `deadly_corridor`. First demo
   serializes the labels buffer and logs action/kill latency; no Jev call is needed for the control
   arm.
10. **Novel mechanism.** A calibrated typed judge gates event-triggered tactical decisions over
    symbolic object state while a deterministic controller handles frame-rate mechanics. Closest
    work is See-Symbolize-Act, NanoJev and AgileThinker; none uses Jev's API probability as the
    reflex/planner switch in this environment.
11. **SOTA to beat.** See-Symbolize-Act's symbol-agent reference **12 kills per 600 frames** on
    Defend the Center, Mar 2026, <https://arxiv.org/abs/2603.11601>. Report the mode explicitly:
    its game is paused every frame, while the proposed primary bar is unpaused; a paused re-run is
    required for like-for-like.
12. **Local example.** `vizdoom==1.3.1` runs on this M3 Ultra with bundled scenarios. Start with
    `DefendTheCenter-v0`, deterministic labels, and a 100-episode no-key replay. Do not install a
    ROM or use the user's Chrome.

## Next ten after the top five

6. **Speculative Browser Launch** — Jev predicts the next DOM action and launches only when its
probability clears a fixed selective-branch bar; GT is next-action accuracy and wall time; target
Speculative Actions' 55% next-action accuracy / 20% latency reduction
(<https://arxiv.org/abs/2510.04371>).

7. **AX conformal action set** — calibrate a one-or-small-set element Choice per app, abstain on
larger sets, and compare WebArena **74.3%** with >=95% held-out action coverage; GT is task checker.

8. **MacArena AX transition critic** — verify before/after accessibility-tree deltas and repair
Calculator/Finder/TextEdit actions; target MacArena CUA **31.83%** on 421 tasks
(<https://arxiv.org/abs/2606.06560>).

9. **GUI done-claim CUSUM** — feed Jev `milestone_reached` and `done_claim_supported` into a
running alarm; target CURA's **42.3% failure catch at 0.066 false alarms**
(<https://arxiv.org/abs/2608.27808>).

10. **ViZDoom candidate-target verifier** — deterministic label proposals plus a Jev target Choice;
beat the **12-kill/600-frame** symbol target without asking Jev to parse pixels.

11. **NetHack text tactical shield** — use plain NLE (not the arm64-segfaulting BALROG wrapper) and
Choice flee/fight/search; target BALROG NetHack **13.2% progress** with engine score as GT.

12. **Crafter resource-risk controller** — parallel hunger/health/craft Nouls and a safe macro Choice;
target BALROG Crafter **76.8% progress** and progress/$.

13. **LLM Chess legal-move selector** — Jev selects among deterministic legal/Stockfish candidates;
beat LLM Chess **1613.8 Elo at $0.058/move** while disclosing Stockfish as a non-LLM ceiling.

14. **Chess search-depth allocator** — a Jev Score decides shallow/deep engine budget; target same
1613.8 Elo with >=50% fewer deep searches, GT Stockfish/game result.

15. **lmgame-Bench symbolic critic** — Jev scores after-states in 2048/Tetris; compare only to the
published LLM rows (not TD-n-tuple/51M-line specialist records), with board score as GT.

## Explicit no-claims

- No idea above is live, scored, wired into omp, or a SOTA result from this pane.
- “SOTA to beat” is a published target; it is not a claim that the proposed observation type is
  comparable. Where the source is screenshot/pixel, the proposed AX/RAM/text arm must be labeled a
  separate text-state track.
- No probability threshold is portable across games/apps. Tune only on a dev split and report the
  held-out split, model id `jev-1.13.0`, calls, tokens, dollars, p50/p95, 429s, timeouts and
  repeated-run variance.
- No LLM judge is allowed to grade Jev. The environment checker, engine score, task checker or
  later human action is the oracle. Audit PASS and FAIL grader errors before any SOTA comparison.
