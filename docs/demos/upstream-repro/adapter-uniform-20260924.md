# Why 14 Haiku rows came back exactly uniform through system-one-adapter-python (bead `jev-mly`)

AdapterUniform (background agent of pane 1), 2026-09-24. Live lane. Source of the anomaly:
[`choice-banking77-20260924.md`](choice-banking77-20260924.md) (bead `jev-k3k`), where 14 of 400
`anthropic/claude-haiku-4-5` rows through `upstream/typesafe-ai/system-one-adapter-python` returned
every option at exactly 0.1, confidence 0, choice = the first criterion (`activate_my_card`).

## Pins

- Adapter as vendored: `adffc2eab300a4fa3c0e92252d4ffd6ceaa53700` (Release v0.2.0, 2026-09-18).
- Upstream `main` at the time of this pass: `e1d4cc938204b22fc5a3c3aca7044072fe3f712d` (Release
  v0.2.1, 2026-09-22), one commit ahead; not pulled. `gh api .../compare/adffc2e...e1d4cc9` lists the
  changed files: `_utils/probability_normalization.py`, `_utils/confidence_metrics.py` and the Choice
  branch of `_client.py` are **not** among them, so every line cited below is unchanged at upstream
  HEAD. v0.2.1 adds an Anthropic `stop_reason` check (`providers/anthropic.py`), which is relevant
  only if the uniform rows carry an unusual stop reason.

## Every path to a uniform Choice answer, from source (file:line at `adffc2e`)

Paths are relative to `upstream/typesafe-ai/system-one-adapter-python/src/system_one_adapter/`.

1. **Zero-total rescale.** `_utils/probability_normalization.py:100-106`: in probabilities mode the
   model's per-label values are read as-is; total 0 gives `error = 1.0 > 1e-6`, so with
   `normalize_probabilities=True` it calls `rescale_probabilities`, whose zero-total branch
   (`:69-72`) returns `1/len(labels)` for every label. With 10 labels that is exactly 0.1 each.
2. **Tie resolves to the first criterion.** `_client.py:159`, `max(answers, key=probabilities.__getitem__)`
   returns the first label on a tie, so a uniform vector always answers criterion #1.
3. **Confidence 0 on a zero or uniform vector.** `_utils/confidence_metrics.py:22-24` via `_normalize`
   (`:27-32`, zero total -> uniform): `(max - 1/n) / (1 - 1/n) = 0`.
4. **With `normalize_probabilities=False`** (`probability_normalization.py:103-104`) the all-zero
   vector is returned unchanged, and paths 2 and 3 still apply: choice = first criterion, confidence
   0, probabilities all 0.0. Normalization off does not turn it into an error.
5. **A model-asserted uniform** (the model itself returns 0.1 for every label, sum 1) passes through
   untouched (`:103-104`) and is byte-identical in `answers` to path 1.
6. **Not a path:** a parse or schema failure. `_client.py:216-225` retries or raises
   `TypeSafeAPIResponseValidationError`; it never yields an answer. Missing labels fail the strict
   per-question model (`_schema.py`), and values outside [0, 1] fail `Probability = Field(ge=0, le=1)`
   (`_schema.py:25`) on decode. No logprobs are involved anywhere: the distribution is the model's
   own JSON numbers.

The only signal separating path 1 from path 5 is in `response.debug`:
`probability_errors[<id>] == 1.0` and `original_probabilities[<id>]` all zero
(`probability_normalization.py:21-54`). The jev-k3k runner kept `answers` and discarded `debug`
(`work/choice-banking77/run.py:183-190`), so its 14 rows cannot tell path 1 from path 5.

## Keyless mechanism check (no key, no network)

`work/adapter-uniform/repro_keyless.py` injects a caller-owned fake provider (the adapter's documented
`model=<provider instance>` seam) that returns a fixed raw payload, and runs the adapter's real
decode/normalize/confidence code on it. Seven cases, 7/7 expectations hold (exit 0; the last three
were added after the bar commit and before the result, to check two workarounds and the Score twin):

| Raw model payload (4 labels) | `normalize_probabilities` | Adapter `choice` | `confidence` | `probabilities` | `debug.probability_errors` |
|---|---|---|---|---|---|
| all 0.0 | True | `alpha` (first) | 0.0 | 0.25 each | `{"q": 1.0}` + `original_probabilities` all 0 |
| all 0.0 | False | `alpha` (first) | 0.0 | 0.0 each | `{"q": 1.0}` |
| 0.25 each (model-asserted) | True | `alpha` (first) | 0.0 | 0.25 each | `{}` |
| one-hot on `gamma` | True | `gamma` | 1.0 | one-hot | `{}` |
| all 0.0, `n_retry_malformed_structure=2` | True | `alpha` (first), **1 provider call** | 0.0 | 0.25 each | `{"q": 1.0}` |
| Score, 3 levels all 0.0 | True | `score=1.0` (middle level) | 0.0 | 1/3 each | `{"s": 1.0}` |
| Score, 3 levels all 0.0 | False | `score=1.0` (middle level) | 0.0 | 0.0 each | `{"s": 1.0}` |

Rows 1 and 3 have identical `answers`. That is the mechanism; it does not yet say which path the 14
live rows took.

## Preregistered live bar (committed before any live call)

**Question.** For the jev-k3k rows that came back uniform, is the raw Haiku response an all-zero
distribution (path 1, the adapter fabricating a uniform answer from a non-distribution), a
model-asserted uniform (path 5, provider behaviour), or something else?

**Inputs, byte-identical to jev-k3k.** State, question, labels and rows are read with `git show`
from `3709ee6` (the commit that recorded jev-k3k `rows-haiku.jsonl`; `work/choice-banking77/run.py`
was extended for jev-4jf afterwards at `909278f`, so the working-tree runner is not used). Client
settings copy that runner: `structured_outputs=True`, `llm_answer_mode="probabilities"`,
`normalize_probabilities=True`, `RetryPolicy()`; model `claude-haiku-4-5`; adapter at `adffc2e`.

**Rows.** Targets: all 14 jev-k3k Haiku rows with an exactly uniform distribution. Controls: for each
target, the next subset row by `i` with the same intent that was not uniform in jev-k3k, never
reused (14). Selection is code: `select_rows()` in `work/adapter-uniform/live.py`.

**Calls.** 5 repeats per row, 28 rows, 140 calls, 8 concurrent. The raw Anthropic response of every
provider attempt is captured by wrapping the caller-owned provider's SDK `messages.create` (the
vendored clone is not edited), and parsed independently of the adapter.

**Decision rules, fixed now.**
- **ADAPTER-FABRICATES-UNIFORM (path 1) CONFIRMED LIVE** if at least one call returns an adapter
  answer that is exactly uniform and its captured raw response parses to a Choice distribution whose
  values sum to 0. Paired with the keyless table this is the defect: a non-distribution is returned
  as a well-formed, zero-confidence answer for the first criterion, not as an error.
- **PROVIDER BEHAVIOUR (path 5)** if every uniform adapter answer has a raw distribution summing to
  a positive value (the model asserted uniform). No adapter defect claimed.
- **NOT REPRODUCED** if no call returns a uniform adapter answer. The keyless mechanism stands; the
  link from it to the 14 rows stays inferred and is recorded in `NEGATIVE_EVIDENCE.md` with a retry
  condition.
- **Recurrence** is reported as uniform calls / calls, per arm, and rows with at least one uniform /
  rows, per arm. A target-arm rate above the control-arm rate says the input, not chance, drives it.
  No threshold is attached; it is descriptive.
- **Our misuse** is assessed separately: whether any documented adapter setting would have turned
  the zero-sum case into an error (keyless row 2 says `normalize_probabilities=False` does not).

**Re-score (keyless, from committed rows):** `python3 work/adapter-uniform/live.py score`.

## Result

Run 2026-09-24 02:34 UTC, live lane, `claude-haiku-4-5` via `AsyncAnthropicProvider`, adapter at
`adffc2e`, 140/140 calls answered, 0 errors, every captured response `stop_reason = end_turn`, one
provider attempt per call. Rows: `work/adapter-uniform/live-raw.jsonl`.

| Arm | Calls | Adapter answer uniform | …raw all-zero | …raw model-asserted uniform | Rows with ≥1 uniform |
|---|---|---|---|---|---|
| Target (the 14 jev-k3k uniform rows) | 70 | **58/70** | 58/58 | 0/58 | 13/14 |
| Control (14 same-intent rows) | 70 | 1/70 | 1/1 | 0/1 | 1/14 (`i=208`) |

All 59 uniform answers are `choice = activate_my_card` (criterion #1) at confidence 0. The only
target row that never went uniform, `i=214`, is the one whose text names a beneficiary directly
("What are the rules for transferring to a beneficiary?"). One raw response, verbatim (`i=229`):

```json
{"answers":{"intent":{"activate my card":0,"age limit":0,"apple pay or google pay":0,"atm support":0,"automatic top up":0,"balance not updated after bank transfer":0,"balance not updated after cheque or cash deposit":0,"beneficiary not allowed":0,"cancel transfer":0,"card about to expire":0}}}
```

**Verdict under the preregistered rules: ADAPTER-FABRICATES-UNIFORM (path 1) CONFIRMED LIVE.**
Level `[live]` N=140 for the recurrence, `[test]` for the mechanism (keyless, 7/7).

Split of responsibility, each stated at its evidence level:
- **Provider behaviour** `[live, N=140]`: Haiku 4.5 returns an all-zero map, against the adapter's
  system prompt ("make the probabilities sum to 1", `_client.py:70-77`), and does so repeatably on
  specific inputs (58/70 on the target rows vs 1/70 on controls). Why these inputs is not measured
  here; the texts (crypto purchase, transfer timing, card delivery abroad) read as poor fits for all
  ten option names `[INFERENCE]`.
- **Adapter defect** `[test]`: a probability map with no mass is returned as a successful answer
  naming criterion #1, in both `normalize_probabilities` modes, schema-valid so the corrective retry
  never fires, and indistinguishable in `answers` from a model-asserted uniform. Score's twin
  reports the middle level. The only signal is `debug.probability_errors` = 1.0. Same class as the
  maintainers' own accepted #38 (incomplete output returned as a successful evaluation).
- **Our misuse** `[test]`: no documented setting turns the case into an error (keyless rows 2 and
  5), so the configuration was not the cause. What we did wrong is discard `debug`:
  `work/choice-banking77/run.py` at `3709ee6` kept `answers` only, so jev-k3k scored 14 "no answer"
  rows as Haiku picking `activate_my_card`. Any Haiku arm through this adapter must record
  `debug.probability_errors` (jev-4jf's runner now records `normError`/`rawSum`, per its author).

Effect on jev-k3k, stated and not re-scored: its Haiku 362/400 counts these 14 as wrong answers;
they are non-answers. Whether that changes the WIN verdict is for that bead's owner to rule on.

## Stranger repro and upstream draft

- `work/adapter-uniform/stranger_repro.py`: standalone, no key, no path hacks. Ran clean-room
  against the published wheel: `uv run --no-project --with system-one-adapter==0.2.1 python
  stranger_repro.py` in a `mktemp -d`, `typesafe-sdk` 0.7.1 resolved; output matches the draft.
- Pin gap: vendored `adffc2e` (v0.2.0) vs upstream `e1d4cc9` (v0.2.1). Every cited line was
  re-located in the v0.2.1 sources fetched with `gh api`; only `_decode_or_correct` moved
  (`216-225` to `222-231`). Behaviour is the same on the v0.2.1 wheel (repro above, plus the Score
  twin run on the wheel).
- Dedup (Phase −1, 2026-09-24T02:35Z): `gh issue list --state all --search` for `uniform`,
  `zero probabilities`, `normalize`, `all zero`, `rescale`, `confidence 0`, `probability sum`, plus
  the full lists (8 issues, 32 PRs): no duplicate. Nearest is #38 (different mechanism).
- Draft body: `work/adapter-uniform/issue-draft.md`; proposed title *"An all-zero probability map
  returns option #1 as a successful answer"* (68 chars). Report Test: the draft's bash block was
  executed verbatim and its output matched the draft's expected block byte-for-byte.
- Rubric: `python3 ~/Developer/flywheel/.flywheel/scripts/jeff-issue.py rubric --draft
  work/adapter-uniform/issue-draft.md --tracking-bead jev-mly --json` → `status: pass`,
  `decision: auto_post`, 7/7 axes high, ledger `rubric-a362057f2126`. Two honest edits were needed
  to get there: the model id `claude-haiku-4-5` tripped the internal-id leak patterns (a false
  positive; written as "Claude Haiku 4.5" instead, pattern not touched), and the body was trimmed
  under the 1,200-word tone limit. A pass certifies form only; the Report Test above is the
  substance check.
- **Not posted.** Posting is Joshua's call.

## Spend

140 Haiku calls, 126,560 input + 14,545 output tokens, about $0.20 at $1 / $5 per MTok list price
`[INFERENCE: price not read from a bill]`. Zero Jev calls.

## NO-CLAIM

- No claim about why Haiku zeroes these inputs, or its rate on any other question, label set or
  model; N is one question, 28 rows, 5 repeats.
- No claim about the hosted TypeSafe API's behaviour on a zero-mass answer; not tested.
- `llm_answer_mode="discrete"` and `structured_outputs=False` not exercised.
- The jev-k3k verdict is not re-scored here.
- The live run used the vendored v0.2.0; v0.2.1 was checked keyless only.

## Non-author verification — LabelFixT2u (pane 1 background agent, claude-opus), 2026-09-24

**Verdict: CONFIRMED.** The mechanism, the live recurrence and the upstream draft's Report Test all reproduce.

- **Keyless mechanism `[test]`.** `upstream/typesafe-ai/system-one-adapter-python/.venv/bin/python work/adapter-uniform/repro_keyless.py` printed 7/7 cases with `expectation_holds: true` and exited 0. The adapter imported from the vendored clone at `adffc2e`, and the clone's worktree is clean. The output matches the keyless table row for row, including 1 provider call with `n_retry_malformed_structure=2` and Score `1.0` in both normalize modes.
- **Live re-score `[test]` on the committed rows.** In a clean `git clone --local` at `04de976`, `python3 work/adapter-uniform/live.py score` gave: target 58/70 uniform, 58 raw all-zero, 0 model-asserted, 13/14 rows; control 1/70 (`i=208`); `stop_reason` always `end_turn`; 126,560 / 14,545 tokens. I also recounted without the scorer, parsing `raw_responses[-1].text` and comparing it with `adapter_probabilities`, and got the same numbers: target 58 uniform, all with raw sum 0, all `activate_my_card`, and 12 non-uniform, all with positive raw sum; control 1 and 69. The 14 target ids equal the 14 exactly uniform rows in `rows-haiku.jsonl` at `3709ee6`. The 14 controls do not overlap them.
- **Order.** The bar `bbc600d` (20:32:56 -0600) precedes the live commit `80a499f` (20:41:09). The input-pinning commit `640cfb9` (20:34:22) falls in the same minute as the stated run start (02:34 UTC). The rows carry no timestamps, so I cannot order these two more finely than the minute.
- **Citations at `adffc2e`**, read in the vendored source. Every one holds: `probability_normalization.py:21` (`probability_debug_data`), `:69-72` (zero-total branch returns `1/len`), `:100-106` (read as-is, `error = abs(total-1)`, `:103-104` return unchanged when disabled, `:106` rescale); `_client.py:70-77` ("make the probabilities sum to 1"), `:159` (`max(answers, key=…)`), `:216-225` (validate or corrective retry or raise); `confidence_metrics.py:22-24`, `:27-32`; `_schema.py:25` (`Probability = Annotated[float, Field(ge=0, le=1)]`). At upstream `e1d4cc9` (v0.2.1), read with `gh api`, the draft's cites also hold: `:58` (docstring naming the uniform fallback), `:70-72`, `:100-106`, `_client.py:141-142` (Score always rescales), `:159`, `:222-231`.
- **Report Test.** I ran the draft's bash block unchanged except for the scratch directory, `/tmp/allzero` → `/tmp/lfx-allzero-v`, because `/tmp/allzero` already existed from the author's run. It exited 0 and resolved `typesafe-sdk 0.7.1` and `system-one-adapter 0.2.1`. Its stdout is byte-identical to the draft's expected output block (`diff` empty).
- The 14 jev-k3k rows are non-answers, not wrong answers. I agree, and that is still for jev-k3k's owner to re-score.

NO-CLAIM of this check: no live call was repeated. The draft has not been posted; that is Joshua's call. The rubric was not re-run. Scratch left in place: `/tmp/lfx-allzero-v`, `/tmp/lfx-draft-*.txt|.sh`, `/tmp/lfx-v021-*`, `/tmp/lfx-k3k-rows-haiku.jsonl`.
