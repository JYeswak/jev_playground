# WIZARD_SCORES_CC_ON_COD: the Claude wizard scores the Codex wizard's ideas

Scored by SapphireFalcon (pane 3, claude-opus-5) on 2026-09-24, for bead `jev-jy7t.1`. The file
under review is `notes/deep/next-gen/WIZARD_IDEAS_COD.md`, all 407 lines, at `main` after my pull.
This was read-only work with no key and no model API calls. I fetched primary sources to check
numbers; they are listed in §3. [I] marks my own arithmetic or judgment.

## Scores at a glance

| # | COD idea | Score /1000 | One-line verdict |
|---:|---|---:|---|
| 2 | MiniWoB++ DOM action lattice | **540** | The cleanest and most runnable of the five, but it is not novel, speed does not affect its primary bar, and the SOTA row reads screenshots. |
| 1 | ReflexGate on Real-Time Reasoning Gym | **380** | The gap it names is real. At the published setting time pressure never bites, and at settings where it does, no published number exists. |
| 4 | BALROG Relative-Tree search | **360** | Searching with a copy of the simulator is not the BALROG protocol, and the 6-environment average cannot be computed on this Mac. |
| 3 | Web step verifier and self-healer | **340** | Good slot, wrong bar. The Web-Shepherd lift needs WebArena-lite (amd64-only) and a GPT-4o-mini policy, which is a paid model we may not run. |
| 5 | ViZDoom symbolic tactical controller | **300** | Honestly framed, but the scripted turn-and-fire floor will very likely win, and the reference is 2 seeds of a paused game. |

Taken together, three of the five top ideas (#1, #4, #5) sit in the scripted-floor zone: symbolic
games where a bot with zero model calls is the real competitor, so a win can only ever be against
the LLM row. One (#3) sets a bar that cannot be run here. COD's file is careful. It is marked
PREPARED-NOT-MEASURED, lists four floors on every row and has an explicit no-claims section, but its
ranking does not act on those constraints.

## 1. The five best, scored

### COD #1 · Jev ReflexGate on Real-Time Reasoning Gym: 380

(a) **Novelty: moderate.** research-classifier-uses gap 1 (a calibrated probability deciding when to
wait for the planner) is a real gap. The closest published work is AgileThinker's fixed
reactive-plus-planning threads, Lumine and Game-TARS's learned "think when necessary", and
DPT-Agent's state machine. Using the confidence of an outside classifier as the switch is new as far
as the abstracts say.

(b) **Fit test: not decisive.** The defined answers pass.
- The "only because fast" leg fails at the published setting. The wall-clock table gives 6-minute
  environment steps, about 8,000 tokens at 0.047 s per token (arXiv 2511.04898 §6, checked). Jev's
  130 ms is never late there, so latency is not the variable being tested.
- The loop also runs a "sub-millisecond deterministic reflex", which is code we would write. When
  the reflex acts, it earns the score. The file never separates Jev's contribution from the reflex's
  (credit attribution).

(c) **SOTA like for like: no.**
- AgileThinker's 0.88 / 0.45 / 0.89 is at 6-minute steps. In the token-budget simulation at medium
  cognitive load, a planner with 32k tokens per turn scores 0.96 on Freeway, 0.96 on Snake and 0.84
  on Overcooked (Table 7, checked). So a slow planner wins once time pressure stops binding, and a
  per-step classifier cannot plausibly beat that on Freeway car timing (jaggedness #2) or Snake
  lookahead.
- At the short step intervals where Jev's latency would matter, nobody has published a number
  (research-sota §3.2). The result there is a new Pareto point, not a SOTA claim.
- The bar's escape hatch, "or beat the deterministic reflex by ≥10%", lets a result pass that beats
  no published number.

(d) **Runs on this Mac: unverified.** research-sota calls it "Likely YES", but the local probe did
not run it. COD says to confirm this before spending, which is correct.

(e) **Experiment: partly sound.** It has floors, a dev/test split and a call cap. It lists "four arms"
and then names five, and the escape hatch weakens the bar.

(f) **Payoff: small.** These are three toy games whose scripted or code-as-policy solutions are well
understood. It becomes interesting only as a demo of calibrated gating.

### COD #2 · MiniWoB++ DOM action lattice: 540

(a) **Novelty: low.** A Choice over code-enumerated `{element, operation}` pairs is what BrowserGym's
GenericAgent already does with element ids. The only difference is a Jev chooser in place of an
LLM. The "precondition Noul" is a small addition. Closest published work: GenericAgent on BrowserGym,
MindAct/Laya element ranking, and GUI-Actor's verifier.

(b) **Fit test: partial.** Answers are defined, and the environment checker is outside ground truth.
Speed matters only to MiniWoB's time-scaled reward. The primary bar is binary success rate above
74.9, which is indifferent to speed, so the "only because cheap/fast" leg holds only for the
secondary "≥2× success per dollar" arm.

(c) **SOTA like for like: no, and one detail is wrong.**
- 74.9 ± 1.2 is correct: I read `results/OrbyAgent-Claude-3.5-Sonnet/miniwob.json` in the
  leaderboard space, dated 2025-02-21. But that agent's README says it uses **both screenshot and
  HTML**, so a text-only Jev arm is a different observation category (guidance rule 3). GPT-5's
  GenericAgent row (71.5 ± 1.8, also checked) is the closer text reference.
- The experiment's "46 tasks × four seeds" does not match the benchmark. BrowserGym's MiniWoB
  benchmark has **125 tasks** (BrowserGym paper; cua-lite README), and the leaderboard number is
  over that set. I found no published 46-task split, and a subset is not like for like.

(d) **Runs on this Mac: yes.** The local probe ran miniwob 1.1.0 with Selenium and Chrome, and
BrowserGym MiniWoB, on this machine.

(e) **Experiment: sound but mis-sized.**
- The bar can fail. Several tasks need text that is not a span of the utterance (transform, reply,
  date entry), so the ceiling is below 100% [I].
- "Cap at 1,200 calls (the API rate cap)" confuses the per-minute rate limit with a call budget.
- The cost uses 683 tokens per answer, but DOM states run 1-3k tokens [I]. It is still under $0.2.

(f) **Payoff: modest.** CC-Net's RL already reaches human level on MiniWoB, so this is an LLM-row
claim on an old benchmark. It is still the fastest honest experiment in COD's top 5, and it tests
the element-Choice primitive every computer-use idea depends on.

### COD #3 · Web action transition verifier and self-healer ("Step Surgeon"): 340

(a) **Novelty: moderate.** A verifier with several criteria and no training, feeding a
reversible-repair policy. Closest published work: STEVE (GPT-4o labels before and after each
action), Web-Shepherd (a trained process reward model), GUI-Critic-R1, and HiViG.

(b) **Fit test: passes.** Answers are Nouls plus one Choice. Judging every step needs cheap calls,
and task checkers grade the outcome. This is the best-fitted slot in COD's list.

(c) **SOTA like for like: not runnable.**
- The bar is Web-Shepherd's 23.64 → 34.55 on WebArena-lite. I checked this in arXiv 2505.15277,
  Table 2, along with "10× more cost-effective than GPT-4o-mini as evaluator".
- That lift is a live trajectory search with a **GPT-4o-mini policy**. Reproducing it requires
  paying for GPT-4o-mini, which AGENTS.md forbids for comparators, and WebArena's images are
  amd64-only with a 1 TB AMI reference setup (research-sota C9: "NO").
- The experiment's "300 held-out trajectories, 1,500 calls" cannot measure a live search lift.
  Replaying trajectories measures verifier accuracy, not policy success.
- The runnable version is WebRewardBench, where Web-Shepherd scores 85.0%. COD did not set that as
  its bar.

(d) **Runs on this Mac: only the MiniWoB proxy,** which has no Web-Shepherd number.

(e) **Experiment: unsound as written,** for the replay-vs-live mismatch above. The kill condition
("repairs no more than no-verifier") is good.

(f) **Payoff: high if it were rebased.** The payoff is real, but the path goes through a benchmark we
cannot run.

### COD #4 · BALROG policy and value search with relative comparisons: 360

(a) **Novelty: low to moderate.** It makes relative child comparisons the evaluator. Agent Alpha
(comparison-based step MCTS) and typesafe-chess's saturation finding already point there. Closest
published work: Agent Alpha, WebDreamer, and Motif/ONI for progress rewards.

(b) **Fit test: passes on answers and outcome, weak on "only because fast".** BALROG is paused, turn
by turn. The cheapness argument holds only if the search is deep, and the design caps it at a
beam of two.

(c) **SOTA like for like: no.**
- BALROG's 58.1 average and Crafter's 76.8 come from agents with no lookahead. Expanding children
  needs a copy of the simulator, which is a different protocol, so it is not the same leaderboard.
- The 6-environment average needs NetHack and MiniHack, whose BALROG wrappers segfault on this Mac
  (local-env-probe, "Blocked").
- The escape hatch, "or a Pareto win of equal progress at ≥2× lower calls", again allows passing
  without beating anything.

(d) **Runs on this Mac: partial.** Crafter and TextWorld run; the average does not.

(e) **Experiment: floors and split are sound.** The bar mixes a number it cannot compute with an
escape hatch.

(f) **Payoff: low.** Crafter is "effectively solved by the Gemini 3 family" (research-sota: Crafter
76.8 on BALROG), and RL dominates Craftax.

### COD #5 · ViZDoom symbolic real-time tactical controller: 300

(a) **Novelty: low.** Closest published work: jev-doom-agent, NanoJev (a fine-tuned 0.6B model at
128/128 against Jev's 56/128 on Basic), and SauerkrautLM-Doom (a 1.3M classifier head; 178 kills
across 10 episodes against 13 for all LLMs combined, arXiv 2604.07385). Event-triggered gating is a
small twist on these.

(b) **Fit test: the latency leg is real,** and the engine grades the outcome.

(c) **SOTA like for like: honest but thin.**
- The 12 kills per 600 frames is correct. I checked Table 4 of arXiv 2603.11601: symbol-only
  Claude-4-Sonnet scores 12 and Gemini-2.5-Pro 12, over 600 frames, **2 seeds**, with the game
  **paused on every frame**.
- The table's best cell is 14 (Claude, frame plus ground-truth symbols). COD's comparison uses the
  symbol-only column, which is like for like, and it correctly asks for a paused rerun.
- A two-seed reference is weak.

(d) **Runs on this Mac: yes.** The local probe ran defend_the_center at 0.46-0.87 ms per step.

(e) **Experiment: the bar can fail and very likely will.** Defend the Center is a known case for
"turn and fire". The scripted floor COD itself requires is likely to meet or beat 12 kills [I].
Handing aim to a deterministic routine then leaves Jev only target choice, with little to add.

(f) **Payoff: low.** At best it is a latency demo against the LLM row.

## 2. COD's next ten: keep, merge or kill

- **6. Speculative browser launch: KEEP, merged with my next-10 #6.** It is the same mechanism. Both
  need released actor trajectories with accessibility trees; the Speculative Actions bar of 54.7% /
  19.5% is correct (arXiv 2510.04371).
- **7. AX conformal action set vs WebArena 74.3%: KILL as written, MERGE the mechanism.** WebArena
  does not run here, and pairing a coverage guarantee with an overall success-rate board is a
  category error. Move it to Mind2Web, where human action labels exist (my #8).
- **8. MacArena AX transition critic: KEEP as a follow-on.** It is native to this Mac, but the 31.83%
  bar needs typing and planning Jev cannot supply. Merge with my #14.
- **9. GUI done-claim CUSUM: KEEP, merged with my top-5 #4.** It is the same idea. COD's "1,000
  steps" trace set is too small against CURA's 361 tasks; use a released OSWorld-Verified run.
- **10. ViZDoom candidate-target verifier: KILL.** It duplicates COD #5 and faces the same scripted
  floor.
- **11. NetHack text tactical shield: KILL.** A flee/fight Choice cannot move BALROG's progression,
  which depends on depth and experience level. The AutoAscend floor (median 5,300) dominates.
- **12. Crafter resource-risk controller: KILL.** RL dominates, and a scripted survival floor would
  beat a risk Noul.
- **13. LLM Chess selector over Stockfish candidates: KILL.** Choosing among Stockfish's top moves
  makes Stockfish the player, and LLM Chess agents get no engine, so it leaks the engine. The fair
  version is policy-only over the legal-move list (my #13).
- **14. Chess search-depth allocator: KILL.** A system with an engine clears 1613.8 at any depth, so
  "match 1613.8 LLM Elo with fewer deep searches" is vacuous.
- **15. lmgame-Bench symbolic critic: KEEP only as a cheap control.** COD says itself that it is
  LLM-row-only. Low value.

## 3. Numbers I checked against their sources

| COD's number | Source I read | Result |
|---|---|---|
| AgileThinker 0.88 / 0.45 / 0.89, six-minute steps, 0.047 s per token | arXiv 2511.04898 HTML: Table 2; §6 "T = 6 minutes, ~8,000 tokens per step"; α = 0.0473 | **Correct.** Table 7 in the same paper (medium load) shows a 32k-token planner at 0.96 / 0.96 / 0.84, which undercuts COD #1's bar. |
| Web-Shepherd 23.64 → 34.55, "10× cheaper" | arXiv 2505.15277v2, Table 2 and §1 | **Correct.** The lift uses a GPT-4o-mini policy with trajectory search on WebArena-lite. |
| MiniWoB 74.9 ± 1.2 (OrbyAgent, Feb 2025) | HF space `ServiceNow/browsergym-leaderboard`: `results/OrbyAgent-Claude-3.5-Sonnet/miniwob.json` and README | **Correct** (dated 2025-02-21), but the README says the agent reads screenshot plus HTML. GPT-5 GenericAgent is 71.5 ± 1.8. |
| Symbol-only Defend the Center, 12 kills per 600 frames | arXiv 2603.11601v2, Table 4 and §3.3 | **Correct** for Claude-4-Sonnet and Gemini-2.5-Pro. Paused every frame, 2 seeds. The table's maximum is 14 with frame plus ground-truth symbols. |
| VideoGameBench 2026 board, 4.6% full real-time | antimlabs.com/vgbench | **Correct.** VG-Agent with Claude Opus 4.6, and with Gemini 3.1 Pro, each 4.6%. |
| LLM Chess 1613.8 Elo at about $0.058 per move | `maxim-saplin/llm_chess` `elo_refined.csv`, row gpt-6-astra-2026-09-03-high | **Correct:** 1613.842 ± 109.730; $4.644 per game ÷ 80.343 moves ≈ $0.058. |
| MiniWoB "46 tasks × four seeds" as the published split | BrowserGym paper and cua-lite README | **Mismatch.** BrowserGym's MiniWoB has 125 tasks. |

## 4. What COD does better than my file, stated plainly

- A four-floor requirement on every row. My top 5 names floors per idea, but not in one uniform
  column.
- A written no-claims section and the PREPARED-NOT-MEASURED status at the top.
- MiniWoB (COD #2) runs on this Mac today, as the local probe showed. My #3 (AndroidWorld) needs an
  emulator install and my #2 (Jericho) needs Docker. COD is ahead on "run it tonight".
- It keeps rate-limit and 429 accounting in every loop.

These are real strengths. The low scores come from where the ideas land, not from how carefully the
file is written.
