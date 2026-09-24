# WIZARD_IDEAS_CC: next-gen Jev for computer use and games (Claude wizard)

Author: SapphireFalcon (pane 3, claude-opus-5), 2026-09-24. Bead `jev-jy7t.1`. This file follows
BRIEF.md section 9, which supersedes sections 1 and 8 where they conflict. Every section 8 field
plus fields 10-12 is filled for the top 5.

**What I read:** BRIEF.md, ledger-20260924.md, outside-scan-20260924.md, and the four research
files (research-classifier-uses.md, research-guidance.md, research-sota.md, local-env-probe.md).

**My own sources:** web searches plus primary papers read this session. They are listed in section 5.
Where one of my numbers is not in the four files, I read it in the paper's arXiv HTML myself.

**Limits of this work:** it was read-only. I used no key, made no model API calls and ran no local
models. I did not open any other WIZARD_* file. [I] marks my own arithmetic or judgment.

## 0. The lens: four findings that decided the ranking

1. **Published LLM agents lose on the clock, not only on knowledge.**
   - PokéChamp, the LLM champion of Pokémon Showdown, lost about a third of its human-ladder games by
     exceeding the turn timer. Its 76% win rate is counted over the other two thirds only
     (arXiv 2503.04094 §5, ladder paragraph; the clock is 150 s per game plus 15 s per turn).
   - V-Droid's trained 8B verifier takes 4.3 s per step on AndroidWorld, and Agent-S2 takes more than
     25 s (arXiv 2503.15937 §2).
   - In Orak's real-time StarCraft II, every LLM scores 0 on hard, at 19.6-99.2 s per step
     (research-sota G8).
   - In OSWorld, LLM calls dominate task latency; for GTA1, planning and judging are 91-96% of it
     (OSWorld-Human, arXiv 2506.16042).
2. **The strongest LLM search recipes need token log-probabilities that frontier APIs no longer
   expose.**
   - MC-DML, the best LLM planner on Jericho, gets its action prior from the top-20 log-probs of
     `gpt-3.5-turbo-0125` (arXiv 2504.16855, implementation details).
   - V-Droid scores candidates by prefill.
   - KnowNo needs likelihoods for each option.
   - Jev returns a calibrated distribution over up to 255 options as its native output. That is the
     property no LLM API gives cheaply, and every top idea below uses it.
3. **The scripted-floor trap.** Guidance rule 4 requires beating a scripted bot with zero model
   calls. When the state is symbolic, scripted bots dominate:
   - Freeway, Snake, Pong, Breakout.
   - Defend the Center (turn and fire).
   - 2048, Tetris and Sokoban, where the non-LLM records are thousands of times the LLM rows.
   - StarCraft II's built-in AI, which a scripted controller beats (research-sota §3.1).

   In those games only an "LLM-agent row" can fall, never the overall SOTA. I therefore put first the
   games where no scripted bot is competitive: Pokémon battles (PokéChamp already beats the
   heuristic Abyssal bot 84% of the time) and Infocom text adventures.
4. **20 requests/s is the real ceiling** (1,200/min, research-guidance §2), along with 250k tokens/s
   and 32k tokens for the state plus the longest question.
   - Every search loop below batches up to 16 nodes into one request, with a question per node that
     points at `nodes[i]`.
   - pg-jev measured 100% accuracy at 1-20 rows per request and 77-94% at 80 (outside-scan A0).
   - 16 nodes of about 700 tokens is 224k tokens/s at 20 req/s, just under the token cap [I].

Every experiment below keeps guidance rules 1-15: pin `jev-1.13.0`, preregister, compare text-state
to text-state, run four floors, run repeated episodes, and report cost and time. Jev never grades
itself.

## 1. The five best, best first

### 1. PokéJev: clock-proof expectiminimax for Pokémon Showdown

1. **Pitch.** Put Jev in all three LLM slots of PokéChamp (action prior, opponent model, leaf value).
   The saved clock then goes into search depth, so the agent never loses on time, which cost the
   GPT-4o version a third of its ladder games.
2. **The loop.** One cycle per Showdown `|request|`, about 25 turns per battle.
   - **State:** JSON built from the poke-env battle object:
     - our active Pokémon and bench (HP, status, boosts, moves with PP, tera);
     - what the opponent has revealed, plus Smogon usage-stat priors for its unrevealed moves;
     - the field (weather, terrain, hazards) and the last 3 turns of the log.
   - **Questions at the root, in one request:**
     - `self`: a Choice over our legal actions (at most 4 moves × tera/no-tera + 5 switches = 13),
       with the list built by code.
     - `opp`: a Choice over the opponent's plausible actions: revealed moves, top usage-stat moves
       and revealed switches, about 20 at most.
   - **Search:**
     - Branch on our actions in full. Branch on opponent actions until their Jev probability sums
       to 0.9 or more.
     - PokéChamp's local damage calculator (code) produces the after-states.
     - Leaves are judged relatively: a Choice {A better, B better, even} between sibling
       after-states, 16 leaves per request. Absolute Scores saturate once one side leads
       (typesafe-chess; Agent Alpha, research-classifier-uses §1).
     - The search is anytime: it stops at 5 s per turn, so it cannot time out.
   - **Budget:** about 20 requests per turn, about 1 s at 20 req/s [I].
3. **Fit test.**
   - **Defined answers:** yes. Every option comes from the simulator's legal-move list or from
     usage stats.
   - **Only because it is cheap and fast:**
     - About 300 leaf judgments per turn inside a 15 s increment.
     - Jev: about 3.5M input tokens per battle ≈ $0.15, and about 1 s per turn [I].
     - Haiku at list price for the same 300 judgments: ≈ $0.3-0.4 per turn (≈ $8-10 per battle).
       Run serially at its ~4 s p50 (ledger §1, 77-way Choice), 300 judgments would take about
       20 minutes per turn [I].
     - Jev's stability (0-2 flips against 9-97 for LLMs) makes the tree reproducible and the leaf
       judgments cacheable by state hash.
   - **An outcome grades it:** the Showdown engine's win or loss, human actions in public replays,
     and the public PokeAgent ladder's rating.
4. **Why this is next-gen.** The LLM recipe samples a few moves and judges them slowly. Here the
   search is exhaustive and weighted by a calibrated opponent distribution, and it finishes inside
   a human's clock.
5. **Ground truth and prevalence.**
   - Battles: a 50% base rate against an equal opponent.
   - Replays: `huggingface.co/datasets/milkkarten/pokechamp` (2M battles) and
     `jakegrigsby/metamon-parsed-replays` (3.5M), both linked from pokeagent.github.io/track1.html.
   - The replay test has a published bar: PokéChamp's action-prediction table gives top-1 accuracy of
     26-30% for the player and 13-16% for the opponent, against 7% and under 1% for random
     (arXiv 2503.04094, Table 1).
6. **Cheapest falsifying experiment.**
   - **Stage A (offline, ≈ $0.13):**
     - Setup: 2,000 held-out Gen 9 OU turns from 1400-1600 Elo replays, with a fixed seed.
     - Question: predict the player's actual action and, from the player's view, the opponent's
       action.
     - Bar: top-1 ≥ 30% for the player and ≥ 16% for the opponent, and a log-loss better than the
       usage-frequency baseline.
     - Kill: worse than usage frequency.
     - Cost: 2,000 requests × ~1.5k tokens.
   - **Stage B (local battles, ≈ $30 per 200 battles [I]):**
     - Setup: Gen 9 OU with PokéChamp's own team set and the clock on.
     - Opponents, 200 battles each: Abyssal, poke-env `SimpleHeuristicsPlayer`, `MaxBasePowerPlayer`,
       random, and PokéChamp running on a free OpenRouter backend (`dots-3-note-preview:free`) in the
       same harness.
     - Bar: ≥ 84% against Abyssal (PokéChamp-GPT-4o's published figure), zero losses on time, and
       a Wilson lower bound above 0.5 against free-LLM PokéChamp.
     - Kill: below 70% against Abyssal, or more than 1% of battles lost on time.
   - **Stage C (public PokeAgent ladder, Gen 9 OU):** play until the rating deviation is 40 or
     less; report GXE and FH-BT next to the ladder's PokéChamp and Metamon baselines.
7. **Map location.** Use-case map: Gaming (the "Real-time applications" category). Decision shapes:
   Classification (the opponent model), Ranking (the prior) and Scoring (relative leaf value).
8. **Nearest dead relatives.**
   - Tool selection lost to always-bash, 192 vs 252 (README:209).
   - typesafe-chess lost 168-190 cp per move with a single call.
   - Both had a single-shot Choice picking an action with nothing to correct it.
   - Here search corrects the prior, the engine grades the result, and the floors include heuristic
     bots that PokéChamp already beats. The flat Choice follows R85, where a hierarchical Choice lost
     to a flat one.
9. **First build.**
   - `work/poke-jev/`: a poke-env `Player` subclass that calls the official Python SDK (RULE 14),
     plus a replay-prediction scorer.
   - The PokéChamp clone is wrapped, never patched.
   - Keyless runs fall back to a heuristic agent and print NOT_RUN.
   - It is not an omp surface. It is the public demo, and its batched search engine is shared with
     idea 2.
10. **Novel mechanism.**
    - The calibrated distribution over opponent actions is used directly as the chance-node weights.
    - All leaves are judged in batched parallel questions under a hard clock, so the search is
      anytime and never times out.
    - Closest published work: PokéChamp (an LLM samples actions, predicts the opponent and scores
      values; GPT-4o; loses on time) and Metamon (offline RL, no search).
11. **SOTA to beat.**
    - PokéChamp (ICML 2025, arXiv 2503.04094, March 2025):
      - 84% against Abyssal and 76% against PokéLLMon;
      - projected Elo 1300-1500;
      - about a third of ladder games lost on time.
    - Specialist ceiling: Metamon policies at 70-83% GXE on the human ladder
      (github.com/UT-Austin-RPL/metamon).
    - PokeAgent Challenge (arXiv 2603.15563, March 2026): RL leads LLM agents.
    - I claim the LLM-agent record plus cost and latency. Metamon is the stretch goal.
12. **Local example.**
    - Install:
      `git clone https://github.com/smogon/pokemon-showdown && cd pokemon-showdown && npm install && node pokemon-showdown start --no-security`
      (Node 22.22 is present), then
      `uv venv --python 3.12 && uv pip install poke-env`, then
      `git clone https://github.com/sethkarten/pokechamp`.
    - First demo: 20 battles of Jev against Abyssal on the local server, with the win rate and
      seconds per turn printed.

### 2. Jev-PUCT for Infocom games (Jericho): the MC-DML search without log-probs

1. **Pitch.** The best LLM planner for Infocom games gets its prior from a retired model's token
   log-probs. Jev gives a calibrated prior over every valid action natively, so the same search runs
   today, with more simulations per step.
2. **The loop.**
   - PUCT with MC-DML's own budget: 50 × |valid actions| simulations per real step. Zork1 averages
     15.96 actions per step, so about 800 simulations [I].
   - Each newly expanded node gets one Choice over its valid actions (Jericho's `get_valid_actions`:
     the same valid-action handicap and save/restore that MC-DML used). That Choice is the prior.
   - Variant A keeps MC-DML's rollouts, for a like-for-like comparison.
   - Variant B replaces rollouts with a leaf value: a relative Choice between siblings, or a Score
     from 0 to 4 on progress.
   - The node state is `{observation, look, inventory, last 3 actions, score}`, about 700 tokens.
   - 16 nodes go into each request. At 20 req/s that is about 320 node evaluations per second,
     roughly 2.5 s per real step [I].
3. **Fit test.**
   - **Defined answers:** yes. The valid-action list comes from the Z-machine.
   - **Only because it is cheap and fast:**
     - About 80k node priors per game run: 100 steps × 800 simulations, the upper bound with no
       tree reuse [I].
     - Jev: ≈ 56M tokens ≈ $2.4 and about 5 minutes per run [I].
     - Without log-probs, MC-DML's own fallback is self-consistency, meaning several sampled answers
       per node. With an LLM that is hundreds of dollars and days of wall-clock per game [I].
   - **An outcome grades it:** the game score, reported by the engine.
4. **Why this is next-gen.** Prior-guided search at a simulation budget an LLM prior cannot afford,
   with a stable prior, so a tree can be rerun exactly.
5. **Ground truth.**
   - MC-DML's 9 Jericho games: Zork1 (max score 350, walkthrough 396 steps, 9.12 steps per reward),
     Deephome, Ludicorp, Pentari, Detective, Library, Balances, Temple and Ztuu.
   - Rewards are sparse; prevalence does not apply.
6. **Cheapest falsifying experiment.**
   - **Setup:** Zork1, Deephome and Detective, 3 runs each, at MC-DML's step limit and simulation
     count.
   - **Arms:** uniform-prior PUCT (the floor), random valid actions, a do-nothing "look" loop, and
     Jev-PUCT variant A.
   - **Bar:** Jev-PUCT reaches at least MC-DML's own no-memory LLM-prior PUCT ablation on all 3
     games (Table 4: Zork1 31.67, Deephome 51, Detective 320), and beats uniform PUCT by 5 or more
     on Zork1.
   - **Stretch:** full MC-DML (48.66 / 67 / 346.67).
   - **Kill:** Jev-PUCT is no better than uniform PUCT on 2 of the 3 games, meaning the prior adds
     nothing.
   - **Cost:** ≈ $21 for the 9 runs [I].
7. **Map location.** Use-case map: Gaming. Decision shapes: Ranking (the prior) and Scoring (the
   value).
8. **Nearest dead relatives.**
   - R99 and R100: Jev predicting which tool results a later turn will need reached only AUC
     0.689-0.714. Predicting future usefulness is a measured weakness.
   - MC-DML itself found the bare LLM policy poor without search.
   - The difference: search corrects a weak prior, and the engine grades the result.
9. **First build.**
   - `work/jev-if/`: a Dockerfile (arm64 Python 3.12 + jericho + `en_core_web_sm`), about 200
     lines of PUCT, and batched questions through the official Python SDK.
   - It shares the batched evaluator with idea 1.
   - It is a public demo, not an omp surface.
10. **Novel mechanism.**
    - A native calibrated prior over all valid actions.
    - Many tree nodes judged in one request.
    - No log-prob access and no LLM rollouts.
    - Closest published work: MC-DML (ICLR 2025), MC-LAVE-RL and PUCT-RL, and typesafe-chess (MCTS
      over Jev, 25 cp per move).
11. **SOTA to beat.**
    - MC-DML (arXiv 2504.16855, April 2025), Table 1: Zork1 48.66 ± 1.89, Deephome 67, Ludicorp
      19.67, Pentari 70, Detective 346.67, Library 21, Balances 10, Temple 8, Ztuu 23.67.
    - In the same handicapped setting: XTX at 56% (research-sota G5).
    - TALES (o3 at 58.7%) and TextQuests (74.2%) use no valid-action handicap, so they are a
      different protocol and I do not compare against them.
12. **Local example.**
    - Install:
      `docker run --rm -it -v "$PWD":/w python:3.12-slim bash -lc 'apt-get update && apt-get install -y build-essential && pip install jericho && python -m spacy download en_core_web_sm'`.
      Docker 29.4.0, aarch64, 32 CPUs, is running on this Mac; I checked with `docker info`.
    - Game files come from the z-machine-games archive named in the Jericho README.
    - Native development environment: TextWorld 1.7.0, which lists admissible commands and was run by
      the local probe.
    - First demo: 20 real steps of Zork1 with the tree printed.
    - **I disagree with research-sota §4**, which says Jericho has no path: "Linux-only, contexts
      over 100K tokens". Linux runs in arm64 Docker here, and a PUCT node needs only the current
      observation, not a 100K-token history.

### 3. A training-free verifier in V-Droid's slot on AndroidWorld

1. **Pitch.** V-Droid showed that a mobile agent should verify candidate actions rather than
   generate them. It needed a Llama-3.1-8B verifier trained on 110K annotated samples, at 0.7 s per
   decision. Jev fills that slot with one Choice per step and no training.
2. **The loop, per step.**
   - Code extracts candidate actions from the Android accessibility tree: about 20 interactive
     elements on average (V-Droid §2.2), plus V-Droid's default actions (open app, wait, home,
     back, complete, answer).
   - One request carries three questions:
     - a Choice over the candidates: "which makes the most progress on this task", with the action
       history;
     - a Noul: "the task is already complete";
     - for `input {content} to <field>`, a Choice over text spans that code extracts from the
       instruction (quoted strings, names, numbers, copied verbatim). This covers jaggedness #2 and
       #9: Jev chooses a span and never writes one.
3. **Fit test.**
   - **Defined answers:** yes. Code enumerates the candidates and the spans.
   - **Only because it is cheap and fast:** Jev takes about 0.15-0.2 s per decision [I], against
     V-Droid's 0.7 s on 2× RTX 4090 and Agent-S2's more than 25 s per step, at about $0.0001 per
     step [I].
   - **An outcome grades it:** AndroidWorld's programmatic task checkers.
4. **Why this is next-gen.** A verifier-driven phone agent with no training set and sub-second
   decisions, so the agent runs at interactive speed.
5. **Ground truth and prevalence.** AndroidWorld's 116 tasks with their checkers; human success is
   80.0%. Floors: do nothing, a random candidate, and always the most common action type.
6. **Cheapest falsifying experiment.**
   - **Setup:** all 116 tasks × 3 seeds at V-Droid's step budget, text-only observation.
   - **Bar:** success rate of 29.8% or more (half of V-Droid's) with p50 decision time of 300 ms or
     less is a Pareto point. 59.5% or more is the SOTA claim.
   - **Kill:** below 20%, or not clearly above the floors.
   - **Cost:** about 21M tokens ≈ $0.9 [I].
7. **Map location.** Use-case map: AI Automation Software. Decision shapes: Ranking and Verification.
8. **Nearest dead relatives.**
   - Tool selection vs always-bash.
   - Skill routing: top-1 0.800, failed promotion.
   - R85: the hierarchical Choice lost.
   - The difference: mobile screens offer about 20 options, a programmatic checker grades the result,
     and the constant floor is measured.
9. **First build.**
   - `work/droid-jev/` wraps the V-Droid repo's action extraction; only the verifier call is
     swapped.
   - Later: the same Choice over macOS AX elements could serve our own Mac agents (next-10 #14).
10. **Novel mechanism.**
    - A verifier-driven GUI agent with no training.
    - Termination decided by a calibrated Noul.
    - Typing done by choosing a span, not by generation.
    - Closest published work:
      - V-Droid, with a trained verifier.
      - GTA1, where a judge picks among sampled proposals.
      - The step-level cascade, a ModernBERT trained on 300 trajectories.
11. **SOTA to beat.**
    - V-Droid (arXiv 2503.15937, March 2025): 59.5% on AndroidWorld, 4.3 s per step, 0.7 s per
      decision, text-only.
    - The overall board (screenshot agents, a different category): 100% self-reported (August 2026)
      and MAI-UI-2B at 49.1% (January 2026) (research-sota C8).
12. **Local example.**
    - Install:
      `brew install --cask android-commandlinetools` (needs approval), then
      `sdkmanager "platform-tools" "emulator" "system-images;android-33;google_apis;arm64-v8a"`,
      then an AVD `AndroidWorldAvd` (Pixel 6), `emulator -avd AndroidWorldAvd -no-snapshot -grpc 8554`,
      then `git clone https://github.com/google-research/android_world` with its requirements.
    - research-sota rates this PARTIAL: the README's macOS emulator path, unverified here.
    - First demo: 5 contacts and clock tasks.

### 4. A zero-training certified step monitor for computer-use agents

1. **Pitch.** CURA showed a certified sequential alarm can stop failing computer-use runs early.
   Because it forbids extra model calls, it barely beat a token count. Per-step Jev Nouls cost about
   $0.0002 per step at ~4k tokens [I], and could give the same test semantic evidence with no training set.
2. **The loop, every agent step.**
   - **State:** `{task, last k actions and the agent's own text, step index, tokens so far}`. This is
     CURA-style harness telemetry as text, with no screenshots.
   - **Parallel Nouls, one request:**
     - "repeating without progress (stuck)";
     - "the last step moved the task forward";
     - at a done-claim: "the task is actually complete".
   - **Composite:** a logistic head fit on development folds turns the answers into s_t.
   - **Alarm:** CUSUM at α = 0.10 or 0.20, CURA's certified construction.
3. **Fit test.**
   - **Defined answers:** yes, all Nouls.
   - **Only because it is cheap and fast:**
     - The monitor judges every step at about 130 ms, while agents spend tens of seconds per step.
     - A frontier overseer per step would roughly double the run's cost, which is why CURA refused
       extra calls.
   - **An outcome grades it:** OSWorld's official evaluator scores, which are programmatic, not an
     LLM judge.
4. **Why this is next-gen.** Semantic, per-step, certified oversight at the price of logging. It
   targets the failure mode CURA measured: 90% of failures end with a success claim.
5. **Ground truth and prevalence.**
   - Data: `razzant/ouroboros-osworld-verified-sonnet46` and `-opus5` (361 tasks, official per-task
     scores and every acting record), and `xlangai/ubuntu_osworld_verified_trajs`.
   - Failure prevalence depends on the agent: 71 of 361 (19.7%) for CURA's pipeline. It must be read
     from the chosen run before preregistering.
6. **Cheapest falsifying experiment.**
   - **Setup:** one released run of 361 tasks, with CURA's 5-fold protocol on that run.
   - **Arms:** total tokens, step count, a re-implementation of CURA's telemetry composite, and Jev
     plus telemetry.
   - **Bar:** the Jev composite beats the token baseline with p < 0.05. CURA's own margin was
     Δ = +0.026, p = 0.101. It must also beat the CURA re-implementation's online recall at α = 0.10
     with realized FAR ≤ 0.10.
   - **Context, not like-for-like:** CURA's published 0.828 AUROC and 0.41 recall are on its own
     pipeline's trajectories.
   - **Kill:** Jev adds nothing significant over tokens.
   - **Blocker to check first:** if the released records hold only screenshots and no agent text,
     Jev cannot read them. Then the status is BLOCKED, not a loss.
   - **Cost:** 361 × ~40 steps × ~4k tokens ≈ 58M ≈ $2.4 [I].
7. **Map location.** Use-case map: Universal Verification and Harness Engineering. Decision shapes:
   Detection and Verification.
8. **Nearest dead relatives.**
   - Safety vetoes at 0.016% prevalence (AUC 0.750, unusable).
   - Foreman's stuck detector (AUC 0.750 against a 0.90 bar).
   - The difference: failures here run near 20%, not 0.016%; an official evaluator grades the
     outcome; the certified test bounds false alarms rather than relying on a hand-set threshold; and
     the done-claim Noul aims at the 90% false-success mode.
9. **First build.**
   - `work/cua-monitor/`: a dataset loader, batched Nouls via `work/jev-client` `askJevBundle`,
     CUSUM in about 50 lines, and a scorer using CURA's metrics.
   - **omp surface:** the same monitor as a post-tool hook over our own sessions, flagging stuck
     loops and false "done" claims. Here the ground truth is a later human action, such as a bead
     being reopened.
10. **Novel mechanism.**
    - Training-free semantic step classifiers feeding a certified sequential test.
    - Closest published work:
      - CURA: CUSUM over telemetry, no model calls.
      - The step-level cascade: a ModernBERT trained on GPT-5.2 labels; its stuck detector reaches
        93.9% accuracy.
      - Automata from traces: held-out AUROC 0.94.
11. **SOTA to beat.**
    - CURA (arXiv 2608.27808, August 2026):
      - detects 42.3% of failures a median of 31 steps early, at a realized false-alarm rate of
        0.066 (α = 0.10);
      - AUROC 0.828 against 0.802 for tokens (p = 0.101);
      - recall 0.41 vs 0.34 at α = 0.10 and 0.56 vs 0.38 at α = 0.20.
    - Step-level cascade (arXiv 2604.27151, April 2026): stuck detector 93.9% accuracy / 91.5 F1.
12. **Local example.**
    - Offline on this Mac:
      `uv pip install datasets huggingface_hub && huggingface-cli download razzant/ouroboros-osworld-verified-sonnet46 --repo-type dataset --local-dir /tmp/osw`.
    - First demo: 20 trajectories keyless (NOT_RUN), then 20 live.

### 5. A streaming injection shield for browser agents, on BrowseSafe-Bench

1. **Pitch.** Perplexity's benchmark shows that the accurate injection detectors for browser agents
   are a fine-tuned 30B model, or frontier LLMs at up to 36 s per page. Test whether a zero-shot
   130 ms Noul matches them, then put it in front of our own agents' web reads.
2. **The loop, every page or DOM observation an agent reads.**
   - Code extracts visible text, attributes and comments (where injections hide) and splits them into
     chunks of 24k tokens or less.
   - Each chunk gets one request with three Nouls, each carrying the task context:
     - "this text instructs an AI agent to do something the user did not ask";
     - "it addresses the reader as an AI or assistant";
     - "it asks to reveal or send data, or to visit a URL".
   - A page's score is the maximum over its chunks. The threshold is fit on the train split.
3. **Fit test.**
   - **Defined answers:** Nouls.
   - **Only because it is cheap and fast:** reads happen on every step. Sonnet 4.5 reaches F1 ≈ 0.86
     at up to 36 s per page; Jev takes about 0.15-0.3 s [I].
   - **An outcome grades it:** labels written by Perplexity, not by us.
4. **Why this is next-gen.** Screening every page for injection at a latency and price that let it
   run on every read.
5. **Ground truth and prevalence.**
   - `perplexity-ai/browsesafe-bench`, test split: 3,680 rows, 1,824 yes / 1,856 no (49.6%). I read
     this from the HF datasets-server statistics.
   - Page length: mean 53,769 characters (≈ 13k tokens), maximum 209,564. Chunking is required.
6. **Cheapest falsifying experiment.**
   - **Setup:** fit the threshold on 1,000 train rows; score all 3,680 test rows, then rerun twice to
     measure stability.
   - **Floors:** a constant, a keyword regex, and random.
   - **Bar:** F1 ≥ 0.86 (Sonnet 4.5) with p95 latency ≤ 1 s.
   - **Stretch:** F1 ≥ 0.904 (BrowseSafe).
   - **Kill:** F1 below 0.75, or a false-positive rate above 15% on benign pages with distractors.
   - **Cost:** about 49M test tokens plus 13M train tokens ≈ 63M ≈ $2.6, and about 5 minutes at 20 req/s [I].
7. **Map location.** Use-case map: Universal Verification and LLM guardrails. Decision shape:
   Detection.
8. **Nearest dead relatives.**
   - R80: 175 of 300 clean tool results were flagged.
   - R82: without the persona, 213/263 at 12/300 false flags, Wilson lower bound 0.758 against a
     0.80 bar.
   - The difference: prevalence here is 49.6% against about 0 in our tool output; pages are the
     attack surface the question was written for; and the labels come from outside.
   - The real risk remains jaggedness #6 (adversarial content moves the answer). The benchmark's
     distractors test exactly that.
9. **First build.**
   - `work/browsesafe-jev/` scorer.
   - **omp surface:** an annotating post-hook, never a blocking one, on `browser` and `web_fetch`
     results. It reuses the `jev_flag` plumbing; jev-l2o3's calledModel fix lands first.
10. **Novel mechanism.**
    - Zero-shot, calibrated, chunked screening with question decomposition, and a stated
      false-positive rate on benign pages with distractors.
    - Closest published work: BrowseSafe (a fine-tuned Qwen3-30B-A3B), PromptGuard-2 and
      LlamaFirewall.
11. **SOTA to beat.** BrowseSafe (arXiv 2511.20597, November 2025; COLM 2026):
    - F1 0.904, recall 0.841, balanced accuracy 0.912;
    - Sonnet 4.5 at F1 ≈ 0.86 and up to 36 s per page;
    - PromptGuard-2 at F1 0.350 / 0.360.
12. **Local example.** Offline:
    `uv pip install datasets && python -c "from datasets import load_dataset; load_dataset('perplexity-ai/browsesafe-bench', split='test')"`.

## 2. The next 10, one line each (name, loop, ground truth, SOTA)

6. **Calibrated speculator for computer-use agents.**
   - Loop: Jev predicts the actor's next accessibility-tree action and launches branches until their
     cumulative probability reaches 0.8.
   - Ground truth: actions recorded in released trajectories (OSWorld-Verified, AgentRewardBench).
   - SOTA: Speculative Actions, 54.7% accuracy and 19.5% time saved with 3 branches (arXiv
     2510.04371).
7. **MiniWoB++ against the clock.**
   - Loop: a Choice over DOM elements and instruction spans per step, scored on the original
     time-scaled reward.
   - Ground truth: the environment's reward. It runs here.
   - SOTA: binary success rate 74.9 for OrbyAgent and 71.5 for GPT-5. No LLM has reported the
     time-scaled reward (research-sota C14).
8. **Conformal element sets.**
   - Loop: a Choice over MindAct's top-50 candidates, turned into a split-conformal set at 90%
     coverage. Ask only when the set has two or more elements.
   - Ground truth: Mind2Web's human actions.
   - SOTA: element accuracy 55.1 / 42.0 / 42.1 for MindAct and 50.3 / 48.2 / 48.4 for Laya; MindAct's
     top-50 recall is 85-89%.
9. **Web PRM slot.**
   - Loop: a Choice over candidate actions.
   - Ground truth: labels in WebPRMBench, WebRewardBench and AgentRewardBench.
   - SOTA: WebArbiter-7B at +9.1 over GPT-5; Web-Shepherd; the AgentRewardBench GPT-4o judge at F1
     75.9.
10. **Real-time StarCraft II (Orak).**
    - Loop: a Choice over 72 actions from python-sc2's text state, unpaused, against the built-in AI
      on hard.
    - Ground truth: game wins.
    - SOTA: every LLM scores 0 on hard at 19.6-99.2 s per step.
    - Only the LLM-agent row can fall: a scripted controller already beats the built-in AI.
11. **Real-Time Reasoning Gym at a thousandth of the step time.**
    - Loop: a Jev reactive thread whose confidence decides when to wait for a planner.
    - Ground truth: the gym's scores.
    - SOTA: AgileThinker 0.88 / 0.45 / 0.89, published with 6-minute steps.
12. **ViZDoom Defend the Center, unpaused, from the labels buffer.**
    - Loop: a Choice over actions per 4-frame skip.
    - Ground truth: kills per 600 frames.
    - SOTA: LLMs reading symbols score 12, with the game paused. A scripted turn-and-fire floor must
      run first, and NanoJev's 56/128 result is the warning.
13. **LLM Chess, playing policy-only from the legal-move list.**
    - Loop: one Choice of at most 218 moves per turn.
    - Ground truth: the leaderboard's games.
    - SOTA: 1613.8 Elo at $4.644 per game (gpt-6-astra-high). The claim would be Elo per dollar.
14. **An AX-tree executor for MacArena, native on this Mac.**
    - Loop: Jev picks an AX element or a span to type; a free LLM plans.
    - Ground truth: MacArena's checkers.
    - SOTA: OpenAI CUA 31.83%, Qwen3-VL-4B 24.23%.
15. **A game-QA oracle over state.**
    - Loop: glitch Nouls over RAM or object state transitions from OCAtari.
    - Ground truth: bugs injected with HackAtari.
    - SOTA: VLMs stay near chance on TempGlitch (arXiv 2605.21443), a different modality.

## 3. The other 15 I considered, and what dropped each

16. **Codenames spymaster by listener simulation.** Self-play trap: word-vector bots reach 100% when
    paired with themselves (arXiv 2412.11373). Cross-play has no clean published bar.
17. **lmgame-Bench 2048, Tetris and Sokoban.** The non-LLM records dwarf the LLM rows: 625,377 for
    2048 and 51M lines for Tetris.
18. **Freeway, Snake, Pong and Breakout from OCAtari RAM.** Scripted floors dominate them.
19. **NetHack policy or online Motif.**
    - The game needs memory and long planning; the best LLM reaches only 13.2%.
    - AutoAscend's median score of 5,300 is about 3× the best neural agent.
    - BALROG's NLE wrapper segfaults on this Mac.
    - RL training on this machine is heavy.
20. **Crafter or Craftax subgoal selector.** RL dominates (MBRL 69.66% on Craftax-Classic).
21. **OSWorld-Verified with the accessibility tree only.**
    - Needs an arm Linux VM in VMware Fusion.
    - The headline results (86-90%) are screenshot agents; the best text-only result is 22.5%.
22. **Search over WebArena or VisualWebArena with a Jev value.** The images are amd64-only and the
    reference setup is a 1 TB AMI, so it does not run here.
23. **Online-Mind2Web or WebVoyager live agent.** Self-reports are saturated at 97-99%, the tasks
    need heavy typing, and they depend on live sites.
24. **Kaggle chess or poker.** The chess harness gives no legal-move list. Poker needs calibration on
    chance, and Jev said "1" on all 400 die rolls.
25. **Street Fighter III (DIAMBRA).** Needs a ROM; Elo is relative to the pool; FPX already runs a 3B
    model at 195 ms.
26. **Pokémon Emerald speedrun.** Needs a ROM; the RL-distilled record is 40:13.
27. **Semantic plan cache (APC with a Jev matcher).** No local benchmark carries APC's published
    numbers (−50.31% cost, −27.28% latency).
28. **Irreversible-action gate (CORA's Phone-Harm).** Dead relatives R81 (11/23 caught vs Haiku's
    23/23) and the 0.016% veto prevalence.
29. **Chess move prediction without training.** Maia-2 reaches 53.25% after training on 9.1B
    positions. A likely loss, and it is not a playing claim.
30. **Deterministic regression oracle for harness A/B tests.** No outside outcome: grading on our
    own labels is R28.

## 4. Where I disagree with the research files, for the duel

- **Jericho has a path** (research-sota §4 says it has none). Docker runs Linux on arm64 here
  (checked with `docker info`), and PUCT nodes need about 700 tokens, not a 100K-token history.
- **Pokémon battling belongs on the shortlist.** research-sota lists PokeAgent only as a speedrun
  stretch that needs a ROM. The battling track needs no ROM: Showdown is open-source and runs on
  Node locally. Its published LLM champion loses on the clock, which is the clearest latency failure
  I found in which the scripted floor loses too.
- **Real-time symbolic games get demoted, including shortlist items 1-3.** Guidance rule 4's
  scripted floor wins them, so a claim there is only against the LLM row. They are good latency
  demos, but not "shatter SOTA" material.

## 5. Sources I added (read this session)

- **PokéChamp** (arXiv 2503.04094):
  - the 150 s + 15 s/turn clock;
  - about a third of ladder games lost on time;
  - Table 1 action-prediction accuracy;
  - 84% / 76%.
- **MC-DML** (arXiv 2504.16855): `gpt-3.5-turbo-0125` top-20 log-probs, 50 × |A| simulations,
  Tables 1, 3 and 4.
- **V-Droid** (arXiv 2503.15937): about 20 elements per screen, default actions, 4.3 s per step and
  0.7 s per decision, Agent-S2 over 25 s.
- **CURA** (arXiv 2608.27808): the full abstract.
- **BrowseSafe:** arXiv 2511.20597, and the HF split statistics (3,680 test rows, 1,824 / 1,856,
  mean 53,769 characters).
- **Speculative Actions** (arXiv 2510.04371): 54.7% and 19.5%, the GPT-5-nano / 4.1-nano / Gemini
  2.5 Flash speculators.
- **Discriminative World Models** (arXiv 2609.02885) and **CORA** (arXiv 2604.09155): abstracts.
- **Real-Time Reasoning Gym** (arXiv 2511.04898): abstract.
- **SauerkrautLM-Doom** (arXiv 2604.07385): 178 kills vs 13 in total for the LLMs, with ASCII input.
- **OSWorld-Human** (arXiv 2506.16042).
- **The OSWorld-Verified trajectory datasets on HF:** `xlangai/ubuntu_osworld_verified_trajs` and
  `razzant/ouroboros-*`.
- **Local probe of my own** (read-only):
  - macOS 26.5.2 on an M3 Ultra with 512 GB RAM.
  - Docker 29.4.0, aarch64, running.
  - No JDK: ScienceWorld and TextWorld-Express need `brew install openjdk`.
  - 95 GiB free on `/`.
