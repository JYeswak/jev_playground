# Jev Discovery Plan — Review R1

**Review target:** `work/plan-20261002/PLAN.md` (DRAFT round 0).
**Scope:** plan review only; no implementation or change to `PLAN.md`.
**Recommendation:** do not convert this draft to beads unchanged. First reconcile its state with evidence already present in this checkout, narrow the portfolio to viable candidates, and replace the shared success protocol. The core discovery goal is sound; the present candidate list and acceptance rules would spend calls on already-refuted work and could declare a model win without demonstrating user benefit.

## Highest-priority findings

1. **The plan is already stale relative to the evidence in this checkout.** `NEGATIVE_EVIDENCE.md` R140 records the proposed V2 conductor triage experiment as FAIL: Jev accuracy 0.704 against a 0.75 bar, with action recall 0.459; it names missing fleet/bead state as the limit. R141 records V3 as NOT ENOUGH DATA / BASELINE WINS: 5/151,275 labels were over 60 seconds, and the recorded duration is censored for backgrounded calls. These are not future candidates; they have measured outcomes and retry conditions. R140/R141 should be linked into the plan and their beads/status checked before dispatch, not re-run as V2/V3.
2. **The evaluation unit and label definitions are underspecified.** A same command appearing later is not proof that an identical retry would succeed under the same state; a conductor action is only a proxy for whether a message needed action; “ever use again” is not the same as whether a tool result can be safely removed. These target/proxy gaps can make accuracy meaningless even with a large N.
3. **“Beat the baseline by a stated margin” is not a complete gate.** No metric, decision threshold, paired test, confidence bound, multiple-candidate policy, or minimum operational effect is specified. N≥60 and a held-out slice do not guarantee usable power—especially for rare harmful outcomes, clustered sessions, and repeated tuning.
4. **The stated final conclusion is too broad.** A failure of V1–V5 cannot establish that no new useful decision exists: V6/V7 are explicitly untested, and even V1–V5 cover a small, biased set of candidate ideas. It can only close those tested candidates under their specified designs and data windows.
5. **A model win is not automatically a product win.** The goal requires a new Jev decision and live Jev calls, but several candidates are better served by deterministic policy or conventional statistics. Jev should be introduced only when it improves the downstream action under the real cost/safety constraints, not merely when a classifier score is higher.

## Evidence basis and plan-specific corrections

- `AGENTS.md` defines progress as an ON capability tested both ways, or a measured Jev result with a pre-fixed bar on data not written by us. Live runs must be bounded, stop on 401/402/403, report model/tokens/latency/status and spend; the model is pinned to `jev-1.13.0`. Offline and live evidence must remain distinct.
- The README’s current measured results and `work/jev-inventory/expected.json` show a more nuanced inventory than “seven surfaces.” The plan’s five-row proven table is not an inventory of every applied surface, and some runtime entries are shadow/off/retired/idle-by-design rather than useful active decisions. Separate **implemented/on**, **measured useful**, **shadow**, and **retired/refuted** in the plan; never count a capability merely because it exists.
- The plan’s `$0.32/day` statement is not directly comparable to AGENTS’ “about $3 a week” (~$0.43/day), and README’s older 2026-09-25 census is explicitly not a current daily rate. Pick one observation window/source and label it as an estimate; do not use it as a universal cap.
- R134 shows that a Jev ranking was not actionable because users did not open selected results. This is direct evidence for measuring the *downstream action*, not only model agreement/accuracy. R137–R139 show that repeated prompt/conjunction changes did not solve memory keep precision; V4 must not recast that exhausted relevance direction without a new fact. R140/R141 provide the concrete V2/V3 stop findings above.

## Proposed revisions

### 1. Add a state reconciliation gate before dispatch; mark V2 and V3 complete as evaluated

**Why:** The target plan lists V2 and V3 as currently dispatched, but R140 and R141 already contain outcomes, bars, costs, failure analysis, and retry conditions. Re-running them wastes calls and risks obscuring the recorded verdict. The first plan operation should reconcile bead status and linked evidence, not issue another dispatch. Also define what “seven surfaces” means against the inventory: active/on is not equivalent to useful, measured, or Jev-exclusive.

**Change versus original (add to §1 / replace the V2 and V3 entries in §3):**

```diff
 Status: DRAFT round 0 (conductor BrownGoose). Consumer: the five jev worker panes, via the beads this
 plan converts into. Retirement: this file is frozen once its beads exist; the beads carry everything.
+
+Evidence snapshot: reconcile this draft against NEGATIVE_EVIDENCE.md, EVAL.md, and
+work/jev-inventory/expected.json before dispatch. Record the snapshot/revision used by each
+candidate. Existing verdicts are not redispatched; check the corresponding bead and preserve its
+retry condition. Inventory rows distinguish ON, shadow, OFF/retired, and useful-measured.
```

```diff
-### V2 Conductor triage (pane 5, OrangeFrog, dispatched 04:15Z)
-- Decision: does this message reaching pane 1 need conductor action?
-- Labels: whether the conductor's next turn changed state (ntm send, br, git, edit) or only replied.
-- Baseline: message-type rules (IDLE repeat = no action; DONE = action).
-- Payoff: hundreds of pages/day cost conductor context; suppressing the no-action ones saves it.
-- Risk: label leakage (the conductor's response depends on later messages); restrict to the first
-  response after each message.
+### V2 Conductor triage — evaluated; no-go for text-only design (R140)
+- Evidence: `NEGATIVE_EVIDENCE.md` R140 / bead `jev-6c8n`; Jev 0.704 vs 0.75 bar, action
+  recall 0.459. Autopsy identifies fleet/assignment and bead state absent from the packet.
+- Action: do not redispatch or wire this text-only filter. Reopen only after a state-enriched
+  candidate beats the frozen cheap baseline keylessly on the frozen items.
```

```diff
-### V3 Long-runner prediction (pane 6, WindyLantern, dispatched 04:15Z)
-- Decision: from command text and cwd, will this call run longer than 60 s?
-- Labels: recorded wall time in tool results.
-- Baseline: command-name table (cargo, npm test, gates.sh, rpc_drive => long).
-- Payoff: fewer blocked turns, fewer needless background jobs.
-- Risk: duration depends on machine load, not text; a ceiling on achievable accuracy.
+### V3 Long-runner prediction — stopped at feasibility (R141)
+- Evidence: `NEGATIVE_EVIDENCE.md` R141 / bead `jev-uup3`; 5 positives in 151,275 rows,
+  majority-short baseline 0.999967, and wall-time labels censor backgrounded calls.
+- Action: no live calls. Reopen only after a keyless label-source proof joins backgrounded
+  completions and yields enough uncensored positives under the predeclared bar.
```

### 2. Change the objective from “higher model score” to “better safe downstream decision”

**Why:** In R134 Jev disagreed with provider rank but users opened none of the picks; ranking agreement was not the relevant payoff. V2 similarly used conductor action as a proxy for need, and R141’s recorded outcome did not measure actual duration. Require each candidate to state the action changed, the loss of false positive/negative decisions, and the measurable operational effect. If a deterministic rule wins, ship or recommend that rule as a separate engineering result, but do not count it as a new Jev decision or as a Jev win. Avoid making Jev a requirement where the baseline already solves the consumer’s problem.

**Change versus original (replace §1 goal and add to §3 candidate contract):**

```diff
-The goal of this plan is one thing: find at least one new Jev decision, on data this machine produces
-every day, that beats the best cheap baseline by a pre-committed margin on live `jev-1.13.0` calls,
-and turn it on.
+The goal is to identify a real, recurring decision gap in this machine's workflow. A candidate
+advances only if the end-to-end policy (Jev plus its safe fallback and action threshold) improves
+the predeclared operational outcome over the strongest eligible cheap baseline by a material,
+precommitted margin. A deterministic-baseline win is useful maintenance, not a Jev discovery. No
+candidate is required to ship; an evidenced no-go is a valid result.
```

```diff
 Each vein is one new Jev decision. All share the protocol in section 4. Veins are ordered by the
 expected value of a pass times the probability that a pass is measurable at all (data exists, a
 baseline does not already solve it).
+
+Before ranking or dispatch, each vein must name: consumer and concrete action; unit of decision;
+label source and what the label actually means; eligible population; false-positive and
+false-negative costs; cheapest deployed baseline; operational outcome (not only classifier score);
+and a retry condition. Drop a vein if the action can be decided exactly and safely by a cheap rule.
```

### 3. Replace the shared protocol with a paired, leakage-resistant, power-aware gate

**Why:** N≥60 is a convenience threshold, not a sample-size justification. At 60 examples, rare events may not appear; with session-correlated examples, effective N is lower still. “Held-out slice” does not prevent leakage if examples from the same session, duplicate command, or same bead occur in both sides. The 300-call cap is per vein, with no portfolio-wide cap; seven candidates can therefore consume up to 2,100 calls and sequential experiments can overstate the winner. Comparing metrics without paired intervals or a threshold does not establish the stated margin.

Use a keyless feasibility check to freeze the dataset, group split, label, baseline, and analysis before live calls. Compare Jev and baseline on the same eligible examples, report the paired disagreements and uncertainty, and select the primary metric from the operational harm/benefit. For rare safety failures, zero observed errors is not proof of zero risk; specify an acceptable upper confidence bound and test set size. Avoid peeking or tuning on held-out rows. Keep the existing safety principle: malformed, low-confidence, error, cap, or unavailable model takes the explicit safe path.

**Change versus original (replace §4):**

```diff
-1. Keyless feasibility: count usable labelled items N, the base rate, and the cheapest baseline's
-   score. Stop at N < 60 or if the baseline already meets the bar (NOT ENOUGH DATA / BASELINE WINS).
-2. Commit the bar before any live call: Jev beats the best baseline by a stated margin on a held-out
-   slice; name the tooling decision it changes and the per-day saving.
-3. Live `jev-1.13.0`, one question per request, at most 300 calls, spend stated; labels come from
-   observed outcomes, never typed.
-4. One-line verdict: N, baseline, Jev, margin, spend, verdict. PASS proposes the seam; FAIL writes a
-   NEGATIVE_EVIDENCE line. A non-author pane verifies before close.
-5. LOSS DEPTH applies once per vein: on FAIL, autopsy the failing rows and try the single best
-   one-variable fix on a dev slice before closing.
+1. Keyless feasibility: freeze a reproducible eligible population, label provenance, base rate,
+   uncensored-label check, and strongest cheap baseline. Split by the natural dependency group
+   (session/task/bead, not random rows); keep a final untouched held-out set. Stop when labels,
+   positives, or power cannot support the decision—not at a universal N=60. Stop if a deterministic
+   baseline already achieves the consumer's bar.
+2. Before any live call, commit a preregistration with the exact model (`jev-1.13.0`), state and
+   question, threshold/fallback, primary operational metric, baseline, margin, paired statistical
+   method/uncertainty bound, harm limits, eligible row hashes, split, call/spend cap, and go/no-go
+   rule. Include an explicit cap for the whole discovery wave, not only per vein.
+3. Run the pinned Jev arm only on the preregistered held-out eligible rows, paired against the
+   baseline on those identical rows. One question per request remains the default. Capture for each
+   attempted call: model, row ID/hash, status, input tokens, latency, and spend; stop on 401/402/403,
+   cap, or other preregistered hard stop. Never label a timeout/error as a safe model decision.
+4. A PASS requires the predeclared material operational improvement and harm bound, not merely a
+   point-score lead. Report N eligible/attempted/scored, base rate, paired counts, uncertainty,
+   latency distribution, spend, and excluded/censored rows. A baseline win, FAIL, or insufficient
+   evidence has its own explicit verdict. A non-author verifies the frozen arithmetic and source
+   links before close.
+5. Keep LOSS DEPTH, but separate exploration from confirmation: diagnose failure on development
+   data; change one variable at a time there; freeze the best candidate; then use a fresh untouched
+   confirmation set with the original or stricter bar. No repeated peeking at or reuse of the final
+   held-out set as a development set.
```

### 4. Fix candidate labels and operational validity before spending on V1, V4, and V5

#### V1 — Retry-worthiness

**Why:** “Failed command followed by the same command later” is an observed sequence, not a counterfactual retry label. The later run may be in a changed state, may have different inputs/environment, or may not be a retry at all. It can also miss successful retries hidden by new sessions or background execution. A regex may be a sensible deterministic fallback, but the useful question is whether the policy reduces wasted retries without suppressing recoverable work—not whether a text classifier predicts a proxy label.

**Change versus original:**

```diff
-- Decision: given a failed command and its error output, will an identical re-run succeed?
-- Labels: session files, failed command followed by the same command later in the session.
+- Decision: should the agent retry this failed operation now, under the observed error AND the
+  captured relevant state (attempt history, exit status, elapsed time, and any state change)?
+- Labels: adjudicated retry episodes where the follow-up is demonstrably the same operation and
+  its result is observed; mark unknown/censored when state changed or the outcome is missing.
+- Unit: one failure episode, not every repeated tool-result row. Deduplicate retries within an
+  episode and split train/dev/held-out by session and operation family.
+- Primary outcome: fewer futile retries without suppressing a successful safe retry; compare the
+  complete policy with the existing retry behavior and the regex baseline.
```

#### V4 — Context bloat

**Why:** “Never referenced later” is hindsight, not proof of irrelevance, and “not reused” does not imply safe-to-remove. An output may be important evidence even if the agent does not quote a path or line later. More fundamentally, a context hook’s existence does not prove it can reclaim already-injected tool-result tokens at the needed time or preserve audit/debug semantics. First prove the exact hook lifecycle and reversible/safe semantics on a disposable session. Measure retained input tokens and task correctness, not just percentage of unreferenced outputs. R137–R139 also make a return to memory keep-precision judgments unattractive without a genuinely new source of signal.

**Change versus original:**

```diff
-- Decision: will the agent ever use this tool result again in the session?
-- Labels: later turns reference content from the result (path, identifier, quoted line).
-- Baseline: size + tool-type rules (large `cat`/`rg` outputs rarely reused).
-- Payoff: dropping never-used large results from context cuts input tokens every later turn.
-- Risk: this needs an omp context seam; omp's `context` hook exists, so it is buildable in our tree.
+- Decision: can a particular retained result span be compacted/omitted at a defined context
+  boundary without reducing task success, evidence traceability, or safety?
+- Feasibility first: demonstrate in a disposable fresh session that the exact supported context
+  seam receives the relevant result, can transform it before the next model request, and does not
+  mutate the durable session/audit record. If not, retire V4 without Jev calls.
+- Labels: task-level outcome and evidence sufficiency under a randomized paired replay, not only
+  later lexical references. “Not referenced” is a feature, never ground-truth irrelevance.
+- Baseline: byte/token threshold and tool/source-specific deterministic compaction; include no-op.
+- Payoff/bar: net input-token reduction at non-inferior task success and no increase in missing-
+  evidence or safety errors. Use only a shadow/replay until this is demonstrated.
```

#### V5 — Duplicate bead detection

**Why:** Exact/near duplicate detection is plausibly useful, but a title-overlap score is an impoverished baseline and “duplicate/superseded” close reasons are a selected subset. The proposal needs a clear intervention: flag for human review, never auto-close or suppress a bead on an unvalidated model score. Avoid labeling duplicate pairs with both members across train/test.

**Change versus original:**

```diff
-- Decision: is a new bead a duplicate of an open or recently closed one?
-- Labels: beads closed with duplicate/superseded reasons (tonight: ...).
-- Baseline: title token overlap.
-- Payoff: no duplicated pane work (several duplicate beads filed by the generator on 10-01).
+- Decision: should the bead author/reviewer inspect one specific existing bead as a possible
+  duplicate before dispatch? Jev may rank a bounded candidate set; it may not auto-close, merge,
+  or suppress work.
+- Labels: independently reviewed candidate pairs, including hard non-duplicates and near-duplicate
+  positives. Split by bead lineage/issue cluster so related pair variants cannot cross splits.
+- Baselines: exact normalized title, token overlap, and existing bead search workflow; compare on
+  the same pairs and measure reviewer-confirmed duplicates found per review minute plus false
+  duplicate burden.
+- Go/no-go: enough independently adjudicated pairs and an explicit acceptable false-positive
+  burden; otherwise NOT ENOUGH DATA. Keep a human accept/reject action in the workflow.
```

### 5. Reclassify V6 and V7; prefer deterministic verification and avoid premature routing

**Why:** V6 proposes comparing numerical claims to cited evidence, which is usually a parsing, arithmetic, provenance, and exact-equality task. The repository already has claim-check functionality and a retired claim-without-evidence rule (R130); a second Noul verifier risks duplicating a weak judgment surface. Make a deterministic parser/calculator the baseline and use Jev only for the irreducible semantic claim-to-evidence relation, if a labelled set demonstrates that the parser cannot handle it. V7’s assignment outcomes confound pane skill, task difficulty, available capacity, and assignment order. “Past success by assignee” is not causal evidence that rerouting improves completion or latency.

**Change versus original:**

```diff
-### V6 Verification-claim check (candidate, not yet assigned)
-- Decision: does a DONE callback's claimed number match the evidence it cites?
-- Labels: tonight's verifier outcomes (VERIFIED vs differs) on 40+ callbacks.
-- Baseline: none cheap; numbers mismatch by recount only.
-- Payoff: fewer verifier cycles; earlier catch of arithmetic slips (jev-r8dp sum error).
-- Risk: needs the cited evidence in the state, often too large; R130 shows claim judging is hard.
+### V6 Evidence reconciliation (candidate only after deterministic baseline)
+- First build/measure a keyless deterministic check for parseable counts, command results, and cited
+  artifact identity; compare the callback claim to its cited evidence, not only a verifier's summary.
+- Do not count `VERIFIED` as ground truth until independently adjudicated against source evidence.
+  Split by callback/session and freeze cited evidence references before any judgment.
+- Only test Jev on semantic entailment cases the deterministic checker cannot decide. Human review
+  remains the action for uncertain or high-impact claims; do not auto-approve from Jev.
+- Reuse/examine the existing claim-check contract and R130 evidence before proposing another rule.
```

```diff
 ### V7 Prompt-to-pane routing (candidate)
-- Decision: which pane/profile should take this bead (by past success on similar beads)?
-- Labels: bead outcomes by assignee.
-- Risk: N small, confounded by assignment order. Low priority.
+- Defer until assignment, queue state, task class, and outcome logging support a prospective
+  controlled comparison. Historical completion by assignee is confounded by task selection and
+  availability; do not treat it as a valid routing label. The action is advisory recommendation
+  with human override, and its outcome metric must include time-to-completion and quality, not
+  merely completion.
```

### 6. Turn “From PASS to ON” into a staged rollout with an explicit rollback and safety owner

**Why:** A 24-hour shadow is not automatically enough to label outcomes, cover rare cases, or prove an improvement. It may produce zero informative events. The current plan says “enforce only on the bar” without specifying which bar, what happens on model/API/hook failure, or who can stop rollout. Project guidance requires the positive and planted-negative paths in a fresh session; its ladder distinguishes seam loading from a real event firing. Hook parse failures have already disabled a live seam in this project, so syntax/runtime/load checks belong before shadow exposure, not only after editing.

**Change versus original (replace §5):**

```diff
-A passing vein becomes a surface only through the existing pattern: shadow (log-only) for 24 h on
-real traffic, blind label of the decisions it would have changed, enforce only on the bar, fresh-
-session proof both ways, inventory row, README row if user-visible.
+A passing offline/live experiment does not authorize enforcement by itself. Promotion requires:
+1. A named consumer, action, owner, explicit safe fallback for invalid/low-confidence/error/cap,
+   and a runtime kill switch where the seam can affect work.
+2. Keyless contract tests and an actual disposable fresh-session smoke proving load, positive
+   behavior, planted-negative behavior, privacy/logging constraints, and failure fallback.
+3. Shadow on real eligible traffic until the preregistered information/coverage criterion is met;
+   24 hours is a minimum/observation window only, never evidence of sufficient sample size.
+   Blindly label changed decisions and report unknowns separately.
+4. Human-reviewed canary enforcement on the predeclared cohort. Promote only when the held-out
+   harm and benefit bars still hold; automatically fall back to the incumbent on failures or
+   missing telemetry. Record an explicit rollback trigger and the operator who owns it.
+5. Update the expected inventory and README only for a user-visible, actually active surface;
+   preserve the model id, window, N, latency, cost, and boundary. Retire the candidate if its
+   consumer disappears or the bar fails.
```

### 7. Fix the portfolio stop rule and dispatch graph

**Why:** The current stop condition says failure of V1–V5 establishes that daily traffic offers no further new decision, despite V6/V7 being untested and despite the plan sampling only five design hypotheses. That is a logical overreach. “Maintenance” may be the right operational choice after this bounded wave, but label it a capacity decision, not a universal evidence claim. Also, the pane assignments and prerequisites are time-specific and now stale for V2/V3; the plan says five worker panes but assigns pane 6. Dispatch should use currently available capacity and dependencies, not hard-coded pane numbers. Each independent candidate can still proceed concurrently after shared dataset/label prerequisites are complete.

**Change versus original (replace §§7–8):**

```diff
-## 7. Dependencies
-- V1, V2, V3 run now (independent).
-- V4 waits on HazySpring finishing jev-1w52; V5 waits on CyanPeak finishing CI.
-- V6, V7 wait on at least one of V1-V5 finishing (fleet capacity), and V6 waits on V2's label work
-  (shared callback corpus).
-- Any PASS spawns its shadow bead (section 5), blocked by the vein's verification.
+## 7. Dependencies and dispatch
+- First reconcile existing evidence/bead states; V2/R140 and V3/R141 are not runnable candidates.
+- Assign one owner per candidate from currently available workers. Do not bind plan semantics to
+  pane numbers; record the owner and current task in the bead.
+- Candidate feasibility/label audit is a prerequisite to its bar and any live calls. Independent
+  feasible candidates may proceed in parallel only when their data, spend caps, and reviewer
+  capacity are independent. Shared callbacks or labels require one canonical frozen dataset and
+  one owner to avoid inconsistent joins.
+- A PASS creates a separate rollout task only after an independent verifier accepts its evidence;
+  a no-go closes only that candidate/design with the observed boundary and retry trigger.
```

```diff
-If all of V1-V5 end in FAIL, NOT ENOUGH DATA or BASELINE WINS, the honest conclusion is that this
-machine's daily traffic offers no further new Jev decision beyond the seven surfaces already on, and
-the fleet should be stood down to maintenance. That is a result, not a failure of the plan.
+If every candidate admitted to this bounded wave is FAIL, NOT ENOUGH DATA, or BASELINE WINS, stop
+this wave and report exactly those candidate/design/data-window results. Do not claim that no other
+useful Jev decision exists. The conductor may choose maintenance as the next allocation, but that
+is an operational choice, not an inference from an incomplete portfolio. Reopen a candidate only
+when its recorded retry condition is met; propose a new vein only with a named consumer, observed
+problem, and a keyless feasibility path.
```

## Recommended ordering

1. **Immediately reconcile and annotate status:** link R140/R141; check bead status; remove them from active work. Correct the inventory and spend/window wording. This is a factual repair, not another experiment.
2. **Tighten protocol and candidate cards before any new paid calls:** freeze labels, grouping, comparison, uncertainty/harm gate, data boundaries, and a wave-level call/spend ceiling.
3. **Run keyless feasibility first on V1, V4, V5, and V6.** V1 needs valid retry episodes; V4 first needs seam/lifecycle proof; V5 needs unbiased pair labels and a human-review action; V6 should measure deterministic reconciliation before any Jev call.
4. **Do not allocate V7 yet.** It lacks an adequately identified counterfactual and a low-risk operational consumer.
5. **Only after a candidate passes its frozen offline gate**, make a separate rollout decision using the fresh-session positive/negative proof and canary/rollback conditions above.

## Overall assessment

The strongest parts are the commitment to keyless feasibility before spend, pinned `jev-1.13.0`, one-question requests, explicit negative outcomes, non-author verification, and the willingness to treat baseline wins or insufficient data as real outcomes. Keep these. The largest improvements are not more candidate ideas; they are stale-state reconciliation, valid labels, paired operational evaluation, stricter evidence boundaries, and a rollout gate that proves the actual consumer path. With these revisions, the plan can discover useful decisions without confusing model accuracy, an observed proxy, and a live product benefit.
