# PREREG — wbel cookbook two-request design (bead jev-wbel)

Frozen 2026-10-02 before any cookbook live call. Source: the VERIFY half D9
skipped — `docs-mirror/typesafe/cookbooks/skill_suggestion.md` (rank wide, then
re-read the top three with full detail; fixed 0.30s become a dev-fitted cut).

## Request 1 — rank (Choice, one round trip)

`askJevChoice`, state `{request}` (same 2000-char truncation as the hook).
Instructions (cookbook verbatim): "Which of these skills, if any, is the right
one to load to help with the user's latest request?" Classes: per-row
10-shortlist (`work/wbel/shortlists.json`: loaded parent always first + top 9
lexical-overlap from the 934-skill inventory) with FULL descriptions
(desc + body head, like the cookbook's rerank criteria). Reference/line-ranged
loads mapped to the deepest SKILL.md-owning parent (11/2000 shortlist slots
undescribed, down from 38/200 rows). Take top 3 by probability.

## Request 2 — verify (bundle: Choice + fits Nouls, one round trip)

`askJevBundle`, same state. `which`: Choice over the top 3 with full
descriptions (cookbook RERANK_INSTRUCTIONS verbatim). `fits::<name>`: one Noul
per candidate, D9 wording verbatim ("Does the skill '<name>' do the specific
thing the user's request asks for? It is described as: <desc>"). Winner =
Choice argmax (must hold max probability and valid distribution, else the
request is invalid). Verified iff max fits >= cut.

## Decision (veto = block the load)

Veto iff a verified winner exists AND resolved-loaded != winner. Everything
else allows: no winner, winner == loaded, invalid/refused either request
(fail-open, counted as exclusions only when a request itself fails; a
below-cut winner is a scored allow, not an exclusion).

## Cut (dev-fitted)

Fit the fits-threshold on DEV (r000–r099, blind labels already frozen)
maximizing Youden J with UNFIT as positive, tie-break lowest cut. Report HELD
(r100–r199). Full-200 as secondary context only.

## Bar (held half, fixed pre-call)

Incumbent always-allow: 0 vetoes, miss rate = FIT fraction. D9 on the same
held half (recomputed from `replay-rows.jsonl`) + full-200 (0.335 / 0.881).
LOCKED PREDICTION: cookbook beats D9 precision by >= 0.15 AND held miss rate
<= 0.50. Enforcement bar unchanged (0.80/0.10) — this tests the DESIGN, and a
pass earns a full-sample enforcement run, not enforcement itself.

## Caps

<= 400 calls (2/row), spend cap $0.06 (~$0.04 expected: request 1 carries ~12k
chars of descriptions), stop on 401/402/403 or cap, 20 s timeout,
checkpointed resume by sample_id (a resumed row repeats request 1;
idempotent, disclosed). NO-CLAIM beyond session skill loads.
Runner `work/wbel/run_cook.mjs`; receipt `work/wbel/cook-rows.jsonl`
(sample_id, winner, winner_p, fits, best_fits, resolved, status, latencies,
model, usage; no raw text).
