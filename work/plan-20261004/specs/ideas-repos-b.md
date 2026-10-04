# Ideas from clones, batch B (14 repos)
Read-only. Plan = work/plan-20261004/PRODUCT.md (families §3 lines 46-66). Where this says "repro", the line cited is our EVAL entry. Where it says "own claim", the number comes from the repo's README and we have not re-run it.

## What each repo is, and our status
|repo|what it is|ported/refuted here|
|---|---|---|
|jev-curate|Rust/Py Parquet dataset filter: per-row Choice/Score/Noul rubric (README:3,39)|FLOOR: the binary returns 422, and the clone rule rejects 30/30 (EVAL.md:1673). Upstream bug filed as bead jev-jjw. Its code_quality Score beat Haiku (WIN), then fell to DOWNGRADED on rerun (NEGATIVE_EVIDENCE.md:3784-3792)|
|jev-drone|MuJoCo quadrotor. Jev answers one joint question (Choice+Score+Noul) at about 2.5 Hz and gives advice only. Code owns safety (README:20-36)|FLOOR: 287 calls, prevalence exit 2, no accuracy claim (EVAL.md:1675)|
|jev-mcp|MCP server with jev_verify, jev_screen and jev_find (README:8)|Reproduced: 9/9 unit, 4/4 live (EVAL.md:281,1471). The design was ported into our xd://jev_* tools [INFERENCE from the tool names]|
|jev-phishing-bench|Jev vs Haiku on "click this link?" over 2,000 emails (README:1-20)|Reproduced: verdict 0.6298, below the 0.9165 domain-list floor. REFUSED (EVAL.md:1607-1615). Also NEGATIVE_EVIDENCE.md:600|
|jev-rerank-bench|Jev rerank variants vs Cohere/ZeroEntropy (README:22-36)|Reproduced: cache reproduces 28/30 (EVAL.md:1436). NevIR +4.2pt (EVAL.md:278,1752; NEGATIVE_EVIDENCE.md:4058)|
|jev-review|MCP jev_review: quality-dimension scores at agent checkpoints (README:16,77)|Ported as omp-jev-review (EVAL.md:2275,2817). Beads jev-deep-kit-8q7.6 and .11 replace the Jev applicability pre-gate with a deterministic check|
|jev-router|Per-turn model-tier routing for Claude Code/Codex: 3 Scores + model_tier Choice (src/config.mjs:101-113)|Tests 58/58 (EVAL.md:1485). Live benchmark bead jev-38qj is DEFERRED, so there is no quality measurement|
|jev-sec-bench|Go: injection on 662 messages plus vulnerable-code pairs (README:12-13)|Reproduced, plus an LLM-vs-Jev differential (EVAL.md:286,1214,1583)|
|jev-spam-eval|Zero-label spam vs TF-IDF learning curve and OOD (README:11-28)|Reproduced: OOD win, in-distribution tie or loss (EVAL.md:277,1195,1637). Also in NEGATIVE_EVIDENCE.md (2 hits)|
|jev-trader|A buy/sell Choice for every Monad block, about 300 ms each (README:3,26)|Not run (EVAL.md:1680)|
|jev-ultrafast|Browser agent: one request = operation Choice + target Choices over an indexed element table (README:30-40)|Reproduced: 8/10, 0 invalid executions, p50 193 ms (EVAL.md:1358-1366)|
|jevcal|Per-question threshold picker, escalation share, CI fail on drift (README:3-19)|Reproduced: 24/0 tests, T4 proposed (EVAL.md:1454-1456). A threshold carries within one dataset, not across two (docs/LEDGER.md:212)|
|killmyidea|Startup idea → 8 Scores + category Choice + clarity Noul → KILL/FIX/SHIP (README:5-10)|Tests 48/48, no live run (EVAL.md:2164-2178)|
|neo4jev|Graph walk: next-edge Choice + goal Noul per hop, beam search (README:6-14)|FLOOR: 2/3 goals (EVAL.md:1671)|

## Ideas
|repo or doc|idea (one line)|primitive(s) + pattern|evidence the repo gives (claim + reproducible?)|maps to plan family/verb, or GAP|already tested by us?|
|---|---|---|---|---|---|
|jev-curate README:39|Run a whole rubric per row in one request, at bulk scale over Parquet|Score+Noul+Choice, joint per row, streaming|Own claim: 24 rows/s on a mock bench (README:13). No live receipt; the binary 422s|score batch. The plan has no file-format/streaming input (GAP, minor)|EVAL.md:1673 FLOOR; NE:3784 DOWNGRADED|
|jev-curate src/filter.rs:11,33|Keep/reject with recorded rejection_reasons|Noul thresholds → reject reason list|Code only|score/verify `explain` per row: partly in the plan (explain shows the request, not per-row reasons)|clone rule rejects 30/30 (EVAL.md:1673)|
|jev-drone README:20-39,114|Code decides *when* to ask; Jev decides *what to do*; deterministic layer always owns safety|joint Choice(maneuver)+Score(risk)+Noul(lost) in one call, triggered by code|Own demo; flight is reproducible only with MuJoCo; no accuracy claim|GAP: there is no "joint multi-question state" family. Closest are route+score; the safety-owning pattern matches the gate cascade|FLOOR, EVAL.md:1675|
|jev-mcp README:8,150|Three agent tools: verify, screen, find (rank with no embeddings)|Noul (verify, screen), Choice (find)|Own anecdotes (README:10-12); our 4/4 live run|verify, screen, rank: all in plan. Distribution via MCP is not a plan surface (GAP: `classifier mcp`/serve)|EVAL.md:281,1471|
|jev-phishing-bench README:23|Ask 5 signal questions next to the verdict and fit LR on the signals; signals beat the verdict|parallel Noul signals in one call → offline logistic regression|Own claim: free-host signal AUROC 0.96, CV LR 95.1%. But a list rule alone gets 91.6% (README:36)|GAP: "signals then fit" (a decomposed feature mode). Overlaps `calibrate`, but the plan fits Platt on one output, not a multi-signal model|Verdict REFUSED vs floor (EVAL.md:1607-1615); signal-fit UNVERIFIED by us|
|jev-phishing-bench README:36|A non-AI floor must run first; this dataset separates by construction|baseline-before-model|Reproduced exactly (EVAL.md:279)|Matches `ready` / prevalence-first rule; also the gate free cascade|yes|
|jev-rerank-bench README:22-36|Design matters: 4-level rubric over 30 in one call ≈ Cohere; Choice+none best top-1; pairwise/duels worse|Score batch, Choice with "none" abstain, tournaments|Own claim 0.692 vs 0.691; repro cache 28/30|rank: in plan. "none" abstain + AUROC "nothing here" → rank should expose abstain (partial GAP)|EVAL.md:278,1436,1752|
|jev-rerank-bench (NevIR)|Negation-sensitive ranking where Jev beats others|Choice over 2-passage pairs|repro +4.2pt p=.002 (EVAL.md:278)|rank cases|yes, NE:4058|
|jev-review README:16,77|Baseline-then-delta quality scores at agent checkpoints; agent fixes, Jev only scores|Score per dimension, repeated, delta tracking|Own; tests 13/13|score + watch; delta-vs-baseline is not explicit in plan (GAP, small: `score --baseline`)|ported omp-jev-review; jev-deep-kit-8q7.6/.11|
|jev-review (applicable:false)|Abstain when input not applicable|Noul pre-gate → replaced by deterministic check|EVAL.md:282|ready/explain: free check before model|bead 8q7.11|
|jev-router src/config.mjs:101-113|Pick model tier per turn from complexity Scores + tier Choice|3 Score + Choice joint|Own claim only; no benchmark in repo read [UNVERIFIED]|effort: in plan (shadow only)|tests 58/58; jev-38qj DEFERRED; plan says usage router LOST (PRODUCT.md §3 row 8)|
|jev-sec-bench README:42-52|Telling the model what the assistant is for adds +20pp recall|Noul with a deployment-context field in the state|Own 96.5% / AUC 0.9927. Reproduced (EVAL.md:286)|screen: in plan. Context field should be a first-class `screen --context` input (GAP, small)|EVAL.md:286,1214,1583|
|jev-sec-bench README:89|Vulnerable twin scores above secure twin 89%|Score, paired comparison|Own; part of repro run|diff/score; "pairwise twin" eval not a verb (GAP minor)|EVAL.md:1583 [partial, UNVERIFIED which arm]|
|jev-spam-eval README:11-28|Zero-label value = labels saved + OOD robustness; TF-IDF needs 100–10k labels to match|Noul/Choice zero-shot vs learning curve|Own; reproduced regime (EVAL.md:1195)|route/screen eval. "labels-to-match" learning-curve report is not in `eval` (GAP)|yes|
|jev-trader README:3,26,34|One Choice per tick under a hard latency budget; record `late` flag|Choice buy/sell/hold + Noul upIn10, streaming SSE|Own; dry-run demo; no PnL claim read|GAP: no streaming/real-time family; `watch` is about agents, not event streams|not run (EVAL.md:1680)|
|jev-ultrafast README:30-40|Dynamic indexed action space: operation Choice + per-op target Choices in one request; LLM writes text only|joint dependent Choices; options built per observation|Own 7.1 s Google Flights; repro 8/10|GAP: "act"/agent-step family (choose operation+target). Nearest route|EVAL.md:1358|
|jevcal README:3-19|Per-question threshold for target accuracy, coverage handled, cost of escalation, CI fail|calibration curve → threshold → cascade economics|Simulator only, by design; tests repro|calibrate + eval: in plan. Plan lacks "target accuracy → threshold + coverage/escalation share" output (partial GAP)|EVAL.md:1454; LEDGER:212 (threshold does not transfer across datasets)|
|killmyidea README:5-10|Multi-Score weighted sum + clarity Noul gate → 3-way verdict|8 Score + Choice + Noul joint → deterministic aggregator|Own; tests 48/48; no accuracy claim|score (rubric aggregate). Composite verdict policy not a plan verb (GAP small)|EVAL.md:2164 tests only|
|neo4jev README:6-14|Multi-step search: Choice per hop + goal Noul, beam over log-probs|Choice + Noul per step, iterated, beam|Own demo; repro 2/3 goals|GAP: sequential/iterated decision (walk/search). Not in plan|FLOOR EVAL.md:1671|

## GAPs ranked by plan impact
1. **Joint multi-question decision on one state** (jev-drone, jev-ultrafast, killmyidea, jev-router, jev-phishing signals). This is Jev's core property (parallel questions over one state), yet the plan exposes single-decision families. Missing: a generic `classifier ask --schema` / `custom` family taking N typed questions. The meta `ask` might cover it [UNVERIFIED: PRODUCT.md does not define `ask` semantics in the lines read].
2. **Iterated/sequential decisions** (neo4jev beam walk, jev-ultrafast agent loop, jev-trader per tick). No family loops over states. `watch` is an agent-health monitor, not this.
3. **Signals → fitted model** (phishing: 5 Noul signals + LR). This differs from Platt `calibrate` on one output. It would add a multi-feature calibrate mode.
4. **Threshold-for-target + escalation economics** (jevcal). `calibrate` should output the threshold at a target accuracy, the share of traffic handled, and the cost of escalating the rest. LEDGER:212 says it must be fit per dataset.
5. **Abstain/"none" option and deployment-context input** (rerank Choice+none; sec-bench +20pp recall with context). These are small input flags on rank and screen.
6. **MCP/serve surface** (jev-mcp, jev-review). The plan has CLI, library and hooks, but no MCP server.
7. **Learning-curve "labels-to-match" report** (jev-spam-eval) and **baseline-delta scoring** (jev-review). These are eval/score report options.

## Verbs/primitives the plan does not expose
- Raw primitives: there is no direct `choice`/`score`/`noul` verb with a user-supplied option list (jev-mcp, neo4jev, jev-ultrafast all build options per call).
- Choice with options generated at runtime (indexed elements, graph edges): each family's option set is fixed.
- Full probability distribution and top-k/beam output (neo4jev). The plan output appears to be one decision [INFERENCE].
- A per-call latency budget with a `late` flag (jev-trader).
- Streaming input (Parquet/Arrow, SSE). `batch` is NDJSON only.
