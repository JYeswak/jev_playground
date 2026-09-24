<!-- SOTA scan by SotaScan (task agent spawned by pane 1 AmberWillow, bead jev-jy7t.1), 2026-09-24. Read-only web research with sub-scouts; no model API called. Citations are the agent's; pane 1 has not re-checked them. Self-reported leaderboard rows are marked as such where the agent said so. -->

# SOTA for computer-use and game benchmarks, and which run on this Mac (bead jev-jy7t.1)

**How this was verified.** Five sub-scouts read every number on the cited page (2026-09-24). I re-read these sources myself: OSWorld-Human, MacArena, V-Droid, Real-Time Gym, Orak, PokeAgent, See-Symbolize-Act, NanoJev, the BALROG board, the LLM Chess CSV, Quesma, the MiniWoB reward docs, Win-Fast-or-Lose-Slow, the python-sc2 README, and PyPI JSON. "Sibling" means LocalEnvProbe ran it on this M3 Ultra. [I] means my own arithmetic or judgment. Jev's cost is $0.016–0.029 per 1,000 answers and p50 is about 130 ms (ledger).

## 1. Computer use

| Benchmark | Metric | Best LLM/VLM | Best non-LLM | Time/cost published | Mode | Runs on macOS arm64? |
|---|---|---|---|---|---|---|
| OSWorld-Verified [C1] | Success rate (SR) on 361–369 Ubuntu tasks; human 72.36% | Framework: Intelligence-Indeed 90.19% @100 steps (Jul 2026). Single model: claude-fable-5 85.96% (Aug 2026). At 15 steps: GBOX 64.22% (Nov 2025). Best text-only (a11y tree): 22.5% (Oct 2024) | None | Agents take tens of minutes per task and 2.7–4.3× the needed steps. LLM calls are most of the latency. The a11y tree takes 3–26 s per observation [C2] | Turn | PARTIAL: README requires VMware Fusion running an Ubuntu-arm **Linux VM**; no KVM on Mac |
| OSWorld 2.0 [C3] | 108 long workflows | Opus 4.8: 20.6% binary. StateAct harness: 26.9% at ~9× lower cost (Jul 2026) | None | Plots reward against cost and turns | 16/108 tasks dynamic | Same VM |
| macOSWorld [C5] | 202 tasks, 30 apps | Claude CUA 44.4% (English), Oct 2025 | None | – | Turn | NO: runs on AWS Mac minis; the VMware fork needs x86 Ubuntu |
| MacArena [C6] | 421 tasks, 50 apps; screenshot + a11y tree | OpenAI CUA 31.83%; Qwen3-VL-4B 24.23%; Qwen3-VL-2B 11.40% (Jun 2026) | None | CUA averages about 14 steps | Turn | **YES**: Apple Virtualization framework (UTM) |
| WindowsAgentArena [C7] | 150+ Windows 11 tasks; human 74.5% | UI-Mate-27B 66.2% (Aug 2026) | None | – | Turn | NO: Docker plus a Win11 ISO, "WSL or Linux" |
| AndroidWorld [C8] | 116 tasks; human 80.0% | 100% (FluizAI, Kirk; self-reported, Aug 2026). MAI-UI-2B 49.1% (Jan 2026). Text-only V-Droid 59.5% (Mar 2025) | None | V-Droid: **4.3 s/step** | Turn, live emulator | PARTIAL: README uses the macOS emulator path; its Docker route warns about ARM |
| WebArena [C9] | 812 tasks; human 78.24% | WebTactix (DeepSeek v3.2) 74.3% (board updated Jun 2026). Plan-MCTS 55.3% (Feb 2026) | None (smallest trained policy: NNetNav-8B 16.3%) | Not published | Turn | NO: Docker images are amd64-only; the reference setup is an AWS AMI with 1 TB |
| VisualWebArena [C11, C17] | 910 tasks | PANDO 58.3% (May 2026). Tree search 26.4%, +39.7% relative (2024, foundational) | None | PANDO uses 58% fewer tokens than SGV | Turn | NO [I]: same stack as WebArena |
| WorkArena L1/L2/L3 [C10] | ServiceNow tasks | 90.3 (Mar 2026) / 69.4 / 11.5 (Aug 2025) | None | – | Turn | PARTIAL: local client, cloud instance |
| Online-Mind2Web [C12] | 300 live tasks | Independently verified: SeeAct/GPT-5 42.33%, $171 total. Self-reported: up to 97% | None | HAL publishes a $-vs-accuracy Pareto; Gemini 2.0 Flash 29% for $8.83 | Live web | PARTIAL: needs live sites |
| WebVoyager [C13] | 643 live tasks | 99.19%, self-reported (Mar 2026) | None | Fara-7B: $0.025/task at 73.5% (Nov 2025) | Live web | PARTIAL |
| MiniWoB++ [C10, C14] | Binary SR "used in most previous publications"; the original reward is scaled by time remaining | OrbyAgent (Claude 3.5) 74.9±1.2 (Feb 2025); GPT-5 71.5 (Aug 2025) | CC-Net (behaviour cloning + RL) reached human level (2022, foundational) | No LLM entry reports the time-scaled reward | Timer in reward | **YES**: "Linux and macOS"; sibling installed it |
| ScreenSpot-Pro / v2 [C15] | Click-in-box grounding | Pro: Indeed-UI-32B 82.7 verified (Sep 2026). v2: UI-Venus-72B 95.3 | None | – | Static | YES (static data) |
| Web reward and judge sets [C16] | Step choice; trajectory success | Web-Shepherd-8B PRM lifts WebArena-lite from 23.64 to 34.55 (May 2025). WebArbiter-7B scores +9.1 over GPT-5 on WebPRMBench (Jan 2026). AgentRewardBench: GPT-4o judge F1 75.9; rules reach precision 83.8 (Apr 2025). WebJudge agrees with humans about 85% | – | Web-Shepherd is about 10× cheaper than a GPT-4o verifier | Offline | YES (static) |

## 2. Games

| Benchmark | Metric | Best LLM/VLM | Best non-LLM | Time/cost | Mode | Runs on macOS arm64? |
|---|---|---|---|---|---|---|
| BALROG [G1] | Average % progress over 6 environments | GPT-6-Astra-Max 68.3 (2026-09-18, not checked by BALROG). Best checked: Gemini-3-Pro 58.1 (Feb 2026). Per-environment best: BabyAI 100, BabaIsAI 100, Crafter 76.8, TextWorld 75.7, MiniHack 65.0, NetHack 13.2. Best VLM: 35.7 (Apr 2025) | See rows below | **None published** | Turn | PARTIAL: README has Mac notes. Sibling: BALROG's git install failed under CMake 4.2 (retrying) |
| NetHack [G2] | Score / progression | 13.2% progress (above) | AutoAscend (symbolic) median score 5,300, about 3× the best neural agent (2021, foundational) | None | Turn | YES: sibling built nle and minihack from sdist in 88 s |
| Crafter [G3] | Score; human 50.5% | SPRING 27.3% (2023) | Curious Replay 19.4% at 1M steps (2023) | None | Turn | Likely YES (pure-Python sdist) |
| Craftax-Classic / Craftax [G4] | % of max reward at 1M steps | None found | MBRL 69.66% (above human) / 7.20% (Jul 2025) | PPO runs 1B steps in under an hour on one GPU | Turn | YES (JAX on CPU; jaxlib arm64 wheel) |
| TextQuests / TALES / Jericho [G5, G6] | Infocom game progress | GPT-6-astra 74.2% without clues (board undated). TALES: o3 58.7% (2025) | XTX 56% (2022, handicapped setting) | 500 steps; context over 100K tokens | Turn | NO: Jericho and TextQuests READMEs require Linux |
| VideoGameBench / Lite [G7] | % of game completed, **raw frames only** | Gemini 2.5 Pro 0.48%; Lite: three-way tie at 1.6% (May 2025) | None | About $30 per ~2,000 steps; "action… is now stale" | Full: real-time. Lite: paused | PARTIAL: JS-DOS runs in the browser; Game Boy ROMs are user-supplied |
| Orak [G8] | 12 games, text game state | Gemini-2.5-pro: best average rank 3.5 | – | **Real-time StarCraft II: every model scores 0 on hard.** Per-step latency 19.6 / 27.2 / 99.2 s | SC2, SF3 and Mario are paused by default | PARTIAL: SC2 through python-sc2 (README: "macOS, just install SC2"); the other games are commercial |
| Real-Time Reasoning Gym [G9] | Freeway/Snake/Overcooked. The world advances regardless and a default action is applied if the agent has not answered | AgileThinker (DeepSeek V3+R1), wall-clock with 6-min steps: 0.88 / 0.45 / 0.89. Planning agent: 0.12 / 0.04 / 0.00 (Nov 2025, ICLR 2026) | None | 0.047 s/token. Under pressure the planning agent falls 0.92→0.05 | **Real-time** | Likely YES: `pip install -e .` (not run) |
| Street Fighter III (DIAMBRA) [G10] | Elo within the tested pool | Qwen2.5-3B with FPX is best, at **195 ms** (May 2025) | – | 195–354 ms per action | Real-time | PARTIAL: Docker engine plus a user-supplied ROM |
| ViZDoom Defend the Center [G11] | Kills per 600 frames, game **paused every frame** | Symbols only: Claude-4-Sonnet 12, Gemini-2.5-Pro 12, GPT-4o 3. Frame only: 5 / 11 / 12 (Mar 2026) | No 2025–26 RL score found | Paper: "real-time gameplay infeasible" | Sync mode (turn-based) | **YES**: arm64 wheel; sibling ran it at 0.46–0.87 ms per step |
| ViZDoom Basic [G12] | Successes out of 128 | **Jev 56/128**, the same as untuned Qwen3-0.6B (author claim) | NanoJev, a fine-tuned 0.6B model: 128/128 (Sep 2026, author claim) | – | Turn | YES |
| Atari-100k / ALE [G13, G11] | Human-normalized score | Claude-4-Sonnet with symbols: Pong −3, Breakout 12 | EfficientZero V2: mean 2.428, median 1.286 (2024) | – | Turn | YES: ale-py ships the ROMs and arm64 wheels |
| Minecraft, diamond [G14] | Success | Optimus-3 0.15 (Feb 2026) | DreamerV3: every agent reaches diamonds within 100M steps (Nature, Apr 2025) | – | Real-time | PARTIAL: needs Java 8 |
| MicroRTS [G15] | Win rate | LLM track: AlliBot (qwen3:14b) 100.5; GPT-5 entry 69 (WCCI 2026) | Classic track caps compute at **100 ms per cycle** | 15-min game timeout | Real-time | PARTIAL: Java |
| Pokémon Emerald speedrun [G16] | Wall-clock to first gym | Raw VLMs about 0%. "X Plays Pokémon" runs pause the emulator (Gemini Blue took 406 h) | Heatz (LLM distilled into RL) 40:13. Top human 18 min; average human 1:22:05 | Ranked by wall-clock; Deepest used 649 steps vs Heatz's 1,608 | **Real-time** | PARTIAL: GBA ROM and emulator |
| Chess [G18–G21] | Elo; puzzles | LLM Chess: gpt-6-astra-high 1613.8±109.7 at $4.644/game (Sep 2026). Kaggle text: Gemini 3.8 Flash 1502 at 0.71¢/turn. Epoch puzzles: GPT-6 Astra 72.0% | Searchless 270M model: 2895 Lichess blitz (2024); Stockfish | $/game and ¢/turn published | Turn | YES: python-chess plus `brew install stockfish` |
| lmgame-Bench [G17] | Game scores | Sokoban 11, Tetris 125.67, 2048 7,580, Candy Crush 647, Mario 3,445 (board through about Aug 2025) | 2048 TD n-tuple: 625,377 average (2022). Tetris CBMPI: 51M lines (2013). Festival: 90/90 XSokoban levels (2020) | None | Turn | YES for four games; Mario needs a ROM |
| ARC-AGI-3 [G23] | Action efficiency vs humans (humans = 100%) | GPT-6 Astra High with an adapter: 99.9% (read Sep 2026) | StochasticGoose (CNN) 12.58% in the preview (Aug 2025) | $18.8K | Turn | YES (pure-Python wheels), but the prize track bans API calls |
| BabaIsBench (the real game) [G24] | Levels, seconds, $ | Fable 5 and GPT-5.6 Sol solve the intro; a human streamer is 4× faster than Fable 5 (Jul 2026) | – | Seconds and $ per level | Turn | Not checked |

**Where speed or cost is reported at all:** OSWorld 2.0, HAL Online-Mind2Web, Kaggle chess, LLM Chess, PokeAgent, BabaIsBench, VideoGameBench ($ per run), Orak (s/step), OSWorld-Human, V-Droid, and MiniWoB's original reward. BALROG, lmgame-Bench, AndroidWorld, WebArena and BrowserGym report no success per second.

## 3. Shortlist: where a ~130 ms typed judge has a plausible like-for-like path

1. **Orak real-time StarCraft II [G8].**
   - Target: win rate against the hard built-in AI in real time. Every LLM scored 0 there, at 19.6–99.2 s per step.
   - Why it fits: state arrives as text from python-sc2, and there are 72 discrete actions, so one Choice covers the move. Jev is about 100–760× faster per step [I]. The published failure is latency, not knowledge.
   - Risk: a scripted controller written by a coding agent, with zero model calls, reportedly beats every fair built-in AI (arXiv 2609.18996; the sub-scout read it, I did not). So only the "LLM agent" record is at stake.
2. **Real-Time Reasoning Gym [G9].**
   - Target: 0.88 / 0.45 / 0.89, published with 6-minute steps. Jev's 130 ms is about 3 tokens of the gym's time unit [I], so it could play at a step interval roughly 1,000× shorter.
   - Nobody has published results at short intervals, so success per second is open.
   - Risk: Snake and Freeway need look-ahead. A bare reactive agent scored only 0.24–0.57.
3. **ViZDoom Defend the Center, symbols only [G11].**
   - Target: 12 kills per 600 frames, with the game paused on every frame. Jev reads the labels buffer as JSON and could play unpaused. It runs locally (sibling-verified).
   - Risks: NanoJev's Basic result puts raw Jev at 56/128. A scripted "turn and fire" floor must be run first.
4. **MiniWoB++ [C10, C14].**
   - Target: 74.9 binary SR on the BrowserGym split; the time-scaled original reward is unreported for LLM agents. Jev chooses among DOM elements, and text to type is chosen as a span of the instruction. Local.
   - Risk: CC-Net (RL) already reaches human level, so the claim is against LLM agents only.
5. **AndroidWorld in V-Droid's verifier slot [C8].**
   - V-Droid, an LLM verifier scoring a discrete list of candidate actions, is the closest published match to Jev's shape: 59.5% at 4.3 s/step.
   - Jev in the same slot would be about 20–33× faster per step [I]. The realistic win is SR per second, since headline SR is saturated.
6. **Web step-reward and judge sets [C16].** Static data on fixed metrics: WebPRMBench, WebRewardBench and AgentRewardBench. The incumbents are 7–8B PRMs and GPT-4o or GPT-5 judges. Jev's Choice-over-candidates and Noul match these shapes. A Sep 2026 survey names "honest accounting of verifier cost" as an open problem ([C18]).
7. **LLM Chess, legal moves allowed [G18].**
   - Target: 1613.8 Elo. The leader spends about $0.058 per move, against Jev's about $0.00002 (roughly 2,000–3,600×) [I].
   - Policy-only nets exceed 2600, so a good prior is enough in principle. typesafe-chess MCTS lost 25 cp/move (author claim).
   - Risk: a single call lost 168–190 cp/move.
8. **lmgame-Bench Tetris, 2048 and Candy Crush, against the LLM rows only [G17].** A Score over after-states fits, it runs locally, and it is the cheapest experiment. The non-LLM records are thousands of times higher, so this is not an overall SOTA claim.

**Stretch options:** PokeAgent wall-clock (real-time, but needs a GBA stack and a ROM). The MicroRTS LLM track (the classic track's 100 ms cap is below Jev's p50). MacArena (native on this Mac, small-model floor 11–24%, but needs typing and planning). Street Fighter (the best config ran at 195 ms, but Elo is pool-relative and it needs Docker and a ROM).

## 4. No realistic path

- **Pixels are required:** OSWorld-Verified (86–90%, and a Linux VM), ScreenSpot, and VideoGameBench (whose rules ban game state).
- **Headline requires typing, is saturated, or needs cloud/x86:** WebArena and VisualWebArena, WorkArena, WebVoyager and Online-Mind2Web, WindowsAgentArena, macOSWorld.
- **RL or specialists already dominate:** Atari-100k, Craftax/Crafter, Minecraft diamond, and the non-LLM records for 2048, Tetris and Sokoban.
- **Needs memory or long planning:** NetHack (13.2%), and Jericho/TextQuests (Linux-only, contexts over 100K tokens).
- **Already saturated, and no cost metric is reported:** BabyAI and BabaIsAI.
- **Rules exclude it or the metric does not fit:** ARC-AGI-3 (API ban; action-efficiency metric) and Kaggle chess (no legal-move list).

## Sources

**Computer use**

- **C1:** os-world.github.io, verified xlsx and README (read Sep 2026)
- **C2:** arxiv.org/abs/2506.16042 (Jun 2025)
- **C3:** osworld-v2.xlang.ai (Jun 2026); arxiv.org/abs/2607.22798 (Jul 2026)
- **C5:** arxiv.org/pdf/2506.04135v4 (Oct 2025)
- **C6:** arxiv.org/abs/2606.06560 (Jun 2026)
- **C7:** arxiv.org/abs/2608.15930 (Aug 2026); WAA README
- **C8:** AndroidWorld sheet (read Sep 2026); arxiv.org/abs/2503.15937 (Mar 2025)
- **C9:** leaderboard.steel.dev/leaderboards/webarena (Jun 2026); arxiv.org/html/2602.14083 (Feb 2026)
- **C10:** huggingface.co/spaces/ServiceNow/browsergym-leaderboard (read Sep 2026)
- **C11:** arxiv.org/abs/2605.24785 (May 2026)
- **C12:** hal.cs.princeton.edu/online_mind2web (read Sep 2026)
- **C13:** leaderboard.steel.dev/leaderboards/webvoyager (Mar 2026); arxiv.org/html/2511.19663 (Nov 2025)
- **C14:** miniwob.farama.org/content/reward (read Sep 2026); arxiv.org/abs/2202.08137 (2022)
- **C15:** gui-agent.github.io/grounding-leaderboard (Sep 2026)
- **C16:** arxiv.org/html/2505.15277v2 (May 2025); arxiv.org/abs/2601.21872 (Jan 2026); arxiv.org/html/2504.08942v2 (Apr 2025); arxiv.org/abs/2504.01382 (Apr 2025)
- **C17:** arxiv.org/abs/2407.01476 (2024)
- **C18:** arxiv.org/abs/2609.02309 (Sep 2026)

**Games**

- **G1:** balrogai.com (read 2026-09-24)
- **G2:** arxiv.org/abs/2203.11889 (2022)
- **G3:** github.com/danijar/crafter (read Sep 2026)
- **G4:** arxiv.org/abs/2502.01591v3 (Jul 2025)
- **G5:** textquests.ai (read Sep 2026); microsoft.github.io/tale-suite (2025)
- **G6:** github.com/microsoft/jericho; github.com/centerforaisafety/textquests
- **G7:** arxiv.org/abs/2505.18134 (May 2025)
- **G8:** arxiv.org/html/2506.03610 (Jun 2025); python-sc2 README
- **G9:** arxiv.org/html/2511.04898 (Nov 2025)
- **G10:** arxiv.org/html/2505.19481v1 (May 2025); docs.diambra.ai
- **G11:** arxiv.org/html/2603.11601v2 (Mar 2026)
- **G12:** github.com/TianyuCodings/NanoJev (Sep 2026)
- **G13:** arxiv.org/abs/2403.00564 (2024)
- **G14:** nature.com/articles/s41586-025-08744-2 (Apr 2025); arxiv.org/html/2506.10357v2 (Feb 2026)
- **G15:** drchangliu.github.io/MicroRTS (data 2026-09-22)
- **G16:** arxiv.org/html/2603.15563v2 (Mar 2026)
- **G17:** arxiv.org/abs/2505.15146 (May 2025); huggingface.co/spaces/lmgame/game_arena_bench (read Sep 2026)
- **G18:** raw.githubusercontent.com/maxim-saplin/llm_chess/main/data/elo_refined.csv (row dated 2026-09-09)
- **G19:** kaggle.com/benchmarks/kaggle/chess-text (Sep 2026)
- **G20:** epoch.ai/benchmarks/chess-puzzles (Dec 2025)
- **G21:** arxiv.org/abs/2402.04494 (2024); arxiv.org/abs/2212.11087 (2022); festival-solver.site
- **G23:** arcprize.org/leaderboard (read Sep 2026)
- **G24:** quesma.com/blog/baba-is-bench (Jul 2026)

**PyPI:** pypi.org/pypi/<pkg>/json, checked 2026-09-24. arm64 wheels ship for vizdoom 1.3.1, ale-py 0.12.1, stable-retro, pyboy and jaxlib. nle ships Linux wheels plus an sdist.
