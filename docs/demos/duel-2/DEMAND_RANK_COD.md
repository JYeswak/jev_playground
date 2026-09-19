# Duel-2 demand ranking — COD lineage

Status: pre-registered demand judgment, not implementation.
Scope: demos 1–9 from `docs/demos/PLAN.md` §5.1–§5.9.
Forbidden source honored: I did **not** read `docs/demos/PLAN.md` §3b before committing this ranking.
Research date: 2026-09-18.

Demand is not supply readiness. A polished contract can still score low if the buyer has no reason
to download it. I scored four questions: stranger installability, benefit to AI usage broadly, a
named downloader and voiced pain, and a measurable before/after. Existing substitutes reduce
demand even when the underlying problem is real.

## Ranked table

| Rank | Demo | Demand | Who downloads it | What it replaces or displaces |
|---:|---|---:|---|---|
| 1 | Demo-9 review signal | **820** | Engineering teams running AI-generated changes through PR review who need calibrated triage before human approval. | A broad, prose-heavy AI review pass with no stable multidimensional signal. |
| 2 | Demo-2 admission screen | **780** | Agent-platform security owners protecting tool results, retrieved pages, and MCP data before the next model step. | Regex-only filters and post-hoc incident review at the context boundary. |
| 3 | Demo-5 fact ledger | **760** | Long-running agent builders whose tasks lose exact requirements when context compacts. | Lossy summaries as the only memory of exact constraints and tool facts. |
| 4 | Demo-1 route backtest | **540** | LLM gateway operators deciding whether a strong/weak router will save money on their own traffic. | A live routing rollout chosen from upstream benchmarks or intuition. |
| 5 | Demo-7 signals starter | **520** | ML practitioners with a labelled classification corpus who need calibrated uncertainty rather than a single LLM verdict. | Prompting “is this X?” and thresholding prose confidence. |
| 6 | Demo-4 foreman-lite | **480** | Engineering leads supervising autonomous coding workers who need an independent pre-close check. | Self-certified “done” messages and generic PR review praise. |
| 7 | Demo-3 claim-check gate | **360** | Teams with evidence-bearing release claims who want a commit-time contradiction check. | commitlint syntax checks plus manual receipt comparison. |
| 8 | Demo-6 claim-check notes | **320** | Documentation-heavy compliance teams with structured claims and evidence folders. | Manual citation review and general-purpose fact-checking workflows. |
| 9 | Demo-8 credential screen | **120** | No legitimate downloader for the literal credential-question design; local secret scanners already own the safe part. | It should be killed, not packaged. |

## Demand evidence and judgment per demo

### 1. Demo-9 — continuous review signal — 820

**Installability.** A local advisory hook can be installed beside ubs with one command and run on a
diff without a service. The demand score assumes the eventual contract keeps the default advisory,
no-key, no-daemon path; a vague “review signal” command without a diff input or receipt would not
clear this question.

**AI usage broadly.** AI coding has created more generated diffs than human reviewers can inspect.
A multidimensional signal—correctness, complexity, changeability, modularity, tests, security—is
useful across agents, PR bots, and local coding loops. It is broader than this lane's bead close
because the input is code and the output is a review triage signal, not a Jev-specific receipt.

**Who and voiced pain.** The downloader is an engineering team with many AI-authored PRs and a
review queue that cannot distinguish a serious regression from a noisy bot comment. CodeRabbit's
AI-adoption reporting explicitly treats AI code review as a major adoption surface, and Qodo's
2026 review comparison markets context depth and policy enforcement: these are demand signals, not
proof that this particular Jev product wins (`https://www.coderabbit.ai/blog/ai-adoption-how-developers-are-using-ai-dev-tools`,
`https://www.qodo.ai/blog/best-automated-code-review-tools-2026/`).

**Measurable change and substitutes.** Before: review latency, human escalation rate, and ubs-only
findings over a fixed diff window. After: signal dimensions, abstentions, agreement with human
review, and false-positive rate; the command must emit both runs. CodeRabbit, Qodo, Greptile,
GitHub Copilot review, and Sonar already own general AI/static review, so the demand is for a
calibrated advisory layer that proves it is complementary, not another comment bot. The measured
baseline in this lane—ubs over four TS files, 1 critical/6 warnings/27 info with a firing eval
positive control—is a useful local starting point, not broad market evidence.

### 2. Demo-2 — admission screen — 780

**Installability.** A project-scoped hook and CLI are stranger-installable if the profile path is
verified and the initial mode is shadow. The credential branch must remain local-redaction-only;
shipping raw secrets to a classifier would destroy demand on security grounds.

**AI usage broadly.** Prompt injection through tool results, database rows, retrieved documents,
MCP instructions, and webpages is a cross-framework security problem. Google MCP Toolbox issue
[#2844](https://github.com/googleapis/mcp-toolbox/issues/2844), Microsoft AutoGen issue
[#6017](https://github.com/microsoft/autogen/issues/6017), and Agent-S issue
[#199](https://github.com/simular-ai/Agent-S/issues/199) all describe untrusted context reaching
agent decisions or execution. Microsoft Prompt Shields and Lakera/Check Point Guard both document
screening user prompts and documents before the next model step (`https://learn.microsoft.com/en-us/shows/responsible-ai/azure-ai-content-safety-prompt-shields`,
`https://docs.lakera.ai/docs/api/screening-roles`).

**Who and voiced pain.** The downloader is the security owner of an MCP or agent platform whose
tool results include third-party text and privileged tools; their pain is that a legitimate page
can carry an instruction that changes the next action. The external issues are direct demand
voices, not benchmark transcription.

**Measurable change and substitutes.** Before: injected-doc detection rate, false positives,
cost per screened read, and unsafe admissions. After: held-out detection and page-realness rates
in shadow mode, with no blocking until the false-positive rate is known. Lakera Guard and Azure
Prompt Shields are strong existing substitutes, so this demo only deserves 780 if its typed
Choice/Noul policy, local secret boundary, and omp integration solve a specific open workflow;
“Jev detects injection” alone is not demand.

### 3. Demo-5 — fact ledger — 760

**Installability.** A deterministic extractor plus Choice/Noul verifier can run offline from a
transcript and slots. The stranger needs a fixture with multiple turns, not the old one-turn
interpretation; the corrected marker-pair reader is essential to demand.

**AI usage broadly.** Context compaction and memory loss are widely voiced agent failures. OpenClaw
issue [#5429](https://github.com/openclaw/openclaw/issues/5429) reports losing days of agent context
after silent compaction; Hermes issues [#17251](https://github.com/NousResearch/hermes-agent/issues/17251)
and [#64315](https://github.com/NousResearch/hermes-agent/issues/64315) describe memory being
demoted or flushed incorrectly. Exact, recoverable facts are a general agent need, not just this
lane's ports and paths.

**Who and voiced pain.** The downloader is a developer of a long-running coding or research agent
whose exact requirements disappear when context is compacted; they want a small authoritative
ledger instead of trusting a generated summary. Anthropic's compaction and memory tools already
acknowledge the need for durable state (`https://platform.claude.com/docs/en/build-with-claude/compaction`,
`https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool`).

**Measurable change and substitutes.** Before: exact-answer recall after compaction and bytes
retained. After: byte-identity quote recall, source-span validity, ledger bytes, and withheld
facts. Context Ledger (`https://github.com/wiztek-llc/context-ledger`) and Hindsight
(`https://aclanthology.org/2026.acl-demo.27.pdf`) are serious substitutes; Anthropic's native
memory is a platform substitute. Demand remains because none of these proves the exact
Choice→Noul source-span contract on an omp-shaped transcript, but a standalone demo must show a
portable advantage rather than just repeat “summaries lose facts.”

### 4. Demo-1 — routing backtest — 540

**Installability.** The completed demo now installs cleanly and the shipped fixture gives 6 turns
with a cheap/frontier split. That is a demand prerequisite, not demand itself.

**AI usage broadly.** Cost-aware model routing is a large AI-infrastructure problem, but the
backtest is an evaluation instrument, not a router. RouteLLM already routes strong/weak models and
ships an OpenAI-compatible server (`https://github.com/lm-sys/RouteLLM`); LiteLLM documents routing,
cost-based selection, custom pricing, and durable spend tracking (`https://docs.litellm.ai/docs/routing`,
`https://docs.litellm.ai/docs/proxy/cost_tracking`).

**Who and voiced pain.** The downloader is an LLM gateway operator deciding whether to turn on
routing and needing a replay-based cost/quality estimate before exposing production traffic. LiteLLM
issue [#38064](https://github.com/BerriAI/litellm/issues/38064) voices a concrete demand pain:
cost-based routing can ignore cache-read price and select a provider by list order, with a reported
roughly 10× cost difference. That supports price-audit demand, not necessarily this CLI's adoption.

**Measurable change and substitutes.** Before: no per-turn counterfactual, only upstream router
claims or intuition. After: parsed/unparsed denominator, actual spend, counterfactual spend, price
metadata, and deterministic hard/all-trivial controls. The strongest substitutes already own
routing and cost accounting, so this demo is valuable only as a neutral preflight/backtest for
traffic the operator owns. Its lane-local transcript adapter and heuristic are not enough for a
broad demand claim; the current $0.0034 scenario estimate is not a market proof.

### 5. Demo-7 — signals starter — 520

**Installability.** A CSV-to-fit/report/refuse template is straightforward to install, especially
with scikit-learn's existing calibration APIs (`https://scikit-learn.org/stable/modules/generated/sklearn.calibration.CalibratedClassifierCV`).
The hard part is not installation; it is arriving with labels and a corpus large enough to make the
report useful.

**AI usage broadly.** Calibrated selective classification matters for security triage, support,
moderation, and agent routing. The ASK benchmark (`https://github.com/megansquire/ask-benchmark`)
shows that scam-signal behavior is a real evaluation area, but it does not prove users want this
specific starter over mature ML tooling.

**Who and voiced pain.** The downloader is an ML/evaluation engineer with a labelled corpus who
needs an abstention/calibration report for an LLM-derived classifier; teams without labels have no
first value. The external benchmark voices the task, while scikit-learn owns calibration mechanics.

**Measurable change and substitutes.** Before: verdict-only accuracy and uncalibrated confidence.
After: held-out accuracy, AUROC, ECE/Brier, reliability bins, flip rates, and a fixed-rule floor.
The source benchmark's 62.6/95.1 numbers are not independently vendored in this tree, and the
lane's R11 requires a pinned generator or published distribution—not N≥50 by itself. The starter
has broad theoretical use but weak immediate demand because the buyer must already have labels and
can assemble the same pipeline from scikit-learn.

### 6. Demo-4 — foreman-lite — 480

**Installability.** `jev-bead-check <bead-id>` can be a stranger-installable wrapper around `br
show` and a diff baseline, but shared-worktree baselines and bead mutation make install only the
first hurdle.

**AI usage broadly.** Agentic coding needs independent completion checks, but the broad market is
already served by PR review and coding-agent products. CodeRabbit, Qodo, Greptile, and Copilot
Review all sell or provide review of AI-written code; CodeRabbit's adoption report explicitly
frames AI review as a product category (`https://www.coderabbit.ai/blog/ai-adoption-how-developers-are-using-ai-dev-tools`).

**Who and voiced pain.** The downloader is an engineering lead operating autonomous coding workers
who sees “done” messages with no evidence and wants a close gate. That is a real operator pain, but
this exact bead/acceptance integration is mainly valuable to lanes using Beads-like workflow.

**Measurable change and substitutes.** Before: close rate, follow-up bugs, and empty-diff closes.
After: independent verdict dimensions, human-needed referrals, and false-complete rate on a labelled
bead set. Existing code-review bots and CI checks are substitutes; the Jev value is typed evidence
mapping, not generic review. Demand stays below 700 until an external user, not this lane, voices
that exact close-path need.

### 7. Demo-3 — claim-check commit gate — 360

**Installability.** A commit-msg hook is easy to install, but a paid check on every commit must have
an explicit skip/fail-safe path. The artifact is operationally plausible, not automatically wanted.

**AI usage broadly.** Evidence-bearing AI claims are a real problem, but conventional commit
syntax is already owned by commitlint (`https://commitlint.js.org/`). The closer semantic tools
found in research include ClaimLint and backcheck, while CodeRabbit can review changed code; none
is a canonical commit-receipt verifier, but the gap is not an empty market.

**Who and voiced pain.** The downloader is a release engineer whose commit messages assert tests,
security fixes, or numeric outcomes that CI did not actually run. I found no strong external issue
showing broad demand for a Jev commit-message claim checker specifically; that absence costs this
score.

**Measurable change and substitutes.** Before: unsupported claim rate and artifact mismatches over
N commits. After: contradiction refusals, missing-artifact refusals, skip rate, false positives,
and claim coverage. commitlint handles form, while ClaimLint/backcheck are closer to evidence
checking; the proposed Jev hook must demonstrate a materially better receipt linkage or it is a
lane-local gate looking for a demo audience.

### 8. Demo-6 — claim-check notes form — 320

**Installability.** A notes-plus-evidence CLI can be installed, but “working point extraction” is
not a mechanism until the input is constrained to explicit blocks and citations. Arbitrary prose
makes the stranger path underspecified.

**AI usage broadly.** Evidence-backed writing is broadly useful in compliance and research, but
fact checking, citation management, and claim extraction already have many commercial and
open-source substitutes. The research found ClaimLint and backcheck as closer existing concepts;
this demo has no strong independent demand voice beyond the lane's own receipts and EVAL files.

**Who and voiced pain.** The downloader is a compliance or documentation team that must support
claims with an evidence folder and wants contradiction/insufficient-context outcomes. A general
researcher may use existing citation tools instead; the Beads/EVAL workflow is the lane-specific
part.

**Measurable change and substitutes.** Before: manual review time and unsupported-claim rate.
After: supported/contradicted/withheld counts, citation-span coverage, false-positive rate, and
review time. The direct demand is weaker than the commit gate and existing evidence tools; without
a named external user complaint or a differentiated source-span contract, this should remain a
follow-up, not a top demo.

### 9. Demo-8 — credential screen — 120, kill upheld

**Installability.** The literal demo is installable only as a security incident: asking Jev whether
content contains credential material sends the credential to the third party before the answer.
That is a fail, not an install hurdle.

**AI usage broadly.** The safe subset—local secret scanning before an injection screen—is already
owned by Gitleaks (`https://github.com/gitleaks/gitleaks`) and TruffleHog
(`https://github.com/trufflesecurity/trufflehog`), while the injection-only subset is Demo-2.
There is no demand for the unsafe combined branch.

**Who and voiced pain.** A security engineer wants secrets to stay local and tool-result injections
to be screened; they do not want a remote classifier to receive the secret. The existing scanners
and Demo-2 meet those separate needs more safely.

**Measurable change and substitutes.** Before: secret exposure and injection admissions. After:
local detector recall, zero raw-secret bytes sent, and injection false-positive rate. Because the
literal mechanism violates its own security objective, the kill is right. A future local-redact plus
injection-only design is a new Demo-2 contract, not a revival of Demo-8.

## Kill list

Kill Demo-8 outright. Kill Demo-6 as a standalone demo and keep it as a gated phase of Demo-3 only
if a real evidence-writing audience appears. Kill Demo-3's generic claim-check framing unless a
commit-message claim corpus shows a measurable mismatch rate; commitlint and broader evidence tools
already exist. Defer Demo-4 until a second team voices the completion-gate pain. Defer Demo-7 until
labels and a pinned generator/distribution exist. Demo-1 ships as a useful, bounded backtest, but
its broad demand remains conditional because RouteLLM and LiteLLM already own routing.

## Single pick

**Pick Demo-9 review signal.** It serves a large, currently growing AI-code-review population and
can be differentiated as an advisory, calibrated signal beside existing tools rather than another
comment bot. I would be wrong if CodeRabbit/Qodo users cannot identify a review decision that
scalar Jev dimensions improve, or if the false-positive rate is no better than existing review
noise; the first pilot must measure that before any block action.

## Research boundary and NO-CLAIM

Research covered official LiteLLM, RouteLLM, Lakera, Microsoft Prompt Shields, commitlint,
CodeRabbit/Qodo public material, Anthropic compaction/memory, Context Ledger, Hindsight,
scikit-learn calibration, Gitleaks, TruffleHog, and GitHub issue reports for prompt injection,
compaction loss, routing cost bugs, and AI review demand. I did not run installs, poll adoption
analytics, interview users, verify vendor pricing, or independently re-run the 18 unvendored Usage
Map repositories. The ranking is demand diligence, not market-size measurement or implementation
validation.
