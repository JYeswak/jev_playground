<!-- Local environment probe by LocalEnvProbe (task agent spawned by pane 1 AmberWillow, bead jev-jy7t.1), 2026-09-24. Installs and runs in /tmp/jev-envprobe only; random agents; no model API called. Timings measured under heavy machine load (see its caveat). Pane 1 has not re-run these. -->

## Local environment probe: computer-use and game envs on this Mac (M3 Ultra, 2026-09-24)

The load-bearing finding: 15 environments run here today. Every game env steps in about 0.02-15 ms p50, and Jev's measured p50 is about 130 ms per call. So in every game env, Jev is the bottleneck, not the simulator.

**How this was run.** Each env got its own uv venv under `/tmp/jev-envprobe/<name>` on Python 3.12. The general install command was `uv venv --python 3.12 /tmp/jev-envprobe/<name> && uv pip install --python /tmp/jev-envprobe/<name>/bin/python <pkgs>`, with `UV_CACHE_DIR=/tmp/jev-envprobe/uvcache`. Each probe ran a random agent for up to 200 steps or 60 s; the MiniWoB and BrowserGym probes used 60 steps or 45 s. Step times are wall time around `env.step` only; resets are not counted.

Logs are in `/tmp/jev-envprobe/logs/` and probe scripts are `/tmp/jev-envprobe/p_*.py`. Nothing was written inside `/Users/josh/Developer/jev`: the only untracked file there, `jev-drone/MUJOCO_LOG.TXT`, is dated 2026-09-23. No model API was called.

**Timing caveat:** the machine was busy with other agents. `uptime` showed load averages of 54.40 / 37.61 / 22.32 on 32 cores. p95 values are noisy; where I ran a probe twice I give both numbers.

### Table

| Env (version) | Install ok | Runs | step ms p50 / p95 | State that can become JSON | Blocker |
|---|---|---|---|---|---|
| ALE Atari: Breakout / Pong / Freeway, `ale-py 0.12.1`, `gymnasium 1.3.0` | yes (86 s) | yes, 200 steps each | RAM obs: 0.38-0.92 / 0.7-25 (run 1 and run 2 differ; noisy under load). RGB obs: 0.42-0.90 / 2.9-32 | 128-byte RAM, `info` (lives, frame number) | none. 111 ROMs ship inside `ale_py/roms`, including breakout, pong and freeway |
| OCAtari 2.2.1 (object wrapper) | yes (same venv) | yes: Breakout, Pong, Freeway | 0.22-1.0 / 0.43-8.8 | Per-object `category, x, y, w, h`. Example: `{"cat":"Chicken","x":44,"y":187,...}` and a list of `Car` objects | none. My JSON dump failed once on a numpy int64 (a bug in my probe, not in OCAtari) |
| ViZDoom 1.3.1: basic / defend_the_center / deadly_corridor | yes (41 s, arm64 wheel) | yes | frame_skip 4: 0.86 / 1.9, 0.87 / 3.4, 0.46 / 0.88 | Game variables (HEALTH, AMMO2), labels buffer (screen box and world position per object, e.g. `Zombieman`, `GreenArmor`), full object list with positions, sectors, button names | none. Scenarios are bundled |
| Crafter | yes (21 s) | yes | 1.46 / 2.44 | Inventory (16 keys), achievements (22), 64x64 semantic map, `player_pos`, nearby object types | the gym-less `DiscreteSpace` has no `.sample()`; use `randint(action_space.n)` |
| Craftax 1.6.1 (JAX 0.11.2, CPU) | yes (89 s) | yes | Classic-Symbolic: 3.0 / 7.1 (jit compile 5.8 s). Full Symbolic: 10.5 / 19.4 (compile 17.2 s). vmap of 1024 envs: 717 ms per batched step, i.e. 1,427 env-steps/s | Structured state dataclass: map, mob_map, positions, health, food, drink, energy, inventory, zombies, cows, achievements; flat symbolic obs of 1,345 or 8,268 values | none. Not GPU-accelerated here (JAX on CPU) |
| MiniGrid 3.1.0 / BabyAI: DoorKey-8x8, GoToLocal, BossLevel | yes (35 s) | yes | 0.135-0.16 / 0.19-0.87 | Mission string plus a full-grid object list, e.g. `{"type":"key","color":"yellow","pos":[3,4]}`, agent position and direction | none |
| NLE 1.3.0: NetHackScore, NetHackChallenge | yes (88 s, built from sdist locally) | yes | 0.05 / 0.15; 0.025 / 0.025 | `message`, 27-value `blstats`, `chars` / `glyphs` map, `inv_strs`, `screen_descriptions`, `tty_chars` | none |
| MiniHack 1.0.2: Room-5x5, KeyRoom-S5 | yes | yes, after a fix | 0.13 / 0.24; 0.16 / 0.38 | As NLE, plus `chars_crop` / `glyphs_crop` | `import pkg_resources` fails. Fix: `uv pip install "setuptools<81"` |
| TextWorld 1.7.0 | yes (61 s) | yes | 3.4 / 5.1 | Objective, list of admissible commands, logic facts (`at(P, scullery: r)`, 34 facts), inventory, description | none. `tw-make custom ...` generated a game in 9.1 s |
| BALROG harness (git main) | failed at first; ok with a fix | partly | babyai 0.81 / 5.8; crafter 13.7 / 70.6; babaisai 0.94 / 22.5; textworld 3.0 / 6.6 | Text observations (`long_term_context` / `short_term_context`), language action lists (e.g. 17 Crafter actions, 6 BabyAI actions) | **nle and minihack segfault** (SIGSEGV 139) in `NLELanguageObsv()` (`balrog/environments/nle/auto_more.py:9`, balrog-nle 0.9.0) |
| MiniWoB++ via `miniwob 1.1.0` + Selenium 4.49 + local Google Chrome | yes (40 s) | yes: click-test-2, click-button, enter-text, click-checkboxes | 98-145 / 197-302. First launch 10-23 s | `utterance` plus `dom_elements` (ref, tag, text, left/top/width/height, classes) | none. Needs Chrome, which is present. Selenium cache pointed at `/tmp` |
| BrowserGym 0.14.3 on MiniWoB (Playwright chromium-1117 in `/tmp`) | yes (65 s, plus a 28 s browser download) | yes, same 4 tasks | Default: 1,170-1,310 / 1,350-1,650. With `pre_observation_delay=0`: 707 / 923 | Accessibility tree with element ids (e.g. `[21] checkbox 'Nb', checked='false'`), DOM object, `extra_element_properties`, goal | none. It is slow by design: default `pre_observation_delay: float = 0.5` (`browsergym/core/env.py:80`) |
| python-chess 1.11.2 | yes (6 s) | yes, random self-play | 0.031 / 0.063 | FEN and legal moves in SAN | **no engine**: `brew list stockfish` reports no such keg and nothing is on PATH |
| 2048 (`gymnasium-2048`) | yes (35 s) | yes | 0.057 / 0.082 | `info.board` 4x4 of log2 tiles, score, max, `is_legal`, `illegal_count` | none |
| Tetris (`tetris-gymnasium`) | yes (83 s) | yes | 0.089 / 0.133 | Dict: board 24x18, `active_tetromino_mask`, holder, queue; `lines_cleared` | none |
| gym-sokoban on gym 0.26.2 | yes (18 s) | yes, after two fixes | 3.3 / 6.7 (renders RGB every step) | `room_state` 10x10 symbolic grid and `player_position` | Two fixes: `setuptools<81` (pkg_resources) and `numpy<2` (`np.bool8`) |
| jev-drone @c0efd03 (repo check) | uses the repo's existing `.venv` (MuJoCo 3.14.0); nothing installed | **yes, without a key**: `run.py --no-jev --fast --seconds 65 --seeds 0` | 65 s of simulated flight took 21 s of wall time (not a per-step figure) | Result JSON: collisions, target_visible_pct, standoff distances, crossed_barrier, ... | The Jev-engaged runs need `TYPESAFE_API_KEY`. The key is in Infisical; it was not used, per instructions. Run was in a `/tmp` copy with `PYTHONDONTWRITEBYTECODE=1` |
| jev-ultrafast @452c1ad (read only) | `.venv` exists | not run | n/a | Page snapshots via `snapshot.js` / Browser Harness | Demo and examples need `TYPESAFE_API_KEY` + `TEXT_MODEL_API_KEY` (OpenRouter). The README says tests are offline and `scripts/check_guards.py` makes no model calls but needs Chrome remote debugging via Browser Harness. Not run: out of scope, and it attaches to the user's Chrome |
| jev-doom-agent | n/a | n/a | n/a | n/a | not cloned (skipped as instructed) |

### Ready now
These ran a random or no-op agent on this Mac, with timings above:

- **ALE Atari** (RAM and RGB) and **OCAtari** object lists (Breakout, Pong, Freeway). No ROM download is needed.
- **ViZDoom** (basic, defend_the_center, deadly_corridor), with labels, objects and game variables.
- **Crafter** and **Craftax** (Classic-Symbolic and Symbolic on CPU JAX).
- **MiniGrid / BabyAI** (DoorKey, GoToLocal, BossLevel).
- **NLE** (NetHackScore, NetHackChallenge).
- **MiniHack** (after the setuptools pin).
- **TextWorld** (locally generated game).
- **BALROG** for babyai, crafter, babaisai and textworld (after the fixes below).
- **MiniWoB++** via Selenium and local Chrome.
- **BrowserGym MiniWoB** via Playwright chromium in `/tmp`.
- **python-chess** (no engine), **2048**, **Tetris**, **Sokoban** (after pins).
- **jev-drone** runs its no-Jev ablation without a key.

What this means for a Jev loop [INFERENCE]: every game env steps in 0.02-15 ms p50. MiniWoB costs about 100-145 ms per step and BrowserGym 0.7-1.3 s, so in browser envs the browser is as slow as, or slower than, Jev.

### Fixable (exact fix)
1. **BALROG install** fails building `balrog-nle` with "Compatibility with CMake < 3.5 has been removed" (CMake 4.2.3). Fix: `CMAKE_POLICY_VERSION_MINIMUM=3.5 uv pip install --python balrog/bin/python "git+https://github.com/balrog-ai/BALROG.git"`. That succeeded in 38 s.
2. **BALROG runtime** fails on `pkg_resources`. Fix: `uv pip install --python balrog/bin/python "setuptools<81"`.
3. **BALROG textworld and boxoban assets** are missing. Fix: run `balrog/bin/balrog-post-install` from `/tmp/jev-envprobe`. It downloads boxoban from `github.com/deepmind/boxoban-levels` and tw_games from BALROG's own Google Drive link. Then symlink `site-packages/tw_games` to `/tmp/jev-envprobe/tw_games`, because the code joins the path onto the package parent directory (`textworld/base.py:11,33`). After that, textworld ran. Also, the textworld action space is `AlwaysTrue` (free-form text), not a list.
4. **MiniHack / gym-sokoban** fail on `pkg_resources`. Fix: `setuptools<81`. Sokoban also needs `numpy<2`.
5. **Chess engine.** Homebrew offers a `stockfish` 19 bottle for `arm64_tahoe`. The fix is `brew install stockfish`, which needs your approval, since it isn't installed and brew installs were out of bounds. Nothing on PATH or found by `mdfind` counts as an engine.
6. **BrowserGym speed.** Pass `pre_observation_delay=0.0`; measured p50 dropped from about 1,170 ms to 707 ms on click-checkboxes. The remaining cost is AX/DOM/screenshot extraction plus network idle waits (`env.py:489-571`).

### Blocked
- **BALROG's NLE and MiniHack wrappers segfault** on macOS arm64 inside `NLELanguageObsv()` (balrog-nle 0.9.0). The faulthandler traceback points to `auto_more.py:9` for both. Workaround [INFERENCE, untested]: use the plain `nle 1.3.0` venv, which works, and build the JSON state yourself from `message`, `blstats`, `chars` and `inv_strs` instead of BALROG's language wrapper. I found no fix inside BALROG.
- **jev-ultrafast live paths** need `TYPESAFE_API_KEY` + `TEXT_MODEL_API_KEY` and attach to your Chrome. Not run. It is not blocked by missing software.
- **jev-doom-agent** is not cloned. ViZDoom itself works here, so a Doom agent is feasible if the repo is cloned.
- **Craftax at speed:** there is no GPU/Metal JAX backend here. Batched CPU vmap reached only 1,427 env-steps/s (measured under load), so Craftax's published throughput does not carry over to this Mac [INFERENCE].
