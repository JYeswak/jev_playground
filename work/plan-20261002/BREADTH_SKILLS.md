# BREADTH SKILLS — Jev skill routing beyond shortlist+Noul (WindyLantern, 2026-10-02)

Bead: jev-hj5t (labels discovery,breadth). Live jev-1.13.0 only after KEY OK.

## 1. Where we stand

- Roster: 761 skills (`~/.claude/skills`), per R135. Consumer: omp sessions; skill reads
  observable as `read` toolCalls on `*/SKILL.md` (verified in session files this turn).
- R133: lexical shortlist <=20 + one Choice + 'none', cut 0.5 → every recall gain added
  misroutes; N2 0/48 hints. Bar: **>=25% hint rate AND 0 misroutes** on committed per-row dev.
- R135: dev `work/jev-zbb1/dev.jsonl` (20 real prompt/skill-read pairs): lexical recall@20 4/20,
  semantic-desc 3/20, desc+body 4/20, hybrid 1/20. Retry bar: **recall@20 >= 8/20 keylessly first**,
  then the Choice stage (<=20 bounded calls) vs the R133 predicate.
- F1 (this turn): `var/agent-tmp/skills-breadth/harvest_pairs.py` expands the 20-pair dev set
  from all profiles' sessions (request = nearest preceding user text; fixtures excluded).

## 2. Sources read

- `docs-mirror/typesafe/cookbooks/skill_suggestion.md`: two requests — (1) Choice over all 182
  + 3 gate Nouls (act-on-system / documented-procedure / prose-suffices-inverted, mean >= 0.30
  or silence), shortlist 3; (2) Choice over shortlist w/ full description + SKILL.md head +
  per-candidate fits-Noul, drop if best < 0.30. Measured vs Haiku agent: wrong load 16.8→7.3%,
  needless load 9.8→4.0%.
- `docs-mirror/typesafe/cookbooks/hierarchical_classification.md`: Choice tree + beam search,
  top-K paths by geometric-mean edge probability; early mistakes recoverable, parallel
  questions per frontier.
- `docs-mirror/typesafe/cookbooks/classifying_rag_passages.md`: 4 Nouls per item (relevant /
  usable-evidence / contradicts-premise / instructs-model) with thresholds driving branch.
- `docs-mirror/typesafe/patterns/confidence-routing.md`: confidence as second axis, per-action
  thresholds. `intent-routing.md`: Choice intent + Score complexity in parallel, route by
  intent. `fan-out.md`, `composite-scoring.md` (code-controlled weights).
- Community: `typesafe-ai/skills`, `ask-jev-skill`, `jev-system-architect` (README entries;
  nothing cloned, no community code committed).
- House doctrine: **one question per request** default (PLAN 2.3.4). All designs below use one
  question per request; D6 sequences singles with early exit instead of batching.

## 3. Designs (10)

Shared labels: F1 pairs (request -> skill read) + must-silent cases (user texts before long
stretches with no SKILL.md read). Shared baselines: B0 lexical recall@20 (4/20 on dev);
B1 R133 predicate (>=25% hints, 0 misroutes). Shared split: by session; held-out frozen first.

- **D1 Cookbook-faithful, 761 scale.** Q1: Choice over all 761 + single gate Noul
  (documented-procedure?). Top-3 → Q2: Choice over 3 with full descriptions + SKILL.md head.
  Hint iff Q2 confidence >= 0.5 and fits-pass. Why beats R133: gate kills needless loads;
  full-text Q2 separates authoring/editing confusions one-liners cannot. Risk: ~12k input
  tokens per prompt; cost arithmetic in feasibility.
- **D2 Hierarchical beam over skill dirs.** One Choice per level (top: ~40 category names,
  then skills within top-2 categories), beam width 2, geometric-mean path score; hint iff leaf
  geo-mean >= cut. Why beats: <= 40 options per call (cheap, local-model-compatible); beam
  recovers early category errors a flat shortlist cannot.
- **D3 Intent-first routing.** Q1: Choice over 6 use-intents (act-on-system /
  follow-documented-procedure / configure-tooling / explain-advise / create-artifact / none).
  Intent maps to skill subsets deterministically. Q2 only on procedure/act intents over the
  mapped subset (30-80 skills). Why beats: explain-requests exit after one cheap call.
- **D4 Gate-only.** Single Noul ("would an expert consult a documented procedure?"); ranking
  runs only on pass. Why beats: cookbook gate alone cut needless loads 9.8→4.0%; one call.
- **D5 Score-rubric rerank with separation rule.** One Score per top-5 lexical candidate
  ("loading this changes the next action for the better"); hint top iff score >= 0.6 AND
  margin over runner-up >= 0.15, else silence. Why beats: near-ties (the misroute source)
  become silence, which R133 proved safer than a wrong hint.
- **D6 Branching singles (rag-style, serialized).** Per top-5 candidate, at most one Noul each
  with early exit: (a) "does this skill do the specific thing asked?" hint on >= 0.7; (b) tool-use
  check; else next; silence after 5. Why beats: absolute judgments, never forced Choice among
  bad options; averages <2 calls/prompt.
- **D7 Trajectory state.** State = request + last-5 tool calls + loaded skills. One Choice over
  lexical top-10. Why beats: need shows in trajectory (repeated failing tool → diagnostic
  skill); prior reads suppress re-hints (free precision).
- **D8 Composite deterministic + Jev tiebreak.** Code score 0.5*lexical + 0.3*semantic +
  0.2*past-use-rate (frozen weights); Jev Choice over top-5 ONLY when margin(top1,top2) <
  epsilon. Why beats: Jev spend only on ambiguous prompts (<20% traffic); epsilon tunes silence.
- **D9 Verify-only veto.** One fits-Noul on the single otherwise-winning skill; veto hint on
  < 0.4. Why beats structurally: can never misroute (only vetoes); metrics = veto precision +
  miss rate. Pairs with any proposer.
- **D10 Prior-weighted cold split.** Hot set (read >= 2 sessions): Choice over hot+lexical
  top-up (<= 30). Cold rest: D4 gate >= 0.7 before ranking. Why beats: concentrates spend where
  labels exist; the 761-tail cannot misroute without clearing a strict gate.

## 4. Feasibility (keyless, no live calls until KEY OK)

- F1 corpus: pair/session/skill counts, must-silent cases (bg harvest this turn).
- F2 deterministic components on F1+dev: lexical recall@K; intent-keyword subset recall (D3
  minus Jev); category-keyword beam recall (D2 minus Jev); composite weights (D8 minus Jev).
- F3 cost arithmetic per design at dev scale; kill designs whose fleet cost exceeds plausible
  skill-read time saved.
- Preregister the best (R133 predicate on frozen held-out sessions, grouped split, paired vs
  B0/B1, caps, go/no-go). Live only after KEY OK.

## 5. What green does not prove

A hint-rate win on harvested pairs does not prove agents read more skills usefully live
(R134 lesson: nobody opened the picks). Any PASS needs a live session-follow arm (skill read
after hint) before rollout.

## 6. Demo reuse (conductor redirect 2026-10-02) + D1 scale verdict

- `demos/skill-suggest/` implements the cookbook shape with `live-receipt.json`
  (two askJevBundle calls, jev-1.13.0, gate 0.30; fixture: 5-skill roster, 3 tasks).
  Wiring = driver importing the same askJevBundle question shape with our roster/rows,
  not a rebuild. The demo's fits-Noul wording is reused verbatim for D9 below.
- **D1-as-built is DEAD on our roster (keyless kill):** Choice criteria over all 788 skills
  = 235,100 bytes (~59k tokens) > ~32k input limit. The rank-all call cannot run. D1 survives
  only with a deterministic shortlist first (collapses to R133 shape) or via D2 hierarchy.
- Prereg direction: **D9 veto-only** — single fits-Noul per eligible row (~139 + prompt tokens,
  one question per request, fail-open allow). Demo wording reused, our rows/seam.
