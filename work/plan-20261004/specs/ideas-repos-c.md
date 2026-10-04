# Ideas from repos — slice C

Scope: metamon, pi-subagents, pokechamp, pokemon-showdown, prism-liquidity-agent, s1-rs, skillranker and skillranker-tip, typesafe-ai-benchmark, typesafe-mario, awesome-jev, awesome-jev-by-typesafe, awesome-typesafe, and VectifyAI/jev-doc-search (online, README + tree_search.py read via raw.githubusercontent).
Plan: work/plan-20261004/PRODUCT.md §2–3. This was read-only work. I made no live calls and ran no upstream code. "Claim" means the repo's own claim.

## Ideas table

|repo or doc|idea (one line)|primitive(s) + pattern|evidence the repo gives (claim + reproducible?)|maps to plan family/verb, or GAP|already tested by us?|
|---|---|---|---|---|---|
|jev-doc-search README ("Page search")|Flat page search: one Choice, one option per page, with the question as the state|Choice; options = documents|Usage example only; the README gives no accuracy number|`rank` run|no hit for "page search" in EVAL/NEG|
|jev-doc-search README + tree_search.py:28-34,65-128|Tree search over a PageIndex hierarchy: one Choice per level, beam=3 scored by the geometric mean of step probabilities, page sets split into windows of ≤255 options and ≤30k tokens|Choice, hierarchical beam + windowing|README table: 2/2 questions correct (NVIDIA 93 pp, Citi 318 pp). N=2, needs a PageIndex cloud key, so not reproducible as a benchmark|GAP: the `rank` family has no hierarchical or windowed mode for corpora over 255 options or 32k tokens|Partly: hierarchical beam REFUTED for routing (NEGATIVE_EVIDENCE.md:3604-3620, R85, Banking77 beam 77.5% < flat). Not tested for document search|
|tree_search.py:14,30-31,134-141|Choice proposes up to 16 candidates. Each candidate then gets its own Noul with its full text, kept at ≥0.5 or the best 2 are kept as a fallback ("Choice is relative, Noul absolute")|Choice → per-candidate Noul verify cascade|Design argument only|`rank`+`verify` chained. GAP: no cross-family pipeline or verb in the plan|Related: R107 REFUTED, three OR-kept Nouls per node pruning MiniWoB (NEGATIVE_EVIDENCE.md:4295)|
|skillranker-tip README:859-862|Retrieve-then-Choose: Quill BM25 prefilter caps the list at 254 real items + `__none__`, so the request stays within 255 options|BM25 → Choice with a none option|README contract; there are tests in the repo (tests/rank_*.rs). We did not run them|`rank` (and `skillgap`). The plan does not state a 255-option overflow policy|`__none__` abstain copied (EVAL.md:479,507,516)|
|skillranker-tip README:919-939|Two-pass ranking. Wide pass: Choice + phase distribution + 3 oriented gates, `needs_skill = mean(specialized_method, material_help, 1-context_suffices)`, abstain below 0.30. Detail pass: Choice over ≤8 candidates + one fit Noul per candidate, and each candidate must beat none|Fan-out Nouls → composite gate → Choice + per-candidate Noul|README calls it "a heuristic score"; no accuracy claim|`rank`/`skillgap`. GAP: composite "need" pre-gate (abstain before ranking)|skillranker heavily covered: EVAL.md ×41, NEGATIVE_EVIDENCE.md ×18 mentions (e.g. EVAL.md:1342)|
|skillranker-tip README:376-386,1065+|`sr calibrate` consumes a labelled evaluation artifact, previews threshold config, `--apply` to write, `--rollback REVISION`|Threshold calibration with preview/apply/rollback|Contract in README + tests/eval_cli_contract.rs (not run)|`<family> calibrate --apply`. GAP: rollback by revision|UNVERIFIED for rollback|
|skillranker-tip README:1209-1420|Stratified sampling manifest (`--sample-size` frozen before run), weighted loss estimate, bounded-loss reports, promotion cohorts "require evidence before promoting"|Eval methodology (no primitive)|README worked example (2%/20% strata). Not run|`<family> eval`. GAP: frozen sampling manifest + stratified weighting|UNVERIFIED|
|skillranker vs skillranker-tip (diff -rq, excluding .git)|The tip adds docs/relevance-corpus-contract.md (a pre-registered labelling rubric: ≥150 positive, ≥100 no-match, ≥50 near-miss, line 22) and docs/self-host-shadow-deployment.md (≤5% fallback over ≥500 shadow hook calls, p50/p95/p99 by cold/warm/cache). It also adds src/storage/hook_entries.rs, scripts/validate_corpus.py, and tests feedback_snapshot_coverage.rs + pipeline_error_kind_mapping.rs. `skillranker` alone has scratch-ho/ and a linux binary. Git heads: skillranker a6f1ff0 (privacy redaction), tip 2a16486 (rubric v2)|Eval corpus + shadow-rollout gate|Pre-registration docs; no results yet|`<family> cases`/`eval`/`watch`. Near-miss "strong distractor" class: GAP in `cases`|skillranker clone noted at EVAL.md:2178|
|s1-rs README:5-31,128-150|Derive macros turn Rust enums/structs into Choice/Score/Noul. `Policy` maps confidence to `Act/Review/Escalate`, with the invariant act ≥ review. Tests run without a network|Choice/Score/Noul, 3-way confidence gate|tests/golden.rs, tests/ui compile-fail. We re-ran it (see next cell)|GAP: 3-way verdict (Act/Review/Escalate) vs the plan's binary threshold. Library binding: plan has "library" but no typed-schema derive|Yes: EVAL.md:283 (examples offline), EVAL.md:1337 (own suite via RCH)|
|typesafe-mario README:13-17,61|No pixels: emulator RAM is turned into object-centric JSON. A Choice over 7 legal actions runs every 8 frames, and the full distribution + confidence are shown|Choice; control loop over structured state|No result claimed. Needs a ROM|GAP: real-time control. Nearest family is `route`|EVAL.md:1676 UNEARNED (N=0, no ROM)|
|typesafe-ai-benchmark docs/benchmarks/README.md:16-24,45-50|Jev vs Qwen 27B (Cerebras) on 7 scenes. Repo claims p50 176 vs 215 ms and cost $0.0119 vs $0.3106; exact agreement Tickets 75/75, Approvals 95 vs 100, Scoring 100 vs 93|Batched Choice/Noul per decision vs one JSON structured output|Raw exports linked (comparison/*.json). Needs both keys, synthetic fixtures. Reproducible with keys; not run by us|`route`/`screen`/`gate`/`score` incumbents. GAP: plan's comparator is mostly regex/BM25, not a fast LLM|No EVAL hit for this repo name (UNVERIFIED beyond grep)|
|typesafe-ai-benchmark README:21-30|Compile app fields into compact numeric slots so the LLM baseline is fair|Comparator design|Methodology|`<family> eval` comparator arm. GAP|no|
|prism-liquidity-agent AGENTS.md:36; engine/program.ts:470-471,562-564|Jev is "soft-only". Nouls `toxicFlowNoul` ≥0.20 and `regimeStressNoul` ≥0.23 block entry, and Jev never overrides hard EXIT rules|Noul thresholds as veto on a rule engine; fail-open|bench/jev-backtest.ts joins judgments to realized outcomes. Thresholds are hardcoded; no published lift number|`gate` (domain veto). GAP: outcome-joined backtest calibration (labels = realized PnL)|EVAL.md:1672 withheld, smoke N=1|
|prism engine/program.ts:11116|Shadow-disagreement log: the Jev pick vs the heuristic pick, logged per pool|Choice shadow vs heuristic|Logs only|`watch` (the plan has Jev-vs-Clef disagreement; this is Jev-vs-incumbent)|no|
|prism native/rust/README.md:61,69,177|Client trait + stub, fail-open by test, "promote gates only on measured expectancy lift"|Fail-open contract|Tests named in README; not run|`doctor`/`--fake`; matches plan|no|
|pi-subagents examples/typed-gate/README.md:3-15|Classifier as a workflow step: stdin text → stdout JSON → script branches on `.verdict`. Keyword stand-in so the example runs keyless|Any primitive behind a stdin/JSON CLI contract|Runnable example, no metrics|Validates plan `batch` + `--json` + `--fake`. GAP: no pi-subagents install target in `install <target>`|no|
|pokechamp README:107,124,140|Minimax search with an LLM as the leaf evaluator, `choose_move(battle)`|Score/Choice as leaf value inside search|Paper claim "expert-level" (not read in full; UNVERIFIED)|GAP: search-leaf evaluator (not in plan)|Yes: R103 REFUTED (NEGATIVE_EVIDENCE.md:4116), R105 REFUTED (:4204), R108/R109 REFUTED (:4358,:4391); local_simulation cites EVAL.md:1962|
|metamon README:9-13|5M+ reconstructed human trajectories + 40+ baseline policies as an eval ladder|Offline-RL dataset + baselines|Paper (RLC 2025); weights released (UNVERIFIED)|GAP: external graded baseline ladder|EVAL.md:2166 not re-run; stretch pending|
|pokemon-showdown README:13-14, COMMANDLINE.md|Deterministic simulator CLI = free oracle environment|Environment only|Mature project|none (infrastructure)|Used by poke-jev (R105)|

## GAPs ranked by how much they would change the plan

1. **Over-limit ranking (hierarchical/windowed + BM25 prefilter to 254+none).** jev-doc-search and skillranker both treat 255 options / 32k tokens as the main design constraint. The plan's `rank` does not say what happens past that limit. Note: hierarchical beam is REFUTED for routing (R85). Document search is untested, so it needs its own bar.
2. **Cross-family pipelines.** Choice proposes, then per-candidate Noul verifies (tree_search, skillranker detail pass). The plan has 10 independent families and no `pipe`/composition verb.
3. **3-way verdict (act/review/escalate)** from s1-rs, instead of one threshold. This would change `explain`/`calibrate` output and exit codes.
4. **LLM comparator arm** (typesafe-ai-benchmark). The plan's incumbents are regex/BM25/constant. A fast-LLM structured-output arm is missing from `eval`.
5. **Abstain pre-gate (composite need-score)** before ranking (skillranker). `rank` has no explicit abstain/none output contract in §3.
6. **Outcome-joined calibration** (prism backtest: labels come from realized results, not human labels) for `calibrate`.
7. **Eval rigor features:** frozen stratified sampling manifest, near-miss distractor class, calibrate `--rollback REVISION`, shadow cohort gate (≤5% fallback / ≥500 calls) (skillranker-tip).
8. **Real-time control / search-leaf use** (mario, pokechamp). Our own evidence for these is REFUTED or UNEARNED, so these are low priority. Keep them as negative evidence only.

## Verbs/primitives the plan does not expose

- No beam/top-K or hierarchical mode on `rank` (the cookbook pattern).
- No `none`/abstain option as a first-class flag on Choice-based families (`route` mentions abstain; `rank` does not).
- No per-candidate Noul fan-out as a reusable step. `ask noul` handles one statement only.
- No Score-composite (weighted atomic scores, "composite scoring" pattern) verb. `score` is single-rubric.
- No option-count/token-window guard surfaced in `explain` (255 / 32k).
- No SQL/table surface (jevql, vgi-typesafe below) and no MCP surface. `install` targets are cli/omp/daily/clef only.

## Listed in awesome lists but not cloned

Sources: awesome-jev/README.md:65-188 (A), awesome-typesafe/README.md:55-159 (T), awesome-jev-by-typesafe/README.md:31-35 (B). Already cloned here and excluded: s1-rs, typesafe-mario, typesafe-ai-benchmark. jevcal and Janus are not in this directory, but EVAL.md:1454-1460 records earlier clones.

|name|URL|one-line idea|maps-to|
|---|---|---|---|
|Python SDK|https://github.com/typesafe-ai/typesafe-sdk-python|official client|backend|
|JS/TS SDK|https://github.com/typesafe-ai/typesafe-sdk-js|official client|backend|
|System One adapter|https://github.com/typesafe-ai/system-one-adapter-python|same typed interface over LLM APIs, for comparing against chat models|GAP: LLM comparator backend (`--backend`)|
|Vercel AI SDK provider|https://ai-sdk.dev/providers/ai-sdk-providers/typesafe-ai|`experimental_evaluate`|backend|
|Vercel AI Gateway|https://vercel.com/ai-gateway/models/jev|hosted Jev, no waitlist|backend|
|Elixir typesafe_sdk|https://github.com/nshkrdotcom/typesafe_sdk|client|—|
|Ruby typesafe-sdk|https://github.com/joshmn/typesafe-sdk|client, retries, pooled HTTP|—|
|RubyLLM TypeSafe|https://github.com/kieranklaassen/ruby_llm-typesafe|RubyLLM provider|—|
|typesafe-ai-rails|https://github.com/GenieRobot/typesafe-ai-rails|usage/cost telemetry + opt-in confidence policies|`watch`/`doctor` cost|
|typesafe-ai-rs|https://github.com/gilljon/typesafe-ai-rs|Rust client|—|
|TypeSafe AI for Rust|https://github.com/Twister915/typesafe-ai|Rust client, observable retries|—|
|typesafe-rs|https://github.com/AbdelStark/typesafe-rs|latency-focused Rust transport|backend|
|Advocaat|https://github.com/pithings/advocaat|TS tagged helpers|`ask`|
|zio-typesafe-ai|https://github.com/jamesward/zio-typesafe-ai|Scala DSL|—|
|.NET SDK|https://github.com/saibimajdi/typesafe-dotnet-sdk|client|—|
|TypeSafeAI.Net|https://github.com/Hawxy/TypeSafeAI.Net|.NET + MS.Extensions.AI guardrail/routing/eval adapters|`screen`/`route`|
|PHP SDK (Butochnikov)|https://github.com/Butochnikov/typesafe-sdk-php|client|—|
|PHP SDK (Fox-Islam)|https://github.com/Fox-Islam/typesafe-sdk-php|one-call switch TypeSafe ↔ OpenRouter decisions|GAP: backend switch beyond jev/clef|
|laravel-typesafe-jev|https://github.com/Butochnikov/laravel-typesafe-jev|recording fake|`--fake`|
|jev-go|https://github.com/Gaurav-Gosain/jev-go|Go client|—|
|jevclient|https://github.com/AboveColin/jevclient|async Python client|—|
|OCaml verdict|https://github.com/jonesmelton/verdict|eio client|—|
|Swift SDK|https://github.com/alterhq/typesafe-sdk-swift|Swift 6 client, network-free tests|—|
|Java SDK|https://github.com/Premo-Cloud/typesafe-sdk-java|nested-criteria builders|—|
|Jev Ultrafast|https://github.com/browser-use/jev-ultrafast|one request picks operation + DOM element|GAP: joint Choice action space (control)|
|jev-browser (Ying-Kai-Liao)|https://github.com/Ying-Kai-Liao/jev-browser|LLM plans, Jev picks each click; lib/CLI/MCP|GAP: control|
|jev-browser (vlad-terin)|https://github.com/vlad-terin/jev-browser|Codex plans, Jev selects elements, runner verifies|GAP: control|
|typesafe-computer-use|https://github.com/awlevin/typesafe-computer-use|OCR → Jev next action, claim ~$0.0002/step|GAP: control|
|Mobile Jev|https://github.com/droidrun/mobile-jev|Android taps per step|GAP: control|
|jev-mobile|https://github.com/Friedjof/jev-mobile|per-step Choice over prevalidated UI actions + confidence gates + escalation|GAP: control|
|Unclutter|https://github.com/kitze/unclutter|classify page elements, cache as local rules|`route` + rule cache. GAP: distil-to-rule|
|HA-Jev|https://github.com/AboveColin/HA-Jev|entity state → sensors; token budget halts|`watch` budget|
|Every|https://github.com/sufianetaouil/every|a Noul per function, ranked by probability|`rank` (Noul-per-item variant)|
|Jev Review|https://github.com/devagrawal09/jev-review|staged code review via focused calls|`diff`/`score`|
|Foreman|https://github.com/thruwire/foreman|Jev judges completeness/tests/need-human after Codex|`watch`/`verify`|
|Jev Drone|https://github.com/RomanSlack/jev-drone|tactical judgments, control stays in code|GAP: control|
|Jev Plays StarCraft|https://github.com/phyous/tsai-sc|structured state + probability traces|GAP: control|
|Jev Trader|https://github.com/jarrodwatts/jev-trader|buy/sell per block|`gate` (domain)|
|Human Compiler|https://github.com/asfarsadewa/human-compiler|Score passive-aggression/urgency → rustc-style diagnostics|`score`|
|JEVMETER|https://github.com/ChetasLua/jevmeter|score every sentence of a video|`score` batch|
|jev-audio-beeper|https://github.com/santos-sanz/jev-audio-beeper|insult detect ~466 ms|`screen`|
|jev-askable-arm|https://github.com/TarunTomar122/jev-askable-arm|chain hardcoded robot primitives|GAP: control|
|jev-codex-router|https://github.com/0xNatoshi/jev-codex-router|per-turn model/thinking/speed pick|`effort`|
|jev-router|https://github.com/gargpratyush/jev-router|fast vs strong tier per turn|`effort`|
|jev-secret-detection|https://github.com/teyhouse/jev-secret-detection|secret-in-diff|`diff`|
|commit-miner|https://github.com/devanshbatham/commit-miner|classify commits: bugfix/CWE/change type|`diff`/`route`|
|jev-eval-agent|https://github.com/vinilana/jev-eval-agent|eval harness|`eval`|
|Jev Logs|https://github.com/reachjalil/jevlogs|score OTel logs before an LLM reads them|GAP: log triage (`score`/`rank`)|
|Yes / No|https://yesno.coderai.dev|Noul demo + web search|`ask noul`|
|Jev Tetris|https://jev-omega.vercel.app|rotation/column choice|GAP: control|
|Jev Pac-Man|https://jev-pacman.ephraimduncan.com|turn per junction|GAP: control|
|jev-doom-agent|https://github.com/lukaske/jev-doom-agent|Doom WASM + telemetry|GAP: control|
|jev-gomoku|https://github.com/mizchi/jev-gomoku|Jev vs Jev gomoku (MoonBit)|GAP: control|
|jev-t-rex-runner|https://github.com/joshlarsen/jev-t-rex-runner|dino game|GAP: control|
|snake-jev|https://github.com/siroccomask/snake-jev|direction choices|GAP: control|
|Jev Guard|https://guard-jev.vercel.app|comment moderation|`screen`|
|Hollow Creek|https://hollow-creek-sigma.vercel.app|NPCs judge each tick|GAP: control|
|Jev mood demo|https://jev-demo.vercel.app|mood tracked in state over time|GAP: stateful scoring|
|Jev Room|https://jev-room.moe136231.chatgpt.site|sentence → 6 settings|`route` fan-out|
|TypeSafe Typewriter|https://typesafe-demo.val.run/|16 judgments live as you type|fan-out|
|got-jev|https://github.com/phureewat29/got-jev|story LLM writes, Jev answers state facts|GAP: LLM+Jev co-loop|
|Little Airways|https://github.com/lbotinelly/jev-little-airways|ATC divert/priority ~150 ms|GAP: control|
|TypeSafe agent skill|https://github.com/typesafe-ai/skills|official skill|`install`|
|eve|https://github.com/vercel/eve|`autoModel` picks LLM via Jev|`effort`|
|jev-mcp (jkudish)|https://github.com/jkudish/jev-mcp|MCP verify/screen/find|GAP: MCP surface|
|Jev MCP (blakestone-x)|https://github.com/blakestone-x/jev-mcp|MCP classify/score/check/match/screen|GAP: MCP surface|
|Jev Review MCP|https://github.com/NiazMorshed2007/jev-review|quality review while writing|`score` + MCP|
|typesafe-mcp|https://github.com/itsmostafa/typesafe-mcp|Go CLI + MCP|GAP: MCP|
|pi-typesafe|https://github.com/DevMortimer/pi-typesafe|batched `typesafe_evaluate`, offline transport|`install` (pi target GAP)|
|pi-jev|https://github.com/y0usaf/pi-jev|shadow tool-call gate + output judge + `jev_ask`|`gate`/`ask`|
|pi-warden|https://github.com/DevMortimer/pi-warden|verdict as held tool result; rules-file write checks; self-grading|`gate`/`screen`|
|pi-jev-auto-mode|https://github.com/jomatsu/pi-jev-auto-mode|approve bash/write/edit, fail closed|`gate`|
|pi-heed|https://github.com/Nyarlathoteppppp/pi-heed|conversation constraints → replayable policy|GAP: policy extraction|
|Bicameral|https://github.com/AbdelStark/bicameral|reflexes: policy, loop detection, review|`gate`/`watch`|
|ask-jev-skill|https://github.com/shantanugoel/ask-jev-skill|Hermes bounded decision|`ask`|
|jev-system-architect|https://github.com/samtay32/jev-system-architect|hunt brittle semantic logic → Choice/Score/Noul|`skillgap`-like. GAP: code audit for replaceable heuristics|
|jevql|https://github.com/kylemclaren/jevql|`WHERE jev(...)` against plain Postgres|GAP: SQL surface|
|vgi-typesafe|https://github.com/Query-farm/vgi-typesafe|DuckDB table functions, LATERAL join|GAP: SQL surface|
|LlamaIndex Jev|https://github.com/WiktorB2004/llama-index-jev|reranker + query-engine selector|`rank`/`route`|
|is-malicious|https://github.com/luantak/is-malicious|scan source/CI files with line pointers|`diff`/`gate`|
|Jev-assisted compaction|https://github.com/ljedrz/nachalnik/blob/master/kamchatka/examples/jev_assisted_compaction.rs|content-aware compaction|`memory`|
|Jev-assisted shell|https://github.com/ljedrz/nachalnik/blob/master/kamchatka|color-coded shell safety advice|`gate`|
|jev-axi|https://github.com/shiftynick/jev-axi|AXI CLI: block risky calls, screen fetched content, triage build logs|`gate`/`screen`. Closest peer to our CLI|
|jev-cli (jevctl)|https://github.com/Nasrallah-AL/jev-cli|pipeable exit-code-gated verify/screen|`verify`/`screen`. Peer CLI|
|jevcal|https://github.com/abhixhek/jevcal|fit per-question threshold to target accuracy, held-out check, fallback-traffic estimate|`calibrate` (EVAL.md:1454)|
|Supercov|https://github.com/supercorp-ai/supercov|score each file for fix-first|`score`/`rank`|
|Crowdcheck|https://crowdcheck-ai.vercel.app/|10k synthetic personas, batched reaction probs|GAP: persona simulation|
|HEIST//ONE|https://github.com/AbdelStark/heist-one|batched judgments for 6 guards; code validates proposals|GAP: control|
|Jev Plays Pokémon|https://github.com/anxkhn/JevPlaysPokemon|GBA battle decisions|GAP: control (our R103/R105 REFUTED)|
|Jev Search|https://github.com/superagents-lab/jev-search|choose sources/time ranges/queries, then rank|`rank`/`route`|
|JevNoiseGate|https://github.com/ufec/jev-block-android-ad|notification noise Noul + local prefilter|`screen` + free cascade|
|jevlike|https://github.com/vinnylarouge/jevlike|train small one-pass option scorer|Clef-like backend|
|openjev|https://github.com/TheoLeeCJ/openjev|option logits on an RTX 3090|Clef-like backend (EVAL.md:1452 notes the link is stale)|
|PocketJev|https://github.com/NullPo-jp/PocketJev|on-device MLX VL option logits|backend. GAP: vision|
|decider|https://github.com/Mapika/decider|Qwen3.5-2B fine-tune, calibrated typed decisions|backend|
|Jev Rerank Bench|https://github.com/anessbelbati/jev-rerank-bench|rerank with CIs|`rank eval`|
|Jev Spam Eval|https://github.com/bitnovus/jev-spam-eval|zero-shot spam vs TF-IDF|`screen`/`route eval`|
|Jev Phishing Bench|https://github.com/anisselbd/jev-phishing-bench|2,000 emails vs Haiku (repo claims Haiku wins accuracy)|`screen eval`|
|jev-agent-failure-benchmark|https://github.com/TokenTrim/jev-agent-failure-benchmark|who/which step/error category|`watch` (EVAL.md:133)|
|jev-sec-bench|https://github.com/Gaurav-Gosain/jev-sec-bench|injection + vulnerable-code benches|`screen`/`diff eval`|
|Janus|https://github.com/FirasSX914/Janus|calibration on Banking77/WoS + priced Jev→frontier cascade|`route`/`calibrate`/`effort` (EVAL.md:1458)|
|Jev Judge vs Dimension Scores|https://agentjournal.dev/blog/llm-judge-vs-feature-extraction/|one direct question vs 12–14 scored dimensions + fitted weights|GAP: composite scoring w/ fitted weights|
|typesafeai.app|https://typesafeai.app/|capability directory with evidence levels|reference|
|Internal classifier field note|https://x.com/identityTorn/status/2100475121324728615|anecdotal matched-precision vs fine-tuned Qwen|reference|
|Browser Use + Jev post|https://x.com/gregpr07/status/2100411066966749359|dynamic DOM action space|reference|
|awesome-gpt-6-astra (B)|https://github.com/Anil-matcha/awesome-gpt-6-astra|sibling use-case list|reference|
|awesome-agent-apis (B)|https://github.com/Anil-matcha/awesome-agent-apis|APIs typed decisions can route to|`route`|
|open-business-agents (B)|https://github.com/Anil-matcha/open-business-agents|business agents using Jev as decision/safety layer|reference|
|awesome-generative-ai-apps (B)|https://github.com/Anil-matcha/awesome-generative-ai-apps|app templates|reference|
|llm-wiki-agent (B)|https://github.com/SamurAIGPT/llm-wiki-agent|knowledge workflow + citation checks|`verify`/`memory`|
|typesafe-ai (PyPI shim)|https://pypi.org/project/typesafe-ai/|slopsquat-blocking redirect|`doctor` (install check)|

Official cookbooks and patterns listed (A:172-197; B use-case map :239-363 cites the same docs). Each entry gives its idea → maps-to:

- parallel_questions → fan-out across all families.
- semantic_find, a Choice over line IDs plus an "answer exists?" Noul → `rank`. GAP: line-level mode with an existence check.
- rerank_typesafe → `rank`.
- llm_guardrails → `screen`.
- citation_check → `verify`.
- classifying_rag_passages (keep/flag/drop) → `memory`/`screen`.
- function_calling → `route`. GAP: argument filling.
- skill_suggestion → `skillgap`.
- hierarchical_classification → `route`. REFUTED for us (R85).
- sde_cascade → GAP: extraction.
- date_extraction and pre_parsed_value_extraction, where regex finds candidates and Jev picks the span → GAP: extraction (span selection).
- entity_alignment (merge/unlinked/curator) → GAP: dedupe.
- autoresearch_feature_discovery (questions as ML features) → GAP: feature extraction.
- classification_using_confidence (climb the hierarchy when unsure) → `route` abstain.
- autoformat → GAP.
- consistency_noul and consistency_choice → `calibrate`/review routing.
- Patterns fan-out, confidence-routing, composite-scoring, and intent-routing → covered except composite (GAP).
- Smart-home demo → fan-out.

Docs, blogs, social links, and news (A:40-59, 205-217; T:36-81; B:447-460) are reference only, with no project idea. Not enumerated row by row: TypeSafe home, docs, playground, keys, API, evals, GitHub org, jaggedness page, launch post, manifesto, Bitterest Lesson, "too good to be true", Discord/X/LinkedIn, every.to, ziplyne, developersdigest, dev.to, mohammedshehu, The Register, the two zenn posts, warmersun, Steve Krouse post, Shannon video.
