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

**Mission.** Ship installable Jev demos repeatedly, each one proving a capability a stranger can
reproduce from a clean clone.

**Non-goals, stated so they are not re-litigated:**
- Not a Jev SDK. The first-party SDKs are vendored and used, not re-implemented.
- Not a benchmark suite. `evals.typesafe.ai` is the published methodology; we do not invent a
  rival metric.
- Not a live-routing product. Demo-1 is a backtest; whether a router is ever built depends on what
  the backtest measures (see §5.1 — it has now measured near-zero, so the router is **not** queued).
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
