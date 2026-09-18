# Duel-2 demand hunt — replacements for weak demos

Status: post-ranking research, still pre-implementation.
Input: committed `DEMAND_RANK_COD.md` (`e733de8`).
Forbidden source honored: I did **not** read `docs/demos/PLAN.md` §3b.
Research date: 2026-09-18.

## Purpose

The first pass scored six demos below 700 on demand: Demo-1 route backtest (540), Demo-7 signals
starter (520), Demo-4 foreman-lite (480), Demo-3 claim-check commit gate (360), Demo-6 claim-check
notes (320), and Demo-8 credential screen (120). This pass does not defend those scores and does not
stretch a weak concept with adjectives. It searches for a replacement with a larger downloader
population, an externally voiced pain, a measurable pre/post contract, and a Jev-native typed
judgment that is not just another prose-generation wrapper.

A candidate is provisionally **900+ demand** only when all five tests pass:

1. A stranger can install or run it from a shipped fixture without joining this lane's workflow.
2. The value applies to a broad AI workflow, not only Beads or an internal receipt convention.
3. A named external issue, benchmark, or maintained project voices the pain.
4. The output has a decisive before/after metric and an inspectable receipt/EVAL artifact.
5. Existing substitutes leave a specific gap; the candidate is not a renamed version of one.

The scores below are demand scores, not supply scores. A candidate can be desirable and still fail
its later contract, implementation, or product-viability gate.

## Hunt result

| Candidate | Demand | Replaces weak demo(s) | External demand signal | Jev-native wedge |
|---|---:|---|---|---|
| H1. Snapshot-bound completion evidence | **940** | 3, 4, 6 | OpenAI Codex issues #36718 and #41882 report unsupported “done” and correlated PASS signals. | Typed claim → exact revision → command/exit/output receipt; stale evidence becomes unknown. |
| H2. Pre-action abstention evaluator | **935** | 4, 7 | GitHub Spec Kit #4290, AgentAbstain, AbstentionBench, and AbstainQA all treat overconfident action as a production problem. | `pass / clarify / gather / abstain / escalate / block` Choice/Noul result before an irreversible call. |
| H3. Cache-aware routing price-drift auditor | **925** | 1 | LiteLLM #38064 and Hugging Face tau #574 describe wrong route-specific/cache-token pricing. | Deterministic price evidence plus typed request-difficulty choice; no live router claim. |
| H4. Tool-result admission replay benchmark | **920** | 2, 8 | Google MCP Toolbox #2844, AutoGen #6017, Agent-S #199, and MCP #3213 document untrusted tool/web content crossing agent boundaries. | Typed admission decision with action scope, provenance, and shadow/block replay metrics. |
| H5. Compaction-boundary integrity benchmark | **915** | strengthens 5; also replaces the low-demand “notes” framing in 6 | OpenClaw #3560, OpenClaw #5429, ZeroClaw #2381, and Hermes #64315 report facts lost at compaction. | Source-span fact set compared before/after compaction; detects ordering and flush-loss regressions. |

Five candidates clear the 900 target. H1–H2 cover the weak claim-check/foreman/signals cluster;
H3 covers the route backtest; H4 safely replaces the credential-screen branch while sharpening
admission demand; H5 keeps the fact-loss problem but turns a ledger product into a portable regression
benchmark. None revives Demo-8's unsafe “send the credential to the classifier” mechanism.

## H1 — snapshot-bound completion evidence — 940

**Installable.** The stranger-facing product is a local CLI that reads an agent transcript, a
repository revision, and machine-observable command receipts; its first fixture can be a JSONL
transcript with deliberate claims such as “all tests pass,” a focused test result, a later file
mutation, and an unavailable command. A one-command run emits NDJSON plus a human report, so it can
be evaluated without a service, a model key, or a Jev-specific bead. The contract must refuse to
call a claim verified when its evidence is from a different revision or when the producer exit code
is absent.

**Whole-AI benefit.** This is useful for coding agents, release bots, CI copilots, infrastructure
agents, and any model that reports a state-changing task as complete. OpenAI Codex issue
[#36718](https://github.com/openai/codex/issues/36718) asks for evidence-backed completion reports
because agents say “implemented,” “fixed,” or “all tests pass” without proving the relevant checks;
Codex issue [#41882](https://github.com/openai/codex/issues/41882) describes multiple PASS signals
that still missed a shared writer. The general benefit is replacing self-attestation with
requirement-specific, snapshot-bound evidence.

**Named downloader and pain.** The buyer is an engineering platform owner running many coding
agents who cannot trust a green closeout message and must manually reopen the transcript. The
external pain is unusually direct: #36718 calls out focused-subset tests misreported as all tests,
missing exit status, stale evidence after later changes, and unresolved uncertainty. Existing
projects `backcheck` (`https://github.com/VectorInstitute/backcheck`) and `evigate`
(`https://github.com/shiki-yusuke/evigate`) validate parts of this problem, so this candidate is
not claiming an empty market; it wins demand by combining revision binding, producer truth, and a
portable typed receipt rather than another natural-language review.

**Before/after, receipt, and EVAL.** Before: unsupported completion-claim rate, stale-receipt rate,
manual review minutes, and false “all tests pass” claims in a frozen transcript set. After: claim
classification (`proven`, `contradicted`, `unknown`, `stale`), exact-revision coverage, false
verification rate, and review time; every classification carries command, exit code, output hash,
and revision. The planned artifact is `runs/completion-evidence.json` plus `EVAL.md` rows for
fresh evidence, wrong revision, nonzero producer, filtered-output trap, missing command, and
post-receipt mutation. Jev's typed `Choice`/`Noul` can adjudicate claim-to-evidence relation, but
must never replace deterministic command/exit/revision checks.

**Why 940 instead of a renamed Demo-3.** Demo-3 starts from a commit message and is narrow enough
that commitlint plus manual receipt comparison can satisfy many users. H1 starts from the broader,
externally voiced failure “agent completion is not evidence,” covers a session or CI artifact, and
makes commit messages one adapter. It replaces Demo-3, the Beads-specific part of Demo-4, and the
notes-only Demo-6, while explicitly retaining backcheck/evigate as substitutes to benchmark against.

## H2 — pre-action abstention evaluator — 935

**Installable.** The stranger installs a local replay CLI with paired fixtures: one task where the
agent should act and a minimally changed task where it should clarify, gather evidence, abstain, or
escalate. A runner feeds the proposed action, evidence references, risk level, and model confidence
to a typed evaluator and emits a decision before any side effect; the fixture uses a fake sink only
to prove the gate ordering. No vendor gateway or live account is needed for the first receipt.

**Whole-AI benefit.** A model's verbal confidence should not independently authorize a tool call,
code change, memory write, payment, or other irreversible action. GitHub Spec Kit issue
[#4290](https://github.com/github/spec-kit/issues/4290) proposes an evaluator contract that
preserves evidence, provenance, uncertainty, and recovery and returns outcomes such as pass, warn,
clarify, iterate, and block. AgentAbstain
(`https://github.com/AntiQuality/agentabstain`), AbstentionBench
(`https://github.com/facebookresearch/AbstentionBench`), and AbstainQA
(`https://github.com/BunsenFeng/AbstainQA`) provide independent demand signals: agents are still
overconfident, and post-hoc abstention after an irreversible action is too late.

**Named downloader and pain.** The downloader is the owner of an agent that can mutate durable
state or call privileged tools; their pain is risk-weighted false action, not a slightly wrong final
answer. The external issue's acceptance language explicitly asks for deterministic checks before
probabilistic review, independent verification for high-risk decisions, and safe behavior when the
evaluator is unavailable. Existing abstention benchmarks measure models and existing guardrails
screen content, but neither alone is a portable pre-action controller with an auditable decision
and sink-order proof.

**Before/after, receipt, and EVAL.** Before: irreversible-action rate on paired should-act/
should-abstain cases, false-action rate, post-hoc abstention rate, ECE, Brier score, and human
escalation burden. After: selective accuracy at coverage levels, abstention precision/recall,
risk-weighted utility, zero action-before-gate violations, calibration version, and a reason for
every pass/clarify/abstain/block. The planned receipt is `runs/abstention-gate.json`; `EVAL.md`
will include missing evidence, stale evidence, invalid evaluator output, unavailable evaluator,
should-act, minimally perturbed should-abstain, and high-risk independent-review cases. `Choice`
chooses the structured outcome and `Noul` checks whether the proposed action is licensed by the
provided evidence; the side-effect sink remains deterministic.

**Why 935 instead of Demo-7 or Demo-4.** Demo-7 asks for a labelled signals starter and therefore
loses buyers without a corpus; H2 can start with paired safety fixtures and then accept a customer's
labelled calibration set. Demo-4 judges whether work is complete after the fact; H2 prevents an
unsafe action before it happens. It overlaps with Demo-2 only when injection is the reason to
abstain; its independent demand is uncertainty and action authorization.

## H3 — cache-aware routing price-drift auditor — 925

**Installable.** The stranger supplies provider/model price manifests, usage logs, cache-read/write
fields, and a replay fixture; the CLI emits route-level effective cost, unknown-price refusals,
and a drift report. It never claims to be a live router and never sends customer prompts to a
provider. A clean install plus a deterministic fixture can prove the central value before any
production integration.

**Whole-AI benefit.** Operators already route traffic across models and providers, but logical-model
pricing can diverge from the actual backend and cached-token pricing can dominate the result. LiteLLM
issue [#38064](https://github.com/BerriAI/litellm/issues/38064) reports cost-based routing that
ignores cache-read pricing and list-order behavior with a roughly 10× example; Hugging Face tau
issue [#574](https://github.com/huggingface/tau/issues/574) reports route-specific cached-token
pricing keyed incorrectly. LiteLLM documents routing and cost tracking (`https://docs.litellm.ai/docs/routing`,
`https://docs.litellm.ai/docs/proxy/cost_tracking`), so the demand is for an independent audit
that catches incorrect cost metadata before operators trust savings.

**Named downloader and pain.** The downloader is the LLM platform or FinOps operator who owns a
multi-provider bill and has to explain why a “cheap” route cost more after cache hits or a provider
change. The cited issues are direct implementer pain, not a generic cost aspiration. Existing
LiteLLM and RouteLLM (`https://github.com/lm-sys/RouteLLM`) can route and report, but a router is
not an independent assertion that its price table, cache semantics, and observed usage agree.

**Before/after, receipt, and EVAL.** Before: unknown-price rate, price-manifest drift, effective
cost error against a hand-computed oracle, and unexplained route-cost variance. After: caught drift,
cache-aware total, route/provider attribution, refused unverifiable rows, and estimated savings
with confidence intervals; actual and counterfactual must stay separate. The planned receipt is
`runs/price-drift-audit.json`, with EVAL fixtures for cache-read versus input tokens, provider
alias mismatch, missing custom price, list-order routing, stale manifest, and all-trivial/all-
unknown controls. `Choice` classifies request complexity for a counterfactual tier comparison;
deterministic arithmetic and provider metadata remain authoritative, preventing the old route
backtest from hiding a denominator or using an optimistic price.

**Why 925 instead of Demo-1.** Demo-1 asks “would a cheap/frontier route save money on this
transcript?” H3 asks the more urgent operator question “can I trust the price and cache metadata
behind the routing decision?” It benefits users already running LiteLLM/RouteLLM instead of asking
them to adopt another router, and its failure output is actionable even when no routing change is
recommended. H3 is therefore a replacement for the low-demand backtest, not a claim that Jev should
compete with mature routers.

## H4 — tool-result admission replay benchmark — 920

**Installable.** The stranger supplies a tool-result corpus containing ordinary data, hostile
instructions, forged policy text, and mixed-content pages plus a declared action policy. A local
replay runner evaluates the proposed next action in shadow mode, then optionally sends only a safe
synthetic action to a sink; it emits each result's source, decision, policy version, and whether a
block would have happened. The first fixture proves no raw secret crosses the classifier boundary.

**Whole-AI benefit.** Tool results, web pages, database rows, and MCP outputs are often treated as
instructions even when they are untrusted data. Google MCP Toolbox issue
[#2844](https://github.com/googleapis/mcp-toolbox/issues/2844) describes database content entering
LLM context as an injection path; Microsoft AutoGen issue
[#6017](https://github.com/microsoft/autogen/issues/6017) describes propagation across agents;
Agent-S issue [#199](https://github.com/simular-ai/Agent-S/issues/199) describes webpage content
reaching execution; MCP issue [#3213](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/3213)
adds protocol-level demand. This is a benchmark for the whole tool-using ecosystem, not only a
prompt classifier.

**Named downloader and pain.** The downloader is an agent-platform security engineer integrating
MCP, browser, database, or retrieval tools who needs to know whether a result can alter the next
privileged action. Lakera Guard (`https://docs.lakera.ai/docs/api/guard`) and Microsoft Prompt
Shields (`https://learn.microsoft.com/en-us/shows/responsible-ai/azure-ai-content-safety-prompt-shields`)
are strong prevention substitutes, but their hosted/vendor-specific controls do not give every
framework a replayable, vendor-neutral regression corpus with action-scope and false-positive
measurement.

**Before/after, receipt, and EVAL.** Before: unsafe admission rate, action escalation rate, false
positive rate on benign tool data, and detection latency/cost. After: held-out attack detection,
benign admission, safe-action preservation, block-before-side-effect rate, and provenance coverage;
shadow and enforce modes must be reported separately. The planned receipt is
`runs/tool-admission-replay.json`; EVAL includes database injection, webpage injection, forged
system text, cross-agent propagation, tool output with a secret-shaped value, benign imperative
language, and evaluator unavailable. `Noul` checks typed trust/action scope and `Choice` returns
admit, sanitize, hold, or block; neither receives raw secrets, and the synthetic sink proves
ordering.

**Why 920 instead of Demo-8 and why it is sharper than Demo-2.** Demo-8 is killed because a
credential screen that sends the credential to a classifier is self-defeating. H4 makes secret
non-disclosure a hard fixture and measures admission against action scope, while Demo-2's first
version is a more general admission screen. The replacement demand is the independent replay and
regression artifact that a security owner can run across frameworks even when a vendor guard is
already present.

## H5 — compaction-boundary integrity benchmark — 915

**Installable.** The stranger runs a local harness against a transcript and a pluggable compaction
adapter; a fixture puts an exact requirement, decision, and constraint immediately before the
boundary and forces a flush/truncate sequence. The harness compares the pre-boundary fact set with
post-boundary retrieval and reports ordering, provenance, and loss, without requiring a particular
agent vendor. The fixture can be deterministic before any model judge is added.

**Whole-AI benefit.** OpenClaw issue [#3560](https://github.com/openclaw/openclaw/issues/3560)
reports memory flush occurring after truncation, when the facts are already unavailable; ZeroClaw
issue [#2381](https://github.com/zeroclaw-labs/zeroclaw/issues/2381) proposes a pre-compaction flush;
Hermes issue [#64315](https://github.com/NousResearch/hermes-agent/issues/64315) reports a pending
memory buffer being reset without flush; OpenClaw #5429 records silent compaction loss. The common
pain is a regression at a lifecycle boundary, not merely a desire for another notes database.

**Named downloader and pain.** The downloader is an agent-framework maintainer or platform team
whose long sessions silently lose constraints at compaction and then produce plausible but wrong
work. Anthropic's compaction and memory documentation (`https://platform.claude.com/docs/en/build-with-claude/compaction`,
`https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool`) proves the feature is
important, while Context Ledger (`https://github.com/wiztek-llc/context-ledger`) and Hindsight
(`https://aclanthology.org/2026.acl-demo.27.pdf`) are substitutes for storage. H5 is not another
storage product: it is a portable regression oracle that can test those stores and a custom adapter.

**Before/after, receipt, and EVAL.** Before: exact-fact recall, source-span loss, flush-before-
truncate ordering, duplicate-memory rate, and post-resume constraint violations. After: retained
fact precision/recall, provenance completeness, idempotent retries, bounded failure reporting, and
zero facts lost from the discarded span on the fixture. The planned receipt is
`runs/compaction-integrity.json`; EVAL includes flush-after-truncate, dropped pending buffer,
wrong source range, duplicate retry, stale generation, missing commit acknowledgment, and clean
pre-save ordering. `Choice` compares candidate facts to the source with an explicit unknown state;
`Noul` checks that every retained fact has a valid provenance span and compaction generation.

**Why 915 despite Demo-5's 760.** Demo-5's fact ledger is useful but competes with native memory
and ledger products and asks the buyer to adopt its storage shape. H5 meets a different, higher-
urgency need: tell a maintainer whether their existing memory/compaction implementation loses facts
at the exact lifecycle boundary. It can test native Anthropic, OpenClaw, Hermes, or a local adapter,
so the market is the agent ecosystem rather than this lane's transcript format.

## Replacement map for every sub-700 demo

| Weak original | Replacement | Reason the new demand clears the old ceiling |
|---|---|---|
| Demo-1 route backtest (540) | H3 price-drift auditor | External cost/cache pricing bugs create an urgent audit need for users already running routers; no new router adoption is required. |
| Demo-7 signals starter (520) | H2 pre-action abstention evaluator | Paired safety cases work without a customer-labelled corpus, and the output controls behavior rather than merely reporting calibration. |
| Demo-4 foreman-lite (480) | H1 completion evidence or H2 abstention evaluator | H1 proves claims against exact receipts; H2 prevents risky action; both cover all-AI workflows beyond a Beads close. |
| Demo-3 claim-check commit gate (360) | H1 snapshot-bound completion evidence | The externally voiced problem is unsupported agent completion, not commit syntax; the commit hook becomes one adapter. |
| Demo-6 claim-check notes (320) | H1 evidence reports or H5 compaction integrity | H1 has a direct coding-agent demand voice; H5 turns notes into a cross-framework lifecycle oracle. |
| Demo-8 credential screen (120) | H4 tool-result admission replay | H4 keeps secrets local, measures cross-framework tool-result risk, and removes the unsafe raw-secret classifier path. |

The map intentionally gives some originals two options. A product team should not build all five
without a new demand test; the hunt establishes better candidates, not permission to skip selection.

## What would falsify the hunt

The 900+ scores fall if a stranger cannot run the fixture without a hidden Jev service, if the
external issue is merely a one-off maintainer complaint with no repeatable operator, if the metric
can be gamed by refusing every action, or if the candidate duplicates an existing product's core
promise without a measurable wedge. H1 must not mark a claim “proven” from a filtered log whose
producer failed; H2 must not count universal abstention as safe; H3 must not report counterfactual
savings with unknown prices; H4 must not send secret bytes to a judge; H5 must not infer retention
from a generated summary. These are acceptance failures, not future polish.

## Install/test/receipt plan

No candidate was implemented in this hunt. Each candidate's minimum build would be a single local
package with one shipped JSONL/JSON fixture, one exact install command, one machine-readable receipt,
and one `EVAL.md` row set. The first verification lane should run `install.sh`, then the fixture
command in a clean clone, then a mutation or negative-control command that must change the verdict.
For H1–H5, the receipt must include input hash, evaluator/policy version, source spans or revision,
producer exit status, counts, and explicit `unknown`/`unavailable` states; a pretty report without
those fields is not proof. A later implementation may choose one candidate only after comparing
its receipt against existing `docs/demos/USAGE-MAP.md` patterns and the corresponding contract
requirements.

## NO-CLAIM

This hunt does not claim that any candidate has paying users, adoption, benchmark superiority, or
production safety. External evidence is public issue/project/documentation evidence, not an
interview or a controlled market study. I did not install backcheck, evigate, AgentAbstain,
AbstentionBench, RouteLLM, LiteLLM, Context Ledger, Hindsight, Lakera, or Prompt Shields; I did not
run a live provider, browser, MCP, or credential path; and no candidate has an implementation or
passing EVAL receipt yet. Scores are a demand-prioritization hypothesis to be cross-scored against
the other pane and then tested with a real artifact.
