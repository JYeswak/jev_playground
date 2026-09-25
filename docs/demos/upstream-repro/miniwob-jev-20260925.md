# Jev on MiniWoB++, BrowserGym split: result (bead `jev-jy7t.1.5`)

MiniwobLattice (subagent; Agent Mail `DarkCoast`), 2026-09-25.
- Lane: live, TypeSafe only. Model `jev-1.13.0`, pinned; every response resolved to it.
- N = 625 episodes: the full BrowserGym split, 125 tasks × 5 benchmark seeds.
- Bar and protocol: [`miniwob-jev-prereg-20260925.md`](miniwob-jev-prereg-20260925.md), commit `2a1b62d`.
- Code: `work/miniwob-jev/jev_arm.py`. Rows: `work/miniwob-jev/rows/`, commit `002d89a`.
- The non-author check by pane 1 is pending.

**Verdict.**
- **Floor bar: PASS.** Jev succeeds on 49.0% of episodes (Wilson 95% 45.1–52.9); the scripted floor succeeds on 22.4%. Exact McNemar on the 625 paired episodes: 172 Jev-only against 6 scripted-only, two-sided p = 2.2e-43.
- **Published rows: LOSE to four, TIE with GPT-4o-mini.** Jev loses to OrbyAgent, GenericAgent-GPT-5, GenericAgent-Claude-3.5-Sonnet and GenericAgent-GPT-4o. Its interval overlaps GenericAgent-GPT-4o-mini's by 0.2 points.
- None of the five rows ran this arm's protocol, so no comparison with them is a claim about those agents.

## Timeline: the bar strictly precedes the data

| Event | Time (UTC) | Evidence |
|---|---|---|
| Prereg, code and scorer committed | 01:57:40 | `2a1b62d`, subject level `[selftest]` |
| Prereg pushed to `origin/main` | before 01:58:02 | `git push` `8fa9ab5..2a1b62d` |
| Shard 0 launched | 01:58:08 | Infisical injection line in the process log |
| First live call | about 01:58:14 | `work/miniwob-jev/` gained `rows/` at 01:58:13.69; the first request followed that shard's env reset |
| Shards 1–3 launched | 01:58:35 | process logs |
| Last episode row written | 02:12:56 | rows file mtime |
| Rows committed and pushed | 02:13:39 | `002d89a` |

`live` checks before its first call that the prereg, `jev_arm.py` and the floor's `run.py` are committed and clean (`phase_gate.require_bar`). It started without error, so all three matched their committed bytes. The run was attended in this session through four supervised processes. No run halted, and no episode was replayed.

## Results

`python3 work/miniwob-jev/score.py`, keyless, over the committed rows. The floor rows are `work/game-floors/rows/miniwob.s*.jsonl` (`jev-jy7t.1.1`).

| Arm | N | Success % | Wilson 95% | SE | strict % (raw ≥ 1) | raw mean | 10 s reward | errors |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| **Jev (jev-1.13.0)** | 625 | **49.0** | **45.1–52.9** | 2.0 | 45.9 | 0.197 | 0.060 | 0 |
| scripted floor | 625 | 22.4 | 19.3–25.8 | 1.7 | 20.2 | −0.450 | −0.466 | 0 |
| random floor | 625 | 13.1 | 10.7–16.0 | 1.4 | 10.7 | −0.528 | −0.542 | 0 |

- **McNemar, exact, against scripted** on the identical (task, seed, rep) list: 172 episodes Jev-only, 6 scripted-only. p two-sided 2.19e-43; p one-sided in Jev's favour 1.10e-43.
- **Against random**: 230 Jev-only, 6 random-only, p two-sided 4.18e-60.
- **Floor bar (1): PASS.** The Wilson lower bound, 45.1, is above 22.4, and the two-sided McNemar p is below 0.05 with b > c.
- Of the 306 Jev successes, 19 are partial credit (0 < raw < 1). The leaderboard metric counts these, as it did for the floor's 14.

**Per task.**
- Jev succeeds at least once on 76 of 125 tasks. It scores 5/5 on 46 tasks and 0/5 on 49.
- The scripted floor scores higher on 3 tasks: click-menu-2 (0 vs 1), click-pie-nodelay (0 vs 1) and count-sides (0 vs 2).
- `score.py` prints every task where the two differ.

## Against the published rows (bar item 2)

Each row's Wilson interval uses n = 625, OrbyAgent's n = 1,306, implied by its SE. The label depends on whether the intervals separate.

| Published row (BrowserGym leaderboard @`294ebe1`) | Success % | Wilson 95% | Jev 45.1–52.9 vs row | Protocol matches? |
|---|---:|---|---|---|
| OrbyAgent-Claude-3.5-Sonnet | 74.9 ± 1.2 | 72.5–77.2 | **LOSE** | no: screenshot plus HTML, about 1,300 episodes from an unpublished list |
| GenericAgent-GPT-5 | 71.5 ± 1.8 | 67.9–74.9 | **LOSE** | no (see below) |
| GenericAgent-Claude-3.5-Sonnet | 69.8 ± 1.8 | 66.0–73.2 | **LOSE** | no |
| GenericAgent-GPT-4o | 63.8 ± 1.9 | 60.0–67.5 | **LOSE** | no |
| GenericAgent-GPT-4o-mini | 56.6 ± 2.0 | 52.7–60.5 | **TIE** (0.2-point overlap) | no |

The GenericAgent rows are the closest protocol:
- Like this arm, they are text-only: `use_ax_tree=True`, `use_html=False`, `use_screenshot=False` in each row's `README.md`.
- They read the AXTree; this arm reads the floor's Farama DOM element list.
- They act with BrowserGym's `bid` set, which includes free-text `fill`, `select_option`, `press`, scroll and drag. This arm has `click(ref)`, `type(ref, span of the utterance)` and `none`.
- They reason in chain-of-thought before each action.
- They run in BrowserGym's Playwright harness; this arm runs in Farama `miniwob` 1.1.0 with Selenium, on the same HTML, seeds, 10-step cap and 0.5 s wait.

The mismatch cuts both ways. Free-text fill gives the LLM rows actions this arm lacks. Jev never generates, so it cannot use them.

**Nothing here is claimed as beaten.**

## Reported, not barred (bar item 3)

| Quantity | Value |
|---|---|
| Jev calls | 2,808 in total (one per step), 4.49 per episode |
| Input tokens | 7,586,859 in total, 12,139 per episode, 2,702 per call (API `usage`) |
| Spend | $0.319 at $0.042 per million input tokens (`docs-mirror/typesafe/models.md:13,18`) |
| Jev latency per call | p50 161 ms, p90 283 ms (client-side, including the network) |
| Seconds per step, env only | 0.725 (floor: 0.642). Includes the preregistered 0.5 s wait. The machine's load average was 60–110 on 32 cores during the run |
| Seconds per step, end to end | 0.940 (episode wall minus reset, over steps; includes the Jev call) |
| Time-scaled reward, MiniWoB's own 10 s timer | mean 0.060 (scripted −0.466, random −0.542). 32 episodes ran past 10 s |
| Wall time | about 14.8 minutes for the four shards together (01:58:08 to 02:12:56), 2,845 episode-seconds |

## What the policy did

- 2,808 decisions. Jev chose `type` 260 times and `none` 509 times, and clicks the rest. No page reached the 255-option cap: the most options on a page was 79 and the most text heads was 4, and no click option was ever truncated.
- Of the 625 episodes:
  - 483 ended by the task's own terminal action. 306 of them succeeded and 177 failed; 119 succeeded on the first step.
  - 142 ran all 10 steps without ending. 66 of these contain a `none`, and in 43 the last five actions are all `none`. **Choosing `none` on a page it could not solve is Jev's main way of losing an episode here.**
- Of the 90 episodes containing any `none`, 5 succeeded.

## Failed calls

4 of 2,808 calls failed, in 4 different episodes. Each became a no-op step and was scored as whatever the episode earned. Three of the 4 episodes failed. multi-layouts seed 2 lost its first step to a timeout and still succeeded at step 8.
- **3 answers refused by the validator** (`ValueError: invalid Choice answer; no action executed`): bisect-angle seed 10 rep 1 at step 3, bisect-angle seed 23 at step 5, and enter-text-2 seed 31 at step 6. The raw answers were not logged, so which invariant each one broke is not known. Logging it would have meant changing the preregistered code in the middle of the run.
- **1 timeout**: multi-layouts seed 2 at step 0, `TypeSafeAPITimeoutError` at 30 s after the SDK's retries.

There were no halts, no HTTP 401/402/403 responses and no harness errors.

## Re-score, keyless

```
python3 work/miniwob-jev/score.py          # tables and verdict
python3 work/miniwob-jev/score.py --json   # same numbers, JSON
```

It uses the stdlib only and reads the committed rows. It exits 1 if the rows do not cover exactly the floor's 625 episodes.

## Boundary

- **One live run.** No repeat, so run-to-run variance at this N is unmeasured. The model is pinned at `jev-1.13.0`; a later `jev-latest` needs its own run.
- **No comparator model was called**: no Anthropic, xAI, OpenRouter or local model. RULE 14's LLM arm through `system-one-adapter-python` was not run, under the assignment and Joshua's 2026-09-24 no-paid-comparisons directive. The incumbents are the published rows, and their protocol differs from this arm's (above).
- **Not the BrowserGym harness.** Same HTML, seeds, step cap and wait, but through Farama `miniwob` and Selenium. The action set is narrower than BrowserGym's: no drag, coordinates or free text.
- **The verifier slot was not built.** The bead's precondition Noul needs a second serial call per step. Its value is unmeasured.
- The floors are lower bounds: one generic heuristic each, not the best no-model policy.
- Seconds per step were measured on a loaded, shared machine.
- **Not updated:** `EVAL.md`, `README.md` and the omp surface.
