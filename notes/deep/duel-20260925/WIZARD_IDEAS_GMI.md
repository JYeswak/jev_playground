# WIZARD_IDEAS_GMI: From Testing Loop to Product Reality

**Author:** Antigravity / Gemini (pane 18, profile `agy`, identity `BeigeGrove`), 2026-09-25.
**Context:** DUEL on next-stage direction for `jev_playground`.
**Grounding:** Input from `AGENTS.md`, `README.md`, `notes/deep/next-gen/NEXT-STAGE-PLAN.md`, `work/`, `scripts/`, `.omp/`, and `foundation/`.
**Mandate (Joshua, verbatim):** *"lets move this out of repeated testing over and over to actually turning this into something relevant and usable"*.

---

## 0. The Diagnosis: Escaping the Meta-Testing Trap

In the last 9 days, this repository accumulated **2,823 commits**. The breakdown tells the entire story:
- **1,015 commits (36%)** touched only prose documentation.
- **446 commits (16%)** touched only the bead issue store.
- **213 commits (8%)** touched only ledgers (`EVAL.md`, `NEGATIVE_EVIDENCE.md`).
- **Only 799 commits (28%)** touched any functional code.

`AGENTS.md` swelled from 1,214 to 1,862 lines—an accretion of prose rules written in response to trivial incidents, enforced almost entirely by agent discipline rather than code. Meanwhile, `NEGATIVE_EVIDENCE.md` grew to 120 rows. As measured on 2026-09-25:
- **Only 4 of the 120 negative evidence rows** represent clean, unrecoverable losses by a live Jev model.
- **Over 50 rows** were caused by our own harness errors: `color` vs `bg_color` field mismatches, comma-separated option flags ignored by switches, states exceeding the 32k token input ceiling without preflight checks, grader leaks in state builders, and unreachable preregistration bars.
- **Zero organic consumers:** The four custom Jev tools built for omp (`jev_rerank`, `jev_claim_check`, `jev_screen`, `jev_flag`) had **0 organic calls** in real coding work across the entire fleet (`jev-ja32`). Every logged call was an artificial rollout test.
- **The Stranger Barrier:** The root `README.md` is currently 54,824 bytes (48 bytes under GitHub's soft limit). It is a defensive academic ledger and proof catalogue, not an on-ramp. A stranger discovering this repo cannot tell how to use Jev in their own app within 5 minutes.

### The Strategic Pivot
Claude's proposal in `WIZARD_IDEAS_CC.md` identifies these symptoms accurately, but its #1 idea is `jev-trial`: *building yet another testing kernel*. Proposing a better testing framework when the directive is "move out of repeated testing over and over" is the exact pathology Joshua called out.

Jev is not a text generator or a general-purpose agent. Jev is a **high-speed (~500ms), hyper-cheap ($0.042/M tokens), calibrated probabilistic classifier**. Its superpowers are:
1. Fast, calibrated true/false (`noul`), multiclass (`choice`), and ordinal rubric (`score`) judgments.
2. Parallel question execution over a single state snapshot.
3. High leverage when embedded inside deterministic code (guards, routers, compactors, re-rankers, evaluators).

To make Jev "relevant and usable", we must deliver on two distinct fronts:
1. **For US in omp:** Live, active hooks and tools that make daily multi-agent coding safer, faster, and cheaper (active tool-call gating, real context compaction, diff review).
2. **For STRANGERS:** A clean, zero-dependency SDK (`jev-kit`), a versatile CLI tool (`jev`), and standard integrations (MCP server, framework middleware) with a 60-second quickstart.

---

## 1. The 30 Candidate Ideas

Here are 30 pragmatic, accretive ideas spanning internal agent ergonomics, external developer adoption, reliability architecture, and domain applications.

### Category A: Internal Omp Fleet Ergonomics & Real Hot-Path Consumers

#### 1. `omp-safe-guard`: Active Tool-Call Safety Interceptor
- **How it works:** An active pre-execution hook on `tool_call` for `bash` and filesystem modifications. Extracts command, target paths, and git status. Runs an instant local whitelist (bypassing Jev for 90% of benign commands like `git status`, `ls`, `cargo check`). On potentially destructive commands (`rm`, `git reset`, `git checkout .`, `DROP`, process kills), queries Jev's bicameral gate. If risk probability exceeds 0.80 with high confidence, blocks execution and prompts for interactive user confirmation.
- **How users perceive it:** Invisible and zero-latency on ordinary development commands. When an agent hallucinates a dangerous cleanup command or wipes uncommitted work, a clean warning intercepts the action: `[Jev Guard: Blocked destructive git wipe (confidence 0.94)]`.
- **How to implement it:** Built in `.omp/hooks/pre/tool-call.ts`. Reuses the frozen question set from `work/bicameral-gate/questions.mjs` (which already measured 78/100 catches at 1/300 false alarms). Fail-safe defaults to open on timeout (>1.2s) with warning log.

#### 2. `omp-compact-live`: Live Context Compactor Hook
- **How it works:** Hooks into omp's `session_before_compact` and per-turn context assembly. Evaluates past tool results (bash outputs, compiler logs, file dumps) using parallel Jev Noul questions (`keep_or_drop`). Compresses massive outputs (e.g. 500-line test passes or repetitive builds) into concise head/tail summaries while keeping errors, diffs, and instructions byte-identical.
- **How users perceive it:** Conversations stay responsive past turn 100. Token costs on frontier models drop by 40–60%. The agent doesn't suffer context rot or forget initial system constraints.
- **How to implement it:** Connect `work/p2-compaction` and `fast-jev-compaction` directly into `.omp/hooks/pre/jev-compact.ts`. Pre-filter ignores user messages. Fail-safe preserves all unjudged entries.

#### 3. `omp-search-rerank`: Code & Grep Result Re-Ranker
- **How it works:** Intercepts high-volume search results from `grep`, `rg`, or `glob` when candidate matches exceed 15 items. Sends candidate file paths and snippet headers to Jev Choice/Score against the current task prompt. Injects the top 5 most relevant snippets into agent context, collapsing the rest into a summary list.
- **How users perceive it:** Eliminates context pollution. Instead of the agent reading 2,000 lines of irrelevant test fixtures matching a symbol name, it immediately lands on the actual implementation.
- **How to implement it:** Wrap the native `grep` tool in `.omp/tools/` or add a `tool_result` hook. Evaluates up to 16 candidates per request via Jev Choice. Times out cleanly to verbatim results if Jev takes >800ms.

#### 4. `omp-diff-reviewer`: Semantic Commit & Sibling Leak Gate
- **How it works:** Fires during `git commit` or `git add` in omp sessions. Takes the staged diff and commit message. Runs two parallel checks: (1) "Does this diff match the intent described in the commit message?", (2) "Does this diff contain unexpected files, secrets, or sibling agent work?"
- **How users perceive it:** Completely stops the common multi-agent accident where Agent 1 stages a file that Agent 2 was actively editing in the shared worktree, or commits an unverified placeholder.
- **How to implement it:** Pre-tool hook on `bash` matching `git commit*`. Executes `git diff --cached` in subshell, sends diff summary to Jev bundle. Warns or blocks if mismatched.

#### 5. `omp-failure-triage`: Auto-Diagnostician on Command Failures
- **How it works:** When a bash command (build, test, script) exits with non-zero status, Jev analyzes the trailing 40 lines of stderr. Classifies into: `syntax_error`, `missing_dependency`, `flaky_network`, `test_assertion_failure`, or `harness_bug`.
- **How users perceive it:** Agents immediately get an actionable diagnosis hint instead of spending 3 turns flailing with random shell commands.
- **How to implement it:** `tool_result` hook on `bash` when `exitCode !== 0`. Returns a 1-line annotation attached to the error output.

#### 6. `omp-claim-gate`: Agent Hallucination & Self-Grading Buster
- **How it works:** Scans assistant turn text for verification assertions ("all tests pass", "verified working", "zero errors") and validates them against the actual bash logs in the recent transcript using `work/jev-claim-check`.
- **How users perceive it:** Eliminates agent hallucination where the model confidently asserts a fix worked despite the test output showing failures.
- **How to implement it:** Post-turn validation hook. If a discrepancy is detected (p < 0.20 on claim support), attaches an advisory flag to the response.

#### 7. `omp-log-squeezer`: Real-Time Verbose Log Compressor
- **How it works:** Intercepts stdout from verbose commands (like `npm install`, `cargo build`, `webpack`) that output >100 lines. Groups lines into chunks and evaluates information density. Drops repetitive build progress bars while preserving compiler warnings and errors.
- **How users perceive it:** Fast, clean terminal and transcript output with zero token waste on build spam.
- **How to implement it:** Output stream filter or `tool_result` interceptor in omp.

#### 8. `omp-subagent-router`: Intent-Based Subagent Dispatcher
- **How it works:** When a complex task is dispatched, Jev evaluates the user prompt against available subagent profiles (`scout`, `code-simplifier`, `reviewer`, `task`) using Jev Choice.
- **How users perceive it:** Automatic, optimal subagent routing without requiring the user or conductor to manually remember profile names.
- **How to implement it:** Built into dispatch automation scripts (`scripts/fleet-tick.sh`).

#### 9. `omp-conflict-watcher`: Shared Worktree Live Conflict Detector
- **How it works:** Runs as a background daemon in multi-agent tmux sessions. Polls `git diff` across active agent panes. Asks Jev whether two agents' in-progress edits in the same file represent semantic conflicts.
- **How users perceive it:** Agents get alerted *before* saving conflicting changes, preventing costly merge repairs.
- **How to implement it:** Background daemon running every 45s via `scripts/fleet-idle-watch.py`.

#### 10. `omp-test-flakiness-tagger`: Test Failure Stability Classifier
- **How it works:** On test failure, compares the current failure stack trace with historical test failure patterns in the repo. Determines if the failure is an environmental flake or a direct regression from recent edits.
- **How users perceive it:** Prevents wasted debugging sessions chasing flaky tests that have failed for days.
- **How to implement it:** Invoked by test runner scripts or omp hooks.

---

### Category B: Developer Tooling, Stranger Experience & Packaging

#### 11. `jev-kit`: The Zero-Dependency Stranger SDK
- **How it works:** A clean, production-grade npm and PyPI package wrapping the official SDK. Exports high-level, intuitive primitives: `guard()`, `route()`, `score()`, `rerank()`, `verify()`. Automatically embeds size preflights, option validation, timeout guards, and fail-safe defaults.
- **How users perceive it:** A developer installs it (`npm i jev-kit` or `pip install jev-kit`) and writes 4 lines of readable code. It just works. If the key is missing or invalid, it returns clean typed error structures instead of crashing.
- **How to implement it:** Extract and polish `work/jev-client/` into an independent package root. Ship comprehensive TypeScript definitions and Python type stubs.

#### 12. `jev` CLI: The Unix Swiss-Army Knife for Probabilistic Decisions
- **How it works:** A standalone, single-binary / standalone script CLI with subcommands:
  - `jev doctor` (connectivity, key status, model pin verification)
  - `jev guard "text"` (prompt injection & toxicity guard; exit 0/1)
  - `jev route "query" "billing,sales,support"` (intent routing)
  - `jev check --claim "..." --evidence "..."` (claim verification)
  - `jev rerank --query "..." --items file.json` (passage re-ranking)
- **How users perceive it:** Usable directly in bash scripts, CI/CD pipelines, Git pre-commit hooks, and terminal workflows without writing application code. Supports `--robot` for JSON output.
- **How to implement it:** Executable entry point in Node/Bun or Python following Jeffrey's canonical CLI ergonomics standard (`doctor`, `--robot`, clean exit codes).

#### 13. `jev-mcp`: Universal One-Click MCP Server
- **How it works:** A standalone Model Context Protocol server exposing Jev's best capabilities (`jev_guard`, `jev_rerank`, `jev_verify_claim`) over stdio and SSE.
- **How users perceive it:** Cursor, Windsurf, Claude Desktop, and omp users add one line to `.mcp.json` (`"jev": { "command": "npx", "args": ["-y", "jev-mcp"] }`). Their assistant gains immediate access to fast, calibrated secondary judgments.
- **How to implement it:** Refactor `work/omp-jev-review` and `work/jev-mcp` into an independent, publishable package using `@modelcontextprotocol/sdk`.

#### 14. `jev-guard-middleware`: Framework Security Middleware
- **How it works:** Drop-in HTTP middleware for Express, Next.js, and FastAPI. Automatically inspects incoming request payloads for prompt injection and jailbreak attempts before requests reach expensive LLM endpoints.
- **How users perceive it:** Protects production LLM applications against injection attacks at $0.042/M tokens, cutting guardrail costs by 95% compared to running Llama-Guard or Claude Haiku.
- **How to implement it:** Standard middleware package wrapping `jev-kit` injection questions. Configurable `onFlag` behavior (reject 403, flag header, or send to review).

#### 15. `jev-ci-gate`: GitHub Action for PR & Commit Sanity
- **How it works:** An official GitHub Action (`uses: JYeswak/jev-ci-gate@v1`). Runs on pull requests. Validates commit messages against diffs, checks for accidental secrets or debug flags, and verifies that README/doc updates match code changes.
- **How users perceive it:** Instant, automated semantic PR review in GitHub Action checks without needing expensive third-party SaaS review bots.
- **How to implement it:** Docker or composite GitHub Action running `jev` CLI over PR metadata and diffs.

#### 16. Interactive 60-Second Web Playground / Tour
- **How it works:** A zero-config local web UI (`npx jev-tour` or hosted on Vercel). Lets users paste text, try out Guard, Route, and Score primitives, see the live request/response JSON and token breakdown, and copy ready-to-run Python/TypeScript snippets.
- **How users perceive it:** Strangers understand what Jev is and how it behaves within 30 seconds of visiting the project, completely eliminating the 55KB README hurdle.
- **How to implement it:** Single Next.js or static HTML/Tailwind app running against `jev-kit` or local mock mode.

#### 17. `jev-eval`: CLI Evaluation & Calibration Tool
- **How it works:** A developer tool for teams building on LLMs. Takes a JSONL dataset of model outputs and ground truth, runs Jev Score/Noul rubrics in parallel, and computes Brier score, ECE, accuracy, and confusion matrices.
- **How users perceive it:** Replaces slow, non-deterministic LLM-as-a-judge (GPT-4) with a fast, calibrated evaluator that runs in seconds for pennies.
- **How to implement it:** Standalone CLI package derived from `foundation/run_calibration.py`.

#### 18. `jev-langchain` & `jev-llamaindex` Integrations
- **How it works:** Native retriever and guardrail plugins for LangChain, LlamaIndex, and Vercel AI SDK (`ai`). Implements standard `BaseRetriever` interface for passage re-ranking.
- **How users perceive it:** Existing AI engineers adopt Jev with zero code refactoring by simply swapping out their retriever class.
- **How to implement it:** Light connector packages adhering to LangChain and LlamaIndex plugin specifications.

#### 19. `jev-mock`: Offline Deterministic Test Harness
- **How it works:** A lightweight mock engine for unit tests. Allows developers to test their Jev-dependent application code in CI without an API key, using recorded golden distributions or deterministic rules.
- **How users perceive it:** Eliminates CI flakes and billing leaks during automated testing.
- **How to implement it:** Integrated into `jev-kit` (`new Jev({ mock: true })` or `JevMock.record()`).

#### 20. `jev-scaffold`: Pattern Code Generator (`jev recipe new`)
- **How it works:** CLI generator that scaffolds end-to-end boilerplate for common architectural patterns (confidence cascades, intent routing, parallel questions) with typed schemas and tests.
- **How users perceive it:** Developers skip boilerplate setup and immediately start with battle-tested patterns from TypeSafe's cookbooks.
- **How to implement it:** Subcommand in `jev` CLI rendering modular templates.

---

### Category C: Reliability, Robustness & Safety Architecture

#### 21. `jev-shield`: Universal Size & Schema Preflight Engine
- **How it works:** Client-side interceptor that validates every outgoing request before touching the wire. Checks:
  1. Input token limit (<32k tokens, calculated using 1.8 bytes/token heuristic for JSON).
  2. Choice option constraints (2 <= N <= 255 options, non-empty labels).
  3. Non-trivial question content.
  4. Response schema adherence and numeric invariants (`sum(p) == 1.0`, finite numbers).
- **How users perceive it:** Completely eliminates the recurring "infeasible input" failures and silent 400 errors that plagued our research benchmarks.
- **How to implement it:** Core validation module inside `work/jev-client` and `jev-kit`. Throws explicit `PreflightValidationError` before network dispatch.

#### 22. `jev-resilience`: Circuit Breaker & Adaptive Rate Limiter
- **How it works:** Implements token-bucket rate limiting (enforcing the 20 req/s and 1,200 req/min upstream caps), exponential backoff with jitter on 429/503/529, and an automatic circuit breaker if error rates exceed 15% over a 60-second sliding window.
- **How users perceive it:** Production apps never crash under load, never get banned by TypeSafe, and gracefully degrade during upstream API hiccups.
- **How to implement it:** Built directly into the client transport layer in `work/jev-client`.

#### 23. `jev-cascade`: Transparent LLM Fallback on Low Confidence
- **How it works:** A policy wrapper that checks Jev confidence on critical decisions. If Jev confidence is below a configured threshold (e.g. <0.65) or if the API is unreachable, automatically cascades the identical state to a free OpenRouter model (`dots-studio/dots-3-note-preview:free` or local model) via the System One adapter.
- **How users perceive it:** Seamless reliability and high accuracy even on ambiguous boundary cases, with zero additional cost.
- **How to implement it:** Client-level middleware chaining `work/jev-client` with `upstream/typesafe-ai/system-one-adapter-python`.

#### 24. `jev-cache`: Semantic & Deterministic Response Cache
- **How it works:** Local in-memory and SQLite cache keyed on the SHA-256 of `(model, canonical_state, canonical_questions)`. Returns cached distributions for identical states within a configurable TTL.
- **How users perceive it:** 0ms latency and $0 cost for repeated queries (such as checking common shell commands, identical diffs, or duplicate user questions).
- **How to implement it:** Pluggable cache interface in `jev-kit`.

#### 25. `jev-audit`: Structured Receipt & Compliance Logger
- **How it works:** Automatically captures an immutable audit record for every decision: timestamp, model SHA, input SHA, scores, confidence, latency, and applied policy. Emits clean NDJSON for ClickHouse, Datadog, or local file logging.
- **How users perceive it:** Full visibility and compliance tracking for enterprise AI deployments.
- **How to implement it:** Opt-in logging handler in `jev-kit`.

---

### Category D: High-Leverage Domain Applications & Workflows

#### 26. `jev-doc-aligner`: Stale Documentation & Signature Detector
- **How it works:** Compares README and documentation code snippets against recent code changes. Asks Jev: "Does this documentation snippet accurately reflect the updated function signature and usage in the codebase?"
- **How users perceive it:** Prevents documentation from rotting silently as APIs evolve.
- **How to implement it:** Node script extracting markdown code blocks and running Jev Noul checks against source files.

#### 27. `jev-rag-cleaner`: Toxic Passage & Injection Scrubber for RAG
- **How it works:** Positioned between document retrieval and LLM context synthesis. Runs parallel Jev checks on retrieved chunks: (1) prompt injection / instruction override attempt, (2) relevance to user query, (3) contradiction with ground truth.
- **How users perceive it:** Prevents indirect prompt injection attacks via retrieved documents while improving RAG synthesis quality.
- **How to implement it:** Standalone Python/TypeScript class for RAG pipelines.

#### 28. `jev-pr-summary-verifier`: PR Description Truthfulness Checker
- **How it works:** Compares PR descriptions against actual git diffs in GitHub Actions. Flags when PR descriptions claim changes that are not present, or fail to mention major breaking changes.
- **How users perceive it:** Increases code review efficiency by ensuring PR descriptions are trustworthy.
- **How to implement it:** GitHub Action step calling `jev check`.

#### 29. `jev-bug-dedup`: Issue Triage & Duplicate Detector
- **How it works:** Compares newly filed GitHub issues against existing open issues and recent commits. Categorizes component, severity, and flags likely duplicates with confidence scores.
- **How users perceive it:** Maintainers save hours of triage time on large open source repositories.
- **How to implement it:** GitHub webhook server running Jev Choice/Score.

#### 30. `jev-agent-arbiter`: Consensus & Tie-Breaker for Multi-Agent Swarms
- **How it works:** When two competing agents propose conflicting patches or architectural approaches, Jev scores both diffs against the task specification on a multi-point rubric (minimal diff, correctness, idiomatic style, safety).
- **How users perceive it:** Resolves multi-agent deadlocks autonomously with transparent, calibrated scoring.
- **How to implement it:** Extension to the dueling wizards workflow in `scripts/`.

---

## 2. Winnowing: Selecting the Top 5

To select the very best 5 ideas from the 30 candidates, we apply four strict filters derived directly from Joshua's mandate:
1. **Escape the Meta-Testing Trap:** Does it deliver a real, operational tool or consumer, rather than another test harness or benchmark?
2. **Dual-Audience Leverage:** Does it provide immediate, tangible value to **us in omp** AND to **strangers** wanting to adopt Jev?
3. **Accretive on Measured Wins:** Does it build directly on what this repository has already proven works (tool-call safety, compaction, injection screening, passage re-ranking), rather than opening speculative unmeasured veins?
4. **Pragmatic & Low Ceremony:** Can it be built, shipped, and dogfooded rapidly without hundreds of lines of prose rules or brittle abstractions?

### Why Other High-Profile Ideas Were Cut
- **`jev-trial` (Claude's #1 idea):** Building a 500-line testing kernel with e-processes and anytime-valid stopping is still *building testing infrastructure*. It directly contradicts Joshua's instruction to stop repeated testing. Preflight validation belongs inside the *client SDK*, not in a test harness.
- **Game Playing (Jericho, Pokemon, MiniWoB):** Academic research games are high-friction, harness-heavy distractions. Jev is a typed classifier, not an RL policy network. Spending days debugging gym wrappers has zero relevance to our products or strangers.
- **Complex Multi-Agent Arbiter:** High conceptual appeal, but low daily frequency. We need tools that fire hundreds of times a day.

---

## 3. The Top 5 Best Ideas (Ranked from Best to Worst)

---

### Rank 1: `jev-kit` + `jev` CLI — The Zero-Dependency Stranger SDK & Command-Line Utility

#### Why It Is the Very Best Idea
This is the single most accretive, high-leverage product this project can build. Today, a stranger who discovers this repo is confronted with a 55KB README filled with academic dispute ledgers, 20 vendored submodules, and hundreds of internal scripts. There is no simple way to just *use* Jev.

`jev-kit` synthesizes our entire 9 days of hard-won knowledge—the input size rules, the fail-safe error taxonomies, the answer-shape guards, the certified injection and gate questions, and the mock harness—into **one clean, zero-dependency package and CLI tool**.

#### How It Works
`jev-kit` provides two interfaces:

1. **The SDK (TypeScript & Python):**
   ```ts
   import { Jev } from "jev-kit";
   const jev = new Jev(); // reads TYPESAFE_API_KEY from env or infisical

   // High-level ergonomic verbs
   const guard = await jev.guard(userInput);
   if (guard.flagged) throw new Error("Security violation");

   const route = await jev.route("I want to cancel my account", ["billing", "support", "sales"]);
   console.log(route.choice, route.confidence);

   const check = await jev.verify({ claim: "Tests passed", evidence: testOutput });
   ```

2. **The `jev` CLI:**
   ```bash
   # Quick commands for scripts, CI, and terminal use
   jev doctor                                    # verifies key, connectivity, model pin
   jev guard "Ignore previous instructions..."    # exits 1 if flagged, 0 if clean
   jev route "need refund" "billing,tech,sales"  # prints chosen route + confidence
   jev check --claim "..." --evidence "..."      # exits 0 if supported
   ```

3. **Built-in `jev-shield` Preflight:**
   Every call automatically checks token budget (<32k tokens), validates choice bounds (2–255 options), and strips malformed inputs *before* touching the wire. This permanently eliminates the 12+ infeasible input defects that ruined past benchmarks.

4. **Built-in Mock Mode:**
   `new Jev({ mock: true })` or running without a key returns deterministic, typed mock structures, allowing downstream consumers to unit-test their apps in CI with zero cost and zero network.

#### How Users Perceive It
- **The Stranger:** Clones the repo or installs the package. Within 60 seconds, they run `jev doctor` and execute their first working classification. The README transforms from a 55KB ledger into a crisp, inviting 3-page developer portal with copy-pasteable recipes.
- **The Internal Agent:** Imports `jev-kit` directly across all omp tools and scripts, eliminating duplicate fetch logic and inconsistent error handling.

#### Implementation Architecture
- Pure TypeScript (ESM) and Python twin.
- Zero dependencies beyond the official `@typesafe-ai/sdk`.
- Code extracted directly from the battle-tested `work/jev-client/src/index.ts`, `work/bicameral-gate/`, and `foundation/`.
- Packaged with an installer script (`curl -fsSL https://... | bash`) that installs the `jev` CLI to `~/.local/bin`.

#### Risks & Mitigations
- *Risk:* Over-engineering into a heavy framework.
- *Mitigation:* Strict scope boundary: 5 high-level functions (`guard`, `route`, `score`, `rerank`, `verify`), the preflight validator, and the CLI wrapper. Total codebase under 800 lines.

---

### Rank 2: `omp-safe-guard` — Active Pre-Tool Execution Safety Interceptor for the Fleet

#### Why It Is the Second Best Idea
This is the immediate, daily internal consumer that justifies Jev's existence in omp. In `work/bicameral-gate/`, we already proved that Jev catches **78/100 real destructive command risks at only 1/300 false alarms**. But today, that capability sits in an observe-only logging script (`jev-gate-observe.ts`) that nobody reads!

An observe-only log is not a product; it is a research artifact. `omp-safe-guard` turns this proven capability into an **active pre-execution safety gate** protecting all omp agent panes from data loss.

#### How It Works
1. **Pre-Tool Interception:** Installed in `.omp/hooks/pre/tool-call.ts`. Every `bash` call passes through the hook.
2. **Instant Local Whitelist (Zero Overhead on 90% of Commands):**
   Commands matching safe patterns (`git status`, `git diff`, `ls`, `cat`, `read`, `cargo check`, `npm test`, `echo`) bypass Jev entirely. They execute with **0ms latency overhead**.
3. **Targeted Jev Risk Evaluation:**
   Potentially hazardous commands (`rm`, `git reset --hard`, `git clean`, `git checkout .`, `DROP`, `kill`, `chmod -R`) are packaged into `state: { command, cwd, git_status }` and sent to Jev.
4. **Actionable Enforcement:**
   - If Jev risk probability `p >= 0.80` with high confidence: omp halts execution and displays a 1-line interactive confirmation chip: `[Jev Guard: High risk of unrecoverable data loss (p=0.88). Confirm execution? (y/N)]`.
   - In unattended/automated mode: returns `{ block: true, reason: "Jev safety gate blocked destructive command" }`.
5. **Fail-Open Reliability:**
   If Jev times out (>1000ms), returns a 5xx error, or the key is absent, the hook fails open with a discreet log entry. The agent is **never hung**.

#### How Users Perceive It
- For 95% of commands, users and agents notice zero difference.
- When an agent hallucinates a catastrophic `git reset --hard HEAD~5` or accidentally deletes a sibling's directory, the tool call is instantly caught and prevented.
- Fleet traffic becomes live dogfooding data, turning our everyday work into empirical proof of Jev's value.

#### Implementation Architecture
- Refactor `.omp/hooks/post/jev-gate-observe.ts` into `.omp/hooks/pre/jev-safe-guard.ts`.
- Incorporate the fast-path regex whitelist before calling `askJev`.
- Enforce strict 1,000ms abort controller timeout on the network call.

#### Risks & Mitigations
- *Risk:* False positives frustrating agents or slowing down rapid terminal workflows.
- *Mitigation:* The local whitelist handles common development commands. The Jev threshold is set strictly to `p >= 0.80` with confidence gating; boundary cases fail open.

---

### Rank 3: `omp-compact-live` — Live Context Compactor Hook for Long-Running Omp Sessions

#### Why It Is the Third Best Idea
Context window exhaustion is the single largest operational cost and performance bottleneck for coding agents in omp. As conversations reach 50–100 turns, context windows fill up with thousands of lines of compiler errors, massive grep dumps, and redundant test output. The agent becomes sluggish, expensive, and prone to forgetting early instructions.

`fast-jev-compaction` and `work/p2-compaction` already proved that Jev can judge keep/drop per tool call without summarizing—preserving critical debugging context byte-for-byte while dumping boilerplate. Moving this into a live omp hook immediately extends agent stamina and slashes frontier LLM token costs.

#### How It Works
1. **Hook Insertion:** Wires into omp's `session_before_compact` and per-turn context assembly hooks.
2. **Selective Candidate Identification:**
   Ignores user messages and system instructions. Focuses exclusively on past `tool_result` blocks exceeding 20 lines.
3. **Parallel Keep/Drop Classification:**
   Sends tool result headers and intent to Jev with parallel Noul questions: `"Is this tool result necessary to understand or resolve the current task?"`
4. **Verbatim Preservation & Truncation:**
   - Essential results (diffs, active stack traces, compiler errors): kept **100% byte-identical**.
   - Low-signal results (successful test runs, verbose build progress, directory listings): truncated to a clean 3-line head/tail stub: `[Truncated 142 lines of clean build output]`.
5. **Fail-Safe Invariant:** Any unjudged or timed-out entry defaults to **KEEP**.

#### How Users Perceive It
- Agents maintain high performance and sharp reasoning across multi-hour sessions.
- Token billing on Opus/Claude/GPT drops by 40–60%.
- Compaction happens seamlessly in the background without truncating vital error history.

#### Implementation Architecture
- Native TypeScript hook in `.omp/hooks/pre/jev-compact.ts`.
- Leverages the existing `fast-jev-compaction` logic already vendored and verified in the repo.
- Runs asynchronously during session idle periods or right before compaction thresholds trip.

#### Risks & Mitigations
- *Risk:* Accidentally dropping a tool result that contained a subtle error needed 10 turns later.
- *Mitigation:* Conservative threshold: keep if `p(keep) >= 0.40`. Stacks traces and diffs are unconditionally whitelisted by regex before calling Jev.

---

### Rank 4: `jev-mcp` — Universal One-Click MCP Server for Modern IDEs & Agents

#### Why It Is the Fourth Best Idea
Model Context Protocol (MCP) is the universal bridge across the entire AI engineering ecosystem. Developers who do not use omp are using Cursor, Windsurf, Claude Desktop, or custom agent harnesses.

`jev-mcp` packages Jev's three proven strengths into an official, turnkey MCP server that anyone can install with one line in their `.mcp.json`. It turns Jev from a private internal tool into an accessible utility across the entire coding agent market.

#### How It Works
1. Exposes three streamlined tools over stdio/SSE:
   - `jev_guard`: Fast injection, jailbreak, and input safety screen.
   - `jev_rerank`: Re-ranks 2–30 code or text passages by semantic relevance to a query.
   - `jev_verify_claim`: Evaluates whether a qualitative claim is supported or contradicted by evidence text.
2. **Zero Configuration:** Reads `TYPESAFE_API_KEY` from environment or standard config path (`/tmp/.tskey`, `~/.config/jev/key`).
3. **Agent-Optimized Descriptions:** Schemas and descriptions are meticulously tuned so frontier models (Claude 3.7, GPT-4o, Codex) understand exactly when and how to invoke each tool without hesitation.

#### How Users Perceive It
- A developer adds `"npx -y jev-mcp"` to their Cursor or Claude Desktop config.
- In their next conversation, when searching through large codebases or reviewing user inputs, their IDE assistant autonomously calls `jev_rerank` or `jev_guard` to improve its own answers.

#### Implementation Architecture
- Refactor the existing code in `jev-mcp/` and `.omp/tools/` into a polished, standalone npm package.
- Built using `@modelcontextprotocol/sdk`.
- Includes automated unit tests and mock-mode verification.

#### Risks & Mitigations
- *Risk:* External agents under-utilizing tools due to vague prompt triggers.
- *Mitigation:* Embed concrete, directive trigger descriptions in tool metadata (e.g., "Use when choosing between more than 5 code snippets" or "Use before executing unfamiliar shell commands").

---

### Rank 5: `jev-ci-gate` — Semantic PR, Commit & Documentation Verifier GitHub Action

#### Why It Is the Fifth Best Idea
Brings Jev into the software development lifecycle where human teams and CI/CD pipelines operate. While `omp-safe-guard` and `omp-compact-live` serve agent sessions, `jev-ci-gate` acts as an automated, intelligent gatekeeper on Pull Requests in GitHub.

It proves that Jev can perform high-value semantic checks in CI for fractions of a cent, beating slow, expensive LLM-based PR review bots.

#### How It Works
1. **GitHub Action Integration:** Runs on `pull_request` and `push` events via `.github/workflows/jev-gate.yml`.
2. **Three Automated Semantic Checks:**
   - **Commit-Diff Alignment:** Checks if commit messages match actual staged diffs (catching misleading or junk commit messages).
   - **Credential & Secret Scan:** Fast semantic check for accidental key exposures or sensitive debug flags.
   - **Documentation Drift Check:** Checks whether changed function signatures in code PRs are reflected in updated docs/README.
3. **Cost & Speed:** Completes in <3 seconds for less than $0.002 per PR run. Emits a clean GitHub Actions summary and PR comment if violations are found.

#### How Users Perceive It
- Engineering teams get fast, automated sanity checks on incoming PRs without paying $20/user/month for heavy AI review tools.
- Blocks sloppy multi-agent PRs from polluting upstream repositories.

#### Implementation Architecture
- GitHub Action wrapping the `jev` CLI.
- Reads `GITHUB_EVENT_PATH` to extract PR diffs and commit messages.
- Outputs GitHub Markdown annotations and job summary.

#### Risks & Mitigations
- *Risk:* Blocking CI builds on false positives, annoying engineering teams.
- *Mitigation:* Default mode is advisory (warning comments on PR). Hard failure mode is opt-in via `--strict`.

---

## 4. Comparison & Priority Matrix

| Idea | Target Audience | Primary Value Proposition | Latency / Cost Impact | Implementation Effort | Confidence |
|---|---|---|---|---|---|
| **1. `jev-kit` + CLI** | Strangers & Internal Fleet | Unified SDK, instant on-ramp, preflight safety engine | 0ms / $0 (Prevents failed API calls) | **Low** (Extract from `work/jev-client`) | **99%** |
| **2. `omp-safe-guard`** | Omp Fleet (Internal) | Active protection against destructive bash commands | 0ms on 90% whitelist, ~500ms on risky | **Low** (Refactor `jev-gate-observe`) | **95%** |
| **3. `omp-compact-live`** | Omp Fleet (Internal) | Prevents context exhaustion, slashes LLM tokens 50% | Background async, saves $$$ on frontier models | **Medium** (Wire `fast-jev-compaction`) | **92%** |
| **4. `jev-mcp`** | External AI Developers | Turnkey MCP server for Cursor, Windsurf, Claude | ~500ms on-demand tool call | **Low** (Package existing tools) | **94%** |
| **5. `jev-ci-gate`** | Enterprise & OSS Teams | Semantic PR & commit validation in GitHub Actions | <3s in CI / <$0.002 per PR | **Medium** (Action packaging) | **88%** |

---

## 5. Immediate Accretive Roadmap (Next 48 Hours)

To execute Joshua's mandate immediately without opening new speculative research veins, here is the concrete execution plan:

1. **Step 1: Consolidate `jev-kit` (`work/jev-kit/`):**
   - Extract the core client from `work/jev-client/src/index.ts`.
   - Embed `jev-shield` preflights (input token size check, choice option validation, failure taxonomy).
   - Add the 5 clean verbs: `guard()`, `route()`, `score()`, `rerank()`, `verify()`.
   - Add the standalone executable CLI `bin/jev` with `doctor`, `guard`, `route`, and `check`.
   - Verify offline tests pass with zero key.

2. **Step 2: Activate `omp-safe-guard` in Omp:**
   - Migrate `.omp/hooks/post/jev-gate-observe.ts` to `.omp/hooks/pre/tool-call.ts`.
   - Add the local fast-path whitelist for benign commands.
   - Set the active gate threshold to `p >= 0.80` with fail-open timeout.
   - Verify against real test commands.

3. **Step 3: Transform the Root `README.md`:**
   - Prune the 55KB academic ledger into a clean, compelling 3-page developer portal.
   - Lead with the 60-second quickstart (`npx jev-kit` / `pip install jev-kit`).
   - Move the historical benchmark tables and negative evidence ledgers into `docs/benchmarks/`.
   - Showcase the 3 core primitives and live recipes.

4. **Step 4: Package `jev-mcp`:**
   - Publish or symlink `jev-mcp` so any Cursor/Claude Desktop user can add it with one command.

This plan terminates the meta-testing loop, gives our omp fleet active daily protection, and gives strangers a world-class on-ramp to TypeSafe System One.
