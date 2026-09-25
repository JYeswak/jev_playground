# PokéJev Stage B loss-depth autopsy

Status: **PREPARED-NOT-MEASURED for the next live arm**. This is a keyless analysis of the committed Stage B abyssal run. It made no Jev request and does not claim that the four-way labels are causal truth.

## Question and inputs

The Stage B loss-depth question is: **when the Jev-backed player loses, what was the first observable turning point, and which of the four implementation hypotheses should be tested next: action prior, opponent model, leaf value, or missing state?**

Inputs are the committed artifacts at root revision `93082ec`:

- `work/poke-jev/stage-b/results-abyssal.jsonl` — 200 results, 88 losses, 0 time losses in the loss set.
- `work/poke-jev/stage-b/decisions-abyssal.jsonl` — 5,494 decision rows.
- `work/poke-jev/stage-b/replays-abyssal/` — one saved replay for each loss.
- Results SHA-256: `99ea395094fd290990de662c3f40214c0a98ce38b9a7350d890fc8a3c102dc4a`.
- Decisions SHA-256: `c293d555f6e8e4d3493c9e3df97a595819a2a142a1e8d1521112847d43ac3b22`.

The parser and fixed rules are committed at `work/loss-depth/pokejev/autopsy.py`. Reproduce the full 88-row table with:

```bash
python3 work/loss-depth/pokejev/autopsy.py
```

## Fixed autopsy rules

1. **Turning point:** first `|faint|p1a:` event in the saved replay. The first own-side faint is an observable loss transition, not a judgment that the battle became mathematically unwinnable at that exact event.
2. **Missing state:** the faint is residual, contact/item, status, hazard, delayed, recoil, or occurs without a current opponent attack in the replay turn. These are state/effect paths that a one-ply direct-action comparison cannot attribute cleanly to a current opponent move.
3. **Opponent model:** the faint follows a direct opponent action whose predicted probability is absent or `< 0.25`. The threshold is fixed before inspecting aggregate counts and is not tuned to this result set.
4. **Leaf value:** the opponent action is not surprising and the final selected action differs from `prior_top`. This identifies the leaf/expectimax composition as the next suspect, not proof that another action would have won.
5. **Action prior:** the opponent action is not surprising and the final selected action equals `prior_top`. This identifies the root action-prior decision as the next suspect, not proof that the prior was intrinsically wrong.
6. **Credit-exhaustion boundary:** three first-faint rows occurred after the recorded TypeSafe HTTP 402 credit-exhaustion fallback. They are shown but excluded from the four-way denominator because no Jev decision existed at the turning point.

The implementation shape being audited is the pinned player design: root action prior and opponent Choice, local one-ply leaves, then a leaf Choice per opponent candidate and probability-weighted argmax (`work/poke-jev/player.py:1-14`, `265-333`). The related TypeSafe pattern is composite scoring (`docs-mirror/typesafe/patterns/composite-scoring.md:267-341`); this report audits the existing composition rather than proposing a new primitive.

## Ranked hypotheses before the live arm

| Rank | Hypothesis | Losses | Share of Jev-active losses | What the live test must discriminate |
|---:|---|---:|---:|---|
| 1 | Action prior | 31 | 36.5% | Does replacing or calibrating the root action prior change outcomes on fixed held-out battles? |
| 2 | Opponent model | 30 | 35.3% | Does expanding or recalibrating opponent candidates reduce direct losses where the observed move was low-probability or absent? |
| 3 | Leaf value | 19 | 22.4% | Does changing leaf question wording/aggregation reverse rows where leaf selection overrides `prior_top` against a sufficiently likely opponent action? |
| 4 | Missing state | 5 | 5.9% | Does exposing delayed effects, contact items, residual status, and state transitions prevent these first-faint paths? |

The four-way denominator is **85**. The remaining **3/88** first-faint rows are `402 credit exhaustion` fallbacks and are not evidence for any Jev hypothesis. The top two are effectively tied; the next arm should not spend a live call treating 31 versus 30 as a meaningful ordering.

## Representative rows across failure clusters

These rows are sampled from the complete deterministic output to cover every class, early/mid/late turns, absent/low/high opponent probability, and residual effects.

| Battle | Turn | First faint | Cause | Opponent action | P(opp) | Chosen | Prior top | Hypothesis |
|---|---:|---|---|---|---:|---|---|---|
| `battle-gen9ouclock-724` | 5 | Iron Valiant | delayed | `move calmmind` | 0.147 | `switch ironvaliant` | `switch ironvaliant` | missing state |
| `battle-gen9ouclock-782` | 8 | Zamazenta | contact/item | none | — | `move icefang` | `move icefang` | missing state |
| `battle-gen9ouclock-861` | 6 | Venusaur | residual/recoil | `move shadowball` | 0.617 | `move sludgebomb` | `move sludgebomb` | missing state |
| `battle-gen9ouclock-894` | 6 | Kyurem | status | none | — | `move earthpower` | `move earthpower` | missing state |
| `battle-gen9ouclock-899` | 5 | Zamazenta | contact/item | none | — | `move closecombat` | `move closecombat` | missing state |
| `battle-gen9ouclock-729` | 10 | Dragapult | direct | `move psychic` | 0.188 | `move dragondarts` | `switch landorustherian` | opponent model |
| `battle-gen9ouclock-741` | 12 | Zapdos | direct | `move stoneedge` | 0.143 | `move hurricane` | `move hurricane` | opponent model |
| `battle-gen9ouclock-776` | 1 | Weavile | direct | `move dracometeor` | — | `move tripleaxel` | `move iceshard` | opponent model |
| `battle-gen9ouclock-764` | 6 | Iron Crown | direct | `move suckerpunch` | 0.200 | `move focusblast` | `move focusblast` | opponent model |
| `battle-gen9ouclock-720` | 7 | Zamazenta | direct | `move psychic` | 0.783 | `move crunch` | `switch gliscor` | leaf value |
| `battle-gen9ouclock-744` | 5 | Ting-Lu | direct | `move moonblast` | 0.703 | `move earthquake` | `move ruination` | leaf value |
| `battle-gen9ouclock-811` | 12 | Kingambit | direct | `move darkpulse` | 0.914 | `move ironhead + terastallize` | `switch dragapult` | leaf value |
| `battle-gen9ouclock-889` | 9 | Cinderace | direct | `move earthpower` | 0.293 | `move pyroball` | `switch hoopaunbound` | leaf value |
| `battle-gen9ouclock-727` | 4 | Enamorus | direct | `move stoneedge` | 0.403 | `move moonblast` | `move moonblast` | action prior |
| `battle-gen9ouclock-730` | 6 | Raging Bolt | direct | `move earthpower` | 0.571 | `move thunderclap` | `move thunderclap` | action prior |
| `battle-gen9ouclock-742` | 1 | Glimmora | direct | `move psychic` | 0.667 | `move earthpower` | `move earthpower` | action prior |
| `battle-gen9ouclock-772` | 4 | Darkrai | direct | `move earthquake` | 0.798 | `move icebeam` | `move icebeam` | action prior |
| `battle-gen9ouclock-777` | 3 | Landorus | direct | `move shadowball` | 0.810 | `move earthpower` | `move earthpower` | action prior |

## Boundaries and next arm

- This is a **keyless** replay audit. It does not measure a new prompt, policy, win rate, or counterfactual action.
- First-faint attribution is a structured diagnostic label. It does not establish that the labelled component caused the loss or that the alternate action would have won.
- The 402 fallback rows are not part of the Jev evidence. The next live arm must use a fresh credit state and record any service/fallback rows separately.
- The next live arm must be preregistered before calls, use a held-out split rather than these same 85 losses, keep the opponent and team pairing fixed, and report the live arm's model, N, spend, and boundaries.
