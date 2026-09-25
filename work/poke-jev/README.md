# poke-jev: Jev inside PokéChamp's search, on a local Pokémon Showdown server

Bead `jev-jy7t.1.3`. Idea 1 in `notes/deep/next-gen/WIZARD_IDEAS_CC.md`, chosen in `SYNTHESIS.md`.

**Where this is from.** PokéChamp (arXiv 2503.04094, ICML 2025) puts GPT-4o in three slots of a
minimax search:
1. proposing the player's actions;
2. predicting the opponent's;
3. scoring leaf states.

It lost about a third of its human-ladder games on the clock. PokéJev puts Jev (`jev-1.13.0`) in the
same three slots. Jev returns a calibrated distribution over the legal options in about 130 ms, so
the search can weight opponent actions by probability and still finish inside the clock.

**Pattern.** Confidence routing and composite scoring over a game tree:
`docs-mirror/typesafe/patterns/confidence-routing.md`, `docs-mirror/typesafe/primitives/choice.md`.

**Prior art**, wrapped and never patched:

| Repo | Pin | License | Owner |
|---|---|---|---|
| `pokechamp/` (`github.com/sethkarten/pokechamp`) | `0f84c46` | MIT | Seth Karten |
| `pokemon-showdown/` (`github.com/jakegrigsby/pokemon-showdown`, the fork PokéChamp's README names) | `e64915c0e` | MIT | Jake Grigsby |

**Replay data.** `huggingface.co/datasets/milkkarten/pokechamp`, revision `b5820ff`.

**Oracles.**
- Human actions in public replays (Stage A).
- The Showdown engine's win/loss under an enforced clock (Stage B).

## Setup (uv only)

```bash
git clone https://github.com/sethkarten/pokechamp && git -C pokechamp checkout 0f84c46        # repo root
git clone https://github.com/jakegrigsby/pokemon-showdown && git -C pokemon-showdown checkout e64915c0e
(cd pokemon-showdown && npm install && cp config/config-example.js config/config.js)
cd work/poke-jev && uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python \
  numpy pandas tqdm orjson scipy scikit-learn torch transformers accelerate websockets openai \
  google-genai ollama requests termcolor rich pyfiglet fade tabulate pyarrow datasets huggingface-hub mcp httpx \
  -e ../../upstream/typesafe-ai/typesafe-sdk-python
```

- **Why torch and transformers:** PokéChamp's `LocalSim` imports its LLM backends at module load.
  No local model is ever run.
- **Why no bitsandbytes:** it has no macOS wheel, and nothing here needs it.

## Stages

| Stage | What | Lane | Prereg |
|---|---|---|---|
| A | predict human player and opponent actions on 2,000 replay turns vs PokéChamp's Table 1 | live, TypeSafe only | `docs/demos/upstream-repro/pokejev-stage-a-20260925.md` |
| B | 200 local Gen 9 OU battles each vs Abyssal and the poke-env heuristics, clock enforced | live | written before its first battle |
| B stretch | a released Metamon checkpoint on the same server | live | same |
| C | the public ladder | **not authorized** (needs Joshua) | none |

```bash
cd work/poke-jev && python3 -m unittest test_replay                      # offline: labeller + floors
.venv/bin/python stage_a.py sample                                        # offline: fixed-seed sample
infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- .venv/bin/python stage_a.py run
.venv/bin/python stage_a.py score                                         # keyless re-score
```

**Without a key,** `run` prints `unconfigured: ... (NOT_RUN)` and exits with status 2. It never
fakes an answer.
