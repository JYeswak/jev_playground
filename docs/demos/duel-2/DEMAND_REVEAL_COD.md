# Duel-2 demand reveal — preregistered bar versus evidence

Status: final demand reveal for the eight preregistered verdicts.
Pinned source read only after COD ranking, hunt, and cross-score commits: `f06a1e1:docs/demos/PLAN.md` §3b.
COD ranking: `e733de8`. Hunt: `c33cd3c`. Cross-score: `b8d0be9`.
Read state: `read_3b=yes` for this artifact and its callbacks.

## The revealed bar

The pinned §3b demand bar asks four questions before a demo is built:

1. **Installable by a stranger?** Clean clone, one command, green result, no author-home path, and
   committed fixtures by default.
2. **Benefit to AI usage as a whole?** A lane-local tool belongs in scripts, not demos.
3. **Who downloads it, and why?** Name the person and their pain.
4. **Measurably improves what?** State before value, after value, and the command producing both.

The pinned retroactive table preregistered eight demand verdicts: Demo-7 PASS, Demo-2 PASS, Demo-5
PASS, Demo-3 PASS, Demo-4 PASS narrowed, Demo-9 WEAK/hold, Demo-6 REJECT unless Demo-3 proves
the seam, and Demo-1 FAILS the demand bar. Demo-8 was separately killed earlier on safety and is
reported as a safety confirmation below, not counted as one of the eight.

## Verdict table

| Demo | Pinned verdict | COD evidence grade | Reveal |
|---|---|---|---|
| Demo-7 signals starter | PASS; highest of set | Partially supported; broad method is real, headline transfer is not yet evidenced | **PASS, contract-conditional** |
| Demo-2 admission screen | PASS | Supported by direct cross-framework injection reports; generic screen is substitute-heavy | **PASS, wedge required** |
| Demo-5 fact ledger | PASS | Supported by multiple compaction-loss issues; ledger storage competes with native substitutes | **PASS, oracle preferred** |
| Demo-3 claim-check gate | PASS | Supported for evidence-bearing agent claims; commit surface is narrower than the underlying pain | **PASS, adapter not product** |
| Demo-4 foreman-lite | PASS, narrowed | Strongly supported by false-completion reports; `br` coupling narrows stranger demand | **PASS, narrowed** |
| Demo-9 review signal | WEAK — hold | Correctly held; market category is large but differentiation and ubs gap are unproven | **HOLD** |
| Demo-6 claim-check notes | REJECT unless Demo-3 proves seam | Confirmed redundant; no independent buyer or capability boundary | **REJECT** |
| Demo-1 route backtest | FAILS demand bar | Confirmed lane-local and displaced by mature routers; H3 price-drift audit is the replacement | **FAIL** |

**Reveal outcome: 7/8 pinned verdict directions are accepted exactly or with the stated condition;
Demo-9 remains held; Demo-1 remains failed.** The qualification matters: a PASS at the demand bar
is not an implementation pass, model-quality pass, security approval, or adoption result.

## Demo-7 — signals starter — PASS, contract-conditional

**Pinned claim.** The bar calls this the highest-demand demo because its zero-label classification
method transfers beyond Jev and the stated 62.6% → 95.1% result is a compelling improvement.

**Evidence grade.** The transfer direction is credible: calibration and signal models are useful
across classification tasks, and scikit-learn provides a maintained calibration API
(`https://scikit-learn.org/stable/modules/generated/sklearn.calibration.CalibratedClassifierCV`).
AbstentionBench (`https://github.com/facebookresearch/AbstentionBench`) and AgentAbstain
(`https://github.com/AntiQuality/agentabstain`) show adjacent demand for abstention and reliable
agent decisions. However, the pinned headline numbers are not independently vendored in the local
artifact, and a general user still needs a pinned generator/distribution or labels before ECE,
AUROC, and Brier score mean what the report claims.

**Four-bar grade.** Installability is yes if the template ships its synthetic fixture and one
command. Whole-AI benefit is yes, but only if the contract states the method for arbitrary
zero-label classification rather than Jev-only signals. The downloader is an ML practitioner who
needs a baseline and calibrated decision report but lacks a labelled corpus; the contract must
name that buyer rather than “anyone.” Measurement is before verdict-only accuracy and confidence,
after selective accuracy/ECE/Brier/reliability and abstention behavior, with a pinned distribution.

**Reveal.** PASS, contract-conditional. The pinned ordering is right relative to the original nine,
but the exact 62.6 → 95.1 claim is a hypothesis until the source generator/distribution and
negative controls are committed. This agrees with COD's lower 520/560 demand score only in rejecting
an adoption claim; it does not reject the portable method. H2 pre-action abstention is the stronger
replacement shape if the product must create value without customer labels.

## Demo-2 — admission screen — PASS, wedge required

**Pinned claim.** Prompt injection is a universal live agent attack class, and anyone whose agent
reads web or tool output can want a hook with a 0.99 upstream witness.

**Evidence grade.** Direct public failures support the problem: Google MCP Toolbox issue
[#2844](https://github.com/googleapis/mcp-toolbox/issues/2844) describes untrusted database
content entering model context; AutoGen issue [#6017](https://github.com/microsoft/autogen/issues/6017)
describes propagation across agents; Agent-S issue
[#199](https://github.com/simular-ai/Agent-S/issues/199) describes webpage content reaching
execution; MCP issue [#3213](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/3213)
adds protocol-level concern. Lakera (`https://docs.lakera.ai/docs/api/screening-roles`) and
Microsoft Prompt Shields (`https://learn.microsoft.com/en-us/shows/responsible-ai/azure-ai-content-safety-prompt-shields`)
show a mature substitute category, so “prompt injection detector” alone is not a demand bar pass
for a new demo.

**Four-bar grade.** Installability is yes only in shadow mode with committed mixed benign/hostile
fixtures and no hidden service. Whole-AI benefit is yes because the boundary spans MCP, browser,
database, retrieval, and multi-agent workflows. The downloader is an agent-platform security owner
who must know whether a tool result can alter a privileged action; the contract must state that
person and not target generic model users. Measurement is shadow detection, benign admission, false
positive rate, action-scope escalation, and block-before-side-effect rate, with an evaluator-
unavailable case.

**Reveal.** PASS, wedge required. The pinned verdict is directionally correct and direct issues
outweigh MU's 450, but COD's first 780 was too high for a generic screen. H4 tool-result admission
replay is the stronger demand-shaped version: vendor-neutral regression corpus, typed action scope,
shadow/enforce separation, and a hard zero-raw-secret fixture. The 0.99 witness is an input to an
EVAL, not a universal performance claim.

## Demo-5 — fact ledger — PASS, oracle preferred

**Pinned claim.** Compaction that provably keeps answer-bearing facts benefits every long-running
agent; anyone hitting context limits could download it.

**Evidence grade.** This has direct lifecycle failure reports. OpenClaw issue
[#3560](https://github.com/openclaw/openclaw/issues/3560) reports flush after truncation; ZeroClaw
issue [#2381](https://github.com/zeroclaw-labs/zeroclaw/issues/2381) proposes a pre-compaction
flush; Hermes issue [#64315](https://github.com/NousResearch/hermes-agent/issues/64315) reports a
pending-memory buffer reset without flush; OpenClaw #5429 reports silent compaction loss. Anthropic's
own compaction and memory documentation (`https://platform.claude.com/docs/en/build-with-claude/compaction`,
`https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool`) confirms the lifecycle
is important. Context Ledger (`https://github.com/wiztek-llc/context-ledger`) and Hindsight
(`https://aclanthology.org/2026.acl-demo.27.pdf`) are substitutes, not evidence that the ledger
wins.

**Four-bar grade.** Installability is yes if the CLI has an adapter-independent fixture and one
clean-clone command. Whole-AI benefit is yes for long-running coding, research, and operations
agents. The downloader is an agent-framework maintainer or platform owner who needs to know whether
facts survive compaction, not merely a user who would like more memory. Measurement is exact-fact
recall, source-span validity, lost-fact count, duplicate retry rate, and byte cost before versus
after; a generated summary is not a retention measurement.

**Reveal.** PASS, oracle preferred. The pinned verdict survives, but the product demand is stronger
for H5 compaction-boundary integrity benchmark than for another storage sidecar. COD and MU nearly
tied at 755; both were right to demand a source-span/negative-control oracle before treating the
ledger as a product. A late flush must fail the fixture, and an all-summary output must not count as
fact retention.

## Demo-3 — claim-check gate — PASS, adapter not product

**Pinned claim.** Agents fabricate numbers; a pre-commit gate can refuse a contradicted cited claim.
The bar records a local audit of 4 WRONG and 37 UNVERIFIABLE claims among 60.

**Evidence grade.** The local audit is strong evidence that this lane has the pain, but it is not a
market sample. OpenAI Codex issue [#36718](https://github.com/openai/codex/issues/36718) voices the
broader external failure: agents claim “all tests pass” without exact commands, output, exit status,
revision, or uncertainty. Codex #41882
(`https://github.com/openai/codex/issues/41882`) reports several correlated PASS signals while a
shared writer was missed. commitlint (`https://commitlint.js.org/`) is a strong format substitute;
backcheck (`https://github.com/VectorInstitute/backcheck`) and evigate
(`https://github.com/shiki-yusuke/evigate`) are closer evidence-verification substitutes.

**Four-bar grade.** Installability is yes for a local pre-commit fixture. Whole-AI benefit is yes
when the gate is reframed as evidence-backed completion, not only numeric commit messages. The
specific downloader is a release/CI operator whose agents emit claims tied to artifacts; a generic
repo with no checkable claims has no value. Measurement is unsupported/contradicted/unknown counts,
source-span and receipt coverage, false refusals, and review time, with producer exit status and
revision binding.

**Reveal.** PASS, adapter not product. The pinned bar correctly accepts the capability, but H1
snapshot-bound completion evidence is the demand-scale replacement and Demo-3 should be one adapter.
COD's 430 cross-score remains appropriate for the standalone commit hook; the 4/37/60 local result
justifies building a stronger evidence receipt, not pretending the hook has broad adoption.

## Demo-4 — foreman-lite — PASS, narrowed

**Pinned claim.** Independent completion judging kills self-certified close, but the buyer is an
agent-swarm operator with an issue tracker and the `br` coupling is narrower.

**Evidence grade.** The direct Codex issues above support the underlying false-completion demand. The
other pane's buyer description—Claude Code/Codex/Cursor user burned by a confident “done”—is more
credible than COD's original 480. CodeRabbit, Qodo, Greptile, and Copilot Review are adjacent
substitutes, but they do not automatically prove an exact revision-bound completion record or
independent post-change check.

**Four-bar grade.** Installability is only conditional on a generic task-spec interface rather than
requiring this lane's Beads path. Whole-AI benefit is yes after that generalization; a `br show`
wrapper is lane-local. The downloader is the engineering platform owner operating autonomous workers
who sees false closeouts. Measurement is false-complete rate, human rework, judge/human agreement,
stale evidence, and time saved, with an independent baseline.

**Reveal.** PASS, narrowed, exactly as preregistered. MU correctly ranked the raw pain at 800; COD's
cross-score now moves it to 820. H1 is the portable replacement, while the current foreman should
remain a narrow integration demo. A green `br` close alone is not evidence of whole-AI demand.

## Demo-9 — review signal — HOLD

**Pinned claim.** The market is unclear and the demo is unscored by any grader; hold until it finds
what ubs structurally cannot.

**Evidence grade.** Broad category demand is real: CodeRabbit's adoption material
(`https://www.coderabbit.ai/blog/ai-adoption-how-developers-are-using-ai-dev-tools`) and Qodo's
review comparison (`https://www.qodo.ai/blog/best-automated-code-review-tools-2026/`) show an active
AI-code-review market. MU's listed false-positive/style-noise/cost figures are not linked to primary
sources in the artifact, so they cannot establish a precise market cap. COD's local ubs baseline in
`docs/demos/USAGE-MAP.md` proves a candidate metric but not a structural blind spot.

**Four-bar grade.** Installability is plausible as a local advisory hook. Whole-AI benefit is
possible but crowded. The downloader is a tech lead who disabled noisy review bots yet still wants a
cheap, self-hosted first pass; that buyer is narrower than all PR teams. Measurement must show a ubs
blind spot, actionable finding precision/recall, false-positive reduction, reviewer hours, and
abstention—not six scalar scores with no decision consequence.

**Reveal.** HOLD, exactly as preregistered. COD's initial 820 overestimated displacement; MU's 550
underestimated category demand; the cross-score settles at 700 but the verdict remains hold because
there is no independent ubs-gap receipt. Do not build Demo-9 before a held-out diff corpus shows a
specific complementary win. The current H1/H2 candidates have stronger external failure reports
and less crowded demand wedges.

## Demo-6 — REJECT unless Demo-3 proves the seam

**Pinned claim.** Notes claim-checking is redundant given Demo-3 and has no downloader once Demo-3
exists.

**Evidence grade.** The claim is supported. A notes surface and a commit surface can share a
claim-to-evidence engine, but the artifact names no external issue or buyer who needs notes as a
separate product. Citation/fact-checking and the H1 evidence-report shape are existing alternatives;
COD and MU both score it near 330.

**Four-bar grade.** Installability is plausible but the input contract needs explicit claim blocks
and citation spans. Whole-AI benefit is not independently shown; “documentation teams” is a buyer
hypothesis without a voiced external pain. Measurement would be support/contradiction/unknown,
citation coverage, false refusal, and review time, but that is the same seam Demo-3 must prove.

**Reveal.** REJECT unless Demo-3 proves the seam, exactly as preregistered. Keep no separate
backlog item. If a real evidence-writing buyer appears, add an adapter to H1 or Demo-3 and re-run
this four-bar test; do not count a changed UI as a new capability.

## Demo-1 — FAILS the demand bar

**Pinned claim.** The shipped route backtest passes supply artifacts but gives a stranger little
information about their own routing: spend arithmetic over this lane's logs, a hand-written token
heuristic, zero Jev calls.

**Evidence grade.** The failure is confirmed. RouteLLM (`https://github.com/lm-sys/RouteLLM`) and
LiteLLM routing/cost tracking (`https://docs.litellm.ai/docs/routing`,
`https://docs.litellm.ai/docs/proxy/cost_tracking`) cover generic routing and cost operations.
LiteLLM issue [#38064](https://github.com/BerriAI/litellm/issues/38064) and Hugging Face tau issue
[#574](https://github.com/huggingface/tau/issues/574) establish a real price/cache audit gap, but
the current Demo-1 does not solve that gap; its six-turn fixture is a lane artifact.

**Four-bar grade.** Clean-clone install is yes, as the existing route receipt proves, but that is
only the first question. Whole-AI benefit is near zero for the current heuristic because a stranger
cannot trust it on their provider, price manifest, cache semantics, or traffic mix. The downloader
would be a gateway/FinOps operator, but the current command does not accept their logs and price
metadata as an authoritative audit input. Measurement separates actual and counterfactual spend in
the lane fixture, yet it does not measure route quality or price drift for a stranger.

**Reveal.** FAIL, exactly as preregistered. This is the decisive demand lesson: passing install,
tests, denominator, and receipt gates cannot rescue a lane-local answer. Do not delete the shipped
artifact; keep it as evidence of the failure and a regression fixture for H3. H3 must accept
provider/cache metadata, refuse unknown prices, and emit a stranger-owned price-drift receipt.

## Demo-8 — safety confirmation, separately killed

The eight-row reveal excludes Demo-8 because §3b labels it killed earlier. Both panes agree with
that safety outcome. A credential screen that sends raw secret material to a remote classifier has
already violated the boundary it claims to protect; Gitleaks (`https://github.com/gitleaks/gitleaks`)
and TruffleHog (`https://github.com/trufflesecurity/trufflehog`) cover local secret scanning, while
H4 covers tool-result admission without raw-secret disclosure. No demand score can revive this
mechanism.

## Final backlog decision

1. **Retain as demand-qualified:** Demo-4 only in narrowed generic form, Demo-5 as an integrity
   oracle, Demo-7 as a contract-conditional portable method, Demo-2 with a replay/action-scope
   wedge, and Demo-3 only as an evidence adapter.
2. **Hold:** Demo-9 until an independent ubs blind-spot and false-positive receipt exists.
3. **Reject:** Demo-6 as a separate surface unless Demo-3 proves a real distinct seam.
4. **Fail and replace:** Demo-1's lane-local route backtest with H3 cache-aware price-drift audit.
5. **Keep killed:** Demo-8; never send raw credentials to the judge.
6. **Prefer for next demand test:** H1 snapshot-bound completion evidence, H2 pre-action abstention,
   H3 price-drift audit, H4 tool-result replay, or H5 compaction-boundary benchmark, each with a
   stranger fixture and a negative control.

## NO-CLAIM

This reveal compares preregistered demand verdicts to the evidence collected in the four Duel-2
artifacts. It does not claim any demo is implemented, adopted, safe in production, superior to a
vendor, or backed by user interviews. Public issue reports and vendor documentation establish
problem signals and substitute categories; they do not establish market size or willingness to pay.
The route receipt proves the lane command ran, not that a stranger's router would benefit. The
signals numbers are not treated as portable until their generator/distribution is pinned. The
credential branch remains killed. No live model, provider, MCP, browser, secret, or production
agent was used.
