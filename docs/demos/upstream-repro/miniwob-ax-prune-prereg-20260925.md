# MiniWoB AX-observation pruning: preregistration

Bead: `jev-jy7t.1.6`. Owner: TealHawk. This file is written before any live TypeSafe request.

## Question

Can Jev Nouls remove irrelevant nodes from the MiniWoB accessibility-like DOM observation before the existing MiniWoB Jev v1 policy sees it, while preserving the environment-checker success rate and reducing planner input tokens?

This is the MiniWoB-first slice of the WIZARD blind-spot proposal (`notes/deep/next-gen/WIZARD_REACTIONS_COD.md:183-234`). The native macOS AXUIElement slice and later omp `computer.*` seam are outside this run.

## Incumbent and controls

The planner is **not** a new LLM loop. Every arm uses the already-measured v1 `JevPolicy` from `work/miniwob-jev/jev_arm.py` at its pinned working-tree revision, with the same `after-page-change` none policy, the same pinned model `jev-1.13.0`, the same Choice validation, and the same action execution. Only the element list passed to that planner changes.

Arms:

- `full`: all elements from the floor observation.
- `code`: deterministic control retaining goal-overlapping interactive nodes and their parent/text subgraph; on no label match, all interactive nodes and their context.
- `jev`: one TypeSafe request per planner step, with three parallel Nouls per observed node: `relevant_to_current_goal`, `contains_required_value`, and `safe_to_omit`. Keep a node when either of the first two is at least `0.5`, or the last is below `0.5`; then retain all ancestors and attached text runs. Invalid/missing/out-of-range answers are errors and produce no action.
- `random`: seeded uniform positive-node sample at `KEEP_FRACTION=0.5`, followed by the same ancestor/text closure. The policy seed is the floor's stable `policy|task|seed|rep` seed.

The floor remains authoritative: `work/game-floors/miniwob/run.py` supplies the environment, action space, reward, and success checker. No reward, task parse, or simulator field is passed to the planner.

## Frozen split and protocol

- Task list: first 50 task names in `work/game-floors/miniwob/tasks.json`, in file order. The file SHA-256 is `af8890bf4877515c4eb27ee14a2fa0ea180b3c928709682634f96312986bb500`.
- Dev seed: `200` for every selected task.
- Held-out seed: `300` for every selected task.
- These seeds are disjoint from the v1 benchmark seeds `0-33` and pane 5's MiniWoB v2 seeds `100-104`.
- One episode per task/seed/arm: 50 dev + 50 held-out episodes per arm.
- `MAX_STEPS=1`, fixed before calls to keep the four-arm run within the 500-request cap. This is an intentionally cheap falsifying slice, not a claim about the ten-step BrowserGym benchmark.
- MiniWoB environment: pinned local floor, `episode_max_ms=1_000_000`, `wait_ms=500`, default data mode, page reset per episode.
- Jev model: `jev-1.13.0`, resolved model recorded in every live row. No comparator model, no OpenRouter, no Anthropic/xAI API, and no subscription-agent planner loop.

Rows are tracked at these exact paths and must not be redirected to `/tmp`:

- `work/miniwob-ax-prune/rows/dev-full.jsonl`
- `work/miniwob-ax-prune/rows/dev-code.jsonl`
- `work/miniwob-ax-prune/rows/dev-jev.jsonl`
- `work/miniwob-ax-prune/rows/dev-random.jsonl`
- `work/miniwob-ax-prune/rows/heldout-full.jsonl`
- `work/miniwob-ax-prune/rows/heldout-code.jsonl`
- `work/miniwob-ax-prune/rows/heldout-jev.jsonl`
- `work/miniwob-ax-prune/rows/heldout-random.jsonl`

## Bar and kill rules

Primary bar, evaluated on the held-out split:

1. `jev` success is within **1.0 percentage point** of `full` success.
2. `jev` mean `planner_input_tokens` is at least **40% lower** than `full`.
3. `jev` p95 episode `wall_s` is not higher than `full`.

The same quantities are reported on dev; dev does not substitute for held-out acceptance. Kill the proposal if held-out success drops below the one-point bar, if `code` and `jev` have identical success counts, or if Jev does not produce the 40% token cut. A kill is a valid result and is recorded rather than repaired by changing the threshold or split.

Planner-state token metric is the official SDK `usage.input_tokens` returned for the v1 planner request. The row also records full/seen serialized UTF-8 byte counts as an independent structural check. Wall time is the floor row's `wall_s`, including the fixed environment wait, and p95 uses the nearest-rank value over the 50 rows in each arm.

## Request and spend estimate

Maximum HTTP requests:

- full/code/random: `3 arms × 100 episodes × 1 planner step = 300` planner requests.
- Jev: `100` planner requests + `100` Noul-pruner requests = `200` requests.
- Total maximum: **500 TypeSafe requests**, before SDK retries. A failed request is recorded; no unattended retry loop is allowed.

Expected input volume is approximately 1M tokens or less from the one-step, 50-task slice; at the documented input price of `$0.042/M` this is expected to be well below `$1`. The shared MiniWoB v2 + Jericho work has an approximately `$25` credit envelope; this experiment claims no more than its 500-request allocation and does not start until pane 5 confirms MiniWoB v2 has finished.

## Oracle and boundary

Oracle: MiniWoB's environment checker for success; official TypeSafe response `usage.input_tokens` and pinned model field for request accounting. No LLM comparator is used. The result will report actual request count, model set, input tokens, p50/p95 wall time, and all failures.

Not run by this preregistration: native macOS AXUIElement tasks, MacArena, screenshot-only agents, BrowserGym's 625-episode benchmark, a ten-step policy, omp hooks, and any paid or subscription-agent planner. A live result is not valid until the code path and this preregistration are committed and the pane-5 dependency has cleared.
