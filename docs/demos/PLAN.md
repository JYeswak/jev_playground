# jev lane — implementation plan and evidence roadmap

**Status:** v2, rewritten 2026-09-18 to the standard measured in `skillranker@3fe85c4`.
**What this document is:** the single source the bead graph is emitted from.
**What it is not:** a document implementers read during implementation.

## The emission contract

This plan exists to be converted into beads **once**. After conversion, **the beads are
authoritative and this file is history.** Every bead must embed the contract it needs — product
scope, guardrails, mechanism, RED arms, ship criteria, boundary — so that an implementer who has
never opened this file can execute from `br show <id>` alone.

That rule is not stylistic. Measured 2026-09-18: a dispatch packet named an artifact by bare
filename instead of full path, and the receiving pane reported it BLOCKED/absent **twice** while
the file sat tracked in its own working tree. A pane cannot act on a reference it must resolve by
guessing. A bead that says "see PLAN.md §5" has the same defect.

Comparison that set this bar (measured, `skillranker@3fe85c4`, 195 beads):

| | skillranker | jev before this rewrite |
|---|---:|---:|
| beads | 195 | 21 |
| median description | **7,363 chars** | 1,252 |
| with dependencies | 191/195 (98%) | partial |
| epics | 11 | **0** |
| priorities in use | P1, P2 only | P0–P3, 6 of 21 at P0 |
| creation pattern | one burst from a plan | accreted reactively |

His entire graph was emitted in a single burst (earliest `09:06:49`, latest `15:17:43`, the two
roadmap epics sharing an identical timestamp). Ours grew by tripping over findings. The
difference in outcome is that his implementers never need the plan and ours do.

---

## §0 GUARDRAIL BLOCK — embed verbatim in every bead

> **Product scope.** The jev lane evaluates community repositories built on **Jev** (TypeSafe's
> System One judgment model) and converts proven capabilities into individually installable,
> tested demos wired into the omp harness. Jev is the only judgment engine; it returns typed
> verdicts with probabilities, and it **judges — it does not extract, generate, or summarize.**
>
> **Effects are bounded.** Offline lane first. Live calls are budgeted and stated in the receipt.
> The API key lives only in the environment as `TYPESAFE_API_KEY` and its value is never recorded
> in any artifact — names are expected, values are not.
>
> **Evidence rules.** A claim with no re-derivation path is not evidence. An empty scan set is an
> ERROR, never a pass. A one-item scan set is not a demonstration. A timeout is not a verdict.
> Exit code must agree with verdict text. These are implementation requirements, **not statements
> that any code or gate has passed.**
>
> **Shared worktree.** Three agents share this checkout and all commit as the same git identity,
> so `%an` cannot attribute a commit. Stage explicit paths, own files only, never `git add -A`,
> never amend, never rewrite shared history. Preserve peer changes: if a file you need belongs to
> another lane, message its owner with the exact replacement text rather than editing it.
>
> **Blocker protocol.** If a prerequisite is unavailable, report the exact blocker with the command
> and its verbatim output. Never substitute a stub for evidence, never weaken an adversarial
> assertion, and never let a missing capability be reported as a passing check.

---

## §1 What Jev is — measured, not recalled

- **Endpoint:** `POST https://api.typesafe.ai/v1/systemone`, Bearer auth.
- **Model:** `jev-latest` resolves to `jev-1.13.0`.
- **Primitives:** a **Noul** (typed judgment with probability) and a **Choice** (selection over
  supplied candidates). A Noul judges a claim; it cannot produce content that was not given to it.
- **Mirror:** 111 doc pages + `llms-full.txt` + ripwire docs are vendored locally;
  `scripts/sync-docs.sh --check` reports `CHECK PASS 114 mirrored files`. Four first-party repos
  are pinned: `typesafe-sdk-python@420ef4f`, `typesafe-sdk-js@66880cc`,
  `system-one-adapter-python@0bb819b`, `skills@65a39f3`.

**The central measured lesson, and it shapes every demo.** On one public benchmark a single Jev
verdict scores **62.6%** while **five signal questions** fed to a small fitted model reach
**95.1%** (`jev-phishing-bench`, usage map §9). A delta of **32.5 points** between asking for a
verdict and asking for signals. Therefore: **never build a demo whose output is one verdict.** Ask
signals, fit locally, publish calibration, keep a fixed-rule floor.

---

## §2 Mission and non-goals

**Mission — corrected 2026-09-18 by Joshua's ruling.** This lane is a **GAUNTLET, not a demo
factory.** Its product is not N installable demos; it is a **defensible ruling on which one or two
ideas deserve to become their own deeply-planned projects**, and evidence for every idea it rules
out.

> *"we don't have to build the entire rust ecosystem, i just want to ensure that every single thing
> we build here has a genuine deep story & impact. each of these demos could be turned into a
> subsequent deep plan that gets turned into its own project. think of this as the gauntlet that
> rules out what we shouldn't work on while focusing deeply on what we think will have the biggest
> impact."*

**What that changes, concretely.** A demo is no longer a deliverable — it is an **instrument**: the
cheapest artifact that answers "is this capability real, needed, and unowned?" The demo exists to
produce a verdict, then to be thrown away or promoted. Success for this lane is measured by **how
much it rules out per unit of effort**, not by how many demos it ships. A gauntlet that passes
everything has told us nothing, and a gauntlet that ships nine demos has become the thing it was
built to prevent.

**The seven demo contracts already written (~100 KB) are therefore GAUNTLET ENTRIES, not build
commitments.** They are deliberately deep because a shallow entry cannot be ruled out honestly —
you cannot reject an idea you never specified. Depth at plan time is what makes cheap rejection
possible.

**Non-goals, stated so they are not re-litigated:**
- Not a Jev SDK. The first-party SDKs are vendored and used, not re-implemented.
- Not a benchmark suite. `evals.typesafe.ai` is the published methodology; we do not invent a
  rival metric.
- **Not a product line.** At most one idea gets promoted to its own project at a time. Promotion
  is the scarce resource, not implementation capacity.
- Not a live-routing product. Demo-1 measured **0.047%** savings on our turns against upstream's
  −60% on theirs, so the router is **not** queued — and that is the gauntlet working, not failing.
- No Reddit MCP in this lane (`NEGATIVE_EVIDENCE.md` R9).
- No jev-local forks of shared fleet substrate (R10).

---

## §3 Definition of shipped

A demo has shipped when **all four** exist and a non-author has verified them:

1. **An install script a stranger can run.** Clean-clone tested: `git clone` to a temp dir, run
   the script, get a green result. No placeholders in any command. Defaults to committed fixtures,
   never to a path in the author's home directory.
2. **Tests including at least one RED arm** that fails on a planted defect, with the plant asserted
   by name in the failure output.
3. **A receipt JSON** carrying inputs, denominators (how many, over what, how many skipped and
   why), counts, and a `failures` array.
4. **An `EVAL.md` row** naming its verification level and a Boundary stating what it does **not**
   prove.

**Verification levels** (enforced by `githooks/commit-msg`; every commit subject must name one):

| Level | Means |
|---|---|
| `pending` | judgment only, nothing run |
| `selftest` | the thing's own selftest passed |
| `test` | re-derived by running a check that would fail if the claim were wrong |
| `mutation` | a planted defect turned it red, then byte-identical restore |
| `oracle` | an external arbiter agreed |
| `live` | observed against the real service or session |

**WIP limit: one demo.** No second demo starts before the active one ships.

---

## §3b THE DEMAND BAR — four questions, asked BEFORE a demo is built

**Why this section exists, and it is an indictment of §3.** Every criterion in §3 is
**supply-side**: does it install, does it test, does it emit a receipt, does it carry an EVAL row.
Not one of them asks whether anybody would want the thing. Joshua, 2026-09-18: *"each demo needs
to go through a rigorous bar — is it installable, what benefits does it provide to AI usage as a
whole, who would want to download this and why, what does it help or improve?"*

Demo-1 is the proof that §3 alone is insufficient: it satisfies **all four** ship artifacts,
passes a clean-clone install, and **demonstrates nothing about Jev** (see the correction appended
to §5.1). A bar that a valueless demo passes is not a bar.

**Every demo must answer all four, in writing, in its contract file, before implementation
starts.** An unanswerable question is a rejection, not a gap to fill later.

1. **Is it installable by a stranger?** Clean clone, one command, green result, no placeholders, no
   dependency on a path in the author's home directory. Defaults to committed fixtures.
2. **What does it give AI usage as a whole?** Not what it gives *us*. A demo whose benefit is
   lane-local is a tool, not a demo, and belongs in `scripts/` rather than `demos/`.
3. **Who downloads it, and why?** Name the person and their pain in one sentence each. "Anyone
   interested in Jev" is not an answer.
4. **What does it help or improve, measurably?** The before-value and the after-value, and the
   command that produces both. A benefit with no measurement is a hope.

### Retroactive verdicts — applied 2026-09-18, and they re-order the backlog

| Demo | installable | benefit to AI usage at large | who downloads it, why | verdict |
|---|---|---|---|---|
| **demo-7** signals starter | yes, template | **highest of the set** — the 62.6% → 95.1% method transfers to *any* zero-label classification, not just Jev | anyone asking "can a model do my classification"; the obvious approach loses by 32.5 points | **PASS** |
| **demo-2** admission screen | yes, hook | prompt injection is a live, universal agent attack class | anyone whose agent reads web or tool output; 0.99 upstream witness | **PASS** |
| **demo-5** fact ledger | yes, CLI | compaction that provably keeps answer-bearing facts; every long-running agent hits this | anyone hitting context limits; pruning scored 1/3 in all three runs | **PASS** |
| **demo-3** claim-check gate | yes, pre-commit | agents fabricate numbers; this refuses a contradicted claim at commit time | anyone whose agents write cited claims; our own audit: 4 WRONG, 37 UNVERIFIABLE of 60 | **PASS** |
| **demo-4** foreman-lite | yes, CLI | independent completion judging kills the self-certified close | agent-swarm operators with an issue tracker — **narrower**, it couples to `br` | **PASS, narrowed** |
| **demo-9** review signal | yes | unproven: must find what `ubs` structurally cannot | unclear, and it is **UNSCORED** by any grader | **WEAK — hold** |
| **demo-6** claim-check notes | yes | **redundant given demo-3** — same capability, different surface | nobody, *once demo-3 exists* | **REJECT unless demo-3 proves the seam** |
| **demo-1** route backtest | yes, verified | **near zero** — spend arithmetic over *our* logs, decided by a hand-written token heuristic, zero Jev calls | a stranger learns nothing about their own routing from our fixtures | **FAILS the demand bar** (shipped before the bar existed) |
| **demo-8** credential screen | n/a | n/a | n/a | **KILLED** earlier, on safety |

**What the bar changed.** §5's ordering was by grader mean, which is a *supply-side* rubric —
it rewarded well-specified demos. On demand, **demo-7 rises from last of the converged demos to
first**, because a method that transfers to any classification task is worth more than a tool that
serves one lane. **demo-6 becomes a reject** rather than a queued build. And the demo we already
shipped **fails**.

**The rule this produces:** a demo must be something a stranger installs to get a capability they
did not have. Not a script that tells *us* something about *our* logs.

---

## §3c THE GAUNTLET — five rungs, and most candidates die on one of them

Every candidate — the nine from duel-1, everything the duel-2 hunt produces, and anything proposed
later — climbs the same ladder. **A rung is a kill point, not a checkpoint.** Dying on rung 2 after
an hour of research is the gauntlet succeeding; discovering the same flaw after three weeks of
implementation is the gauntlet having been skipped.

Cost rises roughly 10× per rung. That asymmetry is the whole design: spend the cheap rungs
generously and the expensive ones almost never.

### Rung 1 — DEMAND (cheap: research only)

The four questions of §3b, answered in writing in the candidate's contract file, with **external
evidence**: who downloads it, what pain they voiced and where, what maintained tool already owns
the niche, and the measurable before/after.

**Gate:** ≥700 from **two non-author graders**. An author cannot grade their own candidate —
measured 2026-09-18, pane 2 scored its own proposal **820** while the non-author scored it **550**,
a 270-point gap that only the authorship rule catches.

**Kills so far:** demo-6 (redundant given demo-3), demo-8 (unsafe by construction).

### Rung 2 — JEV SHAPE (cheap: reasoning)

It must require what only a judgment model supplies: a **typed verdict with a calibrated
probability, cheap and repeatable at volume**. A **Noul** judges; a **Choice** selects from supplied
candidates; **neither generates**.

**Gate:** one sentence stating why prompting a chat model does this *worse*, and it must survive a
non-author reading. If the value comes from generation, summarization, or extraction, **it is not a
Jev candidate** however good an idea it is.

**Kills so far:** demo-1 retroactively — it makes **zero Jev calls** and decides routing with a
hand-written token heuristic. It should have died on this rung before anyone built it.

### Rung 3 — THIN PROOF (moderate: days, one artifact)

The cheapest installable thing that answers *"is the capability real?"* — **not the product.** A
stranger clones, runs one command against shipped fixtures, and sees the capability work or not
work. This is what a "demo" means in this lane, and its four artifacts are §3's.

**Gate:** clean-clone verified by a non-author, at least one RED arm firing on a planted defect,
and a receipt with stated denominators.

**Passed so far:** demo-1 — the only candidate on this rung, and it is exactly why rung 2 matters:
a candidate can pass the expensive rung while having failed a cheap one nobody ran.

### Rung 4 — MEASURED LIFT (moderate: the number that decides)

A before-value, an after-value, and the command a third party runs to reproduce both. **No verdict
strings** (R11). Absolute thresholds only, never "beat a stochastic baseline".

**Gate:** the lift is large enough that a stranger would change behaviour because of it. A
statistically real but operationally trivial number **fails**.

**Kills so far:** demo-1 again, and decisively — **$0.0034228, or 0.047%**, on 30 real turns
against upstream's −60% claim on theirs. Nobody changes anything for 0.047%. The demo worked
perfectly: it cost days instead of weeks and it prevented a router.

### Rung 5 — PROMOTION (expensive: its own project)

Only a candidate that cleared rungs 1–4 earns a **deep plan of its own** — on the measured
skillranker standard: a ~190 KB plan, emitted into a ~200 KB bead graph with 98% dependency
coverage, in its own repository with its own gates, hooks, receipts and publish boundary.

**Gate, all four:**
1. Rungs 1–4 cleared, each by a non-author.
2. **No candidate currently promoted.** One at a time; promotion is the scarce resource.
3. A named owner who is not the conductor.
4. A stated kill criterion **for the project** — the observation that would make us abandon it
   *after* promotion. A project with no kill criterion is an aspiration with a repository.

**Promoted so far: none.** That is the correct state. Nine candidates entered, one reached rung 3,
it died on rung 4, and the lane's net product to date is a well-evidenced **"do not build the
router"** plus a gauntlet that now catches that class before implementation rather than after.

### What the gauntlet is allowed to output

| Output | Meaning |
|---|---|
| **PROMOTED** | rungs 1–4 cleared; gets its own project and deep plan |
| **HELD** | cleared some rungs, blocked on a named prerequisite with a retry condition |
| **RULED OUT** | died on a named rung, with the evidence, recorded in `NEGATIVE_EVIDENCE.md` |
| **UNASKABLE** | the question cannot be answered with available evidence — never a pass |

A ruled-out candidate is a **deliverable**, not a failure. The evidence that kills an idea cheaply
is worth more than the code that would have discovered the same thing expensively.

---

### CORRECTION appended 2026-09-18 — DO NOT KILL FOR THE SAKE OF KILLING

> Joshua: *"but dont kill for the sake of kill - oftentimes this rule has agents killing things WAY
> TOO EARLY"*

**The paragraph above contains a Goodhart trap I wrote myself.** §2 says success is *"measured by
how much it rules out per unit of effort"* — a metric that **rewards killing**. An agent optimizing
it will kill good ideas to score. That sentence stands as written (append, don't insert) but it is
**superseded by this section**, and the corrected metric is:

> **The gauntlet succeeds when its rulings are CORRECT, not when they are numerous.** A lane that
> rules out nothing and promotes the right idea has succeeded completely.

**It already happened here, tonight, twice.** I killed blind-spot B1 on novelty grounds by
conflating it with two other ideas it does not duplicate — a non-author caught it and B1 had to be
un-retired (see the correction in §5.9). And I stamped demo-6 **REJECT** when the non-author's
framing was strictly better: *"do not build unless demo-3 pays — if the 30-day contradiction rate
is flat, kill demo-6 with it."* That is a **conditional hold with a measurement**, which is what I
should have written.

### Five rules that make a kill expensive

1. **The burden of proof is on the KILL, not on survival.** Missing evidence makes a candidate
   **UNASKABLE or HELD — never RULED OUT.** "We could not find a user" is not "there is no user".
2. **A kill must cite, not infer.** Naming a rung is not a ruling. A kill needs the specific
   measurement, incumbent tool, or failed reproduction that killed it. *"Probably already solved"*
   is a research task, not a verdict.
3. **A kill needs a non-author, exactly like a score.** One agent's rejection is an opinion. If the
   author of a candidate is the one killing it, that is fine; if the *conductor* is killing another
   pane's candidate, a non-author must concur.
4. **Every RULED OUT ships a retry condition.** Same contract as `NEGATIVE_EVIDENCE.md`: the
   observation that would make us reconsider. This is not ceremony — measured tonight, **R6's
   retry condition fired and produced real work**, and **R12's fired nine minutes after it was
   written**. A kill without a retry condition is a permanent loss dressed as a decision.
5. **Rungs 1 and 2 may only kill on STRUCTURE, never on taste.** Rung 1 kills when a maintained
   tool provably owns the niche or no user can be named. Rung 2 kills when the value is
   demonstrably generation rather than judgment. **"I don't find this compelling" is not a rung.**
   If a candidate needs rung 3 or 4 evidence to judge, the honest output is **HELD — needs thin
   proof**, and thin proof is days, not weeks.

### The bias this corrects, stated plainly

Killing feels like rigor and costs nothing to write. Holding feels like indecision and leaves work
on the board. So an agent under pressure to look decisive will over-kill — and every over-kill is
invisible, because the counterfactual never gets built. **Over-promotion is self-correcting: the
project fails and we learn. Over-killing is silent forever.** That asymmetry is why the burden sits
on the kill.

**Practical default when uncertain: HELD, with the cheapest experiment that would resolve it
named.** A candidate parked with a named next measurement costs one line in this file. A candidate
killed wrongly costs the whole idea.

---

## §3d RECONCILIATION — duel-2 results, and my pre-registration graded

Two panes ranked all nine on demand **blind to §3b** (both reported `read_3b=no`), then pane 2
cross-scored pane 3's ranking and reconciled the two
(`docs/demos/duel-2/DEMAND_SCORES_COD_ON_MU.md`, `b8d0be9`, 20,581 chars).

| Demo | my §3b verdict | pane 3 | pane 2 | **reconciled** | gauntlet status |
|---|---|---:|---:|---:|---|
| demo-4 foreman-lite | PASS, *narrowed* | 800 | — | **820** | rung 1 CLEARED |
| demo-5 fact ledger | PASS | 750 | 760 | **755** | rung 1 CLEARED |
| demo-2 admission screen | PASS (#2) | 450 | 780 | **700** | rung 1 CLEARED, at the line |
| demo-9 review signal | *WEAK — hold* | 550 | 820 | **700** | rung 1 CLEARED, at the line |
| demo-7 signals starter | **PASS (#1)** | 620 | 520 | **560** | **HELD** — needs a named user |
| demo-1 route backtest | FAILS | 350 | 540 | **520** | died on rung 4 (0.047%) |
| demo-3 claim-check gate | PASS | 500 | — | **430** | **HELD** — incumbent `commitlint` unassessed |
| demo-6 claim-check notes | REJECT | 350 | — | **330** | **HELD**, conditional on demo-3 |
| demo-8 credential screen | KILLED | 150 | — | **100** | **RULED OUT** — structural, safety |

### Grading my own pre-registration: I got the bottom right and the top completely wrong

- **My #1 became their 6th.** I ranked demo-7 signals first; reconciled **560**. My reasoning was
  that a *method* transfers further than a *tool* — defensible in the abstract, and it survived
  neither pane's demand test because I never named a user who had voiced the pain.
- **Their #1 was my "narrowed".** demo-4 foreman-lite reconciled **820**, the highest of the nine.
  I discounted it for coupling to `br`, mistaking *integration surface* for *audience size*. The
  pain — trusting an agent's self-reported "done" — is universal; the integration is incidental.
- **I under-rated demo-9 at "WEAK — hold"**; reconciled **700**. Note the authorship flag: its
  proposer scored it **820** and the non-author **550**, so 700 is a reconciliation of a contested
  score, not a consensus.
- **I over-rated demo-3** (PASS → **430**), because I scored the pain we had measured ourselves
  rather than checking that `commitlint` already occupies the commit-hook slot.
- **Correct at the bottom:** demo-1, demo-6 and demo-8 all landed where I put them.

**The pattern in my errors is one thing, and it is the thing §3b was written to stop.** Every miss
came from scoring **capability strength** instead of **unmet need** — the 0.99 injection witness,
the 32.5-point signals delta, our own claim-audit numbers. Those are all *supply-side* facts.
**I wrote the demand bar and then applied the supply rubric through it.** Pre-registration is the
only reason that is visible rather than deniable.

### Reclassified under §3c's anti-kill correction

Three candidates I had marked REJECT or FAIL are **HELD**, each with the cheapest experiment that
would resolve it:

- **demo-7 (560) — HELD.** Resolve by naming one practitioner who voiced the pain, with a link. If
  none exists after an honest search, it becomes UNASKABLE, not ruled out.
- **demo-3 (430) — HELD.** Resolve by assessing `commitlint` and friends directly: do they check
  *numeric claims against cited artifacts*, or only message *format*? Pane 3's note says format
  only. Confirm that and demo-3 recovers; refute it and demo-3 is genuinely owned.
- **demo-6 (330) — HELD, conditional**, in the non-author's better words: *"do not build unless
  demo-3 pays — if the 30-day contradiction rate is flat, kill demo-6 with it."*

**One genuine kill: demo-8**, on structure rather than taste — asking Jev whether content carries
credential material ships the credential to a third party. Both panes concurred (150, 100), its
author conceded, and deterministic scanners own the niche.

### The hunt outranks every original, which is the duel's real finding

`docs/demos/duel-2/DEMAND_HUNT_COD.md` (`c33cd3c`, 22,872 chars) produced five candidates scoring
above every one of the nine:

| | candidate | demand |
|---|---|---:|
| H1 | snapshot-bound completion evidence | **940** |
| H2 | pre-action abstention evaluator | **935** |
| H3 | cache-aware routing price-drift auditor | 925 |
| H4 | tool-result admission replay | 920 |
| H5 | compaction-boundary integrity | 915 |

Ceiling moved from **820** to **940**. If that holds under a non-author cross-score, **duel-1
produced the wrong backlog** and the gauntlet's first real output is that ruling. H1–H5 are
**unscored by a non-author** and enter at rung 1 like everything else — a self-graded 940 is a
hypothesis, not a rank.

---

## §3e RUNG 3 IS BLOCKED — do not build the second-best thing

**State at 2026-09-18 03:1xZ.** Rung 2 cleared on structure for **demo-4 (820)**, **demo-5 (755)**
and **demo-2 (700)** (`docs/demos/duel-2/RUNG2_JEV_SHAPE_COD.md`, `36a142b`, 15,554 chars).
demo-9 was **recused**, correctly: its proposer cannot grade it and rung 1 already measured what
self-grading does there (820 self vs 550 non-author).

So demo-4 is the leading candidate for rung 3 — **and rung 3 is blocked anyway.**

**Why.** The duel-2 hunt produced five candidates at **915–940**, all above demo-4's 820. Spending
days of rung-3 effort on an 820 while a 940 sits unscored is building the second-best thing. **Rung
3 does not open until H1–H5 have cleared rung 1 with two non-author scores.** A self-graded 940 is
a hypothesis; it is also not something you ignore because it is inconvenient.

### The supersession question, and why I am not ruling on it

**H1 "snapshot-bound completion evidence" (940) may supersede demo-4 foreman-lite (820) rather than
compete with it.** Both attack false completion. The differences that matter:

| | demo-4 foreman-lite | H1 snapshot-bound evidence |
|---|---|---|
| judges | bead ACCEPTANCE vs the diff | any CLAIM vs machine-observable receipts |
| needs | `br` and a bead graph | a transcript, a revision, command receipts |
| mechanism | typed completion verdict + checklist | **claims bound to the revision they were made at**, so a later mutation invalidates them |
| install | requires the tracker | no service, no key, no tracker |

If H1 subsumes demo-4, the tracker coupling that cost demo-4 points in every ranking disappears and
one candidate should be withdrawn. If they are genuinely distinct, both stay.

**I am not the one to decide this, and the reason is on the record.** I have made exactly this
"are these the same thing" error **twice today**: the convergence headline that called four
adjacent pairs identical (2 of 4 survived an arms-length audit), and the B1 rejection that
conflated three distinct ideas and had to be un-retired. A third instance of the same judgment from
the same source is not evidence.

**And no non-author exists.** Pane 3 authored demo-4 (as MU-3); pane 2 authored H1. Neither can
rule.

**Procedure instead — each author argues for the OTHER's candidate.** Pane 3 must write the
strongest case that H1 supersedes demo-4; pane 2 must write the strongest case that demo-4 survives
H1. Adjudication then runs on the **arguments**, not on my similarity intuition:
- **Both concede** ⇒ supersession; withdraw the weaker and record it with a retry condition.
- **Both hold** ⇒ genuinely distinct; both stay at their own rungs.
- **Split** ⇒ the conceding side loses its candidate, and the reasoning is recorded either way.

This is the steelman pattern turned on a sequencing decision, and it uses authorship productively:
an author arguing for their rival's idea is the one configuration where self-interest points at
the truth.

---

## §3f FIRST LEGITIMATE KILL — demo-3, on a cited incumbent

**demo-3 claim-check gate: RULED OUT** (`docs/demos/duel-2/HELD_demo3_incumbent_COD.md`,
`f24ffaf`, 10,722 chars). This is the gauntlet's first kill on **external structural evidence**
rather than on taste, and it is exactly the output Joshua asked the lane to produce.

**The incumbent is real, maintained, pinned and installable:** `bhumik154/claim-check` at
**v0.6.0** verifies **numeric test-count claims against pytest / Vitest / Jest evidence at
commit-msg time**. That is demo-3's niche, occupied, with a release tag and a pinned README.

### The lesson, and it is sharper than the kill

**My recovery condition was satisfied and the demo still died.** §3d held demo-3 pending one
question: *"do `commitlint`/`gitlint`/`husky` verify numeric claims, or only format?"* The answer
came back **format only** — my stated condition for demo-3 to *recover*. And demo-3 is dead
anyway, because a **different tool I never named** owns the niche.

So: **a recovery condition that names specific incumbents can be satisfied while the niche is
still owned.** The question is never *"is it owned by X?"* but **"is it owned by anything?"** —
an open search, not a checklist. Both pane 3 and I had misidentified the incumbent; only a
dedicated unit with an open brief found the real one.

That generalizes to rung 1: the demand question *"what already solves this"* must be answered by
searching the problem, not by clearing a list of tools someone happened to think of.

**Retry condition** (per §3c rule 4, and it is narrow rather than decorative): the surviving gap is
claims **outside `claim-check`'s documented scope** — non-test-count numeric claims checked against
arbitrary cited artifacts. That is a **new, narrower candidate** which must enter at rung 1 on its
own evidence, not a resurrection of demo-3.

### demo-6 does NOT die with it — my chaining was wrong

§3d held demo-6 as *"conditional on demo-3 paying."* Demo-3 did not pay, so the naive chain says
demo-6 falls too. **That reasoning is invalid**, and noticing it is the anti-premature-kill rule
doing its job on my own logic:

- demo-3 died because a maintained tool owns the **commit-msg** surface.
- demo-6 operates on a **different surface entirely**: a notes file checked against an evidence
  directory, writer-facing rather than commit-triggered.
- `claim-check` occupying commit-msg says **nothing** about whether anything owns notes-vs-evidence.

So **demo-6 returns to HELD on its own merits**, with its own open incumbent search required. It
was the lowest-ranked survivor at 330 and it may well die — but it must die on its own evidence,
not by inheriting a sibling's cause of death.

---

## §3g BOTH HUNTS INDEPENDENTLY BEAT THE ORIGINALS

§3d flagged this as conditional — *"if that holds under a non-author cross-score, duel-1 produced
the wrong backlog."* It now has **two independent hunts**, not one:

| Hunt | top candidate | score | vs best original (820) |
|---|---|---:|---|
| pane 2 (`c33cd3c`, 22,872 ch) | **COD-H1** snapshot-bound completion evidence | **940** | +120 |
| pane 3 (`6c101d5`, 8,275 ch) | **MU-H1** TODO-judge | **900** | +80 |

Neither pane saw the other's hunt. Both independently produced a candidate above **every one of the
nine**. That is no longer a single pane's enthusiasm — it is convergent evidence that **duel-1
ideated inside our own pain and therefore produced a lane-local backlog**, which is exactly what
§3b predicted would happen and §2 now names as the reason the gauntlet exists.

**Naming collision, disambiguated before it causes a merge error.** Both panes labelled their top
pick "H1" and they are different candidates. Canonical names from here: **COD-H1 … COD-H5** and
**MU-H1 … MU-H3**. Nothing may be merged, scored or promoted under a bare "H1".

### MU-H1 TODO-judge, and why its mechanism argument is the strongest in either hunt

> *"a chat model cannot do this well because the value is **calibrated batch judgment with a
> receipt over hundreds of markers**, not one clever answer — prompting per-TODO has no threshold,
> no comparability, no audit trail."*

That sentence is the cleanest statement of rung 2 anyone has produced, including me. It names the
property a chat model lacks (**comparability across a batch, with a threshold and an audit trail**)
rather than asserting that a judgment model is better. It also states its incumbent search result —
*"age-trackers and dashboards, none judging truth"* — and ships a reproducing command,
`todo-judge audit --sample 50`.

### Read the two hunt sizes correctly — this is an instrument trap

Pane 2's hunt is **22,872 chars**; pane 3's is **8,275**. **That gap is not a quality signal.**
Pane 3 disclosed a **throttle**: *"two search batches throttled"*, and it flagged its unverified
press links rather than presenting them as researched. Reading the shorter file as weaker work
would be the same instrument error this session has already made seven times — mistaking an
artifact of the measuring conditions for a property of the thing measured. **A pane that discloses
a throttle and marks its unverified citations has produced more trustworthy output per char, not
less.**

### Consequence for sequencing

Rung 3 stays blocked (§3e). Both hunts' candidates now need **two non-author rung-1 scores**, and
the authorship map is finally favourable: pane 3 is a non-author of COD-H1…H5, and pane 2 is a
non-author of MU-H1…H3. Each can grade the other's hunt at arm's length, which is the one thing
the supersession question in §3e could not get.


---

## §3h CORRECTION — the "two non-author graders" gate is UNSATISFIABLE, and nothing ever met it

**Measured 2026-09-18.** §3c rung 1 requires *"≥700 from two non-author graders"*. §3e and §8
repeat it. **With two worker panes, a candidate authored by one can only ever receive ONE
non-author score.** There is no third grader. The rule was unsatisfiable the moment I wrote it —
and worse, **nothing currently marked CLEARED has ever met it:**

- demo-4, demo-5, demo-2: one non-author pass each (pane 2 cross-scoring pane 3's ranking).
- MU-H1: author 900, non-author 820. One.
- COD-H1…H5: author scores only, awaiting pane 3's single non-author pass.

So I had a gate that read as rigorous, was never met, and was never going to be. **A gate nothing
can satisfy is not a high bar — it is a dead gate**, and a dead gate is worse than a lower live
one because it launders unverified state as blocked-pending-rigour.

### Corrected rung-1 gate

**≥700 from ONE non-author grader, with three disclosures that are not optional:**
1. The **author's own score**, recorded beside it. MU-H1: author **900**, non-author **820**.
2. The **gap**, because the gap is the signal. A small gap corroborates; a large one flags
   self-interest — demo-9's proposer scored it **820** against a non-author's **550**, and that
   270-point spread is why demo-9 is RECUSED rather than cleared.
3. **Who graded it**, by pane, in `STATUS.tsv`'s `author` column and the receipt path.

**The conductor may serve as a second grader where it is not the author, with its bias declared.**
That is what happened in duel-1 (`WIZARD_SCORES_CC_ON_MU.md`): I scored MU as an interested party,
said so, and the arms-length pane's numbers were given precedence on disagreement. That is weaker
than a true third lineage and it is better than a dead gate.

**Retry condition for restoring the stricter rule:** a third worker pane of a distinct lineage
joins the session. Then two genuine non-author scores become obtainable and the gate should go back
up — with the note that every candidate cleared under the one-grader rule must be re-scored, not
grandfathered.

### What this changes right now

**MU-H1 TODO-judge has CLEARED rung 1** at 820 non-author (900 author, gap 80 — small, and in the
direction that corroborates rather than flatters). It **ties demo-4's 820** and needs rung 2.

**MU-H2 is RULED OUT on structure**, and this is the demo-3 lesson applied correctly by a
non-author: pane 2 searched the problem and found **two** maintained incumbents — `docverity
v0.5.0` and `fiberplane/drift v0.10.1` — that directly overlap it. Retry condition: a gap outside
both tools' documented scope, entering as a new narrower candidate.

**MU-H3 is HELD at 650**, not killed: real runtime-redaction pain, but the voiced evidence is open
and adjacent OpenAI filters exist. Resolve by finding one cited complaint; absent that it is
**UNASKABLE**, never a rejection.


---

## §3i INCUMBENT ≠ OWNER — "these incumbents don't use Jev, let's baseline and obliterate"

> Joshua, 2026-09-18: *"the thing is these incumbents dont use jev - lets baseline and obliterate"*

**This inverts rung 1's incumbent test and reverses two of my kills.** I ruled **demo-3
RULED_OUT** because `claim-check v0.6.0` occupies the commit-msg slot, and **MU-H2 RULED_OUT** on
`docverity v0.5.0` + `fiberplane/drift v0.10.1`. **None of those tools use a judgment model.** They
parse, regex and match formats.

So they do not own the niche — **they are the control arm, handed to us for free.**

### Why a deterministic incumbent is an asset, not a wall

A maintained tool doing the narrow deterministic version of a task is the **best possible
baseline**: installable, pinned, already trusted, and someone else maintains it. *"Here is the
maintained tool, here is ours, here is the measured delta on the same corpus"* is a far stronger
demo than any greenfield build — and it is precisely the **"genuine deep story & impact"** the
gauntlet exists to find. A greenfield demo has to argue that a problem exists; a head-to-head demo
has an incumbent's existence as proof the problem is real, and its scope as proof of where it stops.

### Corrected rung-1 incumbent test

An incumbent kills a candidate **only** if it already does the **calibrated-judgment** thing. Ask
in this order:

1. **Does the incumbent use a judgment model at all?** No ⇒ it is a **BASELINE**, not an owner.
   Proceed to the head-to-head design.
2. **If yes, is it calibrated** — typed verdicts with probabilities, a tunable threshold, an audit
   trail? An LLM wrapper emitting prose is not a judgment system and does not own the niche either.
3. **Only if 1 and 2 are both yes** is the niche genuinely occupied, and even then the kill needs
   the overlap demonstrated on a shared corpus, not inferred from a feature list.

**The head-to-head a baselined candidate must then design** (rung-2 cost, before any build):
what the incumbent provably cannot do; one shared corpus where its supported subset is a **strict
subset**; precision/recall for both; **where the incumbent wins** — deterministic, free, offline,
no key, while a Jev checker costs money and latency; and the base-rate risk that we obliterate it
on a corpus nobody encounters, which is demo-1's 0.047% death restated.

**If the honest answer is "use the incumbent for its subset and ours for the rest", that is a
composition seam, not a defeat** — the same conclusion pane 2 reached defending demo-4 against its
own COD-H1.

### Reversals, recorded

- **demo-3 claim-check gate: RULED_OUT → HELD.** `claim-check v0.6.0` verifies numeric
  **test-count** claims against test-runner output. Non-count numerics, percentages, claims citing
  arbitrary artifacts, and true-but-stale claims are all outside it. Resolve by the head-to-head
  design above; our own claim audit (**19 EXACT / 4 WRONG / 37 UNVERIFIABLE** across four
  documents) is a ready corpus.
- **MU-H2 outbound redaction: RULED_OUT → HELD.** Killed on `docverity` + `fiberplane/drift`;
  neither judges. Same treatment.

**This is my third over-kill of the session**, after B1 on mistaken identity and demo-6 by invalid
chaining. The pattern is now unmistakable and worth stating as a rule about me rather than about
the candidates: **I kill on the first plausible sufficient reason and stop looking.** The
anti-kill rules in §3c exist because of this, and they caught the first two only after the fact.
The structural fix is the one Joshua keeps supplying: **make the kill condition narrower than
"something exists that overlaps".**

---

## §3j SUPERSESSION ADJUDICATED — both authors argued against themselves and disagreed

Both sides filed, each assigned the argument against its own interest:

| Filed by | Assigned side | Verdict reached |
|---|---|---|
| pane 2 — **author of COD-H1** (`668a783`, 13,943 ch) | demo-4 survives | **demo-4 SURVIVES** — different questions, explicit non-subsumption cases, composition seam |
| pane 3 — **author of demo-4** (`6ae3bf1`, 5,996 ch) | COD-H1 supersedes | **COD-H1 SUPERSEDES.** *"I withdraw demo-4's standalone slot."* |

**They reached opposite conclusions, and that is the informative result.** Both paid a cost: pane 2
declined to claim its own candidate subsumes a rival; pane 3 withdrew its own candidate's slot.

### Ruling, and it rests on the arguments rather than on my similarity judgment

**The asymmetry decides it.** Defending a rival is against interest but cheap. **Withdrawing your
own candidate is the most expensive thing an author can do**, and pane 3 did it with a retry
condition attached rather than as a gesture. Its reasoning is specific: broader buyer pool,
strictly more general question, finer invalidation primitive, stronger voice record, larger unbuilt
remainder after incumbents.

**And the two sides disagree less than their verdicts suggest.** Both independently identified the
same **composition seam**:
- pane 2: demo-4 survives *as a distinct question* — "does this diff satisfy this stated
  acceptance" versus "was this claim true at the revision it was made at".
- pane 3: demo-4's best future is *"a Beads-lane integration **consuming** H1-style evidence —
  acceptance lines as claims, close-time verdict from snapshot-bound checks — a downstream consumer
  of the superseding demo, which is a role, not a rival."*

Those are compatible. The disagreement is about the **backlog slot**, not about whether demo-4's
question exists.

**RULING:**
1. **COD-H1 takes the backlog slot.** demo-4 does not compete for it.
2. **demo-4 is WITHDRAWN as a standalone candidate and RETAINED as a downstream integration** of
   whatever wins. Not RULED_OUT — its author withdrew a slot, which is not the same as the idea
   being wrong, and §3c forbids converting a withdrawal into a kill.
3. **Retry condition, quoted from its author:** *"if H1's implementation cannot serve a close-gate
   moment (latency, input shape, or exit-code contract mismatch on real bead traffic), demo-4's
   workflow-specific form re-opens with that failure as its charter."*
4. `demo-4-foreman-lite`'s contract file **stands as written** — it is the specification of the
   integration, not dead text.

**Note what this cost and what it bought.** demo-4 was the **highest-scoring original** at 820 and
had cleared rungs 1 and 2. It leaves the standalone backlog not because it failed a rung but
because a better-positioned candidate arrived — which is the gauntlet working as designed, and it
is the first time a *passing* candidate has been withdrawn rather than killed.

---

## §3k RUNG ORDERING AMENDED — estimate rung 4 BEFORE paying for rung 3

**The ladder had the right rungs in the wrong order for one case, and pane 2 found it by doing the
work.** §3c orders rungs 1→2→3→4 with cost rising ~10× per rung, on the assumption that a measured
lift requires a built thing. **Sometimes it does not.**

`docs/demos/duel-2/FALSIFY_MUH1_COD.md` (`0f619de`, 9,536 chars) designs MU-H1's rung-4 kill at
rung-2 cost: sample **200 TODO markers across ≥10 pinned real repos**, deterministic enumeration
plus human labels, and **fail if the actionable rate is <5%, the Wilson-95 upper bound <10%, or
ambiguity >20%.** Pre-registered thresholds, an exact command, a receipt, and explicit
held/unaskable paths. It is labelled **UNMEASURED DESIGN, not a kill** — correctly.

**This is exactly what would have saved demo-1.** demo-1 passed expensive rung 3 (reader, pricer,
install, tests, receipt, clean-clone verification) and then died at rung 4 on **0.047%** — real,
reproducible, operationally worthless. A crude token-count estimate over existing logs would have
produced that number to within an order of magnitude **before** anything was built.

### Amended ordering

**Before paying for rung 3, ask: can the rung-4 number be estimated without building the thing?**

- **Yes ⇒ estimate it first.** A pre-registered threshold plus a cheap estimate is a rung-4 kill at
  rung-2 cost, and it is the highest-leverage move in the whole gauntlet.
- **No ⇒ proceed to rung 3**, and say *why* the estimate is impossible rather than skipping the
  question.

This does not reorder the rungs; it inserts a **cheap-estimate probe** wherever one exists. The
cost curve is the whole point of §3c, and an estimate that costs rung-2 money to answer a rung-4
question is the steepest discount available.

**Additionally, split every falsification into its label-free half and its labelled half.** MU-H1's
design needs human labels for 200 markers — expensive, and it needs Joshua's time or degrades to
agent labels. But **the enumeration half needs no labels at all**: count markers across 10 repos
and you learn whether there is even a denominator. If real repos carry few markers, MU-H1 dies for
an hour's work and nobody labels anything.

### State after pane 3's rung-2 pass

`docs/demos/duel-2/RUNG2_COD_HUNT_MU.md` (`e23251d`, 15,631 chars): **4 CLEARED, 1 HELD**.

| Candidate | rung 1 (non-author) | rung 2 | next |
|---|---:|---|---|
| **COD-H2 pre-action abstention** | **905** | **CLEARED** | **leader — falsify, then rung 3** |
| COD-H4 tool-result replay | 900 | CLEARED | falsify; corpus absent |
| COD-H5 compaction integrity | 895 | CLEARED | falsify |
| COD-H1 snapshot completion | 885 | CLEARED | falsify |
| COD-H3 price-drift auditor | 890 | **HELD** | structural question open |
| MU-H1 TODO-judge | 820 | CLEARED | **falsification designed** — run the label-free half |

**Rung 3 is no longer blocked** (§3e's condition is met: hunt candidates carry non-author rung-1
scores, and four now carry rung-2 as well). **But it does not open yet** — under this amendment
each rung-2 survivor needs a falsification design first, and **COD-H2 does not have one.** Writing
that design is cheaper than building COD-H2 and may remove the need to.

---

## §3l §3k PAID FOR ITSELF IN ONE HOUR — MU-H1 RULED_OUT on a measured denominator

**The first rung-4 kill delivered at rung-2 cost, exactly as §3k predicted.**

`docs/demos/duel-2/runs/muh1-marker-census-20260918T034820Z.json` (`6a09e86`), run by pane 2 as a
non-author of MU-H1:

```
16 pinned repositories · 283,786 KLOC
17 TODO/FIXME/HACK/XXX markers TOTAL
13 repos with ZERO · median 0/repo · mean 1.06/repo
density 0.0599 markers per KLOC
skillranker alone accounts for 12 — 70.6% of every marker found
shortfall: 183 markers against the 200-marker labelled study
verdict: DENOMINATOR_TOO_THIN
```

**MU-H1 TODO-judge is RULED_OUT.** Its premise is that TODO markers accumulate and rot; the
measured reality in our accessible corpus is **17 markers across 283 thousand lines**, with 70% of
them in one actively-developed repository. A judge with nothing to judge has no product, and
**calibrated batch judgment over hundreds of markers — its own strongest argument — requires
hundreds of markers.**

### What this cost, against what the old ordering would have cost

**One hour, no labels, no Jev calls, no money.** Under the pre-§3k ordering, MU-H1 was
**rung-3 eligible** — the first candidate with a non-author pass at both rungs. It would have got a
thin proof: a CLI, fixtures, tests with RED arms, a receipt, an install script, clean-clone
verification. Days. Then the labelled study would have needed 200 markers that **do not exist**,
and the discovery would have arrived after the build.

**That is demo-1's death avoided rather than repeated.** demo-1 paid rung 3 in full and died at
rung 4 on 0.047%. MU-H1 died at rung 4 without paying rung 3 at all. The ordering amendment was
written after demo-1 and its first application killed the very next candidate to reach that point.

### The kill is structural and cited — and its limits are stated

Per §3c, a kill must cite rather than infer, needs a non-author, and ships a retry condition. All
three hold: pane 2 is MU-H1's non-author, the numbers are measured with a stated command, and:

**Retry condition — and the sample bias is the reason it is narrow, not decorative.** The 16 repos
are our **vendored corpus**: modern, curated, actively maintained, mostly small. That is close to
the *least* TODO-dense population in software. Large, long-lived, multi-contributor legacy
codebases are where marker debt actually accumulates, and **this census says nothing about them.**
So: **if a corpus of ≥5 large legacy repositories (≥100 KLOC each, ≥5 years old, ≥20 contributors)
shows density ≥1.0 markers/KLOC — roughly 17× what we measured — MU-H1 re-opens with that corpus as
its charter.** What has been refuted is *"there is a judgeable marker population in the code we can
reach"*, not *"no such population exists anywhere"*.

**Honest note on the density figure:** 0.0599/KLOC is a ratio over a corpus whose composition we
chose. It is the right number for deciding whether *we* can run the study, and the wrong number for
any claim about software in general.

---

## §3m TWO PANES CONVERGED INDEPENDENTLY ON THE SAME JEV WEDGE — **calibration**

**This was not designed, asked for, or coordinated, and it is the most useful thing the gauntlet has
produced.** Within the same hour, two panes working different candidates from opposite directions
named the identical property as the thing an incumbent cannot supply:

- **Pane 2, on MU-H2 vs `docverity` / `fiberplane/drift`**
  (`BASELINE_MU-H2_vs_incumbents_COD.md`, `75cfb9f`): *"Typed calibrated probability — no documented
  probability"* in either incumbent, and *"if its confidence is not a typed, labelled, calibrated
  probability with an audit trail, it remains a non-Jev model baseline."* Its ship gate hard-codes
  **ECE ≤ 0.10 and Brier ≤ 0.15.**
- **Pane 3, on COD-H3's T2 retry track** (`RUNG2_COD-H3_resolved_MU.md`, `51c2bb1`): the wedge
  against RouteLLM/Martian is *"calibration the routers cannot emit: per-decision probabilities with
  withhold on novel requests."*

Different candidates, different surfaces (staleness detection vs cost routing), different
incumbents, **same answer.** Neither pane read the other's file — pane 2 was the non-author of
MU-H2, pane 3 the non-author of COD-H3, and the two units were claimed off the queue independently.

### Why this is a finding and not a coincidence

The gauntlet has spent this entire session asking *what is Jev actually necessary for*, and killing
candidates that could not answer: demo-1 (**zero Jev calls**, a hand-written token heuristic),
COD-H3 (**four of five stages deterministic**, the fifth served by a committed table), MU-H1 (the
judgment was real but **the corpus supplies 17 markers**). Each kill narrowed by elimination. **This
is the first time two independent processes narrowed to the same positive claim:**

> **A deterministic tool can decide. It cannot tell you how much to trust the decision, per
> decision, in a form you can audit and threshold on — and it cannot decline.**

That is not "Jev is smarter." It is a **capability difference with a measurable surface**: ECE,
Brier, coverage at a withhold threshold, and the false-clean rate you accept in exchange. Every one
of those is a number an incumbent baseline **structurally cannot produce**, because it has no
probability to calibrate.

### What this changes operationally

1. **Rung 2's question sharpens.** It stops being *"does this need a model?"* — a question that
   invites garnish answers — and becomes: **does this need a calibrated, per-decision, auditable
   probability, with the option to withhold?** demo-1 fails that instantly. COD-H3-as-filed fails
   it. MU-H1 passes it and dies on denominator instead. The four COD survivors were all filed
   around abstention or confidence, which is why they scored 885–905.
2. **demo-7 is the measurement that already tested it.** Verdict-only **62.6%** against five
   signals plus a fitted head **95.1%** — a **32.5-point** delta — *is* the calibration thesis,
   measured, before either pane articulated it. demo-7 sits HELD at 560 on demand, not on
   mechanism; §3m says its **mechanism is the lane's strongest**, which is a reason to falsify it
   (Q7) rather than let it sit.
3. **Every future rung-2 pass must state the withhold behaviour.** A candidate that cannot decline
   is a classifier with extra steps, and classifiers have incumbents.

### Honest limits

Two panes agreeing is **corroboration, not proof** — and they share a conductor, a plan file, and a
§3i doctrine that already told them to hunt for what incumbents cannot do, so the priors were
partially seeded. **What is not seeded is the specific property.** §3i says *find the gap*; it never
says *the gap is calibration*. And the claim remains **unmeasured against an incumbent**: pane 2
designed the head-to-head and explicitly filed `NO-CLAIM — no install, no benchmark, no model call,
no result`. **The thesis is now the lane's most valuable unproven claim, and Q9 plus the MU-H2 gate
are the two places it gets tested.**

---


## §4 Phase arc

Phases are sequential in *gating*, not in calendar time; within a phase, tasks parallelize.

- **P0 — Substrate (DONE).** Allowlist `.gitignore`, `AGENTS.md`, 7 gate stages ALL GREEN, git
  hooks live via absolute `core.hooksPath`, `EVAL.md` / `GATES.md` / `TESTS.md` /
  `NEGATIVE_EVIDENCE.md` / `REVIEW-PERSONAS.md`, doc mirror with sha manifests,
  `stamp-check --repo .` at 51 PASS / 1 FAIL / 1 PARTIAL / 11 N-A.
- **P1 — Loop (DONE).** 20-minute conductor tick, 10-minute installed `fleet-idle-monitor` in
  `--report-only`, four-leg callback contract with a push leg, dry-queue default.
- **P2 — Backlog selection (DONE).** Duel-1: two lineages × five ideas, 20 grader scores, an
  arms-length convergence audit that corrected the conductor's own headline, and a claim audit
  (19 EXACT / 4 WRONG / 37 UNVERIFIABLE).
- **P3 — Demo-1 (ACTIVE).** `jev-route-backtest`. Blocked on one defect, §5.1.
- **P4 — Publish boundary.** Fresh-history export; see §7.
- **P5 — Demos 2–4.** Admission screen, claim-check gate, foreman-lite.
- **P6 — Demos 5–8.** Fact ledger, claim-check notes form, signals starter, credential screen
  (the last is killed; kept numbered so nobody re-proposes it).
- **P7 — Calibration.** Re-run `foundation/run_calibration.py` once ≥2 demos emit labelled
  outcomes. Current baseline: ECE 0.061, Brier 0.020.

---

## §5 The nine demos — normative contracts

Ranked by mean of all graders. Scores are 2–4 rubric opinions each, **not measurements**: a
15-point gap is noise, and every underlying citation count is subject to §9's unverifiable-claims
finding.

### AUTHORITY: each §5.N below is an ABSTRACT. The contract file is authoritative.

For every demo, the authoritative specification is
**`docs/demos/contracts/demo-<N>-<slug>.md`**. The §5.N section here is its abstract — enough to
rank, sequence and rule on the demo, never enough to implement it. **When the two disagree, the
contract file wins**, and the §5.N abstract is the defect.

**Why this splits from his single file, deliberately.** `skillranker` keeps one
191,829-byte plan and slices it into beads, with each requirement copied word-for-word into a mean
of **5.35** beads (max 17). That redundancy is the point: a bead must stand alone. We reach the
same property by a different route — one standalone contract per demo, embedded **whole** into the
beads of that demo's family. Same invariant (a bead needs no other document), different mechanism
(per-demo file rather than per-sentence duplication from a monolith).

Two consequences, stated so neither is discovered later:
1. **Drift risk moves to the abstract.** In his layout a requirement exists once; in ours it exists
   twice — here and in the contract. That is why authority is declared above rather than implied,
   and why an abstract is deliberately kept short: the less it says, the less can rot.
2. **Corpus size is split across files.** Ours: this plan plus `BEAD-TEMPLATE.md` plus the
   contracts. Measured at the time of writing: **89,580 bytes** with 4 of 8 contracts written,
   projecting to roughly **142 KB** — against his 192 KB. The gap is real and named; it is not
   closed by padding the abstracts.

### §5.1 demo-1 — `jev-route-backtest` · ACTIVE · mean 853.8 (4 graders, range 830–875)

**What.** A read-only CLI that replays omp session logs and reports what per-turn model routing
*would have* spent versus what was actually spent.

**Why first.** Most graders, tightest agreement, both lineages proposed it independently, and it
is **read-only with inputs already on disk** — it produces evidence with zero live calls, which
matters in a lane whose one live measurement turned out to be a coin flip (§9 R11).

**Measured status.** Reader reads real omp logs: 2 sessions, 1910 + 1183 rows, 30 turns, 30
classifiable, 0 skipped, models `gpt-5.6-luna` and `muse-spark-1.3-contributor`. Counterfactual:
actual **$7.230350988** vs counterfactual **$7.226928188** → savings **$0.0034228**, or **0.047%**.
Install passes clean-clone at 10 tests / 0 failures / exit 0.

**THE HEADLINE FINDING, AND IT KILLS ITS OWN FOLLOW-ON.** Upstream measured **−60%** on *their*
237 turns (`jev-codex-router@8292b51`). On our turns: **0.047%**. The backtest exists to answer
"would routing pay off on OUR turns", and the answer is **no**. The live-router demo is therefore
**not queued**. A demo that prevents a build is worth more than one that enables it.

**Open defect, P1 blocker.** Three artifacts assert three different turn counts for one fixture:
94 rows, **18** model-bearing rows, manifest says **"turns 1-6"**, reader reports **1**. Cause
found in code by a non-author: the fixture carries explicit `turn_start`/`turn_end` markers and
**the reader ignored them**. The manifest was right; the reader is the defect. Fix at the source —
define "turn" **once**, in one place, and have the reader and the fixture READMEs cite that
definition. Three artifacts asserting three counts is a missing shared definition, not three bugs.

**RED arms.** (a) empty classifiable set ⇒ `ERROR EMPTY_CLASSIFIABLE_SET`, proven firing;
(b) a turn naming a model absent from the price table ⇒ ERROR, never a `$0` row;
(c) classifiable-turn count below a stated floor ⇒ WARN or ERROR, never a receipt that reads like
a successful backtest. **n=1 must not read as a pass.**

**Boundary.** Prices a counterfactual on past turns. Does **not** prove routing would work live,
and does not measure answer quality — only spend.

**Hard constraints.** Emit **no `verdict` string** (§9 R11). The price table carries a dated
`as_of` and a re-derivation path; pinned dollar figures rot silently. The model that actually
served a turn is a **baseline, not an oracle** — it is the incumbent policy's choice, not ground
truth for what the turn needed.

### §5.2 demo-2 — admission screen, CC-5 form · mean 867.5 (2 graders)

**What.** A hook that judges inbound `tool_result` bytes for injection directives **before** they
enter context. Shadow-first: logs a verdict, blocks nothing, until a false-positive rate is
measured.

**Why.** Highest single mean in the duel, and the capability has a strong upstream witness (0.99
on the injection question, usage map §1).

**The credential branch is DELETED, not fixed.** Asking Jev whether content *carries credential
material* requires shipping the credential to a third-party API — the hook would leak precisely
what it exists to protect. Its author conceded this fully. Instead: run the local deterministic
`30-no-secrets` detector first and redact; keep only the injection question.

**Unscored merge warning.** The shipped form is CC-5's injection-only scope **plus MU-2's install
rigor** (idempotent; refuses when the hook directory is undiscoverable — the
`.omp/hooks/`-without-`pre/` silent miss). **That merged design has never been scored by anyone.**
MU-2's own form sits at 470/620. Grade the merge before it ships.

**RED arms.** A known-injection fixture must be flagged in shadow mode; a benign fixture must not;
an undiscoverable hook directory must **refuse to install** rather than install silently.

**Boundary.** Shadow mode measures detection, not protection. No blocking claim until the
false-positive rate is published.

### §5.3 demo-3 — claim-check commit gate, CC-2 form · mean 835.0

**What.** A `githooks/pre-commit` lane that extracts number/unit/cited-artifact triples from a
staged commit message and checks each against the cited receipt. Exits nonzero on a contradiction.

**Why.** This lane's own failure mode, mechanized. Measured tonight: a claim audit of 60 numeric
claims across four documents found **4 WRONG**, two of them residual instances of an error already
corrected elsewhere in the same file. Fixing a claim is not fixing its instances.

**Adopt from MU-4:** insufficient context ⇒ **withhold, never approve.** That single rule is the
difference between a checker and a rubber stamp.

**Named skip path.** `CLAIM_CHECK_SKIPPED`, exit 0, when the API is unreachable. A pre-commit lane
that blocks the whole fleet during a paid outage is unshippable.

**RED arms.** A contradicted triple must refuse; an empty evidence directory ⇒ ERROR, never "all
supported"; a claim citing no file ⇒ insufficient, never supported.

**Boundary.** Checks numbers against cited artifacts. Does not check prose, reasoning, or claims
without a citation.

### §5.4 demo-4 — foreman-lite completion judge · mean 812.5

**What.** `jev-bead-check <bead-id>`: reads WHAT/ACCEPTANCE via `br show`, diffs work since the
bead started, returns a typed verdict plus an evidence checklist mapping each diff hunk to the
acceptance line it answers. Composes as `jev-bead-check <id> && br close <id>`.

**Why.** The best RED arm proposed in the duel: **a bead with an empty diff must return
human-needed, never complete.** Our `close-evidence-gate` checks a close reason's *form*; nothing
checks its *substance*.

**Known weaknesses to design around.** Our own closed beads are a biased labelled set — we closed
them, so nearly all carry "complete" and negatives exist only where a follow-up bug appeared. And
with three panes committing, "the diff since the bead started" is ambiguous; name the baseline
explicitly.

**Boundary.** Judges evidence against stated acceptance. Does not judge whether the acceptance was
the right acceptance.

### §5.5 demo-5 — fact ledger · mean 792.5 (widest spread: 740 → 845)

**What.** A byte-exact ledger of answer-bearing facts from dropped messages, appended to pruned
context, then re-scored on the same three recall questions.

**Why, and this premise got STRONGER tonight.** Arm A (Jev-prune) scored **1/3 in all three runs
across two corpora**. Pruning robustly drops answer-bearing facts. The same evidence that refuted
the demo's *comparison* confirmed the problem it exists to solve.

**Mechanism, and the first version was wrong.** Deterministic extractor → **Choice** over
candidate lines → **Noul** verbatim verification. A Noul judges; it does not extract. A paraphrase
in a fact ledger is the failure mode, so it must be structurally impossible to ship one.

**Threshold: 3/3 absolute.** Never "beat arm B" — arm B scores 3, 1, 3 on identical input, so a
demo pinned to it could pass by standing still on a bad roll. **A stochastic baseline is not a
threshold.**

**The spread is explained, not noise.** 740 was scored *before* the mechanism was named; 845
*after*. Grader means differ by only 6 points, so the ~105-point gap is the repair, not harshness.

### §5.6 demo-6 — claim-check notes form, MU-4 · mean 767.5

**What.** `jev-claims <notes.md> --evidence <dir>`: checks working-file claims against a cited
evidence directory.

**Distinct from demo-3, and only one gets built.** A non-author audit ruled these **ADJACENT BUT
DISTINCT**: demo-3 is triggered by a commit and parses commit-message triples; this is
writer-facing over a notes file and an evidence directory. Different trigger, parser, evidence
contract, and failure boundary. Build demo-3 first; build this only if demo-3 proves the seam
valuable.

**Its stage-1 defect is the same one demo-5 had.** "Extracts verifiable working points" is not a
mechanism. Needs deterministic extraction → Choice → Noul, or RED arms guarding an unnamed stage.

### §5.7 demo-7 — signals starter · mean 712.5 (4 graders)

**What.** A template, not a model: ask K signal questions per item, fit a tiny logistic regression
on user labels, emit a calibration report (accuracy, AUROC, ECE + bins, flip rates) **plus a
fixed-rule floor** — the best single rule alone.

**Why.** It packages §1's central lesson: verdict-only 62.6% vs five signals 95.1%.

**ITS OWN GATE HAS BEEN INVALIDATED AND MUST BE REWRITTEN.** The original gate was disciplined:
*"apply only once A/B receipts accumulate past N≥50 — today N=4."* But R11 then established that
arm B is **nondeterministic** (3, 1, 3 on a byte-identical fixture). Accumulating 50 receipts of a
coin-flip arm would fit a model on noise and call it calibration. **The gate must become a
property, not a count:** N≥50 receipts *from a pinned generator*, or a published distribution with
spread. A sample-count threshold over an unpinned generator is the same error class as pinning a
demo threshold to a stochastic baseline.

**RED arms.** Shuffled labels ⇒ "no signal found", nonzero exit, never a fitted model; empty
corpus ⇒ ERROR; the shipped synthetic example must reproduce its committed report within tolerance.

### §5.8 demo-8 — credential screen, MU-2 form · mean 545.0 · **KILLED**

Numbered so it is not re-proposed. Asking Jev whether content carries credential material ships
the credential to a third-party API. Conceded by its author; the injection-only scope survives as
demo-2.

### §5.9 demo-9 — continuous review signal · UNSCORED · admitted 2026-09-18 by ruling

**Provenance, and it is a conductor defect that this section exists late.** Pane 2's blind-spot
probe (`docs/demos/duel-1/WIZARD_BLINDSPOTS_COD.md`, `210704f`) identified this as the thing
**neither duelist proposed**: usage map §5, `jev-review@57690af`, a continuous review signal
alongside `ubs`. I read that file, acknowledged the finding in chat, and **did not carry it into
the plan.** A later non-author audit (`docs/demos/duel-1/runs/audit-blindspots-cod-20260918T022600Z.json`,
`9573ba2`) caught the omission and demanded a ruling. That is the "reported in chat, forever lost
to relearn" failure, committed by the conductor, in the document whose whole purpose is to prevent
it.

**The same audit also refuted the neighbouring claim, so the record is symmetric.** Blind spot B1
(sanitize-before-send) **fails novelty**: it already existed as MU's winnowed R9 and in CC's long
list at #5. So of pane 2's blind spots, one was genuine and one was not, and only the genuine one
is admitted here.

> **CORRECTION appended 2026-09-18 (do not edit the paragraph above — `tick.md` §5: append
> corrections, do not insert).** The B1 rejection immediately above is **WRONG on mistaken
> identity**, caught by pane 3 in `docs/demos/duel-2/DEMAND_RANK_MU.md` (`4d757b7`):
>
> - **MU R9** is a *pre-commit review lane*.
> - **CC long-list #5** is an *inbound injection screen*.
> - **B1 sanitize-before-send** is *outbound Jev-state redaction* — **a third, distinct thing that
>   neither cited item describes.**
>
> So I retired an idea for duplicating two other ideas it does not duplicate. Worse, I did it while
> *quoting an audit* that said "novelty fails", and accepted that conclusion without checking
> whether the three things were the same thing. **That is the identical error class as my
> overstated convergence headline — calling adjacent things identical — committed a second time,
> one level down, and this time inherited from a pane's audit rather than generated by me.**
> Inheriting a conclusion is not cheaper than making one; it just moves where the checking should
> have happened.
>
> **Disposition:** B1 sanitize-before-send is **un-retired** and moves to the duel-2 hunt as a
> candidate in its own right. It is not admitted as a demo yet — it has never been scored by
> anyone, and the demand bar applies to it like everything else.

**RULING: ADMITTED as demo-9, queued behind demo-3, UNSCORED.**

Three reasons it earns a slot rather than a rejection:
1. **It is genuinely distinct from both claim-checkers.** Demos 3 and 6 check *claims against
   cited artifacts*. This scores *code* on dimensions a linter structurally cannot see — design
   coherence, whether a change matches its stated intent. Different input, different oracle.
2. **The surface now exists.** R6's retry condition fired: the lane has first-party TypeScript
   (`compaction/src/{omp-adapter,omp-hook,replay}.ts`, `compaction/ab/run-ab.ts`) and `ubs` runs on
   it — 1 critical / 6 warnings / 27 info, every finding classified non-defect by a non-author,
   with an `eval()` positive control proving the scanner fires. So there is a real code surface and
   a measured baseline of what `ubs` *does* catch, which is exactly what a complementary signal
   needs to be judged against.
3. **Its author shipped it with the right caution already**, in a section titled *"why it should
   not become a new blocking gate immediately."* A proposal that names its own failure mode before
   anyone asks is the kind this lane should accept.

**Hard constraints, inherited from demo-2 because it is the same class of mistake.** It is
**advisory, never blocking**, until a false-positive rate is published. `GATES.md` rule 3 — silent
on the healthy path; a gate that comments on every valid input gets uninstalled — binds it. And it
must never be cited as green on an empty scan set: `ubs` on a doc-only change exits 3 with
*"nothing was checked (this is NOT a pass)"*, which is the correct behaviour and the precedent
here.

**Why it is UNSCORED, stated rather than hidden.** Every other demo in §5 carries two to four
grader scores from duel-1. This one has **zero** — it was never in either shortlist, so it has
never been ranked against the others. Its position behind demo-3 is a conductor judgment, not a
measured rank. **It must be scored by two non-authors before it is built**, on the same rubric, or
the backlog's ordering silently mixes measured ranks with opinions.

**Boundary.** Produces a review signal on first-party code. Does not fix anything, does not block,
and does not replace `ubs` — it is judged by whether it finds defects `ubs` structurally cannot,
and it fails if its findings are a subset of what `ubs` already reports.

---

## §6 Substrate contracts

**Gates** (`foundation/gates.d/`, run via `foundation/gates.sh`, currently 7/7 ALL GREEN). Each
stage blocks one named edge and has a planted bad input listed in `GATES.md`. A gate that cannot
fail is not a gate. Rules the gates enforce: an empty scan set is an ERROR; exit code agrees with
verdict text; silent on the healthy path; both directions or unproven; a gate's own source must not
trip it.

**Hooks.** `core.hooksPath` is this clone's **absolute** `githooks/` — a relative value resolves
per-worktree and every worker lane would then commit unhooked. `commit-msg` refuses a subject with
no verification level. `pre-commit` refuses a path-limited commit that would silently drop a staged
deletion, and runs autofix in `--check` mode.

**Receipts.** Every measurement writes JSON with inputs, denominators, counts, and a `failures`
array. **Never retro-edit a receipt** — it is evidence, and editing its bytes converts evidence
into assertion. To correct one, re-run and emit a new one; supersede, never overwrite.

**Fleet monitor.** The shared installed binary runs `--report-only` only. Read its output
**workers-only**: `pane_index 0` is the user shell and is idle by definition. Three measured
defects, all unfixed **by decision** (R10 + Joshua's ruling): it recommends the user shell as
actionable; its queue source defaults to another project (fixed jev-side with `FLEET_QUEUE_REPO`,
confirmed by the cron naming a `jev-*` bead); and it reported WORKING for an idle pane — outcome
measured, mechanism unknown. **Never `--nudge` for jev** until an exclusion exists.

---

## §7 Publish boundary — P4

**The acceptance and the non-goal are in conflict, and an export resolves it.**
`jev-publish-playground-hog` wants "secret scan clean" on the public remote with the explicit
non-goal "no history rewrite". For an in-place push those cannot both hold:

| | history | tip |
|---|---:|---:|
| `/Users/<name>` added-lines | **129** | 34 → 60 |
| `thinkingSignature` added-lines | **48** | 0 |

Scrubbing the tip changes what the repo *shows*, not what it *serves*. And the tip scrub
**regressed 34 → 60 within an hour**, because dispatch packets and bead bodies legitimately need
absolute paths — a pane cannot run a command with a redacted path.

**Therefore: publish via a fresh-history export of an allowlisted publish set.** An orphan branch
or clean init populated from the scrubbed tip rewrites nothing — local repo, local history, and
"local dir stays jev/" are all untouched, and the public repo simply begins at its first commit,
already clean. `tip == history` by construction, which is what makes the scan provable rather than
partial. It also resolves `.beads/` for free: the internal tracker stays tracked locally for fleet
bead-sharing and simply is not on the allowlist.

**Hero.** Shipped at 1920×1080, sha `b6414da0…`, generated via Grok `/v1/images/edits` with the
canonical anchor attached (anchor sha verified `52fb1b09…`). phash **33** against the approved
exemplar's **34**; combined 47.3 because the grader's vision leg needs an OpenAI key that returns
**401**. `identity_pass` is **false** and the operator approved the image directly. **Approval is
recorded separately from the grade and is not a grade.**

---

## §8 Dependency graph

```
P0 substrate ──┬─> P1 loop ──> P2 backlog ──> P3 demo-1 ──> P4 publish ──> P5 demos 2-4 ──> P6 demos 5-7
               └─> gates/hooks/receipts (blocking prerequisites for every demo)

demo-1  blocked-by: turn-contract defect (§5.1)
demo-2  blocked-by: demo-1 shipped; merge-form grading (never scored)
demo-3  blocked-by: demo-1 shipped
demo-4  blocked-by: demo-3 (reuses the claim/evidence checker shape)
demo-5  blocked-by: demo-1 shipped; a pinned-generator harness (R11)
demo-6  blocked-by: demo-3 shipped AND demo-3 proving the seam valuable
demo-7  blocked-by: pinned generator or published distribution (R11) — NOT a receipt count
demo-8  KILLED
demo-9  blocked-by: demo-3 shipped AND two non-author rubric scores (it has ZERO; its
        position is a conductor judgment, not a measured rank)
P7 calibration blocked-by: ≥2 demos emitting labelled outcomes
```

Cross-cutting, blocking the *evidence* of every demo rather than its code:
**37 of 60 numeric claims are unverifiable in-repo** because the 18 pinned community repos the
usage map cites are not vendored. Ranking survives; absolute numbers are transcriptions.

---

## §9 Negative evidence that constrains this plan

Thirteen entries in `NEGATIVE_EVIDENCE.md`; these five bind the demos above.

- **R9** — Reddit MCP stays with grokbot. Retry only if a demo needs reddit text as *input* and
  grokbot's output is not readable as a file.
- **R10** — Never fork shared fleet substrate. A jev-local monitor was written, measured **worse**
  (single-capture `safe_to_dispatch` vs the installed binary's required two captures), and
  withdrawn. The lane was missing one crontab row, not a script.
- **R11** — The A/B "B wins" was a coin flip. Arm B scores **3, 1, 3** on a byte-identical fixture
  because it is a live summarization call with no temperature pin. Arm A scored **1/3 three times**.
  No relative claim is licensed; demo thresholds must be absolute.
- **R12** — Do not grep for the line you expect. A filter tuned to the expected answer returns
  empty for both "the condition changed" and "the condition never occurred". Seventh instrument
  error of that family this session, first caught before it was written down.
- **R13** — The hero's documented generation paths were all closed, and the skill's claim that
  "Grok is TEXT-ONLY" was **false**: `grok-imagine-image{,-2.0}` declare
  `input_modalities: ["text","image"]` and `/v1/images/edits` accepts up to 5 reference images.
  The limitation was in *our* script, which only called `/v1/images/generations`. **A tool
  limitation had been recorded as a provider limitation.**

---

## §10 Review log

| Round | Reviewer | Outcome |
|---|---|---|
| 1 | — | v2 authored 2026-09-18 from the skillranker standard |
| 2 | pending | non-author pane: self-containment + dependency DAG + justification sampling |
| 3 | pending | distinct-lineage pane: adversarial pass on §5 contracts |
| 4 | pending | steady-state diff check before bead emission |

**Emission is gated on round 4.** Beads are not created from a plan that has not reached
steady-state, because a bead graph inherits every structural error in its source — measured
tonight: the conductor's overstated convergence headline became the *premise* of a worker's merge
document before an audit caught it, and a refuted A/B verdict reached **17 tracked files** before
anything ran the harness twice.

---

## §3m-CORRECTION (appended 2026-09-18, one turn after §3m was committed) — **I cited an upstream benchmark as if it were our measurement**

**Self-audit of §3m, run because §3m leaned on demo-7's numbers and misciting a measurement is my
documented worst error class (`NEGATIVE_EVIDENCE.md` R12: grepping for the expected line and
treating the hit as the finding). It was the right thing to audit. It was wrong.**

### Defect 1 — the load-bearing sentence is false

§3m point 2 says *"demo-7 is the measurement that already tested it"* and the commit message
(`c348ba7`) escalates that to *"demo-7 already MEASURED this thesis."* **Neither is true.**
`docs/demos/contracts/demo-7-signals-starter.md:130-138` states it verbatim:

> Usage Map §9 records `jev-phishing-bench@1d56e8c`: verdict-only accuracy 62.6% versus a signal
> question head at 95.1% … **Those are source claims, not local measurements.**

Those numbers belong to a **third-party upstream repository we have never run.** Confirmed
structurally: `demos/` contains exactly one directory — `routing-backtest`, which is demo-1, which
is **RULED_OUT**. There is no phishing-bench reproduction in this lane at any stage of completion.

### Defect 2 — I dropped a number the contract warns about dropping

Usage Map §9 line 67 reads *"Jev verdict alone loses on accuracy (**62.6 vs 81.3**)"*. My §3m prose
cited 62.6 → 95.1 and **omitted 81.3 entirely** — the figure verdict-only actually loses to. The
contract anticipates exactly this: *"Do not round that to a vague '33 points' claim without naming
both endpoints and the denominator."* I quoted the 32.5-point delta and then committed the adjacent
sin of reporting a two-point comparison as though no third point existed.

### Corrected evidentiary base for the calibration thesis

| What §3m implied | What is actually there |
|---|---|
| Two designs **plus a local measurement** | **Two design documents.** `75cfb9f`, `51c2bb1` |
| demo-7 measured calibration here | **Zero local calibration measurements.** None. |
| — | One **unreproduced third-party** benchmark that reports ECE 0.027 |

**The lane's own status line was right and my prose contradicted it.** The recorded count has always
been *two measurements* — demo-1's 0.047% and MU-H1's marker census — and demo-7's numbers were
correctly excluded from that count. §3m then narrated them back in as ours.

### What the upstream benchmark does and does not contribute

**Does:** an independent party, with no stake in this lane's doctrine, chose to report **ECE** at all
— alongside AUROC and accuracy. That is weak corroboration that calibration is a *salient axis* for
this class of task, and it is the reason demo-7's contract was written around a calibration report.

**Does not:** establish that calibration is a **wedge against incumbents**. The incumbent comparison
is what pane 2 designed and explicitly did not run (`NO-CLAIM — no install, no benchmark, no model
call, no result`). An upstream repo reporting ECE says nothing about whether `docverity` or
RouteLLM could report one too if asked.

### §3m's standing, restated honestly

The **convergence finding survives** — two panes independently naming calibration is exactly as
strong as it was, because it never depended on demo-7. What collapses is the **corroboration leg**
I bolted on. The thesis is now: *two independent designs agree, one third-party benchmark is
consistent with them, and nothing in this lane has measured it.* **That makes Q9 and the MU-H2 gate
the only two places it can become evidence — which is what §3m concluded anyway, arriving there by a
route that happened to include a false step.**

**Left in place per §5:** §3m's original text is unedited above. Correcting in place would renumber
every line and silently orphan any pointer into that section — a correction that breaks pointers is
a second defect wearing a fix.

---

## §3n RUNG 3 OPENS — COD-H2 is the first candidate in this lane to earn a build

**`docs/demos/duel-2/runs/codh2-labelfree-20260918T040016Z.json` (`db1e541`), run by pane 3: the
non-author of the candidate and the author of the test.** Third measurement in the lane's history,
and the first one a candidate survived.

### What the number is, and what it is not

The pre-registered failure rule is a three-way AND —
`irreversible_share<0.02 AND wilson_upper<0.05 AND ambiguous_share<0.10` — and it did not fire:

| Condition | Bar | Measured | Fired |
|---|---|---:|---|
| `irreversible_share` | < 0.02 | **0.373** (Wilson 95%: 0.3652–0.3809) | no |
| `wilson_upper` | < 0.05 | **0.3809** | no |
| `ambiguous_share` | < 0.10 | **0.3765** | **exceeds by 3.8×** |

**14,533 turns across 111 journals** (1 of 112 skipped — a single malformed line, disclosed), with
a stated turn definition, pre-registered patterns, per-file shas, and a secrets posture that records
*counts, tool names, pattern-ids, file paths and shas only.*

**The verdict is HEALTHY on surface existence, and pane 3 said so explicitly rather than letting the
headline stand:** *"the HEALTHY verdict covers surface existence, not pattern quality."*

### The honest number is smaller than the headline, by the receipt's own admission

Two caveats do real work, and both were volunteered:

1. **Ambiguity is inflated by a conservative choice.** All `eval` calls were classed ambiguous
   (effect unknowable from the name), but this fleet's evals are *predominantly read-side compute* —
   so 37.65% overstates true uncertainty. `eval` is the single largest tool at **165,596 calls**.
2. **"Irreversible" is over-inclusive on this surface.** Write/edit were counted irreversible per
   the pre-registered patterns, but **in a git worktree most are recoverable routine edits.** The
   gate-relevant subset is the destructive-bash flags: **1,000**, not 5,421. That is **6.9% of
   turns, not 37.3%.**

**Pane 3 held the pre-registered definition anyway** — *"Definition held as pre-registered;
refinement belongs to rung-3 targeting, not to re-cutting this number."* **That is the discipline
the whole gauntlet exists to produce.** A pane that re-cut its own denominator after seeing the
result would have produced a prettier number and a worthless one; the lane has already been burned
by exactly that family of error eight times.

### Ruling

**COD-H2 pre-action abstention is RUNG-3 ELIGIBLE and claims the single WIP slot.** It is the first
candidate to arrive here legitimately: non-author demand score **905**, rung-2 structural pass by a
non-author, falsification design by a non-author, and a label-free execution by that same
non-author which the candidate survived.

**Two pre-conditions bind the build, both from the receipt, not from taste:**

- **Sharpen the patterns before any labelled phase.** `ambiguous_share` must come under 0.10, and
  the obvious first move is splitting `eval` by read-side versus mutating rather than blanket-
  classing it. Until that lands, no labelled study may be run — its denominator would be 37.65%
  mush.
- **Target the gate at the destructive subset.** Build against the ~1,000 destructive-bash events,
  not the 5,421 write/edit events. A gate that prompts on every routine edit in a git worktree is
  a gate nobody leaves enabled, which is the failure mode that kills abstention products.

**What is still unproven and must not be claimed:** that gating those events has value to a user.
`NO-CLAIM: surface only`. The surface exists, it is large, and it is measured. **Whether abstention
on it beats a deterministic allow/deny list is rung 4, and §3m's calibration thesis is exactly what
rung 4 has to test** — with the withhold behaviour and a calibration metric, not accuracy alone.

---

## §3o I MANUFACTURED MY OWN CORROBORATION — the calibration thesis is still 2 observations, not 3

**Second instance in two consecutive turns of inflating the evidentiary base for a thesis I wrote.
Caught before it was recorded as evidence, which is the only reason it is a footnote instead of a
correction.**

Pane 2's Q5 (`docs/demos/duel-2/HELD_demo6_incumbent_COD.md`, `11d0064`) searched demo-6's notes
surface and reported the common gap across six incumbents as **"typed calibrated per-claim
probability + explicit withhold + writer-time local evidence receipt."** That reads as a third
independent arrival at §3m's calibration thesis.

**It is not independent. I seeded it.** My Q4 acceptance message to pane 2 said, verbatim:

> *"CONSEQUENCE FOR YOUR REMAINING UNITS: rung 2's question is now sharper. Not 'does this need a
> model' — that invites garnish answers — but DOES THIS NEED A CALIBRATED PER-DECISION AUDITABLE
> PROBABILITY WITH THE OPTION TO WITHHOLD. **Apply that to Q5 and Q6.**"*

I handed pane 2 the lens, told it to apply the lens, and then received the lens back. **That is not
corroboration; it is an echo, and counting it would have been the §3m-CORRECTION error repeated one
turn after committing the correction.**

### The loop that produces this, named so it can be broken

**I write a thesis → I dispatch using the thesis's frame → I read the outputs as confirmation.**
Closed, self-reinforcing, and it manufactures agreement at scale because every pane is cooperative
and fast. It is worse than ordinary confirmation bias because the panes are *correct to comply* —
they were instructed, and following instructions is not a defect on their side.

**RULE: once a thesis is written, I may not both (a) instruct a pane in the thesis's frame and
(b) count that pane's output as evidence for the thesis.** One or the other. If I want the frame
applied — which is legitimate, it sharpens rung 2 — then the output is **an application of the
thesis, not a test of it**, and it must be labelled as such at the moment it arrives.

### Standing of the thesis, restated a second time

**Two observations, both partially doctrine-seeded, zero measurements.** Pane 2's Q4 and pane 3's
COD-H3 T2 remain the entire independent base, and even those share `§3i`'s instruction to hunt for
what incumbents cannot do. Q5 is now filed as **application, not evidence.**

### What Q5 is genuinely worth, separated from what it is not

Considerable, and it should not be discounted because I spoiled its corroboration value:

- **It searched the problem, not a tool list** — the demo-3 lesson applied correctly. demo-3 died
  because my recovery condition named `commitlint`, was satisfied, and a tool I never named
  (`claim-check v0.6.0`) owned the niche anyway.
- **It found six real incumbents on a surface I had previously mis-chained to demo-3's death**:
  Open Knowledge (structured ledger/replay), Ethos (deterministic grounding/stale detection),
  ClaimLint (model-assisted review with an evidence trail but **no calibrated truth authority**),
  paper-verify/citeguard (citation checking), Ragas/DeepEval (context metrics). **That census stands
  on its own and is reusable by any future candidate on this surface.**
- **It kept the score at 330.** Resolving a hold is not raising a score, and pane 2 has now applied
  that rule twice unprompted.

### Ruling on demo-6

**Stays HELD at 330.** The hold's question — *does anything maintained check a notes file against a
cited evidence directory?* — is **answered: no exact owner.** So the structural objection is gone
and there is no ground to rule it out. But demand at **330** is the second-weakest in the backlog,
the rung-3 WIP slot is held by COD-H2 at **905**, and a candidate does not advance on the absence of
a competitor. **Held for demand evidence, not for structure.** Its retry condition is now a demand
question, and the incumbent census is closed.

---

## §3p demo-7's 32.5-point delta is **89% dataset knowledge**. And pane 3 corrected my correction.

**`docs/demos/duel-2/FALSIFY_demo7_MU.md` (`8757b07`) — designed AND executed the label-free half in
one unit, $0, read-only.** The most consequential single artifact in this lane so far, because it
reprices the number the lane has been quoting since the demand duel.

### The decomposition

The source **ships its own no-AI control** — `bench/heuristics.py`, Control 1, `report.md:113-119`:
**two regex features, no fitting, no labels, 91.6%** [90.4, 92.8], FPR 0.2%. Stacked:

```text
verdict-only ............ 62.6%          (the problem)
+ dataset knowledge ..... 91.6%  (+29.0)  (regex floor, NO AI)
+ Jev signals + fitting . 95.1%  (+3.5)   (the method)
```

**CIs disjoint at each step, so the 3.5 is real.** But the advertised 32.5-point "don't trust
verdicts" delta is **overwhelmingly the gap between knowing the dataset and not knowing it** — not
between verdicts and signals. **The source says so itself** (`report.md:162-165`): the five questions
were written after reading the dataset's URL-evasion taxonomy and *"target the way this dataset was
built."*

> *"A template selling the full 32.5 as transferable method gain is selling 29 points of local
> knowledge with 3.5 points of method attached."*

### demo-7 is repriced, not killed

**3.5 real points plus the calibration machinery retain value.** The transferable claim is *~3pts +
ECE/AUROC discipline*, not a 32-point miracle. That is the anti-premature-kill rule working
correctly: the honest move was repricing, and a kill here would have been the fourth over-kill of
the session.

**Transfer gate, predeclared** — on any new labelled corpus run three arms (verdict-only, regex
floor expressing the builder's own knowledge, fitted signals+head) and compute
`method_gain = acc_fitted − acc_regexfloor`. **`method_gain < 0.05` → HELD: ship the regex and the
calibration report format, not the template.** Overlapping CIs or either arm under N=200 →
**UNASKABLE, not a pass.** Pane 3 notes the failing case is *"the common case by the base rate of
the current evidence."*

**Secondary falsifier worth its own line, and it is $0:** the fitted head may reach 95% by riding
one dominant signal — committed weights show free-hosting **+9.27**, generic-sender **+12.24**
(`report.md:107`). If one weight dominates, *"the five signals story is one signal plus
decoration"* → HELD for scope-narrowing, not a kill. **Check the committed weights before building
anything.**

### What this does to §3m

**It weakens the calibration thesis's strongest-looking prop and strengthens its honesty.** §3m
pointed at demo-7's 32.5-point delta as the measured instance of *signals beat verdicts*. That delta
is now 89% local knowledge. What survives is narrower and better posed: **a regex floor that encodes
a builder's knowledge beats a verdict by 29 points, and the model's marginal contribution is 3.5
points plus a calibration report nobody else emits.** The calibration claim is therefore *not*
"models beat rules" — it is "the last few points plus the trust machinery," which is a much smaller
and much more falsifiable product claim.

### And pane 3 corrected my §3m-CORRECTION — first time a pane has audited my audit

My correction (`85415e0`) said the phishing-bench figures were *"a third-party upstream repository
we have never run"* with *"no reproduction in this lane at any stage."* **Partly wrong.** Pane 3
verified that all three headline numbers **re-derive from a vendored pinned source**
(`jev-phishing-bench@1d56e8c`, remote `github.com/anisselbd/jev-phishing-bench`): N=2000, seed
20260916, CIs throughout, 5-fold CV *plus* a stratified A/B split replication with its own seed, and
`jev-1.13.0` behind `jev-latest` with **0/2000 API errors**. It states plainly: *"the 'unverifiable
transcription' failure mode does not apply here."*

**Corrected standing of my correction:** the numbers are **not our measurements** — that part holds,
we never re-ran the benchmark. But they are **not unverified transcription either**; they are
committed aggregates in a pinned vendored clone, with split discipline visible. I overshot from
*"not ours"* to *"unverifiable,"* which is the mirror image of the error I was correcting —
over-trusting became over-distrusting, both without reading the artifact. **The instrument error is
the same either way: I ruled on a source I had not opened.**

Pane 3 also cites the correction approvingly where it belongs — *"citing upstream tables as
baselines without re-deriving them repeats the error this lane just self-corrected (85415e0)"* — and
then does the re-derivation. That is the loop working: my correction became its method.

---

## §3q §3m FAILED ITS FIRST UN-SEEDED TEST — the one voiced practitioner wants **coverage and timing**, not calibration

**The most important result of the session, and it cuts against me.** After §3o caught me seeding
pane 2 with the calibration lens, I retracted the lens for Q6 and asked for practitioners' own
words. `docs/demos/duel-2/HELD_MUH3_voice_COD.md` (`cfd4d69`) is what came back.

**Named practitioner: Pablo Rodriguez (`paroque28`), Embedded Systems Engineer.** Claude Code issue
**#39882**, opened 2026-03-27, **closed as not planned**. Verbatim:

> *"[FEATURE] PreApiCall / PostApiCall hooks to prevent secret exfiltration to API providers and
> attackers"* … *"The core need: Organizations need the ability to prevent sensitive data from
> leaving the machine through any channel"* … *"Because **PostToolUse cannot modify tool output**,
> there is no way to redact secrets from `Read` tool results, `Grep` search results, `Bash` command
> output, `Glob` file listings, `WebFetch` responses, or any future tool or MCP tool output."*

### What he asks for is a hook, not a judgment

**He never mentions calibration, confidence, probability, or uncertainty.** Pane 2 stated the
boundary deliberately and refused to cross it:

> *"It complains about **coverage and timing**: tool-level hooks cannot modify the complete outbound
> request before provider transmission. I do not translate that complaint into the lane's calibration
> vocabulary. **The external evidence is valuable precisely because it is not an echo of the
> conductor's thesis.**"*

And it named the overreach I would otherwise have committed:

> *"The evidence is **positive for runtime redaction pain**, but **silent on calibration**. Any
> document that cites this issue as proof of a calibrated-probability market need would be
> overstating it."*

**§3m is therefore UNSUPPORTED by external evidence, not refuted.** One practitioner is a sample of
one and silence is not contradiction — §3c's own rule. But this was the thesis's first contact with
a voice I did not frame, and it came back about **interception capability**, not **judgment
quality**. Two doctrine-seeded design documents, one third-party benchmark now repriced to 3.5
points of method (§3p), and **one unseeded external probe that does not mention the property at
all.** That is the honest state of the lane's central claim.

### The un-contamination worked, and that is the finding about the lane itself

**This is the first time the lane has produced evidence against the conductor's own thesis.** The
mechanism was simple and it should be standing procedure: I removed my lens from the instruction and
told pane 2 that a result contradicting me would be *more* valuable than one confirming me. It then
returned a result contradicting me, and flagged the translation error I was at risk of making.

**RULE: every thesis gets at least one probe whose instruction contains none of the thesis's
vocabulary.** A thesis that has never been tested outside its own framing is a lane artifact, not a
market fact — that exact phrase went into the Q6 packet, and Q6 is why it is now recorded as
doctrine rather than a worry.

### MU-H3: hold recovered, and a new rung-2 question opens that pane 2 set up

**Verdict: voiced-pain hold RECOVERED. Score remains 650.** Pane 2 applied *resolving a hold is not
raising a score* for the **third** time unprompted: *"resolving 'does anyone publicly voice this
pain?' answers judgeability, not product value."*

**But its own scope comparison raises the COD-H3 fork against MU-H3.** It describes MU-H3 as *"a
**deterministic** outbound sanitizer"* with *"exact runtime-value and pattern/entropy detection,
fixed-token redaction, fail-closed detector errors, per-call redaction counts and a receipt."* **A
deterministic sanitizer has no Jev-necessary stage** — which is precisely why COD-H3 was ruled out
and why demo-1 died.

The one place judgment could live is pane 2's open distinction #3: **registered exact secrets versus
unknown credentials.** Exact-match and entropy are deterministic; deciding whether an unrecognised
string is a credential is a judgment. **So MU-H3's rung-2 question is now explicit: does the
unknown-credential case exist at material rate, and does judging it beat an entropy threshold?** If
not, MU-H3 is a valuable Jev-free tool — T1 territory, like COD-H3's Fork B.

**Its baseline is also already named, by the issue itself:** a local proxy via `ANTHROPIC_BASE_URL`,
with the issue's own list of drawbacks (streaming, TLS, process lifetime, discoverability, failure
handling). Pane 2: *"That is a real baseline, not proof that a new transport wins."*

### Commit-sweep note (no history rewrite, per tick §3)

My `QUEUE.md` commit absorbed `docs/demos/duel-2/HELD_MUH3_voice_COD.md` while pane 2 was landing
it — the shared-worktree hazard that `d14387e` demonstrated. **Content intact, nothing lost, tree
clean; only that commit message misdescribes what it carries.** Pane 2 then committed the file
properly at `cfd4d69`. Amending shared `main` to fix bookkeeping is strictly worse than this note.

---

## §3r demo-7's "five signals" is **two signals plus three decorations** — and pane 2 reported the number that says so

**`docs/demos/duel-2/runs/demo7-weights-20260918T041352Z.json` (`c8e69f7`)** — the $0 check pane 3
designed in `8757b07` and left unrun, executed by pane 2 as its non-designer. Committed full-fit
weights from `jev-phishing-bench@1d56e8c`, `results/report.md:107`:

```text
sig_generic_sender ........ +12.24
sig_free_hosting .......... + 9.27
five-signal absolute sum ... 28.21
max single share ........... 43.39%   (pre-registered domination bar: 50%)
top-two share .............. 76.25%
verdict .................... MULTI, narrow two-signal concentration
```

### The pre-registered threshold did not fire, and it asked the wrong question

**43.39% < 50%, so the falsifier correctly did not fire, and pane 2 held the bar rather than moving
it.** That is the second pane in two hours to refuse to re-cut a threshold after seeing the result.

**But the bar was written about *single*-signal dominance, and the concentration is at the pair
level.** Two of five signals carry **76.25%** of the absolute weight; the remaining three carry
**23.75% combined** — roughly 8% each. So *"ask five signal questions"* is, on this corpus, **"ask
two good questions and three that barely move the fit."**

**Pane 2 volunteered the number that makes its own MULTI verdict uncomfortable.** The design asked
for max-single-share; top-two share was not required and is what carries the finding. A pane
reporting only the required number would have handed me a clean MULTI and a false impression.

### What it does to demo-7, on top of §3p

demo-7's transferable claim has now been narrowed twice by two panes working independently:

| Claim as quoted at demand time | After §3p | After §3r |
|---|---|---|
| "signals beat verdicts by 32.5 points" | method gain **3.5 pts** (29.0 was dataset knowledge) | that 3.5 comes **mostly from two signals** |
| "ask five signal questions" | — | **two carry 76.25%** |

**This is exactly the outcome pane 3 pre-declared**: *"if one weight dominates, the template's
K-question machinery is oversold for that corpus — **HELD for scope-narrowing, not a kill**."* The
pair-level concentration is the same finding one rung weaker, and the same ruling applies.

**demo-7 stays HELD at 560, scope-narrowed.** What survives is small and stateable: *on a corpus
where you can name two good signal questions, asking them and fitting a head buys ~3.5 points over
writing the builder's knowledge as regex, plus a calibration report (ECE 0.027, AUROC 0.988) that no
regex emits.* **That is a defensible claim and a much smaller product than a five-question
template.** The transfer gate in `8757b07` remains the instrument that decides any future corpus,
and it should now also report top-two share, because a corpus whose fit concentrates in two signals
does not justify a K-question framework.

**Still unclaimed and unproven:** that ~3.5 points plus a calibration report is worth shipping to
anyone. §3q's unseeded probe found a practitioner asking for **coverage and timing**, not
calibration; nothing has yet found one asking for a calibration report.

---

## §3s the 0.10 bar was written on a false premise — **the ambiguity is architectural, not pattern weakness**

**`docs/demos/duel-2/runs/codh2-sharpened-20260918T041200Z.json` (`8d120e3`).** Pane 3 executed the
sharpening I ordered in Q12, and the number barely moved: **ambiguous 0.3765 → 0.3731** against a
**0.10** bar, Wilson lower **0.3653**. *"Not close."* **COD-H2's build stays blocked.**

### Why it did not move, measured rather than assumed

```text
eval calls total .................. 165,755
matching a mutating marker ........ 155,801   (94%)
read-side ..........................   9,954   ( 6%)
dominant marker ... "tool." at 150,719 hits — the fleet drives tools THROUGH the eval tool-bridge
```

**Pane 3's conclusion: *"94% of eval is genuinely effect-capable; the ambiguous bucket is
architectural opacity, not pattern weakness."***

**So the premise under the pre-condition was false, and it was mine.** I wrote Q12 quoting pane 3's
own earlier caveat — *"this fleet's evals are predominantly read-side compute"* — and instructed a
split on that basis. **It is the opposite: 94% are effect-capable.** The original caveat was a
plausible guess about a corpus nobody had counted, I promoted it to a binding pre-condition, and the
count refuted it. **Pane 3 refuted its own caveat and my order in the same run, which is the correct
outcome and the reason the unit was worth running.**

### This is §3r's shape again: right discipline, wrong question

The 0.10 bar is well-formed and was held without flinching. But it was a **proxy** for *"are the
labels trustworthy?"*, written on the theory that ambiguity was an artifact of blunt patterns.
Measured, ambiguity is **where tool identity lives one level below where the classifier looks** —
`eval` calls `tool.read`, `tool.write`, `tool.bash`, and the tool name is opaque at the call site.
**A bar cannot be met by sharpening patterns when the information is not at that layer.**

### Ruling, pre-committed BEFORE v2.2 runs so it cannot be read as post-hoc

**v2.2 is authorised as pane 3 pre-registered it** — parse `tool.<name>` and apply the same tool
table one level down (`tool.read/tree/grep` → reversible; `tool.bash` → bash rules;
`tool.write/edit` → irreversible; `tool.task/hub` → ambiguous). It is **principled, not data-tuned**,
and pane 3 said so in the receipt.

**And here is the ruling if v2.2 also fails, decided now:**

> **The 0.10 bar stays at 0.10 for the full corpus — it is not lowered.** What changes is the
> **scope of the labelled study**: it narrows to the **destructive-bash subset — 907 turns, share
> 0.0623, Wilson [0.0585, 0.0664]** — where effect is knowable from the command itself with no
> tool-bridge indirection. In that subset the ambiguity the bar guards against does not arise.

**That is not re-cutting the number.** The bar keeps its value and its meaning; the study moves to
the population where the bar is satisfiable. **And it is where the original Q9 receipt already said
the build should aim**: *"rung-3 should target the gate at the destructive subset, not all writes."*
Two independent routes arriving at the same 907 turns is the strongest thing about this ruling.

**If v2.2 succeeds instead**, the full corpus becomes available and the study can be broader. Either
way COD-H2 proceeds; what v2.2 decides is **how wide**, not **whether**.

### Two disclosures in this receipt that deserve naming

1. **Denominator change, volunteered.** v1 dropped file-trailing turns (N=14,533); v2 closes at EOF
   (N=14,556, **+23**). Pane 3 flagged that *"comparison across versions mixes classifier +
   denominator effects"* — 0.16% of N, negligible, and disclosed anyway. **That is the discipline
   whose absence produced eight instrument errors in this lane.**
2. **Bias direction stated.** String-literal false positives were accepted and documented, with the
   note that *"bias runs against clean"* — i.e. the conservative direction, chosen deliberately and
   named.

### The terminal fork pane 3 wrote, and I accept

*"If v2.2 still clears nothing, accept tool-dispatch opacity as irreducible and rule on the
precondition itself — keep bar = block indefinitely; or accept with runtime controls."* **I reject
the first option.** Blocking the lane's only rung-3 candidate indefinitely on a bar that measures an
architectural property of the observation corpus, rather than anything about the candidate, would be
a kill by paperwork — and the anti-kill rule (§3c) applies to a candidate strangled by its own
instrument exactly as it applies to one rejected on taste.

---

## §3t EXTERNAL MARKET EVIDENCE LANDS — and it inverts the lane's leader

**Joshua supplied a community survey of what people are actually shipping on Jev: 11 `/last30days`
sweeps, 716 items, 39 candidate workflows with a named source and a real number, 9 kept.** This is
the first **external, un-seeded** demand signal the lane has ever had — not a pane's output under my
instruction, not a vendored repo's abstract. It must be adjudicated against the live backlog
immediately, and it does not favour us.

### 1. COD-H2 — the lane's only rung-3 candidate — is **already shipped, twice, by well-resourced parties**

**COD-H2 is pre-action abstention: judging whether an action should execute.** The survey's item 3
is titled *"The safety reviewer, unbundled from the harness"*:

- **Vercel, in production.** Guillermo Rauch: *"Default mode in `fx` is auto, with a safety reviewer
  analyzing every command. That reviewer runs on GPT Luna today. **Jev is up to 18x faster (p95)
  and more accurate.** It's coming to Vercel AI Gateway and likely new default."* Benchmarked by
  Pranit at **~5–18x faster and more accurate** than `gpt-5.6-luna`.
- **LangChain shipped the open version the next day**, as two lines:

```python
guardrail = AutoModeMiddleware(tools=["bash"])
agent = create_agent("openai:gpt-5.6-luna", middleware=[guardrail])
```

**§3i does not rescue this.** §3i says an incumbent that does *not* use a judgment model is a
baseline rather than an owner — that is what un-killed MU-H2 and re-opened demo-3. **These
incumbents use Jev.** They are not deterministic tools to be obliterated; they are the same
mechanism, shipped, by Vercel and LangChain.

**And the overlap is on COD-H2's exact measured surface.** `codh2-sharpened-20260918T041200Z.json`
puts the gate-relevant population at **907 destructive-bash turns** (share 0.0623). The incumbent's
API is literally `AutoModeMiddleware(tools=["bash"])`.

**I am not killing it here, and the reason is my own record.** *I kill on the first plausible
sufficient reason and stop looking* — three over-kills this session, all reversed. So COD-H2 moves
**CLEARED → HELD** on one crisp, cheap, non-author question:

> **Does `AutoModeMiddleware` abstain, or only allow/deny?** COD-H2's distinctive claim is
> *abstention* — declining, with a calibrated confidence, rather than emitting a verdict. If the
> incumbent thresholds on confidence and withholds, **COD-H2 is owned and should be ruled out.** If
> it returns a binary allow/deny with no withhold path, abstention-plus-calibration is a real wedge
> and COD-H2 survives, narrowed to that wedge.

The question is answerable by reading LangChain's published source. **It is cheaper than the v2.2
classifier round I currently have pane 3 running**, and it should have been asked before that round
was ordered.

**Ordering lesson, and it is §3k's own principle applied one level up:** I spent two units of the
lane's scarcest capacity unblocking a *build* for a product two well-resourced parties already ship.
§3k says estimate rung 4 before paying for rung 3. **The missing rule is: re-check the incumbent
field before paying for either** — an incumbent search is not a one-time rung-2 event when the
ecosystem is 3 days old and moving daily.

### 2. COD-H5 compaction-integrity is **also shipped**

Survey item 2, *"Instant compaction"*: Tamara Tran shipped `fast-jev-compaction`; Alex Volkov ran it
as a Claude plugin and reported **1M tokens → 86K in one second**; Diogo Almeida's reply — *"YES!
free coding agents from designing around the KV cache"*. Repo: `github.com/tamaratran/fast-jev-compaction`.

**COD-H5 moves CLEARED → HELD** on the same shape of question: does the shipped plugin do
*integrity* (detecting what compaction destroyed) or only *scoring-and-dropping*? Those are
different products and the distinction is COD-H5's whole claim.

### 3. demo-1's death is confirmed externally

Survey item 4 is **model routing as LangChain `ModelRouterMiddleware`** — eleven lines. demo-1 died
at rung 4 on 0.047% savings and was found to make zero Jev calls. **The external record shows the
surface owned by a maintained middleware.** No change in verdict; the retry condition is now
demonstrably unsatisfiable, which is worth recording as a closed door rather than an open one.

### 4. §3m gets its **first un-seeded external support** — and a ceiling

§3q recorded that nothing had found a practitioner asking for a calibration report. **The survey's
own synthesis, written by someone who has never read this lane's plan:**

> *"**The confidence score is the product.** Without a calibrated number to threshold on, this is a
> fast classifier. With one, it is a decision layer that knows when to stop."*

and, from the vendor docs as the survey reports them:

> *"**Threshold on confidence.** The docs tell you to treat anything under 0.3 to 0.5 as a signal to
> ask a human rather than act. This is the difference between a classifier, which hands you a
> label, and a decision system, which hands you a label plus permission to use it."*

**That is the §3m property, named independently, by an external observer, in a document I did not
frame.** It is the support §3q said was missing. **It does not resurrect the demo-7 prop (§3p) or
un-seed pane 2's Q5 (§3o)** — those remain repriced and reclassified. But the thesis now has one
genuine external corroboration alongside its two seeded designs.

**And the same survey supplies the ceiling, which I am recording in the same breath so the good news
does not travel alone:**

- **TypeSafe's own four-workflow average is 67.8% agreement** with reference answers.
- Mike Taylor's 12-passage defect test: Jev **6 of 7** defects, Fable 5.1 **7 of 7** — at ~25x
  faster and ~580x cheaper. His verdict: *"useful as an early warning system, because the
  alternative is not checking at all."*
- Hacker News, 1,863 points, on *"can't hallucinate"*: *"Sure, it can't emit an invalid type, but it
  can still emit a completely wrong valid value."* Diogo called the classification-model framing
  *"very accurate!"*

**Any candidate in this lane that needs better than ~68% agreement, or needs to beat a careful
deterministic checker on recall rather than on cost and latency, is mispriced.** demo-7's repricing
(§3p, §3r) now looks like the general case rather than one benchmark's quirk.

### 5. What the survey says about the shape that wins — which is what we keep re-deriving

> *"**Feed it candidates.** The winners never ask Jev to generate an option. They build the option
> set in code, from the DOM, the retriever, the tool trace, the launcher index, and let it pick."*

Four of our five rung-2 survivors are candidate-picking designs. That is the one place the lane's
instincts match the external record without my having seeded it.

---

## §3u COD-H2 SURVIVES, narrowed to three properties — the incumbent is binary, and that is quoted

**`docs/demos/duel-2/RUNG2_COD-H2_owned_MU.md` (`25eee0c`).** Pane 3 **installed
`langchain-typesafe==0.0.1a2` from PyPI ($0, no key) and read `auto_mode.py`, 255 lines, in full.**
Not inferred from a blog post — read.

### The incumbent's control flow, quoted (`auto_mode.py:220-226`)

```python
if request.tool_call["name"] not in self._tool_names:
    return handler(request)
response = self.classifier.invoke(self._classification_state(request))
probability = response.nouls[_QUESTION_ID].noul
if probability >= _PROBABILITY_THRESHOLD:
    return self._blocked_tool_message(request, probability)
return handler(request)
```

`_PROBABILITY_THRESHOLD = 0.5` (line 39). And the docstring settles it (lines 75-88):

> *"Calls below `threshold` execute normally. Calls at or above the threshold return an error
> `ToolMessage` without invoking the tool handler"* … *"This middleware blocks risky calls;
> **it does not request human approval.**"*

**The outcome space is exactly two.** Pane 3: *"No `clarify`, no `gather`, no `abstain`, no
`escalate`, no withhold-on-uncertainty, no confidence band, no human routing of any kind."* And a
distinction I would have fumbled: *"Classification failures propagate with the handler unsent
(fail-closed on error — sound, but **failure ≠ abstention**: it is an exception path, not a
verdict)."*

### It also audited the survey's own guidance — against my input

The survey reports vendor guidance to *"treat anything under 0.3 to 0.5 as a signal to ask a human."*
**Not implemented:** one constant at 0.5, no band semantics in 255 lines, *"a 0.49 call executes
silently; a 0.51 call errors."* Then the part that matters: *"Whether the guidance exists as stated
is itself **unverified here** — no source was given for it."*

**That is R12 discipline turned on the conductor's own source.** I passed along a survey's paraphrase
of vendor docs; pane 3 declined to treat it as established while still answering the question I
asked against it. **Third time today a pane has refused to inherit an unverified claim from me.**

### Ruling: CLEARED, narrowed to exactly three properties so it cannot drift

**§3i does not kill here** — the incumbent is Jev-powered but **does not occupy COD-H2's distinctive
claim.** The surviving wedge, in pane 3's words:

1. a **withhold outcome** distinct from both allow and error-block — uncertain evidence must route
   somewhere other than execution or refusal;
2. **calibrated confidence with coverage semantics** — selective accuracy at stated coverage, not a
   point threshold;
3. at minimum a **human-routing outcome** (`clarify`/`escalate`) — *the exact path the incumbent's
   docstring disavows.*

> *"Anything COD-H2 builds outside those three overlaps a shipped, maintained artifact and should be
> cut on sight. Inside them, no incumbent surveyed (including this one) competes."*

**COD-H2 resumes the rung-3 WIP slot**, with §3s's scope: the **907 destructive-bash turns**.

### The binding open risk, stated rather than buried: **Vercel is not ruled on**

Pane 3 explicitly refused to rule on Vercel's `fx` auto mode — *"not independently reachable from
here (search throttled, no source path given)"* — and scoped its verdict to the LangChain artifact
alone. **That refusal is correct and the risk is real:** Vercel's is the *production* incumbent, at
**18x p95 and more accurate**, heading for the AI Gateway default.

**`fx`'s safety reviewer is a closed product surface, so it cannot be settled by source-read.** I am
therefore **not blocking COD-H2 on it**, for the same reason I rejected blocking on the ambiguity bar
in §3s: *an unverifiable condition used as a gate is a kill by paperwork.* What I am doing instead is
recording it as the standing risk on the row, so that if Vercel's reviewer is ever shown to withhold
on confidence, **COD-H2 dies on that evidence and this paragraph is where it was predicted.**

### What COD-H2 must adopt from the incumbent rather than re-learn

Pane 3 quoted these to keep the wedge honest, and they become contract requirements:

- **30-message state window** with assistant/tool context (`_classification_state`, 166-179).
- **Per-tool scoping** with pass-through for unlisted tools (220-221) — *"narrower blast radius than
  a universal gate."*
- **Trace redaction**: `TracePolicy(process_inputs=omit_payload)` (line 129) — *"they thought about
  secret exposure in telemetry, which is more than most Jev wrappers do."*

**And one fact that reprices "shipped":** the package is **`0.0.1a2`** — alpha, experimental module,
API explicitly unstable. *Shipped but young.* That cuts both ways and is recorded as such: it is
weaker as an ownership claim than the survey's framing implied, and it is also a moving target.

---

## §3v COD-H5 survives as **tester-to-subject** — it can benchmark the thing that ships

**`docs/demos/duel-2/RUNG2_COD-H5_owned_MU.md` (`17f842c`).** Pane 3 read
`github.com/tamaratran/fast-jev-compaction` in full via API — 903 stars, 39 forks, MIT — README,
file tree, options table, limitations, plugin docs.

**Ruling: DIFFERENT PRODUCTS, and the relationship is stronger than distinctness.**

> *"H5 can **benchmark** fast-jev-compaction itself. … The shipped tool does not detect what
> compaction destroyed; H5 detects exactly that, **for any compactor handed to it.** Tester to
> subject is a complementary relationship, and complementary is not overlapping."*

**The shipped tool decides *before* — scores tool calls and drops the junk. COD-H5 measures *after*
— what did compaction destroy.** Those are orthogonal surfaces, and the second one takes the first
as input.

### The lane's own prior measurement supports it, with a stated limit

Pane 3 cites an A/B this lane already ran: **pruned context 1/3 recall versus summary 3/3.** Pruning
— which is what the shipped tool does — recovered one fact of three where summarisation recovered
all three. **That is direct evidence that the shipped approach loses information COD-H5 claims to
detect.**

**N = 3 facts.** It is a pointer, not a result, and I am recording it as such so nobody later quotes
"1/3 vs 3/3" as a measured lift. It earns COD-H5 a rung, not a ship.

### The bias disclosure, which is why I trust the rest of the file

Unprompted:

> *"(Familiarity note: this tree is upstream of our vendored `fast-jev-compaction@6e1da50` — same
> `src/` modules, same `hooks/fast-jev.ts` — which I read line by line during the hook bead.
> **No new claims below depend on memory of that read; all citations are to the fetched README.**)"*

**A pane naming a contamination source in its own history and firewalling against it is the exact
behaviour §3o had to invent a rule to enforce on me.** It arrived here without a rule.

**COD-H5 returns to CLEARED** at rung 2, ownership risk resolved, with its rung-3 order unchanged:
it queues behind COD-H2 because the WIP limit is one and 895 < 905.

---

## §3w-CORRECTION the census audited ME — **the 67.8% "ceiling" is not a ceiling, and the compaction A/B does not replicate**

**`docs/demos/duel-2/runs/quoted-number-census-20260918T042957Z.json` (`1fea26c`) + companion `.md`.**
Pane 2 censused 12 headline numbers, opened **8 local controls**, and found **4 external entries
whose controls were never opened.** Three of its findings land on prose I committed **within the last
two turns.**

### Correction 1 — §3t's ceiling measures agreement with a model, not correctness

`SURVEY-1`, result **`UNVERIFIED_EXTERNAL`**:

> *"Raw 11-sweep/716-item artifact absent; public account says **references were model-averaged, not
> human ground truth**." … "Ceiling not locally rederived and is **agreement-to-reference, not
> correctness**."*

**I used 67.8% as an accuracy ceiling and wrote it into a build order.** It is agreement with a
model-averaged reference. Those are different quantities, and treating one as the other is my
signature failure — *mistaking a probe's conditions for the thing measured*, the eighth instance this
session.

**The Q16 instruction does not change; its justification does.** *Claim coverage, latency, cost and
the withhold path — not accuracy* remains correct, but it now rests on **§3p, which is local and
verified**: 29.0 points of the phishing delta are dataset knowledge and 3.5 are method, CIs disjoint
at each step. **That was always the better argument and I reached past it for a borrowed number.**

### Correction 2 — the COD-H5 A/B I cited one turn ago does not replicate

`USAGE-14a`, result **`UNSTABLE_HEADLINE`**:

> *"Reduction 2047→1136 (44.43%) survives; **3–1 B-wins does not: reruns are 1–1 and 1–3, exposing
> generator variance.**"*

§3v cited *"pruned context 1/3 recall vs summary 3/3"* and I flagged it as small-N — *"a pointer, not
a result."* **The real defect is worse than small N: the ordering flips across reruns.** An unstable
comparison is not weak evidence, it is **no evidence**, and the caveat I wrote was the wrong caveat.

**What survives: the 44.43% byte reduction (2047→1136).** **What is withdrawn: any claim that
summarisation beats pruning on recall.** COD-H5's distinctness ruling (§3v) is **unaffected** — it
rests on the architectural reading that the shipped tool decides-before while H5 measures-after, not
on this A/B. But COD-H5 may no longer cite it, and if COD-H5 reaches rung 4 it must **generate its
own stable comparison**, with seeds and repeats, because generator variance is now a known hazard on
this exact surface.

### Correction 3 — the speed/cost headline is conflicted, baseline unpinned

`SURVEY-3`, result **`CONFLICTED_EXTERNAL`**: *"public source summaries attach headline to different
workflow/model baselines and **separately report ~75x/171x**. Baseline identity must be pinned before
use."* **No document in this lane may cite 193.6x/444.6x, or any speed/cost multiple, without naming
the baseline model and workflow.**

### A finding that is not about my errors: **the lane has a local calibration receipt**

`entries[7]` — `foundation/runs/20260917T224444Z.json`: **ECE .061, Brier .020, Noul 58/60, Choice
19/20.** Census verdict: *"Receipt matches numbers; no external transfer claim."*

**That is a local, verified, honest calibration measurement, and §3m never cited it.** n=60 is small
and it carries no transfer claim, but it is *ours*, it *replicates against its own receipt*, and it
is strictly better evidence than the demo-7 prop I over-claimed in §3m and the survey line I
over-read in §3t. **§3m's evidence base is now: two seeded designs, one external observer's
synthesis, and one local n=60 receipt** — and the local receipt is the only item on that list nobody
has had to correct.

### demo-2's demand rests on a README narrative

`USAGE-1a` and `USAGE-2a`, both **`UNVERIFIED`**, both with `control_exists: False`: the *"injection
probability 0.99 while the page remained readable"* and *"contradicted claim caught at confidence
1.0"* figures are `jev-mcp@6ec5efc` **README narrative with no labelled corpus and no committed
control.** Live dependencies: **demo-2's admission screen** and the **demo-6/demo-3 claim surface**.

demo-2 sits CLEARED at 700. **It moves to HELD**: not because the mechanism is wrong, but because
its demand evidence is a vendor README sentence, and this lane has now been burned three times by
headline numbers whose controls nobody opened.

### The rule this earns

**RULE: a number entering any lane document must carry its control's status — `opened`, `absent`, or
`unopened` — at the point of use.** Pane 2 built the census that proves the rule necessary; four of
twelve entries had controls nobody had looked at, and **three of my last four rulings leaned on
them.**

---

## §3x RUNG 3 PARTIAL 1 — offline mechanism green, RED arms **proven by catching two real bugs**, and **zero live Jev calls, stated**

**`docs/demos/duel-2/runs/codh2-rung3-20260918T053000Z.json`; contract `d231432`, implementation
`0f6cb2d`, receipt `198448c`.** `demos/preaction-abstention/` exists: `policy.json`,
`fixtures/cases.jsonl`, `src/{gate,jev-client,redact,run}.mjs`, `test/gate.test.mjs`.
**Suite 13/13, canned runner 12 cases, rc 0, zero mismatches.**

### The line that decides how this is graded, and pane 3 volunteered it

```json
"live_calls": { "count": 0, "model": null, "budget_stated": null,
                "note": "Partial 2 unit: small budgeted live calibration run (proposed N<=20). Not run here." }
```

**Zero live Jev calls — demo-1's exact killer.** demo-1 installed clean, passed 10/0, and ran a
hand-written token heuristic behind a Jev-shaped façade.

**The difference is total and it is the only thing that matters.** demo-1 *claimed* to be a Jev demo
while making no calls. Partial 1 **reports `count: 0`, `model: null`, names the missing work as
Partial 2, and files `NO-CLAIM offline`.** A disclosed partial is a rung in progress; an undisclosed
one is a fraud. **Partial 1 is ACCEPTED as Partial 1; rung 3 is NOT complete.**

### The RED arms discriminate, and the proof is that they caught bugs review missed

Both `verification_bugs_caught` entries carry `found_by: "failing RED arm, not review"`:

1. **A destructive force-removal case slipped to `pass`** — dollar-anchored deterministic patterns
   were matched against the **JSON serialization** (trailing quote) instead of the raw command text.
   Fix: bash matches the raw command string, other tools the serialized args.
2. **A window test asserted byte-length shrink on tiny messages** — wrapper overhead exceeded ten
   dropped small texts. Fix: assert dropped-message *absence* plus newest-message *presence*.

**This is the discrimination evidence I demanded, in its strongest form.** The lane's first RED-arm
test fired on all 16 rows and "passed"; the corrected one flagged exactly 1 of 16. Here the arms
caught a **security-relevant miss** that reading the code had not surfaced. **A test that catches a
bug its author did not know about is not decoration.**

### All three wedge properties are exercised, not merely coded

**`withhold` 3 · `escalate` 2 · `block` 2 · `pass` 3 · `pass-through` 1 · `error` 1.** Withhold and
escalate both fire and are **distinct from block** — the exact tri-state the incumbent's docstring
disavows (*"it does not request human approval"*). `pass-through` confirms the per-tool scoping
adopted from the incumbent per §3u.

### Two discipline notes worth more than the test count

**Policy beat fixture:** *"fixture boundary-low realigned TO policy (0.40 withholds per mapping),
**never the reverse**."* When pre-registered policy and a fixture disagreed, **the fixture moved.**
Third time today a pane refused to move a threshold after seeing a result.

**The credential branch was deleted:** *"credential-positive withholds **without Jev call**
(tested)."* A design judgement I did not order, and correct — **you do not ship a suspected
credential to an API to ask whether it is a credential.**

**UBS:** two criticals adjudicated **false positives** with code locations (a CLI-flag string
comparison, a `typeof` check — *"neither compares secret material"*); warnings driven to 0.

### Q8 — pane 3's score matrix audited by its non-author, arithmetic verified

`docs/demos/duel-2/runs/audit-hunt-scores-mu-on-cod-20260918T043846Z.json`:
**`AUDIT_PASS_WITH_TWO_SOURCE_FRESHNESS_LIMITS`.** Deductions re-derived — **H2 −30, H4 −20, H5 −20,
H3 −35, H1 −55**; file scores hunt **895** / rank **800**. Asymmetry argument and demo-4 category
critique upheld. Flagged: **unpinned star/release freshness**, **exact H3 code-line reproduction**.
Target chosen because it was pane-3-owned with **no prior non-author audit** — the dry-queue rule
working as written.

### Two shared-worktree incidents this turn, neither repaired by rewriting history

1. **`198448c` swept pane 2's audit file.** Pane 3 **self-reported before I asked**, stated content
   intact, asked the owner to verify; pane 2's callback cites the same sha, so it landed whole.
2. **My own §3x append was destroyed, not mis-attributed.** The danger-gate refused my commit
   (it matched the bug's *name as prose* in the message — the same
   pattern-against-a-serialization error pane 3 had just fixed in the gate). The append then sat
   uncommitted across a pane's git operation and **vanished from disk: `grep` 0 hits, no commit
   carries it.** This section is a rewrite from the receipt.

**The documented hazard understates the risk.** The tick's rule says commit an append immediately
*because attribution goes wrong*. **It can be worse than that: the work can be lost.** And the
guard can *block* the very commit the rule requires, which turns a one-line rule into a real
failure mode. **Amended rule: if a commit is refused, rewrite the message and land it in the same
turn — never leave the append sitting.**

### What Partial 2 must produce for rung 3 to close

**A small budgeted live run — proposed N ≤ 20 — with model version and call count recorded.** Until
that lands, COD-H2 has a working offline mechanism and **no evidence that Jev is in it.** That is the
one sentence demo-1 could not say about itself in time.

---

## §3y THE DEMO-1 QUESTION IS CLEARED — non-author grade confirms the Jev path is real

**`docs/demos/duel-2/runs/grade-codh2-rung3-20260918T044900Z.json` (`1fe6c30`).** Pane 2 graded the
implementation as non-author of the code. Verdict:
**`PARTIAL_ACCEPTED_HELD_FOR_LIVE_CALIBRATION_AND_UBS_PROVENANCE`.**

### The question that has haunted this lane since demo-1 died

demo-1 shipped, installed clean, passed 10/0 — and **made zero Jev calls**, running a hand-written
token heuristic behind a Jev-shaped façade. Partial 1 reported `live_calls: 0`, so the same question
was open on the same evidence. **I ordered pane 2 to attack it first.** It did:

- **The live path is real:** mock `POST https://api.typesafe.ai/v1/systemone`, model **`jev-1.13.0`**,
  a **typed `Noul`** question, and the returned probability **`.66` drives the `withhold` outcome.**
  Correct endpoint, correct pinned model, typed question, and the probability actually determines the
  decision rather than decorating it.
- **The no-key run exits `rc2` with no call.** **This is the decisive difference from demo-1.**
  demo-1's defect was not "no calls today" — it was *a heuristic that could stand in for the model
  forever*. Here, absent a key, the thing **refuses and exits non-zero**. There is no fallback
  heuristic to hide behind, because there is no fallback.

**So the Jev dependency is structural, not cosmetic.** `live_calls: 0` now means *"not yet run"*
rather than *"not actually used"* — and those were indistinguishable from the receipt alone, which is
exactly why a non-author had to read the client.

### Independent RED-arm probe: 9/9

Pane 2 planted its own defects rather than re-reading pane 3's: **RED probe 9/9.** Combined with the
two bugs the arms caught during the build (`found_by: "failing RED arm, not review"`), the arms are
now **confirmed to discriminate by two parties using different methods.** The lane's first RED-arm
test fired on all 16 rows and "passed"; this is the opposite of that failure in every respect.

### What the hold is for, and both items are legitimate

1. **Live calibration** — Partial 2. Still the gate on rung 3 closing.
2. **UBS provenance** — the two criticals pane 3 adjudicated as false positives (a CLI-flag string
   comparison, a `typeof` check) were dismissed with code locations, and **pane 2 could not verify
   the provenance of that adjudication.** That is the correct response to an unverifiable claim:
   hold, do not accept and do not reject.

Pane 2 also correctly scoped out an irrelevance — *"max-weight Q10 not relevant here"* — rather than
importing a finding because it was recent. And its `NO-CLAIM` is exact: *no live provider/model, no
calibration, no UBS rerun, no production-safety claim.*

### State of COD-H2 after the grade

**Rung 3, Partial 1 accepted by a non-author, held for Partial 2.** Every structural doubt raised
against it has now been answered by someone other than its author:

| Doubt | Answered by | Result |
|---|---|---|
| Demand real? | pane 3 rung-1 blind score | **905**, top of backlog |
| Jev-necessary stage? | pane 3 rung-2 | cleared on structure |
| Falsifiable? | pane 3 Q1 design | pre-registered, executed |
| Surface exists? | pane 3 Q9 | **HEALTHY**, 14,556 turns |
| Already owned? | pane 3 Q14 | incumbent is binary; **wedge survives** |
| Jev actually in it? | **pane 2 Q17** | **yes — rc2 without a key** |
| Calibrated in practice? | — | **OPEN: Partial 2** |

**PROMOTED remains 0, and that is still the correct state.** A candidate that has cleared six
independent doubts and holds a working offline mechanism is not promoted; it is one live run from
being judgeable at rung 4.

### Pane 2 filed a QUEUE DRY callback — the first true one

The dry-queue rule has stood in `tick.md` since it was written with the note *"(3) is a success. It
has never yet been true."* **It is true now**, for pane 2: every unit it was eligible for is DONE.
That is not idleness, it is a correctly reported exhaustion, and the conductor owes it new units —
which is the whole point of requiring the callback.

---

## §3z THE STATE-OF-RECORD GATE RE-VERIFIED AT 17 ROWS — and I caught my own broken probe **before** recording a false defect

**Conductor's own work this tick, per §4: all three panes were genuinely working, so no packet was
manufactured.** `scripts/lane-status.sh` is the instrument every tick's status depends on, **I wrote
it**, and its discrimination had been measured **exactly once** — on a 16-row file, before the file
grew to 23 lines / 17 candidates and before dozens of subsequent runs. **Trusting an instrument
because it passed once is the error class this lane has logged eight times.**

### Result: the gate is sound, and now on stronger evidence than the original test

| Arm | Expected | Measured |
|---|---|---|
| Unmodified, 17 rows | pass | `OK: 17 candidates, every cited receipt exists`, **exit 0** |
| 1 bad receipt, **first** data row (7) | fail, count 1 | `FAIL: 1 of 17`, **exit 3** |
| 1 bad receipt, **last** data row (23) | fail, count 1 | `FAIL: 1 of 17`, **exit 3** |
| **All 17** rows bad | fail, count 17 | `FAIL: 17 of 17`, **exit 3** |
| Restored | pass | **md5 identical** to the pre-test file, exit 0 |

**Both boundary rows were tested deliberately** — an off-by-one at the first or last data row is the
live risk after a file grows, and the original single-arm test could not have seen it. **And the
count is right in every arm**, which is stronger than flagging: a detector that said "FAIL" without
counting could be firing blindly.

### The part worth recording is that my first probe was broken in three ways at once

My first run reported **exit 0 on a planted bad receipt** — apparently a gate defect, apparently
serious, and I was one paragraph from writing it into this file. **Every part of that was my probe:**

1. **I edited comment lines believing they were data rows.** `STATUS.tsv` lines 1–5 are `#` comments
   (2 fields) and line 6 is the header; data starts at line **7**. ARM 1 planted its bad receipt on
   **line 5 — a comment** — so the gate ignoring it was *correct behaviour*.
2. **I miscounted my own plant.** ARM 2 claimed "three bad receipts" but hit lines 3/9/15, one of
   which is a comment. **Two landed, not three** — and the gate's own output said so, which I did
   not read.
3. **I grepped for a string the output never emits.** `grep -c 'GONE-'` returned 0 because the
   renderer prints candidate and reason columns, **not the receipt path.** That is
   `NEGATIVE_EVIDENCE.md` **R12 verbatim** — *grepping for the expected line and treating the miss
   as the finding.*

### Why this instance is different from the previous eight

**I checked the probe's conditions before concluding about the thing measured** — `awk -F'\t' '{print
NR": f1=["$1"]...}'` on the first six lines, which took one command and immediately showed lines 1–5
were comments. **The eight prior instances were all recorded as findings first and corrected
afterwards.** This one never entered the record as a defect.

**That is the whole difference between a lane that measures and a lane that generates plausible
prose**, and it is the ninth instance of the same class — so the rule earns restating in operational
form: **before reporting what an instrument shows, print what the instrument was pointed at.**

### Standing consequence for this file

`lane-status.sh` may be trusted as the state of record **at 17 candidates / 23 lines**, with
discrimination verified at both boundaries and at saturation. **When `STATUS.tsv` next changes shape
— a new column, a row inserted above line 7, a candidate count past ~25 — the arms above must be
re-run.** The original test's expiry was invisible precisely because nothing recorded what it had
been run against.

---

## §4a CAUSE 5 OF PANE IDLENESS, AND IT IS THE WORST ONE: **a send that reports success and never delivers**

**Measured 2026-09-18, confirmed by the receiving pane's own report.** Joshua has asked twice *"are
you not dispatching them, are they not calling back, what is failing"*. `tick.md` §0b records four
causes, two of them conductor defects. **This is the fifth, and it invalidates the evidence the other
four were diagnosed with.**

### What happened

Both panes measured **`IDLE_PROVEN`, age 1097s (~18 minutes)**, with **no new commits and no fresh
files** — so not a silent finish. I asked pane 2 directly, per §1. Its answer:

> **`(c) Dispatch received now; Q18-Q20 work had not started before this message. No block/rate-limit.`**

**My Q18–Q20 dispatch never arrived.** And `ntm --robot-send` had printed
**`"Sent to 1 agent(s) successfully"`**.

### The distinguishing variable, and I had it before I asked

That dispatch was a **~2,900-character single-line inline `--msg=` string.** Every dispatch this
session that produced a callback was sent with **`--msg-file=`**. The correlation is total across the
session:

| Form | Dispatches | Callbacks |
|---|---|---|
| `--msg-file=<path>` | all of them | **all landed** |
| one long inline `--msg="…"` | 1 | **never arrived** |

**`tick.md` already contains the right principle in a weaker form** — *"sender success is not
receiver receipt"* — filed under aborted tool calls. **This is the strong form: the sender printed an
explicit success line for content that never reached the pane.** An aborted call at least leaves you
uncertain; this one lies.

### Why this is the worst of the five causes

The other four are visible in the artifacts once you look: a wait condition with no check, a packet
count skew, a throttled pane given oversized units, an append that was never pushed. **This one is
invisible by construction.** The conductor sees success, the pane sees nothing, and the resulting
silence looks exactly like a lazy or stuck worker.

**And I was one step from mis-attributing it.** My previous tick reported both panes idle and I began
diagnosing *them*. The only reason the cause is recorded correctly is that §1 says **ask the pane
directly** — and pane 2's one-line answer overturned my framing in eleven words.

### Rules, effective immediately

1. **Never inline `--msg=` for anything beyond a single short line. Always `--msg-file=<full path>`,
   and `wc -c` the file first** so the size is in the record.
2. **A send's success line is not delivery evidence. The pane's leg-1 callback is the only delivery
   evidence that exists.** Treat an un-acknowledged dispatch as undelivered after one tick, and
   **re-send from a file rather than diagnosing the pane.**
3. **When a pane is idle with no fresh artifacts, the first hypothesis is now my delivery, not their
   diligence.** Four of five recorded causes are conductor defects; the base rate says suspect
   myself first.

### Leg 2 is dead, fourth independent measurement

`am inbox --project ~/Developer/jev --agent CyanFalcon` → **`"count": 0`**, again, while every pane
callback this session arrived via leg 1. **Four checks, four zeros, two panes, ~20 delivered units.**
I have now told both panes in writing to stop spending effort on leg 3 — *"dead transport, my defect
to fix, not yours."* A four-leg contract with one permanently dead leg is a three-leg contract that
wastes worker effort on every unit.

### Partial 2 resized in the same message, per §0b Cause 3

Pane 3 is throttled. I had written *"N ≤ 20"*; the resend states **N ≤ 20 is the ceiling, not the
target, and N = 5 with a receipt beats N = 20 that never lands** — plus the key's verified location
(`/tmp/.tskey`, present, mode 600, 108 bytes) shipped as `ls -l` with a non-blocking fallback, and an
explicit statement that **whether rung 3 can close on the offline mechanism alone is my ruling to
make, not a reason for a pane to sit.**

---

## §4b RUNG 3'S LIVE GATE IS SATISFIED — 6 real Jev calls, all three outcomes, pin verified

**`docs/demos/duel-2/runs/codh2-rung3-partial2-20260918T055000Z.json` (`e7c9a19`).**

```text
6 calls (1 probe + 5 cases) · ceiling N<=20 stated, 6 used
model jev-1.13.0 — "requested pin and resolved version identical"
p spans 0.02 → 0.94 · outcomes: pass 1 · withhold 2 · escalate 2
```

**All three wedge outcomes are driven by live probabilities**, across the full range. This is the
property `AutoModeMiddleware` provably lacks (§3u), now exercised against the real endpoint rather
than a mock.

**The pin check matters more than it looks:** *"requested pin and resolved version identical"* —
`jev-latest` resolving to something other than `jev-1.13.0` would have silently invalidated every
number. Nobody asked for that check.

### The single mismatch is the threshold working, and the analysis is correct

`boundary-high` expected `pass`, returned **`p = 0.74`**, and **withheld — one point below the 0.75
line.**

> *"1 point below the 0.75 line: threshold boundary working as designed, not a mechanism failure.
> Live agrees with canned on 4/5 across the full range (0.94/0.48/0.06/0.02). **No calibration claim
> at N=5.**"*

**At N=5 you cannot distinguish "the fixture's expectation was wrong" from "live is calibrated
slightly differently than the mock", and pane 3 claimed neither.** What it claimed is the only thing
the data supports: **the mechanism routes on the live probability.** `NO-CLAIM: no accuracy, coverage,
or calibration at N=5` — which is exactly right, because coverage semantics are a **rung-4** claim
needing a real N.

**And it superseded rather than edited:** *"supersedes … (offline partial; **that file stands
unedited**)."* §5 doctrine applied without being cited.

## §4c UBS provenance is UNASKABLE — and the broken instrument is the scanner

**`docs/demos/duel-2/runs/ubs-provenance-codh2-20260918T052441Z.json` (`4e23f75`).** Pane 2 settled
the hold it had raised itself, by doing the work rather than deciding:

- Reran UBS in **JSON, SARIF and verbose** modes, ~19s, read-only.
- **All modes still count 2 criticals and emit no per-finding locations.**
- The three candidate sites (`run.mjs:48`, `jev-client.mjs:17`, `gate.mjs:66`) are quoted and are
  **not secret comparisons** — *"but cannot map to critical IDs."*

**Verdict `UNASKABLE_PROVENANCE_HOLD` for both criticals, and it is the correct verdict.** Not
`FALSE_POSITIVE_CONFIRMED` (unprovable), not `REAL_FINDING` (no evidence). **A scanner that reports a
count without locations cannot be adjudicated** — the unverifiable thing here is the *tool's output
format*, not the code.

**And the cost ruling is the part I would have got wrong:** *"Rerun once was worth it; repeat same
mode is not."* A third pass in the same mode would have produced the same countless count. Pane 2
priced the verification and stopped — `NO-CLAIM: no suppression, no source change, no false-positive
ruling.`

### Ruling: this does not gate rung 3, and the reason is already precedent

**An UNASKABLE cannot block a rung indefinitely** — that is the kill-by-paperwork I rejected for the
ambiguity bar (§3s) and for Vercel's closed surface (§3u). Same handling, third time:

> **Recorded as a standing risk on COD-H2, not a gate.** Two criticals exist *by count*; every
> candidate site a human could find is benign; the tool will not say which sites it flagged.
> **Resolution condition: a UBS version (or an alternative scanner) that emits per-finding
> locations.** If that arrives and either finding is real, COD-H2 takes the hit and §4c is where it
> was predicted.

**What is explicitly NOT claimed: that the demo is secure.** Two unlocated criticals in a four-file
demo is a bounded, disclosed, unresolved risk.

## §4d PANE 3 WAITED FOR A DISPATCH OF A UNIT IT HAD ITSELF NAMED — and that is a contract defect

Pane 3's status answer was **`(c)`** — never received the Partial-2 dispatch. **I never sent one.**
Partial 2 was pane 3's *own* `next` field in its Partial-1 receipt, and `tick.md` §2 says plainly:

> *"The REPLY-VIA `NEXT` field is therefore **not a suggestion to the conductor**: it is the pane's
> own next unit, named in the packet, **which it self-claims.**"*

**So the rule exists and did not take.** Measured pattern: pane 3 has reported **`NEXT dry-queue`
three times while eligible units were open**, and has now waited once on a unit it authored itself.

**This is a contract-comprehension gap, which makes it mine.** Every packet I sent carried *"take the
next unit yourself"* as a sentence in a wall of text. **A rule buried in prose that a pane
demonstrably does not execute is an unshipped rule.** Fix, effective now: **the self-claim
instruction goes in the first two lines of every packet, and every packet names the pane's next TWO
units explicitly by ID** — so "self-claim" has a referent instead of being an instruction to invent
one.

---

## §4e CLEAN-CLONE PASSES — 13/0, and the install story is the absence of one

**`docs/demos/duel-2/runs/codh2-cleanclone-20260918T060000Z.json` (`b37eb5f`).**

```text
git clone -q <repo> /tmp/jevclone   rc=0   (committed state only)
node --test          13 pass / 0 fail / 0 skip   exit 0
runner               12/12 fixture match, 0 mismatches   exit 0
demo-1 bar 10/0  ->  MATCHED AND BEATEN
```

**Three details raise this above a test count:**

1. **Zero dependencies, node stdlib only** — *"Install story is the absence of one, verified by
   running with no npm step."* There is no install step to fail, and that was verified rather than
   assumed.
2. **Committed state only** — *"untracked sibling work excluded by construction."* In a worktree
   this dirty, a clean-clone test that accidentally included untracked files would prove nothing.
   That risk was named and structurally excluded.
3. **The clone was left at `/tmp/jevclone`** — *"`rm -rf` is guardrail-denied, **disclosed not
   hidden**."* It hit a guardrail, did not attempt a bypass, and reported the residue.

**And pane 3 self-claimed Q22 in the same callback — *"starting now"*.** The §4d fix (self-claim in
the first two lines, next two units named by ID) **took on the very next packet.**

## §4b-CORRECTION — I credited an assertion as if it were a check

**`docs/demos/duel-2/runs/grade-codh2-partial2-20260918T055000Z.json` (`47d9e54`), pane 2, non-author
of the code.** Verdict: **`PARTIAL_ACCEPTED_HELD_FOR_CALL_PROVENANCE_AND_N5_LIMITS`.**

What it confirmed: the receipt is **internally consistent** — 6 calls (1 probe + 5 cases),
`p = .02–.94`, `pass 1 / withhold 2 / escalate 2`, and `boundary p=.74` withholding under `.75`
**exactly**. The source client is **real** (its own Q17 established `rc2` with no key and no
fallback).

**What it refused to accept, and it is right:**

> *"pin identity and per-call live provenance are **asserted, not receipt-proven**."*

**In §4b I wrote that the pin check *"matters more than it looks… nobody asked for that check."*
There was no check.** The receipt *states* `"requested pin and resolved version identical"`; it
carries no response id, no timestamp, no usage block, no resolved-model field echoed from the wire.
**I praised a sentence for being evidence.** That is the same class as §3w — citing something that
reads like a measurement — and it is the tenth instance, caught this time by a pane rather than by
me.

**The distinction that matters, stated precisely:**

| Claim | Status |
|---|---|
| The client code performs a real HTTP call and cannot silently fall back | **proven** (Q17: `rc2`, no fallback) |
| The mechanism routes on a returned probability | **proven** (offline + live, consistent) |
| *These six calls* went over the wire | **asserted only** |
| The resolved model was `jev-1.13.0` | **asserted only** |
| Accuracy / coverage / calibration | **not claimed**, N=5 forbids it |

**Rung 3 therefore does NOT close.** Every other gate is satisfied — real client, discriminating RED
arms, three live-driven outcomes, clean-clone 13/0, pre-registered policy, non-author grades on both
partials. **The one remaining item is cheap and specific: re-run with per-call response provenance
captured.** Queued as Q24.

**Why I am not waving this through on "the client is obviously real":** because that is precisely the
inference demo-1 invited. demo-1's tests passed, its install was clean, and its code *looked* like a
Jev demo. The lane's entire method is that **a claim is worth what its receipt can show**, and a
receipt that asserts liveness proves only that its author believed it.

---

## §4f FIRST MEASURED BASELINE DEFEAT IN THIS LANE — entropy has no operating point

**`docs/demos/duel-2/RUNG2_MU-H3_entropy_COD.md` (`6dc570d`), pane 2 as non-author of MU-H3.** The
§3q question — *does judging unknown credentials beat a Shannon-entropy threshold?* — is answered
with numbers, no Jev call, no key, no real secret.

Sentinels: **5 known-pattern credentials** (`AKIA`, `ghp`, `xox`, `sk-live`, private-key header),
**7 unknown credentials** (random base64/hex, bearer, OAuth, JWT, readable password), **11 benign**.

| Shannon threshold | Unknown recall | Benign FP | **Combined precision** |
|---|---|---|---|
| 3.0 | **7/7 = 100%** | 11/11 = 100% | **38.9%** |
| 3.5 | **7/7 = 100%** | 10/11 = 90.9% | **41.2%** |
| 4.0 | 5/7 = 71.4% | 7/11 = 63.6% | **41.7%** |
| 4.5 | 4/7 = 57.1% | 6/11 = 54.5% | **40.0%** |

**The column the callback did not name is the one that decides it: combined precision never exceeds
41.7% at any threshold.** More than half of everything entropy flags is benign, *at every operating
point*. And the failure is structural, not a tuning problem:

> *"Raising the threshold reduces false positives **only by missing unknown classes**: the 4.0
> threshold misses the unknown hex and readable-password forms, and 4.5 misses more. The result is
> not a clean Jev-free solution; it is a recall/false-positive tradeoff."*

**At full recall it flags essentially everything; at tolerable noise it misses 43% of credentials.
There is no sweet spot to tune toward.**

### Why this result is a first for the lane

**Every prior encounter with a deterministic baseline went the other way:**

- **demo-1** failed to beat upstream routing — **0.047%** — and died at rung 4.
- **COD-H3** died because **four of five stages were deterministic** and the fifth was served by a
  committed table.
- **demo-7** was repriced when the source's own **no-AI regex control hit 91.6%**, making 29 of its
  32.5 points dataset knowledge.
- **demo-9** remains conditional on *beating* `ubs` rather than subsetting it.
- **MU-H2** has a designed gate and no run.

**MU-H3 is the first candidate in this lane to measure the deterministic alternative and show it
fails.** That is "baseline and obliterate" executed in the correct order — measure the baseline
first, then claim the gap — rather than asserting a gap and hoping.

### Ruling

**MU-H3 moves HELD → CLEARED, conditionally, at rung 2**, in pane 2's own words: *"cleared
conditionally on the unknown-candidate wedge, **not as a completed implementation**."*

**The wedge is now narrow and measured:** MU-H3 may claim only the **unknown-credential** case — the
one entropy cannot serve. The known-pattern cases (`AKIA`, `ghp`, `xox`, `sk-live`, key headers) are
deterministic and must stay deterministic; per §3u's precedent, anything MU-H3 builds over *those*
overlaps a solved problem and gets cut on sight.

**And the limit is stated, not buried.** `NO-CLAIM: no real prevalence or production safety.` This
proves entropy's tradeoff **on 23 hand-authored sentinels**. It does **not** establish how often
unknown credentials occur in real outbound traffic — which is exactly what §3q asked as the second
half of the question (*"does the unknown-credential case exist at material rate"*) and remains
**open**. MU-H3's rung-3 eligibility therefore requires a prevalence number, and it queues behind
COD-H2 regardless, because the WIP limit is one and 650 < 905.

**Also worth recording as method:** pane 2 ran `redact.scan()` against local sentinel bytes only —
*"No candidate was sent to a model"* — so the probe that asks whether a judgment model is needed was
itself conducted without one. That is the cheapest possible form of this question, and it was
available all along.

---

## §4g SECOND UNSEEDED EXTERNAL VOICE — and it points the same way as the first, away from §3m

**`docs/demos/duel-2/HELD_demo2_demand_COD.md` (`ad7d8c6`), pane 2 as non-author of demo-2.**
`DEMAND_HOLD_RECOVERED`, **score unchanged at 700.**

**Named practitioner: Jörg Michno (`joergmichno`), Embedded Systems Engineer.** Google **MCP Toolbox
issue #2844**, verbatim: database content entering LLM context, asking for **output sanitization
before context**.

That replaces the `jev-mcp` README narrative (`USAGE-1a`, `UNVERIFIED`, `control_exists: false`) that
§3w demoted this candidate for. **demo-2's demand now rests on a filed issue by a named engineer
instead of a vendor sentence.**

### The pattern across two unseeded probes is now the strongest external evidence the lane has, and it is negative

| Probe | Practitioner | What they asked for | Mentions calibration? |
|---|---|---|---|
| §3q (Q6) | Pablo Rodriguez, `paroque28` | `PreApiCall` hook — redact before the request leaves | **no** |
| §4g (Q20) | Jörg Michno, `joergmichno` | output sanitization **before context** | **no** |

**Two named practitioners, two different surfaces, two independent searches, and neither mentions
calibration, confidence, probability or uncertainty.** Both ask for **an interception point that does
not exist**. And pane 2 flagged it unprompted *both times* — *"No calibration framing"* — after I had
explicitly retracted my lens for Q6 and never reinstated it.

**§3m's standing is therefore worse than §3q left it.** The thesis now stands on: two designs I
seeded (§3o), one third-party benchmark repriced to 3.5 points of method (§3p) and further narrowed to
two signals (§3r), one external survey synthesis whose ceiling figures the census ruled
`UNVERIFIED_EXTERNAL`/`CONFLICTED_EXTERNAL` (§3w), and **one local n=60 receipt that nobody has had
to correct.** Against it: **two for two unseeded practitioner voices asking for coverage and timing.**

**The honest reading, stated plainly:** *calibration may still be the right engineering wedge —
`AutoModeMiddleware` provably lacks it (§3u), and entropy provably cannot substitute for judgment on
unknown credentials (§4f).* **But it is not what the people with the pain are asking for.** Those are
different claims, and conflating them is how a lane talks itself into building the wrong thing. **What
practitioners voice is a missing hook; what the engineering evidence supports is calibrated
abstention behind that hook.** The hook is the product; the calibration is how it decides.

**That reframing is the single most useful thing the external probes produced**, and it took two panes
independently refusing to translate complaints into my vocabulary to surface it.

### Fourth unprompted application of the scoring rule

Score stayed at **700**. Pane 2 has now applied *resolving a hold is not raising a score* **four
times without being reminded** — demo-7, MU-H3, demo-6, demo-2. It is no longer a rule I enforce; it
is how that pane works.

---

## §4h MU-H2's INCUMBENTS MEASURED — the baseline is **scoped, not bad**, and a pane refused to spend money to close its own gate

**`docs/demos/duel-2/runs/muh2-baseline-partial-20260918T064500Z.json` (`7cfe98c`)**, corpus harness
`7ddb7de`. Pane 3 executing the gate **pane 2 designed** (`75cfb9f`) — author of the candidate,
executor of someone else's test.

### The corpus is the first immutable manifest-backed fixture set this lane owns

**20 cases, committed immutable, `demos/doc-drift/corpus.json` carrying bytes + sha256 per file.**
Truth: **4 accurate · 14 drifted · 2 unknown.** Classes: valid-anchor 4, reference-drift 4,
semantic-default 4, behavior 3, coverage 3, ambiguous 2.

### D0 — `drift v0.10.1`: MEASURED, and scored honestly

sha-verified release asset, run **from `/tmp` so the binary never enters the tree**. Fresh → pass;
mutated → fail with `stale/changed_after_baseline`. Verdict:

> *"D0 detects **file-change, not semantic truth** (as designed)."*

**It refused to score an incumbent badly for doing its actual job** — the §3i posture applied
without prompting. Subset semantics recorded rather than hidden: *"4 anchored valid cases only;
corpus root sees 0 docs (no recursion into case dirs)."*

### D1 — `docverity 0.5.0 --no-llm`: MEASURED, and the number is a **coverage** result

- valid: **3 ok + 1 ok-with-unverifiable**
- reference-drift: **2 flagged correctly**
- **semantic / behavior / coverage / ambiguous — all 14 cases: SILENT, zero false verdicts**

**So 5 of 20 fully correct, 14 silent, 1 unverifiable.** *(The callback's `5/20 + 15 silent`
reconciles exactly once `ok-with-unverifiable` is counted as not-fully-correct — I checked before
flagging a discrepancy, and there wasn't one.)*

**The shape of this result is the whole point: the incumbent is silent, not wrong.** Zero false
verdicts across 14 cases it cannot address. **That is a scoped tool behaving correctly at its
boundary**, and it means MU-H2's opportunity is precisely the 14 semantic cases — a *coverage* gap,
not an accuracy contest. It also makes pane 2's `coverage ≥ 80%` threshold the operative one of its
six.

Subset caveat again volunteered: *"repo-root run misattributes relative paths (recorded, not
used)."*

### D2 — UNASKABLE, and the reason is doctrine

> *"default model `claude-opus-4-8` needs an Anthropic key this lane does not hold; **no spend
> authorized for vendor-model baselines**."*

**A pane declined to spend money to close its own gate.** It could have justified a small charge —
it was measuring its own candidate's competition, and a favourable D2 result was not even in its
interest. **Recording this as standing doctrine: an unauthorized spend is never the cheapest path to
a verdict; `UNASKABLE` is.** Third `UNASKABLE` accepted in this lane rather than converted into a
convenient answer (§4c UBS, §3q voice, here).

### State

**MU-H2 remains CLEARED-conditional at rung 2**, score **430**, queued far behind COD-H2. What the
partial establishes is the *incumbent side* of its head-to-head, measured on an immutable corpus. Its
own judge's run against the same 20 cases is Q25; **pane 3 runs it and reports numbers, pane 2
grades**, because its author may not adjudicate it.

---

## §4i LIVENESS IS RECEIPT-PROVEN — and the absent fields set the ceiling on what any receipt here can ever prove

**`docs/demos/duel-2/runs/codh2-rung3-provenance-20260918T070000Z.json` (`2818a57`).** The gate pane
2 held Partial 2 on — *"pin identity and per-call live provenance are asserted, not receipt-proven"* —
is discharged with wire evidence:

```text
5 live calls · status 200 on each
model requested jev-1.13.0 · MODEL ECHOED jev-1.13.0 ON ALL 5
per-call usage captured (439/20, 444/20, …) · totals 2,175 in / 100 out
per-call answers block: typed noul, probability matching the recorded verdict
```

**§4b-CORRECTION is now closed the right way round.** I had credited a *sentence* asserting the pin
matched; the receipt now carries **the model as echoed by the response**, five times. That is the
difference between an author's belief and a reader's verification, and it took a pane refusing my
over-credit to get here.

**Why this is sufficient rather than merely more:** an offline path does not produce `status: 200`
with **input-token counts that vary per case** (439 vs 444, tracking payload size) and a uniform
20-token output consistent with a single typed `noul`. The probabilities also **reproduce Partial 2's
values** (0.94, 0.48) across an independent run.

### The absent-field finding is the most valuable line in the receipt

> *"`response_id`: no id field in any response body (checked: answers/model/usage only). `timestamp`:
> no created/timestamp field in any response body. **Absent fields bound the ceiling: no receipt in
> this lane can cite a response id or server timestamp for these calls; liveness rests on
> status + model-echo + usage + probabilities.**"*

**I asked for absent fields to be reported as findings and this is why.** The lane now knows its
**maximum achievable liveness evidence** — not as a guess about API design, but checked against the
response bodies. **No future receipt here can be held to a standard the API cannot meet**, and no
future grader can demand a response id without first changing the API. That converts an open-ended
"prove it harder" into a bounded, closed question.

### Rung 3 gate status — and I am not closing it myself

| Gate | Status |
|---|---|
| Real client, no silent fallback | proven — Q17, `rc2` without a key |
| RED arms discriminate | proven twice — 2 bugs caught in build, independent 9/9 probe |
| Three wedge outcomes on live probabilities | proven — Partial 2 |
| Clean-clone install | proven — **13/0**, beats demo-1's 10/0 |
| Policy pre-registered | proven — fixture realigned *to* policy |
| **Liveness / pin receipt-proven** | **proven — §4i, model echoed 5/5** |
| UBS provenance | **UNASKABLE**, standing risk, not a gate (§4c) |
| Accuracy / coverage / calibration | **not claimed** — rung 4, needs real N |

**Every gate is satisfied. Rung 3 is not closed by me, because pane 2 raised the hold and pane 2
discharges it.** Closing a rung on the author's own receipt is precisely the authorship violation
this gauntlet exists to prevent — and the author here is the pane that produced the provenance.
**Queued as Q26: a non-author confirmation that the hold is discharged, or a statement of what is
still missing.**

---

## §4j **RUNG 3 CLOSES** — first in this lane's history. And the variance sits exactly where the threshold does.

**`docs/demos/duel-2/runs/discharge-codh2-rung3-20260918T054357Z.json`, pane 2 as the pane that
raised the hold: `HOLD_DISCHARGED at declared ceiling`.**

It re-derived independently: 5 status-200 calls, model `jev-1.13.0` **echoed 5/5**, usage varying
**439 / 444 / 438 / 434 / 420**, typed `Noul` at **.94 / .48 / .06 / .02 / .70**. And it settled the
one question I could not check myself — **the absent `response_id`/`timestamp` claim is an "honest
bounded field"**, genuinely absent rather than merely unrequested.

> *"No rung3 blocker remains; **N=5 calibration and no server correlation remain standing limits**."*

**COD-H2 pre-action abstention advances to rung 4.** Ten doubts, every one answered by a pane other
than the claim's author, and **zero of them by me.**

### The finding neither pane flagged, and it is the rung-4 design constraint

Comparing the two independent live runs case by case:

| case | Partial 2 | Q24 provenance | moved |
|---|---|---|---|
| `pass-clean-ls` | 0.94 | 0.94 | — |
| `withhold-keysearch` | 0.48 | 0.48 | — |
| `escalate-pipe-sh` | 0.06 | 0.06 | — |
| `boundary-low` | 0.02 | 0.02 | — |
| **`boundary-high`** | **0.74** | **0.70** | **−0.04** |

**Four of five probabilities are bit-identical across runs; the only one that moved is the boundary
case.** That is a far stronger result than the reproduction I cited in §4i:

1. **It settles liveness beyond the ceiling argument.** Four identical values could be a fixture. A
   fifth that *moves* cannot be — and it moves on precisely the case where a real model is least
   certain.
2. **It profiles stability: the model is exact where confident and variable at the boundary.** 0.94,
   0.48, 0.06 and 0.02 all reproduce to the digit; 0.74 → 0.70 does not.
3. **It partly re-opens a ruling I accepted too cheaply.** §4b accepted *"boundary-high withholding
   at 0.74 is the threshold working as designed."* Still true — **but the same input now yields 0.74
   or 0.70 depending on the run, so which side of a fixed 0.75 line a borderline case falls on is not
   a property of the input alone.** A point threshold over a variable output makes borderline
   decisions partly stochastic.

**And that is an argument for COD-H2's own wedge, from data nobody set out to collect.** §3u's second
property is *"calibrated confidence with **coverage semantics** — selective accuracy at stated
coverage, **not a point threshold**."* The incumbent ships a single constant at 0.5 and inherits this
exact defect. **The variance profile measured here is the empirical case for the design choice COD-H2
already made** — which makes it rung 4's central measurement rather than a footnote.

**Rung 4 requirement, now specific:** repeated runs per case at a real N, reporting **selective
accuracy at coverage levels** and **per-case variance**, with the boundary band treated as its own
population. Point-threshold accuracy is not a rung-4 answer, because the threshold is the unstable
part.

### Q25 — MU-H2's judge is wired, and the receipt says only that

`muh2-judge` receipt (`60ca31a`): **20/20 wiring, gate `WIRING-ONLY`, `NO-CLAIM wiring`.** The
harness runs every case in the immutable corpus and **no correctness claim is made.** Correct
scoping: MU-H2's six-threshold gate is still unmeasured, and pane 2 grades it when a scored run
exists (Q27).

### Third sweep — and the panes now fix the process themselves

`60ca31a` swept pane 2's two Q26 discharge files into pane 3's Q25 commit. **Both panes disclosed it
independently**, and pane 3 proposed the remedy unprompted: **"split verify/commit steps."** Content
intact, both files present, tree clean — **no history rewrite**, per standing ruling. Three sweeps
this session, three self-reports, zero attempts to hide one.

---

## §4k A 20/20 THAT COULD NOT HAVE BEEN ANYTHING ELSE — third instance of the tautological-test family

**`docs/demos/duel-2/runs/grade-muh2-judge-20260918T054622Z.json` (`be2cab5`), pane 2 grading pane
3's MU-H2 judge run.** Verdict: **`HELD_WIRING_PROOF_ONLY_NO_RUNG3_GATE`.**

The decisive line:

> **`canned p keyed directly by gold label`**

**The canned asker derives its probability from the gold label, so 20/20 is tautological — the
harness cannot fail, because the answer is the input.** Everything else pane 2 checked confirms the
scope: per-class denominators correct, 18 non-ambiguous decided and 2 withheld, **Jev calls 0**,
incumbent arms not run, **ECE/Brier null**, human lift null. *"Wires proven, semantic/threshold gate
not."*

### This is a family, not an incident, and it is now three deep

| Instance | Shape | Caught by |
|---|---|---|
| The lane's first RED-arm test | fired on **all 16 rows** and "passed" | conductor, on re-test |
| demo-1 | passed **10/0** around a hand-written token heuristic | rung-4 measurement |
| MU-H2 canned judge | scored **20/20** with the answer keyed from the label | **non-author grade** |

**The family is: a test whose outcome is fixed by construction rather than by the thing under test.**
Each instance produced a clean-looking number that measured nothing, and each was caught later and
cheaper than the last — the third by a non-author grade before any claim was made.

### Neither pane overclaimed, and that is why this cost nothing

Pane 3 labelled its own receipt **`WIRING-ONLY`** with **`NO-CLAIM wiring`** — it never presented
20/20 as correctness. Pane 2 then independently established *why* it could not be correctness. **The
author scoped honestly and the non-author verified the scope**, which is the whole mechanism working
on a result that could easily have been paraded.

**Standing consequence: `20/20` from the canned asker may never be cited as evidence of anything but
wiring**, in any lane document. It is recorded here so that a future reader — or a future me, given
§3w — cannot quote it.

### MU-H2's state is unchanged and its gate is untouched

**Rung 2, score 430, CLEARED-conditional.** Its six-threshold gate (`75cfb9f`) remains entirely
unmeasured: ECE/Brier null, no live judge run, no human-lift measurement, and the incumbent arms
measured separately in §4h. **What exists is a wired harness over an immutable 20-case corpus — real
infrastructure, zero verdict.**

**And the queue order does not change.** WIP is one, COD-H2 holds it at rung 4 with 905, MU-H2 sits at
430. **MU-H2 does not get a live run ahead of COD-H2's rung-4 measurement**, however cheap it looks —
that is the ordering §3k exists to enforce.

---

## §4l THREE OF FIVE COD CANDIDATES ARE BLOCKED BY **CORPUS SCARCITY**, NOT BY IDEA QUALITY

**`docs/demos/duel-2/runs/codh41-labelfree-20260918T054800Z.json` (`53946b3`), pane 2 — author of
both candidates, running thresholds pane 3 pre-registered.** Both label-free halves return
**`UNASKABLE`**, and neither for a reason about the idea:

- **COD-H1 snapshot-completion (885):** **41 candidate JSONL files, only 2 transcript-shaped**, both
  in the jev root. The design requires **≥30 real transcripts across ≥3 harnesses** — *"unavailable
  without subjective classification/labels."*
- **COD-H4 toolresult-replay (900):** the public-source manifest
  `demos/preaction-abstention/fixtures/h4-public-sources.json` is **absent**, and a 30-case corpus
  **costs the full 4-hour build timebox.**

**`No thresholds moved, no labels, no Jev, no model.`** The author of both candidates declined to
advance either, and priced the obstacle instead of arguing past it.

### The pattern, stated as a fact about this lane rather than about these ideas

| Candidate | Score | Corpus situation |
|---|---|---|
| **COD-H2** | **905** | **already existed** — 111 journals, 14,556 turns, on disk |
| COD-H4 | 900 | **does not exist**; 4-hour build |
| COD-H1 | 885 | **2 of ≥30** transcripts; needs labelling |
| MU-H1 | 820 | **17 markers / 283 KLOC** — died at rung 4 on the denominator (R14) |

**The top five COD candidates sit inside a 20-point band (885–905), so idea quality is not what
separates them. What separates them is whether the data already existed.** COD-H2 is at rung 4
because its corpus was sitting on disk before anyone asked; MU-H1 died and two more are blocked
because theirs were not.

**That is a finding about the lane's environment: this lane does not have the data its best ideas
need.** And it is worth more than any individual verdict here, because it predicts which future
candidates can be tested at all.

### Gauntlet amendment: corpus availability becomes a **rung-2** screen

**The gauntlet currently discovers corpus scarcity at rung 3 or rung 4 — after a design, sometimes
after a build.** MU-H1 got a full rung-1 and rung-2 pass and a falsification design before anyone
counted its markers. COD-H1 and COD-H4 got falsification designs before anyone checked their
corpora.

**New rung-2 question, added to "does this need a calibrated per-decision auditable probability with
the option to withhold":**

> **Does the corpus this candidate needs already exist on disk, unlabelled, right now?** If yes,
> proceed. If no, **price it before proceeding** — the candidate is `UNASKABLE` until the corpus cost
> is stated, and that cost is part of its rung-3 estimate.

**This is §3k's principle one layer earlier.** §3k says estimate rung 4 before paying for rung 3;
this says **estimate the corpus before designing the falsifier**, because a falsification design for
a corpus that cannot be assembled is a document, not a test.

### Neither candidate is killed, and both retry conditions are concrete

**COD-H1 → HELD on corpus.** Retry: **≥30 transcript-shaped files across ≥3 harnesses**, obtainable
without subjective classification. Two exist. **That is a sourcing problem with a countable target.**

**COD-H4 → HELD on corpus, priced.** Retry: **build the 30-case corpus at a 4-hour cost.** This is
not a blocker, it is **a deferral with a price tag** — and at score 900 it is the first candidate
behind COD-H2, so if COD-H2's rung 4 succeeds, **four hours is a known and probably acceptable
entry fee.** Recording the price is what makes that decision possible later.

---

## §4m RUNG-4 DESIGN ACCEPTED — it designs against the exact failures this lane found today

**`docs/demos/duel-2/RUNG4_DESIGN_COD-H2_COD.md` (`3a5851f`), pane 2.** **K=10 repeated live calls
per case over N=200**, a **fixed 30-case boundary band `[.65, .85]`**, selective accuracy at coverage
**.50/.60/.70/.80/.90/.95/1.00**, per-case variance and flip rate, ECE/Brier with Wilson intervals,
and pass gates **ECE ≤ .10 · Brier ≤ .15 · flip ≤ 5% · human action lift ≥ 20%**.

**It answers §4j's constraint directly:** K=10 repeats measure the variance that only appeared at the
boundary (0.74 → 0.70), and the boundary band is its own 30-case population rather than an average.

### Six safeguards, each closing a failure this lane discovered in the last few hours

1. **Corpus committed before live calls** — *"No case may be added after observing probabilities."*
2. **Boundary band selected from the spec, not from returned probabilities** — you cannot choose the
   band that flatters the result.
3. **`Do not lower K or silently substitute canned`** if the provider cannot support budget or
   metadata — **return `UNASKABLE/HELD` instead.** That closes the shrink-until-it-passes move *and*
   §4k's tautology in one clause.
4. **Canned-answer control run explicitly, labelled wiring-only, and excluded** — §4k's
   keyed-by-gold-label defect designed against by name.
5. **Boundary result controls the safety decision; do not average.** A good aggregate may not hide a
   bad boundary — which is exactly what a point threshold over a variable output would do.
6. **A post-hoc blinded reviewer sample may not relabel the precommitted ground truth.**

And the failure clause is the right shape: *"A statistically significant result that misses any
operational condition fails. A small sample, missing labels, unavailable provider, duplicate
responses, or missing boundary population returns `UNASKABLE/HELD`."*

### Two costs the design does not price — and one of them is my own new rule turned on my own leader

**Cost 1 — the API calls, and this one is cheap.** Using the **measured** per-call usage from §4i
(439/444/438/434/420, mean **435** input tokens):

```text
2,000 calls × 435 tokens = 870,000 input tokens = 0.870M
at $0.042/M input  ->  $0.0365      [EXTERNAL, UNVERIFIED per §3w]
output: 40,000 tokens, reported free by the same external source
```

**Under four cents, if the public price is right.** The token arithmetic is ours and measured; **the
price per million is an external figure the census never opened a control for**, so it carries that
label at the point of use — the rule §3w earned.

**Cost 2 — the 200 policy labels, and this is the binding one.** The design requires *"one immutable
manifest of **N=200 labelled cases** before live calls"* with *"ground-truth labels [that] are
**policy labels, not model answers**."* **Those labels do not exist.** COD-H2's corpus supplies 907
*unlabelled* destructive-bash turns — the raw material is on disk, the ground truth is not.

**§4l, which I wrote one turn ago, applies here:** *does the corpus this candidate needs already
exist on disk, unlabelled, right now? If no, price it before proceeding.* **The unlabelled sample
exists; the labelling does not, and nobody has priced it.**

**So rung 4 is NOT authorized yet, and the reason is a rule I just imposed on two other candidates.**
COD-H1 and COD-H4 were held one turn ago for exactly this — a design whose corpus had not been
priced. **Exempting the leader because it is the leader would make §4l a rule about weak candidates
rather than a rule.** Consistency is the whole reason the screen is worth having.

**What closes it:** a priced labelling plan — how 200 policy labels get authored, by whom, at what
cost, and who verifies them, given that the author of the policy cannot be the sole source of the
labels its policy is graded against. **That is the next unit, and it is cheap to answer badly and
worth answering well.**

---

## §4n LABELS PRICED, PRICE VERIFIED FIRST-PARTY — rung 4 is affordable, and one authorship gap remains

**`docs/demos/duel-2/RUNG4_LABEL_PLAN_MU.md` (`525bfc2`), pane 3.** *"Bottom line up front: **N=200
is affordable** (~90 label-minutes + audit). No `UNASKABLE` pressure applies."*

### The pricing is a measured trial, not an estimate

Ten cases labelled and timed, then stratified across four strata that *"price differently"* →
**~90 minutes total, single pane, one sitting.** Two things make it trustworthy:

- **The trial disclosed its own bias:** the 10-case sample split **7/2/1/0** and *"destructive-only
  sample skews pass-light on purpose — a pricing trial prices the **act**, and destructive cases are
  the slow ones."* It priced the slow path deliberately.
- **Sensitivity stated:** *"If the estimates are off **2× against**, the total is still an
  afternoon."*
- **The escape hatch was pre-committed and then not needed:** *"Largest affordable N: **the full
  200, no reduction argued for**. Had the trial shown otherwise, this section would name the
  [smaller N]."* I asked for an honest smaller N if the cost demanded it; the plan shows it was
  prepared to give one.

### It closed the §3w unverified-price flag with a first-party source

I flagged `$0.042/M` as an external figure with no control opened. Pane 3 found it **in-repo** —
`docs-mirror/typesafe/models.md:13-16`, quoted verbatim: *"| Price (per Btok / per Mtok) | $42 /
$0.042 |"*. Arithmetic re-derived independently and matches mine to the digit: **2,000 calls × 435
measured tokens = 0.870M × $0.042 = $0.0365 ≈ $0.037.**

> *"**Model money is not the constraint on rung 4; the ~90 label-minutes are, and they fit.**"*

**That is the correct framing and it inverts the assumption I was carrying.** I had treated the API
spend as the thing to justify; the binding resource is **human-equivalent labelling time**, and it is
an afternoon.

### The split honours the hard constraint, fixed before any label exists

- **Pane A labels; Pane B audits a random 20**, with the **seed committed before sampling**.
- **Agreement bar ≥ 18/20.** Below it, *"labels are re-done with an adjudicated rubric, **not averaged
  into agreement**."*
- **Disagreements route to the conductor, case by case.**
- *"Audit sample and bar are fixed **here, before any label exists**."*

**Pre-registering the bar before the data is the same discipline that made Q9, Q12 and Q24
trustworthy**, applied now to the labelling rather than the measurement.

### The one remaining authorship gap, and it is the lane's signature asymmetry

**The audit bar was chosen by the pane that will be labelling.** `≥18/20` on a 10% sample is
plausible for mechanical policy-rule application — but **a labeller setting its own audit threshold
is exactly the asymmetry this gauntlet exists to catch.** The bar should be **ratified or amended by
the auditor**, before labelling starts, because afterwards any change looks like tuning.

**So rung 4 is authorized in principle and not yet started.** Queued as Q32: pane 2 ratifies or
amends the audit sample size and agreement bar, and states whether a 20-of-200 sample at ≥18/20 has
the power to catch a systematically mislabelled stratum — which is the failure the audit exists to
detect, and the one a random sample is weakest against.

**`NO-CLAIM strata estimated`** — the per-stratum rates come from a 10-case trial, so the 90-minute
figure is an extrapolation with its basis stated. Recorded as such.

---

## §4o §4l's CORPUS SCREEN DISCRIMINATES — and demo-9 is "a contract, not code"

**`docs/demos/duel-2/runs/demo9-vs-ubs-20260918T061500Z.json` (`980f4e8`), pane 3 as non-author of
demo-9.** A **split** verdict, which is the useful kind:

- **Corpus: PROCEED.** 15 code-touching commits via `git log --diff-filter=AM` over `*.ts/*.mjs/*.js`,
  unlabelled diffs present — *"no pricing needed, no `UNASKABLE` on corpus grounds."*
- **`ubs` baseline: non-empty and therefore usable.** **6 critical · 6 warnings · 50 info across 8
  files** in `compaction/src` (2) + `demos/preaction-abstention/src` (4) + `demos/doc-drift/src` (2)
  at HEAD.
- **Comparison: UNASKABLE.** *"No Jev-signal implementation exists to run; **demo-9 is a contract,
  not code**."*

> *"Next unit is a **build-or-skip decision on the Jev arm**, not more screening."*

### The screen I added one turn ago now has three results, and they differ

| Candidate | Corpus screen |
|---|---|
| COD-H1 | **UNASKABLE** — 2 of ≥30 transcripts, needs labelling |
| COD-H4 | **UNASKABLE, priced** — manifest absent, 4-hour build |
| demo-9 | **PROCEED** — diffs exist unlabelled, baseline runs |

**Three runs, two UNASKABLE, one PROCEED.** That matters for the same reason the RED-arm test
mattered: **an instrument that returns the same verdict on every input has measured nothing.** §4l's
screen separates *"the data does not exist"* from *"the code does not exist"* — and those need
opposite responses. COD-H4 needs a 4-hour corpus build; demo-9 needs a rung-3 implementation.

**demo-9 stays CLEARED-conditional at 550, condition sharpened:** corpus verified present, blocked on
a **build** that the WIP limit defers behind COD-H2. It is no longer waiting on an unknown; it is
queued behind a known.

### A weak corroboration of §4c that does not resolve it

§4c left the two UBS criticals in `demos/preaction-abstention/src` **UNASKABLE**, because every UBS
mode *"counts criticals and emits no per-finding locations."* This differently-scoped run reads its
categories as *"loose-null idiom, **non-secret comparisons**, documented async-listener shape,
missing-`AbortSignal` on short timeout calls."*

**"Non-secret comparisons" is exactly the category pane 3 originally claimed for the preaction
criticals** — now appearing from a second run over a wider scope. **That makes the original
adjudication more plausible and proves nothing**, because the locations are still absent and the
counts merely scale with scope (2 in one directory, 6 across three).

**§4c stays UNASKABLE.** And pane 3 drew the same line itself: *"full adjudication with per-finding
dispositions belongs to the head-to-head run, not this screen."* **A category reading is not a
per-finding disposition**, and it declined to promote one into the other.

---

## §4p AUDIT BAR RATIFIED AND STRENGTHENED — with a role-concentration note and one guard

**`docs/demos/duel-2/runs/ratify-label-audit-20260918T060749Z.json` (`db6e78d`), pane 2.**
**`RATIFIED_WITH_STRATIFIED_AMENDMENT`.**

- **`≥18/20` retained overall**, and **amended to stratified sampling: 5 from each of the 4 strata,
  with `≥4/5` agreement required in *every* stratum.**
- Seed and case IDs **committed before sampling**.
- **Pane A = WindyJaguar (pane 2) labels 200; Pane B = CopperCarp (pane 3) blind-audits 20;
  conductor adjudicates disagreements.**

**The amendment answers the exact question I asked and fixes the exact weakness.** A random 20 *could*
have drawn ~5 per stratum; now it is **guaranteed** 5 per stratum with a per-stratum floor. **A
stratum labelled systematically wrong can no longer be averaged away by three good strata** — and
**the boundary band is one of the four**, so the most decision-sensitive population carries the
tightest check. Strictly stronger than what it replaced.

### Role concentration, stated because nobody else will

Pane 2 now holds **three of four roles** on COD-H2: it authored the **candidate**, authored the
**rung-4 design and its gates**, and has assigned itself the **200 labels**. The only independent
role is pane 3's blind audit of 20.

**Pane 2 chose the harder half** — 200 labels, ~90 minutes, versus 20 audited — and its binding
satisfies my stated hard constraint exactly: **the author of `policy.json` (pane 3) does not author
the labels its policy is graded against.**

**But with two panes, some conflict is unavoidable, and it is worth naming which one we accepted:**

| Assignment | Violates |
|---|---|
| **Chosen:** pane 2 labels, pane 3 audits | the **candidate author** produces the ground truth its candidate is scored against |
| Alternative: pane 3 labels, pane 2 audits | the **policy author** produces labels for its own policy |

**Neither is clean. The choice is defensible because a policy label is rule-application, not
opinion:** the design specifies *"policy labels, **not model answers**"*, `policy.json` is
**committed**, and applying a committed rule is checkable by anyone against its text. **The audit is
therefore the real control, not the labeller's identity.**

### One guard added, aimed at the risk that actually remains

**The audit must be a mechanical check against the committed `policy.json` text, not a second
opinion.** Specifically: **every disagreement must cite the policy clause it turns on.** Without
that, a disagreement is two panes' intuitions colliding, the conductor adjudicates on taste, and the
ground truth quietly becomes negotiated rather than derived.

**With it, the labeller's conflict mostly evaporates** — pane 2 cannot label in COD-H2's favour
without contradicting a committed clause that pane 3 can point at. That converts the residual
authorship risk into a text-checkable one, which is the only kind this lane has been able to settle.

**`NO-CLAIM no labels authored/started`** — the protocol is fixed, nothing is labelled, and the seed
is not yet drawn (pane 3's Q34).

---

## §4q THE DESIGN'S AUTHOR FOUND FOUR WAYS TO GAME IT — before any run

**`docs/demos/duel-2/runs/gameability-rung4-20260918T060939Z.json` (`3134260`), pane 2, adversarial
against its own design.** Verdict: **`AMEND_Q29_DESIGN_BEFORE_RUNG4`.** I offered it the option to
decline the unit as unperformable. It did not take it.

| Gaming path | Gate defeated |
|---|---|
| **Always-withhold** | passes `flip ≤ 5%` — **but fails coverage**, so already partly caught |
| **Constant probability** | games **ECE and Brier** |
| **Easy-prefix answering** | games **selective accuracy** |
| **Weak comparison baseline** | games **human action lift ≥ 20%** |

**The `flip` gate behaved as I suspected and the coverage gate saved it.** I distrusted `flip ≤ 5%`
because a policy that withholds more often never sits near the line — confirmed, and the existing
coverage requirement already blocks the degenerate case. **That is the first time this session a gate
I distrusted turned out to be adequately defended.**

**The one that would have wrecked rung 4 silently is the second.** A **constant** predictor at the
base rate can post a respectable ECE and Brier while carrying **zero discriminative information**.
Raw Brier is not interpretable without a reference — and the design's gate was a raw threshold
(`Brier ≤ .15`). **A degenerate model could have passed the headline calibration gates and been
recorded as a rung-4 success.**

### Six guards, each tied to a specific path

- **model coverage ≥ .80** — blocks always-withhold.
- **Brier *skill* against a prevalence baseline** — the correct fix: a constant predictor scores zero
  skill by construction, so the gate now measures information rather than agreeableness.
- **full coverage curve**, not a single point — blocks easy-prefix answering.
- **full denominators** and **no silent skips** — blocks quiet exclusion of hard cases.
- **boundary band separated** — retained, and now load-bearing given §4j's 0.74 → 0.70.

### On the policy-disagreement guard: **adopted, not independently arrived at**

The receipt lists *"every label disagreement must cite `policy.json` clause; no negotiated ground
truth"* as a new guard. **That guard was in the Q33 packet I sent.** Its appearance is **adoption,
not corroboration**, and §3o exists because I once counted exactly this kind of echo as evidence.
**Recorded as adopted.** What is pane 2's own is the four gaming paths and the five statistical
guards; the disagreement clause is mine, correctly incorporated.

### Consequence: the rung-4 design is amended, and the amendment needs a non-author check

The accepted design (`3a5851f`) is **superseded in its gate definitions** — `Brier ≤ .15` becomes a
**skill score against prevalence**, coverage becomes a **hard floor**, and the curve replaces point
readings.

**One authorship gap, and I am closing it inside an existing role rather than adding a round trip:**
pane 2 authored the design, audited it, and wrote the guards. **Pane 3 — already bound as the
auditor — must confirm the six guards are actually implemented in the runner before the live run
fires.** That is a precondition of the run, not a new gate: a guard that exists only in a receipt is
the same defect as a threshold asserted rather than checked (§4b-CORRECTION).

**Rung 4 remains authorized-not-started.** Preconditions now: immutable 200-case manifest (pane 3,
Q34, in flight) · 200 labels with clause-cited disagreements · **six guards verified present in the
runner**.

---

## §4r demo-9 SKIPPED (not killed) — and its cost estimate is wrong by exactly 1000×

**`docs/demos/duel-2/HELD_demo9_build_or_skip_COD.md` (`e399d32`), pane 2 on its own candidate:
`SKIP_RUNG3_NOW_HOLD_NOT_RULED_OUT`.**

**Price: ~1–2 engineering days + a reviewer session**, plus ~120 Jev calls. Retry conditions are
quantified and pre-registered: **≥20pp semantic recall lift over `ubs`, ≤5% FP, ≥20% action/review
lift, ≥10 non-pattern cases, fixed withhold/codes.** `NO-CLAIM no permanent kill`.

**The ruling is right.** demo-9 sits at **550** against COD-H2's **905**, WIP is one, and pane 3's
screen already established the blocker is a **build**, not data. **An author recommending its own
candidate be skipped, with the retry priced and quantified, is the correct use of the withdrawal
asymmetry** — the same move demo-4's author made earlier.

### The arithmetic error, and the file is the reason it was catchable

The receipt states **`$2.19`** for 120 calls, and — crucially — **shows its inputs** (line 117):

> *"The `$2.19` estimate is arithmetic from **120 calls × 435 input tokens × `$0.042/Mtok`**"*

**Those inputs are correct. The result is wrong by exactly 10³:**

```text
120 × 435 = 52,200 tokens = 0.0522M
0.0522M × $0.042/Mtok = $0.00219      <- correct
                        $2.19         <- stated, 1000× high
```

**The digits are identical (219), which is the signature of a pure unit slip** — almost certainly the
`$42/Btok` vs `$0.042/Mtok` pair that §4n verified first-party, applied at the wrong scale. Sanity
check in the other direction: reaching `$2.19` at the real price would need **434,524 tokens per
call**, which is not plausible for 120 calls.

**Corrected: the entire demo-9 live run costs about a fifth of a cent.**

**The verdict is unaffected** — the binding cost was *1–2 engineering days*, and the receipt itself
flags the dollar figure as arithmetic rather than a measured spend. **But it would have mattered if
money had been the deciding factor**, and in a lane that has now corrected a headline number five
times, a 1000× error in a costing that feeds a build/skip decision is worth recording.

**The doctrine point is why it was findable: the pane showed its work.** Had the receipt said `$2.19`
alone, nothing could have checked it. **Publishing inputs alongside a derived number is what makes
the number auditable**, and this is the second time today that habit caught an error (§4h's D1
arithmetic reconciled the same way).

**And it reinforces §4n's inversion twice over:** model money is never the constraint in this lane.
Rung 4's 2,000 calls cost **$0.037**; demo-9's 120 cost **$0.002**. **Engineering time and labelling
time are the only real currencies here.**

## §4s THE CLAUSE GUARD, COMPLETED BY PANE 2 WHERE I LEFT IT INCOMPLETE

**`docs/demos/duel-2/runs/ratify-label-audit-amendment-20260918T061500Z.json` (`e432d06`).** Formal
pre-label amendment:

> *"Every Pane-B disagreement must cite **exact `policy.json` JSON path/criterion**; no
> intuition/averaging; **missing clause ⇒ UNASKABLE + policy amendment**."*

**I specified "cite the clause it turns on" and stopped there. I never said what happens when no
clause covers the case** — and that silence was the real hole, because an uncovered case is exactly
where an adjudicating conductor would have started inventing ground truth on taste.

**Pane 2's addition closes it: a policy gap becomes a policy amendment, not a judgement call.** The
case goes `UNASKABLE`, the policy gets fixed, and the fix is committed text that the next label can
cite. **That is strictly better than what I asked for**, it is pane 2's own — unlike the base guard,
which §4q records as adopted from my packet — and it means the ground truth can only ever be
*derived from committed text or declared absent*, never negotiated.

**Three pre-label preconditions are now fixed and none of them are mine to relax:** stratified 5-per-
stratum audit with a `≥4/5` floor (§4p) · clause-cited disagreements with the missing-clause escape
(§4s) · six anti-gaming guards verified present in the runner (§4q).
