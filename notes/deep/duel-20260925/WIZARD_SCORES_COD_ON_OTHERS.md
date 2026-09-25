# COD scoring of the other duel ideas

Date: 2026-09-25
Evaluator: IvoryCreek / Codex
Origins scored in full:

- `notes/deep/duel-20260925/WIZARD_IDEAS_CC.md` — five ideas from Claude/pane 1.
- `notes/deep/duel-20260925/WIZARD_IDEAS_GMI.md` — thirty ideas from Gemini.

This is an independent design score, not a Jev result. No Jev/API call was made. Scores combine
real human/agent utility, evidence of an actual consumer, implementation practicality, and whether
the benefit pays for complexity and maintenance. A high score is not approval to build; each idea
still needs a consumer, a pre-call feasibility arm, a non-authored outcome, and a bounded first
experiment.

The requested `NEXT-SCODE-PLAN.md` was absent. I evaluated against the current
`notes/deep/next-gen/NEXT-STAGE-PLAN.md`, `SYNTHESIS.md`, and `BRIEF.md`, plus the current client,
`.omp`, `foundation`, and script seams.

## Score table

| Origin | Idea # | Title | Score | One-line reason |
|---|---:|---|---:|---|
| CC | 1 | `jev-trial`: one experiment kernel | **790** | Highest leverage for repeated harness defects, but risks becoming a second research framework unless two real consumers land immediately. |
| CC | 2 | Jev in the fleet hot path, shadow mode | **930** | Direct daily consumer with organic labels and reversible rollout; the strongest answer to “make it relevant,” provided it stays advisory until measured. |
| CC | 3 | `jev-kit` published with five-minute quickstart | **900** | Best stranger-facing product and consolidates proven client discipline, but packaging and TS/Python scope can sprawl. |
| CC | 4 | Agent-first `doctor`, robot JSON, one-line install | **820** | Small, high-leverage ergonomics fix that makes every later surface usable by agents and strangers, though it is an enabler rather than the product. |
| CC | 5 | Jev as fast judge inside a planner | **650** | Correctly avoids sole-policy game claims and fits Jev’s distribution output, but planner harnesses and weak product consumer make it a later bet. |
| GMI | 1 | `omp-safe-guard`: active tool-call interceptor | **540** | Valuable outcome but premature blocking, hook blind spots, and current false-positive/recall evidence make the proposed active form unsafe. |
| GMI | 2 | `omp-compact-live`: live context compactor | **430** | Important pain, but current compaction evidence is below bar and model-driven dropping of context has asymmetric failure cost. |
| GMI | 3 | `omp-search-rerank`: code/grep result reranker | **650** | Existing rerank evidence is strong and the need is real, but intercepting native results adds latency and the consumer boundary is underspecified. |
| GMI | 4 | `omp-diff-reviewer`: semantic commit/sibling-leak gate | **570** | Useful shared-worktree problem, but overlapping reservations/kit guards already catch much of it and labels are weak. |
| GMI | 5 | `omp-failure-triage` | **610** | Good agent ergonomics and frequent trigger, but error taxonomy is cheaply rule-based and Jev’s added value is not yet shown. |
| GMI | 6 | `omp-claim-gate` | **520** | Targets real self-grading failures, but a model judging model prose risks recursion and lacks independent ground truth. |
| GMI | 7 | `omp-log-squeezer` | **470** | Token savings are plausible, but deterministic grouping/limits are safer and the proposal hides the preserve boundary. |
| GMI | 8 | `omp-subagent-router` | **570** | Routing is a valid Choice use, but profile quality, label scarcity, and routing thresholds are unresolved. |
| GMI | 9 | `omp-conflict-watcher` | **520** | Shared-file conflict prevention matters, but semantic polling is expensive and reservations/git structure are more reliable first. |
| GMI | 10 | `omp-test-flakiness-tagger` | **580** | Useful diagnosis, but requires a durable historical failure corpus and Jev may add little over signatures/timing. |
| GMI | 11 | `jev-kit`: zero-dependency stranger SDK | **900** | The most practical external product, directly grounded in `work/jev-client`; still needs ruthless scope control. |
| GMI | 12 | `jev` Unix CLI | **820** | A CLI is the fastest adoption path for humans, CI, and agents, but it overlaps `jev-kit` and needs packaging/release discipline. |
| GMI | 13 | `jev-mcp`: universal MCP server | **760** | Standard interoperability is compelling and prior code exists, but MCP distribution is not a consumer until strangers actually install it. |
| GMI | 14 | `jev-guard-middleware` | **690** | Real production value in LLM apps, but security middleware demands stronger ground truth and framework maintenance than this lane owns. |
| GMI | 15 | `jev-ci-gate` | **600** | Useful to teams, but semantic PR/document checks have noisy labels and overlap existing hooks, CI gates, and review advisory. |
| GMI | 16 | Interactive 60-second web playground | **560** | Onboarding improves, but a UI can hide live/configuration limits and adds a framework before the core package earns usage. |
| GMI | 17 | `jev-eval`: calibration/evaluation CLI | **730** | Strong fit for real users building typed decisions, but it can perpetuate the meta-testing trap unless paired with a shipped decision. |
| GMI | 18 | LangChain/LlamaIndex/Vercel integrations | **500** | Distribution reach is large, but dependency/API churn and framework-specific maintenance erase the thin-client advantage. |
| GMI | 19 | `jev-mock`: offline deterministic test harness | **780** | Essential for trustworthy adoption and already demanded by the testing policy, but it is a `jev-kit` feature rather than a top-level product. |
| GMI | 20 | `jev-scaffold`: pattern code generator | **590** | Templates reduce setup, but generated policy code creates tech debt and stale examples unless the kit is already stable. |
| GMI | 21 | `jev-shield`: universal size/schema preflight | **860** | Directly prevents the lane’s repeated costly defects and belongs in the sanctioned client, though it is infrastructure not a standalone consumer. |
| GMI | 22 | `jev-resilience`: circuit breaker/rate limiter | **640** | Production reliability matters, but the official SDK already owns retries and the proposal risks duplicating policy before organic load exists. |
| GMI | 23 | `jev-cascade`: automatic LLM fallback | **180** | Existing evidence says cascades were not useful, paid-comparator policy blocks the suggested path, and fallback can hide Jev failures. |
| GMI | 24 | `jev-cache`: deterministic response cache | **760** | Hash-keyed reuse can reduce cost/latency materially, but stale judgments and policy/model invalidation require careful provenance. |
| GMI | 25 | `jev-audit`: structured compliance receipt logger | **800** | Trust, cost, and model/version accounting are required for every real consumer; existing score-register pieces make this practical. |
| GMI | 26 | `jev-doc-aligner` | **640** | Concrete maintenance utility with later code/docs outcomes, but much of the first cut is deterministic signature matching. |
| GMI | 27 | `jev-rag-cleaner` | **700** | Relevant measured RAG/injection use with clear outcomes, but crowded market and state-size/cost make scope discipline essential. |
| GMI | 28 | `jev-pr-summary-verifier` | **620** | Easy distribution through GitHub Actions and useful to humans, but PR truth labels are delayed and overlap diff review. |
| GMI | 29 | `jev-bug-dedup` | **590** | Maintainer value is real, but retrieval/embeddings are the incumbent and duplicate detection needs a large outcome corpus. |
| GMI | 30 | `jev-agent-arbiter` | **560** | Multi-agent disagreement is visible, but subjective patch scoring invites self-grading and weakens accountability. |

## Detailed evaluation

### Claude / pane 1 ideas

#### CC-1 — `jev-trial`

This is the best reliability architecture proposed, not the best immediate user feature. The
repository has a repeated, concrete defect family: state-size omissions, wrong field names, arm
flags with no effect, leaked graders, stale labels, and bars that arithmetic could reject. A shared
runner that owns preflight, imports, hashes, resume, receipts, and the e-process would turn those
failures into refusals before spend. That is genuinely accretive if it replaces three existing
runners rather than becoming a fifth harness.

The counterargument is real: Joshua explicitly wants to leave repeated testing. A kernel can be
process-porn with a nicer API. The 500-line target is plausible only if the four hooks are strict,
the scorer is the benchmark’s own scorer, and the first consumers are MiniWoB plus the next real
omp shadow run. I would not build the Node twin up front; the Python-first proposal is right. Score
790: high infrastructure value, but its value is conditional on immediate use and deletion of
parallel runners.

#### CC-2 — shadow mode in the fleet hot path

This directly answers the consumer gap. The existing post-hook already observes real bash calls,
redacts secret-shaped commands, records probabilities and spend, and never blocks. Shadow mode is
the correct adoption posture because the measured gate has a promising criteria arm but not enough
real-label evidence for enforcement. The feedback loop (revert, dcg deny, undo, human review) is
more valuable than another hand-authored 100-row corpus.

The hard parts are not the API call: labels arrive late, false alarms have asymmetric cost, and
normal bash is only one of omp’s surfaces. It must keep the explicit blind spot for browser/
computer prelude calls and cannot claim “fleet safety” from bash rows alone. The one-second
fail-open path also needs cost/session accounting. Score 930 because the consumer exists now,
the action is reversible, and the next evidence is generated by actual use.

#### CC-3 — published `jev-kit`

This is the strongest stranger-facing proposal in both files. The current client already contains
the right boring design: official SDK only, lazy SDK import, injectable transport, explicit
`unconfigured`/`sdk-missing`/`http`/`no-answers`/`billing-hold`, typed Choice/Score/Noul, and no
coercion of malformed answers. Packaging those facts is useful; reproducing them in every demo is
not.

The risk is calling two packages, five verbs, a CLI, a kernel, and a hook a “thin kit.” I would
start with the TS core plus mock asker, shield, doctor, and one recipe; Python parity follows an
actual Python consumer. It needs a clean API and a stranger test, not a new internal framework.
Score 900: direct benefit for strangers and internal tools, high reuse, and an implementation
that can be extracted rather than invented.

#### CC-4 — doctor/robot/install

This is less glamorous but unusually correct. The README and scripts currently make agents infer
key state, SDK installation, model pins, hook discovery, and lane semantics. Stable robot JSON is
how `br`, `bv`, `ubs`, and omp tooling are actually driven. A doctor would make the first failure
actionable and allow `quickstart`, CI, and agents to consume one readiness contract.

The reason it is not higher is that it is an enabler. A doctor without a consumer is another
instrument inventory row. One-line installers also introduce supply-chain and versioning risk;
prefer `npx`/`uvx` or a checked-out command before a curl installer. Score 820: cheap, broad, and
highly accretive when shipped with `jev-kit`, not alone.

#### CC-5 — Jev as fast judge inside a planner

The mechanism is sound: Jev’s Choice distribution is more naturally a prior/pruner/critic than a
sole policy. The local findings support this shape: symbolic game tasks have strong scripted floors,
while Jev can rank options and supply calibrated uncertainty. A deterministic executor plus Jev
selection is safer than asking Jev to perform every action.

The cost is the planner itself. Jericho, Pokémon, and browser loops need environment adapters,
replay semantics, action budgets, and external baselines. The idea becomes excellent when attached
to one existing task with a checker; it becomes a research program when phrased as “games.” Score
650: intellectually right and potentially compelling, but lower immediate consumer probability.

### Gemini ideas: Category A — omp fleet

#### GMI-1 — active safety interceptor

The utility is obvious, but the proposed enforcement is too aggressive for the evidence. The
current gate has measured recall/false-alarm tradeoffs, and the real in-place-edit slice is weak;
ordinary tool hooks also do not see eval-prelude computer/browser actions. “Fail open” on timeout
means the safety claim is not a hard safety guarantee, while “block at 0.80” risks blocking safe
work without a reliable human-confirmation contract.

The good version is CC-2 shadow mode plus deterministic local guards, then a separately measured
pre-hook for one narrowly scoped destructive class. The GMI proposal jumps from advisory data to
active interception and assumes a confirmation UX that the hook contract does not provide. Score
540 rather than 800: the problem is important, but the proposed form is not yet trustworthy.

#### GMI-2 — live compactor

Context pressure is a real omp problem and the existing compaction hook is the obvious seam. The
proposal correctly preserves user/system content, errors, and diffs, and defaults unjudged entries
to keep. But the current compaction studies did not clear their bars; a failed compaction judge
can lose information long after the decision. Jev latency and token cost also happen inside the
same path where latency is already the problem.

The best implementation is first a shadow recommendation/report with human labels, then one
conservative deterministic preserve/drop rule supported by a measured seat. Wiring active Jev
dropping now is not justified. Score 430: high problem value, low current evidence, high downside.

#### GMI-3 — search/grep reranker

This has a credible Jev seat: existing BEIR/NevIR rerank results show semantic ranking can beat
lexical overlap where negation and relevance matter. Code search is a useful agent consumer. The
risk is the integration boundary: native grep/browser outputs are not uniformly visible to hooks,
and reranking every large result adds latency and may discard the exact symbol a code agent needs.

Start with an explicit `jev_rerank` tool or opt-in `jevify` command, not an invisible global
interceptor. Add a deterministic path/symbol preservation rule and use human “opened/used” outcomes
as labels. Score 650: promising reuse of a measured capability, but the seamless interception
claim is ahead of the contract.

#### GMI-4 — semantic commit/sibling-leak gate

Shared worktree staging accidents are real and were documented in AGENTS. A Jev question about
intent/diff mismatch could catch semantic omissions that path reservations cannot. However, the
proposal combines two problems: sibling ownership is better handled by reservations/index checks,
and commit-message alignment is subjective with weak labels. The existing kit-guard and commit
hook already block several mechanical hazards.

Make this advisory after staging, with a diff hash and explicit “unexpected path” evidence; do not
block commits on an unvalidated semantic score. Score 570: useful supplement, not a primary Jev
consumer.

#### GMI-5 — failure triage

A compact failure annotation could save agent turns, and nonzero tool results are frequent. But
most proposed classes are already well served by exit code, exception type, regex, and recent
history. Jev adds value only for ambiguous “harness bug vs test assertion vs environment” cases,
where labels are also hardest to obtain.

The safe first cut is a deterministic classifier with Jev only on an ambiguity bucket, logged for
human outcome. Score 610: practical ergonomics, moderate differentiation, no current proof that
Jev beats the rule.

#### GMI-6 — claim gate

The target defect is genuine: agents self-grade and call offline runs “verified.” Yet a post-turn
model judging the same model’s prose can become recursive self-grading, especially when no actual
command receipt is linked. A deterministic claim parser plus receipt lookup should do most of the
work; Jev could rank only ambiguous claim/evidence pairs.

Require a real evidence reference and make the output advisory. Score 520: good hygiene goal, but
weak independent oracle and high risk of performative warnings.

#### GMI-7 — log squeezer

Verbose logs consume context, but line grouping, compiler-error preservation, and head/tail limits
are mostly deterministic. A Jev information-density score could drop the exact line that matters,
and an opaque stream filter makes reproducing a bad context difficult.

A good product would be a deterministic compressor with Jev as an offline evaluator, not a model
in the hot path. Score 470: user benefit real, Jev justification weak.

#### GMI-8 — subagent router

Intent-based dispatch is a valid Choice use and could reduce manual fleet routing. The hard part is
not selecting a profile; it is keeping profiles, capabilities, and outcome labels current. A
majority or deterministic tagger may be enough, and a wrong route can waste a full turn.

Use Jev only among a small, explicit option set with a review/none option, then score routing
completion and rework. Score 570: plausible but not yet a high-leverage consumer.

#### GMI-9 — shared-worktree conflict watcher

The pain exists, but polling semantic diffs every 45 seconds is a poor first move. Agent Mail
reservations, exact staged-path checks, and the shared index already identify many conflicts without
API cost. Semantic conflict detection also needs a notion of intended edits that is unavailable
from raw diffs.

If built, make it event-triggered and advisory on overlapping paths only. Score 520: useful
infrastructure idea, but deterministic coordination should be exhausted first.

#### GMI-10 — flakiness tagger

Failure stability is valuable to agents, and a historical corpus can distinguish environment from
regression. But the proposal assumes that enough comparable history exists and that stack traces
carry the distinction. It also overlaps CI/test infrastructure, which can record retries and
versions deterministically.

A small Jev ambiguity bucket could be useful after a failure ledger exists. Score 580: practical
secondary feature, not a compelling first Jev product.

### Gemini ideas: Category B — stranger/tool packaging

#### GMI-11 — `jev-kit`

This is essentially the same core idea as CC-3 and deserves the same high score. The GMI version’s
friendly verbs and mock mode make the user story concrete. Its weak point is the claim that a missing
key should return mock structures automatically: that can launder “NOT_RUN” into a fake decision.
Mock mode must be explicit and typed, and the live result must say whether a request happened.

The right package is thin official-SDK glue plus shield/validator/doctor, not a second prompt
framework. Score 900.

#### GMI-12 — `jev` CLI

A CLI is an excellent agent/human boundary: exit codes, `--robot`, stdin JSONL, and local files are
more accessible than importing a library. `doctor`, `guard`, `route`, `check`, and `rerank` map to
real current code. It is also a good way to dogfood the client without needing omp.

The proposal should be a front end to `jev-kit`, not a separate implementation. Publishing a
binary/installer adds release/signing/version work; start with `npx`/`uvx` or repository-local
`jev`. Score 820: high practical value, slightly below the kit because it depends on the kit’s
stable contract.

#### GMI-13 — universal MCP server

MCP is a real adoption channel and prior `jev-mcp` exists. Guard, rerank, and verify are natural
model-callable tools, and stdio avoids hosting. But “universal” is marketing until packaging,
secret ownership, schema descriptions, keyless behavior, and actual install tests are solved. The
existing `.omp/mcp.json` does not yet expose Jev, so the current path is not plug-and-play.

Ship only after the kit’s schemas stabilize and test with at least omp plus one stranger client.
Score 760: strong distribution route, but not the first product loop.

#### GMI-14 — framework middleware

Prompt-injection middleware is a real market problem and Jev is cheap enough to sit before an
expensive LLM. Yet security middleware needs application-specific threat labels, latency bounds,
privacy handling, and a strong false-positive contract. Existing gate evidence does not transfer
automatically from a news-injection corpus to arbitrary HTTP payloads.

A narrow adapter with advisory/review defaults is credible; broad Express/Next/FastAPI support is
not a pragmatic first cut. Score 690.

#### GMI-15 — GitHub semantic CI gate

A PR gate has a real consumer and a durable external event (merge/rework/revert), but the three
checks are not equally feasible. Secret scanning should remain deterministic; commit-message
alignment and docs drift lack stable labels. Blocking CI on a Jev probability is a poor default.

Make it advisory and narrow to one measurable boundary, such as changed exported signatures with
missing docs tests. Score 600: useful later, high false-positive/maintenance risk now.

#### GMI-16 — web playground

A visual playground could explain Choice/Score/Noul quickly, but this project’s existing problem
is not that a user cannot see a sample response; it is that live/key/configuration boundaries are
hard to understand. A new Next.js surface adds dependency and deployment complexity while the
README is already near a size ceiling.

A static page or CLI quickstart is better. Score 560: onboarding benefit, low need for a web app.

#### GMI-17 — evaluation/calibration CLI

This is useful to teams that already have labeled rows and directly exploits Jev’s probability
output. Foundation already has calibration receipts, so the proposal can become a reusable reader
rather than another scorer. It is still close to the meta-testing trap; it becomes product only when
used to set a real seat or release gate.

Require outside labels and report prevalence/constant baseline. Score 730: strong supporting tool,
not the central consumer.

#### GMI-18 — LangChain/LlamaIndex/Vercel integrations

Distribution reach is real, but these ecosystems churn and bring dependencies that conflict with
this project’s best property—small SDK-backed code. Each connector needs CI, version matrices, and
framework-specific failure semantics. A generic MCP/CLI can reach many users with less debt.

Score 500: possible later after a stable kit and actual user demand; weak first move.

#### GMI-19 — offline deterministic mock

This is almost mandatory for a trustworthy kit. Explicit mock mode, recorded distributions, and
hostile-answer cases let users test policy without network or billing. It also prevents a common
failure where “key missing” silently looks like a model answer.

As a standalone idea it is a component, not a product; it scores high because it makes every other
idea safer. Score 780.

#### GMI-20 — scaffold generator

Scaffolding recipes can reduce time-to-first-policy, but generated policy code ages badly and
creates exactly the copy/paste convention drift this lane has repeatedly suffered. A small set of
handwritten examples in the kit is more maintainable.

Generate only schemas/tests after the core stabilizes; do not generate opaque prompts. Score 590.

### Gemini ideas: Category C — reliability

#### GMI-21 — universal size/schema preflight

This is the strongest reliability subcomponent in the entire duel. It directly addresses measured
failures: over-limit OSWorld states, one-option Choices, malformed distributions, and missing
fields. It belongs in `work/jev-client`/`jev-kit`, not as a separate product. The client already
has strict response/failure taxonomy; adding shared preflight is high-confidence and high benefit.

The proposal’s 1.8 bytes/token heuristic should not be hardcoded as truth; use the committed
calibration band and classify FITS/NEAR/OVER. Score 860.

#### GMI-22 — circuit breaker/rate limiter

Production resilience matters, but the official SDK already supplies retry policy and this client
already has a 402 billing hold. An additional circuit breaker can be justified for many concurrent
callers, but the lane has not shown organic load at the proposed scale. Measure and reuse SDK
semantics before adding another transport policy.

Score 640: sensible later, but lower than preflight and not a current consumer.

#### GMI-23 — automatic LLM fallback

This is the weakest idea. The project’s own evidence says cascading to an LLM was not useful, and
paid comparator rules forbid the suggested Haiku/grok path. A free fallback can be useful in another
product, but the result would be a different experiment with provider drift, extra state exposure,
and unclear fail-safe semantics. Fallback also hides Jev outage/model failure instead of recording
it.

Score 180: only reconsider with a separately preregistered free comparator and a real availability
or quality bar.

#### GMI-24 — deterministic response cache

Hashing model/state/questions can remove duplicate cost and latency, especially for repeated diffs,
commands, or batch rows. The cache must include model id, policy version, question hash, and expiry;
otherwise a stale judgment becomes an invisible answer. Cache hits also need to be distinguishable
from live calls in receipts.

This is a good `jev-kit` capability after the score register exists. Score 760.

#### GMI-25 — audit receipt logger

Every serious consumer needs model id, input hash, policy version, latency, usage, and outcome
provenance. Existing score-register work demonstrates the right direction, and this is necessary
for trust and cost rather than decorative telemetry. It does not itself make Jev useful, however;
its reader must drive calibration, spend controls, or human review.

Score 800: high enabling value and low conceptual risk, with the caveat that receipts must not
contain raw sensitive state.

### Gemini ideas: Category D — applications

#### GMI-26 — documentation/signature aligner

Docs drift has an external code/docs outcome and is a reasonable Jev seat when deterministic
signature extraction cannot decide semantic equivalence. The first version should use AST/signature
checks and ask Jev only for ambiguous prose/examples. It could live as an advisory CI tool.

Useful, but narrower and less urgent than the core consumer loop. Score 640.

#### GMI-27 — RAG cleaner

This combines two measured seats—relevance and prompt-injection screening—with a clear pipeline
boundary. The current rerank and injection work gives it more evidence than many ideas. But the
user must define the corpus, prevalence, and external answer/contradiction labels; a generic
“cleaner” can silently drop contrary evidence or over-filter rare attacks.

A safe first cut preserves all dropped IDs and runs advisory/shadow. Score 700.

#### GMI-28 — PR description truthfulness checker

Useful to maintainers and easy to distribute through GitHub Actions, but evidence extraction and
claim matching are already weak areas (numeric claims are explicitly refused, and claim checks on
close reasons failed). The correct scope is qualitative claim-to-diff alignment with a nonblocking
advisory; broad “truthfulness” is overclaiming.

Score 620.

#### GMI-29 — issue deduplication

The problem is real at scale, but embeddings/retrieval are the incumbent and a duplicate label may
not be available until maintainers close issues. Jev’s typed output could help rank borderline cases,
but the proposal needs a history corpus and a human correction loop before it beats lexical search.

Score 590.

#### GMI-30 — multi-agent arbiter

A calibrated tie-breaker over patches could help a conductor, but it risks turning subjective
architectural preferences into an automated authority. “Minimal,” “correct,” and “idiomatic” need
independent outcomes, and the arbiter should never silently decide a merge. Use it as a reviewer
suggestion tied to tests/receipts, not a judge of humans.

Score 560.

## Overall comparison

Claude’s proposal is better aligned with the measured state of this repository: it starts with the
consumer and explicitly warns that `jev-trial` can become a framework. Gemini is strongest when it
turns existing client/tool pieces into packaging (`jev-kit`), a CLI, preflight, mock, and audit
receipts; it is weakest when it proposes active enforcement, automatic fallback, or broad semantic
claims before labels exist.

The highest-value combination is not “build all five top-five lists.” It is:

1. shadow consumer with outcome labels;
2. thin kit with preflight/mock/fail-safe;
3. kernel only where it replaces existing runners;
4. native omp batch/doctor path;
5. one powered trajectory selector or one genuinely labeled daily decision.

That combination is accretive because each layer has a named reader and a measurable next action.
The main anti-pattern to avoid is implementing all 30 as adapters before one organic user reads one
result.
