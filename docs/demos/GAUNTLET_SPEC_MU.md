# GAUNTLET_SPEC — the duel-lane gauntlet as a reusable method, with a hostile audit

**Status:** non-author extraction and critique (CopperCarp / pane 3, muse).
The conductor wrote nearly all of the method; this read is against it, not from it.
**Sources:** `docs/demos/PLAN.md` (§3c, §3h, §3i, §3k, §4d, §4k, §4l, §4o–§4q, §4u–§4z),
`docs/demos/RULING.md`, `NEGATIVE_EVIDENCE.md`, `docs/demos/QUEUE.md` (protocol, rules, Q32, stale-file section).
**Method of this audit:** every firing claim below cites the receipt that would prove it wrong;
two scout enumerations (self-catches N=22; UNASKABLE/authorship/tautology events) supplied the counts,
verdicts are mine. Where I could not locate a firing instance in the sources read, I say so —
absence-from-my-reads is not absence-from-the-lane, and the distinction is kept explicit.

**One-line verdict:** the gauntlet is real — its mechanisms fired repeatedly and changed outcomes —
but three of its rules have never fired, two fired only because a human chased what no gate required,
and its headline self-praise ("caught its own conductor eleven times") is an unenumerated aggregate
of exactly the class this method forbids. Corrected count and replacement wording in §9.

---

## 1. The ladder (extract)

Five rungs, cost rising ~10x per rung (§3c, `PLAN.md:198-272`). **A rung is a kill point, not a checkpoint.**

| Rung | Name | Cost | Gate |
|---|---|---|---|
| 1 | DEMAND | research only | §3b's four questions answered in writing with external evidence (who downloads, what pain voiced where, what maintained tool owns the niche, measurable before/after); score bar (see §3, corrected) |
| 2 | JEV SHAPE | reasoning | one sentence on why a chat model does this worse, surviving a non-author reading; generation/summarization/extraction value is disqualifying **plus** the §4l screen: does the corpus the candidate needs already exist on disk, unlabelled, right now? If no, price it before proceeding |
| 3 | THIN PROOF | days, one artifact | clean-clone verified by a non-author; ≥1 RED arm firing on a planted defect; receipt with stated denominators; cheapest installable thing answering "is the capability real", not the product |
| 4 | MEASURED LIFT | the number that decides | before-value, after-value, third-party reproduction command; **no verdict strings**; absolute thresholds only, never "beat a stochastic baseline"; lift must be large enough to change a stranger's behaviour |
| 5 | PROMOTION | its own project | all four: rungs 1–4 cleared each by a non-author; no candidate currently promoted; a named non-conductor owner; a stated kill criterion **for the project** |

**Ordering amendment (§3k):** before paying for rung 3, ask whether the rung-4 number can be
*estimated* without building. Yes → estimate first (pre-registered threshold + cheap estimate =
rung-4 kill at rung-2 cost). No → proceed, stating why estimation is impossible. **Split every
falsification into its label-free half and its labelled half** — the label-free half (denominators,
existence) runs first and may remove the need for labels entirely.

**Allowed outputs:** PROMOTED · HELD (blocked on a named prerequisite with retry condition) ·
RULED_OUT (named rung + evidence + retry condition, recorded in the negative ledger) ·
UNASKABLE (cannot be answered with available evidence — never a pass). A ruled-out candidate is a
deliverable; the evidence that kills cheaply outranks the code that would discover it expensively.

## 2. Authorship rules (extract + firing)

1. **Author cannot grade, falsify, or kill their own candidate** (QUEUE:43; §3c rung 1).
   *Fired, repeatedly, outcome-changing:* the 820-vs-550 self-score gap (demo-9 RECUSED, never admitted
   on the author's number); MU-H1 killed by a non-author census (R14); COD-H3 killed by its non-author
   (R15); COD-H2 clearances each signed by a non-author (RULING:17); demo-4 withdrawn as standalone by
   its own author. **This is the most-fired rule in the gauntlet and the least dispensable.**
2. **Conductor killing another pane's candidate needs non-author concurrence** (§3c rule 3).
   *No firing instance located in sources read.* The kills on record were executed or concurred by
   non-authors without visible invocation of this clause. Candidate for deletion-or-demotion (see §8).
3. **Labeller cannot set its own audit bar** (§4n → Q32 → §4p). *Fired once, strongly:* the
   labeller-chosen ≥18/20 was caught before labelling; pane 2 ratified the number but amended to
   stratified 5-per-stratum with a per-stratum ≥4/5 floor — strictly stronger, and aimed at the exact
   failure (a systematically mislabelled stratum averaged away) the audit exists to detect.
4. **Receipt author cannot accept its own provenance** (Q26, after §4b-CORRECTION). *Firing not verified
   in sources read* (Q26's execution state unclear from what I read). Pending, not dead — but a rule
   whose first use is still outstanding should not be cited as load-bearing yet.
5. **Role-concentration must be stated with the conflict named** (§4p: pane 2 holding 3 of 4 roles;
   neither assignment clean, choice defended on checkability grounds). *Fired once as disclosure;*
   note the follow-up: §4x later refuted §4p's *premise* (rule-application is mechanical) while the
   *mechanism* (the audit) caught the defect anyway — right conclusion, wrong reason, distinguished
   in the record. That distinction is itself a rule worth keeping: **record which half of an argument
   did the work.**

## 3. Pre-registration discipline (extract + firing)

**The rule:** thresholds, seeds, case IDs, and predictions committed before the run; blinding
conditions disclosed rather than assumed ("formed decisions before reading the other's" stated in the
receipt); a contrary result is a finding, never a failure.

*Fired, and every firing changed something:*
- MU-H1 falsification design (FALSIFY_MUH1_COD): pre-registered thresholds + label-free/labelled split;
  the label-free half killed at $0 (R14, §3l). The template for §3k.
- §4y prediction (7/7, 4–3): falsified by name with per-case reasoning (`d3aecaf`); exposed the
  scoped-vs-low-risk conflation. A prediction that survives is evidence; one that dies is a finding —
  both halves used.
- Clause prediction (7-to-pass, floor 5): failed *below its floor* (2 pass, 5 withhold); located the
  bottleneck move from rule strictness to missing record evidence (AMENDMENT 5). A floor that cannot
  fail is decoration; this one failed.
- §3s ruling pre-committed BEFORE v2.2 runs (explicit anti-post-hoc).
- Seeds committed before sampling, repeatedly (audit seed 20260920; Q45 draw seed; case IDs named
  before labelling — the per-case-ID rule, without which the Q51 join would have been impossible).
- Blinding disclosure twice (Q42 pane 2; Q53 pane 3 disclosing partial anchor exposure) — and the
  disclosed-against-anchor contradiction was correctly read as *stronger* evidence, not tainted evidence.

**Never-fired corner:** no pre-registered prediction is on record for any *rung-3 build gate* (RED-arm
thresholds, clean-clone bars were asserted in Q16's design, not pre-registered as falsifiable
predictions with floors). The discipline covered judgments and audits; builds got checklists. If the
method is reused, extend pre-registration to build gates or stop claiming it covers them.

## 4. Anti-tautology checks (extract + firing)

**The rule:** a test whose outcome is fixed by construction measures nothing. The family (§4k, four deep):
(1) RED-arm test firing on all 16 rows ("passed" automatically); (2) demo-1's 10/0 around a hand-written
heuristic; (3) MU-H2's canned asker keyed by gold label (20/20 that could not have been anything else);
(4) rung-4 labels as a deterministic function of the stratum-assignment pattern rule (a regex scores
100% by construction — the most consequential, at the top of the backlog).

*Fired, with a cost gradient worth preserving:* each instance was caught later-and-cheaper than the
last — re-test, rung-4 measurement, non-author grade *before any claim*, conductor cross-tab. The
standing breaker that generalizes: **prove discrimination in both directions** (QUEUE.md:328: the
corrected RED arm flags exactly 1 of 16 and exits 3; the fixed rubric crosses the same stratum into
opposite outcomes). An instrument that returns one verdict on every input has measured nothing (§4o) —
that sentence is the portable form of the whole check.

*Limitation found by hostile read:* all four catches were retrospective — the family was named at
instance 3, the general breaker at instance 4. There is still no *prospective* tautology screen (no
"before you run this test, state what observation would constitute failure" gate on rung-3 builds).
The method punishes tautologies reliably and prevents none structurally. That is the next rule to write.

## 5. Corpus screen (extract + firing)

**The rule (§4l):** rung-2 question — does the corpus this candidate needs already exist on disk,
unlabelled, right now? Yes → proceed. No → price it; candidate is UNASKABLE until the corpus cost is
stated, and that cost is part of the rung-3 estimate. Estimate the corpus before designing the
falsifier (§3k one layer earlier).

*Fired three times with discrimination* (§4o): COD-H1 UNASKABLE (2 of ≥30 transcripts), COD-H4
UNASKABLE-priced (4-hour build), demo-9 PROCEED (15 diffs, working baseline) — plus MU-H1's census as
the retrospective justification. Separates "data does not exist" (needs sourcing with a countable
target) from "code does not exist" (needs a build decision), which demand opposite responses.
**Keep as-is; it is the cheapest rule with the highest demonstrated yield.**

## 6. UNASKABLE (when correct vs evasive)

*Issued 5 times on record (scout enumeration):* rung-4-on-this-data (5→6 blockers, correct — terminus
confirms); UBS criticals (§4c, unresolved — correct *so far*, retry Q18 still open, which is what keeps
it honest); demo-8 re-entry without instances (correct — predicate stated, never satisfied); MU-H3
in-lane prevalence (correct — demoted to external prerequisite rather than re-asked); consolidated
rung-4 verdict (stands).

**When it is correct:** the verdict names the missing evidence *countably* (n=30 vs ≤5%, 2 of ≥30, 0 of
111 journals), ships a retry predicate with a shape (NEGATIVE_EVIDENCE rows carry them; predeclared
`method_gain` gates in R16), and survives the substitution test — "would the answer change if the
evidence arrived?" If yes, UNASKABLE. If the question would still be unanswerable, the defect is in the
question (undefined central term — §4x), and UNASKABLE is the wrong label: **the specification is the
blocker, not the evidence.** The lane learned this distinction the hard way (§4w→§4x reversal:
"sourcing question" retracted to "specification question"). Future lanes should check the question
*before* counting the evidence — the current method discovers question-defects only after exhausting
evidence-defects, which is the expensive order.

**Evasion guard that works:** "missing evidence yields UNASKABLE or HELD — never RULED OUT" (§3c rule 1)
plus "a retry condition that cannot be checked is a kill wearing a retry" (RULING:294). The one
violation on record (two "none" retry conditions plus unchecked ones in the ruling itself) was caught
by non-author audit (R5) — the guard guarding the guard.

## 7. Dry-queue / self-claim contract (extract + firing history)

**The rule as it stands:** units self-contained and claimable without asking (QUEUE claim protocol:
top-down, first-eligible, commit-the-claim-alone-immediately — `d14387e` swept three sibling files
proving why); four-leg callbacks, leg 1 first; on finish take the next unit yourself, never wait for
dispatch; blocked units declared as success; QUEUE DRY callback must name every considered unit and why,
*then* fall through to the default; **a unit dispatched in a packet MUST also be appended to QUEUE.md
in the same turn** (stale-file section) — because the fallback reads the file, not the packets.

*Firing history — the most instructive in the lane, because every firing was a failure first:*
- Self-claim existed in tick.md §2 and **did not take** (§4d: three dry-queue reports with eligible
  units open + waiting on a self-authored unit). Fix was mechanical, not attentive: next-two-units by
  ID in the packet's first two lines. **Took on the very next packet** (Q22 "starting now"). Lesson
  kept: *a rule buried in prose that a pane demonstrably does not execute is an unshipped rule.*
- Cause 2 (fast pane pulls dispatch) recurred *after documentation*; fix likewise mechanical
  (check-the-other-pane-first). Whether the mechanical fix fired after prescription: **not verified in
  sources read** — prescribed, not yet proven. Do not cite it as working.
- Dry-queue default proved **terminal, not generative** (pane 2 reached it and stopped, QUEUE:7) and
  then read a **two-hour-stale file**, correctly reporting four DONE units as open. Both defects fixed
  by rule (append-in-same-turn; staleness self-report clause). **The fallback failed twice and each
  failure improved it** — which is the mechanism working, but only because a pane *hit* the gap; no
  gate would have found either defect proactively.

---

## 8. NEVER FIRED — candidates for deletion

Graded strictly: a rule with no outcome-changing firing in this lane. Distinguished from
*not-yet-due* (young rules whose trigger never arose) and *dormant-by-design* (conditional rules
whose condition never fired). Only the first class should be deleted; the other two should be marked.

**Delete or demote (fired never, trigger arose and passed without it):**
1. **Conductor-kill concurrence (§3c rule 3).** Every kill on record was executed or concurred by
   non-authors on other grounds; no concurrence was ever *invoked* to license or block a kill. Either
   it constrains nothing (delete) or its trigger never arose because conductors never kill here
   (demote to guidance). Cost without evidence either way.
2. **"Resolving a hold is not raising a score" (QUEUE:45).** No instance on record of anyone
   conflating the two — holds were resolved (MU-H3 hold recovered, demo-6 conditional hold) without
   the rule visibly doing work. Mistake-proofing against an error nobody committed. Demote to a
   one-line reminder inside the HELD definition.
3. **Rung-5 gate as specified.** No promotion was ever attempted; sub-gates 2–4 (one-at-a-time,
   named owner, project kill criterion) were never exercised. Untestable in any lane that promotes
   nothing — which, if the method works, is most lanes. Mark *dormant-by-design*, and stop presenting
   the five-rung ladder as fully validated: **this lane validated rungs 1–4 and the refusal of 5.
   Rung 5's gate is untested doctrine.** The honest diagram has four tested rungs and one grey box.

**Not-yet-due (keep, mark the trigger):**
4. Most retry predicates (R14 legacy-repos, R15 T1/T2, demo-8 dual condition). Young, stated
   checkably — the property the method needs. The one that fired (R6→R12, nine minutes) proves the
   machinery works when the world cooperates.
5. Provenance authorship bar (Q26). Created, first use outstanding. Keep with the caveat in §2.
6. Manifest-design rule (carry bytes, not coordinates). Specified and priced, implementation is
   project work. Keep; its first test is someone else's unit.

**Dormant-by-design (keep, stop implying validation):**
7. Third-pane restoration of the two-grader gate (§3h retry). Correct conditional, trigger absent.
   Note what §3h models instead: **the lane deleted its own dead gate rather than venerating it** —
   "a gate nothing can satisfy is not a high bar, it is a dead gate." That deletion is the method's
   best self-maintenance event and should be a standing rule: **every gate ships the condition under
   which it is re-examined, and gates nothing can satisfy are removed, not worked around.**

## 9. THE ELEVEN — adjudication of "caught its own conductor eleven times" (RULING:526)

**Finding: the number is unverifiable from artifacts, and I checked.** The string "eleven" occurs four
times in-lane: LangChain's eleven *lines* (PLAN:1862, unrelated), pane 2's eleven-*word* answer
(PLAN:2386, unrelated), **eleven of fifteen disagreements** (PLAN:4305 — the fresh-sample analysis,
a different eleven), and the claim itself. **No artifact enumerates eleven conductor-catches.**
The claim is an unenumerated aggregate — a per-case conclusion drawn from an aggregate impression —
of exactly the family §3w polices and §9's unverifiable-claims finding constrains. It should never
have been written in that form, and its position (the rhetorical climax of "why PROMOTED 0 is the
deliverable") is where rigor was most owed.

**Auditable counts** (scout enumeration of PLAN.md: 10 CORRECTION headings + 12 other explicit
self-catches; trigger split 12 pane/agent, 8 self re-read, 2 human):
- **22 instances** of conductor-error-caught-and-recorded. Too broad (includes self-audits and
  Joshua's direct corrections, which are the conductor checking itself and a human checking the
  conductor — neither is "the method catching").
- **10 CORRECTION headings.** A count of *sections*, not catches — and one of them (§3m-CORRECTION)
  was itself corrected for overshoot, so headings double-count at least once.
- **12 pane/agent-triggered catches.** Closest to the claim's spirit, still not eleven — and it
  credits the method with #19 (ask-the-pane), which was an *unwritten* habit, not a rule.
- **3 recurrence families covering 10 of the 22:** over-kill on first reason (B1/demo-6/incumbents),
  citing-without-opening-the-control (§3m/§3w/§4b/§4y/§3o — five times the same error),
  adjacent-things-called-identical (B1/convergence headline). **Eleven recurrences of few errors is a
  weaker claim than eleven distinct catches, and the record supports the former:** the conductor's
  modal failure is citing a number without opening its control, caught five times, still recurring.

**The two-elevens collision, flagged:** PLAN:4305's "eleven of fifteen" (one-sided escalations) and
RULING:526's "eleven times" (conductor-catches) are independent counts sharing a number in the same
document set within days. Either coincidence — or the second absorbed the first by availability, which
would be §3o's manufactured-corroboration shape wearing a new number. I cannot distinguish these from
inside the lane; that inability is itself the finding. **Numbers that arrive without enumeration must
be treated as contaminated until counted, no matter who wrote them.**

**Replacement wording, offered for the consolidated verdict:**
> "…and a method whose mechanisms (non-author audit, pre-registered predictions, census, blind
> re-decision) caught conductor errors on record twelve times across three recurring defect families —
> over-killing, citing-without-reading, and calling-adjacent-things-identical — with the citing
> defect recurring five times and still unextinguished."

Twelve, not eleven; families named; recurrence admitted; the live defect stated. If that sentence
embarrasses, good — it is the only form of the claim this lane's own rules permit.

## 10. HUMAN-CHASED — rules that fired only because someone chased, not because a gate required it

These are real catches with no mechanism behind them. Each needs a gate or an honest "diligence" label:
- **R10 (fleet monitor):** the conductor read the live crontab himself after building a redundant,
  inferior script. The generalized rule ("grep crontab + ~/.local/bin before writing lane infra")
  exists only as ledger prose. No gate forces it; the next conductor-side tooling impulse will not
  trip anything.
- **R12 (grep-for-expected-line):** a near-miss caught mid-command by the conductor's own suspicion,
  one step from a false "fixed" record. The AGENTS.md producer-truth procedure now encodes it —
  *this one got its gate.* Cite it as the model: near-miss → standing procedure, same turn.
- **§3o (manufactured corroboration):** caught on self re-read *before* being recorded — "the only
  reason it is a footnote instead of a correction." No mechanism looks for framing echoes in dispatch
  packets. The Q-unit author and the evidence reader are the same party by construction; a
  frame/echo check (does this unit's instruction presuppose its expected finding?) has no owner.
- **Hero R13 (three asks):** conductor rejected two HERO-BLOCKED reports lacking the step, forcing the
  verbatim-output diagnosis. "Report the step, not the verdict" is enforced nowhere; the next
  terse-blocked report will cost the same three asks.
- **§3t survey / R16 controls:** the conductor opened the report's controls himself (regex floor,
  sentinel table). Q11 (census headline numbers) *is* the mechanized form and it fired (§3w) — so
  this one partially graduated: instinct first, gate after. That ordering (chase → gate) is fine and
  should be named as the intended lifecycle: **every human-chased catch must either graduate into a
  gate within the lane or be recorded as unmechanized diligence, not silently banked as method.**

## 11. Cost note (the hostile part the method already admits)

QUEUE:49 states it plainly: *"The lane has ~350 KB of analysis and one measurement."* The gauntlet's
overhead is its largest unmeasured cost — no receipt prices the conductor's own writing time against
the kills it bought. §3k and §4l are cost-control rules that fired (MU-H1 $0 kill; $0 falsifiers as
standard; price-before-build as norm), and the 65–110-minute spec pricing extends the discipline to
human time. But the method prices everything except itself. A future lane should carry one standing
unit: **price the lane** — conductor-hours per ruling, panes' idle fraction (Cause 1–5), bytes of
analysis per measurement. The lane that measures everything else and not its own cost has a hole
exactly where its pride is.

## 12. Adoption checklist (what a future lane takes, in order)

1. Claim protocol + self-claim-first-two-lines + commit-the-claim-alone (dry-queue terminal finding
   makes this non-optional in a shared worktree).
2. Append-in-same-turn for any dispatched unit; staleness self-report clause on every shared file.
3. Authorship exclusions before any score/label exists (grader, labeller-vs-auditor, receipt-acceptor);
   state the residual conflict explicitly (§4p model) — and distrust your own premise for it (§4x model).
4. Pre-register thresholds, seeds, predictions *with floors that can fail*; blind by disclosure.
5. Label-free half before labelled half; corpus screen before falsifier design; rung-4 estimate before
   rung-3 build (§3k/§4l ordering — the two highest-yield rules on record).
6. UNASKABLE with countable missing evidence + checkable retry; HELD with named next measurement;
   kill only with citation + non-author concurrence + retry predicate.
7. Tautology breaker per test: state the failure observation in advance; prove discrimination both ways.
8. Negative ledger with the R12 lesson: exact-failure counts over upper bounds refused honestly
   (the C5 addendum: "40 is an evidence-risk upper bound, not a fabricated exact count").
9. Standing price-the-lane unit (§11). No exemption for the method.
10. Re-examine §8's three deletions within one session of adoption: concurrence rule, hold/score
    reminder, rung-5 gate. What has not fired by then goes.

---

*Receipt: Q55 (this file is the output). Scout inputs: self-catch enumeration (22 instances,
10 headings, 3 recurrence families) and rule-firing enumeration (5 UNASKABLE, 12 authorship events,
4-family tautology) — counts used, verdicts mine. No predictions were pre-registered for this unit
(extraction, not measurement), and none are claimed.*
