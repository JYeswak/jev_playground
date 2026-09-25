# No-model floors on three game and web benchmarks (bead `jev-jy7t.1.1`)

This measures what no model at all scores on three benchmarks: a random policy and a hand-written scripted policy. Each is scored on the benchmark's own published metric and setting. A later Jev arm on these environments is compared with the published LLM numbers and with these floors. A Jev result that does not clear the floor is not a result.

CopperHeron (pane 2), 2026-09-25. **Keyless: no model call of any kind, $0.** The runners and serializers were written by three subagents of pane 2 (VizdoomFloor, MiniwobFloor, RtrgFloor). They read each setting from the paper and the authors' code, and ran development seeds only.

## Preregistered (committed before any preregistered seed or instance is run)

**What is fixed here:**
- the setting of every environment;
- the policies;
- the seeds and instances;
- the number of episodes;
- the metric and how it is aggregated;
- the exact commands.

Results are appended below this section and nothing above it changes. The runners are committed in the same commit as this section. The hashes below were taken after the repo's pre-commit formatter ran, which left each file's Python AST identical and only added a trailing newline to `tasks.json`:

| File | sha256 |
|---|---|
| `work/game-floors/vizdoom/run.py` | `ee29f9c5b9a783d84756c012851fa3381ce2402e47a541388fceb8af6f93d735` |
| `work/game-floors/miniwob/run.py` | `e0b0c42886e4ba176f6d7620b013604a1740d6c8513443b99bbe366443273c7b` |
| `work/game-floors/miniwob/tasks.json` | `af8890bf4877515c4eb27ee14a2fa0ea180b3c928709682634f96312986bb500` |
| `work/game-floors/rtrg/run.py` | `6f5b570304b3110692ae8116f528801229cac1ba8a5be9fad65145f98108c483` |

**The floor a later Jev arm must clear**, per environment and reading, is the higher of the random and scripted means. A floor is not a verdict on Jev. It is the number below which a Jev score means nothing.

**Development runs happened before this commit, on seeds outside every list below.** They are disclosed so that nobody reads the floors as a surprise:
- ViZDoom: seeds 9000–9004. Scripted scored about 36–38 cumulative reward at 600 decisions, and random about −5 to 3.
- MiniWoB: seeds 9000–9101 on dev tasks. Scripted succeeded on 0.32–0.64, random on 0.20–0.31.
- RTRG: Freeway seeds ≥ 9000 whose minimum steps fall in each level's range; Snake layouts 900–903 per level; Overcooked on non-published layouts. Scripted Snake-Easy scored 0.95.

Every scripted rule was written before its first dev run. Two changes were made on dev seeds and are disclosed:
- MiniWoB: tag names are compared case-insensitively, because Chrome 154 reports lowercase. This was a bug fix.
- MiniWoB: "one" was removed from the list of stop-words.

### 1. ViZDoom `defend_the_center` (arXiv 2603.11601v2, code `Lossfunk/See-Symbolize-Act` @`051fca1`)

**Published setting, as the runner implements it:**
- vizdoom 1.3.1 with the bundled `defend_the_center.cfg` (`vizdoom_ground_truth.py:97-103, 214-223`).
- 1280×720 screen, labels buffer on.
- `Mode.PLAYER`, which is synchronous. The paper says "the game is paused at every frame" (§3.3).
- Action set {TURN_LEFT, TURN_RIGHT, ATTACK}, sent one-hot (`vizdoom_ground_truth.py:279-284`).
- `frame_skip` 2: each decision repeats its action for 3 tics (`vizdoom_symbolic_runner.py:68, 1043-1046`).
- **600 decisions per run.** The runner's `--frames` flag counts decisions, and the README runs `--num_frames 600`.
- A death resets the game with the same seed. The decision count continues and the reward keeps accumulating (`vizdoom_symbolic_runner.py:1055-1065`).
- Reward: +1 per kill, −1 per death.

**Metric.** Per run, `cumulative_reward`. This is the runner's `total_reward`, which equals kills − deaths. Table 4 is captioned "kills", and the paper's runner can only produce cumulative reward, so `kills` and `deaths` are reported beside it.

**Readings of "600 frames".** The paper does not resolve which is meant, so all four are fixed now and all are reported:

| Reading | Decisions | Frame skip | Game tics | Runs |
|---|---|---|---|---|
| A (primary) | 600 | 2 | 1,800 | separate runs |
| B | 600 | 0 | 600 | separate runs |
| C | 200 | 2 | 600 | checkpoint of the A runs |
| D | 300 | 2 | 900 | checkpoint of the A runs; the runner's own default |

C and D equal shorter runs from the same seed, because runs are deterministic. This was checked on a dev seed.

**Published numbers to compare** (Table 4, one symbols-only run per model over 2 seeds of unstated value):
- S-GT (symbols only): Claude-4-Sonnet 12, GPT-4o 3, Gemini-2.5-Pro 12.
- F+S-GT (frame plus true symbols): 13–14.

**Policies:**
- `random`: uniform over the 3 actions, seeded by the run seed.
- `scripted`:
  - If a monster's labels-buffer box contains the centre column, ATTACK.
  - Otherwise turn toward the nearest monster.
  - With no monster visible, keep turning in the last direction.
  - It has no RNG.

**Seeds and episodes.** Seeds **1–30**, one run per seed per policy per reading: 30 A runs and 30 B runs per policy.

**Aggregation.** Mean ± SE (sample SD/√n) over the 30 runs. An errored or incomplete run is listed with its error, excluded from the mean, and counted.

**Commands.** P=`/tmp/jev-game-floors/venv-vizdoom/bin/python`, vizdoom 1.3.1. Each shard writes its own file, since `--out` overwrites. Every invocation below is run once for each shard `s` in {1-10, 11-20, 21-30}:
```
$P work/game-floors/vizdoom/run.py --policy random   --seeds $s --out /tmp/jev-game-floors/wave2/vizdoom-A-random-$s.jsonl
$P work/game-floors/vizdoom/run.py --policy scripted --seeds $s --out /tmp/jev-game-floors/wave2/vizdoom-A-scripted-$s.jsonl
$P work/game-floors/vizdoom/run.py --policy random   --seeds $s --frame-skip 0 --out /tmp/jev-game-floors/wave2/vizdoom-B-random-$s.jsonl
$P work/game-floors/vizdoom/run.py --policy scripted --seeds $s --frame-skip 0 --out /tmp/jev-game-floors/wave2/vizdoom-B-scripted-$s.jsonl
```

### 2. MiniWoB++ (the BrowserGym MiniWoB split behind the leaderboard)

**Published setting, as the runner implements it:**
- BrowserGym `DEFAULT_BENCHMARKS["miniwob"]` (`experiments/benchmark/configs.py:101-114` @`9e779f0`): all 125 tasks of `metadata/miniwob.csv`, 5 seeds each, **625 episodes**.
- Seeds come from `RandomState(42)` shared across the task list with `SEED_MAX = 2 ^ 32`. That is Python XOR, so it equals 34 and every seed is in 0–33 (`benchmark/utils.py:50-78`, `loop.py:35`). 590 (task, seed) pairs are distinct, and a repeated pair runs as `rep` 0, 1, … . `run.py --print-split` emits the list, sha256 `39f55c44e775b0f7626d9cac55318596443a023d3b8e9ab31ca236b1ddf392d8`.
- At most 10 actions per episode.
- BrowserGym sets `EPISODE_MAX_TIME` to 1,000,000 ms, which removes MiniWoB's 10 s timer.
- 0.5 s wait after each action, and a fresh page each episode.
- Task HTML: `miniwob` 1.1.0, byte-identical to miniwob-plusplus @`7fd85d7`, the commit BrowserGym pins.
- Run through the Farama `miniwob` package with Selenium and the local Chrome 154, headless.
- **Actions are narrower than BrowserGym's `miniwob_all`:** element click and focus-and-type only. Drag, draw and coordinate tasks are out of reach except through partial credit.

**Metric (the leaderboard's own).** `success = float(raw_reward > 0)` per episode (`browsergym/miniwob/base.py:183`), so partial credit counts. The score is 100 × the mean over all 625 episodes, errors counted as 0, ± 100·√(p(1−p)/n).

**Secondary metrics:**
- `success_strict`: raw ≥ 1.
- The mean raw reward.
- `reward_miniwob_10s`: MiniWoB's original time-scaled reward under its own 10 s timer, from the JS-measured episode time.

**Published numbers to compare** (leaderboard `results/*/miniwob.json` @`294ebe1`):
- **74.9 ± 1.2**: OrbyAgent with Claude-3.5-Sonnet, 2025-02-21, screenshot + HTML. Its SE implies n ≈ 1,250, not 625, and its episode list is not public.
- GenericAgent-GPT-5: 71.5 ± 1.8.
- GenericAgent-Claude-3.5-Sonnet: 69.8 ± 1.8 (n = 625, paper arXiv 2412.05467).
- GPT-4o: 63.8 ± 1.9.
- GPT-4o-mini: 56.6 ± 2.0.

**Policies:**
- `random`: uniform over clickable elements. A text input gets a random utterance token typed into it. Seeded per (task, seed, rep).
- `scripted`: generic, with no per-task code.
  1. Parse the utterance into ordered click/type intents.
  2. Type into the next untouched input.
  3. Click the best text match. A `<select>` gets the option text typed into it.
  4. Then click a submit or named button.
  5. Otherwise fall back to `random`.

**Episodes.** The full split, 625 per policy, no subsample.

**Commands.** P=`/tmp/jev-game-floors/venv-miniwob/bin/python`, miniwob 1.1.0, selenium 4.49.0; `PYTHONDONTWRITEBYTECODE=1`. Run once for each shard `k` in {0, 1, 2, 3}:
```
$P work/game-floors/miniwob/run.py --policy random,scripted --seeds benchmark --tasks all --shard $k/4 --out /tmp/jev-game-floors/wave2/miniwob.s$k.jsonl
```

### 3. Real-Time Reasoning Gym (arXiv 2511.04898, code `SALT-NLP/RealtimeGym` @`3d5b3ef`)

**Published setting, as the runner implements it:**
- Games Freeway, Snake and Overcooked at difficulties E, M and H (`src/realtimegym/__init__.py:9-19`).
- Step limit M = 100.
- Rewards are the gym's own `env.reward`:
  - Freeway: 100 − turns if the player crosses, else 0. A hit resets the player to the start.
  - Snake: food eaten − 1 on death.
  - Overcooked: dish 3, soup 5, serve 20.
- **Normalized score** S = (R − Rmin)/(Rmax − Rmin), using Table 4's Rmin/Rmax: Freeway 0/89, Snake −1/15, Overcooked 0/56.
  - R can exceed Rmax, and the paper states no clip. **Primary is S as written, unclipped.** S clipped to [0, 1] and raw R are reported beside it.
- The env is turn-based. Time pressure (4k–32k tokens per step) is simulated inside the agent wrapper (`agents/base.py:309-369`). A model-free policy answers with zero latency, so every time-pressure setting gives it the same score.
- **Published instances:** game seeds 0–7 for every game and level (`agile_eval.py:395`).
  - Freeway maps them through `seed_mapping` (`freeway.py:8-39`).
  - Snake maps them to N·1000 + i with N = 1/5/8 obstacles.
  - Overcooked uses the layouts `cc_easy`, `cc_hard` and `cc_insane`, where the seed changes nothing.

**Published numbers to compare** (normalized S, 8 game seeds × 4 samples):
- Table 6 at 8k tokens/step, E / M / H:
  - Freeway: Reactive V3 .98/.33/.06, AgileThinker .96/.84/.51.
  - Snake: Reactive V3 .77/.49/.30, AgileThinker .69/.54/.39.
  - Overcooked: Reactive V3 .92/.37/.09, AgileThinker 1.0/.92/.60.
- Table 2, wall-clock with 6-minute steps, difficulty unstated:
  - AgileThinker 0.88/0.45/0.89.
  - Reactive V3 0.24/0.37/0.57.
  - Planning R1 0.12/0.04/0.00.

**Policies:**
- `default`: the gym's DEFAULT_ACTION every step, i.e. an agent that never answers. Freeway `U`, Snake keep heading, Overcooked stay.
- `random`: uniform over legal actions, seeded.
- `scripted`: reactive, current observation only.
  - Freeway: up if lane y+1 is clear at the arrival turn, else stay, else down.
  - Snake: BFS to the nearest reachable live food, never into a wall, obstacle or body, avoiding dead-end cells.
  - Overcooked: fetch onions to a pot, fetch a dish, serve.

**Episodes.** Instances 0–7 × 3 games × 3 levels. default ×1, scripted ×1 and random ×4 reps give 432 episodes.

**Aggregation.** Per game × level, the mean of S over all runs. SE is over the 8 per-seed means, averaging within a seed first, as in App. C.2. Before the floors run, a first command checks Freeway's published seeds against Table 5's minimum-steps ranges.

**Commands.** P=`/tmp/jev-game-floors/venv-rtrg/bin/python`, realtime-gym 0.1.0 from an export of `3d5b3ef`:
```
$P work/game-floors/rtrg/run.py --allow-published --min-steps --difficulty E M H --seeds 0-7 > /tmp/jev-game-floors/wave2/rtrg-freeway-minsteps.jsonl
$P work/game-floors/rtrg/run.py --allow-published --game freeway snake overcooked --difficulty E M H --policy default scripted --seeds 0-7 --reps 1 --out /tmp/jev-game-floors/wave2/rtrg.jsonl
$P work/game-floors/rtrg/run.py --allow-published --game freeway snake overcooked --difficulty E M H --policy random --seeds 0-7 --reps 4 --out /tmp/jev-game-floors/wave2/rtrg.jsonl
```

### The state a Jev arm would receive (serializers, measured before this commit)

Each runner has a `serialize_state(...)` that returns only what an agent sees at decision time. It mirrors the observation each paper gave its agents. A sample of each is committed.

| Env | Sample | Bytes | o200k | claude-v5 | qwen3 | jev |
|---|---|---:|---:|---:|---:|---:|
| ViZDoom (the S-GT prompt's objects, health, armor, screen hints; seed 9001, decision 50) | `work/game-floors/vizdoom/state-sample.json` | 864 | 276 | 406 | 332 | 302 |
| MiniWoB (utterance + element list with bbox; click-checkboxes, seed 9000) | `work/game-floors/miniwob/state-sample.json` | 1,526 | 594 | 897 | 676 | 682 |
| RTRG (the gym's `obs["state"]` as JSON, one per game, M level, turn 2) | `work/game-floors/rtrg/state-sample.json` | 3,910 | 1,477 | 1,822 | 1,863 | 1,526 |

Counts come from `omp toks <file> --json`, which runs offline tokenizers. MiniWoB states range from 406 to 9,636 bytes across dev tasks. A ViZDoom state grows by about 59 jev tokens for each visible label.

**Re-run, keyless.** Install the venvs with uv, under /tmp only:
```
uv venv --python 3.12 /tmp/jev-game-floors/venv-vizdoom && uv pip install --python /tmp/jev-game-floors/venv-vizdoom/bin/python vizdoom==1.3.1
uv venv --python 3.12 /tmp/jev-game-floors/venv-miniwob && uv pip install --python /tmp/jev-game-floors/venv-miniwob/bin/python miniwob==1.1.0 selenium==4.49.0
git clone https://github.com/SALT-NLP/RealtimeGym /tmp/jev-game-floors/rtrg && mkdir -p /tmp/jev-game-floors/rtrg-src-3d5b3ef && git -C /tmp/jev-game-floors/rtrg archive 3d5b3ef | tar -x -C /tmp/jev-game-floors/rtrg-src-3d5b3ef
uv venv --python 3.11 /tmp/jev-game-floors/venv-rtrg && uv pip install --python /tmp/jev-game-floors/venv-rtrg/bin/python -e /tmp/jev-game-floors/rtrg-src-3d5b3ef
```
Then run the commands above. MiniWoB also needs a local Google Chrome; Selenium Manager fetches the matching chromedriver. No key is used, and nothing goes over the network except that chromedriver download.

## Results

Not yet run.
