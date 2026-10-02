# BREADTH — memory/context: beyond the single relevance Noul (HazySpring, jev-h1hr)

Sources read: docs-mirror/typesafe/cookbooks/classifying_rag_passages.md (full: 4 Nouls per passage — relevant, usable-evidence, contradicts-premise, instructs — plus route() in code, thresholds named in one dict), docs-mirror/typesafe/patterns/fan-out.md (full: many questions one request, speculative questions ignored, parallel answers), pattern essences for confidence-routing (confidence as second axis to act), composite-scoring, hierarchical_classification (parallel beam search over Choice probabilities), plus consistency/citation/rerank/sde_cascade/semantic_find cookbooks (listed/located). Community: jevlike (train small scorer — rejected: needs training infra we don't have). Starting point: keep precision 0.22 from one relevance Noul at 0.5 (m959 9/44); drops 0.978+ (do not regress); R137 closed single-sentence rewordings, R139 closed two-question AND-conjunction, yl60 closed local-nimble-for-memory, jev-9n6h failed per-item bundling (93.1% parity, systematic boundary harshness).

## D1. RAG-classifier port: 4 Nouls + route() (PREREGISTERED)
- **Decision:** keep iff usable-evidence ≥ bar after routing; contradict → conflict block; instruct/irrelevant → drop.
- **State:** {prompt, memory} per pair (cookbook shape).
- **Questions (one request, fan-out):** is_relevant / states-usable-evidence / contradicts-request-premise / instructs-model.
- **Action:** route() in code with named thresholds (cookbook: thresholds live in one dict, policy is a constant edit).
- **Labels:** m959 44 keeps (usable ≈ relevant) + s47b 30 drops + wb7j 96 drops; same dev slice as 9tkx.
- **Baseline:** single-Noul 0.205 keep / 1.0 drop; bar: keep ≥ 0.405 with drops ≥ 0.90.
- **Why it might win:** our failures are usable-vs-topical confusion (stale dispatches, tips, echoes kept for adjacency); the usable-evidence question targets exactly that, and branching (separate fates) is not the refuted AND-conjunction.

## D2. Choice top-k over the memory set
- **Decision:** one Choice per turn: "which memories does this request need?" options = memory ids + none-of-these; keep the chosen set.
- **State:** {prompt, memories: [...]} once; options carry short idents, not full text twice.
- **Questions:** single Choice (criteria per memory, generated from idents).
- **Action:** keep chosen; drop rest; empty/none → drop all.
- **Labels:** same 44 re-expressed as sets (relevant set per prompt-grouped turn where reconstructible; else per-item precision/recall of chosen vs relevant).
- **Baseline:** same 0.205/1.0.
- **Why:** relative judgment beats absolute 0.5 cuts (9n6h showed the cut is where bundling dies); one call per turn.

## D3. Score rubric (0–4 usefulness)
- **Decision:** Score per memory on a committed rubric (0 noise … 4 directly usable); keep ≥ 2.
- **State/Questions:** per pair, Score primitive with legend criteria.
- **Action:** threshold in code.
- **Labels:** needs 20 freshly graded rows (binary m959 labels map poorly to grades); wb7j strict labels inform the rubric.
- **Baseline:** same.
- **Why:** graded signal separates "topical" (1) from "usable" (3–4); the binary cut may be the whole problem.

## D4. Fan-out bundle of the 4-question set (one request per turn)
- **Decision/action/labels/baseline:** as D1, but all memories × 4 questions in ONE request (prompt sent once).
- **Why:** 9n6h failed per-memory bundling with systematic boundary harshness; fan-out bundles QUESTIONS per item instead — tests whether the harshness came from cross-item interference. Cost: same call count as now, ~70% fewer tokens (9n6h measured 0.22–0.30×).

## D5. Hierarchical Choice + beam over source clusters
- **Decision:** beam search over a two-level Choice tree: level 1 picks topic clusters, level 2 picks memories within.
- **State:** level 1: {prompt, cluster digests}; level 2: {prompt, cluster members}.
- **Questions:** Choice at each level with beam width committed.
- **Action:** keep leaves under chosen clusters.
- **Labels:** same 44 (clusters from existing source tags: coding-agent-transcript, sleep_consolidation, etc.).
- **Baseline:** same.
- **Why:** recall already arrives tagged; hierarchy matches the data shape and bounds the option set per call (≤26 local limit respected).

## D6. Rank-then-verify (cheap rank, Noul verify top-k only)
- **Decision:** deterministic rank → Noul-verify top-k → keep verified.
- **State:** ranker sees (prompt, memory) strings; verifier sees winners only.
- **Action:** keep verified; drop rest without a call.
- **Labels:** same; rank quality measurable keylessly.
- **Baseline:** same + call-count metric (20 → k).
- **Why:** cuts cost AND forces the Noul onto contenders only.
- **Feasibility (keyless, just run): lexical-overlap rank REFUTED — irrelevant median overlap (4) EXCEEDS relevant (2): topicality trap confirmed numerically.** Recency/source-prior rankers untested.

## D7. Contradiction-first with conflict block
- **Decision:** three fates per cookbook: evidence / conflict / drop; stale-or-wrong memories about the request become signal instead of silent drops.
- **State/Questions:** D1's four questions; route() sends contradicts-premise hits to a separate conflict block in the injected context.
- **Action:** inject evidence + conflict blocks separately (cookbook: generator reacts appropriately).
- **Labels:** 44 + drops; conflict precision measured on stale-dispatch rows.
- **Baseline:** same + downstream-use metric later.
- **Why:** our biggest wrong-keep cluster (stale dispatches) is premise-conflicting information wearing a relevance disguise.

## D8. Confidence-gated routing
- **Decision:** keep iff relevant AND confidence high; low-confidence relevant → drop (or second cheap probe).
- **State/Questions:** same Noul; confidence from the returned value.
- **Action:** two thresholds, both committed (act-bar + route-bar per confidence-routing pattern).
- **Labels:** same + recorded probs already in sidecar.
- **Baseline:** same.
- **Why:** 9n6h flips clustered at 0.27–0.51 — the boundary is where precision dies; confidence routing attacks exactly that band.

## D9. Session-topic Choice with drift re-score
- **Decision:** one Choice per session ("which topic does each memory serve?"); reuse across turns; re-score on drift.
- **State:** {session-topic-summary, memory}.
- **Action:** memo by (memoryHash, topic); drift detector re-opens.
- **Labels:** same; needs topic summaries (derivable from prompts keylessly).
- **Baseline:** same + calls/session metric (tonight: 40/3-turn session).
- **Why:** recall is static per session but scored per turn; dueling #3 variant, never refuted.

## D10. Composite deterministic score (Jev for one axis only)
- **Decision:** composite = w1·usability(Noul) + w2·recency + w3·source-prior, weights committed; keep ≥ bar.
- **State:** Noul sees (prompt, memory); recency/prior are arithmetic.
- **Action:** threshold in code; ablate weights.
- **Labels:** same.
- **Baseline:** same.
- **Why:** isolates what Jev uniquely adds (usability judgment) from what arithmetic does better (time, priors); cheapest live cost of all.

## Keyless feasibility (top 3)

- **D1 READY:** labels (44 + 126), baseline, replay harness pattern (9tkx), thresholds committable. Needs live calls post-KEY-OK.
- **D2 READY:** same labels re-expressible; option counts ≤20 fit limits; same harness shape.
- **D6 lexical rank REFUTED keylessly** (overlap inverts: irr med 4 > rel med 2). Recency/source variants untested — not preregistered.

## Preregistration: D1

Run D1 on the 9tkx dev slice (44 keeps + 126 drops), live jev-1.13.0, single calls (stability EXPLORED), bounded ≤250 calls, spend stated. SHIP to shadow iff keep precision ≥ 0.405 (base +0.20) with drop precision ≥ 0.90; else NEGATIVE_EVIDENCE row. Thresholds committed in code before the run; no wording iteration inside the run.
