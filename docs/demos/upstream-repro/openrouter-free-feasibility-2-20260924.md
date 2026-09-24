# Can a free OpenRouter model carry an incumbent arm when the harness is paced? (bead `jev-3e2i`, run 2 of `jev-14qk`)

GreenForest (background agent of pane 1, hub id FreeModelScout), 2026-09-24. Live lane, $0: `:free`
model ids only. No Anthropic model, no TypeSafe/Jev call (AGENTS.md, "No Anthropic API spend on
comparisons").

## Preregistered (committed on its own, before the first call)

**Why a second run.** Joshua stopped Anthropic API spend on comparisons on 2026-09-24, so Haiku no
longer serves as the incumbent. `jev-14qk` (`5498c91` bar, `7840279` rows,
`openrouter-free-feasibility-20260924.md`) found no free model that answered 50/50. Its failures
were mostly `429 Rate limit exceeded: free-models-per-min` and `429 Provider returned error` (all
150 failures of the two gemma models and qwen), plus `TimeoutError` (19 nemotron, 9 nex). nex had a
p95 of 151 s against a 180 s whole-call cap. That pattern points at how the harness paced its
requests (2 in flight, the adapter's 30 s retry budget with at most 5 s backoff), not
necessarily at the models. This run changes only the pacing and measures the same thing again.

**Unchanged from `jev-14qk`.** Same question: the committed SST-5 Score question
(`work/score-sst5/run.py`, `QUESTION`, imported). Same rows: the first 50 of
`work/score-sst5/sample.jsonl`. Same adapter settings: `structured_outputs=True`,
`llm_answer_mode="probabilities"`, `normalize_probabilities=True`. Same provider:
the adapter's own `AsyncOpenAIProvider` at `https://openrouter.ai/api/v1`, `chat_completions`, built
by `work/openrouter/provider.py`. Same scorer logic: `work/openrouter/score_feasibility.py`, with
a `--run2` flag that only switches which row files and model list it reads. One pass per model.
Failed rows are not re-run.

**Same bar.**

- A model **can carry a 500-row arm** only if it answers **50/50** with **0 zero-mass rows**.
  Zero-mass means a raw probability map that sums to 0 and that the adapter fills in as uniform
  (`jev-mly`).
- The **`jev-3e2i` comparator gate** is **>=49/50 answered**.
- Accuracy and MAE on 50 rows are printed but decide nothing.

**The only harness changes, and why each one is made.** They sit behind `--paced` in
`work/openrouter/run_sst5.py`. Without the flag the runner behaves exactly as it did in `jev-14qk`.

1. **One model at a time, concurrency 1 (was 2).** With two requests in flight, the per-minute
   request count doubles against the account's free-model per-minute limit. That limit produced
   the dominant failure class.
2. **At most 15 requests per minute from this process.** This is a sliding 60 s window, counted
   at the provider seam, so adapter retries and every other HTTP request count too. Why: OpenRouter
   limits free-model requests per minute per account, and `GET /api/v1/key` does not report that
   limit. [INFERENCE] The published figure is 20/min. 15 leaves headroom, and other panes may share
   the key. The pacer cannot see requests from other processes on the same key.
3. **Per-attempt timeout 120 s.** This is enforced at the provider seam and raised as the SDK's
   `TypeSafeAPITimeoutError`. Why: nex's answered p50 was 64 s and p95 151 s. A slow but valid
   answer is feasibility evidence, not a failure. The whole-call cap rises from 180 s to 420 s
   (pacer wait excluded) so that it can never cut a 120 s attempt that follows an adapter retry.
   The call is still bounded.
4. **429 handling moves from the adapter to the runner.** 429 is removed from the adapter
   `RetryPolicy`'s retried statuses. Everything else in `RetryPolicy()` is unchanged: 408 and 5xx,
   up to 2 retries, the 30 s budget. On a 429 the runner waits the server's `retry-after-ms` or
   `Retry-After`, or **60 s** when neither is sent, then re-sends the row. It waits **at most 3
   times per row**. A 4th 429 fails the row with that 429 recorded verbatim. Why: a per-minute
   limit cannot clear inside the default policy's 30 s budget and 5 s maximum backoff. In
   `jev-14qk` every retry of those rows landed inside the same limited minute.

**Guards (in code, before any request).**

- Every request passes through one wrapper that refuses any model id not ending in `:free`, before
  the HTTP call. This check sits on top of `provider.openrouter_provider`'s construction-time
  refusal.
- There is a process-wide cap of **599 HTTP requests** (under 600). When it is reached, the run
  stops and the remaining models are reported as not run.
- **5 consecutive failed rows of the same class** stop that model. Its remaining rows count as
  failed (not attempted), and the stop is reported.
- `GET /api/v1/key` `usage_daily` is recorded before and after the run. A rise of more than
  $0.001 is reported as a spend incident.
- Keys come only through `infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba`
  and are never printed.

**Models, in run order.** These are the 8 `:free` ids pane 1 listed with structured output. The
support column is re-read from the public `GET /api/v1/models` before this commit (2026-09-24). All
8 are priced 0/0.

| # | Model | `structured_outputs` / `response_format` listed now |
|---|---|---|
| 1 | `dots-studio/dots-3-note-preview:free` | yes / yes |
| 2 | `nex-agi/nex-n2.5-pro:free` | yes / yes |
| 3 | `nvidia/nemotron-3-super-120b-a12b:free` | yes / yes |
| 4 | `nex-agi/nex-n2.5-mini:free` | yes / yes |
| 5 | `liquid/lfm-2.5-2.6b:free` | yes / yes |
| 6 | `qwen/qwen3.8-27b:free` | yes / no |
| 7 | `google/gemma-4-31b-it:free` | no / yes |
| 8 | `google/gemma-4-26b-a4b-it:free` | no / yes |

The order puts the three models that answered in `jev-14qk` first, so the request cap cannot
starve them.

**Recorded per row** (`work/openrouter/rows-sst5-<model>-run2.jsonl`; the `jev-14qk` row files stay
untouched): the same fields as `jev-14qk`, plus these:

- `rateLimitWaits`, the number of 429 waits;
- `waitMs`, the total 429 wait;
- `pacerWaitMs`, the time held by the 15/min pacer;
- `requests`, the HTTP requests this row made.

`latencyMs` is the duration of the row's last `system_one` call, with the pacer wait subtracted.
Like `jev-14qk`'s, it includes adapter retries.

**Scorer, keyless:** `python3 work/openrouter/score_feasibility.py --run2`.

**Stated before running:** at least 400 requests, and at most 599. All go to `:free` ids, so the
cost is $0. At 15/min and the latencies above, [INFERENCE] the run takes 1-3 hours.

**NO-CLAIM.** One paced pass per model: 50 rows, one day, one wording. Free endpoints are shared
and their limits change by the hour. A model that passes is feasible today under this pacing, not
reliable in general. No quality comparison with Jev or Haiku is made or implied.

## Results

Live lane. N = 50 rows per model. 2026-09-24, from 14:52 to 18:44 UTC (3 h 51 m, one process,
`run_sst5.py --paced`). Model ids as in the table. Upstream providers are the ones OpenRouter
reported. The table below is the output of `python3 work/openrouter/score_feasibility.py --run2`
(`work/openrouter/score-feasibility-run2.txt`). The requests and 429-wait columns are summed from
the row files' `requests` and `rateLimitWaits` fields.

| Model | Answered | Failed, by verbatim class | Zero-mass | p50 / p95 ms (answered) | Upstream | Requests | 429 waits |
|---|---:|---|---:|---|---|---:|---:|
| `dots-studio/dots-3-note-preview:free` | 50/50 | 0 | 0 | 21493 / 35643 | AtlasCloud 50 | 50 | 0 |
| `nex-agi/nex-n2.5-pro:free` | 29/50 | 21 `TypeSafeAPITimeoutError: Request timed out (timeout=120.0).` | 1 | 58959 / 108306 | Nex AGI 29 | 50 | 0 |
| `nvidia/nemotron-3-super-120b-a12b:free` | 12/50 | 22 `TypeSafeAPITimeoutError` (120 s); 14 `TypeError: 'NoneType' object is not subscriptable`; 1 `TypeSafeAPIResponseValidationError: 200 Invalid response data at 'answers'.`; 1 `TypeSafeError: Expecting value: line 11 column 1 (char 55)` | 2 | 6607 / 53991 | Nvidia 12 | 50 | 0 |
| `nex-agi/nex-n2.5-mini:free` | 50/50 | 0 | 2 | 4060 / 26290 | Nex AGI 50 | 50 | 0 |
| `liquid/lfm-2.5-2.6b:free` | 49/50 | 1 `TypeSafeError: OpenAI chat completion did not complete: length.` | 4 | 29676 / 71240 | Liquid 49 | 51 | 1 (row 42, then answered) |
| `qwen/qwen3.8-27b:free` | 0/50 | 5 `TypeSafeRateLimitError: 429 Provider returned error` (3 waits each); 45 not attempted (stopped: 5 consecutive) | 0 | none | not reported | 20 | 15 |
| `google/gemma-4-31b-it:free` | 0/50 | 9 `TypeSafeRateLimitError: 429 Provider returned error`; 2 `TypeSafeAPIResponseValidationError: 200 Invalid response data at 'answers'.` (upstream Google AI Studio); 39 not attempted (stopped: 5 consecutive 429) | 0 | none | Google AI Studio on the 2 non-429 rows | 41 | 30 |
| `google/gemma-4-26b-a4b-it:free` | 0/50 | 5 `TypeSafeRateLimitError: 429 Provider returned error` (3 waits each); 45 not attempted (stopped: 5 consecutive) | 0 | none | not reported | 20 | 15 |

Flat and renormalized counts, and exact/MAE on the answered rows, are in the scorer output. They are
descriptive only.

**Against the preregistered bar (counts only).**

- **50/50 answered and 0 zero-mass** (carries a 500-row arm):
  `dots-studio/dots-3-note-preview:free`.
- **>=49/50 answered** (the `jev-3e2i` gate): `dots-studio/dots-3-note-preview:free` (50, 0
  zero-mass), `nex-agi/nex-n2.5-mini:free` (50, 2 zero-mass), `liquid/lfm-2.5-2.6b:free` (49, 4
  zero-mass).
- **>=49/50 answered and 0 zero-mass:** `dots-studio/dots-3-note-preview:free` only.

**Harness facts observed.**

- 332 HTTP requests in total, under the 599 cap. Every row file's `model` is a `:free` id (0 non-free
  across 271 rows). The only request path is `PacedProvider.request`, which calls `require_free`
  first.
- The 15/min pacer never held a request: `pacerWaitMs` is 0 on every row, so no 60 s window ever
  reached 15 request starts.
- No row's stored error or retry reason carries `free-models-per-min`, the dominant class in
  `jev-14qk`. The text of the waited 429s is not stored (see the next item).
- 80 responses were 429: 61 were waited out and 19 failed their row. All 19 row-failing 429s
  read `429 Provider returned error`. The text of a waited 429 is not stored. Of the 61 waits, 60
  were the 60 s default because no `Retry-After` or `retry-after-ms` was sent. The exception is
  lfm row 42: its 429 asked for 1 s, the row waited 1 s, and it then answered.
- No adapter 408/5xx retry fired: requests equal rows plus 429 re-sends on every model.
- The public model list read before the prereg lists the two gemma ids with `response_format` but
  not `structured_outputs`. They ran as preregistered.
- The account's `free_model_daily_requests` counter read `used` 144 (limit 1000) before and 381
  after. It is the whole account's counter, not this process's alone.

**Spend.** `GET /api/v1/key` `usage_daily` was **0.016185 before** (14:52:51Z) and **0.016185
after** (18:44:56Z), a change of $0. `usage` stayed at 100.176529287.

**Commits.** Prereg `d2cf882` (this file, before any call). Paced mode and guards `db6e4a7`
(provider tests 9/9, with the planted guard removal turning red). Rows and scorer output `8c45cf4`.
Results: the commit that adds this section.

**Not run / not claimed.** No row was re-run, and no model was run a second time. 45 qwen, 39
gemma-4-31b and 45 gemma-4-26b rows were never attempted, because the preregistered 5-consecutive
stop fired. No accuracy comparison with Jev or Haiku was run. The 50-row numbers are one paced pass
on one day, through shared free endpoints.
