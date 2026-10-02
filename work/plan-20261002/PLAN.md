<!-- 2026-10-02 Joshua: discovery, not refusal. See section 8 loss-depth rule. -->
# Jev Discovery Plan — 2026-10-02

Status: rounds 1-2 integrated (reviewer: gpt-6-luna via omp `claude` profile, REVIEW_R1.md, REVIEW_R2.md);
round 2 was additive (steady state). Consumer: the jev worker panes via beads. Retirement: frozen once
its beads exist.

## 1. Goal

Identify a real, recurring decision gap in this machine's daily workflow where a Jev decision
improves the downstream action. A candidate advances only if the end-to-end policy (Jev, its safe
fallback and its action threshold) improves a predeclared operational outcome over the strongest
eligible cheap baseline by a material, precommitted margin on live `jev-1.13.0` calls on data we did
not write. A deterministic baseline that wins is useful maintenance and ships as such, but it is not
a Jev discovery. No candidate is required to ship; an evidenced no-go is a valid result.

Why now: tonight's verified wins are extensions of decisions omp already made; every new kind of
decision tried on 2026-10-01/02 failed or lacked data. Joshua (2026-10-02): put the fleet on discovery
without ceremony.

## 2. Ground truth

### 2.1 Measured useful and active (verified by a non-author)

| Surface | Decision | Measured | Evidence |
|---|---|---|---|
| Gate cascade | destructive/exfiltrating bash? nimble first, paid Jev on flags, deterministic pre-rule | ~96% screened free; 0/950 clears harmful; 10/10 planted to paid; 0/1553 timeout-clears | jev-nr3c, jev-syje, jev-nbbm, jev-t3tk |
| Memory filter | recalled memory irrelevant? (drop only) | drop precision 0.978 held-out; median 797 tok/turn removed; 1.3 s vs 3.3 s | jev-wb7j, jev-s47b, jev-11qz |
| Web-result screen | tool result instructs the assistant? | live 52/54 caught, 0/59 clean withheld | jev-eo40, jev-rud1, jev-n4eu |
| find (native) | files that answer a query | 404 vs 1,861 tool tokens per located file | jev-04q2, jev-ynn7 |
| auto-thinking (native) | effort level for a prompt | 16% cheaper, equal or better success, hard tasks | jev-8qu6 |

Shadow (not yet enforcing): global web/injection screens (sample immature, jev-j0er). Idle by design:
smart stop. Retired/off: claim rule, web_search rerank, skill hint.

### 2.2 Closed candidates (do not re-propose without a new fact)

| Candidate | Verdict | Record |
|---|---|---|
| web_search rerank | turned off, no downstream opens | R134 |
| skill hint (lexical, semantic) | vein exhausted / refuted | R133, R135 |
| cass-hit rerank | not enough traffic (N=8) | jev-ygyp |
| needs-human enrichment | deleted, n=1 fragile | R136 |
| nimble for injection / webscreen / memory relevance | worse than Jev | uhc5, R138 |
| memory keep precision (rewording, conjunction, bundling) | model limit ~0.22 | R137, R139, jev-9n6h |
| conductor triage (V2) | FAIL 0.704 vs 0.75, missing fleet state | R140, jev-6c8n |
| long-runner prediction (V3) | 5/151,275 over 60 s, censored labels | R141, jev-uup3 |
| duplicate beads (V5) | 3 genuine pairs in 425 | jev-f5ig |

### 2.3 What the evidence says about Jev here

1. Good at binary or small-choice judgements whose answer is visible in the request text.
2. Good where error is asymmetric and a confident-only action is safe (drop, withhold, flag).
3. Weak in the "keep" direction and wherever the answer depends on state not in the request (V2).
4. Transport-sensitive: one question per request is the safe default (bundling moved boundaries).
5. Spend is small: about $0.32/day from the 7-day hook+native census (jev-r8dp; AGENTS.md's older
   ~$3/week is a different window). Label quality and latency constrain discovery, not money.
6. Downstream action is the payoff, not agreement (R134: ranked picks nobody opened).

## 3. Candidate contract (every vein, before ranking or dispatch)

Rank candidates by eligible unique decisions x measurable action headroom x probability the safe
intervention is correct; labels and quality are hard gates. Event rows are not decisions (gate-observe
17,963 rows vs 1,194 paid calls in 7 days); use complete UTC windows and unique-event denominators.
The wave cap is an upper bound, never a budget to fill.

Name: consumer and concrete action; unit of decision; label source and what the label actually means;
eligible population; false-positive and false-negative costs; cheapest deployed baseline; the
operational outcome measured (not only classifier score); and a retry condition. Drop the vein if a
cheap rule decides the action exactly and safely.

## 4. Live candidates

### V1 Retry decision (WildCarp, running since 04:15Z)
- Decision: should the agent retry this failed operation now, given the error and the attempt
  history, elapsed time and observed state change?
- Unit: one failure episode (repeated rows deduplicated). Split by session and operation family.
- Labels: adjudicated retry episodes where the follow-up is demonstrably the same operation and its
  result is observed; state-changed or missing outcomes are censored, not labels.
- Baseline: error-text regex (index.lock, timeout, 429, refused => transient) and current behaviour.
- Outcome: fewer futile retries without suppressing a retry that would have succeeded.
- Retry condition if FAIL: an episode corpus with captured pre/post state.

### V4 Context compaction of tool results (HazySpring, after jev-1w52)
- Decision: can this retained tool-result span be compacted or omitted at a defined context
  boundary without lowering task success, evidence traceability or safety?
- Feasibility first: in a disposable fresh session, prove omp's `context` seam receives the result,
  can transform it before the next model request, and leaves the durable session record intact. If
  not, retire V4 with no Jev calls.
- Labels: task outcome and evidence sufficiency in paired replays. "Not referenced later" is a
  feature, never ground truth. Not a return to memory relevance (R137-R139 closed).
- Baseline: byte/token threshold and tool-specific deterministic compaction; no-op arm.
- Outcome: net input-token reduction at non-inferior task success, no rise in missing-evidence errors.

### V8 Test selection for a diff (new, unassigned)
- Decision: given a diff, which registered suites (TESTS.md) must run locally before commit?
- Labels: CI history: for each pushed commit, which suites failed, joined to changed paths
  (40+ runs on 2026-10-01/02 alone, more in git history).
- Baseline: path-to-suite mapping from TESTS.md rows; run-everything as the safety ceiling.
- Outcome: local verification wall time saved at zero missed CI failures on the held-out commits.
- Risk: failures are rare per suite; power may only support a no-miss bound, not a speed claim.

### V9 Compaction keep/drop for conversation turns (new, unassigned)
- Decision: when omp compacts a session, which turns must survive verbatim?
- Labels: after a compaction, did the agent re-fetch or re-ask for content that was dropped
  (re-read of the same path, repeated command, "lost state" in the transcript)?
- Baseline: omp's current compaction plus recency rules. The `jev-compaction` skill already frames
  this decision: reuse its question rather than invent one.
- Outcome: fewer re-fetches after compaction at equal or smaller summary size.
- Risk: label noise; compactions per day may be few (feasibility check decides).

### V10 TTSR reminder applicability (new, R2; highest organic volume)
- Traffic basis: R132 census 2026-09-24..10-01: 1,447 organic ttsr injections across 36 rules, 534
  purpose=ttsr calls; one rule 491 firings with 0/26 applicable on blind review. Repeated traffic, not
  benefit, independent N or per-rule cost.
- Decision: for an already-triggered, currently active rule, is its reminder applicable to this exact
  event? Suppress only a high-confidence inapplicable reminder; invalid, low-confidence, timeout or
  unavailable answers keep current behaviour.
- Freshness precondition: satisfied by jev-pn7b (retired rules fire only in sessions started before
  retirement, 0 after); the eligible population is active rules in post-retirement sessions only.
- Keyless gate: join injection -> rule id -> triggering event -> next agent action; blind-label
  applicability from enough event context; truncated or blocked cases are censored; per-rule volume.
- Unit/split: one rule-injection episode, deduplicated; split by session and rule; include must-not-
  suppress applicable reminders and hard negatives; never pool low-volume rules to reach N.
- Baseline: the deterministic trigger alone (current behaviour) and a tightened trigger.
- Outcome: fewer inapplicable interruptions per eligible turn at no rise in missed applicable reminders.

### V6 Evidence reconciliation (deterministic first; Jev only for the remainder)
- Build a keyless parser/calculator that compares a DONE callback's numbers to its cited artifact
  (counts, SHAs, sums; tonight's jev-r8dp 0.10+2.12 slip is the motivating defect). Jev is tested only
  on semantic claim-to-evidence cases the parser cannot decide; human review stays the action.
- Reuse claim-check and R130 before proposing a rule.

### V7 Bead routing: deferred
- Historical completion by assignee is confounded; revisit only with prospective logging.

## 5. Protocol (every vein)

1. Keyless feasibility: freeze a reproducible eligible population, label provenance, base rate,
   censoring check and strongest cheap baseline; split by session/task/bead, not row; keep an untouched
   held-out set. Stop when labels, positives or power cannot support the decision (no universal N=60),
   or when a deterministic baseline meets the consumer's bar.
2. Before any live call, commit a preregistration: model `jev-1.13.0`, state and question, threshold
   and fallback, primary operational metric, baseline, margin, paired method and uncertainty bound,
   harm limits, eligible row hashes, split, call and spend cap, go/no-go rule.
3. Wave cap: at most 300 calls per vein and 1,200 calls for this whole wave.
4. Run Jev only on the preregistered held-out rows, paired with the baseline on identical rows; one
   question per request; log model, row hash, status, tokens, latency, spend per call; stop on
   401/402/403 or the cap; a timeout or error is never a model decision.
5. PASS needs the material operational improvement and the harm bound, not a point-score lead. Report
   eligible/attempted/scored N, base rate, paired counts, uncertainty, latency, spend, exclusions.
6. LOSS DEPTH: diagnose on development data, change one variable there, freeze, then confirm on a
   fresh untouched set at the original or stricter bar.
7. A non-author verifies the frozen arithmetic and sources before close.

## 6. From PASS to ON

1. Named consumer, action, owner, safe fallback for invalid/low-confidence/error/cap, kill switch.
2. Keyless contract tests plus a disposable fresh-session smoke: load, positive, planted negative,
   logging constraints, failure fallback. The hook must parse before any exposure (03:46Z incident).
3. Shadow on real traffic until a preregistered coverage criterion is met (24 h is a minimum, never a
   sample-size argument); blind-label changed decisions.
4. Canary enforcement with an explicit rollback trigger and owner; promote only if held-out harm and
   benefit bars still hold.
5. Inventory and README rows only for an active, user-visible surface.

## 7. Dependencies and dispatch

- Reconciled: V2, V3, V5 closed (section 2.2). Active: V1 (WildCarp). Queued: V4 (HazySpring after
  jev-1w52), V8 and V9 (next free workers), V6 deterministic part (any free worker).
- Each candidate's feasibility check precedes its preregistration; independent candidates run in
  parallel when data, spend caps and verifier capacity are independent.
- A PASS spawns a separate rollout bead only after independent verification.

## 8. Stop rule

If every candidate admitted to this wave ends FAIL, NOT ENOUGH DATA or BASELINE WINS, stop the wave and
report exactly those candidate, design and data-window results. This does not prove no other useful
Jev decision exists; choosing maintenance next is an operational decision. Reopen a candidate only
when its retry condition is met; propose a new vein only with a named consumer, an observed problem
and a keyless feasibility path.

Loss-depth rule (Joshua, 2026-10-02: "we're supposed to be going into discovery - not claiming things
are too hard"): NOT ENOUGH DATA or BASELINE WINS is not an exit until the owner has searched for more
real data (other repos' `.beads` and sessions, longer windows, all omp profiles, background-job
records) and tried the redesign the failure itself names. V2, V3 and V5 stopped after one look and are
reopened as jev-ztfe (fleet state in the request), jev-zezf (labels from background-job durations) and
jev-eruw (machine-wide ~59k-bead corpus).
