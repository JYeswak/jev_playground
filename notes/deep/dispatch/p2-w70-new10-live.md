# Amendment to `p2-w70-new10.md` — this unit is LIVE (bead `jev-deep-kit-8q7.9`)

From pane 1 AmberWillow. Joshua asked "why do we keep resorting to keyless first?". There was no
good reason: the cost gate was lifted on 2026-09-21 (AGENTS.md "Live Call Budget Gate — LIFTED"),
and a clone's own mocked suite teaches us about the clone, not about Jev. **This unit now says live.**
§2 "Scope: keyless only" of the original packet is withdrawn. Everything else stands.

## What changes

For every clone below, in this order, in the same unit:
1. T1-T3 as already under way (keep what you have).
2. **Commit the T4 bar first** (`[pending]`, in the receipt or a `-prereg` file), so it predates the
   first live call. Then run **T4 live on the clone's own question and data**, pinned `jev-1.13.0`
   (not `jev-latest`: pass the model id through the clone's config), and T5-T8 per the class
   profile. T6 incumbent: same state and questions through `upstream/typesafe-ai/system-one-adapter-python`
   against at least one LLM. Key: `infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- <cmd>`;
   never print a key. State calls and cost in each receipt.
3. Before any live call on a set with labels, run `skill://prevalence-first`
   (`node work/jev-prevalence-first/prevalence-check.mjs <rows> --truth <label>`) and paste its
   three lines into the receipt.

| clone | live work | hard limits |
|---|---|---|
| `Canny` | its done-claim Noul on real agent Stop events: take 20+ finished turns from jev's own omp session transcripts, label done/not-done from whether a verify command passed after the last edit, and score Jev's `claims_done` against those labels and against Canny's deterministic ledger alone | read transcripts only; never install Canny as a hook in a live pane |
| `neo4jev` | budgeted navigation on its public demo DB (<=24 calls per navigate) over several goals, success vs a BFS / keyword baseline | its own call cap |
| `jev-curate` | its presets on a small labelled sample (build one from a public labelled set, not one you author) plus its 3 sample rows; check whether its 1-5 score index matches what Jev returns | built via RCH |
| `prism-liquidity-agent` | its Jev judgments in backtest / paper mode on its committed or public data only | **never** with a wallet, key, or order path |
| `jev-drone` | Jev-on flights in the MuJoCo sim with the same seeds as your `--no-jev` ablation; paired comparison | simulation only |
| `typesafe-mario` | only if a legally obtained ROM is already on this machine; otherwise NOT-RUN with that reason | no downloading ROMs |
| `agent-desktop` | **not live**: its executor clicks the real desktop. Keyless policy tests plus a live Jev call only through a no-execute / dry-run path if the code has one (cite it); otherwise NOT-RUN with that reason | never let it act on the real desktop |

`jev-trader`, `killmyidea`, `OneVOneJev` stay out of scope.

## Callback

Same as the original packet: `CALLBACK-P2-W70-NEW10-DONE`, now including per-clone live N, cost,
and the result class (SELF / FLOOR / INCUMBENT).
