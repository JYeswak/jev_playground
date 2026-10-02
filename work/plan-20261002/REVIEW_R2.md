# Jev Discovery Plan — Review R2

**Review target:** `work/plan-20261002/PLAN.md` (round 1 integrated).
**Scope:** review only; this file is the only requested edit.
**Recommendation:** keep the plan's evidence-first protocol and candidates V1/V4/V6/V8/V9, but do not freeze or dispatch the portfolio unchanged. Add a measured, high-volume TTSR applicability vein; put a hard freshness/consumer-integrity gate ahead of all traffic-derived work; and separate deterministic maintenance from Jev discovery. The best new Jev candidate is not another ranking or memory-relevance experiment: it is suppressing a demonstrably inapplicable active rule reminder before it interrupts an agent.

## Round-one improvements to retain

R1 already corrected the major design defects: R140/R141 are closed evidence rather than active work; operational outcomes outrank classifier agreement; candidate labels, grouped held-outs, uncertainty, error handling, wave caps, and staged rollout are explicit. Keep those revisions. R2 should not reopen those settled points or relabel old experiments as new candidates.

## Highest-priority findings

1. **There is a high-frequency, unmined decision surface in TTSR rule injection.** R132 reports 1,447 organic `ttsr_injection` rows in seven days across 36 rules and 534 `purpose=ttsr` model calls. One rule fired 491 times (34% of all injections); blind review found 0/26 labelable cases where its reminder addressed the triggering event. The larger audit also found retired `claim-without-evidence` firing 125 times after retirement. These are direct observations of recurring agent interruptions, not a hypothetical consumer or a synthetic benchmark. At the same time, the rule-level call join is missing, so these counts do **not** establish per-rule model cost or prove any active rule's false-positive rate. This is strong keyless-feasibility evidence for an applicability decision, not permission to spend immediately.
2. **TTSR runtime freshness is a data-integrity precondition.** If a disabled rule continues to inject, source configuration, loaded runtime state, and logged rule identity disagree. Any rule-quality experiment could then sample the wrong active population and any rule-level rate could be misattributed. Reconcile which rules are actually loaded before constructing a new candidate corpus. R132 is the measured defect; do not treat it as an unexplained old event or as proof every rule remains stale.
3. **Separate event counts from decision counts and cost.** The current seven-day shadow census gives `gate-observe` 17,963 rows / 1,194 paid calls, `injection-shadow` 9,257 / 274, `webscreen-shadow` 283 / 190, and `memory-filter` 8,112 / 1,470. These are event rows versus paid calls, not independent decisions, beneficial actions, or a stable daily rate. The census covers partial boundary dates (2026-09-26 and 2026-10-02); moreover, 2026-10-01 alone has large spikes (6,007 gate rows, 3,536 injection-shadow rows, 7,674 memory-filter rows). Do not rank veins by raw row volume or extrapolate the 7-day window as a stationary daily workload. Use complete UTC windows, unique event/session denominators, and measured downstream outcomes.
4. **V1/V4/V8/V9/V6 remain hypotheses, not evidence of available signal.** The plan correctly requires feasibility first, but its dispatch list can read as though candidate names already imply enough natural episodes. Require a machine-traffic census and consumer action join before assigning worker effort. An inconclusive candidate stays out of the live-call budget; it does not justify weakening the common bar.

## Proposed revisions

### 1. Add a TTSR applicability vein, gated by live-rule reconciliation

**Why:** This is the clearest newly observed decision gap with repeated organic opportunities and a direct consumer. The current behavior injects a rule reminder when its trigger predicate fires. The new decision is narrower than generic skill/rule recommendation: *given an already-triggered active rule and the current event, is the rule's specific intervention applicable now?* A safe positive action is suppressing only high-confidence inapplicable reminders; uncertain answers preserve the current reminder. That matches Jev's comparatively stronger asymmetric binary use pattern without claiming that relevance to a prompt equals downstream usefulness.

The keyless stage must first establish that the rule is active in a fresh session, join each injection to the exact rule ID and triggering event, recover enough preceding/following context without leaking the reviewer label, and blindly adjudicate whether the rule's stated intervention was applicable. Exclude blocked-edit interrupts and truncated event context as unknown, as R132 did. Split by session and rule lineage. The current census's missing per-rule call attribution is a feasibility defect: add a stable rule ID to a future observation path only if it can be recorded without raw sensitive content; do not infer rule costs by dividing aggregate `purpose=ttsr` usage.

**Rationale and limits:** R132's 0/26 for one retired rule is not a general estimate for the remaining rules (wide interval, selected sample, rule already retired). The 13-rule audit has uneven Ns and several rules below any useful bar. Start with currently active high-volume rules and require a held-out, independently labeled sample; do not pool rule identities to manufacture N. Since R131/R133 show skill hints traded recall for misroutes, include a must-not-suppress relevant-reminder set and compare to the deterministic trigger/current behavior. If deterministic rule predicates already decide applicability, record BASELINE WINS and fix the trigger instead of calling Jev.

**Change versus original (add to §4):**

```diff
+### V10 TTSR reminder applicability (new; feasibility only until active-rule and event joins pass)
+- Traffic basis: R132's 2026-09-24..10-01 census counted 1,447 organic TTSR injections across
+  36 rules and 534 purpose=ttsr calls. This establishes repeated traffic, not benefit, independent N,
+  or per-rule cost. Do not reuse the retired key-canonical-source rule as a live candidate.
+- Decision: for an already-triggered, currently active rule, is its specific reminder applicable
+  to this exact event? Suppress only a high-confidence inapplicable reminder; invalid, low-confidence,
+  timeout, or unavailable answers preserve current behavior.
+- Keyless gate: in a fresh session, verify loaded rule IDs against configured enabled/disabled state;
+  join injection -> rule ID -> triggering event -> next agent action. Blindly label applicability
+  from sufficient event context; unknown/truncated/blocked cases are censored. Establish eligible
+  volume by active rule and session, and a deterministic-trigger baseline before preregistration.
+- Unit/split: one rule-injection episode, deduplicated; split by session and rule lineage. Sample
+  must-not-suppress relevant reminders and hard negatives. Never treat repeated injections as
+  independent labels or aggregate low-volume rules to pass a bar.
+- Outcome: fewer inapplicable interruptions per eligible agent-turn at no increase in missed
+  applicable reminders or downstream safety/work errors. The primary measure is a blind-labeled
+  paired policy outcome, not Jev/current-rule agreement.
+- No-go: if the runtime/config join, sufficient context, active eligible volume, or independent labels
+  cannot be established keylessly, stop without Jev calls. Reuse R132 evidence only as motivation,
+  not as a held-out result.
```

### 2. Add a rule-runtime reconciliation gate before all TTSR-derived work

**Why:** R132 reports that a retired rule still fired 125 times. This is a concrete stale-runtime / lifecycle failure, and it makes current rule traffic and inventory claims potentially stale. Fixing it is useful maintenance even if Jev has no role. It also protects V10 from evaluating disabled rules or labeling the wrong rule version. Do not make the model responsible for a configuration/cache invalidation defect.

**Change versus original (add before §4 dispatch prerequisites):**

```diff
+### TTSR source/runtime freshness (keyless prerequisite, not a Jev vein)
+- Before using TTSR traffic as an eligible population, compare enabled/disabled rule IDs and
+  versions in source configuration with what a fresh omp session actually injects.
+- Plant one enabled and one disabled rule in a disposable session; verify the enabled positive and
+  disabled negative, then repeat after the supported reload/restart boundary. A retired rule firing
+  is a failed freshness gate, not a positive sample or Jev error.
+- Reconcile historical rows separately; do not retroactively infer which rule version was loaded
+  when the log lacks that identity. Record the active population and exact measurement window.
```

### 3. Rank by qualified consumer value, not traffic alone; distinguish daily workload from opportunity

**Why:** Raw volume can be a trap: existing high-volume surfaces are already served by Jev, and event rows include multiple observations per action. The census demonstrates this: memory-filter is 8,112 rows but 1,470 paid calls; gate-observe is 17,963 rows but 1,194 paid; webscreen-shadow 283 rows but 190 paid. Conversely R134 had a model that often changed rank but no downstream opens. Rank candidates by *eligible unique decisions × measurable action headroom × safe intervention probability*, with quality and labels as hard gates. Preserve cost/call caps as upper bounds, not a reason to use all available calls.

**Change versus original (add to §3 and amend §7):**

```diff
+Portfolio admission also reports, for one complete UTC window: raw observations, unique eligible
+decision episodes, sessions, consumer actions joined, censored/unjoined rows, baseline action rate,
+and current model/API calls. Report partial-window counts separately. Traffic volume is opportunity
+evidence only; it is not Jev benefit, label N, or authorization to send that data to a provider.
```

### 4. Keep the current candidates but require a candidate-specific stop boundary and status readback

**Why:** V1 is already marked running and V4 waits on a bead; V8/V9/V6 are not yet admitted by keyless evidence in this review. These statuses can drift while a plan is converted into Beads. Make conversion reconcile each source and status once, and write a no-go boundary that prevents adjacent relabeling (notably V9 must not become another memory-relevance experiment; V4 must stay distinct from R137-R139).

**Change versus original (replace the first line of §7):**

```diff
-- Reconciled: V2, V3, V5 closed (section 2.2). Active: V1 (WildCarp). Queued: V4 (HazySpring after
-  jev-1w52), V8 and V9 (next free workers), V6 deterministic part (any free worker).
+- Before conversion, read back each candidate's current bead state, owner, source data window, and
+  existing receipts. R140/R141/V5 remain closed; never redispatch them. Confirm V1 is still active
+  and whether V4's prerequisite is complete; queue V8/V9/V6/V10 only after their separate keyless
+  feasibility gates. Do not encode worker names/pane assignments as candidate status.
```

### 5. Do not expand the wave budget to fill it

**Why:** Five named candidates are in the current portfolio (V1, V4, V8, V9, and V6's semantic remainder); 300 each would permit 1,500 calls, already above the 1,200 wave cap, before adding V10. More importantly, discovery calls cannot repair missing labels, missing runtime identity, or low action volume. The TTSR census has 534 TTSR-purpose calls total in a seven-day window and unknown per-rule allocation, so a naive cap could overwhelm natural traffic or produce repeated judgments on a few sessions.

**Change versus original (replace §5 step 3):**

```diff
-Wave cap: at most 300 calls per vein and 1,200 calls for this whole wave.
+Keep the existing 1,200-call whole-wave hard cap; it is a ceiling, not a target. Allocate a lower
+per-vein cap in each preregistration based on eligible independent episodes and paired analysis.
+V10 receives zero live calls until active rule IDs, event joins, labels, and holdout feasibility pass.
+Never spend multiple calls on repeated rows to fill a cap; one question/request remains the default.
```

## Suggested execution order

1. **Resolve TTSR freshness first, keylessly.** Verify active/disabled IDs in a fresh session and establish the historical limitation for the 125 stale injections. Keep this as maintenance, not a Jev result.
2. **Run V10 keyless feasibility on currently active rules only.** Measure complete-window eligible unique injection episodes, same-event action joins, independent labelability, rule-level baseline precision/coverage, and must-not-suppress cases. Admit only a rule/stratum that has enough labelable headroom for its own bar.
3. **Continue V1/V4/V8/V9/V6 only on their own gate.** Do not let the attractive TTSR volume displace a stronger candidate whose operational outcome is already measurable; use the same consumer/action and independent-N criteria.
4. **Preregister and spend only on a candidate that survives its keyless stop test.** Reserve the wave cap across admitted candidates; a no-call no-go is a complete feasibility result.
5. **Promote only with a live consumer readback.** For TTSR that means proving the applicable reminder remains and only confidently irrelevant reminders are suppressed, with current-rule behavior restored on every model/hook failure.

## Overall assessment

Round 1 made the plan scientifically much stronger. Round 2's best addition is a real new vein: high-volume TTSR applicability has both an observed consumer (agents receiving rule reminders) and an organic opportunity stream, unlike another ranking proposal with no downstream opens. The evidence is not yet enough for a live call: R132 exposes a runtime freshness defect, the TTSR event-to-rule call join is incomplete, and the 0/26 finding is specific to one retired rule. Address those boundaries first. A useful deterministic fix or an underpowered no-go is preferable to converting noisy injection counts into a Jev success claim.

**Evidence read for this review:** `NEGATIVE_EVIDENCE.md` R130-R141; `work/plan-20261002/REVIEW_R1.md`; `work/plan-20261002/PLAN.md`; `work/jev-r8dp/census.json` and `census.py`; `EVAL.md` native-judge and gate-demand entries. The census snapshot spans UTC dates 2026-09-26 through 2026-10-02 and includes partial boundary dates. This review made no Jev/API calls and does not claim a runtime retest, a new label audit, or an implementation result.
