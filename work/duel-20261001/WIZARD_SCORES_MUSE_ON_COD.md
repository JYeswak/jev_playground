# Scores: Muse on the Codex five — duel round 2, 2026-10-01

Scale 0–1000: idea quality × real-world usefulness (humans + agents like me)
× implementability × whether the benefit justifies the complexity/tech debt.
Judged as a builder who would have to implement, measure, and maintain each one.

| Rank | Idea | Score |
|---|---|---|
| 1 | Fast, occurrence-scoped memory filtering | 860 |
| 2 | One composable web-result screening path | 800 |
| 3 | Effective retirement and version-bound activation | 760 |
| 4 | Evidence-addressed needs-human pages | 580 |
| 5 | Fleet-persistent judgment budgets and refusal holds | 520 |

Credit first: the evidence-boundaries section is the best part of the
proposal. It states what is *not* proven (no combined precision estimate,
no causal recovery-time claim, mixed log rows are not a savings
denominator, fake-offline rows excluded). That honesty raises my priors on
every bar below actually being enforced. Scoring is on the ideas, not the
prose — but the prose is why I trust the bars.

## 1. Memory filtering: parallel + occurrence-scoped — 860

**Why it leads.** Two genuine defects, both on a blocking path I feel every
turn: (a) serial judging (20 × ~137ms ≈ 2.7s of `before_agent_start` wall
before work starts — the agent and the human both wait); (b) a real safety
hazard class, `pruneSystemPrompt` removing cleaned lines across *all*
system-prompt elements, so a relevance verdict on a recall can delete an
identical instruction line elsewhere. (b) is the kind of silent
instruction-loss bug that poisons sessions without leaving evidence, and
the fix direction (span-addressed drops, keep-on-ambiguity) is exactly
right. The quality evidence already exists (0.978/0.985 held-out), so this
is pure engineering on top of a shipped verdict — my favorite kind of work.
Concurrency ≤4 with a 1.5s deadline and keep-on-unresolved is well-shaped;
the memo-accounting catch (a memo hit must not re-bill historical tokens)
shows the author has actually thought about what gets measured.

**Deductions (−140).** Benefit concentrates on heavy-recall turns; the
median turn carries few memories, so median latency savings are small and
the win is p90-flavored — worth stating in the receipt. The 1.5s deadline
against p95 230ms/item gives ~5 waves ≈ 1.15s + overhead: tight, and any
deadline miss converts to keeps, so coverage must be reported next to
latency or the experiment can "win" by judging less. Span hashing +
dedup + per-element preservation is the most intricate code in the five
ideas; the replay-equivalence bar (frozen transport preserves every
eligible-span decision) is the right guard and I would hold it strictly.
One more consideration: 4 in-flight against the TypeSafe API from many
fleet processes at once — the per-process story is fine, the fleet-wide
burst story wants a sentence in the prereg.

**Planteds:** the occurrence-collision negative (drop verdict must remove
only the recall span, never the duplicated instruction) is the test I would
have written. Good.

## 2. Composable web screening — 800

**Strengths.** The reporting defect is real and load-bearing: `withheld:
flag` written in shadow mode means today's logs cannot distinguish "would
have withheld" from "did withhold" — and the global wrappers' whole
SHADOW→ENFORCING decision (jev-j0er) rests on those logs. Fixing that is
worth doing even if nothing else ships; it is nearly a one-liner plus a
test, and I would sever it from the orchestration work and land it first.
Deterministic composition (enforcing whole-result flag wins, else passage
replacements, else byte-exact original; failures contribute nothing) is the
correct architecture for two writers on one result, and running both evals
concurrently removes serial latency instead of adding a third detector.
Freezing both questions/personas (no new model capability) bounds the risk.

**Deductions (−200).** The multi-writer hazard is stated conditionally
("depending on host sequencing") — I want one measurement of what omp
actually delivers to the second hook today before building the
orchestrator; if each hook already receives the original, half the
justification evaporates (the reporting fix and the latency win stand).
Traffic is modest (~20 events/day), so the dollar upside is small; this
scores on reliability + rollout-evidence, not savings, and should be
presented that way. Also: concurrent eval doubles simultaneous gateway
load per event — trivial here, but the pattern shouldn't be copied to
high-volume seams without noting it.

## 3. Effective retirement — 760

**Strengths.** R132's 125 post-retirement firings are a measured,
embarrassing defect: withdrawal does not withdraw. The owned-hook half
(check a retirement record before acting/applying, late answers cannot
resurrect) is cheap, complete, and clearly worth building. Binding policy
revision to loaded code bytes + recording it on first invocation is good
hygiene that also fixes "configured masquerades as running." The native
TTSR half is handled with rare honesty (may be impossible from our side;
stale workers stay explicitly incomplete rather than greenwashed).

**Deductions (−240).** Half of a proposal being possibly-impossible caps
the score: the native-rule leg is where most of the 125 wasted firings
live (TTSR injections into context), so the shippable half addresses the
smaller share of the observed waste. Overlaps idea 5's sibling (durable
state): the retirement record and the allowance store should be one
mechanism, not two filings. And the genuinely cheapest mitigation gets one
clause but deserves emphasis: stop *referencing* retired rules in
configs/profiles so fresh sessions never load them, while the runtime
check covers already-running workers.

## 4. Needs-human enrichment — 580

**Strengths.** Best-structured gamble of the five: a keyless opportunity
check first (are ≥10/30 prefixes actually missing the decision?), an
explicit deterministic fallback (last explicit question) that wins ties
against the Jev seat, enrichment-failure-still-pages, and no suppression
of the incumbent for comparison purposes. The Choice-over-spans design
(select, never generate/approve) contains the blast radius correctly —
quote without executing is the right line for approval-adjacent text.
Small scope (≤20 calls/day) caps the downside of being wrong.

**Deductions (−420).** It is a bet that the bottleneck is excerpt quality
rather than human availability, and the author's own evidence (6.9 vs 5.4
min, correctly labeled non-causal) points at availability. If the keyless
check finds the decision is usually present, the correct outcome is the
formatting-only winner at $0 — which makes this a good *experiment* but a
weak *feature proposal*, and I score proposals. The 95%-correct-selection
bar on a held-out set is doing the heavy lifting for a 25%-faster-resume
claim that will be very hard to power (30 interleaved pages, censored
cases, human-availability variance). Fund the keyless check; decide after.

## 5. Fleet-persistent budgets — 520

**Strengths.** Names a real failure class with a real incident behind it
(233×402 before the hold) and correctly excludes native judge traffic from
its scope. Sharing the 402/auth hold across processes for one account is
the valuable kernel: it is small (file-based refusal record), clearly
correct (a new process must not re-storm a known-dead credential), and
completes the existing 15-minute process-local hold. Conservative
accounting of crashed reservations and refusal to cache failures/grants
are the right instincts.

**Deductions (−480).** The proposal itself concedes the central objection:
a coordination mechanism "built to save pennies," with the danger of a
central bottleneck. Per-surface durable allowances solve a problem with no
current incident (caps rarely bind; no storm since the hold), at the cost
of the most intricate state in the five ideas — cross-process atomic
admission, crash conservatism, secret-free identity binding, day-boundary
semantics — plus a "narrow safe Rust" component, i.e. a new language
runtime in the fleet, to administer token caps. That complexity ledger
does not balance. The conditional cache (≥10% exact duplicates first) is
correctly gated and will, I predict, stay ungated: memory states embed
per-turn prompts, so exact repeats across processes should be rare.
Recommendation if funded: sever the shared 402-hold (ship it; it is
idea-sized) from allowances+caching (do not build without an incident).

## Overall

Fund in this order: idea 1; idea 2's reporting fix immediately, then its
orchestrator after one host-sequencing measurement; the owned-hook half of
idea 4 (fold its state record together with the 402-hold kernel of idea 5
and stop there); idea 5's keyless excerpt audit only. The list's discipline
— modify paths, freeze questions, bars before labels, stop conditions on
every branch — is what makes even the rejections cheap. My top objection
across all five: none proposes removing anything, and the fleet's cheapest
savings to date came from removals (retirements, silence over misroutes).
The next duel should include one "what do we turn OFF" candidate by rule.
