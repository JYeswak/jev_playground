# rc-pane2 — official applications inventory (Phases 1–2)

Pane: P2 (pane_index 2, `%2 jev__omp-muse_1`). Scope: official Jev applications from
`docs-mirror/typesafe/`, ranked for omp wiring. No edits to P4-owned files.
Date: 2026-09-21. Lane: offline (no key, no network). Oracle: vendor docs on disk.

## Phase 1 — vision checklist, re-derived (README + AGENTS mission)

Mission: validate Jev → build from survivors → liven omp → dogfood → share.

| # | Stage | Status (this pane's read) | Evidence |
|---|-------|---------------------------|----------|
| 1 | Validate Jev | WORKING — verdict ZERO **on blocking veto seats only** | `docs/REALITY-CHECK-20260921.md` R69: required n=∞ at p̂ 0.50 |
| 2 | Build from survivors | NOT_STARTED as blocking tools; INPUT EXISTS as advisory tools | 18 cookbooks + 12 upstream repos RUN (README lines 199–223) |
| 3 | Liven omp | PARTIAL | 1 hook, 1 MCP, 0 tools, 0 extensions (reality-check doc) |
| 4 | Dogfood | REGRESSED for veto instrument (R68) | first real dogfood found instrument broken |
| 5 | Share | PARTIAL | 1 issue + 2 corrections; ARC unpublished |

Five answers:
1. WORKING: refusal machinery, exposure-check, gate suite, 12 upstream RUN receipts.
2. NOT WORKING: no advisory build attempted; veto framing blocked stage 2.
3. BLOCKING: premise, not capability — stage 1 tested vetoes at 0.016% prevalence.
4. Open/in-progress beads close it? NO — none reframes veto→advisory.
5. ZERO-coverage goals: the premise question itself; publication past n=2.

Separation (required): "Jev lost to a regex on OUR tasks" (tool_call harm rule 12/12
vs Jev 11/12, keep-everything beats pruners, flat pricing beats router — README TL;DR)
is a cost-benefit verdict on five hand-picked veto/routing seats. "Jev has no
application" does not follow: README lines 98–104 + 12 RUN receipts show Jev tying a
14.8k-label TF-IDF at zero labels, holding 0.97–0.99 under shift, 96.5% injection
with context, 5× skillranker abstain control. Veto lost. Advisory unattempted.

## Phase 2 — every official application (local path + one line)

Source: `docs-mirror/typesafe/cookbooks/` (18), `docs-mirror/typesafe/patterns/` (4),
`docs-mirror/typesafe/demos.md` + `demos/smart-home.md` (1). One-line bodies verified
2026-09-21 via title + first-content-line read; question-type tags marked
[INFERENCE] where the body was not fully read.

| # | Application | Local path | Primitive [INFERENCE unless stated] |
|---|-------------|------------|--------------------------------------|
| 1 | Structure recovery (restore stripped markup) | `docs-mirror/typesafe/cookbooks/autoformat.md` | Score/Choice [INFERENCE] |
| 2 | Autoresearch feature discovery loop | `docs-mirror/typesafe/cookbooks/autoresearch_feature_discovery.md` | parallel Choice [INFERENCE] |
| 3 | Citation double-check (claim ↔ source section) | `docs-mirror/typesafe/cookbooks/citation_check.md` | Noul per claim [INFERENCE] |
| 4 | SEC-business classification with confidence | `docs-mirror/typesafe/cookbooks/classification_using_confidence.md` | Choice + confidence |
| 5 | RAG passage classification (wording-similar ≠ answering) | `docs-mirror/typesafe/cookbooks/classifying_rag_passages.md` | Noul/Score per passage [INFERENCE] |
| 6 | Moderation self-consistency (1 post × 15 runs) | `docs-mirror/typesafe/cookbooks/consistency_choice_cookbook.md` | Choice × N runs (stated) |
| 7 | Insurance-claim rubric self-consistency (14 Q × 15 runs) | `docs-mirror/typesafe/cookbooks/consistency_noul_cookbook.md` | Noul × N runs (stated) |
| 8 | Date extraction `extract_date(document, role)` | `docs-mirror/typesafe/cookbooks/date_extraction_cookbook.md` | Choice/Score [INFERENCE] |
| 9 | KG entity alignment across NL sources | `docs-mirror/typesafe/cookbooks/entity_alignment.md` | Choice [INFERENCE] |
| 10 | Typed function calling (order → structured args) | `docs-mirror/typesafe/cookbooks/function_calling.md` | Choice + extraction [INFERENCE] |
| 11 | Hierarchical classification (taxonomy/filesystem) | `docs-mirror/typesafe/cookbooks/hierarchical_classification.md` | Choice per level [INFERENCE] |
| 12 | LLM guardrails (per-lab refusal lines) | `docs-mirror/typesafe/cookbooks/llm_guardrails.md` | Noul [INFERENCE] |
| 13 | Parallel questions (1 doc, N questions, 1 call) | `docs-mirror/typesafe/cookbooks/parallel_questions.md` | fan-out primitive (stated) |
| 14 | Pre-parsed value extraction, verbatim copy | `docs-mirror/typesafe/cookbooks/pre_parsed_value_extraction_cookbook.md` | extraction [INFERENCE] |
| 15 | Re-ranking (1 answer among thousands) | `docs-mirror/typesafe/cookbooks/rerank_typesafe.md` | Score per doc [INFERENCE] |
| 16 | SDE cascade (cheap Jev first, big model on low-confidence) | `docs-mirror/typesafe/cookbooks/sde_cascade.md` | confidence routing (stated) |
| 17 | Line-by-line semantic find (ToS question → lines) | `docs-mirror/typesafe/cookbooks/semantic_find.md` | Score per line [INFERENCE] |
| 18 | Skill suggestion (route without context rot) | `docs-mirror/typesafe/cookbooks/skill_suggestion.md` | Choice over roster [INFERENCE] |
| P1 | Speculative fan-out | `docs-mirror/typesafe/patterns/fan-out.md` | many questions, code decides |
| P2 | Confidence-gated routing | `docs-mirror/typesafe/patterns/confidence-routing.md` | answer × confidence axes |
| P3 | Composite scoring | `docs-mirror/typesafe/patterns/composite-scoring.md` | atomic scores, code weights |
| P4 | Intent routing (deterministic / specialist / human) | `docs-mirror/typesafe/patterns/intent-routing.md` | Choice + confidence |
| D1 | Smart-home assistant (speculative Qs + LLM fallback) | `docs-mirror/typesafe/demos.md`, `docs-mirror/typesafe/demos/smart-home.md` | fan-out + fallback (stated) |

## Ranked 3 for omp wiring today

1. **RAG-passage filter + rerank (#5 + #15, patterns P1/P2).** Omp pain it meets:
   `tool_result` 50 KiB outputs flooding context; usage-shape shows 98.878% tokens are
   re-sent context. Seam: `tool_result` hook logging scores + custom tool `jev_rerank`
   (advisory order, never block). Ground truth on disk, zero-API baseline (TF-IDF/cosine)
   on identical rows, prevalence ~30–50% (FP = misorder, not incident).
2. **Skill suggestion / intent routing (#18, pattern P4).** Omp pain: next-step skill/tool
   choice every turn; wrong suggestion costs nothing (ignored). Seam: custom tool
   `jev_suggest`, log suggestion-vs-taken for dogfood accrual. Abstention first-class.
3. **Guardrails advisory flag + citation check (#12 + #3).** Omp pain: injection/claim
   review on tool results. Seam: `tool_result` annotation, flag-only (veto retired by
   measurement). Framing-leak control mandatory (evidence-withheld arm).

## Single pick to ship this week

**#1 RAG-passage filter + rerank.** Proven by upstream `anessbelbati/jev-rerank-bench@cd9a35b`
(RUN — headlines reproduce per README receipt; rerank-thirty-results question). Consumer:
omp `tool_result` hook + `jev_rerank` tool. RED arm: shuffled ranking must score below
true order; random-judge substitution must not pass. NO-CLAIM: advisory order only,
never a blocking filter.

Boundary: cookbook bodies skimmed (title + first line), not fully executed; pattern
pages are code skeletons; upstream SHAs from local clones (unverified vs remote tip
except pinned EVAL rows); no live calls in this slice.
