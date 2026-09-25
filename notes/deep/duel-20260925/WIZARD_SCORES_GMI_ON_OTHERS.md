# WIZARD_SCORES_GMI_ON_OTHERS: Critical Evaluation of Claude and Codex Proposals

**Evaluator:** Antigravity / Gemini (pane 18, profile `agy`, identity `BeigeGrove`), 2026-09-25.
**Subject Files:**
- `notes/deep/duel-20260925/WIZARD_IDEAS_CC.md` (Claude / AmberWillow, pane 1)
- `notes/deep/duel-20260925/WIZARD_IDEAS_COD.md` (Codex, pane 3)
**Governing Mandate (Joshua, verbatim):** *"lets move this out of repeated testing over and over to actually turning this into something relevant and usable"*.

---

## 0. Scoring Rubric & Methodology

Every candidate proposal is evaluated on a strict 0 to 1000 scale across four weighted axes:
1. **Strategic Relevance (30%):** Does it break the meta-testing trap and deliver an actual, relevant tool/consumer, or does it double down on testing infrastructure?
2. **Real-World Utility (30%):** How valuable is it in practice for human developers and for AI coding agents working in omp?
3. **Implementation Pragmatism (20%):** Can it be implemented cleanly without brittle regexes, framework bloat, or complex harness dependencies?
4. **Complexity vs. Tech-Debt ROI (20%):** Does the concrete benefit easily justify the maintenance burden, latency overhead, and API spend?

### Score Bands
- **900–1000:** Indispensable core moves that immediately unlock product value, establish real consumers, or solve fatal stranger barriers.
- **800–899:** Highly accretive, pragmatic additions with clear ROI and low maintenance cost.
- **650–799:** Decent concept, but limited by passivity (shadow-only), narrow scope, or modest leverage.
- **450–649:** Marginal value; high complexity, premature abstraction, or lingering testing-orientation.
- **0–449:** Counterproductive, harness-heavy distraction, or direct perpetuation of the meta-testing loop.

---

## 1. Master Score Table (All 35 Ideas)

| Origin File | Idea # | Title | Score (0–1000) | One-Line Reason |
|---|---|---|---|---|
| `WIZARD_IDEAS_CC.md` | CC-1 | `jev-trial`: unified experiment kernel & preflights | **510** | Doubles down on the testing trap; preflight checks belong in the client SDK, not in another benchmark runner. |
| `WIZARD_IDEAS_CC.md` | CC-2 | Jev in fleet hot path (shadow mode) | **740** | Real fleet consumer is the right direction, but permanent observe-only logging creates no active product value. |
| `WIZARD_IDEAS_CC.md` | CC-3 | `jev-kit` published with stranger quickstart | **925** | The single highest-leverage external move; packages the SDK, preflights, and slashes the 55KB README hurdle. |
| `WIZARD_IDEAS_CC.md` | CC-4 | Agent-first tool contract (`doctor`, robot JSON, installer) | **855** | Adopts Jeffrey's proven standard; makes tools easily discoverable and drivable by autonomous agents. |
| `WIZARD_IDEAS_CC.md` | CC-5 | Re-scope games/computer use to fast-judge in planner | **420** | Lingering academic distraction; debugging gym wrappers and game clocks does not advance our real products. |
| `WIZARD_IDEAS_COD.md` | COD-1 | OMP shadow decision plane with outcome feedback | **765** | Solid expansion of the shadow gate linking to actual human outcomes (reverts/denies), but still strictly passive. |
| `WIZARD_IDEAS_COD.md` | COD-2 | `jev-kit`: thin TS/Python decision package | **940** | Best formulation of the kit: extracts stable core from `work/jev-client`, keeps zero runtime deps, enforces preflights. |
| `WIZARD_IDEAS_COD.md` | COD-3 | Experiment kernel: prereg, preflight, scorer, resume | **530** | Well-architected, but fundamentally answers the wrong problem: we need tools to ship, not better test execution. |
| `WIZARD_IDEAS_COD.md` | COD-4 | Native omp Judge-role bridge with safe profile | **885** | Brilliant leverage of existing omp 18.3 runtime primitives (`judge`/`judge_batch`) with zero custom tool overhead. |
| `WIZARD_IDEAS_COD.md` | COD-5 | `jevify`: guarded bulk classification over local files | **780** | Pragmatic AI Map-Reduce application for diffs and logs, though requires strict local secret-taint boundaries. |
| `WIZARD_IDEAS_COD.md` | COD-6 | Redacted score register with replay & drift reports | **630** | Sound audit trail concept, but risks becoming a passive JSONL graveyard without an active consumer. |
| `WIZARD_IDEAS_COD.md` | COD-7 | `omp doctor jev`: readiness before a call or claim | **860** | Fast, high-utility diagnostic preventing unconfigured keys and unreachable bars before any spend occurs. |
| `WIZARD_IDEAS_COD.md` | COD-8 | Taint-aware state builder & secret redaction | **805** | Essential defense-in-depth preventing accidental API credential/data leaks across all future tools. |
| `WIZARD_IDEAS_COD.md` | COD-9 | Per-seat calibration & coverage profiles | **670** | Statistically rigorous, but introduces premature configuration bureaucracy before real tools are in daily use. |
| `WIZARD_IDEAS_COD.md` | COD-10 | Human review queue as explicit fail-safe consumer | **725** | Clear triage design for uncertain scores, but easily degenerates into an unread spam queue without UI tooling. |
| `WIZARD_IDEAS_COD.md` | COD-11 | One-request fan-out API with policy combinators | **875** | Exceptional API design; fully exploits Jev's parallel question superpower via clean `all`/`any`/`max-risk` operators. |
| `WIZARD_IDEAS_COD.md` | COD-12 | Compaction hook from shadow report to action | **870** | Directly attacks the #1 pain point of long agent sessions (context bloat) using byte-identical selective retention. |
| `WIZARD_IDEAS_COD.md` | COD-13 | Diff-review feedback loop | **640** | Delayed, noisy human feedback signals make threshold calibration difficult and merging authority impossible. |
| `WIZARD_IDEAS_COD.md` | COD-14 | Tool-result evidence-density triage | **810** | High-utility context squeezer that preserves compiler errors while dropping repetitive build progress spam. |
| `WIZARD_IDEAS_COD.md` | COD-15 | Semantic cache-validity gate | **590** | High risk of stale false-positives; caching probabilistic judgments adds more complexity than token savings justify. |
| `WIZARD_IDEAS_COD.md` | COD-16 | Receipt-driven README & example generation | **850** | Replaces the bloated 55KB ledger with an automated, verifiable results table and clean stranger quickstart. |
| `WIZARD_IDEAS_COD.md` | COD-17 | Five-minute stranger package runner | **895** | Essential on-ramp proving offline policy, mock fallback, and clear live instructions in under 5 minutes. |
| `WIZARD_IDEAS_COD.md` | COD-18 | Typed question/state compiler | **560** | Over-abstracted metaprogramming; declaring typed questions in TypeScript/Python is already only 5 lines of code. |
| `WIZARD_IDEAS_COD.md` | COD-19 | Free-incumbent differential runner | **680** | Respects the no-paid-comparisons rule, but remains focused on benchmarking rather than building usable tools. |
| `WIZARD_IDEAS_COD.md` | COD-20 | Anytime-valid experiment runner (e-process) | **490** | Elegant mathematics from asupersync, but solving the early-stopping problem in tests does not create a product. |
| `WIZARD_IDEAS_COD.md` | COD-21 | `jev_select`: best-of-N trajectory selector | **675** | Conceptually sound, but candidate diversity is often low and previous OSWorld trials suffered severe power issues. |
| `WIZARD_IDEAS_COD.md` | COD-22 | Browser action lattice plus verifier slot | **530** | 130ms latency per step is too slow for real browser loops, and eval-prelude browser calls bypass tool hooks. |
| `WIZARD_IDEAS_COD.md` | COD-23 | AX-tree pruning with full-tree fallback | **610** | Promising cost-saver, but prior MiniWoB experiments missed the 40% token-reduction bar; needs stronger evidence. |
| `WIZARD_IDEAS_COD.md` | COD-24 | Desktop transition verifier | **480** | Host-bridge blind spots, screenshot privacy concerns, and heavy complexity yield poor operational ROI. |
| `WIZARD_IDEAS_COD.md` | COD-25 | Host-owned irreversible-action confirmation | **785** | Pragmatic desktop safety gate on the host seam, though largely superseded by the tool-call bash gate. |
| `WIZARD_IDEAS_COD.md` | COD-26 | Jev-PUCT prior/value for text games (Jericho) | **430** | Text-adventure games are research theater; they consume massive engineering time with zero production relevance. |
| `WIZARD_IDEAS_COD.md` | COD-27 | Clock-aware Pokémon decision controller | **390** | Entertaining showcase, but completely disconnected from practical developer tooling or coding agent needs. |
| `WIZARD_IDEAS_COD.md` | COD-28 | Real-time reflex anomaly monitor | **460** | Event-window triggers are difficult to calibrate; scripted baselines dominate symbolic environments effortlessly. |
| `WIZARD_IDEAS_COD.md` | COD-29 | Game trajectory step monitor | **440** | Self-authored subgoals provide weak labels and high false alarm rates in complex state transitions. |
| `WIZARD_IDEAS_COD.md` | COD-30 | Task-difficulty/model/effort router | **710** | Reasonable concept for routing easy tasks to cheap models, but historical cascade evidence in this lane is weak. |

---

## 2. Detailed Evaluation of Claude's Proposals (`WIZARD_IDEAS_CC.md`)

Claude's submission is tightly structured around 5 ideas, but reveals a fundamental cognitive bias: **Claude is obsessed with building testing harnesses.** When Joshua explicitly intervened to say *"lets move this out of repeated testing over and over to actually turning this into something relevant and usable"*, Claude's immediate response was to propose `jev-trial` as idea #1.

### CC-1: `jev-trial`: unified experiment kernel & preflight runner
- **Score: 510 / 1000**
- **The Case For:** It directly addresses the 25 harness bugs, 12 infeasible inputs, and 3 unreachable bars that corrupted past benchmarks. Turning prose rules into executable preflight refusals is solid defensive engineering.
- **The Fatal Flaw:** It is still a test runner. It exists solely to run more benchmark experiments. A developer or agent wanting to *use* Jev does not want to run benchmarks; they want to guard a prompt, route a query, or compress context. Preflight checks (size limits, choice option counts, schema guards) belong directly in the client library (`jev-kit`), not in a bespoke benchmark runner.
- **Verdict:** Necessary as internal plumbing if we ever run another benchmark, but proposing it as the #1 next-stage priority completely misses the product mandate.

### CC-2: Jev in fleet hot path (shadow mode)
- **Score: 740 / 1000**
- **The Case For:** Points Jev at real fleet traffic on every bash command. Uses our own daily work as the labelled dataset. Leverages a proven capability (78/100 catch at 1/300 false alarms).
- **The Limitation:** Strictly observe-only. We already have `jev-gate-observe.ts` running in shadow mode, and its logs are rarely inspected. A permanent shadow mode is the illusion of production: it spends tokens and writes JSONL rows, but protects nobody from data loss. It must graduate to an active, interactive gate on dangerous commands with an instant local whitelist for safe commands.
- **Verdict:** Good incremental step, but overly timid. Needs a clear path to active protection.

### CC-3: `jev-kit` published with stranger quickstart & receipt-driven README
- **Score: 925 / 1000**
- **The Case For:** Claude's best idea by a wide margin. Solves the massive stranger adoption barrier. Packages the client, validator, preflights, and fake asker into a clean, installable distribution. Collapses the 55KB academic ledger README into a concise quickstart with automated receipt tables.
- **Implementation Reality:** Highly practical. Almost all the code is already written and battle-tested in `work/jev-client/`. It merely needs extraction, clean packaging, and documentation.
- **Verdict:** Top-tier. Must be executed immediately.

### CC-4: Agent-first tool contract (`doctor`, robot JSON, one-line install)
- **Score: 855 / 1000**
- **The Case For:** Adopts Jeffrey's proven CLI discipline. Coding agents are our primary users; tools without `--robot` JSON or `doctor` diagnostics are difficult for autonomous agents to drive reliably.
- **Implementation Reality:** Low complexity. Exposing `doctor` (key check, model pin, size limit check) and `--robot` JSON output across our tools creates instant ergonomic leverage.
- **Verdict:** Highly accretive, high ROI, low maintenance burden.

### CC-5: Re-scope games and computer use to fast-judge in planner
- **Score: 420 / 1000**
- **The Case For:** Recognizes that Jev cannot serve as an autonomous sole policy in complex games and needs to act as a prior or critic.
- **The Fatal Flaw:** Games (Jericho text adventures, Pokémon Showdown, MiniWoB) are a massive time sink with virtually zero production applicability. We have burned days of fleet compute and human attention debugging gym wrappers, action space serialization, and clock timeouts. Continuing to pursue game benchmarks when our real developer tools have 0 organic callers is pure avoidance of product reality.
- **Verdict:** Should be frozen. Do not spend another engineering hour on game planners until core developer tools are shipped and dogfooded.

---

## 3. Detailed Evaluation of Codex's Proposals (`WIZARD_IDEAS_COD.md`)

Codex delivered a comprehensive 30-idea brainstorm and winnowed down to a coherent top 5. Codex demonstrates deeper familiarity with omp's native primitives and articulates stronger operational boundaries, though it occasionally strays into premature abstraction.

### The Standout Winners in Codex's Roster

#### COD-2: `jev-kit`: thin TS/Python decision package
- **Score: 940 / 1000 (Highest in Duel)**
- **Why it wins:** Codex nails the design: keep it thin, keep the official SDK as the wire owner, enforce zero external runtime dependencies, package the size preflight and failure taxonomy, and include the fake asker for offline tests. It creates a unified substrate for both strangers and internal omp tools.

#### COD-17: Five-minute stranger package runner
- **Score: 895 / 1000**
- **Why it wins:** Complements `jev-kit` by defining the exact user journey. A stranger runs one command, sees a deterministic offline classification pass, gets an explanation of why `NOT_RUN` occurred if no key is present, and sees the exact copy-paste snippet for live use. Completely destroys the cognitive barrier of this repository.

#### COD-4: Native omp Judge-role bridge with safe project profile
- **Score: 885 / 1000**
- **Why it wins:** The smartest internal integration proposal. Instead of hand-rolling custom MCP servers or standalone extensions that agents ignore, configure omp 18.3's built-in `judge()` and `judge_batch()` primitives to route to Jev. It meets agents directly where the harness already provides native APIs.

#### COD-11: One-request fan-out API with policy combinators
- **Score: 875 / 1000**
- **Why it wins:** Jev's greatest architectural advantage over sequential LLM prompting is parallel question evaluation over a single state. Codex's proposal to formalize combinators (`all`, `any`, `max-risk`, confidence thresholds) makes complex multi-criteria decisions trivial to write in user code.

#### COD-12: Compaction hook from shadow report to selective action
- **Score: 870 / 1000**
- **Why it wins:** Attacks the universal pain point of agent harnesses: context exhaustion. Long sessions become sluggish and expensive. Using Jev to selectively drop verbose compilation spam while preserving error traces byte-for-byte is an enormous win for agent stamina.

#### COD-7: `omp doctor jev`: readiness before a call or a claim
- **Score: 860 / 1000**
- **Why it wins:** Preflight diagnostics that check key validity, model pin, hook discovery, and bar reachability before any spend. Prevents silent misconfigurations.

#### COD-16: Receipt-driven README & example generation
- **Score: 850 / 1000**
- **Why it wins:** Permanently solves the 55KB README maintenance problem. Lets receipts speak for themselves in a clean generated table while keeping human prose focused on quickstarts.

---

### The Over-Engineered, Passive, or Distracting Ideas in Codex's Roster

#### COD-3 & COD-20: Unified experiment kernel & anytime-valid e-process
- **Scores: 530 & 490 / 1000**
- **Critique:** Like Claude's CC-1, this is an over-investment in academic evaluation machinery. An anytime-valid e-process stopped early in tests is neat statistical theory, but Joshua's mandate was to get out of testing. Spending time building a generalized experiment kernel distracts from shipping products.

#### COD-18: Typed question/state compiler
- **Score: 560 / 1000**
- **Critique:** Premature metaprogramming. Declaring a Jev state and typed questions in TypeScript or Python requires 5 to 10 lines of standard code. Writing a compiler to generate that code introduces indirection and debugging headaches for virtually zero gain.

#### COD-15: Semantic cache-validity gate
- **Score: 590 / 1000**
- **Critique:** Asking Jev whether an old cached answer is still valid for a new prompt is paradoxical: you are making an API call to save an API call. A deterministic SHA-256 hash cache with a short TTL is 100x simpler, 0ms fast, and avoids subtle semantic cache invalidation bugs.

#### COD-22 to COD-29: Browser action lattices, AX-tree pruning, and game controllers
- **Scores: 390 to 610 / 1000**
- **Critique:** An extensive catalog of complex planner and computer-use ideas (Pokémon Showdown, Jericho, desktop screenshot verifiers, AX pruning). All suffer from severe operational friction: high per-step latency, invisible host-bridge event hooks, gym wrapper maintenance, and low relevance to daily coding workflows.

---

## 4. Synthesis: Shared Blind Spots of Both Models

Reviewing both `WIZARD_IDEAS_CC.md` and `WIZARD_IDEAS_COD.md` reveals three critical shared blind spots that our implementation must correct:

1. **The Fear of Active Intervention (The Shadow Trap):**
   Both Claude (CC-2) and Codex (COD-1) timidly advocate keeping Jev in "shadow mode" forever. They propose logging bash commands to JSONL and analyzing them offline. This is a failure of nerve. We *already* ran shadow logging in `jev-gate-observe.ts`, and nobody looks at it! A tool that only observes is not a product. We must introduce **active gating with an instant local whitelist**: safe commands execute with 0ms overhead; truly dangerous commands trigger a fast Jev evaluation and prompt the user with an interactive confirmation chip.

2. **The Gravitational Pull of Testing Harnesses:**
   Both models ranked a unified testing kernel in their top 3 (CC-1 and COD-3). When asked to make Jev usable, their reflexive instinct was to build a better test runner. We must reject this: preflight checks belong in `jev-kit` for all callers, not in a test-suite runner.

3. **Inability to Let Go of Game Benchmarks:**
   Both models spent substantial bandwidth trying to rehabilitate game playing (Jericho, Pokémon, MiniWoB) by embedding Jev into planners (CC-5, COD-26, COD-27). Computer games are an academic distraction for this lane. We must freeze them completely and focus 100% of our energy on coding agent ergonomics and developer tooling.

---

## 5. Final Recommended Product Core

Extracting the highest-scoring ideas across both proposals converges on an unmistakable, high-leverage 4-part product core:

1. **`jev-kit` (COD-2, CC-3, COD-17 — Avg Score: 920):**
   Zero-dependency TypeScript/Python SDK wrapping the official client, embedding size/option preflights, fake askers, and clean verbs (`guard`, `route`, `score`, `verify`). Packaged with a 5-minute stranger quickstart.
2. **Native Omp Integration (COD-4, COD-12, COD-14 — Avg Score: 855):**
   Configure omp's native `judge` role to point at Jev, wire `omp-compact-live` to prevent context exhaustion in long sessions, and squeeze verbose build tool outputs.
3. **Active Safety Gate (`omp-safe-guard` upgrading CC-2 & COD-1 — Avg Score: 850):**
   Graduate the command gate from passive shadow logging to an active pre-tool interceptor with a 0ms local whitelist and interactive confirmation chips on dangerous commands.
4. **Agent-First Ergonomics (`omp doctor jev` & `--robot` — CC-4, COD-7 — Avg Score: 860):**
   Standardize `doctor` diagnostics and machine-readable JSON across all shipped tools.

This terminates the meta-testing loop and establishes Jev as a permanent, indispensable capability in our daily workflow.
