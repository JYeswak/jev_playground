# rc-pane3 — cloned repos that already WON (Phases 1–2)

Pane: P3 (pane_index 3, `%3 jev__omp-muse_2`, profile muse). Scope: the four named
wins only — sec-bench, spam-eval OOD, rerank nevir, jev-review. No edits to
P4-owned files (docs/REALITY-CHECK-20260921.md, docs/PLAN-APPLICATION-20260921.md,
EVAL.md, NEGATIVE_EVIDENCE.md).
Date: 2026-09-21. Lane: offline (no key, no network). Oracle: committed receipts
on disk + upstream clones untouched.

## Phase 1 — vision checklist, re-derived (README + AGENTS mission)

Mission (AGENTS.md tail): validate Jev → build tools from survivors → liven omp
→ dogfood → share.

| # | Stage | Status (this pane's read) | Evidence |
|---|-------|---------------------------|----------|
| 1 | Validate Jev | WORKING — verdict ZERO **on veto seats only** | R69: required n=∞ at p̂ 0.50 (NEGATIVE_EVIDENCE.md:3110); NO-CLAIM at :3139-3141 scopes it to "this fleet's exposure profile", not Jev in general |
| 2 | Build from survivors | NOT_STARTED as veto tools; INPUT EXISTS as advisory tools | 12 upstream RUN receipts (README.md:199-223); 18 cookbooks on disk |
| 3 | Liven omp | PARTIAL | 1 hook, 1 MCP, 0 tools, 0 extensions (REALITY-CHECK-20260921.md:24) |
| 4 | Dogfood | REGRESSED for veto instrument (R68) | first real dogfood found instrument broken |
| 5 | Share | PARTIAL | 1 issue + 2 corrections; ARC unpublished |

Five answers:
1. WORKING: refusal machinery, exposure-check, 12 RUN receipts, four wins below.
2. NOT WORKING: stage 2 attempted veto-shaped tools at 0.016%–3.95% prevalence;
   advisory shape unattempted.
3. BLOCKING: premise, not capability — stage 1 certified vetoes, advisories were
   never the bar.
4. Open/in-progress beads close it? NO — none reframes veto→advisory.
5. ZERO-coverage goals: the premise question; advisory build; publication past n=2.

Separation (required): "Jev lost to a regex on OUR tasks" is README.md:22-26 —
tool_call harm rule 12/12 FP 0/38 vs Jev 11/12, plus phishing monolithic verdict
63.8% beaten by a two-line domain regex +27pts (judgment-quality-20260919.md:22-24).
That is a cost-benefit + question-shape verdict on five hand-picked veto seats.
"Jev has no application" does not follow: the same receipts show zero-label ties,
OOD holds, and injection/rerank wins below. Veto lost. Advisory unattempted.

## Phase 2 — the four wins: deterministic baseline, file:line, can-regex-replace-it?

### W1. jev-sec-bench — prompt injection WITH deployment context
- Upstream: `Gaurav-Gosain/jev-sec-bench@fdb16b9` (local clone SHA verified 2026-09-21).
- Jev result: acc **96.5%, AUC 0.9927, ECE 0.0588, p50 325ms** on 662 messages
  (263 hostile), 10 FP / 13 FN —
  `docs/demos/upstream-repro/jev-sec-bench-20260918.md:21-27`.
- Ablation (upstream's, not ours): bare recall 74.9% vs +context **95.1%**,
  accuracy 89.7% → **96.5%** — same file `:35-38`. Context-that-states-the-task
  is state; context-that-states-the-answer is leakage (`:46-50`).
- Deterministic baseline: **none run** — repo ships no regex/keyword arm; our lane
  ran no TF-IDF here either.
- Can a regex replace it? **NO.** 263 hostile over varied injection phrasings +
  20.2pp recall dependence on purpose-statement (`judgment-quality-20260919.md:16`).
  A keyword list would chase phrasings; the operating guidance (supply purpose as
  state) is the shippable piece.
- Omp consumer: `tool_result` advisory annotation (flag-only, never block).

### W2. jev-spam-eval OOD — zero-label tie + shift-hold
- Upstream: `bitnovus/jev-spam-eval@76ef183`.
- Jev results (saved answers + one 633-req live run, exploratory single-run):
  Ling-Spam plain **0.9857** vs email-dataset-trained TF-IDF **0.7298**;
  modern-mail category **0.9700** vs TF-IDF **0.7251**; names-only **0.9858**;
  recent-phishing Jev share 0.913–0.936 vs TF-IDF 0.703 —
  `docs/demos/upstream-repro/jev-spam-eval-ood-20260918.json:31-53`,
  ruling `REPRODUCED_WITH_SCOPE :56-62`.
- Stronger recomputation: Jev **0.9833** vs TF-IDF logreg **0.9839** on 18,514
  emails, McNemar p=0.677 (statistical tie vs ~14,800 in-domain labels); under
  shift TF-IDF **0.73/0.70/0.73** vs Jev **0.97–0.99** on identical items;
  score tails actionable (≥0.9 → 99.93% spam) —
  `docs/demos/upstream-repro/judgment-quality-20260919.md:13-16`.
- Deterministic baseline: **TF-IDF logreg** (trained, in-domain) — ties Jev
  in-domain, collapses under shift. Criteria-inversion: structured criteria
  1.56pp WORSE than plain (same JSON `:37`, `:53`).
- Can a regex replace it? **NO for the zero-label/OOD seat; YES for the
  monolithic phishing verdict.** The verdict seat is 63.8% / AUROC 0.70 while its
  own `sig_free_hosting` sub-question is AUROC 0.96 and a domain regex wins by
  27pts p=1.5e-8 (`judgment-quality-20260919.md:22-24`). Ship sub-signals +
  tails, never the verdict.
- Omp consumer: triage/rerank pre-filter (balanced prevalence, FP = misorder).

### W3. jev-rerank-bench nevir — fresh-run REAL over Cohere Pro
- Upstream: `anessbelbati/jev-rerank-bench@cd9a35b`.
- Headline (committed cache): Jev rubric nDCG@10 **0.692** vs Cohere Pro 0.691,
  gap 0.001, p=0.910 **within noise** —
  `docs/demos/upstream-repro/jev-rerank-bench-20260918.json:20-35`.
- Fresh run (the win): **nevir_eval over 1,383 pairs, Jev 0.711 vs Cohere 0.670,
  +4.2pts, p=0.002 REAL** — same JSON `:36-43`; interpretation `:77-78`.
- Deterministic baselines: BM25 **0.486**, Qwen one-passage 0.471 (`:21-26`).
  Asking-strategy spread 0.580→0.692 (`judgment-quality-20260919.md:29-30`).
- Can a regex replace it? **NO.** BM25 loses 20+pts; negation (NevIR 71.2% vs
  67.0% per judgment-quality `:17`) is semantic. Note P2 already claimed this
  seat for the build (notes/rc-pane2-applications.md:82-86) — I defer on
  rerank to avoid a second build.
- Omp consumer: (P2's) `jev_rerank` advisory order.

### W4. jev-review — the honest loss that proves the harness works
- Upstream: `NiazMorshed2007/jev-review@57690af`.
- Result: QUALITY **AUC 0.625** (better n=14 mean 7.33, worse n=8 mean 7.20) vs
  preregistered bar 0.75 → **RULED_OUT**; feasibility arm **AUC 0.939** proves
  the harness was not blind —
  `docs/demos/upstream-repro/jev-review-real-diffs-20260919.md:26-46`.
- Deterministic baseline: **feasibility check** ("does diff touch a test file")
  through the same pipeline, both classes present, 0.939.
- Can a regex replace it? **YES for feasibility** (path match on test files
  replaces the Jev noul); **quality seat retired** — scores 5.89–7.94 overlap
  almost fully, label is file-overlap proxy (NO-CLAIM `:48-52`).
- Omp lesson: ship the path check as code; do not buy a quality score here.

## Single pick to ship this week (P3)

**W1 — prompt-injection advisory flag with deployment context**
(`Gaurav-Gosain/jev-sec-bench@fdb16b9`).

Why this one: largest honest n (662, 263 hostile) with a committed ablation that
converts directly into operating guidance (purpose-in-state); no regex arm
exists to undercut it; FP-tolerant advisory fit (flag-only on `tool_result`,
never a veto — the veto was retired by measurement); complements P2's rerank
pick instead of colliding with it.

RED arm: purpose-stripped arm must recall ≥15pp below purpose-supplied arm on
the same items (upstream gap is 20.2pp); random-judge substitution must not hold
AUC. NO-CLAIM: advisory annotation only; live tab unrun
(`jev-sec-bench-20260918.md:52-62`); figures read from committed results, no
fresh API run in this slice.

Boundary: offline slice only; SHAs from local clones; numbers are committed
receipts re-cited, not re-measured; jev-review is a loss carried as a harness
proof, not a seat.
