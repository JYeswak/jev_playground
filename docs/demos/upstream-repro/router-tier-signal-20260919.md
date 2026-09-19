# jev-model-router: the tier signal is real but weak, and loses to prompt length twice in three

**Date:** 2026-09-19 · **Level:** `[live]` · Oracle: `work/router-spec/oracle.mjs`

Joshua installed `productivity/jev-model-router` (`claude-code-templates --mod`). Unlike the two
routers this lane ruled out, it ships **`routeMainModel: false`** — it routes subagent model and
main-loop *effort*, not the main model. Our own +90.2% finding endorses that default, so the open
question is narrower: **does the tier it picks carry information about how hard the turn turns out
to be?**

## Design

- **Ground truth (not supplied to the model):** tool calls the turn actually made. `≥5` = hard,
  `<2` = mechanical, read from the transcript after the fact.
- **Balanced draw, declared before measuring:** the raw pool is ~10:1 hard:easy (278 usable, 253/25
  in one session), so every easy turn plus an equal number of evenly-spaced hard ones. An
  imbalanced denominator lets a weak signal look strong.
- **Preregistered bar, written in the file before the first run:** adopt if AUC ≥ **0.70** *and* it
  beats a **prompt-length-only** baseline by ≥ 0.05. Length is the dumb baseline that has already
  beaten a model twice in this lane.
- **Feasibility arm:** score a near-deterministic label ("does this prompt mention a file path").
  Below 0.80 → report a blind harness, no verdict.

## Result — 3 sessions, n=50 each, live

| session | feasibility arm | tier AUC | length baseline | margin | verdict |
|---|---|---|---|---|---|
| A | **1.000** | 0.631 | 0.750 | −0.119 | REJECT |
| B | **0.958** | 0.566 | 0.366 | +0.200 | REJECT |
| C | **0.979** | 0.562 | 0.608 | −0.046 | REJECT |

The arm passes everywhere, so the harness sees signal. The tier signal is **real but weak**
(0.56–0.63, consistently above chance) and **does not clear 0.70**. Prompt length — free, local,
zero-latency — beats it in two of three sessions.

## A bug of mine, caught by its own smell test

The first three runs reported tier AUC of **exactly 0.500** on all three sessions. Exactly 0.500
three times is a tie-induced artefact, not a measurement: the code read
`r.answers.tier.distribution`, but the field is **`probabilities`**, so the score was a constant 0.
Those REJECTs were bogus and are discarded. The oracle now **throws** if the field is absent rather
than silently scoring silence — scoring a constant is how a harness fakes a null.

## Ruling

`REJECT` the **tier** signal as a model-choice input on this workload; it does not beat a length
heuristic reliably. This says **nothing** about the mod's two enabled-by-default behaviours —
**effort** routing and **subagent** routing — which are untested here and are cheap by
construction. Keep `routeMainModel: false`.

## NO-CLAIM

Ground truth is a **proxy**: tool-call count. A genuinely hard prompt answered in one call is
mis-labelled mechanical, which biases against the model. The prompts are orchestrator dispatch
packets — long and structured — so prompt length is an unusually strong baseline here and would
likely be weaker on human chat turns. n=50 per session, 3 sessions, one machine, one model
version. Effort and subagent routing are unmeasured; so is any cost or latency effect.
