# BREADTH — SEARCH / RESEARCH (CyanPeak, 2026-10-02)

Targets: cass/session search, EE recall, web research results, docs lookup.
Our refuted priors here: lexical/semantic shortlist + single Noul (R133/R135 lexical
line). The skill's own scorecard warns: Jev marks beat recency 11-to-4, but the
digest built on them lost to plain last-24k. So every design below is judged on the
downstream decision, never on mark quality.

## D1 — Choice top-k rerank over find shortlist (rerank_typesafe, one Choice)
Decision: which file answers this search. State: query + ≤10 candidate
path+snippet pairs. Question: one Choice "which candidate answers the query".
Action: open top-1. Labels: file actually opened next in the same session
(mined keylessly from session toolCalls). Baseline: find-rank order / recency.
Why it might win: one call per query (not per pair), Choice probs sum to 1 so
ranking is free; tests the rerank cookbook shape on our own traffic.

## D2 — Per-function Noul screen, Every-style (one Noul per function)
Decision: which functions implement X. State: query + one function body.
Question: Noul "does this implement X", rank by noul. Action: show top-k.
Labels: functions inside files opened post-search. Baseline: grep hit order.
Why it might win: fine granularity where names lie; Every's shipped shape.
Costs one call per function — needs a shortlist gate to be affordable.

## D3 — Choice rank + Noul existence gate (semantic_find combo)
Decision: which lines answer + whether any answer exists. State: query +
tagged lines. Questions: Choice over line ids AND Noul "does an answer exist".
Action: show Choice top-1 iff Noul says yes, else say none. Labels: held-out
Q/A with known answer locations. Baseline: Choice alone (which always ranks
something first even when nothing answers). Why it might win: kills the
forced-pick failure mode the cookbook names.

## D4 — Hierarchical Choice + beam over the file garden (hierarchical_classification)
Decision: where to look machine-wide (202 repos). State: query + category
descriptions (repo/dir blurbs). Questions: Choice over categories, beam top-2,
then Choice over files within. Action: search only those dirs. Labels: file
eventually opened. Baseline: flat repo-wide grep/find. Why it might win:
prunes 202 repos to 2 before any file IO; beam keeps recall when categories blur.

## D5 — Multi-question branch per passage (classifying_rag_passages)
Decision: what to do with each research passage. State: query + passage.
Questions per item: relevant? usable? contradicts? instructs? Branch:
evidence / conflict-queue / drop. Action: build brief only from evidence.
Labels: passages cited in EVAL rows vs ignored. Baseline: single relevance Noul.
Why it might win: contradicts/instructs catch what relevance misses; mirrors
the MEMORY area's multi-question shape on research text.

## D6 — Confidence-gated routing (confidence-routing pattern)
Decision: spend the rerank or not. State: query + cheap-screen top-1.
Questions: Noul screen first; full Choice rerank only if top-1 conf < τ.
Action: answer fast or rerank. Labels: D1 labels + cost ledger. Baseline:
always-rerank. Why it might win: same quality at a fraction of calls; the win
is spend, measured in calls/query at equal top-1 accuracy.

## D7 — Composite score (composite-scoring pattern)
Decision: rank by relevance AND usability AND recency. State: query + passage
+ age. Questions: Noul(relevant) + Noul(usable) in one request; score =
f(p1, p2, recency). Action: top-k. Labels: cited vs ignored passages.
Baseline: single relevance Noul. Why it might win: usability screens
tutorial-grade passages that relevance loves; no threshold fitting by hand.

## D8 — Citation Check Choice on agent claims (citation_check, ties to V6)
Decision: does the cited evidence support the DONE number. State: claim text +
cited artifact excerpt. Question: Choice verified / unsupported / contradicted /
fabricated + confidence gate to human. Action: accept or flag for verifier.
Labels: 40+ verifier callback outcomes (VERIFIED vs differs) — observed, never
typed. Baseline: R130 claim rule (retired, precision 0.571) / regex number
presence. Why it might win: four-way Choice with evidence in state is exactly
the cookbook shape; labels already exist.

## D9 — Rank-then-verify with abstain (rank-then-verify)
Decision: which web result to open, or none. State: query + result snippets.
Questions: Choice top-1, then Noul "does this answer the query"; abstain on no.
Action: open or say none. Labels: results opened/cited post-search (hook log +
session mining). Baseline: rank-1 always (the forced pick). Why it might win:
abstention kills confident-wrong opens; matches D3's gate in the web domain.

## D10 — Score-3-level duplicate call (entity_alignment; eruw-adjacent, not built here)
Decision: same / related-needs-curator / different bead pair. Noted only:
eruw owns the Choice version of this area; Score with ordered levels + field
Nouls riding along is the documented alternative if Choice stalls.

## Feasibility ranking (keyless, this wave)
1. D8 — labels on disk (verifier outcomes), state constructible (claim + cited
   artifact). First probe.
2. D1 — labels minable (search→open in session toolCalls). Second probe.
3. D9 — needs web_search hook log volume check. Third probe.
Preregister the winner after probes; live only on KEY OK.
