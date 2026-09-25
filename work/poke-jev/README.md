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

| Stage | What | Lane | Prereg | Result |
|---|---|---|---|---|
| A | predict human player and opponent actions on 2,000 replay turns vs PokéChamp's Table 1 | live, TypeSafe only | `pokejev-stage-a-20260925.md` | **FAIL** (`pokejev-stage-a-results-20260925.md`): top-1 0.3365 / 0.2235 clears Table 1, log-loss loses to a usage floor (R103) |
| B | 200 local Gen 9 OU battles each vs Abyssal, OneStep and MaxBasePower under an enforced clock, plus a zero-call control | live | `pokejev-stage-b-20260925.md` | **KILL** (`pokejev-stage-b-results-20260925.md`): 56.0% vs Abyssal, 0 time losses; the <70% KILL bar fires |
| B stretch | a released Metamon checkpoint on the same server | live | addendum before its first battle | pending |
| C | the public ladder | **not authorized** (needs Joshua) | none | — |

The prereg and result files live in `docs/demos/upstream-repro/`.

```bash
cd work/poke-jev && python3 -m unittest test_replay test_policy           # offline: labeller, floors, policy, validator
.venv/bin/python stage_a.py sample                                        # offline: fixed-seed sample
infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- .venv/bin/python stage_a.py run
.venv/bin/python stage_a.py score                                         # keyless re-score
.venv/bin/python stage_a.py verify-copy 40                                # keyless: fast copy and memo change no answer
./serve.sh                                                                # local server, Gen 9 OU Clock format
.venv/bin/python stage_b.py selftest                                      # keyless, 4 arms incl. the clock's RED arm
.venv/bin/python stage_b.py battles abyssal 200 --control                 # keyless zero-call control
infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- .venv/bin/python stage_b.py battles abyssal 200
.venv/bin/python stage_b.py score                                         # keyless receipt
```

**Without a key,** `run` and `battles` print `unconfigured: ... (NOT_RUN)` and exit with status 2.
They never fake an answer.

**Clock.** PokéChamp's simulator, as shipped, took 72–134 s per decision here, the same order as
the clock it lost to on the ladder. `pc.fast_copy` and `pc.memoize_predictor` bring that to
0.35–1.05 s. `verify-copy` checks that neither changes a state text or a simulated leaf.
