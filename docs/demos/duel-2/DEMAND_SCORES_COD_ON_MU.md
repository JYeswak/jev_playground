# Duel-2 cross-score — COD on MU demand ranking

Status: cross-score of the other pane's demand artifact, not a replacement for either ranking.
Compared artifact: `docs/demos/duel-2/DEMAND_RANK_MU.md` (`#7DFA` in the read receipt).
COD artifacts already committed: `DEMAND_RANK_COD.md` (`e733de8`) and `DEMAND_HUNT_COD.md`
(`c33cd3c`).
Forbidden source honored: `docs/demos/PLAN.md` §3b was **not** read before this cross-score.

## Method

MU correctly changed the question from “is this a good contract?” to “would somebody want this?”
That is the right axis. I scored the ranking itself on five properties: evidence quality, buyer
specificity, substitute accounting, metric decisiveness, and resistance to supply/spec halo. The
cross-score is not a vote for COD's numbers. It reconciles disagreements by preferring direct
external pain over population guesses, and by penalizing an existing product category only when the
substitute actually covers the proposed wedge.

Evidence hierarchy used here:

1. A named external issue or benchmark with a concrete failure mode.
2. A maintained external product or official documentation showing an active buyer category.
3. A local contract, EVAL, or shipped fixture showing the proposed metric is runnable.
4. A market-size or adoption assertion without a linked source.

The other pane supplied useful claims and some external references. Several of its phrases—“most
agent users,” “hundreds of thousands,” “hundreds of teams,” and “ten-plus articles”—are not
independently linked in the artifact, so they are treated as hypotheses, not evidence. Conversely,
COD's first pass sometimes treated broad vendor attention as adoption proof; the revisions below
apply the same discount to both lineages.

## Side-by-side table

| Demo | COD | MU | Cross-score | Decision |
|---|---:|---:|---:|---|
| Demo-4 foreman-lite | 480 | 800 | **820** | MU is right that false completion is the strongest raw pain; COD underweighted it because of Beads coupling. |
| Demo-5 fact ledger | 760 | 750 | **755** | Near tie; real pain, but native memory and ledger substitutes require a portable oracle wedge. |
| Demo-7 signals starter | 520 | 620 | **560** | MU is directionally right; label burden and scikit-learn overlap keep it below broad demand. |
| Demo-9 review signal | 820 | 550 | **700** | Both are too extreme: broad AI-review demand is real, but existing bots and false-positive noise cap the immediate wedge. |
| Demo-3 claim-check gate | 360 | 500 | **430** | MU sees a real substance gap; COD is right that commit-message frequency is narrow. |
| Demo-2 admission screen | 780 | 450 | **700** | Direct injection incidents lift it above MU, but Lakera/Azure/Rebuff/Vigil-style substitutes block a 780 claim without a benchmark wedge. |
| Demo-1 route backtest | 540 | 350 | **520** | COD is right that cache/pricing failures create demand; existing routers own most generic routing demand. |
| Demo-6 claim-check notes | 320 | 350 | **330** | Agreement; population and differentiation are weak. |
| Demo-8 credential screen | 120 | 150 | **100** | Both correctly kill it; local secret scanners and Demo-2 cover the safe needs. |

The reconciled order is therefore Demo-4, Demo-5, Demo-2/Demo-9, Demo-1, Demo-7, Demo-3,
Demo-6, Demo-8. This is a demand order, not an implementation order. The highest-quality new
product hunt remains H1 snapshot-bound completion evidence, H2 pre-action abstention, H3 cache-aware
price drift, H4 tool-result admission replay, and H5 compaction-boundary integrity; each is a
better-shaped replacement than simply shipping the lowest-scoring original.

## Demo-4 — foreman-lite: 480 vs 800 → 820

MU's strongest point is that independent judgment of agent completion is a broad, immediately
recognizable pain. The artifact names Claude Code, Codex, and Cursor users, gives a concrete buyer
(people burned by a confident “done”), and measures human rework and judge agreement. That is a
better demand argument than COD's original treatment, which over-penalized the current `br`/Beads
coupling and treated generic code review substitutes as if they covered independent closeout.

The external Codex issues reinforce MU's direction. Codex issue
[#36718](https://github.com/openai/codex/issues/36718) asks for evidence-backed completion reports
because “implemented” and “all tests pass” claims can lack command, exit status, scope, or exact
revision. Codex issue [#41882](https://github.com/openai/codex/issues/41882) reports several PASS
signals agreeing while a shared writer remained broken. These are direct failure reports, not
vendor marketing.

The adjustment is not 940 for the original Demo-4. The current shape is still Beads/close-path
specific, and CodeRabbit, Qodo, Greptile, Copilot Review, and ordinary CI are adjacent substitutes.
MU's statement that “no dominant tool owns the independent-judge shape” is plausible but not proven
by the artifact; `backcheck` and `evigate` now exist as closer evidence-verification substitutes.
Therefore 820 is the reconciled score for the concept, while H1 in the hunt scores 940 only because
it expands the input to any agent transcript/revision and makes evidence freshness the product.

**Cross-score verdict:** MU wins the raw-demand call; COD wins the boundary warning. Preserve
MU's 800-level base, add 20 for direct issue evidence and cross-framework scope, and reserve the
higher H1 score for the broader snapshot-bound replacement. A real first EVAL must measure false
completion, stale receipt, focused-subset masquerading as full-suite, and human rework—not only
judge/human agreement.

## Demo-5 — fact ledger: 760 vs 750 → 755

The two panes substantially agree. MU supplies a concrete compaction-amnesia story and names the
buyer as a multi-hour agent user; COD supplies OpenClaw and Hermes evidence, plus Anthropic's own
compaction/memory documentation. MU is right that the byte-exact provenance-per-byte thesis is
meaningfully different from generic summaries; COD is right that native memory and ledger products
make a standalone storage product crowded.

The external issue evidence is strong. OpenClaw issue [#3560](https://github.com/openclaw/openclaw/issues/3560)
reports memory flush after truncation, which makes the flush too late. Hermes issue
[#64315](https://github.com/NousResearch/hermes-agent/issues/64315) reports a pending-memory buffer
reset without flush. ZeroClaw issue [#2381](https://github.com/zeroclaw-labs/zeroclaw/issues/2381)
proposes a pre-compaction flush. Those sources establish pain; they do not establish willingness to
adopt a particular ledger.

Both artifacts should reject MU's unsupported “hundreds of thousands” population statement and COD's
implicit assumption that a source-span ledger will beat every native memory system. The scored
concept should be a portable exact-fact retention test or ledger adapter, not “another memory
platform.” Context Ledger (`https://github.com/wiztek-llc/context-ledger`) and Hindsight
(`https://aclanthology.org/2026.acl-demo.27.pdf`) are substitutes that demand a differential
benchmark.

**Cross-score verdict:** retain 755, essentially a tie. The next demand test is not another market
essay: run a pre/post compaction fixture against at least two adapters, report exact-fact recall,
source-span coverage, lost-fact count, and byte cost, and include a negative control where a late
flush must fail. H5 is the better product candidate than the original ledger because it lets the
buyer test an existing system.

## Demo-7 — signals starter: 520 vs 620 → 560

MU is right that an offline synthetic template is the easiest stranger install and that calibration
is a useful practice. The other pane also honestly discounts the headline 62.6/95.1 numbers because
the upstream corpus is not vendored. That self-correction is good evidence discipline.

COD's lower score identifies the adoption bottleneck: the buyer needs labels, a stable distribution,
and enough examples before ECE/AUROC means anything. Scikit-learn already provides
`CalibratedClassifierCV` and calibration examples (`https://scikit-learn.org/stable/modules/generated/sklearn.calibration.CalibratedClassifierCV`),
so a generic “fit a signal model and report ECE” template has weak displacement power. The ASK
benchmark (`https://github.com/megansquire/ask-benchmark`) supports the existence of related
classification work, but it is not evidence that a new starter wins downloads.

MU's “thousands per year” and COD's “weak immediate demand” are both unmeasured. A buyer with no
labels gets a report-shaped artifact but no trustworthy threshold; a buyer with labels can often
assemble this from established ML tooling. Demand would rise if the starter owned a hard agent
behavior decision, such as pre-action abstention, instead of generic classifier calibration.

**Cross-score verdict:** 560. Keep the template only as a substrate for H2, whose paired
should-act/should-abstain fixtures create value before a customer corpus exists. Do not present a
local synthetic score as evidence of production calibration. EVAL must pin a generator/distribution,
include shuffled labels and empty corpus, and report ECE/Brier/selective accuracy with an explicit
unknown state.

## Demo-9 — review signal: 820 vs 550 → 700

COD's first score correctly saw broad AI-code-review demand and cited CodeRabbit's AI-adoption
material plus Qodo's review category. MU's lower score correctly surfaced category crowding, false
positive fatigue, style-comment noise, and per-review cost. The disagreement is therefore about
substitute strength, not whether the pain exists.

The CodeRabbit adoption article (`https://www.coderabbit.ai/blog/ai-adoption-how-developers-are-using-ai-dev-tools`)
and Qodo comparison material (`https://www.qodo.ai/blog/best-automated-code-review-tools-2026/`)
show a large active category. They do not show that teams will install a local Jev signal beside
those products. MU's exact 9:1, 64%, and “$1/review tax” claims are not linked to primary evidence
inside the ranking, so they cannot by themselves justify a 550 or a 820.

The useful differentiator is a calibrated, advisory signal beside ubs, not another prose review bot.
The local baseline in `docs/demos/USAGE-MAP.md`—ubs over four TypeScript files with 1 critical, 6
warnings, and 27 info findings—shows a testable starting point but is not market demand. The
candidate must prove actionability, abstention, reviewer time, and false-positive reduction on a
held-out diff set; scalar quality dimensions alone will not beat existing review tools.

**Cross-score verdict:** 700. COD's broad category score is too high because it assumes the buyer
wants a second review product; MU's score is too low because a self-hosted, receipt-bearing,
calibrated complement can target teams that disabled noisy SaaS bots. The score does not enter the
900+ replacement list until an external team demonstrates lower false-positive review burden. H1/H2
remain stronger hunts because their external issue evidence is more specific and their receipt/action
contract is less crowded.

## Demo-3 — claim-check commit gate: 360 vs 500 → 430

MU makes the best argument for this demo: commitlint checks shape, not whether a numeric claim in a
commit or release note matches an artifact. The external search found no mainstream official tool
that owns factual commit claims, and emerging tools such as backcheck/evigate show a neighboring
need. COD correctly asks how often ordinary repositories make checkable numeric claims and whether
a hook has enough evidence to act.

The named buyer—CI or release operator maintaining changelog-from-commits—is real but narrow. The
artifact's “hundreds of teams” count is unsupported, while commitlint's official role is documented
at `https://commitlint.js.org/` and should be treated as a strong adjacent substitute. The demand
is higher for evidence-backed completion reports over agent sessions than for a hook that parses
commit prose.

The metric is decisive if the team has a corpus: unsupported claim rate, contradiction refusal,
missing-artifact refusal, false-positive rate, and review time. Without that corpus the demo can
only show a beautiful negative fixture. A safe design keeps deterministic receipt checks
authoritative and uses `Choice`/`Noul` for explicit claim relation, not free-form “sounds true.”

**Cross-score verdict:** 430. Keep Demo-3 as an adapter in H1 rather than a standalone product.
MU's 500 is a reasonable upper bound for a release-specific buyer; COD's 360 reflects the much
larger number of repositories where the hook has no frequent claim surface. H1's 940 is not a
contradiction: it broadens the trigger from commit messages to all agent completion reports and is
backed by direct Codex issue pain.

## Demo-2 — admission screen: 780 vs 450 → 700

MU discounts this too aggressively by listing Rebuff, Vigil, PromptGuard, and enterprise shields as
if a mature detection category eliminates all demand. COD's 780 correctly cites multiple concrete
cross-framework failures: Google MCP Toolbox issue [#2844](https://github.com/googleapis/mcp-toolbox/issues/2844),
Microsoft AutoGen issue [#6017](https://github.com/microsoft/autogen/issues/6017), Agent-S issue
[#199](https://github.com/simular-ai/Agent-S/issues/199), and MCP issue [#3213](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/3213).
Those reports establish ongoing pain at the tool-result/action boundary.

MU is right that a generic prompt-injection detector is not a differentiated product. Lakera
screening (`https://docs.lakera.ai/docs/api/screening-roles`), Microsoft Prompt Shields
(`https://learn.microsoft.com/en-us/shows/responsible-ai/azure-ai-content-safety-prompt-shields`),
and existing open-source/enterprise guards mean the buyer needs a vendor-neutral replay benchmark,
policy provenance, action-scope decision, or local secret boundary—not another binary “injection”
score.

**Cross-score verdict:** 700. Direct issues lift the concept over MU's 450, while substitutes and
high false-positive cost cap COD's 780. H4's 920 is a stronger replacement because it is a
replayable regression benchmark with shadow/enforce separation and a hard “no raw secret to judge”
fixture. Demo-2 can remain a candidate only if its contract adopts that wedge.

## Demo-1 — route backtest: 540 vs 350 → 520

Both panes recognize that routing demand is real but substitute-heavy. MU's 350 discounts the
category because RouteLLM and vendor savings claims already exist; COD's 540 adds a concrete cost
metadata failure mode. The external evidence supports COD's adjustment: LiteLLM issue
[#38064](https://github.com/BerriAI/litellm/issues/38064) describes cache-read pricing and list-order
behavior producing a large cost difference, and Hugging Face tau issue
[#574](https://github.com/huggingface/tau/issues/574) describes route-specific cached-token pricing.

LiteLLM's official routing and cost-tracking docs (`https://docs.litellm.ai/docs/routing`,
`https://docs.litellm.ai/docs/proxy/cost_tracking`) and RouteLLM's maintained repository
(`https://github.com/lm-sys/RouteLLM`) are strong substitutes for a generic router. They are not
necessarily substitutes for an independent price-drift audit that catches unknown or route-specific
metadata before the operator trusts a savings report.

The route backtest's shipped six-turn fixture and denominator receipt are good local evidence of
installability and measurement, but do not establish a buyer. It must keep actual spend,
counterfactual spend, and unknown price rows separate. The better demand artifact is H3, which
measures whether the existing router's cost premise is trustworthy rather than asking the buyer to
adopt a second router.

**Cross-score verdict:** 520. COD wins the evidence adjustment; MU wins the substitute warning.
Keep the original below 700 and prioritize H3. A price-drift audit that finds zero drift should
still produce a useful receipt; otherwise it is only a savings calculator.

## Demo-6 — claim-check notes: 320 vs 350 → 330

The panes agree that this is a small evidence-writing population and that Demo-3 can cover much of
the need manually. MU's “evidence-note author” is a plausible buyer, but the artifact does not name
an external issue, benchmark, or maintained tool gap specific to notes. COD's score is appropriately
low because generic citation/fact-checking workflows already exist.

The only defensible metric is before/after review burden over a constrained note corpus: supported,
contradicted, insufficient-context, and unsupported claims; citation span coverage; and false
refusal rate. A general language model answer is not evidence, and a notes parser that cannot
preserve source spans is not a claim checker.

**Cross-score verdict:** 330. Do not build this separately. Fold explicit evidence-note adapters
into H1 if a real completion-report buyer needs them, or into H5 if the notes are compaction facts.
A standalone Demo-6 contract needs a named external user and a corpus before it can leave the kill
list.

## Demo-8 — credential screen: 120 vs 150 → 100

The panes agree on the essential ruling: a design that asks a remote judge whether raw credential
content is suspicious has already crossed the security boundary. The small score difference is
irrelevant; it should not be shipped or marketed.

Gitleaks (`https://github.com/gitleaks/gitleaks`) and TruffleHog
(`https://github.com/trufflesecurity/trufflehog`) already cover local secret scanning. Demo-2/H4
covers untrusted tool-result admission, but it must guarantee that secret-shaped bytes remain local
or redacted. The safe composition is two separate stages with separate receipts, not one classifier
that receives both.

**Cross-score verdict:** 100 and kill. H4 is the only acceptable replacement in this area, and H4's
first EVAL must prove zero raw-secret bytes cross the judge boundary. A pass on detection recall
cannot compensate for a secret emission.

## Evidence-quality score for MU

| Dimension | Score | Reason |
|---|---:|---|
| Demand-axis discipline | 9/10 | Explicitly rejects spec quality and scores want; four answers per demo. |
| Buyer specificity | 8/10 | Most rows name a buyer, but several population sizes are asserted without source. |
| External grounding | 7/10 | Strongest on compaction and false completion; weaker where “ten-plus articles” or vendor claims are unnamed. |
| Substitute accounting | 9/10 | Correctly penalizes mature review, routing, memory, and security categories. |
| Measurement clarity | 8/10 | Before/after metrics are concrete, but some require labels or mechanisms not yet shipped. |
| Safety/epistemic restraint | 8/10 | Honest about unbuilt work and kills Demo-8; must remove unsupported population counts. |
| **Overall ranking quality** | **8.2/10** | Directionally strong; direct issue links and differentiated wedges change several scores. |

## Corrections to carry forward

1. Replace unsupported population language with “buyer hypothesis” unless a source or observed
   download/issue corpus is attached.
2. Separate category demand from product displacement. AI review, prompt injection, routing,
   calibration, and memory all have demand; that does not make an unbuilt local tool a winner.
3. Treat `backcheck`, `evigate`, RouteLLM, LiteLLM, Lakera, Azure Prompt Shields, Gitleaks,
   TruffleHog, Context Ledger, Hindsight, AgentAbstain, and AbstentionBench as substitutes or
   comparison baselines, not as evidence that demand is absent.
4. Prefer H1/H2/H3/H4/H5 over the weak originals because each has a specific external failure,
   an installable offline starting point, a typed Jev-native decision, and a receipt that can prove
   a negative control.
5. Do not turn a score into a verdict. A 900+ hunt score means “worth a real demand test”; it does
   not mean users will install it, a model will be accurate, or a production gate is safe.

## NO-CLAIM

This is a cross-score of two research artifacts. No product was installed, no user was interviewed,
no vendor adoption figure was verified, and no external benchmark was re-run. The cross-scores are
judgment calls based on the linked public issues/docs and the local contracts/fixtures; they are not
market-size estimates, revenue forecasts, security certification, or implementation results.
`PLAN.md` §3b remains unread at this stage.
