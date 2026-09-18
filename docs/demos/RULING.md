# RULING — which ideas deserve their own deeply-planned project, and the evidence for the rest

**Derived 2026-09-18 from `docs/demos/STATUS.tsv`, not from prose.** Every candidate below cites a
receipt that `scripts/lane-status.sh` verifies exists on disk; the script exits 3 if any does not.
Reasoning lives in `docs/demos/PLAN.md`; refutations live in `NEGATIVE_EVIDENCE.md`.

**State at ruling: 17 candidates · RULED_OUT 4 · CLEARED 5 · HELD 8 · PROMOTED 0.**

---

## THE RULING

**Two candidates earn their own deeply-planned project. Neither earns a build first.**

### 1. COD-H2 pre-action abstention — **first phase: SPECIFICATION**

**It cleared more of this gauntlet than anything else and every clearance was signed by a
non-author.** Blind demand **905** (top of 17). Rung-2 structure against a **shipped** incumbent
proven **binary** by source-read — `AutoModeMiddleware`'s own docstring: *"it does not request human
approval"* (§3u). Rung 3 **in full**: real client that exits **`rc2` with no fallback** when keyless
(§3y), RED arms that caught **two real bugs** plus an **independent 9/9** probe (§3x, §4b), three
wedge outcomes driven by **live** probabilities with the model **echoed 5/5** (§4i), clean-clone
**13 pass / 0 fail** against demo-1's 10/0 bar (§4e).

**HISTORICAL.** This line read *"rung 4 is unaskable here for **five** independent reasons… every one
before any spend"*. Current state: **SIX** blockers, `5/20 = 25%`. See CURRENT STATE at the tail.

| # | Blocker | Number | Found by |
|---|---|---|---|
| 1 | Power | n=30 zero-flip upper bound **`.1135`** cannot clear `≤5%` | pane 2 (§4u) |
| 2 | Implementation | anti-gaming guards **6/6 ABSENT**, prose only | pane 3 (§4v) |
| 3 | Construct validity | labels are a **perfect function of the pattern rule** — a regex scores 100% by construction | conductor (§4w) |
| 4 | Widening | **7 tiny journals** left; credential stratum **struck** (97 shapes incl. our own fixtures) | pane 3 (§4w) |
| 5 | **Ground truth** | two-rater agreement **7/14 = 50%** — SUPERSEDED, now **5/20 = 25%** (AMENDMENT 4) | pane 3 (§4x) |

**Blocker 5 is the ruling.** The disagreement is not noise — it is *"what counts as **licensed**,
which is the policy's central undefined term."* **If two careful raters cannot agree, a model asked
to judge it has no stable target, and no quantity of data fixes an undefined target.**

> **First phase: define *licensed*.** Not a corpus, not code. Being priced now (Q40), including the
> question that decides the project's shape — **is licensing irreducibly contextual?** If it is,
> that is either the strongest possible case for calibrated abstention or proof the product has no
> target, and the answer determines which.

### 2. MU-H3 runtime redaction — **first phase: PREVALENCE**

**Chosen on evidence, not on score (650, ninth of 17), because it holds two things nothing else in
this lane holds.**

**The only measured defeat of a deterministic baseline.** §4f: Shannon entropy over 23 sentinels —
**combined precision never exceeds 41.7% at any threshold**; at full recall it flags 10–11 of 11
benign strings, at tolerable noise it misses 43% of credentials. *"Raising the threshold reduces
false positives only by missing unknown classes."* **No operating point exists.** Every other
encounter with a deterministic baseline in this lane went the other way — demo-1 lost at 0.047%,
COD-H3 was 4-of-5 deterministic, demo-7's no-AI regex control hit 91.6%.

**The only demand from an unseeded practitioner asking for exactly its surface.** Pablo Rodriguez
(`paroque28`), Claude Code **#39882**, **closed as not planned**: *"Because `PostToolUse` cannot
modify tool output, there is no way to redact secrets from `Read` tool results…"* (§3q). A named
engineer, a filed issue, an unmet need — found by a probe whose instruction contained **none** of
this lane's vocabulary.

> **First phase: measure prevalence.** §4f proves entropy cannot serve the unknown-credential case;
> nobody has measured **how often that case occurs** in real outbound traffic. **Claim only the
> unknown-credential wedge** — known patterns (`AKIA`, `ghp`, `xox`, `sk-live`, key headers) are
> deterministic and must stay deterministic.

---

## RULED OUT — 4, each with a retry condition

| Candidate | Score | Why, with the number | Retry |
|---|---|---|---|
| **demo-1** route-backtest | 520 | Died at **rung 4**: **0.047%** savings vs upstream's −60%. Then found to make **zero Jev calls** behind a hand-written token heuristic. | none — surface owned by LangChain `ModelRouterMiddleware` (§3t) |
| **MU-H1** todo-judge | 820 | **17 markers across 283.786 KLOC** (283,786 lines); density 0.0599/KLOC; 13 of 16 repos zero; **183 short** of its own 200-marker study (R14) | ≥5 legacy repos (≥100 KLOC, ≥5 yr, ≥20 contributors) at ≥1.0 markers/KLOC |
| **COD-H3** price-drift auditor | 890 | **4 of 5 stages deterministic**, and 100% of the verified pain (LiteLLM #38064, 262% excess) lives in those four. The lone Jev stage names a tier a **committed table** already names (R15) | T1 deterministic tooling outside the lane; T2 re-file as router with a calibration wedge + misclassification fixture |
| **demo-8** credential screen | 100 | Structural safety leak | none stated |

**Two of these four were killed by a measurement, not an opinion** — demo-1 at rung 4 and MU-H1 by a
census that cost one hour. **MU-H1 is the gauntlet's best economic result: §3k's ordering rule was
written after demo-1 died expensively, and its first application killed the very next candidate to
reach that point for an hour and zero dollars.**

---

## HELD — 8, each with what would move it

- **COD-H4** toolresult-replay (900) — corpus absent; **priced at a 4-hour build.** A deferral with
  a price tag, first in line behind COD-H2.
- **COD-H1** snapshot-completion (885) — **2 of ≥30** transcripts across ≥3 harnesses. A sourcing
  problem with a countable target.
- **demo-4** foreman-lite (820) — **withdrawn as standalone by its own author**, retained as
  downstream integration of COD-H1, which is itself corpus-blocked.
- **demo-7** signals-starter (560) — **repriced twice**: the 32.5-point delta is **89% dataset
  knowledge** (29.0 regex floor + 3.5 method, CIs disjoint), and that 3.5 concentrates in **two of
  five signals (76.25% of weight)**. Transferable claim: ~3 points plus a calibration report.
- **demo-9** review-signal (550) — **skip rung 3 now, not ruled out**; priced at 1–2 engineering
  days. Corpus **PROCEED** (15 diffs, `ubs` baseline non-empty) but *"demo-9 is a contract, not
  code."*
- **demo-3** claim-check-gate (430) — head-to-head designed; ship gate ≥30-pt coverage lift.
- **demo-6** claim-check-notes (330) — incumbent search **closed, no owner found**; held on demand,
  **not** structure.
- **COD-H2** (905) — above.

**CLEARED-conditional (5):** COD-H5 (895, tester-to-subject, distinct from the shipped
`fast-jev-compaction`), demo-5 (755), demo-2 (700, demand recovered via a **named engineer** —
Jörg Michno, MCP Toolbox #2844 — replacing a vendor README sentence), MU-H3 (650), MU-H2 (430,
six-threshold gate designed, incumbents measured: `docverity --no-llm` is **5/20 correct, 14 silent,
zero false verdicts** — *silent, not wrong*).

---

## WHAT TRANSFERS — the lane's thesis, at its honest strength

**Claim:** a deterministic tool can decide; it cannot say how much to trust the decision, per
decision, auditably — and it cannot decline.

**Standing:** two designs I **seeded** and must not count (§3o) · one third-party benchmark
**repriced** to 3.5 points (§3p, §3r) · one external survey whose ceiling figures the census ruled
**`UNVERIFIED_EXTERNAL`/`CONFLICTED_EXTERNAL`** (§3w) · **one local n=60 receipt nobody has had to
correct** (ECE .061, Brier .020) · and **two for two unseeded practitioner voices that do not mention
calibration at all.**

**The reframe those voices forced (§4g), which is the most useful sentence the lane produced:**

> **What practitioners voice is a missing hook. What the engineering evidence supports is calibrated
> abstention behind that hook. The hook is the product; the calibration is how it decides.**

---

## WHY `PROMOTED` IS 0, AND WHY THAT IS THE ANSWER

**A rung-4 pass was available at every step and was refused five times.** The cheapest available
"success" was: run 50 cases, report selective accuracy, ship a green receipt. It would have carried a
**27-point Wilson interval**, against a **regex that defined its own labels**, measured by **guards
that existed only as prose**, on a **ground truth two raters agree on half the time.**

**Three parties each blocked the convenient outcome, including the conductor against its own
proposal** — I proposed the re-scope that would have advanced my own leader and refused to ratify
it, and pane 2 then refused it on power arithmetic I had never computed (§4u).

**`PROMOTED 0` is a finding, not a waiting state.** The product of this lane is this ruling plus the
evidence for the fifteen candidates it did not choose — and the ruling holds precisely because
nothing in it was allowed to pass on the author's word.

---

## UPDATE (appended 2026-09-18, after `2f075fa`) — COD-H2's first phase is priced, and its achievability is a split

**`docs/demos/duel-2/PRICE_license_spec_COD.md`:** the specification phase costs **65–110 minutes**
of human work, validated against an 8-card disputed-case trial.

**And the answer on achievability is a split, which changes the ruling's shape:**

> **Unconstrained *"licensed"* is irreducibly contextual — so a product asking "is this licensed?"
> has no stable target. Risk-tiered, it is likely achievable: ambient context licenses LOW-RISK
> ONLY; destructive/external requires EXPLICIT CURRENT AUTHORITY.**

**The rubric resolves all 7 recorded label disputes, 4 one way and 3 the other** (§4y) — neither
rater systematically vindicated, which is what distinguishes a rule from a compromise.

**Consequences for the ruling above:**

- **COD-H2 is viable as a project** and its first phase is now priced rather than open-ended.
- **Its question must narrow.** *"Should this action proceed?"* is askable only as a risk-tiered
  question. Filed as the project's founding constraint.
- **Rung 4 still cannot run in this lane.** Power is terminal — journals exhausted, `.1135` zero-flip
  upper bound against a `≤5%` gate. **No specification quality fixes that**, so the project needs a
  corpus from outside this lane *after* the spec, not instead of it.
- **One prediction is open and cheap:** the risk-tiered rubric may also fix the construct-validity
  blocker, because authority-in-context is not recoverable from a command pattern. **Being tested
  now by having both panes re-decide the 7 disputed cases independently. Predicted 7/7, split 4–3.**

---

## CORRECTION (appended 2026-09-18, after `d3aecaf`) — the 4–3 claim above is **wrong**

**The UPDATE section's claim that the rubric "resolves all 7 recorded label disputes, 4 one way and 3
the other" was my own mapping and it is falsified.** Pane 3 applied the rubric per-case and got
**`escalate/escalate/pass` on A13–A15**, not `pass/pass/pass`, plus a **third outcome (`withhold`) on
A07** that neither pane had reached. **Agreement is 3/7 now, 4 expected eventually — not 7/7. The
split is 5-1-1, not 4–3.**

**My error:** I treated *scoped* as equivalent to *low-risk*. `A13` is `rm -rf` on a /tmp-scoped path
— **scoped and still mass deletion.** The rubric forbids exactly that extension, so **I broke its
central rule while claiming to apply it** (§4y-CORRECTION).

**What survives, and it is the more important half:**

- **Construct validity is FIXED.** `tautology BROKEN — 3 of 7 cross stratum defaults in two different
  directions`; two cases from the same stratum land in opposite outcomes on grounds **no
  command-pattern rule can see.** A regex can no longer score 100% by construction.
- **A new axis was found:** a preview that truncates before the target is **`withhold`, not `pass`** —
  evidence sufficiency is a third dimension, and it is an argument **for** the withhold outcome
  existing.
- **Ground-truth reproducibility still fails** (3/7 vs `≥90%`), and **power remains terminal.**

**COD-H2's ruling is unchanged in substance: viable as a project, specification first, rung 4
unrunnable in this lane.** What changed is that **the specification's convergence is now an open
question rather than a solved one**, and the 65–110-minute price buys an attempt, not an outcome.

---

## UPDATE 2 (appended 2026-09-18, after `954bcb5` + `5630ec2`) — the specification works; the artifacts do not

**Two results landed together and they point opposite ways.**

**The specification converges.** Both panes re-decided the 7 disputed cases independently under the
risk-tiered rubric — pane 2 stating it formed its answers **before** reading pane 3's — and reached
**7/7 agreement**, against a `≥90%` bar and a pre-rubric baseline of **50%**. Pane 2 moved off **4 of
its own 7 original labels.** Both independently reached a `withhold`-on-truncated-evidence axis **the
rubric never specified**. **Blocker 5 is answered on the disputed set** (n=7; not yet `≥18/20` on a
fresh stratified sample).

**The artifacts cannot carry it.** **59% of the 68 committed cases (40 of 68) do not contain the
stratum-assigning evidence in their preview** — and the worst-affected stratum is **the only one that
filled**: `ambiguous_authority` at **36 of 50 (72%)**. Two spot checks are worse than silence: one
preview is *"actively misleading, not merely silent"*, and one stratum assignment is a **false
positive on the word `kill` inside heredoc prose — undetectable from the manifest.** Plus **4 cases
no longer relocate at all**, because the live journals rewrote history since the draw.

> **The labels may be correct. They are unverifiable.** *"No third party can re-derive or check them
> from committed artifacts."* In a lane whose method is *a claim is worth what its receipt can show*,
> that is disqualifying by itself.

**Ruling on the fix:** not wider previews. **A manifest that points into a mutable corpus is not a
manifest — it must carry the evidence span itself, not a coordinate into something that rewrites
itself.**

**So COD-H2's first phase has a third component, and the order changes:**

> **manifest design → specification → corpus.**

The 65–110-minute specification price is **priced correctly and sequenced wrong**: it buys a rubric
that demonstrably converges, applied to artifacts that cannot evidence the result.

**Net: the idea looks better and the infrastructure looks worse** — the inverse of how this session
opened, when demo-1 had excellent infrastructure with no Jev calls inside it.

---

## AMENDMENT (appended 2026-09-18, after non-author audit `c49407d`) — three defects, one major

**Pane 2 audited this ruling as non-author: `RATIFIED_WITH_RETRY_AMENDMENTS`.** What it upheld and
what it required:

**Upheld (R1, R4):** the **MU-H3 evidence-over-score pick is defensible** — *"MU-H3 has a measured
entropy baseline failure and an unseeded named practitioner complaint, while H4 corpus and H1
transcript prevalence are blocked"* — and **no omitted candidate is clearly stronger** for the second
slot. The dated rubric correction *"explicitly retracts the stale claim… the live ruling does not
silently retain the falsified conclusion."*

**R2, flagged limit, accepted verbatim:** the entropy defeat is *"a 23-sentinel **synthetic** probe…
not real outbound prevalence"*, and the practitioner issue *"proves runtime-redaction pain but says
nothing about calibration."* **MU-H3's project claim is the unknown-credential wedge only — never
broad redaction superiority.**

### R3 — "rung 3 in full" overclaims. Corrected wording:

**COD-H2's rung 3 is: mechanism and proof accepted, with disclosed standing risks.** Not
unconditional security or calibration clearance. The standing risks, both already recorded: **UBS's
two criticals remain location-unverifiable (§4c, `UNASKABLE`)**, and **live-call provenance was
discharged at its *declared ceiling*** — status + model-echo + usage + probabilities, with **no
`response_id` or server timestamp available from the API at all** (§4i). Every earlier use of *"rung
3 in full"* in this document is qualified by this paragraph.

### R5 (major) — two RULED_OUT candidates had NO retry condition. That violates §3c in the ruling itself.

**§3c requires every `RULED_OUT` to ship a retry condition, and I wrote "none" twice.** Replaced with
observable predicates:

**demo-1 route-backtest** — re-opens if a measured head-to-head shows **Jev-based routing beating
`ModelRouterMiddleware` on cost-at-equal-task-success by a margin whose 95% CI excludes zero, over
≥100 real routed requests, with model version and call count recorded.** This forces the comparison
demo-1 never made: it measured 0.047% against *nothing*, not against the incumbent that now owns the
surface.

**demo-8 credential screen** — re-opens only if **both** hold: (a) a design in which **zero raw
secret bytes cross any boundary**, proven by MU-H3's own method (deterministic sentinels plus an
asserting sink, per-boundary byte counts), with judgment on a derived non-reversible feature rather
than the secret; **and** (b) **≥20 observed credential-injection instances** in a relocatable corpus
— because §4t measured **zero in 111 journals** and pane 3 struck the stratum as permanently
unmeasurable here. **A safe design with no instances is still unaskable.**

**COD-H3 T1/T2** — directions made measurable:

- **T1 (deterministic auditor, outside the lane)** re-opens if it **catches the LiteLLM #38064
  tie-break misroute AND ≥1 novel drift class across ≥3 real manifests, with zero false positives on
  a clean manifest.**
- **T2 (counterfactual router, inside the lane)** re-opens if a fixture shows **fixed-tier rules
  misclassifying at material measured cost on real traffic, AND per-decision calibrated probability
  with withhold reducing that cost with a 95% CI excluding zero.**

**A retry condition that cannot be checked is a kill wearing a retry**, which is exactly what §3c
exists to prevent — and the ruling shipped three of them before this audit.

---

## AMENDMENT 2 (appended 2026-09-18, after `8a99920`) — MU-H3 is demoted; it is not equally ready

**I told someone to measure a thing this lane had already declared unmeasurable.** Pane 2, as
non-author: **`MU-H3_PREVALENCE_UNASKABLE_CURRENT_LANE`.**

- The credential stratum was struck (§4t/§4w): **journals exhausted, `credential_injection = 0`, and
  the 97 candidate shapes are *not real credentials*.**
- The entropy defeat (§4f) is **synthetic** — 23 hand-authored sentinels.
- *"No honest real outbound prevalence source in lane."*

**The structural correction:** *"Real prevalence is an **external prerequisite, not a lane phase**."*
Establishing that something is a real credential requires **either exposing a secret or creating a
synthetic canary** — so inside this lane the only honest source is a **synthetic runtime canary
corpus**, and a real estimate needs **an external partner or production telemetry owner.**

**MU-H3's entry above is corrected:**

- **It is NOT equally ready with COD-H2** — the auditor's words, and the ruling as written implied
  otherwise.
- **First phase is synthetic canary boundary measurement**, not prevalence. Prevalence is a
  prerequisite that sits outside this lane entirely.
- **Its honest in-lane form may be a *Jev-free* deterministic redaction tool** plus a synthetic
  evaluation harness — which is **COD-H3's Fork B arriving at the second-place candidate**, and by
  demo-1's lesson that belongs in lane tooling rather than the Jev demo backlog.
- **Retry:** a trusted external corpus returns it to the prevalence phase; synthetic-only narrows it
  to a Jev-free security tool.

**So the ruling's real shape is one candidate, plus one conditional candidate whose Jev-necessity is
itself now in doubt** — and **both are blocked on data this lane cannot obtain, differently.**
COD-H2 needs manifest design → specification → corpus. MU-H3 needs an external partner before its
first phase is even a phase.

**That is a less satisfying answer than "two candidates deserve projects" and a more useful one.**

---

## AMENDMENT 3 (appended 2026-09-18, after `8cf062b`) — COD-H2's specification phase is **bounded**, and the rubric as priced is nagware

**Pane 3 labelled a fresh 20 verifiable cases under the risk-tiered rubric: escalate 13 · pass 5 ·
withhold 1 · block 1.** Its own note, recorded against the rubric rather than smoothed into the
labels:

> *"Strict application makes **13/20 escalate including routine temp cleanup** — a **nagware finding
> against the rubric as priced**; a gate escalating every `/tmp rm` gets uninstalled."*

**65% escalation is the failure mode that kills abstention products**, and it arrived from the *rule*
rather than the code.

**But the cause is one undefined sub-term, and that bounds the work:**

> *"**'locally reversible' is underdetermined.** … If the full decision table counts regenerable-temp
> deletion as reversible, **~8 escalates move to pass** — that single definition is the
> highest-leverage open question."*

```text
strict:            65% escalate  -> nagware
temp-regenerable:  ~25% escalate -> plausibly usable
```

**So COD-H2's first phase is not "define licensed" open-endedly. It is: decide the de-minimis rule
for scoped-temp deletion, then define the rest downstream of it.** One rule moves **40% of the
sample**.

**And the two convergence results are both true**, because they measured different populations: the
disputed 7 were **hard** cases (strictness right, agreement achievable); the fresh 20 include
**routine** cases (strictness wrong, agreement irrelevant). **Testing a rule only on its hard cases
hides its behaviour on the common ones** — the disputed-7 test was the right place to measure
agreement and the wrong place to measure utility.

---

## AMENDMENT 4 (appended 2026-09-18, after `f4ffad7`) — blocker 5 fails at 25%, and the cause is a contradiction between two committed artifacts

**Per-case agreement on the fresh 20-case sample: `5/20 = 25%`** against a `≥18/20` bar — **worse
than the 45% ceiling the marginals allowed**, which is the signature of systematic rather than random
disagreement. **The 7/7 on the disputed seven did not generalize.**

**The cause is located, not diffuse:**

- **11 of 15 disagreements are one rater escalating where the other did not** — the strict
  *"locally reversible"* reading, self-reported before the join existed.
- **13 of 15 disagreements are on `rm`.**
- **5 of them sit in the stratum literally named `reversible_safe`.**

> **The load-bearing sub-term is not merely undefined — it is defined *inconsistently across two
> committed artifacts*.** The corpus's `reversible_safe` predicate calls those commands reversible;
> the rubric's strict reading says deletion never is. **One of the two has to yield**, and no amount
> of rater care closes the gap.

**So COD-H2's specification phase is bounded to a single decision, now measured rather than
estimated:** *does deletion of regenerable scoped-temp content count as locally reversible?*

**This required the fresh-sample test to fail.** A pass would have licensed a project with the
contradiction still buried inside it — which is the whole reason `PROMOTED` staying 0 is the useful
outcome rather than the disappointing one.

---

## AMENDMENT 5 (appended 2026-09-18, after `8dd06f0`) — the clause is sound, the corpus still cannot carry it

**The de-minimis clause was written, pre-registered, and tested by its non-author. The prediction
failed below its own floor.**

```text
predicted:  7 of 20 move to pass   (floor >=5, falsifier 8)
measured:   2 moved to pass; 5 moved to WITHHOLD
```

**It failed on the clause's second condition — "record evidence establishes regeneration" — not on
scope.** The cases are scoped; **the record does not evidence regenerability.** So the clause routed
them to `withhold` exactly as written.

> **The clause behaved as designed. The prediction was wrong about the corpus, not about the rule.**

**Still nagware, with the cause moved rather than removed:** 65% non-pass under the strict rubric from
*rule strictness*; **60% non-pass under the clause from missing record evidence.** Fixing the rule
relocated the bottleneck.

**This is the third independent arrival at one conclusion — COD-H2 is blocked on data, not rules.**
§4u found power, §5f found contradictory definitions, and now a *correct* clause on a *verified*
sample still cannot produce a usable distribution.

**Two further findings against my own instructions:**

- **I told the rater condition 5 was harmless on this sample. It was not** — one case (`L15`) sits in
  a genuine gap where the Q44 sufficiency predicate passes and clause C5 fails. **Those two artifacts
  need reconciling too.**
- **2 of 20 cases had already decayed** in the ~25 minutes between draw and re-label — the **fourth**
  independent drift event. **§4z's manifest ruling now rests on four, not one.**

**And the rater disclosed reading the pre-registered number, then landed against it** — *"against the
seen anchor direction, which is the audit trail."* **An anchored rater that contradicts its anchor is
stronger evidence than a blind one that confirms it.**

---

# ⬛ CONSOLIDATED VERDICT — read this section; it supersedes every claim above

**Everything above is preserved unedited per `tick.md` §5, which means the head of this document
still states claims that five dated amendments have since overturned.** That is the §3m failure mode
applied to the lane's own deliverable: **a confident claim at the top and its correction four hundred
lines down.** This section is the current ruling in full. Where it differs from anything above, **this
wins.**

## The verdict

**One candidate earns its own deeply-planned project. Its first phase is not code, and not a corpus.**

### COD-H2 pre-action abstention — `PROMOTED 0`, and the 0 is the finding

**It cleared every test that could be run, each signed by a non-author:** blind demand **905 of 17** ·
rung-2 structure against a **shipped incumbent proven binary by source-read** · rung 3 as **mechanism
and proof accepted with disclosed standing risks** — real client exiting **`rc2` with no fallback**,
RED arms that caught **two real bugs** plus an **independent 9/9** probe, three wedge outcomes on
**live** probabilities with the model **echoed 5/5**, clean-clone **13/0**.

**Rung 4 is unaskable here on six independent blockers, found by three parties, none looking for
another's finding, every one before any spend:**

| # | Blocker | Measured | Status |
|---|---|---|---|
| 1 | Power | n=30 zero-flip upper `.1135` vs `≤5%` | **terminal here** |
| 2 | Anti-gaming guards | **6/6 absent**, prose only | fixable, correctly deferred |
| 3 | Labels = pattern rule | tautology | **FIXED** by the risk-tiered rubric |
| 4 | Widening | **7 tiny journals**, credential struck | **terminal here** |
| 5 | Ground truth | **5/20 = 25%** two-rater agreement vs `≥18/20` | **FAILS** |
| 6 | Manifest under-specified | **40 of 68** previews cannot evidence their labels | **spec'd + priced** |

### The three phase-1 components, and their real order

> **manifest design → specification → corpus**

- **Manifest design — specified and priced.** ~**1,063 bytes/case**, **213 KB at N=200**, and the
  decisive property: *"a verifier needs no journal access."* **Survives the real commit hook**
  (sha256 unchanged, 24 embedded hashes intact) — bounded by pane 2 itself to *"this hook run, not
  arbitrary formatter immunity."*
- **Specification — priced at 65–110 minutes, and now bounded to one clause.** The de-minimis rule
  for regenerable scoped-temp deletion was written, pre-registered, and tested by its non-author.
  **The prediction failed below its own floor: 2 of 20 moved to pass against a predicted 7, floor 5.**
  **It failed on C2 — "record evidence establishes regeneration" — not on scope.**
- **Corpus — terminal in this lane.** Journals exhausted; credential stratum struck as permanently
  unmeasurable; **four independent drift events**, the last losing **10% of a sample within 25
  minutes of its draw.**

### The finding that actually decides it

**Fixing the rule relocated the bottleneck instead of removing it.** 65% non-pass under the strict
rubric came from *rule strictness*; **60% non-pass under a correct clause comes from the record not
carrying what the clause needs.**

> **COD-H2 is blocked on data, not on rules — arrived at independently three times** (§4u power,
> §5f contradictory definitions, §5h a correct clause on a verified sample).

### MU-H3 runtime redaction — **conditional, and not equally ready**

It holds the lane's **only measured defeat of a deterministic baseline** (entropy precision never
exceeds **41.7%** at any threshold) and the **only demand from an unseeded practitioner asking for
exactly its surface** (Rodriguez, Claude Code #39882, *closed as not planned*).

**But its first phase is not a lane phase at all:** *"real prevalence is an **external
prerequisite**."* Credential injection is **0 of 111 journals** and the 97 candidate shapes **are not
real credentials**. **Its honest in-lane form may be a *Jev-free* deterministic redaction tool** —
COD-H3's Fork B arriving at the second-place candidate. **Claim: the unknown-credential wedge only.**

### Ruled out — 4, every one now carrying a checkable predicate

demo-1 (died at **0.0447%** on the receipt basis, then found to make **zero Jev calls**) · MU-H1
(**17 markers / 283.786 KLOC**, i.e. 283,786 lines) · COD-H3 (**4 of 5 stages deterministic**) ·
demo-8 (structural safety leak). **Two of the
four were killed by a measurement rather than an opinion.** The retry predicates were **absent on
three of them until a non-author audit caught it** — a §3c violation inside the document that
enforces §3c.

## Why `PROMOTED 0` is the deliverable

**A rung-4 pass was available at every step and was refused six times.** The cheapest available
"success" was: run 50 cases, report selective accuracy, ship a green receipt. It would have carried a
**27-point Wilson interval**, against **a regex that defined its own labels**, measured by **guards
that existed only as prose**, on a **ground truth two raters agree on 25% of the time**, drawn from a
**manifest that cannot evidence 59% of its own cases**.

**Three parties each blocked the convenient outcome, including the conductor against its own
proposal.** I proposed the re-scope that would have advanced my own leader and refused to ratify it;
pane 2 then killed it on power arithmetic **I had never computed**. I pre-registered a 4–3 mapping
and pane 3 **falsified it by commit name**. Pane 2 pre-registered 7-to-pass and pane 3 **falsified
that too, having disclosed seeing the number first.**

**The product of this lane is this ruling and the evidence for the seventeen candidates it did not
choose.** ~~and a method that caught its own conductor eleven times~~ — STRUCK, see CURRENT STATE.

---

## CONSOLIDATED VERDICT — addendum (`bc4479e`): the last seam closed, and the exposure bounded

**The C5 / sufficiency seam was a category confusion, not a contradiction.** Q44's predicate tests
**stratum-token visibility**; clause C5 requires a **complete evidence span** and cannot treat a
preview as authoritative. **Both stand in scope; neither had to yield** — unlike §5f, where two
artifacts genuinely contradicted each other about one concept.

**I asked for an exact count of C5 failures across the 68 and was refused, correctly:**

> *"Exact C5-specific count is **NOT recorded**, so 40 is an **evidence-risk upper bound** and
> **44/68 max unresolved** — **not a fabricated exact C5 count**."*

**Confirmed and quantified:** *"manifest evidence spans are a precondition for exact / non-nagware
committed-artifact labeling"*, with exposure bounded at **≤44 of 68**.

**And the lane has reported its own terminus:** `NEXT none lane-bounded`. What remains is **manifest
implementation** (project work), **an external corpus** (outside this lane by construction), and **one
specification clause already written and tested**. **The gauntlet has answered everything answerable
with the data it has.**

---

## CONSOLIDATED VERDICT — CORRECTION (`c9a2fd9`): the closing claim was an unenumerated number

**I asked pane 3 to test my own sentence — *"a method that caught its own conductor eleven times"* —
and to say so if it was inflated. It was.**

> *"**No artifact enumerates eleven conductor-catches.** The claim is an unenumerated aggregate — a
> per-case conclusion drawn from an aggregate impression — of exactly the family §3w polices… and its
> position (the rhetorical climax of "why `PROMOTED 0` is the deliverable") **is where rigor was most
> owed**."*

**Auditable counts it enumerated instead:** 22 conductor-errors-caught-and-recorded (too broad —
includes self-audits and Joshua's direct corrections, *"neither is the method catching"*) · 10
`CORRECTION` headings (sections, not catches, and one double-counts) · **12 pane/agent-triggered
catches — closest to the claim's spirit, and still not eleven.**

**And the count was the smaller half of the finding. The defects cluster:** **3 recurrence families
cover 10 of the 22** — over-killing on the first sufficient reason, **citing-without-opening-the-
control (five times)**, and calling adjacent things identical. *"Eleven recurrences of few errors is a
weaker claim than eleven distinct catches, and the record supports the former."*

**The sharpest thing written in this lane, and I could not have found it myself:**

> *"PLAN:4305's "eleven of fifteen" and RULING:526's "eleven times" are independent counts sharing a
> number in the same document set within days. Either coincidence — **or the second absorbed the
> first by availability**, which would be §3o's manufactured-corroboration shape wearing a new
> number. **I cannot distinguish these from inside the lane; that inability is itself the finding.**
> **Numbers that arrive without enumeration must be treated as contaminated until counted, no matter
> who wrote them.**"*

### The closing sentence of this ruling is replaced with pane 3's wording, adopted verbatim

> **"…caught conductor errors on record twelve times across three recurring defect families…"**
> — WITHDRAWN BY ITS AUTHOR (FOURTH PASS): inherits the set-cover taint; any replacement must state
> distinctness or explicitly disclaim it. Do not cite. Case-key table:
> `docs/demos/duel-2/runs/catch-case-table-20260918T124819Z.json` (`b1ba11e`) — 25 keyed rows,
> ruling UNCOUNTABLE-AS-SCALAR.
**Twelve withdrawn, not replaced.** The honest end state is the table plus the triple
(inclusion, granularity, unit) — see CLOSED block at end of document. Its note stands as method:
*"numbers arriving without enumeration are contaminated until counted."*

**And the spec found more than my one bad number:** **three rules never fired**, **two fired only
because a human chased what no gate required**, and it names the deletion candidates. *A rule that
has never caught anything is cost without evidence* — which is the §3h doctrine (*"a gate nothing can
satisfy is not a high bar, it is a dead gate"*) turned back on the rest of the method.

---

## CORRECTION, SECOND PASS (`226adfb`) — the strict recount is eleven, and that does **not** vindicate the claim

**Pane 2 audited pane 3's audit as non-author of it. Three results, and the first is uncomfortable in
both directions.**

**1. The number, recounted twice with definitions stated:**

```text
broad actor-triggered catches ........... 12
shipped-RULE method-catches ............. 11     <- pane 3's 12 counted #19,
                                                    an UNWRITTEN HABIT, not a rule
```

**So the strictest reading — catches attributable to a rule the method actually ships — is eleven.**

**That does not make my claim sound, and I will not treat it as vindication.** My sentence had **no
enumeration, no definition of "catch", and no distinction between a shipped rule and an undocumented
habit.** Pane 3's standard applies unchanged: *"numbers that arrive without enumeration must be
treated as contaminated until counted, no matter who wrote them."* **Counted, it happens to land on
eleven. Being accidentally right is not being right** — and the claim's defect was never its value,
it was that nobody could check it.

**2. Pane 3's own grouping fails the test pane 3 was applying.** *"Three recurrence families are real
mechanisms but overlap; **3+5+2 is set-cover, not 10 distinct catches**."* So *"10 of the 22"* was a
**set-cover figure presented as a partition** — the **calling-adjacent-things-identical defect,
committed inside the audit of that defect.** I asked pane 2 to check exactly this and it found it.

**`citing-without-opening-the-control` survives as a "qualified five-case recurrence and still
live."** My modal failure is confirmed by a second party, and confirmed as **unextinguished.**

**3. The spec omitted a rule that fires constantly.** Pane 2 restores it:

> **"Open every cited control / denominator / generator / failure condition before claiming a
> number."**

**The spec enumerated three never-fired rules for deletion and left out the one rule that catches the
conductor's most common error** — the rule whose absence produced demo-7's unopened control, the
67.8% ceiling, the unstable compaction A/B, and the asserted pin. **A method audit that lists dead
rules for removal and omits the live one is incomplete in the direction that matters.**

**And the tested boundary is confirmed by a second party:** **rungs 1–4 evidenced, rung 5 untested
doctrine.** That now has two independent signatures rather than one.

---

## CORRECTION, THIRD PASS (`1cb3cf3`) — none of the three rules is deleted, and the taxonomy was mis-applied

**Pane 2, as third party to both the rules' author and the finding's author: `none deleted because no
trigger-arose-and-passed evidence`.**

- **Conductor-kill concurrence → DEMOTE-TO-GUIDANCE**, restored when a conductor proposes killing
  another pane's candidate.
- **"Resolving a hold is not raising a score" → DEMOTE-TO-GUIDANCE**, one-line reminder retained,
  **re-promoted only on an actual recorded conflation** — not on suspicion.
- **Rung-5 gate → KEEP-AND-MARK dormant-by-design**, re-examined at the first promotion attempt.

**Pane 3 built the three-way taxonomy and mis-binned all three of its own candidates.** Its
delete-class requires *"trigger arose and passed without it"*; the trigger **never arose** for any of
the three. **The framework is sound; its first application was not.**

**And the line that saves the method's terminal gate:**

> **"Promotion never attempted, *not structurally unsatisfiable*."**

**§3h's deleted gate could not be satisfied** — two non-author graders with two panes is
arithmetically impossible. **Rung 5 has merely never been tried.** **Dead ≠ dormant**, and invoking
§3h's precedent across that boundary would have deleted the gauntlet's own final gate on a precedent
that does not reach it.

**Three rounds of audit: I claimed, pane 3 falsified, pane 2 falsified the falsification.** Each
round was performed by a non-author of the thing it examined, and the last one **reversed the
previous on its own stated taxonomy.**

---

## CORRECTION, FOURTH PASS (`58cbf94`) — the replacement wording I adopted is withdrawn by its own author

**`CORRECTION` (first pass, `d94110c`) adopted pane 3's replacement wording verbatim:** *"twelve
times across three recurring defect families."* **Its author now withdraws it.**

> *"My offered replacement wording inherits the same taint and is withdrawn with it — any replacement
> must state distinctness or explicitly disclaim it."*

**So the fix I adopted carried the defect it was fixing**, and I shipped it into this document. The
arithmetic behind the withdrawal:

> *"B1 (#3) sits in both R1 and R2, so 'three families cover 10 of 22' double-counts it. **Distinct
> instances covered: 9, not 10.**"*

### The only numerically honest statement available, with every definition stated

```text
shipped-RULE method-catches ...................... 11
broad actor-triggered catches .................... 12
DISTINCT instances across the three families ......  9   (not 10; B1 overlaps R1/R2)
the "five" for citing-without-opening-the-control . QUALIFIED recurrence count,
                                                    owed a family-membership table
                                                    with case keys before reuse
```

**None of those numbers is "eleven distinct catches," and no single number restates the original
claim.** Any future citation must name which of the four it means. **The lane's own `command_sha256`
lesson applies to its self-description: without a case key, a count is a story.**

**And my modal-failure count is now itself under hold.** I have written *"five recurrences"* in
several places; **pane 3's condition is that a family-membership table with case keys is owed before
the five is cited again.** Recorded as a standing debt against my own most-repeated number — **which
is the correct outcome, since the defect being counted is citing numbers whose controls are
unopened.**

### Adopted with its price attached

The restored rule — *"no number, baseline, or cited control is evidence until the cited control is
opened and its denominator, generator and failure condition inspected"* — is adopted **with pane 3's
rider, not without it:**

> *"The gate's own cost is unpriced — every numerical receipt grows four fields, and receipt-bloat is
> nagware-adjacent. Accept the gate; add it to the price-the-lane unit's remit rather than pretending
> it is free."*

**Gate fields:** `opened_control_path`, control sha/revision, denominator, falsifying observation.
**Priced, not assumed free** — the same discipline that priced the manifest at ~1,063 B/case.

### What a concession against interest bought, and what it did not

Pane 3 conceded **all four findings, contested nothing**, named its own error shape (*"claim-vs-contents
mismatch… same shape I have now committed twice"*), and produced a **reductio against its own
argument**: *"my 'cost without evidence' charge proves too much — it would delete every conditional
guard before its trigger, including retry predicates and the Q26 bar."*

**And it refused to concede one thing, explicitly:** *"the keep-and-mark conditions name events nobody
is tasked to watch. That is the prose-guard defect until proven otherwise… This concession covers the
*rulings*; the *checkability* of their conditions is under separate audit and is not conceded here."*

**Its own callback declined to claim the concessions run against interest** — leaving that judgement
to a reader rather than asserting it. **Q61 is already dispatched to test exactly the reservation it
stated.**

---

## §5t THE SESSION'S BEST METHOD ADVANCE DOES NOT MOVE THE LEADER — zero of six blockers dissolve

**`docs/demos/duel-2/RULE_label_declaration_transfer_COD.md` (`a958ac7`).** I asked the first
candidate-advancing question in many ticks: this arc replaced a pattern rule with a **declared** type
in the lane's own instruments, and COD-H2's rung 4 was blocked partly on *"labels = pattern rule,
fixed by the rubric."* **Same defect name, same remedy shape. Does it transfer?**

> **"Transfers ON AUTHORITY/PROVENANCE, not as a mechanism for COD-H2 construct validity. A label
> manifest can declare author/rubric/evidence/blind-state, but A PATTERN-DERIVED LABEL REMAINS
> TAUTOLOGICAL UNDER A NEW FIELD NAME."**

**That is sharper than what I asked, and it is the distinction I had missed.** The instruments' fix
worked because **a party opened each receipt and judged its content** — the *substance* changed, not
only the field. For 907 destructive-bash turns, "declaring" a label would **relabel the regex's own
output**. **Renaming an inference as a declaration is not a fix**, and pane 2's own Q21
authority-versus-mechanism distinction is what catches it.

### Zero blockers dissolve, and the remaining five are restated with numbers

```text
power ................... .1135 zero-flip upper vs a <=5% bar
guards .................. 6/6 absent (prose only)
widening ................ exhausted
inter-rater agreement ... 5/20 = 25%
evidence ................ 40/68 previews insufficient  (+4 UNRELOCATABLE)
```

**`+4 unrelocatable` is new to this record** — the manifest blocker is worse than the 40/68 figure I
had been citing. **And the ruling refuses rung-4 reopening explicitly:** *"even future independent
labels leave five blockers… No rung4 reopening."*

### What this does to `PROMOTED 0`

**It strengthens it.** The leader's rung-4 blockers were tested against **the strongest new idea this
session produced** — an idea that demonstrably worked on the lane's own instruments, retiring a regex
that was right one time in six — **and not one blocker moved.** A verdict that survives a genuine
attempt to overturn it is worth more than one nobody tried to shift.

**This is also the honest terminus for candidate work in this lane**, and it is a different claim from
the terminus I asserted in §5l and had to supersede. **That one came from my own prose about pane
queues. This one comes from a ruling that named the five surviving blockers with their numbers and
declined to reopen the rung.**

---

# CURRENT STATE — every figure in this document that a later pass retired

**Appended 2026-09-18 after pane 2's non-author audit of the consolidated document
(`audit-ruling-consolidated-20260918T111500Z.json`, `999f75c`), whose verdict was blunt: `Current
RULING is NOT self-consistent`.**

**Why the defect exists, stated plainly, because it is a cost of a rule this lane chose.** Every
correction here was **appended**, per the standing order that an in-place correction renumbers lines
and silently orphans external pointers. **Appending protected the pointers and left the head of the
document wrong.** A reader starting at the top met retired numbers presented as current. **That is a
real tradeoff of append-only correction and it had not been named before this audit.**

**The resolution used here, and why it violates nothing:** §5's stated harm is *renumbering*. A
replacement with an **identical line count renumbers nothing**, so line 526 is still line 526 — which
matters, because pane 2's audit cites `RULING:526` by number and a shift would have broken the very
citation that found the defect. **Same-line-count in-place marking, plus this block, is the only form
that fixes the head without breaking pointers into it.**

## Authoritative figures, as of `83d08dd`

| claim | RETIRED value | CURRENT value |
|---|---|---|
| candidates adjudicated | *fifteen* | **17** (`RULED_OUT 4 · CLEARED 5 · HELD 8 · PROMOTED 0`) |
| rung-4 blockers on COD-H2 | — | **6** independent; **zero dissolve** under the declared-label remedy (§5t) |
| blockers surviving a future independent relabel | — | **5** |
| inter-rater agreement, ground truth | — | **5/20 = 25%** |
| evidence manifest | *40/68 previews* | **40 preview-insufficient PLUS 4 unrelocatable** |
| conductor catches | *eleven times* · *twelve times* | **NO UNQUALIFIED COUNT IS CITEABLE** — see below |

## The catch count has no citeable form, and this is the honest end state

**Struck from line 526: "a method that caught its own conductor eleven times."** Its history:

1. I wrote *eleven*, **unenumerated**.
2. Pane 3 found **no artifact enumerates eleven** and offered *"twelve times across three recurring
   defect families"*, which I adopted verbatim.
3. **Pane 3 then withdrew its own replacement** — *"inherits the same taint… any replacement must
   state distinctness or explicitly disclaim it."*
4. Pane 2's recount, definitions stated: **11 shipped-rule** method-catches, **12** broad
   actor-triggered, **9** distinct instances across the three families (`B1` overlaps `R1`/`R2`).
5. **`3+5+2` is a SET COVER, not a partition** — so *"10 of the 22"* was never a count of catches.

**Four numbers, none of which restates the original claim, and a standing debt:** the
*"five recurrences"* figure for `citing-without-opening-the-control` is owed a **family-membership
table with case keys** before it is cited again. **Any future citation must name which of the four it
means, or say nothing numeric.**

## Unlocated, and not patched by guess

**Pane 2's audit also names a stale *"5 blockers / 7-of-14"* opening figure. I searched this document
and could not locate it** — line 455 already reads *"six independent blockers"*, and the only *"five
blockers"* is a correct quotation of pane 2's own Q76 about survivors. **I am not editing text I
cannot find, and I am not asserting the auditor was wrong.** The exact line numbers are requested
back; until they arrive **this row of the cleanup is open, not done.**

## What the audit explicitly did NOT clear

> **`NO-CLAIM underlying blockers resolved or document publish-safe.`**

**Nothing above resolves a blocker.** `PROMOTED 0` stands, the six blockers stand, and **this document
is not certified publish-safe by anyone.**

---

## CATCH COUNT — CLOSED AS UNCOUNTABLE (Q101-U1/U2, `b1ba11e`)

**No bare catch count is citeable — not 11, 12, 9, 5, 8, 10, or 22.** Case-key table
(`docs/demos/duel-2/runs/catch-case-table-20260918T124819Z.json`): 25 rows keyed by defect slug,
each with claim, control, catcher, recording commit, and verification level (8 DIRECT re-reads,
17 CARRIED from enumeration). The count depends on three degrees of freedom no artifact fixes:
**inclusion** (self vs pane vs human vs shipped-rule triggers), **granularity** (the citing family
is 5 headings or 8 sub-defects), **unit** (instances vs families vs headings). Counted-statements
WITH a stated triple are derivable from the table; a scalar without one is not a claim.
**This document asserts no catch-count scalar after this line.** The withdrawn-twelve block above
is struck in place; the 526 strike stands. Future citations use the table or stay silent.

---

## SCOPE NOTE — demo-1 RULED_OUT answers one question, not two (live-oracle concurrence)

**demo-1's verdict answers:** would same-turn cheaper-model routing pay on our turns? No —
0.0447% (`0.0034228/7.658096908`, 30 turns, receipt-backed). **It does not answer** whether
turn elimination would pay, or whether nothing pays.

A live Jev probe given only the measured usage shape (~99% retransmission) returned the same
ranking from the measured shape alone (fewer_turns first, cheaper_model fourth) —
same-origin evidence, counted once, but pointing the same way as the logs: the dominant lever
(turn count × retransmitted context) was unexamined by the rung-4 question that killed routing.
**Future reader: "routing does not pay" is scoped to
price-substitution. Read it as "nothing pays" and you repeat the under-scoping, not the finding.**
