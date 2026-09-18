# Duel-1 cross-score: COD on corrected CC ideas

Bead: `jev-demo-loop-a1q`
Role: arms-length, different-lineage grader of the corrected
`WIZARD_IDEAS_CC.md`
Ground truth: `docs/demos/USAGE-MAP.md`, the local compaction/foundation receipts, and
`AGENTS.md` §4

The file was corrected after pane 3's first score: the A/B has three questions, not four,
and CC-1 now names deterministic extraction → Choice over candidate lines → Noul
verbatim check. I score the corrected proposal, not the earlier prose. Unit 3's audit
also found a separate numeric error in CC-4's “33 points worse” wording: the mapped
accuracy difference is 18.7 percentage points.

## Summary

| Idea | COD score | Pane 3 score | Difference | One-line verdict |
|---|---:|---:|---:|---|
| CC-1 fact-ledger companion | **845** | 740 | +105 | The corrected mechanism turns the best decision question into a dispatchable design, but it is still unbuilt. |
| CC-2 claim-check pre-commit lane | **820** | 850 | −30 | Tight and useful, but message-only scope plus no-key skipping limits the safety claim. |
| CC-3 routing backtest | **840** | 830 | +10 | Strong read-only money experiment with the best deterministic RED arms in its category. |
| CC-4 signals-not-verdicts starter | **710** | 800 | −90 | Correct lesson, weak near-term readiness, and its “33 points” number is wrong. |
| CC-5 context-admission screen hook | **855** | 880 | −25 | Best rollout shape, but per-read cost and the unproven omp seam prevent an 880. |

**Strongest: CC-5 at 855.** Shadow-first, a blind arm, and a both-directions page
classifier make its characteristic failure observable before enforcement.

**Weakest: CC-4 at 710.** It is a good external template but asks this lane to build and
calibrate a labelled classifier before the lane has the required corpus; its headline
“33 points worse” also fails the claim audit.

No two ideas merge. CC-1 and CC-2 both protect written claims, but one preserves dropped
fact bytes while the other verifies staged claims against receipts. CC-3 and CC-4 both
measure model choices, but routing estimates cost counterfactuals while signals fit a
labelled classifier.

## CC-1 — fact-ledger companion

**Score: 845/1000 (+105 versus pane 3's 740).**

### Truth and citation

The §14 citation is genuine. Usage Map §14 says relevance pruning loses verbatim recall
and should pair with a fact ledger or yield to summarization. The local A/B receipt
supports the motivating observation: three questions existed, Arm A scored 1/3, and the
summary Arm B scored 3/3.

The corrected file fixes both defects pane 3 identified. It records the denominator
correction (`WIZARD_IDEAS_CC.md:18-19`) and now names the pipeline explicitly: deterministic
candidate extraction, Choice over the supplied candidates, then Noul verbatim checking
(`WIZARD_IDEAS_CC.md:74-82`). That is a real mechanism, not a prompt-shaped gesture.

The correction does not create implementation evidence. The extractor, source byte-range
contract, and third-arm receipt are still greenfield. The local score is a judgment, not
a new A/B result.

### Usefulness, artifacts, complexity, readiness

Highest decision value: this can decide whether the compaction hook should ship at all.
It reuses the fixture, adapter, and A/B receipt shape, so readiness is materially better
than a new generic template.

- **Install:** `jev-fact-ledger` CLI/module with deterministic extraction and a declared
  `armC` or a separate merged receipt. Do not claim the existing scorer is unchanged if
  it gains an arm.
- **Tests and RED arms:** missing answer line → recall miss; non-byte-identical quote →
  refuse; source id/range mismatch → refuse; satisfying q1–q3 ledger → score at least
  the declared comparator. A negative result is a valid shipped outcome.
- **Receipt:** transcript SHA, source message/range for every quote, ledger hash, arm
  scores, byte sizes, model/version, and exact question denominator.
- **EVAL row:** state whether the result reached an omp seam, what extractor grammar was
  covered, and that a three-question fixture is not general recall evidence.

Complexity is justified if extraction stays structural. A generator model would recreate
paraphrase risk and destroy the idea's strongest invariant.

## CC-2 — claim-check pre-commit lane

**Score: 820/1000 (−30 versus pane 3's 850).**

### Truth and citation

The §2 citation is genuine: Usage Map reports `jev_verify` catching a contradicted claim
at confidence 1.0. The observed form-versus-substance gap is plausible and useful. The
proposal's exact RED arms—false `8/8` against `passed=7,total=8`, missing artifact, and
no-key/API skip—are stronger than a regex-only check.

I mark it below pane 3 because the proposed enforcement surface is narrower than the
lane's claims. Commit subjects rarely contain the substantive numbers; bead bodies,
receipts, EVAL rows, and close reasons do. The no-key path exits 0 with
`CLAIM_CHECK_SKIPPED`, which is operationally necessary but means a green commit does not
mean its claim was checked.

### Usefulness, artifacts, complexity, readiness

High usefulness and good readiness: it reuses the existing `githooks/` and
`core.hooksPath` mechanism rather than introducing a daemon.

- **Install:** one idempotent hook install through the existing hook path; report whether
  the paid check ran or was explicitly skipped.
- **Tests and RED arms:** wrong numerator/denominator → refuse; missing artifact → refuse;
  malformed evidence → refuse; truthful claim → silent pass; unavailable key → named
  skip with no mutation. Add bead-body and close-reason fixtures before claiming lane-wide
  coverage.
- **Receipt:** claim text, artifact path/hash, parsed values, verdict, skip reason,
  model/version, latency, and false-positive rate over a bounded commit window.
- **EVAL row:** distinguish “hook ran” from “all lane claims are covered”; document the
  no-key bypass and the exact claim grammar.

The complexity/payoff ratio is good, but the scope must not quietly expand from commit
messages to every document in the lane.

## CC-3 — routing backtest over our omp logs

**Score: 840/1000 (+10 versus pane 3's 830).**

### Truth and citation

The §4 citation is direct in Usage Map: upstream reports −60% versus full-frontier on
237 turns, $0.00003 and 0.6s per decision, fail-open, kill switch, and local log. Unit 3
found the pinned upstream checkout is not present locally, so those upstream values remain
UNVERIFIABLE here; the proposal correctly treats them as prior art rather than our result.

The corrected design is a read-only backtest over our actual omp logs. Its all-hard,
all-trivial, malformed-line denominator, and two-run determinism arms are exactly the
right RED/sanity ladder. The small uplift over pane 3 reflects that stronger falsifier
set, not a claim that the upstream metric is verified.

### Usefulness, artifacts, complexity, readiness

Highest direct dollar value and low blast radius because it never routes live traffic.
The input exists on disk, but the backtest itself is not implemented; price-table and
model-identity contracts remain work.

- **Install:** one command accepting a transcript and committed price table; refuse
  missing input or unknown model ids.
- **Tests and RED arms:** all-hard → approximately zero savings; all-trivial → bounded
  maximum; malformed event → `UNPARSED` denominator row; repeated offline run → identical
  receipt; absent price row → ERROR rather than `$0`.
- **Receipt:** transcript hash, turns, parsed/unparsed counts, per-turn routing decision,
  saved-cost estimate, latency, model/prices versions, and threshold.
- **EVAL row:** name the replay window, the oracle proxy, human spot-label coverage, and
  the fact that counterfactual savings are not realized savings.

Keep it replay-only. A live router would be a different, higher-risk demo.

## CC-4 — signals-not-verdicts classifier starter

**Score: 710/1000 (−90 versus pane 3's 800).**

### Truth and citation

The §9/§13 citation is directionally genuine: Usage Map records the phishing-bench
comparison, five signal questions, logistic regression, AUROC/ECE, fixed rule, and label
requirements. The cited upstream checkout is not present locally, so Unit 3 could not
independently rederive those metrics. More importantly, the corrected idea's line 211
says the verdict-only approach is “33 points worse”; 81.3−62.6 is 18.7 percentage
points. That is WRONG, not a harmless rounding.

The self-falsifying RED arm is excellent: if the signal model does not beat the
verdict-only baseline, the template refuses to report. It still does not solve the
near-term data problem. The MUSE and CC texts acknowledge that local A/B evidence is one
transcript, three questions, and four calls—not a labelled classifier corpus.

### Usefulness, artifacts, complexity, readiness

Useful as an external template and eventually useful to this lane, but low immediate
readiness. A synthetic fixture can prove the pipeline runs; it cannot prove transfer to
our support or resume data.

- **Install:** one deterministic template command that declares schema, split, seed,
  minimum labels, and fixed-rule baseline.
- **Tests and RED arms:** verdict-only baseline must lose or the run refuses; miscalibrated
  probabilities fail ECE; below-minimum labels → ERROR; shuffled labels → no-signal refusal.
- **Receipt:** dataset hash, row count, split/seed, signal questions, coefficients,
  baseline, AUROC/ECE/bins, model versions, and refusal reasons.
- **EVAL row:** synthetic-only boundary until a predeclared labelled corpus exists; cite
  the external source and license without presenting its metrics as local evidence.

The idea deserves a later experiment, not an 800-level readiness score today.

## CC-5 — context-admission screen hook

**Score: 855/1000 (−25 versus pane 3's 880).**

### Truth and citation

The §1 citation is genuine for injection screening: Usage Map reports the 0.99 hidden
instruction witness while preserving page readability. §12 supplies the proposed blind
corpus size of 662 injection messages and 200 vulnerability pairs, but the pinned source
checkout is not present locally, so those external counts remain UNVERIFIABLE here.

This corrected CC version is materially safer than the MU wording: it proposes injection
screening, shadow-first rollout, and an explicit cost-per-read receipt; it does not claim
that sending raw credential material to Jev is a secret guard. The both-directions test
(flag the instruction and classify the page as real) catches the page-blocker failure.

### Usefulness, artifacts, complexity, readiness

High security value and the best rollout discipline of the five. The deduction is for
unproven omp hook reachability, per-read paid latency, false-positive cost, and absent
local blind-corpus evidence. Shadow mode reduces blast radius but is not enforcement.

- **Install:** idempotent project/profile-aware hook plus `jev-screen` CLI; shadow by
  default and an explicit human-approved enforce flip.
- **Tests and RED arms:** embedded instruction must flag while page remains real; held-out
  corpus arm must be genuinely blind; ordinary docs must report false-positive rate;
  malformed Jev answer and unavailable API must follow declared shadow/fail-safe policy.
  A clean-page comment or silent-path regression must be RED.
- **Receipt:** corpus slice hash, threshold, class counts, false positives, cost per
  screened read, latency, model version, and shadow/enforce mode.
- **EVAL row:** name the actual omp seam and rung; shadow evidence is not an enforcement
  claim, and no real secret belongs in the corpus.

Do not add a credential-classification branch unless it adopts the Unit 1 steelman:
local detection/redaction before Jev, with raw credential bytes never sent externally.

## Conclusion

The corrected CC file is substantially stronger than the version pane 3 scored. CC-1
gets the largest increase because its mechanism now has a deterministic first stage and
its denominator is corrected. CC-4 gets the largest decrease because the corrected
numeric claim is still wrong and the greenfield/label boundary is immediate. CC-5 remains
the strongest candidate, but 880 would overstate readiness while the seam, cost, and
blind-set evidence remain unproven.

**NO-CLAIM:** I did not implement or run any CC idea, hook, classifier, backtest, or live
validation. These are independent judgment scores against the corrected proposal and
available receipts, not measurements.
