# Jev on MiniWoB++, BrowserGym split: preregistration (bead `jev-jy7t.1.5`)

MiniwobLattice (subagent; Agent Mail `DarkCoast`), 2026-09-25. This file and the code it names are committed and pushed **before the first live call**. `live` refuses to start unless this file, `work/miniwob-jev/jev_arm.py` and the floor runner are all committed and clean (`work/sr-adopt/phase_gate.py:require_bar`). Results go to `miniwob-jev-20260925.md`; nothing here changes after data.

Lane: live, TypeSafe only. Model pinned `jev-1.13.0`. No comparator model of any kind is called (no Anthropic, xAI, OpenRouter or local model). The incumbents are the published leaderboard rows below.

## The bar, verbatim (pane 1, bead comment 2026-09-25 01:25 UTC)

> BAR MADE CONCRETE (pane 1, before any Jev call; the subagent's prereg may add operational detail but not loosen this): split = the BrowserGym MiniWoB split pane 2 measured (125 tasks x 5 benchmark seeds = 625 episodes, work/game-floors/miniwob/run.py --seeds benchmark --tasks all, max 10 steps, 0.5 s wait), metric = the leaderboard's success % (raw reward > 0, errors = 0). Floors to beat (jev-jy7t.1.1, closed): scripted 22.4 +- 1.7, random 13.1. (1) PASS vs floor iff the Jev arm's Wilson 95% lower bound is above 22.4 AND McNemar on the paired 625 episodes vs the scripted floor rows has p < 0.05 in Jev's favour. KILL if not. (2) Against published LLM rows (GenericAgent-GPT-5 71.5 +- 1.8, GenericAgent-Claude-3.5-Sonnet 69.8, GPT-4o 63.8, GPT-4o-mini 56.6, OrbyAgent 74.9 on a different, larger episode list), each reported BEAT / TIE / LOSE by whether the Wilson intervals separate; no row is claimed beaten unless its protocol matches (state it). (3) Reported, not barred: seconds per step, Jev calls and input tokens per episode, time-scaled reward under MiniWoB's own 10 s timer. Action space as the floor's: click(ref) and type(ref, text) where text is chosen by a Choice over code-extracted spans of the utterance, never written by Jev.

## How the bar is computed (no loosening)

`work/miniwob-jev/score.py`, stdlib only, reads the committed rows and nothing else.

- **Success** per episode: `raw_reward > 0` and no harness error. An errored episode counts as a failure, as in the floor.
- **Wilson 95%**: z = 1.959964, k = successes, n = 625.
- **McNemar**: exact, on the 625 (task, seed, rep) pairs shared with `work/game-floors/rows/miniwob.s*.jsonl` policy `scripted`. b = Jev success and scripted failure; c = the reverse. "p < 0.05 in Jev's favour" is read as **two-sided exact p < 0.05 and b > c**, which is stricter than a one-sided test; the one-sided p is reported beside it.
- **PASS** iff Wilson lower > 22.4 and the McNemar condition holds, and the rows cover exactly the 625 floor episodes. Anything else is **KILL**, and a `NEGATIVE_EVIDENCE.md` row with a retry condition follows.
- **Published rows** (BrowserGym leaderboard `results/*/miniwob.json` and `README.md` @`294ebe1`): each gets a Wilson interval from its published mean at n = 625 (the split's size), except OrbyAgent at n = round(p(1−p)/SE²) = 1,306, since its list is not public. Jev lower > row upper is **BEAT**; Jev upper < row lower is **LOSE**; otherwise **TIE**.
- **Protocol.** No published row matches this arm's protocol, so no row can be claimed beaten; a BEAT would be reported as a number, not a win over that agent.
  - GenericAgent rows (GPT-5, Claude-3.5-Sonnet, GPT-4o, GPT-4o-mini): text-only like this arm (`use_ax_tree=True`, `use_html=False`, `use_screenshot=False`), but they read the AXTree, act with the BrowserGym `bid` action set (free-text `fill`, `select_option`, `press`, scroll, drag), think in chain-of-thought, and run in BrowserGym's Playwright harness.
  - OrbyAgent: screenshot plus HTML, about 1,300 episodes from an unpublished list.
  - This arm: Farama `miniwob` 1.1.0 with Selenium, the same HTML, seeds, 10-step cap and 0.5 s wait; the floor's DOM element list; `click(ref)` and `type(ref, span)` only.

## Episodes and harness: the floor's, unchanged

- `work/game-floors/miniwob/run.py` supplies the task list, the benchmark seeds (`--print-split` sha256 `39f55c44e775b0f7626d9cac55318596443a023d3b8e9ab31ca236b1ddf392d8`), `episode_plan`, `make_env`, `run_episode`, `serialize_state`, `clickable_refs`, the 10-step cap, `EPISODE_MAX_TIME` = 1,000,000 ms, the 0.5 s wait and the success metric. The arm registers a `jev` entry in the floor module's `POLICIES` at runtime; the floor file is not edited and `random`/`scripted` are untouched.
- 625 episodes, the full split, no subsample. Four shard processes, tasks `[k::4]` for k = 0..3, as the floor ran. Rows: `work/miniwob-jev/rows/miniwob-jev.s{k}.jsonl`, one JSON object per episode.
- Environment: Python 3.12.12, `miniwob` 1.1.0, `selenium` 4.49.0, `gymnasium` 1.3.0, `numpy` 2.5.3 (the floor venv's pins), `typesafe-sdk` 0.7.1 installed from the vendored `upstream/typesafe-ai/typesafe-sdk-python` @`0ffd094`; local Google Chrome 154.0.8037.57, headless. The machine is shared and loaded; seconds per step are reported as measured.

## The policy, fixed

**One TypeSafe request per step**, official SDK `TypeSafeClient(model="jev-1.13.0", retry=RetryPolicy(), timeout=30.0)`; `RetryPolicy()` defaults are 2 retries on 408/429/5xx and connection errors, backoff 0.5 s doubling to 5 s.

**State** (sent as `state`, a JSON object): the floor's `serialize_state(utterance, els, step, 10, history, select_options)` exactly: `utterance`, `step`, `max_steps`, `actions`, `history` (this episode's actions as `{type, ref, text?}`), and `elements` (`ref`, `parent`, `tag`, `text`, `value`, `id`, `classes`, `bbox`, `focused`, and `options` for a `<select>`). A checked checkbox shows `value: "True"`.

**Question `action`**: a Choice.

- Options, code-enumerated each step:
  - `click [r] <desc>` for every r in the floor's `clickable_refs(els)` (the same set the floor's random policy draws from);
  - `type [r] <desc>` for every text input (`TEXT_INPUT_TAGS`) and every `<select>` one of whose options equals (after the floor's `_norm`) a span of the utterance;
  - `none: do nothing this step`.
- `<desc>` is the tag, `#id` if any, the visible text in quotes (the element's own text, else its text runs, else its `<label>`'s text runs, else a button's value; cut to 60 characters), and `value="..."` for a non-button input with a value (cut to 40).
- **Cap 255** (the API's Choice limit). Over the cap, every `type` option and `none` are kept, then `click` options on interactive elements, then the rest, each in DOM order, and the kept options are listed in DOM order. On dev seed 9000 no page came near the cap (maximum 76 options over 878 steps), so truncation is recorded per step but not expected.
- Instructions, verbatim, with the utterance substituted:

```
Goal: {utterance}
Choose the one next action that makes progress on this goal on the current web page. The state lists the page elements (ref, tag, text, value, id, classes, bbox) and the actions already taken this episode (history). 'click [ref]' clicks that element. 'type [ref]' types text taken from the goal into that field or dropdown; the text is chosen separately. Do not repeat an action from the history unless the goal requires doing it again. Choose 'none' only if no offered action makes progress.
```

**Questions `text_<r>`**, one per `type` option, in the same request (the operation/target fan-out of `jev-ultrafast/jev_ultrafast/model.py:81-148`): a Choice over code-extracted spans of the utterance, in this order, deduplicated, at most 255:

1. quoted strings (`"..."` and `“...”`);
2. whitespace tokens;
3. contiguous token n-grams, n = 2, 3, ... up to the whole utterance, left to right, with each word's own quote marks removed before joining.

Every span has `"'.,:;!?()` stripped from its ends. For a `<select>`, only the spans equal to one of its options are offered. Instructions, verbatim:

```
Goal: {utterance}
Which text from the goal should be typed into element [{r}] ({desc})?
```

**Reading the answer.** The `action` answer is validated with `jev-ultrafast`'s `validate_choice` invariants: the choice is an offered option, the probability keys equal the options, every number is finite in [0, 1], the probabilities sum to 1 within 0.02, and the choice has the top probability. `click [r]` becomes the floor's `click(r)`, `none` becomes Farama `NONE`, and `type [r]` becomes `type(r, text)`, where text is the validated choice of `text_<r>`. Unused text heads are never read. Jev never writes text.

**Not in this arm.** The bead's verifier slot, a precondition Noul on the chosen action, would need a second, serial request per step and a threshold that could only be tuned on live data this prereg forbids before the first call. It is left out, and the arm is one request per step. No LLM arm through `system-one-adapter-python` is run: the assignment and Joshua's 2026-09-24 directive exclude comparator calls, so the published rows are the incumbent reference.

## Failures, halts and resume (fixed before data)

- **A failed call** (an SDK error after its retries, a timeout, or an answer the validator refuses) makes **that step a no-op** (Farama `NONE`, which spends the step). It is recorded in the row's `failures` with the step and the error, and scored as whatever the episode then earns. It is never retried by hand.
- **Halt.** Three failed calls in a row within a process, or any HTTP 401, 402 or 403, halt that process at once. The episode in progress is **not written**, so a resumed run replays it from reset with the same seed. Earlier completed episodes stand, including any with isolated failed calls. The halt depends only on API availability, not on how an episode was going.
- **Resume** is per episode: a restarted shard skips every (task, seed, rep) already in its rows file, after dropping a trailing partial line. There is no other re-run of any episode.
- A harness error (Selenium/Chrome) is recorded in `error`, the episode counts as a failure, and the env is rebuilt, exactly as the floor's driver does.
- Runs are attended in this session; no unattended background loop.

## Calls and rate

Four processes, each with one request in flight; about 1 request per 1–2 s per process, so at most roughly 250 per minute, under the 1,200/min limit. At most 10 calls per episode, 6,250 in total. Every row records calls, input and output tokens, Jev latency, the resolved model and each step's decision (option counts, choice, confidence).

## Reported, not barred

- seconds per step: the env's step time, which is comparable with the floor's 0.642 s and includes the 0.5 s wait, and end to end (episode wall minus reset, over steps), which includes the Jev call;
- Jev calls and input tokens per episode, and total spend at $0.042 per million input tokens (`docs-mirror/typesafe/models.md:13,18`);
- `reward_miniwob_10s`, MiniWoB's time-scaled reward under its own 10 s timer, from the JS-measured episode time; `success_strict` (raw ≥ 1); mean raw reward;
- failed calls and halts; per-task successes against the scripted floor; exact McNemar against the random floor.

## Keyless proof, run before this commit (no key, no network, no live call)

P=`/tmp/jev-miniwob-jev/venv/bin/python`, `TYPESAFE_API_KEY` unset.

- `$P work/miniwob-jev/jev_arm.py selftest` → `selftest: ok (0 failures)`. It covers:
  - span order, dedupe, the 255 cap, and quote-free n-grams;
  - `type` options for a text input and a matching `<select>`, and none for a `<select>` with no matching span;
  - a checkbox labelled by its `<label>` text;
  - the 255 action cap on a 402-element page, which keeps the `type` option, the interactive `click` and `none`;
  - 11 hostile answers, all refused: missing, wrong choice, missing or extra key, sum off, choice not the argmax, NaN, negative, confidence above 1, string probability;
  - a malformed answer becomes a no-op and is recorded, and the third in a row halts;
  - a valid answer resets the streak, and the history record matches the floor's;
  - HTTP 402 halts at once;
  - `LiveAsker()` without a key raises;
  - `live` without a key returns 2 before any Chrome starts.
- `live --shard 0/4` without a key prints `unconfigured: TYPESAFE_API_KEY unset, no call made (NOT_RUN)` and exits 2. No Chrome starts and no rows directory is created.
- `dev --fake malformed` and `dev --fake raise` on click-button seed 9000: `HALT ... 3 consecutive failed calls ... (episode row not written; resume replays it)`, exit 4, zero rows written.
- `dev --fake greedy` over all 125 tasks on dev seed 9000 (four processes, final code): 125 episodes, 878 steps and requests built, 68 of them `type` actions, 0 harness errors, 0 failed calls. The fake types into each untyped field first, then picks by word overlap. It is a plumbing check; its 21 successes are not a floor and are not cited.
  - action options per step: min 1 (drag-items-grid offers only `none`), median 10, p90 48, max 76 (daily-calendar); clicks truncated: 0.
  - text heads per step: median 0, p90 2, max 4 (copy-paste-2).
  - request bytes: state median 1,556, p90 7,663, max 11,352 (daily-calendar); questions median 1,353, p90 9,998, max 33,421 (copy-paste-2).
  - the env's step time averaged 0.667 s, and end to end 0.690 s with the fake asker.
- The type path reaches the page. On choose-list seed 9000, "Select Jersey from the list and click Submit.", the lattice offers `type [4] select #options` with the text head `["Jersey"]`; `type(4, "Jersey")` then `click` Submit ends the episode with raw reward 1.
- **The lattice contains the floor's action space.** The floor's own `ScriptedPolicy` was run on dev seed 9000 over all 125 tasks (a throwaway script, no model). At each step its action was checked against `build_candidates` on the same page. All 370 of its actions are offered options: 308 clicks, 52 types whose text is one of the offered spans, and 10 `none`. So are all the actions of its 27 successful episodes.

## Token counts (`omp toks <file> --json`, offline tokenizers; full request body = model + state + questions)

| Sample (dev seed 9000, step 0) | Bytes | o200k | claude-v5 | jev |
|---|---:|---:|---:|---:|
| click-checkboxes (the floor's state sample; 12 action options, no text head) | 2,622 | 906 | 1,357 | 1,001 |
| login-user (8 action options, 2 text heads of 117 spans) | 11,207 | 2,774 | 3,728 | 2,832 |
| copy-paste-2 (the largest request seen; 10 options, 4 text heads of 185 spans) | 34,447 | 9,317 | 11,632 | 9,382 |

All are under the 32k-token state-plus-longest-question limit (`docs-mirror/typesafe/models.md:15`).

## Commands

```
uv venv --python 3.12 /tmp/jev-miniwob-jev/venv
uv pip install --python /tmp/jev-miniwob-jev/venv/bin/python miniwob==1.1.0 selenium==4.49.0 gymnasium==1.3.0 numpy==2.5.3 ./upstream/typesafe-ai/typesafe-sdk-python
P=/tmp/jev-miniwob-jev/venv/bin/python
# live, one per shard k in 0..3, attended, resumable
PYTHONDONTWRITEBYTECODE=1 infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- $P work/miniwob-jev/jev_arm.py live --shard $k/4
# keyless re-score
python3 work/miniwob-jev/score.py
```

## Hashes (after the repo's pre-commit formatter)

| File | sha256 |
|---|---|
| `work/miniwob-jev/jev_arm.py` | `31fd2231e09521089c7853f3d2d3bad2b566599f2fb30aff980b79722c87dab7` |
| `work/miniwob-jev/score.py` | `60e01d02964a2a61eaae07b3027c6d37da926589728b3a732d2f66498c28a6a8` |
| `work/game-floors/miniwob/run.py` | `e0b0c42886e4ba176f6d7620b013604a1740d6c8513443b99bbe366443273c7b` (the floor's preregistered hash, unchanged) |
| `work/game-floors/miniwob/tasks.json` | `af8890bf4877515c4eb27ee14a2fa0ea180b3c928709682634f96312986bb500` (unchanged) |

## Boundary: not run before this commit

- No live Jev call of any kind. No live development run: every run above used a fake asker, no key and no network except Selenium Manager's chromedriver cache.
- No benchmark seed was touched by any Jev-arm code. Development used seeds 9000 and 9001 only, which lie outside the split.
- No comparator model. BrowserGym's Playwright harness was not run, and neither were drag, coordinate or free-text actions.
