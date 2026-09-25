# MiniWoB AX-observation pruning: live receipt

Bead: `jev-jy7t.1.6`. Preregistration: `miniwob-ax-prune-prereg-20260925.md` (committed `dd04baf`,
scorer paragraph `b62e9e6`, both before any live call). Runner: subagent AxPruneRun, Agent Mail
`QuietPrairie`, 2026-09-25.

**Verdict on the held-out bar: LOSE.** Jev's pruning kept success equal to `full` (14/50 vs 14/50),
but it cut mean planner input tokens by only 25.9%. The bar required 40%. Its p95 wall time was
also higher than `full`. The kill rule "Jev does not produce the 40% token cut" fires. Counting the
pruner request, the `jev` arm spent 4.2x the input tokens of `full`.

## What ran

- The arms, seeds (dev `200`, held-out `300`), task list (the first 50 of `tasks.json`,
  sha256 `af8890bf…`), `MAX_STEPS=1`, row paths, and scorer are as preregistered. `ax_prune.py` and
  `score.py` ran unmodified (`ax_prune.py` sha256 `5174f75b…` at `dd04baf` and HEAD).
- Every row was produced through `work/miniwob-ax-prune/run_frozen.py` (`10cba66`; the SIGSTOP
  option was added in the next commit). The launcher was committed before the first live call. Its
  only job is to pin the code: pane 5 holds uncommitted working-tree edits to
  `work/miniwob-jev/jev_arm.py` (an unconditional `utterance_spans` quote-stripping change) and to
  `work/game-floors/miniwob/run.py` (gated on `MINIWOB_V3`). Without the launcher, the planner that
  ran would not have been the committed v1 planner the prereg names. The launcher exports the
  `dd04baf` bytes of `jev_arm.py` (sha256 `f6f712fe441cf3ac…`), `run.py` (`e0b0c42886e4ba17…`), and
  `tasks.json` to `/tmp/jev-ax-prune-frozen/dd04baf/`. It redirects `ax_prune`'s two module loads
  there and refuses on any sha mismatch or a set `MINIWOB_V3`. Every one of the 400 rows carries
  `frozen_pin_commit: dd04baf` and `frozen_sources_sha256_16`. Pane 1 approved this option on
  2026-09-25.
- The launcher also stops a run before the next episode after any HTTP 401/402/403. None occurred.
- The none-policy defect that halted MiniWoB v2 (`dedada5`, an empty Choice) cannot occur at
  `MAX_STEPS=1`. Each episode builds a fresh `JevPolicy` (`ax_prune.py:305`, factory `:376`), so
  step 0 runs with `page_fingerprint is None` and `none` is always offered
  (`jev_arm.py@dd04baf:453-463`). No prereg amendment was needed.
- Planner and pruner ran on TypeSafe `jev-1.13.0`, pinned. The model was resolved and recorded in
  every row, and all 400 rows resolved to `jev-1.13.0`. The key came from
  `infisical run --silent --projectId=42b194c3-…`. No comparator model, no OpenRouter, no
  Anthropic/xAI API.
- Runs were sequential, one arm at a time, supervised with `hub`. Each started with
  `AX_PRUNE_STOP_BEFORE_FIRST_EPISODE=1`, which puts the process under SIGSTOP after the row file
  is open and before any request. At that point `lsof` was run on the Python runner, then the run
  resumed with SIGCONT. The only regular file each runner held open for writing was its own
  preregistered row path:

| Run | Runner PID | Write path (lsof, fd 3w) |
|---|---:|---|
| dev full | 93198 | `/Users/josh/Developer/jev/work/miniwob-ax-prune/rows/dev-full.jsonl` |
| dev code | 10704 | `/Users/josh/Developer/jev/work/miniwob-ax-prune/rows/dev-code.jsonl` (see note) |
| dev jev | 25357 | `/Users/josh/Developer/jev/work/miniwob-ax-prune/rows/dev-jev.jsonl` |
| dev random | 41223 | `/Users/josh/Developer/jev/work/miniwob-ax-prune/rows/dev-random.jsonl` |
| held-out full | 50311 | `/Users/josh/Developer/jev/work/miniwob-ax-prune/rows/heldout-full.jsonl` |
| held-out code | 59132 | `/Users/josh/Developer/jev/work/miniwob-ax-prune/rows/heldout-code.jsonl` |
| held-out jev | 75381 | `/Users/josh/Developer/jev/work/miniwob-ax-prune/rows/heldout-jev.jsonl` |
| held-out random | 85142 | `/Users/josh/Developer/jev/work/miniwob-ax-prune/rows/heldout-random.jsonl` |

Note on dev code: while it was stopped, `pgrep` matched both the `infisical` parent and the Python
child, so the pre-resume `lsof` printed nothing. The Python child's `lsof` was taken seconds after
SIGCONT and showed the path above. The other seven were taken while the process was stopped.

Row commits: dev `2c6cfed`, held-out `66b8f61`, both `[live]` and path-limited.

## Results (keyless re-score)

```text
env -u TYPESAFE_API_KEY /tmp/jev-miniwob-jev/venv/bin/python work/miniwob-ax-prune/score.py
```

Held-out (seed 300), N=50 per arm:

| Arm | Success | Rate | Mean planner input tokens | Cut vs full | p50 wall_s | p95 wall_s | Errors |
|---|---:|---:|---:|---:|---:|---:|---:|
| full | 14/50 | 0.28 | 1944.70 | — | 0.9349 | 1.4484 | 0 |
| code | 9/50 | 0.18 | 1068.24 | 45.1% | 0.8561 | 1.0174 | 0 |
| jev | 14/50 | 0.28 | 1441.62 | 25.9% | 1.0771 | 1.7938 | 0 |
| random | 8/50 | 0.16 | 1396.88 | 28.2% | 0.8240 | 0.9977 | 0 |

Dev (seed 200), N=50 per arm:

| Arm | Success | Rate | Mean planner input tokens | Cut vs full | p50 wall_s | p95 wall_s | Errors |
|---|---:|---:|---:|---:|---:|---:|---:|
| full | 15/50 | 0.30 | 1847.00 | — | 1.0446 | 1.7112 | 0 |
| code | 10/50 | 0.20 | 984.04 | 46.7% | 0.8946 | 1.1516 | 0 |
| jev | 15/50 | 0.30 | 1373.22 | 25.7% | 1.0304 | 1.5110 | 0 |
| random | 7/50 | 0.14 | 1263.96 | 31.6% | 0.8528 | 0.9931 | 0 |

Tasks that succeeded in at least one arm (`ever_successful_tasks`, descriptive only):

- held-out **14/50**: buy-ticket, click-button, click-color, click-dialog, click-link, click-tab,
  click-tab-2, click-tab-2-easy, click-tab-2-medium, click-test, click-test-2,
  click-test-transfer, click-widget, count-shape.
- dev **16/50**: buy-ticket, click-button, click-checkboxes, click-checkboxes-transfer,
  click-color, click-dialog, click-link, click-shape, click-tab, click-tab-2-easy,
  click-tab-2-medium, click-test, click-test-2, click-test-transfer, click-widget, count-sides.

## Bar, held-out

| Condition | Required | Measured | Result |
|---|---|---|---|
| 1. jev success within 1.0 pt of full | ≥ 27.0% | 28.0% vs 28.0% | pass |
| 2. jev mean planner input tokens ≥ 40% lower | ≤ 1166.82 | 1441.62 (−25.9%) | **fail** |
| 3. jev p95 wall_s ≤ full | ≤ 1.4484 | 1.7938 | **fail** |
| Kill: code and jev success counts identical | — | 9 vs 14 | not fired |
| Kill: no 40% token cut | — | 25.9% | **fired** |

**Bar verdict: LOSE.**

Jev against the controls, held-out. The arms did not run at the same budget, so none of these
comparisons is budget-matched:

- **vs random.** Jev kept fewer nodes (481 vs 548 of 770) at a similar planner token count
  (1441.6 vs 1396.9) and won 14 successes to 8 (discordant pairs 6/0, exact two-sided McNemar
  p=0.031; this test was not preregistered, so it is descriptive). On this slice, Jev's node
  choice beats a uniform 50% sample closed the same way.
- **vs code.** The deterministic selector cut 45.1% of tokens and lost 5 successes (9 vs 14;
  discordant 5/0, exact p=0.0625, descriptive). Jev cut less and lost nothing. Neither arm
  reached "at least 40% cut with no success loss".
- **The same tasks every time.** Jev and full succeeded on exactly the same tasks in both splits,
  with zero discordant pairs. Jev's pruning never helped the planner, and it never hurt it.
- **Where the shortfall comes from.** Jev left the observation byte-identical to `full` on 20 of
  50 held-out episodes (19/50 on dev). The keep rule keeps any node judged relevant or required,
  or not safe to omit. On these small MiniWoB pages that keeps most nodes. Structural byte cut:
  jev 35.0%, code 53.2%, random 28.1%.
- **Cost.** One pruner request per step carried the full state plus three Nouls per node. It
  averaged 6,820 input tokens per held-out episode (max 55,937). With it, the `jev` arm spent
  8,261 input tokens per episode against 1,945 for `full`. A pruner that costs 4.2x the tokens it
  is meant to save cannot pay for itself at `MAX_STEPS=1`, whatever the planner cut.

## Calls and spend

| Item | Count |
|---|---:|
| HTTP attempts (SDK retries included, counted from the SDK log) | 500, all HTTP 200 |
| Planner requests (8 runs × 50) | 400 |
| Jev pruner requests (2 runs × 50) | 100 |
| SDK retries, 4xx/5xx, 402 | 0 |
| Planner input tokens | 565,983 |
| Pruner input tokens | 660,572 |
| Total input tokens | 1,226,555 |
| Planner output tokens (not billed) | 175,952 |
| Spend at $0.042/M input | **$0.0515** |

That is exactly the preregistered 500-request cap, with no retries.

## Boundary

- One step (`MAX_STEPS=1`) over 50 tasks × one seed per split. This is not the ten-step
  BrowserGym benchmark, and nothing here claims anything about it. `full` success of 28% is a
  one-step number.
- MiniWoB DOM-derived element lists only. No native macOS AXUIElement tree, no omp `computer.*`
  surface, no screenshots.
- One prune design: three Nouls per node, OR-keep at 0.5, ancestor and text closure. This loss rules
  out this design at this budget, not Jev pruning in general (see the `NEGATIVE_EVIDENCE.md` row).
- `wall_s` includes the 0.5 s environment wait and, for `jev`, the pruner round trip. Runs were
  sequential on one machine, so wall times are comparable across arms but are not a latency
  benchmark.
- No comparator LLM ran (Joshua's standing 2026-09-24 order). No response bodies, key material,
  screenshots, or browser state are committed. Rows hold element-list byte and node counts only.
- The bead stays `in_progress` for pane 1's non-author check.
