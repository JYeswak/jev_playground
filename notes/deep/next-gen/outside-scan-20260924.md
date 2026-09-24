<!-- Scout report by OutsideScan2 (task agent spawned by pane 1 AmberWillow, bead jev-jy7t), 2026-09-24. Read-only; no model API called. Citations are the scout's; pane 1 re-checked only the tax-doc-classifier (README:50-56 @3e95a77) and typesafe-chess (README:60-65,86-90 @9e12565) corrections; everything else is the scout's reading. Saved verbatim as input to BRIEF.md. -->

# Jev next-gen uses: grounding report (bead jev-jy7t)

## A0. The ten projects Joshua named (priority)

Across all ten, the model's output is a probability over options someone wrote in advance. One project does generate text: jev-ultrafast has a small LLM write the text for `TYPE_TEXT` (README:7). Jev itself writes none.

| Project @sha | Loop and rate | What Jev chooses (type) | What it measured (README line) | What it did not measure |
|---|---|---|---|---|
| [jev-trader](https://github.com/jarrodwatts/jev-trader) @b587759 | One Monad block, about 300 ms (README:3) | `direction` Choice {buy, sell} over a 100-block horizon; `hold` appears only when the call was late (src/model.ts:5-6,43-54; README:34) | Book read p50 18 ms, whole loop p50 100 ms, **with the mock model** (README:66-67). The deployed demo also runs the mock model (README:15) | Jev latency, direction accuracy, fill rate, P&L. model.ts:47-48 says "every few blocks" and "IOC market order", but README:3 says every block and post-only limit orders. Our repo did not run it (EVAL.md:1673) |
| [jev-ultrafast](https://github.com/browser-use/jev-ultrafast) @452c1ad | One browser step | Operation Choice {CLICK, TYPE_TEXT, SELECT, SCROLL_UP/DOWN, WAIT, DONE, BLOCKED}, plus a target Choice for each operation in the same request (README:27,45) | One Flights run in 7,073 ms (:116). Six alternating runs, 3/3 passed for both versions; median 9.450→7.092 s; browser protocol calls 1,092→101 (:118). Our oracle: top-1 20/20, 0/10 false advances (docs/demos/upstream-repro/README.md:185) | General reliability. The README says so itself ("not a general reliability benchmark", :118). No comparison against an LLM-only agent |
| [jev-drone](https://github.com/RomanSlack/jev-drone) @c0efd03 | About 2.5 Hz tactical layer inside 500/50/15 Hz loops, called only when the scene changes (:21-26,39-42) | Choice {hold_course, gap_left, gap_right, climb, brake, reacquire}, risk Score, target_truly_lost Noul (:33-37) | Baseline 17.7 m vs 77.5 m (whole course); target in view 19%→82%; 0 collisions; 80 calls, 0.11 s median (:68-73,89). **Single run.** An earlier 3-seed comparison showed no advantage (:95-98). Tunnel: 21 decisions/s (:270) | Seed-matched success. Our row is FLOOR: 287 calls, no accuracy claim (EVAL.md:1668) |
| [killmyidea](https://github.com/monteduro/killmyidea) @bc85342 | One request per idea | 8 Scores (0–4) plus category and understandability, 10 questions in total (:5-7). Code: ×25, weighted mean, KILL <50, FIX 50–64, SHIP ≥65, clarity gate 0.3 (:76-83) | A benchmark script exists (:148-160); the README publishes no numbers | Any outcome validity |
| [jev-curate](https://github.com/AkashPriyadarshii/jev-curate) @d1a3a05 | One request per dataset row; rate limit 20 rows/s (:37) | Noul plus Score 1–5 presets; keep or reject the row (:96-100) | 24.0 rows/s on a **mock** bench (:13) | Filter precision. Our run: 30/30 HTTP 200, but the clone's rule rejected 30/30 (EVAL.md:1666) |
| [jev-doom-agent](https://github.com/lukaske/jev-doom-agent) @318c32a | Next decision 400 ms after the previous one returns (src/main.ts:18) | Four Choices: movement (6), view (3), trigger (2), use (2). Confidence is the minimum of the four; failures are shown as FALLBACK (src/types.ts:4-7; server/typesafe.ts:9-21; README:20) | Nothing | Kills, survival, comparison with the offline policy |
| [jev-t-rex-runner](https://github.com/joshlarsen/jev-t-rex-runner) @4968200 | Once per new obstacle (README:5-7) | Choice {jump, duck, keep_running} and Choice {short, full}; gate at 0.5 (server/decision-service.mjs:3-4; ai/controller.js:3,236) | Nothing | Score, crash rate, latency against obstacle speed |
| [typesafe-chess](https://github.com/TholeG/typesafe-chess) @9e12565 | One move; about 350 ms in fast mode (:27). In MCTS mode each new tree node costs one call; 16 evaluations take about 3 s (:57-61,125) | Choice with one option per legal move (the policy), Score (the value), Noul for "sharp" (:22-24) | MCTS beat the single-call player 2–0 (:88). Against Stockfish on 20 positions: fast mode lost 168–190 cp on average, 5/20 best moves; MCTS with forcing-reply facts lost **25 cp**, 9/20 best (:159-165) | **No "overruled half" figure exists.** The UI only shows confirmed/overruled per move (:64-65). No usable Elo: 8 games give about ±200 Elo (:152-153) |
| [tax-doc-classifier](https://github.com/kyotofin/tax-doc-classifier) @3e95a77 | One request per page | Choice over 7 page kinds, Choice over 230 forms plus not_in_list, a second call for 5 parent forms; gate at 0.95 (:73-88) | 314 filled pages: 0 wrong. 753 blank pages covering 261 forms: 0 wrong, **38 strict errors (5.05%)** (:55-56). $0.00115 vs $0.039 per page against Sonnet; about 0.5 s vs 3.3 s (:66-67) | Scanned pages and state forms; three page kinds are untested (:94). **"261/261" is true for "wrong", false for "strict"** |
| [pg-jev](https://github.com/realZachi/pg-jev) @afd11fa | Each row; 20 rows per request, one Noul per row (:45-48) | `jev`/`jev_prob` (Noul), `jev_choice`, `jev_score` (:135-141) | 2,000 rows ≈ 3.5 s, $0.012; re-run 50 ms (:56-57). Batching accuracy: 1–20 rows 100%, 40 rows 92–98%, 80 rows 77–94% (:64-66) | Accuracy of semantic conditions; threshold calibration |

**The "three-question test" article: not found. I will not invent it.** No three-question fit test appears in any of these: Wikipedia, OpenRouter's what-is-jev post, flaviocopes.com/jev, firecrawl, langchain, getmaxim, cometapi, sanity, digitalstrategy-ai, the valyuai and gabrielanhaia dev.to posts, mindstudio, archestra, lindfors, forkast, vercel.com/i/jev-use-cases, or HN Algolia. The closest thing is ziplyne's one-question "two-second test" ([link](https://ziplyne.agency/blog/ai-that-doesnt-talk-typesafe-jev-guide)). X is not searchable from here.

## A1. Official sources

- **[Launch post](https://typesafe.ai/blog/introducing-system-one-models-and-jev).**
  - Speed and price: 70–500 ms per call; $0.042 per million input tokens; output is free.
  - Choices can have up to 255 options.
  - The Doom demo runs about 10 queries/s, about $7/hour.
  - The training method is called RLCD.
- **[evals.typesafe.ai](https://evals.typesafe.ai).** I decoded these from the chart tooltips.
  - Reference labels are the average of GPT-6 Astra and Fable 5.1.
  - All four workflows averaged: Jev 67.8% / $0.0004 / 0.4 s; sol 74.1% / $0.0836 / 23.3 s; Opus 5 73.1% / $0.1761 / 37.8 s.
  - [Agent-trace triage workflow](https://evals.typesafe.ai/agent_trace_observability): Jev 71.6% / $0.0003 / 0.5 s; luna 76.1% / $0.0025 / 14.5 s.
- **[Demos](https://docs.typesafe.ai/demos.md):** only the smart-home demo.
- **[Use-case map](https://docs.typesafe.ai/concepts/use-case-map.md):** automation, real-time "(150ms)", map-reduce over big data, universal verification, harness engineering.

## A2. awesome-jev: pinned copy vs live

- **Pinned:** `ef19300` (2026-09-17), which is `awesome-jev/README.md`.
- **Live:** [`7f1f861`](https://github.com/AnotiaWang/awesome-jev) (2026-09-24T01:52Z).
- **Size:** link entries went from 141 to 200. 101 were added and 42 removed. Most removals are pruning: the Cookbooks and Patterns sections, most Official links, and 8 articles. Vlad Terin's jev-browser was dropped. openjev was renamed SemIf.
- **Access:** public access opened 21 Sep (live:7).

**Added, by section** (live README, section by section):
- **SDKs:** Jev (Elixir OTP), Stumble/jev-go, LlamaIndex Jev, two Swift SDKs, discern, kojev, jev4k, hunch.
- **Applications:** MemSearch, Jev Social, Jev Web Analyzer, jev-align (Sutro), Jev for Chrome, jev-ego, Yappy, jevMail, TypeSafe AdBlock, JevPDF, blink, Jev Search, Jev Reranker, jevsearch, jev-research-pipeline, neo4jev, hono-jev-router, sqlite3-jev, jevql, jev-resilience, tripwire, ProgressGate, jev-harness, jev-tree, jev-shell-history, Supercov, Jev × Civ II, Jev Trade, Jev Wrapped, jev.nvim, jev-skip, JevBystander, Paper Radar.
- **Demos:** Jev Chess, jev-fit, jev-plays-pokemon-red, jev-canvas, Jevtown, sudoku-vs-jev, chess-vs-jev, JevsBistro, jev-asks-until-sure, Jev × 2048, Book Aurora.
- **Agent tools:** fast-jev-compaction, SkillRanker, langchain-skill-router, JevRouter, JevLoop, Jevbridge, jev-pref, hermes-jev-skills, augustus, jev-axi, jev-engineering, Jevonian, jev-belay, jev-commit, jev-use, dsh-jev-tools, slop-grader, pytest-jev, jgrep, jevgrep, wellposed.
- **Research:** Kev, Von, Laya, NanoJev, SemIf, jev-visual, jevmlx, JEVfire, LitJev, PlayJev, Jev × NASA Kepler, Jev DSPy Lab, jevcal, ASSAY-001, Jev search rerank eval, Smoking-history benchmark, Jevals.com, stuntd, jev-fanout-bench.
- **Articles:** agentjournal, amankumar, OpenRouter, ayautomate, Jev × LexGLUE, Jev Does Not Play Dice.
- **Other:** Console, MrJev/awesome-jev.

**New entries that report a number** (live line; author claims unless I checked the source):
- **[jev-skip](https://github.com/valentynkit/jev-skip)** (:126): catches 77% of SponsorBlock sponsor seconds across 23 videos, $0.0008 per video. Checked in its README.
- **[NanoJev](https://github.com/TianyuCodings/NanoJev)** (:207): 128/128 on ViZDoom Basic vs Jev 56/128. Checked.
- **[JevRouter](https://github.com/BillionsBobby/JevRouter)** (:169): 38–44% position-wise hits vs 24%. Checked.
- **[OpenRouter](https://openrouter.ai/blog/insights/jev-vs-claude-opus-5-classification/)** (:241): Banking77, Jev 81.0% vs Opus 5 84.4%; p50 latency 175 ms vs 2,266 ms. Checked.
- **[ayautomate](https://www.ayautomate.com/blog/jev-vs-llm-benchmark)** (:242): answer only at confidence ≥ 0.80 and send the rest to Terra; this matches Terra's accuracy at about a quarter of the cost. Checked.
- **[Dice](https://kantahayashiai.github.io/posts/jev-does-not-play-dice/)** (:244): Jev picked "1" on all 400 die rolls with about 83% average probability, against 19% accuracy. Checked. **So calibration does not hold for pure chance.**
- Unchecked, from list blurbs only:
  - Kepler: 72.5% vs 64.4% (:220).
  - LexGLUE: micro-F1 69.9 at $4.02 vs 71.3 at $16.45 (:243).
  - Rerank eval: Jev alone does not beat embeddings (:227).
  - Yappy: 275–690 ms per decision (:82).
  - Book Aurora: 6,010 decisions in about 25 s (:159).
  - hermes-jev-skills: about 0.4 s per route (:184).
  - agentjournal: +11.7 pt on the hard task, −2.0 on the easy one (:239).
- Measure nothing: ProgressGate (:101), jev-belay (:190), Jevtown (:153), jev-canvas (:152).

## A3. Beyond the list

- **[githubnext/localjev](https://github.com/githubnext/localjev):**
  - What it is: a Bun server with Jev's wire format on top of DiffusionGemma.
  - Caveat: its probabilities are generated by the model, not read from logits; it says to calibrate them yourself.
  - Its bake-off: 1,200 requests.
  - Our differential test is BLOCKED (docs/demos/upstream-repro/README.md:183).
- **[razorback16/openjev](https://github.com/razorback16/openjev):**
  - What it is: DiffusionGemma 26B-A4B read directly from the model's probabilities, plus the Laya (421M) and Verdict (151M) models.
  - Speed: 1 question p50 27 ms; 3 questions 31 ms; 57.4 req/s at concurrency 64 on an RTX PRO 6000.
  - It reports **no accuracy or calibration**.
  - It is hosted free on Codiv.
- **The list covers only a fraction of the ecosystem.** Six `gh search repos` queries returned 637 repos; 578 of them appear in neither README.
  - Other catalogues: [yibie/awesome-jev](https://github.com/yibie/awesome-jev) (1,616★), [heyjunpenn](https://github.com/heyjunpenn/awesome-jev) ("896 projects").
  - Unlisted repos that fit "next-gen" (author claims):
    - [shapeshift](https://github.com/anishfn/shapeshift): a text box that turns into the right UI as you type.
    - [jev-voice-browser](https://github.com/moritzkremb/jev-voice-browser): about 300 ms per spoken word.
    - [dasheng](https://github.com/wquguru/dasheng): Jev judges each word of streaming speech recognition.
    - [Astra-Ares](https://github.com/miuuyy/Astra-Ares): picks GPT-6's reasoning effort per task.
    - [minecraft-agent](https://github.com/rmalde/minecraft-agent): Astra plans, Jev controls.
    - [jevpilot](https://github.com/standardagents/jevpilot): driving autopilot.
    - [JevHarness](https://github.com/TianyuCodings/JevHarness): evolves harnesses with GEPA.
    - [openJev-verdict-2.0](https://github.com/Heman10x-NGU/openJev-verdict-2.0): claims 0.0636 Brier.

## B. The frontier: where a small, fast, calibrated judge wins

| Area | Work and published number | Property that matters | Fit with Jev's shape; obvious ground truth |
|---|---|---|---|
| Verifier / process-reward search | [Lightman](https://arxiv.org/abs/2305.20050): step-level reward model reaches 78% on a MATH subset. [Snell](https://arxiv.org/abs/2408.03314): over 4× more efficient than best-of-N; beats a 14× larger model at equal FLOPs. [Liu](https://arxiv.org/abs/2502.06703): a 1B model beats a 405B model on MATH-500 | Many cheap per-step scores | Partial: a Score per candidate fits the shape, but checking math steps is slow reasoning, not a quick judgment [INFERENCE]. GT: PRM800K |
| Search over agent actions | [Koh](https://arxiv.org/abs/2407.01476): +39.7% relative success on VisualWebArena, +28.0% on WebArena. [Agent Q](https://arxiv.org/abs/2408.07199): 18.6%→81.7% success, 95.4% with online search. typesafe-chess: 25 vs 168–190 cp | A prior over every child move plus a value, fast | **Strong:** Choice = policy (up to 255 options), Score = value, one call per node. GT: WebArena task checkers; Stockfish |
| Routing and cascades | [FrugalGPT](https://arxiv.org/abs/2305.05176): up to 98% cost cut at GPT-4 quality. [RouteLLM](https://arxiv.org/abs/2406.18665): over 2× cheaper. [Hybrid LLM](https://arxiv.org/abs/2404.14618): 40% fewer calls to the large model | Cost plus trustworthy confidence | Strong but crowded (jev-router, Jevonian). GT: per-query win or loss, cheap model vs strong |
| Monitoring agent trajectories | [Baker](https://arxiv.org/abs/2503.11926): weaker GPT-4o catches o3-mini reward hacking from its reasoning. [SHADE-Arena](https://arxiv.org/abs/2506.15740): best monitor AUC 0.87. [Who&When](https://arxiv.org/abs/2505.00212): blame the right agent 53.5%, the right step 14.2%. [MAST](https://arxiv.org/abs/2503.13657): 14 failure modes, 1,600+ traces | Runs on every step, so cost and latency | Shape fits (several yes/no checks per step). Our evidence so far is weak: Foreman AUC 0.750 against a 0.90 bar (docs/demos/STATUS.tsv:34). GT: MAST-Data, Who&When |
| When to retrieve | [Mallen](https://arxiv.org/html/2212.10511): retrieving only when useful cuts API cost 15% at equal accuracy. [Adaptive-RAG](https://arxiv.org/abs/2403.14403): 3-class query-complexity router. [Self-RAG](https://arxiv.org/abs/2310.11511) | A decision on the hot path | Strong: Choice {no retrieval, single, multi-step}. GT: Adaptive-RAG's labels, taken from which strategy got the answer right |
| Streaming guardrails | [Constitutional Classifiers](https://arxiv.org/abs/2501.18837): +0.38% refusals, 23.7% overhead. [SCM](https://arxiv.org/abs/2506.09996): macro-F1 above 0.95 after seeing the first 18% of tokens | Latency per chunk | Medium: fits sentence-sized chunks, not single tokens [INFERENCE]. GT: FineHarm |
| Weak supervision | [Snorkel](https://arxiv.org/abs/1711.10160): 2.8× faster, +45.5% vs hand labels. [Prompted labeling functions](https://arxiv.org/abs/2205.02318): 19.5% fewer errors than zero-shot | Many labeling functions per item | Strong: each Noul is a labeling function that comes with a probability. GT: WRENCH |
| Data curation | [FineWeb-Edu](https://huggingface.co/datasets/HuggingFaceFW/fineweb-edu): Llama3-70B scored 500k samples on a 0–5 scale, threshold 3. [DCLM](https://arxiv.org/abs/2406.11794): +6.6 pp MMLU with 40% less compute | Cost per document | Strong: a 6-level Score is the same rubric. Scoring all 15T tokens directly would cost about $630k [INFERENCE arithmetic]. GT: FineWeb-Edu annotations |
| Semantic caching | [vCache](https://arxiv.org/abs/2502.03771): up to 12.5× more cache hits and 26× lower error than a fixed threshold | Deciding must cost far less than regenerating | Strong, and **no ecosystem project does it**. GT: vCache's benchmarks |
| Real-time and embodied | [LiveKit end-of-turn model](https://blog.livekit.io/using-a-transformer-to-improve-end-of-turn-detection/): 135M params, about 50 ms, 85% fewer unintended interruptions. [SayCan](https://say-can.github.io/): 84% correct plans, 74% executed. [KnowNo](https://arxiv.org/html/2307.01928v2): conformal sets over the model's options guarantee a 1−ε success rate, and the robot asks for help otherwise | Latency plus calibrated options | SayCan and KnowNo have exactly Jev's shape. Jev is too slow for end-of-turn detection alone, but fits a "reply / wait / backchannel" Choice. GT: robot task success; dialogue corpora with turn labels |

## C. Five promising, underexplored directions

1. **Jev as the policy and value inside a search.** Only typesafe-chess and neo4jev do this. Chess shows a 7× lower centipawn loss than a single greedy call. The literature puts search with a value function as the biggest lever (Snell, Koh, Agent Q). One call gives a prior over up to 255 children plus a value. A known trap: the absolute Score saturates once one side is ahead (chess :67-72), so ask for relative or pairwise judgments. Ground truth: Stockfish, WebArena checkers, jev-ultrafast's `verify()`.
2. **"Ask when unsure" with a guarantee.** Today people pick thresholds by hand (0.95 tax gate, 0.80 in ayautomate, jevcal). No project builds conformal prediction sets from Choice probabilities the way KnowNo does. The dice result says raw probabilities need calibrating per question on held-out labels. Ground truth: labelled deployment logs.
3. **Reflexes on every step of an agent loop, aimed at common failures.** Step-level blame sits at 14.2% (Who&When), so there is headroom. ProgressGate and jev-belay publish no measurements. Our Foreman result shows a rare target (30 of 186,449; notes/deep/w74-ranking.tsv:13) can't be measured, so target frequent events: loops, false "done" claims. Ground truth: MAST-Data, Who&When, our own transcripts with verified outcomes.
4. **Deciding semantic-cache hits.** The ecosystem has no such project. vCache shows thresholds learned per prompt are the lever. A Noul asking "does the cached answer satisfy this prompt?" at about 0.25 s is cheap next to regenerating. Ground truth: vCache's benchmarks, paraphrase pairs.
5. **Judgments on live media and voice, phrase by phrase.** jev-skip, jev-audio-beeper (466 ms), dasheng, jev-voice-browser and jev-canvas show it works. SCM shows early stopping works. Jev fits phrase-level decisions, not token-level ones. Ground truth: SponsorBlock segments, FineHarm, turn-labelled dialogue.

No files edited; no model API called.
