# Duel-1 cross-scores: muse grader on the Claude file (CC-1..CC-5)

Grader: CopperCarp (pane 3, muse lineage; non-author). Scored against
`docs/demos/USAGE-MAP.md` (14 sections, SHAs as pinned 2026-09-18),
`compaction/runs/replay-big-20260917.json`,
`compaction/runs/ab-20260917.json` (`questions: q1–q3` at lines 85–101,
`armA.score 1` vs `armB.score 3`, `verdict "B wins"`), and AGENTS.md §4.
Receipt numbers in the CC file verified line-by-line; the two discrepancies
found are quoted with line numbers below. No scoring of my own file was
re-read for this task.

## Summary

| Idea | Score | One-line verdict |
|---|---|---|
| CC-5 admission screen hook | 880 | Best-engineered proposal in the file; shadow-then-enforce is the rollout done right. |
| CC-2 claim-check pre-commit lane | 850 | Tightest mechanism; checks substance where two installed lanes check form. |
| CC-3 routing backtest over our logs | 830 | Read-only money with inputs on disk; one moving-model wrinkle. |
| CC-4 signals-not-verdicts starter | 800 | Superb self-falsifying RED arm; greenfield, so readiness is lowest. |
| CC-1 fact-ledger companion | 740 | Highest decision value, but its central mechanism is unspecified and it miscounts the fixture. |

**Strongest: CC-5.** Deciding sentence: it is the only idea whose test plan
would catch its own characteristic failure — a page-blocker masquerading as a
screen (the both-directions trigger: flag the injection *and* classify the
page as real).
**Weakest: CC-1.** Deciding sentence: Noul/Choice *judges*; it does not
*extract*, so the ledger's first stage is a generator the proposal never
names, prices, or fail-safes.

No two ideas are the same in different clothes. (Long-list #14 was already
folded into #2 by the author, correctly.)

---

## CC-1 — Fact-ledger companion — 740

**Citation (§14): genuine.** The standing lesson ("pair with fact ledger")
is quoted accurately, and the mechanistic reading of armA's answers — the
dropped bytes carried the facts (`"The saved result for reading saa is not
present in the supplied context"`) — is the sharpest single observation in
either duel file. Receipt numbers (179→24, 13→8, 2333→1292, 4188 vs 1241,
1 vs 3) all verify.

**Factual error, three times:** line 15 claims "4 recall questions", line 66
"re-score **the same four questions**", line 91 "the four existing
questions". The receipt's `questions` array is q1–q3 only
(`ab-20260917.json:85-101`), matching the three grade entries per arm. The
pass criterion ("score ≥ arm B's 3") still parses against 3 questions, so the
design survives — but the file opens by claiming the receipts were read
first (lines 9–17), and the count is wrong in the idea that depends on those
receipts most.

**Central mechanism unspecified:** "extract a **byte-exact fact ledger** …
with a Noul/Choice pass" (lines 64–66). Jev's Noul/Choice primitives return
constrained judgments over *given* state; neither extracts quoted spans.
Something must first enumerate candidate quotes — a generator model (new
cost, new paraphrase risk: the exact failure the byte-identity RED arm
guards), or deterministic value-pattern enumeration with Jev judging
keep/drop per line (which is pruning at finer granularity — the thing that
just lost 1–3). The proposal's excellent RED arms (omission-trigger,
byte-identity-refuse, publishable-negative) guard stages 2+ of a pipeline
whose stage 1 is unnamed. Related tension, lines 71–73: "reuses
`compaction/ab/run-ab.ts` **unchanged** as the scorer, **and** emits a third
arm into the existing schema" — an unchanged scorer cannot emit a new arm.

**Shippability otherwise high:** fixture + scorer + schema owned (best
readiness of the five); "publishable either way" is the correct fail-safe
for a decidable question; no new gates, debt confined to `compaction/`.
Decision value is the highest in the file (does demo-1 ship fleet-wide?).

740 = genuine citation + best readiness + highest decision value, minus the
only factual error in the file and the only unspecified central mechanism.

---

## CC-2 — Claim-check pre-commit lane — 850

**Citation (§2): genuine, and the premise checks out.** `jev_verify` at
confidence 1.0 is as quoted, and `close-evidence-gate` is real
(`GATES.md:58`, `foundation/gates.d/50-house-gates.sh:6`) — the form-vs-substance
gap (lines 106–108: "Both check **form**. Nothing checks whether…") is accurately
observed, not invented.

**Mechanism is the tightest of the five.** The extraction step the idea
needs — (number, unit, cited artifact) triples from a terse commit message —
is regex-plausible, leaving Jev exactly the job §2 measured (claim vs
evidence). The fail-safe design is what lifts this to 850: no-key ⇒ named
`CLAIM_CHECK_SKIPPED`, exit 0 (a pre-commit lane that blocks the fleet when
a paid API is down is unshippable, and the file says so), plus the missing-
artifact arm refusing instead of reporting "no claims found" (the
empty-scan-set rule, correctly applied). Five healthy shapes silent mirrors
the staged-deletion lane's proven shape.

**Ceiling worth naming:** the lane checks commit *messages*, but the lane's
substantive claims live in bead bodies, EVAL rows, and receipts — the
subject rarely carries the number worth checking. The EVAL-row
false-positive-rate criterion (line 137) partially answers this; extending
the lane to close reasons later would complete it. A ceiling, not a flaw.

**Debt:** one lane on an installed mechanism, no daemon. Lowest added
complexity of the five. Readiness high (mechanism installed twice).

---

## CC-3 — Routing backtest over our logs — 830

**Citation (§4): genuine.** −60%, 237 turns, $0.00003/0.6s, fail-open, kill
switch, decision log — all as mapped, and "upstream backtested *their* 237
turns" correctly frames the unanswered question.

**Design is sound and the RED arms are well chosen:** all-hard log ⇒ ~0
savings (estimator honesty), all-trivial ⇒ near-max, malformed lines counted
as `UNPARSED` in the denominator, determinism across two runs. Read-only
starting position is strictly safer than the live router and costs nothing
to learn from.

**One methodological wrinkle,** line 168: "decisions come from recorded Jev
answers in the fixture; the live arm is one budgeted pass to **confirm the
recorded answers still hold**." Against a moving `jev-latest`, a later pass
that "confirms" old answers is the golden-regeneration reflex wearing a lab
coat — AGENTS.md's oracle rule ("our own prior run is not an oracle") says
to pin the model version and record drift, not to re-validate fixtures into
greenness. The idea's own ship criteria already demand model versions in the
receipt, so the fix is one sentence; but the sentence is missing.

**Value vs complexity:** the only idea that pays in named dollars, at one
bin + receipt of debt. Inputs on disk (yesterday's transcripts are today's
backtest corpus). 830, held below CC-2 only because it optimizes cost where
CC-2 defends correctness.

---

## CC-4 — Signals-not-verdicts starter — 800

**Citation (§9 + §13): genuine and complete.** 62.6 vs 81.3, 95.1%/0.988/
0.027, 89.5% fixed rule, 100–10k labels, 20+-point shift collapse — every
number resolves, and citing both source repos *with licenses* in the ship
criteria follows the lane's attribution rule without being asked.

**Best RED arm in the file:** the verdict-only baseline must lose on the
shipped fixture "or the template refuses to report (its thesis is
falsifiable and it checks itself)" (lines 196–198). A demo that refuses to
run when its own thesis stops holding is the anti-reward-hacking shape this
lane preaches. Minimum-rows ERROR and the ECE gate are correct companions.

**Why not higher:** readiness is the lowest of the five — a greenfield
template ("bring a labelled CSV") with no working code in tree, and its
primary user is the AI space, not this fleet. The "us second" line (triage
surfaces later) is honest deferral, correctly ranked fourth by its own
author's bias. Implementation note, unscored: fitting logistic regression
needs either a new dependency via `uv` or a hand-rolled IRLS — say which in
planning so the "one HTTP client" leanness claim stays true.

---

## CC-5 — Context-admission screen hook — 880

**Citation (§1 + §12): genuine.** 0.99-while-still-a-real-page and the
662+200 blind corpora both resolve; the §11 cross-reference for graded
decisions (line 227) is a legitimate use of the scores→actions shape, not
decoration.

**Best-engineered proposal in the file, across four independent choices:**
(1) the both-directions trigger — embedded-instruction flagged *and* page
classified real — which is the only test here that would catch the idea's
own characteristic failure; (2) a genuinely **blind** arm (held-out slice ≠
threshold slice); (3) shadow-first with a measured false-positive rate, the
enforce flip reserved as "a separate, human-approved change with its own
receipt" (lines 236–237) — the correct rollout for a hook on the
highest-frequency event in a session; (4) cost-per-screened-read in the
receipt, because a per-read Jev lane that costs more than the router it
protects is a net loss and the file refuses to hide that line.

**Caveats, both disclosed by the author:** blast radius is maximal (admission
blocking runs on every read), hence last place "deliberately" — I concur
with the sequencing (ship after a live per-event lane teaches its cost).
The "shadow = L3 at best" hedge (line 240) is honest: logged would-blocks
are trip evidence, not enforcement.

880 = strongest technical design + honest sequencing + the cost line its
rivals could have omitted.

---

## Grading notes (method)

- Receipt re-verification: replay-big `eventsIn 179 / messagesIn 24 /
  messagesBefore 13 / messagesAfter 8 / charsBefore 2333 / charsAfter 1292 /
  kept 0 / resultsTrailing 0 / failures []` — CC lines 11–13 exact (45% is
  fair rounding of 44.6%, matching the map). A/B `liveCalls 4 /
  jevRequests 1 / armA.contextBytes 4188 / armB.contextBytes 1241 /
  armA.score 1 / armB.score 3 / verdict "B wins"` — exact except the
  question count (see CC-1).
- Miscitation cap (400) not triggered: every § claim resolves; the CC-1
  deduction is for fixture miscount + mechanism gap, not citation fraud.
- Score spread 740–880: the gap between CC-5 and CC-1 is design
  completeness, not lineage. The author's declared bias (lines 261–265,
  including conceding the #4-over-#1 inversion) is commendable and did not
  move any score.
- NOT verified (no-claim): ran none of the five ideas' proposed harnesses;
  scores are judgment against the cited sources, not measurement.
