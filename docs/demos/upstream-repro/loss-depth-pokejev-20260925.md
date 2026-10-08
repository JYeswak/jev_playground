# PokéJev Stage B loss-depth autopsy

Status: **PREPARED-NOT-MEASURED for the next live arm**. This is a keyless analysis of the committed Stage B abyssal run. It made no Jev request and does not claim that the four-way labels are causal truth.

## Question and inputs

The Stage B loss-depth question is: **when the Jev-backed player loses, what was the first observable turning point, and which of the four implementation hypotheses should be tested next: action prior, opponent model, leaf value, or missing state?**

Inputs are the committed artifacts at root revision `93082ec`:

- `work/poke-jev/stage-b/results-abyssal.jsonl` — 200 results, 88 losses, 0 time losses in the loss set.
- `work/poke-jev/stage-b/decisions-abyssal.jsonl` — 5,494 decision rows.
- `work/poke-jev/stage-b/replays-abyssal/` — one saved replay for each loss.
- Results SHA-256: `99ea395094fd290990de662c3f40214c0a98ce38b9a7350d890fc8a3c102dc4a`.
- Harness receipt: 381 fallback decisions across 27 battles; the classes were 105 `ValueError: Unknown move: nothing` decisions in 12 battles (1 lost), 271 TypeSafe 402 credit fallbacks in 12 battles (5 lost), and 5 timeout fallbacks in 5 battles (2 lost).

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
6. **Harness boundary:** the complete decision log has three named failure classes. `ValueError: Unknown move: nothing` occurred 105 times in 12 battles (1 loss); TypeSafe 402 credit fallback occurred 271 times in 12 battles (5 losses); timeout fallback occurred 5 times in 5 battles (2 losses). These are harness/service observations, not four-way model evidence.


## Harness failure classes

| Harness class | Fallback decisions | Battles | Losses |
|---|---:|---:|---:|
| `ValueError: Unknown move: nothing` | 105 | 12 | 1 |
| TypeSafe 402 credit fallback | 271 | 12 | 5 |
| Timeout fallback | 5 | 5 | 2 |

The implementation shape being audited is the pinned player design: root action prior and opponent Choice, local one-ply leaves, then a leaf Choice per opponent candidate and probability-weighted argmax (`work/poke-jev/player.py:1-14`, `265-333`). The related TypeSafe pattern is composite scoring (`docs-mirror/typesafe/patterns/composite-scoring.md:267-341`); this report audits the existing composition rather than proposing a new primitive.

## Ranked hypotheses for component arms

The next step is **not** an OneStep battle replication. That would measure the same design against another opponent and cannot show a fix. The next step changes one component at a time and scores it against its own ground truth, without playing battles.

| Rank | Component | Ground truth | One-variable arms | Fixed score/oracle |
|---:|---|---|---|---|
| 1 | Opponent model | Actual opponent next action from Stage B decisions plus Stage A replay labels | Dev-fitted probability tempering/floor; add revealed moves/items/speed to state; relative question | Top-1 and log-loss against usage-frequency floor |
| 2 | Action prior | Human player's actual action in Stage A replay decision points | Existing Jev player distribution versus the usage-frequency floor | Top-1 and log-loss; usage floor is the baseline to beat |
| 3 | Leaf value | Eventual battle outcome from the decision state | Pairwise relative-value question instead of an absolute `Score` | AUC against the eventual outcome label |
| 4 | Missing state | Delayed effects, items, status, hazards, and revealed information | Defer until the three component arms identify a state-specific gap | No battle claim from this audit |

The four-way denominator is **85**. The remaining **3/88** first-faint rows are `402 credit exhaustion` fallbacks and are not evidence for any Jev hypothesis. The top two are effectively tied, so the component dev table—not 31 versus 30—must select the first held-out arm.

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
- The 105 unknown-move, 271 TypeSafe 402, and 5 timeout fallback decisions are harness/service observations; they are named separately and are not silently folded into model errors.
- The OneStep replication is explicitly rejected. The next step is a committed dev/held-out split and component-level scoring with one variable per arm, before any new Jev call, held-out score, or battle run.
